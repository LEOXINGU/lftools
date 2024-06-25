# -*- coding: utf-8 -*-

"""
Vect_Overlapping.py
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
__date__ = '2023-05-14'
__copyright__ = '(C) 2023, Leandro França'

from qgis.PyQt.QtCore import QCoreApplication, QVariant
from qgis.core import (QgsApplication,
                       QgsGeometry,
                       QgsWkbTypes,
                       QgsFeature,
                       QgsField,
                       QgsFields,
                       QgsProcessing,
                       QgsSpatialIndex,
                       QgsFeatureRequest,
                       QgsProcessingParameterField,
                       QgsProcessingParameterEnum,
                       QgsProcessingParameterBoolean,
                       QgsProcessingParameterNumber,
                       QgsFeatureSink,
                       QgsProcessingException,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterFeatureSink)
from lftools.geocapt.imgs import Imgs
from lftools.translations.translate import translate
from lftools.geocapt.cartography import OrientarPoligono
import numpy as np
import os
from qgis.PyQt.QtGui import QIcon

class Overlapping(QgsProcessingAlgorithm):

    LOC = QgsApplication.locale()[:2]

    def tr(self, *string):
        return translate(string, self.LOC)

    def createInstance(self):
        return Overlapping()

    def name(self):
        return 'overlapping'

    def displayName(self):
        return self.tr('Overlapping polygons', 'Sobreposição de polígonos')

    def group(self):
        return self.tr('Vector', 'Vetor')

    def groupId(self):
        return 'vector'

    def tags(self):
        return self.tr('cadastro,parcela,sequence,confrontante,vizinho,neighbours,sobreposição,overlap,cadastre,borderer,loteamento').split(',')

    def icon(self):
        return QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images/vetor.png'))

    txt_en = '''Identifies the overlap between features of a polygon type layer.'''
    txt_pt = '''Identifica a sobreposição entre feições de uma camada do tipo polígono.'''
    figure = 'images/tutorial/vect_overlapping.jpg'

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
    OUTPUT = 'OUTPUT'

    def initAlgorithm(self, config = None):
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT,
                self.tr('Polygon layer', 'Camada de polígonos'),
                [QgsProcessing.TypeVectorPolygon]
            )
        )

        # OUTPUT
        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT,
                self.tr('Overlapping', 'Sobreposição')
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


        # Camada de Saída
        Fields = QgsFields()
        itens  = {
                     'ID1' : QVariant.Int,
                     'ID2' : QVariant.Int,
                     }
        for item in itens:
            Fields.append(QgsField(item, itens[item]))
        (sink, dest_id) = self.parameterAsSink(
            parameters,
            self.OUTPUT,
            context,
            Fields,
            QgsWkbTypes.Polygon,
            layer.sourceCrs()
        )
        if sink is None:
            raise QgsProcessingException(self.invalidSinkError(parameters, self.OUTPUT))

        # Validar:
        # não pode ser multipolígono
        for feat in layer.getFeatures():
            if feat.geometry().isMultipart():
                raise QgsProcessingException(self.tr('Feature id {} is multipart! Multipart features are not allowed!', 'Feição de id {} é multiparte! Feições multipartes não são permitidas!' ).format(feat.id()))

        feedback.pushInfo(self.tr('Creating spatial index...', 'Criando índice espacial...'))

        index = QgsSpatialIndex(layer.getFeatures())

        sobreposicoes = []
        feedback.pushInfo(self.tr('Identifying overlapping polygons...', 'Idenficando sobreposição entre polígonos...'))
        total = 100.0 / layer.featureCount() if layer.featureCount() else 0

        for current, feat1 in enumerate(layer.getFeatures()):
            ID1 = feat1.id()
            geom1 = feat1.geometry()
            linha1 = QgsGeometry.fromPolylineXY(geom1.asPolygon()[0])
            bbox1 = geom1.boundingBox()
            feat_ids = index.intersects(bbox1)
            for feat2 in layer.getFeatures(QgsFeatureRequest(feat_ids)):
                ID2 = feat2.id()
                if ID1 != ID2 and (ID2,ID1) not in sobreposicoes:
                    geom2 = feat2.geometry()
                    if geom1.intersects(geom2):
                        inter = geom1.intersection(geom2)
                        for item in inter.asGeometryCollection():
                            if item.type() == 2: #polygon
                                sobreposicoes += [(ID1, ID2)]
                                if item.isMultipart():
                                    coords = item.asMultiPolygon()
                                    for coord in coords:
                                        feature = QgsFeature(Fields)
                                        feature.setGeometry(QgsGeometry.fromPolygonXY(coord))
                                        feature.setAttributes([ID1, ID2])
                                        sink.addFeature(feature, QgsFeatureSink.FastInsert)
                                else:
                                    feature = QgsFeature(Fields)
                                    feature.setGeometry(item)
                                    feature.setAttributes([ID1, ID2])
                                    sink.addFeature(feature, QgsFeatureSink.FastInsert)
            if feedback.isCanceled():
                break
            feedback.setProgress(int((current+1) * total))

        feedback.pushInfo(self.tr('Operation completed successfully!', 'Operação finalizada com sucesso!'))
        feedback.pushInfo(self.tr('Leandro Franca - Cartographic Engineer', 'Leandro França - Eng Cart'))

        return {self.OUTPUT: dest_id}
