# -*- coding: utf-8 -*-

"""
Gnss_pos2layer.py
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
__date__ = '2022-06-13'
__copyright__ = '(C) 2022, Leandro França'

from qgis.PyQt.QtCore import QVariant
from qgis.core import *
from lftools.geocapt.imgs import Imgs
from lftools.translations.translate import translate
from lftools.geocapt.vemos import vemos
from lftools.geocapt.topogeo import meters2degrees, datetime_decimal_str, str_decimal_to_datetime
import codecs
import os
from qgis.PyQt.QtGui import QIcon, QColor


class Pos2layer(QgsProcessingAlgorithm):

    LOC = QgsApplication.locale()[:2]

    def tr(self, *string):
        return translate(string, self.LOC)

    def createInstance(self):
        return Pos2layer()

    def name(self):
        return 'pos2layer'

    def displayName(self):
        return self.tr('POS file (.pos) to layer', 'POS para camada')

    def group(self):
        return self.tr('GNSS', 'GNSS')

    def groupId(self):
        return 'gnss'

    def tags(self):
        return 'GeoOne,gps,position,ibge,.pos,rtklib,ppp,navigation,vemos,satellites,rinex,surveying,glonass,beidou,compass,galileu,track,kinematic,rtk,ntrip,static'.split(',')

    def icon(self):
        return QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images/satellite.png'))

    txt_en = '''Loads a POS file (.pos) from GNSS processing as a point layer.
Compatibility: RTKLIB, IBGE-PPP.
Types:
◼️ All processed points
◼️ Last point'''
    txt_pt = '''Carrega um arquivo POS resultante do processamento de dados GNSS como uma camada do tipo ponto.
Compatibilidade: RTKLIB, IBGE-PPP
Tipos:
◼️ Todos os pontos processados
◼️ Último ponto'''

    figure = 'images/tutorial/gnss_pos2layer.jpg'

    def shortHelpString(self):
        social_BW = Imgs().social_BW
        footer = '''<div align="center">
                      <img src="'''+ os.path.join(os.path.dirname(os.path.dirname(__file__)), self.figure) +'''">
                      </div>
                      <div align="left">
                      <p>
                      <b><a href="'''+ self.tr('https://portal.geoone.com.br/m/lessons/pvgnss?classId=3644') + '''" target="_blank">'''+ self.tr('Click here to watch a full class on this tool',
                                    'Clique aqui para assistir uma aula completa sobre esta ferramenta') +'''</a></b>
                      </p>
                      <p>
                      <b><a href="'''+ self.tr('https://geoone.com.br/pvgnss/') + '''" target="_blank">'''+ self.tr('Sign up for the GNSS with RTKLib and QGIS course',
                                    'Inscreva-se no curso de GNSS com RTKLib e QGIS') +'</a><br><br>'+ self.tr('Author: Leandro Franca', 'Autor: Leandro França')+'''</b>
                      </p>'''+ social_BW + '''
                    </div>'''
        return self.tr(self.txt_en, self.txt_pt) + footer


    FILE = 'FILE'
    TYPE = 'TYPE'
    HEIGHT = 'HEIGHT'
    OUTPUT = 'OUTPUT'
    CRS = 'CRS'
    VEMOS = 'VEMOS'

    def initAlgorithm(self, config=None):

        self.addParameter(
            QgsProcessingParameterFile(
                self.FILE,
                self.tr('POS file (.pos)', 'Arquivo POS (.pos)'),
                behavior = QgsProcessingParameterFile.File,
                fileFilter = 'POS (*.pos)'
            )
        )

        tipo = [self.tr('All points processed','Todos os pontos processados'),
                self.tr('Last point','Último ponto')
               ]

        self.addParameter(
            QgsProcessingParameterEnum(
                self.TYPE,
                self.tr('Type', 'Tipo'),
				options = tipo,
                defaultValue = 0
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

        vemos = [self.tr('None', 'Nenhum'),
                self.tr('VEMOS2009'),
                self.tr('VEMOS2017'),
                self.tr('VEMOS2022')
                ]

        self.addParameter(
            QgsProcessingParameterEnum(
                self.VEMOS,
                self.tr('Velocity Model', 'Modelo de Velocidade'),
				options = vemos,
                defaultValue= 0
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
        nome = file

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

        model_vel = self.parameterAsEnum(
            parameters,
            self.VEMOS,
            context
        )

        itens  = {"ord": QVariant.Int,
                  "lat": QVariant.Double,
                  "lon": QVariant.Double,
                  "h": QVariant.Double,
                  self.tr("datetime","datahora"): QVariant.String,
                  "sigma_x": QVariant.Double,
                  "sigma_y": QVariant.Double,
                  "sigma_z": QVariant.Double,
                  "num_sat": QVariant.Int,
                  "quality": QVariant.String,
                  "h_reduction": QVariant.Double,
             }
        Fields = QgsFields()
        for item in itens:
            Fields.append(QgsField(item, itens[item]))

        (sink, dest_id) = self.parameterAsSink( parameters, self.OUTPUT, context, Fields, QgsWkbTypes.PointZ, crs)
        if sink is None:
            raise QgsProcessingException(self.invalidSinkError(parameters, self.OUTPUT))

        arq = codecs.open(caminho, 'r', encoding='utf-8', errors='ignore')

        saida = self.parameterAsEnum(
            parameters,
            self.TYPE,
            context
        )
        quality_dic = {1:'1: fix', 2:'2: float', 3:'3: sbas', 4:'4: dgps', 5: '5: single', 6: '6: ppp'}

        # IBGE ou RTKLIB
        for linha in arq.readlines():
            break
        arq.close()
        if linha[0] == '%':
            tipo = 'rtklib'
            feedback.pushInfo(self.tr("It's a RTKLIB file!", 'É um arquivo do RTKLIB!'))
        elif linha[0] == '-':
            tipo = 'ibge'
            feedback.pushInfo(self.tr("It's a IBGE-PPP file!", 'É um arquivo do PPP-IBGE!'))
        else:
            raise QgsProcessingException(self.tr('Unrecognized POS file format!', 'Formato de arquivo POS não reconhecido!'))

        arq = codecs.open(caminho, 'r', encoding='utf-8', errors='ignore')
        lista = []
        dic = {}
        if tipo == 'rtklib':
            for linha in arq.readlines():
                if linha[0] != '%':
                    while '  ' in linha:
                        linha = linha.replace('  ', ' ')
                    lista += [linha.split(' ')]
            arq.close()
            for k,pnt in enumerate(lista):
                lat = float(pnt[2])
                lon = float(pnt[3])
                h = float(pnt[4])
                ano, mes, dia = pnt[0].split('/')
                hora, minuto, segundo = pnt[1].split(':')
                datahora = datetime_decimal_str(int(ano), int(mes), int(dia), int(hora), int(minuto), float(segundo))
                quality = quality_dic[int(pnt[5])]
                nsat = int(pnt[6])
                slat = float(pnt[7])
                slon = float(pnt[8])
                sh = float(pnt[9])
                dic[k+1] = {'lat': lat, 'lon':lon, 'h': h, 'datahora': datahora, 'quality': quality, 'nsat': nsat,
                          'slat': slat, 'slon': slon, 'sh':sh   }
        elif tipo == 'ibge':
            for linha in arq.readlines():
                if linha[0:3] == 'FWD':
                    while '  ' in linha:
                        linha = linha.replace('  ', ' ')
                    lista += [linha.split(' ')]
            arq.close()
            for k,pnt in enumerate(lista):
                lat = float(pnt[20]) + (-1 if float(pnt[20]) < 0 else 1)*(float(pnt[21])/60. + float(pnt[22])/3600)
                lon = float(pnt[23]) + (-1 if float(pnt[23]) < 0 else 1)*(float(pnt[24])/60. + float(pnt[25])/3600)
                h = float(pnt[26])
                ano, mes, dia = pnt[4].split('-')
                hora, minuto, segundo = pnt[5].split(':')
                if int(float(segundo)) != 60:
                    datahora = datetime_decimal_str(int(ano), int(mes), int(dia), int(hora), int(minuto), float(segundo))
                else:
                    if int(minuto) < 59:
                        datahora = datetime_decimal_str(int(ano), int(mes), int(dia), int(hora), int(minuto) + 1, 0)
                    else:
                        datahora = datetime_decimal_str(int(ano), int(mes), int(dia), int(hora) + 1, 0, 0)
                quality = 'ppp-ibge'
                nsat = int(pnt[6])
                slat = float(pnt[15])
                slon = float(pnt[16])
                sh = float(pnt[17])
                dic[k+1] = {'lat': lat, 'lon':lon, 'h': h, 'datahora': datahora, 'quality': quality, 'nsat': nsat,
                          'slat': slat, 'slon': slon, 'sh':sh   }
        # Salvando os resultados
        tam = len(lista)
        total = 100./tam if tam>0 else 0
        for k, item in enumerate(dic):
            lat = dic[item]['lat']
            lon = dic[item]['lon']
            h = dic[item]['h'] - aa
            datahora = dic[item]['datahora']
            quality = dic[item]['quality']
            nsat = dic[item]['nsat']
            slat = dic[item]['slat']
            slon = dic[item]['slon']
            sh = dic[item]['sh']
            feat = QgsFeature(Fields)
            feat['ord'] = item
            feat['lat'] = lat
            feat['lon'] = lon
            feat['h'] = h
            feat[self.tr("datetime","datahora")] = datahora
            feat['sigma_x'] = slon
            feat['sigma_y'] = slat
            feat['sigma_z'] = sh
            feat['num_sat'] = nsat
            feat['quality'] = quality
            feat['h_reduction'] = aa

            if model_vel > 0 and saida == 0:
                vlat, vlon = vemos(lat, lon, ['vemos2009','vemos2017','vemos2022'][model_vel-1])
                delta_tempo = str_decimal_to_datetime(datahora) - str_decimal_to_datetime('2000-04-24 12:00:00')
                anos = delta_tempo.days/365.25
                dLat = meters2degrees(vlat*anos, lat, QgsCoordinateReferenceSystem('EPSG:4674'))
                dLon = meters2degrees(vlon*anos, lat, QgsCoordinateReferenceSystem('EPSG:4674'))
                lat -= dLat
                lon -= dLon
                feat['lat'] = float(lat)
                feat['lon'] = float(lon)

            if saida == 0:
                feat.setGeometry(QgsPoint(lon, lat, h))
                sink.addFeature(feat, QgsFeatureSink.FastInsert)
            if feedback.isCanceled():
                break
            feedback.setProgress(int((k+1) * total))


        if saida == 1:
            if model_vel > 0:
                vlat, vlon = vemos(lat, lon, ['vemos2009','vemos2017','vemos2022'][model_vel-1])
                delta_tempo = str_decimal_to_datetime(datahora) - str_decimal_to_datetime('2000-04-24 12:00:00')
                anos = delta_tempo.days/365.25
                dLat = meters2degrees(vlat*anos, lat, QgsCoordinateReferenceSystem('EPSG:4674'))
                dLon = meters2degrees(vlon*anos, lat, QgsCoordinateReferenceSystem('EPSG:4674'))
                lat -= dLat
                lon -= dLon
                feat['lat'] = float(lat)
                feat['lon'] = float(lon)
            feat.setGeometry(QgsPoint(lon, lat, h))
            sink.addFeature(feat, QgsFeatureSink.FastInsert)

        feedback.pushInfo(self.tr('Operation completed successfully!', 'Operação finalizada com sucesso!'))
        feedback.pushInfo(self.tr('Leandro Franca - Cartographic Engineer', 'Leandro França - Eng Cart'))

        global renamer
        renamer = Renamer(nome)
        context.layerToLoadOnCompletionDetails(dest_id).setPostProcessor(renamer)

        self.SAIDA = dest_id

        return {self.OUTPUT: dest_id}
    

    def postProcessAlgorithm(self, context, feedback):
        layer = QgsProcessingUtils.mapLayerFromString(self.SAIDA, context)
        if layer is not None:

           # Criar a simbologia baseada em regras
            root_rule = QgsRuleBasedRenderer.Rule(None)

            # Helper: cria regra com filtro, label e cor
            def add_rule(filter_expr, label, color_hex, size=2.1):
                rule = QgsRuleBasedRenderer.Rule(QgsSymbol.defaultSymbol(layer.geometryType()))
                rule.setFilterExpression(filter_expr)
                rule.setLabel(label)
                rule.symbol().setColor(QColor(color_hex))
                rule.symbol().setSize(size)
                root_rule.appendChild(rule)

            # FIX (verde)
            add_rule('"quality" = \'1: fix\'',   "1: fix",    "#33a02c")  # verde

            # FLOAT (laranja)
            add_rule('"quality" = \'2: float\'', "2: float",  "#FF8C00")  # laranja

            # SINGLE (vermelho)
            add_rule('"quality" = \'5: single\'',"5: single", "#FF0000")  # vermelho

            # PPP (roxo)
            add_rule('"quality" in (\'6: ppp\', \'ppp-ibge\')',   "6: ppp",    "#c45ec4")  # roxo

            # OUTROS (cinza) - pega tudo que não caiu nas regras acima
            add_rule('ELSE', self.tr('others', 'outras'), "#b0b0b0")      # cinza

            # Aplicar a simbologia baseada em regras na camada
            renderer = QgsRuleBasedRenderer(root_rule)
            layer.setRenderer(renderer)
            layer.triggerRepaint()

        return {}

class Renamer (QgsProcessingLayerPostProcessorInterface):
    def __init__(self, layer_name):
        self.name = layer_name
        super().__init__()

    def postProcessLayer(self, layer, context, feedback):
        layer.setName(self.name)


  