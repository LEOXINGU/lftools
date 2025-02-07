# -*- coding: utf-8 -*-

"""
Vect_ReprojectGPKG.py
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
__date__ = '2024-10-19'
__copyright__ = '(C) 2024, Leandro França'

from PyQt5.QtCore import QCoreApplication, QVariant
from qgis.core import (QgsProcessing,
                       QgsFeatureSink,
                       QgsWkbTypes,
                       QgsVectorLayer,
                       QgsFields,
                       QgsField,
                       QgsPoint,
                       QgsFeature,
                       QgsGeometry,
                       QgsVectorFileWriter,
                       QgsProcessingException,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterFile,
                       QgsProcessingParameterEnum,
                       QgsProcessingParameterNumber,
                       QgsFeatureRequest,
                       QgsProcessingUtils,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterFeatureSink,
                       QgsProcessingParameterFileDestination,
                       QgsProcessingParameterRasterLayer,
                       QgsProcessingParameterRasterDestination,
                       QgsApplication,
                       QgsProcessingParameterCrs,
                       QgsProcessingParameterBoolean,
                       QgsProject,
                       QgsRasterLayer,
                       QgsCoordinateTransform,
                       QgsProcessingLayerPostProcessorInterface,
                       QgsCoordinateReferenceSystem)

from lftools.geocapt.imgs import Imgs
from lftools.translations.translate import translate
from qgis.PyQt.QtGui import QIcon
import processing, os


class ReprojectGPKG(QgsProcessingAlgorithm):

    LOC = QgsApplication.locale()[:2]

    def tr(self, *string):
        return translate(string, self.LOC)

    def createInstance(self):
        return ReprojectGPKG()

    def name(self):
        return 'reprojectgpkg'

    def displayName(self):
        return self.tr('Reproject GeoPackage', 'Reprojetar GeoPackage')

    def group(self):
        return self.tr('Vector', 'Vetor')

    def groupId(self):
        return 'vector'

    def tags(self):
        return self.tr('GPKG,GeoPackage,TopoGeo,convert,reprojetar,transform,coordinate,CRS,SRC,pacote').split(',')

    def icon(self):
        return QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images/vetor.png'))

    txt_en = 'This tool allows for the automatic conversion and reprojection of all vector layers present in a GeoPackage (.GPKG) file to a new Coordinate Reference System (CRS) defined by the user. The tool simplifies working with multiple layers while maintaining the integrity of the vector data by reprojecting them in batch.'
    txt_pt = 'Esta ferramenta permite a conversão e reprojeção automática de todas as camadas vetoriais presentes em um arquivo GeoPackage (.GPKG) para um novo Sistema de Referência de Coordenadas (SRC) definido pelo usuário. A ferramenta facilita o trabalho com múltiplas camadas, mantendo a integridade dos dados vetoriais ao reprojetá-los em lote.'

    figure = 'images/tutorial/vect_reprojectGPKG.jpg'

    def shortHelpString(self):
        social_BW = Imgs().social_BW
        footer = '''<div align="center">
                      <img src="'''+ os.path.join(os.path.dirname(os.path.dirname(__file__)), self.figure) +'''">
                      </div>
                      <div align="right">
                      <p align="right">
                      <b>'''+self.tr('Author: Leandro Franca', 'Autor: Leandro França')+'''</b>
                      </p>'''+ social_BW + '''</div>
                      '''
        return self.tr(self.txt_en, self.txt_pt) + footer

    INPUT = 'INPUT'
    OUTPUT = 'OUTPUT'
    CRS = 'CRS'
    PROJECTED = 'PROJECTED'
    INSTANTIATED = 'INSTANTIATED'

    def initAlgorithm(self, config=None):

        self.addParameter(
            QgsProcessingParameterFile(
                self.INPUT,
                self.tr('Input GeoPackage'),
                behavior = QgsProcessingParameterFile.File,
                fileFilter = 'GeoPackage (*.gpkg)'
            )
        )

        self.addParameter(
            QgsProcessingParameterCrs(
                self.CRS,
                self.tr('CRS', 'SRC'),
                QgsProject.instance().crs()
                )
            )

        self.addParameter(
            QgsProcessingParameterBoolean(
                self.PROJECTED,
                self.tr('Allow projected CRS', 'Permitir SRC projetado'),
                defaultValue = False
            )
        )

        self.addParameter(
            QgsProcessingParameterBoolean(
                self.INSTANTIATED,
                self.tr('Only instantiated layers', 'Apenas camadas instanciadas'),
                defaultValue = False
            )
        )

        self.addParameter(
            QgsProcessingParameterFileDestination(
                self.OUTPUT,
                self.tr('Output GeoPackage'),
                fileFilter = 'GeoPackage (*.gpkg)'
            )
        )


    def processAlgorithm(self, parameters, context, feedback):

        inputGPKG = self.parameterAsFile(
            parameters,
            self.INPUT,
            context
        )
        if not inputGPKG:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.INPUT))

        outputGPKG = self.parameterAsFileOutput(
            parameters,
            self.OUTPUT,
            context
        )
        if not inputGPKG:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.OUTPUT))

        out_CRS = self.parameterAsCrs(
            parameters,
            self.CRS,
            context
        )

        Projetado = self.parameterAsBool(
            parameters,
            self.PROJECTED,
            context
        )

        Instanciado = self.parameterAsBool(
            parameters,
            self.INSTANTIATED,
            context
        )

        if not Projetado:
            if not out_CRS.isGeographic():
                raise QgsProcessingException(self.tr('Choose a geographic CRS!', 'Escolha um SRC geográfico!'))

        layer = QgsVectorLayer(inputGPKG,"test","ogr")
        subLayers = layer.dataProvider().subLayers()

        layers = []

        for subLayer in subLayers:
            name = subLayer.split('!!::!!')[1]
            uri = "%s|layername=%s" % (inputGPKG, name,)
            # Create layer
            sub_vlayer = QgsVectorLayer(uri, name, 'ogr')
            if sub_vlayer.isValid():
                # Reprojetar camada
                feedback.pushInfo(self.tr('Converting layer {}...', 'Convertendo camada {}...').format(name))
                layer = processing.run("native:reprojectlayer",
                            {'INPUT': sub_vlayer,
                             'TARGET_CRS': out_CRS,
                             'CONVERT_CURVED_GEOMETRIES':False,'OPERATION':'+proj=noop',
                             'OUTPUT':'TEMPORARY_OUTPUT'})
                layer = layer['OUTPUT']
                newlayer = QgsVectorLayer(layer.dataProvider().dataSourceUri(), name, 'memory')
                DP = newlayer.dataProvider()

                # Transformação de coordenadas
                coordinateTransformer = QgsCoordinateTransform(sub_vlayer.crs(), out_CRS, QgsProject.instance())

                for feat in sub_vlayer.getFeatures():
                    geom = feat.geometry()
                    geom.transform(coordinateTransformer)
                    newfeat = feat
                    newfeat.setGeometry(geom)
                    DP.addFeature(newfeat)
                    if Instanciado:
                        layers += [newlayer]

                if not Instanciado:
                    layers += [newlayer]

        params = {'LAYERS': layers,
                  'OUTPUT': outputGPKG,
                  'OVERWRITE': False,  # Important!
                  'SAVE_STYLES': False,
                  'SAVE_METADATA': False,
                  'SELECTED_FEATURES_ONLY': False}

        processing.run("native:package", params)

        feedback.pushInfo(self.tr('Operation completed successfully!', 'Operação finalizada com sucesso!'))
        feedback.pushInfo(self.tr('Leandro Franca - Cartographic Engineer', 'Leandro França - Eng Cart'))

        return {self.OUTPUT: outputGPKG}
