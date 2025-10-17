# -*- coding: utf-8 -*-

"""
Drone_photosByBlocks.py
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
__date__ = '2021-11-07'
__copyright__ = '(C) 2021, Leandro França'

from qgis.core import (QgsApplication,
                       QgsProcessingParameterVectorLayer,
                       QgsGeometry,
                       QgsProcessing,
                       QgsProcessingParameterField,
                       QgsProcessingParameterString,
                       QgsProcessingParameterEnum,
                       QgsProcessingParameterBoolean,
                       QgsProcessingParameterFile,
                       QgsFeatureSink,
                       QgsProcessingException,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterFeatureSink)
from lftools.geocapt.imgs import Imgs
from lftools.translations.translate import translate
import os, shutil
from qgis.PyQt.QtGui import QIcon

class PhotosByBlocks(QgsProcessingAlgorithm):

    LOC = QgsApplication.locale()[:2]

    def tr(self, *string):
        return translate(string, self.LOC)

    def createInstance(self):
        return PhotosByBlocks()

    def name(self):
        return 'photosbyblocks'

    def displayName(self):
        return self.tr('Photos by blocks', 'Fotos por blocos')

    def group(self):
        return self.tr('Drones')

    def groupId(self):
        return 'drones'

    def tags(self):
        return 'GeoOne,drones,fotografia,photography,blocks,separate,separar,organize,organizar'.split(',')

    def icon(self):
        return QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images/drone.png'))

    txt_en = 'This tool separates drone photographs into new folders to be processed by blocks, from a layer of polygons (blocks) and from layers of geotagged photographs.'
    txt_pt = 'Esta ferramenta separa fotografias de drones em novas pastas para serem processadas por blocos, a partir de uma camada de polígonos (blocos) e da camadas de fotografias com geotag.'
    figure = 'images/tutorial/drone_photosByBlocks.jpg'

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

    POINTS = 'POINTS'
    FILEPATH = 'FILEPATH'
    BLOCKS = 'BLOCKS'
    PREFIX = 'PREFIX'
    FOLDER = 'FOLDER'

    def initAlgorithm(self, config=None):
        self.addParameter(
            QgsProcessingParameterVectorLayer(
                self.POINTS,
                self.tr('Points', 'Pontos'),
                [QgsProcessing.TypeVectorPoint]
            )
        )

        self.addParameter(
            QgsProcessingParameterField(
                self.FILEPATH,
                self.tr('Field with file path', 'Campo com o caminho do arquivo'),
                parentLayerParameterName=self.POINTS,
                type=QgsProcessingParameterField.String
            )
        )

        self.addParameter(
            QgsProcessingParameterVectorLayer(
                self.BLOCKS,
                self.tr('Blocks', 'Blocos'),
                [QgsProcessing.TypeVectorPolygon]
            )
        )

        self.addParameter(
            QgsProcessingParameterString(
                self.PREFIX,
                self.tr('Folder name prefix', 'Prefixo do nome da pasta'),
                defaultValue = self.tr('block_', 'bloco_')
            )
        )

        self.addParameter(
            QgsProcessingParameterFile(
                self.FOLDER,
                self.tr('Folder with raster files', 'Pasta com arquivos raster'),
                behavior=QgsProcessingParameterFile.Folder,
                defaultValue=None
            )
        )

    def processAlgorithm(self, parameters, context, feedback):

        pontos = self.parameterAsVectorLayer(
            parameters,
            self.POINTS,
            context
        )
        if pontos is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.POINTS))

        poligono = self.parameterAsVectorLayer(
            parameters,
            self.BLOCKS,
            context
        )
        if poligono is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.BLOCKS))

        campo = self.parameterAsFields(
            parameters,
            self.FILEPATH,
            context
        )
        if campo is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.FILEPATH))

        columnIndex = pontos.fields().indexFromName(campo[0])

        prefixo = self.parameterAsString(
            parameters,
            self.PREFIX,
            context
        )

        pasta = self.parameterAsFile(
            parameters,
            self.FOLDER,
            context
        )
        if not pasta:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.FOLDER))

        # As duas camadas devem ter o mesmo SRC
        if poligono.crs() != pontos.crs():
            raise QgsProcessingException(self.tr('Both layers must have the same CRS!', 'As duas camadas devem ter o mesmo SRC!'))

        # Copiando arquivos para as novas pastas
        total = 100.0 / (poligono.featureCount()*pontos.featureCount())
        block_count, cont = 1, 1
        for pol in poligono.getFeatures():
            geom_pol = pol.geometry()
            destino = os.path.join(pasta, prefixo + str(block_count))
            os.mkdir(destino)
            for pnt in pontos.getFeatures():
                geom_pnt = pnt.geometry()
                if geom_pnt.intersects(geom_pol):
                    origem = pnt[columnIndex]
                    nome = os.path.split(origem)[-1]
                    shutil.copy2(origem, os.path.join(destino, nome))
                if feedback.isCanceled():
                    break
                feedback.setProgress(int((cont) * total))
                cont += 1
            block_count += 1

        feedback.pushInfo(self.tr('Operation completed successfully!', 'Operação finalizada com sucesso!'))
        feedback.pushInfo(self.tr('Leandro Franca - Cartographic Engineer', 'Leandro França - Eng Cart'))

        return {}
