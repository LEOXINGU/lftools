# -*- coding: utf-8 -*-

"""
Rast_SplitRaster.py
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
__date__ = '2023-06-18'
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
                       QgsProject,
                       QgsProcessingException,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterString,
                       QgsProcessingParameterBand,
                       QgsProcessingParameterBoolean,
                       QgsProcessingParameterCrs,
                       QgsProcessingParameterEnum,
                       QgsFeatureRequest,
                       QgsExpression,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterFeatureSink,
                       QgsProcessingParameterFileDestination,
                       QgsProcessingParameterFile,
                       QgsProcessingParameterNumber,
                       QgsProcessingParameterMultipleLayers,
                       QgsProcessingParameterRasterLayer,
                       QgsProcessingParameterRasterDestination,
                       QgsApplication,
                       QgsProject,
                       QgsRasterLayer,
                       QgsCoordinateTransform,
                       QgsCoordinateReferenceSystem)

from math import floor, ceil
from osgeo import osr, gdal_array, gdal #https://gdal.org/python/
from matplotlib import path
import numpy as np
from lftools.geocapt.imgs import Imgs
from lftools.translations.translate import translate
import os
from qgis.PyQt.QtGui import QIcon

class SplitRaster(QgsProcessingAlgorithm):

    LOC = QgsApplication.locale()[:2]

    def tr(self, *string):
        return translate(string, self.LOC)

    def createInstance(self):
        return SplitRaster()

    def name(self):
        return 'splitraster'

    def displayName(self):
        return self.tr('Split raster', 'Dividir raster')

    def group(self):
        return self.tr('Raster')

    def groupId(self):
        return 'raster'

    def tags(self):
        return self.tr('splitting,dividir,separar,quebrar,break').split(',')

    def icon(self):
        return QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images/raster.png'))

    txt_en = '''Splits a raster dataset into smaller pieces, by horizontal and vertical tiles.'''
    txt_pt = '''Divide um raster em pedaços menores, por blocos horizontais e verticais'''
    figure = 'images/tutorial/raster_split.jpg'

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

    INPUT ='INPUT'
    VERTICAL = 'VERTICAL'
    HORIZONTAL = 'HORIZONTAL'
    OUTPUT_FOLDER = 'OUTPUT_FOLDER'
    OPEN = 'OPEN'

    def initAlgorithm(self, config=None):
        # INPUT
        self.addParameter(
            QgsProcessingParameterRasterLayer(
                self.INPUT,
                self.tr('Input Raster', 'Raster de entrada'),
                [QgsProcessing.TypeRaster]
            )
        )

        self.addParameter(
            QgsProcessingParameterNumber(
                self.HORIZONTAL,
                self.tr("X axis split", 'Eixo X'),
                type = QgsProcessingParameterNumber.Type.Integer,
                minValue = 1,
                defaultValue = 2
                )
            )

        self.addParameter(
            QgsProcessingParameterNumber(
                self.VERTICAL,
                self.tr("Y axis split", 'Eixo Y'),
                type = QgsProcessingParameterNumber.Type.Integer,
                minValue = 1,
                defaultValue = 2
                )
            )

        # OUTPUT
        self.addParameter(
            QgsProcessingParameterFile(
                self.OUTPUT_FOLDER,
                self.tr('Folder for split rasters', 'Pasta para rasters divididos'),
                behavior = QgsProcessingParameterFile.Folder,
                defaultValue = None
            )
        )

        self.addParameter(
            QgsProcessingParameterBoolean(
                self.OPEN,
                self.tr('Load output raster', 'Carregar imagens de saída'),
                defaultValue = True
            )
        )

    def processAlgorithm(self, parameters, context, feedback):

        RasterIN = self.parameterAsRasterLayer(
            parameters,
            self.INPUT,
            context
        )
        if RasterIN is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.INPUT))
        nome = RasterIN.name()
        RasterIN = RasterIN.dataProvider().dataSourceUri()

        pasta_out = self.parameterAsFile(
            parameters,
            self.OUTPUT_FOLDER,
            context
        )
        if not pasta_out:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.OUTPUT_FOLDER))

        n_clip_lin = self.parameterAsInt(
            parameters,
            self.VERTICAL,
            context
        )

        n_clip_col = self.parameterAsInt(
            parameters,
            self.HORIZONTAL,
            context
        )

        Carregar = self.parameterAsBool(
            parameters,
            self.OPEN,
            context
        )

        # Abrir Raster layer como array
        feedback.pushInfo(self.tr('Opening raster...', 'Abrindo raster...'))
        image = gdal.Open(RasterIN)
        prj = image.GetProjection()
        banda = image.GetRasterBand(1).ReadAsArray()
        Pixel_Nulo = image.GetRasterBand(1).GetNoDataValue()
        n_bands = image.RasterCount
        # Origem e resolucao da imagem
        geotransform  = image.GetGeoTransform()
        ulx, xres, xskew, uly, yskew, yres  = geotransform
        origem = [ulx, uly]
        # Pegar tipo de dado do array
        GDT = gdal_array.NumericTypeCodeToGDALTypeCode(banda.dtype)


        # Retalhar imagem
        n_lin = image.RasterYSize # numero de linhas
        n_col = image.RasterXSize # numero de colunas
        linhas = np.round(np.linspace(0, n_lin, n_clip_lin+1))
        colunas = np.round(np.linspace(0, n_col, n_clip_col+1))
        lista = []
        for i in range(n_clip_lin):
            for j in range(n_clip_col):
                new_name = nome + '_' + '{:02}'.format(j+1) +'_' + '{:02}'.format(i+1) + '.tif'
                feedback.pushInfo(self.tr('Exporting file {} ...', 'Exportando arquivo {} ...').format(new_name))
                Output = os.path.join(pasta_out, new_name)
                cols = colunas[j+1] - colunas[j]
                rows = linhas[i+1] - linhas[i]
                ulx = origem[0] + abs(xres)*colunas[j]
                uly = origem[1] - abs(yres)*linhas[i]
                geotransform = [ulx, xres, 0, uly, 0, yres]
                # Arquivo de saída
                Driver = gdal.GetDriverByName('GTiff').Create(Output, int(cols), int(rows), n_bands, GDT)
                Driver.SetGeoTransform(geotransform)
                Driver.SetProjection(prj)

                for k in range(n_bands):
                    banda = image.GetRasterBand(k+1).ReadAsArray()
                    split_banda = banda[int(linhas[i]):int(linhas[i+1]), int(colunas[j]):int(colunas[j+1])]
                    outband = Driver.GetRasterBand(k+1)
                    feedback.pushInfo(self.tr('Writing Band {}...'.format(k+1), 'Escrevendo Banda {}...'.format(k+1)))
                    outband.WriteArray(split_banda)
                    if Pixel_Nulo or Pixel_Nulo == 0:
                        outband.SetNoDataValue(Pixel_Nulo)
                    del banda, split_banda
                lista += [Output]
                Driver.FlushCache() # write to disk
                Driver = None  # save, close
        image = None # Close dataset

        feedback.pushInfo(self.tr('Operation completed successfully!', 'Operação finalizada com sucesso!'))
        feedback.pushInfo(self.tr('Leandro Franca - Cartographic Engineer', 'Leandro França - Eng Cart'))
        self.CAMINHO = lista
        self.CARREGAR = Carregar
        return {self.OUTPUT_FOLDER: pasta_out}

    def postProcessAlgorithm(self, context, feedback):
        if self.CARREGAR:
            for file_path in self.CAMINHO:
                layer_name = os.path.basename(file_path)[:-4]
                rlayer = QgsRasterLayer(file_path, layer_name)
                QgsProject.instance().addMapLayer(rlayer)
        return {}
