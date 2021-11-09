# -*- coding: utf-8 -*-

"""
Vect_sequencePoints.py
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
__date__ = '2020-06-11'
__copyright__ = '(C) 2020, Leandro França'

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
import os
from qgis.PyQt.QtGui import QIcon

class SequencePoints(QgsProcessingAlgorithm):
    POINTS = 'POINTS'
    POLYGON = 'POLYGON'
    FIELD = 'FIELD'
    FIRST = 'FIRST'
    SAVE = 'SAVE'
    LOC = QgsApplication.locale()[:2]

    INPUT = 'INPUT'
    OUTPUT = 'OUTPUT'

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
        return SequencePoints()

    def name(self):
        return 'sequencepoints'

    def displayName(self):
        return self.tr('Sequence points', 'Sequenciar pontos')

    def group(self):
        return self.tr('Vector', 'Vetor')

    def groupId(self):
        return 'vector'

    def tags(self):
        return self.tr('sequence,reverse,vertex,point,organize,topography').split(',')

    def icon(self):
        return QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images/vetor.png'))

    txt_en = 'This script fills a certain attribute of the features of a layer of points according to its sequence in relation to the polygon of another layer.'
    txt_pt = 'Este script preenche um determinado atributo das feições de uma camada de pontos de acordo com sua sequência em relação ao polígono de outra camada.'
    figure = 'images/tutorial/vect_sequence_points.jpg'

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
        self.addParameter(
            QgsProcessingParameterVectorLayer(
                self.POINTS,
                self.tr('Points', 'Pontos'),
                [QgsProcessing.TypeVectorPoint]
            )
        )

        self.addParameter(
            QgsProcessingParameterField(
                self.FIELD,
                self.tr('Sequence Field', 'Campo de ordenação dos vértices'),
                parentLayerParameterName=self.POINTS,
                type=QgsProcessingParameterField.Numeric
            )
        )

        self.addParameter(
            QgsProcessingParameterVectorLayer(
                self.POLYGON,
                self.tr('Polygon', 'Polígono'),
                [QgsProcessing.TypeVectorPolygon]
            )
        )

        opcoes = [self.tr('Polygon sequence','Sequência do polígono'),
				  self.tr('Northmost','Mais ao Norte'),
				  self.tr('Southernmost','Mais ao Sul'),
				  self.tr('Eastmost','Mais ao Leste'),
				  self.tr('Westmost','Mais ao Oeste')
               ]

        self.addParameter(
            QgsProcessingParameterEnum(
                self.FIRST,
                self.tr('First point', 'Primeiro Ponto'),
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

        pontos = self.parameterAsVectorLayer(
            parameters,
            self.POINTS,
            context
        )
        if pontos is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.POINTS))

        poligono = self.parameterAsVectorLayer(
            parameters,
            self.POLYGON,
            context
        )
        if poligono is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.POLYGON))

        campo = self.parameterAsFields(
            parameters,
            self.FIELD,
            context
        )
        if campo is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.FIELD))

        columnIndex = pontos.fields().indexFromName(campo[0])

        primeiro = self.parameterAsEnum(
            parameters,
            self.FIRST,
            context
        )

        # As duas camadas devem ter o mesmo SRC
        if poligono.crs() != pontos.crs():
            raise QgsProcessingException(self.tr('Both layers must have the same CRS!', 'As duas camadas devem ter o mesmo SRC!'))

        # Camada de polígonos deve ter apenas 1 polígono
        if poligono.featureCount() != 1:
            raise QgsProcessingException(self.tr('Polygon layer must have only 1 feature!', 'A camada do tipo polígono deve ter apenas 1 feição!'))

        for feat in poligono.getFeatures():
            pol = feat.geometry()

        if pol.isMultipart():
            coords = pol.asMultiPolygon()[0][0]
        else:
            coords = pol.asPolygon()[0]
        coords = coords[:-1]

        if primeiro == 1: #Mais ao norte
            ind = None
            ymax = -1e10
            for k, pnt in enumerate(coords):
                print(k, round(pnt.y(),2))
                if pnt.y() > ymax:
                    ymax = pnt.y()
                    ind = k
            coords = coords[ind :] + coords[0 : ind]

        elif primeiro == 2: #Mais ao sul
            ind = None
            ymin = 1e10
            for k, pnt in enumerate(coords):
                print(k, round(pnt.y(),2))
                if pnt.y() < ymin:
                    ymin = pnt.y()
                    ind = k
            coords = coords[ind :] + coords[0 : ind]

        elif primeiro == 3: #Mais ao Leste
            ind = None
            xmax = -1e10
            for k, pnt in enumerate(coords):
                print(k, round(pnt.x(),2))
                if pnt.x() > xmax:
                    xmax = pnt.x()
                    ind = k
            coords = coords[ind :] + coords[0 : ind]

        elif primeiro == 4: #Mais ao Oeste
            ind = None
            xmin = 1e10
            for k, pnt in enumerate(coords):
                print(k, round(pnt.x(),2))
                if pnt.x() < xmin:
                    xmin = pnt.x()
                    ind = k
            coords = coords[ind :] + coords[0 : ind]

        # Número de vértices do ponlígono deve ser igual ao número de pontos
        if (len(coords)) != pontos.featureCount():
            raise QgsProcessingException(self.tr('The number of points must equal the number of vertices of the polygon!', 'O número de pontos deve ser igual ao número de vértices do polígono!'))


        pontos.startEditing() # coloca no modo edição
        total = 100.0 / (len(coords))

        def norma1(p1, p2):
            return abs(p1.x() - p2.x()) + abs(p1.y() - p2.y())

        for cont, vertice in enumerate(coords):
            dist1 = 1e9
            pnt_id = None
            for feat in pontos.getFeatures():
                pnt = feat.geometry().asPoint()
                if norma1(vertice, pnt) < dist1:
                    dist1 = norma1(vertice, pnt)
                    pnt_id = feat.id()
            pontos.changeAttributeValue(pnt_id, columnIndex, cont+1)
            feedback.setProgress(int((cont+1) * total))

        salvar = self.parameterAsBool(
            parameters,
            self.SAVE,
            context
        )
        if salvar is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.SAVE))

        if salvar:
            pontos.commitChanges() # salva as edições

        feedback.pushInfo(self.tr('Operation completed successfully!', 'Operação finalizada com sucesso!'))
        feedback.pushInfo(self.tr('Leandro Franca - Cartographic Engineer', 'Leandro França - Eng Cart'))

        return {}
