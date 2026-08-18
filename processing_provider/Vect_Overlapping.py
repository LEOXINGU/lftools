# -*- coding: utf-8 -*-

"""
Vect_Overlapping.py
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
__date__ = '2023-05-14'
__copyright__ = '(C) 2023, Leandro França'

from qgis.PyQt.QtCore import QMetaType
from qgis.core import (QgsApplication,
                       QgsGeometry,
                       Qgis,
                       QgsFeature,
                       QgsField,
                       QgsFields,
                       QgsSpatialIndex,
                       QgsProcessingUtils,
                       QgsFillSymbol,
                       QgsUnitTypes,
                       QgsFeatureSink,
                       QgsProcessingException,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterFeatureSink)
from lftools.geocapt.imgs import Imgs
from lftools.translations.translate import translate
from lftools.geocapt.cartography import OrientarPoligono
import numpy as np
import os
from qgis.PyQt.QtGui import QIcon

class Overlapping(QgsProcessingAlgorithm):

    LOC = QgsApplication.locale()[:2]

    def tr(self, *string):
        return translate(string, self.LOC)

    def createInstance(self):
        return Overlapping()

    def name(self):
        return 'overlapping'

    def displayName(self):
        return self.tr('Overlapping polygons', 'Sobreposição de polígonos')

    def group(self):
        return self.tr('Vector', 'Vetor')

    def groupId(self):
        return 'vector'

    def tags(self):
        return 'GeoOne,cadastro,parcela,sequence,confrontante,vizinho,neighbours,sobreposição,overlap,cadastre,borderer,loteamento'.split(',')

    def icon(self):
        return QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images/vetor.png'))

    txt_en = '''Identifies the overlap between features of a polygon type layer.'''
    txt_pt = '''Identifica a sobreposição entre feições de uma camada do tipo polígono.'''
    figure = 'images/tutorial/vect_overlapping.jpg'

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
    OUTPUT = 'OUTPUT'

    def initAlgorithm(self, config = None):
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT,
                self.tr('Polygon layer', 'Camada de polígonos'),
                [Qgis.ProcessingSourceType.TypeVectorPolygon]
            )
        )

        # OUTPUT
        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT,
                self.tr('Overlapping', 'Sobreposição')
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

        # Camada de Saída
        Fields = QgsFields()
        itens = {
            'ID1': QMetaType.Type.Int,
            'ID2': QMetaType.Type.Int,
        }
        for item in itens:
            Fields.append(QgsField(item, itens[item]))

        (sink, dest_id) = self.parameterAsSink(
            parameters,
            self.OUTPUT,
            context,
            Fields,
            Qgis.WkbType.Polygon,
            layer.sourceCrs()
        )
        if sink is None:
            raise QgsProcessingException(self.invalidSinkError(parameters, self.OUTPUT))

        feedback.pushInfo(self.tr(
            'Checking geometries and creating spatial index...',
            'Verificando geometrias e criando índice espacial...'
        ))

        # Pré-processa as geometrias.
        # Geometrias nulas/vazias são ignoradas. Geometrias inválidas são
        # reparadas com makeValid(). Polygon e MultiPolygon são aceitos.
        index = QgsSpatialIndex()
        geometrias = {}
        n_null = 0
        n_empty = 0
        n_invalid = 0
        n_repaired = 0
        n_ignored = 0

        for feat in layer.getFeatures():
            if feedback.isCanceled():
                break

            fid = feat.id()
            geom = feat.geometry()

            if geom is None or geom.isNull():
                n_null += 1
                n_ignored += 1
                feedback.pushWarning(self.tr(
                    'Feature id {} has null geometry and was ignored.',
                    'Feição de id {} possui geometria nula e foi ignorada.'
                ).format(fid))
                continue

            if geom.isEmpty():
                n_empty += 1
                n_ignored += 1
                feedback.pushWarning(self.tr(
                    'Feature id {} has empty geometry and was ignored.',
                    'Feição de id {} possui geometria vazia e foi ignorada.'
                ).format(fid))
                continue

            # O parâmetro de entrada já restringe a camada a polígonos,
            # mas esta checagem protege o algoritmo contra geometrias anômalas.
            if geom.type() != Qgis.GeometryType.Polygon:
                n_ignored += 1
                feedback.pushWarning(self.tr(
                    'Feature id {} is not polygonal and was ignored.',
                    'Feição de id {} não possui geometria poligonal e foi ignorada.'
                ).format(fid))
                continue

            # Trabalha sobre uma cópia da geometria para não alterar a fonte.
            geom = QgsGeometry(geom)

            if not geom.isGeosValid():
                n_invalid += 1
                repaired = geom.makeValid()

                if repaired is None or repaired.isNull() or repaired.isEmpty():
                    n_ignored += 1
                    feedback.pushWarning(self.tr(
                        'Feature id {} is invalid and could not be repaired. It was ignored.',
                        'Feição de id {} é inválida e não pôde ser reparada. Foi ignorada.'
                    ).format(fid))
                    continue

                # makeValid() pode retornar GeometryCollection quando há colapso
                # dimensional. Mantemos somente os componentes poligonais.
                if repaired.type() != Qgis.GeometryType.Polygon:
                    repaired.convertGeometryCollectionToSubclass(Qgis.GeometryType.Polygon)

                if repaired.isNull() or repaired.isEmpty() or repaired.type() != Qgis.GeometryType.Polygon:
                    n_ignored += 1
                    feedback.pushWarning(self.tr(
                        'Feature id {} has no valid polygonal component after repair and was ignored.',
                        'Feição de id {} não possui componente poligonal válido após o reparo e foi ignorada.'
                    ).format(fid))
                    continue

                geom = repaired
                n_repaired += 1

            # Guarda a geometria preparada e indexa sua extensão.
            geometrias[fid] = geom
            feat_index = QgsFeature(feat)
            feat_index.setGeometry(geom)
            index.addFeature(feat_index)

        feedback.pushInfo(self.tr(
            'Identifying overlapping polygons...',
            'Identificando sobreposição entre polígonos...'
        ))

        ids = list(geometrias.keys())
        total = 100.0 / len(ids) if ids else 0
        n_pairs = 0
        n_output = 0
        n_errors = 0

        for current, ID1 in enumerate(ids):
            if feedback.isCanceled():
                break

            geom1 = geometrias[ID1]
            feat_ids = index.intersects(geom1.boundingBox())

            for ID2 in feat_ids:
                # Evita comparar uma feição consigo mesma e evita duplicar
                # os pares (ID1, ID2) / (ID2, ID1).
                if ID2 <= ID1 or ID2 not in geometrias:
                    continue

                geom2 = geometrias[ID2]

                try:
                    if not geom1.intersects(geom2):
                        continue

                    inter = geom1.intersection(geom2)

                    if inter is None or inter.isNull() or inter.isEmpty():
                        continue

                    # Contatos apenas por linha ou ponto não são sobreposição
                    # de área e, portanto, não são gravados.
                    itens_inter = inter.asGeometryCollection()
                    if not itens_inter:
                        itens_inter = [inter]

                    pair_written = False

                    for item in itens_inter:
                        if item is None or item.isNull() or item.isEmpty():
                            continue

                        if item.type() != Qgis.GeometryType.Polygon:
                            continue

                        if item.isMultipart():
                            for coord in item.asMultiPolygon():
                                if not coord:
                                    continue
                                feature = QgsFeature(Fields)
                                feature.setGeometry(QgsGeometry.fromPolygonXY(coord))
                                feature.setAttributes([ID1, ID2])
                                sink.addFeature(feature, QgsFeatureSink.Flag.FastInsert)
                                n_output += 1
                                pair_written = True
                        else:
                            feature = QgsFeature(Fields)
                            feature.setGeometry(item)
                            feature.setAttributes([ID1, ID2])
                            sink.addFeature(feature, QgsFeatureSink.Flag.FastInsert)
                            n_output += 1
                            pair_written = True

                    if pair_written:
                        n_pairs += 1

                except Exception as e:
                    # Uma geometria problemática não deve interromper toda a execução.
                    n_errors += 1
                    feedback.pushWarning(self.tr(
                        'Error processing features {} and {}: {}. Pair ignored.',
                        'Erro ao processar as feições {} e {}: {}. Par ignorado.'
                    ).format(ID1, ID2, str(e)))
                    continue

            feedback.setProgress(int((current + 1) * total))

        feedback.pushInfo(self.tr(
            'Valid geometries used: {}',
            'Geometrias válidas utilizadas: {}'
        ).format(len(geometrias)))
        feedback.pushInfo(self.tr(
            'Null geometries ignored: {}',
            'Geometrias nulas ignoradas: {}'
        ).format(n_null))
        feedback.pushInfo(self.tr(
            'Empty geometries ignored: {}',
            'Geometrias vazias ignoradas: {}'
        ).format(n_empty))
        feedback.pushInfo(self.tr(
            'Invalid geometries found: {} | repaired: {}',
            'Geometrias inválidas encontradas: {} | reparadas: {}'
        ).format(n_invalid, n_repaired))
        feedback.pushInfo(self.tr(
            'Ignored geometries: {} | geometry-operation errors: {}',
            'Geometrias ignoradas: {} | erros em operações geométricas: {}'
        ).format(n_ignored, n_errors))
        feedback.pushInfo(self.tr(
            'Overlapping feature pairs: {} | output polygons: {}',
            'Pares de feições com sobreposição: {} | polígonos de saída: {}'
        ).format(n_pairs, n_output))

        feedback.pushInfo(self.tr(
            'Operation completed successfully!',
            'Operação finalizada com sucesso!'
        ))
        feedback.pushInfo(self.tr(
            'Leandro Franca - Cartographic Engineer',
            'Leandro França - Eng Cart'
        ))

        self.dest_id = dest_id
        return {self.OUTPUT: dest_id}


    def postProcessAlgorithm(self, context, feedback):

        try:
            layer = QgsProcessingUtils.mapLayerFromString(
                self.dest_id,
                context
            )

            if layer is not None and layer.isValid():

                symbol = QgsFillSymbol.createSimple({
                    'color': '255,0,0,80',
                    'outline_color': '255,0,0,255',
                    'outline_width': '1.5',
                    'outline_width_unit': 'MM',
                    'style': 'solid',
                    'outline_style': 'solid'
                })

                layer.renderer().setSymbol(symbol)
                layer.triggerRepaint()

        except Exception as e:
            feedback.pushWarning(
                self.tr(
                    'Could not apply output layer style: {}',
                    'Não foi possível aplicar a simbologia da camada de saída: {}'
                ).format(str(e))
            )

        return {}