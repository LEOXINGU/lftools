# -*- coding: utf-8 -*-

"""
/***************************************************************************
 LFTools
                                 A QGIS plugin
 Tools for cartographic production and spatial analysis.
                              -------------------
        begin                : 2021-03-19
        copyright            : (C) 2021 by Leandro Franca
        email                : geoleandro.franca@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

__author__ = 'Leandro Franca'
__date__ = '2021-03-19'
__copyright__ = '(C) 2021 by Leandro Franca'


from qgis.core import *
from qgis.gui import *
from qgis.utils import qgsfunction
from lftools.geocapt.cartography import (map_sistem,
                                         MeridianConvergence,
                                         SRC_Projeto,
                                         ScaleFactor,
                                         geom2PointList,
                                         reprojectPoints,
                                         areaGauss,
                                         main_azimuth,
                                         inom2mi as INOM2MI)
from lftools.geocapt.topogeo import (dd2dms as DD2DMS,
                                     dms2dd as DMS2DD,
                                     azimute, str2HTML,
                                     geod2geoc, geoc2enu,
                                     gpsdate as GPSDATE)
from lftools import geomag
from lftools.geocapt.imgs import img2html_resized
from numpy import array, pi, sqrt, median
import numpy as np
from pyproj.crs import CRS
import unicodedata
from datetime import datetime, date
import re, os
# https://qgis.org/pyqgis/3.2/core/Expression/QgsExpression.html

LOC = QgsApplication.locale()[:2]
def tr(*string):
    # Traduzir para o portugês: arg[0] - english (translate), arg[1] - português
    if LOC == 'pt':
        if len(string) == 2:
            return string[1]
        else:
            return string[0]
    else:
        return string[0]

@qgsfunction(args='auto', group='LF Tools')
def fieldstat(layer_name, field_name, type, feature, parent):
    ''' Returns the Aggregate function of a layer's field.
        <h2>Example usage:</h2>
        <ul>
          <li>fieldstat('layer_name', 'field_name', 'sum') ->Sum of the values</li>
          <li>fieldstat('layer_name', 'field_name', 'min') ->Min of the values</li>
          <li>fieldstat('layer_name', 'field_name', 'max') ->Max of the values</li>
          <li>fieldstat('layer_name', 'field_name', 'mean') ->Mean of the values</li>
          <li>fieldstat('layer_name', 'field_name', 'std') ->Standard Deviation of the values</li>
          <li>fieldstat('layer_name', 'field_name', 'median') ->Median of the values</li>
        </ul>'''
    lista = []

    if len(QgsProject.instance().mapLayersByName(layer_name)) == 1:
        layer = QgsProject.instance().mapLayersByName(layer_name)[0]
    else:
        layer = QgsProject.instance().mapLayer(layer_name)

    for feat in layer.getFeatures():
        att = feat[field_name]
        if att:
            lista += [float(att)]
    if type == 'sum':
        return  float((array(lista)).sum())
    elif type == 'min':
        return  float((array(lista)).min())
    elif type == 'max':
        return  float((array(lista)).max())
    elif type == 'mean':
        return  float((array(lista)).mean())
    elif type == 'std':
        return  float((array(lista)).std())
    elif type == 'median':
        return  float(median(array(lista)))
    else:
        return None


@qgsfunction(args='auto', group='LF Tools')
def coord2inom(lon, lat, ScaleD, feature, parent):
    """
    Calculates the chart index from coordinates.
    <h2>Example usage:</h2>
    <ul>
      <li>coord2inom(lon, lat, ScaleD) -> inom</li>
      <li>coord2inom(-42.2, -13.4, 1000000) -> SA-23</li>
    </ul>
    """
    lon, lat = lon+1e-10, lat+1e-10
    return map_sistem(lon, lat, ScaleD)


@qgsfunction(args='auto', group='LF Tools')
def dd2dms(dd, n_digits, feature, parent):
    """
    Transform decimal degrees to degrees, minutes and seconds.
    <h2>Example usage:</h2>
    <ul>
      <li>dd2dms(dd, 3) -> -12°12'34.741"</li>
    </ul>
    """
    return DD2DMS(dd, n_digits)


@qgsfunction(args='auto', group='LF Tools')
def dms2dd(txt, feature, parent):
    """
    Transform degrees, minutes, seconds coordinate to decimal degrees.
    <h2>Example usage:</h2>
    <ul>
      <li>dms2dd("dms") -> dd</li>
      <li>dms2dd('-10d30m00.0s') -> -10.5</li>
    </ul>
    """
    return DMS2DD(txt)

@qgsfunction(args='auto', group='LF Tools')
def scalefactor(lon, lat, feature, parent):
    """
    Calculates the Scale (Kappa) Factor based on a feature coordinates.
    <h2>Example usage:</h2>
    <ul>
      <li>scalefactor("lon", "lat") -> 0.99138</li>
    </ul>
    """
    return ScaleFactor(lon, lat)


@qgsfunction(args='auto', group='LF Tools')
def meridianconv(lon, lat, feature, parent):
    """
    Calculates the Meridian Convergence based on a feature coordinates (Longitude and Latitude).
    <h2>Example usage:</h2>
    <ul>
      <li>meridianconv("lon", "lat") -> -0.3451</li>
    </ul>
    """
    SRC = QgsCoordinateReferenceSystem('EPSG:4326')
    return MeridianConvergence(lon, lat, SRC)


@qgsfunction(args='auto', group='LF Tools')
def mainAzimuth(geometry, feature, parent):
    """
    Calculates the principal azimuth of a feature by returning the orientation of the longest side in degrees.
    <h2>Example usage:</h2>
    <ul>
      <li>mainAzimuth(geometry) -> 63.87543</li>
    </ul>
    """
    az = float(main_azimuth(geometry))
    return az


@qgsfunction(args='auto', group='LF Tools')
def magneticdec(lon, lat, h, ano, mes, dia, feature, parent):
    """
    Calculates magnetic declination based on Position (Longitude, Latitude and Altitude), and Date (Year, Month and Day).
    <h2>Example usage:</h2>
    <ul>
      <li>magneticdec("lon", "lat", "h", 2022, 5, 31) -> -21.22381</li>
    </ul>
    <div>
    <p><b>Source:</b></p>
    <p>
    <b><a href="https://github.com/cmweiss/geomag" target="_blank">Christopher Weiss: geomag Python package</a></b>
    </p>
    <p>
    <b><a href="https://www.ngdc.noaa.gov/geomag/geomag.shtml" target="_blank">NCEI Geomagnetic Modeling Team and British Geological Survey. 2019. World Magnetic Model 2020. NOAA National Centers for Environmental Information. doi: 10.25921/11v3-da71, 2020.</a></b>
    </p>
  </div>
    """
    return geomag.declination(lat, lon, h, time = date(ano,mes,dia))


@qgsfunction(args='auto', group='LF Tools')
def inom2mi(inom, feature, parent):
    """
    Determines the MI from INOM.
    <h2>Example usage:</h2>
    <ul>
      <li>inom2mi(inom) -> mi</li>
      <li>inom2mi('SB-25-V-C-I') -> '900'</li>
    </ul>
    """
    dicionario = INOM2MI
    inom_list = inom.split('-')
    inom100k = ''
    resto = ''
    if len(inom_list) >= 5:
        for k in range(5):
            inom100k += inom_list[k]+'-'
        if len(inom_list) > 5:
            for k in range(5,len(inom_list)):
                resto += inom_list[k]+'-'
            if inom100k[:-1] in dicionario:
                return dicionario[inom100k[:-1]]+'-'+resto[:-1]
            else:
                return None
        else:
            if inom100k[:-1] in dicionario:
                return dicionario[inom100k[:-1]]
    else:
        return None


@qgsfunction(args='auto', group='LF Tools')
def projectCRS(output_type, feature, parent):
    """
    Return the descriptive name  or the EPSG code of the Project's CRS.
    <h2>Example usage:</h2>
    <ul>
      <li>ProjectCRS('EPSG') -> EPSG:4674</li>
      <li>ProjectCRS('') -> SIRGAS 2000 / UTM 25 S</li>
    </ul>
    """
    a = QgsProject.instance()
    b = a.crs()
    if output_type == 'EPSG':
        return b.authid()
    else:
        return b.description()


@qgsfunction(args='auto', group='LF Tools')
def layerCRS(layer_name, output_type, feature, parent):
    """
    Return the descriptive name or the EPSG code of a layer's CRS.
    <h2>Example usage:</h2>
    <ul>
      <li>LayerCRS('layer_name','EPSG') -> EPSG:4326</li>
      <li>LayerCRS('layer_name','') -> SIRGAS 2000 / UTM 23 S</li>
    </ul>
    """
    if len(QgsProject.instance().mapLayersByName(layer_name)) == 1:
        layer = QgsProject.instance().mapLayersByName(layer_name)[0]
    else:
        layer = QgsProject.instance().mapLayer(layer_name)
    b = layer.crs()
    if output_type == 'EPSG':
        return b.authid()
    else:
        return b.description()


@qgsfunction(args='auto', group='LF Tools')
def zonehemisf(lon, lat, feature, parent):
    """
    Return the zone and hemisphere from longitude and latitude.
    <h2>Example usage:</h2>
    <ul>
      <li>zonehemisf("lon", "lat") -> 25S</li>
    </ul>
    """
    # Calculo do Fuso
    fuso = round((183+lon)/6.0)
    # Hemisferio
    hemisf = 'N' if lat>= 0 else 'S'
    return str(fuso) + hemisf


@qgsfunction(args='auto', group='LF Tools')
def removespetialchar (text, feature, parent):
    """
    Replaces special characters.
    <h2>Example:</h2>
    <ul>
      <li>removespetialchar('coração') -> coracao </li>
      <li>removespetialchar('gênesis') -> genesis</li>
    </ul>
    """
    # Unicode normalize transforma um caracter em seu equivalente em latin.
    nfkd = unicodedata.normalize('NFKD', text)
    palavraSemAcento = u"".join([c for c in nfkd if not unicodedata.combining(c)])
    # Usa expressão regular para retornar a palavra apenas com números, letras e espaço
    return re.sub('[^a-zA-Z0-9 \\\]', '', palavraSemAcento)


@qgsfunction(args='auto', group='LF Tools')
def gpsdate (datahora, tempo, feature, parent):
    """
    Inputs:
      datetime or unicode datetime string.
    <ul>
      <li>year ('Y')</li>
      <li>month ('M')</li>
      <li>day of month ('DoM')</li>
      <li>day of year ('DoY')</li>
      <li>GPS week ('GPSW')</li>
      <li>day of GPS week ('DoGPSW')</li>
      <li>second of GPS week ('SoGPSW')</li>
      <li>Julian day ('JD')</li>
      <li>decimal year ('DecY')</li>
    </ul>
    <h2>Examples:</h2>
    <ul>
      <li>gpsdate("datatime", 'time') -> time value</li>
      <li>gpsdate('2023-03-01 15:58:40', 'SoGPSW') -> 316720 </li>
    </ul>
    """

    if isinstance(datahora, str):
        dt_hr = datetime.strptime(datahora, '%Y-%m-%d %H:%M:%S')
    else:
        dt_hr = datahora.toPyDateTime()
    Y, M, DoM, Hr, Mn, Sc = dt_hr.year, dt_hr.month, dt_hr.day, dt_hr.hour, dt_hr.minute, dt_hr.second
    [Y,M,DoM,DoY,GPSW,DoGPSW,SoGPSW,JD,DecY] = GPSDATE(Y, M, DoM, Hr, Mn, Sc)
    if tempo.lower() == 'y':
        return Y
    elif tempo.lower() == 'm':
        return M
    elif tempo.lower() == 'dom':
        return DoM
    elif tempo.lower() == 'doy':
        return DoY
    elif tempo.lower() == 'gpsw':
        return GPSW
    elif tempo.lower() == 'dogpsw':
        return DoGPSW
    elif tempo.lower() == 'sogpsw':
        return SoGPSW
    elif tempo.lower() == 'jd':
        return JD
    elif tempo.lower() == 'decy':
        return DecY
    else:
        return None


@qgsfunction(args='auto', group='LF Tools')
def str2html(text, feature, parent):
    """
    Transform a string (text) with special characters into HTML.
    <h2>Examples:</h2>
    <ul>
      <li>str2html (text) -> HTML </li>
      <li>str2html ('Açaí') -> A&amp;ccedil;a&amp;iacute; </li>
    </ul>
    """
    return (str2HTML(text))

@qgsfunction(args='auto', group='LF Tools')
def img2html(filepath, size, feature, parent):
    """
    Reads the photo file from a given path and transforms it into an image in base64 textual format for reading as HTML.
    Images are resized to a new size corresponding to the image's largest side.
    <h2>Examples:</h2>
    <ul>
      <li>img2html (filepath, size) -> HTML </li>
      <li>img2html ('C:\photos\test.jpg', 350) -> HTML </li>
    </ul>
    """

    html = '<img src="data:image/jpg;base64,[FOTO]">'

    if os.path.exists(filepath):
        foto = img2html_resized(filepath, size)
    else:
        foto = ''
    return html.replace('[FOTO]', foto)



@qgsfunction(args='auto', group='LF Tools')
def cusum (layer_name, sequence_field, value_field, group_field, feature, parent):
    """
    Calculates the cumulative sum of attributes considering the sequence and value fields. The group field also can be used, otherwise set as ''.
    <h2>Examples:</h2>
    <ul>
      <li>cusum (layer_name, sequence_field, value_field, group_field) -> cumulative sum </li>
      <li>cusum ('layer_name', 'seq', 'measure', 'class') -> 543.87 </li>
      <li>cusum ('layer_name', 'seq', 'measure', '') -> 943.18 </li>
    </ul>
    """
    if len(QgsProject.instance().mapLayersByName(layer_name)) == 1:
        layer = QgsProject.instance().mapLayersByName(layer_name)[0]
    else:
        layer = QgsProject.instance().mapLayer(layer_name)
    field_names = [campo.name() for campo in layer.fields()]

    if group_field in field_names: # Grupos
        grupos = {}
        for feat in layer.getFeatures():
            if feat[group_field] not in grupos:
                grupos[feat[group_field]] = [feat]
            else:
                grupos[feat[group_field]] += [feat]

        dic = {}
        for grupo in grupos:
            dic2 = {}
            for feat in grupos[grupo]:
                valor = feat[value_field]
                dic2[feat[sequence_field]] = valor

            chaves = list(dic2.keys())
            chaves.sort()

            soma = 0
            for id in chaves:
                soma += dic2[id]
                dic2[id] = soma
            dic[grupo] = dic2
        return dic[feature[group_field]][feature[sequence_field]]

    else:
        dic = {}
        for feat in layer.getFeatures():
            valor = feat[value_field]
            dic[feat[sequence_field]] = valor

        chaves = list(dic.keys())
        chaves.sort()

        soma = 0
        for id in chaves:
            soma += dic[id]
            dic[id] = soma
        return dic[feature[sequence_field]]


# Area no SGL
def areaParteSGL(coordsGeo, coords, crsGeo):
    centroide = QgsGeometry.fromPolygonXY([coordsGeo]).centroid().asPoint()
    alt = []
    for pnt in coords[:-1]:
        if str(pnt.z()) != 'nan':
            alt += [pnt.z()]
        else:
            alt += [0]
    h0 = np.array(alt).mean()
    lon0 = centroide.x()
    lat0 = centroide.y()
    EPSG = int(crsGeo.authid().split(':')[-1]) # pegando o EPGS do SRC do QGIS
    proj_crs = CRS.from_epsg(EPSG) # transformando para SRC do pyproj
    a=proj_crs.ellipsoid.semi_major_metre
    f_inv = proj_crs.ellipsoid.inverse_flattening
    f=1/f_inv
    # CENTRO DE ROTAÇÃO
    Xo, Yo, Zo = geod2geoc(lon0, lat0, h0, a, f)
    # CONVERSÃO DAS COORDENADAS
    coordsSGL = []
    for k, coord in enumerate(coordsGeo):
        lon = coord.x()
        lat = coord.y()
        h = coords[k].z() if str(coords[k].z()) != 'nan' else 0
        X, Y, Z = geod2geoc(lon, lat, h, a, f)
        E, N, U = geoc2enu(X, Y, Z, lon0, lat0, Xo, Yo, Zo)
        coordsSGL += [QgsPointXY(E, N)]
    return abs(areaGauss(coordsSGL))


@qgsfunction(args='auto', group='LF Tools')
def areaLTP (layer_name, feature, parent):
    """
    Calculates the area on the Local Tangent Plane (LTP), also known as Local Geodetic Coordinate System, which is a spatial reference system based on the tangent plane on the feature centroid defined by the local vertical direction.
    <p>Note: PolygonZ or MultiPoligonZ should be used to obtain the most accurate result.</p>
    <h2>Examplo:</h2>
    <ul>
      <li>areaLTP('layer_name') -> 607503.4825 </li>
    </ul>
    <div>
    <p><b>About the LTP:</b></p>
    <p>
    <b><a href="https://geoone.com.br/sistema-geodesico-local/" target="_blank">França, L. Local Geodetic Coordinate System. GeoOne. 2022.</a></b>
    </p>
  </div>
    """
    if len(QgsProject.instance().mapLayersByName(layer_name)) == 1:
        layer = QgsProject.instance().mapLayersByName(layer_name)[0]
    else:
        layer = QgsProject.instance().mapLayer(layer_name)

    geom = feature.geometry()

    if not layer.crs().isGeographic():
        crsProj = layer.crs()
        crsGeo = QgsCoordinateReferenceSystem(crsProj.geographicCrsAuthId())
        coordinateTransformer = QgsCoordinateTransform()
        coordinateTransformer.setDestinationCrs(crsGeo)
        coordinateTransformer.setSourceCrs(crsProj)
        geomGeo = reprojectPoints(geom, coordinateTransformer)
    else:
        geomGeo = geom
        crsGeo = layer.crs()

    if geom.isMultipart():
        coordsM = geom2PointList(geom)
        coordsGeoM = geomGeo.asMultiPolygon()
        areaSGL = 0
        for k, coords in enumerate(coordsM):
            coordsGeo = coordsGeoM[k]
            areaSGL += areaParteSGL(coordsGeo[0], coords[0], crsGeo)

    else:
        coords = geom2PointList(geom)[0]
        coordsGeo = geomGeo.asPolygon()[0]
        areaSGL = areaParteSGL(coordsGeo, coords, crsGeo)

    return areaSGL



@qgsfunction(args='auto', group='LF Tools')
def inter_area (this_layer, other_layer, calc_CRS, filter, feature, parent):
    """
    Calculates for each feature the sum of the intersection areas considering other layer's features, the projected CRS for calculation and a expression filter (optional).
    <h2>Examples:</h2>
    <ul>
      <li>inter_area (this_layer, other_layer, calc_CRS, filter) -> intersection area </li>
      <li>inter_area ('this_layer', 'other_layer', @project_crs, '"classe" = \\\'V\\\'' ) -> 18409.37 </li>
      <li>inter_area ('this_layer', 'other_layer', 'EPSG:31985', '"type" &lt; 4' ) -> 658.12 </li>
      <li>inter_area ('this_layer', 'other_layer', 'EPSG:31984', '' ) -> 1048.432 </li>
    </ul>
    """
    if len(QgsProject.instance().mapLayersByName(this_layer)) == 1:
        layer1 = QgsProject.instance().mapLayersByName(this_layer)[0]
    else:
        layer1 = QgsProject.instance().mapLayer(this_layer)

    if len(QgsProject.instance().mapLayersByName(other_layer)) == 1:
        layer2 = QgsProject.instance().mapLayersByName(other_layer)[0]
    else:
        layer2 = QgsProject.instance().mapLayer(other_layer)

    exp = QgsExpression(filter)
    request = QgsFeatureRequest(exp)

    crs1 = QgsCoordinateReferenceSystem(layer1.crs())
    crs2 = QgsCoordinateReferenceSystem(layer2.crs())
    transf1 = QgsCoordinateTransform()
    transf1.setDestinationCrs(crs1)
    transf1.setSourceCrs(crs2)

    calc_CRS = QgsCoordinateReferenceSystem(calc_CRS)
    transf2 = QgsCoordinateTransform()
    transf2.setDestinationCrs(calc_CRS)
    transf2.setSourceCrs(crs1)

    area = 0
    iterLayer2 = layer2.getFeatures(request) if filter else layer2.getFeatures()
    geom1 = feature.geometry()
    for feat2 in iterLayer2:
        geom2 = feat2.geometry()
        geom2.transform(transf1)
        if geom1.intersects(geom2):
            inter = geom1.intersection(geom2)
            if inter.type() == 2: #Polygon
                inter.transform(transf2)
                area += inter.area()
    return float(area)

@qgsfunction(args='auto', group='LF Tools')
def dinamictable(titulo, campos, apelidos, decimal, fator, feature, parent):
    """
    Generates a dynamic HTML table from a list of numeric fields with the sum of their values for each feature.
    <p>Note: Values equal to zero are ignored.</p>
    <h2>Examples:</h2>
    <ul>
      <li>dinamictable(title, fields, alias, precision, factor) -> HTML</li>
      <li>dinamictable('Table 1', 'field1,field2,field3', 'Field 1,Field 2,Field 3',2, 1) -> HTML</li>
      <li>dinamictable('Report', 'a,b,c', '',2, 0.0001) -> HTML</li>
    </ul>
    """
    campos = campos.replace(' ', '').split(',')
    if apelidos == '':
        apelidos = campos
    else:
        apelidos = apelidos.split(',')

    format_num = '{:,.Xf}'.replace('X', str(decimal))

    tabela = '''
    <!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
    <html>
    <head>
    </head>
    <body>
    <table class="MsoTableGrid"
     style="border: medium none ; margin-left: 14.2pt; border-collapse: collapse;"
     border="1" cellpadding="0" cellspacing="0">
      <tbody>
        <tr style="height: 10.9pt;">
          <td colspan="2"
     style="border: 1pt solid windowtext; padding: 0cm 5.4pt; width: 212.35pt; height: 10.9pt;"
     width="283">
          <p class="MsoBodyText" style="text-align: center;"
     align="center"><span class="eop"><b><span
     style="background: white none repeat scroll 0% 50%; -moz-background-clip: initial; -moz-background-origin: initial; -moz-background-inline-policy: initial; font-size: 8pt; color: black;"
     lang="PT">[TITULO]<o:p></o:p></span></b></span></p>
          </td>
        </tr>
        <tr style="height: 10.95pt;">
          <td
     style="border-style: none solid solid; border-color: -moz-use-text-color windowtext windowtext; border-width: medium 1pt 1pt; padding: 0cm 5.4pt; width: 106.15pt; height: 10.95pt;"
     width="142">
          <p class="MsoBodyText" style="text-align: center;"
     align="center"><span class="eop"><span
     style="background: white none repeat scroll 0% 50%; -moz-background-clip: initial; -moz-background-origin: initial; -moz-background-inline-policy: initial; font-size: 8pt; color: black;"
     lang="PT">''' + tr('CLASS', 'CLASSE') + '''<o:p></o:p></span></span></p>
          </td>
          <td
     style="border-style: none solid solid none; border-color: -moz-use-text-color windowtext windowtext -moz-use-text-color; border-width: medium 1pt 1pt medium; padding: 0cm 5.4pt; width: 106.2pt; height: 10.95pt;"
     width="142">
          <p class="MsoBodyText" style="text-align: center;"
     align="center"><span class="eop"><span
     style="background: white none repeat scroll 0% 50%; -moz-background-clip: initial; -moz-background-origin: initial; -moz-background-inline-policy: initial; font-size: 8pt; color: black;"
     lang="PT">''' + tr('VALUE', 'VALOR') + '''<o:p></o:p></span></span></p>
          </td>
        </tr>
    [LINHAS]
        <tr style="height: 10.95pt;">
          <td
     style="border-style: none solid solid; border-color: -moz-use-text-color windowtext windowtext; border-width: medium 1pt 1pt; padding: 0cm 5.4pt; width: 106.15pt; height: 10.95pt;"
     width="142">
          <p class="MsoBodyText" style="text-align: center;"
     align="center"><span class="eop"><span
     style="background: white none repeat scroll 0% 50%; -moz-background-clip: initial; -moz-background-origin: initial; -moz-background-inline-policy: initial; font-size: 8pt; color: black;"
     lang="PT">''' + tr('SUM', 'TOTAL') + ''':<o:p></o:p></span></span></p>
          </td>
          <td
     style="border-style: none solid solid none; border-color: -moz-use-text-color windowtext windowtext -moz-use-text-color; border-width: medium 1pt 1pt medium; padding: 0cm 5.4pt; width: 106.2pt; height: 10.95pt;"
     width="142">
          <p class="MsoBodyText" style="text-align: center;"
     align="center"><span class="eop"><span
     style="background: white none repeat scroll 0% 50%; -moz-background-clip: initial; -moz-background-origin: initial; -moz-background-inline-policy: initial; font-size: 8pt; color: black;"
     lang="PT">[TOTAL]</span></span></p>
          </td>
        </tr>
      </tbody>
    </table>
    </body>
    </html>'''

    linha = '''<tr style="height: 10.9pt;">
          <td
     style="border-style: none solid solid; border-color: -moz-use-text-color windowtext windowtext; border-width: medium 1pt 1pt; padding: 0cm 5.4pt; width: 106.15pt; height: 10.9pt;"
     width="142">
          <p class="MsoBodyText" style="text-align: center;"
     align="center"><span class="eop"><span
     style="background: white none repeat scroll 0% 50%; -moz-background-clip: initial; -moz-background-origin: initial; -moz-background-inline-policy: initial; font-size: 8pt; color: black;"
     lang="PT">[NOME]<o:p></o:p></span></span></p>
          </td>
          <td
     style="border-style: none solid solid none; border-color: -moz-use-text-color windowtext windowtext -moz-use-text-color; border-width: medium 1pt 1pt medium; padding: 0cm 5.4pt; width: 106.2pt; height: 10.9pt;"
     width="142">
          <p class="MsoBodyText" style="text-align: center;"
     align="center"><span class="eop"><span
     style="background: white none repeat scroll 0% 50%; -moz-background-clip: initial; -moz-background-origin: initial; -moz-background-inline-policy: initial; font-size: 8pt; color: black;"
     lang="PT"><o:p>[VALOR]&nbsp;</o:p></span></span></p>
          </td>
        </tr>
    '''

    soma = 0
    dic = {}
    for k, campo in enumerate(campos):
        valor = round(feature[campo]*fator, decimal)
        if valor > 0:
            soma = soma + valor
            if valor > 10**(-1*decimal):
                dic[apelidos[k]] = valor
    lista = list(dic.keys())
    lista.sort()
    linhas =''
    for item in lista:
        linha0 = linha
        linha0 = linha0.replace('[NOME]', item).replace('[VALOR]', format_num.format(dic[item]).replace(',', 'X').replace('.', ',').replace('X', '.'))
        linhas += linha0
    texto = tabela
    texto = texto.replace('[LINHAS]', linhas).replace('[TITULO]', str2HTML(titulo)).replace('[TOTAL]', format_num.format(soma).replace(',', 'X').replace('.', ',').replace('X', '.'))

    return texto



@qgsfunction(args='auto', group='LF Tools')
def deedtable(layer_name, ini, fim, titulo, fontsize, feature, parent):
    """
    Generates the Vertices and Sides Descriptive Table, also known as Synthetic Deed Description, based on the attributes, sequence and code, in the point layer's attribute table.
    <p>Note: The table title must be inserted as string.</p>
    <h2>Exemple:</h2>
    <ul>
      <li>deedtable('layer_name', start, end, 'title',fontsize) = HTML</li>
      <li>deedtable('Limit Point', 1, 20, 'Area X',10) = HTML</li>
    </ul>
    """
    # Templates HTML
    texto = '''<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
    <html>
    <head>
      <title>''' + tr('Synthetic deed description', str2HTML('Memorial Sintético')) + '''</title>    </head>
    <body>
    <table
    style="text-align: center; width: 100%; font-size: [FONTSIZE]px; font-family: Arial;"
    border="1" cellpadding="0" cellspacing="0">
    <tbody>
    [CABECALHO]
    [LINHAS]
    </tbody>
    </table>
    <br>
    </body>
    </html>
    '''
    linha = '''<tr>
      <td>Vn</td>
      <td>En</td>
      <td>Nn</td>
      <td>hn</td>
      <td>Ln</td>
      <td>Az_n</td>
      <td>Dn</td>
    </tr>
    '''
    cabec = '''<tr>
      <td colspan="7" rowspan="1">''' + tr('Synthetic deed description'.upper(), str2HTML('Memorial Sintético'.upper())) + '''[TITULO]</td>
    </tr>
    <tr>
      <td colspan="1" rowspan="2">''' + tr('VERTEX', str2HTML('VÉRTICE')) + '''</td>
      <td colspan="3" rowspan="1">''' + tr('COORDINATE', str2HTML('COORDENADA')) + '''</td>
      <td colspan="1" rowspan="2">''' + tr('SIDE', str2HTML('LADO')) + '''</td>
      <td colspan="1" rowspan="2">''' + tr('AZIMUTH', str2HTML('AZIMUTE')) + '''</td>
      <td colspan="1" rowspan="2">''' + tr('DISTANCE', str2HTML('DISTÂNCIA')) + ''' (m)</td>
    </tr>
    <tr>
      <td>E</td>
      <td>N</td>
      <td>h</td>
    </tr>'''

    decimal = 2
    format_num = '{:,.Xf}'.replace('X', str(decimal))

    # Camada de Pontos
    if len(QgsProject.instance().mapLayersByName(layer_name)) == 1:
        layer = QgsProject.instance().mapLayersByName(layer_name)[0]
    else:
        layer = QgsProject.instance().mapLayer(layer_name)
    SRC = layer.crs()
    pnts_UTM = {}
    pnts_GEO = {}
    # Transformacao de Coordenadas Geograficas para Projetadas no sistema UTM
    crsDest = QgsCoordinateReferenceSystem(SRC_Projeto('EPSG'))
    coordinateTransformer = QgsCoordinateTransform()
    coordinateTransformer.setDestinationCrs(crsDest)
    coordinateTransformer.setSourceCrs(SRC)
    for feat in layer.getFeatures():
        pnt = feat.geometry().asPoint()
        coord = geom2PointList(feat.geometry())
        pnts_UTM[feat['sequence']] = [coordinateTransformer.transform(pnt), feat['type'], feat['code'], MeridianConvergence(pnt.x(), pnt.y(), crsDest) ]
        pnts_GEO[feat['sequence']] = [QgsPoint(pnt.x(),pnt.y(),coord.z()), feat['type'], feat['code'] ]

    # Calculo dos Azimutes e Distancias
    tam = len(pnts_UTM)
    Az_lista, Az_Geo_lista, Dist = [], [], []
    for k in range(tam):
        pntA = pnts_UTM[k+1][0]
        pntB = pnts_UTM[1 if k+2 > tam else k+2][0]
        Az_lista += [(180/pi)*azimute(pntA, pntB)[0]]
        ConvMerediana = pnts_UTM[k+1][3]
        Az_Geo_lista += [(180/pi)*azimute(pntA, pntB)[0]+ConvMerediana]
        Dist += [sqrt((pntA.x() - pntB.x())**2 + (pntA.y() - pntB.y())**2)]

    LINHAS = ''
    if fim == -1 or fim > tam:
        fim = tam
    for k in range(ini-1,fim):
        linha0 = linha
        itens = {'Vn': pnts_UTM[k+1][2],
                    'En':tr(format_num.format(pnts_UTM[k+1][0].x()), format_num.format(pnts_UTM[k+1][0].x()).replace(',', 'X').replace('.', ',').replace('X', '.')),
                    'Nn':tr(format_num.format(pnts_UTM[k+1][0].y()), format_num.format(pnts_UTM[k+1][0].y()).replace(',', 'X').replace('.', ',').replace('X', '.')),
                    'hn':tr(format_num.format(pnts_GEO[k+1][0].z()), format_num.format(pnts_GEO[k+1][0].z()).replace(',', 'X').replace('.', ',').replace('X', '.')),
                    'lonn':tr(DD2DMS(pnts_GEO[k+1][0].x(),decimal + 3), DD2DMS(pnts_GEO[k+1][0].x(),decimal + 3).replace('.', ',')),
                    'latn':tr(DD2DMS(pnts_GEO[k+1][0].y(),decimal + 3), DD2DMS(pnts_GEO[k+1][0].y(),decimal + 3).replace('.', ',')),
                    'Ln': pnts_UTM[k+1][2] + '/' + pnts_UTM[1 if k+2 > tam else k+2][2],
                    'Az_n':tr(DD2DMS(Az_lista[k],1), DD2DMS(Az_lista[k],1).replace('.', ',')),
                    'Dn':tr(format_num.format(Dist[k]), format_num.format(Dist[k]).replace(',', 'X').replace('.', ',').replace('X', '.'))
                    }
        for item in itens:
            linha0 = linha0.replace(item, itens[item])
        LINHAS += linha0
    resultado = texto.replace('[CABECALHO]', cabec).replace('[LINHAS]', LINHAS).replace('[TITULO]', str2HTML(titulo.upper())).replace('[FONTSIZE]', str(fontsize))
    return resultado



@qgsfunction(args='auto', group='LF Tools')
def deedtable2(prefix, titulo, decimal, fontsize, layer_name, tipo, azimuteDist, feature, parent):
    """
    Generates the 2D Vertices and Sides Descriptive Table, also known as Synthetic Deed Description, based on vertices of a Polygon or MultiPoligon.
    <p>Note 1: A layer or QGIS Project with a projected SRC is required.</p>
    <p>Note 2: Table types: 'proj' - projected, 'geo' - geographic, 'both' - both coordinate systems.</p>
    <p>Note 3: Define 1 or 0 for with or without azimuths and distances, respectivelly.</p>

    <h2>Exemples:</h2>
    <ul>
      <li>deedtable2('preffix', 'title', precision, fontsize, layer_name, type, azimuth_dist) = HTML</li>
      <li>deedtable2('V-', ' - Area X', 3, 12, 'layer_name', 'proj', 1) = HTML</li>
      <li>deedtable2('V-', ' - Area X', 3, 12, 'layer_name', 'geo', 0) = HTML</li>
      <li>deedtable2('V-', ' - Area X', 3, 12, 'layer_name', 'both', 1) = HTML</li>
    </ul>
    """
    if len(QgsProject.instance().mapLayersByName(layer_name)) == 1:
        layer = QgsProject.instance().mapLayersByName(layer_name)[0]
    else:
        layer = QgsProject.instance().mapLayer(layer_name)

    SRC = layer.crs()
    SGR = QgsCoordinateReferenceSystem(SRC.geographicCrsAuthId())

    format_num = '{:,.Xf}'.replace('X', str(decimal))

    geom = feature.geometry()
    TipoGeometria = geom.type()
    if geom and TipoGeometria in [1,2]:

        if TipoGeometria == 2: # Polígono
            if geom.isMultipart():
                coords = geom2PointList(geom)[0][0]
            else:
                coords = geom2PointList(geom)[0]
        else: # Linha
            if geom.isMultipart():
                coords = geom2PointList(geom)[0]
            else:
                coords = geom2PointList(geom)

        pnts_UTM = {}
        pnts_GEO = {}

        # Prefixo
        try:
            descricao, id, nome = prefix.replace(' ', '').split(',') #nome da camada, ID, atributo
            if len(QgsProject.instance().mapLayersByName(descricao)) == 1:
                layer = QgsProject.instance().mapLayersByName(descricao)[0]
            campos = [field.name() for field in layer.fields()]
            # Camadas de polígono e confrontantes deve estar com o mesmo SRC
            filter = '"{}" = {}'.format(id, feature.id())
            exp = QgsExpression(filter)
            if id not in campos or nome not in campos:
                prefixo = str(prefix)
        except:
            prefixo = str(prefix)

        # Pegando valores dos pontos
        if not SRC.isGeographic(): # Projetado
            coordinateTransformer = QgsCoordinateTransform()
            coordinateTransformer.setDestinationCrs(SGR)
            coordinateTransformer.setSourceCrs(SRC)

            for k, coord in enumerate(coords[:-1] if TipoGeometria == 2 else coords):
                pnt = coordinateTransformer.transform(QgsPointXY(coord.x(), coord.y()))
                if 'prefixo' in locals():
                    pnts_UTM[k+1] = [coord, prefixo, prefixo + '{:02}'.format(k+1)]
                    pnts_GEO[k+1] = [QgsPoint(pnt.x(),pnt.y(),coord.z()), prefixo, prefixo + '{:02}'.format(k+1) ]
                else:
                    for feat in layer.getFeatures(QgsFeatureRequest(exp)):
                        # Identificar ponto correspondente
                        pnt_corresp = feat.geometry().asPoint()
                        if coord.x() == pnt_corresp.x() and coord.y() == pnt_corresp.y():
                            prefix = feat[nome]
                            pnts_UTM[k+1] = [coord, prefix, prefix]
                            pnts_GEO[k+1] = [QgsPoint(pnt.x(),pnt.y(),coord.z()), prefix, prefix ]
                            break
                    else:
                        prefix = '?'
                        pnts_UTM[k+1] = [coord, prefix, prefix]
                        pnts_GEO[k+1] = [QgsPoint(pnt.x(),pnt.y(),coord.z()), prefix, prefix]

            try:
                projecao = SRC.description().split(r' / ')[-1]
                PROJ = tr(projecao, projecao.replace('zone', 'fuso'))
            except:
                PROJ = SRC.description()

        else: # Geográfico
            CRS_projeto = QgsCoordinateReferenceSystem(SRC_Projeto('EPSG'))
            coordinateTransformer = QgsCoordinateTransform()
            coordinateTransformer.setDestinationCrs(CRS_projeto)
            coordinateTransformer.setSourceCrs(SRC)
            for k, coord in enumerate(coords[:-1] if TipoGeometria == 2 else coords):
                pnt = coordinateTransformer.transform(QgsPointXY(coord.x(), coord.y()))
                if 'prefixo' in locals():
                    pnts_GEO[k+1] = [coord, prefixo, prefixo + '{:02}'.format(k+1)]
                    pnts_UTM[k+1] = [QgsPoint(pnt.x(),pnt.y(),coord.z()), prefixo, prefixo + '{:02}'.format(k+1) ]
                else:
                    for feat in layer.getFeatures(QgsFeatureRequest(exp)):
                        # Identificar ponto correspondente
                        pnt_corresp = feat.geometry().asPoint()
                        if coord.x() == pnt_corresp.x() and coord.y() == pnt_corresp.y():
                            prefix = feat[nome]
                            pnts_GEO[k+1] = [coord, prefix, prefix]
                            pnts_UTM[k+1] = [QgsPoint(pnt.x(),pnt.y(),coord.z()), prefix, prefix]
                            break
                    else:
                        prefix = '?'
                        pnts_GEO[k+1] = [coord, prefix, prefix]
                        pnts_UTM[k+1] = [QgsPoint(pnt.x(),pnt.y(),coord.z()), prefix, prefix]

            try:
                projecao = CRS_projeto.description().split(r' / ')[-1]
                PROJ = tr(projecao, projecao.replace('zone', 'fuso'))
            except:
                PROJ = SRC.description()

        # Calculo dos Azimutes e Distancias
        tam = len(pnts_UTM)
        Az_lista, Dist = [], []
        if TipoGeometria == 2:
            for k in range(tam):
                pntA = pnts_UTM[k+1][0]
                pntB = pnts_UTM[1 if k+2 > tam else k+2][0]
                Az_lista += [(180/pi)*azimute(pntA, pntB)[0]]
                Dist += [sqrt((pntA.x() - pntB.x())**2 + (pntA.y() - pntB.y())**2)]
        else:
            for k in range(tam-1):
                pntA = pnts_UTM[k+1][0]
                pntB = pnts_UTM[k+2][0]
                Az_lista += [(180/pi)*azimute(pntA, pntB)[0]]
                Dist += [sqrt((pntA.x() - pntB.x())**2 + (pntA.y() - pntB.y())**2)]

        texto = '''<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
        <html>
        <head>
          <title>''' + tr('Synthetic deed description', str2HTML('Memorial Sintético')) + '''</title>    </head>
        <body>
        <table
        style="text-align: center; width: 100%; font-size: [FONTSIZE]px; font-family: Arial; border: medium none; border-collapse: collapse;"
        border="1" cellpadding="0" cellspacing="0">
        <tbody>
        [CABECALHO]
        [LINHAS]
        </tbody>
        </table>
        <br>
        </body>
        </html>
        '''

        #Tipos de cabeçalhos

        # UTM
        if tipo == 'proj' and azimuteDist == 1:
            linha = '''<tr>
          <td>Vn</td>
          <td>En</td>
          <td>Nn</td>
          <td>Ln</td>
          <td>Az_n</td>
          <td>Dn</td>
        </tr>
        '''
            cabec = '''<tr>
              <td colspan="6" rowspan="1">''' + tr('Synthetic deed description'.upper(), str2HTML('Memorial Sintético'.upper())) + '''[TITULO]</td>
            </tr>
            <tr>
              <td colspan="1" rowspan="2">''' + tr('VERTEX', str2HTML('VÉRTICE')) + '''</td>
              <td colspan="2" rowspan="1">''' + tr('COORDINATE', str2HTML('COORDENADA')) + '''</td>
              <td colspan="1" rowspan="2">''' + tr('SIDE', str2HTML('LADO')) + '''</td>
              <td colspan="1" rowspan="2">''' + tr('AZIMUTH', str2HTML('AZIMUTE')) + '''</td>
              <td colspan="1" rowspan="2">''' + tr('DISTANCE', str2HTML('DISTÂNCIA')) + ''' (m)</td>
            </tr>
            <tr>
              <td>E</td>
              <td>N</td>
            </tr>'''

        # UTM sem Az e d
        if tipo == 'proj' and azimuteDist == 0:
            linha = '''<tr>
          <td>Vn</td>
          <td>En</td>
          <td>Nn</td>
        </tr>
        '''

            cabec = '''<tr>
              <td colspan="3" rowspan="1">''' + tr('Synthetic deed description'.upper(), str2HTML('Memorial Sintético'.upper())) + '''[TITULO]</td>
            </tr>
            <tr>
              <td colspan="1" rowspan="2">''' + tr('VERTEX', str2HTML('VÉRTICE')) + '''</td>
              <td colspan="2" rowspan="1">''' + tr('COORDINATE', str2HTML('COORDENADA')) + '''</td>
            </tr>
            <tr>
              <td>E</td>
              <td>N</td>
            </tr>'''

        # GEO
        if tipo == 'geo' and azimuteDist == 1:
            linha = '''<tr>
              <td>Vn</td>
              <td>lonn</td>
              <td>latn</td>
              <td>Ln</td>
              <td>Az_n</td>
              <td>Dn</td>
            </tr>
            '''
            cabec = '''<tr>
              <td colspan="6" rowspan="1">''' + tr('Synthetic deed description'.upper(), str2HTML('Memorial Sintético'.upper())) + '''[TITULO]</td>
            </tr>
            <tr>
              <td colspan="1" rowspan="2">''' + tr('VERTEX', str2HTML('VÉRTICE')) + '''</td>
              <td colspan="2" rowspan="1">''' + tr('COORDINATE', str2HTML('COORDENADA')) + '''</td>
              <td colspan="1" rowspan="2">''' + tr('SIDE', str2HTML('LADO')) + '''</td>
              <td colspan="1" rowspan="2">''' + tr('AZIMUTH', str2HTML('AZIMUTE')) + '''</td>
              <td colspan="1" rowspan="2">''' + tr('DISTANCE', str2HTML('DISTÂNCIA')) + ''' (m)</td>
            </tr>
            <tr>
              <td>longitude</td>
              <td>latitude</td>
            </tr>'''

        # GEO sem Az e d
        if tipo == 'geo' and azimuteDist == 0:
            linha = '''<tr>
              <td>Vn</td>
              <td>lonn</td>
              <td>latn</td>
            </tr>
            '''

            cabec = '''<tr>
              <td colspan="3" rowspan="1">''' + tr('Synthetic deed description'.upper(), str2HTML('Memorial Sintético'.upper())) + '''[TITULO]</td>
            </tr>
            <tr>
              <td colspan="1" rowspan="2">''' + tr('VERTEX', str2HTML('VÉRTICE')) + '''</td>
              <td colspan="2" rowspan="1">''' + tr('COORDINATE', str2HTML('COORDENADA')) + '''</td>
            </tr>
            <tr>
              <td>longitude</td>
              <td>latitude</td>
            </tr>'''

        # UTM e GEO
        if tipo == 'both' and azimuteDist == 1:
            linha = '''<tr>
              <td>Vn</td>
              <td>lonn</td>
              <td>latn</td>
              <td>En</td>
              <td>Nn</td>
              <td>Ln</td>
              <td>Az_n</td>
              <td>Dn</td>
            </tr>
            '''

            cabec = '''<tr>
              <td colspan="8" rowspan="1">''' + tr('Synthetic deed description'.upper(), str2HTML('Memorial Sintético'.upper())) + '''[TITULO]</td>
            </tr>
            <tr>
              <td colspan="1" rowspan="2">''' + tr('VERTEX', str2HTML('VÉRTICE')) + '''</td>
              <td colspan="4" rowspan="1">''' + tr('COORDINATE', str2HTML('COORDENADA')) + '''</td>
              <td colspan="1" rowspan="2">''' + tr('SIDE', str2HTML('LADO')) + '''</td>
              <td colspan="1" rowspan="2">''' + tr('AZIMUTH', str2HTML('AZIMUTE')) + '''</td>
              <td colspan="1" rowspan="2">''' + tr('DISTANCE', str2HTML('DISTÂNCIA')) + ''' (m)</td>
            </tr>
            <tr>
              <td>longitude</td>
              <td>latitude</td>
              <td>E</td>
              <td>N</td>
            </tr>'''

        # UTM e GEO sem Az e d
        if tipo == 'both' and azimuteDist == 0:
            linha = '''<tr>
              <td>Vn</td>
              <td>lonn</td>
              <td>latn</td>
              <td>En</td>
              <td>Nn</td>
            </tr>
            '''

            cabec = '''<tr>
              <td colspan="5" rowspan="1">''' + tr('Synthetic deed description'.upper(), str2HTML('Memorial Sintético'.upper())) + '''[TITULO]</td>
            </tr>
            <tr>
              <td colspan="1" rowspan="2">''' + tr('VERTEX', str2HTML('VÉRTICE')) + '''</td>
              <td colspan="4" rowspan="1">''' + tr('COORDINATE', str2HTML('COORDENADA')) + '''</td>
            </tr>
            <tr>
              <td>longitude</td>
              <td>latitude</td>
              <td>E</td>
              <td>N</td>
            </tr>'''

        LINHAS = ''
        for k in range(tam):
            linha0 = linha
            itens = {'Vn': pnts_UTM[k+1][2],
                        'En': tr(format_num.format(pnts_UTM[k+1][0].x()), format_num.format(pnts_UTM[k+1][0].x()).replace(',', 'X').replace('.', ',').replace('X', '.')),
                        'Nn': tr(format_num.format(pnts_UTM[k+1][0].y()), format_num.format(pnts_UTM[k+1][0].y()).replace(',', 'X').replace('.', ',').replace('X', '.')),
                        'lonn': tr(DD2DMS(pnts_GEO[k+1][0].x(),decimal + 3), DD2DMS(pnts_GEO[k+1][0].x(),decimal + 3).replace('.', ',')),
                        'latn': tr(DD2DMS(pnts_GEO[k+1][0].y(),decimal + 3), DD2DMS(pnts_GEO[k+1][0].y(),decimal + 3).replace('.', ',')),
                        'Ln': '-' if TipoGeometria == 1 and k+1 == tam else pnts_UTM[k+1][2] + '/' + pnts_UTM[1 if k+2 > tam else k+2][2],
                        'Az_n': '-' if TipoGeometria == 1 and k+1 == tam else tr(DD2DMS(Az_lista[k],1), DD2DMS(Az_lista[k],1).replace('.', ',')),
                        'Dn': '-' if TipoGeometria == 1 and k+1 == tam else tr(format_num.format(Dist[k]), format_num.format(Dist[k]).replace(',', 'X').replace('.', ',').replace('X', '.'))
                        }
            for item in itens:
                linha0 = linha0.replace(item, itens[item])
            LINHAS += linha0

        resultado = texto.replace('[CABECALHO]', cabec).replace('[LINHAS]', LINHAS).replace('[TITULO]', str2HTML(titulo.upper())).replace('[FONTSIZE]', str(fontsize))

        return resultado

    else:
        return tr('Check if the geometry is null or invalid! Or if Atlas is on!', 'Verifique se a geometria é nula ou inválida! Ou se o Atlas está ligado!')



@qgsfunction(args='auto', group='LF Tools')
def deedtable3(prefix, titulo, decimal, fontsize, layer_name, tipo, azimuteDist, feature, parent):
    """
    Generates the 3D Vertices and Sides Descriptive Table, also known as Synthetic Deed Description, based on vertices of a PolygonZ or MultiPoligonZ.
    <p>Note 1: A layer or QGIS Project with a projected SRC is required.</p>
    <p>Note 2: Table types: 'proj' - projected, 'geo' - geographic, 'both' - both coordinate systems.</p>
    <p>Note 3: Define 1 or 0 for with or without azimuths and distances, respectivelly.</p>

    <h2>Exemples:</h2>
    <ul>
      <li>deedtable3('preffix', 'title', precision, fontsize, layer_name, type, azimuth_dist) = HTML</li>
      <li>deedtable3('V-', ' - Area X', 3, 12, 'layer_name', 'proj', 1) = HTML</li>
      <li>deedtable3('V-', ' - Area X', 3, 12, 'layer_name', 'geo', 0) = HTML</li>
      <li>deedtable3('V-', ' - Area X', 3, 12, 'layer_name', 'both', 1) = HTML</li>
    </ul>
    """
    if len(QgsProject.instance().mapLayersByName(layer_name)) == 1:
        layer = QgsProject.instance().mapLayersByName(layer_name)[0]
    else:
        layer = QgsProject.instance().mapLayer(layer_name)

    SRC = layer.crs()
    SGR = QgsCoordinateReferenceSystem(SRC.geographicCrsAuthId())

    format_num = '{:,.Xf}'.replace('X', str(decimal))

    geom = feature.geometry()
    TipoGeometria = geom.type()
    if geom and TipoGeometria in [1,2]:

        if TipoGeometria == 2: # Polígono
            if geom.isMultipart():
                coords = geom2PointList(geom)[0][0]
            else:
                coords = geom2PointList(geom)[0]
        else: # Linha
            if geom.isMultipart():
                coords = geom2PointList(geom)[0]
            else:
                coords = geom2PointList(geom)

        pnts_UTM = {}
        pnts_GEO = {}

        # Prefixo
        try:
            descricao, id, nome = prefix.replace(' ', '').split(',') #nome da camada, ID, atributo
            if len(QgsProject.instance().mapLayersByName(descricao)) == 1:
                layer = QgsProject.instance().mapLayersByName(descricao)[0]
            campos = [field.name() for field in layer.fields()]
            # Camadas de polígono e confrontantes deve estar com o mesmo SRC
            filter = '"{}" = {}'.format(id, feature.id())
            exp = QgsExpression(filter)
            if id not in campos or nome not in campos:
                prefixo = str(prefix)
        except:
            prefixo = str(prefix)

        # Pegando valores dos pontos
        if not SRC.isGeographic(): # Projetado
            coordinateTransformer = QgsCoordinateTransform()
            coordinateTransformer.setDestinationCrs(SGR)
            coordinateTransformer.setSourceCrs(SRC)

            for k, coord in enumerate(coords[:-1] if TipoGeometria == 2 else coords):
                pnt = coordinateTransformer.transform(QgsPointXY(coord.x(), coord.y()))
                if 'prefixo' in locals():
                    pnts_UTM[k+1] = [coord, prefixo, prefixo + '{:02}'.format(k+1)]
                    pnts_GEO[k+1] = [QgsPoint(pnt.x(),pnt.y(),coord.z()), prefixo, prefixo + '{:02}'.format(k+1) ]
                else:
                    for feat in layer.getFeatures(QgsFeatureRequest(exp)):
                        # Identificar ponto correspondente
                        pnt_corresp = feat.geometry().asPoint()
                        if coord.x() == pnt_corresp.x() and coord.y() == pnt_corresp.y():
                            prefix = feat[nome]
                            pnts_UTM[k+1] = [coord, prefix, prefix]
                            pnts_GEO[k+1] = [QgsPoint(pnt.x(),pnt.y(),coord.z()), prefix, prefix ]
                            break
                    else:
                        prefix = '?'
                        pnts_UTM[k+1] = [coord, prefix, prefix]
                        pnts_GEO[k+1] = [QgsPoint(pnt.x(),pnt.y(),coord.z()), prefix, prefix]

            try:
                projecao = SRC.description().split(r' / ')[-1]
                PROJ = tr(projecao, projecao.replace('zone', 'fuso'))
            except:
                PROJ = SRC.description()

        else: # Geográfico
            CRS_projeto = QgsCoordinateReferenceSystem(SRC_Projeto('EPSG'))
            coordinateTransformer = QgsCoordinateTransform()
            coordinateTransformer.setDestinationCrs(CRS_projeto)
            coordinateTransformer.setSourceCrs(SRC)
            for k, coord in enumerate(coords[:-1] if TipoGeometria == 2 else coords):
                pnt = coordinateTransformer.transform(QgsPointXY(coord.x(), coord.y()))
                if 'prefixo' in locals():
                    pnts_GEO[k+1] = [coord, prefixo, prefixo + '{:02}'.format(k+1)]
                    pnts_UTM[k+1] = [QgsPoint(pnt.x(),pnt.y(),coord.z()), prefixo, prefixo + '{:02}'.format(k+1) ]
                else:
                    for feat in layer.getFeatures(QgsFeatureRequest(exp)):
                        # Identificar ponto correspondente
                        pnt_corresp = feat.geometry().asPoint()
                        if coord.x() == pnt_corresp.x() and coord.y() == pnt_corresp.y():
                            prefix = feat[nome]
                            pnts_GEO[k+1] = [coord, prefix, prefix]
                            pnts_UTM[k+1] = [QgsPoint(pnt.x(),pnt.y(),coord.z()), prefix, prefix]
                            break
                    else:
                        prefix = '?'
                        pnts_GEO[k+1] = [coord, prefix, prefix]
                        pnts_UTM[k+1] = [QgsPoint(pnt.x(),pnt.y(),coord.z()), prefix, prefix]

            try:
                projecao = CRS_projeto.description().split(r' / ')[-1]
                PROJ = tr(projecao, projecao.replace('zone', 'fuso'))
            except:
                PROJ = SRC.description()

        # Calculo dos Azimutes e Distancias
        tam = len(pnts_UTM)
        Az_lista, Dist = [], []
        for k in range(tam):
            pntA = pnts_UTM[k+1][0]
            pntB = pnts_UTM[1 if k+2 > tam else k+2][0]
            Az_lista += [(180/pi)*azimute(pntA, pntB)[0]]
            Dist += [sqrt((pntA.x() - pntB.x())**2 + (pntA.y() - pntB.y())**2)]

        texto = '''<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
        <html>
        <head>
          <title>''' + tr('Synthetic deed description', str2HTML('Memorial Sintético')) + '''</title>    </head>
        <body>
        <table class="MsoTableGrid"
        style="text-align: center; width: 100%; font-size: [FONTSIZE]px; font-family: Arial; border: medium none ; border-collapse: collapse;"
        border="1" cellpadding="0" cellspacing="0">
        <tbody>
        [CABECALHO]
        [LINHAS]
        </tbody>
        </table>
        <br>
        </body>
        </html>
        '''

        #Tipos de cabeçalhos

        # UTM
        if tipo == 'proj' and azimuteDist == 1:
            linha = '''<tr>
          <td>Vn</td>
          <td>En</td>
          <td>Nn</td>
          <td>hn</td>
          <td>Ln</td>
          <td>Az_n</td>
          <td>Dn</td>
        </tr>
        '''
            cabec = '''<tr>
              <td colspan="7" rowspan="1">''' + tr('Synthetic deed description'.upper(), str2HTML('Memorial Sintético'.upper())) + '''[TITULO]</td>
            </tr>
            <tr>
              <td colspan="1" rowspan="2">''' + tr('VERTEX', str2HTML('VÉRTICE')) + '''</td>
              <td colspan="3" rowspan="1">''' + tr('COORDINATE', str2HTML('COORDENADA')) + '''</td>
              <td colspan="1" rowspan="2">''' + tr('SIDE', str2HTML('LADO')) + '''</td>
              <td colspan="1" rowspan="2">''' + tr('AZIMUTH', str2HTML('AZIMUTE')) + '''</td>
              <td colspan="1" rowspan="2">''' + tr('DISTANCE', str2HTML('DISTÂNCIA')) + ''' (m)</td>
            </tr>
            <tr>
              <td>E</td>
              <td>N</td>
              <td>h</td>
            </tr>'''

        # UTM sem Az e d
        if tipo == 'proj' and azimuteDist == 0:
            linha = '''<tr>
          <td>Vn</td>
          <td>En</td>
          <td>Nn</td>
          <td>hn</td>
        </tr>
        '''

            cabec = '''<tr>
              <td colspan="4" rowspan="1">''' + tr('Synthetic deed description'.upper(), str2HTML('Memorial Sintético'.upper())) + '''[TITULO]</td>
            </tr>
            <tr>
              <td colspan="1" rowspan="2">''' + tr('VERTEX', str2HTML('VÉRTICE')) + '''</td>
              <td colspan="3" rowspan="1">''' + tr('COORDINATE', str2HTML('COORDENADA')) + '''</td>
            </tr>
            <tr>
              <td>E</td>
              <td>N</td>
              <td>h</td>
            </tr>'''

        # GEO
        if tipo == 'geo' and azimuteDist == 1:
            linha = '''<tr>
              <td>Vn</td>
              <td>lonn</td>
              <td>latn</td>
              <td>hn</td>
              <td>Ln</td>
              <td>Az_n</td>
              <td>Dn</td>
            </tr>
            '''
            cabec = '''<tr>
              <td colspan="7" rowspan="1">''' + tr('Synthetic deed description'.upper(), str2HTML('Memorial Sintético'.upper())) + '''[TITULO]</td>
            </tr>
            <tr>
              <td colspan="1" rowspan="2">''' + tr('VERTEX', str2HTML('VÉRTICE')) + '''</td>
              <td colspan="3" rowspan="1">''' + tr('COORDINATE', str2HTML('COORDENADA')) + '''</td>
              <td colspan="1" rowspan="2">''' + tr('SIDE', str2HTML('LADO')) + '''</td>
              <td colspan="1" rowspan="2">''' + tr('AZIMUTH', str2HTML('AZIMUTE')) + '''</td>
              <td colspan="1" rowspan="2">''' + tr('DISTANCE', str2HTML('DISTÂNCIA')) + ''' (m)</td>
            </tr>
            <tr>
              <td>longitude</td>
              <td>latitude</td>
              <td>h</td>
            </tr>'''

        # GEO sem Az e d
        if tipo == 'geo' and azimuteDist == 0:
            linha = '''<tr>
              <td>Vn</td>
              <td>lonn</td>
              <td>latn</td>
              <td>hn</td>
            </tr>
            '''

            cabec = '''<tr>
              <td colspan="4" rowspan="1">''' + tr('Synthetic deed description'.upper(), str2HTML('Memorial Sintético'.upper())) + '''[TITULO]</td>
            </tr>
            <tr>
              <td colspan="1" rowspan="2">''' + tr('VERTEX', str2HTML('VÉRTICE')) + '''</td>
              <td colspan="3" rowspan="1">''' + tr('COORDINATE', str2HTML('COORDENADA')) + '''</td>
            </tr>
            <tr>
              <td>longitude</td>
              <td>latitude</td>
              <td>h</td>
            </tr>'''

        # UTM e GEO
        if tipo == 'both' and azimuteDist == 1:
            linha = '''<tr>
              <td>Vn</td>
              <td>lonn</td>
              <td>latn</td>
              <td>En</td>
              <td>Nn</td>
              <td>hn</td>
              <td>Ln</td>
              <td>Az_n</td>
              <td>Dn</td>
            </tr>
            '''

            cabec = '''<tr>
              <td colspan="9" rowspan="1">''' + tr('Synthetic deed description'.upper(), str2HTML('Memorial Sintético'.upper())) + '''[TITULO]</td>
            </tr>
            <tr>
              <td colspan="1" rowspan="2">''' + tr('VERTEX', str2HTML('VÉRTICE')) + '''</td>
              <td colspan="5" rowspan="1">''' + tr('COORDINATE', str2HTML('COORDENADA')) + '''</td>
              <td colspan="1" rowspan="2">''' + tr('SIDE', str2HTML('LADO')) + '''</td>
              <td colspan="1" rowspan="2">''' + tr('AZIMUTH', str2HTML('AZIMUTE')) + '''</td>
              <td colspan="1" rowspan="2">''' + tr('DISTANCE', str2HTML('DISTÂNCIA')) + ''' (m)</td>
            </tr>
            <tr>
              <td>longitude</td>
              <td>latitude</td>
              <td>E</td>
              <td>N</td>
              <td>h</td>
            </tr>'''

        # UTM e GEO sem Az e d
        if tipo == 'both' and azimuteDist == 0:
            linha = '''<tr>
              <td>Vn</td>
              <td>lonn</td>
              <td>latn</td>
              <td>En</td>
              <td>Nn</td>
              <td>hn</td>
            </tr>
            '''

            cabec = '''<tr>
              <td colspan="6" rowspan="1">''' + tr('Synthetic deed description'.upper(), str2HTML('Memorial Sintético'.upper())) + '''[TITULO]</td>
            </tr>
            <tr>
              <td colspan="1" rowspan="2">''' + tr('VERTEX', str2HTML('VÉRTICE')) + '''</td>
              <td colspan="5" rowspan="1">''' + tr('COORDINATE', str2HTML('COORDENADA')) + '''</td>
            </tr>
            <tr>
              <td>longitude</td>
              <td>latitude</td>
              <td>E</td>
              <td>N</td>
              <td>h</td>
            </tr>'''

        LINHAS = ''
        for k in range(tam):
            linha0 = linha
            itens = {'Vn': pnts_UTM[k+1][2],
                        'En': tr(format_num.format(pnts_UTM[k+1][0].x()), format_num.format(pnts_UTM[k+1][0].x()).replace(',', 'X').replace('.', ',').replace('X', '.')),
                        'Nn': tr(format_num.format(pnts_UTM[k+1][0].y()), format_num.format(pnts_UTM[k+1][0].y()).replace(',', 'X').replace('.', ',').replace('X', '.')),
                        'hn': tr(format_num.format(pnts_UTM[k+1][0].z()), format_num.format(pnts_UTM[k+1][0].z()).replace(',', 'X').replace('.', ',').replace('X', '.')),
                        'lonn': tr(DD2DMS(pnts_GEO[k+1][0].x(),decimal + 3), DD2DMS(pnts_GEO[k+1][0].x(),decimal + 3).replace('.', ',')),
                        'latn': tr(DD2DMS(pnts_GEO[k+1][0].y(),decimal + 3), DD2DMS(pnts_GEO[k+1][0].y(),decimal + 3).replace('.', ',')),
                        'Ln': '-' if TipoGeometria == 1 and k+1 == tam else pnts_UTM[k+1][2] + '/' + pnts_UTM[1 if k+2 > tam else k+2][2],
                        'Az_n': '-' if TipoGeometria == 1 and k+1 == tam else tr(DD2DMS(Az_lista[k],1), DD2DMS(Az_lista[k],1).replace('.', ',')),
                        'Dn': '-' if TipoGeometria == 1 and k+1 == tam else tr(format_num.format(Dist[k]), format_num.format(Dist[k]).replace(',', 'X').replace('.', ',').replace('X', '.'))
                        }
            for item in itens:
                linha0 = linha0.replace(item, itens[item])
            LINHAS += linha0
        resultado = texto.replace('[CABECALHO]', cabec).replace('[LINHAS]', LINHAS).replace('[TITULO]', str2HTML(titulo.upper())).replace('[FONTSIZE]', str(fontsize))
        return resultado

    else:
        return tr('Check if the geometry is null or invalid! Or if Atlas is on!', 'Verifique se a geometria é nula ou inválida! Ou se o Atlas está ligado!')



@qgsfunction(args='auto', group='LF Tools')
def deedtext(layer_name, description, estilo, prefix, decimal, fontsize, feature, parent):
    """
    Generates a description of a property with coordinates as text.
    <p>Note 1: A layer or QGIS Project with a projected SRC is required.</p>
    <p>Note 2: Coordinates styles: 'E,N,h', 'N,E,h', 'E,N' (default) or 'N,E'.</p>

    <h2>Exemples:</h2>
    <ul>
      <li>deedtext('layer_name', 'initial description', 'style', 'preffix', precision, fontsize) = HTML</li>
      <li>deedtext('layer_name', 'northernmost point', 'E,N,h', 'V-', 2, 12) = HTML</li>
      <li>deedtext('layer_name', 'rightmost point in front of the property', 'N,E', 'P-', 3, 10) = HTML</li>
    </ul>
    <h2>Exemples with adjointer layer:</h2>
    <ul>
      <li>deedtext('layer_name', 'adjoiner_line_layer,id,name', 'style', 'preffix', precision, fontsize) = HTML</li>
      <li>deedtext('layer_name', 'Adjoiners,ID1,name', 'E,N', 'P-', 2, 10) = HTML</li>
    </ul>
    <h2>Exemples with vertex layer:</h2>
    <ul>
      <li>deedtext('layer_name', 'initial description', 'style', 'vertex_point_layer,ID,name', precision, fontsize) = HTML</li>
      <li>deedtext('layer_name', 'northernmost point', 'E,N', 'Vertex,id,name', 2, 10) = HTML</li>
    </ul>
    """
    if len(QgsProject.instance().mapLayersByName(layer_name)) == 1:
        layer = QgsProject.instance().mapLayersByName(layer_name)[0]
    else:
        layer = QgsProject.instance().mapLayer(layer_name)

    SRC = layer.crs()
    SGR = QgsCoordinateReferenceSystem(SRC.geographicCrsAuthId())

    format_num = '{:,.Xf}'.replace('X', str(decimal))

    geom = feature.geometry()
    TipoGeometria = geom.type()
    if geom and TipoGeometria in (1,2):

        if TipoGeometria == 2: # Polígono
            if geom.isMultipart():
                coords = geom2PointList(geom)[0][0]
            else:
                coords = geom2PointList(geom)[0]
        else: # Linha
            if geom.isMultipart():
                coords = geom2PointList(geom)[0]
            else:
                coords = geom2PointList(geom)
        pnts_UTM = {}
        pnts_GEO = {}

        # Prefixo
        try:
            descricao, id, nome = prefix.replace(' ', '').split(',') #nome da camada, ID, atributo
            if len(QgsProject.instance().mapLayersByName(descricao)) == 1:
                layer = QgsProject.instance().mapLayersByName(descricao)[0]
            campos = [field.name() for field in layer.fields()]
            # Camadas de polígono e confrontantes deve estar com o mesmo SRC
            filter = '"{}" = {}'.format(id, feature.id())
            exp = QgsExpression(filter)
            if id not in campos or nome not in campos:
                prefixo = str(prefix)
        except:
            prefixo = str(prefix)

        if not SRC.isGeographic(): # Projetado
            coordinateTransformer = QgsCoordinateTransform()
            coordinateTransformer.setDestinationCrs(SGR)
            coordinateTransformer.setSourceCrs(SRC)

            for k, coord in enumerate(coords[:-1] if TipoGeometria == 2 else coords):
                pnt = coordinateTransformer.transform(QgsPointXY(coord.x(), coord.y()))
                if 'prefixo' in locals():
                    pnts_UTM[k+1] = [coord, prefixo, prefixo + '{:02}'.format(k+1)]
                    pnts_GEO[k+1] = [QgsPoint(pnt.x(),pnt.y(),coord.z()), prefixo, prefixo + '{:02}'.format(k+1) ]
                else:
                    for feat in layer.getFeatures(QgsFeatureRequest(exp)):
                        # Identificar ponto correspondente
                        pnt_corresp = feat.geometry().asPoint()
                        if coord.x() == pnt_corresp.x() and coord.y() == pnt_corresp.y():
                            prefix = feat[nome]
                            pnts_UTM[k+1] = [coord, prefix, prefix]
                            pnts_GEO[k+1] = [QgsPoint(pnt.x(),pnt.y(),coord.z()), prefix, prefix ]
                            break
                    else:
                        prefix = '?'
                        pnts_UTM[k+1] = [coord, prefix, prefix]
                        pnts_GEO[k+1] = [QgsPoint(pnt.x(),pnt.y(),coord.z()), prefix, prefix]

            try:
                projecao = SRC.description().split(r' / ')[-1]
                PROJ = tr(projecao, projecao.replace('zone', 'fuso'))
            except:
                PROJ = SRC.description()

        else: # Geográfico
            CRS_projeto = QgsCoordinateReferenceSystem(SRC_Projeto('EPSG'))
            coordinateTransformer = QgsCoordinateTransform()
            coordinateTransformer.setDestinationCrs(CRS_projeto)
            coordinateTransformer.setSourceCrs(SRC)
            for k, coord in enumerate(coords[:-1] if TipoGeometria == 2 else coords):
                pnt = coordinateTransformer.transform(QgsPointXY(coord.x(), coord.y()))
                if 'prefixo' in locals():
                    pnts_GEO[k+1] = [coord, prefixo, prefixo + '{:02}'.format(k+1)]
                    pnts_UTM[k+1] = [QgsPoint(pnt.x(),pnt.y(),coord.z()), prefixo, prefixo + '{:02}'.format(k+1) ]
                else:
                    for feat in layer.getFeatures(QgsFeatureRequest(exp)):
                        # Identificar ponto correspondente
                        pnt_corresp = feat.geometry().asPoint()
                        if coord.x() == pnt_corresp.x() and coord.y() == pnt_corresp.y():
                            prefix = feat[nome]
                            pnts_GEO[k+1] = [coord, prefix, prefix]
                            pnts_UTM[k+1] = [QgsPoint(pnt.x(),pnt.y(),coord.z()), prefix, prefix]
                            break
                    else:
                        prefix = '?'
                        pnts_GEO[k+1] = [coord, prefix, prefix]
                        pnts_UTM[k+1] = [QgsPoint(pnt.x(),pnt.y(),coord.z()), prefix, prefix]

            try:
                projecao = CRS_projeto.description().split(r' / ')[-1]
                PROJ = tr(projecao, projecao.replace('zone', 'fuso'))
            except:
                PROJ = SRC.description()

        # Calculo dos Azimutes e Distancias
        tam = len(pnts_UTM)
        Az_lista, Dist = [], []
        if TipoGeometria == 2: # Polígono
            for k in range(tam):
                pntA = pnts_UTM[k+1][0]
                pntB = pnts_UTM[1 if k+2 > tam else k+2][0]
                Az_lista += [(180/pi)*azimute(pntA, pntB)[0]]
                Dist += [sqrt((pntA.x() - pntB.x())**2 + (pntA.y() - pntB.y())**2)]
        else: # Linha
            for k in range(tam-1):
                pntA = pnts_UTM[k+1][0]
                pntB = pnts_UTM[k+2][0]
                Az_lista += [(180/pi)*azimute(pntA, pntB)[0]]
                Dist += [sqrt((pntA.x() - pntB.x())**2 + (pntA.y() - pntB.y())**2)]

        # Definindo estilo das coordendas
        estilo = estilo.replace(' ','').lower()
        if estilo == 'E,N,h'.lower():
            estilo_vertices = '<b>E [Xn]m</b>, <b>N [Yn]m</b> ' + tr('and', 'e') +  ' <b>h [hn]m</b>'
        elif estilo =='N,E,h'.lower():
            estilo_vertices = '<b>N [Yn]m</b>, <b>E [Xn]m</b> ' + tr('and', 'e') +  ' <b>h [hn]m</b>'
        elif estilo =='E,N'.lower():
            estilo_vertices = '<b>E [Xn]m</b> ' + tr('and', 'e') +  ' <b>N [Yn]m</b>'
        elif estilo =='N,E'.lower():
            estilo_vertices = '<b>N [Yn]m</b> ' + tr('and', 'e') +  ' <b>E [Xn]m</b>'
        else: # default
            estilo_vertices = '<b>E [Xn]m</b> ' + tr('and', 'e') +  ' <b>N [Yn]m</b>'

        # Descrição
        try:
            descricao, id, nome = description.replace(' ', '').split(',')
            if len(QgsProject.instance().mapLayersByName(descricao)) == 1:
                layer = QgsProject.instance().mapLayersByName(descricao)[0]
            campos = [field.name() for field in layer.fields()]
            # Camadas de polígono e confrontantes deve estar com o mesmo SRC
            filter = '"{}" = {}'.format(id, feature.id())
            exp = QgsExpression(filter)
            if id not in campos or nome not in campos:
                descr_pnt_ini = description
        except: # >>>>>>>>>>>>>>>>> Apenas inserir a descrição do ponto inicial
            descr_pnt_ini = description

        if TipoGeometria == 1:
            descr_pnt_ini = description

        try:
            descr_pnt_ini = str(descr_pnt_ini)

            # conteudo do memorial
            text_ini = tr('<div style="text-align: justify; font-size: [FONTSIZE]px; font-family: Arial;">The description of this perimeter begins at the vertex <b>[Vn]</b>, with coordinates ' + estilo_vertices + ', [descr_pnt_ini] from this, with the following flat azimuths and distances: ',
                          '<div style="text-align: justify; font-size: [FONTSIZE]px; font-family: Arial;">Inicia-se a descrição deste perímetro no vértice <b>[Vn]</b>, de coordenadas ' + estilo_vertices + ', [descr_pnt_ini] deste, segue com os seguintes azimutes planos e distâncias: ')

            text_meio = tr('[Azn] and [Dn]m up to the vertex <b>[Vn]</b>, with coordinates ' + estilo_vertices + ', ',
                           '[Azn] e [Dn]m até o vértice <b>[Vn]</b>, de coordenadas ' + estilo_vertices + ', ')

            if TipoGeometria == 2:
                text_fim = tr('''the starting point for the description of this perimeter.
                All coordinates described here are georeferenced to the Geodetic Reference System (GRS) (SGR) <b>[SGR]</b>, and are projected in the system <b>[PROJ]</b>,
                from which all azimuths and distances, area and perimeter were calculated.''',
                '''ponto inicial da descrição deste perímetro.
                Todas as coordenadas aqui descritas estão georreferenciadas ao Sistema Geodésico de Referência (SGR) <b>[SGR]</b>, sendo projetadas no sistema <b>[PROJ]</b>,
                a partir das quais todos os azimutes e distâncias foram calculados.</div>
                ''')
            else:
                text_fim = tr('''the last point of this perimeter.
                All coordinates described here are georeferenced to the Geodetic Reference System (GRS) (SGR) <b>[SGR]</b>, and are projected in the system <b>[PROJ]</b>,
                from which all azimuths and distances, area and perimeter were calculated.''',
                '''último ponto deste perímetro.
                Todas as coordenadas aqui descritas estão georreferenciadas ao Sistema Geodésico de Referência (SGR) <b>[SGR]</b>, sendo projetadas no sistema <b>[PROJ]</b>,
                a partir das quais todos os azimutes e distâncias foram calculados.</div>
                ''')

            # Texto inicial
            itens = {'[Vn]': pnts_UTM[1][2],
                     '[Xn]': tr(format_num.format(pnts_UTM[1][0].x()), format_num.format(pnts_UTM[1][0].x()).replace(',', 'X').replace('.', ',').replace('X', '.')),
                     '[Yn]': tr(format_num.format(pnts_UTM[1][0].y()), format_num.format(pnts_UTM[1][0].y()).replace(',', 'X').replace('.', ',').replace('X', '.')),
                     '[descr_pnt_ini]': descr_pnt_ini + ', ' if descr_pnt_ini else ''
                        }
            if 'h' in estilo:
                itens['[hn]'] = tr(format_num.format(pnts_UTM[1][0].z()), format_num.format(pnts_UTM[1][0].z()).replace(',', 'X').replace('.', ',').replace('X', '.'))
            for item in itens:
                text_ini = text_ini.replace(item, itens[item]).replace('[FONTSIZE]', str(fontsize))

            # Texto do meio
            LINHAS = ''
            if TipoGeometria == 2:
                for k in range(tam):
                    linha0 = text_meio
                    indice = k+2 if k+2 <= tam else 1
                    itens = {'[Vn]': pnts_UTM[indice][2],
                             '[Xn]': tr(format_num.format(pnts_UTM[indice][0].x()),
                                      format_num.format(pnts_UTM[indice][0].x()).replace(',', 'X').replace('.', ',').replace('X', '.')),
                             '[Yn]': tr(format_num.format(pnts_UTM[indice][0].y()),
                                      format_num.format(pnts_UTM[indice][0].y()).replace(',', 'X').replace('.', ',').replace('X', '.')),
                             '[Azn]': tr(DD2DMS(Az_lista[k],1), DD2DMS(Az_lista[k],1).replace('.', ',')),
                             '[Dn]': tr(format_num.format(Dist[k]), format_num.format(Dist[k]).replace(',', 'X').replace('.', ',').replace('X', '.'))
                                }
                    if 'h' in estilo:
                        itens['[hn]'] = tr(format_num.format(pnts_UTM[indice][0].z()),
                                           format_num.format(pnts_UTM[indice][0].z()).replace(',', 'X').replace('.', ',').replace('X', '.'))
                    for item in itens:
                        linha0 = linha0.replace(item, itens[item])
                    LINHAS += linha0

            else: # Linha
                for k in range(tam-1):
                    linha0 = text_meio
                    indice = k+2
                    itens = {'[Vn]': pnts_UTM[indice][2],
                             '[Xn]': tr(format_num.format(pnts_UTM[indice][0].x()),
                                      format_num.format(pnts_UTM[indice][0].x()).replace(',', 'X').replace('.', ',').replace('X', '.')),
                             '[Yn]': tr(format_num.format(pnts_UTM[indice][0].y()),
                                      format_num.format(pnts_UTM[indice][0].y()).replace(',', 'X').replace('.', ',').replace('X', '.')),
                             '[Azn]': tr(DD2DMS(Az_lista[k],1), DD2DMS(Az_lista[k],1).replace('.', ',')),
                             '[Dn]': tr(format_num.format(Dist[k]), format_num.format(Dist[k]).replace(',', 'X').replace('.', ',').replace('X', '.'))
                                }
                    if 'h' in estilo:
                        itens['[hn]'] = tr(format_num.format(pnts_UTM[indice][0].z()),
                                           format_num.format(pnts_UTM[indice][0].z()).replace(',', 'X').replace('.', ',').replace('X', '.'))
                    for item in itens:
                        linha0 = linha0.replace(item, itens[item])
                    LINHAS += linha0

            # Texto final
            itens = {'[SGR]': SGR.description(),
                     '[PROJ]': PROJ
                        }
            for item in itens:
                text_fim = text_fim.replace(item, itens[item])

            FINAL = text_ini + LINHAS + text_fim
            return FINAL

        except: # >>>>>>>>>>>>>>>>> puxar nome dos confrontantes

            # conteudo do memorial
            text_ini = tr('<div style="text-align: justify; font-size: [FONTSIZE]px; font-family: Arial;">The description of this perimeter begins at the vertex <b>[Vn]</b>, with coordinates ' + estilo_vertices + ', ',
                          '<div style="text-align: justify; font-size: [FONTSIZE]px; font-family: Arial;">Inicia-se a descrição deste perímetro no vértice <b>[Vn]</b>, de coordenadas ' + estilo_vertices + ', ')

            text_meio1 = tr('from this, it continues adjoining with [ADJOINER], with the following flat azimuths and distances: [Azn] and [Dn]m up to the vertex <b>[Vn]</b>, with coordinates ' + estilo_vertices + ', ',
                            'deste, segue confrontando com [ADJOINER], com os seguintes azimutes planos e distâncias: [Azn] e [Dn]m até o vértice <b>[Vn]</b>, de coordenadas ' + estilo_vertices + ', ')

            text_meio2 = tr('[Azn] and [Dn]m up to the vertex <b>[Vn]</b>, with coordinates ' + estilo_vertices + ', ',
                            '[Azn] e [Dn]m até o vértice <b>[Vn]</b>, de coordenadas ' + estilo_vertices + ', ')

            text_fim = tr('''the starting point for the description of this perimeter.
            All coordinates described here are georeferenced to the Geodetic Reference System (GRS) (SGR) <b>[SGR]</b>, and are projected in the system <b>[PROJ]</b>,
            from which all azimuths and distances, area and perimeter were calculated.''',
            '''ponto inicial da descrição deste perímetro.
            Todas as coordenadas aqui descritas estão georreferenciadas ao Sistema Geodésico de Referência (SGR) <b>[SGR]</b>, sendo projetadas no sistema <b>[PROJ]</b>,
            a partir das quais todos os azimutes e distâncias foram calculados.</div>
            ''')

            # Texto inicial
            itens = {'[Vn]': pnts_UTM[1][2],
                     '[Xn]': tr(format_num.format(pnts_UTM[1][0].x()), format_num.format(pnts_UTM[1][0].x()).replace(',', 'X').replace('.', ',').replace('X', '.')),
                     '[Yn]': tr(format_num.format(pnts_UTM[1][0].y()), format_num.format(pnts_UTM[1][0].y()).replace(',', 'X').replace('.', ',').replace('X', '.'))
                        }
            if 'h' in estilo:
                itens['[hn]'] = tr(format_num.format(pnts_UTM[1][0].z()), format_num.format(pnts_UTM[1][0].z()).replace(',', 'X').replace('.', ',').replace('X', '.'))
            for item in itens:
                text_ini = text_ini.replace(item, itens[item]).replace('[FONTSIZE]', str(fontsize))

            # Texto do meio
            LINHAS = ''
            Confrontante = ''

            for k in range(tam):
                indice = k+2 if k+2 <= tam else 1
                ponto = QgsPointXY(pnts_GEO[indice][0])
                for feat in layer.getFeatures(QgsFeatureRequest(exp)):
                    # Identificar linha de confrontação
                    geom_lin = feat.geometry()
                    if geom_lin.intersects(geom):
                        inter = geom_lin.intersection(geom)
                        if inter.type() == 1: # linha
                            if inter.isMultipart():
                                lin_coords = inter.asMultiPolyline()
                                lin_coords = sum(lin_coords, [])
                            else:
                                lin_coords = inter.asPolyline()
                            if ponto in lin_coords[1:]:
                                if feat[nome] != Confrontante:
                                    linha0 = text_meio1
                                    Confrontante = feat[nome]
                                else:
                                    linha0 = text_meio2
                                break

                itens = {'[Vn]': pnts_UTM[indice][2],
                         '[Xn]': tr(format_num.format(pnts_UTM[indice][0].x()),
                                  format_num.format(pnts_UTM[indice][0].x()).replace(',', 'X').replace('.', ',').replace('X', '.')),
                         '[Yn]': tr(format_num.format(pnts_UTM[indice][0].y()),
                                  format_num.format(pnts_UTM[indice][0].y()).replace(',', 'X').replace('.', ',').replace('X', '.')),
                         '[Azn]': tr(DD2DMS(Az_lista[k],1), DD2DMS(Az_lista[k],1).replace('.', ',')),
                         '[Dn]': tr(format_num.format(Dist[k]), format_num.format(Dist[k]).replace(',', 'X').replace('.', ',').replace('X', '.')),
                         '[ADJOINER]': Confrontante,
                            }
                if 'h' in estilo:
                    itens['[hn]'] = tr(format_num.format(pnts_UTM[indice][0].z()),
                                       format_num.format(pnts_UTM[indice][0].z()).replace(',', 'X').replace('.', ',').replace('X', '.'))

                for item in itens:
                    linha0 = linha0.replace(item, itens[item])
                LINHAS += linha0

            # Texto final
            itens = {'[SGR]': SGR.description(),
                     '[PROJ]': PROJ
                        }
            for item in itens:
                text_fim = text_fim.replace(item, itens[item])

            FINAL = text_ini + LINHAS + text_fim
            return FINAL
    else:
        return tr('Check if the geometry is null or invalid! Or if Atlas is on!', 'Verifique se a geometria é nula ou inválida! Ou se o Atlas está ligado!')


@qgsfunction(args='auto', group='LF Tools')
def geoneighbors(layer_name, street, borderer_field, prefix, decimal, fontsize, feature, parent):
    """
    Generates a table of coordinates with neighbors (boundaries) and a polygon and distances.
    <p>Note: A layer or QGIS Project with a projected CRS is required.</p>

    <h2>Exemples:</h2>
    <ul>
      <li>geoneighbors('layer_name', 'borderer_field', 'preffix', precision, fontsize) = HTML</li>
      <li>geoneighbors('layer_name', street, borderer_field , 'V-', 2, 12) = HTML</li>
    </ul>
    """
    if len(QgsProject.instance().mapLayersByName(layer_name)) == 1:
        layer = QgsProject.instance().mapLayersByName(layer_name)[0]
    else:
        layer = QgsProject.instance().mapLayer(layer_name)

    SRC = layer.crs()
    SGR = QgsCoordinateReferenceSystem(SRC.geographicCrsAuthId())

    format_num = '{:,.Xf}'.replace('X', str(decimal))

    geom = feature.geometry()
    if geom.type() == 2 and geom:

        # Pegar vizinhos
        geom1 = feature.geometry()
        feat1 = feature
        confront = {}
        for feat2 in layer.getFeatures():
            geom2 = feat2.geometry()
            cd_lote2 = str(feat2[borderer_field])
            if feat1 != feat2:
                if geom1.intersects(geom2):
                    inters = geom1.intersection(geom2)
                    confront[feat2.id()] = [cd_lote2, inters]

        if geom1.isMultipart():
            coords = geom1.asMultiPolygon()[0][0]
        else:
            coords = geom1.asPolygon()[0]

        vizinhos = []
        for pnt in coords[:-1]:
            geom1 = QgsGeometry.fromPointXY(pnt)
            vante = ''
            compl = ''
            for item in confront:
                geom2 = confront[item][1]
                if geom2.type() == 1 and geom1.intersects(geom2): #Line
                    try:
                        coord_lin = geom2.asPolyline()
                    except:
                        coord_lin = geom2.asMultiPolyline()[-1]
                    if pnt != coord_lin[-1]:
                        vante = confront[item][0]
                elif geom2.type() == 0 and geom1.intersects(geom2): #Point
                    compl = confront[item][0]
            vizinhos += [(vante, compl)]

        if geom.isMultipart():
            coords = geom2PointList(geom)[0][0]
        else:
            coords = geom2PointList(geom)[0]
        pnts_UTM = {}
        pnts_GEO = {}

        # Prefixo
        try:
            descricao, id, nome = prefix.replace(' ', '').split(',') #nome da camada, ID, atributo
            if len(QgsProject.instance().mapLayersByName(descricao)) == 1:
                layer = QgsProject.instance().mapLayersByName(descricao)[0]
            campos = [field.name() for field in layer.fields()]
            # Camadas de polígono e confrontantes deve estar com o mesmo SRC
            filter = '"{}" = {}'.format(id, feature.id())
            exp = QgsExpression(filter)
            if id not in campos or nome not in campos:
                prefixo = str(prefix)
        except:
            prefixo = str(prefix)

        # Pegando valores dos pontos
        if not SRC.isGeographic(): # Projetado
            coordinateTransformer = QgsCoordinateTransform()
            coordinateTransformer.setDestinationCrs(SGR)
            coordinateTransformer.setSourceCrs(SRC)

            for k, coord in enumerate(coords[:-1]):
                pnt = coordinateTransformer.transform(QgsPointXY(coord.x(), coord.y()))
                if 'prefixo' in locals():
                    pnts_UTM[k+1] = [coord, prefixo, prefixo + '{:02}'.format(k+1)]
                    pnts_GEO[k+1] = [QgsPoint(pnt.x(),pnt.y(),coord.z()), prefixo, prefixo + '{:02}'.format(k+1) ]
                else:
                    for feat in layer.getFeatures(QgsFeatureRequest(exp)):
                        # Identificar ponto correspondente
                        pnt_corresp = feat.geometry().asPoint()
                        if coord.x() == pnt_corresp.x() and coord.y() == pnt_corresp.y():
                            prefix = feat[nome]
                            pnts_UTM[k+1] = [coord, prefix, prefix]
                            pnts_GEO[k+1] = [QgsPoint(pnt.x(),pnt.y(),coord.z()), prefix, prefix ]
                            break
                    else:
                        prefix = '?'
                        pnts_UTM[k+1] = [coord, prefix, prefix]
                        pnts_GEO[k+1] = [QgsPoint(pnt.x(),pnt.y(),coord.z()), prefix, prefix]

            try:
                projecao = SRC.description().split(r' / ')[-1]
                PROJ = tr(projecao, projecao.replace('zone', 'fuso'))
            except:
                PROJ = SRC.description()

        else: # Geográfico
            CRS_projeto = QgsCoordinateReferenceSystem(SRC_Projeto('EPSG'))
            coordinateTransformer = QgsCoordinateTransform()
            coordinateTransformer.setDestinationCrs(CRS_projeto)
            coordinateTransformer.setSourceCrs(SRC)
            for k, coord in enumerate(coords[:-1]):
                pnt = coordinateTransformer.transform(QgsPointXY(coord.x(), coord.y()))
                if 'prefixo' in locals():
                    pnts_GEO[k+1] = [coord, prefixo, prefixo + '{:02}'.format(k+1)]
                    pnts_UTM[k+1] = [QgsPoint(pnt.x(),pnt.y(),coord.z()), prefixo, prefixo + '{:02}'.format(k+1) ]
                else:
                    for feat in layer.getFeatures(QgsFeatureRequest(exp)):
                        # Identificar ponto correspondente
                        pnt_corresp = feat.geometry().asPoint()
                        if coord.x() == pnt_corresp.x() and coord.y() == pnt_corresp.y():
                            prefix = feat[nome]
                            pnts_GEO[k+1] = [coord, prefix, prefix]
                            pnts_UTM[k+1] = [QgsPoint(pnt.x(),pnt.y(),coord.z()), prefix, prefix]
                            break
                    else:
                        prefix = '?'
                        pnts_GEO[k+1] = [coord, prefix, prefix]
                        pnts_UTM[k+1] = [QgsPoint(pnt.x(),pnt.y(),coord.z()), prefix, prefix]

            try:
                projecao = CRS_projeto.description().split(r' / ')[-1]
                PROJ = tr(projecao, projecao.replace('zone', 'fuso'))
            except:
                PROJ = SRC.description()

        # Calculo dos Azimutes e Distancias
        tam = len(pnts_UTM)
        Az_lista, Dist = [], []
        for k in range(tam):
            pntA = pnts_UTM[k+1][0]
            pntB = pnts_UTM[1 if k+2 > tam else k+2][0]
            Az_lista += [(180/pi)*azimute(pntA, pntB)[0]]
            Dist += [sqrt((pntA.x() - pntB.x())**2 + (pntA.y() - pntB.y())**2)]

        # conteudo da tabela
        texto = '''<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
<html>
<head>
  <meta content="text/html; charset=ISO-8859-1"
 http-equiv="content-type">
  <title></title>
</head>
<body>
<div align="center">
<table class="MsoTableGrid"
 style="border: medium none ; width: 100%; border-collapse: collapse;"
 border="1" cellpadding="0" cellspacing="0"
 width="100%">
  <tbody>
    <tr style="">
      <td
 style="border: 1pt solid windowtext; padding: 0cm 5.4pt; width: 10.06%;"
 width="10%">
      <p class="MsoNormal"
 style="margin-bottom: 0cm; text-align: center; line-height: normal;"
 align="center"><b>'''+ tr('Vertex', 'Vértice') + '''<o:p></o:p></b></p>
      </td>
      <td
 style="border-style: solid solid solid none; border-color: windowtext windowtext windowtext -moz-use-text-color; border-width: 1pt 1pt 1pt medium; padding: 0cm 5.4pt; width: 11.22%;"
 width="11%">
      <p class="MsoNormal"
 style="margin-bottom: 0cm; text-align: center; line-height: normal;"
 align="center"><b>Latitude<o:p></o:p></b></p>
      </td>
      <td
 style="border-style: solid solid solid none; border-color: windowtext windowtext windowtext -moz-use-text-color; border-width: 1pt 1pt 1pt medium; padding: 0cm 5.4pt; width: 13.06%;"
 width="13%">
      <p class="MsoNormal"
 style="margin-bottom: 0cm; text-align: center; line-height: normal;"
 align="center"><b>Longitude<o:p></o:p></b></p>
      </td>
      <td
 style="border-style: solid solid solid none; border-color: windowtext windowtext windowtext -moz-use-text-color; border-width: 1pt 1pt 1pt medium; padding: 0cm 5.4pt; width: 20%;"
 width="20%">
      <p class="MsoNormal"
 style="margin-bottom: 0cm; text-align: center; line-height: normal;"
 align="center"><b>'''+ tr('Forward neighbor', 'Confrontante a vante') + '''<o:p></o:p></b></p>
      </td>
      <td
 style="border-style: solid solid solid none; border-color: windowtext windowtext windowtext -moz-use-text-color; border-width: 1pt 1pt 1pt medium; padding: 0cm 5.4pt; width: 17.12%;"
 width="17%">
      <p class="MsoNormal"
 style="margin-bottom: 0cm; text-align: center; line-height: normal;"
 align="center"><b>'''+ tr('Distance (m)', 'Distância (m)') + '''<o:p></o:p></b></p>
      </td>
      <td
 style="border-style: solid solid solid none; border-color: windowtext windowtext windowtext -moz-use-text-color; border-width: 1pt 1pt 1pt medium; padding: 0cm 5.4pt; width: 17.56%;"
 width="17%">
      <p class="MsoNormal"
 style="margin-bottom: 0cm; text-align: center; line-height: normal;"
 align="center"><b>'''+ tr('Complement', 'Complemento') + '''<o:p></o:p></b></p>
      </td>
    </tr>
    [LINHAS]
  </tbody>
</table>
</div>
</body>
</html>
'''

        linha = '''<tr style="">
      <td
 style="border-style: none solid solid; border-color: -moz-use-text-color windowtext windowtext; border-width: medium 1pt 1pt; padding: 0cm 5.4pt; width: 10.06%;"
 width="10%">
      <p class="MsoNormal"
 style="margin-bottom: 0cm; text-align: center; line-height: normal;"
 align="center">[Vn]<o:p></o:p></p>
      </td>
      <td
 style="border-style: none solid solid none; border-color: -moz-use-text-color windowtext windowtext -moz-use-text-color; border-width: medium 1pt 1pt medium; padding: 0cm 5.4pt; width: 11.22%;"
 width="11%">
      <p class="MsoNormal"
 style="margin-bottom: 0cm; text-align: center; line-height: normal;"
 align="center">[LAT]<o:p></o:p></p>
      </td>
      <td
 style="border-style: none solid solid none; border-color: -moz-use-text-color windowtext windowtext -moz-use-text-color; border-width: medium 1pt 1pt medium; padding: 0cm 5.4pt; width: 13.06%;"
 width="13%">
      <p class="MsoNormal"
 style="margin-bottom: 0cm; text-align: center; line-height: normal;"
 align="center">[LON]<o:p></o:p></p>
      </td>
      <td
 style="border-style: none solid solid none; border-color: -moz-use-text-color windowtext windowtext -moz-use-text-color; border-width: medium 1pt 1pt medium; padding: 0cm 5.4pt; width: 20%;"
 width="20%">
      <p class="MsoNormal"
 style="margin-bottom: 0cm; text-align: center; line-height: normal;"
 align="center">[confr]<o:p></o:p></p>
      </td>
      <td
 style="border-style: none solid solid none; border-color: -moz-use-text-color windowtext windowtext -moz-use-text-color; border-width: medium 1pt 1pt medium; padding: 0cm 5.4pt; width: 17.12%;"
 width="17%">
      <p class="MsoNormal"
 style="margin-bottom: 0cm; text-align: center; line-height: normal;"
 align="center">[dist]<o:p></o:p></p>
      </td>
      <td
 style="border-style: none solid solid none; border-color: -moz-use-text-color windowtext windowtext -moz-use-text-color; border-width: medium 1pt 1pt medium; padding: 0cm 5.4pt; width: 17.56%;"
 width="17%">
      <p class="MsoNormal"
 style="margin-bottom: 0cm; text-align: center; line-height: normal;"
 align="center">[comp]<o:p></o:p></p>
      </td>
    </tr>'''

        # Texto do meio
        LINHAS = ''
        ruas = str(street).split(',')
        n_ruas = 0
        for k in range(tam):
            linha0 = linha

            if not vizinhos[k][0]:
                try:
                    rua = ruas[n_ruas].strip()
                    n_ruas += 1
                except:
                    rua = street

            LAT = tr(DD2DMS(pnts_GEO[k+1][0].y(),decimal + 3), DD2DMS(pnts_GEO[k+1][0].y(),decimal + 3).replace('.', ','))
            LON = tr(DD2DMS(pnts_GEO[k+1][0].x(),decimal + 3), DD2DMS(pnts_GEO[k+1][0].x(),decimal + 3).replace('.', ','))
            LAT = LAT + 'N' if LAT[0] != '-' else LAT[1:] + 'S'
            LON = LON + 'E' if LON[0] != '-' else LON[1:] + 'W'
            itens = {'[Vn]': pnts_UTM[k+1][2],
                     '[LON]': LON,
                     '[LAT]': LAT,
                     '[h]': tr(format_num.format(pnts_GEO[k+1][0].z()), format_num.format(pnts_GEO[k+1][0].z()).replace(',', 'X').replace('.', ',').replace('X', '.')),
                     '[confr]': vizinhos[k][0] if vizinhos[k][0] else rua,
                     '[dist]': tr(format_num.format(Dist[k]), format_num.format(Dist[k]).replace(',', 'X').replace('.', ',').replace('X', '.')),
                     '[comp]': tr('Punctual neighbor with ' + vizinhos[k][1], 'Confrontação pontual com ' + vizinhos[k][1]) if vizinhos[k][1] else '-',
                        }

            for item in itens:
                linha0 = linha0.replace(item, itens[item])
            LINHAS += linha0

        # Resultado final
        return texto.replace('[LINHAS]', LINHAS)

    else:
        return tr('Check if the geometry is null or invalid! Or if Atlas is on!', 'Verifique se a geometria é nula ou inválida! Ou se o Atlas está ligado!')
