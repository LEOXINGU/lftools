# -*- coding: utf-8 -*-

"""
Stat_standardDistance.py
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
__date__ = '2023-01-22'
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
                       QgsApplication,
                       QgsProject,
                       QgsCoordinateTransform,
                       QgsCoordinateReferenceSystem)
import processing
import numpy as np
from numpy import pi, cos, sin, sqrt
#from scipy.stats import chi2
from lftools.geocapt.imgs import Imgs
from lftools.translations.translate import translate
import os
from qgis.PyQt.QtGui import QIcon


class StandardDistance(QgsProcessingAlgorithm):

    LOC = QgsApplication.locale()[:2]

    def tr(self, *string):
        return translate(string, self.LOC)

    def createInstance(self):
        return StandardDistance()

    def name(self):
        return 'standarddistance'

    def displayName(self):
        return self.tr('Standard Distance', 'Distância padrão')

    def group(self):
        return self.tr('Spatial Statistics', 'Estatística Espacial')

    def groupId(self):
        return 'spatialstatistics'

    def tags(self):
        return self.tr('circle,círculo,circunferência,confidence,deviational,standard,tendency,dispertion,directional,trend,confidence,covariance,mvc').split(',')

    def icon(self):
        return QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images/statistics.png'))

    txt_en = 'Measures the degree to which features are concentrated or dispersed around the geometric mean center.'
    txt_pt = 'Mede o grau em que as feições estão concentradas ou dispersas em torno do centro médio geométrico.'
    figure = 'images/tutorial/stat_standard_distance.jpg'

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
    TAM = 'TAM'
    CAMPO_PESO = 'CAMPO_PESO'
    CAMPO_AGRUPAR = 'CAMPO_AGRUPAR'
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

        tipos = [self.tr('1 standard deviation', '1 desvio-padrão'),
                 self.tr('2 standard deviations', '2 desvios-padrões'),
                 self.tr('3 standard deviations', '3 desvios-padrões')
                 ]

        self.addParameter(
            QgsProcessingParameterEnum(
                self.TAM,
                self.tr('Circle Size', 'Tamanho do círculo'),
				options = tipos,
                defaultValue = 1
            )
        )


        self.addParameter(
            QgsProcessingParameterField(
                self.CAMPO_PESO,
                self.tr('Weight Field', 'Campo de Peso'),
                parentLayerParameterName = self.INPUT,
                type = QgsProcessingParameterField.Numeric,
                optional = True
            )
        )

        self.addParameter(
            QgsProcessingParameterField(
                self.CAMPO_AGRUPAR,
                self.tr('Group Field', 'Campo de Agrupamento'),
                parentLayerParameterName=self.INPUT,
                type = QgsProcessingParameterField.Any,
                optional = True
            )
        )

        # OUTPUT
        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT,
                self.tr('Standard Distance', 'Distância Padrão')
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

        size = self.parameterAsEnum(
            parameters,
            self.TAM,
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
        GeomType = QgsWkbTypes.Polygon
        Fields = QgsFields()
        CRS = layer.sourceCrs()
        itens  = {
             'id' : QVariant.Int,
             self.tr('group','grupo'): QVariant.String,
             'avg_x' : QVariant.Double,
             'avg_y' : QVariant.Double,
             'std_x' : QVariant.Double,
             'std_y' : QVariant.Double,
             'std': QVariant.Double,
             self.tr('size','tamanho'): QVariant.Double
             }
        for item in itens:
            Fields.append(QgsField(item, itens[item]))
        (sink, dest_id) = self.parameterAsSink(
            parameters,
            self.OUTPUT,
            context,
            Fields,
            GeomType,
            CRS
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

        feature = QgsFeature()
        total = 100.0 / len(dic) if len(dic) else 0
        for current, grupo in enumerate(dic):
            x = np.array(dic[grupo]['x'])
            y = np.array(dic[grupo]['y'])
            if Campo_Peso:
                w = dic[grupo]['w']

            if len(x)==1:
                raise QgsProcessingException(self.tr("Invalid Group Field!","Campo de Agrupamento Inválido!"))

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

            # Círculo para um determinado desvio-padrão
            # Centro da Círculo
            C = [mediaX, mediaY]

            # Construção do círculo
            p = np.arange(0,2*pi,0.1)

            # Raio
            R =  np.sqrt(std_X**2 + std_Y**2)
            s = size + 1
            x_cir = s*R*cos(p) + C[0]
            y_cir = s*R*sin(p) + C[1]

            coord = []

            for k in range(len(x_cir)):
                coord += [QgsPointXY(float(x_cir[k]), float(y_cir[k]))]

            pol = QgsGeometry.fromPolygonXY([coord + [coord[0]]])
            feat = QgsFeature(Fields)
            feat.setGeometry(pol)
            att = [current+1, str(grupo), mediaX, mediaY, std_X, std_Y, float(R), float(s)]
            feat.setAttributes(att)

            sink.addFeature(feat, QgsFeatureSink.FastInsert)
            if feedback.isCanceled():
                break
            feedback.setProgress(int(current * total))

        feedback.pushInfo(self.tr('Operation completed successfully!', 'Operação finalizada com sucesso!'))
        feedback.pushInfo(self.tr('Leandro Franca - Cartographic Engineer', 'Leandro França - Eng Cart'))

        return {self.OUTPUT: dest_id}
