# -*- coding: utf-8 -*-

"""
createHolesInRaster.py
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
__date__ = '2020-09-02'
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
                       QgsProcessingParameterField,
                       QgsProcessingParameterBoolean,
                       QgsProcessingParameterCrs,
                       QgsProcessingParameterEnum,
                       QgsFeatureRequest,
                       QgsExpression,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterFeatureSink,
                       QgsProcessingParameterFileDestination,
                       QgsProcessingParameterMultipleLayers,
                       QgsProcessingParameterRasterLayer,
                       QgsProcessingParameterRasterDestination,
                       QgsApplication,
                       QgsProject,
                       QgsRasterLayer,
                       QgsCoordinateTransform,
                       QgsCoordinateReferenceSystem)

from osgeo import osr, gdal_array, gdal #https://gdal.org/python/
import numpy as np
from matplotlib import path
from lftools.geocapt.imgs import Imgs
import os
from qgis.PyQt.QtGui import QIcon

class CreateHolesInRaster(QgsProcessingAlgorithm):

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
        return CreateHolesInRaster()

    def name(self):
        return 'createholesinraster'

    def displayName(self):
        return self.tr('Create holes in raster', 'Esburacar raster')

    def group(self):
        return self.tr('Raster')

    def groupId(self):
        return 'raster'

    def tags(self):
        return self.tr('hole,raster,cloud,remove,drone,patch').split(',')

    def icon(self):
        return QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images/raster.png'))

    txt_en = 'Creates holes in Raster by defining "no data" pixels (transparent) from the Polygon Layer.'
    txt_pt = 'Cria buracos em Raster definindo pixels nulos (transparentes) a partir de Camada de Polígonos.'
    figure = 'images/tutorial/raster_create_holes.jpg'

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

    RasterIN ='RasterIN'
    HOLES = 'HOLES'
    RasterOUT = 'RasterOUT'
    OPEN = 'OPEN'

    def initAlgorithm(self, config=None):
        # INPUT
        self.addParameter(
            QgsProcessingParameterRasterLayer(
                self.RasterIN,
                self.tr('Input Raster', 'Raster de Entrada'),
                [QgsProcessing.TypeRaster]
            )
        )

        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.HOLES,
                self.tr('Polygon layer'),
                [QgsProcessing.TypeVectorPolygon]
            )
        )

        # OUTPUT
        self.addParameter(
            QgsProcessingParameterFileDestination(
                self.RasterOUT,
                self.tr('Bumpy Raster', 'Raster Esburacado'),
                fileFilter = 'GeoTIFF (*.tif)'
            )
        )

        self.addParameter(
            QgsProcessingParameterBoolean(
                self.OPEN,
                self.tr('Load Output Raster', 'Carregar Imagem de Saída'),
                defaultValue= True
            )
        )

    def processAlgorithm(self, parameters, context, feedback):

        RasterIN = self.parameterAsRasterLayer(
            parameters,
            self.RasterIN,
            context
        )
        if RasterIN is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.RasterIN))
        RasterIN = RasterIN.dataProvider().dataSourceUri()

        layer = self.parameterAsSource(
            parameters,
            self.HOLES,
            context
        )
        if layer is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.HOLES))

        RGB_Output = self.parameterAsFileOutput(
            parameters,
            self.RasterOUT,
            context
        )

        Carregar = self.parameterAsBool(
            parameters,
            self.OPEN,
            context
        )

        # Abrir Raster layer como array
        image = gdal.Open(RasterIN)
        prj=image.GetProjection()
        CRS=osr.SpatialReference(wkt=prj)
        geotransform = image.GetGeoTransform()
        n_bands = image.RasterCount # Número de bandas
        cols = image.RasterXSize # Number of columns
        rows = image.RasterYSize # Number of rows
        # Origem e resolucao da imagem
        ulx, xres, xskew, uly, yskew, yres  = geotransform
        origem = (ulx, uly)
        resol_X = abs(xres)
        resol_Y = abs(yres)
        feedback.pushInfo(self.tr('Opening Band R...', 'Abrindo Banda R...'))
        band1 = image.GetRasterBand(1).ReadAsArray()
        feedback.pushInfo(self.tr('Opening Band G...', 'Abrindo Banda G...'))
        band2 = image.GetRasterBand(2).ReadAsArray()
        feedback.pushInfo(self.tr('Opening Band B...', 'Abrindo Banda B...'))
        band3 = image.GetRasterBand(3).ReadAsArray()
        # Transparência
        if n_bands == 4:
            feedback.pushInfo(self.tr('Opening Band Alpha...', 'Abrindo Banda Alfa...'))
            band4 = image.GetRasterBand(4).ReadAsArray()
        Pixel_Nulo = image.GetRasterBand(1).GetNoDataValue()
        if Pixel_Nulo == None:
            Pixel_Nulo = 0
        image=None # Fechar imagem

        # Remendos
        total = 100.0 /layer.featureCount() if layer.featureCount() else 0

        for cont, feat in enumerate(layer.getFeatures()):
            geom = feat.geometry()
            coords = geom.asPolygon()[0]
            caminho = []
            for ponto in coords:
                linha = (origem[1]-ponto.y())/resol_Y
                coluna = (ponto.x() - origem[0])/resol_X
                caminho += [(linha, coluna)]
            p = path.Path(caminho)
            box = geom.boundingBox()
            uly = box.yMaximum()
            lry = box.yMinimum()
            ulx = box.xMinimum()
            lrx = box.xMaximum()

            # Limites de Varredura
            row_ini = int(round((origem[1]-uly)/resol_Y - 0.5))-1
            row_fim = int(round((origem[1]-lry)/resol_Y - 0.5))+1
            col_ini = int(round((ulx - origem[0])/resol_X - 0.5))-1
            col_fim = int(round((lrx - origem[0])/resol_X - 0.5))+1

            # Varrer Raster
            if n_bands == 4:
                for lin in range(row_ini, row_fim):
                    for col in range(col_ini, col_fim):
                        pixel = (lin+0.5, col+0.5)
                        if p.contains_points([pixel]):
                            band4[lin][col] = 0
            else:
                for lin in range(row_ini, row_fim):
                    for col in range(col_ini, col_fim):
                        pixel = (lin+0.5, col+0.5)
                        if p.contains_points([pixel]):
                            band1[lin][col] = Pixel_Nulo
                            band2[lin][col] = Pixel_Nulo
                            band3[lin][col] = Pixel_Nulo
            feedback.setProgress(int(cont * total))

        # Criar imagem RGB
        feedback.pushInfo(self.tr('Saving Raster...', 'Salvando Raster...'))
        GDT = gdal_array.NumericTypeCodeToGDALTypeCode(band1.dtype)
        if n_bands == 4:
            RGB = gdal.GetDriverByName('GTiff').Create(RGB_Output, cols, rows, 4, GDT)
        else:
            RGB = gdal.GetDriverByName('GTiff').Create(RGB_Output, cols, rows, 3, GDT)
        RGB.SetGeoTransform(geotransform)    # specify coords
        RGB.SetProjection(CRS.ExportToWkt()) # export coords to file
        feedback.pushInfo(self.tr('Writing Band R...', 'Escrevendo Banda R...'))
        bandaR = RGB.GetRasterBand(1)
        bandaR.WriteArray(band1)
        feedback.pushInfo(self.tr('Writing Band G...', 'Escrevendo Banda G...'))
        bandaG = RGB.GetRasterBand(2)
        bandaG.WriteArray(band2)
        feedback.pushInfo(self.tr('Writing Band B...', 'Escrevendo Banda B...'))
        bandaB = RGB.GetRasterBand(3)
        bandaB.WriteArray(band3)
        if n_bands == 4:
            feedback.pushInfo(self.tr('Writing Alpha Band...', 'Escrevendo Banda Alfa...'))
            bandaAlpha = RGB.GetRasterBand(4)
            bandaAlpha.WriteArray(band4)
        else:
            bandaR.SetNoDataValue(Pixel_Nulo)
            bandaG.SetNoDataValue(Pixel_Nulo)
            bandaB.SetNoDataValue(Pixel_Nulo)
        RGB.FlushCache()   # Escrever no disco
        RGB = None   # Salvar e fechar

        feedback.pushInfo(self.tr('Operation completed successfully!', 'Operação finalizada com sucesso!'))
        feedback.pushInfo(self.tr('Leandro Franca - Cartographic Engineer', 'Leandro França - Eng Cart'))

        self.CAMINHO = RGB_Output
        self.CARREGAR = Carregar
        return {self.RasterOUT: RGB_Output}

    # Carregamento de arquivo de saída
    def postProcessAlgorithm(self, context, feedback):
        if self.CARREGAR:
            rlayer = QgsRasterLayer(self.CAMINHO, self.tr('Bumpy Raster', 'Raster Esburacado'))
            QgsProject.instance().addMapLayer(rlayer)
        return {}
