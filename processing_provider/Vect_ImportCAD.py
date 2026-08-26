# -*- coding: utf-8 -*-

"""
Vect_ImportCAD.py
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
__date__ = '2026-08-25'
__copyright__ = '(C) 2026, Leandro França'

import os
import re
import math
import shutil
import subprocess
import tempfile
from pathlib import Path
from collections import defaultdict, Counter

from osgeo import gdal, ogr, osr

from qgis.PyQt.QtGui import QIcon, QColor
from qgis.core import (
    Qgis,
    QgsApplication,
    QgsCategorizedSymbolRenderer,
    QgsCoordinateReferenceSystem,
    QgsFeatureRequest,
    QgsFillSymbol,
    QgsLineSymbol,
    QgsMarkerSymbol,
    QgsPalLayerSettings,
    QgsProcessingAlgorithm,
    QgsProcessingException,
    QgsProcessingParameterBoolean,
    QgsProcessingParameterCrs,
    QgsProcessingParameterEnum,
    QgsProcessingParameterFile,
    QgsProcessingParameterFileDestination,
    QgsProject,
    QgsProperty,
    QgsRendererCategory,
    QgsTextFormat,
    QgsUnitTypes,
    QgsVectorLayer,
    QgsVectorLayerSimpleLabeling,
)

from lftools.geocapt.imgs import Imgs
from lftools.translations.translate import translate


class ImportCAD(QgsProcessingAlgorithm):

    LOC = QgsApplication.locale()[:2]

    INPUT = 'INPUT'
    CRS = 'CRS'
    UNITS = 'UNITS'
    BLOCKS = 'BLOCKS'
    CURVES = 'CURVES'
    CLOSED_AS_POLYGONS = 'CLOSED_AS_POLYGONS'
    STYLE = 'STYLE'
    ODA_FALLBACK = 'ODA_FALLBACK'
    OUTPUT = 'OUTPUT'

    # Drawing-unit options. Index zero means auto detection.
    UNIT_OPTIONS = (
        'Auto detect',
        'Same as CRS units',
        'Meters',
        'Millimeters',
        'Centimeters',
        'Kilometers',
        'Feet',
        'US survey feet',
        'Inches',
        'Yards',
        'Degrees',
    )

    # AutoCAD $INSUNITS values -> internal unit key.
    INSUNITS = {
        1: 'in',       # Inches
        2: 'ft',       # Feet
        4: 'mm',       # Millimeters
        5: 'cm',       # Centimeters
        6: 'm',        # Meters
        7: 'km',       # Kilometers
        10: 'yd',      # Yards
        21: 'usft',    # US survey feet
    }

    MANUAL_UNITS = {
        1: 'same',
        2: 'm',
        3: 'mm',
        4: 'cm',
        5: 'km',
        6: 'ft',
        7: 'usft',
        8: 'in',
        9: 'yd',
        10: 'deg',
    }

    # Unit conversion to metres. Degrees are intentionally excluded because
    # an angular-to-linear conversion cannot be represented by one global scale.
    TO_METERS = {
        'm': 1.0,
        'mm': 0.001,
        'cm': 0.01,
        'km': 1000.0,
        'ft': 0.3048,
        'usft': 1200.0 / 3937.0,
        'in': 0.0254,
        'yd': 0.9144,
    }

    def tr(self, *string):
        return translate(string, self.LOC)

    def createInstance(self):
        return ImportCAD()

    def name(self):
        return 'importcad'

    def displayName(self):
        return self.tr('Import CAD', 'Importar CAD')

    def group(self):
        return self.tr('Vector', 'Vetor')

    def groupId(self):
        return 'vector'

    def tags(self):
        return 'CAD,DXF,DWG,GeoPackage,GPKG,import,OGR,layer,style,text,block,curve,CRS,unit,CAD,DXF,DWG,GeoPackage,GPKG,importar,camada,estilo,texto,bloco,curva,SRC,unidade'.split(',')

    def icon(self):
        return QIcon(
            os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                'images',
                'vetor.png'
            )
        )

    def flags(self):
        # Layers are loaded and styled directly in the current project.
        return super().flags() | Qgis.ProcessingAlgorithmFlag.FlagNoThreading

    txt_en = '''Imports a CAD drawing (DXF or DWG) into a GeoPackage, automatically detecting the coordinate reference system and drawing units when possible. The entities are organized into points, lines, polygons and texts and loaded in a group with adapted symbology. For DWG versions not supported by GDAL/OGR, the tool can optionally use an installed ODA File Converter as a fallback.'''

    txt_pt = '''Importa um desenho CAD (DXF ou DWG) para um GeoPackage, detectando automaticamente o sistema de referência de coordenadas e as unidades do desenho quando possível. As entidades são organizadas em pontos, linhas, polígonos e textos e carregadas em um grupo com simbologia adaptada. Para versões DWG não suportadas pelo GDAL/OGR, a ferramenta pode utilizar opcionalmente um ODA File Converter já instalado como alternativa.'''

    figure = 'images/tutorial/Vect_ImportCAD.jpg'
    
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
            QgsProcessingParameterFile(
                self.INPUT,
                self.tr('CAD file', 'Arquivo CAD'),
                behavior=QgsProcessingParameterFile.Behavior.File,
                fileFilter='CAD (*.dxf *.DXF *.dwg *.DWG)'
            )
        )

        crs_param = QgsProcessingParameterCrs(
            self.CRS,
            self.tr(
                'Drawing CRS (optional - automatic if possible)',
                'SRC do desenho (opcional - automático quando possível)'
            ),
            defaultValue=None,
            optional=True
        )
        self.addParameter(crs_param)

        self.addParameter(
            QgsProcessingParameterEnum(
                self.UNITS,
                self.tr(
                    'Drawing units',
                    'Unidades do desenho'
                ),
                options=[
                    self.tr('Auto detect', 'Detectar automaticamente'),
                    self.tr('Same as CRS units', 'Mesma unidade do SRC'),
                    self.tr('Meters', 'Metros'),
                    self.tr('Millimeters', 'Milímetros'),
                    self.tr('Centimeters', 'Centímetros'),
                    self.tr('Kilometers', 'Quilômetros'),
                    self.tr('Feet', 'Pés'),
                    self.tr('US survey feet', 'Pés de levantamento dos EUA'),
                    self.tr('Inches', 'Polegadas'),
                    self.tr('Yards', 'Jardas'),
                    self.tr('Degrees', 'Graus'),
                ],
                defaultValue=0
            )
        )

        self.addParameter(
            QgsProcessingParameterEnum(
                self.BLOCKS,
                self.tr('Block handling', 'Tratamento dos blocos'),
                options=[
                    self.tr('Expand block geometries', 'Expandir geometrias dos blocos'),
                    self.tr('Expand geometries and add insertion points', 'Expandir geometrias e adicionar pontos de inserção'),
                    self.tr('Insertion points only', 'Somente pontos de inserção'),
                ],
                defaultValue=0
            )
        )

        self.addParameter(
            QgsProcessingParameterBoolean(
                self.CURVES,
                self.tr('Preserve curves when possible', 'Preservar curvas quando possível'),
                defaultValue=True
            )
        )

        self.addParameter(
            QgsProcessingParameterBoolean(
                self.CLOSED_AS_POLYGONS,
                self.tr('Convert closed polylines to polygons', 'Converter polilinhas fechadas em polígonos'),
                defaultValue=True
            )
        )

        self.addParameter(
            QgsProcessingParameterEnum(
                self.STYLE,
                self.tr('Output styling', 'Simbologia de saída'),
                options=[
                    self.tr('Adapt CAD appearance', 'Adaptar aparência CAD'),
                    self.tr('Categorize by CAD layer', 'Categorizar por camada CAD'),
                    self.tr('Simple GIS style', 'Simbologia GIS simples'),
                ],
                defaultValue=0
            )
        )

        self.addParameter(
            QgsProcessingParameterBoolean(
                self.ODA_FALLBACK,
                self.tr(
                    'Use ODA File Converter as DWG fallback (if installed)',
                    'Usar ODA File Converter como alternativa para DWG (se instalado)'
                ),
                defaultValue=True
            )
        )

        self.addParameter(
            QgsProcessingParameterFileDestination(
                self.OUTPUT,
                self.tr('Output GeoPackage', 'GeoPackage de saída'),
                fileFilter='GeoPackage (*.gpkg)'
            )
        )

    # ------------------------------------------------------------------
    # Metadata detection
    # ------------------------------------------------------------------

    @staticmethod
    def _read_dxf_header_value(path, variable, max_bytes=1024 * 1024):
        """Read one variable from an ASCII DXF HEADER section.

        Returns the raw value string or None. Binary DXF files are left to the
        OGR driver and manual parameters.
        """
        if not path.lower().endswith('.dxf'):
            return None
        try:
            with open(path, 'rb') as f:
                raw = f.read(max_bytes)
            # Binary DXF has a well-known binary signature.
            if raw.startswith(b'AutoCAD Binary DXF'):
                return None
            text = raw.decode('utf-8', errors='ignore')
            lines = text.splitlines()
            wanted = variable.upper()
            for i, line in enumerate(lines):
                if line.strip().upper() != wanted:
                    continue
                # Header variables are followed by one or more code/value pairs.
                # INSUNITS normally uses group code 70; this generic routine
                # returns the first value following a numeric group code.
                for j in range(i + 1, min(i + 10, len(lines) - 1)):
                    if lines[j].strip().lstrip('-').isdigit():
                        return lines[j + 1].strip()
        except Exception:
            pass
        return None

    def _detect_insunits(self, path, dataset=None):
        raw = self._read_dxf_header_value(path, '$INSUNITS')
        if raw is not None:
            try:
                code = int(raw)
                if code in self.INSUNITS:
                    return self.INSUNITS[code], code
            except Exception:
                pass

        # Some GDAL/OGR builds may expose useful CAD metadata. This is kept as
        # a secondary, non-required path because the available keys vary.
        if dataset is not None:
            try:
                metadata = dataset.GetMetadata() or {}
                for key in ('INSUNITS', '$INSUNITS', 'DXF_INSUNITS'):
                    if key in metadata:
                        code = int(metadata[key])
                        if code in self.INSUNITS:
                            return self.INSUNITS[code], code
            except Exception:
                pass
        return None, None

    @staticmethod
    def _sidecar_crs(path):
        base = os.path.splitext(os.path.abspath(path))[0]
        for ext in ('.qpj', '.prj'):
            sidecar = base + ext
            if not os.path.isfile(sidecar):
                continue
            try:
                with open(sidecar, 'r', encoding='utf-8', errors='ignore') as f:
                    text = f.read().strip()
                if not text:
                    continue
                crs = QgsCoordinateReferenceSystem()
                # createFromWkt is the most reliable path for .prj/.qpj, while
                # createFromString also accepts AUTH:CODE and PROJ strings.
                if crs.createFromWkt(text) and crs.isValid():
                    return crs, sidecar
                crs = QgsCoordinateReferenceSystem(text)
                if crs.isValid():
                    return crs, sidecar
            except Exception:
                pass
        return QgsCoordinateReferenceSystem(), None

    @staticmethod
    def _ogr_crs(dataset):
        if dataset is None:
            return QgsCoordinateReferenceSystem()
        try:
            for i in range(dataset.GetLayerCount()):
                lyr = dataset.GetLayerByIndex(i)
                if lyr is None:
                    continue
                srs = lyr.GetSpatialRef()
                if srs is None:
                    continue
                wkt = srs.ExportToWkt()
                if not wkt:
                    continue
                crs = QgsCoordinateReferenceSystem()
                if crs.createFromWkt(wkt) and crs.isValid():
                    return crs
        except Exception:
            pass
        return QgsCoordinateReferenceSystem()

    def _resolve_crs(self, parameters, context, dataset, input_path, feedback):
        manual = self.parameterAsCrs(parameters, self.CRS, context)
        if manual.isValid():
            feedback.pushInfo(
                self.tr('CRS defined by user: {}', 'SRC definido pelo usuário: {}').format(
                    manual.authid() or manual.description()
                )
            )
            return manual

        detected = self._ogr_crs(dataset)
        if detected.isValid():
            feedback.pushInfo(
                self.tr('CRS detected from CAD/OGR metadata: {}', 'SRC detectado nos metadados CAD/OGR: {}').format(
                    detected.authid() or detected.description()
                )
            )
            return detected

        detected, sidecar = self._sidecar_crs(input_path)
        if detected.isValid():
            feedback.pushInfo(
                self.tr('CRS detected from sidecar file: {}', 'SRC detectado no arquivo lateral: {}').format(
                    os.path.basename(sidecar)
                )
            )
            return detected

        raise QgsProcessingException(
            self.tr(
                'The drawing CRS could not be detected. Run the tool again and fill in the "Drawing CRS" parameter.',
                'O SRC do desenho não pôde ser detectado. Execute novamente a ferramenta e preencha o parâmetro "SRC do desenho".'
            )
        )

    def _resolve_units(self, parameters, context, input_path, dataset, crs, feedback):
        idx = self.parameterAsEnum(parameters, self.UNITS, context)
        if idx != 0:
            unit_key = self.MANUAL_UNITS.get(idx)
            feedback.pushInfo(
                self.tr('Drawing units defined by user.', 'Unidades do desenho definidas pelo usuário.')
            )
            return unit_key

        unit_key, ins_code = self._detect_insunits(input_path, dataset)
        if unit_key:
            feedback.pushInfo(
                self.tr(
                    'Drawing units detected from $INSUNITS (code {}).',
                    'Unidades do desenho detectadas pelo $INSUNITS (código {}).'
                ).format(ins_code)
            )
            return unit_key

        raise QgsProcessingException(
            self.tr(
                'The drawing units could not be detected. Run the tool again and choose the "Drawing units" parameter.',
                'As unidades do desenho não puderam ser detectadas. Execute novamente a ferramenta e escolha o parâmetro "Unidades do desenho".'
            )
        )

    @staticmethod
    def _crs_linear_unit_to_meter(crs):
        """Return metres per one CRS map unit, or None for angular/unknown CRS."""
        if not crs.isValid() or crs.isGeographic():
            return None
        try:
            # QGIS conversion factor: one map unit -> metres.
            return QgsUnitTypes.fromUnitToUnitFactor(crs.mapUnits(), Qgis.DistanceUnit.Meters)
        except Exception:
            return None

    def _unit_scale(self, unit_key, crs):
        """Scale drawing coordinates into the map units of the chosen CRS."""
        if unit_key == 'same':
            return 1.0

        if crs.isGeographic():
            if unit_key == 'deg':
                return 1.0
            raise QgsProcessingException(
                self.tr(
                    'A geographic CRS requires drawing coordinates in degrees. Select "Degrees" or use a projected CRS compatible with the drawing units.',
                    'Um SRC geográfico requer coordenadas do desenho em graus. Selecione "Graus" ou utilize um SRC projetado compatível com as unidades do desenho.'
                )
            )

        if unit_key == 'deg':
            raise QgsProcessingException(
                self.tr(
                    'Drawing units in degrees are incompatible with the selected projected CRS.',
                    'Unidades do desenho em graus são incompatíveis com o SRC projetado selecionado.'
                )
            )

        meters_per_input = self.TO_METERS.get(unit_key)
        meters_per_map = self._crs_linear_unit_to_meter(crs)
        if meters_per_input is None or not meters_per_map:
            raise QgsProcessingException(
                self.tr('Unsupported or unknown unit conversion.', 'Conversão de unidades não suportada ou desconhecida.')
            )
        return float(meters_per_input) / float(meters_per_map)

    # ------------------------------------------------------------------
    # OGR / CAD helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _open_dataset(path, inline_blocks=True):
        previous = gdal.GetConfigOption('DXF_INLINE_BLOCKS')
        try:
            gdal.SetConfigOption('DXF_INLINE_BLOCKS', 'TRUE' if inline_blocks else 'FALSE')
            return gdal.OpenEx(path, gdal.OF_VECTOR | gdal.OF_READONLY)
        finally:
            gdal.SetConfigOption('DXF_INLINE_BLOCKS', previous)

    @staticmethod
    def _try_open_dataset(path, inline_blocks=True):
        """Open a CAD dataset without exposing GDAL exceptions to Processing.

        Returns ``(dataset, error_message)``.  The original GDAL message is kept
        so a useful explanation can be shown when a DWG version is unsupported.
        """
        try:
            ds = ImportCAD._open_dataset(path, inline_blocks)
            return ds, '' if ds is not None else 'GDAL/OGR returned an empty dataset.'
        except Exception as exc:
            return None, str(exc).strip()

    @staticmethod
    def _find_oda_file_converter():
        """Return an installed ODA File Converter executable, if found.

        The application is never bundled, downloaded or installed by LFTools.
        Detection is limited to PATH, an optional environment variable and common
        installation folders on Windows/macOS/Linux.
        """
        candidates = []

        env_path = os.environ.get('ODA_FILE_CONVERTER', '').strip()
        if env_path:
            candidates.append(env_path)

        for name in ('ODAFileConverter', 'ODAFileConverter.exe'):
            found = shutil.which(name)
            if found:
                candidates.append(found)

        # Common Windows installation folders.  ODA version numbers are part of
        # the directory name, therefore globbing is preferable to hard-coding one.
        for root_var in ('PROGRAMFILES', 'PROGRAMFILES(X86)', 'LOCALAPPDATA'):
            root = os.environ.get(root_var)
            if not root or not os.path.isdir(root):
                continue
            base = Path(root)
            patterns = (
                'ODA/ODAFileConverter*/ODAFileConverter.exe',
                'Open Design Alliance/ODAFileConverter*/ODAFileConverter.exe',
                'ODAFileConverter*/ODAFileConverter.exe',
            )
            for pattern in patterns:
                try:
                    candidates.extend(str(p) for p in base.glob(pattern))
                except Exception:
                    pass

        # Common standalone paths on macOS/Linux.
        candidates.extend((
            '/Applications/ODAFileConverter.app/Contents/MacOS/ODAFileConverter',
            '/usr/local/bin/ODAFileConverter',
            '/usr/bin/ODAFileConverter',
            '/opt/ODAFileConverter/ODAFileConverter',
        ))

        seen = set()
        for candidate in candidates:
            if not candidate:
                continue
            path = os.path.abspath(os.path.expanduser(candidate))
            key = os.path.normcase(path)
            if key in seen:
                continue
            seen.add(key)
            if os.path.isfile(path):
                return path
        return None

    def _convert_dwg_with_oda(self, input_path, feedback, temp_root):
        """Convert one DWG to a temporary DXF using an existing ODA install."""
        executable = self._find_oda_file_converter()
        if not executable:
            return None, self.tr(
                'ODA File Converter was not found on this computer.',
                'O ODA File Converter não foi encontrado neste computador.'
            )

        input_dir = os.path.join(temp_root, 'input')
        output_dir = os.path.join(temp_root, 'output')
        os.makedirs(input_dir, exist_ok=True)
        os.makedirs(output_dir, exist_ok=True)

        local_dwg = os.path.join(input_dir, os.path.basename(input_path))
        shutil.copy2(input_path, local_dwg)

        feedback.pushInfo(
            self.tr(
                'ODA File Converter detected: {}',
                'ODA File Converter detectado: {}'
            ).format(executable)
        )
        feedback.pushInfo(
            self.tr(
                'Converting DWG to a temporary DXF...',
                'Convertendo o DWG para um DXF temporário...'
            )
        )

        # ODA File Converter command-line syntax:
        # InputFolder OutputFolder OutputVersion OutputType Recurse Audit InputFilter
        command = [
            executable, input_dir, output_dir, 'ACAD2018', 'DXF',
            '0', '1', '*.dwg'
        ]

        kwargs = {
            'stdout': subprocess.PIPE,
            'stderr': subprocess.PIPE,
            'text': True,
            'errors': 'replace',
        }
        if os.name == 'nt' and hasattr(subprocess, 'CREATE_NO_WINDOW'):
            kwargs['creationflags'] = subprocess.CREATE_NO_WINDOW

        try:
            process = subprocess.run(command, **kwargs)
        except Exception as exc:
            return None, self.tr(
                'Could not start ODA File Converter: {}',
                'Não foi possível iniciar o ODA File Converter: {}'
            ).format(str(exc))

        if process.returncode != 0:
            details = (process.stderr or process.stdout or '').strip()
            return None, self.tr(
                'ODA File Converter failed (code {}). {}',
                'O ODA File Converter falhou (código {}). {}'
            ).format(process.returncode, details)

        generated = []
        for root, _dirs, files in os.walk(output_dir):
            for filename in files:
                if filename.lower().endswith('.dxf'):
                    generated.append(os.path.join(root, filename))

        if not generated:
            return None, self.tr(
                'ODA File Converter finished but no DXF file was generated.',
                'O ODA File Converter foi concluído, mas nenhum arquivo DXF foi gerado.'
            )

        # There is only one DWG in the isolated input directory. Prefer the
        # matching basename, with the first generated DXF as a safe fallback.
        stem = os.path.splitext(os.path.basename(input_path))[0].lower()
        matching = [p for p in generated if os.path.splitext(os.path.basename(p))[0].lower() == stem]
        result = matching[0] if matching else generated[0]
        feedback.pushInfo(
            self.tr(
                'Temporary DXF created successfully.',
                'DXF temporário criado com sucesso.'
            )
        )
        return result, ''

    @staticmethod
    def _field_map(feature):
        result = {}
        try:
            defn = feature.GetDefnRef()
            for i in range(defn.GetFieldCount()):
                name = defn.GetFieldDefn(i).GetNameRef()
                result[name.lower()] = name
        except Exception:
            pass
        return result

    @staticmethod
    def _field_value(feature, names, default=None):
        fmap = ImportCAD._field_map(feature)
        for name in names:
            real = fmap.get(name.lower())
            if not real:
                continue
            try:
                value = feature.GetField(real)
            except Exception:
                continue
            if value not in (None, ''):
                return value
        return default

    @staticmethod
    def _style_value(style, key):
        if not style:
            return None
        # Accepts simple OGR style tokens, e.g. c:#FF0000, w:0.25mm, a:45.
        match = re.search(r'(?<![A-Za-z0-9_])' + re.escape(key) + r'\s*:\s*("(?:[^"\\]|\\.)*"|[^,\)]+)', style, re.I)
        if not match:
            return None
        value = match.group(1).strip()
        if len(value) >= 2 and value[0] == '"' and value[-1] == '"':
            value = value[1:-1]
            value = value.replace(r'\"', '"').replace(r'\\', '\\')
        return value

    @staticmethod
    def _to_float(value, default=None):
        if value is None:
            return default
        try:
            text = str(value).strip().replace(',', '.')
            match = re.match(r'^[-+]?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?', text)
            if not match:
                return default
            number = float(match.group(0))
            return number if math.isfinite(number) else default
        except Exception:
            return default

    @staticmethod
    def _aci_color(value):
        """Small fallback mapping for the most common AutoCAD Color Index values."""
        try:
            idx = int(value)
        except Exception:
            return None
        basic = {
            1: '#ff0000', 2: '#ffff00', 3: '#00ff00', 4: '#00ffff',
            5: '#0000ff', 6: '#ff00ff', 7: '#ffffff', 8: '#808080', 9: '#c0c0c0'
        }
        return basic.get(idx)

    def _feature_metadata(self, feature, source_file):
        style = feature.GetStyleString() or ''

        cad_layer = str(self._field_value(feature, ['Layer', 'cad_layer'], '0') or '0')
        handle = str(self._field_value(feature, ['EntityHandle', 'Handle', 'cad_handle'], '') or '')
        block = str(self._field_value(feature, ['BlockName', 'Block', 'cad_block'], '') or '')
        ltype = str(self._field_value(feature, ['Linetype', 'LineType', 'cad_ltype'], '') or '')
        elev = self._to_float(self._field_value(feature, ['Elevation', 'cad_elev']), 0.0)

        text = self._field_value(feature, ['Text', 'Label', 'cad_text'], '')
        if text in (None, ''):
            text = self._style_value(style, 't') or ''
        text = str(text or '')

        color = self._style_value(style, 'c')
        if color:
            color_match = re.search(r'#[0-9A-Fa-f]{6,8}', color)
            color = color_match.group(0)[:7] if color_match else None
        if not color:
            raw_color = self._field_value(feature, ['Color', 'cad_color'])
            if isinstance(raw_color, str) and re.match(r'^#[0-9A-Fa-f]{6}', raw_color.strip()):
                color = raw_color.strip()[:7]
            else:
                color = self._aci_color(raw_color)
        color = color or ''

        rotation = self._to_float(self._field_value(feature, ['Rotation', 'Angle', 'cad_rotation']))
        if rotation is None:
            rotation = self._to_float(self._style_value(style, 'a'), 0.0)

        height = self._to_float(self._field_value(feature, ['TextHeight', 'Height', 'cad_height']))
        if height is None:
            height = self._to_float(self._style_value(style, 's'), 0.0)

        linewt = self._to_float(self._field_value(feature, ['LineWeight', 'Lineweight', 'cad_linewt']))
        if linewt is None:
            linewt = self._to_float(self._style_value(style, 'w'), 0.0)

        subclasses = str(self._field_value(feature, ['SubClasses', 'Subclass'], '') or '')
        entity = str(self._field_value(feature, ['EntityType', 'Type', 'cad_entity'], '') or '')
        if not entity and subclasses:
            tokens = re.findall(r'AcDb([A-Za-z0-9_]+)', subclasses)
            if tokens:
                entity = tokens[-1]
        if not entity:
            try:
                entity = feature.GetGeometryRef().GetGeometryName()
            except Exception:
                entity = ''

        return {
            'cad_layer': cad_layer,
            'cad_entity': entity,
            'cad_handle': handle,
            'cad_text': text,
            'cad_block': block,
            'cad_color': color,
            'cad_ltype': ltype,
            'cad_linewt': float(linewt or 0.0),
            'cad_elev': float(elev or 0.0),
            'cad_rotation': float(rotation or 0.0),
            'cad_height': float(height or 0.0),
            'cad_style': style,
            'source_file': os.path.basename(source_file),
        }

    @staticmethod
    def _scaled_geometry(geometry, factor):
        if geometry is None:
            return None
        geom = geometry.Clone()
        if abs(factor - 1.0) < 1e-15:
            return geom

        # Recursive coordinate scaling keeps arcs/curves whenever the OGR
        # geometry API exposes point access for their components.
        def scale_part(g):
            if g is None:
                return
            count = g.GetGeometryCount()
            if count:
                for i in range(count):
                    scale_part(g.GetGeometryRef(i))
                return
            try:
                n = g.GetPointCount()
            except Exception:
                n = 0
            for i in range(n):
                p = g.GetPoint(i)
                if len(p) >= 3:
                    g.SetPoint(i, p[0] * factor, p[1] * factor, p[2] * factor)
                else:
                    g.SetPoint_2D(i, p[0] * factor, p[1] * factor)

        scale_part(geom)
        return geom

    @staticmethod
    def _is_closed_line(geom):
        if geom is None:
            return False
        try:
            flat = ogr.GT_Flatten(geom.GetGeometryType())
        except Exception:
            flat = geom.GetGeometryType()

        if flat == ogr.wkbLineString:
            try:
                return bool(geom.IsRing())
            except Exception:
                try:
                    if geom.GetPointCount() < 4:
                        return False
                    a = geom.GetPoint(0)
                    b = geom.GetPoint(geom.GetPointCount() - 1)
                    return abs(a[0]-b[0]) < 1e-12 and abs(a[1]-b[1]) < 1e-12
                except Exception:
                    return False

        if flat == ogr.wkbMultiLineString and geom.GetGeometryCount() == 1:
            return ImportCAD._is_closed_line(geom.GetGeometryRef(0))
        return False

    @staticmethod
    def _closed_line_to_polygon(geom):
        if geom is None:
            return None
        try:
            flat = ogr.GT_Flatten(geom.GetGeometryType())
        except Exception:
            flat = geom.GetGeometryType()

        if flat == ogr.wkbMultiLineString and geom.GetGeometryCount() == 1:
            geom = geom.GetGeometryRef(0).Clone()
            flat = ogr.wkbLineString

        if flat != ogr.wkbLineString:
            return None
        try:
            ring = ogr.Geometry(ogr.wkbLinearRing)
            for i in range(geom.GetPointCount()):
                p = geom.GetPoint(i)
                ring.AddPoint(p[0], p[1], p[2] if len(p) > 2 else 0.0)
            if ring.GetPointCount() < 4:
                return None
            poly = ogr.Geometry(ogr.wkbPolygon)
            poly.AddGeometry(ring)
            return poly
        except Exception:
            return None

    @staticmethod
    def _geometry_dimension(geom):
        if geom is None:
            return -1
        try:
            return int(geom.GetDimension())
        except Exception:
            return -1

    @staticmethod
    def _linearize(geom):
        if geom is None:
            return None
        try:
            return geom.GetLinearGeometry()
        except Exception:
            return geom

    # ------------------------------------------------------------------
    # GeoPackage creation
    # ------------------------------------------------------------------

    @staticmethod
    def _create_fields(layer):
        fields = (
            ('cad_layer', ogr.OFTString, 120),
            ('cad_entity', ogr.OFTString, 60),
            ('cad_handle', ogr.OFTString, 80),
            ('cad_text', ogr.OFTString, 2048),
            ('cad_block', ogr.OFTString, 160),
            ('cad_color', ogr.OFTString, 16),
            ('cad_ltype', ogr.OFTString, 100),
            ('cad_linewt', ogr.OFTReal, 0),
            ('cad_elev', ogr.OFTReal, 0),
            ('cad_rotation', ogr.OFTReal, 0),
            ('cad_height', ogr.OFTReal, 0),
            ('cad_style', ogr.OFTString, 2048),
            ('source_file', ogr.OFTString, 255),
        )
        for name, ftype, width in fields:
            fd = ogr.FieldDefn(name, ftype)
            if width:
                fd.SetWidth(width)
            layer.CreateField(fd)

    @staticmethod
    def _ogr_srs(crs):
        srs = osr.SpatialReference()
        srs.ImportFromWkt(crs.toWkt())
        try:
            srs.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER)
        except Exception:
            pass
        return srs

    def _create_output_layers(self, datasource, crs, preserve_curves):
        srs = self._ogr_srs(crs)

        # Curved GPKG geometry types are used when supported by the local GDAL.
        # If unavailable, linear multi-geometries are used transparently.
        line_type = getattr(ogr, 'wkbMultiCurve', ogr.wkbMultiLineString) if preserve_curves else ogr.wkbMultiLineString
        polygon_type = getattr(ogr, 'wkbMultiSurface', ogr.wkbMultiPolygon) if preserve_curves else ogr.wkbMultiPolygon

        definitions = {
            'points': ogr.wkbMultiPoint,
            'lines': line_type,
            'polygons': polygon_type,
            'texts': ogr.wkbMultiPoint,
        }
        layers = {}
        for name, gtype in definitions.items():
            layer = datasource.CreateLayer(name, srs=srs, geom_type=gtype)
            if layer is None:
                raise QgsProcessingException(
                    self.tr('Could not create layer "{}" in the GeoPackage.', 'Não foi possível criar a camada "{}" no GeoPackage.').format(name)
                )
            self._create_fields(layer)
            layers[name] = layer
        return layers

    @staticmethod
    def _force_geometry_family(geom, family, preserve_curves):
        if geom is None:
            return None

        if not preserve_curves:
            geom = ImportCAD._linearize(geom)

        try:
            if family in ('points', 'texts'):
                return ogr.ForceToMultiPoint(geom)
            if family == 'lines':
                if preserve_curves and hasattr(ogr, 'wkbMultiCurve'):
                    return ogr.ForceTo(geom, ogr.wkbMultiCurve)
                return ogr.ForceToMultiLineString(geom)
            if family == 'polygons':
                if preserve_curves and hasattr(ogr, 'wkbMultiSurface'):
                    return ogr.ForceTo(geom, ogr.wkbMultiSurface)
                return ogr.ForceToMultiPolygon(geom)
        except Exception:
            pass
        return geom

    @staticmethod
    def _write_output_feature(layer, geometry, attrs):
        out = ogr.Feature(layer.GetLayerDefn())
        out.SetGeometry(geometry)
        for key, value in attrs.items():
            try:
                out.SetField(key, value)
            except Exception:
                pass
        result = layer.CreateFeature(out)
        out = None
        return result == 0

    def _import_pass(self, dataset, output_layers, input_path, scale_factor,
                     preserve_curves, closed_as_polygons, feedback,
                     counts, only_block_inserts=False):
        if dataset is None:
            return

        total = 0
        for li in range(dataset.GetLayerCount()):
            lyr = dataset.GetLayerByIndex(li)
            if lyr is not None:
                try:
                    total += max(0, lyr.GetFeatureCount())
                except Exception:
                    pass
        total = max(1, total)
        current = 0

        for li in range(dataset.GetLayerCount()):
            source_layer = dataset.GetLayerByIndex(li)
            if source_layer is None:
                continue
            source_layer.ResetReading()

            for feat in source_layer:
                if feedback.isCanceled():
                    return
                current += 1
                if current % 50 == 0:
                    feedback.setProgress(min(99, int(100.0 * current / total)))

                geom = feat.GetGeometryRef()
                if geom is None or geom.IsEmpty():
                    counts['ignored'] += 1
                    continue

                attrs = self._feature_metadata(feat, input_path)

                # In the second block pass, only keep actual block insertion
                # records. OGR commonly exposes BlockName when inline expansion
                # is disabled.
                if only_block_inserts:
                    is_insert = bool(attrs['cad_block']) or 'insert' in attrs['cad_entity'].lower()
                    if not is_insert:
                        continue

                geom = self._scaled_geometry(geom, scale_factor)
                if geom is None or geom.IsEmpty():
                    counts['ignored'] += 1
                    continue

                dim = self._geometry_dimension(geom)
                family = None

                if attrs['cad_text'].strip() and dim == 0:
                    family = 'texts'
                elif dim == 0:
                    family = 'points'
                elif dim == 1:
                    if closed_as_polygons and self._is_closed_line(geom):
                        converted = self._closed_line_to_polygon(self._linearize(geom))
                        if converted is not None and not converted.IsEmpty():
                            geom = converted
                            family = 'polygons'
                        else:
                            family = 'lines'
                    else:
                        family = 'lines'
                elif dim == 2:
                    family = 'polygons'
                else:
                    counts['ignored'] += 1
                    continue

                out_geom = self._force_geometry_family(geom, family, preserve_curves)
                if out_geom is None or out_geom.IsEmpty():
                    counts['ignored'] += 1
                    continue

                if self._write_output_feature(output_layers[family], out_geom, attrs):
                    counts[family] += 1
                else:
                    counts['ignored'] += 1

    # ------------------------------------------------------------------
    # QGIS styling and project loading
    # ------------------------------------------------------------------

    @staticmethod
    def _valid_hex_color(value):
        if not value:
            return None
        value = str(value).strip()
        if re.match(r'^#[0-9A-Fa-f]{6}$', value):
            return value
        return None

    @staticmethod
    def _fallback_color(key):
        # Stable color derived from the CAD layer name.
        hue = abs(hash(str(key))) % 360
        color = QColor()
        color.setHsv(hue, 150, 210)
        return color

    def _layer_stats(self, layer):
        stats = defaultdict(lambda: {'colors': Counter(), 'ltypes': Counter(), 'heights': []})
        for f in layer.getFeatures(QgsFeatureRequest()):
            cad_layer = str(f['cad_layer'] or '0')
            color = self._valid_hex_color(f['cad_color'])
            ltype = str(f['cad_ltype'] or '')
            try:
                height = float(f['cad_height'] or 0.0)
            except Exception:
                height = 0.0
            if color:
                stats[cad_layer]['colors'][color] += 1
            if ltype:
                stats[cad_layer]['ltypes'][ltype] += 1
            if height > 0:
                stats[cad_layer]['heights'].append(height)
        return stats

    @staticmethod
    def _line_style_name(ltype):
        text = (ltype or '').upper()
        if 'CENTER' in text or 'DASHDOT' in text or 'DASH-DOT' in text:
            return 'dash dot'
        if 'HIDDEN' in text or 'DASH' in text:
            return 'dash'
        if 'DOT' in text:
            return 'dot'
        return 'solid'

    def _apply_categorized_style(self, layer, family, style_mode):
        if style_mode == 2:  # Simple GIS style
            return

        stats = self._layer_stats(layer)
        categories = []
        for cad_layer in sorted(stats.keys(), key=lambda x: x.lower()):
            color_hex = None
            if style_mode == 0 and stats[cad_layer]['colors']:
                color_hex = stats[cad_layer]['colors'].most_common(1)[0][0]
            color = QColor(color_hex) if color_hex else self._fallback_color(cad_layer)

            if family == 'lines':
                ltype = stats[cad_layer]['ltypes'].most_common(1)[0][0] if stats[cad_layer]['ltypes'] else ''
                symbol = QgsLineSymbol.createSimple({
                    'line_color': color.name(),
                    'line_width': '0.30',
                    'line_style': self._line_style_name(ltype),
                })
            elif family == 'polygons':
                fill = QColor(color)
                fill.setAlpha(70)
                symbol = QgsFillSymbol.createSimple({
                    'color': fill.name(QColor.HexArgb),
                    'outline_color': color.name(),
                    'outline_width': '0.25',
                })
            else:
                symbol = QgsMarkerSymbol.createSimple({
                    'name': 'circle',
                    'color': color.name(),
                    'outline_color': color.name(),
                    'size': '2.0',
                })
            categories.append(QgsRendererCategory(cad_layer, symbol, cad_layer))

        if categories:
            layer.setRenderer(QgsCategorizedSymbolRenderer('cad_layer', categories))

    def _apply_text_labels(self, layer, style_mode):
        # Keep text geometry unobtrusive: the information is represented by labels.
        try:
            symbol = QgsMarkerSymbol.createSimple({
                'name': 'circle',
                'size': '0.1',
                'color': '0,0,0,0',
                'outline_color': '0,0,0,0',
            })
            layer.renderer().setSymbol(symbol)
        except Exception:
            pass

        settings = QgsPalLayerSettings()
        settings.fieldName = 'cad_text'
        settings.enabled = True
        try:
            settings.placement = Qgis.LabelPlacement.OverPoint
        except Exception:
            try:
                settings.placement = QgsPalLayerSettings.OverPoint
            except Exception:
                pass

        text_format = QgsTextFormat()
        text_format.setSize(9.0)
        text_format.setColor(QColor('#202020'))
        settings.setFormat(text_format)

        # Data-defined rotation is broadly supported in QGIS 3.x. Height is
        # retained as an attribute but is not forced as a font size because CAD
        # drawing units can be very different from typographic points.
        try:
            ddp = settings.dataDefinedProperties()
            if hasattr(QgsPalLayerSettings, 'Rotation'):
                ddp.setProperty(QgsPalLayerSettings.Rotation, QgsProperty.fromField('cad_rotation'))
            settings.setDataDefinedProperties(ddp)
        except Exception:
            pass

        layer.setLabeling(QgsVectorLayerSimpleLabeling(settings))
        layer.setLabelsEnabled(True)

    def _load_group(self, output_gpkg, source_name, style_mode, counts, feedback):
        project = QgsProject.instance()
        root = project.layerTreeRoot()
        group_name = 'CAD - ' + os.path.splitext(os.path.basename(source_name))[0]

        # Avoid silently merging into an unrelated pre-existing group.
        existing = root.findGroup(group_name)
        if existing is not None:
            suffix = 2
            candidate = '{} ({})'.format(group_name, suffix)
            while root.findGroup(candidate) is not None:
                suffix += 1
                candidate = '{} ({})'.format(group_name, suffix)
            group_name = candidate

        group = root.insertGroup(0, group_name)

        labels = {
            'points': self.tr('Points', 'Pontos'),
            'lines': self.tr('Lines', 'Linhas'),
            'polygons': self.tr('Polygons', 'Polígonos'),
            'texts': self.tr('Texts', 'Textos'),
        }

        loaded = 0
        for family in ('points', 'lines', 'polygons', 'texts'):
            if counts.get(family, 0) <= 0:
                continue
            uri = '{}|layername={}'.format(output_gpkg, family)
            layer = QgsVectorLayer(uri, labels[family], 'ogr')
            if not layer.isValid():
                feedback.reportError(
                    self.tr('Could not load output layer: {}', 'Não foi possível carregar a camada de saída: {}').format(family),
                    fatalError=False
                )
                continue

            if family == 'texts':
                self._apply_text_labels(layer, style_mode)
            else:
                self._apply_categorized_style(layer, family, style_mode)

            layer.triggerRepaint()
            project.addMapLayer(layer, False)
            group.addLayer(layer)
            loaded += 1

        if loaded == 0:
            root.removeChildNode(group)

    # ------------------------------------------------------------------
    # Processing
    # ------------------------------------------------------------------

    def processAlgorithm(self, parameters, context, feedback):
        input_path = self.parameterAsFile(parameters, self.INPUT, context)
        output_gpkg = self.parameterAsFileOutput(parameters, self.OUTPUT, context)
        block_mode = self.parameterAsEnum(parameters, self.BLOCKS, context)
        preserve_curves = self.parameterAsBool(parameters, self.CURVES, context)
        closed_as_polygons = self.parameterAsBool(parameters, self.CLOSED_AS_POLYGONS, context)
        style_mode = self.parameterAsEnum(parameters, self.STYLE, context)
        use_oda_fallback = self.parameterAsBool(parameters, self.ODA_FALLBACK, context)

        if not input_path or not os.path.isfile(input_path):
            raise QgsProcessingException(
                self.tr('The CAD file does not exist.', 'O arquivo CAD não existe.')
            )

        ext = os.path.splitext(input_path)[1].lower()
        if ext not in ('.dxf', '.dwg'):
            raise QgsProcessingException(
                self.tr('Select a DXF or DWG file.', 'Selecione um arquivo DXF ou DWG.')
            )

        if not output_gpkg:
            raise QgsProcessingException(self.invalidSinkError(parameters, self.OUTPUT))

        if os.path.exists(output_gpkg):
            raise QgsProcessingException(
                self.tr(
                    'The output GeoPackage already exists. Choose another file name or remove the existing file.',
                    'O GeoPackage de saída já existe. Escolha outro nome ou remova o arquivo existente.'
                )
            )

        out_dir = os.path.dirname(os.path.abspath(output_gpkg))
        if not os.path.isdir(out_dir):
            raise QgsProcessingException(
                self.tr('The output directory does not exist.', 'A pasta de saída não existe.')
            )

        feedback.pushInfo(
            self.tr('Opening CAD file...', 'Abrindo arquivo CAD...')
        )

        # Metadata inspection uses an expanded-block view where possible.
        # ``working_path`` remains the original CAD file unless a DWG fallback is
        # required, in which case it points to a temporary DXF created by ODA.
        working_path = input_path
        oda_temp = None
        inspect_ds, open_error = self._try_open_dataset(working_path, inline_blocks=True)

        if inspect_ds is None and ext == '.dwg' and use_oda_fallback:
            feedback.reportError(
                self.tr(
                    'GDAL/OGR could not open the DWG directly: {}',
                    'O GDAL/OGR não conseguiu abrir o DWG diretamente: {}'
                ).format(open_error or self.tr('unknown error', 'erro desconhecido')),
                fatalError=False
            )

            oda_temp = tempfile.TemporaryDirectory(prefix='lftools_oda_')
            converted_path, oda_error = self._convert_dwg_with_oda(
                input_path, feedback, oda_temp.name
            )
            if converted_path:
                working_path = converted_path
                inspect_ds, converted_open_error = self._try_open_dataset(
                    working_path, inline_blocks=True
                )
                if inspect_ds is None:
                    oda_temp.cleanup()
                    oda_temp = None
                    raise QgsProcessingException(
                        self.tr(
                            'The DWG was converted by ODA, but GDAL/OGR could not open the resulting DXF. {}',
                            'O DWG foi convertido pelo ODA, mas o GDAL/OGR não conseguiu abrir o DXF resultante. {}'
                        ).format(converted_open_error)
                    )
            else:
                oda_temp.cleanup()
                oda_temp = None
                details = open_error or ''
                if oda_error:
                    details = (details + '\n' + oda_error).strip()
                raise QgsProcessingException(
                    self.tr(
                        'This QGIS/GDAL installation cannot read the selected DWG file, and the optional ODA fallback was not available. Convert the drawing to DXF (or DWG R2000 when using libopencad) and try again. {}',
                        'Esta instalação do QGIS/GDAL não consegue ler o arquivo DWG selecionado e a alternativa opcional pelo ODA não estava disponível. Converta o desenho para DXF (ou DWG R2000 quando estiver usando libopencad) e tente novamente. {}'
                    ).format(details)
                )

        if inspect_ds is None:
            if ext == '.dwg':
                details = open_error or self.tr('Unknown GDAL/OGR error.', 'Erro desconhecido do GDAL/OGR.')
                raise QgsProcessingException(
                    self.tr(
                        'This QGIS/GDAL installation cannot read the selected DWG file. Enable the ODA fallback, convert the drawing to DXF, or save it as DWG R2000 when using libopencad. GDAL/OGR message: {}',
                        'Esta instalação do QGIS/GDAL não consegue ler o arquivo DWG selecionado. Ative a alternativa pelo ODA, converta o desenho para DXF ou salve-o como DWG R2000 quando estiver usando libopencad. Mensagem do GDAL/OGR: {}'
                    ).format(details)
                )
            raise QgsProcessingException(
                self.tr(
                    'The CAD file could not be opened by GDAL/OGR. Check whether the file is valid and the DXF driver is available. {}',
                    'O arquivo CAD não pôde ser aberto pelo GDAL/OGR. Verifique se o arquivo é válido e se o driver DXF está disponível. {}'
                ).format(open_error or '')
            )

        # CRS sidecar lookup intentionally uses the original filename, while unit
        # detection uses the actual file being imported (including ODA DXF).
        crs = self._resolve_crs(parameters, context, inspect_ds, input_path, feedback)
        unit_key = self._resolve_units(parameters, context, working_path, inspect_ds, crs, feedback)
        scale_factor = self._unit_scale(unit_key, crs)

        if abs(scale_factor - 1.0) > 1e-12:
            feedback.pushInfo(
                self.tr(
                    'Coordinate scale applied to match CRS units: {:.12g}',
                    'Escala aplicada às coordenadas para compatibilizar com as unidades do SRC: {:.12g}'
                ).format(scale_factor)
            )

        driver = ogr.GetDriverByName('GPKG')
        if driver is None:
            raise QgsProcessingException(
                self.tr('The GDAL GeoPackage driver is not available.', 'O driver GeoPackage do GDAL não está disponível.')
            )

        out_ds = driver.CreateDataSource(output_gpkg)
        if out_ds is None:
            raise QgsProcessingException(
                self.tr('Could not create the output GeoPackage.', 'Não foi possível criar o GeoPackage de saída.')
            )

        try:
            output_layers = self._create_output_layers(out_ds, crs, preserve_curves)
            counts = {'points': 0, 'lines': 0, 'polygons': 0, 'texts': 0, 'ignored': 0}

            # 0 = expanded geometries
            # 1 = expanded geometries + separate insertion-point pass
            # 2 = no expansion (insertion points retained by OGR when supported)
            if block_mode in (0, 1):
                ds_main, reopen_error = self._try_open_dataset(working_path, inline_blocks=True)
            else:
                ds_main, reopen_error = self._try_open_dataset(working_path, inline_blocks=False)

            if ds_main is None:
                raise QgsProcessingException(
                    self.tr('The CAD dataset could not be reopened for import. {}', 'O conjunto de dados CAD não pôde ser reaberto para importação. {}').format(reopen_error or '')
                )

            self._import_pass(
                ds_main, output_layers, input_path, scale_factor,
                preserve_curves, closed_as_polygons, feedback, counts,
                only_block_inserts=False
            )
            ds_main = None

            if block_mode == 1 and not feedback.isCanceled():
                ds_inserts, insert_error = self._try_open_dataset(working_path, inline_blocks=False)
                if ds_inserts is not None:
                    self._import_pass(
                        ds_inserts, output_layers, input_path, scale_factor,
                        preserve_curves, closed_as_polygons, feedback, counts,
                        only_block_inserts=True
                    )
                    ds_inserts = None
                elif insert_error:
                    feedback.reportError(
                        self.tr(
                            'Block insertion points could not be read: {}',
                            'Os pontos de inserção dos blocos não puderam ser lidos: {}'
                        ).format(insert_error),
                        fatalError=False
                    )

            inspect_ds = None
            out_ds = None

        except Exception:
            inspect_ds = None
            out_ds = None
            if oda_temp is not None:
                try:
                    oda_temp.cleanup()
                except Exception:
                    pass
                oda_temp = None
            # Remove incomplete output when processing fails.
            try:
                if os.path.exists(output_gpkg):
                    driver.DeleteDataSource(output_gpkg)
            except Exception:
                pass
            raise

        if feedback.isCanceled():
            if oda_temp is not None:
                try:
                    oda_temp.cleanup()
                except Exception:
                    pass
                oda_temp = None
            try:
                if os.path.exists(output_gpkg):
                    driver.DeleteDataSource(output_gpkg)
            except Exception:
                pass
            return {}

        if oda_temp is not None:
            try:
                oda_temp.cleanup()
            except Exception:
                pass
            oda_temp = None

        total_imported = counts['points'] + counts['lines'] + counts['polygons'] + counts['texts']
        if total_imported == 0:
            try:
                driver.DeleteDataSource(output_gpkg)
            except Exception:
                pass
            raise QgsProcessingException(
                self.tr('No supported CAD entities were imported.', 'Nenhuma entidade CAD compatível foi importada.')
            )

        feedback.pushInfo(
            self.tr(
                'Imported entities - Points: {}; Lines: {}; Polygons: {}; Texts: {}.',
                'Entidades importadas - Pontos: {}; Linhas: {}; Polígonos: {}; Textos: {}.'
            ).format(counts['points'], counts['lines'], counts['polygons'], counts['texts'])
        )

        if counts['ignored']:
            feedback.pushInfo(
                self.tr('Ignored/unsupported entities: {}.', 'Entidades ignoradas/não suportadas: {}.').format(counts['ignored'])
            )

        # Load only non-empty layers in one project group.
        self._load_group(output_gpkg, input_path, style_mode, counts, feedback)

        feedback.setProgress(100)
        feedback.pushInfo(
            self.tr('CAD import completed successfully!', 'Importação CAD concluída com sucesso!')
        )
        feedback.pushInfo(
            self.tr('Leandro Franca - Cartographic Engineer', 'Leandro França - Eng. Cartógrafo')
        )

        return {self.OUTPUT: output_gpkg}
