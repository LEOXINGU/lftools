# -*- coding: utf-8 -*-

"""
Survey_LocalTangentPlane.py
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
__date__ = '2019-10-28'
__copyright__ = '(C) 2019, Leandro França'

from PyQt5.QtCore import *
from qgis.core import *
import processing
from numpy import sin, cos, sqrt, matrix, radians, arctan, pi, floor
from pyproj.crs import CRS
from lftools.geocapt.imgs import Imgs
from lftools.geocapt.topogeo import geod2geoc, geoc2geod, geoc2enu, enu2geoc, dd2dms, dms2dd
import os
from qgis.PyQt.QtGui import QIcon


class LocalTangentPlane(QgsProcessingAlgorithm):

    INPUT = 'INPUT'
    TABLE = 'TABLE'
    TYPE = 'TYPE'
    COORD1 = 'COORD1'
    COORD2 = 'COORD2'
    COORD3 = 'COORD3'
    GRS = 'GRS'
    LON_0 = 'LON_0'
    LAT_0 = 'LAT_0'
    H_0 = 'H_0'
    OUTPUT = 'OUTPUT'

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
        return LocalTangentPlane()

    def name(self):
        return 'localtangentplane'

    def displayName(self):
        return self.tr('Local Geodetic System transform', 'Transformação para SGL')

    def group(self):
        return self.tr('Survey', 'Agrimensura')

    def groupId(self):
        return 'survey'

    def tags(self):
        return self.tr('survey,agrimensura,LGS,SGL,tangent,transform,geocentric,topocentric,ECEF,geodetic,geodesic,brazil').split(',')

    def icon(self):
        return QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images/total_station.png'))

    txt_en = '''
This algorithm transforms coordinates between the following reference systems:
- geodetic <b>(λ, ϕ, h)</b>;
- geocentric or ECEF <b>(X, Y, Z)</b>; and
- topocentric in a local tangent plane <b>(E, N, U)</b>.
Default values for origin coordinates can be applied to Recife / Brazil.'''
    txt_pt = '''Este algoritmo transforma coordenadas entre os seguintes sistemas de referência:
- Geodésico <b>(λ, ϕ, h)</b>
- Geocêntrico ou ECEF <b>(X, Y, Z)</b>;
- Topocêntrico <b>(E, N, U)</b>.
Default: coordenadas de origem para Recife-PE, Brasil.'''
    figure = 'images/tutorial/survey_LTP.jpg'

    def shortHelpString(self):
        social_BW = Imgs().social_BW
        nota_en = '''Note: Example data obtained from Mendonça et al. (2010).
Know more:'''
        nota_pt = '''Nota: Dados de exemplo obtidos de Mendonça et al. (2010).
Saiba mais:'''
        footer = '''<div align="center">
                      <img src="'''+ os.path.join(os.path.dirname(os.path.dirname(__file__)), self.figure) +'''">
                      </div>
                      <div align="right">
                      <div>''' + self.tr(nota_en, nota_pt) + '''
                      </div>
                      <p align="right">
                      <b><a href="https://geoone.com.br/sistema-geodesico-local/" target="_blank">'''+self.tr('Local Geodetic System (LGS)', 'Sistema Geodésico Local (SGL)') + '''</b>
                                    ''' +'</a><br><b>'+ self.tr('Author: Leandro Franca', 'Autor: Leandro França')+'''</b>
                      </p>'''+ social_BW + '''</div>
                    </div>'''
        return self.tr(self.txt_en, self.txt_pt) + footer

    def initAlgorithm(self, config=None):
        # INPUT
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.TABLE,
                self.tr('Table of coordinates', 'Tabela de coordenadas'),
                [QgsProcessing.TypeVector]
            )
        )

        types = [ self.tr('lon, lat, h'),
                      self.tr('X, Y, Z'),
                      self.tr('E, N, U')
               ]

        self.addParameter(
            QgsProcessingParameterEnum(
                self.TYPE,
                self.tr('Input Coordinates type', 'Tipo de Coordenadas de Entrada'),
				options = types,
                defaultValue= 0
            )
        )

        self.addParameter(
            QgsProcessingParameterField(
                self.COORD1,
                self.tr('Lon, X or E field', 'Campo Lon, X ou E'),
                parentLayerParameterName=self.TABLE,
                type=QgsProcessingParameterField.Numeric
            )
        )

        self.addParameter(
            QgsProcessingParameterField(
                self.COORD2,
                self.tr('Lat, Y or N field', 'Campo Lat, Y ou N'),
                parentLayerParameterName=self.TABLE,
                type=QgsProcessingParameterField.Numeric
            )
        )

        self.addParameter(
            QgsProcessingParameterField(
                self.COORD3,
                self.tr('h, Z or U field', 'Campo h, Z ou U'),
                parentLayerParameterName=self.TABLE,
                type=QgsProcessingParameterField.Numeric
            )
        )

        self.addParameter(
            QgsProcessingParameterCrs(
                self.GRS,
                self.tr('Ellipsoid parameters', 'Parâmetros do Elipsoide'),
                QgsCoordinateReferenceSystem('EPSG:4674')
            )
        )

        self.addParameter(
            QgsProcessingParameterString(
                self.LON_0,
                self.tr('Origin Longitude (λ)', 'Longitude (λ) da Origem'),
                defaultValue = '''-34°57'05.45910"'''
            )
        )

        self.addParameter(
            QgsProcessingParameterString(
                self.LAT_0,
                self.tr('Origin Latitude (ϕ)', 'Latitude (ϕ) da Origem'),
                defaultValue = '''-8°03'03.46970"'''
            )
        )

        self.addParameter(
            QgsProcessingParameterNumber(
                self.H_0,
                self.tr('Origin Elipsoid Height (h)', 'Altitude (h) da Origem'),
                type=1, #Double = 1 and Integer = 0
                defaultValue = 4.217
            )
        )

        # OUTPUT
        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT,
                self.tr('Transformed Coordinates', 'Coordenadas Transformadas')
            )
        )

    def processAlgorithm(self, parameters, context, feedback):

        # Tabela de coordenadas
        table = self.parameterAsSource(
            parameters,
            self.TABLE,
            context
        )
        if table is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.TABLE))

        # Tipo de Coordenadas
        tipo = self.parameterAsEnum(
            parameters,
            self.TYPE,
            context
        )
        if tipo < 0 or tipo >2:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.TYPE))

        # Coordenadas
        coord1 = self.parameterAsFields(
            parameters,
            self.COORD1,
            context
        )
        coord2 = self.parameterAsFields(
            parameters,
            self.COORD2,
            context
        )
        coord3 = self.parameterAsFields(
            parameters,
            self.COORD3,
            context
        )

        # Sistema Geodésico de Referência
        GRS = self.parameterAsCrs(
            parameters,
            self.GRS,
            context
        )

        # Coordenadas da Origem (lon, lat, h)
        lon0 = self.parameterAsString(
            parameters,
            self.LON_0,
            context
        )
        lon0 = dms2dd(lon0)
        if lon0 < -180 or lon0 >180:
            raise QgsProcessingException('Invalid Longitude')

        lat0 = self.parameterAsString(
            parameters,
            self.LAT_0,
            context
        )
        lat0 = dms2dd(lat0)
        if lat0 < -90 or lat0 >90:
            raise QgsProcessingException('Invalid Latitude')

        h0 = self.parameterAsDouble(
            parameters,
            self.H_0,
            context
        )
        if h0 < -1e3 or h0 >1e4:
            raise QgsProcessingException('Invalid Height')


        # OUTPUT
        # Camada de Saída
        GeomType = QgsWkbTypes.Point
        Fields = QgsFields()
        itens  = {
                     'lon' : QVariant.Double,
                     'lon_dms' : QVariant.String,
                     'lat':  QVariant.Double,
                     'lat_dms':  QVariant.String,
                     'h': QVariant.Double,
                     'X':  QVariant.Double,
                     'Y': QVariant.Double,
                     'Z': QVariant.Double,
                     'E': QVariant.Double,
                     'N': QVariant.Double,
                     'U': QVariant.Double
                     }

        field_list = []
        for field in table.fields():
            if field.name() not in itens:
                Fields.append(field)
                field_list += [field.name()]

        for item in itens:
            Fields.append(QgsField(item, itens[item]))

        (sink, dest_id) = self.parameterAsSink(
            parameters,
            self.OUTPUT,
            context,
            Fields,
            GeomType,
            GRS
        )
        if sink is None:
            raise QgsProcessingException(self.invalidSinkError(parameters, self.OUTPUT))

        # Parâmetros a e f do elipsoide
        EPSG = int(GRS.authid().split(':')[-1]) # pegando o EPGS do SRC do QGIS
        proj_crs = CRS.from_epsg(EPSG) # transformando para SRC do pyproj
        a=proj_crs.ellipsoid.semi_major_metre
        f_inv = proj_crs.ellipsoid.inverse_flattening
        f=1/f_inv
        feedback.pushInfo((self.tr('Semi major axis: {}', 'Semi-eixo maior: {}')).format(str(a)))
        feedback.pushInfo((self.tr('Inverse flattening: {}', 'Achatamento (inverso): {}')).format(str(f_inv)))

        Xo, Yo, Zo = geod2geoc(lon0, lat0, h0, a, f)

        # Field index
        coord1_id = table.fields().indexFromName(coord1[0])
        coord2_id = table.fields().indexFromName(coord2[0])
        coord3_id = table.fields().indexFromName(coord3[0])

        # Gerar output
        total = 100.0 / table.featureCount() if table.featureCount() else 0
        for current, feature in enumerate(table.getFeatures()):
            att = feature.attributes()
            coord1 = att[coord1_id]
            coord2 = att[coord2_id]
            coord3 = att[coord3_id]
            if tipo == 0: #(lon,lat,h)
                lon, lat, h = coord1, coord2, coord3
                X, Y, Z = geod2geoc(lon, lat, h, a, f)
                E, N, U = geoc2enu(X, Y, Z, lon0, lat0, Xo, Yo, Zo)
            elif tipo == 1: #(X,Y,Z)
                X, Y, Z = coord1, coord2, coord3
                lon, lat, h = geoc2geod(X, Y, Z, a, f)
                E, N, U = geoc2enu(X, Y, Z, lon0, lat0, Xo, Yo, Zo)
            elif tipo == 2: #(E,N,U)
                E, N, U = coord1, coord2, coord3
                X, Y, Z = enu2geoc(E, N, U, lon0, lat0, Xo, Yo, Zo)
                lon, lat, h = geoc2geod(X, Y, Z, a, f)

            feat = QgsFeature(Fields)
            itens  = {
                         'lon' : float(lon),
                         'lon_dms' : dd2dms(float(lon),5),
                         'lat':  float(lat),
                         'lat_dms':  dd2dms(float(lat),5),
                         'h': float(h),
                         'X':  float(X),
                         'Y': float(Y),
                         'Z': float(Z),
                         'E': float(E),
                         'N': float(N),
                         'U': float(U)
                         }

            for item in itens:
                feat[item] = itens[item]

            for item in field_list: # atributos antigos
                feat[item] = feature[item]

            geom = QgsGeometry.fromPointXY(QgsPointXY(lon, lat))
            feat.setGeometry(geom)
            sink.addFeature(feat, QgsFeatureSink.FastInsert)
            if feedback.isCanceled():
                break
            feedback.setProgress(int(current * total))

        feedback.pushInfo(self.tr('Operation completed successfully!', 'Operação finalizada com sucesso!'))
        feedback.pushInfo(self.tr('Leandro Franca - Cartographic Engineer','Leandro França - Eng Cart'))
        return {self.OUTPUT: dest_id}
