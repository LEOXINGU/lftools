# -*- coding: utf-8 -*-

"""
RV360_Cubemap2Equiretangular.py
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
__date__ = '2025-12-25'
__copyright__ = '(C) 2025, Leandro França'

from qgis.core import (QgsApplication,
                       QgsProcessingParameterFile,
                       QgsProcessingParameterNumber,
                       QgsProcessingException,
                       QgsProcessingParameterFileDestination,
                       QgsProcessingAlgorithm)

from lftools.geocapt.imgs import Imgs
from lftools.geocapt.rv360 import cube_faces_to_equirect
from lftools.translations.translate import translate
from qgis.PyQt.QtGui import QIcon
import os
from PIL import Image


class Cubemap2Equiretangular(QgsProcessingAlgorithm):

    LOC = QgsApplication.locale()[:2]

    def tr(self, *string):
        return translate(string, self.LOC)

    def createInstance(self):
        return Cubemap2Equiretangular()

    def name(self):
        return 'Cubemap2Equiretangular'.lower()

    def displayName(self):
        return self.tr('Cubemap to Equirectangular', 'Cubemap para Equiretangular')

    def group(self):
        return self.tr('VR 360°', 'RV 360°')

    def groupId(self):
        return 'rv360'

    def tags(self):
        return 'GeoOne,virtual,reality,realidade,esphere,esférica,360°,graus,photography,photos,fotos,fotografia,gopro,insta360,VR,RV,cubemap,cubo,faces'.split(',')

    def icon(self):
        return QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images/rv_360.png'))

    txt_en = '''Rebuilds a 360° equirectangular image from the six faces of a cubemap.
The tool reads the face images (+X, −X, +Y, −Y, +Z, −Z), recomposes the panorama, and produces a new image in standard equirectangular format.
Useful for returning to 360° format after editing, anonymization, or adding information directly on the cube faces.
When available, EXIF metadata from the original image can be reapplied to preserve GPS data and compatibility with 360° viewers.'''
    txt_pt = '''Reconstrói uma imagem 360° no formato equiretangular a partir das seis faces de um cubemap.
A ferramenta lê os arquivos correspondentes às faces (+X, −X, +Y, −Y, +Z, −Z), recompõe o panorama e gera uma nova imagem no mesmo padrão da original.
Ideal para retornar ao formato 360° após processos de edição, anonimização ou inserção de informações nas faces do cubo.
Quando disponível, os metadados EXIF da imagem original podem ser reaplicados na imagem final para manter informações de GPS e compatibilidade com visualizadores 360°.'''
    figure = 'images/tutorial/vr360_cube_eq.jpg'

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

    FOLDER = 'FOLDER'
    H = 'H'
    ORIGIN = 'ORIGIN'

    OUTPUT = 'OUTPUT'

    def initAlgorithm(self, config=None):

        self.addParameter(
            QgsProcessingParameterFile(
                self.FOLDER,
                self.tr('Cubemap faces folder', 'Pasta com as faces do cubo'),
                behavior = QgsProcessingParameterFile.Folder,
                defaultValue=None
            )
        )

        self.addParameter(
            QgsProcessingParameterNumber(
                self.H,
                self.tr('Image Height (H)', 'Altura da imagem (H)'),
                type = QgsProcessingParameterNumber.Type.Integer,
                minValue = 400,
                defaultValue = 2880  # H = 2880  # GoPro Max
            )
        )

        self.addParameter(
            QgsProcessingParameterFile(
                self.ORIGIN,
                self.tr('Original equirectangular image', 'Imagem equiretangular original'),
                behavior = QgsProcessingParameterFile.File,
                fileFilter = 'Image (*.jpeg *.jpg *.JPG)',
                optional = True
            )
        )
        
        # OUTPUT
        self.addParameter(
            QgsProcessingParameterFileDestination(
                self.OUTPUT,
                self.tr('Rebuilt 360° Image', 'Imagem 360° reconstruída'),
                fileFilter = 'Image (*.jpg)'
            )
        )


    def processAlgorithm(self, parameters, context, feedback):

        # pasta com as faces do cubo
        folder = self.parameterAsFile(
            parameters,
            self.FOLDER,
            context
        )
        if not folder:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.FOLDER))

        # caminho da foto 360 original
        img_original = self.parameterAsFile(
            parameters,
            self.ORIGIN,
            context
        )

        # resolução das faces do cubo
        H = self.parameterAsInt(
            parameters,
            self.H,
            context
        )

        # Imagem final
        img_final = self.parameterAsFileOutput(
            parameters,
            self.OUTPUT,
            context
        )

        # Ler H da imagem original
        if img_original:
            img_orig = Image.open(img_original)
            W_orig, H_orig = img_orig.size
            H = H_orig      # altura da equiretangular final
            feedback.pushInfo(self.tr(f'Image resolution defined to {2*H} x {H}.'))
            exif_data = img_orig.info.get("exif", None)
        else:
            exif_data = None
        
        if exif_data is not None:
            feedback.pushInfo(self.tr('EXIF found.'))
        else:
            feedback.reportError(self.tr("Original image without exif!"))

        # 3) Reconstruir a equiretangular a partir das faces
        cube_faces_to_equirect(folder, img_final, H=H, exif_data=exif_data, feedback=feedback)

        feedback.pushInfo(self.tr('Operation completed successfully!', 'Operação finalizada com sucesso!'))
        feedback.pushInfo(self.tr('Leandro Franca - Cartographic Engineer', 'Leandro França - Eng Cart'))

        # Abrir arquivo
        return {}
