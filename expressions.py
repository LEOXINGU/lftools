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
                                         Mesclar_Multilinhas,
                                         areaGauss,
                                         classificar,
                                         FusoHemisf,
                                         main_azimuth,
                                         AzimuteDistanciaSGL,
                                         areaSGL, perimetroSGL, comprimentoSGL,
                                         inom2mi as INOM2MI)
from lftools.geocapt.topogeo import (dd2dms as DD2DMS,
                                     dms2dd as DMS2DD,
                                     azimute, str2HTML,
                                     geod2geoc, geoc2enu,
                                     meters2degrees,
                                     gpsdate as GPSDATE)
from lftools import geomag
from lftools.geocapt.imgs import img2html_resized, geom_icons
from lftools.translations.translate import translate
from numpy import array, pi, sqrt, median
import numpy as np
from pyproj.crs import CRS
import unicodedata
from datetime import datetime, date
import re, os
# https://qgis.org/pyqgis/3.2/core/Expression/QgsExpression.html

LOC = QgsApplication.locale()[:2]
def tr(*string):
    return translate(string, LOC)


def proportion(values, total):
    sum_values = np.sum(values)
    new_values = []
    acc = 0
    for v in values:
        q, r = divmod(v * total, sum_values)
        if acc + r < sum_values:
            acc += r
        else:
            if acc > r:
                new_values[-1] += 1
            else:
                q += 1
            acc -= sum_values - r
        new_values.append(q)
    return new_values


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
    <h2>Examples:</h2>
    <ul>
      <li>dd2dms(dd, precision) -> GG°MM'SS.SSS"</li>
      <li>dd2dms(-12.20965027, 3) -> -12°12'34.741"</li>
      <li>dd2dms(0.56333, 2) -> 0°33'47.99"</li>
      <li>dd2dms(0.56333, 0) -> 0°33'48"</li>
      <li>dd2dms(0.56333,-1) -> 0°34'</li>
      <li>dd2dms(0.56333,-2) -> 0°33.8'</li>
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
def classify(value, number_classes, method, group, feature, parent, context):
    """
    Classifies a feature's numeric value into a class (from 1 to N) based on a statistical classification method.
    Parameters:
    - <b>value</b> (numeric): the numeric value to classify (e.g. a field like "elevation" or "area")<br>
    - <b>number_classes</b> (int): total number of desired classes (e.g. 5)<br>
    - <b>method</b> (string): classification method to apply (see list below)<br>
    - <b>group</b> (string): group identifier to classify values separately per group (use '' for no grouping)

    Returns:
    - An integer (1 to number_classes) indicating the class.
    <h2>Example usage:</h2>
    <ul>
      <li>classify('measure', 4, 'jenks', 'block') -> 1</li>
      <li>classify('value', 5, 'quantile', '') -> 3</li>
    </ul>
    <h3>Available classification methods:</h3>
   <ul>
    <li><b>'stddev'</b> – Standard Deviation from the mean</li>
    <li><b>'log'</b> – Logarithmic scale</li>
    <li><b>'quantile'</b> – Equal count per class (e.g., quartiles)</li>
    <li><b>'fixed'</b> – Fixed interval (default step = 10)</li>
    <li><b>'equal'</b> – Equal range intervals between min and max</li>
    <li><b>'jenks'</b> – Natural Breaks (Jenks optimization)</li>
    <li><b>'smooth'</b> – Smooth sinusoidal distribution (sine interpolation)</li>
   </ul>
    """
    layer_id = context.variable('layer_id')
    layer = QgsProject.instance().mapLayer(layer_id)

    grupo = group if group else 'ALL'
    # Dicionário para agrupar valores por grupo
    grupos = {}

    for f in layer.getFeatures():
        g = f[group] if group else 'ALL'
        v = f[value]
        if g not in grupos:
            grupos[g] = [v]
        else:
            grupos[g] += [v]

    # Obter valores para o grupo atual
    lista_valores = grupos[feature[group]] if group else grupos['ALL']
    if len(lista_valores) < number_classes:
        return NULL
    else:
        # Calcular limites das classes
        limites = classificar(lista_valores, method, number_classes)

        valor = feature[value]
        if valor is None:
            return NULL
        # Determinar a qual classe o valor pertence
        for i, limite in enumerate(limites):
            if valor <= limite:
                resultado = i + 1
                break
        return resultado


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


@qgsfunction(args='auto', group='LF Tools')
def azimuth_by_sequence (sequence_field, group_field, feature, parent, context):
    """
    Calculates the azimuth between sequential points in a point layer based on an ordering field.
    Optionally, azimuths can be calculated within separate groups defined by a grouping field
    (e.g., segments, classes, blocks).

    If a grouping field is provided, the azimuth is computed independently within each group.
    The azimuth for each point is calculated from it to the next point in the sequence.
    For the last point in the sequence, the azimuth is calculated to the first point (cyclical).

    Parameters:
    - sequence_field (string or number): Name of the field that defines the order of the points.
    - group_field (string or number): Name of the grouping field. If no grouping is used, provide an empty string ''.

    Returns:
    - The azimuth value (in degrees) for the current feature.
    <ul>
      <li>azimuth_by_sequence (sequence_field, group_field) -> azimuth </li>
      <li>azimuth_by_sequence('order', 'block') -> 45.7823</li>
      <li>azimuth_by_sequence('fid', '') -> 192.1045</li>
    </ul>
    """
    layer_id = context.variable('layer_id')
    layer = QgsProject.instance().mapLayer(layer_id)
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
                ponto = feat.geometry().asPoint()
                dic2[feat[sequence_field]] = ponto

            chaves = list(dic2.keys())
            chaves.sort()
            lista = list(chaves)
            tam = len(lista)
            dic3 = {}
            for k in range(tam):
                p1 = dic2[lista[k]]
                p2 = dic2[lista[0 if k+1 >= tam else k+1]]
                Az = (180/pi)*azimute(p1, p2)[0]
                dic3[lista[k]] = Az
            dic[grupo] = dic3
        return float(dic[feature[group_field]][feature[sequence_field]])

    else:
        dic = {}
        for feat in layer.getFeatures():
            ponto = feat.geometry().asPoint()
            dic[feat[sequence_field]] = ponto

        chaves = list(dic.keys())
        chaves.sort()
        lista = list(chaves)
        tam = len(lista)
        dic2 = {}
        for k in range(tam):
            p1 = dic[lista[k]]
            p2 = dic[lista[0 if k+1 >= tam else k+1]]
            Az = (180/pi)*azimute(p1, p2)[0]
            dic2[lista[k]] = Az
        return float(dic2[feature[sequence_field]])


@qgsfunction(args='auto', group='LF Tools')
def areaLTP (geometry, layer_crs, feature, parent):
    """
    Calculates the area on the Local Tangent Plane (LTP), also known as Local Geodetic Coordinate System, which is a spatial reference system based on the tangent plane on the feature centroid defined by the local vertical direction.
    <p>Note: PolygonZ or MultiPoligonZ should be used to obtain the most accurate result.</p>
    <h2>Example:</h2>
    <ul>
      <li> areaLTP(geometry, layer_crs) -> LTP area </li>
      <li> areaLTP($geometry, 'EPSG:31985') -> 607503.4825 </li>
    </ul>
    <div>
    <p><b>About the LTP:</b></p>
    <p>
    <b><a href="https://geoone.com.br/sistema-geodesico-local/" target="_blank">França, L. Local Geodetic Coordinate System. GeoOne. 2022.</a></b>
    </p>
  </div>
    """
    layer_crs = QgsCoordinateReferenceSystem(layer_crs)
    geom = geometry
    if not layer_crs.isGeographic():
        crsProj = layer_crs
        crsGeo = QgsCoordinateReferenceSystem(crsProj.geographicCrsAuthId())
        coordinateTransformer = QgsCoordinateTransform()
        coordinateTransformer.setDestinationCrs(crsGeo)
        coordinateTransformer.setSourceCrs(crsProj)
        geom.transform(coordinateTransformer)
    else:
        crsGeo = layer_crs
    geomGeo = geom
    try:
        return areaSGL(geomGeo, crsGeo)
    except:
        return tr('Check the geometry type!', 'Verifique o tipo de geometria!')


@qgsfunction(args='auto', group='LF Tools', name = '$areaLTP')
def areaLTP2 (feature, parent, context):
    """
    Calculates the area on the Local Tangent Plane (LTP), also known as Local Geodetic Coordinate System, which is a spatial reference system based on the tangent plane on the feature centroid defined by the local vertical direction.
    <p>Note: PolygonZ or MultiPoligonZ should be used to obtain the most accurate result.</p>
    <h2>Example:</h2>
    <ul>
      <li> $areaLTP -> 607503.4825 </li>
    </ul>
    <div>
    <p><b>About the LTP:</b></p>
    <p>
    <b><a href="https://geoone.com.br/sistema-geodesico-local/" target="_blank">França, L. Local Geodetic Coordinate System. GeoOne. 2022.</a></b>
    </p>
  </div>
    """
    layer_id = context.variable('layer_id')
    layer = QgsProject.instance().mapLayer(layer_id)
    geom = feature.geometry()
    if not layer.crs().isGeographic():
        crsProj = layer.crs()
        crsGeo = QgsCoordinateReferenceSystem(crsProj.geographicCrsAuthId())
        coordinateTransformer = QgsCoordinateTransform()
        coordinateTransformer.setDestinationCrs(crsGeo)
        coordinateTransformer.setSourceCrs(crsProj)
        geom.transform(coordinateTransformer)
    else:
        crsGeo = layer.crs()
    geomGeo = geom
    try:
        return areaSGL(geomGeo, crsGeo)
    except:
        return tr('Check the geometry type!', 'Verifique o tipo de geometria!')


@qgsfunction(args='auto', group='LF Tools')
def perimeterLTP (geometry, layer_crs, feature, parent):
    """
    Calculates the perimeter on the Local Tangent Plane (LTP), also known as Local Geodetic Coordinate System, which is a spatial reference system based on the tangent plane on the feature centroid defined by the local vertical direction.
    <p>Note: PolygonZ or MultiPoligonZ should be used to obtain the most accurate result.</p>
    <h2>Example:</h2>
    <ul>
      <li> perimeterLTP(geometry, layer_crs) -> LTP area </li>
      <li> perimeterLTP($geometry, 'EPSG:31985') -> 607503.4825 </li>
    </ul>
    <div>
    <p><b>About the LTP:</b></p>
    <p>
    <b><a href="https://geoone.com.br/sistema-geodesico-local/" target="_blank">França, L. Local Geodetic Coordinate System. GeoOne. 2022.</a></b>
    </p>
  </div>
    """
    layer_crs = QgsCoordinateReferenceSystem(layer_crs)
    geom = geometry
    if layer_crs.isGeographic():
        crsProj = layer_crs
        crsGeo = QgsCoordinateReferenceSystem(crsProj.geographicCrsAuthId())
        coordinateTransformer = QgsCoordinateTransform()
        coordinateTransformer.setDestinationCrs(crsGeo)
        coordinateTransformer.setSourceCrs(crsProj)
        geom.transform(coordinateTransformer)
    else:
        crsGeo = layer_crs
    geomGeo = geom
    try:
        return perimetroSGL(geomGeo, crsGeo)
    except:
        return tr('Check the geometry type!', 'Verifique o tipo de geometria!')


@qgsfunction(args='auto', group='LF Tools', name = '$perimeterLTP')
def perimeterLTP2 (feature, parent, context):
    """
    Calculates the perimeter on the Local Tangent Plane (LTP), also known as Local Geodetic Coordinate System, which is a spatial reference system based on the tangent plane on the feature centroid defined by the local vertical direction.
    <p>Note: PolygonZ or MultiPoligonZ should be used to obtain the most accurate result.</p>
    <h2>Example:</h2>
    <ul>
      <li> $perimeterLTP -> 456.48 </li>
    </ul>
    <div>
    <p><b>About the LTP:</b></p>
    <p>
    <b><a href="https://geoone.com.br/sistema-geodesico-local/" target="_blank">França, L. Local Geodetic Coordinate System. GeoOne. 2022.</a></b>
    </p>
  </div>
    """
    layer_id = context.variable('layer_id')
    layer = QgsProject.instance().mapLayer(layer_id)
    geom = feature.geometry()
    if not layer.crs().isGeographic():
        crsProj = layer.crs()
        crsGeo = QgsCoordinateReferenceSystem(crsProj.geographicCrsAuthId())
        coordinateTransformer = QgsCoordinateTransform()
        coordinateTransformer.setDestinationCrs(crsGeo)
        coordinateTransformer.setSourceCrs(crsProj)
        geom.transform(coordinateTransformer)
    else:
        crsGeo = layer.crs()
    geomGeo = geom
    try:
        return perimetroSGL(geomGeo, crsGeo)
    except:
        return tr('Check the geometry type!', 'Verifique o tipo de geometria!')


@qgsfunction(args='auto', group='LF Tools')
def lengthLTP (geometry, layer_crs, dimension, feature, parent):
    """
    Calculates the 2D or 3D length on the Local Tangent Plane (LTP), also known as Local Geodetic Coordinate System, which is a spatial reference system based on the tangent plane on the feature centroid defined by the local vertical direction.
    <p>Note: LineStringZ or MultiLineStringZ should be used to obtain the most accurate result.</p>
    <h2>Examples:</h2>
    <ul>
      <li> lengthLTP(geometry, layer_crs, dimension) -> length </li>
      <li> lengthLTP($geometry, 'EPSG:4326', '2d') -> 12.45 </li>
      <li> lengthLTP($geometry, 'EPSG:4326', '3d') -> 12.59 </li>
    </ul>
    <div>
    <p><b>About the LTP:</b></p>
    <p>
    <b><a href="https://geoone.com.br/sistema-geodesico-local/" target="_blank">França, L. Local Geodetic Coordinate System. GeoOne. 2022.</a></b>
    </p>
  </div>
    """
    layer_crs = QgsCoordinateReferenceSystem(layer_crs)
    geom = geometry
    if not layer_crs.isGeographic():
        crsProj = layer_crs
        crsGeo = QgsCoordinateReferenceSystem(crsProj.geographicCrsAuthId())
        coordinateTransformer = QgsCoordinateTransform()
        coordinateTransformer.setDestinationCrs(crsGeo)
        coordinateTransformer.setSourceCrs(crsProj)
        geom.transform(coordinateTransformer)
    else:
        crsGeo = layer_crs
    geomGeo = geom
    try:
        return comprimentoSGL(geomGeo, crsGeo, dimension)
    except:
        return tr('Check the geometry type', 'Verifique o tipo de geometria')


@qgsfunction(args='auto', group='LF Tools', name = '$lengthLTP2d')
def lengthLTP2 (feature, parent, context):
    """
    Calculates the 2D or 3D length on the Local Tangent Plane (LTP), also known as Local Geodetic Coordinate System, which is a spatial reference system based on the tangent plane on the feature centroid defined by the local vertical direction.
    <p>Note: LineStringZ or MultiLineStringZ should be used to obtain the most accurate result.</p>
    <h2>Examples:</h2>
    <ul>
      <li> $lengthLTP2d -> 12.45 </li>
    </ul>
    <div>
    <p><b>About the LTP:</b></p>
    <p>
    <b><a href="https://geoone.com.br/sistema-geodesico-local/" target="_blank">França, L. Local Geodetic Coordinate System. GeoOne. 2022.</a></b>
    </p>
  </div>
    """
    dimension = '2d'
    layer_id = context.variable('layer_id')
    layer = QgsProject.instance().mapLayer(layer_id)
    geom = feature.geometry()
    if not layer.crs().isGeographic():
        crsProj = layer.crs()
        crsGeo = QgsCoordinateReferenceSystem(crsProj.geographicCrsAuthId())
        coordinateTransformer = QgsCoordinateTransform()
        coordinateTransformer.setDestinationCrs(crsGeo)
        coordinateTransformer.setSourceCrs(crsProj)
        geom.transform(coordinateTransformer)
    else:
        crsGeo = layer.crs()
    geomGeo = geom
    try:
        return comprimentoSGL(geomGeo, crsGeo, dimension)
    except:
        return tr('Check the geometry type', 'Verifique o tipo de geometria')


@qgsfunction(args='auto', group='LF Tools', name = '$lengthLTP3d')
def lengthLTP3 (feature, parent, context):
    """
    Calculates the 2D or 3D length on the Local Tangent Plane (LTP), also known as Local Geodetic Coordinate System, which is a spatial reference system based on the tangent plane on the feature centroid defined by the local vertical direction.
    <p>Note: LineStringZ or MultiLineStringZ should be used to obtain the most accurate result.</p>
    <h2>Examples:</h2>
    <ul>
      <li> $lengthLTP3d -> 12.59 </li>
    </ul>
    <div>
    <p><b>About the LTP:</b></p>
    <p>
    <b><a href="https://geoone.com.br/sistema-geodesico-local/" target="_blank">França, L. Local Geodetic Coordinate System. GeoOne. 2022.</a></b>
    </p>
  </div>
    """
    dimension = '3d'
    layer_id = context.variable('layer_id')
    layer = QgsProject.instance().mapLayer(layer_id)
    geom = feature.geometry()
    if not layer.crs().isGeographic():
        crsProj = layer.crs()
        crsGeo = QgsCoordinateReferenceSystem(crsProj.geographicCrsAuthId())
        coordinateTransformer = QgsCoordinateTransform()
        coordinateTransformer.setDestinationCrs(crsGeo)
        coordinateTransformer.setSourceCrs(crsProj)
        geom.transform(coordinateTransformer)
    else:
        crsGeo = layer.crs()
    geomGeo = geom
    try:
        return comprimentoSGL(geomGeo, crsGeo, dimension)
    except:
        return tr('Check the geometry type', 'Verifique o tipo de geometria')


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
def dinamictable(titulo, campos, apelidos, decimal, fator, compensador, feature, parent):
    """
    Generates a dynamic HTML table from a list of numeric fields with the sum of their values for each feature.
    <p>Note 1: Values equal to zero are ignored.</p>
    <p>Note 2: Values are multiplied by the factor.</p>
    <p>Note 3: Values are proportionally compensating for rounding errors by the compensator value. If you wish to ignore, fill in as -1.</p>
    <h2>Examples:</h2>
    <ul>
      <li>dinamictable(title, fields, alias, precision, factor, compensator) -> HTML</li>
      <li>dinamictable('Table 1', 'field1,field2,field3', 'Field 1,Field 2,Field 3',2, 1, -1) -> HTML</li>
      <li>dinamictable('Report', 'a,b,c', '',2, 0.0001, 100) -> HTML</li>
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
     style="font-size: 8pt; color: black;"
     lang="PT">[TITULO]<o:p></o:p></span></b></span></p>
          </td>
        </tr>
        <tr style="height: 10.95pt;">
          <td
     style="border-style: none solid solid; border-color: -moz-use-text-color windowtext windowtext; border-width: medium 1pt 1pt; padding: 0cm 5.4pt; width: 106.15pt; height: 10.95pt;"
     width="142">
          <p class="MsoBodyText" style="text-align: center;"
     align="center"><span class="eop"><span
     style="font-size: 8pt; color: black;"
     lang="PT">''' + tr('CLASS', 'CLASSE') + '''<o:p></o:p></span></span></p>
          </td>
          <td
     style="border-style: none solid solid none; border-color: -moz-use-text-color windowtext windowtext -moz-use-text-color; border-width: medium 1pt 1pt medium; padding: 0cm 5.4pt; width: 106.2pt; height: 10.95pt;"
     width="142">
          <p class="MsoBodyText" style="text-align: center;"
     align="center"><span class="eop"><span
     style="font-size: 8pt; color: black;"
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
     style="font-size: 8pt; color: black;"
     lang="PT">''' + tr('SUM', 'TOTAL') + ''':<o:p></o:p></span></span></p>
          </td>
          <td
     style="border-style: none solid solid none; border-color: -moz-use-text-color windowtext windowtext -moz-use-text-color; border-width: medium 1pt 1pt medium; padding: 0cm 5.4pt; width: 106.2pt; height: 10.95pt;"
     width="142">
          <p class="MsoBodyText" style="text-align: center;"
     align="center"><span class="eop"><span
     style="font-size: 8pt; color: black;"
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
     style="font-size: 8pt; color: black;"
     lang="PT">[NOME]<o:p></o:p></span></span></p>
          </td>
          <td
     style="border-style: none solid solid none; border-color: -moz-use-text-color windowtext windowtext -moz-use-text-color; border-width: medium 1pt 1pt medium; padding: 0cm 5.4pt; width: 106.2pt; height: 10.9pt;"
     width="142">
          <p class="MsoBodyText" style="text-align: center;"
     align="center"><span class="eop"><span
     style="font-size: 8pt; color: black;"
     lang="PT"><o:p>[VALOR]&nbsp;</o:p></span></span></p>
          </td>
        </tr>
    '''

    soma = 0
    dic = {}
    for k, campo in enumerate(campos):
        valor = round(feature[campo]*fator, decimal)
        if valor > 0:
            soma += valor
            if valor > 10**(-1*decimal):
                dic[apelidos[k]] = valor

    lista = list(dic.keys())
    lista.sort()

    if compensador > 0:
        soma = 0
        compensador = int(round(round(compensador, decimal)*(10**(decimal))))
        valores = []
        for item in lista:
            valores += [int(dic[item]*10**(decimal))]
        compensados = proportion(valores, compensador)
        for k, item in enumerate(lista):
            valor = compensados[k]/10**(decimal)
            dic[item] = valor
            soma += valor

    linhas =''
    for item in lista:
        linha0 = linha
        linha0 = linha0.replace('[NOME]', item).replace('[VALOR]', format_num.format(dic[item]).replace(',', 'X').replace('.', ',').replace('X', '.'))
        linhas += linha0
    texto = tabela
    texto = texto.replace('[LINHAS]', linhas).replace('[TITULO]', str2HTML(titulo)).replace('[TOTAL]', format_num.format(soma).replace(',', 'X').replace('.', ',').replace('X', '.'))

    return texto



def template_table(tipo, azimuth_dist, dimension):
    texto = '''<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
        <html>
        <head>
          <title>''' + str2HTML(tr('Synthetic deed description', 'Memorial Sintético')) + '''</title>    </head>
        <body>
        <table
        style="text-align: center; width: 100%; font-size: [FONTSIZE]px;  border: medium none; border-collapse: collapse;"
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

    # Definição de cabeçalhos

    dimension = dimension.lower()
    if dimension == '2d':
        # UTM
        if tipo == 'proj' and azimuth_dist > 0:
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
                <td colspan="6" rowspan="1">''' + str2HTML(tr('Synthetic deed description', 'Memorial Sintético').upper()) + '''[TITULO]</td>
            </tr>
            <tr>
                <td colspan="1" rowspan="2">''' + str2HTML(tr('VERTEX', 'VÉRTICE')) + '''</td>
                <td colspan="2" rowspan="1">''' + str2HTML(tr('COORDINATE', 'COORDENADA')) + '''</td>
                <td colspan="1" rowspan="2">''' + str2HTML(tr('SIDE', 'LADO')) + '''</td>
                <td colspan="1" rowspan="2">''' + str2HTML(tr('AZIMUTH', 'AZIMUTE')) + '''</td>
                <td colspan="1" rowspan="2">''' + str2HTML(tr('DISTANCE', 'DISTÂNCIA')) + ''' (m)</td>
            </tr>
            <tr>
                <td>E</td>
                <td>N</td>
            </tr>'''

        # UTM sem Az e d
        if tipo == 'proj' and azimuth_dist == 0:
            linha = '''<tr>
            <td>Vn</td>
            <td>En</td>
            <td>Nn</td>
        </tr>
        '''

            cabec = '''<tr>
                <td colspan="3" rowspan="1">''' + str2HTML(tr('Synthetic deed description', 'Memorial Sintético').upper()) + '''[TITULO]</td>
            </tr>
            <tr>
                <td colspan="1" rowspan="2">''' + str2HTML(tr('VERTEX', 'VÉRTICE')) + '''</td>
                <td colspan="2" rowspan="1">''' + str2HTML(tr('COORDINATE', 'COORDENADA')) + '''</td>
            </tr>
            <tr>
                <td>E</td>
                <td>N</td>
            </tr>'''

        # GEO
        if 'geo' in tipo and azimuth_dist > 0:
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
                <td colspan="6" rowspan="1">''' + str2HTML(tr('Synthetic deed description', 'Memorial Sintético').upper()) + '''[TITULO]</td>
            </tr>
            <tr>
                <td colspan="1" rowspan="2">''' + str2HTML(tr('VERTEX', 'VÉRTICE')) + '''</td>
                <td colspan="2" rowspan="1">''' + str2HTML(tr('COORDINATE', 'COORDENADA')) + '''</td>
                <td colspan="1" rowspan="2">''' + str2HTML(tr('SIDE', 'LADO')) + '''</td>
                <td colspan="1" rowspan="2">''' + str2HTML(tr('AZIMUTH', 'AZIMUTE')) + '''</td>
                <td colspan="1" rowspan="2">''' + str2HTML(tr('DISTANCE', 'DISTÂNCIA')) + ''' (m)</td>
            </tr>
            <tr>
                <td>longitude</td>
                <td>latitude</td>
            </tr>'''

        # GEO sem Az e d
        if 'geo' in tipo and azimuth_dist == 0:
            linha = '''<tr>
                <td>Vn</td>
                <td>lonn</td>
                <td>latn</td>
            </tr>
            '''

            cabec = '''<tr>
                <td colspan="3" rowspan="1">''' + str2HTML(tr('Synthetic deed description', 'Memorial Sintético').upper()) + '''[TITULO]</td>
            </tr>
            <tr>
                <td colspan="1" rowspan="2">''' + str2HTML(tr('VERTEX', 'VÉRTICE')) + '''</td>
                <td colspan="2" rowspan="1">''' + str2HTML(tr('COORDINATE', 'COORDENADA')) + '''</td>
            </tr>
            <tr>
                <td>longitude</td>
                <td>latitude</td>
            </tr>'''

        # UTM e GEO
        if tipo == 'both' and azimuth_dist > 0:
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
                <td colspan="8" rowspan="1">''' + str2HTML(tr('Synthetic deed description', 'Memorial Sintético').upper()) + '''[TITULO]</td>
            </tr>
            <tr>
                <td colspan="1" rowspan="2">''' + str2HTML(tr('VERTEX', 'VÉRTICE')) + '''</td>
                <td colspan="4" rowspan="1">''' + str2HTML(tr('COORDINATE', 'COORDENADA')) + '''</td>
                <td colspan="1" rowspan="2">''' + str2HTML(tr('SIDE', 'LADO')) + '''</td>
                <td colspan="1" rowspan="2">''' + str2HTML(tr('AZIMUTH', 'AZIMUTE')) + '''</td>
                <td colspan="1" rowspan="2">''' + str2HTML(tr('DISTANCE', 'DISTÂNCIA')) + ''' (m)</td>
            </tr>
            <tr>
                <td>longitude</td>
                <td>latitude</td>
                <td>E</td>
                <td>N</td>
            </tr>'''

        # UTM e GEO sem Az e d
        if tipo == 'both' and azimuth_dist == 0:
            linha = '''<tr>
                <td>Vn</td>
                <td>lonn</td>
                <td>latn</td>
                <td>En</td>
                <td>Nn</td>
            </tr>
            '''

            cabec = '''<tr>
                <td colspan="5" rowspan="1">''' + str2HTML(tr('Synthetic deed description', 'Memorial Sintético').upper()) + '''[TITULO]</td>
            </tr>
            <tr>
                <td colspan="1" rowspan="2">''' + str2HTML(tr('VERTEX', 'VÉRTICE')) + '''</td>
                <td colspan="4" rowspan="1">''' + str2HTML(tr('COORDINATE', 'COORDENADA')) + '''</td>
            </tr>
            <tr>
                <td>longitude</td>
                <td>latitude</td>
                <td>E</td>
                <td>N</td>
            </tr>'''
    elif dimension == '3d':

        # UTM
        if tipo == 'proj' and azimuth_dist > 0:
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
              <td colspan="7" rowspan="1">''' + str2HTML(tr('Synthetic deed description', 'Memorial Sintético').upper()) + '''[TITULO]</td>
            </tr>
            <tr>
              <td colspan="1" rowspan="2">''' + str2HTML(tr('VERTEX', 'VÉRTICE')) + '''</td>
              <td colspan="3" rowspan="1">''' + str2HTML(tr('COORDINATE', 'COORDENADA')) + '''</td>
              <td colspan="1" rowspan="2">''' + str2HTML(tr('SIDE', 'LADO')) + '''</td>
              <td colspan="1" rowspan="2">''' + str2HTML(tr('AZIMUTH', 'AZIMUTE')) + '''</td>
              <td colspan="1" rowspan="2">''' + str2HTML(tr('DISTANCE', 'DISTÂNCIA')) + ''' (m)</td>
            </tr>
            <tr>
              <td>E</td>
              <td>N</td>
              <td>h</td>
            </tr>'''

        # UTM sem Az e d
        if tipo == 'proj' and azimuth_dist== 0:
            linha = '''<tr>
          <td>Vn</td>
          <td>En</td>
          <td>Nn</td>
          <td>hn</td>
        </tr>
        '''

            cabec = '''<tr>
              <td colspan="4" rowspan="1">''' + str2HTML(tr('Synthetic deed description', 'Memorial Sintético').upper()) + '''[TITULO]</td>
            </tr>
            <tr>
              <td colspan="1" rowspan="2">''' + str2HTML(tr('VERTEX', 'VÉRTICE')) + '''</td>
              <td colspan="3" rowspan="1">''' + str2HTML(tr('COORDINATE', 'COORDENADA')) + '''</td>
            </tr>
            <tr>
              <td>E</td>
              <td>N</td>
              <td>h</td>
            </tr>'''

        # GEO
        if 'geo' in tipo and azimuth_dist> 0:
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
              <td colspan="7" rowspan="1">''' + str2HTML(tr('Synthetic deed description', 'Memorial Sintético').upper()) + '''[TITULO]</td>
            </tr>
            <tr>
              <td colspan="1" rowspan="2">''' + str2HTML(tr('VERTEX', 'VÉRTICE')) + '''</td>
              <td colspan="3" rowspan="1">''' + str2HTML(tr('COORDINATE', 'COORDENADA')) + '''</td>
              <td colspan="1" rowspan="2">''' + str2HTML(tr('SIDE', 'LADO')) + '''</td>
              <td colspan="1" rowspan="2">''' + str2HTML(tr('AZIMUTH', 'AZIMUTE')) + '''</td>
              <td colspan="1" rowspan="2">''' + str2HTML(tr('DISTANCE', 'DISTÂNCIA')) + ''' (m)</td>
            </tr>
            <tr>
              <td>longitude</td>
              <td>latitude</td>
              <td>h</td>
            </tr>'''

        # GEO sem Az e d
        if 'geo' in tipo and azimuth_dist== 0:
            linha = '''<tr>
              <td>Vn</td>
              <td>lonn</td>
              <td>latn</td>
              <td>hn</td>
            </tr>
            '''

            cabec = '''<tr>
              <td colspan="4" rowspan="1">''' + str2HTML(tr('Synthetic deed description', 'Memorial Sintético').upper()) + '''[TITULO]</td>
            </tr>
            <tr>
              <td colspan="1" rowspan="2">''' + str2HTML(tr('VERTEX', 'VÉRTICE')) + '''</td>
              <td colspan="3" rowspan="1">''' + str2HTML(tr('COORDINATE', 'COORDENADA')) + '''</td>
            </tr>
            <tr>
              <td>longitude</td>
              <td>latitude</td>
              <td>h</td>
            </tr>'''

        # UTM e GEO
        if tipo == 'both' and azimuth_dist> 0:
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
              <td colspan="9" rowspan="1">''' + str2HTML(tr('Synthetic deed description', 'Memorial Sintético').upper()) + '''[TITULO]</td>
            </tr>
            <tr>
              <td colspan="1" rowspan="2">''' + str2HTML(tr('VERTEX', 'VÉRTICE')) + '''</td>
              <td colspan="5" rowspan="1">''' + str2HTML(tr('COORDINATE', 'COORDENADA')) + '''</td>
              <td colspan="1" rowspan="2">''' + str2HTML(tr('SIDE', 'LADO')) + '''</td>
              <td colspan="1" rowspan="2">''' + str2HTML(tr('AZIMUTH', 'AZIMUTE')) + '''</td>
              <td colspan="1" rowspan="2">''' + str2HTML(tr('DISTANCE', 'DISTÂNCIA')) + ''' (m)</td>
            </tr>
            <tr>
              <td>longitude</td>
              <td>latitude</td>
              <td>E</td>
              <td>N</td>
              <td>h</td>
            </tr>'''

        # UTM e GEO sem Az e d
        if tipo == 'both' and azimuth_dist== 0:
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
              <td colspan="6" rowspan="1">''' + str2HTML(tr('Synthetic deed description', 'Memorial Sintético').upper()) + '''[TITULO]</td>
            </tr>
            <tr>
              <td colspan="1" rowspan="2">''' + str2HTML(tr('VERTEX', 'VÉRTICE')) + '''</td>
              <td colspan="5" rowspan="1">''' + str2HTML(tr('COORDINATE', 'COORDENADA')) + '''</td>
            </tr>
            <tr>
              <td>longitude</td>
              <td>latitude</td>
              <td>E</td>
              <td>N</td>
              <td>h</td>
            </tr>'''

    return texto, linha, cabec



@qgsfunction(args='auto', group='LF Tools')
def deedtable(layer_name, ini, fim, titulo, decimal, fontsize, tipo, azimuth_dist, feature, parent):
    """
    Generates the Vertices and Sides for a Descriptive Table, also known as Synthetic Deed Description, based on the layer'sattributes: sequence and code.
    <p>Note 1: A layer or QGIS Project with a projected SRC is required.</p>
    <p>Note 2: Types: 'proj' - projected, 'geo' - geographic, 'both' - both coordinate systems.</p>
    <p>Note 3: Use 'geo-suffix' for geographic with suffix.</p>
    <p>Note 4: The value of "precision" can be an integer that will be applied to coordinate and distance, or an array with 3 numbers for the precision of the coordinates, azimuth and distances, respectively.</p>

    <h2>Exemples:</h2>
    <ul>
      <li>deedtable('layer_name', start, end, 'title', precision, fontsize, coord_type, azimuth_dist) = HTML</li>
      <li>deedtable('Limit Point', 1, 20, 'Area X', 3, 10, 'proj', 1) = HTML</li>
      <li>deedtable('Vertices', 1, -1, 'Property B', 2, 12, 'geo', 0) = HTML</li>
    </ul>

    <h2>Choose the method for calculating azimuths and distances:</h2>
    <ul>
      <li>azimuth_dist = 0 ➡️ No azimuths and distances</li>
      <li>azimuth_dist = 1 ➡️ Layer or projection CRS</li>
      <li>azimuth_dist = 2 ➡️ Local Tangent Plane (LTP)</li>
      <li>azimuth_dist = 3 ➡️ LTP distance and Puissant azimuth</li>
    </ul>
    """
    # Novos parâmetros: decimal, tipo, azimuth_dist

    tipo = tipo.lower()

    if isinstance(decimal, list):
        if not isinstance(decimal[0], int):
            prec_h = round(10*float(decimal[0] - np.floor(decimal[0])))
            decimal[0] = int(decimal[0])
        else:
            prec_h = decimal[0]
        format_utm = '{:,.Xf}'.replace('X', str(decimal[0]))
        format_h = '{:,.Xf}'.replace('X', str(prec_h))
        prec_geo = decimal[0]
        prec_Azimute = decimal[1]
        format_dist = '{:,.Xf}'.replace('X', str(decimal[2]))
    else:
        if not isinstance(decimal, int):
            prec_h = round(10*float(decimal - np.floor(decimal)))
            decimal = int(decimal)
        else:
            prec_h = decimal
        format_utm = '{:,.Xf}'.replace('X', str(decimal))
        format_h = '{:,.Xf}'.replace('X', str(prec_h))
        prec_geo = decimal + 2
        prec_Azimute = 1
        format_dist = '{:,.Xf}'.replace('X', str(decimal))

    # Templates HTML
    texto, linha, cabec = template_table(tipo, azimuth_dist, '3d')

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
        pnts_UTM[feat['sequence']] = [coordinateTransformer.transform(pnt), feat['type'], feat['code'] ]
        pnts_GEO[feat['sequence']] = [QgsPoint(pnt.x(),pnt.y(),coord.z()), feat['type'], feat['code'] ]

    # Calculo dos Azimutes e Distancias
    tam = len(pnts_UTM)
    Az_lista, lista_pnts, Dist = [], [], []
    crsGeo = SRC
    for k in range(tam):
        lista_pnts += [pnts_GEO[k+1][0]]
    # criar poligono a partir dos pontos da camada
    anel_ext = QgsLineString(lista_pnts)
    pol = QgsPolygon(anel_ext)
    geomGeo = QgsGeometry(pol)

    if azimuth_dist == 1: # Projetadas (Ex: UTM)
        for k in range(tam):
            pntA = pnts_UTM[k+1][0]
            pntB = pnts_UTM[1 if k+2 > tam else k+2][0]
            Az_lista += [(180/pi)*azimute(pntA, pntB)[0]]
            Dist += [sqrt((pntA.x() - pntB.x())**2 + (pntA.y() - pntB.y())**2)]
    elif azimuth_dist == 2: # SGL
        for k in range(tam):
            pntA = pnts_GEO[k+1][0]
            pntB = pnts_GEO[1 if k+2 > tam else k+2][0]
            Az, dist = AzimuteDistanciaSGL(pntA, pntB, geomGeo, crsGeo, 'SGL')
            Az_lista += [Az]
            Dist += [dist]
    elif azimuth_dist == 3: # SGL e Puissant
        for k in range(tam):
            pntA = pnts_GEO[k+1][0]
            pntB = pnts_GEO[1 if k+2 > tam else k+2][0]
            Az, dist = AzimuteDistanciaSGL(pntA, pntB, geomGeo, crsGeo, 'puissant')
            Az_lista += [Az]
            Dist += [dist]
    elif azimuth_dist == 0: # Sem cálculo de Azimute e distância
        for k in range(tam):
            Az_lista += [0]
            Dist += [0]

    LINHAS = ''
    if fim == -1 or fim > tam:
        fim = tam
    for k in range(ini-1,fim):
        linha0 = linha
        lonn = tr(DD2DMS(pnts_GEO[k+1][0].x(),prec_geo), DD2DMS(pnts_GEO[k+1][0].x(),prec_geo).replace('.', ','))
        latn = tr(DD2DMS(pnts_GEO[k+1][0].y(),prec_geo), DD2DMS(pnts_GEO[k+1][0].y(),prec_geo).replace('.', ','))
        if 'suffix' in tipo:
            lonn = lonn.replace('-', '') + str('W' if pnts_GEO[k+1][0].x() < 0 else 'E')
            latn = latn.replace('-', '') + str('S' if pnts_GEO[k+1][0].y() < 0 else 'N')
        itens = {'Vn': pnts_UTM[k+1][2],
                 'En': tr(format_utm.format(pnts_UTM[k+1][0].x()), format_utm.format(pnts_UTM[k+1][0].x()).replace(',', 'X').replace('.', ',').replace('X', '.')),
                 'Nn': tr(format_utm.format(pnts_UTM[k+1][0].y()), format_utm.format(pnts_UTM[k+1][0].y()).replace(',', 'X').replace('.', ',').replace('X', '.')),
                 'hn': tr(format_h.format(pnts_GEO[k+1][0].z()), format_h.format(pnts_GEO[k+1][0].z()).replace(',', 'X').replace('.', ',').replace('X', '.')),
                 'lonn': lonn,
                 'latn': latn,
                 'Ln': pnts_UTM[k+1][2] + '/' + pnts_UTM[1 if k+2 > tam else k+2][2],
                 'Az_n': tr(DD2DMS(Az_lista[k], prec_Azimute), DD2DMS(Az_lista[k], prec_Azimute).replace('.', ',')),
                 'Dn': tr(format_dist.format(Dist[k]), format_dist.format(Dist[k]).replace(',', 'X').replace('.', ',').replace('X', '.'))
                 }
        for item in itens:
            linha0 = linha0.replace(item, itens[item])
        LINHAS += linha0
    resultado = texto.replace('[CABECALHO]', cabec).replace('[LINHAS]', LINHAS).replace('[TITULO]', str2HTML(titulo.upper())).replace('[FONTSIZE]', str(fontsize))
    return resultado



@qgsfunction(args='auto', group='LF Tools')
def deedtable2(prefix, titulo, decimal, fontsize, tipo, azimuth_dist, feature, parent, context):
    """
    Generates the 2D Vertices and Sides Descriptive Table, also known as Synthetic Deed Description, based on vertices of a Polygon or Linestring.
    <p>Note 1: A layer or QGIS Project with a projected SRC is required.</p>
    <p>Note 2: Table types: 'proj' - projected, 'geo' - geographic, 'both' - both coordinate systems.</p>
    <p>Note 3: Use 'geo-suffix' for geographic with suffix.</p>
    <p>Note 4: The value of "precision" can be an integer that will be applied to coordinate and distance, or an array with 3 numbers for the precision of the coordinates, azimuth and distances, respectively.</p>

    <h2>Exemples:</h2>
    <ul>
      <li>deedtable2('preffix', 'title', precision, fontsize, type, azimuth_dist) = HTML</li>
      <li>deedtable2('V-', ' - Area X', 3, 12, 'proj', 1) = HTML</li>
      <li>deedtable2('V-', ' - Area X', 3, 12, 'geo', 0) = HTML</li>
      <li>deedtable2('V-', ' - Area X', 3, 12, 'both', 1) = HTML</li>
    </ul>

    <h2>Exemple with vertex layer:</h2>
    <ul>
      <li>deedtable2('vertex_point_layer,ID,name', 'title', precision, fontsize, type, azimuth_dist) = HTML</li>
      <li>deedtable2('Vertex,id,name', ' - Area Z', 3, 12, 'both', 1) = HTML</li>
    </ul>

    <h2>Exemple with different precisions:</h2>
    <ul>
      <li>deedtable2('preffix', 'title', array(coord,azimuth,distance), fontsize, type, azimuth_dist) = HTML</li>
      <li>deedtable2('M-', ' - Property', array(3,0,2), 10, 'both', 0) = HTML</li>
    </ul>

    <h2>Choose the method for calculating azimuths and distances:</h2>
    <ul>
      <li>azimuth_dist = 0 ➡️ No azimuths and distances</li>
      <li>azimuth_dist = 1 ➡️ Layer or projection CRS</li>
      <li>azimuth_dist = 2 ➡️ Local Tangent Plane (LTP)</li>
      <li>azimuth_dist = 3 ➡️ LTP distance and Puissant azimuth</li>
    </ul>
    """
    layer_id = context.variable('layer_id')
    layer = QgsProject.instance().mapLayer(layer_id)
    SRC = layer.crs()
    SGR = QgsCoordinateReferenceSystem(SRC.geographicCrsAuthId())

    tipo = tipo.lower()

    if isinstance(decimal, list):
        if not isinstance(decimal[0], int):
            prec_h = round(10*float(decimal[0] - np.floor(decimal[0])))
            decimal[0] = int(decimal[0])
        else:
            prec_h = decimal[0]
        format_utm = '{:,.Xf}'.replace('X', str(decimal[0]))
        format_h = '{:,.Xf}'.replace('X', str(prec_h))
        prec_geo = decimal[0]
        prec_Azimute = decimal[1]
        format_dist = '{:,.Xf}'.replace('X', str(decimal[2]))
    else:
        if not isinstance(decimal, int):
            prec_h = round(10*float(decimal - np.floor(decimal)))
            decimal = int(decimal)
        else:
            prec_h = decimal
        format_utm = '{:,.Xf}'.replace('X', str(decimal))
        format_h = '{:,.Xf}'.replace('X', str(prec_h))
        prec_geo = decimal + 2
        prec_Azimute = 1
        format_dist = '{:,.Xf}'.replace('X', str(decimal))

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
            tol = 0.01 # tolerancia 1 cm

            for k, coord in enumerate(coords[:-1] if TipoGeometria == 2 else coords):
                pnt = coordinateTransformer.transform(QgsPointXY(coord.x(), coord.y()))
                if 'prefixo' in locals():
                    pnts_UTM[k+1] = [coord, prefixo, prefixo + '{:02}'.format(k+1)]
                    pnts_GEO[k+1] = [QgsPoint(pnt.x(),pnt.y(),coord.z()), prefixo, prefixo + '{:02}'.format(k+1) ]
                else:
                    for feat in layer.getFeatures(QgsFeatureRequest(exp)):
                        # Identificar ponto correspondente
                        pnt_corresp = feat.geometry().asPoint()
                        if abs(coord.x() - pnt_corresp.x()) < tol and abs(coord.y() - pnt_corresp.y()) < tol:
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
            tol = 0.01/111000 # tolerancia 1 cm em graus

            for k, coord in enumerate(coords[:-1] if TipoGeometria == 2 else coords):
                pnt = coordinateTransformer.transform(QgsPointXY(coord.x(), coord.y()))
                if 'prefixo' in locals():
                    pnts_GEO[k+1] = [coord, prefixo, prefixo + '{:02}'.format(k+1)]
                    pnts_UTM[k+1] = [QgsPoint(pnt.x(),pnt.y(),coord.z()), prefixo, prefixo + '{:02}'.format(k+1) ]
                else:
                    for feat in layer.getFeatures(QgsFeatureRequest(exp)):
                        # Identificar ponto correspondente
                        pnt_corresp = feat.geometry().asPoint()
                        if abs(coord.x() - pnt_corresp.x()) < tol and abs(coord.y() - pnt_corresp.y()) < tol:
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

        # Calcular geomGeo e crsGeo
        if not layer.crs().isGeographic():
            geom.transform(coordinateTransformer)
        crsGeo = SGR
        geomGeo = geom

        if TipoGeometria == 2: # Polígono

            if azimuth_dist == 1: # Projetadas (Ex: UTM)
                for k in range(tam):
                    pntA = pnts_UTM[k+1][0]
                    pntB = pnts_UTM[1 if k+2 > tam else k+2][0]
                    Az_lista += [(180/pi)*azimute(pntA, pntB)[0]]
                    Dist += [sqrt((pntA.x() - pntB.x())**2 + (pntA.y() - pntB.y())**2)]
            elif azimuth_dist == 2: # SGL
                for k in range(tam):
                    pntA = pnts_GEO[k+1][0]
                    pntB = pnts_GEO[1 if k+2 > tam else k+2][0]
                    Az, dist = AzimuteDistanciaSGL(pntA, pntB, geomGeo, crsGeo, 'SGL')
                    Az_lista += [Az]
                    Dist += [dist]
            elif azimuth_dist == 3: # SGL e Puissant
                for k in range(tam):
                    pntA = pnts_GEO[k+1][0]
                    pntB = pnts_GEO[1 if k+2 > tam else k+2][0]
                    Az, dist = AzimuteDistanciaSGL(pntA, pntB, geomGeo, crsGeo, 'puissant')
                    Az_lista += [Az]
                    Dist += [dist]
            elif azimuth_dist == 0: # Sem cálculo de Azimute e distância
                for k in range(tam):
                    Az_lista += [0]
                    Dist += [0]

        else: # Linha

            if azimuth_dist == 1: # Projetadas (Ex: UTM)
                for k in range(tam-1):
                    pntA = pnts_UTM[k+1][0]
                    pntB = pnts_UTM[k+2][0]
                    Az_lista += [(180/pi)*azimute(pntA, pntB)[0]]
                    Dist += [sqrt((pntA.x() - pntB.x())**2 + (pntA.y() - pntB.y())**2)]
            elif azimuth_dist == 2: # SGL
                for k in range(tam-1):
                    pntA = pnts_GEO[k+1][0]
                    pntB = pnts_GEO[k+2][0]
                    Az, dist = AzimuteDistanciaSGL(pntA, pntB, geomGeo, crsGeo, 'SGL')
                    Az_lista += [Az]
                    Dist += [dist]
            elif azimuth_dist == 3: # SGL e Puissant
                for k in range(tam-1):
                    pntA = pnts_GEO[k+1][0]
                    pntB = pnts_GEO[k+2][0]
                    Az, dist = AzimuteDistanciaSGL(pntA, pntB, geomGeo, crsGeo, 'puissant')
                    Az_lista += [Az]
                    Dist += [dist]
            elif azimuth_dist == 0: # Sem cálculo de Azimute e distância
                for k in range(tam-1):
                    Az_lista += [0]
                    Dist += [0]

        texto, linha, cabec = template_table(tipo, azimuth_dist, '2d')

        LINHAS = ''
        for k in range(tam):
            linha0 = linha
            lonn = tr(DD2DMS(pnts_GEO[k+1][0].x(),prec_geo), DD2DMS(pnts_GEO[k+1][0].x(),prec_geo).replace('.', ','))
            latn = tr(DD2DMS(pnts_GEO[k+1][0].y(),prec_geo), DD2DMS(pnts_GEO[k+1][0].y(),prec_geo).replace('.', ','))
            if 'suffix' in tipo:
                lonn = lonn.replace('-', '') + str('W' if pnts_GEO[k+1][0].x() < 0 else 'E')
                latn = latn.replace('-', '') + str('S' if pnts_GEO[k+1][0].y() < 0 else 'N')
            itens = {'Vn': pnts_UTM[k+1][2],
                        'En': tr(format_utm.format(pnts_UTM[k+1][0].x()), format_utm.format(pnts_UTM[k+1][0].x()).replace(',', 'X').replace('.', ',').replace('X', '.')),
                        'Nn': tr(format_utm.format(pnts_UTM[k+1][0].y()), format_utm.format(pnts_UTM[k+1][0].y()).replace(',', 'X').replace('.', ',').replace('X', '.')),
                        'lonn': lonn,
                        'latn': latn,
                        'Ln': '-' if TipoGeometria == 1 and k+1 == tam else pnts_UTM[k+1][2] + '/' + pnts_UTM[1 if k+2 > tam else k+2][2],
                        'Az_n': '-' if TipoGeometria == 1 and k+1 == tam else tr(DD2DMS(Az_lista[k],prec_Azimute), DD2DMS(Az_lista[k],prec_Azimute).replace('.', ',')),
                        'Dn': '-' if TipoGeometria == 1 and k+1 == tam else tr(format_dist.format(Dist[k]), format_dist.format(Dist[k]).replace(',', 'X').replace('.', ',').replace('X', '.'))
                        }
            for item in itens:
                linha0 = linha0.replace(item, itens[item])
            LINHAS += linha0

        resultado = texto.replace('[CABECALHO]', cabec).replace('[LINHAS]', LINHAS).replace('[TITULO]', str2HTML(titulo.upper())).replace('[FONTSIZE]', str(fontsize))

        return resultado

    else:
        return tr('Check if the geometry is null or invalid! Or if Atlas is on!', 'Verifique se a geometria é nula ou inválida! Ou se o Atlas está ligado!')



@qgsfunction(args='auto', group='LF Tools')
def deedtable3(prefix, titulo, decimal, fontsize, tipo, azimuth_dist, feature, parent, context):
    """
    Generates the 3D Vertices and Sides Descriptive Table, also known as Synthetic Deed Description, based on vertices of a PolygonZ or LinestringZ.
    <p>Note 1: A layer or QGIS Project with a projected SRC is required.</p>
    <p>Note 2: Table types: 'proj' - projected, 'geo' - geographic, 'both' - both coordinate systems.</p>
    <p>Note 3: Use 'geo-suffix' for geographic with suffix.</p>
    <p>Note 4: The value of "precision" can be an integer that will be applied to coordinate and distance, or an array with 3 numbers for the precision of the coordinates, azimuth and distances, respectively.</p>

    <h2>Exemples:</h2>
    <ul>
      <li>deedtable3('preffix', 'title', precision, fontsize, type, azimuth_dist) = HTML</li>
      <li>deedtable3('V-', ' - Area X', 3, 12, 'proj', 1) = HTML</li>
      <li>deedtable3('V-', ' - Area X', 3, 12, 'geo', 0) = HTML</li>
      <li>deedtable3('P-', ' - Area X', 3, 12, 'both', 1) = HTML</li>
    </ul>

    <h2>Exemple with vertex layer:</h2>
    <ul>
      <li>deedtable3('vertex_point_layer,ID,name', 'title', precision, fontsize, type, azimuth_dist) = HTML</li>
      <li>deedtable3('Vertex,id,name', ' - Area Z', 3, 12, 'both', 1) = HTML</li>
    </ul>

    <h2>Exemple with different precisions:</h2>
    <ul>
      <li>deedtable3('preffix', 'title', array(coord,azimuth,distance), fontsize, type, azimuth_dist) = HTML</li>
      <li>deedtable3('M-', ' - Property', array(3,0,2), 10, 'both', 0) = HTML</li>
    </ul>

    <h2>Choose the method for calculating azimuths and distances:</h2>
    <ul>
      <li>azimuth_dist = 0 ➡️ No azimuths and distances</li>
      <li>azimuth_dist = 1 ➡️ Layer or projection CRS</li>
      <li>azimuth_dist = 2 ➡️ Local Tangent Plane (LTP)</li>
      <li>azimuth_dist = 3 ➡️ LTP distance and Puissant azimuth</li>
    </ul>
    """
    layer_id = context.variable('layer_id')
    layer = QgsProject.instance().mapLayer(layer_id)
    SRC = layer.crs()
    SGR = QgsCoordinateReferenceSystem(SRC.geographicCrsAuthId())

    tipo = tipo.lower()

    if isinstance(decimal, list):
        if not isinstance(decimal[0], int):
            prec_h = round(10*float(decimal[0] - np.floor(decimal[0])))
            decimal[0] = int(decimal[0])
        else:
            prec_h = decimal[0]
        format_utm = '{:,.Xf}'.replace('X', str(decimal[0]))
        format_h = '{:,.Xf}'.replace('X', str(prec_h))
        prec_geo = decimal[0]
        prec_Azimute = decimal[1]
        format_dist = '{:,.Xf}'.replace('X', str(decimal[2]))
    else:
        if not isinstance(decimal, int):
            prec_h = round(10*float(decimal - np.floor(decimal)))
            decimal = int(decimal)
        else:
            prec_h = decimal
        format_utm = '{:,.Xf}'.replace('X', str(decimal))
        format_h = '{:,.Xf}'.replace('X', str(prec_h))
        prec_geo = decimal + 2
        prec_Azimute = 1
        format_dist = '{:,.Xf}'.replace('X', str(decimal))

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
            tol = 0.01 # tolerancia 1 cm

            for k, coord in enumerate(coords[:-1] if TipoGeometria == 2 else coords):
                pnt = coordinateTransformer.transform(QgsPointXY(coord.x(), coord.y()))
                if 'prefixo' in locals():
                    pnts_UTM[k+1] = [coord, prefixo, prefixo + '{:02}'.format(k+1)]
                    pnts_GEO[k+1] = [QgsPoint(pnt.x(),pnt.y(),coord.z()), prefixo, prefixo + '{:02}'.format(k+1) ]
                else:
                    for feat in layer.getFeatures(QgsFeatureRequest(exp)):
                        # Identificar ponto correspondente
                        pnt_corresp = feat.geometry().asPoint()
                        if abs(coord.x() - pnt_corresp.x()) < tol and abs(coord.y() - pnt_corresp.y()) < tol:
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
            tol = 0.01/111000 # tolerancia 1 cm em graus

            for k, coord in enumerate(coords[:-1] if TipoGeometria == 2 else coords):
                pnt = coordinateTransformer.transform(QgsPointXY(coord.x(), coord.y()))
                if 'prefixo' in locals():
                    pnts_GEO[k+1] = [coord, prefixo, prefixo + '{:02}'.format(k+1)]
                    pnts_UTM[k+1] = [QgsPoint(pnt.x(),pnt.y(),coord.z()), prefixo, prefixo + '{:02}'.format(k+1) ]
                else:
                    for feat in layer.getFeatures(QgsFeatureRequest(exp)):
                        # Identificar ponto correspondente
                        pnt_corresp = feat.geometry().asPoint()
                        if abs(coord.x() - pnt_corresp.x()) < tol and abs(coord.y() - pnt_corresp.y()) < tol:
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
        # Calcular geomGeo e crsGeo
        if not layer.crs().isGeographic():
            geom.transform(coordinateTransformer)
        crsGeo = SGR
        geomGeo = geom

        if TipoGeometria == 2: # Polígono

            if azimuth_dist == 1: # Projetadas (Ex: UTM)
                for k in range(tam):
                    pntA = pnts_UTM[k+1][0]
                    pntB = pnts_UTM[1 if k+2 > tam else k+2][0]
                    Az_lista += [(180/pi)*azimute(pntA, pntB)[0]]
                    Dist += [sqrt((pntA.x() - pntB.x())**2 + (pntA.y() - pntB.y())**2)]
            elif azimuth_dist == 2: # SGL
                for k in range(tam):
                    pntA = pnts_GEO[k+1][0]
                    pntB = pnts_GEO[1 if k+2 > tam else k+2][0]
                    Az, dist = AzimuteDistanciaSGL(pntA, pntB, geomGeo, crsGeo, 'SGL')
                    Az_lista += [Az]
                    Dist += [dist]
            elif azimuth_dist == 3: # SGL e Puissant
                for k in range(tam):
                    pntA = pnts_GEO[k+1][0]
                    pntB = pnts_GEO[1 if k+2 > tam else k+2][0]
                    Az, dist = AzimuteDistanciaSGL(pntA, pntB, geomGeo, crsGeo, 'puissant')
                    Az_lista += [Az]
                    Dist += [dist]
            elif azimuth_dist == 0: # Sem cálculo de Azimute e distância
                for k in range(tam):
                    Az_lista += [0]
                    Dist += [0]

        texto, linha, cabec = template_table(tipo, azimuth_dist, '3d')

        LINHAS = ''
        for k in range(tam):
            linha0 = linha
            lonn = tr(DD2DMS(pnts_GEO[k+1][0].x(),prec_geo), DD2DMS(pnts_GEO[k+1][0].x(),prec_geo).replace('.', ','))
            latn = tr(DD2DMS(pnts_GEO[k+1][0].y(),prec_geo), DD2DMS(pnts_GEO[k+1][0].y(),prec_geo).replace('.', ','))
            if 'suffix' in tipo:
                lonn = lonn.replace('-', '') + str('W' if pnts_GEO[k+1][0].x() < 0 else 'E')
                latn = latn.replace('-', '') + str('S' if pnts_GEO[k+1][0].y() < 0 else 'N')
            itens = {'Vn': pnts_UTM[k+1][2],
                        'En': tr(format_utm.format(pnts_UTM[k+1][0].x()), format_utm.format(pnts_UTM[k+1][0].x()).replace(',', 'X').replace('.', ',').replace('X', '.')),
                        'Nn': tr(format_utm.format(pnts_UTM[k+1][0].y()), format_utm.format(pnts_UTM[k+1][0].y()).replace(',', 'X').replace('.', ',').replace('X', '.')),
                        'hn': tr(format_h.format(pnts_UTM[k+1][0].z()), format_h.format(pnts_UTM[k+1][0].z()).replace(',', 'X').replace('.', ',').replace('X', '.')),
                        'lonn': lonn,
                        'latn': latn,
                        'Ln': '-' if TipoGeometria == 1 and k+1 == tam else pnts_UTM[k+1][2] + '/' + pnts_UTM[1 if k+2 > tam else k+2][2],
                        'Az_n': '-' if TipoGeometria == 1 and k+1 == tam else tr(DD2DMS(Az_lista[k],prec_Azimute), DD2DMS(Az_lista[k],prec_Azimute).replace('.', ',')),
                        'Dn': '-' if TipoGeometria == 1 and k+1 == tam else tr(format_dist.format(Dist[k]), format_dist.format(Dist[k]).replace(',', 'X').replace('.', ',').replace('X', '.'))
                        }
            for item in itens:
                linha0 = linha0.replace(item, itens[item])
            LINHAS += linha0
        resultado = texto.replace('[CABECALHO]', cabec).replace('[LINHAS]', LINHAS).replace('[TITULO]', str2HTML(titulo.upper())).replace('[FONTSIZE]', str(fontsize))
        return resultado

    else:
        return tr('Check if the geometry is null or invalid! Or if Atlas is on!', 'Verifique se a geometria é nula ou inválida! Ou se o Atlas está ligado!')



@qgsfunction(args='auto', group='LF Tools')
def deedtext(description, estilo, prefix, decimal, calculation, fontsize, feature, parent, context):
    """
    Generates a description of a property with coordinates as text.
    <p>Note 1: A layer or QGIS Project with a projected SRC is required.</p>
    <p>Note 2: Coordinates styles: 'E,N' (default), 'N,E', 'E,N,h', 'N,E,h', 'lat,lon', 'lon,lat', 'lat,lon,h'  or 'lon,lat,h'.</p>
    <p>Note 3: Combine the text 'suffix' for geographic coordinates with suffix.</p>
    <p>Note 4: The value of "precision" can be an integer that will be applied to coordinate and distance, or an array with 3 numbers for the precision of the coordinates, azimuth and distances, respectively.</p>

    <h2>Exemples:</h2>
    <ul>
      <li>deedtext('initial description', 'style', 'preffix', precision, calculation, fontsize) = HTML</li>
      <li>deedtext('northernmost point', 'E,N,h', 'V-', 2, 1, 12) = HTML</li>
      <li>deedtext('rightmost point in front of the property', 'N,E', 'P-', 3, 1, 10) = HTML</li>

    </ul>
    <h2>Exemple with adjointer layer:</h2>
    <ul>
      <li>deedtext('adjoiner_line_layer,id,name', 'style', 'preffix', precision, calculation, fontsize) = HTML</li>
      <li>deedtext('Adjoiners,ID1,name', 'E,N', 'P-', 2, 1, 10) = HTML</li>
    </ul>
    <h2>Exemple with vertex layer:</h2>
    <ul>
      <li>deedtext('initial description', 'style', 'vertex_point_layer,ID,name', precision, calculation, fontsize) = HTML</li>
      <li>deedtext('northernmost point', 'E,N', 'Vertex,id,name', 2, 1, 10) = HTML</li>
    </ul>
    <h2>Exemple with different precisions:</h2>
    <ul>
      <li>deedtext('initial description', 'style', 'preffix', array(coord,azimuth,distance), calc, fontsize) = HTML</li>
      <li>deedtext('northernmost point', 'lat,lon,h', 'P-', array(3,-1,2), 3, 10) = HTML</li>
    </ul>

    <h2>Choose the method for calculating azimuths and distances:</h2>
    <ul>
      <li>calculation = 1 ➡️ Layer or projection CRS</li>
      <li>calculation = 2 ➡️ Local Tangent Plane (LTP)</li>
      <li>calculation = 3 ➡️ LTP distance and Puissant azimuth</li>
    </ul>
    """
    layer_id = context.variable('layer_id')
    layer = QgsProject.instance().mapLayer(layer_id)
    SRC = layer.crs()
    SGR = QgsCoordinateReferenceSystem(SRC.geographicCrsAuthId())

    if isinstance(decimal, list):
        if not isinstance(decimal[0], int):
            prec_h = round(10*float(decimal[0] - np.floor(decimal[0])))
            decimal[0] = int(decimal[0])
        else:
            prec_h = decimal[0]
        format_utm = '{:,.Xf}'.replace('X', str(decimal[0]))
        format_h = '{:,.Xf}'.replace('X', str(prec_h))
        prec_geo = decimal[0]
        prec_Azimute = decimal[1]
        format_dist = '{:,.Xf}'.replace('X', str(decimal[2]))
    else:
        if not isinstance(decimal, int):
            prec_h = round(10*float(decimal - np.floor(decimal)))
            decimal = int(decimal)
        else:
            prec_h = decimal
        format_utm = '{:,.Xf}'.replace('X', str(decimal))
        format_h = '{:,.Xf}'.replace('X', str(prec_h))
        prec_geo = decimal + 2
        prec_Azimute = 1
        format_dist = '{:,.Xf}'.replace('X', str(decimal))


    geom = feature.geometry()
    TipoGeometria = geom.type()

    estilo = estilo.replace(' ', '').lower()

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
            tol = 0.01 # tolerancia 1 cm

            for k, coord in enumerate(coords[:-1] if TipoGeometria == 2 else coords):
                pnt = coordinateTransformer.transform(QgsPointXY(coord.x(), coord.y()))
                if 'prefixo' in locals():
                    pnts_UTM[k+1] = [coord, prefixo, prefixo + '{:02}'.format(k+1)]
                    pnts_GEO[k+1] = [QgsPoint(pnt.x(),pnt.y(),coord.z()), prefixo, prefixo + '{:02}'.format(k+1) ]
                else:
                    for feat in layer.getFeatures(QgsFeatureRequest(exp)):
                        # Identificar ponto correspondente
                        pnt_corresp = feat.geometry().asPoint()
                        if abs(coord.x() - pnt_corresp.x()) < tol and abs(coord.y() - pnt_corresp.y()) < tol:
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
            tol = 0.01/111000 # tolerancia 1 cm em graus

            for k, coord in enumerate(coords[:-1] if TipoGeometria == 2 else coords):
                pnt = coordinateTransformer.transform(QgsPointXY(coord.x(), coord.y()))
                if 'prefixo' in locals():
                    pnts_GEO[k+1] = [coord, prefixo, prefixo + '{:02}'.format(k+1)]
                    pnts_UTM[k+1] = [QgsPoint(pnt.x(),pnt.y(),coord.z()), prefixo, prefixo + '{:02}'.format(k+1) ]
                else:
                    for feat in layer.getFeatures(QgsFeatureRequest(exp)):
                        # Identificar ponto correspondente
                        pnt_corresp = feat.geometry().asPoint()
                        if abs(coord.x() - pnt_corresp.x()) < tol and abs(coord.y() - pnt_corresp.y()) < tol:
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

        # Calcular geomGeo e crsGeo
        if not layer.crs().isGeographic():
            geom.transform(coordinateTransformer)
        crsGeo = SGR
        geomGeo = geom
        centroideG = geom.centroid().asPoint()

        if TipoGeometria == 2: # Polígono

            if calculation == 1: # Projetadas (Ex: UTM)
                for k in range(tam):
                    pntA = pnts_UTM[k+1][0]
                    pntB = pnts_UTM[1 if k+2 > tam else k+2][0]
                    Az_lista += [(180/pi)*azimute(pntA, pntB)[0]]
                    Dist += [sqrt((pntA.x() - pntB.x())**2 + (pntA.y() - pntB.y())**2)]
            elif calculation == 2: # SGL
                for k in range(tam):
                    pntA = pnts_GEO[k+1][0]
                    pntB = pnts_GEO[1 if k+2 > tam else k+2][0]
                    Az, dist = AzimuteDistanciaSGL(pntA, pntB, geomGeo, crsGeo, 'SGL')
                    Az_lista += [Az]
                    Dist += [dist]
            elif calculation == 3: # SGL e Puissant
                for k in range(tam):
                    pntA = pnts_GEO[k+1][0]
                    pntB = pnts_GEO[1 if k+2 > tam else k+2][0]
                    Az, dist = AzimuteDistanciaSGL(pntA, pntB, geomGeo, crsGeo, 'puissant')
                    Az_lista += [Az]
                    Dist += [dist]


        else: # Linha

            if calculation == 1: # Projetadas (Ex: UTM)
                for k in range(tam-1):
                    pntA = pnts_UTM[k+1][0]
                    pntB = pnts_UTM[k+2][0]
                    Az_lista += [(180/pi)*azimute(pntA, pntB)[0]]
                    Dist += [sqrt((pntA.x() - pntB.x())**2 + (pntA.y() - pntB.y())**2)]
            elif calculation == 2: # SGL
                for k in range(tam-1):
                    pntA = pnts_GEO[k+1][0]
                    pntB = pnts_GEO[k+2][0]
                    Az, dist = AzimuteDistanciaSGL(pntA, pntB, geomGeo, crsGeo, 'SGL')
                    Az_lista += [Az]
                    Dist += [dist]
            elif calculation == 3: # SGL e Puissant
                for k in range(tam-1):
                    pntA = pnts_GEO[k+1][0]
                    pntB = pnts_GEO[k+2][0]
                    Az, dist = AzimuteDistanciaSGL(pntA, pntB, geomGeo, crsGeo, 'puissant')
                    Az_lista += [Az]
                    Dist += [dist]


        # Definindo estilo das coordendas
        estilo = estilo.replace(' ','').lower()
        if estilo == 'E,N,h'.lower():
            estilo_vertices = '<b>E [Xn]m</b>, <b>N [Yn]m</b> ' + tr('and', 'e') +  ' <b>h [hn]m</b>'
        elif estilo =='N,E,h'.lower():
            estilo_vertices = '<b>N [Yn]m</b>, <b>E [Xn]m</b> ' + tr('and', 'e') +  ' <b>h [hn]m</b>'
        elif estilo =='E,N'.lower():
            estilo_vertices = '<b>E [Xn]    m</b> ' + tr('and', 'e') +  ' <b>N [Yn]m</b>'
        elif estilo =='N,E'.lower():
            estilo_vertices = '<b>N [Yn]m</b> ' + tr('and', 'e') +  ' <b>E [Xn]m</b>'
        elif 'lon,lat,h' in estilo:
            estilo_vertices = '<b> [Xn]</b>,  <b> [Yn]</b> ' + tr('and', 'e') + ' <b>h [hn]m</b>'
        elif 'lon,lat' in estilo:
            estilo_vertices = '<b> [Xn]</b> ' + tr('and', 'e') +  ' <b> [Yn]</b>'
        elif 'lat,lon,h' in estilo:
            estilo_vertices = '<b> [Yn]</b>,  <b> [Xn]</b> ' + tr('and', 'e') + ' <b>h [hn]m</b>'
        elif 'lat,lon' in estilo:
            estilo_vertices = '<b> [Yn]</b> ' + tr('and', 'e') +  ' <b> [Xn]</b>'
        else: # default
            estilo_vertices = '<b>E [Xn]m</b> ' + tr('and', 'e') +  ' <b>N [Yn]m</b>'

        def CoordenadaN (PtsUTM, PtsGEO, estilo, decimal):
            if 'e' in estilo: # coordenadas projetadas
                Xn = tr(format_utm.format(PtsUTM[0].x()), format_utm.format(PtsUTM[0].x()).replace(',', 'X').replace('.', ',').replace('X', '.'))
                Yn = tr(format_utm.format(PtsUTM[0].y()), format_utm.format(PtsUTM[0].y()).replace(',', 'X').replace('.', ',').replace('X', '.'))
            else: # coordenadas geodesicas
                if 'suffix' in estilo:
                    Xn = str2HTML(tr(DD2DMS(PtsGEO[0].x(),prec_geo), DD2DMS(PtsGEO[0].x(),prec_geo).replace('.', ','))).replace('-','') + str('W' if PtsGEO[0].x() < 0 else 'E')
                    Yn = str2HTML(tr(DD2DMS(PtsGEO[0].y(),prec_geo), DD2DMS(PtsGEO[0].y(),prec_geo).replace('.', ','))).replace('-','') + str('S' if PtsGEO[0].y() < 0 else 'N')
                else:
                    Xn = str2HTML(tr(DD2DMS(PtsGEO[0].x(),prec_geo), DD2DMS(PtsGEO[0].x(),prec_geo).replace('.', ',')))
                    Yn = str2HTML(tr(DD2DMS(PtsGEO[0].y(),prec_geo), DD2DMS(PtsGEO[0].y(),prec_geo).replace('.', ',')))
            return (Xn, Yn)

        # Texto do cálculo, no final do memorial
        if 'e' in estilo and calculation == 1: # Coordenadas UTM e cálculo em UTM
            texto_calculo = tr(', and are projected in the UTM system, zone [FUSO] and hemisphere [HEMISFERIO], from which all azimuths and distances were calculated.',
                                    ', sendo projetadas no Sistema UTM, fuso [FUSO] e hemisfério [HEMISFERIO], a partir das quais todos os azimutes e distâncias foram calculados.')
        elif 'e' in estilo and calculation == 2: # Coordenadas UTM e cálculo em SGL:
            texto_calculo = tr(', and are projected in the UTM system, zone [FUSO] and hemisphere [HEMISFERIO]. All azimuths and distances were calculated in the Local Tangent Plane (LTP), having as origin the centroid and average altitude of the perimeter.',
                                    ', sendo projetadas no Sistema UTM, fuso [FUSO] e hemisfério [HEMISFERIO]. Todos os azimutes e distâncias foram calculados no Sistema Geodésico Local (SGL) com origem no centroide e altitude média do perímetro.')
        elif 'lat' in estilo and calculation == 1: # Coordenadas Geo e cálculo em UTM:
            texto_calculo = tr('. All azimuths and distances were calculated from the projected coordinates in UTM, zone [FUSO] and hemisphere [HEMISPHERE].',
                                    '. Todos os azimutes e distâncias foram calculados a partir das coordenadas projetadas no sistema UTM, fuso [FUSO] e hemisfério [HEMISFERIO].')
        elif 'lat' in estilo and calculation == 2: # Coordenadas Geo e cálculo em SGL:
            texto_calculo = tr('. All azimuths and distances were calculated in the Local Tangent Plane (LTP), having as origin the centroid and average altitude of the perimeter.',
                                    '. Todos os azimutes e distâncias foram calculados no Sistema Geodésico Local (SGL) com origem no centroide e altitude média do perímetro.')
        elif 'e' in estilo and calculation == 3: # Coordenadas UTM, cálculo em SGL e Azimute Puissant:
            texto_calculo = tr(', and are projected in the UTM system, zone [FUSO] and hemisphere [HEMISFERIO]. The azimuths were calculated using the Inverse Geodetic Problem formula according to Puissant, and the distances were calculated in the Local Tangent Plane (LTP) having as origin the centroid and average altitude of the perimeter.',
                                    ', sendo projetadas no Sistema UTM, fuso [FUSO] e hemisfério [HEMISFERIO]. Os azimutes foram determinados pela fórmula do Problema Geodésico Inverso segundo Puissant, e as distâncias foram calculados no Sistema Geodésico Local (SGL) com origem no centroide e altitude média do perímetro.')
        elif 'lat' in estilo and calculation == 3: # Coordenadas Geo, cálculo em SGL e Azimute Puissant:
            texto_calculo = tr('. The azimuths were calculated using the Inverse Geodetic Problem formula according to Puissant, and the distances were calculated in the Local Tangent Plane (LTP) having as origin the centroid and average altitude of the perimeter.',
                                    '. Os azimutes foram determinados pela fórmula do Problema Geodésico Inverso segundo Puissant, e as distâncias foram calculadas no Sistema Geodésico Local (SGL) com origem no centroide e altitude média do perímetro.')
        # texto final do memorial
        if TipoGeometria == 2:
            text_fim = tr('''the starting point for the description of this perimeter.
            All coordinates described here are georeferenced to the Geodetic Reference System (GRS) <b>[SGR]</b>''' + texto_calculo,
            '''ponto inicial da descrição deste perímetro.
            Todas as coordenadas aqui descritas estão georreferenciadas ao Sistema Geodésico de Referência (SGR) <b>[SGR]</b>''' + texto_calculo)
        else:
            text_fim = tr('''the last point of this perimeter.
            All coordinates described here are georeferenced to the Geodetic Reference System (GRS) <b>[SGR]</b>''' + texto_calculo,
            '''último ponto deste perímetro.
            Todas as coordenadas aqui descritas estão georreferenciadas ao Sistema Geodésico de Referência (SGR) <b>[SGR]</b>''' + texto_calculo)

        try:  # >>>>>>>>>>>>>>>>> Pegar nome do confrontante
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
            text_ini = tr('<p style="text-align: justify; font-size: [FONTSIZE]px; ">The description of this perimeter begins at the vertex <b>[Vn]</b>, with coordinates [XXX], [descr_pnt_ini] from this, with the following azimuths and distances: ',
                          '<p style="text-align: justify; font-size: [FONTSIZE]px; ">Inicia-se a descrição deste perímetro no vértice <b>[Vn]</b>, de coordenadas [XXX], [descr_pnt_ini] deste, segue com os seguintes azimutes e distâncias: ').replace('[XXX]', estilo_vertices)

            text_meio = tr('[Azn] and [Dn]m up to the vertex <b>[Vn]</b>, with coordinates [XXX], ',
                           '[Azn] e [Dn]m até o vértice <b>[Vn]</b>, de coordenadas [XXX], ').replace('[XXX]', estilo_vertices)

            # Texto inicial
            itens = {'[Vn]': pnts_UTM[1][2],
                     '[Xn]': CoordenadaN (pnts_UTM[1], pnts_GEO[1], estilo, decimal)[0],
                     '[Yn]': CoordenadaN (pnts_UTM[1], pnts_GEO[1], estilo, decimal)[1],
                     '[descr_pnt_ini]': descr_pnt_ini + ', ' if descr_pnt_ini else ''
                        }
            if 'h' in estilo:
                itens['[hn]'] = tr(format_h.format(pnts_UTM[1][0].z()), format_h.format(pnts_UTM[1][0].z()).replace(',', 'X').replace('.', ',').replace('X', '.'))
            for item in itens:
                text_ini = text_ini.replace(item, itens[item]).replace('[FONTSIZE]', str(fontsize))

            # Texto do meio
            LINHAS = ''
            if TipoGeometria == 2:
                for k in range(tam):
                    linha0 = text_meio
                    indice = k+2 if k+2 <= tam else 1
                    itens = {'[Vn]': pnts_UTM[indice][2],
                             '[Xn]': CoordenadaN (pnts_UTM[indice], pnts_GEO[indice], estilo, decimal)[0],
                             '[Yn]': CoordenadaN (pnts_UTM[indice], pnts_GEO[indice], estilo, decimal)[1],
                             '[Azn]': tr(DD2DMS(Az_lista[k],prec_Azimute), DD2DMS(Az_lista[k],prec_Azimute).replace('.', ',')),
                             '[Dn]': tr(format_dist.format(Dist[k]), format_dist.format(Dist[k]).replace(',', 'X').replace('.', ',').replace('X', '.'))
                                }
                    if 'h' in estilo:
                        itens['[hn]'] = tr(format_h.format(pnts_UTM[indice][0].z()),
                                           format_h.format(pnts_UTM[indice][0].z()).replace(',', 'X').replace('.', ',').replace('X', '.'))
                    for item in itens:
                        linha0 = linha0.replace(item, itens[item])
                    LINHAS += linha0

            else: # Linha
                for k in range(tam-1):
                    linha0 = text_meio
                    indice = k+2
                    itens = {'[Vn]': pnts_UTM[indice][2],
                             '[Xn]': CoordenadaN (pnts_UTM[indice], pnts_GEO[indice], estilo, decimal)[0],
                             '[Yn]': CoordenadaN (pnts_UTM[indice], pnts_GEO[indice], estilo, decimal)[1],
                             '[Azn]': tr(DD2DMS(Az_lista[k],prec_Azimute), DD2DMS(Az_lista[k],prec_Azimute).replace('.', ',')),
                             '[Dn]': tr(format_dist.format(Dist[k]), format_dist.format(Dist[k]).replace(',', 'X').replace('.', ',').replace('X', '.'))
                                }
                    if 'h' in estilo:
                        itens['[hn]'] = tr(format_h.format(pnts_UTM[indice][0].z()),
                                           format_h.format(pnts_UTM[indice][0].z()).replace(',', 'X').replace('.', ',').replace('X', '.'))
                    for item in itens:
                        linha0 = linha0.replace(item, itens[item])
                    LINHAS += linha0

            # Texto final
            itens = {'[SGR]': SGR.description(),
                     '[FUSO]': str(FusoHemisf(centroideG)[0]),
                     '[HEMISFERIO]': FusoHemisf(centroideG)[1]
                        }
            for item in itens:
                text_fim = text_fim.replace(item, itens[item])

            FINAL = text_ini + LINHAS + text_fim
            return FINAL

        except: # >>>>>>>>>>>>>>>>> puxar nome dos confrontantes

            # conteudo do memorial
            text_ini = tr('<p style="text-align: justify; font-size: [FONTSIZE]px; ">The description of this perimeter begins at the vertex <b>[Vn]</b>, with coordinates [XXX], ',
                          '<p style="text-align: justify; font-size: [FONTSIZE]px; ">Inicia-se a descrição deste perímetro no vértice <b>[Vn]</b>, de coordenadas [XXX], ').replace('[XXX]', estilo_vertices)

            text_meio1 = tr('from this, it continues adjoining with [ADJOINER], with the following flat azimuths and distances: [Azn] and [Dn]m up to the vertex <b>[Vn]</b>, with coordinates [XXX], ',
                            'deste, segue confrontando com [ADJOINER], com os seguintes azimutes planos e distâncias: [Azn] e [Dn]m até o vértice <b>[Vn]</b>, de coordenadas [XXX], ').replace('[XXX]', estilo_vertices)

            text_meio2 = tr('[Azn] and [Dn]m up to the vertex <b>[Vn]</b>, with coordinates [XXX], ',
                            '[Azn] e [Dn]m até o vértice <b>[Vn]</b>, de coordenadas [XXX], ').replace('[XXX]', estilo_vertices)


            # Texto inicial
            itens = {'[Vn]': pnts_UTM[1][2],
                     '[Xn]': CoordenadaN (pnts_UTM[1], pnts_GEO[1], estilo, decimal)[0],
                     '[Yn]': CoordenadaN (pnts_UTM[1], pnts_GEO[1], estilo, decimal)[1]
                        }
            if 'h' in estilo:
                itens['[hn]'] = tr(format_h.format(pnts_UTM[1][0].z()), format_h.format(pnts_UTM[1][0].z()).replace(',', 'X').replace('.', ',').replace('X', '.'))
            for item in itens:
                text_ini = text_ini.replace(item, itens[item]).replace('[FONTSIZE]', str(fontsize))

            # Texto do meio
            LINHAS = ''
            Confrontante = ''
            confr_list = [Confrontante]

            for k in range(tam):
                indice = k+2 if k+2 <= tam else 1
                ponto = QgsPointXY(pnts_GEO[indice][0])
                for feat in layer.getFeatures(QgsFeatureRequest(exp)):
                    # Identificar linha de confrontação
                    geom_lin = feat.geometry()
                    if geom.intersects(geom_lin):
                        inter = geom.intersection(geom_lin)
                        if inter.type() == 1: # linha
                            inter = Mesclar_Multilinhas(inter)
                            lin_coords = inter.asPolyline()
                            if ponto in lin_coords[1:]:
                                if feat[nome] != Confrontante:
                                    Confrontante = feat[nome]
                                break

                # Verificar se houve mudança de confrontante
                if Confrontante != confr_list[-1]:
                    linha0 = text_meio1
                else:
                    linha0 = text_meio2
                confr_list += [Confrontante]

                itens = {'[Vn]': pnts_UTM[indice][2],
                         '[Xn]': CoordenadaN (pnts_UTM[indice], pnts_GEO[indice], estilo, decimal)[0],
                         '[Yn]': CoordenadaN (pnts_UTM[indice], pnts_GEO[indice], estilo, decimal)[1],
                         '[Azn]': tr(DD2DMS(Az_lista[k],prec_Azimute), DD2DMS(Az_lista[k],prec_Azimute).replace('.', ',')),
                         '[Dn]': tr(format_dist.format(Dist[k]), format_dist.format(Dist[k]).replace(',', 'X').replace('.', ',').replace('X', '.')),
                         '[ADJOINER]': Confrontante,
                            }
                if 'h' in estilo:
                    itens['[hn]'] = tr(format_h.format(pnts_UTM[indice][0].z()),
                                       format_h.format(pnts_UTM[indice][0].z()).replace(',', 'X').replace('.', ',').replace('X', '.'))

                for item in itens:
                    try:
                        linha0 = linha0.replace(item, itens[item])
                    except:
                        return(tr('Invalid adjoiner line in [X] and [Y] coordinates! Perform layers topological validation!',
                                  'Linha de confrontante inválida nas coordenadas [X] e [Y]! Execute a validação topológica das camadas!').replace('[X]',itens['[Xn]']).replace('[Y]',itens['[Yn]']))
                LINHAS += linha0

            # Texto final
            itens = {'[SGR]': SGR.description(),
                     '[FUSO]': str(FusoHemisf(centroideG)[0]),
                     '[HEMISFERIO]': FusoHemisf(centroideG)[1]
                        }
            for item in itens:
                text_fim = text_fim.replace(item, itens[item])

            FINAL = text_ini + LINHAS + text_fim
            return FINAL
    else:
        return tr('Check if the geometry is null or invalid! Or if Atlas is on!', 'Verifique se a geometria é nula ou inválida! Ou se o Atlas está ligado!')




@qgsfunction(args='auto', group='LF Tools')
def geoneighbors(prefix, testada, borderer_field, coord_type, precision, fontsize, feature, parent, context):
    """
    This function automatically generates a table listing the vertex codes, their coordinates, the distances between each perimeter segment, and the linear and pointwise boundary neighbors, based on a polygon layer representing land lots or parcels.
    <h3>Parameters:</h3>
    <ul>
      <li><b>preffix</b> – A letter or code to preffix the vertex numbering. This can also be a reference to a field or layer.</li>
      <li><b>front_lot_name</b> – Front lot name or a reference to a layer containing front lot lines.</li>
      <li><b>borderer_field</b> – Field name containing the textual description of the neighboring boundary (to be included in the generated table).</li>
      <li><b>precision</b> – Either a single number (e.g., 2) defining the number of decimal places for coordinates and distances, or a list of two values: array(4,2).</li>
      <li><b>coord_type</b> – Coordinate type: 'geo' for geographic (latitude/longitude) or 'proj' for projected coordinates.</li>
      <li><b>fontsize</b> – Font size used in the output table.</li>
    </ul>
    <p><b>Note:</b> This function requires the project or layer to use a projected Coordinate Reference System (CRS).</p>

    <h2>Examples:</h2>
    <ul>
      <li>geoneighbors('preffix', 'front_lot_field', 'borderer_name_field', coord_type, precision, fontsize) = HTML</li>
      <li>geoneighbors('V-', "road" , 'parcel_code', 'geo', 2, 12) = HTML</li>
    </ul>
    <h2>Exemples with vertex layer:</h2>
    <ul>
      <li>geoneighbors('vertex_point_layer,ID,name', 'front_lot_name', 'borderer_name_field', coord_type, precision, fontsize) = HTML</li>
      <li>geoneighbors('Vertex,id,name', "street" , 'parcel', 'proj', 2, 10) = HTML</li>
    </ul>
    <h2>Exemples with a line Front Lot layer:</h2>
    <ul>
      <li>geoneighbors('preffix', 'front_line_layer,id,name', 'borderer_name_field', coord_type, precision, fontsize) = HTML</li>
      <li>geoneighbors('V-', 'FrontLot,featID,name' , 'parcel_code', 'geo', array(3,2), 12) = HTML</li>
    </ul>
    """

    layer_id = context.variable('layer_id')
    layer = QgsProject.instance().mapLayer(layer_id)
    SRC = layer.crs()
    SGR = QgsCoordinateReferenceSystem(SRC.geographicCrsAuthId())

    if isinstance(precision, list):
        format_coord = '{:,.Xf}'.replace('X', str(precision[0]))
        format_dist = '{:,.Xf}'.replace('X', str(precision[1]))
        decimal_geo = precision[0]
    elif isinstance(precision, int):
        format_coord = '{:,.Xf}'.replace('X', str(precision))
        format_dist = '{:,.Xf}'.replace('X', str(precision))
        decimal_geo = precision + 2
    else:
        return tr('Invalid precision!')

    coord_type = coord_type.lower()

    geom = feature.geometry()
    if geom.type() == 2 and geom:
        # Pegar vizinhos
        feat1 = feature
        geom1 = feat1.geometry()
        index = QgsSpatialIndex(layer.getFeatures())
        bbox1 = geom1.boundingBox()
        feat_ids = index.intersects(bbox1)
        confront = {}
        for feat2 in layer.getFeatures(QgsFeatureRequest(feat_ids)):
            geom2 = feat2.geometry()
            cd_lote2 = str(feat2[borderer_field])
            if feat1 != feat2:
                if geom1.intersects(geom2):
                    inters = geom1.intersection(geom2)
                    inters = Mesclar_Multilinhas(inters)
                    confront[feat2.id()] = [cd_lote2, inters]

        if geom1.isMultipart():
            coords = geom1.asMultiPolygon()[0][0]
        else:
            coords = geom1.asPolygon()[0]

        # Testada
        try:
            descricao, id, nome = testada.replace(' ', '').split(',') #nome da camada, ID, atributo
            if len(QgsProject.instance().mapLayersByName(descricao)) == 1:
                layer = QgsProject.instance().mapLayersByName(descricao)[0]
            campos = [field.name() for field in layer.fields()]
            # Camadas de polígono e confrontantes deve estar com o mesmo SRC
            filter = '"{}" = {}'.format(id, feature.id())
            exp = QgsExpression(filter)
            if id not in campos or nome not in campos:
                frontLot = str(testada)
        except:
            frontLot = str(testada)

        vizinhos = []
        for pnt in coords[:-1]:
            geom1 = QgsGeometry.fromPointXY(pnt)
            vante = ''
            compl = ''
            for item in confront:
                geom2 = confront[item][1]
                if geom2.type() == 1 and geom1.intersects(geom2): #Line
                    coord_lin = geom2.asPolyline()
                    if pnt != coord_lin[-1]:
                        vante = confront[item][0]
                elif geom2.type() == 0 and geom1.intersects(geom2): #Point
                    compl = confront[item][0]
            # Se não foi encontrado vante, buscar na camada de testada
            if not vante:
                if 'frontLot' in locals():
                    vante = frontLot
                else:
                    for feat in layer.getFeatures(QgsFeatureRequest(exp)):
                        geom2 = feat.geometry()
                        coords = geom2.asPolyline()
                        if geom1.intersects(geom2) and pnt != coords[-1]:
                            vante = feat[nome]
                            break
                    else:
                        vante = testada
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
            tol = 0.01 # tolerancia 1 cm

            for k, coord in enumerate(coords[:-1]):
                pnt = coordinateTransformer.transform(QgsPointXY(coord.x(), coord.y()))
                if 'prefixo' in locals():
                    pnts_UTM[k+1] = [coord, prefixo, prefixo + '{:02}'.format(k+1)]
                    pnts_GEO[k+1] = [QgsPoint(pnt.x(),pnt.y(),coord.z()), prefixo, prefixo + '{:02}'.format(k+1) ]
                else:
                    for feat in layer.getFeatures(QgsFeatureRequest(exp)):
                        # Identificar ponto correspondente
                        pnt_corresp = feat.geometry().asPoint()
                        if abs(coord.x() - pnt_corresp.x()) < tol and abs(coord.y() - pnt_corresp.y()) < tol:
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
            tol = 0.01/111000 # tolerancia 1 cm em graus

            for k, coord in enumerate(coords[:-1]):
                pnt = coordinateTransformer.transform(QgsPointXY(coord.x(), coord.y()))
                if 'prefixo' in locals():
                    pnts_GEO[k+1] = [coord, prefixo, prefixo + '{:02}'.format(k+1)]
                    pnts_UTM[k+1] = [QgsPoint(pnt.x(),pnt.y(),coord.z()), prefixo, prefixo + '{:02}'.format(k+1) ]
                else:
                    for feat in layer.getFeatures(QgsFeatureRequest(exp)):
                        # Identificar ponto correspondente
                        pnt_corresp = feat.geometry().asPoint()
                        if abs(coord.x() - pnt_corresp.x()) < tol and abs(coord.y() - pnt_corresp.y()) < tol:
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
 style="border: medium none ; width: 100%; font-size: [FONTSIZE]px; border-collapse: collapse;"
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
 align="center"><b>[Y_COORD]<o:p></o:p></b></p>
      </td>
      <td
 style="border-style: solid solid solid none; border-color: windowtext windowtext windowtext -moz-use-text-color; border-width: 1pt 1pt 1pt medium; padding: 0cm 5.4pt; width: 13.06%;"
 width="13%">
      <p class="MsoNormal"
 style="margin-bottom: 0cm; text-align: center; line-height: normal;"
 align="center"><b>[X_COORD]<o:p></o:p></b></p>
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
        for k in range(tam):
            linha0 = linha
            Este = tr(format_coord.format(pnts_UTM[k+1][0].x()), format_coord.format(pnts_UTM[k+1][0].x()).replace(',', 'X').replace('.', ',').replace('X', '.')),
            Norte = tr(format_coord.format(pnts_UTM[k+1][0].y()), format_coord.format(pnts_UTM[k+1][0].y()).replace(',', 'X').replace('.', ',').replace('X', '.')),
            LAT = tr(DD2DMS(pnts_GEO[k+1][0].y(), decimal_geo), DD2DMS(pnts_GEO[k+1][0].y(), decimal_geo).replace('.', ','))
            LON = tr(DD2DMS(pnts_GEO[k+1][0].x(), decimal_geo), DD2DMS(pnts_GEO[k+1][0].x(), decimal_geo).replace('.', ','))
            LAT = str(LAT + 'N') if LAT[0] != '-' else str(LAT[1:] + 'S')
            LON = str(LON + 'E') if LON[0] != '-' else str(LON[1:] + 'W')

            itens = {'[Vn]': pnts_UTM[k+1][2],
                     '[LON]': LON if coord_type == 'geo' else Este[0],
                     '[LAT]': LAT if coord_type == 'geo' else Norte[0],
                     '[confr]': vizinhos[k][0],
                     '[dist]': tr(format_dist.format(Dist[k]), format_dist.format(Dist[k]).replace(',', 'X').replace('.', ',').replace('X', '.')),
                     '[comp]': tr('Punctual neighbor with ' + vizinhos[k][1], 'Confrontação pontual com ' + vizinhos[k][1]) if vizinhos[k][1] else '-',
                        }
            for item in itens:
                linha0 = linha0.replace(item, itens[item])
            LINHAS += linha0

        # Resultado final
        return texto.replace('[LINHAS]', LINHAS).replace('[FONTSIZE]', str(fontsize)).replace('[X_COORD]', 'Longitude' if coord_type == 'geo' else 'Este (m)').replace('[Y_COORD]', 'Latitude' if coord_type == 'geo' else tr('North', 'Norte') + '(m)')

    else:
        return tr('Check if the geometry is null or invalid! Or if Atlas is on!', 'Verifique se a geometria é nula ou inválida! Ou se o Atlas está ligado!')


@qgsfunction(args='auto', group='LF Tools')
def layer_schema(layer_name, not_rela, feature, parent):
    """
    Generates a conceptual model of the given layer, documenting its geometry type and attributes. The output is formatted as an HTML table for better visualization.<br>
    <h2>Example usage:</h2>
    <ul>
      <li>layer_schema(layer_name, not_related_attributes) -> HTML Table</li>
      <li>layer_schema('vegetation', array('id', 'area')) -> HTML</li>
    </ul>
    """

    if len(QgsProject.instance().mapLayersByName(layer_name)) == 1:
        layer = QgsProject.instance().mapLayersByName(layer_name)[0]
    else:
        layer = QgsProject.instance().mapLayer(layer_name)
    nao_rela = list(not_rela)

    # ler nome da classe
    nome = str2HTML(layer.name())
    # ler nome e tipo dos atributos
    header = layer.fields()
    campos = [field.name() for field in header]

    if layer.type() == 0:
        geomTipo = layer.geometryType()
        if geomTipo == 0:
            tipo = 'ponto'
        elif geomTipo == 1:
            tipo = 'linha'
        elif geomTipo == 2:
            tipo = 'area'
        else:
            tipo = 'nogeom'

    if tipo == 'nogeom':
        lista = ''
    else:
        try:
            lista = '+geom: ' + QgsWkbTypes.displayString(layer.wkbType()) + '<br>'
        except:
            lista = ''

    for field in header:
        if field.name() not in nao_rela:
            lista += '+' + str2HTML(field.name()) + ': ' + field.typeName() +'<br>'

    figuras = geom_icons

    html = '''<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
<html>
<head>
  <meta content="text/html; charset=ISO-8859-1"
 http-equiv="content-type">
  <title>classe</title>
</head>
<body>
<table class="MsoTableGrid"
 style="border: medium none ; background: rgb(251, 254, 187) none repeat scroll 0% 50%; -moz-background-clip: initial; -moz-background-origin: initial; -moz-background-inline-policy: initial; border-collapse: collapse; text-align: left; margin-left: auto; margin-right: auto; font-family: Arial;"
 border="1" cellpadding="0" cellspacing="0">
  <tbody>
    <tr style="">
      <td
 style="border: 1.5pt solid rgb(128, 96, 0); padding: 0cm 5.4pt;">
      <p class="MsoNormal"
 style="margin-bottom: 0cm; text-align: center; line-height: normal;"
 align="center"><span style="">
 <img style="width: 22px; height: 22px;" alt="geometry" src="data:image/jpg;base64,[FIGURA]">
 </span><o:p></o:p></p>
      </td>
      <td
 style="border: 1.5pt solid rgb(128, 96, 0); padding: 0cm 5.4pt;">
      <p class="MsoNormal"
 style="margin-bottom: 0cm; text-align: center; line-height: normal;"
 align="center"><span style="color: black;">[CLASS_NAME]</span><o:p></o:p></p>
      </td>
    </tr>
    <tr style="">
      <td colspan="2"
 style="border: 1.5pt solid rgb(128, 96, 0); padding: 0cm 5.4pt;">
[ATT]
      </td>
    </tr>
  </tbody>
</table>
</body>
</html>
'''

    html = html.replace('[CLASS_NAME]',nome).replace('[ATT]', lista).replace('[FIGURA]', figuras[tipo])
    return html
