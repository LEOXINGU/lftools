# -*- coding: utf-8 -*-

"""
Rast_loadRasterByLocation.py
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
__date__ = '2020-12-11'
__copyright__ = '(C) 2020, Leandro França'

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
                       QgsProcessingParameterCrs,
                       QgsProcessingParameterEnum,
                       QgsProcessingParameterMultipleLayers,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterRasterLayer,
                       QgsProcessingParameterFile,
                       QgsFeatureRequest,
                       QgsExpression,
                       QgsProcessingParameterFeatureSink,
                       QgsProcessingParameterFileDestination,
                       QgsProcessingParameterRasterDestination,
                       QgsApplication,
                       QgsProject,
                       QgsRasterLayer,
                       QgsCoordinateTransform,
                       QgsCoordinateReferenceSystem)

from osgeo import osr, gdal_array, gdal #https://gdal.org/python/
from lftools.geocapt.imgs import Imgs
from lftools.geocapt.cartography import reprojectPoints
import os, shutil
import numpy as np
from qgis.PyQt.QtGui import QIcon

class LoadRasterByLocation(QgsProcessingAlgorithm):

    LOC = QgsApplication.locale()[:2]

    def translate(self, string):
        return QCoreApplication.translate('Processing', string)

    def tr(self, *string):
        # Traduzir para o portugês: arg[0] - english (translate), arg[1] - português
        if self.LOC == 'pt':
            if len(string) == 2:
                return string[1]
            else:
                return self.translate(string[0])
        else:
            return self.translate(string[0])

    def createInstance(self):
        return LoadRasterByLocation()

    def name(self):
        return 'loadrasterbylocation'

    def displayName(self):
        return self.tr('Load raster by location', 'Carregar raster pela localização')

    def group(self):
        return self.tr('Raster')

    def groupId(self):
        return 'raster'

    def tags(self):
        return self.tr('load,detect,organize,location,bounding').split(',')

    def icon(self):
        return QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images/raster.png'))

    txt_en = '''Loads a set of raster files that intersect the geometries of an input vector layer.
    Optionally, it is possible to copy the selected rasters and paste them in another folder.'''
    txt_pt = '''Carrega um conjunto de arquivos raster que interceptam as geometrias de uma camada vetorial de entrada.
    Opcionalmente é possível copiar os rasters selcionados e colar em outra pasta.'''
    figure = 'images/tutorial/raster_loadByLocation.jpg'

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


    FOLDER ='FOLDER'
    SUBFOLDER = 'SUBFOLDER'
    FORMAT = 'FORMAT'
    INPUT = 'INPUT'
    OUTPUTFOLDER = 'OUTPUTFOLDER'

    def initAlgorithm(self, config=None):
        # INPUT
        self.addParameter(
            QgsProcessingParameterFile(
                self.FOLDER,
                self.tr('Folder with raster files', 'Pasta com arquivos raster'),
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
            QgsProcessingParameterString(
                self.FORMAT,
                self.tr('Format', 'Formato'),
                defaultValue = '.tif'
            )
        )

        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT,
                self.tr('Vector Layer', 'Camada Vetorial'),
                [QgsProcessing.TypeVectorAnyGeometry]
            )
        )

        # OUTPUT
        self.addParameter(
            QgsProcessingParameterFile(
                self.OUTPUTFOLDER,
                self.tr('Destination folder', 'Pasta de destino'),
                behavior = QgsProcessingParameterFile.Folder,
                defaultValue = None,
                optional = True
            )
        )

    def processAlgorithm(self, parameters, context, feedback):

        pasta = self.parameterAsFile(
            parameters,
            self.FOLDER,
            context
        )
        if not pasta:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.FOLDER))

        subpasta = self.parameterAsBool(
            parameters,
            self.SUBFOLDER,
            context
        )

        formato = self.parameterAsString(
            parameters,
            self.FORMAT,
            context
        )

        source = self.parameterAsSource(
            parameters,
            self.INPUT,
            context
        )
        if source is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.INPUT))
        crs = source.sourceCrs()

        # Copiar arquivos selecionados
        saida = self.parameterAsFile(
            parameters,
            self.OUTPUTFOLDER,
            context
        )

        # List files
        feedback.pushInfo(self.tr('Checking files in the folder...', 'Checando arquivos na pasta...'))
        lista = []
        if subpasta:
            for root, dirs, files in os.walk(pasta, topdown=True):
                for name in files:
                    if name[-1*len(formato):] == formato:
                        lista += [os.path.join(root, name)]
        else:
            for item in os.listdir(pasta):
                if item[-1*len(formato):] == formato:
                    lista += [os.path.join(pasta, item)]

        total = 100.0 / len(lista) if len(lista)>0 else 0

        # Verify raster to be loaded
        feedback.pushInfo(self.tr('Verifying raster files...', 'Verificando arquivos raster...'))
        selecao = []
        for current, file_path in enumerate(lista):
            try:
                image = gdal.Open(file_path)
                prj = image.GetProjection() # wkt
                ulx, xres, xskew, uly, yskew, yres = image.GetGeoTransform()
                cols = image.RasterXSize # Number of columns
                rows = image.RasterYSize # Number of rows
                image=None # Close image

                # Creating BBox
                coord = [[QgsPointXY(ulx, uly),
                          QgsPointXY(ulx+cols*xres, uly),
                          QgsPointXY(ulx+cols*xres, uly+rows*yres),
                          QgsPointXY(ulx, uly+rows*yres),
                          QgsPointXY(ulx, uly)]]
                geom = QgsGeometry.fromPolygonXY(coord)

                # CRS transformation
                CRS= QgsCoordinateReferenceSystem(prj) # Create image CRS
                coordinateTransformer = QgsCoordinateTransform()
                coordinateTransformer.setDestinationCrs(crs)
                coordinateTransformer.setSourceCrs(CRS)
                geom_transf = reprojectPoints(geom, coordinateTransformer)

                for feat in source.getFeatures():
                    if geom_transf.intersects(feat.geometry()):
                        selecao += [file_path]
                        break

                if saida and os.path.exists(saida):
                    for caminho in selecao:
                        head, tail = os.path.split(caminho)
                        shutil.copy2(caminho, os.path.join(saida, tail))
            except:
                feedback.pushInfo(self.tr('Problem opening the file: {}'.format(file_path), 'Problema para abrir o arquivo: {}'.format(file_path)))

            if feedback.isCanceled():
                break
            feedback.setProgress(int((current+1) * total))

        self.LISTA = selecao
        self.FORMATO = formato
        feedback.pushInfo(self.tr('Operation completed successfully!', 'Operação finalizada com sucesso!'))
        feedback.pushInfo(self.tr('Leandro Franca - Cartographic Engineer', 'Leandro França - Eng Cart'))
        return {'files': self.LISTA}

    def postProcessAlgorithm(self, context, feedback):
        for file_path in self.LISTA:
            layer_name = os.path.basename(file_path)[:-1*(len(self.FORMATO))]
            rlayer = QgsRasterLayer(file_path, layer_name)
            QgsProject.instance().addMapLayer(rlayer)
        return {}
