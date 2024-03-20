# -*- coding: utf-8 -*-


"""
Vect_ExtendLines.py
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
__date__ = '2021-02-14'
__copyright__ = '(C) 2021, Leandro França'

from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (QgsApplication,
                       QgsProcessingParameterVectorLayer,
                       QgsGeometry,
                       QgsPointXY,
                       QgsFeature,
                       QgsProcessing,
                       QgsProcessingParameterField,
                       QgsProcessingParameterBoolean,
                       QgsProcessingParameterEnum,
                       QgsProcessingParameterNumber,
                       QgsFeatureSink,
                       QgsProcessingException,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterFeatureSink)
from numpy import array
import numpy as np
from numpy.linalg import norm
from pyproj.crs import CRS
from lftools.geocapt.imgs import Imgs
import os
from qgis.PyQt.QtGui import QIcon

class ExtendLines(QgsProcessingAlgorithm):

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
        return ExtendLines()

    def name(self):
        return 'extendlines'

    def displayName(self):
        return self.tr('Extend lines', 'Estender linhas')

    def group(self):
        return self.tr('Vector', 'Vetor')

    def groupId(self):
        return 'vector'

    def tags(self):
        return self.tr('extend,cross,increase,segment,line,vector').split(',')

    def icon(self):
        return QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images/vetor.png'))

    txt_en = 'Extends lines at their <b>start</b> and/or <b>end</b> points.'
    txt_pt = 'Estende linhas nos seus pontos inicial e/ou final.'
    figure = 'images/tutorial/vect_extend_lines.jpg'

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


    LINES = 'LINES'
    TYPE = 'TYPE'
    DISTANCE = 'DISTANCE'
    OUTPUT = 'OUTPUT'

    def initAlgorithm(self, config=None):

        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.LINES,
                self.tr('Line Layer', 'Camada de Linhas'),
                [QgsProcessing.TypeVectorLine]
            )
        )

        tipo = [self.tr('Start and End points','Pontos inicial e final'),
                self.tr('Only End Point','Apenas ponto final'),
                self.tr('Only Start Point','Apenas ponto inicial')
               ]

        self.addParameter(
            QgsProcessingParameterEnum(
                self.TYPE,
                self.tr('Attributes', 'Atributos'),
				options = tipo,
                defaultValue= 0
            )
        )

        self.addParameter(
            QgsProcessingParameterNumber(
                self.DISTANCE,
                self.tr('Distance (m)', 'Distância (m)'),
                type = QgsProcessingParameterNumber.Type.Double,
                defaultValue = 25.0
                )
            )

        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT,
                self.tr('Extended lines', 'Linhas estendidas')
            )
        )


    def processAlgorithm(self, parameters, context, feedback):

        linhas = self.parameterAsSource(
            parameters,
            self.LINES,
            context
        )
        if linhas is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.LINES))


        tipo = self.parameterAsEnum(
            parameters,
            self.TYPE,
            context
        )

        Distancia = self.parameterAsDouble(
            parameters,
            self.DISTANCE,
            context
        )
        if Distancia is None or Distancia < 0:
            raise QgsProcessingException(self.tr('The input distance must be grater than 0!', 'A distância de entrada deve ser maior que 0!'))


        (sink, dest_id) = self.parameterAsSink(
            parameters,
            self.OUTPUT,
            context,
            linhas.fields(),
            linhas.wkbType(),
            linhas.sourceCrs()
        )
        if sink is None:
            raise QgsProcessingException(self.invalidSinkError(parameters, self.OUTPUT))

        # Camada de entrada
        SRC = linhas.sourceCrs()
        fields = linhas.fields()
        extensao = linhas.sourceExtent()
        y_max = extensao.yMaximum()
        y_min = extensao.yMinimum()

        # Transformar distancia para graus, se o SRC for Geográfico
        if SRC.isGeographic():
            EPSG = int(SRC.authid().split(':')[-1])
            proj_crs = CRS.from_epsg(EPSG)
            a=proj_crs.ellipsoid.semi_major_metre
            f=1/proj_crs.ellipsoid.inverse_flattening
            e2 = f*(2-f)
            N = a/np.sqrt(1-e2*(np.sin((y_min+y_max)/2))**2) # Raio de curvatura 1º vertical
            M = a*(1-e2)/(1-e2*(np.sin((y_min+y_max)/2))**2)**(3/2.) # Raio de curvatura meridiana
            R = np.sqrt(M*N) # Raio médio de Gauss
            theta = Distancia/R
            Distancia = np.degrees(theta) # Radianos para graus

        # Varrer linhas
        Percent = 100.0/linhas.featureCount() if linhas.featureCount()>0 else 0
        for index, feat in enumerate(linhas.getFeatures()):
            geom = feat.geometry()
            att = feat.attributes()
            if geom:
                if geom.isMultipart():
                    lines = geom.asMultiPolyline()
                    for line in lines:
                        P1 = line[0]
                        P2 = line[1]
                        Pn = line[-1]
                        Pn_1 = line[-2]
                        P_ini =  QgsGeometry.fromPointXY(P1)
                        P_fim =  QgsGeometry.fromPointXY(Pn)
                        if tipo == 0 or tipo == 2:
                            vetor = array(P1) - array(P2)
                            P = array(P1) + vetor/norm(vetor)*Distancia
                            P1 = QgsPointXY(P[0], P[1])
                        if tipo == 0 or tipo == 1:
                            vetor = array(Pn) - array(Pn_1)
                            P = array(Pn) + vetor/norm(vetor)*Distancia
                            Pn = QgsPointXY(P[0], P[1])
                        if tipo == 0:
                            line = [P1] + line[1:-1] + [Pn]
                        elif tipo == 1:
                            line = line[0:-1] + [Pn]
                        elif tipo == 2:
                            line = [P1] + line[1:]
                        new_geom = QgsGeometry.fromPolylineXY(line)
                        feature = QgsFeature(fields)
                        feature.setAttributes(att)
                        feature.setGeometry(new_geom)
                        sink.addFeature(feature, QgsFeatureSink.FastInsert)
                else:
                    line = geom.asPolyline()
                    P1 = line[0]
                    P2 = line[1]
                    Pn = line[-1]
                    Pn_1 = line[-2]
                    P_ini =  QgsGeometry.fromPointXY(P1)
                    P_fim =  QgsGeometry.fromPointXY(Pn)
                    if tipo == 0 or tipo == 2:
                        vetor = array(P1) - array(P2)
                        P = array(P1) + vetor/norm(vetor)*Distancia
                        P1 = QgsPointXY(P[0], P[1])
                    if tipo == 0 or tipo == 1:
                        vetor = array(Pn) - array(Pn_1)
                        P = array(Pn) + vetor/norm(vetor)*Distancia
                        Pn = QgsPointXY(P[0], P[1])
                    if tipo == 0:
                        line = [P1] + line[1:-1] + [Pn]
                    elif tipo == 1:
                        line = line[0:-1] + [Pn]
                    elif tipo == 2:
                        line = [P1] + line[1:]
                    new_geom = QgsGeometry.fromPolylineXY(line)
                    feature = QgsFeature(fields)
                    feature.setAttributes(att)
                    feature.setGeometry(new_geom)
                    sink.addFeature(feature, QgsFeatureSink.FastInsert)
            if feedback.isCanceled():
                break
            feedback.setProgress(int((index+1) * Percent))

        feedback.pushInfo(self.tr('Operation completed successfully!', 'Operação finalizada com sucesso!'))
        feedback.pushInfo(self.tr('Leandro Franca - Cartographic Engineer', 'Leandro França - Eng Cart'))

        return {self.OUTPUT: dest_id}
