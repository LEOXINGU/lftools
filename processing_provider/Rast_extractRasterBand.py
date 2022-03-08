# -*- coding: utf-8 -*-

"""
Rast_extractRasterBand.py
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
__date__ = '2020-12-15'
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
                       QgsProcessingParameterRasterLayer,
                       QgsProcessingParameterBand,
                       QgsProcessingParameterRasterDestination,
                       QgsApplication,
                       QgsProject,
                       QgsRasterLayer,
                       QgsCoordinateTransform,
                       QgsCoordinateReferenceSystem)

from osgeo import osr, gdal_array, gdal #https://gdal.org/python/
from lftools.geocapt.imgs import Imgs
import os
from qgis.PyQt.QtGui import QIcon

class ExtractRasterBand(QgsProcessingAlgorithm):

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
        return ExtractRasterBand()

    def name(self):
        return 'extractrasterband'

    def displayName(self):
        return self.tr('Extract raster band', 'Extrair banda de raster')

    def group(self):
        return self.tr('Raster')

    def groupId(self):
        return 'raster'

    def tags(self):
        return self.tr('bands,raster,extract,color,spectral,frequency,RGB,composite,channel').split(',')

    def icon(self):
        return QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images/raster.png'))

    txt_en = 'Extracts a difined band of a raster (for multiband rasters).'
    txt_pt = 'Extrai uma das bandas de um arquivo raster (para imagens multi-bandas/multi-canal).'
    figure = 'images/tutorial/raster_extract_band.jpg'

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
    BAND = 'BAND'
    OUTPUT = 'OUTPUT'
    OPEN = 'OPEN'

    def initAlgorithm(self, config=None):
        # INPUT
        self.addParameter(
            QgsProcessingParameterRasterLayer(
                self.INPUT,
                self.tr('Multiband Input Raster', 'Raster multibandas'),
                [QgsProcessing.TypeRaster]
            )
        )

        self.addParameter(
            QgsProcessingParameterBand(
                self.BAND,
                self.tr('Band number', 'Número da banda'),
                parentLayerParameterName=self.INPUT,
            )
        )

        # OUTPUT
        self.addParameter(
            QgsProcessingParameterFileDestination(
                self.OUTPUT,
                self.tr('Selected band', 'Banda selecionada'),
                fileFilter = 'GeoTIFF (*.tif)'
            )
        )

        self.addParameter(
            QgsProcessingParameterBoolean(
                self.OPEN,
                self.tr('Load output raster', 'Carregar raster de saída'),
                defaultValue= True
            )
        )

    def processAlgorithm(self, parameters, context, feedback):

        entrada = self.parameterAsRasterLayer(
            parameters,
            self.INPUT,
            context
        )
        if entrada is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.INPUT))

        n_banda = self.parameterAsInt(
            parameters,
            self.BAND,
            context
        )
        if n_banda is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.BAND))

        saida = self.parameterAsFileOutput(
            parameters,
            self.OUTPUT,
            context
        )

        Carregar = self.parameterAsBool(
            parameters,
            self.OPEN,
            context
        )

        # Abrir banda
        feedback.pushInfo(self.tr('Reading the selected band...', 'Lendo a banda selecionada...'))
        image = gdal.Open(entrada.dataProvider().dataSourceUri())
        banda = image.GetRasterBand(n_banda).ReadAsArray()
        prj=image.GetProjection()
        geotransform = image.GetGeoTransform()

        # Criar objeto CRS
        CRS=osr.SpatialReference(wkt=prj)

        # Obter número de linhas e colunas
        cols = image.RasterXSize
        rows = image.RasterYSize
        image=None # fechar magem

        # Pegar tipo de dado do array
        GDT = gdal_array.NumericTypeCodeToGDALTypeCode(banda.dtype)

        # Criar imagem com uma única banda
        feedback.pushInfo(self.tr('Writing the selected band...', 'Escrevendo a banda selecionada...'))
        nova_imagem = gdal.GetDriverByName('GTiff').Create(saida, cols, rows, 1, GDT)
        nova_imagem.SetGeoTransform(geotransform)
        nova_imagem.SetProjection(CRS.ExportToWkt())
        nova_imagem.GetRasterBand(1).WriteArray(banda)
        nova_imagem.FlushCache() # Escrever no disco
        nova_imagem = None # Salvar e fechar
        CRS = None

        feedback.pushInfo(self.tr('Operation completed successfully!', 'Operação finalizada com sucesso!'))
        feedback.pushInfo(self.tr('Leandro Franca - Cartographic Engineer', 'Leandro França - Eng Cart'))
        self.CAMINHO = saida
        self.CARREGAR = Carregar
        return {self.OUTPUT: saida}

    def postProcessAlgorithm(self, context, feedback):
        if self.CARREGAR:
            rlayer = QgsRasterLayer(self.CAMINHO, self.tr('Extracted band', 'Banda extraída'))
            QgsProject.instance().addMapLayer(rlayer)
        return {}
