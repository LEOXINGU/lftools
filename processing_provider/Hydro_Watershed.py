# -*- coding: utf-8 -*-

"""Delineate a watershed from a DEM and an outlet point."""

__author__ = 'Leandro França'
__date__ = '2026-09-18'
__copyright__ = '(C) 2026, Leandro França'

from math import ceil, hypot, sqrt
import os

import numpy as np
from osgeo import gdal

from qgis.PyQt.QtCore import QMetaType
from qgis.PyQt.QtGui import QIcon
from qgis.core import (
    Qgis,
    QgsApplication,
    QgsFeature,
    QgsFeatureSink,
    QgsField,
    QgsFields,
    QgsGeometry,
    QgsPointXY,
    QgsProcessing,
    QgsProcessingAlgorithm,
    QgsProcessingException,
    QgsProcessingParameterBoolean,
    QgsProcessingParameterEnum,
    QgsProcessingParameterFeatureSink,
    QgsProcessingParameterNumber,
    QgsProcessingParameterPoint,
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
    calculate_d8,
    cell_centre,
    condition_dem,
    configure_output_postprocessors,
    create_drainage_raster,
    create_vector_network,
    distance_area,
    drainage_fields,
    grass_algorithm,
    guard_raster_size,
    linear_unit_to_metre,
    map_to_cell,
    open_hydrology_rasters,
    read_hydrology_arrays,
    representative_pixel_area_m2,
    supported_parameters,
    threshold_in_cells,
    validate_input_raster,
    validate_matching_grids,
    write_raster,
)


class WatershedDelineation(QgsProcessingAlgorithm):

    LOC = QgsApplication.locale()[:2]

    def tr(self, *string):
        return translate(string, self.LOC)

    def createInstance(self):
        return WatershedDelineation()

    def name(self):
        return 'watersheddelineation'

    def displayName(self):
        return self.tr(
            'Delineate watershed',
            'Delimitar bacia hidrográfica',
        )

    def group(self):
        return self.tr('Hydrology', 'Hidrologia')

    def groupId(self):
        return 'hydrology'

    def tags(self):
        return (
            'GeoOne,hydrology,hidrologia,watershed,bacia hidrográfica,bacia,'
            'outlet,exutório,pour point,drainage,drenagem,stream,river,'
            'flow direction,direcao de fluxo,D8,flow accumulation,'
            'acumulacao de fluxo,dem,mde,dtm,mdt,terrain,relevo,grass'
        ).split(',')

    def icon(self):
        return QIcon(
            os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                'images/hydrology.png',
            )
        )

    txt_en = '''Delineates the <b>upstream contributing watershed</b> from a Digital Elevation Model (DEM) and an outlet point. The point can be adjusted to the extracted drainage network or to the cell with the greatest flow accumulation within a search distance.
<b>Processing workflow</b>
1. Optional hydrological conditioning of the DEM with GRASS <i>r.fill.dir</i>.
2. D8 flow direction and flow accumulation with GRASS <i>r.watershed</i>.
3. Drainage extraction using a minimum contributing-area threshold.
4. Outlet adjustment and watershed delineation with GRASS <i>r.water.outlet</i>.
5. Basin vectorization and generation of the ordered drainage network inside the basin.
<b>Outlet adjustment</b>
&#8226; <b>Nearest drainage cell:</b> moves the point to the closest extracted drainage cell within the maximum distance. This is the recommended option when the user clicks close to a known stream.
&#8226; <b>Greatest flow accumulation:</b> selects, within the search distance, the cell receiving the largest upstream contribution.
&#8226; <b>Do not adjust:</b> uses the DEM cell containing the informed coordinate. If it is on a hillslope, the resulting basin may be very small or narrow.
<b>Outputs</b>
Watershed polygon and raster; original and adjusted outlet points; ordered drainage network and drainage raster inside the basin; conditioned DEM; D8 flow direction; and flow accumulation.
<b>Important information</b>
&#8226; The maximum adjustment distance is expressed in metres, including when the DEM uses a geographic CRS.
&#8226; Before running GRASS, the algorithm checks the outlet position, DEM resolution, drainage threshold and adjustment distance. Incompatible parameters are reported before any output is created.
&#8226; The drainage threshold controls both the density of the network and the cells available for the nearest-drainage adjustment.
&#8226; Check the adjusted outlet before using the basin in engineering analyses, especially near confluences.
<b>Reference</b>
GRASS GIS documentation: <a href="https://grass.osgeo.org/grass-stable/manuals/r.water.outlet.html"><i>r.water.outlet</i></a>, <a href="https://grass.osgeo.org/grass-stable/manuals/r.watershed.html"><i>r.watershed</i></a> and <a href="https://grass.osgeo.org/grass-stable/manuals/r.fill.dir.html"><i>r.fill.dir</i></a>.'''

    txt_pt = '''Delimita a <b>bacia hidrográfica contribuinte a montante</b> a partir de um Modelo Digital de Elevação (MDE) e de um ponto de exutório. O ponto pode ser ajustado para a rede de drenagem extraída ou para a célula de maior acumulação de fluxo dentro de uma distância de busca.
<b>Fluxo de processamento</b>
1. Condicionamento hidrológico opcional do MDE com o GRASS <i>r.fill.dir</i>.
2. Direção de fluxo D8 e acumulação de fluxo com o GRASS <i>r.watershed</i>.
3. Extração da drenagem pelo limiar de área mínima de contribuição.
4. Ajuste do exutório e delimitação da bacia com o GRASS <i>r.water.outlet</i>.
5. Vetorização da bacia e geração da rede de drenagem ordenada dentro da bacia.
<b>Ajuste do exutório</b>
&#8226; <b>Célula de drenagem mais próxima:</b> move o ponto para a célula da drenagem extraída mais próxima, dentro da distância máxima. É a opção recomendada quando o usuário clica próximo de um curso d'água conhecido.
&#8226; <b>Maior acumulação de fluxo:</b> seleciona, dentro da distância de busca, a célula que recebe a maior contribuição a montante.
&#8226; <b>Não ajustar:</b> utiliza a célula do MDE que contém a coordenada informada. Se ela estiver em uma vertente, a bacia resultante poderá ser muito pequena ou estreita.
<b>Produtos gerados</b>
Bacia vetorial e raster; pontos original e ajustado do exutório; rede de drenagem ordenada e drenagem raster dentro da bacia; MDE condicionado; direção de fluxo D8; e acumulação de fluxo.
<b>Informações importantes</b>
&#8226; A distância máxima de ajuste é informada em metros, inclusive quando o MDE utiliza SRC geográfico.
&#8226; Antes de executar o GRASS, o algoritmo verifica a posição do exutório, a resolução do MDE, o limiar da drenagem e a distância de ajuste. Parâmetros incompatíveis são informados antes da criação das saídas.
&#8226; O limiar controla tanto a densidade da drenagem quanto as células disponíveis para o ajuste pela drenagem mais próxima.
&#8226; Confira o exutório ajustado antes de utilizar a bacia em análises de engenharia, especialmente próximo a confluências.
<b>Referência</b>
Documentação do GRASS GIS: <a href="https://grass.osgeo.org/grass-stable/manuals/r.water.outlet.html"><i>r.water.outlet</i></a>, <a href="https://grass.osgeo.org/grass-stable/manuals/r.watershed.html"><i>r.watershed</i></a> e <a href="https://grass.osgeo.org/grass-stable/manuals/r.fill.dir.html"><i>r.fill.dir</i></a>.'''

    figure = 'images/tutorial/hydro_watershed.jpg'

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
    OUTLET = 'OUTLET'
    CONDITION = 'CONDITION'
    THRESHOLD = 'THRESHOLD'
    THRESHOLD_UNIT = 'THRESHOLD_UNIT'
    SNAP_MODE = 'SNAP_MODE'
    SNAP_DISTANCE = 'SNAP_DISTANCE'
    MEMORY = 'MEMORY'
    CONDITIONED_DEM = 'CONDITIONED_DEM'
    FLOW_DIRECTION = 'FLOW_DIRECTION'
    FLOW_ACCUMULATION = 'FLOW_ACCUMULATION'
    DRAINAGE_RASTER = 'DRAINAGE_RASTER'
    DRAINAGE_VECTOR = 'DRAINAGE_VECTOR'
    OUTLET_POINTS = 'OUTLET_POINTS'
    BASIN_RASTER = 'BASIN_RASTER'
    BASIN_VECTOR = 'BASIN_VECTOR'

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
            QgsProcessingParameterPoint(
                self.OUTLET,
                self.tr('Outlet point', 'Ponto de exutório'),
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
        self.snap_modes = [
            self.tr(
                'Nearest extracted drainage cell (recommended)',
                'Célula da drenagem extraída mais próxima (recomendado)',
            ),
            self.tr(
                'Cell with greatest flow accumulation',
                'Célula com maior acumulação de fluxo',
            ),
            self.tr('Do not adjust', 'Não ajustar'),
        ]
        self.addParameter(
            QgsProcessingParameterEnum(
                self.SNAP_MODE,
                self.tr('Outlet adjustment', 'Ajuste do exutório'),
                options=self.snap_modes,
                defaultValue=0,
            )
        )
        self.addParameter(
            QgsProcessingParameterNumber(
                self.SNAP_DISTANCE,
                self.tr(
                    'Maximum adjustment distance (m)',
                    'Distância máxima de ajuste (m)',
                ),
                type=QgsProcessingParameterNumber.Double,
                minValue=0.0,
                defaultValue=100.0,
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
            QgsProcessingParameterFeatureSink(
                self.BASIN_VECTOR,
                self.tr('Watershed', 'Bacia hidrográfica'),
                Qgis.ProcessingSourceType.TypeVectorPolygon,
            )
        )
        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTLET_POINTS,
                self.tr('Outlet points', 'Pontos do exutório'),
                Qgis.ProcessingSourceType.TypeVectorPoint,
            )
        )
        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.DRAINAGE_VECTOR,
                self.tr(
                    'Ordered drainage network inside the watershed',
                    'Rede de drenagem ordenada na bacia',
                ),
                Qgis.ProcessingSourceType.TypeVectorLine,
            )
        )
        self.addParameter(
            QgsProcessingParameterRasterDestination(
                self.BASIN_RASTER,
                self.tr('Watershed raster', 'Bacia hidrográfica (raster)'),
            )
        )
        self.addParameter(
            QgsProcessingParameterRasterDestination(
                self.DRAINAGE_RASTER,
                self.tr(
                    'Drainage network inside the watershed (raster)',
                    'Rede de drenagem na bacia (raster)',
                ),
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
        original_point = self.parameterAsPoint(
            parameters, self.OUTLET, context, dem_layer.crs()
        )
        condition = self.parameterAsBool(parameters, self.CONDITION, context)
        threshold_value = self.parameterAsDouble(
            parameters, self.THRESHOLD, context
        )
        threshold_unit = self.parameterAsEnum(
            parameters, self.THRESHOLD_UNIT, context
        )
        snap_mode = self.parameterAsEnum(parameters, self.SNAP_MODE, context)
        snap_distance = self.parameterAsDouble(
            parameters, self.SNAP_DISTANCE, context
        )
        memory = self.parameterAsInt(parameters, self.MEMORY, context)
        conditioned_output = self.parameterAsOutputLayer(
            parameters, self.CONDITIONED_DEM, context
        )
        direction_output = self.parameterAsOutputLayer(
            parameters, self.FLOW_DIRECTION, context
        )
        accumulation_output = self.parameterAsOutputLayer(
            parameters, self.FLOW_ACCUMULATION, context
        )
        basin_raster_output = self.parameterAsOutputLayer(
            parameters, self.BASIN_RASTER, context
        )
        drainage_raster_output = self.parameterAsOutputLayer(
            parameters, self.DRAINAGE_RASTER, context
        )

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
        self._validate_parameters_before_processing(
            source_path=source_path,
            original_point=original_point,
            snap_mode=snap_mode,
            snap_distance=snap_distance,
            threshold_value=threshold_value,
            threshold_unit=threshold_unit,
            is_geographic=is_geographic,
            metre_factor=metre_factor,
            distance_calculator=distance_calculator,
            feedback=feedback,
        )
        if is_geographic:
            feedback.pushInfo(
                self.tr(
                    'The DEM uses a geographic CRS. Cell areas, adjustment distances and vector measurements will be calculated geodesically.',
                    'O MDE utiliza um SRC geográfico. As áreas das células, as distâncias de ajuste e as medições vetoriais serão calculadas geodesicamente.',
                )
            )

        # Hydrological rasters are first generated in internal temporary
        # files. They are copied to the declared outputs only after the whole
        # workflow succeeds, preventing partial results from being loaded.
        conditioned_path = QgsProcessingUtils.generateTempFilename(
            'conditioned_dem.tif'
        )
        direction_path = QgsProcessingUtils.generateTempFilename(
            'flow_direction.tif'
        )
        accumulation_path = QgsProcessingUtils.generateTempFilename(
            'flow_accumulation.tif'
        )
        basin_raster_path = QgsProcessingUtils.generateTempFilename(
            'watershed.tif'
        )
        drainage_raster_path = QgsProcessingUtils.generateTempFilename(
            'watershed_drainage.tif'
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
        guard_raster_size(rows * cols, feedback, self.tr)
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
        if not np.any(stream):
            raise QgsProcessingException(
                self.tr(
                    'The selected threshold did not generate any drainage cells. Reduce the minimum contributing area.',
                    'O limiar selecionado não gerou células de drenagem. Reduza a área mínima de contribuição.',
                )
            )

        original_cell = map_to_cell(
            original_point, rows, cols, geotransform
        )
        if original_cell is None or not valid.ravel()[original_cell]:
            raise QgsProcessingException(
                self.tr(
                    'The informed outlet is outside the valid DEM area.',
                    'O exutório informado está fora da área válida do MDE.',
                )
            )
        adjusted_cell, adjustment_m = self._adjust_outlet(
            original_point=original_point,
            original_cell=original_cell,
            mode=snap_mode,
            maximum_distance_m=snap_distance,
            stream=stream,
            valid=valid,
            accumulation_valid=accumulation_valid,
            accumulation=absolute_accumulation,
            rows=rows,
            cols=cols,
            geotransform=geotransform,
            pixel_area_m2=pixel_area_m2,
            metre_factor=metre_factor,
            distance_calculator=distance_calculator,
        )
        adjusted_point = cell_centre(adjusted_cell, cols, geotransform)
        feedback.pushInfo(
            self.tr(
                'Outlet adjusted by {:.3f} m to a cell with accumulation of {:.0f} cells.',
                'Exutório ajustado em {:.3f} m para uma célula com acumulação de {:.0f} células.',
            ).format(
                adjustment_m,
                absolute_accumulation.ravel()[adjusted_cell],
            )
        )

        feedback.pushInfo(
            self.tr(
                'Delineating the upstream watershed...',
                'Delimitando a bacia contribuinte a montante...',
            )
        )
        raw_basin_path = QgsProcessingUtils.generateTempFilename(
            'watershed_raw.tif'
        )
        outlet_algorithm = grass_algorithm('r.water.outlet', self.tr)
        outlet_parameters = supported_parameters(
            outlet_algorithm,
            {
                'input': direction_path,
                'coordinates': '{:.15g},{:.15g}'.format(
                    adjusted_point.x(), adjusted_point.y()
                ),
                'output': raw_basin_path,
            },
        )
        processing.run(
            outlet_algorithm,
            outlet_parameters,
            context=context,
            feedback=feedback,
            is_child_algorithm=True,
        )
        raw_basin_dataset = gdal.Open(raw_basin_path, gdal.GA_ReadOnly)
        if raw_basin_dataset is None:
            raise QgsProcessingException(
                self.tr(
                    'The watershed raster generated by GRASS could not be opened.',
                    'Não foi possível abrir o raster da bacia gerado pelo GRASS.',
                )
            )
        validate_matching_grids(
            (dem_dataset, raw_basin_dataset), self.tr
        )
        raw_basin = raw_basin_dataset.GetRasterBand(1).ReadAsArray()
        basin_mask = valid & (raw_basin == 1)
        basin_cell_count = int(np.count_nonzero(basin_mask))
        if basin_cell_count == 0:
            raise QgsProcessingException(
                self.tr(
                    'The selected outlet did not generate a watershed.',
                    'O exutório selecionado não gerou uma bacia hidrográfica.',
                )
            )
        basin_raster = np.full((rows, cols), 255, dtype=np.uint8)
        basin_raster[valid] = 0
        basin_raster[basin_mask] = 1
        write_raster(
            basin_raster_path,
            basin_raster,
            dem_dataset,
            gdal.GDT_Byte,
            255,
        )
        stream_in_basin = stream & basin_mask
        write_raster(
            drainage_raster_path,
            create_drainage_raster(stream_in_basin, basin_mask),
            dem_dataset,
            gdal.GDT_Byte,
            255,
        )

        basin_sink, basin_destination = self._create_basin_vector(
            parameters,
            context,
            basin_raster_path,
            dem_layer.crs(),
            distance_calculator,
            metre_factor,
            adjusted_point,
            adjustment_m,
        )
        del basin_sink
        outlet_destination = self._create_outlet_points(
            parameters,
            context,
            dem_layer.crs(),
            original_point,
            adjusted_point,
            adjustment_m,
            absolute_accumulation.ravel()[adjusted_cell],
        )

        fields = drainage_fields()
        drainage_sink, drainage_destination = self.parameterAsSink(
            parameters,
            self.DRAINAGE_VECTOR,
            context,
            fields,
            QgsWkbTypes.LineString,
            dem_layer.crs(),
        )
        if drainage_sink is None:
            raise QgsProcessingException(
                self.invalidSinkError(parameters, self.DRAINAGE_VECTOR)
            )
        downstream = build_downstream(direction, valid)
        vector_result = create_vector_network(
            sink=drainage_sink,
            fields=fields,
            stream_flat=stream_in_basin.ravel(),
            downstream=downstream,
            accumulation=absolute_accumulation.ravel(),
            dem=dem.ravel(),
            cols=cols,
            geotransform=geotransform,
            pixel_area_m2=pixel_area_m2,
            metre_factor=metre_factor,
            distance_calculator=distance_calculator,
            feedback=feedback,
            tr=self.tr,
            progress_start=75,
        )
        feedback.pushInfo(
            self.tr(
                'Watershed area: approximately {:.6f} km². {} drainage reaches created.',
                'Área da bacia: aproximadamente {:.6f} km². {} trechos de drenagem criados.',
            ).format(
                basin_cell_count * pixel_area_m2 / 1_000_000.0,
                vector_result['reach_count'],
            )
        )

        raw_basin_dataset = None
        dem_dataset = None
        direction_dataset = None
        accumulation_dataset = None

        feedback.pushInfo(
            self.tr(
                'Finalizing output rasters...',
                'Finalizando os rasters de saída...',
            )
        )
        for working_path, output_path in (
            (conditioned_path, conditioned_output),
            (direction_path, direction_output),
            (accumulation_path, accumulation_output),
            (basin_raster_path, basin_raster_output),
            (drainage_raster_path, drainage_raster_output),
        ):
            self._copy_raster(working_path, output_path)

        results = {
            self.BASIN_VECTOR: basin_destination,
            self.OUTLET_POINTS: outlet_destination,
            self.DRAINAGE_VECTOR: drainage_destination,
            self.BASIN_RASTER: basin_raster_output,
            self.DRAINAGE_RASTER: drainage_raster_output,
            self.FLOW_ACCUMULATION: accumulation_output,
            self.FLOW_DIRECTION: direction_output,
            self.CONDITIONED_DEM: conditioned_output,
        }
        names = {
            self.BASIN_VECTOR: self.tr('Watershed', 'Bacia hidrográfica'),
            self.OUTLET_POINTS: self.tr(
                'Outlet points', 'Pontos do exutório'
            ),
            self.DRAINAGE_VECTOR: self.tr(
                'Ordered drainage network', 'Rede de drenagem ordenada'
            ),
            self.BASIN_RASTER: self.tr(
                'Watershed (raster)', 'Bacia hidrográfica (raster)'
            ),
            self.DRAINAGE_RASTER: self.tr(
                'Drainage network (raster)', 'Rede de drenagem (raster)'
            ),
            self.FLOW_ACCUMULATION: self.tr(
                'Flow accumulation', 'Acumulação de fluxo'
            ),
            self.FLOW_DIRECTION: self.tr(
                'D8 flow direction', 'Direção de fluxo D8'
            ),
            self.CONDITIONED_DEM: self.tr(
                'Conditioned DEM', 'MDE condicionado'
            ),
        }
        configure_output_postprocessors(
            context=context,
            results=results,
            names=names,
            order=(
                self.OUTLET_POINTS,
                self.DRAINAGE_VECTOR,
                self.BASIN_VECTOR,
                self.BASIN_RASTER,
                self.DRAINAGE_RASTER,
                self.FLOW_ACCUMULATION,
                self.FLOW_DIRECTION,
                self.CONDITIONED_DEM,
            ),
            visible=(
                self.OUTLET_POINTS,
                self.DRAINAGE_VECTOR,
                self.BASIN_VECTOR,
            ),
            group_name=self.tr(
                'Watershed — {}', 'Bacia hidrográfica — {}'
            ).format(dem_layer.name()),
            styles={
                self.OUTLET_POINTS: 'outlets',
                self.DRAINAGE_VECTOR: 'drainage',
                self.BASIN_VECTOR: 'basin',
            },
        )
        feedback.pushInfo(
            self.tr(
                'Operation completed successfully!',
                'Operação finalizada com sucesso!',
            )
        )
        return results

    def _validate_parameters_before_processing(
        self,
        source_path,
        original_point,
        snap_mode,
        snap_distance,
        threshold_value,
        threshold_unit,
        is_geographic,
        metre_factor,
        distance_calculator,
        feedback,
    ):
        """Validate DEM-dependent parameters before running GRASS."""
        dataset = gdal.Open(source_path, gdal.GA_ReadOnly)
        if dataset is None:
            raise QgsProcessingException(
                self.tr(
                    'The input DEM could not be opened for parameter validation.',
                    'Não foi possível abrir o MDE para validar os parâmetros.',
                )
            )
        rows = dataset.RasterYSize
        cols = dataset.RasterXSize
        geotransform = dataset.GetGeoTransform()
        pixel_area_m2 = representative_pixel_area_m2(
            geotransform,
            rows,
            cols,
            is_geographic,
            metre_factor,
            distance_calculator,
        )
        if pixel_area_m2 <= 0:
            dataset = None
            raise QgsProcessingException(
                self.tr(
                    'The DEM has an invalid pixel area.',
                    'O MDE possui área de pixel inválida.',
                )
            )

        original_cell = map_to_cell(
            original_point, rows, cols, geotransform
        )
        if original_cell is None:
            dataset = None
            raise QgsProcessingException(
                self.tr(
                    'The informed outlet is outside the DEM extent. Processing was not started.',
                    'O exutório informado está fora da extensão do MDE. O processamento não foi iniciado.',
                )
            )
        original_row = original_cell // cols
        original_col = original_cell - original_row * cols
        band = dataset.GetRasterBand(1)
        cell_value = band.ReadAsArray(
            original_col, original_row, 1, 1
        )
        nodata = band.GetNoDataValue()
        valid_cell = (
            cell_value is not None
            and cell_value.size == 1
            and np.isfinite(cell_value[0, 0])
        )
        if valid_cell and nodata is not None:
            valid_cell = (
                not np.isnan(nodata)
                and cell_value[0, 0] != nodata
            ) or (np.isnan(nodata) and not np.isnan(cell_value[0, 0]))
        if not valid_cell:
            dataset = None
            raise QgsProcessingException(
                self.tr(
                    'The informed outlet falls on a NoData cell of the DEM. Move the point to valid terrain. Processing was not started.',
                    'O exutório informado está sobre uma célula NoData do MDE. Mova o ponto para uma área válida. O processamento não foi iniciado.',
                )
            )

        centre = cell_centre(original_cell, cols, geotransform)
        horizontal_cell = (
            original_cell + 1 if original_col + 1 < cols else original_cell - 1
        )
        vertical_cell = (
            original_cell + cols
            if original_row + 1 < rows
            else original_cell - cols
        )
        pixel_width_m = self._point_distance_m(
            centre,
            cell_centre(horizontal_cell, cols, geotransform),
            metre_factor,
            distance_calculator,
        )
        pixel_height_m = self._point_distance_m(
            centre,
            cell_centre(vertical_cell, cols, geotransform),
            metre_factor,
            distance_calculator,
        )
        pixel_diagonal_m = hypot(pixel_width_m, pixel_height_m)
        recommended_distance_m = 3.0 * max(pixel_width_m, pixel_height_m)
        threshold_cells = threshold_in_cells(
            threshold_value, threshold_unit, pixel_area_m2
        )
        dataset = None

        feedback.pushInfo(
            self.tr(
                'Pre-processing validation: pixel approximately {:.3f} × {:.3f} m; drainage threshold {:.0f} cells ({:.6f} km²); outlet adjustment distance {:.3f} m.',
                'Validação prévia: pixel de aproximadamente {:.3f} × {:.3f} m; limiar da drenagem de {:.0f} células ({:.6f} km²); distância de ajuste do exutório de {:.3f} m.',
            ).format(
                pixel_width_m,
                pixel_height_m,
                threshold_cells,
                threshold_cells * pixel_area_m2 / 1_000_000.0,
                snap_distance,
            )
        )

        if threshold_cells > rows * cols:
            raise QgsProcessingException(
                self.tr(
                    'The drainage threshold ({:.0f} cells) is greater than the total number of DEM cells ({:,}). Reduce the threshold. Processing was not started.',
                    'O limiar da drenagem ({:.0f} células) é maior que o número total de células do MDE ({:,}). Reduza o limiar. O processamento não foi iniciado.',
                ).format(threshold_cells, rows * cols)
            )

        if snap_mode != 2 and snap_distance < pixel_diagonal_m:
            minimum_value = ceil(pixel_diagonal_m)
            recommended_value = ceil(recommended_distance_m)
            raise QgsProcessingException(
                self.tr(
                    'The maximum outlet adjustment distance ({:.3f} m) is smaller than the DEM pixel diagonal (approximately {:.3f} m). A drainage cell is represented by its centre, so the selected distance may contain no candidate cell. Use at least {} m; approximately {} m (three pixels) is recommended for this DEM. Processing was not started and no output layer was created.',
                    'A distância máxima de ajuste do exutório ({:.3f} m) é menor que a diagonal do pixel do MDE (aproximadamente {:.3f} m). Como a célula de drenagem é representada por seu centro, a distância selecionada pode não conter nenhuma célula candidata. Utilize pelo menos {} m; para este MDE recomenda-se aproximadamente {} m (três pixels). O processamento não foi iniciado e nenhuma camada de saída foi criada.',
                ).format(
                    snap_distance,
                    pixel_diagonal_m,
                    minimum_value,
                    recommended_value,
                )
            )

    def _copy_raster(self, source_path, destination_path):
        options = gdal.TranslateOptions(
            format='GTiff',
            creationOptions=['COMPRESS=LZW', 'TILED=YES', 'BIGTIFF=IF_SAFER'],
        )
        output = gdal.Translate(destination_path, source_path, options=options)
        if output is None:
            raise QgsProcessingException(
                self.tr(
                    'Could not finalize output raster: {}',
                    'Não foi possível finalizar o raster de saída: {}',
                ).format(destination_path)
            )
        output.FlushCache()
        output = None

    def _adjust_outlet(
        self,
        original_point,
        original_cell,
        mode,
        maximum_distance_m,
        stream,
        valid,
        accumulation_valid,
        accumulation,
        rows,
        cols,
        geotransform,
        pixel_area_m2,
        metre_factor,
        distance_calculator,
    ):
        if mode == 2:
            adjusted_point = cell_centre(
                original_cell, cols, geotransform
            )
            return original_cell, self._point_distance_m(
                original_point,
                adjusted_point,
                metre_factor,
                distance_calculator,
            )

        original_row = original_cell // cols
        original_col = original_cell - original_row * cols
        centre = cell_centre(original_cell, cols, geotransform)
        neighbour_distances = []
        if original_col + 1 < cols:
            neighbour_distances.append(
                self._point_distance_m(
                    centre,
                    cell_centre(original_cell + 1, cols, geotransform),
                    metre_factor,
                    distance_calculator,
                )
            )
        if original_row + 1 < rows:
            neighbour_distances.append(
                self._point_distance_m(
                    centre,
                    cell_centre(original_cell + cols, cols, geotransform),
                    metre_factor,
                    distance_calculator,
                )
            )
        positive_sizes = [value for value in neighbour_distances if value > 0]
        representative_size_m = (
            min(positive_sizes)
            if positive_sizes
            else max(0.001, sqrt(pixel_area_m2))
        )
        radius = int(ceil(maximum_distance_m / representative_size_m)) + 2
        row_min = max(0, original_row - radius)
        row_max = min(rows, original_row + radius + 1)
        col_min = max(0, original_col - radius)
        col_max = min(cols, original_col + radius + 1)
        candidate_mask = (
            stream[row_min:row_max, col_min:col_max]
            if mode == 0
            else (
                valid[row_min:row_max, col_min:col_max]
                & accumulation_valid[row_min:row_max, col_min:col_max]
            )
        )
        candidate_rows, candidate_cols = np.nonzero(candidate_mask)
        if candidate_rows.size == 0:
            raise QgsProcessingException(
                self.tr(
                    'No suitable outlet cell was found within the maximum adjustment distance.',
                    'Nenhuma célula adequada para o exutório foi encontrada dentro da distância máxima de ajuste.',
                )
            )
        candidate_rows = candidate_rows + row_min
        candidate_cols = candidate_cols + col_min
        candidate_cells = candidate_rows * cols + candidate_cols
        distances = np.empty(candidate_cells.size, dtype=np.float64)
        for index, cell in enumerate(candidate_cells):
            candidate_point = cell_centre(
                int(cell), cols, geotransform
            )
            distances[index] = self._point_distance_m(
                original_point,
                candidate_point,
                metre_factor,
                distance_calculator,
            )
        accepted = distances <= maximum_distance_m + 1e-9
        if not np.any(accepted):
            raise QgsProcessingException(
                self.tr(
                    'No suitable outlet cell was found within {:.3f} m. Increase the maximum distance or reduce the drainage threshold.',
                    'Nenhuma célula adequada para o exutório foi encontrada dentro de {:.3f} m. Aumente a distância máxima ou reduza o limiar da drenagem.',
                ).format(maximum_distance_m)
            )
        candidate_cells = candidate_cells[accepted]
        distances = distances[accepted]
        if mode == 0:
            selected = int(np.argmin(distances))
        else:
            values = accumulation.ravel()[candidate_cells]
            maximum = np.max(values)
            tied = np.flatnonzero(values == maximum)
            selected = int(tied[np.argmin(distances[tied])])
        return int(candidate_cells[selected]), float(distances[selected])

    @staticmethod
    def _point_distance_m(
        first, second, metre_factor, distance_calculator
    ):
        if metre_factor is None:
            return float(distance_calculator.measureLine(first, second))
        return hypot(
            second.x() - first.x(), second.y() - first.y()
        ) * metre_factor

    def _create_outlet_points(
        self,
        parameters,
        context,
        crs,
        original_point,
        adjusted_point,
        adjustment_m,
        cell_accumulation,
    ):
        fields = QgsFields()
        fields.append(QgsField('point_type', QMetaType.Type.QString, len=16))
        fields.append(
            QgsField('snap_dist_m', QMetaType.Type.Double, len=20, prec=3)
        )
        fields.append(
            QgsField('cell_accum', QMetaType.Type.Double, len=20, prec=3)
        )
        fields.append(
            QgsField('x_coord', QMetaType.Type.Double, len=24, prec=10)
        )
        fields.append(
            QgsField('y_coord', QMetaType.Type.Double, len=24, prec=10)
        )
        sink, destination = self.parameterAsSink(
            parameters,
            self.OUTLET_POINTS,
            context,
            fields,
            QgsWkbTypes.Point,
            crs,
        )
        if sink is None:
            raise QgsProcessingException(
                self.invalidSinkError(parameters, self.OUTLET_POINTS)
            )
        original = QgsFeature(fields)
        original.setGeometry(QgsGeometry.fromPointXY(original_point))
        original.setAttributes(
            [
                'original',
                0.0,
                None,
                original_point.x(),
                original_point.y(),
            ]
        )
        sink.addFeature(original, QgsFeatureSink.FastInsert)
        adjusted = QgsFeature(fields)
        adjusted.setGeometry(QgsGeometry.fromPointXY(adjusted_point))
        adjusted.setAttributes(
            [
                'adjusted',
                float(adjustment_m),
                float(cell_accumulation),
                adjusted_point.x(),
                adjusted_point.y(),
            ]
        )
        sink.addFeature(adjusted, QgsFeatureSink.FastInsert)
        return destination

    def _create_basin_vector(
        self,
        parameters,
        context,
        basin_raster_path,
        crs,
        distance_calculator,
        metre_factor,
        adjusted_point,
        adjustment_m,
    ):
        polygonized = processing.run(
            'gdal:polygonize',
            {
                'INPUT': basin_raster_path,
                'BAND': 1,
                'FIELD': 'DN',
                'EIGHT_CONNECTEDNESS': False,
                'EXTRA': '',
                'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT,
            },
            context=context,
            feedback=None,
            is_child_algorithm=True,
        )
        polygon_layer = QgsProcessingUtils.mapLayerFromString(
            polygonized['OUTPUT'], context
        )
        if polygon_layer is None:
            raise QgsProcessingException(
                self.tr(
                    'The watershed raster could not be vectorized.',
                    'Não foi possível vetorizar o raster da bacia.',
                )
            )
        geometries = []
        for feature in polygon_layer.getFeatures():
            try:
                value = int(feature['DN'])
            except (TypeError, ValueError):
                continue
            if value == 1 and feature.hasGeometry():
                geometries.append(feature.geometry())
        if not geometries:
            raise QgsProcessingException(
                self.tr(
                    'No watershed polygon was generated.',
                    'Nenhum polígono de bacia foi gerado.',
                )
            )
        geometry = QgsGeometry.unaryUnion(geometries)
        if geometry.isNull() or geometry.isEmpty():
            raise QgsProcessingException(
                self.tr(
                    'The watershed geometry is empty.',
                    'A geometria da bacia está vazia.',
                )
            )
        if not geometry.isMultipart():
            geometry.convertToMultiType()
        area_m2 = (
            float(distance_calculator.measureArea(geometry))
            if metre_factor is None
            else geometry.area() * metre_factor * metre_factor
        )
        fields = QgsFields()
        fields.append(QgsField('basin_id', QMetaType.Type.Int))
        fields.append(
            QgsField('area_km2', QMetaType.Type.Double, len=20, prec=6)
        )
        fields.append(
            QgsField('outlet_x', QMetaType.Type.Double, len=24, prec=10)
        )
        fields.append(
            QgsField('outlet_y', QMetaType.Type.Double, len=24, prec=10)
        )
        fields.append(
            QgsField('snap_dist_m', QMetaType.Type.Double, len=20, prec=3)
        )
        sink, destination = self.parameterAsSink(
            parameters,
            self.BASIN_VECTOR,
            context,
            fields,
            QgsWkbTypes.MultiPolygon,
            crs,
        )
        if sink is None:
            raise QgsProcessingException(
                self.invalidSinkError(parameters, self.BASIN_VECTOR)
            )
        feature = QgsFeature(fields)
        feature.setGeometry(geometry)
        feature.setAttributes(
            [
                1,
                area_m2 / 1_000_000.0,
                adjusted_point.x(),
                adjusted_point.y(),
                float(adjustment_m),
            ]
        )
        sink.addFeature(feature, QgsFeatureSink.FastInsert)
        return sink, destination
