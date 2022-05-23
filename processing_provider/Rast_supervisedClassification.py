# -*- coding: utf-8 -*-

"""
supervisedClassification.py
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
__date__ = '2020-09-19'
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
                       QgsProject,
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

class SupervisedClassification(QgsProcessingAlgorithm):

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
        return SupervisedClassification()

    def name(self):
        return 'supervisedclassification'

    def displayName(self):
        return self.tr('Supervised classification', 'Classificação supervisionada')

    def group(self):
        return self.tr('Raster')

    def groupId(self):
        return 'raster'

    def tags(self):
        return self.tr('classification,supervised,ellipse,rectangle,mahalanobis,sphefere,covariance,statistics').split(',')

    def icon(self):
        return QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images/raster.png'))

    txt_en = 'Performs the supervised classification of a raster layer with two or more bands.'
    txt_pt = 'Realize a classificação supervisionada de camada raster com duas ou mais bandas.'
    figure = 'images/tutorial/raster_classification.jpg'

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
    CLASSES = 'CLASSES'
    FIELD = 'FIELD'
    METHOD = 'METHOD'
    SIZE = 'SIZE'
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
                self.CLASSES,
                self.tr('Sample Polygons', 'Polígonos de Amostra'),
                [QgsProcessing.TypeVectorPolygon]
            )
        )

        self.addParameter(
            QgsProcessingParameterField(
                self.FIELD,
                self.tr('Class Field', 'Campo da Classe'),
                parentLayerParameterName=self.CLASSES,
                type=QgsProcessingParameterField.Numeric
            )
        )

        metodos = [self.tr('Parallelepiped', 'Paralelepípedo'),
                   self.tr('Ellipsoid', 'Elipsoide'),
                   self.tr('Euclidean Distance', 'Distância Euclidiana'),
                   self.tr('Mahalanobis Distance', 'Distância de Mahalanobis')]

        self.addParameter(
            QgsProcessingParameterEnum(
                self.METHOD,
                self.tr('Method', 'Método'),
				options = metodos,
                defaultValue= 0
            )
        )

        tam   = [self.tr('1 Standard Deviation (68%)', '1 Desvio-Padrão (68%)'),
                 self.tr('2 Standard Deviations (95%)', '2 Desvios-Padrões (95%)'),
                 self.tr('3 Standard Deviations (99.7%)', '3 Desvios-Padrões (99,7%)')]

        self.addParameter(
            QgsProcessingParameterEnum(
                self.SIZE,
                self.tr('Size (only for Parallelepiped and Ellipsoid Methods)', 'Tamanho (apenas para os Métodos do Paralelepípedo e Elipsoide)'),
				options = tam,
                defaultValue= 2
            )
        )

        # OUTPUT
        self.addParameter(
            QgsProcessingParameterFileDestination(
                self.RasterOUT,
                self.tr('Classified Image', 'Imagem Classificada'),
                fileFilter = 'GeoTIFF (*.tif)'
            )
        )

        self.addParameter(
            QgsProcessingParameterBoolean(
                self.OPEN,
                self.tr('Load classified Image', 'Carregar Imagem Classificada'),
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
            self.CLASSES,
            context
        )
        if layer is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.CLASSES))

        campo = self.parameterAsFields(
            parameters,
            self.FIELD,
            context
        )
        if campo is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.FIELD))

        metodo = self.parameterAsEnum(
            parameters,
            self.METHOD,
            context
        )

        size = self.parameterAsEnum(
            parameters,
            self.SIZE,
            context
        )
        fator = size+1

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
        n_bands = image.RasterCount
        if n_bands < 2:
            raise QgsProcessingException(self.tr('The raster layer must have more than 1 band!', 'A camada raster deve ter mais de 1 banda!'))
        bandas = []
        for k in range(n_bands):
            bandas += [image.GetRasterBand(k+1).ReadAsArray()]
        Pixel_Nulo = image.GetRasterBand(1).GetNoDataValue()
        if Pixel_Nulo == None:
            Pixel_Nulo = 0
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

        # Transformação de coordenadas
        crsSrc = layer.sourceCrs()
        crsDest = QgsCoordinateReferenceSystem(prj)
        if crsSrc != crsDest:
            transf_SRC = True
            coordTransf = QgsCoordinateTransform(crsSrc, crsDest, QgsProject.instance())
        else:
            transf_SRC = False

        # Amostra de Raster por poligono
        dic = {}
        for feat in layer.getFeatures():
            code = feat[campo[0]]
            if code not in dic:
                bands_dic = {}
                for k in range(n_bands):
                    bands_dic[k+1] = []
                dic[code] = {'valores': bands_dic}
            geom = feat.geometry()
            if transf_SRC:
                geom.transform(coordTransf)
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
            # Recorte de cada banda
            for k in range(n_bands):
                banda = bandas[k]
                recorte_img = banda[lin_min:lin_max+1, col_min:col_max+1]
                if np.shape(recorte)!=np.shape(recorte_img):
                    # chegou no fim do recorte
                    recorte = recorte[0:np.shape(recorte_img)[0], 0:np.shape(recorte_img)[1]]
                tam = np.shape(recorte_img)
                valores = []
                for x in range(tam[0]):
                    for y in range(tam[1]):
                        if recorte[x][y]:
                            valores += [float(recorte_img[x][y])]
                dic[code]['valores'][k+1] = dic[code]['valores'][k+1] + valores

        # Cálculo da Média por banda e MVC de cada classe
        ordem = []
        for code in dic:
            media = []
            desvpad = []
            val_list = []
            for k in range(n_bands):
                valores = dic[code]['valores'][k+1]
                media += [[np.mean(valores)]]
                desvpad += [[np.std(valores)]]
                val_list += [valores]
            MVC = np.matrix(np.cov(np.array(val_list)))
            media = np.array(media)
            desvpad = np.array(desvpad)
            dic[code]['media'] = media
            dic[code]['desvpad'] = desvpad
            dic[code]['mvc'] = MVC
            dic[code]['det'] = np.linalg.det(MVC*fator**2)
            if dic[code]['det'] == 0 and metodo == 3:
                raise QgsProcessingException(self.tr('Covariance matrix is singular. Choose another method!', 'Matriz Covariância é singular. Escolha outro método!'))
            elif dic[code]['det'] != 0:
                dic[code]['MVC_inv'] = np.linalg.inv(MVC)
            ordem += [[np.trace(MVC), code]]
        ordem = sorted(ordem, reverse = True)

        # Varrer imagem e classificar cada pixel
        img_class = np.zeros((rows, cols), dtype=np.byte)
        total = 100.0/rows

        if metodo == 0: # Paralelepípedo
            for lin in range(rows):
                for col in range(cols):
                    px = []
                    for k in range(n_bands):
                        px += [[float(bandas[k][lin][col])]]
                    px = np.array(px)
                    classe = None
                    for item in ordem:
                        m = dic[item[1]]['media']
                        s = dic[item[1]]['desvpad']
                        cond = (m-fator*s < px) * (px < m+fator*s)
                        if cond.sum() == len(px):
                            classe = item[1]
                    if classe:
                        img_class[lin,col] = classe
                feedback.setProgress(int((lin+1) * total))
                if feedback.isCanceled():
                    break

        elif metodo == 1: # Elipsoide
            for lin in range(rows):
                for col in range(cols):
                    px = []
                    for k in range(n_bands):
                        px += [[float(bandas[k][lin][col])]]
                    px = np.array(px)
                    classe = None
                    for item in ordem:
                        m = dic[item[1]]['media']
                        mvc = dic[item[1]]['mvc']
                        det = dic[item[1]]['det']
                        pos = (px - m).T*mvc*(px - m) - det
                        if pos <= 0:
                            classe = item[1]
                    if classe:
                        img_class[lin,col] = classe
                feedback.setProgress(int((lin+1) * total))
                if feedback.isCanceled():
                    break

        elif metodo == 2: # Distância Euclidiana
            for lin in range(rows):
                for col in range(cols):
                    px = []
                    for k in range(n_bands):
                        px += [[float(bandas[k][lin][col])]]
                    px = np.array(px)
                    min_dist = 1e9
                    classe = None
                    for code in dic:
                        m = dic[code]['media']
                        dist = (px - m).T*(px - m)
                        if dist[0][0] < min_dist:
                            min_dist = dist[0][0]
                            classe = code
                    img_class[lin,col] = classe
                feedback.setProgress(int((lin+1) * total))
                if feedback.isCanceled():
                    break

        elif metodo == 3: # Distância de Mahalanobis
            for lin in range(rows):
                for col in range(cols):
                    px = []
                    for k in range(n_bands):
                        px += [[float(bandas[k][lin][col])]]
                    px = np.array(px)
                    min_dist = 1e9
                    classe = None
                    for code in dic:
                        m = dic[code]['media']
                        MVC_inv = dic[code]['MVC_inv']
                        dist_Mah = (px - m).T*MVC_inv*(px - m)
                        if dist_Mah[0][0] < min_dist:
                            min_dist = dist_Mah[0][0]
                            classe = code
                    img_class[lin,col] = classe
                feedback.setProgress(int((lin+1) * total))
                if feedback.isCanceled():
                    break


        # Salvando Resultado
        GDT = gdal_array.NumericTypeCodeToGDALTypeCode(img_class.dtype)
        classified_img = gdal.GetDriverByName('GTiff').Create(Raster_Output, cols, rows, 1, GDT)
        classified_img.SetGeoTransform(geotransform)
        classified_img.SetProjection(prj)
        banda = classified_img.GetRasterBand(1)
        banda.WriteArray(img_class)
        banda.SetNoDataValue(Pixel_Nulo)
        classified_img.FlushCache()   # Escrever no disco
        classified_img = None   # Salvar e fechar



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
            rlayer = QgsRasterLayer(self.CAMINHO, self.tr('Classified Image', 'Imagem Classificada'))
            QgsProject.instance().addMapLayer(rlayer)
        return {}
