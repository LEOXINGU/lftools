# -*- coding: utf-8 -*-

"""
Vector_LightGeometryCleanup.py
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
__date__ = '2026-04-13'
__copyright__ = '(C) 2026, Leandro França'

from qgis.core import (
    QgsApplication,
    QgsFeature,
    QgsField,
    QgsFields,
    QgsGeometry,
    Qgis,
    QgsProcessingAlgorithm,
    QgsProcessingException,
    QgsProcessingParameterBoolean,
    QgsProcessingParameterFeatureSink,
    QgsProcessingParameterVectorLayer,
    QgsFeatureRequest,
    QgsMemoryProviderUtils,
    QgsWkbTypes)

from qgis.PyQt.QtCore import QMetaType
from qgis.PyQt.QtGui import QIcon

from lftools.geocapt.imgs import Imgs
from lftools.translations.translate import translate

import os
import json
import processing


class LightGeometryCleanup(QgsProcessingAlgorithm):

    LOC = QgsApplication.locale()[:2]

    def tr(self, *string):
        return translate(string, self.LOC)

    def createInstance(self):
        return LightGeometryCleanup()

    def name(self):
        return 'lightgeometrycleanup'

    def displayName(self):
        return self.tr('Light Geometry Cleanup', 'Limpeza Geométrica Leve')

    def group(self):
        return self.tr('Vector', 'Vetor')

    def groupId(self):
        return 'vector'

    def tags(self):
        return 'cleanup,geometry,null,empty,duplicate,vertices,line,polygon,table,light,sanitize,ghost,fantasma,limpeza,geometria,nula,vazia,duplicados,vértices,linha,polígono,tabela,leve,saneamento'.split(',')

    def icon(self):
        return QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images/vetor.png'))

    txt_en = '''
This tool performs a light geometric cleanup directly on the input layer.

It:
- removes features with null or empty geometries directly from the original layer;
- records the deleted feature IDs in the processing log;
- exports the attributes of removed features to a no-geometry table;
- removes duplicate vertices for line and polygon features.

Note: Invalid geometries are not fixed or deleted by this tool.
'''

    txt_pt = '''
Esta ferramenta executa uma leve limpeza geométrica diretamente na camada de entrada.

Ela:
- remove da camada original as feições com geometria nula ou vazia;
- registra no log os IDs das feições apagadas;
- exporta os atributos das feições removidas para uma tabela sem geometria;
- remove vértices duplicados de feições lineares e poligonais.

Obs.: Geometrias inválidas não são corrigidas nem removidas por esta ferramenta.
'''
    
    figure = 'images/tutorial/vect_geometry_cleanup.jpg'

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
    SELECTED = 'SELECTED'
    SAVE = 'SAVE'
    OUTPUT = 'OUTPUT'

    def initAlgorithm(self, config=None):

        self.addParameter(
            QgsProcessingParameterVectorLayer(
                self.INPUT,
                self.tr('Input Layer', 'Camada de entrada'),
                [Qgis.ProcessingSourceType.TypeVectorAnyGeometry]
            )
        )

        self.addParameter(
            QgsProcessingParameterBoolean(
                self.SELECTED,
                self.tr('Only selected', 'Apenas feições selecionadas'),
                defaultValue=False
            )
        )

        self.addParameter(
            QgsProcessingParameterBoolean(
                self.SAVE,
                self.tr('Save Editions', 'Salvar Edições'),
                defaultValue=True
            )
        )

        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT,
                self.tr('Output table of removed features', 'Tabela de saída das feições removidas'),
                Qgis.ProcessingSourceType.TypeVector
            )
        )

    def _unique_field_name(self, fields, base_name):
        """Retorna um nome de campo que ainda não exista."""
        if fields.indexOf(base_name) == -1:
            return base_name

        i = 2
        while fields.indexOf(f'{base_name}_{i}') != -1:
            i += 1
        return f'{base_name}_{i}'

    def _sink_fields(self, input_fields):
        """
        Mantém todos os atributos originais e acrescenta campos de auditoria.
        lf_attributes guarda também uma cópia JSON dos atributos originais,
        facilitando a recuperação mesmo que a estrutura da tabela mude.
        """
        fields = QgsFields()
        for field in input_fields:
            fields.append(field)

        self._fld_orig_id = self._unique_field_name(fields, 'lf_orig_id')
        fields.append(QgsField(self._fld_orig_id, QMetaType.Type.LongLong))

        self._fld_reason = self._unique_field_name(fields, 'lf_reason')
        fields.append(QgsField(self._fld_reason, QMetaType.Type.QString, len=80))

        self._fld_attributes = self._unique_field_name(fields, 'lf_attributes')
        fields.append(QgsField(self._fld_attributes, QMetaType.Type.QString))

        return fields

    def _attributes_as_json(self, feat, input_fields):
        """Serializa os atributos originais em JSON legível e recuperável."""
        data = {}
        attrs = feat.attributes()

        for i, field in enumerate(input_fields):
            value = attrs[i] if i < len(attrs) else None

            # Datas, horários e outros QVariant/PyQt são convertidos
            # para representação textual caso não sejam JSON nativos.
            try:
                json.dumps(value)
                data[field.name()] = value
            except (TypeError, ValueError):
                data[field.name()] = str(value) if value is not None else None

        return json.dumps(data, ensure_ascii=False, default=str)

    def _append_removed_feature_to_sink(self, feat, sink, sink_fields,
                                        input_fields, reason):
        """Registra uma feição realmente excluída sem perder seus atributos."""
        new_feat = QgsFeature(sink_fields)
        new_feat.setGeometry(QgsGeometry())

        attrs = feat.attributes()[:]
        attrs += [
            int(feat.id()),
            reason,
            self._attributes_as_json(feat, input_fields)
        ]

        new_feat.setAttributes(attrs)
        sink.addFeature(new_feat)

    def _copy_target_features_to_temp_layer(self, layer, feature_ids):
        """
        Cria uma camada temporária em memória preservando explicitamente
        o FID ORIGINAL em __lf_id__.

        Importante: não usa $id depois de native:savefeatures, pois o FID
        de uma camada temporária não deve ser usado como chave para alterar
        a camada original.
        """
        fields = QgsFields()
        fields.append(QgsField('__lf_id__', QMetaType.Type.LongLong))

        temp = QgsMemoryProviderUtils.createMemoryLayer(
            'lf_light_geometry_cleanup',
            fields,
            layer.wkbType(),
            layer.crs()
        )

        provider = temp.dataProvider()

        req = QgsFeatureRequest().setFilterFids(list(feature_ids))
        features = []

        for feat in layer.getFeatures(req):
            geom = feat.geometry()

            # Somente geometrias utilizáveis entram na rotina de
            # remoção de vértices duplicados.
            if geom is None or geom.isNull() or geom.isEmpty():
                continue

            new_feat = QgsFeature(fields)
            new_feat.setGeometry(QgsGeometry(geom))
            new_feat.setAttributes([int(feat.id())])
            features.append(new_feat)

        if features:
            provider.addFeatures(features)

        temp.updateExtents()
        return temp

    def processAlgorithm(self, parameters, context, feedback):

        layer = self.parameterAsVectorLayer(parameters, self.INPUT, context)
        if layer is None:
            raise QgsProcessingException(
                self.invalidSourceError(parameters, self.INPUT)
            )

        selected_only = self.parameterAsBool(
            parameters, self.SELECTED, context
        )
        save_edits = self.parameterAsBool(
            parameters, self.SAVE, context
        )

        input_fields = layer.fields()

        # --------------------------------------------------------------
        # Tabela de auditoria das feições efetivamente removidas
        # --------------------------------------------------------------
        sink_fields = self._sink_fields(input_fields)
        sink, sink_id = self.parameterAsSink(
            parameters,
            self.OUTPUT,
            context,
            sink_fields,
            Qgis.WkbType.NoGeometry,
            layer.sourceCrs()
        )

        if sink is None:
            raise QgsProcessingException(
                self.tr(
                    'Could not create output table.',
                    'Não foi possível criar a tabela de saída.'
                )
            )

        # --------------------------------------------------------------
        # Definir universo de processamento
        # --------------------------------------------------------------
        if selected_only:
            target_features = list(layer.getSelectedFeatures())
        else:
            target_features = list(layer.getFeatures())

        target_ids = {feat.id() for feat in target_features}
        total_target = len(target_features)

        if total_target == 0:
            feedback.pushInfo(
                self.tr(
                    'No features to process.',
                    'Nenhuma feição para processar.'
                )
            )
            return {self.OUTPUT: sink_id}

        feedback.pushInfo(
            self.tr(
                'Starting light geometry cleanup...',
                'Iniciando limpeza geométrica leve...'
            )
        )

        # --------------------------------------------------------------
        # FASE 1 - DIAGNÓSTICO
        # Nenhuma alteração na camada original é feita nesta fase.
        # --------------------------------------------------------------
        feedback.pushInfo(
            self.tr(
                'Checking for null or empty geometries...',
                'Verificando geometrias nulas ou vazias...'
            )
        )

        features_to_delete = []
        remaining_ids = set(target_ids)

        total = 100.0 / total_target if total_target else 0

        for current, feat in enumerate(target_features):

            if feedback.isCanceled():
                feedback.pushInfo(
                    self.tr(
                        'Operation canceled. No changes were applied.',
                        'Operação cancelada. Nenhuma alteração foi aplicada.'
                    )
                )
                return {self.OUTPUT: sink_id}

            geom = feat.geometry()
            reason = None

            if geom is None or geom.isNull():
                reason = self.tr(
                    'null geometry',
                    'geometria nula'
                )
            elif geom.isEmpty():
                reason = self.tr(
                    'empty geometry',
                    'geometria vazia'
                )

            if reason is not None:
                features_to_delete.append((feat, reason))
                remaining_ids.discard(feat.id())

            feedback.setProgress(int((current + 1) * total))

        # --------------------------------------------------------------
        # FASE 2 - Preparar alterações geométricas SEM aplicá-las ainda
        # --------------------------------------------------------------
        geometry_changes = {}
        skipped_invalid = 0
        skipped_unsafe = 0

        geom_type = layer.geometryType()

        if (
            geom_type in (
                Qgis.GeometryType.Line,
                Qgis.GeometryType.Polygon
            )
            and remaining_ids
        ):
            feedback.pushInfo(
                self.tr(
                    'Checking duplicate vertices...',
                    'Verificando vértices duplicados...'
                )
            )

            # Preserva explicitamente o FID original em __lf_id__.
            temp_layer = self._copy_target_features_to_temp_layer(
                layer,
                remaining_ids
            )

            cleaned = processing.run(
                "native:removeduplicatevertices",
                {
                    'INPUT': temp_layer,
                    'TOLERANCE': 0.0,
                    'USE_Z_VALUE': False,
                    'OUTPUT': 'TEMPORARY_OUTPUT'
                },
                context=context,
                feedback=feedback
            )['OUTPUT']

            cleaned_dict = {}
            for cleaned_feat in cleaned.getFeatures():
                try:
                    original_fid = int(cleaned_feat['__lf_id__'])
                except (TypeError, ValueError):
                    continue

                cleaned_dict[original_fid] = cleaned_feat.geometry()

            ids_sorted = sorted(remaining_ids)
            req = QgsFeatureRequest().setFilterFids(ids_sorted)
            feats_remaining = list(layer.getFeatures(req))
            total2 = 100.0 / len(feats_remaining) if feats_remaining else 0

            for current, feat in enumerate(feats_remaining):

                if feedback.isCanceled():
                    feedback.pushInfo(
                        self.tr(
                            'Operation canceled. No changes were applied.',
                            'Operação cancelada. Nenhuma alteração foi aplicada.'
                        )
                    )
                    return {self.OUTPUT: sink_id}

                fid = feat.id()
                old_geom = feat.geometry()
                new_geom = cleaned_dict.get(fid)

                if (
                    old_geom is None
                    or old_geom.isNull()
                    or old_geom.isEmpty()
                    or new_geom is None
                ):
                    feedback.setProgress(int((current + 1) * total2))
                    continue

                # A ferramenta declara que não corrige geometrias inválidas.
                # Por segurança, elas também não são alteradas nesta etapa.
                if not old_geom.isGeosValid():
                    skipped_invalid += 1
                    feedback.pushInfo(
                        self.tr(
                            'Feature ID {} has invalid geometry and was not modified.'
                            .format(fid),
                            'A feição ID {} possui geometria inválida e não foi modificada.'
                            .format(fid)
                        )
                    )
                    feedback.setProgress(int((current + 1) * total2))
                    continue

                # REGRA DE SEGURANÇA:
                # jamais substituir geometria válida por resultado nulo/vazio.
                if new_geom.isNull() or new_geom.isEmpty():
                    skipped_unsafe += 1
                    feedback.pushWarning(
                        self.tr(
                            'Cleanup result for feature ID {} was null/empty. '
                            'Original geometry was preserved.'.format(fid),
                            'O resultado da limpeza da feição ID {} ficou nulo/vazio. '
                            'A geometria original foi preservada.'.format(fid)
                        )
                    )
                    feedback.setProgress(int((current + 1) * total2))
                    continue

                # A família geométrica deve continuar a mesma.
                if new_geom.type() != old_geom.type():
                    skipped_unsafe += 1
                    feedback.pushWarning(
                        self.tr(
                            'Cleanup result for feature ID {} changed geometry type. '
                            'Original geometry was preserved.'.format(fid),
                            'O resultado da limpeza da feição ID {} alterou o tipo '
                            'de geometria. A geometria original foi preservada.'.format(fid)
                        )
                    )
                    feedback.setProgress(int((current + 1) * total2))
                    continue

                # Para geometria originalmente válida, não aceitar um
                # resultado que passe a ser inválido.
                if not new_geom.isGeosValid():
                    skipped_unsafe += 1
                    feedback.pushWarning(
                        self.tr(
                            'Cleanup result for feature ID {} became invalid. '
                            'Original geometry was preserved.'.format(fid),
                            'O resultado da limpeza da feição ID {} tornou-se inválido. '
                            'A geometria original foi preservada.'.format(fid)
                        )
                    )
                    feedback.setProgress(int((current + 1) * total2))
                    continue

                old_wkb = old_geom.asWkb()
                new_wkb = new_geom.asWkb()

                if old_wkb != new_wkb:
                    geometry_changes[fid] = QgsGeometry(new_geom)

                feedback.setProgress(int((current + 1) * total2))

        else:
            feedback.pushInfo(
                self.tr(
                    'Duplicate vertex cleanup skipped '
                    '(only applies to line and polygon layers).',
                    'A remoção de vértices duplicados foi ignorada '
                    '(aplica-se apenas a linhas e polígonos).'
                )
            )

        # --------------------------------------------------------------
        # FASE 3 - APLICAR ALTERAÇÕES
        # Só chegamos aqui se toda a análise terminou sem cancelamento.
        # --------------------------------------------------------------
        layer_was_editable = layer.isEditable()
        started_editing_here = False

        if not layer_was_editable:
            if not layer.startEditing():
                raise QgsProcessingException(
                    self.tr(
                        'Could not start layer editing.',
                        'Não foi possível iniciar a edição da camada.'
                    )
                )
            started_editing_here = True

        # 3A - apagar SOMENTE feições previamente diagnosticadas
        ids_to_delete = [feat.id() for feat, reason in features_to_delete]

        if ids_to_delete:
            if not layer.deleteFeatures(ids_to_delete):
                if started_editing_here:
                    layer.rollBack()
                raise QgsProcessingException(
                    self.tr(
                        'Could not delete null/empty geometry features.',
                        'Não foi possível apagar as feições com geometria nula/vazia.'
                    )
                )

        # Só registra na tabela depois que a exclusão foi aceita
        for feat, reason in features_to_delete:
            self._append_removed_feature_to_sink(
                feat,
                sink,
                sink_fields,
                input_fields,
                reason
            )

            feedback.pushInfo(
                self.tr(
                    'Deleted feature ID {} ({})'.format(feat.id(), reason),
                    'Feição ID {} apagada ({})'.format(feat.id(), reason)
                )
            )

        # 3B - alterações geométricas seguras
        changed_count = 0

        for fid, new_geom in geometry_changes.items():
            if not layer.changeGeometry(fid, new_geom):
                if started_editing_here:
                    layer.rollBack()
                raise QgsProcessingException(
                    self.tr(
                        'Could not update geometry of feature ID {}.'
                        .format(fid),
                        'Não foi possível atualizar a geometria da feição ID {}.'
                        .format(fid)
                    )
                )

            changed_count += 1
            feedback.pushInfo(
                self.tr(
                    'Duplicate vertices removed from feature ID {}'
                    .format(fid),
                    'Vértices duplicados removidos da feição ID {}'
                    .format(fid)
                )
            )

        feedback.pushInfo(
            self.tr(
                '{} feature(s) removed due to null or empty geometry.'
                .format(len(ids_to_delete)),
                '{} feição(ões) removida(s) por geometria nula ou vazia.'
                .format(len(ids_to_delete))
            )
        )

        feedback.pushInfo(
            self.tr(
                '{} feature(s) had duplicate vertices removed.'
                .format(changed_count),
                '{} feição(ões) tiveram vértices duplicados removidos.'
                .format(changed_count)
            )
        )

        if skipped_invalid:
            feedback.pushInfo(
                self.tr(
                    '{} invalid feature(s) were preserved without modification.'
                    .format(skipped_invalid),
                    '{} feição(ões) inválida(s) foram preservadas sem modificação.'
                    .format(skipped_invalid)
                )
            )

        if skipped_unsafe:
            feedback.pushWarning(
                self.tr(
                    '{} potentially unsafe geometry change(s) were blocked.'
                    .format(skipped_unsafe),
                    '{} alteração(ões) geométrica(s) potencialmente insegura(s) '
                    'foram bloqueadas.'.format(skipped_unsafe)
                )
            )

        # --------------------------------------------------------------
        # FASE 4 - SALVAR
        # Nunca faz commit automático de uma sessão de edição que já
        # estava aberta antes da ferramenta, pois isso poderia salvar
        # alterações não relacionadas feitas pelo usuário.
        # --------------------------------------------------------------
        if save_edits and started_editing_here:
            if not layer.commitChanges():
                layer.rollBack()
                raise QgsProcessingException(
                    self.tr(
                        'Could not save layer edits.',
                        'Não foi possível salvar as edições da camada.'
                    )
                )

        elif save_edits and layer_was_editable:
            feedback.pushWarning(
                self.tr(
                    'The layer was already in edit mode. Cleanup changes were '
                    'left in the current edit session and were not committed '
                    'automatically, in order to avoid saving unrelated edits.',
                    'A camada já estava em modo de edição. As alterações da limpeza '
                    'foram mantidas na sessão de edição atual e não foram salvas '
                    'automaticamente, para evitar salvar edições não relacionadas.'
                )
            )

        else:
            feedback.pushInfo(
                self.tr(
                    'Edits were kept in edit mode and not committed.',
                    'As edições foram mantidas em modo de edição e não foram salvas.'
                )
            )

        feedback.pushInfo(
            self.tr(
                'Operation completed successfully!',
                'Operação finalizada com sucesso!'
            )
        )
        feedback.pushInfo(
            self.tr(
                'Leandro Franca - Cartographic Engineer',
                'Leandro França - Eng Cart'
            )
        )

        return {self.OUTPUT: sink_id}