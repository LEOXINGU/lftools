# -*- coding: utf-8 -*-


"""
Vect_reverseVertexOrder.py
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
__date__ = '2020-02-14'
__copyright__ = '(C) 2021, Leandro França'

from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (QgsApplication,
                       QgsProcessingParameterVectorLayer,
                       QgsGeometry,
                       QgsProcessing,
                       QgsProcessingParameterField,
                       QgsProcessingParameterBoolean,
                       QgsFeatureSink,
                       QgsProcessingException,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterFeatureSink)
from lftools.geocapt.imgs import Imgs
from lftools.geocapt.cartography import inv_vertex_order
from lftools.translations.translate import translate
import os
from qgis.PyQt.QtGui import QIcon

class ReverseVertexOrder(QgsProcessingAlgorithm):

    LOC = QgsApplication.locale()[:2]

    def tr(self, *string):
        return translate(string, self.LOC)

    def createInstance(self):
        return ReverseVertexOrder()

    def name(self):
        return 'reversevertexorder'

    def displayName(self):
        return self.tr('Reverse vertex order', 'Inverter ordem dos vértices')

    def group(self):
        return self.tr('Vector', 'Vetor')

    def groupId(self):
        return 'vector'

    def tags(self):
        return 'GeoOne,sequence,reverse,vertex,point,organize,orientar,orientation,topography'.split(',')

    def icon(self):
        return QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images/vetor.png'))

    txt_en = 'Inverts vertex order for polygons and lines.'
    txt_pt = 'Inverte a ordem dos vértices para polígonos e linhas.'
    figure = 'images/tutorial/vect_reverse_vertex_sequence.jpg'

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
    SAVE = 'SAVE'

    def initAlgorithm(self, config=None):

        self.addParameter(
            QgsProcessingParameterVectorLayer(
                self.INPUT,
                self.tr('Input Layer', 'Camada de entrada'),
                [QgsProcessing.TypeVectorLine,
                 QgsProcessing.TypeVectorPolygon]
            )
        )

        self.addParameter(
            QgsProcessingParameterBoolean(
                self.SELECTED,
                self.tr('Only selected', 'Apenas feições selecionadas'),
                defaultValue=False
            )
        )

        self.addParameter(
            QgsProcessingParameterBoolean(
                self.SAVE,
                self.tr('Save Editions', 'Salvar Edições'),
                defaultValue=True
            )
        )

    def processAlgorithm(self, parameters, context, feedback):

        camada = self.parameterAsVectorLayer(
            parameters,
            self.INPUT,
            context
        )
        if camada is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.INPUT))

        selecionados = self.parameterAsBool(
            parameters,
            self.SELECTED,
            context
        )
        if selecionados is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.SELECTED))

        salvar = self.parameterAsBool(
            parameters,
            self.SAVE,
            context
        )
        if salvar is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.SAVE))

        camada.startEditing() # coloca no modo edição

        if not selecionados:
            total = 100.0 / camada.featureCount() if camada.featureCount() else 0
            for current, feat in enumerate(camada.getFeatures()):
                cont = 0
                geom = feat.geometry()
                new_geom = inv_vertex_order(geom)
                camada.changeGeometry(feat.id(), new_geom)
                feedback.setProgress(int(current * total))
        else:
            total = 100.0 / camada.selectedFeatureCount() if camada.selectedFeatureCount() else 0
            for current, feat in enumerate(camada.getSelectedFeatures()):
                cont = 0
                geom = feat.geometry()
                new_geom = inv_vertex_order(geom)
                camada.changeGeometry(feat.id(), new_geom)
                feedback.setProgress(int(current * total))

        if salvar:
            camada.commitChanges() # salva as edições

        feedback.pushInfo(self.tr('Operation completed successfully!', 'Operação finalizada com sucesso!'))
        feedback.pushInfo(self.tr('Leandro Franca - Cartographic Engineer', 'Leandro França - Eng Cart'))

        return {}
