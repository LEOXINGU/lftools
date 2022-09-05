# -*- coding: utf-8 -*-

"""
Stat_centralTendency.py
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
__date__ = '2022-06-05'
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
                       QgsProcessingLayerPostProcessorInterface,
                       QgsApplication,
                       QgsProject,
                       QgsCoordinateTransform,
                       QgsCoordinateReferenceSystem)
import processing
import numpy as np
from numpy import pi, cos, sin, sqrt
#from scipy.stats import chi2
from lftools.geocapt.imgs import Imgs
import os
from qgis.PyQt.QtGui import QIcon


class CentralTendency(QgsProcessingAlgorithm):

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
        return CentralTendency()

    def name(self):
        return 'centraltendency'

    def displayName(self):
        return self.tr('Central Tendency', 'Tendência central')

    def group(self):
        return self.tr('Spatial Statistics', 'Estatística Espacial')

    def groupId(self):
        return 'spatialstatistics'

    def shortHelpString(self):
        if self.LOC == 'pt':
            return ""
        else:
            return self.tr("")

    def tags(self):
        return self.tr('deviational,standard,tendency,dispertion,directional,trend,confidence,covariance,mean,average,median,center,distances,centroid,').split(',')

    def icon(self):
        return QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images/statistics.png'))

    txt_en = '''RThis tool returns the central tendency point(s) for clustering points of entry points.
The following statistics can be obtained by grouping:
◼️ <b>Mean Center</b>: calculation of the average in X and Y
◼️ <b>Median Center</b>: calculation of the median in X and Y (less influenced by outliers)
◼️ <b>Central Feature</b>: identification of the central feature (smallest Euclidean distance)
Note: Layer in a projected SRC gets more accurate results.'''
    txt_pt = '''Esta ferramenta retorna o(s) ponto(s) de tendência central para agrupamento de pontos dos pontos de entrada.
As seguintes estatísticas pode ser obtidas por agrupamento:
◼️ <b>Centro Médio</b>: cálculo da média em X e Y
◼️ <b>Centro Mediano</b>: cálculo da mediana em X e Y (menos influenciado por outliers)
◼️ <b>Feição Central</b>: identificação da feição central (menor distância euclidiana)
Observação: Camada em um SRC projetado obtém resultado mais acurados.'''
    figure = 'images/tutorial/stat_central_tendency.jpg'

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
    STATS = 'STATS'
    CAMPO_AGRUPAR = 'CAMPO_AGRUPAR'
    CAMPO_PESO = 'CAMPO_PESO'
    OUTPUT = 'OUTPUT'

    def initAlgorithm(self, config=None):
        # INPUT
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT,
                self.tr('Point Layer', 'Camada de Pontos'),
                [QgsProcessing.TypeVectorPoint]
            )
        )

        tipos = [self.tr('Mean Center', 'Centro Médio'),
                 self.tr('Median Center', 'Centro Mediano'),
                 self.tr('Central Feature', 'Feição Central')]

        self.addParameter(
            QgsProcessingParameterEnum(
                self.STATS,
                self.tr('Statistics', 'Estatística'),
				options = tipos,
                defaultValue = 1
            )
        )

        self.addParameter(
            QgsProcessingParameterField(
                self.CAMPO_AGRUPAR,
                self.tr('Group Field', 'Campo de Agrupamento'),
                parentLayerParameterName=self.INPUT,
                type=QgsProcessingParameterField.Any,
                optional=True
            )
        )

        self.addParameter(
            QgsProcessingParameterField(
                self.CAMPO_PESO,
                self.tr('Weight Field', 'Campo de Peso'),
                parentLayerParameterName=self.INPUT,
                type=QgsProcessingParameterField.Numeric,
                optional=True
            )
        )

        # OUTPUT
        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT,
                self.tr('Central point', 'Ponto Cental')
            )
        )

    def processAlgorithm(self, parameters, context, feedback):

        layer = self.parameterAsSource(
            parameters,
            self.INPUT,
            context
        )
        if layer is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.INPUT))

        estat = self.parameterAsEnum(
            parameters,
            self.STATS,
            context
        )

        Campo_Peso = self.parameterAsFields(
            parameters,
            self.CAMPO_PESO,
            context
        )

        Campo_Agrupar = self.parameterAsFields(
            parameters,
            self.CAMPO_AGRUPAR,
            context
        )

        # Field index
        if Campo_Peso:
            Campo_Peso = layer.fields().indexFromName(Campo_Peso[0])
        if Campo_Agrupar:
            Campo_Agrupar = layer.fields().indexFromName(Campo_Agrupar[0])

        # OUTPUT
        if estat == 0: # média
            itens  = {
                 'id' : QVariant.Int,
                 self.tr('group','grupo'): QVariant.String,
                 'min_x' : QVariant.Double,
                 'min_y' : QVariant.Double,
                 'avg_x' : QVariant.Double,
                 'avg_y' : QVariant.Double,
                 'max_x' : QVariant.Double,
                 'max_y' : QVariant.Double,
                 'std_x' : QVariant.Double,
                 'std_y' : QVariant.Double,
                 }
        elif estat == 1: # mediana
            itens  = {
                 'id' : QVariant.Int,
                 self.tr('group','grupo'): QVariant.String,
                 'min_x' : QVariant.Double,
                 'min_y' : QVariant.Double,
                 'perc25_x' : QVariant.Double,
                 'perc25_y' : QVariant.Double,
                 'median_x' : QVariant.Double,
                 'median_y' : QVariant.Double,
                 'perc75_x' : QVariant.Double,
                 'perc75_y' : QVariant.Double,
                 'max_x' : QVariant.Double,
                 'max_y' : QVariant.Double,
                 }
        elif estat == 2: # feição central
            itens = {
                    self.tr('group','grupo'): QVariant.String,
                    self.tr('count', 'contagem'): QVariant.Int}

        if estat in (0,1):
            Fields = QgsFields()
        else:
            Fields = layer.fields()

        for item in itens:
            Fields.append(QgsField(item, itens[item]))
        (sink, dest_id) = self.parameterAsSink(
            parameters,
            self.OUTPUT,
            context,
            Fields,
            QgsWkbTypes.Point,
            layer.sourceCrs()
        )
        if sink is None:
            raise QgsProcessingException(self.invalidSinkError(parameters, self.OUTPUT))

        if Campo_Agrupar:
            dic = {}
            for feat in layer.getFeatures():
                geom = feat.geometry()
                if geom.isMultipart():
                    pnt = geom.asMultiPoint()[0]
                else:
                    pnt = geom.asPoint()
                grupo = feat[Campo_Agrupar]
                if grupo in dic:
                    dic[grupo]['x'] = dic[grupo]['x'] + [pnt.x()]
                    dic[grupo]['y'] = dic[grupo]['y'] + [pnt.y()]
                    if Campo_Peso:
                        dic[grupo]['w'] = dic[grupo]['w'] + [int(feat[Campo_Peso])]
                else:
                    if Campo_Peso:
                        dic[grupo] = {'x':[pnt.x()], 'y':[pnt.y()], 'w':[int(feat[Campo_Peso])]}
                    else:
                        dic[grupo] = {'x':[pnt.x()], 'y':[pnt.y()]}
        else:
            dic = {}
            for feat in layer.getFeatures():
                geom = feat.geometry()
                if geom.isMultipart():
                    pnt = geom.asMultiPoint()[0]
                else:
                    pnt = geom.asPoint()
                grupo = 'ungrouped'
                if grupo in dic:
                    dic[grupo]['x'] = dic[grupo]['x'] + [pnt.x()]
                    dic[grupo]['y'] = dic[grupo]['y'] + [pnt.y()]
                    if Campo_Peso:
                        dic[grupo]['w'] = dic[grupo]['w'] + [int(feat[Campo_Peso])]
                else:
                    if Campo_Peso:
                        dic[grupo] = {'x':[pnt.x()], 'y':[pnt.y()], 'w':[int(feat[Campo_Peso])]}
                    else:
                        dic[grupo] = {'x':[pnt.x()], 'y':[pnt.y()]}

        # Função para calcular a Mediana Ponderada
        def quantis_ponderados(valores, quantis, pesos):
            # entradas:
                # valores: array com valores
                # quantil: array com quantil entre 0 e 1
                # pesos: lista com mesma dimensão de valores com os respectivos pesos
            pesos = np.array(pesos)
            sorter = np.argsort(valores) # ordenar valores
            valores = valores[sorter]
            pesos = pesos[sorter]
            q = 1.*pesos.cumsum()/pesos.sum() # quantis ponderados
            return np.interp(quantis, q, valores)

        # Função para retornar a feição central
        def CentralFeature(x, y, w):
            dist_soma = 1e15
            indice = -1
            for i in range(len(x)):
                x1 = x[i]
                y1 = y[i]
                soma = 0
                for j in range(len(y)):
                    if i != j:
                        x2 = x[j]
                        y2 = y[j]
                        peso = w[j]
                        soma += peso*((x1 - x2)**2 + (y1 - y2)**2)
                if soma < dist_soma:
                    dist_soma = soma
                    indice = i
            return x[indice], y[indice]

        # Cálculo
        feature = QgsFeature()
        total = 100.0 / len(dic) if len(dic) else 0
        for current, grupo in enumerate(dic):
            x = np.array(dic[grupo]['x'])
            y = np.array(dic[grupo]['y'])
            if Campo_Peso:
                w = dic[grupo]['w']
            else:
                w = np.ones(len(x))

            if estat == 0:
                if Campo_Peso:
                    if (np.array(w) > 0).sum() > 1: # Mais de um ponto com peso maior que zero
                        mediaX = float(np.average(x, weights = w))
                        mediaY = float(np.average(y, weights = w))
                        std_X = float(np.sqrt(np.average((x-mediaX)**2, weights = w)))
                        std_Y = float(np.sqrt(np.average((y-mediaY)**2, weights = w)))
                    else:
                        continue
                else:
                    mediaX = float(np.average(x))
                    mediaY = float(np.average(y))
                    std_X = float(np.std(x))
                    std_Y = float(np.std(y))
            elif estat == 1:
                if Campo_Peso:
                    if (np.array(w) > 0).sum() > 1: # Mais de um ponto com peso maior que zero
                        perc25X, medianX, perc75X = quantis_ponderados(x, [0.25, 0.5, 0.75], w)
                        perc25Y, medianY, perc75Y = quantis_ponderados(y, [0.25, 0.5, 0.75], w)
                    else:
                        continue
                else:
                    perc25X, medianX, perc75X = np.quantile(x, [0.25, 0.5, 0.75])
                    perc25Y, medianY, perc75Y = np.quantile(y, [0.25, 0.5, 0.75])
            elif estat == 2:
                central_X, central_Y = CentralFeature(x, y, w)

            max_x = np.max(x)
            max_y = np.max(y)
            min_x = np.min(x)
            min_y = np.min(y)

            feat = QgsFeature(Fields)
            if estat == 0:
                pnt = QgsGeometry.fromPointXY(QgsPointXY(float(mediaX),float(mediaY)))
                att = [current+1, str(grupo),
                        float(min_x), float(min_y),
                        float(mediaX),float(mediaY),
                        float(max_x), float(max_y),
                        float(std_X), float(std_Y)]
            elif estat == 1:
                pnt = QgsGeometry.fromPointXY(QgsPointXY(float(medianX), float(medianY)))
                att = [current+1, str(grupo),
                    float(min_x), float(min_y),
                    float(perc25X), float(perc25Y),
                    float(medianX), float(medianY),
                    float(perc75X), float(perc75Y),
                    float(max_x), float(max_y)]
            elif estat == 2:
                pnt = QgsGeometry.fromPointXY(QgsPointXY(float(central_X), float(central_Y)))
                # Pegar atributos do ponto central
                for feat in layer.getFeatures():
                    geom = feat.geometry()
                    if geom.isMultipart():
                        coord = geom.asMultiPoint()[0]
                    else:
                        coord = geom.asPoint()
                    if coord.x() == central_X and coord.y() == central_Y:
                        att = feat.attributes()
                        break
                att += [str(grupo), len(x)]

            feat.setGeometry(pnt)
            feat.setAttributes(att)

            sink.addFeature(feat, QgsFeatureSink.FastInsert)
            if feedback.isCanceled():
                break
            feedback.setProgress(int(current * total))

        feedback.pushInfo(self.tr('Operation completed successfully!', 'Operação finalizada com sucesso!'))
        feedback.pushInfo(self.tr('Leandro Franca - Cartographic Engineer', 'Leandro França - Eng Cart'))

        global renamer
        tipos = [self.tr('Mean Center', 'Centro Médio'),
                 self.tr('Median Center', 'Centro Mediano'),
                 self.tr('Central Feature', 'Feição Central')]
        renamer = Renamer(self.tr('Central tendency - ', 'Tendência central - ') + tipos[estat])
        context.layerToLoadOnCompletionDetails(dest_id).setPostProcessor(renamer)

        return {self.OUTPUT: dest_id}

class Renamer (QgsProcessingLayerPostProcessorInterface):
    def __init__(self, layer_name):
        self.name = layer_name
        super().__init__()

    def postProcessLayer(self, layer, context, feedback):
        layer.setName(self.name)
