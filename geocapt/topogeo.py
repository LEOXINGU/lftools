# -*- coding: utf-8 -*-

"""
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""
__author__ = 'Leandro França'
__date__ = '2021-03-01'
__copyright__ = '(C) 2021, Leandro França'

from numpy import radians, arctan, pi, sin, cos, sqrt, degrees, array, diag, ones, zeros, floor
from numpy.linalg import norm, pinv, inv
from pyproj.crs import CRS
import datetime as dt
import numpy as np

def azimute(A,B):
    # Cálculo dos Azimutes entre dois pontos (Vetor AB origem A extremidade B)
    if ((B.x()-A.x())>=0 and (B.y()-A.y())>0): #1º quadrante
        AzAB=arctan((B.x()-A.x())/(B.y()-A.y()))
        AzBA=AzAB+pi
    elif ((B.x()-A.x())>0 and (B.y()-A.y())<0): #2º quadrante
        AzAB=pi+arctan((B.x()-A.x())/(B.y()-A.y()))
        AzBA=AzAB+pi
    elif ((B.x()-A.x())<=0 and (B.y()-A.y())<0): #3º quadrante
        AzAB=arctan((B.x()-A.x())/(B.y()-A.y()))+pi
        AzBA=AzAB-pi
    elif ((B.x()-A.x())<0 and (B.y()-A.y())>0): #4º quadrante
        AzAB=2*pi+arctan((B.x()-A.x())/(B.y()-A.y()))
        AzBA=AzAB+pi
    elif ((B.x()-A.x())>0 and (B.y()-A.y())==0): # no eixo positivo de x (90º)
        AzAB=pi/2
        AzBA=1.5*pi
    else: # ((B.x()-A.x())<0 and(B.y()-A.y())==0) # no eixo negativo de x (270º)
        AzAB=1.5*pi
        AzBA=pi/2
    # Correção dos ângulos para o intervalo de 0 a 2pi
    if AzAB<0 or AzAB>2*pi:
        if (AzAB<0):
           AzAB=AzAB+2*pi
        else:
           AzAB=AzAB-2*pi
    if AzBA<0 or AzBA>2*pi:
        if (AzBA<0):
            AzBA=AzBA+2*pi
        else:
            AzBA=AzBA-2*pi
    return (AzAB, AzBA)


def DifAz(Az_ini, Az_fim):
    # Diferença (ângulo) entre azimutes
    dAz = Az_fim - Az_ini
    if dAz < 0:
        dAz = 2*pi + Az_fim - Az_ini
    return dAz


def dd2dms(dd, n_digits):
    if dd != 0:
        graus = int(floor(abs(dd)))
        resto1 = round(abs(dd) - graus, 10)
        minutos = 60*resto1
        if n_digits >= 0:
            minutos = int(floor(minutos))
            resto2 = round(resto1*60 - minutos, 10)
            segundos = resto2*60
            if round(segundos,n_digits) == 60:
                minutos += 1
                segundos = 0
            if minutos == 60:
                graus += 1
                minutos = 0
        else:
            mindec = -1*(n_digits+1)
            if round(minutos,mindec) == 60:
                graus += 1
                minutos = 0
        if dd < 0:
            texto = '-' + str(graus) + '°'
        else:
            texto = str(graus) + '°'

        if n_digits < -1: # graus e minutos decimais
            texto = texto + ('{:0' + str(3+mindec) + '.' + str(mindec) + 'f}').format(minutos) + "'"
        elif n_digits == -1: # graus e minutos inteiros
            texto = texto + '{:02d}'.format(round(minutos)) + "'"
        else: # graus, minutos e segundos
            texto = texto + '{:02d}'.format(minutos) + "'"

        if n_digits == 0: # segundos inteiros
            texto = texto + '{:02d}'.format(round(segundos)) + '"'
        elif n_digits > 0: # segundos decimais
            texto = texto + ('{:0' + str(3+n_digits) + '.' + str(n_digits) + 'f}').format(segundos) + '"'
        return texto
    else:
        if n_digits > 0:
            return "0°00'" + ('{:0' + str(3+n_digits) + '.' + str(n_digits) + 'f}').format(0) + '"'
        elif n_digits == 0:
            return "0°00'" + '"'
        elif n_digits == -1:
            return "0°00'"
        else:
            return "0°" + ('{:0' + str(3+mindec) + '.' + str(mindec) + 'f}').format(0) + "'"


def dms2dd(txt):
    txt = txt.replace(' ','').replace("''", '"').replace('\t','').replace(',','.')
    newtxt =''
    if (txt[-1]).upper() in ('W','O','S'):
        if txt[0] != '-':
            txt = '-' + txt[:-1]
        else:
            txt = txt[:-1]
    elif (txt[-1]).upper() in ('E','L','N'):
        txt = txt[:-1]
    for letter in txt:
        if not letter.isnumeric() and letter != '.' and letter != '-':
            newtxt += '|'
        else:
            newtxt += letter
    lista = newtxt[:-1].split('|')
    if len(lista) == 3: # GMS
        if '-' in lista[0]:
            return -1*(abs(float(lista[0])) + float(lista[1])/60 + float(lista[2])/3600)
        else:
            return float(lista[0]) + float(lista[1])/60 + float(lista[2])/3600
    elif len(lista) == 2:
        if '-' in lista[0]:
            return -1*(abs(float(lista[0])) + float(lista[1])/60)
        else:
            return float(lista[0]) + float(lista[1])/60
    else:
        return None


def str2HTML(texto):
    if texto:
        dicHTML = {'Á': '&Aacute;',	'á': '&aacute;',	'Â': '&Acirc;',	'â': '&acirc;',	'À': '&Agrave;',	'à': '&agrave;',	'Å': '&Aring;',	'å': '&aring;',	'Ã': '&Atilde;',	'ã': '&atilde;',	'Ä': '&Auml;',	'ä': '&auml;', 'ú': '&uacute;', 'Ú': '&Uacute;', 'Æ': '&AElig;',	'æ': '&aelig;',	'É': '&Eacute;',	'é': '&eacute;',	'Ê': '&Ecirc;',	'ê': '&ecirc;',	'È': '&Egrave;',	'è': '&egrave;',	'Ë': '&Euml;',	'ë': '&Euml;',	'Ð': '&ETH;',	'ð': '&eth;',	'Í': '&Iacute;',	'í': '&iacute;',	'Î': '&Icirc;',	'î': '&icirc;',	'Ì': '&Igrave;',	'ì': '&igrave;',	'Ï': '&Iuml;',	'ï': '&iuml;',	'Ó': '&Oacute;',	'ó': '&oacute;',	'Ô': '&Ocirc;',	'ô': '&ocirc;',	'Ò': '&Ograve;', 'Õ': '&Otilde;', 'õ': '&otilde;',	'ò': '&ograve;',	'Ø': '&Oslash;',	'ø': '&oslash;',	'Ù': '&Ugrave;',	'ù': '&ugrave;',	'Ü': '&Uuml;',	'ü': '&uuml;',	'Ç': '&Ccedil;',	'ç': '&ccedil;',	'Ñ': '&Ntilde;',	'ñ': '&ntilde;',	'Ý': '&Yacute;',	'ý': '&yacute;',	'"': '&quot;', '”': '&quot;',	'<': '&lt;',	'>': '&gt;',	'®': '&reg;',	'©': '&copy;',	'\'': '&apos;', 'ª': '&ordf;', 'º': '&ordm;', '°':'&deg;', '²':'&sup2;', '¿':'&iquest;', '¡':'&iexcl;'}
        for item in dicHTML:
            if item in texto:
                texto = texto.replace(item, dicHTML[item])
        return texto
    else:
        return ''


def String2NumberList (txt):
    txt = txt.replace(' ', '').replace('\t','').replace('\n','')
    Splited = txt.split(',')
    lista = []
    for item in Splited:
        lista += [float(item)]
    return lista


def String2StringList(txt):
    txt = txt.replace(' ', '').replace('\t','').replace('\n','')
    Splited = txt.split(',')
    return Splited


def String2CoordList (txt):
        txt = txt.replace(' ', '').replace('\t','').replace('\n','')
        Splited = txt.split(';')
        lista = []
        for Coords in Splited:
            Splited2 = Coords.split(',')
            lista_aux = []
            for coord in Splited2:
                lista_aux += [float(coord)]
            lista += [lista_aux]
        return lista


# Conversão de coordenadas geodésicas para geocêntricas
def geod2geoc(lon, lat, h, a, f):
    lon = radians(lon)
    lat = radians(lat)
    e2 = f*(2-f) # primeira excentricidade
    N = a/sqrt(1-(e2*sin(lat)**2))
    X = (N+h)*cos(lat)*cos(lon)
    Y = (N+h)*cos(lat)*sin(lon)
    Z = (N*(1-e2)+h)*sin(lat)
    return (X,Y,Z)


# Conversão de coordenadas geocêntricas para geodésicas
def geoc2geod(X, Y, Z, a, f):
    b = a*(1-f)
    e2 = f*(2-f) # primeira excentricidade
    e2_2 = e2/(1-e2) # segunda excentricidade
    tg_u = (a/b)*Z/sqrt(X**2 + Y**2)
    sen_u = tg_u/sqrt(1+tg_u**2)
    cos_u = 1/sqrt(1+tg_u**2)
    lon = arctan(Y/X)
    lat = arctan( (Z+ e2_2 * b * sen_u**3) / (sqrt(X**2 + Y**2) - e2 * a * cos_u**3))
    N = a/sqrt(1-(e2*sin(lat)**2))
    h = sqrt(X**2 + Y**2)/cos(lat) - N
    lon = lon/pi*180
    lat = lat/pi*180
    return (lon, lat, h)


# Conversão de Coordenadas Geocêntrica para Topocêntricas
def geoc2enu(X, Y, Z, lon0, lat0, Xo, Yo, Zo):
    lon = radians(lon0)
    lat = radians(lat0)

    M = array(
    [
    [  -sin(lon),                     cos(lon),                 0 ],
    [  -sin(lat)*cos(lon),   -sin(lat)*sin(lon),          cos(lat)],
    [   cos(lat)*cos(lon),    cos(lat)*sin(lon),          sin(lat)]
    ]
    )

    T = array(
    [[X - Xo], [Y-Yo], [Z-Zo]]
    )

    Fo = array([[15e4],[25e4],[0]]) # False E and N

    R = M@T + Fo
    return (R[0,0], R[1,0], R[2,0])


# Conversão de Coordenadas Topocêntricas para Geocêntrica
def enu2geoc(E, N, U, lon0, lat0, Xo, Yo, Zo):
    lon = radians(lon0)
    lat = radians(lat0)

    Fo = array([[15e4],[25e4],[0]]) # False E and N

    M = array(
    [
    [  -sin(lon),     -sin(lat)*cos(lon),          cos(lat)*cos(lon)],
    [  cos(lon),      -sin(lat)*sin(lon),          cos(lat)*sin(lon)],
    [   0        ,              cos(lat),                       sin(lat)     ]
    ]
    )

    T = array(
    [[E], [N], [U]]
    )

    R = M@(T-Fo) + [[Xo], [Yo], [Zo]]
    return (R[0,0], R[1,0], R[2,0])


# Transformar distancia em metros para graus
def meters2degrees(dist, lat, SRC):
    EPSG = int(SRC.authid().split(':')[-1])
    proj_crs = CRS.from_epsg(EPSG)
    a=proj_crs.ellipsoid.semi_major_metre
    f=1/proj_crs.ellipsoid.inverse_flattening
    e2 = f*(2-f)
    N = a/np.sqrt(1-e2*(np.sin(lat))**2) # Raio de curvatura 1º vertical
    M = a*(1-e2)/(1-e2*(np.sin(lat))**2)**(3/2.) # Raio de curvatura meridiana
    R = np.sqrt(M*N) # Raio médio de Gauss
    theta = dist/R
    theta = np.degrees(theta) # Radianos para graus
    return theta


# Transformar de graus para metros
def degrees2meters(theta, lat, SRC):
    EPSG = int(SRC.authid().split(':')[-1])
    proj_crs = CRS.from_epsg(EPSG)
    a=proj_crs.ellipsoid.semi_major_metre
    f=1/proj_crs.ellipsoid.inverse_flattening
    e2 = f*(2-f)
    N = a/np.sqrt(1-e2*(np.sin(lat))**2) # Raio de curvatura 1º vertical
    M = a*(1-e2)/(1-e2*(np.sin(lat))**2)**(3/2.) # Raio de curvatura meridiana
    R = np.sqrt(M*N) # Raio médio de Gauss
    theta = np.radians(theta)
    dist = theta*R
    return dist

# Hora GPS
def gpsdate(Y, M, DoM, Hr, Mn, Sc):
    '''
    		Inputs:
    		  Year, Month, Day, Hour, Min, Sec

    		Returns: year, month, day of month, day of year, GPS week,
    			 day of GPS week, second of GPS week, Julian day,
    			 decimal year.
    '''
    UT = Hr + Mn/60 + Sc/3600
    if M <= 2:
        y = Y - 1
        m = M + 12
    else:
        y = Y
        m = M
    # calculation of the Julian Date
    JD = int(365.25*y) + int(30.6001*(m+1)) + DoM  + UT/24 + 1720981.5
    # Calculation of the Decimal Year
    DecY = (JD - 2451545.0)/365.25
    # Calculation of the Day of the Year
    DoY = (dt.date(Y, M, DoM) - dt.date(Y, 1, 1)).days  + 1
    # calculation of GPS week
    GPSW = int((JD - 2444244.5)/7)
    # calculation of day of the GPS Week
    DoGPSW = round(((JD - 2444244.5)/7 - GPSW)*7)
    # calculation of second of the GPS Week
    SoGPSW = round((((JD - 2444244.5)/7 - GPSW)*7)*(24*60*60))
    return [Y,M,DoM,DoY,GPSW,DoGPSW,SoGPSW,JD,DecY]


# Validar lista de precisões
def validar_precisoes(lista, val = [1,5]):
    # Verifica se a lista tem 1 ou 5 elementos
    if len(lista) != val[0] and len(lista) != val[1]:
        return False
    for item in lista:
        # Tenta converter o item para um inteiro
        try:
            numero = int(item)
        except ValueError:
            return False
        # Verifica se o número é maior ou igual a zero
        if numero < 0:
            return False
    return True
