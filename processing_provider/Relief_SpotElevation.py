# -*- coding: utf-8 -*-

"""
Relief_SpotElevation.py
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
__date__ = '2021-12-18'
__copyright__ = '(C) 2021, Leandro França'

from qgis.PyQt.QtCore import QVariant
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
                       QgsProcessingParameterVectorLayer,
                       QgsProcessingParameterRasterLayer,
                       QgsProcessingParameterRasterDestination,
                       QgsApplication,
                       QgsProject,
                       QgsRasterLayer,
                       QgsCoordinateTransform,
                       QgsCoordinateReferenceSystem)

from osgeo import osr, gdal_array, gdal #https://gdal.org/python/
import numpy as np
from pyproj.crs import CRS
from math import floor, ceil
from lftools.geocapt.imgs import Imgs
from lftools.translations.translate import translate
import os
from qgis.PyQt.QtGui import QIcon
from matplotlib import path

class SpotElevation(QgsProcessingAlgorithm):

    LOC = QgsApplication.locale()[:2]

    def tr(self, *string):
        return translate(string, self.LOC)

    def createInstance(self):
        return SpotElevation()

    def name(self):
        return 'spotelevation'

    def displayName(self):
        return self.tr('Generate Spot Elevations', 'Gerar Pontos Cotados')

    def group(self):
        return self.tr('Relief', 'Relevo')

    def groupId(self):
        return 'relief'

    def tags(self):
        return 'GeoOne,dem,dsm,dtm,mde,mdt,mds,terreno,relevo,contours,curvas,nível,isoline,isolinha,ponto,cotado,spot,elevation,height'.split(',')

    def icon(self):
        return QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images/contours.png'))

    txt_en = '''This tool generates a layer of points with <b>Spot Elevations</b> from a <b>Digital Terrain Model</b> and a vector layer of <b>contour lines</b>.'''
    txt_pt = '''Esta ferramenta gera uma camada de <b>pontos cotados</b> gerados a partir de um raster correspondente ao <b>Modelo Digital do Terreno</b> e uma camada vetorial do tipo linha correspondente às <b>curvas de nível</b>.'''
    figure = 'images/tutorial/relief_spot_elevation.jpg'

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
    CONTOURS = 'CONTOURS'
    FIELD = 'FIELD'
    SPOTS = 'SPOTS'

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
            QgsProcessingParameterFeatureSource(
                self.CONTOURS,
                self.tr('Contour Lines', 'Curvas de nível'),
                [QgsProcessing.TypeVectorLine]
            )
        )

        self.addParameter(
            QgsProcessingParameterField(
                self.FIELD,
                self.tr('Elevation field', 'Campo com valor da cota'),
                parentLayerParameterName=self.CONTOURS,
                type=QgsProcessingParameterField.Numeric
            )
        )

        # OUTPUT
        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.SPOTS,
                self.tr('Spot Elevations', 'Pontos cotados')
            )
        )

    def processAlgorithm(self, parameters, context, feedback):

        # inputs
        RasterIN = self.parameterAsRasterLayer(
            parameters,
            self.INPUT,
            context
        )
        if RasterIN is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.INPUT))
        RasterIN = RasterIN.dataProvider().dataSourceUri()

        curvas = self.parameterAsSource(
            parameters,
            self.CONTOURS,
            context
        )
        if curvas is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.CONTOURS))

        campo = self.parameterAsFields(
            parameters,
            self.FIELD,
            context
        )
        # Field index
        campo_id = curvas.fields().indexFromName(campo[0])


        # Abrir arquivo Raster
        feedback.pushInfo(self.tr('Opening raster file...', 'Abrindo arquivo Raster...'))
        # Abrir Raster layer como array
        image = gdal.Open(RasterIN)
        band = image.GetRasterBand(1).ReadAsArray()
        prj = image.GetProjection()
        geotransform = image.GetGeoTransform()
        SRC = QgsCoordinateReferenceSystem()
        SRC.createFromWkt(prj)
        cols = image.RasterXSize # Number of columns
        rows = image.RasterYSize # Number of rows
        # Origem e resolucao da imagem
        ulx, xres, xskew, uly, yskew, yres  = image.GetGeoTransform()
        origem = (ulx, uly)
        resol_X = abs(xres)
        resol_Y = abs(yres)
        image=None # Close image

        # Transformação de coordenadas
        crsSrc = curvas.sourceCrs()
        crsDest = QgsCoordinateReferenceSystem(prj)
        if crsSrc != crsDest:
            transf_SRC = True
            coordTransf = QgsCoordinateTransform(crsSrc, crsDest, QgsProject.instance())
        else:
            transf_SRC = False

        # OUTPUT
        Fields = QgsFields()
        itens  = {
                     self.tr('elevation','cota') : QVariant.Double,
                     self.tr('type','tipo') : QVariant.Int,
                     }
        for item in itens:
            Fields.append(QgsField(item, itens[item]))
        (sink, dest_id) = self.parameterAsSink(
            parameters,
            self.SPOTS,
            context,
            Fields,
            QgsWkbTypes.Point,
            crsDest
        )
        if sink is None:
            raise QgsProcessingException(self.invalidSinkError(parameters, self.SPOTS))

        # Verificar todas as feicoes e armazenar aquelas que sao anel linear
        poligonos = []
        pontos = []
        cotas = []
        for feature in curvas.getFeatures():
            geom = feature.geometry()
            if transf_SRC:
                geom.transform(coordTransf)
            if geom.isMultipart():
                coord = geom.asMultiPolyline()[0]
            else:
                coord = geom.asPolyline()
            if len(coord)>4 and coord[0] == coord[-1]:
                poligonos += [coord]
                pontos += [coord[0]]
                cotas += [feature[campo_id]]
            if feedback.isCanceled():
                raise QgsProcessingException(self.tr('The process was finished!', 'Processo finalizado!'))
                break

        # Verificando qual Curva esta dentro de outra
        lista = []
        COTAS = []
        for index, poligono in enumerate(poligonos):
            polygon = QgsGeometry.fromPolygonXY([poligono])
            ponto_poly = poligono[0]
            sentinela = True
            for ponto in pontos:
                point = QgsGeometry.fromPointXY(ponto)
                if polygon.contains(point) and ponto_poly != ponto:
                    sentinela = False
                    break
            if sentinela:
                lista += [poligono]
                COTAS += [cotas[index]]

        # Amostra de Raster por poligono
        Percent = 100.0/len(lista) if len(lista)>0 else 0
        for index, poly in enumerate(lista):
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
            # Determinar qual(is) pixel(s) eh de maximo ou minimo
            recorte_img = band[lin_min:lin_max+1, col_min:col_max+1]
            if np.shape(recorte)==np.shape(recorte_img):
                produto = recorte*recorte_img
            else:
                recorte = recorte[0:np.shape(recorte_img)[0], 0:np.shape(recorte_img)[1]]
                produto = recorte*recorte_img
            min = 1e8
            max = -1e8
            tam = np.shape(produto)
            MIN = -1
            MAX = -1
            for x in range(tam[0]):
                for y in range(tam[1]):
                    if produto[x][y] < min and produto[x][y]!=0:
                        min = produto[x][y]
                        MIN = (x,y)
                    if produto[x][y] > max and produto[x][y]!=0:
                        max = produto[x][y]
                        MAX = (x,y)
            # Saber se eh depressao ou pico
            COTA = COTAS[index]
            TIPO = 0
            if np.sum(produto)/np.sum(recorte) > COTA:
                TIPO = 1 # pico
                VALOR = max
                coord = MAX
            else:
                TIPO = -1 # depressao
                VALOR = min
                coord = MIN
            cota = float(VALOR)
            # Determinar a coordenada do pixel da cota
            if coord != -1:
                X = origem[0] + resol_X*(col_min+0.5+coord[1])
                Y = origem[1] - resol_Y*(lin_min+0.5+coord[0])
                # Criar feicao
                feat = QgsFeature(Fields)
                feat.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(X,Y)))
                feat.setAttributes([cota, TIPO])
                sink.addFeature(feat, QgsFeatureSink.FastInsert)

            if feedback.isCanceled():
                break
            feedback.setProgress(int((index+1) * Percent))


        feedback.pushInfo(self.tr('Operation completed successfully!', 'Operação finalizada com sucesso!'))
        feedback.pushInfo(self.tr('Leandro Franca - Cartographic Engineer', 'Leandro França - Eng Cart'))

        return {self.SPOTS: dest_id}
