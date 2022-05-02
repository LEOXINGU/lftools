# -*- coding: utf-8 -*-

"""
Drone_verticalAdjustment.py
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
__date__ = '2021-11-08'
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
from lftools.geocapt.dip import Interpolar
from lftools.geocapt.adjust import AjustVertical, ValidacaoGCP
import os
from qgis.PyQt.QtGui import QIcon

class VerticalAdjustment(QgsProcessingAlgorithm):

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
        return VerticalAdjustment()

    def name(self):
        return 'verticaladjustment'

    def displayName(self):
        return self.tr('Vertical adjustment', 'Ajuste Vertical')

    def group(self):
        return self.tr('Drones')

    def groupId(self):
        return 'drones'

    def tags(self):
        return self.tr('drone,model,modelo,mosaic,adjustment,raster,vertical,dem,dsm,mdt,georreferenciamento,ajuste,mds,dtm,GCP,ground control points,pontos de controle,elevation,terrain,surface').split(',')

    def icon(self):
        return QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images/drone.png'))

    txt_en = '''This tool performs the vertical adjustment of Digital Elevation Models (DEM) from Ground Control Points (GCP).'''
    txt_pt = '''Esta ferramenta realiza o ajuste vertical de Modelos Digitais de Elevação (MDE) a partir de Pontos de Controle no Terreno (GCP).'''
    figure = 'images/tutorial/drone_verticalAdjustment.jpg'

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
    POINTS = 'POINTS'
    FIELD = 'FIELD'
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
                self.DEM,
                self.tr('Digital Elevation Model (DEM)', 'Modelo Digital de Elevação (MDE)'),
                [QgsProcessing.TypeRaster]
            )
        )

        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.POINTS,
                self.tr('Ground Control Points (GCP)', 'Pontos de Controle no Terrno (GCP)'),
                [QgsProcessing.TypeVectorPoint]
            )
        )

        self.addParameter(
            QgsProcessingParameterField(
                self.FIELD,
                self.tr('Z Coordinate', 'Coordenada Z'),
                parentLayerParameterName=self.POINTS,
                type=QgsProcessingParameterField.Numeric
            )
        )

        self.addParameter(
            QgsProcessingParameterBoolean(
                self.CHECKCRS,
                self.tr('Check CRS', 'Verificar SRC'),
                defaultValue= True
            )
        )

        tipos = [self.tr('Constant','Constante'),
                  self.tr('Plane','Plano')
               ]

        self.addParameter(
            QgsProcessingParameterEnum(
                self.METHOD,
                self.tr('Method', 'Método'),
				options = tipos,
                defaultValue= 0
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
                defaultValue= 1
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
        dem = self.parameterAsRasterLayer(
            parameters,
            self.DEM,
            context
        )
        if dem is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.DEM))
        dem = dem.dataProvider().dataSourceUri()

        reamostragem = self.parameterAsEnum(
            parameters,
            self.RESAMPLING,
            context
        )
        reamostragem = ['nearest','bilinear','bicubic'][reamostragem]

        pontos = self.parameterAsSource(
            parameters,
            self.POINTS,
            context
        )
        if pontos is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.POINTS))

        Z_field = self.parameterAsFields(
            parameters,
            self.FIELD,
            context
        )
        if Z_field:
            Z_id = pontos.fields().indexFromName(Z_field[0])

        metodo = self.parameterAsEnum(
            parameters,
            self.METHOD,
            context
        )

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
        Fields = pontos.fields()
        CRS = pontos.sourceCrs()
        prj = CRS.toWkt()

        itens  = {   self.tr('delta_z') : QVariant.Double,
                     self.tr('adjusted_z', 'z_ajustado') : QVariant.Double,
                     self.tr('precision_z','precisao_z') : QVariant.Double
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

        image = gdal.Open(dem)
        #prj = image.GetProjection() # wkt
        SRC = QgsCoordinateReferenceSystem(image.GetProjection())
        geotransform = image.GetGeoTransform()
        ulx, xres, xskew, uly, yskew, yres  = geotransform
        cols = image.RasterXSize
        rows = image.RasterYSize
        n_bands = image.RasterCount
        if n_bands != 1:
            raise QgsProcessingException(self.tr('The DEM raster layer must have only one band!', 'A camada raster do MDE deve ter apenas uma banda!'))
        banda = image.GetRasterBand(1).ReadAsArray()
        GDT = image.GetRasterBand(1).DataType
        valor_nulo = image.GetRasterBand(1).GetNoDataValue()
        if not valor_nulo:
            valor_nulo = 0
        origem = (ulx, uly)
        xres = abs(xres)
        yres = abs(yres)
        # Fechar Raster
        image = None # Close image

        ## Validar dados de entrada
        # Verificar se o Raster e os Vetores tem o mesmo SRC
        if checkCRS:
            if not SRC.description() == CRS.description():
                raise QgsProcessingException(self.tr('The raster layer and the GCP layer must have the same CRS!', 'A camada raster e a camada vetorial de GCP devem ter o mesmo SRC!'))

        feedback.pushInfo(self.tr('Size: ', 'Tamanho: ') + str(rows) +'x' + str(cols))

        # lista de Valores para Ajustamento
        feedback.pushInfo(self.tr('Determining values for the adjustment...', 'Determinando valores para o ajustamento...'))
        lista =[]
        for feat in pontos.getFeatures():
            coord = feat.geometry().asPoint()
            X = coord.x()
            Y = coord.y()
            Z = feat[Z_id]
            Zf = Interpolar(X, Y,
                            banda,
                            origem,
                            xres,
                            yres,
                            reamostragem,
                            valor_nulo)
            lista += [[(X,Y,Z),Zf]]

        # Ajustamento
        feedback.pushInfo(self.tr('Calculating adjustment parameters...', 'Calculando parâmetros de ajustamento...'))
        COTAS, PREC, DELTA, CoordTransf, texto = AjustVertical(lista, metodo)

        # Criar Raster
        Driver = gdal.GetDriverByName('GTiff').Create(Output, cols, rows, n_bands, GDT)
        Driver.SetGeoTransform(geotransform)
        Driver.SetProjection(prj)
        outband = Driver.GetRasterBand(1)

        # Fazer correção do Raster
        feedback.pushInfo(self.tr("Adjusting the DEM...", 'Ajustando o MDE...'))
        if metodo == 0:
            k = CoordTransf(0,0)
            banda_nova = (banda + k)*(banda != valor_nulo) + valor_nulo*(banda == valor_nulo)
            # Salvar banda
            feedback.pushInfo(self.tr('Writing Band {}...'.format(1), 'Escrevendo Banda {}...'.format(1)))
            outband.WriteArray(banda_nova)
            outband.SetNoDataValue(valor_nulo)
        elif metodo == 1:
            Percent = 100.0/rows
            current = 0
            banda_nova = banda
            for lin in range(rows):
                for col in range(cols):
                    if banda[lin][col] != valor_nulo:
                        X = origem[0] + xres*(col + 0.5)
                        Y = origem[1] - yres*(lin + 0.5)
                        dz = CoordTransf(X, Y)
                        banda_nova[lin][col] = banda[lin][col] + dz
                if feedback.isCanceled():
                    break
                current += 1
                feedback.setProgress(int(current * Percent))
            # Salvar banda
            feedback.pushInfo(self.tr('Writing Band {}...'.format(1), 'Escrevendo Banda {}...'.format(1)))
            outband.WriteArray(banda_nova)
            outband.SetNoDataValue(valor_nulo)

        del banda_nova, banda
        Driver.FlushCache()   # Escrever no disco
        Driver = None   # Salvar e fechar

        # Salvando pontos de controle com discrepancias e precisões
        feature = QgsFeature(Fields)
        for ind, feat in enumerate(pontos.getFeatures()):
            feature.setGeometry(feat.geometry())
            z_aj = float(COTAS[ind])
            s_z = float(PREC[ind])
            d_z = float(DELTA[ind])
            feature.setAttributes(feat.attributes() + [d_z, z_aj, s_z])
            sink.addFeature(feature, QgsFeatureSink.FastInsert)
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
