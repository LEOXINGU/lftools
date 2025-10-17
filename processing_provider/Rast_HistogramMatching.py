# -*- coding: utf-8 -*-

"""
Rast_HistogramMatching.py
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
__date__ = '2023-06-18'
__copyright__ = '(C) 2023, Leandro França'

from qgis.core import (QgsProcessing,
                       QgsFeatureSink,
                       QgsWkbTypes,
                       QgsFields,
                       QgsField,
                       QgsFeature,
                       QgsPointXY,
                       QgsGeometry,
                       QgsProject,
                       QgsProcessingException,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterString,
                       QgsProcessingParameterBand,
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

from math import floor, ceil
from osgeo import osr, gdal_array, gdal #https://gdal.org/python/
from matplotlib import path
import numpy as np
from lftools.geocapt.imgs import Imgs
from lftools.translations.translate import translate
import os
from qgis.PyQt.QtGui import QIcon

class HistogramMatching(QgsProcessingAlgorithm):

    LOC = QgsApplication.locale()[:2]

    def tr(self, *string):
        return translate(string, self.LOC)

    def createInstance(self):
        return HistogramMatching()

    def name(self):
        return 'histogrammatching'

    def displayName(self):
        return self.tr('Histogram matching', 'Casamento de Histograma')

    def group(self):
        return self.tr('Raster')

    def groupId(self):
        return 'raster'

    def tags(self):
        return 'GeoOne,estatísticas,histograma,matching,statistics,zonal,zonais,amostra,sample,mean,average,std,bands,values'.split(',')

    def icon(self):
        return QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images/raster.png'))

    txt_en = '''This tool matches the histogram of a raster layer in relation to another reference raster layer.'''
    txt_pt = '''Esta ferramenta realiza o casamento do histograma de uma camada raster em relação a outra camada raster de referência.'''
    figure = 'images/tutorial/raster_histogrammatching.jpg'

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
    REFERENCE = 'REFERENCE'
    POLYGONS = 'POLYGONS'
    OUTPUT = 'OUTPUT'
    OPEN = 'OPEN'

    def initAlgorithm(self, config=None):
        # INPUT
        self.addParameter(
            QgsProcessingParameterRasterLayer(
                self.INPUT,
                self.tr('Input Raster', 'Raster a ser ajustado'),
                [QgsProcessing.TypeRaster]
            )
        )

        self.addParameter(
            QgsProcessingParameterRasterLayer(
                self.REFERENCE,
                self.tr('Reference raster', 'Referência'),
                [QgsProcessing.TypeRaster]
            )
        )

        # self.addParameter(
        #     QgsProcessingParameterFeatureSource(
        #         self.POLYGONS,
        #         self.tr('Polygons', 'Polígonos'),
        #         [QgsProcessing.TypeVectorPolygon]
        #     )
        # )

        # OUTPUT
        self.addParameter(
            QgsProcessingParameterFileDestination(
                self.OUTPUT,
                self.tr('Histogram matched', 'Histograma ajustado'),
                fileFilter = 'GeoTIFF (*.tif)'
            )
        )

        self.addParameter(
            QgsProcessingParameterBoolean(
                self.OPEN,
                self.tr('Load output raster', 'Carregar imagem de saída'),
                defaultValue = True
            )
        )

    def processAlgorithm(self, parameters, context, feedback):

        RasterIN = self.parameterAsRasterLayer(
            parameters,
            self.INPUT,
            context
        )
        if RasterIN is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.INPUT))
        RasterIN = RasterIN.dataProvider().dataSourceUri()

        Reference = self.parameterAsRasterLayer(
            parameters,
            self.REFERENCE,
            context
        )
        if Reference is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.REFERENCE))
        Reference = Reference.dataProvider().dataSourceUri()

        # layer = self.parameterAsSource(
        #     parameters,
        #     self.POLYGONS,
        #     context
        # )
        # if layer is None:
        #     raise QgsProcessingException(self.invalidSourceError(parameters, self.POLYGONS))

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

        # Abrir Raster layer como array
        feedback.pushInfo(self.tr('Opening reference raster...', 'Abrindo raster de referência...'))
        image = gdal.Open(RasterIN)
        prj = image.GetProjection()
        Pixel_Nulo = image.GetRasterBand(1).GetNoDataValue()
        n_bands = image.RasterCount
        cols = image.RasterXSize
        rows = image.RasterYSize
        # Origem e resolucao da imagem
        geotransform  = image.GetGeoTransform()
        if n_bands == 4:
            alfa = image.GetRasterBand(4).ReadAsArray()
            alfa = alfa == 255

        # Imagem de Referência
        imageRef = gdal.Open(Reference)
        nulo = imageRef.GetRasterBand(1).GetNoDataValue()
        n_bandsRef = imageRef.RasterCount
        if n_bandsRef == 4:
            alfaRef = imageRef.GetRasterBand(4).ReadAsArray()
            alfaRef = alfaRef == 255

        # Arquivo de saída
        Driver = gdal.GetDriverByName('GTiff').Create(Output, cols, rows, n_bands, gdal.GDT_Byte)
        Driver.SetGeoTransform(geotransform)
        Driver.SetProjection(prj)

        feedback.pushInfo(self.tr('Calculating histogram...', 'Calculando histograma...'))
        for k in range(n_bands):
            if k < 3: # não banda alfa
                bandaRef = imageRef.GetRasterBand(k+1).ReadAsArray()
                bandaRef = bandaRef.astype('float')
                if n_bandsRef == 4:
                    bandaRef = bandaRef*alfaRef - 9999*(np.logical_not(alfaRef))
                    valores = bandaRef.flatten()
                    valores = valores[valores != -9999]
                else:
                    valores = bandaRef.flatten()
                    valores = valores[valores != nulo]
                mediaRef = valores.mean()
                desvpadRef = valores.std()
                del bandaRef, valores

                banda = image.GetRasterBand(k+1).ReadAsArray()
                if n_bands == 4:
                    banda = banda*alfa - 9999*(np.logical_not(alfa))
                    valores = banda.flatten()
                    valores = valores[valores != -9999]
                else:
                    valores = banda.flatten()
                    valores = valores[valores != Pixel_Nulo]

                media = valores.mean()
                desvpad = valores.std()
                del valores

                # Normalização
                banda = (banda - media)/desvpad

                # Calibração
                banda = np.round(banda*desvpadRef + mediaRef)

                # Limites radiométricos 8 bits
                banda = banda*((banda>0)*(banda<256)) + 255*(banda>255)

                # Escrever saída
                banda = banda.astype('uint8')
                outband = Driver.GetRasterBand(k+1)
                feedback.pushInfo(self.tr('Writing Band {}...'.format(k+1), 'Escrevendo Banda {}...'.format(k+1)))
                outband.WriteArray(banda)
                if Pixel_Nulo or Pixel_Nulo == 0:
                    outband.SetNoDataValue(Pixel_Nulo)

            elif k==3: # banda alfa
                banda = image.GetRasterBand(4).ReadAsArray()
                outband = Driver.GetRasterBand(k+1)
                feedback.pushInfo(self.tr('Writing Band {}...'.format(k+1), 'Escrevendo Banda {}...'.format(k+1)))
                outband.WriteArray(banda)

        image, imageRef = None, None # Close dataset
        Driver.FlushCache() # write to disk
        Driver = None  # save, close

        # total = 100.0/(len(n_bands)*layer.featureCount())
        # feedback.setProgress(int((cont) * total))
        # if feedback.isCanceled():
            # break

        feedback.pushInfo(self.tr('Operation completed successfully!', 'Operação finalizada com sucesso!'))
        feedback.pushInfo(self.tr('Leandro Franca - Cartographic Engineer', 'Leandro França - Eng Cart'))
        self.CAMINHO = Output
        self.CARREGAR = Carregar
        return {self.OUTPUT: Output}

    def postProcessAlgorithm(self, context, feedback):
        if self.CARREGAR:
            rlayer = QgsRasterLayer(self.CAMINHO, self.tr('Histogram matched', 'Histograma ajustado'))
            QgsProject.instance().addMapLayer(rlayer)
        return {}
