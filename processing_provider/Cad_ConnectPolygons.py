# -*- coding: utf-8 -*-

"""
Cad_ConnectFeatures.py
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
__date__ = '2022-06-13'
__copyright__ = '(C) 2022, Leandro França'

from qgis.PyQt.QtCore import QCoreApplication, QVariant
from qgis.core import (QgsApplication,
                       QgsGeometry,
                       QgsWkbTypes,
                       QgsFeature,
                       QgsField,
                       QgsProcessing,
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
import numpy as np
import os
from qgis.PyQt.QtGui import QIcon

class ConnectFeatures(QgsProcessingAlgorithm):

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
        return ConnectFeatures()

    def name(self):
        return 'connectfeatures'

    def displayName(self):
        return self.tr('Connect features', 'Conectar feições')

    def group(self):
        return self.tr('Cadastre', 'Cadastro')

    def groupId(self):
        return 'cadastro'

    def tags(self):
        return self.tr('connect,polygons,polígonos,conectar,validation,topology,cadastro,parcela,organize,system,cadastre,borderer,testada,linha,loteamento,adjacency,adjacência,dangle,lacuna,overlap,validação,qualidade,quality').split(',')

    def icon(self):
        return QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images/cadastre.png'))

    txt_en = '''Creates new vertices between adjacent polygons to ensure perfect connectivity (topology) between them.'''
    txt_pt = '''Gera novos vértices entre polígonos adjacentes para garantir a perfeita conectividade (topologia) entre eles.'''
    figure = 'images/tutorial/cadastre_connectFeatures.jpg'

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

    def initAlgorithm(self, config=None):
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT,
                self.tr('Parcels', 'Lotes'),
                [QgsProcessing.TypeVectorPolygon]
            )
        )

        self.addParameter(
            QgsProcessingParameterNumber(
                self.TOLERANCE,
                self.tr('Tolerance for snapping in meters', 'Tolerância para a aderência (metros)'),
                type=1,
                defaultValue = 0.01
            )
        )

        # OUTPUT
        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT,
                self.tr('Connected parcels', 'Lotes conectados')
            )
        )

    def processAlgorithm(self, parameters, context, feedback):

        lotes = self.parameterAsSource(
            parameters,
            self.INPUT,
            context
        )
        if lotes is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.INPUT))

        tol = self.parameterAsDouble(
            parameters,
            self.TOLERANCE,
            context
        )
        if not tol or tol <= 0:
            raise QgsProcessingException(self.tr('Invalid tolerance!', 'Tolerâncias inválida!'))

        # Camada de Saída
        Fields = lotes.fields()
        (sink, dest_id) = self.parameterAsSink(
            parameters,
            self.OUTPUT,
            context,
            Fields,
            QgsWkbTypes.Polygon,
            lotes.sourceCrs()
        )
        if sink is None:
            raise QgsProcessingException(self.invalidSinkError(parameters, self.OUTPUT))

        # Validar:
        # não pode ser multipolígono
        feicoes = []
        for feat in lotes.getFeatures():
            feicoes += [feat]
            if feat.geometry().isMultipart():
                raise QgsProcessingException(self.tr('Feature id {} is multipart! Multipart features are not allowed!', 'Feição de id {} é multiparte! Feições multipartes não são permitidas!' ).format(feat.id()))

        if lotes.sourceCrs().isGeographic():
            tol /= 111000 # transforma de graus para metros

        # Verificar e corrigir conectividade
        feedback.pushInfo(self.tr('Checking and fixing connectivity...', 'Verificando e corrigindo conectividade...'))
        tam = len(feicoes)
        for i in range(tam):
            for j in range(tam):
                if i != j:
                    feat_a = feicoes[i]
                    geom_a = feat_a.geometry()
                    feat_b = feicoes[j]
                    geom_b = feat_b.geometry()
                    if geom_a.intersects(geom_b):
                        # Verificar se algum ponto de A que intercepta o segmento de B, não tem vértice correspondente
                        coord_a = geom_a.asPolygon()[0]
                        coord_b = geom_b.asPolygon()[0]
                        new_coord_b =[]
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
                        feicoes[j] = feat_b
        # Resultados
        tam = len(feicoes)
        total = 100/tam if tam > 0 else 0
        for cont, feat in enumerate(feicoes):
            sink.addFeature(feat, QgsFeatureSink.FastInsert)
            feedback.setProgress(int((cont+1) * total))
            if feedback.isCanceled():
                break

        feedback.pushInfo(self.tr('Operation completed successfully!', 'Operação finalizada com sucesso!'))
        feedback.pushInfo(self.tr('Leandro Franca - Cartographic Engineer', 'Leandro França - Eng Cart'))

        return {self.OUTPUT: dest_id}
