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

from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (QgsApplication,
                       QgsGeometry,
                       QgsWkbTypes,
                       QgsFeature,
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
        return self.tr('cadastro,sequence,number,code,codificar,organize,system,lot,line,front,cadastre,street,borderer,testada,linha').split(',')

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

    def initAlgorithm(self, config=None):
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT,
                self.tr('Parcels', 'Lotes'),
                [QgsProcessing.TypeVectorPolygon]
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

        # Camada de Saída
        (sink, dest_id) = self.parameterAsSink(
            parameters,
            self.OUTPUT,
            context,
            lotes.fields(),
            QgsWkbTypes.LineString,
            lotes.sourceCrs()
        )
        if sink is None:
            raise QgsProcessingException(self.invalidSinkError(parameters, self.OUTPUT))

        # Colocar poligonos em lista
        linhas = []
        atributos = []
        for feat in lotes.getFeatures():
            geom = feat.geometry()
            att = feat.attributes()
            atributos += [att]
            if geom.isMultipart():
                linhas += [geom.asMultiPolygon()[0][0]]
            else:
                linhas += [geom.asPolygon()[0]]

        tam = len(linhas)

        total = 100.0 / lotes.featureCount() if lotes.featureCount() else 0
        feature = QgsFeature()

        # Calculando a diferenca para cada linha
        new_lines = []
        for current, i in enumerate(range(tam)):
            geom1 = QgsGeometry.fromPolylineXY(linhas[i])
            for j in range(tam):
                if i != j:
                    geom2 = QgsGeometry.fromPolylineXY(linhas[j])
                    if geom1.intersects(geom2):
                        differ = geom1.difference(geom2)
                        geom1 = differ
            if geom1.length() > 0:
                if geom1.isMultipart():
                    partes = geom1.asMultiPolyline()
                    for parte in partes:
                        new_lines += [parte]
                        geom = QgsGeometry.fromPolylineXY(parte)
                        feature.setGeometry(geom)
                        feature.setAttributes(atributos[i])
                        sink.addFeature(feature, QgsFeatureSink.FastInsert)
                else:
                    new_lines += [geom1.asPolyline()]
                    feature.setGeometry(geom1)
                    feature.setAttributes(atributos[i])
                    sink.addFeature(feature, QgsFeatureSink.FastInsert)
            if feedback.isCanceled():
                break
            feedback.setProgress(int(current * total))

        feedback.pushInfo(self.tr('Operation completed successfully!', 'Operação finalizada com sucesso!'))
        feedback.pushInfo(self.tr('Leandro Franca - Cartographic Engineer', 'Leandro França - Eng Cart'))

        return {self.OUTPUT: dest_id}
