# -*- coding: utf-8 -*-

"""
Vect_ConnectLayers.py
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
                       QgsSpatialIndex,
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

class ConnectLayers(QgsProcessingAlgorithm):

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
        return ConnectLayers()

    def name(self):
        return 'ConnectLayers'.lower()

    def displayName(self):
        return self.tr('Connect layers', 'Conectar camadas')

    def group(self):
        return self.tr('Vector', 'Vetor')

    def groupId(self):
        return 'vector'

    def tags(self):
        return self.tr('conectar,connect,create,vertex,point,topology,topologia,conectividade,connection,connected,polygon,polígono').split(',')

    def icon(self):
        return QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images/vetor.png'))

    txt_en = '''Creates new vertices into polygons to ensure perfect connectivity (topology) between two layers.'''
    txt_pt = '''Gera novos vértices em polígonos para garantir a perfeita conectividade (topologia) entre duas camadas.'''
    figure = 'images/tutorial/vect_connectLayers.jpg'

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

    POLYGONS = 'POLYGONS'
    LAYER = 'LAYER'
    TOLERANCE = 'TOLERANCE'
    OUTPUT = 'OUTPUT'

    def initAlgorithm(self, config=None):
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.POLYGONS,
                self.tr('Polygons', 'Polígonos'),
                [QgsProcessing.TypeVectorPolygon]
            )
        )

        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.LAYER,
                self.tr('Reference layer', 'Camada de referência'),
                [QgsProcessing.TypeVectorAnyGeometry]
            )
        )

        self.addParameter(
            QgsProcessingParameterNumber(
                self.TOLERANCE,
                self.tr('Tolerance for snapping in meters', 'Tolerância para a aderência (metros)'),
                type = 1,
                defaultValue = 0.1,
                minValue = 0.001
            )
        )

        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT,
                self.tr('Connected polygons', 'Polígonos conectados')
            )
        )

    def processAlgorithm(self, parameters, context, feedback):

        lotes = self.parameterAsSource(
            parameters,
            self.POLYGONS,
            context
        )
        if lotes is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.POLYGONS))

        camada = self.parameterAsSource(
            parameters,
            self.LAYER,
            context
        )
        if camada is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.LAYER))

        # OUTPUT
        (sink, dest_id) = self.parameterAsSink(
            parameters,
            self.OUTPUT,
            context,
            lotes.fields(),
            lotes.wkbType(),
            lotes.sourceCrs()
        )
        if sink is None:
            raise QgsProcessingException(self.invalidSinkError(parameters, self.OUTPUT))

        tol = self.parameterAsDouble(
            parameters,
            self.TOLERANCE,
            context
        )
        if not tol or tol <= 0:
            raise QgsProcessingException(self.tr('Invalid tolerance!', 'Tolerâncias inválida!'))

        index = QgsSpatialIndex(lotes.getFeatures())

        # Verificando SRC das camadas
        mesmoSRC = True
        if lotes.sourceCrs() != camada.sourceCrs():
            mesmoSRC = False
            coordinateTransformer = QgsCoordinateTransform()
            coordinateTransformer.setDestinationCrs(lotes.sourceCrs())
            coordinateTransformer.setSourceCrs(camada.sourceCrs())

        feicoes = {}
        for feat in lotes.getFeatures():
            feicoes[feat.id()] = feat
            if feat.geometry().isMultipart():
                raise QgsProcessingException(self.tr('Feature id {} is multipart! Multipart features are not allowed!', 'Feição de id {} é multiparte! Feições multipartes não são permitidas!' ).format(feat.id()))

        if lotes.sourceCrs().isGeographic():
            tol /= 111000 # transforma de graus para metros

        # Verificar e corrigir conectividade
        #feedback.pushInfo(self.tr('Checking and fixing connectivity...', 'Verificando e corrigindo conectividade...'))
        tam = len(feicoes)
        for feat_a in camada.getFeatures():
            geom_a = feat_a.geometry()
            if not mesmoSRC:
                geom_a.transform(coordinateTransformer)
            if geom_a.type() == 1:
                if geom_a.isMultipart():
                    coord_a = geom_a.asMultiPolyline()[0]
                else:
                    coord_a = geom_a.asPolyline()
            elif geom_a.type() == 2:
                if geom_a.isMultipart():
                    coord_a = geom_a.asMultiPolygon()[0][0]
                else:
                    coord_a = geom_a.asPolygon()[0]
            elif geom_a.type() == 0:
                if geom_a.isMultipart():
                    coord_a = geom_a.asMultiPoint()
                else:
                    coord_a = [geom_a.asPoint()]

            bbox_a = geom_a.boundingBox()
            feat_ids = index.intersects(bbox_a)

            for feat_id in feat_ids:
                feat_b = feicoes[feat_id]
                geom_b = feat_b.geometry()
                # Verificar se algum ponto de A que intercepta o segmento de B, não tem vértice correspondente
                if geom_b.isMultipart():
                    coord_b = geom_b.asMultiPolygon()[0][0]
                else:
                    coord_b = geom_b.asPolygon()[0]
                new_coord_b = []
                for k in range(len(coord_b)-1):
                    p1 = coord_b[k]
                    p2 = coord_b[k+1]
                    segm = QgsGeometry.fromPolylineXY([p1, p2])
                    sentinela = False
                    for pnt_a in coord_a:
                        pnt = QgsGeometry.fromPointXY(pnt_a).buffer(tol,1)
                        if pnt_a not in coord_b and pnt.intersects(segm):
                            new_coord_b += [p1, pnt_a]
                            sentinela = True
                            break
                    if not sentinela:
                        new_coord_b += [p1]
                new_coord_b += [coord_b[-1]]
                feat_b.setGeometry(QgsGeometry.fromPolygonXY([new_coord_b]))
                feicoes[feat_id] = feat_b

        for index, ID in enumerate(feicoes):
            feature = feicoes[ID]
            sink.addFeature(feature, QgsFeatureSink.FastInsert)

        feedback.pushInfo(self.tr('Operation completed successfully!', 'Operação finalizada com sucesso!'))
        feedback.pushInfo(self.tr('Leandro Franca - Cartographic Engineer', 'Leandro França - Eng Cart'))

        return {self.OUTPUT: dest_id}
