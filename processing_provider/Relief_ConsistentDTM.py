# -*- coding: utf-8 -*-
"""
Relief_ConsistentDTM.py
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
__date__ = '2026-09-26'
__copyright__ = '(C) 2026, Leandro França'

from qgis.core import (QgsProcessingAlgorithm,
                       QgsProcessingException,
                       QgsProcessingParameterBoolean,
                       QgsProcessingParameterEnum,
                       QgsProcessingParameterFileDestination,
                       QgsProcessingParameterRasterLayer,
                       QgsApplication,
                       QgsProject,
                       QgsRasterLayer)

from osgeo import gdal
import numpy as np
from lftools.geocapt.imgs import Imgs
from lftools.translations.translate import translate
import os
import tempfile
from qgis.PyQt.QtGui import QIcon


class ConsistentDTM(QgsProcessingAlgorithm):

    LOC = QgsApplication.locale()[:2]

    def tr(self, *string):
        return translate(string, self.LOC)

    def createInstance(self):
        return ConsistentDTM()

    def name(self):
        return 'consistentdtm'

    def displayName(self):
        return self.tr('Consistent DTM (DTM ≤ DSM)', 'MDT consistente (MDT ≤ MDS)')

    def group(self):
        return self.tr('Relief', 'Relevo')

    def groupId(self):
        return 'relief'

    def tags(self):
        return 'GeoOne,DTM,DSM,DEM,MDT,MDS,MDE,terrain,surface,consistency,consistência,relief,relevo'.split(',')

    def icon(self):
        return QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images/contours.png'))

    txt_en = '''Creates a consistent DTM on the input DTM grid.
For each cell with valid DTM and DSM values, output = min(DTM, DSM).
If either value is NoData, the output is NoData.
The DSM is resampled/reprojected to the DTM grid when necessary.
This constraint does not reconstruct the true ground surface or correct differences in vertical reference.'''
    txt_pt = '''Cria um MDT consistente na grade do MDT de entrada.
Em cada célula com MDT e MDS válidos, saída = min(MDT, MDS).
Se algum valor for NoData, a saída será NoData.
O MDS é reamostrado/reprojetado para a grade do MDT quando necessário.
Essa restrição não reconstrói a superfície real do terreno nem corrige diferenças de referencial vertical.'''
    figure = 'images/tutorial/relief_consistent_dtm.jpg'

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

    DTM = 'DTM'
    DSM = 'DSM'
    RESAMPLING = 'RESAMPLING'
    OUTPUT = 'OUTPUT'
    OPEN = 'OPEN'

    def initAlgorithm(self, config=None):
        # INPUT
        self.addParameter(
            QgsProcessingParameterRasterLayer(
                self.DTM,
                self.tr('Input DTM', 'MDT de entrada')
            )
        )

        self.addParameter(
            QgsProcessingParameterRasterLayer(
                self.DSM,
                self.tr('Input DSM', 'MDS de entrada')
            )
        )

        interp = [self.tr('Nearest neighbor', 'Vizinho mais próximo'),
                  self.tr('Bilinear'),
                  self.tr('Bicubic', 'Bicúbica')]

        self.addParameter(
            QgsProcessingParameterEnum(
                self.RESAMPLING,
                self.tr('DSM resampling', 'Reamostragem do MDS'),
                options=interp,
                defaultValue=0
            )
        )

        # OUTPUT
        self.addParameter(
            QgsProcessingParameterFileDestination(
                self.OUTPUT,
                self.tr('Consistent DTM', 'MDT consistente'),
                fileFilter='GeoTIFF (*.tif)'
            )
        )

        self.addParameter(
            QgsProcessingParameterBoolean(
                self.OPEN,
                self.tr('Load raster', 'Carregar raster'),
                defaultValue=True
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        # inputs
        dtm_layer = self.parameterAsRasterLayer(parameters, self.DTM, context)
        dsm_layer = self.parameterAsRasterLayer(parameters, self.DSM, context)
        if dtm_layer is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.DTM))
        if dsm_layer is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.DSM))

        # output
        output = self.parameterAsFileOutput(parameters, self.OUTPUT, context)
        if not output:
            raise QgsProcessingException(self.tr('Invalid output path.', 'Caminho de saída inválido.'))
        dtm_path = dtm_layer.dataProvider().dataSourceUri()
        dsm_path = dsm_layer.dataProvider().dataSourceUri()
        if any(os.path.abspath(output) == os.path.abspath(path)
               for path in (dtm_path, dsm_path)):
            raise QgsProcessingException(self.tr(
                'The output must differ from both inputs.',
                'A saída deve ser diferente das duas entradas.'))

        choice = self.parameterAsEnum(parameters, self.RESAMPLING, context)
        if choice not in (0, 1, 2):
            raise QgsProcessingException(self.tr(
                'Invalid resampling method.', 'Método de reamostragem inválido.'))
        resampling = ('near', 'bilinear', 'cubic')[choice]
        load_output = self.parameterAsBool(parameters, self.OPEN, context)

        # MDT e MDS
        dtm = gdal.Open(dtm_path, gdal.GA_ReadOnly)
        dsm = gdal.Open(dsm_path, gdal.GA_ReadOnly)
        if dtm is None or dsm is None:
            raise QgsProcessingException(self.tr(
                'Could not open the input rasters.', 'Não foi possível abrir os rasters de entrada.'))
        if dtm.RasterCount < 1 or dsm.RasterCount < 1:
            raise QgsProcessingException(self.tr(
                'Both inputs must have at least one band.',
                'As entradas devem ter pelo menos uma banda.'))
        if any(gdal.DataTypeIsComplex(ds.GetRasterBand(1).DataType) for ds in (dtm, dsm)):
            raise QgsProcessingException(self.tr(
                'Complex raster bands are not supported.',
                'Bandas raster complexas não são aceitas.'))

        # Grade de referência: MDT
        gt = dtm.GetGeoTransform()
        dsm_gt = dsm.GetGeoTransform()
        if gt[2] != 0 or gt[4] != 0 or gt[1] <= 0 or gt[5] >= 0:
            raise QgsProcessingException(self.tr(
                'The DTM must have a north-up, non-rotated grid.',
                'O MDT deve ter uma grade orientada ao norte, sem rotação.'))
        projection = dtm.GetProjection()
        same_grid = (dtm.RasterXSize == dsm.RasterXSize and
                     dtm.RasterYSize == dsm.RasterYSize and
                     gt == dsm_gt and projection == dsm.GetProjection())
        if not same_grid and (not projection or not dsm.GetProjection()):
            raise QgsProcessingException(self.tr(
                'Both rasters need a CRS when their grids differ.',
                'Os dois rasters precisam de SRC quando as grades diferem.'))

        aligned = dsm
        if not same_grid:
            feedback.pushInfo(self.tr(
                'Aligning DSM to the DTM grid...', 'Alinhando o MDS à grade do MDT...'))
            bounds = (gt[0], gt[3] + dtm.RasterYSize * gt[5],
                      gt[0] + dtm.RasterXSize * gt[1], gt[3])
            aligned = gdal.Warp('', dsm, format='VRT',
                                dstSRS=projection, outputBounds=bounds,
                                width=dtm.RasterXSize, height=dtm.RasterYSize,
                                resampleAlg=resampling, dstNodata='nan',
                                outputType=gdal.GDT_Float64,
                                warpOptions=['INIT_DEST=NO_DATA'])
            if aligned is None:
                raise QgsProcessingException(self.tr(
                    'Could not align DSM to the DTM grid.',
                    'Não foi possível alinhar o MDS à grade do MDT.'))

        # MDT consistente (processamento por blocos)
        fd, temporary_path = tempfile.mkstemp(
            suffix='.tif', prefix='.consistent_dtm_',
            dir=os.path.dirname(os.path.abspath(output)))
        os.close(fd)
        os.unlink(temporary_path)
        result = None
        try:
            result = gdal.GetDriverByName('GTiff').Create(
                temporary_path, dtm.RasterXSize, dtm.RasterYSize, 1,
                gdal.GDT_Float64,
                options=['TILED=YES', 'COMPRESS=DEFLATE', 'PREDICTOR=3',
                         'BIGTIFF=IF_SAFER'])
            if result is None:
                raise QgsProcessingException(self.tr(
                    'Could not create output GeoTIFF.',
                    'Não foi possível criar o GeoTIFF de saída.'))
            result.SetGeoTransform(gt)
            result.SetProjection(projection)
            result_band = result.GetRasterBand(1)
            result_band.SetNoDataValue(float('nan'))

            dtm_band = dtm.GetRasterBand(1)
            dsm_band = aligned.GetRasterBand(1)
            dtm_mask = dtm_band.GetMaskBand()
            dsm_mask = dsm_band.GetMaskBand()
            corrected = valid = 0
            block = 512
            for y in range(0, dtm.RasterYSize, block):
                if feedback.isCanceled():
                    raise QgsProcessingException(self.tr('Canceled.', 'Cancelado.'))
                h = min(block, dtm.RasterYSize - y)
                for x in range(0, dtm.RasterXSize, block):
                    w = min(block, dtm.RasterXSize - x)
                    terrain = dtm_band.ReadAsArray(x, y, w, h).astype(np.float64)
                    surface = dsm_band.ReadAsArray(x, y, w, h).astype(np.float64)
                    ok = (dtm_mask.ReadAsArray(x, y, w, h) != 0) & (
                        dsm_mask.ReadAsArray(x, y, w, h) != 0)
                    ok &= np.isfinite(terrain) & np.isfinite(surface)
                    change = ok & (terrain > surface)
                    valid += int(np.count_nonzero(ok))
                    corrected += int(np.count_nonzero(change))
                    output_array = np.full((h, w), np.nan, dtype=np.float64)
                    output_array[ok] = np.minimum(terrain[ok], surface[ok])
                    result_band.WriteArray(output_array, x, y)
                feedback.setProgress(round(100 * (y + h) / dtm.RasterYSize))
            if feedback.isCanceled():
                raise QgsProcessingException(self.tr('Canceled.', 'Cancelado.'))
            if valid == 0:
                raise QgsProcessingException(self.tr(
                    'No cells have valid values in both rasters.',
                    'Nenhuma célula possui valores válidos nos dois rasters.'))

            result.FlushCache()
            result_band = None
            result = None
            aligned = None
            dtm = None
            dsm = None
            os.replace(temporary_path, output)
        finally:
            result = None
            aligned = None
            dtm = None
            dsm = None
            if os.path.exists(temporary_path):
                os.unlink(temporary_path)

        feedback.pushInfo(self.tr(
            'Valid cells: {}. Corrected cells: {}.',
            'Células válidas: {}. Células corrigidas: {}.').format(valid, corrected))
        self.CAMINHO = output
        self.CARREGAR = load_output
        return {self.OUTPUT: output}

    # Carregamento de arquivo de saída
    def postProcessAlgorithm(self, context, feedback):
        if self.CARREGAR:
            layer = QgsRasterLayer(self.CAMINHO, self.tr('Consistent DTM', 'MDT consistente'))
            if layer.isValid():
                QgsProject.instance().addMapLayer(layer)
        return {}
