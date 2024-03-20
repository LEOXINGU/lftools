# -*- coding: utf-8 -*-

"""
Gnss_RTKCorrection.py
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
                       QgsProcessingParameterPoint,
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
                       QgsCoordinateReferenceSystem,
                       QgsCoordinateTransform,
                       QgsPointXY,
                       QgsProject,
                       QgsRasterLayer,
                       QgsCoordinateTransform,
                       QgsProcessingLayerPostProcessorInterface,
                       QgsCoordinateReferenceSystem)

from lftools.geocapt.imgs import Imgs
from lftools.geocapt.cartography import raioMedioGauss
from numpy import sqrt
from lftools.geocapt.topogeo import geod2geoc, geoc2geod
from pyproj.crs import CRS
from datetime import datetime
import codecs
import os
from qgis.PyQt.QtGui import QIcon


class RTKCorrection(QgsProcessingAlgorithm):

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
        return RTKCorrection()

    def name(self):
        return 'rtkcorrection'

    def displayName(self):
        return self.tr('RTK Points Correction', 'Correção de Pontos RTK')

    def group(self):
        return self.tr('GNSS')

    def groupId(self):
        return 'gnss'

    def tags(self):
        return self.tr('gps,position,ibge,ppp,ppk,navigation,satellites,surveying,rinex,glonass,beidou,compass,galileu,track,kinematic,rtk,ntrip,static,real').split(',')

    def icon(self):
        return QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images/satellite.png'))

    txt_en = '''Performs base RTK correction using post-process coordinates, for example by PPP, and applies corrections to all rover points.'''
    txt_pt = '''Realiza a correção da base RTK utilizando as coordenas pós-processsas, por exemplo pelo PPP, e aplica as correções a todos os pontos Rover.'''

    figure = 'images/tutorial/gnss_rtk_correction.jpg'

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

    BASE = 'BASE'
    ALTITUDE_INI = 'ALTITUDE_INI'
    PPP = 'PPP'
    ALTITUDE_END = 'ALTITUDE_END'
    INPUT = 'INPUT'
    OUTPUT = 'OUTPUT'

    def initAlgorithm(self, config=None):

        # INPUT
        self.addParameter(
            QgsProcessingParameterPoint(
                self.BASE,
                self.tr('Initial X,Y coordinates of the base', 'Coordenadas X,Y iniciais da base'),
                defaultValue = QgsPointXY(0.0, 0.0)
            )
        )

        self.addParameter(
            QgsProcessingParameterNumber(
                self.ALTITUDE_INI,
                self.tr('Initial Z coordinate of the base (m)', 'Coordenada Z inicial da base (m)'),
                type = QgsProcessingParameterNumber.Type.Double,
                )
            )

        self.addParameter(
            QgsProcessingParameterPoint(
                self.PPP,
                self.tr('Post-processed X,Y coordinates of the base', 'Coordenadas X,Y pós-processadas da base'),
                defaultValue = QgsPointXY(0.0, 0.0)
            )
        )

        self.addParameter(
            QgsProcessingParameterNumber(
                self.ALTITUDE_END,
                self.tr('Post-processed Z coordinate of the base (m)', 'Coordenada Z pós-processada da base (m)'),
                type = QgsProcessingParameterNumber.Type.Double,
                )
            )

        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT,
                self.tr('GNSS RTK Point Layer', 'Camada de Pontos GNSS RTK'),
                [QgsProcessing.TypeVectorPoint]
            )
        )

        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT,
                self.tr('Adjusted RTK points', 'Pontos RTK corrigidos')
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
        if layer.wkbType() != QgsWkbTypes.PointZ:
            raise QgsProcessingException(self.tr('Input points layer must be of type PointZ!', 'Camada de pontos de entrada deve ser do tipo PointZ!'))

        # Transformação para o SGR da camada
        SRC = layer.sourceCrs()
        GRS = QgsCoordinateReferenceSystem(SRC.geographicCrsAuthId())
        transf_layer = QgsCoordinateTransform()
        transf_layer.setDestinationCrs(GRS)
        transf_layer.setSourceCrs(SRC)

        ProjectCRS = QgsProject.instance().crs()
        transf_pnt = QgsCoordinateTransform()
        transf_pnt.setDestinationCrs(GRS)
        transf_pnt.setSourceCrs(ProjectCRS)

        base = self.parameterAsPoint(
            parameters,
            self.BASE,
            context
        )

        z_ini = self.parameterAsDouble(
            parameters,
            self.ALTITUDE_INI,
            context
        )

        base = QgsGeometry(QgsPoint(base.x(), base.y(), z_ini))
        base.transform(transf_pnt)

        ppp = self.parameterAsPoint(
            parameters,
            self.PPP,
            context
        )

        z_fim = self.parameterAsDouble(
            parameters,
            self.ALTITUDE_END,
            context
        )

        ppp = QgsGeometry(QgsPoint(ppp.x(), ppp.y(), z_fim))
        ppp.transform(transf_pnt)


        (sink, dest_id) = self.parameterAsSink( parameters, self.OUTPUT, context, layer.fields(), QgsWkbTypes.PointZ, GRS)
        if sink is None:
            raise QgsProcessingException(self.invalidSinkError(parameters, self.OUTPUT))


        # Parâmetros a e f do elipsoide
        EPSG = int(GRS.authid().split(':')[-1]) # pegando o EPGS do SRC do QGIS
        proj_crs = CRS.from_epsg(EPSG) # transformando para SRC do pyproj
        a = proj_crs.ellipsoid.semi_major_metre
        f_inv = proj_crs.ellipsoid.inverse_flattening
        f = 1/f_inv
        feedback.pushInfo((self.tr('Semi major axis: {}', 'Semi-eixo maior: {}')).format(str(a)))
        feedback.pushInfo((self.tr('Inverse flattening: {}', 'Achatamento (inverso): {}')).format(str(f_inv)))

        # Cálculo das Deltas Geocêntricos
        pnt_ini = base.constGet()
        X_ini, Y_ini, Z_ini = geod2geoc(pnt_ini.x(), pnt_ini.y(), pnt_ini.z(), a, f)

        pnt_fim = ppp.constGet()
        X_fim, Y_fim, Z_fim = geod2geoc(pnt_fim.x(), pnt_fim.y(), pnt_fim.z(), a, f)

        delta_X = X_fim - X_ini
        delta_Y = Y_fim - Y_ini
        delta_Z = Z_fim - Z_ini
        DELTA = sqrt(delta_X**2 + delta_Y**2 + delta_Z**2)
        feedback.pushInfo((self.tr('Geocentric delta X: {:.4f} m', 'Delta geocêntrico em X: {:.4f} m')).format(delta_X))
        feedback.pushInfo((self.tr('Geocentric delta Y: {:.4f} m', 'Delta geocêntrico em Y: {:.4f} m')).format(delta_Y))
        feedback.pushInfo((self.tr('Geocentric delta Z: {:.4f} m', 'Delta geocêntrico em Z: {:.4f} m')).format(delta_Z))
        feedback.pushInfo((self.tr('Geocentric Delta 3D: {:.4f} m', 'Delta geocêntrico total (3D): {:.4f} m')).format(DELTA))

        # Aplicação das correções  na camada de pontos
        total = 100.0 / layer.featureCount() if layer.featureCount() else 0
        feature = QgsFeature()
        for current, feat in enumerate(layer.getFeatures()):
            geom = feat.geometry()
            geom.transform(transf_layer)
            pnt = geom.constGet()
            X, Y, Z = geod2geoc(pnt.x(), pnt.y(), pnt.z(), a, f)
            X_novo = X + delta_X
            Y_novo = Y + delta_Y
            Z_novo = Z + delta_Z
            lon, lat, h = geoc2geod(X_novo, Y_novo, Z_novo, a, f)

            new_geom = QgsGeometry(QgsPoint(lon, lat, h))
            feature.setGeometry(new_geom)
            feature.setAttributes( feat.attributes() )
            sink.addFeature(feature, QgsFeatureSink.FastInsert)

            if feedback.isCanceled():
                break
            feedback.setProgress(int((current+1) * total))


        feedback.pushInfo(self.tr('Operation completed successfully!', 'Operação finalizada com sucesso!'))
        feedback.pushInfo(self.tr('Leandro Franca - Cartographic Engineer', 'Leandro França - Eng Cart'))

        return {self.OUTPUT: dest_id}
