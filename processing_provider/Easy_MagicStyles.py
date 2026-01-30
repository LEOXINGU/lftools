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

from qgis.core import (QgsApplication,
                       QgsProcessingParameterVectorLayer,
                       QgsWkbTypes,
                       QgsProcessing,
                       QgsProject,
                       QgsProcessingParameterEnum,
                       QgsProcessingParameterBoolean,
                       QgsFeatureSink,
                       QgsProcessingException,
                       QgsProcessingAlgorithm,
                       QgsCoordinateTransform,
                       QgsProcessingParameterFeatureSink)
from lftools.geocapt.imgs import Imgs
from lftools.translations.translate import translate
from lftools.geocapt.cartography import OrientarPoligono
from collections import Counter
import os, shutil
import tempfile
from qgis.PyQt.QtGui import QIcon

class MagicStyles(QgsProcessingAlgorithm):

    LOC = QgsApplication.locale()[:2]

    def tr(self, *string):
        return translate(string, self.LOC)

    def createInstance(self):
        return MagicStyles()

    def name(self):
        return 'MagicStyles'.lower()

    def displayName(self):
        return self.tr('Magic Styles', 'Estilos Mágicos')

    def group(self):
        return self.tr('Easy', 'Mão na Roda')

    def groupId(self):
        return 'easy'

    def tags(self):
        return 'GeoOne,easy,estilos,qml,styles,cotagem,sld,azimute,azimuth,distância,distance,symbology,simbologia,cotas,dimensioning,drones,VR,RV,360'.split(',')

    def icon(self):
        return QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images/easy.png'))

    txt_en = '''This tool automatically <b>applies cartographic styles</b> to your QGIS vector layers — as if by magic.
It turns points, lines, and polygons into ready-to-use visual representations for professional maps, quickly and effortlessly.'''
    txt_pt = '''Esta ferramenta <b>aplica estilos</b> cartográficos automáticos às suas camadas vetoriais no QGIS, como um passe de mágica.
Transforme pontos, linhas e polígonos em representações visuais prontas para mapas profissionais — simples, rápidas e com um toque criativo.'''
    figure = 'images/tutorial/easy_magic_styles.jpg'

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

    LAYER = 'LAYER'
    STYLE_POINT = 'STYLE_POINT'
    STYLE_LINE = 'STYLE_LINE'
    STYLE_POLYGON = 'STYLE_POLYGON'
    
    def initAlgorithm(self, config=None):
        self.addParameter(
            QgsProcessingParameterVectorLayer(
                self.LAYER,
                self.tr('Layer', 'Camada'),
                [QgsProcessing.TypeVectorPoint, QgsProcessing.TypeVectorLine, QgsProcessing.TypeVectorPolygon]
            )
        )

        STYLES = {
        QgsWkbTypes.PointGeometry: [self.tr('- Select one style -', '- Selecione um estilo -'),
                                    self.tr('Drone'),
                                    self.tr('VR Photo 360°', 'RV Foto 360°'),
                                    self.tr('VR Video 360°', 'RV Vídeo 360°'),
                                    self.tr('Simple Camera', 'Camera simples'),
                                    self.tr('Spot elevation', 'Ponto cotado')],

        QgsWkbTypes.LineGeometry: [self.tr('- Select one style -', '- Selecione um estilo -'),
                                   self.tr('Dimensioning', 'Cotagem'),
                                   self.tr('Contour Lines', 'Curvas de nível'),
                                   self.tr('Distance and Azimuth', 'Distância e Azimute'),
                                   self.tr('VR Video 360°', 'RV Video 360°')],

        QgsWkbTypes.PolygonGeometry: [self.tr('- Select one style -', '- Selecione um estilo -'),
                                      self.tr('Cadastre', 'Cadastro')]
    }

        self.addParameter(
            QgsProcessingParameterEnum(
                self.STYLE_POINT,
                self.tr('POINT Layer Style'),
				options = STYLES[QgsWkbTypes.PointGeometry],
                defaultValue= 0
            )
        )

        self.addParameter(
            QgsProcessingParameterEnum(
                self.STYLE_LINE,
                self.tr('LINE Layer Style'),
				options = STYLES[QgsWkbTypes.LineGeometry],
                defaultValue= 0
            )
        )

        self.addParameter(
            QgsProcessingParameterEnum(
                self.STYLE_POLYGON,
                self.tr('POLYGON Layer Style'),
				options = STYLES[QgsWkbTypes.PolygonGeometry],
                defaultValue= 0
            )
        )


    def processAlgorithm(self, parameters, context, feedback):

        camada = self.parameterAsVectorLayer(
            parameters,
            self.LAYER,
            context
        )
        if camada is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.LAYER))

        estilo_ponto = self.parameterAsEnum(
            parameters,
            self.STYLE_POINT,
            context
        )

        estilo_linha = self.parameterAsEnum(
            parameters,
            self.STYLE_LINE,
            context
        )

        estilo_poligono = self.parameterAsEnum(
            parameters,
            self.STYLE_POLYGON,
            context
        )
        
        tipo_geom = QgsWkbTypes.geometryType(camada.wkbType())
        CRS = camada.crs()

        QML = {
        QgsWkbTypes.PointGeometry: {
                                    1: 'drone_prof_leandro',
                                    2: 'vr_photo_360_prof_leandro',
                                    3: 'vr_video_point_360_prof_leandro',
                                    4: 'camera_prof_leandro',
                                    5: 'spot_elevation_prof_leandro'
                                    },
        QgsWkbTypes.LineGeometry: {
                                    1: 'cotagem_GEO_prof_leandro' if CRS.isGeographic() else 'cotagem_UTM_prof_leandro',
                                    2: 'contours_prof_leandro',
                                    3: 'dist_azim_linha_GEO_prof_leandro' if CRS.isGeographic() else 'dist_azim_linha_UTM_prof_leandro',
                                    4: 'vr_video_line_360_prof_leandro',
                                    },

        QgsWkbTypes.PolygonGeometry: {
                                    1: 'cadastro_GEO_prof_leandro' if CRS.isGeographic() else 'cadastro_UTM_prof_leandro',
                                    }
        }

        caminho_estilos = os.path.join( os.path.join(os.path.dirname(os.path.dirname(__file__))) , 'styles')

        # Verificar se para o tipo de geometria da camada foi selecionado um estilo válido
        if tipo_geom == QgsWkbTypes.PointGeometry:
            if estilo_ponto == 0:
                raise QgsProcessingException('Select a Point Layer Style!')
            else:
                estilo_selec = os.path.join(caminho_estilos, QML[tipo_geom][estilo_ponto] + '.qml')
                if estilo_ponto == 1: # drone
                    estilo_selec = self.prepare_temp_qml_with_svg(estilo_selec, ['[CAMINHO1]', '[CAMINHO2]'], 
                                                                       [ os.path.join( caminho_estilos , 'SVG/drone_azimuth.svg'),
                                                                         os.path.join( caminho_estilos , 'SVG/drone.svg')] )
                elif estilo_ponto == 2: # foto 360
                    estilo_selec = self.prepare_temp_qml_with_svg(estilo_selec, ['[CAMINHO]'], 
                                                                       [ os.path.join( caminho_estilos , 'SVG/multidirectional 360.svg') ] )
                elif estilo_ponto == 3: # video 360
                    estilo_selec = self.prepare_temp_qml_with_svg(estilo_selec, ['[CAMINHO]'], 
                                                                       [ os.path.join( caminho_estilos , 'SVG/video360.svg') ] )
                elif estilo_ponto == 4: # camera simples
                    estilo_selec = self.prepare_temp_qml_with_svg(estilo_selec, ['[CAMINHO]'], 
                                                                       [ os.path.join( caminho_estilos , 'SVG/camera.svg') ] )
                elif estilo_ponto == 5: # ponto cotado
                    ATT = self.detectar_campo(camada, feedback = feedback)
                    estilo_selec = self.prepare_temp_qml(estilo_selec, ['[COTA]'], [ ATT ] )

        if tipo_geom == QgsWkbTypes.LineGeometry:
            if estilo_linha == 0:
                raise QgsProcessingException('Select a Line Layer Style!')
            else:
                estilo_selec = os.path.join(caminho_estilos, QML[tipo_geom][estilo_linha] + '.qml')
                if estilo_linha == 4: # video 360
                    estilo_selec = self.prepare_temp_qml_with_svg(estilo_selec, ['[CAMINHO]'], 
                                                                       [ os.path.join( caminho_estilos , 'SVG/video360.svg') ] )
                elif estilo_linha == 2: # curvas de nivel
                    ATT, EQUIDIST = self.detectar_campo_cota_e_equidistancia(camada, feedback = feedback)
                    estilo_selec = self.prepare_temp_qml(estilo_selec, ['[ATT]', '[EQUIDIST]', '[INTERMEDIATE]', '[INDEX]'], 
                                                                       [ str(ATT), str(EQUIDIST), self.tr('intermediate contours', 'curvas normais'), self.tr('index contours', 'curvas mestras') ])
            
        if tipo_geom == QgsWkbTypes.PolygonGeometry:
            if estilo_poligono == 0:
                raise QgsProcessingException('Select a Polygon Layer Style!')
            else:
                estilo_selec = os.path.join(caminho_estilos, QML[tipo_geom][estilo_poligono] + '.qml')

        camada.loadNamedStyle(estilo_selec)
        camada.triggerRepaint()

        feedback.pushInfo(self.tr('Operation completed successfully!', 'Operação finalizada com sucesso!'))
        feedback.pushInfo(self.tr('Leandro Franca - Cartographic Engineer', 'Leandro França - Eng Cart'))

        return {}
    
    def prepare_temp_qml_with_svg(self, qml_path, tokens_to_replace, svg_paths):
        """
        Cria um QML temporário substituindo múltiplos placeholders por caminhos de SVG.

        Parâmetros
        ----------
        qml_path : str
            Caminho para o arquivo QML original (texto).
        tokens_to_replace : list[str]
            Lista de strings a serem substituídas (placeholders) no QML. Ex.: ['[CAMINHO1]', '[CAMINHO2]'].
        svg_paths : list[str]
            Lista de caminhos de arquivos SVG que substituirão os tokens, na mesma ordem.

        Retorna
        -------
        str
            Caminho do arquivo QML temporário (mesmo nome do QML original, salvo em pasta tmp).

        Regras
        ------
        - O número de tokens deve ser igual ao número de caminhos de SVG.
        - Os caminhos de SVG são normalizados com barras '/' (mais seguro para QGIS).
        - Em caso de erro, a pasta temporária criada é removida.
        """
        # Validações básicas
        if not os.path.isfile(qml_path):
            raise FileNotFoundError(f"QML not found: {qml_path}!")

        if not isinstance(tokens_to_replace, (list, tuple)) or not isinstance(svg_paths, (list, tuple)):
            raise TypeError("tokens_to_replace and svg_paths must bem list or tuple!")

        if len(tokens_to_replace) != len(svg_paths):
            raise ValueError("tokens_to_replace and svg_paths must have the SAME length!")

        # Normaliza caminhos de SVG (QGIS lida bem com '/')
        norm_svg_paths = []
        for p in svg_paths:
            if not os.path.isfile(p):
                raise FileNotFoundError(f"SVG not found: {p}!")
            norm = os.path.normpath(p).replace('\\', '/')
            norm_svg_paths.append(norm)

        # Lê o QML original
        with open(qml_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Substituições (uma a uma, na ordem)
        for token, svg in zip(tokens_to_replace, norm_svg_paths):
            content = content.replace(token, svg)

        # Cria pasta temporária e salva o QML com o MESMO nome do original
        temp_dir = tempfile.mkdtemp(prefix='lftools_qml_')
        temp_qml_path = os.path.join(temp_dir, os.path.basename(qml_path))

        try:
            with open(temp_qml_path, 'w', encoding='utf-8') as f:
                f.write(content)
        except Exception as e:
            # limpa se falhar ao gravar
            shutil.rmtree(temp_dir, ignore_errors=True)
            raise RuntimeError(f"Error saving temporary QML: {e}")

        return temp_qml_path
    

    def prepare_temp_qml(self, qml_path, tokens_to_replace, text_to_replace):
        """
        Cria um QML temporário substituindo múltiplos placeholders por textos

        Parâmetros
        ----------
        qml_path : str
            Caminho para o arquivo QML original (texto).
        tokens_to_replace : list[str]
            Lista de strings a serem substituídas (placeholders) no QML. Ex.: ['[CAMINHO1]', '[CAMINHO2]'].
        text_to_replace : list[str]
            Lista de strings que substituirão os tokens, na mesma ordem.

        Retorna
        -------
        str
            Caminho do arquivo QML temporário (mesmo nome do QML original, salvo em pasta tmp).

        Regras
        ------
        - O número de tokens deve ser igual ao número de textos.
        - Em caso de erro, a pasta temporária criada é removida.
        """
        # Validações básicas
        if not os.path.isfile(qml_path):
            raise FileNotFoundError(f"QML not found: {qml_path}!")

        if not isinstance(tokens_to_replace, (list, tuple)) or not isinstance(text_to_replace, (list, tuple)):
            raise TypeError("tokens_to_replace and text_to_replace must bem list or tuple!")

        if len(tokens_to_replace) != len(text_to_replace):
            raise ValueError("tokens_to_replace and text_to_replace must have the SAME length!")

        # Lê o QML original
        with open(qml_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Substituições (uma a uma, na ordem)
        for token, txt in zip(tokens_to_replace, text_to_replace):
            content = content.replace(token, txt)

        # Cria pasta temporária e salva o QML com o MESMO nome do original
        temp_dir = tempfile.mkdtemp(prefix='lftools_qml_')
        temp_qml_path = os.path.join(temp_dir, os.path.basename(qml_path))

        try:
            with open(temp_qml_path, 'w', encoding='utf-8') as f:
                f.write(content)
        except Exception as e:
            # limpa se falhar ao gravar
            shutil.rmtree(temp_dir, ignore_errors=True)
            raise RuntimeError(f"Error saving temporary QML: {e}")

        return temp_qml_path
    

    def detectar_campo_cota_e_equidistancia(self, layer, candidate_names=None, casas_decimais=6, feedback=None):
        """
        Detecta automaticamente o campo de cota e a equidistância entre curvas de nível.

        Parâmetros
        ----------
        layer : QgsVectorLayer
            Camada vetorial de curvas de nível.
        candidate_names : list[str], opcional
            Lista de nomes possíveis para o campo de cota.
            Padrão: ["ELEV", "cota", "elevation", "Z"] (case-insensitive).
        casas_decimais : int, opcional
            Número de casas decimais para arredondar as diferenças entre cotas,
            a fim de reduzir ruído de ponto flutuante. Padrão: 6.

        Retorno
        -------
        (field_name, equidistancia) : (str, float)
            field_name  -> nome do campo de cota encontrado.
            equidistancia -> equidistância estimada entre curvas de nível.

        Verificações
        --------
            Se não encontrar campo de cota, se não houver valores suficientes
            ou não for possível calcular equidistância.
        """

        if candidate_names is None:
            candidate_names = ["cota", "cotas", "nivel", "nível", "nivels", "nivels", "altura", "altitude", "altimetria", "elev", "elevation", "elevation_m", "elev_m", "height", "height_m", "elevação", "elevacao",
                               "z", "zvalue", "z_value", "contour", "contour_elev", "niveles", "altitud", "cote", "côte", "hauteur", "quota", "quote", "altitudine", "hoehe", "höhe", "gelaendehoehe", "gelaende_hoehe"]

        equidistancia_padrao = 10

        # 1. Procurar o campo de cota (case-insensitive)
        field_name = None
        candidate_lower = [c.lower() for c in candidate_names]

        for f in layer.fields():
            if f.name().lower() in candidate_lower:
                field_name = f.name()
                break

        if field_name is None:
            feedback.reportError(self.tr('Field name for contours layer was not found!'))
            field_name = "ELEV"

        # 2. Ler valores de cota
        values = []
        for feat in layer.getFeatures():
            val = feat[field_name]
            if val is not None:
                try:
                    values.append(float(val))
                except Exception:
                    # Ignora valores não numéricos
                    pass
        
        # 3. Valores únicos ordenados
        unique_vals = sorted(set(values))

        if len(values) < 2:
            feedback.reportError(self.tr("Insufficient values ​​to calculate equidistance (less than 2 elevations)!"))
            return field_name, equidistancia_padrao
        
        elif len(unique_vals) < 2:
            feedback.reportError(self.tr("Apparently all the curves have the same elevation. There is no way to calculate the equidistance!"))
            return field_name, equidistancia_padrao
        
        else:
            # 4. Diferenças entre cotas consecutivas
            diffs = []
            for i in range(1, len(unique_vals)):
                d = unique_vals[i] - unique_vals[i - 1]
                if d > 0:
                    diffs.append(d)

            if not diffs:
                feedback.reportError(self.tr("It was not possible to obtain positive differences between quotas!"))
                return field_name, equidistancia_padrao
            
            else:
                # 5. Arredonda difs para evitar ruído de ponto flutuante
                rounded_diffs = [round(d, casas_decimais) for d in diffs]

                # 6. Conta qual diferença aparece mais (modo)
                counter = Counter(rounded_diffs)
                equidistancia, freq = counter.most_common(1)[0]

                return field_name, equidistancia

    def detectar_campo(self, layer, candidate_names=None, standard_name=None, feedback=None):
        """Detecta automaticamente o possível nome do campo de uma camada."""

        if candidate_names is None:
            candidate_names = ["cota", "cotas", "nivel", "nível", "nivels", "nivels", "altura", "altitude", "altimetria", "elev", "elevation", "elevation_m", "elev_m", "height", "height_m", "elevação", "elevacao",
                               "z", "zvalue", "z_value", "contour", "niveles", "altitud", "cote", "côte", "hauteur", "quota", "quote", "altitudine", "hoehe", "höhe", "gelaendehoehe", "gelaende_hoehe"]

        if standard_name is None:
            standard_name = self.tr('elevation','cota')

        # 1. Procurar o campo de cota (case-insensitive)
        field_name = None
        candidate_lower = [c.lower() for c in candidate_names]

        for f in layer.fields():
            if f.name().lower() in candidate_lower:
                field_name = f.name()
                break
        
        if field_name is None:
            feedback.reportError(self.tr('Field name for contours layer was not found!'))
            field_name = standard_name

        return field_name
