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

from qgis.core import (QgsApplication,
                       QgsProcessingParameterVectorLayer,
                       QgsProcessing,
                       QgsProcessingParameterField,
                       QgsProcessingParameterCrs,
                       QgsCoordinateTransform,
                       QgsProcessingParameterNumber,
                       QgsProcessingParameterBoolean,
                       QgsProcessingParameterFileDestination,
                       QgsProject,
                       QgsProcessingException,
                       QgsProcessingAlgorithm)
from lftools.geocapt.imgs import Imgs
from lftools.translations.translate import translate
import os, subprocess
from qgis.PyQt.QtGui import QIcon

class CreateGCPfile(QgsProcessingAlgorithm):

    LOC = QgsApplication.locale()[:2]

    def tr(self, *string):
        return translate(string, self.LOC)

    def createInstance(self):
        return CreateGCPfile()

    def name(self):
        return 'creategcpfile'

    def displayName(self):
        return self.tr('Generate GCP file for WebODM', 'Gerar arquivo de GCP para o WebODM')

    def group(self):
        return self.tr('Drones')

    def groupId(self):
        return 'drones'

    def tags(self):
        return 'GeoOne,drones,fotografia,webodm,opendronemap,odm,photography,gcp,copy,points,control,ground,quality,homologous,controle,terreno'.split(',')

    def icon(self):
        return QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images/drone.png'))

    txt_en = 'Generate text file with Ground Control Points (GCP) from a point layer to WebODM.'
    txt_pt = 'Gera arquivo texto com Pontos de Controle no Terreno (GCP) a partir de uma camada de pontos para ser carregado no WebODM.'
    figure = 'images/tutorial/drone_createGCP.jpg'

    def shortHelpString(self):
        social_BW = Imgs().social_BW
        footer = '''<div align="center">
                      <img src="'''+ os.path.join(os.path.dirname(os.path.dirname(__file__)), self.figure) +'''">
                      </div>
                      <div align="left">
                      <p>
                      <b><a href="'''+ self.tr('https://portal.geoone.com.br/m/lessons/drone-webodm?classId=2307') + '''" target="_blank">'''+ self.tr('Click here to watch a full class on this tool',
                                    'Clique aqui para assistir uma aula completa sobre esta ferramenta') +'''</a></b>
                      </p>
                      <p>
                      <b><a href="'''+ self.tr('https://geoone.com.br/pvdrone/') + '''" target="_blank">'''+ self.tr('Sign up for the WebODM and QGIS course',
                                    'Inscreva-se no curso de WebODM e QGIS') +'</a><br><br>'+ self.tr('Author: Leandro Franca', 'Autor: Leandro França')+'''</b>
                      </p>'''+ social_BW + '''
                    </div>'''
        return self.tr(self.txt_en, self.txt_pt) + footer

    POINTS = 'POINTS'
    NAME = 'NAME'
    FILE = 'FILE'
    DECIMAL = 'DECIMAL'
    CRS = 'CRS'
    OPEN = 'OPEN'

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
                defaultValue = 3,
                minValue = 1
                )
            )
        
        self.addParameter(
            QgsProcessingParameterCrs(
                self.CRS,
                self.tr('CRS', 'SRC'),
                optional = True
                )
            )

        self.addParameter(
            QgsProcessingParameterFileDestination(
                self.FILE,
                self.tr('TXT with Ground Control Points (GCP)', 'TXT com Pontos de Controle (GCP)'),
                fileFilter = 'Text (*.txt)'
            )
        )

        self.addParameter(
            QgsProcessingParameterBoolean(
                self.OPEN,
                self.tr('Open output file after executing the algorithm', 'Abrir arquivo de saída com GCPs'),
                defaultValue= True
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

        out_CRS = self.parameterAsCrs(
            parameters,
            self.CRS,
            context
        )

        if out_CRS.isValid():
            # Transformação de coordenadas
            coordinateTransformer = QgsCoordinateTransform(pontos.crs(), out_CRS, QgsProject.instance())

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
        if out_CRS.isValid():
            arq.write(out_CRS.toProj4()  + '\n')
        else:
            arq.write(pontos.sourceCrs().toProj4()  + '\n')

        for feat in pontos.getFeatures():
            nome = feat[columnIndex].replace(' ', '_')
            geom = feat.geometry()
            if out_CRS.isValid():
                geom.transform(coordinateTransformer)
            if not eh3d:
                pnt = geom.asPoint()
                X, Y, Z = pnt.x(), pnt.y(), 0
            else:
                X, Y, Z = geom.constGet().x(), geom.constGet().y(), geom.constGet().z()
            arq.write(format_num.format(X) + ' ' + format_num.format(Y) + ' ' + format_num.format(Z) + ' 0 0 ' + nome + '\n')
            if feedback.isCanceled():
                break

        arq.close()

        Carregar = self.parameterAsBool(
            parameters,
            self.OPEN,
            context
        )

        if Carregar:
            try:
                os.popen(filepath)
            except Exception as e:
                feedback.reportError(f"Failed to open File Explorer: {e}")

        feedback.pushInfo(self.tr('Operation completed successfully!', 'Operação finalizada com sucesso!'))
        feedback.pushInfo(self.tr('Leandro Franca - Cartographic Engineer', 'Leandro França - Eng Cart'))

        return {self.FILE: filepath}
