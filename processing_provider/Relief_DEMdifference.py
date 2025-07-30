# -*- coding: utf-8 -*-

"""
Relief_DEMdifference.py
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
__date__ = '2023-05-30'
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
from lftools.geocapt.imgs import Imgs
from lftools.translations.translate import translate
from lftools.geocapt.dip import Interpolar
import os
from qgis.PyQt.QtGui import QIcon

class DEMdifference(QgsProcessingAlgorithm):

    LOC = QgsApplication.locale()[:2]

    def tr(self, *string):
        return translate(string, self.LOC)

    def createInstance(self):
        return DEMdifference()

    def name(self):
        return 'demdifference'

    def displayName(self):
        return self.tr('DEM difference', 'Diferença de MDE')

    def group(self):
        return self.tr('Relief', 'Relevo')

    def groupId(self):
        return 'relief'

    def tags(self):
        return 'GeoOne,dem,dsm,dtm,difference,diferença,height,geoid,geoidal,ellipsoid,elipsoide,ondulação,normal,altitude,ortométrica,elevação,mdt,mds,terreno,relevo,elevation,elevação'.split(',')

    def icon(self):
        return QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images/contours.png'))

    txt_en = '''This tool performs the difference between two Digital Elevation Models (DEM).
Minuend is the raster to be subtracted.
Subtrahend is the rastar that is subtracting.'''
    txt_pt = '''Esta ferramenta executa a diferença entre dois Modelos Digitais de Elevação (MDE).
Minuendo é o raster a ser subtraído.
Subtraendo é o rastar que está subtraindo.'''
    figure = 'images/tutorial/relief_difference.jpg'

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

    MINUEND = 'MINUEND'
    SUBTRAHEND ='SUBTRAHEND'
    REF = 'REF'
    RESAMPLING = 'RESAMPLING'
    NEGATIVE = 'NEGATIVE'
    OUTPUT = 'OUTPUT'
    OPEN = 'OPEN'

    def initAlgorithm(self, config=None):
        # INPUT
        self.addParameter(
            QgsProcessingParameterRasterLayer(
                self.MINUEND,
                self.tr('Minuend', 'Minuendo'),
                [QgsProcessing.TypeRaster]
            )
        )

        self.addParameter(
            QgsProcessingParameterRasterLayer(
                self.SUBTRAHEND,
                self.tr('Subtrahend', 'Subtraendo'),
                [QgsProcessing.TypeRaster]
            )
        )

        ref = [self.tr('Minuend','Minuendo'),
               self.tr('Subtrahend','Subtraendo')
               ]

        self.addParameter(
            QgsProcessingParameterEnum(
                self.REF,
                self.tr('Reference grid', 'Grade de Referência'),
				options = ref,
                defaultValue = 0
            )
        )

        interp = [self.tr('Nearest neighbor', 'Vizinho mais próximo'),
                 self.tr('Bilinear'),
                 self.tr('Bicubic', 'Bicúbica')]

        self.addParameter(
            QgsProcessingParameterEnum(
                self.RESAMPLING,
                self.tr('Interpolation', 'Interpolação'),
				options = interp,
                defaultValue = 0
            )
        )

        self.addParameter(
            QgsProcessingParameterBoolean(
                self.NEGATIVE,
                self.tr('Multiply the result by -1', 'Multiplicar o resultado por -1'),
                defaultValue = False
            )
        )

        # OUTPUT
        self.addParameter(
            QgsProcessingParameterFileDestination(
                self.OUTPUT,
                self.tr('Difference', 'Diferença'),
                fileFilter = 'GeoTIFF (*.tif)'
            )
        )

        self.addParameter(
            QgsProcessingParameterBoolean(
                self.OPEN,
                self.tr('Load raster', 'Carregar raster'),
                defaultValue= True
            )
        )

    def processAlgorithm(self, parameters, context, feedback):

        # inputs

        minuendo = self.parameterAsRasterLayer(
            parameters,
            self.MINUEND,
            context
        )
        if minuendo is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.MINUEND))
        minuendo = minuendo.dataProvider().dataSourceUri()


        subtraendo = self.parameterAsRasterLayer(
            parameters,
            self.SUBTRAHEND,
            context
        )
        if subtraendo is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.SUBTRAHEND))
        subtraendo = subtraendo.dataProvider().dataSourceUri()

        interpolacao = self.parameterAsEnum(
            parameters,
            self.RESAMPLING,
            context
        )
        interpolacao = ['nearest','bilinear','bicubic'][interpolacao]

        negativo = self.parameterAsBool(
            parameters,
            self.NEGATIVE,
            context
        )

        grade_ref = self.parameterAsEnum(
            parameters,
            self.REF,
            context
        )

        # output
        Output = self.parameterAsFileOutput(
            parameters,
            self.OUTPUT,
            context
        )

        Carregar = self.parameterAsBool(
            parameters,
            self.OPEN,
            context
        )

        # Minuendo
        feedback.pushInfo(self.tr('Opening minuend raster file...', 'Abrindo arquivo raster Minuendo...'))
        image = gdal.Open(minuendo)
        prj = image.GetProjection()
        banda = image.GetRasterBand(1).ReadAsArray()
        nulo = image.GetRasterBand(1).GetNoDataValue()
        if nulo == None:
            nulo =-9999
        # Number of rows and columns
        cols = image.RasterXSize
        rows = image.RasterYSize
        # Origem e resolucao da imagem
        geotransform = image.GetGeoTransform()
        ulx, xres, xskew, uly, yskew, yres  = geotransform
        origem = (ulx, uly)
        resol_X = abs(xres)
        resol_Y = abs(yres)
        lrx = ulx + (cols * xres)
        lry = uly + (rows * yres)
        bbox = [ulx, lrx, lry, uly]
        image = None # Fechar imagem

        # Subtraendo
        feedback.pushInfo(self.tr('Opening subtrahend raster file...', 'Abrindo arquivo raster Subtraendo...'))
        image = gdal.Open(subtraendo)
        prjRef = image.GetProjection()
        bandRef = image.GetRasterBand(1).ReadAsArray()
        nuloRef = image.GetRasterBand(1).GetNoDataValue()
        if nuloRef == None:
            nuloRef =-9999
        # Number of rows and columns
        colsRef = image.RasterXSize
        rowsRef = image.RasterYSize
        # Origem e resolucao da imagem
        geotransformRef = image.GetGeoTransform()
        ulx, xres, xskew, uly, yskew, yres  = geotransformRef
        origemRef = (ulx, uly)
        resol_XRef = abs(xres)
        resol_YRef = abs(yres)
        image = None # Fechar imagem

        # Transformação de coordenadas
        crsSrc = QgsCoordinateReferenceSystem(prj)
        crsDest = QgsCoordinateReferenceSystem(prjRef)
        if crsSrc != crsDest:
            transf_SRC = True
            coordTransf = QgsCoordinateTransform(crsSrc, crsDest, QgsProject.instance())
            InvCoordTransf = QgsCoordinateTransform(crsDest, crsSrc, QgsProject.instance())
        else:
            transf_SRC = False

        # Diferença
        feedback.pushInfo(self.tr('Calculating the difference...', 'Calculando a diferença...'))
        if grade_ref == 0: # Referencia é o minuendo
            DIFER = -9999.*np.ones([rows,cols])
            Percent = 100./rows
            for current, lin in enumerate(range(rows)):
                for col in range(cols):
                    X = origem[0] + resol_X*(col + 0.5)
                    Y = origem[1] - resol_Y*(lin + 0.5)
                    Z = banda[lin, col]
                    if transf_SRC:
                        geom = QgsGeometry.fromPointXY(QgsPointXY(X,Y))
                        geom.transform(coordTransf)
                        pnt = geom.asPoint()
                        X, Y = pnt.x(), pnt.y()
                    Z_ref = Interpolar(X, Y, bandRef, origemRef, resol_XRef, resol_YRef, metodo = 'nearest', nulo = nuloRef)
                    if Z != -9999 and Z_ref != -9999:
                        DIFER[lin,col] = (Z - Z_ref)*(-1 if negativo else 1)
                if feedback.isCanceled():
                    break
                feedback.setProgress(int((current+1) * Percent))

            # Verificar novos valores de número de linhas e colunas
            # Verificar nova extensão

            new_img = gdal.GetDriverByName('GTiff').Create(Output, cols, rows, 1, gdal.GDT_Float32)
            new_img.SetGeoTransform(geotransform)
            new_img.SetProjection(prj)
            new_band = new_img.GetRasterBand(1)
            new_band.SetNoDataValue(nulo)
            new_band.WriteArray(DIFER)
            new_img.FlushCache()
            new_img = None

        elif grade_ref == 1: # Referência é o subtraendo
            DIFER = -9999.*np.ones([rowsRef,colsRef])
            Percent = 100./rowsRef
            for current, lin in enumerate(range(rowsRef)):
                for col in range(colsRef):
                    X = origemRef[0] + resol_XRef*(col + 0.5)
                    Y = origemRef[1] - resol_YRef*(lin + 0.5)
                    Z = bandRef[lin, col]
                    if transf_SRC:
                        geom = QgsGeometry.fromPointXY(QgsPointXY(X,Y))
                        geom.transform(InvCoordTransf)
                        pnt = geom.asPoint()
                        X, Y = pnt.x(), pnt.y()
                    Z_ref = Interpolar(X, Y, banda, origem, resol_X, resol_Y, metodo = 'nearest', nulo = nulo)
                    if Z != -9999 and Z_ref != -9999:
                        DIFER[lin,col] = (Z_ref - Z) * (-1 if negativo else 1)
                if feedback.isCanceled():
                    break
                feedback.setProgress(int((current+1) * Percent))

            # Verificar novos valores de número de linhas e colunas
            # Verificar nova extensão

            new_img = gdal.GetDriverByName('GTiff').Create(Output, colsRef, rowsRef, 1, gdal.GDT_Float32)
            new_img.SetGeoTransform(geotransformRef)
            new_img.SetProjection(prjRef)
            new_band = new_img.GetRasterBand(1)
            new_band.SetNoDataValue(nuloRef)
            new_band.WriteArray(DIFER)
            new_img.FlushCache()
            new_img = None

        feedback.pushInfo(self.tr('Operation completed successfully!', 'Operação finalizada com sucesso!'))
        feedback.pushInfo(self.tr('Leandro Franca - Cartographic Engineer', 'Leandro França - Eng Cart'))
        self.CAMINHO = Output
        self.CARREGAR = Carregar
        return {self.OUTPUT: Output}

    # Carregamento de arquivo de saída
    def postProcessAlgorithm(self, context, feedback):
        if self.CARREGAR:
            rlayer = QgsRasterLayer(self.CAMINHO, self.tr('Difference', 'Diferença'))
            QgsProject.instance().addMapLayer(rlayer)
        return {}
