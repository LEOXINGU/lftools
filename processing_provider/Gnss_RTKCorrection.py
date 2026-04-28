# -*- coding: utf-8 -*-

"""
Gnss_RTKCorrection.py
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
from qgis.core import (QgsProcessing,
                       QgsFeatureSink,
                       QgsWkbTypes,
                       QgsField,
                       QgsPoint,
                       QgsFeature,
                       QgsGeometry,
                       QgsProcessingException,
                       QgsProcessingParameterString,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterNumber,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterFeatureSink,
                       QgsProcessingParameterField,
                       QgsProcessingParameterFileDestination,
                       QgsApplication,
                       QgsEllipsoidUtils,
                       QgsProject,
                       QgsProcessingParameterCrs,
                       QgsCoordinateTransform,
                       QgsCoordinateReferenceSystem)

from lftools.geocapt.imgs import Imgs, lftools_logo
from lftools.translations.translate import translate
from numpy import sqrt
from lftools.geocapt.topogeo import geod2geoc, geoc2geod, geoc2enu, str2HTML, dd2dms
from lftools.geocapt.cartography import ellipsoidFromCRS
from datetime import datetime
from numpy import array
import os
from qgis.PyQt.QtGui import QIcon


class RTKCorrection(QgsProcessingAlgorithm):

    LOC = QgsApplication.locale()[:2]

    def tr(self, *string):
        return translate(string, self.LOC)

    def createInstance(self):
        return RTKCorrection()

    def name(self):
        return 'rtkcorrection'

    def displayName(self):
        return self.tr('RTK Points Correction', 'Correção de Pontos RTK')

    def group(self):
        return self.tr('GNSS')

    def groupId(self):
        return 'gnss'

    def tags(self):
        return 'GeoOne,gps,position,ibge,ppp,ppk,navigation,ajdusted,ajustar,ajustado,ajustada,satellites,corrected,corrigir,surveying,rinex,glonass,beidou,compass,galileu,track,kinematic,rtk,ntrip,static,real'.split(',')

    def icon(self):
        return QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images/satellite.png'))

    txt_en = '''Applies RTK base correction using post-processed coordinates (e.g., PPP) by computing a geocentric translation vector and applying it to all rover points. Optionally propagates positional uncertainties and provides results in both geocentric and local topocentric (E, N, U) systems.'''

    txt_pt = '''Aplica a correção da base RTK utilizando coordenadas pós-processadas (por exemplo, PPP), por meio do cálculo de um vetor de translação geocêntrico aplicado a todos os pontos rover. Opcionalmente realiza a propagação das incertezas posicionais e fornece resultados nos sistemas geocêntrico e topocêntrico local (E, N, U).'''

    figure = 'images/tutorial/gnss_rtk_correction.jpg'

    def shortHelpString(self):
        social_BW = Imgs().social_BW
        footer = '''<div align="center">
                      <img src="'''+ os.path.join(os.path.dirname(os.path.dirname(__file__)), self.figure) +'''">
                      </div>
                      <div align="left">
                      <p>
                      <b><a href="'''+ self.tr('https://portal.geoone.com.br/m/lessons/pvgnss?classId=3647') + '''" target="_blank">'''+ self.tr('Click here to watch a full class on this tool',
                                    'Clique aqui para assistir uma aula completa sobre esta ferramenta') +'''</a></b>
                      </p>
                      <p>
                      <b><a href="'''+ self.tr('https://geoone.com.br/pvgnss/') + '''" target="_blank">'''+ self.tr('Sign up for the GNSS with RTKLib and QGIS course',
                                    'Inscreva-se no curso de GNSS com RTKLib e QGIS') +'</a><br><br>'+ self.tr('Author: Leandro Franca', 'Autor: Leandro França')+'''</b>
                      </p>'''+ social_BW + '''
                    </div>'''
        return self.tr(self.txt_en, self.txt_pt) + footer

    BASE_RTK = 'BASE_RTK'
    PPP = 'PPP'
    CRS = 'CRS'
    INPUT = 'INPUT'
    OUTPUT = 'OUTPUT'
    SIGMA_X_BASE = 'SIGMA_X_BASE'
    SIGMA_Y_BASE = 'SIGMA_Y_BASE'
    SIGMA_Z_BASE = 'SIGMA_Z_BASE'
    SIGMA_X_ROVER = 'SIGMA_X_ROVER'
    SIGMA_Y_ROVER = 'SIGMA_Y_ROVER'
    SIGMA_Z_ROVER = 'SIGMA_Z_ROVER'
    REPORT = 'REPORT'

    def initAlgorithm(self, config=None):

        # INPUT
        self.addParameter(
            QgsProcessingParameterString(
                self.BASE_RTK,
                self.tr('Initial X,Y,Z coordinates of the base', 'Coordenadas X,Y,Z iniciais da base'),
                defaultValue='PointZ (X Y Z)'
            )
        )

        self.addParameter(
            QgsProcessingParameterString(
                self.PPP,
                self.tr('Post-processed X,Y,Z coordinates of the base', 'Coordenadas X,Y,Z pós-processadas da base'),
                defaultValue='PointZ (X Y Z)'
            )
        )

        self.addParameter(
            QgsProcessingParameterCrs(
                self.CRS,
                self.tr('Base CRS', 'SRC da Base'),
                QgsProject.instance().crs()
                )
            )

        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT,
                self.tr('GNSS RTK Point Layer', 'Camada de Pontos GNSS RTK'),
                [QgsProcessing.TypeVectorPoint]
            )
        )

        # Base Precisions

        self.addParameter(
            QgsProcessingParameterNumber(
                self.SIGMA_X_BASE,
                self.tr('Base Sigma X (m) - East', 'Sigma da Base X (m) - Este'),
                type = QgsProcessingParameterNumber.Type.Double,
                minValue = 0.0,
                maxValue = 1.0,
                optional = True
            )
        )

        self.addParameter(
            QgsProcessingParameterNumber(
                self.SIGMA_Y_BASE,
                self.tr('Base Sigma Y (m) - North', 'Sigma da Base Y (m) - Norte'),
                type = QgsProcessingParameterNumber.Type.Double,
                minValue = 0.0,
                maxValue = 1.0,
                optional = True
            )
        )

        self.addParameter(
            QgsProcessingParameterNumber(
                self.SIGMA_Z_BASE,
                self.tr('Base Sigma Z (m) - Up', 'Sigma da Base Z (m) - Altura'),
                type = QgsProcessingParameterNumber.Type.Double,
                minValue = 0.0,
                maxValue = 1.0,
                optional = True
            )
        )

        # Rover Precisions
        self.addParameter(
             QgsProcessingParameterField(
                self.SIGMA_X_ROVER,
                self.tr('Rover Sigma X (m) - East', 'Sigma do Rover X (m) - Este'),
                parentLayerParameterName=self.INPUT,
                optional = True
            )
        )

        self.addParameter(
             QgsProcessingParameterField(
                self.SIGMA_Y_ROVER,
                self.tr('Rover Sigma Y (m) - North', 'Sigma do Rover Y (m) - Norte'),
                parentLayerParameterName=self.INPUT,
                optional = True
            )
        )

        self.addParameter(
             QgsProcessingParameterField(
                self.SIGMA_Z_ROVER,
                self.tr('Rover Sigma Z (m) - Up', 'Sigma do Rover Z (m) - Altura'),
                parentLayerParameterName=self.INPUT,
                optional = True
            )
        )

        # OUTPUT
        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT,
                self.tr('Adjusted RTK points', 'Pontos RTK corrigidos')
            )
        )

        self.addParameter(
            QgsProcessingParameterFileDestination(
                self.REPORT,
                self.tr('Adjustment Report', 'Relatório de Ajustamento'),
                self.tr('HTML files (*.html)')
            )
        )

    
    def ValidarPointZ_WKT(self, wkt_texto, descricao):
            try:
                geom = QgsGeometry.fromWkt(wkt_texto)
            except:
                raise QgsProcessingException(
                    self.tr('Invalid {} WKT: {}'.format(descricao, wkt_texto),
                            'WKT inválido para {}: {}'.format(descricao, wkt_texto))
                )

            if geom.isNull() or geom.type() != QgsWkbTypes.PointGeometry:
                raise QgsProcessingException(
                    self.tr('Invalid {} WKT: {}'.format(descricao, wkt_texto),
                            'WKT inválido para {}: {}'.format(descricao, wkt_texto))
                )

            pnt = geom.constGet()

            if not pnt.is3D():
                raise QgsProcessingException(
                    self.tr('{} must be a PointZ geometry: {}'.format(descricao, wkt_texto),
                            '{} deve ser uma geometria PointZ: {}'.format(descricao, wkt_texto))
                )

            try:
                float(pnt.z())
            except:
                raise QgsProcessingException(
                    self.tr('Invalid Z coordinate in {}: {}'.format(descricao, wkt_texto),
                            'Coordenada Z inválida em {}: {}'.format(descricao, wkt_texto))
                )

            return geom


    def processAlgorithm(self, parameters, context, feedback):

        layer = self.parameterAsSource(
            parameters,
            self.INPUT,
            context
        )
        if layer is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.INPUT))
        if layer.wkbType() != QgsWkbTypes.PointZ:
            raise QgsProcessingException(self.tr('Input points layer must be of type PointZ!', 'Camada de pontos de entrada deve ser do tipo PointZ!'))

        # Transformação para o SGR da camada
        SRC = layer.sourceCrs()
        GRS = QgsCoordinateReferenceSystem(SRC.geographicCrsAuthId())
        transf_layer = QgsCoordinateTransform()
        transf_layer.setDestinationCrs(GRS)
        transf_layer.setSourceCrs(SRC)

        BaseCRS = self.parameterAsCrs(parameters, self.CRS, context)
        transf_pnt = QgsCoordinateTransform()
        transf_pnt.setDestinationCrs(GRS)
        transf_pnt.setSourceCrs(BaseCRS)

        base_wkt = self.parameterAsString(parameters, self.BASE_RTK, context).strip()
        base = self.ValidarPointZ_WKT(base_wkt, self.tr('initial base', 'base inicial'))
        base.transform(transf_pnt)

        ppp_wkt = self.parameterAsString(parameters, self.PPP, context).strip()
        ppp = self.ValidarPointZ_WKT(ppp_wkt, self.tr('post-processed base', 'base pós-processada'))
        ppp.transform(transf_pnt)

        sigma_x_base_raw = parameters.get(self.SIGMA_X_BASE)
        sigma_y_base_raw = parameters.get(self.SIGMA_Y_BASE)
        sigma_z_base_raw = parameters.get(self.SIGMA_Z_BASE)

        sigma_x_base = self.parameterAsDouble(parameters, self.SIGMA_X_BASE, context) if sigma_x_base_raw not in [None, ''] else None
        sigma_y_base = self.parameterAsDouble(parameters, self.SIGMA_Y_BASE, context) if sigma_y_base_raw not in [None, ''] else None
        sigma_z_base = self.parameterAsDouble(parameters, self.SIGMA_Z_BASE, context) if sigma_z_base_raw not in [None, ''] else None

        sigma_x_rover_field = self.parameterAsString(parameters, self.SIGMA_X_ROVER, context)
        sigma_y_rover_field = self.parameterAsString(parameters, self.SIGMA_Y_ROVER, context)
        sigma_z_rover_field = self.parameterAsString(parameters, self.SIGMA_Z_ROVER, context)


        # Validate that if any sigma is filled, then all must be filled for both base and rover
        base_group = [sigma_x_base, sigma_y_base, sigma_z_base]
        rover_group = [sigma_x_rover_field, sigma_y_rover_field, sigma_z_rover_field]

        base_any = any(v not in [None, ''] for v in base_group)
        base_all = all(v not in [None, ''] for v in base_group)

        rover_any = any(v not in [None, ''] for v in rover_group)
        rover_all = all(v not in [None, ''] for v in rover_group)

        propagate_sigmas = False

        if base_any or rover_any:
            if not (base_all and rover_all):
                raise QgsProcessingException(
                    self.tr(
                        'To propagate variances, all base and rover sigmas must be filled in (X, Y and Z).',
                        'Para propagar as variâncias, todos os sigmas da base e do rover devem ser preenchidos (X, Y e Z).'
                    )
                )
            propagate_sigmas = True

        report = self.parameterAsFileOutput(
            parameters,
            self.REPORT,
            context
        )

        # Novos atributos
        Fields = layer.fields()
        itens  = {
            self.tr('lon_adjusted', 'lon_ajustada') : QMetaType.Double,
            self.tr('lat_adjusted', 'lat_ajustada') : QMetaType.Double,
            self.tr('h_adjusted', 'h_ajustada') : QMetaType.Double,
        }
        if propagate_sigmas:
            itens[self.tr('sigma_x_adj', 'sigma_x_ajust')] = QMetaType.Double
            itens[self.tr('sigma_y_adj', 'sigma_y_ajust')] = QMetaType.Double
            itens[self.tr('sigma_z_adj', 'sigma_z_ajust')] = QMetaType.Double
        for item in itens:
            Fields.append(QgsField(item, itens[item]))

        (sink, dest_id) = self.parameterAsSink( parameters, self.OUTPUT, context, Fields, QgsWkbTypes.PointZ, GRS)
        if sink is None:
            raise QgsProcessingException(self.invalidSinkError(parameters, self.OUTPUT))


        # Parâmetros a e f do elipsoide
        ellipsoid_id = GRS.ellipsoidAcronym()
        ellipsoid = QgsEllipsoidUtils.ellipsoidParameters(ellipsoid_id)
        a = ellipsoid.semiMajor
        f_inv = ellipsoid.inverseFlattening
        f=1/f_inv
        feedback.pushInfo((self.tr('Semi major axis: {}', 'Semi-eixo maior: {}')).format(str(a)))
        feedback.pushInfo((self.tr('Inverse flattening: {}', 'Achatamento (inverso): {}')).format(str(f_inv)))

        # Cálculo das Deltas Geocêntricos
        pnt_ini = base.constGet()
        X_ini, Y_ini, Z_ini = geod2geoc(pnt_ini.x(), pnt_ini.y(), pnt_ini.z(), a, f)

        pnt_fim = ppp.constGet()
        X_fim, Y_fim, Z_fim = geod2geoc(pnt_fim.x(), pnt_fim.y(), pnt_fim.z(), a, f)

        delta_X = X_fim - X_ini
        delta_Y = Y_fim - Y_ini
        delta_Z = Z_fim - Z_ini
        DELTA = sqrt(delta_X**2 + delta_Y**2 + delta_Z**2)
        delta_E, delta_N, delta_U = geoc2enu(
            X_fim, Y_fim, Z_fim,
            pnt_ini.x(), pnt_ini.y(),
            X_ini, Y_ini, Z_ini, Fo=array([[0],[0],[0]])
            )
        DELTA_Hz = sqrt(delta_E**2 + delta_N**2)
       
        feedback.pushInfo((self.tr('Geocentric delta X: {:.4f} m', 'Delta geocêntrico em X: {:.4f} m')).format(delta_X))
        feedback.pushInfo((self.tr('Geocentric delta Y: {:.4f} m', 'Delta geocêntrico em Y: {:.4f} m')).format(delta_Y))
        feedback.pushInfo((self.tr('Geocentric delta Z: {:.4f} m', 'Delta geocêntrico em Z: {:.4f} m')).format(delta_Z))
        feedback.pushInfo((self.tr('Geocentric Delta 3D: {:.4f} m', 'Delta geocêntrico total (3D): {:.4f} m')).format(DELTA))
        feedback.pushInfo((self.tr('Topocentric delta E: {:.4f} m', 'Delta topocêntrico em E: {:.4f} m')).format(delta_E))
        feedback.pushInfo((self.tr('Topocentric delta N: {:.4f} m', 'Delta topocêntrico em N: {:.4f} m')).format(delta_N))
        feedback.pushInfo((self.tr('Topocentric delta U: {:.4f} m', 'Delta topocêntrico em U: {:.4f} m')).format(delta_U))
        feedback.pushInfo((self.tr('Topocentric horizontal delta: {:.4f} m', 'Delta horizontal topocêntrico: {:.4f} m')).format(DELTA_Hz))

        if DELTA_Hz > 20:
            raise QgsProcessingException(self.tr('Base correction above expected value. Check the initial and final base coordinates!',
                                                 'Correção da base acima do esperado. Verifique as coordenadas inicial e final da base!'))
        

        def format_num(precision):
            return '{:,.Xf}'.replace('X', str(precision))

        report_rows = []
        sigma_x_vals = []
        sigma_y_vals = []
        sigma_z_vals = []

        # Aplicação das correções  na camada de pontos
        total = 100.0 / layer.featureCount() if layer.featureCount() else 0
        feature = QgsFeature()
        for current, feat in enumerate(layer.getFeatures()):
            geom = feat.geometry()
            geom.transform(transf_layer)
            pnt = geom.constGet()
            X, Y, Z = geod2geoc(pnt.x(), pnt.y(), pnt.z(), a, f)
            X_novo = X + delta_X
            Y_novo = Y + delta_Y
            Z_novo = Z + delta_Z
            lon, lat, h = geoc2geod(X_novo, Y_novo, Z_novo, a, f)

            if propagate_sigmas:
                sigma_x_rover = feat[sigma_x_rover_field]
                sigma_y_rover = feat[sigma_y_rover_field]
                sigma_z_rover = feat[sigma_z_rover_field]
                
                if sigma_x_rover in [None, ''] or sigma_y_rover in [None, ''] or sigma_z_rover in [None, '']:
                    raise QgsProcessingException(
                        self.tr(
                            'Feature ID {} has null/empty rover sigma values.'.format(feat.id()),
                            'A feição ID {} possui sigmas do rover nulos/vazios.'.format(feat.id())
                        )
                    )
                try:
                    sigma_x_rover = float(str(sigma_x_rover).replace(',', '.'))
                    sigma_y_rover = float(str(sigma_y_rover).replace(',', '.'))
                    sigma_z_rover = float(str(sigma_z_rover).replace(',', '.'))
                except:
                    raise QgsProcessingException(
                        self.tr(
                            'Feature ID {} has invalid rover sigma values.'.format(feat.id()),
                            'A feição ID {} possui sigmas do rover inválidos.'.format(feat.id())
                        )
                    )
                for valor, nome in [
                    (sigma_x_rover, self.tr('Rover sigma X', 'Sigma X do rover')),
                    (sigma_y_rover, self.tr('Rover sigma Y', 'Sigma Y do rover')),
                    (sigma_z_rover, self.tr('Rover sigma Z', 'Sigma Z do rover')),
                ]:
                    if abs(valor) > 1.0:
                        raise QgsProcessingException(
                            self.tr(
                                'Feature ID {} has {} greater than {} m.',
                                'A feição ID {} possui {} maior que {} m.'
                            ).format(feat.id(), nome, 1.0)
                        )
                sigma_x_adj = sqrt(sigma_x_base**2 + sigma_x_rover**2)
                sigma_y_adj = sqrt(sigma_y_base**2 + sigma_y_rover**2)
                sigma_z_adj = sqrt(sigma_z_base**2 + sigma_z_rover**2)

            new_geom = QgsGeometry(QgsPoint(lon, lat, h))
            feature.setGeometry(new_geom)
            att = feat.attributes() + [float(lon), float(lat), float(h)]
            if propagate_sigmas:
                att += [float(sigma_x_adj), float(sigma_y_adj), float(sigma_z_adj)]
            feature.setAttributes( att )
            sink.addFeature(feature, QgsFeatureSink.FastInsert)

            # Guardar dados para o relatório
            row = [
                str(feat.id()),
                format_num(8).format(float(lon)),
                format_num(8).format(float(lat)),
                format_num(8).format(float(h))
            ]
            if propagate_sigmas:
                row += [
                    format_num(4).format(float(sigma_x_adj)),
                    format_num(4).format(float(sigma_y_adj)),
                    format_num(4).format(float(sigma_z_adj))
                ]
            report_rows.append(row)
            if propagate_sigmas:
                sigma_x_vals.append(float(sigma_x_adj))
                sigma_y_vals.append(float(sigma_y_adj))
                sigma_z_vals.append(float(sigma_z_adj))

            if feedback.isCanceled():
                break
            feedback.setProgress(int((current+1) * total))

        # Gerar relatório HTML
        feedback.pushInfo(self.tr('Generating HTML report...', 'Gerando relatório HTML...'))

        def SummaryTable(rows, propagate_sigmas):
            tabela = '''<table style="margin: 0px;" border="1" cellpadding="4" cellspacing="0">
              <tbody>
                <tr>
                  <td style="text-align: center; font-weight: bold;">{}</td>
                  <td style="text-align: center; font-weight: bold;">Lon</td>
                  <td style="text-align: center; font-weight: bold;">Lat</td>
                  <td style="text-align: center; font-weight: bold;">h</td>'''.format(
                      str2HTML(self.tr('ID', 'ID'))
                  )

            if propagate_sigmas:
                tabela += '''
                  <td style="text-align: center; font-weight: bold;">&sigma;X</td>
                  <td style="text-align: center; font-weight: bold;">&sigma;Y</td>
                  <td style="text-align: center; font-weight: bold;">&sigma;Z</td>'''

            tabela += '''
                </tr>'''

            for row in rows:
                tabela += '<tr>'
                for cell in row:
                    tabela += '<td style="text-align: center;">{}</td>'.format(str2HTML(str(cell)))
                tabela += '</tr>'

            tabela += '''
              </tbody>
            </table>'''
            return tabela


        def WarningBlock():
            notas = []

            notas.append(
                self.tr(
                    'The base correction vector has a geocentric magnitude of {:.3f} m and a local horizontal magnitude of {:.3f} m.'.format(DELTA, DELTA_Hz),
                    'O vetor de correção da base possui magnitude geocêntrica de {:.3f} m e magnitude horizontal local de {:.3f} m.'.format(DELTA, DELTA_Hz)
                )
            )

            if propagate_sigmas:
                notas.append(
                    self.tr(
                        'Variance propagation was performed using a simplified model, assuming independence between base and rover uncertainties.',
                        'A propagação das variâncias foi realizada por um modelo simplificado, assumindo independência entre as incertezas da base e do rover.'
                    )
                )
            else:
                notas.append(
                    self.tr(
                        'Variance propagation was not applied. The precisions of corrected points were not updated according to the base precision.',
                        'A propagação das variâncias não foi aplicada. As precisões dos pontos corrigidos não foram atualizadas em função da precisão da base.'
                    )
                )

            return '<br>'.join([str2HTML(txt) for txt in notas])

        if propagate_sigmas:
            SX = array(sigma_x_vals)
            SY = array(sigma_y_vals)
            SZ = array(sigma_z_vals)

            variance_text = '''
&nbsp;&nbsp;&nbsp; <b>{}</b><br>
&nbsp;&nbsp;&nbsp; &sigma;X ({}) = {} m<br>
&nbsp;&nbsp;&nbsp; &sigma;Y ({}) = {} m<br>
&nbsp;&nbsp;&nbsp; &sigma;Z ({}) = {} m<br><br>
{}'''.format(
                str2HTML(self.tr('Base precision', 'Precisão da base')),
                str2HTML(self.tr('base', 'base')),
                format_num(3).format(float(sigma_x_base)),
                str2HTML(self.tr('base', 'base')),
                format_num(3).format(float(sigma_y_base)),
                str2HTML(self.tr('base', 'base')),
                format_num(3).format(float(sigma_z_base)),
                str2HTML(self.tr(
                    'The final standard deviation of each rover point was computed by combining base and rover sigmas.',
                    'O desvio-padrão final de cada ponto rover foi calculado pela combinação dos sigmas da base e do rover.'
                ))
            )

            variance_formula = '''
&nbsp;&nbsp;&nbsp; <b>{}</b><br>
&nbsp;&nbsp;&nbsp; 
$$
\\sigma_{{final}} = \\sqrt{{\\sigma_{{base}}^2 + \\sigma_{{rover}}^2}}
$$
<br><br>
&nbsp;&nbsp;&nbsp; {}'''.format(
                str2HTML(self.tr('Propagation model', 'Modelo de propagação')),
                str2HTML(self.tr(
                    'This approach ensures that the final rover precision is not better than the base precision.',
                    'Essa abordagem garante que a precisão final dos pontos rover não seja superior à precisão da base.'
                ))
            )

            variance_stats = '''
&nbsp;&nbsp;&nbsp; <b>{}</b><br>
&nbsp;&nbsp;&nbsp; &sigma;X &rarr; {}: {} m | {}: {} m | {}: {} m<br>
&nbsp;&nbsp;&nbsp; &sigma;Y &rarr; {}: {} m | {}: {} m | {}: {} m<br>
&nbsp;&nbsp;&nbsp; &sigma;Z &rarr; {}: {} m | {}: {} m | {}: {} m<br>'''.format(
                str2HTML(self.tr('Adjusted sigma statistics', 'Estatísticas dos sigmas ajustados')),
                str2HTML(self.tr('minimum', 'mínimo')), format_num(3).format(float(SX.min())),
                str2HTML(self.tr('mean', 'média')), format_num(3).format(float(SX.mean())),
                str2HTML(self.tr('maximum', 'máximo')), format_num(3).format(float(SX.max())),
                str2HTML(self.tr('minimum', 'mínimo')), format_num(3).format(float(SY.min())),
                str2HTML(self.tr('mean', 'média')), format_num(3).format(float(SY.mean())),
                str2HTML(self.tr('maximum', 'máximo')), format_num(3).format(float(SY.max())),
                str2HTML(self.tr('minimum', 'mínimo')), format_num(3).format(float(SZ.min())),
                str2HTML(self.tr('mean', 'média')), format_num(3).format(float(SZ.mean())),
                str2HTML(self.tr('maximum', 'máximo')), format_num(3).format(float(SZ.max()))
            )
        else:
            variance_text = str2HTML(self.tr(
                'Variance propagation: not applied.',
                'Propagação das variâncias: não aplicada.'
            ))
            variance_formula = ''
            variance_stats = ''

        method_text = str2HTML(self.tr(
            'Rover points were corrected by applying a rigid translation derived from the difference between the geocentric coordinates of the initial base and the post-processed base. The correction vector (ΔX, ΔY, ΔZ) was computed in the geocentric reference frame and applied uniformly to all rover points. The adjusted coordinates were then transformed back to geodetic coordinates. For interpretation purposes, the correction vector is also represented in the local topocentric system (E, N, U).',
            'Os pontos rover foram corrigidos por meio da aplicação de uma translação rígida, derivada da diferença entre as coordenadas geocêntricas da base inicial e da base pós-processada. O vetor de correção (ΔX, ΔY, ΔZ) foi calculado no sistema geocêntrico e aplicado de forma uniforme a todos os pontos rover. As coordenadas ajustadas foram então convertidas de volta para coordenadas geodésicas. Para fins de interpretação, o vetor de correção também é representado no sistema topocêntrico local (E, N, U).'
        ))

        summary_table = SummaryTable(report_rows, propagate_sigmas)
        warning_text = WarningBlock()

        html_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        arq = open(report, 'w', encoding='utf-8')

        texto = '''<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
<html>
<head>
  <meta content="text/html; charset=ISO-8859-1" http-equiv="content-type">
  <title>''' + str2HTML(self.tr('RTK POINTS CORRECTION REPORT', 'RELATÓRIO DE CORREÇÃO DE PONTOS RTK')) + '''</title>
  <link rel = "icon" href = "https://github.com/LEOXINGU/lftools/blob/main/images/lftools.png?raw=true" type = "image/x-icon">
  <meta name="qrichtext" content="1">
  <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
  <script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
</head>
<body style="background-color: rgb(229, 233, 166);">
<div style="text-align: center;"><span style="font-weight: bold;"><br>
    <img height="80" src="data:image/''' + 'png;base64,' + lftools_logo + '''">
</div>

<div style="text-align: center;"><span style="font-weight: bold; text-decoration: underline;">''' + str2HTML(self.tr('RTK POINTS CORRECTION REPORT', 'RELATÓRIO DE CORREÇÃO DE PONTOS RTK')) + '''</span><br>
</div>
<br>

<span style="font-weight: bold;"><br>''' + str2HTML(self.tr('PROCESSING DATA', 'DADOS DO PROCESSAMENTO')) + '''</span><br>
&nbsp;&nbsp;&nbsp; a. ''' + str2HTML(self.tr('Input layer', 'Camada de entrada')) + ''': [input_layer]<br>
&nbsp;&nbsp;&nbsp; b. ''' + str2HTML(self.tr('Processed points', 'Pontos processados')) + ''': [layer_count]<br>
&nbsp;&nbsp;&nbsp; c. ''' + str2HTML(self.tr('Output CRS', 'SRC de saída')) + ''': [crs]<br>
&nbsp;&nbsp;&nbsp; d. ''' + str2HTML(self.tr('Ellipsoid', 'Elipsoide')) + ''': [ellipsoid]<br>
&nbsp;&nbsp;&nbsp; e. ''' + str2HTML(self.tr('Date and time', 'Data e hora')) + ''': [date_time]<br>

<br><hr><br>

<span style="font-weight: bold;">''' + str2HTML(self.tr('BASE COORDINATES', 'COORDENADAS DA BASE')) + '''</span><br><br>
&nbsp;&nbsp;&nbsp; <b>''' + str2HTML(self.tr('Initial base coordinates', 'Coordenadas iniciais da base')) + '''</b><br>
&nbsp;&nbsp;&nbsp; &nbsp;&nbsp;&nbsp; Lon: [base_lon_ini]<br>
&nbsp;&nbsp;&nbsp; &nbsp;&nbsp;&nbsp; Lat: [base_lat_ini]<br>
&nbsp;&nbsp;&nbsp; &nbsp;&nbsp;&nbsp; h: [base_h_ini] m<br>
<br>
&nbsp;&nbsp;&nbsp; <b>''' + str2HTML(self.tr('Post-processed base coordinates', 'Coordenadas pós-processadas da base')) + '''</b><br>
&nbsp;&nbsp;&nbsp; &nbsp;&nbsp;&nbsp; Lon: [base_lon_ppp]<br>
&nbsp;&nbsp;&nbsp; &nbsp;&nbsp;&nbsp; Lat: [base_lat_ppp]<br>
&nbsp;&nbsp;&nbsp; &nbsp;&nbsp;&nbsp; h: [base_h_ppp] m<br>

<br><hr><br>

<span style="font-weight: bold;">''' + str2HTML(self.tr('APPLIED CORRECTION', 'CORREÇÃO APLICADA')) + '''</span><br><br>
&nbsp;&nbsp;&nbsp; <b>''' + str2HTML(self.tr('Geocentric correction', 'Correção geocêntrica')) + '''</b><br>
&nbsp;&nbsp;&nbsp; &Delta;X: [delta_x] m<br>
&nbsp;&nbsp;&nbsp; &Delta;Y: [delta_y] m<br>
&nbsp;&nbsp;&nbsp; &Delta;Z: [delta_z] m<br>
&nbsp;&nbsp;&nbsp; &Delta;3D: [delta_3d] m<br><br>

&nbsp;&nbsp;&nbsp; <b>''' + str2HTML(self.tr('Local topocentric representation', 'Representação topocêntrica local')) + '''</b><br>
&nbsp;&nbsp;&nbsp; &Delta;E: [delta_e] m<br>
&nbsp;&nbsp;&nbsp; &Delta;N: [delta_n] m<br>
&nbsp;&nbsp;&nbsp; &Delta;U: [delta_u] m<br>
&nbsp;&nbsp;&nbsp; &Delta;Hz: [delta_h] m<br>

<br><hr><br>

<span style="font-weight: bold;">''' + str2HTML(self.tr('METHODOLOGY', 'METODOLOGIA')) + '''</span><br>
[method_text]

<br><br><hr><br>

<span style="font-weight: bold;">''' + str2HTML(self.tr('VARIANCE PROPAGATION', 'PROPAGAÇÃO DAS VARIÂNCIAS')) + '''</span><br><br>
[variance_text]
<br><br>
[variance_formula]
<br><br>
[variance_stats]

<br><hr><br>

<span style="font-weight: bold;">''' + str2HTML(self.tr('TECHNICAL NOTES', 'OBSERVAÇÕES TÉCNICAS')) + '''</span><br>
[warning_text]

<br><hr><br>

<span style="font-weight: bold;">''' + str2HTML(self.tr('FINAL ADJUSTED COORDINATES', 'COORDENADAS FINAIS AJUSTADAS')) + '''</span><br><br>
[summary_table]

<br><hr>''' + str2HTML(self.tr('Leandro Franca', 'Leandro França')) + ''' 2026<br>
<address><font size="+l">''' + str2HTML(self.tr('Cartographic Engineer', 'Eng. Cartógrafo')) + '''<br>
email: contato@geoone.com.br<br>
</font>
</address>
</body>
</html>
        '''

        valores = {
            '[input_layer]': str2HTML(layer.sourceName()),
            '[layer_count]': str(layer.featureCount()),
            '[crs]': str2HTML(GRS.authid() + ' - ' + GRS.description() if GRS.isValid() else ''),
            '[ellipsoid]': str2HTML('{}, a = {} m, 1/f = {}'.format(
                                                                        ellipsoidFromCRS(GRS),
                                                                        ellipsoid.semiMajor,
                                                                        ellipsoid.inverseFlattening
                                    )
                                ),
            '[date_time]': str2HTML(html_time),

            '[base_lon_ini]': format_num(8).format(float(pnt_ini.x())) + '  |  ' + str2HTML(dd2dms(pnt_ini.x(), 4)),
            '[base_lat_ini]': format_num(8).format(float(pnt_ini.y())) + '  |  ' + str2HTML(dd2dms(pnt_ini.y(), 4)),
            '[base_h_ini]': format_num(3).format(float(pnt_ini.z())),

            '[base_lon_ppp]': format_num(8).format(float(pnt_fim.x())) + '  |  ' + str2HTML(dd2dms(pnt_fim.x(), 4)),
            '[base_lat_ppp]': format_num(8).format(float(pnt_fim.y())) + '  |  ' + str2HTML(dd2dms(pnt_fim.y(), 4)),
            '[base_h_ppp]': format_num(3).format(float(pnt_fim.z())),

            '[delta_x]': format_num(3).format(float(delta_X)),
            '[delta_y]': format_num(3).format(float(delta_Y)),
            '[delta_z]': format_num(3).format(float(delta_Z)),
            '[delta_3d]': format_num(3).format(float(DELTA)),
            '[delta_e]': format_num(3).format(float(delta_E)),
            '[delta_n]': format_num(3).format(float(delta_N)),
            '[delta_u]': format_num(3).format(float(delta_U)),
            '[delta_h]': format_num(3).format(float(DELTA_Hz)),

            '[method_text]': method_text,
            '[variance_text]': variance_text,
            '[variance_formula]': variance_formula,
            '[variance_stats]': variance_stats,
            '[warning_text]': warning_text,
            '[summary_table]': summary_table,
        }

        for valor in valores:
            texto = texto.replace(valor, valores[valor])

        arq.write(texto)
        arq.close()

        feedback.pushInfo(self.tr('Operation completed successfully!', 'Operação finalizada com sucesso!'))
        feedback.pushInfo(self.tr('Leandro Franca - Cartographic Engineer', 'Leandro França - Eng Cart'))

        return {self.OUTPUT: dest_id,
                self.REPORT: report}
