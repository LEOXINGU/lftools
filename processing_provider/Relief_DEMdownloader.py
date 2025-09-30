# -*- coding: utf-8 -*-

"""
Relief_DEMdownloader.py
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
__date__ = '2024-11-09'
__copyright__ = '(C) 2024, Leandro França'

from qgis.core import *
import numpy as np
from lftools.geocapt.imgs import Imgs
from lftools.geocapt.cartography import reprojectPoints, gerar_tiles, folder_10x10_for_tile
from lftools.geocapt.dem import *
from lftools.translations.translate import translate
import os, processing
import urllib.request
from qgis.PyQt.QtGui import QIcon

class DEMdownloader(QgsProcessingAlgorithm):

    LOC = QgsApplication.locale()[:2]

    def tr(self, *string):
        return translate(string, self.LOC)

    def createInstance(self):
        return DEMdownloader()

    def name(self):
        return 'DEMdownloader'.lower()

    def displayName(self):
        return self.tr('DEM Downloader', 'Baixar MDE')

    def group(self):
        return self.tr('Relief', 'Relevo')

    def groupId(self):
        return 'relief'

    def tags(self):
        return 'GeoOne,dem,dsm,dtm,mde,mdt,baixar,download,mds,terreno,relevo,elevation,height,elevação'.split(',')

    def icon(self):
        return QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images/contours.png'))

    txt_en = '''A tool that streamlines the download of Digital Elevation Models (DEMs), allowing the user to define the area of interest directly in QGIS. It supports access to FABDEM and other modern DEMs, automatically generating the exact clipped extent for immediate use in your projects.'''
    txt_pt = '''Ferramenta que simplifica o download de Modelos Digitais de Elevação (MDE), permitindo ao usuário definir a área de interesse diretamente no QGIS. Suporta o acesso ao FABDEM e a outros MDEs modernos, gerando automaticamente o recorte exato da extensão selecionada para uso imediato em seus projetos.'''
    figure = 'images/tutorial/relief_defineZ.jpg'

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

    EXTENT = 'EXTENT'
    DATASET = 'DATASET'
    OUTPUT = 'OUTPUT'
    OPEN = 'OPEN'

    dataset = ['FABDEM']

    def initAlgorithm(self, config=None):

        # INPUT
        self.addParameter(
            QgsProcessingParameterExtent(
                self.EXTENT,
                self.tr('Extent', 'Extensão')
            )
        )

        self.addParameter(
            QgsProcessingParameterEnum(
                self.DATASET,
                self.tr('DEM', 'MDE'),
				options = self.dataset,
                defaultValue= 0
            )
        )

        self.addParameter(
            QgsProcessingParameterBoolean(
                self.OPEN,
                self.tr('Load output raster', 'Carregar MDE'),
                defaultValue= True
            )
        )

        # OUTPUT
        self.addParameter(
            QgsProcessingParameterFileDestination(
                self.OUTPUT,
                self.tr('Digital Elevation Model (DEM)', 'Modelo Digital de Elevação (MDE)'),
                fileFilter = 'GeoTIFF (*.tif)'
            )
        )

    def processAlgorithm(self, parameters, context, feedback):

        extensao = self.parameterAsExtent(
        parameters,
        self.EXTENT,
        context
        )
        y_min = extensao.yMinimum()
        y_max = extensao.yMaximum()
        x_min = extensao.xMinimum()
        x_max = extensao.xMaximum()

        ProjectCRS = QgsProject.instance().crs()
        if not ProjectCRS.isGeographic():
            crsGeo = QgsCoordinateReferenceSystem(ProjectCRS.geographicCrsAuthId())
            coordinateTransformer = QgsCoordinateTransform()
            coordinateTransformer.setDestinationCrs(crsGeo)
            coordinateTransformer.setSourceCrs(ProjectCRS)
            MinPoint = reprojectPoints(QgsGeometry(QgsPoint(x_min, y_min)), coordinateTransformer)
            MaxPoint = reprojectPoints(QgsGeometry(QgsPoint(x_max, y_max)), coordinateTransformer)
            MinPoint = MinPoint.asPoint()
            MaxPoint = MaxPoint.asPoint()
            lon_min, lat_min = MinPoint.x(), MinPoint.y()
            lon_max, lat_max = MaxPoint.x(), MaxPoint.y()
        else:
            lon_min, lat_min = x_min, y_min
            lon_max, lat_max = x_max, y_max
        
        dataset = self.parameterAsEnum(
            parameters,
            self.DATASET,
            context
        )

        self.datasetName = self.dataset[dataset]
        Tiles = ['FABDEM_tiles']
        dataset = eval(Tiles[dataset])
        
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

        # Listar datasets a partir da extensão
        tiles = gerar_tiles(lat_min, lat_max, lon_min, lon_max)
        out_folder = os.path.dirname(Output)
        # Verificar se cada tile tem correspondente no tipo de dataset 
        rasters = []
        for tile in tiles:
            if tile in dataset:
                pasta = folder_10x10_for_tile(tile) + '_FABDEM_V1-2'
                tile_name = f"{tile}_FABDEM_V1-2.tif"
                url = f"https://huggingface.co/datasets/links-ads/fabdem-v12/resolve/main/tiles/{pasta}/{tile_name}?download=true"
                
                try:
                    out_path = os.path.join(out_folder, tile_name)
                    feedback.pushInfo(self.tr("Downloading file", "Baixando arquivo") + f" {tile_name} ...")
                    urllib.request.urlretrieve(url, out_path)
                    rasters += [out_path]
                except:
                    feedback.reportError(self.tr("Problem in downloading" , "Problema ao baixar") + f" {tile_name}!")    
            if feedback.isCanceled():
                break
        # Mesclar arquivos temporários baixados (gera VRT se >1)
        if not rasters:
            raise QgsProcessingException(self.tr("No rasters were downloaded!", "Nenhum raster foi baixado!"))

        if len(rasters) == 1:
            mosaic_src = rasters[0]
        else:
            vrt_path = QgsProcessingUtils.generateTempFilename("mosaic.vrt")
            processing.run(
                "gdal:buildvirtualraster",
                {
                    "INPUT": rasters,
                    "RESOLUTION": 0,      # average / highest? (0 = highest)
                    "SEPARATE": False,
                    "ADD_ALPHA": False,
                    "ASSIGN_CRS": None,
                    "RESAMPLING": 0,      # nearest
                    "SRC_NODATA": None,
                    "EXTRA": "",
                    "OUTPUT": vrt_path
                },
                context=context,
                feedback=feedback
            )
            mosaic_src = vrt_path

        # Recortar o mosaico pela extensão (em WGS84) e salvar como output
        extent_str = f"{lon_min},{lon_max},{lat_min},{lat_max}"

        processing.run(
            "gdal:cliprasterbyextent",
            {
                "INPUT": mosaic_src,
                "PROJWIN": extent_str,
                "NODATA": -9999,
                "CROP_TO_CUTLINE": False,
                "DATA_TYPE": 0,  # manter tipo original
                "EXTRA": "",
                "OUTPUT": Output
            },
            context=context,
            feedback=feedback
        )

        
        feedback.pushInfo(self.tr('Operation completed successfully!', 'Operação finalizada com sucesso!'))
        feedback.pushInfo(self.tr('Leandro Franca - Cartographic Engineer', 'Leandro França - Eng Cart'))

        self.CAMINHO = Output
        self.CARREGAR = Carregar
        return {self.OUTPUT: Output}

    def postProcessAlgorithm(self, context, feedback):
        if self.CARREGAR:
            rlayer = QgsRasterLayer(self.CAMINHO, self.datasetName)
            QgsProject.instance().addMapLayer(rlayer)
        return {}
