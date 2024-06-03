# -*- coding: utf-8 -*-

"""
Rast_bandArithmetic.py
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
__date__ = '2022-01-20'
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
                       QgsProcessingParameterRasterDestination,
                       QgsApplication,
                       QgsProject,
                       QgsRasterLayer,
                       QgsCoordinateTransform,
                       QgsCoordinateReferenceSystem)

from osgeo import osr, gdal_array, gdal
from lftools.geocapt.imgs import Imgs
import numpy as np
import os
from qgis.PyQt.QtGui import QIcon

class BandArithmetic(QgsProcessingAlgorithm):

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
        return BandArithmetic()

    def name(self):
        return 'bandarithmetic'

    def displayName(self):
        return self.tr('Band Arithmetic', 'Aritmética de bandas')

    def group(self):
        return self.tr('Raster')

    def groupId(self):
        return 'raster'

    def tags(self):
        return self.tr('raster,rgb,bands,color,algebra,arithmetic,aritmética,ndvi,gli,ndwi,index,índice').split(',')

    def icon(self):
        return QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images/raster.png'))

    txt_en = '''Performs an arithmetic operation on the bands of a raster. The predefined formula is used to calculate the Green Leaf Index (GLI) for a RGB raster. However you can enter your own formula.
Examples:
NDVI with RGN raster: ( b3 - b1) / (b3 + b1)
NDWI with RGN raster: ( b2 - b3) / (b2 + b3)
GLI with RGB raster: (2*b2 - b1 - b3) / (2*b2 + b1 + b3)
VARI with RGB raster: (b2 - b1) / (b2 + b1 - b3)
VIgreen with RGB raster: (b2 - b1) / (b2 + b1)
Obs.:
The operators supported are:  + , - , * , /'''
    txt_pt = '''Executa uma operação aritmética entre as bandas de um raster. A fórmula predefinida é usado para calcular o Green Leaf Index (GLI) para um raster RGB. No entanto, você pode inserir sua própria fórmula.
Exemplos:
NDVI com raster RGN: ( b3 - b1) / (b3 + b1)
NDWI com raster RGN: ( b3 - b2) / (b3 + b2)
GLI com raster RGB: (2*b2 - b1 - b3) / (2*b2 + b1 + b3)
VARI com raster RGB: (b2 - b1) / (b2 + b1 - b3)
VIgreen com raster RGB: (b2 - b1) / (b2 + b1)
Obs.:
Os operadores suportados são: + , - , * , /'''
    figure = 'images/tutorial/raster_bandArithmetic.jpg'

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
    ALPHA = 'ALPHA'
    FORMULA = 'FORMULA'
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

        self.addParameter(
            QgsProcessingParameterBoolean(
                self.ALPHA,
                self.tr('Fourth band is transparency', 'Quarta banda é de transparência'),
                defaultValue= True
            )
        )

        self.addParameter(
            QgsProcessingParameterString(
                self.FORMULA,
                self.tr('Formula', 'Fórmula'),
                defaultValue = '(2*b2 - b1 - b3)/(2*b2 + b1 + b3)'
            )
        )

        # OUTPUT
        self.addParameter(
            QgsProcessingParameterFileDestination(
                self.OUTPUT,
                self.tr('Calculated index', 'Índice calculado'),
                fileFilter = 'GeoTIFF (*.tif)'
            )
        )

        self.addParameter(
            QgsProcessingParameterBoolean(
                self.OPEN,
                self.tr('Load calculated index', 'Carregar índice calculado'),
                defaultValue= True
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

        alfa = self.parameterAsBool(
            parameters,
            self.ALPHA,
            context
        )

        expr = self.parameterAsString(
            parameters,
            self.FORMULA,
            context
        )

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

        # Input Raster
        image = gdal.Open(RasterIN.dataProvider().dataSourceUri())
        prj=image.GetProjection()
        geotransform  = image.GetGeoTransform()
        GDT = image.GetRasterBand(1).DataType
        Pixel_Nulo = image.GetRasterBand(1).GetNoDataValue()
        n_bands = image.RasterCount
        cols = image.RasterXSize
        rows = image.RasterYSize
        CRS=osr.SpatialReference(wkt=prj)

        # Verificar número de bandas
        dic = {}
        for k in range(n_bands):
            feedback.pushInfo(self.tr('Reading band {}...'.format(k+1), 'Lendo a banda {}...'.format(k+1)))
            dic['b[n]'.replace('[n]', str(k+1))] = image.GetRasterBand(k+1).ReadAsArray().astype('float')
            expr = expr.replace('b[n]'.replace('[n]', str(k+1)), "dic['b[n]']".replace('[n]', str(k+1)))
        if n_bands == 4 and alfa:
            transp = dic['b4'] > 0
        image = None
        lista = expr.lower().split('/')

        try:
            feedback.pushInfo(self.tr('Carrying out the calculations...', 'Realizando os cálculos...'))
            if len(lista) == 2:
                NUM, DEN = lista
                NUM = eval(NUM)
                DEN = eval(DEN)
                if n_bands == 4 and alfa:
                    INDICE = -9999*((DEN == 0) | np.logical_not(transp)) + ((DEN != 0) & transp)*(NUM/(DEN + (DEN == 0)*1))
                else:
                    if isinstance(Pixel_Nulo, (int, float)):
                        b1 = dic['b1']
                        INDICE = -9999*((DEN == 0) | (b1 == Pixel_Nulo)) + ((DEN != 0) & (b1 != Pixel_Nulo))*(NUM/(DEN + (DEN == 0)*1))
                    else:
                        INDICE = -9999*(DEN == 0) + (DEN != 0)*(NUM/(DEN + (DEN == 0)*1))
            elif len(lista) == 1:
                formula = eval(lista[0])
                if n_bands == 4 and alfa:
                    INDICE = -9999*(np.logical_not(transp)) + (transp)*formula
                else:
                    if isinstance(Pixel_Nulo, (int, float)):
                        INDICE = -9999*(b1 == Pixel_Nulo) + (b1 != Pixel_Nulo)*formula
                    else:
                        INDICE = formula
            else:
                raise QgsProcessingException(self.tr('Check the input formula!', 'Verifique a fórmula de entrada!'))
        except:
            raise QgsProcessingException(self.tr('Check if your formula is correct!', 'Verifique se sua fórmula está correta!'))

        # Criate driver
        Driver = gdal.GetDriverByName('GTiff').Create(Output, cols, rows, 1, gdal.GDT_Float32)
        Driver.SetGeoTransform(geotransform)
        Driver.SetProjection(CRS.ExportToWkt())
        outband = Driver.GetRasterBand(1)
        feedback.pushInfo(self.tr('Writing results...', 'Escrevendo resultados...'))
        outband.SetNoDataValue(-9999)
        outband.WriteArray(INDICE)
        Driver.FlushCache()
        Driver = None

        feedback.pushInfo(self.tr('Operation completed successfully!', 'Operação finalizada com sucesso!'))
        feedback.pushInfo(self.tr('Leandro Franca - Cartographic Engineer', 'Leandro França - Eng Cart'))

        self.CAMINHO = Output
        self.CARREGAR = Carregar
        return {self.OUTPUT: Output}

    def postProcessAlgorithm(self, context, feedback):
        if self.CARREGAR:
            rlayer = QgsRasterLayer(self.CAMINHO, self.tr('Calculated index', 'Índice calculado'))
            QgsProject.instance().addMapLayer(rlayer)
        return {}
