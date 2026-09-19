# -*- coding: utf-8 -*-

"""
Qualy_ValidateIntraclassTopology.py
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
from math import ceil, floor, isfinite, log10
import os

import processing

from qgis.PyQt.QtCore import QMetaType
from qgis.PyQt.QtGui import QColor, QIcon
from qgis.core import (
    QgsApplication,
    QgsCoordinateReferenceSystem,
    QgsCoordinateTransform,
    QgsFeature,
    QgsFeatureSink,
    QgsField,
    QgsFields,
    QgsGeometry,
    QgsPointXY,
    QgsProcessing,
    QgsProcessingAlgorithm,
    QgsProcessingException,
    QgsProcessingParameterBoolean,
    QgsProcessingParameterFeatureSink,
    QgsProcessingParameterFeatureSource,
    QgsProcessingParameterFileDestination,
    QgsProcessingParameterMultipleLayers,
    QgsProcessingParameterNumber,
    QgsProcessingUtils,
    QgsRectangle,
    QgsSettings,
    QgsSpatialIndex,
    QgsVectorLayerSimpleLabeling,
    QgsVectorLayer,
    QgsWkbTypes,
    Qgis,
)

from lftools.geocapt.imgs import Imgs, lftools_logo
from lftools.geocapt.cartography import LabelConf, SymbolSimplePoint
from lftools.geocapt.topogeo import str2HTML
from lftools.translations.translate import translate


class ValidateIntraclassTopology(QgsProcessingAlgorithm):

    INPUTS = 'INPUTS'
    MAPPING_AREA = 'MAPPING_AREA'
    BOUNDARY_TOLERANCE = 'BOUNDARY_TOLERANCE'
    TOPOLOGY_TOLERANCE = 'TOPOLOGY_TOLERANCE'
    NEAR_TOLERANCE = 'NEAR_TOLERANCE'
    MIN_OVERLAP_LENGTH = 'MIN_OVERLAP_LENGTH'
    MIN_OVERLAP_AREA = 'MIN_OVERLAP_AREA'
    CHECK_DANGLES = 'CHECK_DANGLES'
    CHECK_GAPS = 'CHECK_GAPS'
    MAX_GAP_AREA = 'MAX_GAP_AREA'
    CHECK_MISSING_VERTICES = 'CHECK_MISSING_VERTICES'
    ERRORS = 'ERRORS'
    HTML = 'HTML'

    SETTINGS_PREFIX = 'LFTools/ValidateIntraclassTopology/'
    LOC = QgsApplication.locale()[:2]

    RULES = {
        'VTI001': ('Coincident points', 'Pontos coincidentes'),
        'VTI002': ('Duplicated geometries', 'Geometrias duplicadas'),
        'VTI003': ('Overlapping line segments', 'Segmentos de linha sobrepostos'),
        'VTI004': ('Intersection without corresponding vertex', 'Interseção sem vértice correspondente'),
        'VTI005': ('Dangle end', 'Extremidade pendente'),
        'VTI006': ('Near disconnected ends', 'Extremidades próximas e desconectadas'),
        'VTI007': ('Overlapping polygons', 'Polígonos sobrepostos'),
        'VTI008': ('Polygon inside polygon', 'Polígono contido em outro polígono'),
        'VTI009': ('Small gap between polygons', 'Pequena lacuna entre polígonos'),
        'VTI010': ('Missing vertex along shared border', 'Vértice ausente em limite comum'),
    }

    def tr(self, *string):
        return translate(string, self.LOC)

    def createInstance(self):
        return ValidateIntraclassTopology()

    def name(self):
        return 'validateintraclasstopology'

    def displayName(self):
        return self.tr(
            'Validate Intraclass Topology',
            'Validar Topologia Intraclasse'
        )

    def group(self):
        return self.tr('Quality', 'Qualidade')

    def groupId(self):
        return 'quality'

    def tags(self):
        return (
            'GeoOne,quality,qualidade,topology,topologia,intraclass,intraclasse,'
            'duplicate,coincident,overlap,dangle,gap,missing vertex,shared border,'
            'logical consistency,consistência lógica,QGIS,LFTools'
        ).split(',')

    def icon(self):
        return QIcon(os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'images/quality.png'
        ))

    txt_en = '''
<p>This tool performs an <b>automated intraclass topological validation</b> of one or more point, line, or polygon layers. Each layer is evaluated independently.</p>
<p><b>Checks:</b></p>
▪️ Coincident points and duplicated geometries;<br>
▪️ Overlapping line segments and intersections without corresponding vertices;<br>
▪️ Dangle ends and near disconnected ends, except those located near the optional mapping boundary;<br>
▪️ Polygon overlaps, containment, small gaps, and missing vertices along shared borders.
<p><b>Outputs:</b> a point layer containing all located errors and their attributes, and an HTML quality report.</p>
<p>An optional single-polygon mapping area can be used to accept otherwise disconnected line ends located within the defined boundary tolerance.</p>
<p>Feature identifiers are obtained automatically from each layer provider's primary key. When no primary key is declared, the internal QGIS feature ID is used. Gaps receive an occurrence ID and list the adjacent polygons, but do not receive a feature ID of their own.</p>
<p>Linear tolerances are expressed in <b>metres</b> and area thresholds in <b>square metres</b>. Geographic and projected CRS are accepted; when necessary, the tool creates an internal local metric CRS for the validation.</p>
<p>Distance and area thresholds must consider the reference scale, input resolution, feature class, and intended use. Some occurrences may represent intentional spatial arrangements and must be technically reviewed.</p>
<p style="color:#b00020;"><b>Important:</b> validate and correct individual geometries before running this tool. Null, empty, or invalid geometries are ignored and reported in the execution summary. Input layers are not modified or automatically corrected.</p>
'''

    txt_pt = '''
<p>Esta ferramenta realiza a <b>validação topológica intraclasse automatizada</b> de uma ou mais camadas de pontos, linhas ou polígonos. Cada camada é avaliada de forma independente.</p>
<p><b>Verificações:</b></p>
▪️ Pontos coincidentes e geometrias duplicadas;
▪️ Segmentos de linha sobrepostos e interseções sem vértices correspondentes;
▪️ Extremidades pendentes e extremidades próximas desconectadas, exceto aquelas próximas ao limite opcional da área de mapeamento;
▪️ Sobreposições, contenções, pequenas lacunas e vértices ausentes em limites comuns de polígonos.
<p><b>Saídas:</b> camada pontual contendo todos os erros localizados e seus atributos, e relatório de qualidade em HTML.</p>
<p>Uma área de mapeamento opcional, contendo uma única feição poligonal, pode ser utilizada para aceitar extremidades de linhas desconectadas situadas dentro da tolerância definida para a fronteira.</p>
<p>Os identificadores das feições são obtidos automaticamente pela chave primária declarada pelo provedor de cada camada. Quando não existe uma chave primária declarada, utiliza-se o identificador interno da feição no QGIS. As lacunas recebem um identificador de ocorrência e apresentam os polígonos adjacentes, mas não recebem um identificador de feição próprio.</p>
<p>As tolerâncias lineares são expressas em <b>metros</b> e os limites de área em <b>metros quadrados</b>. São aceitos SRC geográficos e projetados; quando necessário, a ferramenta cria internamente um SRC métrico local para realizar a validação.</p>
<p>As tolerâncias lineares e de área devem considerar a escala de referência, a resolução do insumo, a classe da feição e a finalidade de utilização. Algumas ocorrências podem representar configurações espaciais intencionais e devem ser analisadas tecnicamente.</p>
<p style="color:#b00020;"><b>Importante:</b> valide e corrija as geometrias individuais antes de executar esta ferramenta. Geometrias nulas, vazias ou inválidas são ignoradas e contabilizadas no resumo da execução. As camadas de entrada não são modificadas nem corrigidas automaticamente.</p>
'''

    figure = 'images/tutorial/qualy_validate_intraclass_topology.jpg'

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
        topology_tolerance = settings.value(
            self.SETTINGS_PREFIX + 'topologyTolerance', 0.01, type=float
        )
        near_tolerance = settings.value(
            self.SETTINGS_PREFIX + 'nearTolerance', 0.20, type=float
        )
        min_overlap_length = settings.value(
            self.SETTINGS_PREFIX + 'minimumOverlapLength', 0.01, type=float
        )
        min_overlap_area = settings.value(
            self.SETTINGS_PREFIX + 'minimumOverlapArea', 0.0001, type=float
        )
        check_dangles = settings.value(
            self.SETTINGS_PREFIX + 'checkDangles', True, type=bool
        )
        check_gaps = settings.value(
            self.SETTINGS_PREFIX + 'checkGaps', True, type=bool
        )
        max_gap_area = settings.value(
            self.SETTINGS_PREFIX + 'maximumGapArea', 0.04, type=float
        )
        check_missing_vertices = settings.value(
            self.SETTINGS_PREFIX + 'checkMissingVertices', True, type=bool
        )
        boundary_tolerance = settings.value(
            self.SETTINGS_PREFIX + 'boundaryTolerance', 1.20, type=float
        )

        self.addParameter(QgsProcessingParameterMultipleLayers(
            self.INPUTS,
            self.tr('Vector layers', 'Camadas vetoriais'),
            QgsProcessing.TypeVectorAnyGeometry
        ))
        self.addParameter(QgsProcessingParameterFeatureSource(
            self.MAPPING_AREA,
            self.tr(
                'Mapping area (optional single polygon)',
                'Área de mapeamento (polígono único opcional)'
            ),
            types=[QgsProcessing.TypeVectorPolygon],
            optional=True
        ))
        self.addParameter(QgsProcessingParameterNumber(
            self.BOUNDARY_TOLERANCE,
            self.tr(
                'Mapping boundary tolerance for line ends (m)',
                'Tolerância da fronteira da área de mapeamento para extremidades de linhas (m)'
            ),
            type=QgsProcessingParameterNumber.Type.Double,
            defaultValue=boundary_tolerance,
            minValue=0.0
        ))
        self.addParameter(QgsProcessingParameterNumber(
            self.TOPOLOGY_TOLERANCE,
            self.tr(
                'Topological coincidence tolerance (m)',
                'Tolerância de coincidência topológica (m)'
            ),
            type=QgsProcessingParameterNumber.Type.Double,
            defaultValue=topology_tolerance,
            minValue=0.0
        ))
        self.addParameter(QgsProcessingParameterNumber(
            self.NEAR_TOLERANCE,
            self.tr(
                'Maximum distance for near disconnected ends (m)',
                'Distância máxima para extremidades próximas desconectadas (m)'
            ),
            type=QgsProcessingParameterNumber.Type.Double,
            defaultValue=near_tolerance,
            minValue=0.0
        ))
        self.addParameter(QgsProcessingParameterNumber(
            self.MIN_OVERLAP_LENGTH,
            self.tr(
                'Minimum line overlap length to report (m)',
                'Comprimento mínimo de sobreposição linear a reportar (m)'
            ),
            type=QgsProcessingParameterNumber.Type.Double,
            defaultValue=min_overlap_length,
            minValue=0.0
        ))
        self.addParameter(QgsProcessingParameterNumber(
            self.MIN_OVERLAP_AREA,
            self.tr(
                'Minimum polygon overlap area to report (m²)',
                'Área mínima de sobreposição de polígonos a reportar (m²)'
            ),
            type=QgsProcessingParameterNumber.Type.Double,
            defaultValue=min_overlap_area,
            minValue=0.0
        ))
        self.addParameter(QgsProcessingParameterBoolean(
            self.CHECK_DANGLES,
            self.tr(
                'Check dangle and near disconnected line ends',
                'Verificar extremidades pendentes e próximas desconectadas'
            ),
            defaultValue=check_dangles
        ))
        self.addParameter(QgsProcessingParameterBoolean(
            self.CHECK_GAPS,
            self.tr(
                'Check small gaps between polygons',
                'Verificar pequenas lacunas entre polígonos'
            ),
            defaultValue=check_gaps
        ))
        self.addParameter(QgsProcessingParameterNumber(
            self.MAX_GAP_AREA,
            self.tr(
                'Maximum gap area to report (m²; 0 reports all)',
                'Área máxima da lacuna a reportar (m²; 0 reporta todas)'
            ),
            type=QgsProcessingParameterNumber.Type.Double,
            defaultValue=max_gap_area,
            minValue=0.0
        ))
        self.addParameter(QgsProcessingParameterBoolean(
            self.CHECK_MISSING_VERTICES,
            self.tr(
                'Check missing vertices along shared polygon borders',
                'Verificar vértices ausentes em limites comuns de polígonos'
            ),
            defaultValue=check_missing_vertices
        ))
        self.addParameter(QgsProcessingParameterFeatureSink(
            self.ERRORS,
            self.tr('Located topological errors', 'Erros topológicos localizados'),
            type=Qgis.ProcessingSourceType.TypeVectorPoint
        ))
        self.addParameter(QgsProcessingParameterFileDestination(
            self.HTML,
            self.tr(
                'Intraclass topology validation report',
                'Relatório de validação topológica intraclasse'
            ),
            self.tr('HTML files (*.html)')
        ))

    def _rule_name(self, rule_id):
        return self.tr(*self.RULES[rule_id])

    def _geometry_type_name(self, layer):
        geometry_type = QgsWkbTypes.geometryType(layer.wkbType())
        if geometry_type == QgsWkbTypes.PointGeometry:
            return self.tr('Point', 'Ponto')
        if geometry_type == QgsWkbTypes.LineGeometry:
            return self.tr('Line', 'Linha')
        if geometry_type == QgsWkbTypes.PolygonGeometry:
            return self.tr('Polygon', 'Polígono')
        return self.tr('Unknown', 'Desconhecida')

    @staticmethod
    def _point_geometry(point):
        return QgsGeometry.fromPointXY(QgsPointXY(point))

    @staticmethod
    def _finite_point(point):
        return (
            point is not None
            and isfinite(point.x())
            and isfinite(point.y())
        )

    @staticmethod
    def _representative_point(geometry):
        if geometry is None or geometry.isNull() or geometry.isEmpty():
            return None
        geometry_type = QgsWkbTypes.geometryType(geometry.wkbType())
        if geometry_type == QgsWkbTypes.PointGeometry:
            try:
                point = geometry.asPoint()
                if ValidateIntraclassTopology._finite_point(point):
                    return QgsPointXY(point)
            except Exception:
                pass
        try:
            point = geometry.pointOnSurface().asPoint()
            if ValidateIntraclassTopology._finite_point(point):
                return QgsPointXY(point)
        except Exception:
            pass
        try:
            for vertex in geometry.vertices():
                if ValidateIntraclassTopology._finite_point(vertex):
                    return QgsPointXY(vertex)
        except Exception:
            pass
        return None

    @staticmethod
    def _extract_points(geometry):
        if geometry is None or geometry.isNull() or geometry.isEmpty():
            return []
        geometry_type = QgsWkbTypes.geometryType(geometry.wkbType())
        if geometry_type == QgsWkbTypes.PointGeometry:
            if geometry.isMultipart():
                return [QgsPointXY(point) for point in geometry.asMultiPoint()]
            return [QgsPointXY(geometry.asPoint())]
        if QgsWkbTypes.flatType(geometry.wkbType()) == QgsWkbTypes.GeometryCollection:
            points = []
            for part in geometry.asGeometryCollection():
                points.extend(ValidateIntraclassTopology._extract_points(part))
            return points
        return []

    @staticmethod
    def _line_endpoints(geometry):
        if geometry.isMultipart():
            lines = geometry.asMultiPolyline()
        else:
            lines = [geometry.asPolyline()]
        endpoints = []
        for line in lines:
            if line:
                endpoints.append(QgsPointXY(line[0]))
                if len(line) > 1:
                    endpoints.append(QgsPointXY(line[-1]))
        return endpoints

    @staticmethod
    def _vertices(geometry):
        vertices = []
        try:
            for vertex in geometry.vertices():
                if ValidateIntraclassTopology._finite_point(vertex):
                    vertices.append(QgsPointXY(vertex))
        except Exception:
            pass
        return vertices

    @staticmethod
    def _polygon_boundary(geometry):
        """Build a polygon boundary without relying on QgsGeometry.boundary()."""
        polygons = geometry.asMultiPolygon() if geometry.isMultipart() else [
            geometry.asPolygon()
        ]
        rings = []
        for polygon in polygons:
            for ring in polygon:
                if ring:
                    rings.append([QgsPointXY(point) for point in ring])
        if not rings:
            return QgsGeometry()
        return QgsGeometry.fromMultiPolylineXY(rings)

    @staticmethod
    def _has_vertex(vertices, point, tolerance):
        point_geometry = ValidateIntraclassTopology._point_geometry(point)
        return any(
            point_geometry.distance(
                ValidateIntraclassTopology._point_geometry(vertex)
            ) <= tolerance
            for vertex in vertices
        )

    @staticmethod
    def _search_rectangle(point, distance):
        return QgsRectangle(
            point.x() - distance,
            point.y() - distance,
            point.x() + distance,
            point.y() + distance
        )

    @staticmethod
    def _valid_features(layer):
        valid = []
        skipped = 0
        for feature in layer.getFeatures():
            geometry = feature.geometry()
            if geometry is None or geometry.isNull() or geometry.isEmpty():
                skipped += 1
                continue
            try:
                validation_errors = geometry.validateGeometry()
            except TypeError:
                validation_errors = []
                geometry.validateGeometry(validation_errors)
            if validation_errors:
                skipped += 1
                continue
            valid.append(feature)
        return valid, skipped

    @staticmethod
    def _feature_identifier(layer, feature):
        """Return the provider primary key, falling back to the QGIS feature id."""
        try:
            primary_key_indexes = list(
                layer.dataProvider().pkAttributeIndexes()
            )
        except Exception:
            primary_key_indexes = []
        if primary_key_indexes:
            key_parts = []
            for field_index in primary_key_indexes:
                field_name = layer.fields().at(field_index).name()
                value = feature.attribute(field_index)
                value_text = '' if value is None else str(value)
                if len(primary_key_indexes) == 1:
                    return value_text
                key_parts.append('{}={}'.format(field_name, value_text))
            if key_parts:
                return '; '.join(key_parts)
        return str(feature.id())

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

    def _metric_features(self, features, transform):
        if transform is None:
            return features
        metric_features = []
        for feature in features:
            metric_feature = QgsFeature(feature)
            metric_feature.setId(feature.id())
            metric_feature.setGeometry(
                self._metric_geometry(feature.geometry(), transform)
            )
            metric_features.append(metric_feature)
        return metric_features

    def _source_point(self, point, transform):
        source_point = QgsPointXY(point)
        if transform is not None:
            try:
                source_point = transform.transform(source_point)
            except Exception as error:
                raise QgsProcessingException(self.tr(
                    'An error location could not be transformed back to the input CRS: {}',
                    'Uma localização de erro não pôde ser transformada de volta para o SRC de entrada: {}'
                ).format(str(error)))
        return source_point

    def processAlgorithm(self, parameters, context, feedback):
        layers = self.parameterAsLayerList(parameters, self.INPUTS, context)
        if not layers:
            raise QgsProcessingException(self.tr(
                'Select at least one vector layer!',
                'Selecione pelo menos uma camada vetorial!'
            ))

        first_crs = layers[0].crs()
        incompatible = [layer.name() for layer in layers if layer.crs() != first_crs]
        if incompatible:
            raise QgsProcessingException(self.tr(
                'All input layers must use the same CRS. Incompatible layers: {}',
                'Todas as camadas de entrada devem utilizar o mesmo SRC. Camadas incompatíveis: {}'
            ).format(', '.join(incompatible)))

        working_crs, to_metric, from_metric = self._metric_working_context(
            layers, context
        )
        if to_metric is None:
            feedback.pushInfo(self.tr(
                'Validation will use the input CRS in metres ({}).',
                'A validação utilizará o SRC de entrada em metros ({}).'
            ).format(working_crs.authid()))
        else:
            feedback.pushInfo(self.tr(
                'Validation will use the local metric working CRS {}. Error locations will be returned in the input CRS.',
                'A validação utilizará o SRC métrico local de trabalho {}. As localizações dos erros serão retornadas no SRC de entrada.'
            ).format(working_crs.authid()))

        mapping_source = self.parameterAsSource(
            parameters, self.MAPPING_AREA, context
        )
        mapping_boundary = None
        mapping_area_name = self.tr('Not provided', 'Não fornecida')
        if mapping_source is not None:
            if mapping_source.sourceCrs() != first_crs:
                raise QgsProcessingException(self.tr(
                    'The mapping area and all input layers must use the same CRS.',
                    'A área de mapeamento e todas as camadas de entrada devem utilizar o mesmo SRC.'
                ))
            if mapping_source.featureCount() != 1:
                raise QgsProcessingException(self.tr(
                    'The mapping area must contain exactly one polygon feature.',
                    'A área de mapeamento deve conter exatamente uma feição poligonal.'
                ))
            mapping_feature = next(mapping_source.getFeatures(), None)
            mapping_geometry = (
                mapping_feature.geometry() if mapping_feature is not None else None
            )
            if (
                mapping_geometry is None
                or mapping_geometry.isNull()
                or mapping_geometry.isEmpty()
            ):
                raise QgsProcessingException(self.tr(
                    'The mapping area has a null or empty geometry.',
                    'A área de mapeamento possui geometria nula ou vazia.'
                ))
            try:
                mapping_errors = mapping_geometry.validateGeometry()
            except TypeError:
                mapping_errors = []
                mapping_geometry.validateGeometry(mapping_errors)
            if mapping_errors:
                raise QgsProcessingException(self.tr(
                    'The mapping area geometry is invalid. Correct it before validation.',
                    'A geometria da área de mapeamento é inválida. Corrija-a antes da validação.'
                ))
            metric_mapping_geometry = self._metric_geometry(
                mapping_geometry, to_metric
            )
            mapping_boundary = self._polygon_boundary(metric_mapping_geometry)
            mapping_area_name = (
                mapping_source.sourceName()
                if hasattr(mapping_source, 'sourceName')
                else self.tr('Provided', 'Fornecida')
            )

        topology_tolerance = self.parameterAsDouble(
            parameters, self.TOPOLOGY_TOLERANCE, context
        )
        near_tolerance = self.parameterAsDouble(
            parameters, self.NEAR_TOLERANCE, context
        )
        boundary_tolerance = self.parameterAsDouble(
            parameters, self.BOUNDARY_TOLERANCE, context
        )
        min_overlap_length = self.parameterAsDouble(
            parameters, self.MIN_OVERLAP_LENGTH, context
        )
        min_overlap_area = self.parameterAsDouble(
            parameters, self.MIN_OVERLAP_AREA, context
        )
        check_dangles = self.parameterAsBool(parameters, self.CHECK_DANGLES, context)
        check_gaps = self.parameterAsBool(parameters, self.CHECK_GAPS, context)
        max_gap_area = self.parameterAsDouble(parameters, self.MAX_GAP_AREA, context)
        check_missing_vertices = self.parameterAsBool(
            parameters, self.CHECK_MISSING_VERTICES, context
        )
        html_output = self.parameterAsFileOutput(parameters, self.HTML, context)

        error_fields = QgsFields()
        error_fields.append(QgsField('occurrence_id', QMetaType.Type.LongLong))
        error_fields.append(QgsField('rule_id', QMetaType.Type.QString))
        error_fields.append(QgsField('rule', QMetaType.Type.QString))
        error_fields.append(QgsField('layer', QMetaType.Type.QString))
        error_fields.append(QgsField('geom_type', QMetaType.Type.QString))
        error_fields.append(QgsField('feature_id', QMetaType.Type.QString))
        error_fields.append(QgsField('related_id', QMetaType.Type.QString))
        error_fields.append(QgsField('involved_ids', QMetaType.Type.QString))
        error_fields.append(QgsField('detail', QMetaType.Type.QString))
        error_fields.append(QgsField('value', QMetaType.Type.Double))
        error_fields.append(QgsField('tolerance', QMetaType.Type.Double))

        error_sink, error_dest = self.parameterAsSink(
            parameters, self.ERRORS, context, error_fields,
            QgsWkbTypes.Point, first_crs
        )
        if error_sink is None:
            raise QgsProcessingException(self.invalidSinkError(parameters, self.ERRORS))
        occurrences = []
        layer_counts = Counter()
        rule_counts = Counter()
        skipped_counts = Counter()
        evaluated_counts = Counter()
        boundary_exempt_counts = Counter()
        seen = set()
        occurrence_sequence = 0

        def register(rule_id, layer, feature_id=None, related_id=None,
                     detail='', point=None, value=None, threshold=None,
                     involved_ids=''):
            nonlocal occurrence_sequence
            feature_text = str(feature_id) if feature_id is not None else None
            related_text = str(related_id) if related_id is not None else None
            rounded_point = None
            if point is not None:
                rounded_point = (round(point.x(), 8), round(point.y(), 8))
            key = (
                rule_id, layer.name(), feature_text, related_text,
                str(involved_ids or ''),
                rounded_point
            )
            if key in seen:
                return
            seen.add(key)
            occurrence_sequence += 1

            rule_name = self._rule_name(rule_id)
            geometry_name = self._geometry_type_name(layer)
            located = point is not None and self._finite_point(point)
            output_point = (
                self._source_point(point, from_metric) if located else None
            )
            attributes = [
                occurrence_sequence, rule_id, rule_name, layer.name(),
                geometry_name, feature_text, related_text, str(involved_ids or ''),
                detail, value, threshold
            ]
            if located:
                error = QgsFeature(error_fields)
                error.setGeometry(QgsGeometry.fromPointXY(output_point))
                error.setAttributes(attributes)
                error_sink.addFeature(error, QgsFeatureSink.Flag.FastInsert)
            occurrences.append({
                'occurrence_id': occurrence_sequence,
                'rule_id': rule_id,
                'rule': rule_name,
                'layer': layer.name(),
                'geom_type': geometry_name,
                'feature_id': feature_text,
                'related_id': related_text,
                'involved_ids': str(involved_ids or ''),
                'detail': detail,
                'value': value,
                'threshold': threshold,
                'located': located,
            })
            layer_counts[layer.name()] += 1
            rule_counts[rule_id] += 1

        total_layers = len(layers)
        for layer_number, layer in enumerate(layers, 1):
            if feedback.isCanceled():
                break
            feedback.pushInfo(self.tr(
                'Validating intraclass topology: {}',
                'Validando topologia intraclasse: {}'
            ).format(layer.name()))

            source_features, skipped = self._valid_features(layer)
            skipped_counts[layer.name()] = skipped
            evaluated_counts[layer.name()] = len(source_features)
            if skipped:
                feedback.pushWarning(self.tr(
                    '{} null, empty, or invalid feature(s) were ignored in layer {}.',
                    '{} feição(ões) nula(s), vazia(s) ou inválida(s) foram ignoradas na camada {}.'
                ).format(skipped, layer.name()))
            if not source_features:
                feedback.setProgress(int(layer_number * 100.0 / total_layers))
                continue

            geometry_type = QgsWkbTypes.geometryType(layer.wkbType())
            features = self._metric_features(source_features, to_metric)
            feature_map = {feature.id(): feature for feature in features}
            feature_ids = {
                feature.id(): self._feature_identifier(layer, feature)
                for feature in source_features
            }
            # Some PyQGIS versions do not accept a regular Python list in
            # the QgsSpatialIndex constructor. Insert the features one by
            # one to keep the algorithm compatible across QGIS versions.
            index = QgsSpatialIndex()
            for indexed_feature in features:
                index.addFeature(indexed_feature)

            if geometry_type == QgsWkbTypes.PointGeometry:
                self._validate_points(
                    layer, features, feature_map, feature_ids, index,
                    topology_tolerance, register, feedback
                )
            elif geometry_type == QgsWkbTypes.LineGeometry:
                boundary_exempt_counts[layer.name()] += self._validate_lines(
                    layer, features, feature_map, feature_ids, index,
                    topology_tolerance, near_tolerance,
                    min_overlap_length, check_dangles,
                    mapping_boundary, boundary_tolerance,
                    register, feedback
                )
            elif geometry_type == QgsWkbTypes.PolygonGeometry:
                self._validate_polygons(
                    layer, features, feature_map, feature_ids, index,
                    topology_tolerance, min_overlap_area,
                    check_gaps, max_gap_area, check_missing_vertices,
                    working_crs, register, context, feedback
                )
            feedback.setProgress(int(layer_number * 100.0 / total_layers))

        self._write_report(
            html_output, layers, evaluated_counts, skipped_counts,
            layer_counts, rule_counts, occurrences,
            topology_tolerance, near_tolerance,
            min_overlap_length, min_overlap_area,
            check_dangles, check_gaps, max_gap_area,
            check_missing_vertices, mapping_area_name,
            boundary_tolerance, boundary_exempt_counts
        )
        self._save_settings(
            topology_tolerance, near_tolerance,
            min_overlap_length, min_overlap_area,
            check_dangles, check_gaps, max_gap_area,
            check_missing_vertices, boundary_tolerance
        )

        if occurrences:
            feedback.reportError(self.tr(
                '{} intraclass topology occurrence(s) were found.',
                'Foram encontradas {} ocorrência(s) na validação topológica intraclasse.'
            ).format(len(occurrences)), fatalError=False)
        else:
            feedback.pushInfo(self.tr(
                'No intraclass topology occurrences were found.',
                'Nenhuma ocorrência topológica intraclasse foi encontrada.'
            ))
        feedback.pushInfo(self.tr(
            'Operation completed successfully!',
            'Operação finalizada com sucesso!'
        ))
        feedback.pushInfo('Leandro França - Eng Cart')

        self.ERROR_LAYER_DEST = error_dest
        return {
            self.ERRORS: error_dest,
            self.HTML: html_output,
        }

    def _validate_points(self, layer, features, feature_map, feature_ids, index,
                         tolerance, register, feedback):
        for feature in features:
            if feedback.isCanceled():
                return
            point = self._representative_point(feature.geometry())
            if point is None:
                continue
            rectangle = self._search_rectangle(point, tolerance)
            for candidate_id in index.intersects(rectangle):
                if candidate_id <= feature.id() or candidate_id not in feature_map:
                    continue
                candidate = feature_map[candidate_id]
                distance = feature.geometry().distance(candidate.geometry())
                if distance <= tolerance:
                    register(
                        'VTI001', layer, feature_ids[feature.id()],
                        feature_ids[candidate.id()],
                        self.tr(
                            'Distance between points: {}',
                            'Distância entre os pontos: {}'
                        ).format(distance),
                        point, distance, tolerance
                    )

    def _validate_lines(self, layer, features, feature_map, feature_ids, index,
                        tolerance, near_tolerance, min_overlap_length,
                        check_dangles, mapping_boundary, boundary_tolerance,
                        register, feedback):
        boundary_exempt = 0
        vertices = {
            feature.id(): self._vertices(feature.geometry())
            for feature in features
        }
        for feature in features:
            if feedback.isCanceled():
                return boundary_exempt
            geometry = feature.geometry()
            rectangle = geometry.boundingBox()
            rectangle.grow(max(tolerance, near_tolerance))
            for candidate_id in index.intersects(rectangle):
                if candidate_id <= feature.id() or candidate_id not in feature_map:
                    continue
                candidate = feature_map[candidate_id]
                candidate_geometry = candidate.geometry()
                if geometry.equals(candidate_geometry):
                    register(
                        'VTI002', layer, feature_ids[feature.id()],
                        feature_ids[candidate.id()],
                        point=self._representative_point(geometry)
                    )
                    continue
                if not geometry.intersects(candidate_geometry):
                    continue
                intersection = geometry.intersection(candidate_geometry)
                intersection_type = QgsWkbTypes.geometryType(intersection.wkbType())
                if intersection_type == QgsWkbTypes.LineGeometry:
                    length = intersection.length()
                    if length >= min_overlap_length:
                        register(
                            'VTI003', layer, feature_ids[feature.id()],
                            feature_ids[candidate.id()],
                            point=self._representative_point(intersection),
                            value=length, threshold=min_overlap_length
                        )
                elif intersection_type == QgsWkbTypes.PointGeometry:
                    for point in self._extract_points(intersection):
                        has_first = self._has_vertex(
                            vertices[feature.id()], point, tolerance
                        )
                        has_second = self._has_vertex(
                            vertices[candidate.id()], point, tolerance
                        )
                        if not (has_first and has_second):
                            missing_ids = []
                            if not has_first:
                                missing_ids.append(feature_ids[feature.id()])
                            if not has_second:
                                missing_ids.append(feature_ids[candidate.id()])
                            register(
                                'VTI004', layer, feature_ids[feature.id()],
                                feature_ids[candidate.id()],
                                self.tr(
                                    'Missing corresponding vertex in feature(s): {}',
                                    'Vértice correspondente ausente na(s) feição(ões): {}'
                                ).format(', '.join(missing_ids)),
                                point, None, tolerance
                            )

        if not check_dangles:
            return boundary_exempt
        for feature in features:
            if feedback.isCanceled():
                return boundary_exempt
            for endpoint in self._line_endpoints(feature.geometry()):
                endpoint_geometry = self._point_geometry(endpoint)
                near_rectangle = self._search_rectangle(endpoint, near_tolerance)
                connected = False
                nearest = None
                nearest_id = None
                for candidate_id in index.intersects(near_rectangle):
                    if candidate_id == feature.id() or candidate_id not in feature_map:
                        continue
                    distance = endpoint_geometry.distance(
                        feature_map[candidate_id].geometry()
                    )
                    if distance <= tolerance:
                        connected = True
                        break
                    if nearest is None or distance < nearest:
                        nearest = distance
                        nearest_id = candidate_id
                if connected:
                    continue
                if (
                    mapping_boundary is not None
                    and endpoint_geometry.distance(mapping_boundary)
                    <= boundary_tolerance
                ):
                    boundary_exempt += 1
                    continue
                if nearest is not None and nearest <= near_tolerance:
                    register(
                        'VTI006', layer, feature_ids[feature.id()],
                        feature_ids[nearest_id],
                        self.tr(
                            'Distance to the nearest line: {}',
                            'Distância até a linha mais próxima: {}'
                        ).format(nearest),
                        endpoint, nearest, near_tolerance
                    )
                else:
                    register(
                        'VTI005', layer, feature_ids[feature.id()],
                        detail=self.tr(
                            'No connection with another line was found.',
                            'Não foi encontrada conexão com outra linha.'
                        ),
                        point=endpoint, threshold=tolerance
                    )
        return boundary_exempt

    def _validate_polygons(self, layer, features, feature_map, feature_ids, index,
                           tolerance, min_overlap_area, check_gaps,
                           max_gap_area, check_missing_vertices,
                           working_crs, register, context, feedback):
        boundaries = {
            feature.id(): self._polygon_boundary(feature.geometry())
            for feature in features
        }
        vertices = {
            feature.id(): self._vertices(feature.geometry())
            for feature in features
        }
        native_missing_vertices = False
        if check_missing_vertices:
            native_missing_vertices = self._check_missing_vertices_native(
                layer, features, feature_ids, tolerance,
                working_crs, register, context, feedback
            )
        for feature in features:
            if feedback.isCanceled():
                return
            geometry = feature.geometry()
            rectangle = geometry.boundingBox()
            rectangle.grow(tolerance)
            for candidate_id in index.intersects(rectangle):
                if candidate_id <= feature.id() or candidate_id not in feature_map:
                    continue
                candidate = feature_map[candidate_id]
                candidate_geometry = candidate.geometry()
                if geometry.equals(candidate_geometry):
                    register(
                        'VTI002', layer, feature_ids[feature.id()],
                        feature_ids[candidate.id()],
                        point=self._representative_point(geometry)
                    )
                    continue

                contained = False
                if geometry.within(candidate_geometry):
                    contained = True
                    register(
                        'VTI008', layer, feature_ids[feature.id()],
                        feature_ids[candidate.id()],
                        point=self._representative_point(geometry)
                    )
                elif candidate_geometry.within(geometry):
                    contained = True
                    register(
                        'VTI008', layer, feature_ids[candidate.id()],
                        feature_ids[feature.id()],
                        point=self._representative_point(candidate_geometry)
                    )

                if geometry.intersects(candidate_geometry) and not contained:
                    intersection = geometry.intersection(candidate_geometry)
                    area = intersection.area()
                    if area >= min_overlap_area and area > 0:
                        register(
                            'VTI007', layer, feature_ids[feature.id()],
                            feature_ids[candidate.id()],
                            point=self._representative_point(intersection),
                            value=area, threshold=min_overlap_area
                        )

                if check_missing_vertices and not native_missing_vertices:
                    self._check_missing_vertices_pair(
                        layer, feature, candidate,
                        boundaries, vertices, feature_ids,
                        tolerance, register
                    )

        if check_gaps:
            self._check_polygon_gaps(
                layer, features, feature_map, feature_ids, index,
                boundaries, tolerance, max_gap_area, register, feedback
            )

    def _check_missing_vertices_native(self, layer, features, feature_ids,
                                       tolerance, working_crs, register,
                                       context, feedback):
        """Use the native QGIS 3.42+ checker, retaining a legacy fallback."""
        algorithm_id = 'native:checkgeometrymissingvertex'
        if QgsApplication.processingRegistry().algorithmById(algorithm_id) is None:
            feedback.pushInfo(self.tr(
                'The native missing-vertex checker is not available; the compatible LFTools method will be used.',
                'O verificador nativo de vértices ausentes não está disponível; será utilizado o método compatível do LFTools.'
            ))
            return False

        geometry_name = QgsWkbTypes.displayString(layer.wkbType())
        temporary = QgsVectorLayer(
            '{}?crs={}'.format(geometry_name, working_crs.authid()),
            '_lftools_valid_polygons',
            'memory'
        )
        if not temporary.isValid():
            return False
        provider = temporary.dataProvider()
        provider.addAttributes([QgsField('_lf_fid', QMetaType.Type.LongLong)])
        temporary.updateFields()
        copied = []
        for source_feature in features:
            copied_feature = QgsFeature(temporary.fields())
            copied_feature.setGeometry(source_feature.geometry())
            copied_feature['_lf_fid'] = int(source_feature.id())
            copied.append(copied_feature)
        provider.addFeatures(copied)
        temporary.updateExtents()

        if tolerance > 0:
            precision = max(0, min(15, int(ceil(-log10(tolerance)))))
        else:
            precision = 15
        try:
            result = processing.run(
                algorithm_id,
                {
                    'INPUT': temporary,
                    'UNIQUE_ID': '_lf_fid',
                    'TOLERANCE': precision,
                    'ERRORS': QgsProcessing.TEMPORARY_OUTPUT,
                    'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT,
                },
                context=context,
                feedback=feedback,
                is_child_algorithm=True
            )
            errors = result.get('ERRORS')
            if isinstance(errors, str):
                errors = QgsProcessingUtils.mapLayerFromString(errors, context)
            if errors is None:
                return False
            for error in errors.getFeatures():
                feature_id = error['_lf_fid']
                point = self._representative_point(error.geometry())
                source_fid = int(feature_id)
                register(
                    'VTI010', layer,
                    feature_ids.get(source_fid, str(source_fid)),
                    detail=self.tr(
                        'Vertex reported by the native QGIS missing-vertices checker.',
                        'Vértice reportado pelo verificador nativo de vértices ausentes do QGIS.'
                    ),
                    point=point,
                    threshold=tolerance
                )
            feedback.pushInfo(self.tr(
                'Missing vertices along shared borders were checked with the native QGIS algorithm.',
                'Os vértices ausentes em limites comuns foram verificados com o algoritmo nativo do QGIS.'
            ))
            return True
        except Exception as error:
            feedback.pushWarning(self.tr(
                'The native missing-vertex checker failed ({}); the compatible LFTools method will be used.',
                'O verificador nativo de vértices ausentes falhou ({}); será utilizado o método compatível do LFTools.'
            ).format(str(error)))
            return False

    def _check_missing_vertices_pair(self, layer, first, second,
                                     boundaries, vertices, feature_ids,
                                     tolerance, register):
        first_boundary = boundaries[first.id()]
        second_boundary = boundaries[second.id()]
        if first_boundary.distance(second_boundary) > tolerance:
            return
        for source, target in ((first, second), (second, first)):
            target_boundary = boundaries[target.id()]
            target_vertices = vertices[target.id()]
            for vertex in vertices[source.id()]:
                point_geometry = self._point_geometry(vertex)
                if point_geometry.distance(target_boundary) > tolerance:
                    continue
                if not self._has_vertex(target_vertices, vertex, tolerance):
                    register(
                        'VTI010', layer, feature_ids[target.id()],
                        feature_ids[source.id()],
                        self.tr(
                            'A vertex from the related polygon is missing from this shared border.',
                            'Um vértice do polígono relacionado está ausente neste limite comum.'
                        ),
                        vertex, None, tolerance
                    )

    def _check_polygon_gaps(self, layer, features, feature_map, feature_ids,
                            index, boundaries, tolerance, max_gap_area,
                            register, feedback):
        try:
            union = QgsGeometry.unaryUnion([
                feature.geometry() for feature in features
            ])
        except Exception as error:
            feedback.pushWarning(self.tr(
                'The gap check could not be completed: {}',
                'A verificação de lacunas não pôde ser concluída: {}'
            ).format(str(error)))
            return
        if union is None or union.isNull() or union.isEmpty():
            return
        polygons = union.asMultiPolygon() if union.isMultipart() else [union.asPolygon()]
        for polygon in polygons:
            for ring in polygon[1:]:
                if len(ring) < 4:
                    continue
                gap = QgsGeometry.fromPolygonXY([ring])
                area = gap.area()
                if area <= 0 or (max_gap_area > 0 and area > max_gap_area):
                    continue
                gap_boundary = self._polygon_boundary(gap)
                rectangle = gap.boundingBox()
                rectangle.grow(tolerance)
                adjacent_ids = []
                for candidate_id in index.intersects(rectangle):
                    if candidate_id not in feature_map:
                        continue
                    if boundaries[candidate_id].distance(gap_boundary) <= tolerance:
                        adjacent_ids.append(feature_ids[candidate_id])
                adjacent_ids = sorted(set(adjacent_ids))

                if len(adjacent_ids) < 2:
                    continue

                register(
                    'VTI009', layer,
                    detail=self.tr(
                        'Potential internal gap in the polygon coverage.',
                        'Lacuna interna potencial na cobertura de polígonos.'
                    ),
                    point=self._representative_point(gap),
                    value=area, threshold=max_gap_area,
                    involved_ids=', '.join(adjacent_ids)
                )

    def _save_settings(self, topology_tolerance, near_tolerance,
                       min_overlap_length, min_overlap_area,
                       check_dangles, check_gaps, max_gap_area,
                       check_missing_vertices, boundary_tolerance):
        settings = QgsSettings()
        settings.setValue(
            self.SETTINGS_PREFIX + 'topologyTolerance', topology_tolerance
        )
        settings.setValue(
            self.SETTINGS_PREFIX + 'nearTolerance', near_tolerance
        )
        settings.setValue(
            self.SETTINGS_PREFIX + 'minimumOverlapLength', min_overlap_length
        )
        settings.setValue(
            self.SETTINGS_PREFIX + 'minimumOverlapArea', min_overlap_area
        )
        settings.setValue(self.SETTINGS_PREFIX + 'checkDangles', check_dangles)
        settings.setValue(self.SETTINGS_PREFIX + 'checkGaps', check_gaps)
        settings.setValue(self.SETTINGS_PREFIX + 'maximumGapArea', max_gap_area)
        settings.setValue(
            self.SETTINGS_PREFIX + 'checkMissingVertices',
            check_missing_vertices
        )
        settings.setValue(
            self.SETTINGS_PREFIX + 'boundaryTolerance', boundary_tolerance
        )

    def postProcessAlgorithm(self, context, feedback):
        error_layer = QgsProcessingUtils.mapLayerFromString(
            self.ERROR_LAYER_DEST, context
        )
        if error_layer is None:
            return {}
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
        labeling = LabelConf(
            'rule_id', fonte='Arial', tam=9, bold=True,
            cor='white', buffer_tam=0.8,
            buffer_cor='black', dist=2
        )
        label_settings = labeling.settings()
        label_settings.fieldName = (
            '\'#\' || to_string("occurrence_id") || \' | \' || '
            'coalesce("rule_id", \'\') || \': \' || '
            'coalesce("rule", \'\') || \'\\n\' || '
            'coalesce("layer", \'\') || '
            'CASE WHEN coalesce("feature_id", \'\') <> \'\' '
            'THEN \'\\n\' || "feature_id" ELSE \'\' END || '
            'CASE WHEN "related_id" IS NOT NULL '
            'THEN \' × \' || "related_id" ELSE \'\' END || '
            'CASE WHEN coalesce("involved_ids", \'\') <> \'\' '
            'THEN \'\\n\' || \'IDs: \' || "involved_ids" ELSE \'\' END || '
            'CASE WHEN coalesce("detail", \'\') <> \'\' '
            'THEN \'\\n\' || "detail" ELSE \'\' END'
        )
        label_settings.isExpression = True
        error_layer.setLabeling(QgsVectorLayerSimpleLabeling(label_settings))
        error_layer.setLabelsEnabled(True)
        error_layer.triggerRepaint()
        return {}

    def _write_report(self, html_output, layers, evaluated_counts,
                      skipped_counts, layer_counts, rule_counts,
                      occurrences, topology_tolerance, near_tolerance,
                      min_overlap_length, min_overlap_area, check_dangles,
                      check_gaps, max_gap_area, check_missing_vertices,
                      mapping_area_name, boundary_tolerance,
                      boundary_exempt_counts):
        total_features = sum(evaluated_counts.values())
        total_skipped = sum(skipped_counts.values())
        total_occurrences = len(occurrences)
        total_boundary_exempt = sum(boundary_exempt_counts.values())
        affected = len({
            (item['layer'], item['feature_id'])
            for item in occurrences if item['feature_id'] is not None
        })
        status = self.tr('NONCONFORMING', 'NÃO CONFORME') if occurrences else self.tr(
            'CONFORMING', 'CONFORME'
        )
        status_class = 'bad' if occurrences else 'ok'

        layer_rows = ''
        for layer in layers:
            layer_rows += '<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>'.format(
                str2HTML(layer.name()),
                str2HTML(QgsWkbTypes.displayString(layer.wkbType())),
                evaluated_counts[layer.name()],
                skipped_counts[layer.name()],
                boundary_exempt_counts[layer.name()],
                layer_counts[layer.name()],
                str2HTML(layer.crs().authid())
            )

        enabled_rules = ['VTI001', 'VTI002', 'VTI003', 'VTI004', 'VTI007', 'VTI008']
        if check_dangles:
            enabled_rules.extend(['VTI005', 'VTI006'])
        if check_gaps:
            enabled_rules.append('VTI009')
        if check_missing_vertices:
            enabled_rules.append('VTI010')
        enabled_rules.sort(key=lambda rule_id: int(rule_id[3:]))
        rule_rows = ''
        for rule_id in enabled_rules:
            count = rule_counts[rule_id]
            result = self.tr('Nonconforming', 'Não conforme') if count else self.tr(
                'Conforming', 'Conforme'
            )
            css_class = 'bad' if count else 'ok'
            rule_rows += '<tr><td>{}</td><td>{}</td><td>{}</td><td class="{}">{}</td></tr>'.format(
                rule_id, str2HTML(self._rule_name(rule_id)), count,
                css_class, str2HTML(result)
            )

        parameter_rows = ''.join([
            '<tr><td>{}</td><td>{}</td></tr>'.format(str2HTML(label), value)
            for label, value in [
                (self.tr('Topological coincidence tolerance', 'Tolerância de coincidência topológica'), '{} m'.format(topology_tolerance)),
                (self.tr('Near disconnected ends tolerance', 'Tolerância para extremidades próximas desconectadas'), '{} m'.format(near_tolerance)),
                (self.tr('Mapping area', 'Área de mapeamento'), str2HTML(mapping_area_name)),
                (self.tr('Mapping boundary tolerance', 'Tolerância da fronteira da área de mapeamento'), '{} m'.format(boundary_tolerance) if mapping_area_name != self.tr('Not provided', 'Não fornecida') else self.tr('Not evaluated', 'Não avaliada')),
                (self.tr('Minimum line overlap length', 'Comprimento mínimo de sobreposição linear'), '{} m'.format(min_overlap_length)),
                (self.tr('Minimum polygon overlap area', 'Área mínima de sobreposição de polígonos'), '{} m²'.format(min_overlap_area)),
                (self.tr('Maximum gap area', 'Área máxima das lacunas'), '{} m²'.format(max_gap_area) if check_gaps else self.tr('Not evaluated', 'Não avaliada')),
            ]
        ])

        interpretation = self.tr(
            'The automated intraclass validation evaluated {} valid feature(s) in {} layer(s), ignored {} null, empty, or invalid feature(s), accepted {} disconnected line end(s) near the mapping boundary, and identified {} occurrence(s) affecting {} feature(s). The dataset is {} for the rules enabled in this execution. The input layers were not modified.',
            'A validação intraclasse automatizada avaliou {} feição(ões) válida(s) em {} camada(s), ignorou {} feição(ões) nula(s), vazia(s) ou inválida(s), aceitou {} extremidade(s) de linha desconectada(s) próxima(s) à fronteira da área de mapeamento e identificou {} ocorrência(s) que afetam {} feição(ões). O conjunto de dados está {} para as regras habilitadas nesta execução. As camadas de entrada não foram modificadas.'
        ).format(
            total_features, len(layers), total_skipped,
            total_boundary_exempt, total_occurrences, affected, status
        )

        report = '''<!DOCTYPE html>
<html><head><meta charset="utf-8">
<title>''' + str2HTML(self.tr(
            'INTRACLASS TOPOLOGY VALIDATION REPORT',
            'RELATÓRIO DE VALIDAÇÃO TOPOLÓGICA INTRACLASSE'
        )) + '''</title>
<link rel="icon" href="https://github.com/LEOXINGU/lftools/blob/main/images/lftools.png?raw=true" type="image/x-icon">
<style>
body { font-family:Arial,sans-serif; background:#f4f6f0; color:#222; margin:0; padding:0; }
.page { max-width:1100px; margin:24px auto; background:white; padding:32px; border-radius:12px; box-shadow:0 2px 12px rgba(0,0,0,.12); }
.header { text-align:center; border-bottom:3px solid #365f2c; padding-bottom:16px; margin-bottom:24px; }
.header img { height:72px; } h1 { color:#274e22; font-size:24px; margin:12px 0 4px 0; }
h2 { color:#365f2c; font-size:18px; border-bottom:1px solid #ddd; padding-bottom:6px; margin-top:28px; }
.subtitle { color:#666; font-size:13px; }
.cards { display:grid; grid-template-columns:repeat(4,1fr); gap:12px; margin:20px 0; }
.card { background:#eef5ea; border-left:5px solid #365f2c; padding:14px; border-radius:8px; }
.label { color:#666; font-size:12px; text-transform:uppercase; }
.big { font-size:22px; font-weight:bold; color:#1f3f1b; margin-top:6px; }
table { width:100%; border-collapse:collapse; margin:12px 0; font-size:13px; }
th { background:#365f2c; color:white; padding:8px; text-align:left; }
td { border:1px solid #ddd; padding:8px; } tr:nth-child(even) { background:#f8f8f8; }
.note { background:#fff8dc; border-left:5px solid #c9a227; padding:12px; margin:12px 0; border-radius:6px; }
.warning { background:#fdecec; border-left:5px solid #b00020; padding:12px; margin:12px 0; border-radius:6px; }
.ok { color:#1f7a1f; font-weight:bold; } .bad { color:#a00000; font-weight:bold; }
.footer { margin-top:30px; border-top:1px solid #ccc; padding-top:12px; color:#555; font-size:12px; }
@media (max-width:760px) { .cards { grid-template-columns:1fr 1fr; } }
</style></head><body><div class="page"><div class="header">
<img src="data:image/png;base64,''' + lftools_logo + '''">
<h1>''' + str2HTML(self.tr(
            'INTRACLASS TOPOLOGY VALIDATION REPORT',
            'RELATÓRIO DE VALIDAÇÃO TOPOLÓGICA INTRACLASSE'
        )) + '''</h1><div class="subtitle">LFTools | ''' + str2HTML(self.tr(
            'Logical consistency — intraclass level',
            'Consistência lógica — nível intraclasse'
        )) + ''' | ''' + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + '''</div></div>
<div class="cards">
<div class="card"><div class="label">''' + str2HTML(self.tr('Evaluated features', 'Feições avaliadas')) + '''</div><div class="big">''' + str(total_features) + '''</div></div>
<div class="card"><div class="label">''' + str2HTML(self.tr('Ignored features', 'Feições ignoradas')) + '''</div><div class="big">''' + str(total_skipped) + '''</div></div>
<div class="card"><div class="label">''' + str2HTML(self.tr('Occurrences', 'Ocorrências')) + '''</div><div class="big">''' + str(total_occurrences) + '''</div></div>
<div class="card"><div class="label">''' + str2HTML(self.tr('Result', 'Resultado')) + '''</div><div class="big ''' + status_class + '''">''' + str2HTML(status) + '''</div></div>
</div>
<div class="warning"><b>''' + str2HTML(self.tr('Prerequisite:', 'Pré-requisito:')) + '''</b> ''' + str2HTML(self.tr(
            'individual geometries must be validated and corrected before intraclass topology is assessed. Null, empty, or invalid geometries were ignored.',
            'as geometrias individuais devem ser validadas e corrigidas antes da avaliação topológica intraclasse. Geometrias nulas, vazias ou inválidas foram ignoradas.'
        )) + '''</div>
<h2>''' + str2HTML(self.tr('1. Evaluated Data', '1. Dados Avaliados')) + '''</h2>
<table><tr><th>''' + str2HTML(self.tr('Layer', 'Camada')) + '''</th><th>''' + str2HTML(self.tr('Geometry', 'Geometria')) + '''</th><th>''' + str2HTML(self.tr('Evaluated', 'Avaliadas')) + '''</th><th>''' + str2HTML(self.tr('Ignored', 'Ignoradas')) + '''</th><th>''' + str2HTML(self.tr('Boundary exceptions', 'Exceções na fronteira')) + '''</th><th>''' + str2HTML(self.tr('Occurrences', 'Ocorrências')) + '''</th><th>''' + str2HTML(self.tr('CRS', 'SRC')) + '''</th></tr>''' + layer_rows + '''</table>
<h2>''' + str2HTML(self.tr('2. Methodology', '2. Metodologia')) + '''</h2>
<p>''' + str2HTML(self.tr(
            'Each layer was evaluated independently in a metric working CRS. Spatial relationships were compared using a spatial index, linear thresholds in metres, and area thresholds in square metres. When a mapping area was provided, disconnected line ends within the boundary tolerance were accepted and counted separately. Identifiers were obtained automatically from provider-declared primary keys, with the internal QGIS feature ID used as a fallback. The validation only identifies potential nonconformities; it does not edit the source data.',
            'Cada camada foi avaliada de forma independente em um SRC métrico de trabalho. As relações espaciais foram comparadas com índice espacial, tolerâncias lineares em metros e limites de área em metros quadrados. Quando uma área de mapeamento foi fornecida, as extremidades de linhas desconectadas situadas dentro da tolerância da fronteira foram aceitas e contabilizadas separadamente. Os identificadores foram obtidos automaticamente pelas chaves primárias declaradas pelos provedores, com uso do identificador interno do QGIS como alternativa. A validação apenas identifica não conformidades potenciais; ela não altera os dados de origem.'
        )) + '''</p>
<h2>''' + str2HTML(self.tr('3. Parameters', '3. Parâmetros')) + '''</h2>
<table><tr><th>''' + str2HTML(self.tr('Parameter', 'Parâmetro')) + '''</th><th>''' + str2HTML(self.tr('Value', 'Valor')) + '''</th></tr>''' + parameter_rows + '''</table>
<h2>''' + str2HTML(self.tr('4. Results by Rule', '4. Resultados por Regra')) + '''</h2>
<table><tr><th>ID</th><th>''' + str2HTML(self.tr('Rule', 'Regra')) + '''</th><th>''' + str2HTML(self.tr('Occurrences', 'Ocorrências')) + '''</th><th>''' + str2HTML(self.tr('Result', 'Resultado')) + '''</th></tr>''' + rule_rows + '''</table>
<h2>''' + str2HTML(self.tr('5. Automatic Interpretation', '5. Interpretação Automática')) + '''</h2>
<div class="note">''' + str2HTML(interpretation) + '''</div>
<div class="footer">Leandro França 2026<br>Cartographic Engineer<br>email: contato@geoone.com.br</div>
</div></body></html>'''
        with open(html_output, 'w', encoding='utf-8') as report_file:
            report_file.write(report)
