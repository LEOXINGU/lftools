# -*- coding: utf-8 -*-

"""
Vect_PolygonOrientation.py
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
from lftools.geocapt.cartography import areaGauss
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
        return self.tr('Vector', 'Vetor')

    def groupId(self):
        return 'vector'

    def tags(self):
        return self.tr('cadastre,clockwise,counterclockwise,oriented,orientation,northmost').split(',')

    def icon(self):
        return QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images/vetor.png'))

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

        opcoes = [self.tr('Polygon sequence','Sequência do polígono'),
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
                coords = geom.asMultiPolygon()[0][0]
            else:
                coords = geom.asPolygon()[0]
            coords = coords[:-1]

            # definir primeiro vértice
            if primeiro == 1: # Mais ao norte
                ind = None
                ymax = -1e10
                x_ymax = 1e10
                for k, pnt in enumerate(coords):
                    if pnt.y() > ymax:
                        ymax = pnt.y()
                        x_ymax = pnt.x()
                        ind = k
                    elif pnt.y() == ymax:
                        if pnt.x() < x_ymax:
                            ymax = pnt.y()
                            x_ymax = pnt.x()
                            ind = k

            elif primeiro == 2: # Mais ao sul
                ind = None
                ymin = 1e10
                x_ymim = -1e10
                for k, pnt in enumerate(coords):
                    if pnt.y() < ymin:
                        ymin = pnt.y()
                        x_ymim = pnt.x()
                        ind = k
                    elif pnt.y() == ymin:
                        if pnt.x() > x_ymim:
                            ymin = pnt.y()
                            x_ymim = pnt.x()
                            ind = k

            elif primeiro == 3: # Mais ao Leste
                ind = None
                xmax = -1e10
                for k, pnt in enumerate(coords):
                    if pnt.x() > xmax:
                        xmax = pnt.x()
                        ind = k

            elif primeiro == 4: # Mais ao Oeste
                ind = None
                xmin = 1e10
                for k, pnt in enumerate(coords):
                    if pnt.x() < xmin:
                        xmin = pnt.x()
                        ind = k

            if primeiro != 0:
                coords = coords[ind :] + coords[0 : ind]

            #rotacionar
            coords = coords +[coords[0]]
            areaG = areaGauss(coords)
            if areaG < 0 and sentido == 0:
                coords = coords[::-1]
            elif areaG > 0 and sentido == 1:
                coords = coords[::-1]

            if geom.isMultipart():
                newGeom = QgsGeometry.fromMultiPolygonXY([[coords]])
            else:
                newGeom = QgsGeometry.fromPolygonXY([coords])

            camada.changeGeometry(feat.id(), newGeom)

            if feedback.isCanceled():
                break
            feedback.setProgress(int((current+1) * total))

        if salvar:
            camada.commitChanges() # salva as edições

        feedback.pushInfo(self.tr('Operation completed successfully!', 'Operação finalizada com sucesso!'))
        feedback.pushInfo(self.tr('Leandro França - Cartographic Engineer', 'Leandro França - Eng Cart'))
        return {}
