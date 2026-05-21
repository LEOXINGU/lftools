# -*- coding: utf-8 -*-

"""
Relief_ThematicSlope.py
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
__date__ = '2026-05-20'
__copyright__ = '(C) 2026, Leandro França'

from qgis.core import (QgsProcessing,
                       QgsProcessingException,
                       QgsProcessingAlgorithm,
                       QgsProcessingLayerPostProcessorInterface,
                       QgsProcessingParameterCrs,
                       QgsProcessingParameterEnum,
                       QgsProcessingParameterRasterDestination,
                       QgsProcessingParameterRasterLayer,
                       QgsApplication,
                       QgsSettings,
                       QgsProcessingUtils)

from qgis.PyQt.QtGui import QIcon
from lftools.geocapt.imgs import Imgs
from lftools.translations.translate import translate
import os
import processing


class ThematicSlope(QgsProcessingAlgorithm):

    LOC = QgsApplication.locale()[:2]

    def tr(self, *string):
        return translate(string, self.LOC)

    def createInstance(self):
        return ThematicSlope()

    def name(self):
        return 'thematicslope'

    def displayName(self):
        return self.tr('Thematic slope', 'Declividade temática')

    def group(self):
        return self.tr('Relief', 'Relevo')

    def groupId(self):
        return 'relief'

    def tags(self):
        return 'GeoOne,slope,declividade,percent,percentage,porcentagem,degrees,graus,mde,dem,mdt,dtm,terrain,relevo,gdal,car,codigo florestal,embrapa,fao,usda,qgis'.split(',')

    def icon(self):
        return QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images/contours.png'))

    txt_en = '''This tool calculates terrain slope from a DEM using GDAL. If the input DEM is in a geographic CRS, it is automatically reprojected to the selected projected CRS before slope calculation. The output raster is generated according to the selected thematic classification: FAO, USDA/NRCS and Embrapa styles use slope in percentage (%), while the CAR / Brazilian Forest Code style uses slope in degrees (°).'''
    txt_pt = '''Esta ferramenta calcula a declividade do terreno a partir de um MDE utilizando o GDAL. Se o MDE de entrada estiver em um SRC geográfico, ele será automaticamente reprojetado para o SRC projetado selecionado antes do cálculo da declividade. O raster de saída é gerado de acordo com a classificação temática escolhida: os estilos FAO, USDA/NRCS e Embrapa utilizam declividade em porcentagem (%), enquanto o estilo CAR / Código Florestal utiliza declividade em graus (°).'''
    figure = 'images/tutorial/relief_thematicslope.jpg'

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
    CRS = 'CRS'
    OUTPUT = 'OUTPUT'
    STYLE = 'STYLE'
    OPEN = 'OPEN'

    def initAlgorithm(self, config=None):

        self.addParameter(
            QgsProcessingParameterRasterLayer(
                self.INPUT,
                self.tr('Input DEM', 'MDE de entrada'),
                [QgsProcessing.TypeRaster]
            )
        )

        self.addParameter(
            QgsProcessingParameterCrs(
                self.CRS,
                self.tr('Projected CRS for reprojection', 'SRC projetado para reprojeção'),
                'ProjectCrs',
                optional = True
            )
        )

        self.ESTILOS = [
            self.tr('No style', 'Sem estilo'), # 0
            self.tr('Slope FAO (%)', 'Declividade FAO (%)'), # 4
            self.tr('Slope USDA/NRCS (%)', 'Declividade USDA/NRCS (%)'), # 5
            self.tr('Slope Embrapa - Brazil (%)', 'Declividade Embrapa (%)'), # 6
            self.tr('Slope CAR - Brazil (°)', 'Declividade CAR (°)') # 7
        ]

        my_settings = QgsSettings()
        slope_style = my_settings.value("LFTools/slope_style", 1)

        self.addParameter(
            QgsProcessingParameterEnum(
                self.STYLE,
                self.tr('Symbology and slope unit', 'Simbologia e unidade da declividade'),
                options = self.ESTILOS,
                defaultValue = slope_style
            )
        )

        self.addParameter(
            QgsProcessingParameterRasterDestination(
                self.OUTPUT,
                self.tr('Slope raster', 'Raster de declividade')
            )
        )

    def processAlgorithm(self, parameters, context, feedback):

        raster_in = self.parameterAsRasterLayer(parameters, self.INPUT, context)
        if raster_in is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.INPUT))

        src_crs = raster_in.crs()
        if not src_crs.isValid():
            raise QgsProcessingException(
                self.tr('The input DEM has no valid CRS!',
                        'O MDE de entrada não possui SRC válido!')
            )

        target_crs = self.parameterAsCrs(parameters, self.CRS, context)
        

        output = self.parameterAsOutputLayer(parameters, self.OUTPUT, context)
        style = self.parameterAsEnum(parameters, self.STYLE, context)

        my_settings = QgsSettings()
        my_settings.setValue("LFTools/slope_style", style)

        STYLE_NONE = 0
        STYLE_FAO = 4
        STYLE_USDA = 5
        STYLE_EMBRAPA = 6
        STYLE_CAR = 7
        STYLES = [STYLE_NONE, STYLE_FAO, STYLE_USDA, STYLE_EMBRAPA, STYLE_CAR] # ordem dos estilos deve corresponder à ordem definida no parâmetro de enumeração
        

        # FAO, USDA and Embrapa classes are in percentage.
        # CAR / Brazilian Forest Code uses degrees, because the APP threshold is > 45 degrees.
        output_in_degrees = STYLES[style] == STYLE_CAR
        as_percent = not output_in_degrees

        input_for_slope = raster_in
        raster_source = raster_in.dataProvider().dataSourceUri()

        # Reproject only when the input DEM is in a geographic CRS.
        # This avoids slope calculation directly on angular units (degrees of latitude/longitude).
        if src_crs.isGeographic():
            if target_crs.isGeographic():
                raise QgsProcessingException(
                    self.tr('Please select a projected CRS for reprojection!',
                            'Por favor, selecione um SRC projetado para reprojeção!')
                )
            feedback.pushInfo(
                self.tr('The input DEM is in a geographic CRS. Reprojecting to the selected projected CRS...',
                        'O MDE de entrada está em SRC geográfico. Reprojetando para o SRC projetado selecionado...')
            )

            warp_params = {
                'INPUT': raster_source,
                'SOURCE_CRS': src_crs,
                'TARGET_CRS': target_crs,
                'RESAMPLING': 1,    # Bilinear, appropriate for continuous DEM data
                'NODATA': None,
                'TARGET_RESOLUTION': None,
                'OPTIONS': '',
                'DATA_TYPE': 0,      # Use input layer data type
                'TARGET_EXTENT': None,
                'TARGET_EXTENT_CRS': None,
                'MULTITHREADING': True,
                'EXTRA': '',
                'OUTPUT': 'TEMPORARY_OUTPUT'
            }

            reproj = processing.run(
                'gdal:warpreproject',
                warp_params,
                context=context,
                feedback=feedback,
                is_child_algorithm=True
            )
            input_for_slope = reproj['OUTPUT']

        else:
            feedback.pushInfo(
                self.tr('The input DEM is already projected. Reprojection is not required.',
                        'O MDE de entrada já está em SRC projetado. A reprojeção não é necessária.')
            )

        if feedback.isCanceled():
            return {}

        if output_in_degrees:
            feedback.pushInfo(
                self.tr('Calculating slope in degrees...',
                        'Calculando declividade em graus...')
            )
        else:
            feedback.pushInfo(
                self.tr('Calculating slope in percentage...',
                        'Calculando declividade em porcentagem...')
            )

        slope_params = {
            'INPUT': input_for_slope,
            'BAND': 1,
            'SCALE': 1.0,
            'AS_PERCENT': as_percent,
            'COMPUTE_EDGES': True,
            'ZEVENBERGEN': False,
            'OPTIONS': '',
            'EXTRA': '',
            'OUTPUT': output
        }

        processing.run(
            'gdal:slope',
            slope_params,
            context=context,
            feedback=feedback,
            is_child_algorithm=True
        )

        feedback.pushInfo(self.tr('Operation completed successfully!', 'Operação finalizada com sucesso!'))
        feedback.pushInfo(self.tr('Leandro Franca - Cartographic Engineer', 'Leandro França - Eng Cart'))

        self.CAMINHO = output
        self.estilo_valor = STYLES[style]
        self.output_in_degrees = output_in_degrees
        
        layer_name = self.tr('Slope (%)', 'Declividade (%)') if self.estilo_valor == 0  else self.ESTILOS[style]
        self.LAYER_NAME = layer_name

        global renamer
        renamer = Renamer(layer_name)
        context.layerToLoadOnCompletionDetails(output).setPostProcessor(renamer)

        return {self.OUTPUT: output}

    
    def postProcessAlgorithm(self, context, feedback):
            
        layer = QgsProcessingUtils.mapLayerFromString(self.CAMINHO, context)

        if self.estilo_valor != 0:
            params = {
                'LAYER': layer,
                'STYLE_POINT': 0,
                'STYLE_LINE': 0,
                'STYLE_POLYGON': 0,
                'STYLE_RASTER': self.estilo_valor
            }
            processing.run(
                'lftools:magicstyles',
                params,
                context=context,
                feedback=feedback,
                is_child_algorithm=True
            )

        return {}


class Renamer (QgsProcessingLayerPostProcessorInterface):
    def __init__(self, layer_name):
        self.name = layer_name
        super().__init__()

    def postProcessLayer(self, layer, context, feedback):
        layer.setName(self.name)