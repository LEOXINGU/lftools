# -*- coding: utf-8 -*-
"""
Immersive Cloud - Automated Dependency Downloader & Manager
Part of LFTools for QGIS
"""

import os
import shutil
import zipfile
import subprocess
import urllib.request
import urllib.error
import ssl
from typing import Dict, Tuple

from qgis.PyQt.QtCore import QThread, pyqtSignal

from .config import (
    POTREE_CONVERTER_URL,
    POTREE_DESKTOP_URL,
    get_bin_dir,
    get_converter_path,
    get_desktop_template_path,
)


def test_converter_executable(exe_path: str) -> Tuple[bool, str]:
    """
    Testa se o executável do PotreeConverter consegue ser executado no sistema.
    """
    if not exe_path or not os.path.isfile(exe_path):
        return False, "Arquivo PotreeConverter.exe não encontrado."

    try:
        creationflags = 0
        if os.name == "nt":
            creationflags = subprocess.CREATE_NO_WINDOW

        proc = subprocess.run(
            [exe_path, "--help"],
            capture_output=True,
            text=True,
            timeout=8,
            creationflags=creationflags
        )
        out = (proc.stdout or "") + (proc.stderr or "")
        if proc.returncode == 0 or "PotreeConverter" in out or "usage" in out.lower() or "input" in out.lower():
            return True, "PotreeConverter funcionando perfeitamente."
        return False, f"Código de saída inesperado ({proc.returncode}): {out[:150]}"
    except subprocess.TimeoutExpired:
        return False, "Tempo limite excedido ao testar PotreeConverter.exe."
    except Exception as e:
        return False, f"Falha ao executar PotreeConverter.exe: {e}"


def check_dependencies(custom_conv: str = "", custom_desk: str = "") -> Dict:
    """
    Verifica se os componentes 3D necessários (Converter e Desktop) estão instalados e prontos.
    """
    conv_path = get_converter_path(custom_conv)
    desk_path = get_desktop_template_path(custom_desk)

    conv_ok = False
    conv_msg = ""
    if os.path.isfile(conv_path):
        conv_ok, conv_msg = test_converter_executable(conv_path)
    else:
        conv_msg = "PotreeConverter.exe não encontrado."

    desk_ok = False
    if os.path.isdir(desk_path):
        has_index = False
        has_bat_or_exe = False
        for root, _, files in os.walk(desk_path):
            if "index.html" in files:
                has_index = True
            if "PotreeDesktop.bat" in files or "electron.exe" in files:
                has_bat_or_exe = True
            if has_index and has_bat_or_exe:
                desk_ok = True
                break

    ready = conv_ok and desk_ok
    status_text = "Pronto para uso" if ready else "Componentes ausentes ou incompletos"

    return {
        "ready": ready,
        "converter_ok": conv_ok,
        "desktop_ok": desk_ok,
        "converter_path": conv_path if conv_ok else "",
        "desktop_path": desk_path if desk_ok else "",
        "message": f"{status_text} (Conversor: {'OK' if conv_ok else 'Pendente'}, Visualizador: {'OK' if desk_ok else 'Pendente'})"
    }


class PotreeDependencyDownloader(QThread):
    """
    Thread responsável pelo download em segundo plano e extração silenciosa dos pacotes Potree.
    """
    progress_signal = pyqtSignal(int, str)
    finished_signal = pyqtSignal(bool, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.is_cancelled = False

    def cancel(self):
        self.is_cancelled = True

    def _download_file(self, url: str, target_path: str, start_pct: int, end_pct: int, label: str):
        """Baixa um arquivo via HTTP informando o progresso da fatia de porcentagem."""
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) LFTools-QGIS/1.0"}
        )
        try:
            ssl_ctx = ssl.create_default_context()
            resp = urllib.request.urlopen(req, timeout=60, context=ssl_ctx)
        except Exception:
            ssl_ctx = ssl._create_unverified_context()
            resp = urllib.request.urlopen(req, timeout=60, context=ssl_ctx)

        with resp as response, open(target_path, "wb") as out_file:
            total_size = response.getheader("Content-Length")
            total_size = int(total_size) if total_size else 0
            downloaded = 0
            block_size = 65536  # 64 KB

            while True:
                if self.is_cancelled:
                    raise Exception("Download cancelado pelo usuário.")
                buffer = response.read(block_size)
                if not buffer:
                    break
                downloaded += len(buffer)
                out_file.write(buffer)

                if total_size > 0:
                    fraction = downloaded / total_size
                    current_pct = int(start_pct + fraction * (end_pct - start_pct))
                    mb_down = downloaded / (1024 * 1024)
                    mb_total = total_size / (1024 * 1024)
                    self.progress_signal.emit(current_pct, f"{label} ({mb_down:.1f}MB / {mb_total:.1f}MB)...")
                else:
                    self.progress_signal.emit(start_pct, f"{label}...")

    def run(self):
        bin_dir = get_bin_dir()
        temp_zip_dir = os.path.join(bin_dir, "_tmp_dl")
        os.makedirs(temp_zip_dir, exist_ok=True)

        converter_zip = os.path.join(temp_zip_dir, "PotreeConverter.zip")
        desktop_zip = os.path.join(temp_zip_dir, "PotreeDesktop.zip")

        try:
            # 1. Download do PotreeConverter (14 MB, 0% a 25%)
            self.progress_signal.emit(2, "Iniciando download do PotreeConverter (14 MB)...")
            self._download_file(POTREE_CONVERTER_URL, converter_zip, 2, 25, "Baixando PotreeConverter")

            # 2. Extração do PotreeConverter (25% a 30%)
            self.progress_signal.emit(26, "Extraindo PotreeConverter...")
            conv_target = os.path.join(bin_dir, "PotreeConverter")
            if os.path.exists(conv_target):
                shutil.rmtree(conv_target, ignore_errors=True)
            os.makedirs(conv_target, exist_ok=True)

            with zipfile.ZipFile(converter_zip, "r") as z:
                z.extractall(conv_target)

            # Teste rápido do executável
            conv_path = get_converter_path()
            conv_ok, conv_err = test_converter_executable(conv_path)
            if not conv_ok:
                raise Exception(f"Falha de validação do PotreeConverter: {conv_err}")

            # 3. Download do PotreeDesktop (105 MB, 30% a 85%)
            self.progress_signal.emit(30, "Iniciando download do PotreeDesktop (105 MB)...")
            self._download_file(POTREE_DESKTOP_URL, desktop_zip, 30, 85, "Baixando PotreeDesktop")

            # 4. Extração do PotreeDesktop (85% a 98%)
            self.progress_signal.emit(86, "Extraindo PotreeDesktop...")
            desk_target = os.path.join(bin_dir, "PotreeDesktop")
            if os.path.exists(desk_target):
                shutil.rmtree(desk_target, ignore_errors=True)
            os.makedirs(desk_target, exist_ok=True)

            with zipfile.ZipFile(desktop_zip, "r") as z:
                z.extractall(desk_target)

            # 5. Limpeza dos arquivos compactados temporários
            shutil.rmtree(temp_zip_dir, ignore_errors=True)

            # Verificação final
            status = check_dependencies()
            if status["ready"]:
                self.progress_signal.emit(100, "Componentes 3D prontos para uso.")
                self.finished_signal.emit(True, "Componentes 3D configurados e testados com sucesso!")
            else:
                self.finished_signal.emit(False, f"Componentes extraídos com ressalvas: {status['message']}")

        except Exception as e:
            shutil.rmtree(temp_zip_dir, ignore_errors=True)
            self.finished_signal.emit(False, f"Erro na preparação dos componentes: {e}")
