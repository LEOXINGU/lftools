# -*- coding: utf-8 -*-

"""
VR360_ExtractPerspectiveView.py
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
__date__ = '2026-01-27'
__copyright__ = '(C) 2026, Leandro França'

from qgis.core import (QgsApplication,
                       QgsProcessingParameterFile,
                       QgsProcessingParameterNumber,
                       QgsProcessingException,
                       QgsProcessingParameterFileDestination,
                       QgsProcessingAlgorithm)

from lftools.geocapt.imgs import Imgs
from lftools.geocapt.vr360 import extract_perspective_from_equirect
from lftools.translations.translate import translate
from qgis.PyQt.QtGui import QIcon
import os
from PIL import Image
import numpy as np


class ExtractPerspectiveView(QgsProcessingAlgorithm):

    LOC = QgsApplication.locale()[:2]

    def tr(self, *string):
        return translate(string, self.LOC)

    def createInstance(self):
        return ExtractPerspectiveView()

    def name(self):
        return 'ExtractPerspectiveView'.lower()

    def displayName(self):
        return self.tr('Extract Perspective View', 'Extrair vista perspectiva')

    def group(self):
        return self.tr('VR 360°', 'RV 360°')

    def groupId(self):
        return 'vr360'

    def tags(self):
        return 'GeoOne,virtual,reality,realidade,esphere,esférica,360°,graus,photography,photos,fotos,fotografia,gopro,insta360,VR,RV,perspective,perspectiva,crop,recorte,FOV'.split(',')

    def icon(self):
        return QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images/rv_360.png'))

    txt_en = 'Extracts a perspective (pinhole) image from a 360° equirectangular image, simulating the framing of a conventional camera oriented toward a specified viewing direction.'
    txt_pt = 'Extrai uma imagem em projeção perspectiva (pinhole) a partir de uma imagem 360° no formato equiretangular, simulando o enquadramento de uma câmera convencional orientada para uma direção específica no espaço.'
    figure = 'images/tutorial/vr360_extract_perspective.jpg'

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

    INPUT = 'INPUT'
    LAT = 'LAT'
    LON = 'LON'
    FOV = 'FOV'
    W = 'W'
    H = 'H'
    ROLL = 'ROLL'
    OUTPUT = 'OUTPUT'

    def initAlgorithm(self, config=None):

        self.addParameter(
            QgsProcessingParameterFile(
                self.INPUT,
                self.tr('Equirectangular image (360°)', 'Imagem equiretangular (360°)'),
                behavior=QgsProcessingParameterFile.File,
                fileFilter='Image (*.jpeg *.jpg *.JPG)'
            )
        )

        self.addParameter(
            QgsProcessingParameterNumber(
                self.LAT,
                self.tr('Perspective center – latitude', 'Centro da perspectiva - latitude'),
                type=QgsProcessingParameterNumber.Type.Double,
                minValue=-90.0,
                maxValue=90.0,
                defaultValue=0.0
            )
        )

        self.addParameter(
            QgsProcessingParameterNumber(
                self.LON,
                self.tr('Perspective center – longitude', 'Centro da perspectiva - longitude'),
                type=QgsProcessingParameterNumber.Type.Double,
                minValue=-180.0,
                maxValue=180.0,
                defaultValue=0.0
            )
        )

        self.addParameter(
            QgsProcessingParameterNumber(
                self.FOV,
                self.tr('Horizontal field of view (°)', 'Campo de visão horizontal (°)'),
                type=QgsProcessingParameterNumber.Type.Double,
                minValue=30.0,
                maxValue=110.0,
                defaultValue=90.0
            )
        )

        self.addParameter(
            QgsProcessingParameterNumber(
                self.W,
                self.tr('Output image width (pixels)', 'Largura da imagem de saída (pixels)'),
                type=QgsProcessingParameterNumber.Type.Integer,
                minValue=256,
                maxValue=8192,
                defaultValue=1920
            )
        )

        self.addParameter(
            QgsProcessingParameterNumber(
                self.H,
                self.tr('Output image height (pixels)', 'Altura da imagem de saída (pixels)'),
                type=QgsProcessingParameterNumber.Type.Integer,
                minValue=256,
                maxValue=8192,
                defaultValue=1080
            )
        )

        self.addParameter(
            QgsProcessingParameterNumber(
                self.ROLL,
                self.tr('Camera roll (°)', 'Rotação da câmera (roll) (°)'),
                type=QgsProcessingParameterNumber.Type.Double,
                minValue=-180.0,
                maxValue=180.0,
                defaultValue=0.0
            )
        )

        # OUTPUT
        self.addParameter(
            QgsProcessingParameterFileDestination(
                self.OUTPUT,
                self.tr('Perspective view image', 'Imagem de vista perspectiva'),
                fileFilter='Image (*.jpg)'
            )
        )


    def processAlgorithm(self, parameters, context, feedback):        
        
        # INPUT (imagem equiretangular)
        entrada = self.parameterAsFile(parameters, self.INPUT, context)
        if not entrada:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.INPUT))

        # Parâmetros numéricos
        center_lat = self.parameterAsDouble(parameters, self.LAT, context)
        center_lon = self.parameterAsDouble(parameters, self.LON, context)
        fov = self.parameterAsDouble(parameters, self.FOV, context)
        w = self.parameterAsInt(parameters, self.W, context)
        h = self.parameterAsInt(parameters, self.H, context)
        roll = self.parameterAsDouble(parameters, self.ROLL, context)

        # OUTPUT (arquivo de saída)
        saida = self.parameterAsFileOutput(parameters, self.OUTPUT, context)
        if not saida:
            raise QgsProcessingException(self.invalidSinkError(parameters, self.OUTPUT))

        # Checagem rápida equiretangular ~2:1
        img_pil = Image.open(entrada)
        exif_bytes = img_pil.info.get("exif", None)
        W_eq, H_eq = img_pil.size
        ratio = W_eq / H_eq
        if not (1.94 <= ratio <= 2.06):
            raise QgsProcessingException(
                self.tr(
                    f'Input image does not appear to be equirectangular (expected ~2:1, found {ratio:.3f}).',
                    f'A imagem de entrada não parece ser equiretangular (esperado ~2:1, encontrado {ratio:.3f}).'
                )
            )

        feedback.pushInfo(self.tr('Reading input image...', 'Lendo imagem de entrada...'))

        # Carrega como RGB
        img_eq = np.array(img_pil.convert("RGB"))

        feedback.pushInfo(self.tr('Extracting perspective view...', 'Extraindo vista perspectiva...'))
        feedback.setProgress(30)

        # Gera a vista perspectiva
        view = extract_perspective_from_equirect(
            img_eq,
            center_lat=center_lat,
            center_lon=center_lon,
            fov_h=fov,
            w=w,
            h=h,
            roll=roll,
            interp="nearest"
        )

        feedback.setProgress(90)
        feedback.pushInfo(self.tr('Saving output image...', 'Salvando imagem de saída...'))

        out = Image.fromarray(view)
        if exif_bytes:
            out.save(saida, exif=exif_bytes)
        else:
            out.save(saida)

        feedback.setProgress(100)
        feedback.pushInfo(self.tr('Operation completed successfully!', 'Operação finalizada com sucesso!'))
        feedback.pushInfo(self.tr('Leandro Franca - Cartographic Engineer', 'Leandro França - Eng Cart'))

        return {self.OUTPUT: saida}
