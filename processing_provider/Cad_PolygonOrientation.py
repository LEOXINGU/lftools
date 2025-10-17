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

from qgis.core import *
from lftools.geocapt.imgs import Imgs
from lftools.translations.translate import translate
from lftools.geocapt.cartography import areaGauss, geom2PointList, OrientarPoligono
import os
from qgis.PyQt.QtGui import QIcon


class PolygonOrientation(QgsProcessingAlgorithm):

    POLYGONS = 'POLYGONS'
    ORIENTATION = 'ORIENTATION'
    FIRST = 'FIRST'
    SAVE = 'SAVE'
    STREET = 'STREET'
    SELECTED = 'SELECTED'
    LOC = QgsApplication.locale()[:2]

    def tr(self, *string):
        return translate(string, self.LOC)

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
        return 'GeoOne,cadastre,clockwise,counterclockwise,oriented,orientation,northmost,ordenar'.split(',')

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

        self.addParameter(
            QgsProcessingParameterBoolean(
                self.SELECTED,
                self.tr('Only selected', 'Apenas selecionados'),
                defaultValue= False
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
                self.STREET,
                self.tr('First vertex with forefront bordering the street','Primeiro vértice com vante confrontando o sistema viário'),
                defaultValue = False
            )
        )

        self.addParameter(
            QgsProcessingParameterBoolean(
                self.SAVE,
                self.tr('Save Editions', 'Salvar Edições'),
                defaultValue = False
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

        selecionados = self.parameterAsBool(
            parameters,
            self.SELECTED,
            context
        )

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

        rua = self.parameterAsBool(
            parameters,
            self.STREET,
            context
        )
        if rua is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.STREET))

        salvar = self.parameterAsBool(
            parameters,
            self.SAVE,
            context
        )
        if salvar is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.SAVE))

        camada.startEditing() # coloca no modo edição

        feedback.pushInfo(self.tr('Orienting polygons...', 'Orientando polígonos...'))

        total = 100.0 / camada.featureCount() if camada.featureCount() else 0

        for current, feat in enumerate(camada.getSelectedFeatures() if selecionados else camada.getFeatures()):

            geom = feat.geometry()
            if geom.isEmpty() or geom is None:
                continue
            else:
                if geom.isMultipart():
                    multipol = geom2PointList(geom)  # lista de polígonos (com anéis)
                    mPol = QgsMultiPolygon()

                    for pol in multipol:
                        if not pol:  # segurança contra geometria vazia
                            continue

                        # Anel exterior
                        ext_coords = pol[0][:-1]
                        ext_coords = OrientarPoligono(ext_coords, primeiro, sentido)
                        ext_ring = QgsLineString(ext_coords)
                        qgs_pol = QgsPolygon(ext_ring)

                        # Anéis internos
                        for ring in pol[1:]:
                            int_coords = ring[:-1]
                            int_coords = OrientarPoligono(int_coords, primeiro, sentido)
                            int_ring = QgsLineString(int_coords)
                            qgs_pol.addInteriorRing(int_ring)

                        mPol.addGeometry(qgs_pol)

                    newGeom = QgsGeometry(mPol)

                else:
                    pol = geom2PointList(geom)
                    if not pol:
                        continue
                    ext_coords = pol[0][:-1]
                    ext_coords = OrientarPoligono(ext_coords, primeiro, sentido)
                    ext_ring = QgsLineString(ext_coords)
                    qgs_pol = QgsPolygon(ext_ring)

                    for ring in pol[1:]:
                        int_coords = ring[:-1]
                        int_coords = OrientarPoligono(int_coords, primeiro, sentido)
                        int_ring = QgsLineString(int_coords)
                        qgs_pol.addInteriorRing(int_ring)

                    newGeom = QgsGeometry(qgs_pol)

                camada.changeGeometry(feat.id(), newGeom)

                if feedback.isCanceled():
                    break
                feedback.setProgress(int((current+1) * total))

            if rua:
                feedback.pushInfo(self.tr('Identifying the first forward point for road access...', 'Identificando primeiro ponto com vante para o acesso viário...'))
                for feat1 in camada.getSelectedFeatures() if selecionados else camada.getFeatures():
                    # Pegar vizinhos
                    geom1 = feat1.geometry()
                    if not geom1.isMultipart():
                        COORDS = geom2PointList(geom1)[0]
                        COORDS  = COORDS[:-1]
                        coords = geom1.asPolygon()[0]
                        coords = coords[:-1]
                        confront = {}
                        for feat2 in camada.getSelectedFeatures() if selecionados else camada.getFeatures():
                            geom2 = feat2.geometry()
                            cd_lote2 = feat2.id()
                            if feat1 != feat2:
                                if geom1.intersects(geom2):
                                    inters = geom1.intersection(geom2)
                                    if inters.isMultipart():
                                        partes = inters.asMultiPolyline()
                                        parte1 = QgsGeometry.fromPolylineXY(partes[0])
                                        k = 1
                                        cont = 1
                                        while len(partes) > 1:
                                            # print(k, cont, len(partes), parte1)
                                            parte2 = QgsGeometry.fromPolylineXY(partes[k])
                                            if  parte1.intersects(parte2):
                                                parte1 = parte1.combine(parte2)
                                                del partes[k]
                                            else:
                                                k += 1
                                            cont +=1
                                            if cont > 10:
                                                # print('erro no loop',cont)
                                                break
                                        inters = parte1
                                    confront[feat2.id()] = [cd_lote2, inters]

                        lista = []
                        # Fazer um teste para todos os pontos (sim ou não)
                        vante = []
                        for pnt in coords:
                            geom1 = QgsGeometry.fromPointXY(pnt)
                            for item in confront:
                                geom2 = confront[item][1]
                                if geom2.type() == 1 and geom1.intersects(geom2): #Line
                                    coord_lin = geom2.asPolyline()
                                    if pnt != coord_lin[-1]:
                                        vante += [True]
                                        break
                            else:
                                vante += [False]

                        for k in range(len(vante)):
                            anterior = vante[k-1 if k-1 > 0 else -1]
                            posterior = vante[k]
                            if anterior and not posterior:
                                ind = k
                                COORDS = COORDS[ind :] + COORDS[0 : ind]
                                break

                        anel = QgsLineString(COORDS)
                        pol = QgsPolygon(anel)
                        newGeom = QgsGeometry(pol)
                        ok = camada.changeGeometry(feat1.id(), newGeom)

        if salvar:
            camada.commitChanges() # salva as edições

        feedback.pushInfo(self.tr('Operation completed successfully!', 'Operação finalizada com sucesso!'))
        feedback.pushInfo(self.tr('Leandro França - Cartographic Engineer', 'Leandro França - Eng Cart'))
        return {}
