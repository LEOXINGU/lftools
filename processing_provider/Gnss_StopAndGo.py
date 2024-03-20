# -*- coding: utf-8 -*-

"""
Gnss_StopAndGo.py
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
                       QgsPointXY,
                       QgsProject,
                       QgsRasterLayer,
                       QgsCoordinateTransform,
                       QgsProcessingLayerPostProcessorInterface,
                       QgsCoordinateReferenceSystem)

from lftools.geocapt.imgs import Imgs
from lftools.geocapt.cartography import raioMedioGauss
import numpy as np
from pyproj.crs import CRS
from datetime import datetime
import codecs
import os
from qgis.PyQt.QtGui import QIcon


class StopAndGo(QgsProcessingAlgorithm):

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
        return StopAndGo()

    def name(self):
        return 'stopandgo'

    def displayName(self):
        return self.tr('Stop and Go', 'Semicinemático')

    def group(self):
        return self.tr('GNSS')

    def groupId(self):
        return 'gnss'

    def tags(self):
        return self.tr('gps,position,ibge,rtklib,ppp,ppk,navigation,satellites,surveying,rinex,glonass,beidou,compass,galileu,track,kinematic,rtk,ntrip,static,semikinematic,stop,and,go,semicinemático').split(',')

    def icon(self):
        return QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images/satellite.png'))

    txt_en = '''It finds the central points (vertices) of the concentrations of points surveyed by the Kinematic method (stop and go) from the processing of GNSS data.
Input data:
◼️ GNSS point layer from RTKLIB or IBGE-PPP from .pos file
◼️ Minimum time to survey the point in minutes
◼️ Tolerance in centimeters to consider the static point'''
    txt_pt = '''Encontra os pontos centrais (vértices) das concentrações de pontos levantados pelo método Seminemático (stop and go) provenientes do processamento de dados GNSS.
Dados de entrada:
◼️ Camada do tipo ponto gerada do arquivo .pos do RTKLIB ou IBGE-PPP
◼️ Tempo mínimo de levantamento do ponto em minutos
◼️ Tolerância em centímetros para considerar o ponto estático'''

    figure = 'images/tutorial/gnss_ppk.jpg'

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


    INPUT = 'INPUT'
    TIME = 'TIME'
    DIST = 'DIST'
    OUTPUT = 'OUTPUT'

    def initAlgorithm(self, config=None):

        # INPUT
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT,
                self.tr('GNSS point Layer', 'Camada de Pontos GNSS'),
                [QgsProcessing.TypeVectorPoint]
            )
        )

        self.addParameter(
            QgsProcessingParameterNumber(
                self.TIME,
                self.tr('Minimum time for static positioning (minutes)', 'Tempo mínimo para o posicionamento estático (minutos)'),
                type = QgsProcessingParameterNumber.Type.Double,
                defaultValue = 3.0,
                minValue = 0.10
                )
            )

        self.addParameter(
            QgsProcessingParameterNumber(
                self.DIST,
                self.tr('Maximum distance to be static (cm)', 'Distância máxima para ser estático (cm)'),
                type = QgsProcessingParameterNumber.Type.Double,
                defaultValue = 2.0,
                minValue = 0.5
                )
            )

        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT,
                self.tr('Central points', 'Vértices')
            )
        )


    def processAlgorithm(self, parameters, context, feedback):

        layer = self.parameterAsSource(
            parameters,
            self.INPUT,
            context
        )
        if layer is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.INPUT))

        tempo_min = self.parameterAsDouble(
            parameters,
            self.TIME,
            context
        )
        if not tempo_min:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.TIME))
        tempo_min *= 60 # segudos

        dist_max = self.parameterAsDouble(
            parameters,
            self.DIST,
            context
        )
        if not dist_max:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.DIST))
        dist_max /= 1e2 # metros

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
                  "start_time": QVariant.String,
                  "end_time": QVariant.String,
                  "count": QVariant.Int,
                  "group": QVariant.Int
             }
        Fields = QgsFields()
        for item in itens:
            Fields.append(QgsField(item, itens[item]))

        (sink, dest_id) = self.parameterAsSink( parameters, self.OUTPUT, context, Fields, QgsWkbTypes.PointZ, layer.sourceCrs())
        if sink is None:
            raise QgsProcessingException(self.invalidSinkError(parameters, self.OUTPUT))


        # Transformar distancia para graus
        extensao = layer.sourceExtent()
        SRC = layer.sourceCrs()
        y_max = extensao.yMaximum()
        y_min = extensao.yMinimum()
        EPSG = int(SRC.authid().split(':')[-1])
        proj_crs = CRS.from_epsg(EPSG)
        a=proj_crs.ellipsoid.semi_major_metre
        f=1/proj_crs.ellipsoid.inverse_flattening
        e2 = f*(2-f)
        N = a/np.sqrt(1-e2*(np.sin((y_min+y_max)/2))**2) # Raio de curvatura 1º vertical
        M = a*(1-e2)/(1-e2*(np.sin((y_min+y_max)/2))**2)**(3/2.) # Raio de curvatura meridiana
        R = np.sqrt(M*N) # Raio médio de Gauss
        theta = dist_max/R
        dist_max = np.degrees(theta) # Radianos para graus

        x, y = [],[]
        pontos = []
        for feat in layer.getFeatures():
            x += [feat.geometry().asPoint().x()]
            y += [feat.geometry().asPoint().y()]

        w = np.ones(len(x))

        def CentralFeature(x, y):
            dist_soma = 1e15
            indice = -1
            for i in range(len(x)):
                x1 = x[i]
                y1 = y[i]
                soma = 0
                for j in range(len(y)):
                    x2 = x[j]
                    y2 = y[j]
                    soma += np.sqrt((x1 - x2)**2 + (y1 - y2)**2)
                if soma < dist_soma:
                    dist_soma = soma
                    indice = i
            return x[indice], y[indice]

        # Saber se o ponto está parado em um ponto
        X, Y = [],[]
        datahora = []
        for feat in layer.getFeatures():
            X += [feat.geometry().asPoint().x()]
            Y += [feat.geometry().asPoint().y()]
            datahora += [feat[self.tr('datetime', 'datahora')]]

        cont = 1
        try:
            t_ini = datahora[0]
        except:
            raise QgsProcessingException(self.tr('Check the input layer!', 'Verifique a camada de entrada!'))
        grupos = {}
        x, y = [],[]
        for i in range(len(X)-1):
            x1 = X[i]
            y1 = Y[i]
            x2 = X[i+1]
            y2 = Y[i+1]
            t = datahora[i+1]
            if np.sqrt((x1 - x2)**2 + (y1 - y2)**2) < dist_max:
                x += [x1]
                y += [y1]
            else:
                intervalo = datetime.strptime(t, "%Y-%m-%d %H:%M:%S") - datetime.strptime(t_ini, "%Y-%m-%d %H:%M:%S")
                intervalo = intervalo.total_seconds() # intervalo em segundos
                if  intervalo > tempo_min: # se ficou parado pelo tempo mínimo
                    grupos[cont] = {'x': x, 'y': y, 't_ini': t_ini, 't_fim': t}
                    cont += 1
                t_ini = t
                x, y = [],[]

        # Última leva
        intervalo = datetime.strptime(t, "%Y-%m-%d %H:%M:%S") - datetime.strptime(t_ini, "%Y-%m-%d %H:%M:%S")
        intervalo = intervalo.total_seconds()
        if  intervalo > tempo_min:
            grupos[cont] = {'x': x, 'y': y, 't_ini': t_ini, 't_fim': t}

        # Calcular feição central
        feedback.pushInfo(self.tr('Calculating central features...', 'Calculando feições centrais...'))
        for grupo in grupos:
            x = grupos[grupo]['x']
            y = grupos[grupo]['y']
            if len(x) > 0:
                central_X, central_Y = CentralFeature(x, y)
                # Pegar atributos do ponto central
                for feat in layer.getFeatures():
                    geom = feat.geometry()
                    if geom.isMultipart():
                        pnt = geom.asMultiPoint()[0]
                    else:
                        pnt = geom.asPoint()
                    if pnt.x() == central_X and pnt.y() == central_Y:
                        att = feat.attributes()
                        break
                pnt = QgsGeometry.fromPointXY(QgsPointXY(float(central_X), float(central_Y)))
                att += [grupos[grupo]['t_ini'], grupos[grupo]['t_fim'], len(x), str(grupo)]
                feat.setGeometry(pnt)
                feat.setAttributes(att)
                sink.addFeature(feat, QgsFeatureSink.FastInsert)
                if feedback.isCanceled():
                    break

        feedback.pushInfo(self.tr('Operation completed successfully!', 'Operação finalizada com sucesso!'))
        feedback.pushInfo(self.tr('Leandro Franca - Cartographic Engineer', 'Leandro França - Eng Cart'))

        return {self.OUTPUT: dest_id}
