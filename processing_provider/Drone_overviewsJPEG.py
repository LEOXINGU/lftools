# -*- coding: utf-8 -*-

"""
Drone_overviewsJPEG.py
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
__date__ = '2021-11-01'
__copyright__ = '(C) 2021, Leandro França'

from PyQt5.QtCore import QCoreApplication, QVariant
from qgis.core import (QgsProcessing,
                       QgsFeatureSink,
                       QgsWkbTypes,
                       QgsFields,
                       QgsField,
                       QgsFeature,
                       QgsPointXY,
                       QgsGeometry,
                       QgsProcessingException,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterString,
                       QgsProcessingParameterNumber,
                       QgsProcessingParameterField,
                       QgsProcessingParameterBoolean,
                       QgsProcessingParameterCrs,
                       QgsProcessingParameterEnum,
                       QgsFeatureRequest,
                       QgsExpression,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterFeatureSink,
                       QgsProcessingParameterFileDestination,
                       QgsProcessingParameterMultipleLayers,
                       QgsProcessingParameterRasterLayer,
                       QgsProcessingParameterRasterDestination,
                       QgsApplication,
                       QgsProject,
                       QgsRasterLayer,
                       QgsCoordinateTransform,
                       QgsCoordinateReferenceSystem)

from osgeo import osr, gdal_array, gdal # https://gdal.org/programs/gdaladdo.html
from lftools.geocapt.imgs import Imgs
from lftools.translations.translate import translate
from qgis.PyQt.QtGui import QIcon
from qgis.utils import iface
import os

class OverviewsJPEG(QgsProcessingAlgorithm):

    LOC = QgsApplication.locale()[:2]

    def tr(self, *string):
        return translate(string, self.LOC)

    def createInstance(self):
        return OverviewsJPEG()

    def name(self):
        return 'overviewsjpeg'

    def displayName(self):
        return self.tr('Overviews with JPEG compression', 'Pirâmides com Compressão JPEG')

    def group(self):
        return self.tr('Drones')

    def groupId(self):
        return 'drones'

    def tags(self):
        return self.tr('drone,compression,reduce,size,JPEG,JPG,photometric,compact,image,overviews,piramides,faster,velocity').split(',')

    def icon(self):
        return QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images/drone.png'))

    txt_en = 'This tool aims to create an Overviews file (.ovr). This algorithm has the advantage of applying a JPEG compression at each level, greatly reducing the generated file size.'
    txt_pt = 'Esta ferramenta tem como objetivo criar um arquivo .ovr, correspondente às Overviews (ou pirâmides, em português). Este algoritmo tem a vantagem de aplicar uma compressão JPEG em cada nível, reduzindo bastante o tamanho do arquivo gerado.'
    figure = 'images/tutorial/raster_overviews.jpg'

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

    def tags(self):
        return self.tr('jpeg,jpg,compressão,compression,compress,photo,comprimir,compact').split(',')

    RasterIN ='RasterIN'
    LEVELS = 'LEVELS'
    TYPE_GEN = 'TYPE_GEN'
    generalization = 'nearest,average,rms,bilinear,gauss,cubic,cubicspline,lanczos,average_magphase,mode'.split(',')

    def initAlgorithm(self, config=None):
        # INPUT
        self.addParameter(
            QgsProcessingParameterRasterLayer(
                self.RasterIN,
                self.tr('RGB Raster', 'Raster RGB'),
                [QgsProcessing.TypeRaster]
            )
        )


        self.addParameter(
            QgsProcessingParameterEnum(
                self.TYPE_GEN,
                self.tr('Resampling method', 'Método de reamostragem'),
				options = self.generalization,
                defaultValue= 1
            )
        )

        self.addParameter(
            QgsProcessingParameterString(
                self.LEVELS,
                self.tr('Factors', 'Fatores'),
                defaultValue = '2,4,8,16'
            )
        )

    def processAlgorithm(self, parameters, context, feedback):

        RasterIN = self.parameterAsRasterLayer(
            parameters,
            self.RasterIN,
            context
        )
        if RasterIN is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.RasterIN))
        RasterIN = RasterIN.dataProvider().dataSourceUri()

        tipo = self.parameterAsEnum(
            parameters,
            self.TYPE_GEN,
            context
        )
        tipo = self.generalization[tipo]


        levels = self.parameterAsString(
            parameters,
            self.LEVELS,
            context
        )
        levels = eval ('[' + levels + ']')

        # Abrindo imagem e verificando número de bandas
        raster = gdal.OpenEx(RasterIN, gdal.OF_RASTER | gdal.OF_READONLY)
        nbands = raster.RasterCount

        gdal.SetConfigOption('COMPRESS_OVERVIEW', 'JPEG')
        # Definindo tipo de compressão JPEG para os OVR
        if nbands == 3:
            gdal.SetConfigOption('PHOTOMETRIC_OVERVIEW', 'YCBCR')
        elif nbands == 4:
            gdal.SetConfigOption('PHOTOMETRIC_OVERVIEW', 'RGB')
        else:
            raise QgsProcessingException(self.tr('The image must be RGB with 3 or 4 bands (alpha)!', 'A imagem deve ser RGB com 3 ou 4 bandas (alfa)!'))

        gdal.SetConfigOption('INTERLEAVE_OVERVIEW', 'PIXEL')

        # Criando as Overviews
        feedback.pushInfo(self.tr('Creating the Overviews...', 'Criando as Overviews...'))
        raster.BuildOverviews(tipo, levels)

        feedback.pushInfo(self.tr('Operation completed successfully!', 'Operação finalizada com sucesso!'))
        feedback.pushInfo(self.tr('Leandro Franca - Cartographic Engineer', 'Leandro França - Eng Cart'))

        return {}

    def postProcessAlgorithm(self, context, feedback):
        canvas = iface.mapCanvas()
        canvas.refresh()
        return {}
