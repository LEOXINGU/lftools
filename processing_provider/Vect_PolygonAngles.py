# -*- coding: utf-8 -*-

"""
Vect_PolygonAngles.py
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
__date__ = '2019-11-02'
__copyright__ = '(C) 2019, Leandro França'

from qgis.PyQt.QtCore import QVariant
from qgis.core import *
from math import atan, pi, sqrt
from numpy.linalg import norm
import numpy as np
import math
from numpy import floor
from lftools.geocapt.imgs import Imgs
from lftools.translations.translate import translate
from lftools.geocapt.topogeo import azimute, dd2dms, meters2degrees
from lftools.geocapt.cartography import areaGauss, Mesclar_Multilinhas
import os
from qgis.PyQt.QtGui import QIcon


class CalculatePolygonAngles(QgsProcessingAlgorithm):

    POLYGONS = 'POLYGONS'
    ANGLES = 'ANGLES'
    DISTANCE = 'DISTANCE'
    INTERNAL = 'INTERNAL'
    EXTERNAL = 'EXTERNAL'

    LOC = QgsApplication.locale()[:2]

    def tr(self, *string):
        return translate(string, self.LOC)

    def createInstance(self):
        return CalculatePolygonAngles()

    def name(self):
        return 'calculatepolygonangles'

    def displayName(self):
        return self.tr('Calculate polygon angles', 'Calcular ângulos de polígono')

    def group(self):
        return self.tr('Vector', 'Vetor')

    def groupId(self):
        return 'vector'

    def tags(self):
        return 'GeoOne,angle,angulos,medida,abertura,outer,inner,polygon,measure,topography,azimuth,extract,vertices,extrair,vértices'.split(',')

    def icon(self):
        return QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images/vetor.png'))

    txt_en = 'This algorithm calculates the inner and outer angles of the polygon vertices of a layer. The output layer corresponds to the points with the calculated angles stored in the respective attributes.'
    txt_pt = 'Este algoritmo calcula os ângulos internos e externos dos vértices de uma camada de polígonos. A camada de pontos de saída tem os ângulos calculados armazenados em sua tabela de atributos.'
    figure = 'images/tutorial/vect_polygon_angles.jpg'

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
        # INPUT
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.POLYGONS,
                self.tr('Polygon layer', 'Camada de Polígonos'),
                [QgsProcessing.TypeVectorPolygon]
            )
        )

        self.addParameter(
            QgsProcessingParameterNumber(
                self.DISTANCE,
                self.tr('Distance (m)', 'Distância (m)'),
                type = QgsProcessingParameterNumber.Type.Double,
                defaultValue = 2.5,
                minValue = 0.001
                )
            )

        # OUTPUT
        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.ANGLES,
                self.tr('Points with angles', 'Pontos com ângulos')
            )
        )

        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.INTERNAL,
                self.tr('Interior angle lines', 'Linhas de ângulos interiores')
            )
        )

        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.EXTERNAL,
                self.tr('Exterior angle lines', 'Linhas de ângulos exteriores')
            )
        )


    def processAlgorithm(self, parameters, context, feedback):
        # INPUT
        source = self.parameterAsSource(
            parameters,
            self.POLYGONS,
            context
        )
        if source is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.POLYGONS))

        Distancia = self.parameterAsDouble(
            parameters,
            self.DISTANCE,
            context
        )
        if Distancia is None or Distancia < 0:
            raise QgsProcessingException(self.tr('The input distance must be grater than 0!', 'A distância de entrada deve ser maior que 0!'))

        # Camada de entrada
        CRS = source.sourceCrs()
        extensao = source.sourceExtent()
        y_max = extensao.yMaximum()
        y_min = extensao.yMinimum()

        # Transformar distancia para graus, se o SRC for Geográfico
        if CRS.isGeographic():
            Distancia = meters2degrees(Distancia, (y_max + y_min)/2, CRS)

        # OUTPUT 1: Points
        GeomType = QgsWkbTypes.Point
        Fields = QgsFields()

        itens  = {
                     'ord' : QVariant.Int,
                     self.tr('ang_inner_dd','ang_int_dec') : QVariant.Double,
                     self.tr('ang_inner_dms','ang_int_gms') : QVariant.String,
                     self.tr('ang_outer_dd','ang_ext_dec') : QVariant.Double,
                     self.tr('ang_outer_dms','ang_ext_gms') : QVariant.String,
                     'feat_id': QVariant.Int,
                     self.tr('label_azimuth','azimute_rotulo') : QVariant.Double,
                     }
        for item in itens:
            Fields.append(QgsField(item, itens[item]))

        (sink1, dest_id1) = self.parameterAsSink(
            parameters,
            self.ANGLES,
            context,
            Fields,
            GeomType,
            CRS
        )
        if sink1 is None:
            raise QgsProcessingException(self.invalidSinkError(parameters, self.ANGLES))

        # OUTPUT 2: Linhas interiores
        GeomType = QgsWkbTypes.LineString
        Fields = QgsFields()

        itens  = {
                     'ord' : QVariant.Int,
                     self.tr('ang_dd','ang_dec') : QVariant.Double,
                     self.tr('ang_dms','ang_gms') : QVariant.String,
                     'feat_id': QVariant.Int,
                     }
        for item in itens:
            Fields.append(QgsField(item, itens[item]))

        (sink2, dest_id2) = self.parameterAsSink(
            parameters,
            self.INTERNAL,
            context,
            Fields,
            GeomType,
            CRS
        )
        if sink2 is None:
            raise QgsProcessingException(self.invalidSinkError(parameters, self.ANGLES))

        # OUTPUT 3: Linhas exteriores
        (sink3, dest_id3) = self.parameterAsSink(
            parameters,
            self.EXTERNAL,
            context,
            Fields,
            GeomType,
            CRS
        )
        if sink3 is None:
            raise QgsProcessingException(self.invalidSinkError(parameters, self.ANGLES))

        total = 100.0 / source.featureCount() if source.featureCount() else 0

        for current, feat in enumerate(source.getFeatures()):
            geom = feat.geometry()
            if geom.isMultipart():
                poligonos = geom.asMultiPolygon() # Poligonos
                coords = []
                for poligono in poligonos:
                    coords += [poligono[0]] # anel externo
            else:
                coords = [geom.asPolygon()[0]] # anel externo

            # para cada parte
            for coord in coords:
                geomPol = QgsGeometry.fromPolygonXY([coord])
                AreaGauss = areaGauss(coord[:-1])
                tam = len(coord[:-1])
                cont = 0
                pntsDic = {}
                for ponto in coord[:-1]:
                    cont += 1
                    pntsDic[cont] = {'pnt': ponto}
                # Cálculo dos Ângulos Internos e Externos
                for k in range(tam):
                    P1 = pntsDic[ tam if k==0 else k]['pnt']
                    P2 = pntsDic[k+1]['pnt']
                    P3 = pntsDic[ 1 if (k+2)==(tam+1) else (k+2)]['pnt']
                    alfa = azimute(P2, P1)[0] - azimute(P2,P3)[0]
                    alfa = alfa if alfa > 0 else alfa+2*pi
                    if AreaGauss > 0: # sentido horário
                        pntsDic[k+1]['alfa_int'] = alfa*180/pi
                        pntsDic[k+1]['alfa_ext'] = 360 - alfa*180/pi
                    else: # sentido anti-horário
                        pntsDic[k+1]['alfa_ext'] = alfa*180/pi
                        pntsDic[k+1]['alfa_int'] = 360 - alfa*180/pi
                    # Cálculo do azimute principal para o rótulo
                    P2P1 = np.array([P1.x()-P2.x(), P1.y()-P2.y()])
                    Va =  P2P1/norm(P2P1)
                    P2P3 = np.array([P3.x()-P2.x(), P3.y()-P2.y()])
                    Vb =  P2P3/norm(P2P3)
                    Vr = Va + Vb
                    Azimute = azimute(QgsPointXY(0,0), QgsPointXY(float(Vr[0]), float(Vr[1]) ))[0]
                    pntsDic[k+1]['azimute'] = Azimute*180/pi


                for ponto in pntsDic:
                    # Carregando ângulos internos na camada
                    geomPonto = QgsGeometry.fromPointXY(pntsDic[ponto]['pnt'])
                    fet = QgsFeature()
                    fet.setGeometry(geomPonto)
                    fet.setAttributes([ponto,
                                        float(pntsDic[ponto]['alfa_int']),
                                        dd2dms(pntsDic[ponto]['alfa_int'],1),
                                        float(pntsDic[ponto]['alfa_ext']),
                                        dd2dms(pntsDic[ponto]['alfa_ext'],1),
                                        feat.id(),
                                        float(pntsDic[ponto]['azimute'])
                                            ])
                    sink1.addFeature(fet, QgsFeatureSink.FastInsert)

                    # Geração das linhas internas e externas
                    buffer = geomPonto.buffer(Distancia, 6)
                    anel = QgsGeometry.fromPolylineXY(buffer.asPolygon()[0])
                    lin_int = anel.intersection(geomPol)
                    lin_ext = anel.difference(geomPol)

                    try:
                        # Alimentar camada de linhas internas
                        fet = QgsFeature()
                        fet.setGeometry(Mesclar_Multilinhas(lin_int))
                        fet.setAttributes([ponto,
                                            float(pntsDic[ponto]['alfa_int']),
                                            dd2dms(pntsDic[ponto]['alfa_int'],1),
                                            feat.id()
                                                ])
                        sink2.addFeature(fet, QgsFeatureSink.FastInsert)

                        # Alimentar camada de linhas externas
                        fet = QgsFeature()
                        fet.setGeometry(Mesclar_Multilinhas(lin_ext))
                        fet.setAttributes([ponto,
                                            float(pntsDic[ponto]['alfa_ext']),
                                            dd2dms(pntsDic[ponto]['alfa_ext'],1),
                                            feat.id()
                                                ])
                        sink3.addFeature(fet, QgsFeatureSink.FastInsert)

                    except:
                        feedback.reportError(self.tr('Angle line outside polygon bounds! Reduce radius size (distance).', 'Linha de ângulo fora dos limites do polígono! Reduza o tamanho do raio (distância).') + ' ID: {}, vertex: {}'.format(feat.id(), ponto))


            if feedback.isCanceled():
                break
            feedback.setProgress(int(current * total))

        feedback.pushInfo(self.tr('Operation completed successfully!', 'Operação finalizada com sucesso!'))
        feedback.pushInfo(self.tr('Leandro França - Cartographic Engineer', 'Leandro França - Eng Cart'))

        self.SAIDA1 = dest_id1
        self.SAIDA2 = dest_id2
        self.SAIDA3 = dest_id3

        return {self.ANGLES: dest_id1,
                self.INTERNAL: dest_id2,
                self.EXTERNAL: dest_id3,    }

    def postProcessAlgorithm(self, context, feedback):
        layer1 = QgsProcessingUtils.mapLayerFromString(self.SAIDA1, context)

        # Definir estilos
        estilo1 = os.path.join(os.path.dirname(os.path.dirname(__file__)), self.tr('styles/vertex_angle_prof_leandro.qml', 'styles/vertice_angulo_prof_leandro.qml'))
        layer1.loadNamedStyle(estilo1)
        layer1.triggerRepaint()

        layer2 = QgsProcessingUtils.mapLayerFromString(self.SAIDA2, context)
        estilo2 = os.path.join(os.path.dirname(os.path.dirname(__file__)), self.tr('styles/line_angles_interior_prof_leandro.qml', 'styles/linha_angulo_int_prof_leandro.qml'))
        layer2.loadNamedStyle(estilo2)
        layer2.triggerRepaint()

        layer3 = QgsProcessingUtils.mapLayerFromString(self.SAIDA3, context)
        estilo3 = os.path.join(os.path.dirname(os.path.dirname(__file__)), self.tr('styles/line_angles_exterior_prof_leandro.qml', 'styles/linha_angulo_ext_prof_leandro.qml'))
        layer3.loadNamedStyle(estilo3)
        layer3.triggerRepaint()

        return {}
