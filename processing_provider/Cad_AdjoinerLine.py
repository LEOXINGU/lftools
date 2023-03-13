# -*- coding: utf-8 -*-

"""
Cad_AdjoinerLine.py
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
__date__ = '2023-03-12'
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
from lftools.geocapt.cartography import OrientarPoligono
import numpy as np
import os
from qgis.PyQt.QtGui import QIcon

class AdjoinerLine(QgsProcessingAlgorithm):

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
        return AdjoinerLine()

    def name(self):
        return 'adjoinerline'

    def displayName(self):
        return self.tr('Adjoiner Lines', 'Linhas de Confrontantes')

    def group(self):
        return self.tr('Cadastre', 'Cadastro')

    def groupId(self):
        return 'cadastro'

    def tags(self):
        return self.tr('cadastro,parcela,sequence,confrontante,vizinho,neighbours,adjoiner,adjoining,abut,adjacent,lot,line,front,cadastre,street,borderer,testada,linha,loteamento').split(',')

    def icon(self):
        return QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images/cadastre.png'))

    txt_en = '''Generates adjoiner lines from a polygon layer of parcels.'''
    txt_pt = '''Gera as linhas de confrontantes das parcelas a partir dos polígonos dos lotes.'''
    figure = 'images/tutorial/cadastre_adjoiners.jpg'

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
    TOLERANCE = 'TOLERANCE'

    def initAlgorithm(self, config = None):
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT,
                self.tr('Parcels', 'Lotes'),
                [QgsProcessing.TypeVectorPolygon]
            )
        )

        # OUTPUT
        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT,
                self.tr('Adjoiners', 'Confrontantes')
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
            QgsWkbTypes.LineString,
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

        lista_inter = []
        lista_testada = []
        feedback.pushInfo(self.tr('Identifying adjoining lines...', 'Idenficando linhas de confrontação...'))
        total = 100.0 / layer.featureCount() if layer.featureCount() else 0
        for current, feat1 in enumerate(layer.getFeatures()):
            geom1 = feat1.geometry()
            linha1 = QgsGeometry.fromPolylineXY(geom1.asPolygon()[0])
            bbox1 = geom1.boundingBox()
            feat_ids = index.intersects(bbox1)
            for feat2 in layer.getFeatures(QgsFeatureRequest(feat_ids)):
                if feat1.id() != feat2.id():
                    geom2 = feat2.geometry()
                    bbox2 = geom2.boundingBox()
                    linha2 = QgsGeometry.fromPolylineXY(geom2.asPolygon()[0])

                    # Linhas de interseção com confrontantes
                    if geom1.intersects(geom2):
                        inter = geom1.intersection(geom2)
                        if inter.type() == 1: # linha
                            feature = QgsFeature()
                            feature.setGeometry(inter)
                            feature.setAttributes([feat1.id(), feat2.id()])
                            lista_inter += [feature]

                    # Linhas de testada dos polígonos
                    bbox_linha1 = linha1.boundingBox()
                    if bbox_linha1.intersects(bbox2):
                        if linha1.intersects(linha2):
                            differ = linha1.difference(linha2)
                            linha1 = differ

            # Gravando as linhas de testada
            if linha1.type() == 1: # linha
                if linha1.isMultipart():
                    linhas = linha1.asMultiPolyline()
                    for linha in linhas:
                        geom = QgsGeometry.fromPolylineXY(linha)
                        feature = QgsFeature()
                        feature.setGeometry(geom)
                        feature.setAttributes([feat1.id(), feat1.id()])
                        lista_testada += [feature]
                else:
                    feature = QgsFeature()
                    feature.setGeometry(linha1)
                    feature.setAttributes([feat1.id(), feat1.id()])
                    lista_testada += [feature]

            if feedback.isCanceled():
                break
            feedback.setProgress(int((current+1) * total))


        # Juntar tudo
        lista = lista_inter + lista_testada
        feedback.pushInfo(self.tr('Creating new layer...', 'Criando nova camada...'))
        for feat in lista:
            sink.addFeature(feat, QgsFeatureSink.FastInsert)
            if feedback.isCanceled():
                break

        feedback.pushInfo(self.tr('Operation completed successfully!', 'Operação finalizada com sucesso!'))
        feedback.pushInfo(self.tr('Leandro Franca - Cartographic Engineer', 'Leandro França - Eng Cart'))

        return {self.OUTPUT: dest_id}
