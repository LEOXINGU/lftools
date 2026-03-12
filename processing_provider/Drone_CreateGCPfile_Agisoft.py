# -*- coding: utf-8 -*-

"""
Drone_CreateGCPfile_Agisoft.py
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""
__author__ = 'Ilton Freitas and Leandro França'
__date__ = '2026-03-12'
__copyright__ = '(C) 2026, Leandro França'

from qgis.core import (
    QgsApplication,
    QgsProcessingParameterVectorLayer,
    QgsProcessing,
    QgsProcessingParameterField,
    QgsProcessingParameterCrs,
    QgsCoordinateTransform,
    QgsProcessingParameterFileDestination,
    QgsProcessingParameterBoolean,
    QgsProcessingParameterNumber,
    QgsProject,
    QgsProcessingException,
    QgsProcessingAlgorithm,
    QgsWkbTypes
)
from lftools.geocapt.imgs import Imgs
from lftools.translations.translate import translate
from qgis.PyQt.QtGui import QIcon

import os
import csv
import subprocess


class CreateGCPfileAgisoft(QgsProcessingAlgorithm):

    LOC = QgsApplication.locale()[:2]

    def tr(self, *string):
        return translate(string, self.LOC)

    def createInstance(self):
        return CreateGCPfileAgisoft()

    def name(self):
        return 'creategcpfileagisoft'

    def displayName(self):
        return self.tr(
            'Generate GCP file for Agisoft Metashape',
            'Gerar arquivo de GCP para Agisoft Metashape'
        )

    def group(self):
        return self.tr('Drones')

    def groupId(self):
        return 'drones'

    def tags(self):
        return 'GeoOne,drones,fotografia,agisoft,metashape,photography,gcp,points,control,ground,quality,homologous,controle,terreno'.split(',')

    def icon(self):
        return QIcon(
            os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                'images/drone.png'
            )
        )

    txt_en = '''Generate a <b>TXT file with Ground Control Points (GCP)</b> from a <b>point layer</b><br> for import into <b>Agisoft Metashape</b>.
<p>
  <b>Output format:</b>
  <code>Name, X, Y, Z, X_error, Y_error, Z_error</code>
</p>
<p>
  <b>Notes:</b>
</p>
  - <b>X</b> and <b>Y</b> coordinates are obtained from the <b>point geometry</b>.
  - <b>Z</b> values can be obtained from a <b>field</b> or from the <b>3D geometry</b> of the layer.
  - If no <b>Z field</b> is provided and the geometry has no <b>Z value</b>, the <b>Z coordinate</b> will be set to <b>0</b>.
  - For best results in <b>Agisoft Metashape</b>, use <b>projected coordinate systems</b>.
'''

    txt_pt = '''Gera um <b>arquivo TXT com Pontos de Controle no Terreno (GCP)</b> a partir de uma <b>camada de pontos</b><br> para importação no <b>Agisoft Metashape</b>.

<p>
  <b>Formato de saída:</b>
  <code>Name, X, Y, Z, X_error, Y_error, Z_error</code>
</p>

<p>
  <b>Observações:</b>
</p>
  - As coordenadas <b>X</b> e <b>Y</b> são obtidas da <b>geometria do ponto</b>.
  - O valor de <b>Z</b> pode ser obtido a partir de um <b>campo</b> ou da <b>geometria 3D</b> da camada.
  - Se nenhum <b>campo Z</b> for fornecido e a geometria não possuir <b>valor Z</b>, a <b>coordenada Z</b> será definida como <b>0</b>.
  - Para melhores resultados no <b>Agisoft Metashape</b>, utilize <b>sistemas de coordenadas projetados</b>.
'''

    figure = 'images/tutorial/drone_createGCP_Agisoft.jpg'

    def shortHelpString(self):
        social_BW = Imgs().social_BW
        footer = '''<div align="center">
                      <img src="'''+ os.path.join(os.path.dirname(os.path.dirname(__file__)), self.figure) +'''">
                      </div>
                      <div align="left">
                      <p>
                      <b><a href="'''+ self.tr('https://portal.geoone.com.br/m/lessons/drone-webodm?classId=2307') + '''" target="_blank">'''+ self.tr('Click here to watch a full class on this tool',
                                    'Clique aqui para assistir uma aula completa sobre esta ferramenta') +'''</a></b>
                      </p>
                      <p>
                      <b><a href="'''+ self.tr('https://geoone.com.br/pvdrone/') + '''" target="_blank">'''+ self.tr('Sign up for the WebODM and QGIS course',
                                    'Inscreva-se no curso de WebODM e QGIS') +'</a><br><br>'+ self.tr('Author: Leandro Franca & Prof Ilton', 'Autor: Leandro França e Prof. Ilton')+'''</b>
                      </p>'''+ social_BW + '''
                    </div>'''
        return self.tr(self.txt_en, self.txt_pt) + footer

    INPUT_LAYER = 'INPUT_LAYER'
    NAME_FIELD = 'NAME_FIELD'
    Z_FIELD = 'Z_FIELD'
    X_ERROR_FIELD = 'X_ERROR_FIELD'
    Y_ERROR_FIELD = 'Y_ERROR_FIELD'
    Z_ERROR_FIELD = 'Z_ERROR_FIELD'
    TARGET_CRS = 'TARGET_CRS'
    DECIMAL_PLACES = 'DECIMAL_PLACES'
    OUTPUT_FILE = 'OUTPUT_FILE'
    OPEN = 'OPEN'

    def initAlgorithm(self, config=None):

        self.addParameter(
            QgsProcessingParameterVectorLayer(
                self.INPUT_LAYER,
                self.tr('Point Layer', 'Camada de Pontos'),
                [QgsProcessing.TypeVectorPoint]
            )
        )

        self.addParameter(
            QgsProcessingParameterField(
                self.NAME_FIELD,
                self.tr('GCP name', 'Nome do ponto de controle'),
                parentLayerParameterName=self.INPUT_LAYER,
                type=QgsProcessingParameterField.Any,
                # optional=True
            )
        )

        self.addParameter(
            QgsProcessingParameterField(
                self.Z_FIELD,
                self.tr('Z Coordinate', 'Coordenada Z'),
                parentLayerParameterName=self.INPUT_LAYER,
                type=QgsProcessingParameterField.Any,
                optional=True
            )
        )

        self.addParameter(
            QgsProcessingParameterField(
                self.X_ERROR_FIELD,
                self.tr('X Error', 'Erro em X'),
                parentLayerParameterName=self.INPUT_LAYER,
                type=QgsProcessingParameterField.Any,
                optional=True
            )
        )

        self.addParameter(
            QgsProcessingParameterField(
                self.Y_ERROR_FIELD,
                self.tr('Y Error', 'Erro em Y'),
                parentLayerParameterName=self.INPUT_LAYER,
                type=QgsProcessingParameterField.Any,
                optional=True
            )
        )

        self.addParameter(
            QgsProcessingParameterField(
                self.Z_ERROR_FIELD,
                self.tr('Z Error', 'Erro em Z'),
                parentLayerParameterName=self.INPUT_LAYER,
                type=QgsProcessingParameterField.Any,
                optional=True
            )
        )

        self.addParameter(
            QgsProcessingParameterCrs(
                self.TARGET_CRS,
                self.tr('Target CRS', 'SRC de Destino'),
                optional=True
            )
        )

        self.addParameter(
            QgsProcessingParameterNumber(
                self.DECIMAL_PLACES,
                self.tr('Decimal places', 'Casas decimais'),
                type=QgsProcessingParameterNumber.Type.Integer,
                defaultValue=3,
                minValue=1,
                maxValue=10
            )
        )

        self.addParameter(
            QgsProcessingParameterFileDestination(
                self.OUTPUT_FILE,
                self.tr('TXT with Ground Control Points (GCP)', 'TXT com Pontos de Controle (GCP)'),
                fileFilter='Text (*.txt)'
            )
        )

        self.addParameter(
            QgsProcessingParameterBoolean(
                self.OPEN,
                self.tr(
                    'Open output file after executing the algorithm',
                    'Abrir arquivo de saída com GCPs'
                ),
                defaultValue=True
            )
        )

    def _to_float(self, value, default=None):
        if value is None:
            return default
        try:
            return float(str(value).strip().replace(',', '.'))
        except Exception:
            return default

    def _sanitize_name(self, value, fallback):
        if value is None:
            return fallback
        name = str(value).strip().replace(' ', '_')
        if not name or name.lower() == 'none':
            return fallback
        return name

    def processAlgorithm(self, parameters, context, feedback):

        layer = self.parameterAsVectorLayer(parameters, self.INPUT_LAYER, context)
        if layer is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.INPUT_LAYER))

        if layer.featureCount() == 0:
            raise QgsProcessingException(
                self.tr('The input layer has no features!',
                        'A camada de entrada não possui feições!')
            )

        name_field = self.parameterAsString(parameters, self.NAME_FIELD, context)
        z_field = self.parameterAsString(parameters, self.Z_FIELD, context)
        x_error_field = self.parameterAsString(parameters, self.X_ERROR_FIELD, context)
        y_error_field = self.parameterAsString(parameters, self.Y_ERROR_FIELD, context)
        z_error_field = self.parameterAsString(parameters, self.Z_ERROR_FIELD, context)

        target_crs = self.parameterAsCrs(parameters, self.TARGET_CRS, context)
        decimal_places = self.parameterAsInt(parameters, self.DECIMAL_PLACES, context)
        output_file = self.parameterAsFile(parameters, self.OUTPUT_FILE, context)
        open_file = self.parameterAsBool(parameters, self.OPEN, context)

        if decimal_places is None or decimal_places < 1:
            raise QgsProcessingException(
                self.tr('Invalid number of decimal places!',
                        'Número de casas decimais inválido!')
            )

        if not output_file:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.OUTPUT_FILE))

        fields = layer.fields()
        field_names = [f.name() for f in fields]

        if name_field and name_field not in field_names:
            raise QgsProcessingException(
                self.tr('Invalid name field!',
                        'Campo de nome inválido!')
            )

        if z_field and z_field not in field_names:
            raise QgsProcessingException(
                self.tr('Invalid Z field!',
                        'Campo Z inválido!')
            )

        if x_error_field and x_error_field not in field_names:
            raise QgsProcessingException(
                self.tr('Invalid X error field!',
                        'Campo de erro X inválido!')
            )

        if y_error_field and y_error_field not in field_names:
            raise QgsProcessingException(
                self.tr('Invalid Y error field!',
                        'Campo de erro Y inválido!')
            )

        if z_error_field and z_error_field not in field_names:
            raise QgsProcessingException(
                self.tr('Invalid Z error field!',
                        'Campo de erro Z inválido!')
            )

        if target_crs.isValid():
            coordinate_transformer = QgsCoordinateTransform(
                layer.crs(), target_crs, QgsProject.instance()
            )
            if target_crs.isGeographic():
                feedback.reportError(
                    self.tr(
                        'Warning: target CRS is geographic. Agisoft Metashape works best with projected coordinates.',
                        'Aviso: o SRC de destino é geográfico. O Agisoft Metashape funciona melhor com coordenadas projetadas.'
                    )
                )
        else:
            coordinate_transformer = None
            if layer.crs().isGeographic():
                feedback.reportError(
                    self.tr(
                        'Warning: layer CRS is geographic. Agisoft Metashape works best with projected coordinates.',
                        'Aviso: o SRC da camada é geográfico. O Agisoft Metashape funciona melhor com coordenadas projetadas.'
                    )
                )

        # Verifica se a camada possui geometria Z quando não há campo Z
        has_z_geometry = QgsWkbTypes.hasZ(layer.wkbType())

        if not z_field and not has_z_geometry:
            feedback.reportError(
                self.tr(
                    'Layer features do not have a Z coordinate. The Z coordinate will be set to 0 (zero)!',
                    'Feições da camada não possuem coordenada Z. A coordenada Z será definida como 0 (zero)!'
                )
            )

        format_num = '{:.Xf}'.replace('X', str(decimal_places))
        total = layer.featureCount()

        with open(output_file, 'w', encoding='utf-8', newline='') as arq:
            writer = csv.writer(arq, delimiter=',', lineterminator='\n')

            for current, feat in enumerate(layer.getFeatures(), start=1):

                if feedback.isCanceled():
                    break

                geom = feat.geometry()
                if geom is None or geom.isNull() or geom.isEmpty():
                    feedback.reportError(
                        self.tr(
                            'Skipping feature ID {}: empty geometry.',
                            'Ignorando feição ID {}: geometria vazia.'
                        ).format(feat.id())
                    )
                    continue

                if coordinate_transformer is not None:
                    try:
                        geom.transform(coordinate_transformer)
                    except Exception as e:
                        feedback.reportError(
                            self.tr(
                                'Error transforming feature ID {}: {}',
                                'Erro ao transformar a feição ID {}: {}'
                            ).format(feat.id(), str(e))
                        )
                        continue

                pnt = geom.asPoint()

                name_value = feat[name_field] if name_field else None
                name = self._sanitize_name(name_value, 'GCP_{}'.format(current))

                x = pnt.x()
                y = pnt.y()

                if z_field:
                    z = self._to_float(feat[z_field], default=None)
                    if z is None:
                        raise QgsProcessingException(
                            self.tr(
                                'Invalid Z value "{}" for feature ID {}',
                                'Valor Z inválido "{}" para a feição ID {}'
                            ).format(str(feat[z_field]), feat.id())
                        )
                else:
                    if has_z_geometry:
                        try:
                            z = geom.constGet().z()
                        except Exception:
                            z = 0.0
                    else:
                        z = 0.0

                x_error = self._to_float(feat[x_error_field], default=0.0) if x_error_field else 0.0
                y_error = self._to_float(feat[y_error_field], default=0.0) if y_error_field else 0.0
                z_error = self._to_float(feat[z_error_field], default=0.0) if z_error_field else 0.0

                writer.writerow([
                    name,
                    format_num.format(x),
                    format_num.format(y),
                    format_num.format(z),
                    format_num.format(x_error),
                    format_num.format(y_error),
                    format_num.format(z_error)
                ])

                feedback.setProgress(int(current * 100 / total))

        if open_file:
            try:
                if os.name == 'nt':
                    os.startfile(output_file)
                elif os.name == 'posix':
                    subprocess.Popen(['xdg-open', output_file])
                else:
                    feedback.reportError(
                        self.tr(
                            'Automatic file opening is not supported on this operating system.',
                            'A abertura automática do arquivo não é suportada neste sistema operacional.'
                        )
                    )
            except Exception as e:
                feedback.reportError(
                    self.tr(
                        'Failed to open output file: {}',
                        'Falha ao abrir o arquivo de saída: {}'
                    ).format(str(e))
                )

        feedback.pushInfo(self.tr('Operation completed successfully!', 'Operação finalizada com sucesso!'))
        feedback.pushInfo(self.tr('Leandro Franca - Cartographic Engineer', 'Leandro França - Eng Cart'))

        return {self.OUTPUT_FILE: output_file}