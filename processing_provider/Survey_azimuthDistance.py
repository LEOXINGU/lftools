# -*- coding: utf-8 -*-

"""
Survey_azimuthDistance.py
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
__date__ = '2021-03-08'
__copyright__ = '(C) 2021, Leandro França'

from qgis.PyQt.QtCore import QMetaType
from qgis.core import (
    QgsApplication, QgsProcessingAlgorithm, QgsProcessingException,
    QgsProcessingParameterPoint, QgsProcessingParameterString,
    QgsProcessingParameterCrs, QgsProcessingParameterBoolean,
    QgsProcessingParameterFeatureSink, QgsProcessingUtils, QgsProcessing,
    QgsFields, QgsField, QgsFeature, QgsFeatureSink, QgsGeometry, QgsPointXY,
    QgsMarkerSymbol, QgsLineSymbol, QgsSingleSymbolRenderer,
    QgsPalLayerSettings, QgsTextFormat, QgsTextBufferSettings,
    QgsVectorLayerSimpleLabeling, QgsUnitTypes, Qgis,
)
from math import sin, cos, radians, degrees, atan2, hypot, fsum, isfinite
from lftools.geocapt.imgs import Imgs
from lftools.translations.translate import translate
from lftools.geocapt.topogeo import rumo_para_azimute
import os, re
from qgis.PyQt.QtGui import QIcon, QColor, QFont


class AzimuthDistance(QgsProcessingAlgorithm):

    LOC = QgsApplication.locale()[:2]

    def tr(self, *string):
        return translate(string, self.LOC)

    def createInstance(self):
        return AzimuthDistance()

    def name(self):
        return 'azimuthdistance'

    def displayName(self):
        return self.tr('Azimuth and distance', 'Azimute e distância')

    def group(self):
        return self.tr('Survey', 'Agrimensura')

    def groupId(self):
        return 'survey'

    def tags(self):
        return 'GeoOne,survey,agrimensura,azimuth,distance,traverse,analytical,total,station,angle'.split(',')

    def icon(self):
        return QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images/total_station.png'))

    txt_en = (
        'Generates <b>point and line layers</b> from origin coordinates, horizontal '
        'distances and azimuths or quadrant bearings. Vertex codes are optional; '
        'when omitted, vertices are numbered sequentially. For closed traverses, '
        'the Bowditch method compensates the misclosure and reports quality '
        'indicators in the log.'
    )
    txt_pt = (
        'Gera camadas de <b>pontos e linhas</b> a partir das coordenadas iniciais, '
        'distâncias horizontais e azimutes ou rumos. Os códigos dos vértices são '
        'opcionais; quando omitidos, utiliza-se a sequência numérica. Para '
        'poligonais fechadas, compensa o erro de fechamento pelo método de '
        'Bowditch e apresenta os indicadores de qualidade no log.'
    )
    figure = 'images/tutorial/survey_azimuth_distance.jpg' 

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
    AZIMUTHS = 'AZIMUTHS'
    DISTANCES = 'DISTANCES'
    CODES = 'CODES'
    CRS = 'CRS'
    CLOSED = 'CLOSED'
    OUTPUT_POINTS = 'OUTPUT_POINTS'
    OUTPUT_LINES = 'OUTPUT_LINES'

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterPoint(
            self.POINT,
            self.tr('Origin point coordinates', 'Coordenadas do ponto inicial'),
            defaultValue=QgsPointXY(0.0, 0.0)))
        self.addParameter(QgsProcessingParameterString(
            self.DISTANCES,
            self.tr('List of horizontal distances', 'Lista de distâncias horizontais'),
            defaultValue='41.33, 50.21, 23.71, 36.75', multiLine=True))
        self.addParameter(QgsProcessingParameterString(
            self.AZIMUTHS,
            self.tr('List of directions (azimuths or bearings)',
                    'Lista de direções (azimutes ou rumos)'),
            defaultValue='34°12\'43.2", 82°51\'08.9", 132°26\'44.7", 35°08\'47.1"',
            multiLine=True))
        self.addParameter(QgsProcessingParameterString(
            self.CODES,
            self.tr('Vertex codes',
                    'Códigos dos vértices'),
            defaultValue='', optional=True))
        self.addParameter(QgsProcessingParameterCrs(
            self.CRS, self.tr('CRS', 'SRC'), 'ProjectCrs'))
        self.addParameter(QgsProcessingParameterBoolean(
            self.CLOSED,
            self.tr('Closed traverse: compensate coordinate misclosure (Bowditch)',
                    'Poligonal fechada: compensar erro de fechamento (Bowditch)'),
            defaultValue=False))
        self.addParameter(QgsProcessingParameterFeatureSink(
            self.OUTPUT_POINTS, self.tr('Vertices', 'Vértices'),
            type=QgsProcessing.TypeVectorPoint))
        self.addParameter(QgsProcessingParameterFeatureSink(
            self.OUTPUT_LINES, self.tr('Traverse sides', 'Lados da poligonal'),
            type=QgsProcessing.TypeVectorLine))

    @staticmethod
    def _split_values(text, keep_empty=False):
        # Semicolons allow decimal commas. Otherwise commas are separators.
        text = text.strip().replace('\r\n', '\n').replace('\r', '\n')
        if not text:
            return []
        separator = ';' if ';' in text else ','
        # A line break after a delimiter is formatting, not an extra value.
        text = re.sub(re.escape(separator) + r'[ \t]*\n[ \t]*', separator, text)
        text = re.sub(r'\n[ \t]*' + re.escape(separator), separator, text)
        values = [value.strip() for value in re.split(
            re.escape(separator) + r'|\n', text)]
        # Preserve positions: blank codes default to sequence, blank observations
        # are rejected instead of silently shifting the distance/direction pairs.
        return values

    def _vertex_codes(self, text, count, closed):
        if not text.strip():
            return [str(k + 1) for k in range(count)]
        codes = self._split_values(text, keep_empty=True)
        # Accept an explicitly repeated origin, but never a distinct last code.
        if closed and len(codes) == count + 1:
            first = codes[0] or '1'
            if codes[-1] != first:
                raise QgsProcessingException(self.tr(
                    'The repeated final code must match the origin code.',
                    'O código repetido no final deve ser igual ao do ponto inicial.'))
            codes.pop()
        if len(codes) != count:
            raise QgsProcessingException(self.tr(
                'Expected {} vertex codes, starting at the origin; received {}.',
                'Esperados {} códigos de vértices, começando no ponto inicial; recebidos {}.'
            ).format(count, len(codes)))
        return [code or str(k + 1) for k, code in enumerate(codes)]

    def string_to_azimuth_deg(self, text):
        """Parse decimal/DMS azimuths and quadrant bearings, including NO/SO."""
        original = text
        text = (text.strip().upper().replace('º', '°')
                .replace('′', "'").replace('’', "'").replace('‘', "'")
                .replace('´', "'").replace('`', "'").replace('″', '"')
                .replace('“', '"').replace('”', '"'))
        letters = ''.join(re.findall(r'[A-Z]', text)).replace('O', 'W')
        if letters and letters not in ('N', 'S', 'E', 'W', 'NE', 'SE', 'SW', 'NW'):
            raise QgsProcessingException(self.tr(
                'Invalid quadrant in direction: {}', 'Quadrante inválido na direção: {}'
            ).format(original))
        numeric = re.sub(r'[NSEWO]', '', text).strip()
        # Keep spaces as DMS separators (the original helper removes them).
        if not numeric or re.search(r'[^0-9.,+\-\s°\'":]', numeric):
            raise QgsProcessingException(self.tr(
                'Invalid direction: {}', 'Direção inválida: {}').format(original))
        components = re.sub(r'[°\'":]', ' ', numeric).split()
        try:
            if not 1 <= len(components) <= 3:
                raise ValueError('DMS')
            values = [float(value.replace(',', '.')) for value in components]
            if not all(isfinite(value) for value in values):
                raise ValueError('finite')
            if len(values) > 1:
                if not values[0].is_integer() or not 0 <= values[1] < 60:
                    raise ValueError('minutes')
            if len(values) > 2:
                if not values[1].is_integer() or not 0 <= values[2] < 60:
                    raise ValueError('seconds')
            angle = abs(values[0])
            if len(values) > 1:
                angle += values[1] / 60.0
            if len(values) > 2:
                angle += values[2] / 3600.0
            if components[0].startswith('-'):
                angle = -angle
            if letters:
                return float(rumo_para_azimute(angle, letters))
            if not 0.0 <= angle <= 360.0:
                raise ValueError('range')
            return angle % 360.0
        except (ValueError, OverflowError) as error:
            raise QgsProcessingException(self.tr(
                'Invalid direction: {}. Check degrees, minutes, seconds and quadrant.',
                'Direção inválida: {}. Verifique graus, minutos, segundos e quadrante.'
            ).format(original)) from error

    @staticmethod
    def _fields(definitions):
        fields = QgsFields()
        for name, field_type in definitions:
            fields.append(QgsField(name, field_type))
        return fields

    def processAlgorithm(self, parameters, context, feedback):
        self._output_ids = {}
        crs = self.parameterAsCrs(parameters, self.CRS, context)
        if not crs.isValid() or crs.isGeographic():
            raise QgsProcessingException(self.tr(
                'Choose a valid projected CRS.', 'Escolha um SRC projetado válido.'))
        # Transform a clicked/CRS-tagged origin to the OUTPUT CRS, not project CRS.
        origin = self.parameterAsPoint(parameters, self.POINT, context, crs)
        if not all(isfinite(value) for value in (origin.x(), origin.y())):
            raise QgsProcessingException(self.tr(
                'Invalid origin coordinates.', 'Coordenadas iniciais inválidas.'))
        closed = self.parameterAsBool(parameters, self.CLOSED, context)
        distance_text = self.parameterAsString(parameters, self.DISTANCES, context)
        direction_text = self.parameterAsString(parameters, self.AZIMUTHS, context)
        try:
            distances = [float(value.replace(',', '.'))
                         for value in self._split_values(distance_text)]
        except ValueError as error:
            raise QgsProcessingException(self.tr(
                'Invalid distance list.', 'Lista de distâncias inválida.')) from error
        directions = self._split_values(direction_text)
        if not distances or len(distances) != len(directions):
            raise QgsProcessingException(self.tr(
                'Enter the same nonzero number of distances and directions.',
                'Informe a mesma quantidade, não nula, de distâncias e direções.'))
        if not all(directions):
            raise QgsProcessingException(self.tr(
                'The direction list contains an empty value.',
                'A lista de direções contém um valor vazio.'))
        if not all(isfinite(value) and value > 0 for value in distances):
            raise QgsProcessingException(self.tr(
                'All distances must be finite and greater than zero.',
                'Todas as distâncias devem ser finitas e maiores que zero.'))
        n = len(distances)
        if closed and n < 3:
            raise QgsProcessingException(self.tr(
                'A closed traverse requires at least three measured sides.',
                'Uma poligonal fechada exige pelo menos três lados medidos.'))
        codes = self._vertex_codes(
            self.parameterAsString(parameters, self.CODES, context),
            n if closed else n + 1, closed)
        azimuths = []
        for k, text in enumerate(directions):
            if feedback.isCanceled():
                return {}
            try:
                azimuths.append(self.string_to_azimuth_deg(text))
            except QgsProcessingException as error:
                raise QgsProcessingException(self.tr(
                    'Side {}: {}', 'Lado {}: {}').format(k + 1, error)) from error

        try:
            length = fsum(distances)
        except OverflowError as error:
            raise QgsProcessingException(self.tr(
                'Traverse length exceeds numeric limits.',
                'O comprimento da poligonal excede os limites numéricos.')) from error
        deltas_e = [d * sin(radians(az)) for d, az in zip(distances, azimuths)]
        deltas_n = [d * cos(radians(az)) for d, az in zip(distances, azimuths)]
        error_e, error_n = fsum(deltas_e), fsum(deltas_n)
        error_linear = hypot(error_e, error_n)
        corrections_e = [-error_e * (d / length) if closed else 0.0 for d in distances]
        corrections_n = [-error_n * (d / length) if closed else 0.0 for d in distances]
        adjusted_e = [de + ce for de, ce in zip(deltas_e, corrections_e)]
        adjusted_n = [dn + cn for dn, cn in zip(deltas_n, corrections_n)]
        raw_points, points = [origin], [origin]
        raw_e = raw_n = offset_e = offset_n = 0.0
        for k in range(n):
            if feedback.isCanceled():
                return {}
            raw_e += deltas_e[k]
            raw_n += deltas_n[k]
            offset_e += adjusted_e[k]
            offset_n += adjusted_n[k]
            raw_points.append(QgsPointXY(origin.x() + raw_e, origin.y() + raw_n))
            points.append(QgsPointXY(origin.x() + offset_e, origin.y() + offset_n))
        if not all(isfinite(v) for point in raw_points + points
                   for v in (point.x(), point.y())):
            raise QgsProcessingException(self.tr(
                'Calculated coordinates exceed numeric limits.',
                'As coordenadas calculadas excedem os limites numéricos.'))
        # Report BEFORE snapping the terminal point to the origin.
        residual_e, residual_n = fsum(adjusted_e), fsum(adjusted_n)
        coordinate_residual = hypot(points[-1].x() - origin.x(),
                                    points[-1].y() - origin.y())
        if closed:
            points[-1] = QgsPointXY(origin.x(), origin.y())
        unit = QgsUnitTypes.toAbbreviatedString(crs.mapUnits())
        self._unit = unit
        feedback.pushInfo(self.tr(
            'Distances and coordinates are in the CRS unit: {}.',
            'Distâncias e coordenadas estão na unidade do SRC: {}.').format(unit))
        feedback.pushInfo(self.tr(
            'Grid azimuths; no ground-to-grid reduction applied.',
            'Azimutes de quadrícula; sem redução das distâncias ao plano.'))
        feedback.pushInfo(self.tr(
            'Measured sides: {}; sum of input distances: {:.6f} {}.',
            'Lados medidos: {}; soma das distâncias de entrada: {:.6f} {}.'
        ).format(n, length, unit))
        if closed:
            self._log_closure(feedback, length, error_e, error_n, error_linear,
                              residual_e, residual_n, coordinate_residual,
                              corrections_e, corrections_n, raw_points, points, unit)

        integer, string, real = (QMetaType.Type.Int, QMetaType.Type.QString,
                                 QMetaType.Type.Double)
        point_fields = self._fields([
            ('id', integer), ('sequence', integer), ('code', string),
            ('easting', real), ('northing', real), ('e_raw', real), ('n_raw', real),
            ('corr_e', real), ('corr_n', real)])
        line_fields = self._fields([
            ('id', integer), ('from_code', string), ('to_code', string),
            ('azimuth', real), ('distance', real), ('az_calc', real),
            ('dist_calc', real), ('corr_e', real), ('corr_n', real)])
        point_sink, point_id = self.parameterAsSink(
            parameters, self.OUTPUT_POINTS, context, point_fields,
            Qgis.WkbType.Point, crs)
        if point_sink is None:
            raise QgsProcessingException(self.invalidSinkError(parameters, self.OUTPUT_POINTS))
        line_sink, line_id = self.parameterAsSink(
            parameters, self.OUTPUT_LINES, context, line_fields,
            Qgis.WkbType.LineString, crs)
        if line_sink is None:
            raise QgsProcessingException(self.invalidSinkError(parameters, self.OUTPUT_LINES))
        self._output_ids = {self.OUTPUT_POINTS: point_id, self.OUTPUT_LINES: line_id}

        vertex_count = n if closed else n + 1
        total_features = vertex_count + n
        for k in range(vertex_count):
            if feedback.isCanceled():
                return self._output_ids
            point, raw = points[k], raw_points[k]
            feature = QgsFeature(point_fields)
            feature.setGeometry(QgsGeometry.fromPointXY(point))
            feature.setAttributes([
                k + 1, k + 1, codes[k], point.x(), point.y(), raw.x(), raw.y(),
                point.x() - raw.x(), point.y() - raw.y()])
            if not point_sink.addFeature(feature, QgsFeatureSink.Flag.FastInsert):
                raise QgsProcessingException(self.tr(
                    'Failed to write vertex {}.', 'Falha ao gravar o vértice {}.').format(k + 1))
            feedback.setProgress(100.0 * (k + 1) / total_features)
        geometric_length = 0.0
        for k in range(n):
            if feedback.isCanceled():
                return self._output_ids
            start, end = points[k], points[k + 1]
            de, dn = end.x() - start.x(), end.y() - start.y()
            distance = hypot(de, dn)
            # Undefined azimuth for a collapsed side is NULL, not north.
            azimuth = degrees(atan2(de, dn)) % 360.0 if distance > 0 else None
            if distance == 0:
                feedback.pushWarning(self.tr(
                    'Side {} has zero length in the output geometry.',
                    'O lado {} tem comprimento nulo na geometria de saída.').format(k + 1))
            geometric_length += distance
            feature = QgsFeature(line_fields)
            feature.setGeometry(QgsGeometry.fromPolylineXY([start, end]))
            feature.setAttributes([
                k + 1, codes[k], codes[(k + 1) % vertex_count], azimuths[k], distances[k],
                azimuth, distance, corrections_e[k], corrections_n[k]])
            if not line_sink.addFeature(feature, QgsFeatureSink.Flag.FastInsert):
                raise QgsProcessingException(self.tr(
                    'Failed to write side {}.', 'Falha ao gravar o lado {}.').format(k + 1))
            feedback.setProgress(100.0 * (vertex_count + k + 1) / total_features)
        feedback.pushInfo(self.tr(
            'Output geometric length: {:.6f} {}.',
            'Comprimento geométrico de saída: {:.6f} {}.').format(geometric_length, unit))
        feedback.pushInfo(self.tr(
            'Operation completed successfully!', 'Operação finalizada com sucesso!'))
        feedback.pushInfo(self.tr(
            'Leandro Franca - Cartographic Engineer', 'Leandro França - Eng Cart'))
        return self._output_ids

    def _log_closure(self, feedback, length, de, dn, error, re_, rn,
                     coordinate_residual, ce, cn, raw_points, points, unit):
        feedback.pushInfo(self.tr(
            'CLOSED TRAVERSE — BEFORE COMPENSATION',
            'POLIGONAL FECHADA — ANTES DA COMPENSAÇÃO'))
        for label, value in [('ΔE', de), ('ΔN', dn)]:
            feedback.pushInfo('{} = {:+.6f} {}'.format(label, value, unit))
        feedback.pushInfo(self.tr(
            'Linear misclosure: {:.6f} {}.', 'Erro linear de fechamento: {:.6f} {}.'
        ).format(error, unit))
        feedback.pushInfo(self.tr(
            'Relative misclosure (e / Σd): {:.10f}; {:.6f} ppm.',
            'Erro relativo de fechamento (e / Σd): {:.10f}; {:.6f} ppm.'
        ).format(error / length, 1e6 * error / length))
        if error <= 1e-12 * max(1.0, length):
            feedback.pushInfo(self.tr(
                'Closure ratio 1:N: not applicable (numerically zero misclosure).',
                'Relação de fechamento 1:N: não aplicável (erro numericamente nulo).'))
        else:
            feedback.pushInfo(self.tr(
                'Closure ratio: 1:{:.2f} (N = Σd / e).',
                'Relação de fechamento: 1:{:.2f} (N = Σd / e).').format(length / error))
            feedback.pushInfo(self.tr(
                'Misclosure vector grid azimuth: {:.8f}°.',
                'Azimute de quadrícula do vetor de fechamento: {:.8f}°.'
            ).format(degrees(atan2(de, dn)) % 360.0))
        feedback.pushInfo(self.tr(
            'Unadjusted terminal coordinates: E = {:.6f}; N = {:.6f} {}.',
            'Coordenadas finais sem compensação: E = {:.6f}; N = {:.6f} {}.'
        ).format(raw_points[-1].x(), raw_points[-1].y(), unit))
        feedback.pushInfo(self.tr(
            'Bowditch: cE_i = -ΔE × d_i / Σd; cN_i = -ΔN × d_i / Σd.',
            'Bowditch: cE_i = -ΔE × d_i / Σd; cN_i = -ΔN × d_i / Σd.'))
        for k, (e, n) in enumerate(zip(ce, cn)):
            feedback.pushInfo(self.tr(
                'Side {}: cE = {:+.6f}; cN = {:+.6f} {}.',
                'Lado {}: cE = {:+.6f}; cN = {:+.6f} {}.'
            ).format(k + 1, e, n, unit))
        feedback.pushInfo(self.tr(
            'Maximum side correction vector: {:.6f} {}.',
            'Maior vetor de correção de lado: {:.6f} {}.'
        ).format(max(hypot(e, n) for e, n in zip(ce, cn)), unit))
        # Exclude the duplicated terminal origin from vertex displacement stats.
        feedback.pushInfo(self.tr(
            'Maximum vertex displacement: {:.6f} {}.',
            'Maior deslocamento de vértice: {:.6f} {}.'
        ).format(max(hypot(p.x() - r.x(), p.y() - r.y())
                     for p, r in zip(points[:-1], raw_points[:-1])), unit))
        feedback.pushInfo(self.tr(
            'Residual before enforcing exact closure: ΔE = {:+.3e}; ΔN = {:+.3e} {}.',
            'Resíduo antes de fixar o fechamento exato: ΔE = {:+.3e}; ΔN = {:+.3e} {}.'
        ).format(re_, rn, unit))
        feedback.pushInfo(self.tr(
            'Coordinate residual before enforcing exact closure: {:.3e} {}.',
            'Resíduo em coordenadas antes de fixar o fechamento exato: {:.3e} {}.'
        ).format(coordinate_residual, unit))
        feedback.pushInfo(self.tr(
            'The terminal point is set to the origin. A zero adjusted closure does '
            'not establish positional accuracy. Angular misclosure cannot be '
            'evaluated without independent angular observations.',
            'O ponto final é fixado no inicial. Fechamento compensado nulo não '
            'comprova acurácia posicional. Não é possível avaliar o erro angular '
            'sem observações angulares independentes.'))

    def postProcessAlgorithm(self, context, feedback):
        """Style both outputs on the context thread, as in Doc_PointsFromText."""
        for output, destination in getattr(self, '_output_ids', {}).items():
            if feedback.isCanceled():
                break
            layer = QgsProcessingUtils.mapLayerFromString(destination, context)
            if layer is None or not layer.isValid():
                feedback.pushWarning(self.tr(
                    'Could not style output: {}.', 'Não foi possível aplicar o estilo: {}.'
                ).format(output))
                continue
            settings = QgsPalLayerSettings()
            settings.enabled = True
            settings.isExpression = True
            if output == self.OUTPUT_POINTS:
                symbol = QgsMarkerSymbol.createSimple({
                    'name': 'circle', 'color': '255,0,255', 'size': '3.5',
                    'size_unit': 'MM', 'outline_style': 'no'})
                settings.fieldName = '"code"'
                settings.placement = Qgis.LabelPlacement.AroundPoint
                settings.dist = 2.0
            else:
                symbol = QgsLineSymbol.createSimple({
                    'line_color': '0,0,0', 'line_width': '0.5',
                    'line_width_unit': 'MM', 'line_style': 'solid'})
                # Label the actual output geometry; input observations are retained.
                unit = getattr(self, '_unit', '').replace("'", "''")
                settings.fieldName = (
                    "format_number(\"dist_calc\", 2) || ' " + unit + " | Az: ' || "
                    "coalesce(format_number(\"az_calc\", 4) || '°', '—')")
                settings.placement = Qgis.LabelPlacement.Line
            text_format = QgsTextFormat()
            font = QFont('Arial', 9)
            font.setBold(True)
            text_format.setFont(font)
            text_format.setSize(9)
            text_format.setColor(QColor('black'))
            buffer = QgsTextBufferSettings()
            buffer.setEnabled(True)
            buffer.setSize(0.7)
            buffer.setColor(QColor('white'))
            text_format.setBuffer(buffer)
            settings.setFormat(text_format)
            layer.setRenderer(QgsSingleSymbolRenderer(symbol))
            layer.setLabeling(QgsVectorLayerSimpleLabeling(settings))
            layer.setLabelsEnabled(True)
            layer.triggerRepaint()
        # Empty map preserves the two processAlgorithm output references.
        return {}

