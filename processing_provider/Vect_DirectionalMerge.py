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

from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (QgsApplication,
                       QgsProcessingParameterVectorLayer,
                       QgsGeometry,
                       QgsFeature,
                       QgsProcessing,
                       QgsProcessingParameterField,
                       QgsProcessingParameterBoolean,
                       QgsProcessingParameterEnum,
                       QgsProcessingParameterNumber,
                       QgsFeatureSink,
                       QgsProcessingException,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterFeatureSink)
from math import atan2, degrees, fabs
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

    txt_en = 'This algorithm merges lines that touch at their starting or ending points and has the same direction (given a tolerance in degrees). <p>For the attributes can be considered:</p>1 - merge lines that have the same attributes; or</li><li>2 - keep the attributes of the longest line.</li>'
    txt_pt = 'Este algoritmo mescla linhas que se tocam nos seus pontos inicial ou final e tem a mesma direção (dada uma tolerância em graus).<p>Para os atributos pode ser considerado:</p><li>1 - mesclar linhas que tenham os mesmos atributos; ou</li><li>2 - manter os atributos da linha maior.</li>'
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
                [QgsProcessing.TypeVectorLine]
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
                defaultValue = 30
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
        if tol is None or tol > 90 or tol < 0:
            raise QgsProcessingException(self.tr('The input angle must be between 0 and 90 degrees!', 'O ângulo de entrada deve ser entre 0 e 90 graus!'))


        (sink, dest_id) = self.parameterAsSink(
            parameters,
            self.OUTPUT,
            context,
            linhas.fields(),
            linhas.wkbType(),
            linhas.sourceCrs()
        )
        if sink is None:
            raise QgsProcessingException(self.invalidSinkError(parameters, self.OUTPUT))

        # Criar lista com informacoes das feicoes
        feedback.pushInfo(self.tr('Calculating feature informations...', 'Calculando informações das feições...'))
        lista = []
        for feature in linhas.getFeatures():
                lista += self.pontos_ang(feature)

        # Criar uma nova lista com as feicoes finais mescladas
        nova_lista = []
        # Remover os aneis lineares da lista e acrescentar na nova lista
        ind = 0
        while ind < len(lista)-1:
            P_ini = lista[ind][1]
            P_fim = lista[ind][2]
            if P_ini == P_fim:
                nova_lista += [lista[ind][0]]
                del lista[ind]
            else:
                ind +=1

        # Mesclar linhas que se tocam e tem a mesma direcao (com mesmo atributo)
        feedback.pushInfo(self.tr('Merging lines...', 'Mesclando linhas...'))
        if atributos == 0:
            while len(lista)>1:
                tam = len(lista)
                for i in range(0,tam-1):
                    mergeou = False
                    # Ponto inicial e final da feicao A
                    coord_A = lista[i][0]
                    P_ini_A = lista[i][1]
                    P_fim_A = lista[i][2]
                    ang_ini_A = lista[i][3]
                    ang_fim_A = lista[i][4]
                    att_A = lista[i][5]
                    for j in range(i+1,tam):
                        # Ponto inicial e final da feicao B
                        coord_B = lista[j][0]
                        P_ini_B = lista[j][1]
                        P_fim_B = lista[j][2]
                        ang_ini_B = lista[j][3]
                        ang_fim_B = lista[j][4]
                        att_B = lista[j][5]
                        if att_A == att_B:
                            # 4 possibilidades
                            # 1 - Ponto final de A igual ao ponto inicial de B
                            if (P_fim_A == P_ini_B) and (fabs(ang_fim_A-ang_ini_B)<tol or fabs(360-fabs(ang_fim_A-ang_ini_B))<tol):
                                mergeou = True
                                break
                            # 2 - Ponto inicial de A igual ao ponto final de B
                            elif (P_ini_A == P_fim_B) and (fabs(ang_ini_A-ang_fim_B)<tol or fabs(360-fabs(ang_ini_A-ang_fim_B))<tol):
                                mergeou = True
                                break
                            # 3 - Ponto incial de A igual ao ponto inicial de B
                            elif (P_ini_A == P_ini_B) and (fabs(ang_ini_A- self.contraAz(ang_ini_B))<tol or fabs(360-fabs(ang_ini_A - self.contraAz(ang_ini_B)))<tol):
                                mergeou = True
                                break
                            # 4 - Ponto final de A igual ao ponto final de B
                            elif (P_fim_A == P_fim_B) and (fabs(ang_fim_A - self.contraAz(ang_fim_B))<tol or fabs(360-fabs(ang_fim_A - self.contraAz(ang_fim_B)))<tol):
                                mergeou = True
                                break
                    if mergeou:
                        geom_A = QgsGeometry.fromPolylineXY(coord_A)
                        geom_B = QgsGeometry.fromPolylineXY(coord_B)
                        new_geom = geom_A.combine(geom_B)

                        new_feat = QgsFeature()
                        new_feat.setAttributes(att_A)
                        new_feat.setGeometry(new_geom)

                        if new_geom.isMultipart():
                            nova_lista += [[coord_A, att_A], [coord_B, att_B]]
                            del lista[i], lista[j-1]
                            break
                        else:
                            del lista[i], lista[j-1]
                            lista = self.pontos_ang(new_feat)+lista
                            break
                    if not(mergeou):
                        # Tirar a geometria que nao se conecta com nada da lista
                        nova_lista += [[coord_A, att_A]]
                        del lista[i]
                        break
                if len(lista)==1:
                    nova_lista += [[lista[0][0], lista[0][5]]]

        # Mesclar os que se tocam e tem mesma direcao (preservar atributos da linha maior)
        if atributos == 1:
            while len(lista)>1:
                tam = len(lista)
                for i in range(0,tam-1):
                    mergeou = False
                    # Ponto inicial e final da feicao A
                    coord_A = lista[i][0]
                    P_ini_A = lista[i][1]
                    P_fim_A = lista[i][2]
                    ang_ini_A = lista[i][3]
                    ang_fim_A = lista[i][4]
                    att_A = lista[i][5]
                    for j in range(i+1,tam):
                        # Ponto inicial e final da feicao B
                        coord_B = lista[j][0]
                        P_ini_B = lista[j][1]
                        P_fim_B = lista[j][2]
                        ang_ini_B = lista[j][3]
                        ang_fim_B = lista[j][4]
                        att_B = lista[j][5]
                        # 4 possibilidades
                        # 1 - Ponto final de A igual ao ponto inicial de B
                        if (P_fim_A == P_ini_B) and (fabs(ang_fim_A-ang_ini_B)<tol or fabs(360-fabs(ang_fim_A-ang_ini_B))<tol):
                            mergeou = True
                            break
                        # 2 - Ponto inicial de A igual ao ponto final de B
                        elif (P_ini_A == P_fim_B) and (fabs(ang_ini_A-ang_fim_B)<tol or fabs(360-fabs(ang_ini_A-ang_fim_B))<tol):
                            mergeou = True
                            break
                        # 3 - Ponto incial de A igual ao ponto inicial de B
                        elif (P_ini_A == P_ini_B) and (fabs(ang_ini_A - self.contraAz(ang_ini_B))<tol or fabs(360-fabs(ang_ini_A - self.contraAz(ang_ini_B)))<tol):
                            mergeou = True
                            break
                        # 4 - Ponto final de A igual ao ponto final de B
                        elif (P_fim_A == P_fim_B) and (fabs(ang_fim_A - self.contraAz(ang_fim_B))<tol or fabs(360-fabs(ang_fim_A - self.contraAz(ang_fim_B)))<tol):
                            mergeou = True
                            break
                    if mergeou:
                        geom_A = QgsGeometry.fromPolylineXY(coord_A)
                        geom_B = QgsGeometry.fromPolylineXY(coord_B)
                        new_geom = geom_A.combine(geom_B)

                        length_A = geom_A.length()
                        length_B = geom_B.length()
                        if length_A > length_B:
                            att = att_A
                        else:
                            att = att_B
                        new_feat = QgsFeature()
                        new_feat.setAttributes(att)
                        new_feat.setGeometry(new_geom)

                        if new_geom.isMultipart():
                            nova_lista += [[coord_A, att_A], [coord_B, att_B]]
                            del lista[i], lista[j-1]
                            break
                        else:
                            del lista[i], lista[j-1]
                            lista = self.pontos_ang(new_feat)+lista
                            break
                    if not(mergeou):
                        # Tirar a geometria que nao se conecta com nada da lista
                        nova_lista += [[coord_A, att_A]]
                        del lista[i]
                        break
                if len(lista)==1:
                    nova_lista += [[lista[0][0], lista[0][5]]]

        # Criando o shapefile de saida
        feedback.pushInfo(self.tr('Saving output...', 'Salvando saída...'))
        n_pnts = len(nova_lista)
        total = 100.0 /n_pnts if n_pnts else 0
        for k, item in enumerate(nova_lista):
            fet = QgsFeature()
            fet.setGeometry(QgsGeometry.fromPolylineXY(item[0]))
            fet.setAttributes(item[1])
            sink.addFeature(fet, QgsFeatureSink.FastInsert)
            if feedback.isCanceled():
                break
            feedback.setProgress(int((k+1) * total))

        feedback.pushInfo(self.tr('Operation completed successfully!', 'Operação finalizada com sucesso!'))
        feedback.pushInfo(self.tr('Leandro Franca - Cartographic Engineer', 'Leandro França - Eng Cart'))

        return {self.OUTPUT: dest_id}

    def pontos_ang(self, feature):
            att = feature.attributes()
            geom = feature.geometry()
            if not geom.isMultipart():
                coord = geom.asPolyline()
                # Tangente entre o primeiro e segundo ponto
                Xa = coord[0].x()
                Xb = coord[1].x()
                Ya = coord[0].y()
                Yb = coord[1].y()
                ang_ini = degrees(atan2(Yb-Ya,Xb-Xa))
                Xa = coord[-2].x()
                Xb = coord[-1].x()
                Ya = coord[-2].y()
                Yb = coord[-1].y()
                ang_fim = degrees(atan2(Yb-Ya,Xb-Xa))
                return [[coord, coord[0], coord[-1], ang_ini, ang_fim, att]]
            else:
                coord = geom.asMultiPolyline()
                itens = []
                for item in coord:
                    Xa = item[0].x()
                    Xb = item[1].x()
                    Ya = item[0].y()
                    Yb = item[1].y()
                    ang_ini = degrees(atan2(Yb-Ya,Xb-Xa))
                    Xa = item[-2].x()
                    Xb = item[-1].x()
                    Ya = item[-2].y()
                    Yb = item[-1].y()
                    ang_fim = degrees(atan2(Yb-Ya,Xb-Xa))
                    itens += [[item, item[0], item[-1], ang_ini, ang_fim, att]]
                return itens

    # Funcao para dar a direcao oposta
    def contraAz(self, x):
        if x<=0:
            return x+180
        else:
            return x-180
