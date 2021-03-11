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

class FillRasterwithPatches(QgsProcessingAlgorithm):

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
        return self.tr('fill,hole,raster,cloud,remove,drone,patch').split(',')

    def icon(self):
        return QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images/raster.png'))

    def shortHelpString(self):
        txt_en = 'Fills Raster null pixels (no data) with data obtained from other smaller raster layers (Patches).'
        txt_pt = 'Preenche vazios de Raster (pixels nulos) com dados obtidos de outras camadas raster menores (Remendos).'
        social_BW = Imgs().social_BW
        footer = '''<div align="center">
                      <img src="'''+ os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images/tutorial/raster_fill_holes.jpg') +'''">
                      </div>
                      <div align="right">
                      <p align="right">
                      <b>'''+self.tr('Author: Leandro Franca', 'Autor: Leandro França')+'''</b>
                      </p>'''+ social_BW + '''</div>
                    </div>'''
        return self.tr(txt_en, txt_pt) + footer

    RasterIN ='RasterIN'
    PATCHES = 'PATCHES'
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

        # OUTPUT
        self.addParameter(
            QgsProcessingParameterFileDestination(
                self.RasterOUT,
                self.tr('Patched Image', 'Imagem Remendada'),
                fileFilter = '.tif'
            )
        )

        self.addParameter(
            QgsProcessingParameterBoolean(
                self.OPEN,
                self.tr('Load patched Image', 'Carregar Imagem Remendada'),
                defaultValue= True
            )
        )

    # Função de Interpolação
    def Interpolar(self, X, Y, BAND, origem, resol_X, resol_Y, metodo, nulo):
        if metodo == 'nearest':
            linha = int(round((origem[1]-Y)/resol_Y - 0.5))
            coluna = int(round((X - origem[0])/resol_X - 0.5))
            if BAND[linha][coluna] != nulo:
                return float(BAND[linha][coluna])
            else:
                return nulo
        elif metodo == 'bilinear':
            nlin = len(BAND)
            ncol = len(BAND[0])
            I = (origem[1]-Y)/resol_Y - 0.5
            J = (X - origem[0])/resol_X - 0.5
            di = I - floor(I)
            dj = J - floor(J)
            if I<0:
                I=0
            if I>nlin-1:
                I=nlin-1
            if J<0:
                J=0
            if J>ncol-1:
                J=ncol-1
            if (BAND[int(floor(I)):int(ceil(I))+1, int(floor(J)):int(ceil(J))+1] == nulo).sum() == 0:
                Z = (1-di)*(1-dj)*BAND[int(floor(I))][int(floor(J))] + (1-dj)*di*BAND[int(ceil(I))][int(floor(J))] + (1-di)*dj*BAND[int(floor(I))][int(ceil(J))] + di*dj*BAND[int(ceil(I))][int(ceil(J))]
                return float(Z)
            else:
                return nulo
        elif metodo == 'bicubic':
            nlin = len(BAND)
            ncol = len(BAND[0])
            I = (origem[1]-Y)/resol_Y - 0.5
            J = (X - origem[0])/resol_X - 0.5
            di = I - floor(I)
            dj = J - floor(J)
            I=int(floor(I))
            J=int(floor(J))
            if I<2:
                I=2
            if I>nlin-3:
                I=nlin-3
            if J<2:
                J=2
            if J>ncol-3:
                J=ncol-3
            if (BAND[I-1:I+3, J-1:J+3] == nulo).sum() == 0:
                MatrInv = (mat([[-1, 1, -1, 1], [0, 0, 0, 1], [1, 1, 1, 1], [8, 4, 2, 1]])).I # < Jogar para fora da funcao
                MAT  = mat([[BAND[I-1, J-1],   BAND[I-1, J],   BAND[I-1, J+1],  BAND[I-2, J+2]],
                                     [BAND[I, J-1],      BAND[I, J],      BAND[I, J+1],      BAND[I, J+2]],
                                     [BAND[I+1, J-1],  BAND[I+1, J], BAND[I+1, J+1], BAND[I+1, J+2]],
                                     [BAND[I+2, J-1],  BAND[I+2, J], BAND[I+2, J+1], BAND[I+2, J+2]]])
                coef = MatrInv*MAT.transpose()
                # Horizontal
                pi = coef[0,:]*pow(dj,3)+coef[1,:]*pow(dj,2)+coef[2,:]*dj+coef[3,:]
                # Vertical
                coef2 = MatrInv*pi.transpose()
                pj = coef2[0]*pow(di,3)+coef2[1]*pow(di,2)+coef2[2]*di+coef2[3]
                return float(pj)
            else:
                return nulo

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

        limiar = 240
        reamostragem = 'nearest'

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
                        if px_value == 0 or band1[lin][col] > limiar: # Verificar Limiar
                            X = origem[0] + resol_X*(col + 0.5)
                            Y = origem[1] - resol_Y*(lin + 0.5)
                            band1[lin][col] = self.Interpolar(X, Y, Rem_band1, Rem_origem, Rem_resol_X, Rem_resol_Y, reamostragem, Rem_nulo)
                            band2[lin][col] = self.Interpolar(X, Y, Rem_band2, Rem_origem, Rem_resol_X, Rem_resol_Y, reamostragem, Rem_nulo)
                            band3[lin][col] = self.Interpolar(X, Y, Rem_band3, Rem_origem, Rem_resol_X, Rem_resol_Y, reamostragem, Rem_nulo)
                    cont += 1
                    feedback.setProgress(int(cont * total))
            else:
                for lin in range(row_ini, row_fim):
                    for col in range(col_ini, col_fim):
                        px_value = band1[lin][col]
                        if px_value == Pixel_Nulo or band1[lin][col] > limiar: # Verificar Limiar
                            X = origem[0] + resol_X*(col + 0.5)
                            Y = origem[1] - resol_Y*(lin + 0.5)
                            band1[lin][col] = self.Interpolar(X, Y, Rem_band1, Rem_origem, Rem_resol_X, Rem_resol_Y, reamostragem, Rem_nulo)
                            band2[lin][col] = self.Interpolar(X, Y, Rem_band2, Rem_origem, Rem_resol_X, Rem_resol_Y, reamostragem, Rem_nulo)
                            band3[lin][col] = self.Interpolar(X, Y, Rem_band3, Rem_origem, Rem_resol_X, Rem_resol_Y, reamostragem, Rem_nulo)
                    cont += 1
                    feedback.setProgress(int(cont * total))
            Rem = None # Fechar imagem

        # Criar imagem RGB
        feedback.pushInfo(self.tr('Saving Raster...', 'Salvando Raster...'))
        GDT = gdal_array.NumericTypeCodeToGDALTypeCode(band1.dtype)
        RGB = gdal.GetDriverByName('GTiff').Create(RGB_Output, cols, rows, 3, GDT)
        RGB.SetGeoTransform(geotransform)    # specify coords
        RGB.SetProjection(CRS.ExportToWkt()) # export coords to file
        feedback.pushInfo(self.tr('Writing Band R...', 'Escrevendo Banda R...'))
        bandaR = RGB.GetRasterBand(1)
        bandaR.WriteArray(band1)
        feedback.pushInfo(self.tr('Writing Band G...', 'Escrevendo Banda G...'))
        bandaG = RGB.GetRasterBand(2)
        bandaG.WriteArray(band2)
        feedback.pushInfo(self.tr('Writing Band B...', 'Escrevendo Banda B...'))
        bandaB = RGB.GetRasterBand(3)
        bandaB.WriteArray(band3)
        RGB.FlushCache()   # Escrever no disco
        RGB = None   # Salvar e fechar

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
