# -*- coding: utf-8 -*-

"""
Drone_createGCPfile.py
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
__date__ = '2021-11-08'
__copyright__ = '(C) 2021, Leandro França'

from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (QgsApplication,
                       QgsProcessingParameterVectorLayer,
                       QgsGeometry,
                       QgsProcessing,
                       QgsProcessingParameterField,
                       QgsProcessingParameterString,
                       QgsProcessingParameterEnum,
                       QgsProcessingParameterNumber,
                       QgsProcessingParameterBoolean,
                       QgsProcessingParameterFileDestination,
                       QgsFeatureSink,
                       QgsProcessingException,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterFeatureSink)
from lftools.geocapt.imgs import Imgs
import os
from qgis.PyQt.QtGui import QIcon

class CreateGCPfile(QgsProcessingAlgorithm):

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
        return CreateGCPfile()

    def name(self):
        return 'creategcpfile'

    def displayName(self):
        return self.tr('Generate GCP file from layer', 'Gerar arquivo de GCP a partir de camada')

    def group(self):
        return self.tr('Drones')

    def groupId(self):
        return 'drones'

    def tags(self):
        return self.tr('drones,fotografia,photography,gcp,copy,points,control,ground,quality,homologous,controle,terreno').split(',')

    def icon(self):
        return QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images/drone.png'))

    txt_en = 'Generate text file with Ground Control Points (GCP) from a point layer.'
    txt_pt = 'Gera arquivo texto com Pontos de Controle no Terreno (GCP) a partir de uma camada de pontos.'
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

    def initAlgorithm(self, config=None):
        self.addParameter(
            QgsProcessingParameterVectorLayer(
                self.POINTS,
                self.tr('Point Layer', 'Camada de Pontos'),
                [QgsProcessing.TypeVectorPoint]
            )
        )

        self.addParameter(
            QgsProcessingParameterField(
                self.NAME,
                self.tr('GCP name', 'Nome do ponto de controle'),
                parentLayerParameterName=self.POINTS,
                type=QgsProcessingParameterField.String
            )
        )

        self.addParameter(
            QgsProcessingParameterNumber(
                self.DECIMAL,
                self.tr('Decimal places', 'Casas decimais'),
                type = QgsProcessingParameterNumber.Type.Integer,
                defaultValue = 3
                )
            )

        self.addParameter(
            QgsProcessingParameterFileDestination(
                self.FILE,
                self.tr('Ground Control Points (GCP)', 'Pontos de Controle (GCP)'),
                fileFilter = 'Text (*.txt)'
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

        campo = self.parameterAsFields(
            parameters,
            self.NAME,
            context
        )
        if campo is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.NAME))

        columnIndex = pontos.fields().indexFromName(campo[0])

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

        # Verificando se a camada possui coordenada Z
        for feat in pontos.getFeatures():
                geom = feat.geometry()
                break
        t = str(geom.constGet().z())
        try:
            t = str(geom.constGet().z())
        except:
            t = 'nan'
        if t == 'nan':
            eh3d = False
            feedback.pushInfo(self.tr('''Layer features do not have a Z coordinate.
            The Z coordinate will be set to 0 (zero)!''', '''Feições da camada não possuem coordenada Z.
A coordena Z será definida com 0 (zero)!'''))
        else:
            eh3d = True

        # Criando arquivo de pontos de controle
        arq = open(filepath, 'w')

        # Escrevendo SRC como WKT
        arq.write(pontos.sourceCrs().toProj4()  + '\n')

        for feat in pontos.getFeatures():
            nome = feat[columnIndex]
            geom = feat.geometry()
            if not eh3d:
                pnt = geom.asPoint()
                X, Y, Z = pnt.x(), pnt.y(), 0
            else:
                X, Y, Z = geom.constGet().x(), geom.constGet().y(), geom.constGet().z()
            arq.write(nome + '\t' + format_num.format(X) + '\t' + format_num.format(Y) + '\t' + format_num.format(Z) + '\n')
            if feedback.isCanceled():
                break

        arq.close()

        feedback.pushInfo(self.tr('Operation completed successfully!', 'Operação finalizada com sucesso!'))
        feedback.pushInfo(self.tr('Leandro Franca - Cartographic Engineer', 'Leandro França - Eng Cart'))

        return {}
