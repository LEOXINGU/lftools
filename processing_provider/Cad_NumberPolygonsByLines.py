# -*- coding: utf-8 -*-

"""
Cad_NumberPolygonsByLines.py
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
__date__ = '2026-08-13'
__copyright__ = '(C) 2026, Leandro França'

from qgis.core import (
    QgsApplication,
    QgsCoordinateTransform,
    QgsGeometry,
    QgsProcessingAlgorithm,
    QgsProcessingException,
    QgsProcessingParameterBoolean,
    QgsProcessingParameterField,
    QgsProcessingParameterNumber,
    QgsProcessingParameterVectorLayer,
    QgsProject,
    QgsSpatialIndex,
    Qgis
)
from qgis.PyQt.QtCore import QVariant
from qgis.PyQt.QtGui import QIcon

from lftools.geocapt.imgs import Imgs
from lftools.translations.translate import translate

import os


class NumberPolygonsByLines(QgsProcessingAlgorithm):

    LOC = QgsApplication.locale()[:2]

    def tr(self, *string):
        return translate(string, self.LOC)

    def createInstance(self):
        return NumberPolygonsByLines()

    def name(self):
        return 'numberpolygonsbylines'

    def displayName(self):
        return self.tr('Number Polygons by Lines', 'Numerar Polígonos por Linhas')

    def group(self):
        return self.tr('Cadastre', 'Cadastro')

    def groupId(self):
        return 'cadastro'

    def tags(self):
        return 'GeoOne,cadastre,cadastro,polygon,poligono,line,linha,number,numbering,numerar,sequence,sequencia,direction,direcao,lot,lote'.split(',')

    def icon(self):
        return QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images/cadastre.png'))

    txt_en = 'This tool numbers polygons according to guide lines. Polygons intersected by each line are sorted following the geometric direction of the line. Lines can optionally be sorted by an attribute field and can also contain an attribute defining the first number of each sequence. If no first-number field is selected, the user defines a general initial value and chooses whether numbering restarts for every line or continues between lines.'
    txt_pt = 'Esta ferramenta numera polígonos de acordo com linhas diretrizes. Os polígonos interceptados por cada linha são ordenados seguindo o sentido geométrico da linha. As linhas podem opcionalmente ser ordenadas por um campo de atributo e também podem possuir um atributo que define o primeiro número de cada sequência. Se nenhum campo de primeiro número for selecionado, o usuário define um valor inicial geral e escolhe se a numeração reinicia a cada linha ou continua entre as linhas.'
    figure = 'images/tutorial/cadastre_numberpolygonsbylines.jpg'

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

    POLYGONS = 'POLYGONS'
    FIELD = 'FIELD'
    LINES = 'LINES'
    SELECTED_LINES = 'SELECTED_LINES'
    ORDER_FIELD = 'ORDER_FIELD'
    FIRST_FIELD = 'FIRST_FIELD'
    INITIAL = 'INITIAL'
    RESTART = 'RESTART'
    SAVE = 'SAVE'

    def initAlgorithm(self, config=None):

        self.addParameter(
            QgsProcessingParameterVectorLayer(
                self.POLYGONS,
                self.tr('Polygons to number', 'Polígonos a numerar'),
                [Qgis.ProcessingSourceType.TypeVectorPolygon]
            )
        )

        self.addParameter(
            QgsProcessingParameterField(
                self.FIELD,
                self.tr('Numbering field', 'Campo de numeração'),
                parentLayerParameterName=self.POLYGONS
            )
        )

        self.addParameter(
            QgsProcessingParameterVectorLayer(
                self.LINES,
                self.tr('Guide lines', 'Linhas diretrizes'),
                [Qgis.ProcessingSourceType.TypeVectorLine]
            )
        )

        self.addParameter(
            QgsProcessingParameterBoolean(
                self.SELECTED_LINES,
                self.tr('Use only selected lines', 'Usar apenas linhas selecionadas'),
                defaultValue=False
            )
        )

        self.addParameter(
            QgsProcessingParameterField(
                self.ORDER_FIELD,
                self.tr('Line order field (optional)', 'Campo de ordem das linhas (opcional)'),
                parentLayerParameterName=self.LINES,
                type=Qgis.ProcessingFieldParameterDataType.Numeric,
                optional=True
            )
        )

        self.addParameter(
            QgsProcessingParameterField(
                self.FIRST_FIELD,
                self.tr('First number field for each line (optional)', 'Campo do primeiro número de cada linha (opcional)'),
                parentLayerParameterName=self.LINES,
                type=Qgis.ProcessingFieldParameterDataType.Numeric,
                optional=True
            )
        )

        self.addParameter(
            QgsProcessingParameterNumber(
                self.INITIAL,
                self.tr('Initial number (used when no first-number field is selected)',
                        'Número inicial (usado quando não há campo de primeiro número)'),
                type=QgsProcessingParameterNumber.Type.Integer,
                defaultValue=1,
                minValue=0
            )
        )

        self.addParameter(
            QgsProcessingParameterBoolean(
                self.RESTART,
                self.tr('Restart numbering for each line', 'Reiniciar numeração a cada linha'),
                defaultValue=True
            )
        )

        self.addParameter(
            QgsProcessingParameterBoolean(
                self.SAVE,
                self.tr('Save Editions', 'Salvar Edições'),
                defaultValue=False
            )
        )

    # ---------------------------------------------------------------------
    # Geometry validation kept inside the tool for now. It is intentionally
    # independent from messages/exceptions so it can later be moved to a
    # common LFTools utility module and reused by other algorithms.
    # ---------------------------------------------------------------------
    def validate_geometries(self, layer, features=None):
        """
        Checks null, empty and invalid geometries.

        Parameters
        ----------
        layer : QgsVectorLayer
            Layer being checked.
        features : iterable of QgsFeature, optional
            Subset of features to validate. If None, all features are read.

        Returns
        -------
        dict
            IDs grouped in 'null', 'empty' and 'invalid'.
        """
        result = {
            'null': [],
            'empty': [],
            'invalid': []
        }

        iterator = features if features is not None else layer.getFeatures()

        for feat in iterator:
            geom = feat.geometry()

            if geom is None or geom.isNull():
                result['null'].append(feat.id())
                continue

            if geom.isEmpty():
                result['empty'].append(feat.id())
                continue

            if not geom.isGeosValid():
                result['invalid'].append(feat.id())

        return result

    def _format_ids(self, ids, limit=20):
        ids = list(ids)
        shown = ', '.join(str(fid) for fid in ids[:limit])
        if len(ids) > limit:
            shown += self.tr(' ... and {} more', ' ... e mais {}').format(len(ids) - limit)
        return shown

    def _raise_geometry_errors(self, polygon_errors, line_errors):
        messages = []

        def append_errors(title, errors):
            parts = []
            if errors['null']:
                parts.append(self.tr(
                    '{} null geometries (IDs: {})',
                    '{} geometrias nulas (IDs: {})'
                ).format(len(errors['null']), self._format_ids(errors['null'])))
            if errors['empty']:
                parts.append(self.tr(
                    '{} empty geometries (IDs: {})',
                    '{} geometrias vazias (IDs: {})'
                ).format(len(errors['empty']), self._format_ids(errors['empty'])))
            if errors['invalid']:
                parts.append(self.tr(
                    '{} invalid geometries (IDs: {})',
                    '{} geometrias inválidas (IDs: {})'
                ).format(len(errors['invalid']), self._format_ids(errors['invalid'])))

            if parts:
                messages.append(title + ':\n- ' + '\n- '.join(parts))

        append_errors(self.tr('Polygon layer', 'Camada de polígonos'), polygon_errors)
        append_errors(self.tr('Line layer', 'Camada de linhas'), line_errors)

        if messages:
            raise QgsProcessingException(
                self.tr(
                    'Geometry problems were found. Fix the geometries before running the tool.\n\n',
                    'Foram encontrados problemas geométricos. Corrija as geometrias antes de executar a ferramenta.\n\n'
                ) + '\n\n'.join(messages)
            )

    def _field_name(self, parameters, name, context):
        fields = self.parameterAsFields(parameters, name, context)
        return fields[0] if fields else None

    def _validate_line_attributes(self, line_features, order_field, first_field):
        """Validates optional fields selected from the line layer."""

        if order_field:
            null_ids = []
            values = {}
            duplicates = {}

            for feat in line_features:
                value = feat[order_field]
                if value is None or value == QVariant():
                    null_ids.append(feat.id())
                    continue

                # QGIS NULL values normally compare through QVariant helpers;
                # converting to string also catches providers returning NULL-like objects.
                if str(value).upper() == 'NULL':
                    null_ids.append(feat.id())
                    continue

                if value in values:
                    duplicates.setdefault(value, [values[value]]).append(feat.id())
                else:
                    values[value] = feat.id()

            if null_ids:
                raise QgsProcessingException(
                    self.tr(
                        'The line order field "{}" has NULL values. Feature IDs: {}',
                        'O campo de ordem das linhas "{}" possui valores NULL. IDs das feições: {}'
                    ).format(order_field, self._format_ids(null_ids))
                )

            if duplicates:
                details = []
                for value, ids in list(duplicates.items())[:20]:
                    details.append('{}: {}'.format(value, ', '.join(str(i) for i in ids)))
                raise QgsProcessingException(
                    self.tr(
                        'The line order field "{}" has duplicate values. Each processed line must have a unique order. Duplicates: {}',
                        'O campo de ordem das linhas "{}" possui valores duplicados. Cada linha processada deve ter uma ordem única. Duplicidades: {}'
                    ).format(order_field, '; '.join(details))
                )

        if first_field:
            null_ids = []
            non_integer = []

            for feat in line_features:
                value = feat[first_field]
                if value is None or value == QVariant() or str(value).upper() == 'NULL':
                    null_ids.append(feat.id())
                    continue

                try:
                    numeric = float(value)
                    if not numeric.is_integer():
                        non_integer.append(feat.id())
                except (TypeError, ValueError):
                    non_integer.append(feat.id())

            if null_ids:
                raise QgsProcessingException(
                    self.tr(
                        'The first-number field "{}" has NULL values. Feature IDs: {}',
                        'O campo do primeiro número "{}" possui valores NULL. IDs das feições: {}'
                    ).format(first_field, self._format_ids(null_ids))
                )

            if non_integer:
                raise QgsProcessingException(
                    self.tr(
                        'The first-number field "{}" must contain integer values. Invalid feature IDs: {}',
                        'O campo do primeiro número "{}" deve conter valores inteiros. IDs inválidos: {}'
                    ).format(first_field, self._format_ids(non_integer))
                )

    def processAlgorithm(self, parameters, context, feedback):

        polygons = self.parameterAsVectorLayer(parameters, self.POLYGONS, context)
        if polygons is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.POLYGONS))

        lines = self.parameterAsVectorLayer(parameters, self.LINES, context)
        if lines is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.LINES))

        numbering_field = self._field_name(parameters, self.FIELD, context)
        if not numbering_field:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.FIELD))

        numbering_index = polygons.fields().indexFromName(numbering_field)
        if numbering_index < 0:
            raise QgsProcessingException(
                self.tr('Numbering field not found.', 'Campo de numeração não encontrado.')
            )

        order_field = self._field_name(parameters, self.ORDER_FIELD, context)
        first_field = self._field_name(parameters, self.FIRST_FIELD, context)

        selected_lines = self.parameterAsBool(parameters, self.SELECTED_LINES, context)
        initial = self.parameterAsInt(parameters, self.INITIAL, context)
        restart = self.parameterAsBool(parameters, self.RESTART, context)
        save = self.parameterAsBool(parameters, self.SAVE, context)

        # Cache line features because they are used in validation and processing.
        if selected_lines:
            line_features = list(lines.getSelectedFeatures())
            if not line_features:
                raise QgsProcessingException(
                    self.tr(
                        'The option "Use only selected lines" is enabled, but no line is selected.',
                        'A opção "Usar apenas linhas selecionadas" está ativada, mas nenhuma linha está selecionada.'
                    )
                )
        else:
            line_features = list(lines.getFeatures())

        if not line_features:
            raise QgsProcessingException(
                self.tr('The line layer has no features.', 'A camada de linhas não possui feições.')
            )

        if polygons.featureCount() == 0:
            raise QgsProcessingException(
                self.tr('The polygon layer has no features.', 'A camada de polígonos não possui feições.')
            )

        # ---------------------------------------------------------------
        # 1. VALIDATION
        # ---------------------------------------------------------------
        feedback.pushInfo(self.tr('Validating geometries...', 'Validando geometrias...'))

        polygon_errors = self.validate_geometries(polygons)
        line_errors = self.validate_geometries(lines, line_features)
        self._raise_geometry_errors(polygon_errors, line_errors)

        feedback.pushInfo(self.tr('Validating line attributes...', 'Validando atributos das linhas...'))
        self._validate_line_attributes(line_features, order_field, first_field)

        # Sort lines using selected order field, or FID as fallback.
        if order_field:
            line_features.sort(key=lambda feat: (feat[order_field], feat.id()))
            feedback.pushInfo(self.tr(
                'Lines sorted by field: {}',
                'Linhas ordenadas pelo campo: {}'
            ).format(order_field))
        else:
            line_features.sort(key=lambda feat: feat.id())
            feedback.pushInfo(self.tr(
                'No line order field selected. Feature ID will be used.',
                'Nenhum campo de ordem foi selecionado. Será utilizado o ID da feição.'
            ))

        if first_field:
            feedback.pushInfo(self.tr(
                'Each line will start at the value stored in field: {}',
                'Cada linha iniciará no valor armazenado no campo: {}'
            ).format(first_field))
        elif restart:
            feedback.pushInfo(self.tr(
                'Numbering will restart at {} for each line.',
                'A numeração reiniciará em {} para cada linha.'
            ).format(initial))
        else:
            feedback.pushInfo(self.tr(
                'Numbering will start at {} and continue between lines.',
                'A numeração iniciará em {} e continuará entre as linhas.'
            ).format(initial))

        # ---------------------------------------------------------------
        # 2. SPATIAL INDEX AND CRS PREPARATION
        # ---------------------------------------------------------------
        feedback.pushInfo(self.tr('Building spatial index...', 'Construindo índice espacial...'))
        polygon_features = {feat.id(): feat for feat in polygons.getFeatures()}
        
        spatial_index = QgsSpatialIndex()

        for feat in polygon_features.values():
            spatial_index.addFeature(feat)

        transform_line_to_polygon = None
        if lines.crs() != polygons.crs():
            transform_line_to_polygon = QgsCoordinateTransform(
                lines.crs(), polygons.crs(), QgsProject.instance()
            )

        # Dictionary with final attribute updates: polygon FID -> number
        updates = {}
        already_numbered = set()
        global_counter = initial
        processed_lines = 0
        lines_without_polygons = 0

        total_lines = len(line_features)

        # ---------------------------------------------------------------
        # 3. NUMBERING
        # ---------------------------------------------------------------
        feedback.pushInfo(self.tr('Numbering polygons...', 'Numerando polígonos...'))

        for line_pos, line_feat in enumerate(line_features):

            if feedback.isCanceled():
                break

            line_geom = QgsGeometry(line_feat.geometry())
            if transform_line_to_polygon is not None:
                line_geom.transform(transform_line_to_polygon)

            candidate_ids = spatial_index.intersects(line_geom.boundingBox())
            intercepted = []

            for polygon_id in candidate_ids:
                # A polygon intercepted by more than one line belongs to the
                # first line according to the line processing order.
                if polygon_id in already_numbered:
                    continue

                polygon_feat = polygon_features.get(polygon_id)
                if polygon_feat is None:
                    continue

                polygon_geom = polygon_feat.geometry()

                if not polygon_geom.intersects(line_geom):
                    continue

                try:
                    intersection = polygon_geom.intersection(line_geom)
                except Exception as e:
                    raise QgsProcessingException(
                        self.tr(
                            'Error intersecting polygon ID {} with line ID {}: {}',
                            'Erro ao intersectar o polígono ID {} com a linha ID {}: {}'
                        ).format(polygon_id, line_feat.id(), str(e))
                    )

                if intersection.isNull() or intersection.isEmpty():
                    continue

                # The centroid of the crossing geometry provides a representative
                # point whose position is measured along the line direction.
                crossing_point = intersection.centroid()
                distance = line_geom.lineLocatePoint(crossing_point)

                if distance < 0:
                    raise QgsProcessingException(
                        self.tr(
                            'Could not locate the intersection of polygon ID {} along line ID {}.',
                            'Não foi possível localizar a interseção do polígono ID {} ao longo da linha ID {}.'
                        ).format(polygon_id, line_feat.id())
                    )

                intercepted.append((distance, polygon_id))

            intercepted.sort(key=lambda item: (item[0], item[1]))

            if not intercepted:
                lines_without_polygons += 1
                feedback.pushInfo(self.tr(
                    'Line ID {} did not intercept any available polygon.',
                    'A linha ID {} não interceptou nenhum polígono disponível.'
                ).format(line_feat.id()))
                feedback.setProgress(int(((line_pos + 1) / total_lines) * 90))
                continue

            if first_field:
                line_counter = int(float(line_feat[first_field]))
            elif restart:
                line_counter = initial
            else:
                line_counter = global_counter

            for offset, (distance, polygon_id) in enumerate(intercepted):
                updates[polygon_id] = line_counter + offset
                already_numbered.add(polygon_id)

            if not first_field and not restart:
                global_counter += len(intercepted)

            processed_lines += 1
            feedback.pushInfo(self.tr(
                'Line ID {}: {} polygon(s) numbered from {} to {}.',
                'Linha ID {}: {} polígono(s) numerado(s) de {} a {}.'
            ).format(
                line_feat.id(),
                len(intercepted),
                line_counter,
                line_counter + len(intercepted) - 1
            ))

            feedback.setProgress(int(((line_pos + 1) / total_lines) * 90))

        if feedback.isCanceled():
            return {}

        if not updates:
            raise QgsProcessingException(
                self.tr(
                    'No polygon was intercepted by the processed lines.',
                    'Nenhum polígono foi interceptado pelas linhas processadas.'
                )
            )

        # ---------------------------------------------------------------
        # 4. WRITE RESULTS
        # ---------------------------------------------------------------
        feedback.pushInfo(self.tr('Writing values...', 'Gravando valores...'))

        if not polygons.isEditable():
            if not polygons.startEditing():
                raise QgsProcessingException(
                    self.tr(
                        'Could not start editing the polygon layer.',
                        'Não foi possível iniciar a edição da camada de polígonos.'
                    )
                )

        total_updates = len(updates)
        for pos, (polygon_id, value) in enumerate(updates.items()):
            if feedback.isCanceled():
                break

            if not polygons.changeAttributeValue(polygon_id, numbering_index, value):
                raise QgsProcessingException(
                    self.tr(
                        'Could not write the value for polygon ID {}.',
                        'Não foi possível gravar o valor no polígono ID {}.'
                    ).format(polygon_id)
                )

            feedback.setProgress(90 + int(((pos + 1) / total_updates) * 10))

        if feedback.isCanceled():
            return {}

        if save:
            if not polygons.commitChanges():
                errors = '; '.join(polygons.commitErrors())
                raise QgsProcessingException(
                    self.tr(
                        'Could not save edits. {}',
                        'Não foi possível salvar as edições. {}'
                    ).format(errors)
                )

        polygons.triggerRepaint()

        feedback.pushInfo('----------------------------------------')
        feedback.pushInfo(self.tr('Operation completed successfully!', 'Operação finalizada com sucesso!'))
        feedback.pushInfo(self.tr(
            '{} line(s) processed.',
            '{} linha(s) processada(s).'
        ).format(processed_lines))
        feedback.pushInfo(self.tr(
            '{} polygon(s) numbered.',
            '{} polígono(s) numerado(s).'
        ).format(len(updates)))

        if lines_without_polygons:
            feedback.pushInfo(self.tr(
                '{} line(s) did not intercept available polygons.',
                '{} linha(s) não interceptou/interceptaram polígonos disponíveis.'
            ).format(lines_without_polygons))

        untouched = polygons.featureCount() - len(updates)
        if untouched > 0:
            feedback.pushInfo(self.tr(
                '{} polygon(s) were not numbered.',
                '{} polígono(s) não foi/foram numerado(s).'
            ).format(untouched))

        feedback.pushInfo(self.tr(
            'Leandro Franca - Cartographic Engineer',
            'Leandro França - Eng Cart'
        ))

        return {}
