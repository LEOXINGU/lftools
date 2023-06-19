# -*- coding: utf-8 -*-

"""
compressJPEG.py
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
__date__ = '2020-11-25'
__copyright__ = '(C) 2020, Leandro França'

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

from osgeo import osr, gdal_array, gdal #https://gdal.org/python/
from lftools.geocapt.imgs import Imgs
from qgis.PyQt.QtGui import QIcon
import os

class CompressJPEG(QgsProcessingAlgorithm):

    LOC = QgsApplication.locale()[:2]

    def translate(self, string):
        return QCoreApplication.translate('Processing', string)

    def tr(self, *string):
        # Traduzir para o portugês: arg[0] - english (translate), arg[1] - português
        if self.LOC == 'pt':
            if len(string) == 2:
                return string[1]
            else:
                return self.translate(string[0])
        else:
            return self.translate(string[0])

    def createInstance(self):
        return CompressJPEG()

    def name(self):
        return 'compressjpeg'

    def displayName(self):
        return self.tr('JPEG compression', 'Compressão JPEG')

    def group(self):
        return self.tr('Raster')

    def groupId(self):
        return 'raster'

    def tags(self):
        return self.tr('compression,reduce,size,JPEG,JPG,photometric,compact,image').split(',')

    def icon(self):
        return QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images/raster.png'))

    txt_en = 'JPEG compression is a lossy method to reduce the raster file size (about to 10%). The compression level can be adjusted, allowing a selectable tradeoff between storage size and image quality.'
    txt_pt = 'A compressão JPEG é um método "com perdas" para reduzir o tamanho de um arquivo raster (para aproximadamente 10%). O grau de compressão pode ser ajustado, permitindo um limiar entre o tamanho de armazenamento e a qualidade da imagem.'
    figure = 'images/tutorial/raster_jpeg_compress.jpg'

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
    TYPE = 'TYPE'
    QUALITY = 'QUALITY'
    TILED = 'TILED'
    RasterOUT = 'RasterOUT'
    OPEN = 'OPEN'

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
                self.TYPE,
                self.tr('Compression Type', 'Tipo de Compressão'),
				options = ['JPEG_PHOTOMETRIC','JPEG', 'PHOTOMETRIC'],
                defaultValue= 0
            )
        )

        self.addParameter(
            QgsProcessingParameterEnum(
                self.QUALITY,
                self.tr('Quality', 'Qualidade'),
				options = ['65%', '75%', '85%'],
                defaultValue= 1
            )
        )

        self.addParameter(
            QgsProcessingParameterBoolean(
                self.TILED,
                self.tr('Tiled', 'Ladrilhado (tiled)'),
                defaultValue= True
            )
        )

        self.addParameter(
            QgsProcessingParameterBoolean(
                self.OPEN,
                self.tr('Load output raster', 'Carregar imagem de saída'),
                defaultValue= True
            )
        )

        # OUTPUT
        self.addParameter(
            QgsProcessingParameterFileDestination(
                self.RasterOUT,
                self.tr('Compressed Raster', 'Raster com Compressão JPEG'),
                fileFilter = 'GeoTIFF (*.tif)'
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

        RGB_Output = self.parameterAsFileOutput(
            parameters,
            self.RasterOUT,
            context
        )

        Carregar = self.parameterAsBool(
            parameters,
            self.OPEN,
            context
        )

        tipo = self.parameterAsEnum(
            parameters,
            self.TYPE,
            context
        )

        qualidade = self.parameterAsEnum(
            parameters,
            self.QUALITY,
            context
        )

        tiled = self.parameterAsBool(
            parameters,
            self.TILED,
            context
        )

        image = gdal.Open(RasterIN) # https://gdal.org/python/
        GDT = image.GetRasterBand(1).DataType
        n_bands = image.RasterCount

        # Validação dos dados de entrada
        # Se não tiver 3 ou 4 bandas
        if n_bands not in (3,4):
            raise QgsProcessingException(self.tr('The input image must have 3 or 4 bands!', 'A imagem de entrada deve ter 3 ou 4 bandas!'))
        # Tipo de dado 8 btis
        if GDT != gdal.GDT_Byte:
            raise QgsProcessingException(self.tr('Data type must be 8 bit!', 'Tipo de dado deve ser de 8 bit!'))
        # Se Photometric tem que ter 3 bandas
        if tipo in (0, 2) and n_bands != 3:
            raise QgsProcessingException(self.tr('The image must have 3 bands for Photometric compression!', 'A imagem deve ter 3 bandas para a compressão Photometric!'))

        degree = ['65%', '75%', '85%']
        qualidade = 'JPEG_QUALITY=' + degree[qualidade]

        if tipo == 0:
            options = ['PHOTOMETRIC=YCBCR', 'COMPRESS=JPEG', qualidade]
        elif tipo == 1:
            options = ['COMPRESS=JPEG', qualidade]
        elif tipo == 2:
            options = ['PHOTOMETRIC=YCBCR', 'COMPRESS=JPEG']

        if tiled:
            options += ['TILED=YES']

        topts = gdal.TranslateOptions(creationOptions=options)

        feedback.pushInfo(self.tr('Compressing...', 'Comprimindo...'))
        outds=gdal.Translate(RGB_Output, RasterIN, options=topts)

        feedback.pushInfo(self.tr('Operation completed successfully!', 'Operação finalizada com sucesso!'))
        feedback.pushInfo(self.tr('Leandro Franca - Cartographic Engineer', 'Leandro França - Eng Cart'))

        self.CAMINHO = RGB_Output
        self.CARREGAR = Carregar
        return {self.RasterOUT: RGB_Output}

    def postProcessAlgorithm(self, context, feedback):
        if self.CARREGAR:
            rlayer = QgsRasterLayer(self.CAMINHO, self.tr('Compressed Raster', 'Raster com Compressão JPEG'))
            QgsProject.instance().addMapLayer(rlayer)
        return {}
