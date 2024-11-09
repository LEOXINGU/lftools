# -*- coding: utf-8 -*-

"""
Relief_SetZfromDEM.py
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
__date__ = '2024-11-09'
__copyright__ = '(C) 2024, Leandro França'

from PyQt5.QtCore import QCoreApplication, QVariant
from qgis.core import *
from osgeo import osr, gdal_array, gdal #https://gdal.org/python/
import numpy as np
from pyproj.crs import CRS
from lftools.geocapt.imgs import Imgs
from lftools.geocapt.cartography import LayerIs3D
from lftools.translations.translate import translate
from lftools.geocapt.dip import Interpolar
import os, processing
from qgis.PyQt.QtGui import QIcon

class SetZfromDEM(QgsProcessingAlgorithm):

    LOC = QgsApplication.locale()[:2]

    def tr(self, *string):
        return translate(string, self.LOC)

    def createInstance(self):
        return SetZfromDEM()

    def name(self):
        return 'SetZfromDEM'.lower()

    def displayName(self):
        return self.tr('Set Z coordinate from DEM', 'Definir coordenada Z pelo MDE')

    def group(self):
        return self.tr('Relief', 'Relevo')

    def groupId(self):
        return 'relief'

    def tags(self):
        return self.tr('dem,dsm,dtm,txt,texto,mde,mdt,mds,terreno,relevo,contour,elevation,height,elevação').split(',')

    def icon(self):
        return QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images/contours.png'))

    txt_en = '''This tool replaces the Z coordinates of an existing layer with the value of the nearest cell from a Digital Elevation Model (DEM).'''
    txt_pt = '''Esta ferramenta substitui as coordenadas Z de uma camada existente pelo valor da célula mais próxima de um Modelo Digital de Elevação (MDE).'''
    figure = 'images/tutorial/relief_dem2txt.jpg'

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
    DEM ='DEM'
    SAVE = 'SAVE'
    SELECTED = 'SELECTED'

    def initAlgorithm(self, config=None):

        # INPUT
        self.addParameter(
            QgsProcessingParameterVectorLayer(
                self.INPUT,
                self.tr('Input Layer', 'Camada de entrada'),
                [QgsProcessing.TypeVectorAnyGeometry]
            )
        )

        self.addParameter(
            QgsProcessingParameterBoolean(
                self.SELECTED,
                self.tr('Only selected', 'Apenas feições selecionadas'),
                defaultValue=False
            )
        )

        self.addParameter(
            QgsProcessingParameterRasterLayer(
                self.DEM,
                self.tr('DEM', 'MDE'),
                [QgsProcessing.TypeRaster]
            )
        )

        self.addParameter(
            QgsProcessingParameterBoolean(
                self.SAVE,
                self.tr('Save Editions', 'Salvar Edições'),
                defaultValue = True
            )
        )

    def processAlgorithm(self, parameters, context, feedback):

        # inputs
        MDE = self.parameterAsRasterLayer(
            parameters,
            self.DEM,
            context
        )
        if MDE is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.DEM))

        camada = self.parameterAsVectorLayer(
            parameters,
            self.INPUT,
            context
        )
        if camada is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.INPUT))
        # Verificar se a camada de entrada tem a coordenada Z
        if not LayerIs3D(camada):
            raise QgsProcessingException(self.tr('Input layer has no Z dimension', 'Camada de entrada não possui dimensão Z'))

        selecionados = self.parameterAsBool(
            parameters,
            self.SELECTED,
            context
        )
        if selecionados is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.SELECTED))

        salvar = self.parameterAsBool(
            parameters,
            self.SAVE,
            context
        )
        if salvar is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.SAVE))

        # Criar coluna de ID
        layerID = processing.run("native:fieldcalculator",
                            {'INPUT': camada, 'FIELD_NAME':'campoID','FIELD_TYPE':1,'FIELD_LENGTH':0,'FIELD_PRECISION':0,'FORMULA':'$id',
                            'OUTPUT':'TEMPORARY_OUTPUT'})
        layerID = layerID['OUTPUT']
        # Definir coordenada Z
        feedback.pushInfo(self.tr('Defining Z coordinate...', 'Definindo coordenada Z...'))
        layer3D = processing.run("native:setzfromraster",
                    {'INPUT': layerID,
                     'RASTER': MDE,
                     'BAND':1, 'NODATA':0, 'SCALE':1, 'OFFSET':0,
                     'OUTPUT':'TEMPORARY_OUTPUT'})
        layer3D = layer3D['OUTPUT']

        dic = {}
        for feat in layer3D.getFeatures():
            dic[feat['campoID']] = feat.geometry()

        camada.startEditing() # coloca no modo edição
        feedback.pushInfo(self.tr('Saving results...', 'Salvando resultados...'))

        if not selecionados:
            total = 100.0 / camada.featureCount() if camada.featureCount() else 0
            for current, feat in enumerate(camada.getFeatures()):
                cont = 0
                geom = feat.geometry()
                new_geom = dic[feat.id()]
                camada.changeGeometry(feat.id(), new_geom)
                feedback.setProgress(int(current * total))
        else:
            total = 100.0 / camada.selectedFeatureCount() if camada.selectedFeatureCount() else 0
            for current, feat in enumerate(camada.getSelectedFeatures()):
                cont = 0
                geom = feat.geometry()
                new_geom = dic[feat.id()]
                camada.changeGeometry(feat.id(), new_geom)
                feedback.setProgress(int(current * total))

        if salvar:
            camada.commitChanges() # salva as edições

        feedback.pushInfo(self.tr('Operation completed successfully!', 'Operação finalizada com sucesso!'))
        feedback.pushInfo(self.tr('Leandro Franca - Cartographic Engineer', 'Leandro França - Eng Cart'))

        return {}
