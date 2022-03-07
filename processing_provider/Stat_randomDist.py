# -*- coding: utf-8 -*-

"""
Stat_randomDist.py
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
__date__ = '2020-12-04'
__copyright__ = '(C) 2020, Leandro França'

from PyQt5.QtCore import QCoreApplication, QVariant
from qgis.core import (QgsProcessing,
                       QgsFeatureSink,
                       QgsWkbTypes,
                       QgsFields,
                       QgsField,
                       QgsFeature,
                       QgsPointXY,
                       QgsGeometry,
                       QgsProcessingException,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterPoint,
                       QgsProcessingParameterNumber,
                       QgsProcessingParameterString,
                       QgsProcessingParameterField,
                       QgsProcessingParameterBoolean,
                       QgsProcessingParameterCrs,
                       QgsProcessingParameterEnum,
                       QgsFeatureRequest,
                       QgsExpression,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterFeatureSink,
                       QgsProcessingParameterFileDestination,
                       QgsApplication,
                       QgsProject,
                       QgsCoordinateTransform,
                       QgsCoordinateReferenceSystem)
import numpy as np
from numpy import cos, sin
from lftools.geocapt.imgs import Imgs
import os
from qgis.PyQt.QtGui import QIcon


class RandomDist(QgsProcessingAlgorithm):

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
        return RandomDist()

    def name(self):
        return 'randomdist'

    def displayName(self):
        return self.tr('Gaussian random points', 'Pontos aleatórios gaussiano')

    def tags(self):
        return self.tr('gaussian,random,distribution,normal,mean,variance').split(',')

    def group(self):
        return self.tr('Spatial Statistics', 'Estatística Espacial')

    def groupId(self):
        return 'spatialstatistics'

    def tags(self):
        return self.tr('random,gauss,confidence,deviational,standard,tendency,dispertion,directional,trend,confidence,covariance,mvc').split(',')

    def icon(self):
        return QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images/statistics.png'))

    txt_en = 'Generate gaussian (normal) random points in 2D space with a given mean position (X0, Y0), standard deviation for X and Y, and rotation angle.'
    txt_pt = 'Gera pontos aleatórios no espaço 2D a partir de um ponto central (X0, Y0), desvios-padrões para X e Y, e ângulo de rotação.'
    figure = 'images/tutorial/stat_random_points.jpg'

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

    ORIGIN = 'ORIGIN'
    STDX = 'STDX'
    STDY = 'STDY'
    ROTATION = 'ROTATION'
    NPOINTS = 'NPOINTS'
    OUTPUT = 'OUTPUT'
    CRS = 'CRS'

    def initAlgorithm(self, config=None):
        # INPUT
        self.addParameter(
            QgsProcessingParameterPoint(
                self.ORIGIN,
                self.tr('Origin Point', 'Ponto de Origem'),
                defaultValue= QgsPointXY(0,0)
                )
            )

        self.addParameter(
            QgsProcessingParameterNumber(
                self.STDX,
                self.tr('Standard Deviation for X', 'Desvio-padrão para X'),
                type =1,
                defaultValue = 2
                )
            )

        self.addParameter(
            QgsProcessingParameterNumber(
                self.STDY,
                self.tr('Standard Deviation for Y', 'Desvio-padrão para Y'),
                type =1,
                defaultValue = 1
                )
            )

        self.addParameter(
            QgsProcessingParameterNumber(
                self.ROTATION,
                self.tr('Rotation Angle', 'Ângulo de Rotação'),
                type =1,
                defaultValue = 45
                )
            )

        self.addParameter(
            QgsProcessingParameterNumber(
                self.NPOINTS,
                self.tr('Number of Points', 'Número de Pontos'),
                type =0,
                minValue = 2,
                defaultValue = 100
                )
            )

        self.addParameter(
            QgsProcessingParameterCrs(
                self.CRS,
                self.tr('CRS', 'SRC'),
                'ProjectCrs'))

        # OUTPUT
        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT,
                self.tr('Gaussian Random Points', 'Pontos Aleatórios Gaussiano')
            )
        )

    def processAlgorithm(self, parameters, context, feedback):

        ponto = self.parameterAsPoint(
            parameters,
            self.ORIGIN,
            context
        )
        if ponto is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.ORIGIN))

        sigmaX = self.parameterAsDouble(
            parameters,
            self.STDX,
            context
        )
        if sigmaX is None or sigmaX<=0:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.STDX))

        sigmaY = self.parameterAsDouble(
            parameters,
            self.STDY,
            context
        )
        if sigmaY is None or sigmaY<=0:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.STDY))

        n_pnts = self.parameterAsInt(
            parameters,
            self.NPOINTS,
            context
        )
        if n_pnts is None or n_pnts<1:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.NPOINTS))

        angle = self.parameterAsDouble(
            parameters,
            self.ROTATION,
            context
        )
        if angle is None or angle<-180 or angle>=180:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.ROTATION))

        CRS = self.parameterAsCrs(
            parameters,
            self.CRS,
            context
        )

        x0 = ponto.x()
        y0 = ponto.y()
        phi = np.radians(angle)

        x = np.random.normal(loc=0, scale=sigmaX, size=n_pnts)
        y = np.random.normal(loc=0, scale=sigmaY, size=n_pnts)

        # Rotation
        M1 = np.matrix([x, y])
        rot = np.matrix([[cos(phi), -sin(phi)], [sin(phi), cos(phi)]])
        M2 = rot*M1
        x_rot = M2[0]+x0
        y_rot = M2[1]+y0

        # OUTPUT
        GeomType = QgsWkbTypes.Point
        Fields = QgsFields()
        itens  = {
             'id' : QVariant.Int,
             }
        for item in itens:
            Fields.append(QgsField(item, itens[item]))
        (sink, dest_id) = self.parameterAsSink(
            parameters,
            self.OUTPUT,
            context,
            Fields,
            GeomType,
            CRS
        )
        if sink is None:
            raise QgsProcessingException(self.invalidSinkError(parameters, self.OUTPUT))

        total = 100.0 /n_pnts if n_pnts else 0
        for k in range(n_pnts):
            x = float(x_rot[0,k])
            y = float(y_rot[0,k])
            feat = QgsFeature()
            geom = QgsGeometry.fromPointXY(QgsPointXY(x,y))
            att = [k+1]
            feat.setGeometry(geom)
            feat.setAttributes(att)
            sink.addFeature(feat, QgsFeatureSink.FastInsert)
            if feedback.isCanceled():
                break
            feedback.setProgress(int((k+1) * total))

        feedback.pushInfo(self.tr('Operation completed successfully!', 'Operação finalizada com sucesso!'))
        feedback.pushInfo(self.tr('Leandro Franca - Cartographic Engineer', 'Leandro França - Eng Cart'))

        return {self.OUTPUT: dest_id}
