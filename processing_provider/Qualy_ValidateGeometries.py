# -*- coding: utf-8 -*-

"""
Qualy_ValidateGeometries.py
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
__date__ = '2026-09-12'
__copyright__ = '(C) 2026, Leandro França'

from collections import Counter
from datetime import datetime
from math import acos, degrees, floor, hypot, isfinite
import os

from qgis.PyQt.QtCore import QMetaType
from qgis.PyQt.QtGui import QIcon, QColor
from qgis.core import (
    QgsApplication,
    QgsCoordinateReferenceSystem,
    QgsCoordinateTransform,
    QgsFeature,
    QgsFeatureSink,
    QgsField,
    QgsFields,
    QgsGeometry,
    QgsProcessing,
    QgsProcessingAlgorithm,
    QgsProcessingException,
    QgsProcessingParameterBoolean,
    QgsProcessingParameterFeatureSink,
    QgsProcessingParameterFileDestination,
    QgsProcessingParameterMultipleLayers,
    QgsProcessingParameterNumber,
    QgsProcessingUtils,
    QgsPointXY,
    QgsRectangle,
    QgsSettings,
    QgsVectorLayerSimpleLabeling,
    QgsWkbTypes,
    Qgis,
)

from lftools.geocapt.imgs import Imgs, lftools_logo
from lftools.geocapt.cartography import LabelConf, SymbolSimplePoint
from lftools.geocapt.topogeo import str2HTML
from lftools.translations.translate import translate


class ValidateGeometries(QgsProcessingAlgorithm):

    INPUTS = 'INPUTS'
    DUPLICATE_TOLERANCE = 'DUPLICATE_TOLERANCE'
    CHECK_MULTIPART = 'CHECK_MULTIPART'
    CHECK_SMALL_ANGLE = 'CHECK_SMALL_ANGLE'
    MIN_ANGLE = 'MIN_ANGLE'
    CHECK_MIN_SIZE = 'CHECK_MIN_SIZE'
    MIN_LENGTH = 'MIN_LENGTH'
    MIN_AREA = 'MIN_AREA'
    CHECK_HOLES = 'CHECK_HOLES'
    MIN_HOLE_AREA = 'MIN_HOLE_AREA'
    ERRORS = 'ERRORS'
    OCCURRENCES = 'OCCURRENCES'
    HTML = 'HTML'

    SETTINGS_PREFIX = 'LFTools/ValidateGeometries/'

    LOC = QgsApplication.locale()[:2]

    RULES = {
        'VGE001': ('Null or empty geometry', 'Geometria nula ou vazia'),
        'VGE002': ('Invalid geometry', 'Geometria inválida'),
        'VGE003': ('Degenerate geometry', 'Geometria degenerada'),
        'VGE004': ('Duplicated consecutive vertex', 'Vértice consecutivo duplicado'),
        'VGE005': ('Multipart geometry', 'Geometria multiparte'),
        'VGE006': ('Angle below tolerance', 'Ângulo inferior à tolerância'),
        'VGE007': ('Length below tolerance', 'Comprimento inferior à tolerância'),
        'VGE008': ('Area below tolerance', 'Área inferior à tolerância'),
        'VGE009': ('Hole below minimum area', 'Buraco inferior à área mínima'),
    }

    def tr(self, *string):
        return translate(string, self.LOC)

    def createInstance(self):
        return ValidateGeometries()

    def name(self):
        return 'validategeometries'

    def displayName(self):
        return self.tr('Validate Geometries', 'Validar Geometrias')

    def group(self):
        return self.tr('Quality', 'Qualidade')

    def groupId(self):
        return 'quality'

    def tags(self):
        return (
            'GeoOne,quality,qualidade,geometry,geometria,validation,validação,'
            'logical consistency,consistência lógica,topology,topologia,invalid,'
            'empty,null,degenerate,duplicate vertex,multipart,small angle,'
            'minimum area,minimum length,hole,interior ring,anel interno,QGIS,LFTools'
        ).split(',')

    def icon(self):
        return QIcon(os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'images/quality.png'
        ))

    txt_en = '''
<p>This tool performs a <b>complete automated inspection</b> of individual geometries in one or more point, line, or polygon layers. This step should be completed before intraclass topological validation.</p>
<p><b>Checks:</b></p>
▪️ Null, empty, invalid, or degenerate geometries;
▪️ Duplicated consecutive vertices;
▪️ Multipart geometries and angles below the defined tolerance;
▪️ Lines or polygons smaller than the defined thresholds;
▪️ Polygon holes smaller than the minimum allowed area.
<p><b>Outputs:</b> a point layer of located errors, a complete occurrence table, and an HTML quality report.</p>
<p>Linear tolerances are expressed in <b>metres</b>, area thresholds in <b>square metres</b>, and angles in degrees. Geographic and projected CRS are accepted; when necessary, the tool creates an internal local metric CRS for the measurements.</p>
<p>Tolerances should consider the reference scale, input resolution, feature class, and intended use. Multipart, undersized, or holed geometries are not necessarily errors and should be technically reviewed.</p>
<p style="color:#b00020;"><b>Important:</b> the input layers are not modified or automatically corrected.</p>
'''

    txt_pt = '''
<p>Esta ferramenta realiza uma <b>inspeção completa automatizada</b> das geometrias individuais de uma ou mais camadas de pontos, linhas ou polígonos. Essa etapa deve ser concluída antes da validação topológica intraclasse.</p>
<p><b>Verificações:</b></p>
▪️ Geometrias nulas, vazias, inválidas ou degeneradas;
▪️ Vértices consecutivos duplicados;
▪️ Geometrias multipartes e ângulos inferiores à tolerância definida;
▪️ Linhas ou polígonos inferiores às dimensões mínimas definidas;
▪️ Buracos em polígonos inferiores à área mínima permitida.
<p><b>Saídas:</b> camada pontual de erros localizados, tabela completa de ocorrências e relatório de qualidade em HTML.</p>
<p>As tolerâncias lineares são expressas em <b>metros</b>, os limites de área em <b>metros quadrados</b> e os ângulos em graus. São aceitos SRC geográficos e projetados; quando necessário, a ferramenta cria internamente um SRC métrico local para realizar as medições.</p>
<p>As tolerâncias devem considerar a escala de referência, a resolução do insumo, a classe da feição e a finalidade de utilização. Geometrias multipartes, inferiores às dimensões mínimas ou com buracos não constituem necessariamente erros e devem ser analisadas tecnicamente.</p>
<p style="color:#b00020;"><b>Importante:</b> as camadas de entrada não são modificadas nem corrigidas automaticamente.</p>
'''

    figure = 'images/tutorial/qualy_validate_geometries.jpg'

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
        settings = QgsSettings()
        duplicate_tolerance = settings.value(
            self.SETTINGS_PREFIX + 'duplicateTolerance', 0.01, type=float
        )
        check_multipart = settings.value(
            self.SETTINGS_PREFIX + 'checkMultipart', False, type=bool
        )
        check_small_angle = settings.value(
            self.SETTINGS_PREFIX + 'checkSmallAngle', True, type=bool
        )
        min_angle = settings.value(
            self.SETTINGS_PREFIX + 'minAngle', 5.0, type=float
        )
        check_min_size = settings.value(
            self.SETTINGS_PREFIX + 'checkMinimumSize', True, type=bool
        )
        min_length = settings.value(
            self.SETTINGS_PREFIX + 'minLength', 0.20, type=float
        )
        min_area = settings.value(
            self.SETTINGS_PREFIX + 'minArea', 0.04, type=float
        )
        check_holes = settings.value(
            self.SETTINGS_PREFIX + 'checkHoles', True, type=bool
        )
        min_hole_area = settings.value(
            self.SETTINGS_PREFIX + 'minHoleArea', 0.04, type=float
        )

        self.addParameter(QgsProcessingParameterMultipleLayers(
            self.INPUTS,
            self.tr('Vector layers', 'Camadas vetoriais'),
            QgsProcessing.TypeVectorAnyGeometry
        ))

        self.addParameter(QgsProcessingParameterNumber(
            self.DUPLICATE_TOLERANCE,
            self.tr(
                'Tolerance for duplicated consecutive vertices (m)',
                'Tolerância para vértices consecutivos duplicados (m)'
            ),
            type=QgsProcessingParameterNumber.Type.Double,
            defaultValue=duplicate_tolerance,
            minValue=0.0
        ))

        self.addParameter(QgsProcessingParameterBoolean(
            self.CHECK_MULTIPART,
            self.tr(
                'Report multipart geometries',
                'Reportar geometrias multipartes'
            ),
            defaultValue=check_multipart
        ))

        self.addParameter(QgsProcessingParameterBoolean(
            self.CHECK_SMALL_ANGLE,
            self.tr(
                'Check angles below a tolerance',
                'Verificar ângulos inferiores a uma tolerância'
            ),
            defaultValue=check_small_angle
        ))

        self.addParameter(QgsProcessingParameterNumber(
            self.MIN_ANGLE,
            self.tr('Minimum angle (degrees)', 'Ângulo mínimo (graus)'),
            type=QgsProcessingParameterNumber.Type.Double,
            defaultValue=min_angle,
            minValue=0.0,
            maxValue=180.0
        ))

        self.addParameter(QgsProcessingParameterBoolean(
            self.CHECK_MIN_SIZE,
            self.tr(
                'Check minimum length and area',
                'Verificar comprimento e área mínimos'
            ),
            defaultValue=check_min_size
        ))

        self.addParameter(QgsProcessingParameterNumber(
            self.MIN_LENGTH,
            self.tr(
                'Minimum line length (m)',
                'Comprimento mínimo das linhas (m)'
            ),
            type=QgsProcessingParameterNumber.Type.Double,
            defaultValue=min_length,
            minValue=0.0
        ))

        self.addParameter(QgsProcessingParameterNumber(
            self.MIN_AREA,
            self.tr(
                'Minimum polygon area (m²)',
                'Área mínima dos polígonos (m²)'
            ),
            type=QgsProcessingParameterNumber.Type.Double,
            defaultValue=min_area,
            minValue=0.0
        ))

        self.addParameter(QgsProcessingParameterBoolean(
            self.CHECK_HOLES,
            self.tr(
                'Check polygon holes below the minimum area',
                'Verificar buracos em polígonos inferiores à área mínima'
            ),
            defaultValue=check_holes
        ))

        self.addParameter(QgsProcessingParameterNumber(
            self.MIN_HOLE_AREA,
            self.tr(
                'Minimum allowed hole area (m²)',
                'Área mínima permitida para buracos (m²)'
            ),
            type=QgsProcessingParameterNumber.Type.Double,
            defaultValue=min_hole_area,
            minValue=0.0
        ))

        self.addParameter(QgsProcessingParameterFeatureSink(
            self.ERRORS,
            self.tr('Located geometry errors', 'Erros geométricos localizados'),
            type=Qgis.ProcessingSourceType.TypeVectorPoint
        ))

        self.addParameter(QgsProcessingParameterFeatureSink(
            self.OCCURRENCES,
            self.tr(
                'Geometry validation occurrences',
                'Ocorrências da validação geométrica'
            ),
            type=Qgis.ProcessingSourceType.TypeVector
        ))

        self.addParameter(QgsProcessingParameterFileDestination(
            self.HTML,
            self.tr(
                'Geometry validation report',
                'Relatório de validação geométrica'
            ),
            self.tr('HTML files (*.html)')
        ))

    def _metric_working_context(self, layers, context):
        """Return a metric working CRS and optional forward/back transforms."""
        source_crs = layers[0].crs()
        if not source_crs.isValid():
            raise QgsProcessingException(self.tr(
                'The input CRS is invalid or undefined.',
                'O SRC de entrada é inválido ou não está definido.'
            ))

        if (
            not source_crs.isGeographic()
            and source_crs.mapUnits() == Qgis.DistanceUnit.Meters
        ):
            return source_crs, None, None

        extent = QgsRectangle(layers[0].extent())
        for layer in layers[1:]:
            extent.combineExtentWith(layer.extent())
        if extent.isNull():
            raise QgsProcessingException(self.tr(
                'A local metric CRS could not be determined from the invalid input extent.',
                'Não foi possível determinar um SRC métrico local a partir da extensão inválida das entradas.'
            ))

        geographic_crs = QgsCoordinateReferenceSystem.fromEpsgId(4326)
        center = extent.center()
        try:
            if source_crs != geographic_crs:
                center = QgsCoordinateTransform(
                    source_crs, geographic_crs, context.transformContext()
                ).transform(center)
        except Exception as error:
            raise QgsProcessingException(self.tr(
                'The input extent could not be transformed to determine a local metric CRS: {}',
                'A extensão de entrada não pôde ser transformada para determinar um SRC métrico local: {}'
            ).format(str(error)))

        longitude = center.x()
        latitude = center.y()
        if not (-180.0 <= longitude <= 180.0 and -80.0 <= latitude <= 84.0):
            raise QgsProcessingException(self.tr(
                'The input centre is outside the area supported by the temporary UTM CRS.',
                'O centro das entradas está fora da área suportada pelo SRC UTM temporário.'
            ))
        zone = max(1, min(60, int(floor((longitude + 180.0) / 6.0)) + 1))
        epsg = (32600 if latitude >= 0 else 32700) + zone
        working_crs = QgsCoordinateReferenceSystem.fromEpsgId(epsg)
        if not working_crs.isValid():
            raise QgsProcessingException(self.tr(
                'The local metric CRS EPSG:{} could not be created.',
                'Não foi possível criar o SRC métrico local EPSG:{}.'
            ).format(epsg))

        return (
            working_crs,
            QgsCoordinateTransform(
                source_crs, working_crs, context.transformContext()
            ),
            QgsCoordinateTransform(
                working_crs, source_crs, context.transformContext()
            )
        )

    def _metric_geometry(self, geometry, transform):
        metric_geometry = QgsGeometry(geometry)
        if transform is not None:
            try:
                result = metric_geometry.transform(transform)
                if result != Qgis.GeometryOperationResult.Success:
                    raise ValueError(self.tr(
                        'geometry transformation returned status {}',
                        'a transformação da geometria retornou o estado {}'
                    ).format(result))
            except Exception as error:
                raise QgsProcessingException(self.tr(
                    'A geometry could not be transformed to the metric working CRS: {}',
                    'Uma geometria não pôde ser transformada para o SRC métrico de trabalho: {}'
                ).format(str(error)))
        return metric_geometry

    @staticmethod
    def _same_point(point_a, point_b, tolerance):
        distance = hypot(point_a.x() - point_b.x(), point_a.y() - point_b.y())
        return distance <= tolerance

    @staticmethod
    def _geometry_sequences(geometry):
        """Return vertex sequences without mixing parts or polygon rings."""
        geometry_type = QgsWkbTypes.geometryType(geometry.wkbType())
        multipart = geometry.isMultipart()

        if geometry_type == QgsWkbTypes.LineGeometry:
            return geometry.asMultiPolyline() if multipart else [geometry.asPolyline()]

        if geometry_type == QgsWkbTypes.PolygonGeometry:
            polygons = geometry.asMultiPolygon() if multipart else [geometry.asPolygon()]
            return [ring for polygon in polygons for ring in polygon]

        return []

    @staticmethod
    def _angle(point_a, vertex, point_b):
        vector_a = (point_a.x() - vertex.x(), point_a.y() - vertex.y())
        vector_b = (point_b.x() - vertex.x(), point_b.y() - vertex.y())
        norm_a = hypot(*vector_a)
        norm_b = hypot(*vector_b)
        if norm_a == 0 or norm_b == 0:
            return None
        cosine = (
            vector_a[0] * vector_b[0] + vector_a[1] * vector_b[1]
        ) / (norm_a * norm_b)
        return degrees(acos(max(-1.0, min(1.0, cosine))))

    def _rule_name(self, rule_id):
        return self.tr(*self.RULES[rule_id])

    @staticmethod
    def _polygon_holes(geometry):
        """Return each interior ring as a polygon geometry."""
        polygons = geometry.asMultiPolygon() if geometry.isMultipart() else [
            geometry.asPolygon()
        ]
        holes = []
        for polygon_index, polygon in enumerate(polygons, 1):
            for ring_index, ring in enumerate(polygon[1:], 1):
                if len(ring) >= 4:
                    holes.append((
                        polygon_index,
                        ring_index,
                        QgsGeometry.fromPolygonXY([ring])
                    ))
        return holes

    @staticmethod
    def _first_vertex(geometry):
        try:
            for vertex in geometry.vertices():
                if isfinite(vertex.x()) and isfinite(vertex.y()):
                    return QgsPointXY(vertex.x(), vertex.y())
        except Exception:
            pass
        return None

    def processAlgorithm(self, parameters, context, feedback):
        layers = self.parameterAsLayerList(parameters, self.INPUTS, context)
        if not layers:
            raise QgsProcessingException(self.tr(
                'Select at least one vector layer!',
                'Selecione pelo menos uma camada vetorial!'
            ))

        first_crs = layers[0].crs()
        incompatible_layers = [
            layer.name() for layer in layers if layer.crs() != first_crs
        ]
        if incompatible_layers:
            raise QgsProcessingException(self.tr(
                'All input layers must use the same CRS. Incompatible layers: {}',
                'Todas as camadas de entrada devem utilizar o mesmo SRC. Camadas incompatíveis: {}'
            ).format(', '.join(incompatible_layers)))

        working_crs, to_metric, _from_metric = self._metric_working_context(
            layers, context
        )
        if to_metric is None:
            feedback.pushInfo(self.tr(
                'Measurements will use the input CRS in metres ({}).',
                'As medições utilizarão o SRC de entrada em metros ({}).'
            ).format(working_crs.authid()))
        else:
            feedback.pushInfo(self.tr(
                'Measurements will use the local metric working CRS {}. Output locations remain in the input CRS.',
                'As medições utilizarão o SRC métrico local de trabalho {}. As localizações de saída permanecem no SRC de entrada.'
            ).format(working_crs.authid()))

        tolerance = self.parameterAsDouble(
            parameters, self.DUPLICATE_TOLERANCE, context
        )
        check_multipart = self.parameterAsBool(
            parameters, self.CHECK_MULTIPART, context
        )
        check_small_angle = self.parameterAsBool(
            parameters, self.CHECK_SMALL_ANGLE, context
        )
        min_angle = self.parameterAsDouble(parameters, self.MIN_ANGLE, context)
        check_min_size = self.parameterAsBool(
            parameters, self.CHECK_MIN_SIZE, context
        )
        min_length = self.parameterAsDouble(
            parameters, self.MIN_LENGTH, context
        )
        min_area = self.parameterAsDouble(parameters, self.MIN_AREA, context)
        check_holes = self.parameterAsBool(
            parameters, self.CHECK_HOLES, context
        )
        min_hole_area = self.parameterAsDouble(
            parameters, self.MIN_HOLE_AREA, context
        )
        html_output = self.parameterAsFileOutput(parameters, self.HTML, context)

        error_fields = QgsFields()
        error_fields.append(QgsField('rule_id', QMetaType.Type.QString))
        error_fields.append(QgsField('rule', QMetaType.Type.QString))
        error_fields.append(QgsField('layer', QMetaType.Type.QString))
        error_fields.append(QgsField('feature_id', QMetaType.Type.LongLong))
        error_fields.append(QgsField('detail', QMetaType.Type.QString))
        error_fields.append(QgsField('value', QMetaType.Type.Double))
        error_fields.append(QgsField('tolerance', QMetaType.Type.Double))

        occurrence_fields = QgsFields()
        for field in error_fields:
            occurrence_fields.append(field)
        occurrence_fields.append(QgsField('located', QMetaType.Type.Bool))

        error_sink, error_dest = self.parameterAsSink(
            parameters,
            self.ERRORS,
            context,
            error_fields,
            QgsWkbTypes.Point,
            first_crs
        )
        if error_sink is None:
            raise QgsProcessingException(self.invalidSinkError(parameters, self.ERRORS))

        occurrence_sink, occurrence_dest = self.parameterAsSink(
            parameters,
            self.OCCURRENCES,
            context,
            occurrence_fields,
            QgsWkbTypes.NoGeometry,
            first_crs
        )
        if occurrence_sink is None:
            raise QgsProcessingException(
                self.invalidSinkError(parameters, self.OCCURRENCES)
            )

        total_features = sum(max(0, layer.featureCount()) for layer in layers)
        processed = 0
        occurrences = []
        layer_counts = Counter()
        rule_counts = Counter()
        layer_feature_counts = {
            layer.name(): max(0, layer.featureCount()) for layer in layers
        }

        def register(rule_id, layer, feature_id, detail='', point=None,
                     value=None, threshold=None):
            rule_name = self._rule_name(rule_id)
            located = point is not None
            attributes = [
                rule_id,
                rule_name,
                layer.name(),
                int(feature_id),
                detail,
                value,
                threshold,
            ]

            occurrence = QgsFeature(occurrence_fields)
            occurrence.setAttributes(attributes + [located])
            occurrence_sink.addFeature(occurrence, QgsFeatureSink.Flag.FastInsert)

            if located:
                error = QgsFeature(error_fields)
                error.setGeometry(QgsGeometry.fromPointXY(point))
                error.setAttributes(attributes)
                error_sink.addFeature(error, QgsFeatureSink.Flag.FastInsert)

            occurrences.append({
                'rule_id': rule_id,
                'rule': rule_name,
                'layer': layer.name(),
                'feature_id': int(feature_id),
                'detail': detail,
                'value': value,
                'threshold': threshold,
                'located': located,
            })
            layer_counts[layer.name()] += 1
            rule_counts[rule_id] += 1

        for layer in layers:
            feedback.pushInfo(self.tr(
                'Validating layer: {}', 'Validando camada: {}'
            ).format(layer.name()))

            for feature in layer.getFeatures():
                if feedback.isCanceled():
                    break

                processed += 1
                geometry = feature.geometry()
                feature_id = feature.id()

                if geometry is None or geometry.isNull() or geometry.isEmpty():
                    register('VGE001', layer, feature_id)
                    if total_features:
                        feedback.setProgress(int(processed * 100.0 / total_features))
                    continue

                metric_geometry = self._metric_geometry(geometry, to_metric)

                # In current PyQGIS bindings validateGeometry() returns the
                # error list directly. Some older bindings exposed the C++
                # output-argument form, so retain a compatibility fallback.
                try:
                    validation_errors = geometry.validateGeometry()
                except TypeError:
                    validation_errors = []
                    geometry.validateGeometry(validation_errors)

                if validation_errors is None:
                    validation_errors = []
                for validation_error in validation_errors:
                    point = None
                    try:
                        point = validation_error.where()
                        if (
                            point is None
                            or not isfinite(point.x())
                            or not isfinite(point.y())
                        ):
                            point = None
                    except Exception:
                        point = None
                    register(
                        'VGE002',
                        layer,
                        feature_id,
                        validation_error.what(),
                        point
                    )

                geometry_type = QgsWkbTypes.geometryType(geometry.wkbType())
                anchor = self._first_vertex(geometry)

                if (
                    geometry_type == QgsWkbTypes.LineGeometry
                    and metric_geometry.length() == 0
                ):
                    register('VGE003', layer, feature_id, point=anchor, value=0.0)
                elif (
                    geometry_type == QgsWkbTypes.PolygonGeometry
                    and metric_geometry.area() == 0
                ):
                    register('VGE003', layer, feature_id, point=anchor, value=0.0)

                if check_multipart and geometry.isMultipart():
                    register('VGE005', layer, feature_id, point=anchor)

                source_sequences = self._geometry_sequences(geometry)
                metric_sequences = self._geometry_sequences(metric_geometry)
                for source_sequence, metric_sequence in zip(
                    source_sequences, metric_sequences
                ):
                    for index in range(1, len(metric_sequence)):
                        if self._same_point(
                            metric_sequence[index - 1],
                            metric_sequence[index],
                            tolerance
                        ):
                            register(
                                'VGE004',
                                layer,
                                feature_id,
                                point=source_sequence[index],
                                value=hypot(
                                    metric_sequence[index].x()
                                    - metric_sequence[index - 1].x(),
                                    metric_sequence[index].y()
                                    - metric_sequence[index - 1].y()
                                ),
                                threshold=tolerance
                            )

                    if check_small_angle and len(metric_sequence) >= 3:
                        closed = self._same_point(
                            metric_sequence[0], metric_sequence[-1], 0.0
                        )
                        vertices = (
                            metric_sequence[:-1] if closed else metric_sequence
                        )
                        source_vertices = (
                            source_sequence[:-1] if closed else source_sequence
                        )
                        if closed:
                            triples = [
                                (
                                    vertices[index - 1],
                                    vertices[index],
                                    vertices[(index + 1) % len(vertices)],
                                    source_vertices[index]
                                )
                                for index in range(len(vertices))
                            ]
                        else:
                            triples = [
                                (
                                    vertices[index - 1], vertices[index],
                                    vertices[index + 1], source_vertices[index]
                                )
                                for index in range(1, len(vertices) - 1)
                            ]

                        for point_a, vertex, point_b, source_vertex in triples:
                            angle = self._angle(point_a, vertex, point_b)
                            if angle is not None and angle < min_angle:
                                register(
                                    'VGE006',
                                    layer,
                                    feature_id,
                                    point=source_vertex,
                                    value=angle,
                                    threshold=min_angle
                                )

                if check_min_size:
                    if (
                        geometry_type == QgsWkbTypes.LineGeometry
                        and metric_geometry.length() < min_length
                    ):
                        register(
                            'VGE007', layer, feature_id, point=anchor,
                            value=metric_geometry.length(), threshold=min_length
                        )
                    elif (
                        geometry_type == QgsWkbTypes.PolygonGeometry
                        and metric_geometry.area() < min_area
                    ):
                        register(
                            'VGE008', layer, feature_id, point=anchor,
                            value=metric_geometry.area(), threshold=min_area
                        )

                if check_holes and geometry_type == QgsWkbTypes.PolygonGeometry:
                    try:
                        source_holes = self._polygon_holes(geometry)
                        metric_holes = self._polygon_holes(metric_geometry)
                        for source_hole, metric_hole in zip(
                            source_holes, metric_holes
                        ):
                            polygon_index, ring_index, hole = source_hole
                            hole_area = metric_hole[2].area()
                            if hole_area < min_hole_area:
                                hole_point = None
                                try:
                                    point = hole.pointOnSurface().asPoint()
                                    if isfinite(point.x()) and isfinite(point.y()):
                                        hole_point = QgsPointXY(point.x(), point.y())
                                except Exception:
                                    hole_point = None
                                register(
                                    'VGE009',
                                    layer,
                                    feature_id,
                                    self.tr(
                                        'Interior ring {} of polygon part {}.',
                                        'Anel interno {} da parte poligonal {}.'
                                    ).format(ring_index, polygon_index),
                                    point=hole_point,
                                    value=hole_area,
                                    threshold=min_hole_area
                                )
                    except Exception as error:
                        feedback.pushWarning(self.tr(
                            'Holes could not be inspected in feature {} of layer {}: {}',
                            'Os buracos não puderam ser inspecionados na feição {} da camada {}: {}'
                        ).format(feature_id, layer.name(), str(error)))

                if total_features:
                    feedback.setProgress(int(processed * 100.0 / total_features))

            if feedback.isCanceled():
                break

        self._write_report(
            html_output,
            layers,
            layer_feature_counts,
            layer_counts,
            rule_counts,
            occurrences,
            tolerance,
            check_multipart,
            check_small_angle,
            min_angle,
            check_min_size,
            min_length,
            min_area,
            check_holes,
            min_hole_area
        )

        settings = QgsSettings()
        settings.setValue(
            self.SETTINGS_PREFIX + 'duplicateTolerance', tolerance
        )
        settings.setValue(
            self.SETTINGS_PREFIX + 'checkMultipart', check_multipart
        )
        settings.setValue(
            self.SETTINGS_PREFIX + 'checkSmallAngle', check_small_angle
        )
        settings.setValue(
            self.SETTINGS_PREFIX + 'minAngle', min_angle
        )
        settings.setValue(
            self.SETTINGS_PREFIX + 'checkMinimumSize', check_min_size
        )
        settings.setValue(
            self.SETTINGS_PREFIX + 'minLength', min_length
        )
        settings.setValue(
            self.SETTINGS_PREFIX + 'minArea', min_area
        )
        settings.setValue(
            self.SETTINGS_PREFIX + 'checkHoles', check_holes
        )
        settings.setValue(
            self.SETTINGS_PREFIX + 'minHoleArea', min_hole_area
        )

        if occurrences:
            feedback.reportError(self.tr(
                '{} geometry validation occurrence(s) were found.',
                'Foram encontradas {} ocorrência(s) na validação geométrica.'
            ).format(len(occurrences)), fatalError=False)
        else:
            feedback.pushInfo(self.tr(
                'No geometry validation occurrences were found.',
                'Nenhuma ocorrência foi encontrada na validação geométrica.'
            ))

        feedback.pushInfo(self.tr(
            'Operation completed successfully!',
            'Operação finalizada com sucesso!'
        ))
        feedback.pushInfo('Leandro França - Eng Cart')

        # Store the destination for styling in postProcessAlgorithm(), when
        # the output layer is already available in the processing context.
        self.ERROR_LAYER_DEST = error_dest

        return {
            self.ERRORS: error_dest,
            self.OCCURRENCES: occurrence_dest,
            self.HTML: html_output,
        }

    def postProcessAlgorithm(self, context, feedback):
        error_layer = QgsProcessingUtils.mapLayerFromString(
            self.ERROR_LAYER_DEST, context
        )
        if error_layer is None:
            return {}

        # Red point symbol used to emphasize every located geometry problem.
        renderer = SymbolSimplePoint(
            error_layer,
            cor=QColor(255, 0, 0),
            tamanho=3.0,
            tipo='circle',
            cor_borda=QColor(120, 0, 0),
            largura_borda=0.3,
            opacidade=1.0
        )
        error_layer.setRenderer(renderer)

        # Start from the standard LFTools labeling configuration and replace
        # its field with a multiline QGIS expression. coalesce() prevents a
        # null detail or value from suppressing the complete label.
        labeling = LabelConf(
            'rule_id',
            fonte='Arial',
            tam=9,
            bold=True,
            cor='white',
            buffer_tam=0.8,
            buffer_cor='black',
            dist=2
        )
        label_settings = labeling.settings()
        label_settings.fieldName = (
            'coalesce("rule_id", \'\') || \': \' || '
            'coalesce("rule", \'\') || \'\\n\' || '
            'coalesce("layer", \'\') || \'\\n\' || '
            'coalesce(to_string("feature_id"), \'\') || '
            'CASE WHEN coalesce("detail", \'\') <> \'\' '
            'THEN \'\\n\' || "detail" ELSE \'\' END'
        )
        label_settings.isExpression = True
        error_layer.setLabeling(QgsVectorLayerSimpleLabeling(label_settings))
        error_layer.setLabelsEnabled(True)
        error_layer.triggerRepaint()

        return {}

    def _write_report(self, html_output, layers, layer_feature_counts,
                      layer_counts, rule_counts, occurrences, tolerance,
                      check_multipart, check_small_angle, min_angle,
                      check_min_size, min_length, min_area,
                      check_holes, min_hole_area):
        total_features = sum(layer_feature_counts.values())
        total_occurrences = len(occurrences)
        affected = len({
            (item['layer'], item['feature_id']) for item in occurrences
        })
        status = self.tr('NONCONFORMING', 'NÃO CONFORME') if occurrences else self.tr(
            'CONFORMING', 'CONFORME'
        )
        status_class = 'bad' if occurrences else 'ok'

        layer_rows = ''
        for layer in layers:
            geometry_name = QgsWkbTypes.displayString(layer.wkbType())
            layer_rows += '''<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>'''.format(
                str2HTML(layer.name()),
                str2HTML(geometry_name),
                layer_feature_counts[layer.name()],
                layer_counts[layer.name()],
                str2HTML(layer.crs().authid())
            )

        rule_rows = ''
        enabled_rules = ['VGE001', 'VGE002', 'VGE003', 'VGE004']
        if check_multipart:
            enabled_rules.append('VGE005')
        if check_small_angle:
            enabled_rules.append('VGE006')
        if check_min_size:
            enabled_rules.extend(['VGE007', 'VGE008'])
        if check_holes:
            enabled_rules.append('VGE009')

        for rule_id in enabled_rules:
            count = rule_counts[rule_id]
            result = self.tr('Nonconforming', 'Não conforme') if count else self.tr(
                'Conforming', 'Conforme'
            )
            css_class = 'bad' if count else 'ok'
            rule_rows += '''<tr><td>{}</td><td>{}</td><td>{}</td><td class="{}">{}</td></tr>'''.format(
                rule_id,
                str2HTML(self._rule_name(rule_id)),
                count,
                css_class,
                str2HTML(result)
            )

        parameters_rows = '''
<tr><td>{}</td><td>{}</td></tr>
<tr><td>{}</td><td>{}</td></tr>
<tr><td>{}</td><td>{}</td></tr>
<tr><td>{}</td><td>{}</td></tr>
<tr><td>{}</td><td>{}</td></tr>
<tr><td>{}</td><td>{}</td></tr>
'''.format(
            str2HTML(self.tr('Duplicated vertex tolerance', 'Tolerância de vértice duplicado')),
            '{} m'.format(tolerance),
            str2HTML(self.tr('Report multipart geometries', 'Reportar geometrias multipartes')),
            self.tr('Yes', 'Sim') if check_multipart else self.tr('No', 'Não'),
            str2HTML(self.tr('Minimum angle', 'Ângulo mínimo')),
            '{}°'.format(min_angle) if check_small_angle else self.tr('Not evaluated', 'Não avaliado'),
            str2HTML(self.tr('Minimum line length', 'Comprimento mínimo das linhas')),
            '{} m'.format(min_length) if check_min_size else self.tr('Not evaluated', 'Não avaliado'),
            str2HTML(self.tr('Minimum polygon area', 'Área mínima dos polígonos')),
            '{} m²'.format(min_area) if check_min_size else self.tr('Not evaluated', 'Não avaliada'),
            str2HTML(self.tr('Minimum allowed hole area', 'Área mínima permitida para buracos')),
            '{} m²'.format(min_hole_area) if check_holes else self.tr('Not evaluated', 'Não avaliada')
        )

        interpretation = self.tr(
            'The complete automated inspection evaluated {} feature(s) from {} vector layer(s). '
            '{} occurrence(s) were identified in {} feature(s). The dataset is classified as {} '
            'for the geometry rules enabled in this execution. The input layers were not modified.',

            'A inspeção completa automatizada avaliou {} feição(ões) de {} camada(s) vetorial(is). '
            'Foram identificadas {} ocorrência(s) em {} feição(ões). O conjunto de dados foi classificado '
            'como {} para as regras geométricas habilitadas nesta execução. As camadas de entrada não foram modificadas.'
        ).format(
            total_features,
            len(layers),
            total_occurrences,
            affected,
            status
        )

        report = '''<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>''' + str2HTML(self.tr(
            'GEOMETRY VALIDATION REPORT', 'RELATÓRIO DE VALIDAÇÃO DE GEOMETRIAS'
        )) + '''</title>
  <link rel="icon" href="https://github.com/LEOXINGU/lftools/blob/main/images/lftools.png?raw=true" type="image/x-icon">
  <style>
    body { font-family:Arial,sans-serif; background:#f4f6f0; color:#222; margin:0; padding:0; }
    .page { max-width:1100px; margin:24px auto; background:white; padding:32px; border-radius:12px; box-shadow:0 2px 12px rgba(0,0,0,.12); }
    .header { text-align:center; border-bottom:3px solid #365f2c; padding-bottom:16px; margin-bottom:24px; }
    .header img { height:72px; }
    h1 { color:#274e22; font-size:24px; margin:12px 0 4px 0; }
    h2 { color:#365f2c; font-size:18px; border-bottom:1px solid #ddd; padding-bottom:6px; margin-top:28px; }
    .subtitle { color:#666; font-size:13px; }
    .cards { display:grid; grid-template-columns:repeat(4,1fr); gap:12px; margin:20px 0; }
    .card { background:#eef5ea; border-left:5px solid #365f2c; padding:14px; border-radius:8px; }
    .label { color:#666; font-size:12px; text-transform:uppercase; }
    .big { font-size:22px; font-weight:bold; color:#1f3f1b; margin-top:6px; }
    table { width:100%; border-collapse:collapse; margin:12px 0; font-size:13px; }
    th { background:#365f2c; color:white; padding:8px; text-align:left; }
    td { border:1px solid #ddd; padding:8px; }
    tr:nth-child(even) { background:#f8f8f8; }
    .note { background:#fff8dc; border-left:5px solid #c9a227; padding:12px; margin:12px 0; border-radius:6px; }
    .ok { color:#1f7a1f; font-weight:bold; }
    .bad { color:#a00000; font-weight:bold; }
    .footer { margin-top:30px; border-top:1px solid #ccc; padding-top:12px; color:#555; font-size:12px; }
    @media (max-width:760px) { .cards { grid-template-columns:1fr 1fr; } }
  </style>
</head>
<body>
<div class="page">
<div class="header">
  <img src="data:image/png;base64,''' + lftools_logo + '''">
  <h1>''' + str2HTML(self.tr(
            'GEOMETRY VALIDATION REPORT', 'RELATÓRIO DE VALIDAÇÃO DE GEOMETRIAS'
        )) + '''</h1>
  <div class="subtitle">LFTools | ''' + str2HTML(self.tr(
            'Individual geometry inspection', 'Inspeção da geometria individual'
        )) + ''' | ''' + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + '''</div>
</div>

<div class="cards">
  <div class="card"><div class="label">''' + str2HTML(self.tr(
            'Evaluated features', 'Feições avaliadas'
        )) + '''</div><div class="big">''' + str(total_features) + '''</div></div>
  <div class="card"><div class="label">''' + str2HTML(self.tr(
            'Occurrences', 'Ocorrências'
        )) + '''</div><div class="big">''' + str(total_occurrences) + '''</div></div>
  <div class="card"><div class="label">''' + str2HTML(self.tr(
            'Affected features', 'Feições afetadas'
        )) + '''</div><div class="big">''' + str(affected) + '''</div></div>
  <div class="card"><div class="label">''' + str2HTML(self.tr(
            'Result', 'Resultado'
        )) + '''</div><div class="big ''' + status_class + '''">''' + str2HTML(status) + '''</div></div>
</div>

<h2>''' + str2HTML(self.tr('1. Evaluated Data', '1. Dados Avaliados')) + '''</h2>
<table><tr><th>''' + str2HTML(self.tr('Layer', 'Camada')) + '''</th><th>''' + str2HTML(self.tr('Geometry', 'Geometria')) + '''</th><th>''' + str2HTML(self.tr('Features', 'Feições')) + '''</th><th>''' + str2HTML(self.tr('Occurrences', 'Ocorrências')) + '''</th><th>''' + str2HTML(self.tr('CRS', 'SRC')) + '''</th></tr>''' + layer_rows + '''</table>

<h2>''' + str2HTML(self.tr('2. Methodology', '2. Metodologia')) + '''</h2>
<p>''' + str2HTML(self.tr(
            'A complete automated inspection was performed on every feature. Each geometry was evaluated independently, without changing the source data. Spatially identifiable problems were written to a point layer, while all occurrences, including those without a valid spatial location, were recorded in a non-spatial table.',
            'Foi realizada uma inspeção completa automatizada de todas as feições. Cada geometria foi avaliada individualmente, sem alteração dos dados de origem. Os problemas espacialmente identificáveis foram registrados em uma camada pontual, enquanto todas as ocorrências, inclusive aquelas sem localização espacial válida, foram armazenadas em uma tabela não espacial.'
        )) + '''</p>

<h2>''' + str2HTML(self.tr('3. Parameters', '3. Parâmetros')) + '''</h2>
<table><tr><th>''' + str2HTML(self.tr('Parameter', 'Parâmetro')) + '''</th><th>''' + str2HTML(self.tr('Value', 'Valor')) + '''</th></tr>''' + parameters_rows + '''</table>

<h2>''' + str2HTML(self.tr('4. Results by Rule', '4. Resultados por Regra')) + '''</h2>
<table><tr><th>ID</th><th>''' + str2HTML(self.tr('Rule', 'Regra')) + '''</th><th>''' + str2HTML(self.tr('Occurrences', 'Ocorrências')) + '''</th><th>''' + str2HTML(self.tr('Result', 'Resultado')) + '''</th></tr>''' + rule_rows + '''</table>

<h2>''' + str2HTML(self.tr('5. Automatic Interpretation', '5. Interpretação Automática')) + '''</h2>
<div class="note">''' + str2HTML(interpretation) + '''</div>

<div class="footer">Leandro França 2026<br>Cartographic Engineer<br>email: contato@geoone.com.br</div>
</div>
</body>
</html>'''

        with open(html_output, 'w', encoding='utf-8') as report_file:
            report_file.write(report)
