# -*- coding: utf-8 -*-

"""
Relief_DEMfilter.py
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
__date__ = '2021-12-18'
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
                       QgsProcessingParameterVectorLayer,
                       QgsProcessingParameterRasterLayer,
                       QgsProcessingParameterRasterDestination,
                       QgsApplication,
                       QgsProject,
                       QgsRasterLayer,
                       QgsCoordinateTransform,
                       QgsCoordinateReferenceSystem)

from osgeo import osr, gdal_array, gdal #https://gdal.org/python/
import numpy as np
from pyproj.crs import CRS
from math import floor, ceil
from lftools.geocapt.imgs import Imgs
import os
from qgis.PyQt.QtGui import QIcon

class DEMfilter(QgsProcessingAlgorithm):

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
        return DEMfilter()

    def name(self):
        return 'demfilter'

    def displayName(self):
        return self.tr('DEM filter', 'Filtro de MDE')

    def group(self):
        return self.tr('Relief', 'Relevo')

    def groupId(self):
        return 'relief'

    def tags(self):
        return self.tr('dem,dsm,dtm,filtro,smooth,suavizar,passa-baixa,mean,média,convolution,convolução,kernel,median,mde,mdt,mds,terreno,relevo,contour,curva de nível,isoline,isolinha,elevation,height,elevação').split(',')

    def icon(self):
        return QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images/contours.png'))

    txt_en = '''This tool applies the filtering technique in the Raster pixel by pixel, based on the gray level values of neighboring pixels.
The filtering process is done using matrices called masks (or kernel), which are applied to the image.'''
    txt_pt = '''Esta ferramenta aplica a técnica de filtragem no Raster pixel a pixel, baseando-se nos valores dos níveis de cinza dos pixels vizinhos.
O processo de filtragem é feito utilizando matrizes denominadas máscaras (ou kernel), as quais são aplicadas sobre a imagem.'''
    figure = 'images/tutorial/relief_demfilter.jpg'

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

    INPUT ='INPUT'
    KERNEL = 'KERNEL'
    OUTPUT = 'OUTPUT'
    OPEN = 'OPEN'

    def initAlgorithm(self, config=None):
        # INPUT
        self.addParameter(
            QgsProcessingParameterRasterLayer(
                self.INPUT,
                self.tr('Input Raster', 'Raster de Entrada'),
                [QgsProcessing.TypeRaster]
            )
        )



        tipos = [self.tr('Mean kernel - 3 by 3','Máscara da média 3 por 3'),
                 self.tr('Mean kernel - 5 by 5','Máscara da média 5 por 5'),
                 self.tr('Median kernel - 3 by 3','Máscara da mediana 3 por 3'),
                 self.tr('Median kernel - 5 by 5','Máscara da mediana 5 por 5')
               ]

        self.addParameter(
            QgsProcessingParameterEnum(
                self.KERNEL,
                self.tr('Filter', 'Filtro'),
				options = tipos,
                defaultValue= 0
            )
        )

        # OUTPUT
        self.addParameter(
            QgsProcessingParameterFileDestination(
                self.OUTPUT,
                self.tr('Filtered Raster', 'Raster filtrado'),
                fileFilter = 'GeoTIFF (*.tif)'
            )
        )

        self.addParameter(
            QgsProcessingParameterBoolean(
                self.OPEN,
                self.tr('Load filtered raster', 'Carregar raster filtrado'),
                defaultValue= True
            )
        )

    def processAlgorithm(self, parameters, context, feedback):

        # inputs
        RasterIN = self.parameterAsRasterLayer(
            parameters,
            self.INPUT,
            context
        )
        if RasterIN is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.INPUT))
        RasterIN = RasterIN.dataProvider().dataSourceUri()

        tipo = self.parameterAsEnum(
            parameters,
            self.KERNEL,
            context
        )
        size = [3,5,3,5][tipo]

        # output

        Output = self.parameterAsFileOutput(
            parameters,
            self.OUTPUT,
            context
        )

        Carregar = self.parameterAsBool(
            parameters,
            self.OPEN,
            context
        )

        # Abrir arquivo Raster
        feedback.pushInfo(self.tr('Opening raster file...', 'Abrindo arquivo Raster...'))

        # Abrir Raster layer como array
        image = gdal.Open(RasterIN)
        prj=image.GetProjection()
        geotransform = image.GetGeoTransform()
        num_bands = image.RasterCount
        if num_bands != 1:
            raise QgsProcessingException(self.tr('The raster layer should only have 1 band!','A camada raster deve ter apenas 1 banda!'))
        banda = image.GetRasterBand(1).ReadAsArray()
        nulo = image.GetRasterBand(1).GetNoDataValue()
        cols = image.RasterXSize
        rows = image.RasterYSize
        # Origem e resolucao da imagem
        ulx, xres, xskew, uly, yskew, yres  = image.GetGeoTransform()
        origem = (ulx, uly)
        resol_X = abs(xres)
        resol_Y = abs(yres)
        image=None # Fechar imagem

        # Novo geotransform
        new_ulx = ulx + abs(xres)*(size -1)/2
        new_uly = uly - abs(yres)*(size -1)/2
        new_geotransform = (new_ulx, xres, xskew, new_uly, yskew, yres)

        # Kernel (filtro da média)
        kernel = 1.0/(size**2)*np.ones((size, size))

        # Convolução 2D
        m, n = kernel.shape # n = m
        y, x = banda.shape
        y = y - m + 1
        x = x - m + 1
        RESULT = np.zeros((y,x))
        Percent = 100.0/y
        current = 0
        if tipo in [0,1]: #Filtro da média
            for i in range(y):
                for j in range(x):
                    if np.sum(banda[i:i+m, j:j+m] == nulo) > 0:
                        RESULT[i][j] = nulo
                    else:
                        RESULT[i][j] = np.sum(banda[i:i+m, j:j+m]*kernel)
                if feedback.isCanceled():
                    break
                current += 1
                feedback.setProgress(int(current * Percent))
        elif tipo in [2,3]: #Filtro da mediana
            for i in range(y):
                for j in range(x):
                    if np.sum(banda[i:i+m, j:j+m] == nulo) > 0:
                        RESULT[i][j] = nulo
                    else:
                        RESULT[i][j] = np.median(banda[i:i+m, j:j+m])
                if feedback.isCanceled():
                    break
                current += 1
                feedback.setProgress(int(current * Percent))

        # Salvando Resultado
        ncols = cols - (size - 1)
        nrows = rows - (size - 1)
        new_img = gdal.GetDriverByName('GTiff').Create(Output, ncols, nrows, 1, gdal.GDT_Float32)
        new_img.SetGeoTransform(new_geotransform)
        new_img.SetProjection(prj)
        new_band = new_img.GetRasterBand(1)
        if nulo:
            new_band.SetNoDataValue(nulo)
        new_band.WriteArray(RESULT)
        new_img.FlushCache()
        new_img = None

        feedback.pushInfo(self.tr('Operation completed successfully!', 'Operação finalizada com sucesso!'))
        feedback.pushInfo(self.tr('Leandro Franca - Cartographic Engineer', 'Leandro França - Eng Cart'))
        self.CAMINHO = Output
        self.CARREGAR = Carregar
        return {self.OUTPUT: Output}

    # Carregamento de arquivo de saída
    def postProcessAlgorithm(self, context, feedback):
        if self.CARREGAR:
            rlayer = QgsRasterLayer(self.CAMINHO, self.tr('Filtered raster', 'Raster filtrado'))
            QgsProject.instance().addMapLayer(rlayer)
        return {}
