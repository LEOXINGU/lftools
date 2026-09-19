# -*- coding: utf-8 -*-

"""Extract and order a drainage network from a DEM."""

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
    QgsWkbTypes,
)

from lftools.geocapt.imgs import Imgs
from lftools.translations.translate import translate

from lftools.geocapt.hydro_utils import (
    build_downstream,
    calculate_d8,
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


class DrainageNetwork(QgsProcessingAlgorithm):

    LOC = QgsApplication.locale()[:2]

    def tr(self, *string):
        return translate(string, self.LOC)

    def createInstance(self):
        return DrainageNetwork()

    def name(self):
        return 'drainagenetwork'

    def displayName(self):
        return self.tr(
            'Extract drainage network',
            'Extrair rede de drenagem',
        )

    def group(self):
        return self.tr('Hydrology', 'Hidrologia')

    def groupId(self):
        return 'hydrology'

    def tags(self):
        return (
            'GeoOne,hydrology,hidrologia,drainage,drenagem,stream,river,'
            'rede de drenagem,flow direction,direcao de fluxo,D8,'
            'flow accumulation,acumulacao de fluxo,Strahler,Shreve,'
            'watershed,bacia,dem,mde,dtm,mdt,terrain,relevo,grass'
        ).split(',')

    def icon(self):
        return QIcon(
            os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                'images/hydrology.png',
            )
        )

    txt_en = '''Extracts a drainage network from a <b>Digital Elevation Model (DEM)</b>. The algorithm calculates D8 flow direction and flow accumulation, applies a minimum contributing-area threshold and generates raster and ordered vector drainage networks.
<b>Processing workflow</b>
1. Optional hydrological conditioning of the DEM with GRASS <i>r.fill.dir</i>.
2. D8 flow direction and flow accumulation with GRASS <i>r.watershed</i>.
3. Drainage extraction using a minimum contributing-area threshold.
4. Vectorization and stream ordering using the Strahler and Shreve methods.
<b>Outputs</b>
Conditioned DEM; D8 flow direction; flow accumulation; drainage raster; and ordered vector drainage network.
<b>Important information</b>
&#8226; Both projected and geographic CRS are accepted, but DEM elevations must be expressed in metres.
&#8226; The drainage threshold may be entered as number of cells, km&sup2; or hectares. A smaller threshold generates a denser network; a larger threshold retains only the main channels.
&#8226; For a geographic CRS, area conversions use the geodesic area of a cell at the centre of the DEM and are therefore approximate.
&#8226; The vector network contains Strahler and Shreve order, length, upstream area, initial and final elevation, and slope.
<b>References</b>
Strahler, A. N. (1957). <i>Quantitative analysis of watershed geomorphology</i>. Transactions, American Geophysical Union, 38(6), 913&ndash;920.
Shreve, R. L. (1966). <i>Statistical law of stream numbers</i>. Journal of Geology, 74(1), 17&ndash;37.
GRASS GIS documentation: <a href="https://grass.osgeo.org/grass-stable/manuals/r.fill.dir.html"><i>r.fill.dir</i></a> and <a href="https://grass.osgeo.org/grass-stable/manuals/r.watershed.html"><i>r.watershed</i></a>.'''

    txt_pt = '''Extrai a rede de drenagem a partir de um <b>Modelo Digital de Elevação (MDE)</b>. O algoritmo calcula a direção de fluxo D8 e a acumulação de fluxo, aplica um limiar de área mínima de contribuição e gera a drenagem nos formatos raster e vetorial ordenado.
<b>Fluxo de processamento</b>
1. Condicionamento hidrológico opcional do MDE com o GRASS <i>r.fill.dir</i>.
2. Direção de fluxo D8 e acumulação de fluxo com o GRASS <i>r.watershed</i>.
3. Extração da drenagem pelo limiar de área mínima de contribuição.
4. Vetorização e ordenamento da rede pelos métodos de Strahler e Shreve.
<b>Produtos gerados</b>
MDE condicionado; direção de fluxo D8; acumulação de fluxo; drenagem raster; e rede de drenagem vetorial ordenada.
<b>Informações importantes</b>
&#8226; São aceitos SRC projetado e SRC geográfico, mas as altitudes do MDE devem estar expressas em metros.
&#8226; O limiar da drenagem pode ser informado em número de células, km&sup2; ou hectares. Um limiar menor produz uma rede mais densa; um limiar maior mantém apenas os canais principais.
&#8226; Em SRC geográfico, a conversão de área utiliza a área geodésica de uma célula no centro do MDE e, portanto, é aproximada.
&#8226; A rede vetorial contém ordem de Strahler e Shreve, comprimento, área a montante, cotas inicial e final e declividade.
<b>Referências</b>
Strahler, A. N. (1957). <i>Quantitative analysis of watershed geomorphology</i>. Transactions, American Geophysical Union, 38(6), 913&ndash;920.
Shreve, R. L. (1966). <i>Statistical law of stream numbers</i>. Journal of Geology, 74(1), 17&ndash;37.
Documentação do GRASS GIS: <a href="https://grass.osgeo.org/grass-stable/manuals/r.fill.dir.html"><i>r.fill.dir</i></a> e <a href="https://grass.osgeo.org/grass-stable/manuals/r.watershed.html"><i>r.watershed</i></a>.'''

    figure = 'images/tutorial/hydro_drainage.jpg'

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
    MEMORY = 'MEMORY'
    CONDITIONED_DEM = 'CONDITIONED_DEM'
    FLOW_DIRECTION = 'FLOW_DIRECTION'
    FLOW_ACCUMULATION = 'FLOW_ACCUMULATION'
    DRAINAGE_RASTER = 'DRAINAGE_RASTER'
    DRAINAGE_VECTOR = 'DRAINAGE_VECTOR'

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

        write_raster(
            drainage_raster_path,
            create_drainage_raster(stream, valid),
            dem_dataset,
            gdal.GDT_Byte,
            255,
        )
        downstream = build_downstream(direction, valid)
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
            stream_flat=stream.ravel(),
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
        }
        configure_output_postprocessors(
            context=context,
            results=results,
            names=names,
            order=(
                self.DRAINAGE_VECTOR,
                self.DRAINAGE_RASTER,
                self.FLOW_ACCUMULATION,
                self.FLOW_DIRECTION,
                self.CONDITIONED_DEM,
            ),
            visible=(self.DRAINAGE_VECTOR,),
            group_name=self.tr(
                'Drainage network — {}', 'Rede de drenagem — {}'
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
