# -*- coding: utf-8 -*-

"""
Doc_ValidateTopology.py
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
__date__ = '2023-08-22'
__copyright__ = '(C) 2023, Leandro França'

from qgis.PyQt.QtCore import QCoreApplication, QVariant
from qgis.core import (QgsProcessing,
                       QgsApplication,
                       QgsProcessingParameterString,
                       QgsProcessingParameterCrs,
                       QgsProcessingParameterBoolean,
                       QgsFields,
                       QgsWkbTypes,
                       QgsField,
                       QgsFeature,
                       QgsGeometry,
                       QgsPointXY,
                       QgsFeatureSink,
                       QgsProcessingException,
                       QgsProcessingAlgorithm,
                       QgsFeatureRequest,
                       QgsProcessingUtils,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterFeatureSink)
import re, os
from lftools.geocapt.imgs import *
from lftools.translations.translate import translate
from lftools.geocapt.topogeo import dd2dms, dd2dms
from lftools.geocapt.cartography import LabelConf, SymbolSimplePoint
from qgis.PyQt.QtGui import QIcon
import numpy as np

class ValidateTopology(QgsProcessingAlgorithm):

    LOC = QgsApplication.locale()[:2]

    def tr(self, *string):
        return translate(string, self.LOC)

    def createInstance(self):
        return ValidateTopology()

    def name(self):
        return 'ValidateTopology'.lower()

    def displayName(self):
        return self.tr('Validate topology', 'Validar topologia')

    def group(self):
        return self.tr('Documents', 'Documentos')

    def groupId(self):
        return 'documents'

    def tags(self):
        return self.tr('validate,validar,topology,topologia,contains,contém,aggregate,vertex,duplicate,connect,conectividade,topografia,imóvel,memorial,deed description').split(',')

    def icon(self):
        return QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images/document.png'))

    txt_en = "This tool performs a series of topological validations to ensure the correct generation of survey plans and deed description based on GeoOne's <b>TopoGeo</b> and <b>GeoRural</b> models."
    txt_pt = "Esta ferramenta executa uma série de validações topológicas para garantir a correta geração de plantas topográficas e memoriais descritivos baseado nos modelos <b>TopoGeo</b> e <b>GeoRural</b> da GeoOne."
    figure = 'images/tutorial/doc_validation.jpg'

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

    POINT = 'POINT'
    LINE = 'LINE'
    POLYGON = 'POLYGON'
    OUTPUT = 'OUTPUT'

    def initAlgorithm(self, config=None):

        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.POINT,
                self.tr('Vertices (points)', 'Vértices (pontos)'),
                [QgsProcessing.TypeVectorPoint]
            )
        )

        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.LINE,
                self.tr('Limits (lines)', 'Limites (linhas)'),
                [QgsProcessing.TypeVectorLine]
            )
        )

        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.POLYGON,
                self.tr('Area (polygon)', 'Área (polígono)'),
                [QgsProcessing.TypeVectorPolygon]
            )
        )

        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT,
                self.tr('Topology errors','Erros de topologia')
            )
        )


    def processAlgorithm(self, parameters, context, feedback):

        vertices = self.parameterAsSource(parameters, self.POINT, context)
        limites = self.parameterAsSource(parameters, self.LINE, context)
        context.setInvalidGeometryCheck(QgsFeatureRequest.GeometryNoCheck)
        area = self.parameterAsSource(parameters, self.POLYGON, context)

        Fields = QgsFields()
        itens  = {
                     'ord' : QVariant.Int,
                     'feat_id': QVariant.Int,
                     self.tr('type','tipo') : QVariant.String,
                     }
        for item in itens:
            Fields.append(QgsField(item, itens[item]))

        (sink, dest_id) = self.parameterAsSink(
            parameters,
            self.OUTPUT,
            context,
            Fields,
            QgsWkbTypes.Point,
            vertices.sourceCrs()
        )
        if sink is None:
            raise QgsProcessingException(self.invalidSinkError(parameters, self.OUTPUT))

        feedback.pushInfo(self.tr('Validating topology of geometries...', 'Validando topologia das geometrias...' ))
        cont = 0

        def validarGeometria(layer, nome_camada):
            for feat in layer.getFeatures():
                geom = feat.geometry()

                if geom is None:
                    erro = self.tr(
                        'Null geometry in feature ID {} of layer "{}"!',
                        'Geometria nula na feição de ID {} da camada "{}"!'
                    ).format(feat.id(), nome_camada)
                    feedback.reportError(erro)

                elif geom.isEmpty():
                    erro = self.tr(
                        'Empty geometry in feature ID {} of layer "{}"!',
                        'Geometria vazia na feição de ID {} da camada "{}"!'
                    ).format(feat.id(), nome_camada)
                    feedback.reportError(erro)

                elif not geom.isGeosValid():
                    # IGNORAR multipolígonos com mais de uma parte
                    if geom.isMultipart() and geom.type() == 2:  # 2 = Polygon
                        partes = geom.asMultiPolygon()
                        if len(partes) > 1:
                            continue  # ignora multipolígono com múltiplas partes

                    erro = self.tr(
                        'Invalid geometry in feature ID {} of layer "{}"!',
                        'Geometria inválida na feição de ID {} da camada "{}"!'
                    ).format(feat.id(), nome_camada)
                    feedback.reportError(erro)

        validarGeometria(vertices, self.tr('Vertices (points)', 'Vértices (pontos)'))
        validarGeometria(limites, self.tr('Limits (lines)', 'Limites (linhas)'))
        validarGeometria(area, self.tr('Area (polygon)', 'Área (polígono)'))


        feedback.pushInfo(self.tr('Checking if each vertex of the Limit layer (line) has the corresponding one of the Vertex layer (point)...', 'Verificando se cada vértice da camada Limite (linha) tem o correspondente da camada Vértice (ponto)...'))
        for feat1 in limites.getFeatures():
            geom1 = feat1.geometry()
            if geom1:
                if geom1.isMultipart():
                    linha = feat1.geometry().asMultiPolyline()[0]
                else:
                    linha = feat1.geometry().asPolyline()
                for pnt in linha:
                    corresp = False
                    for feat2 in vertices.getFeatures():
                        vert = feat2.geometry().asPoint()
                        if vert == pnt:
                            corresp = True
                            continue
                    if not corresp:
                        cont += 1
                        X, Y = pnt.x(), pnt.y()
                        erro = self.tr('Point of the "line" layer has no correspondent in the "point" layer!',
                                    'Ponto de camada "linha" não possui correspondente na camada "ponto"!')
                        fet = QgsFeature(Fields)
                        fet.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(X,Y)))
                        fet.setAttributes([cont, feat1.id(), erro])
                        sink.addFeature(fet, QgsFeatureSink.FastInsert)

        feedback.pushInfo(self.tr('Checking if each vertex of the Area layer (polygon) has the corresponding one of the Vertex layer (point)...', 'Verificando se cada vértice da camada Área (polígono) tem o correspondente da camada Vértice (ponto)...'))
        for feat1 in area.getFeatures():
            geom1 = feat1.geometry()
            if geom1:
                if geom1.isMultipart():
                    pols = geom1.asMultiPolygon()
                else:
                    pols = [geom1.asPolygon()]
                for aneis in pols:
                    for anel in aneis:
                        for pnt in anel:
                            corresp = False
                            for feat2 in vertices.getFeatures():
                                vert = feat2.geometry().asPoint()
                                if vert == pnt:
                                    corresp = True
                                    continue
                            if not corresp:
                                cont += 1
                                X, Y = pnt.x(), pnt.y()
                                erro = self.tr('Point of the "area" layer has no correspondent in the "point" layer!',
                                            'Ponto de camada "área" não possui correspondente na camada "ponto"!')
                                fet = QgsFeature(Fields)
                                fet.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(X,Y)))
                                fet.setAttributes([cont, feat1.id(), erro])
                                sink.addFeature(fet, QgsFeatureSink.FastInsert)

        feedback.pushInfo(self.tr('Checking if each vertex of the Vertex layer (point) has the corresponding one of the Area layer (polygon)...', 'Verificando se cada vértice da camada Vértice (ponto) tem o correspondente da camada Área (polígono)...'))
        for feat1 in vertices.getFeatures():
            geom1 = feat1.geometry()
            if geom1:
                vert = geom1.asPoint()
                corresp = False
                for feat2 in area.getFeatures():
                    geom2 = feat2.geometry()
                    if geom2:
                        if geom2.isMultipart():
                            pols = geom2.asMultiPolygon()
                        else:
                            pols = [geom2.asPolygon()]
                        for aneis in pols:
                            for anel in aneis:
                                for pnt in anel:
                                    if vert == pnt:
                                        corresp = True
                                        break
                            if corresp:
                                break
                if not corresp:
                    cont += 1
                    X, Y = vert.x(), vert.y()
                    erro = self.tr('Point of the "point" layer has no correspondent in the "area" layer!',
                                'Ponto da camada "ponto" não possui correspondente na camada "área"!')
                    fet = QgsFeature(Fields)
                    fet.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(X,Y)))
                    fet.setAttributes([cont, feat1.id(), erro])
                    sink.addFeature(fet, QgsFeatureSink.FastInsert)

        feedback.pushInfo(self.tr('Checking if each vertex of the Vertex layer (point) has the corresponding one of the limit layer (line)...', 'Verificando se cada vértice da camada Vértice (ponto) tem o correspondente da camada Limite (linha)...'))
        for feat1 in vertices.getFeatures():
            geom1 = feat1.geometry()
            if geom1:
                vert = geom1.asPoint()
                geom1 = geom1.buffer(0.001/110000,5)
                corresp = False
                for feat2 in limites.getFeatures():
                    geom2 = feat2.geometry()
                    if geom2:
                        if geom2.intersects(geom1):
                            corresp = True
                            break
                if not corresp:
                    cont += 1
                    X, Y = vert.x(), vert.y()
                    erro = self.tr('Point of the "point" layer has no correspondent in the "line" layer!',
                                'Ponto de camada "ponto" não possui correspondente na camada "linha"!')
                    fet = QgsFeature(Fields)
                    fet.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(X,Y)))
                    fet.setAttributes([cont, feat1.id(), erro])
                    sink.addFeature(fet, QgsFeatureSink.FastInsert)

        feedback.pushInfo(self.tr('Checking for duplicate vertices inside the vertex (point) layer...', 'Verificando vértices duplicados dentro da camada vértice (ponto)...'))
        pontos = []
        for feat1 in vertices.getFeatures():
            geom1 = feat1.geometry()
            if geom1:
                vert = geom1.asPoint()
                if vert not in pontos:
                    pontos += [vert]
                else:
                    cont += 1
                    X, Y = vert.x(), vert.y()
                    erro = self.tr('Vertex of the "point" layer is duplicated!',
                                'Vértice da camada "ponto" está duplicado!')
                    fet = QgsFeature(Fields)
                    fet.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(X,Y)))
                    fet.setAttributes([cont, feat1.id(), erro])
                    sink.addFeature(fet, QgsFeatureSink.FastInsert)

        feedback.pushInfo(self.tr('Checking for duplicate vertices inside the limit (line) layer...', 'Verificando vértices duplicados dentro da camada limite (linha)...'))
        for feat1 in limites.getFeatures():
            geom1 = feat1.geometry()
            if geom1:
                if geom1.isMultipart():
                    linha = feat1.geometry().asMultiPolyline()[0]
                else:
                    linha = feat1.geometry().asPolyline()
                pontos = []
                for pnt in linha:
                    if pnt not in pontos:
                        pontos += [pnt]
                    else:
                        if not pnt == linha[-1]: # fechamento de anel linear
                            cont += 1
                            X, Y = pnt.x(), pnt.y()
                            erro = self.tr('Vertex of the "line" layer is duplicated!',
                                        'Vértice da camada "linha" está duplicado!')
                            fet = QgsFeature(Fields)
                            fet.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(X,Y)))
                            fet.setAttributes([cont, feat1.id(), erro])
                            sink.addFeature(fet, QgsFeatureSink.FastInsert)


        feedback.pushInfo(self.tr('Checking for duplicate vertices inside the area (polygon) layer...', 'Verificando vértices duplicados dentro da camada área (polígono)...'))
        for feat1 in area.getFeatures():
            geom1 = feat1.geometry()
            if geom1:
                if geom1.isMultipart():
                    pols = geom1.asMultiPolygon()
                else:
                    pols = [geom1.asPolygon()]
                for aneis in pols:
                    for anel in aneis:
                        pontos = []
                        for pnt in anel[:-1]:
                            if pnt not in pontos:
                                pontos += [pnt]
                            else:
                                cont += 1
                                X, Y = pnt.x(), pnt.y()
                                erro = self.tr('Vertex of the "area" layer is duplicated!',
                                            'Vértice da camada "área" está duplicado!')
                                fet = QgsFeature(Fields)
                                fet.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(X,Y)))
                                fet.setAttributes([cont, feat1.id(), erro])
                                sink.addFeature(fet, QgsFeatureSink.FastInsert)


        feedback.pushInfo(self.tr('Checking line layer orientation...', 'Verificando orientação da camada linha...'))
        for feat1 in limites.getFeatures():
            geom1 =  feat1.geometry()
            if geom1:
                if geom1.isMultipart():
                    ultimo_pnt = geom1.asMultiPolyline()[0][-1]
                    p0 = geom1.asMultiPolyline()[0][0]
                else:
                    ultimo_pnt = geom1.asPolyline()[-1]
                    p0 = geom1.asPolyline()[0]
                for feat2 in limites.getFeatures():
                    if feat1.id() != feat2.id():
                        geom2 = feat2.geometry()
                        if geom2:
                            if geom2.isMultipart():
                                primeiro_pnt = geom2.asMultiPolyline()[0][0]
                            else:
                                primeiro_pnt = geom2.asPolyline()[0]
                            if ultimo_pnt == primeiro_pnt:
                                break
                else:
                    if ultimo_pnt != p0: # não for fechamento de anel linear
                        X, Y = ultimo_pnt.x(), ultimo_pnt.y()
                        erro = self.tr('Problem with the orientation of the vertices of the line layer!',
                                    'Problema na orientação dos vértices da camada de linhas!')
                        fet = QgsFeature(Fields)
                        fet.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(X,Y)))
                        fet.setAttributes([cont, feat1.id(), erro])
                        sink.addFeature(fet, QgsFeatureSink.FastInsert)

        # Checar geometrias duplicadas para linhas
        feedback.pushInfo(self.tr('Checking for duplicate geometry line layer...', 'Verificando geometria duplicada na camada de linhas...'))
        geoms = []
        for feat1 in limites.getFeatures():
            geom = feat1.geometry()
            if geom:
                if geom.asWkt() not in geoms:
                    geoms += [geom.asWkt()]
                else:
                    pnt = geom.centroid().asPoint()
                    X, Y = pnt.x(), pnt.y()
                    erro = self.tr('Duplicated line geometry in feature ID {}!'.format(feat1.id()),
                                'Geometria linha duplicada na feição de ID {}!'.format(feat1.id()))
                    fet = QgsFeature(Fields)
                    fet.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(X,Y)))
                    fet.setAttributes([cont, feat1.id(), erro])
                    sink.addFeature(fet, QgsFeatureSink.FastInsert)

        # Checar geometrias duplicadas para polígono
        feedback.pushInfo(self.tr('Checking for duplicate geometry polygon layer...', 'Verificando geometria duplicada na camada de polígonos...'))
        geoms = []
        for feat1 in area.getFeatures():
            geom = feat1.geometry()
            if geom:
                if geom.asWkt() not in geoms:
                    geoms += [geom.asWkt()]
                else:
                    pnt = geom.centroid().asPoint()
                    X, Y = pnt.x(), pnt.y()
                    erro = self.tr('Duplicated polygon geometry in feature ID {}!'.format(feat1.id()),
                                'Geometria polígono duplicada na feição de ID {}!'.format(feat1.id()))
                    fet = QgsFeature(Fields)
                    fet.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(X,Y)))
                    fet.setAttributes([cont, feat1.id(), erro])
                    sink.addFeature(fet, QgsFeatureSink.FastInsert)

        # Verificar coordenada Z igual a Zero
        feedback.pushInfo(self.tr('Checking if any vertex has a dimension-Z equal to Zero...', 'Verificando se algum vértice tem cota Z igual a Zero...'))
        for feat1 in vertices.getFeatures():
            geom1 =  feat1.geometry()
            if geom1:
                z = float(geom1.constGet().z())
                pnt = geom1.asPoint()
                if str(z) == 'nan' or z == 0:
                    X, Y = pnt.x(), pnt.y()
                    erro = self.tr('Z altitude not filled in correctly!',
                                'Altitude Z não preenchida corretamente!')
                    fet = QgsFeature(Fields)
                    fet.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(X,Y)))
                    fet.setAttributes([cont, feat1.id(), erro])
                    sink.addFeature(fet, QgsFeatureSink.FastInsert)

        def avaliar_erros(cont):
            if cont == 0:
                return "🎉"
            elif 1 <= cont <= 5:
                return "🙁"
            elif 6 <= cont <= 20:
                return "😢"
            else:
                return "😱"

        if cont > 0:
            feedback.reportError(avaliar_erros(cont) + self.tr(' {} topological inconsistencies detected!', ' Foram encontradas {} inconsistências topológicas!').format(cont))
        else:
            feedback.pushInfo(avaliar_erros(cont) + self.tr(' Congratulations! No topological inconsistency was detected.', ' Parabéns! Nenhuma inconsistência topológica detectada.'))

        feedback.pushInfo(self.tr('Operation completed successfully!', 'Operação finalizada com sucesso!'))
        feedback.pushInfo('Leandro França - Eng Cart')
        self.SAIDA = dest_id
        return {self.OUTPUT: dest_id}

    def postProcessAlgorithm(self, context, feedback):
        layer = QgsProcessingUtils.mapLayerFromString(self.SAIDA, context)
        # Rotulação
        labeling = LabelConf(self.tr('type','tipo'))
        layer.setLabeling(labeling)
        layer.setLabelsEnabled(True)
        layer.triggerRepaint()
        # Simbologia
        renderer = SymbolSimplePoint(layer)
        layer.setRenderer(renderer)
        layer.triggerRepaint()

        return {}
