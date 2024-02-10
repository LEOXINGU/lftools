# -*- coding: utf-8 -*-

"""
Cart_framesFromLines.py
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
__date__ = '2023-08-12'
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

class FramesFromLines(QgsProcessingAlgorithm):

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
        return FramesFromLines()

    def name(self):
        return 'FramesFromLines'.lower()

    def displayName(self):
        return self.tr('Frames from lines', 'Molduras a partir de linhas')

    def group(self):
        return self.tr('Cartography', 'Cartografia')

    def groupId(self):
        return 'cartography'

    def tags(self):
        return self.tr('sequence,frames,molduras,carta,folha,lines,order,ordenar,orientar,polygon,polígono').split(',')

    def icon(self):
        return QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images/cart_frames2.png'))

    txt_en = 'This tool generates frames in the direction of lines, given the measurements of longitudinal distance, transverse distance and overlapping percentage between frames.'
    txt_pt = 'Esta ferramenta gera molduras na direção de linhas, dada as medidas de distância longitudinal, distância transversal e percentual de sobreposição entre os quadros.'
    figure = 'images/tutorial/grid_lines_frames.jpg'

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
    OVERLAP = 'OVERLAP'
    OUTPUT = 'OUTPUT'
    NFRAMES = 'NFRAMES'

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
                type = 1,
                defaultValue = 500,
                minValue = 0
            )
        )

        self.addParameter(
            QgsProcessingParameterNumber(
                self.TRANVERSE,
                self.tr('Transverse distance in meters', 'Distância transversal (metros)'),
                type = 1,
                defaultValue = 250,
                minValue = 0
            )
        )

        self.addParameter(
            QgsProcessingParameterNumber(
                self.OVERLAP,
                self.tr('Overlap between frames (%)', 'Sobreposição entre molduras (%)'),
                type = 1,
                defaultValue = 10,
                minValue = 0,
                maxValue = 99
            )
        )

        self.addParameter(
            QgsProcessingParameterNumber(
                self.NFRAMES,
                self.tr('Number of frames per page', 'Número de molduras por página'),
                type = 0,
                defaultValue = 1,
                minValue = 1
            )
        )

        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT,
                self.tr('Frames', 'Camada de molduras')
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
                     self.tr('page','folha'): QVariant.Int,
                     self.tr('sequence','ordem'): QVariant.Int,
                     }
        for item in itens:
            Fields.append(QgsField(item, itens[item]))

        (sink, dest_id) = self.parameterAsSink(
            parameters,
            self.OUTPUT,
            context,
            Fields,
            QgsWkbTypes.Polygon,
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

        Sobrep = self.parameterAsDouble(
            parameters,
            self.OVERLAP,
            context
        )

        n_frames = self.parameterAsDouble(
            parameters,
            self.NFRAMES,
            context
        )

        Sobrep /= 100
        Yo = distSec/2 - Sobrep*distSec/2 if Sobrep < 0.5 else 0 # distância da primeira moldura
        deltaY = distSec*(1-Sobrep) # intervalo entre as molduras

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

            # Numero de molduras e Distancia para Centro médio
            if Yo < comprimento:
                # Criar lista de pontos e distancias
                ListaDist = [0]
                soma = 0
                for i in range(len(coord)-1):
                    point1 = coord[i]
                    point2 = coord[i+1]
                    m = distancia(point1, point2)
                    soma += m
                    ListaDist += [soma]

                valor = Yo
                dist = []
                while valor < comprimento:
                    dist += [valor]
                    valor += deltaY

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
                        # Pontos extremos do retângulo
                        v1 = array([vetor[1], -1*vetor[0]])
                        v2 = vetor
                        v3 = -1*v1
                        v4 = -1*v2
                        p1 = centro + v1*tamSec/2.0 + v2*distSec/2
                        p2 = centro + v3*tamSec/2.0 + v2*distSec/2
                        p3 = centro + v3*tamSec/2.0 + v4*distSec/2
                        p4 = centro + v1*tamSec/2.0 + v4*distSec/2
                        LIST_COORD += [[[QgsPointXY(float(p1[0]), float(p1[1])),
                                         QgsPointXY(float(p2[0]), float(p2[1])),
                                         QgsPointXY(float(p3[0]), float(p3[1])),
                                         QgsPointXY(float(p4[0]), float(p4[1])),
                                         QgsPointXY(float(p1[0]), float(p1[1]))]]]
                        folha = floor(cont/n_frames) + 1
                        ordem = (cont)%n_frames + 1
                        LIST_ATT += [[feat.id(), int(folha), int(ordem)]]
                        cont += 1
                        if cont == len(dist):
                            break
                    if cont == len(dist):
                        break
            else: # gerar moldura do centro médio
                point1 = array([coord[0].x(), coord[0].y()])
                point2 = array([coord[-1].x(), coord[-1].y()])
                vetor = point2 - point1
                vetor/= norm(vetor)
                centro = 0.5*(point1 + point2)
                # Pontos extremos do retângulo
                v1 = array([vetor[1], -1*vetor[0]])
                v2 = vetor
                v3 = -1*v1
                v4 = -1*v2
                p1 = centro + v1*tamSec/2.0 + v2*distSec/2
                p2 = centro + v3*tamSec/2.0 + v2*distSec/2
                p3 = centro + v3*tamSec/2.0 + v4*distSec/2
                p4 = centro + v1*tamSec/2.0 + v4*distSec/2
                LIST_COORD += [[[QgsPointXY(float(p1[0]), float(p1[1])),
                                 QgsPointXY(float(p2[0]), float(p2[1])),
                                 QgsPointXY(float(p3[0]), float(p3[1])),
                                 QgsPointXY(float(p4[0]), float(p4[1])),
                                 QgsPointXY(float(p1[0]), float(p1[1]))]]]
                LIST_ATT += [[feat.id(), 1, 1]]

            # Salvando as feições
            feature = QgsFeature()
            for index, COORD in enumerate(LIST_COORD):
                geom = QgsGeometry.fromPolygonXY(COORD)
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
