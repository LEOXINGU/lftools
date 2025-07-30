# -*- coding: utf-8 -*-

"""
Easy_SelectByKeyAtt.py
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
__date__ = '2024-11-10'
__copyright__ = '(C) 2024, Leandro França'

from PyQt5.QtCore import QCoreApplication, QVariant
from qgis.core import *
import numpy as np
from pyproj.crs import CRS
from lftools.geocapt.imgs import Imgs
from lftools.geocapt.cartography import LayerIs3D
from lftools.translations.translate import translate
from lftools.geocapt.dip import Interpolar
import os, processing
from qgis.PyQt.QtGui import QIcon

class SelectByKeyAtt(QgsProcessingAlgorithm):

    LOC = QgsApplication.locale()[:2]

    def tr(self, *string):
        return translate(string, self.LOC)

    def createInstance(self):
        return SelectByKeyAtt()

    def name(self):
        return 'SelectByKeyAtt'.lower()

    def displayName(self):
        return self.tr('Select by key attribute', 'Selecionar por atributo chave')

    def group(self):
        return self.tr('Easy', 'Mão na Roda')

    def groupId(self):
        return 'easy'

    def tags(self):
        return 'GeoOne,selecionar,pimary,key,foreing,estrangeira,chave,selected,relação,relation'.split(',')

    def icon(self):
        return QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images/easy.png'))

    txt_en = '''This tool allows you to select features that share the same foreign key attribute from multiple layers based on the primary key attribute of a selected feature from another layer.
    Note: Enter the foreign key field name if it is not the same as the primary key field name.'''
    txt_pt = '''Esta ferramenta permite selecionar feições que compartilham o mesmo atributo de chave estrangeira de diversas camadas com base no atributo de chave primária de uma feição selecionada de outra camada.
    Nota: Insira o nome do campo de chave estrangeira se não for igual ao nome do campo de chave primária.'''
    figure = 'images/tutorial/easy_selectByKey.jpg'

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

    PRIMARY = 'PRIMARY'
    PRIMARY_FIELD = 'PRIMARY_FIELD'
    FOREIGNS ='FOREIGNS'
    FOREIGNS_FIELD = 'FOREIGNS_FIELD'

    def initAlgorithm(self, config=None):

        # INPUT
        self.addParameter(
            QgsProcessingParameterVectorLayer(
                self.PRIMARY,
                self.tr('Input Layer', 'Camada de entrada'),
                [QgsProcessing.TypeVectorAnyGeometry]
            )
        )

        self.addParameter(
            QgsProcessingParameterField(
                self.PRIMARY_FIELD,
                self.tr('Primary key', 'Chave primária'),
                parentLayerParameterName = self.PRIMARY
            )
        )

        self.addParameter(
            QgsProcessingParameterMultipleLayers(
                self.FOREIGNS,
                self.tr('Layers', 'Camadas'),
                layerType = QgsProcessing.TypeVectorAnyGeometry
            )
        )

        self.addParameter(
            QgsProcessingParameterString(
                self.FOREIGNS_FIELD,
                self.tr('Foreign key', 'Chave estrangeira'),
                optional = True
            )
        )


    def processAlgorithm(self, parameters, context, feedback):

        camada = self.parameterAsVectorLayer(
            parameters,
            self.PRIMARY,
            context
        )
        if camada is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.PRIMARY))

        campo = self.parameterAsFields(
            parameters,
            self.PRIMARY_FIELD,
            context
        )
        if campo is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.PRIMARY_FIELD))

        # Verificar se existe apenas uma feição selecionada
        if camada.selectedFeatureCount() != 1:
            raise QgsProcessingException(self.tr('At least one feature must be selected!', 'Pelo menos uma feição deve ser selecionada!'))

        campo_indice_pk = camada.fields().indexFromName(campo[0])
        campo_nome_pk = campo[0]

        layers = self.parameterAsLayerList(
            parameters,
            self.FOREIGNS,
            context
        )

        campo_nome_fk = self.parameterAsString(
            parameters,
            self.FOREIGNS_FIELD,
            context
        )

        if campo_nome_fk is None or campo_nome_fk == '':
            campo_nome_fk = campo_nome_pk

        # Obtendo o atributo chave
        for feat in camada.getSelectedFeatures():
            att = feat[campo_nome_pk]

        # Expressão para seleção
        expressao =  QgsExpression('"{}" = \'{}\''.format(campo_nome_fk, att))

        for layer in layers:
            if campo_nome_fk in [field.name() for field in layer.fields()]:
                ids_selecionados = []
                for feat in layer.getFeatures(QgsFeatureRequest(expressao)):
                    ids_selecionados.append(feat.id())
                layer.selectByIds(ids_selecionados)
            else:
                feedback.pushInfo(self.tr('Layer {} has no key field!', 'A camada {} não possui campo chave!').format(layer.name()))

        feedback.pushInfo(self.tr('Operation completed successfully!', 'Operação finalizada com sucesso!'))
        feedback.pushInfo(self.tr('Leandro Franca - Cartographic Engineer', 'Leandro França - Eng Cart'))

        return {}
