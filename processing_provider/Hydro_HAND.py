# -*- coding: utf-8 -*-

"""Generate the HAND terrain model from a DEM."""

__author__ = 'Leandro França'
__date__ = '2026-09-18'
__copyright__ = '(C) 2026, Leandro França'

import os

import numpy as np
from osgeo import gdal

from qgis.PyQt.QtGui import QIcon
from qgis.core import (
    Qgis,
    QgsApplication,
    QgsProcessingAlgorithm,
    QgsProcessingException,
    QgsProcessingParameterBoolean,
    QgsProcessingParameterEnum,
    QgsProcessingParameterFeatureSink,
    QgsProcessingParameterNumber,
    QgsProcessingParameterRasterDestination,
    QgsProcessingParameterRasterLayer,
    QgsProcessingUtils,
    QgsWkbTypes,
)

import processing

from lftools.geocapt.imgs import Imgs
from lftools.translations.translate import translate

from lftools.geocapt.hydro_utils import (
    build_downstream,
    build_external_outlets,
    calculate_d8,
    calculate_hand_targets,
    condition_dem,
    configure_output_postprocessors,
    create_drainage_raster,
    create_vector_network,
    distance_area,
    drainage_fields,
    guard_raster_size,
    linear_unit_to_metre,
    open_hydrology_rasters,
    read_hydrology_arrays,
    representative_pixel_area_m2,
    threshold_in_cells,
    validate_input_raster,
    write_raster,
)


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
Documentação do GRASS GIS: <a href="https://grass.osgeo.org/grass-stable/manuals/r.fill.dir.html"><i>r.fill.dir</i></a> e <a href="https://grass.osgeo.org/grass-stable/manuals/r.watershed.html"><i>r.watershed</i></a>.'''

    figure = 'images/tutorial/hydrology_hand.jpg'

    def shortHelpString(self):
        social_BW = Imgs().social_BW
        footer = '''<div align="center">
                      <img src="''' + os.path.join(
                          os.path.dirname(os.path.dirname(__file__)), self.figure
                      ) + '''">
                      </div>
                      <div align="right">
                      <p align="right">
                      <b>''' + self.tr(
                          'Author: Leandro Franca', 'Autor: Leandro França'
                      ) + '''</b>
                      </p>''' + social_BW + '''</div>
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
        del config
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
        self.addParameter(
            QgsProcessingParameterNumber(
                self.MEMORY,
                self.tr(
                    'Memory available to GRASS (MB)',
                    'Memória disponível para o GRASS (MB)',
                ),
                type=QgsProcessingParameterNumber.Integer,
                minValue=64,
                defaultValue=500,
            )
        )
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

        validate_input_raster(source_path, self.tr)
        is_geographic = dem_layer.crs().isGeographic()
        metre_factor = (
            None if is_geographic else linear_unit_to_metre(dem_layer.crs())
        )
        if not is_geographic and metre_factor is None:
            raise QgsProcessingException(
                self.tr(
                    'The linear unit of the DEM CRS could not be converted to metres.',
                    'Não foi possível converter para metros a unidade linear do SRC do MDE.',
                )
            )
        distance_calculator = distance_area(dem_layer.crs(), context)
        if is_geographic:
            feedback.pushInfo(
                self.tr(
                    'The DEM uses a geographic CRS. Cell areas and vector lengths will be measured geodesically.',
                    'O MDE utiliza um SRC geográfico. As áreas das células e os comprimentos vetoriais serão medidos geodesicamente.',
                )
            )

        feedback.pushInfo(
            self.tr(
                'Preparing the elevation model...',
                'Preparando o modelo de elevação...',
            )
        )
        condition_dem(
            source_path,
            conditioned_path,
            condition,
            context,
            feedback,
            self.tr,
        )
        if feedback.isCanceled():
            return {}
        feedback.pushInfo(
            self.tr(
                'Calculating D8 flow direction and flow accumulation...',
                'Calculando a direção de fluxo D8 e a acumulação de fluxo...',
            )
        )
        calculate_d8(
            conditioned_path,
            direction_path,
            accumulation_path,
            memory,
            context,
            feedback,
            self.tr,
        )
        if feedback.isCanceled():
            return {}

        dem_dataset, direction_dataset, accumulation_dataset = (
            open_hydrology_rasters(
                conditioned_path,
                direction_path,
                accumulation_path,
                self.tr,
            )
        )
        rows = dem_dataset.RasterYSize
        cols = dem_dataset.RasterXSize
        cell_count = rows * cols
        guard_raster_size(cell_count, feedback, self.tr, hand=True)
        geotransform = dem_dataset.GetGeoTransform()
        pixel_area_m2 = representative_pixel_area_m2(
            geotransform,
            rows,
            cols,
            is_geographic,
            metre_factor,
            distance_calculator,
        )
        if pixel_area_m2 <= 0:
            raise QgsProcessingException(
                self.tr(
                    'The DEM has an invalid pixel area.',
                    'O MDE possui área de pixel inválida.',
                )
            )
        threshold_cells = threshold_in_cells(
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

        dem, direction, accumulation, valid, accumulation_valid = (
            read_hydrology_arrays(
                dem_dataset, direction_dataset, accumulation_dataset
            )
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

        downstream = build_downstream(direction, valid)
        stream_flat = stream.ravel()
        external_outlet_flat = None
        if external_outlet_mode > 0:
            external_outlet_flat = build_external_outlets(
                direction, valid, downstream
            )

        feedback.pushInfo(self.tr('Calculating HAND...', 'Calculando o HAND...'))
        target = calculate_hand_targets(
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
            external_resolved = external_outlet_flat[target[resolved_index]]
            if external_outlet_mode == 2:
                reference_elevation[external_resolved] = reference_level
        hand_flat[resolved_index] = dem_flat[resolved_index] - reference_elevation
        external_resolved_count = int(np.count_nonzero(external_resolved))
        if external_resolved_count:
            if external_outlet_mode == 1:
                feedback.pushInfo(
                    self.tr(
                        '{} terrain cells were referenced to the elevation of their external outlet cell.',
                        '{} células do terreno foram referenciadas à cota de sua célula de saída externa.',
                    ).format(external_resolved_count)
                )
            else:
                feedback.pushInfo(
                    self.tr(
                        '{} terrain cells were referenced to the fixed level of {:.3f} m.',
                        '{} células do terreno foram referenciadas ao nível fixo de {:.3f} m.',
                    ).format(external_resolved_count, reference_level)
                )
        tiny_negative = resolved & (hand_flat < 0) & (hand_flat > -0.001)
        hand_flat[tiny_negative] = 0.0
        negative_count = int(
            np.count_nonzero(resolved & (hand_flat < -0.001))
        )
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

        write_raster(
            drainage_raster_path,
            create_drainage_raster(stream, valid),
            dem_dataset,
            gdal.GDT_Byte,
            255,
        )
        write_raster(
            hand_path,
            hand_flat.reshape(rows, cols),
            dem_dataset,
            gdal.GDT_Float32,
            -9999.0,
        )
        fields = drainage_fields()
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
        vector_result = create_vector_network(
            sink=sink,
            fields=fields,
            stream_flat=stream_flat,
            downstream=downstream,
            accumulation=absolute_accumulation.ravel(),
            dem=dem_flat,
            cols=cols,
            geotransform=geotransform,
            pixel_area_m2=pixel_area_m2,
            metre_factor=metre_factor,
            distance_calculator=distance_calculator,
            feedback=feedback,
            tr=self.tr,
            progress_start=75,
        )
        if feedback.isCanceled():
            return {}
        feedback.pushInfo(
            self.tr(
                '{} drainage reaches created. Maximum Strahler order: {}.',
                '{} trechos de drenagem criados. Ordem máxima de Strahler: {}.',
            ).format(
                vector_result['reach_count'], vector_result['max_strahler']
            )
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
            self.HAND: 'HAND',
        }
        configure_output_postprocessors(
            context=context,
            results=results,
            names=names,
            order=(
                self.DRAINAGE_VECTOR,
                self.HAND,
                self.DRAINAGE_RASTER,
                self.FLOW_ACCUMULATION,
                self.FLOW_DIRECTION,
                self.CONDITIONED_DEM,
            ),
            visible=(self.DRAINAGE_VECTOR, self.HAND),
            group_name=self.tr(
                'HAND Model — {}', 'Modelo HAND — {}'
            ).format(dem_layer.name()),
            styles={self.DRAINAGE_VECTOR: 'drainage'},
        )
        feedback.pushInfo(
            self.tr(
                'Operation completed successfully!',
                'Operação finalizada com sucesso!',
            )
        )
        return results

    def postProcessAlgorithm(self, context, feedback):
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
