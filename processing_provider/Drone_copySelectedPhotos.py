# -*- coding: utf-8 -*-

"""
Drone_copySelectedPhotos.py
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
__date__ = '2021-11-07'
__copyright__ = '(C) 2021, Leandro França'

from qgis.utils import iface
from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import *
from lftools.geocapt.imgs import Imgs
from lftools.translations.translate import translate
import os, shutil
from qgis.PyQt.QtGui import QIcon

class CopySelectedPhotos(QgsProcessingAlgorithm):

    LOC = QgsApplication.locale()[:2]

    def tr(self, *string):
        return translate(string, self.LOC)

    def createInstance(self):
        return CopySelectedPhotos()

    def name(self):
        return 'copyselectedphotos'

    def displayName(self):
        return self.tr('Copy selected files', 'Copiar arquivos selecionados')

    def group(self):
        return self.tr('Drones')

    def groupId(self):
        return 'drones'

    def tags(self):
        return 'GeoOne,drones,fotografia,photography,blocks,copy,copiar,separate,separar,organize,organizar,filtrar,filter'.split(',')

    def icon(self):
        return QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images/drone.png'))

    txt_en = 'This tool makes it possible to copy or move files to a new folder from a point layer with file paths.'
    txt_pt = 'Esta ferramenta possibilita copiar ou mover arquivos para uma nova pasta a partir de uma camada de pontos com os caminhos dos arquivos.'
    figure = 'images/tutorial/drone_copySelectedFiles.jpg'

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
    FILEPATH = 'FILEPATH'
    OPTION = 'OPTION'
    FOLDER = 'FOLDER'

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
                self.FILEPATH,
                self.tr('Field with file path', 'Campo com o caminho do arquivo'),
                parentLayerParameterName=self.POINTS,
                type=QgsProcessingParameterField.String
            )
        )

        opt = [self.tr('Copy','Copiar'),
                  self.tr('Move','Mover')
               ]

        self.addParameter(
            QgsProcessingParameterEnum(
                self.OPTION,
                self.tr('Option', 'Opção'),
				options = opt,
                defaultValue= 0
            )
        )

        self.addParameter(
            QgsProcessingParameterFile(
                self.FOLDER,
                self.tr('Destination folder for photos', 'Pasta de destino para fotografias'),
                behavior=QgsProcessingParameterFile.Folder,
                defaultValue=None
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
            self.FILEPATH,
            context
        )
        if campo is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.FILEPATH))

        columnIndex = pontos.fields().indexFromName(campo[0])

        opcao = self.parameterAsEnum(
            parameters,
            self.OPTION,
            context
        )

        destino = self.parameterAsFile(
            parameters,
            self.FOLDER,
            context
        )
        if not destino:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.FOLDER))

        # Verificar se tem arquivos selecionados
        if pontos.selectedFeatureCount() <1:
            raise QgsProcessingException(self.tr('At least one feature must be selected!', 'Pelo menos uma feição deve ser selecionada!'))

        # Copiando arquivos selecionados para a nova pasta
        total = 100.0 / pontos.selectedFeatureCount()
        cont = 1
        for pnt in pontos.getSelectedFeatures():
            origem = pnt[columnIndex]
            if os.path.exists(origem):
                nome = os.path.split(origem)[-1]
                if opcao == 0:
                    shutil.copy2(origem, os.path.join(destino, nome))
                elif opcao == 1:
                    shutil.move(origem, os.path.join(destino, nome))
            else:
                feedback.reportError('📢 ' + self.tr('Path {} does not exist!', 'Caminho {} não exite!').format(origem))

            if feedback.isCanceled():
                break
            feedback.setProgress(int((cont) * total))
            cont += 1

        feedback.pushInfo(self.tr('Operation completed successfully!', 'Operação finalizada com sucesso!'))
        feedback.pushInfo(self.tr('Leandro Franca - Cartographic Engineer', 'Leandro França - Eng Cart'))

        return {}
