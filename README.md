<!-- PROJECT LOGO -->
<p align="center">
    <img src="images/lftoos_logo.png" alt="Logo" width="90" height="75">
  <h3 align="center">LF Tools</h3>
  <p align="center">
    <b><i>Tools for cartographic production, surveying, digital image processing and spatial analysis</i><b>
    <br />
  </p>
</p>

<!-- TABLE OF CONTENTS -->
<details open="open">
  <summary>Set of Tools</summary>
  <ol>
    <li>
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
        <li><a href="#synthetic-deed-description">Synthetic deed description</a></li>
      </ul>
      </li><li>
      <a href="#easy">Easy</a>
      <ul>
        <li><a href="#measure-layers">Measure layers</a></li>
      </ul>
      <ul>
        <li><a href="#table-to-point-layer">Table to point layer</a></li>
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
        <li><a href="#binary-thresholding">Binary Thresholding</a></li>
      </ul>
      <ul>
        <li><a href="#create-holes-in-raster">Create holes in raster</a></li>
      </ul>
      <ul>
        <li><a href="#define-null-cells">Define null cells</a></li>
      </ul>
      <ul>
        <li><a href="#extract-raster-band">Extract raster band</a></li>
      </ul>
      <ul>
        <li><a href="#fill-with-patches">Fill with patches</a></li>
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
        <li><a href="#raster-data-inventory">Raster data inventory</a></li>
      </ul>
      <ul>
        <li><a href="#remove-alpha-band">Remove alpha band</a></li>
      </ul>
      <ul>
        <li><a href="#rescale-to-8-bit">Rescale to 8 bit</a></li>
      </ul>
      <ul>
        <li><a href="#save-as-jpeg">Save as JPEG</a></li>
      </ul>
      <ul>
        <li><a href="#supervised-classification">Supervised classification</a></li>
      </ul>
      </li><li>
      <a href="#reambulation">Reambulation</a>
      <ul>
        <li><a href="#photos-with-geotag">Photos with geotag</a></li>
      </ul>
      </li><li>
      <a href="#spatial-statistics">Spatial Statistics</a>
      <ul>
        <li><a href="#confidence-ellipses">Confidence ellipses</a></li>
      </ul>
      <ul>
        <li><a href="#gaussian-random-points">Gaussian random points</a></li>
      </ul>
      </li><li>
      <a href="#survey">Survey</a>
      <ul>
        <li><a href="#2d-conformal-transformation">2D conformal transformation</a></li>
      </ul>
      <ul>
        <li><a href="#azimuth-and-distance">Azimuth and distance</a></li>
      </ul>
      <ul>
        <li><a href="#closed-polygonal">Closed polygonal</a></li>
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
        <li><a href="#merge-lines-in-direction">Merge lines in direction</a></li>
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
        <li><a href="#azimute-e-dist??ncia">Azimute e dist??ncia</a></li>
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
        <li><a href="#transforma????o-conforme-2d">Transforma????o conforme 2D</a></li>
      </ul>
      <ul>
        <li><a href="#transforma????o-para-sgl">Transforma????o para SGL</a></li>
      </ul>
      </li><li>
      <a href="#cartografia">Cartografia</a>
      <ul>
        <li><a href="#coordenadas-para-moldura-utm">Coordenadas para moldura UTM</a></li>
      </ul>
      <ul>
        <li><a href="#extens??o-para-molduras-utm">Extens??o para molduras UTM</a></li>
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
        <li><a href="#memorial-sint??tico">Memorial sint??tico</a></li>
      </ul>
      <ul>
        <li><a href="#monografia-de-marco-geod??sico">Monografia de marco geod??sico</a></li>
      </ul>
      <ul>
        <li><a href="#planilha-de-??rea-e-per??metro">Planilha de ??rea e per??metro</a></li>
      </ul>
      </li><li>
      <a href="#estat??stica-espacial">Estat??stica Espacial</a>
      <ul>
        <li><a href="#elipses-de-confian??a">Elipses de confian??a</a></li>
      </ul>
      <ul>
        <li><a href="#pontos-aleat??rios-gaussiano">Pontos aleat??rios gaussiano</a></li>
      </ul>
      </li><li>
      <a href="#m??o-na-roda">M??o na Roda</a>
      <ul>
        <li><a href="#medir-camadas">Medir camadas</a></li>
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
        <li><a href="#trocar-codifica????o-de-sql">Trocar codifica????o de SQL</a></li>
      </ul>
      </li><li>
      <a href="#raster">Raster</a>
      <ul>
        <li><a href="#carregar-raster-pela-localiza????o">Carregar raster pela localiza????o</a></li>
      </ul>
      <ul>
        <li><a href="#classifica????o-supervisionada">Classifica????o supervisionada</a></li>
      </ul>
      <ul>
        <li><a href="#composi????o-rgb">Composi????o RGB</a></li>
      </ul>
      <ul>
        <li><a href="#compress??o-jpeg">Compress??o JPEG</a></li>
      </ul>
      <ul>
        <li><a href="#definir-pixel-nulo">Definir pixel nulo</a></li>
      </ul>
      <ul>
        <li><a href="#esburacar-raster">Esburacar raster</a></li>
      </ul>
      <ul>
        <li><a href="#extrair-banda-de-raster">Extrair banda de raster</a></li>
      </ul>
      <ul>
        <li><a href="#invent??rio-de-dados-raster">Invent??rio de dados raster</a></li>
      </ul>
      <ul>
        <li><a href="#limiariza????o-bin??ria">Limiariza????o Bin??ria</a></li>
      </ul>
      <ul>
        <li><a href="#mosaicar-raster">Mosaicar raster</a></li>
      </ul>
      <ul>
        <li><a href="#reescalonar-para-8-bits">Reescalonar para 8 bits</a></li>
      </ul>
      <ul>
        <li><a href="#remendar-vazios-de-raster">Remendar vazios de raster</a></li>
      </ul>
      <ul>
        <li><a href="#remover-banda-alfa">Remover banda alfa</a></li>
      </ul>
      <ul>
        <li><a href="#salvar-como-jpeg">Salvar como JPEG</a></li>
      </ul>
      </li><li>
      <a href="#reambula????o">Reambula????o</a>
      <ul>
        <li><a href="#fotos-com-geotag">Fotos com geotag</a></li>
      </ul>
      </li><li>
      <a href="#vetor">Vetor</a>
      <ul>
        <li><a href="#calcular-??ngulos-de-pol??gono">Calcular ??ngulos de pol??gono</a></li>
      </ul>
      <ul>
        <li><a href="#estender-linhas">Estender linhas</a></li>
      </ul>
      <ul>
        <li><a href="#inverter-ordem-dos-v??rtices">Inverter ordem dos v??rtices</a></li>
      </ul>
      <ul>
        <li><a href="#mesclar-linhas-na-dire????o">Mesclar linhas na dire????o</a></li>
      </ul>
      <ul>
        <li><a href="#sequenciar-pontos">Sequenciar pontos</a></li>
      </ul>
      </li>
  </ol>
</details>




## Cartography


### Coordinates to UTM grid
This algorithm returns the frame related to a scale of the Brazilian Mapping System. The generated frame, which is a polygon, is calculated from a Point defined by the user.
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="images/tutorial/grid_coord_utm.jpg"></td>
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
      <td><img src="images/tutorial/grid_ext_utm.jpg"></td>
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
      <td><img src="images/tutorial/grid_inom_utm.jpg"></td>
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
      <td><img src="images/tutorial/doc_analytical_results.jpg"></td>
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
      <td><img src="images/tutorial/doc_descriptive_memorial.jpg"></td>
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
      <td><img src="images/tutorial/doc_mark.jpg"></td>
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
      <td><img src="images/tutorial/doc_descriptive_table.jpg"></td>
    </tr>
  </tbody>
</table>
</div>



## Easy


### Measure layers
This tool calculates the line feature's lengths and polygon feature's perimeter and area in virtual fields for all vector layers.
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="images/tutorial/easy_measure_layer.jpg"></td>
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
      <td><img src="images/tutorial/easy_coord_layer.jpg"></td>
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
      <td><img src="images/tutorial/post_backup.jpg"></td>
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
      <td><img src="images/tutorial/post_encoding.jpg"></td>
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
      <td><img src="images/tutorial/post_clonedb.jpg"></td>
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
      <td><img src="images/tutorial/post_deletedb.jpg"></td>
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
      <td><img src="images/tutorial/post_importraster.jpg"></td>
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
      <td><img src="images/tutorial/post_renamedb.jpg"></td>
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
      <td><img src="images/tutorial/post_restore.jpg"></td>
    </tr>
  </tbody>
</table>
</div>



## Raster


### Binary Thresholding
Creates a binarized raster by dividing the input raster into two distinct classes from statistical data (lower and upper threshold) of area samples.</br>A class matches the values within the range of thresholds, where the value 1 (true) is returned. The other class corresponds to values outside the range, returning the value 0 (false).
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="images/tutorial/raster_thresholding.jpg"></td>
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
      <td><img src="images/tutorial/raster_create_holes.jpg"></td>
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
      <td><img src="images/tutorial/raster_define_null_px.jpg"></td>
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
      <td><img src="images/tutorial/raster_extract_band.jpg"></td>
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
      <td><img src="images/tutorial/raster_fill_holes.jpg"></td>
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
      <td><img src="images/tutorial/raster_jpeg_compress.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

### Load raster by location
Loads a set of raster files that intersect the geometries of an input vector layer.
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="images/tutorial/raster_loadByLocation.jpg"></td>
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
      <td><img src="images/tutorial/raster_mosaic.jpg"></td>
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
      <td><img src="images/tutorial/raster_rgb.jpg"></td>
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
      <td><img src="images/tutorial/raster_inventory.jpg"></td>
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
      <td><img src="images/tutorial/raster_remove_alpha.jpg"></td>
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
      <td><img src="images/tutorial/raster_histogram.jpg"></td>
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
      <td><img src="images/tutorial/raster_jpeg_tfw.jpg"></td>
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
      <td><img src="images/tutorial/raster_classification.jpg"></td>
    </tr>
  </tbody>
</table>
</div>



## Reambulation


### Photos with geotag
Imports photos with geotag to a Point Layer.
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="images/tutorial/reamb_geotag.jpg"></td>
    </tr>
  </tbody>
</table>
</div>



## Spatial Statistics


### Confidence ellipses
Creates ellipses based on the covariance matrix to summarize the spatial characteristics of point type geographic features: central tendency, dispersion, and directional trends.
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="images/tutorial/stat_ellipses.jpg"></td>
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
      <td><img src="images/tutorial/stat_random_points.jpg"></td>
    </tr>
  </tbody>
</table>
</div>



## Survey


### 2D conformal transformation
Two-dimensional conformal coordinate transformation, also known as the four-parameter similarity transformation or Helmert 2D, has the characteristic that true shape is retained after transformation.</br>It is typically used in surveying when converting separate surveys into a common reference coordinate system.</br>This transformation involves: Scaling, Rotation and Translations.</br>
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="images/tutorial/survey_helmert2D.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

### Azimuth and distance
Calculation of points or line from a set of azimuths and distances.
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="images/tutorial/survey_azimuth_distance.jpg"></td>
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
      <td><img src="images/tutorial/survey_closed_polygonal.jpg"></td>
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
      <td><img src="images/tutorial/survey_3D_coord.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

### Local Geodetic System transform
</br>This algorithm transforms coordinates between the following reference systems:</br>- geodetic <b>(??, ??, h)</b>;</br>- geocentric or ECEF <b>(X, Y, Z)</b>; and</br>- topocentric in a local tangent plane <b>(E, N, U)</b>.</br>Default values for origin coordinates can be applied to Recife / Brazil.
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="images/tutorial/survey_SGL_coord.jpg"></td>
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
      <td><img src="images/tutorial/survey_traverse.jpg"></td>
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
      <td><img src="images/tutorial/vect_polygon_angles.jpg"></td>
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
      <td><img src="images/tutorial/vect_extend_lines.jpg"></td>
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
      <td><img src="images/tutorial/vect_directional_merge.jpg"></td>
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
      <td><img src="images/tutorial/vect_reverse_vertex_sequence.jpg"></td>
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
      <td><img src="images/tutorial/vect_sequence_points.jpg"></td>
    </tr>
  </tbody>
</table>
</div>






## Agrimensura


### Azimute e dist??ncia
C??lculo de pontos ou linha a partir de um conjunto de azimutes e dist??ncias.
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="images/tutorial/survey_azimuth_distance.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

### Estimar coordenadas 3D
Esta ferramenta calcula as coordenadas (X,Y,Z) de um ponto a partir de medi????es de azimute e ??ngulo zenital observados de duas ou mais esta????es de coordenadas conhecidas utilizando o M??todo de Interse????o ?? Vante ajustado pelas Dist??ncias M??nimas.
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="images/tutorial/survey_3D_coord.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

### Poligonal enquadrada
Este algoritmo realiza o ajustamento de poligonal enquadrada pelo m??todo dos m??nimos quadrados, onde as observa????es de dist??ncias, ??ngulos e dire????es s??o ajustadas simultaneamente, fornecendo os valores mais prov??veis para o conjunto de dados. Al??m disso, as observa????es podem ser rigorosamente ponderadas considerando os erros estimados e ajustados.
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="images/tutorial/survey_traverse.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

### Poligonal fechada
C??lculo das coordenadas ajustadas a partir de medi????es de ??ngulos e dist??ncias de uma poligonal fechada.
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="images/tutorial/survey_closed_polygonal.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

### Transforma????o conforme 2D
A transforma????o Conforme, tamb??m conhecida como transforma????o de similaridade de quatro par??metros ou Helmert 2D, tem a caracter??stica de manter a forma (configura????o) verdadeira da fei????o ap??s a transforma????o.</br>?? normalmente utilizada para o correto georreferenciamento de levantamentos topogr??ficos com coordenadas arbitr??rias.</br>Esta transforma????o envolve: Escala, Rota????o e Transla????o.</br>
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="images/tutorial/survey_helmert2D.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

### Transforma????o para SGL
Este algoritmo transforma coordenadas entre os seguintes sistemas de refer??ncia:</br>- Geod??sico <b>(??, ??, h)</b></br>- Geoc??ntrico ou ECEF <b>(X, Y, Z)</b>;</br>- Topoc??ntrico <b>(E, N, U)</b>.</br>Default: coordenadas de origem para Recife-PE, Brasil.
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="images/tutorial/survey_SGL_coord.jpg"></td>
    </tr>
  </tbody>
</table>
</div>



## Cartografia


### Coordenadas para moldura UTM
Este algoritmo retorna o pol??gono correspondente ?? <b>moldura</b> relativa a uma escala do <b>Mapeamento Sistem??tico Brasileiro</b>. Esta moldura ?? calculada a partir das coordenadas de um <b>Ponto</b> definido pelo usu??rio.
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="images/tutorial/grid_coord_utm.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

### Extens??o para molduras UTM
Este algoritmo retorna os pol??gonos correspondentes ??s molduras relacionadas a uma escala do Mapeamento Sistem??tico Brasileiro para uma extens??o espec??fica definida pelo usu??rio.
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="images/tutorial/grid_ext_utm.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

### Nome para moldura UTM
Este algoritmo retorna o pol??gono correspondente ?? <b>moldura</b> relativa a uma escala do <b>Mapeamento Sistem??tico Brasileiro</b>. Esta moldura ?? calculada a partir do ??ndice de Nomenclatura <b>INOM</b> ou Mapa ??ndice <b>MI</b> v??lido, que deve ser dado pelo usu??rio.
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="images/tutorial/grid_inom_utm.jpg"></td>
    </tr>
  </tbody>
</table>
</div>



## Documentos


### Memorial descritivo
Elabora????o de Memorial Descritivo a partir de camadas vetorias que definem uma propriedade.
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="images/tutorial/doc_descriptive_memorial.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

### Memorial sint??tico
Esta ferramenta gera a Tabela Descriva de V??rtices e Lados, tamb??m conhecida como Memorial Descritivo Sint??tico, a partir de uma camada de pontos com os atributos de c??digo e ordem (sequ??ncia) dos pontos.
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="images/tutorial/doc_descriptive_table.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

### Monografia de marco geod??sico
Esta ferramenta gera monografia(s) de marcos geod??sicos de forma autom??tica a partir da camada "reference_point_p".
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="images/tutorial/doc_mark.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

### Planilha de ??rea e per??metro
Esta gera o Relat??rio de C??lculo Anal??tico de ??rea, Azimutes, Lados, Coordenadas Planas e Geod??sicas de um Im??vel.
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="images/tutorial/doc_analytical_results.jpg"></td>
    </tr>
  </tbody>
</table>
</div>



## Estat??stica Espacial


### Elipses de confian??a
Cria elipses a partir da matriz vari??ncia-covari??ncia para resumir as caracter??sticas espaciais de fe????es geogr??ficas do tipo ponto: tend??ncia central, dispers??o e tend??ncias direcionais.
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="images/tutorial/stat_ellipses.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

### Pontos aleat??rios gaussiano
Gera pontos aleat??rios no espa??o 2D a partir de um ponto central (X0, Y0), desvios-padr??es para X e Y, e ??ngulo de rota????o.
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="images/tutorial/stat_random_points.jpg"></td>
    </tr>
  </tbody>
</table>
</div>



## M??o na Roda


### Medir camadas
Esta ferramenta calcula em campos virtuais os comprimentos de fei????es do tipo linha e o per??metro e ??rea de fei????es do tipo pol??gono para todas as camadas.
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="images/tutorial/easy_measure_layer.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

### Planilha para camada de pontos
Gera????o de uma camada de pontos a partir das coordenadas preenchidas em uma planilha do Excel (.xls) ou Open Document Spreadsheet (.ods), ou at?? mesmo, a partir dos atributos de outra camada.
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="images/tutorial/easy_coord_layer.jpg"></td>
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
      <td><img src="images/tutorial/post_backup.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

### Clonar BD
Esta ferramenta permite clonar qualquer banco PostgreSQL. A partir de um banco de dados modelo, ?? gerado um outro banco exatamente igual (esquema e inst??ncias) com um novo nome definido pelo operador.</br>Obs.: Para cria????o de mais de um "clone", os novos nomes dos bancos devem ser inseridos "separados por v??rgula".
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="images/tutorial/post_clonedb.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

### Deletar BD
Esta ferramenta permite apagar (delete/drop) qualquer banco do PostgreSQL.</br>Obs.:</br>- Para realizar esta opera????o, ?? necess??rio que o banco esteja desconectado, ou seja, n??o esteja aberto em nenhum software (PgAdmin, QGIS, etc).</br>- Para deletar mais de um BD, os nomes devem ser preenchidos separados por v??rgula.</br><p style="color:red;">Aten????o: Esta opera????o ?? irrevers??vel, portanto esteja seguro quando for execut??-la!</p>
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="images/tutorial/post_deletedb.jpg"></td>
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
      <td><img src="images/tutorial/post_importraster.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

### Renomear BD
Esta ferramenta permite renomear um banco de dados do PostgreSQL.</br>Nota: Para realizar esta opera????o, ?? necess??rio que o banco de dados esteja desconectado, ou seja, n??o esteja aberto em nenhum software (PgAdmin, QGIS, etc.).
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="images/tutorial/post_renamedb.jpg"></td>
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
      <td><img src="images/tutorial/post_restore.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

### Trocar codifica????o de SQL
Esta ferramenta realiza a troca do tipo de codifica????o de um arquivo <b>.sql</b>. Um novo arquivo ser?? criado com a codifica????o definida pelo usu??rio.</br>Em alguns casos, esse processo ?? uma poss??vel solu????o para transferir dados entre diferentes sistemas operacionais, por exemplo de Window para Linux, e vice-versa.
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="images/tutorial/post_encoding.jpg"></td>
    </tr>
  </tbody>
</table>
</div>



## Raster


### Carregar raster pela localiza????o
Carrega um conjunto de arquivos raster que interseptam as geometrias de uma camada vetorial de entrada.
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="images/tutorial/raster_loadByLocation.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

### Classifica????o supervisionada
Realize a classifica????o supervisionada de camada raster com duas ou mais bandas.
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="images/tutorial/raster_classification.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

### Composi????o RGB
Realiza a combina????o de tr??s bandas em uma ??nica imagem, apresentando-as nas bandas vermelha (R), verde (G) e Azul (B).
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="images/tutorial/raster_rgb.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

### Compress??o JPEG
A compress??o JPEG ?? um m??todo "com perdas" para reduzir o tamanho de um arquivo raster (para aproximadamente 10%). O grau de compress??o pode ser ajustado, permitindo um limiar entre o tamanho de armazenamento e a qualidade da imagem.
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="images/tutorial/raster_jpeg_compress.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

### Definir pixel nulo
As c??lulas do raster com valores fora do intervalo (m??nimo e m??ximo) s??o definidas como valor nulo.
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="images/tutorial/raster_define_null_px.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

### Esburacar raster
Cria buracos em Raster definindo pixels nulos (transparentes) a partir de Camada de Pol??gonos.
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="images/tutorial/raster_create_holes.jpg"></td>
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
      <td><img src="images/tutorial/raster_extract_band.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

### Invent??rio de dados raster
Cria uma camada vetorial com o invent??rio de arquivos raster de uma pasta. O tipo de geometria das fei????es dessa camada pode ser Pol??gono (ret??ngulo envolvente) ou Ponto (centroide).
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="images/tutorial/raster_inventory.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

### Limiariza????o Bin??ria
Cria um raster binarizado, dividindo o raster de entrada em duas classes distintas a partir de dados estat??sticos (limiar inferior e superior) de amostras de ??reas.</br>Uma classe ir?? corresponder aos valores compreendidos dentro do intervalo dos limiares, sendo retornado o valor 1 (verdadeiro). J?? a outra classe correpondem aos valores fora do intervalo, sendo retornado o valor 0 (falso).
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="images/tutorial/raster_thresholding.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

### Mosaicar raster
Cria um mosaico: uma combina????o ou mesclagem de duas ou mais imagens.
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="images/tutorial/raster_mosaic.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

### Reescalonar para 8 bits
Reescalona os valores dos pixels de raster com resolu????o radiom??trica de 16 bits (ou at?? mesmo 8 bits ou float) para exatamente o intervalo de 0 a 255, criando um novo raster com 8 bits (byte) de resolu????o radiom??trica.
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="images/tutorial/raster_histogram.jpg"></td>
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
      <td><img src="images/tutorial/raster_fill_holes.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

### Remover banda alfa
Esta ferramenta remove a 4?? banda (banda alfa), transferindo a informa????o de transpar??ncia como "Sem Valor" para os pixels da imagem RGB de sa??da.
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="images/tutorial/raster_remove_alpha.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

### Salvar como JPEG
Exporta qualquer camada raster RGB ou RGBA de 8 bits como um arquivo JPEG. Ideal para reduzir o tamanho do arquivo de sa??da. Realiza a compress??o JPEG com uma pequena perda de qualidade que, em geral, passa despercebida visualmente.
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="images/tutorial/raster_jpeg_tfw.jpg"></td>
    </tr>
  </tbody>
</table>
</div>



## Reambula????o


### Fotos com geotag
Importa fotos com geotag para uma camada de pontos.
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="images/tutorial/reamb_geotag.jpg"></td>
    </tr>
  </tbody>
</table>
</div>



## Vetor


### Calcular ??ngulos de pol??gono
Este algoritmo calcula os ??ngulos internos e externos dos v??rtices de uma camada de pol??gonos. A camada de pontos de sa??da tem os ??ngulos calculados armazenados em sua tabela de atributos.
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="images/tutorial/vect_polygon_angles.jpg"></td>
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
      <td><img src="images/tutorial/vect_extend_lines.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

### Inverter ordem dos v??rtices
Inverte a ordem dos v??rtices para pol??gonos e linhas.
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="images/tutorial/vect_reverse_vertex_sequence.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

### Mesclar linhas na dire????o
Este algoritmo mescla linhas que se tocam nos seus pontos inicial ou final e tem a mesma dire????o (dada uma toler??ncia em graus).<p>Para os atributos pode ser considerado:</p><li>1 - mesclar linhas que tenham os mesmos atributos; ou</li><li>2 - manter os atributos da linha maior.</li>
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="images/tutorial/vect_directional_merge.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

### Sequenciar pontos
Este script preenche um determinado atributo das fei????es de uma camada de pontos de acordo com sua sequ??ncia em rela????o ao pol??gono de outra camada.
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="images/tutorial/vect_sequence_points.jpg"></td>
    </tr>
  </tbody>
</table>
</div>


