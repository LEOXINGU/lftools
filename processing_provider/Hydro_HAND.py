# -*- coding: utf-8 -*-

"""
Hydro_HAND.py
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""
__author__ = 'Leandro França'
__date__ = '2026-09-17'
__copyright__ = '(C) 2026, Leandro França'

from collections import deque
from math import ceil, log2
import os

import numpy as np
from osgeo import gdal, osr

from qgis.PyQt.QtCore import QMetaType, QTimer
from qgis.PyQt.QtGui import QColor, QIcon
from qgis.core import (
    Qgis,
    QgsApplication,
    QgsCategorizedSymbolRenderer,
    QgsDistanceArea,
    QgsFeature,
    QgsFeatureSink,
    QgsField,
    QgsFields,
    QgsGeometry,
    QgsLineSymbol,
    QgsPointXY,
    QgsProcessing,
    QgsProcessingAlgorithm,
    QgsProcessingException,
    QgsProcessingLayerPostProcessorInterface,
    QgsProcessingUtils,
    QgsProcessingParameterBoolean,
    QgsProcessingParameterEnum,
    QgsProcessingParameterFeatureSink,
    QgsProcessingParameterNumber,
    QgsProcessingParameterRasterDestination,
    QgsProcessingParameterRasterLayer,
    QgsProject,
    QgsRendererCategory,
    QgsUnitTypes,
    QgsWkbTypes,
)

import processing

from lftools.geocapt.imgs import Imgs
from lftools.translations.translate import translate


# QGIS requires layer post-processors to remain alive until the outputs load.
_POST_PROCESSORS = []
_OUTPUT_LAYER_IDS = {}
_EXPECTED_OUTPUTS = set()
_OUTPUT_GROUP = None
_OUTPUT_GROUP_NAME = ''


# Display order in the QGIS Layers panel (top to bottom).
_OUTPUT_ORDER = (
    'DRAINAGE_VECTOR',
    'HAND',
    'DRAINAGE_RASTER',
    'FLOW_ACCUMULATION',
    'FLOW_DIRECTION',
    'CONDITIONED_DEM',
)


def _build_downstream(direction, valid):
    """Return the downstream flat index for each cell of a GRASS D8 raster.

    GRASS r.watershed uses values 1..8 counter-clockwise from north-east:
    1=NE, 2=N, 3=NW, 4=W, 5=SW, 6=S, 7=SE and 8=E. Negative
    values represent flow leaving the computational region.
    """
    rows, cols = direction.shape
    size = rows * cols
    direction_flat = np.abs(direction).ravel()
    valid_flat = valid.ravel()
    downstream = np.full(size, -1, dtype=np.int64)

    offsets = {
        1: (-1, 1),
        2: (-1, 0),
        3: (-1, -1),
        4: (0, -1),
        5: (1, -1),
        6: (1, 0),
        7: (1, 1),
        8: (0, 1),
    }

    for code, (delta_row, delta_col) in offsets.items():
        source = np.flatnonzero(valid_flat & (direction_flat == code))
        if source.size == 0:
            continue

        source_row = source // cols
        source_col = source - source_row * cols
        target_row = source_row + delta_row
        target_col = source_col + delta_col
        inside = (
            (target_row >= 0)
            & (target_row < rows)
            & (target_col >= 0)
            & (target_col < cols)
        )
        if not np.any(inside):
            continue

        source = source[inside]
        target = target_row[inside] * cols + target_col[inside]
        target_valid = valid_flat[target]
        downstream[source[target_valid]] = target[target_valid]

    # In r.watershed, a negative drainage value explicitly marks runoff
    # leaving the computational region. It must not be connected to another
    # valid cell even when its absolute direction happens to point inward.
    negative_outflow = valid_flat & (direction.ravel() < 0)
    downstream[negative_outflow] = -1

    return downstream


def _build_external_outlets(direction, valid, downstream):
    """Identify cells whose D8 flow leaves the valid DEM domain."""
    direction_flat = np.asarray(direction).ravel()
    valid_flat = np.asarray(valid).ravel()
    has_direction = (np.abs(direction_flat) >= 1) & (
        np.abs(direction_flat) <= 8
    )
    return valid_flat & has_direction & (
        (downstream < 0) | (direction_flat < 0)
    )


def _calculate_hand_targets(downstream, stream_flat, outlet_flat=None):
    """Associate each cell with its first downstream drainage cell.

    Vectorized pointer jumping is used instead of following each flow path
    independently. The returned array contains the flat index of the connected
    drainage or external-outlet cell, or -1 when neither can be reached.
    """
    size = downstream.size
    target = downstream.copy()
    stream_index = np.flatnonzero(stream_flat)
    target[stream_index] = stream_index
    if outlet_flat is not None:
        outlet_index = np.flatnonzero(outlet_flat)
        target[outlet_index] = outlet_index

    # Each iteration approximately doubles the travelled downstream distance.
    max_iterations = max(2, int(ceil(log2(max(size, 2)))) + 2)
    for _ in range(max_iterations):
        active = target >= 0
        if not np.any(active):
            break
        current = target[active]
        jumped = target[current]
        changed = np.any(jumped != current)
        target[active] = jumped
        if not changed:
            break

    resolved = target >= 0
    resolved_index = np.flatnonzero(resolved)
    if resolved_index.size:
        reaches_reference = stream_flat[target[resolved_index]]
        if outlet_flat is not None:
            reaches_reference |= outlet_flat[target[resolved_index]]
        target[resolved_index[~reaches_reference]] = -1
    return target


def _calculate_stream_orders(stream_flat, downstream):
    """Calculate cell-based Strahler order and Shreve magnitude."""
    size = downstream.size
    stream_index = np.flatnonzero(stream_flat)
    indegree = np.zeros(size, dtype=np.uint16)

    target = downstream[stream_index]
    linked = (target >= 0)
    if np.any(linked):
        linked_position = np.flatnonzero(linked)
        linked[linked_position] = stream_flat[target[linked_position]]
        np.add.at(indegree, target[linked], 1)

    remaining = indegree.copy()
    strahler = np.zeros(size, dtype=np.uint16)
    shreve = np.zeros(size, dtype=np.uint64)
    maximum_upstream_order = np.zeros(size, dtype=np.uint16)
    maximum_order_count = np.zeros(size, dtype=np.uint16)
    shreve_sum = np.zeros(size, dtype=np.uint64)

    sources = stream_index[indegree[stream_index] == 0]
    strahler[sources] = 1
    shreve[sources] = 1
    queue = deque(int(index) for index in sources)
    processed = 0

    while queue:
        cell = queue.popleft()
        processed += 1
        next_cell = int(downstream[cell])
        if next_cell < 0 or not stream_flat[next_cell]:
            continue

        upstream_order = strahler[cell]
        if upstream_order > maximum_upstream_order[next_cell]:
            maximum_upstream_order[next_cell] = upstream_order
            maximum_order_count[next_cell] = 1
        elif upstream_order == maximum_upstream_order[next_cell]:
            maximum_order_count[next_cell] += 1

        shreve_sum[next_cell] += shreve[cell]
        remaining[next_cell] -= 1

        if remaining[next_cell] == 0:
            order = maximum_upstream_order[next_cell]
            if maximum_order_count[next_cell] >= 2:
                order += 1
            strahler[next_cell] = max(1, order)
            shreve[next_cell] = max(1, shreve_sum[next_cell])
            queue.append(next_cell)

    return indegree, strahler, shreve, processed


class HANDModel(QgsProcessingAlgorithm):

    LOC = QgsApplication.locale()[:2]

    def tr(self, *string):
        return translate(string, self.LOC)

    def createInstance(self):
        return HANDModel()

    def name(self):
        return 'handmodel'

    def displayName(self):
        return self.tr('HAND model', 'Modelo HAND')

    def group(self):
        return self.tr('Hydrology', 'Hidrologia')

    def groupId(self):
        return 'hydrology'

    def tags(self):
        return (
            'GeoOne,HAND,height above nearest drainage,altura acima da drenagem,'
            'hydrology,hidrologia,drainage,drenagem,stream,river,rede de drenagem,'
            'flow direction,direcao de fluxo,D8,flow accumulation,acumulacao de fluxo,'
            'watershed,bacia,dem,mde,dtm,mdt,terrain,relevo,grass,flood,inundacao,'
            'Strahler,Shreve,INPE,TerraHidro'
        ).split(',')

    def icon(self):
        return QIcon(
            os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                'images/hydrology.png',
            )
        )

    txt_en = '''Generates the <b>Height Above Nearest Drainage (HAND)</b> model from a Digital Elevation Model (DEM). HAND is the vertical difference between each terrain cell and the first drainage cell reached downstream along its D8 flow path.
<b>Processing workflow</b>
1. Optional hydrological conditioning of the DEM with GRASS <i>r.fill.dir</i>.
2. D8 flow direction and flow accumulation with GRASS <i>r.watershed</i>.
3. Drainage extraction using a minimum contributing-area threshold.
4. HAND calculation and Strahler and Shreve stream ordering.
<b>Outputs</b>
Conditioned DEM; D8 flow direction; flow accumulation; drainage raster; ordered vector drainage network; and HAND raster.
<b>Important information</b>
&#8226; Both projected and geographic CRS are accepted, but DEM elevations must be expressed in metres.
&#8226; The drainage threshold may be entered as number of cells, km&sup2; or hectares. For a geographic CRS, area conversions use the geodesic area of a cell at the centre of the DEM and are therefore approximate.
&#8226; Flow paths leaving the valid DEM before reaching the extracted drainage can remain as NoData, use the outlet-cell elevation, or use a fixed reference level, such as mean sea level.
&#8226; HAND is a terrain descriptor. By itself, it does not represent a hydraulic flood simulation.
<b>References</b>
Rennó, C. D. et al. (2008). <i>HAND, a new terrain descriptor using SRTM-DEM: Mapping terra-firme rainforest environments in Amazonia</i>. Remote Sensing of Environment, 112(9), 3469&ndash;3481. <a href="https://doi.org/10.1016/j.rse.2008.03.018">DOI: 10.1016/j.rse.2008.03.018</a>.
Nobre, A. D. et al. (2011). <i>Height Above the Nearest Drainage &mdash; a hydrologically relevant new terrain model</i>. Journal of Hydrology, 404(1&ndash;2), 13&ndash;29. <a href="https://doi.org/10.1016/j.jhydrol.2011.03.051">DOI: 10.1016/j.jhydrol.2011.03.051</a>.
GRASS GIS documentation: <a href="https://grass.osgeo.org/grass-stable/manuals/r.fill.dir.html"><i>r.fill.dir</i></a> and <a href="https://grass.osgeo.org/grass-stable/manuals/r.watershed.html"><i>r.watershed</i></a>.'''

    txt_pt = '''Gera o modelo <b>HAND (Height Above Nearest Drainage)</b>, ou Altura Acima da Drenagem mais Próxima, a partir de um Modelo Digital de Elevação (MDE). O HAND corresponde à diferença vertical entre cada célula do terreno e a primeira célula de drenagem alcançada a jusante pelo seu caminho de fluxo D8.
<b>Fluxo de processamento</b>
1. Condicionamento hidrológico opcional do MDE com o GRASS <i>r.fill.dir</i>.
2. Direção de fluxo D8 e acumulação de fluxo com o GRASS <i>r.watershed</i>.
3. Extração da drenagem pelo limiar de área mínima de contribuição.
4. Cálculo do HAND e ordenamento da drenagem pelos métodos de Strahler e Shreve.
<b>Produtos gerados</b>
MDE condicionado; direção de fluxo D8; acumulação de fluxo; drenagem raster; rede de drenagem vetorial ordenada; e raster HAND.
<b>Informações importantes</b>
&#8226; São aceitos SRC projetado e SRC geográfico, mas as altitudes do MDE devem estar expressas em metros.
&#8226; O limiar da drenagem pode ser informado em número de células, km&sup2; ou hectares. Em SRC geográfico, a conversão de área utiliza a área geodésica de uma célula no centro do MDE e, portanto, é aproximada.
&#8226; Caminhos de fluxo que saem do MDE válido antes de alcançar a drenagem extraída podem permanecer como NoData, utilizar a cota da célula de saída ou utilizar um nível de referência fixo, como o nível médio do mar.
&#8226; O HAND é um descritor do terreno. Isoladamente, ele não representa uma simulação hidráulica de inundação.
<b>Referências</b>
Rennó, C. D. et al. (2008). <i>HAND, a new terrain descriptor using SRTM-DEM: Mapping terra-firme rainforest environments in Amazonia</i>. Remote Sensing of Environment, 112(9), 3469&ndash;3481. <a href="https://doi.org/10.1016/j.rse.2008.03.018">DOI: 10.1016/j.rse.2008.03.018</a>.
Nobre, A. D. et al. (2011). <i>Height Above the Nearest Drainage &mdash; a hydrologically relevant new terrain model</i>. Journal of Hydrology, 404(1&ndash;2), 13&ndash;29. <a href="https://doi.org/10.1016/j.jhydrol.2011.03.051">DOI: 10.1016/j.jhydrol.2011.03.051</a>.
Documentação do GRASS GIS: <a href="https://grass.osgeo.org/grass-stable/manuals/r.fill.dir.html"><i>r.fill.dir</i></a>  e <a href="https://grass.osgeo.org/grass-stable/manuals/r.watershed.html"><i>r.watershed</i></a>.'''

    figure = 'images/tutorial/hydrology_hand.jpg'

    def shortHelpString(self):
            social_BW = Imgs().social_BW
            footer = '''<div align="center">
                          <img src="'''+ os.path.join(os.path.dirname(os.path.dirname(__file__)), self.figure) +'''">
                          </div>
                          <div align="right">
                          <p align="right">
                          <b>'''+self.tr('Author: Leandro Franca', 'Autor: Leandro França')+'''</b>
                          </p>'''+ social_BW + '''</div>
                        </div>'''
            return self.tr(self.txt_en, self.txt_pt) + footer

    INPUT = 'INPUT'
    CONDITION = 'CONDITION'
    THRESHOLD = 'THRESHOLD'
    THRESHOLD_UNIT = 'THRESHOLD_UNIT'
    EXTERNAL_OUTLET_MODE = 'EXTERNAL_OUTLET_MODE'
    REFERENCE_LEVEL = 'REFERENCE_LEVEL'
    MEMORY = 'MEMORY'
    CONDITIONED_DEM = 'CONDITIONED_DEM'
    FLOW_DIRECTION = 'FLOW_DIRECTION'
    FLOW_ACCUMULATION = 'FLOW_ACCUMULATION'
    DRAINAGE_RASTER = 'DRAINAGE_RASTER'
    DRAINAGE_VECTOR = 'DRAINAGE_VECTOR'
    HAND = 'HAND'

    def initAlgorithm(self, config=None):
        self.addParameter(
            QgsProcessingParameterRasterLayer(
                self.INPUT,
                self.tr('Input DEM', 'MDE de entrada'),
                [Qgis.ProcessingSourceType.TypeRaster],
            )
        )

        self.addParameter(
            QgsProcessingParameterBoolean(
                self.CONDITION,
                self.tr(
                    'Hydrologically condition the DEM (fill depressions)',
                    'Condicionar hidrologicamente o MDE (preencher depressões)',
                ),
                defaultValue=True,
            )
        )

        self.addParameter(
            QgsProcessingParameterNumber(
                self.THRESHOLD,
                self.tr(
                    'Drainage initiation threshold',
                    'Limiar para iniciar a drenagem',
                ),
                type=QgsProcessingParameterNumber.Double,
                minValue=0.000001,
                defaultValue=1000.0,
            )
        )

        self.threshold_units = [
            self.tr('Number of cells (pixels)', 'Número de células (pixels)'),
            self.tr('Square kilometres (km²)', 'Quilômetros quadrados (km²)'),
            self.tr('Hectares (ha)', 'Hectares (ha)'),
        ]
        self.addParameter(
            QgsProcessingParameterEnum(
                self.THRESHOLD_UNIT,
                self.tr('Threshold unit', 'Unidade do limiar'),
                options=self.threshold_units,
                defaultValue=0,
            )
        )

        self.external_outlet_modes = [
            self.tr(
                'Keep as NoData (strict drainage network)',
                'Manter como NoData (rede de drenagem estrita)',
            ),
            self.tr(
                'Use elevation of the outlet cell',
                'Usar a cota da célula de saída',
            ),
            self.tr(
                'Use a fixed reference level (sea/lake)',
                'Usar nível de referência fixo (mar/lagoa)',
            ),
        ]
        self.addParameter(
            QgsProcessingParameterEnum(
                self.EXTERNAL_OUTLET_MODE,
                self.tr(
                    'Flow paths leaving the valid DEM',
                    'Caminhos de fluxo que saem do MDE válido',
                ),
                options=self.external_outlet_modes,
                defaultValue=1,
            )
        )
        self.addParameter(
            QgsProcessingParameterNumber(
                self.REFERENCE_LEVEL,
                self.tr(
                    'Fixed reference level (m)',
                    'Nível de referência fixo (m)',
                ),
                type=QgsProcessingParameterNumber.Double,
                defaultValue=0.0,
                optional=True,
            )
        )

        memory_parameter = QgsProcessingParameterNumber(
            self.MEMORY,
            self.tr(
                'Memory available to GRASS (MB)',
                'Memória disponível para o GRASS (MB)',
            ),
            type=QgsProcessingParameterNumber.Integer,
            minValue=64,
            defaultValue=500,
        )
        self.addParameter(memory_parameter)

        self.addParameter(
            QgsProcessingParameterRasterDestination(
                self.CONDITIONED_DEM,
                self.tr('Conditioned DEM', 'MDE condicionado'),
            )
        )
        self.addParameter(
            QgsProcessingParameterRasterDestination(
                self.FLOW_DIRECTION,
                self.tr('D8 flow direction', 'Direção de fluxo D8'),
            )
        )
        self.addParameter(
            QgsProcessingParameterRasterDestination(
                self.FLOW_ACCUMULATION,
                self.tr('Flow accumulation', 'Acumulação de fluxo'),
            )
        )
        self.addParameter(
            QgsProcessingParameterRasterDestination(
                self.DRAINAGE_RASTER,
                self.tr('Drainage network (raster)', 'Rede de drenagem (raster)'),
            )
        )
        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.DRAINAGE_VECTOR,
                self.tr('Ordered drainage network', 'Rede de drenagem ordenada'),
                Qgis.ProcessingSourceType.TypeVectorLine,
            )
        )
        self.addParameter(
            QgsProcessingParameterRasterDestination(
                self.HAND,
                self.tr('HAND raster', 'Raster HAND'),
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        gdal.UseExceptions()

        dem_layer = self.parameterAsRasterLayer(parameters, self.INPUT, context)
        if dem_layer is None:
            raise QgsProcessingException(
                self.invalidSourceError(parameters, self.INPUT)
            )
        if not dem_layer.crs().isValid():
            raise QgsProcessingException(
                self.tr(
                    'The input DEM has no valid CRS!',
                    'O MDE de entrada não possui SRC válido!',
                )
            )
        source_path = dem_layer.dataProvider().dataSourceUri().split('|')[0]
        condition = self.parameterAsBool(parameters, self.CONDITION, context)
        threshold_value = self.parameterAsDouble(
            parameters, self.THRESHOLD, context
        )
        threshold_unit = self.parameterAsEnum(
            parameters, self.THRESHOLD_UNIT, context
        )
        external_outlet_mode = self.parameterAsEnum(
            parameters, self.EXTERNAL_OUTLET_MODE, context
        )
        reference_level = self.parameterAsDouble(
            parameters, self.REFERENCE_LEVEL, context
        )
        memory = self.parameterAsInt(parameters, self.MEMORY, context)

        conditioned_path = self.parameterAsOutputLayer(
            parameters, self.CONDITIONED_DEM, context
        )
        direction_path = self.parameterAsOutputLayer(
            parameters, self.FLOW_DIRECTION, context
        )
        accumulation_path = self.parameterAsOutputLayer(
            parameters, self.FLOW_ACCUMULATION, context
        )
        drainage_raster_path = self.parameterAsOutputLayer(
            parameters, self.DRAINAGE_RASTER, context
        )
        hand_path = self.parameterAsOutputLayer(parameters, self.HAND, context)
        self.HAND_PATH = hand_path

        self._validate_input_raster(source_path)
        is_geographic = dem_layer.crs().isGeographic()
        metre_factor = (
            None if is_geographic
            else self._linear_unit_to_metre(dem_layer.crs())
        )
        if not is_geographic and metre_factor is None:
            raise QgsProcessingException(
                self.tr(
                    'The linear unit of the DEM CRS could not be converted to metres.',
                    'Não foi possível converter para metros a unidade linear do SRC do MDE.',
                )
            )
        distance_area = self._distance_area(
            dem_layer.crs(), context
        )
        if is_geographic:
            feedback.pushInfo(
                self.tr(
                    'The DEM uses a geographic CRS. Cell areas and vector lengths will be measured geodesically.',
                    'O MDE utiliza um SRC geográfico. As áreas das células e os comprimentos vetoriais serão medidos geodesicamente.',
                )
            )

        feedback.pushInfo(
            self.tr('Preparing the elevation model...', 'Preparando o modelo de elevação...')
        )
        if condition:
            fill_algorithm = self._grass_algorithm('r.fill.dir')
            fill_parameters = self._supported_parameters(
                fill_algorithm,
                {
                    'input': source_path,
                    'format': 0,
                    '-f': False,
                    'output': conditioned_path,
                    'direction': QgsProcessing.TEMPORARY_OUTPUT,
                    'areas': QgsProcessing.TEMPORARY_OUTPUT,
                },
            )
            processing.run(
                fill_algorithm,
                fill_parameters,
                context=context,
                feedback=feedback,
                is_child_algorithm=True,
            )
        else:
            feedback.pushInfo(
                self.tr(
                    'The DEM was marked as already conditioned. Copying it without changing elevations...',
                    'O MDE foi indicado como já condicionado. Copiando-o sem alterar as altitudes...',
                )
            )
            processing.run(
                'gdal:translate',
                {
                    'INPUT': source_path,
                    'TARGET_CRS': None,
                    'NODATA': None,
                    'COPY_SUBDATASETS': False,
                    'OPTIONS': 'COMPRESS=LZW|TILED=YES|BIGTIFF=IF_SAFER',
                    'EXTRA': '',
                    'DATA_TYPE': 0,
                    'OUTPUT': conditioned_path,
                },
                context=context,
                feedback=feedback,
                is_child_algorithm=True,
            )

        if feedback.isCanceled():
            return {}

        feedback.pushInfo(
            self.tr(
                'Calculating D8 flow direction and flow accumulation...',
                'Calculando a direção de fluxo D8 e a acumulação de fluxo...',
            )
        )
        watershed_algorithm = self._grass_algorithm('r.watershed')
        watershed_parameters = self._supported_parameters(
            watershed_algorithm,
            {
                'elevation': conditioned_path,
                'convergence': 5,
                'memory': memory,
                '-s': True,
                '-m': False,
                '-4': False,
                '-a': False,
                '-b': False,
                'accumulation': accumulation_path,
                'drainage': direction_path,
            },
        )
        processing.run(
            watershed_algorithm,
            watershed_parameters,
            context=context,
            feedback=feedback,
            is_child_algorithm=True,
        )

        if feedback.isCanceled():
            return {}

        feedback.pushInfo(
            self.tr(
                'Reading hydrological rasters...',
                'Lendo os rasters hidrológicos...',
            )
        )
        dem_dataset = gdal.Open(conditioned_path, gdal.GA_ReadOnly)
        direction_dataset = gdal.Open(direction_path, gdal.GA_ReadOnly)
        accumulation_dataset = gdal.Open(accumulation_path, gdal.GA_ReadOnly)
        if not dem_dataset or not direction_dataset or not accumulation_dataset:
            raise QgsProcessingException(
                self.tr(
                    'One or more intermediate rasters could not be opened.',
                    'Não foi possível abrir um ou mais rasters intermediários.',
                )
            )

        self._validate_matching_grids(
            dem_dataset, direction_dataset, accumulation_dataset
        )
        rows = dem_dataset.RasterYSize
        cols = dem_dataset.RasterXSize
        cell_count = rows * cols
        if cell_count > 100_000_000:
            raise QgsProcessingException(
                self.tr(
                    'The raster has more than 100 million cells. Clip the DEM to the study area or use a coarser resolution.',
                    'O raster possui mais de 100 milhões de células. Recorte o MDE para a área de estudo ou utilize uma resolução mais grosseira.',
                )
            )
        if cell_count > 25_000_000:
            feedback.pushWarning(
                self.tr(
                    'This raster has more than 25 million cells. The HAND calculation may require substantial RAM; clipping the DEM is recommended on computers with limited memory.',
                    'Este raster possui mais de 25 milhões de células. O cálculo do HAND pode exigir muita memória RAM; recomenda-se recortar o MDE em computadores com memória limitada.',
                )
            )

        geotransform = dem_dataset.GetGeoTransform()
        pixel_area_m2 = self._representative_pixel_area_m2(
            geotransform=geotransform,
            rows=rows,
            cols=cols,
            is_geographic=is_geographic,
            metre_factor=metre_factor,
            distance_area=distance_area,
        )
        if pixel_area_m2 <= 0:
            raise QgsProcessingException(
                self.tr(
                    'The DEM has an invalid pixel area.',
                    'O MDE possui área de pixel inválida.',
                )
            )

        threshold_cells = self._threshold_in_cells(
            threshold_value, threshold_unit, pixel_area_m2
        )
        feedback.pushInfo(
            self.tr(
                'Drainage threshold: {:.0f} cells (approximately {:.6f} km²).',
                'Limiar de drenagem: {:.0f} células (aproximadamente {:.6f} km²).',
            ).format(
                threshold_cells,
                threshold_cells * pixel_area_m2 / 1_000_000.0,
            )
        )
        if is_geographic:
            feedback.pushWarning(
                self.tr(
                    'In a geographic CRS the physical area of a pixel varies with latitude. The km²/ha conversion and the up_area_km2 vector attribute are estimates based on the central pixel of the DEM.',
                    'Em SRC geográfico, a área física do pixel varia com a latitude. A conversão para km²/ha e o atributo vetorial up_area_km2 são estimativas baseadas no pixel central do MDE.',
                )
            )

        dem_band = dem_dataset.GetRasterBand(1)
        direction_band = direction_dataset.GetRasterBand(1)
        accumulation_band = accumulation_dataset.GetRasterBand(1)
        dem = dem_band.ReadAsArray().astype(np.float32, copy=False)
        direction = direction_band.ReadAsArray().astype(np.int16, copy=False)
        accumulation = accumulation_band.ReadAsArray().astype(
            np.float64, copy=False
        )

        valid = self._valid_mask(dem, dem_band.GetNoDataValue())
        valid &= self._valid_mask(
            direction, direction_band.GetNoDataValue()
        )
        accumulation_valid = self._valid_mask(
            accumulation, accumulation_band.GetNoDataValue()
        )

        absolute_accumulation = np.abs(accumulation)
        stream = (
            valid
            & accumulation_valid
            & (absolute_accumulation >= threshold_cells)
        )
        stream_count = int(np.count_nonzero(stream))
        if stream_count == 0:
            raise QgsProcessingException(
                self.tr(
                    'The selected threshold did not generate any drainage cells. Reduce the minimum contributing area.',
                    'O limiar selecionado não gerou células de drenagem. Reduza a área mínima de contribuição.',
                )
            )

        feedback.pushInfo(
            self.tr(
                'Drainage network generated with {:,} raster cells.',
                'Rede de drenagem gerada com {:,} células raster.',
            ).format(stream_count)
        )

        downstream = _build_downstream(direction, valid)
        stream_flat = stream.ravel()
        external_outlet_flat = None
        if external_outlet_mode > 0:
            external_outlet_flat = _build_external_outlets(
                direction, valid, downstream
            )

        feedback.pushInfo(
            self.tr('Calculating HAND...', 'Calculando o HAND...')
        )
        target = _calculate_hand_targets(
            downstream, stream_flat, external_outlet_flat
        )
        dem_flat = dem.ravel()
        valid_flat = valid.ravel()
        resolved = valid_flat & (target >= 0)
        unresolved_count = int(np.count_nonzero(valid_flat & ~resolved))

        hand_flat = np.full(cell_count, -9999.0, dtype=np.float32)
        resolved_index = np.flatnonzero(resolved)
        reference_elevation = dem_flat[target[resolved_index]].copy()
        external_resolved = np.zeros(resolved_index.size, dtype=bool)
        if external_outlet_flat is not None and resolved_index.size:
            external_resolved = external_outlet_flat[
                target[resolved_index]
            ]
            if external_outlet_mode == 2:
                reference_elevation[external_resolved] = reference_level
        hand_flat[resolved_index] = (
            dem_flat[resolved_index] - reference_elevation
        )
        external_resolved_count = int(np.count_nonzero(external_resolved))
        if external_resolved_count:
            if external_outlet_mode == 1:
                message = self.tr(
                    '{} terrain cells were referenced to the elevation of their external outlet cell.',
                    '{} células do terreno foram referenciadas à cota de sua célula de saída externa.',
                )
            else:
                message = self.tr(
                    '{} terrain cells were referenced to the fixed level of {:.3f} m.',
                    '{} células do terreno foram referenciadas ao nível fixo de {:.3f} m.',
                )
            feedback.pushInfo(
                message.format(external_resolved_count, reference_level)
                if external_outlet_mode == 2
                else message.format(external_resolved_count)
            )
        tiny_negative = resolved & (hand_flat < 0) & (hand_flat > -0.001)
        hand_flat[tiny_negative] = 0.0
        substantial_negative = resolved & (hand_flat < -0.001)
        negative_count = int(np.count_nonzero(substantial_negative))
        if negative_count:
            feedback.pushWarning(
                self.tr(
                    '{} HAND cells have negative values. Check DEM conditioning and vertical units.',
                    '{} células do HAND possuem valores negativos. Verifique o condicionamento do MDE e as unidades verticais.',
                ).format(negative_count)
            )
        if unresolved_count:
            feedback.pushInfo(
                self.tr(
                    '{} valid terrain cells reach neither the extracted drainage nor an identifiable external outlet and were written as NoData.',
                    '{} células válidas do terreno não alcançam a drenagem extraída nem uma saída externa identificável e foram gravadas como NoData.',
                ).format(unresolved_count)
            )

        drainage = np.full((rows, cols), 255, dtype=np.uint8)
        drainage[valid] = 0
        drainage[stream] = 1
        self._write_raster(
            drainage_raster_path,
            drainage,
            dem_dataset,
            gdal.GDT_Byte,
            255,
        )
        self._write_raster(
            hand_path,
            hand_flat.reshape(rows, cols),
            dem_dataset,
            gdal.GDT_Float32,
            -9999.0,
        )

        feedback.pushInfo(
            self.tr(
                'Vectorizing and ordering the drainage network...',
                'Vetorizando e ordenando a rede de drenagem...',
            )
        )
        fields = self._drainage_fields()
        sink, vector_destination = self.parameterAsSink(
            parameters,
            self.DRAINAGE_VECTOR,
            context,
            fields,
            QgsWkbTypes.LineString,
            dem_layer.crs(),
        )
        if sink is None:
            raise QgsProcessingException(
                self.invalidSinkError(parameters, self.DRAINAGE_VECTOR)
            )

        vector_result = self._create_vector_network(
            sink=sink,
            fields=fields,
            stream_flat=stream_flat,
            downstream=downstream,
            accumulation=absolute_accumulation.ravel(),
            dem=dem_flat,
            rows=rows,
            cols=cols,
            geotransform=geotransform,
            pixel_area_m2=pixel_area_m2,
            metre_factor=metre_factor,
            distance_area=distance_area,
            feedback=feedback,
        )
        if feedback.isCanceled():
            return {}
        feedback.pushInfo(
            self.tr(
                '{} drainage reaches created. Maximum Strahler order: {}.',
                '{} trechos de drenagem criados. Ordem máxima de Strahler: {}.',
            ).format(vector_result['reach_count'], vector_result['max_strahler'])
        )

        dem_dataset = None
        direction_dataset = None
        accumulation_dataset = None

        results = {
            self.CONDITIONED_DEM: conditioned_path,
            self.FLOW_DIRECTION: direction_path,
            self.FLOW_ACCUMULATION: accumulation_path,
            self.DRAINAGE_RASTER: drainage_raster_path,
            self.DRAINAGE_VECTOR: vector_destination,
            self.HAND: hand_path,
        }

        group_name = self.tr(
            'HAND Model — {}',
            'Modelo HAND — {}',
        ).format(dem_layer.name())
        self._set_output_postprocessors(context, results, group_name)
        feedback.pushInfo(
            self.tr(
                'Operation completed successfully!',
                'Operação finalizada com sucesso!',
            )
        )
        feedback.pushInfo(
            self.tr(
                'Leandro Franca - Cartographic Engineer',
                'Leandro França - Eng Cart',
            )
        )
        return results

    def postProcessAlgorithm(self, context, feedback):
        """Apply the HAND QML through LFTools Magic Styles.

        Layer naming, drainage symbology, visibility and panel order are
        completed by the output post-processors after QGIS loads each layer.
        """
        feedback.pushInfo(
            self.tr(
                'Post-processing: applying the HAND raster style...',
                'Pós-processamento: aplicando a simbologia do raster HAND...',
            )
        )
        hand_layer = QgsProcessingUtils.mapLayerFromString(
            self.HAND_PATH, context
        )
        if hand_layer is None:
            feedback.pushWarning(
                self.tr(
                    'The HAND layer could not be loaded to apply its style.',
                    'Não foi possível carregar a camada HAND para aplicar sua simbologia.',
                )
            )
            return {}

        processing.run(
            'lftools:magicstyles',
            {
                'LAYER': hand_layer,
                'STYLE_POINT': 0,
                'STYLE_LINE': 0,
                'STYLE_POLYGON': 0,
                'STYLE_RASTER': 9,
            },
            context=context,
            feedback=feedback,
            is_child_algorithm=True,
        )
        feedback.pushInfo(
            self.tr(
                'Post-processing: HAND raster style applied.',
                'Pós-processamento: simbologia do raster HAND aplicada.',
            )
        )
        return {}

    def _grass_algorithm(self, module_name):
        registry = QgsApplication.processingRegistry()
        for provider_id in ('grass', 'grass7'):
            algorithm_id = '{}:{}'.format(provider_id, module_name)
            if registry.algorithmById(algorithm_id) is not None:
                return algorithm_id
        raise QgsProcessingException(
            self.tr(
                'The GRASS Processing provider or the {} module is not available. Install/enable GRASS in QGIS and try again.',
                'O provedor GRASS do Processamento ou o módulo {} não está disponível. Instale/ative o GRASS no QGIS e tente novamente.',
            ).format(module_name)
        )

    @staticmethod
    def _supported_parameters(algorithm_id, parameters):
        algorithm = QgsApplication.processingRegistry().algorithmById(
            algorithm_id
        )
        if algorithm is None:
            return parameters
        supported = {
            definition.name() for definition in algorithm.parameterDefinitions()
        }
        return {
            name: value
            for name, value in parameters.items()
            if name in supported
        }

    def _validate_input_raster(self, path):
        dataset = gdal.Open(path, gdal.GA_ReadOnly)
        if dataset is None:
            raise QgsProcessingException(
                self.tr(
                    'The input DEM could not be opened.',
                    'Não foi possível abrir o MDE de entrada.',
                )
            )
        if dataset.RasterCount != 1:
            dataset = None
            raise QgsProcessingException(
                self.tr(
                    'The input DEM must have exactly one band.',
                    'O MDE de entrada deve possuir exatamente uma banda.',
                )
            )
        geotransform = dataset.GetGeoTransform()
        if not geotransform or geotransform[1] == 0 or geotransform[5] == 0:
            dataset = None
            raise QgsProcessingException(
                self.tr(
                    'The input DEM has an invalid geotransform.',
                    'O MDE de entrada possui geotransformação inválida.',
                )
            )
        dataset = None

    def _linear_unit_to_metre(self, crs):
        try:
            factor = QgsUnitTypes.fromUnitToUnitFactor(
                crs.mapUnits(), Qgis.DistanceUnit.Meters
            )
            if not np.isfinite(factor) or factor <= 0:
                return None
            return factor
        except Exception:
            return None

    @staticmethod
    def _threshold_in_cells(value, unit, pixel_area_m2):
        if unit == 0:
            return float(max(1, ceil(value)))
        if unit == 1:
            return value * 1_000_000.0 / pixel_area_m2
        return value * 10_000.0 / pixel_area_m2

    @staticmethod
    def _distance_area(crs, context):
        distance_area = QgsDistanceArea()
        distance_area.setSourceCrs(crs, context.transformContext())
        ellipsoid = QgsProject.instance().ellipsoid()
        if not ellipsoid or str(ellipsoid).upper() in ('NONE', 'NOT_SET'):
            ellipsoid = crs.ellipsoidAcronym()
        if not ellipsoid and crs.isGeographic():
            ellipsoid = 'WGS84'
        if ellipsoid:
            distance_area.setEllipsoid(ellipsoid)
        return distance_area

    @staticmethod
    def _representative_pixel_area_m2(
        geotransform,
        rows,
        cols,
        is_geographic,
        metre_factor,
        distance_area,
    ):
        pixel_area_map_units = abs(
            geotransform[1] * geotransform[5]
            - geotransform[2] * geotransform[4]
        )
        if not is_geographic:
            return pixel_area_map_units * metre_factor * metre_factor

        row = rows // 2
        col = cols // 2

        def corner(column, line):
            return QgsPointXY(
                geotransform[0]
                + column * geotransform[1]
                + line * geotransform[2],
                geotransform[3]
                + column * geotransform[4]
                + line * geotransform[5],
            )

        ring = [
            corner(col, row),
            corner(col + 1, row),
            corner(col + 1, row + 1),
            corner(col, row + 1),
            corner(col, row),
        ]
        geometry = QgsGeometry.fromPolygonXY([ring])
        return abs(float(distance_area.measureArea(geometry)))

    @staticmethod
    def _valid_mask(array, nodata):
        valid = np.isfinite(array)
        if nodata is not None:
            if np.isnan(nodata):
                valid &= ~np.isnan(array)
            else:
                valid &= array != nodata
        return valid

    def _validate_matching_grids(self, *datasets):
        reference = datasets[0]
        reference_size = (reference.RasterXSize, reference.RasterYSize)
        reference_transform = reference.GetGeoTransform()
        reference_projection = reference.GetProjection()
        for dataset in datasets[1:]:
            if (dataset.RasterXSize, dataset.RasterYSize) != reference_size:
                raise QgsProcessingException(
                    self.tr(
                        'The hydrological rasters have different dimensions.',
                        'Os rasters hidrológicos possuem dimensões diferentes.',
                    )
                )
            if not np.allclose(
                dataset.GetGeoTransform(),
                reference_transform,
                rtol=0,
                atol=1e-9,
            ):
                raise QgsProcessingException(
                    self.tr(
                        'The hydrological rasters are not aligned.',
                        'Os rasters hidrológicos não estão alinhados.',
                    )
                )
            reference_srs = osr.SpatialReference()
            dataset_srs = osr.SpatialReference()
            reference_srs.ImportFromWkt(reference_projection)
            dataset_srs.ImportFromWkt(dataset.GetProjection())
            if not bool(reference_srs.IsSame(dataset_srs)):
                raise QgsProcessingException(
                    self.tr(
                        'The hydrological rasters have different coordinate reference systems.',
                        'Os rasters hidrológicos possuem sistemas de referência diferentes.',
                    )
                )

    @staticmethod
    def _write_raster(path, array, reference, data_type, nodata):
        driver = gdal.GetDriverByName('GTiff')
        dataset = driver.Create(
            path,
            reference.RasterXSize,
            reference.RasterYSize,
            1,
            data_type,
            options=[
                'COMPRESS=LZW',
                'TILED=YES',
                'BIGTIFF=IF_SAFER',
            ],
        )
        if dataset is None:
            raise QgsProcessingException(
                'Could not create output raster: {}'.format(path)
            )
        dataset.SetGeoTransform(reference.GetGeoTransform())
        dataset.SetProjection(reference.GetProjection())
        band = dataset.GetRasterBand(1)
        band.SetNoDataValue(nodata)
        band.WriteArray(array)
        band.FlushCache()
        dataset.FlushCache()
        dataset = None

    @staticmethod
    def _drainage_fields():
        fields = QgsFields()
        fields.append(QgsField('stream_id', QMetaType.Type.Int))
        fields.append(QgsField('from_node', QMetaType.Type.Int))
        fields.append(QgsField('to_node', QMetaType.Type.Int))
        fields.append(QgsField('strahler', QMetaType.Type.Int))
        fields.append(QgsField('shreve', QMetaType.Type.LongLong))
        fields.append(QgsField('length_m', QMetaType.Type.Double, len=20, prec=3))
        fields.append(QgsField('up_area_km2', QMetaType.Type.Double, len=20, prec=6))
        fields.append(QgsField('z_start', QMetaType.Type.Double, len=20, prec=3))
        fields.append(QgsField('z_end', QMetaType.Type.Double, len=20, prec=3))
        fields.append(QgsField('slope_pct', QMetaType.Type.Double, len=20, prec=6))
        return fields

    def _create_vector_network(
        self,
        sink,
        fields,
        stream_flat,
        downstream,
        accumulation,
        dem,
        rows,
        cols,
        geotransform,
        pixel_area_m2,
        metre_factor,
        distance_area,
        feedback,
    ):
        del rows  # dimensions are implicit in flat indices and cols
        indegree, strahler, shreve, processed = _calculate_stream_orders(
            stream_flat, downstream
        )
        stream_index = np.flatnonzero(stream_flat)
        if processed != stream_index.size:
            feedback.pushWarning(
                self.tr(
                    '{} drainage cells could not be topologically ordered. Check the D8 raster for cycles.',
                    '{} células de drenagem não puderam ser ordenadas topologicamente. Verifique se existem ciclos no raster D8.',
                ).format(stream_index.size - processed)
            )

        downstream_is_stream = np.zeros(downstream.size, dtype=bool)
        linked = downstream >= 0
        linked_index = np.flatnonzero(linked)
        downstream_is_stream[linked_index] = stream_flat[
            downstream[linked_index]
        ]

        node_mask = stream_flat & (
            (indegree != 1) | ~downstream_is_stream
        )
        node_cells = np.flatnonzero(node_mask)
        node_ids = np.full(downstream.size, -1, dtype=np.int32)
        node_ids[node_cells] = np.arange(1, node_cells.size + 1, dtype=np.int32)

        start_cells = np.flatnonzero(
            stream_flat & (indegree != 1) & downstream_is_stream
        )
        reach_count = 0
        maximum_strahler = 0
        total_starts = max(1, start_cells.size)

        for position, start in enumerate(start_cells):
            if feedback.isCanceled():
                break

            cells = [int(start)]
            visited = {int(start)}
            current = int(start)
            while True:
                next_cell = int(downstream[current])
                if next_cell < 0 or not stream_flat[next_cell]:
                    break
                if next_cell in visited:
                    feedback.pushWarning(
                        self.tr(
                            'A cycle was found in the D8 drainage raster; the affected reach was truncated.',
                            'Foi encontrado um ciclo no raster de drenagem D8; o trecho afetado foi interrompido.',
                        )
                    )
                    break
                cells.append(next_cell)
                visited.add(next_cell)
                current = next_cell
                if indegree[current] != 1 or not downstream_is_stream[current]:
                    break

            if len(cells) < 2:
                continue

            points = [
                self._cell_centre(cell, cols, geotransform)
                for cell in cells
            ]
            geometry = QgsGeometry.fromPolylineXY(points)
            length_m = (
                float(distance_area.measureLength(geometry))
                if metre_factor is None
                else geometry.length() * metre_factor
            )
            z_start = float(dem[start])
            z_end = float(dem[current])
            attribute_end = (
                cells[-2]
                if indegree[current] > 1 and len(cells) > 1
                else current
            )
            slope_pct = (
                100.0 * (z_start - z_end) / length_m
                if length_m > 0
                else 0.0
            )
            reach_count += 1
            reach_order = int(strahler[start])
            maximum_strahler = max(maximum_strahler, reach_order)

            feature = QgsFeature(fields)
            feature.setGeometry(geometry)
            feature.setAttributes(
                [
                    reach_count,
                    int(node_ids[start]),
                    int(node_ids[current]),
                    reach_order,
                    int(shreve[start]),
                    float(length_m),
                    float(accumulation[attribute_end] * pixel_area_m2 / 1_000_000.0),
                    z_start,
                    z_end,
                    float(slope_pct),
                ]
            )
            sink.addFeature(feature, QgsFeatureSink.FastInsert)
            feedback.setProgress(
                75 + int(25.0 * (position + 1) / total_starts)
            )

        return {
            'reach_count': reach_count,
            'max_strahler': maximum_strahler,
        }

    @staticmethod
    def _cell_centre(cell, cols, geotransform):
        row = cell // cols
        col = cell - row * cols
        x = (
            geotransform[0]
            + (col + 0.5) * geotransform[1]
            + (row + 0.5) * geotransform[2]
        )
        y = (
            geotransform[3]
            + (col + 0.5) * geotransform[4]
            + (row + 0.5) * geotransform[5]
        )
        return QgsPointXY(x, y)

    def _set_output_postprocessors(self, context, results, group_name):
        global _OUTPUT_GROUP, _OUTPUT_GROUP_NAME
        names = {
            self.CONDITIONED_DEM: self.tr(
                'Conditioned DEM', 'MDE condicionado'
            ),
            self.FLOW_DIRECTION: self.tr(
                'D8 flow direction', 'Direção de fluxo D8'
            ),
            self.FLOW_ACCUMULATION: self.tr(
                'Flow accumulation', 'Acumulação de fluxo'
            ),
            self.DRAINAGE_RASTER: self.tr(
                'Drainage network (raster)', 'Rede de drenagem (raster)'
            ),
            self.DRAINAGE_VECTOR: self.tr(
                'Ordered drainage network', 'Rede de drenagem ordenada'
            ),
            self.HAND: self.tr('HAND', 'HAND'),
        }
        _POST_PROCESSORS.clear()
        _OUTPUT_LAYER_IDS.clear()
        _EXPECTED_OUTPUTS.clear()
        _OUTPUT_GROUP = None
        _OUTPUT_GROUP_NAME = group_name
        for output_name, destination in results.items():
            if not destination or not context.willLoadLayerOnCompletion(destination):
                continue
            _EXPECTED_OUTPUTS.add(output_name)
            postprocessor = HandOutputPostProcessor(
                output_name=output_name,
                layer_name=names[output_name],
            )
            _POST_PROCESSORS.append(postprocessor)
            context.layerToLoadOnCompletionDetails(
                destination
            ).setPostProcessor(postprocessor)


class HandOutputPostProcessor(QgsProcessingLayerPostProcessorInterface):

    def __init__(self, output_name, layer_name):
        self.output_name = output_name
        self.name = layer_name
        super().__init__()

    def postProcessLayer(self, layer, context, feedback):
        del context
        layer.setName(self.name)
        _OUTPUT_LAYER_IDS[self.output_name] = layer.id()
        feedback.pushInfo(
            self._tr(
                'Post-processing output: {}.',
                'Pós-processando a saída: {}.',
            ).format(self.name)
        )

        if self.output_name == 'DRAINAGE_VECTOR':
            self._apply_drainage_style(layer, feedback)

        self._organize_output_layers()
        QTimer.singleShot(0, self._organize_output_layers)
        if _EXPECTED_OUTPUTS.issubset(_OUTPUT_LAYER_IDS):
            feedback.pushInfo(
                self._tr(
                    'Post-processing completed: output group, layer order and visibility configured.',
                    'Pós-processamento concluído: grupo de saída, ordem e visibilidade das camadas configurados.',
                )
            )

    @staticmethod
    def _tr(*strings):
        return translate(strings, QgsApplication.locale()[:2])

    @staticmethod
    def _apply_drainage_style(layer, feedback):
        field_index = layer.fields().indexFromName('strahler')
        if field_index < 0:
            feedback.pushWarning(
                'The strahler field was not found; the drainage style was not applied.'
            )
            return

        widths = {
            1: 0.25,
            2: 0.40,
            3: 0.60,
            4: 0.85,
        }
        values = sorted(
            int(value)
            for value in layer.uniqueValues(field_index)
            if value is not None
        )
        categories = []
        for order in values:
            width = widths.get(order, 1.10)
            symbol = QgsLineSymbol.createSimple(
                {
                    'color': QColor('#1565c0').name(),
                    'width': str(width),
                    'line_style': 'solid',
                    'capstyle': 'round',
                    'joinstyle': 'round',
                }
            )
            label = 'Strahler {}'.format(order)
            categories.append(QgsRendererCategory(order, symbol, label))

        if not categories:
            feedback.pushWarning(
                'No valid Strahler values were found; the drainage style was not applied.'
            )
            return

        layer.setRenderer(
            QgsCategorizedSymbolRenderer('strahler', categories)
        )
        layer.triggerRepaint()
        feedback.pushInfo(
            HandOutputPostProcessor._tr(
                'Drainage symbology applied using the Strahler order.',
                'Simbologia da drenagem aplicada pela ordem de Strahler.',
            )
        )

    @staticmethod
    def _organize_output_layers():
        root = QgsProject.instance().layerTreeRoot()
        group = HandOutputPostProcessor._output_group(root)
        ordered_nodes = []

        for output_name in _OUTPUT_ORDER:
            layer_id = _OUTPUT_LAYER_IDS.get(output_name)
            node = root.findLayer(layer_id) if layer_id else None
            if node is not None:
                ordered_nodes.append((output_name, node))

        if not ordered_nodes:
            return

        clones = [
            (output_name, node.clone())
            for output_name, node in ordered_nodes
        ]
        # Insert the clones first. Removing all original nodes before insertion
        # makes QGIS interpret the temporary absence as removal of the layers
        # from the project.
        for index, (output_name, clone) in enumerate(clones):
            group.insertChildNode(index, clone)
            clone.setItemVisibilityChecked(
                output_name in ('DRAINAGE_VECTOR', 'HAND')
            )

        for output_name, node in ordered_nodes:
            parent = node.parent()
            if parent is not None:
                parent.removeChildNode(node)

    @staticmethod
    def _output_group(root):
        global _OUTPUT_GROUP

        if _OUTPUT_GROUP is not None and _OUTPUT_GROUP.parent() is not None:
            return _OUTPUT_GROUP

        base_name = _OUTPUT_GROUP_NAME or 'Modelo HAND'
        group_name = base_name
        suffix = 2
        while root.findGroup(group_name) is not None:
            group_name = '{} ({})'.format(base_name, suffix)
            suffix += 1

        _OUTPUT_GROUP = root.insertGroup(0, group_name)
        _OUTPUT_GROUP.setExpanded(True)
        return _OUTPUT_GROUP
