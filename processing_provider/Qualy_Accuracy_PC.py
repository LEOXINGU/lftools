# -*- coding: utf-8 -*-

"""
Qualy_Accuracy_PC.py
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
__date__ = '2026-09-26'
__copyright__ = '(C) 2026, Leandro França'

from qgis.PyQt.QtCore import QMetaType
from qgis.core import *
from numpy import sqrt, array, mean, std, pi, sin
import numpy as np
from datetime import datetime
import base64
from io import BytesIO
from lftools.geocapt.imgs import *
from lftools.translations.translate import translate
from lftools.geocapt.topogeo import str2HTML
from lftools.geocapt.cartography import PEC
import os
from itertools import combinations
from qgis.PyQt.QtGui import QIcon, QColor, QFont
import processing
from lftools.dependencies import (
                                    ensure_scipy,
                                    ensure_pyplot
                                )


class Accuracy_PC(QgsProcessingAlgorithm):

    CHECKPOINTS = 'CHECKPOINTS'
    FIELD = 'FIELD'
    CLOUD = 'CLOUD'
    DISTFILTER = 'DISTFILTER'
    METHOD = 'METHOD'
    IDW_POWER = 'IDW_POWER'
    CRS = 'CRS'
    DECIMAL = 'DECIMAL'
    OUTPUT = 'OUTPUT'
    HTML = 'HTML'

    def createInstance(self):
        return Accuracy_PC()

    def name(self):
        return 'Accuracy_PC'.lower()

    def displayName(self):
        return self.tr('Point Cloud positional accuracy', 'Acurácia posicional de Nuvem de Pontos')

    def group(self):
        return self.tr('Quality','Qualidade')

    def groupId(self):
        return 'quality'

    LOC = QgsApplication.locale()[:2]

    def tr(self, *string):
        return translate(string, self.LOC)

    def tags(self):
        return 'GeoOne,PEC,PEC-PCD,qualidade,padrão,rmse,remq,checkpoints,gcps,exactness,point cloud,PC,nuvem de pontos,precision,precisão,tendência,tendency,correctness,accuracy,acurácia,discrepância,discrepancy,vector,deltas,3d,vertical,altimétrico,altimetric,cqdg,asprs'.split(',')

    def icon(self):
        return QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images/quality.png'))

    txt_en = '''This tool can be used to evaluate the <b>altimetric (Z) positional accuracy</b> of point clouds.
<b>Elevation extraction methods</b>
1. Nearest point in 3D distance (default).
2. IDW using the three nearest points in horizontal distance.
3. Local plane/TIN formed by three non-collinear points surrounding the checkpoint.
<b>Outputs</b>
1. <b>Vertical discrepancies</b> between the elevation estimated from the point cloud and the reference elevation.
2. <b>Accuracy report</b>: Cartographic Accuracy Standard report containing RMSE results and classification according to the PEC-PCD.
<b>Input Requirements:</b>
 - Indexed LAS/LAZ point cloud with a valid projected CRS
 - Point layer with an altitude (Z) field
The optional CRS parameter is used to define the projected calculation CRS when the reference point layer is not projected. It must match the point-cloud CRS.'''
    
    txt_pt = '''Esta ferramenta pode ser utilizada para avaliar a acurácia posicional altimétrica (Z) de nuvem de pontos.
<b>Métodos de extração da altitude:</b>
1. Ponto mais próximo em distância 3D (padrão).
2. IDW com os três pontos mais próximos em distância horizontal.
3. Plano local/TIN formado por três pontos não colineares envolvendo o checkpoint.
<b>Saídas:</b>
1. Discrepâncias verticais entre a altitude estimada na nuvem e a altitude de referência.
2. Relatório do Padrão de Exatidão Cartográfica com resultado da REMQ e classificação do PEC-PCD.
<b>Requisitos de Entrada:</b>
- Nuvem LAS/LAZ indexada, com SRC projetado válido
- Camada de pontos com campo de altitude (Z)
O parâmetro SRC opcional é utilizado para definir o SRC projetado dos cálculos quando a camada de pontos de referência não estiver projetada. Ele deve coincidir com o SRC da nuvem.'''
    
    figure = 'images/tutorial/qualy_pc.jpg'

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

        self.addParameter(
            QgsProcessingParameterPointCloudLayer(
                self.CLOUD,
                self.tr('Point cloud (LAS/LAZ)', 'Nuvem de pontos (LAS/LAZ)')
            )
        )

        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.CHECKPOINTS,
                self.tr('Reference points', 'Pontos de referência'),
                [Qgis.ProcessingSourceType.TypeVectorPoint]
            )
        )
        
        self.addParameter(
            QgsProcessingParameterField(
                self.FIELD,
                self.tr('Reference altitude', 'Altitude de referência'),
                parentLayerParameterName=self.CHECKPOINTS,
                type=Qgis.ProcessingFieldParameterDataType.Numeric
            )
        )
        
        self.addParameter(
            QgsProcessingParameterNumber(
                self.DISTFILTER,
                self.tr('Maximum horizontal search radius (m)', 'Raio máximo de busca horizontal (m)'),
                QgsProcessingParameterNumber.Type.Double,
                defaultValue = 1.2,
                minValue = 0
                )
            )

        self.addParameter(
            QgsProcessingParameterEnum(
                self.METHOD,
                self.tr('Cloud elevation extraction method', 'Método de extração da altitude da nuvem'),
                options=[
                    self.tr('Nearest point — 3D distance', 'Ponto mais próximo — distância 3D'),
                    self.tr('Three nearest points — horizontal IDW', 'Três pontos mais próximos — IDW horizontal'),
                    self.tr('Local plane/TIN — three non-collinear points', 'Plano local/TIN — três pontos não colineares')
                ],
                defaultValue=0
            )
        )

        self.addParameter(
            QgsProcessingParameterNumber(
                self.IDW_POWER,
                self.tr('IDW power', 'Potência do IDW'),
                QgsProcessingParameterNumber.Type.Double,
                defaultValue=2.0,
                minValue=0.1
            )
        )
        
        self.addParameter(
            QgsProcessingParameterCrs(
                self.CRS,
                self.tr('CRS', 'SRC'),
                # QgsProject.instance().crs(),
                optional = True
                )
            )

        self.addParameter(
            QgsProcessingParameterNumber(
                self.DECIMAL,
                self.tr('Decimal places', 'Casas decimais'),
                QgsProcessingParameterNumber.Type.Integer,
                defaultValue = 3,
                minValue = 0
                )
            )
        
        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT,
                self.tr('Point Cloud Discrepancies', 'Discrepâncias da Nuvem de Pontos')
            )
        )

        self.addParameter(
            QgsProcessingParameterFileDestination(
                self.HTML,
                self.tr('Accuracy Report of the Point Cloud', 'Relatório de Acurácia da nuvem de pontos'),
                self.tr('HTML files (*.html)')
            )
        )


    def processAlgorithm(self, parameters, context, feedback):

        scipy_stats = ensure_scipy(feedback)
        plt = ensure_pyplot(feedback)
        
        source = self.parameterAsSource(
            parameters,
            self.CHECKPOINTS,
            context
        )
        if source is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.CHECKPOINTS))
            
        campo = self.parameterAsFields(
            parameters,
            self.FIELD,
            context
        )
        if campo is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.FIELD))
        
        columnIndex = source.fields().indexFromName(campo[0])
        
        cloud_layer = self.parameterAsPointCloudLayer(
            parameters,
            self.CLOUD,
            context
        )
        if cloud_layer is None or not cloud_layer.isValid():
            raise QgsProcessingException(self.invalidSourceError(parameters, self.CLOUD))
        
        distProx = self.parameterAsDouble(
            parameters,
            self.DISTFILTER,
            context
        )
        if distProx is None or distProx<=0:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.DISTFILTER))

        method = self.parameterAsEnum(parameters, self.METHOD, context)
        idw_power = self.parameterAsDouble(parameters, self.IDW_POWER, context)

        method_names = [
            self.tr('Nearest point — 3D distance', 'Ponto mais próximo — distância 3D'),
            self.tr('Three nearest points — horizontal IDW', 'Três pontos mais próximos — IDW horizontal'),
            self.tr('Local plane/TIN — three non-collinear points', 'Plano local/TIN — três pontos não colineares')
        ]
        method_name = method_names[method]

        method_descriptions = [
            self.tr(
                'For each checkpoint, the point with the shortest three-dimensional distance is selected among the point-cloud points contained in the horizontal search radius. This method preserves the discrete three-dimensional character of the point cloud and is the default method.',
                'Para cada checkpoint, seleciona-se o ponto de menor distância tridimensional entre os pontos da nuvem contidos no raio horizontal de busca. Este método preserva o caráter tridimensional discreto da nuvem de pontos e constitui o método padrão.'
            ),
            self.tr(
                'For each checkpoint, the three nearest point-cloud points are selected by horizontal distance within the search radius. Elevation is estimated by inverse distance weighting (IDW) at the checkpoint XY position. Checkpoints with fewer than three candidates are not included in the statistics.',
                'Para cada checkpoint, os três pontos da nuvem mais próximos são selecionados pela distância horizontal dentro do raio de busca. A altitude é estimada por ponderação pelo inverso da distância (IDW), na posição XY do checkpoint. Checkpoints com menos de três candidatos não são incluídos nas estatísticas.'
            ),
            self.tr(
                'For each checkpoint, candidate points are selected exclusively by horizontal distance within the search radius. Among the 12 nearest candidates, the algorithm selects the smallest valid triangle that contains the checkpoint and is formed by three non-collinear points. The point-cloud elevation is linearly interpolated on the local plane at the checkpoint XY position. Checkpoints without a valid surrounding triangle are not included in the statistics.',
                'Para cada checkpoint, os pontos candidatos são selecionados exclusivamente pela distância horizontal dentro do raio de busca. Entre os 12 candidatos mais próximos, o algoritmo seleciona o menor triângulo válido que contém o checkpoint e é formado por três pontos não colineares. A altitude da nuvem é interpolada linearmente no plano local, na posição XY do checkpoint. Checkpoints sem um triângulo envolvente válido não são incluídos nas estatísticas.'
            )
        ]
        method_description = method_descriptions[method]
        method_formulas = [
            '$$d_{3D}=\\sqrt{(X_i-X_c)^2+(Y_i-Y_c)^2+(Z_i-Z_c)^2}$$',
            '$$\\widehat{Z}_c=\\frac{\\sum_{i=1}^{3} Z_i/d_{XY,i}^{p}}{\\sum_{i=1}^{3}1/d_{XY,i}^{p}}$$',
            '$$\\widehat{Z}_c = w_1Z_1+w_2Z_2+w_3Z_3, \\qquad w_1+w_2+w_3=1$$'
        ]
        method_formula = method_formulas[method]
        selection_note = self.tr(
            'The vertical discrepancy is calculated as the point-cloud elevation obtained by the selected method minus the reference elevation. In the 3D-distance method, the reference elevation participates in the selection of the nearest point; in the IDW and local-plane methods, support points are selected by horizontal distance.',
            'A discrepância vertical é calculada como a altitude da nuvem obtida pelo método selecionado menos a altitude de referência. No método da distância 3D, a altitude de referência participa da seleção do ponto mais próximo; nos métodos IDW e plano local, os pontos de suporte são selecionados pela distância horizontal.'
        )
        idw_row = ''
        if method == 1:
            idw_row = '<tr><td>{}</td><td>{}</td></tr>'.format(
                str2HTML(self.tr('IDW power', 'Potência do IDW')),
                idw_power
            )

        support_metric = self.tr(
            'Three-dimensional distance to the selected point',
            'Distância tridimensional ao ponto selecionado'
        ) if method == 0 else self.tr(
            'Maximum horizontal distance to the three supporting points',
            'Maior distância horizontal aos três pontos de suporte'
        )
        
        decimal = self.parameterAsInt(
            parameters,
            self.DECIMAL,
            context
        )
        
        out_CRS = self.parameterAsCrs(
            parameters,
            self.CRS,
            context
        )
        
        format_num = '{:,.Xf}'.replace('X', str(decimal))
        def fnum(value):
            try:
                return format_num.format(float(value))
            except Exception:
                return str(value)

        
        Fields = source.fields()
        
        itens  = {
                     'pc_distance' : QMetaType.Type.Double,
                     'pc_npts' : QMetaType.Type.Int,
                     'pc_method' : QMetaType.Type.QString,
                     'pc_h' : QMetaType.Type.Double,
                     'pc_discrep_z' : QMetaType.Type.Double
                     }
        for item in itens:
            Fields.append(QgsField(item, itens[item]))

        
        html_output = self.parameterAsFileOutput(
            parameters, 
            self.HTML, 
            context
        )


        # VALIDAÇÕES
        num_teste = source.featureCount()
        if num_teste < 4:
            raise QgsProcessingException(self.tr('Insufficient number of features for quality evaluation!', 'Número de feições insuficiente para avaliação de qualidade!'))
          
        # A nuvem define obrigatoriamente o SRC dos cálculos.
        cloud_crs = cloud_layer.crs()
        if not cloud_crs.isValid():
            raise QgsProcessingException(self.tr(
                'The point cloud has no valid CRS. Assign the correct CRS or reproject the cloud using the native QGIS point-cloud tools before running this algorithm.',
                'A nuvem de pontos não possui SRC válido. Defina o SRC correto ou reprojete a nuvem com as ferramentas nativas de nuvem de pontos do QGIS antes de executar este algoritmo.'
            ))
        if cloud_crs.isGeographic():
            raise QgsProcessingException(self.tr(
                'The point cloud CRS must be projected. Reproject the cloud using the native QGIS point-cloud tools before running this algorithm.',
                'O SRC da nuvem de pontos deve ser projetado. Reprojete a nuvem com as ferramentas nativas de nuvem de pontos do QGIS antes de executar este algoritmo.'
            ))

        ref_crs = source.sourceCrs()
        SRC = cloud_crs
        coordTransf = False
        coordinateTransf = None

        # O parâmetro SRC é mantido para pontos de referência sem SRC projetado.
        if not ref_crs.isValid():
            if not out_CRS.isValid() or out_CRS.isGeographic():
                raise QgsProcessingException(self.tr(
                    'The reference point layer has no valid projected CRS. Define its projected CRS in the CRS parameter.',
                    'A camada de pontos de referência não possui SRC projetado válido. Defina seu SRC projetado no parâmetro SRC.'
                ))
            if out_CRS != cloud_crs:
                raise QgsProcessingException(self.tr(
                    'The CRS selected for the reference points must match the point-cloud CRS ({}).',
                    'O SRC selecionado para os pontos de referência deve coincidir com o SRC da nuvem de pontos ({}).'
                ).format(cloud_crs.authid()))
            # Sem SRC de origem não há transformação: as coordenadas são interpretadas no SRC informado.
            ref_crs = out_CRS
        elif ref_crs.isGeographic():
            if not out_CRS.isValid() or out_CRS.isGeographic():
                raise QgsProcessingException(self.tr(
                    'The reference point layer is geographic. Select a projected CRS matching the point-cloud CRS in the CRS parameter.',
                    'A camada de pontos de referência está em SRC geográfico. Selecione no parâmetro SRC um SRC projetado coincidente com o da nuvem de pontos.'
                ))
            if out_CRS != cloud_crs:
                raise QgsProcessingException(self.tr(
                    'The CRS selected for the calculations must match the point-cloud CRS ({}).',
                    'O SRC selecionado para os cálculos deve coincidir com o SRC da nuvem de pontos ({}).'
                ).format(cloud_crs.authid()))
            coordinateTransf = QgsCoordinateTransform(ref_crs, cloud_crs, QgsProject.instance())
            coordTransf = ref_crs != cloud_crs
        elif ref_crs != cloud_crs:
            coordinateTransf = QgsCoordinateTransform(ref_crs, cloud_crs, QgsProject.instance())
            coordTransf = True

        (sink, dest_id) = self.parameterAsSink(
            parameters,
            self.OUTPUT,
            context,
            Fields,
            source.wkbType(),
            SRC
        )
        if sink is None:
            raise QgsProcessingException(self.invalidSinkError(parameters, self.OUTPUT))

        dicionario = {'0.5k': '1:500', '1k': '1:1.000', '2k': '1:2.000', '5k': '1:5.000', '10k': '1:10.000', '25k': '1:25.000', '50k': '1:50.000', '100k': '1:100.000', '250k': '1:250.000'}
        
        valores = ['A', 'B', 'C', 'D']
        
        Escalas = [ esc for esc in dicionario]
        
        def horizontal_candidates(x_ref, y_ref):
            radius2 = distProx * distProx
            candidates = []
            for x, y, z in pontos_teste:
                d2 = (x - x_ref)**2 + (y - y_ref)**2
                if d2 <= radius2:
                    candidates.append((d2, x, y, z))
            candidates.sort(key=lambda item: item[0])
            return candidates

        def point_in_triangle(px, py, triangle, tolerance=1e-12):
            (_, x1, y1, _), (_, x2, y2, _), (_, x3, y3, _) = triangle
            denominator = (y2 - y3)*(x1 - x3) + (x3 - x2)*(y1 - y3)
            if abs(denominator) <= tolerance:
                return None
            w1 = ((y2 - y3)*(px - x3) + (x3 - x2)*(py - y3)) / denominator
            w2 = ((y3 - y1)*(px - x3) + (x1 - x3)*(py - y3)) / denominator
            w3 = 1.0 - w1 - w2
            if min(w1, w2, w3) < -1e-10:
                return None
            return w1, w2, w3

        def local_tin_elevation(x_ref, y_ref, candidates):
            # Limita a busca combinatória aos 12 vizinhos horizontais mais próximos.
            nearby = candidates[:12]
            best = None
            for triangle in combinations(nearby, 3):
                weights = point_in_triangle(x_ref, y_ref, triangle)
                if weights is None:
                    continue
                support = max(np.sqrt(item[0]) for item in triangle)
                if best is None or support < best[0]:
                    z_est = sum(weight * item[3] for weight, item in zip(weights, triangle))
                    best = (support, z_est)
            return best
        
        
        # Número de pontos da nuvem de entrada
        total_pnts = cloud_layer.pointCount()
        feedback.pushInfo(self.tr('Total number of points: ', 'Número total de pontos: ') + '{}'.format(total_pnts))

        # Prepara os pontos de referência e uma única cobertura de recorte formada
        # pela união dos buffers correspondentes ao raio de busca.
        feedback.pushInfo(self.tr('Extracting local point-cloud neighborhoods...', 'Extraindo vizinhanças locais da nuvem de pontos...'))
        pontos_ref = []
        buffer_geometries = []
        for feat in source.getFeatures():
            geom = feat.geometry()
            if geom is None or geom.isNull() or geom.isEmpty():
                continue
            if coordTransf:
                geom.transform(coordinateTransf)
            pnt = geom.asPoint()
            x_ref, y_ref = pnt.x(), pnt.y()
            pontos_ref.append([x_ref, y_ref])
            buffer_geometries.append(
                QgsGeometry.fromPointXY(QgsPointXY(x_ref, y_ref)).buffer(distProx, 16)
            )

        if not buffer_geometries:
            raise QgsProcessingException(self.tr(
                'No valid reference point geometry was found.',
                'Nenhuma geometria válida de ponto de referência foi encontrada.'
            ))

        if QgsApplication.processingRegistry().algorithmById('pdal:clip') is None or \
           QgsApplication.processingRegistry().algorithmById('pdal:exportvector') is None:
            raise QgsProcessingException(self.tr(
                'The native QGIS PDAL algorithms are unavailable. Install a QGIS build with PDAL support and enable the PDAL provider.',
                'Os algoritmos PDAL nativos do QGIS não estão disponíveis. Instale uma distribuição do QGIS com suporte ao PDAL e habilite o provedor PDAL.'
            ))

        overlay = QgsVectorLayer('MultiPolygon?crs={}'.format(cloud_crs.authid()), 'search_neighborhoods', 'memory')
        overlay_feature = QgsFeature()
        overlay_feature.setGeometry(QgsGeometry.unaryUnion(buffer_geometries))
        overlay.dataProvider().addFeature(overlay_feature)
        overlay.updateExtents()

        try:
            clipped_result = processing.run(
                'pdal:clip',
                {
                    'INPUT': cloud_layer,
                    'OVERLAY': overlay,
                    'FILTER_EXPRESSION': '',
                    'FILTER_EXTENT': None,
                    'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
                },
                context=context,
                feedback=feedback,
                is_child_algorithm=True
            )
            vector_result = processing.run(
                'pdal:exportvector',
                {
                    'INPUT': clipped_result['OUTPUT'],
                    'ATTRIBUTE': [],
                    'FILTER_EXPRESSION': '',
                    'FILTER_EXTENT': None,
                    'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
                },
                context=context,
                feedback=feedback,
                is_child_algorithm=True
            )
        except QgsProcessingException:
            raise
        except Exception as e:
            raise QgsProcessingException(self.tr(
                'Could not extract points from the LAS/LAZ cloud: {}',
                'Não foi possível extrair os pontos da nuvem LAS/LAZ: {}'
            ).format(str(e)))

        extracted_layer = QgsProcessingUtils.mapLayerFromString(vector_result['OUTPUT'], context)
        if extracted_layer is None or not extracted_layer.isValid():
            raise QgsProcessingException(self.tr(
                'The temporary point-cloud extraction could not be loaded.',
                'Não foi possível carregar a extração temporária da nuvem de pontos.'
            ))

        pontos_teste = []
        extracted_count = extracted_layer.featureCount()
        total_extract = 100.0 / extracted_count if extracted_count else 0
        for cont, cloud_feat in enumerate(extracted_layer.getFeatures()):
            geom = cloud_feat.geometry()
            if geom is None or geom.isNull() or geom.isEmpty():
                continue
            point = geom.constGet()
            try:
                x, y, z = float(point.x()), float(point.y()), float(point.z())
            except Exception:
                vertex = geom.vertexAt(0)
                x, y, z = float(vertex.x()), float(vertex.y()), float(vertex.z())
            if np.isfinite(x) and np.isfinite(y) and np.isfinite(z):
                pontos_teste.append([x, y, z])
            if feedback.isCanceled():
                break
            feedback.setProgress(int((cont + 1) * total_extract))

        feedback.pushInfo(self.tr(
            'Points extracted in the search neighborhoods: ',
            'Pontos extraídos nas vizinhanças de busca: '
        ) + str(len(pontos_teste)))

        if not pontos_teste:
            raise QgsProcessingException(self.tr(
                'No point-cloud points were found within the search neighborhoods.',
                'Nenhum ponto da nuvem foi encontrado nas vizinhanças de busca.'
            ))
        
        # Cálculo das discrepâncias
        feedback.pushInfo(self.tr('Altimetric calculation...', 'Cálculo das discrepâncias altimétricas...'))
        feedback.pushInfo(self.tr('Elevation extraction method: ', 'Método de extração da altitude: ') + method_name)
        DISCREP = []
        DISTANCES = []
        SKIPPED = 0
        total = 100.0 / source.featureCount() if source.featureCount() else 0
        for w, feat in enumerate(source.getFeatures()):
            geom = feat.geometry()
            if coordTransf:
                geom.transform(coordinateTransf)
            pnt = geom.asPoint()
            z_ref = float(feat[columnIndex])
            att = feat.attributes()
            candidates = horizontal_candidates(pnt.x(), pnt.y())
            z_test = None
            support_distance = None
            used_points = 0
            output_x, output_y = pnt.x(), pnt.y()

            if method == 0 and candidates:
                nearest = min(
                    candidates,
                    key=lambda item: item[0] + (item[3] - z_ref)**2
                )
                support_distance = float(np.sqrt(nearest[0] + (nearest[3] - z_ref)**2))
                z_test = nearest[3]
                output_x, output_y = nearest[1], nearest[2]
                used_points = 1

            elif method == 2 and len(candidates) >= 3:
                result = local_tin_elevation(pnt.x(), pnt.y(), candidates)
                if result is not None:
                    support_distance, z_test = result
                    used_points = 3

            elif method == 1 and len(candidates) >= 3:
                nearest = candidates[:3]
                distances = np.sqrt([item[0] for item in nearest])
                if distances[0] <= 1e-12:
                    z_test = nearest[0][3]
                else:
                    weights = 1.0 / np.power(distances, idw_power)
                    z_test = float(np.sum(weights * np.array([item[3] for item in nearest])) / np.sum(weights))
                support_distance = float(distances.max())
                used_points = 3

            if z_test is None:
                SKIPPED += 1
                feedback.reportError(self.tr(
                    'Checkpoint FID {} was skipped: no valid neighborhood was found within the search radius.',
                    'Checkpoint FID {} foi ignorado: nenhuma vizinhança válida foi encontrada dentro do raio de busca.'
                ).format(feat.id()))
                feedback.setProgress(int((w+1) * total))
                continue

            discrep = z_test - float(z_ref)
            DISCREP += [discrep]
            DISTANCES += [support_distance]
            fet = QgsFeature(Fields)
            fet.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(float(output_x), float(output_y))))
            fet.setAttributes(att + [support_distance, used_points, method_name, float(z_test), float(discrep)])
            sink.addFeature(fet, QgsFeatureSink.Flag.FastInsert)
            if feedback.isCanceled():
                break
            feedback.setProgress(int((w+1) * total))
            
        
        # Gerar relatorio
        feedback.pushInfo(self.tr('Generating accuracy report...', 'Gerando relatório de acurácia...'))

        DISCREP = array(DISCREP, dtype=float)
        DISTANCES = array(DISTANCES, dtype=float)

        if len(DISCREP) < 4:
            raise QgsProcessingException(self.tr(
                'Fewer than four checkpoints had a valid neighborhood for quality evaluation.',
                'Menos de quatro checkpoints apresentaram vizinhança válida para a avaliação de qualidade.'
            ))

        feedback.pushInfo(self.tr('Valid checkpoints: ', 'Checkpoints válidos: ') + str(len(DISCREP)))
        feedback.pushInfo(self.tr('Checkpoints skipped: ', 'Checkpoints ignorados: ') + str(SKIPPED))

        # Estatísticas de Acurácia
        RMSE = sqrt((DISCREP*DISCREP).sum()/len(DISCREP))
        P68 = np.percentile(np.abs(DISCREP), 68)
        P90 = np.percentile(np.abs(DISCREP), 90)
        P95 = np.percentile(np.abs(DISCREP), 95)
        P99 = np.percentile(np.abs(DISCREP), 99)

        MEDIAN = np.median(DISCREP)
        MAD = np.median(np.abs(DISCREP - MEDIAN))
        NMAD = 1.4826 * MAD

        Q1 = np.percentile(DISCREP, 25)
        Q3 = np.percentile(DISCREP, 75)
        IQR = Q3 - Q1
        OUT_LOW = Q1 - 1.5 * IQR
        OUT_HIGH = Q3 + 1.5 * IQR
        OUTLIERS = ((DISCREP < OUT_LOW) | (DISCREP > OUT_HIGH)).sum()
        OUTLIERS_PERC = 100.0 * OUTLIERS / len(DISCREP)

        # Cálculo do PEC-PCD
        RESULTADOS = {}
        for escala in Escalas:
            mudou = False
            for valor in valores[::-1]:
                EM = PEC[escala]['altim'][valor]['EM']
                EP = PEC[escala]['altim'][valor]['EP']
                if (sum(DISCREP<EM)/len(DISCREP))>0.9 and (RMSE < EP):
                    RESULTADOS[escala] = valor
                    mudou = True
            if not mudou:
                RESULTADOS[escala] = 'R'
        
        feedback.pushInfo('RMSE: {}'.format(round(RMSE,3)))
        for result in RESULTADOS:
            feedback.pushInfo('{} ➜ {}'.format(dicionario[result],RESULTADOS[result]))

        # Testes de Normalidade
        shapiro_text = self.tr('SciPy unavailable', 'SciPy indisponível')
        anderson_text = self.tr('SciPy unavailable', 'SciPy indisponível')
        normality_class = self.tr('Not assessed', 'Não avaliada')
        normality_explanation = self.tr(
            'Normality was not assessed because SciPy is unavailable or the sample size is insufficient.',
            'A normalidade não foi avaliada porque o SciPy está indisponível ou o tamanho da amostra é insuficiente.'
        )

        if scipy_stats is not None and len(DISCREP) >= 3:
            try:
                shapiro = scipy_stats.shapiro(DISCREP)
                if shapiro.pvalue > 0.05:
                    shapiro_result = self.tr('Normality not rejected', 'Normalidade não rejeitada')
                    normality_class = self.tr('Compatible with normality', 'Compatível com normalidade')
                    normality_explanation = self.tr(
                        'The Shapiro-Wilk test did not reject the null hypothesis of normality at the 5% significance level (p > 0.05).',
                        'O teste de Shapiro-Wilk não rejeitou a hipótese nula de normalidade ao nível de significância de 5% (p > 0,05).'
                    )
                else:
                    shapiro_result = self.tr('Normality rejected', 'Normalidade rejeitada')
                    normality_class = self.tr('Non-normal', 'Não normal')
                    normality_explanation = self.tr(
                        'The Shapiro-Wilk test rejected the null hypothesis of normality at the 5% significance level (p ≤ 0.05).',
                        'O teste de Shapiro-Wilk rejeitou a hipótese nula de normalidade ao nível de significância de 5% (p ≤ 0,05).'
                    )
                shapiro_text = 'W = {}, p-value = {} ({})'.format(
                    fnum(shapiro.statistic),
                    fnum(shapiro.pvalue),
                    shapiro_result
                )
            except Exception as e:
                shapiro_text = str(e)

            try:
                anderson = scipy_stats.anderson(DISCREP, dist='norm')
                critical_5 = anderson.critical_values[2]
                ad_result = self.tr('below 5% critical value', 'abaixo do valor crítico de 5%') if anderson.statistic < critical_5 else self.tr('above 5% critical value', 'acima do valor crítico de 5%')
                anderson_text = 'A² = {}, critical 5% = {} ({})'.format(
                    fnum(anderson.statistic),
                    fnum(critical_5),
                    ad_result
                )
            except Exception as e:
                anderson_text = str(e)

        # Gráficos do relatório (Histograma e CDF)
        def FigToBase64(fig):
            buffer = BytesIO()
            fig.savefig(buffer, format='png', dpi=200, bbox_inches='tight')
            buffer.seek(0)
            encoded = base64.b64encode(buffer.read()).decode('utf-8')
            try:
                plt.close(fig)
            except Exception:
                pass
            return encoded

        def ChartUnavailableBlock():
            return '<div class="note">' + str2HTML(self.tr(
                'Charts were not generated because Matplotlib is unavailable in the QGIS Python environment.',
                'Os gráficos não foram gerados porque o Matplotlib não está disponível no ambiente Python do QGIS.'
            )) + '</div>'

        def GenerateHistogramBase64():
            if plt is None:
                return None
            try:
                fig, ax = plt.subplots(figsize=(9, 5.2))

                ax.hist(DISCREP, bins='fd', edgecolor='black', alpha=0.75)

                ax.axvline(DISCREP.mean(), linewidth=2,
                           label='Mean = {} m'.format(fnum(DISCREP.mean())))
                ax.axvline(np.median(DISCREP), linewidth=2, linestyle='--',
                           label='Median = {} m'.format(fnum(np.median(DISCREP))))

                ax.axvline(-RMSE, linewidth=1.5, linestyle=':',
                           label='±RMSEz = {} m'.format(fnum(RMSE)))
                ax.axvline(RMSE, linewidth=1.5, linestyle=':')


                ax.axvline(-P95, linewidth=1.5, linestyle=(0, (5, 5)),
                           label='±P95 = {} m'.format(fnum(P95)))
                ax.axvline(P95, linewidth=1.5, linestyle=(0, (5, 5)))

                ax.set_title(self.tr('Histogram of Vertical Residuals (ΔZ)',
                                     'Histograma dos Resíduos Verticais (ΔZ)'))
                ax.set_xlabel(self.tr('Vertical discrepancy ΔZ (m)',
                                      'Discrepância vertical ΔZ (m)'))
                ax.set_ylabel(self.tr('Frequency', 'Frequência'))
                ax.grid(True, alpha=0.25)
                ax.legend(loc='best')
                fig.tight_layout()
                return FigToBase64(fig)
            except Exception as e:
                if feedback:
                    feedback.reportError(self.tr(
                        'Could not generate histogram: {}',
                        'Não foi possível gerar o histograma: {}'
                    ).format(str(e)))
                return None

        def GenerateCDFBase64():
            if plt is None:
                return None
            try:
                abs_errors = np.sort(np.abs(DISCREP))
                cdf = np.arange(1, len(abs_errors) + 1) / len(abs_errors) * 100.0

                fig, ax = plt.subplots(figsize=(9, 5.2))
                ax.plot(abs_errors, cdf, linewidth=2, label='CDF')

                for p_value, label, level in [
                    (P68, 'P68', 68),
                    (P90, 'P90', 90),
                    (P95, 'P95', 95),
                    (P99, 'P99', 99)
                ]:
                    ax.axvline(p_value, linestyle='--', linewidth=1.4)
                    ax.axhline(level, linestyle=':', linewidth=1.0)
                    ax.annotate('{} = {} m'.format(label, fnum(p_value)),
                                xy=(p_value, level),
                                xytext=(5, 5),
                                textcoords='offset points')


                ax.set_title(self.tr('CDF of Absolute Vertical Errors |ΔZ|',
                                     'CDF dos Erros Verticais Absolutos |ΔZ|'))
                ax.set_xlabel(self.tr('Absolute vertical error |ΔZ| (m)',
                                      'Erro vertical absoluto |ΔZ| (m)'))
                ax.set_ylabel(self.tr('Cumulative percentage (%)',
                                      'Percentual acumulado (%)'))
                ax.set_xlim(left=0)
                ax.set_ylim(0, 100)
                ax.grid(True, alpha=0.25)
                ax.legend(loc='best')
                fig.tight_layout()
                return FigToBase64(fig)
            except Exception as e:
                if feedback:
                    feedback.reportError(self.tr(
                        'Could not generate CDF chart: {}',
                        'Não foi possível gerar o gráfico CDF: {}'
                    ).format(str(e)))
                return None

        histogram_b64 = GenerateHistogramBase64()
        cdf_b64 = GenerateCDFBase64()

        histogram_chart = '<img class="chart-img" src="data:image/png;base64,{}">'.format(histogram_b64) if histogram_b64 else ChartUnavailableBlock()
        cdf_chart = '<img class="chart-img" src="data:image/png;base64,{}">'.format(cdf_b64) if cdf_b64 else ChartUnavailableBlock()
        
        # Criacao do arquivo html com os resultados
        arq = open(html_output, 'w', encoding='utf-8')

        texto = '''<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>''' + str2HTML(self.tr('POINT CLOUD POSITIONAL ACCURACY', 'ACURÁCIA POSICIONAL DE NUVEM DE PONTOS')) + '''</title>
  <link rel = "icon" href = "https://github.com/LEOXINGU/lftools/blob/main/images/lftools.png?raw=true" type = "image/x-icon">
  <script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
  <style>
    body { font-family: Arial, sans-serif; background:#f4f6f0; color:#222; margin:0; padding:0; }
    .page { max-width:1100px; margin:24px auto; background:white; padding:32px; border-radius:12px; box-shadow:0 2px 12px rgba(0,0,0,.12); }
    .header { text-align:center; border-bottom:3px solid #365f2c; padding-bottom:16px; margin-bottom:24px; }
    .header img { height:72px; }
    h1 { color:#274e22; font-size:24px; margin:12px 0 4px 0; }
    h2 { color:#365f2c; font-size:18px; border-bottom:1px solid #ddd; padding-bottom:6px; margin-top:28px; }
    .subtitle { color:#666; font-size:13px; }
    .cards { display:grid; grid-template-columns:repeat(4,1fr); gap:12px; margin:20px 0; }
    .card { background:#eef5ea; border-left:5px solid #365f2c; padding:14px; border-radius:8px; }
    .label { color:#666; font-size:12px; text-transform:uppercase; }
    .big { font-size:22px; font-weight:bold; color:#1f3f1b; margin-top:6px; }
    table { width:100%; border-collapse:collapse; margin:12px 0; font-size:13px; }
    th { background:#365f2c; color:white; padding:8px; text-align:left; }
    td { border:1px solid #ddd; padding:8px; }
    tr:nth-child(even) { background:#f8f8f8; }
    .note { background:#fff8dc; border-left:5px solid #c9a227; padding:12px; margin:12px 0; border-radius:6px; }
    .ok { color:#1f7a1f; font-weight:bold; }
    .warn { color:#b36b00; font-weight:bold; }
    .footer { margin-top:30px; border-top:1px solid #ccc; padding-top:12px; color:#555; font-size:12px; }
    .chart-img { width:100%; max-width:900px; display:block; margin:16px auto 8px auto; border:1px solid #ddd; border-radius:8px; }
  </style>
</head>
<body>
<div class="page">

<div class="header">
  <img src="data:image/''' + 'png;base64,' + lftools_logo + '''">
  <h1>''' + str2HTML(self.tr('POINT CLOUD POSITIONAL ACCURACY REPORT', 'RELATÓRIO DE ACURÁCIA POSICIONAL DE NUVEM DE PONTOS')) + '''</h1>
  <div class="subtitle">LFTools | ASPRS-oriented vertical accuracy assessment | ''' + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + '''</div>
</div>

<div class="cards">
  <div class="card"><div class="label">''' + str2HTML(self.tr('Valid checkpoints', 'Checkpoints válidos')) + '''</div><div class="big">[layer_count]</div></div>
  <div class="card"><div class="label">RMSE<sub>Z</sub></div><div class="big">[RMSE_Z] m</div></div>
  <div class="card"><div class="label">''' + str2HTML(self.tr('Mean Error', 'Erro médio')) + '''</div><div class="big">[discrepZ_mean] m</div></div>
  <div class="card"><div class="label">P95 |ΔZ|</div><div class="big">[P95] m</div></div>
</div>

<h2>''' + str2HTML(self.tr('1. Evaluated Data', '1. Dados Avaliados')) + '''</h2>
<table>
<tr><th>''' + str2HTML(self.tr('Item', 'Item')) + '''</th><th>''' + str2HTML(self.tr('Value', 'Valor')) + '''</th></tr>
<tr><td>''' + str2HTML(self.tr('Point cloud', 'Nuvem de pontos')) + '''</td><td>[cloud]</td></tr>
<tr><td>''' + str2HTML(self.tr('Total points in the input cloud', 'Total de pontos na nuvem de entrada')) + '''</td><td>[total_points]</td></tr>
<tr><td>''' + str2HTML(self.tr('Points extracted in the search neighborhoods', 'Pontos extraídos nas vizinhanças de busca')) + '''</td><td>[extracted_points]</td></tr>
<tr><td>''' + str2HTML(self.tr('Reference points', 'Pontos de referência')) + '''</td><td>[layer_name]</td></tr>
<tr><td>''' + str2HTML(self.tr('Input checkpoints', 'Checkpoints de entrada')) + '''</td><td>[input_count]</td></tr>
<tr><td>''' + str2HTML(self.tr('Valid checkpoints', 'Checkpoints válidos')) + '''</td><td>[layer_count]</td></tr>
<tr><td>''' + str2HTML(self.tr('Checkpoints without a valid neighborhood', 'Checkpoints sem vizinhança válida')) + '''</td><td>[skipped]</td></tr>
<tr><td>''' + str2HTML(self.tr('Elevation extraction method', 'Método de extração da altitude')) + '''</td><td>[method]</td></tr>
<tr><td>''' + str2HTML(self.tr('Search radius', 'Raio de busca')) + '''</td><td>[dist_filter] m</td></tr>
[IDW_ROW]
<tr><td>''' + str2HTML(self.tr('Coordinate reference system', 'Sistema de referência')) + '''</td><td>[crs]</td></tr>
</table>

<h2>''' + str2HTML(self.tr('2. Methodology', '2. Metodologia')) + '''</h2>
<p>''' + str2HTML(self.tr(
'The LAS/LAZ cloud was spatially clipped to the union of the checkpoint search neighborhoods using the native QGIS PDAL provider. Only the resulting 3D points were loaded for the calculations; the original point cloud was not modified.',
'A nuvem LAS/LAZ foi recortada espacialmente pela união das vizinhanças de busca dos checkpoints por meio do provedor PDAL nativo do QGIS. Apenas os pontos 3D resultantes foram carregados para os cálculos; a nuvem original não foi modificada.'
)) + '''</p>
<p>[METHOD_DESCRIPTION]</p>
<p>[SELECTION_NOTE]</p>

<div class="note">
[METHOD_FORMULA]
$$\\Delta Z_i = Z_{test,i} - Z_{ref,i}$$
$$RMSE_Z = \\sqrt{\\frac{\\sum_{i=1}^{n}(\\Delta Z_i)^2}{n}}$$
$$MAD = median(|\\Delta_i - median(\\Delta)|)$$
$$NMAD = 1.4826 \\times MAD$$
$$IQR=Q_3-Q_1$$
$$Lower\\ Limit=Q_1-1.5 \\times IQR$$
$$Upper\\ Limit=Q_3+1.5 \\times IQR$$
</div>

<h2>''' + str2HTML(self.tr('3. ASPRS-Oriented Vertical Accuracy Summary', '3. Resumo da Acurácia Vertical orientado pela ASPRS')) + '''</h2>
<table>
<tr><th>Metric</th><th>Value</th><th>Description</th></tr>
<tr><td>Mean Error</td><td>[discrepZ_mean] m</td><td>Vertical bias</td></tr>
<tr><td>Standard Deviation</td><td>[discrepZ_std] m</td><td>Residual dispersion</td></tr>
<tr><td>Minimum ΔZ</td><td>[discrepZ_min] m</td><td>Minimum vertical discrepancy</td></tr>
<tr><td>Maximum ΔZ</td><td>[discrepZ_max] m</td><td>Maximum vertical discrepancy</td></tr>
<tr><td>RMSE<sub>Z</sub></td><td>[RMSE_Z] m</td><td>ASPRS primary vertical accuracy metric</td></tr>
</table>

<h2>''' + str2HTML(self.tr('4. Histogram of Residuals', '4. Histograma dos Resíduos')) + '''</h2>
<p>''' + str2HTML(self.tr(
'The histogram presents the distribution of vertical residuals (ΔZ), including the mean, median, RMSEz and P95 indicators.',
'O histograma apresenta a distribuição dos resíduos verticais (ΔZ), incluindo os indicadores de média, mediana, RMSEz e P95.'
)) + '''</p>
[HISTOGRAM_CHART]

<h2>''' + str2HTML(self.tr('5. CDF of Absolute Errors', '5. CDF dos Erros Absolutos')) + '''</h2>
<p>''' + str2HTML(self.tr(
'The cumulative distribution function (CDF) summarizes the percentage of checkpoints whose absolute vertical error is smaller than a given threshold. Percentiles P68, P90, P95 and P99 are highlighted as empirical indicators of the absolute error distribution.',
'A função de distribuição acumulada (CDF) resume o percentual de checkpoints cujo erro vertical absoluto é menor que um determinado limiar. Os percentis P68, P90, P95 e P99 são destacados como indicadores empíricos da distribuição dos erros absolutos.'
)) + '''</p>
[CDF_CHART]
<h2>''' + str2HTML(self.tr('6. Percentile-based Accuracy', '6. Acurácia baseada em Percentis')) + '''</h2>
<table>
<tr><th>Percentile</th><th>|ΔZ|</th></tr>
<tr><td>P68</td><td>[P68] m</td></tr>
<tr><td>P90</td><td>[P90] m</td></tr>
<tr><td>P95</td><td>[P95] m</td></tr>
<tr><td>P99</td><td>[P99] m</td></tr>
</table>

<h2>''' + str2HTML(self.tr('7. Robust Statistics and Outliers', '7. Estatísticas Robustas e Outliers')) + '''</h2>
<table>
<tr><th>Metric</th><th>Value</th></tr>
<tr><td>Median Error</td><td>[median] m</td></tr>
<tr><td>MAD</td><td>[MAD] m</td></tr>
<tr><td>NMAD</td><td>[NMAD] m</td></tr>
<tr><td>IQR Lower Limit</td><td>[OUT_LOW] m</td></tr>
<tr><td>IQR Upper Limit</td><td>[OUT_HIGH] m</td></tr>
<tr><td>Outliers</td><td>[OUTLIERS] ([OUTLIERS_PERC]%)</td></tr>
</table>

<h2>''' + str2HTML(self.tr('8. Residual Normality Assessment', '8. Avaliação da Normalidade dos Resíduos')) + '''</h2>
<table>
<tr><th>Test</th><th>Result</th></tr>
<tr><td>Shapiro-Wilk</td><td>[SHAPIRO]</td></tr>
<tr><td>Anderson-Darling</td><td>[ANDERSON]</td></tr>
<tr><td>''' + str2HTML(self.tr('Classification', 'Classificação')) + '''</td><td>[NORMALITY_CLASS]</td></tr>
</table>
<div class="note">[NORMALITY_EXPLANATION]</div>

<h2>''' + str2HTML(self.tr('9. Point Cloud Sampling Statistics', '9. Estatísticas de Amostragem da Nuvem')) + '''</h2>
<p>[SUPPORT_METRIC]</p>
<table>
<tr><th>Metric</th><th>Distance</th></tr>
<tr><td>Mean support distance</td><td>[dist_mean] m</td></tr>
<tr><td>Median support distance</td><td>[dist_median] m</td></tr>
<tr><td>Minimum support distance</td><td>[dist_min] m</td></tr>
<tr><td>Maximum support distance</td><td>[dist_max] m</td></tr>
</table>

<h2>''' + str2HTML(self.tr('10. ASPRS-Oriented Checklist', '10. Checklist orientado pela ASPRS')) + '''</h2>
<table>
<tr><th>Requirement</th><th>Status</th></tr>
<tr><td>Independent checkpoints</td><td class="ok">''' + str2HTML(self.tr('User-defined', 'Definido pelo usuário')) + '''</td></tr>
<tr><td>Minimum 30 checkpoints</td><td>[CHECK_30]</td></tr>
<tr><td>RMSE<sub>Z</sub> reported</td><td class="ok">OK</td></tr>
<tr><td>Residual normality assessed</td><td>[CHECK_NORMALITY]</td></tr>
<tr><td>Outliers reported without automatic removal</td><td class="ok">OK</td></tr>
</table>

<h2>''' + str2HTML(self.tr('11. PEC-PCD Classification', '11. Classificação PEC-PCD')) + '''</h2>
[PEC_Z]

<h2>''' + str2HTML(self.tr('12. Automatic Interpretation', '12. Interpretação Automática')) + '''</h2>
<div class="note">
[INTERPRETATION]
</div>

<div class="footer">
Leandro França 2026<br>
Cartographic Engineer<br>
email: contato@geoone.com.br
</div>

</div>
</body>
</html>
'''
        
        def TabelaPEC(RESULTADOS):
            tabela = '''<table style="margin: 0px;" border="1" cellpadding="4"
     cellspacing="0">
      <tbody>
        <tr>'''
            for escala in Escalas:
                tabela += '    <td style="text-align: center; font-weight: bold;">{}</td>'.format(dicionario[escala])
            
            tabela +='''
            </tr>
            <tr>'''
            for escala in Escalas:
                tabela += '    <td style="text-align: center;">{}</td>'.format(RESULTADOS[escala])
            
            tabela +='''
        </tr>
      </tbody>
    </table>'''
            return tabela
        
        check30 = '<span class="ok">OK</span>' if len(DISCREP) >= 30 else '<span class="warn">Below ASPRS recommendation</span>'
        check_norm = '<span class="ok">OK</span>' if scipy_stats is not None else '<span class="warn">SciPy unavailable</span>'

        # Interpretação automática
        if OUTLIERS == 0:
            outlier_comment_en = 'No IQR-based outliers were detected.'
            outlier_comment_pt = 'Nenhum outlier pelo critério IQR foi detectado.'
        elif OUTLIERS == 1:
            outlier_comment_en = 'One IQR-based outlier was detected and kept in the analysis.'
            outlier_comment_pt = 'Um outlier pelo critério IQR foi detectado e mantido na análise.'
        else:
            outlier_comment_en = '{} IQR-based outliers were detected and kept in the analysis.'.format(int(OUTLIERS))
            outlier_comment_pt = '{} outliers pelo critério IQR foram detectados e mantidos na análise.'.format(int(OUTLIERS))

        interpretation = self.tr(
            (
                'The evaluated point cloud achieved RMSEz = {} m based on {} independent checkpoints. '
                'Cloud elevations were obtained using the method "{}"; {} input checkpoints had no valid neighborhood and were excluded. '
                'The mean vertical error was {} m, indicating the vertical bias of the dataset. '
                'The P95 absolute vertical discrepancy was {} m, meaning that 95% of the checkpoints presented |ΔZ| below this value. '
                'Residual normality classification: {}. {} {} '
                'No outliers were automatically removed from the analysis.'
            ).format(
                fnum(RMSE),
                len(DISCREP),
                method_name,
                SKIPPED,
                fnum(DISCREP.mean()),
                fnum(P95),
                normality_class,
                normality_explanation,
                outlier_comment_en
            ),
            (
                'A nuvem de pontos avaliada obteve RMSEz = {} m com base em {} checkpoints independentes. '
                'As altitudes da nuvem foram obtidas pelo método "{}"; {} checkpoints de entrada não apresentaram vizinhança válida e foram excluídos. '
                'A média das discrepâncias verticais foi {} m, indicando a tendência vertical do conjunto de dados. '
                'O percentil P95 das discrepâncias verticais absolutas foi {} m, ou seja, 95% dos checkpoints apresentaram |ΔZ| abaixo desse valor. '
                'Classificação da normalidade dos resíduos: {}. {} {} '
                'Nenhum outlier foi removido automaticamente da análise.'
            ).format(
                fnum(RMSE),
                len(DISCREP),
                method_name,
                SKIPPED,
                fnum(DISCREP.mean()),
                fnum(P95),
                normality_class,
                normality_explanation,
                outlier_comment_pt
            )
        )


        valores = {
            '[layer_name]': str2HTML(source.sourceName()),
            '[cloud]': str2HTML(cloud_layer.name()),
            '[total_points]': str(total_pnts),
            '[extracted_points]': str(len(pontos_teste)),
            '[input_count]': str(num_teste),
            '[layer_count]': str(len(DISCREP)),
            '[skipped]': str(SKIPPED),
            '[method]': str2HTML(method_name),
            '[METHOD_DESCRIPTION]': str2HTML(method_description),
            '[METHOD_FORMULA]': method_formula,
            '[SELECTION_NOTE]': str2HTML(selection_note),
            '[IDW_ROW]': idw_row,
            '[SUPPORT_METRIC]': str2HTML(support_metric),
            '[dist_filter]': fnum(distProx),
            '[crs]': str2HTML(SRC.authid() + ' - ' + SRC.description() if SRC.isValid() else ''),
            '[HISTOGRAM_CHART]': histogram_chart,
            '[CDF_CHART]': cdf_chart,

            '[discrepZ_mean]': fnum(DISCREP.mean()),
            '[discrepZ_std]': fnum(DISCREP.std()),
            '[discrepZ_max]': fnum(DISCREP.max()),
            '[discrepZ_min]': fnum(DISCREP.min()),

            '[RMSE_Z]': fnum(RMSE),
            '[P68]': fnum(P68),
            '[P90]': fnum(P90),
            '[P95]': fnum(P95),
            '[P99]': fnum(P99),

            '[median]': fnum(MEDIAN),
            '[MAD]': fnum(MAD),
            '[NMAD]': fnum(NMAD),
            '[OUT_LOW]': fnum(OUT_LOW),
            '[OUT_HIGH]': fnum(OUT_HIGH),
            '[OUTLIERS]': str(int(OUTLIERS)),
            '[OUTLIERS_PERC]': fnum(OUTLIERS_PERC),

            '[SHAPIRO]': str2HTML(shapiro_text),
            '[ANDERSON]': str2HTML(anderson_text),
            '[NORMALITY_CLASS]': str2HTML(normality_class),
            '[NORMALITY_EXPLANATION]': str2HTML(normality_explanation),

            '[dist_mean]': fnum(DISTANCES.mean()),
            '[dist_median]': fnum(np.median(DISTANCES)),
            '[dist_min]': fnum(DISTANCES.min()),
            '[dist_max]': fnum(DISTANCES.max()),

            '[CHECK_30]': check30,
            '[CHECK_NORMALITY]': check_norm,

            '[PEC_Z]': TabelaPEC(RESULTADOS),
            '[INTERPRETATION]': str2HTML(interpretation),
        }
        
        for valor in valores:
            texto = texto.replace(valor, valores[valor])

        arq.write(texto)
        arq.close()
        
        feedback.pushInfo(self.tr('Operation completed successfully!', 'Operação finalizada com sucesso!'))
        feedback.pushInfo(self.tr('Leandro Franca - Cartographic Engineer', 'Leandro França - Eng Cart'))

        self.SAIDA = dest_id
        self.P68 = P68
        self.P90 = P90
        self.P95 = P95
        self.P99 = P99

        return {self.OUTPUT: dest_id,
                self.HTML: html_output}

    def postProcessAlgorithm(self, context, feedback):

        layer = QgsProcessingUtils.mapLayerFromString(self.SAIDA, context)

        if layer is None or layer.featureCount() == 0:
            return {}

        field = 'pc_discrep_z'

        # Verifica se o campo existe
        if layer.fields().indexFromName(field) == -1:
            return {}

        # Criar simbologia baseada em regras por |ΔZ|
        root_rule = QgsRuleBasedRenderer.Rule(None)

        classes = [
            (
                self.tr('|ΔZ| ≤ P68', '|ΔZ| ≤ P68'),
                'abs("{}") <= {}'.format(field, self.P68),
                '#1a9850',
                2.4
            ),
            (
                self.tr('P68 < |ΔZ| ≤ P90', 'P68 < |ΔZ| ≤ P90'),
                'abs("{}") > {} AND abs("{}") <= {}'.format(field, self.P68, field, self.P90),
                '#91cf60',
                2.6
            ),
            (
                self.tr('P90 < |ΔZ| ≤ P95', 'P90 < |ΔZ| ≤ P95'),
                'abs("{}") > {} AND abs("{}") <= {}'.format(field, self.P90, field, self.P95),
                '#fee08b',
                2.8
            ),
            (
                self.tr('P95 < |ΔZ| ≤ P99', 'P95 < |ΔZ| ≤ P99'),
                'abs("{}") > {} AND abs("{}") <= {}'.format(field, self.P95, field, self.P99),
                '#fc8d59',
                3.0
            ),
            (
                self.tr('|ΔZ| > P99', '|ΔZ| > P99'),
                'abs("{}") > {}'.format(field, self.P99),
                '#d73027',
                3.4
            ),
        ]

        for label, expression, color, size in classes:
            symbol = QgsMarkerSymbol.createSimple({
                'name': 'circle',
                'color': color,
                'outline_color': '0,0,0',
                'outline_style': 'solid',
                'size': str(size),
                'size_unit': 'MM'
            })

            rule = QgsRuleBasedRenderer.Rule(symbol)
            rule.setFilterExpression(expression)
            rule.setLabel(label)
            root_rule.appendChild(rule)

        renderer = QgsRuleBasedRenderer(root_rule)
        layer.setRenderer(renderer)

        # Rotular com discrepância Z
        label_settings = QgsPalLayerSettings()
        label_settings.fieldName = 'round("{}", 3)'.format(field)
        label_settings.isExpression = True
        label_settings.enabled = True

        text_format = QgsTextFormat()
        font = QFont("Arial", 8)
        font.setBold(True)
        text_format.setFont(font)
        text_format.setSize(8)
        text_format.setColor(QColor("white"))

        buffer_settings = QgsTextBufferSettings()
        buffer_settings.setEnabled(True)
        buffer_settings.setSize(0.6)
        buffer_settings.setColor(QColor("black"))
        text_format.setBuffer(buffer_settings)

        label_settings.setFormat(text_format)

        labeling = QgsVectorLayerSimpleLabeling(label_settings)
        layer.setLabeling(labeling)
        layer.setLabelsEnabled(True)

        layer.triggerRepaint()

        return {}
