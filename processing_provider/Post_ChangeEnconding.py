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

from PyQt5.QtCore import QCoreApplication, QVariant
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
import os
from qgis.PyQt.QtGui import QIcon

class ChangeEnconding(QgsProcessingAlgorithm):

    LOC = QgsApplication.locale()

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
        return self.tr('postgis,postgresql,database,BD,DB,restore,backup,manager,import,encoding,sql,change').split(',')

    def icon(self):
        return QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images/postgis.png'))

    def shortHelpString(self):
        txt_en = '''This tool changes the encoding type of a <b>.sql</b> file. A new file will be created with the user-defined encoding.
In some cases, this process is necessary to make it possible to transfer data between different operating systems, for example from Window to Linux, and vice versa.'''
        txt_pt = '''Esta ferramenta realizar a troca do tipo de codificação de um arquivo <b>.sql</b>. Um novo arquivo será criado com a codificação definida pelo usuário.
Em alguns casos, esse processo é necessário para possibilitar  transferir dados entre diferentes sistemas operacionais, por exemplo de Window para Linux, e vice-versa.'''
        social_BW = Imgs().social_BW
        footer = '''<div align="center">
                      <img src="'''+ os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images/tutorial/post_encoding.jpg') +'''">
                      </div>
                      <div align="right">
                      <p align="right">
                      <b>'''+self.tr('Author: Leandro Franca', 'Autor: Leandro França')+'''</b>
                      </p>'''+ social_BW + '''</div>
                    </div>'''
        return self.tr(txt_en, txt_pt) + footer


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
