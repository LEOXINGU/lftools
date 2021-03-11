# -*- coding: utf-8 -*-

"""
defineNullCell.py
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
__date__ = '2020-11-22'
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
import os
from qgis.PyQt.QtGui import QIcon

class DefineNullCell(QgsProcessingAlgorithm):

    LOC = QgsApplication.locale()

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
        return DefineNullCell()

    def name(self):
        return 'definenullcell'

    def displayName(self):
        return self.tr('Define null cells', 'Definir pixel nulo')

    def group(self):
        return self.tr('Raster')

    def groupId(self):
        return 'raster'

    def tags(self):
        return self.tr('null,none,empty,cell,pixel,raster').split(',')

    def icon(self):
        return QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images/raster.png'))

    def shortHelpString(self):
        txt_en = 'Cells of a raster with values outside the interval (minimum and maximum) are defined as null value.'
        txt_pt = 'As células do raster com valores fora do intervalo (mínimo e máximo) são definidas como valor nulo.'
        social_BW = Imgs().social_BW
        footer = '''<div align="center">
                      <img src="'''+ os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images/tutorial/raster_define_null_px.jpg') +'''">
                      </div>
                      <div align="right">
                      <p align="right">
                      <b>'''+self.tr('Author: Leandro Franca', 'Autor: Leandro França')+'''</b>
                      </p>'''+ social_BW + '''</div>
                    </div>'''
        return self.tr(txt_en, txt_pt) + footer


    RasterIN ='RasterIN'
    MIN = 'MIN'
    MAX = 'MAX'
    NULLVALUE = 'NULLVALUE'
    RasterOUT = 'RasterOUT'
    OPEN = 'OPEN'

    def initAlgorithm(self, config=None):
        # INPUT
        self.addParameter(
            QgsProcessingParameterRasterLayer(
                self.RasterIN,
                self.tr('Input Raster', 'Raster de Entrada'),
                [QgsProcessing.TypeRaster]
            )
        )

        self.addParameter(
            QgsProcessingParameterNumber(
                self.MIN,
                self.tr('Minimum Value', 'Valor mínimo'),
                type = 1,
                defaultValue = 1
            )
        )

        self.addParameter(
            QgsProcessingParameterNumber(
                self.MAX,
                self.tr('Maximum Value', 'Valor máximo'),
                type = 1,
                defaultValue = 2**16-1
            )
        )

        self.addParameter(
            QgsProcessingParameterNumber(
                self.NULLVALUE,
                self.tr('Value for defining null cells', 'Valor para definir os pixels nulos'),
                type = 1,
                defaultValue = 0
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
                self.tr('Raster with null cells defined', 'Raster com pixels nulos definidos'),
                fileFilter = '.tif'
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

        MIN = self.parameterAsDouble(
            parameters,
            self.MIN,
            context
        )

        MAX = self.parameterAsDouble(
            parameters,
            self.MAX,
            context
        )

        Pixel_Nulo = self.parameterAsDouble(
            parameters,
            self.NULLVALUE,
            context
        )

        if MAX < MIN or (Pixel_Nulo>MIN and Pixel_Nulo<MAX):
            raise QgsProcessingException(self.tr('Problem in input parameters interval!', 'Problema no intervalo dos parâmetros de entrada!'))

        else:
            image = gdal.Open(RasterIN) # https://gdal.org/python/
            prj=image.GetProjection()
            geotransform  = image.GetGeoTransform()
            GDT = image.GetRasterBand(1).DataType
            n_bands = image.RasterCount
            cols = image.RasterXSize # Number of columns
            rows = image.RasterYSize # Number of rows
            # Create CRS object
            CRS=osr.SpatialReference(wkt=prj)
            # Criate driver
            Driver = gdal.GetDriverByName('GTiff').Create(RGB_Output, cols, rows, n_bands, GDT)
            Driver.SetGeoTransform(geotransform)    # specify coords
            Driver.SetProjection(CRS.ExportToWkt()) # export coords to file

            for k in range(n_bands):
                band = image.GetRasterBand(k+1).ReadAsArray()
                # Defining null pixels
                band = ((band>=MIN)*(band<=MAX))*band + ((band<MIN)*(band>MAX))*Pixel_Nulo
                outband = Driver.GetRasterBand(k+1)
                feedback.pushInfo(self.tr('Writing Band {}...'.format(k+1), 'Escrevendo Banda {}...'.format(k+1)))
                outband.WriteArray(band) # write band to the raster
                outband.SetNoDataValue(Pixel_Nulo)

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
            rlayer = QgsRasterLayer(self.CAMINHO, self.tr('Raster with defined null cells', 'Raster com pixels nulos definidos'))
            QgsProject.instance().addMapLayer(rlayer)
        return {}
