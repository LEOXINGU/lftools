# -*- coding: utf-8 -*-

"""
VR360_Equiretangular2Cubemap.py
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
                       QgsProcessingAlgorithm)

from lftools.geocapt.imgs import Imgs
from lftools.geocapt.vr360 import generate_cube_face_from_image
from lftools.translations.translate import translate
from qgis.PyQt.QtGui import QIcon
import numpy as np
import os
from PIL import Image


class Equiretangular2Cubemap(QgsProcessingAlgorithm):

    LOC = QgsApplication.locale()[:2]

    def tr(self, *string):
        return translate(string, self.LOC)

    def createInstance(self):
        return Equiretangular2Cubemap()

    def name(self):
        return 'Equiretangular2Cubemap'.lower()

    def displayName(self):
        return self.tr('Equirectangular to Cubemap', 'Equiretangular para Cubemap (Gerar Faces)')

    def group(self):
        return self.tr('VR 360°', 'RV 360°')

    def groupId(self):
        return 'vr360'

    def tags(self):
        return 'GeoOne,virtual,reality,realidade,esphere,esférica,360,graus,photography,photos,fotos,fotografia,gopro,insta360,VR,RV,cubemap,cubo,faces'.split(',')

    def icon(self):
        return QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images/rv_360.png'))

    txt_en = '''Converts a 360° image in equirectangular format into six images corresponding to the faces of a cube (cubemap).
The tool automatically creates a folder next to the original file and saves the faces using the original filename plus the face suffix (+X, −X, +Y, −Y, +Z, −Z).
These images can be opened in external editors for tasks such as anonymization, blurring, fixing artifacts near the poles, or inserting additional information.
The face resolution can be defined by the user, allowing a balance between performance and visual quality.'''
    txt_pt = '''Converte uma imagem 360° no formato equiretangular em seis imagens correspondentes às faces de um cubo (cubemap).
A ferramenta cria automaticamente uma pasta ao lado do arquivo original e salva as faces com o nome do arquivo seguido do sufixo da face (+X, −X, +Y, −Y, +Z, −Z).
Essas imagens podem ser abertas em editores externos para tarefas como anonimização, borramento, correções nos polos ou inserção de informações.
A resolução das faces pode ser definida pelo usuário, permitindo escolher entre desempenho e qualidade visual.'''
    figure = 'images/tutorial/vr360_eq_cube.jpg'

    def shortHelpString(self):
        social_BW = Imgs().social_BW

        footer = '''<div align="center">
                      <img src="'''+ os.path.join(os.path.dirname(os.path.dirname(__file__)), self.figure) +'''">
                      </div>
                      <div align="left">
                      <p>
                      <b><a href="'''+ self.tr('https://portal.geoone.com.br/m/lessons/mapeamento360?classId=5995') + '''" target="_blank">'''+ self.tr('Click here to watch a full class on this tool',
                                    'Clique aqui para assistir uma aula completa sobre esta ferramenta') +'''</a></b>
                      </p>
                      <p>
                      <b><a href="'''+ self.tr('https://geoone.com.br/pvmapeamento360/') + '''" target="_blank">'''+ self.tr('Enroll in the 360° VR course in QGIS.',
                                    'Inscreva-se no curso de RV 360° no QGIS') +'</a><br><br>'+ self.tr('Author: Leandro Franca', 'Autor: Leandro França')+'''</b>
                      </p>'''+ social_BW + '''
                    </div>'''
        return self.tr(self.txt_en, self.txt_pt) + footer

    FILE = 'FILE'
    SIZE = 'SIZE'

    def initAlgorithm(self, config=None):

        self.addParameter(
            QgsProcessingParameterFile(
                self.FILE,
                self.tr('Equirectangular image (360°)', 'Imagem equiretangular (360°)'),
                behavior = QgsProcessingParameterFile.File,
                fileFilter = 'Image (*.jpeg *.jpg *.JPG)'
            )
        )

        self.addParameter(
            QgsProcessingParameterNumber(
                self.SIZE,
                self.tr('Face resolution (N × N)', 'Resolução das faces (N x N)'),
                type = QgsProcessingParameterNumber.Type.Integer,
                minValue = 200,
                defaultValue = 2000
                )
            )

    def processAlgorithm(self, parameters, context, feedback):

        # Entradas
        # caminho da sua foto 360 original
        input_path = self.parameterAsFile(
            parameters,
            self.FILE,
            context
        )
        if not input_path:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.FILE))

        # resolução das faces do cubo
        N = self.parameterAsInt(
            parameters,
            self.SIZE,
            context
        )             

        # Ler imagem original
        img = Image.open(input_path)
        # exif_data = img.info.get("exif", None)

        # Condição para ser equiretangular
        W, H = img.size
        ratio = W / H
        if ratio != 2:
            raise QgsProcessingException(f"Invalid input: equirectangular images must be 2:1 (found {ratio:.1f}:1)!")

        img_np = np.array(img)

        # Caminho/base para criar a pasta das faces
        folder, filename = os.path.split(input_path)
        basename, _ = os.path.splitext(filename)

        # Pasta das faces: mesmo local da foto, com sufixo "_faces"
        faces_dir = os.path.join(folder, basename + "_faces")
        os.makedirs(faces_dir, exist_ok=True)

        # Gerar e salvar as 6 faces
        faces = ["+X", "-X", "+Y", "-Y", "+Z", "-Z"]

        for face in faces:
            feedback.pushInfo(self.tr(f'Generating face {face}...', f'Gerando face {face}...'))
            face_np = generate_cube_face_from_image(img_np, face, N)
            face_img = Image.fromarray(face_np.astype(np.uint8))

            # nome do arquivo: <basename>_<face>.png, dentro da pasta
            out_name = f"{basename}_{face}.png"
            out_path = os.path.join(faces_dir, out_name)
            face_img.save(out_path)
            # face_img.save(out_path, exif=exif_data)

        feedback.pushInfo(self.tr('Operation completed successfully!', 'Operação finalizada com sucesso!'))
        feedback.pushInfo(self.tr('Leandro Franca - Cartographic Engineer', 'Leandro França - Eng Cart'))

        # Abrir pasta

        return {'FOLDER': folder}
