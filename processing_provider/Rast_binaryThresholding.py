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
from lftools.translations.translate import translate
from lftools.geocapt.dip import Interpolar
from lftools.geocapt.cartography import reprojectPoints
import os
from qgis.PyQt.QtGui import QIcon

class BinaryThresholding(QgsProcessingAlgorithm):

    LOC = QgsApplication.locale()[:2]

    def tr(self, *string):
        return translate(string, self.LOC)

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
        return 'GeoOne,thresholding,binary,supervised,variance,mean,average,histogram,standard,statistics'.split(',')

    def icon(self):
        return QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images/raster.png'))

    txt_en = '''Creates a binarized raster, dividing the input raster into two distinct classes from statistical data (lower and upper threshold) from area or point samples. Optionally, minimum and maximum threshold values can also be set.
A class matches the values within the range of thresholds, where the value 1 (true) is returned. The other class corresponds to values outside the range, returning the value 0 (false).'''
    txt_pt = '''Cria um raster binarizado, dividindo o raster de entrada em duas classes distintas a partir de dados estatísticos (limiar inferior e superior) de amostras de áreas ou pontuais. Opcionalmente, os valores de limiar mínimo e máximo também podem ser definidos.
Uma classe irá corresponder aos valores compreendidos dentro do intervalo dos limiares, sendo retornado o valor 1 (verdadeiro). Já a outra classe correpondem aos valores fora do intervalo, sendo retornado o valor 0 (falso).'''
    figure = 'images/tutorial/raster_thresholding.jpg'

    def shortHelpString(self):
        social_BW = Imgs().social_BW
        nota_en = '''Note: Binary thresholding is one of the easiest and fastest ways to classify an image from an index such as NDVI. This algorithm can be used to identify areas with vegetation cover using an index such as the NDVI (França et al., 2017).
Reference:'''
        nota_pt = '''Nota: A binarização é uma das formas mais fáceis e rápidas para classificar uma imagem a partir de um índice como o NDVI. Este algoritmo pode ser utilizado para identificar áreas com cobertura vegetal a partir de um índice como o NDVI (França et al., 2017).
Referência:'''
        footer = '''<div align="center">
                      <img src="'''+ os.path.join(os.path.dirname(os.path.dirname(__file__)), self.figure) +'''">
                      </div>
                      <div align="right">
                      <div>''' + self.tr(nota_en, nota_pt) + '''
                      </div>
                      <p align="right">
                      <b><a href="https://www.researchgate.net/publication/320020755_Mapping_of_the_spatial-temporal_change_for_vegetation_canopy_in_rough_relief_areas" target="_blank">'''+self.tr('FRANÇA, L. L. S.; SILVA, L. F. C. F.; SILVA, W. B. Mapping of the spatial-temporal change for vegetation canopy in rough relief areas. R. bras. Geom., Curitiba, v. 5, n. 3, p. 343-360, jul/set. 2017.') + '''</b>
                                    ''' +'</a><br><b>'+ self.tr('Author: Leandro Franca', 'Autor: Leandro França')+'''</b>
                      </p>'''+ social_BW + '''</div>
                    </div>'''
        return self.tr(self.txt_en, self.txt_pt) + footer

    RasterIN ='RasterIN'
    RasterOUT = 'RasterOUT'
    SAMPLES = 'SAMPLES'
    METHOD = 'METHOD'
    VALUES = 'VALUES'
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
                [QgsProcessing.TypeVectorPolygon, QgsProcessing.TypeVectorPoint],
                optional = True
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
                defaultValue= 3
            )
        )

        self.addParameter(
            QgsProcessingParameterString(
                self.VALUES,
                self.tr('Threshold values (minimum and maximum) separated by comma', 'Valores de limiares (mínimo e máximo) separadados por vírgula'),
                optional = True
            )
        )

        # OUTPUT
        self.addParameter(
            QgsProcessingParameterFileDestination(
                self.RasterOUT,
                self.tr('Binarized raster', 'Imagem binarizada'),
                fileFilter = 'GeoTIFF (*.tif)'
            )
        )

        self.addParameter(
            QgsProcessingParameterBoolean(
                self.OPEN,
                self.tr('Load binarized image', 'Carregar imagem binarizada'),
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

        minmax = self.parameterAsString(
            parameters,
            self.VALUES,
            context
        )

        layer = self.parameterAsSource(
            parameters,
            self.SAMPLES,
            context
        )

        if layer is None and not minmax:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.SAMPLES))

        if not layer:
            try:
                minmax = minmax.replace(' ','')
                a, b = minmax.split(',')
                a, b = float(a), float(b)
                if a < b:
                    lim_min = a
                    lim_max = b
                elif a > b:
                    lim_min = b
                    lim_max = a
                else:
                    raise QgsProcessingException(self.tr('The maximum and minimum thresholds cannot be the same!', 'O limiares máximo e mínimo não podem ser iguais!'))
            except:
                raise QgsProcessingException(self.tr('Check that the minimum and maximum threshold values are correct!', 'Verifique se os valores de limiares mínimo e máximo estão corretos!'))

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
        SRC_rater = QgsCoordinateReferenceSystem(prj)
        num_bands = image.RasterCount
        if num_bands != 1:
            raise QgsProcessingException(self.tr('The raster layer must have only 1 band!', 'A camada raster deve ter apenas 1 banda!'))
        banda = image.GetRasterBand(1).ReadAsArray()
        Pixel_Nulo = image.GetRasterBand(1).GetNoDataValue()
        Pixel_Nulo = Pixel_Nulo if Pixel_Nulo else 0
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


        if not minmax:
            # Amostra de Raster por poligono
            feedback.pushInfo(self.tr('Taking raster samples by polygon...', 'Pegando amostras do raster por polígono...'))
            valores = []

            # Verificando SRC das camadas
            mesmoSRC = True
            if SRC_rater != layer.sourceCrs():
                mesmoSRC = False
                coordinateTransformer = QgsCoordinateTransform()
                coordinateTransformer.setDestinationCrs(SRC_rater)
                coordinateTransformer.setSourceCrs(layer.sourceCrs())

            try: #poligono if layer.wkbType() == QgsWkbTypes.PolygonGeometry:
                for feat in layer.getFeatures():
                    geom = feat.geometry() if mesmoSRC else reprojectPoints(feat.geometry(), coordinateTransformer)
                    if geom.isMultipart():
                        poly = geom.asMultiPolygon()[0][0]
                    else:
                        poly = geom.asPolygon()[0]
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
            except: #ponto elif layer.wkbType() == QgsWkbTypes.PointGeometry:
                for feat in layer.getFeatures():
                    geom = feat.geometry() if mesmoSRC else reprojectPoints(feat.geometry(), coordinateTransformer)
                    if geom.isMultipart():
                        ponto = geom.asMultiPoint()[0]
                    else:
                        ponto = geom.asPoint()
                    valorPixel = Interpolar(ponto.x(), ponto.y(), banda, origem, resol_X, resol_Y, metodo = 'nearest', nulo = Pixel_Nulo)
                    valores += [valorPixel]

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
            rlayer = QgsRasterLayer(self.CAMINHO, self.tr('Binarized raster', 'Imagem binarizada'))
            QgsProject.instance().addMapLayer(rlayer)
        return {}
