# -*- coding: utf-8 -*-

"""
Cad_GeoNumbering.py
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

from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (QgsApplication,
                       QgsProcessingParameterVectorLayer,
                       QgsGeometry,
                       QgsProcessing,
                       QgsProcessingParameterField,
                       QgsProcessingParameterEnum,
                       QgsProcessingParameterBoolean,
                       QgsFeatureSink,
                       QgsProcessingException,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterFeatureSink)
from lftools.geocapt.imgs import Imgs
import numpy as np
import os
from qgis.PyQt.QtGui import QIcon

class GeoNumbering(QgsProcessingAlgorithm):

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
        return GeoNumbering()

    def name(self):
        return 'geonumbering'

    def displayName(self):
        return self.tr('Geographic Numbering', 'Numerar geograficamente')

    def group(self):
        return self.tr('Cadastre', 'Cadastro')

    def groupId(self):
        return 'cadastro'

    def tags(self):
        return self.tr('cadastro,geographic,sequence,north,south,east,west,number,code,codificar,organize,system').split(',')

    def icon(self):
        return QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images/cadastre.png'))

    txt_en = '''This tool fills in a numeric attribute following a geographic criterion, for example: from north to south and west to east.
Note: This algorithm uses the feature centroid to sort geographically.'''
    txt_pt = '''Esta ferramenta preenche um atributo numérico seguindo um critério geográfico, por exemplo de norte para sul e oeste para leste.
Obs.: Este algoritmo utiliza o centroide da feição para ordenar geograficamente.'''
    figure = 'images/tutorial/cadastre_geonumbering.jpg'

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
    SELECTED = 'SELECTED'
    FIELD = 'FIELD'
    METHOD = 'METHOD'
    GROUP = 'GROUP'
    SAVE = 'SAVE'

    def initAlgorithm(self, config=None):
        self.addParameter(
            QgsProcessingParameterVectorLayer(
                self.INPUT,
                self.tr('Points', 'Pontos'),
                [QgsProcessing.TypeVectorAnyGeometry]
            )
        )

        self.addParameter(
            QgsProcessingParameterBoolean(
                self.SELECTED,
                self.tr('Only selected', 'Apenas selecionados'),
                defaultValue= False
            )
        )

        self.addParameter(
            QgsProcessingParameterField(
                self.FIELD,
                self.tr('Sequence Field', 'Campo de ordenação dos vértices'),
                parentLayerParameterName=self.INPUT
            )
        )

        self.addParameter(
            QgsProcessingParameterField(
                self.GROUP,
                self.tr('Group Field', 'Campo de Agrupamento'),
                parentLayerParameterName=self.INPUT,
                type=QgsProcessingParameterField.Any,
                optional=True
            )
        )

        opcoes = [self.tr('North to South, West to East','Norte para Sul, Oeste para Leste'),
				  self.tr('North to South, East to West','Norte para Sul, Leste para Oeste'),
				  self.tr('West to East, North to South','Oeste para Leste, Norte para Sul'),
				  self.tr('West to East, South to North','Oeste para Leste, Sul para Norte'),
				  self.tr('South to North, West to East','Sul para Norte, Oeste para Leste'),
                  self.tr('South to North, East to West','Sul para Norte, Leste para Oeste'),
                  self.tr('East to West, North to South','Leste para Oeste, Norte para Sul'),
                  self.tr('East to West, South to North','Leste para Oeste, Sul para Norte')
               ]

        self.addParameter(
            QgsProcessingParameterEnum(
                self.METHOD,
                self.tr('Method', 'Método'),
				options = opcoes,
                defaultValue= 0
            )
        )

        self.addParameter(
            QgsProcessingParameterBoolean(
                self.SAVE,
                self.tr('Save Editions', 'Salvar Edições'),
                defaultValue=False
            )
        )

    def processAlgorithm(self, parameters, context, feedback):

        layer = self.parameterAsVectorLayer(
            parameters,
            self.INPUT,
            context
        )
        if layer is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.INPUT))

        campo = self.parameterAsFields(
            parameters,
            self.FIELD,
            context
        )
        if campo is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.FIELD))

        columnIndex = layer.fields().indexFromName(campo[0])

        Campo_Agrupar = self.parameterAsFields(
            parameters,
            self.GROUP,
            context
        )
        if Campo_Agrupar:
            Campo_Agrupar = layer.fields().indexFromName(Campo_Agrupar[0])

        metodo = self.parameterAsEnum(
            parameters,
            self.METHOD,
            context
        )

        selecionados = self.parameterAsBool(
            parameters,
            self.SELECTED,
            context
        )

        dtype = [('id', int), ('x', float), ('y', float)]
        valores = []

        # Ler feições
        feedback.pushInfo(self.tr('Reading features...', 'Lendo feições...'))
        if Campo_Agrupar:
            cont_grupo = {}
            id_grupo = {}
        for feat in layer.getSelectedFeatures() if selecionados else layer.getFeatures():
            geom = feat.geometry().centroid()
            id = feat.id()
            x = geom.asPoint().x() * (1 if metodo in [0,2,3,4] else -1)
            y = geom.asPoint().y() * (1 if metodo in [3,4,5,7] else -1)
            valores += [(id, x, y)]
            if Campo_Agrupar:
                valor_grupo = feat[Campo_Agrupar]
                id_grupo[id] = valor_grupo
                if valor_grupo not in cont_grupo:
                    cont_grupo[valor_grupo] = 0

        estr = np.array(valores, dtype=dtype)
        feedback.pushInfo(self.tr('Sorting the features...', 'Ordenando as feições...'))
        if metodo in [2,3,6,7]:
            ordenado = np.sort(estr, order=['x', 'y'])
        else:
            ordenado = np.sort(estr, order=['y', 'x'])

        dic = {}
        if Campo_Agrupar:
            for k, ord in enumerate(ordenado):
                cont_grupo[id_grupo[ord[0]]] += 1
                dic[ord[0]] = cont_grupo[id_grupo[ord[0]]]
        else:
            for k, ord in enumerate(ordenado):
                dic[ord[0]] = k+1

        layer.startEditing()

        # Salvando resultado
        total = 100.0 /len(valores) if len(valores)!=0 else 0
        for cont, feat in enumerate(layer.getSelectedFeatures() if selecionados else layer.getFeatures()):
            id = feat.id()
            layer.changeAttributeValue(feat.id(), columnIndex, dic[id])
            feedback.setProgress(int((cont+1) * total))

        salvar = self.parameterAsBool(
            parameters,
            self.SAVE,
            context
        )
        if salvar is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.SAVE))

        if salvar:
            layer.commitChanges() # salva as edições

        feedback.pushInfo(self.tr('Operation completed successfully!', 'Operação finalizada com sucesso!'))
        feedback.pushInfo(self.tr('Leandro Franca - Cartographic Engineer', 'Leandro França - Eng Cart'))

        return {}
