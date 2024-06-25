# -*- coding: utf-8 -*-

"""
Relief_DEM2txt.py
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
__date__ = '2023-01-23'
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
                       QgsProcessingParameterCrs,
                       QgsProcessingParameterEnum,
                       QgsFeatureRequest,
                       QgsExpression,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterFeatureSink,
                       QgsProcessingParameterFileDestination,
                       QgsProcessingParameterMultipleLayers,
                       QgsProcessingParameterVectorLayer,
                       QgsProcessingParameterRasterLayer,
                       QgsProcessingParameterRasterDestination,
                       QgsApplication,
                       QgsProject,
                       QgsRasterLayer,
                       QgsCoordinateTransform,
                       QgsCoordinateReferenceSystem)

from osgeo import osr, gdal_array, gdal #https://gdal.org/python/
import numpy as np
from pyproj.crs import CRS
from math import floor, ceil
from lftools.geocapt.imgs import Imgs
from lftools.translations.translate import translate
from lftools.geocapt.dip import Interpolar
import os
from qgis.PyQt.QtGui import QIcon

class DEM2txt(QgsProcessingAlgorithm):

    LOC = QgsApplication.locale()[:2]

    def tr(self, *string):
        return translate(string, self.LOC)

    def createInstance(self):
        return DEM2txt()

    def name(self):
        return 'dem2txt'

    def displayName(self):
        return self.tr('DEM to Text', 'Exportar MDE como Texto')

    def group(self):
        return self.tr('Relief', 'Relevo')

    def groupId(self):
        return 'relief'

    def tags(self):
        return self.tr('dem,dsm,dtm,txt,texto,nuvem,cloud,notepad,bloco de notas,mde,mdt,mds,terreno,relevo,contour,elevation,height,elevação').split(',')

    def icon(self):
        return QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images/contours.png'))

    txt_en = '''This tool exports a Digital Elevation Model (DEM) as a text file (txt) for later transformation into a point cloud.
Optionally, the associated Orthomosaic RGB colors can be taken to the text file.'''
    txt_pt = '''Esta ferramenta exporta um Modelo Digital de Elevação (MDE) como um arquivo de texto (txt) para posterior transformação em nuvem de pontos.
Opcionalmente, as cores RGB associadas do Ortomosaico podem ser levadas para o arquivo de texto.'''
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

    DEM ='DEM'
    ORTO = 'ORTO'
    TXT = 'TXT'
    DECIMAL = 'DECIMAL'

    def initAlgorithm(self, config=None):

        # INPUT
        self.addParameter(
            QgsProcessingParameterRasterLayer(
                self.DEM,
                self.tr('DEM', 'MDE'),
                [QgsProcessing.TypeRaster]
            )
        )

        self.addParameter(
            QgsProcessingParameterRasterLayer(
                self.ORTO,
                self.tr('Orthomosaic', 'Ortomosaico'),
                [QgsProcessing.TypeRaster],
                optional = True
            )
        )

        self.addParameter(
            QgsProcessingParameterNumber(
                self.DECIMAL,
                self.tr('Decimal places', 'Casas decimais'),
                type = QgsProcessingParameterNumber.Type.Integer,
                defaultValue = 2
                )
            )

        # OUTPUT
        self.addParameter(
            QgsProcessingParameterFileDestination(
                self.TXT,
                self.tr('X,Y,Z Points as Text', 'Pontos X,Y,Z como Texto'),
                fileFilter = 'Text (*.txt)'
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
        MDE = MDE.dataProvider().dataSourceUri()


        ORTO = self.parameterAsRasterLayer(
            parameters,
            self.ORTO,
            context
        )

        decimal = self.parameterAsInt(
            parameters,
            self.DECIMAL,
            context
        )
        if decimal is None or decimal<1:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.DECIMAL))

        format_num = '{:.Xf}'.replace('X', str(decimal))

        # output
        arquivo_saida = self.parameterAsFile(
            parameters,
            self.TXT,
            context
        )
        if 'TXT.txt' in arquivo_saida: # não permitir arquivo temporário
            raise QgsProcessingException(self.tr('Output file path must be filled!', 'Caminho do arquivo de saída deve ser preenchido!'))

        # Abrir MDE como array
        feedback.pushInfo(self.tr('Opening DEM raster file...', 'Abrindo arquivo Raster do MDE...'))
        image = gdal.Open(MDE)
        prj = image.GetProjection()
        geotransform = image.GetGeoTransform()
        num_bands = image.RasterCount
        if num_bands != 1:
            raise QgsProcessingException(self.tr('The raster layer should only have 1 band!','A camada raster deve ter apenas 1 banda!'))
        dem = image.GetRasterBand(1).ReadAsArray()
        nulo = image.GetRasterBand(1).GetNoDataValue()
        cols = image.RasterXSize
        rows = image.RasterYSize
        # Origem e resolucao da imagem
        ulx, xres, xskew, uly, yskew, yres  = geotransform
        origem = (ulx, uly)
        resol_X = abs(xres)
        resol_Y = abs(yres)
        image = None # Fechar imagem

        # Abrir ORTO
        if ORTO:
            feedback.pushInfo(self.tr('Opening Orthomosaic raster file...', 'Abrindo arquivo Raster do Ortomosaico...'))
            ORTO = ORTO.dataProvider().dataSourceUri()
            image = gdal.Open(ORTO)
            geotransform = image.GetGeoTransform()
            num_bands = image.RasterCount
            if num_bands < 3:
                raise QgsProcessingException(self.tr('The raster layer should have RBG bands!','A camada raster deve ter 3 bandas RBG!'))
            R = image.GetRasterBand(1).ReadAsArray()
            G = image.GetRasterBand(2).ReadAsArray()
            B = image.GetRasterBand(3).ReadAsArray()
            orto_nulo = image.GetRasterBand(1).GetNoDataValue()
            orto_cols = image.RasterXSize
            orto_rows = image.RasterYSize
            ulx, xres, xskew, uly, yskew, yres  = geotransform
            orto_origem = (ulx, uly)
            orto_resol_X = abs(xres)
            orto_resol_Y = abs(yres)
            image = None # Fechar imagem

        feedback.pushInfo(self.tr('Creating output file...', 'Criando arquivo de saída...'))

        Percent = 100.0/cols if cols > 0 else 0
        cont = 0
        arq_out = open(arquivo_saida, 'w')

        for col in range(cols):
            for lin in range(rows):
                Z = dem[lin,col]
                if Z != nulo:
                    X = origem[0] + resol_X*(col + 0.5)
                    Y = origem[1] - resol_Y*(lin + 0.5)

                    if ORTO:
                        red   = Interpolar(X, Y, R, orto_origem, orto_resol_X, orto_resol_Y, 'nearest', orto_nulo)
                        green = Interpolar(X, Y, G, orto_origem, orto_resol_X, orto_resol_Y, 'nearest', orto_nulo)
                        blue  = Interpolar(X, Y, B, orto_origem, orto_resol_X, orto_resol_Y, 'nearest', orto_nulo)

                        if red != orto_nulo and green != orto_nulo and blue != orto_nulo:
                            arq_out.write('{} {} {} {} {} {}\n'.format(format_num.format(X), format_num.format(Y), format_num.format(Z), int(red), int(green), int(blue)))
                    else:
                        arq_out.write('{} {} {}\n'.format(format_num.format(X), format_num.format(Y), format_num.format(Z)))

            if feedback.isCanceled():
                break
            cont += 1
            feedback.setProgress(int(cont * Percent))

        arq_out.close()

        feedback.pushInfo(self.tr('Operation completed successfully!', 'Operação finalizada com sucesso!'))
        feedback.pushInfo(self.tr('Leandro Franca - Cartographic Engineer', 'Leandro França - Eng Cart'))

        return {self.TXT: arquivo_saida}
