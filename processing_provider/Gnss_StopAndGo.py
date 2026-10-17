# -*- coding: utf-8 -*-

"""
Gnss_StopAndGo.py
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
__date__ = '2022-06-13'
__copyright__ = '(C) 2022, Leandro França'

from qgis.PyQt.QtCore import QMetaType
from qgis.core import (Qgis,
                       QgsFeatureSink,
                       QgsFeature,
                       QgsFields,
                       QgsDistanceArea,
                       QgsPointXY,
                       QgsField,
                       QgsPoint,
                       QgsGeometry,
                       QgsProcessingException,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterNumber,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterFeatureSink,
                       QgsApplication
                       )

from lftools.geocapt.imgs import Imgs
from lftools.translations.translate import translate

from math import isfinite
from datetime import datetime
import os
from qgis.PyQt.QtGui import QIcon


class StopAndGo(QgsProcessingAlgorithm):

    LOC = QgsApplication.locale()[:2]

    def tr(self, *string):
        return translate(string, self.LOC)

    def createInstance(self):
        return StopAndGo()

    def name(self):
        return 'stopandgo'

    def displayName(self):
        return self.tr('Stop and Go', 'Semicinemático (Stop and Go)')

    def group(self):
        return self.tr('GNSS')

    def groupId(self):
        return 'gnss'

    def tags(self):
        return 'GeoOne,gps,position,ibge,rtklib,ppp,ppk,navigation,satellites,surveying,rinex,glonass,beidou,compass,galileu,track,kinematic,rtk,ntrip,static,semikinematic,stop,and,go,semicinemático'.split(',')

    def icon(self):
        return QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images/satellite.png'))

    txt_en = '''It finds the central points (vertices) of the concentrations of points surveyed by the Kinematic method (stop and go) from the processing of GNSS data.
Input data:
◼️ GNSS point layer from RTKLIB or IBGE-PPP from .pos file
◼️ Minimum time to survey the point in minutes
◼️ Tolerance in centimeters to consider the static point'''
    txt_pt = '''Encontra os pontos centrais (vértices) das concentrações de pontos levantados pelo método Semicinemático (stop and go) provenientes do processamento de dados GNSS.
Dados de entrada:
◼️ Camada do tipo ponto gerada do arquivo .pos do RTKLIB ou IBGE-PPP
◼️ Tempo mínimo de levantamento do ponto em minutos
◼️ Tolerância em centímetros para considerar o ponto estático'''

    figure = 'images/tutorial/gnss_ppk.jpg'

    def shortHelpString(self):
        social_BW = Imgs().social_BW
        footer = '''<div align="center">
                      <img src="'''+ os.path.join(os.path.dirname(os.path.dirname(__file__)), self.figure) +'''">
                      </div>
                      <div align="left">
                      <p>
                      <b><a href="'''+ self.tr('https://portal.geoone.com.br/m/lessons/pvgnss?classId=3646') + '''" target="_blank">'''+ self.tr('Click here to watch a full class on this tool',
                                    'Clique aqui para assistir uma aula completa sobre esta ferramenta') +'''</a></b>
                      </p>
                      <p>
                      <b><a href="'''+ self.tr('https://geoone.com.br/pvgnss/') + '''" target="_blank">'''+ self.tr('Sign up for the GNSS with RTKLib and QGIS course',
                                    'Inscreva-se no curso de GNSS com RTKLib e QGIS') +'</a><br><br>'+ self.tr('Author: Leandro Franca', 'Autor: Leandro França')+'''</b>
                      </p>'''+ social_BW + '''
                    </div>'''
        return self.tr(self.txt_en, self.txt_pt) + footer


    INPUT = 'INPUT'
    TIME = 'TIME'
    DIST = 'DIST'
    OUTPUT = 'OUTPUT'

    def initAlgorithm(self, config=None):

        # INPUT
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT,
                self.tr('GNSS point Layer', 'Camada de Pontos GNSS'),
                [Qgis.ProcessingSourceType.TypeVectorPoint]
            )
        )

        self.addParameter(
            QgsProcessingParameterNumber(
                self.TIME,
                self.tr('Minimum time for static positioning (minutes)', 'Tempo mínimo para o posicionamento estático (minutos)'),
                type = QgsProcessingParameterNumber.Type.Double,
                defaultValue = 3.0,
                minValue = 0.10
                )
            )

        self.addParameter(
            QgsProcessingParameterNumber(
                self.DIST,
                self.tr('Maximum distance to be static (cm)', 'Distância máxima para ser estático (cm)'),
                type = QgsProcessingParameterNumber.Type.Double,
                defaultValue = 5.0,
                minValue = 0.5
                )
            )

        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT,
                self.tr('Central points', 'Vértices')
            )
        )


    def processAlgorithm(self, parameters, context, feedback):

        layer = self.parameterAsSource(parameters, self.INPUT, context)
        if layer is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.INPUT))

        tempo_min = self.parameterAsDouble(parameters, self.TIME, context) * 60.0
        dist_max = self.parameterAsDouble(parameters, self.DIST, context) / 100.0
        if not isfinite(tempo_min) or tempo_min <= 0:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.TIME))
        if not isfinite(dist_max) or dist_max <= 0:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.DIST))

        source_fields = layer.fields()
        time_index = -1
        for name in (self.tr('datetime', 'datahora'), 'datetime', 'datahora'):
            time_index = source_fields.lookupField(name)
            if time_index >= 0:
                break
        height_index = source_fields.lookupField('h')
        if time_index < 0 or height_index < 0:
            raise QgsProcessingException(
                self.tr('Check the input layer!', 'Verifique a camada de entrada!')
                + ' (datetime / datahora, h)')

        # Copy the schema; avoid duplicate metadata fields if the input already
        # contains a previous result. No input feature is modified.
        metadata = {'start_time': QMetaType.Type.QString,
                    'end_time': QMetaType.Type.QString,
                    'count': QMetaType.Type.Int,
                    'group': QMetaType.Type.Int,
                    'duration_s': QMetaType.Type.Double}
        Fields = QgsFields()
        attribute_indices = []
        for index, field in enumerate(source_fields):
            if field.name().lower() not in metadata:
                Fields.append(field)
                attribute_indices.append(index)
        for name, field_type in metadata.items():
            Fields.append(QgsField(name, field_type))

        # Provider iteration order (and FID order) is not a time sequence.
        # Retain the feature itself so the central point's attributes always
        # belong to the current stop, even when coordinates are repeated.
        records = []
        for feat in layer.getFeatures():
            if feedback.isCanceled():
                return {}
            try:
                geom = feat.geometry()
                if geom.isEmpty():
                    raise ValueError('empty geometry')
                if geom.isMultipart():
                    points = geom.asMultiPoint()
                    if len(points) != 1:
                        raise ValueError('expected one GNSS point per epoch')
                    point = points[0]
                else:
                    point = geom.asPoint()
                if not all(isfinite(v) for v in (point.x(), point.y(), float(feat[height_index]))):
                    raise ValueError('non-finite coordinates')
                value = feat[time_index]
                if hasattr(value, 'toPyDateTime'):
                    epoch = value.toPyDateTime()
                elif isinstance(value, datetime):
                    epoch = value
                else:
                    epoch = datetime.fromisoformat(str(value).strip().replace('Z', '+00:00'))
                if not isinstance(epoch, datetime):
                    raise ValueError('invalid datetime')
                time_text = (epoch.isoformat(sep=' ') if isinstance(value, datetime)
                             or hasattr(value, 'toPyDateTime') else str(value))
                records.append((epoch, feat.id(), QgsFeature(feat),
                                QgsPointXY(point.x(), point.y()), time_text))
            except Exception as error:
                raise QgsProcessingException(
                    self.tr('Check the input layer!', 'Verifique a camada de entrada!')
                    + ' FID {}: {}'.format(feat.id(), error)) from error

        try:
            records.sort(key=lambda record: (record[0], record[1]))
        except (TypeError, ValueError) as error:
            raise QgsProcessingException(
                self.tr('Check the input layer!', 'Verifique a camada de entrada!')
                + ' (datetime / datahora)') from error

        # Measure horizontal distances in meters on the source CRS ellipsoid,
        # for both geographic and projected input layers.
        distance = QgsDistanceArea()
        distance.setSourceCrs(layer.sourceCrs(), context.transformContext())
        ellipsoid = layer.sourceCrs().ellipsoidAcronym()
        if not ellipsoid or not distance.setEllipsoid(ellipsoid):
            if not distance.setEllipsoid('WGS84'):
                raise QgsProcessingException(
                    self.tr('Check the input layer!', 'Verifique a camada de entrada!'))

        (sink, dest_id) = self.parameterAsSink(
            parameters, self.OUTPUT, context, Fields,
            Qgis.WkbType.PointZ, layer.sourceCrs())
        if sink is None:
            raise QgsProcessingException(self.invalidSinkError(parameters, self.OUTPUT))

        # A stop is a maximal chronological run of neighboring epochs within
        # the distance tolerance. The first moving epoch starts the next run;
        # it must not extend the duration of the stop which just ended.
        groups = []
        start = 0
        for index in range(1, len(records) + 1):
            if feedback.isCanceled():
                return {self.OUTPUT: dest_id}
            if (index == len(records)
                    or distance.measureLine(records[index - 1][3], records[index][3]) > dist_max):
                duration = (records[index - 1][0] - records[start][0]).total_seconds()
                if duration >= tempo_min:
                    groups.append((start, index, duration))
                start = index

        feedback.pushInfo(self.tr('Calculating central features...', 'Calculando feições centrais...'))
        for group_id, (start, end, duration) in enumerate(groups, 1):
            group = records[start:end]
            # Central observed feature (medoid), not an averaged coordinate:
            # its height, precision and other attributes remain consistent.
            sums = [0.0] * len(group)
            for i in range(len(group)):
                if feedback.isCanceled():
                    return {self.OUTPUT: dest_id}
                for j in range(i + 1, len(group)):
                    separation = distance.measureLine(group[i][3], group[j][3])
                    sums[i] += separation
                    sums[j] += separation
            central = group[min(range(len(group)), key=lambda i: sums[i])]
            source_feat = central[2]
            point = central[3]
            output_feat = QgsFeature(Fields)
            output_feat.setGeometry(QgsGeometry(QgsPoint(
                point.x(), point.y(), float(source_feat[height_index]))))
            attributes = [source_feat[index] for index in attribute_indices]
            attributes += [group[0][4], group[-1][4], len(group), group_id, duration]
            output_feat.setAttributes(attributes)
            if not sink.addFeature(output_feat, QgsFeatureSink.Flag.FastInsert):
                raise QgsProcessingException(sink.lastError())
            feedback.setProgress(100.0 * group_id / len(groups))

        feedback.pushInfo(self.tr('Operation completed successfully!', 'Operação finalizada com sucesso!'))
        feedback.pushInfo(self.tr('Leandro Franca - Cartographic Engineer', 'Leandro França - Eng Cart'))
        return {self.OUTPUT: dest_id}
