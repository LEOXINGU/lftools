# -*- coding: utf-8 -*-

"""
Post_CloneDB.py
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

class CloneDB(QgsProcessingAlgorithm):

    LOC = QgsApplication.locale()[:2]

    def tr(self, *string):
        return translate(string, self.LOC)

    def createInstance(self):
        return CloneDB()

    def name(self):
        return 'clonedb'

    def displayName(self):
        return self.tr('Clone database', 'Clonar BD')

    def group(self):
        return self.tr('PostGIS')

    def groupId(self):
        return 'postgis'

    def tags(self):
        return self.tr('postgis,postgresql,database,BD,DB,clone,backup,manager,copy,version,control').split(',')

    def icon(self):
        return QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images/postgis.png'))

    txt_en = '''This tool allows the user to clone any PostgreSQL database. From a model database, another database that has exactly the same (schema and instances) is generated with a new name defined by the operator.
Note: To create more than one "clone", the new database names must be filled and separated by "comma".'''
    txt_pt = """Esta ferramenta permite clonar qualquer banco PostgreSQL. A partir de um banco de dados modelo, é gerado um outro banco exatamente igual (esquema e instâncias) com um novo nome definido pelo operador.
Obs.: Para criação de mais de um "clone", os novos nomes dos bancos devem ser inseridos "separados por vírgula"."""
    figure = 'images/tutorial/post_clonedb.jpg'

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


    ORIGINALDB ='ORIGINALDB'
    CLONES = 'CLONES'
    HOST = 'HOST'
    USER = 'USER'
    PORT = 'PORT'
    VERSION = 'VERSION'
    versions = ['9.5', '9.6', '10', '11', '12', '13', '14', '15', '16', '17']

    def initAlgorithm(self, config=None):
        # INPUT
        self.addParameter(
            QgsProcessingParameterString(
                self.ORIGINALDB,
                self.tr('Original database', 'Banco de dados original')
            )
        )

        self.addParameter(
            QgsProcessingParameterString(
                self.CLONES,
                self.tr('Name(s) of the cloned database(s)', 'Nome(s) do(s) BD clonado(s)')
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

        template = self.parameterAsString(
            parameters,
            self.ORIGINALDB,
            context
        )
        if not template or template == '' or ' ' in template:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.ORIGINALDB))

        clones = self.parameterAsString(
            parameters,
            self.CLONES,
            context
        )
        if not clones or clones == '' or ' ' in clones:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.CLONES))

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
        file_path = str(Path(Path.home(), "clones.sql"))
        arquivo = open(file_path,'w')
        for clone in clones.split(','):
            arquivo.write('CREATE DATABASE '+clone.replace('-', '_')+' WITH TEMPLATE '+template+';\n')
        arquivo.close()
        comando = 'psql -d postgres -U '+user+' -h '+host+' -p '+port+' -f ' + file_path
        feedback.pushInfo('\n' + self.tr('Command: ','Comando: ') + comando)
        feedback.pushInfo('\n' + self.tr('Starting database cloning process...', 'Iniciando processo de clonagem do BD...'))
        result = os.system(comando)
        os.remove(file_path)

        if result==0:
            feedback.pushInfo(self.tr('Operation completed successfully!', 'Operação finalizada com sucesso!'))
            feedback.pushInfo(self.tr('Leandro Franca - Cartographic Engineer', 'Leandro França - Eng Cart'))
        else:
            feedback.pushInfo(self.tr('There was a problem while executing the command. Please check the input parameters.',
                                      'Houve algum problema durante a execução do comando. Por favor, verifique os parâmetros de entrada.'))

        return {}
