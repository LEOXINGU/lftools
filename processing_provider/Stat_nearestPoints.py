# -*- coding: utf-8 -*-

"""
Stat_nearestPoints.py
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
__date__ = '2023-06-28'
__copyright__ = '(C) 2023, Leandro França'

from PyQt5.QtCore import QCoreApplication, QVariant
from qgis.core import (QgsProcessing,
                       QgsFeatureSink,
                       QgsWkbTypes,
                       QgsField,
                       QgsFeature,
                       QgsGeometry,
                       QgsMultiPoint,
                       QgsProcessingException,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterNumber,
                       QgsProcessingParameterField,
                       QgsProcessingParameterEnum,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterFeatureSink,
                       QgsApplication,
                       QgsCoordinateTransform,
                       QgsCoordinateReferenceSystem)
import numpy as np
from lftools.geocapt.imgs import Imgs
from lftools.geocapt.topogeo import meters2degrees, degrees2meters
import os
from qgis.PyQt.QtGui import QIcon


class NearestPoints(QgsProcessingAlgorithm):

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
        return NearestPoints()

    def name(self):
        return 'nearestpoints'

    def displayName(self):
        return self.tr('Nearest points', 'Pontos mais próximos')

    def group(self):
        return self.tr('Spatial Statistics', 'Estatística Espacial')

    def groupId(self):
        return 'spatialstatistics'

    def tags(self):
        return self.tr('deviational,standard,nmea,gnss,gps,trend,confidence,covariance,mean,average,median,center,distances,centroid').split(',')

    def icon(self):
        return QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images/statistics.png'))

    txt_en = '''Calculates the sigmax, sigmay and sigmaz precisions (when available) of the closest points to each reference point considering a maximum distance or a minimum number of closest points.
Output: Multipoint layer with positional accuracies in meters and other statistics.
1) Max distance: get all points within the distance.
2) Minimum quantity: get all the closest points, regardless of the maximum distance.
3) Maximum distance and minimum quantity: get only the closest points that are within the maximum distance.'''
    txt_pt = '''Calcula as precisões sigmax, sigmay e sigmaz (quando existir) dos pontos mais próximos de cada ponto de referência considerando uma distância máxima ou uma quantidade mínima de pontos mais próximos.
Saída: Camada de multipoint com precisões posicionais em metros e outras estatísticas.
1) Distância máxima: busca todos os pontos dentro da distância.
2) Quantidade mínima: busca todos os pontos mais próximos, independente de distância máxima.
3) Distância máxima e quantidade mínima: busca apenas os pontos mais próximos que estão dentro da distância máxima.'''
    figure = 'images/tutorial/stat_nearestPoints.jpg'

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

    REF = 'REF'
    PNTS = 'PNTS'
    FIELD = 'FIELD'
    STATS = 'STATS'
    OPTIONS = ['count','sum','mean','median', 'std', 'min', 'max']
    DIST = 'DIST'
    QNT = 'QNT'
    COND = 'COND'
    OUTPUT = 'OUTPUT'

    def initAlgorithm(self, config=None):
        # INPUT
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.REF,
                self.tr('Reference points', 'Pontos de referência'),
                [QgsProcessing.TypeVectorPoint]
            )
        )

        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.PNTS,
                self.tr('Points to be analyzed', 'Pontos a serem analisados'),
                [QgsProcessing.TypeVectorPoint]
            )
        )

        self.addParameter(
            QgsProcessingParameterNumber(
                self.DIST,
                self.tr('Maximum distance (meters)', 'Distância máxima (metros)'),
                type = 1,
                defaultValue = 0.5
                )
            )

        self.addParameter(
            QgsProcessingParameterNumber(
                self.QNT,
                self.tr('Minimum quantity', 'Quantidade mínima'),
                type = 0,
                defaultValue = 20
                )
            )

        tipos = [self.tr('Maximum distance', 'Distância máxima'),
                 self.tr('Minimum quantity', 'Quantidade mínima'),
                 self.tr('Maximum distance and minimum quantity', 'Distância máxima e quantidade mínima')]

        self.addParameter(
            QgsProcessingParameterEnum(
                self.COND,
                self.tr('Condition', 'Condição'),
				options = tipos,
                defaultValue = 2
            )
        )

        self.addParameter(
            QgsProcessingParameterField(
                self.FIELD,
                self.tr('Attribute stats', 'Estatísticas de atributo'),
                parentLayerParameterName = self.PNTS,
                type = QgsProcessingParameterField.Numeric,
                optional = True
            )
        )

        self.addParameter(
            QgsProcessingParameterEnum(
                self.STATS,
                self.tr('Statistics', 'Estatísticas'),
				options = self.OPTIONS,
                allowMultiple = True,
                defaultValue = [2,4]
            )
        )

        # OUTPUT
        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT,
                self.tr('Nearest points', 'Pontos mais próximos')
            )
        )

    def processAlgorithm(self, parameters, context, feedback):

        # Camada de pontos de referência
        ref = self.parameterAsSource(
            parameters,
            self.REF,
            context
        )
        if ref is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.REF))
        SRC = ref.sourceCrs()

        # Camada de pontos aleatorios
        pnts = self.parameterAsSource(
            parameters,
            self.PNTS,
            context
        )
        if pnts is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.PNTS))
        possuiZ = True if pnts.wkbType() == QgsWkbTypes.PointZ else False

        campo = self.parameterAsFields(
            parameters,
            self.FIELD,
            context
        )
        nome_campo = campo[0]

        stats = self.parameterAsEnums(
            parameters,
            self.STATS,
            context
        )

        # Condição
        cond = self.parameterAsEnum(
            parameters,
            self.COND,
            context
        )

        # distância máxima em metros
        dist = self.parameterAsDouble(
            parameters,
            self.DIST,
            context
        )

        # quantidade mínima de pontos
        qnt = self.parameterAsInt(
            parameters,
            self.QNT,
            context
        )

        # OUTPUT
        itens  = {
             self.tr('count', 'contagem'): QVariant.Int,
             'std_x' : QVariant.Double,
             'std_y' : QVariant.Double,
             }
        if possuiZ:
            itens['std_z'] = QVariant.Double

        Fields = ref.fields()
        for item in itens:
            Fields.append(QgsField(item, itens[item]))

        if campo:
            for st in stats:
                Fields.append(QgsField(nome_campo + '_' + self.OPTIONS[st], QVariant.Double))

        (sink, dest_id) = self.parameterAsSink(
            parameters,
            self.OUTPUT,
            context,
            Fields,
            QgsWkbTypes.MultiPointZ if possuiZ else QgsWkbTypes.MultiPoint,
            SRC
        )
        if sink is None:
            raise QgsProcessingException(self.invalidSinkError(parameters, self.OUTPUT))

        # Transformação de SRC das camadas
        mesmoSRC = True
        if ref.sourceCrs() != pnts.sourceCrs():
            mesmoSRC = False
            coordinateTransformer = QgsCoordinateTransform()
            coordinateTransformer.setDestinationCrs(ref.sourceCrs())
            coordinateTransformer.setSourceCrs(pnts.sourceCrs())

        # Pegar latitude média da extensão da camada de referência
        if not SRC.isGeographic():
            GRS = QgsCoordinateReferenceSystem(SRC.geographicCrsAuthId())
            transf_layer = QgsCoordinateTransform()
            transf_layer.setDestinationCrs(GRS)
            transf_layer.setSourceCrs(SRC)
            geom = QgsGeometry.fromPointXY(ref.sourceExtent().center())
            geom.transform(coordinateTransformer)
            pnt = geom.asPoint()
            lat = pnt.y()
        else:
            lat = ref.sourceExtent().center().y()

        if SRC.isGeographic():
            dist = meters2degrees(dist, lat, SRC)

        def distancia2D (pnt1, pnt2):
            return np.sqrt((pnt1.x() - pnt2.x())**2 + (pnt1.y() - pnt2.y())**2)

        dtype = [('id', int),('dist',float)]

        # Colocar camada de pontos em dicionário
        dic = {}
        for feat in pnts.getFeatures():
            dic[feat.id()] = feat

        cont = 0
        total = ref.featureCount()
        total = 100.0/total if total else 0
        for cont, feat1 in enumerate(ref.getFeatures()):
            geom1 = feat1.geometry()
            pnt1 = geom1.asPoint()
            valores = []
            # Calculando distâncias
            for feat2 in pnts.getFeatures():
                geom2 = feat2.geometry()
                if not mesmoSRC:
                    geom2.transform(coordinateTransformer)
                pnt2 = geom2.asPoint()
                dist2D = distancia2D (pnt1, pnt2)
                valores += [(feat2.id(), dist2D)]
            # Ordenando valores
            estr = np.array(valores, dtype=dtype)
            ordenado = np.sort(estr, order=['dist'])
            # Selecionando pontos
            if cond == 0: # Condição 1 - Distância máxima
                IDS = []
                for item in ordenado:
                    IDS += [item[0]]
                    if item[-1] > dist:
                        break
            elif cond == 1: # Condição 2 - Quantidade mínima de pontos
                IDS = []
                for k in range(qnt):
                    IDS += [ordenado[k][0]]
            elif cond == 2: # Condição 3 - Ambas
                IDS = []
                cont = 0
                for item in ordenado:
                    cont += 1
                    if cont > qnt:
                        break
                    else:
                        if item[-1] <= dist:
                            IDS += [item[0]]
                        else:
                            break

            if len(IDS) > 0:
                # Calcular estatísticas
                X, Y, Z = [],[],[]
                atributos = []
                for ID in IDS:
                    pnt = dic[ID].geometry().constGet()
                    if possuiZ:
                        x, y, z = pnt.x(), pnt.y(), pnt.z()
                        X.append(x)
                        Y.append(y)
                        Z.append(z)
                    else:
                        x, y = pnt.x(), pnt.y()
                        X.append(x)
                        Y.append(y)
                    atributos.append(dic[ID][nome_campo])

                sigmaX = np.std(np.array(X))
                sigmaY = np.std(np.array(Y))
                if SRC.isGeographic():
                    sigmaX = degrees2meters(sigmaX, lat, SRC)
                    sigmaY = degrees2meters(sigmaY, lat, SRC)
                if possuiZ:
                   sigmaZ = np.std(np.array(Z))

                atributos = np.array(atributos)
                lista_stats = []
                if campo:
                    for st in stats:
                        if self.OPTIONS[st] == 'count':
                            lista_stats += [int(len(atributos))]
                        if self.OPTIONS[st] == 'sum':
                            lista_stats += [float(atributos.sum())]
                        if self.OPTIONS[st] == 'mean':
                            lista_stats += [float(atributos.mean())]
                        if self.OPTIONS[st] == 'median':
                            lista_stats += [float(np.median(atributos))]
                        if self.OPTIONS[st] == 'std':
                            lista_stats += [float(atributos.std())]
                        if self.OPTIONS[st] == 'min':
                            lista_stats += [float(atributos.min())]
                        if self.OPTIONS[st] == 'max':
                            lista_stats += [float(atributos.max())]

                # Criar feição multiponto
                geom = QgsGeometry(dic[IDS[0]].geometry())
                for ID in IDS[1:]:
                    geom0  = dic[ID].geometry()
                    geom = geom.combine(geom0) # adicinar pontos

                feat = QgsFeature(Fields)
                feat.setGeometry(geom)

                att = feat1.attributes() + [len(IDS), float(sigmaX), float(sigmaY)] + [float(sigmaZ)] if possuiZ else []
                att += lista_stats
                feat.setAttributes(att)
                sink.addFeature(feat, QgsFeatureSink.FastInsert)
            if feedback.isCanceled():
                break
            feedback.setProgress(int((cont+1) * total))

        feedback.pushInfo(self.tr('Operation completed successfully!', 'Operação finalizada com sucesso!'))
        feedback.pushInfo(self.tr('Leandro Franca - Cartographic Engineer', 'Leandro França - Eng Cart'))

        return {self.OUTPUT: dest_id}
