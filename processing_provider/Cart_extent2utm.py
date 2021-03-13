# -*- coding: utf-8 -*-

"""
Cart_extent2utm.py
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
__date__ = '2019-12-29'
__copyright__ = '(C) 2019, Leandro França'

from PyQt5.QtCore import QCoreApplication, QVariant
from qgis.core import *
from lftools.geocapt.imgs import Imgs
from lftools.geocapt.cartography import *
import os
from qgis.PyQt.QtGui import QIcon

class Extent2UTMGrid(QgsProcessingAlgorithm):

    EXTENT = 'EXTENT'
    SCALE = 'SCALE'
    FRAME = 'FRAME'
    CRS = 'CRS'
    CHART_SIZE = 'CHART_SIZE'
    MC = 'MC' # Meridian Convergence
    MD = 'MD' # Magnetic Declination
    ZONE_HEMISF = 'ZONE_HEMISF'

    LOC = QgsApplication.locale()

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
        return Extent2UTMGrid()

    def name(self):
        return 'extent2utmgrid'

    def displayName(self):

        return self.tr('Extent to UTM Grids', 'Extensão para Molduras UTM')

    def group(self):

        return self.tr('Cartography', 'Cartografia')

    def groupId(self):

        return 'cartography'

    def tags(self):
        return self.tr('name,extent,extension,frame,utm,grid,system,map,inom,mi,sistemático,índice,nomenclatura,grade,mapeamento,moldura').split(',')

    def icon(self):
        return QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images/cart_frames.png'))

    figure = 'images/tutorial/grid_ext_utm.jpg'
    txt_en = 'This algorithm returns the polygons correspondent to the <b>frames</b> related to a scale of the Brazilian Mapping System from a specific <b>extent</b> definied by the user.'
    txt_pt = 'Este algoritmo retorna os polígonos correspondentes às molduras relacionadas a uma escala do Mapeamento Sistemático Brasileiro para uma extensão específica definida pelo usuário.'

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

    def initAlgorithm(self, config=None):

        # 'INPUTS'
        self.addParameter(
            QgsProcessingParameterExtent(
                self.EXTENT,
                self.tr('Extent', 'Extensão')
            )
        )

        scales = [self.tr('1:1,000,000','1:1.000.000'),
                  self.tr('1:500,000','1:500.000'),
                  self.tr('1:250,000','1:250.000'),
				  self.tr('1:100,000','1:100.000'),
				  self.tr('1:50,000','1:50.000'),
				  self.tr('1:25,000','1:25.000'),
				  self.tr('1:10,000','1:10.000'),
				  self.tr('1:5,000','1:5.000'),
				  self.tr('1:2,000','1:2.000'),
				  self.tr('1:1,000','1:1.000')
               ]

        self.addParameter(
            QgsProcessingParameterEnum(
                self.SCALE,
                self.tr('Scale', 'Escala'),
				options = scales,
                defaultValue= 0
            )
        )

        self.addParameter(
            QgsProcessingParameterCrs(
                self.CRS,
                self.tr('Grid CRS', 'SRC'),
                'ProjectCrs'))

        self.addParameter(
            QgsProcessingParameterBoolean(
                self.CHART_SIZE,
                self.tr('Calculate Chart Size (Height and Width)', 'Calcular Altura e Largura da Carta'),
                defaultValue= False
            )
        )

        self.addParameter(
            QgsProcessingParameterBoolean(
                self.MC,
                self.tr('Calculate Meridian Convergence (MC)', 'Calcular Convergência Meridiana (CM)'),
                defaultValue= False
            )
        )

        self.addParameter(
            QgsProcessingParameterBoolean(
                self.MD,
                self.tr('Calculate Magnetic Declination (MD)', 'Calcular Declinação Magnética (DM)'),
                defaultValue= False
            )
        )

        self.addParameter(
            QgsProcessingParameterBoolean(
                self.ZONE_HEMISF,
                self.tr('Calculate Zone and Hemisphere', 'Calcular Fuso e Hemisfério'),
                defaultValue= False
            )
        )


        # 'OUTPUT'
        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.FRAME,
                self.tr('UTM Grids', 'Camada de Molduras')
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

        escala = self.parameterAsEnum(
            parameters,
            self.SCALE,
            context
        )
        # Escala
        escalas = [1e6, 500e3, 250e3, 100e3, 50e3, 25e3, 10e3, 5e3, 2e3, 1e3]
        escala = escalas[escala]

        crs = self.parameterAsCrs(
            parameters,
            self.CRS,
            context
        )

        # Checking for geographic coordinate reference system
        if not crs.isGeographic():
            crsGeo = QgsCoordinateReferenceSystem(crs.geographicCrsAuthId())
            coordinateTransformer = QgsCoordinateTransform()
            coordinateTransformer.setDestinationCrs(crs)
            coordinateTransformer.setSourceCrs(crsGeo)


        tam_carta = self.parameterAsBool(
        parameters,
        self.CHART_SIZE,
        context
        )

        mer_conv = self.parameterAsBool(
        parameters,
        self.MC,
        context
        )

        mag_decl = self.parameterAsBool(
        parameters,
        self.MD,
        context
        )

        zone_hemisf = self.parameterAsBool(
        parameters,
        self.ZONE_HEMISF,
        context
        )

        # Output Definition
        Fields = QgsFields()
        Fields.append(QgsField('inom', QVariant.String))
        Fields.append(QgsField('mi', QVariant.String))
        Fields.append(QgsField(self.tr('scale', 'escala'), QVariant.Int))
        Fields.append(QgsField(self.tr('chart_name', 'nome'), QVariant.String))
        if tam_carta:
            Fields.append(QgsField(self.tr('height', 'altura'), QVariant.Double))
            Fields.append(QgsField(self.tr('width', 'largura'), QVariant.Double))
        if mer_conv:
            Fields.append(QgsField(self.tr('MC', 'CM'), QVariant.Double))
        if mag_decl:
            Fields.append(QgsField(self.tr('MD', 'DM'), QVariant.Double))
            Fields.append(QgsField(self.tr('VAR_MD', 'var_DM'), QVariant.Double))
            Fields.append(QgsField(self.tr('Epoch', 'Época'), QVariant.Date))
        if zone_hemisf:
            Fields.append(QgsField(self.tr('zone_hemisphere', 'fuso_hemisfério'), QVariant.String))

        GeomType = QgsWkbTypes.Polygon

        (sink2, dest2_id) = self.parameterAsSink(
            parameters,
            self.FRAME,
            context,
            Fields,
            GeomType,
            crs
        )

        deltas = array([[6.0, 3.0, 1.5, 0.5, 0.25, 0.125, 0.125/2, 0.125/2/2, 0.125/2/2/3, 0.125/2/2/3/2],
                    [4.0, 2.0, 1.0, 0.5, 0.25, 0.125, 0.125/3, 0.125/3/2, 0.125/3/2/2, 0.125/3/2/2/2]])

        d_lon = deltas[:, escalas.index(escala)][0]
        d_lat = deltas[:, escalas.index(escala)][1]

        LON = arange(lon_min + 1e-10, lon_max + 1e-10 + d_lon, d_lon)
        LAT = arange(lat_min + 1e-10, lat_max+ 1e-10 + d_lat, d_lat)

        Percent = 100.0/(len(LON)*len(LAT))
        current = 0
        for lon in LON:
            for lat in LAT:
                if lon>=0:
                    lon0 = modf(lon/d_lon)[1]*d_lon
                else:
                    lon0 = modf(lon/d_lon)[1]*d_lon - d_lon
                if lat >=0:
                    lat0 = modf(lat/d_lat)[1]*d_lat
                else:
                    lat0 = modf(lat/d_lat)[1]*d_lat - d_lat

                coord = [[QgsPointXY(lon0, lat0),
                      QgsPointXY(lon0, lat0+d_lat),
                      QgsPointXY(lon0+d_lon, lat0+d_lat),
                      QgsPointXY(lon0+d_lon, lat0),
                      QgsPointXY(lon0, lat0)]]

                feat = QgsFeature(Fields)
                geom = QgsGeometry.fromPolygonXY(coord)
                centroide = geom.centroid().asPoint()
                inom = map_sistem(lon, lat, escala)
                # INOM para MI
                dicionario = inom2mi
                # Indice de Nomenclatura
                inom_list = inom.split('-')
                inom100k = ''
                resto = ''
                att = [inom, None, escala]
                feat['inom'] = inom
                feat[self.tr('scale', 'escala')] = escala
                if len(inom_list) >= 5:
                    for k in range(5):
                        inom100k += inom_list[k]+'-'
                    if len(inom_list) > 5:
                        for k in range(5,len(inom_list)):
                            resto += inom_list[k]+'-'
                        if inom100k[:-1] in dicionario:
                            feat['mi'] = dicionario[inom100k[:-1]]+'-'+resto[:-1]
                    else:
                        if inom100k[:-1] in dicionario:
                            feat['mi'] = dicionario[inom100k[:-1]]

                if tam_carta:
                    zone, hemisf = FusoHemisf(lon, lat)
                    feat[self.tr('height', 'altura')] = float(ChartSize(geom, zone, hemisf, escala)[0])
                    feat[self.tr('width', 'largura')] = float(ChartSize(geom, zone, hemisf, escala)[1])

                if mer_conv:
                    feat[self.tr('MC', 'CM')] = float(MeridianConvergence(centroide.x(), centroide.y(), crs))

                if zone_hemisf:
                    zone, hemisf = FusoHemisf(lon, lat)
                    feat[self.tr('zone_hemisphere', 'fuso_hemisfério')] = str(zone)+hemisf

                # Coordinate Transformations (if needed)
                geom = geom if crs.isGeographic() else reprojectPoints(geom, coordinateTransformer)
                feat.setGeometry(geom)
                sink2.addFeature(feat, QgsFeatureSink.FastInsert)
                current += 1
                feedback.setProgress(int(current * Percent))

        if sink2 is None:
            raise QgsProcessingException(self.invalidSinkError(parameters, self.FRAME))

        feedback.pushInfo(self.tr('Operation completed successfully!', 'Operação finalizada com sucesso!'))
        feedback.pushInfo(self.tr('Leandro Franca - Cartographic Engineer', 'Leandro França - Eng Cart'))

        return {self.FRAME: dest2_id}
