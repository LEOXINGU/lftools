# -*- coding: utf-8 -*-

"""
mosaicRaster.py
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
__date__ = '2021-01-12'
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
from itertools import combinations
from matplotlib import path
import numpy as np
from pyproj.crs import CRS
from math import floor, ceil
from lftools.geocapt.imgs import Imgs
from lftools.translations.translate import translate
from lftools.geocapt.dip import Interpolar
import os
from qgis.PyQt.QtGui import QIcon

class MosaicRaster(QgsProcessingAlgorithm):

    LOC = QgsApplication.locale()[:2]

    def tr(self, *string):
        return translate(string, self.LOC)

    def createInstance(self):
        return MosaicRaster()

    def name(self):
        return 'mosaicraster'

    def displayName(self):
        return self.tr('Mosaic raster', 'Mosaicar raster')

    def group(self):
        return self.tr('Raster')

    def groupId(self):
        return 'raster'

    def tags(self):
        return self.tr('mosaic,merge,raster,combine,mosaik,mosaico,mesclar').split(',')

    def icon(self):
        return QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images/raster.png'))

    txt_en = 'Creates raster mosaic: a combination or merge of two or more images.'
    txt_pt = 'Cria um mosaico: uma combinação ou mesclagem de duas ou mais imagens.'
    figure = 'images/tutorial/raster_mosaic.jpg'

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

    RASTERLIST ='RASTERLIST'
    RESOLUTION = 'RESOLUTION'
    OVERLAP = 'OVERLAP'
    NULLVALUE = 'NULLVALUE'
    RESAMPLING = 'RESAMPLING'
    FRAME = 'FRAME'
    MOSAIC = 'MOSAIC'
    OPEN = 'OPEN'

    def initAlgorithm(self, config=None):
        # INPUT
        self.addParameter(
            QgsProcessingParameterMultipleLayers(
                self.RASTERLIST,
                self.tr('Raster List', 'Lista de Rasters'),
                layerType = QgsProcessing.TypeRaster
            )
        )

        self.addParameter(
            QgsProcessingParameterNumber(
                self.RESOLUTION,
                self.tr('New Resolution (meters)', 'Nova resolução espacial (metros)'),
                type = QgsProcessingParameterNumber.Type.Double, #Double = 1 and Integer = 0
                defaultValue = None,
                minValue = 0.01,
                optional = True
            )
        )

        sobrep = [self.tr('First (faster)', 'Primeiro (mais rápido)'),
                 self.tr('Average', 'Média'),
                 self.tr('Median', 'Mediana'),
                 self.tr('Maximum', 'Máximo'),
                 self.tr('Minimum', 'Mínimo')]

        self.addParameter(
            QgsProcessingParameterEnum(
                self.OVERLAP,
                self.tr('Ovelap', 'Sobreposição'),
				options = sobrep,
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
                defaultValue= 0
            )
        )

        self.addParameter(
            QgsProcessingParameterNumber(
                self.NULLVALUE,
                self.tr('Null value', 'Valor nulo'),
                type = QgsProcessingParameterNumber.Type.Integer, #Double = 1 and Integer = 0
                defaultValue = 0
            )
        )

        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.FRAME,
                self.tr('Clip by frame', 'Cortar pela moldura'),
                [QgsProcessing.TypeVectorPolygon],
                optional = True
            )
        )

        # OUTPUT
        self.addParameter(
            QgsProcessingParameterFileDestination(
                self.MOSAIC,
                self.tr('Mosaic', 'Mosaico'),
                fileFilter = 'GeoTIFF (*.tif)'
            )
        )

        self.addParameter(
            QgsProcessingParameterBoolean(
                self.OPEN,
                self.tr('Load mosaic', 'Carregar mosaico'),
                defaultValue= True
            )
        )


    def processAlgorithm(self, parameters, context, feedback):

        # inputs
        rasters = self.parameterAsLayerList(
            parameters,
            self.RASTERLIST,
            context
        )
        if rasters is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.RASTERLIST))

        reamostragem = self.parameterAsEnum(
            parameters,
            self.RESAMPLING,
            context
        )
        reamostragem = ['nearest','bilinear','bicubic'][reamostragem]

        sobrep = self.parameterAsEnum(
            parameters,
            self.OVERLAP,
            context
        )

        resolucao = self.parameterAsDouble(
            parameters,
            self.RESOLUTION,
            context
        )

        valor_nulo = self.parameterAsDouble(
            parameters,
            self.NULLVALUE,
            context
        )


        vlayer = self.parameterAsVectorLayer(
            parameters,
            self.FRAME,
            context
        )

        # output

        Output = self.parameterAsFileOutput(
            parameters,
            self.MOSAIC,
            context
        )

        Carregar = self.parameterAsBool(
            parameters,
            self.OPEN,
            context
        )


        lista = []
        for raster_lyr in rasters:
            lista += [raster_lyr.dataProvider().dataSourceUri()]
        if len(lista) < 1:
            raise QgsProcessingException(self.tr('At least one raster must be selected!', 'Pelo menos um raster deve ser selecionado!'))
        if len(lista) == 1:
            sobrep = 0 # apenas um raster (sem sobreposicao)

        # Gerar geometria para cada raster
        geoms = []
        SRC = []
        n_bands =[]
        GDT = []
        nulos = []
        XRES, YRES = [], []
        for item in lista:
            image = gdal.Open(item)
            SRC += [QgsCoordinateReferenceSystem(image.GetProjection())] # wkt
            ulx, xres, xskew, uly, yskew, yres  = image.GetGeoTransform()
            cols = image.RasterXSize
            rows = image.RasterYSize
            n_bands += [image.RasterCount]
            GDT += [image.GetRasterBand(1).DataType]
            nulos += [image.GetRasterBand(1).GetNoDataValue()]
            XRES += [xres]
            YRES += [yres]
            image=None # Close image
            # Creating BBox
            coord = [[QgsPointXY(ulx, uly),
                      QgsPointXY(ulx+cols*xres, uly),
                      QgsPointXY(ulx+cols*xres, uly+rows*yres),
                      QgsPointXY(ulx, uly+rows*yres),
                      QgsPointXY(ulx, uly)]]
            geom = QgsGeometry.fromPolygonXY(coord)
            geoms += [geom]

        ## Validar dados de entrada
        # Mesmo numero de bandas
        if not n_bands.count(n_bands[0]) == len(n_bands):
            raise QgsProcessingException(self.tr('The images must have the same number of bands!', 'As imagens devem ter o mesmo número de bandas!'))
        # Mesmo SRC
        if not SRC.count(SRC[0]) == len(SRC):
            raise QgsProcessingException(self.tr('The images must have the same CRS!', 'As imagens devem ter o mesmo SRC!'))
        # Mesmo GDT
        if not GDT.count(GDT[0]) == len(GDT):
            raise QgsProcessingException(self.tr('The images must have the same data type!', 'As imagens devem ter o tipo de dado!'))
        # Mesmo valor nulo
        if not nulos.count(nulos[0]) == len(nulos):
            raise QgsProcessingException(self.tr('The images must have the same definied null value!', 'As imagens devem ter o mesmo valor para definir pixel nulo!'))

        # Dados para o raster de saída
        prj = SRC[0].toWkt()
        n_bands = n_bands[0]
        GDT = GDT[0]
        xres = np.mean(XRES)
        yres = np.mean(YRES)
        NULO = valor_nulo
        if valor_nulo == -1:
            valor_nulo = nulos[0] if nulos[0] is not None else 0

        if vlayer: # Pegar extensão X e Y da moldura
            # SRC da moldura deve ser o mesmo dos raster
            if vlayer.sourceCrs() != QgsCoordinateReferenceSystem(prj):
                raise QgsProcessingException(self.tr("The frame's CRS must be iqual to the rasters' CRS!", 'O SRC da moldura deve ser igual ao SRC dos rasters!'))
            for feat in vlayer.getFeatures():
                moldura_geom = feat.geometry()
                break
            moldura_rect = moldura_geom.boundingBox()
            y_min = moldura_rect.yMinimum()
            y_max = moldura_rect.yMaximum()
            x_min = moldura_rect.xMinimum()
            x_max = moldura_rect.xMaximum()
        else: # Mesclar geometrias e obter a extensão
            new_geom = QgsGeometry()
            new_geom = new_geom.unaryUnion(geoms)
            extensao = new_geom.boundingBox()
            # Coodenadas máxima e mínima da extensão
            y_min = extensao.yMinimum()
            y_max = extensao.yMaximum()
            x_min = extensao.xMinimum()
            x_max = extensao.xMaximum()

        # Transformar resolucao de metros para graus, se o SRC for Geográfico
        src_qgis = QgsCoordinateReferenceSystem(prj)
        if src_qgis.isGeographic():
            EPSG = int(src_qgis.authid().split(':')[-1])
            proj_crs = CRS.from_epsg(EPSG)
            a=proj_crs.ellipsoid.semi_major_metre
            f=1/proj_crs.ellipsoid.inverse_flattening
            e2 = f*(2-f)
            N = a/np.sqrt(1-e2*(np.sin((y_min+y_max)/2))**2) # Raio de curvatura 1º vertical
            M = a*(1-e2)/(1-e2*(np.sin((y_min+y_max)/2))**2)**(3/2.) # Raio de curvatura meridiana
            R = np.sqrt(M*N) # Raio médio de Gauss
            theta = resolucao/R
            resolucao = np.degrees(theta) # Radianos para graus

        # Definir n_col, n_lin e resolucao
        if vlayer:
            if resolucao:
                n_lin = round((y_max-y_min)/abs(resolucao))
                n_col = round((x_max-x_min)/abs(resolucao))
            else:
                n_lin = round((y_max-y_min)/abs(yres))
                n_col = round((x_max-x_min)/abs(xres))
            xres = (x_max-x_min)/n_col
            yres = -(y_max-y_min)/n_lin
        else:
            if resolucao:
                n_lin = round((y_max-y_min)/abs(resolucao))
                n_col = round((x_max-x_min)/abs(resolucao))
                xres = resolucao
                yres = -resolucao
            else:
                n_lin = round((y_max-y_min)/abs(yres))
                n_col = round((x_max-x_min)/abs(xres))
                xres = (x_max-x_min)/n_col
                yres = -(y_max-y_min)/n_lin

        feedback.pushInfo(self.tr('Size: ', 'Tamanho: ') + str(n_lin) +'x' + str(n_col))
        # Geotransform do Mosaico
        ulx = x_min
        uly = y_max
        xskew, yskew = 0, 0
        geotransform = [ulx, xres, xskew, uly, yskew, yres]
        origem = (ulx, uly)
        resol_X = abs(xres)
        resol_Y = abs(yres)
        # Numeração das Imagens
        valores = list(range(1,len(lista)+1))

        # Definição de áreas de varredura
        feedback.pushInfo(self.tr('Defining mosaic filling areas...', 'Definindo áreas de preenchimento do mosaico...'))

        # Gerar combinações dos Rasters
        if sobrep != 0:
            combs = []
            feedback.pushInfo(self.tr('Creating combinations...', 'Gerando combinações...'))
            for k in range(1,5):
                combs += list(combinations(valores,k))
                if feedback.isCanceled():
                    break
            # Armazenar geometrias exclusivas de cada combinação
            classes = {}
            feedback.pushInfo(self.tr('Indentifying combinations...', 'Identificando combinações...'))
            Percent = 100.0/(len(combs))
            current = 0

            for comb in combs:
                if len(comb)==1:
                    geom1 = geoms[comb[0]-1]
                    lista_outras = []
                    for geom in geoms:
                        if geom1 != geom:
                            lista_outras += [geom]
                    outras = QgsGeometry()
                    outras = outras.unaryUnion(lista_outras)
                    diferença = geom1.difference(outras)
                    if not diferença.isEmpty():
                        classes[comb] = {'geom': diferença}
                elif len(comb) < len(valores):
                    intersecao = geoms[comb[0]-1]
                    sentinela = True
                    for ind in comb[1:]:
                        geom = geoms[ind-1]
                        if geom.intersects(intersecao):
                            intersecao = intersecao.intersection(geom)
                        else:
                            sentinela = False
                            continue
                    lista_outras = []
                    for valor in valores:
                        if valor not in comb:
                            lista_outras += [geoms[valor-1]]
                    outras = QgsGeometry()
                    outras = outras.unaryUnion(lista_outras)
                    if sentinela:
                        diferença = intersecao.difference(outras)
                        if not diferença.isEmpty():
                            classes[comb] = {'geom': diferença}
                else:
                    intersecao = geoms[comb[0]-1]
                    sentinela = True
                    for ind in comb[1:]:
                        geom = geoms[ind-1]
                        if geom.intersects(intersecao):
                            intersecao = intersecao.intersection(geom)
                        else:
                            sentinela = False
                            continue
                    if sentinela:
                        classes[comb] = {'geom': intersecao}
                if feedback.isCanceled():
                    break
                current += 1
                feedback.setProgress(int(current * Percent))
        else:
            # Gerar geometrias por área sem cálculo de sobreposição ("first")
            combs = np.array(valores)[:,np.newaxis]
            classes = {}
            acumulado = geoms[combs[0][0]-1]
            classes[(1,)] = {'geom': acumulado}
            for k in range(1, len(combs)):
                comb = combs[k]
                geom = geoms[comb[0]-1]
                diferenca = geom.difference(acumulado)
                classes[(comb[0],)] = {'geom': diferenca}
                acumulado = acumulado.combine(geom)
                if feedback.isCanceled():
                    break

        # Gerar lista com os valores classificados
        Percent = 100.0/(len(classes))
        current = 0
        cont_px = 0
        for classe in classes:
            feedback.pushInfo((self.tr('Classifying class {}...', 'Classificando classe {}...')).format(str(classe)))
            geom = classes[classe]['geom']
            if vlayer:
                geom = geom.intersection(moldura_geom)
            if geom.type() == 2:
                if geom.isMultipart():
                    coords = geom.asMultiPolygon()[0][0]
                else:
                    coords = geom.asPolygon()[0]
            else:
                del classes[classe]
                continue
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
            lin, col = np.meshgrid(np.arange(row_ini, row_fim),np.arange(col_ini, col_fim))
            LIN = lin.flatten()[:,np.newaxis]
            COL = col.flatten()[:,np.newaxis]
            pixels_center = np.hstack((LIN + 0.5, COL + 0.5)) # centro do pixel
            # Verificando pixels dentro de poligono
            flags = p.contains_points(pixels_center)
            pixels_x = (LIN+1).flatten()*flags # soma e subtrair 1 para evitar zero
            pixels_y = (COL+1).flatten()*flags
            pixels_x = (pixels_x[pixels_x>0]-1)[:,np.newaxis]
            pixels_y = (pixels_y[pixels_y>0]-1)[:,np.newaxis]
            pixels = np.hstack((pixels_x, pixels_y))
            classes[classe]['pixels'] = pixels
            cont_px += len(pixels)
            current += 1
            feedback.setProgress(int(current * Percent))

        # Criar Raster
        Driver = gdal.GetDriverByName('GTiff').Create(Output, n_col, n_lin, n_bands, GDT)
        Driver.SetGeoTransform(geotransform)
        Driver.SetProjection(prj)


        # Mosaicar por banda
        Percent = 100.0/(cont_px*n_bands)
        current = 0

        for k in range(n_bands):
            feedback.pushInfo((self.tr('Creating band {}...', 'Criando banda {}...')).format(str(k+1)))
            # Criar Array do mosaico
            tipo = gdal_array.GDALTypeCodeToNumericTypeCode(GDT)
            inteiro = True if GDT in (gdal.GDT_Byte,
                                      gdal.GDT_UInt16,
                                      gdal.GDT_Int16,
                                      gdal.GDT_UInt32,
                                      gdal.GDT_Int32) else False
            banda = np.ones((n_lin,n_col), dtype = tipo) * (int(valor_nulo) if inteiro else valor_nulo)
            imgs = {}
            # Para cada classe abrir banda da(s) imagem(ns)
            for classe in classes:
                # Deixando somente imagens a serem utilizadas
                for item in valores:
                    if (item not in classe) and (item in imgs):
                        del imgs[item]
                # Preenchendo dados da imagem no dicionário
                for img in classe:
                    if img not in imgs or len(lista) == 1:
                        img_path = lista[img-1]
                        image = gdal.Open(img_path)
                        ulx, xres, xskew, uly, yskew, yres  = image.GetGeoTransform()
                        img_origem = (ulx, uly)
                        img_resol_X = abs(xres)
                        img_resol_Y = abs(yres)
                        img_band = image.GetRasterBand(k+1).ReadAsArray()
                        imgs[img] = {'band': img_band,
                                     'xres': img_resol_X,
                                     'yres': img_resol_Y,
                                     'origem': img_origem }
                        image = None

                if sobrep == 0: # Se for "primeiro", interpolar apenas da primeira img da comb, caso contrário
                    img = classe[0]
                    # Para cada pixel da classe
                    for px in classes[classe]['pixels']:
                        lin,col = px
                        X = origem[0] + resol_X*(col + 0.5)
                        Y = origem[1] - resol_Y*(lin + 0.5)
                        Interpolado = Interpolar(X, Y,
                                                imgs[img]['band'],
                                                imgs[img]['origem'],
                                                imgs[img]['xres'],
                                                imgs[img]['yres'],
                                                reamostragem,
                                                valor_nulo)
                        if Interpolado != valor_nulo:
                            banda[lin][col] = round(Interpolado) if inteiro else Interpolado

                        if feedback.isCanceled():
                            break
                        current += 1
                        feedback.setProgress(int(current * Percent))

                else: # Para cada pixel da classe interpolar o valor da banda de cada img
                    for px in classes[classe]['pixels']:
                        lin,col = px
                        X = origem[0] + resol_X*(col + 0.5)
                        Y = origem[1] - resol_Y*(lin + 0.5)
                        interp_values = []
                        for img in imgs:
                            Interpolado = Interpolar(X, Y,
                                                     imgs[img]['band'],
                                                     imgs[img]['origem'],
                                                     imgs[img]['xres'],
                                                     imgs[img]['yres'],
                                                     reamostragem,
                                                     valor_nulo)
                            if Interpolado != valor_nulo:
                                interp_values += [Interpolado]
                        # Calcular o valor agregado (0:first, 1:average, 2:median, 3:min, 4:max) e inserir na banda (se byte, arredondar)
                        if interp_values:
                            if sobrep == 1:
                                result = np.mean(interp_values)
                            elif sobrep == 2:
                                result = np.median(interp_values)
                            elif sobrep == 3:
                                result = np.min(interp_values)
                            elif sobrep == 4:
                                result = np.max(interp_values)
                            banda[lin][col] = round(result) if inteiro else result

                        if feedback.isCanceled():
                            break
                        current += 1
                        feedback.setProgress(int(current * Percent))

            # Salvar banda
            outband = Driver.GetRasterBand(k+1)
            feedback.pushInfo(self.tr('Writing Band {}...'.format(k+1), 'Escrevendo Banda {}...'.format(k+1)))
            outband.WriteArray(banda)
            if NULO != -1:
                outband.SetNoDataValue(valor_nulo)

        # Salvar e Fechar Raster
        Driver.FlushCache()   # Escrever no disco
        Driver = None   # Salvar e fechar


        feedback.pushInfo(self.tr('Operation completed successfully!', 'Operação finalizada com sucesso!'))
        feedback.pushInfo(self.tr('Leandro Franca - Cartographic Engineer', 'Leandro França - Eng Cart'))
        self.CAMINHO = Output
        self.CARREGAR = Carregar
        return {self.MOSAIC: Output}

    # Carregamento de arquivo de saída
    def postProcessAlgorithm(self, context, feedback):
        if self.CARREGAR:
            rlayer = QgsRasterLayer(self.CAMINHO, self.tr('Mosaic', 'Mosaico'))
            QgsProject.instance().addMapLayer(rlayer)
        return {}
