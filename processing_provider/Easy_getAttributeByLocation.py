# -*- coding: utf-8 -*-

"""
Easy_getAttributeByLocation.py
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
__date__ = '2022-01-02'
__copyright__ = '(C) 2022, Leandro França'

from PyQt5.QtCore import QCoreApplication, QVariant
from qgis.core import *
import processing
from lftools.geocapt.imgs import Imgs
from lftools.translations.translate import translate
from lftools.geocapt.cartography import reprojectPoints
import os
from qgis.PyQt.QtGui import QIcon


class GetAttributeByLocation(QgsProcessingAlgorithm):

    LOC = QgsApplication.locale()[:2]

    def tr(self, *string):
        return translate(string, self.LOC)

    def createInstance(self):
        return GetAttributeByLocation()

    def name(self):
        return 'getattributebylocation'

    def displayName(self):
        return self.tr('Get attribute by location', 'Pegar atributo pela localização')

    def group(self):
        return self.tr('Easy', 'Mão na Roda')

    def groupId(self):
        return 'easy'

    def tags(self):
        return 'GeoOne,easy,topologia,centroide,quadra,lote,parcel,setor,cadastro,cadastre,parcela,polígono'.split(',')

    def icon(self):
        return QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images/easy.png'))

    txt_en = '''This algorithm fills in the attributes of a specific field from another layer, in such a way that the feature's centroid intercepts the corresponding feature from the other layer.
The source and destination fields must be indicated to fill in the attributes.'''
    txt_pt = '''Este algoritmo preenche os atributos de um campo específico a partir de outra camada, tal que o centróide da feição intercepte a feição correspondente da outra camada.
Os campos de origem e de destino devem ser indicadas para preenchimento dos atributos.'''
    figure = 'images/tutorial/easy_get_attributes.jpg'

    SOURCE ='SOURCE'
    SOURCE_SELECTED = 'SOURCE_SELECTED'
    SOURCE_FIELD = 'SOURCE_FIELD'
    DEST = 'DEST'
    DEST_SELECTED = 'DEST_SELECTED'
    DEST_FIELD = 'DEST_FIELD'
    TOPOLOGY = 'TOPOLOGY'
    SAVE = 'SAVE'

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

    def initAlgorithm(self, config=None):
        # INPUT
        self.addParameter(
            QgsProcessingParameterVectorLayer(
                self.SOURCE,
                self.tr('Attribute source layer', 'Camada fonte de atributo'),
                [QgsProcessing.TypeVector]
            )
        )

        self.addParameter(
            QgsProcessingParameterBoolean(
                self.SOURCE_SELECTED,
                self.tr('Only selected', 'Apenas selecionados'),
                defaultValue= False
            )
        )

        self.addParameter(
            QgsProcessingParameterField(
                self.SOURCE_FIELD,
                self.tr('Source field', 'Campo de origem'),
                parentLayerParameterName=self.SOURCE
            )
        )

        self.addParameter(
        QgsProcessingParameterVectorLayer(
            self.DEST,
            self.tr('Target layer for attribute', 'Camada de destino para o atributo'),
            [QgsProcessing.TypeVector]
            )
        )

        self.addParameter(
            QgsProcessingParameterBoolean(
                self.DEST_SELECTED,
                self.tr('Only selected', 'Apenas selecionados'),
                defaultValue= False
            )
        )

        self.addParameter(
            QgsProcessingParameterField(
                self.DEST_FIELD,
                self.tr('Destination field', 'Campo de destino'),
                parentLayerParameterName=self.DEST
            )
        )

        tipos = [self.tr('from target feature','da feição alvo'),
                 self.tr('from origin feature','da feição de origem'),
               ]

        self.addParameter(
            QgsProcessingParameterEnum(
                self.TOPOLOGY,
                self.tr('Intersection with the centroid (Topology)', 'Interseção com o centróide (Topologia)'),
				options = tipos,
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

        lotes = self.parameterAsVectorLayer(
            parameters,
            self.SOURCE,
            context
        )
        if lotes is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.SOURCE))

        campo_lote = self.parameterAsFields(
            parameters,
            self.SOURCE_FIELD,
            context
        )
        if campo_lote is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.SOURCE_FIELD))

        edif = self.parameterAsVectorLayer(
            parameters,
            self.DEST,
            context
        )
        if edif is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.DEST))

        campo_edif = self.parameterAsFields(
            parameters,
            self.DEST_FIELD,
            context
        )
        if campo_edif is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.DEST_FIELD))

        columnIndex = edif.fields().indexFromName(campo_edif[0])
        att = campo_lote[0]
        edif.startEditing()

        topologia = self.parameterAsEnum(
            parameters,
            self.TOPOLOGY,
            context
        )

        selec_origem = self.parameterAsBool(
            parameters,
            self.SOURCE_SELECTED,
            context
        )

        selec_dest = self.parameterAsBool(
            parameters,
            self.DEST_SELECTED,
            context
        )

        feedback.pushInfo(self.tr('Source field: {}'.format(campo_lote[0]), 'Campo de origem: {}'.format(campo_lote[0])))
        feedback.pushInfo(self.tr('Destination field: {}'.format(campo_edif[0]), 'Campo de destino: {}\n'.format(campo_edif[0])))

        # Verificando SRC das camadas
        mesmoSRC = True
        if lotes.crs() != edif.crs():
            mesmoSRC = False
            if topologia == 0:
                coordinateTransformer = QgsCoordinateTransform()
                coordinateTransformer.setDestinationCrs(lotes.crs())
                coordinateTransformer.setSourceCrs(edif.crs())
            else:
                coordinateTransformer = QgsCoordinateTransform()
                coordinateTransformer.setDestinationCrs(edif.crs())
                coordinateTransformer.setSourceCrs(lotes.crs())

        # Criar índice espacial
        feedback.pushInfo(self.tr('Creating spatial index...', 'Criando índice espacial...'))
        if topologia == 0:
            index = QgsSpatialIndex(lotes.getFeatures())
            if selec_dest:
                total = 100.0 /edif.selectedFeatureCount() if edif.selectedFeatureCount()>0 else 0
            else:
                total = 100.0 /edif.featureCount() if edif.featureCount() else 0
        else:
            index = QgsSpatialIndex(edif.getFeatures())
            if selec_origem:
                total = 100.0 /lotes.selectedFeatureCount() if lotes.selectedFeatureCount()>0 else 0
            else:
                total = 100.0 /lotes.featureCount() if lotes.featureCount() else 0
        cont = 0

        # Preenchendo atributos
        feedback.pushInfo(self.tr('Filling attributes...', 'Preenchendo atributos...'))
        if topologia == 0:
            feicoes = {}
            for feat in lotes.getSelectedFeatures() if selec_origem else lotes.getFeatures():
                feicoes[feat.id()] = feat

            for feat1 in edif.getSelectedFeatures() if selec_dest else edif.getFeatures():
                centroide = feat1.geometry().centroid()
                if not mesmoSRC:
                    centroide = reprojectPoints(centroide, coordinateTransformer)
                bbox = centroide.boundingBox()
                feat_ids = index.intersects(bbox)
                for feat_id in feat_ids:
                    feat2 = feicoes[feat_id]
                    if centroide.intersects(feat2.geometry()):
                        valor = feat2[att]
                        edif.changeAttributeValue(feat1.id(), columnIndex, valor)
                        break
                    if feedback.isCanceled():
                        break
                cont += 1
                feedback.setProgress(int(cont * total))
        elif topologia == 1:
            feicoes = {}
            for feat in edif.getSelectedFeatures() if selec_dest else edif.getFeatures():
                feicoes[feat.id()] = feat

            for feat1 in lotes.getSelectedFeatures() if selec_origem else lotes.getFeatures():
                centroide = feat1.geometry().centroid()
                if not mesmoSRC:
                    centroide = reprojectPoints(centroide, coordinateTransformer)
                bbox = centroide.boundingBox()
                feat_ids = index.intersects(bbox)

                valor = feat1[att]
                for feat_id in feat_ids:
                    feat2 = feicoes[feat_id]
                    if centroide.intersects(feat2.geometry()):
                        edif.changeAttributeValue(feat2.id(), columnIndex, valor)
                        break
                    if feedback.isCanceled():
                        break
                cont += 1
                feedback.setProgress(int(cont * total))

        salvar = self.parameterAsBool(
            parameters,
            self.SAVE,
            context
        )
        if salvar is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.SAVE))

        if salvar:
            edif.commitChanges() # salva as edições

        feedback.pushInfo(self.tr('Operation completed successfully!', 'Operação finalizada com sucesso!'))
        feedback.pushInfo(self.tr('Leandro Franca - Cartographic Engineer', 'Leandro França - Eng Cart'))

        return {}
