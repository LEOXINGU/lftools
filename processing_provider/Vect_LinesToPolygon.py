# -*- coding: utf-8 -*-

"""
Vect_LinesToPolygon.py
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
from qgis.PyQt.QtGui import QIcon
from lftools.geocapt.cartography import geom2PointList

class LinesToPolygon(QgsProcessingAlgorithm):

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
        return LinesToPolygon()

    def name(self):
        return 'linestopolygon'

    def displayName(self):
        return self.tr('Lines to polygon', 'Linhas para polígono')

    def group(self):
        return self.tr('Vector', 'Vetor')

    def groupId(self):
        return 'vector'

    def tags(self):
        return self.tr('sequence,lines,order,ordenar,orientar,polygon,polígono').split(',')

    def icon(self):
        return QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images/vetor.png'))

    txt_en = 'This tool generates a polygon layer from a connected line layer.'
    txt_pt = 'Esta ferramenta gera uma camada de polígono a partir de uma camada de linhas conectadas.'
    figure = 'images/tutorial/vect_lines2polygon.jpg'

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
    POLYGON = 'POLYGON'

    def initAlgorithm(self, config=None):
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.LINES,
                self.tr('Lines layer (connected)', 'Camada de linhas conectadas'),
                [QgsProcessing.TypeVectorLine]
            )
        )

        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.POLYGON,
                self.tr('Polygon from lines', 'Polígono a partir de linhas')
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

        # OUTPUT
        Fields = QgsFields()

        itens  = {
                     'id' : QVariant.Int,
                     }
        for item in itens:
            Fields.append(QgsField(item, itens[item]))

        (sink, dest_id) = self.parameterAsSink(
            parameters,
            self.POLYGON,
            context,
            Fields,
            QgsWkbTypes.PolygonZ if layer.wkbType() not in (2,5) else QgsWkbTypes.Polygon,
            layer.sourceCrs()
        )
        if sink is None:
            raise QgsProcessingException(self.invalidSinkError(parameters, self.POLYGON))

        # Sequencia de Linhas
        linhas = {}
        for featA in layer.getFeatures():
            mont = None
            jus = None
            geomA = featA.geometry()
            if geomA.isMultipart():
                coordsA = geomA.asMultiPolyline()[0]
                coords = geom2PointList(geomA)[0]
            else:
                coordsA = geomA.asPolyline()
                coords = geom2PointList(geomA)
            pnt_iniA = QgsGeometry().fromPointXY(coordsA[0])
            pnt_fimA = QgsGeometry().fromPointXY(coordsA[-1])

            for featB in layer.getFeatures():
                geomB = featB.geometry()
                if geomB.isMultipart():
                    coordsB = geomB.asMultiPolyline()[0]
                else:
                    coordsB = geomB.asPolyline()
                pnt_iniB = QgsGeometry().fromPointXY(coordsB[0])
                pnt_fimB = QgsGeometry().fromPointXY(coordsB[-1])

                if pnt_iniA.intersects(pnt_fimB):
                    mont = featB.id()
                elif pnt_fimA.intersects(pnt_iniB):
                    jus = featB.id()

                if mont != None and jus != None:
                    break

            linhas[featA.id()] = {'mont': mont, 'jus': jus, 'coords': coords}

        # Validando atributos dos dados de entrada
        feedback.pushInfo(self.tr('Validating connected features...', 'Validando feições conectadas...' ))
        sentinela = False
        for linha in linhas:
            if linhas[linha]['mont'] == None:
                pnt = linhas[linha]['coords'][0]
                sentinela = True
            if linhas[linha]['jus'] == None:
                pnt = linhas[linha]['coords'][-1]
                sentinela = True
            if sentinela:
                raise QgsProcessingException(self.tr('Unconnected line at coordinate point ({} , {})!'.format(pnt.x(), pnt.y()),
                                                 'Linha não conectada no ponto de coordenadas ({} , {})!'.format(pnt.x(), pnt.y())))

        # ID da primeira feição
        for feat in layer.getFeatures():
            seq = [feat.id()]
            COORDS = linhas[feat.id()]['coords'][:-1]
            proximo = linhas[feat.id()]['jus']
            break

        for k in range(len(linhas)-1):
            seq += [proximo]
            COORDS += linhas[proximo]['coords'][:-1]
            proximo = linhas[proximo]['jus']

        COORDS = COORDS + [COORDS[0]]
        anel = QgsLineString(COORDS)
        pol = QgsPolygon(anel)
        Poligono = QgsGeometry(pol)

        feature = QgsFeature()
        feature.setGeometry(Poligono)
        feature.setAttributes([1])
        sink.addFeature(feature, QgsFeatureSink.FastInsert)

        feedback.pushInfo(self.tr('Operation completed successfully!', 'Operação finalizada com sucesso!'))
        feedback.pushInfo(self.tr('Leandro Franca - Cartographic Engineer', 'Leandro França - Eng Cart'))

        return {self.POLYGON: dest_id}
