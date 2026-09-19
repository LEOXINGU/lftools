# -*- coding: utf-8 -*-

dic = {
'Elaboration of Deed Description based on vector layers that define a property survey.': {'es': 'Elaboración de la Descripción de la Escritura basada en capas vectoriales que definen un levantamiento de la propiedad.'},
'This tool works properly only with data in "TopoGeo" modeling.': {'es': 'Esta herramienta funciona correctamente sólo con datos en el modelado "TopoGeo".'},
'Click here for understanding more about this data model.': {'es': 'Haga clic aquí para comprender este modelo de datos.'},
'Deed description': {'es': 'Descripción de Escritura'},
'Documents': {'es': 'Documentación'},
'Author: Leandro Franca': {'es': 'Autor: Leandro Franca'},
'Boundary Survey Points': {'es': 'Puntos de levantamiento de límites'},
'Neighborhood Dividing Lines': {'es': 'Líneas divisorias'},
'Property Polygon': {'es': 'Polígono de la propiedad'},
' without suffix': {'es': ' sin sufijo'},
'Coordinates': {'es': 'Coordenadas'},
'Project CRS, area in m²': {'es': 'Proyecto CRS, área en m²'},
'Project CRS, area in ha': {'es': 'Proyecto CRS, área en ha'},
'Local Tangent Plane (LTP), area in m²': {'es': 'Plano tangente local (LTP), área en m²'},
'Local Tangent Plane (LTP), area in ha': {'es': 'Plano tangente local (LTP), área en ha'},
'LTP, Puissant azimuth, area in m²': {'es': 'LTP, azimut de Puissant, área en m²'},
'LTP, Puissant azimuth, area in ha': {'es': 'LTP, azimut de Puissant, área en ha'},
'Logo (JPEG)': {'es': 'Logotipo (JPEG)'},
'CARTOGRAPHY & SURVEYING': {'es': 'CARTOGRAFÍA Y TOPOGRAFÍA'},
'Decimal places': {'es': 'Posiciones decimales'},
'Verify map projection': {'es': 'Verificar proyección cartográfica'},
'Verify attributes': {'es': 'Verificar atributos'},
'Verify topology': {'es': 'Verificar topología'},
'HTML files (*.html)': {'es': 'Archivos HTML (*.html)'},
'Database in the TopoGeo model...': {'es': 'Base de datos en el modelo TopoGeo...'},
'Check that your layers have the correct field names for the TopoGeo model! More information: https://bit.ly/3FDNQGC': {'es': '¡Compruebe que sus capas tengan los nombres de campo correctos para el modelo TopoGeo! Más información: https://bit.ly/3FDNQGC'},
'Input coordinates must be geodetic (longitude and latitude)!': {'es': '¡Las coordenadas de entrada deben ser geodésicas (longitud y latitud)!'},
'Validating layer attributes...': {'es': 'Validando los atributos de la capa...'},
'The code attribute must be filled in for all features!': {'es': '¡El atributo de código debe estar lleno para todas las entidades!'},
'The point sequence field must be filled in correctly!': {'es': '¡El campo de secuencia de puntos debe estar lleno correctamente!'},
'Validating topology of geometries...': {'es': 'Validando topología de geometrías...'},
'Sequencing "boundary_element_l" features...': {'es': 'Secuenciando entidades "boundary_element_l"...'},
'The Project CRS must be projected!': {'es': '¡El Proyecto CRS debe ser proyectado!'},
'Project CRS is {}.': {'es': 'El proyecto CRS es {}.'},
'The number of points must be greater than 2!': {'es': '¡El número de puntos debe ser mayor que 2!'},
'Limit Point layer must be "PointZ" type!': {'es': '¡La capa de punto límite debe ser del tipo "PointZ"!'},
'The attribute {} of the polygon layer must be filled!': {'es': '¡El atributo {} de la capa de polígono debe estar lleno!'},
'and': {'es': 'y'},
'Descriptive memorial': {'es': 'Memorial descriptivo'},
'DESCRIPTIVE MEMORIAL': {'es': 'MEMORIAL DESCRIPTIVO'},
'Property': {'es': 'Propiedad'},
'Real estate registry': {'es': 'registro de bienes raices'},
'Owner': {'es': 'Dueño'},
'County': {'es': 'Condado'},
'State': {'es': 'Estado'},
'Registration(s)': {'es': 'Registro(s)'},
'Area ({})': {'es': 'Área ({})'},
'Perimeter': {'es': 'Perímetro'},
'Coordinate Reference System': {'es': 'Sistema de referencia de coordenadas'},
'The description of this perimeter begins ': {'es': 'La descripción de este perímetro comienza'},
'at the vertex ': {'es': 'en el vértice '},
'the vertex ': {'es': 'el vértice '},
'PROPERTY OWNER': {'es': 'PROPIETARIO'},
'TECHNICAL MANAGER': {'es': 'GERENTE TÉCNICO'},
'Operation completed successfully!': {'es': '¡La operación se realizó con éxito!'},
'Leandro França - Cartographic Engineer': {'es': 'Leandro França - Ingeniero Cartográfico'},
'Coordinate point ({}, {}) of the "boundary_element_l" layer has no correspondent in the "limit_point_p" layer!': {'es': '¡El punto de coordenadas ({}, {}) de la capa "boundary_element_l" no tiene correspondencia en la capa "limit_point_p"!'},
'Coordinate point ({}, {}) of the "property_area_a" layer has no correspondent in the "limit_point_p" layer!': {'es': '¡El punto de coordenadas ({}, {}) de la capa "property_area_a" no tiene correspondencia en la capa "limit_point_p"!'},
'Coordinate point ({}, {}) of the "limit_point_p" layer has no correspondent in the "boundary_element_l" layer!': {'es': '¡El punto de coordenadas ({}, {}) de la capa "limit_point_p" no tiene correspondencia en la capa "boundary_element_l"!'},
'Coordinate point ({}, {}) of the "limit_point_p" layer is duplicated!': {'es': '¡El punto de coordenadas ({}, {}) de la capa "limit_point_p" está duplicado!'},
'Coordinate point ({}, {}) of the "boundary_element_l" layer is duplicated!': {'es': '¡El punto de coordenadas ({}, {}) de la capa "boundary_element_l" está duplicado!'},
'Coordinate point ({}, {}) of the "property_area_a" layer is duplicated!': {'es': '¡El punto de coordenadas ({}, {}) de la capa "property_area_a" está duplicado!'},
'The first point of the limit_point_p layer must coincide with the first vertex of a line of the boundary_element_l layer!': {'es': '¡El primer punto de la capa limit_point_p debe coincidir con el primer vértice de una línea de la capa border_element_l!'},
'All lines must be sequenced with a consistent orientation, either clockwise or counterclockwise. Check coordinate point ({}, {})!': {'es': 'Todas las lineas deben estar secuenciadas manteniendo la misma orientacion, ya sea en sentido horario o antihorario ¡Verificar el punto de coordenadas ({}, {})!'},
'Warning: Make sure your projection is correct!': {'es': 'Advertencia: ¡Asegúrese de que su proyección sea correcta!'},
'with coordinates ': {'es': 'con coordenadas '},
'from this, it continues to confront [Confront_k], with the following flat azimuths and distances: [Az_n] and [Dist_n]m up to ': {'es': 'a partir de esto, continúa enfrentando [Confront_k], con los siguientes azimuts planos y distancias: [Az_n] y [Dist_n]m hasta '},
', and are projected in the UTM system, zone [FUSO] and hemisphere [HEMISFERIO], from which all azimuths and distances, area and perimeter were calculated.': {'es': ', y están proyectados en el sistema UTM, zona [FUSO] y hemisferio [HEMISFERIO], a partir del cual se calcularon todos los acimutes y distancias, área y perímetro.'},
', and are projected in the UTM system, zone [FUSO] and hemisphere [HEMISFERIO]. All azimuths and distances, area and perimeter were calculated in the Local Tangent Plane (LTP), having as origin the centroid and average altitude of the property survey.': {'es': ', y se proyectan en el sistema UTM, zona [FUSO] y hemisferio [HEMISFERIO]. Todos los acimutes y distancias, área y perímetro se calcularon en el Plano Tangente Local (LTP), teniendo como origen el centroide y la altitud media del levantamiento de la propiedad.'},
'. All azimuths and distances, area and perimeter were calculated from the projected coordinates in UTM, zone [FUSO] and hemisphere [HEMISPHERE].': {'es': '. Todos los acimutes y distancias, área y perímetro se calcularon a partir de las coordenadas proyectadas en UTM, zona [FUSO] y hemisferio [HEMISFERIO].'},
'. All azimuths and distances, area and perimeter were calculated in the Local Tangent Plane (LTP), having as origin the centroid and average altitude of the property survey.': {'es': '. Todos los acimutes y distancias, área y perímetro se calcularon en el Plano Tangente Local (LTP), teniendo como origen el centroide y la altitud media del levantamiento de la propiedad.'},
', and are projected in the UTM system, zone [FUSO] and hemisphere [HEMISFERIO]. The azimuths were calculated using the Inverse Geodetic Problem formula according to Puissant. The distances, area and perimeter were calculated in the Local Tangent Plane (LTP), having as origin the centroid and average altitude of the property survey.': {'es': '. Todos los acimutes y distancias, área y perímetro se calcularon en el Plano Tangente Local (LTP), teniendo como origen el centroide y la altitud media del levantamiento de la propiedad.'},
'. The azimuths were calculated using the Inverse Geodetic Problem formula according to Puissant. The distances, area and perimeter were calculated in the Local Tangent Plane (LTP), having as origin the centroid and average altitude of the property survey.': {'es': '. Los acimutes se calcularon utilizando la fórmula del Problema Geodésico Inverso según Puissant. Las distancias, área y perímetro se calcularon en el Plano Tangente Local (LTP), teniendo como origen el centroide y la altitud promedio del levantamiento de la propiedad.'},
'the starting point for the description of this perimeter. All coordinates described here are georeferenced to the Geodetic Reference System (GRS)': {'es': 'el punto de partida para la descripción de este perímetro. Todas las coordenadas descritas aquí están georreferenciadas al Sistema de Referencia Geodésica (GRS)'},
'janeiro': {'es': 'Enero'},
'fevereiro': {'es': 'Febrero'},
'março': {'es': 'Marzo'},
'abril': {'es': 'Abril'},
'maio': {'es': 'Mayo'},
'junho': {'es': 'Junio'},
'julho': {'es': 'Julio'},
'agosto': {'es': 'Agosto'},
'setembro': {'es': 'Septiembre'},
'outubro': {'es': 'Octubre'},
'novembro': {'es': 'Noviembre'},
'dezembro': {'es': 'Diciembre'},
'Parcel Boundary Lines' : {'es': 'Líneas de Adyacentes '},
'Cadastre' : {'es': 'Catastro'},
'Parcels' : {'es': 'Parcelas '},
'Adjoiners' : {'es': 'Adyacentes'},
'Feature id {} is multipart! Multipart features are not allowed!' : {'es': '¡La entidade con ID {} es multipart! ¡No se permiten entidades multipart! '},
'Creating spatial index...' : {'es': 'Creando índice espacial...'},
'Identifying adjoining lines...' : {'es': 'Identificando líneas contiguas...'},
'Creating new layer...' : {'es': 'Creando nueva capa...'},
'Leandro Franca - Cartographic Engineer' : {'es': 'Leandro Franca - Ingeniero Cartográfico'},
'Connect features' : {'es': 'Funciones de conexión'},
'Tolerance for snapping in meters' : {'es': 'Tolerancia al rompimiento en metros'},
'Connected parcels' : {'es': 'Paquetes conectados'},
'Invalid tolerance!' : {'es': '¡Tolerancia inválida!'},
'Checking and fixing connectivity...' : {'es': 'Comprobando y arreglando la conectividad...'},
'Front Lot Lines' : {'es': 'Líneas frontales del lote'},
'Northmost' : {'es': 'más al norte'},
'Southernmost' : {'es': 'Más meridional'},
'Eastmost' : {'es': 'más al este'},
'Westmost' : {'es': 'Más al oeste'},
'Start' : {'es': 'Comenzar'},
'sequence' : {'es': 'secuencia'},
'lenght' : {'es': 'largo'},
'cumulative' : {'es': 'acumulativo'},
'Defining set of parcels (blocks)...' : {'es': 'Definiendo conjunto de parcelas (bloques)...'},
'Orienting polygon (clockwise)...' : {'es': 'Polígono de orientación (en el sentido de las agujas del reloj)...'},
'Calculating front lot lines...' : {'es': 'Calculando líneas de frente de lote...'},
'Sequencing and saving front lot lines...' : {'es': 'Secuenciar y guardar líneas de lote frontal...'},
'Check if the input layer topology is correct!' : {'es': '¡Compruebe si la topología de la capa de entrada es correcta!'},
'Geographic Numbering' : {'es': 'Numeración geográfica'},
'Points' : {'es': 'Puntos'},
'Only selected' : {'es': 'Sólo seleccionado'},
'Sequence Field' : {'es': 'Campo de secuencia'},
'Group Field' : {'es': 'Campo de grupo'},
'North to South, West to East' : {'es': 'De norte a sur, de oeste a este'},
'North to South, East to West' : {'es': 'De norte a sur, de este a oeste'},
'West to East, North to South' : {'es': 'De oeste a este, de norte a sur'},
'West to East, South to North' : {'es': 'De oeste a este, de sur a norte'},
'South to North, West to East' : {'es': 'De sur a norte, de oeste a este'},
'South to North, East to West' : {'es': 'De sur a norte, de este a oeste'},
'East to West, North to South' : {'es': 'De este a oeste, de norte a sur'},
'East to West, South to North' : {'es': 'De este a oeste, de sur a norte'},
'Method' : {'es': 'Método'},
'Initial count' : {'es': 'Recuento inicial'},
'Save Editions' : {'es': 'Guardar ediciones'},
'Reading features...' : {'es': 'Funciones de lectura...'},
'Sorting the features...' : {'es': 'Ordenando las entidades...'},
'Orient polygons' : {'es': 'Orientar polígonos'},
'Polygon layer' : {'es': 'capa de polígono'},
'Clockwise' : {'es': 'Agujas del reloj'},
'Counterclockwise' : {'es': 'En sentido anti-horario'},
'Do not change' : {'es': 'No cambies'},
'Orientation' : {'es': 'Orientación'},
'Polygon sequence (do not change)' : {'es': 'Secuencia de polígonos (no cambiar)'},
'First point' : {'es': 'Primer punto'},
'First vertex with forefront bordering the street' : {'es': 'Primer vértice con frente lindando con la calle.'},
'Orienting polygons...' : {'es': 'Orientando polígonos...'},
'Identifying the first forward point for road access...' : {'es': 'Identificando el primer punto de avance para el acceso por carretera...'},
'Coordinates to UTM grid' : {'es': 'Coordenadas de la cuadrícula UTM'},
'Cartography' : {'es': 'Cartografía'},
'Point' : {'es': 'Punto'},
'Scale' : {'es': 'Escala'},
'Grid CRS' : {'es': 'SRC de rejilla'},
'UTM Grid' : {'es': 'Cuadrícula UTM'},
'Invalid Latitude' : {'es': 'Latitud no válida'},
'Invalid Longitude' : {'es': 'Longitud no válida'},
'scale' : {'es': 'escala'},
'Nomenclature Index' : {'es': 'Índice de nomenclatura'},
'Map Index' : {'es': 'Índice de mapas'},
'Extent to UTM grids' : {'es': 'Extensión a cuadrículas UTM'},
'Source:' : {'es': 'Fuente:'},
'Extent' : {'es': 'Medida'},
'Calculate Chart Size (Height and Width)' : {'es': 'Calcular el tamaño del gráfico (alto y ancho)'},
'Calculate Meridian Convergence (MC)' : {'es': 'Calcular la convergencia de meridianos (MC)'},
'Calculate Magnetic Declination (MD)' : {'es': 'Calcular la declinación magnética (MD)'},
'Calculate Zone and Hemisphere' : {'es': 'Calcular zona y hemisferio'},
'UTM Grids' : {'es': 'Cuadrículas UTM'},
'chart_name' : {'es': 'nombre_del_gráfico'},
'height' : {'es': 'altura'},
'width' : {'es': 'ancho'},
'Epoch' : {'es': 'Época'},
'zone_hemisphere' : {'es': 'zona_hemisferio'},
'Frames from lines' : {'es': 'Marcos de líneas'},
'Line layer' : {'es': 'capa de línea'},
'Longitudinal distance in meters' : {'es': 'Distancia longitudinal en metros'},
'Transverse distance in meters' : {'es': 'Distancia transversal en metros'},
'Overlap between frames (%)' : {'es': 'Superposición entre fotogramas (%)'},
'Number of frames per page' : {'es': 'Número de fotogramas por página'},
'Frames' : {'es': 'Marcos'},
'page' : {'es': 'página'},
'Name to UTM grid' : {'es': 'Nombre a la grilla UTM'},
'Name' : {'es': 'Nombre'},
'Type' : {'es': 'Tipo'},
'Origin' : {'es': 'Origen'},
'Area and perimeter report' : {'es': 'Informe de área y perímetro'},
'Project CRS' : {'es': 'Proyecto CRS'},
'Local Tangent Plane (LTP)' : {'es': 'Plano tangente local (LTP)'},
'LTP, Puissant azimuth' : {'es': 'LTP, azimut potente'},
'Slogan' : {'es': 'Eslogan'},
'Analytical Calculation Results' : {'es': 'Resultados del cálculo analítico'},
'All attributes of the class "property_polygon" must be filled!' : {'es': '¡Se deben completar todos los atributos de la clase "property_polygon"!'},
'Area and Perimeter Calculation' : {'es': 'Cálculo de área y perímetro'},
'County-State' : {'es': 'Condado-Estado'},
'GRS' : {'es': 'GRS'},
'Projection' : {'es': 'Proyección'},
'Station' : {'es': 'Estación'},
'Forward' : {'es': 'Adelante'},
'East (m)' : {'es': 'Este (m)'},
'North (m)' : {'es': 'Norte (m)'},
'Azimuth' : {'es': 'Azimut'},
'Distance (m)' : {'es': 'Distancia (m)'},
'Longitude' : {'es': 'Longitud'},
'Latitude' : {'es': 'Latitud'},
'Total Area' : {'es': 'Área total'},
'Observation' : {'es': 'Observación'},
'Synthetic deed description' : {'es': 'Descripción de escritura sintética'},
'First vertex' : {'es': 'Primer vértice'},
'Last vertex' : {'es': 'último vértice'},
'Title' : {'es': 'Título'},
'Font size' : {'es': 'Tamaño de fuente'},
'Planimetric (E,N)' : {'es': 'Planimétrico (E,N)'},
'Planimetric (N,E)' : {'es': 'Planimétrico (N,E)'},
'Model' : {'es': 'Modelo'},
'Layer in the TopoGeo model...' : {'es': 'Capa en el modelo TopoGeo...'},
'LTP ' : {'es': 'LTP '},
'LTP' : {'es': 'LTP'},
'FLAT' : {'es': 'PLANA'},
'VERTEX' : {'es': 'VÉRTICE'},
'COORDINATE' : {'es': 'COORDINAR'},
'SIDE' : {'es': 'LADO'},
'AZIMUTH' : {'es': 'AZIMUT'},
'DISTANCE' : {'es': 'DISTANCIA'},
'TRUE' : {'es': 'VERDADERO'},
'Geodetic mark report' : {'es': 'Informe de marcas geodésicas'},
'Survey Landmark' : {'es': 'Punto de referencia de la encuesta'},
'Code' : {'es': 'Código'},
'Geodetic Landmark Report' : {'es': 'Informe de hito geodésico'},
'The survey mark code {} is not valid!' : {'es': '¡El código de marca de encuesta {} no es válido!'},
'The attributes of the class "reference_point_p" must be filled!' : {'es': '¡Los atributos de la clase "reference_point_p" deben estar completos!'},
'Monograph of Geodetic Landmark' : {'es': 'Monografía de hito geodésico'},
'MONOGRAPH OF GEODETIC LANDMARK' : {'es': 'MONOGRAFÍA DE HITO GEODÉSICO'},
'CODE' : {'es': 'CÓDIGO'},
'TYPE' : {'es': 'TIPO'},
'PROPERTY' : {'es': 'PROPIEDAD'},
'COUNTY' : {'es': 'CONDADO'},
'STATE' : {'es': 'ESTADO'},
'Description/Location:' : {'es': 'Descripción/Ubicación:'},
'GEODESIC COORDINATES' : {'es': 'COORDENADAS GEODÉSICAS'},
'FLAT COORDINATES (UTM)' : {'es': 'COORDENADAS PLANAS (UTM)'},
'PRECISIONS (m)' : {'es': 'PRECISIONES (m)'},
'East' : {'es': 'Este'},
'North' : {'es': 'Norte'},
'Elipsoidal Altitude' : {'es': 'Altitud elipsoidal'},
'CM' : {'es': 'CM'},
'Orthometric Altitude' : {'es': 'Altitud ortométrica'},
'EQUIPMENT' : {'es': 'EQUIPO'},
'STEP' : {'es': 'PASO'},
'DATE' : {'es': 'FECHA'},
'RESPONSIBLE' : {'es': 'RESPONSABLE'},
'METHOD' : {'es': 'MÉTODO'},
'Surveying' : {'es': 'topografía'},
'REF. BASE(S)' : {'es': 'ÁRBITRO. BASES'},
'Processing' : {'es': 'Procesando'},
'Monograph' : {'es': 'Monografía'},
'LANDMARK PHOTO' : {'es': 'FOTO HISTÓRICA'},
'AERIAL IMAGE' : {'es': 'IMAGEN AÉREA'},
'PANORAMIC PHOTO' : {'es': 'FOTO PANORÁMICA'},
'PROFESSION/SPECIALIZATION' : {'es': 'PROFESIÓN/ESPECIALIZACIÓN'},
'PROFESSIONAL REGISTRATION' : {'es': 'REGISTRACION PROFESIONAL'},
'Check that your layer "reference_point_p" has the correct field names for the TopoGeo model! More information: https://bit.ly/3FDNQGC' : {'es': '¡Compruebe que su capa "reference_point_p" tenga los nombres de campo correctos para el modelo TopoGeo! Más información: https://bit.ly/3FDNQGC'},
'Verify if the file {} exists!': {'es': '¡Verifica si el archivo {} existe!'},
'Make sure your file {} is in JPEG format!': {'es': '¡Asegúrate de que tu archivo {} esté en formato JPEG!'},
'Points from Deed Description' : {'es': 'Puntos de la descripción de la escritura'},
'RegEx for Vertex Code' : {'es': 'RegEx para código de vértice'},
'X coordinate RegEx' : {'es': 'Coordenada X RegEx'},
'Text' : {'es': 'Texto'},
'Decimal separator is dot' : {'es': 'El separador decimal es el punto.'},
'Point layer' : {'es': 'capa de puntos'},
'code' : {'es': 'código'},
'Códigos:' : {'es': 'Códigos:'},
'Coordenadas X:' : {'es': 'Coordenadas X:'},
'Coordenadas Y:' : {'es': 'Coordenadas Y:'},
'Error: The number of input values does not match.' : {'es': 'Error: el número de valores de entrada no coincide.'},
'Codes and coordinates' : {'es': 'Códigos y coordenadas'},
'Validate topology' : {'es': 'Validar topología'},
'Vertices (points)' : {'es': 'Vértices (puntos)'},
'Limits (lines)' : {'es': 'Límites (líneas)'},
'Area (polygon)' : {'es': 'Área (polígono)'},
'Topology errors' : {'es': 'Errores de topología'},
'type' : {'es': 'tipo'},
'Checking if each vertex of the Limit layer (line) has the corresponding one of the Vertex layer (point)...' : {'es': 'Comprobando si cada vértice de la capa Límite (línea) tiene el correspondiente de la capa Vértice (punto)...'},
'Checking if each vertex of the Area layer (polygon) has the corresponding one of the Vertex layer (point)...' : {'es': 'Comprobando si cada vértice de la capa Área (polígono) tiene el correspondiente de la capa Vértice (punto)...'},
'Checking if each vertex of the Vertex layer (point) has the corresponding one of the Area layer (polygon)...' : {'es': 'Comprobando si cada vértice de la capa Vértice (punto) tiene el correspondiente de la capa Área (polígono)...'},
'Checking if each vertex of the Vertex layer (point) has the corresponding one of the limit layer (line)...' : {'es': 'Comprobando si cada vértice de la capa Vértice (punto) tiene el correspondiente de la capa límite (línea)...'},
'Checking for duplicate vertices inside the vertex (point) layer...' : {'es': 'Comprobando si hay vértices duplicados dentro de la capa de vértice (punto)...'},
'Checking for duplicate vertices inside the limit (line) layer...' : {'es': 'Comprobando si hay vértices duplicados dentro de la capa de límite (línea)...'},
'Checking for duplicate vertices inside the area (polygon) layer...' : {'es': 'Comprobando si hay vértices duplicados dentro de la capa de área (polígono)...'},
'Checking line layer orientation...' : {'es': 'Comprobando la orientación de la capa de líneas...'},
'Checking for duplicate geometry line layer...' : {'es': 'Comprobando si hay una capa de línea de geometría duplicada...'},
'Checking for duplicate geometry polygon layer...' : {'es': 'Comprobando si hay una capa de polígono de geometría duplicada...'},
'Checking if any vertex has a dimension-Z equal to Zero...' : {'es': 'Comprobando si algún vértice tiene una dimensión Z igual a cero...'},
'Copy selected files' : {'es': 'Copiar archivos seleccionados'},
'Drones' : {'es': 'Drones'},
'Field with file path' : {'es': 'Campo con ruta de archivo'},
'Copy' : {'es': 'Copiar'},
'Move' : {'es': 'Mover'},
'Option' : {'es': 'Opción'},
'Destination folder for photos' : {'es': 'Carpeta de destino para fotos.'},
'At least one feature must be selected!' : {'es': '¡Se debe seleccionar al menos una entidade!'},
'Generate GCP file for WebODM' : {'es': 'Generar archivo GCP para WebODM'},
'Generate GCP file for CloudCompare' : {'es': 'Generar archivo GCP para CloudCompare'},
'Point Layer' : {'es': 'Capa de puntos'},
'GCP name' : {'es': 'nombre de GCP'},
'Ground Control Points (GCP)' : {'es': 'Puntos de control terrestre (GCP)'},
'TXT with Ground Control Points (GCP)' : {'es': 'TXT con puntos de control terrestre (GCP)'},
'Georeferencing Adjustment' : {'es': 'Ajuste de Georreferenciación'},
'Input Raster' : {'es': 'Ráster de entrada'},
'Vectors Lines (two vertices)' : {'es': 'Líneas de vectores (dos vértices)'},
'Translation' : {'es': 'Traducción'},
'Helmert 2D (Conformal)' : {'es': 'Helmert 2D (Conforme)'},
'Afinne' : {'es': 'afinne'},
'Check CRS' : {'es': 'Comprobar CRS'},
'Nearest neighbor' : {'es': 'Vecino más cercano'},
'Bilinear' : {'es': 'bilineal'},
'Bicubic' : {'es': 'bicúbico'},
'Interpolation' : {'es': 'Interpolación'},
'Adjusted Raster' : {'es': 'Ráster ajustado'},
'Load Adjusted Raster' : {'es': 'Carga ráster ajustada'},
'Adjusted Coordinates with precisions' : {'es': 'Coordenadas ajustadas con precisiones.'},
'Adjustment Report' : {'es': 'Informe de ajuste'},
'Calculating adjustment parameters...' : {'es': 'Calculando parámetros de ajuste...'},
'precision_x' : {'es': 'precisión_x'},
'precision_y' : {'es': 'precisión_y'},
'Opening raster file...' : {'es': 'Abriendo archivo ráster...'},
'The raster layer and the homologous point vector layer must have the same CRS!' : {'es': '¡La capa ráster y la capa vectorial de puntos homólogos deben tener el mismo CRS!'},
'Size: ' : {'es': 'Tamaño:'},
'Opening band {} as array...' : {'es': 'Banda de apertura {} como matriz...'},
'Transforming new band {}...' : {'es': 'Transformando nueva banda {}....'},
'Join folders' : {'es': 'Unir carpetas'},
'Folders with files' : {'es': 'Carpetas con archivos'},
'Rename copied files' : {'es': 'Cambiar el nombre de los archivos copiados'},
'File name prefix' : {'es': 'Prefijo de nombre de archivo'},
'Destination folder' : {'es': 'Carpeta de destino'},
'Checking files in the folders...' : {'es': 'Comprobando archivos en las carpetas...'},
'Choose another output folder!' : {'es': '¡Elija otra carpeta de salida!'},
'Overviews with JPEG compression' : {'es': 'Resúmenes con compresión JPEG'},
'RGB Raster' : {'es': 'Ráster RGB'},
'Resampling method' : {'es': 'Método de remuestreo'},
'Factors' : {'es': 'Factores'},
'The image must be RGB with 3 or 4 bands (alpha)!' : {'es': '¡La imagen debe ser RGB con 3 o 4 bandas (alfa)!'},
'Creating the Overviews...' : {'es': 'Creando las descripciones generales...'},
'Photos by blocks' : {'es': 'Fotos por bloques'},
'Blocks' : {'es': 'Bloques'},
'Folder name prefix' : {'es': 'Prefijo del nombre de la carpeta'},
'block_' : {'es': 'bloquear_'},
'Folder with raster files' : {'es': 'Carpeta con archivos rasterizados'},
'Both layers must have the same CRS!' : {'es': '¡Ambas capas deben tener el mismo CRS!'},
'Photos Histogram Matching' : {'es': 'Coincidencia de histograma de fotos'},
'Input photo layer' : {'es': 'Capa de foto de entrada'},
'Layer of reference photos' : {'es': 'Capa de fotos de referencia.'},
'Histogram matching...' : {'es': 'Coincidencia de histograma...'},
'path' : {'es': 'camino'},
'name' : {'es': 'nombre'},
'Point cloud adjustment' : {'es': 'Ajuste de nube de puntos'},
'Point Cloud' : {'es': 'Punto de nube'},
'Vectors Lines (two 3D vertices)' : {'es': 'Líneas de vectores (dos vértices 3D)'},
'Method of horizontal adjustment' : {'es': 'Método de ajuste horizontal.'},
'Constant' : {'es': 'Constante'},
'Plane' : {'es': 'Avión'},
'Method of vertical adjustment' : {'es': 'Método de ajuste vertical.'},
'Adjusted Point Cloud' : {'es': 'Nube de puntos ajustada'},
'Output file path must be filled!' : {'es': '¡Se debe completar la ruta del archivo de salida!'},
'Opening point cloud file...' : {'es': 'Abriendo archivo de nube de puntos...'},
'Total number of points: ' : {'es': 'Número total de puntos:'},
'Calculating horizontal adjustment parameters...' : {'es': 'Calculando los parámetros de ajuste horizontal...'},
'Calculating vertical adjustment parameters...' : {'es': 'Calculando los parámetros de ajuste vertical...'},
'Remove alpha band' : {'es': 'Quitar banda alfa'},
'Input Raster with Alpha Band' : {'es': 'Ráster de entrada con banda alfa'},
'Define null pixel' : {'es': 'Definir píxel nulo'},
'Load output raster' : {'es': 'Cargar ráster de salida'},
'Raster with alpha band removed' : {'es': 'Ráster con banda alfa eliminada'},
'Reading the input raster...' : {'es': 'Leyendo el ráster de entrada...'},
'The input raster must have 4 bands!' : {'es': '¡El ráster de entrada debe tener 4 bandas!'},
'Reading alpha band...' : {'es': 'Leyendo banda alfa...'},
'Raster without alpha band.' : {'es': 'Ráster sin banda alfa.'},
'Save as JPEG' : {'es': 'Guardar como JPEG'},
'Input Raster (3 or 4 bands - 8bit)' : {'es': 'Ráster de entrada (3 o 4 bandas - 8 bits)'},
'Create world file (.jpw)' : {'es': 'Crear archivo mundial (.jpw)'},
'JPEG image' : {'es': 'imagen JPEG'},
'The input raster must have 3 or 4 bands!' : {'es': '¡El ráster de entrada debe tener 3 o 4 bandas!'},
'The raster data type must byte (8bit)!' : {'es': '¡El tipo de datos ráster debe ser de bytes (8 bits)!'},
'Salving as JPEG...' : {'es': 'Guardando como JPEG...'},
'Creating new RGB bands...' : {'es': 'Creando nuevas bandas RGB...'},
'Vertical adjustment' : {'es': 'Ajuste vertical'},
'Digital Elevation Model (DEM)' : {'es': 'Modelo de Elevación Digital (DEM)'},
'Z Coordinate' : {'es': 'Coordenada Z'},
'The DEM raster layer must have only one band!' : {'es': '¡La capa ráster DEM debe tener solo una banda!'},
'The raster layer and the GCP layer must have the same CRS!' : {'es': '¡La capa ráster y la capa GCP deben tener el mismo CRS!'},
'GCP layer': {'es': 'Capa de GCP'},
'Input point layer must have PointZ geometry!': {'es': '¡La capa de puntos de entrada debe tener geometría de tipo PointZ!'},
'Determining values for the adjustment...' : {'es': 'Determinación de valores para el ajuste...'},
'Table to point layer' : {'es': 'Capa de tabla a punto'},
'Easy' : {'es': 'Fácil'},
'Table with coordinates' : {'es': 'Tabla con coordenadas'},
'X Coordinate' : {'es': 'Coordenada X'},
'Y Coordinate' : {'es': 'Coordenada Y'},
'CRS incompatible with input coordinates!' : {'es': '¡CRS incompatible con las coordenadas de entrada!'},
'Export expression as ASCII' : {'es': 'Exportar expresión como ASCII'},
'Input layer' : {'es': 'Capa de entrada'},
'Output file name' : {'es': 'Nombre del archivo de salida'},
'Expression to be written' : {'es': 'Expresión a escribir'},
'Write to single file' : {'es': 'Escribir en un solo archivo'},
'Sort field' : {'es': 'Ordenar campo'},
'Output file format' : {'es': 'Formato de archivo de salida'},
'Leandro França - Eng Cart' : {'es': 'Leandro França - Eng Carrito'},
'Get attribute by location' : {'es': 'Obtener atributo por ubicación'},
'Attribute source layer' : {'es': 'Capa de origen de atributos'},
'Source field' : {'es': 'Campo fuente'},
'Target layer for attribute' : {'es': 'Capa de destino para atributo'},
'Destination field' : {'es': 'Campo de destino'},
'from target feature' : {'es': 'desde la entidade objetivo'},
'from origin feature' : {'es': 'desde la entidade de origen'},
'Intersection with the centroid (Topology)' : {'es': 'Intersección con el centroide (Topología)'},
'Filling attributes...' : {'es': 'Atributos de relleno...'},
'Measure layers' : {'es': 'Medir capas'},
'Meters (m)' : {'es': 'Metros (m)'},
'Feet (ft)' : {'es': 'Pies (pies)'},
'Yards (yd)' : {'es': 'Yardas (yd)'},
'Kilometers (Km)' : {'es': 'Kilómetros (Km)'},
'Miles (mi)' : {'es': 'Millas (mi)'},
'Square Meters (m²)' : {'es': 'Metros cuadrados (m²)'},
'Hectares (ha)' : {'es': 'Hectáreas (ha)'},
'Square Kilometers (Km²)' : {'es': 'Kilómetros cuadrados (Km²)'},
'Layers' : {'es': 'Capas'},
'Distance Units' : {'es': 'Unidades de distancia'},
'Area Units' : {'es': 'Unidades de área'},
'Precision' : {'es': 'Precisión'},
'Ellipsoid' : {'es': 'elipsoide'},
'Cartesian / Projected' : {'es': 'Cartesiano / Proyectado'},
'Local Tangent Plane - LTP' : {'es': 'Plano tangente local - LTP'},
'Calculation' : {'es': 'Cálculo'},
'NMEA to layer' : {'es': 'NMEA a capa'},
'GNSS' : {'es': 'GNSS'},
'NMEA file .nmea' : {'es': 'Archivo NMEA .nmea'},
'Kinematic' : {'es': 'Cinemático'},
'Static, fixed solution (best result)' : {'es': 'Solución estática y fija (mejor resultado)'},
'Static, all observations' : {'es': 'Estático, todas las observaciones.'},
'Attributes' : {'es': 'Atributos'},
'Antenna height' : {'es': 'Altura de la antena'},
'Choose a geographic CRS!' : {'es': '¡Elija un CRS geográfico!'},
'There is no observation with RTK correction.' : {'es': 'No hay observación con la corrección RTK.'},
'POS file (.pos) to layer' : {'es': 'Archivo POS (.pos) a capa'},
'Velocity models:' : {'es': 'Modelos de velocidad:'},
'POS file (.pos)' : {'es': 'Archivo POS (.pos)'},
'All points processed' : {'es': 'Todos los puntos procesados'},
'Last point' : {'es': 'Ultimo punto'},
'None' : {'es': 'Ninguno'},
'VEMOS2009' : {'es': 'VEMOS2009'},
'VEMOS2017' : {'es': 'VEMOS2017'},
'Velocity Model' : {'es': 'Modelo de velocidad'},
'Unrecognized POS file format!' : {'es': '¡Formato de archivo POS no reconocido!'},
'RTK Points Correction' : {'es': 'Corrección de puntos RTK'},
'GNSS RTK Point Layer' : {'es': 'Capa de puntos GNSS RTK'},
'Adjusted RTK points' : {'es': 'Puntos RTK ajustados'},
'Input points layer must be of type PointZ!' : {'es': '¡La capa de puntos de entrada debe ser del tipo PointZ!'},
'Semi major axis: {}' : {'es': 'Semieje mayor: {}'},
'Inverse flattening: {}' : {'es': 'Aplanamiento inverso: {}'},
'Geocentric delta X: {:.4f} m' : {'es': 'Delta geocéntrico X: {:.4f} m'},
'Geocentric delta Y: {:.4f} m' : {'es': 'Delta geocéntrico Y: {:.4f} m'},
'Geocentric delta Z: {:.4f} m' : {'es': 'Delta geocéntrico Z: {:.4f} m'},
'Geocentric Delta 3D: {:.4f} m' : {'es': 'Delta geocéntrico 3D: {:.4f} m'},
'Stop and Go' : {'es': 'Detente y sigue'},
'GNSS point Layer' : {'es': 'Capa de puntos GNSS'},
'Minimum time for static positioning (minutes)' : {'es': 'Tiempo mínimo para posicionamiento estático (minutos)'},
'Maximum distance to be static (cm)' : {'es': 'Distancia máxima para ser estático (cm)'},
'Central points' : {'es': 'Puntos centrales'},
'datetime' : {'es': 'fecha y hora'},
'Check the input layer!' : {'es': '¡Comprueba la capa de entrada!'},
'Calculating central features...' : {'es': 'Calculando entidades centrales...'},
'Backup database' : {'es': 'Backup de base de datos'},
'PostGIS' : {'es': 'PostGIS'},
'Folder to save the backup file' : {'es': 'Carpeta para guardar el archivo de copia de seguridad'},
'Database name' : {'es': 'Nombre de la base de datos'},
'Host' : {'es': 'Anfitrión'},
'User' : {'es': 'Usuario'},
'PostgreSQL version' : {'es': 'Versión PostgreSQL'},
'Make sure your PostgreSQL version is correct!' : {'es': '¡Asegúrese de que su versión de PostgreSQL sea correcta!'},
'Command: ' : {'es': 'Dominio:'},
'Starting DB Backup process...' : {'es': 'Iniciando el proceso de copia de seguridad de la base de datos...'},
'Change SQL encoding' : {'es': 'Cambiar la codificación SQL'},
'SQL File' : {'es': 'Archivo SQL'},
'Original encoding' : {'es': 'Codificación original'},
'New encoding' : {'es': 'Nueva codificación'},
'Clone database' : {'es': 'Clonar base de datos'},
'Original database' : {'es': 'Base de datos original'},
'Name(s) of the cloned database(s)' : {'es': 'Nombre(s) de la(s) base(s) de base de datos clonada(s)'},
'Port' : {'es': 'Puerto'},
'Starting database cloning process...' : {'es': 'Iniciando proceso de clonación de base de datos...'},
'Delete database' : {'es': 'Eliminar base de datos'},
'DB Name(s) to be deleted' : {'es': 'Nombre(s) de base de datos que se eliminarán'},
'Starting delete/drop database(s)...' : {'es': 'Iniciando eliminar/eliminar bases de datos...'},
'Import raster' : {'es': 'Importar ráster'},
'Raster layer' : {'es': 'capa rasterizada'},
'Database' : {'es': 'Base de datos'},
'Schema' : {'es': 'Esquema'},
'Table' : {'es': 'Mesa'},
'Options' : {'es': 'Opciones'},
'Create column with raster name' : {'es': 'Crear columna con nombre de ráster'},
'Tiling' : {'es': 'Embaldosado'},
'Overviews' : {'es': 'Resúmenes'},
'Importing raster into the database...' : {'es': 'Importando ráster a la base de datos...'},
'Rename database' : {'es': 'Cambiar nombre de base de datos'},
'Original database name' : {'es': 'Nombre de la base de datos original'},
'New database name' : {'es': 'Nuevo nombre de base de datos'},
'Starting rename database process...' : {'es': 'Iniciando el proceso de cambio de nombre de la base de datos...'},
'Restore database' : {'es': 'Restaurar base de datos'},
'Starting DB Restore process...' : {'es': 'Iniciando el proceso de restauración de base de datos...'},
'Band Arithmetic' : {'es': 'Aritmética de bandas'},
'Raster' : {'es': 'Ráster'},
'Fourth band is transparency' : {'es': 'La cuarta banda es la transparencia.'},
'Formula' : {'es': 'Fórmula'},
'Calculated index' : {'es': 'Índice calculado'},
'Load calculated index' : {'es': 'Cargar índice calculado'},
'Carrying out the calculations...' : {'es': 'Realizando los cálculos...'},
'Check the input formula!' : {'es': '¡Comprueba la fórmula de entrada!'},
'Check if your formula is correct!' : {'es': '¡Comprueba si tu fórmula es correcta!'},
'Writing results...' : {'es': 'Escribiendo resultados...'},
'RGB composite' : {'es': 'compuesto RGB'},
'Red Band' : {'es': 'Banda roja'},
'Green Band' : {'es': 'Banda verde'},
'Blue Band' : {'es': 'Banda Azul'},
'RGB Composite' : {'es': 'Compuesto RGB'},
'Load RGB output' : {'es': 'Cargar salida RGB'},
'Opening R band...' : {'es': 'Abriendo banda R...'},
'Opening G band...' : {'es': 'Abriendo banda G...'},
'Opening B band...' : {'es': 'Apertura banda B...'},
'Creating RGB raster...' : {'es': 'Creando ráster RGB...'},
'Binary Thresholding' : {'es': 'Umbral binario'},
'Sample Polygons' : {'es': 'Polígonos de muestra'},
'Calculation of thresholds' : {'es': 'Cálculo de umbrales'},
'Threshold values (minimum and maximum) separated by comma' : {'es': 'Valores umbral (mínimo y máximo) separados por coma'},
'Binarized raster' : {'es': 'Ráster binarizado'},
'Load binarized image' : {'es': 'Cargar imagen binarizada'},
'The maximum and minimum thresholds cannot be the same!' : {'es': '¡Los umbrales máximo y mínimo no pueden ser iguales!'},
'Check that the minimum and maximum threshold values are correct!' : {'es': '¡Compruebe que los valores de umbral mínimo y máximo sean correctos!'},
'The raster layer must have only 1 band!' : {'es': '¡La capa ráster debe tener solo 1 banda!'},
'Taking raster samples by polygon...' : {'es': 'Tomando muestras ráster por polígono...'},
'Thresholding...' : {'es': 'Umbral...'},
'JPEG compression' : {'es': 'Compresión JPEG'},
'Compression Type' : {'es': 'Tipo de compresión'},
'Quality' : {'es': 'Calidad'},
'Tiled' : {'es': 'embaldosado'},
'Compressed Raster' : {'es': 'Ráster comprimido'},
'The input image must have 3 or 4 bands!' : {'es': '¡La imagen de entrada debe tener 3 o 4 bandas!'},
'Data type must be 8 bit!' : {'es': '¡El tipo de datos debe ser de 8 bits!'},
'The image must have 3 bands for Photometric compression!' : {'es': '¡La imagen debe tener 3 bandas para compresión fotométrica!'},
'Compressing...' : {'es': 'Apresamiento...'},
'Create holes in raster' : {'es': 'Crear agujeros en ráster'},
'Bumpy Raster' : {'es': 'Ráster lleno de baches'},
'Load Output Raster' : {'es': 'Cargar ráster de salida'},
'Opening Band R...' : {'es': 'Banda de apertura R...'},
'Opening Band G...' : {'es': 'Banda de apertura G...'},
'Opening Band B...' : {'es': 'Banda de apertura B...'},
'Opening band...' : {'es': 'Banda de apertura...'},
'Opening Band Alpha...' : {'es': 'Banda de apertura Alfa...'},
'Saving Raster...' : {'es': 'Guardando ráster...'},
'Writing Band R...' : {'es': 'Banda de escritura R...'},
'Writing Band G...' : {'es': 'Banda de escritura G...'},
'Writing Band B...' : {'es': 'Banda de escritura B...'},
'Writing Alpha Band...' : {'es': 'Escribiendo Banda Alfa...'},
'Writing raster band...' : {'es': 'Escribiendo banda rasterizada...'},
'Define null cells' : {'es': 'Definir celdas nulas'},
'Minimum Value' : {'es': 'Valor mínimo'},
'Maximum Value' : {'es': 'Valor máximo'},
'Value for defining null cells' : {'es': 'Valor para definir celdas nulas'},
'Raster with null cells defined' : {'es': 'Ráster con celdas nulas definidas'},
'Problem in input parameters interval!' : {'es': '¡Problema en el intervalo de parámetros de entrada!'},
'Raster with defined null cells' : {'es': 'Ráster con celdas nulas definidas'},
'Extract raster band' : {'es': 'Extraer banda ráster'},
'Multiband Input Raster' : {'es': 'Ráster de entrada multibanda'},
'Band number' : {'es': 'Número de banda'},
'Selected band' : {'es': 'banda seleccionada'},
'Reading the selected band...' : {'es': 'Leyendo la banda seleccionada...'},
'Writing the selected band...' : {'es': 'Escribiendo la banda seleccionada...'},
'Extracted band' : {'es': 'Banda extraída'},
'Fill with patches' : {'es': 'Rellenar con parches'},
'Patch Layers' : {'es': 'Capas de parche'},
'Patched Image' : {'es': 'Imagen parcheada'},
'Load patched Image' : {'es': 'Cargar imagen parcheada'},
'Opening raster band...' : {'es': 'Banda raster de apertura...'},
'Processing Layer: {}' : {'es': 'Capa de procesamiento: {}'},
'Writing rater band...' : {'es': 'Banda evaluadora de escritura...'},
'Saving raster...' : {'es': 'Guardando ráster...'},
'Estimate point value from Raster' : {'es': 'Estimar el valor de puntos a partir de Raster'},
'Vector Layer de Pontos' : {'es': 'Capa vectorial de puntos'},
'Nearest' : {'es': 'Más cercano'},
'Interpolation method' : {'es': 'Método de interpolación'},
'Output column prefix' : {'es': 'Prefijo de columna de salida'},
'sample_' : {'es': 'muestra_'},
'Points with interpolated value from raster' : {'es': 'Puntos con valor interpolado desde ráster'},
'Getting values from band {}...' : {'es': 'Obteniendo valores de la banda {}....'},
'Saving results...' : {'es': 'Guardando resultados...'},
'Histogram matching' : {'es': 'Coincidencia de histograma'},
'Reference raster' : {'es': 'Ráster de referencia'},
'Polygons' : {'es': 'Polígonos'},
'Histogram matched' : {'es': 'Histograma coincidente'},
'Opening reference raster...' : {'es': 'Ráster de referencia de apertura...'},
'Calculating histogram...' : {'es': 'Calculando histograma...'},
'Raster data inventory' : {'es': 'Inventario de datos ráster'},
'Check subfolders' : {'es': 'Comprobar subcarpetas'},
'Format' : {'es': 'Formato'},
'Geometry' : {'es': 'Geometría'},
'Polygon' : {'es': 'Polígono'},
'Inventory Layer' : {'es': 'Capa de inventario'},
'extension' : {'es': 'extensión'},
'Checking files in the folder...' : {'es': 'Comprobando archivos en la carpeta...'},
'Creating raster files...' : {'es': 'Creando archivos ráster...'},
'Load raster by location' : {'es': 'Cargar ráster por ubicación'},
'Vector Layer' : {'es': 'capa vectorial'},
'Verifying raster files...' : {'es': 'Verificando archivos ráster...'},
'Mosaic raster' : {'es': 'mosaico de trama'},
'Raster List' : {'es': 'Lista de ráster'},
'New Resolution (meters)' : {'es': 'Nueva resolución (metros)'},
'First (faster)' : {'es': 'Primero (más rápido)'},
'Average' : {'es': 'Promedio'},
'Median' : {'es': 'Mediana'},
'Maximum' : {'es': 'Máximo'},
'Minimum' : {'es': 'Mínimo'},
'Ovelap' : {'es': 'superposición'},
'Null value' : {'es': 'Valor nulo'},
'Clip by frame' : {'es': 'Clip por fotograma'},
'Mosaic' : {'es': 'Mosaico'},
'Load mosaic' : {'es': 'Cargar mosaico'},
'At least one raster must be selected!' : {'es': '¡Se debe seleccionar al menos un ráster!'},
'The images must have the same number of bands!' : {'es': '¡Las imágenes deben tener la misma cantidad de bandas!'},
'The images must have the same CRS!' : {'es': '¡Las imágenes deben tener el mismo CRS!'},
'The images must have the same data type!' : {'es': '¡Las imágenes deben tener el mismo tipo de datos!'},
'The images must have the same definied null value!' : {'es': '¡Las imágenes deben tener el mismo valor nulo definido!'},
'Defining mosaic filling areas...' : {'es': 'Definiendo áreas de relleno de mosaico...'},
'Creating combinations...' : {'es': 'Creando combinaciones...'},
'Indentifying combinations...' : {'es': 'Identificando combinaciones...'},
'Classifying class {}...' : {'es': 'Clasificando clase {}....'},
'Creating band {}...' : {'es': 'Creando banda {}....'},
'Rescale to 8 bit' : {'es': 'Reescalar a 8 bits'},
'Raster Imagery' : {'es': 'Imágenes rasterizadas'},
'Rescale type' : {'es': 'Tipo de cambio de escala'},
'Rescales by band' : {'es': 'Reescala por banda'},
'Define null pixel as zero' : {'es': 'Establece el píxel nulo en cero'},
'8 bit rescaled raster' : {'es': 'Ráster reescalado de 8 bits'},
'Opening raster...' : {'es': 'Apertura de trama...'},
'Calculating statistics...' : {'es': 'Calculando estadísticas...'},
'Rescaling and saving bands...' : {'es': 'Reescalando y guardando bandas...'},
'Rescaled to 8 bit' : {'es': 'Reescalado a 8 bits'},
'RGB to HSV' : {'es': 'RGB a HSV'},
'Hue' : {'es': 'Matiz'},
'Saturation' : {'es': 'Saturación'},
'Value' : {'es': 'Valor'},
'The raster layer must have 3 (RGB) or 4 bands (RGBA)!' : {'es': '¡La capa ráster debe tener 3 (RGB) o 4 bandas (RGBA)!'},
'Split raster' : {'es': 'Ráster dividido'},
'Folder for split rasters' : {'es': 'Carpeta para rásteres divididos'},
'Exporting file {} ...' : {'es': 'Exportando archivo {}...'},
'Supervised classification' : {'es': 'Clasificación supervisada'},
'Class Field' : {'es': 'Campo de clase'},
'Parallelepiped' : {'es': 'Paralelepípedo'},
'Euclidean Distance' : {'es': 'Distancia euclidiana'},
'Mahalanobis Distance' : {'es': 'Distancia de Mahalanobis'},
'1 Standard Deviation (68%)' : {'es': '1 desviación estándar (68%)'},
'2 Standard Deviations (95%)' : {'es': '2 desviaciones estándar (95%)'},
'3 Standard Deviations (99.7%)' : {'es': '3 desviaciones estándar (99,7%)'},
'Size (only for Parallelepiped and Ellipsoid Methods)' : {'es': 'Tamaño (solo para métodos de paralelepípedo y elipsoide)'},
'Classified Image' : {'es': 'Imagen clasificada'},
'Load classified Image' : {'es': 'Cargar imagen clasificada'},
'The raster layer must have more than 1 band!' : {'es': '¡La capa ráster debe tener más de 1 banda!'},
'Covariance matrix is singular. Choose another method!' : {'es': 'La matriz de covarianza es singular. ¡Elija otro método!'},
'Zonal Statistics' : {'es': 'Estadísticas Zonales'},
'Band' : {'es': 'Banda'},
'Statistics' : {'es': 'Estadísticas'},
'Zonal statistics' : {'es': 'Estadísticas zonales'},
'Calculating zonal statistics...' : {'es': 'Calculando estadísticas zonales...'},
'Creating layer with results...' : {'es': 'Creando capa con resultados...'},
'Photos with geotag' : {'es': 'Fotos con geoetiqueta'},
'Reambulation' : {'es': 'Reambulación'},
'Folder with geotagged photos' : {'es': 'Carpeta con fotos geoetiquetadas'},
'Folder to copy the photos without geotag' : {'es': 'Carpeta para copiar las fotos sin geoetiqueta'},
'Geolocated photos' : {'es': 'Fotos geolocalizadas'},
'longitude' : {'es': 'longitud'},
'latitude' : {'es': 'latitud'},
'altitude' : {'es': 'altitud'},
'azimuth' : {'es': 'azimut'},
'date_time' : {'es': 'fecha y hora'},
'make' : {'es': 'constituir'},
'model' : {'es': 'modelo'},
'Open photo' : {'es': 'Abrir Foto'},
'KML with photos' : {'es': 'KML con fotos'},
'Filepath to image' : {'es': 'Ruta de archivo a la imagen'},
'Description' : {'es': 'Descripción'},
'Altitude' : {'es': 'Altitud'},
'KML file with photos' : {'es': 'Archivo KML con fotos.'},
'Resize photos' : {'es': 'Cambiar el tamaño de las fotos'},
'Folder with photos (.jpeg or .jpg)' : {'es': 'Carpeta con fotos (.jpeg o .jpg)'},
'Size for the larger side' : {'es': 'Tamaño para el lado más grande'},
'Folder for the resized photos' : {'es': 'Carpeta para las fotos redimensionadas.'},
'Input and output folders cannot be the same!' : {'es': '¡Las carpetas de entrada y salida no pueden ser iguales!'},
'Resizing the images...' : {'es': 'Cambiando el tamaño de las imágenes...'},
'DEM to Text' : {'es': 'DEM a texto'},
'Relief' : {'es': 'Elevación'},
'DEM' : {'es': 'DEM'},
'Orthomosaic' : {'es': 'ortomosaico'},
'X,Y,Z Points as Text' : {'es': 'Puntos X,Y,Z como texto'},
'Opening DEM raster file...' : {'es': 'Abriendo archivo ráster DEM...'},
'The raster layer should only have 1 band!' : {'es': '¡La capa ráster solo debe tener 1 banda!'},
'Opening Orthomosaic raster file...' : {'es': 'Abriendo archivo ráster ortomosaico...'},
'The raster layer should have RBG bands!' : {'es': '¡La capa ráster debe tener bandas RBG!'},
'Creating output file...' : {'es': 'Creando archivo de salida...'},
'DEM difference' : {'es': 'diferencia DEM'},
'Minuend' : {'es': 'minuendo'},
'Subtrahend' : {'es': 'Sustraendo'},
'Reference grid' : {'es': 'Cuadrícula de referencia'},
'Multiply the result by -1' : {'es': 'Multiplica el resultado por -1'},
'Difference' : {'es': 'Diferencia'},
'Load raster' : {'es': 'Cargar ráster'},
'Opening minuend raster file...' : {'es': 'Abriendo archivo ráster de minuendo...'},
'Opening subtrahend raster file...' : {'es': 'Abriendo archivo ráster de sustraendo...'},
'Calculating the difference...' : {'es': 'Calculando la diferencia...'},
'DEM filter' : {'es': 'Filtro DEM'},
'Mean kernel - 3 by 3' : {'es': 'Núcleo medio - 3 por 3'},
'Mean kernel - 5 by 5' : {'es': 'Núcleo medio - 5 por 5'},
'Median kernel - 3 by 3' : {'es': 'Núcleo mediano - 3 por 3'},
'Median kernel - 5 by 5' : {'es': 'Núcleo mediano - 5 por 5'},
'Minimum kernel - 3 by 3' : {'es': 'Núcleo mínimo - 3 por 3'},
'Minimum kernel - 5 by 5' : {'es': 'Núcleo mínimo - 5 por 5'},
'Maximum kernel - 3 by 3' : {'es': 'Núcleo máximo - 3 por 3'},
'Maximum kernel - 5 by 5' : {'es': 'Núcleo máximo - 5 por 5'},
'Filter' : {'es': 'Filtrar'},
'Filtered Raster' : {'es': 'Ráster filtrado'},
'Load filtered raster' : {'es': 'Cargar ráster filtrado'},
'Raster filtering...' : {'es': 'Filtrado de trama...'},
'Filtered raster' : {'es': 'Ráster filtrado'},
'Generate Spot Elevations' : {'es': 'Generar elevaciones puntuales'},
'Contour Lines' : {'es': 'Curvas de nivel'},
'Elevation field' : {'es': 'campo de elevación'},
'Spot Elevations' : {'es': 'Elevaciones puntuales'},
'elevation' : {'es': 'elevación'},
'The process was finished!' : {'es': '¡El proceso había terminado!'},
'Central Tendency' : {'es': 'Tendencia central'},
'Spatial Statistics' : {'es': 'Estadísticas espaciales'},
'Mean Center' : {'es': 'Centro medio'},
'Median Center' : {'es': 'Centro de Medios'},
'Central Feature' : {'es': 'Característica central'},
'Weight Field' : {'es': 'Campo de peso'},
'Central point' : {'es': 'Punto central'},
'group' : {'es': 'grupo'},
'count' : {'es': 'contar'},
'Central tendency - ' : {'es': 'Tendencia central -'},
'Confidence ellipses' : {'es': 'Elipses de confianza'},
'68% Confidence Ellipse' : {'es': 'Elipse de confianza del 68%'},
'90% Confidence Ellipse' : {'es': 'Elipse de confianza del 90%'},
'95% Confidence Ellipse' : {'es': 'Elipse de confianza del 95%'},
'99% Confidence Ellipse' : {'es': 'Elipse de confianza del 99%'},
'Size' : {'es': 'Tamaño'},
'Standard Deviational Ellipse(s)' : {'es': 'Elipse(s) de desviación estándar'},
'confidence' : {'es': 'confianza'},
'rotation' : {'es': 'rotación'},
'Nearest points' : {'es': 'Puntos más cercanos'},
'Reference points' : {'es': 'Puntos de referencia'},
'Points to be analyzed' : {'es': 'Puntos a analizar'},
'Maximum distance (meters)' : {'es': 'Distancia máxima (metros)'},
'Minimum quantity' : {'es': 'Cantidad mínima'},
'Maximum distance' : {'es': 'Distancia máxima'},
'Maximum distance and minimum quantity' : {'es': 'Distancia máxima y cantidad mínima'},
'Condition' : {'es': 'Condición'},
'Attribute stats' : {'es': 'Estadísticas de atributos'},
'Gaussian random points' : {'es': 'Puntos aleatorios gaussianos'},
'Origin Point' : {'es': 'Punto de origen'},
'Standard Deviation for X' : {'es': 'Desviación estándar para X'},
'Standard Deviation for Y' : {'es': 'Desviación estándar para Y'},
'Rotation Angle' : {'es': 'Ángulo de rotación'},
'Number of Points' : {'es': 'Número de puntos'},
'Gaussian Random Points' : {'es': 'Puntos aleatorios gaussianos'},
'Standard Distance' : {'es': 'Distancia estándar'},
'1 standard deviation' : {'es': '1 desviación estándar'},
'2 standard deviations' : {'es': '2 desviaciones estándar'},
'3 standard deviations' : {'es': '3 desviaciones estándar'},
'Circle Size' : {'es': 'Tamaño del círculo'},
'size' : {'es': 'tamaño'},
'Azimuth and distance' : {'es': 'Azimut y distancia'},
'Survey' : {'es': 'Topografía'},
'Origin Point Coordinates' : {'es': 'Coordenadas del punto de origen'},
'List of Horizontal Distances' : {'es': 'Lista de distancias horizontales'},
'List of Azimuths' : {'es': 'Lista de acimutes'},
'Output geometry type' : {'es': 'Tipo de geometría de salida'},
'Solve misclosure' : {'es': 'Resolver error de cierre'},
'Output layer' : {'es': 'Capa de salida'},
'The number of measured distances must be equal to the number of azimuths!' : {'es': '¡El número de distancias medidas debe ser igual al número de acimutes!'},
'The output CRS must be Projected!' : {'es': '¡La salida del CRS debe ser proyectada!'},
'Misclosure error: {} m' : {'es': 'Error de cierre incorrecto: {} m'},
'Closed polygonal' : {'es': 'Poligonal cerrado'},
'Azimuth (origin)' : {'es': 'Azimut (original)'},
'List of Angles' : {'es': 'Lista de ángulos'},
'Adjusted Points' : {'es': 'Puntos ajustados'},
'The number of measured distances must be equal to the number of angles!' : {'es': '¡El número de distancias medidas debe ser igual al número de ángulos!'},
'Closed Traverse' : {'es': 'Travesía cerrada'},
'CLOSED TRAVERSE' : {'es': 'TRAVESÍA CERRADA'},
'Analytical Calculation' : {'es': 'Cálculo analítico'},
'REPORT' : {'es': 'INFORME'},
'Angle' : {'es': 'Ángulo'},
'Distance' : {'es': 'Distancia'},
'Corrected Angle' : {'es': 'Ángulo corregido'},
'Final E' : {'es': 'mi final'},
'Final N' : {'es': 'N final'},
'Angular closure error' : {'es': 'Error de cierre angular'},
'Linear closure error' : {'es': 'Error de cierre lineal'},
'Linear relative error' : {'es': 'Error relativo lineal'},
'*The unit of measurement of the adjusted coordinates is the same as the input coordinates.' : {'es': '*La unidad de medida de las coordenadas ajustadas es la misma que la de las coordenadas de entrada.'},
'Leandro Franca' : {'es': 'Leandro Franca'},
'Cartographic Engineer' : {'es': 'Ingeniero Cartográfico'},
'Coordinate transformation 2D' : {'es': 'Transformación de coordenadas 2D'},
'Input Vector Layer' : {'es': 'Capa de vector de entrada'},
'Transformed Layer' : {'es': 'Capa transformada'},
'The geometry type of vectors layer must be Polyline!' : {'es': '¡El tipo de geometría de la capa de vectores debe ser Polilínea!'},
'The vectors must be lines with exactly two vertices!' : {'es': '¡Los vectores deben ser líneas con exactamente dos vértices!'},
'Estimate 3D coordinates' : {'es': 'Estimar coordenadas 3D'},
'Coordinates of Optical Centers' : {'es': 'Coordenadas de Centros Ópticos'},
'Azimuths' : {'es': 'Acimutes'},
'Zenith Angles' : {'es': 'Ángulos cenit'},
'Use Weight Matrix (W)' : {'es': 'Usar matriz de peso (W)'},
'Adjusted 3D Coordinates' : {'es': 'Coordenadas 3D ajustadas'},
'Open output file after executing the algorithm' : {'es': 'Abrir el archivo de salida después de ejecutar el algoritmo'},
'Wrong number of parameters!' : {'es': '¡Número incorrecto de parámetros!'},
'Estimate 3D Coordinates' : {'es': 'Estimar coordenadas 3D'},
'ESTIMATE 3D COORDINATES' : {'es': 'ESTIMA COORDENADAS 3D'},
'Minimum Distance Method' : {'es': 'Método de distancia mínima'},
'Inputs' : {'es': 'Entradas'},
'Adjustment' : {'es': 'Ajustamiento'},
'Coordinates of the Optical Centers' : {'es': 'Coordenadas de los Centros Ópticos'},
'Residuals (V)' : {'es': 'Residuos (V)'},
'Posteriori Variance' : {'es': 'Varianza posterior'},
'Adjusted Coordinates, Slant Ranges and Precisions**' : {'es': 'Coordenadas ajustadas, rangos de inclinación y precisiones**'},
'*The inverse of the distances to the diagonal of the Weight Matrix is considered.' : {'es': '*Se considera la inversa de las distancias a la diagonal de la Matriz de Pesos.'},
'**The unit of measurement of the adjusted coordinates is the same as the input coordinates.' : {'es': '**La unidad de medida de las coordenadas ajustadas es la misma que la de las coordenadas de entrada.'},
'Yes' : {'es': 'Sí'},
'Local Geodetic System transform' : {'es': 'Transformación del sistema geodésico local'},
'Local Geodetic System (LGS)' : {'es': 'Sistema Geodésico Local (LGS)'},
'Table of coordinates' : {'es': 'tabla de coordenadas'},
'lon, lat, h' : {'es': 'lon, lat, h'},
'X, Y, Z' : {'es': 'X Y Z'},
'E, N, U' : {'es': 'E, N, U'},
'Input Coordinates type' : {'es': 'Tipo de coordenadas de entrada'},
'Lon, X or E field' : {'es': 'Campo Lon, X o E'},
'Lat, Y or N field' : {'es': 'Campo Lat, Y o N'},
'h, Z or U field' : {'es': 'campo h, Z o U'},
'Ellipsoid parameters' : {'es': 'Parámetros del elipsoide'},
'Origin Longitude (λ)' : {'es': 'Longitud de origen (λ)'},
'Origin Latitude (ϕ)' : {'es': 'Origen Latitud (ϕ)'},
'Origin Elipsoid Height (h)' : {'es': 'Origen Elipsoide Altura (h)'},
'Transformed Coordinates' : {'es': 'Coordenadas transformadas'},
'Traverse adjustment' : {'es': 'Ajuste transversal'},
'A: first (E,N) coordinates' : {'es': 'A: primeras coordenadas (E,N)'},
'B: second (E,N) coordinates' : {'es': 'B: segundas coordenadas (E,N)'},
'Y: penultimate (E,N) coordinates' : {'es': 'Y: penúltimas coordenadas (E,N)'},
'Z: final (E,N) coordinates' : {'es': 'Z: coordenadas finales (E,N)'},
'List of Horizontal Distances (m)' : {'es': 'Lista de Distancias Horizontales (m)'},
'Initial distance precision (mm)' : {'es': 'Precisión de distancia inicial (mm)'},
'PPM distance precision' : {'es': 'Precisión de distancia PPM'},
'Angular precision (seconds)' : {'es': 'Precisión angular (segundos)'},
'Report of the closed traverse' : {'es': 'Informe del cruce cerrado'},
'Traverse Adjustment Report' : {'es': 'Informe de ajuste transversal'},
'TRAVERSE ADJUSTMENT' : {'es': 'AJUSTE TRANSVERSAL'},
'Method of Least Squares' : {'es': 'Método de mínimos cuadrados'},
'Initial approximation' : {'es': 'Aproximación inicial'},
'Adjusted Coordinates' : {'es': 'Coordenadas ajustadas'},
'Posteriori variance' : {'es': 'varianza posterior'},
'Observations' : {'es': 'Observaciones'},
'Residual' : {'es': 'Residual'},
'Adjusted Observation' : {'es': 'Observación ajustada'},
'Standard Deviation' : {'es': 'Desviación Estándar'},
'Connect layers' : {'es': 'Conectar capas'},
'Vector' : {'es': 'Vector'},
'Reference layer' : {'es': 'Capa de referencia'},
'Connected polygons' : {'es': 'Polígonos conectados'},
'Cross Sections' : {'es': 'Secciones cruzadas'},
'Cross sections' : {'es': 'Secciones cruzadas'},
'Merge lines in direction' : {'es': 'Fusionar líneas en dirección'},
'Line Layer' : {'es': 'Capa de línea'},
'merge lines that have the same attributes' : {'es': 'fusionar líneas que tienen los mismos atributos'},
'keep the attributes of the longest line' : {'es': 'mantener los atributos de la línea más larga'},
'Tolerance in degrees' : {'es': 'Tolerancia en grados'},
'Merged lines' : {'es': 'Líneas fusionadas'},
'The input angle must be between 0 and 90 degrees!' : {'es': '¡El ángulo de entrada debe estar entre 0 y 90 grados!'},
'Calculating feature informations...' : {'es': 'Calculando información de entidades...'},
'Merging lines...' : {'es': 'Fusionando líneas...'},
'Saving output...' : {'es': 'Guardando salida...'},
'Extend lines' : {'es': 'Extender líneas'},
'Start and End points' : {'es': 'Puntos de inicio y fin'},
'Only End Point' : {'es': 'Sólo punto final'},
'Only Start Point' : {'es': 'Sólo punto de inicio'},
'Extended lines' : {'es': 'Líneas extendidas'},
'The input distance must be greater than 0!' : {'es': '¡La distancia de entrada debe ser mayor que 0!'},
'Line sequence' : {'es': 'Secuencias de líneas'},
'Only selected line' : {'es': 'Sólo línea seleccionada'},
'Tolerance (m)' : {'es': 'Tolerancia (m)'},
'Check the connectivity between the lines or increase the tolerance value!' : {'es': '¡Compruebe la conectividad entre las líneas o aumente el valor de tolerancia!'},
'Lines to polygon' : {'es': 'Líneas a polígono'},
'Line layer (connected)' : {'es': 'Capa de línea (conectada)'},
'Polygon from lines' : {'es': 'Polígono de líneas'},
'Validating connected features...' : {'es': 'Validando funciones conectadas...'},
'Overlapping polygons' : {'es': 'Polígonos superpuestos'},
'Overlapping' : {'es': 'superpuestas'},
'Identifying overlapping polygons...' : {'es': 'Identificando polígonos superpuestos...'},
'Points to polygon' : {'es': 'Puntos al polígono'},
'Polygon from points' : {'es': 'Polígono desde puntos'},
'All attributes of the order field (sequence) must be greater than zero and not null!' : {'es': '¡Todos los atributos del campo de orden (secuencia) deben ser mayores que cero y no nulos!'},
'Calculate polygon angles' : {'es': 'Calcular ángulos de polígonos'},
'Points with angles' : {'es': 'Puntos con ángulos'},
'ang_inner_dd' : {'es': 'ang_inner_dd'},
'ang_inner_dms' : {'es': 'ang_inner_dms'},
'ang_outer_dd' : {'es': 'ang_exterior_dd'},
'ang_outer_dms' : {'es': 'ang_outer_dms'},
'label_azimuth' : {'es': 'etiqueta_azimut'},
'Reverse vertex order' : {'es': 'Orden inverso de los vértices'},
'Input Layer' : {'es': 'Capa de entrada'},
'Sequence points' : {'es': 'Puntos de secuencia'},
'Only selected points' : {'es': 'Sólo puntos seleccionados'},
'Only selected polygon' : {'es': 'Sólo polígono seleccionado'},
'Polygon sequence' : {'es': 'Secuencias de polígonos'},
'Polygon layer must have only 1 selected feature!' : {'es': '¡La capa de polígono debe tener solo 1 entidad seleccionada!'},
'The number of points must equal the number of vertices of the polygon!' : {'es': '¡El número de puntos debe ser igual al número de vértices del polígono!'},
'Click here for understanding this data model.' : {'es': 'Haga clic aquí para comprender este modelo de datos.'},
'Calculation of azimuths, distances and area' : {'es': 'Cálculo de acimutes, distancias y áreas.'},
'Calculation of azimuths, distances and area considering the Project CRS.' : {'es': 'Cálculo de acimutes, distancias y áreas considerando el Proyecto CRS.'},
'Calculation azimuths, distances and area considering the Local Tangent Plane (LTP).' : {'es': 'Cálculo de acimutes, distancias y áreas considerando el Plano Tangente Local (LTP).'},
'Calculation of distances and area considering the Local Tangent Plane (LTP). Calculation of azimuths carried out according to the Inverse Geodetic Problem formulae according to Puissant.' : {'es': 'Cálculo de distancias y áreas considerando el Plano Tangente Local (LTP). Cálculo de acimutes realizado según las fórmulas del Problema Geodésico Inverso según Puissant.'},
'Analytical Calculation of Area, Azimuths, Sides, Flat and Geodetic Coordinates' : {'es': 'Cálculo Analítico de Área, Acimutes, Lados, Coordenadas Planas y Geodésicas'},
'from this, it continues to confront [Confront_k], with the following azimuths and distances: [Az_n] and [Dist_n]m up to ' : {'es': 'a partir de esto continúa enfrentando [Confront_k], con los siguientes azimuts planos y distancias: [Az_n] y [Dist_n]m hasta'},
'Calculation of azimuths and distances' : {'es': 'Cálculo de acimutes y distancias.'},
'Click here for testing your regular expression (RegEx).' : {'es': 'Haga clic aquí para probar su expresión regular (RegEx).'},
'Point of the "line" layer has no correspondent in the "point" layer!' : {'es': '¡El punto de la capa "línea" no tiene correspondencia en la capa "punto"!'},
'Point of the "area" layer has no correspondent in the "point" layer!' : {'es': '¡El punto de la capa "área" no tiene correspondencia en la capa "punto"!'},
'Point of the "point" layer has no correspondent in the "area" layer!' : {'es': '¡El punto de la capa "punto" no tiene correspondencia en la capa "área"!'},
'Point of the "point" layer has no correspondent in the "line" layer!' : {'es': '¡El punto de la capa "punto" no tiene correspondencia en la capa "línea"!'},
'Vertex of the "point" layer is duplicated!' : {'es': '¡El vértice de la capa "punto" está duplicado!'},
'Vertex of the "line" layer is duplicated!' : {'es': '¡El vértice de la capa "línea" está duplicado!'},
'Vertex of the "area" layer is duplicated!' : {'es': '¡El vértice de la capa "área" está duplicado!'},
'Problem with the orientation of the vertices of the line layer!' : {'es': '¡Problema con la orientación de los vértices de la capa de líneas!'},
'Z altitude not filled in correctly!' : {'es': '¡La altitud Z no se completó correctamente!'},
'Input layer must be of type LineStringZ!' : {'es': '¡La capa de entrada debe ser del tipo LineStringZ!'},
'There was a problem while executing the command. Please check the input parameters.' : {'es': 'Hubo un problema al ejecutar el comando. Por favor verifique los parámetros de entrada.'},
'This algorithm returns the polygon correspondent to the frame related to a scale of the Brazilian Mapping System based on the Map Index (MI). Example: MI = 1214-1' : {'es': 'Este algoritmo devuelve el polígono correspondiente al marco relacionado con una escala del Sistema Cartográfico Brasileño basado en el Índice de Mapa (IM). Ejemplo: MI = 1214-1'},
'Check the geometry type!' : {'es': '¡Comprueba el tipo de geometría!'},
'Check the geometry type' : {'es': 'Verifique el tipo de geometría'},
'CLASS' : {'es': 'CLASE'},
'VALUE' : {'es': 'VALOR'},
'SUM' : {'es': 'SUMA'},
'Check if the geometry is null or invalid! Or if Atlas is on!' : {'es': '¡Compruebe si la geometría es nula o no válida! ¡O si Atlas está encendido!'},
'Vertex' : {'es': 'Vértice'},
'Forward neighbor' : {'es': 'Vecino de adelante'},
'Complement' : {'es': 'Complementar'},
'Invalid adjoiner line in [X] and [Y] coordinates! Perform layers topological validation!' : {'es': '¡Línea de Adyacentes no válida en las coordenadas [X] e [Y]! ¡Realice validación topológica de capas!'},
'This algorithm returns the frame related to a scale of the Brazilian Mapping System. The generated frame, which is a polygon, is calculated from a Point defined by the user.' : {'es': 'Este algoritmo devuelve el cuadro relacionado con una escala del Sistema Brasileño de Cartografía. El marco generado, que es un polígono, se calcula a partir de un Punto definido por el usuario.'},
'This algorithm returns the polygons correspondent to the <b>frames</b> related to a scale of the Brazilian Mapping System from a specific <b>extent</b> definied by the user.' : {'es': 'Este algoritmo devuelve los polígonos correspondientes a los <b>cuadros</b> relacionados con una escala del Sistema Cartográfico Brasileño a partir de una <b>extensión</b> específica definida por el usuario.'},
'Calculates the adjusted coordinates from angles and horizontal distances of a Closed Polygonal.' : {'es': 'Calcula las coordenadas ajustadas a partir de ángulos y distancias horizontales de un Poligonal Cerrado.'},
'This tool calculates the coordinates (X, Y, Z) of a point from azimuth and zenith angle measurements observed from two or more stations with known coordinates using the Foward Intersection Method adjusted by the Minimum Distances.' : {'es': 'Esta herramienta calcula las coordenadas (X, Y, Z) de un punto a partir de mediciones de ángulos de acimut y cenit observadas desde dos o más estaciones con coordenadas conocidas utilizando el método de intersección directa ajustado por las distancias mínimas.'},
'This algorithm performs the traverse adjustments of a framed polygonal by least squares method, where  the distances, angles, and directions observations are adjusted simultaneously, providing the most probable values for the given data set.  Futhermore, the observations can be rigorously weighted based on their estimated errors and adjusted accordingly.' : {'es': 'Este algoritmo realiza los ajustes transversales de un poligonal enmarcado mediante el método de mínimos cuadrados, donde las observaciones de distancias, ángulos y direcciones se ajustan simultáneamente, proporcionando los valores más probables para el conjunto de datos dado. Además, las observaciones pueden ponderarse rigurosamente en función de sus errores estimados y ajustarse en consecuencia.'},
'Creates ellipses based on the covariance matrix to summarize the spatial characteristics of point type geographic features: central tendency, dispersion, and directional trends.' : {'es': 'Crea elipses basadas en la matriz de covarianza para resumir las características espaciales de las entidades geográficas de tipo puntual: tendencia central, dispersión y tendencias direccionales.'},
'Generate gaussian (normal) random points in 2D space with a given mean position (X0, Y0), standard deviation for X and Y, and rotation angle.' : {'es': 'Genere puntos aleatorios gaussianos (normales) en el espacio 2D con una posición media determinada (X0, Y0), desviación estándar para X e Y y ángulo de rotación.'},
'Generates a <b>point layer</b> from a coordinate table, whether it comes from a Microsoft <b>Excel</b> spreadsheet (.xls), Open Document Spreadsheet (.ods), or even attributes from another layer.' : {'es': 'Genera una <b>capa de puntos</b> a partir de una tabla de coordenadas, ya sea que provenga de una hoja de cálculo de Microsoft <b>Excel</b> (.xls), una hoja de cálculo de documento abierto (.ods) o incluso atributos de otra capa. .'},
"This tool calculates the line feature's lengths and polygon feature's perimeter and area in virtual fields for all vector layers." : {'es': 'Esta herramienta calcula las longitudes de la entidad de línea y el perímetro y el área de la entidad poligonal en campos virtuales para todas las capas vectoriales.'},
'Combine three image bands into one picture by display each band as either Red, Green or Blue.' : {'es': 'Combine tres bandas de imágenes en una sola imagen mostrando cada banda como Roja, Verde o Azul.'},
'JPEG compression is a lossy method to reduce the raster file size (about to 10%). The compression level can be adjusted, allowing a selectable tradeoff between storage size and image quality.' : {'es': 'La compresión JPEG es un método con pérdida para reducir el tamaño del archivo rasterizado (aproximadamente hasta un 10%). El nivel de compresión se puede ajustar, lo que permite un equilibrio seleccionable entre el tamaño de almacenamiento y la calidad de la imagen.'},
'Creates holes in Raster by defining "no data" pixels (transparent) from the Polygon Layer.' : {'es': 'Crea agujeros en Raster definiendo píxeles "sin datos" (transparentes) de la capa de polígono.'},
'Cells of a raster with values outside the interval (minimum and maximum) are defined as null value.' : {'es': 'Las celdas de un ráster con valores fuera del intervalo (mínimo y máximo) se definen como valor nulo.'},
'Extracts a difined band of a raster (for multiband rasters).' : {'es': 'Extrae una banda definida de un ráster (para rásteres multibanda).'},
'Fills Raster null pixels (no data) with data obtained from other smaller raster layers (Patches).' : {'es': 'Rellena píxeles nulos de ráster (sin datos) con datos obtenidos de otras capas ráster más pequeñas (parches).'},
'Creates a vector layer with the inventory of raster files in a folder. The geometry type of the features of this layer can be Polygon (bounding box) or Point (centroid).' : {'es': 'Crea una capa vectorial con el inventario de archivos ráster en una carpeta. El tipo de geometría de las entidades de esta capa puede ser Polígono (cuadro delimitador) o Punto (centroide).'},
'Loads a set of raster files that intersect the geometries of an input vector layer.' : {'es': 'Carga un conjunto de archivos ráster que intersectan las geometrías de una capa vectorial de entrada.'},
'Creates raster mosaic: a combination or merge of two or more images.' : {'es': 'Crea un mosaico rasterizado: una combinación o fusión de dos o más imágenes.'},
'This tool removes the 4th band (apha band), transfering the transparency information as "NoData" to pixels of the RGB output.' : {'es': 'Esta herramienta elimina la cuarta banda (banda afa), transfiriendo la información de transparencia como "NoData" a los píxeles de la salida RGB.'},
'Rescales the values of the raster pixels with radiometric resolution of 16 bits (or even 8 bits or float) to exactly the range of 0 to 255, creating a new raster with 8 bits (byte) of radiometric resolution.' : {'es': 'Reescala los valores de los píxeles ráster con resolución radiométrica de 16 bits (o incluso 8 bits o flotante) exactamente al rango de 0 a 255, creando un nuevo ráster con 8 bits (byte) de resolución radiométrica.'},
'Performs the supervised classification of a raster layer with two or more bands.' : {'es': 'Realiza la clasificación supervisada de una capa ráster con dos o más bandas.'},
'Imports photos with geotag to a Point Layer.' : {'es': 'Importa fotografías con etiquetas geográficas a una capa de puntos.'},
'This algorithm merges lines that touch at their starting or ending points and has the same direction (given a tolerance in degrees). <p>For the attributes can be considered:</p>1 - merge lines that have the same attributes; or</li><li>2 - keep the attributes of the longest line.</li>' : {'es': 'Este algoritmo fusiona líneas que se tocan en sus puntos inicial o final y tienen la misma dirección (dada una tolerancia en grados). <p>Para los atributos se puede considerar:</p>1 - fusionar líneas que tengan los mismos atributos; o</li><li>2 - conservar los atributos de la línea más larga.</li>'},
'Extends lines at their <b>start</b> and/or <b>end</b> points.' : {'es': 'Extiende líneas en sus puntos <b>inicio</b> y/o <b>final</b>.'},
'This algorithm calculates the inner and outer angles of the polygon vertices of a layer. The output layer corresponds to the points with the calculated angles stored in the respective attributes.' : {'es': 'Este algoritmo calcula los ángulos interior y exterior de los vértices del polígono de una capa. La capa de salida corresponde a los puntos con los ángulos calculados almacenados en los atributos respectivos.'},
'Inverts vertex order for polygons and lines.' : {'es': 'Invierte el orden de los vértices de polígonos y líneas.'},
'This script fills a certain attribute of the features of a layer of points according to its sequence in relation to the polygon of another layer.' : {'es': 'Este script rellena un determinado atributo de las entidades de una capa de puntos según su secuencia en relación al polígono de otra capa.'},
'This tool generates a Report for the Analytical Calculation of Area, Azimuths, Polygon Sides, UTM Projection and Geodetic Coordinates of a Property.' : {'es': 'Esta herramienta genera un Informe para el Cálculo Analítico de Área, Acimutes, Lados de Polígono, Proyección UTM y Coordenadas Geodésicas de una Propiedad.'},
'This tool generates report(s) with the informations about a geodetic landmarks automatically from the "reference_point_p" layer.' : {'es': 'Esta herramienta genera informes con la información sobre puntos de referencia geodésicos automáticamente desde la capa "reference_point_p".'},
"This tool generates the Vertices and Sides Descriptive Table, also known as Synthetic Deed Description, based on the attributes, sequence and code, in the point layer's attribute table." : {'es': 'Esta herramienta genera la Tabla Descriptiva de Vértices y Lados, también conocida como Descripción de Escritura Sintética, basada en los atributos, secuencia y código, en la tabla de atributos de la capa de puntos.'},
'This tool allows you to restore a database content by importing all the backup information in a ".sql" file into a PostgreSQL server.' : {'es': 'Esta herramienta le permite restaurar el contenido de una base de datos importando toda la información de la copia de seguridad en un archivo ".sql" a un servidor PostgreSQL.'},
'This tool creates a <b>backup</b> file in the "<b>.sql</b>" format for a PostgreSQL server database.' : {'es': 'Esta herramienta crea un archivo <b>copia de seguridad</b> en el formato "<b>.sql</b>" para una base de datos del servidor PostgreSQL.'},
'This tool allows the user to clone any PostgreSQL database. From a model database, another database that has exactly the same (schema and instances) is generated with a new name defined by the operator.' : {'es': 'Esta herramienta permite al usuario clonar cualquier base de datos PostgreSQL. A partir de una base de datos modelo se genera otra base de datos que tiene exactamente lo mismo (esquema e instancias) con un nuevo nombre definido por el operador.'},
'This tool allows you to delete / drop any PostgreSQL database.' : {'es': 'Esta herramienta le permite eliminar/eliminar cualquier base de datos PostgreSQL.'},
'This tool allows you to rename a PostgreSQL database.' : {'es': 'Esta herramienta le permite cambiar el nombre de una base de datos PostgreSQL.'},
'This tool allows you to load a raster layer into a PostGIS database.' : {'es': 'Esta herramienta le permite cargar una capa ráster en una base de datos PostGIS.'},
'This tool changes the encoding type of a .sql file. A new file will be created with the user-defined encoding.' : {'es': 'Esta herramienta cambia el tipo de codificación de un archivo .sql. Se creará un nuevo archivo con la codificación definida por el usuario.'},
'Exports any 8 bit RGB or RGBA raster layer as a JPEG file. Ideal for reducing the size of the output file. It performs a lossy JPEG compression that, in general, the loss of quality goes unnoticed visually.' : {'es': 'Exporta cualquier capa ráster RGB o RGBA de 8 bits como un archivo JPEG. Ideal para reducir el tamaño del archivo de salida. Realiza una compresión JPEG con pérdida que, por lo general, la pérdida de calidad pasa desapercibida visualmente.'},
'Creates a binarized raster, dividing the input raster into two distinct classes from statistical data (lower and upper threshold) from area or point samples. Optionally, minimum and maximum threshold values can also be set.' : {'es': 'Crea un ráster binario, dividiendo el ráster de entrada en dos clases distintas a partir de datos estadísticos (umbral inferior y superior) de muestras de área o puntos. Opcionalmente, también se pueden establecer valores de umbral mínimo y máximo.'},
'A class matches the values within the range of thresholds, where the value 1 (true) is returned. The other class corresponds to values outside the range, returning the value 0 (false).' : {'es': 'Una clase coincide con los valores dentro del rango de umbrales, donde se devuelve el valor 1 (verdadero). La otra clase corresponde a valores fuera del rango, devolviendo el valor 0 (falso).'},
'This tool aims to create an Overviews file (.ovr). This algorithm has the advantage of applying a JPEG compression at each level, greatly reducing the generated file size.' : {'es': 'Esta herramienta tiene como objetivo crear un archivo de descripción general (.ovr). Este algoritmo tiene la ventaja de aplicar una compresión JPEG en cada nivel, reduciendo en gran medida el tamaño del archivo generado.'},
'This tool estimates the value of the points from Raster, making the proper interpolation of the nearest pixels (cells).' : {'es': 'Esta herramienta estima el valor de los puntos de Raster, realizando la interpolación adecuada de los píxeles (celdas) más cercanos.'},
'This tool separates drone photographs into new folders to be processed by blocks, from a layer of polygons (blocks) and from layers of geotagged photographs.' : {'es': 'Esta herramienta separa las fotografías tomadas por drones en nuevas carpetas para ser procesadas por bloques, desde una capa de polígonos (bloques) y desde capas de fotografías geoetiquetadas.'},
'This tool makes it possible to copy or move files to a new folder from a point layer with file paths.' : {'es': 'Esta herramienta permite copiar o mover archivos a una nueva carpeta desde una capa de puntos con rutas de archivo.'},
'Generate text file with Ground Control Points (GCP) from a point layer to WebODM.' : {'es': 'Generar archivo de texto con Puntos de Control Terrestre (GCP) desde una capa de puntos para WebODM.'},
'Generate text file with Ground Control Points (GCP) from a point layer to CloudCompare.' : {'es': 'Generar archivo de texto con Puntos de Control Terrestre (GCP) desde una capa de puntos para CloudCompare.'},
'This tool performs the vertical adjustment of Digital Elevation Models (DEM) from Ground Control Points (GCP).' : {'es': 'Esta herramienta realiza el ajuste vertical de Modelos Digitales de Elevación (DEM) desde Puntos de Control Terrestre (GCP).'},
'This tool applies the filtering technique in the Raster pixel by pixel, based on the gray level values of neighboring pixels.' : {'es': 'Esta herramienta aplica la técnica de filtrado en el Raster píxel a píxel, en función de los valores del nivel de gris de los píxeles vecinos.'},
'The filtering process is done using matrices called masks (or kernel), which are applied to the image.' : {'es': 'El proceso de filtrado se realiza mediante matrices llamadas máscaras (o kernel), que se aplican a la imagen.'},
'This tool generates a layer of points with <b>Spot Elevations</b> from a <b>Digital Terrain Model</b> and a vector layer of <b>contour lines</b>.' : {'es': 'Esta herramienta genera una capa de puntos con <b>Elevaciones puntuales</b> a partir de un <b>Modelo digital de terreno</b> y una capa vectorial de <b>líneas de contorno</b>.'},
'This tool orients the geometry of polygon-like features clockwise or counterclockwise, defining the first vertex as the north, south, east, or west.' : {'es': 'Esta herramienta orienta la geometría de entidades tipo polígono en sentido horario o antihorario, definiendo el primer vértice como norte, sur, este u oeste.'},
"This algorithm fills in the attributes of a specific field from another layer, in such a way that the feature's centroid intercepts the corresponding feature from the other layer." : {'es': 'Este algoritmo completa los atributos de un campo específico de otra capa, de tal manera que el centroide de la entidad intercepta la entidad correspondiente de la otra capa.'},
'The source and destination fields must be indicated to fill in the attributes.' : {'es': 'Se deben indicar los campos de origen y destino para completar los atributos.'},
'Converts the red, green, and blue values of an RGB image to Hue (H), Saturation (S), and Value (V) images.' : {'es': 'Convierte los valores de rojo, verde y azul de una imagen RGB en imágenes de Tono (H), Saturación (S) y Valor (V).'},
'This tool fills in a numeric attribute following a geographic criterion, for example: from north to south and west to east.' : {'es': 'Esta herramienta completa un atributo numérico siguiendo un criterio geográfico, por ejemplo: de norte a sur y de oeste a este.'},
'Note: This algorithm uses the feature centroid to sort geographically.' : {'es': 'Nota: Este algoritmo utiliza el centroide de entidades para ordenar geográficamente.'},
'Generates front lot lines from a polygon layer of parcels.' : {'es': 'Genera líneas frontales de lote a partir de una capa poligonal de parcelas.'},
'This tool returns the central tendency point(s) for clustering points of entry points.' : {'es': 'Esta herramienta devuelve los puntos de tendencia central para los puntos de agrupación de puntos de entrada.'},
'Performs the reconstitution of a Deed Description using Regular Expressions (RegEx).' : {'es': 'Realiza la reconstitución de una Descripción de Escritura utilizando Expresiones Regulares (RegEx).'},
'This tool assigns a sequential value to connected line features based on their topological order. It is ideal for mapping drainage networks, road segments, pipelines, irrigation systems, or any linear vector structure where directional order matters. Users can define the sequence direction (forward, reverse, or both), group by an attribute field, and set a spatial tolerance for node connection. The result is written directly to the layer in custom fields.' : {'es': 'Esta herramienta permite asignar un valor secuencial a entidades lineales conectadas, según su orden topológico. Es ideal para aplicaciones en redes de drenaje, sistemas de riego, carreteras, tuberías u otras estructuras lineales donde la secuencia tenga importancia. El usuario puede definir la dirección de la numeración (hacia adelante, hacia atrás o ambas), agrupar por un campo de atributo y ajustar la tolerancia espacial para la conexión entre vértices. El resultado se guarda directamente en la capa, en campos personalizados.'},
'This tool generates a polygon layer from a point layer and its filled order (sequence) attributes.' : {'es': 'Esta herramienta genera una capa de polígono a partir de una capa de puntos y sus atributos de orden (secuencia) rellenos.'},
'This tool generates a polygon layer from a connected line layer.' : {'es': 'Esta herramienta genera una capa de polígono a partir de una capa de líneas conectadas.'},
'Measures the degree to which features are concentrated or dispersed around the geometric mean center.' : {'es': 'Mide el grado en que las entidades se concentran o dispersan alrededor del centro de la media geométrica.'},
'This tool performs the horizontal and vertical adjustment of Cloud of Points in (TXT) format using LineStringZ vectors.' : {'es': 'Esta herramienta realiza el ajuste horizontal y vertical de Nube de Puntos en formato (TXT) utilizando vectores LineStringZ.'},
'This tool exports a Digital Elevation Model (DEM) as a text file (txt) for later transformation into a point cloud.' : {'es': 'Esta herramienta exporta un Modelo de Elevación Digital (DEM) como un archivo de texto (txt) para su posterior transformación en una nube de puntos.'},
'Optionally, the associated Orthomosaic RGB colors can be taken to the text file.' : {'es': 'Opcionalmente, los colores RGB del Ortomosaico asociados se pueden llevar al archivo de texto.'},
'Generates adjoiner lines from a polygon layer of parcels.' : {'es': 'Genera líneas adyacentes a partir de una capa poligonal de parcelas.'},
'This tool performs the difference between two Digital Elevation Models (DEM).' : {'es': 'Esta herramienta realiza la diferencia entre dos Modelos Digitales de Elevación (DEM).'},
'Minuend is the raster to be subtracted.' : {'es': 'Minuendo es el ráster que se va a restar.'},
'Subtrahend is the rastar that is subtracting.' : {'es': 'El sustraendo es el ráster que se está restando.'},
'This algorithm calculates statistics for the bands of a raster layer, categorized by zones defined in a polygon type vector layer.' : {'es': 'Este algoritmo calcula estadísticas para las bandas de una capa ráster, categorizadas por zonas definidas en una capa vectorial de tipo polígono.'},
'The values of the raster cells where the pixel center is exactly inside the polygon are considered in the statistics.' : {'es': 'En las estadísticas se consideran los valores de las celdas ráster donde el centro del píxel está exactamente dentro del polígono.'},
'This tool performs histogram matching of the JPEG photo files of one input photo layer relative to another reference photo layer.' : {'es': 'Esta herramienta realiza una comparación de histogramas de los archivos de fotografías JPEG de una capa de fotografías de entrada en relación con otra capa de fotografías de referencia.'},
'This tool matches the histogram of a raster layer in relation to another reference raster layer.' : {'es': 'Esta herramienta hace coincidir el histograma de una capa ráster en relación con otra capa ráster de referencia.'},
'Splits a raster dataset into smaller pieces, by horizontal and vertical tiles.' : {'es': 'Divide un conjunto de datos ráster en partes más pequeñas, mediante mosaicos horizontales y verticales.'},
'Creates new vertices into polygons to ensure perfect connectivity (topology) between two layers.' : {'es': 'Crea nuevos vértices en polígonos para garantizar una conectividad (topología) perfecta entre dos capas.'},
'This tool generates frames in the direction of lines, given the measurements of longitudinal distance, transverse distance and overlapping percentage between frames.' : {'es': 'Esta herramienta genera cuadros en la dirección de las líneas, dadas las medidas de distancia longitudinal, distancia transversal y porcentaje de superposición entre cuadros.'},
'Generates cross sections from a line-type layer.' : {'es': 'Genera secciones transversales a partir de una capa de tipo línea.'},
'This tool exports one or several files in standard text file (ASCII) based on an expression considering the attributes of a layer.' : {'es': 'Esta herramienta exporta uno o varios archivos en formato de texto estándar (ASCII) en base a una expresión considerando los atributos de una capa.'},
"This tool performs a series of topological validations to ensure the correct generation of survey plans and deed description based on GeoOne's <b>TopoGeo</b> and <b>GeoRural</b> models." : {'es': 'Esta herramienta realiza una serie de validaciones topológicas para asegurar la correcta generación de planos topográficos y descripción de escrituración basados ​​en los modelos <b>TopoGeo</b> y <b>GeoRural</b> de GeoOne.'},

'''the starting point for the description of this perimeter.
All coordinates described here are georeferenced to the Geodetic Reference System (GRS) (SGR) <b>[SGR]</b>, and are projected in the system <b>[PROJ]</b>,
from which all azimuths and distances, area and perimeter were calculated.</p>''': {'es': '''el punto de partida para la descripción de este perímetro.
 Todas las coordenadas aquí descritas están georreferenciadas al Sistema de Referencia Geodésica (GRS) (SGR) <b>[SGR]</b>, y se proyectan en el sistema <b>[PROJ]</b>,
 a partir del cual se calcularon todos los acimutes y distancias, área y perímetro.</p>'''},

 '''the last point of this perimeter.
 All coordinates described here are georeferenced to the Geodetic Reference System (GRS) (SGR) <b>[SGR]</b>, and are projected in the system <b>[PROJ]</b>,
 from which all azimuths and distances, area and perimeter were calculated.</p>''': {'es': '''el último punto de este perímetro.
 Todas las coordenadas aquí descritas están georreferenciadas al Sistema de Referencia Geodésica (GRS) (SGR) <b>[SGR]</b>, y se proyectan en el sistema <b>[PROJ]</b>,
 a partir del cual se calcularon todos los acimutes y distancias, área y perímetro.</p>'''},

'''This tool fills in a numeric attribute following a geographic criterion, for example: from north to south and west to east.
Note: This algorithm uses the feature centroid to sort geographically.''': {'es': '''Esta herramienta completa un atributo numérico siguiendo un criterio geográfico, por ejemplo: de norte a sur y de oeste a este.
Nota: Este algoritmo utiliza el centroide de entidades para ordenar geográficamente.'''},

'''This tool exports a Digital Elevation Model (DEM) as a text file (txt) for later transformation into a point cloud.
Optionally, the associated Orthomosaic RGB colors can be taken to the text file.''': {'es': '''Esta herramienta exporta un Modelo de Elevación Digital (DEM) como un archivo de texto (txt) para su posterior transformación en una nube de puntos.
Opcionalmente, los colores RGB de Orthomosaic asociados se pueden llevar al archivo de texto.'''},

'''This tool performs the difference between two Digital Elevation Models (DEM).
Minuend is the raster to be subtracted.
Subtrahend is the rastar that is subtracting.''': {'es': '''Esta herramienta realiza la diferencia entre dos Modelos Digitales de Elevación (DEM).
Minuendo es el ráster que se va a restar.
El sustraendo es el ráster que se está restando.'''},

'''This tool applies the filtering technique in the Raster pixel by pixel, based on the gray level values of neighboring pixels.
The filtering process is done using matrices called masks (or kernel), which are applied to the image.''': {'es': '''Esta herramienta aplica la técnica de filtrado en el Raster píxel a píxel, en función de los valores del nivel de gris de los píxeles vecinos.
El proceso de filtrado se realiza mediante matrices llamadas máscaras (o kernel), que se aplican a la imagen.'''},


'''Calculates the sigmax, sigmay and sigmaz precisions (when available) of the closest points to each reference point considering a maximum distance or a minimum number of closest points.
Output: Multipoint layer with positional accuracies in meters and other statistics.
1) Max distance: get all points within the distance.
2) Minimum quantity: get all the closest points, regardless of the maximum distance.
3) Maximum distance and minimum quantity: get only the closest points that are within the maximum distance.''': {'es': '''Calcula las precisiones sigmax, sigmay y sigmaz (cuando estén disponibles) de los puntos más cercanos a cada punto de referencia considerando una distancia máxima o un número mínimo de puntos más cercanos.
Salida: Capa multipunto con precisiones posicionales en metros y otras estadísticas.
1) Distancia máxima: obtén todos los puntos dentro de la distancia.
2) Cantidad mínima: consigue todos los puntos más cercanos, independientemente de la distancia máxima.
3) Distancia máxima y cantidad mínima: obtenga solo los puntos más cercanos que estén dentro de la distancia máxima.'''},

'''This tool returns the central tendency point(s) for clustering points of entry points.
The following statistics can be obtained by grouping:
◼️ <b>Mean Center</b>: calculation of the average in X and Y
◼️ <b>Median Center</b>: calculation of the median in X and Y (less influenced by outliers)
◼️ <b>Central Feature</b>: identification of the central feature (smallest Euclidean distance)
Note: Layer in a projected SRC gets more accurate results.''': {'es': '''Esta herramienta devuelve los puntos de tendencia central para agrupar puntos de puntos de entrada.
Las siguientes estadísticas se pueden obtener agrupando:
◼️ <b>Centro medio</b>: cálculo del promedio en X e Y
◼️ <b>Centro de la mediana</b>: cálculo de la mediana en X e Y (menos influenciado por valores atípicos)
◼️ <b>Entidad central</b>: identificación de la entidad central (distancia euclidiana más pequeña)
Nota: La capa en un SRC proyectado obtiene resultados más precisos.'''},

'''Loads a GNSS processing POS file (.pos) as a point layer.
Compatibility: RTKLIB and IBGE-PPP.
Types:
◼️ All processed points
◼️ Last point
For relative solutions (RTK/PPK), base station standard deviations can be informed to propagate the rover coordinate precisions. Use this option when the base coordinates are not error-free.'''
: {'es': '''Carga un archivo POS (.pos) de procesamiento GNSS como una capa de puntos.
Compatibilidad: RTKLIB e IBGE-PPP.
Tipos:
◼️ Todos los puntos procesados
◼️ Último punto
Para posicionamiento relativo (RTK/PPK), las desviaciones estándar de la estación base pueden utilizarse para propagar las precisiones de las coordenadas del rover.'''},

'''It finds the central points (vertices) of the concentrations of points surveyed by the Kinematic method (stop and go) from the processing of GNSS data.
Input data:
◼️ GNSS point layer from RTKLIB or IBGE-PPP from .pos file
◼️ Minimum time to survey the point in minutes
◼️ Tolerance in centimeters to consider the static point''': {'es': '''Encuentra los puntos centrales (vértices) de las concentraciones de puntos levantados por el método Cinemático (stop and go) a partir del procesamiento de datos GNSS.
Datos de entrada:
◼️ Capa de puntos GNSS de RTKLIB o IBGE-PPP desde un archivo .pos
◼️ Tiempo mínimo para inspeccionar el punto en minutos
◼️ Tolerancia en centímetros para considerar el punto estático'''},

'''Loads a NMEA file (protocol 0183) from GNSS receivers as a point layer.
Modes:
◼️ Kinematic - generates all tracked points with their accuracies (PDOP, HDOP and VDOP) and number of satellites.
◼️ Static - calculates the mean and standard deviation of the observed points, for all points or only for fixed solution points (best result).''': {'es': '''Carga un archivo NMEA (protocolo 0183) desde receptores GNSS como una capa de puntos.
Modos:
◼️ Cinemática: genera todos los puntos rastreados con sus precisiones (PDOP, HDOP y VDOP) y número de satélites.
◼️ Estático: calcula la media y la desviación estándar de los puntos observados, para todos los puntos o solo para los puntos de solución fijos (mejor resultado).'''},


'''This tool changes the encoding type of a .sql file. A new file will be created with the user-defined encoding.
In some cases, this is a possible solution  to transfer data between different operating systems, for example from Windows to Linux, and vice versa.''': {'es': '''Esta herramienta cambia el tipo de codificación de un archivo .sql. Se creará un nuevo archivo con la codificación definida por el usuario.
En algunos casos, esta es una posible solución para transferir datos entre diferentes sistemas operativos, por ejemplo de Windows a Linux, y viceversa.'''},

'''This tool allows you to rename a PostgreSQL database.
Note: To run this operation, the database must be disconnected. This means, that it must not be opened in any software (PgAdmin, QGIS, etc.).''': {'es': '''Esta herramienta le permite cambiar el nombre de una base de datos PostgreSQL.
Nota: Para ejecutar esta operación, la base de datos debe estar desconectada. Esto significa que no debe abrirse en ningún software (PgAdmin, QGIS, etc.).'''},

'''This tool allows the user to clone any PostgreSQL database. From a model database, another database that has exactly the same (schema and instances) is generated with a new name defined by the operator.
Note: To create more than one "clone", the new database names must be filled and separated by "comma".''': {'es': '''Esta herramienta permite al usuario clonar cualquier base de datos PostgreSQL. A partir de una base de datos modelo se genera otra base de datos que tiene exactamente lo mismo (esquema e instancias) con un nuevo nombre definido por el operador.
Nota: Para crear más de un "clon", los nombres de las nuevas bases de datos deben completarse y separarse por "coma".'''},

'''This tool allows you to delete / drop any PostgreSQL database.
Notes:
- To run this operation, the database must be disconnected. This means, that it must not be opened in any software (PgAdmin, QGIS, etc.).
- To delete more than one database, the names must be filled and separated by "comma".
<p style="color:red;">Attention: This operation is irreversible, so be sure before running it!</p>''': {'es': '''Esta herramienta le permite eliminar cualquier base de datos PostgreSQL.
Notas:
- Para ejecutar esta operación, la base de datos debe estar desconectada. Esto significa que no debe abrirse en ningún software (PgAdmin, QGIS, etc.).
- Para eliminar más de una base de datos, se deben llenar los nombres y separarlos por "coma".
<p style="color:red;">Atención: ¡Esta operación es irreversible, así que asegúrese antes de ejecutarla!</p>'''},

'''Performs an arithmetic operation on the bands of a raster. The predefined formula is used to calculate the Green Leaf Index (GLI) for a RGB raster. However you can enter your own formula.
Examples:
NDVI with RGN raster: ( b3 - b1) / (b3 + b1)
NDWI with RGN raster: ( b2 - b3) / (b2 + b3)
GLI with RGB raster: (2*b2 - b1 - b3) / (2*b2 + b1 + b3)
VARI with RGB raster: (b2 - b1) / (b2 + b1 - b3)
VIgreen with RGB raster: (b2 - b1) / (b2 + b1)
Obs.:
The operators supported are:  + , - , * , /''': {'es': '''Realiza una operación aritmética sobre las bandas de un ráster. La fórmula predefinida se utiliza para calcular el Green Leaf Index (GLI) para un ráster RGB. Sin embargo, puede ingresar su propia fórmula.
Ejemplos:
NDVI con ráster RGN: ( b3 - b1) / (b3 + b1)
NDWI con ráster RGN: ( b2 - b3) / (b2 + b3)
GLI con ráster RGB: (2*b2 - b1 - b3) / (2*b2 + b1 + b3)
VARI con ráster RGB: (b2 - b1) / (b2 + b1 - b3)
VIgreen con ráster RGB: (b2 - b1) / (b2 + b1)
Obs.:
Los operadores admitidos son: + , - , * , /'''},

'''Loads a set of raster files that intersect the geometries of an input vector layer.
Optionally, it is possible to copy the selected rasters and paste them in another folder.''': {'es': '''Carga un conjunto de archivos ráster que intersectan las geometrías de una capa vectorial de entrada.
 Opcionalmente, es posible copiar los rásteres seleccionados y pegarlos en otra carpeta.'''},

 '''This algorithm calculates statistics for the bands of a raster layer, categorized by zones defined in a polygon type vector layer.
The values of the raster cells where the pixel center is exactly inside the polygon are considered in the statistics.''': {'es': '''Este algoritmo calcula estadísticas para las bandas de una capa ráster, categorizadas por zonas definidas en una capa vectorial de tipo polígono.
Los valores de las celdas ráster donde el centro del píxel está exactamente dentro del polígono se consideran en las estadísticas.'''},

'''Creates a binarized raster, dividing the input raster into two distinct classes from statistical data (lower and upper threshold) from area or point samples. Optionally, minimum and maximum threshold values can also be set.
A class matches the values within the range of thresholds, where the value 1 (true) is returned. The other class corresponds to values outside the range, returning the value 0 (false).''': {'es': '''Crea un ráster binario, dividiendo el ráster de entrada en dos clases distintas a partir de datos estadísticos (umbral inferior y superior) de muestras de área o puntos. Opcionalmente, también se pueden establecer valores de umbral mínimo y máximo.
Una clase coincide con los valores dentro del rango de umbrales, donde se devuelve el valor 1 (verdadero). La otra clase corresponde a valores fuera del rango, devolviendo el valor 0 (falso).'''},

'Note: Binary thresholding is one of the easiest and fastest ways to classify an image from an index such as NDVI. This algorithm can be used to identify areas with vegetation cover using an index such as the NDVI (França et al., 2017).': {'es': 'Nota: El umbral binario es una de las formas más fáciles y rápidas de clasificar una imagen a partir de un índice como NDVI. Este algoritmo se puede utilizar para identificar áreas con cobertura vegetal utilizando un índice como el NDVI (França et al., 2017).'},

'''The largest width or height value of the original image is resized to the user-defined value. The short side is scaled proportionately.
Note: The metadata is preserved.''': {'es': '''El valor de ancho o alto más grande de la imagen original cambia de tamaño al valor definido por el usuario. El lado corto tiene una escala proporcional.
 Nota: Los metadatos se conservan."'''},

 '''Creates a KML file embedding in that single file all photographs in base64 textual format to be viewed in Google Earth.
 Images are resized to a new size corresponding to the image's largest side.''': {'es': '''Crea un archivo KML incrustando en ese único archivo todas las fotografías en formato textual base64 para ser visualizadas en Google Earth.
 Las imágenes cambian de tamaño a un nuevo tamaño correspondiente al lado más grande de la imagen.'''},

 '''Note: Sample data obtained from class notes of the Geodetic Survey discipline at UFPE.
''': {'es': '''Nota: Datos de muestra obtenidos de apuntes de clase de la disciplina Levantamiento Geodésico de la UFPE.
'''},

'''Notes: Data collected in the discipline of <i>Geodetic Surveys</i> in the Graduate Program at UFPE, in field work coordinated by <b>Prof. Dr. Andrea de Seixas</b>.
For more information on the methodology used, please read the article at the link below:''': {'es': '''Notas: Datos recopilados en la disciplina de <i>Levantamientos Geodésicos</i> en el Programa de Posgrado de la UFPE, en trabajo de campo coordinado por el <b>Prof. Dra. Andrea de Seixas</b>.
Para obtener más información sobre la metodología utilizada, lea el artículo en el siguiente link:'''},


"""This tool performs the following types of coordinate transformation:
◼️ <b>Translation Transformation</b>: 1 vector without adjustment / 2 or + vectors with adjustment.
◼️ <b>Conformal Transformation (2D Helmert)</b>: 2 vectors without adjustment / 3 or + vectors with adjustment.
◼️ <b>Affine Transformation</b>: 3 vectors without adjustment / 4 or + vectors with adjustment.
With this tool it is possible to perform correctly the georeferencing of vector files in QGIS.
""": {'es': """Esta herramienta realiza los siguientes tipos de transformación de coordenadas:
◼️ <b>Transformación de traslación</b>: 1 vector sin ajuste / 2 o + vectores con ajuste.
◼️ <b>Transformación Conformal (2D Helmert)</b>: 2 vectores sin ajuste / 3 o + vectores con ajuste.
◼️ <b>Transformación Afín</b>: 3 vectores sin ajuste / 4 o + vectores con ajuste.
Con esta herramienta es posible realizar correctamente la georreferenciación de archivos vectoriales en QGIS.
"""},

'''
This algorithm transforms coordinates between the following reference systems:
- geodetic <b>(λ, ϕ, h)</b>;
- geocentric or ECEF <b>(X, Y, Z)</b>; and
- topocentric in a local tangent plane <b>(E, N, U)</b>.
Default values for origin coordinates can be applied to Recife / Brazil.''': {'es': '''
Este algoritmo transforma coordenadas entre los siguientes sistemas de referencia:
- geodésico <b>(λ, ϕ, h)</b>;
- geocéntrico o ECEF <b>(X, Y, Z)</b>; y
- topocéntrico en un plano tangente local <b>(E, N, U)</b>.
Los valores predeterminados para las coordenadas de origen se pueden aplicar a Recife/Brasil.'''},

'''Nota: Dados de exemplo obtidos de Mendonça et al. (2010).
Saiba mais:''': {'es': '''Nota: Dados de ejemplo obtidos de Mendonça et al. (2010).
Saiba más:'''},

'Error in coordinate {}!' : {'es': '¡Error en la coordenada {}!'},
'New CRS defined to zone {} and hemisphere {}.' : {'es': 'Nuevo CRS definido para zona {} y hemisferio {}.'},
'Set CRS in UTM': {'es': 'Establecer SRC en UTM'},
'No active layer found!': {'es': '¡No se encontró ninguna capa activa!'},
'Active layer style successfully copied.': {'es': 'Estilo de la capa activa copiado con éxito.'},
'Copy layer style': {'es': 'Copiar estilo de la capa'},
'No style copied!': {'es': '¡Ningún estilo copiado!'},
'The layers are of different types (raster and vector)!': {'es': '¡Las capas son de tipos diferentes (ráster y vector)!'},
'The vector layers have different geometry types!': {'es': '¡Las capas vectoriales tienen diferentes tipos de geometría!'},
'Style successfully pasted to the destination layer.': {'es': 'Estilo pegado con éxito en la capa de destino.'},
'Paste style to the layer': {'es': 'Pegar estilo en la capa'},
'Tutorials': {'es': 'Tutoriales'},
'This tool allows for the automatic conversion and reprojection of all vector layers present in a GeoPackage (.GPKG) file to a new Coordinate Reference System (CRS) defined by the user. The tool simplifies working with multiple layers while maintaining the integrity of the vector data by reprojecting them in batch.': {'es': 'Esta herramienta permite la conversión y reproyección automática de todas las capas vectoriales presentes en un archivo GeoPackage (.GPKG) a un nuevo Sistema de Referencia de Coordenadas (SRC) definido por el usuario. La herramienta facilita el trabajo con múltiples capas, manteniendo la integridad de los datos vectoriales al reproyectarlos por lotes.'},
'Reproject GeoPackage': {'es': 'Reproyectar GeoPackage'},
'Allow projected CRS': {'es': 'Permitir SRC proyectado'},
'Converting layer {}...': {'es': 'Convirtiendo capa {}...'},
'Only instantiated layers': {'es': 'Solo capas instanciadas'},
'This tool replaces the Z coordinates of an existing layer with the value of the nearest cell from a Digital Elevation Model (DEM).': {'es': 'Esta herramienta reemplaza las coordenadas Z de una capa existente con el valor de la celda más cercana de un Modelo de Elevación Digital (DEM).'},
'Set Z coordinate from DEM': {'es': 'Establecer la coordenada Z desde DEM'},
'Defining Z coordinate...': {'es': 'Definiendo la coordenada Z...'},
'Input layer has no Z dimension': {'es': 'La capa de entrada no tiene dimensión Z'},
'Select by key attribute': {'es': 'Seleccionar por atributo clave'},
'''This tool allows you to select features that share the same foreign key attribute from multiple layers based on the primary key attribute of a selected feature from another layer.
Note: Enter the foreign key field name if it is not the same as the primary key field name.''': {'es': '''Esta herramienta le permite seleccionar entidades que comparten el mismo atributo de clave externa de varias capas en función del atributo de clave principal de una entidad seleccionada de otra capa.
Nota: Introduzca el nombre del campo de clave externa si no es el mismo que el nombre del campo de clave principal.'''},
'Primary key': {'es': 'Clave primaria'},
'Foreign key': {'es': 'Clave externa'},
'Layer {} has no key field!': {'es': '¡La capa {} no tiene campo clave!'},
'Offset': {'es': 'Compensar'},
'Connected layer': {'es': 'Capa conectada'},
'Path {} does not exist!': {'es': '¡La ruta del archivo {} no existe!'},
'Coordinates in Degrees, Minutes, and Seconds (DMS)': {'es': 'Coordenadas en Grados, Minutos y Segundos (GMS)'},
'Estimate azimuth': {'es': 'Estimar el azimut'},
', and are projected in the UTM system, zone [FUSO] and hemisphere [HEMISFERIO], from which all azimuths and distances were calculated.': {'es': ', y están proyectados en el sistema UTM, zona [FUSO] y hemisferio [HEMISFERIO], a partir del cual se calcularon todos los acimutes y distancias.'},
', and are projected in the UTM system, zone [FUSO] and hemisphere [HEMISFERIO]. All azimuths and distances were calculated in the Local Tangent Plane (LTP), having as origin the centroid and average altitude of the perimeter.': {'es': ', y están proyectados en el sistema UTM, zona [FUSO] y hemisferio [HEMISFERIO]. Todos los acimutes y distancias se calcularon en el Plano Tangente Local (LTP), teniendo como origen el centroide y la altitud media del perímetro.'},
'. All azimuths and distances were calculated from the projected coordinates in UTM, zone [FUSO] and hemisphere [HEMISPHERE].': {'es': '. Todos los acimutes y distancias se calcularon a partir de las coordenadas proyectadas en UTM, zona [FUSO] y hemisferio [HEMISFERIO].'},
'. All azimuths and distances were calculated in the Local Tangent Plane (LTP), having as origin the centroid and average altitude of the perimeter.': {'es': '. Todos los acimutes y distancias se calcularon en el Plano Tangente Local (LTP), teniendo como origen el centroide y la altitud media del perímetro.'},
', and are projected in the UTM system, zone [FUSO] and hemisphere [HEMISFERIO]. The azimuths were calculated using the Inverse Geodetic Problem formula according to Puissant, and the distances were calculated in the Local Tangent Plane (LTP) having as origin the centroid and average altitude of the perimeter.': {'es': ', y están proyectados en el sistema UTM, zona [FUSO] y hemisferio [HEMISFERIO]. Los acimutes se calcularon utilizando la fórmula del Problema Geodésico Inverso según Puissant, y las distancias se calcularon en el Plano Tangente Local (LTP), teniendo como origen el centroide y la altitud media del levantamiento del perímetro.'},
'. The azimuths were calculated using the Inverse Geodetic Problem formula according to Puissant, and the distances were calculated in the Local Tangent Plane (LTP) having as origin the centroid and average altitude of the perimeter.': {'es': '. Los acimutes se calcularon utilizando la fórmula del Problema Geodésico Inverso según Puissant, y las distancias se calcularon en el Plano Tangente Local (LTP), teniendo como origen el centroide y la altitud media del perímetro.'},
'Interior angle lines': {'es': 'Líneas de ángulos interiores'},
'Exterior angle lines': {'es': 'Líneas de ángulos exteriores'},
'Angle line outside polygon bounds! Reduce radius size (distance).': {'es': '¡Línea angular fuera de los límites del polígono! Reducir el radio (distancia).'},
' {} inconsistencies detected ({} topological errors and {} structural geometry errors)!': {'es': ' ¡Se detectaron {} inconsistencias ({} errores topológicos y {} errores estructurales de geometría)!'},
' Congratulations! No topological inconsistency was detected.': {'es': ' ¡Enhorabuena! No se encontró ninguna inconsistencia topológica.'},
'Make sure the canvas extent is valid for a UTM projection!' : {'es': '¡Asegúrese de que la extensión del lienzo sea válida para una proyección UTM!'},
'Test Points' : {'es': 'Puntos de prueba'},
'Reference Points' : {'es': 'Puntos de referencia'},
'Name Field' : {'es': 'Campo de nombre'},
'3D Planialtimetric Discrepancies' : {'es': 'Discrepancias planialtimétricas 3D'},
'Decimal Places' : {'es': 'Decimales'},
'3D Planialtimetric Accuracy Report' : {'es': 'Informe de Exactitud Planialtimétrica 3D'},
'PLANIALTIMETRIC POSITIONAL ACCURACY' : {'es': 'Precisión posicional planialtimétrica'},
'PLANIMETRIC POSITIONAL ACCURACY' : {'es': 'Precisión posicional planialtimétrica'},
'VERTICAL POSITIONAL ACCURACY' : {'es': 'Precisión posicional altimétrica'},
'PLANIALTIMETRIC POSITIONAL ACCURACY REPORT (3D)' : {'es': 'Informe de precisión posicional planialtimétrica (3D)'},
'EVALUATED DATA' : {'es': 'DATOS EVALUADOS'},
'Discrepancy Vectors' : {'es': 'Vectores de discrepancia'},
'Total Pairs of Homologous Points' : {'es': 'Total de pares de puntos homólogos'},
'X Discrepancies' : {'es': 'Discrepancias X'},
'Y Discrepancies' : {'es': 'Discrepancias Y'},
'Z Discrepancies' : {'es': 'Discrepancias Z'},
'average (tendency)' : {'es': 'Promedio (tendencia)'},
'standard deviation (precision)' : {'es': 'Desviación estándar (precisión)'},
'maximum' : {'es': 'Máximo'},
'minimum' : {'es': 'Mínimo'},
'maximum discrepancy' : {'es': 'Discrepancia máxima'},
'minimum discrepancy' : {'es': 'Discrepancia mínima'},
'Cartographic Accuracy Standard' : {'es': 'Estándar de precisión cartográfica'},
'Vector lines' : {'es': 'Líneas vectoriales'},
'2D Planimetric Discrepancies' : {'es': 'Discrepancias planimétricas 2D'},
'Insufficient number of features for quality evaluation!' : {'es': '¡Número insuficiente de entidades para la evaluación de calidad!'},
'The number of features must be the same in both layers!' : {'es': '¡El número de entidades debe ser el mismo en ambas capas!'},
'The test and reference layers must be distinct!' : {'es': '¡Las capas de prueba y de referencia deben ser distintas!'},
'Define a projected CRS for the calculations!' : {'es': '¡Defina un CRS proyectado para los cálculos!'},
'Planimetric calculation...' : {'es': 'Cálculo planimétrico...'},
'Altimetric calculation...' : {'es': 'Cálculo altimétrico...'},
'Generating accuracy report...' : {'es': 'Generando informe de precisión...'},
'PLANIMETRIC POSITIONAL ACCURACY REPORT (2D)' : {'es': 'INFORME DE PRECISIÓN POSICIONAL PLANIMÉTRICA (2D)'},
'Check points' : {'es': 'Puntos de control'},
'Reference altitude' : {'es': 'Altitud de referencia'},
'Distance to filter nearest points (m)' : {'es': 'Distancia para filtrar los puntos más cercanos (m)'},
'Point Cloud Discrepancies' : {'es': 'Discrepancias en la nube de puntos'},
'Accuracy Report of the Point Cloud' : {'es': 'Informe de precisión de la nube de puntos'},
'Filtering nearest points...' : {'es': 'Filtrando los puntos más cercanos...'},
'Point Cloud positional accuracy' : {'es': 'Precisión posicional de la nube de puntos'},
'Vertical positional accuracy' : {'es': 'Precisión posicional vertical'},
'Horizontal positional accuracy' : {'es': 'Precisión posicional horizontal'},
'3D positional accuracy' : {'es': 'Precisión posicional 3D'},
'POINT CLOUD POSITIONAL ACCURACY' : {'es': 'PRECISA POSICIONAL DE LA NUBE DE PUNTOS'},
'DEM Discrepancies' : {'es': 'Discrepancias del DEM'},
'Accuracy Report of the DEM' : {'es': 'Informe de precisión del DEM'},
'DEM POSITIONAL ACCURACY' : {'es': 'PRECISA POSICIONAL DEL DEM'},
'A tool that streamlines the download of Digital Elevation Models (DEMs), allowing the user to define the area of interest directly in QGIS. It supports access to FABDEM and other modern DEMs, automatically generating the exact clipped extent for immediate use in your projects.': {'es': 'Herramienta que simplifica la descarga de Modelos Digitales de Elevación (MDE), permitiendo al usuario definir el área de interés directamente en QGIS. Admite el acceso a FABDEM y a otros MDEs modernos, generando automáticamente el recorte exacto de la extensión seleccionada para su uso inmediato en los proyectos.'},
'DEM Downloader': {'es': 'Descargador de MDE'},
'Define a smaller extent on the map!': {'es': '¡Define una extensión más pequeña en el mapa!'},
'No raster was downloaded!': {'es': '¡Ningún ráster fue descargado!'},
'Problem downloading': {'es': 'Problema al descargar'},
'Downloading file': {'es': 'Descargando archivo'},
'''This tool automatically <b>applies cartographic styles</b> to your QGIS vector layers — as if by magic.
It turns points, lines, and polygons into ready-to-use visual representations for professional maps, quickly and effortlessly.''': {'es': '''Esta herramienta <b>aplica estilos</b> cartográficos automáticos a tus capas vectoriales en QGIS, como por arte de magia.
Transforma puntos, líneas y polígonos en representaciones visuales listas para mapas profesionales, de forma rápida y sencilla.'''},
'- Select one style -': {'es': '- Selecciona un estilo -'},
'Dimensioning': {'es': 'Acotación'},
'Distance and Azimuth': {'es': 'Distancia y Azimut'},
'Equirectangular to Cubemap': {'es': 'Equirectangular a Cubemap'},
'''Converts a 360° image in equirectangular format into six images corresponding to the faces of a cube (cubemap).
The tool automatically creates a folder next to the original file and saves the faces using the original filename plus the face suffix (+X, −X, +Y, −Y, +Z, −Z).
These images can be opened in external editors for tasks such as anonymization, blurring, fixing artifacts near the poles, or inserting additional information.

The face resolution can be defined by the user, allowing a balance between performance and visual quality.''': {'es': '''Convierte una imagen 360° en formato equirectangular en seis imágenes que corresponden a las caras de un cubo (cubemap).
La herramienta crea automáticamente una carpeta junto al archivo original y guarda las caras usando el nombre del archivo seguido del sufijo de la cara (+X, −X, +Y, −Y, +Z, −Z).
Estas imágenes pueden abrirse en editores externos para tareas como anonimización, desenfoque, correcciones en los polos o inserción de información adicional.
La resolución de las caras puede ser definida por el usuario, permitiendo elegir entre rendimiento y calidad visual.'''},
'Equirectangular image (360°)': {'es': 'Imagen equirectangular (360°)'},
'Face resolution (N × N)': {'es': 'Tamaño de cada imagen generada del cubo'},
'Cubemap to Equirectangular': {'es': 'Cubemap a Equirectangular'},
'''Rebuilds a 360° equirectangular image from the six faces of a cubemap.
The tool reads the face images (+X, −X, +Y, −Y, +Z, −Z), recomposes the panorama, and produces a new image in standard equirectangular format.
Useful for returning to 360° format after editing, anonymization, or adding information directly on the cube faces.
When available, EXIF metadata from the original image can be reapplied to preserve GPS data and compatibility with 360° viewers.''': {'es': '''Reconstruye una imagen 360° en formato equirectangular a partir de las seis caras de un cubemap.
La herramienta lee las caras (+X, −X, +Y, −Y, +Z, −Z), recompone el panorama y genera una nueva imagen en formato equirectangular estándar.
Útil para volver al formato 360° después de procesos de edición, anonimización o inserción de información en las caras del cubo.
Cuando sea posible, los metadatos EXIF de la imagen original pueden aplicarse nuevamente para mantener los datos de GPS y la compatibilidad con visualizadores 360°.'''},
'Cubemap faces folder': {'es': 'Carpeta con las caras del cubemap'},
'Image Height (H)': {'es': 'Altura de la imagen (H)'},
'Original equirectangular image': {'es': 'Imagen equirectangular original'},
'Rebuilt 360° Image': {'es': 'Imagen 360° reconstruida'},
'Enroll in the 360° VR course in QGIS': {'es': 'Inscríbete en el curso de RV 360° en QGIS'},
'Click here to watch a full class on this tool': {'es': 'Haz clic aquí para ver una clase completa sobre esta herramienta'},
'Simple Camera': {'es': 'Cámara simple'},
'Layer Style': {'es': 'Estilo de capa'},
'intermediate contours': {'es': 'curvas de nivel intermedias'},
'index contours': {'es': 'curvas de nivel maestras'},
'List of Directions (Azimuths or Bearings)': {'es': 'Lista de Direcciones (Azimutes o Rumbos)'},
'''Calculation of points or a line from a set of horizontal <b>distances</b> and <b>directions.</b>
    <p>
      Directions can be entered as:
    </p>
    <ul>
      <li><b>Azimuths</b> (0–360°, in decimal or DMS format), e.g.:<br>
          <code>34°12'43.2"</code>, <code>165.25</code>
      </li>
      <li><b>Quadrant bearings</b> (rumo + quadrant/direction), e.g.:<br>
          <code>34°12'43.2" NE</code>, <code>N 34°12'43.2" E</code>, <code>47°33'15.3" SE</code>
      </li>
    </ul>
    <p>
      Both formats can be mixed in the same list of directions. Bearings are automatically converted to azimuths for the traverse computation.
    </p>
    ''': {'es': '''Cálculo de puntos o de una línea a partir de un conjunto de <b>distancias</b> y <b>direcciones</b> horizontales.
<p>
  Las direcciones se pueden introducir como:
</p>
<ul>
  <li><b>Azimuts</b> (0–360°, en formato decimal o DMS), por ejemplo:<br>
      <code>34°12'43.2"</code>, <code>165.25</code>
  </li>
  <li><b>Rumbos en cuadrantes</b> (rumbo + cuadrante/dirección), por ejemplo:<br>
      <code>34°12'43.2" NE</code>, <code>N 34°12'43.2" E</code>, <code>47°33'15.3" SE</code>
  </li>
</ul>
<p>
  Ambos formatos pueden mezclarse en la misma lista de direcciones. Los rumbos se convierten automáticamente en azimuts para el cálculo de la poligonal.
</p>
'''},
'Sign up for the WebODM and QGIS course': {'es': 'Inscríbete en el curso de WebODM y QGIS.'},
'Sign up for the GNSS with RTKLib and QGIS course': {'es': 'Inscríbete en el curso GNSS con RTKLib y QGIS'},
"Sign up for GeoOne's PostGIS course": {'es': 'Inscríbete en el curso PostGIS de GeoOne'},
'Sign up for the Remote Sensing in QGIS course': {'es': 'Inscríbete en el curso de Teledetección en QGIS'},
'Extract Perspective View': {'es': 'Extraer Vista en Perspectiva'},
'Extracts a perspective (pinhole) image from a 360° equirectangular image, simulating the framing of a conventional camera oriented toward a specified viewing direction.': {'es': 'Extrae una imagen en proyección perspectiva (pinhole) a partir de una imagen 360° en formato equirectangular, simulando el encuadre de una cámara convencional orientada hacia una dirección específica del espacio.'},
'Perspective center – latitude': {'es': 'Centro de la perspectiva – latitud'},
'Perspective center – longitude': {'es': 'Centro de la perspectiva – longitud'},
'Horizontal field of view (°)': {'es': 'ampo de visión horizontal (°)'},
'Output image width (pixels)': {'es': 'Ancho de la imagen de salida (píxeles)'},
'Output image height (pixels)': {'es': 'Altura de la imagen de salida (píxeles)'},
'Camera roll (°)': {'es': 'Rotación de la cámara (roll) (°)'},
'Perspective view image': {'es': 'Imagen de vista perspectiva'},
'Spot elevation': {'es': 'Cota puntual'},
'Export Flight Area to DJI KML': {'es': 'Exportar área de vuelo a KML de DJI'},
'''Exports polygon features to a simplified KML compatible with DJI flight controllers.
            Multipart geometries are reduced to the first polygon part, interior rings are removed, and the output is automatically transformed to WGS84 (EPSG:4326).''': {'es': '''Exporta entidades poligonales a un KML simplificado compatible con los controles de vuelo de DJI. 
                                                                                                                                                                           Las geometrías multiparte se reducen a la primera parte del polígono, los anillos interiores se eliminan y la salida se transforma automáticamente a WGS84 (EPSG:4326).'''},
'Polygon Layer':{'es': 'Capa de polígonos'},
'DJI-Compatible KML': {'es':'KML compatible con DJI'},
'The input layer has no features!': {'es': '¡La capa de entrada no tiene entidades!'},
'''Generate a <b>TXT file with Ground Control Points (GCP)</b> from a <b>point layer</b><br> for import into <b>Agisoft Metashape</b>.
<p>
  <b>Output format:</b>
  <code>Name, X, Y, Z, X_error, Y_error, Z_error</code>
</p>
<p>
  <b>Notes:</b>
</p>
  - <b>X</b> and <b>Y</b> coordinates are obtained from the <b>point geometry</b>.
  - <b>Z</b> values can be obtained from a <b>field</b> or from the <b>3D geometry</b> of the layer.
  - If no <b>Z field</b> is provided and the geometry has no <b>Z value</b>, the <b>Z coordinate</b> will be set to <b>0</b>.
  - For best results in <b>Agisoft Metashape</b>, use <b>projected coordinate systems</b>.
''': {'es': '''Genera un <b>archivo TXT con Puntos de Control en Tierra (GCP)</b> a partir de una <b>capa de puntos</b><br> para su importación en <b>Agisoft Metashape</b>.
<p>
  <b>Formato de salida:</b>
  <code>Name, X, Y, Z, X_error, Y_error, Z_error</code>
</p>
<p>
  <b>Notas:</b>
</p>
  - Las coordenadas <b>X</b> y <b>Y</b> se obtienen de la <b>geometría del punto</b>.<br>
  - Los valores <b>Z</b> pueden obtenerse de un <b>campo</b> o de la <b>geometría 3D</b> de la capa.<br>
  - Si no se proporciona un <b>campo Z</b> y la geometría no tiene <b>valor Z</b>, la <b>coordenada Z</b> se establecerá en <b>0</b>.<br>
  - Para obtener mejores resultados en <b>Agisoft Metashape</b>, utilice <b>sistemas de coordenadas proyectados</b>.'''},
'No valid observations found!': {'es': '¡No se encontraron observaciones válidas!'},
'Select a Raster Layer Style!': {'es': '¡Selecciona un estilo de capa ráster!'},
'Elevation': {'es': 'Elevación'},
'No style': {'es': 'Sin estilo'},
'Symbology': {'es': 'Simbología'},
'Light Geometry Cleanup': {'es': 'Limpieza Geométrica Ligera'},
'''
This tool performs a light geometric cleanup directly on the input layer.

It:
- removes features with null or empty geometries directly from the original layer;
- records the deleted feature IDs in the processing log;
- exports the attributes of removed features to a no-geometry table;
- removes duplicate vertices for line and polygon features.

Note: Invalid geometries are not fixed or deleted by this tool.
''': {'es': '''Esta herramienta realiza una limpieza geométrica ligera directamente sobre la capa de entrada.

Permite:
- eliminar de la capa original las entidades con geometrías nulas o vacías;
- registrar en el log de procesamiento los IDs de las entidades eliminadas;
- exportar los atributos de las entidades eliminadas a una tabla sin geometría;
- eliminar vértices duplicados en entidades de tipo línea y polígono.

Nota: Las geometrías inválidas no son corregidas ni eliminadas por esta herramienta.'''},
'Output table of removed features': {'es': 'Tabla de salida de entidades eliminadas'},
'Could not create output table.':{'es': 'No se pudo crear la tabla de salida.'},
'No features to process.': {'es': 'No hay entidades para procesar.'},
'Starting light geometry cleanup...': {'es': 'Iniciando limpieza geométrica ligera...'},
'Checking for null or empty geometries...': {'es': 'Verificando geometrías nulas o vacías...'},
'null geometry': {'es': 'geometría nula'},
'empty geometry': {'es': 'geometría vacía'},
'Deleted feature ID {} ({})': {'es': 'Entidad ID {} eliminada ({})'},
'Could not delete null/empty geometry features.': {'es': 'No se pudieron eliminar las entidades con geometría nula/vacía.'},
'{} feature(s) removed due to null or empty geometry.': {'es': '{} entidad(es) eliminada(s) por geometría nula o vacía.'},
'Duplicate vertices removed from feature ID {}': {'es': 'Vértices duplicados eliminados de la entidad ID {}'},
'{} feature(s) had duplicate vertices removed.': {'es': '{} entidad(es) tuvieron vértices duplicados eliminados.'},
'Duplicate vertex cleanup skipped (only applies to line and polygon layers).': {'es': 'La eliminación de vértices duplicados fue omitida (solo aplica a capas de líneas y polígonos).'},
'Could not save layer edits.': {'es': 'No se pudieron guardar las ediciones de la capa.'},
'Edits were kept in edit mode and not committed.': {'es': 'Las ediciones se mantuvieron en modo de edición y no fueron guardadas.'},
'Invalid X/longitude coordinate: {}': {'es': 'Coordenada X/longitud inválida: {}'},
'Invalid Y/latitude coordinate: {}': {'es': 'Coordenada Y/latitud inválida: {}'},
'Invalid CRS selected!': {'es': '¡SRC seleccionado inválido!'},
'Applies RTK base correction using post-processed coordinates (e.g., PPP) by computing a geocentric translation vector and applying it to all rover points. Optionally propagates positional uncertainties and provides results in both geocentric and local topocentric (E, N, U) systems.': {'es': 'Aplica la corrección de la base RTK utilizando coordenadas posprocesadas (por ejemplo, PPP), mediante el cálculo de un vector de traslación geocéntrico aplicado a todos los puntos rover. Opcionalmente realiza la propagación de incertidumbres posicionales y proporciona resultados en sistemas geocéntrico y topocéntrico local (E, N, U).'},
'Initial X,Y,Z coordinates of the base': {'es': 'Coordenadas X,Y,Z iniciales de la base'},
'Post-processed X,Y,Z coordinates of the base': {'es': 'Coordenadas X,Y,Z posprocesadas de la base'},
'Base CRS': {'es': 'SRC de la base'},
'Base Sigma X (m) - East': {'es': 'Sigma de la base X (m) - Este'},
'Base Sigma Y (m) - North': {'es': 'Sigma de la base Y (m) - Norte'},
'Base Sigma Z (m) - Up': {'es': 'Sigma de la base Z (m) - Altura'},
'Rover Sigma X (m) - East': {'es': 'Sigma del rover X (m) - Este'},
'Rover Sigma Y (m) - North': {'es': 'Sigma del rover Y (m) - Norte'},
'Rover Sigma Z (m) - Up': {'es': 'Sigma del rover Z (m) - Altura'},
'Invalid {} WKT: {}': {'es': 'WKT inválido para {}: {}'},
'{} must be a PointZ geometry: {}': {'es': '{} debe ser una geometría PointZ: {}'},
'Invalid Z coordinate in {}: {}': {'es': 'Coordenada Z inválida en {}: {}'},
'To propagate variances, all base and rover sigmas must be filled in (X, Y and Z).': {'es': 'Para propagar las varianzas, todos los sigmas de la base y del rover deben completarse (X, Y y Z).'},
'Feature ID {} has null/empty rover sigma values.': {'es': 'La entidad ID {} tiene valores de sigma del rover nulos/vacíos.'},
'Feature ID {} has invalid rover sigma values.': {'es': 'La entidad ID {} tiene valores de sigma del rover inválidos.'},
'Feature ID {} has {} greater than {} m.': {'es': 'La entidad ID {} tiene {} mayor que {} m.'},
'Base correction above expected value. Check the initial and final base coordinates!': {'es': 'Corrección de la base por encima del valor esperado. ¡Verifique las coordenadas inicial y final de la base!'},
'Topocentric delta E: {:.4f} m': {'es': 'Delta topocéntrico en E: {:.4f} m'},
'Topocentric delta N: {:.4f} m': {'es': 'Delta topocéntrico en N: {:.4f} m'},
'Topocentric delta U: {:.4f} m': {'es': 'Delta topocéntrico en U: {:.4f} m'},
'Topocentric horizontal delta: {:.4f} m': {'es': 'Delta horizontal topocéntrico: {:.4f} m'},
'Generating HTML report...': {'es': 'Generando informe HTML...'},
'RTK POINTS CORRECTION REPORT': {'es': 'INFORME DE CORRECCIÓN DE PUNTOS RTK'},
'PROCESSING DATA': {'es': 'DATOS DEL PROCESAMIENTO'},
'Processed points': {'es': 'Puntos procesados'},
'Output CRS': {'es': 'SRC de salida'},
'Date and time': {'es': 'Fecha y hora'},
'BASE COORDINATES': {'es': 'COORDENADAS DE LA BASE'},
'Initial base coordinates': {'es': 'Coordenadas iniciales de la base'},
'Post-processed base coordinates': {'es': 'Coordenadas posprocesadas de la base'},
'APPLIED CORRECTION': {'es': 'CORRECCIÓN APLICADA'},
'Geocentric correction': {'es': 'Corrección geocéntrica'},
'Local topocentric representation': {'es': 'Representación topocéntrica local'},
'METHODOLOGY': {'es': 'METODOLOGÍA'},
'VARIANCE PROPAGATION': {'es': 'PROPAGACIÓN DE VARIANZAS'},
'TECHNICAL NOTES': {'es': 'OBSERVACIONES TÉCNICAS'},
'FINAL ADJUSTED COORDINATES': {'es': 'COORDENADAS FINALES AJUSTADAS'},
'Base precision': {'es': 'Precisión de la base'},
'The final standard deviation of each rover point was computed by combining base and rover sigmas.': {'es': 'La desviación estándar final de cada punto rover se calculó combinando los sigmas de la base y del rover.'},
'Propagation model': {'es': 'Modelo de propagación'},
'This approach ensures that the final rover precision is not better than the base precision.': {'es': 'Este enfoque garantiza que la precisión final de los puntos rover no sea mejor que la precisión de la base.'},
'Adjusted sigma statistics': {'es': 'Estadísticas de los sigmas ajustados'},
'Variance propagation: not applied.': {'es': 'Propagación de varianzas: no aplicada.'},
'Rover points were corrected by applying a rigid translation derived from the difference between the geocentric coordinates of the initial base and the post-processed base. The correction vector (ΔX, ΔY, ΔZ) was computed in the geocentric reference frame and applied uniformly to all rover points. The adjusted coordinates were then transformed back to geodetic coordinates. For interpretation purposes, the correction vector is also represented in the local topocentric system (E, N, U).': {'es': 'Los puntos rover fueron corregidos mediante la aplicación de una traslación rígida derivada de la diferencia entre las coordenadas geocéntricas de la base inicial y la base posprocesada. El vector de corrección (ΔX, ΔY, ΔZ) se calculó en el sistema geocéntrico y se aplicó de forma uniforme a todos los puntos rover. Las coordenadas ajustadas se transformaron nuevamente a coordenadas geodésicas. Para fines de interpretación, el vector de corrección también se representa en el sistema topocéntrico local (E, N, U).'},
'The base correction vector has a geocentric magnitude of {:.3f} m and a local horizontal magnitude of {:.3f} m.': {'es': 'El vector de corrección de la base tiene una magnitud geocéntrica de {:.3f} m y una magnitud horizontal local de {:.3f} m.'},
'Variance propagation was performed using a simplified model, assuming independence between base and rover uncertainties.': {'es': 'La propagación de varianzas se realizó utilizando un modelo simplificado, asumiendo independencia entre las incertidumbres de la base y del rover.'},
'Variance propagation was not applied. The precisions of corrected points were not updated according to the base precision.': {'es': 'No se aplicó la propagación de varianzas. Las precisiones de los puntos corregidos no se actualizaron en función de la precisión de la base.'},
'The field {} contains duplicate values and cannot be a primary key!': {'es': 'El campo {} contiene valores repetidos y no puede ser clave primaria!'},
'The field {} contains null or empty values and cannot be used as a primary key!': {'es': 'El campo {} contiene valores nulos o vacíos y no puede ser utilizado como clave primaria.'},
'Polygon ID': {'es': 'ID del polígono'},
'Thematic slope': {'es': 'Pendiente temática'},
'Projected CRS for reprojection': { 'es': 'SRC proyectado para reproyección' },
'Slope FAO (%)': {'es': 'Pendiente FAO (%)'},
'Slope USDA/NRCS (%)': {'es': 'Pendiente USDA/NRCS (%)'},
'Slope Embrapa - Brazil (%)': {'es': 'Pendiente Embrapa (%)' },
'Slope CAR - Brazil (°)': {'es': 'Pendiente CAR (°)' },
'Symbology and slope unit': { 'es': 'Simbología y unidad de pendiente' },
'Slope raster': {'es': 'Raster de pendiente'},
'The input DEM has no valid CRS!': {'es': 'El MDE de entrada no tiene un SRC válido!'},
'Please select a projected CRS for reprojection!': {'es': '¡Por favor, seleccione un SRC proyectado para la reproyección!' },
'The input DEM is in a geographic CRS. Reprojecting to the selected projected CRS...': {'es': 'El MDE de entrada está en un SRC geográfico. Reproyectando al SRC proyectado seleccionado...' },
'The input DEM is already projected. Reprojection is not required.': {'es': 'El MDE de entrada ya está proyectado. La reproyección no es necesaria.'},
'Calculating slope in degrees...': { 'es': 'Calculando pendiente en grados...'},
'Calculating slope in percentage...': { 'es': 'Calculando pendiente en porcentaje...'},
'Slope (%)': { 'es': 'Pendiente (%)' },
'All input layers must use the same CRS!': {'es': '¡Todas las capas de entrada deben utilizar el mismo SRC!'},
'The layers are defined as geographic CRS, but their coordinates are outside valid longitude/latitude limits. Check whether the CRS was assigned incorrectly.': {'es': 'Las capas están definidas en un SRC geográfico, pero sus coordenadas están fuera de los límites válidos de longitud y latitud. Verifique si el SRC fue asignado correctamente.'},
'All input layers must use a geographic CRS!': {'es': '¡Todas las capas de entrada deben utilizar un SRC geográfico!'},
'parcel': {'es': 'parcela'},
'Concrete monument with plate': {'es': 'Mojón de hormigón con placa'},
'Type P (point)': {'es': 'Tipo P (punto)'},
'Type V (virtual)': {'es': 'Tipo V (virtual)'},
'Concrete monument without plate': {'es': 'Mojón de hormigón sin placa'},
'borderer': {'es': 'colindante'},
'borderer_label': {'es': 'rotulo_colindante'},
'start_point_description': {'es': 'descripcion_punto_inicial'},
'authorizer': {'es': 'responsable'},
'authorizer_id': {'es': 'identificacion_responsable'},
'borderer_registry': {'es': 'registro_colindante'},
'property': {'es': 'inmueble'},
'registry': {'es': 'registro'},
'transcript': {'es': 'matrícula'},
'owner': {'es': 'propietario'},
'owner_id': {'es': 'identificación del propietario'},
'address': {'es': 'dirección'},
'county': {'es': 'municipio'},
'state': {'es': 'estado'},
'survey_date': {'es': 'levantamiento - fecha'},
'surveyor': {'es': 'agrimensor'},
'Technical Manager': {'es': 'Responsable Técnico'},
'Professional registration': {'es': 'Registro profesional'},
'GEODETIC MARK': {'es': 'MOJÓN GEODÉSICO'},
'Ellipsoidal height': {'es': 'altura elipsoidal'},
'Orthometric height': {'es': 'altura ortométrica'},
'GNSS receiver': {'es': 'receptor GNSS'},
'Survey method': {'es': 'método de levantamiento'},
'Static Relative': {'es': 'Relativo Estático'},
'Reference base': {'es': 'Base de referencia'},
'Survey responsible': {'es': 'levantamiento - responsable'},
'Processing date': {'es': 'procesamiento - fecha'},
'Processing responsible': {'es': 'procesamiento - responsable'},
'Report date': {'es': 'monografía - fecha'},
'Report responsible': {'es': 'monografía - responsable'},
'Mark photo': {'es': 'foto del mojón'},
'Panoramic photo': {'es': 'foto panorámica'},
'Aerial image': {'es': 'imagen aérea'},
'Professional qualification': {'es': 'formación profesional'},
'Methodology': {'es': 'Metodología'},
'Reference Base(s)': {'es': 'Base(s) de referencia'},
'Phases': {'es': 'Etapas'},
'Images': {'es': 'Imágenes'},
'Responsibility': {'es': 'Responsabilidad'},
'Altimetric': {'es': 'Altimétrico'},
'Planimetric': {'es': 'Planimétrico'},
'Planialtimetric': {'es': 'Planialtimétrico'},
'Gravimetric': {'es': 'Gravimétrico'},
'Other': {'es': 'Otro'},
'''This tool creates a new GeoPackage file based on the simplified <b>TopoGeo Demo</b> template.
<p>
The generated database contains the minimum set of layers required to use the automated documentation tools available in the <b>LFTools</b> plugin, such as the generation of Survey Descriptions and other technical documents.
</p>
<h3>Generated layers</h3>
<ul>
  <li><code>limit_point_p</code></li>
  <li><code>boundary_element_l</code></li>
  <li><code>property_area_a</code></li>
  <li><code>reference_point_p</code> — optional</li>
</ul>
<h3>Important notes</h3>
<p>
<b>1.</b> The <code>reference_point_p</code> layer is used exclusively to generate the <b>Geodetic mark report</b>.
</p>
<p>
<b>2.</b> For the LFTools documentation tools to work correctly, the Coordinate Reference System (CRS) of the database <b>must be Geographic</b>.
</p>
''': {'es': '''Esta herramienta crea un nuevo archivo GeoPackage basado en la plantilla simplificada <b>TopoGeo Demo</b>.
<p>
La base de datos generada contiene el conjunto mínimo de capas necesarias para utilizar las herramientas de documentación automatizada disponibles en el complemento <b>LFTools</b>, como la generación de Memorias Descriptivas y otros documentos técnicos.
</p>
<h3>Capas generadas</h3>
<ul>
  <li><code>limit_point_p</code></li>
  <li><code>boundary_element_l</code></li>
  <li><code>property_area_a</code></li>
  <li><code>reference_point_p</code> — opcional</li>
</ul>
<h3>Notas importantes</h3>
<p>
<b>1.</b> La capa <code>reference_point_p</code> se utiliza exclusivamente para generar la <b>Monografía del Marco Geodésico</b>.
</p>
<p>
<b>2.</b> Para que las herramientas de documentación del <b>LFTools</b> funcionen correctamente, el Sistema de Referencia de Coordenadas (SRC) de la base de datos <b>debe ser Geográfico</b>.
</p>
'''},
'There is no feature in the layer!': {'es': '¡No hay ninguna entidad en la capa!'},
'Number Polygons by Lines': {'es': 'Numerar polígonos por líneas'},
'This tool numbers polygons according to guide lines. Polygons intersected by each line are sorted following the geometric direction of the line. Lines can optionally be sorted by an attribute field and can also contain an attribute defining the first number of each sequence. If no first-number field is selected, the user defines a general initial value and chooses whether numbering restarts for every line or continues between lines.': {'es': 'Esta herramienta numera polígonos de acuerdo con líneas guía. Los polígonos intersectados por cada línea se ordenan siguiendo la dirección geométrica de la línea. Opcionalmente, las líneas pueden ordenarse mediante un campo de atributos y también pueden contener un atributo que defina el primer número de cada secuencia. Si no se selecciona ningún campo de primer número, el usuario define un valor inicial general y elige si la numeración se reinicia para cada línea o continúa entre líneas.'},
'Polygons to number': {'es': 'Polígonos que se van a numerar'},
'Numbering field': {'es': 'Campo de numeración'},
'Guide lines': {'es': 'Líneas guía'},
'Use only selected lines': {'es': 'Usar solo las líneas seleccionadas'},
'Line order field (optional)': {'es': 'Campo de orden de las líneas (opcional)'},
'First number field for each line (optional)': {'es': 'Campo del primer número para cada línea (opcional)'},
'Initial number (used when no first-number field is selected)': {'es': 'Número inicial (usado cuando no se selecciona ningún campo de primer número)'},
'Restart numbering for each line': {'es': 'Reiniciar la numeración para cada línea'},
' ... and {} more': {'es': ' ... y {} más'},
'{} null geometries (IDs: {})': {'es': '{} geometrías nulas (ID: {})'},
'{} empty geometries (IDs: {})': {'es': '{} geometrías vacías (ID: {})'},
'{} invalid geometries (IDs: {})': {'es': '{} geometrías no válidas (ID: {})'},
'Geometry problems were found. Fix the geometries before running the tool.\n\n': {'es': 'Se encontraron problemas geométricos. Corrija las geometrías antes de ejecutar la herramienta.\n\n'},
'The line order field "{}" has NULL values. Feature IDs: {}': {'es': 'El campo de orden de las líneas "{}" contiene valores NULL. ID de las entidades: {}'},
'The line order field "{}" has duplicate values. Each processed line must have a unique order. Duplicates: {}': {'es': 'El campo de orden de las líneas "{}" contiene valores duplicados. Cada línea procesada debe tener un orden único. Duplicados: {}'},
'The first-number field "{}" has NULL values. Feature IDs: {}': {'es': 'El campo del primer número "{}" contiene valores NULL. ID de las entidades: {}'},
'The first-number field "{}" must contain integer values. Invalid feature IDs: {}': {'es': 'El campo del primer número "{}" debe contener valores enteros. ID de las entidades no válidas: {}'},
'Numbering field not found.': {'es': 'No se encontró el campo de numeración.'},
'The option "Use only selected lines" is enabled, but no line is selected.': {'es': 'La opción "Usar solo las líneas seleccionadas" está activada, pero no hay ninguna línea seleccionada.'},
'The line layer has no features.': {'es': 'La capa de líneas no contiene entidades.'},
'The polygon layer has no features.': {'es': 'La capa de polígonos no contiene entidades.'},
'Validating geometries...': {'es': 'Validando geometrías...'},
'Validating line attributes...': {'es': 'Validando los atributos de las líneas...'},
'Lines sorted by field: {}': {'es': 'Líneas ordenadas por el campo: {}'},
'No line order field selected. Feature ID will be used.': {'es': 'No se seleccionó ningún campo de orden de las líneas. Se utilizará el ID de la entidad.'},
'Each line will start at the value stored in field: {}': {'es': 'Cada línea comenzará con el valor almacenado en el campo: {}'},
'Numbering will restart at {} for each line.': {'es': 'La numeración se reiniciará en {} para cada línea.'},
'Numbering will start at {} and continue between lines.': {'es': 'La numeración comenzará en {} y continuará entre las líneas.'},
'Building spatial index...': {'es': 'Construyendo el índice espacial...'},
'Numbering polygons...': {'es': 'Numerando polígonos...'},
'Error intersecting polygon ID {} with line ID {}: {}': {'es': 'Error al intersectar el polígono con ID {} con la línea con ID {}: {}'},
'Could not locate the intersection of polygon ID {} along line ID {}.': {'es': 'No se pudo localizar la intersección del polígono con ID {} a lo largo de la línea con ID {}.'},
'Line ID {} did not intercept any available polygon.': {'es': 'La línea con ID {} no intersectó ningún polígono disponible.'},
'Line ID {}: {} polygon(s) numbered from {} to {}.': {'es': 'Línea con ID {}: {} polígono(s) numerado(s) de {} a {}.'},
'No polygon was intercepted by the processed lines.': {'es': 'Ningún polígono fue intersectado por las líneas procesadas.'},
'Writing values...': {'es': 'Escribiendo valores...'},
'Could not start editing the polygon layer.': {'es': 'No se pudo iniciar la edición de la capa de polígonos.'},
'Could not write the value for polygon ID {}.': {'es': 'No se pudo escribir el valor del polígono con ID {}.'},
'Could not save edits. {}': {'es': 'No se pudieron guardar las ediciones. {}'},
'{} line(s) processed.': {'es': '{} línea(s) procesada(s).'},
'{} polygon(s) numbered.': {'es': '{} polígono(s) numerado(s).'},
'{} line(s) did not intercept available polygons.': {'es': '{} línea(s) sin intersección con polígonos disponibles.'},
'{} polygon(s) were not numbered.': {'es': '{} polígono(s) sin numerar.'},
'Checking geometries and creating spatial index...' : {'es': 'Verificando geometrías y creando el índice espacial...'},
'Feature id {} has null geometry and was ignored.' : {'es': 'La entidad con ID {} tiene geometría nula y fue ignorada.'},
'Feature id {} has empty geometry and was ignored.' : {'es': 'La entidad con ID {} tiene geometría vacía y fue ignorada.'},
'Feature id {} is not polygonal and was ignored.' : {'es': 'La entidad con ID {} no tiene geometría poligonal y fue ignorada.'},
'Feature id {} is invalid and could not be repaired. It was ignored.' : {'es': 'La entidad con ID {} tiene una geometría no válida y no pudo ser reparada. Fue ignorada.'},
'Feature id {} has no valid polygonal component after repair and was ignored.' : {'es': 'La entidad con ID {} no tiene ningún componente poligonal válido después de la reparación y fue ignorada.'},
'Error processing features {} and {}: {}. Pair ignored.' : {'es': 'Error al procesar las entidades {} y {}: {}. Par ignorado.'},
'Valid geometries used: {}' : {'es': 'Geometrías válidas utilizadas: {}'},
'Null geometries ignored: {}' : {'es': 'Geometrías nulas ignoradas: {}'},
'Empty geometries ignored: {}' : {'es': 'Geometrías vacías ignoradas: {}'},
'Invalid geometries found: {} | repaired: {}' : {'es': 'Geometrías no válidas encontradas: {} | reparadas: {}'},
'Ignored geometries: {} | geometry-operation errors: {}' : {'es': 'Geometrías ignoradas: {} | errores en operaciones geométricas: {}'},
'Overlapping feature pairs: {} | output polygons: {}' : {'es': 'Pares de entidades con superposición: {} | polígonos de salida: {}'},
'Could not apply output layer style: {}' : {'es': 'No se pudo aplicar la simbología de la capa de salida: {}'},
'Operation canceled. No changes were applied.' : {'es': 'Operación cancelada. No se aplicó ningún cambio.'},
'Checking duplicate vertices...' : {'es': 'Verificando vértices duplicados...'},
'Feature ID {} has invalid geometry and was not modified.' : {'es': 'La entidad con ID {} tiene una geometría no válida y no fue modificada.'},
'Cleanup result for feature ID {} was null/empty. Original geometry was preserved.' : {'es': 'El resultado de la limpieza de la entidad con ID {} fue nulo/vacío. Se conservó la geometría original.'},
'Cleanup result for feature ID {} changed geometry type. Original geometry was preserved.' : {'es': 'El resultado de la limpieza de la entidad con ID {} cambió el tipo de geometría. Se conservó la geometría original.'},
'Cleanup result for feature ID {} became invalid. Original geometry was preserved.' : {'es': 'El resultado de la limpieza de la entidad con ID {} se volvió no válido. Se conservó la geometría original.'},
'Could not start layer editing.' : {'es': 'No se pudo iniciar la edición de la capa.'},
'Could not update geometry of feature ID {}.' : {'es': 'No se pudo actualizar la geometría de la entidad con ID {}.'},
'{} invalid feature(s) were preserved without modification.' : {'es': 'Se conservaron {} entidad(es) con geometría no válida sin modificaciones.'},
'{} potentially unsafe geometry change(s) were blocked.' : {'es': 'Se bloquearon {} cambio(s) geométrico(s) potencialmente inseguro(s).'},
'The layer was already in edit mode. Cleanup changes were left in the current edit session and were not committed automatically, in order to avoid saving unrelated edits.' : {'es': 'La capa ya estaba en modo de edición. Los cambios de la limpieza se mantuvieron en la sesión de edición actual y no se guardaron automáticamente, para evitar guardar ediciones no relacionadas.'},
'Snapping behavior' : {'es': 'Comportamiento del ajuste'},
'Prefer aligning nodes, insert extra vertices where required' : {'es': 'Preferir alinear vértices e insertar nuevos vértices cuando sea necesario'},
'Prefer closest point, insert extra vertices where required' : {'es': 'Preferir el punto más cercano e insertar nuevos vértices cuando sea necesario'},
'Prefer aligning nodes, do not insert new vertices' : {'es': 'Preferir alinear vértices sin insertar nuevos vértices'},
'Prefer closest point, do not insert new vertices' : {'es': 'Preferir el punto más cercano sin insertar nuevos vértices'},
'Connectivity correction report' : {'es': 'Informe de corrección de conectividad'},
'Snapping tolerance: {} m | equivalent angular tolerance: {} degrees' : {'es': 'Tolerancia de ajuste: {} m | tolerancia angular equivalente: {} grados'},
'Snapping tolerance: {} m' : {'es': 'Tolerancia de ajuste: {} m'},
'Preparing geometries and preserving original feature IDs...' : {'es': 'Preparando geometrías y preservando los ID originales de las entidades...'},
'Connecting adjacent polygon geometries...' : {'es': 'Conectando geometrías poligonales adyacentes...'},
'Operation canceled by the user.' : {'es': 'Operación cancelada por el usuario.'},
'No connectivity adjustment was required' : {'es': 'No fue necesario realizar ningún ajuste de conectividad'},
'Original geometry is null or empty' : {'es': 'La geometría original es nula o está vacía'},
'Original geometry is invalid; connectivity adjustment was not applied' : {'es': 'La geometría original no es válida; no se aplicó el ajuste de conectividad'},
'Snapping result was not found; original geometry preserved' : {'es': 'No se encontró el resultado del ajuste; se conservó la geometría original'},
'Snapping returned a null or empty geometry; original geometry preserved' : {'es': 'El ajuste produjo una geometría nula o vacía; se conservó la geometría original'},
'Snapping changed the geometry family; original geometry preserved' : {'es': 'El ajuste cambió la familia geométrica; se conservó la geometría original'},
'Snapping produced an invalid geometry; original geometry preserved' : {'es': 'El ajuste produjo una geometría no válida; se conservó la geometría original'},
'Geometry adjusted within the snapping tolerance' : {'es': 'Geometría ajustada dentro de la tolerancia de ajuste'},
'{} feature(s) modified.' : {'es': '{} entidad(es) modificada(s).'},
'{} feature(s) unchanged.' : {'es': '{} entidad(es) sin cambios.'},
'{} potentially unsafe modification(s) were blocked and the original geometries were preserved.' : {'es': 'Se bloquearon {} modificación(es) potencialmente insegura(s) y se conservaron las geometrías originales.'},
'Feature ID {} has null or empty geometry and was ignored.': {'es': 'La entidad ID {} tiene una geometría nula o vacía y fue ignorada.'},
'Orientation result for feature ID {} was unsafe; original geometry was preserved.': {'es': 'El resultado de la orientación de la entidad ID {} no fue seguro; se conservó la geometría original.'},
'Could not orient feature ID {}: {}': {'es': 'No se pudo orientar la entidad ID {}: {}'},
'Feature ID {} is multipart; road-access first vertex was not changed.': {'es': 'La entidad ID {} es multiparte; no se modificó el primer vértice para el acceso vial.'},
'Could not evaluate boundary between features {} and {}: {}': {'es': 'No se pudo evaluar el límite entre las entidades {} y {}: {}'},
'Road-access adjustment for feature ID {} produced an unsafe geometry; original geometry was preserved.': {'es': 'El ajuste para el acceso vial de la entidad ID {} produjo una geometría no segura; se conservó la geometría original.'},
'The layer was already in edit mode. Changes were left in the current edit session and were not committed automatically.': {'es': 'La capa ya estaba en modo de edición. Los cambios se mantuvieron en la sesión de edición actual y no se guardaron automáticamente.'},
'{} feature(s) had polygon orientation adjusted.': {'es': 'Se ajustó la orientación del polígono de {} entidad(es).'},
'{} feature(s) had the road-access first vertex adjusted.': {'es': 'Se ajustó el primer vértice para el acceso vial de {} entidad(es).'},
'{} multipart feature(s) were not modified in the road-access step.': {'es': 'No se modificaron {} entidad(es) multiparte en la etapa de acceso vial.'},
'{} null/empty feature(s) were ignored.': {'es': 'Se ignoraron {} entidad(es) con geometría nula o vacía.'},
'Road-access first vertex has priority over the selected geographic first vertex.' : {'es': 'El primer vértice para el acceso vial tiene prioridad sobre el primer vértice geográfico seleccionado.'},
'Remove polygons with abnormally small areas': {'es': 'Eliminar polígonos con áreas anormalmente pequeñas'},
'Identifying polygons with abnormally small areas...': {'es': 'Identificando polígonos con áreas anormalmente pequeñas...'},
'Reference median parcel area: {:.6f} m² ({} valid geometries).': {'es': 'Área mediana de referencia de las parcelas: {:.6f} m² ({} geometrías válidas).'},
'Polygon area is zero or negative ({:.12g} m²)': {'es': 'El área del polígono es cero o negativa ({:.12g} m²)'},
'Polygon area ({:.12g} m²) is practically zero relative to the median area ({:.6f} m²); ratio = {:.3e}': {'es': 'El área del polígono ({:.12g} m²) es prácticamente nula en relación con el área mediana ({:.6f} m²); razón = {:.3e}'},
'Polygon area ({:.12g} m²) is an extreme lower outlier; median = {:.6f} m², ratio = {:.3e}, robust z = {:.3f}': {'es': 'El área del polígono ({:.12g} m²) es un valor atípico inferior extremo; mediana = {:.6f} m², razón = {:.3e}, z robusto = {:.3f}'},
'Polygons with abnormally small areas removed: {}': {'es': 'Polígonos con áreas anormalmente pequeñas eliminados: {}'},
'Remaining polygons with abnormally small areas: {}': {'es': 'Polígonos con áreas anormalmente pequeñas restantes: {}'},
'''This tool performs a controlled geometric cleanup and topological correction workflow for parcel layers.
The workflow can remove null or empty geometries, repair invalid geometries, convert multipart features to singleparts, remove duplicate geometries, remove holes, remove polygons with abnormally small areas, remove excessively narrow polygons (slivers), snap coordinates to a grid, remove duplicate vertices, and adjust connectivity between adjacent polygons.
Removed features are recorded in a separate table with their original attributes. Modified or blocked operations are recorded in an audit table.
Note: Automatic corrections are accepted only when the resulting geometry passes safety checks. Remaining topological problems must be reviewed after processing.
''' : { 'es': '''Esta herramienta ejecuta un flujo controlado de limpieza geométrica y corrección topológica para capas de parcelas.
El flujo puede eliminar geometrías nulas o vacías, reparar geometrías no válidas, convertir entidades multiparte en partes simples, eliminar geometrías duplicadas, eliminar huecos, eliminar polígonos con áreas anormalmente pequeñas, eliminar polígonos excesivamente estrechos (slivers), ajustar las coordenadas a una cuadrícula, eliminar vértices duplicados y ajustar la conectividad entre polígonos adyacentes.
Las entidades eliminadas se registran en una tabla separada con sus atributos originales. Las operaciones que modificaron entidades o que fueron bloqueadas se registran en una tabla de auditoría.
Nota: Las correcciones automáticas solo se aceptan cuando la geometría resultante supera las comprobaciones de seguridad. Los problemas topológicos restantes deben revisarse después del procesamiento.
'''},
'Original feature unique identifier field': {'es': 'Campo identificador único de la entidad original'},
'The selected identifier field was not found in the input layer.': {'es': 'El campo identificador seleccionado no se encontró en la capa de entrada.'},
'The selected identifier field contains null values. Choose a field with unique and non-null values.': {'es': 'El campo identificador seleccionado contiene valores nulos. Elija un campo con valores únicos y no nulos.'},
'The selected identifier field contains duplicate values. Choose a field with unique and non-null values.': {'es': 'El campo identificador seleccionado contiene valores duplicados. Elija un campo con valores únicos y no nulos.'},
'Using field "{}" as original feature identifier.': {'es': 'Utilizando el campo "{}" como identificador de la entidad original.'},
'No identifier field selected. Internal QGIS feature IDs will be used.': {'es': 'No se seleccionó ningún campo identificador. Se utilizarán los ID internos de las entidades de QGIS.'},
'''Identifies the overlap between features of a polygon type layer.
The optional unique identifier field is used to populate ID1 and ID2 in the output. If no field is selected, the internal QGIS feature ID is used.''' : {'es': '''Identifica la superposición entre entidades de una capa de tipo polígono.
El campo identificador único opcional se utiliza para completar ID1 e ID2 en la salida. Si no se selecciona ningún campo, se utiliza el ID interno de la entidad en QGIS.'''},
'Import CAD': {'es': 'Importar CAD'},
'CAD file': {'es': 'Archivo CAD'},
'Drawing CRS (optional - automatic if possible)': {'es': 'SRC del dibujo (opcional - automático cuando sea posible)'},
'Drawing units': {'es': 'Unidades del dibujo'},
'Auto detect': {'es': 'Detectar automáticamente'},
'Same as CRS units': {'es': 'Mismas unidades que el SRC'},
'Meters': {'es': 'Metros'},
'Millimeters': {'es': 'Milímetros'},
'Centimeters': {'es': 'Centímetros'},
'Kilometers': {'es': 'Kilómetros'},
'Feet': {'es': 'Pies'},
'US survey feet': {'es': 'Pies topográficos de EE. UU.'},
'Inches': {'es': 'Pulgadas'},
'Yards': {'es': 'Yardas'},
'Degrees': {'es': 'Grados'},
'Block handling': {'es': 'Tratamiento de bloques'},
'Expand block geometries': {'es': 'Expandir geometrías de los bloques'},
'Expand geometries and add insertion points': {'es': 'Expandir geometrías y añadir puntos de inserción'},
'Insertion points only': {'es': 'Solo puntos de inserción'},
'Preserve curves when possible': {'es': 'Preservar curvas cuando sea posible'},
'Convert closed polylines to polygons': {'es': 'Convertir polilíneas cerradas en polígonos'},
'Output styling': {'es': 'Simbología de salida'},
'Adapt CAD appearance': {'es': 'Adaptar apariencia CAD'},
'Categorize by CAD layer': {'es': 'Categorizar por capa CAD'},
'Simple GIS style': {'es': 'Simbología SIG simple'},
'Use ODA File Converter as fallback for DWG (if installed)': {'es': 'Usar ODA File Converter como alternativa para DWG (si está instalado)'},
'Output GeoPackage': {'es': 'GeoPackage de salida'},
'Lines': {'es': 'Líneas'},
'Texts': {'es': 'Textos'},
'Imports a CAD drawing (DXF or DWG) into a GeoPackage. The tool automatically attempts to identify the coordinate reference system and drawing units, organizes the entities into points, lines, polygons and texts, and loads the resulting layers in a group with adapted symbology. Unsupported DWG files can optionally be converted using ODA File Converter when installed.': {'es': 'Importa un dibujo CAD (DXF o DWG) a un GeoPackage. La herramienta intenta identificar automáticamente el sistema de referencia de coordenadas y las unidades del dibujo, organiza las entidades en puntos, líneas, polígonos y textos, y carga las capas resultantes en un grupo con simbología adaptada. Los archivos DWG no compatibles pueden convertirse opcionalmente mediante ODA File Converter, cuando esté instalado.'},
'Split polygon': {'es': 'Dividir polígono'},
'Reference line (division direction)': {'es': 'Línea de referencia (dirección de la división)'},
'Subdivision method': {'es': 'Método de división'},
'Equal parts': {'es': 'Partes iguales'},
'Target area': {'es': 'Área deseada'},
'Percentage': {'es': 'Porcentaje'},
'Value (number of parts / area / percentage)': {'es': 'Valor (número de partes / área / porcentaje)'},
'Area calculation method': {'es': 'Método de cálculo del área'},
'Ellipsoidal ($area)': {'es': 'Elipsoidal ($area)'},
'Cartesian - input CRS': {'es': 'Cartesiana - SRC de entrada'},
'INCRA / SIGEF': {'es': 'INCRA / SIGEF'},
'Reverse subdivision side': {'es': 'Invertir lado de la división'},
'Area tolerance': {'es': 'Tolerancia de área'},
'Subdivided polygon': {'es': 'Polígono dividido'},
'Could not determine the geographic CRS associated with the input CRS.': {'es': 'No se pudo determinar el SRC geográfico asociado al SRC de entrada.'},
'The polygon input must contain exactly one feature. If the layer contains several polygons, select one and run the algorithm using selected features only.': {'es': 'La entrada de polígonos debe contener exactamente una entidad. Si la capa contiene varios polígonos, seleccione uno y ejecute el algoritmo utilizando únicamente las entidades seleccionadas.'},
'The reference line input must contain exactly one feature.': {'es': 'La entrada de la línea de referencia debe contener exactamente una entidad.'},
'Empty polygon geometry!': {'es': '¡Geometría de polígono vacía!'},
'The polygon geometry is invalid. Correct the geometry before subdivision.': {'es': 'La geometría del polígono no es válida. Corrija la geometría antes de la división.'},
'Empty reference line!': {'es': '¡Línea de referencia vacía!'},
'Invalid area tolerance!': {'es': '¡Tolerancia de área no válida!'},
'Cartesian area calculation requires a projected CRS. Select another area method or reproject the layer.': {'es': 'El cálculo de área cartesiana requiere un SRC proyectado. Seleccione otro método de cálculo de área o reproyecte la capa.'},
'The polygon area could not be calculated.': {'es': 'No se pudo calcular el área del polígono.'},
'For equal parts, the value must be an integer greater than or equal to 2.': {'es': 'Para partes iguales, el valor debe ser un número entero mayor o igual a 2.'},
'The target area must be greater than zero and smaller than the polygon area ({:.6f}).': {'es': 'El área deseada debe ser mayor que cero y menor que el área del polígono ({:.6f}).'},
'The percentage must be greater than 0 and smaller than 100.': {'es': 'El porcentaje debe ser mayor que 0 y menor que 100.'},
'Total area according to the selected method: {:.6f}': {'es': 'Área total según el método seleccionado: {:.6f}'},
'The subdivision generated {} parts instead of {}. Check the geometry and the reference direction.': {'es': 'La división generó {} partes en lugar de {}. Verifique la geometría y la dirección de referencia.'},
'Could not calculate the area of the generated parts.': {'es': 'No se pudo calcular el área de las partes generadas.'},
'Subdivision completed successfully! {} part(s) generated.': {'es': '¡División completada correctamente! {} parte(s) generada(s).'},
'''
<p>This tool performs a <b>complete automated inspection</b> of individual geometries in one or more point, line, or polygon layers. This step should be completed before intraclass topological validation.</p>
<p><b>Checks:</b></p>
▪️ Null, empty, invalid, or degenerate geometries;
▪️ Duplicated consecutive vertices;
▪️ Multipart geometries and angles below the defined tolerance;
▪️ Lines or polygons smaller than the defined thresholds;
▪️ Polygon holes smaller than the minimum allowed area.
<p><b>Outputs:</b> a point layer of located errors, a complete occurrence table, and an HTML quality report.</p>
<p>Tolerances should consider the reference scale, input resolution, feature class, and intended use. Multipart, undersized, or holed geometries are not necessarily errors and should be technically reviewed.</p>
<p style="color:#b00020;"><b>Important:</b> the input layers are not modified or automatically corrected.</p>
''': {'es': '''
<p>Esta herramienta realiza una <b>inspección automatizada completa</b> de las geometrías individuales de una o varias capas de puntos, líneas o polígonos. Esta etapa debe completarse antes de la validación topológica intraclase.</p>
<p><b>Comprobaciones:</b></p>
▪️ Geometrías nulas, vacías, no válidas o degeneradas;
▪️ Vértices consecutivos duplicados;
▪️ Geometrías multiparte y ángulos inferiores a la tolerancia definida;
▪️ Líneas o polígonos inferiores a los límites definidos;
▪️ Huecos de polígonos con área inferior a la mínima permitida.
<p><b>Salidas:</b> una capa de puntos con los errores localizados, una tabla completa de incidencias y un informe de calidad en HTML.</p>
<p>Las tolerancias deben considerar la escala de referencia, la resolución de los datos de entrada, la clase de entidad y el uso previsto. Las geometrías multiparte, de dimensiones reducidas o con huecos no constituyen necesariamente errores y deben revisarse técnicamente.</p>
<p style="color:#b00020;"><b>Importante:</b> las capas de entrada no se modifican ni se corrigen automáticamente.</p>
'''},
'Validate Geometries': {'es': 'Validar geometrías'},
'Vector layers': {'es': 'Capas vectoriales'},
'Tolerance for duplicated consecutive vertices (layer units)': {'es': 'Tolerancia para vértices consecutivos duplicados (unidades de la capa)'},
'Report multipart geometries': {'es': 'Reportar geometrías multiparte'},
'Check angles below a tolerance': {'es': 'Verificar ángulos inferiores a una tolerancia'},
'Minimum angle (degrees)': {'es': 'Ángulo mínimo (grados)'},
'Check minimum length and area': {'es': 'Verificar longitud y área mínimas'},
'Minimum line length (layer units)': {'es': 'Longitud mínima de las líneas (unidades de la capa)'},
'Minimum polygon area (square layer units)': {'es': 'Área mínima de los polígonos (unidades cuadradas de la capa)'},
'Located geometry errors': {'es': 'Errores geométricos localizados'},
'Geometry validation occurrences': {'es': 'Ocurrencias de la validación geométrica'},
'Geometry validation report': {'es': 'Informe de validación geométrica'},
'Null or empty geometry': {'es': 'Geometría nula o vacía'},
'Invalid geometry': {'es': 'Geometría no válida'},
'Degenerate geometry': {'es': 'Geometría degenerada'},
'Duplicated consecutive vertex': {'es': 'Vértice consecutivo duplicado'},
'Multipart geometry': {'es': 'Geometría multiparte'},
'Angle below tolerance': {'es': 'Ángulo inferior a la tolerancia'},
'Length below tolerance': {'es': 'Longitud inferior a la tolerancia'},
'Area below tolerance': {'es': 'Área inferior a la tolerancia'},
'Select at least one vector layer!': {'es': '¡Seleccione al menos una capa vectorial!'},
'All input layers must use the same CRS. Incompatible layers: {}': {'es': 'Todas las capas de entrada deben utilizar el mismo SRC. Capas incompatibles: {}'},
'Validating layer: {}': {'es': 'Validando capa: {}'},
'{} geometry validation occurrence(s) were found.': {'es': 'Se encontraron {} ocurrencia(s) en la validación geométrica.'},
'No geometry validation occurrences were found.': {'es': 'No se encontraron ocurrencias en la validación geométrica.'},
'GEOMETRY VALIDATION REPORT': {'es': 'INFORME DE VALIDACIÓN GEOMÉTRICA'},
'Individual geometry inspection': {'es': 'Inspección de la geometría individual'},
'Evaluated features': {'es': 'Entidades evaluadas'},
'Affected features': {'es': 'Entidades afectadas'},
'Occurrences': {'es': 'Ocurrencias'},
'Result': {'es': 'Resultado'},
'NONCONFORMING': {'es': 'NO CONFORME'},
'CONFORMING': {'es': 'CONFORME'},
'Nonconforming': {'es': 'No conforme'},
'Conforming': {'es': 'Conforme'},
'1. Evaluated Data': {'es': '1. Datos evaluados'},
'Layer': {'es': 'Capa'},
'Features': {'es': 'Entidades'},
'CRS': {'es': 'SRC'},
'2. Methodology': {'es': '2. Metodología'},
'3. Parameters': {'es': '3. Parámetros'},
'Parameter': {'es': 'Parámetro'},
'4. Results by Rule': {'es': '4. Resultados por regla'},
'Rule': {'es': 'Regla'},
'5. Automatic Interpretation': {'es': '5. Interpretación automática'},
'Duplicated vertex tolerance': {'es': 'Tolerancia para vértices duplicados'},
'Minimum angle': {'es': 'Ángulo mínimo'},
'Minimum line length': {'es': 'Longitud mínima de las líneas'},
'Minimum polygon area': {'es': 'Área mínima de los polígonos'},
'Not evaluated': {'es': 'No evaluado'},
'No': {'es': 'No'},
'A complete automated inspection was performed on every feature. Each geometry was evaluated independently, without changing the source data. Spatially identifiable problems were written to a point layer, while all occurrences, including those without a valid spatial location, were recorded in a non-spatial table.': {'es': 'Se realizó una inspección completa automatizada de todas las entidades. Cada geometría fue evaluada individualmente, sin modificar los datos de origen. Los problemas identificables espacialmente se registraron en una capa de puntos, mientras que todas las ocurrencias, incluidas aquellas sin una ubicación espacial válida, se almacenaron en una tabla no espacial.'},
'The complete automated inspection evaluated {} feature(s) from {} vector layer(s). {} occurrence(s) were identified in {} feature(s). The dataset is classified as {} for the geometry rules enabled in this execution. The input layers were not modified.': {'es': 'La inspección completa automatizada evaluó {} entidad(es) de {} capa(s) vectorial(es). Se identificaron {} ocurrencia(s) en {} entidad(es). El conjunto de datos se clasifica como {} para las reglas geométricas habilitadas en esta ejecución. Las capas de entrada no fueron modificadas.'},
'Hole below minimum area': {'es': 'Hueco con área inferior a la mínima'},
'Check polygon holes below the minimum area': {'es': 'Comprobar huecos de polígonos con área inferior a la mínima'},
'Minimum allowed hole area (square layer units)': {'es': 'Área mínima permitida para los huecos (unidades cuadradas de la capa)'},
'Interior ring {} of polygon part {}.': {'es': 'Anillo interior {} de la parte poligonal {}.'},
'Holes could not be inspected in feature {} of layer {}: {}': {'es': 'No se pudieron inspeccionar los huecos de la entidad {} de la capa {}: {}'},
'Minimum allowed hole area': {'es': 'Área mínima permitida para los huecos'},
'''
<p>This tool performs an <b>automated intraclass topological validation</b> of one or more point, line, or polygon layers. Each layer is evaluated independently.</p>
<p><b>Checks:</b></p>
▪️ Coincident points and duplicated geometries;<br>
▪️ Overlapping line segments and intersections without corresponding vertices;<br>
▪️ Dangle ends and near disconnected ends, except those located near the optional mapping boundary;<br>
▪️ Polygon overlaps, containment, small gaps, and missing vertices along shared borders.
<p><b>Outputs:</b> a point layer containing all located errors and their attributes, and an HTML quality report.</p>
<p>An optional single-polygon mapping area can be used to accept otherwise disconnected line ends located within the defined boundary tolerance.</p>
<p>Feature identifiers are obtained automatically from each layer provider's primary key. When no primary key is declared, the internal QGIS feature ID is used. Gaps receive an occurrence ID and list the adjacent polygons, but do not receive a feature ID of their own.</p>
<p>Distance and area thresholds must consider the reference scale, input resolution, feature class, and intended use. Some occurrences may represent intentional spatial arrangements and must be technically reviewed.</p>
<p style="color:#b00020;"><b>Important:</b> validate and correct individual geometries before running this tool. Null, empty, or invalid geometries are ignored and reported in the execution summary. Input layers are not modified or automatically corrected.</p>
''': {'es': '''
<p>Esta herramienta realiza una <b>validación topológica intraclase automatizada</b> de una o varias capas de puntos, líneas o polígonos. Cada capa se evalúa de forma independiente.</p>
<p><b>Comprobaciones:</b></p>
▪️ Puntos coincidentes y geometrías duplicadas;<br>
▪️ Segmentos de línea superpuestos e intersecciones sin vértices correspondientes;<br>
▪️ Extremos colgantes y extremos próximos desconectados,, excepto los situados cerca del límite opcional del área de mapeo;<br>
▪️ Superposiciones, contenciones, pequeños huecos y vértices ausentes en límites compartidos de polígonos.
<p><b>Salidas:</b> una capa de puntos con todos los errores localizados y sus atributos, y un informe de calidad en HTML.</p>
<p>Puede utilizarse un área de mapeo opcional, formada por una única entidad poligonal, para aceptar extremos de líneas desconectados situados dentro de la tolerancia definida para el límite.</p>
<p>Los identificadores de las entidades se obtienen automáticamente de la clave primaria declarada por el proveedor de cada capa. Cuando no existe una clave primaria declarada, se utiliza el identificador interno de la entidad de QGIS. Los huecos reciben un identificador de incidencia y enumeran los polígonos adyacentes, pero no reciben un identificador de entidad propio.</p>
<p>Las tolerancias de distancia y área deben considerar la escala de referencia, la resolución de los datos de entrada, la clase de entidad y el uso previsto. Algunas incidencias pueden representar configuraciones espaciales intencionadas y deben revisarse técnicamente.</p>
<p style="color:#b00020;"><b>Importante:</b> valide y corrija las geometrías individuales antes de ejecutar esta herramienta. Las geometrías nulas, vacías o no válidas se ignoran y se contabilizan en el resumen de la ejecución. Las capas de entrada no se modifican ni se corrigen automáticamente.</p>
'''},
'Coincident points': {'es': 'Puntos coincidentes'},
'Duplicated geometries': {'es': 'Geometrías duplicadas'},
'Overlapping line segments': {'es': 'Segmentos de línea superpuestos'},
'Intersection without corresponding vertex': {'es': 'Intersección sin vértice correspondiente'},
'Dangle end': {'es': 'Extremo colgante'},
'Near disconnected ends': {'es': 'Extremos próximos y desconectados'},
'Polygon inside polygon': {'es': 'Polígono dentro de otro polígono'},
'Small gap between polygons': {'es': 'Pequeño hueco entre polígonos'},
'Missing vertex along shared border': {'es': 'Vértice ausente en el límite compartido'},
'Validate Intraclass Topology': {'es': 'Validar topología intraclase'},
'Unknown': {'es': 'Desconocida'},
'Not provided': {'es': 'No proporcionada'},
'Line': {'es': 'Línea'},
'NONCONFORMING': {'es': 'NO CONFORME'},
'CONFORMING': {'es': 'CONFORME'},
'Vector layers': {'es': 'Capas vectoriales'},
'Mapping area (optional single polygon)': {'es': 'Área de mapeo (polígono único opcional)'},
'Mapping boundary tolerance for line ends (layer units)': {'es': 'Tolerancia del límite del área de mapeo para extremos de líneas (unidades de la capa)'},
'Topological coincidence tolerance (layer units)': {'es': 'Tolerancia de coincidencia topológica (unidades de la capa)'},
'Maximum distance for near disconnected ends (layer units)': {'es': 'Distancia máxima para extremos próximos y desconectados (unidades de la capa)'},
'Minimum line overlap length to report (layer units)': {'es': 'Longitud mínima de superposición lineal que se debe informar (unidades de la capa)'},
'Minimum polygon overlap area to report (square layer units)': {'es': 'Área mínima de superposición de polígonos que se debe informar (unidades cuadradas de la capa)'},
'Check dangle and near disconnected line ends': {'es': 'Comprobar extremos colgantes y extremos próximos desconectados'},
'Check small gaps between polygons': {'es': 'Comprobar pequeños huecos entre polígonos'},
'Maximum gap area to report (square layer units; 0 reports all)': {'es': 'Área máxima del hueco que se debe informar (unidades cuadradas de la capa; 0 informa todos)'},
'Check missing vertices along shared polygon borders': {'es': 'Comprobar vértices ausentes en límites compartidos de polígonos'},
'Located topological errors': {'es': 'Errores topológicos localizados'},
'Intraclass topology validation report': {'es': 'Informe de validación topológica intraclase'},
'Select at least one vector layer!': {'es': '¡Seleccione al menos una capa vectorial!'},
'Use a projected CRS because the validation parameters are expressed in layer units.': {'es': 'Utilice un SRC proyectado porque los parámetros de validación se expresan en unidades de la capa.'},
'Provided': {'es': 'Proporcionada'},
'No intraclass topology occurrences were found.': {'es': 'No se encontraron incidencias topológicas intraclase.'},
'The native missing-vertex checker is not available; the compatible LFTools method will be used.': {'es': 'El verificador nativo de vértices ausentes no está disponible; se utilizará el método compatible de LFTools.'},
'Missing vertices along shared borders were checked with the native QGIS algorithm.': {'es': 'Los vértices ausentes en límites compartidos se comprobaron con el algoritmo nativo de QGIS.'},
'Nonconforming': {'es': 'No conforme'},
'Conforming': {'es': 'Conforme'},
'The mapping area and all input layers must use the same CRS.': {'es': 'El área de mapeo y todas las capas de entrada deben utilizar el mismo SRC.'},
'The mapping area must contain exactly one polygon feature.': {'es': 'El área de mapeo debe contener exactamente una entidad poligonal.'},
'The mapping area has a null or empty geometry.': {'es': 'El área de mapeo tiene una geometría nula o vacía.'},
'The mapping area geometry is invalid. Correct it before validation.': {'es': 'La geometría del área de mapeo no es válida. Corríjala antes de la validación.'},
'All input layers must use the same CRS. Incompatible layers: {}': {'es': 'Todas las capas de entrada deben utilizar el mismo SRC. Capas incompatibles: {}'},
'Validating intraclass topology: {}': {'es': 'Validando topología intraclase: {}'},
'{} intraclass topology occurrence(s) were found.': {'es': 'Se encontraron {} incidencia(s) en la validación topológica intraclase.'},
'Vertex reported by the native QGIS missing-vertices checker.': {'es': 'Vértice informado por el verificador nativo de vértices ausentes de QGIS.'},
'A vertex from the related polygon is missing from this shared border.': {'es': 'Falta un vértice del polígono relacionado en este límite compartido.'},
'Potential internal gap in the polygon coverage.': {'es': 'Posible hueco interno en la cobertura de polígonos.'},
'{} null, empty, or invalid feature(s) were ignored in layer {}.': {'es': 'Se ignoraron {} entidad(es) nula(s), vacía(s) o no válida(s) en la capa {}.'},
'No connection with another line was found.': {'es': 'No se encontró conexión con otra línea.'},
'The native missing-vertex checker failed ({}); the compatible LFTools method will be used.': {'es': 'El verificador nativo de vértices ausentes falló ({}); se utilizará el método compatible de LFTools.'},
'The gap check could not be completed: {}': {'es': 'No se pudo completar la comprobación de huecos: {}'},
'Topological coincidence tolerance': {'es': 'Tolerancia de coincidencia topológica'},
'Near disconnected ends tolerance': {'es': 'Tolerancia para extremos próximos y desconectados'},
'Mapping area': {'es': 'Área de mapeo'},
'Mapping boundary tolerance': {'es': 'Tolerancia del límite del área de mapeo'},
'Minimum line overlap length': {'es': 'Longitud mínima de superposición lineal'},
'Minimum polygon overlap area': {'es': 'Área mínima de superposición de polígonos'},
'Maximum gap area': {'es': 'Área máxima de los huecos'},
'5. Automatic Interpretation': {'es': '5. Interpretación automática'},
'Distance between points: {}': {'es': 'Distancia entre los puntos: {}'},
'Distance to the nearest line: {}': {'es': 'Distancia hasta la línea más próxima: {}'},
'Not evaluated': {'es': 'No evaluada'},
'Missing corresponding vertex in feature(s): {}': {'es': 'Falta el vértice correspondiente en la(s) entidad(es): {}'},
'Result': {'es': 'Resultado'},
'Occurrences': {'es': 'Incidencias'},
'Rule': {'es': 'Regla'},
'4. Results by Rule': {'es': '4. Resultados por regla'},
'Parameter': {'es': 'Parámetro'},
'3. Parameters': {'es': '3. Parámetros'},
'2. Methodology': {'es': '2. Metodología'},
'CRS': {'es': 'SRC'},
'Boundary exceptions': {'es': 'Excepciones en el límite'},
'Ignored': {'es': 'Ignoradas'},
'Evaluated': {'es': 'Evaluadas'},
'Layer': {'es': 'Capa'},
'1. Evaluated Data': {'es': '1. Datos evaluados'},
'individual geometries must be validated and corrected before intraclass topology is assessed. Null, empty, or invalid geometries were ignored.': {'es': 'las geometrías individuales deben validarse y corregirse antes de evaluar la topología intraclase. Se ignoraron las geometrías nulas, vacías o no válidas.'},
'Prerequisite:': {'es': 'Requisito previo:'},
'Ignored features': {'es': 'Entidades ignoradas'},
'Evaluated features': {'es': 'Entidades evaluadas'},
'Logical consistency — intraclass level': {'es': 'Consistencia lógica — nivel intraclase'},
'INTRACLASS TOPOLOGY VALIDATION REPORT': {'es': 'INFORME DE VALIDACIÓN TOPOLÓGICA INTRACLASE'},
'The automated intraclass validation evaluated {} valid feature(s) in {} layer(s), ignored {} null, empty, or invalid feature(s), accepted {} disconnected line end(s) near the mapping boundary, and identified {} occurrence(s) affecting {} feature(s). The dataset is {} for the rules enabled in this execution. The input layers were not modified.': {'es': 'La validación intraclase automatizada evaluó {} entidad(es) válida(s) en {} capa(s), ignoró {} entidad(es) nula(s), vacía(s) o no válida(s), aceptó {} extremo(s) de línea desconectado(s) próximo(s) al límite del área de mapeo e identificó {} incidencia(s) que afectan a {} entidad(es). El conjunto de datos está {} para las reglas habilitadas en esta ejecución. Las capas de entrada no fueron modificadas.'},
'Each layer was evaluated independently. Spatial relationships were compared using a spatial index and the enabled linear and area thresholds. When a mapping area was provided, disconnected line ends within the boundary tolerance were accepted and counted separately. Identifiers were obtained automatically from provider-declared primary keys, with the internal QGIS feature ID used as a fallback. The validation only identifies potential nonconformities; it does not edit the source data.': {'es': 'Cada capa se evaluó de forma independiente. Las relaciones espaciales se compararon mediante un índice espacial y los límites lineales y de área habilitados. Cuando se proporcionó un área de mapeo, los extremos de líneas desconectados situados dentro de la tolerancia del límite fueron aceptados y contabilizados por separado. Los identificadores se obtuvieron automáticamente de las claves primarias declaradas por los proveedores, utilizando como alternativa el identificador interno de la entidad de QGIS. La validación únicamente identifica posibles no conformidades; no modifica los datos de origen.'},

'HAND model': {'es': 'Modelo HAND'},
'Hydrology': {'es': 'Hidrología'},
'Number of cells (pixels)': {'es': 'Número de celdas (píxeles)'},
'Square kilometres (km²)': {'es': 'Kilómetros cuadrados (km²)'},
'Keep as NoData (strict drainage network)': {'es': 'Mantener como NoData (red de drenaje estricta)'},
'Use elevation of the outlet cell': {'es': 'Usar la elevación de la celda de salida'},
'Use a fixed reference level (sea/lake)': {'es': 'Usar un nivel de referencia fijo (mar/lago)'},
'Preparing the elevation model...': {'es': 'Preparando el modelo de elevación...'},
'Calculating D8 flow direction and flow accumulation...': {'es': 'Calculando la dirección de flujo D8 y la acumulación de flujo...'},
'Calculating HAND...': {'es': 'Calculando el HAND...'},
'Conditioned DEM': {'es': 'MDE acondicionado'},
'D8 flow direction': {'es': 'Dirección de flujo D8'},
'Flow accumulation': {'es': 'Acumulación de flujo'},
'Drainage network (raster)': {'es': 'Red de drenaje (ráster)'},
'Ordered drainage network': {'es': 'Red de drenaje ordenada'},
'Post-processing: applying the HAND raster style...': {'es': 'Posprocesamiento: aplicando la simbología del ráster HAND...'},
'Post-processing: HAND raster style applied.': {'es': 'Posprocesamiento: simbología del ráster HAND aplicada.'},
'Input DEM': {'es': 'MDE de entrada'},
'Hydrologically condition the DEM (fill depressions)': {'es': 'Acondicionar hidrológicamente el MDE (rellenar depresiones)'},
'Drainage initiation threshold': {'es': 'Umbral de inicio del drenaje'},
'Threshold unit': {'es': 'Unidad del umbral'},
'Flow paths leaving the valid DEM': {'es': 'Trayectorias de flujo que salen del MDE válido'},
'Fixed reference level (m)': {'es': 'Nivel de referencia fijo (m)'},
'Memory available to GRASS (MB)': {'es': 'Memoria disponible para GRASS (MB)'},
'HAND raster': {'es': 'Ráster HAND'},
'The linear unit of the DEM CRS could not be converted to metres.': {'es': 'No se pudo convertir a metros la unidad lineal del SRC del MDE.'},
'The DEM uses a geographic CRS. Cell areas and vector lengths will be measured geodesically.': {'es': 'El MDE utiliza un SRC geográfico. Las áreas de las celdas y las longitudes vectoriales se medirán geodésicamente.'},
'The DEM has an invalid pixel area.': {'es': 'El MDE tiene un área de píxel no válida.'},
'The selected threshold did not generate any drainage cells. Reduce the minimum contributing area.': {'es': 'El umbral seleccionado no generó ninguna celda de drenaje. Reduzca el área mínima de aporte.'},
'The HAND layer could not be loaded to apply its style.': {'es': 'No se pudo cargar la capa HAND para aplicar su simbología.'},
'Drainage threshold: {:.0f} cells (approximately {:.6f} km²).': {'es': 'Umbral de drenaje: {:.0f} celdas (aproximadamente {:.6f} km²).'},
'Drainage network generated with {:,} raster cells.': {'es': 'Red de drenaje generada con {:,} celdas ráster.'},
'{} drainage reaches created. Maximum Strahler order: {}.': {'es': 'Se crearon {} tramos de drenaje. Orden máximo de Strahler: {}.'},
'{} HAND cells have negative values. Check DEM conditioning and vertical units.': {'es': '{} celdas del HAND tienen valores negativos. Compruebe el acondicionamiento del MDE y las unidades verticales.'},
'{} valid terrain cells reach neither the extracted drainage nor an identifiable external outlet and were written as NoData.': {'es': '{} celdas válidas del terreno no alcanzan ni la red de drenaje extraída ni una salida externa identificable y se guardaron como NoData.'},
'HAND Model — {}': {'es': 'Modelo HAND — {}'},
'{} terrain cells were referenced to the elevation of their external outlet cell.': {'es': '{} celdas del terreno se referenciaron a la elevación de su celda de salida externa.'},
'{} terrain cells were referenced to the fixed level of {:.3f} m.': {'es': '{} celdas del terreno se referenciaron al nivel fijo de {:.3f} m.'},
'Extract drainage network': {'es': 'Extraer red de drenaje'},
'Drainage network — {}': {'es': 'Red de drenaje — {}'},
'Delineate watershed': {'es': 'Delimitar cuenca hidrográfica'},
'Nearest extracted drainage cell (recommended)': {'es': 'Celda de drenaje extraída más cercana (recomendado)'},
'Cell with greatest flow accumulation': {'es': 'Celda con mayor acumulación de flujo'},
'Do not adjust': {'es': 'No ajustar'},
'Delineating the upstream watershed...': {'es': 'Delimitando la cuenca aportante aguas arriba...'},
'Finalizing output rasters...': {'es': 'Finalizando los rásteres de salida...'},
'Watershed': {'es': 'Cuenca hidrográfica'},
'Outlet points': {'es': 'Puntos de salida'},
'Watershed (raster)': {'es': 'Cuenca hidrográfica (ráster)'},
'Outlet point': {'es': 'Punto de salida'},
'Outlet adjustment': {'es': 'Ajuste del punto de salida'},
'Maximum adjustment distance (m)': {'es': 'Distancia máxima de ajuste (m)'},
'Ordered drainage network inside the watershed': {'es': 'Red de drenaje ordenada dentro de la cuenca'},
'Watershed raster': {'es': 'Ráster de la cuenca hidrográfica'},
'Drainage network inside the watershed (raster)': {'es': 'Red de drenaje dentro de la cuenca (ráster)'},
'The DEM uses a geographic CRS. Cell areas, adjustment distances and vector measurements will be calculated geodesically.': {'es': 'El MDE utiliza un SRC geográfico. Las áreas de las celdas, las distancias de ajuste y las mediciones vectoriales se calcularán geodésicamente.'},
'The informed outlet is outside the valid DEM area.': {'es': 'El punto de salida indicado está fuera del área válida del MDE.'},
'The watershed raster generated by GRASS could not be opened.': {'es': 'No se pudo abrir el ráster de la cuenca generado por GRASS.'},
'The selected outlet did not generate a watershed.': {'es': 'El punto de salida seleccionado no generó una cuenca hidrográfica.'},
'The input DEM could not be opened for parameter validation.': {'es': 'No se pudo abrir el MDE de entrada para validar los parámetros.'},
'The informed outlet is outside the DEM extent. Processing was not started.': {'es': 'El punto de salida indicado está fuera de la extensión del MDE. El procesamiento no se inició.'},
'The informed outlet falls on a NoData cell of the DEM. Move the point to valid terrain. Processing was not started.': {'es': 'El punto de salida indicado se encuentra sobre una celda NoData del MDE. Mueva el punto a un terreno válido. El procesamiento no se inició.'},
'No suitable outlet cell was found within the maximum adjustment distance.': {'es': 'No se encontró ninguna celda adecuada para el punto de salida dentro de la distancia máxima de ajuste.'},
'The watershed raster could not be vectorized.': {'es': 'No se pudo vectorizar el ráster de la cuenca.'},
'No watershed polygon was generated.': {'es': 'No se generó ningún polígono de cuenca.'},
'The watershed geometry is empty.': {'es': 'La geometría de la cuenca está vacía.'},
'Outlet adjusted by {:.3f} m to a cell with accumulation of {:.0f} cells.': {'es': 'Punto de salida ajustado {:.3f} m a una celda con una acumulación de {:.0f} celdas.'},
'Watershed area: approximately {:.6f} km². {} drainage reaches created.': {'es': 'Área de la cuenca: aproximadamente {:.6f} km². Se crearon {} tramos de drenaje.'},
'Pre-processing validation: pixel approximately {:.3f} × {:.3f} m; drainage threshold {:.0f} cells ({:.6f} km²); outlet adjustment distance {:.3f} m.': {'es': 'Validación previa: píxel de aproximadamente {:.3f} × {:.3f} m; umbral de drenaje de {:.0f} celdas ({:.6f} km²); distancia de ajuste del punto de salida de {:.3f} m.'},
'Watershed — {}': {'es': 'Cuenca hidrográfica — {}'},
'The drainage threshold ({:.0f} cells) is greater than the total number of DEM cells ({:,}). Reduce the threshold. Processing was not started.': {'es': 'El umbral de drenaje ({:.0f} celdas) es mayor que el número total de celdas del MDE ({:,}). Reduzca el umbral. El procesamiento no se inició.'},
'The maximum outlet adjustment distance ({:.3f} m) is smaller than the DEM pixel diagonal (approximately {:.3f} m). A drainage cell is represented by its centre, so the selected distance may contain no candidate cell. Use at least {} m; approximately {} m (three pixels) is recommended for this DEM. Processing was not started and no output layer was created.': {'es': 'La distancia máxima de ajuste del punto de salida ({:.3f} m) es menor que la diagonal del píxel del MDE (aproximadamente {:.3f} m). Como una celda de drenaje se representa por su centro, la distancia seleccionada puede no contener ninguna celda candidata. Utilice al menos {} m; para este MDE se recomiendan aproximadamente {} m (tres píxeles). El procesamiento no se inició y no se creó ninguna capa de salida.'},
'Could not finalize output raster: {}': {'es': 'No se pudo finalizar el ráster de salida: {}'},
'No suitable outlet cell was found within {:.3f} m. Increase the maximum distance or reduce the drainage threshold.': {'es': 'No se encontró ninguna celda adecuada para el punto de salida dentro de {:.3f} m. Aumente la distancia máxima o reduzca el umbral de drenaje.'},
'The input DEM could not be opened.': {'es': 'No se pudo abrir el MDE de entrada.'},
'The input DEM must have exactly one band.': {'es': 'El MDE de entrada debe tener exactamente una banda.'},
'The input DEM has an invalid geotransform.': {'es': 'El MDE de entrada tiene una geotransformación no válida.'},
'One or more hydrological rasters could not be opened.': {'es': 'No se pudieron abrir uno o más rásteres hidrológicos.'},
'The raster has more than 100 million cells. Clip the DEM to the study area or use a coarser resolution.': {'es': 'El ráster tiene más de 100 millones de celdas. Recorte el MDE al área de estudio o utilice una resolución más gruesa.'},
'This raster has more than 25 million cells. The HAND calculation may require substantial RAM.': {'es': 'Este ráster tiene más de 25 millones de celdas. El cálculo del HAND puede requerir una cantidad considerable de memoria RAM.'},
'The GRASS Processing provider or the {} module is not available. Install/enable GRASS in QGIS and try again.': {'es': 'El proveedor de Procesos GRASS o el módulo {} no está disponible. Instale o habilite GRASS en QGIS e inténtelo de nuevo.'},
'The hydrological rasters have different dimensions.': {'es': 'Los rásteres hidrológicos tienen dimensiones diferentes.'},
'The hydrological rasters are not aligned.': {'es': 'Los rásteres hidrológicos no están alineados.'},
'The hydrological rasters have different coordinate reference systems.': {'es': 'Los rásteres hidrológicos tienen sistemas de referencia de coordenadas diferentes.'},
'Post-processing completed: output group, layer order and visibility configured.': {'es': 'Posprocesamiento finalizado: se configuraron el grupo de salida, el orden y la visibilidad de las capas.'},
'The strahler field was not found; the drainage style was not applied.': {'es': 'No se encontró el campo strahler; no se aplicó la simbología de drenaje.'},
'The point_type field was not found; the outlet style was not applied.': {'es': 'No se encontró el campo point_type; no se aplicó la simbología de los puntos de salida.'},
'Original point': {'es': 'Punto original'},
'Adjusted outlet': {'es': 'Punto de salida ajustado'},
'{} drainage cells could not be topologically ordered. Check the D8 raster for cycles.': {'es': '{} celdas de drenaje no pudieron ordenarse topológicamente. Compruebe si hay ciclos en el ráster D8.'},
'A cycle was found in the D8 drainage raster; the affected reach was truncated.': {'es': 'Se encontró un ciclo en el ráster de drenaje D8; el tramo afectado fue truncado.'},

'''Generates the <b>Height Above Nearest Drainage (HAND)</b> model from a Digital Elevation Model (DEM). HAND is the vertical difference between each terrain cell and the first drainage cell reached downstream along its D8 flow path.
<b>Processing workflow</b>
1. Optional hydrological conditioning of the DEM with GRASS <i>r.fill.dir</i>.
2. D8 flow direction and flow accumulation with GRASS <i>r.watershed</i>.
3. Drainage extraction using a minimum contributing-area threshold.
4. HAND calculation and Strahler and Shreve stream ordering.
<b>Outputs</b>
Conditioned DEM; D8 flow direction; flow accumulation; drainage raster; ordered vector drainage network; and HAND raster.
<b>Important information</b>
&#8226; Both projected and geographic CRS are accepted, but DEM elevations must be expressed in metres.
&#8226; The drainage threshold may be entered as number of cells, km&sup2; or hectares. For a geographic CRS, area conversions use the geodesic area of a cell at the centre of the DEM and are therefore approximate.
&#8226; Flow paths leaving the valid DEM before reaching the extracted drainage can remain as NoData, use the outlet-cell elevation, or use a fixed reference level, such as mean sea level.
&#8226; HAND is a terrain descriptor. By itself, it does not represent a hydraulic flood simulation.
<b>References</b>
Rennó, C. D. et al. (2008). <i>HAND, a new terrain descriptor using SRTM-DEM: Mapping terra-firme rainforest environments in Amazonia</i>. Remote Sensing of Environment, 112(9), 3469&ndash;3481. <a href="https://doi.org/10.1016/j.rse.2008.03.018">DOI: 10.1016/j.rse.2008.03.018</a>.
Nobre, A. D. et al. (2011). <i>Height Above the Nearest Drainage &mdash; a hydrologically relevant new terrain model</i>. Journal of Hydrology, 404(1&ndash;2), 13&ndash;29. <a href="https://doi.org/10.1016/j.jhydrol.2011.03.051">DOI: 10.1016/j.jhydrol.2011.03.051</a>.
GRASS GIS documentation: <a href="https://grass.osgeo.org/grass-stable/manuals/r.fill.dir.html"><i>r.fill.dir</i></a> and <a href="https://grass.osgeo.org/grass-stable/manuals/r.watershed.html"><i>r.watershed</i></a>.''': {'es': '''Genera el modelo <b>HAND (Height Above Nearest Drainage)</b>, o altura sobre el drenaje más cercano, a partir de un Modelo Digital de Elevación (MDE). HAND es la diferencia vertical entre cada celda del terreno y la primera celda de drenaje alcanzada aguas abajo a lo largo de su trayectoria de flujo D8.
<b>Flujo de procesamiento</b>
1. Acondicionamiento hidrológico opcional del MDE con GRASS <i>r.fill.dir</i>.
2. Dirección de flujo D8 y acumulación de flujo con GRASS <i>r.watershed</i>.
3. Extracción del drenaje mediante un umbral de área mínima de aporte.
4. Cálculo del HAND y ordenación de la red según los métodos de Strahler y Shreve.
<b>Resultados</b>
MDE acondicionado; dirección de flujo D8; acumulación de flujo; ráster de drenaje; red de drenaje vectorial ordenada; y ráster HAND.
<b>Información importante</b>
&#8226; Se admiten SRC proyectados y geográficos, pero las elevaciones del MDE deben estar expresadas en metros.
&#8226; El umbral de drenaje puede introducirse como número de celdas, km&sup2; o hectáreas. Para un SRC geográfico, las conversiones de área utilizan el área geodésica de una celda en el centro del MDE y, por tanto, son aproximadas.
&#8226; Las trayectorias de flujo que salen del MDE válido antes de alcanzar el drenaje extraído pueden permanecer como NoData, utilizar la elevación de la celda de salida o utilizar un nivel de referencia fijo, como el nivel medio del mar.
&#8226; HAND es un descriptor del terreno. Por sí solo, no representa una simulación hidráulica de inundación.
<b>Referencias</b>
Rennó, C. D. et al. (2008). <i>HAND, a new terrain descriptor using SRTM-DEM: Mapping terra-firme rainforest environments in Amazonia</i>. Remote Sensing of Environment, 112(9), 3469&ndash;3481. <a href="https://doi.org/10.1016/j.rse.2008.03.018">DOI: 10.1016/j.rse.2008.03.018</a>.
Nobre, A. D. et al. (2011). <i>Height Above the Nearest Drainage &mdash; a hydrologically relevant new terrain model</i>. Journal of Hydrology, 404(1&ndash;2), 13&ndash;29. <a href="https://doi.org/10.1016/j.jhydrol.2011.03.051">DOI: 10.1016/j.jhydrol.2011.03.051</a>.
Documentación de GRASS GIS: <a href="https://grass.osgeo.org/grass-stable/manuals/r.fill.dir.html"><i>r.fill.dir</i></a> y <a href="https://grass.osgeo.org/grass-stable/manuals/r.watershed.html"><i>r.watershed</i></a>.'''},

'''Extracts a drainage network from a <b>Digital Elevation Model (DEM)</b>. The algorithm calculates D8 flow direction and flow accumulation, applies a minimum contributing-area threshold and generates raster and ordered vector drainage networks.
<b>Processing workflow</b>
1. Optional hydrological conditioning of the DEM with GRASS <i>r.fill.dir</i>.
2. D8 flow direction and flow accumulation with GRASS <i>r.watershed</i>.
3. Drainage extraction using a minimum contributing-area threshold.
4. Vectorization and stream ordering using the Strahler and Shreve methods.
<b>Outputs</b>
Conditioned DEM; D8 flow direction; flow accumulation; drainage raster; and ordered vector drainage network.
<b>Important information</b>
&#8226; Both projected and geographic CRS are accepted, but DEM elevations must be expressed in metres.
&#8226; The drainage threshold may be entered as number of cells, km&sup2; or hectares. A smaller threshold generates a denser network; a larger threshold retains only the main channels.
&#8226; For a geographic CRS, area conversions use the geodesic area of a cell at the centre of the DEM and are therefore approximate.
&#8226; The vector network contains Strahler and Shreve order, length, upstream area, initial and final elevation, and slope.
<b>References</b>
Strahler, A. N. (1957). <i>Quantitative analysis of watershed geomorphology</i>. Transactions, American Geophysical Union, 38(6), 913&ndash;920.
Shreve, R. L. (1966). <i>Statistical law of stream numbers</i>. Journal of Geology, 74(1), 17&ndash;37.
GRASS GIS documentation: <a href="https://grass.osgeo.org/grass-stable/manuals/r.fill.dir.html"><i>r.fill.dir</i></a> and <a href="https://grass.osgeo.org/grass-stable/manuals/r.watershed.html"><i>r.watershed</i></a>.''': {'es': '''Extrae una red de drenaje a partir de un <b>Modelo Digital de Elevación (MDE)</b>. El algoritmo calcula la dirección de flujo D8 y la acumulación de flujo, aplica un umbral de área mínima de aporte y genera redes de drenaje en formato ráster y vectorial ordenado.
<b>Flujo de procesamiento</b>
1. Acondicionamiento hidrológico opcional del MDE con GRASS <i>r.fill.dir</i>.
2. Dirección de flujo D8 y acumulación de flujo con GRASS <i>r.watershed</i>.
3. Extracción del drenaje mediante un umbral de área mínima de aporte.
4. Vectorización y ordenación de la red según los métodos de Strahler y Shreve.
<b>Resultados</b>
MDE acondicionado; dirección de flujo D8; acumulación de flujo; ráster de drenaje; y red de drenaje vectorial ordenada.
<b>Información importante</b>
&#8226; Se admiten SRC proyectados y geográficos, pero las elevaciones del MDE deben estar expresadas en metros.
&#8226; El umbral de drenaje puede introducirse como número de celdas, km&sup2; o hectáreas. Un umbral menor genera una red más densa; un umbral mayor conserva solo los cauces principales.
&#8226; Para un SRC geográfico, las conversiones de área utilizan el área geodésica de una celda en el centro del MDE y, por tanto, son aproximadas.
&#8226; La red vectorial contiene el orden de Strahler y Shreve, la longitud, el área aguas arriba, las elevaciones inicial y final y la pendiente.
<b>Referencias</b>
Strahler, A. N. (1957). <i>Quantitative analysis of watershed geomorphology</i>. Transactions, American Geophysical Union, 38(6), 913&ndash;920.
Shreve, R. L. (1966). <i>Statistical law of stream numbers</i>. Journal of Geology, 74(1), 17&ndash;37.
Documentación de GRASS GIS: <a href="https://grass.osgeo.org/grass-stable/manuals/r.fill.dir.html"><i>r.fill.dir</i></a> y <a href="https://grass.osgeo.org/grass-stable/manuals/r.watershed.html"><i>r.watershed</i></a>.'''},

'''Delineates the <b>upstream contributing watershed</b> from a Digital Elevation Model (DEM) and an outlet point. The point can be adjusted to the extracted drainage network or to the cell with the greatest flow accumulation within a search distance.
<b>Processing workflow</b>
1. Optional hydrological conditioning of the DEM with GRASS <i>r.fill.dir</i>.
2. D8 flow direction and flow accumulation with GRASS <i>r.watershed</i>.
3. Drainage extraction using a minimum contributing-area threshold.
4. Outlet adjustment and watershed delineation with GRASS <i>r.water.outlet</i>.
5. Basin vectorization and generation of the ordered drainage network inside the basin.
<b>Outlet adjustment</b>
&#8226; <b>Nearest drainage cell:</b> moves the point to the closest extracted drainage cell within the maximum distance. This is the recommended option when the user clicks close to a known stream.
&#8226; <b>Greatest flow accumulation:</b> selects, within the search distance, the cell receiving the largest upstream contribution.
&#8226; <b>Do not adjust:</b> uses the DEM cell containing the informed coordinate. If it is on a hillslope, the resulting basin may be very small or narrow.
<b>Outputs</b>
Watershed polygon and raster; original and adjusted outlet points; ordered drainage network and drainage raster inside the basin; conditioned DEM; D8 flow direction; and flow accumulation.
<b>Important information</b>
&#8226; The maximum adjustment distance is expressed in metres, including when the DEM uses a geographic CRS.
&#8226; Before running GRASS, the algorithm checks the outlet position, DEM resolution, drainage threshold and adjustment distance. Incompatible parameters are reported before any output is created.
&#8226; The drainage threshold controls both the density of the network and the cells available for the nearest-drainage adjustment.
&#8226; Check the adjusted outlet before using the basin in engineering analyses, especially near confluences.
<b>Reference</b>
GRASS GIS documentation: <a href="https://grass.osgeo.org/grass-stable/manuals/r.water.outlet.html"><i>r.water.outlet</i></a>, <a href="https://grass.osgeo.org/grass-stable/manuals/r.watershed.html"><i>r.watershed</i></a> and <a href="https://grass.osgeo.org/grass-stable/manuals/r.fill.dir.html"><i>r.fill.dir</i></a>.''': {'es': '''Delimita la <b>cuenca hidrográfica aportante aguas arriba</b> a partir de un Modelo Digital de Elevación (MDE) y de un punto de salida. El punto puede ajustarse a la red de drenaje extraída o a la celda con mayor acumulación de flujo dentro de una distancia de búsqueda.
<b>Flujo de procesamiento</b>
1. Acondicionamiento hidrológico opcional del MDE con GRASS <i>r.fill.dir</i>.
2. Dirección de flujo D8 y acumulación de flujo con GRASS <i>r.watershed</i>.
3. Extracción del drenaje mediante un umbral de área mínima de aporte.
4. Ajuste del punto de salida y delimitación de la cuenca con GRASS <i>r.water.outlet</i>.
5. Vectorización de la cuenca y generación de la red de drenaje ordenada dentro de ella.
<b>Ajuste del punto de salida</b>
&#8226; <b>Celda de drenaje más cercana:</b> mueve el punto a la celda de drenaje extraída más cercana dentro de la distancia máxima. Es la opción recomendada cuando el usuario hace clic cerca de un curso de agua conocido.
&#8226; <b>Mayor acumulación de flujo:</b> selecciona, dentro de la distancia de búsqueda, la celda que recibe el mayor aporte aguas arriba.
&#8226; <b>No ajustar:</b> utiliza la celda del MDE que contiene la coordenada indicada. Si se encuentra en una ladera, la cuenca resultante puede ser muy pequeña o estrecha.
<b>Resultados</b>
Polígono y ráster de la cuenca; puntos de salida original y ajustado; red de drenaje ordenada y ráster de drenaje dentro de la cuenca; MDE acondicionado; dirección de flujo D8; y acumulación de flujo.
<b>Información importante</b>
&#8226; La distancia máxima de ajuste se expresa en metros, incluso cuando el MDE utiliza un SRC geográfico.
&#8226; Antes de ejecutar GRASS, el algoritmo comprueba la posición del punto de salida, la resolución del MDE, el umbral de drenaje y la distancia de ajuste. Los parámetros incompatibles se notifican antes de crear cualquier resultado.
&#8226; El umbral de drenaje controla tanto la densidad de la red como las celdas disponibles para el ajuste al drenaje más cercano.
&#8226; Compruebe el punto de salida ajustado antes de utilizar la cuenca en análisis de ingeniería, especialmente cerca de confluencias.
<b>Referencia</b>
Documentación de GRASS GIS: <a href="https://grass.osgeo.org/grass-stable/manuals/r.water.outlet.html"><i>r.water.outlet</i></a>, <a href="https://grass.osgeo.org/grass-stable/manuals/r.watershed.html"><i>r.watershed</i></a> y <a href="https://grass.osgeo.org/grass-stable/manuals/r.fill.dir.html"><i>r.fill.dir</i></a>.'''},

}
