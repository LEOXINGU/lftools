# -*- coding: utf-8 -*-

"""
Cad_ParcelTopologyCleanup.py
***************************************************************************
*                                                                         *
*   LFTools - Parcel Topology Cleanup and Correction                      *
*                                                                         *
***************************************************************************
"""

__author__ = 'Leandro França'
__date__ = '2026-08-18'
__copyright__ = '(C) 2026, Leandro França'

from qgis.PyQt.QtCore import QMetaType
from qgis.PyQt.QtGui import QIcon

from qgis.core import (
    QgsApplication,
    QgsDistanceArea,
    QgsFeature,
    QgsFeatureSink,
    QgsField,
    QgsFields,
    QgsGeometry,
    QgsMemoryProviderUtils,
    QgsProcessingAlgorithm,
    QgsProcessingException,
    QgsProcessingParameterBoolean,
    QgsProcessingParameterEnum,
    QgsProcessingParameterFeatureSink,
    QgsProcessingParameterFeatureSource,
    QgsProcessingParameterNumber,
    QgsSpatialIndex,
    QgsWkbTypes,
    Qgis
)

from lftools.geocapt.imgs import Imgs
from lftools.geocapt.topogeo import meters2degrees
from lftools.translations.translate import translate

import json
import math
import os
import processing


class ParcelTopologyCleanup(QgsProcessingAlgorithm):

    LOC = QgsApplication.locale()[:2]

    def tr(self, *string):
        return translate(string, self.LOC)

    def createInstance(self):
        return ParcelTopologyCleanup()

    def name(self):
        return 'parceltopologycleanup'

    def displayName(self):
        return self.tr(
            'Parcel Topology Cleanup and Correction',
            'Limpeza e Correção Topológica de Lotes'
        )

    def group(self):
        return self.tr('Cadastre', 'Cadastro')

    def groupId(self):
        return 'cadastro'

    def tags(self):
        return (
            'GeoOne,cadastre,cadastro,parcel,lote,topology,topologia,cleanup,'
            'correction,correção,geometry,geometria,null,empty,invalid,duplicate,'
            'sliver,filete,hole,buraco,multipart,snap,grid,grade,connectivity,'
            'conectividade,quality,qualidade'
        ).split(',')

    def icon(self):
        return QIcon(os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'images/cadastre.png'
        ))

    txt_en = '''This tool performs a controlled geometric cleanup and topological correction workflow for parcel layers.
The workflow can remove null or empty geometries, repair invalid geometries, convert multipart features to singleparts, remove duplicate geometries, remove holes, remove excessively narrow polygons (slivers), snap coordinates to a grid, remove duplicate vertices, and adjust connectivity between adjacent polygons.
Removed features are recorded in a separate table with their original attributes. Modified or blocked operations are recorded in an audit table.
Note: Automatic corrections are accepted only when the resulting geometry passes safety checks. Remaining topological problems must be reviewed after processing.
'''

    txt_pt = '''Esta ferramenta executa um fluxo controlado de limpeza geométrica e correção topológica para camadas de lotes.
O fluxo pode remover geometrias nulas ou vazias, corrigir geometrias inválidas, converter multipartes em partes simples, remover geometrias duplicadas, remover buracos, remover polígonos excessivamente estreitos (filetes), aderir coordenadas à grade, remover vértices duplicados e ajustar a conectividade entre polígonos adjacentes.
As feições removidas são registradas em uma tabela separada com seus atributos originais. As operações que modificaram feições ou foram bloqueadas são registradas em uma tabela de auditoria.
Obs.: Correções automáticas somente são aceitas quando a geometria resultante passa pelas verificações de segurança. Problemas topológicos remanescentes devem ser revisados após o processamento.
'''

    figure = 'images/tutorial/cadastre_parcelTopologyCleanup.jpg'

    def shortHelpString(self):
        social_BW = Imgs().social_BW
        img = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            self.figure
        )
        footer = (
            '<div align="center"><img src="' + img + '"></div>'
            '<div align="right"><p align="right"><b>'
            + self.tr('Author: Leandro Franca', 'Autor: Leandro França')
            + '</b></p>' + social_BW + '</div></div>'
        )
        return self.tr(self.txt_en, self.txt_pt) + footer

    INPUT = 'INPUT'
    REMOVE_NULL_EMPTY = 'REMOVE_NULL_EMPTY'
    FIX_INVALID = 'FIX_INVALID'
    SINGLEPARTS = 'SINGLEPARTS'
    REMOVE_DUPLICATES = 'REMOVE_DUPLICATES'
    REMOVE_HOLES = 'REMOVE_HOLES'
    REMOVE_SLIVERS = 'REMOVE_SLIVERS'
    MIN_SHAPE_RATIO = 'MIN_SHAPE_RATIO'
    SNAP_GRID = 'SNAP_GRID'
    GRID_SPACING = 'GRID_SPACING'
    REMOVE_DUPLICATE_VERTICES = 'REMOVE_DUPLICATE_VERTICES'
    CONNECT = 'CONNECT'
    CONNECT_TOLERANCE = 'CONNECT_TOLERANCE'
    CONNECT_BEHAVIOR = 'CONNECT_BEHAVIOR'
    OUTPUT = 'OUTPUT'
    REMOVED = 'REMOVED'
    REPORT = 'REPORT'

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterFeatureSource(
            self.INPUT,
            self.tr('Parcels', 'Lotes'),
            [Qgis.ProcessingSourceType.TypeVectorPolygon]
        ))

        self.addParameter(QgsProcessingParameterBoolean(
            self.REMOVE_NULL_EMPTY,
            self.tr('Remove null or empty geometries',
                    'Remover geometrias nulas ou vazias'),
            defaultValue=True
        ))

        self.addParameter(QgsProcessingParameterBoolean(
            self.FIX_INVALID,
            self.tr('Repair invalid geometries',
                    'Corrigir geometrias inválidas'),
            defaultValue=True
        ))

        self.addParameter(QgsProcessingParameterBoolean(
            self.SINGLEPARTS,
            self.tr('Convert multipart features to singleparts',
                    'Converter feições multipartes em partes simples'),
            defaultValue=True
        ))

        self.addParameter(QgsProcessingParameterBoolean(
            self.REMOVE_DUPLICATES,
            self.tr('Remove duplicate geometries',
                    'Remover geometrias duplicadas'),
            defaultValue=True
        ))

        self.addParameter(QgsProcessingParameterBoolean(
            self.REMOVE_HOLES,
            self.tr('Remove holes', 'Remover buracos'),
            defaultValue=True
        ))

        self.addParameter(QgsProcessingParameterBoolean(
            self.REMOVE_SLIVERS,
            self.tr('Remove excessively narrow polygons (slivers)',
                    'Remover polígonos excessivamente estreitos (filetes)'),
            defaultValue=True
        ))

        self.addParameter(QgsProcessingParameterNumber(
            self.MIN_SHAPE_RATIO,
            self.tr('Minimum equivalent-rectangle width/length ratio',
                    'Razão mínima largura/comprimento do retângulo equivalente'),
            type=QgsProcessingParameterNumber.Type.Double,
            defaultValue=0.001,
            minValue=0.0,
            maxValue=1.0
        ))

        self.addParameter(QgsProcessingParameterBoolean(
            self.SNAP_GRID,
            self.tr('Snap coordinates to grid',
                    'Aderir coordenadas à grade'),
            defaultValue=True
        ))

        self.addParameter(QgsProcessingParameterNumber(
            self.GRID_SPACING,
            self.tr('Grid spacing (meters)',
                    'Espaçamento da grade (metros)'),
            type=QgsProcessingParameterNumber.Type.Double,
            defaultValue=0.001,
            minValue=0.000001
        ))

        self.addParameter(QgsProcessingParameterBoolean(
            self.REMOVE_DUPLICATE_VERTICES,
            self.tr('Remove duplicate vertices',
                    'Remover vértices duplicados'),
            defaultValue=True
        ))

        self.addParameter(QgsProcessingParameterBoolean(
            self.CONNECT,
            self.tr('Adjust connectivity between adjacent polygons',
                    'Ajustar conectividade entre polígonos adjacentes'),
            defaultValue=True
        ))

        self.addParameter(QgsProcessingParameterNumber(
            self.CONNECT_TOLERANCE,
            self.tr('Connectivity tolerance (meters)',
                    'Tolerância de conectividade (metros)'),
            type=QgsProcessingParameterNumber.Type.Double,
            defaultValue=0.01,
            minValue=0.000001
        ))

        self.addParameter(QgsProcessingParameterEnum(
            self.CONNECT_BEHAVIOR,
            self.tr('Connectivity snapping behavior',
                    'Comportamento da aderência para conectividade'),
            options=[
                self.tr(
                    'Prefer aligning nodes, insert extra vertices where required',
                    'Preferir alinhar vértices e inserir novos vértices quando necessário'
                ),
                self.tr(
                    'Prefer closest point, insert extra vertices where required',
                    'Preferir o ponto mais próximo e inserir novos vértices quando necessário'
                ),
                self.tr(
                    'Prefer aligning nodes, do not insert new vertices',
                    'Preferir alinhar vértices sem inserir novos vértices'
                ),
                self.tr(
                    'Prefer closest point, do not insert new vertices',
                    'Preferir o ponto mais próximo sem inserir novos vértices'
                )
            ],
            defaultValue=0
        ))

        self.addParameter(QgsProcessingParameterFeatureSink(
            self.OUTPUT,
            self.tr('Corrected parcels', 'Lotes corrigidos')
        ))

        self.addParameter(QgsProcessingParameterFeatureSink(
            self.REMOVED,
            self.tr('Removed features table',
                    'Tabela de feições removidas'),
            type=Qgis.ProcessingSourceType.TypeVector
        ))

        self.addParameter(QgsProcessingParameterFeatureSink(
            self.REPORT,
            self.tr('Topology correction audit',
                    'Auditoria da correção topológica'),
            type=Qgis.ProcessingSourceType.TypeVector
        ))

    def _unique_field_name(self, fields, base_name):
        if fields.indexOf(base_name) == -1:
            return base_name
        i = 2
        while fields.indexOf(f'{base_name}_{i}') != -1:
            i += 1
        return f'{base_name}_{i}'

    def _vertex_count(self, geom):
        if geom is None or geom.isNull() or geom.isEmpty():
            return 0
        return sum(1 for _ in geom.vertices())

    def _part_count(self, geom):
        if geom is None or geom.isNull() or geom.isEmpty():
            return 0
        if not geom.isMultipart():
            return 1
        return len(geom.asGeometryCollection())

    def _metric_area_perimeter(self, geom, distance_area):
        if geom is None or geom.isNull() or geom.isEmpty():
            return 0.0, 0.0
        try:
            area = float(distance_area.measureArea(geom))
            perimeter = float(distance_area.measurePerimeter(geom))
            return abs(area), abs(perimeter)
        except Exception:
            return abs(float(geom.area())), abs(float(geom.length()))

    def _shape_ratio(self, geom, distance_area):
        area, perimeter = self._metric_area_perimeter(geom, distance_area)
        if area <= 0.0 or perimeter <= 0.0:
            return 0.0, area, perimeter

        delta = perimeter * perimeter - 16.0 * area
        if delta <= 0.0:
            return 1.0, area, perimeter

        root = math.sqrt(delta)
        larger = (perimeter + root) / 4.0
        smaller = (perimeter - root) / 4.0

        if larger <= 0.0:
            return 0.0, area, perimeter

        ratio = max(0.0, min(1.0, smaller / larger))
        return ratio, area, perimeter

    def _canonical_wkb(self, geom):
        if geom is None or geom.isNull() or geom.isEmpty():
            return None
        g = QgsGeometry(geom)
        try:
            g.normalize()
        except Exception:
            pass
        return bytes(g.asWkb())

    def _polygonal_only(self, geom):
        if geom is None or geom.isNull() or geom.isEmpty():
            return QgsGeometry()

        if geom.type() == Qgis.GeometryType.Polygon:
            return QgsGeometry(geom)

        polygons = []
        for item in geom.asGeometryCollection():
            if (
                item is not None
                and not item.isNull()
                and not item.isEmpty()
                and item.type() == Qgis.GeometryType.Polygon
            ):
                polygons.append(QgsGeometry(item))

        if not polygons:
            return QgsGeometry()
        if len(polygons) == 1:
            return polygons[0]
        return QgsGeometry.collectGeometry(polygons)

    def _attributes_json(self, attrs, input_fields):
        data = {}
        for i, field in enumerate(input_fields):
            value = attrs[i] if i < len(attrs) else None
            try:
                json.dumps(value)
                data[field.name()] = value
            except (TypeError, ValueError):
                data[field.name()] = str(value) if value is not None else None
        return json.dumps(data, ensure_ascii=False, default=str)

    def _removed_fields(self, input_fields):
        fields = QgsFields()
        for field in input_fields:
            fields.append(field)

        self._rm_orig = self._unique_field_name(fields, 'lf_orig_id')
        fields.append(QgsField(self._rm_orig, QMetaType.Type.LongLong))
        self._rm_part = self._unique_field_name(fields, 'lf_part')
        fields.append(QgsField(self._rm_part, QMetaType.Type.Int))
        self._rm_step = self._unique_field_name(fields, 'lf_step')
        fields.append(QgsField(self._rm_step, QMetaType.Type.QString, len=60))
        self._rm_reason = self._unique_field_name(fields, 'lf_reason')
        fields.append(QgsField(self._rm_reason, QMetaType.Type.QString, len=160))
        self._rm_ratio = self._unique_field_name(fields, 'lf_shape_ratio')
        fields.append(QgsField(self._rm_ratio, QMetaType.Type.Double))
        self._rm_area = self._unique_field_name(fields, 'lf_area_m2')
        fields.append(QgsField(self._rm_area, QMetaType.Type.Double))
        self._rm_perim = self._unique_field_name(fields, 'lf_perim_m')
        fields.append(QgsField(self._rm_perim, QMetaType.Type.Double))
        self._rm_attrs = self._unique_field_name(fields, 'lf_attributes')
        fields.append(QgsField(self._rm_attrs, QMetaType.Type.QString))
        return fields

    def _report_fields(self):
        fields = QgsFields()
        fields.append(QgsField('lf_orig_id', QMetaType.Type.LongLong))
        fields.append(QgsField('lf_part', QMetaType.Type.Int))
        fields.append(QgsField('lf_step', QMetaType.Type.QString, len=60))
        fields.append(QgsField('lf_status', QMetaType.Type.QString, len=20))
        fields.append(QgsField('lf_reason', QMetaType.Type.QString, len=180))
        fields.append(QgsField('vertices_b', QMetaType.Type.Int))
        fields.append(QgsField('vertices_a', QMetaType.Type.Int))
        fields.append(QgsField('parts_b', QMetaType.Type.Int))
        fields.append(QgsField('parts_a', QMetaType.Type.Int))
        fields.append(QgsField('area_before', QMetaType.Type.Double))
        fields.append(QgsField('area_after', QMetaType.Type.Double))
        fields.append(QgsField('area_delta', QMetaType.Type.Double))
        return fields

    def _write_removed(self, sink, sink_fields, record, input_fields,
                       step, reason, distance_area, shape_ratio=None):
        ratio, area, perimeter = self._shape_ratio(
            record['geom'], distance_area
        )
        if shape_ratio is not None:
            ratio = shape_ratio

        feat = QgsFeature(sink_fields)
        feat.setGeometry(QgsGeometry())
        feat.setAttributes(
            record['attrs'][:] + [
                int(record['orig_id']),
                int(record.get('part', 1)),
                step,
                reason,
                float(ratio),
                float(area),
                float(perimeter),
                self._attributes_json(record['attrs'], input_fields)
            ]
        )
        sink.addFeature(feat, QgsFeatureSink.Flag.FastInsert)

    def _write_report(self, sink, fields, record, step, status, reason,
                      before_geom, after_geom, distance_area):
        vb = self._vertex_count(before_geom)
        va = self._vertex_count(after_geom)
        pb = self._part_count(before_geom)
        pa = self._part_count(after_geom)
        ab, _ = self._metric_area_perimeter(before_geom, distance_area)
        aa, _ = self._metric_area_perimeter(after_geom, distance_area)

        feat = QgsFeature(fields)
        feat.setAttributes([
            int(record['orig_id']),
            int(record.get('part', 1)),
            step,
            status,
            reason,
            int(vb),
            int(va),
            int(pb),
            int(pa),
            float(ab),
            float(aa),
            float(aa - ab)
        ])
        sink.addFeature(feat, QgsFeatureSink.Flag.FastInsert)

    def _work_layer(self, records, fields, crs, source_wkb):
        work_fields = QgsFields()
        for field in fields:
            work_fields.append(field)

        uid_field = self._unique_field_name(work_fields, '__lf_uid__')
        work_fields.append(QgsField(uid_field, QMetaType.Type.LongLong))

        layer = QgsMemoryProviderUtils.createMemoryLayer(
            'lf_parcel_topology_work',
            work_fields,
            QgsWkbTypes.multiType(source_wkb),
            crs
        )
        provider = layer.dataProvider()
        feats = []

        for rec in records:
            geom = rec['geom']
            if (
                geom is None
                or geom.isNull()
                or geom.isEmpty()
                or not geom.isGeosValid()
            ):
                continue
            feat = QgsFeature(work_fields)
            feat.setGeometry(QgsGeometry(geom))
            feat.setAttributes(rec['attrs'][:] + [int(rec['uid'])])
            feats.append(feat)

        if feats:
            provider.addFeatures(feats)
        layer.updateExtents()
        return layer, uid_field

    def _effective_distance(self, meters, crs, mean_latitude):
        if crs.isGeographic():
            return meters2degrees(meters, mean_latitude, crs)
        return meters

    def _safe_geometry(self, old_geom, new_geom, allow_multi=True):
        if new_geom is None or new_geom.isNull() or new_geom.isEmpty():
            return False, 'null_or_empty'
        if new_geom.type() != Qgis.GeometryType.Polygon:
            return False, 'non_polygonal'
        if (
            old_geom is not None
            and not old_geom.isNull()
            and not old_geom.isEmpty()
            and old_geom.isGeosValid()
            and not new_geom.isGeosValid()
        ):
            return False, 'became_invalid'
        if not allow_multi and new_geom.isMultipart():
            return False, 'became_multipart'
        return True, ''

    def _remove_duplicates(self, records, removed_sink, removed_fields,
                           input_fields, distance_area, report_sink,
                           report_fields, step):
        seen = {}
        kept = []
        count = 0

        for rec in records:
            key = self._canonical_wkb(rec['geom'])
            if key is None:
                kept.append(rec)
                continue

            if key in seen:
                first = seen[key]
                reason = self.tr(
                    'Duplicate of original feature ID {}'
                    .format(first['orig_id']),
                    'Duplicada da feição original ID {}'
                    .format(first['orig_id'])
                )
                self._write_removed(
                    removed_sink, removed_fields, rec, input_fields,
                    step, reason, distance_area
                )
                self._write_report(
                    report_sink, report_fields, rec, step, 'removed',
                    reason, rec['geom'], QgsGeometry(), distance_area
                )
                count += 1
            else:
                seen[key] = rec
                kept.append(rec)

        return kept, count

    def _count_overlaps(self, records):
        feats = []
        index = QgsSpatialIndex()

        for rec in records:
            geom = rec['geom']
            if geom is None or geom.isNull() or geom.isEmpty():
                continue
            f = QgsFeature()
            f.setId(int(rec['uid']))
            f.setGeometry(QgsGeometry(geom))
            feats.append(f)
            index.addFeature(f)

        geom_by_id = {int(f.id()): f.geometry() for f in feats}
        pairs = set()

        for f in feats:
            fid = int(f.id())
            g1 = f.geometry()
            for fid2 in index.intersects(g1.boundingBox()):
                fid2 = int(fid2)
                if fid2 <= fid:
                    continue
                g2 = geom_by_id.get(fid2)
                if g2 is None:
                    continue
                try:
                    if not g1.intersects(g2):
                        continue
                    inter = g1.intersection(g2)
                    if (
                        inter is not None
                        and not inter.isNull()
                        and not inter.isEmpty()
                        and inter.type() == Qgis.GeometryType.Polygon
                        and inter.area() > 0
                    ):
                        pairs.add((fid, fid2))
                except Exception:
                    continue
        return len(pairs)

    def processAlgorithm(self, parameters, context, feedback):
        source = self.parameterAsSource(parameters, self.INPUT, context)
        if source is None:
            raise QgsProcessingException(
                self.invalidSourceError(parameters, self.INPUT)
            )

        input_fields = source.fields()
        crs = source.sourceCrs()

        remove_null_empty = self.parameterAsBool(
            parameters, self.REMOVE_NULL_EMPTY, context
        )
        fix_invalid = self.parameterAsBool(
            parameters, self.FIX_INVALID, context
        )
        singleparts = self.parameterAsBool(
            parameters, self.SINGLEPARTS, context
        )
        remove_duplicates = self.parameterAsBool(
            parameters, self.REMOVE_DUPLICATES, context
        )
        remove_holes = self.parameterAsBool(
            parameters, self.REMOVE_HOLES, context
        )
        remove_slivers = self.parameterAsBool(
            parameters, self.REMOVE_SLIVERS, context
        )
        min_shape_ratio = self.parameterAsDouble(
            parameters, self.MIN_SHAPE_RATIO, context
        )
        snap_grid = self.parameterAsBool(
            parameters, self.SNAP_GRID, context
        )
        grid_spacing_m = self.parameterAsDouble(
            parameters, self.GRID_SPACING, context
        )
        remove_duplicate_vertices = self.parameterAsBool(
            parameters, self.REMOVE_DUPLICATE_VERTICES, context
        )
        connect = self.parameterAsBool(
            parameters, self.CONNECT, context
        )
        connect_tolerance_m = self.parameterAsDouble(
            parameters, self.CONNECT_TOLERANCE, context
        )
        connect_behavior = self.parameterAsEnum(
            parameters, self.CONNECT_BEHAVIOR, context
        )

        if not 0.0 <= min_shape_ratio <= 1.0:
            raise QgsProcessingException(
                self.tr('Invalid shape ratio.', 'Razão de forma inválida.')
            )
        if grid_spacing_m <= 0.0:
            raise QgsProcessingException(
                self.tr('Invalid grid spacing.',
                        'Espaçamento da grade inválido.')
            )
        if connect_tolerance_m <= 0.0:
            raise QgsProcessingException(
                self.tr('Invalid connectivity tolerance.',
                        'Tolerância de conectividade inválida.')
            )

        extent = source.sourceExtent()
        mean_latitude = (
            (extent.yMaximum() + extent.yMinimum()) / 2.0
            if not extent.isNull() else 0.0
        )

        grid_spacing = self._effective_distance(
            grid_spacing_m, crs, mean_latitude
        )
        connect_tolerance = self._effective_distance(
            connect_tolerance_m, crs, mean_latitude
        )
        distance_area = QgsDistanceArea()
        try:
            distance_area.setSourceCrs(
                crs, context.transformContext()
            )
            ellipsoid = crs.ellipsoidAcronym()
            if ellipsoid:
                distance_area.setEllipsoid(ellipsoid)
        except Exception:
            pass

        if crs.isGeographic():
            feedback.pushInfo(self.tr(
                'Metric tolerances were converted to angular values using the mean latitude of the layer extent.',
                'As tolerâncias métricas foram convertidas para valores angulares utilizando a latitude média da extensão da camada.'
            ))

        output_wkb = (
            QgsWkbTypes.singleType(source.wkbType())
            if singleparts
            else QgsWkbTypes.multiType(source.wkbType())
        )

        sink, dest_id = self.parameterAsSink(
            parameters, self.OUTPUT, context,
            input_fields, output_wkb, crs
        )
        if sink is None:
            raise QgsProcessingException(
                self.invalidSinkError(parameters, self.OUTPUT)
            )

        removed_fields = self._removed_fields(input_fields)
        removed_sink, removed_id = self.parameterAsSink(
            parameters, self.REMOVED, context,
            removed_fields, Qgis.WkbType.NoGeometry, crs
        )
        if removed_sink is None:
            raise QgsProcessingException(
                self.invalidSinkError(parameters, self.REMOVED)
            )

        report_fields = self._report_fields()
        report_sink, report_id = self.parameterAsSink(
            parameters, self.REPORT, context,
            report_fields, Qgis.WkbType.NoGeometry, crs
        )
        if report_sink is None:
            raise QgsProcessingException(
                self.invalidSinkError(parameters, self.REPORT)
            )

        feedback.pushInfo(self.tr(
            'Starting parcel topology cleanup and correction...',
            'Iniciando limpeza e correção topológica de lotes...'
        ))

        records = []
        uid = 1
        input_count = initial_null = initial_empty = 0
        initial_invalid = initial_multipart = 0

        for feat in source.getFeatures():
            input_count += 1
            geom = feat.geometry()

            if geom is None or geom.isNull():
                initial_null += 1
            elif geom.isEmpty():
                initial_empty += 1
            else:
                if not geom.isGeosValid():
                    initial_invalid += 1
                if geom.isMultipart():
                    initial_multipart += 1

            records.append({
                'uid': uid,
                'orig_id': int(feat.id()),
                'part': 1,
                'attrs': feat.attributes()[:],
                'geom': QgsGeometry(geom) if geom is not None else QgsGeometry()
            })
            uid += 1

        feedback.pushInfo(self.tr(
            'Input features: {} | null: {} | empty: {} | invalid: {} | multipart: {}'
            .format(input_count, initial_null, initial_empty,
                    initial_invalid, initial_multipart),
            'Feições de entrada: {} | nulas: {} | vazias: {} | inválidas: {} | multipartes: {}'
            .format(input_count, initial_null, initial_empty,
                    initial_invalid, initial_multipart)
        ))

        counters = {
            'null_empty_removed': 0,
            'invalid_fixed': 0,
            'invalid_blocked': 0,
            'multipart_split': 0,
            'duplicates_removed': 0,
            'holes_modified': 0,
            'slivers_removed': 0,
            'grid_modified': 0,
            'grid_blocked': 0,
            'duplicate_vertices_modified': 0,
            'connect_modified': 0,
            'connect_blocked': 0,
            'final_duplicates_removed': 0
        }

        # 1) Nulas e vazias
        if remove_null_empty:
            feedback.pushInfo(self.tr(
                'Removing null or empty geometries...',
                'Removendo geometrias nulas ou vazias...'
            ))
            kept = []
            for rec in records:
                geom = rec['geom']
                if geom is None or geom.isNull():
                    reason = self.tr('Null geometry', 'Geometria nula')
                elif geom.isEmpty():
                    reason = self.tr('Empty geometry', 'Geometria vazia')
                else:
                    kept.append(rec)
                    continue

                self._write_removed(
                    removed_sink, removed_fields, rec, input_fields,
                    'remove_null_empty', reason, distance_area
                )
                self._write_report(
                    report_sink, report_fields, rec,
                    'remove_null_empty', 'removed', reason,
                    geom, QgsGeometry(), distance_area
                )
                counters['null_empty_removed'] += 1
            records = kept

        if feedback.isCanceled():
            raise QgsProcessingException(self.tr(
                'Operation canceled by the user.',
                'Operação cancelada pelo usuário.'
            ))

        # 2) Corrigir inválidas
        if fix_invalid:
            feedback.pushInfo(self.tr(
                'Repairing invalid geometries...',
                'Corrigindo geometrias inválidas...'
            ))
            for rec in records:
                old_geom = rec['geom']
                if (
                    old_geom is None
                    or old_geom.isNull()
                    or old_geom.isEmpty()
                    or old_geom.isGeosValid()
                ):
                    continue

                try:
                    repaired = self._polygonal_only(
                        old_geom.makeValid()
                    )
                except Exception:
                    repaired = QgsGeometry()

                safe, _ = self._safe_geometry(
                    old_geom, repaired, allow_multi=True
                )

                if safe and repaired.isGeosValid():
                    rec['geom'] = QgsGeometry(repaired)
                    counters['invalid_fixed'] += 1
                    self._write_report(
                        report_sink, report_fields, rec,
                        'fix_invalid', 'modified',
                        self.tr('Invalid geometry repaired',
                                'Geometria inválida corrigida'),
                        old_geom, repaired, distance_area
                    )
                else:
                    counters['invalid_blocked'] += 1
                    self._write_report(
                        report_sink, report_fields, rec,
                        'fix_invalid', 'blocked',
                        self.tr(
                            'Invalid geometry could not be safely repaired; original geometry preserved',
                            'A geometria inválida não pôde ser corrigida com segurança; geometria original preservada'
                        ),
                        old_geom, old_geom, distance_area
                    )

        # 3) Multipartes para simples
        if singleparts:
            feedback.pushInfo(self.tr(
                'Converting multipart features to singleparts...',
                'Convertendo feições multipartes em partes simples...'
            ))
            new_records = []

            for rec in records:
                geom = rec['geom']
                if (
                    geom is None
                    or geom.isNull()
                    or geom.isEmpty()
                    or not geom.isMultipart()
                ):
                    new_records.append(rec)
                    continue

                if not geom.isGeosValid():
                    new_records.append(rec)
                    self._write_report(
                        report_sink, report_fields, rec,
                        'multipart_to_singleparts', 'blocked',
                        self.tr(
                            'Invalid multipart geometry was preserved for manual review',
                            'A geometria multiparte inválida foi preservada para revisão manual'
                        ),
                        geom, geom, distance_area
                    )
                    continue

                parts = [
                    QgsGeometry(p)
                    for p in geom.asGeometryCollection()
                    if (
                        p is not None
                        and not p.isNull()
                        and not p.isEmpty()
                        and p.type() == Qgis.GeometryType.Polygon
                    )
                ]

                if not parts:
                    new_records.append(rec)
                    self._write_report(
                        report_sink, report_fields, rec,
                        'multipart_to_singleparts', 'blocked',
                        self.tr(
                            'Multipart geometry could not be split safely',
                            'A geometria multiparte não pôde ser separada com segurança'
                        ),
                        geom, geom, distance_area
                    )
                    continue

                counters['multipart_split'] += 1
                for part_idx, part_geom in enumerate(parts, start=1):
                    part_rec = {
                        'uid': uid,
                        'orig_id': rec['orig_id'],
                        'part': part_idx,
                        'attrs': rec['attrs'][:],
                        'geom': QgsGeometry(part_geom)
                    }
                    uid += 1
                    new_records.append(part_rec)
                    self._write_report(
                        report_sink, report_fields, part_rec,
                        'multipart_to_singleparts', 'modified',
                        self.tr(
                            'Multipart feature converted to singlepart',
                            'Feição multiparte convertida em parte simples'
                        ),
                        geom, part_geom, distance_area
                    )
            records = new_records

        # 4) Geometrias duplicadas
        if remove_duplicates:
            feedback.pushInfo(self.tr(
                'Removing duplicate geometries...',
                'Removendo geometrias duplicadas...'
            ))
            records, count = self._remove_duplicates(
                records, removed_sink, removed_fields,
                input_fields, distance_area,
                report_sink, report_fields,
                'remove_duplicate_geometries'
            )
            counters['duplicates_removed'] += count

        # 5) Buracos
        if remove_holes:
            feedback.pushInfo(self.tr(
                'Removing holes...',
                'Removendo buracos...'
            ))
            for rec in records:
                old_geom = rec['geom']
                if (
                    old_geom is None
                    or old_geom.isNull()
                    or old_geom.isEmpty()
                    or old_geom.type() != Qgis.GeometryType.Polygon
                    or not old_geom.isGeosValid()
                ):
                    continue

                try:
                    # Para parcelas/lotes, quando esta opção está ativa,
                    # todos os anéis internos são removidos.
                    new_geom = old_geom.removeInteriorRings()
                except Exception:
                    continue

                if (
                    new_geom is None
                    or new_geom.isNull()
                    or new_geom.isEmpty()
                    or old_geom.asWkb() == new_geom.asWkb()
                ):
                    continue

                safe, _ = self._safe_geometry(
                    old_geom, new_geom,
                    allow_multi=not singleparts
                )

                if safe:
                    rec['geom'] = QgsGeometry(new_geom)
                    counters['holes_modified'] += 1
                    self._write_report(
                        report_sink, report_fields, rec,
                        'remove_holes', 'modified',
                        self.tr('Interior rings removed',
                                'Anéis internos removidos'),
                        old_geom, new_geom, distance_area
                    )
                else:
                    self._write_report(
                        report_sink, report_fields, rec,
                        'remove_holes', 'blocked',
                        self.tr(
                            'Hole removal produced an unsafe geometry; original geometry preserved',
                            'A remoção de buracos produziu uma geometria insegura; geometria original preservada'
                        ),
                        old_geom, old_geom, distance_area
                    )

        # 6) Filetes
        if remove_slivers:
            feedback.pushInfo(self.tr(
                'Identifying excessively narrow polygons...',
                'Identificando polígonos excessivamente estreitos...'
            ))
            kept = []
            for rec in records:
                geom = rec['geom']
                if (
                    geom is None
                    or geom.isNull()
                    or geom.isEmpty()
                    or not geom.isGeosValid()
                ):
                    kept.append(rec)
                    if (
                        geom is not None
                        and not geom.isNull()
                        and not geom.isEmpty()
                        and not geom.isGeosValid()
                    ):
                        self._write_report(
                            report_sink, report_fields, rec,
                            'remove_slivers', 'blocked',
                            self.tr(
                                'Sliver test was skipped because the geometry is invalid',
                                'O teste de filete foi ignorado porque a geometria é inválida'
                            ),
                            geom, geom, distance_area
                        )
                    continue

                ratio, _, _ = self._shape_ratio(
                    geom, distance_area
                )
                if ratio < min_shape_ratio:
                    reason = self.tr(
                        'Equivalent-rectangle width/length ratio ({:.8f}) is below the minimum ({:.8f})'
                        .format(ratio, min_shape_ratio),
                        'A razão largura/comprimento do retângulo equivalente ({:.8f}) é inferior ao mínimo ({:.8f})'
                        .format(ratio, min_shape_ratio)
                    )
                    self._write_removed(
                        removed_sink, removed_fields, rec, input_fields,
                        'remove_slivers', reason, distance_area,
                        shape_ratio=ratio
                    )
                    self._write_report(
                        report_sink, report_fields, rec,
                        'remove_slivers', 'removed', reason,
                        rec['geom'], QgsGeometry(), distance_area
                    )
                    counters['slivers_removed'] += 1
                else:
                    kept.append(rec)
            records = kept

        # 7) Aderir à grade
        if snap_grid:
            feedback.pushInfo(self.tr(
                'Snapping coordinates to grid...',
                'Aderindo coordenadas à grade...'
            ))
            for rec in records:
                old_geom = rec['geom']
                if (
                    old_geom is None
                    or old_geom.isNull()
                    or old_geom.isEmpty()
                ):
                    continue

                if not old_geom.isGeosValid():
                    counters['grid_blocked'] += 1
                    self._write_report(
                        report_sink, report_fields, rec,
                        'snap_to_grid', 'blocked',
                        self.tr(
                            'Grid snapping was skipped because the geometry is invalid',
                            'A aderência à grade foi ignorada porque a geometria é inválida'
                        ),
                        old_geom, old_geom, distance_area
                    )
                    continue

                try:
                    new_geom = old_geom.snappedToGrid(
                        grid_spacing, grid_spacing, 0.0, 0.0
                    )
                except Exception:
                    new_geom = QgsGeometry()

                if (
                    new_geom is not None
                    and not new_geom.isNull()
                    and not new_geom.isEmpty()
                    and old_geom.asWkb() == new_geom.asWkb()
                ):
                    continue

                safe, _ = self._safe_geometry(
                    old_geom, new_geom,
                    allow_multi=not singleparts
                )

                if safe:
                    rec['geom'] = QgsGeometry(new_geom)
                    counters['grid_modified'] += 1
                    self._write_report(
                        report_sink, report_fields, rec,
                        'snap_to_grid', 'modified',
                        self.tr('Coordinates snapped to grid',
                                'Coordenadas aderidas à grade'),
                        old_geom, new_geom, distance_area
                    )
                else:
                    counters['grid_blocked'] += 1
                    self._write_report(
                        report_sink, report_fields, rec,
                        'snap_to_grid', 'blocked',
                        self.tr(
                            'Grid snapping produced an unsafe geometry; original geometry preserved',
                            'A aderência à grade produziu uma geometria insegura; geometria original preservada'
                        ),
                        old_geom, old_geom, distance_area
                    )

        # 8) Vértices duplicados
        if remove_duplicate_vertices:
            feedback.pushInfo(self.tr(
                'Removing duplicate vertices...',
                'Removendo vértices duplicados...'
            ))
            for rec in records:
                old_geom = rec['geom']
                if (
                    old_geom is None
                    or old_geom.isNull()
                    or old_geom.isEmpty()
                    or not old_geom.isGeosValid()
                ):
                    continue

                new_geom = QgsGeometry(old_geom)
                try:
                    changed = new_geom.removeDuplicateNodes()
                except Exception:
                    changed = False

                if not changed:
                    continue

                safe, _ = self._safe_geometry(
                    old_geom, new_geom,
                    allow_multi=not singleparts
                )

                if safe:
                    rec['geom'] = QgsGeometry(new_geom)
                    counters['duplicate_vertices_modified'] += 1
                    self._write_report(
                        report_sink, report_fields, rec,
                        'remove_duplicate_vertices', 'modified',
                        self.tr('Duplicate vertices removed',
                                'Vértices duplicados removidos'),
                        old_geom, new_geom, distance_area
                    )
                else:
                    self._write_report(
                        report_sink, report_fields, rec,
                        'remove_duplicate_vertices', 'blocked',
                        self.tr(
                            'Duplicate-vertex removal produced an unsafe geometry; original geometry preserved',
                            'A remoção de vértices duplicados produziu uma geometria insegura; geometria original preservada'
                        ),
                        old_geom, old_geom, distance_area
                    )

        # 9) Conectividade
        if connect and records:
            feedback.pushInfo(self.tr(
                'Adjusting connectivity between adjacent polygons...',
                'Ajustando conectividade entre polígonos adjacentes...'
            ))

            work, uid_field = self._work_layer(
                records, input_fields, crs, source.wkbType()
            )

            snapped = processing.run(
                'native:snapgeometries',
                {
                    'INPUT': work,
                    'REFERENCE_LAYER': work,
                    'TOLERANCE': connect_tolerance,
                    'BEHAVIOR': connect_behavior,
                    'OUTPUT': 'TEMPORARY_OUTPUT'
                },
                context=context,
                feedback=feedback
            )['OUTPUT']

            result_by_uid = {}
            for feat in snapped.getFeatures():
                try:
                    rec_uid = int(feat[uid_field])
                except (TypeError, ValueError):
                    continue
                result_by_uid[rec_uid] = QgsGeometry(feat.geometry())

            for rec in records:
                old_geom = rec['geom']
                new_geom = result_by_uid.get(rec['uid'])

                if new_geom is None:
                    counters['connect_blocked'] += 1
                    self._write_report(
                        report_sink, report_fields, rec,
                        'connect_polygons', 'blocked',
                        self.tr(
                            'Connectivity result was not found; original geometry preserved',
                            'O resultado da conectividade não foi encontrado; geometria original preservada'
                        ),
                        old_geom, old_geom, distance_area
                    )
                    continue

                if old_geom.asWkb() == new_geom.asWkb():
                    continue

                safe, _ = self._safe_geometry(
                    old_geom, new_geom,
                    allow_multi=not singleparts
                )

                if safe:
                    rec['geom'] = QgsGeometry(new_geom)
                    counters['connect_modified'] += 1
                    self._write_report(
                        report_sink, report_fields, rec,
                        'connect_polygons', 'modified',
                        self.tr(
                            'Connectivity adjusted within tolerance',
                            'Conectividade ajustada dentro da tolerância'
                        ),
                        old_geom, new_geom, distance_area
                    )
                else:
                    counters['connect_blocked'] += 1
                    self._write_report(
                        report_sink, report_fields, rec,
                        'connect_polygons', 'blocked',
                        self.tr(
                            'Connectivity adjustment produced an unsafe geometry; original geometry preserved',
                            'O ajuste de conectividade produziu uma geometria insegura; geometria original preservada'
                        ),
                        old_geom, old_geom, distance_area
                    )

        # 10) Segunda limpeza
        if remove_duplicate_vertices:
            for rec in records:
                old_geom = rec['geom']
                if (
                    old_geom is None
                    or old_geom.isNull()
                    or old_geom.isEmpty()
                    or not old_geom.isGeosValid()
                ):
                    continue

                new_geom = QgsGeometry(old_geom)
                try:
                    changed = new_geom.removeDuplicateNodes()
                except Exception:
                    changed = False

                if not changed:
                    continue

                safe, _ = self._safe_geometry(
                    old_geom, new_geom,
                    allow_multi=not singleparts
                )
                if safe:
                    rec['geom'] = QgsGeometry(new_geom)
                    counters['duplicate_vertices_modified'] += 1
                    self._write_report(
                        report_sink, report_fields, rec,
                        'final_duplicate_vertices', 'modified',
                        self.tr(
                            'Duplicate vertices removed after topological corrections',
                            'Vértices duplicados removidos após as correções topológicas'
                        ),
                        old_geom, new_geom, distance_area
                    )

        if remove_duplicates:
            records, count = self._remove_duplicates(
                records, removed_sink, removed_fields,
                input_fields, distance_area,
                report_sink, report_fields,
                'final_duplicate_geometries'
            )
            counters['final_duplicates_removed'] += count

        # 11) Validação final
        final_null = final_empty = final_invalid = 0
        final_multipart = final_slivers = 0

        for rec in records:
            geom = rec['geom']
            if geom is None or geom.isNull():
                final_null += 1
                continue
            if geom.isEmpty():
                final_empty += 1
                continue
            if not geom.isGeosValid():
                final_invalid += 1
            if geom.isMultipart():
                final_multipart += 1

            ratio, _, _ = self._shape_ratio(
                geom, distance_area
            )
            if ratio < min_shape_ratio:
                final_slivers += 1

        final_overlaps = self._count_overlaps(records)

        # 12) Saída
        feedback.pushInfo(self.tr(
            'Writing corrected parcel layer...',
            'Gravando camada de lotes corrigidos...'
        ))

        for rec in records:
            feat = QgsFeature(input_fields)
            feat.setGeometry(QgsGeometry(rec['geom']))
            feat.setAttributes(rec['attrs'])
            sink.addFeature(feat, QgsFeatureSink.Flag.FastInsert)

        feedback.pushInfo('----------------------------------------')
        feedback.pushInfo(self.tr(
            'PARCEL TOPOLOGY CLEANUP SUMMARY',
            'RESUMO DA LIMPEZA E CORREÇÃO TOPOLÓGICA'
        ))
        feedback.pushInfo(self.tr(
            'Input features: {}'.format(input_count),
            'Feições de entrada: {}'.format(input_count)
        ))
        feedback.pushInfo(self.tr(
            'Null/empty geometries removed: {}'
            .format(counters['null_empty_removed']),
            'Geometrias nulas/vazias removidas: {}'
            .format(counters['null_empty_removed'])
        ))
        feedback.pushInfo(self.tr(
            'Invalid geometries repaired: {} | blocked: {}'
            .format(counters['invalid_fixed'],
                    counters['invalid_blocked']),
            'Geometrias inválidas corrigidas: {} | bloqueadas: {}'
            .format(counters['invalid_fixed'],
                    counters['invalid_blocked'])
        ))
        feedback.pushInfo(self.tr(
            'Multipart features split: {}'
            .format(counters['multipart_split']),
            'Feições multipartes separadas: {}'
            .format(counters['multipart_split'])
        ))
        feedback.pushInfo(self.tr(
            'Duplicate geometries removed: {}'
            .format(counters['duplicates_removed']
                    + counters['final_duplicates_removed']),
            'Geometrias duplicadas removidas: {}'
            .format(counters['duplicates_removed']
                    + counters['final_duplicates_removed'])
        ))
        feedback.pushInfo(self.tr(
            'Features with holes removed: {}'
            .format(counters['holes_modified']),
            'Feições com buracos removidos: {}'
            .format(counters['holes_modified'])
        ))
        feedback.pushInfo(self.tr(
            'Sliver polygons removed: {}'
            .format(counters['slivers_removed']),
            'Polígonos em forma de filete removidos: {}'
            .format(counters['slivers_removed'])
        ))
        feedback.pushInfo(self.tr(
            'Features snapped to grid: {} | blocked: {}'
            .format(counters['grid_modified'],
                    counters['grid_blocked']),
            'Feições aderidas à grade: {} | bloqueadas: {}'
            .format(counters['grid_modified'],
                    counters['grid_blocked'])
        ))
        feedback.pushInfo(self.tr(
            'Features with duplicate vertices removed: {}'
            .format(counters['duplicate_vertices_modified']),
            'Feições com vértices duplicados removidos: {}'
            .format(counters['duplicate_vertices_modified'])
        ))
        feedback.pushInfo(self.tr(
            'Connectivity adjustments: {} | blocked: {}'
            .format(counters['connect_modified'],
                    counters['connect_blocked']),
            'Ajustes de conectividade: {} | bloqueados: {}'
            .format(counters['connect_modified'],
                    counters['connect_blocked'])
        ))

        feedback.pushInfo('----------------------------------------')
        feedback.pushInfo(self.tr('FINAL VALIDATION', 'VALIDAÇÃO FINAL'))
        feedback.pushInfo(self.tr(
            'Output features: {}'.format(len(records)),
            'Feições de saída: {}'.format(len(records))
        ))
        feedback.pushInfo(self.tr(
            'Null: {} | empty: {} | invalid: {} | multipart: {}'
            .format(final_null, final_empty,
                    final_invalid, final_multipart),
            'Nulas: {} | vazias: {} | inválidas: {} | multipartes: {}'
            .format(final_null, final_empty,
                    final_invalid, final_multipart)
        ))
        feedback.pushInfo(self.tr(
            'Remaining sliver polygons: {}'
            .format(final_slivers),
            'Polígonos em forma de filete remanescentes: {}'
            .format(final_slivers)
        ))
        feedback.pushInfo(self.tr(
            'Overlapping polygon pairs detected: {}'
            .format(final_overlaps),
            'Pares de polígonos com sobreposição detectados: {}'
            .format(final_overlaps)
        ))

        if (
            final_null
            or final_empty
            or final_invalid
            or (singleparts and final_multipart)
            or final_slivers
            or final_overlaps
        ):
            feedback.pushWarning(self.tr(
                'Remaining problems were detected. Review the final validation results and the audit table.',
                'Foram detectados problemas remanescentes. Revise os resultados da validação final e a tabela de auditoria.'
            ))
        else:
            feedback.pushInfo(self.tr(
                'No problems covered by the final validation were detected.',
                'Não foram detectados problemas contemplados pela validação final.'
            ))

        feedback.pushInfo(self.tr(
            'Operation completed successfully!',
            'Operação finalizada com sucesso!'
        ))
        feedback.pushInfo(self.tr(
            'Leandro Franca - Cartographic Engineer',
            'Leandro França - Eng Cart'
        ))

        return {
            self.OUTPUT: dest_id,
            self.REMOVED: removed_id,
            self.REPORT: report_id
        }