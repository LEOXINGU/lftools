# -*- coding: utf-8 -*-

"""
Stat_stdDevEllipse.py
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
__date__ = '2020-08-22'
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


class ConfidenceEllipse(QgsProcessingAlgorithm):

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
        return ConfidenceEllipse()

    def name(self):
        return 'confidenceellipse'

    def displayName(self):
        return self.tr('Confidence ellipses', 'Elipses de confiança')

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
        return self.tr('ellipse,elipse,confidence,deviational,standard,tendency,dispertion,directional,trend,confidence,covariance,mvc').split(',')

    def icon(self):
        return QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images/statistics.png'))

    txt_en = 'Creates ellipses based on the covariance matrix to summarize the spatial characteristics of point type geographic features: central tendency, dispersion, and directional trends.'
    txt_pt = 'Cria elipses a partir da matriz variância-covariância para resumir as características espaciais de feções geográficas do tipo ponto: tendência central, dispersão e tendências direcionais.'
    figure = 'images/tutorial/stat_ellipses.jpg'

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

        tipos = [self.tr('68% Confidence Ellipse', 'Elipse com 68% de confiança'),
                 self.tr('90% Confidence Ellipse', 'Elipse com 90% de confiança'),
                 self.tr('95% Confidence Ellipse', 'Elipse com 95% de confiança'),
                 self.tr('99% Confidence Ellipse', 'Elipse com 99% de confiança')]

        self.addParameter(
            QgsProcessingParameterEnum(
                self.TAM,
                self.tr('Size', 'Tamanho'),
				options = tipos,
                defaultValue= 1
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

        self.addParameter(
            QgsProcessingParameterField(
                self.CAMPO_AGRUPAR,
                self.tr('Group Field', 'Campo de Agrupamento'),
                parentLayerParameterName=self.INPUT,
                type=QgsProcessingParameterField.Any,
                optional=True
            )
        )

        # OUTPUT
        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT,
                self.tr('Standard Deviational Ellipse(s)', 'Elipse(s) de Distribuição')
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
        porcent = [0.68, 0.90, 0.95, 0.99]
        confidence = porcent[size]
        # size = chi2.ppf(confidence, 2)
        size = [2.27886856637673, 4.605170185988092, 5.991464547107979, 9.21034037197618][size]

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
             self.tr('confidence','confiança'): QVariant.Double,
             self.tr('rotation','rotação'): QVariant.Double,
             'major_axis': QVariant.Double,
             'minor_axis': QVariant.Double
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
                    MVC = np.cov(x,y, fweights = w)
                    mediaX = float(np.average(x, weights = w))
                    mediaY = float(np.average(y, weights = w))
                    std_X = float(np.sqrt(np.average((x-mediaX)**2, weights = w)))
                    std_Y = float(np.sqrt(np.average((y-mediaY)**2, weights = w)))
                else:
                    continue
            else:
                MVC = np.cov(x,y)
                mediaX = float(np.average(x))
                mediaY = float(np.average(y))
                std_X = float(np.std(x))
                std_Y = float(np.std(y))

            σ2x = MVC[0][0]
            σ2y = MVC[1][1]
            σ2xy = MVC[0][1]

            # Elipse de Erro para um determinado desvio-padrão
            # Centro da Elipse
            C=[mediaX, mediaY]
            # Auto valores e autovetores da MVC
            Val, Vet = np.linalg.eig(np.matrix(MVC))
            λ1 = Val[0]
            λ2 = Val[1]
            v1 = np.array(Vet[:,0]).reshape([1,2])
            v2 = np.array(Vet[:,1]).reshape([1,2])

            AtPA = Vet.T*MVC*Vet
            c1 = sqrt(AtPA[1,1]) # para x
            c2 = sqrt(AtPA[0,0]) # para y

            # Construção da Elipse
            p = np.arange(0,2*pi,0.1)
            a = c2 if λ1 > λ2 else c1 # semi eixo maior
            b = c1 if λ1 > λ2 else c2 # semi eixo menor
            # Fator de tamanho
            s = np.sqrt(size) # Distribuição Chi-Square, diferente do ArcGIS - sqrt(2*std**2)
            x_ell = s*a*cos(p)
            y_ell = s*b*sin(p)
            M1 = np.matrix([x_ell, y_ell])

            # Rotacionamento de phi (direção do eixo maior)
            v = v1 if λ1 > λ2 else v2 # vetor do semi-eixo maior
            if v[0][1]>=0:
                phi = np.arccos(np.dot(v,[1,0]))[0] # 1Q e 2Q
            else:
                phi = np.pi - np.arccos(np.dot(v,[1,0]))[0] # 3Q e 4Q

            rot = np.matrix([[cos(phi), -sin(phi)], [sin(phi), cos(phi)]])
            M2 = rot*M1
            X_ell = np.array(M2[0,:]) + C[0]
            Y_ell = np.array(M2[1,:]) + C[1]

            coord = []
            for k in range(len(X_ell[0])):
                coord += [QgsPointXY(float(X_ell[0,k]), float(Y_ell[0,k]))]

            pol = QgsGeometry.fromPolygonXY([coord + [coord[0]]])
            feat = QgsFeature(Fields)
            feat.setGeometry(pol)
            cont = 1
            att = [cont, str(grupo), mediaX, mediaY, std_X,std_Y,
                   confidence, float(np.degrees(phi)),
                   float(np.sqrt(size)*a), float(np.sqrt(size)*b)]
            feat.setAttributes(att)

            sink.addFeature(feat, QgsFeatureSink.FastInsert)
            if feedback.isCanceled():
                break
            feedback.setProgress(int(current * total))

        feedback.pushInfo(self.tr('Operation completed successfully!', 'Operação finalizada com sucesso!'))
        feedback.pushInfo(self.tr('Leandro Franca - Cartographic Engineer', 'Leandro França - Eng Cart'))

        return {self.OUTPUT: dest_id}
