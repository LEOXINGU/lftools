# -*- coding: utf-8 -*-

"""
Easy_measures_layers.py
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
__date__ = '2019-10-06'
__copyright__ = '(C) 2020, Leandro França'

from PyQt5.QtCore import QCoreApplication, QVariant
from qgis.core import *
from lftools.geocapt.imgs import Imgs
import os
from qgis.PyQt.QtGui import QIcon

class MeasureLayers(QgsProcessingAlgorithm):

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
        return MeasureLayers()

    def name(self):
        return 'measure_layers'

    def displayName(self):
        return self.tr('Measure layers', 'Medir camadas')

    def group(self):
        return self.tr('Easy', 'Mão na Roda')

    def groupId(self):
        return 'easy'

    def tags(self):
        return self.tr('measure,layer,area,perimeter,length,multiple,feet,meters,km,square,SGL,LTP,units').split(',')

    def icon(self):
        return QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images/easy.png'))

    txt_en = """This tool calculates the line feature's lengths and polygon feature's perimeter and area in virtual fields for all vector layers."""
    txt_pt = 'Esta ferramenta calcula em campos virtuais os comprimentos de feições do tipo linha e o perímetro e área de feições do tipo polígono para todas as camadas.'
    figure = 'images/tutorial/easy_measure_layer.jpg'

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

    DISTANCE = 'DISTANCE'
    AREA = 'AREA'
    PRECISION = 'PRECISION'
    LAYERS = 'LAYERS'
    TYPE = 'TYPE'

    def initAlgorithm(self, config=None):
        units_dist = [self.tr('Meters (m)', 'Metros (m)'),
                      self.tr('Feet (ft)', 'Pés (ft)'),
                      self.tr('Yards (yd)', 'Jardas (Yd)'),
                      self.tr('Kilometers (Km)', 'Quilômetros (Km)'),
                      self.tr('Miles (mi)', 'Milhas (mi)')
               ]
        units_area = [self.tr('Square Meters (m²)', 'Metros quadrados (m²)'),
                      self.tr('Hectares (ha)', 'Hectares (ha)'),
                      self.tr('Square Kilometers (Km²)', 'Quilômetros quadrados (Km²)')
               ]

        self.addParameter(
            QgsProcessingParameterMultipleLayers(
                self.LAYERS,
                self.tr('Layers', 'Camadas'),
                layerType = QgsProcessing.TypeVectorAnyGeometry
            )
        )

        self.addParameter(
            QgsProcessingParameterEnum(
                self.DISTANCE,
                self.tr('Distance Units', 'Unidade de distância'),
				options = units_dist,
                defaultValue= 0
            )
        )

        self.addParameter(
            QgsProcessingParameterEnum(
                self.AREA,
                self.tr('Area Units', 'Unidade de Área'),
				options = units_area,
                defaultValue= 0
            )
        )

        self.addParameter(
            QgsProcessingParameterNumber(
                self.PRECISION,
                self.tr('Precision', 'Precisão'),
                type = QgsProcessingParameterNumber.Type.Integer, # float = 1 and integer = 0
                defaultValue = 4
            )
        )

        tipo = [self.tr('Ellipsoid', 'Elipsoidal'),
                 self.tr('Cartesian / Projected', 'Cartesiano / Projetado'),
                 self.tr('Local Tangent Plane - LTP', 'Sistema Geodésico Local - SGL')]

        self.addParameter(
            QgsProcessingParameterEnum(
                self.TYPE,
                self.tr('Calculation', 'Cálculo'),
				options = tipo,
                defaultValue = 0
            )
        )

    def processAlgorithm(self, parameters, context, feedback):

        units_dist = self.parameterAsEnum(
            parameters,
            self.DISTANCE,
            context
        )

        units_area = self.parameterAsEnum(
            parameters,
            self.AREA,
            context
        )

        precisao = self.parameterAsInt(
            parameters,
            self.PRECISION,
            context
        )

        formula = self.parameterAsEnum(
            parameters,
            self.TYPE,
            context
        )

        # Transformação de unidades
        unid_transf_dist = [1, 0.3048, 0.9144, 1000, 621.4]
        unid_abb_dist = ['m', 'ft', 'yd', 'Km', 'mi']
        unid_transf_area = [1.0, 1e4, 1e6]
        unid_abb_area = ['m²', 'ha', 'Km²']
        unidade_dist = unid_transf_dist[units_dist]
        unidade_area = unid_transf_area[units_area]

        formula_tipo = [self.tr('ellip', 'elip'), self.tr('cart'), self.tr('LTP', 'SGL')][formula]

        field_length = QgsField( self.tr('length', 'comprimento')+ '_' + formula_tipo + '_' + unid_abb_dist[units_dist], QVariant.Double, "numeric", 14, precisao)
        field_perimeter = QgsField( self.tr('perimeter', 'perímetro') + '_'  + formula_tipo + '_' + unid_abb_dist[units_dist], QVariant.Double, "numeric", 14, precisao)
        field_area = QgsField( self.tr('area', 'área') + '_'  + formula_tipo + '_' + unid_abb_area[units_area], QVariant.Double, "numeric", 14, precisao)

        camadas = [layer.name() for layer in QgsProject.instance().mapLayers().values()]
        num_camadas = len(camadas)
        total = 100.0 / num_camadas if num_camadas else 0

        #layers = QgsProject.instance().mapLayers()
        layers = self.parameterAsLayerList(
            parameters,
            self.LAYERS,
            context
        )

        for current, layer in enumerate(layers):

            if layer.type() == 0:# VectorLayer
                if formula in [0,1]: # Elipsoidal e Cartográfica
                    formula_length = ['$length', 'length($geometry)'][formula]
                    formula_perimeter = ['$perimeter', 'perimeter($geometry)'][formula]
                    formula_area = ['$area', 'area($geometry)'][formula]

                elif formula == 2: # SGL
                    formula_length = "lengthLTP('{}', '2d')".format(layer.id())
                    formula_area = "areaLTP('{}')".format(layer.id())
                    formula_perimeter = "perimeterLTP('{}')".format(layer.id())

                if layer.geometryType() == QgsWkbTypes.LineGeometry:
                    layer.addExpressionField(formula_length + '/' + str(unidade_dist), field_length)
                if layer.geometryType() == QgsWkbTypes.PolygonGeometry:
                    layer.addExpressionField(formula_perimeter + '/' + str(unidade_dist), field_perimeter)
                    layer.addExpressionField(formula_area + '/' + str(unidade_area), field_area)

            if feedback.isCanceled():
                break
            feedback.setProgress(int((current+1) * total))

        feedback.pushInfo(self.tr('Operation completed successfully!', 'Operação finalizada com sucesso!'))
        feedback.pushInfo(self.tr('Leandro Franca - Cartographic Engineer', 'Leandro França - Eng Cart'))

        return {}
