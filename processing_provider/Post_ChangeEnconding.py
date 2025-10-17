# -*- coding: utf-8 -*-

"""
Post_ChangeEnconding.py
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
__date__ = '2021-03-10'
__copyright__ = '(C) 2020, Leandro França'

from qgis.core import (QgsProcessing,
                       QgsProcessingException,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterString,
                       QgsProcessingParameterBoolean,
                       QgsProcessingParameterEnum,
                       QgsProcessingParameterRasterLayer,
                       QgsProcessingParameterFile,
                       QgsProcessingParameterFileDestination,
                       QgsApplication,
                       QgsRasterLayer,
                       QgsCoordinateReferenceSystem)

from lftools.geocapt.imgs import Imgs
from lftools.translations.translate import translate
import os
from qgis.PyQt.QtGui import QIcon

class ChangeEnconding(QgsProcessingAlgorithm):

    LOC = QgsApplication.locale()[:2]

    def tr(self, *string):
        return translate(string, self.LOC)

    def createInstance(self):
        return ChangeEnconding()

    def name(self):
        return 'changeencoding'

    def displayName(self):
        return self.tr('Change SQL encoding', 'Trocar codificação de SQL')

    def group(self):
        return self.tr('PostGIS')

    def groupId(self):
        return 'postgis'

    def tags(self):
        return 'GeoOne,postgis,postgresql,database,BD,DB,restore,backup,manager,import,encoding,sql,change'.split(',')

    def icon(self):
        return QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images/postgis.png'))

    figure = 'images/tutorial/post_encoding.jpg'
    txt_en = '''This tool changes the encoding type of a .sql file. A new file will be created with the user-defined encoding.
In some cases, this is a possible solution  to transfer data between different operating systems, for example from Windows to Linux, and vice versa.'''
    txt_pt = '''Esta ferramenta realiza a troca do tipo de codificação de um arquivo <b>.sql</b>. Um novo arquivo será criado com a codificação definida pelo usuário.
Em alguns casos, esse processo é uma possível solução para transferir dados entre diferentes sistemas operacionais, por exemplo de Window para Linux, e vice-versa.'''

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


    FILE ='FILE'
    ORIGINAL = 'ORIGINAL'
    CHANGED = 'CHANGED'

    def initAlgorithm(self, config=None):
        # INPUT
        self.addParameter(
            QgsProcessingParameterFile(
                self.FILE,
                self.tr('SQL File', 'Arquivo SQL'),
                extension = 'sql'
            )
        )

        self.addParameter(
            QgsProcessingParameterString(
                self.ORIGINAL,
                self.tr('Original encoding', 'Codificação original'),
                defaultValue = 'Portuguese_Brazil.1252'
            )
        )

        self.addParameter(
            QgsProcessingParameterString(
                self.CHANGED,
                self.tr('New encoding', 'Nova codificação'),
                defaultValue = 'pt_BR.UTF-8'
            )
        )


    def processAlgorithm(self, parameters, context, feedback):

        file_path = self.parameterAsFile(
            parameters,
            self.FILE,
            context
        )
        if not file_path:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.FILE))

        original = self.parameterAsString(
            parameters,
            self.ORIGINAL,
            context
        )

        changed = self.parameterAsString(
            parameters,
            self.CHANGED,
            context
        )

        arq = open(file_path, 'r')
        data = arq.read()
        arq.close()
        data = data.replace(original, changed)
        path, file = os.path.split(file_path)
        new_file = file[:-3] + changed + '.sql'
        arq = open(os.path.join(path, new_file), 'w')
        arq.write(data)
        arq.close()

        feedback.pushInfo(self.tr('Operation completed successfully!', 'Operação finalizada com sucesso!'))
        feedback.pushInfo(self.tr('Leandro Franca - Cartographic Engineer', 'Leandro França - Eng Cart'))

        return {}
