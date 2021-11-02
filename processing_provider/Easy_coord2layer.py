# -*- coding: utf-8 -*-

"""
Easy_coord2layer.py
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
__date__ = '2019-11-02'
__copyright__ = '(C) 2019, Leandro França'

from PyQt5.QtCore import QCoreApplication, QVariant
from qgis.core import *
import processing
from lftools.geocapt.imgs import Imgs
import os
from qgis.PyQt.QtGui import QIcon


class CoordinatesToLayer(QgsProcessingAlgorithm):

    TABLE = 'TABLE'
    X = 'X'
    Y = 'Y'
    Z = 'Z'
    CRS = 'CRS'
    LAYER = 'LAYER'
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
        return CoordinatesToLayer()

    def name(self):
        return 'coord2layer'

    def displayName(self):
        return self.tr('Table to point layer', 'Planilha para camada de pontos')

    def group(self):
        return self.tr('Easy', 'Mão na Roda')

    def groupId(self):
        return 'easy'

    def tags(self):
        return self.tr('easy,coordinate,table,layer,spreadsheet,excel,calc,csv,import,points').split(',')

    def icon(self):
        return QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images/easy.png'))

    txt_en = 'Generates a <b>point layer</b> from a coordinate table, whether it comes from a Microsoft <b>Excel</b> spreadsheet (.xls), Open Document Spreadsheet (.ods), or even attributes from another layer.'
    txt_pt = 'Geração de uma camada de pontos a partir das coordenadas preenchidas em uma planilha do Excel (.xls) ou Open Document Spreadsheet (.ods), ou até mesmo, a partir dos atributos de outra camada.'
    figure = 'images/tutorial/easy_coord_layer.jpg'

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
            QgsProcessingParameterFeatureSource(
                self.TABLE,
                self.tr('Table with coordinates', 'Tabela com coordenadas'),
                [QgsProcessing.TypeVector]
            )
        )

        self.addParameter(
            QgsProcessingParameterField(
                self.X,
                self.tr('X Coordinate', 'Coordenada X'),
                parentLayerParameterName=self.TABLE,
                type=QgsProcessingParameterField.Numeric
            )
        )

        self.addParameter(
            QgsProcessingParameterField(
                self.Y,
                self.tr('Y Coordinate', 'Coordenada Y'),
                parentLayerParameterName=self.TABLE,
                type=QgsProcessingParameterField.Numeric
            )
        )

        self.addParameter(
            QgsProcessingParameterField(
                self.Z,
                self.tr('Z Coordinate', 'Coordenada Z'),
                parentLayerParameterName=self.TABLE,
                type=QgsProcessingParameterField.Numeric,
                optional = True
            )
        )

        self.addParameter(
            QgsProcessingParameterCrs(
                self.CRS,
                self.tr('CRS', 'SRC'),
                'ProjectCrs'))

        # OUTPUT
        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.LAYER,
                self.tr('Point Layer', 'Camada de Pontos')
            )
        )

    def processAlgorithm(self, parameters, context, feedback):

        table = self.parameterAsSource(
            parameters,
            self.TABLE,
            context
        )

        if table is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.TABLE))

        X_field = self.parameterAsFields(
            parameters,
            self.X,
            context
        )

        Y_field = self.parameterAsFields(
            parameters,
            self.Y,
            context
        )

        # Field index
        X_id = table.fields().indexFromName(X_field[0])
        Y_id = table.fields().indexFromName(Y_field[0])


        Z_field = self.parameterAsFields(
            parameters,
            self.Z,
            context
        )
        if Z_field:
            Z_id = table.fields().indexFromName(Z_field[0])

        CRS = self.parameterAsCrs(
            parameters,
            self.CRS,
            context
        )

        # OUTPUT
        Fields = table.fields()
        (sink, dest_id) = self.parameterAsSink(
            parameters,
            self.LAYER,
            context,
            Fields,
            QgsWkbTypes.Point,
            CRS
        )
        if sink is None:
            raise QgsProcessingException(self.invalidSinkError(parameters, self.LAYER))

        feature = QgsFeature()
        total = 100.0 / table.featureCount() if table.featureCount() else 0
        for current, feat in enumerate(table.getFeatures()):
            att = feat.attributes()
            X = att[X_id]
            Y = att[Y_id]
            if Z_field:
                Z = att[Z_id]
                geom = QgsGeometry(QgsPoint(float(X), float(Y), float(Z)))
            else:
                geom = QgsGeometry.fromPointXY(QgsPointXY(float(X), float(Y)))
            feature.setGeometry(geom)
            feature.setAttributes(att)
            sink.addFeature(feature, QgsFeatureSink.FastInsert)
            if feedback.isCanceled():
                break
            feedback.setProgress(int(current * total))

        feedback.pushInfo(self.tr('Operation completed successfully!', 'Operação finalizada com sucesso!'))
        feedback.pushInfo(self.tr('Leandro Franca - Cartographic Engineer', 'Leandro França - Eng Cart'))

        return {self.LAYER: dest_id}
