# -*- coding: utf-8 -*-

"""
Drone_removeAlphaBand.py
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
from lftools.geocapt.imgs import Imgs
from lftools.translations.translate import translate
import os
from qgis.PyQt.QtGui import QIcon

class RemoveAlphaBand(QgsProcessingAlgorithm):

    LOC = QgsApplication.locale()[:2]

    def tr(self, *string):
        return translate(string, self.LOC)

    def createInstance(self):
        return RemoveAlphaBand()

    def name(self):
        return 'removealphaband'

    def displayName(self):
        return self.tr('Remove alpha band', 'Remover banda alfa')

    def group(self):
        return self.tr('Drones')

    def groupId(self):
        return 'drones'

    def tags(self):
        return self.tr('alpha,band,remove,reduce,bands,compact,compress').split(',')

    def icon(self):
        return QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images/drone.png'))

    txt_en = 'This tool removes the 4th band (apha band), transfering the transparency information as "NoData" to pixels of the RGB output.'
    txt_pt = 'Esta ferramenta remove a 4ª banda (banda alfa), transferindo a informação de transparência como "Sem Valor" para os pixels da imagem RGB de saída.'
    figure = 'images/tutorial/raster_remove_alpha.jpg'

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
    DefineNULL = 'DefineNULL'
    RasterOUT = 'RasterOUT'
    OPEN = 'OPEN'


    def initAlgorithm(self, config=None):
        # INPUT
        self.addParameter(
            QgsProcessingParameterRasterLayer(
                self.RasterIN,
                self.tr('Input Raster with Alpha Band', 'Raster com Banda Alfa'),
                [QgsProcessing.TypeRaster]
            )
        )

        self.addParameter(
            QgsProcessingParameterBoolean(
                self.DefineNULL,
                self.tr('Define null pixel', 'Definir pixel nulo'),
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
                self.tr('Raster with alpha band removed', 'Raster com banda alfa removida'),
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

        definirNulo = self.parameterAsBool(
            parameters,
            self.DefineNULL,
            context
        )

        Carregar = self.parameterAsBool(
            parameters,
            self.OPEN,
            context
        )

        feedback.pushInfo(self.tr('Reading the input raster...', 'Lendo o raster de entrada...'))
        image = gdal.Open(RasterIN) # https://gdal.org/python/
        prj=image.GetProjection()
        geotransform  = image.GetGeoTransform()
        GDT = image.GetRasterBand(1).DataType
        n_bands = image.RasterCount
        cols = image.RasterXSize # Number of columns
        rows = image.RasterYSize # Number of rows
        # Create CRS object
        CRS=osr.SpatialReference(wkt=prj)

        if n_bands != 4:
            raise QgsProcessingException(self.tr('The input raster must have 4 bands!', 'O raster de entrada deve ter 4 bandas!'))
        else:
            # Criate driver
            Driver = gdal.GetDriverByName('GTiff').Create(RGB_Output, cols, rows, 3, GDT)
            Driver.SetGeoTransform(geotransform)    # specify coords
            Driver.SetProjection(CRS.ExportToWkt()) # export coords to file

            # Alpha band
            if definirNulo:
                feedback.pushInfo(self.tr('Reading alpha band...', 'Lendo banda alfa...'))
                alpha = image.GetRasterBand(4).ReadAsArray()
                alpha = alpha != 0

            for k in range(n_bands-1):
                band = image.GetRasterBand(k+1).ReadAsArray()
                feedback.pushInfo(self.tr('Writing the band {}...'.format(k+1), 'Escrevendo a banda {}...'.format(k+1)))
                if definirNulo:
                    # Defining cell 0 to 1 value
                    if band.min() == 0:
                        band =  (band == 0)*1 + band
                    # Defining null cells
                    band = (alpha*band)
                    outband = Driver.GetRasterBand(k+1)
                    outband.WriteArray(band) # write band to the raster
                    Pixel_Nulo = 0
                    outband.SetNoDataValue(Pixel_Nulo)
                else:
                    outband = Driver.GetRasterBand(k+1)
                    outband.WriteArray(band) # write band to the raster

            image=None # Close dataset
            Driver.FlushCache()                     # write to disk
            Driver = None                           # save, close

            feedback.pushInfo(self.tr('Operation completed successfully!', 'Operação finalizada com sucesso!'))
            feedback.pushInfo(self.tr('Leandro Franca - Cartographic Engineer', 'Leandro França - Eng Cart'))
            self.CAMINHO = RGB_Output
            self.CARREGAR = Carregar
            return {self.RasterOUT: RGB_Output}

    def postProcessAlgorithm(self, context, feedback):
        if self.CARREGAR:
            rlayer = QgsRasterLayer(self.CAMINHO, self.tr('Raster without alpha band.', 'Raster sem banda alfa'))
            QgsProject.instance().addMapLayer(rlayer)
        return {}
