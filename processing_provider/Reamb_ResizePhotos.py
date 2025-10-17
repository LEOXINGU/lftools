# -*- coding: utf-8 -*-

"""
Reamb_ResizePhotos.py
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
__date__ = '2022-03-07'
__copyright__ = '(C) 2022, Leandro França'

from qgis.PyQt.QtCore import QVariant
from qgis.core import (QgsApplication,
                       QgsProcessingParameterFile,
                       QgsProcessingParameterBoolean,
                       QgsProcessingParameterEnum,
                       QgsProcessingParameterNumber,
                       QgsProcessingUtils,
                       QgsProcessingException,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterFeatureSink)

import shutil
from lftools.geocapt.imgs import Imgs
from lftools.translations.translate import translate
import os
from qgis.PyQt.QtGui import QIcon
import PIL


class ResizePhotos(QgsProcessingAlgorithm):

    LOC = QgsApplication.locale()[:2]

    def tr(self, *string):
        return translate(string, self.LOC)

    def createInstance(self):
        return ResizePhotos()

    def name(self):
        return 'resizephotos'

    def displayName(self):
        return self.tr('Resize photos', 'Redimensionar fotos')

    def group(self):
        return self.tr('Reambulation', 'Reambulação')

    def groupId(self):
        return 'reambulation'

    def tags(self):
        return 'GeoOne,resized,photo,reambulation,redimensionar,geophoto,reambulação,fotografia,photography,diminuir,reduzir,compactar,foto'.split(',')

    def icon(self):
        return QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images/reamb_camera.png'))

    txt_en = '''The largest width or height value of the original image is resized to the user-defined value. The short side is scaled proportionately.
    Note: The metadata is preserved.'''
    txt_pt = '''O maior valor de largura ou altura da imagem original é redimensionado para o valor definido pelo usuário. O lado menor é redimensionado proporcionalmente.
    Obs.: Os metadados são preservados.'''
    figure = 'images/tutorial/reamb_resize_photo.jpg'

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

    INPUT_FOLDER = 'INPUT_FOLDER'
    OUTPUT_FOLDER = 'OUTPUT_FOLDER'
    SUBFOLDER = 'SUBFOLDER'
    SIZE = 'SIZE'

    def initAlgorithm(self, config=None):

        self.addParameter(
            QgsProcessingParameterFile(
                self.INPUT_FOLDER,
                self.tr('Folder with photos (.jpeg or .jpg)', 'Pasta com fotografias (.jpeg ou .jpg)'),
                behavior=QgsProcessingParameterFile.Folder,
                defaultValue=None
            )
        )

        self.addParameter(
            QgsProcessingParameterBoolean(
                self.SUBFOLDER,
                self.tr('Check subfolders', 'Verificar sub-pastas'),
                defaultValue = False
            )
        )

        self.addParameter(
            QgsProcessingParameterNumber(
                self.SIZE,
                self.tr('Size for the larger side', 'Tamanho para o lado maior'),
                type = QgsProcessingParameterNumber.Type.Integer,
                minValue = 10,
                defaultValue = 800
                )
            )

        self.addParameter(
            QgsProcessingParameterFile(
                self.OUTPUT_FOLDER,
                self.tr('Folder for the resized photos', 'Pasta para as fotos redimensionadas'),
                behavior=QgsProcessingParameterFile.Folder,
                defaultValue=None
            )
        )

    def processAlgorithm(self, parameters, context, feedback):

        pasta_in = self.parameterAsFile(
            parameters,
            self.INPUT_FOLDER,
            context
        )
        if not pasta_in:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.INPUT_FOLDER))

        subpasta = self.parameterAsBool(
            parameters,
            self.SUBFOLDER,
            context
        )

        lado = self.parameterAsInt(
            parameters,
            self.SIZE,
            context
        )

        pasta_out = self.parameterAsFile(
            parameters,
            self.OUTPUT_FOLDER,
            context
        )
        if not pasta_out:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.OUTPUT_FOLDER))
        if pasta_in == pasta_out:
            raise QgsProcessingException(self.tr('Input and output folders cannot be the same!', 'As pastas de entrada e de saída não podem ser iguais!'))

        feedback.pushInfo(self.tr('Checking files in the folder...', 'Checando arquivos na pasta...'))
        lista = []
        if subpasta:
            for root, dirs, files in os.walk(pasta_in, topdown=True):
                for name in files:
                    if (name).lower().endswith(('.jpg', '.jpeg')):
                        lista += [os.path.join(root, name)]
        else:
            for item in os.listdir(pasta_in):
                if (item).lower().endswith(('.jpg', '.jpeg')):
                    lista += [os.path.join(pasta_in, item)]

        tam = len(lista)
        Percent = 100.0/tam if tam!=0 else 0

        # Redimensionando imagens
        feedback.pushInfo(self.tr('Resizing the images...', 'Redimensionando as imagens...'))
        for index, caminho in enumerate(lista):
            arquivo = os.path.split(caminho)[-1]
            img = PIL.Image.open(caminho)
            if 'exif' in img.info:
                exif = img.info['exif']
            altura = img.size[1]
            largura = img.size[0]
            if largura > altura:
                new_height = int(lado/float(largura)*altura)
                new_width = lado
            else:
                new_width = int(lado/float(altura)*largura)
                new_height = lado
            img = img.resize((new_width, new_height))
            if 'exif' in img.info:
                img.save(os.path.join(pasta_out, arquivo), exif=exif)
            else:
                img.save(os.path.join(pasta_out, arquivo))
            if feedback.isCanceled():
                break
            feedback.setProgress(int((index+1) * Percent))

        del img
        feedback.pushInfo(self.tr('Operation completed successfully!', 'Operação finalizada com sucesso!'))
        feedback.pushInfo(self.tr('Leandro Franca - Cartographic Engineer', 'Leandro França - Eng Cart'))

        return {}
