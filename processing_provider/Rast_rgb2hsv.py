# -*- coding: utf-8 -*-

"""
Rast_rgb2hsv.py
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
__date__ = '2022-03-07'
__copyright__ = '(C) 2022, Leandro França'

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
                       QgsProcessingParameterField,
                       QgsProcessingParameterBoolean,
                       QgsProcessingParameterCrs,
                       QgsProcessingParameterEnum,
                       QgsFeatureRequest,
                       QgsExpression,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterFeatureSink,
                       QgsProcessingParameterFileDestination,
                       QgsProcessingParameterRasterLayer,
                       QgsProcessingParameterBand,
                       QgsProcessingParameterRasterDestination,
                       QgsApplication,
                       QgsProject,
                       QgsRasterLayer,
                       QgsCoordinateTransform,
                       QgsCoordinateReferenceSystem)

from osgeo import osr, gdal_array, gdal #https://gdal.org/python/
from lftools.geocapt.imgs import Imgs
from lftools.geocapt.dip import rgb2hsv
import numpy as np
import os
from qgis.PyQt.QtGui import QIcon

class RGB2HSV(QgsProcessingAlgorithm):

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
        return RGB2HSV()

    def name(self):
        return 'rgb2hsv'

    def displayName(self):
        return self.tr('RGB to HSV', 'RGB para HSV')

    def group(self):
        return self.tr('Raster')

    def groupId(self):
        return 'raster'

    def tags(self):
        return self.tr('bands,raster,RGB,color,HSV,composite,hue,saturation,value,intensity,matiz,saturação,intensidade,valor').split(',')

    def icon(self):
        return QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images/raster.png'))

    txt_en = 'Converts the red, green, and blue values of an RGB image to Hue (H), Saturation (S), and Value (V) images.'
    txt_pt = 'Converte os valores de vermelho, verde e azul de uma imagem RGB em imagens Matiz (H), Saturação (S) e Valor (V).'
    figure = 'images/tutorial/raster_rgb2hsv.jpg'

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

    RGB = 'RGB'
    H = 'H'
    S = 'S'
    V = 'V'
    OPEN = 'OPEN'

    def initAlgorithm(self, config=None):
        # INPUT
        self.addParameter(
            QgsProcessingParameterRasterLayer(
                self.RGB,
                self.tr('RGB Raster', 'Raster RGB'),
                [QgsProcessing.TypeRaster]
            )
        )

        # OUTPUT
        self.addParameter(
            QgsProcessingParameterFileDestination(
                self.H,
                self.tr('Hue', 'Matiz (H)'),
                fileFilter = 'GeoTIFF (*.tif)'
            )
        )

        self.addParameter(
            QgsProcessingParameterFileDestination(
                self.S,
                self.tr('Saturation', 'Saturação (S)'),
                fileFilter = 'GeoTIFF (*.tif)'
            )
        )

        self.addParameter(
            QgsProcessingParameterFileDestination(
                self.V,
                self.tr('Value', 'Valor (V)'),
                fileFilter = 'GeoTIFF (*.tif)'
            )
        )

        self.addParameter(
            QgsProcessingParameterBoolean(
                self.OPEN,
                self.tr('Load output raster', 'Carregar raster de saída'),
                defaultValue= True
            )
        )

    def processAlgorithm(self, parameters, context, feedback):

        RasterIN = self.parameterAsRasterLayer(
            parameters,
            self.RGB,
            context
        )
        if RasterIN is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.RGB))
        RasterIN = RasterIN.dataProvider().dataSourceUri()

        hue = self.parameterAsFileOutput(
            parameters,
            self.H,
            context
        )

        sat = self.parameterAsFileOutput(
            parameters,
            self.S,
            context
        )

        val = self.parameterAsFileOutput(
            parameters,
            self.V,
            context
        )

        Carregar = self.parameterAsBool(
            parameters,
            self.OPEN,
            context
        )

        # Abrir Raster layer como array
        image = gdal.Open(RasterIN)
        prj=image.GetProjection()
        geotransform = image.GetGeoTransform()
        num_bands = image.RasterCount
        if num_bands not in (3,4):
            raise QgsProcessingException(self.tr('The raster layer must have 3 (RGB) or 4 bands (RGBA)!','A camada raster deve ter 3 (RGB) ou 4 bandas (RGBA)!'))
        bandas = []
        for b in range(num_bands):
            bandas += [image.GetRasterBand(b+1).ReadAsArray()]
        rgb = np.dstack((bandas[0], bandas[1] ,bandas[2]))
        cols = image.RasterXSize
        rows = image.RasterYSize
        # Origem e resolucao da imagem
        ulx, xres, xskew, uly, yskew, yres  = image.GetGeoTransform()
        origem = (ulx, uly)
        resol_X = abs(xres)
        resol_Y = abs(yres)
        image=None # Fechar imagem

        # Transformação
        HSV = rgb2hsv(rgb)

        # Salvando Resultados
        img = gdal.GetDriverByName('GTiff').Create(hue, cols, rows, 1, gdal.GDT_Float32)
        img.SetGeoTransform(geotransform)
        img.SetProjection(prj)
        banda = img.GetRasterBand(1)
        banda.WriteArray(HSV[:,:,0])
        img.FlushCache()
        img = None

        S = HSV[:,:,1]
        img = gdal.GetDriverByName('GTiff').Create(sat, cols, rows, 1, gdal.GDT_Float32)
        img.SetGeoTransform(geotransform)
        img.SetProjection(prj)
        banda = img.GetRasterBand(1)
        banda.WriteArray(HSV[:,:,1])
        img.FlushCache()
        img = None

        V = HSV[:,:,2]
        img = gdal.GetDriverByName('GTiff').Create(val, cols, rows, 1, gdal.GDT_Float32)
        img.SetGeoTransform(geotransform)
        img.SetProjection(prj)
        banda = img.GetRasterBand(1)
        banda.WriteArray(HSV[:,:,2])
        img.FlushCache()

        feedback.pushInfo(self.tr('Operation completed successfully!', 'Operação finalizada com sucesso!'))
        feedback.pushInfo(self.tr('Leandro Franca - Cartographic Engineer', 'Leandro França - Eng Cart'))
        self.CAMINHO1 = hue
        self.CAMINHO2 = sat
        self.CAMINHO3 = val
        self.CARREGAR = Carregar
        return {self.H: hue,
                self.S: sat,
                self.V: val}

    def postProcessAlgorithm(self, context, feedback):
        if self.CARREGAR:
            rlayer1 = QgsRasterLayer(self.CAMINHO1, self.tr('Hue', 'Matiz (H)'))
            QgsProject.instance().addMapLayer(rlayer1)
            rlayer2 = QgsRasterLayer(self.CAMINHO2, self.tr('Saturation', 'Saturação (S)'))
            QgsProject.instance().addMapLayer(rlayer2)
            rlayer3 = QgsRasterLayer(self.CAMINHO3, self.tr('Value', 'Valor (V)'))
            QgsProject.instance().addMapLayer(rlayer3)
        return {}
