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
    QgsProcessing,
    QgsProcessingAlgorithm,
    QgsProcessingException,
    QgsProcessingParameterBoolean,
    QgsProcessingParameterFeatureSink,
    QgsProcessingParameterVectorLayer,
    QgsFeatureRequest,
    QgsProject,
    QgsVectorLayer,
    QgsWkbTypes
)

from qgis.PyQt.QtCore import QMetaType
from qgis.PyQt.QtGui import QIcon

from lftools.geocapt.imgs import Imgs
from lftools.translations.translate import translate

import os
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
                [QgsProcessing.TypeVectorAnyGeometry]
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
                QgsProcessing.TypeVector
            )
        )

    def _sink_fields(self, input_fields):
        fields = QgsFields()
        for field in input_fields:
            fields.append(field)

        # Campos auxiliares
        if fields.indexOf('lf_orig_id') == -1:
            fields.append(QgsField('lf_orig_id', QMetaType.Type.LongLong))
        else:
            fields.append(QgsField('lf_orig_id_2', QMetaType.Type.LongLong))

        if fields.indexOf('lf_reason') == -1:
            fields.append(QgsField('lf_reason', QMetaType.QString, len=40))
        else:
            fields.append(QgsField('lf_reason_2', QMetaType.QString, len=40))

        return fields

    def _append_removed_feature_to_sink(self, feat, sink, sink_fields, reason):
        new_feat = QgsFeature(sink_fields)
        new_feat.setGeometry(QgsGeometry())  # sem geometria

        attrs = feat.attributes()[:]

        if sink_fields.indexOf('lf_orig_id') != -1:
            attrs += [feat.id(), reason]
        else:
            attrs += [feat.id(), reason]

        new_feat.setAttributes(attrs)
        sink.addFeature(new_feat)

    def _copy_target_features_to_temp_layer(self, layer, selected_only, context, feedback):
        """
        Cria uma camada temporária apenas com as feições alvo.
        Adiciona um campo auxiliar __lf_id__ = $id para permitir
        mapear geometrias processadas de volta à camada original.
        """
        if selected_only:
            temp = processing.run(
                "native:saveselectedfeatures",
                {
                    'INPUT': layer,
                    'OUTPUT': 'TEMPORARY_OUTPUT'
                },
                context=context,
                feedback=feedback
            )['OUTPUT']
        else:
            temp = processing.run(
                "native:savefeatures",
                {
                    'INPUT': layer,
                    'OUTPUT': 'TEMPORARY_OUTPUT'
                },
                context=context,
                feedback=feedback
            )['OUTPUT']

        temp = processing.run(
            "native:fieldcalculator",
            {
                'INPUT': temp,
                'FIELD_NAME': '__lf_id__',
                'FIELD_TYPE': 1,  # inteiro
                'FIELD_LENGTH': 20,
                'FIELD_PRECISION': 0,
                'FORMULA': '$id',
                'OUTPUT': 'TEMPORARY_OUTPUT'
            },
            context=context,
            feedback=feedback
        )['OUTPUT']

        return temp

    def processAlgorithm(self, parameters, context, feedback):

        layer = self.parameterAsVectorLayer(parameters, self.INPUT, context)
        if layer is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.INPUT))

        selected_only = self.parameterAsBool(parameters, self.SELECTED, context)
        save_edits = self.parameterAsBool(parameters, self.SAVE, context)

        # Criar tabela de saída sem geometria
        sink_fields = self._sink_fields(layer.fields())
        sink, sink_id = self.parameterAsSink(
            parameters,
            self.OUTPUT,
            context,
            sink_fields,
            QgsWkbTypes.NoGeometry,
            layer.sourceCrs()
        )
        if sink is None:
            raise QgsProcessingException(self.tr('Could not create output table.', 'Não foi possível criar a tabela de saída.'))

        # Definir conjunto de feições alvo
        if selected_only:
            target_features = list(layer.getSelectedFeatures())
            target_ids = {feat.id() for feat in target_features}
            total_target = len(target_features)
        else:
            target_features = list(layer.getFeatures())
            target_ids = {feat.id() for feat in target_features}
            total_target = len(target_features)

        if total_target == 0:
            feedback.pushInfo(self.tr('No features to process.', 'Nenhuma feição para processar.'))
            return {self.OUTPUT: sink_id}

        feedback.pushInfo(self.tr(
            'Starting light geometry cleanup...',
            'Iniciando limpeza geométrica leve...'
        ))

        # Entrar em edição
        if not layer.isEditable():
            layer.startEditing()

        # ------------------------------------------------------------------
        # 1) Identificar e remover geometrias nulas ou vazias
        # ------------------------------------------------------------------
        feedback.pushInfo(self.tr(
            'Checking for null or empty geometries...',
            'Verificando geometrias nulas ou vazias...'
        ))

        ids_to_delete = []
        remaining_ids = set(target_ids)

        total = 100.0 / total_target if total_target else 0

        for current, feat in enumerate(target_features):
            if feedback.isCanceled():
                break

            geom = feat.geometry()
            reason = None

            if geom is None:
                reason = self.tr('null geometry', 'geometria nula')
            elif geom.isNull():
                reason = self.tr('null geometry', 'geometria nula')
            elif geom.isEmpty():
                reason = self.tr('empty geometry', 'geometria vazia')

            if reason is not None:
                self._append_removed_feature_to_sink(feat, sink, sink_fields, reason)
                ids_to_delete.append(feat.id())
                if feat.id() in remaining_ids:
                    remaining_ids.remove(feat.id())

                feedback.pushInfo(
                    self.tr(
                        'Deleted feature ID {} ({})'.format(feat.id(), reason),
                        'Feição ID {} apagada ({})'.format(feat.id(), reason)
                    )
                )

            feedback.setProgress(int(current * total))

        if ids_to_delete:
            ok = layer.deleteFeatures(ids_to_delete)
            if not ok:
                raise QgsProcessingException(
                    self.tr(
                        'Could not delete null/empty geometry features.',
                        'Não foi possível apagar as feições com geometria nula/vazia.'
                    )
                )

        feedback.pushInfo(
            self.tr(
                '{} feature(s) removed due to null or empty geometry.'.format(len(ids_to_delete)),
                '{} feição(ões) removida(s) por geometria nula ou vazia.'.format(len(ids_to_delete))
            )
        )

        # ------------------------------------------------------------------
        # 2) Remover vértices duplicados para linhas e polígonos
        # ------------------------------------------------------------------
        geom_type = layer.geometryType()
        if geom_type in (QgsWkbTypes.LineGeometry, QgsWkbTypes.PolygonGeometry) and remaining_ids:

            feedback.pushInfo(self.tr(
                'Removing duplicate vertices...',
                'Removendo vértices duplicados...'
            ))

            # Atualizar seleção temporariamente se necessário
            old_selected_ids = layer.selectedFeatureIds()

            if selected_only:
                layer.selectByIds(list(remaining_ids))

            temp_layer = self._copy_target_features_to_temp_layer(
                layer,
                selected_only,
                context,
                feedback
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
            for feat in cleaned.getFeatures():
                cleaned_dict[int(feat['__lf_id__'])] = feat.geometry()

            changed_count = 0
            ids_sorted = sorted(list(remaining_ids))
            total2 = 100.0 / len(ids_sorted) if ids_sorted else 0

            req = QgsFeatureRequest().setFilterFids(ids_sorted)
            for current, feat in enumerate(layer.getFeatures(req)):
                if feedback.isCanceled():
                    break

                fid = feat.id()
                old_geom = feat.geometry()
                new_geom = cleaned_dict.get(fid)

                if new_geom is None:
                    feedback.setProgress(int(current * total2))
                    continue

                # compara WKB para detectar alteração real
                old_wkb = old_geom.asWkb() if old_geom and not old_geom.isNull() else None
                new_wkb = new_geom.asWkb() if new_geom and not new_geom.isNull() else None

                if old_wkb != new_wkb:
                    ok = layer.changeGeometry(fid, new_geom)
                    if ok:
                        changed_count += 1
                        feedback.pushInfo(
                            self.tr(
                                'Duplicate vertices removed from feature ID {}'.format(fid),
                                'Vértices duplicados removidos da feição ID {}'.format(fid)
                            )
                        )

                feedback.setProgress(int(current * total2))

            # Restaurar seleção original
            if selected_only:
                layer.selectByIds(old_selected_ids)

            feedback.pushInfo(
                self.tr(
                    '{} feature(s) had duplicate vertices removed.'.format(changed_count),
                    '{} feição(ões) tiveram vértices duplicados removidos.'.format(changed_count)
                )
            )

        else:
            feedback.pushInfo(self.tr(
                'Duplicate vertex cleanup skipped (only applies to line and polygon layers).',
                'A remoção de vértices duplicados foi ignorada (aplica-se apenas a linhas e polígonos).'
            ))

        # ------------------------------------------------------------------
        # 3) Salvar edições
        # ------------------------------------------------------------------
        if save_edits:
            if not layer.commitChanges():
                raise QgsProcessingException(
                    self.tr(
                        'Could not save layer edits.',
                        'Não foi possível salvar as edições da camada.'
                    )
                )
        else:
            feedback.pushInfo(self.tr(
                'Edits were kept in edit mode and not committed.',
                'As edições foram mantidas em modo de edição e não foram salvas.'
            ))

        feedback.pushInfo(self.tr(
            'Operation completed successfully!',
            'Operação finalizada com sucesso!'
        ))
        feedback.pushInfo(self.tr(
            'Leandro Franca - Cartographic Engineer',
            'Leandro França - Eng Cart'
        ))

        return {self.OUTPUT: sink_id}