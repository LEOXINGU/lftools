# -*- coding: utf-8 -*-

"""
saveAsJPEG.py
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
__date__ = '2020-11-24'
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
                       QgsCoordinateReferenceSystem,
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
from math import floor, ceil
import numpy as np
from PIL import Image
from lftools.geocapt.imgs import Imgs
import os
from qgis.PyQt.QtGui import QIcon

class SaveAsJPEG(QgsProcessingAlgorithm):

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
        return SaveAsJPEG()

    def name(self):
        return 'saveasjpeg'

    def displayName(self):
        return self.tr('Save as JPEG', 'Salvar como JPEG')

    def group(self):
        return self.tr('Raster')

    def groupId(self):
        return 'raster'

    def tags(self):
        return self.tr('RGB,bands,jpeg,jpg,compact,compress,jpw,world').split(',')

    def icon(self):
        return QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images/raster.png'))

    txt_en = 'Exports any 8 bit RGB or RGBA raster layer as a JPEG file. Ideal for reducing the size of the output file. It performs a lossy JPEG compression that, in general, the loss of quality goes unnoticed visually.'
    txt_pt = 'Exporta qualquer camada raster RGB ou RGBA de 8 bits como um arquivo JPEG. Ideal para reduzir o tamanho do arquivo de saída. Realiza a compressão JPEG com uma pequena perda de qualidade que, em geral, passa despercebida visualmente.'
    figure = 'images/tutorial/raster_jpeg_tfw.jpg'

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


    RasterIN ='RasterIN'
    RasterOUT = 'RasterOUT'
    OPEN = 'OPEN'
    WORLDFILE = 'WORLDFILE'


    def initAlgorithm(self, config=None):
        # INPUT
        self.addParameter(
            QgsProcessingParameterRasterLayer(
                self.RasterIN,
                self.tr('Input Raster (3 or 4 bands - 8bit)', 'Raster de entrada (3 ou 4 bandas - 8bits'),
                [QgsProcessing.TypeRaster]
            )
        )

        self.addParameter(
            QgsProcessingParameterBoolean(
                self.WORLDFILE,
                self.tr('Create world file (.jpw)', 'Criar arquivo mundo (.jpw)'),
                defaultValue= True
            )
        )

        self.addParameter(
            QgsProcessingParameterBoolean(
                self.OPEN,
                self.tr('Load output raster', 'Carregar imagem de Saída'),
                defaultValue= True
            )
        )

        # OUTPUT
        self.addParameter(
            QgsProcessingParameterFileDestination(
                self.RasterOUT,
                self.tr('JPEG image', 'Imagem no formato JPEG'),
                fileFilter = '.jpeg'
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

        JPEG = self.parameterAsFileOutput(
            parameters,
            self.RasterOUT,
            context
        )

        Carregar = self.parameterAsBool(
            parameters,
            self.OPEN,
            context
        )

        ArqMundo = self.parameterAsBool(
            parameters,
            self.WORLDFILE,
            context
        )

        feedback.pushInfo(self.tr('Reading the input raster...', 'Lendo o raster de entrada...'))
        image = gdal.Open(RasterIN) # https://gdal.org/python/
        ulx, xres, xskew, uly, yskew, yres  = image.GetGeoTransform()
        prj = image.GetProjection() # wkt
        GDT = image.GetRasterBand(1).DataType
        n_bands = image.RasterCount
        cols = image.RasterXSize # Number of columns
        rows = image.RasterYSize # Number of rows
        # Create CRS object
        CRS=osr.SpatialReference(wkt=prj)

        if n_bands not in [3,4]:
            raise QgsProcessingException(self.tr('The input raster must have 3 or 4 bands!', 'O raster de entrada deve ter 3 ou 4 bandas!'))
        elif GDT != gdal.GDT_Byte:
            raise QgsProcessingException(self.tr('The raster data type must byte (8bit)!', 'O tipo de dado do raster deve ser byte (8bits)!'))
        else:
            RGB = np.zeros((rows,cols,3), dtype = 'uint8')
            feedback.pushInfo(self.tr('Creating new RGB bands...', 'Criando novas bandas RGB...'))
            for k in range(3):
                band = image.GetRasterBand(k+1).ReadAsArray()
                RGB[...,k] = band

            del band

            new_img = Image.fromarray(RGB)
            new_img.save(JPEG)

            image=None # Close dataset
            if ArqMundo:
                georref = '''{}
{}
{}
{}
{}
{}'''.format(xres, xskew, yskew, yres, ulx, uly)
                pathfilename = JPEG
                arq = open(pathfilename.replace('jpeg','jpw'), 'w')
                arq.write(georref)
                arq.close()

            feedback.pushInfo(self.tr('Operation completed successfully!', 'Operação finalizada com sucesso!'))
            feedback.pushInfo(self.tr('Leandro Franca - Cartographic Engineer', 'Leandro França - Eng Cart'))
            self.CAMINHO = JPEG
            self.SRC = QgsCoordinateReferenceSystem(prj)
            self.CARREGAR = Carregar
            return {self.RasterOUT: JPEG}

    def postProcessAlgorithm(self, context, feedback):
        if self.CARREGAR:
            rlayer = QgsRasterLayer(self.CAMINHO, self.tr('JPEG image', 'Imagem no formato JPEG'))
            rlayer.setCrs(self.SRC)
            QgsProject.instance().addMapLayer(rlayer)
        return {}
