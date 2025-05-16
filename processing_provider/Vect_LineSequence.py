# -*- coding: utf-8 -*-

"""
Vect_LineSequence.py
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
__date__ = '2023-01-06'
__copyright__ = '(C) 2023, Leandro França'

from qgis.PyQt.QtCore import QCoreApplication, QVariant
from qgis.core import (QgsApplication,
                       QgsProcessingParameterVectorLayer,
                       QgsGeometry,
                       QgsField,
                       QgsProcessing,
                       QgsProject,
                       QgsProcessingParameterField,
                       QgsProcessingParameterEnum,
                       QgsProcessingParameterBoolean,
                       QgsProcessingParameterNumber,
                       QgsProcessingParameterString,
                       QgsFeatureSink,
                       QgsProcessingException,
                       QgsProcessingAlgorithm,
                       QgsCoordinateTransform,
                       QgsProcessingParameterFeatureSink)
from lftools.geocapt.imgs import Imgs
from lftools.translations.translate import translate
import os
from qgis.PyQt.QtGui import QIcon

class LineSequence(QgsProcessingAlgorithm):

    LOC = QgsApplication.locale()[:2]

    def tr(self, *string):
        return translate(string, self.LOC)

    def createInstance(self):
        return LineSequence()

    def name(self):
        return 'linesequence'

    def displayName(self):
        return self.tr('Line sequence', 'Sequenciar linhas')

    def group(self):
        return self.tr('Vector', 'Vetor')

    def groupId(self):
        return 'vector'

    def tags(self):
        return self.tr('sequence,lines,order,ordenar,orientar').split(',')

    def icon(self):
        return QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images/vetor.png'))

    txt_en = 'This tool assigns a sequential value to connected line features based on their topological order. It is ideal for mapping drainage networks, road segments, pipelines, irrigation systems, or any linear vector structure where directional order matters. Users can define the sequence direction (forward, reverse, or both), group by an attribute field, and set a spatial tolerance for node connection. The result is written directly to the layer in custom fields.'
    txt_pt = 'Esta ferramenta permite atribuir um valor sequencial a feições lineares conectadas, com base na ordem de conectividade entre elas. Ideal para aplicações em redes de drenagem, sistemas de irrigação, estradas, dutos e qualquer estrutura vetorial linear em que a sequência seja relevante. É possível definir o sentido da numeração (vante, ré ou ambos), aplicar agrupamentos por campo de atributo e ajustar a tolerância espacial para conexão entre os vértices. O resultado é armazenado diretamente na camada, em campos personalizados.'
    figure = 'images/tutorial/vect_line_sequence.jpg'

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

    LINHAS = 'LINHAS'
    SELECTEDLINES = 'SELECTEDLINES'
    GROUP = 'GROUP'
    NAME = 'NAME'
    TYPE = 'TYPE'
    FIELD = 'FIELD'
    OPTION = 'OPTION'
    TOLERANCE = 'TOLERANCE'
    SAVE = 'SAVE'

    def initAlgorithm(self, config=None):
        self.addParameter(
            QgsProcessingParameterVectorLayer(
                self.LINHAS,
                self.tr('Line layer', 'Camada de linhas'),
                [QgsProcessing.TypeVectorLine]
            )
        )

        self.addParameter(
            QgsProcessingParameterBoolean(
                self.SELECTEDLINES,
                self.tr('Only selected line', 'Apenas linhas selecionadas'),
                defaultValue = False
            )
        )

        self.addParameter(
            QgsProcessingParameterString(
                self.NAME,
                self.tr('Sequence Field', 'Campo de sequência'),
                defaultValue = self.tr('sequence', 'sequência')
            )
        )

        tipos = [self.tr('Forward', 'Vante'),
                  self.tr('Reverse', 'Ré'),
                  self.tr('Both', 'Ambos')]

        self.addParameter(
            QgsProcessingParameterEnum(
                self.TYPE,
                self.tr('Type', 'Tipo'),
				options = tipos,
                defaultValue = 0
            )
        )

        self.addParameter(
            QgsProcessingParameterField(
                self.FIELD,
                self.tr('Group Field', 'Campo de agrupamento'),
                parentLayerParameterName=self.LINHAS,
                optional = True
            )
        )

        self.addParameter(
            QgsProcessingParameterNumber(
                self.TOLERANCE,
                self.tr('Tolerance (m)', 'Tolerância (m)'),
                type = QgsProcessingParameterNumber.Type.Double,
                defaultValue = 0.25,
                minValue = 0.001
                )
            )

        self.addParameter(
            QgsProcessingParameterBoolean(
                self.SAVE,
                self.tr('Save Editions', 'Salvar Edições'),
                defaultValue = True
            )
        )

    def processAlgorithm(self, parameters, context, feedback):

        layer = self.parameterAsVectorLayer(
            parameters,
            self.LINHAS,
            context
        )
        if layer is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.LINHAS))

        nome = self.parameterAsString(
            parameters,
            self.NAME,
            context
        )

        tipo = self.parameterAsEnum(
            parameters,
            self.TYPE,
            context
        )

        campo = self.parameterAsFields(
            parameters,
            self.FIELD,
            context
        )

        temGrupo = False if campo == [] else True


        lin_selecionadas = self.parameterAsBool(
            parameters,
            self.SELECTEDLINES,
            context
        )

        tol = self.parameterAsDouble(
            parameters,
            self.TOLERANCE,
            context
        )

        if layer.crs().isGeographic():
            tol /= 111000

        # Cria campos dinamicamente conforme tipo escolhido
        campos_existentes = [field.name() for field in layer.fields()]
        novos_campos = []
        DP = layer.dataProvider()

        if tipo == 0 or tipo == 2:  # Vante ou Ambos
            if nome not in campos_existentes:
                DP.addAttributes([QgsField(nome,  QVariant.Int)])
                novos_campos.append(nome)
        if tipo == 1 or tipo == 2:  # Ré ou Ambos
            nome_inv = nome + '_inv'
            if nome_inv not in campos_existentes:
                DP.addAttributes([QgsField(nome_inv,  QVariant.Int)])
                novos_campos.append(nome_inv)
        if novos_campos:
            layer.updateFields()

        # Agrupar por campo, se existir
        grupos = {}
        for feat in layer.getSelectedFeatures() if lin_selecionadas else layer.getFeatures():
            if temGrupo:
                val = feat[campo[0]]
            else:
                val = 'all'
            if val not in grupos:
                grupos[val] = []
            grupos[val].append(feat)

        # Análise de conectividade por grupo
        layer.startEditing()
        for grupo in grupos:
            feats = grupos[grupo]
            # Construir dicionário de conectividade para o grupo
            linhas = {}
            for featA in feats:
                mont = None
                jus = None
                geomA = featA.geometry()
                if geomA.isEmpty():
                    continue
                if geomA.isMultipart():
                    coordsA = geomA.asMultiPolyline()[0]
                else:
                    coordsA = geomA.asPolyline()
                pnt_iniA = QgsGeometry().fromPointXY(coordsA[0])
                pnt_fimA = QgsGeometry().fromPointXY(coordsA[-1])

                for featB in feats:
                    if featA.id() == featB.id():
                        continue
                    geomB = featB.geometry()
                    if geomB.isEmpty():
                        continue
                    if geomB.isMultipart():
                        coordsB = geomB.asMultiPolyline()[0]
                    else:
                        coordsB = geomB.asPolyline()
                    pnt_iniB = QgsGeometry().fromPointXY(coordsB[0])
                    pnt_fimB = QgsGeometry().fromPointXY(coordsB[-1])

                    if pnt_iniA.intersects(pnt_fimB.buffer(tol,5)):
                        mont = featB.id()
                    elif pnt_fimA.intersects(pnt_iniB.buffer(tol,5)):
                        jus = featB.id()
                    if mont and jus:
                        break
                linhas[featA.id()] = {'mont': mont, 'jus': jus}

            # Validar conectividade
            ids = list(linhas.keys())
            primeiros = [fid for fid in ids if linhas[fid]['mont'] is None]
            ultimos = [fid for fid in ids if linhas[fid]['jus'] is None]
            intermediarios = [fid for fid in ids if linhas[fid]['mont'] is not None and linhas[fid]['jus'] is not None]
            if len(primeiros) != 1 or len(ultimos) != 1 or (len(primeiros) + len(ultimos) + len(intermediarios) != len(linhas)):
                raise QgsProcessingException(self.tr('Check the connectivity between the lines or increase the tolerance value!', 'Verifique a conectividade entre as linhas ou aumente o valor da tolerância!'))

            # Sequência direta (vante)
            if tipo == 0 or tipo == 2:
                seq = []
                atual = primeiros[0]
                while atual:
                    seq.append(atual)
                    atual = linhas[atual]['jus']

                for k, id in enumerate(seq):
                    layer.changeAttributeValue(id, layer.fields().indexFromName(nome), k+1)

            # Sequência inversa (ré)
            if tipo == 1 or tipo == 2:
                seq_inv = []
                atual = ultimos[0]
                while atual:
                    seq_inv.append(atual)
                    atual = linhas[atual]['mont']

                nome_inv = nome + '_inv'
                for k, id in enumerate(seq_inv):
                    layer.changeAttributeValue(id, layer.fields().indexFromName(nome_inv), k+1)

        # Salvar edições se selecionado
        salvar = self.parameterAsBool(parameters, self.SAVE, context)
        if salvar:
            layer.commitChanges()

        feedback.pushInfo(self.tr('Operation completed successfully!', 'Operação finalizada com sucesso!'))
        feedback.pushInfo(self.tr('Leandro Franca - Cartographic Engineer', 'Leandro França - Eng Cart'))

        return {}
