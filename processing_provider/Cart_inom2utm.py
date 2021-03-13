# -*- coding: utf-8 -*-

"""
Cart_inom2utm.py
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
from numpy import array
from lftools.geocapt.imgs import Imgs
from lftools.geocapt.cartography import reprojectPoints, mi2inom
import os
from qgis.PyQt.QtGui import QIcon

class Inom2utmGrid(QgsProcessingAlgorithm):

    NAME = 'NAME'
    TYPE = 'TYPE'
    FRAME = 'FRAME'
    CRS = 'CRS'
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

        return Inom2utmGrid()

    def name(self):

        return 'inom2utmgrid'

    def displayName(self):

        return self.tr('Name to UTM Grid', 'Nome para Moldura UTM')

    def group(self):

        return self.tr('Cartography', 'Cartografia')

    def groupId(self):

        return 'cartography'

    def tags(self):
        return self.tr('name,frame,utm,grid,system,map,inom,mi,sistemático,índice,nomenclatura,grade,mapeamento,moldura').split(',')

    def icon(self):
        return QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images/cart_frame.png'))

    figure = 'images/tutorial/grid_inom_utm.jpg'
    txt_en = 'This algorithm returns the polygon correspondent to the frame related to a scale of the Brazilian Mapping System based on the Map Index (MI). Example: MI = 1214-1'
    txt_pt = 'Este algoritmo retorna o polígono correspondente à <b>moldura</b> relativa a uma escala do <b>Mapeamento Sistemático Brasileiro</b>. Esta moldura é calculada a partir do Índice de Nomenclatura <b>INOM</b> ou Mapa Índice <b>MI</b> válido, que deve ser dado pelo usuário.'

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
            QgsProcessingParameterString(
                self.NAME,
                self.tr('Name', 'Nome')
            )
        )

        tipos = [self.tr('MI'),
                  self.tr('INOM')]

        self.addParameter(
            QgsProcessingParameterEnum(
                self.TYPE,
                self.tr('Type', 'Tipo'),
				options = tipos,
                defaultValue= 0
            )
        )

        self.addParameter(
            QgsProcessingParameterCrs(
                self.CRS,
                self.tr('Grid CRS', 'SRC da Moldura'),
                'ProjectCrs'
			)
		)

        # 'OUTPUT'
        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.FRAME,
                self.tr('UTM Grid', 'Moldura')
            )
        )

    def processAlgorithm(self, parameters, context, feedback):

        nome = self.parameterAsString(
            parameters,
            self.NAME,
            context
        )

        tipo = self.parameterAsEnum(
            parameters,
            self.TYPE,
            context
        )

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

        # Output Definition
        Fields = QgsFields()
        Fields.append(QgsField('inom', QVariant.String))
        Fields.append(QgsField('mi', QVariant.String))
        Fields.append(QgsField(self.tr('scale', 'escala'), QVariant.Int))
        GeomType = QgsWkbTypes.Polygon

        (sink, dest_id) = self.parameterAsSink(
            parameters,
            self.FRAME,
            context,
            Fields,
            GeomType,
            crs
        )

        nome = nome.upper()
        lista = nome.split('-')

        # Converter MI para INOM
        dicionario = mi2inom

        if tipo == 0:

            if lista[0] not in dicionario:
                raise QgsProcessingException(self.tr('error: MI does not exist!','erro: MI não existe!'))

            if len(lista)>1:
                lista = dicionario[lista[0]].split('-') + lista[1:]
            else:
                lista = dicionario[lista[0]].split('-')

        if len(lista)<2:
            raise QgsProcessingException(self.tr('error: Incomplete name!','erro: nome incorreto!'))

        # Hemisphere
        if lista[0][0] == 'S':
            sinal = -1
        elif lista[0][0] == 'N':
            sinal = 1
        else:
            raise QgsProcessingException(self.tr('error: wrong hemisphere!','erro: hemisfério incorreto!'))

        # Latitude inicial
        if sinal == -1:
            lat = sinal*4*(ord(lista[0][1])-64)
        else:
            lat = sinal*4*(ord(lista[0][1])-64) - 4

        # Longitude inicial
        if int(lista[1])<1 or int(lista[1])>60:
            raise QgsProcessingException(self.tr('error: wrong zone!','erro: fuso incorreto!'))
        lon = 6*int(lista[1]) - 186

        if len(lista) ==2:
            d_lon = 6.0
            d_lat = 4.0
            coord = [[QgsPointXY(lon, lat), QgsPointXY(lon, lat+d_lat), QgsPointXY(lon+d_lon, lat+d_lat), QgsPointXY(lon+d_lon, lat), QgsPointXY(lon, lat)]]
            escala = 1e6
        else:
            dic_delta  =  {'500k': {'Y':[0, 0], 'V':[0, 2.0], 'X':[3.0, 2.0], 'Z':[3.0, 0]},
                                '250k': {'C':[0, 0], 'A':[0, 1.0], 'B':[1.5, 1.0], 'D':[1.5, 0]},
                                '100k': {'IV':[0, 0], 'I':[0, 0.5], 'II':[0.5, 0.5], 'V':[0.5, 0], 'III':[1.0, 0.5], 'VI': [1.0, 0]},
                                '50k': {'3':[0, 0], '1':[0, 0.25], '2':[0.25, 0.25], '4':[0.25, 0]},
                                '25k': {'SO':[0, 0], 'NO':[0, 0.125], 'NE':[0.125, 0.125], 'SE':[0.125, 0]},
                                '10k': {'E':[0, 0], 'C':[0, 0.125/3], 'D':[0.125/2, 0.125/3], 'F':[0.125/2, 0], 'A':[0, 2*0.125/3], 'B':[0.125/2, 2*0.125/3] },
                                '5k': {'III':[0, 0], 'I':[0, 0.125/3/2], 'II':[0.125/2/2, 0.125/3/2], 'IV':[0.125/2/2, 0]},
                                '2k': {'4':[0, 0], '1':[0, 0.125/3/2/2], '2':[0.125/2/2/3, 0.125/3/2/2], '5':[0.125/2/2/3, 0], '3':[2*0.125/2/2/3, 0.125/3/2/2], '6':[2*0.125/2/2/3,0]},
                                '1k': {'C':[0, 0], 'A':[0, 0.125/3/2/2/2], 'B':[0.125/2/2/3/2, 0.125/3/2/2/2], 'D':[0.125/2/2/3/2, 0]}
                                }
            escalas = ['500k', '250k', '100k', '50k', '25k', '10k', '5k', '2k', '1k']
            for k, cod in enumerate(lista[2:]):
                d_lon = dic_delta[escalas[k]][cod][0]
                d_lat = dic_delta[escalas[k]][cod][1]
                lon += d_lon
                lat += d_lat
            feedback.pushInfo(self.tr('Origin','Origem')+': Longitude = {} e Latitude = {}'.format(lon, lat))
            valores = array([[3.0, 1.5, 0.5, 0.25, 0.125, 0.125/2, 0.125/2/2, 0.125/2/2/3, 0.125/2/2/3/2],
                                   [2.0, 1.0, 0.5, 0.25, 0.125, 0.125/3, 0.125/3/2, 0.125/3/2/2, 0.125/3/2/2/2]])
            d_lon = valores[0,k]
            d_lat = valores[1,k]
            coord = [[QgsPointXY(lon         , lat),
                          QgsPointXY(lon          , lat+d_lat),
                          QgsPointXY(lon+d_lon, lat+d_lat),
                          QgsPointXY(lon+d_lon, lat),
                          QgsPointXY(lon          , lat)]]
            escala = int(escalas[k][:-1])*1000

        feat = QgsFeature()
        geom = QgsGeometry.fromPolygonXY(coord)
        # Coordinate Transformations (if needed)
        geom = geom if crs.isGeographic() else reprojectPoints(geom, coordinateTransformer)
        if tipo == 0:
            mi = nome
            lista = mi.split('-')
            inom = dicionario[lista[0]]
            if len(lista)>1:
                resto = ''
                for k in range(1,len(lista)):
                    resto += lista[k] +'-'
                inom += '-' + resto[:-1]
            att = [inom, mi, escala]
        else:
            inom = nome
            mi = None
            for MI, val in dicionario.items():
                if val == inom:
                    mi = MI
            att = [inom, mi, escala]
        feedback.pushInfo('INOM: {} e MI: {}'.format(inom, mi))
        feat.setGeometry(geom)
        feat.setAttributes(att)
        sink.addFeature(feat, QgsFeatureSink.FastInsert)

        if sink is None:
            raise QgsProcessingException(self.invalidSinkError(parameters, self.FRAME))

        feedback.pushInfo(self.tr('Operation completed successfully!', 'Operação finalizada com sucesso!'))
        feedback.pushInfo(self.tr('Leandro Franca - Cartographic Engineer', 'Leandro França - Eng Cart'))

        return {self.FRAME: dest_id}
