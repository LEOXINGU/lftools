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
                                         inom2mi as INOM2MI)
from lftools.geocapt.topogeo import (dd2dms as DD2DMS,
                                     dms2dd as DMS2DD,
                                     azimute, str2HTML)
from numpy import array, pi, sqrt, median
import unicodedata
import re
# https://qgis.org/pyqgis/3.2/core/Expression/QgsExpression.html

LOC = QgsApplication.locale()[:2]
def translate(string):
    return QCoreApplication.translate('Processing', string)
def tr(*string):
    # Traduzir para o portugês: arg[0] - english (translate), arg[1] - português
    if LOC == 'pt':
        if len(string) == 2:
            return string[1]
        else:
            return translate(string[0])
    else:
        return translate(string[0])

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
    Calculates the Meridian Convergence based on a feature coordinates.
    <h2>Example usage:</h2>
    <ul>
      <li>meridianconv("lon", "lat") -> -0.3451</li>
    </ul>
    """
    SRC = QgsCoordinateReferenceSystem('EPSG:4326')
    return MeridianConvergence(lon, lat, SRC)


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
def removespetialchar (palavra, feature, parent):
    """
    Substitui caracteres especiais.
    <h2>Examplo:</h2>
    <ul>
      <li>removespetialchar('coração') -> coracao </li>
      <li>removespetialchar('gênesis') -> genesis</li>
    </ul>
    """
    # Unicode normalize transforma um caracter em seu equivalente em latin.
    nfkd = unicodedata.normalize('NFKD', palavra)
    palavraSemAcento = u"".join([c for c in nfkd if not unicodedata.combining(c)])
    # Usa expressão regular para retornar a palavra apenas com números, letras e espaço
    return re.sub('[^a-zA-Z0-9 \\\]', '', palavraSemAcento)


@qgsfunction(args='auto', group='LF Tools')
def deedtable(layer_name, ini, fim, titulo, fontsize, feature, parent):
    """
    Generates the Vertices and Sides Descriptive Table, also known as Synthetic Deed Description, based on the attributes, sequence and code, in the point layer's attribute table.
    <p>Note: The table title must be inserted as string.</p>
    <h2>Exemple:</h2>
    <ul>
      <li>deedtable('layer_name', start, end, 'title','fontsize') = HTML</li>
      <li>deedtable('Limit Point', 1, 20, 'Area X',10) = HTML</li>
    </ul>
    """
    # Templates HTML
    linha = '''<tr>
      <td>Vn</td>
      <td>En</td>
      <td>Nn</td>
      <td>Ln</td>
      <td>Az_n</td>
      <td>AzG_n</td>
      <td>Dn</td>
    </tr>
    '''
    texto = '''<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
    <html>
    <head>
      <title>''' + tr('Synthetic deed description', str2HTML('Memorial Sintético')) + '''</title>
    </head>
    <body>
    <table
    style="text-align: center; width: 100%; font-size: [FONTSIZE]px; font-family: Arial;"
    border="1" cellpadding="0" cellspacing="0">
    <tbody>
    <tr>
      <td colspan="7" rowspan="1">''' + tr('Synthetic deed description'.upper(), str2HTML('Memorial Sintético'.upper())) + '''[TITULO]</td>
    </tr>
    <tr>
      <td colspan="1" rowspan="2">''' + tr('VERTEX', str2HTML('VÉRTICE')) + '''</td>
      <td colspan="2" rowspan="1">''' + tr('COORDINATE', str2HTML('COORDENADA')) + '''</td>
      <td colspan="1" rowspan="2">''' + tr('SIDE', str2HTML('LADO')) + '''</td>
      <td colspan="2" rowspan="1">''' + tr('AZIMUTH', str2HTML('AZIMUTE')) + '''</td>
      <td colspan="1" rowspan="2">''' + tr('DISTANCE', str2HTML('DISTÂNCIA')) + '''<br>
    (m)</td>
    </tr>
    <tr>
      <td>E</td>
      <td>N</td>
      <td>''' + tr('FLAT', str2HTML('PLANO')) + '''</td>
      <td>''' + tr('TRUE', str2HTML('VERDADEIRO')) + '''</td>
    </tr>
    [LINHAS]
    </tbody>
    </table>
    <br>
    </body>
    </html>
    '''
    # Camada de Pontos
    if len(QgsProject.instance().mapLayersByName(layer_name)) == 1:
        layer = QgsProject.instance().mapLayersByName(layer_name)[0]
    else:
        layer = QgsProject.instance().mapLayer(layer_name)
    SRC = layer.crs()
    pnts_UTM = {}
    # Transformacao de Coordenadas Geograficas para Projetadas no sistema UTM
    crsDest = QgsCoordinateReferenceSystem(SRC_Projeto('EPSG'))
    coordinateTransformer = QgsCoordinateTransform()
    coordinateTransformer.setDestinationCrs(crsDest)
    coordinateTransformer.setSourceCrs(SRC)
    for feat in layer.getFeatures():
        pnt = feat.geometry().asPoint()
        pnts_UTM[feat['ordem']] = [coordinateTransformer.transform(pnt), feat['tipo'], feat['codigo'], MeridianConvergence(pnt.x(), pnt.y(), crsDest) ]
    # Calculo dos Azimutes e Distancias
    tam = len(pnts_UTM)
    Az_lista, Az_Geo_lista, Dist = [], [], []
    for k in range(tam):
        pntA = pnts_UTM[k+1][0]
        pntB = pnts_UTM[1 if k+2 > tam else k+2][0]
        Az_lista += [(180/pi)*azimute(pntA, pntB)[0]]
        MeridianConvergenceediana = pnts_UTM[k+1][3]
        Az_Geo_lista += [(180/pi)*azimute(pntA, pntB)[0]+MeridianConvergenceediana]
        Dist += [sqrt((pntA.x() - pntB.x())**2 + (pntA.y() - pntB.y())**2)]
    LINHAS = ''
    if fim == -1 or fim > tam:
        fim = tam
    for k in range(ini-1,fim):
        linha0 = linha
        itens = {'Vn': pnts_UTM[k+1][2],
                    'En': tr('{:,.2f}'.format(pnts_UTM[k+1][0].x()), '{:,.2f}'.format(pnts_UTM[k+1][0].x()).replace(',', 'X').replace('.', ',').replace('X', '.')),
                    'Nn': tr('{:,.2f}'.format(pnts_UTM[k+1][0].y()), '{:,.2f}'.format(pnts_UTM[k+1][0].y()).replace(',', 'X').replace('.', ',').replace('X', '.')),
                    'Ln': pnts_UTM[k+1][2] + '/' + pnts_UTM[1 if k+2 > tam else k+2][2],
                    'Az_n': tr(DD2DMS(Az_lista[k],1), DD2DMS(Az_lista[k],1).replace('.', ',')),
                    'AzG_n':  tr(DD2DMS(Az_Geo_lista[k],1), DD2DMS(Az_Geo_lista[k],1).replace('.', ',')),
                    'Dn': tr('{:,.2f}'.format(Dist[k]), '{:,.2f}'.format(Dist[k]).replace(',', 'X').replace('.', ',').replace('X', '.'))
                    }
        for item in itens:
            linha0 = linha0.replace(item, itens[item])
        LINHAS += linha0
    resultado = texto.replace('[LINHAS]', LINHAS).replace('[TITULO]', str2HTML(titulo.upper())).replace('[FONTSIZE]', str(fontsize))
    return resultado
