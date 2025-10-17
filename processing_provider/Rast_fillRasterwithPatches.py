# -*- coding: utf-8 -*-

"""
fillRasterwithPatches.py
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
__date__ = '2020-09-01'
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
from lftools.geocapt.dip import Interpolar
from lftools.geocapt.imgs import Imgs
from lftools.translations.translate import translate
import os
from qgis.PyQt.QtGui import QIcon

class FillRasterwithPatches(QgsProcessingAlgorithm):

    LOC = QgsApplication.locale()[:2]

    def tr(self, *string):
        return translate(string, self.LOC)

    def createInstance(self):
        return FillRasterwithPatches()

    def name(self):
        return 'fillrasterwithpatches'

    def displayName(self):
        return self.tr('Fill with patches', 'Remendar vazios de raster')

    def group(self):
        return self.tr('Raster')

    def groupId(self):
        return 'raster'

    def tags(self):
        return 'GeoOne,fill,hole,raster,cloud,remove,drone,patch'.split(',')

    def icon(self):
        return QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images/raster.png'))

    txt_en = 'Fills Raster null pixels (no data) with data obtained from other smaller raster layers (Patches).'
    txt_pt = 'Preenche vazios de Raster (pixels nulos) com dados obtidos de outras camadas raster menores (Remendos).'
    figure = 'images/tutorial/raster_fill_holes.jpg'

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
    PATCHES = 'PATCHES'
    RESAMPLING = 'RESAMPLING'
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
            QgsProcessingParameterMultipleLayers(
                self.PATCHES,
                self.tr('Patch Layers', 'Rasters de Remendo'),
                layerType = QgsProcessing.TypeRaster
            )
        )

        interp = [self.tr('Nearest neighbor', 'Vizinho mais próximo'),
                 self.tr('Bilinear'),
                 self.tr('Bicubic', 'Bicúbica')]

        self.addParameter(
            QgsProcessingParameterEnum(
                self.RESAMPLING,
                self.tr('Interpolation', 'Interpolação'),
				options = interp,
                defaultValue= 0
            )
        )

        # OUTPUT
        self.addParameter(
            QgsProcessingParameterFileDestination(
                self.RasterOUT,
                self.tr('Patched Image', 'Imagem Remendada'),
                fileFilter = 'GeoTIFF (*.tif)'
            )
        )

        self.addParameter(
            QgsProcessingParameterBoolean(
                self.OPEN,
                self.tr('Load patched Image', 'Carregar Imagem Remendada'),
                defaultValue= True
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

        PatchesLayers = self.parameterAsLayerList(
            parameters,
            self.PATCHES,
            context
        )

        reamostragem = self.parameterAsEnum(
            parameters,
            self.RESAMPLING,
            context
        )
        reamostragem = ['nearest','bilinear','bicubic'][reamostragem]

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

        #limiar = 240

        # Abrir Raster layer como array
        image = gdal.Open(RasterIN)
        prj=image.GetProjection()
        CRS=osr.SpatialReference(wkt=prj)
        geotransform = image.GetGeoTransform()
        n_bands = image.RasterCount # Número de bandas
        cols = image.RasterXSize # Number of columns
        rows = image.RasterYSize # Number of rows
        # Origem e resolucao da imagem
        ulx, xres, xskew, uly, yskew, yres  = geotransform
        origem = (ulx, uly)
        resol_X = abs(xres)
        resol_Y = abs(yres)
        if n_bands ==1:
            feedback.pushInfo(self.tr('Opening raster band...', 'Abrindo banda do raster...'))
            band1 = image.GetRasterBand(1).ReadAsArray()
        if n_bands >=3:
            feedback.pushInfo(self.tr('Opening Band R...', 'Abrindo Banda R...'))
            band1 = image.GetRasterBand(1).ReadAsArray()
            feedback.pushInfo(self.tr('Opening Band G...', 'Abrindo Banda G...'))
            band2 = image.GetRasterBand(2).ReadAsArray()
            feedback.pushInfo(self.tr('Opening Band B...', 'Abrindo Banda B...'))
            band3 = image.GetRasterBand(3).ReadAsArray()
        # Transparência
        if n_bands == 4:
            feedback.pushInfo(self.tr('Opening Band Alpha...', 'Abrindo Banda Alfa...'))
            band4 = image.GetRasterBand(4).ReadAsArray()
        Pixel_Nulo = image.GetRasterBand(1).GetNoDataValue()
        if Pixel_Nulo == None:
            Pixel_Nulo = 0
        image=None # Fechar imagem

        # Número de pixels para processamento
        TAM =  0
        for Remendo in PatchesLayers:
            Rem_Path = Remendo.dataProvider().dataSourceUri()
            Rem = gdal.Open(Rem_Path)
        #    Rem_cols = Rem.RasterXSize # Number of columns
            Rem_rows = Rem.RasterYSize # Number of rows
            TAM += Rem_rows

        # Remendos
        total = 100.0 / TAM
        cont = 0
        for Remendo in PatchesLayers:
            feedback.pushInfo((self.tr('Processing Layer: {}', 'Processando Camada: {}')).format(Remendo))
            Rem_Path = Remendo.dataProvider().dataSourceUri()
            Rem = gdal.Open(Rem_Path)
            ulx, xres, xskew, uly, yskew, yres  = Rem.GetGeoTransform()
            Rem_origem = (ulx, uly)
            Rem_resol_X = abs(xres)
            Rem_resol_Y = abs(yres)
            Rem_cols = Rem.RasterXSize # Number of columns
            Rem_rows = Rem.RasterYSize # Number of rows
            lrx = ulx + (Rem_cols * xres)
            lry = uly + (Rem_rows * yres)
            bbox = [ulx, lrx, lry, uly]
            Rem_nulo = Rem.GetRasterBand(1).GetNoDataValue()
            if Rem_nulo == None:
                Rem_nulo = 0
            Rem_band1 = Rem.GetRasterBand(1).ReadAsArray()
            if n_bands >1:
                Rem_band2 = Rem.GetRasterBand(2).ReadAsArray()
                Rem_band3 = Rem.GetRasterBand(3).ReadAsArray()

            # Limites de Varredura
            row_ini = int(round((origem[1]-uly)/resol_Y - 0.5))
            row_fim = int(round((origem[1]-lry)/resol_Y - 0.5))
            col_ini = int(round((ulx - origem[0])/resol_X - 0.5))
            col_fim = int(round((lrx - origem[0])/resol_X - 0.5))
            # Varrer Raster
            if n_bands == 4:
                for lin in range(row_ini, row_fim):
                    for col in range(col_ini, col_fim):
                        px_value = band4[lin][col]
                        if px_value == 0: # or band1[lin][col] > limiar: # Verificar Limiar
                            X = origem[0] + resol_X*(col + 0.5)
                            Y = origem[1] - resol_Y*(lin + 0.5)
                            R = Interpolar(X, Y, Rem_band1, Rem_origem, Rem_resol_X, Rem_resol_Y, reamostragem, Rem_nulo)
                            G = Interpolar(X, Y, Rem_band2, Rem_origem, Rem_resol_X, Rem_resol_Y, reamostragem, Rem_nulo)
                            B = Interpolar(X, Y, Rem_band3, Rem_origem, Rem_resol_X, Rem_resol_Y, reamostragem, Rem_nulo)
                            if R != Rem_nulo:
                                band1[lin][col] = R
                            if G != Rem_nulo:
                                band2[lin][col] = G
                            if B != Rem_nulo:
                                band3[lin][col] = B
                    cont += 1
                    feedback.setProgress(int(cont * total))
                    if feedback.isCanceled():
                        break
            elif n_bands == 3:
                for lin in range(row_ini, row_fim):
                    for col in range(col_ini, col_fim):
                        px_value = band1[lin][col]
                        if px_value == Pixel_Nulo: # or band1[lin][col] > limiar: # Verificar Limiar
                            X = origem[0] + resol_X*(col + 0.5)
                            Y = origem[1] - resol_Y*(lin + 0.5)
                            R = Interpolar(X, Y, Rem_band1, Rem_origem, Rem_resol_X, Rem_resol_Y, reamostragem, Rem_nulo)
                            G = Interpolar(X, Y, Rem_band2, Rem_origem, Rem_resol_X, Rem_resol_Y, reamostragem, Rem_nulo)
                            B = Interpolar(X, Y, Rem_band3, Rem_origem, Rem_resol_X, Rem_resol_Y, reamostragem, Rem_nulo)
                            if R != Rem_nulo:
                                band1[lin][col] = R
                            if G != Rem_nulo:
                                band2[lin][col] = G
                            if B != Rem_nulo:
                                band3[lin][col] = B
                    cont += 1
                    feedback.setProgress(int(cont * total))
                    if feedback.isCanceled():
                        break
            elif n_bands == 1:
                for lin in range(row_ini, row_fim):
                    for col in range(col_ini, col_fim):
                        px_value = band1[lin][col]
                        if px_value == Pixel_Nulo: # or band1[lin][col] > limiar: # Verificar Limiar
                            X = origem[0] + resol_X*(col + 0.5)
                            Y = origem[1] - resol_Y*(lin + 0.5)
                            band1[lin][col] = Interpolar(X, Y, Rem_band1, Rem_origem, Rem_resol_X, Rem_resol_Y, reamostragem, Rem_nulo)
                    cont += 1
                    feedback.setProgress(int(cont * total))
                    if feedback.isCanceled():
                        break
            Rem = None # Fechar imagem

        # Criar imagem RGB
        feedback.pushInfo(self.tr('Saving Raster...', 'Salvando Raster...'))
        GDT = gdal_array.NumericTypeCodeToGDALTypeCode(band1.dtype)
        if n_bands ==1:
            RASTER = gdal.GetDriverByName('GTiff').Create(RGB_Output, cols, rows, 1, GDT)
        else:
            RASTER = gdal.GetDriverByName('GTiff').Create(RGB_Output, cols, rows, 3, GDT)
        RASTER.SetGeoTransform(geotransform)    # specify coords
        RASTER.SetProjection(CRS.ExportToWkt()) # export coords to file
        if n_bands ==1:
            feedback.pushInfo(self.tr('Writing rater band...', 'Escrevendo banda do raster...'))
            banda = RASTER.GetRasterBand(1)
            banda.WriteArray(band1)
            banda.SetNoDataValue(Pixel_Nulo)
        else:
            feedback.pushInfo(self.tr('Writing Band R...', 'Escrevendo Banda R...'))
            bandaR = RASTER.GetRasterBand(1)
            bandaR.WriteArray(band1)
            feedback.pushInfo(self.tr('Writing Band G...', 'Escrevendo Banda G...'))
            bandaG = RASTER.GetRasterBand(2)
            bandaG.WriteArray(band2)
            feedback.pushInfo(self.tr('Writing Band B...', 'Escrevendo Banda B...'))
            bandaB = RASTER.GetRasterBand(3)
            bandaB.WriteArray(band3)

        feedback.pushInfo(self.tr('Saving raster...', 'Salvando raster...'))
        RASTER.FlushCache()   # Escrever no disco
        RASTER = None   # Salvar e fechar

        feedback.pushInfo(self.tr('Operation completed successfully!', 'Operação finalizada com sucesso!'))
        feedback.pushInfo(self.tr('Leandro Franca - Cartographic Engineer', 'Leandro França - Eng Cart'))
        self.CAMINHO = RGB_Output
        self.CARREGAR = Carregar
        return {self.RasterOUT: RGB_Output}

    # Carregamento de arquivo de saída
    CAMINHO = ''
    CARREGAR = True
    def postProcessAlgorithm(self, context, feedback):
        if self.CARREGAR:
            rlayer = QgsRasterLayer(self.CAMINHO, self.tr('Patched Image', 'Imagem Remendada'))
            QgsProject.instance().addMapLayer(rlayer)
        return {}
