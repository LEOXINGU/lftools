# -*- coding: utf-8 -*-

"""
Cad_SplitPolygon.py
***************************************************************************
*                                                                         *
*   LFTools - Split polygon by equal parts, target area or percentage     *
*                                                                         *
***************************************************************************
"""

__author__ = 'Leandro França'
__date__ = '2026-08-25'
__copyright__ = '(C) 2026, Leandro França'

from math import hypot
import os

from qgis.PyQt.QtCore import QMetaType
from qgis.PyQt.QtGui import QIcon
from qgis.core import (
    Qgis,
    QgsApplication,
    QgsCoordinateReferenceSystem,
    QgsCoordinateTransform,
    QgsDistanceArea,
    QgsFeature,
    QgsFeatureSink,
    QgsField,
    QgsFields,
    QgsGeometry,
    QgsPointXY,
    QgsProcessingAlgorithm,
    QgsProcessingException,
    QgsProcessingParameterEnum,
    QgsProcessingParameterFeatureSink,
    QgsProcessingParameterFeatureSource,
    QgsProcessingParameterNumber,
    QgsProcessingParameterBoolean,
    QgsProject,
    QgsWkbTypes,
)

from lftools.geocapt.cartography import areaSGL, areaINCRA
from lftools.geocapt.imgs import Imgs
from lftools.translations.translate import translate


class SplitPolygon(QgsProcessingAlgorithm):

    INPUT = 'INPUT'
    REFERENCE = 'REFERENCE'
    METHOD = 'METHOD'
    VALUE = 'VALUE'
    AREA_METHOD = 'AREA_METHOD'
    REVERSE = 'REVERSE'
    TOLERANCE = 'TOLERANCE'
    OUTPUT = 'OUTPUT'

    LOC = QgsApplication.locale()[:2]

    def tr(self, *string):
        return translate(string, self.LOC)

    def createInstance(self):
        return SplitPolygon()

    def name(self):
        return 'splitpolygon'

    def displayName(self):
        return self.tr('Split polygon', 'Dividir polígono')

    def group(self):
        return self.tr('Cadastre', 'Cadastro')

    def groupId(self):
        return 'cadastro'

    def tags(self):
        return ('GeoOne,split,polygon,parcel,lot,cadastre,subdivision,divide,'
                'area,percentage,equal parts,parcela,lote,cadastro,dividir,'
                'desmembramento,fracionamento,área,percentual,partes iguais,'
                'SGL,LTP,INCRA,SIGEF,ellipsoid').split(',')

    def icon(self):
        return QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)),
                                  'images/cadastre.png'))

    txt_en = '''Divides a polygon according to the direction of a reference line, using equal parts, a target area, or a percentage. The cut position is calculated iteratively according to the selected area calculation method. The tool also supports concave polygons, holes, and multipart geometries.'''

    txt_pt = '''Divide um polígono conforme a direção de uma linha de referência, utilizando partes iguais, uma área desejada ou um percentual. A posição do corte é calculada iterativamente de acordo com o método de cálculo de área selecionado. A ferramenta também suporta polígonos côncavos, com ilhas e geometrias multipartes.'''

    figure = 'images/tutorial/cadastre_splitpolygon.jpg'
    
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
        self.addParameter(QgsProcessingParameterFeatureSource(
            self.INPUT,
            self.tr('Polygon', 'Polígono'),
            [Qgis.ProcessingSourceType.TypeVectorPolygon]
        ))

        self.addParameter(QgsProcessingParameterFeatureSource(
            self.REFERENCE,
            self.tr('Reference line (division direction)',
                    'Linha de referência (direção da divisão)'),
            [Qgis.ProcessingSourceType.TypeVectorLine]
        ))

        self.addParameter(QgsProcessingParameterEnum(
            self.METHOD,
            self.tr('Subdivision method', 'Método de divisão'),
            options=[
                self.tr('Equal parts', 'Partes iguais'),
                self.tr('Target area', 'Área desejada'),
                self.tr('Percentage', 'Percentual'),
            ],
            defaultValue=0
        ))

        self.addParameter(QgsProcessingParameterNumber(
            self.VALUE,
            self.tr('Value (number of parts / area / percentage)',
                    'Valor (número de partes / área / percentual)'),
            type=QgsProcessingParameterNumber.Type.Double,
            defaultValue=2.0,
            minValue=0.000000001
        ))

        self.addParameter(QgsProcessingParameterEnum(
            self.AREA_METHOD,
            self.tr('Area calculation method', 'Método de cálculo da área'),
            options=[
                self.tr('Ellipsoidal ($area)', 'Elipsoidal ($area)'),
                self.tr('Cartesian - input CRS', 'Plana - SRC de entrada'),
                self.tr('Local Tangent Plane (LTP)', 'Sistema Geodésico Local (SGL)'),
                self.tr('INCRA / SIGEF', 'INCRA / SIGEF'),
            ],
            defaultValue=0
        ))

        self.addParameter(QgsProcessingParameterBoolean(
            self.REVERSE,
            self.tr('Reverse subdivision side', 'Inverter lado da divisão'),
            defaultValue=False
        ))

        self.addParameter(QgsProcessingParameterNumber(
            self.TOLERANCE,
            self.tr('Area tolerance', 'Tolerância de área'),
            type=QgsProcessingParameterNumber.Type.Double,
            defaultValue=0.001,
            minValue=0.000000001
        ))

        self.addParameter(QgsProcessingParameterFeatureSink(
            self.OUTPUT,
            self.tr('Subdivided polygon', 'Polígono dividido')
        ))

    # ------------------------------------------------------------------
    # Utility methods
    # ------------------------------------------------------------------

    @staticmethod
    def _unique_field_name(fields, base_name):
        if fields.indexOf(base_name) == -1:
            return base_name
        i = 2
        while fields.indexOf('{}_{}'.format(base_name, i)) != -1:
            i += 1
        return '{}_{}'.format(base_name, i)

    @staticmethod
    def _single_feature(source, label):
        feats = list(source.getFeatures())
        if len(feats) != 1:
            raise QgsProcessingException(label)
        return feats[0]

    @staticmethod
    def _line_direction(geom):
        """Returns a unit direction vector based on the first and last vertices."""
        vertices = [QgsPointXY(v.x(), v.y()) for v in geom.vertices()]
        if len(vertices) < 2:
            raise QgsProcessingException('Invalid reference line.')

        p0 = vertices[0]
        p1 = vertices[-1]
        dx = p1.x() - p0.x()
        dy = p1.y() - p0.y()
        length = hypot(dx, dy)

        # Closed or degenerate polyline: use its longest segment.
        if length <= 0:
            best = None
            best_len = 0.0
            for a, b in zip(vertices[:-1], vertices[1:]):
                sx = b.x() - a.x()
                sy = b.y() - a.y()
                seg_len = hypot(sx, sy)
                if seg_len > best_len:
                    best_len = seg_len
                    best = (sx, sy)
            if best is None or best_len <= 0:
                raise QgsProcessingException('Invalid reference line.')
            dx, dy = best
            length = best_len

        return dx / length, dy / length

    @staticmethod
    def _td_ranges(geom, ux, uy):
        """Projection ranges along tangent u and normal n=(-uy, ux)."""
        ext = geom.boundingBox()
        corners = [
            QgsPointXY(ext.xMinimum(), ext.yMinimum()),
            QgsPointXY(ext.xMinimum(), ext.yMaximum()),
            QgsPointXY(ext.xMaximum(), ext.yMinimum()),
            QgsPointXY(ext.xMaximum(), ext.yMaximum()),
        ]
        nx, ny = -uy, ux
        ts = [ux * p.x() + uy * p.y() for p in corners]
        ds = [nx * p.x() + ny * p.y() for p in corners]

        tspan = max(ts) - min(ts)
        dspan = max(ds) - min(ds)
        margin = max(tspan, dspan, 1.0) * 2.0
        return (min(ts) - margin, max(ts) + margin,
                min(ds) - margin, max(ds) + margin)

    @staticmethod
    def _xy_from_td(t, d, ux, uy):
        # p = u*t + n*d ; n=(-uy, ux)
        return QgsPointXY(ux * t - uy * d,
                          uy * t + ux * d)

    def _half_plane(self, cut_d, lower, ranges, ux, uy):
        tmin, tmax, dmin, dmax = ranges
        if lower:
            coords = [
                self._xy_from_td(tmin, dmin, ux, uy),
                self._xy_from_td(tmax, dmin, ux, uy),
                self._xy_from_td(tmax, cut_d, ux, uy),
                self._xy_from_td(tmin, cut_d, ux, uy),
                self._xy_from_td(tmin, dmin, ux, uy),
            ]
        else:
            coords = [
                self._xy_from_td(tmin, cut_d, ux, uy),
                self._xy_from_td(tmax, cut_d, ux, uy),
                self._xy_from_td(tmax, dmax, ux, uy),
                self._xy_from_td(tmin, dmax, ux, uy),
                self._xy_from_td(tmin, cut_d, ux, uy),
            ]
        return QgsGeometry.fromPolygonXY([coords])

    def _cumulative_geometry(self, geom, cut_d, reverse, ranges, ux, uy):
        # Normal side grows from dmin -> dmax. Reverse side grows dmax -> dmin.
        mask = self._half_plane(cut_d, not reverse, ranges, ux, uy)
        result = geom.intersection(mask)
        if result is None or result.isNull() or result.isEmpty():
            return QgsGeometry()
        return result

    def _prepare_geographic(self, geom, crs, context):
        clone = QgsGeometry(geom)
        if crs.isGeographic():
            return clone, crs

        authid = crs.geographicCrsAuthId()
        crs_geo = QgsCoordinateReferenceSystem(authid)
        if not crs_geo.isValid():
            raise QgsProcessingException(self.tr(
                'Could not determine the geographic CRS associated with the input CRS.',
                'Não foi possível determinar o SRC geográfico associado ao SRC de entrada.'
            ))
        transformer = QgsCoordinateTransform(crs, crs_geo, context.transformContext())
        clone.transform(transformer)
        return clone, crs_geo

    def _area(self, geom, area_method, crs, context, distance_area=None):
        if geom is None or geom.isNull() or geom.isEmpty():
            return 0.0

        if area_method == 0:  # Ellipsoidal, square metres
            return abs(float(distance_area.measureArea(geom)))

        if area_method == 1:  # Cartesian, squared layer units
            return abs(float(geom.area()))

        geom_geo, crs_geo = self._prepare_geographic(geom, crs, context)
        if area_method == 2:
            return abs(float(areaSGL(geom_geo, crs_geo)))
        return abs(float(areaINCRA(geom_geo, crs_geo)))

    def _find_cut(self, geom, target_area, total_area, reverse, ranges,
                  ux, uy, area_method, crs, context, distance_area,
                  tolerance, feedback):
        _, _, dmin, dmax = ranges
        lo, hi = dmin, dmax
        best_d = (lo + hi) / 2.0
        best_geom = QgsGeometry()
        best_err = float('inf')

        # 80 bisection iterations exceed the practical precision required by
        # cadastral geometries while keeping expensive geodetic calculations bounded.
        for _ in range(80):
            if feedback.isCanceled():
                break

            mid = (lo + hi) / 2.0
            candidate = self._cumulative_geometry(
                geom, mid, reverse, ranges, ux, uy
            )
            current_area = self._area(
                candidate, area_method, crs, context, distance_area
            )
            err = abs(current_area - target_area)

            if err < best_err:
                best_err = err
                best_d = mid
                best_geom = candidate

            effective_tol = max(tolerance, abs(target_area) * 1e-12)
            if err <= effective_tol:
                break

            if not reverse:
                # lower half-plane area increases as d increases
                if current_area < target_area:
                    lo = mid
                else:
                    hi = mid
            else:
                # upper half-plane area decreases as d increases
                if current_area > target_area:
                    lo = mid
                else:
                    hi = mid

        return best_d, best_geom, best_err

    @staticmethod
    def _as_multi(geom):
        if geom is None or geom.isNull() or geom.isEmpty():
            return geom
        out = QgsGeometry(geom)
        if not out.isMultipart():
            out.convertToMultiType()
        return out

    # ------------------------------------------------------------------
    # Main processing
    # ------------------------------------------------------------------

    def processAlgorithm(self, parameters, context, feedback):
        source = self.parameterAsSource(parameters, self.INPUT, context)
        if source is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.INPUT))

        reference = self.parameterAsSource(parameters, self.REFERENCE, context)
        if reference is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.REFERENCE))

        polygon_feat = self._single_feature(
            source,
            self.tr(
                'The polygon input must contain exactly one feature. If the layer contains several polygons, select one and run the algorithm using selected features only.',
                'A entrada poligonal deve conter exatamente uma feição. Se a camada possuir vários polígonos, selecione um deles e execute o algoritmo apenas nas feições selecionadas.'
            )
        )
        line_feat = self._single_feature(
            reference,
            self.tr(
                'The reference line input must contain exactly one feature.',
                'A entrada da linha de referência deve conter exatamente uma feição.'
            )
        )

        geom = QgsGeometry(polygon_feat.geometry())
        line_geom = QgsGeometry(line_feat.geometry())
        if geom.isNull() or geom.isEmpty():
            raise QgsProcessingException(self.tr('Empty polygon geometry!', 'Geometria poligonal vazia!'))
        if not geom.isGeosValid():
            raise QgsProcessingException(self.tr(
                'The polygon geometry is invalid. Correct the geometry before subdivision.',
                'A geometria do polígono é inválida. Corrija a geometria antes da divisão.'
            ))
        if line_geom.isNull() or line_geom.isEmpty():
            raise QgsProcessingException(self.tr('Empty reference line!', 'Linha de referência vazia!'))

        method = self.parameterAsEnum(parameters, self.METHOD, context)
        value = self.parameterAsDouble(parameters, self.VALUE, context)
        area_method = self.parameterAsEnum(parameters, self.AREA_METHOD, context)
        reverse = self.parameterAsBoolean(parameters, self.REVERSE, context)
        tolerance = self.parameterAsDouble(parameters, self.TOLERANCE, context)

        if tolerance <= 0:
            raise QgsProcessingException(self.tr('Invalid area tolerance!', 'Tolerância de área inválida!'))

        crs = source.sourceCrs()
        if area_method == 1 and crs.isGeographic():
            raise QgsProcessingException(self.tr(
                'Cartesian area calculation requires a projected CRS. Select another area method or reproject the layer.',
                'O cálculo de área plana requer um SRC projetado. Selecione outro método de cálculo ou reprojete a camada.'
            ))

        # Ellipsoidal area measurement ($area concept): source CRS + project ellipsoid.
        distance_area = QgsDistanceArea()
        distance_area.setSourceCrs(crs, context.transformContext())
        ellipsoid = QgsProject.instance().ellipsoid()
        if not ellipsoid or str(ellipsoid).upper() in ('NONE', 'NOT_SET'):
            ellipsoid = crs.ellipsoidAcronym()
        if ellipsoid:
            distance_area.setEllipsoid(ellipsoid)

        total_area = self._area(geom, area_method, crs, context, distance_area)
        if total_area <= 0:
            raise QgsProcessingException(self.tr(
                'The polygon area could not be calculated.',
                'Não foi possível calcular a área do polígono.'
            ))

        if method == 0:
            parts = int(round(value))
            if abs(value - parts) > 1e-9 or parts < 2:
                raise QgsProcessingException(self.tr(
                    'For equal parts, the value must be an integer greater than or equal to 2.',
                    'Para partes iguais, o valor deve ser um número inteiro maior ou igual a 2.'
                ))
            target_first = total_area / parts
        elif method == 1:
            if value <= 0 or value >= total_area:
                raise QgsProcessingException(self.tr(
                    'The target area must be greater than zero and smaller than the polygon area ({:.6f}).',
                    'A área desejada deve ser maior que zero e menor que a área do polígono ({:.6f}).'
                ).format(total_area))
            parts = 2
            target_first = value
        else:
            if value <= 0 or value >= 100:
                raise QgsProcessingException(self.tr(
                    'The percentage must be greater than 0 and smaller than 100.',
                    'O percentual deve ser maior que 0 e menor que 100.'
                ))
            parts = 2
            target_first = total_area * value / 100.0

        ux, uy = self._line_direction(line_geom)
        ranges = self._td_ranges(geom, ux, uy)

        feedback.pushInfo(self.tr(
            'Total area according to the selected method: {:.6f}',
            'Área total conforme o método selecionado: {:.6f}'
        ).format(total_area))

        # Find cumulative cut positions.
        cuts = []
        if method == 0:
            for k in range(1, parts):
                target = total_area * k / parts
                d, cum_geom, err = self._find_cut(
                    geom, target, total_area, reverse, ranges, ux, uy,
                    area_method, crs, context, distance_area,
                    tolerance, feedback
                )
                cuts.append((d, target, err))
                feedback.setProgress(int(70.0 * k / parts))
        else:
            d, cum_geom, err = self._find_cut(
                geom, target_first, total_area, reverse, ranges, ux, uy,
                area_method, crs, context, distance_area,
                tolerance, feedback
            )
            cuts.append((d, target_first, err))
            feedback.setProgress(70)

        # Build output pieces from cumulative half-planes. This formulation
        # supports concave polygons, holes and multipart results.
        pieces = []
        previous_cumulative = QgsGeometry()
        for idx, (cut_d, _, _) in enumerate(cuts):
            cumulative = self._cumulative_geometry(
                geom, cut_d, reverse, ranges, ux, uy
            )
            if idx == 0:
                piece = cumulative
            else:
                piece = cumulative.difference(previous_cumulative)
            if piece is not None and not piece.isNull() and not piece.isEmpty():
                pieces.append(piece)
            previous_cumulative = cumulative

        remainder = geom.difference(previous_cumulative)
        if remainder is not None and not remainder.isNull() and not remainder.isEmpty():
            pieces.append(remainder)

        expected = parts
        if len(pieces) != expected:
            raise QgsProcessingException(self.tr(
                'The subdivision generated {} parts instead of {}. Check the geometry and the reference direction.',
                'A divisão gerou {} partes em vez de {}. Verifique a geometria e a direção de referência.'
            ).format(len(pieces), expected))

        # Output fields: preserve all original attributes and append audit fields.
        fields = QgsFields()
        for fld in source.fields():
            fields.append(fld)
        fld_part = self._unique_field_name(fields, 'part')
        fields.append(QgsField(fld_part, QMetaType.Type.Int))
        fld_area = self._unique_field_name(fields, 'calc_area')
        fields.append(QgsField(fld_area, QMetaType.Type.Double, 'double', 20, 6))
        fld_percent = self._unique_field_name(fields, 'percent')
        fields.append(QgsField(fld_percent, QMetaType.Type.Double, 'double', 12, 6))

        output_wkb = QgsWkbTypes.multiType(source.wkbType())
        sink, dest_id = self.parameterAsSink(
            parameters,
            self.OUTPUT,
            context,
            fields,
            output_wkb,
            crs
        )
        if sink is None:
            raise QgsProcessingException(self.invalidSinkError(parameters, self.OUTPUT))

        # Calculate all output areas first. Percentages are normalized using the
        # sum of the generated parts, avoiding tiny numerical discrepancies between
        # the original geometry and the geometries produced by overlay operations.
        output_pieces = []
        output_areas = []
        for piece in pieces:
            piece = self._as_multi(piece)
            output_pieces.append(piece)
            output_areas.append(self._area(
                piece, area_method, crs, context, distance_area
            ))

        sum_output_areas = sum(output_areas)
        if sum_output_areas <= 0:
            raise QgsProcessingException(self.tr(
                'Could not calculate the area of the generated parts.',
                'Não foi possível calcular a área das partes geradas.'
            ))

        # Store percentages with six decimal places and force the last value to be
        # the exact complement of the previous ones, so the attribute table totals
        # exactly 100.000000%.
        percentages = []
        accumulated_percent = 0.0
        for i, calculated_area in enumerate(output_areas):
            if i == len(output_areas) - 1:
                pct = round(100.0 - accumulated_percent, 6)
            else:
                pct = round(100.0 * calculated_area / sum_output_areas, 6)
                accumulated_percent += pct
            percentages.append(pct)

        original_attrs = polygon_feat.attributes()
        for i, (piece, calculated_area, pct) in enumerate(
                zip(output_pieces, output_areas, percentages), 1):
            if feedback.isCanceled():
                break

            feat = QgsFeature(fields)
            feat.setGeometry(piece)
            feat.setAttributes(original_attrs + [
                i,
                calculated_area,
                pct,
            ])
            sink.addFeature(feat, QgsFeatureSink.Flag.FastInsert)
            feedback.setProgress(70 + int(30.0 * i / len(output_pieces)))

        feedback.pushInfo(self.tr(
            'Subdivision completed successfully! {} part(s) generated.',
            'Divisão concluída com sucesso! {} parte(s) gerada(s).'
        ).format(len(pieces)))
        feedback.pushInfo(self.tr(
            'Leandro Franca - Cartographic Engineer',
            'Leandro França - Eng. Cartógrafo'
        ))

        return {self.OUTPUT: dest_id}
