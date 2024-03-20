# -*- coding: utf-8 -*-

"""
Gnss_NMEA2layer.py
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
__date__ = '2022-02-27'
__copyright__ = '(C) 2022, Leandro França'

from PyQt5.QtCore import QCoreApplication, QVariant
from qgis.core import (QgsProcessing,
                       QgsFeatureSink,
                       QgsWkbTypes,
                       QgsFields,
                       QgsField,
                       QgsPoint,
                       QgsFeature,
                       QgsGeometry,
                       QgsProcessingException,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterFile,
                       QgsProcessingParameterEnum,
                       QgsProcessingParameterNumber,
                       QgsFeatureRequest,
                       QgsProcessingUtils,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterFeatureSink,
                       QgsProcessingParameterFileDestination,
                       QgsProcessingParameterRasterLayer,
                       QgsProcessingParameterRasterDestination,
                       QgsApplication,
                       QgsProcessingParameterCrs,
                       QgsProject,
                       QgsRasterLayer,
                       QgsCoordinateTransform,
                       QgsProcessingLayerPostProcessorInterface,
                       QgsCoordinateReferenceSystem)

from lftools.geocapt.imgs import Imgs
from lftools.geocapt.cartography import raioMedioGauss
import numpy as np
import datetime
import codecs
import os
from qgis.PyQt.QtGui import QIcon


class NMEA2layer(QgsProcessingAlgorithm):

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
        return NMEA2layer()

    def name(self):
        return 'nmea2layer'

    def displayName(self):
        return self.tr('NMEA to layer', 'NMEA para camada')

    def group(self):
        return self.tr('GNSS', 'GNSS')

    def groupId(self):
        return 'gnss'

    def tags(self):
        return self.tr('gps,navigation,satellites,surveying,glonass,beidou,compass,galileu,track,kinematic,rtk,ntrip,static').split(',')

    def icon(self):
        return QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images/satellite.png'))

    txt_en = '''Loads a NMEA file (protocol 0183) from GNSS receivers as a point layer.
Modes:
◼️ Kinematic - generates all tracked points with their accuracies (PDOP, HDOP and VDOP) and number of satellites.
◼️ Static - calculates the mean and standard deviation of the observed points, for all points or only for fixed solution points (best result).'''
    txt_pt = '''Carrega um arquivo NMEA de rastreio GNSS (protocolo 0183) como uma camada do tipo ponto.
Modos:
◼️ Cinemático - gera todos os pontos rastreados com suas precisões (PDOP, HDOP e VDOP) e número de satélites.
◼️ Estático - calcula a média e desvio-padrão dos pontos observados, para todos os pontos ou somente para os pontos de solução fixa (melhor resultado).'''

    figure = 'images/tutorial/gnss_nmea.jpg'

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


    FILE = 'FILE'
    TYPE = 'TYPE'
    HEIGHT = 'HEIGHT'
    OUTPUT = 'OUTPUT'
    CRS = 'CRS'

    def initAlgorithm(self, config=None):

        self.addParameter(
            QgsProcessingParameterFile(
                self.FILE,
                self.tr('NMEA file .nmea', 'Arquivo NMEA .nmea'),
                behavior = QgsProcessingParameterFile.File,
                fileFilter = 'NMEA (*.nmea)'
            )
        )

        tipo = [self.tr('Kinematic','Cinemático'),
                self.tr('Static, fixed solution (best result)','Estático, solução fixa  (melhor resultado)'),
                self.tr('Static, all observations','Estático, todas as observações')
               ]

        self.addParameter(
            QgsProcessingParameterEnum(
                self.TYPE,
                self.tr('Attributes', 'Atributos'),
				options = tipo,
                defaultValue= 0
            )
        )

        self.addParameter(
            QgsProcessingParameterNumber(
                self.HEIGHT,
                self.tr('Antenna height', 'Altura da antena'),
                type = QgsProcessingParameterNumber.Type.Double,
                defaultValue = 0.0,
                minValue = 0
                )
            )

        self.addParameter(
            QgsProcessingParameterCrs(
                self.CRS,
                self.tr('CRS', 'SRC'),
                eval(self.tr("QgsCoordinateReferenceSystem('EPSG:4326')", "QgsCoordinateReferenceSystem('EPSG:4674')"))
                )
            )

        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT,
                self.tr('Point layer', 'Camada de ponto(s)')
            )
        )


    def processAlgorithm(self, parameters, context, feedback):

        caminho = self.parameterAsFile(
            parameters,
            self.FILE,
            context
        )
        if not caminho:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.FILE))

        path, file = os.path.split(caminho)
        nome = file[:-5]

        aa = self.parameterAsDouble(
            parameters,
            self.HEIGHT,
            context
        )

        crs = self.parameterAsCrs(
            parameters,
            self.CRS,
            context
        )
        if not crs.isGeographic():
            raise QgsProcessingException(self.tr('Choose a geographic CRS!', 'Escolha um SRC geográfico!'))

        arq = codecs.open(caminho, 'r', encoding='utf-8', errors='ignore')

        tipo = self.parameterAsEnum(
            parameters,
            self.TYPE,
            context
        )

        lista = []
        PDOP, HDOP, VDOP = -1, -1, -1
        nmea_quality = {0:'0: Invalid', 1:'1: Standalone', 2:'2: DGPS', 3:'3: n/a', 4:'4: RTK fixed', 5:'5: RTK float'}

        for line in arq.readlines():
            try:
                if line[3:6] == 'GSA': # GPS DOP and active satellites
                    partes = line.split(',')
                    PDOP = float(partes[-4])
                    HDOP = float(partes[-3])
                    VDOP = float(partes[-2])
                if line[3:6] == 'GGA': # global position system fix data
                    partes = line.split(',')
                    hora = int(partes[1][0:2])
                    min = int(partes[1][2:4])
                    seg = float(partes[1][4:10])
                    lat = (-1 if partes[3] == 'S' else 1)*( float(partes[2][0:2]) + float(partes[2][2:-1])/60)
                    lon = (-1 if partes[5] == 'W' else 1)*( float(partes[4][0:3]) + float(partes[4][3:-1])/60)
                    quality = nmea_quality[int(partes[6])]
                    num_sat = int(partes[7])
                    HDOP = float(partes[8])
                    H = float(partes[9]) - aa
                    N = float(partes[11])
                    h = N + H
                    lista += [[lat, lon, h, H, N, HDOP, VDOP, PDOP, hora, min, seg, quality, num_sat]]

                if line[3:6] == 'ZDA': # Time & Date – UTC, Day, Month, Year and Local Time Zone
                    partes = line.split(',')
                    dia = int(partes[2])
                    mes = int(partes[3])
                    ano = int(partes[4])
            except:
                pass

        arq.close()

        valores = np.array(lista)
        # Campos
        if tipo == 0:
            itens  = {"lat": QVariant.Double,
                      "lon": QVariant.Double,
                      "h_ellip": QVariant.Double,
                      "H_orto": QVariant.Double,
                      "N": QVariant.Double,
                      "datetime": QVariant.String,
                      "HDOP": QVariant.Double,
                      "VDOP": QVariant.Double,
                      "PDOP": QVariant.Double,
                      "quality": QVariant.String,
                      "num_sat": QVariant.Int
                 }
        else:
            itens  = {"lat": QVariant.Double,
                      "lon": QVariant.Double,
                      "h_ellip": QVariant.Double,
                      "H_orto": QVariant.Double,
                      "N": QVariant.Double,
                      "start_datetime": QVariant.String,
                      "end_datetime": QVariant.String,
                      "sigma_x": QVariant.Double,
                      "sigma_y": QVariant.Double,
                      "sigma_z": QVariant.Double,
                      "num_obs": QVariant.Int
                 }
        Fields = QgsFields()
        for item in itens:
            Fields.append(QgsField(item, itens[item]))

        (sink, dest_id) = self.parameterAsSink( parameters, self.OUTPUT, context, Fields, QgsWkbTypes.PointZ, crs)
        if sink is None:
            raise QgsProcessingException(self.invalidSinkError(parameters, self.OUTPUT))

        if tipo == 0: # Cinemático
            feat = QgsFeature()
            for pnt in lista:
                feat.setGeometry(QgsPoint(pnt[1],pnt[0], pnt[2]))
                try:
                    data_hora = unicode(datetime.datetime(ano, mes, dia, pnt[-5], pnt[-4], int(pnt[-3])))
                except:
                    data_hora = None
                feat.setAttributes(pnt[0:5] + [data_hora] + pnt[5:8] + pnt[-2:]  ) # lat, lon, h, H, N, HDOP, VDOP, PDOP, hora, min, seg, quality, num_sat
                sink.addFeature(feat, QgsFeatureSink.FastInsert)

        elif tipo == 1: # Estático com solução fixa
            valores = valores[valores[:,-2] == nmea_quality[4] ] # eliminando observações de baixa qualidade
            if len(valores) == 0:
                raise QgsProcessingException(self.tr('There is no observation with RTK correction.', 'Não existe observação com correção RTK.'))
            # calculo de valores médios
            lat = valores[:,0].astype('float').mean()
            s_lat = valores[:,0].astype('float').std()
            lon = valores[:,1].astype('float').mean()
            s_lon = valores[:,1].astype('float').std()
            h = valores[:,2].astype('float').mean()
            s_h = valores[:,2].astype('float').std()
            H = valores[:,3].astype('float').mean()
            N = valores[:,4].astype('float').mean()
            try:
                data_hora_ini = unicode(datetime.datetime(ano, mes, dia, int(valores[0, -5]), int(valores[0, -4]), int(float(valores[0, -3]))))
                data_hora_fim = unicode(datetime.datetime(ano, mes, dia, int(valores[-1, -5]), int(valores[-1, -4]), int(float(valores[-1, -3]))))
            except:
                data_hora_ini, data_hora_fim = None
            # Raio Médio de Gauss
            R = raioMedioGauss(lat, int(self.tr('4326','4674')))
            sigma_x = (R+h)*np.radians(s_lon)
            sigma_y = (R+h)*np.radians(s_lat)

            feat = QgsFeature()
            feat.setGeometry(QgsPoint(lon, lat, h))
            feat.setAttributes([float(lat),
                                float(lon),
                                float(h),
                                float(H),
                                float(N),
                                data_hora_ini,
                                data_hora_fim,
                                float(sigma_x),
                                float(sigma_y),
                                float(s_h),
                                len(valores)])
            sink.addFeature(feat, QgsFeatureSink.FastInsert)

        elif tipo == 2: # Estático com todos os valores
            # calculo de valores médios
            lat = valores[:,0].astype('float').mean()
            s_lat = valores[:,0].astype('float').std()
            lon = valores[:,1].astype('float').mean()
            s_lon = valores[:,1].astype('float').std()
            h = valores[:,2].astype('float').mean()
            s_h = valores[:,2].astype('float').std()
            H = valores[:,3].astype('float').mean()
            N = valores[:,4].astype('float').mean()
            try:
                data_hora_ini = unicode(datetime.datetime(ano, mes, dia, int(valores[0, -5]), int(valores[0, -4]), int(float(valores[0, -3]))))
                data_hora_fim = unicode(datetime.datetime(ano, mes, dia, int(valores[-1, -5]), int(valores[-1, -4]), int(float(valores[-1, -3]))))
            except:
                data_hora_ini, data_hora_fim = None, None
            # Raio Médio de Gauss
            R = raioMedioGauss(lat, int(self.tr('4326','4674')))
            sigma_x = (R+h)*np.radians(s_lon)
            sigma_y = (R+h)*np.radians(s_lat)

            feat = QgsFeature()
            feat.setGeometry(QgsPoint(lon, lat, h))
            feat.setAttributes([float(lat),
                                float(lon),
                                float(h),
                                float(H),
                                float(N),
                                data_hora_ini,
                                data_hora_fim,
                                float(sigma_x),
                                float(sigma_y),
                                float(s_h),
                                len(valores)])
            sink.addFeature(feat, QgsFeatureSink.FastInsert)

        feedback.pushInfo(self.tr('Operation completed successfully!', 'Operação finalizada com sucesso!'))
        feedback.pushInfo(self.tr('Leandro Franca - Cartographic Engineer', 'Leandro França - Eng Cart'))

        global renamer
        renamer = Renamer(nome)
        context.layerToLoadOnCompletionDetails(dest_id).setPostProcessor(renamer)

        return {self.OUTPUT: dest_id}

class Renamer (QgsProcessingLayerPostProcessorInterface):
    def __init__(self, layer_name):
        self.name = layer_name
        super().__init__()

    def postProcessLayer(self, layer, context, feedback):
        layer.setName(self.name)
