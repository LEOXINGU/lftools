# -*- coding: utf-8 -*-

"""
Cad_PolygonOrientation.py
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
__date__ = '2022-01-05'
__copyright__ = '(C) 2021, Leandro França'

from PyQt5.QtCore import *
from qgis.core import *
from lftools.geocapt.imgs import Imgs
from lftools.geocapt.cartography import areaGauss, geom2PointList, OrientarPoligono
import os
from qgis.PyQt.QtGui import QIcon


class PolygonOrientation(QgsProcessingAlgorithm):

    POLYGONS = 'POLYGONS'
    ORIENTATION = 'ORIENTATION'
    FIRST = 'FIRST'
    SAVE = 'SAVE'
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
        return PolygonOrientation()

    def name(self):
        return 'polygonorientation'

    def displayName(self):
        return self.tr('Orient polygons', 'Orientar polígonos')

    def group(self):
        return self.tr('Cadastre', 'Cadastro')

    def groupId(self):
        return 'cadastro'

    def tags(self):
        return self.tr('cadastre,clockwise,counterclockwise,oriented,orientation,northmost,ordenar').split(',')

    def icon(self):
        return QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images/cadastre.png'))

    txt_en = 'This tool orients the geometry of polygon-like features clockwise or counterclockwise, defining the first vertex as the north, south, east, or west.'
    txt_pt = 'Esta ferramenta orienta a geometria de feições do tipo polígono no sentido horário ou antihorário, definindo o primeiro vértice mais ao norte, sul, leste ou oeste.'
    figure = 'images/tutorial/vect_orient_polygon.jpg'

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
            QgsProcessingParameterVectorLayer(
                self.POLYGONS,
                self.tr('Polygon layer', 'Camada de Polígonos'),
                [QgsProcessing.TypeVectorPolygon]
            )
        )

        orient = [self.tr('Clockwise','Horário'),
				  self.tr('Counterclockwise','Anti-horário'),
				  self.tr('Do not change','Não alterar')
               ]

        self.addParameter(
            QgsProcessingParameterEnum(
                self.ORIENTATION,
                self.tr('Orientation', 'Orientação'),
				options = orient,
                defaultValue= 0
            )
        )

        opcoes = [self.tr('Polygon sequence (do not change)','Sequência do polígono (não alterar)'),
				  self.tr('Northmost','Mais ao Norte'),
				  self.tr('Southernmost','Mais ao Sul'),
				  self.tr('Eastmost','Mais ao Leste'),
				  self.tr('Westmost','Mais ao Oeste')
               ]

        self.addParameter(
            QgsProcessingParameterEnum(
                self.FIRST,
                self.tr('First point', 'Primeiro Ponto'),
				options = opcoes,
                defaultValue= 1
            )
        )

        self.addParameter(
            QgsProcessingParameterBoolean(
                self.SAVE,
                self.tr('Save Editions', 'Salvar Edições'),
                defaultValue=False
            )
        )


    def processAlgorithm(self, parameters, context, feedback):
        # INPUT
        camada = self.parameterAsVectorLayer(
            parameters,
            self.POLYGONS,
            context
        )
        if camada is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.POLYGONS))

        sentido = self.parameterAsEnum(
            parameters,
            self.ORIENTATION,
            context
        )
        if sentido is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.ORIENTATION))

        primeiro = self.parameterAsEnum(
            parameters,
            self.FIRST,
            context
        )

        salvar = self.parameterAsBool(
            parameters,
            self.SAVE,
            context
        )
        if salvar is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.SAVE))

        camada.startEditing() # coloca no modo edição

        total = 100.0 / camada.featureCount() if camada.featureCount() else 0

        for current, feat in enumerate(camada.getFeatures()):
            geom = feat.geometry()
            if geom.isMultipart():
                poligonos = geom2PointList(geom)
                mPol = QgsMultiPolygon()
                for pol in poligonos:
                    coords = pol[0]
                    coords = coords[:-1]
                    coords = OrientarPoligono(coords, primeiro, sentido)
                    anel = QgsLineString(coords)
                    pol = QgsPolygon(anel)
                    mPol.addGeometry(pol)
                newGeom = QgsGeometry(mPol)
            else:
                coords = geom2PointList(geom)[0]
                coords = coords[:-1]
                coords = OrientarPoligono(coords, primeiro, sentido)
                anel = QgsLineString(coords)
                pol = QgsPolygon(anel)
                newGeom = QgsGeometry(pol)

            camada.changeGeometry(feat.id(), newGeom)

            if feedback.isCanceled():
                break
            feedback.setProgress(int((current+1) * total))

        if salvar:
            camada.commitChanges() # salva as edições

        feedback.pushInfo(self.tr('Operation completed successfully!', 'Operação finalizada com sucesso!'))
        feedback.pushInfo(self.tr('Leandro França - Cartographic Engineer', 'Leandro França - Eng Cart'))
        return {}
