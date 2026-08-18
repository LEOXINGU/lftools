# -*- coding: utf-8 -*-

"""
Cad_ConnectPolygons.py
***************************************************************************
*                                                                         *
*   LFTools - robust polygon connectivity correction                      *
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
    QgsFeature,
    QgsField,
    QgsFields,
    QgsGeometry,
    QgsMemoryProviderUtils,
    QgsProcessingAlgorithm,
    QgsProcessingException,
    QgsProcessingParameterEnum,
    QgsProcessingParameterFeatureSink,
    QgsProcessingParameterFeatureSource,
    QgsProcessingParameterNumber,
    QgsFeatureSink,
    Qgis
)

from lftools.geocapt.imgs import Imgs
from lftools.geocapt.topogeo import meters2degrees
from lftools.translations.translate import translate

import os
import processing


class ConnectPolygons(QgsProcessingAlgorithm):

    LOC = QgsApplication.locale()[:2]

    def tr(self, *string):
        return translate(string, self.LOC)

    def createInstance(self):
        return ConnectPolygons()

    def name(self):
        return 'connectpolygons'

    def displayName(self):
        return self.tr('Connect polygons', 'Conectar polígonos')

    def group(self):
        return self.tr('Cadastre', 'Cadastro')

    def groupId(self):
        return 'cadastro'

    def tags(self):
        return ('GeoOne,connect,polygons,polígonos,conectar,validation,topology,'
                'cadastro,parcela,lote,adjacency,adjacência,gap,snap,vertex,'
                'vértice,quality,qualidade').split(',')

    def icon(self):
        return QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)),
                                  'images/cadastre.png'))

    txt_en = '''This tool corrects connectivity between parcels or other adjacent polygon features by snapping vertices and segments within a specified tolerance.
Snapping internally uses the native QGIS "Snap geometries to layer" algorithm. The main difference is that this tool adds safety and auditing controls specifically designed for cadastral data processing.
Note: This tool does not remove features or correct other topological problems, such as overlaps, small polygons, duplicate geometries, or null geometries. These problems should be handled using specific geometry cleanup and quality control tools.
'''

    txt_pt = '''Esta ferramenta corrige a conectividade entre lotes ou outras feições poligonais adjacentes, aderindo vértices e segmentos dentro de uma tolerância definida.
A aderência utiliza internamente o algoritmo nativo "Aderir geometrias à camada" do QGIS. O diferencial desta ferramenta é acrescentar controles de segurança e auditoria especificamente voltados ao tratamento de dados cadastrais.
Obs.: Esta ferramenta não remove feições nem corrige outros problemas topológicos, como sobreposições, pequenos polígonos, geometrias duplicadas ou geometrias nulas. Esses problemas devem ser tratados por ferramentas específicas de limpeza geométrica e controle de qualidade.
'''
    figure = 'images/tutorial/cadastre_connectFeatures.jpg'

    def shortHelpString(self):
        social_BW = Imgs().social_BW
        footer = '''<div align="center">
                      <img src="''' + os.path.join(os.path.dirname(os.path.dirname(__file__)), self.figure) + '''">
                      </div>
                      <div align="right">
                      <p align="right">
                      <b>''' + self.tr('Author: Leandro Franca', 'Autor: Leandro França') + '''</b>
                      </p>''' + social_BW + '''</div>
                    </div>'''
        return self.tr(self.txt_en, self.txt_pt) + footer

    INPUT = 'INPUT'
    TOLERANCE = 'TOLERANCE'
    BEHAVIOR = 'BEHAVIOR'
    OUTPUT = 'OUTPUT'
    REPORT = 'REPORT'

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterFeatureSource(
            self.INPUT,
            self.tr('Parcels', 'Lotes'),
            [Qgis.ProcessingSourceType.TypeVectorPolygon]
        ))

        self.addParameter(QgsProcessingParameterNumber(
            self.TOLERANCE,
            self.tr('Tolerance for snapping in meters', 'Tolerância para a aderência (metros)'),
            type=QgsProcessingParameterNumber.Type.Double,
            defaultValue=0.01,
            minValue=0.00001
        ))

        self.addParameter(QgsProcessingParameterEnum(
            self.BEHAVIOR,
            self.tr('Snapping behavior', 'Comportamento da aderência'),
            options=[
                self.tr('Prefer aligning nodes, insert extra vertices where required',
                        'Preferir alinhar vértices e inserir novos vértices quando necessário'),
                self.tr('Prefer closest point, insert extra vertices where required',
                        'Preferir o ponto mais próximo e inserir novos vértices quando necessário'),
                self.tr('Prefer aligning nodes, do not insert new vertices',
                        'Preferir alinhar vértices sem inserir novos vértices'),
                self.tr('Prefer closest point, do not insert new vertices',
                        'Preferir o ponto mais próximo sem inserir novos vértices')
            ],
            defaultValue=0
        ))

        self.addParameter(QgsProcessingParameterFeatureSink(
            self.OUTPUT,
            self.tr('Connected parcels', 'Lotes conectados')
        ))

        self.addParameter(QgsProcessingParameterFeatureSink(
            self.REPORT,
            self.tr('Connectivity correction report', 'Relatório de correção da conectividade'),
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

    def _create_work_layer(self, source):
        original_fields = source.fields()
        work_fields = QgsFields()
        for field in original_fields:
            work_fields.append(field)

        self._orig_id_field = self._unique_field_name(work_fields, '__lf_orig_id__')
        work_fields.append(QgsField(self._orig_id_field, QMetaType.Type.LongLong))

        work = QgsMemoryProviderUtils.createMemoryLayer(
            'lf_connect_work', work_fields, source.wkbType(), source.sourceCrs()
        )
        provider = work.dataProvider()
        new_features = []

        for feat in source.getFeatures():
            new_feat = QgsFeature(work_fields)
            new_feat.setGeometry(QgsGeometry(feat.geometry()))
            new_feat.setAttributes(feat.attributes()[:] + [int(feat.id())])
            new_features.append(new_feat)

        if new_features:
            provider.addFeatures(new_features)
        work.updateExtents()
        return work

    def _report_fields(self):
        fields = QgsFields()
        fields.append(QgsField('lf_orig_id', QMetaType.Type.LongLong))
        fields.append(QgsField('lf_status', QMetaType.Type.QString, len=20))
        fields.append(QgsField('lf_reason', QMetaType.Type.QString, len=160))
        fields.append(QgsField('vertices_b', QMetaType.Type.Int))
        fields.append(QgsField('vertices_a', QMetaType.Type.Int))
        fields.append(QgsField('area_before', QMetaType.Type.Double))
        fields.append(QgsField('area_after', QMetaType.Type.Double))
        fields.append(QgsField('area_delta', QMetaType.Type.Double))
        return fields

    def _add_report(self, sink, fields, fid, status, reason,
                    vertices_before, vertices_after, area_before, area_after):
        feat = QgsFeature(fields)
        feat.setAttributes([
            int(fid), status, reason,
            int(vertices_before), int(vertices_after),
            float(area_before), float(area_after),
            float(area_after - area_before)
        ])
        sink.addFeature(feat, QgsFeatureSink.Flag.FastInsert)

    def processAlgorithm(self, parameters, context, feedback):
        source = self.parameterAsSource(parameters, self.INPUT, context)
        if source is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.INPUT))

        tolerance = self.parameterAsDouble(parameters, self.TOLERANCE, context)
        behavior = self.parameterAsEnum(parameters, self.BEHAVIOR, context)

        if tolerance <= 0:
            raise QgsProcessingException(self.tr('Invalid tolerance!', 'Tolerância inválida!'))

        crs = source.sourceCrs()

        # A tolerância informada pelo usuário é sempre em metros.
        # Se o SRC for geográfico, converte para graus usando a latitude
        # média da extensão da camada, seguindo o padrão do LFTools.
        tolerance_m = tolerance
        tolerance_effective = tolerance_m

        if crs.isGeographic():
            extent = source.sourceExtent()
            mean_latitude = (extent.yMaximum() + extent.yMinimum()) / 2.0
            tolerance_effective = meters2degrees(
                tolerance_m,
                mean_latitude,
                crs
            )

            feedback.pushInfo(self.tr(
                'Snapping tolerance: {} m | equivalent angular tolerance: {} degrees'
                .format(tolerance_m, tolerance_effective),
                'Tolerância de aderência: {} m | tolerância angular equivalente: {} graus'
                .format(tolerance_m, tolerance_effective)
            ))
        else:
            feedback.pushInfo(self.tr(
                'Snapping tolerance: {} m'.format(tolerance_m),
                'Tolerância de aderência: {} m'.format(tolerance_m)
            ))

        output_fields = source.fields()
        sink, dest_id = self.parameterAsSink(
            parameters, self.OUTPUT, context, output_fields,
            source.wkbType(), crs
        )
        if sink is None:
            raise QgsProcessingException(self.invalidSinkError(parameters, self.OUTPUT))

        report_fields = self._report_fields()
        report_sink, report_id = self.parameterAsSink(
            parameters, self.REPORT, context, report_fields,
            Qgis.WkbType.NoGeometry, crs
        )
        if report_sink is None:
            raise QgsProcessingException(self.invalidSinkError(parameters, self.REPORT))

        feedback.pushInfo(self.tr(
            'Preparing geometries and preserving original feature IDs...',
            'Preparando geometrias e preservando os IDs originais das feições...'
        ))

        work = self._create_work_layer(source)

        originals = {}
        attrs = {}
        for feat in source.getFeatures():
            originals[int(feat.id())] = QgsGeometry(feat.geometry())
            attrs[int(feat.id())] = feat.attributes()[:]

        feedback.pushInfo(self.tr(
            'Connecting adjacent polygon geometries...',
            'Conectando geometrias poligonais adjacentes...'
        ))

        snapped = processing.run(
            'native:snapgeometries',
            {
                'INPUT': work,
                'REFERENCE_LAYER': work,
                'TOLERANCE': tolerance_effective,
                'BEHAVIOR': behavior,
                'OUTPUT': 'TEMPORARY_OUTPUT'
            },
            context=context,
            feedback=feedback
        )['OUTPUT']

        results = {}
        for feat in snapped.getFeatures():
            try:
                fid = int(feat[self._orig_id_field])
            except (TypeError, ValueError):
                continue
            results[fid] = QgsGeometry(feat.geometry())

        total = 100.0 / len(originals) if originals else 0
        modified = 0
        unchanged = 0
        blocked = 0

        for current, fid in enumerate(sorted(originals.keys())):
            if feedback.isCanceled():
                feedback.pushWarning(self.tr(
                    'Operation canceled by the user.',
                    'Operação cancelada pelo usuário.'
                ))
                return {self.OUTPUT: dest_id, self.REPORT: report_id}

            old_geom = originals[fid]
            new_geom = results.get(fid)
            vertices_before = self._vertex_count(old_geom)
            area_before = old_geom.area() if old_geom and not old_geom.isNull() and not old_geom.isEmpty() else 0.0

            status = 'unchanged'
            reason = self.tr('No connectivity adjustment was required',
                             'Nenhum ajuste de conectividade foi necessário')
            out_geom = QgsGeometry(old_geom)

            if old_geom is None or old_geom.isNull() or old_geom.isEmpty():
                status = 'blocked'
                reason = self.tr('Original geometry is null or empty',
                                 'Geometria original nula ou vazia')
            elif not old_geom.isGeosValid():
                status = 'blocked'
                reason = self.tr(
                    'Original geometry is invalid; connectivity adjustment was not applied',
                    'A geometria original é inválida; o ajuste de conectividade não foi aplicado'
                )
            elif new_geom is None:
                status = 'blocked'
                reason = self.tr('Snapping result was not found; original geometry preserved',
                                 'Resultado da aderência não encontrado; geometria original preservada')
            elif new_geom.isNull() or new_geom.isEmpty():
                status = 'blocked'
                reason = self.tr('Snapping returned a null or empty geometry; original geometry preserved',
                                 'A aderência resultou em geometria nula ou vazia; geometria original preservada')
            elif new_geom.type() != Qgis.GeometryType.Polygon:
                status = 'blocked'
                reason = self.tr('Snapping changed the geometry family; original geometry preserved',
                                 'A aderência alterou a família geométrica; geometria original preservada')
            elif not new_geom.isGeosValid():
                status = 'blocked'
                reason = self.tr('Snapping produced an invalid geometry; original geometry preserved',
                                 'A aderência produziu uma geometria inválida; geometria original preservada')
            elif old_geom.asWkb() != new_geom.asWkb():
                status = 'modified'
                reason = self.tr('Geometry adjusted within the snapping tolerance',
                                 'Geometria ajustada dentro da tolerância de aderência')
                out_geom = QgsGeometry(new_geom)

            vertices_after = self._vertex_count(out_geom)
            area_after = out_geom.area() if out_geom and not out_geom.isNull() and not out_geom.isEmpty() else 0.0

            sink_feat = QgsFeature(output_fields)
            sink_feat.setGeometry(out_geom)
            sink_feat.setAttributes(attrs[fid])
            sink.addFeature(sink_feat, QgsFeatureSink.Flag.FastInsert)

            if status == 'modified':
                modified += 1
                self._add_report(report_sink, report_fields, fid, status, reason,
                                 vertices_before, vertices_after, area_before, area_after)
            elif status == 'blocked':
                blocked += 1
                self._add_report(report_sink, report_fields, fid, status, reason,
                                 vertices_before, vertices_after, area_before, area_after)
            else:
                unchanged += 1

            feedback.setProgress(int((current + 1) * total))

        feedback.pushInfo(self.tr(
            '{} feature(s) modified.'.format(modified),
            '{} feição(ões) modificada(s).'.format(modified)
        ))
        feedback.pushInfo(self.tr(
            '{} feature(s) unchanged.'.format(unchanged),
            '{} feição(ões) sem alteração.'.format(unchanged)
        ))
        if blocked:
            feedback.pushWarning(self.tr(
                '{} potentially unsafe modification(s) were blocked and the original geometries were preserved.'.format(blocked),
                '{} modificação(ões) potencialmente insegura(s) foram bloqueadas e as geometrias originais foram preservadas.'.format(blocked)
            ))

        feedback.pushInfo(self.tr('Operation completed successfully!', 'Operação finalizada com sucesso!'))
        feedback.pushInfo(self.tr('Leandro Franca - Cartographic Engineer', 'Leandro França - Eng Cart'))

        return {self.OUTPUT: dest_id, self.REPORT: report_id}