# -*- coding: utf-8 -*-

"""
Drone_PhotosHistogramMatch.py
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
__date__ = '2023-06-17'
__copyright__ = '(C) 2023, Leandro França'

from PyQt5.QtCore import QCoreApplication, QVariant
from qgis.core import (QgsProcessing,
                       QgsFeatureSink,
                       QgsWkbTypes,
                       QgsFields,
                       QgsField,
                       QgsFeature,
                       QgsPointXY,
                       QgsGeometry,
                       QgsProcessingException,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterString,
                       QgsProcessingParameterNumber,
                       QgsProcessingParameterField,
                       QgsProcessingParameterBoolean,
                       QgsProcessingParameterFile,
                       QgsProcessingParameterEnum,
                       QgsFeatureRequest,
                       QgsExpression,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterFeatureSink,
                       QgsProcessingParameterFileDestination,
                       QgsProcessingParameterVectorLayer,
                       QgsProcessingParameterRasterLayer,
                       QgsProcessingParameterRasterDestination,
                       QgsApplication,
                       QgsProject,
                       QgsRasterLayer,
                       QgsCoordinateTransform,
                       QgsCoordinateReferenceSystem)

import numpy as np
from lftools.geocapt.imgs import Imgs
from lftools.translations.translate import translate
from lftools.geocapt.dip import Interpolar
from lftools.geocapt.adjust import AjustVertical, ValidacaoGCP, Ajust2D, ValidacaoVetores
from lftools.geocapt.cartography import geom2PointList
import os
from qgis.PyQt.QtGui import QIcon
from PIL import Image
import matplotlib.pyplot as plt

class PhotosHistogramMatch(QgsProcessingAlgorithm):

    LOC = QgsApplication.locale()[:2]

    def tr(self, *string):
        return translate(string, self.LOC)

    def createInstance(self):
        return PhotosHistogramMatch()

    def name(self):
        return 'photoshistogrammatch'

    def displayName(self):
        return self.tr('Photos Histogram Matching', 'Casar histogramas de fotos')

    def group(self):
        return self.tr('Drones')

    def groupId(self):
        return 'drones'

    def tags(self):
        return self.tr('drone,match,mosaic,casar,ajuste,casamento,ajustamento,equalização,equalization,adjustment,histograma,fotos').split(',')

    def icon(self):
        return QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images/drone.png'))

    txt_en = '''This tool performs histogram matching of the JPEG photo files of one input photo layer relative to another reference photo layer.'''
    txt_pt = '''Esta ferramenta realiza o casamento do histograma dos arquivos de fotos JPEG de uma camada de fotografias de entrada em relação a outra camada de fotografias de referência.'''
    figure = 'images/tutorial/drone_histogram.jpg'

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

    INPUT = 'INPUT'
    REFERENCE = 'REFERENCE'
    FOLDER = 'FOLDER'

    def initAlgorithm(self, config=None):
        # INPUT
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT,
                self.tr('Input photo layer', 'Camada de fotos a serem ajustadas'),
                [QgsProcessing.TypeVectorPoint]
            )
        )

        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.REFERENCE,
                self.tr('Layer of reference photos', 'Fotos de Referência'),
                [QgsProcessing.TypeVectorPoint]
            )
        )

        # OUTPUT
        self.addParameter(
            QgsProcessingParameterFile(
                self.FOLDER,
                self.tr('Destination folder', 'Pasta de destino'),
                behavior = QgsProcessingParameterFile.Folder
            )
        )

    def processAlgorithm(self, parameters, context, feedback):

        # camada de fotos a serem ajustadas
        ajust = self.parameterAsSource(
            parameters,
            self.INPUT,
            context
        )
        if ajust is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.INPUT))

        # camada de fotos de referência
        ref = self.parameterAsSource(
            parameters,
            self.REFERENCE,
            context
        )
        if ref is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.REFERENCE))

        # pasta de destino
        pasta = self.parameterAsFile(
            parameters,
            self.FOLDER,
            context
        )
        if not pasta:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.FOLDER))

        # distancia
        def distancia1(geom1, geom2):
            p1 = geom1.asPoint()
            x1,y1 =  p1.x(),  p1.y()
            p2 = geom2.asPoint()
            x2,y2 =  p2.x(),  p2.y()
            return np.sqrt((x1-x2)**2 + (y1-y2)**2)

        # Para cada imagem a ser ajustada encontrar a foto mais próxima
        feedback.pushInfo(self.tr('Histogram matching...', 'Casamento de histograma...'))
        Percent = 100.0/ajust.featureCount() if ajust.featureCount() else 0

        for current, feat1 in enumerate(ajust.getFeatures()):
            geom1 = feat1.geometry()
            caminho = feat1[self.tr('path','caminho')]
            nome = feat1[self.tr('name','nome')]
            dist = 1e10
            for feat2 in ref.getFeatures():
                geom2 = feat2.geometry()
                distancia = distancia1(geom1,geom2)
                if distancia < dist:
                    dist = distancia
                    caminho_ref = feat2[self.tr('path','caminho')]
                    nome_ref = feat2[self.tr('name','nome')]

            # Abrir imagem de referência
            img = Image.open(caminho_ref)
            rgb = np.asarray(img)
            img = None

            # Calcular média e desvio padrão por banda
            R = rgb[..., 0]
            G = rgb[..., 1]
            B = rgb[..., 2]
            meanR_ref, stdR_ref = R.mean(), R.std()
            meanG_ref, stdG_ref = G.mean(), G.std()
            meanB_ref, stdB_ref = B.mean(), B.std()

            del rgb

            # Abrir imagem a ser ajustada
            img = Image.open(caminho)
            exif = img.info['exif']
            rgb = np.asarray(img)
            R = rgb[..., 0]
            G = rgb[..., 1]
            B = rgb[..., 2]
            meanR, stdR = R.mean(), R.std()
            meanG, stdG = G.mean(), G.std()
            meanB, stdB = B.mean(), B.std()

            # Normalizar imagem a ser ajustada
            R_norm = (R - meanR)/stdR
            G_norm = (G - meanG)/stdG
            B_norm = (B - meanB)/stdB

            # Calibrar parâmetros de acordo com a imagem de referência
            R = np.round(R_norm*stdR_ref + meanR_ref)
            G = np.round(G_norm*stdG_ref + meanG_ref)
            B = np.round(B_norm*stdB_ref + meanB_ref)

            R = R*((R>0)*(R<256)) + 255*(R>255)
            G = G*((G>0)*(G<256)) + 255*(G>255)
            B = B*((B>0)*(B<256)) + 255*(B>255)

            RGB = np.dstack((R,G,B))

            # Salvar imagem ajustada
            nova_img = Image.fromarray(np.uint8(RGB))
            nova_img.save(os.path.join(pasta,nome), quality=90, subsampling=0, exif=exif)

            if feedback.isCanceled():
                break
            feedback.setProgress(int((current + 1) * Percent))


        feedback.pushInfo(self.tr('Operation completed successfully!', 'Operação finalizada com sucesso!'))
        feedback.pushInfo(self.tr('Leandro Franca - Cartographic Engineer', 'Leandro França - Eng Cart'))

        return {self.FOLDER: pasta}
