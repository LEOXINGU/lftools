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
from lftools.geocapt.imgs import Imgs
from lftools.geocapt.cartography import reprojectPoints, gerar_tiles, folder_10x10_for_tile
from lftools.geocapt.dem import *
from lftools.translations.translate import translate
import os
import gzip
import shutil
import processing
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
        return 'GeoOne,dem,dsm,dtm,mde,mdt,baixar,srtm,fabdem,anadem,copernicus,opentopography,topography,topografia,open,download,mds,terreno,relevo,elevation,height,elevação'.split(',')

    def icon(self):
        return QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images/contours.png'))

    txt_en = '''A tool that streamlines the download of Digital Elevation Models (DEMs), allowing the user to define the area of interest directly in QGIS. It supports access to FABDEM and other modern DEMs, automatically generating the exact clipped extent for immediate use in your projects.'''
    txt_pt = '''Ferramenta que simplifica o download de Modelos Digitais de Elevação (MDE), permitindo ao usuário definir a área de interesse diretamente no QGIS. Suporta o acesso ao FABDEM e a outros MDEs modernos, gerando automaticamente o recorte exato da extensão selecionada para uso imediato em seus projetos.'''
    figure = 'images/tutorial/relief_download.jpg'

    def shortHelpString(self):
        social_BW = Imgs().social_BW
        footer = '''<div align="center">
                      <img src="'''+ os.path.join(os.path.dirname(os.path.dirname(__file__)), self.figure) +'''">
                      </div>
                      <div align="right">
                      <small>Credits:</small>
                      <small>FABDEM - global 30 m bare-earth DEM derived from Copernicus GLO-30 developed by Hawker et al., 2022. University of Bristol.</small>
                      <small>ANADEM - digital terrain model for South America developed by Laipelt, L. et al., 2024. ANA/UFRGS. 2024.</small>
                      <small>GMTED2010 - Global Multi-resolution Terrain Elevation Data 2010. USGS / NGA.</small>
                      <small>SRTM - Shuttle Radar Topography Mission global DEM.</small>
                      <small>Copernicus DEM GLO-30 - Global 30 m DEM derived from WorldDEM.</small>
                      <p align="right">
                      <b>'''+self.tr('Author: Leandro Franca', 'Autor: Leandro França')+'''</b>
                      </p>'''+ social_BW + '''</div>
                    </div>'''
        return self.tr(self.txt_en, self.txt_pt) + footer

    EXTENT = 'EXTENT'
    DATASET = 'DATASET'
    OUTPUT = 'OUTPUT'
    OPEN = 'OPEN'

    dataset = ['FABDEM - Global - 1 arc sec',
               'ANADEM - South America - 1 arc sec',
               'GMTED2010 - Global - 30 arc sec',
               'SRTM - Global - 1 arc sec',
               'Copernicus DEM GLO-30 - Global - 1 arc sec']

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
            crsGeo = QgsCoordinateReferenceSystem("EPSG:4326")
            coordinateTransformer = QgsCoordinateTransform(
                ProjectCRS,
                crsGeo,
                QgsProject.instance()
            )
            MinPoint = reprojectPoints(QgsGeometry(QgsPoint(x_min, y_min)), coordinateTransformer)
            MaxPoint = reprojectPoints(QgsGeometry(QgsPoint(x_max, y_max)), coordinateTransformer)
            MinPoint = MinPoint.asPoint()
            MaxPoint = MaxPoint.asPoint()
            lon_min, lat_min = MinPoint.x(), MinPoint.y()
            lon_max, lat_max = MaxPoint.x(), MaxPoint.y()
        else:
            lon_min, lat_min = x_min, y_min
            lon_max, lat_max = x_max, y_max
        
        mde = self.parameterAsEnum(
            parameters,
            self.DATASET,
            context
        )

        self.datasetName = self.dataset[mde]

        Tiles = [FABDEM_tiles, ANADEM_tiles, GMTED_tiles, SRTM_tiles, COPDEM30_tiles]
        dataset = Tiles[mde]
        
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
        if mde in [0, 1, 3, 4]:  # FABDEM, ANADEM, SRTM, Copernicus
            tiles = gerar_tiles(lat_min, lat_max, lon_min, lon_max)
        elif mde == 2:  # GMTED2010
            tiles = gerar_tiles(lat_min, lat_max, lon_min, lon_max, lat0=-56.0, lon0=-180.0, step_lat=20.0, step_lon=30.0)
        
        max_tiles = 4 if mde in [0, 1, 4] else 9
        if len(tiles) > max_tiles:
            raise QgsProcessingException(
                self.tr("Define a smaller extent on the map!",
                        "Defina uma extensão menor no mapa!")
            )
        
        out_folder = os.path.dirname(Output)
        rasters = []

        for k, tile in enumerate(tiles):

            if feedback.isCanceled():
                break

            tile_exists = tile in dataset

            if not tile_exists:
                feedback.reportError(f"[{k+1}/{len(tiles)}] {tile} is not in the dataset!")
                continue

            # Montar nome e URL conforme o dataset
            if mde == 0:  # FABDEM
                pasta = folder_10x10_for_tile(tile) + '_FABDEM_V1-2'
                tile_name = f"{tile}_FABDEM_V1-2.tif"
                url = f"https://huggingface.co/datasets/links-ads/fabdem-v12/resolve/main/tiles/{pasta}/{tile_name}?download=true"

            elif mde == 1:  # ANADEM
                pasta = folder_10x10_for_tile(tile) + '_ANADEM_V1'
                tile_name = f"{tile}_ANADEM_V1.tif"
                url = f"https://huggingface.co/datasets/GeoOne/anadem-v1/resolve/main/tiles/{pasta}/{tile_name}?download=true"

            elif mde == 2:  # GMTED2010
                tile_name = f"{tile}_GMTED2010_be30.tif"
                url = f"https://huggingface.co/datasets/GeoOne/GMTED2010/resolve/main/{tile_name}?download=1"

            elif mde == 3:  # SRTM
                tile_name, url = self.srtm_url(tile)

            elif mde == 4:  # Copernicus DEM
                tile_name, url = self.copdem_url(tile)

            try:
                out_path = os.path.join(out_folder, tile_name)
                feedback.pushInfo(
                    f"[{k+1}/{len(tiles)}] " +
                    self.tr("Downloading file", "Baixando arquivo") +
                    f" {tile_name} ..."
                )
                urllib.request.urlretrieve(url, out_path)

                # Tratamento específico do SRTM
                if mde == 3:
                    # feedback.pushInfo(
                    #     f"[{k+1}/{len(tiles)}] " +
                    #     self.tr("Decompressing file", "Descompactando arquivo") +
                    #     f" {tile_name} ..."
                    # )
                    hgt_path = self.gunzip_file(out_path)
                    try:
                        os.remove(out_path)  # remove o .gz após descompactar
                    except:
                        pass
                    rasters += [hgt_path]
                else:
                    rasters += [out_path]

            except Exception as e:
                feedback.reportError(
                    f"[{k+1}/{len(tiles)}] " +
                    self.tr("Problem downloading", "Problema ao baixar") +
                    f" {tile_name}! {str(e)}"
                )

        # Mesclar arquivos temporários baixados (gera VRT se > 1)
        if not rasters:
            raise QgsProcessingException(self.tr("No raster was downloaded!", "Nenhum raster foi baixado!"))

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
                # "OVERCRS": False,
                "NODATA": -9999,
                "CROP_TO_CUTLINE": False,
                "DATA_TYPE": 0,  # manter tipo original
                "EXTRA": "",
                "OUTPUT": Output
            },
            context=context,
            feedback=feedback
        )

        for rst in rasters:
            try:
                os.remove(rst)
            except:
                pass

        
        feedback.pushInfo(self.tr('Operation completed successfully!', 'Operação finalizada com sucesso!'))
        feedback.pushInfo(self.tr('Leandro Franca - Cartographic Engineer', 'Leandro França - Eng Cart'))

        self.CAMINHO = Output
        self.CARREGAR = Carregar
        return {self.OUTPUT: Output}

    
    def srtm_tile_name(self, tile):
        return f"{tile}.hgt.gz"

    def srtm_url(self, tile):
        pasta = tile[:3]  # ex.: S07, N00
        tile_name = self.srtm_tile_name(tile)
        return tile_name, f"https://s3.amazonaws.com/elevation-tiles-prod/skadi/{pasta}/{tile_name}"

    def copdem_tile_name(self, tile):
        # tile no formato N00E000
        lat_tag = tile[:3]   # N00 / S07
        lon_tag = tile[3:]   # E000 / W035
        lat_num = lat_tag[1:]
        lon_num = lon_tag[1:]
        lat_hemi = lat_tag[0]
        lon_hemi = lon_tag[0]
        return f"Copernicus_DSM_COG_10_{lat_hemi}{lat_num}_00_{lon_hemi}{lon_num}_00_DEM.tif"

    def copdem_url(self, tile):
        tile_name = self.copdem_tile_name(tile).replace('.tif', '')
        url = f"https://copernicus-dem-30m.s3.amazonaws.com/{tile_name}/{tile_name}.tif"
        return tile_name + '.tif', url

    def gunzip_file(self, gz_path):
        out_path = gz_path[:-3]  # remove .gz
        with gzip.open(gz_path, 'rb') as f_in:
            with open(out_path, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        return out_path

    
    def postProcessAlgorithm(self, context, feedback):
        if self.CARREGAR:
            rlayer = QgsRasterLayer(self.CAMINHO, self.datasetName)
            QgsProject.instance().addMapLayer(rlayer)
        return {}
