# -*- coding: utf-8 -*-

"""
Post_DeleteDB.py
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

class DeleteDB(QgsProcessingAlgorithm):

    LOC = QgsApplication.locale()[:2]

    def tr(self, *string):
        return translate(string, self.LOC)

    def createInstance(self):
        return DeleteDB()

    def name(self):
        return 'deletedb'

    def displayName(self):
        return self.tr('Delete database', 'Deletar BD')

    def group(self):
        return self.tr('PostGIS')

    def groupId(self):
        return 'postgis'

    def tags(self):
        return self.tr('postgis,postgresql,database,BD,DB,delete,drop,manager,clean').split(',')

    def icon(self):
        return QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images/postgis.png'))

    txt_en = '''This tool allows you to delete / drop any PostgreSQL database.
Notes:
- To run this operation, the database must be disconnected. This means, that it must not be opened in any software (PgAdmin, QGIS, etc.).
- To delete more than one database, the names must be filled and separated by "comma".
<p style="color:red;">Attention: This operation is irreversible, so be sure before running it!</p>'''
    txt_pt = """Esta ferramenta permite apagar (delete/drop) qualquer banco do PostgreSQL.
Obs.:
- Para realizar esta operação, é necessário que o banco esteja desconectado, ou seja, não esteja aberto em nenhum software (PgAdmin, QGIS, etc).
- Para deletar mais de um BD, os nomes devem ser preenchidos separados por vírgula.
<p style="color:red;">Atenção: Esta operação é irreversível, portanto esteja seguro quando for executá-la!</p>"""
    figure = 'images/tutorial/post_deletedb.jpg'

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

    DELETED = 'DELETED'
    HOST = 'HOST'
    USER = 'USER'
    PORT = 'PORT'
    VERSION = 'VERSION'
    versions = ['9.5', '9.6', '10', '11', '12', '13', '14', '15', '16', '17']

    def initAlgorithm(self, config=None):
        # INPUT
        self.addParameter(
            QgsProcessingParameterString(
                self.DELETED,
                self.tr('DB Name(s) to be deleted', 'Nome(s) do(s) BD a serem deletado(s)')
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

        deleted = self.parameterAsString(
            parameters,
            self.DELETED,
            context
        )
        if not deleted or deleted == '' or ' ' in deleted:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.DELETED))

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

        # Renomeando BD
        file_path = str(Path(Path.home(), "deleted.sql"))
        arquivo = open(file_path,'w')
        for item in deleted.split(','):
            arquivo.write('DROP DATABASE ' + item +';\n')
        arquivo.close()
        comando = 'psql -d postgres -U '+user+' -h '+host+' -p '+port+' -f ' + file_path
        feedback.pushInfo('\n' + self.tr('Command: ','Comando: ') + comando)
        feedback.pushInfo('\n' + self.tr('Starting delete/drop database(s)...', 'Iniciando processo de delete/drop BD...'))
        result = os.system(comando)
        os.remove(file_path)

        if result==0:
            feedback.pushInfo(self.tr('Operation completed successfully!', 'Operação finalizada com sucesso!'))
            feedback.pushInfo(self.tr('Leandro Franca - Cartographic Engineer', 'Leandro França - Eng Cart'))
        else:
            feedback.pushInfo(self.tr('There was a problem while executing the command. Please check the input parameters.',
                                      'Houve algum problema durante a execução do comando. Por favor, verifique os parâmetros de entrada.'))

        return {}
