# -*- coding: utf-8 -*-

"""
Cad_FrontLotLine.py
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
__date__ = '2022-03-08'
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
from lftools.geocapt.cartography import OrientarPoligono
import numpy as np
import os
from qgis.PyQt.QtGui import QIcon

class FrontLotLine(QgsProcessingAlgorithm):

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
        return FrontLotLine()

    def name(self):
        return 'frontlotline'

    def displayName(self):
        return self.tr('Front Lot Lines', 'Linhas de Testada')

    def group(self):
        return self.tr('Cadastre', 'Cadastro')

    def groupId(self):
        return 'cadastro'

    def tags(self):
        return self.tr('cadastro,parcela,sequence,number,code,codificar,organize,system,lot,line,front,cadastre,street,borderer,testada,linha,loteamento').split(',')

    def icon(self):
        return QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images/cadastre.png'))

    txt_en = '''Generates front lot lines from a polygon layer of parcels.'''
    txt_pt = '''Gera as linhas de testada das parcelas a partir dos polígonos dos lotes.'''
    figure = 'images/tutorial/cadastre_frontlotline.jpg'

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

        self.addParameter(
            QgsProcessingParameterNumber(
                self.TOLERANCE,
                self.tr('Tolerance for snapping in meters', 'Tolerância para a aderência (metros)'),
                type = 1,
                defaultValue = 0.01,
                minValue = 0
            )
        )

        # OUTPUT
        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT,
                self.tr('Front Lot Lines', 'Linhas de Testada')
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
        if tol <= 0:
            raise QgsProcessingException(self.tr('Invalid tolerance!', 'Tolerâncias inválida!'))

        # Camada de Saída
        Fields = lotes.fields()
        itens  = {
                     self.tr('sequence', 'sequência') : QVariant.Int,
                     self.tr('lenght', 'comprimento') : QVariant.Double,
                     self.tr('cumulative', 'valor_testada') : QVariant.Double,
                     }
        for item in itens:
            Fields.append(QgsField(item, itens[item]))
        (sink, dest_id) = self.parameterAsSink(
            parameters,
            self.OUTPUT,
            context,
            Fields,
            QgsWkbTypes.LineString,
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

        # Pegar geometrias para mesclar
        feedback.pushInfo(self.tr('Defining set of parcels (blocks)...', 'Definindo conjunto de parcelas (quadras)...'))
        geometrias = []
        for feat in feicoes:
            geometrias += [feat.geometry()]

        # Separar por quadras (Mesclar lotes)
        quadras = []
        while len(geometrias)>1:
            tam = len(geometrias)
            for i in range(0,tam-1):
                mergeou = False
                geom_A = geometrias[i]
                for j in range(i+1,tam):
                    geom_B = geometrias[j]
                    if geom_A.intersects(geom_B):
                        mergeou = True
                        new_geom = geom_A.combine(geom_B)
                        break
                if mergeou:
                    del geometrias[i], geometrias[j-1]
                    geometrias = [new_geom] + geometrias
                    break
                else:
                    quadras += [geom_A]
                    del geometrias[i]
                    break
        if geometrias:
            quadras += geometrias

        # Orientar polígonos
        feedback.pushInfo(self.tr('Orienting polygon (clockwise)...', 'Orientando polígono (sentido horário)...'))
        for k in range(len(feicoes)):
            feat = feicoes[k]
            coords = feat.geometry().asPolygon()[0]
            coords = coords[:-1]
            coords = OrientarPoligono(coords, primeiro=1, sentido=0) #mais ao norte e sentido horário
            new_geom = QgsGeometry.fromPolygonXY([coords])
            feat.setGeometry(new_geom)
            feicoes[k] = feat

        # Separar feições por quadra
        qd_dic = {}
        testada_dic = {}
        for qd in quadras:
            qd_dic[qd] = []
            testada_dic[qd] = []

        for feat in feicoes:
            geom = feat.geometry()
            for qd in quadras:
                if geom.intersects(qd):
                    qd_dic[qd] += [feat]


        # Calcular testadas por quadras
        feedback.pushInfo(self.tr('Calculating front lot lines...', 'Calculando testadas...'))
        for qd in quadras:
            linhas = [] # Colocar poligonos em lista
            atributos = []
            for feat in qd_dic[qd]:
                geom = feat.geometry()
                att = feat.attributes()
                atributos += [att]
                linhas += [geom.asPolygon()[0]]

            TAM = len(linhas)

            # Calculando a diferenca para cada linha
            for current, i in enumerate(range(TAM)):
                geom1 = QgsGeometry.fromPolylineXY(linhas[i])
                for j in range(TAM):
                    if i != j:
                        geom2 = QgsGeometry.fromPolylineXY(linhas[j])
                        if geom1.intersects(geom2):
                            differ = geom1.difference(geom2)
                            geom1 = differ
                if geom1.length() > 0:
                    if geom1.isMultipart():
                        partes = geom1.asMultiPolyline()
                        partes_novas = []
                        while len(partes)>1:
                            tam = len(partes)
                            for r in range(0,tam-1):
                                mergeou = False
                                parte_A = partes[r]
                                for s in range(r+1,tam):
                                    parte_B = partes[s]
                                    if parte_A[0] == parte_B[0] or parte_A[0] == parte_B[-1] or parte_A[-1] == parte_B[0] or parte_A[-1] == parte_B[-1]:
                                        mergeou = True
                                        if parte_A[0] == parte_B[0]:
                                            parte_nova = parte_B[1:][::-1] + parte_A
                                        elif parte_A[0] == parte_B[-1]:
                                            parte_nova = parte_B + parte_A[1:]
                                        elif parte_A[-1] == parte_B[0]:
                                            parte_nova = parte_A + parte_B[1:]
                                        elif  parte_A[-1] == parte_B[-1]:
                                            parte_nova = parte_A + parte_B[::-1][1:]
                                        break
                                if mergeou:
                                    del partes[r], partes[s-1]
                                    partes = [parte_nova] + partes
                                    break
                                else:
                                    partes_novas += [parte_A]
                                    del partes[r]
                                    break
                        if partes:
                            partes_novas += partes
                        for parte in partes_novas:
                            geom = QgsGeometry.fromPolylineXY(parte)
                            feature = QgsFeature()
                            feature.setGeometry(geom)
                            feature.setAttributes(atributos[i])
                            testada_dic[qd] += [feature]
                    else:
                        feature = QgsFeature()
                        feature.setGeometry(geom1)
                        feature.setAttributes(atributos[i])
                        testada_dic[qd] += [feature]

        feedback.pushInfo(self.tr('Sequencing and saving front lot lines...', 'Sequenciando e salvando as linhas de testada...'))
        for qd in testada_dic:
            testadas = testada_dic[qd]
            # Pegar ponto mais ao norte/oeste da Quadra
            coords = qd.asPolygon()[0]
            pnt = OrientarPoligono(coords[:-1], primeiro=1, sentido=2)[0]
            pnt = QgsGeometry.fromPointXY(pnt)
            if len(testadas) == 1: #apenas 1 lote
                testadas_seq = [testadas[0]]
            else:
                # Verificar qual testada intercepta e não é último ponto
                for feat in testadas:
                    lin = feat.geometry()
                    ultimo_pnt = QgsGeometry.fromPointXY(lin.asPolyline()[-1])
                    if pnt.intersects(lin) and not pnt.intersects(ultimo_pnt):
                        testadas_seq = [feat]
                # Criar rede para cada quadra
                for k in range(1, len(testadas)):
                    ultima_testada = testadas_seq[k-1].geometry()
                    ultimo_pnt = QgsGeometry.fromPointXY(ultima_testada.asPolyline()[-1])
                    for feat in testadas:
                        primeiro_pnt = QgsGeometry.fromPointXY(feat.geometry().asPolyline()[0])
                        if ultimo_pnt.intersects(primeiro_pnt):
                            testadas_seq += [feat]
                            break
            # Preencher atributos: ordem, comprimento e comprimento acumulado
            soma = 0
            for k, feat in enumerate(testadas_seq):
                comprimento = feat.geometry().length()
                soma += comprimento
                feature = QgsFeature(Fields)
                feature.setGeometry(feat.geometry())
                feature.setAttributes(feat.attributes() + [k+1, comprimento, soma])
                sink.addFeature(feature, QgsFeatureSink.FastInsert)
                if feedback.isCanceled():
                    break

        feedback.pushInfo(self.tr('Operation completed successfully!', 'Operação finalizada com sucesso!'))
        feedback.pushInfo(self.tr('Leandro Franca - Cartographic Engineer', 'Leandro França - Eng Cart'))

        return {self.OUTPUT: dest_id}
