# -*- coding: utf-8 -*-

"""
inventoryRaster.py
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
__date__ = '2020-11-29'
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
import os
import numpy as np
from qgis.PyQt.QtGui import QIcon

class InventoryRaster(QgsProcessingAlgorithm):

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
        return InventoryRaster()

    def name(self):
        return 'inventoryraster'

    def displayName(self):
        return self.tr('Raster data inventory', 'Inventário de dados raster')

    def group(self):
        return self.tr('Raster')

    def groupId(self):
        return 'raster'

    def tags(self):
        return self.tr('list,raster,load,detect,organize,inventory,bounding').split(',')

    def icon(self):
        return QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images/raster.png'))

    txt_en = 'Creates a vector layer with the inventory of raster files in a folder. The geometry type of the features of this layer can be Polygon (bounding box) or Point (centroid).'
    txt_pt = 'Cria uma camada vetorial com o inventário de arquivos raster de uma pasta. O tipo de geometria das feições dessa camada pode ser Polígono (retângulo envolvente) ou Ponto (centroide).'
    figure = 'images/tutorial/raster_inventory.jpg'

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
    GEOMETRY = 'GEOMETRY'
    OUTPUT = 'OUTPUT'
    CRS = 'CRS'

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
            QgsProcessingParameterEnum(
                self.GEOMETRY,
                self.tr('Geometry', 'Geometria'),
				options = [self.tr('Polygon','Polígono'), self.tr('Point','Ponto')],
                defaultValue= 0
            )
        )

        self.addParameter(
            QgsProcessingParameterCrs(
                self.CRS,
                self.tr('CRS', 'SRC'),
                'ProjectCrs'))

        # OUTPUT
        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT,
                self.tr('Inventory Layer', 'Camada de Inventário')
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

        geometria = self.parameterAsEnum(
            parameters,
            self.GEOMETRY,
            context
        )

        crs = self.parameterAsCrs(
            parameters,
            self.CRS,
            context
        )

        # OUTPUT
        GeomType = QgsWkbTypes.Point if geometria == 1 else QgsWkbTypes.Polygon
        Fields = QgsFields()
        itens  = {
                     self.tr('name','nome') : QVariant.String,
                     self.tr('extension','extensão') : QVariant.String,
                     self.tr('path', 'caminho') : QVariant.String,
                     self.tr('resX') : QVariant.Double,
                     self.tr('resY') : QVariant.Double,
                     self.tr('n_cols') : QVariant.Int,
                     self.tr('n_rows', 'n_lin') : QVariant.Int,
                     self.tr('crs','src') : QVariant.String,
                     self.tr('n_bands', 'n_bandas') : QVariant.Int,
                     self.tr('dataType', 'tipoDado') : QVariant.String,
                     }
        for item in itens:
            Fields.append(QgsField(item, itens[item]))

        (sink, dest_id) = self.parameterAsSink(
            parameters,
            self.OUTPUT,
            context,
            Fields,
            GeomType,
            crs
        )
        if sink is None:
            raise QgsProcessingException(self.invalidSinkError(parameters, self.OUTPUT))

        # Listar Arquivos
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

        # Obter dados dos arquivos listados
        feedback.pushInfo(self.tr('Creating raster files...', 'Criando inventário de arquivos raster...'))
        for current, file_path in enumerate(lista):
            image = gdal.Open(file_path) # https://gdal.org/python/
            prj = image.GetProjection() # wkt
            ulx, xres, xskew, uly, yskew, yres  = image.GetGeoTransform()
            GDT = image.GetRasterBand(1).DataType
            n_bands = image.RasterCount
            cols = image.RasterXSize # Number of columns
            rows = image.RasterYSize # Number of rows
            CRS= QgsCoordinateReferenceSystem(prj) # Create CRS
            image=None # Close image

            # Creating BBox
            coord = [[QgsPointXY(ulx, uly),
                      QgsPointXY(ulx+cols*xres, uly),
                      QgsPointXY(ulx+cols*xres, uly+rows*yres),
                      QgsPointXY(ulx, uly+rows*yres),
                      QgsPointXY(ulx, uly)]]
            geom = QgsGeometry.fromPolygonXY(coord)

            # CRS transformation
            coordinateTransformer = QgsCoordinateTransform()
            coordinateTransformer.setDestinationCrs(crs)
            coordinateTransformer.setSourceCrs(CRS)
            geom_transf = self.reprojectPoints(geom, coordinateTransformer)

            # Attributes
            path, file = os.path.split(file_path)
            name = os.path.splitext(file)[0]
            extension = os.path.splitext(file)[1]
            att = [name,
                   extension,
                   path,
                   abs(xres),
                   abs(yres),
                   cols,
                   rows,
                   CRS.description(),
                   n_bands,
                   gdal.GetDataTypeName(GDT)]

            # Saving feature
            feat = QgsFeature()
            feat.setGeometry(geom_transf.centroid()) if geometria == 1 else feat.setGeometry(geom_transf) # centroid or polygon
            feat.setAttributes(att)
            sink.addFeature(feat, QgsFeatureSink.FastInsert)

            if feedback.isCanceled():
                break
            feedback.setProgress(int((current+1) * total))

        feedback.pushInfo(self.tr('Operation completed successfully!', 'Operação finalizada com sucesso!'))
        feedback.pushInfo(self.tr('Leandro Franca - Cartographic Engineer', 'Leandro França - Eng Cart'))
        return {self.OUTPUT: dest_id}

    def reprojectPoints(self, geom, xform):
        if geom.type() == 0: #Point
            if geom.isMultipart():
                pnts = geom.asMultiPoint()
                newPnts = []
                for pnt in pnts:
                    newPnts += [xform.transform(pnt)]
                newGeom = QgsGeometry.fromMultiPointXY(newPnts)
                return newGeom
            else:
                pnt = geom.asPoint()
                newPnt = xform.transform(pnt)
                newGeom = QgsGeometry.fromPointXY(newPnt)
                return newGeom
        elif geom.type() == 1: #Line
            if geom.isMultipart():
                linhas = geom.asMultiPolyline()
                newLines = []
                for linha in linhas:
                    newLine =[]
                    for pnt in linha:
                        newLine += [xform.transform(pnt)]
                    newLines += [newLine]
                newGeom = QgsGeometry.fromMultiPolylineXY(newLines)
                return newGeom
            else:
                linha = geom.asPolyline()
                newLine =[]
                for pnt in linha:
                    newLine += [xform.transform(pnt)]
                newGeom = QgsGeometry.fromPolylineXY(newLine)
                return newGeom
        elif geom.type() == 2: #Polygon
            if geom.isMultipart():
                poligonos = geom.asMultiPolygon()
                newPolygons = []
                for pol in poligonos:
                    newPol = []
                    for anel in pol:
                        newAnel = []
                        for pnt in anel:
                            newAnel += [xform.transform(pnt)]
                        newPol += [newAnel]
                    newPolygons += [newPol]
                newGeom = QgsGeometry.fromMultiPolygonXY(newPolygons)
                return newGeom
            else:
                pol = geom.asPolygon()
                newPol = []
                for anel in pol:
                    newAnel = []
                    for pnt in anel:
                        newAnel += [xform.transform(pnt)]
                    newPol += [newAnel]
                newGeom = QgsGeometry.fromPolygonXY(newPol)
                return newGeom
        else:
            return None
