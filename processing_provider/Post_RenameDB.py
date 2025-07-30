# -*- coding: utf-8 -*-

"""
Post_RenameDB.py
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
from lftools.translations.translate import translate
import os
from pathlib import Path
from qgis.PyQt.QtGui import QIcon

class RenameDB(QgsProcessingAlgorithm):

    LOC = QgsApplication.locale()[:2]

    def tr(self, *string):
        return translate(string, self.LOC)

    def createInstance(self):
        return RenameDB()

    def name(self):
        return 'renamedb'

    def displayName(self):
        return self.tr('Rename database', 'Renomear BD')

    def group(self):
        return self.tr('PostGIS')

    def groupId(self):
        return 'postgis'

    def tags(self):
        return 'GeoOne,postgis,postgresql,database,BD,DB,rename,change,manager,name,version,upadate'.split(',')

    def icon(self):
        return QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images/postgis.png'))

    txt_en = '''This tool allows you to rename a PostgreSQL database.
Note: To run this operation, the database must be disconnected. This means, that it must not be opened in any software (PgAdmin, QGIS, etc.).'''
    txt_pt = """Esta ferramenta permite renomear um banco de dados do PostgreSQL.
Nota: Para realizar esta operação, é necessário que o banco de dados esteja desconectado, ou seja, não esteja aberto em nenhum software (PgAdmin, QGIS, etc.)."""
    figure = 'images/tutorial/post_renamedb.jpg'

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


    ORIGINAL ='ORIGINAL'
    RENAMED = 'RENAMED'
    HOST = 'HOST'
    USER = 'USER'
    PORT = 'PORT'
    VERSION = 'VERSION'
    versions = ['9.5', '9.6', '10', '11', '12', '13', '14', '15', '16', '17']

    def initAlgorithm(self, config=None):
        # INPUT
        self.addParameter(
            QgsProcessingParameterString(
                self.ORIGINAL,
                self.tr('Original database name', 'Nome original do BD')
            )
        )

        self.addParameter(
            QgsProcessingParameterString(
                self.RENAMED,
                self.tr('New database name', 'Novo nome do BD')
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
                defaultValue = 8
            )
        )

    def processAlgorithm(self, parameters, context, feedback):

        antigo = self.parameterAsString(
            parameters,
            self.ORIGINAL,
            context
        )
        if not antigo or antigo == '' or ' ' in antigo:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.ORIGINAL))

        novo = self.parameterAsString(
            parameters,
            self.RENAMED,
            context
        )
        if not novo or novo == '' or ' ' in novo:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.RENAMED))

        host = self.parameterAsString(
            parameters,
            self.HOST,
            context
        )

        port = self.parameterAsString(
            parameters,
            self.PORT,
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

        # Procurando arquivo psql
        win64 = 'C:/Program Files (x86)/PostgreSQL/'+version+'/bin'
        win64d = 'D:/Program Files (x86)/PostgreSQL/'+version+'/bin'
        win32 = 'C:/Program Files/PostgreSQL/'+version+'/bin'
        win32d = 'D:/Program Files/PostgreSQL/'+version+'/bin'
        mac = '/Library/PostgreSQL/'+version+'/bin/'
        linux = '/usr/lib/postgresql/'+version+'/bin/'
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
        elif os.path.isdir(linux):
            os.chdir(linux)
        else:
            raise QgsProcessingException(self.tr('Make sure your PostgreSQL version is correct!', 'Verifique se a versão do seu PostgreSQL está correta!'))

        # Renomeando BD
        file_path = str(Path(Path.home(), "rename.sql"))
        arquivo = open(file_path,'w')
        arquivo.write('ALTER DATABASE '+antigo+' RENAME TO '+novo)
        arquivo.close()
        comando = 'psql -d postgres -U '+user+' -h '+host+' -p '+port+' -f ' + file_path
        feedback.pushInfo('\n' + self.tr('Command: ','Comando: ') + comando)
        feedback.pushInfo('\n' + self.tr('Starting rename database process...', 'Iniciando processo de renomear BD...'))
        result = os.system(comando)
        os.remove(file_path)

        if result==0:
            feedback.pushInfo(self.tr('Operation completed successfully!', 'Operação finalizada com sucesso!'))
            feedback.pushInfo(self.tr('Leandro Franca - Cartographic Engineer', 'Leandro França - Eng Cart'))
        else:
            feedback.pushInfo(self.tr('There was a problem while executing the command. Please check the input parameters.',
                                      'Houve algum problema durante a execução do comando. Por favor, verifique os parâmetros de entrada.'))

        return {}
