# -*- coding: utf-8 -*-

"""
Drone_GeorrefAdjust.py
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
__date__ = '2021-11-04'
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
from lftools.geocapt.adjust import Ajust2D, ValidacaoVetores, transformGeom2D
import os
from qgis.PyQt.QtGui import QIcon

class GeorrefAdjust(QgsProcessingAlgorithm):

    LOC = QgsApplication.locale()[:2]

    def tr(self, *string):
        return translate(string, self.LOC)

    def createInstance(self):
        return GeorrefAdjust()

    def name(self):
        return 'georrefadjust'

    def displayName(self):
        return self.tr('Georeferencing Adjustment', 'Ajuste do Georreferenciamento')

    def group(self):
        return self.tr('Drones')

    def groupId(self):
        return 'drones'

    def tags(self):
        return self.tr('drone,mosaic,adjustment,raster,combine,mosaik,mosaico,georreferencing,georreferenciamento,ajuste,registry,registro,GCP,planimetrico,ground control points,pontos de controle').split(',')

    def icon(self):
        return QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images/drone.png'))

    txt_en = '''This tool performs the georeferencing adjustment of any raster image using Ground Control Points.
     The following types of coordinate transformation can be used:
◼️ <b>Translation Transformation</b>: 1 vector without adjustment / 2 or + vectors with adjustment.
◼️ <b>Conformal Transformation (2D Helmert)</b>: 2 vectors without adjustment / 3 or + vectors with adjustment.
◼️ <b>Affine Transformation</b>: 3 vectors without adjustment / 4 or + vectors with adjustment.'''
    txt_pt = '''Esta ferramenta realiza o ajuste do georreferenciamento de qualquer imagem raster utilizando Pontos de Controle no Terreno.
    Os seguintes tipos de transformação de coordenadas podem ser utilizados:
◼️	<b>Transformação de Translação</b>: 1 vetor sem ajustamento / 2 ou + vetores com ajustamento.
◼️	<b>Transformação Conforme (Helmert 2D)</b>: 2 vetores sem ajustamento / 3 ou + vetores com ajustamento.
◼️	<b>Transformação Afim</b>: 3 vetores sem ajustamento / 4 ou + vetores com ajustamento.'''
    figure = 'images/tutorial/drone_georref_adjust.jpg'

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

    RASTER ='RASTER'
    VECTORS = 'VECTORS'
    METHOD = 'METHOD'
    RESAMPLING = 'RESAMPLING'
    ADJUSTED = 'ADJUSTED'
    OPEN = 'OPEN'
    COORDS = 'COORDS'
    HTML = 'HTML'
    CHECKCRS = 'CHECKCRS'

    def initAlgorithm(self, config=None):
        # INPUT
        self.addParameter(
            QgsProcessingParameterRasterLayer(
                self.RASTER,
                self.tr('Input Raster', 'Raster de Entrada'),
                [QgsProcessing.TypeRaster]
            )
        )

        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.VECTORS,
                self.tr('Vectors Lines (two vertices)', 'Linhas de vetores (dois vértices)'),
                [QgsProcessing.TypeVectorLine]
            )
        )

        tipos = [self.tr('Translation','Translação'),
                  self.tr('Helmert 2D (Conformal)','Helmert 2D (Conforme)'),
                  self.tr('Afinne','Afim (Polinomial grau 1)')
               ]

        self.addParameter(
            QgsProcessingParameterBoolean(
                self.CHECKCRS,
                self.tr('Check CRS', 'Verificar SRC'),
                defaultValue= True
            )
        )

        self.addParameter(
            QgsProcessingParameterEnum(
                self.METHOD,
                self.tr('Method', 'Método'),
				options = tipos,
                defaultValue= 2
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
                defaultValue= 0
            )
        )

        # OUTPUT
        self.addParameter(
            QgsProcessingParameterFileDestination(
                self.ADJUSTED,
                self.tr('Adjusted Raster', 'Raster Ajustado'),
                fileFilter = 'GeoTIFF (*.tif)'
            )
        )

        self.addParameter(
            QgsProcessingParameterBoolean(
                self.OPEN,
                self.tr('Load Adjusted Raster', 'Carregar Raster Ajustado'),
                defaultValue= True
            )
        )

        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.COORDS,
                self.tr('Adjusted Coordinates with precisions', 'Coordenadas Ajustadas com precisões')
            )
        )

        self.addParameter(
            QgsProcessingParameterFileDestination(
                self.HTML,
                self.tr('Adjustment Report', 'Relatório de Ajustamento'),
                self.tr('HTML files (*.html)')
            )
        )

    def processAlgorithm(self, parameters, context, feedback):

        # inputs
        RasterIN = self.parameterAsRasterLayer(
            parameters,
            self.RASTER,
            context
        )
        if RasterIN is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.RASTER))
        RasterIN = RasterIN.dataProvider().dataSourceUri()

        reamostragem = self.parameterAsEnum(
            parameters,
            self.RESAMPLING,
            context
        )
        reamostragem = ['nearest','bilinear','bicubic'][reamostragem]

        deslc = self.parameterAsSource(
            parameters,
            self.VECTORS,
            context
        )
        if deslc is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.VECTORS))

        metodo = self.parameterAsEnum(
            parameters,
            self.METHOD,
            context
        )

        feedback.pushInfo(self.tr('Calculating adjustment parameters...', 'Calculando parâmetros de ajustamento...'))
        validacao = ValidacaoVetores(deslc, metodo)
        COORD, PREC, CoordTransf, texto, CoordInvTransf = Ajust2D(deslc, metodo)


        # output

        Output = self.parameterAsFileOutput(
            parameters,
            self.ADJUSTED,
            context
        )

        Carregar = self.parameterAsBool(
            parameters,
            self.OPEN,
            context
        )

        checkCRS = self.parameterAsBool(
            parameters,
            self.CHECKCRS,
            context
        )

        # Coordenas ajustadas de saida
        GeomType = QgsWkbTypes.Point
        Fields = QgsFields()
        CRS = deslc.sourceCrs()
        prj = CRS.toWkt()

        itens  = {
                     'ord' : QVariant.Int,
                     self.tr('precision_x', 'precisao_x') : QVariant.Double,
                     self.tr('precision_y','precisao_y') : QVariant.Double
                     }
        for item in itens:
            Fields.append(QgsField(item, itens[item]))

        (sink, dest_id) = self.parameterAsSink(
            parameters,
            self.COORDS,
            context,
            Fields,
            GeomType,
            CRS
        )
        if sink is None:
            raise QgsProcessingException(self.invalidSinkError(parameters, self.COORDS))

        html_output = self.parameterAsFileOutput(
            parameters,
            self.HTML,
            context
        )


        # Abrir arquivo Raster
        feedback.pushInfo(self.tr('Opening raster file...', 'Abrindo arquivo Raster...'))

        image = gdal.Open(RasterIN)
        #prj = image.GetProjection() # wkt
        SRC = QgsCoordinateReferenceSystem(image.GetProjection())
        ulx, xres, xskew, uly, yskew, yres  = image.GetGeoTransform()
        cols = image.RasterXSize
        rows = image.RasterYSize
        n_bands = image.RasterCount
        GDT = image.GetRasterBand(1).DataType
        valor_nulo = image.GetRasterBand(1).GetNoDataValue()
        if not valor_nulo:
            valor_nulo = 0
        origem_antiga = (ulx, uly)
        xres_antiga = abs(xres)
        yres_antiga = abs(yres)

        # Creating BBox
        coord = [[QgsPointXY(ulx, uly),
                  QgsPointXY(ulx+cols*xres, uly),
                  QgsPointXY(ulx+cols*xres, uly+rows*yres),
                  QgsPointXY(ulx, uly+rows*yres),
                  QgsPointXY(ulx, uly)]]
        geom = QgsGeometry.fromPolygonXY(coord)

        ## Validar dados de entrada
        # Verificar se o Raster e os Vetores tem o mesmo SRC
        if checkCRS:
            if not SRC.description() == CRS.description():
                raise QgsProcessingException(self.tr('The raster layer and the homologous point vector layer must have the same CRS!', 'A camada raster e a camada vetorial de pontos homólogos devem ter o mesmo SRC!'))


        # Calcular nova extensão e origem
        trans_geom = transformGeom2D(geom, CoordTransf)
        bbox = trans_geom.boundingBox()
        y_min = bbox.yMinimum()
        y_max = bbox.yMaximum()
        x_min = bbox.xMinimum()
        x_max = bbox.xMaximum()

        # Definir n_col, n_lin e resolucao da nova imagem
        n_lin = round((y_max-y_min)/abs(yres))
        n_col = round((x_max-x_min)/abs(xres))
        # Novas resoluções
        xres = (x_max-x_min)/n_col
        yres = -(y_max-y_min)/n_lin

        feedback.pushInfo(self.tr('Size: ', 'Tamanho: ') + str(n_lin) +'x' + str(n_col))
        # Geotransform do novo Raster
        ulx = x_min
        uly = y_max
        xskew, yskew = 0, 0
        geotransform = [ulx, xres, xskew, uly, yskew, yres]
        origem = (ulx, uly)
        resol_X = abs(xres)
        resol_Y = abs(yres)

        # Criar Raster
        Driver = gdal.GetDriverByName('GTiff').Create(Output, n_col, n_lin, n_bands, GDT)
        Driver.SetGeoTransform(geotransform)
        Driver.SetProjection(prj)

        # Iniciar reamostragem
        Percent = 100.0/(n_lin*n_bands)
        current = 0

        for k in range(n_bands):
            # Abrir banda 1 como array
            feedback.pushInfo((self.tr('Opening band {} as array...', 'Abrindo banda {} como array...')).format(str(k+1)))
            banda_antiga = image.GetRasterBand(k+1).ReadAsArray()
            # Criando novo array
            feedback.pushInfo((self.tr('Transforming new band {}...', 'Transformando nova banda {}...')).format(str(k+1)))
            tipo = gdal_array.GDALTypeCodeToNumericTypeCode(GDT)
            inteiro = True if GDT in (gdal.GDT_Byte,
                                      gdal.GDT_UInt16,
                                      gdal.GDT_Int16,
                                      gdal.GDT_UInt32,
                                      gdal.GDT_Int32) else False
            banda_nova = np.ones((n_lin,n_col), dtype = tipo) * (int(valor_nulo) if inteiro else valor_nulo)
            # Varrendo e preenchendo nova imagem
            for lin in range(n_lin):
                for col in range(n_col):
                    X = origem[0] + resol_X*(col + 0.5)
                    Y = origem[1] - resol_Y*(lin + 0.5)
                    X_antigo, Y_antigo = CoordInvTransf(QgsPointXY(X,Y))
                    Interpolado = Interpolar(X_antigo, Y_antigo,
                                            banda_antiga,
                                            origem_antiga,
                                            xres_antiga,
                                            yres_antiga,
                                            reamostragem,
                                            valor_nulo)
                    if Interpolado != valor_nulo:
                        banda_nova[lin][col] = round(Interpolado) if inteiro else Interpolado

                if feedback.isCanceled():
                    break
                current += 1
                feedback.setProgress(int(current * Percent))

            # Salvar banda
            outband = Driver.GetRasterBand(k+1)
            feedback.pushInfo(self.tr('Writing Band {}...'.format(k+1), 'Escrevendo Banda {}...'.format(k+1)))
            outband.WriteArray(banda_nova)
            outband.SetNoDataValue(valor_nulo)

        # Fechar Raster
        image = None # Close image

        Driver.FlushCache()   # Escrever no disco
        Driver = None   # Salvar e fechar

        # Salvando pontos estimados e precisões
        feat = QgsFeature()
        for ind, coord in enumerate(COORD):
            feat.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(coord[0], coord[1])))
            s_x = PREC[ind][0]
            s_y = PREC[ind][1]
            feat.setAttributes([ind+1, s_x, s_y])
            sink.addFeature(feat, QgsFeatureSink.FastInsert)
            if feedback.isCanceled():
                break

        # Exportar Relatório HTML
        arq = open(html_output, 'w')
        arq.write(texto)
        arq.close()

        feedback.pushInfo(self.tr('Operation completed successfully!', 'Operação finalizada com sucesso!'))
        feedback.pushInfo(self.tr('Leandro Franca - Cartographic Engineer', 'Leandro França - Eng Cart'))
        self.CAMINHO = Output
        self.CARREGAR = Carregar
        return {self.ADJUSTED: Output,
                self.COORDS: dest_id,
                self.HTML: html_output}

    # Carregamento de arquivo de saída
    def postProcessAlgorithm(self, context, feedback):
        if self.CARREGAR:
            rlayer = QgsRasterLayer(self.CAMINHO, self.tr('Adjusted Raster', 'Raster Ajustado'))
            QgsProject.instance().addMapLayer(rlayer)
        return {}
