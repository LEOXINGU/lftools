# -*- coding: utf-8 -*-

"""
Cart_coord2utm.py
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
__date__ = '2019-10-06'
__copyright__ = '(C) 2019, Leandro França'

from PyQt5.QtCore import QCoreApplication, QVariant
from qgis.core import *
from lftools.geocapt.imgs import Imgs
from lftools.geocapt.cartography import *
import os
from qgis.PyQt.QtGui import QIcon

class Coord2UTMGrid(QgsProcessingAlgorithm):
    POINT = 'POINT'
    SCALE = 'SCALE'
    FRAME = 'FRAME'
    CRS = 'CRS'
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
        return Coord2UTMGrid()

    def name(self):
        return 'coord2utmgrid'

    def displayName(self):

        return self.tr('Coordinates to UTM grid', 'Coordenadas para moldura UTM')

    def group(self):

        return self.tr('Cartography', 'Cartografia')

    def groupId(self):

        return 'cartography'

    def tags(self):
        return self.tr('name,coordinates,frame,utm,grid,system,map,inom,mi,sistemático,índice,nomenclatura,grade,mapeamento,moldura').split(',')

    def icon(self):
        return QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images/cart_frame.png'))

    figure = 'images/tutorial/grid_coord_utm.jpg'
    txt_en = 'This algorithm returns the frame related to a scale of the Brazilian Mapping System. The generated frame, which is a polygon, is calculated from a Point defined by the user.'
    txt_pt = 'Este algoritmo retorna o polígono correspondente à <b>moldura</b> relativa a uma escala do <b>Mapeamento Sistemático Brasileiro</b>. Esta moldura é calculada a partir das coordenadas de um <b>Ponto</b> definido pelo usuário.'

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
            QgsProcessingParameterPoint(
                self.POINT,
                self.tr('Point', 'Ponto')
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
                self.tr('Grid CRS', 'SRC da Moldura'),
                'ProjectCrs'))

        # 'OUTPUT'
        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.FRAME,
                self.tr('UTM Grid', 'Moldura')
            )
        )

    def processAlgorithm(self, parameters, context, feedback):

        ponto = self.parameterAsPoint(
            parameters,
            self.POINT,
            context
        )
        ProjectCRS = QgsProject.instance().crs()
        if not ProjectCRS.isGeographic():
            crsGeo = QgsCoordinateReferenceSystem(ProjectCRS.geographicCrsAuthId())
            coordinateTransformer = QgsCoordinateTransform()
            coordinateTransformer.setDestinationCrs(crsGeo)
            coordinateTransformer.setSourceCrs(ProjectCRS)
            PontoGeo = reprojectPoints(QgsGeometry(QgsPoint(ponto.x(), ponto.y())), coordinateTransformer)
            ponto = PontoGeo.asPoint()
            lon, lat = ponto.x(), ponto.y()
        else:
            lon, lat = ponto.x(), ponto.y()

        lon, lat = lon+1e-10, lat+1e-10 # avoid grid intersections

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

        # Input Validation
        if lat <-90 or lat >90:
            raise QgsProcessingException(self.tr('Invalid Latitude', 'Latitude Inválida'))
        if lat <-180 or lat >180:
            raise QgsProcessingException(self.tr('Invalid Longitude', 'Longitude Inválida'))

        # Output Definition
        Fields = QgsFields()
        Fields.append(QgsField('inom', QVariant.String))
        Fields.append(QgsField('mi', QVariant.String))
        Fields.append(QgsField(self.tr('scale', 'escala'), QVariant.Int))
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

        feat = QgsFeature()
        geom = QgsGeometry.fromPolygonXY(coord)
        # Coordinate Transformations (if needed)
        geom = geom if crs.isGeographic() else reprojectPoints(geom, coordinateTransformer)
        inom = map_sistem(lon, lat, escala)
        feedback.pushInfo(self.tr('Nomenclature Index', 'Índice de Nomenclatura') + ': {}'.format(inom))

        # INOM para MI
        dicionario = inom2mi

        # Indice de Nomenclatura
        inom_list = inom.split('-')
        inom100k = ''
        resto = ''
        att = [inom, None, escala]
        if len(inom_list) >= 5:
            for k in range(5):
                inom100k += inom_list[k]+'-'
            if len(inom_list) > 5:
                for k in range(5,len(inom_list)):
                    resto += inom_list[k]+'-'
                if inom100k[:-1] in dicionario:
                    att[1] = dicionario[inom100k[:-1]]+'-'+resto[:-1]
                    feedback.pushInfo(self.tr('Map Index','Mapa Índice') + ': {}'.format(att[1]))
            else:
                if inom100k[:-1] in dicionario:
                    att[1] = dicionario[inom100k[:-1]]
                    feedback.pushInfo(self.tr('Map Index','Mapa Índice') + ': {}'.format(att[1]))

        feat.setGeometry(geom)
        feat.setAttributes(att)
        sink2.addFeature(feat, QgsFeatureSink.FastInsert)
        if sink2 is None:
            raise QgsProcessingException(self.invalidSinkError(parameters, self.FRAME))

        feedback.pushInfo(self.tr('Operation completed successfully!', 'Operação finalizada com sucesso!'))
        feedback.pushInfo(self.tr('Leandro Franca - Cartographic Engineer', 'Leandro França - Eng Cart'))

        return {self.FRAME: dest2_id}
