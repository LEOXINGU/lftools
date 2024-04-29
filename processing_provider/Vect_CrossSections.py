# -*- coding: utf-8 -*-

"""
Vect_CrossSections.py
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
__date__ = '2023-08-22'
__copyright__ = '(C) 2023, Leandro França'

from qgis.PyQt.QtCore import QCoreApplication, QVariant
from qgis.core import (QgsApplication,
                       QgsProcessingParameterFeatureSource,
                       QgsGeometry,
                       QgsFeature,
                       QgsProcessing,
                       QgsProject,
                       QgsFields,
                       QgsField,
                       QgsWkbTypes,
                       QgsLineString,
                       QgsPolygon,
                       QgsPoint,
                       QgsPointXY,
                       QgsProcessingParameterField,
                       QgsProcessingParameterEnum,
                       QgsProcessingParameterBoolean,
                       QgsProcessingParameterNumber,
                       QgsFeatureSink,
                       QgsProcessingException,
                       QgsProcessingAlgorithm,
                       QgsCoordinateTransform,
                       QgsProcessingParameterFeatureSink)
from lftools.geocapt.imgs import Imgs
import os
from numpy import array, arange, sqrt, floor, ceil
from numpy.linalg import norm
from qgis.PyQt.QtGui import QIcon
from lftools.geocapt.cartography import geom2PointList

class CrossSections(QgsProcessingAlgorithm):

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
        return CrossSections()

    def name(self):
        return 'CrossSections'.lower()

    def displayName(self):
        return self.tr('Cross Sections', 'Seções transversais')

    def group(self):
        return self.tr('Vector', 'Vetor')

    def groupId(self):
        return 'vector'

    def tags(self):
        return self.tr('cross,section,seção,transversal,paralela,roads,topography,lines,profile,perfil,longitudinal,order,ordenar,hidrography,drenagem,channels,canais').split(',')

    def icon(self):
        return QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images/vetor.png'))

    txt_en = 'Generates cross sections from a line-type layer.'
    txt_pt = 'Gera seções transversais a partir de uma camada do tipo linha.'
    figure = 'images/tutorial/vect_cross_sections.jpg'

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
    LONGITUDINAL = 'LONGITUDINAL'
    TRANVERSE = 'TRANVERSE'
    OUTPUT = 'OUTPUT'

    def initAlgorithm(self, config=None):
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.LINES,
                self.tr('Line layer', 'Camada de linhas'),
                [QgsProcessing.TypeVectorLine]
            )
        )

        self.addParameter(
            QgsProcessingParameterNumber(
                self.LONGITUDINAL,
                self.tr('Longitudinal distance in meters', 'Distância longitudinal (metros)'),
                type = QgsProcessingParameterNumber.Type.Double,
                defaultValue = 50,
                minValue = 0
            )
        )

        self.addParameter(
            QgsProcessingParameterNumber(
                self.TRANVERSE,
                self.tr('Transverse distance in meters', 'Distância transversal (metros)'),
                type = QgsProcessingParameterNumber.Type.Double,
                defaultValue = 150,
                minValue = 0
            )
        )

        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT,
                self.tr('Cross sections', 'Seções Transversais')
            )
        )

    def processAlgorithm(self, parameters, context, feedback):

        layer = self.parameterAsSource(
            parameters,
            self.LINES,
            context
        )
        if layer is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.LINES))
        SRC = layer.sourceCrs()

        # OUTPUT
        Fields = QgsFields()

        itens  = {
                     self.tr('feat_id'): QVariant.Int,
                     self.tr('sequence','ordem'): QVariant.Int,
                     }
        for item in itens:
            Fields.append(QgsField(item, itens[item]))

        (sink, dest_id) = self.parameterAsSink(
            parameters,
            self.OUTPUT,
            context,
            Fields,
            QgsWkbTypes.LineString,
            SRC
        )
        if sink is None:
            raise QgsProcessingException(self.invalidSinkError(parameters, self.OUTPUT))

        distSec = self.parameterAsDouble(
            parameters,
            self.LONGITUDINAL,
            context
        )

        tamSec = self.parameterAsDouble(
            parameters,
            self.TRANVERSE,
            context
        )

        # Se a camada de linhas for Geográfica, obter medidas em graus decimais
        if SRC.isGeographic():
            distSec /= 111000
            tamSec /= 111000

        def distancia(P1, P2):
            return sqrt((P1.x() - P2.x())**2 + (P1.y() - P2.y())**2)

        Percent = 100.0/layer.featureCount() if layer.featureCount()>0 else 0
        for current, feat in enumerate(layer.getFeatures()):
            geom = feat.geometry()
            comprimento = geom.length()
            coord = geom.asPolyline()
            LIST_COORD = []
            LIST_ATT = []
            # Criar lista de pontos e distancias
            ListaDist = [0]
            soma = 0
            for i in range(len(coord)-1):
                point1 = coord[i]
                point2 = coord[i+1]
                m = distancia(point1, point2)
                soma += m
                ListaDist += [soma]
            # Numero de Secoes e Nova Distancia
            if distSec < comprimento:
                NumSec = floor(comprimento/distSec)
                DistSecNova = comprimento/NumSec
                dist = arange(0, comprimento+DistSecNova, DistSecNova)
            else:
                NumSec, DistSecNova = 1, comprimento
                dist = arange(0, comprimento+DistSecNova, DistSecNova)
            # Algoritmo para pegar secoes transversais
            cont = 0
            for k in range(len(coord)-1):
                while ListaDist[k] <= dist[cont] and dist[cont] < ListaDist[k+1]:
                    point1 = array([coord[k].x(), coord[k].y()])
                    point2 = array([coord[k+1].x(), coord[k+1].y()])
                    vetor = point2 - point1
                    vetor/= norm(vetor)
                    MultDist = dist[cont]-ListaDist[k]
                    centro = point1 + vetor*MultDist
                    # Aqui pode ser criado o perfil do terreno...
                    # Pontos extremos de cada secao
                    p1 = centro + array([vetor[1], -1*vetor[0]])*tamSec/2.0
                    p2 = centro + array([-1*vetor[1], vetor[0]])*tamSec/2.0
                    LIST_COORD += [[QgsPointXY(float(p1[0]), float(p1[1])),
                                    QgsPointXY(float(centro[0]), float(centro[1])),
                                    QgsPointXY(float(p2[0]), float(p2[1]))]]
                    cont +=1
                    LIST_ATT += [[feat.id(), cont]]
                    if cont == NumSec +1:
                        break
                if cont == NumSec +1:
                    break
            # Ultima secao
            cont +=1
            point1 = array([coord[-2].x(), coord[-2].y()])
            point2 = array([coord[-1].x(), coord[-1].y()])
            vetor = point2 - point1
            vetor/= norm(vetor)
            centro = array([coord[-1].x(), coord[-1].y()])
            p1 = centro + array([vetor[1], -1*vetor[0]])*tamSec/2.0
            p2 = centro + array([-1*vetor[1], vetor[0]])*tamSec/2.0
            LIST_COORD += [[QgsPointXY(float(p1[0]), float(p1[1])),
                            QgsPointXY(float(centro[0]), float(centro[1])),
                            QgsPointXY(float(p2[0]), float(p2[1]))]]
            LIST_ATT += [[feat.id(), cont]]

            # Salvando as feições
            feature = QgsFeature()
            for index, COORD in enumerate(LIST_COORD):
                geom = QgsGeometry.fromPolylineXY(COORD)
                att = LIST_ATT[index]
                feature.setGeometry(geom)
                feature.setAttributes(att)
                sink.addFeature(feature, QgsFeatureSink.FastInsert)

            if feedback.isCanceled():
                break
            feedback.setProgress(int((current+1) * Percent))

        feedback.pushInfo(self.tr('Operation completed successfully!', 'Operação finalizada com sucesso!'))
        feedback.pushInfo(self.tr('Leandro Franca - Cartographic Engineer', 'Leandro França - Eng Cart'))

        return {self.OUTPUT: dest_id}
