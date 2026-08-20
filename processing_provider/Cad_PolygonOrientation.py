# -*- coding: utf-8 -*-

"""
Cad_PolygonOrientation.py
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
__date__ = '2022-01-05'
__copyright__ = '(C) 2021, Leandro França'

from qgis.core import *
from lftools.geocapt.imgs import Imgs
from lftools.translations.translate import translate
from lftools.geocapt.cartography import geom2PointList, OrientarPoligono, Mesclar_Multilinhas
import os
from qgis.PyQt.QtGui import QIcon


class PolygonOrientation(QgsProcessingAlgorithm):

    POLYGONS = 'POLYGONS'
    ORIENTATION = 'ORIENTATION'
    FIRST = 'FIRST'
    SAVE = 'SAVE'
    STREET = 'STREET'
    SELECTED = 'SELECTED'
    LOC = QgsApplication.locale()[:2]

    def tr(self, *string):
        return translate(string, self.LOC)

    def createInstance(self):
        return PolygonOrientation()

    def name(self):
        return 'polygonorientation'

    def displayName(self):
        return self.tr('Orient polygons', 'Orientar polígonos')

    def group(self):
        return self.tr('Cadastre', 'Cadastro')

    def groupId(self):
        return 'cadastro'

    def tags(self):
        return 'GeoOne,cadastre,clockwise,counterclockwise,oriented,orientation,northmost,ordenar'.split(',')

    def icon(self):
        return QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images/cadastre.png'))

    txt_en = 'This tool orients the geometry of polygon-like features clockwise or counterclockwise, defining the first vertex as the north, south, east, or west.'
    txt_pt = 'Esta ferramenta orienta a geometria de feições do tipo polígono no sentido horário ou antihorário, definindo o primeiro vértice mais ao norte, sul, leste ou oeste.'
    figure = 'images/tutorial/vect_orient_polygon.jpg'

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
        # INPUT
        self.addParameter(
            QgsProcessingParameterVectorLayer(
                self.POLYGONS,
                self.tr('Polygon layer', 'Camada de Polígonos'),
                [Qgis.ProcessingSourceType.TypeVectorPolygon]
            )
        )

        self.addParameter(
            QgsProcessingParameterBoolean(
                self.SELECTED,
                self.tr('Only selected', 'Apenas selecionados'),
                defaultValue= False
            )
        )

        orient = [self.tr('Clockwise','Horário'),
				  self.tr('Counterclockwise','Anti-horário'),
				  self.tr('Do not change','Não alterar')
               ]

        self.addParameter(
            QgsProcessingParameterEnum(
                self.ORIENTATION,
                self.tr('Orientation', 'Orientação'),
				options = orient,
                defaultValue= 0
            )
        )

        opcoes = [self.tr('Polygon sequence (do not change)','Sequência do polígono (não alterar)'),
				  self.tr('Northmost','Mais ao Norte'),
				  self.tr('Southernmost','Mais ao Sul'),
				  self.tr('Eastmost','Mais ao Leste'),
				  self.tr('Westmost','Mais ao Oeste')
               ]

        self.addParameter(
            QgsProcessingParameterEnum(
                self.FIRST,
                self.tr('First point', 'Primeiro Ponto'),
				options = opcoes,
                defaultValue= 1
            )
        )

        self.addParameter(
            QgsProcessingParameterBoolean(
                self.STREET,
                self.tr('First vertex with forefront bordering the street','Primeiro vértice com vante confrontando o sistema viário'),
                defaultValue = False
            )
        )

        self.addParameter(
            QgsProcessingParameterBoolean(
                self.SAVE,
                self.tr('Save Editions', 'Salvar Edições'),
                defaultValue = False
            )
        )


    def processAlgorithm(self, parameters, context, feedback):

        # INPUT
        camada = self.parameterAsVectorLayer(
            parameters,
            self.POLYGONS,
            context
        )
        if camada is None:
            raise QgsProcessingException(
                self.invalidSourceError(parameters, self.POLYGONS)
            )

        selecionados = self.parameterAsBool(
            parameters,
            self.SELECTED,
            context
        )

        sentido = self.parameterAsEnum(
            parameters,
            self.ORIENTATION,
            context
        )
        if sentido is None:
            raise QgsProcessingException(
                self.invalidSourceError(parameters, self.ORIENTATION)
            )

        primeiro = self.parameterAsEnum(
            parameters,
            self.FIRST,
            context
        )

        rua = self.parameterAsBool(
            parameters,
            self.STREET,
            context
        )

        salvar = self.parameterAsBool(
            parameters,
            self.SAVE,
            context
        )

        # --------------------------------------------------------------
        # Conjunto de feições alvo
        # --------------------------------------------------------------
        if selecionados:
            target_ids = list(camada.selectedFeatureIds())
        else:
            target_ids = [feat.id() for feat in camada.getFeatures()]

        if not target_ids:
            feedback.pushInfo(
                self.tr(
                    'No features to process.',
                    'Nenhuma feição para processar.'
                )
            )
            return {}

        # --------------------------------------------------------------
        # Controle seguro da sessão de edição
        # --------------------------------------------------------------
        layer_was_editable = camada.isEditable()
        started_editing_here = False

        if not layer_was_editable:
            if not camada.startEditing():
                raise QgsProcessingException(
                    self.tr(
                        'Could not start layer editing.',
                        'Não foi possível iniciar a edição da camada.'
                    )
                )
            started_editing_here = True

        # --------------------------------------------------------------
        # 1) Orientar polígonos
        # --------------------------------------------------------------
        feedback.pushInfo(
            self.tr(
                'Orienting polygons...',
                'Orientando polígonos...'
            )
        )

        total = 100.0 / len(target_ids) if target_ids else 0.0

        req = QgsFeatureRequest().setFilterFids(target_ids)

        changed_orientation = 0
        skipped_invalid = 0
        skipped_null = 0

        for current, feat in enumerate(camada.getFeatures(req)):

            if feedback.isCanceled():
                if started_editing_here:
                    camada.rollBack()
                raise QgsProcessingException(
                    self.tr(
                        'Operation canceled by the user.',
                        'Operação cancelada pelo usuário.'
                    )
                )

            geom = feat.geometry()

            if geom is None or geom.isNull() or geom.isEmpty():
                skipped_null += 1
                feedback.pushWarning(
                    self.tr(
                        'Feature ID {} has null or empty geometry and was ignored.'
                        .format(feat.id()),
                        'A feição ID {} possui geometria nula ou vazia e foi ignorada.'
                        .format(feat.id())
                    )
                )
                feedback.setProgress(int((current + 1) * total))
                continue

            # Esta ferramenta reorganiza vértices; não deve tentar reparar
            # geometrias inválidas silenciosamente.
            if not geom.isGeosValid():
                skipped_invalid += 1
                feedback.pushWarning(
                    self.tr(
                        'Feature ID {} has invalid geometry and was not modified.'
                        .format(feat.id()),
                        'A feição ID {} possui geometria inválida e não foi modificada.'
                        .format(feat.id())
                    )
                )
                feedback.setProgress(int((current + 1) * total))
                continue

            try:
                if geom.isMultipart():

                    multipol = geom2PointList(geom)
                    mPol = QgsMultiPolygon()

                    for pol in multipol:
                        if not pol or not pol[0]:
                            continue

                        # Anel exterior
                        ext_coords = pol[0][:-1]

                        if len(ext_coords) < 3:
                            continue

                        ext_coords = OrientarPoligono(
                            ext_coords,
                            primeiro,
                            sentido
                        )
                        ext_ring = QgsLineString(ext_coords)
                        qgs_pol = QgsPolygon(ext_ring)

                        # Anéis internos
                        for ring in pol[1:]:
                            if not ring:
                                continue

                            int_coords = ring[:-1]

                            if len(int_coords) < 3:
                                continue

                            int_coords = OrientarPoligono(
                                int_coords,
                                primeiro,
                                sentido
                            )
                            int_ring = QgsLineString(int_coords)
                            qgs_pol.addInteriorRing(int_ring)

                        mPol.addGeometry(qgs_pol)

                    newGeom = QgsGeometry(mPol)

                else:
                    pol = geom2PointList(geom)

                    if not pol or not pol[0]:
                        feedback.setProgress(int((current + 1) * total))
                        continue

                    ext_coords = pol[0][:-1]

                    if len(ext_coords) < 3:
                        feedback.setProgress(int((current + 1) * total))
                        continue

                    ext_coords = OrientarPoligono(
                        ext_coords,
                        primeiro,
                        sentido
                    )
                    ext_ring = QgsLineString(ext_coords)
                    qgs_pol = QgsPolygon(ext_ring)

                    # Preservar e orientar anéis internos
                    for ring in pol[1:]:
                        if not ring:
                            continue

                        int_coords = ring[:-1]

                        if len(int_coords) < 3:
                            continue

                        int_coords = OrientarPoligono(
                            int_coords,
                            primeiro,
                            sentido
                        )
                        int_ring = QgsLineString(int_coords)
                        qgs_pol.addInteriorRing(int_ring)

                    newGeom = QgsGeometry(qgs_pol)

                # Nunca substituir uma geometria válida por resultado
                # nulo, vazio ou inválido.
                if (
                    newGeom is None
                    or newGeom.isNull()
                    or newGeom.isEmpty()
                    or not newGeom.isGeosValid()
                ):
                    feedback.pushWarning(
                        self.tr(
                            'Orientation result for feature ID {} was unsafe; original geometry was preserved.'
                            .format(feat.id()),
                            'O resultado da orientação da feição ID {} foi inseguro; a geometria original foi preservada.'
                            .format(feat.id())
                        )
                    )
                    feedback.setProgress(int((current + 1) * total))
                    continue

                if geom.asWkb() != newGeom.asWkb():
                    if camada.changeGeometry(feat.id(), newGeom):
                        changed_orientation += 1

            except Exception as e:
                feedback.pushWarning(
                    self.tr(
                        'Could not orient feature ID {}: {}'
                        .format(feat.id(), str(e)),
                        'Não foi possível orientar a feição ID {}: {}'
                        .format(feat.id(), str(e))
                    )
                )

            feedback.setProgress(int((current + 1) * total))

        # --------------------------------------------------------------
        # 2) Identificar primeiro ponto com vante para acesso viário
        # --------------------------------------------------------------
        street_changed = 0
        street_skipped_multipart = 0

        if rua:

            feedback.pushInfo(
                self.tr(
                    'Identifying the first forward point for road access...',
                    'Identificando primeiro ponto com vante para o acesso viário...'
                )
            )

            # Recarregar as feições, pois algumas geometrias podem ter sido
            # alteradas na etapa anterior.
            req = QgsFeatureRequest().setFilterFids(target_ids)

            for feat1 in camada.getFeatures(req):

                if feedback.isCanceled():
                    if started_editing_here:
                        camada.rollBack()
                    raise QgsProcessingException(
                        self.tr(
                            'Operation canceled by the user.',
                            'Operação cancelada pelo usuário.'
                        )
                    )

                geom_poly = feat1.geometry()

                if (
                    geom_poly is None
                    or geom_poly.isNull()
                    or geom_poly.isEmpty()
                    or not geom_poly.isGeosValid()
                ):
                    continue

                # Para MultiPolygon, "primeiro vértice com vante" é ambíguo.
                # Não alterar silenciosamente.
                if geom_poly.isMultipart():
                    street_skipped_multipart += 1
                    feedback.pushWarning(
                        self.tr(
                            'Feature ID {} is multipart; road-access first vertex was not changed.'
                            .format(feat1.id()),
                            'A feição ID {} é multiparte; o primeiro vértice para acesso viário não foi alterado.'
                            .format(feat1.id())
                        )
                    )
                    continue

                pol_parts = geom2PointList(geom_poly)

                if not pol_parts or not pol_parts[0]:
                    continue

                # Coordenadas com QgsPoint para reconstrução e preservação de Z
                COORDS = pol_parts[0][:-1]

                # Coordenadas XY usadas nas interseções pontuais
                coords_xy = geom_poly.asPolygon()[0][:-1]

                if len(COORDS) < 3 or len(coords_xy) < 3:
                    continue

                confront = {}

                # Procurar polígonos confrontantes
                req2 = QgsFeatureRequest().setFilterFids(target_ids)

                for feat2 in camada.getFeatures(req2):

                    if feat1.id() == feat2.id():
                        continue

                    geom2 = feat2.geometry()

                    if (
                        geom2 is None
                        or geom2.isNull()
                        or geom2.isEmpty()
                    ):
                        continue

                    try:
                        if not geom_poly.intersects(geom2):
                            continue

                        inters = geom_poly.intersection(geom2)

                        # A interseção entre polígonos pode ser:
                        # Point/MultiPoint   -> contato apenas em vértices
                        # Line/MultiLine    -> confrontação real
                        # Polygon/MultiPoly -> sobreposição
                        #
                        # Para identificar confrontantes nesta rotina,
                        # interessam apenas interseções LINEARES.
                        if (
                            inters is None
                            or inters.isNull()
                            or inters.isEmpty()
                            or inters.type() != Qgis.GeometryType.Line
                        ):
                            continue

                        # MultiLineString: mesclar somente partes conectadas.
                        # Partes desconectadas permanecem multipartes.
                        if inters.isMultipart():
                            inters = Mesclar_Multilinhas(inters)

                        confront[feat2.id()] = [
                            feat2.id(),
                            inters
                        ]

                    except Exception as e:
                        feedback.pushWarning(
                            self.tr(
                                'Could not evaluate boundary between features {} and {}: {}'
                                .format(feat1.id(), feat2.id(), str(e)),
                                'Não foi possível avaliar a confrontação entre as feições {} e {}: {}'
                                .format(feat1.id(), feat2.id(), str(e))
                            )
                        )

                # ------------------------------------------------------
                # Identificar, para cada vértice, se existe confrontação
                # no segmento de vante.
                # ------------------------------------------------------
                vante = []

                for pnt in coords_xy:

                    geom_pnt = QgsGeometry.fromPointXY(pnt)
                    tem_vante = False

                    for item in confront:

                        geom_confront = confront[item][1]

                        if (
                            geom_confront is None
                            or geom_confront.isNull()
                            or geom_confront.isEmpty()
                            or geom_confront.type() != Qgis.GeometryType.Line
                        ):
                            continue

                        if not geom_pnt.intersects(geom_confront):
                            continue

                        # Tratar LineString e MultiLineString sem assumir
                        # conversão direta de multipartes.
                        if geom_confront.isMultipart():
                            linhas = geom_confront.asMultiPolyline()
                        else:
                            linhas = [geom_confront.asPolyline()]

                        for coord_lin in linhas:

                            if not coord_lin or len(coord_lin) < 2:
                                continue

                            linha_geom = QgsGeometry.fromPolylineXY(coord_lin)

                            if not geom_pnt.intersects(linha_geom):
                                continue

                            # Se o ponto não for o último ponto desta parte,
                            # há segmento de confrontação no sentido de vante.
                            if pnt != coord_lin[-1]:
                                tem_vante = True
                                break

                        if tem_vante:
                            break

                    vante.append(tem_vante)

                # Encontrar transição:
                # segmento anterior confronta e o posterior não confronta.
                ind = None
                tam_vante = len(vante)

                for k in range(tam_vante):
                    anterior = vante[k - 1]
                    posterior = vante[k]

                    if anterior and not posterior:
                        ind = k
                        break

                if ind is None:
                    continue

                # Rotacionar somente o anel exterior.
                # Buracos são preservados integralmente.
                new_ext = COORDS[ind:] + COORDS[:ind]

                # QgsLineString/QgsPolygon precisam do anel fechado.
                if new_ext:
                    new_ext = new_ext + [new_ext[0]]

                ext_ring = QgsLineString(new_ext)
                new_pol = QgsPolygon(ext_ring)

                # Preservar anéis interiores da geometria já orientada
                for ring in pol_parts[1:]:
                    if not ring or len(ring) < 4:
                        continue
                    new_pol.addInteriorRing(
                        QgsLineString(ring)
                    )

                newGeom = QgsGeometry(new_pol)

                if (
                    newGeom is None
                    or newGeom.isNull()
                    or newGeom.isEmpty()
                    or not newGeom.isGeosValid()
                ):
                    feedback.pushWarning(
                        self.tr(
                            'Road-access adjustment for feature ID {} produced an unsafe geometry; original geometry was preserved.'
                            .format(feat1.id()),
                            'O ajuste para acesso viário da feição ID {} produziu uma geometria insegura; a geometria original foi preservada.'
                            .format(feat1.id())
                        )
                    )
                    continue

                if geom_poly.asWkb() != newGeom.asWkb():
                    if camada.changeGeometry(feat1.id(), newGeom):
                        street_changed += 1

        # --------------------------------------------------------------
        # Salvar edições
        # --------------------------------------------------------------
        if salvar and started_editing_here:

            if not camada.commitChanges():
                camada.rollBack()
                raise QgsProcessingException(
                    self.tr(
                        'Could not save layer edits.',
                        'Não foi possível salvar as edições da camada.'
                    )
                )

        elif salvar and layer_was_editable:

            feedback.pushWarning(
                self.tr(
                    'The layer was already in edit mode. Changes were left in the current edit session and were not committed automatically.',
                    'A camada já estava em modo de edição. As alterações foram mantidas na sessão de edição atual e não foram salvas automaticamente.'
                )
            )

        else:
            feedback.pushInfo(
                self.tr(
                    'Edits were kept in edit mode and not committed.',
                    'As edições foram mantidas em modo de edição e não foram salvas.'
                )
            )

        # --------------------------------------------------------------
        # Resumo
        # --------------------------------------------------------------
        feedback.pushInfo(
            self.tr(
                '{} feature(s) had polygon orientation adjusted.'
                .format(changed_orientation),
                '{} feição(ões) tiveram a orientação do polígono ajustada.'
                .format(changed_orientation)
            )
        )

        if rua:
            feedback.pushInfo(
                self.tr(
                    '{} feature(s) had the road-access first vertex adjusted.'
                    .format(street_changed),
                    '{} feição(ões) tiveram o primeiro vértice para acesso viário ajustado.'
                    .format(street_changed)
                )
            )

            if street_skipped_multipart:
                feedback.pushWarning(
                    self.tr(
                        '{} multipart feature(s) were not modified in the road-access step.'
                        .format(street_skipped_multipart),
                        '{} feição(ões) multiparte(s) não foram modificadas na etapa de acesso viário.'
                        .format(street_skipped_multipart)
                    )
                )

        if skipped_null:
            feedback.pushWarning(
                self.tr(
                    '{} null/empty feature(s) were ignored.'
                    .format(skipped_null),
                    '{} feição(ões) nula(s)/vazia(s) foram ignoradas.'
                    .format(skipped_null)
                )
            )

        if skipped_invalid:
            feedback.pushWarning(
                self.tr(
                    '{} invalid feature(s) were preserved without modification.'
                    .format(skipped_invalid),
                    '{} feição(ões) inválida(s) foram preservadas sem modificação.'
                    .format(skipped_invalid)
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
                'Leandro França - Cartographic Engineer',
                'Leandro França - Eng Cart'
            )
        )

        return {}