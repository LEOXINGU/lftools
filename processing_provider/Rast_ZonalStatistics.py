# -*- coding: utf-8 -*-

"""
Rast_ZonalStatistics.py
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
__date__ = '2023-06-04'
__copyright__ = '(C) 2023, Leandro França'

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

class ZonalStatistics(QgsProcessingAlgorithm):

    LOC = QgsApplication.locale()[:2]

    def tr(self, *string):
        return translate(string, self.LOC)

    def createInstance(self):
        return ZonalStatistics()

    def name(self):
        return 'zonalstatistics'

    def displayName(self):
        return self.tr('Zonal Statistics', 'Estatísticas zonais')

    def group(self):
        return self.tr('Raster')

    def groupId(self):
        return 'raster'

    def tags(self):
        return self.tr('estatísticas,statistics,zonal,zonais,amostra,sample,mean,average,std,bands,values').split(',')

    def icon(self):
        return QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images/raster.png'))

    txt_en = '''This algorithm calculates statistics for the bands of a raster layer, categorized by zones defined in a polygon type vector layer.
The values of the raster cells where the pixel center is exactly inside the polygon are considered in the statistics.'''
    txt_pt = '''Este algoritmo calcula estatísticas para as bandas de uma camada raster, categorizados por zonas definidas em camada vetorial do tipo polígono.
Os valores das células do raster onde o centro do pixel se encontra exatamente dentro do polígonos são considerados nas estatísticas.'''
    figure = 'images/tutorial/raster_zonalstatistics.jpg'

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
    BAND = 'BAND'
    POLYGONS = 'POLYGONS'
    PREFIX = 'PREFIX'
    STATISTICS = 'STATISTICS'
    OUTPUT = 'OUTPUT'
    STATS = ['count','sum','mean','median', 'std', 'min', 'max']

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
            QgsProcessingParameterBand(
                self.BAND,
                self.tr('Band', 'Banda'),
                parentLayerParameterName=self.INPUT,
                optional = True
            )
        )

        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.POLYGONS,
                self.tr('Polygons', 'Polígonos'),
                [QgsProcessing.TypeVectorPolygon]
            )
        )

        self.addParameter(
            QgsProcessingParameterString(
                self.PREFIX,
                self.tr('Output column prefix', 'Prefixo da coluna de saída'),
                defaultValue = self.tr('stat_', 'estat_')
            )
        )

        self.addParameter(
            QgsProcessingParameterEnum(
                self.STATISTICS,
                self.tr('Statistics', 'Estatísticas'),
				options = self.STATS,
                allowMultiple = True,
                defaultValue = [2,4]
            )
        )

        # OUTPUT
        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT,
                self.tr('Zonal statistics', 'Estatísticas zonais')
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

        layer = self.parameterAsSource(
            parameters,
            self.POLYGONS,
            context
        )
        if layer is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.POLYGONS))

        stats = self.parameterAsEnums(
            parameters,
            self.STATISTICS,
            context
        )

        n_banda = self.parameterAsInt(
            parameters,
            self.BAND,
            context
        )

        prefixo = self.parameterAsString(
            parameters,
            self.PREFIX,
            context
        )

        # Abrir Raster layer como array
        feedback.pushInfo(self.tr('Opening raster...', 'Abrindo raster...'))
        image = gdal.Open(RasterIN)
        prj = image.GetProjection()
        n_bands = image.RasterCount
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

        # Transformação de coordenadas
        crsSrc = layer.sourceCrs()
        crsDest = QgsCoordinateReferenceSystem(prj)
        if crsSrc != crsDest:
            transf_SRC = True
            coordTransf = QgsCoordinateTransform(crsSrc, crsDest, QgsProject.instance())
        else:
            transf_SRC = False

        # Amostra de Raster por banda e poligono
        dic = {}
        if n_banda == 0: # Calculo para todas as bandas
            n_bands = np.array(range(n_bands))+1
        else: # Calculo para uma banda específica
            n_bands = [n_banda]

        total = 100.0/(len(n_bands)*layer.featureCount())
        cont = 0
        feedback.pushInfo(self.tr('Calculating zonal statistics...', 'Calculando estatísticas zonais...'))
        for k in n_bands:
            banda = image.GetRasterBand(int(k)).ReadAsArray()
            for feat in layer.getFeatures():
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

                # Recorte de banda
                recorte_img = banda[lin_min:lin_max+1, col_min:col_max+1]
                if np.shape(recorte)!=np.shape(recorte_img):
                    # chegou no fim do recorte
                    recorte = recorte[0:np.shape(recorte_img)[0], 0:np.shape(recorte_img)[1]]
                tam = np.shape(recorte_img)
                valores = []
                for x in range(tam[0]):
                    for y in range(tam[1]):
                        if recorte[x][y]:
                            valor = recorte_img[x][y]
                            if valor != Pixel_Nulo:
                                valores += [float(valor)]
                # Calcular estatísticas da lista de valores
                valores = np.array(valores)
                lista_stats = []
                for st in stats:
                    if self.STATS[st] == 'count':
                        lista_stats += [int(len(valores))]
                    if self.STATS[st] == 'sum':
                        lista_stats += [float(valores.sum())]
                    if self.STATS[st] == 'mean':
                        lista_stats += [float(valores.mean())]
                    if self.STATS[st] == 'median':
                        lista_stats += [float(np.median(valores))]
                    if self.STATS[st] == 'std':
                        lista_stats += [float(valores.std())]
                    if self.STATS[st] == 'min':
                        lista_stats += [float(valores.min())]
                    if self.STATS[st] == 'max':
                        lista_stats += [float(valores.max())]
                if feat.id() not in dic:
                    dic[feat.id()] = {(k):lista_stats}
                else:
                    dic[feat.id()][k] = lista_stats

                cont += 1
                feedback.setProgress(int((cont) * total))
                if feedback.isCanceled():
                    break

        # Criar polígono de saída
        feedback.pushInfo(self.tr('Creating layer with results...', 'Criando camada com resultados...'))
        Fields = layer.fields()
        for band in n_bands:
            for st in stats:
                Fields.append(QgsField(prefixo + self.tr('band{}_'.format(band), 'banda{}_'.format(band)) + self.STATS[st], QVariant.Double))

        (sink, dest_id) = self.parameterAsSink(
            parameters,
            self.OUTPUT,
            context,
            Fields,
            layer.wkbType(),
            layer.sourceCrs()
        )
        if sink is None:
            raise QgsProcessingException(self.invalidSinkError(parameters, self.OUTPUT))

        # Exportar resultados
        for feat in layer.getFeatures():
            att = feat.attributes()
            for band in n_bands:
                att += dic[feat.id()][band]
            feature = QgsFeature(Fields)
            feature.setAttributes(att)
            feature.setGeometry(feat.geometry())
            sink.addFeature(feature, QgsFeatureSink.FastInsert)

        feedback.pushInfo(self.tr('Operation completed successfully!', 'Operação finalizada com sucesso!'))
        feedback.pushInfo(self.tr('Leandro Franca - Cartographic Engineer', 'Leandro França - Eng Cart'))

        return {self.OUTPUT: dest_id}
