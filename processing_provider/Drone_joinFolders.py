# -*- coding: utf-8 -*-

"""
Drone_joinFolders.py
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
                       QgsProcessingParameterBoolean,
                       QgsProcessingParameterFile,
                       QgsFeatureSink,
                       QgsProcessingException,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterFeatureSink)
from lftools.geocapt.imgs import Imgs
import os, shutil
from qgis.PyQt.QtGui import QIcon

class JoinFolders(QgsProcessingAlgorithm):

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
        return JoinFolders()

    def name(self):
        return 'joinfolders'

    def displayName(self):
        return self.tr('Join folders', 'Juntar pastas')

    def group(self):
        return self.tr('Drones')

    def groupId(self):
        return 'drones'

    def tags(self):
        return self.tr('drones,fotografia,photography,blocks,join,juntar,organize,organizar').split(',')

    def icon(self):
        return QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images/drone.png'))

    txt_en = '''This tool has the objective of joining the files from several folders in another new folder, with the possibility of <b>renaming</b> the files.
    It is a very useful procedure for joining multiple drone images with repeated names into a single folder.'''
    txt_pt = '''Esta ferramenta tem o objetivo de juntar os arquivos de várias pastas em uma outra nova pasta, com a possibilidade de <b>renomear</b> os arquivos.
É um procedimento muito útil para juntar várias imagens de drone com nomes repetidos em uma única pasta.'''
    figure = 'images/tutorial/drone_joinFolders.jpg'

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

    FOLDERS = 'FOLDERS'
    RENAME = 'RENAME'
    PREFIX = 'PREFIX'
    OUT_FOLDER = 'OUT_FOLDER'

    def initAlgorithm(self, config=None):
        #inputs
        self.addParameter(
            QgsProcessingParameterFile(
                self.FOLDERS,
                self.tr('Folders with files', 'Pastas com arquivos'),
                behavior=QgsProcessingParameterFile.Folder,
                defaultValue=None
            )
        )

        self.addParameter(
            QgsProcessingParameterBoolean(
                self.RENAME,
                self.tr('Rename copied files', 'Renomear arquivos copiados'),
                defaultValue = True
            )
        )

        self.addParameter(
            QgsProcessingParameterString(
                self.PREFIX,
                self.tr('File name prefix', 'Prefixo do nome do arquivo'),
                defaultValue = self.tr('IMG_')
            )
        )

        #output
        self.addParameter(
            QgsProcessingParameterFile(
                self.OUT_FOLDER,
                self.tr('Destination folder', 'Pasta de destino'),
                behavior=QgsProcessingParameterFile.Folder,
                defaultValue=None
            )
        )

    def processAlgorithm(self, parameters, context, feedback):

        caminho_geral = self.parameterAsFile(
            parameters,
            self.FOLDERS,
            context
        )
        if not caminho_geral:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.FOLDERS))

        renomear = self.parameterAsBool(
            parameters,
            self.RENAME,
            context
        )

        prefixo = self.parameterAsString(
            parameters,
            self.PREFIX,
            context
        )

        destino = self.parameterAsFile(
            parameters,
            self.OUT_FOLDER,
            context
        )
        if not destino:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.OUT_FOLDER))


        # Listando arquivos
        itens = os.listdir(caminho_geral)

        # contagem de arquivos
        pastas = []
        cont_files = 0
        for item in itens:
            caminho = os.path.join(caminho_geral,item)
            if not os.path.isfile(caminho):
                pastas += [item]
                arquivos = os.listdir(caminho)
                for arq in arquivos:
                    filepath = os.path.join(caminho,arq)
                    if os.path.isfile(filepath):
                        cont_files += 1

        feedback.pushInfo(self.tr('Number of files to be copied: {}'.format(cont_files), 'Total de arquivos a serem copiados: {}'.format(cont_files)))
        total = 100.0 / cont_files if cont_files else 0
        cont = 0

        # copiando os arquivos
        for pasta in pastas:
            caminho = os.path.join(caminho_geral,pasta)
            if os.path.join(caminho, '') != os.path.join(destino, ''):
                lista = os.listdir(caminho)
                for arq in lista:
                    if os.path.isfile(os.path.join(caminho, arq)):
                        shutil.copy(os.path.join(caminho, arq),
                                    os.path.join(destino, prefixo + "{:04d}.".format(cont) + arq.split('.')[-1]) if renomear else os.path.join(destino, arq))
                    if feedback.isCanceled():
                        break
                    cont += 1
                    feedback.setProgress(int((cont) * total))

        feedback.pushInfo(self.tr('Operation completed successfully!', 'Operação finalizada com sucesso!'))
        feedback.pushInfo(self.tr('Leandro Franca - Cartographic Engineer', 'Leandro França - Eng Cart'))

        return {}
