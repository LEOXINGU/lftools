# -*- coding: utf-8 -*-

"""
Rast_getPointValue.py
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
                       QgsProcessingParameterBand,
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
from lftools.translations.translate import translate
from lftools.geocapt.dip import Interpolar
import os
import numpy as np
from qgis.PyQt.QtGui import QIcon

class GetPointValue(QgsProcessingAlgorithm):

    LOC = QgsApplication.locale()[:2]

    def tr(self, *string):
        return translate(string, self.LOC)
        
    def createInstance(self):
        return GetPointValue()

    def name(self):
        return 'getpointvalue'

    def displayName(self):
        return self.tr('Estimate point value from Raster', 'Estimar valor de ponto a partir de Raster')

    def group(self):
        return self.tr('Raster')

    def groupId(self):
        return 'raster'

    def tags(self):
        return self.tr('sampling,sample,amostra,pegar,get,interpolate,interpolar,bilinear,cell').split(',')

    def icon(self):
        return QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images/raster.png'))

    txt_en = 'This tool estimates the value of the points from Raster, making the proper interpolation of the nearest pixels (cells).'
    txt_pt = 'Esta ferramenta estima o valor dos pontos a partir de Raster, fazendo a devida interpolação dos pixels (células) mais próximos.'
    figure = 'images/tutorial/raster_getpointvalue.jpg'

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
    POINTS = 'POINTS'
    RESAMPLING = 'RESAMPLING'
    PREFIX = 'PREFIX'
    OUTPUT = 'OUTPUT'

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
            QgsProcessingParameterBand(
                self.BAND,
                self.tr('Band number', 'Número da banda'),
                parentLayerParameterName=self.INPUT,
                optional = True
            )
        )

        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.POINTS,
                self.tr('Vector Layer de Pontos', 'Camada Vetorial de Pontos'),
                [QgsProcessing.TypeVectorPoint]
            )
        )

        opcoes = [self.tr('Nearest','Vizinho mais próximo'),
				  self.tr('Bilinear'),
				  self.tr('Bicubic','Bicúbica')
               ]

        self.addParameter(
            QgsProcessingParameterEnum(
                self.RESAMPLING,
                self.tr('Interpolation method', 'Método de Interpolação'),
				options = opcoes,
                defaultValue= 1
            )
        )

        self.addParameter(
            QgsProcessingParameterString(
                self.PREFIX,
                self.tr('Output column prefix', 'Prefixo da coluna de saída'),
                defaultValue = self.tr('sample_', 'amostra_')
            )
        )

        # output
        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT,
                self.tr('Points with interpolated value from raster', 'Pontos com valor interpolado do Raster')
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

        n_banda = self.parameterAsInt(
            parameters,
            self.BAND,
            context
        )

        pontos = self.parameterAsSource(
            parameters,
            self.POINTS,
            context
        )
        if pontos is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.POINTS))

        reamostragem = self.parameterAsEnum(
            parameters,
            self.RESAMPLING,
            context
        )
        reamostragem = ['nearest','bilinear','bicubic'][reamostragem]

        prefixo = self.parameterAsString(
            parameters,
            self.PREFIX,
            context
        )

        # Abrir Raster
        feedback.pushInfo(self.tr('Opening raster file...', 'Abrindo arquivo Raster...'))
        image = gdal.Open(RasterIN.dataProvider().dataSourceUri())
        prj=image.GetProjection()
        SRC = QgsCoordinateReferenceSystem(prj)
        ulx, xres, xskew, uly, yskew, yres  = image.GetGeoTransform()
        cols = image.RasterXSize
        rows = image.RasterYSize
        total_bands = image.RasterCount
        GDT = image.GetRasterBand(1).DataType
        valor_nulo = image.GetRasterBand(1).GetNoDataValue()
        if not valor_nulo:
            valor_nulo = 0
        origem = (ulx, uly)
        xres = abs(xres)
        yres = abs(yres)

        # Transformação de coordenadas
        crsSrc = pontos.sourceCrs()
        crsDest = QgsCoordinateReferenceSystem(prj)
        if crsSrc != crsDest:
            transf_SRC = True
            coordTransf = QgsCoordinateTransform(crsSrc, crsDest, QgsProject.instance())
            InvCoordTransf = QgsCoordinateTransform(crsDest, crsSrc, QgsProject.instance())
        else:
            transf_SRC = False

        # Camada de saída
        Fields = pontos.fields()
        CRS = pontos.sourceCrs()
        if n_banda == 0:
            for k in range(total_bands):
                Fields.append(QgsField(prefixo + self.tr('band{}'.format(k+1), 'banda{}'.format(k+1)), QVariant.Double))

        else:
            Fields.append(QgsField(prefixo + self.tr('band{}'.format(n_banda), 'banda{}'.format(n_banda)), QVariant.Double))

        (sink, dest_id) = self.parameterAsSink(
            parameters,
            self.OUTPUT,
            context,
            Fields,
            QgsWkbTypes.Point,
            CRS
        )
        if sink is None:
            raise QgsProcessingException(self.invalidSinkError(parameters, self.OUTPUT))

        # Calcular valor interpolado para cada ponto
        if n_banda == 0: # Calculo para todas as bandas
            Percent = 100.0/total_bands if total_bands>0 else 0
            feicoes = {}
            for index, k in enumerate(range(total_bands)):
                banda = image.GetRasterBand(k+1).ReadAsArray()
                feedback.pushInfo(self.tr('Getting values from band {}...', 'Pegando valores da banda {}...').format(k+1))
                for feat in pontos.getFeatures():
                    geom = feat.geometry()
                    if transf_SRC:
                        geom.transform(coordTransf)
                    if geom.isMultipart():
                        pnt = geom.asMultiPoint()[0]
                    else:
                        pnt = geom.asPoint()
                    X, Y = pnt.x(), pnt.y()
                    valor = Interpolar(X, Y,
                                        banda,
                                        origem,
                                        xres,
                                        yres,
                                        reamostragem,
                                        valor_nulo)
                    coord = (X, Y)
                    if coord in feicoes:
                        feicoes[coord] += [valor]
                    else:
                        att = feat.attributes()
                        feicoes[coord] = att + [valor]

                if feedback.isCanceled():
                    break
                feedback.setProgress(int((index+1) * Percent))

            feedback.pushInfo(self.tr('Saving results...', 'Salvando resultados...'))
            for coord in feicoes:
                newGeom = QgsGeometry.fromPointXY(QgsPointXY(coord[0], coord[1]))
                newfeat = QgsFeature(Fields)
                if transf_SRC:
                    newGeom.transform(InvCoordTransf)
                newfeat.setGeometry(newGeom)
                newfeat.setAttributes(feicoes[coord])
                sink.addFeature(newfeat, QgsFeatureSink.FastInsert)

        else: # Calculo para uma banda específica
            Percent = 100.0/pontos.featureCount() if pontos.featureCount()>0 else 0
            banda = image.GetRasterBand(n_banda).ReadAsArray()
            feedback.pushInfo(self.tr('Getting values from band {}...', 'Pegando valores da banda {}...').format(n_banda))
            newfeat = QgsFeature(Fields)
            for index, feat in enumerate(pontos.getFeatures()):
                geom = feat.geometry()
                if transf_SRC:
                    geom.transform(coordTransf)
                att = feat.attributes()
                if geom.isMultipart():
                    pnts = geom.asMultiPoint()
                    for pnt in pnts:
                        X, Y = pnt.x(), pnt.y()
                        valor = Interpolar(X, Y,
                                            banda,
                                            origem,
                                            xres,
                                            yres,
                                            reamostragem,
                                            valor_nulo)
                        newGeom = QgsGeometry.fromPointXY(QgsPointXY(X, Y))
                        if transf_SRC:
                            newGeom.transform(InvCoordTransf)
                        newfeat.setGeometry(newGeom)
                        newfeat.setAttributes(att + [valor])
                        sink.addFeature(newfeat, QgsFeatureSink.FastInsert)
                else:
                    pnt = geom.asPoint()
                    X, Y = pnt.x(), pnt.y()
                    valor = Interpolar(X, Y,
                                        banda,
                                        origem,
                                        xres,
                                        yres,
                                        reamostragem,
                                        valor_nulo)
                    newGeom = QgsGeometry.fromPointXY(QgsPointXY(X, Y))
                    if transf_SRC:
                        newGeom.transform(InvCoordTransf)
                    newfeat.setGeometry(newGeom)
                    newfeat.setAttributes(att + [valor])
                    sink.addFeature(newfeat, QgsFeatureSink.FastInsert)

                if feedback.isCanceled():
                    break
                feedback.setProgress(int((index+1) * Percent))

        feedback.pushInfo(self.tr('Operation completed successfully!', 'Operação finalizada com sucesso!'))
        feedback.pushInfo(self.tr('Leandro Franca - Cartographic Engineer', 'Leandro França - Eng Cart'))

        return {'output': self.OUTPUT}
