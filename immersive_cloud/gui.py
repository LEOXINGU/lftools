# -*- coding: utf-8 -*-
"""
Immersive Cloud - GUI DockWidget
Part of LFTools for QGIS
Strictly follows QGIS Plugin UI Guidelines:
- Lean layout
- Collapsible advanced section (starts collapsed)
- Exclusive descriptive Cause-and-Effect tooltips on all inputs
- State persistence with QgsSettings
- Native QGIS styling
- Factory defaults reset
- Anti-Gap / Sticky Top Layout & Responsive QScrollArea
- Full Internationalization (PT, ES, EN)
"""

import os
import re
import platform
import subprocess
from qgis.PyQt.QtWidgets import (
    QDockWidget,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QLineEdit,
    QDoubleSpinBox,
    QSpinBox,
    QComboBox,
    QCheckBox,
    QPushButton,
    QTextEdit,
    QLabel,
    QProgressBar,
    QMessageBox,
    QApplication,
    QScrollArea,
    QFrame,
    QSizePolicy,
)
from qgis.PyQt.QtCore import Qt, QUrl
from qgis.PyQt.QtGui import QDesktopServices
from qgis.gui import QgsFileWidget, QgsCollapsibleGroupBox
from qgis.core import QgsSettings, QgsApplication

from ..translations.translate import translate
from .config import (
    SETTINGS_PREFIX,
    DEFAULT_SETTINGS,
    get_converter_path,
    get_desktop_template_path,
)
from .downloader import (
    check_dependencies,
    PotreeDependencyDownloader,
)
from .worker import ImmersiveCloudWorker


class ImmersiveCloudDockWidget(QDockWidget):
    """
    DockWidget nativo do QGIS para geração de pacotes 3D imersivos.
    """

    def __init__(self, parent=None):
        super().__init__("Visualizador 3D Imersivo", parent)
        self.setWindowTitle(self.tr("Immersive 3D Viewer", "Visualizador 3D Imersivo"))
        self.setObjectName("LFTools_ImmersiveCloudDockWidget")
        self.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea)

        self.settings = QgsSettings()
        self.worker = None
        self.download_worker = None
        self.is_silent_download = False

        self._init_ui()
        self._load_settings()
        self.refresh_dependency_status(auto_download_if_missing=True)

    def tr(self, *string):
        """Traduz mensagens dinamicamente de acordo com o idioma ativo do QGIS."""
        return translate(string, QgsApplication.locale()[:2])

    def _init_ui(self):
        container = QWidget()
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(6, 6, 6, 6)
        main_layout.setSpacing(5)

        # -------------------------------------------------------------
        # 1. PARÂMETROS PRINCIPAIS (Layout Enxuto)
        # -------------------------------------------------------------
        form_main = QFormLayout()
        form_main.setContentsMargins(2, 2, 2, 2)
        form_main.setSpacing(4)

        # Arquivo de Nuvem de Pontos
        self.fw_las = QgsFileWidget()
        self.fw_las.setFilter(self.tr("Point Clouds (*.las *.laz)", "Nuvens de Pontos (*.las *.laz)"))
        self.fw_las.setStorageMode(QgsFileWidget.GetFile)
        self.fw_las.setToolTip(
            self.tr(
                "Select the LAS or LAZ file containing the georeferenced point cloud.\n"
                "Cause and Effect: The converter will read 3D coordinates (X, Y, Z), RGB colors, and intensity from this file "
                "to structure the viewer's multi-resolution octree. LAZ files save disk space but require a few extra seconds to decompress.",
                "Selecione o arquivo LAS ou LAZ contendo a nuvem de pontos georreferenciada.\n"
                "Causa e Efeito: O conversor lerá as coordenadas 3D (X, Y, Z), cores RGB e intensidade deste arquivo "
                "para estruturar a octree multi-resolução do visualizador. Arquivos LAZ ocupam menos espaço, mas podem levar "
                "poucos segundos adicionais para descompressão durante a geração."
            )
        )
        form_main.addRow(self.tr("Point Cloud (.las/.laz):", "Nuvem (.las/.laz):"), self.fw_las)

        # Diretório de Saída
        self.fw_out = QgsFileWidget()
        self.fw_out.setStorageMode(QgsFileWidget.GetDirectory)
        self.fw_out.setToolTip(
            self.tr(
                "Directory where the full 3D deliverable folder will be created.\n"
                "Cause and Effect: The plugin will generate a project subfolder containing the portable standalone viewer "
                "('Visualizador_3D') and the fast-launch executable shortcut ('1_CLIQUE_AQUI_PARA_ABRIR.bat'), without requiring installation by your client.",
                "Diretório onde a pasta completa de entrega do projeto 3D será criada.\n"
                "Causa e Efeito: O plugin criará neste local uma subpasta com o nome do projeto contendo a estrutura portátil "
                "do visualizador ('Visualizador_3D') e o atalho executável ('1_CLIQUE_AQUI_PARA_ABRIR.bat'), sem necessidade "
                "de instalação por parte do seu cliente."
            )
        )
        form_main.addRow(self.tr("Output Folder:", "Pasta Destino:"), self.fw_out)

        # Nome do Projeto
        self.txt_project = QLineEdit()
        self.txt_project.setPlaceholderText(self.tr("Ex: Projeto_GeoOne_3D", "Ex: Projeto_GeoOne_3D"))
        self.txt_project.setToolTip(
            self.tr(
                "Descriptive project or mapped area name.\n"
                "Cause and Effect: Defines the project directory name on disk, the browser tab title, and the headline on the floating 3D HUD card.",
                "Nome descritivo do projeto ou área mapeada.\n"
                "Causa e Efeito: Esse texto define o nome da pasta de saída no disco, o título exibido na aba do navegador "
                "e o cabeçalho em destaque no painel HUD flutuante do modelo 3D. Evite caracteres especiais proibidos pelo sistema operacional."
            )
        )
        form_main.addRow(self.tr("Project Name:", "Nome do Projeto:"), self.txt_project)

        # Cliente / Contratante
        self.txt_client = QLineEdit()
        self.txt_client.setPlaceholderText(self.tr("Ex: Parceiro GeoOne", "Ex: Parceiro GeoOne"))
        self.txt_client.setToolTip(
            self.tr(
                "Client, institution, or landowner name.\n"
                "Cause and Effect: Displayed on the floating identification card of the 3D viewer. Omitted automatically if left blank.",
                "Nome do cliente, órgão ou proprietário atendido.\n"
                "Causa e Efeito: Se preenchido, será exibido no cartão de identificação visual flutuante do modelo 3D. "
                "Se deixado em branco, a linha de cliente é omitida automaticamente para manter o visual limpo."
            )
        )
        form_main.addRow(self.tr("Client/Agency:", "Cliente/Órgão:"), self.txt_client)

        # Empresa / Responsável
        self.txt_company = QLineEdit()
        self.txt_company.setPlaceholderText(self.tr("Ex: Geonista da Silva", "Ex: Geonista da Silva"))
        self.txt_company.setToolTip(
            self.tr(
                "Name of the company, office, or professional responsible for the survey.\n"
                "Cause and Effect: Identifies technical authorship on the viewer HUD delivered to the client.",
                "Nome da sua empresa, escritório ou profissional responsável técnico pelo levantamento.\n"
                "Causa e Efeito: Identifica a autoria técnica do modelo no cartão HUD flutuante do visualizador entregue ao cliente. "
                "Se deixado em branco, nenhuma marca de empresa será exibida."
            )
        )
        form_main.addRow(self.tr("Company/Author:", "Empresa/Autor:"), self.txt_company)

        form_widget = QWidget()
        form_widget.setLayout(form_main)
        try:
            form_widget.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)
        except AttributeError:
            form_widget.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        main_layout.addWidget(form_widget, stretch=0)

        # -------------------------------------------------------------
        # 2. SEÇÃO AVANÇADA COLAPSÁVEL (Inicia Colapsada)
        # -------------------------------------------------------------
        self.grp_advanced = QgsCollapsibleGroupBox(self.tr("Advanced Settings", "Configurações Avançadas"))
        self.grp_advanced.setCollapsed(True)
        try:
            self.grp_advanced.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)
        except AttributeError:
            self.grp_advanced.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        self.grp_advanced.setToolTip(
            self.tr(
                "Detailed 3D rendering parameters, complementary metadata, and dependency management.\n"
                "Cause and Effect: Adjusts visual point density, GPU memory budget, and conversion components.",
                "Configurações detalhadas de renderização 3D, metadados complementares e gestão de dependências.\n"
                "Causa e Efeito: Permite ajustar a finura gráfica da nuvem de pontos, limite de GPU e componentes de conversão."
            )
        )

        form_adv = QFormLayout()
        form_adv.setContentsMargins(4, 4, 4, 4)
        form_adv.setSpacing(4)

        # Contato
        self.txt_contact = QLineEdit()
        self.txt_contact.setPlaceholderText(self.tr("Ex: suporte@geoone.com.br", "Ex: suporte@geoone.com.br"))
        self.txt_contact.setToolTip(
            self.tr(
                "Direct contact channels (telephone, WhatsApp, email, or website).\n"
                "Cause and Effect: Displays a technical support footer on the 3D screen HUD card.",
                "Canais de contato direto (telefone, WhatsApp, e-mail ou website).\n"
                "Causa e Efeito: Aparece como rodapé de suporte técnico no cartão HUD flutuante da tela 3D. "
                "Facilita para que seu cliente entre em contato caso necessite de suporte no uso do visualizador."
            )
        )
        form_adv.addRow(self.tr("Contact:", "Contato:"), self.txt_contact)

        # Endereço / Localidade
        self.txt_address = QLineEdit()
        self.txt_address.setPlaceholderText(self.tr("Ex: Florianópolis - SC", "Ex: Florianópolis - SC"))
        self.txt_address.setToolTip(
            self.tr(
                "Survey location, municipality, or region.\n"
                "Cause and Effect: Adds geographic context to the viewer's HUD card. Leave blank if preferred.",
                "Localidade, município ou endereço de referência do trabalho.\n"
                "Causa e Efeito: Adiciona a coordenada contextual no painel HUD do visualizador. Deixe em branco se preferir não exibir."
            )
        )
        form_adv.addRow(self.tr("Location:", "Localidade:"), self.txt_address)

        # Tamanho do Ponto
        self.spin_point_size = QDoubleSpinBox()
        self.spin_point_size.setRange(0.05, 5.0)
        self.spin_point_size.setSingleStep(0.1)
        self.spin_point_size.setValue(0.5)
        self.spin_point_size.setToolTip(
            self.tr(
                "Base rendering size for points on the GPU.\n"
                "Cause and Effect: Smaller values (0.3 to 0.5) provide crisp photographic quality on dense clouds. "
                "Larger values (0.8 to 2.0) fill gaps in sparse clouds.",
                "Tamanho base de renderização dos pontos da nuvem na GPU.\n"
                "Causa e Efeito: Valores menores (ex: 0.3 a 0.5) proporcionam maior nitidez e aspecto fotográfico refinado em nuvens densas. "
                "Valores maiores (ex: 0.8 a 2.0) preenchem buracos em nuvens esparsas, mas podem gerar aspecto excessivamente granulado."
            )
        )
        form_adv.addRow(self.tr("Point Size:", "Tamanho Ponto:"), self.spin_point_size)

        # Geometria do Ponto (Shape)
        self.cmb_point_shape = QComboBox()
        self.cmb_point_shape.addItem(self.tr("Circle (Photorealistic)", "Círculo (Fotorealista)"), "CIRCLE")
        self.cmb_point_shape.addItem(self.tr("Square (Lightweight)", "Quadrado (Leve)"), "SQUARE")
        self.cmb_point_shape.setToolTip(
            self.tr(
                "Geometric shape of points drawn by the graphics card.\n"
                "Cause and Effect: 'Circle' produces smooth, continuous realistic visuals. "
                "'Square' consumes less GPU shader processing, suitable for legacy PCs.",
                "Formato geométrico dos pontos desenhados pela placa gráfica.\n"
                "Causa e Efeito: 'Círculo' produz uma visualização contínua e suave de alta qualidade visual. "
                "'Quadrado' consome menor processamento de shader, indicado para computadores clientes muito antigos sem placa dedicada."
            )
        )
        form_adv.addRow(self.tr("Point Shape:", "Forma Ponto:"), self.cmb_point_shape)

        # Perfil de Desempenho / Orçamento GPU
        self.cmb_budget_preset = QComboBox()
        self.cmb_budget_preset.addItem(self.tr("Balanced (3M points) [Recommended]", "Equilibrado (3M pontos) [Recomendado]"), 3000000)
        self.cmb_budget_preset.addItem(self.tr("Economic / Laptops (1M points)", "Econômico / Notebooks (1M pontos)"), 1000000)
        self.cmb_budget_preset.addItem(self.tr("High Quality (5M points)", "Alta Qualidade (5M pontos)"), 5000000)
        self.cmb_budget_preset.addItem(self.tr("Ultra / Maximum Detail (8M points)", "Ultra / Máximo Detalhe (8M pontos)"), 8000000)
        self.cmb_budget_preset.addItem(self.tr("Custom...", "Personalizado..."), -1)
        self.cmb_budget_preset.setToolTip(
            self.tr(
                "Defines graphics fidelity and video memory (VRAM) consumption.\n"
                "Cause and Effect:\n"
                "- Economic (1M): Instant loading and smooth FPS on entry-level notebooks.\n"
                "- Balanced (3M - Default): Crisp continuous display and excellent framerate (60 FPS).\n"
                "- High Quality / Ultra (5M to 8M): Maximum visual resolution for high-end GPUs.\n"
                "- Custom: Manually input exact point count.",
                "Define a fidelidade gráfica e o consumo de memória da placa de vídeo (GPU).\n"
                "Causa e Efeito:\n"
                "- Econômico (1 milhão de pontos): Carga imediata e fluidez máxima em qualquer notebook básico ou PC antigo.\n"
                "- Equilibrado (3 milhões de pontos - Padrão): Visualização nítida, contínua e excelente taxa de quadros (60 FPS).\n"
                "- Alta Qualidade / Ultra (5M a 8M de pontos): Máxima resolução em nuvens muito densas, exigindo GPU com mais VRAM.\n"
                "- Personalizado: Permite digitar manualmente a quantidade exata de pontos."
            )
        )
        self.cmb_budget_preset.currentIndexChanged.connect(self._on_budget_preset_changed)

        self.spin_budget = QSpinBox()
        self.spin_budget.setRange(200000, 30000000)
        self.spin_budget.setSingleStep(500000)
        self.spin_budget.setValue(3000000)
        self.spin_budget.setVisible(False)
        self.spin_budget.setToolTip(
            self.tr(
                "Exact maximum points loaded simultaneously in GPU memory.\n"
                "Cause and Effect: Higher values improve distant detail at the cost of higher VRAM usage.",
                "Quantidade exata de pontos carregados simultaneamente na GPU.\n"
                "Causa e Efeito: Valores maiores aumentam o alcance de visão detalhado à distância, consumindo mais memória de vídeo."
            )
        )

        budget_widget = QWidget()
        budget_layout = QVBoxLayout(budget_widget)
        budget_layout.setContentsMargins(0, 0, 0, 0)
        budget_layout.setSpacing(3)
        budget_layout.addWidget(self.cmb_budget_preset)
        budget_layout.addWidget(self.spin_budget)

        form_adv.addRow(self.tr("Quality / GPU:", "Qualidade / GPU:"), budget_widget)

        # Eye Dome Lighting (EDL)
        self.chk_edl = QCheckBox(self.tr("Enable EDL (Eye Dome Lighting)", "Habilitar EDL (Sombreamento de Contorno)"))
        self.chk_edl.setChecked(True)
        self.chk_edl.setToolTip(
            self.tr(
                "EDL post-processing shader that highlights silhouettes, borders, and depth.\n"
                "Cause and Effect: Emphasizes relief and structure in complex environments. Uncheck to view raw photograph colors.",
                "Efeito de pós-processamento EDL que realça arestas e profundidade na nuvem de pontos.\n"
                "Causa e Efeito: Quando ativado, cria um sombreado fino nos limites das feições (árvores, construções, desníveis), "
                "melhorando drasticamente a percepção de relevo e tridimensionalidade. Desmarque caso prefira apenas as cores puras da foto."
            )
        )
        form_adv.addRow(self.chk_edl)

        # Status dos Componentes e Download Automático
        self.lbl_dep_status = QLabel(self.tr("Checking 3D components...", "Verificando componentes 3D..."))
        self.lbl_dep_status.setWordWrap(True)
        self.lbl_dep_status.setToolTip(
            self.tr(
                "Indicates readiness of Potree conversion and viewer binaries.\n"
                "Cause and Effect: If missing, the plugin downloads and tests them automatically.",
                "Indica o estado de prontidão dos binários de conversão e visualização no sistema.\n"
                "Causa e Efeito: Se ausentes, o plugin pode baixá-los automaticamente com um clique para a pasta dedicada do plugin."
            )
        )
        form_adv.addRow(self.tr("3D Components:", "Componentes 3D:"), self.lbl_dep_status)

        self.btn_download_deps = QPushButton(self.tr("Download / Update 3D Components", "Baixar / Atualizar Componentes 3D"))
        self.btn_download_deps.setToolTip(
            self.tr(
                "Initiates background download and extraction of official PotreeConverter and PotreeDesktop packages.\n"
                "Cause and Effect: Downloads to internal plugin folder and tests execution, eliminating manual zip configuration.",
                "Inicia o download silencioso e extração dos pacotes oficiais PotreeConverter e PotreeDesktop diretamente do GitHub.\n"
                "Causa e Efeito: Baixa os arquivos necessários para a pasta interna do plugin e testa sua execução, dispensando a necessidade "
                "de qualquer configuração manual de arquivos ZIP."
            )
        )
        self.btn_download_deps.clicked.connect(self.start_dependency_download)
        form_adv.addRow(self.btn_download_deps)

        # Conversor Manual (100% Opcional - Avançado)
        self.chk_custom_conv = QCheckBox(self.tr("Use external PotreeConverter executable (Advanced)", "Utilizar executável PotreeConverter externo (Avançado)"))
        self.chk_custom_conv.setChecked(False)
        self.chk_custom_conv.setToolTip(
            self.tr(
                "Enables selection of an external PotreeConverter.exe executable.\n"
                "Cause and Effect: By default, LFTools uses its tested internal binaries. Enable only if air-gapped or using a custom build.",
                "Habilita a seleção manual de um executável PotreeConverter.exe externo.\n"
                "Causa e Efeito: Por padrão, o LFTools gerencia e utiliza automaticamente seus próprios binários internos testados. "
                "Marque esta opção apenas se estiver em uma rede isolada (air-gapped) ou desejar utilizar uma compilação customizada."
            )
        )
        self.chk_custom_conv.toggled.connect(self._on_custom_conv_toggled)

        self.fw_custom_conv = QgsFileWidget()
        self.fw_custom_conv.setFilter(self.tr("Executable (*.exe)", "Executável (*.exe)"))
        self.fw_custom_conv.setStorageMode(QgsFileWidget.GetFile)
        self.fw_custom_conv.setVisible(False)
        self.fw_custom_conv.setToolTip(
            self.tr(
                "Alternative path to a custom PotreeConverter.exe.\n"
                "Cause and Effect: Overrides the default internal converter with the specified executable.",
                "Caminho alternativo para um PotreeConverter.exe customizado (opcional).\n"
                "Causa e Efeito: Substitui o conversor padrão interno do LFTools pelo executável selecionado."
            )
        )

        form_adv.addRow(self.chk_custom_conv)
        form_adv.addRow(self.tr("Manual Executable:", "Executável Manual:"), self.fw_custom_conv)

        self.grp_advanced.setLayout(form_adv)
        main_layout.addWidget(self.grp_advanced, stretch=0)

        # -------------------------------------------------------------
        # 3. BARRA DE PROGRESSO & AÇÕES (Estilo Nativo)
        # -------------------------------------------------------------
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        main_layout.addWidget(self.progress_bar, stretch=0)

        actions_widget = QWidget()
        actions_layout = QHBoxLayout(actions_widget)
        actions_layout.setContentsMargins(0, 2, 0, 2)
        actions_layout.setSpacing(4)

        self.btn_run = QPushButton(self.tr("Generate 3D Package", "Gerar Pacote 3D"))
        self.btn_run.setToolTip(
            self.tr(
                "Starts point cloud processing and packages the portable viewer in the output folder.\n"
                "Cause and Effect: The LAS/LAZ file is converted to a Potree octree, the standalone viewer is packaged, and the quick-launch shortcut is created.",
                "Inicia o processamento da nuvem de pontos e montagem do visualizador portátil na pasta de destino.\n"
                "Causa e Efeito: O arquivo LAS/LAZ será convertido para estrutura octree Potree, o ambiente 3D portátil será empacotado "
                "e o arquivo executável de inicialização rápida será criado com todos os metadados configurados."
            )
        )
        self.btn_run.clicked.connect(self.run_process)
        actions_layout.addWidget(self.btn_run, 3)

        self.btn_reset = QPushButton(self.tr("Restore Defaults", "Restaurar Padrões"))
        self.btn_reset.setToolTip(
            self.tr(
                "Restores all tool settings and metadata to recommended factory defaults.\n"
                "Cause and Effect: Resets point size, GPU budget, GeoOne project defaults, and advanced parameters.",
                "Restaura todas as configurações da ferramenta para os valores de fábrica.\n"
                "Causa e Efeito: Limpa os campos preenchidos e redefine tamanho de ponto, orçamento de GPU e parâmetros avançados "
                "para o estado padrão original recomendado."
            )
        )
        self.btn_reset.clicked.connect(self.reset_defaults)
        actions_layout.addWidget(self.btn_reset, 2)

        try:
            actions_widget.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)
        except AttributeError:
            actions_widget.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        main_layout.addWidget(actions_widget, stretch=0)

        # -------------------------------------------------------------
        # 4. LOG DE PROCESSAMENTO
        # -------------------------------------------------------------
        lbl_log = QLabel(self.tr("Processing Log:", "Log de Processamento:"))
        lbl_log.setToolTip(self.tr("Tracks conversion and directory packaging steps.", "Acompanhamento das etapas técnicas de conversão e estruturação dos arquivos."))
        try:
            lbl_log.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)
        except AttributeError:
            lbl_log.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        main_layout.addWidget(lbl_log, stretch=0)

        self.txt_log = QTextEdit()
        self.txt_log.setReadOnly(True)
        try:
            self.txt_log.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        except AttributeError:
            self.txt_log.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.txt_log.setMinimumHeight(120)
        main_layout.addWidget(self.txt_log, stretch=1)

        container.setLayout(main_layout)

        # Adiciona área de rolagem vertical responsiva (Anti-Gap e Anti-Vácuo)
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        try:
            scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        except AttributeError:
            scroll_area.setFrameShape(QFrame.NoFrame)

        try:
            scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        except AttributeError:
            scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        scroll_area.setWidget(container)
        self.setWidget(scroll_area)

    def log(self, message: str):
        self.txt_log.append(message)
        QApplication.processEvents()

    def _on_budget_preset_changed(self):
        val = self.cmb_budget_preset.currentData()
        self.spin_budget.setVisible(val == -1)

    def get_point_budget(self) -> int:
        val = self.cmb_budget_preset.currentData()
        if val == -1:
            return self.spin_budget.value()
        return val

    def _on_custom_conv_toggled(self, checked: bool):
        self.fw_custom_conv.setVisible(checked)
        if not checked:
            self.fw_custom_conv.setFilePath("")
        self.refresh_dependency_status(auto_download_if_missing=False)

    def refresh_dependency_status(self, auto_download_if_missing: bool = False):
        """Atualiza a indicação visual de prontidão dos binários."""
        custom_conv = self.fw_custom_conv.filePath()
        status = check_dependencies(custom_conv=custom_conv)
        if status["ready"]:
            self.lbl_dep_status.setText(self.tr("Ready (Converter and Viewer OK)", "Pronto (Conversor e Visualizador OK)"))
            self.btn_download_deps.setText(self.tr("Re-check / Update Components", "Re-verificar / Atualizar Componentes"))
        else:
            if self.download_worker and self.download_worker.isRunning():
                self.lbl_dep_status.setText(self.tr("Downloading and extracting 3D components...", "Baixando e extraindo componentes 3D..."))
            else:
                self.lbl_dep_status.setText(self.tr("Components missing", "Componentes ausentes"))
            self.btn_download_deps.setText(self.tr("Download / Update 3D Components", "Baixar / Atualizar Componentes 3D"))
            if auto_download_if_missing and (not self.download_worker or not self.download_worker.isRunning()):
                self.start_dependency_download(silent=True)

    def start_dependency_download(self, silent: bool = False):
        """Inicia o download dos componentes em segundo plano."""
        if self.download_worker and self.download_worker.isRunning():
            return

        self.is_silent_download = silent
        self.btn_download_deps.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.log(self.tr("Downloading and extracting 3D components...", "Baixando e extraindo componentes 3D..."))

        self.download_worker = PotreeDependencyDownloader(self)
        self.download_worker.progress_signal.connect(self._on_download_progress)
        self.download_worker.finished_signal.connect(self._on_download_finished)
        self.download_worker.start()

    def _on_download_progress(self, pct: int, msg: str):
        self.progress_bar.setValue(pct)
        if pct % 10 == 0 or pct in (2, 26, 30, 86, 100):
            self.log(msg)

    def _on_download_finished(self, success: bool, message: str):
        self.btn_download_deps.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.refresh_dependency_status(auto_download_if_missing=False)
        self.log(message)
        if success:
            if not self.is_silent_download:
                QMessageBox.information(self, self.tr("3D Components", "Componentes 3D"), self.tr("Process finished successfully!", "Componentes configurados e testados com sucesso!"))
        else:
            if not self.is_silent_download:
                QMessageBox.warning(self, self.tr("Configuration Failure", "Falha na Configuração"), message)

    def _load_settings(self):
        """Carrega e memoriza todos os parâmetros salvos no QgsSettings."""
        s = self.settings
        self.fw_las.setFilePath(s.value(SETTINGS_PREFIX + "las_file", DEFAULT_SETTINGS["las_file"], type=str))
        self.fw_out.setFilePath(s.value(SETTINGS_PREFIX + "out_dir", DEFAULT_SETTINGS["out_dir"], type=str))
        
        # Valores GeoOne na primeira abertura (garante exibição se for a primeira vez)
        if not s.contains(SETTINGS_PREFIX + "geoone_initialized"):
            self.txt_project.setText(DEFAULT_SETTINGS["project_name"])
            self.txt_client.setText(DEFAULT_SETTINGS["client_name"])
            self.txt_company.setText(DEFAULT_SETTINGS["company_name"])
            self.txt_contact.setText(DEFAULT_SETTINGS["contact"])
            self.txt_address.setText(DEFAULT_SETTINGS["address"])
            s.setValue(SETTINGS_PREFIX + "geoone_initialized", True)
        else:
            self.txt_project.setText(s.value(SETTINGS_PREFIX + "project_name", DEFAULT_SETTINGS["project_name"], type=str))
            self.txt_client.setText(s.value(SETTINGS_PREFIX + "client_name", DEFAULT_SETTINGS["client_name"], type=str))
            self.txt_company.setText(s.value(SETTINGS_PREFIX + "company_name", DEFAULT_SETTINGS["company_name"], type=str))
            self.txt_contact.setText(s.value(SETTINGS_PREFIX + "contact", DEFAULT_SETTINGS["contact"], type=str))
            self.txt_address.setText(s.value(SETTINGS_PREFIX + "address", DEFAULT_SETTINGS["address"], type=str))


        point_size = float(s.value(SETTINGS_PREFIX + "point_size", DEFAULT_SETTINGS["point_size"]))
        self.spin_point_size.setValue(point_size)

        point_shape = s.value(SETTINGS_PREFIX + "point_shape", DEFAULT_SETTINGS["point_shape"], type=str)
        idx = self.cmb_point_shape.findData(point_shape)
        if idx >= 0:
            self.cmb_point_shape.setCurrentIndex(idx)

        budget = int(s.value(SETTINGS_PREFIX + "point_budget", DEFAULT_SETTINGS["point_budget"]))
        idx = self.cmb_budget_preset.findData(budget)
        if idx >= 0:
            self.cmb_budget_preset.setCurrentIndex(idx)
            self.spin_budget.setVisible(False)
            self.spin_budget.setValue(budget)
        else:
            custom_idx = self.cmb_budget_preset.findData(-1)
            self.cmb_budget_preset.setCurrentIndex(custom_idx)
            self.spin_budget.setVisible(True)
            self.spin_budget.setValue(budget)

        edl = s.value(SETTINGS_PREFIX + "edl_enabled", DEFAULT_SETTINGS["edl_enabled"], type=bool)
        self.chk_edl.setChecked(edl)

        custom_exe = s.value(SETTINGS_PREFIX + "custom_converter_exe", "", type=str)
        use_custom = s.value(SETTINGS_PREFIX + "use_custom_converter", False, type=bool) and bool(custom_exe)
        self.chk_custom_conv.setChecked(use_custom)
        self.fw_custom_conv.setVisible(use_custom)
        self.fw_custom_conv.setFilePath(custom_exe if use_custom else "")

    def _save_settings(self):
        """Persiste todos os parâmetros no QgsSettings (Honrando a UI)."""
        s = self.settings
        s.setValue(SETTINGS_PREFIX + "las_file", self.fw_las.filePath())
        s.setValue(SETTINGS_PREFIX + "out_dir", self.fw_out.filePath())
        s.setValue(SETTINGS_PREFIX + "project_name", self.txt_project.text())
        s.setValue(SETTINGS_PREFIX + "client_name", self.txt_client.text())
        s.setValue(SETTINGS_PREFIX + "company_name", self.txt_company.text())
        s.setValue(SETTINGS_PREFIX + "contact", self.txt_contact.text())
        s.setValue(SETTINGS_PREFIX + "address", self.txt_address.text())
        s.setValue(SETTINGS_PREFIX + "point_size", self.spin_point_size.value())
        s.setValue(SETTINGS_PREFIX + "point_shape", self.cmb_point_shape.currentData())
        s.setValue(SETTINGS_PREFIX + "point_budget", self.get_point_budget())
        s.setValue(SETTINGS_PREFIX + "edl_enabled", self.chk_edl.isChecked())
        s.setValue(SETTINGS_PREFIX + "use_custom_converter", self.chk_custom_conv.isChecked())
        s.setValue(SETTINGS_PREFIX + "custom_converter_exe", self.fw_custom_conv.filePath() if self.chk_custom_conv.isChecked() else "")

    def reset_defaults(self):
        """Restaura todos os valores para o padrão de fábrica (Valores GeoOne)."""
        self.spin_point_size.setValue(DEFAULT_SETTINGS["point_size"])
        idx = self.cmb_point_shape.findData(DEFAULT_SETTINGS["point_shape"])
        if idx >= 0:
            self.cmb_point_shape.setCurrentIndex(idx)
        
        b_idx = self.cmb_budget_preset.findData(DEFAULT_SETTINGS["point_budget"])
        if b_idx >= 0:
            self.cmb_budget_preset.setCurrentIndex(b_idx)
        self.spin_budget.setValue(DEFAULT_SETTINGS["point_budget"])
        self.spin_budget.setVisible(False)

        self.chk_edl.setChecked(DEFAULT_SETTINGS["edl_enabled"])
        
        # Conteúdo padrão GeoOne
        self.txt_project.setText(DEFAULT_SETTINGS["project_name"])
        self.txt_client.setText(DEFAULT_SETTINGS["client_name"])
        self.txt_company.setText(DEFAULT_SETTINGS["company_name"])
        self.txt_contact.setText(DEFAULT_SETTINGS["contact"])
        self.txt_address.setText(DEFAULT_SETTINGS["address"])
        
        self.chk_custom_conv.setChecked(False)
        self.fw_custom_conv.setVisible(False)
        self.fw_custom_conv.setFilePath("")
        self._save_settings()
        self.log(self.tr("Settings restored to factory defaults.", "Parâmetros redefinidos para os valores padrão de fábrica."))

    def run_process(self):
        """Executa a verificação e lança o worker de geração do pacote 3D."""
        las_file = self.fw_las.filePath()
        out_dir = self.fw_out.filePath()
        project_name = self.txt_project.text().strip()
        client_name = self.txt_client.text().strip()
        company_name = self.txt_company.text().strip()
        contact = self.txt_contact.text().strip()
        address = self.txt_address.text().strip()
        point_size = self.spin_point_size.value()
        point_shape = self.cmb_point_shape.currentData()
        point_budget = self.get_point_budget()
        edl_enabled = self.chk_edl.isChecked()
        custom_conv = self.fw_custom_conv.filePath() if self.chk_custom_conv.isChecked() else ""

        # Validação de campos obrigatórios
        if not las_file or not os.path.isfile(las_file):
            QMessageBox.warning(self, self.tr("Warning", "Atenção"), self.tr("Select an input point cloud file (.las/.laz).", "Selecione um arquivo de nuvem de pontos (.las ou .laz) válido."))
            return

        if not out_dir or not os.path.isdir(out_dir):
            QMessageBox.warning(self, self.tr("Warning", "Atenção"), self.tr("Select a valid output destination folder.", "Selecione uma pasta de destino válida para a entrega."))
            return

        if not project_name:
            QMessageBox.warning(self, self.tr("Warning", "Atenção"), self.tr("Enter a project name.", "Informe um nome para o projeto."))
            return

        # Verifica componentes
        dep_status = check_dependencies(custom_conv=custom_conv)
        if not dep_status["ready"]:
            resp = QMessageBox.question(
                self,
                self.tr("Dependencies Missing", "Componentes Ausentes"),
                self.tr("Do you want to download and install them now automatically?", "Os componentes do visualizador 3D Potree ainda não foram baixados.\nDeseja que o plugin faça o download automático agora?"),
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if resp == QMessageBox.StandardButton.Yes:
                self.start_dependency_download()
            return

        # Salva o estado atual
        self._save_settings()

        self.btn_run.setEnabled(False)
        self.btn_reset.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.txt_log.clear()
        self.log(self.tr("=== STARTING IMMERSIVE 3D VIEWER PACKAGING ===", "=== INICIANDO MONTAGEM DO VISUALIZADOR 3D IMERSIVO ==="))

        self.worker = ImmersiveCloudWorker(
            las_file=las_file,
            out_dir=out_dir,
            project_name=project_name,
            client_name=client_name,
            company_name=company_name,
            contact=contact,
            address=address,
            point_size=point_size,
            point_shape=point_shape,
            point_budget=point_budget,
            edl_enabled=edl_enabled,
            custom_converter_exe=custom_conv,
            parent=self
        )
        self.worker.log_signal.connect(self.log)
        self.worker.progress_signal.connect(self.progress_bar.setValue)
        self.worker.finished_signal.connect(self.process_finished)
        self.worker.start()

    def _open_output_directory(self, folder_path: str):
        """Abre a pasta de saída no explorador de arquivos do sistema operacional."""
        if not folder_path or not os.path.exists(folder_path):
            return

        norm_path = os.path.normpath(folder_path)
        try:
            opened = QDesktopServices.openUrl(QUrl.fromLocalFile(norm_path))
            if not opened:
                if platform.system() == "Windows" and hasattr(os, "startfile"):
                    os.startfile(norm_path)
                elif platform.system() == "Darwin":
                    subprocess.Popen(["open", norm_path])
                else:
                    subprocess.Popen(["xdg-open", norm_path])
        except Exception:
            try:
                if platform.system() == "Windows" and hasattr(os, "startfile"):
                    os.startfile(norm_path)
            except Exception as err:
                self.log(f"{self.tr('Notice: Could not open output folder automatically:', 'Aviso: Não foi possível abrir a pasta automaticamente:')} {err}")

    def process_finished(self, success: bool, message: str):
        self.btn_run.setEnabled(True)
        self.btn_reset.setEnabled(True)
        self.progress_bar.setVisible(False)

        if success:
            self.log(f"\n>>> {self.tr('Process finished successfully!', 'PACOTE 3D FINALIZADO COM SUCESSO')} <<<")
            self.log(message)

            # Abre a pasta de saída do projeto automaticamente no explorador de arquivos
            project_dir = getattr(self.worker, "final_project_dir", None)
            if not project_dir or not os.path.exists(project_dir):
                safe_name = re.sub(r'[\\/*?:"<>| ]', '_', self.txt_project.text().strip()) or "Projeto_3D"
                project_dir = os.path.join(self.fw_out.filePath(), safe_name)

            if not os.path.exists(project_dir):
                project_dir = self.fw_out.filePath()

            self._open_output_directory(project_dir)

            QMessageBox.information(self, self.tr("Success", "Sucesso"), message)
        else:
            self.log(f"\n>>> {self.tr('Processing failed: {}', 'FALHA NO PROCESSAMENTO').format(message)} <<<")
            self.log(message)
            QMessageBox.critical(self, self.tr("Error", "Erro"), message)

