# -*- coding: utf-8 -*-

"""
Easy_MagicStyles.py
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
__date__ = '2025-10-25'
__copyright__ = '(C) 2025, Leandro França'

from qgis.core import (
    QgsApplication,
    QgsProcessingParameterMapLayer,
    QgsWkbTypes,
    QgsProcessing,
    QgsProcessingParameterEnum,
    QgsRasterBandStats,
    QgsProcessingException,
    QgsProcessingAlgorithm,
    QgsMapLayerType
)
from lftools.geocapt.imgs import Imgs
from lftools.translations.translate import translate
from collections import Counter
import os
import shutil
import tempfile
from qgis.PyQt.QtGui import QIcon


class MagicStyles(QgsProcessingAlgorithm):

    LOC = QgsApplication.locale()[:2]

    LAYER = 'LAYER'
    STYLE_POINT = 'STYLE_POINT'
    STYLE_LINE = 'STYLE_LINE'
    STYLE_POLYGON = 'STYLE_POLYGON'
    STYLE_RASTER = 'STYLE_RASTER'

    def tr(self, *string):
        return translate(string, self.LOC)

    def createInstance(self):
        return MagicStyles()

    def name(self):
        return 'magicstyles'

    def displayName(self):
        return self.tr('Magic Styles', 'Estilos Mágicos')

    def group(self):
        return self.tr('Easy', 'Mão na Roda')

    def groupId(self):
        return 'easy'

    def tags(self):
        return 'GeoOne,easy,estilos,qml,styles,cotagem,sld,azimute,azimuth,distância,distance,symbology,simbologia,cotas,dimensioning,drones,VR,RV,360,raster,MDE,DEM,elevation,temperature'.split(',')

    def icon(self):
        return QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images/easy.png'))

    txt_en = '''This tool automatically <b>applies cartographic styles</b> to your QGIS layers — as if by magic.
It transforms point, line, polygon and raster layers into ready-to-use visual representations for professional maps, quickly and effortlessly.'''
    txt_pt = '''Esta ferramenta <b>aplica estilos</b> cartográficos automáticos às suas camadas no QGIS, como um passe de mágica.
Transforme pontos, linhas, polígonos e rasters em representações visuais prontas para mapas profissionais — simples, rápidas e com um toque criativo.'''
    figure = 'images/tutorial/easy_magic_styles.jpg'

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

    def initAlgorithm(self, config=None):

        self.addParameter(
            QgsProcessingParameterMapLayer(
                self.LAYER,
                self.tr('Layer', 'Camada'),
                [QgsProcessing.TypeVectorPoint,
                 QgsProcessing.TypeVectorLine,
                 QgsProcessing.TypeVectorPolygon,
                 QgsProcessing.TypeRaster]
            )
        )

        STYLES = {
            QgsWkbTypes.PointGeometry: [
                self.tr('- Select one style -', '- Selecione um estilo -'),
                self.tr('Drone'),
                self.tr('VR Photo 360°', 'RV Foto 360°'),
                self.tr('VR Video 360°', 'RV Vídeo 360°'),
                self.tr('Simple Camera', 'Camera simples'),
                self.tr('Spot elevation', 'Ponto cotado')
            ],
            QgsWkbTypes.LineGeometry: [
                self.tr('- Select one style -', '- Selecione um estilo -'),
                self.tr('Dimensioning', 'Cotagem'),
                self.tr('Contour Lines', 'Curvas de nível'),
                self.tr('Distance and Azimuth', 'Distância e Azimute'),
                self.tr('VR Video 360°', 'RV Video 360°')
            ],
            QgsWkbTypes.PolygonGeometry: [
                self.tr('- Select one style -', '- Selecione um estilo -'),
                self.tr('Cadastre', 'Cadastro')
            ],
            "RASTER": [
                self.tr('- Select one style -', '- Selecione um estilo -'),
                self.tr('Elevation', 'Elevação') + ' 1',
                self.tr('Elevation', 'Elevação') + ' 2',
                self.tr('Temperature', 'Temperatura')
            ]
        }

        self.addParameter(
            QgsProcessingParameterEnum(
                self.STYLE_POINT,
                self.tr('POINT Layer Style'),
                options=STYLES[QgsWkbTypes.PointGeometry],
                defaultValue=0
            )
        )

        self.addParameter(
            QgsProcessingParameterEnum(
                self.STYLE_LINE,
                self.tr('LINE Layer Style'),
                options=STYLES[QgsWkbTypes.LineGeometry],
                defaultValue=0
            )
        )

        self.addParameter(
            QgsProcessingParameterEnum(
                self.STYLE_POLYGON,
                self.tr('POLYGON Layer Style'),
                options=STYLES[QgsWkbTypes.PolygonGeometry],
                defaultValue=0
            )
        )

        self.addParameter(
            QgsProcessingParameterEnum(
                self.STYLE_RASTER,
                self.tr('RASTER Layer Style'),
                options=STYLES["RASTER"],
                defaultValue=0
            )
        )

    def processAlgorithm(self, parameters, context, feedback):

        camada = self.parameterAsLayer(
            parameters,
            self.LAYER,
            context
        )
        if camada is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.LAYER))

        estilo_ponto = self.parameterAsEnum(parameters, self.STYLE_POINT, context)
        estilo_linha = self.parameterAsEnum(parameters, self.STYLE_LINE, context)
        estilo_poligono = self.parameterAsEnum(parameters, self.STYLE_POLYGON, context)
        estilo_raster = self.parameterAsEnum(parameters, self.STYLE_RASTER, context)

        caminho_estilos = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'styles')

        QML = {
            QgsWkbTypes.PointGeometry: {
                1: 'drone_prof_leandro',
                2: 'vr_photo_360_prof_leandro',
                3: 'vr_video_point_360_prof_leandro',
                4: 'camera_prof_leandro',
                5: 'spot_elevation_prof_leandro'
            },
            QgsWkbTypes.LineGeometry: {
                1: 'cotagem_prof_leandro',
                2: 'contours_prof_leandro',
                3: 'dist_azim_linha_prof_leandro',
                4: 'vr_video_line_360_prof_leandro'
            },
            QgsWkbTypes.PolygonGeometry: {
                1: 'cadastro_prof_leandro'
            },
            "RASTER": {
                1: 'raster_dem',
                2: 'raster_dem',
                3: 'raster_dem'
            }
        }

        # =========================
        # RASTER
        # =========================
        if camada.type() == QgsMapLayerType.RasterLayer:

            if estilo_raster == 0:
                raise QgsProcessingException(self.tr('Select a Raster Layer Style!', 'Selecione um estilo de camada Raster!'))

            estilo_base = os.path.join(caminho_estilos, QML["RASTER"][estilo_raster] + '.qml')

            ramp_names = {
                1: 'raster_elevation_1',
                2: 'raster_elevation_2',
                3: 'raster_temperature'
            }

            ramp_sources = {
                1: 'grass/elevation',
                2: 'wkp/schwarzwald/wiki-schwarzwald-cont',
                3: 'h5/jet'
            }

            label_decimals_map = {
                1: 0,
                2: 0,
                3: 1
            }

            min_val, max_val, nodata = self.get_raster_min_max(camada, band=1, feedback=feedback)

            ramp_name = ramp_names[estilo_raster]
            source_name = ramp_sources[estilo_raster]
            label_decimals = label_decimals_map[estilo_raster]

            colors = self.COLOR_RAMPS[ramp_name]
            item_values = self.gerar_item_values(
                colors=colors,
                min_val=min_val,
                max_val=max_val,
                decimals=6,
                label_decimals=label_decimals
            )

            estilo_selec = self.prepare_temp_qml(
                estilo_base,
                ['[MIN]', '[MAX]', '[RAMP_NAME]', '[ITEM_VALUES]'],
                [
                    self.format_number(min_val, 6),
                    self.format_number(max_val, 6),
                    source_name,
                    item_values
                ]
            )

            camada.loadNamedStyle(estilo_selec)
            camada.triggerRepaint()

            feedback.pushInfo(self.tr('Operation completed successfully!', 'Operação finalizada com sucesso!'))
            feedback.pushInfo(self.tr('Leandro Franca - Cartographic Engineer', 'Leandro França - Eng Cart'))

            return {}

        # =========================
        # VECTOR
        # =========================
        tipo_geom = QgsWkbTypes.geometryType(camada.wkbType())
        CRS = camada.crs()

        if tipo_geom == QgsWkbTypes.PointGeometry:
            if estilo_ponto == 0:
                raise QgsProcessingException(self.tr('Select a Point Layer Style!', 'Selecione um estilo para camada de pontos!'))
            else:
                estilo_selec = os.path.join(caminho_estilos, QML[tipo_geom][estilo_ponto] + '.qml')
                if estilo_ponto == 1:  # drone
                    estilo_selec = self.prepare_temp_qml_with_svg(
                        estilo_selec,
                        ['[CAMINHO1]', '[CAMINHO2]'],
                        [
                            os.path.join(caminho_estilos, 'SVG/drone_azimuth.svg'),
                            os.path.join(caminho_estilos, 'SVG/drone.svg')
                        ]
                    )
                elif estilo_ponto == 2:  # foto 360
                    estilo_selec = self.prepare_temp_qml_with_svg(
                        estilo_selec,
                        ['[CAMINHO]'],
                        [os.path.join(caminho_estilos, 'SVG/multidirectional 360.svg')]
                    )
                elif estilo_ponto == 3:  # vídeo 360
                    estilo_selec = self.prepare_temp_qml_with_svg(
                        estilo_selec,
                        ['[CAMINHO]'],
                        [os.path.join(caminho_estilos, 'SVG/video360.svg')]
                    )
                elif estilo_ponto == 4:  # camera simples
                    estilo_selec = self.prepare_temp_qml_with_svg(
                        estilo_selec,
                        ['[CAMINHO]'],
                        [os.path.join(caminho_estilos, 'SVG/camera.svg')]
                    )
                elif estilo_ponto == 5:  # ponto cotado
                    ATT = self.detectar_campo(camada, feedback=feedback)
                    estilo_selec = self.prepare_temp_qml(estilo_selec, ['[COTA]'], [ATT])

        elif tipo_geom == QgsWkbTypes.LineGeometry:
            if estilo_linha == 0:
                raise QgsProcessingException(self.tr('Select a Line Layer Style!', 'Selecione um estilo para camada de linhas!'))
            else:
                estilo_selec = os.path.join(caminho_estilos, QML[tipo_geom][estilo_linha] + '.qml')
                if estilo_linha in (1, 3):  # cotagem / distância e azimute
                    expr = '$length' if CRS.isGeographic() else 'length($geometry)'
                    estilo_selec = self.prepare_temp_qml(estilo_selec, ['[EXPRESSION]'], [expr])
                elif estilo_linha == 4:  # vídeo 360
                    estilo_selec = self.prepare_temp_qml_with_svg(
                        estilo_selec,
                        ['[CAMINHO]'],
                        [os.path.join(caminho_estilos, 'SVG/video360.svg')]
                    )
                elif estilo_linha == 2:  # curvas de nível
                    ATT, EQUIDIST = self.detectar_campo_cota_e_equidistancia(camada, feedback=feedback)
                    estilo_selec = self.prepare_temp_qml(
                        estilo_selec,
                        ['[ATT]', '[EQUIDIST]', '[INTERMEDIATE]', '[INDEX]'],
                        [
                            str(ATT),
                            str(EQUIDIST),
                            self.tr('intermediate contours', 'curvas normais'),
                            self.tr('index contours', 'curvas mestras')
                        ]
                    )

        elif tipo_geom == QgsWkbTypes.PolygonGeometry:
            if estilo_poligono == 0:
                raise QgsProcessingException(self.tr('Select a Polygon Layer Style!', 'Selecione um estilo para camada de polígonos!'))
            else:
                estilo_selec = os.path.join(caminho_estilos, QML[tipo_geom][estilo_poligono] + '.qml')
                if estilo_poligono == 1:  # cadastro
                    if CRS.isGeographic():
                        expr1 = "format_number( distance( start_point(geometry_n(   transform($geometry, @layer_crs,  @project_crs ),  @geometry_part_num )), end_point(geometry_n(   transform($geometry, @layer_crs,  @project_crs ),  @geometry_part_num )) ) ,2)  ||  ' m'"
                        expr2 = "format_number(area(transform($geometry, @layer_crs, @project_crs)),2) ||  ' m²'"
                        expr3 = "'Az '  || dd2dms(degrees(  azimuth( start_point(geometry_n(   transform($geometry, @layer_crs,  @project_crs ),  @geometry_part_num )), end_point(geometry_n(   transform($geometry, 'EPSG:4674',  @project_crs ),  @geometry_part_num )))),0)"
                    else:
                        expr1 = "format_number( distance( start_point(geometry_n(  $geometry,  @geometry_part_num )), end_point(geometry_n(  $geometry,  @geometry_part_num )) ) ,2)  ||  ' m'"
                        expr2 = "format_number(area($geometry), 2)  ||  ' m²'"
                        expr3 = "'Az '  || dd2dms( degrees(  azimuth( start_point(geometry_n(  $geometry,  @geometry_part_num )), end_point(geometry_n(  $geometry,  @geometry_part_num )))),0)"
                    estilo_selec = self.prepare_temp_qml(
                        estilo_selec,
                        ['[EXPRESSION_DISTANCE]', '[EXPRESSION_AREA]', '[EXPRESSION_AZIMUTH]'],
                        [expr1, expr2, expr3]
                    )
        else:
            raise QgsProcessingException(self.tr('Unsupported layer type!', 'Tipo de camada não suportado!'))

        camada.loadNamedStyle(estilo_selec)
        camada.triggerRepaint()

        feedback.pushInfo(self.tr('Operation completed successfully!', 'Operação finalizada com sucesso!'))
        feedback.pushInfo(self.tr('Leandro Franca - Cartographic Engineer', 'Leandro França - Eng Cart'))

        return {}

    def format_number(self, value, decimals=6):
        txt = f"{float(value):.{decimals}f}"
        txt = txt.rstrip("0").rstrip(".")
        return txt if txt else "0"

    def prepare_temp_qml_with_svg(self, qml_path, tokens_to_replace, svg_paths):
        """
        Cria um QML temporário substituindo múltiplos placeholders por caminhos de SVG.
        """
        if not os.path.isfile(qml_path):
            raise FileNotFoundError(f"QML not found: {qml_path}!")

        if not isinstance(tokens_to_replace, (list, tuple)) or not isinstance(svg_paths, (list, tuple)):
            raise TypeError("tokens_to_replace and svg_paths must be list or tuple!")

        if len(tokens_to_replace) != len(svg_paths):
            raise ValueError("tokens_to_replace and svg_paths must have the SAME length!")

        norm_svg_paths = []
        for p in svg_paths:
            if not os.path.isfile(p):
                raise FileNotFoundError(f"SVG not found: {p}!")
            norm = os.path.normpath(p).replace('\\', '/')
            norm_svg_paths.append(norm)

        with open(qml_path, 'r', encoding='utf-8') as f:
            content = f.read()

        for token, svg in zip(tokens_to_replace, norm_svg_paths):
            content = content.replace(token, svg)

        temp_dir = tempfile.mkdtemp(prefix='lftools_qml_')
        temp_qml_path = os.path.join(temp_dir, os.path.basename(qml_path))

        try:
            with open(temp_qml_path, 'w', encoding='utf-8') as f:
                f.write(content)
        except Exception as e:
            shutil.rmtree(temp_dir, ignore_errors=True)
            raise RuntimeError(f"Error saving temporary QML: {e}")

        return temp_qml_path

    def prepare_temp_qml(self, qml_path, tokens_to_replace, text_to_replace):
        """
        Cria um QML temporário substituindo múltiplos placeholders por textos.
        """
        if not os.path.isfile(qml_path):
            raise FileNotFoundError(f"QML not found: {qml_path}!")

        if not isinstance(tokens_to_replace, (list, tuple)) or not isinstance(text_to_replace, (list, tuple)):
            raise TypeError("tokens_to_replace and text_to_replace must be list or tuple!")

        if len(tokens_to_replace) != len(text_to_replace):
            raise ValueError("tokens_to_replace and text_to_replace must have the SAME length!")

        with open(qml_path, 'r', encoding='utf-8') as f:
            content = f.read()

        for token, txt in zip(tokens_to_replace, text_to_replace):
            content = content.replace(token, txt)

        temp_dir = tempfile.mkdtemp(prefix='lftools_qml_')
        temp_qml_path = os.path.join(temp_dir, os.path.basename(qml_path))

        try:
            with open(temp_qml_path, 'w', encoding='utf-8') as f:
                f.write(content)
        except Exception as e:
            shutil.rmtree(temp_dir, ignore_errors=True)
            raise RuntimeError(f"Error saving temporary QML: {e}")

        return temp_qml_path

    def detectar_campo_cota_e_equidistancia(self, layer, candidate_names=None, casas_decimais=6, feedback=None):
        """
        Detecta automaticamente o campo de cota e a equidistância entre curvas de nível.
        """
        if candidate_names is None:
            candidate_names = [
                "cota", "cotas", "nivel", "nível", "nivels", "altura", "altitude", "altimetria",
                "elev", "elevation", "elevation_m", "elev_m", "height", "height_m",
                "elevação", "elevacao", "z", "zvalue", "z_value", "contour", "contour_elev",
                "niveles", "altitud", "cote", "côte", "hauteur", "quota", "quote",
                "altitudine", "hoehe", "höhe", "gelaendehoehe", "gelaende_hoehe"
            ]

        equidistancia_padrao = 10
        field_name = None
        candidate_lower = [c.lower() for c in candidate_names]

        for f in layer.fields():
            if f.name().lower() in candidate_lower:
                field_name = f.name()
                break

        if field_name is None:
            if feedback:
                feedback.reportError(self.tr('Field name for contours layer was not found!', 'Nome do campo de cota não foi encontrado!'))
            field_name = "ELEV"

        values = []
        for feat in layer.getFeatures():
            val = feat[field_name]
            if val is not None:
                try:
                    values.append(float(val))
                except Exception:
                    pass

        unique_vals = sorted(set(values))

        if len(values) < 2:
            if feedback:
                feedback.reportError(self.tr("Insufficient values to calculate equidistance (less than 2 elevations)!", "Valores insuficientes para calcular a equidistância (menos de 2 cotas)!"))
            return field_name, equidistancia_padrao

        elif len(unique_vals) < 2:
            if feedback:
                feedback.reportError(self.tr("Apparently all contours have the same elevation. It is not possible to calculate equidistance!", "Aparentemente todas as curvas possuem a mesma cota. Não é possível calcular a equidistância!"))
            return field_name, equidistancia_padrao

        else:
            diffs = []
            for i in range(1, len(unique_vals)):
                d = unique_vals[i] - unique_vals[i - 1]
                if d > 0:
                    diffs.append(d)

            if not diffs:
                if feedback:
                    feedback.reportError(self.tr("It was not possible to obtain positive differences between elevations!", "Não foi possível obter diferenças positivas entre as cotas!"))
                return field_name, equidistancia_padrao

            rounded_diffs = [round(d, casas_decimais) for d in diffs]
            counter = Counter(rounded_diffs)
            equidistancia, _freq = counter.most_common(1)[0]

            return field_name, equidistancia

    def detectar_campo(self, layer, candidate_names=None, standard_name=None, feedback=None):
        """
        Detecta automaticamente o possível nome do campo de uma camada.
        """
        if candidate_names is None:
            candidate_names = [
                "cota", "cotas", "nivel", "nível", "nivels", "altura", "altitude", "altimetria",
                "elev", "elevation", "elevation_m", "elev_m", "height", "height_m",
                "elevação", "elevacao", "z", "zvalue", "z_value", "contour",
                "niveles", "altitud", "cote", "côte", "hauteur", "quota", "quote",
                "altitudine", "hoehe", "höhe", "gelaendehoehe", "gelaende_hoehe"
            ]

        if standard_name is None:
            standard_name = self.tr('elevation', 'cota')

        field_name = None
        candidate_lower = [c.lower() for c in candidate_names]

        for f in layer.fields():
            if f.name().lower() in candidate_lower:
                field_name = f.name()
                break

        if field_name is None:
            if feedback:
                feedback.reportError(self.tr('Field name for contours layer was not found!', 'Nome do campo não foi encontrado!'))
            field_name = standard_name

        return field_name

    def get_raster_min_max(self, raster_layer, band=1, feedback=None):
        """
        Retorna mínimo, máximo e NoData de um raster, ignorando NoData.
        """
        if raster_layer is None or not raster_layer.isValid():
            raise QgsProcessingException(self.tr("Invalid raster layer!", "Camada raster inválida!"))

        provider = raster_layer.dataProvider()

        nodata = None
        if provider.sourceHasNoDataValue(band):
            nodata = provider.sourceNoDataValue(band)

        stats = provider.bandStatistics(
            band,
            QgsRasterBandStats.Min | QgsRasterBandStats.Max,
            raster_layer.extent(),
            0
        )

        min_val = stats.minimumValue
        max_val = stats.maximumValue

        if min_val is None or max_val is None:
            raise QgsProcessingException(self.tr("Could not compute raster statistics!", "Não foi possível calcular as estatísticas do raster!"))

        if nodata is not None and min_val == nodata and feedback:
            feedback.reportError(self.tr("Minimum equals NoData — check raster configuration!", "O valor mínimo é igual ao NoData — verifique a configuração do raster!"))

        if min_val == max_val:
            if feedback:
                feedback.pushInfo(self.tr("Raster has constant value. Expanding range slightly.", "O raster tem valor constante. Expandindo ligeiramente a faixa."))
            max_val = min_val + 1e-9

        return float(min_val), float(max_val), nodata

    def gerar_item_values(self, colors, min_val, max_val, decimals=6, label_decimals=0):
        """
        Gera o bloco XML <item> para substituir [ITEM_VALUES] no QML.
        """
        if not colors or len(colors) < 2:
            raise ValueError("At least two colors are required!")

        if min_val == max_val:
            raise ValueError("min_val and max_val cannot be equal!")

        n = len(colors)
        items_xml = []

        for i, color in enumerate(colors):
            ratio = i / (n - 1)
            value = min_val + ratio * (max_val - min_val)

            value_str = self.format_number(value, decimals)
            label = self.format_number(value, label_decimals)

            item = f'<item alpha="255" value="{value_str}" label="{label}" color="{color}"/>'
            items_xml.append(item)

        return "\n".join(items_xml)
    

    COLOR_RAMPS = {
        "raster_elevation_1": [
            "#00bfbf",
            "#00fe04",
            "#14ff00",
            "#f5ff00",
            "#fff700",
            "#ff8700",
            "#fc7f02",
            "#c47f3a",
            "#bc7d3e",
            "#141414"
        ],
        "raster_elevation_2": [
            "#aeefd5",
            "#b6f6b2",
            "#f9fcb2",
            "#dfef94",
            "#9bd362",
            "#31ab2c",
            "#1c9e2c",
            "#07843c",
            "#15823f",
            "#4b8e3b",
            "#bbad22",
            "#ebb510",
            "#f5b609",
            "#f8b004",
            "#cd5a02",
            "#a82902",
            "#7e0400",
            "#6a2f0d",
            "#967460",
            "#aeaeae",
            "#ebe9eb"
        ],
        "raster_temperature": [
            "#0000bf",
            "#0000ff",
            "#00ffff",
            "#3fffff",
            "#ffff3f",
            "#ffff00",
            "#ff0000",
            "#bf0000"
        ]
    }