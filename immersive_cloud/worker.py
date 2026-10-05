# -*- coding: utf-8 -*-
"""
Immersive Cloud - Processing Worker Thread
Part of LFTools for QGIS
Supports Portuguese, Spanish, and English based on active QGIS locale.
"""

import os
import re
import shutil
import subprocess
import platform
from datetime import datetime

from qgis.PyQt.QtCore import QThread, pyqtSignal
from qgis.core import QgsApplication

from ..translations.translate import translate
from .config import get_converter_path, get_desktop_template_path
from .downloader import test_converter_executable
from .template import generate_html_content, generate_guide_html


class ImmersiveCloudWorker(QThread):
    """
    Worker assíncrono para conversão de nuvem de pontos e montagem do pacote 3D.
    """
    log_signal = pyqtSignal(str)
    progress_signal = pyqtSignal(int)
    finished_signal = pyqtSignal(bool, str)

    def __init__(
        self,
        las_file: str,
        out_dir: str,
        project_name: str,
        client_name: str = "",
        company_name: str = "",
        contact: str = "",
        address: str = "",
        point_size: float = 0.5,
        point_shape: str = "CIRCLE",
        point_size_type: str = "ADAPTIVE",
        point_budget: int = 3000000,
        edl_enabled: bool = True,
        fov: int = 60,
        custom_converter_exe: str = "",
        custom_desktop_dir: str = "",
        parent=None
    ):
        super().__init__(parent)
        self.las_file = las_file
        self.out_dir = out_dir
        self.project_name = project_name
        self.client_name = client_name
        self.company_name = company_name
        self.contact = contact
        self.address = address
        self.point_size = point_size
        self.point_shape = point_shape
        self.point_size_type = point_size_type
        self.point_budget = point_budget
        self.edl_enabled = edl_enabled
        self.fov = fov
        self.custom_converter_exe = custom_converter_exe
        self.custom_desktop_dir = custom_desktop_dir
        self.is_cancelled = False

    def tr(self, *string):
        return translate(string, QgsApplication.locale()[:2])

    def cancel(self):
        self.is_cancelled = True

    def run(self):
        try:
            loc = QgsApplication.locale()[:2].lower()
            self.progress_signal.emit(5)
            self.log_signal.emit(self.tr("Starting 3D package generation...", "Iniciando geração do pacote 3D..."))

            # 1. Validação dos caminhos dos componentes
            converter_exe = get_converter_path(self.custom_converter_exe)
            if not converter_exe or not os.path.isfile(converter_exe):
                raise Exception(self.tr("PotreeConverter executable not found.", "Executável PotreeConverter não encontrado."))

            conv_ok, conv_msg = test_converter_executable(converter_exe)
            if not conv_ok:
                raise Exception(f"{self.tr('PotreeConverter not available:', 'PotreeConverter não disponível:')} {conv_msg}")

            desktop_template = get_desktop_template_path(self.custom_desktop_dir)
            if not desktop_template or not os.path.isdir(desktop_template):
                raise Exception(self.tr("PotreeDesktop template not found. Please verify 3D components.", "Template do PotreeDesktop não encontrado. Verifique os componentes 3D."))

            # 2. Encerramento de processos anteriores no Windows
            self.log_signal.emit(self.tr("Checking for previous running viewer instances...", "Verificando instâncias anteriores em execução..."))
            if platform.system() == "Windows":
                subprocess.run(
                    ["taskkill", "/F", "/IM", "PotreeDesktop.exe"],
                    capture_output=True,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
                subprocess.run(
                    ["taskkill", "/F", "/IM", "electron.exe"],
                    capture_output=True,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )

            # 3. Preparação das pastas do projeto
            safe_name = re.sub(r'[\\/*?:"<>| ]', '_', self.project_name.strip())
            if not safe_name:
                safe_name = "Projeto_3D"

            final_project_dir = os.path.join(self.out_dir, safe_name)
            self.final_project_dir = final_project_dir
            viewer_dir = os.path.join(final_project_dir, "Visualizador_3D")

            self.log_signal.emit(f"{self.tr('Structuring output directory:', 'Estruturando diretório de saída:')} {final_project_dir}")
            if os.path.exists(final_project_dir):
                self.log_signal.emit(self.tr("Cleaning previous processing files...", "Limpando arquivos de processamento anterior..."))
                shutil.rmtree(final_project_dir, ignore_errors=True)

            os.makedirs(viewer_dir, exist_ok=True)

            # 4. Cópia dos arquivos base do visualizador
            self.log_signal.emit(self.tr("Copying standalone 3D viewer base...", "Copiando base do visualizador 3D autônomo..."))
            self.progress_signal.emit(10)

            for item in os.listdir(desktop_template):
                s = os.path.join(desktop_template, item)
                d = os.path.join(viewer_dir, item)
                if os.path.isdir(s):
                    shutil.copytree(s, d, dirs_exist_ok=True)
                else:
                    shutil.copy2(s, d)

            # Renomear launcher .bat conforme idioma
            bat_name = "1_CLIQUE_AQUI_PARA_ABRIR.bat"
            if loc == "es":
                bat_name = "1_HAGA_CLIC_AQUI_PARA_ABRIR.bat"
            elif loc == "en":
                bat_name = "1_CLICK_HERE_TO_OPEN.bat"

            bat_antigo = os.path.join(viewer_dir, "PotreeDesktop.bat")
            bat_novo = os.path.join(viewer_dir, bat_name)
            if os.path.isfile(bat_antigo):
                if os.path.exists(bat_novo):
                    os.remove(bat_novo)
                os.rename(bat_antigo, bat_novo)

            # 5. Diretório de saída da nuvem convertida
            pc_dir = os.path.join(viewer_dir, "pointclouds", "projeto_atual")
            if os.path.exists(pc_dir):
                shutil.rmtree(pc_dir, ignore_errors=True)
            os.makedirs(pc_dir, exist_ok=True)

            # 6. Execução do PotreeConverter
            self.log_signal.emit(self.tr("Starting point cloud conversion with PotreeConverter...", "Iniciando conversão da nuvem de pontos com PotreeConverter..."))
            self.progress_signal.emit(25)

            cmd = [converter_exe, self.las_file, "-o", pc_dir]
            creationflags = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
            converter_dir = os.path.dirname(converter_exe)

            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                cwd=converter_dir,
                creationflags=creationflags
            )

            pct_pattern = re.compile(r'(\d+)%')

            for line in process.stdout:
                line_str = line.strip()
                if not line_str:
                    continue
                self.log_signal.emit(line_str)

                match = pct_pattern.search(line_str)
                if match:
                    val = int(match.group(1))
                    mapped_progress = int(25 + (val * 0.65))
                    self.progress_signal.emit(mapped_progress)

            process.wait()
            if process.returncode != 0:
                raise Exception(f"{self.tr('PotreeConverter failed with return code', 'PotreeConverter falhou com código de saída')} {process.returncode}.")

            # 7. Injeção e personalização do HTML
            self.log_signal.emit(self.tr("Customizing viewer interface and metadata...", "Personalizando interface do visualizador e metadados..."))
            self.progress_signal.emit(92)

            html_content = generate_html_content(
                project_name=self.project_name,
                client_name=self.client_name,
                company_name=self.company_name,
                contact=self.contact,
                address=self.address,
                point_size=self.point_size,
                point_shape=self.point_shape,
                point_size_type=self.point_size_type,
                point_budget=self.point_budget,
                edl_enabled=self.edl_enabled,
                fov=self.fov,
                locale=loc
            )

            html_path = os.path.join(viewer_dir, "index.html")
            with open(html_path, "w", encoding="utf-8") as f:
                f.write(html_content)

            # 8. Criação de guia visual em HTML de orientação para o cliente final
            self.log_signal.emit(self.tr("Generating interactive HTML 3D user guide...", "Gerando guia interativo em HTML de instruções do modelo 3D..."))
            date_today = datetime.now().strftime("%d/%m/%Y")
            
            guide_html = generate_guide_html(
                project_name=self.project_name,
                client_name=self.client_name,
                company_name=self.company_name,
                contact=self.contact,
                address=self.address,
                date_str=date_today,
                locale=loc
            )

            guide_filename = "COMO_VISUALIZAR_O_MODELO_3D.html"
            if loc == "es":
                guide_filename = "COMO_VISUALIZAR_EL_MODELO_3D.html"
            elif loc == "en":
                guide_filename = "HOW_TO_VIEW_THE_3D_MODEL.html"

            guide_path = os.path.join(final_project_dir, guide_filename)
            with open(guide_path, "w", encoding="utf-8") as f:
                f.write(guide_html)

            self.progress_signal.emit(100)
            msg = (
                f"{self.tr('SUCCESS! Your standalone 3D package is ready at:', 'SUCESSO! O seu pacote 3D autônomo está pronto em:')}\n"
                f"{final_project_dir}\n\n"
                f"{self.tr('Open the guide file to view interactive instructions:', 'Abra o arquivo de guia para visualizar as instruções interativas:')} '{guide_filename}'"
            )
            self.finished_signal.emit(True, msg)

        except Exception as e:
            self.finished_signal.emit(False, str(e))
