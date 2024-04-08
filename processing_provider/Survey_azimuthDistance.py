# -*- coding: utf-8 -*-

"""
Survey_azimuthDistance.py
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
__date__ = '2021-03-08'
__copyright__ = '(C) 2021, Leandro França'

from PyQt5.QtCore import QCoreApplication, QVariant
from qgis.core import *
import processing
from numpy import sin, cos, modf, radians, sqrt, floor
from lftools.geocapt.imgs import Imgs
from lftools.geocapt.topogeo import *
import os
from qgis.PyQt.QtGui import QIcon


class AzimuthDistance(QgsProcessingAlgorithm):

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
        return AzimuthDistance()

    def name(self):
        return 'azimuthdistance'

    def displayName(self):
        return self.tr('Azimuth and distance', 'Azimute e distância')

    def group(self):
        return self.tr('Survey', 'Agrimensura')

    def groupId(self):
        return 'survey'

    def tags(self):
        return self.tr('survey,agrimensura,azimuth,distance,traverse,analytical,total,station,angle').split(',')

    def icon(self):
        return QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images/total_station.png'))

    txt_en = 'Calculation of points or line from a set of azimuths and distances.'
    txt_pt = 'Cálculo de pontos ou linha a partir de um conjunto de azimutes e distâncias.'
    figure = 'images/tutorial/survey_azimuth_distance.jpg'

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

    POINT = 'POINT'
    AZIMUTHS = 'AZIMUTHS'
    DISTANCES = 'DISTANCES'
    CRS = 'CRS'
    TYPE = 'TYPE'
    CLOSED = 'CLOSED'
    OUTPUT = 'OUTPUT'

    def initAlgorithm(self, config=None):

        self.addParameter(
            QgsProcessingParameterPoint(
                self.POINT,
                self.tr('Origin Point Coordinates', 'Coordenadas do ponto inicial'),
                defaultValue = QgsPointXY(0.0, 0.0)
            )
        )

        self.addParameter(
            QgsProcessingParameterString(
                self.DISTANCES,
                self.tr('List of Horizontal Distances', 'Lista de Distâncias Horizontais'),
                defaultValue = '41.33, 50.21, 23.71, 36.75',
                multiLine = True
            )
        )

        self.addParameter(
            QgsProcessingParameterString(
                self.AZIMUTHS,
                self.tr('List of Azimuths','Lista de Azimutes'),
                defaultValue = '''34°12'43.2", 82°51'08.9", 132°26'44.7", 35°08'47.1" ''',
                multiLine = True
            )
        )

        self.addParameter(
            QgsProcessingParameterCrs(
                self.CRS,
                self.tr('CRS', 'SRC'),
                'ProjectCrs'
            )
        )

        self.addParameter(
            QgsProcessingParameterEnum(
                self.TYPE,
                self.tr('Output geometry type', 'Tipo de geometria de saída'),
				options = [self.tr('Point', 'Ponto'), self.tr('Line', 'Linha')],
                defaultValue= 1
            )
        )

        self.addParameter(
            QgsProcessingParameterBoolean(
                self.CLOSED,
                self.tr('Solve misclosure', 'Resolva o erro de fechamento'),
                defaultValue = False
            )
        )

        # OUTPUT
        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT,
                self.tr('Output layer', 'Camada de saída')
            )
        )

    def processAlgorithm(self, parameters, context, feedback):

        ponto = self.parameterAsPoint(
            parameters,
            self.POINT,
            context
        )

        distances = self.parameterAsString(
            parameters,
            self.DISTANCES,
            context
        )

        Azims = self.parameterAsString(
            parameters,
            self.AZIMUTHS,
            context
        )

        distances = String2NumberList(distances)
        Azims = String2StringList(Azims)
        if len(distances) !=  len(Azims):
            raise QgsProcessingException(self.tr('The number of measured distances must be equal to the number of azimuths!', 'O número de distâncias medidas deve ser igual ao número de azimutes!'))
        tam = len(distances)

        CRS = self.parameterAsCrs(
            parameters,
            self.CRS,
            context
        )

        if CRS.isGeographic():
            raise QgsProcessingException(self.tr('The output CRS must be Projected!', 'O SRC da camada de saída deve ser Projetado!'))

        pnts = [ponto]

        for k in range(tam):
            dx = distances[k]*cos(radians(90 - dms2dd(Azims[k])))
            dy = distances[k]*sin(radians(90 - dms2dd(Azims[k])))
            x = pnts[-1].x() + dx
            y = pnts[-1].y() + dy
            pnts += [QgsPointXY(x, y)]

        tipo = self.parameterAsEnum(
            parameters,
            self.TYPE,
            context
        )

        fechamento = self.parameterAsBool(
            parameters,
            self.CLOSED,
            context
        )

        if fechamento:
            # Calcular Distâncias
            DIST = []
            soma = 0
            Deltas_E = []
            Deltas_N = []
            for k in range(len(pnts)-1):
                deltaE = pnts[k+1].x()-pnts[k].x()
                Deltas_E += [deltaE]
                deltaN = pnts[k+1].y()-pnts[k].y()
                Deltas_N += [deltaN]
                dist = sqrt((deltaE)**2 + (deltaN)**2)
                DIST += [dist]
                soma += dist
            # Calcular erro por comprimento
            dE = (pnts[-1].x() - pnts[0].x())
            dN = (pnts[-1].y() - pnts[0].y())
            Erro = sqrt(dE**2 + dN**2)
            feedback.pushInfo(self.tr('Misclosure error: {} m', 'Erro de fechamento: {} m').format(round(Erro,3)))
            dE /= soma
            dN /= soma

            # Novas coordenadas
            p0 = pnts[0]
            for k in range(1, len(pnts)):
                p0 = QgsPointXY(p0.x() + Deltas_E[k-1] - dE*DIST[k-1], p0.y() + Deltas_N[k-1] - dN*DIST[k-1])
                pnts[k] = p0
            pnts[-1] = pnts[0]

        # Camada de Saída
        if tipo == 0:
            GeomType = QgsWkbTypes.Point
        elif tipo == 1:
            GeomType = QgsWkbTypes.LineString

        Fields = QgsFields()
        itens  = {
                     'id' : QVariant.Int,
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

        # Criar pontos ajustados
        if tipo == 0:
            for k, pnt in enumerate(pnts):
                geom = QgsGeometry.fromPointXY(pnt)
                feat = QgsFeature(Fields)
                feat.setGeometry(geom)
                feat.setAttributes([k])
                sink.addFeature(feat, QgsFeatureSink.FastInsert)
                if feedback.isCanceled():
                    break
        elif tipo == 1:
            geom = QgsGeometry.fromPolylineXY(pnts)
            feat = QgsFeature(Fields)
            feat.setGeometry(geom)
            sink.addFeature(feat, QgsFeatureSink.FastInsert)

        feedback.pushInfo(self.tr('Operation completed successfully!', 'Operação finalizada com sucesso!'))
        feedback.pushInfo(self.tr('Leandro Franca - Cartographic Engineer', 'Leandro França - Eng Cart'))

        return {self.OUTPUT: dest_id}
