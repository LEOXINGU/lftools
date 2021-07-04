# -*- coding: utf-8 -*-

"""
Rast_binaryThresholding.py
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
__date__ = '2021-07-03'
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

from math import floor, ceil
from osgeo import osr, gdal_array, gdal #https://gdal.org/python/
from matplotlib import path
import numpy as np
from lftools.geocapt.imgs import Imgs
import os
from qgis.PyQt.QtGui import QIcon

class BinaryThresholding(QgsProcessingAlgorithm):

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
        return BinaryThresholding()

    def name(self):
        return 'binarythresholding'

    def displayName(self):
        return self.tr('Binary Thresholding', 'Limiarização Binária')

    def group(self):
        return self.tr('Raster')

    def groupId(self):
        return 'raster'

    def tags(self):
        return self.tr('thresholding,binary,supervised,variance,mean,average,histogram,standard,statistics').split(',')

    def icon(self):
        return QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images/raster.png'))

    txt_en = '''Creates a binarized raster by dividing the input raster into two distinct classes from statistical data (lower and upper threshold) of area samples.
A class matches the values within the range of thresholds, where the value 1 (true) is returned. The other class corresponds to values outside the range, returning the value 0 (false).'''
    txt_pt = '''Cria um raster binarizado, dividindo o raster de entrada em duas classes distintas a partir de dados estatísticos (limiar inferior e superior) de amostras de áreas.
Uma classe irá corresponder aos valores compreendidos dentro do intervalo dos limiares, sendo retornado o valor 1 (verdadeiro). Já a outra classe correpondem aos valores fora do intervalo, sendo retornado o valor 0 (falso).'''
    figure = 'images/tutorial/raster_thresholding.jpg'

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
    SAMPLES = 'SAMPLES'
    METHOD = 'METHOD'
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
            QgsProcessingParameterFeatureSource(
                self.SAMPLES,
                self.tr('Sample Polygons', 'Polígonos de Amostra'),
                [QgsProcessing.TypeVectorPolygon]
            )
        )


        opcoes = [self.tr('Min / Max'),
                  self.tr('Quantile (2% - 98%)', 'Quantil (2% - 98%)'),
                  self.tr('Mean ± 2*stdDev', 'Média ± 2*desvPad'),
                  self.tr('Mean ± 3*stdDev', 'Média ± 3*desvPad')]

        self.addParameter(
            QgsProcessingParameterEnum(
                self.METHOD,
                self.tr('Calculation of thresholds', 'Cálculo dos limiares'),
				options = opcoes,
                defaultValue= 0
            )
        )

        # OUTPUT
        self.addParameter(
            QgsProcessingParameterFileDestination(
                self.RasterOUT,
                self.tr('Thresholded raster', 'Imagem limiarizada'),
                fileFilter = '.tif'
            )
        )

        self.addParameter(
            QgsProcessingParameterBoolean(
                self.OPEN,
                self.tr('Load thresholded image', 'Carregar imagem limiarizada'),
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

        layer = self.parameterAsSource(
            parameters,
            self.SAMPLES,
            context
        )
        if layer is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.SAMPLES))

        metodo = self.parameterAsEnum(
            parameters,
            self.METHOD,
            context
        )
        if metodo is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.METHOD))

        Carregar = self.parameterAsBool(
            parameters,
            self.OPEN,
            context
        )

        Raster_Output = self.parameterAsFileOutput(
            parameters,
            self.RasterOUT,
            context
        )

        # Abrir Raster layer como array
        image = gdal.Open(RasterIN)
        prj=image.GetProjection()
        geotransform = image.GetGeoTransform()
        num_bands = image.RasterCount
        if num_bands != 1:
            raise QgsProcessingException(self.tr('The raster layer must have only 1 band!', 'A camada raster deve ter apenas 1 banda!'))
        banda = image.GetRasterBand(1).ReadAsArray()
        cols = image.RasterXSize
        rows = image.RasterYSize
        # Origem e resolucao da imagem
        ulx, xres, xskew, uly, yskew, yres  = image.GetGeoTransform()
        origem = (ulx, uly)
        resol_X = abs(xres)
        resol_Y = abs(yres)
        lrx = ulx + (cols * xres)
        lry = uly + (rows * yres)
        bbox = [ulx, lrx, lry, uly]
        image=None # Fechar imagem

        # Amostra de Raster por poligono
        feedback.pushInfo(self.tr('Taking raster samples by polygon...', 'Pegando amostras do raster por polígono...'))
        valores = []
        for feat in layer.getFeatures():
            poly = feat.geometry().asPolygon()[0]
            caminho = []
            lin_min = 1e8
            col_min = 1e8
            lin_max = -1e8
            col_max = -1e8
            for ponto in poly:
                linha = (origem[1]-ponto.y())/resol_Y
                if linha > lin_max:
                    lin_max = linha
                if linha < lin_min:
                    lin_min = linha
                coluna = (ponto.x() - origem[0])/resol_X
                if coluna > col_max:
                    col_max = coluna
                if coluna < col_min:
                    col_min = coluna
                caminho += [(linha, coluna)]
            p = path.Path(caminho)
            lin_min = int(np.floor(lin_min))
            lin_max = int(np.floor(lin_max))
            col_min = int(np.floor(col_min))
            col_max = int(np.floor(col_max))
            nx, ny = (lin_max-lin_min+1, col_max-col_min+1)
            lin = np.linspace(lin_min, lin_max, nx)
            col = np.linspace(col_min, col_max, ny)
            COL, LIN = np.meshgrid(col, lin)
            recorte = np.zeros((int(nx), int(ny)), dtype=bool)
            for x in range(int(nx)):
                for y in range(int(ny)):
                    pixel = (LIN[x][y]+0.5, COL[x][y]+0.5) # 0.5 eh o centro do pixel
                    contem = p.contains_points([pixel])
                    recorte[x][y] = contem[0]
            # Amostras dentro do polígono
            recorte_img = banda[lin_min:lin_max+1, col_min:col_max+1]
            if np.shape(recorte)!=np.shape(recorte_img):
                # chegou no fim do recorte
                recorte = recorte[0:np.shape(recorte_img)[0], 0:np.shape(recorte_img)[1]]
            tam = np.shape(recorte_img)
            for x in range(tam[0]):
                for y in range(tam[1]):
                    if recorte[x][y]:
                        valores += [float(recorte_img[x][y])]

        # Estatísticas dos Valores
        valores = np.array(valores)
        media = np.mean(valores)
        desvioPad = np.std(valores)

        if metodo == 0:
            lim_min = np.min(valores)
            lim_max = np.max(valores)
        elif metodo == 1:
            lim_min = np.quantile(valores,0.02)
            lim_max = np.quantile(valores,0.98)
        elif metodo == 2:
            lim_min = media - 2*desvioPad
            lim_max = media + 2*desvioPad
        elif metodo == 3:
            lim_min = media - 3*desvioPad
            lim_max = media + 3*desvioPad

        feedback.pushInfo(self.tr('Total pixels in samples: {}'.format(len(valores)), 'Total de pixels nas amostras: {}'.format(len(valores))))
        feedback.pushInfo(self.tr('Average of sample: {}'.format(media), 'Média das amostras: {}'.format(media)))
        feedback.pushInfo(self.tr('Standard deviation of samples: {}'.format(desvioPad), 'Desvio-padrão das amostras: {}'.format(desvioPad)))
        feedback.pushInfo(self.tr('Lower threshold: {}'.format(lim_min), 'Limiar inferior: {}'.format(lim_min)))
        feedback.pushInfo(self.tr('Upper threshold: {}'.format(lim_max), 'Limiar superior: {}'.format(lim_max)))

        # Varrer imagem e classificar cada pixel
        feedback.pushInfo(self.tr('Thresholding...', 'Limiarizando...'))
        RESULT = (banda > lim_min) * (banda < lim_max)*1

        # Salvando Resultado
        threshold_img = gdal.GetDriverByName('GTiff').Create(Raster_Output, cols, rows, 1, gdal.GDT_Byte)
        threshold_img.SetGeoTransform(geotransform)
        threshold_img.SetProjection(prj)
        banda = threshold_img.GetRasterBand(1)
        banda.WriteArray(RESULT)
        threshold_img.FlushCache()   # Escrever no disco
        threshold_img = None   # Salvar e fechar

        feedback.pushInfo(self.tr('Operation completed successfully!', 'Operação finalizada com sucesso!'))
        feedback.pushInfo(self.tr('Leandro Franca - Cartographic Engineer', 'Leandro França - Eng Cart'))
        self.CAMINHO = Raster_Output
        self.CARREGAR = Carregar
        return {self.RasterOUT: Raster_Output}

    # Carregamento de arquivo de saída
    CAMINHO = ''
    CARREGAR = True
    def postProcessAlgorithm(self, context, feedback):
        if self.CARREGAR:
            rlayer = QgsRasterLayer(self.CAMINHO, self.tr('Thresholded raster', 'Imagem limiarizada'))
            QgsProject.instance().addMapLayer(rlayer)
        return {}
