
 
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
        <li><a href="#coordinates-to-utm-grid">Coordinates to UTM Grid</a></li>
      </ul>
      <ul>
        <li><a href="#extent-to-utm-grids">Extent to UTM Grids</a></li>
      </ul>
      <ul>
        <li><a href="#name-to-utm-grid">Name to UTM Grid</a></li>
      </ul>
      </li><li>
      <a href="#documents">Documents</a>
      <ul>
        <li><a href="#area-and-perimeter-report">Area and Perimeter Report</a></li>
      </ul>
      <ul>
        <li><a href="#descriptive-memorial">Descriptive Memorial</a></li>
      </ul>
      <ul>
        <li><a href="#descriptive-table-of-vertices-and-sides">Descriptive table of vertices and sides</a></li>
      </ul>
      <ul>
        <li><a href="#geodetic-landmark-informations">Geodetic Landmark Informations</a></li>
      </ul>
      </li><li>
      <a href="#easy">Easy</a>
      <ul>
        <li><a href="#coordinates-to-layer">Coordinates to Layer</a></li>
      </ul>
      <ul>
        <li><a href="#measure-layers">Measure Layers</a></li>
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
        <li><a href="#import-raster">Import Raster</a></li>
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
        <li><a href="#jpeg-compress">JPEG Compress</a></li>
      </ul>
      <ul>
        <li><a href="#load-raster-by-location">Load Raster by Location</a></li>
      </ul>
      <ul>
        <li><a href="#mosaic-raster">Mosaic raster</a></li>
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
        <li><a href="#rgb-composite">RGB Composite</a></li>
      </ul>
      <ul>
        <li><a href="#supervised-classification">Supervised classification</a></li>
      </ul>
      </li><li>
      <a href="#reambulation">Reambulation</a>
      <ul>
        <li><a href="#photos-with-geotag">Photos with Geotag</a></li>
      </ul>
      </li><li>
      <a href="#spatial-statistics">Spatial Statistics</a>
      <ul>
        <li><a href="#confidence-ellipses">Confidence Ellipses</a></li>
      </ul>
      <ul>
        <li><a href="#gaussian-random-points">Gaussian Random Points</a></li>
      </ul>
      </li><li>
      <a href="#survey">Survey</a>
      <ul>
        <li><a href="#2d-conformal-transformation">2D Conformal Transformation</a></li>
      </ul>
      <ul>
        <li><a href="#azimuth-and-distance">Azimuth and Distance</a></li>
      </ul>
      <ul>
        <li><a href="#closed-polygonal">Closed Polygonal</a></li>
      </ul>
      <ul>
        <li><a href="#estimate-3d-coordinates">Estimate 3D Coordinates</a></li>
      </ul>
      <ul>
        <li><a href="#local-geodetic-system-transform">Local Geodetic System Transform</a></li>
      </ul>
      <ul>
        <li><a href="#traverse-adjustment">Traverse Adjustment</a></li>
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



## Cartography

### Coordinates to UTM Grid
This algorithm returns the polygon correspondent to the frame related to a scale of the Brazilian Mapping System. That frame is calculated from a Point definied by the user.
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="images/tutorial/grid_coord_utm.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

  
### Extent to UTM Grids
This algorithm returns the polygons correspondent to the frames related to a scale of the Brazilian Mapping System from a specific extent definied by the user.
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="images/tutorial/grid_ext_utm.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

### Name to UTM Grid
This algorithm returns the polygon correspondent to the frame related to a scale of the Brazilian Mapping System from name (map index).
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

### Area and Perimeter Report
This tool generate the Report for the Analytical Calculation of Area, Azimuths, Sides, UTM Projected and Geodetic Coordinates of a Property.
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="images/tutorial/doc_analytical_results.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

### Descriptive Memorial
Elaboration of Descriptive Memorials based on vector layers that define a property.
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="images/tutorial/doc_descriptive_memorial.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

### Descriptive table of vertices and sides
This tool generates the Descriptive Table of Vertices and Sides, also known as Synthetic Descriptive Memorial, from a layer of points with the attributes of code and order (sequence) of the points.
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="images/tutorial/doc_descriptive_table.jpg"></td>
    </tr>
  </tbody>
</table>
</div>


### Geodetic Landmark Informations
This tool generates monograph(s) of geodetic landmarks automatically from the "pto_ref_geod_topo_p" layer.
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="images/tutorial/doc_mark.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

## Easy

### Coordinates to Layer
Generates a point layer from a coordinate table, whether it comes from a Microsoft Excel spreadsheet, Open Document Spreadsheet (ODS), or even attributes from another layer.
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="images/tutorial/easy_coord_layer.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

### Measure Layers
This tool calculates in virtual fields the lengths of features of the line type and the perimeter and area of features of the polygon type for all layers.
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="images/tutorial/easy_measure_layer.jpg"></td>
    </tr>
  </tbody>
</table>
</div>


## PostGIS

### Backup database
This tool creates a backup file in the ".sql" format for a PostgreSQL server database.
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
This tool changes the encoding type of a .sql file. A new file will be created with the user-defined encoding.
In some cases, this process is necessary to make it possible to transfer data between different operating systems, for example from Window to Linux, and vice versa.
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
This tool allows you to clone any PostgreSQL database. From a model database, another database that is exactly the same (schema and instances) is generated with a new name defined by the operator.
Note: To create more than one "clone", the new bank names must be filled in separated by a "comma".
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
This tool allows you to delete / drop any PostgreSQL database.
Notes:
- To perform this operation, it is necessary that the database is disconnected, that is, it is not open in any software (PgAdmin, QGIS, etc.).
- To delete more than one database, the names must be filled in separated by a "comma".
Attention: This operation is irreversible, so be sure when performing it!
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="images/tutorial/post_deletedb.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

### Import Raster
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
This tool allows you to rename a PostgreSQL database.
Note: To perform this operation, it is necessary that the database is disconnected, that is, it is not open in any software (PgAdmin, QGIS, etc.).
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
This tool allows you to restore, that is, import a database on a PostgreSQL server, from a backup file in the ".sql" format.
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


### JPEG Compress
JPEG compression is a lossy method to reduce the raster file size (about to 10%). The degree of compression can be adjusted, allowing a selectable tradeoff between storage size and image quality.
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="images/tutorial/raster_jpeg_compress.jpg"></td>
    </tr>
  </tbody>
</table>
</div>


### Load Raster by Location
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


### RGB Composite
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

### Photos with Geotag
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

### Confidence Ellipses
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


### Gaussian Random Points
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

### 2D Conformal Transformation
Two-dimensional conformal coordinate transformation, also known as the four-parameter similarity transformation or Helmert 2D, has the characteristic that true shape is retained after transformation.
It is typically used in surveying when converting separate surveys into a common reference coordinate system.
This transformation involves: Scaling, Rotation and Translations.
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="images/tutorial/survey_helmert2D.jpg"></td>
    </tr>
  </tbody>
</table>
</div>

### Azimuth and Distance
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


### Closed Polygonal
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


### Estimate 3D Coordinates
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


### Local Geodetic System Transform
This algorithm transforms coordinates between the following reference systems:
- geodetic (λ, ϕ, h);
- geocentric or ECEF (X, Y, Z); and
- topocentric in a local tangent plane (E, N, U).
Default values for origin coordinates can be applied to Recife / Brazil.
<div align="center">
<table style="text-align: left; width: 275px;" border="0" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td><img src="images/tutorial/survey_SGL_coord.jpg"></td>
    </tr>
  </tbody>
</table>
</div>


### Traverse Adjustment
This algorithm performs the traverse adjustments of a framed polygonal by least squares method, where the distances, angles, and directions observations are adjusted simultaneously, providing the most probable values for the given data set. Futhermore, the observations can be rigorously weighted based on their estimated errors and adjusted accordingly.
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
Extends lines at their start and/or end points.
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
This algorithm merges lines that touch at their starting or ending points and has the same direction (given a tolerance in degrees). 
For the attributes can be considered:
1 - merge lines that have the same attributes; or
2 - keep the attributes of the longest line.
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

