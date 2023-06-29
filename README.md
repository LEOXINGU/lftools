<!-- PROJECT LOGO -->
<p align="center">
    <img src="https://github.com/LEOXINGU/lftools/blob/main/images/lftools_logo.png" alt="Logo" width="90" height="75">
  <h3 align="center">LF Tools</h3>
  <p align="center">
    <b><i>Tools for cartographic production, surveying, digital image processing and spatial analysis</i><b>
    <br />
  </p>
</p>

## Tutorials
<div style="text-align: center;"><a
 style="font-weight: bold;"
 href="https://www.youtube.com/watch?v=uuy39iutMhM&list=PLswoyLl1BbPp4zd-M4CmP_B2Qr2ROY3LT&index=1">Click here to learn how to use the LFTools plugin on YouTube</a></div>

## Requirement for QGIS 3.22 in MacOS:
    
Install the following package as follows:
```
pip install Pillow
```

## Description of each tool


<!-- TABLE OF CONTENTS -->
<details open="open">
  <summary>Set of Tools</summary>
  <ol>
    <li>
      <a href="#cadastre">Cadastre</a>
      <ul>
        <li><a href="#adjoiner-lines">Adjoiner Lines</a></li>
      </ul>
      <ul>
        <li><a href="#connect-features">Connect features</a></li>
      </ul>
      <ul>
        <li><a href="#front-lot-lines">Front Lot Lines</a></li>
      </ul>
      <ul>
        <li><a href="#geographic-numbering">Geographic Numbering</a></li>
      </ul>
      <ul>
        <li><a href="#orient-polygons">Orient polygons</a></li>
      </ul>
      </li><li>
      <a href="#cartography">Cartography</a>
      <ul>
        <li><a href="#coordinates-to-utm-grid">Coordinates to UTM grid</a></li>
      </ul>
      <ul>
        <li><a href="#extent-to-utm-grids">Extent to UTM grids</a></li>
      </ul>
      <ul>
        <li><a href="#name-to-utm-grid">Name to UTM grid</a></li>
      </ul>
      </li><li>
      <a href="#documents">Documents</a>
      <ul>
        <li><a href="#area-and-perimeter-report">Area and perimeter report</a></li>
      </ul>
      <ul>
        <li><a href="#deed-description">Deed description</a></li>
      </ul>
      <ul>
        <li><a href="#geodetic-mark-report">Geodetic mark report</a></li>
      </ul>
      <ul>
        <li><a href="#points-from-deed-description">Points from Deed Description</a></li>
      </ul>
      <ul>
        <li><a href="#synthetic-deed-description">Synthetic deed description</a></li>
      </ul>
      </li><li>
      <a href="#drones">Drones</a>
      <ul>
        <li><a href="#copy-selected-files">Copy selected files</a></li>
      </ul>
      <ul>
        <li><a href="#generate-gcp-file-from-layer">Generate GCP file from layer</a></li>
      </ul>
      <ul>
        <li><a href="#georeferencing-adjustment">Georeferencing Adjustment</a></li>
      </ul>
      <ul>
        <li><a href="#join-folders">Join folders</a></li>
      </ul>
      <ul>
        <li><a href="#overviews-with-jpeg-compression">Overviews with JPEG compression</a></li>
      </ul>
      <ul>
        <li><a href="#photos-histogram-matching">Photos Histogram Matching</a></li>
      </ul>
      <ul>
        <li><a href="#photos-by-blocks">Photos by blocks</a></li>
      </ul>
      <ul>
        <li><a href="#point-cloud-adjustment">Point cloud adjustment</a></li>
      </ul>
      <ul>
        <li><a href="#remove-alpha-band">Remove alpha band</a></li>
      </ul>
      <ul>
        <li><a href="#save-as-jpeg">Save as JPEG</a></li>
      </ul>
      <ul>
        <li><a href="#vertical-adjustment">Vertical adjustment</a></li>
      </ul>
      </li><li>
      <a href="#easy">Easy</a>
      <ul>
        <li><a href="#get-attribute-by-location">Get attribute by location</a></li>
      </ul>
      <ul>
        <li><a href="#measure-layers">Measure layers</a></li>
      </ul>
      <ul>
        <li><a href="#table-to-point-layer">Table to point layer</a></li>
      </ul>
      </li><li>
      <a href="#gnss">GNSS</a>
      <ul>
        <li><a href="#nmea-to-layer">NMEA to layer</a></li>
      </ul>
      <ul>
        <li><a href="#pos-file-(.pos)-to-layer">POS file (.pos) to layer</a></li>
      </ul>
      <ul>
        <li><a href="#rtk-points-correction">RTK Points Correction</a></li>
      </ul>
      <ul>
        <li><a href="#stop-and-go">Stop and Go</a></li>
      </ul>
      </li><li>
      <a href="#postgis">PostGIS</a>
      <ul>
        <li><a href="#backup-database">Backup database</a></li>
      </ul>
      <ul>
        <li><a href="#change-sql-encoding">Change SQL encoding</a></li>
      </ul>
      <ul>
        <li><a href="#clone-database">Clone database</a></li>
      </ul>
      <ul>
        <li><a href="#delete-database">Delete database</a></li>
      </ul>
      <ul>
        <li><a href="#import-raster">Import raster</a></li>
      </ul>
      <ul>
        <li><a href="#rename-database">Rename database</a></li>
      </ul>
      <ul>
        <li><a href="#restore-database">Restore database</a></li>
      </ul>
      </li><li>
      <a href="#raster">Raster</a>
      <ul>
        <li><a href="#band-arithmetic">Band Arithmetic</a></li>
      </ul>
      <ul>
        <li><a href="#binary-thresholding">Binary Thresholding</a></li>
      </ul>
      <ul>
        <li><a href="#create-holes-in-raster">Create holes in raster</a></li>
      </ul>
      <ul>
        <li><a href="#define-null-cells">Define null cells</a></li>
      </ul>
      <ul>
        <li><a href="#estimate-point-value-from-raster">Estimate point value from Raster</a></li>
      </ul>
      <ul>
        <li><a href="#extract-raster-band">Extract raster band</a></li>
      </ul>
      <ul>
        <li><a href="#fill-with-patches">Fill with patches</a></li>
      </ul>
      <ul>
        <li><a href="#histogram-matching">Histogram matching</a></li>
      </ul>
      <ul>
        <li><a href="#jpeg-compression">JPEG compression</a></li>
      </ul>
      <ul>
        <li><a href="#load-raster-by-location">Load raster by location</a></li>
      </ul>
      <ul>
        <li><a href="#mosaic-raster">Mosaic raster</a></li>
      </ul>
      <ul>
        <li><a href="#rgb-composite">RGB composite</a></li>
      </ul>
      <ul>
        <li><a href="#rgb-to-hsv">RGB to HSV</a></li>
      </ul>
      <ul>
        <li><a href="#raster-data-inventory">Raster data inventory</a></li>
      </ul>
      <ul>
        <li><a href="#rescale-to-8-bit">Rescale to 8 bit</a></li>
      </ul>
      <ul>
        <li><a href="#split-raster">Split raster</a></li>
      </ul>
      <ul>
        <li><a href="#supervised-classification">Supervised classification</a></li>
      </ul>
      <ul>
        <li><a href="#zonal-statistics">Zonal Statistics</a></li>
      </ul>
      </li><li>
      <a href="#reambulation">Reambulation</a>
      <ul>
        <li><a href="#kml-with-photos">KML with photos</a></li>
      </ul>
      <ul>
        <li><a href="#photos-with-geotag">Photos with geotag</a></li>
      </ul>
      <ul>
        <li><a href="#resize-photos">Resize photos</a></li>
      </ul>
      </li><li>
      <a href="#relief">Relief</a>
      <ul>
        <li><a href="#dem-difference">DEM difference</a></li>
      </ul>
      <ul>
        <li><a href="#dem-filter">DEM filter</a></li>
      </ul>
      <ul>
        <li><a href="#dem-to-text">DEM to Text</a></li>
      </ul>
      <ul>
        <li><a href="#generate-spot-elevations">Generate Spot Elevations</a></li>
      </ul>
      </li><li>
      <a href="#spatial-statistics">Spatial Statistics</a>
      <ul>
        <li><a href="#central-tendency">Central Tendency</a></li>
      </ul>
      <ul>
        <li><a href="#confidence-ellipses">Confidence ellipses</a></li>
      </ul>
      <ul>
        <li><a href="#gaussian-random-points">Gaussian random points</a></li>
      </ul>
      <ul>
        <li><a href="#nearest-points">Nearest points</a></li>
      </ul>
      <ul>
        <li><a href="#standard-distance">Standard Distance</a></li>
      </ul>
      </li><li>
      <a href="#survey">Survey</a>
      <ul>
        <li><a href="#azimuth-and-distance">Azimuth and distance</a></li>
      </ul>
      <ul>
        <li><a href="#closed-polygonal">Closed polygonal</a></li>
      </ul>
      <ul>
        <li><a href="#coordinate-transformation-2d">Coordinate transformation 2D</a></li>
      </ul>
      <ul>
        <li><a href="#estimate-3d-coordinates">Estimate 3D coordinates</a></li>
      </ul>
      <ul>
        <li><a href="#local-geodetic-system-transform">Local Geodetic System transform</a></li>
      </ul>
      <ul>
        <li><a href="#traverse-adjustment">Traverse adjustment</a></li>
      </ul>
      </li><li>
      <a href="#vector">Vector</a>
      <ul>
        <li><a href="#calculate-polygon-angles">Calculate polygon angles</a></li>
      </ul>
      <ul>
        <li><a href="#extend-lines">Extend lines</a></li>
      </ul>
      <ul>
        <li><a href="#line-sequence">Line sequence</a></li>
      </ul>
      <ul>
        <li><a href="#lines-to-polygon">Lines to polygon</a></li>
      </ul>
      <ul>
        <li><a href="#merge-lines-in-direction">Merge lines in direction</a></li>
      </ul>
      <ul>
        <li><a href="#overlapping-polygons">Overlapping polygons</a></li>
      </ul>
      <ul>
        <li><a href="#points-to-polygon">Points to polygon</a></li>
      </ul>
      <ul>
        <li><a href="#reverse-vertex-order">Reverse vertex order</a></li>
      </ul>
      <ul>
        <li><a href="#sequence-points">Sequence points</a></li>
      </ul>
      </li>
  </ol>
</details>

<!-- TABLE OF CONTENTS -->
<details open="open">
  <summary>Conjunto de Ferramentas (Portuguese-BR)</summary>
  <ol>
    <li>
      <a href="#agrimensura">Agrimensura</a>
      <ul>
        <li><a href="#azimute-e-distância">Azimute e distância</a></li>
      </ul>
      <ul>
        <li><a href="#estimar-coordenadas-3d">Estimar coordenadas 3D</a></li>
      </ul>
      <ul>
        <li><a href="#poligonal-enquadrada">Poligonal enquadrada</a></li>
      </ul>
      <ul>
        <li><a href="#poligonal-fechada">Poligonal fechada</a></li>
      </ul>
      <ul>
        <li><a href="#transformação-de-coordenadas-2d">Transformação de coordenadas 2D</a></li>
      </ul>
      <ul>
        <li><a href="#transformação-para-sgl">Transformação para SGL</a></li>
      </ul>
      </li><li>
      <a href="#cadastro">Cadastro</a>
      <ul>
        <li><a href="#conectar-feições">Conectar feições</a></li>
      </ul>
      <ul>
        <li><a href="#linhas-de-confrontantes">Linhas de Confrontantes</a></li>
      </ul>
      <ul>
        <li><a href="#linhas-de-testada">Linhas de Testada</a></li>
      </ul>
      <ul>
        <li><a href="#numerar-geograficamente">Numerar geograficamente</a></li>
      </ul>
      <ul>
        <li><a href="#orientar-polígonos">Orientar polígonos</a></li>
      </ul>
      </li><li>
      <a href="#cartografia">Cartografia</a>
      <ul>
        <li><a href="#coordenadas-para-moldura-utm">Coordenadas para moldura UTM</a></li>
      </ul>
      <ul>
        <li><a href="#extensão-para-molduras-utm">Extensão para molduras UTM</a></li>
      </ul>
      <ul>
        <li><a href="#nome-para-moldura-utm">Nome para moldura UTM</a></li>
      </ul>
      </li><li>
      <a href="#documentos">Documentos</a>
      <ul>
        <li><a href="#memorial-descritivo">Memorial descritivo</a></li>
      </ul>
      <ul>
        <li><a href="#memorial-sintético">Memorial sintético</a></li>
      </ul>
      <ul>
        <li><a href="#monografia-de-marco-geodésico">Monografia de marco geodésico</a></li>
      </ul>
      <ul>
        <li><a href="#planilha-de-área-e-perímetro">Planilha de área e perímetro</a></li>
      </ul>
      <ul>
        <li><a href="#reconstituição-de-memorial">Reconstituição de Memorial</a></li>
      </ul>
      </li><li>
      <a href="#drones">Drones</a>
      <ul>
        <li><a href="#ajuste-vertical">Ajuste Vertical</a></li>
      </ul>
      <ul>
        <li><a href="#ajuste-de-nuvem-de-pontos">Ajuste de Nuvem de Pontos</a></li>
      </ul>
      <ul>
        <li><a href="#ajuste-do-georreferenciamento">Ajuste do Georreferenciamento</a></li>
      </ul>
      <ul>
        <li><a href="#casar-histogramas-de-fotos">Casar histogramas de fotos</a></li>
      </ul>
      <ul>
        <li><a href="#copiar-arquivos-selecionados">Copiar arquivos selecionados</a></li>
      </ul>
      <ul>
        <li><a href="#fotos-por-blocos">Fotos por blocos</a></li>
      </ul>
      <ul>
        <li><a href="#gerar-arquivo-de-gcp-a-partir-de-camada">Gerar arquivo de GCP a partir de camada</a></li>
      </ul>
      <ul>
        <li><a href="#juntar-pastas">Juntar pastas</a></li>
      </ul>
      <ul>
        <li><a href="#pirâmides-com-compressão-jpeg">Pirâmides com Compressão JPEG</a></li>
      </ul>
      <ul>
        <li><a href="#remover-banda-alfa">Remover banda alfa</a></li>
      </ul>
      <ul>
        <li><a href="#salvar-como-jpeg">Salvar como JPEG</a></li>
      </ul>
      </li><li>
      <a href="#estatística-espacial">Estatística Espacial</a>
      <ul>
        <li><a href="#distância-padrão">Distância padrão</a></li>
      </ul>
      <ul>
        <li><a href="#elipses-de-confiança">Elipses de confiança</a></li>
      </ul>
      <ul>
        <li><a href="#pontos-aleatórios-gaussiano">Pontos aleatórios gaussiano</a></li>
      </ul>
      <ul>
        <li><a href="#pontos-mais-próximos">Pontos mais próximos</a></li>
      </ul>
      <ul>
        <li><a href="#tendência-central">Tendência central</a></li>
      </ul>
      </li><li>
      <a href="#gnss">GNSS</a>
      <ul>
        <li><a href="#correção-de-pontos-rtk">Correção de Pontos RTK</a></li>
      </ul>
      <ul>
        <li><a href="#nmea-para-camada">NMEA para camada</a></li>
      </ul>
      <ul>
        <li><a href="#pos-para-camada">POS para camada</a></li>
      </ul>
      <ul>
        <li><a href="#semicinemático">Semicinemático</a></li>
      </ul>
      </li><li>
      <a href="#mão-na-roda">Mão na Roda</a>
      <ul>
        <li><a href="#medir-camadas">Medir camadas</a></li>
      </ul>
      <ul>
        <li><a href="#pegar-atributo-pela-localização">Pegar atributo pela localização</a></li>
      </ul>
      <ul>
        <li><a href="#planilha-para-camada-de-pontos">Planilha para camada de pontos</a></li>
      </ul>
      </li><li>
      <a href="#postgis">PostGIS</a>
      <ul>
        <li><a href="#backup-de-bd">Backup de BD</a></li>
      </ul>
      <ul>
        <li><a href="#clonar-bd">Clonar BD</a></li>
      </ul>
      <ul>
        <li><a href="#deletar-bd">Deletar BD</a></li>
      </ul>
      <ul>
        <li><a href="#importar-raster">Importar raster</a></li>
      </ul>
      <ul>
        <li><a href="#renomear-bd">Renomear BD</a></li>
      </ul>
      <ul>
        <li><a href="#restaurar-bd">Restaurar BD</a></li>
      </ul>
      <ul>
        <li><a href="#trocar-codificação-de-sql">Trocar codificação de SQL</a></li>
      </ul>
      </li><li>
      <a href="#raster">Raster</a>
      <ul>
        <li><a href="#aritmética-de-bandas">Aritmética de bandas</a></li>
      </ul>
      <ul>
        <li><a href="#carregar-raster-pela-localização">Carregar raster pela localização</a></li>
      </ul>
      <ul>
        <li><a href="#casamento-de-histograma">Casamento de Histograma</a></li>
      </ul>
      <ul>
        <li><a href="#classificação-supervisionada">Classificação supervisionada</a></li>
      </ul>
      <ul>
        <li><a href="#composição-rgb">Composição RGB</a></li>
      </ul>
      <ul>
        <li><a href="#compressão-jpeg">Compressão JPEG</a></li>
      </ul>
      <ul>
        <li><a href="#definir-pixel-nulo">Definir pixel nulo</a></li>
      </ul>
      <ul>
        <li><a href="#dividir-raster">Dividir raster</a></li>
      </ul>
      <ul>
        <li><a href="#esburacar-raster">Esburacar raster</a></li>
      </ul>
      <ul>
        <li><a href="#estatísticas-zonais">Estatísticas zonais</a></li>
      </ul>
      <ul>
        <li><a href="#estimar-valor-de-ponto-a-partir-de-raster">Estimar valor de ponto a partir de Raster</a></li>
      </ul>
      <ul>
        <li><a href="#extrair-banda-de-raster">Extrair banda de raster</a></li>
      </ul>
      <ul>
        <li><a href="#inventário-de-dados-raster">Inventário de dados raster</a></li>
      </ul>
      <ul>
        <li><a href="#limiarização-binária">Limiarização Binária</a></li>
      </ul>
      <ul>
        <li><a href="#mosaicar-raster">Mosaicar raster</a></li>
      </ul>
      <ul>
        <li><a href="#rgb-para-hsv">RGB para HSV</a></li>
      </ul>
      <ul>
        <li><a href="#reescalonar-para-8-bits">Reescalonar para 8 bits</a></li>
      </ul>
      <ul>
        <li><a href="#remendar-vazios-de-raster">Remendar vazios de raster</a></li>
      </ul>
      </li><li>
      <a href="#reambulação">Reambulação</a>
      <ul>
        <li><a href="#fotos-com-geotag">Fotos com geotag</a></li>
      </ul>
      <ul>
        <li><a href="#kml-com-fotos">KML com fotos</a></li>
      </ul>
      <ul>
        <li><a href="#redimensionar-fotos">Redimensionar fotos</a></li>
      </ul>
      </li><li>
      <a href="#relevo">Relevo</a>
      <ul>
        <li><a href="#diferença-de-mde">Diferença de MDE</a></li>
      </ul>
      <ul>
        <li><a href="#exportar-mde-como-texto">Exportar MDE como Texto</a></li>
      </ul>
      <ul>
        <li><a href="#filtro-de-mde">Filtro de MDE</a></li>
      </ul>
      <ul>
        <li><a href="#gerar-pontos-cotados">Gerar Pontos Cotados</a></li>
      </ul>
      </li><li>
      <a href="#vetor">Vetor</a>
      <ul>
        <li><a href="#calcular-ângulos-de-polígono">Calcular ângulos de polígono</a></li>
      </ul>
      <ul>
        <li><a href="#estender-linhas">Estender linhas</a></li>
      </ul>
      <ul>
        <li><a href="#inverter-ordem-dos-vértices">Inverter ordem dos vértices</a></li>
      </ul>
      <ul>
        <li><a href="#linhas-para-polígono">Linhas para polígono</a></li>
      </ul>
      <ul>
        <li><a href="#mesclar-linhas-na-direção">Mesclar linhas na direção</a></li>
      </ul>
      <ul>
        <li><a href="#pontos-para-polígono">Pontos para polígono</a></li>
      </ul>
      <ul>
        <li><a href="#sequenciar-linhas">Sequenciar linhas</a></li>
      </ul>
      <ul>
        <li><a href="#sequenciar-pontos">Sequenciar pontos</a></li>
      </ul>
      <ul>
        <li><a href="#sobreposição-de-polígonos">Sobreposição de polígonos</a></li>
      </ul>
      </li>
  </ol>
</details>




## Cadastre


### Adjoiner Lines
Generates adjoiner lines from a polygon layer of parcels.
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="https://github.com/LEOXINGU/lftools/blob/main/images/tutorial/cadastre_adjoiners.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

### Connect features
Creates new vertices between adjacent polygons to ensure perfect connectivity (topology) between them.
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="https://github.com/LEOXINGU/lftools/blob/main/images/tutorial/cadastre_connectFeatures.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

### Front Lot Lines
Generates front lot lines from a polygon layer of parcels.
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="https://github.com/LEOXINGU/lftools/blob/main/images/tutorial/cadastre_frontlotline.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

### Geographic Numbering
This tool fills in a numeric attribute following a geographic criterion, for example: from north to south and west to east.</br>Note: This algorithm uses the feature centroid to sort geographically.
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="https://github.com/LEOXINGU/lftools/blob/main/images/tutorial/cadastre_geonumbering.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

### Orient polygons
This tool orients the geometry of polygon-like features clockwise or counterclockwise, defining the first vertex as the north, south, east, or west.
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="https://github.com/LEOXINGU/lftools/blob/main/images/tutorial/vect_orient_polygon.jpg"></td>
    </tr>
  </tbody>
</table>
</div>



## Cartography


### Coordinates to UTM grid
This algorithm returns the frame related to a scale of the Brazilian Mapping System. The generated frame, which is a polygon, is calculated from a Point defined by the user.
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="https://github.com/LEOXINGU/lftools/blob/main/images/tutorial/grid_coord_utm.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

### Extent to UTM grids
This algorithm returns the polygons correspondent to the <b>frames</b> related to a scale of the Brazilian Mapping System from a specific <b>extent</b> definied by the user.
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="https://github.com/LEOXINGU/lftools/blob/main/images/tutorial/grid_ext_utm.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

### Name to UTM grid
This algorithm returns the polygon correspondent to the frame related to a scale of the Brazilian Mapping System based on the Map Index (MI). Example: MI = 1214-1
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="https://github.com/LEOXINGU/lftools/blob/main/images/tutorial/grid_inom_utm.jpg"></td>
    </tr>
  </tbody>
</table>
</div>



## Documents


### Area and perimeter report
This tool generates a Report for the Analytical Calculation of Area, Azimuths, Polygon Sides, UTM Projection and Geodetic Coordinates of a Property.
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="https://github.com/LEOXINGU/lftools/blob/main/images/tutorial/doc_analytical_results.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

### Deed description
Elaboration of Deed Description based on vector layers that define a property.
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="https://github.com/LEOXINGU/lftools/blob/main/images/tutorial/doc_descriptive_memorial.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

### Geodetic mark report
This tool generates report(s) with the informations about a geodetic landmarks automatically from the "reference_point_p" layer.
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="https://github.com/LEOXINGU/lftools/blob/main/images/tutorial/doc_mark.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

### Points from Deed Description
Performs the reconstitution of a Deed Description using Regular Expressions (RegEx).
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="https://github.com/LEOXINGU/lftools/blob/main/images/tutorial/doc_pointsFromText.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

### Synthetic deed description
This tool generates the Vertices and Sides Descriptive Table, also known as Synthetic Deed Description, based on the attributes, sequence and code, in the point layer's attribute table.
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="https://github.com/LEOXINGU/lftools/blob/main/images/tutorial/doc_descriptive_table.jpg"></td>
    </tr>
  </tbody>
</table>
</div>



## Drones


### Copy selected files
This tool makes it possible to copy or move files to a new folder from a point layer with file paths.
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="https://github.com/LEOXINGU/lftools/blob/main/images/tutorial/drone_copySelectedFiles.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

### Generate GCP file from layer
Generate text file with Ground Control Points (GCP) from a point layer.
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="https://github.com/LEOXINGU/lftools/blob/main/images/tutorial/drone_createGCP.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

### Georeferencing Adjustment
This tool performs the georeferencing adjustment of any raster image using Ground Control Points.</br>     The following types of coordinate transformation can be used:</br>◼️ <b>Translation Transformation</b>: 1 vector without adjustment / 2 or + vectors with adjustment.</br>◼️ <b>Conformal Transformation (2D Helmert)</b>: 2 vectors without adjustment / 3 or + vectors with adjustment.</br>◼️ <b>Affine Transformation</b>: 3 vectors without adjustment / 4 or + vectors with adjustment.
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="https://github.com/LEOXINGU/lftools/blob/main/images/tutorial/drone_georref_adjust.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

### Join folders
This tool has the objective of joining the files from several folders in another new folder, with the possibility of <b>renaming</b> the files.</br>    It is a very useful procedure for joining multiple drone images with repeated names into a single folder.
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="https://github.com/LEOXINGU/lftools/blob/main/images/tutorial/drone_joinFolders.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

### Overviews with JPEG compression
This tool aims to create an Overviews file (.ovr). This algorithm has the advantage of applying a JPEG compression at each level, greatly reducing the generated file size.
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="https://github.com/LEOXINGU/lftools/blob/main/images/tutorial/raster_overviews.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

### Photos Histogram Matching
This tool performs histogram matching of the JPEG photo files of one input photo layer relative to another reference photo layer.
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="https://github.com/LEOXINGU/lftools/blob/main/images/tutorial/drone_histogram.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

### Photos by blocks
This tool separates drone photographs into new folders to be processed by blocks, from a layer of polygons (blocks) and from layers of geotagged photographs.
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="https://github.com/LEOXINGU/lftools/blob/main/images/tutorial/drone_photosByBlocks.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

### Point cloud adjustment
This tool performs the horizontal and vertical adjustment of Cloud of Points in (TXT) format using LineStringZ vectors.
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="https://github.com/LEOXINGU/lftools/blob/main/images/tutorial/drone_point_cloud_adjust.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

### Remove alpha band
This tool removes the 4th band (apha band), transfering the transparency information as "NoData" to pixels of the RGB output.
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="https://github.com/LEOXINGU/lftools/blob/main/images/tutorial/raster_remove_alpha.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

### Save as JPEG
Exports any 8 bit RGB or RGBA raster layer as a JPEG file. Ideal for reducing the size of the output file. It performs a lossy JPEG compression that, in general, the loss of quality goes unnoticed visually.
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="https://github.com/LEOXINGU/lftools/blob/main/images/tutorial/raster_jpeg_tfw.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

### Vertical adjustment
This tool performs the vertical adjustment of Digital Elevation Models (DEM) from Ground Control Points (GCP).
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="https://github.com/LEOXINGU/lftools/blob/main/images/tutorial/drone_verticalAdjustment.jpg"></td>
    </tr>
  </tbody>
</table>
</div>



## Easy


### Get attribute by location
This algorithm fills in the attributes of a specific field from another layer, in such a way that the feature's centroid intercepts the corresponding feature from the other layer.</br>The source and destination fields must be indicated to fill in the attributes.
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="https://github.com/LEOXINGU/lftools/blob/main/images/tutorial/easy_get_attributes.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

### Measure layers
This tool calculates the line feature's lengths and polygon feature's perimeter and area in virtual fields for all vector layers.
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="https://github.com/LEOXINGU/lftools/blob/main/images/tutorial/easy_measure_layer.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

### Table to point layer
Generates a <b>point layer</b> from a coordinate table, whether it comes from a Microsoft <b>Excel</b> spreadsheet (.xls), Open Document Spreadsheet (.ods), or even attributes from another layer.
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="https://github.com/LEOXINGU/lftools/blob/main/images/tutorial/easy_coord_layer.jpg"></td>
    </tr>
  </tbody>
</table>
</div>



## GNSS


### NMEA to layer
Loads a NMEA file (protocol 0183) from GNSS receivers as a point layer.</br>Modes:</br>◼️ Kinematic - generates all tracked points with their accuracies (PDOP, HDOP and VDOP) and number of satellites.</br>◼️ Static - calculates the mean and standard deviation of the observed points, for all points or only for fixed solution points (best result).
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="https://github.com/LEOXINGU/lftools/blob/main/images/tutorial/gnss_nmea.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

### POS file (.pos) to layer
Loads a POS file (.pos) from GNSS processing as a point layer.</br>Compatibility: RTKLIB, IBGE-PPP.</br>Types:</br>◼️ All processed points</br>◼️ Last point
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="https://github.com/LEOXINGU/lftools/blob/main/images/tutorial/gnss_pos2layer.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

### RTK Points Correction
Performs base RTK correction using post-process coordinates, for example by PPP, and applies corrections to all rover points.
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="https://github.com/LEOXINGU/lftools/blob/main/images/tutorial/gnss_rtk_correction.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

### Stop and Go
It finds the central points (vertices) of the concentrations of points surveyed by the Kinematic method (stop and go) from the processing of GNSS data.</br>Input data:</br>◼️ GNSS point layer from RTKLIB or IBGE-PPP from .pos file</br>◼️ Minimum time to survey the point in minutes</br>◼️ Tolerance in centimeters to consider the static point
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="https://github.com/LEOXINGU/lftools/blob/main/images/tutorial/gnss_ppk.jpg"></td>
    </tr>
  </tbody>
</table>
</div>



## PostGIS


### Backup database
This tool creates a <b>backup</b> file in the "<b>.sql</b>" format for a PostgreSQL server database.
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="https://github.com/LEOXINGU/lftools/blob/main/images/tutorial/post_backup.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

### Change SQL encoding
This tool changes the encoding type of a .sql file. A new file will be created with the user-defined encoding.</br>In some cases, this is a possible solution  to transfer data between different operating systems, for example from Windows to Linux, and vice versa.
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="https://github.com/LEOXINGU/lftools/blob/main/images/tutorial/post_encoding.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

### Clone database
This tool allows the user to clone any PostgreSQL database. From a model database, another database that has exactly the same (schema and instances) is generated with a new name defined by the operator.</br>Note: To create more than one "clone", the new database names must be filled and separated by "comma".
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="https://github.com/LEOXINGU/lftools/blob/main/images/tutorial/post_clonedb.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

### Delete database
This tool allows you to delete / drop any PostgreSQL database.</br>Notes:</br>- To run this operation, the database must be disconnected. This means, that it must not be opened in any software (PgAdmin, QGIS, etc.).</br>- To delete more than one database, the names must be filled and separated by "comma".</br><p style="color:red;">Attention: This operation is irreversible, so be sure before running it!</p>
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="https://github.com/LEOXINGU/lftools/blob/main/images/tutorial/post_deletedb.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

### Import raster
This tool allows you to load a raster layer into a PostGIS database.
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="https://github.com/LEOXINGU/lftools/blob/main/images/tutorial/post_importraster.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

### Rename database
This tool allows you to rename a PostgreSQL database.</br>Note: To run this operation, the database must be disconnected. This means, that it must not be opened in any software (PgAdmin, QGIS, etc.).
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="https://github.com/LEOXINGU/lftools/blob/main/images/tutorial/post_renamedb.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

### Restore database
This tool allows you to restore a database content by importing all the backup information in a ".sql" file into a PostgreSQL server.
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="https://github.com/LEOXINGU/lftools/blob/main/images/tutorial/post_restore.jpg"></td>
    </tr>
  </tbody>
</table>
</div>



## Raster


### Band Arithmetic
Performs an arithmetic operation on the bands of a raster. The predefined formula is used to calculate the Green Leaf Index (GLI) for a RGB raster. However you can enter your own formula.</br>Examples:</br>NDVI with RGN raster: ( b3 - b1) / (b3 + b1)</br>NDWI with RGN raster: ( b3 - b2) / (b3 + b2)</br>GLI with RGB raster: (2*b2 - b1 - b3) / (2*b2 + b1 + b3)</br>VARI with RGB raster: (b2 - b1) / (b2 + b1 - b3)</br>VIgreen with RGB raster: (b2 - b1) / (b2 + b1)</br>Obs.:</br>The operators supported are:  + , - , * , /
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="https://github.com/LEOXINGU/lftools/blob/main/images/tutorial/raster_bandArithmetic.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

### Binary Thresholding
Creates a binarized raster, dividing the input raster into two distinct classes from statistical data (lower and upper threshold) from area or point samples. Optionally, minimum and maximum threshold values can also be set.</br>A class matches the values within the range of thresholds, where the value 1 (true) is returned. The other class corresponds to values outside the range, returning the value 0 (false).
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="https://github.com/LEOXINGU/lftools/blob/main/images/tutorial/raster_thresholding.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

### Create holes in raster
Creates holes in Raster by defining "no data" pixels (transparent) from the Polygon Layer.
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="https://github.com/LEOXINGU/lftools/blob/main/images/tutorial/raster_create_holes.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

### Define null cells
Cells of a raster with values outside the interval (minimum and maximum) are defined as null value.
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="https://github.com/LEOXINGU/lftools/blob/main/images/tutorial/raster_define_null_px.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

### Estimate point value from Raster
This tool estimates the value of the points from Raster, making the proper interpolation of the nearest pixels (cells).
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="https://github.com/LEOXINGU/lftools/blob/main/images/tutorial/raster_getpointvalue.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

### Extract raster band
Extracts a difined band of a raster (for multiband rasters).
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="https://github.com/LEOXINGU/lftools/blob/main/images/tutorial/raster_extract_band.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

### Fill with patches
Fills Raster null pixels (no data) with data obtained from other smaller raster layers (Patches).
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="https://github.com/LEOXINGU/lftools/blob/main/images/tutorial/raster_fill_holes.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

### Histogram matching
This tool matches the histogram of a raster layer in relation to another reference raster layer.
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="https://github.com/LEOXINGU/lftools/blob/main/images/tutorial/raster_histogrammatching.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

### JPEG compression
JPEG compression is a lossy method to reduce the raster file size (about to 10%). The compression level can be adjusted, allowing a selectable tradeoff between storage size and image quality.
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="https://github.com/LEOXINGU/lftools/blob/main/images/tutorial/raster_jpeg_compress.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

### Load raster by location
Loads a set of raster files that intersect the geometries of an input vector layer.</br>    Optionally, it is possible to copy the selected rasters and paste them in another folder.
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="https://github.com/LEOXINGU/lftools/blob/main/images/tutorial/raster_loadByLocation.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

### Mosaic raster
Creates raster mosaic: a combination or merge of two or more images.
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="https://github.com/LEOXINGU/lftools/blob/main/images/tutorial/raster_mosaic.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

### RGB composite
Combine three image bands into one picture by display each band as either Red, Green or Blue.
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="https://github.com/LEOXINGU/lftools/blob/main/images/tutorial/raster_rgb.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

### RGB to HSV
Converts the red, green, and blue values of an RGB image to Hue (H), Saturation (S), and Value (V) images.
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="https://github.com/LEOXINGU/lftools/blob/main/images/tutorial/raster_rgb2hsv.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

### Raster data inventory
Creates a vector layer with the inventory of raster files in a folder. The geometry type of the features of this layer can be Polygon (bounding box) or Point (centroid).
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="https://github.com/LEOXINGU/lftools/blob/main/images/tutorial/raster_inventory.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

### Rescale to 8 bit
Rescales the values of the raster pixels with radiometric resolution of 16 bits (or even 8 bits or float) to exactly the range of 0 to 255, creating a new raster with 8 bits (byte) of radiometric resolution.
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="https://github.com/LEOXINGU/lftools/blob/main/images/tutorial/raster_histogram.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

### Split raster
Splits a raster dataset into smaller pieces, by horizontal and vertical tiles.
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="https://github.com/LEOXINGU/lftools/blob/main/images/tutorial/raster_split.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

### Supervised classification
Performs the supervised classification of a raster layer with two or more bands.
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="https://github.com/LEOXINGU/lftools/blob/main/images/tutorial/raster_classification.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

### Zonal Statistics
This algorithm calculates statistics for the bands of a raster layer, categorized by zones defined in a polygon type vector layer.</br>The values of the raster cells where the pixel center is exactly inside the polygon are considered in the statistics.
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="https://github.com/LEOXINGU/lftools/blob/main/images/tutorial/raster_zonalstatistics.jpg"></td>
    </tr>
  </tbody>
</table>
</div>



## Reambulation


### KML with photos
Creates a KML file embedding in that single file all photographs in base64 textual format to be viewed in Google Earth.</br>    Images are resized to a new size corresponding to the image's largest side.
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="https://github.com/LEOXINGU/lftools/blob/main/images/tutorial/reamb_kml_photos.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

### Photos with geotag
Imports photos with geotag to a Point Layer.
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="https://github.com/LEOXINGU/lftools/blob/main/images/tutorial/reamb_geotag.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

### Resize photos
The largest width or height value of the original image is resized to the user-defined value. The short side is scaled proportionately.</br>    Note: The metadata is preserved.
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="https://github.com/LEOXINGU/lftools/blob/main/images/tutorial/reamb_resize_photo.jpg"></td>
    </tr>
  </tbody>
</table>
</div>



## Relief


### DEM difference
This tool performs the difference between two Digital Elevation Models (DEM).</br>Minuend is the raster to be subtracted.</br>Subtrahend is the rastar that is subtracting.
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="https://github.com/LEOXINGU/lftools/blob/main/images/tutorial/relief_difference.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

### DEM filter
This tool applies the filtering technique in the Raster pixel by pixel, based on the gray level values of neighboring pixels.</br>The filtering process is done using matrices called masks (or kernel), which are applied to the image.
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="https://github.com/LEOXINGU/lftools/blob/main/images/tutorial/relief_demfilter.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

### DEM to Text
This tool exports a Digital Elevation Model (DEM) as a text file (txt) for later transformation into a point cloud.</br>Optionally, the associated Orthomosaic RGB colors can be taken to the text file.
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="https://github.com/LEOXINGU/lftools/blob/main/images/tutorial/relief_dem2txt.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

### Generate Spot Elevations
This tool generates a layer of points with <b>Spot Elevations</b> from a <b>Digital Terrain Model</b> and a vector layer of <b>contour lines</b>.
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="https://github.com/LEOXINGU/lftools/blob/main/images/tutorial/relief_spot_elevation.jpg"></td>
    </tr>
  </tbody>
</table>
</div>



## Spatial Statistics


### Central Tendency
This tool returns the central tendency point(s) for clustering points of entry points.</br>The following statistics can be obtained by grouping:</br>◼️ <b>Mean Center</b>: calculation of the average in X and Y</br>◼️ <b>Median Center</b>: calculation of the median in X and Y (less influenced by outliers)</br>◼️ <b>Central Feature</b>: identification of the central feature (smallest Euclidean distance)</br>Note: Layer in a projected SRC gets more accurate results.
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="https://github.com/LEOXINGU/lftools/blob/main/images/tutorial/stat_central_tendency.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

### Confidence ellipses
Creates ellipses based on the covariance matrix to summarize the spatial characteristics of point type geographic features: central tendency, dispersion, and directional trends.
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="https://github.com/LEOXINGU/lftools/blob/main/images/tutorial/stat_ellipses.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

### Gaussian random points
Generate gaussian (normal) random points in 2D space with a given mean position (X0, Y0), standard deviation for X and Y, and rotation angle.
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="https://github.com/LEOXINGU/lftools/blob/main/images/tutorial/stat_random_points.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

### Nearest points
Calculates the sigmax, sigmay and sigmaz precisions (when available) of the closest points to each reference point considering a maximum distance or a minimum number of closest points.</br>Output: Multipoint layer with positional accuracies in meters and other statistics.</br>1) Max distance: get all points within the distance.</br>2) Minimum quantity: get all the closest points, regardless of the maximum distance.</br>3) Maximum distance and minimum quantity: get only the closest points that are within the maximum distance.
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="https://github.com/LEOXINGU/lftools/blob/main/images/tutorial/stat_nearestPoints.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

### Standard Distance
Measures the degree to which features are concentrated or dispersed around the geometric mean center.
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="https://github.com/LEOXINGU/lftools/blob/main/images/tutorial/stat_standard_distance.jpg"></td>
    </tr>
  </tbody>
</table>
</div>



## Survey


### Azimuth and distance
Calculation of points or line from a set of azimuths and distances.
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="https://github.com/LEOXINGU/lftools/blob/main/images/tutorial/survey_azimuth_distance.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

### Closed polygonal
Calculates the adjusted coordinates from angles and horizontal distances of a Closed Polygonal.
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="https://github.com/LEOXINGU/lftools/blob/main/images/tutorial/survey_closed_polygonal.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

### Coordinate transformation 2D
This tool performs the following types of coordinate transformation:</br>◼️ <b>Translation Transformation</b>: 1 vector without adjustment / 2 or + vectors with adjustment.</br>◼️ <b>Conformal Transformation (2D Helmert)</b>: 2 vectors without adjustment / 3 or + vectors with adjustment.</br>◼️ <b>Affine Transformation</b>: 3 vectors without adjustment / 4 or + vectors with adjustment.</br>With this tool it is possible to perform correctly the georeferencing of vector files in QGIS.</br>
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="https://github.com/LEOXINGU/lftools/blob/main/images/tutorial/survey_helmert2D.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

### Estimate 3D coordinates
This tool calculates the coordinates (X, Y, Z) of a point from azimuth and zenith angle measurements observed from two or more stations with known coordinates using the Foward Intersection Method adjusted by the Minimum Distances.
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="https://github.com/LEOXINGU/lftools/blob/main/images/tutorial/survey_3D_coord.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

### Local Geodetic System transform
</br>This algorithm transforms coordinates between the following reference systems:</br>- geodetic <b>(λ, ϕ, h)</b>;</br>- geocentric or ECEF <b>(X, Y, Z)</b>; and</br>- topocentric in a local tangent plane <b>(E, N, U)</b>.</br>Default values for origin coordinates can be applied to Recife / Brazil.
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="https://github.com/LEOXINGU/lftools/blob/main/images/tutorial/survey_LTP.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

### Traverse adjustment
This algorithm performs the traverse adjustments of a framed polygonal by least squares method, where  the distances, angles, and directions observations are adjusted simultaneously, providing the most probable values for the given data set.  Futhermore, the observations can be rigorously weighted based on their estimated errors and adjusted accordingly.
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="https://github.com/LEOXINGU/lftools/blob/main/images/tutorial/survey_traverse.jpg"></td>
    </tr>
  </tbody>
</table>
</div>



## Vector


### Calculate polygon angles
This algorithm calculates the inner and outer angles of the polygon vertices of a layer. The output layer corresponds to the points with the calculated angles stored in the respective attributes.
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="https://github.com/LEOXINGU/lftools/blob/main/images/tutorial/vect_polygon_angles.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

### Extend lines
Extends lines at their <b>start</b> and/or <b>end</b> points.
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="https://github.com/LEOXINGU/lftools/blob/main/images/tutorial/vect_extend_lines.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

### Line sequence
This script fills in a certain attribute of the features of a layer of lines according to their connectivity sequence between them.
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="https://github.com/LEOXINGU/lftools/blob/main/images/tutorial/vect_line_sequence.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

### Lines to polygon
This tool generates a polygon layer from a connected line layer.
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="https://github.com/LEOXINGU/lftools/blob/main/images/tutorial/vect_lines2polygon.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

### Merge lines in direction
This algorithm merges lines that touch at their starting or ending points and has the same direction (given a tolerance in degrees). <p>For the attributes can be considered:</p>1 - merge lines that have the same attributes; or</li><li>2 - keep the attributes of the longest line.</li>
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="https://github.com/LEOXINGU/lftools/blob/main/images/tutorial/vect_directional_merge.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

### Overlapping polygons
Identifies the overlap between features of a polygon type layer.
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="https://github.com/LEOXINGU/lftools/blob/main/images/tutorial/vect_overlapping.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

### Points to polygon
This tool generates a polygon layer from a point layer and its filled order (sequence) attributes.
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="https://github.com/LEOXINGU/lftools/blob/main/images/tutorial/vect_point2polygon.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

### Reverse vertex order
Inverts vertex order for polygons and lines.
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="https://github.com/LEOXINGU/lftools/blob/main/images/tutorial/vect_reverse_vertex_sequence.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

### Sequence points
This script fills a certain attribute of the features of a layer of points according to its sequence in relation to the polygon of another layer.
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="https://github.com/LEOXINGU/lftools/blob/main/images/tutorial/vect_sequence_points.jpg"></td>
    </tr>
  </tbody>
</table>
</div>






## Agrimensura


### Azimute e distância
Cálculo de pontos ou linha a partir de um conjunto de azimutes e distâncias.
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="https://github.com/LEOXINGU/lftools/blob/main/images/tutorial/survey_azimuth_distance.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

### Estimar coordenadas 3D
Esta ferramenta calcula as coordenadas (X,Y,Z) de um ponto a partir de medições de azimute e ângulo zenital observados de duas ou mais estações de coordenadas conhecidas utilizando o Método de Interseção à Vante ajustado pelas Distâncias Mínimas.
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="https://github.com/LEOXINGU/lftools/blob/main/images/tutorial/survey_3D_coord.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

### Poligonal enquadrada
Este algoritmo realiza o ajustamento de poligonal enquadrada pelo método dos mínimos quadrados, onde as observações de distâncias, ângulos e direções são ajustadas simultaneamente, fornecendo os valores mais prováveis para o conjunto de dados. Além disso, as observações podem ser rigorosamente ponderadas considerando os erros estimados e ajustados.
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="https://github.com/LEOXINGU/lftools/blob/main/images/tutorial/survey_traverse.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

### Poligonal fechada
Cálculo das coordenadas ajustadas a partir de medições de ângulos e distâncias de uma poligonal fechada.
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="https://github.com/LEOXINGU/lftools/blob/main/images/tutorial/survey_closed_polygonal.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

### Transformação de coordenadas 2D
Esta ferramenta realiza os seguintes tipos de transformação de coordenadas:</br>◼️	<b>Transformação de Translação</b>: 1 vetor sem ajustamento / 2 ou + vetores com ajustamento.</br>◼️	<b>Transformação Conforme (Helmert 2D)</b>: 2 vetores sem ajustamento / 3 ou + vetores com ajustamento.</br>◼️	<b>Transformação Afim</b>: 3 vetores sem ajustamento / 4 ou + vetores com ajustamento.</br>Com esta ferramenta é possível realizar o correto georreferenciamento de arquivos vetoriais no QGIS.</br>
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="https://github.com/LEOXINGU/lftools/blob/main/images/tutorial/survey_helmert2D.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

### Transformação para SGL
Este algoritmo transforma coordenadas entre os seguintes sistemas de referência:</br>- Geodésico <b>(λ, ϕ, h)</b></br>- Geocêntrico ou ECEF <b>(X, Y, Z)</b>;</br>- Topocêntrico <b>(E, N, U)</b>.</br>Default: coordenadas de origem para Recife-PE, Brasil.
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="https://github.com/LEOXINGU/lftools/blob/main/images/tutorial/survey_LTP.jpg"></td>
    </tr>
  </tbody>
</table>
</div>



## Cadastro


### Conectar feições
Gera novos vértices entre polígonos adjacentes para garantir a perfeita conectividade (topologia) entre eles.
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="https://github.com/LEOXINGU/lftools/blob/main/images/tutorial/cadastre_connectFeatures.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

### Linhas de Confrontantes
Gera as linhas de confrontantes das parcelas a partir dos polígonos dos lotes.
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="https://github.com/LEOXINGU/lftools/blob/main/images/tutorial/cadastre_adjoiners.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

### Linhas de Testada
Gera as linhas de testada das parcelas a partir dos polígonos dos lotes.
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="https://github.com/LEOXINGU/lftools/blob/main/images/tutorial/cadastre_frontlotline.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

### Numerar geograficamente
Esta ferramenta preenche um atributo numérico seguindo um critério geográfico, por exemplo de norte para sul e oeste para leste.</br>Obs.: Este algoritmo utiliza o centroide da feição para ordenar geograficamente.
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="https://github.com/LEOXINGU/lftools/blob/main/images/tutorial/cadastre_geonumbering.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

### Orientar polígonos
Esta ferramenta orienta a geometria de feições do tipo polígono no sentido horário ou antihorário, definindo o primeiro vértice mais ao norte, sul, leste ou oeste.
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="https://github.com/LEOXINGU/lftools/blob/main/images/tutorial/vect_orient_polygon.jpg"></td>
    </tr>
  </tbody>
</table>
</div>



## Cartografia


### Coordenadas para moldura UTM
Este algoritmo retorna o polígono correspondente à <b>moldura</b> relativa a uma escala do <b>Mapeamento Sistemático Brasileiro</b>. Esta moldura é calculada a partir das coordenadas de um <b>Ponto</b> definido pelo usuário.
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="https://github.com/LEOXINGU/lftools/blob/main/images/tutorial/grid_coord_utm.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

### Extensão para molduras UTM
Este algoritmo retorna os polígonos correspondentes às molduras relacionadas a uma escala do Mapeamento Sistemático Brasileiro para uma extensão específica definida pelo usuário.
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="https://github.com/LEOXINGU/lftools/blob/main/images/tutorial/grid_ext_utm.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

### Nome para moldura UTM
Este algoritmo retorna o polígono correspondente à <b>moldura</b> relativa a uma escala do <b>Mapeamento Sistemático Brasileiro</b>. Esta moldura é calculada a partir do Índice de Nomenclatura <b>INOM</b> ou Mapa Índice <b>MI</b> válido, que deve ser dado pelo usuário.
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="https://github.com/LEOXINGU/lftools/blob/main/images/tutorial/grid_inom_utm.jpg"></td>
    </tr>
  </tbody>
</table>
</div>



## Documentos


### Memorial descritivo
Elaboração de Memorial Descritivo a partir de camadas vetorias que definem uma propriedade.
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="https://github.com/LEOXINGU/lftools/blob/main/images/tutorial/doc_descriptive_memorial.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

### Memorial sintético
Esta ferramenta gera a Tabela Descriva de Vértices e Lados, também conhecida como Memorial Descritivo Sintético, a partir de uma camada de pontos com os atributos de código e ordem (sequência) dos pontos.
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="https://github.com/LEOXINGU/lftools/blob/main/images/tutorial/doc_descriptive_table.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

### Monografia de marco geodésico
Esta ferramenta gera monografia(s) de marcos geodésicos de forma automática a partir da camada "reference_point_p".
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="https://github.com/LEOXINGU/lftools/blob/main/images/tutorial/doc_mark.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

### Planilha de área e perímetro
Esta gera o Relatório de Cálculo Analítico de Área, Azimutes, Lados, Coordenadas Planas e Geodésicas de um Imóvel.
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="https://github.com/LEOXINGU/lftools/blob/main/images/tutorial/doc_analytical_results.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

### Reconstituição de Memorial
Realiza a reconstituição de Memorial descritivo utilizando Expressões Regulares (RegEx).
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="https://github.com/LEOXINGU/lftools/blob/main/images/tutorial/doc_pointsFromText.jpg"></td>
    </tr>
  </tbody>
</table>
</div>



## Drones


### Ajuste Vertical
Esta ferramenta realiza o ajuste vertical de Modelos Digitais de Elevação (MDE) a partir de Pontos de Controle no Terreno (GCP).
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="https://github.com/LEOXINGU/lftools/blob/main/images/tutorial/drone_verticalAdjustment.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

### Ajuste de Nuvem de Pontos
Esta ferramenta realiza o ajuste horizontal e vertical de Nuvem de Pontos no formato (TXT) utilizando vetores do tipo LineStringZ.
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="https://github.com/LEOXINGU/lftools/blob/main/images/tutorial/drone_point_cloud_adjust.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

### Ajuste do Georreferenciamento
Esta ferramenta realiza o ajuste do georreferenciamento de qualquer imagem raster utilizando Pontos de Controle no Terreno.</br>    Os seguintes tipos de transformação de coordenadas podem ser utilizados:</br>◼️	<b>Transformação de Translação</b>: 1 vetor sem ajustamento / 2 ou + vetores com ajustamento.</br>◼️	<b>Transformação Conforme (Helmert 2D)</b>: 2 vetores sem ajustamento / 3 ou + vetores com ajustamento.</br>◼️	<b>Transformação Afim</b>: 3 vetores sem ajustamento / 4 ou + vetores com ajustamento.
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="https://github.com/LEOXINGU/lftools/blob/main/images/tutorial/drone_georref_adjust.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

### Casar histogramas de fotos
Esta ferramenta realiza o casamento do histograma dos arquivos de fotos JPEG de uma camada de fotografias de entrada em relação a outra camada de fotografias de referência.
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="https://github.com/LEOXINGU/lftools/blob/main/images/tutorial/drone_histogram.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

### Copiar arquivos selecionados
Esta ferramenta possibilita copiar ou mover arquivos para uma nova pasta a partir de uma camada de pontos com os caminhos dos arquivos.
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="https://github.com/LEOXINGU/lftools/blob/main/images/tutorial/drone_copySelectedFiles.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

### Fotos por blocos
Esta ferramenta separa fotografias de drones em novas pastas para serem processadas por blocos, a partir de uma camada de polígonos (blocos) e da camadas de fotografias com geotag.
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="https://github.com/LEOXINGU/lftools/blob/main/images/tutorial/drone_photosByBlocks.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

### Gerar arquivo de GCP a partir de camada
Gera arquivo texto com Pontos de Controle no Terreno (GCP) a partir de uma camada de pontos.
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="https://github.com/LEOXINGU/lftools/blob/main/images/tutorial/drone_createGCP.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

### Juntar pastas
Esta ferramenta tem o objetivo de juntar os arquivos de várias pastas em uma outra nova pasta, com a possibilidade de <b>renomear</b> os arquivos.</br>É um procedimento muito útil para juntar várias imagens de drone com nomes repetidos em uma única pasta.
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="https://github.com/LEOXINGU/lftools/blob/main/images/tutorial/drone_joinFolders.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

### Pirâmides com Compressão JPEG
Esta ferramenta tem como objetivo criar um arquivo .ovr, correspondente às Overviews (ou pirâmides, em português). Este algoritmo tem a vantagem de aplicar uma compressão JPEG em cada nível, reduzindo bastante o tamanho do arquivo gerado.
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="https://github.com/LEOXINGU/lftools/blob/main/images/tutorial/raster_overviews.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

### Remover banda alfa
Esta ferramenta remove a 4ª banda (banda alfa), transferindo a informação de transparência como "Sem Valor" para os pixels da imagem RGB de saída.
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="https://github.com/LEOXINGU/lftools/blob/main/images/tutorial/raster_remove_alpha.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

### Salvar como JPEG
Exporta qualquer camada raster RGB ou RGBA de 8 bits como um arquivo JPEG. Ideal para reduzir o tamanho do arquivo de saída. Realiza a compressão JPEG com uma pequena perda de qualidade que, em geral, passa despercebida visualmente.
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="https://github.com/LEOXINGU/lftools/blob/main/images/tutorial/raster_jpeg_tfw.jpg"></td>
    </tr>
  </tbody>
</table>
</div>



## Estatística Espacial


### Distância padrão
Mede o grau em que as feições estão concentradas ou dispersas em torno do centro médio geométrico.
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="https://github.com/LEOXINGU/lftools/blob/main/images/tutorial/stat_standard_distance.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

### Elipses de confiança
Cria elipses a partir da matriz variância-covariância para resumir as características espaciais de feções geográficas do tipo ponto: tendência central, dispersão e tendências direcionais.
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="https://github.com/LEOXINGU/lftools/blob/main/images/tutorial/stat_ellipses.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

### Pontos aleatórios gaussiano
Gera pontos aleatórios no espaço 2D a partir de um ponto central (X0, Y0), desvios-padrões para X e Y, e ângulo de rotação.
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="https://github.com/LEOXINGU/lftools/blob/main/images/tutorial/stat_random_points.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

### Pontos mais próximos
Calcula as precisões sigmax, sigmay e sigmaz (quando existir) dos pontos mais próximos de cada ponto de referência considerando uma distância máxima ou uma quantidade mínima de pontos mais próximos.</br>Saída: Camada de multipoint com precisões posicionais em metros e outras estatísticas.</br>1) Distância máxima: busca todos os pontos dentro da distância.</br>2) Quantidade mínima: busca todos os pontos mais próximos, independente de distância máxima.</br>3) Distância máxima e quantidade mínima: busca apenas os pontos mais próximos que estão dentro da distância máxima.
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="https://github.com/LEOXINGU/lftools/blob/main/images/tutorial/stat_nearestPoints.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

### Tendência central
Esta ferramenta retorna o(s) ponto(s) de tendência central para agrupamento de pontos dos pontos de entrada.</br>As seguintes estatísticas pode ser obtidas por agrupamento:</br>◼️ <b>Centro Médio</b>: cálculo da média em X e Y</br>◼️ <b>Centro Mediano</b>: cálculo da mediana em X e Y (menos influenciado por outliers)</br>◼️ <b>Feição Central</b>: identificação da feição central (menor distância euclidiana)</br>Observação: Camada em um SRC projetado obtém resultado mais acurados.
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="https://github.com/LEOXINGU/lftools/blob/main/images/tutorial/stat_central_tendency.jpg"></td>
    </tr>
  </tbody>
</table>
</div>



## GNSS


### Correção de Pontos RTK
Realiza a correção da base RTK utilizando as coordenas pós-processsas, por exemplo pelo PPP, e aplica as correções a todos os pontos Rover.
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="https://github.com/LEOXINGU/lftools/blob/main/images/tutorial/gnss_rtk_correction.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

### NMEA para camada
Carrega um arquivo NMEA de rastreio GNSS (protocolo 0183) como uma camada do tipo ponto.</br>Modos:</br>◼️ Cinemático - gera todos os pontos rastreados com suas precisões (PDOP, HDOP e VDOP) e número de satélites.</br>◼️ Estático - calcula a média e desvio-padrão dos pontos observados, para todos os pontos ou somente para os pontos de solução fixa (melhor resultado).
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="https://github.com/LEOXINGU/lftools/blob/main/images/tutorial/gnss_nmea.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

### POS para camada
Carrega um arquivo POS resultante do processamento de dados GNSS como uma camada do tipo ponto.</br>Compatibilidade: RTKLIB, IBGE-PPP</br>Tipos:</br>◼️ Todos os pontos processados</br>◼️ Último ponto
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="https://github.com/LEOXINGU/lftools/blob/main/images/tutorial/gnss_pos2layer.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

### Semicinemático
Encontra os pontos centrais (vértices) das concentrações de pontos levantados pelo método Seminemático (stop and go) provenientes do processamento de dados GNSS.</br>Dados de entrada:</br>◼️ Camada do tipo ponto gerada do arquivo .pos do RTKLIB ou IBGE-PPP</br>◼️ Tempo mínimo de levantamento do ponto em minutos</br>◼️ Tolerância em centímetros para considerar o ponto estático
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="https://github.com/LEOXINGU/lftools/blob/main/images/tutorial/gnss_ppk.jpg"></td>
    </tr>
  </tbody>
</table>
</div>



## Mão na Roda


### Medir camadas
Esta ferramenta calcula em campos virtuais os comprimentos de feições do tipo linha e o perímetro e área de feições do tipo polígono para todas as camadas.
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="https://github.com/LEOXINGU/lftools/blob/main/images/tutorial/easy_measure_layer.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

### Pegar atributo pela localização
Este algoritmo preenche os atributos de um campo específico a partir de outra camada, tal que o centróide da feição intercepte a feição correspondente da outra camada.</br>Os campos de origem e de destino devem ser indicadas para preenchimento dos atributos.
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="https://github.com/LEOXINGU/lftools/blob/main/images/tutorial/easy_get_attributes.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

### Planilha para camada de pontos
Geração de uma camada de pontos a partir das coordenadas preenchidas em uma planilha do Excel (.xls) ou Open Document Spreadsheet (.ods), ou até mesmo, a partir dos atributos de outra camada.
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="https://github.com/LEOXINGU/lftools/blob/main/images/tutorial/easy_coord_layer.jpg"></td>
    </tr>
  </tbody>
</table>
</div>



## PostGIS


### Backup de BD
Esta ferramenta gera um arquivo de <b>backup</b> no formato "<b>.sql</b>" para um banco de dados de um servidor PostgreSQL.
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="https://github.com/LEOXINGU/lftools/blob/main/images/tutorial/post_backup.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

### Clonar BD
Esta ferramenta permite clonar qualquer banco PostgreSQL. A partir de um banco de dados modelo, é gerado um outro banco exatamente igual (esquema e instâncias) com um novo nome definido pelo operador.</br>Obs.: Para criação de mais de um "clone", os novos nomes dos bancos devem ser inseridos "separados por vírgula".
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="https://github.com/LEOXINGU/lftools/blob/main/images/tutorial/post_clonedb.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

### Deletar BD
Esta ferramenta permite apagar (delete/drop) qualquer banco do PostgreSQL.</br>Obs.:</br>- Para realizar esta operação, é necessário que o banco esteja desconectado, ou seja, não esteja aberto em nenhum software (PgAdmin, QGIS, etc).</br>- Para deletar mais de um BD, os nomes devem ser preenchidos separados por vírgula.</br><p style="color:red;">Atenção: Esta operação é irreversível, portanto esteja seguro quando for executá-la!</p>
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="https://github.com/LEOXINGU/lftools/blob/main/images/tutorial/post_deletedb.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

### Importar raster
Esta ferramenta permite carregar uma camada raster para dentro de um banco de dados PostGIS.
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="https://github.com/LEOXINGU/lftools/blob/main/images/tutorial/post_importraster.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

### Renomear BD
Esta ferramenta permite renomear um banco de dados do PostgreSQL.</br>Nota: Para realizar esta operação, é necessário que o banco de dados esteja desconectado, ou seja, não esteja aberto em nenhum software (PgAdmin, QGIS, etc.).
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="https://github.com/LEOXINGU/lftools/blob/main/images/tutorial/post_renamedb.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

### Restaurar BD
Esta ferramenta permite <b>restaurar</b>, ou seja, importar um banco de dados para um servidor PostgreSQL, a partir de um arquivo de backup no formato "<b>.sql</b>".
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="https://github.com/LEOXINGU/lftools/blob/main/images/tutorial/post_restore.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

### Trocar codificação de SQL
Esta ferramenta realiza a troca do tipo de codificação de um arquivo <b>.sql</b>. Um novo arquivo será criado com a codificação definida pelo usuário.</br>Em alguns casos, esse processo é uma possível solução para transferir dados entre diferentes sistemas operacionais, por exemplo de Window para Linux, e vice-versa.
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="https://github.com/LEOXINGU/lftools/blob/main/images/tutorial/post_encoding.jpg"></td>
    </tr>
  </tbody>
</table>
</div>



## Raster


### Aritmética de bandas
Executa uma operação aritmética entre as bandas de um raster. A fórmula predefinida é usado para calcular o Green Leaf Index (GLI) para um raster RGB. No entanto, você pode inserir sua própria fórmula.</br>Exemplos:</br>NDVI com raster RGN: ( b3 - b1) / (b3 + b1)</br>NDWI com raster RGN: ( b3 - b2) / (b3 + b2)</br>GLI com raster RGB: (2*b2 - b1 - b3) / (2*b2 + b1 + b3)</br>VARI com raster RGB: (b2 - b1) / (b2 + b1 - b3)</br>VIgreen com raster RGB: (b2 - b1) / (b2 + b1)</br>Obs.:</br>Os operadores suportados são: + , - , * , /
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="https://github.com/LEOXINGU/lftools/blob/main/images/tutorial/raster_bandArithmetic.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

### Carregar raster pela localização
Carrega um conjunto de arquivos raster que interceptam as geometrias de uma camada vetorial de entrada.</br>    Opcionalmente é possível copiar os rasters selcionados e colar em outra pasta.
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="https://github.com/LEOXINGU/lftools/blob/main/images/tutorial/raster_loadByLocation.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

### Casamento de Histograma
Esta ferramenta realiza o casamento do histograma de uma camada raster em relação a outra camada raster de referência.
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="https://github.com/LEOXINGU/lftools/blob/main/images/tutorial/raster_histogrammatching.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

### Classificação supervisionada
Realize a classificação supervisionada de camada raster com duas ou mais bandas.
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="https://github.com/LEOXINGU/lftools/blob/main/images/tutorial/raster_classification.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

### Composição RGB
Realiza a combinação de três bandas em uma única imagem, apresentando-as nas bandas vermelha (R), verde (G) e Azul (B).
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="https://github.com/LEOXINGU/lftools/blob/main/images/tutorial/raster_rgb.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

### Compressão JPEG
A compressão JPEG é um método "com perdas" para reduzir o tamanho de um arquivo raster (para aproximadamente 10%). O grau de compressão pode ser ajustado, permitindo um limiar entre o tamanho de armazenamento e a qualidade da imagem.
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="https://github.com/LEOXINGU/lftools/blob/main/images/tutorial/raster_jpeg_compress.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

### Definir pixel nulo
As células do raster com valores fora do intervalo (mínimo e máximo) são definidas como valor nulo.
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="https://github.com/LEOXINGU/lftools/blob/main/images/tutorial/raster_define_null_px.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

### Dividir raster
Divide um raster em pedaços menores, por blocos horizontais e verticais
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="https://github.com/LEOXINGU/lftools/blob/main/images/tutorial/raster_split.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

### Esburacar raster
Cria buracos em Raster definindo pixels nulos (transparentes) a partir de Camada de Polígonos.
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="https://github.com/LEOXINGU/lftools/blob/main/images/tutorial/raster_create_holes.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

### Estatísticas zonais
Este algoritmo calcula estatísticas para as bandas de uma camada raster, categorizados por zonas definidas em camada vetorial do tipo polígono.</br>Os valores das células do raster onde o centro do pixel se encontra exatamente dentro do polígonos são considerados nas estatísticas.
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="https://github.com/LEOXINGU/lftools/blob/main/images/tutorial/raster_zonalstatistics.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

### Estimar valor de ponto a partir de Raster
Esta ferramenta estima o valor dos pontos a partir de Raster, fazendo a devida interpolação dos pixels (células) mais próximos.
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="https://github.com/LEOXINGU/lftools/blob/main/images/tutorial/raster_getpointvalue.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

### Extrair banda de raster
Extrai uma das bandas de um arquivo raster (para imagens multi-bandas/multi-canal).
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="https://github.com/LEOXINGU/lftools/blob/main/images/tutorial/raster_extract_band.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

### Inventário de dados raster
Cria uma camada vetorial com o inventário de arquivos raster de uma pasta. O tipo de geometria das feições dessa camada pode ser Polígono (retângulo envolvente) ou Ponto (centroide).
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="https://github.com/LEOXINGU/lftools/blob/main/images/tutorial/raster_inventory.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

### Limiarização Binária
Cria um raster binarizado, dividindo o raster de entrada em duas classes distintas a partir de dados estatísticos (limiar inferior e superior) de amostras de áreas ou pontuais. Opcionalmente, os valores de limiar mínimo e máximo também podem ser definidos.</br>Uma classe irá corresponder aos valores compreendidos dentro do intervalo dos limiares, sendo retornado o valor 1 (verdadeiro). Já a outra classe correpondem aos valores fora do intervalo, sendo retornado o valor 0 (falso).
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="https://github.com/LEOXINGU/lftools/blob/main/images/tutorial/raster_thresholding.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

### Mosaicar raster
Cria um mosaico: uma combinação ou mesclagem de duas ou mais imagens.
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="https://github.com/LEOXINGU/lftools/blob/main/images/tutorial/raster_mosaic.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

### RGB para HSV
Converte os valores de vermelho, verde e azul de uma imagem RGB em imagens Matiz (H), Saturação (S) e Valor (V).
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="https://github.com/LEOXINGU/lftools/blob/main/images/tutorial/raster_rgb2hsv.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

### Reescalonar para 8 bits
Reescalona os valores dos pixels de raster com resolução radiométrica de 16 bits (ou até mesmo 8 bits ou float) para exatamente o intervalo de 0 a 255, criando um novo raster com 8 bits (byte) de resolução radiométrica.
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="https://github.com/LEOXINGU/lftools/blob/main/images/tutorial/raster_histogram.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

### Remendar vazios de raster
Preenche vazios de Raster (pixels nulos) com dados obtidos de outras camadas raster menores (Remendos).
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="https://github.com/LEOXINGU/lftools/blob/main/images/tutorial/raster_fill_holes.jpg"></td>
    </tr>
  </tbody>
</table>
</div>



## Reambulação


### Fotos com geotag
Importa fotos com geotag para uma camada de pontos.
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="https://github.com/LEOXINGU/lftools/blob/main/images/tutorial/reamb_geotag.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

### KML com fotos
Cria um arquivo KML incorporando nesse único arquivo todas as fotografias em formato textual base64 para ser visualizado no Google Earth.</br>    As imagens são redimensionadas para um novo tamanho correspondente ao maior lado da imagem.
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="https://github.com/LEOXINGU/lftools/blob/main/images/tutorial/reamb_kml_photos.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

### Redimensionar fotos
O maior valor de largura ou altura da imagem original é redimensionado para o valor definido pelo usuário. O lado menor é redimensionado proporcionalmente.</br>    Obs.: Os metadados são preservados.
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="https://github.com/LEOXINGU/lftools/blob/main/images/tutorial/reamb_resize_photo.jpg"></td>
    </tr>
  </tbody>
</table>
</div>



## Relevo


### Diferença de MDE
Esta ferramenta executa a diferença entre dois Modelos Digitais de Elevação (MDE).</br>Minuendo é o raster a ser subtraído.</br>Subtraendo é o rastar que está subtraindo.
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="https://github.com/LEOXINGU/lftools/blob/main/images/tutorial/relief_difference.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

### Exportar MDE como Texto
Esta ferramenta exporta um Modelo Digital de Elevação (MDE) como um arquivo de texto (txt) para posterior transformação em nuvem de pontos.</br>Opcionalmente, as cores RGB associadas do Ortomosaico podem ser levadas para o arquivo de texto.
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="https://github.com/LEOXINGU/lftools/blob/main/images/tutorial/relief_dem2txt.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

### Filtro de MDE
Esta ferramenta aplica a técnica de filtragem no Raster pixel a pixel, baseando-se nos valores dos níveis de cinza dos pixels vizinhos.</br>O processo de filtragem é feito utilizando matrizes denominadas máscaras (ou kernel), as quais são aplicadas sobre a imagem.
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="https://github.com/LEOXINGU/lftools/blob/main/images/tutorial/relief_demfilter.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

### Gerar Pontos Cotados
Esta ferramenta gera uma camada de <b>pontos cotados</b> gerados a partir de um raster correspondente ao <b>Modelo Digital do Terreno</b> e uma camada vetorial do tipo linha correspondente às <b>curvas de nível</b>.
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="https://github.com/LEOXINGU/lftools/blob/main/images/tutorial/relief_spot_elevation.jpg"></td>
    </tr>
  </tbody>
</table>
</div>



## Vetor


### Calcular ângulos de polígono
Este algoritmo calcula os ângulos internos e externos dos vértices de uma camada de polígonos. A camada de pontos de saída tem os ângulos calculados armazenados em sua tabela de atributos.
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="https://github.com/LEOXINGU/lftools/blob/main/images/tutorial/vect_polygon_angles.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

### Estender linhas
Estende linhas nos seus pontos inicial e/ou final.
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="https://github.com/LEOXINGU/lftools/blob/main/images/tutorial/vect_extend_lines.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

### Inverter ordem dos vértices
Inverte a ordem dos vértices para polígonos e linhas.
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="https://github.com/LEOXINGU/lftools/blob/main/images/tutorial/vect_reverse_vertex_sequence.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

### Linhas para polígono
Esta ferramenta gera uma camada de polígono a partir de uma camada de linhas conectadas.
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="https://github.com/LEOXINGU/lftools/blob/main/images/tutorial/vect_lines2polygon.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

### Mesclar linhas na direção
Este algoritmo mescla linhas que se tocam nos seus pontos inicial ou final e tem a mesma direção (dada uma tolerância em graus).<p>Para os atributos pode ser considerado:</p><li>1 - mesclar linhas que tenham os mesmos atributos; ou</li><li>2 - manter os atributos da linha maior.</li>
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="https://github.com/LEOXINGU/lftools/blob/main/images/tutorial/vect_directional_merge.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

### Pontos para polígono
Esta ferramenta gera uma camada de polígono a partir de uma camada de pontos e seus atributos de ordem (sequência) preenchidos.
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="https://github.com/LEOXINGU/lftools/blob/main/images/tutorial/vect_point2polygon.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

### Sequenciar linhas
Este script preenche um determinado atributo das feições de uma camada do tipo linha de acordo com sua sequência de conectividade entre as linhas.
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="https://github.com/LEOXINGU/lftools/blob/main/images/tutorial/vect_line_sequence.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

### Sequenciar pontos
Este script preenche um determinado atributo das feições de uma camada de pontos de acordo com sua sequência em relação ao polígono de outra camada.
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="https://github.com/LEOXINGU/lftools/blob/main/images/tutorial/vect_sequence_points.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

### Sobreposição de polígonos
Identifica a sobreposição entre feições de uma camada do tipo polígono.
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="https://github.com/LEOXINGU/lftools/blob/main/images/tutorial/vect_overlapping.jpg"></td>
    </tr>
  </tbody>
</table>
</div>


