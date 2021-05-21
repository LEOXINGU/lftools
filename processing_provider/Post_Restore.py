# -*- coding: utf-8 -*-

"""
Post_Restore.py
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
__date__ = '2021-03-09'
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

class Restore(QgsProcessingAlgorithm):

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
        return Restore()

    def name(self):
        return 'restore'

    def displayName(self):
        return self.tr('Restore database', 'Restaurar BD')

    def group(self):
        return self.tr('PostGIS')

    def groupId(self):
        return 'postgis'

    def tags(self):
        return self.tr('postgis,postgresql,database,BD,DB,restore,backup,manager,export').split(',')

    def icon(self):
        return QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images/postgis.png'))

    txt_en = 'This tool allows you to restore a database content by importing all the backup information in a ".sql" file into a PostgreSQL server.'
    txt_pt = 'Esta ferramenta permite <b>restaurar</b>, ou seja, importar um banco de dados para um servidor PostgreSQL, a partir de um arquivo de backup no formato "<b>.sql</b>".'
    figure = 'images/tutorial/post_restore.jpg'

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
    HOST = 'HOST'
    VERSION = 'VERSION'
    USER = 'USER'
    PORT = 'PORT'
    versions = ['9.5', '9.6', '10', '11', '12', '13']

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
                self.HOST,
                self.tr('Host', 'Host'),
                defaultValue = 'localhost'
            )
        )

        self.addParameter(
            QgsProcessingParameterString(
                self.PORT,
                self.tr('Port', 'Porta'),
                defaultValue = '5432'
            )
        )

        self.addParameter(
            QgsProcessingParameterString(
                self.USER,
                self.tr('User', 'Usuário'),
                defaultValue = 'postgres'
            )
        )

        self.addParameter(
            QgsProcessingParameterEnum(
                self.VERSION,
                self.tr('PostgreSQL version', 'Versão do PostgreSQL'),
				options = self.versions,
                defaultValue= 2
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

        host = self.parameterAsString(
            parameters,
            self.HOST,
            context
        )

        version = self.parameterAsEnum(
            parameters,
            self.VERSION,
            context
        )
        version = self.versions[version]

        user = self.parameterAsString(
            parameters,
            self.USER,
            context
        )

        port = self.parameterAsString(
            parameters,
            self.PORT,
            context
        )

        # Procurando arquivo psql
        win64 = 'C:/Program Files (x86)/PostgreSQL/'+version+'/bin'
        win64d = 'D:/Program Files (x86)/PostgreSQL/'+version+'/bin'
        win32 = 'C:/Program Files/PostgreSQL/'+version+'/bin'
        win32d = 'D:/Program Files/PostgreSQL/'+version+'/bin'
        mac = '/Library/PostgreSQL/'+version+'/bin/'
        if os.path.isdir(win64):
            os.chdir(win64)
        elif os.path.isdir(win64d):
            os.chdir(win64d)
        elif os.path.isdir(win32):
            os.chdir(win32)
        elif os.path.isdir(win32d):
            os.chdir(win32d)
        elif os.path.isdir(mac):
            os.chdir(mac)
        else:
            raise QgsProcessingException(self.tr('Make sure your PostgreSQL version is correct!', 'Verifique se a versão do seu PostgreSQL está correta!'))

        # Realizando o Restore
        comando ='psql -d postgres -U '+user+' -h '+host+' -p '+port+' -f '+ '"' + file_path + '"'
        feedback.pushInfo('\n' + self.tr('Command: ','Comando: ') + comando)
        feedback.pushInfo('\n' + self.tr('Starting DB Restore process...', 'Iniciando processo de Restauracao do BD...'))
        result = os.system(comando)

        if result==0:
            feedback.pushInfo(self.tr('Operation completed successfully!', 'Operação finalizada com sucesso!'))
            feedback.pushInfo(self.tr('Leandro Franca - Cartographic Engineer', 'Leandro França - Eng Cart'))
        else:
            feedback.pushInfo(self.tr('There was a problem while executing the command. Please check the input parameters.',
                                      'Houve algum problema durante a execução do comando. Por favor, verifique os parâmetros de entrada.'))

        return {}
