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

from numpy import radians, arctan, pi, sin, cos, matrix, sqrt, degrees, array, diag, ones, zeros, floor
from numpy.linalg import norm, pinv, inv

def azimute(A,B):
    # Cálculo dos Azimutes entre dois pontos (Vetor AB origem A extremidade B)
    if ((B.x()-A.x())>=0 and (B.y()-A.y())>0): #1º quadrante
        AzAB=arctan((B.x()-A.x())/(B.y()-A.y()))
        AzBA=AzAB+pi
    elif ((B.x()-A.x())>0 and(B.y()-A.y())<0): #2º quadrante
        AzAB=pi+arctan((B.x()-A.x())/(B.y()-A.y()))
        AzBA=AzAB+pi
    elif ((B.x()-A.x())<=0 and(B.y()-A.y())<0): #3º quadrante
        AzAB=arctan((B.x()-A.x())/(B.y()-A.y()))+pi
        AzBA=AzAB-pi
    elif ((B.x()-A.x())<0 and(B.y()-A.y())>0): #4º quadrante
        AzAB=2*pi+arctan((B.x()-A.x())/(B.y()-A.y()))
        AzBA=AzAB+pi
    elif ((B.x()-A.x())>0 and(B.y()-A.y())==0): # no eixo positivo de x (90º)
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
        resto = round(abs(dd) - graus, 10)
        minutos = int(floor(60*resto))
        resto = round(resto*60 - minutos, 10)
        segundos = resto*60
        if round(segundos,n_digits) == 60:
            minutos += 1
            segundos = 0
        if minutos == 60:
            graus += 1
            minutos = 0
        if dd < 0:
            texto = '-' + str(graus) + '°'
        else:
            texto = str(graus) + '°'
        texto = texto + '{:02d}'.format(minutos) + "'"
        if n_digits < 1:
            texto = texto + '{:02d}'.format(int(segundos)) + '"'
        else:
            texto = texto + ('{:0' + str(3+n_digits) + '.' + str(n_digits) + 'f}').format(segundos) + '"'
        return texto
    else:
        return "0°00'" + ('{:0' + str(3+n_digits) + '.' + str(n_digits) + 'f}').format(0)


def dms2dd(txt):
    txt = txt.replace(' ','').replace('\t','').replace(',','.')
    newtxt =''
    for letter in txt:
        if not letter.isnumeric() and letter != '.' and letter != '-':
            newtxt += '|'
        else:
            newtxt += letter
    lista = newtxt[:-1].split('|')
    if len(lista) != 3: # GMS
        return None
    else:
        if '-' in lista[0]:
            return -1*(abs(float(lista[0])) + float(lista[1])/60 + float(lista[2])/3600)
        else:
            return float(lista[0]) + float(lista[1])/60 + float(lista[2])/3600


def str2HTML(texto):
    if texto:
        dicHTML = {'Á': '&Aacute;',	'á': '&aacute;',	'Â': '&Acirc;',	'â': '&acirc;',	'À': '&Agrave;',	'à': '&agrave;',	'Å': '&Aring;',	'å': '&aring;',	'Ã': '&Atilde;',	'ã': '&atilde;',	'Ä': '&Auml;',	'ä': '&auml;', 'ú': '&uacute;', 'Ú': '&Uacute;', 'Æ': '&AElig;',	'æ': '&aelig;',	'É': '&Eacute;',	'é': '&eacute;',	'Ê': '&Ecirc;',	'ê': '&ecirc;',	'È': '&Egrave;',	'è': '&egrave;',	'Ë': '&Euml;',	'ë': '&Euml;',	'Ð': '&ETH;',	'ð': '&eth;',	'Í': '&Iacute;',	'í': '&iacute;',	'Î': '&Icirc;',	'î': '&icirc;',	'Ì': '&Igrave;',	'ì': '&igrave;',	'Ï': '&Iuml;',	'ï': '&iuml;',	'Ó': '&Oacute;',	'ó': '&oacute;',	'Ô': '&Ocirc;',	'ô': '&ocirc;',	'Ò': '&Ograve;', 'Õ': '&Otilde;', 'õ': '&otilde;',	'ò': '&ograve;',	'Ø': '&Oslash;',	'ø': '&oslash;',	'Ù': '&Ugrave;',	'ù': '&ugrave;',	'Ü': '&Uuml;',	'ü': '&uuml;',	'Ç': '&Ccedil;',	'ç': '&ccedil;',	'Ñ': '&Ntilde;',	'ñ': '&ntilde;',	'Ý': '&Yacute;',	'ý': '&yacute;',	'"': '&quot;', '”': '&quot;',	'<': '&lt;',	'>': '&gt;',	'®': '&reg;',	'©': '&copy;',	'\'': '&apos;', 'ª': '&ordf;', 'º': '&ordm', '°':'&deg;'}
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
    lon =arctan(Y/X)
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

    M = matrix(
    [
    [  -sin(lon),                     cos(lon),                 0 ],
    [  -sin(lat)*cos(lon),   -sin(lat)*sin(lon),          cos(lat)],
    [   cos(lat)*cos(lon),    cos(lat)*sin(lon),          sin(lat)]
    ]
    )

    T = matrix(
    [[X - Xo], [Y-Yo], [Z-Zo]]
    )

    Fo = matrix([[15e4],[25e4],[0]]) # False E and N

    R = M*T + Fo
    return (R[0,0], R[1,0], R[2,0])


# Conversão de Coordenadas Topocêntricas para Geocêntrica
def enu2geoc(E, N, U, lon0, lat0, Xo, Yo, Zo):
    lon = radians(lon0)
    lat = radians(lat0)

    Fo = matrix([[15e4],[25e4],[0]]) # False E and N

    M = matrix(
    [
    [  -sin(lon),     -sin(lat)*cos(lon),          cos(lat)*cos(lon)],
    [  cos(lon),      -sin(lat)*sin(lon),          cos(lat)*sin(lon)],
    [   0        ,              cos(lat),                       sin(lat)     ]
    ]
    )

    T = matrix(
    [[E], [N], [U]]
    )

    R = M*(T-Fo) + [[Xo], [Yo], [Zo]]
    return (R[0,0], R[1,0], R[2,0])
