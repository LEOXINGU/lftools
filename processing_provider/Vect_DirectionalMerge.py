# -*- coding: utf-8 -*-


"""
Vect_DirectionalMerge.py
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
__date__ = '2021-02-13'
__copyright__ = '(C) 2021, Leandro França'

from qgis.core import (QgsApplication,
                       Qgis,
                       QgsGeometry,
                       QgsWkbTypes,
                       QgsFeature,
                       QgsProcessingParameterEnum,
                       QgsProcessingParameterNumber,
                       QgsFeatureSink,
                       QgsProcessingException,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterFeatureSink)
from math import atan2, degrees, hypot, isfinite
from lftools.geocapt.imgs import Imgs
from lftools.translations.translate import translate
import os
from qgis.PyQt.QtGui import QIcon

class DirectionalMerge(QgsProcessingAlgorithm):

    LOC = QgsApplication.locale()[:2]

    def tr(self, *string):
        return translate(string, self.LOC)

    def createInstance(self):
        return DirectionalMerge()

    def name(self):
        return 'directionalmerge'

    def displayName(self):
        return self.tr('Merge lines in direction', 'Mesclar linhas na direção')

    def group(self):
        return self.tr('Vector', 'Vetor')

    def groupId(self):
        return 'vector'

    def tags(self):
        return 'GeoOne,merge,dissolve,directional,touches,lines,connect,drainage,network'.split(',')

    def icon(self):
        return QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images/vetor.png'))

    txt_en = ('This algorithm merges lines that share a starting or ending XY point and have compatible directions, within an angular tolerance from 0 to 90 degrees (inclusive). '
              '<p>Attributes:</p><ul><li>1 - merge only lines with identical attributes;</li><li>2 - keep the attributes of the longest original line part in each merged chain.</li></ul>'
              '<p>Null, empty and degenerate parts are skipped with a warning. Closed lines are preserved. There is no distance-based snapping.</p>')
    txt_pt = ('Este algoritmo mescla linhas que compartilham uma extremidade XY e apresentam direções compatíveis, dentro de uma tolerância angular de 0 a 90 graus (inclusive). '
              '<p>Atributos:</p><ul><li>1 - mesclar apenas linhas com atributos idênticos;</li><li>2 - manter os atributos da maior parte linear original de cada cadeia mesclada.</li></ul>'
              '<p>Partes nulas, vazias e degeneradas são ignoradas com aviso. Linhas fechadas são preservadas. Não há ajuste por tolerância de distância.</p>')
    figure = 'images/tutorial/vect_directional_merge.jpg'

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
    ANGLE = 'ANGLE'
    OUTPUT = 'OUTPUT'

    def initAlgorithm(self, config=None):

        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.LINES,
                self.tr('Line Layer', 'Camada de Linhas'),
                [Qgis.ProcessingSourceType.TypeVectorLine]
            )
        )

        tipo = [self.tr('merge lines that have the same attributes','mesclar linhas que tenham os mesmos atributos'),
                self.tr('keep the attributes of the longest line','manter os atributos da linha maior')
               ]

        self.addParameter(
            QgsProcessingParameterEnum(
                self.TYPE,
                self.tr('Attributes', 'Atributos'),
				options = tipo,
                defaultValue= 1
            )
        )

        self.addParameter(
            QgsProcessingParameterNumber(
                self.ANGLE,
                self.tr('Tolerance in degrees', 'Tolerância em graus'),
                type = QgsProcessingParameterNumber.Type.Double,
                defaultValue = 30,
                minValue = 0,
                maxValue = 90
                )
            )

        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT,
                self.tr('Merged lines', 'Linhas mescladas')
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


        atributos = self.parameterAsEnum(
            parameters,
            self.TYPE,
            context
        )

        tol = self.parameterAsDouble(
            parameters,
            self.ANGLE,
            context
        )
        if not isfinite(tol) or tol > 90 or tol < 0:
            raise QgsProcessingException(self.tr('The input angle must be between 0 and 90 degrees!', 'O ângulo de entrada deve ser entre 0 e 90 graus!'))


        (sink, dest_id) = self.parameterAsSink(
            parameters,
            self.OUTPUT,
            context,
            linhas.fields(),
            QgsWkbTypes.linearType(linhas.wkbType()),
            linhas.sourceCrs(),
            # Partes de uma mesma feicao podem repetir a chave primaria.
            QgsFeatureSink.SinkFlag.RegeneratePrimaryKey
            if QgsWkbTypes.isMultiType(linhas.wkbType()) else QgsFeatureSink.SinkFlags()
        )
        if sink is None:
            raise QgsProcessingException(self.invalidSinkError(parameters, self.OUTPUT))

        # Cada registro guarda tambem o comprimento da maior parte ORIGINAL.
        # Assim, uma cadeia acumulada nao passa a dominar a escolha dos atributos.
        feedback.pushInfo(self.tr('Calculating feature informations...', 'Calculando informações das feições...'))
        lista = []
        total = max(1, linhas.featureCount())
        for k, feature in enumerate(linhas.getFeatures()):
            if feedback.isCanceled():
                return {self.OUTPUT: dest_id}
            lista.extend(self.pontos_ang(feature, feedback))
            feedback.setProgress(int(20 * (k + 1) / total))

        feedback.pushInfo(self.tr('Merging lines...', 'Mesclando linhas...'))
        nova_lista = []
        total = max(1, len(lista))
        while lista:
            if feedback.isCanceled():
                return {self.OUTPUT: dest_id}
            atual = lista.pop(0)
            # Aneis existentes ou formados por uma mescla nao recebem ramificacoes.
            while not self.same_xy(atual[1], atual[2]):
                for j, proxima in enumerate(lista):
                    if feedback.isCanceled():
                        return {self.OUTPUT: dest_id}
                    if self.same_xy(proxima[1], proxima[2]):
                        continue
                    if atributos == 0 and atual[5] != proxima[5]:
                        continue
                    coord = self.merge_coords(atual, proxima, tol)
                    if coord is None:
                        continue
                    # Empates preservam os atributos do primeiro registro.
                    maior = atual if atual[6] >= proxima[6] else proxima
                    atual = self.line_info(coord, maior[5], maior[6])
                    del lista[j]
                    break
                else:
                    break
            nova_lista.append(atual)
            feedback.setProgress(int(20 + 60 * (1 - len(lista) / total)))

        feedback.pushInfo(self.tr('Saving output...', 'Salvando saída...'))
        total = max(1, len(nova_lista))
        multipart = QgsWkbTypes.isMultiType(linhas.wkbType())
        for k, item in enumerate(nova_lista):
            if feedback.isCanceled():
                return {self.OUTPUT: dest_id}
            # fromPolyline preserva Z/M; asPolyline/fromPolylineXY descartam Z/M.
            geom = QgsGeometry.fromPolyline(item[0])
            if multipart and not geom.convertToMultiType():
                raise QgsProcessingException(self.tr(
                    'Could not create multipart output.',
                    'Não foi possível criar a saída multiparte.'))
            fet = QgsFeature(linhas.fields())
            fet.setGeometry(geom)
            fet.setAttributes(item[5])
            if not sink.addFeature(fet, QgsFeatureSink.Flag.FastInsert):
                raise QgsProcessingException(self.tr(
                    'Could not save an output feature.',
                    'Não foi possível salvar uma feição de saída.'))
            feedback.setProgress(int(80 + 20 * (k + 1) / total))

        feedback.setProgress(100)
        feedback.pushInfo(self.tr('Operation completed successfully!', 'Operação finalizada com sucesso!'))
        feedback.pushInfo(self.tr('Leandro Franca - Cartographic Engineer', 'Leandro França - Eng Cart'))
        return {self.OUTPUT: dest_id}

    @staticmethod
    def same_xy(a, b):
        # A tolerancia do algoritmo e angular, nao uma distancia de ajuste.
        return a.x() == b.x() and a.y() == b.y()

    @staticmethod
    def angle_diff(a, b):
        return abs((a - b + 180.0) % 360.0 - 180.0)

    def merge_coords(self, a, b, tol):
        # Concatenar os vertices evita que a uniao GEOS (combine) devolva uma
        # MultiLineString mesmo quando as duas linhas podem formar uma cadeia.
        # O vertice comum e incluido apenas uma vez.
        if self.same_xy(a[2], b[1]) and self.angle_diff(a[4], b[3]) <= tol:
            return a[0] + b[0][1:]
        if self.same_xy(a[1], b[2]) and self.angle_diff(a[3], b[4]) <= tol:
            return b[0] + a[0][1:]
        if self.same_xy(a[1], b[1]) and self.angle_diff(a[3], b[3] + 180) <= tol:
            return list(reversed(a[0])) + b[0][1:]
        if self.same_xy(a[2], b[2]) and self.angle_diff(a[4], b[4] + 180) <= tol:
            return a[0] + list(reversed(b[0]))[1:]
        return None

    def line_info(self, coord, att, longest=None):
        if len(coord) < 2 or any(not isfinite(p.x()) or not isfinite(p.y()) for p in coord):
            return None
        # Vertices repetidos nas extremidades nao definem uma tangente.
        inicio = next((p for p in coord[1:] if not self.same_xy(p, coord[0])), None)
        fim = next((p for p in reversed(coord[:-1]) if not self.same_xy(p, coord[-1])), None)
        if inicio is None or fim is None:
            return None
        ang_ini = degrees(atan2(inicio.y() - coord[0].y(), inicio.x() - coord[0].x()))
        ang_fim = degrees(atan2(coord[-1].y() - fim.y(), coord[-1].x() - fim.x()))
        if longest is None:
            longest = sum(hypot(b.x() - a.x(), b.y() - a.y())
                          for a, b in zip(coord, coord[1:]))
        return [coord, coord[0], coord[-1], ang_ini, ang_fim, att, longest]

    def pontos_ang(self, feature, feedback=None):
        geom = feature.geometry()
        if geom.isNull() or geom.isEmpty():
            if feedback is not None:
                feedback.pushWarning(self.tr(
                    'Feature {} skipped: null or empty geometry.',
                    'Feição {} ignorada: geometria nula ou vazia.').format(feature.id()))
            return []
        # Trabalhar em uma copia e segmentizar curvas, preservando vertices Z/M.
        geom = QgsGeometry(geom)
        geom.convertToStraightSegment()
        partes = geom.asGeometryCollection() if geom.isMultipart() else [geom]
        itens = []
        for numero, parte in enumerate(partes, 1):
            if feedback is not None and feedback.isCanceled():
                break
            if parte.type() != Qgis.GeometryType.Line:
                raise QgsProcessingException(self.tr(
                    'Feature {} contains a non-line geometry.',
                    'A feição {} contém uma geometria que não é linear.').format(feature.id()))
            item = self.line_info(list(parte.vertices()), feature.attributes())
            if item is None:
                if feedback is not None:
                    feedback.pushWarning(self.tr(
                        'Feature {}, part {} skipped: insufficient distinct XY vertices or non-finite coordinates.',
                        'Feição {}, parte {} ignorada: vértices XY distintos insuficientes ou coordenadas não finitas.'
                    ).format(feature.id(), numero))
                continue
            itens.append(item)
        return itens

    # Funcao mantida para compatibilidade.
    def contraAz(self, x):
        return x + 180 if x <= 0 else x - 180
