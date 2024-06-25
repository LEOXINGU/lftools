# -*- coding: utf-8 -*-

"""
Vect_PointsToPolygon.py
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
__date__ = '2023-01-21'
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
from lftools.translations.translate import translate
import os
from qgis.PyQt.QtGui import QIcon

class PointsToPolygon(QgsProcessingAlgorithm):

    LOC = QgsApplication.locale()[:2]

    def tr(self, *string):
        return translate(string, self.LOC)

    def createInstance(self):
        return PointsToPolygon()

    def name(self):
        return 'pointstopolygon'

    def displayName(self):
        return self.tr('Points to polygon', 'Pontos para polígono')

    def group(self):
        return self.tr('Vector', 'Vetor')

    def groupId(self):
        return 'vector'

    def tags(self):
        return self.tr('sequence,points,pontos,order,ordenar,orientar,polygon,polígono').split(',')

    def icon(self):
        return QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images/vetor.png'))

    txt_en = 'This tool generates a polygon layer from a point layer and its filled order (sequence) attributes.'
    txt_pt = 'Esta ferramenta gera uma camada de polígono a partir de uma camada de pontos e seus atributos de ordem (sequência) preenchidos.'
    figure = 'images/tutorial/vect_point2polygon.jpg'

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

    POINTS = 'POINTS'
    FIELD = 'FIELD'
    POLYGON = 'POLYGON'

    def initAlgorithm(self, config=None):
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.POINTS,
                self.tr('Point layer', 'Camada de pontos'),
                [QgsProcessing.TypeVectorPoint]
            )
        )

        self.addParameter(
            QgsProcessingParameterField(
                self.FIELD,
                self.tr('Sequence Field', 'Campo de ordenação'),
                parentLayerParameterName=self.POINTS,
                type = QgsProcessingParameterField.Numeric
            )
        )

        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.POLYGON,
                self.tr('Polygon from points', 'Polígono a partir de pontos')
            )
        )

    def processAlgorithm(self, parameters, context, feedback):

        layer = self.parameterAsSource(
            parameters,
            self.POINTS,
            context
        )
        if layer is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.POINTS))


        campo = self.parameterAsFields(
            parameters,
            self.FIELD,
            context
        )
        if campo is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.FIELD))

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
            QgsWkbTypes.PolygonZ if layer.wkbType() != 1 else QgsWkbTypes.Polygon,
            layer.sourceCrs()
        )
        if sink is None:
            raise QgsProcessingException(self.invalidSinkError(parameters, self.ANGLES))

        # Validando atributos dos dados de entrada
        feedback.pushInfo(self.tr('Validating layer attributes...', 'Validando atributos das camadas...' ))
        # ponto_limite
        ordem_list = list(range(1,layer.featureCount()+1))
        ordem_comp = []
        for feat in layer.getFeatures():
            if feat[campo[0]] > 0:
                ordem_comp += [feat[campo[0]]]
            else:
                raise QgsProcessingException(self.tr('All attributes of the order field (sequence) must be greater than zero and not null!', 'Todos atributos do campo ordem (sequência) devem ser maiores que zero e não nulos!'))
        ordem_comp.sort()
        if ordem_list != ordem_comp:
            raise QgsProcessingException(self.tr('The point sequence field must be filled in correctly!', 'O campo de sequência dos pontos deve preenchido corretamente!'))

        # Pegar coordenadas dos pontos
        pontos = {}
        for feat in layer.getFeatures():
            geom = feat.geometry()
            pnt = geom.constGet()
            pontos[feat[campo[0]]] = QgsPoint(pnt.x(), pnt.y(), pnt.z()) if layer.wkbType() != 1 else QgsPointXY(pnt.x(), pnt.y())

        # Gerar polígono:
        COORDS = []
        for ordem in ordem_list:
            COORDS += [pontos[ordem]]
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
