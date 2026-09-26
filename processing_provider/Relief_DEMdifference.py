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
Minuend is the raster from which elevations are subtracted.
Subtrahend is the raster whose elevations are subtracted.
The selected reference grid determines the output extent, resolution and CRS.
The other raster is resampled to this grid, and cells without valid values in both models become NoData.
Optionally, multiply the result by -1.'''
    txt_pt = '''Esta ferramenta executa a diferença entre dois Modelos Digitais de Elevação (MDE).
Minuendo é o raster do qual as cotas são subtraídas.
Subtraendo é o raster cujas cotas são subtraídas.
A grade de referência define a extensão, resolução e SRC da saída.
O outro raster é reamostrado para essa grade, e células sem valores válidos nos dois modelos tornam-se NoData.
Opcionalmente, multiplique o resultado por -1.'''
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
    SUBTRAHEND = 'SUBTRAHEND'
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
                self.tr('Minuend', 'Minuendo')
            )
        )

        self.addParameter(
            QgsProcessingParameterRasterLayer(
                self.SUBTRAHEND,
                self.tr('Subtrahend', 'Subtraendo')
            )
        )

        ref = [self.tr('Minuend', 'Minuendo'),
               self.tr('Subtrahend', 'Subtraendo')]

        self.addParameter(
            QgsProcessingParameterEnum(
                self.REF,
                self.tr('Reference grid', 'Grade de Referência'),
                options=ref,
                defaultValue=0
            )
        )

        interp = [self.tr('Nearest neighbor', 'Vizinho mais próximo'),
                  self.tr('Bilinear'),
                  self.tr('Bicubic', 'Bicúbica')]

        self.addParameter(
            QgsProcessingParameterEnum(
                self.RESAMPLING,
                self.tr('Interpolation', 'Interpolação'),
                options=interp,
                defaultValue=0
            )
        )

        self.addParameter(
            QgsProcessingParameterBoolean(
                self.NEGATIVE,
                self.tr('Multiply the result by -1', 'Multiplicar o resultado por -1'),
                defaultValue=False
            )
        )

        # OUTPUT
        self.addParameter(
            QgsProcessingParameterFileDestination(
                self.OUTPUT,
                self.tr('Difference', 'Diferença'),
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
        a_layer = self.parameterAsRasterLayer(parameters, self.MINUEND, context)
        b_layer = self.parameterAsRasterLayer(parameters, self.SUBTRAHEND, context)
        if a_layer is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.MINUEND))
        if b_layer is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.SUBTRAHEND))
        # output
        output = self.parameterAsFileOutput(parameters, self.OUTPUT, context)
        if not output:
            raise QgsProcessingException(self.tr('Invalid output path.', 'Caminho de saída inválido.'))
        a_path = a_layer.dataProvider().dataSourceUri()
        b_path = b_layer.dataProvider().dataSourceUri()
        if any(os.path.abspath(output) == os.path.abspath(path)
               for path in (a_path, b_path)):
            raise QgsProcessingException(self.tr(
                'The output must differ from both inputs.',
                'A saída deve ser diferente das duas entradas.'))

        ref_choice = self.parameterAsEnum(parameters, self.REF, context)
        method = self.parameterAsEnum(parameters, self.RESAMPLING, context)
        if ref_choice not in (0, 1) or method not in (0, 1, 2):
            raise QgsProcessingException(self.tr(
                'Invalid processing option.', 'Opção de processamento inválida.'))
        resampling = ('near', 'bilinear', 'cubic')[method]
        sign = -1 if self.parameterAsBool(parameters, self.NEGATIVE, context) else 1
        load_output = self.parameterAsBool(parameters, self.OPEN, context)

        # Minuendo e subtraendo
        a = gdal.Open(a_path, gdal.GA_ReadOnly)
        b = gdal.Open(b_path, gdal.GA_ReadOnly)
        if a is None or b is None:
            raise QgsProcessingException(self.tr(
                'Could not open the input rasters.', 'Não foi possível abrir os rasters de entrada.'))
        if a.RasterCount < 1 or b.RasterCount < 1:
            raise QgsProcessingException(self.tr(
                'Both inputs must have at least one band.',
                'As entradas devem ter pelo menos uma banda.'))
        if any(gdal.DataTypeIsComplex(ds.GetRasterBand(1).DataType) for ds in (a, b)):
            raise QgsProcessingException(self.tr(
                'Complex raster bands are not supported.',
                'Bandas raster complexas não são aceitas.'))

        # Grade de referência
        reference, other = (a, b) if ref_choice == 0 else (b, a)
        gt = reference.GetGeoTransform()
        if gt[2] != 0 or gt[4] != 0 or gt[1] <= 0 or gt[5] >= 0:
            raise QgsProcessingException(self.tr(
                'The reference raster must have a north-up, non-rotated grid.',
                'O raster de referência deve ter grade orientada ao norte, sem rotação.'))
        projection = reference.GetProjection()
        same_grid = (reference.RasterXSize == other.RasterXSize and
                     reference.RasterYSize == other.RasterYSize and
                     gt == other.GetGeoTransform() and projection == other.GetProjection())
        if not same_grid and (not projection or not other.GetProjection()):
            raise QgsProcessingException(self.tr(
                'Both rasters need a CRS when their grids differ.',
                'Os dois rasters precisam de SRC quando as grades diferem.'))

        aligned = other
        if not same_grid:
            feedback.pushInfo(self.tr('Aligning DEMs...', 'Alinhando os MDEs...'))
            bounds = (gt[0], gt[3] + reference.RasterYSize * gt[5],
                      gt[0] + reference.RasterXSize * gt[1], gt[3])
            aligned = gdal.Warp('', other, format='VRT', dstSRS=projection,
                                outputBounds=bounds, width=reference.RasterXSize,
                                height=reference.RasterYSize, resampleAlg=resampling,
                                dstNodata='nan', outputType=gdal.GDT_Float64,
                                warpOptions=['INIT_DEST=NO_DATA'])
            if aligned is None:
                raise QgsProcessingException(self.tr(
                    'Could not align the DEMs.', 'Não foi possível alinhar os MDEs.'))

        # Diferença (processamento por blocos)
        fd, temporary_path = tempfile.mkstemp(
            suffix='.tif', prefix='.dem_difference_',
            dir=os.path.dirname(os.path.abspath(output)))
        os.close(fd)
        os.unlink(temporary_path)
        result = None
        try:
            result = gdal.GetDriverByName('GTiff').Create(
                temporary_path, reference.RasterXSize, reference.RasterYSize, 1,
                gdal.GDT_Float64, options=['TILED=YES', 'COMPRESS=DEFLATE',
                                          'PREDICTOR=3', 'BIGTIFF=IF_SAFER'])
            if result is None:
                raise QgsProcessingException(self.tr(
                    'Could not create output GeoTIFF.',
                    'Não foi possível criar o GeoTIFF de saída.'))
            result.SetGeoTransform(gt)
            result.SetProjection(projection)
            band_ref = reference.GetRasterBand(1)
            band_other = aligned.GetRasterBand(1)
            mask_ref = band_ref.GetMaskBand()
            mask_other = band_other.GetMaskBand()
            result_band = result.GetRasterBand(1)
            result_band.SetNoDataValue(float('nan'))
            valid = 0
            block = 512
            for y in range(0, reference.RasterYSize, block):
                if feedback.isCanceled():
                    raise QgsProcessingException(self.tr('Canceled.', 'Cancelado.'))
                h = min(block, reference.RasterYSize - y)
                for x in range(0, reference.RasterXSize, block):
                    w = min(block, reference.RasterXSize - x)
                    first = band_ref.ReadAsArray(x, y, w, h).astype(np.float64)
                    second = band_other.ReadAsArray(x, y, w, h).astype(np.float64)
                    ok = (mask_ref.ReadAsArray(x, y, w, h) != 0) & (
                        mask_other.ReadAsArray(x, y, w, h) != 0)
                    ok &= np.isfinite(first) & np.isfinite(second)
                    valid += int(np.count_nonzero(ok))
                    values = np.full((h, w), np.nan, dtype=np.float64)
                    if ref_choice == 0:
                        values[ok] = sign * (first[ok] - second[ok])
                    else:
                        values[ok] = sign * (second[ok] - first[ok])
                    result_band.WriteArray(values, x, y)
                feedback.setProgress(round(100 * (y + h) / reference.RasterYSize))
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
            a = b = None
            os.replace(temporary_path, output)
        finally:
            result = None
            aligned = None
            a = b = None
            if os.path.exists(temporary_path):
                os.unlink(temporary_path)

        feedback.pushInfo(self.tr('Valid cells: {}.', 'Células válidas: {}.').format(valid))
        self.CAMINHO = output
        self.CARREGAR = load_output
        return {self.OUTPUT: output}

    # Carregamento de arquivo de saída
    def postProcessAlgorithm(self, context, feedback):
        if self.CARREGAR:
            layer = QgsRasterLayer(self.CAMINHO, self.tr('Difference', 'Diferença'))
            if layer.isValid():
                QgsProject.instance().addMapLayer(layer)
        return {}
