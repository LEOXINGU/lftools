# -*- coding: utf-8 -*-

"""
rescaleTo8bits.py
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
__date__ = '2020-12-21'
__copyright__ = '(C) 2020, Leandro França'

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

class RescaleTo8bits(QgsProcessingAlgorithm):

    LOC = QgsApplication.locale()[:2]

    def tr(self, *string):
        return translate(string, self.LOC)

    def createInstance(self):
        return RescaleTo8bits()

    def name(self):
        return 'rescaleto8bits'

    def displayName(self):
        return self.tr('Rescale to 8 bit', 'Reescalonar para 8 bits')

    def group(self):
        return self.tr('Raster')

    def groupId(self):
        return 'raster'

    def tags(self):
        return 'GeoOne,8bits,rescale,histograma,radiometric,transform,16bits,reduce,compress'.split(',')

    def icon(self):
        return QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images/raster.png'))

    txt_en = 'Rescales the values of the raster pixels with radiometric resolution of 16 bits (or even 8 bits or float) to exactly the range of 0 to 255, creating a new raster with 8 bits (byte) of radiometric resolution.'
    txt_pt = 'Reescalona os valores dos pixels de raster com resolução radiométrica de 16 bits (ou até mesmo 8 bits ou float) para exatamente o intervalo de 0 a 255, criando um novo raster com 8 bits (byte) de resolução radiométrica.'
    figure = 'images/tutorial/raster_histogram.jpg'

    def shortHelpString(self):
        social_BW = Imgs().social_BW
        footer = '''<div align="center">
                      <img src="'''+ os.path.join(os.path.dirname(os.path.dirname(__file__)), self.figure) +'''">
                      </div>
                      <div align="left">
                      <p>
                      <b><a href="'''+ self.tr('https://portal.geoone.com.br/m/lessons/sensoriamento?classId=2123') + '''" target="_blank">'''+ self.tr('Click here to watch a full class on this tool',
                                    'Clique aqui para assistir uma aula completa sobre esta ferramenta') +'''</a></b>
                      </p>
                      <p>
                      <b><a href="'''+ self.tr('https://geoone.com.br/pvsensoriamento/') + '''" target="_blank">'''+ self.tr('Sign up for the Remote Sensing in QGIS course',
                                    'Inscreva-se no curso Sensoriamento Remoto no QGIS') +'</a><br><br>'+ self.tr('Author: Leandro Franca', 'Autor: Leandro França')+'''</b>
                      </p>'''+ social_BW + '''
                    </div>'''
        return self.tr(self.txt_en, self.txt_pt) + footer

    def tags(self):
        return self.tr('8bits,8 bits,rescale,radiometric,reduce,reduction,bits,linear,stretch').split(',')

    RasterIN ='RasterIN'
    TYPE = 'TYPE'
    BYBAND = 'BYBAND'
    NULLPIXEL = 'NULLPIXEL'
    RasterOUT = 'RasterOUT'
    OPEN = 'OPEN'

    def initAlgorithm(self, config=None):
        # INPUT
        self.addParameter(
            QgsProcessingParameterRasterLayer(
                self.RasterIN,
                self.tr('Raster Imagery', 'Imagem Raster'),
                [QgsProcessing.TypeRaster]
            )
        )

        opcoes = [self.tr('Min / Max'),
                  self.tr('Quantile (2% - 98%)', 'Quantil (2% - 98%)'),
                  self.tr('Mean ± 2*stdDev', 'Média ± 2*desvPad')]

        self.addParameter(
            QgsProcessingParameterEnum(
                self.TYPE,
                self.tr('Rescale type', 'Tipo de Reescalonamento'),
				options = opcoes,
                defaultValue= 1
            )
        )

        self.addParameter(
            QgsProcessingParameterBoolean(
                self.BYBAND,
                self.tr('Rescales by band', 'Reescalonar por banda'),
                defaultValue= True
            )
        )

        self.addParameter(
            QgsProcessingParameterBoolean(
                self.NULLPIXEL,
                self.tr('Define null pixel as zero', 'Definir pixel nulo como zero'),
                defaultValue= False
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
                self.tr('8 bit rescaled raster', 'Raster reescalonado para 8 bits'),
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

        Output = self.parameterAsFileOutput(
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

        porBanda = self.parameterAsBool(
            parameters,
            self.BYBAND,
            context
        )

        nullPixel = self.parameterAsBool(
            parameters,
            self.NULLPIXEL,
            context
        )

        min8 = 1 if nullPixel else 0
        eps = np.finfo(float).eps

        feedback.pushInfo(self.tr('Opening raster...', 'Abrindo raster...'))
        image = gdal.Open(RasterIN)
        prj = image.GetProjection()
        geotransform  = image.GetGeoTransform()
        GDT = image.GetRasterBand(1).DataType
        Pixel_Nulo = image.GetRasterBand(1).GetNoDataValue()
        n_bands = image.RasterCount
        cols = image.RasterXSize
        rows = image.RasterYSize
        CRS = osr.SpatialReference(wkt=prj)

        # Criate driver
        Driver = gdal.GetDriverByName('GTiff').Create(Output, cols, rows, n_bands, gdal.GDT_Byte)
        Driver.SetGeoTransform(geotransform)
        Driver.SetProjection(CRS.ExportToWkt())

        feedback.pushInfo(self.tr('Calculating statistics...', 'Calculando estatísticas...'))
        bands = []
        max,min = [],[]
        for k in range(n_bands):
            band = image.GetRasterBand(k+1).ReadAsArray()
            bands += [band]
            # Remove null pixels of the statistics
            if Pixel_Nulo:
                band = band[band != Pixel_Nulo]
            # Max e Min
            if tipo == 0:
                max += [band.max()]
                min += [band.min()]
            # Quantile (2% - 98%)
            if tipo == 1:
                max += [np.quantile(band,0.98)]
                min += [np.quantile(band,0.02)]
            # Media ± 2*DesvPad
            if tipo == 2:
                max += [band.mean() + 2*band.std()]
                min += [band.mean() - 2*band.std()]

        if not porBanda:
            Max = np.max(max)
            Min = np.min(min)

        # Rescale and save bands
        feedback.pushInfo(self.tr('Rescaling and saving bands...', 'Reescalonando e salvando as bandas...'))
        for k in range(n_bands):
            band = bands[k]
            if porBanda:
                Max = max[k]
                Min = min[k]
            if nullPixel:
                transf = (255*(band.astype('float')- Min)/(Max-Min) + 0.5).round()
            else:
                transf = (256*(band.astype('float')- Min)/(Max-Min) - 0.5).round()
            if tipo in [1,2]:
                transf = ((transf>0)*(transf<=255))*transf + 255*(transf>255)
                if nullPixel:
                    transf = transf*(band != Pixel_Nulo)

            transf = transf.astype('uint8')
            outband = Driver.GetRasterBand(k+1)
            feedback.pushInfo(self.tr('Writing Band {}...'.format(k+1), 'Escrevendo Banda {}...'.format(k+1)))
            outband.WriteArray(transf)
            if nullPixel:
                outband.SetNoDataValue(0)

        image = None # Close dataset
        Driver.FlushCache() # write to disk
        Driver = None  # save, close

        feedback.pushInfo(self.tr('Operation completed successfully!', 'Operação finalizada com sucesso!'))
        feedback.pushInfo(self.tr('Leandro Franca - Cartographic Engineer', 'Leandro França - Eng Cart'))
        self.CAMINHO = Output
        self.CARREGAR = Carregar
        return {self.RasterOUT: Output}

    def postProcessAlgorithm(self, context, feedback):
        if self.CARREGAR:
            rlayer = QgsRasterLayer(self.CAMINHO, self.tr('Rescaled to 8 bit', 'Reescalonado para 8 bits'))
            QgsProject.instance().addMapLayer(rlayer)
        return {}
