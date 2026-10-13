# -*- coding: utf-8 -*-
"""
Immersive Cloud - HTML Viewer Template & Orientation Guide Generator
Part of LFTools for QGIS
Supports Portuguese, Spanish, and English based on active QGIS locale.
"""

def generate_html_content(
    project_name: str = "",
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
    locale: str = "pt"
) -> str:
    """
    Gera o conteúdo completo do index.html para o visualizador Potree 3D.
    Constrói dinamicamente o cartão de metadados apenas com os campos fornecidos.
    """
    loc = locale[:2].lower()
    lbl_client = "Cliente:" if loc in ["pt", "es"] else "Client:"

    project_title = project_name.strip() if project_name.strip() else ("Modelo 3D" if loc == "pt" else ("Modelo 3D" if loc == "es" else "3D Model"))
    client_clean = client_name.strip()
    company_clean = company_name.strip()
    contact_clean = contact.strip()
    address_clean = address.strip()

    # Construção modular do bloco de metadados HUD
    hud_rows = []
    hud_rows.append(f'<h2 style="margin: 0 0 6px 0; font-size: 15px; color: #4CAF50; font-weight: 600;">{project_title}</h2>')

    if client_clean:
        hud_rows.append(f'<p style="margin: 0 0 4px 0; font-size: 12px; color: #e0e0e0;"><strong>{lbl_client}</strong> {client_clean}</p>')

    has_company_info = any([company_clean, contact_clean, address_clean])
    if has_company_info:
        hud_rows.append('<hr style="border: 0; border-top: 1px solid rgba(255,255,255,0.15); margin: 6px 0;">')
        if company_clean:
            hud_rows.append(f'<p style="margin: 0; font-size: 11px; color: #bbbbbb; font-weight: 500;">{company_clean}</p>')
        if contact_clean:
            hud_rows.append(f'<p style="margin: 2px 0 0 0; font-size: 10px; color: #999999;">{contact_clean}</p>')
        if address_clean:
            hud_rows.append(f'<p style="margin: 2px 0 0 0; font-size: 10px; color: #888888;">{address_clean}</p>')

    hud_content = "\n        ".join(hud_rows)

    shape_js = "Potree.PointShape.CIRCLE" if point_shape.upper() == "CIRCLE" else "Potree.PointShape.SQUARE"
    size_type_js = "Potree.PointSizeType.ADAPTIVE" if point_size_type.upper() == "ADAPTIVE" else "Potree.PointSizeType.FIXED"
    edl_js = "true" if edl_enabled else "false"

    html = f"""<!DOCTYPE html>
<html lang="{loc}">
<head>
	<meta charset="utf-8">
	<meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
	<title>{project_title} - 3D Viewer</title>
	<link rel="stylesheet" type="text/css" href="./libs/potree/potree.css">
	<link rel="stylesheet" type="text/css" href="./libs/jquery-ui/jquery-ui.min.css">
	<link rel="stylesheet" type="text/css" href="./libs/openlayers3/ol.css">
	<link rel="stylesheet" type="text/css" href="./libs/spectrum/spectrum.css">
	<link rel="stylesheet" type="text/css" href="./libs/jstree/themes/mixed/style.css">
	<link rel="stylesheet" type="text/css" href="./src/desktop.css">
</head>
<body>
    <script>if (typeof module === 'object') {{ window.module = module; module = undefined; }}</script>

	<script src="./libs/jquery/jquery-3.1.1.min.js"></script>
	<script src="./libs/spectrum/spectrum.js"></script>
	<script src="./libs/jquery-ui/jquery-ui.min.js"></script>
	<script src="./libs/other/BinaryHeap.js"></script>
	<script src="./libs/tween/tween.min.js"></script>
	<script src="./libs/d3/d3.js"></script>
	<script src="./libs/proj4/proj4.js"></script>
	<script src="./libs/openlayers3/ol.js"></script>
	<script src="./libs/i18next/i18next.js"></script>
	<script src="./libs/jstree/jstree.js"></script>
	<script src="./libs/potree/potree.js"></script>
	<script src="./libs/plasio/js/laslaz.js"></script>
	
	<div class="potree_container" style="position: absolute; width: 100%; height: 100%; left: 0px; top: 0px;">
		<div id="potree_render_area"></div>
		<div id="potree_sidebar_container"></div>
	</div>

    <!-- PAINEL FLUTUANTE DE METADADOS DO PROJETO -->
    <div style="position: absolute; bottom: 18px; left: 340px; z-index: 1000; background: rgba(25, 25, 28, 0.88); backdrop-filter: blur(6px); color: #ffffff; padding: 12px 16px; border-radius: 6px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; pointer-events: none; border: 1px solid rgba(255, 255, 255, 0.12); box-shadow: 0 4px 16px rgba(0, 0, 0, 0.4); max-width: 380px;">
        {hud_content}
    </div>

	<script type="module">
		let elRenderArea = document.getElementById("potree_render_area");
		window.viewer = new Potree.Viewer(elRenderArea, {{ noDragAndDrop: true }});
		
		viewer.setEDLEnabled({edl_js});
		viewer.setFOV({fov});
		viewer.setPointBudget({point_budget});
		viewer.setMinNodeSize(0);
		viewer.loadSettingsFromURL();
		
		viewer.setDescription("");
		
		viewer.loadGUI(() => {{
			viewer.setLanguage('{loc}');
			$("#menu_appearance").next().show();
			$("#menu_tools").next().show();
			viewer.toggleSidebar();
		}});
		
		// Carregamento da nuvem convertida
		Potree.loadPointCloud("./pointclouds/projeto_atual/metadata.json", "Nuvem 3D", e => {{
			let scene = viewer.scene;
			let pointcloud = e.pointcloud;
			let material = pointcloud.material;
			
			material.size = {point_size};
			material.pointSizeType = {size_type_js};
			material.shape = {shape_js};
			
			scene.addPointCloud(pointcloud);
			viewer.fitToScreen();
		}});
	</script>
</body>
</html>"""
    return html


GUIDE_TEXTS = {
    "pt": {
        "html_lang": "pt-BR",
        "doc_title": "Guia de Visualização 3D - {}",
        "badge": "Nuvem de Pontos 3D",
        "subtitle": "Guia Rápido de Acesso e Navegação no Modelo Tridimensional",
        "project_info": "📋 Informações do Projeto",
        "lbl_project": "Projeto:",
        "lbl_client": "Cliente:",
        "lbl_author": "Responsável Técnico:",
        "lbl_contact": "Contato:",
        "lbl_address": "Localidade:",
        "lbl_date": "Data de Entrega:",
        "how_to_start": "🚀 Como Iniciar a Visualização",
        "step1_title": "Abra a Pasta",
        "step1_desc": "Acesse a subpasta <span class=\"kbd\">Visualizador_3D</span> dentro desta mesma pasta.",
        "step2_title": "Execute o Atalho",
        "step2_desc": "Dê um duplo clique no arquivo <span class=\"kbd\">1_CLIQUE_AQUI_PARA_ABRIR.bat</span>.",
        "step3_title": "Explore em 3D",
        "step3_desc": "O visualizador abrirá instantaneamente sem necessidade de internet nem instalações.",
        "mouse_nav": "🖱️ Comandos de Navegação do Mouse",
        "left_btn": "Botão Esquerdo",
        "left_btn_desc": "Gira e orbita a câmera em 360° ao redor do terreno.",
        "right_btn": "Botão Direito",
        "right_btn_desc": "Arrasta a visão (Panorâmica / Deslocamento lateral).",
        "scroll": "Roda do Mouse (Scroll)",
        "scroll_desc": "Aproxima e afasta o zoom suavemente.",
        "dbl_click": "Duplo Clique em um Ponto",
        "dbl_click_desc": "Centraliza o foco e o eixo de rotação naquele ponto.",
        "interactive_tools": "🛠️ Ferramentas Interativas no Menu Lateral",
        "tool1_title": "📏 Medição de Distâncias e Alturas",
        "tool1_desc": "Clique nos pontos para medir vãos horizontais, desníveis verticais (Z) e distâncias tridimensionais diretas.",
        "tool2_title": "📐 Cálculo de Áreas e Perímetros",
        "tool2_desc": "Delimite polígonos sobre a superfície para calcular áreas planas ou projetadas no terreno.",
        "tool3_title": "📈 Perfil Topográfico (Corte de Seção)",
        "tool3_desc": "Trace uma linha de corte sobre o modelo para obter o gráfico de perfil de elevação instantâneo.",
        "tool4_title": "🎨 Modos de Cores e Relevo",
        "tool4_desc": "Alterne entre cores naturais (RGB), rampa hipsométrica por altitude, intensidade ou classificação.",
        "footer": "Visualizador autônomo baseado em tecnologia Potree e Electron. 100% portátil para Windows 64-bit."
    },
    "es": {
        "html_lang": "es-ES",
        "doc_title": "Guía de Visualización 3D - {}",
        "badge": "Nube de Puntos 3D",
        "subtitle": "Guía Rápida de Acceso y Navegación en el Modelo Tridimensional",
        "project_info": "📋 Información del Proyecto",
        "lbl_project": "Proyecto:",
        "lbl_client": "Cliente:",
        "lbl_author": "Responsable Técnico:",
        "lbl_contact": "Contacto:",
        "lbl_address": "Ubicación:",
        "lbl_date": "Fecha de Entrega:",
        "how_to_start": "🚀 Cómo Iniciar la Visualización",
        "step1_title": "Abra la Carpeta",
        "step1_desc": "Acceda a la subcarpeta <span class=\"kbd\">Visualizador_3D</span> dentro de esta misma carpeta.",
        "step2_title": "Ejecute el Acceso Directo",
        "step2_desc": "Haga doble clic en el archivo <span class=\"kbd\">1_CLIQUE_AQUI_PARA_ABRIR.bat</span>.",
        "step3_title": "Explore en 3D",
        "step3_desc": "El visualizador se abrirá instantáneamente sin necesidad de internet ni instalaciones.",
        "mouse_nav": "🖱️ Comandos de Navegación del Ratón",
        "left_btn": "Botón Izquierdo",
        "left_btn_desc": "Gira y orbita la cámara en 360° alrededor del terreno.",
        "right_btn": "Botón Derecho",
        "right_btn_desc": "Arrastra la vista (Panorámica / Desplazamiento lateral).",
        "scroll": "Rueda del Ratón (Scroll)",
        "scroll_desc": "Acerca y aleja el zoom suavemente.",
        "dbl_click": "Doble Clic en un Punto",
        "dbl_click_desc": "Centra el foco y el eje de rotación en ese punto.",
        "interactive_tools": "🛠️ Herramientas Interactivas en el Menú Lateral",
        "tool1_title": "📏 Medición de Distancias y Alturas",
        "tool1_desc": "Haga clic en los puntos para medir vanos horizontales, desniveles verticales (Z) y distancias tridimensionales directas.",
        "tool2_title": "📐 Cálculo de Áreas y Perímetros",
        "tool2_desc": "Delimite polígonos sobre la superficie para calcular áreas planas o proyectadas en el terreno.",
        "tool3_title": "📈 Perfil Topográfico (Corte de Sección)",
        "tool3_desc": "Trace una línea de corte sobre el modelo para obtener el gráfico de perfil de elevación instantáneo.",
        "tool4_title": "🎨 Modos de Color y Relieve",
        "tool4_desc": "Alterne entre colores naturales (RGB), rampa hipsométrica por altitud, intensidad o clasificación.",
        "footer": "Visualizador autónomo basado en tecnología Potree y Electron. 100% portátil para Windows 64-bit."
    },
    "en": {
        "html_lang": "en-US",
        "doc_title": "3D Visualization Guide - {}",
        "badge": "3D Point Cloud",
        "subtitle": "Quick Guide for Access and Navigation in the 3D Model",
        "project_info": "📋 Project Information",
        "lbl_project": "Project:",
        "lbl_client": "Client:",
        "lbl_author": "Technical Manager:",
        "lbl_contact": "Contact:",
        "lbl_address": "Location:",
        "lbl_date": "Delivery Date:",
        "how_to_start": "🚀 How to Start the Viewer",
        "step1_title": "Open Folder",
        "step1_desc": "Access the subfolder <span class=\"kbd\">Visualizador_3D</span> inside this same folder.",
        "step2_title": "Run Shortcut",
        "step2_desc": "Double-click the file <span class=\"kbd\">1_CLIQUE_AQUI_PARA_ABRIR.bat</span>.",
        "step3_title": "Explore in 3D",
        "step3_desc": "The viewer will open immediately without requiring internet connection or installations.",
        "mouse_nav": "🖱️ Mouse Navigation Commands",
        "left_btn": "Left Click",
        "left_btn_desc": "Rotate and orbit the camera 360° around the terrain.",
        "right_btn": "Right Click",
        "right_btn_desc": "Pan and drag the camera laterally.",
        "scroll": "Mouse Wheel (Scroll)",
        "scroll_desc": "Smooth zoom in and out.",
        "dbl_click": "Double-Click on a Point",
        "dbl_click_desc": "Centers the focus and rotation axis on that point.",
        "interactive_tools": "🛠️ Interactive Tools in the Sidebar",
        "tool1_title": "📏 Distance and Height Measurements",
        "tool1_desc": "Click points to measure horizontal distances, vertical elevation differences (Z), and direct 3D lengths.",
        "tool2_title": "📐 Area and Perimeter Calculations",
        "tool2_desc": "Delimit polygons over the surface to calculate flat or projected terrain areas.",
        "tool3_title": "📈 Elevation Profile (Section Cut)",
        "tool3_desc": "Draw a cut line across the model to generate an instantaneous elevation profile plot.",
        "tool4_title": "🎨 Color and Relief Modes",
        "tool4_desc": "Switch between natural colors (RGB), elevation hypsometric ramp, intensity, or classification.",
        "footer": "Standalone viewer based on Potree and Electron technology. 100% portable for Windows 64-bit."
    }
}


def generate_guide_html(
    project_name: str = "",
    client_name: str = "",
    company_name: str = "",
    contact: str = "",
    address: str = "",
    date_str: str = "",
    locale: str = "pt"
) -> str:
    """
    Gera o conteúdo de COMO_VISUALIZAR_O_MODELO_3D.html, um guia visual
    completo e interativo para o cliente final, localizado no idioma ativo.
    """
    loc = locale[:2].lower()
    t = GUIDE_TEXTS.get(loc, GUIDE_TEXTS["en"])

    project_title = project_name.strip() if project_name.strip() else ("Modelo 3D Interativo" if loc == "pt" else ("Modelo 3D Interactivo" if loc == "es" else "Interactive 3D Model"))
    client_clean = client_name.strip()
    company_clean = company_name.strip()
    contact_clean = contact.strip()
    address_clean = address.strip()

    meta_items = []
    meta_items.append(f'<div class="meta-item"><span class="meta-label">{t["lbl_project"]}</span> <span class="meta-value">{project_title}</span></div>')
    if client_clean:
        meta_items.append(f'<div class="meta-item"><span class="meta-label">{t["lbl_client"]}</span> <span class="meta-value">{client_clean}</span></div>')
    if company_clean:
        meta_items.append(f'<div class="meta-item"><span class="meta-label">{t["lbl_author"]}</span> <span class="meta-value">{company_clean}</span></div>')
    if contact_clean:
        meta_items.append(f'<div class="meta-item"><span class="meta-label">{t["lbl_contact"]}</span> <span class="meta-value">{contact_clean}</span></div>')
    if address_clean:
        meta_items.append(f'<div class="meta-item"><span class="meta-label">{t["lbl_address"]}</span> <span class="meta-value">{address_clean}</span></div>')
    if date_str:
        meta_items.append(f'<div class="meta-item"><span class="meta-label">{t["lbl_date"]}</span> <span class="meta-value">{date_str}</span></div>')

    meta_html = "\n        ".join(meta_items)
    doc_title = t["doc_title"].format(project_title)

    html = f"""<!DOCTYPE html>
<html lang="{t['html_lang']}">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{doc_title}</title>
  <style>
    :root {{
      --bg: #0f1115;
      --card-bg: #181b22;
      --card-border: rgba(255, 255, 255, 0.08);
      --accent: #00E676;
      --accent-subtle: rgba(0, 230, 118, 0.12);
      --accent-blue: #29B6F6;
      --text: #f0f2f5;
      --text-muted: #9aa0a6;
      --kbd-bg: #262a33;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
      background-color: var(--bg);
      color: var(--text);
      line-height: 1.6;
      padding: 30px 20px;
    }}
    .container {{
      max-width: 860px;
      margin: 0 auto;
    }}
    header {{
      text-align: center;
      margin-bottom: 30px;
      padding-bottom: 20px;
      border-bottom: 1px solid var(--card-border);
    }}
    .badge {{
      display: inline-block;
      padding: 4px 12px;
      background: var(--accent-subtle);
      color: var(--accent);
      border-radius: 20px;
      font-size: 12px;
      font-weight: 600;
      letter-spacing: 0.5px;
      margin-bottom: 10px;
      text-transform: uppercase;
    }}
    h1 {{
      font-size: 26px;
      font-weight: 700;
      color: #ffffff;
      margin-bottom: 8px;
    }}
    .subtitle {{
      color: var(--text-muted);
      font-size: 14px;
    }}
    .card {{
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      border-radius: 12px;
      padding: 24px;
      margin-bottom: 24px;
    }}
    .card-title {{
      font-size: 18px;
      font-weight: 600;
      margin-bottom: 16px;
      display: flex;
      align-items: center;
      gap: 8px;
      color: var(--accent);
    }}
    .meta-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
      gap: 12px;
    }}
    .meta-item {{
      background: rgba(255, 255, 255, 0.03);
      padding: 10px 14px;
      border-radius: 8px;
      border: 1px solid rgba(255, 255, 255, 0.04);
    }}
    .meta-label {{
      font-size: 12px;
      color: var(--text-muted);
      display: block;
      margin-bottom: 2px;
    }}
    .meta-value {{
      font-size: 14px;
      font-weight: 500;
      color: var(--text);
    }}
    .steps-container {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
      gap: 16px;
    }}
    .step-box {{
      background: rgba(255, 255, 255, 0.03);
      border: 1px solid rgba(255, 255, 255, 0.06);
      border-radius: 10px;
      padding: 20px;
      position: relative;
    }}
    .step-number {{
      position: absolute;
      top: 12px;
      right: 12px;
      width: 28px;
      height: 28px;
      background: var(--accent-subtle);
      color: var(--accent);
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: 700;
      font-size: 13px;
    }}
    .step-title {{
      font-size: 16px;
      font-weight: 600;
      margin-bottom: 8px;
      color: #ffffff;
    }}
    .step-desc {{
      font-size: 13px;
      color: var(--text-muted);
      line-height: 1.5;
    }}
    .kbd {{
      display: inline-block;
      padding: 2px 6px;
      background: var(--kbd-bg);
      border: 1px solid rgba(255, 255, 255, 0.15);
      border-radius: 4px;
      font-family: monospace;
      font-size: 11px;
      color: var(--accent);
    }}
    .controls-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
      gap: 14px;
    }}
    .control-item {{
      display: flex;
      align-items: flex-start;
      gap: 12px;
      background: rgba(255, 255, 255, 0.03);
      padding: 14px;
      border-radius: 8px;
      border: 1px solid rgba(255, 255, 255, 0.04);
    }}
    .control-icon {{
      font-size: 24px;
      line-height: 1;
    }}
    .control-text strong {{
      display: block;
      font-size: 14px;
      margin-bottom: 2px;
      color: #ffffff;
    }}
    .control-text span {{
      font-size: 12px;
      color: var(--text-muted);
      line-height: 1.4;
      display: block;
    }}
    .tools-list {{
      display: flex;
      flex-direction: column;
      gap: 10px;
    }}
    .tool-item {{
      background: rgba(255, 255, 255, 0.02);
      border-left: 3px solid var(--accent);
      padding: 12px 16px;
      border-radius: 0 8px 8px 0;
    }}
    .tool-header {{
      font-size: 14px;
      font-weight: 600;
      color: #ffffff;
      margin-bottom: 4px;
    }}
    .tool-desc {{
      font-size: 12px;
      color: var(--text-muted);
    }}
    .footer-note {{
      text-align: center;
      font-size: 12px;
      color: var(--text-muted);
      margin-top: 30px;
      padding-top: 15px;
      border-top: 1px solid var(--card-border);
    }}
  </style>
</head>
<body>
  <div class="container">
    <header>
      <div class="badge">{t['badge']}</div>
      <h1>{project_title}</h1>
      <p class="subtitle">{t['subtitle']}</p>
    </header>

    <section class="card">
      <div class="card-title">{t['project_info']}</div>
      <div class="meta-grid">
        {meta_html}
      </div>
    </section>

    <section class="card">
      <div class="card-title">{t['how_to_start']}</div>
      <div class="steps-container">
        <div class="step-box">
          <div class="step-number">1</div>
          <div class="step-title">{t['step1_title']}</div>
          <p class="step-desc">{t['step1_desc']}</p>
        </div>
        <div class="step-box">
          <div class="step-number">2</div>
          <div class="step-title">{t['step2_title']}</div>
          <p class="step-desc">{t['step2_desc']}</p>
        </div>
        <div class="step-box">
          <div class="step-number">3</div>
          <div class="step-title">{t['step3_title']}</div>
          <p class="step-desc">{t['step3_desc']}</p>
        </div>
      </div>
    </section>

    <section class="card">
      <div class="card-title">{t['mouse_nav']}</div>
      <div class="controls-grid">
        <div class="control-item">
          <div class="control-icon">🖱️</div>
          <div class="control-text">
            <strong>{t['left_btn']}</strong>
            <span>{t['left_btn_desc']}</span>
          </div>
        </div>
        <div class="control-item">
          <div class="control-icon">🖱️</div>
          <div class="control-text">
            <strong>{t['right_btn']}</strong>
            <span>{t['right_btn_desc']}</span>
          </div>
        </div>
        <div class="control-item">
          <div class="control-icon">⚙️</div>
          <div class="control-text">
            <strong>{t['scroll']}</strong>
            <span>{t['scroll_desc']}</span>
          </div>
        </div>
        <div class="control-item">
          <div class="control-icon">🎯</div>
          <div class="control-text">
            <strong>{t['dbl_click']}</strong>
            <span>{t['dbl_click_desc']}</span>
          </div>
        </div>
      </div>
    </section>

    <section class="card">
      <div class="card-title">{t['interactive_tools']}</div>
      <div class="tools-list">
        <div class="tool-item">
          <div class="tool-header">{t['tool1_title']}</div>
          <div class="tool-desc">{t['tool1_desc']}</div>
        </div>
        <div class="tool-item">
          <div class="tool-header">{t['tool2_title']}</div>
          <div class="tool-desc">{t['tool2_desc']}</div>
        </div>
        <div class="tool-item">
          <div class="tool-header">{t['tool3_title']}</div>
          <div class="tool-desc">{t['tool3_desc']}</div>
        </div>
        <div class="tool-item">
          <div class="tool-header">{t['tool4_title']}</div>
          <div class="tool-desc">{t['tool4_desc']}</div>
        </div>
      </div>
    </section>

    <div class="footer-note">
      {t['footer']}
    </div>
  </div>
</body>
</html>"""
    return html
