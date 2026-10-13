# -*- coding: utf-8 -*-
"""
Immersive Cloud - Configuration & Defaults
Part of LFTools for QGIS
"""

import os
from qgis.core import QgsApplication

# URLs oficiais de releases públicas do Potree
POTREE_DESKTOP_URL = "https://github.com/potree/PotreeDesktop/releases/download/1.8.2/PotreeDesktop_1.8.2_x64_windows.zip"
POTREE_CONVERTER_URL = "https://github.com/potree/PotreeConverter/releases/download/2.1.5/PotreeConverter_2.1.5_x64_windows.zip"

POTREE_DESKTOP_ZIP_NAME = "PotreeDesktop_1.8.2_x64_windows.zip"
POTREE_CONVERTER_ZIP_NAME = "PotreeConverter_2.1.5_x64_windows.zip"

TOOL_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_BIN_DIR = os.path.join(TOOL_DIR, "bin")

SETTINGS_PREFIX = "lftools/immersive_cloud/"

DEFAULT_SETTINGS = {
    "las_file": "",
    "out_dir": "",
    "project_name": "Projeto_GeoOne_3D",
    "client_name": "Parceiro GeoOne",
    "company_name": "Geonista da Silva",
    "contact": "suporte@geoone.com.br",
    "address": "Florianópolis - SC",
    "point_size": 0.5,
    "point_shape": "CIRCLE",       # CIRCLE ou SQUARE
    "point_size_type": "ADAPTIVE", # ADAPTIVE ou FIXED
    "point_budget": 3000000,
    "edl_enabled": True,
    "fov": 60,
    "custom_converter_exe": "",
    "custom_desktop_dir": "",
}


def get_bin_dir() -> str:
    """
    Retorna o diretório base para armazenamento dos binários.
    Tenta utilizar a pasta 'bin' local da ferramenta. Caso o diretório do plugin
    seja somente leitura, recorre à pasta de perfil do usuário no QGIS.
    """
    try:
        os.makedirs(DEFAULT_BIN_DIR, exist_ok=True)
        test_file = os.path.join(DEFAULT_BIN_DIR, ".write_test")
        with open(test_file, "w") as f:
            f.write("ok")
        os.remove(test_file)
        return DEFAULT_BIN_DIR
    except Exception:
        fallback_dir = os.path.join(QgsApplication.qgisSettingsDirPath(), "lftools_immersive_cloud", "bin")
        os.makedirs(fallback_dir, exist_ok=True)
        return fallback_dir


def get_converter_path(custom_path: str = "") -> str:
    """Retorna o caminho para o executável PotreeConverter.exe."""
    if custom_path and os.path.isfile(custom_path):
        return custom_path
    
    bin_dir = get_bin_dir()
    default_exe = os.path.join(bin_dir, "PotreeConverter", "PotreeConverter.exe")
    if os.path.isfile(default_exe):
        return default_exe
    
    # Busca recursiva dentro da pasta bin se estiver em subpasta
    conv_dir = os.path.join(bin_dir, "PotreeConverter")
    if os.path.isdir(conv_dir):
        for root, _, files in os.walk(conv_dir):
            if "PotreeConverter.exe" in files:
                return os.path.join(root, "PotreeConverter.exe")
    return default_exe


def get_desktop_template_path(custom_dir: str = "") -> str:
    """Retorna o caminho para a pasta base do PotreeDesktop."""
    if custom_dir and os.path.isdir(custom_dir):
        return custom_dir
    
    bin_dir = get_bin_dir()
    default_dir = os.path.join(bin_dir, "PotreeDesktop")
    if os.path.isdir(default_dir):
        # Validação rápida de presença dos arquivos essenciais
        for root, _, files in os.walk(default_dir):
            if "index.html" in files and ("PotreeDesktop.bat" in files or "electron.exe" in files):
                return root
    return default_dir
