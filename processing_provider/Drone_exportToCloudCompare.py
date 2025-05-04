# -*- coding: utf-8 -*-

"""
Drone_exportToCloudCompare.py
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
__date__ = '2025-05-03'
__copyright__ = '(C) 2025, Leandro França'

from qgis.PyQt.QtCore import QCoreApplication, QVariant
from qgis.core import (QgsApplication,
                       QgsProcessingParameterVectorLayer,
                       QgsProcessing,
                       QgsWkbTypes,
                       QgsFields,
                       QgsField,
                       QgsFeature,
                       QgsProcessingParameterField,
                       QgsProcessingParameterEnum,
                       QgsProcessingParameterNumber,
                       QgsProcessingParameterBoolean,
                       QgsProcessingParameterFileDestination,
                       QgsFeatureSink,
                       QgsProcessingException,
                       QgsProcessingAlgorithm,
                       QgsProcessingUtils,
                       QgsProcessingParameterFeatureSink)
from lftools.geocapt.imgs import Imgs
from lftools.geocapt.cartography import gerar_paleta_tematica
from lftools.translations.translate import translate
import os
from qgis.PyQt.QtGui import QIcon, QColor

class ExportToCloudCompare(QgsProcessingAlgorithm):

    LOC = QgsApplication.locale()[:2]

    def tr(self, *string):
        return translate(string, self.LOC)

    def createInstance(self):
        return ExportToCloudCompare()

    def name(self):
        return 'ExportToCloudCompare'.lower()

    def displayName(self):
        return self.tr('Generate GCP for CloudCompare', 'Gerar arquivo de GCP para o CloudCompare')

    def group(self):
        return self.tr('Drones')

    def groupId(self):
        return 'drones'

    def tags(self):
        return self.tr('drones,cc,fotografia,photography,gcp,copy,points,control,ground,quality,homologous,controle,terreno').split(',')

    def icon(self):
        return QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images/drone.png'))

    txt_en = 'Generate text file with Ground Control Points (GCP) from a point layer to CloudCompare.'
    txt_pt = 'Gera arquivo texto com Pontos de Controle no Terreno (GCP) a partir de uma camada de pontos para o CloudCompare.'
    figure = 'images/tutorial/drone_createGCP.jpg'

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

    POINTS = 'POINTS'
    NAME = 'NAME'
    FILE = 'FILE'
    DECIMAL = 'DECIMAL'
    LAYER = 'LAYER'

    def initAlgorithm(self, config=None):
        self.addParameter(
            QgsProcessingParameterVectorLayer(
                self.POINTS,
                self.tr('Point Layer', 'Camada de Pontos'),
                [QgsProcessing.TypeVectorPoint]
            )
        )

        self.addParameter(
            QgsProcessingParameterNumber(
                self.DECIMAL,
                self.tr('Decimal places', 'Casas decimais'),
                type = QgsProcessingParameterNumber.Type.Integer,
                defaultValue = 3,
                minValue = 1
                )
            )

        self.addParameter(
            QgsProcessingParameterFileDestination(
                self.FILE,
                self.tr('Ground Control Points (GCP)', 'Pontos de Controle (GCP)'),
                fileFilter = 'Text (*.txt)'
            )
        )

        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.LAYER,
                self.tr('GCP layer', 'Camada de GCP')
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
        
        # Verificar se a camada de entrada é do tipo PointZ
        if pontos.wkbType() != QgsWkbTypes.PointZ:
            raise QgsProcessingException(self.tr('Input point layer must have PointZ geometry!', 'Camada de pontos de entrada deve ter geometria do tipo PointZ!'))

        
        decimal = self.parameterAsInt(
            parameters,
            self.DECIMAL,
            context
        )
        if decimal is None or decimal<1:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.DECIMAL))

        format_num = '{:.Xf}'.replace('X', str(decimal))

        filepath = self.parameterAsFile(
            parameters,
            self.FILE,
            context
        )
        if not filepath:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.FILE))

        # Criando arquivo de pontos de controle
        arq = open(filepath, 'w')


        # Camada de saída
        Fields = QgsFields()

        itens  = {
                     'X' : QVariant.Double,
                     'Y' : QVariant.Double,
                     'Z' : QVariant.Double,
                     'R' : QVariant.Int,
                     'G' : QVariant.Int,
                     'B' : QVariant.Int,
                     }
        for item in itens:
            Fields.append(QgsField(item, itens[item]))

        (sink, dest_id) = self.parameterAsSink(
            parameters,
            self.LAYER,
            context,
            Fields,
            pontos.wkbType(),
            pontos.sourceCrs()
        )
        if sink is None:
            raise QgsProcessingException(self.invalidSinkError(parameters, self.ANGLES))
        
        # Lista de Cores
        if pontos.featureCount() > 0:
            lista_cores = gerar_paleta_tematica('vibrante', pontos.featureCount())

        total = 100.0 / pontos.featureCount() if pontos.featureCount() else 0
        for current, feat in enumerate(pontos.getFeatures()):
            geom = feat.geometry()
            X, Y, Z = geom.constGet().x(), geom.constGet().y(), geom.constGet().z()
            R,G,B = lista_cores[current]
            arq.write(format_num.format(X) + ',' + format_num.format(Y) + ',' + format_num.format(Z) + ',' + str(R) + ',' + str(G) + ',' + str(B) + '\n')
            feat2 = QgsFeature(Fields)
            feat2.setGeometry(geom)
            att = [float(X), float(Y), float(Z), int(R), int(G), int(B)]
            feat2.setAttributes(att)
            sink.addFeature(feat2, QgsFeatureSink.FastInsert)

            if feedback.isCanceled():
                break
            feedback.setProgress(int((current+1) * total))

        arq.close()

        feedback.pushInfo(self.tr('Operation completed successfully!', 'Operação finalizada com sucesso!'))
        feedback.pushInfo(self.tr('Leandro Franca - Cartographic Engineer', 'Leandro França - Eng Cart'))

        self.SAIDA = dest_id
        return {self.LAYER: dest_id}

    def postProcessAlgorithm(self, context, feedback):
        layer = QgsProcessingUtils.mapLayerFromString(self.SAIDA, context)
        
        # Criar expressão RGB como string: "R,G,B"
        expr = 'concat("R", \',\', "G", \',\', "B")'
        layer.startEditing()
        if 'RGB' not in [f.name() for f in layer.fields()]:
            layer.dataProvider().addAttributes([QgsField('RGB', QVariant.String)])
            layer.updateFields()

        # Atualizar campo RGB
        rgb_idx = layer.fields().indexFromName('RGB')
        for f in layer.getFeatures():
            rgb = f['R'], f['G'], f['B']
            expr_value = f'{rgb[0]},{rgb[1]},{rgb[2]}'
            layer.changeAttributeValue(f.id(), rgb_idx, expr_value)
        layer.commitChanges()

        # Criar categorias de simbologia
        from qgis.core import QgsSymbol, QgsRendererCategory, QgsCategorizedSymbolRenderer
        categories = []

        for feat in layer.getFeatures():
            rgb_str = f'{feat["R"]},{feat["G"]},{feat["B"]}'
            symbol = QgsSymbol.defaultSymbol(layer.geometryType())
            symbol.setColor(QColor(feat["R"], feat["G"], feat["B"]))
            category = QgsRendererCategory(rgb_str, symbol, rgb_str)
            categories.append(category)

        renderer = QgsCategorizedSymbolRenderer('RGB', categories)
        layer.setRenderer(renderer)
        layer.triggerRepaint()

        return {self.LAYER: self.SAIDA}