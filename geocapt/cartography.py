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

from numpy import sign, array, arange
from numpy.linalg import norm
import numpy as np
from math import floor, modf
import math
import random
import colorsys
from pyproj.crs import CRS
from lftools.geocapt.topogeo import azimute, geod2geoc, geoc2enu
from qgis.core import *
from qgis.PyQt.QtGui import QFont, QColor


def FusoHemisf(pnt):
    lon = pnt.x()
    lat = pnt.y()
    # Calculo do Fuso
    fuso = int(round((183+lon)/6.0))
    # Hemisferio
    hemisf = 'N' if lat>= 0 else 'S'
    return (fuso, hemisf)


def CentralMeridian(pnt):
    lon = pnt.x()
    lat = pnt.y()
    # Calculo do Fuso
    fuso = round((183+lon)/6.0)
    # MC
    MC = 6*fuso - 183
    return MC


def MeridianConvergence(lon, lat, src):
    # Calculo do Fuso
    fuso = round((183+lon)/6.0)
    # Calculo do Meridiano Central
    MC = 6*fuso-183
    # Fator de distorcao inicial
    kappaZero = 0.9996
    # Semi-eixos
    EPSG = int(src.authid().split(':')[-1])
    proj_crs = CRS.from_epsg(EPSG)
    a=proj_crs.ellipsoid.semi_major_metre
    b=proj_crs.ellipsoid.semi_minor_metre
    # Calculo da Convergencia Meridiana
    delta_lon = abs( MC - lon )
    p = 0.0001*( delta_lon*3600 )
    xii = math.sin(math.radians(lat))*math.pow(10, 4)
    e2 = math.sqrt(a*a - b*b)/b
    c5 = math.pow(math.sin(math.radians(1/3600)), 4)*math.sin(math.radians(lat))*math.pow(math.cos(math.radians(lat)), 4)*(2 - math.pow(math.tan(math.radians(lat)), 2))*math.pow(10, 20)/15
    xiii = math.pow(math.sin(math.radians(1/3600)), 2)*math.sin(math.radians(lat))*math.pow(math.cos(math.radians(lat)), 2)*(1 + 3*e2*e2*math.pow(math.cos(math.radians(lat)), 2) + 2*math.pow(e2, 4)*math.pow(math.cos(math.radians(lat)), 4))*math.pow(10, 12)/3
    cSeconds = xii*p + xiii*math.pow(p, 3) + c5*math.pow(p, 5)
    c = abs(cSeconds/3600)
    if (lon-MC)*lat < 0:
        c *= -1
    return c


def ScaleFactor(lon, lat):
    # Calculo do Fuso
    fuso = round((183+lon)/6.0)
    # Calculo do Meridiano Central
    MC = 6*fuso-183
    kappaZero = 0.9996 # Fator de distorcao inicial
    b = math.cos(math.radians(lat))*math.sin(math.radians(lon - MC))
    k = kappaZero/math.sqrt(1 - b*b)
    return k


def SRC_Projeto(output_type):
    a = QgsProject.instance()
    b = a.crs()
    if output_type == 'EPSG':
        return b.authid()
    else:
        return b.description()


def areaGauss(coords):
    soma = 0
    tam = len(coords)
    for k in range(tam):
        P1 = coords[ -1 if k==0 else k-1]
        P2 = coords[k]
        P3 = coords[ 0 if k==(tam-1) else (k+1)]
        soma += P2.x()*(P1.y() - P3.y())
    return soma/2


def distEuclidiana2D(p1, p2):
    return float(np.sqrt((p1.x() - p2.x())**2 + (p1.y() - p2.y())**2))

def distEuclidiana3D(p1, p2):
    return float(np.sqrt((p1.x() - p2.x())**2 + (p1.y() - p2.y())**2  + (p1.z() - p2.z())**2))


def Distancia(coords, dim):
    soma = 0
    tam = len(coords)
    for k in range(tam-1):
        P1 = coords[k]
        P2 = coords[k+1]
        if dim.lower() == '3d':
            soma += distEuclidiana3D(P1,P2)
        else: # '2d'
            soma += distEuclidiana2D(P1,P2)
    return float(soma)


def AzimutePuissant(lat1, lon1, lat2, lon2, a = 6378137, f = 1/298.257222101):
    """
    Calcula o azimute segundo Puissant entre dois pontos geodésicos.

    Parâmetros:
    lat1, lon1: Latitude e longitude do ponto inicial em graus.
    lat2, lon2: Latitude e longitude do ponto final em graus.
    a: Semi-eixo maior do elipsoide (padrão: 6378137 metros).
    f: Achatamento do elipsoide (padrão: 1/298.257222101).

    Retorna:
    Azimute em graus.
    """
    e2 = 2*f - f**2 # Calcula a excentricidade quadrada (e^2) a partir do achatamento (f)
    seno_1segundo = math.sin(math.radians(1/3600))

    lat_media = (math.radians(lat1) + math.radians(lat2)) / 2
    seno_lat_media = math.sin(lat_media)
    cos_lat_media = math.cos(lat_media)
    pow_seno_20 = math.pow(seno_lat_media, 2)
    Nm = a / (math.pow(1 - (e2 * pow_seno_20), 0.5))
    delta_lat = (lat2 - lat1) * 3600
    delta_lon = (lon2 - lon1) * 3600

    Mm = (a * (1 - e2)) / math.pow(1 - (e2 * pow_seno_20), 1.5)
    Bm = 1 / (Mm * seno_1segundo)

    x = delta_lon * cos_lat_media * Nm * seno_1segundo
    y = delta_lat * math.cos(math.radians(delta_lon / 7200))/Bm

    F = (1 / 12) * seno_lat_media * cos_lat_media * cos_lat_media * seno_1segundo * seno_1segundo
    gamma = (delta_lon * seno_lat_media * (1 / math.cos(math.radians(delta_lat / 7200))) + (F * delta_lon * delta_lon * delta_lon))
    Azimute = math.degrees(math.atan2(x, y)) - (gamma / 7200)
    return (Azimute + 360)%360


def raioMedioGauss(lat, EPSG):
    proj_crs = CRS.from_epsg(EPSG)
    a=proj_crs.ellipsoid.semi_major_metre
    f=1/proj_crs.ellipsoid.inverse_flattening
    e2 = f*(2-f)
    N = a/np.sqrt(1-e2*(np.sin(lat))**2) # Raio de curvatura 1º vertical
    M = a*(1-e2)/(1-e2*(np.sin(lat))**2)**(3/2.) # Raio de curvatura meridiana
    R = np.sqrt(M*N) # Raio médio de Gauss
    return R


def OrigemSGL(lon0, lat0, h0, crsGeo):
    ellipsoid_id = crsGeo.ellipsoidAcronym()
    ellipsoid = QgsEllipsoidUtils.ellipsoidParameters(ellipsoid_id)
    a = ellipsoid.semiMajor
    f_inv = ellipsoid.inverseFlattening
    f = 1/f_inv
    X0, Y0, Z0 = geod2geoc(lon0, lat0, h0, a, f)
    return (X0, Y0, Z0, a, f)


# Area no SGL
def AreaPerimetroParteSGL(coordsXYZ, coordsXY, crsGeo):
    centroide = QgsGeometry.fromPolygonXY([coordsXY]).centroid().asPoint()
    alt = []
    for pnt in coordsXYZ[:-1]:
        if str(pnt.z()) != 'nan':
            alt += [pnt.z()]
        else:
            alt += [0]
    h0 = np.array(alt).mean()
    lon0 = centroide.x()
    lat0 = centroide.y()
    Xo, Yo, Zo, a, f = OrigemSGL(lon0, lat0, h0, crsGeo)
    # CONVERSÃO DAS COORDENADAS
    coordsSGL = []
    for coord in coordsXYZ:
        lon = coord.x()
        lat = coord.y()
        h = coord.z() if str(coord.z()) != 'nan' else 0
        X, Y, Z = geod2geoc(lon, lat, h, a, f)
        E, N, U = geoc2enu(X, Y, Z, lon0, lat0, Xo, Yo, Zo)
        coordsSGL += [QgsPointXY(E, N)]
    return (abs(areaGauss(coordsSGL)), Distancia(coordsSGL, '2D'))

def areaSGL(geomGeo, crsGeo):
    if geomGeo.isMultipart():
        coordsXYZ = geom2PointList(geomGeo)
        coordsXY = geomGeo.asMultiPolygon()
        areaSGL = 0
        for k, coords in enumerate(coordsXY):
            coordsGeo = coordsXYZ[k]
            areaSGL += AreaPerimetroParteSGL(coordsGeo[0], coords[0], crsGeo)[0]
            n_aneis = len(coordsGeo)
            if n_aneis > 1:
                for w in range(1, n_aneis):
                    areaSGL -= AreaPerimetroParteSGL(coordsGeo[w], coords[w], crsGeo)[0]
    else:
        coordsGeo = geom2PointList(geomGeo)
        coords = geomGeo.asPolygon()
        areaSGL = AreaPerimetroParteSGL(coordsGeo[0], coords[0], crsGeo)[0]
        n_aneis = len(coordsGeo)
        if n_aneis > 1:
            for w in range(1, n_aneis):
                areaSGL -= AreaPerimetroParteSGL(coordsGeo[w], coords[w], crsGeo)[0]
    return areaSGL

def perimetroSGL(geomGeo, crsGeo):
    if geomGeo.isMultipart():
        coordsXYZ = geom2PointList(geomGeo)
        coordsXY = geomGeo.asMultiPolygon()
        perimetroSGL = 0
        for k, coords in enumerate(coordsXY):
            coordsGeo = coordsXYZ[k]
            perimetroSGL += AreaPerimetroParteSGL(coordsGeo[0], coords[0], crsGeo)[1]
    else:
        coordsGeo = geom2PointList(geomGeo)
        coords = geomGeo.asPolygon()
        perimetroSGL = AreaPerimetroParteSGL(coordsGeo[0], coords[0], crsGeo)[1]
    return float(perimetroSGL)


def Unicos(pnts):
    lista = []
    for pnt in pnts:
        if pnt not in lista:
            lista += [pnt]
    return lista

# Azimute e Distância no SGL
def AzimuteDistanciaSGL(pntA, pntB, geomGeo, crsGeo, tipoAz):
    # Origem do SGL
    centroide = geomGeo.centroid().asPoint()
    coordsXYZ = geom2PointList(geomGeo)
    # Obter cota média
    pnts = np.hstack(coordsXYZ)
    try:
        pnts = Unicos(pnts[0]) # remover duplicados
    except:
        pnts = Unicos(pnts)
    cotas = 0
    for pnt in pnts:
        if str(pnt.z()) != 'nan':
            cotas += pnt.z()
        else:
            cotas += 0
    h0 = cotas/len(pnts)
    lon0 = centroide.x()
    lat0 = centroide.y()
    X0, Y0, Z0, a, f = OrigemSGL(lon0, lat0, h0, crsGeo)
    # Transformar geodésicas para geocêntricas
    XA, YA, ZA = geod2geoc(pntA.x(), pntA.y(), pntA.z() if str(pntA.z()) != 'nan' else 0, a, f)
    XB, YB, ZB = geod2geoc(pntB.x(), pntB.y(), pntB.z() if str(pntB.z()) != 'nan' else 0, a, f)
    # Transformar geocêntricas para topocêntricas (SGL)
    Ea, Na, Ua = geoc2enu(XA, YA, ZA, lon0, lat0, X0, Y0, Z0)
    Eb, Nb, Ub = geoc2enu(XB, YB, ZB, lon0, lat0, X0, Y0, Z0)
    # Calcular distância
    dist = distEuclidiana2D(QgsPointXY(Ea, Na), QgsPointXY(Eb, Nb))
    # Tipo de Azimute
    if tipoAz.lower() == 'puissant': # Calcular azimute de Puissant
        Az = AzimutePuissant(pntA.y(), pntA.x(), pntB.y(), pntB.x(), a, f)
    elif tipoAz.upper() == 'SGL': # Azimute no SGL
        Az = (180/np.pi)*azimute(pntA, pntB)[0]
    return Az, dist


# Comprimento no SGL para linhas 2D e 3D
def comprimentoSGL(geomGeo, crsGeo, dim):
    if geomGeo.isMultipart():
        coordsGeo = geom2PointList(geomGeo)[0]
    else:
        coordsGeo = geom2PointList(geomGeo)
    centroide = geomGeo.centroid().asPoint()
    alt = []
    for pnt in coordsGeo:
        if str(pnt.z()) != 'nan':
            alt += [pnt.z()]
        else:
            alt += [0]
    h0 = np.array(alt).mean()
    lon0 = centroide.x()
    lat0 = centroide.y()

    ellipsoid_id = crsGeo.ellipsoidAcronym()
    ellipsoid = QgsEllipsoidUtils.ellipsoidParameters(ellipsoid_id)
    a = ellipsoid.semiMajor
    f_inv = ellipsoid.inverseFlattening
    f = 1/f_inv

    # CENTRO DE ROTAÇÃO
    Xo, Yo, Zo = geod2geoc(lon0, lat0, h0, a, f)
    # CONVERSÃO DAS COORDENADAS
    coordsSGL = []
    for coord in coordsGeo:
        lon = coord.x()
        lat = coord.y()
        h = coord.z() if str(coord.z()) != 'nan' else 0
        X, Y, Z = geod2geoc(lon, lat, h, a, f)
        E, N, U = geoc2enu(X, Y, Z, lon0, lat0, Xo, Yo, Zo)
        coordsSGL += [QgsPoint(E, N, U)]
    if dim.lower() == '3d': # Comprimento Real 3D no SGL para Linhas 3D
        return Distancia(coordsSGL, dim)
    else: # 2D: Comprimento no plano do SGL
        return Distancia(coordsSGL, dim)


def ChartSize(geom, zone, hemisf, escala):
    # Transformar Coordenadas de Geográficas para o sistema UTM
    coordinateTransformer = QgsCoordinateTransform()
    crs = QgsCoordinateReferenceSystem()
    if hemisf.upper() == 'S':
        proj4 = "PROJ4: +proj=utm +zone={} +south +datum=WGS84 +units=m +no_defs".format(str(zone))
    else:
        proj4 = "PROJ4: +proj=utm +zone={} +datum=WGS84 +units=m +no_defs".format(str(zone))
    crs.createFromString(proj4)
    coordinateTransformer.setDestinationCrs(crs)
    coordinateTransformer.setSourceCrs(QgsCoordinateReferenceSystem('EPSG:4326'))
    projectedGeom = reprojectPoints(geom, coordinateTransformer)
    if projectedGeom.isMultipart():
        coord = projectedGeom.asPolygon()[0][0]
    else:
        coord = projectedGeom.asPolygon()[0]
    tam = len(coord)
    distX = 0
    distY = 0
    for k in range(tam-1):
        p1 = array(coord[k])
        p2 = array(coord[k+1])
        vetor = p1-p2
        dist = norm(vetor)
        if abs(vetor[0]) > abs(vetor[1]): # distância em X
            if dist > distX:
                distX = dist
        else: # distância em Y
            if dist > distY:
                distY = dist
    largura = distX/escala*1000
    altura = distY/escala*1000
    return (altura, largura)


def reprojectPoints(geom, xform):
    if geom.type() == 0: #Point
        if geom.isMultipart():
            pnts = geom.asMultiPoint()
            newPnts = []
            for pnt in pnts:
                newPnts += [xform.transform(pnt)]
            newGeom = QgsGeometry.fromMultiPointXY(newPnts)
            return newGeom
        else:
            pnt = geom.asPoint()
            newPnt = xform.transform(pnt)
            newGeom = QgsGeometry.fromPointXY(newPnt)
            return newGeom
    elif geom.type() == 1: #Line
        if geom.isMultipart():
            linhas = geom.asMultiPolyline()
            newLines = []
            for linha in linhas:
                newLine =[]
                for pnt in linha:
                    newLine += [xform.transform(pnt)]
                newLines += [newLine]
            newGeom = QgsGeometry.fromMultiPolylineXY(newLines)
            return newGeom
        else:
            linha = geom.asPolyline()
            newLine =[]
            for pnt in linha:
                newLine += [xform.transform(pnt)]
            newGeom = QgsGeometry.fromPolylineXY(newLine)
            return newGeom
    elif geom.type() == 2: #Polygon
        if geom.isMultipart():
            poligonos = geom.asMultiPolygon()
            newPolygons = []
            for pol in poligonos:
                newPol = []
                for anel in pol:
                    newAnel = []
                    for pnt in anel:
                        newAnel += [xform.transform(pnt)]
                    newPol += [newAnel]
                newPolygons += [newPol]
            newGeom = QgsGeometry.fromMultiPolygonXY(newPolygons)
            return newGeom
        else:
            pol = geom.asPolygon()
            newPol = []
            for anel in pol:
                newAnel = []
                for pnt in anel:
                    newAnel += [xform.transform(pnt)]
                newPol += [newAnel]
            newGeom = QgsGeometry.fromPolygonXY(newPol)
            return newGeom
    else:
        return None


def geom2PointList(geom):
    """
    Converte uma QgsGeometry em listas de QgsPoint, considerando seu tipo:
    - Point: retorna QgsPoint ou lista de QgsPoint
    - Line: retorna lista de pontos ou lista de listas de pontos
    - Polygon: retorna lista de anéis, cada um como lista de QgsPoint
    """
    tipo = geom.type()

    if tipo == 0:  # Ponto
        if geom.isMultipart():
            const1 = geom.constGet()
            return [const1.childGeometry(k) for k in range(len(geom.asMultiPoint()))]
        else:
            return geom.constGet()

    elif tipo == 1:  # Linha
        const1 = geom.constGet()
        if geom.isMultipart():
            return [
                [const1.childGeometry(k).childPoint(m) for m in range(len(linha))]
                for k, linha in enumerate(geom.asMultiPolyline())
            ]
        else:
            return [const1.childPoint(k) for k in range(len(geom.asPolyline()))]

    elif tipo == 2:  # Polígono
        const1 = geom.constGet()
        if geom.isMultipart():
            return [
                [
                    [const1.childGeometry(k).childGeometry(m).childPoint(n)
                     for n in range(len(anel))]
                    for m, anel in enumerate(poligono)
                ]
                for k, poligono in enumerate(geom.asMultiPolygon())
            ]
        else:
            return [
                [const1.childGeometry(k).childPoint(m)
                 for m in range(len(anel))]
                for k, anel in enumerate(geom.asPolygon())
            ]

# Inverter ordem dos vértices linha e polígono
def inv_vertex_order(geom):
    if geom.type() == 1: #Line
        if geom.isMultipart():
            linhas = geom2PointList(geom)
            mLines = QgsMultiLineString()
            for linha in linhas:
                newLine = linha[::-1]
                Line = QgsLineString(newLine)
                mLines.addGeometry(Line)
            newGeom = QgsGeometry(mLines)
            return newGeom
        else:
            linha = geom2PointList(geom)
            newLine = linha[::-1]
            Line = QgsLineString(newLine)
            newGeom = QgsGeometry(Line)
            return newGeom
    elif geom.type() == 2: #Polygon
        if geom.isMultipart():
            poligonos = geom2PointList(geom)
            mPol = QgsMultiPolygon()
            for pol in poligonos:
                ext_coords = pol[0]
                ext_ring = QgsLineString(ext_coords[::-1])
                qgs_pol = QgsPolygon(ext_ring)

                # Anéis internos
                for ring in pol[1:]:
                    int_coords = ring
                    int_ring = QgsLineString(int_coords[::-1])
                    qgs_pol.addInteriorRing(int_ring)

                mPol.addGeometry(qgs_pol)

            newGeom = QgsGeometry(mPol)
            return newGeom
        else:
            pol = geom2PointList(geom)
            ext_coords = pol[0]
            ext_ring = QgsLineString(ext_coords[::-1])
            qgs_pol = QgsPolygon(ext_ring)
            for ring in pol:
                int_coords = ring
                int_ring = QgsLineString(int_coords[::-1])
                qgs_pol.addInteriorRing(int_ring)
            newGeom = QgsGeometry(qgs_pol)
            return newGeom
    else:
        return None

# Orientar polígono
def OrientarPoligono(coords, primeiro, sentido):
    """
    Reorganiza os vértices do polígono com base em um ponto inicial e sentido de orientação desejado.

    Parâmetros:
        coords   : lista de pontos (com métodos .x() e .y())
        primeiro : int
                   0 = não altera ponto inicial
                   1 = começa pelo ponto mais ao norte (maior Y, depois menor X)
                   2 = começa pelo ponto mais ao sul (menor Y, depois maior X)
                   3 = começa pelo ponto mais ao leste (maior X)
                   4 = começa pelo ponto mais ao oeste (menor X)
        sentido  : int
                   0 = sentido horário
                   1 = sentido anti-horário

    Retorna:
        Lista de coordenadas reorganizada e fechada (primeiro ponto repetido no final).
    """
    # definir primeiro vértice
    if primeiro == 1: # Mais ao norte
        ind = None
        ymax = -1e10
        x_ymax = 1e10
        for k, pnt in enumerate(coords):
            if pnt.y() > ymax:
                ymax = pnt.y()
                x_ymax = pnt.x()
                ind = k
            elif pnt.y() == ymax:
                if pnt.x() < x_ymax:
                    ymax = pnt.y()
                    x_ymax = pnt.x()
                    ind = k
    elif primeiro == 2: # Mais ao sul
        ind = None
        ymin = 1e10
        x_ymim = -1e10
        for k, pnt in enumerate(coords):
            if pnt.y() < ymin:
                ymin = pnt.y()
                x_ymim = pnt.x()
                ind = k
            elif pnt.y() == ymin:
                if pnt.x() > x_ymim:
                    ymin = pnt.y()
                    x_ymim = pnt.x()
                    ind = k
    elif primeiro == 3: # Mais ao Leste
        ind = None
        xmax = -1e10
        for k, pnt in enumerate(coords):
            if pnt.x() > xmax:
                xmax = pnt.x()
                ind = k
    elif primeiro == 4: # Mais ao Oeste
        ind = None
        xmin = 1e10
        for k, pnt in enumerate(coords):
            if pnt.x() < xmin:
                xmin = pnt.x()
                ind = k
    if primeiro != 0:
        coords = coords[ind :] + coords[0 : ind]

    #rotacionar
    coords = coords +[coords[0]]
    areaG = areaGauss(coords)
    if areaG < 0 and sentido == 0:
        coords = coords[::-1]
    elif areaG > 0 and sentido == 1:
        coords = coords[::-1]
    return coords



# Azimute principal das feições
def main_azimuth(geometry):
    if geometry.type() == 0 and not geometry.isMultipart():
        return 0
    else:
        pnts = geom2PointList(geometry)
        pnts = np.hstack(pnts)
        if geometry.type() == 2 and geometry.isMultipart():
            pnts = Unicos(pnts[0])
        else:
            pnts = Unicos(pnts)
        a = []
        for pnt in pnts:
            a += [(pnt.x(), pnt.y())]
        if len(a) < 2:
            return 0
        else:
            ca = np.cov(a,y = None,rowvar = 0,bias = 1)
            v, vect = np.linalg.eig(ca)
            if v[0] > v[1]:
                vetor_maior = vect[:,0]
            else:
                vetor_maior = vect[:,1]
            # se segundo quadrante levar para o quarto
            if vetor_maior[0] > 0 and vetor_maior[1] < 0:
                vetor_maior *= -1
            # se terceiro quadrante levar para o primeiro
            if vetor_maior[0] < 0 and vetor_maior[1] < 0:
                vetor_maior *= -1
            # se direção X
            if vetor_maior[0] != 0 and vetor_maior[1] == 0:
                direcao = -90
            # se direção Y
            elif vetor_maior[1] != 0 and vetor_maior[0] == 0:
                direcao = 0
            # se Zero
            elif vetor_maior[0] == 0 and vetor_maior[1] == 0:
                direcao = 0
            else:
                vetor = QgsPointXY(vetor_maior[0], vetor_maior[1])
                direcao = np.degrees(azimute(QgsPointXY(0,0), vetor)[0])
            return direcao


def Mesclar_Multilinhas(inters):
    if inters.type() == 1 and inters.isMultipart():
        partes = inters.asMultiPolyline()
        parte1 = QgsGeometry.fromPolylineXY(partes[0])
        k = 1
        cont = 1
        while len(partes) > 1:
            parte2 = QgsGeometry.fromPolylineXY(partes[k])
            if  parte1.intersects(parte2):
                parte1 = parte1.combine(parte2)
                del partes[k]
            else:
                k += 1
            cont +=1
            if cont > 10:
                break
        inters = parte1
        return inters
    else:
        return inters


def LayerIs3D(camada):
    if not camada or not camada.type() == 0:
        return False
    else:
        # Iterar sobre as feições para verificar a presença de coordenada Z
        tem_coordenada_Z = False
        for feicao in camada.getFeatures():
            geometria = feicao.geometry()
            if geometria and geometria.isEmpty() == False:
                # Verificar os vértices da geometria
                for parte in geometria.parts():
                    for coordenada in parte.vertices():
                        if coordenada.is3D():
                            tem_coordenada_Z = True
                            break
                    if tem_coordenada_Z:
                        break
            if tem_coordenada_Z:
                break

        if tem_coordenada_Z:
            return True
        else:
            return False


def classificar(values, method, n_classes):
    """
    Classifica uma lista de valores em intervalos segundo o método indicado.
    Métodos suportados:
    - 'stddev'      : Standard Deviation
    - 'log'         : Logarithmic Scale
    - 'quantile'    : Equal Count (e.g., quartiles)
    - 'fixed'       : Fixed Interval (step of 10 by default)
    - 'equal'       : Equal Interval (min to max equally divided)
    - 'jenks'       : Natural Breaks (Jenks)
    - 'smooth'      : Smooth Breaks (sine interpolation)
    Retorna uma lista com os valores de limite superior de cada classe.
    """

    values = sorted([v for v in values if v is not None and isinstance(v, (int, float))])
    if not values or len(values) < n_classes:
        return []

    minimum, maximum = min(values), max(values)

    if method == 'jenks':
        jenks = QgsClassificationJenks()
        ranges = jenks.classes(values, n_classes)
        return [r.upperBound() for r in ranges]

    elif method == 'quantile':
        return [values[int(len(values) * i / n_classes)] for i in range(1, n_classes + 1)]

    elif method == 'equal':
        step = (maximum - minimum) / n_classes
        return [minimum + step * (i + 1) for i in range(n_classes)]

    elif method == 'fixed':
        # Arbitrary fixed step of 10 (customize if needed)
        step = 10
        return [minimum + step * (i + 1) for i in range(n_classes)]

    elif method == 'stddev':
        mean = sum(values) / len(values)
        stddev = (sum((x - mean) ** 2 for x in values) / len(values)) ** 0.5
        return [mean + stddev * (i - n_classes // 2) for i in range(1, n_classes + 1)]

    elif method == 'log':
        if minimum <= 0:
            minimum = 1e-6
        step = (math.log10(maximum) - math.log10(minimum)) / n_classes
        return [10 ** (math.log10(minimum) + step * (i + 1)) for i in range(n_classes)]

    elif method == 'smooth':
        return [(maximum - minimum) * math.sin((i + 1) * math.pi / (2 * n_classes)) + minimum for i in range(n_classes)]

    else:
        return []


def gerar_paleta_tematica(tema, n=10):
    """
    Gera uma lista de cores RGB (tuplas) com base em um tema e quantidade desejada.

    Parâmetros:
    ----------
    tema : str
        Nome do tema de cor. Exemplos: 'pastel', 'vibrante', 'rústica', 'gelo',
        'crepúsculo', 'neon', 'infantil', 'natureza', 'metálico'

    n : int
        Número de cores a serem geradas

    Retorno:
    -------
    List[Tuple[int, int, int]] : Lista de tuplas RGB
    """

    cores = []

    for i in range(n):
        if tema == 'vibrante':
            h = i / n
            s, v = 0.9, 0.95

        elif tema == 'pastel':
            h = i / n
            s, v = 0.4, 0.95

        elif tema == 'rústica':
            h = random.uniform(0.05, 0.15)
            s, v = 0.5, 0.5

        elif tema == 'gelo':
            h = random.uniform(0.5, 0.6)
            s, v = 0.2, 0.95

        elif tema == 'crepúsculo':
            h = random.uniform(0.85, 1.0) if i % 2 == 0 else random.uniform(0.05, 0.1)
            s, v = 0.8, 0.9

        elif tema == 'neon':
            h = random.random()
            s, v = 1.0, 1.0

        elif tema == 'infantil':
            h = i / n
            s, v = 0.5, 1.0

        elif tema == 'natureza':
            h = random.uniform(0.25, 0.4)  # tons de verde e marrom claro
            s, v = 0.5, 0.6

        elif tema == 'metálico':
            paleta_fixa = [
                (105, 105, 105), (169, 169, 169), (192, 192, 192),
                (112, 128, 144), (70, 130, 180)
            ]
            return (paleta_fixa * ((n // len(paleta_fixa)) + 1))[:n]

        else:
            h = random.random()
            s, v = 0.7, 0.9

        r, g, b = colorsys.hsv_to_rgb(h, s, v)
        cores.append((int(r * 255), int(g * 255), int(b * 255)))

    return cores


def LabelConf(nome, fonte="Arial", tam=10, bold=True, cor="white", buffer_tam = 0.5, buffer_cor = "black", dist=2):
    # Configurar as propriedades de rótulo
    label_settings = QgsPalLayerSettings()
    label_settings.fieldName = '"[nome]"'.replace('[nome]',nome)
    label_settings.isExpression = True
    label_settings.placement = QgsPalLayerSettings.AroundPoint
    label_settings.dist = dist
    label_settings.enabled = True
    # Configurar o estilo do texto
    text_format = QgsTextFormat()
    font = QFont(fonte, tam)
    font.setBold(bold)
    text_format.setFont(font)
    text_format.setSize(tam)
    text_format.setColor(QColor(cor))
    # Configurar o buffer
    buffer_settings = QgsTextBufferSettings()
    buffer_settings.setEnabled(True)
    buffer_settings.setSize(buffer_tam)
    buffer_settings.setColor(QColor(buffer_cor))
    text_format.setBuffer(buffer_settings)
    # Aplicar o estilo de texto no rótulo
    label_settings.setFormat(text_format)
    # Configurar e ativar os rótulos
    labeling = QgsVectorLayerSimpleLabeling(label_settings)
    return labeling


def SymbolSimplePoint(layer, cor=QColor(255, 0, 0), tamanho=3.0, tipo='circle',
                      cor_borda=QColor(0, 0, 0), largura_borda=0.3, opacidade=1.0):
    symbol = QgsMarkerSymbol.createSimple({
        'name': tipo,
        'color': cor.name(),               # QColor(255, 0, 0, 100) # vermelho com 100 de opacidade (0 a 255)
        'size': str(tamanho),
        'outline_color': cor_borda.name(),
        'outline_width': str(largura_borda)
    })
    # Aplica opacidade (0 totalmente transparente, 1 totalmente opaco)
    symbol.setOpacity(opacidade)
    return QgsSingleSymbolRenderer(symbol)



def map_sistem(lon, lat, ScaleD=1e6):
    # Escala 1:1.000.000
    nome = ''
    sinal = sign(lat)
    if sinal == -1:
        nome+='S'
    else:
        nome+='N'
    # Determinacao da letra
    letra = chr(int(65+floor(abs(lat)/4.0)))
    nome+=letra
    # Calculo do Fuso
    fuso = round((183+lon)/6.0)
    nome+='-'+str(int(fuso))
    # Calculo do Meridiano Central
    MC = 6*fuso-183
    valores = array([[3.0, 1.5, 0.5, 0.25, 0.125, 0.125/2, 0.125/2/2, 0.125/2/2/3, 0.125/2/2/3/2],
                     [2.0, 1.0, 0.5, 0.25, 0.125, 0.125/3, 0.125/3/2, 0.125/3/2/2, 0.125/3/2/2/2]])
    if ScaleD > 500000:
        return nome

    # Escala 1:500.000
    if ScaleD <= 500000:
        centro = array([MC, 4.0*floor(lat/4.0)+valores[1][0]])
        sinal = sign(array([lon, lat]) - centro)
        if sinal[0]==-1 and sinal[1]==1:
            nome+='-V'
        elif sinal[0]==1 and sinal[1]==1:
            nome+='-X'
        elif sinal[0]==-1 and sinal[1]==-1:
            nome+='-Y'
        elif sinal[0]==1 and sinal[1]==-1:
            nome+='-Z'
    if ScaleD > 250000:
        return nome

    # Escala 1:250.000
    if ScaleD <= 250000:
        centro = centro + sinal*valores[:,1]
        sinal = sign(array([lon, lat]) - centro)
        if sinal[0]==-1 and sinal[1]==1:
            nome+='-A'
        elif sinal[0]==1 and sinal[1]==1:
            nome+='-B'
        elif sinal[0]==-1 and sinal[1]==-1:
            nome+='-C'
        elif sinal[0]==1 and sinal[1]==-1:
            nome+='-D'
    if ScaleD > 100000:
            return nome

    # Escala 1:100.000
    if ScaleD <= 100000:
        ok = False
        if sinal[0]==1:
            c1 = centro + sinal*valores[:,2]
            sinal_ = sign(array([lon, lat]) - c1)
            if sinal_[0]==-1 and sinal_[1]==1:
                nome+='-I'
                ok = True
                centro = c1
                sinalx = sinal_
            elif sinal_[0]==-1 and sinal_[1]==-1:
                nome+='-IV'
                ok = True
                centro = c1
                sinalx = sinal_
            c2 = centro + array([2*sinal[0], sinal[1]])*valores[:,2]
            sinal_ = sign(array([lon, lat]) - c2)
            if sinal_[0]==1 and sinal_[1]==1 and ok == False:
                nome+='-III'
                centro = c2
                sinalx = sinal_
            elif sinal_[0]==1 and sinal_[1]==-1 and ok == False:
                nome+='-VI'
                centro = c2
                sinalx = sinal_
            elif sinal_[0]==-1 and sinal_[1]==1 and ok == False:
                nome+='-II'
                centro = c2
                sinalx = sinal_
            elif sinal_[0]==-1 and sinal_[1]==-1 and ok == False:
                nome+='-V'
                centro = c2
                sinalx = sinal_
        elif sinal[0]==-1:
            c1 = centro + sinal*valores[:,2]
            sinal_ = sign(array([lon, lat]) - c1)
            if sinal_[0]==1 and sinal_[1]==1:
                nome+='-III'
                ok = True
                centro = c1
                sinalx = sinal_
            elif sinal_[0]==1 and sinal_[1]==-1:
                nome+='-VI'
                ok = True
                centro = c1
                sinalx = sinal_
            c2 = centro + array([2*sinal[0], sinal[1]])*valores[:,2]
            sinal_ = sign(array([lon, lat]) - c2)
            if sinal_[0]==1 and sinal_[1]==1 and ok == False:
                nome+='-II'
                centro = c2
                sinalx = sinal_
            elif sinal_[0]==1 and sinal_[1]==-1 and ok == False:
                nome+='-V'
                centro = c2
                sinalx = sinal_
            elif sinal_[0]==-1 and sinal_[1]==1 and ok == False:
                nome+='-I'
                centro = c2
                sinalx = sinal_
            elif sinal_[0]==-1 and sinal_[1]==-1 and ok == False:
                nome+='-IV'
                centro = c2
                sinalx = sinal_
        sinal = sinalx
    if ScaleD > 50000:
            return nome

    # Escala 1:50.000
    if ScaleD <= 50000:
        centro = centro + sinal*valores[:,3]
        sinal = sign(array([lon, lat]) - centro)
        if sinal[0]==-1 and sinal[1]==1:
            nome+='-1'
        elif sinal[0]==1 and sinal[1]==1:
            nome+='-2'
        elif sinal[0]==-1 and sinal[1]==-1:
            nome+='-3'
        elif sinal[0]==1 and sinal[1]==-1:
            nome+='-4'
    if ScaleD > 25000:
            return nome

    # Escala 1:25.000
    if ScaleD <= 25000:
        centro = centro + sinal*valores[:,4]
        sinal = sign(array([lon, lat]) - centro)
        if sinal[0]==-1 and sinal[1]==1:
            nome+='-NO'
        elif sinal[0]==1 and sinal[1]==1:
            nome+='-NE'
        elif sinal[0]==-1 and sinal[1]==-1:
            nome+='-SO'
        elif sinal[0]==1 and sinal[1]==-1:
            nome+='-SE'
    if ScaleD > 10000:
            return nome

    # Escala 1:10.000
    if ScaleD <= 10000:
        ok = False
        if sinal[1]==1:
            c1 = centro + sinal*valores[:,5]
            sinal_ = sign(array([lon, lat]) - c1)
            if sinal_[0]==-1 and sinal_[1]==-1:
                nome+='-E'
                ok = True
                centro = c1
                sinalx = sinal_
            elif sinal_[0]==1 and sinal_[1]==-1:
                nome+='-F'
                ok = True
                centro = c1
                sinalx = sinal_
            c2 = centro + array([sinal[0], 2*sinal[1]])*valores[:,5]
            sinal_ = sign(array([lon, lat]) - c2)
            if sinal_[0]==1 and sinal_[1]==1 and ok == False:
                nome+='-B'
                centro = c2
                sinalx = sinal_
            elif sinal_[0]==1 and sinal_[1]==-1 and ok == False:
                nome+='-D'
                centro = c2
                sinalx = sinal_
            elif sinal_[0]==-1 and sinal_[1]==1 and ok == False:
                nome+='-A'
                centro = c2
                sinalx = sinal_
            elif sinal_[0]==-1 and sinal_[1]==-1 and ok == False:
                nome+='-C'
                centro = c2
                sinalx = sinal_
        elif sinal[1]==-1:
            c1 = centro + sinal*valores[:,5]
            sinal_ = sign(array([lon, lat]) - c1)
            if sinal_[0]==1 and sinal_[1]==1:
                nome+='-B'
                ok = True
                centro = c1
                sinalx = sinal_
            elif sinal_[0]==-1 and sinal_[1]==1:
                nome+='-A'
                ok = True
                centro = c1
                sinalx = sinal_
            c2 = centro + array([sinal[0], 2*sinal[1]])*valores[:,5]
            sinal_ = sign(array([lon, lat]) - c2)
            if sinal_[0]==1 and sinal_[1]==1 and ok == False:
                nome+='-D'
                centro = c2
                sinalx = sinal_
            elif sinal_[0]==1 and sinal_[1]==-1 and ok == False:
                nome+='-F'
                centro = c2
                sinalx = sinal_
            elif sinal_[0]==-1 and sinal_[1]==1 and ok == False:
                nome+='-C'
                centro = c2
                sinalx = sinal_
            elif sinal_[0]==-1 and sinal_[1]==-1 and ok == False:
                nome+='-E'
                centro = c2
                sinalx = sinal_
        sinal = sinalx
    if ScaleD > 5000:
        return nome

    # Escala 1:5.000
    if ScaleD <= 5000:
        centro = centro + sinal*valores[:,6]
        sinal = sign(array([lon, lat]) - centro)
        if sinal[0]==-1 and sinal[1]==1:
            nome+='-I'
        elif sinal[0]==1 and sinal[1]==1:
            nome+='-II'
        elif sinal[0]==-1 and sinal[1]==-1:
            nome+='-III'
        elif sinal[0]==1 and sinal[1]==-1:
            nome+='-IV'
    if ScaleD > 2000:
            return nome

    # Escala 1:2.000
    if ScaleD <= 2000:
        ok = False
        if sinal[0]==1:
            c1 = centro + sinal*valores[:,7]
            sinal_ = sign(array([lon, lat]) - c1)
            if sinal_[0]==-1 and sinal_[1]==1:
                nome+='-1'
                ok = True
                centro = c1
                sinalx = sinal_
            elif sinal_[0]==-1 and sinal_[1]==-1:
                nome+='-4'
                ok = True
                centro = c1
                sinalx = sinal_
            c2 = centro + array([2*sinal[0], sinal[1]])*valores[:,7]
            sinal_ = sign(array([lon, lat]) - c2)
            if sinal_[0]==1 and sinal_[1]==1 and ok == False:
                nome+='-3'
                centro = c2
                sinalx = sinal_
            elif sinal_[0]==1 and sinal_[1]==-1 and ok == False:
                nome+='-6'
                centro = c2
                sinalx = sinal_
            elif sinal_[0]==-1 and sinal_[1]==1 and ok == False:
                nome+='-2'
                centro = c2
                sinalx = sinal_
            elif sinal_[0]==-1 and sinal_[1]==-1 and ok == False:
                nome+='-5'
                centro = c2
                sinalx = sinal_
        elif sinal[0]==-1:
            c1 = centro + sinal*valores[:,7]
            sinal_ = sign(array([lon, lat]) - c1)
            if sinal_[0]==1 and sinal_[1]==1:
                nome+='-3'
                ok = True
                centro = c1
                sinalx = sinal_
            elif sinal_[0]==1 and sinal_[1]==-1:
                nome+='-6'
                ok = True
                centro = c1
                sinalx = sinal_
            c2 = centro + array([2*sinal[0], sinal[1]])*valores[:,7]
            sinal_ = sign(array([lon, lat]) - c2)
            if sinal_[0]==1 and sinal_[1]==1 and ok == False:
                nome+='-2'
                centro = c2
                sinalx = sinal_
            elif sinal_[0]==1 and sinal_[1]==-1 and ok == False:
                nome+='-5'
                centro = c2
                sinalx = sinal_
            elif sinal_[0]==-1 and sinal_[1]==1 and ok == False:
                nome+='-1'
                centro = c2
                sinalx = sinal_
            elif sinal_[0]==-1 and sinal_[1]==-1 and ok == False:
                nome+='-4'
                centro = c2
                sinalx = sinal_
        sinal = sinalx
    if ScaleD > 1000:
            return nome

    # Escala 1:1.000
    if ScaleD <= 1000:
        centro = centro + sinal*valores[:,8]
        sinal = sign(array([lon, lat]) - centro)
        if sinal[0]==-1 and sinal[1]==1:
            nome+='-A'
        elif sinal[0]==1 and sinal[1]==1:
            nome+='-B'
        elif sinal[0]==-1 and sinal[1]==-1:
            nome+='-C'
        elif sinal[0]==1 and sinal[1]==-1:
            nome+='-D'
        return nome


inom2mi = {'SB-21-V-A-I': '709', 'SB-21-V-A-II': '710', 'SB-21-V-A-III': '711', 'SB-21-V-A-IV': '779', 'SB-21-V-A-V': '780', 'SB-21-V-A-VI': '781', 'SB-21-V-B-I': '712', 'SB-21-V-B-II': '713', 'SB-21-V-B-III': '714', 'SB-21-V-B-IV': '782', 'SB-21-V-B-V': '783', 'SB-21-V-B-VI': '784', 'SB-21-V-C-I': '852', 'SB-21-V-C-II': '853', 'SB-21-V-C-III': '854', 'SB-21-V-C-IV': '929', 'SB-21-V-C-V': '930', 'SB-21-V-C-VI': '931', 'SB-21-V-D-I': '855', 'SB-21-V-D-II': '856', 'SB-21-V-D-III': '857', 'SB-21-V-D-IV': '932', 'SB-21-V-D-V': '933', 'SB-21-V-D-VI': '934', 'SB-21-X-A-I': '715', 'SB-21-X-A-II': '716', 'SB-21-X-A-III': '717', 'SB-21-X-A-IV': '785', 'SB-21-X-A-V': '786', 'SB-21-X-A-VI': '787', 'SB-21-X-B-I': '718', 'SB-21-X-B-II': '719', 'SB-21-X-B-III': '720', 'SB-21-X-B-IV': '788', 'SB-21-X-B-V': '789', 'SB-21-X-B-VI': '790', 'SB-21-X-C-I': '858', 'SB-21-X-C-II': '859', 'SB-21-X-C-III': '860', 'SB-21-X-C-IV': '935', 'SB-21-X-C-V': '936', 'SB-21-X-C-VI': '937', 'SB-21-X-D-I': '861', 'SB-21-X-D-II': '862', 'SB-21-X-D-III': '863', 'SB-21-X-D-IV': '938', 'SB-21-X-D-V': '939', 'SB-21-X-D-VI': '940', 'SB-21-Y-A-I': '1006', 'SB-21-Y-A-II': '1007', 'SB-21-Y-A-III': '1008', 'SB-21-Y-A-IV': '1085', 'SB-21-Y-A-V': '1086', 'SB-21-Y-A-VI': '1087', 'SB-21-Y-B-I': '1009', 'SB-21-Y-B-II': '1010', 'SB-21-Y-B-III': '1011', 'SB-21-Y-B-IV': '1088', 'SB-21-Y-B-V': '1089', 'SB-21-Y-B-VI': '1090', 'SB-21-Y-C-I': '1164', 'SB-21-Y-C-II': '1165', 'SB-21-Y-C-III': '1166', 'SB-21-Y-C-IV': '1243', 'SB-21-Y-C-V': '1244', 'SB-21-Y-C-VI': '1245', 'SB-21-Y-D-I': '1167', 'SB-21-Y-D-II': '1168', 'SB-21-Y-D-III': '1169', 'SB-21-Y-D-IV': '1246', 'SB-21-Y-D-V': '1247', 'SB-21-Y-D-VI': '1248', 'SB-21-Z-A-I': '1012', 'SB-21-Z-A-II': '1013', 'SB-21-Z-A-III': '1014', 'SB-21-Z-A-IV': '1091', 'SB-21-Z-A-V': '1092', 'SB-21-Z-A-VI': '1093', 'SB-21-Z-B-I': '1015', 'SB-21-Z-B-II': '1016', 'SB-21-Z-B-III': '1017', 'SB-21-Z-B-IV': '1094', 'SB-21-Z-B-V': '1095', 'SB-21-Z-B-VI': '1096', 'SB-21-Z-C-I': '1170', 'SB-21-Z-C-II': '1171', 'SB-21-Z-C-III': '1172', 'SB-21-Z-C-IV': '1249', 'SB-21-Z-C-V': '1250', 'SB-21-Z-C-VI': '1251', 'SB-21-Z-D-I': '1173', 'SB-21-Z-D-II': '1174', 'SB-21-Z-D-III': '1175', 'SB-21-Z-D-IV': '1252', 'SB-21-Z-D-V': '1253', 'SB-21-Z-D-VI': '1254', 'NB-21-Y-A-IV': '2A', 'NB-21-Y-C-I': '6', 'NB-21-Y-C-IV': '16', 'NB-20-Y-C-VI': '7', 'NB-20-Y-D-IV': '8', 'NB-20-Y-D-V': '9', 'NB-20-Z-B-V': '1', 'NB-20-Z-B-VI': '2', 'NB-20-Z-C-IV': '10', 'NB-20-Z-C-V': '11', 'NB-20-Z-C-VI': '12', 'NB-20-Z-D-I': '3', 'NB-20-Z-D-II': '4', 'NB-20-Z-D-III': '5', 'NB-20-Z-D-IV': '13', 'NB-20-Z-D-V': '14', 'NB-20-Z-D-VI': '15', 'SF-24-V-A-I': '2577', 'SF-24-V-A-II': '2578', 'SF-24-V-A-III': '2579', 'SF-24-V-A-IV': '2613', 'SF-24-V-A-V': '2614', 'SF-24-V-A-VI': '2615', 'SF-24-V-B-I': '2580', 'SF-24-V-B-IV': '2616', 'SF-24-V-C-I': '2649', 'SF-24-V-C-II': '2650', 'SF-24-V-C-III': '2651', 'SF-24-V-C-IV': '2684', 'SF-24-V-C-V': '2685', 'SF-24-V-C-VI': '2685A', 'SF-24-Y-A-I': '2718', 'SF-24-Y-A-II': '2719', 'SF-24-Y-A-IV': '2748', 'SB-25-V-C-I': '900', 'SB-25-V-C-II': '901', 'SB-25-V-C-IV': '977', 'SB-25-V-C-V': '978', 'SB-25-Y-A-I': '1054', 'SB-25-Y-A-II': '1055', 'SB-25-Y-A-III': '1056', 'SB-25-Y-A-IV': '1133', 'SB-25-Y-A-V': '1134', 'SB-25-Y-A-VI': '1135', 'SB-25-Y-C-I': '1212', 'SB-25-Y-C-II': '1213', 'SB-25-Y-C-III': '1214', 'SB-25-Y-C-IV': '1291', 'SB-25-Y-C-V': '1292', 'SB-25-Y-C-VI': '1293', 'SH-22-V-A-I': '2915', 'SH-22-V-A-II': '2916', 'SH-22-V-A-III': '2917', 'SH-22-V-A-IV': '2931', 'SH-22-V-A-V': '2932', 'SH-22-V-A-VI': '2933', 'SH-22-V-B-I': '2918', 'SH-22-V-B-II': '2919', 'SH-22-V-B-III': '2920', 'SH-22-V-B-IV': '2934', 'SH-22-V-B-V': '2935', 'SH-22-V-B-VI': '2936', 'SH-22-V-C-I': '2948', 'SH-22-V-C-II': '2949', 'SH-22-V-C-III': '2950', 'SH-22-V-C-IV': '2965', 'SH-22-V-C-V': '2966', 'SH-22-V-C-VI': '2967', 'SH-22-V-D-I': '2951', 'SH-22-V-D-II': '2952', 'SH-22-V-D-III': '2953', 'SH-22-V-D-IV': '2968', 'SH-22-V-D-V': '2969', 'SH-22-V-D-VI': '2970', 'SH-22-X-A-I': '2921', 'SH-22-X-A-II': '2922', 'SH-22-X-A-III': '2923', 'SH-22-X-A-IV': '2937', 'SH-22-X-A-V': '2938', 'SH-22-X-A-VI': '2939', 'SH-22-X-B-I': '2924', 'SH-22-X-B-II': '2925', 'SH-22-X-B-IV': '2940', 'SH-22-X-B-V': '2941', 'SH-22-X-C-I': '2954', 'SH-22-X-C-II': '2955', 'SH-22-X-C-III': '2956', 'SH-22-X-C-IV': '2971', 'SH-22-X-C-V': '2972', 'SH-22-X-C-VI': '2973', 'SH-22-X-D-I': '2957', 'SH-22-Y-A-I': '2982', 'SH-22-Y-A-II': '2983', 'SH-22-Y-A-III': '2984', 'SH-22-Y-A-IV': '2995', 'SH-22-Y-A-V': '2996', 'SH-22-Y-A-VI': '2997', 'SH-22-Y-B-I': '2985', 'SH-22-Y-B-II': '2986', 'SH-22-Y-B-III': '2987', 'SH-22-Y-B-IV': '2998', 'SH-22-Y-B-V': '2999', 'SH-22-Y-B-VI': '3000', 'SH-22-Y-C-I': '3008', 'SH-22-Y-C-II': '3009', 'SH-22-Y-C-III': '3010', 'SH-22-Y-C-IV': '3017', 'SH-22-Y-C-V': '3018', 'SH-22-Y-C-VI': '3019', 'SH-22-Y-D-I': '3011', 'SH-22-Y-D-II': '3012', 'SH-22-Y-D-III': '3013', 'SH-22-Y-D-IV': '3020', 'SH-22-Y-D-V': '3021', 'SH-22-Y-D-VI': '3022', 'SH-22-Z-A-I': '2988', 'SH-22-Z-A-II': '2989', 'SH-22-Z-A-IV': '3001', 'SH-22-Z-A-V': '3002', 'SH-22-Z-C-I': '3014', 'NA-21-V-A-I': '29', 'NA-21-V-A-IV': '42', 'NA-21-V-C-I': '56', 'NA-21-V-C-IV': '75', 'NA-21-V-D-VI': '76', 'NA-21-X-C-III': '57', 'NA-21-X-C-V': '77', 'NA-21-X-C-VI': '78', 'NA-21-X-D-I': '58', 'NA-21-X-D-II': '58A', 'NA-21-X-D-IV': '79', 'NA-21-X-D-V': '80', 'NA-21-X-D-VI': '81', 'NA-21-Y-A-I': '105', 'NA-21-Y-A-II': '106', 'NA-21-Y-A-IV': '143', 'NA-21-Y-A-V': '144', 'NA-21-Y-A-VI': '145', 'NA-21-Y-B-I': '107', 'NA-21-Y-B-II': '108', 'NA-21-Y-B-III': '109', 'NA-21-Y-B-IV': '146', 'NA-21-Y-B-V': '147', 'NA-21-Y-B-VI': '148', 'NA-21-Y-C-I': '184', 'NA-21-Y-C-II': '185', 'NA-21-Y-C-III': '186', 'NA-21-Y-C-IV': '226', 'NA-21-Y-C-V': '227', 'NA-21-Y-C-VI': '228', 'NA-21-Y-D-I': '187', 'NA-21-Y-D-II': '188', 'NA-21-Y-D-III': '189', 'NA-21-Y-D-IV': '229', 'NA-21-Y-D-V': '230', 'NA-21-Y-D-VI': '231', 'NA-21-Z-A-I': '110', 'NA-21-Z-A-II': '111', 'NA-21-Z-A-III': '112', 'NA-21-Z-A-IV': '149', 'NA-21-Z-A-V': '150', 'NA-21-Z-A-VI': '151', 'NA-21-Z-B-I': '113', 'NA-21-Z-B-II': '114', 'NA-21-Z-B-III': '115', 'NA-21-Z-B-IV': '152', 'NA-21-Z-B-V': '153', 'NA-21-Z-B-VI': '154', 'NA-21-Z-C-I': '190', 'NA-21-Z-C-II': '191', 'NA-21-Z-C-III': '192', 'NA-21-Z-C-IV': '232', 'NA-21-Z-C-V': '233', 'NA-21-Z-C-VI': '234', 'NA-21-Z-D-I': '193', 'NA-21-Z-D-II': '194', 'NA-21-Z-D-III': '195', 'NA-21-Z-D-IV': '235', 'NA-21-Z-D-V': '236', 'NA-21-Z-D-VI': '237', 'SC-18-X-A-III': '1294', 'SC-18-X-B-I': '1295', 'SC-18-X-B-II': '1296', 'SC-18-X-B-III': '1297', 'SC-18-X-B-IV': '1373', 'SC-18-X-B-V': '1374', 'SC-18-X-B-VI': '1375', 'SC-18-X-D-I': '1450', 'SC-18-X-D-II': '1451', 'SC-18-X-D-III': '1452', 'SC-18-X-D-VI': '1527', 'SF-23-V-A-I': '2565', 'SF-23-V-A-II': '2566', 'SF-23-V-A-III': '2567', 'SF-23-V-A-IV': '2601', 'SF-23-V-A-V': '2602', 'SF-23-V-A-VI': '2603', 'SF-23-V-B-I': '2568', 'SF-23-V-B-II': '2569', 'SF-23-V-B-III': '2570', 'SF-23-V-B-IV': '2604', 'SF-23-V-B-V': '2605', 'SF-23-V-B-VI': '2606', 'SF-23-V-C-I': '2637', 'SF-23-V-C-II': '2638', 'SF-23-V-C-III': '2639', 'SF-23-V-C-IV': '2672', 'SF-23-V-C-V': '2673', 'SF-23-V-C-VI': '2674', 'SF-23-V-D-I': '2640', 'SF-23-V-D-II': '2641', 'SF-23-V-D-III': '2642', 'SF-23-V-D-IV': '2675', 'SF-23-V-D-V': '2676', 'SF-23-V-D-VI': '2677', 'SF-23-X-A-I': '2571', 'SF-23-X-A-II': '2572', 'SF-23-X-A-III': '2573', 'SF-23-X-A-IV': '2607', 'SF-23-X-A-V': '2608', 'SF-23-X-A-VI': '2609', 'SF-23-X-B-I': '2574', 'SF-23-X-B-II': '2575', 'SF-23-X-B-III': '2576', 'SF-23-X-B-IV': '2610', 'SF-23-X-B-V': '2611', 'SF-23-X-B-VI': '2612', 'SF-23-X-C-I': '2643', 'SF-23-X-C-II': '2644', 'SF-23-X-C-III': '2645', 'SF-23-X-C-IV': '2678', 'SF-23-X-C-V': '2679', 'SF-23-X-C-VI': '2680', 'SF-23-X-D-I': '2646', 'SF-23-X-D-II': '2647', 'SF-23-X-D-III': '2648', 'SF-23-X-D-IV': '2681', 'SF-23-X-D-V': '2682', 'SF-23-X-D-VI': '2683', 'SF-23-Y-A-I': '2706', 'SF-23-Y-A-II': '2707', 'SF-23-Y-A-III': '2708', 'SF-23-Y-A-IV': '2736', 'SF-23-Y-A-V': '2737', 'SF-23-Y-A-VI': '2738', 'SF-23-Y-B-I': '2709', 'SF-23-Y-B-II': '2710', 'SF-23-Y-B-III': '2711', 'SF-23-Y-B-IV': '2739', 'SF-23-Y-B-V': '2740', 'SF-23-Y-B-VI': '2741', 'SF-23-Y-C-I': '2765', 'SF-23-Y-C-II': '2766', 'SF-23-Y-C-III': '2767', 'SF-23-Y-C-IV': '2791', 'SF-23-Y-C-V': '2792', 'SF-23-Y-C-VI': '2793', 'SF-23-Y-D-I': '2768', 'SF-23-Y-D-II': '2769', 'SF-23-Y-D-III': '2770', 'SF-23-Y-D-IV': '2794', 'SF-23-Y-D-V': '2795', 'SF-23-Y-D-VI': '2796', 'SF-23-Z-A-I': '2712', 'SF-23-Z-A-II': '2713', 'SF-23-Z-A-III': '2714', 'SF-23-Z-A-IV': '2742', 'SF-23-Z-A-V': '2743', 'SF-23-Z-A-VI': '2744', 'SF-23-Z-B-I': '2715', 'SF-23-Z-B-II': '2716', 'SF-23-Z-B-III': '2717', 'SF-23-Z-B-IV': '2745', 'SF-23-Z-B-V': '2746', 'SF-23-Z-B-VI': '2747', 'SF-23-Z-C-I': '2771', 'SF-23-Z-C-II': '2772', 'SF-23-Z-C-III': '2773', 'SF-23-Z-D-I': '2774', 'SF-23-Z-D-II': '2774A', 'SE-21-V-A-I': '2235', 'SE-21-V-A-II': '2236', 'SE-21-V-A-III': '2237', 'SE-21-V-B-I': '2238', 'SE-21-V-B-II': '2239', 'SE-21-V-B-III': '2240', 'SE-21-V-B-IV': '2278', 'SE-21-V-B-V': '2279', 'SE-21-V-B-VI': '2280', 'SE-21-V-D-I': '2318', 'SE-21-V-D-II': '2319', 'SE-21-V-D-III': '2320', 'SE-21-V-D-V': '2357', 'SE-21-V-D-VI': '2358', 'SE-21-X-A-I': '2241', 'SE-21-X-A-II': '2242', 'SE-21-X-A-III': '2243', 'SE-21-X-A-IV': '2281', 'SE-21-X-A-V': '2282', 'SE-21-X-A-VI': '2283', 'SE-21-X-B-I': '2244', 'SE-21-X-B-II': '2245', 'SE-21-X-B-III': '2246', 'SE-21-X-B-IV': '2284', 'SE-21-X-B-V': '2285', 'SE-21-X-B-VI': '2286', 'SE-21-X-C-I': '2321', 'SE-21-X-C-II': '2322', 'SE-21-X-C-III': '2323', 'SE-21-X-C-IV': '2359', 'SE-21-X-C-V': '2360', 'SE-21-X-C-VI': '2361', 'SE-21-X-D-I': '2324', 'SE-21-X-D-II': '2325', 'SE-21-X-D-III': '2326', 'SE-21-X-D-IV': '2362', 'SE-21-X-D-V': '2363', 'SE-21-X-D-VI': '2364', 'SE-21-Y-B-II': '2395', 'SE-21-Y-B-III': '2396', 'SE-21-Y-B-V': '2432', 'SE-21-Y-B-VI': '2433', 'SE-21-Y-D-I': '2468-A', 'SE-21-Y-D-II': '2469', 'SE-21-Y-D-III': '2470', 'SE-21-Y-D-IV': '2506', 'SE-21-Y-D-V': '2507', 'SE-21-Y-D-VI': '2508', 'SE-21-Z-A-I': '2397', 'SE-21-Z-A-II': '2398', 'SE-21-Z-A-III': '2399', 'SE-21-Z-A-IV': '2434', 'SE-21-Z-A-V': '2435', 'SE-21-Z-A-VI': '2436', 'SE-21-Z-B-I': '2400', 'SE-21-Z-B-II': '2401', 'SE-21-Z-B-III': '2402', 'SE-21-Z-B-IV': '2437', 'SE-21-Z-B-V': '2438', 'SE-21-Z-B-VI': '2439', 'SE-21-Z-C-I': '2471', 'SE-21-Z-C-II': '2472', 'SE-21-Z-C-III': '2473', 'SE-21-Z-C-IV': '2509', 'SE-21-Z-C-V': '2510', 'SE-21-Z-C-VI': '2511', 'SE-21-Z-D-I': '2474', 'SE-21-Z-D-II': '2475', 'SE-21-Z-D-III': '2476', 'SE-21-Z-D-IV': '2512', 'SE-21-Z-D-V': '2513', 'SE-21-Z-D-VI': '2514', 'SE-20-X-B-III': '2234', 'SC-21-V-A-I': '1322', 'SC-21-V-A-II': '1323', 'SC-21-V-A-III': '1324', 'SC-21-V-A-IV': '1400', 'SC-21-V-A-V': '1401', 'SC-21-V-A-VI': '1402', 'SC-21-V-B-I': '1325', 'SC-21-V-B-II': '1326', 'SC-21-V-B-III': '1327', 'SC-21-V-B-IV': '1403', 'SC-21-V-B-V': '1404', 'SC-21-V-B-VI': '1405', 'SC-21-V-C-I': '1477', 'SC-21-V-C-II': '1478', 'SC-21-V-C-III': '1479', 'SC-21-V-C-IV': '1552', 'SC-21-V-C-V': '1553', 'SC-21-V-C-VI': '1554', 'SC-21-V-D-I': '1480', 'SC-21-V-D-II': '1481', 'SC-21-V-D-III': '1482', 'SC-21-V-D-IV': '1555', 'SC-21-V-D-V': '1556', 'SC-21-V-D-VI': '1557', 'SC-21-X-A-I': '1328', 'SC-21-X-A-II': '1329', 'SC-21-X-A-III': '1330', 'SC-21-X-A-IV': '1406', 'SC-21-X-A-V': '1407', 'SC-21-X-A-VI': '1408', 'SC-21-X-B-I': '1331', 'SC-21-X-B-II': '1332', 'SC-21-X-B-III': '1333', 'SC-21-X-B-IV': '1409', 'SC-21-X-B-V': '1410', 'SC-21-X-B-VI': '1411', 'SC-21-X-C-I': '1483', 'SC-21-X-C-II': '1484', 'SC-21-X-C-III': '1485', 'SC-21-X-C-IV': '1558', 'SC-21-X-C-V': '1559', 'SC-21-X-C-VI': '1560', 'SC-21-X-D-I': '1486', 'SC-21-X-D-II': '1487', 'SC-21-X-D-III': '1488', 'SC-21-X-D-IV': '1561', 'SC-21-X-D-V': '1562', 'SC-21-X-D-VI': '1563', 'SC-21-Y-A-I': '1621', 'SC-21-Y-A-II': '1622', 'SC-21-Y-A-III': '1623', 'SC-21-Y-A-IV': '1687', 'SC-21-Y-A-V': '1688', 'SC-21-Y-A-VI': '1689', 'SC-21-Y-B-I': '1624', 'SC-21-Y-B-II': '1625', 'SC-21-Y-B-III': '1626', 'SC-21-Y-B-IV': '1690', 'SC-21-Y-B-V': '1691', 'SC-21-Y-B-VI': '1692', 'SC-21-Y-C-I': '1749', 'SC-21-Y-C-II': '1750', 'SC-21-Y-C-III': '1751', 'SC-21-Y-C-IV': '1806', 'SC-21-Y-C-V': '1807', 'SC-21-Y-C-VI': '1808', 'SC-21-Y-D-I': '1752', 'SC-21-Y-D-II': '1753', 'SC-21-Y-D-III': '1754', 'SC-21-Y-D-IV': '1809', 'SC-21-Y-D-V': '1810', 'SC-21-Y-D-VI': '1811', 'SC-21-Z-A-I': '1627', 'SC-21-Z-A-II': '1628', 'SC-21-Z-A-III': '1629', 'SC-21-Z-A-IV': '1693', 'SC-21-Z-A-V': '1694', 'SC-21-Z-A-VI': '1695', 'SC-21-Z-B-I': '1630', 'SC-21-Z-B-II': '1631', 'SC-21-Z-B-III': '1632', 'SC-21-Z-B-IV': '1696', 'SC-21-Z-B-V': '1697', 'SC-21-Z-B-VI': '1698', 'SC-21-Z-C-I': '1755', 'SC-21-Z-C-II': '1756', 'SC-21-Z-C-III': '1757', 'SC-21-Z-C-IV': '1812', 'SC-21-Z-C-V': '1813', 'SC-21-Z-C-VI': '1814', 'SC-21-Z-D-I': '1758', 'SC-21-Z-D-II': '1759', 'SC-21-Z-D-III': '1760', 'SC-21-Z-D-IV': '1815', 'SC-21-Z-D-V': '1816', 'SC-21-Z-D-VI': '1817', 'SD-22-V-A-I': '1874', 'SD-22-V-A-II': '1875', 'SD-22-V-A-III': '1876', 'SD-22-V-A-IV': '1928', 'SD-22-V-A-V': '1929', 'SD-22-V-A-VI': '1930', 'SD-22-V-B-I': '1877', 'SD-22-V-B-II': '1878', 'SD-22-V-B-III': '1879', 'SD-22-V-B-IV': '1931', 'SD-22-V-B-V': '1932', 'SD-22-V-B-VI': '1933', 'SD-22-V-C-I': '1979', 'SD-22-V-C-II': '1980', 'SD-22-V-C-III': '1981', 'SD-22-V-C-IV': '2026', 'SD-22-V-C-V': '2027', 'SD-22-V-C-VI': '2028', 'SD-22-V-D-I': '1982', 'SD-22-V-D-II': '1983', 'SD-22-V-D-III': '1984', 'SD-22-V-D-IV': '2029', 'SD-22-V-D-V': '2030', 'SD-22-V-D-VI': '2031', 'SD-22-X-A-I': '1880', 'SD-22-X-A-II': '1881', 'SD-22-X-A-III': '1882', 'SD-22-X-A-IV': '1934', 'SD-22-X-A-V': '1935', 'SD-22-X-A-VI': '1936', 'SD-22-X-B-I': '1883', 'SD-22-X-B-II': '1884', 'SD-22-X-B-III': '1885', 'SD-22-X-B-IV': '1937', 'SD-22-X-B-V': '1938', 'SD-22-X-B-VI': '1939', 'SD-22-X-C-I': '1985', 'SD-22-X-C-II': '1986', 'SD-22-X-C-III': '1987', 'SD-22-X-C-IV': '2032', 'SD-22-X-C-V': '2033', 'SD-22-X-C-VI': '2034', 'SD-22-X-D-I': '1988', 'SD-22-X-D-II': '1989', 'SD-22-X-D-III': '1990', 'SD-22-X-D-IV': '2035', 'SD-22-X-D-V': '2036', 'SD-22-X-D-VI': '2037', 'SD-22-Y-A-I': '2070', 'SD-22-Y-A-II': '2071', 'SD-22-Y-A-III': '2072', 'SD-22-Y-A-IV': '2114', 'SD-22-Y-A-V': '2115', 'SD-22-Y-A-VI': '2116', 'SD-22-Y-B-I': '2073', 'SD-22-Y-B-II': '2074', 'SD-22-Y-B-III': '2075', 'SD-22-Y-B-IV': '2117', 'SD-22-Y-B-V': '2118', 'SD-22-Y-B-VI': '2119', 'SD-22-Y-C-I': '2159', 'SD-22-Y-C-II': '2160', 'SD-22-Y-C-III': '2161', 'SD-22-Y-C-IV': '2203', 'SD-22-Y-C-V': '2204', 'SD-22-Y-C-VI': '2205', 'SD-22-Y-D-I': '2162', 'SD-22-Y-D-II': '2163', 'SD-22-Y-D-III': '2164', 'SD-22-Y-D-IV': '2206', 'SD-22-Y-D-V': '2207', 'SD-22-Y-D-VI': '2208', 'SD-22-Z-A-I': '2076', 'SD-22-Z-A-II': '2077', 'SD-22-Z-A-III': '2078', 'SD-22-Z-A-IV': '2120', 'SD-22-Z-A-V': '2121', 'SD-22-Z-A-VI': '2122', 'SD-22-Z-B-I': '2079', 'SD-22-Z-B-II': '2080', 'SD-22-Z-B-III': '2081', 'SD-22-Z-B-IV': '2123', 'SD-22-Z-B-V': '2124', 'SD-22-Z-B-VI': '2125', 'SD-22-Z-C-I': '2165', 'SD-22-Z-C-II': '2166', 'SD-22-Z-C-III': '2167', 'SD-22-Z-C-IV': '2209', 'SD-22-Z-C-V': '2210', 'SD-22-Z-C-VI': '2211', 'SD-22-Z-D-I': '2168', 'SD-22-Z-D-II': '2169', 'SD-22-Z-D-III': '2170', 'SD-22-Z-D-IV': '2212', 'SD-22-Z-D-V': '2213', 'SD-22-Z-D-VI': '2214', 'SG-23-V-A-I': '2812', 'SG-23-V-A-II': '2813', 'SG-23-V-A-III': '2814', 'SG-23-V-A-IV': '2829', 'SG-23-V-A-V': '2830', 'SG-23-V-B-I': '2815', 'SG-23-V-C-I': '2845', 'SE-22-V-A-I': '2247', 'SE-22-V-A-II': '2248', 'SE-22-V-A-III': '2249', 'SE-22-V-A-IV': '2287', 'SE-22-V-A-V': '2288', 'SE-22-V-A-VI': '2289', 'SE-22-V-B-I': '2250', 'SE-22-V-B-II': '2251', 'SE-22-V-B-III': '2252', 'SE-22-V-B-IV': '2290', 'SE-22-V-B-V': '2291', 'SE-22-V-B-VI': '2292', 'SE-22-V-C-I': '2327', 'SE-22-V-C-II': '2328', 'SE-22-V-C-III': '2329', 'SE-22-V-C-IV': '2365', 'SE-22-V-C-V': '2366', 'SE-22-V-C-VI': '2367', 'SE-22-V-D-I': '2330', 'SE-22-V-D-II': '2331', 'SE-22-V-D-III': '2332', 'SE-22-V-D-IV': '2368', 'SE-22-V-D-V': '2369', 'SE-22-V-D-VI': '2370', 'SE-22-X-A-I': '2253', 'SE-22-X-A-II': '2254', 'SE-22-X-A-III': '2255', 'SE-22-X-A-IV': '2293', 'SE-22-X-A-V': '2294', 'SE-22-X-A-VI': '2295', 'SE-22-X-B-I': '2256', 'SE-22-X-B-II': '2257', 'SE-22-X-B-III': '2258', 'SE-22-X-B-IV': '2296', 'SE-22-X-B-V': '2297', 'SE-22-X-B-VI': '2298', 'SE-22-X-C-I': '2333', 'SE-22-X-C-II': '2334', 'SE-22-X-C-III': '2335', 'SE-22-X-C-IV': '2371', 'SE-22-X-C-V': '2372', 'SE-22-X-C-VI': '2373', 'SE-22-X-D-I': '2336', 'SE-22-X-D-II': '2337', 'SE-22-X-D-III': '2338', 'SE-22-X-D-IV': '2374', 'SE-22-X-D-V': '2375', 'SE-22-X-D-VI': '2376', 'SE-22-Y-A-I': '2403', 'SE-22-Y-A-II': '2404', 'SE-22-Y-A-III': '2405', 'SE-22-Y-A-IV': '2440', 'SE-22-Y-A-V': '2441', 'SE-22-Y-A-VI': '2442', 'SE-22-Y-B-I': '2406', 'SE-22-Y-B-II': '2407', 'SE-22-Y-B-III': '2408', 'SE-22-Y-B-IV': '2443', 'SE-22-Y-B-V': '2444', 'SE-22-Y-B-VI': '2445', 'SE-22-Y-C-I': '2477', 'SE-22-Y-C-II': '2478', 'SE-22-Y-C-III': '2479', 'SE-22-Y-C-IV': '2515', 'SE-22-Y-C-V': '2516', 'SE-22-Y-C-VI': '2517', 'SE-22-Y-D-I': '2480', 'SE-22-Y-D-II': '2481', 'SE-22-Y-D-III': '2482', 'SE-22-Y-D-IV': '2518', 'SE-22-Y-D-V': '2519', 'SE-22-Y-D-VI': '2520', 'SE-22-Z-A-I': '2409', 'SE-22-Z-A-II': '2410', 'SE-22-Z-A-III': '2411', 'SE-22-Z-A-IV': '2446', 'SE-22-Z-A-V': '2447', 'SE-22-Z-A-VI': '2448', 'SE-22-Z-B-I': '2412', 'SE-22-Z-B-II': '2413', 'SE-22-Z-B-III': '2414', 'SE-22-Z-B-IV': '2449', 'SE-22-Z-B-V': '2450', 'SE-22-Z-B-VI': '2451', 'SE-22-Z-C-I': '2483', 'SE-22-Z-C-II': '2484', 'SE-22-Z-C-III': '2485', 'SE-22-Z-C-IV': '2521', 'SE-22-Z-C-V': '2522', 'SE-22-Z-C-VI': '2523', 'SE-22-Z-D-I': '2486', 'SE-22-Z-D-II': '2487', 'SE-22-Z-D-III': '2488', 'SE-22-Z-D-IV': '2524', 'SE-22-Z-D-V': '2525', 'SE-22-Z-D-VI': '2526', 'SC-22-V-A-I': '1334', 'SC-22-V-A-II': '1335', 'SC-22-V-A-III': '1336', 'SC-22-V-A-IV': '1412', 'SC-22-V-A-V': '1413', 'SC-22-V-A-VI': '1414', 'SC-22-V-B-I': '1337', 'SC-22-V-B-II': '1338', 'SC-22-V-B-III': '1339', 'SC-22-V-B-IV': '1415', 'SC-22-V-B-V': '1416', 'SC-22-V-B-VI': '1417', 'SC-22-V-C-I': '1489', 'SC-22-V-C-II': '1490', 'SC-22-V-C-III': '1491', 'SC-22-V-C-IV': '1564', 'SC-22-V-C-V': '1565', 'SC-22-V-C-VI': '1566', 'SC-22-V-D-I': '1492', 'SC-22-V-D-II': '1493', 'SC-22-V-D-III': '1494', 'SC-22-V-D-IV': '1567', 'SC-22-V-D-V': '1568', 'SC-22-V-D-VI': '1569', 'SC-22-X-A-I': '1340', 'SC-22-X-A-II': '1341', 'SC-22-X-A-III': '1342', 'SC-22-X-A-IV': '1418', 'SC-22-X-A-V': '1419', 'SC-22-X-A-VI': '1420', 'SC-22-X-B-I': '1343', 'SC-22-X-B-II': '1344', 'SC-22-X-B-III': '1345', 'SC-22-X-B-IV': '1421', 'SC-22-X-B-V': '1422', 'SC-22-X-B-VI': '1423', 'SC-22-X-C-I': '1495', 'SC-22-X-C-II': '1496', 'SC-22-X-C-III': '1497', 'SC-22-X-C-IV': '1570', 'SC-22-X-C-V': '1571', 'SC-22-X-C-VI': '1572', 'SC-22-X-D-I': '1498', 'SC-22-X-D-II': '1499', 'SC-22-X-D-III': '1500', 'SC-22-X-D-IV': '1573', 'SC-22-X-D-V': '1574', 'SC-22-X-D-VI': '1575', 'SC-22-Y-A-I': '1633', 'SC-22-Y-A-II': '1634', 'SC-22-Y-A-III': '1635', 'SC-22-Y-A-IV': '1699', 'SC-22-Y-A-V': '1700', 'SC-22-Y-A-VI': '1701', 'SC-22-Y-B-I': '1636', 'SC-22-Y-B-II': '1637', 'SC-22-Y-B-III': '1638', 'SC-22-Y-B-IV': '1702', 'SC-22-Y-B-V': '1703', 'SC-22-Y-B-VI': '1704', 'SC-22-Y-C-I': '1761', 'SC-22-Y-C-II': '1762', 'SC-22-Y-C-III': '1763', 'SC-22-Y-C-IV': '1818', 'SC-22-Y-C-V': '1819', 'SC-22-Y-C-VI': '1820', 'SC-22-Y-D-I': '1764', 'SC-22-Y-D-II': '1765', 'SC-22-Y-D-III': '1766', 'SC-22-Y-D-IV': '1821', 'SC-22-Y-D-V': '1822', 'SC-22-Y-D-VI': '1823', 'SC-22-Z-A-I': '1639', 'SC-22-Z-A-II': '1640', 'SC-22-Z-A-III': '1641', 'SC-22-Z-A-IV': '1705', 'SC-22-Z-A-V': '1706', 'SC-22-Z-A-VI': '1707', 'SC-22-Z-B-I': '1642', 'SC-22-Z-B-II': '1643', 'SC-22-Z-B-III': '1644', 'SC-22-Z-B-IV': '1708', 'SC-22-Z-B-V': '1709', 'SC-22-Z-B-VI': '1710', 'SC-22-Z-C-I': '1767', 'SC-22-Z-C-II': '1768', 'SC-22-Z-C-III': '1769', 'SC-22-Z-C-IV': '1824', 'SC-22-Z-C-V': '1825', 'SC-22-Z-C-VI': '1826', 'SC-22-Z-D-I': '1770', 'SC-22-Z-D-II': '1771', 'SC-22-Z-D-III': '1772', 'SC-22-Z-D-IV': '1827', 'SC-22-Z-D-V': '1828', 'SC-22-Z-D-VI': '1829', 'SE-23-V-A-I': '2259', 'SE-23-V-A-II': '2260', 'SE-23-V-A-III': '2261', 'SE-23-V-A-IV': '2299', 'SE-23-V-A-V': '2300', 'SE-23-V-A-VI': '2301', 'SE-23-V-B-I': '2262', 'SE-23-V-B-II': '2263', 'SE-23-V-B-III': '2264', 'SE-23-V-B-IV': '2302', 'SE-23-V-B-V': '2303', 'SE-23-V-B-VI': '2304', 'SE-23-V-C-I': '2339', 'SE-23-V-C-II': '2340', 'SE-23-V-C-III': '2341', 'SE-23-V-C-IV': '2377', 'SE-23-V-C-V': '2378', 'SE-23-V-C-VI': '2379', 'SE-23-V-D-I': '2342', 'SE-23-V-D-II': '2343', 'SE-23-V-D-III': '2344', 'SE-23-V-D-IV': '2380', 'SE-23-V-D-V': '2381', 'SE-23-V-D-VI': '2382', 'SE-23-X-A-I': '2265', 'SE-23-X-A-II': '2266', 'SE-23-X-A-III': '2267', 'SE-23-X-A-IV': '2305', 'SE-23-X-A-V': '2306', 'SE-23-X-A-VI': '2307', 'SE-23-X-B-I': '2268', 'SE-23-X-B-II': '2269', 'SE-23-X-B-III': '2270', 'SE-23-X-B-IV': '2308', 'SE-23-X-B-V': '2309', 'SE-23-X-B-VI': '2310', 'SE-23-X-C-I': '2345', 'SE-23-X-C-II': '2346', 'SE-23-X-C-III': '2347', 'SE-23-X-C-IV': '2383', 'SE-23-X-C-V': '2384', 'SE-23-X-C-VI': '2385', 'SE-23-X-D-I': '2348', 'SE-23-X-D-II': '2349', 'SE-23-X-D-III': '2350', 'SE-23-X-D-IV': '2386', 'SE-23-X-D-V': '2387', 'SE-23-X-D-VI': '2388', 'SE-23-Y-A-I': '2415', 'SE-23-Y-A-II': '2416', 'SE-23-Y-A-III': '2417', 'SE-23-Y-A-IV': '2452', 'SE-23-Y-A-V': '2453', 'SE-23-Y-A-VI': '2454', 'SE-23-Y-B-I': '2418', 'SE-23-Y-B-II': '2419', 'SE-23-Y-B-III': '2420', 'SE-23-Y-B-IV': '2455', 'SE-23-Y-B-V': '2456', 'SE-23-Y-B-VI': '2457', 'SE-23-Y-C-I': '2489', 'SE-23-Y-C-II': '2490', 'SE-23-Y-C-III': '2491', 'SE-23-Y-C-IV': '2527', 'SE-23-Y-C-V': '2528', 'SE-23-Y-C-VI': '2529', 'SE-23-Y-D-I': '2492', 'SE-23-Y-D-II': '2493', 'SE-23-Y-D-III': '2494', 'SE-23-Y-D-IV': '2530', 'SE-23-Y-D-V': '2531', 'SE-23-Y-D-VI': '2532', 'SE-23-Z-A-I': '2421', 'SE-23-Z-A-II': '2422', 'SE-23-Z-A-III': '2423', 'SE-23-Z-A-IV': '2458', 'SE-23-Z-A-V': '2459', 'SE-23-Z-A-VI': '2460', 'SE-23-Z-B-I': '2424', 'SE-23-Z-B-II': '2425', 'SE-23-Z-B-III': '2426', 'SE-23-Z-B-IV': '2461', 'SE-23-Z-B-V': '2462', 'SE-23-Z-B-VI': '2463', 'SE-23-Z-C-I': '2495', 'SE-23-Z-C-II': '2496', 'SE-23-Z-C-III': '2497', 'SE-23-Z-C-IV': '2533', 'SE-23-Z-C-V': '2534', 'SE-23-Z-C-VI': '2535', 'SE-23-Z-D-I': '2498', 'SE-23-Z-D-II': '2499', 'SE-23-Z-D-III': '2500', 'SE-23-Z-D-IV': '2536', 'SE-23-Z-D-V': '2537', 'SE-23-Z-D-VI': '2538', 'SG-22-V-A-I': '2800', 'SG-22-V-A-II': '2801', 'SG-22-V-A-III': '2802', 'SG-22-V-A-IV': '2817', 'SG-22-V-A-V': '2818', 'SG-22-V-A-VI': '2819', 'SG-22-V-B-I': '2803', 'SG-22-V-B-II': '2804', 'SG-22-V-B-III': '2805', 'SG-22-V-B-IV': '2820', 'SG-22-V-B-V': '2821', 'SG-22-V-B-VI': '2822', 'SG-22-V-C-I': '2833', 'SG-22-V-C-II': '2834', 'SG-22-V-C-III': '2835', 'SG-22-V-C-IV': '2848', 'SG-22-V-C-V': '2849', 'SG-22-V-C-VI': '2850', 'SG-22-V-D-I': '2836', 'SG-22-V-D-II': '2837', 'SG-22-V-D-III': '2838', 'SG-22-V-D-IV': '2851', 'SG-22-V-D-V': '2852', 'SG-22-V-D-VI': '2853', 'SG-22-X-A-I': '2806', 'SG-22-X-A-II': '2807', 'SG-22-X-A-III': '2808', 'SG-22-X-A-IV': '2823', 'SG-22-X-A-V': '2824', 'SG-22-X-A-VI': '2825', 'SG-22-X-B-I': '2809', 'SG-22-X-B-II': '2810', 'SG-22-X-B-III': '2811', 'SG-22-X-B-IV': '2826', 'SG-22-X-B-V': '2827', 'SG-22-X-B-VI': '2828', 'SG-22-X-C-I': '2839', 'SG-22-X-C-II': '2840', 'SG-22-X-C-III': '2841', 'SG-22-X-C-IV': '2854', 'SG-22-X-C-V': '2855', 'SG-22-X-C-VI': '2856', 'SG-22-X-D-I': '2842', 'SG-22-X-D-II': '2843', 'SG-22-X-D-III': '2844', 'SG-22-X-D-IV': '2857', 'SG-22-X-D-V': '2858', 'SG-22-X-D-VI': '2859', 'SG-22-Y-A-I': '2860', 'SG-22-Y-A-II': '2861', 'SG-22-Y-A-III': '2862', 'SG-22-Y-A-IV': '2872', 'SG-22-Y-A-V': '2873', 'SG-22-Y-A-VI': '2874', 'SG-22-Y-B-I': '2863', 'SG-22-Y-B-II': '2864', 'SG-22-Y-B-III': '2865', 'SG-22-Y-B-IV': '2875', 'SG-22-Y-B-V': '2876', 'SG-22-Y-B-VI': '2877', 'SG-22-Y-C-I': '2884', 'SG-22-Y-C-II': '2885', 'SG-22-Y-C-III': '2886', 'SG-22-Y-C-IV': '2899', 'SG-22-Y-C-V': '2900', 'SG-22-Y-C-VI': '2901', 'SG-22-Y-D-I': '2887', 'SG-22-Y-D-II': '2888', 'SG-22-Y-D-III': '2889', 'SG-22-Y-D-IV': '2902', 'SG-22-Y-D-V': '2903', 'SG-22-Y-D-VI': '2904', 'SG-22-Z-A-I': '2866', 'SG-22-Z-A-II': '2867', 'SG-22-Z-A-III': '2868', 'SG-22-Z-A-IV': '2878', 'SG-22-Z-A-V': '2879', 'SG-22-Z-A-VI': '2880', 'SG-22-Z-B-I': '2869', 'SG-22-Z-B-II': '2870', 'SG-22-Z-B-III': '2871', 'SG-22-Z-B-IV': '2881', 'SG-22-Z-B-V': '2882', 'SG-22-Z-C-I': '2890', 'SG-22-Z-C-II': '2891', 'SG-22-Z-C-III': '2892', 'SG-22-Z-C-IV': '2905', 'SG-22-Z-C-V': '2906', 'SG-22-Z-C-VI': '2907', 'SG-22-Z-D-I': '2893', 'SG-22-Z-D-II': '2894', 'SG-22-Z-D-III': '2895', 'SG-22-Z-D-IV': '2908', 'SG-22-Z-D-V': '2909', 'SG-22-Z-D-VI': '2910', 'SI-22-V-A-I': '3023', 'SI-22-V-A-II': '3024', 'SI-22-V-A-III': '3025', 'SI-22-V-A-IV': '3028', 'SI-22-V-A-V': '3029', 'SI-22-V-A-VI': '3030', 'SI-22-V-B-I': '3026', 'SI-22-V-B-II': '3027', 'SI-22-V-B-IV': '3031', 'SI-22-V-C-I': '3032', 'SI-22-V-C-II': '3033', 'SI-22-V-C-III': '3034', 'SI-22-V-C-IV': '3035', 'SI-22-V-C-V': '3036', 'SI-22-V-C-VI': '3036A', 'NA-22-V-B-I': '30', 'NA-22-V-B-II': '31', 'NA-22-V-B-III': '32', 'NA-22-V-B-IV': '43', 'NA-22-V-B-V': '44', 'NA-22-V-B-VI': '45', 'NA-22-V-C-III': '59', 'NA-22-V-C-IV': '82', 'NA-22-V-C-V': '83', 'NA-22-V-C-VI': '84', 'NA-22-V-D-I': '60', 'NA-22-V-D-II': '61', 'NA-22-V-D-III': '62', 'NA-22-V-D-IV': '85', 'NA-22-V-D-V': '86', 'NA-22-V-D-VI': '87', 'NA-22-X-A-IV': '46', 'NA-22-X-C-I': '63', 'NA-22-X-C-IV': '88', 'NA-22-X-C-V': '89', 'NA-22-Y-A-I': '116', 'NA-22-Y-A-II': '117', 'NA-22-Y-A-III': '118', 'NA-22-Y-A-IV': '155', 'NA-22-Y-A-V': '156', 'NA-22-Y-A-VI': '157', 'NA-22-Y-B-I': '119', 'NA-22-Y-B-II': '120', 'NA-22-Y-B-III': '121', 'NA-22-Y-B-IV': '158', 'NA-22-Y-B-V': '159', 'NA-22-Y-B-VI': '160', 'NA-22-Y-C-I': '196', 'NA-22-Y-C-II': '197', 'NA-22-Y-C-III': '198', 'NA-22-Y-C-IV': '238', 'NA-22-Y-C-V': '239', 'NA-22-Y-C-VI': '240', 'NA-22-Y-D-I': '199', 'NA-22-Y-D-II': '200', 'NA-22-Y-D-III': '201', 'NA-22-Y-D-IV': '241', 'NA-22-Y-D-V': '242', 'NA-22-Y-D-VI': '243', 'NA-22-Z-A-I': '122', 'NA-22-Z-A-II': '123', 'NA-22-Z-A-III': '124', 'NA-22-Z-A-IV': '161', 'NA-22-Z-A-V': '162', 'NA-22-Z-A-VI': '163', 'NA-22-Z-C-I': '202', 'NA-22-Z-C-II': '203', 'NA-22-Z-C-III': '204', 'NA-22-Z-C-IV': '244', 'NA-22-Z-C-V': '245', 'NA-22-Z-C-VI': '246', 'NA-22-Z-D-IV': '247', 'SB-18-X-B-V': '753', 'SB-18-X-B-VI': '754', 'SB-18-X-D-II': '826', 'SB-18-X-D-III': '827', 'SB-18-X-D-IV': '902', 'SB-18-X-D-V': '903', 'SB-18-X-D-VI': '904', 'SB-18-Z-A-VI': '1057', 'SB-18-Z-B-I': '979', 'SB-18-Z-B-II': '980', 'SB-18-Z-B-III': '981', 'SB-18-Z-B-IV': '1058', 'SB-18-Z-B-V': '1059', 'SB-18-Z-B-VI': '1060', 'SB-18-Z-C-III': '1136', 'SB-18-Z-C-VI': '1215', 'SB-18-Z-D-I': '1137', 'SB-18-Z-D-II': '1138', 'SB-18-Z-D-III': '1139', 'SB-18-Z-D-IV': '1216', 'SB-18-Z-D-V': '1217', 'SB-18-Z-D-VI': '1218', 'SA-21-V-A-I': '269', 'SA-21-V-A-II': '270', 'SA-21-V-A-III': '271', 'SA-21-V-A-IV': '313', 'SA-21-V-A-V': '314', 'SA-21-V-A-VI': '315', 'SA-21-V-B-I': '272', 'SA-21-V-B-II': '273', 'SA-21-V-B-III': '274', 'SA-21-V-B-IV': '316', 'SA-21-V-B-V': '317', 'SA-21-V-B-VI': '318', 'SA-21-V-C-I': '361', 'SA-21-V-C-II': '362', 'SA-21-V-C-III': '363', 'SA-21-V-C-IV': '412', 'SA-21-V-C-V': '413', 'SA-21-V-C-VI': '414', 'SA-21-V-D-I': '364', 'SA-21-V-D-II': '365', 'SA-21-V-D-III': '366', 'SA-21-V-D-IV': '415', 'SA-21-V-D-V': '416', 'SA-21-V-D-VI': '417', 'SA-21-X-A-I': '275', 'SA-21-X-A-II': '276', 'SA-21-X-A-III': '277', 'SA-21-X-A-IV': '319', 'SA-21-X-A-V': '320', 'SA-21-X-A-VI': '321', 'SA-21-X-B-I': '278', 'SA-21-X-B-II': '279', 'SA-21-X-B-III': '280', 'SA-21-X-B-IV': '322', 'SA-21-X-B-V': '323', 'SA-21-X-B-VI': '324', 'SA-21-X-C-I': '367', 'SA-21-X-C-II': '368', 'SA-21-X-C-III': '369', 'SA-21-X-C-IV': '418', 'SA-21-X-C-V': '419', 'SA-21-X-C-VI': '420', 'SA-21-X-D-I': '370', 'SA-21-X-D-II': '371', 'SA-21-X-D-III': '372', 'SA-21-X-D-IV': '421', 'SA-21-X-D-V': '422', 'SA-21-X-D-VI': '423', 'SA-21-Y-A-I': '464', 'SA-21-Y-A-II': '465', 'SA-21-Y-A-III': '466', 'SA-21-Y-A-IV': '518', 'SA-21-Y-A-V': '519', 'SA-21-Y-A-VI': '520', 'SA-21-Y-B-I': '467', 'SA-21-Y-B-II': '468', 'SA-21-Y-B-III': '469', 'SA-21-Y-B-IV': '521', 'SA-21-Y-B-V': '522', 'SA-21-Y-B-VI': '523', 'SA-21-Y-C-I': '579', 'SA-21-Y-C-II': '580', 'SA-21-Y-C-III': '581', 'SA-21-Y-C-IV': '642', 'SA-21-Y-C-V': '643', 'SA-21-Y-C-VI': '644', 'SA-21-Y-D-I': '582', 'SA-21-Y-D-II': '583', 'SA-21-Y-D-III': '584', 'SA-21-Y-D-IV': '645', 'SA-21-Y-D-V': '646', 'SA-21-Y-D-VI': '647', 'SA-21-Z-A-I': '470', 'SA-21-Z-A-II': '471', 'SA-21-Z-A-III': '472', 'SA-21-Z-A-IV': '524', 'SA-21-Z-A-V': '525', 'SA-21-Z-A-VI': '526', 'SA-21-Z-B-I': '473', 'SA-21-Z-B-II': '474', 'SA-21-Z-B-III': '475', 'SA-21-Z-B-IV': '527', 'SA-21-Z-B-V': '528', 'SA-21-Z-B-VI': '529', 'SA-21-Z-C-I': '585', 'SA-21-Z-C-II': '586', 'SA-21-Z-C-III': '587', 'SA-21-Z-C-IV': '648', 'SA-21-Z-C-V': '649', 'SA-21-Z-C-VI': '650', 'SA-21-Z-D-I': '588', 'SA-21-Z-D-II': '589', 'SA-21-Z-D-III': '590', 'SA-21-Z-D-IV': '651', 'SA-21-Z-D-V': '652', 'SA-21-Z-D-VI': '653', 'SA-24-Y-A-IV': '554', 'SA-24-Y-A-V': '555', 'SA-24-Y-A-VI': '556', 'SA-24-Y-B-IV': '557', 'SA-24-Y-B-V': '558', 'SA-24-Y-C-I': '615', 'SA-24-Y-C-II': '616', 'SA-24-Y-C-III': '617', 'SA-24-Y-C-IV': '678', 'SA-24-Y-C-V': '679', 'SA-24-Y-C-VI': '680', 'SA-24-Y-D-I': '618', 'SA-24-Y-D-II': '619', 'SA-24-Y-D-III': '620', 'SA-24-Y-D-IV': '681', 'SA-24-Y-D-V': '682', 'SA-24-Y-D-VI': '683', 'SA-24-Z-C-I': '621', 'SA-24-Z-C-IV': '684', 'SA-24-Z-C-V': '685', 'SD-21-V-A-I': '1862', 'SD-21-V-A-II': '1863', 'SD-21-V-A-III': '1864', 'SD-21-V-A-IV': '1916', 'SD-21-V-A-V': '1917', 'SD-21-V-A-VI': '1918', 'SD-21-V-B-I': '1865', 'SD-21-V-B-II': '1866', 'SD-21-V-B-III': '1867', 'SD-21-V-B-IV': '1919', 'SD-21-V-B-V': '1920', 'SD-21-V-B-VI': '1921', 'SD-21-V-C-I': '1967', 'SD-21-V-C-II': '1968', 'SD-21-V-C-III': '1969', 'SD-21-V-C-IV': '2014', 'SD-21-V-C-V': '2015', 'SD-21-V-C-VI': '2016', 'SD-21-V-D-I': '1970', 'SD-21-V-D-II': '1971', 'SD-21-V-D-III': '1972', 'SD-21-V-D-IV': '2017', 'SD-21-V-D-V': '2018', 'SD-21-V-D-VI': '2019', 'SD-21-X-A-I': '1868', 'SD-21-X-A-II': '1869', 'SD-21-X-A-III': '1870', 'SD-21-X-A-IV': '1922', 'SD-21-X-A-V': '1923', 'SD-21-X-A-VI': '1924', 'SD-21-X-B-I': '1871', 'SD-21-X-B-II': '1872', 'SD-21-X-B-III': '1873', 'SD-21-X-B-IV': '1925', 'SD-21-X-B-V': '1926', 'SD-21-X-B-VI': '1927', 'SD-21-X-C-I': '1973', 'SD-21-X-C-II': '1974', 'SD-21-X-C-III': '1975', 'SD-21-X-C-IV': '2020', 'SD-21-X-C-V': '2021', 'SD-21-X-C-VI': '2022', 'SD-21-X-D-I': '1976', 'SD-21-X-D-II': '1977', 'SD-21-X-D-III': '1978', 'SD-21-X-D-IV': '2023', 'SD-21-X-D-V': '2024', 'SD-21-X-D-VI': '2025', 'SD-21-Y-A-I': '2058', 'SD-21-Y-A-II': '2059', 'SD-21-Y-A-III': '2060', 'SD-21-Y-A-IV': '2102', 'SD-21-Y-A-V': '2103', 'SD-21-Y-A-VI': '2104', 'SD-21-Y-B-I': '2061', 'SD-21-Y-B-II': '2062', 'SD-21-Y-B-III': '2063', 'SD-21-Y-B-IV': '2105', 'SD-21-Y-B-V': '2106', 'SD-21-Y-B-VI': '2107', 'SD-21-Y-C-I': '2147', 'SD-21-Y-C-II': '2148', 'SD-21-Y-C-III': '2149', 'SD-21-Y-C-IV': '2191', 'SD-21-Y-C-V': '2192', 'SD-21-Y-C-VI': '2193', 'SD-21-Y-D-I': '2150', 'SD-21-Y-D-II': '2151', 'SD-21-Y-D-III': '2152', 'SD-21-Y-D-IV': '2194', 'SD-21-Y-D-V': '2195', 'SD-21-Y-D-VI': '2196', 'SD-21-Z-A-I': '2064', 'SD-21-Z-A-II': '2065', 'SD-21-Z-A-III': '2066', 'SD-21-Z-A-IV': '2108', 'SD-21-Z-A-V': '2109', 'SD-21-Z-A-VI': '2110', 'SD-21-Z-B-I': '2067', 'SD-21-Z-B-II': '2068', 'SD-21-Z-B-III': '2069', 'SD-21-Z-B-IV': '2111', 'SD-21-Z-B-V': '2112', 'SD-21-Z-B-VI': '2113', 'SD-21-Z-C-I': '2153', 'SD-21-Z-C-II': '2154', 'SD-21-Z-C-III': '2155', 'SD-21-Z-C-IV': '2197', 'SD-21-Z-C-V': '2198', 'SD-21-Z-C-VI': '2199', 'SD-21-Z-D-I': '2156', 'SD-21-Z-D-II': '2157', 'SD-21-Z-D-III': '2158', 'SD-21-Z-D-IV': '2200', 'SD-21-Z-D-V': '2201', 'SD-21-Z-D-VI': '2202', 'SD-24-V-A-I': '1898', 'SD-24-V-A-II': '1899', 'SD-24-V-A-III': '1900', 'SD-24-V-A-IV': '1952', 'SD-24-V-A-V': '1953', 'SD-24-V-A-VI': '1954', 'SD-24-V-B-I': '1901', 'SD-24-V-B-II': '1902', 'SD-24-V-B-III': '1903', 'SD-24-V-B-IV': '1955', 'SD-24-V-B-V': '1956', 'SD-24-V-B-VI': '1957', 'SD-24-V-C-I': '2003', 'SD-24-V-C-II': '2004', 'SD-24-V-C-III': '2005', 'SD-24-V-C-IV': '2050', 'SD-24-V-C-V': '2051', 'SD-24-V-C-VI': '2052', 'SD-24-V-D-I': '2006', 'SD-24-V-D-II': '2007', 'SD-24-V-D-III': '2008', 'SD-24-V-D-IV': '2053', 'SD-24-V-D-V': '2054', 'SD-24-V-D-VI': '2055', 'SD-24-X-A-I': '1904', 'SD-24-X-A-II': '1905', 'SD-24-X-A-III': '1906', 'SD-24-X-A-IV': '1958', 'SD-24-X-A-V': '1959', 'SD-24-X-A-VI': '1960', 'SD-24-X-C-I': '2009', 'SD-24-X-C-IV': '2056', 'SD-24-Y-A-I': '2094', 'SD-24-Y-A-II': '2095', 'SD-24-Y-A-III': '2096', 'SD-24-Y-A-IV': '2138', 'SD-24-Y-A-V': '2139', 'SD-24-Y-A-VI': '2140', 'SD-24-Y-B-I': '2097', 'SD-24-Y-B-II': '2098', 'SD-24-Y-B-III': '2099', 'SD-24-Y-B-IV': '2141', 'SD-24-Y-B-V': '2142', 'SD-24-Y-B-VI': '2143', 'SD-24-Y-C-I': '2183', 'SD-24-Y-C-II': '2184', 'SD-24-Y-C-III': '2185', 'SD-24-Y-C-IV': '2227', 'SD-24-Y-C-V': '2228', 'SD-24-Y-C-VI': '2229', 'SD-24-Y-D-I': '2186', 'SD-24-Y-D-II': '2187', 'SD-24-Y-D-III': '2188', 'SD-24-Y-D-IV': '2230', 'SD-24-Y-D-V': '2231', 'SD-24-Y-D-VI': '2232', 'SD-24-Z-A-I': '2100', 'SD-24-Z-A-IV': '2144', 'SD-24-Z-C-I': '2189', 'SD-24-Z-C-IV': '2233', 'SC-25-V-A-I': '1370', 'SC-25-V-A-II': '1371', 'SC-25-V-A-III': '1372', 'SC-25-V-A-IV': '1448', 'SC-25-V-A-V': '1449', 'SC-25-V-A-VI': '1449-A', 'SC-25-V-C-I': '1525', 'SC-25-V-C-II': '1526', 'SC-25-V-C-IV': '1600', 'SH-21-V-D-VI': '2958', 'SH-21-X-A-III': '2911', 'SH-21-X-A-V': '2926', 'SH-21-X-A-VI': '2927', 'SH-21-X-B-I': '2912', 'SH-21-X-B-II': '2913', 'SH-21-X-B-III': '2914', 'SH-21-X-B-IV': '2928', 'SH-21-X-B-V': '2929', 'SH-21-X-B-VI': '2930', 'SH-21-X-C-I': '2942', 'SH-21-X-C-II': '2943', 'SH-21-X-C-III': '2944', 'SH-21-X-C-IV': '2959', 'SH-21-X-C-V': '2960', 'SH-21-X-C-VI': '2961', 'SH-21-X-D-I': '2945', 'SH-21-X-D-II': '2946', 'SH-21-X-D-III': '2947', 'SH-21-X-D-IV': '2962', 'SH-21-X-D-V': '2963', 'SH-21-X-D-VI': '2964', 'SH-21-Y-B-II': '2974', 'SH-21-Y-B-III': '2975', 'SH-21-Z-A-I': '2976', 'SH-21-Z-A-II': '2977', 'SH-21-Z-A-III': '2978', 'SH-21-Z-A-V': '2990', 'SH-21-Z-A-VI': '2991', 'SH-21-Z-B-I': '2979', 'SH-21-Z-B-II': '2980', 'SH-21-Z-B-III': '2981', 'SH-21-Z-B-IV': '2992', 'SH-21-Z-B-V': '2993', 'SH-21-Z-B-VI': '2994', 'SH-21-Z-C-II': '3003', 'SH-21-Z-C-III': '3004', 'SH-21-Z-D-I': '3005', 'SH-21-Z-D-II': '3006', 'SH-21-Z-D-III': '3007', 'SH-21-Z-D-V': '3015', 'SH-21-Z-D-VI': '3016', 'NB-22-Y-D-V': '17', 'NB-22-Y-D-VI': '18', 'SE-24-V-A-I': '2271', 'SE-24-V-A-II': '2272', 'SE-24-V-A-III': '2273', 'SE-24-V-A-IV': '2311', 'SE-24-V-A-V': '2312', 'SE-24-V-A-VI': '2313', 'SE-24-V-B-I': '2274', 'SE-24-V-B-II': '2275', 'SE-24-V-B-III': '2276', 'SE-24-V-B-IV': '2314', 'SE-24-V-B-V': '2315', 'SE-24-V-B-VI': '2316', 'SE-24-V-C-I': '2351', 'SE-24-V-C-II': '2352', 'SE-24-V-C-III': '2353', 'SE-24-V-C-IV': '2389', 'SE-24-V-C-V': '2390', 'SE-24-V-C-VI': '2391', 'SE-24-V-D-I': '2354', 'SE-24-V-D-II': '2355', 'SE-24-V-D-III': '2356', 'SE-24-V-D-IV': '2392', 'SE-24-V-D-V': '2393', 'SE-24-V-D-VI': '2394', 'SE-24-X-A-I': '2277', 'SE-24-X-A-IV': '2317', 'SE-24-Y-A-I': '2427', 'SE-24-Y-A-II': '2428', 'SE-24-Y-A-III': '2429', 'SE-24-Y-A-IV': '2464', 'SE-24-Y-A-V': '2465', 'SE-24-Y-A-VI': '2466', 'SE-24-Y-B-I': '2430', 'SE-24-Y-B-II': '2431', 'SE-24-Y-B-III': '2431A', 'SE-24-Y-B-IV': '2467', 'SE-24-Y-B-V': '2468', 'SE-24-Y-C-I': '2501', 'SE-24-Y-C-II': '2502', 'SE-24-Y-C-III': '2503', 'SE-24-Y-C-IV': '2539', 'SE-24-Y-C-V': '2540', 'SE-24-Y-C-VI': '2541', 'SE-24-Y-D-I': '2504', 'SE-24-Y-D-II': '2505', 'SE-24-Y-D-IV': '2542', 'SE-24-Y-D-V': '2543', 'SB-20-V-A-I': '697', 'SB-20-V-A-II': '698', 'SB-20-V-A-III': '699', 'SB-20-V-A-IV': '767', 'SB-20-V-A-V': '768', 'SB-20-V-A-VI': '769', 'SB-20-V-B-I': '700', 'SB-20-V-B-II': '701', 'SB-20-V-B-III': '702', 'SB-20-V-B-IV': '770', 'SB-20-V-B-V': '771', 'SB-20-V-B-VI': '772', 'SB-20-V-C-I': '840', 'SB-20-V-C-II': '841', 'SB-20-V-C-III': '842', 'SB-20-V-C-IV': '917', 'SB-20-V-C-V': '918', 'SB-20-V-C-VI': '919', 'SB-20-V-D-I': '843', 'SB-20-V-D-II': '844', 'SB-20-V-D-III': '845', 'SB-20-V-D-IV': '920', 'SB-20-V-D-V': '921', 'SB-20-V-D-VI': '922', 'SB-20-X-A-I': '703', 'SB-20-X-A-II': '704', 'SB-20-X-A-III': '705', 'SB-20-X-A-IV': '773', 'SB-20-X-A-V': '774', 'SB-20-X-A-VI': '775', 'SB-20-X-B-I': '706', 'SB-20-X-B-II': '707', 'SB-20-X-B-III': '708', 'SB-20-X-B-IV': '776', 'SB-20-X-B-V': '777', 'SB-20-X-B-VI': '778', 'SB-20-X-C-I': '846', 'SB-20-X-C-II': '847', 'SB-20-X-C-III': '848', 'SB-20-X-C-IV': '923', 'SB-20-X-C-V': '924', 'SB-20-X-C-VI': '925', 'SB-20-X-D-I': '849', 'SB-20-X-D-II': '850', 'SB-20-X-D-III': '851', 'SB-20-X-D-IV': '926', 'SB-20-X-D-V': '927', 'SB-20-X-D-VI': '928', 'SB-20-Y-A-I': '994', 'SB-20-Y-A-II': '995', 'SB-20-Y-A-III': '996', 'SB-20-Y-A-IV': '1073', 'SB-20-Y-A-V': '1074', 'SB-20-Y-A-VI': '1075', 'SB-20-Y-B-I': '997', 'SB-20-Y-B-II': '998', 'SB-20-Y-B-III': '999', 'SB-20-Y-B-IV': '1076', 'SB-20-Y-B-V': '1077', 'SB-20-Y-B-VI': '1078', 'SB-20-Y-C-I': '1152', 'SB-20-Y-C-II': '1153', 'SB-20-Y-C-III': '1154', 'SB-20-Y-C-IV': '1231', 'SB-20-Y-C-V': '1232', 'SB-20-Y-C-VI': '1233', 'SB-20-Y-D-I': '1155', 'SB-20-Y-D-II': '1156', 'SB-20-Y-D-III': '1157', 'SB-20-Y-D-IV': '1234', 'SB-20-Y-D-V': '1235', 'SB-20-Y-D-VI': '1236', 'SB-20-Z-A-I': '1000', 'SB-20-Z-A-II': '1001', 'SB-20-Z-A-III': '1002', 'SB-20-Z-A-IV': '1079', 'SB-20-Z-A-V': '1080', 'SB-20-Z-A-VI': '1081', 'SB-20-Z-B-I': '1003', 'SB-20-Z-B-II': '1004', 'SB-20-Z-B-III': '1005', 'SB-20-Z-B-IV': '1082', 'SB-20-Z-B-V': '1083', 'SB-20-Z-B-VI': '1084', 'SB-20-Z-C-I': '1158', 'SB-20-Z-C-II': '1159', 'SB-20-Z-C-III': '1160', 'SB-20-Z-C-IV': '1237', 'SB-20-Z-C-V': '1238', 'SB-20-Z-C-VI': '1239', 'SB-20-Z-D-I': '1161', 'SB-20-Z-D-II': '1162', 'SB-20-Z-D-III': '1163', 'SB-20-Z-D-IV': '1240', 'SB-20-Z-D-V': '1241', 'SB-20-Z-D-VI': '1242', 'SF-21-V-B-I': '2544', 'SF-21-V-B-II': '2545', 'SF-21-V-B-III': '2546', 'SF-21-V-B-IV': '2580-A', 'SF-21-V-B-V': '2581', 'SF-21-V-B-VI': '2582', 'SF-21-V-D-II': '2617', 'SF-21-V-D-III': '2618', 'SF-21-V-D-V': '2652', 'SF-21-V-D-VI': '2653', 'SF-21-X-A-I': '2547', 'SF-21-X-A-II': '2548', 'SF-21-X-A-III': '2549', 'SF-21-X-A-IV': '2583', 'SF-21-X-A-V': '2584', 'SF-21-X-A-VI': '2585', 'SF-21-X-B-I': '2550', 'SF-21-X-B-II': '2551', 'SF-21-X-B-III': '2552', 'SF-21-X-B-IV': '2586', 'SF-21-X-B-V': '2587', 'SF-21-X-B-VI': '2588', 'SF-21-X-C-I': '2619', 'SF-21-X-C-II': '2620', 'SF-21-X-C-III': '2621', 'SF-21-X-C-IV': '2654', 'SF-21-X-C-V': '2655', 'SF-21-X-C-VI': '2656', 'SF-21-X-D-I': '2622', 'SF-21-X-D-II': '2623', 'SF-21-X-D-III': '2624', 'SF-21-X-D-IV': '2657', 'SF-21-X-D-V': '2658', 'SF-21-X-D-VI': '2659', 'SF-21-Y-B-I': '2685-B', 'SF-21-Y-B-II': '2686', 'SF-21-Y-B-III': '2687', 'SF-21-Z-A-I': '2688', 'SF-21-Z-A-II': '2689', 'SF-21-Z-A-III': '2690', 'SF-21-Z-A-VI': '2720', 'SF-21-Z-B-I': '2691', 'SF-21-Z-B-II': '2692', 'SF-21-Z-B-III': '2693', 'SF-21-Z-B-IV': '2721', 'SF-21-Z-B-V': '2722', 'SF-21-Z-B-VI': '2723', 'SF-21-Z-C-III': '2749', 'SF-21-Z-C-VI': '2775', 'SF-21-Z-D-I': '2750', 'SF-21-Z-D-II': '2751', 'SF-21-Z-D-III': '2752', 'SF-21-Z-D-IV': '2776', 'SF-21-Z-D-V': '2777', 'SF-21-Z-D-VI': '2778', 'SB-19-V-A-I': '685A', 'SB-19-V-A-II': '686', 'SB-19-V-A-III': '687', 'SB-19-V-A-IV': '755', 'SB-19-V-A-V': '756', 'SB-19-V-A-VI': '757', 'SB-19-V-B-I': '688', 'SB-19-V-B-II': '689', 'SB-19-V-B-III': '690', 'SB-19-V-B-IV': '758', 'SB-19-V-B-V': '759', 'SB-19-V-B-VI': '760', 'SB-19-V-C-I': '828', 'SB-19-V-C-II': '829', 'SB-19-V-C-III': '830', 'SB-19-V-C-IV': '905', 'SB-19-V-C-V': '906', 'SB-19-V-C-VI': '907', 'SB-19-V-D-I': '831', 'SB-19-V-D-II': '832', 'SB-19-V-D-III': '833', 'SB-19-V-D-IV': '908', 'SB-19-V-D-V': '909', 'SB-19-V-D-VI': '910', 'SB-19-X-A-I': '691', 'SB-19-X-A-II': '692', 'SB-19-X-A-III': '693', 'SB-19-X-A-IV': '761', 'SB-19-X-A-V': '762', 'SB-19-X-A-VI': '763', 'SB-19-X-B-I': '694', 'SB-19-X-B-II': '695', 'SB-19-X-B-III': '696', 'SB-19-X-B-IV': '764', 'SB-19-X-B-V': '765', 'SB-19-X-B-VI': '766', 'SB-19-X-C-I': '834', 'SB-19-X-C-II': '835', 'SB-19-X-C-III': '836', 'SB-19-X-C-IV': '911', 'SB-19-X-C-V': '912', 'SB-19-X-C-VI': '913', 'SB-19-X-D-I': '837', 'SB-19-X-D-II': '838', 'SB-19-X-D-III': '839', 'SB-19-X-D-IV': '914', 'SB-19-X-D-V': '915', 'SB-19-X-D-VI': '916', 'SB-19-Y-A-I': '982', 'SB-19-Y-A-II': '983', 'SB-19-Y-A-III': '984', 'SB-19-Y-A-IV': '1061', 'SB-19-Y-A-V': '1062', 'SB-19-Y-A-VI': '1063', 'SB-19-Y-B-I': '985', 'SB-19-Y-B-II': '986', 'SB-19-Y-B-III': '987', 'SB-19-Y-B-IV': '1064', 'SB-19-Y-B-V': '1065', 'SB-19-Y-B-VI': '1066', 'SB-19-Y-C-I': '1140', 'SB-19-Y-C-II': '1141', 'SB-19-Y-C-III': '1142', 'SB-19-Y-C-IV': '1219', 'SB-19-Y-C-V': '1220', 'SB-19-Y-C-VI': '1221', 'SB-19-Y-D-I': '1143', 'SB-19-Y-D-II': '1144', 'SB-19-Y-D-III': '1145', 'SB-19-Y-D-IV': '1222', 'SB-19-Y-D-V': '1223', 'SB-19-Y-D-VI': '1224', 'SB-19-Z-A-I': '988', 'SB-19-Z-A-II': '989', 'SB-19-Z-A-III': '990', 'SB-19-Z-A-IV': '1067', 'SB-19-Z-A-V': '1068', 'SB-19-Z-A-VI': '1069', 'SB-19-Z-B-I': '991', 'SB-19-Z-B-II': '992', 'SB-19-Z-B-III': '993', 'SB-19-Z-B-IV': '1070', 'SB-19-Z-B-V': '1071', 'SB-19-Z-B-VI': '1072', 'SB-19-Z-C-I': '1146', 'SB-19-Z-C-II': '1147', 'SB-19-Z-C-III': '1148', 'SB-19-Z-C-IV': '1225', 'SB-19-Z-C-V': '1226', 'SB-19-Z-C-VI': '1227', 'SB-19-Z-D-I': '1149', 'SB-19-Z-D-II': '1150', 'SB-19-Z-D-III': '1151', 'SB-19-Z-D-IV': '1228', 'SB-19-Z-D-V': '1229', 'SB-19-Z-D-VI': '1230', 'SC-19-V-A-I': '1298', 'SC-19-V-A-II': '1299', 'SC-19-V-A-III': '1300', 'SC-19-V-A-IV': '1376', 'SC-19-V-A-V': '1377', 'SC-19-V-A-VI': '1378', 'SC-19-V-B-I': '1301', 'SC-19-V-B-II': '1302', 'SC-19-V-B-III': '1303', 'SC-19-V-B-IV': '1379', 'SC-19-V-B-V': '1380', 'SC-19-V-B-VI': '1381', 'SC-19-V-C-I': '1453', 'SC-19-V-C-II': '1454', 'SC-19-V-C-III': '1455', 'SC-19-V-C-IV': '1528', 'SC-19-V-C-V': '1529', 'SC-19-V-C-VI': '1530', 'SC-19-V-D-I': '1456', 'SC-19-V-D-II': '1457', 'SC-19-V-D-III': '1458', 'SC-19-V-D-IV': '1531', 'SC-19-V-D-V': '1532', 'SC-19-V-D-VI': '1533', 'SC-19-X-A-I': '1304', 'SC-19-X-A-II': '1305', 'SC-19-X-A-III': '1306', 'SC-19-X-A-IV': '1382', 'SC-19-X-A-V': '1383', 'SC-19-X-A-VI': '1384', 'SC-19-X-B-I': '1307', 'SC-19-X-B-II': '1308', 'SC-19-X-B-III': '1309', 'SC-19-X-B-IV': '1385', 'SC-19-X-B-V': '1386', 'SC-19-X-B-VI': '1387', 'SC-19-X-C-I': '1459', 'SC-19-X-C-II': '1460', 'SC-19-X-C-III': '1461', 'SC-19-X-C-IV': '1534', 'SC-19-X-C-V': '1535', 'SC-19-X-C-VI': '1536', 'SC-19-X-D-I': '1462', 'SC-19-X-D-II': '1463', 'SC-19-X-D-III': '1464', 'SC-19-X-D-IV': '1537', 'SC-19-X-D-V': '1538', 'SC-19-X-D-VI': '1539', 'SC-19-Y-A-III': '1601', 'SC-19-Y-A-VI': '1669', 'SC-19-Y-B-I': '1602', 'SC-19-Y-B-II': '1603', 'SC-19-Y-B-III': '1604', 'SC-19-Y-B-IV': '1670', 'SC-19-Y-B-V': '1671', 'SC-19-Y-B-VI': '1672', 'SC-19-Y-D-I': '1735', 'SC-19-Y-D-III': '1735A', 'SC-19-Z-A-I': '1605', 'SC-19-Z-A-II': '1606', 'SC-19-Z-A-III': '1607', 'SC-19-Z-A-IV': '1673', 'SC-19-Z-A-V': '1674', 'SC-19-Z-A-VI': '1675', 'SC-19-Z-B-I': '1608', 'SC-19-Z-B-II': '1609', 'SC-19-Z-C-I': '1736', 'SC-19-Z-C-II': '1737', 'SB-23-V-A-I': '733', 'SB-23-V-A-II': '734', 'SB-23-V-A-III': '735', 'SB-23-V-A-IV': '803', 'SB-23-V-A-V': '804', 'SB-23-V-A-VI': '805', 'SB-23-V-B-I': '736', 'SB-23-V-B-II': '737', 'SB-23-V-B-III': '738', 'SB-23-V-B-IV': '806', 'SB-23-V-B-V': '807', 'SB-23-V-B-VI': '808', 'SB-23-V-C-I': '876', 'SB-23-V-C-II': '877', 'SB-23-V-C-III': '878', 'SB-23-V-C-IV': '953', 'SB-23-V-C-V': '954', 'SB-23-V-C-VI': '955', 'SB-23-V-D-I': '879', 'SB-23-V-D-II': '880', 'SB-23-V-D-III': '881', 'SB-23-V-D-IV': '956', 'SB-23-V-D-V': '957', 'SB-23-V-D-VI': '958', 'SB-23-X-A-I': '739', 'SB-23-X-A-II': '740', 'SB-23-X-A-III': '741', 'SB-23-X-A-IV': '809', 'SB-23-X-A-V': '810', 'SB-23-X-A-VI': '811', 'SB-23-X-B-I': '742', 'SB-23-X-B-II': '743', 'SB-23-X-B-III': '744', 'SB-23-X-B-IV': '812', 'SB-23-X-B-V': '813', 'SB-23-X-B-VI': '814', 'SB-23-X-C-I': '882', 'SB-23-X-C-II': '883', 'SB-23-X-C-III': '884', 'SB-23-X-C-IV': '959', 'SB-23-X-C-V': '960', 'SB-23-X-C-VI': '961', 'SB-23-X-D-I': '885', 'SB-23-X-D-II': '886', 'SB-23-X-D-III': '887', 'SB-23-X-D-IV': '962', 'SB-23-X-D-V': '963', 'SB-23-X-D-VI': '964', 'SB-23-Y-A-I': '1030', 'SB-23-Y-A-II': '1031', 'SB-23-Y-A-III': '1032', 'SB-23-Y-A-IV': '1109', 'SB-23-Y-A-V': '1110', 'SB-23-Y-A-VI': '1111', 'SB-23-Y-B-I': '1033', 'SB-23-Y-B-II': '1034', 'SB-23-Y-B-III': '1035', 'SB-23-Y-B-IV': '1112', 'SB-23-Y-B-V': '1113', 'SB-23-Y-B-VI': '1114', 'SB-23-Y-C-I': '1188', 'SB-23-Y-C-II': '1189', 'SB-23-Y-C-III': '1190', 'SB-23-Y-C-IV': '1267', 'SB-23-Y-C-V': '1268', 'SB-23-Y-C-VI': '1269', 'SB-23-Y-D-I': '1191', 'SB-23-Y-D-II': '1192', 'SB-23-Y-D-III': '1193', 'SB-23-Y-D-IV': '1270', 'SB-23-Y-D-V': '1271', 'SB-23-Y-D-VI': '1272', 'SB-23-Z-A-I': '1036', 'SB-23-Z-A-II': '1037', 'SB-23-Z-A-III': '1038', 'SB-23-Z-A-IV': '1115', 'SB-23-Z-A-V': '1116', 'SB-23-Z-A-VI': '1117', 'SB-23-Z-B-I': '1039', 'SB-23-Z-B-II': '1040', 'SB-23-Z-B-III': '1041', 'SB-23-Z-B-IV': '1118', 'SB-23-Z-B-V': '1119', 'SB-23-Z-B-VI': '1120', 'SB-23-Z-C-I': '1194', 'SB-23-Z-C-II': '1195', 'SB-23-Z-C-III': '1196', 'SB-23-Z-C-IV': '1273', 'SB-23-Z-C-V': '1274', 'SB-23-Z-C-VI': '1275', 'SB-23-Z-D-I': '1197', 'SB-23-Z-D-II': '1198', 'SB-23-Z-D-III': '1199', 'SB-23-Z-D-IV': '1276', 'SB-23-Z-D-V': '1277', 'SB-23-Z-D-VI': '1278', 'SD-23-V-A-I': '1886', 'SD-23-V-A-II': '1887', 'SD-23-V-A-III': '1888', 'SD-23-V-A-IV': '1940', 'SD-23-V-A-V': '1941', 'SD-23-V-A-VI': '1942', 'SD-23-V-B-I': '1889', 'SD-23-V-B-II': '1890', 'SD-23-V-B-III': '1891', 'SD-23-V-B-IV': '1943', 'SD-23-V-B-V': '1944', 'SD-23-V-B-VI': '1945', 'SD-23-V-C-I': '1991', 'SD-23-V-C-II': '1992', 'SD-23-V-C-III': '1993', 'SD-23-V-C-IV': '2038', 'SD-23-V-C-V': '2039', 'SD-23-V-C-VI': '2040', 'SD-23-V-D-I': '1994', 'SD-23-V-D-II': '1995', 'SD-23-V-D-III': '1996', 'SD-23-V-D-IV': '2041', 'SD-23-V-D-V': '2042', 'SD-23-V-D-VI': '2043', 'SD-23-X-A-I': '1892', 'SD-23-X-A-II': '1893', 'SD-23-X-A-III': '1894', 'SD-23-X-A-IV': '1946', 'SD-23-X-A-V': '1947', 'SD-23-X-A-VI': '1948', 'SD-23-X-B-I': '1895', 'SD-23-X-B-II': '1896', 'SD-23-X-B-III': '1897', 'SD-23-X-B-IV': '1949', 'SD-23-X-B-V': '1950', 'SD-23-X-B-VI': '1951', 'SD-23-X-C-I': '1997', 'SD-23-X-C-II': '1998', 'SD-23-X-C-III': '1999', 'SD-23-X-C-IV': '2044', 'SD-23-X-C-V': '2045', 'SD-23-X-C-VI': '2046', 'SD-23-X-D-I': '2000', 'SD-23-X-D-II': '2001', 'SD-23-X-D-III': '2002', 'SD-23-X-D-IV': '2047', 'SD-23-X-D-V': '2048', 'SD-23-X-D-VI': '2049', 'SD-23-Y-A-I': '2082', 'SD-23-Y-A-II': '2083', 'SD-23-Y-A-III': '2084', 'SD-23-Y-A-IV': '2126', 'SD-23-Y-A-V': '2127', 'SD-23-Y-A-VI': '2128', 'SD-23-Y-B-I': '2085', 'SD-23-Y-B-II': '2086', 'SD-23-Y-B-III': '2087', 'SD-23-Y-B-IV': '2129', 'SD-23-Y-B-V': '2130', 'SD-23-Y-B-VI': '2131', 'SD-23-Y-C-I': '2171', 'SD-23-Y-C-II': '2172', 'SD-23-Y-C-III': '2173', 'SD-23-Y-C-IV': '2215', 'SD-23-Y-C-V': '2216', 'SD-23-Y-C-VI': '2217', 'SD-23-Y-D-I': '2174', 'SD-23-Y-D-II': '2175', 'SD-23-Y-D-III': '2176', 'SD-23-Y-D-IV': '2218', 'SD-23-Y-D-V': '2219', 'SD-23-Y-D-VI': '2220', 'SD-23-Z-A-I': '2088', 'SD-23-Z-A-II': '2089', 'SD-23-Z-A-III': '2090', 'SD-23-Z-A-IV': '2132', 'SD-23-Z-A-V': '2133', 'SD-23-Z-A-VI': '2134', 'SD-23-Z-B-I': '2091', 'SD-23-Z-B-II': '2092', 'SD-23-Z-B-III': '2093', 'SD-23-Z-B-IV': '2135', 'SD-23-Z-B-V': '2136', 'SD-23-Z-B-VI': '2137', 'SD-23-Z-C-I': '2177', 'SD-23-Z-C-II': '2178', 'SD-23-Z-C-III': '2179', 'SD-23-Z-C-IV': '2221', 'SD-23-Z-C-V': '2222', 'SD-23-Z-C-VI': '2223', 'SD-23-Z-D-I': '2180', 'SD-23-Z-D-II': '2181', 'SD-23-Z-D-III': '2182', 'SD-23-Z-D-IV': '2224', 'SD-23-Z-D-V': '2225', 'SD-23-Z-D-VI': '2226', 'SB-22-V-A-I': '721', 'SB-22-V-A-II': '722', 'SB-22-V-A-III': '723', 'SB-22-V-A-IV': '791', 'SB-22-V-A-V': '792', 'SB-22-V-A-VI': '793', 'SB-22-V-B-I': '724', 'SB-22-V-B-II': '725', 'SB-22-V-B-III': '726', 'SB-22-V-B-IV': '794', 'SB-22-V-B-V': '795', 'SB-22-V-B-VI': '796', 'SB-22-V-C-I': '864', 'SB-22-V-C-II': '865', 'SB-22-V-C-III': '866', 'SB-22-V-C-IV': '941', 'SB-22-V-C-V': '942', 'SB-22-V-C-VI': '943', 'SB-22-V-D-I': '867', 'SB-22-V-D-II': '868', 'SB-22-V-D-III': '869', 'SB-22-V-D-IV': '944', 'SB-22-V-D-V': '945', 'SB-22-V-D-VI': '946', 'SB-22-X-A-I': '727', 'SB-22-X-A-II': '728', 'SB-22-X-A-III': '729', 'SB-22-X-A-IV': '797', 'SB-22-X-A-V': '798', 'SB-22-X-A-VI': '799', 'SB-22-X-B-I': '730', 'SB-22-X-B-II': '731', 'SB-22-X-B-III': '732', 'SB-22-X-B-IV': '800', 'SB-22-X-B-V': '801', 'SB-22-X-B-VI': '802', 'SB-22-X-C-I': '870', 'SB-22-X-C-II': '871', 'SB-22-X-C-III': '872', 'SB-22-X-C-IV': '947', 'SB-22-X-C-V': '948', 'SB-22-X-C-VI': '949', 'SB-22-X-D-I': '873', 'SB-22-X-D-II': '874', 'SB-22-X-D-III': '875', 'SB-22-X-D-IV': '950', 'SB-22-X-D-V': '951', 'SB-22-X-D-VI': '952', 'SB-22-Y-A-I': '1018', 'SB-22-Y-A-II': '1019', 'SB-22-Y-A-III': '1020', 'SB-22-Y-A-IV': '1097', 'SB-22-Y-A-V': '1098', 'SB-22-Y-A-VI': '1099', 'SB-22-Y-B-I': '1021', 'SB-22-Y-B-II': '1022', 'SB-22-Y-B-III': '1023', 'SB-22-Y-B-IV': '1100', 'SB-22-Y-B-V': '1101', 'SB-22-Y-B-VI': '1102', 'SB-22-Y-C-I': '1176', 'SB-22-Y-C-II': '1177', 'SB-22-Y-C-III': '1178', 'SB-22-Y-C-IV': '1255', 'SB-22-Y-C-V': '1256', 'SB-22-Y-C-VI': '1257', 'SB-22-Y-D-I': '1179', 'SB-22-Y-D-II': '1180', 'SB-22-Y-D-III': '1181', 'SB-22-Y-D-IV': '1258', 'SB-22-Y-D-V': '1259', 'SB-22-Y-D-VI': '1260', 'SB-22-Z-A-I': '1024', 'SB-22-Z-A-II': '1025', 'SB-22-Z-A-III': '1026', 'SB-22-Z-A-IV': '1103', 'SB-22-Z-A-V': '1104', 'SB-22-Z-A-VI': '1105', 'SB-22-Z-B-I': '1027', 'SB-22-Z-B-II': '1028', 'SB-22-Z-B-III': '1029', 'SB-22-Z-B-IV': '1106', 'SB-22-Z-B-V': '1107', 'SB-22-Z-B-VI': '1108', 'SB-22-Z-C-I': '1182', 'SB-22-Z-C-II': '1183', 'SB-22-Z-C-III': '1184', 'SB-22-Z-C-IV': '1261', 'SB-22-Z-C-V': '1262', 'SB-22-Z-C-VI': '1263', 'SB-22-Z-D-I': '1185', 'SB-22-Z-D-II': '1186', 'SB-22-Z-D-III': '1187', 'SB-22-Z-D-IV': '1264', 'SB-22-Z-D-V': '1265', 'SB-22-Z-D-VI': '1266', 'SA-20-V-A-I': '257', 'SA-20-V-A-II': '258', 'SA-20-V-A-III': '259', 'SA-20-V-A-IV': '301', 'SA-20-V-A-V': '302', 'SA-20-V-A-VI': '303', 'SA-20-V-B-I': '260', 'SA-20-V-B-II': '261', 'SA-20-V-B-III': '262', 'SA-20-V-B-IV': '304', 'SA-20-V-B-V': '305', 'SA-20-V-B-VI': '306', 'SA-20-V-C-I': '349', 'SA-20-V-C-II': '350', 'SA-20-V-C-III': '351', 'SA-20-V-C-IV': '400', 'SA-20-V-C-V': '401', 'SA-20-V-C-VI': '402', 'SA-20-V-D-I': '352', 'SA-20-V-D-II': '353', 'SA-20-V-D-III': '354', 'SA-20-V-D-IV': '403', 'SA-20-V-D-V': '404', 'SA-20-V-D-VI': '405', 'SA-20-X-A-I': '263', 'SA-20-X-A-II': '264', 'SA-20-X-A-III': '265', 'SA-20-X-A-IV': '307', 'SA-20-X-A-V': '308', 'SA-20-X-A-VI': '309', 'SA-20-X-B-I': '266', 'SA-20-X-B-II': '267', 'SA-20-X-B-III': '268', 'SA-20-X-B-IV': '310', 'SA-20-X-B-V': '311', 'SA-20-X-B-VI': '312', 'SA-20-X-C-I': '355', 'SA-20-X-C-II': '356', 'SA-20-X-C-III': '357', 'SA-20-X-C-IV': '406', 'SA-20-X-C-V': '407', 'SA-20-X-C-VI': '408', 'SA-20-X-D-I': '358', 'SA-20-X-D-II': '359', 'SA-20-X-D-III': '360', 'SA-20-X-D-IV': '409', 'SA-20-X-D-V': '410', 'SA-20-X-D-VI': '411', 'SA-20-Y-A-I': '452', 'SA-20-Y-A-II': '453', 'SA-20-Y-A-III': '454', 'SA-20-Y-A-IV': '506', 'SA-20-Y-A-V': '507', 'SA-20-Y-A-VI': '508', 'SA-20-Y-B-I': '455', 'SA-20-Y-B-II': '456', 'SA-20-Y-B-III': '457', 'SA-20-Y-B-IV': '509', 'SA-20-Y-B-V': '510', 'SA-20-Y-B-VI': '511', 'SA-20-Y-C-I': '567', 'SA-20-Y-C-II': '568', 'SA-20-Y-C-III': '569', 'SA-20-Y-C-IV': '630', 'SA-20-Y-C-V': '631', 'SA-20-Y-C-VI': '632', 'SA-20-Y-D-I': '570', 'SA-20-Y-D-II': '571', 'SA-20-Y-D-III': '572', 'SA-20-Y-D-IV': '633', 'SA-20-Y-D-V': '634', 'SA-20-Y-D-VI': '635', 'SA-20-Z-A-I': '458', 'SA-20-Z-A-II': '459', 'SA-20-Z-A-III': '460', 'SA-20-Z-A-IV': '512', 'SA-20-Z-A-V': '513', 'SA-20-Z-A-VI': '514', 'SA-20-Z-B-I': '461', 'SA-20-Z-B-II': '462', 'SA-20-Z-B-III': '463', 'SA-20-Z-B-IV': '515', 'SA-20-Z-B-V': '516', 'SA-20-Z-B-VI': '517', 'SA-20-Z-C-I': '573', 'SA-20-Z-C-II': '574', 'SA-20-Z-C-III': '575', 'SA-20-Z-C-IV': '636', 'SA-20-Z-C-V': '637', 'SA-20-Z-C-VI': '638', 'SA-20-Z-D-I': '576', 'SA-20-Z-D-II': '577', 'SA-20-Z-D-III': '578', 'SA-20-Z-D-IV': '639', 'SA-20-Z-D-V': '640', 'SA-20-Z-D-VI': '641', 'SA-22-V-A-I': '281', 'SA-22-V-A-II': '282', 'SA-22-V-A-III': '283', 'SA-22-V-A-IV': '325', 'SA-22-V-A-V': '326', 'SA-22-V-A-VI': '327', 'SA-22-V-B-I': '284', 'SA-22-V-B-II': '285', 'SA-22-V-B-III': '286', 'SA-22-V-B-IV': '328', 'SA-22-V-B-V': '329', 'SA-22-V-B-VI': '330', 'SA-22-V-C-I': '373', 'SA-22-V-C-II': '374', 'SA-22-V-C-III': '375', 'SA-22-V-C-IV': '424', 'SA-22-V-C-V': '425', 'SA-22-V-C-VI': '426', 'SA-22-V-D-I': '376', 'SA-22-V-D-II': '377', 'SA-22-V-D-III': '378', 'SA-22-V-D-IV': '427', 'SA-22-V-D-V': '428', 'SA-22-V-D-VI': '429', 'SA-22-X-A-I': '287', 'SA-22-X-A-II': '288', 'SA-22-X-A-III': '289', 'SA-22-X-A-IV': '331', 'SA-22-X-A-V': '332', 'SA-22-X-A-VI': '333', 'SA-22-X-B-I': '290', 'SA-22-X-B-II': '291', 'SA-22-X-B-III': '292', 'SA-22-X-B-IV': '334', 'SA-22-X-B-V': '335', 'SA-22-X-B-VI': '336', 'SA-22-X-C-I': '379', 'SA-22-X-C-II': '380', 'SA-22-X-C-III': '381', 'SA-22-X-C-IV': '430', 'SA-22-X-C-V': '431', 'SA-22-X-C-VI': '432', 'SA-22-X-D-I': '382', 'SA-22-X-D-II': '383', 'SA-22-X-D-III': '384', 'SA-22-X-D-IV': '433', 'SA-22-X-D-V': '434', 'SA-22-X-D-VI': '435', 'SA-22-Y-A-I': '476', 'SA-22-Y-A-II': '477', 'SA-22-Y-A-III': '478', 'SA-22-Y-A-IV': '530', 'SA-22-Y-A-V': '531', 'SA-22-Y-A-VI': '532', 'SA-22-Y-B-I': '479', 'SA-22-Y-B-II': '480', 'SA-22-Y-B-III': '481', 'SA-22-Y-B-IV': '533', 'SA-22-Y-B-V': '534', 'SA-22-Y-B-VI': '535', 'SA-22-Y-C-I': '591', 'SA-22-Y-C-II': '592', 'SA-22-Y-C-III': '593', 'SA-22-Y-C-IV': '654', 'SA-22-Y-C-V': '655', 'SA-22-Y-C-VI': '656', 'SA-22-Y-D-I': '594', 'SA-22-Y-D-II': '595', 'SA-22-Y-D-III': '596', 'SA-22-Y-D-IV': '657', 'SA-22-Y-D-V': '658', 'SA-22-Y-D-VI': '659', 'SA-22-Z-A-I': '482', 'SA-22-Z-A-II': '483', 'SA-22-Z-A-III': '484', 'SA-22-Z-A-IV': '536', 'SA-22-Z-A-V': '537', 'SA-22-Z-A-VI': '538', 'SA-22-Z-B-I': '485', 'SA-22-Z-B-II': '486', 'SA-22-Z-B-III': '487', 'SA-22-Z-B-IV': '539', 'SA-22-Z-B-V': '540', 'SA-22-Z-B-VI': '541', 'SA-22-Z-C-I': '597', 'SA-22-Z-C-II': '598', 'SA-22-Z-C-III': '599', 'SA-22-Z-C-IV': '660', 'SA-22-Z-C-V': '661', 'SA-22-Z-C-VI': '662', 'SA-22-Z-D-I': '600', 'SA-22-Z-D-II': '601', 'SA-22-Z-D-III': '602', 'SA-22-Z-D-IV': '663', 'SA-22-Z-D-V': '664', 'SA-22-Z-D-VI': '665', 'SB-24-V-A-I': '745', 'SB-24-V-A-II': '746', 'SB-24-V-A-III': '747', 'SB-24-V-A-IV': '815', 'SB-24-V-A-V': '816', 'SB-24-V-A-VI': '817', 'SB-24-V-B-I': '748', 'SB-24-V-B-II': '749', 'SB-24-V-B-III': '750', 'SB-24-V-B-IV': '818', 'SB-24-V-B-V': '819', 'SB-24-V-B-VI': '820', 'SB-24-V-C-I': '888', 'SB-24-V-C-II': '889', 'SB-24-V-C-III': '890', 'SB-24-V-C-IV': '965', 'SB-24-V-C-V': '966', 'SB-24-V-C-VI': '967', 'SB-24-V-D-I': '891', 'SB-24-V-D-II': '892', 'SB-24-V-D-III': '893', 'SB-24-V-D-IV': '968', 'SB-24-V-D-V': '969', 'SB-24-V-D-VI': '970', 'SB-24-X-A-I': '751', 'SB-24-X-A-II': '752', 'SB-24-X-A-III': '752-A', 'SB-24-X-A-IV': '821', 'SB-24-X-A-V': '822', 'SB-24-X-A-VI': '823', 'SB-24-X-B-IV': '824', 'SB-24-X-B-V': '825', 'SB-24-X-C-I': '894', 'SB-24-X-C-II': '895', 'SB-24-X-C-III': '896', 'SB-24-X-C-IV': '971', 'SB-24-X-C-V': '972', 'SB-24-X-C-VI': '973', 'SB-24-X-D-I': '897', 'SB-24-X-D-II': '898', 'SB-24-X-D-III': '899', 'SB-24-X-D-IV': '974', 'SB-24-X-D-V': '975', 'SB-24-X-D-VI': '976', 'SB-24-Y-A-I': '1042', 'SB-24-Y-A-II': '1043', 'SB-24-Y-A-III': '1044', 'SB-24-Y-A-IV': '1121', 'SB-24-Y-A-V': '1122', 'SB-24-Y-A-VI': '1123', 'SB-24-Y-B-I': '1045', 'SB-24-Y-B-II': '1046', 'SB-24-Y-B-III': '1047', 'SB-24-Y-B-IV': '1124', 'SB-24-Y-B-V': '1125', 'SB-24-Y-B-VI': '1126', 'SB-24-Y-C-I': '1200', 'SB-24-Y-C-II': '1201', 'SB-24-Y-C-III': '1202', 'SB-24-Y-C-IV': '1279', 'SB-24-Y-C-V': '1280', 'SB-24-Y-C-VI': '1281', 'SB-24-Y-D-I': '1203', 'SB-24-Y-D-II': '1204', 'SB-24-Y-D-III': '1205', 'SB-24-Y-D-IV': '1282', 'SB-24-Y-D-V': '1283', 'SB-24-Y-D-VI': '1284', 'SB-24-Z-A-I': '1048', 'SB-24-Z-A-II': '1049', 'SB-24-Z-A-III': '1050', 'SB-24-Z-A-IV': '1127', 'SB-24-Z-A-V': '1128', 'SB-24-Z-A-VI': '1129', 'SB-24-Z-B-I': '1051', 'SB-24-Z-B-II': '1052', 'SB-24-Z-B-III': '1053', 'SB-24-Z-B-IV': '1130', 'SB-24-Z-B-V': '1131', 'SB-24-Z-B-VI': '1132', 'SB-24-Z-C-I': '1206', 'SB-24-Z-C-II': '1207', 'SB-24-Z-C-III': '1208', 'SB-24-Z-C-IV': '1285', 'SB-24-Z-C-V': '1286', 'SB-24-Z-C-VI': '1287', 'SB-24-Z-D-I': '1209', 'SB-24-Z-D-II': '1210', 'SB-24-Z-D-III': '1211', 'SB-24-Z-D-IV': '1288', 'SB-24-Z-D-V': '1289', 'SB-24-Z-D-VI': '1290', 'SF-22-V-A-I': '2553', 'SF-22-V-A-II': '2554', 'SF-22-V-A-III': '2555', 'SF-22-V-A-IV': '2589', 'SF-22-V-A-V': '2590', 'SF-22-V-A-VI': '2591', 'SF-22-V-B-I': '2556', 'SF-22-V-B-II': '2557', 'SF-22-V-B-III': '2558', 'SF-22-V-B-IV': '2592', 'SF-22-V-B-V': '2593', 'SF-22-V-B-VI': '2594', 'SF-22-V-C-I': '2625', 'SF-22-V-C-II': '2626', 'SF-22-V-C-III': '2627', 'SF-22-V-C-IV': '2660', 'SF-22-V-C-V': '2661', 'SF-22-V-C-VI': '2662', 'SF-22-V-D-I': '2628', 'SF-22-V-D-II': '2629', 'SF-22-V-D-III': '2630', 'SF-22-V-D-IV': '2663', 'SF-22-V-D-V': '2664', 'SF-22-V-D-VI': '2665', 'SF-22-X-A-I': '2559', 'SF-22-X-A-II': '2560', 'SF-22-X-A-III': '2561', 'SF-22-X-A-IV': '2595', 'SF-22-X-A-V': '2596', 'SF-22-X-A-VI': '2597', 'SF-22-X-B-I': '2562', 'SF-22-X-B-II': '2563', 'SF-22-X-B-III': '2564', 'SF-22-X-B-IV': '2598', 'SF-22-X-B-V': '2599', 'SF-22-X-B-VI': '2600', 'SF-22-X-C-I': '2631', 'SF-22-X-C-II': '2632', 'SF-22-X-C-III': '2633', 'SF-22-X-C-IV': '2666', 'SF-22-X-C-V': '2667', 'SF-22-X-C-VI': '2668', 'SF-22-X-D-I': '2634', 'SF-22-X-D-II': '2635', 'SF-22-X-D-III': '2636', 'SF-22-X-D-IV': '2669', 'SF-22-X-D-V': '2670', 'SF-22-X-D-VI': '2671', 'SF-22-Y-A-I': '2694', 'SF-22-Y-A-II': '2695', 'SF-22-Y-A-III': '2696', 'SF-22-Y-A-IV': '2724', 'SF-22-Y-A-V': '2725', 'SF-22-Y-A-VI': '2726', 'SF-22-Y-B-I': '2697', 'SF-22-Y-B-II': '2698', 'SF-22-Y-B-III': '2699', 'SF-22-Y-B-IV': '2727', 'SF-22-Y-B-V': '2728', 'SF-22-Y-B-VI': '2729', 'SF-22-Y-C-I': '2753', 'SF-22-Y-C-II': '2754', 'SF-22-Y-C-III': '2755', 'SF-22-Y-C-IV': '2779', 'SF-22-Y-C-V': '2780', 'SF-22-Y-C-VI': '2781', 'SF-22-Y-D-I': '2756', 'SF-22-Y-D-II': '2757', 'SF-22-Y-D-III': '2758', 'SF-22-Y-D-IV': '2782', 'SF-22-Y-D-V': '2783', 'SF-22-Y-D-VI': '2784', 'SF-22-Z-A-I': '2700', 'SF-22-Z-A-II': '2701', 'SF-22-Z-A-III': '2702', 'SF-22-Z-A-IV': '2730', 'SF-22-Z-A-V': '2731', 'SF-22-Z-A-VI': '2732', 'SF-22-Z-B-I': '2703', 'SF-22-Z-B-II': '2704', 'SF-22-Z-B-III': '2705', 'SF-22-Z-B-IV': '2733', 'SF-22-Z-B-V': '2734', 'SF-22-Z-B-VI': '2735', 'SF-22-Z-C-I': '2759', 'SF-22-Z-C-II': '2760', 'SF-22-Z-C-III': '2761', 'SF-22-Z-C-IV': '2785', 'SF-22-Z-C-V': '2786', 'SF-22-Z-C-VI': '2787', 'SF-22-Z-D-I': '2762', 'SF-22-Z-D-II': '2763', 'SF-22-Z-D-III': '2764', 'SF-22-Z-D-IV': '2788', 'SF-22-Z-D-V': '2789', 'SF-22-Z-D-VI': '2790', 'SA-23-V-A-IV': '337', 'SA-23-V-A-V': '338', 'SA-23-V-A-VI': '339', 'SA-23-V-B-IV': '340', 'SA-23-V-C-I': '385', 'SA-23-V-C-II': '386', 'SA-23-V-C-III': '387', 'SA-23-V-C-IV': '436', 'SA-23-V-C-V': '437', 'SA-23-V-C-VI': '438', 'SA-23-V-D-I': '388', 'SA-23-V-D-II': '389', 'SA-23-V-D-III': '390', 'SA-23-V-D-IV': '439', 'SA-23-V-D-V': '440', 'SA-23-V-D-VI': '441', 'SA-23-X-C-I': '391', 'SA-23-X-C-IV': '442', 'SA-23-X-C-V': '443', 'SA-23-Y-A-I': '488', 'SA-23-Y-A-II': '489', 'SA-23-Y-A-III': '490', 'SA-23-Y-A-IV': '542', 'SA-23-Y-A-V': '543', 'SA-23-Y-A-VI': '544', 'SA-23-Y-B-I': '491', 'SA-23-Y-B-II': '492', 'SA-23-Y-B-III': '493', 'SA-23-Y-B-IV': '545', 'SA-23-Y-B-V': '546', 'SA-23-Y-B-VI': '547', 'SA-23-Y-C-I': '603', 'SA-23-Y-C-II': '604', 'SA-23-Y-C-III': '605', 'SA-23-Y-C-IV': '666', 'SA-23-Y-C-V': '667', 'SA-23-Y-C-VI': '668', 'SA-23-Y-D-I': '606', 'SA-23-Y-D-II': '607', 'SA-23-Y-D-III': '608', 'SA-23-Y-D-IV': '669', 'SA-23-Y-D-V': '670', 'SA-23-Y-D-VI': '671', 'SA-23-Z-A-I': '494', 'SA-23-Z-A-II': '495', 'SA-23-Z-A-III': '495-A', 'SA-23-Z-A-IV': '548', 'SA-23-Z-A-V': '549', 'SA-23-Z-A-VI': '550', 'SA-23-Z-B-I': '496', 'SA-23-Z-B-II': '497', 'SA-23-Z-B-IV': '551', 'SA-23-Z-B-V': '552', 'SA-23-Z-B-VI': '553', 'SA-23-Z-C-I': '609', 'SA-23-Z-C-II': '610', 'SA-23-Z-C-III': '611', 'SA-23-Z-C-IV': '672', 'SA-23-Z-C-V': '673', 'SA-23-Z-C-VI': '674', 'SA-23-Z-D-I': '612', 'SA-23-Z-D-II': '613', 'SA-23-Z-D-III': '614', 'SA-23-Z-D-IV': '675', 'SA-23-Z-D-V': '676', 'SA-23-Z-D-VI': '677', 'SG-21-X-B-I': '2797', 'SG-21-X-B-II': '2798', 'SG-21-X-B-III': '2799', 'SG-21-X-B-VI': '2816', 'SG-21-X-D-II': '2831', 'SG-21-X-D-III': '2832', 'SG-21-X-D-V': '2846', 'SG-21-X-D-VI': '2847', 'SG-21-Z-D-II': '2882-A', 'SG-21-Z-D-III': '2883', 'SG-21-Z-D-IV': '2896', 'SG-21-Z-D-V': '2897', 'SG-21-Z-D-VI': '2898', 'SC-24-V-A-I': '1358', 'SC-24-V-A-II': '1359', 'SC-24-V-A-III': '1360', 'SC-24-V-A-IV': '1436', 'SC-24-V-A-V': '1437', 'SC-24-V-A-VI': '1438', 'SC-24-V-B-I': '1361', 'SC-24-V-B-II': '1362', 'SC-24-V-B-III': '1363', 'SC-24-V-B-IV': '1439', 'SC-24-V-B-V': '1440', 'SC-24-V-B-VI': '1441', 'SC-24-V-C-I': '1513', 'SC-24-V-C-II': '1514', 'SC-24-V-C-III': '1515', 'SC-24-V-C-IV': '1588', 'SC-24-V-C-V': '1589', 'SC-24-V-C-VI': '1590', 'SC-24-V-D-I': '1516', 'SC-24-V-D-II': '1517', 'SC-24-V-D-III': '1518', 'SC-24-V-D-IV': '1591', 'SC-24-V-D-V': '1592', 'SC-24-V-D-VI': '1593', 'SC-24-X-A-I': '1364', 'SC-24-X-A-II': '1365', 'SC-24-X-A-III': '1366', 'SC-24-X-A-IV': '1442', 'SC-24-X-A-V': '1443', 'SC-24-X-A-VI': '1444', 'SC-24-X-B-I': '1367', 'SC-24-X-B-II': '1368', 'SC-24-X-B-III': '1369', 'SC-24-X-B-IV': '1445', 'SC-24-X-B-V': '1446', 'SC-24-X-B-VI': '1447', 'SC-24-X-C-I': '1519', 'SC-24-X-C-II': '1520', 'SC-24-X-C-III': '1521', 'SC-24-X-C-IV': '1594', 'SC-24-X-C-V': '1595', 'SC-24-X-C-VI': '1596', 'SC-24-X-D-I': '1522', 'SC-24-X-D-II': '1523', 'SC-24-X-D-III': '1524', 'SC-24-X-D-IV': '1597', 'SC-24-X-D-V': '1598', 'SC-24-X-D-VI': '1599', 'SC-24-Y-A-I': '1657', 'SC-24-Y-A-II': '1658', 'SC-24-Y-A-III': '1659', 'SC-24-Y-A-IV': '1723', 'SC-24-Y-A-V': '1724', 'SC-24-Y-A-VI': '1725', 'SC-24-Y-B-I': '1660', 'SC-24-Y-B-II': '1661', 'SC-24-Y-B-III': '1662', 'SC-24-Y-B-IV': '1726', 'SC-24-Y-B-V': '1727', 'SC-24-Y-B-VI': '1728', 'SC-24-Y-C-I': '1785', 'SC-24-Y-C-II': '1786', 'SC-24-Y-C-III': '1787', 'SC-24-Y-C-IV': '1842', 'SC-24-Y-C-V': '1843', 'SC-24-Y-C-VI': '1844', 'SC-24-Y-D-I': '1788', 'SC-24-Y-D-II': '1789', 'SC-24-Y-D-III': '1790', 'SC-24-Y-D-IV': '1845', 'SC-24-Y-D-V': '1846', 'SC-24-Y-D-VI': '1847', 'SC-24-Z-A-I': '1663', 'SC-24-Z-A-II': '1664', 'SC-24-Z-A-III': '1665', 'SC-24-Z-A-IV': '1729', 'SC-24-Z-A-V': '1730', 'SC-24-Z-A-VI': '1731', 'SC-24-Z-B-I': '1666', 'SC-24-Z-B-II': '1667', 'SC-24-Z-B-III': '1668', 'SC-24-Z-B-IV': '1732', 'SC-24-Z-B-V': '1733', 'SC-24-Z-B-VI': '1734', 'SC-24-Z-C-I': '1791', 'SC-24-Z-C-II': '1792', 'SC-24-Z-C-III': '1793', 'SC-24-Z-C-IV': '1848', 'SC-24-Z-C-V': '1849', 'SC-24-Z-C-VI': '1850', 'SC-24-Z-D-I': '1794', 'SC-24-Z-D-IV': '1851', 'SC-23-V-A-I': '1346', 'SC-23-V-A-II': '1347', 'SC-23-V-A-III': '1348', 'SC-23-V-A-IV': '1424', 'SC-23-V-A-V': '1425', 'SC-23-V-A-VI': '1426', 'SC-23-V-B-I': '1349', 'SC-23-V-B-II': '1350', 'SC-23-V-B-III': '1351', 'SC-23-V-B-IV': '1427', 'SC-23-V-B-V': '1428', 'SC-23-V-B-VI': '1429', 'SC-23-V-C-I': '1501', 'SC-23-V-C-II': '1502', 'SC-23-V-C-III': '1503', 'SC-23-V-C-IV': '1576', 'SC-23-V-C-V': '1577', 'SC-23-V-C-VI': '1578', 'SC-23-V-D-I': '1504', 'SC-23-V-D-II': '1505', 'SC-23-V-D-III': '1506', 'SC-23-V-D-IV': '1579', 'SC-23-V-D-V': '1580', 'SC-23-V-D-VI': '1581', 'SC-23-X-A-I': '1352', 'SC-23-X-A-II': '1353', 'SC-23-X-A-III': '1354', 'SC-23-X-A-IV': '1430', 'SC-23-X-A-V': '1431', 'SC-23-X-A-VI': '1432', 'SC-23-X-B-I': '1355', 'SC-23-X-B-II': '1356', 'SC-23-X-B-III': '1357', 'SC-23-X-B-IV': '1433', 'SC-23-X-B-V': '1434', 'SC-23-X-B-VI': '1435', 'SC-23-X-C-I': '1507', 'SC-23-X-C-II': '1508', 'SC-23-X-C-III': '1509', 'SC-23-X-C-IV': '1582', 'SC-23-X-C-V': '1583', 'SC-23-X-C-VI': '1584', 'SC-23-X-D-I': '1510', 'SC-23-X-D-II': '1511', 'SC-23-X-D-III': '1512', 'SC-23-X-D-IV': '1585', 'SC-23-X-D-V': '1586', 'SC-23-X-D-VI': '1587', 'SC-23-Y-A-I': '1645', 'SC-23-Y-A-II': '1646', 'SC-23-Y-A-III': '1647', 'SC-23-Y-A-IV': '1711', 'SC-23-Y-A-V': '1712', 'SC-23-Y-A-VI': '1713', 'SC-23-Y-B-I': '1648', 'SC-23-Y-B-II': '1649', 'SC-23-Y-B-III': '1650', 'SC-23-Y-B-IV': '1714', 'SC-23-Y-B-V': '1715', 'SC-23-Y-B-VI': '1716', 'SC-23-Y-C-I': '1773', 'SC-23-Y-C-II': '1774', 'SC-23-Y-C-III': '1775', 'SC-23-Y-C-IV': '1830', 'SC-23-Y-C-V': '1831', 'SC-23-Y-C-VI': '1832', 'SC-23-Y-D-I': '1776', 'SC-23-Y-D-II': '1777', 'SC-23-Y-D-III': '1778', 'SC-23-Y-D-IV': '1833', 'SC-23-Y-D-V': '1834', 'SC-23-Y-D-VI': '1835', 'SC-23-Z-A-I': '1651', 'SC-23-Z-A-II': '1652', 'SC-23-Z-A-III': '1653', 'SC-23-Z-A-IV': '1717', 'SC-23-Z-A-V': '1718', 'SC-23-Z-A-VI': '1719', 'SC-23-Z-B-I': '1654', 'SC-23-Z-B-II': '1655', 'SC-23-Z-B-III': '1656', 'SC-23-Z-B-IV': '1720', 'SC-23-Z-B-V': '1721', 'SC-23-Z-B-VI': '1722', 'SC-23-Z-C-I': '1779', 'SC-23-Z-C-II': '1780', 'SC-23-Z-C-III': '1781', 'SC-23-Z-C-IV': '1836', 'SC-23-Z-C-V': '1837', 'SC-23-Z-C-VI': '1838', 'SC-23-Z-D-I': '1782', 'SC-23-Z-D-II': '1783', 'SC-23-Z-D-III': '1784', 'SC-23-Z-D-IV': '1839', 'SC-23-Z-D-V': '1840', 'SC-23-Z-D-VI': '1841', 'NA-19-X-C-VI': '64', 'NA-19-X-D-IV': '65', 'NA-19-Y-B-II': '90', 'NA-19-Y-B-III': '91', 'NA-19-Y-B-V': '125', 'NA-19-Y-B-VI': '126', 'NA-19-Y-D-I': '163A', 'NA-19-Y-D-II': '164', 'NA-19-Y-D-III': '165', 'NA-19-Y-D-IV': '205', 'NA-19-Y-D-V': '206', 'NA-19-Y-D-VI': '207', 'NA-19-Z-A-I': '92', 'NA-19-Z-A-II': '93', 'NA-19-Z-A-III': '94', 'NA-19-Z-A-IV': '127', 'NA-19-Z-A-V': '128', 'NA-19-Z-A-VI': '129', 'NA-19-Z-B-I': '95', 'NA-19-Z-B-IV': '130', 'NA-19-Z-B-V': '131', 'NA-19-Z-C-I': '166', 'NA-19-Z-C-II': '167', 'NA-19-Z-C-III': '168', 'NA-19-Z-C-IV': '208', 'NA-19-Z-C-V': '209', 'NA-19-Z-C-VI': '210', 'NA-19-Z-D-I': '169', 'NA-19-Z-D-II': '170', 'NA-19-Z-D-III': '171', 'NA-19-Z-D-IV': '211', 'NA-19-Z-D-V': '212', 'NA-19-Z-D-VI': '213', 'SC-20-V-A-I': '1310', 'SC-20-V-A-II': '1311', 'SC-20-V-A-III': '1312', 'SC-20-V-A-IV': '1388', 'SC-20-V-A-V': '1389', 'SC-20-V-A-VI': '1390', 'SC-20-V-B-I': '1313', 'SC-20-V-B-II': '1314', 'SC-20-V-B-III': '1315', 'SC-20-V-B-IV': '1391', 'SC-20-V-B-V': '1392', 'SC-20-V-B-VI': '1393', 'SC-20-V-C-I': '1465', 'SC-20-V-C-II': '1466', 'SC-20-V-C-III': '1467', 'SC-20-V-C-IV': '1540', 'SC-20-V-C-V': '1541', 'SC-20-V-C-VI': '1542', 'SC-20-V-D-I': '1468', 'SC-20-V-D-II': '1469', 'SC-20-V-D-III': '1470', 'SC-20-V-D-IV': '1543', 'SC-20-V-D-V': '1544', 'SC-20-V-D-VI': '1545', 'SC-20-X-A-I': '1316', 'SC-20-X-A-II': '1317', 'SC-20-X-A-III': '1318', 'SC-20-X-A-IV': '1394', 'SC-20-X-A-V': '1395', 'SC-20-X-A-VI': '1396', 'SC-20-X-B-I': '1319', 'SC-20-X-B-II': '1320', 'SC-20-X-B-III': '1321', 'SC-20-X-B-IV': '1397', 'SC-20-X-B-V': '1398', 'SC-20-X-B-VI': '1399', 'SC-20-X-C-I': '1471', 'SC-20-X-C-II': '1472', 'SC-20-X-C-III': '1473', 'SC-20-X-C-IV': '1546', 'SC-20-X-C-V': '1547', 'SC-20-X-C-VI': '1548', 'SC-20-X-D-I': '1474', 'SC-20-X-D-II': '1475', 'SC-20-X-D-III': '1476', 'SC-20-X-D-IV': '1549', 'SC-20-X-D-V': '1550', 'SC-20-X-D-VI': '1551', 'SC-20-Y-A-II': '1610', 'SC-20-Y-A-III': '1611', 'SC-20-Y-A-V': '1676', 'SC-20-Y-A-VI': '1677', 'SC-20-Y-B-I': '1612', 'SC-20-Y-B-II': '1613', 'SC-20-Y-B-III': '1614', 'SC-20-Y-B-IV': '1678', 'SC-20-Y-B-V': '1679', 'SC-20-Y-B-VI': '1680', 'SC-20-Y-C-II': '1738', 'SC-20-Y-C-III': '1739', 'SC-20-Y-C-V': '1795', 'SC-20-Y-C-VI': '1796', 'SC-20-Y-D-I': '1740', 'SC-20-Y-D-II': '1741', 'SC-20-Y-D-III': '1742', 'SC-20-Y-D-IV': '1797', 'SC-20-Y-D-V': '1798', 'SC-20-Y-D-VI': '1799', 'SC-20-Z-A-I': '1615', 'SC-20-Z-A-II': '1616', 'SC-20-Z-A-III': '1617', 'SC-20-Z-A-IV': '1681', 'SC-20-Z-A-V': '1682', 'SC-20-Z-A-VI': '1683', 'SC-20-Z-B-I': '1618', 'SC-20-Z-B-II': '1619', 'SC-20-Z-B-III': '1620', 'SC-20-Z-B-IV': '1684', 'SC-20-Z-B-V': '1685', 'SC-20-Z-B-VI': '1686', 'SC-20-Z-C-I': '1743', 'SC-20-Z-C-II': '1744', 'SC-20-Z-C-III': '1745', 'SC-20-Z-C-IV': '1800', 'SC-20-Z-C-V': '1801', 'SC-20-Z-C-VI': '1802', 'SC-20-Z-D-I': '1746', 'SC-20-Z-D-II': '1747', 'SC-20-Z-D-III': '1748', 'SC-20-Z-D-IV': '1803', 'SC-20-Z-D-V': '1804', 'SC-20-Z-D-VI': '1805', 'SA-19-V-B-I': '248', 'SA-19-V-B-II': '249', 'SA-19-V-B-III': '250', 'SA-19-V-B-V': '293', 'SA-19-V-B-VI': '294', 'SA-19-V-D-II': '341', 'SA-19-V-D-III': '342', 'SA-19-V-D-V': '392', 'SA-19-V-D-VI': '393', 'SA-19-X-A-I': '251', 'SA-19-X-A-II': '252', 'SA-19-X-A-III': '253', 'SA-19-X-A-IV': '295', 'SA-19-X-A-V': '296', 'SA-19-X-A-VI': '297', 'SA-19-X-B-I': '254', 'SA-19-X-B-II': '255', 'SA-19-X-B-III': '256', 'SA-19-X-B-IV': '298', 'SA-19-X-B-V': '299', 'SA-19-X-B-VI': '300', 'SA-19-X-C-I': '343', 'SA-19-X-C-II': '344', 'SA-19-X-C-III': '345', 'SA-19-X-C-IV': '394', 'SA-19-X-C-V': '395', 'SA-19-X-C-VI': '396', 'SA-19-X-D-I': '346', 'SA-19-X-D-II': '347', 'SA-19-X-D-III': '348', 'SA-19-X-D-IV': '397', 'SA-19-X-D-V': '398', 'SA-19-X-D-VI': '399', 'SA-19-Y-B-II': '444', 'SA-19-Y-B-III': '445', 'SA-19-Y-B-V': '498', 'SA-19-Y-B-VI': '499', 'SA-19-Y-D-II': '559', 'SA-19-Y-D-III': '560', 'SA-19-Y-D-V': '622', 'SA-19-Y-D-VI': '623', 'SA-19-Z-A-I': '446', 'SA-19-Z-A-II': '447', 'SA-19-Z-A-III': '448', 'SA-19-Z-A-IV': '500', 'SA-19-Z-A-V': '501', 'SA-19-Z-A-VI': '502', 'SA-19-Z-B-I': '449', 'SA-19-Z-B-II': '450', 'SA-19-Z-B-III': '451', 'SA-19-Z-B-IV': '503', 'SA-19-Z-B-V': '504', 'SA-19-Z-B-VI': '505', 'SA-19-Z-C-I': '561', 'SA-19-Z-C-II': '562', 'SA-19-Z-C-III': '563', 'SA-19-Z-C-IV': '624', 'SA-19-Z-C-V': '625', 'SA-19-Z-C-VI': '626', 'SA-19-Z-D-I': '564', 'SA-19-Z-D-II': '565', 'SA-19-Z-D-III': '566', 'SA-19-Z-D-IV': '627', 'SA-19-Z-D-V': '628', 'SA-19-Z-D-VI': '629', 'SD-20-V-A-III': '1852', 'SD-20-V-B-I': '1853', 'SD-20-V-B-II': '1854', 'SD-20-V-B-III': '1855', 'SD-20-V-B-IV': '1907', 'SD-20-V-B-V': '1908', 'SD-20-V-B-VI': '1909', 'SD-20-X-A-I': '1856', 'SD-20-X-A-II': '1857', 'SD-20-X-A-III': '1858', 'SD-20-X-A-IV': '1910', 'SD-20-X-A-V': '1911', 'SD-20-X-A-VI': '1912', 'SD-20-X-B-I': '1859', 'SD-20-X-B-II': '1860', 'SD-20-X-B-III': '1861', 'SD-20-X-B-IV': '1913', 'SD-20-X-B-V': '1914', 'SD-20-X-B-VI': '1915', 'SD-20-X-C-I': '1961', 'SD-20-X-C-II': '1962', 'SD-20-X-C-III': '1963', 'SD-20-X-C-VI': '2010', 'SD-20-X-D-I': '1964', 'SD-20-X-D-II': '1965', 'SD-20-X-D-III': '1966', 'SD-20-X-D-IV': '2011', 'SD-20-X-D-V': '2012', 'SD-20-X-D-VI': '2013', 'SD-20-Z-B-III': '2057', 'SD-20-Z-B-VI': '2101', 'SD-20-Z-D-II': '2145', 'SD-20-Z-D-III': '2146', 'SD-20-Z-D-VI': '2190', 'NA-20-V-A-III': '19', 'NA-20-V-B-I': '20', 'NA-20-V-B-II': '21', 'NA-20-V-B-III': '22', 'NA-20-V-B-IV': '33', 'NA-20-V-B-V': '34', 'NA-20-V-B-VI': '35', 'NA-20-V-D-I': '47', 'NA-20-V-D-II': '48', 'NA-20-V-D-III': '49', 'NA-20-V-D-IV': '66', 'NA-20-V-D-V': '67', 'NA-20-V-D-VI': '68', 'NA-20-X-A-I': '23', 'NA-20-X-A-II': '24', 'NA-20-X-A-III': '25', 'NA-20-X-A-IV': '36', 'NA-20-X-A-V': '37', 'NA-20-X-A-VI': '38', 'NA-20-X-B-I': '26', 'NA-20-X-B-II': '27', 'NA-20-X-B-III': '28', 'NA-20-X-B-IV': '39', 'NA-20-X-B-V': '40', 'NA-20-X-B-VI': '41', 'NA-20-X-C-I': '50', 'NA-20-X-C-II': '51', 'NA-20-X-C-III': '52', 'NA-20-X-C-IV': '69', 'NA-20-X-C-V': '70', 'NA-20-X-C-VI': '71', 'NA-20-X-D-I': '53', 'NA-20-X-D-II': '54', 'NA-20-X-D-III': '55', 'NA-20-X-D-IV': '72', 'NA-20-X-D-V': '73', 'NA-20-X-D-VI': '74', 'NA-20-Y-A-V': '132', 'NA-20-Y-A-VI': '133', 'NA-20-Y-B-I': '96', 'NA-20-Y-B-II': '97', 'NA-20-Y-B-III': '98', 'NA-20-Y-B-IV': '134', 'NA-20-Y-B-V': '135', 'NA-20-Y-B-VI': '136', 'NA-20-Y-C-I': '172', 'NA-20-Y-C-II': '173', 'NA-20-Y-C-III': '174', 'NA-20-Y-C-IV': '214', 'NA-20-Y-C-V': '215', 'NA-20-Y-C-VI': '216', 'NA-20-Y-D-I': '175', 'NA-20-Y-D-II': '176', 'NA-20-Y-D-III': '177', 'NA-20-Y-D-IV': '217', 'NA-20-Y-D-V': '218', 'NA-20-Y-D-VI': '219', 'NA-20-Z-A-I': '99', 'NA-20-Z-A-II': '100', 'NA-20-Z-A-III': '101', 'NA-20-Z-A-IV': '137', 'NA-20-Z-A-V': '138', 'NA-20-Z-A-VI': '139', 'NA-20-Z-B-I': '102', 'NA-20-Z-B-II': '103', 'NA-20-Z-B-III': '104', 'NA-20-Z-B-IV': '140', 'NA-20-Z-B-V': '141', 'NA-20-Z-B-VI': '142', 'NA-20-Z-C-I': '178', 'NA-20-Z-C-II': '179', 'NA-20-Z-C-III': '180', 'NA-20-Z-C-IV': '220', 'NA-20-Z-C-V': '221', 'NA-20-Z-C-VI': '222', 'NA-20-Z-D-I': '181', 'NA-20-Z-D-II': '182', 'NA-20-Z-D-III': '183', 'NA-20-Z-D-IV': '223', 'NA-20-Z-D-V': '224', 'NA-20-Z-D-VI': '225'}

mi2inom = {'709': 'SB-21-V-A-I', '710': 'SB-21-V-A-II', '711': 'SB-21-V-A-III', '779': 'SB-21-V-A-IV', '780': 'SB-21-V-A-V', '781': 'SB-21-V-A-VI', '712': 'SB-21-V-B-I', '713': 'SB-21-V-B-II', '714': 'SB-21-V-B-III', '782': 'SB-21-V-B-IV', '783': 'SB-21-V-B-V', '784': 'SB-21-V-B-VI', '852': 'SB-21-V-C-I', '853': 'SB-21-V-C-II', '854': 'SB-21-V-C-III', '929': 'SB-21-V-C-IV', '930': 'SB-21-V-C-V', '931': 'SB-21-V-C-VI', '855': 'SB-21-V-D-I', '856': 'SB-21-V-D-II', '857': 'SB-21-V-D-III', '932': 'SB-21-V-D-IV', '933': 'SB-21-V-D-V', '934': 'SB-21-V-D-VI', '715': 'SB-21-X-A-I', '716': 'SB-21-X-A-II', '717': 'SB-21-X-A-III', '785': 'SB-21-X-A-IV', '786': 'SB-21-X-A-V', '787': 'SB-21-X-A-VI', '718': 'SB-21-X-B-I', '719': 'SB-21-X-B-II', '720': 'SB-21-X-B-III', '788': 'SB-21-X-B-IV', '789': 'SB-21-X-B-V', '790': 'SB-21-X-B-VI', '858': 'SB-21-X-C-I', '859': 'SB-21-X-C-II', '860': 'SB-21-X-C-III', '935': 'SB-21-X-C-IV', '936': 'SB-21-X-C-V', '937': 'SB-21-X-C-VI', '861': 'SB-21-X-D-I', '862': 'SB-21-X-D-II', '863': 'SB-21-X-D-III', '938': 'SB-21-X-D-IV', '939': 'SB-21-X-D-V', '940': 'SB-21-X-D-VI', '1006': 'SB-21-Y-A-I', '1007': 'SB-21-Y-A-II', '1008': 'SB-21-Y-A-III', '1085': 'SB-21-Y-A-IV', '1086': 'SB-21-Y-A-V', '1087': 'SB-21-Y-A-VI', '1009': 'SB-21-Y-B-I', '1010': 'SB-21-Y-B-II', '1011': 'SB-21-Y-B-III', '1088': 'SB-21-Y-B-IV', '1089': 'SB-21-Y-B-V', '1090': 'SB-21-Y-B-VI', '1164': 'SB-21-Y-C-I', '1165': 'SB-21-Y-C-II', '1166': 'SB-21-Y-C-III', '1243': 'SB-21-Y-C-IV', '1244': 'SB-21-Y-C-V', '1245': 'SB-21-Y-C-VI', '1167': 'SB-21-Y-D-I', '1168': 'SB-21-Y-D-II', '1169': 'SB-21-Y-D-III', '1246': 'SB-21-Y-D-IV', '1247': 'SB-21-Y-D-V', '1248': 'SB-21-Y-D-VI', '1012': 'SB-21-Z-A-I', '1013': 'SB-21-Z-A-II', '1014': 'SB-21-Z-A-III', '1091': 'SB-21-Z-A-IV', '1092': 'SB-21-Z-A-V', '1093': 'SB-21-Z-A-VI', '1015': 'SB-21-Z-B-I', '1016': 'SB-21-Z-B-II', '1017': 'SB-21-Z-B-III', '1094': 'SB-21-Z-B-IV', '1095': 'SB-21-Z-B-V', '1096': 'SB-21-Z-B-VI', '1170': 'SB-21-Z-C-I', '1171': 'SB-21-Z-C-II', '1172': 'SB-21-Z-C-III', '1249': 'SB-21-Z-C-IV', '1250': 'SB-21-Z-C-V', '1251': 'SB-21-Z-C-VI', '1173': 'SB-21-Z-D-I', '1174': 'SB-21-Z-D-II', '1175': 'SB-21-Z-D-III', '1252': 'SB-21-Z-D-IV', '1253': 'SB-21-Z-D-V', '1254': 'SB-21-Z-D-VI', '2A': 'NB-21-Y-A-IV', '6': 'NB-21-Y-C-I', '16': 'NB-21-Y-C-IV', '7': 'NB-20-Y-C-VI', '8': 'NB-20-Y-D-IV', '9': 'NB-20-Y-D-V', '1': 'NB-20-Z-B-V', '2': 'NB-20-Z-B-VI', '10': 'NB-20-Z-C-IV', '11': 'NB-20-Z-C-V', '12': 'NB-20-Z-C-VI', '3': 'NB-20-Z-D-I', '4': 'NB-20-Z-D-II', '5': 'NB-20-Z-D-III', '13': 'NB-20-Z-D-IV', '14': 'NB-20-Z-D-V', '15': 'NB-20-Z-D-VI', '2577': 'SF-24-V-A-I', '2578': 'SF-24-V-A-II', '2579': 'SF-24-V-A-III', '2613': 'SF-24-V-A-IV', '2614': 'SF-24-V-A-V', '2615': 'SF-24-V-A-VI', '2580': 'SF-24-V-B-I', '2616': 'SF-24-V-B-IV', '2649': 'SF-24-V-C-I', '2650': 'SF-24-V-C-II', '2651': 'SF-24-V-C-III', '2684': 'SF-24-V-C-IV', '2685': 'SF-24-V-C-V', '2685A': 'SF-24-V-C-VI', '2718': 'SF-24-Y-A-I', '2719': 'SF-24-Y-A-II', '2748': 'SF-24-Y-A-IV', '900': 'SB-25-V-C-I', '901': 'SB-25-V-C-II', '977': 'SB-25-V-C-IV', '978': 'SB-25-V-C-V', '1054': 'SB-25-Y-A-I', '1055': 'SB-25-Y-A-II', '1056': 'SB-25-Y-A-III', '1133': 'SB-25-Y-A-IV', '1134': 'SB-25-Y-A-V', '1135': 'SB-25-Y-A-VI', '1212': 'SB-25-Y-C-I', '1213': 'SB-25-Y-C-II', '1214': 'SB-25-Y-C-III', '1291': 'SB-25-Y-C-IV', '1292': 'SB-25-Y-C-V', '1293': 'SB-25-Y-C-VI', '2915': 'SH-22-V-A-I', '2916': 'SH-22-V-A-II', '2917': 'SH-22-V-A-III', '2931': 'SH-22-V-A-IV', '2932': 'SH-22-V-A-V', '2933': 'SH-22-V-A-VI', '2918': 'SH-22-V-B-I', '2919': 'SH-22-V-B-II', '2920': 'SH-22-V-B-III', '2934': 'SH-22-V-B-IV', '2935': 'SH-22-V-B-V', '2936': 'SH-22-V-B-VI', '2948': 'SH-22-V-C-I', '2949': 'SH-22-V-C-II', '2950': 'SH-22-V-C-III', '2965': 'SH-22-V-C-IV', '2966': 'SH-22-V-C-V', '2967': 'SH-22-V-C-VI', '2951': 'SH-22-V-D-I', '2952': 'SH-22-V-D-II', '2953': 'SH-22-V-D-III', '2968': 'SH-22-V-D-IV', '2969': 'SH-22-V-D-V', '2970': 'SH-22-V-D-VI', '2921': 'SH-22-X-A-I', '2922': 'SH-22-X-A-II', '2923': 'SH-22-X-A-III', '2937': 'SH-22-X-A-IV', '2938': 'SH-22-X-A-V', '2939': 'SH-22-X-A-VI', '2924': 'SH-22-X-B-I', '2925': 'SH-22-X-B-II', '2940': 'SH-22-X-B-IV', '2941': 'SH-22-X-B-V', '2954': 'SH-22-X-C-I', '2955': 'SH-22-X-C-II', '2956': 'SH-22-X-C-III', '2971': 'SH-22-X-C-IV', '2972': 'SH-22-X-C-V', '2973': 'SH-22-X-C-VI', '2957': 'SH-22-X-D-I', '2982': 'SH-22-Y-A-I', '2983': 'SH-22-Y-A-II', '2984': 'SH-22-Y-A-III', '2995': 'SH-22-Y-A-IV', '2996': 'SH-22-Y-A-V', '2997': 'SH-22-Y-A-VI', '2985': 'SH-22-Y-B-I', '2986': 'SH-22-Y-B-II', '2987': 'SH-22-Y-B-III', '2998': 'SH-22-Y-B-IV', '2999': 'SH-22-Y-B-V', '3000': 'SH-22-Y-B-VI', '3008': 'SH-22-Y-C-I', '3009': 'SH-22-Y-C-II', '3010': 'SH-22-Y-C-III', '3017': 'SH-22-Y-C-IV', '3018': 'SH-22-Y-C-V', '3019': 'SH-22-Y-C-VI', '3011': 'SH-22-Y-D-I', '3012': 'SH-22-Y-D-II', '3013': 'SH-22-Y-D-III', '3020': 'SH-22-Y-D-IV', '3021': 'SH-22-Y-D-V', '3022': 'SH-22-Y-D-VI', '2988': 'SH-22-Z-A-I', '2989': 'SH-22-Z-A-II', '3001': 'SH-22-Z-A-IV', '3002': 'SH-22-Z-A-V', '3014': 'SH-22-Z-C-I', '29': 'NA-21-V-A-I', '42': 'NA-21-V-A-IV', '56': 'NA-21-V-C-I', '75': 'NA-21-V-C-IV', '76': 'NA-21-V-D-VI', '57': 'NA-21-X-C-III', '77': 'NA-21-X-C-V', '78': 'NA-21-X-C-VI', '58': 'NA-21-X-D-I', '58A': 'NA-21-X-D-II', '79': 'NA-21-X-D-IV', '80': 'NA-21-X-D-V', '81': 'NA-21-X-D-VI', '105': 'NA-21-Y-A-I', '106': 'NA-21-Y-A-II', '143': 'NA-21-Y-A-IV', '144': 'NA-21-Y-A-V', '145': 'NA-21-Y-A-VI', '107': 'NA-21-Y-B-I', '108': 'NA-21-Y-B-II', '109': 'NA-21-Y-B-III', '146': 'NA-21-Y-B-IV', '147': 'NA-21-Y-B-V', '148': 'NA-21-Y-B-VI', '184': 'NA-21-Y-C-I', '185': 'NA-21-Y-C-II', '186': 'NA-21-Y-C-III', '226': 'NA-21-Y-C-IV', '227': 'NA-21-Y-C-V', '228': 'NA-21-Y-C-VI', '187': 'NA-21-Y-D-I', '188': 'NA-21-Y-D-II', '189': 'NA-21-Y-D-III', '229': 'NA-21-Y-D-IV', '230': 'NA-21-Y-D-V', '231': 'NA-21-Y-D-VI', '110': 'NA-21-Z-A-I', '111': 'NA-21-Z-A-II', '112': 'NA-21-Z-A-III', '149': 'NA-21-Z-A-IV', '150': 'NA-21-Z-A-V', '151': 'NA-21-Z-A-VI', '113': 'NA-21-Z-B-I', '114': 'NA-21-Z-B-II', '115': 'NA-21-Z-B-III', '152': 'NA-21-Z-B-IV', '153': 'NA-21-Z-B-V', '154': 'NA-21-Z-B-VI', '190': 'NA-21-Z-C-I', '191': 'NA-21-Z-C-II', '192': 'NA-21-Z-C-III', '232': 'NA-21-Z-C-IV', '233': 'NA-21-Z-C-V', '234': 'NA-21-Z-C-VI', '193': 'NA-21-Z-D-I', '194': 'NA-21-Z-D-II', '195': 'NA-21-Z-D-III', '235': 'NA-21-Z-D-IV', '236': 'NA-21-Z-D-V', '237': 'NA-21-Z-D-VI', '1294': 'SC-18-X-A-III', '1295': 'SC-18-X-B-I', '1296': 'SC-18-X-B-II', '1297': 'SC-18-X-B-III', '1373': 'SC-18-X-B-IV', '1374': 'SC-18-X-B-V', '1375': 'SC-18-X-B-VI', '1450': 'SC-18-X-D-I', '1451': 'SC-18-X-D-II', '1452': 'SC-18-X-D-III', '1527': 'SC-18-X-D-VI', '2565': 'SF-23-V-A-I', '2566': 'SF-23-V-A-II', '2567': 'SF-23-V-A-III', '2601': 'SF-23-V-A-IV', '2602': 'SF-23-V-A-V', '2603': 'SF-23-V-A-VI', '2568': 'SF-23-V-B-I', '2569': 'SF-23-V-B-II', '2570': 'SF-23-V-B-III', '2604': 'SF-23-V-B-IV', '2605': 'SF-23-V-B-V', '2606': 'SF-23-V-B-VI', '2637': 'SF-23-V-C-I', '2638': 'SF-23-V-C-II', '2639': 'SF-23-V-C-III', '2672': 'SF-23-V-C-IV', '2673': 'SF-23-V-C-V', '2674': 'SF-23-V-C-VI', '2640': 'SF-23-V-D-I', '2641': 'SF-23-V-D-II', '2642': 'SF-23-V-D-III', '2675': 'SF-23-V-D-IV', '2676': 'SF-23-V-D-V', '2677': 'SF-23-V-D-VI', '2571': 'SF-23-X-A-I', '2572': 'SF-23-X-A-II', '2573': 'SF-23-X-A-III', '2607': 'SF-23-X-A-IV', '2608': 'SF-23-X-A-V', '2609': 'SF-23-X-A-VI', '2574': 'SF-23-X-B-I', '2575': 'SF-23-X-B-II', '2576': 'SF-23-X-B-III', '2610': 'SF-23-X-B-IV', '2611': 'SF-23-X-B-V', '2612': 'SF-23-X-B-VI', '2643': 'SF-23-X-C-I', '2644': 'SF-23-X-C-II', '2645': 'SF-23-X-C-III', '2678': 'SF-23-X-C-IV', '2679': 'SF-23-X-C-V', '2680': 'SF-23-X-C-VI', '2646': 'SF-23-X-D-I', '2647': 'SF-23-X-D-II', '2648': 'SF-23-X-D-III', '2681': 'SF-23-X-D-IV', '2682': 'SF-23-X-D-V', '2683': 'SF-23-X-D-VI', '2706': 'SF-23-Y-A-I', '2707': 'SF-23-Y-A-II', '2708': 'SF-23-Y-A-III', '2736': 'SF-23-Y-A-IV', '2737': 'SF-23-Y-A-V', '2738': 'SF-23-Y-A-VI', '2709': 'SF-23-Y-B-I', '2710': 'SF-23-Y-B-II', '2711': 'SF-23-Y-B-III', '2739': 'SF-23-Y-B-IV', '2740': 'SF-23-Y-B-V', '2741': 'SF-23-Y-B-VI', '2765': 'SF-23-Y-C-I', '2766': 'SF-23-Y-C-II', '2767': 'SF-23-Y-C-III', '2791': 'SF-23-Y-C-IV', '2792': 'SF-23-Y-C-V', '2793': 'SF-23-Y-C-VI', '2768': 'SF-23-Y-D-I', '2769': 'SF-23-Y-D-II', '2770': 'SF-23-Y-D-III', '2794': 'SF-23-Y-D-IV', '2795': 'SF-23-Y-D-V', '2796': 'SF-23-Y-D-VI', '2712': 'SF-23-Z-A-I', '2713': 'SF-23-Z-A-II', '2714': 'SF-23-Z-A-III', '2742': 'SF-23-Z-A-IV', '2743': 'SF-23-Z-A-V', '2744': 'SF-23-Z-A-VI', '2715': 'SF-23-Z-B-I', '2716': 'SF-23-Z-B-II', '2717': 'SF-23-Z-B-III', '2745': 'SF-23-Z-B-IV', '2746': 'SF-23-Z-B-V', '2747': 'SF-23-Z-B-VI', '2771': 'SF-23-Z-C-I', '2772': 'SF-23-Z-C-II', '2773': 'SF-23-Z-C-III', '2774': 'SF-23-Z-D-I', '2774A': 'SF-23-Z-D-II', '2235': 'SE-21-V-A-I', '2236': 'SE-21-V-A-II', '2237': 'SE-21-V-A-III', '2238': 'SE-21-V-B-I', '2239': 'SE-21-V-B-II', '2240': 'SE-21-V-B-III', '2278': 'SE-21-V-B-IV', '2279': 'SE-21-V-B-V', '2280': 'SE-21-V-B-VI', '2318': 'SE-21-V-D-I', '2319': 'SE-21-V-D-II', '2320': 'SE-21-V-D-III', '2357': 'SE-21-V-D-V', '2358': 'SE-21-V-D-VI', '2241': 'SE-21-X-A-I', '2242': 'SE-21-X-A-II', '2243': 'SE-21-X-A-III', '2281': 'SE-21-X-A-IV', '2282': 'SE-21-X-A-V', '2283': 'SE-21-X-A-VI', '2244': 'SE-21-X-B-I', '2245': 'SE-21-X-B-II', '2246': 'SE-21-X-B-III', '2284': 'SE-21-X-B-IV', '2285': 'SE-21-X-B-V', '2286': 'SE-21-X-B-VI', '2321': 'SE-21-X-C-I', '2322': 'SE-21-X-C-II', '2323': 'SE-21-X-C-III', '2359': 'SE-21-X-C-IV', '2360': 'SE-21-X-C-V', '2361': 'SE-21-X-C-VI', '2324': 'SE-21-X-D-I', '2325': 'SE-21-X-D-II', '2326': 'SE-21-X-D-III', '2362': 'SE-21-X-D-IV', '2363': 'SE-21-X-D-V', '2364': 'SE-21-X-D-VI', '2395': 'SE-21-Y-B-II', '2396': 'SE-21-Y-B-III', '2432': 'SE-21-Y-B-V', '2433': 'SE-21-Y-B-VI', '2468-A': 'SE-21-Y-D-I', '2469': 'SE-21-Y-D-II', '2470': 'SE-21-Y-D-III', '2506': 'SE-21-Y-D-IV', '2507': 'SE-21-Y-D-V', '2508': 'SE-21-Y-D-VI', '2397': 'SE-21-Z-A-I', '2398': 'SE-21-Z-A-II', '2399': 'SE-21-Z-A-III', '2434': 'SE-21-Z-A-IV', '2435': 'SE-21-Z-A-V', '2436': 'SE-21-Z-A-VI', '2400': 'SE-21-Z-B-I', '2401': 'SE-21-Z-B-II', '2402': 'SE-21-Z-B-III', '2437': 'SE-21-Z-B-IV', '2438': 'SE-21-Z-B-V', '2439': 'SE-21-Z-B-VI', '2471': 'SE-21-Z-C-I', '2472': 'SE-21-Z-C-II', '2473': 'SE-21-Z-C-III', '2509': 'SE-21-Z-C-IV', '2510': 'SE-21-Z-C-V', '2511': 'SE-21-Z-C-VI', '2474': 'SE-21-Z-D-I', '2475': 'SE-21-Z-D-II', '2476': 'SE-21-Z-D-III', '2512': 'SE-21-Z-D-IV', '2513': 'SE-21-Z-D-V', '2514': 'SE-21-Z-D-VI', '2234': 'SE-20-X-B-III', '1322': 'SC-21-V-A-I', '1323': 'SC-21-V-A-II', '1324': 'SC-21-V-A-III', '1400': 'SC-21-V-A-IV', '1401': 'SC-21-V-A-V', '1402': 'SC-21-V-A-VI', '1325': 'SC-21-V-B-I', '1326': 'SC-21-V-B-II', '1327': 'SC-21-V-B-III', '1403': 'SC-21-V-B-IV', '1404': 'SC-21-V-B-V', '1405': 'SC-21-V-B-VI', '1477': 'SC-21-V-C-I', '1478': 'SC-21-V-C-II', '1479': 'SC-21-V-C-III', '1552': 'SC-21-V-C-IV', '1553': 'SC-21-V-C-V', '1554': 'SC-21-V-C-VI', '1480': 'SC-21-V-D-I', '1481': 'SC-21-V-D-II', '1482': 'SC-21-V-D-III', '1555': 'SC-21-V-D-IV', '1556': 'SC-21-V-D-V', '1557': 'SC-21-V-D-VI', '1328': 'SC-21-X-A-I', '1329': 'SC-21-X-A-II', '1330': 'SC-21-X-A-III', '1406': 'SC-21-X-A-IV', '1407': 'SC-21-X-A-V', '1408': 'SC-21-X-A-VI', '1331': 'SC-21-X-B-I', '1332': 'SC-21-X-B-II', '1333': 'SC-21-X-B-III', '1409': 'SC-21-X-B-IV', '1410': 'SC-21-X-B-V', '1411': 'SC-21-X-B-VI', '1483': 'SC-21-X-C-I', '1484': 'SC-21-X-C-II', '1485': 'SC-21-X-C-III', '1558': 'SC-21-X-C-IV', '1559': 'SC-21-X-C-V', '1560': 'SC-21-X-C-VI', '1486': 'SC-21-X-D-I', '1487': 'SC-21-X-D-II', '1488': 'SC-21-X-D-III', '1561': 'SC-21-X-D-IV', '1562': 'SC-21-X-D-V', '1563': 'SC-21-X-D-VI', '1621': 'SC-21-Y-A-I', '1622': 'SC-21-Y-A-II', '1623': 'SC-21-Y-A-III', '1687': 'SC-21-Y-A-IV', '1688': 'SC-21-Y-A-V', '1689': 'SC-21-Y-A-VI', '1624': 'SC-21-Y-B-I', '1625': 'SC-21-Y-B-II', '1626': 'SC-21-Y-B-III', '1690': 'SC-21-Y-B-IV', '1691': 'SC-21-Y-B-V', '1692': 'SC-21-Y-B-VI', '1749': 'SC-21-Y-C-I', '1750': 'SC-21-Y-C-II', '1751': 'SC-21-Y-C-III', '1806': 'SC-21-Y-C-IV', '1807': 'SC-21-Y-C-V', '1808': 'SC-21-Y-C-VI', '1752': 'SC-21-Y-D-I', '1753': 'SC-21-Y-D-II', '1754': 'SC-21-Y-D-III', '1809': 'SC-21-Y-D-IV', '1810': 'SC-21-Y-D-V', '1811': 'SC-21-Y-D-VI', '1627': 'SC-21-Z-A-I', '1628': 'SC-21-Z-A-II', '1629': 'SC-21-Z-A-III', '1693': 'SC-21-Z-A-IV', '1694': 'SC-21-Z-A-V', '1695': 'SC-21-Z-A-VI', '1630': 'SC-21-Z-B-I', '1631': 'SC-21-Z-B-II', '1632': 'SC-21-Z-B-III', '1696': 'SC-21-Z-B-IV', '1697': 'SC-21-Z-B-V', '1698': 'SC-21-Z-B-VI', '1755': 'SC-21-Z-C-I', '1756': 'SC-21-Z-C-II', '1757': 'SC-21-Z-C-III', '1812': 'SC-21-Z-C-IV', '1813': 'SC-21-Z-C-V', '1814': 'SC-21-Z-C-VI', '1758': 'SC-21-Z-D-I', '1759': 'SC-21-Z-D-II', '1760': 'SC-21-Z-D-III', '1815': 'SC-21-Z-D-IV', '1816': 'SC-21-Z-D-V', '1817': 'SC-21-Z-D-VI', '1874': 'SD-22-V-A-I', '1875': 'SD-22-V-A-II', '1876': 'SD-22-V-A-III', '1928': 'SD-22-V-A-IV', '1929': 'SD-22-V-A-V', '1930': 'SD-22-V-A-VI', '1877': 'SD-22-V-B-I', '1878': 'SD-22-V-B-II', '1879': 'SD-22-V-B-III', '1931': 'SD-22-V-B-IV', '1932': 'SD-22-V-B-V', '1933': 'SD-22-V-B-VI', '1979': 'SD-22-V-C-I', '1980': 'SD-22-V-C-II', '1981': 'SD-22-V-C-III', '2026': 'SD-22-V-C-IV', '2027': 'SD-22-V-C-V', '2028': 'SD-22-V-C-VI', '1982': 'SD-22-V-D-I', '1983': 'SD-22-V-D-II', '1984': 'SD-22-V-D-III', '2029': 'SD-22-V-D-IV', '2030': 'SD-22-V-D-V', '2031': 'SD-22-V-D-VI', '1880': 'SD-22-X-A-I', '1881': 'SD-22-X-A-II', '1882': 'SD-22-X-A-III', '1934': 'SD-22-X-A-IV', '1935': 'SD-22-X-A-V', '1936': 'SD-22-X-A-VI', '1883': 'SD-22-X-B-I', '1884': 'SD-22-X-B-II', '1885': 'SD-22-X-B-III', '1937': 'SD-22-X-B-IV', '1938': 'SD-22-X-B-V', '1939': 'SD-22-X-B-VI', '1985': 'SD-22-X-C-I', '1986': 'SD-22-X-C-II', '1987': 'SD-22-X-C-III', '2032': 'SD-22-X-C-IV', '2033': 'SD-22-X-C-V', '2034': 'SD-22-X-C-VI', '1988': 'SD-22-X-D-I', '1989': 'SD-22-X-D-II', '1990': 'SD-22-X-D-III', '2035': 'SD-22-X-D-IV', '2036': 'SD-22-X-D-V', '2037': 'SD-22-X-D-VI', '2070': 'SD-22-Y-A-I', '2071': 'SD-22-Y-A-II', '2072': 'SD-22-Y-A-III', '2114': 'SD-22-Y-A-IV', '2115': 'SD-22-Y-A-V', '2116': 'SD-22-Y-A-VI', '2073': 'SD-22-Y-B-I', '2074': 'SD-22-Y-B-II', '2075': 'SD-22-Y-B-III', '2117': 'SD-22-Y-B-IV', '2118': 'SD-22-Y-B-V', '2119': 'SD-22-Y-B-VI', '2159': 'SD-22-Y-C-I', '2160': 'SD-22-Y-C-II', '2161': 'SD-22-Y-C-III', '2203': 'SD-22-Y-C-IV', '2204': 'SD-22-Y-C-V', '2205': 'SD-22-Y-C-VI', '2162': 'SD-22-Y-D-I', '2163': 'SD-22-Y-D-II', '2164': 'SD-22-Y-D-III', '2206': 'SD-22-Y-D-IV', '2207': 'SD-22-Y-D-V', '2208': 'SD-22-Y-D-VI', '2076': 'SD-22-Z-A-I', '2077': 'SD-22-Z-A-II', '2078': 'SD-22-Z-A-III', '2120': 'SD-22-Z-A-IV', '2121': 'SD-22-Z-A-V', '2122': 'SD-22-Z-A-VI', '2079': 'SD-22-Z-B-I', '2080': 'SD-22-Z-B-II', '2081': 'SD-22-Z-B-III', '2123': 'SD-22-Z-B-IV', '2124': 'SD-22-Z-B-V', '2125': 'SD-22-Z-B-VI', '2165': 'SD-22-Z-C-I', '2166': 'SD-22-Z-C-II', '2167': 'SD-22-Z-C-III', '2209': 'SD-22-Z-C-IV', '2210': 'SD-22-Z-C-V', '2211': 'SD-22-Z-C-VI', '2168': 'SD-22-Z-D-I', '2169': 'SD-22-Z-D-II', '2170': 'SD-22-Z-D-III', '2212': 'SD-22-Z-D-IV', '2213': 'SD-22-Z-D-V', '2214': 'SD-22-Z-D-VI', '2812': 'SG-23-V-A-I', '2813': 'SG-23-V-A-II', '2814': 'SG-23-V-A-III', '2829': 'SG-23-V-A-IV', '2830': 'SG-23-V-A-V', '2815': 'SG-23-V-B-I', '2845': 'SG-23-V-C-I', '2247': 'SE-22-V-A-I', '2248': 'SE-22-V-A-II', '2249': 'SE-22-V-A-III', '2287': 'SE-22-V-A-IV', '2288': 'SE-22-V-A-V', '2289': 'SE-22-V-A-VI', '2250': 'SE-22-V-B-I', '2251': 'SE-22-V-B-II', '2252': 'SE-22-V-B-III', '2290': 'SE-22-V-B-IV', '2291': 'SE-22-V-B-V', '2292': 'SE-22-V-B-VI', '2327': 'SE-22-V-C-I', '2328': 'SE-22-V-C-II', '2329': 'SE-22-V-C-III', '2365': 'SE-22-V-C-IV', '2366': 'SE-22-V-C-V', '2367': 'SE-22-V-C-VI', '2330': 'SE-22-V-D-I', '2331': 'SE-22-V-D-II', '2332': 'SE-22-V-D-III', '2368': 'SE-22-V-D-IV', '2369': 'SE-22-V-D-V', '2370': 'SE-22-V-D-VI', '2253': 'SE-22-X-A-I', '2254': 'SE-22-X-A-II', '2255': 'SE-22-X-A-III', '2293': 'SE-22-X-A-IV', '2294': 'SE-22-X-A-V', '2295': 'SE-22-X-A-VI', '2256': 'SE-22-X-B-I', '2257': 'SE-22-X-B-II', '2258': 'SE-22-X-B-III', '2296': 'SE-22-X-B-IV', '2297': 'SE-22-X-B-V', '2298': 'SE-22-X-B-VI', '2333': 'SE-22-X-C-I', '2334': 'SE-22-X-C-II', '2335': 'SE-22-X-C-III', '2371': 'SE-22-X-C-IV', '2372': 'SE-22-X-C-V', '2373': 'SE-22-X-C-VI', '2336': 'SE-22-X-D-I', '2337': 'SE-22-X-D-II', '2338': 'SE-22-X-D-III', '2374': 'SE-22-X-D-IV', '2375': 'SE-22-X-D-V', '2376': 'SE-22-X-D-VI', '2403': 'SE-22-Y-A-I', '2404': 'SE-22-Y-A-II', '2405': 'SE-22-Y-A-III', '2440': 'SE-22-Y-A-IV', '2441': 'SE-22-Y-A-V', '2442': 'SE-22-Y-A-VI', '2406': 'SE-22-Y-B-I', '2407': 'SE-22-Y-B-II', '2408': 'SE-22-Y-B-III', '2443': 'SE-22-Y-B-IV', '2444': 'SE-22-Y-B-V', '2445': 'SE-22-Y-B-VI', '2477': 'SE-22-Y-C-I', '2478': 'SE-22-Y-C-II', '2479': 'SE-22-Y-C-III', '2515': 'SE-22-Y-C-IV', '2516': 'SE-22-Y-C-V', '2517': 'SE-22-Y-C-VI', '2480': 'SE-22-Y-D-I', '2481': 'SE-22-Y-D-II', '2482': 'SE-22-Y-D-III', '2518': 'SE-22-Y-D-IV', '2519': 'SE-22-Y-D-V', '2520': 'SE-22-Y-D-VI', '2409': 'SE-22-Z-A-I', '2410': 'SE-22-Z-A-II', '2411': 'SE-22-Z-A-III', '2446': 'SE-22-Z-A-IV', '2447': 'SE-22-Z-A-V', '2448': 'SE-22-Z-A-VI', '2412': 'SE-22-Z-B-I', '2413': 'SE-22-Z-B-II', '2414': 'SE-22-Z-B-III', '2449': 'SE-22-Z-B-IV', '2450': 'SE-22-Z-B-V', '2451': 'SE-22-Z-B-VI', '2483': 'SE-22-Z-C-I', '2484': 'SE-22-Z-C-II', '2485': 'SE-22-Z-C-III', '2521': 'SE-22-Z-C-IV', '2522': 'SE-22-Z-C-V', '2523': 'SE-22-Z-C-VI', '2486': 'SE-22-Z-D-I', '2487': 'SE-22-Z-D-II', '2488': 'SE-22-Z-D-III', '2524': 'SE-22-Z-D-IV', '2525': 'SE-22-Z-D-V', '2526': 'SE-22-Z-D-VI', '1334': 'SC-22-V-A-I', '1335': 'SC-22-V-A-II', '1336': 'SC-22-V-A-III', '1412': 'SC-22-V-A-IV', '1413': 'SC-22-V-A-V', '1414': 'SC-22-V-A-VI', '1337': 'SC-22-V-B-I', '1338': 'SC-22-V-B-II', '1339': 'SC-22-V-B-III', '1415': 'SC-22-V-B-IV', '1416': 'SC-22-V-B-V', '1417': 'SC-22-V-B-VI', '1489': 'SC-22-V-C-I', '1490': 'SC-22-V-C-II', '1491': 'SC-22-V-C-III', '1564': 'SC-22-V-C-IV', '1565': 'SC-22-V-C-V', '1566': 'SC-22-V-C-VI', '1492': 'SC-22-V-D-I', '1493': 'SC-22-V-D-II', '1494': 'SC-22-V-D-III', '1567': 'SC-22-V-D-IV', '1568': 'SC-22-V-D-V', '1569': 'SC-22-V-D-VI', '1340': 'SC-22-X-A-I', '1341': 'SC-22-X-A-II', '1342': 'SC-22-X-A-III', '1418': 'SC-22-X-A-IV', '1419': 'SC-22-X-A-V', '1420': 'SC-22-X-A-VI', '1343': 'SC-22-X-B-I', '1344': 'SC-22-X-B-II', '1345': 'SC-22-X-B-III', '1421': 'SC-22-X-B-IV', '1422': 'SC-22-X-B-V', '1423': 'SC-22-X-B-VI', '1495': 'SC-22-X-C-I', '1496': 'SC-22-X-C-II', '1497': 'SC-22-X-C-III', '1570': 'SC-22-X-C-IV', '1571': 'SC-22-X-C-V', '1572': 'SC-22-X-C-VI', '1498': 'SC-22-X-D-I', '1499': 'SC-22-X-D-II', '1500': 'SC-22-X-D-III', '1573': 'SC-22-X-D-IV', '1574': 'SC-22-X-D-V', '1575': 'SC-22-X-D-VI', '1633': 'SC-22-Y-A-I', '1634': 'SC-22-Y-A-II', '1635': 'SC-22-Y-A-III', '1699': 'SC-22-Y-A-IV', '1700': 'SC-22-Y-A-V', '1701': 'SC-22-Y-A-VI', '1636': 'SC-22-Y-B-I', '1637': 'SC-22-Y-B-II', '1638': 'SC-22-Y-B-III', '1702': 'SC-22-Y-B-IV', '1703': 'SC-22-Y-B-V', '1704': 'SC-22-Y-B-VI', '1761': 'SC-22-Y-C-I', '1762': 'SC-22-Y-C-II', '1763': 'SC-22-Y-C-III', '1818': 'SC-22-Y-C-IV', '1819': 'SC-22-Y-C-V', '1820': 'SC-22-Y-C-VI', '1764': 'SC-22-Y-D-I', '1765': 'SC-22-Y-D-II', '1766': 'SC-22-Y-D-III', '1821': 'SC-22-Y-D-IV', '1822': 'SC-22-Y-D-V', '1823': 'SC-22-Y-D-VI', '1639': 'SC-22-Z-A-I', '1640': 'SC-22-Z-A-II', '1641': 'SC-22-Z-A-III', '1705': 'SC-22-Z-A-IV', '1706': 'SC-22-Z-A-V', '1707': 'SC-22-Z-A-VI', '1642': 'SC-22-Z-B-I', '1643': 'SC-22-Z-B-II', '1644': 'SC-22-Z-B-III', '1708': 'SC-22-Z-B-IV', '1709': 'SC-22-Z-B-V', '1710': 'SC-22-Z-B-VI', '1767': 'SC-22-Z-C-I', '1768': 'SC-22-Z-C-II', '1769': 'SC-22-Z-C-III', '1824': 'SC-22-Z-C-IV', '1825': 'SC-22-Z-C-V', '1826': 'SC-22-Z-C-VI', '1770': 'SC-22-Z-D-I', '1771': 'SC-22-Z-D-II', '1772': 'SC-22-Z-D-III', '1827': 'SC-22-Z-D-IV', '1828': 'SC-22-Z-D-V', '1829': 'SC-22-Z-D-VI', '2259': 'SE-23-V-A-I', '2260': 'SE-23-V-A-II', '2261': 'SE-23-V-A-III', '2299': 'SE-23-V-A-IV', '2300': 'SE-23-V-A-V', '2301': 'SE-23-V-A-VI', '2262': 'SE-23-V-B-I', '2263': 'SE-23-V-B-II', '2264': 'SE-23-V-B-III', '2302': 'SE-23-V-B-IV', '2303': 'SE-23-V-B-V', '2304': 'SE-23-V-B-VI', '2339': 'SE-23-V-C-I', '2340': 'SE-23-V-C-II', '2341': 'SE-23-V-C-III', '2377': 'SE-23-V-C-IV', '2378': 'SE-23-V-C-V', '2379': 'SE-23-V-C-VI', '2342': 'SE-23-V-D-I', '2343': 'SE-23-V-D-II', '2344': 'SE-23-V-D-III', '2380': 'SE-23-V-D-IV', '2381': 'SE-23-V-D-V', '2382': 'SE-23-V-D-VI', '2265': 'SE-23-X-A-I', '2266': 'SE-23-X-A-II', '2267': 'SE-23-X-A-III', '2305': 'SE-23-X-A-IV', '2306': 'SE-23-X-A-V', '2307': 'SE-23-X-A-VI', '2268': 'SE-23-X-B-I', '2269': 'SE-23-X-B-II', '2270': 'SE-23-X-B-III', '2308': 'SE-23-X-B-IV', '2309': 'SE-23-X-B-V', '2310': 'SE-23-X-B-VI', '2345': 'SE-23-X-C-I', '2346': 'SE-23-X-C-II', '2347': 'SE-23-X-C-III', '2383': 'SE-23-X-C-IV', '2384': 'SE-23-X-C-V', '2385': 'SE-23-X-C-VI', '2348': 'SE-23-X-D-I', '2349': 'SE-23-X-D-II', '2350': 'SE-23-X-D-III', '2386': 'SE-23-X-D-IV', '2387': 'SE-23-X-D-V', '2388': 'SE-23-X-D-VI', '2415': 'SE-23-Y-A-I', '2416': 'SE-23-Y-A-II', '2417': 'SE-23-Y-A-III', '2452': 'SE-23-Y-A-IV', '2453': 'SE-23-Y-A-V', '2454': 'SE-23-Y-A-VI', '2418': 'SE-23-Y-B-I', '2419': 'SE-23-Y-B-II', '2420': 'SE-23-Y-B-III', '2455': 'SE-23-Y-B-IV', '2456': 'SE-23-Y-B-V', '2457': 'SE-23-Y-B-VI', '2489': 'SE-23-Y-C-I', '2490': 'SE-23-Y-C-II', '2491': 'SE-23-Y-C-III', '2527': 'SE-23-Y-C-IV', '2528': 'SE-23-Y-C-V', '2529': 'SE-23-Y-C-VI', '2492': 'SE-23-Y-D-I', '2493': 'SE-23-Y-D-II', '2494': 'SE-23-Y-D-III', '2530': 'SE-23-Y-D-IV', '2531': 'SE-23-Y-D-V', '2532': 'SE-23-Y-D-VI', '2421': 'SE-23-Z-A-I', '2422': 'SE-23-Z-A-II', '2423': 'SE-23-Z-A-III', '2458': 'SE-23-Z-A-IV', '2459': 'SE-23-Z-A-V', '2460': 'SE-23-Z-A-VI', '2424': 'SE-23-Z-B-I', '2425': 'SE-23-Z-B-II', '2426': 'SE-23-Z-B-III', '2461': 'SE-23-Z-B-IV', '2462': 'SE-23-Z-B-V', '2463': 'SE-23-Z-B-VI', '2495': 'SE-23-Z-C-I', '2496': 'SE-23-Z-C-II', '2497': 'SE-23-Z-C-III', '2533': 'SE-23-Z-C-IV', '2534': 'SE-23-Z-C-V', '2535': 'SE-23-Z-C-VI', '2498': 'SE-23-Z-D-I', '2499': 'SE-23-Z-D-II', '2500': 'SE-23-Z-D-III', '2536': 'SE-23-Z-D-IV', '2537': 'SE-23-Z-D-V', '2538': 'SE-23-Z-D-VI', '2800': 'SG-22-V-A-I', '2801': 'SG-22-V-A-II', '2802': 'SG-22-V-A-III', '2817': 'SG-22-V-A-IV', '2818': 'SG-22-V-A-V', '2819': 'SG-22-V-A-VI', '2803': 'SG-22-V-B-I', '2804': 'SG-22-V-B-II', '2805': 'SG-22-V-B-III', '2820': 'SG-22-V-B-IV', '2821': 'SG-22-V-B-V', '2822': 'SG-22-V-B-VI', '2833': 'SG-22-V-C-I', '2834': 'SG-22-V-C-II', '2835': 'SG-22-V-C-III', '2848': 'SG-22-V-C-IV', '2849': 'SG-22-V-C-V', '2850': 'SG-22-V-C-VI', '2836': 'SG-22-V-D-I', '2837': 'SG-22-V-D-II', '2838': 'SG-22-V-D-III', '2851': 'SG-22-V-D-IV', '2852': 'SG-22-V-D-V', '2853': 'SG-22-V-D-VI', '2806': 'SG-22-X-A-I', '2807': 'SG-22-X-A-II', '2808': 'SG-22-X-A-III', '2823': 'SG-22-X-A-IV', '2824': 'SG-22-X-A-V', '2825': 'SG-22-X-A-VI', '2809': 'SG-22-X-B-I', '2810': 'SG-22-X-B-II', '2811': 'SG-22-X-B-III', '2826': 'SG-22-X-B-IV', '2827': 'SG-22-X-B-V', '2828': 'SG-22-X-B-VI', '2839': 'SG-22-X-C-I', '2840': 'SG-22-X-C-II', '2841': 'SG-22-X-C-III', '2854': 'SG-22-X-C-IV', '2855': 'SG-22-X-C-V', '2856': 'SG-22-X-C-VI', '2842': 'SG-22-X-D-I', '2843': 'SG-22-X-D-II', '2844': 'SG-22-X-D-III', '2857': 'SG-22-X-D-IV', '2858': 'SG-22-X-D-V', '2859': 'SG-22-X-D-VI', '2860': 'SG-22-Y-A-I', '2861': 'SG-22-Y-A-II', '2862': 'SG-22-Y-A-III', '2872': 'SG-22-Y-A-IV', '2873': 'SG-22-Y-A-V', '2874': 'SG-22-Y-A-VI', '2863': 'SG-22-Y-B-I', '2864': 'SG-22-Y-B-II', '2865': 'SG-22-Y-B-III', '2875': 'SG-22-Y-B-IV', '2876': 'SG-22-Y-B-V', '2877': 'SG-22-Y-B-VI', '2884': 'SG-22-Y-C-I', '2885': 'SG-22-Y-C-II', '2886': 'SG-22-Y-C-III', '2899': 'SG-22-Y-C-IV', '2900': 'SG-22-Y-C-V', '2901': 'SG-22-Y-C-VI', '2887': 'SG-22-Y-D-I', '2888': 'SG-22-Y-D-II', '2889': 'SG-22-Y-D-III', '2902': 'SG-22-Y-D-IV', '2903': 'SG-22-Y-D-V', '2904': 'SG-22-Y-D-VI', '2866': 'SG-22-Z-A-I', '2867': 'SG-22-Z-A-II', '2868': 'SG-22-Z-A-III', '2878': 'SG-22-Z-A-IV', '2879': 'SG-22-Z-A-V', '2880': 'SG-22-Z-A-VI', '2869': 'SG-22-Z-B-I', '2870': 'SG-22-Z-B-II', '2871': 'SG-22-Z-B-III', '2881': 'SG-22-Z-B-IV', '2882': 'SG-22-Z-B-V', '2890': 'SG-22-Z-C-I', '2891': 'SG-22-Z-C-II', '2892': 'SG-22-Z-C-III', '2905': 'SG-22-Z-C-IV', '2906': 'SG-22-Z-C-V', '2907': 'SG-22-Z-C-VI', '2893': 'SG-22-Z-D-I', '2894': 'SG-22-Z-D-II', '2895': 'SG-22-Z-D-III', '2908': 'SG-22-Z-D-IV', '2909': 'SG-22-Z-D-V', '2910': 'SG-22-Z-D-VI', '3023': 'SI-22-V-A-I', '3024': 'SI-22-V-A-II', '3025': 'SI-22-V-A-III', '3028': 'SI-22-V-A-IV', '3029': 'SI-22-V-A-V', '3030': 'SI-22-V-A-VI', '3026': 'SI-22-V-B-I', '3027': 'SI-22-V-B-II', '3031': 'SI-22-V-B-IV', '3032': 'SI-22-V-C-I', '3033': 'SI-22-V-C-II', '3034': 'SI-22-V-C-III', '3035': 'SI-22-V-C-IV', '3036': 'SI-22-V-C-V', '3036A': 'SI-22-V-C-VI', '30': 'NA-22-V-B-I', '31': 'NA-22-V-B-II', '32': 'NA-22-V-B-III', '43': 'NA-22-V-B-IV', '44': 'NA-22-V-B-V', '45': 'NA-22-V-B-VI', '59': 'NA-22-V-C-III', '82': 'NA-22-V-C-IV', '83': 'NA-22-V-C-V', '84': 'NA-22-V-C-VI', '60': 'NA-22-V-D-I', '61': 'NA-22-V-D-II', '62': 'NA-22-V-D-III', '85': 'NA-22-V-D-IV', '86': 'NA-22-V-D-V', '87': 'NA-22-V-D-VI', '46': 'NA-22-X-A-IV', '63': 'NA-22-X-C-I', '88': 'NA-22-X-C-IV', '89': 'NA-22-X-C-V', '116': 'NA-22-Y-A-I', '117': 'NA-22-Y-A-II', '118': 'NA-22-Y-A-III', '155': 'NA-22-Y-A-IV', '156': 'NA-22-Y-A-V', '157': 'NA-22-Y-A-VI', '119': 'NA-22-Y-B-I', '120': 'NA-22-Y-B-II', '121': 'NA-22-Y-B-III', '158': 'NA-22-Y-B-IV', '159': 'NA-22-Y-B-V', '160': 'NA-22-Y-B-VI', '196': 'NA-22-Y-C-I', '197': 'NA-22-Y-C-II', '198': 'NA-22-Y-C-III', '238': 'NA-22-Y-C-IV', '239': 'NA-22-Y-C-V', '240': 'NA-22-Y-C-VI', '199': 'NA-22-Y-D-I', '200': 'NA-22-Y-D-II', '201': 'NA-22-Y-D-III', '241': 'NA-22-Y-D-IV', '242': 'NA-22-Y-D-V', '243': 'NA-22-Y-D-VI', '122': 'NA-22-Z-A-I', '123': 'NA-22-Z-A-II', '124': 'NA-22-Z-A-III', '161': 'NA-22-Z-A-IV', '162': 'NA-22-Z-A-V', '163': 'NA-22-Z-A-VI', '202': 'NA-22-Z-C-I', '203': 'NA-22-Z-C-II', '204': 'NA-22-Z-C-III', '244': 'NA-22-Z-C-IV', '245': 'NA-22-Z-C-V', '246': 'NA-22-Z-C-VI', '247': 'NA-22-Z-D-IV', '753': 'SB-18-X-B-V', '754': 'SB-18-X-B-VI', '826': 'SB-18-X-D-II', '827': 'SB-18-X-D-III', '902': 'SB-18-X-D-IV', '903': 'SB-18-X-D-V', '904': 'SB-18-X-D-VI', '1057': 'SB-18-Z-A-VI', '979': 'SB-18-Z-B-I', '980': 'SB-18-Z-B-II', '981': 'SB-18-Z-B-III', '1058': 'SB-18-Z-B-IV', '1059': 'SB-18-Z-B-V', '1060': 'SB-18-Z-B-VI', '1136': 'SB-18-Z-C-III', '1215': 'SB-18-Z-C-VI', '1137': 'SB-18-Z-D-I', '1138': 'SB-18-Z-D-II', '1139': 'SB-18-Z-D-III', '1216': 'SB-18-Z-D-IV', '1217': 'SB-18-Z-D-V', '1218': 'SB-18-Z-D-VI', '269': 'SA-21-V-A-I', '270': 'SA-21-V-A-II', '271': 'SA-21-V-A-III', '313': 'SA-21-V-A-IV', '314': 'SA-21-V-A-V', '315': 'SA-21-V-A-VI', '272': 'SA-21-V-B-I', '273': 'SA-21-V-B-II', '274': 'SA-21-V-B-III', '316': 'SA-21-V-B-IV', '317': 'SA-21-V-B-V', '318': 'SA-21-V-B-VI', '361': 'SA-21-V-C-I', '362': 'SA-21-V-C-II', '363': 'SA-21-V-C-III', '412': 'SA-21-V-C-IV', '413': 'SA-21-V-C-V', '414': 'SA-21-V-C-VI', '364': 'SA-21-V-D-I', '365': 'SA-21-V-D-II', '366': 'SA-21-V-D-III', '415': 'SA-21-V-D-IV', '416': 'SA-21-V-D-V', '417': 'SA-21-V-D-VI', '275': 'SA-21-X-A-I', '276': 'SA-21-X-A-II', '277': 'SA-21-X-A-III', '319': 'SA-21-X-A-IV', '320': 'SA-21-X-A-V', '321': 'SA-21-X-A-VI', '278': 'SA-21-X-B-I', '279': 'SA-21-X-B-II', '280': 'SA-21-X-B-III', '322': 'SA-21-X-B-IV', '323': 'SA-21-X-B-V', '324': 'SA-21-X-B-VI', '367': 'SA-21-X-C-I', '368': 'SA-21-X-C-II', '369': 'SA-21-X-C-III', '418': 'SA-21-X-C-IV', '419': 'SA-21-X-C-V', '420': 'SA-21-X-C-VI', '370': 'SA-21-X-D-I', '371': 'SA-21-X-D-II', '372': 'SA-21-X-D-III', '421': 'SA-21-X-D-IV', '422': 'SA-21-X-D-V', '423': 'SA-21-X-D-VI', '464': 'SA-21-Y-A-I', '465': 'SA-21-Y-A-II', '466': 'SA-21-Y-A-III', '518': 'SA-21-Y-A-IV', '519': 'SA-21-Y-A-V', '520': 'SA-21-Y-A-VI', '467': 'SA-21-Y-B-I', '468': 'SA-21-Y-B-II', '469': 'SA-21-Y-B-III', '521': 'SA-21-Y-B-IV', '522': 'SA-21-Y-B-V', '523': 'SA-21-Y-B-VI', '579': 'SA-21-Y-C-I', '580': 'SA-21-Y-C-II', '581': 'SA-21-Y-C-III', '642': 'SA-21-Y-C-IV', '643': 'SA-21-Y-C-V', '644': 'SA-21-Y-C-VI', '582': 'SA-21-Y-D-I', '583': 'SA-21-Y-D-II', '584': 'SA-21-Y-D-III', '645': 'SA-21-Y-D-IV', '646': 'SA-21-Y-D-V', '647': 'SA-21-Y-D-VI', '470': 'SA-21-Z-A-I', '471': 'SA-21-Z-A-II', '472': 'SA-21-Z-A-III', '524': 'SA-21-Z-A-IV', '525': 'SA-21-Z-A-V', '526': 'SA-21-Z-A-VI', '473': 'SA-21-Z-B-I', '474': 'SA-21-Z-B-II', '475': 'SA-21-Z-B-III', '527': 'SA-21-Z-B-IV', '528': 'SA-21-Z-B-V', '529': 'SA-21-Z-B-VI', '585': 'SA-21-Z-C-I', '586': 'SA-21-Z-C-II', '587': 'SA-21-Z-C-III', '648': 'SA-21-Z-C-IV', '649': 'SA-21-Z-C-V', '650': 'SA-21-Z-C-VI', '588': 'SA-21-Z-D-I', '589': 'SA-21-Z-D-II', '590': 'SA-21-Z-D-III', '651': 'SA-21-Z-D-IV', '652': 'SA-21-Z-D-V', '653': 'SA-21-Z-D-VI', '554': 'SA-24-Y-A-IV', '555': 'SA-24-Y-A-V', '556': 'SA-24-Y-A-VI', '557': 'SA-24-Y-B-IV', '558': 'SA-24-Y-B-V', '615': 'SA-24-Y-C-I', '616': 'SA-24-Y-C-II', '617': 'SA-24-Y-C-III', '678': 'SA-24-Y-C-IV', '679': 'SA-24-Y-C-V', '680': 'SA-24-Y-C-VI', '618': 'SA-24-Y-D-I', '619': 'SA-24-Y-D-II', '620': 'SA-24-Y-D-III', '681': 'SA-24-Y-D-IV', '682': 'SA-24-Y-D-V', '683': 'SA-24-Y-D-VI', '621': 'SA-24-Z-C-I', '684': 'SA-24-Z-C-IV', '685': 'SA-24-Z-C-V', '1862': 'SD-21-V-A-I', '1863': 'SD-21-V-A-II', '1864': 'SD-21-V-A-III', '1916': 'SD-21-V-A-IV', '1917': 'SD-21-V-A-V', '1918': 'SD-21-V-A-VI', '1865': 'SD-21-V-B-I', '1866': 'SD-21-V-B-II', '1867': 'SD-21-V-B-III', '1919': 'SD-21-V-B-IV', '1920': 'SD-21-V-B-V', '1921': 'SD-21-V-B-VI', '1967': 'SD-21-V-C-I', '1968': 'SD-21-V-C-II', '1969': 'SD-21-V-C-III', '2014': 'SD-21-V-C-IV', '2015': 'SD-21-V-C-V', '2016': 'SD-21-V-C-VI', '1970': 'SD-21-V-D-I', '1971': 'SD-21-V-D-II', '1972': 'SD-21-V-D-III', '2017': 'SD-21-V-D-IV', '2018': 'SD-21-V-D-V', '2019': 'SD-21-V-D-VI', '1868': 'SD-21-X-A-I', '1869': 'SD-21-X-A-II', '1870': 'SD-21-X-A-III', '1922': 'SD-21-X-A-IV', '1923': 'SD-21-X-A-V', '1924': 'SD-21-X-A-VI', '1871': 'SD-21-X-B-I', '1872': 'SD-21-X-B-II', '1873': 'SD-21-X-B-III', '1925': 'SD-21-X-B-IV', '1926': 'SD-21-X-B-V', '1927': 'SD-21-X-B-VI', '1973': 'SD-21-X-C-I', '1974': 'SD-21-X-C-II', '1975': 'SD-21-X-C-III', '2020': 'SD-21-X-C-IV', '2021': 'SD-21-X-C-V', '2022': 'SD-21-X-C-VI', '1976': 'SD-21-X-D-I', '1977': 'SD-21-X-D-II', '1978': 'SD-21-X-D-III', '2023': 'SD-21-X-D-IV', '2024': 'SD-21-X-D-V', '2025': 'SD-21-X-D-VI', '2058': 'SD-21-Y-A-I', '2059': 'SD-21-Y-A-II', '2060': 'SD-21-Y-A-III', '2102': 'SD-21-Y-A-IV', '2103': 'SD-21-Y-A-V', '2104': 'SD-21-Y-A-VI', '2061': 'SD-21-Y-B-I', '2062': 'SD-21-Y-B-II', '2063': 'SD-21-Y-B-III', '2105': 'SD-21-Y-B-IV', '2106': 'SD-21-Y-B-V', '2107': 'SD-21-Y-B-VI', '2147': 'SD-21-Y-C-I', '2148': 'SD-21-Y-C-II', '2149': 'SD-21-Y-C-III', '2191': 'SD-21-Y-C-IV', '2192': 'SD-21-Y-C-V', '2193': 'SD-21-Y-C-VI', '2150': 'SD-21-Y-D-I', '2151': 'SD-21-Y-D-II', '2152': 'SD-21-Y-D-III', '2194': 'SD-21-Y-D-IV', '2195': 'SD-21-Y-D-V', '2196': 'SD-21-Y-D-VI', '2064': 'SD-21-Z-A-I', '2065': 'SD-21-Z-A-II', '2066': 'SD-21-Z-A-III', '2108': 'SD-21-Z-A-IV', '2109': 'SD-21-Z-A-V', '2110': 'SD-21-Z-A-VI', '2067': 'SD-21-Z-B-I', '2068': 'SD-21-Z-B-II', '2069': 'SD-21-Z-B-III', '2111': 'SD-21-Z-B-IV', '2112': 'SD-21-Z-B-V', '2113': 'SD-21-Z-B-VI', '2153': 'SD-21-Z-C-I', '2154': 'SD-21-Z-C-II', '2155': 'SD-21-Z-C-III', '2197': 'SD-21-Z-C-IV', '2198': 'SD-21-Z-C-V', '2199': 'SD-21-Z-C-VI', '2156': 'SD-21-Z-D-I', '2157': 'SD-21-Z-D-II', '2158': 'SD-21-Z-D-III', '2200': 'SD-21-Z-D-IV', '2201': 'SD-21-Z-D-V', '2202': 'SD-21-Z-D-VI', '1898': 'SD-24-V-A-I', '1899': 'SD-24-V-A-II', '1900': 'SD-24-V-A-III', '1952': 'SD-24-V-A-IV', '1953': 'SD-24-V-A-V', '1954': 'SD-24-V-A-VI', '1901': 'SD-24-V-B-I', '1902': 'SD-24-V-B-II', '1903': 'SD-24-V-B-III', '1955': 'SD-24-V-B-IV', '1956': 'SD-24-V-B-V', '1957': 'SD-24-V-B-VI', '2003': 'SD-24-V-C-I', '2004': 'SD-24-V-C-II', '2005': 'SD-24-V-C-III', '2050': 'SD-24-V-C-IV', '2051': 'SD-24-V-C-V', '2052': 'SD-24-V-C-VI', '2006': 'SD-24-V-D-I', '2007': 'SD-24-V-D-II', '2008': 'SD-24-V-D-III', '2053': 'SD-24-V-D-IV', '2054': 'SD-24-V-D-V', '2055': 'SD-24-V-D-VI', '1904': 'SD-24-X-A-I', '1905': 'SD-24-X-A-II', '1906': 'SD-24-X-A-III', '1958': 'SD-24-X-A-IV', '1959': 'SD-24-X-A-V', '1960': 'SD-24-X-A-VI', '2009': 'SD-24-X-C-I', '2056': 'SD-24-X-C-IV', '2094': 'SD-24-Y-A-I', '2095': 'SD-24-Y-A-II', '2096': 'SD-24-Y-A-III', '2138': 'SD-24-Y-A-IV', '2139': 'SD-24-Y-A-V', '2140': 'SD-24-Y-A-VI', '2097': 'SD-24-Y-B-I', '2098': 'SD-24-Y-B-II', '2099': 'SD-24-Y-B-III', '2141': 'SD-24-Y-B-IV', '2142': 'SD-24-Y-B-V', '2143': 'SD-24-Y-B-VI', '2183': 'SD-24-Y-C-I', '2184': 'SD-24-Y-C-II', '2185': 'SD-24-Y-C-III', '2227': 'SD-24-Y-C-IV', '2228': 'SD-24-Y-C-V', '2229': 'SD-24-Y-C-VI', '2186': 'SD-24-Y-D-I', '2187': 'SD-24-Y-D-II', '2188': 'SD-24-Y-D-III', '2230': 'SD-24-Y-D-IV', '2231': 'SD-24-Y-D-V', '2232': 'SD-24-Y-D-VI', '2100': 'SD-24-Z-A-I', '2144': 'SD-24-Z-A-IV', '2189': 'SD-24-Z-C-I', '2233': 'SD-24-Z-C-IV', '1370': 'SC-25-V-A-I', '1371': 'SC-25-V-A-II', '1372': 'SC-25-V-A-III', '1448': 'SC-25-V-A-IV', '1449': 'SC-25-V-A-V', '1449-A': 'SC-25-V-A-VI', '1525': 'SC-25-V-C-I', '1526': 'SC-25-V-C-II', '1600': 'SC-25-V-C-IV', '2958': 'SH-21-V-D-VI', '2911': 'SH-21-X-A-III', '2926': 'SH-21-X-A-V', '2927': 'SH-21-X-A-VI', '2912': 'SH-21-X-B-I', '2913': 'SH-21-X-B-II', '2914': 'SH-21-X-B-III', '2928': 'SH-21-X-B-IV', '2929': 'SH-21-X-B-V', '2930': 'SH-21-X-B-VI', '2942': 'SH-21-X-C-I', '2943': 'SH-21-X-C-II', '2944': 'SH-21-X-C-III', '2959': 'SH-21-X-C-IV', '2960': 'SH-21-X-C-V', '2961': 'SH-21-X-C-VI', '2945': 'SH-21-X-D-I', '2946': 'SH-21-X-D-II', '2947': 'SH-21-X-D-III', '2962': 'SH-21-X-D-IV', '2963': 'SH-21-X-D-V', '2964': 'SH-21-X-D-VI', '2974': 'SH-21-Y-B-II', '2975': 'SH-21-Y-B-III', '2976': 'SH-21-Z-A-I', '2977': 'SH-21-Z-A-II', '2978': 'SH-21-Z-A-III', '2990': 'SH-21-Z-A-V', '2991': 'SH-21-Z-A-VI', '2979': 'SH-21-Z-B-I', '2980': 'SH-21-Z-B-II', '2981': 'SH-21-Z-B-III', '2992': 'SH-21-Z-B-IV', '2993': 'SH-21-Z-B-V', '2994': 'SH-21-Z-B-VI', '3003': 'SH-21-Z-C-II', '3004': 'SH-21-Z-C-III', '3005': 'SH-21-Z-D-I', '3006': 'SH-21-Z-D-II', '3007': 'SH-21-Z-D-III', '3015': 'SH-21-Z-D-V', '3016': 'SH-21-Z-D-VI', '17': 'NB-22-Y-D-V', '18': 'NB-22-Y-D-VI', '2271': 'SE-24-V-A-I', '2272': 'SE-24-V-A-II', '2273': 'SE-24-V-A-III', '2311': 'SE-24-V-A-IV', '2312': 'SE-24-V-A-V', '2313': 'SE-24-V-A-VI', '2274': 'SE-24-V-B-I', '2275': 'SE-24-V-B-II', '2276': 'SE-24-V-B-III', '2314': 'SE-24-V-B-IV', '2315': 'SE-24-V-B-V', '2316': 'SE-24-V-B-VI', '2351': 'SE-24-V-C-I', '2352': 'SE-24-V-C-II', '2353': 'SE-24-V-C-III', '2389': 'SE-24-V-C-IV', '2390': 'SE-24-V-C-V', '2391': 'SE-24-V-C-VI', '2354': 'SE-24-V-D-I', '2355': 'SE-24-V-D-II', '2356': 'SE-24-V-D-III', '2392': 'SE-24-V-D-IV', '2393': 'SE-24-V-D-V', '2394': 'SE-24-V-D-VI', '2277': 'SE-24-X-A-I', '2317': 'SE-24-X-A-IV', '2427': 'SE-24-Y-A-I', '2428': 'SE-24-Y-A-II', '2429': 'SE-24-Y-A-III', '2464': 'SE-24-Y-A-IV', '2465': 'SE-24-Y-A-V', '2466': 'SE-24-Y-A-VI', '2430': 'SE-24-Y-B-I', '2431': 'SE-24-Y-B-II', '2431A': 'SE-24-Y-B-III', '2467': 'SE-24-Y-B-IV', '2468': 'SE-24-Y-B-V', '2501': 'SE-24-Y-C-I', '2502': 'SE-24-Y-C-II', '2503': 'SE-24-Y-C-III', '2539': 'SE-24-Y-C-IV', '2540': 'SE-24-Y-C-V', '2541': 'SE-24-Y-C-VI', '2504': 'SE-24-Y-D-I', '2505': 'SE-24-Y-D-II', '2542': 'SE-24-Y-D-IV', '2543': 'SE-24-Y-D-V', '697': 'SB-20-V-A-I', '698': 'SB-20-V-A-II', '699': 'SB-20-V-A-III', '767': 'SB-20-V-A-IV', '768': 'SB-20-V-A-V', '769': 'SB-20-V-A-VI', '700': 'SB-20-V-B-I', '701': 'SB-20-V-B-II', '702': 'SB-20-V-B-III', '770': 'SB-20-V-B-IV', '771': 'SB-20-V-B-V', '772': 'SB-20-V-B-VI', '840': 'SB-20-V-C-I', '841': 'SB-20-V-C-II', '842': 'SB-20-V-C-III', '917': 'SB-20-V-C-IV', '918': 'SB-20-V-C-V', '919': 'SB-20-V-C-VI', '843': 'SB-20-V-D-I', '844': 'SB-20-V-D-II', '845': 'SB-20-V-D-III', '920': 'SB-20-V-D-IV', '921': 'SB-20-V-D-V', '922': 'SB-20-V-D-VI', '703': 'SB-20-X-A-I', '704': 'SB-20-X-A-II', '705': 'SB-20-X-A-III', '773': 'SB-20-X-A-IV', '774': 'SB-20-X-A-V', '775': 'SB-20-X-A-VI', '706': 'SB-20-X-B-I', '707': 'SB-20-X-B-II', '708': 'SB-20-X-B-III', '776': 'SB-20-X-B-IV', '777': 'SB-20-X-B-V', '778': 'SB-20-X-B-VI', '846': 'SB-20-X-C-I', '847': 'SB-20-X-C-II', '848': 'SB-20-X-C-III', '923': 'SB-20-X-C-IV', '924': 'SB-20-X-C-V', '925': 'SB-20-X-C-VI', '849': 'SB-20-X-D-I', '850': 'SB-20-X-D-II', '851': 'SB-20-X-D-III', '926': 'SB-20-X-D-IV', '927': 'SB-20-X-D-V', '928': 'SB-20-X-D-VI', '994': 'SB-20-Y-A-I', '995': 'SB-20-Y-A-II', '996': 'SB-20-Y-A-III', '1073': 'SB-20-Y-A-IV', '1074': 'SB-20-Y-A-V', '1075': 'SB-20-Y-A-VI', '997': 'SB-20-Y-B-I', '998': 'SB-20-Y-B-II', '999': 'SB-20-Y-B-III', '1076': 'SB-20-Y-B-IV', '1077': 'SB-20-Y-B-V', '1078': 'SB-20-Y-B-VI', '1152': 'SB-20-Y-C-I', '1153': 'SB-20-Y-C-II', '1154': 'SB-20-Y-C-III', '1231': 'SB-20-Y-C-IV', '1232': 'SB-20-Y-C-V', '1233': 'SB-20-Y-C-VI', '1155': 'SB-20-Y-D-I', '1156': 'SB-20-Y-D-II', '1157': 'SB-20-Y-D-III', '1234': 'SB-20-Y-D-IV', '1235': 'SB-20-Y-D-V', '1236': 'SB-20-Y-D-VI', '1000': 'SB-20-Z-A-I', '1001': 'SB-20-Z-A-II', '1002': 'SB-20-Z-A-III', '1079': 'SB-20-Z-A-IV', '1080': 'SB-20-Z-A-V', '1081': 'SB-20-Z-A-VI', '1003': 'SB-20-Z-B-I', '1004': 'SB-20-Z-B-II', '1005': 'SB-20-Z-B-III', '1082': 'SB-20-Z-B-IV', '1083': 'SB-20-Z-B-V', '1084': 'SB-20-Z-B-VI', '1158': 'SB-20-Z-C-I', '1159': 'SB-20-Z-C-II', '1160': 'SB-20-Z-C-III', '1237': 'SB-20-Z-C-IV', '1238': 'SB-20-Z-C-V', '1239': 'SB-20-Z-C-VI', '1161': 'SB-20-Z-D-I', '1162': 'SB-20-Z-D-II', '1163': 'SB-20-Z-D-III', '1240': 'SB-20-Z-D-IV', '1241': 'SB-20-Z-D-V', '1242': 'SB-20-Z-D-VI', '2544': 'SF-21-V-B-I', '2545': 'SF-21-V-B-II', '2546': 'SF-21-V-B-III', '2580-A': 'SF-21-V-B-IV', '2581': 'SF-21-V-B-V', '2582': 'SF-21-V-B-VI', '2617': 'SF-21-V-D-II', '2618': 'SF-21-V-D-III', '2652': 'SF-21-V-D-V', '2653': 'SF-21-V-D-VI', '2547': 'SF-21-X-A-I', '2548': 'SF-21-X-A-II', '2549': 'SF-21-X-A-III', '2583': 'SF-21-X-A-IV', '2584': 'SF-21-X-A-V', '2585': 'SF-21-X-A-VI', '2550': 'SF-21-X-B-I', '2551': 'SF-21-X-B-II', '2552': 'SF-21-X-B-III', '2586': 'SF-21-X-B-IV', '2587': 'SF-21-X-B-V', '2588': 'SF-21-X-B-VI', '2619': 'SF-21-X-C-I', '2620': 'SF-21-X-C-II', '2621': 'SF-21-X-C-III', '2654': 'SF-21-X-C-IV', '2655': 'SF-21-X-C-V', '2656': 'SF-21-X-C-VI', '2622': 'SF-21-X-D-I', '2623': 'SF-21-X-D-II', '2624': 'SF-21-X-D-III', '2657': 'SF-21-X-D-IV', '2658': 'SF-21-X-D-V', '2659': 'SF-21-X-D-VI', '2685-B': 'SF-21-Y-B-I', '2686': 'SF-21-Y-B-II', '2687': 'SF-21-Y-B-III', '2688': 'SF-21-Z-A-I', '2689': 'SF-21-Z-A-II', '2690': 'SF-21-Z-A-III', '2720': 'SF-21-Z-A-VI', '2691': 'SF-21-Z-B-I', '2692': 'SF-21-Z-B-II', '2693': 'SF-21-Z-B-III', '2721': 'SF-21-Z-B-IV', '2722': 'SF-21-Z-B-V', '2723': 'SF-21-Z-B-VI', '2749': 'SF-21-Z-C-III', '2775': 'SF-21-Z-C-VI', '2750': 'SF-21-Z-D-I', '2751': 'SF-21-Z-D-II', '2752': 'SF-21-Z-D-III', '2776': 'SF-21-Z-D-IV', '2777': 'SF-21-Z-D-V', '2778': 'SF-21-Z-D-VI', '685A': 'SB-19-V-A-I', '686': 'SB-19-V-A-II', '687': 'SB-19-V-A-III', '755': 'SB-19-V-A-IV', '756': 'SB-19-V-A-V', '757': 'SB-19-V-A-VI', '688': 'SB-19-V-B-I', '689': 'SB-19-V-B-II', '690': 'SB-19-V-B-III', '758': 'SB-19-V-B-IV', '759': 'SB-19-V-B-V', '760': 'SB-19-V-B-VI', '828': 'SB-19-V-C-I', '829': 'SB-19-V-C-II', '830': 'SB-19-V-C-III', '905': 'SB-19-V-C-IV', '906': 'SB-19-V-C-V', '907': 'SB-19-V-C-VI', '831': 'SB-19-V-D-I', '832': 'SB-19-V-D-II', '833': 'SB-19-V-D-III', '908': 'SB-19-V-D-IV', '909': 'SB-19-V-D-V', '910': 'SB-19-V-D-VI', '691': 'SB-19-X-A-I', '692': 'SB-19-X-A-II', '693': 'SB-19-X-A-III', '761': 'SB-19-X-A-IV', '762': 'SB-19-X-A-V', '763': 'SB-19-X-A-VI', '694': 'SB-19-X-B-I', '695': 'SB-19-X-B-II', '696': 'SB-19-X-B-III', '764': 'SB-19-X-B-IV', '765': 'SB-19-X-B-V', '766': 'SB-19-X-B-VI', '834': 'SB-19-X-C-I', '835': 'SB-19-X-C-II', '836': 'SB-19-X-C-III', '911': 'SB-19-X-C-IV', '912': 'SB-19-X-C-V', '913': 'SB-19-X-C-VI', '837': 'SB-19-X-D-I', '838': 'SB-19-X-D-II', '839': 'SB-19-X-D-III', '914': 'SB-19-X-D-IV', '915': 'SB-19-X-D-V', '916': 'SB-19-X-D-VI', '982': 'SB-19-Y-A-I', '983': 'SB-19-Y-A-II', '984': 'SB-19-Y-A-III', '1061': 'SB-19-Y-A-IV', '1062': 'SB-19-Y-A-V', '1063': 'SB-19-Y-A-VI', '985': 'SB-19-Y-B-I', '986': 'SB-19-Y-B-II', '987': 'SB-19-Y-B-III', '1064': 'SB-19-Y-B-IV', '1065': 'SB-19-Y-B-V', '1066': 'SB-19-Y-B-VI', '1140': 'SB-19-Y-C-I', '1141': 'SB-19-Y-C-II', '1142': 'SB-19-Y-C-III', '1219': 'SB-19-Y-C-IV', '1220': 'SB-19-Y-C-V', '1221': 'SB-19-Y-C-VI', '1143': 'SB-19-Y-D-I', '1144': 'SB-19-Y-D-II', '1145': 'SB-19-Y-D-III', '1222': 'SB-19-Y-D-IV', '1223': 'SB-19-Y-D-V', '1224': 'SB-19-Y-D-VI', '988': 'SB-19-Z-A-I', '989': 'SB-19-Z-A-II', '990': 'SB-19-Z-A-III', '1067': 'SB-19-Z-A-IV', '1068': 'SB-19-Z-A-V', '1069': 'SB-19-Z-A-VI', '991': 'SB-19-Z-B-I', '992': 'SB-19-Z-B-II', '993': 'SB-19-Z-B-III', '1070': 'SB-19-Z-B-IV', '1071': 'SB-19-Z-B-V', '1072': 'SB-19-Z-B-VI', '1146': 'SB-19-Z-C-I', '1147': 'SB-19-Z-C-II', '1148': 'SB-19-Z-C-III', '1225': 'SB-19-Z-C-IV', '1226': 'SB-19-Z-C-V', '1227': 'SB-19-Z-C-VI', '1149': 'SB-19-Z-D-I', '1150': 'SB-19-Z-D-II', '1151': 'SB-19-Z-D-III', '1228': 'SB-19-Z-D-IV', '1229': 'SB-19-Z-D-V', '1230': 'SB-19-Z-D-VI', '1298': 'SC-19-V-A-I', '1299': 'SC-19-V-A-II', '1300': 'SC-19-V-A-III', '1376': 'SC-19-V-A-IV', '1377': 'SC-19-V-A-V', '1378': 'SC-19-V-A-VI', '1301': 'SC-19-V-B-I', '1302': 'SC-19-V-B-II', '1303': 'SC-19-V-B-III', '1379': 'SC-19-V-B-IV', '1380': 'SC-19-V-B-V', '1381': 'SC-19-V-B-VI', '1453': 'SC-19-V-C-I', '1454': 'SC-19-V-C-II', '1455': 'SC-19-V-C-III', '1528': 'SC-19-V-C-IV', '1529': 'SC-19-V-C-V', '1530': 'SC-19-V-C-VI', '1456': 'SC-19-V-D-I', '1457': 'SC-19-V-D-II', '1458': 'SC-19-V-D-III', '1531': 'SC-19-V-D-IV', '1532': 'SC-19-V-D-V', '1533': 'SC-19-V-D-VI', '1304': 'SC-19-X-A-I', '1305': 'SC-19-X-A-II', '1306': 'SC-19-X-A-III', '1382': 'SC-19-X-A-IV', '1383': 'SC-19-X-A-V', '1384': 'SC-19-X-A-VI', '1307': 'SC-19-X-B-I', '1308': 'SC-19-X-B-II', '1309': 'SC-19-X-B-III', '1385': 'SC-19-X-B-IV', '1386': 'SC-19-X-B-V', '1387': 'SC-19-X-B-VI', '1459': 'SC-19-X-C-I', '1460': 'SC-19-X-C-II', '1461': 'SC-19-X-C-III', '1534': 'SC-19-X-C-IV', '1535': 'SC-19-X-C-V', '1536': 'SC-19-X-C-VI', '1462': 'SC-19-X-D-I', '1463': 'SC-19-X-D-II', '1464': 'SC-19-X-D-III', '1537': 'SC-19-X-D-IV', '1538': 'SC-19-X-D-V', '1539': 'SC-19-X-D-VI', '1601': 'SC-19-Y-A-III', '1669': 'SC-19-Y-A-VI', '1602': 'SC-19-Y-B-I', '1603': 'SC-19-Y-B-II', '1604': 'SC-19-Y-B-III', '1670': 'SC-19-Y-B-IV', '1671': 'SC-19-Y-B-V', '1672': 'SC-19-Y-B-VI', '1735': 'SC-19-Y-D-I', '1735A': 'SC-19-Y-D-III', '1605': 'SC-19-Z-A-I', '1606': 'SC-19-Z-A-II', '1607': 'SC-19-Z-A-III', '1673': 'SC-19-Z-A-IV', '1674': 'SC-19-Z-A-V', '1675': 'SC-19-Z-A-VI', '1608': 'SC-19-Z-B-I', '1609': 'SC-19-Z-B-II', '1736': 'SC-19-Z-C-I', '1737': 'SC-19-Z-C-II', '733': 'SB-23-V-A-I', '734': 'SB-23-V-A-II', '735': 'SB-23-V-A-III', '803': 'SB-23-V-A-IV', '804': 'SB-23-V-A-V', '805': 'SB-23-V-A-VI', '736': 'SB-23-V-B-I', '737': 'SB-23-V-B-II', '738': 'SB-23-V-B-III', '806': 'SB-23-V-B-IV', '807': 'SB-23-V-B-V', '808': 'SB-23-V-B-VI', '876': 'SB-23-V-C-I', '877': 'SB-23-V-C-II', '878': 'SB-23-V-C-III', '953': 'SB-23-V-C-IV', '954': 'SB-23-V-C-V', '955': 'SB-23-V-C-VI', '879': 'SB-23-V-D-I', '880': 'SB-23-V-D-II', '881': 'SB-23-V-D-III', '956': 'SB-23-V-D-IV', '957': 'SB-23-V-D-V', '958': 'SB-23-V-D-VI', '739': 'SB-23-X-A-I', '740': 'SB-23-X-A-II', '741': 'SB-23-X-A-III', '809': 'SB-23-X-A-IV', '810': 'SB-23-X-A-V', '811': 'SB-23-X-A-VI', '742': 'SB-23-X-B-I', '743': 'SB-23-X-B-II', '744': 'SB-23-X-B-III', '812': 'SB-23-X-B-IV', '813': 'SB-23-X-B-V', '814': 'SB-23-X-B-VI', '882': 'SB-23-X-C-I', '883': 'SB-23-X-C-II', '884': 'SB-23-X-C-III', '959': 'SB-23-X-C-IV', '960': 'SB-23-X-C-V', '961': 'SB-23-X-C-VI', '885': 'SB-23-X-D-I', '886': 'SB-23-X-D-II', '887': 'SB-23-X-D-III', '962': 'SB-23-X-D-IV', '963': 'SB-23-X-D-V', '964': 'SB-23-X-D-VI', '1030': 'SB-23-Y-A-I', '1031': 'SB-23-Y-A-II', '1032': 'SB-23-Y-A-III', '1109': 'SB-23-Y-A-IV', '1110': 'SB-23-Y-A-V', '1111': 'SB-23-Y-A-VI', '1033': 'SB-23-Y-B-I', '1034': 'SB-23-Y-B-II', '1035': 'SB-23-Y-B-III', '1112': 'SB-23-Y-B-IV', '1113': 'SB-23-Y-B-V', '1114': 'SB-23-Y-B-VI', '1188': 'SB-23-Y-C-I', '1189': 'SB-23-Y-C-II', '1190': 'SB-23-Y-C-III', '1267': 'SB-23-Y-C-IV', '1268': 'SB-23-Y-C-V', '1269': 'SB-23-Y-C-VI', '1191': 'SB-23-Y-D-I', '1192': 'SB-23-Y-D-II', '1193': 'SB-23-Y-D-III', '1270': 'SB-23-Y-D-IV', '1271': 'SB-23-Y-D-V', '1272': 'SB-23-Y-D-VI', '1036': 'SB-23-Z-A-I', '1037': 'SB-23-Z-A-II', '1038': 'SB-23-Z-A-III', '1115': 'SB-23-Z-A-IV', '1116': 'SB-23-Z-A-V', '1117': 'SB-23-Z-A-VI', '1039': 'SB-23-Z-B-I', '1040': 'SB-23-Z-B-II', '1041': 'SB-23-Z-B-III', '1118': 'SB-23-Z-B-IV', '1119': 'SB-23-Z-B-V', '1120': 'SB-23-Z-B-VI', '1194': 'SB-23-Z-C-I', '1195': 'SB-23-Z-C-II', '1196': 'SB-23-Z-C-III', '1273': 'SB-23-Z-C-IV', '1274': 'SB-23-Z-C-V', '1275': 'SB-23-Z-C-VI', '1197': 'SB-23-Z-D-I', '1198': 'SB-23-Z-D-II', '1199': 'SB-23-Z-D-III', '1276': 'SB-23-Z-D-IV', '1277': 'SB-23-Z-D-V', '1278': 'SB-23-Z-D-VI', '1886': 'SD-23-V-A-I', '1887': 'SD-23-V-A-II', '1888': 'SD-23-V-A-III', '1940': 'SD-23-V-A-IV', '1941': 'SD-23-V-A-V', '1942': 'SD-23-V-A-VI', '1889': 'SD-23-V-B-I', '1890': 'SD-23-V-B-II', '1891': 'SD-23-V-B-III', '1943': 'SD-23-V-B-IV', '1944': 'SD-23-V-B-V', '1945': 'SD-23-V-B-VI', '1991': 'SD-23-V-C-I', '1992': 'SD-23-V-C-II', '1993': 'SD-23-V-C-III', '2038': 'SD-23-V-C-IV', '2039': 'SD-23-V-C-V', '2040': 'SD-23-V-C-VI', '1994': 'SD-23-V-D-I', '1995': 'SD-23-V-D-II', '1996': 'SD-23-V-D-III', '2041': 'SD-23-V-D-IV', '2042': 'SD-23-V-D-V', '2043': 'SD-23-V-D-VI', '1892': 'SD-23-X-A-I', '1893': 'SD-23-X-A-II', '1894': 'SD-23-X-A-III', '1946': 'SD-23-X-A-IV', '1947': 'SD-23-X-A-V', '1948': 'SD-23-X-A-VI', '1895': 'SD-23-X-B-I', '1896': 'SD-23-X-B-II', '1897': 'SD-23-X-B-III', '1949': 'SD-23-X-B-IV', '1950': 'SD-23-X-B-V', '1951': 'SD-23-X-B-VI', '1997': 'SD-23-X-C-I', '1998': 'SD-23-X-C-II', '1999': 'SD-23-X-C-III', '2044': 'SD-23-X-C-IV', '2045': 'SD-23-X-C-V', '2046': 'SD-23-X-C-VI', '2000': 'SD-23-X-D-I', '2001': 'SD-23-X-D-II', '2002': 'SD-23-X-D-III', '2047': 'SD-23-X-D-IV', '2048': 'SD-23-X-D-V', '2049': 'SD-23-X-D-VI', '2082': 'SD-23-Y-A-I', '2083': 'SD-23-Y-A-II', '2084': 'SD-23-Y-A-III', '2126': 'SD-23-Y-A-IV', '2127': 'SD-23-Y-A-V', '2128': 'SD-23-Y-A-VI', '2085': 'SD-23-Y-B-I', '2086': 'SD-23-Y-B-II', '2087': 'SD-23-Y-B-III', '2129': 'SD-23-Y-B-IV', '2130': 'SD-23-Y-B-V', '2131': 'SD-23-Y-B-VI', '2171': 'SD-23-Y-C-I', '2172': 'SD-23-Y-C-II', '2173': 'SD-23-Y-C-III', '2215': 'SD-23-Y-C-IV', '2216': 'SD-23-Y-C-V', '2217': 'SD-23-Y-C-VI', '2174': 'SD-23-Y-D-I', '2175': 'SD-23-Y-D-II', '2176': 'SD-23-Y-D-III', '2218': 'SD-23-Y-D-IV', '2219': 'SD-23-Y-D-V', '2220': 'SD-23-Y-D-VI', '2088': 'SD-23-Z-A-I', '2089': 'SD-23-Z-A-II', '2090': 'SD-23-Z-A-III', '2132': 'SD-23-Z-A-IV', '2133': 'SD-23-Z-A-V', '2134': 'SD-23-Z-A-VI', '2091': 'SD-23-Z-B-I', '2092': 'SD-23-Z-B-II', '2093': 'SD-23-Z-B-III', '2135': 'SD-23-Z-B-IV', '2136': 'SD-23-Z-B-V', '2137': 'SD-23-Z-B-VI', '2177': 'SD-23-Z-C-I', '2178': 'SD-23-Z-C-II', '2179': 'SD-23-Z-C-III', '2221': 'SD-23-Z-C-IV', '2222': 'SD-23-Z-C-V', '2223': 'SD-23-Z-C-VI', '2180': 'SD-23-Z-D-I', '2181': 'SD-23-Z-D-II', '2182': 'SD-23-Z-D-III', '2224': 'SD-23-Z-D-IV', '2225': 'SD-23-Z-D-V', '2226': 'SD-23-Z-D-VI', '721': 'SB-22-V-A-I', '722': 'SB-22-V-A-II', '723': 'SB-22-V-A-III', '791': 'SB-22-V-A-IV', '792': 'SB-22-V-A-V', '793': 'SB-22-V-A-VI', '724': 'SB-22-V-B-I', '725': 'SB-22-V-B-II', '726': 'SB-22-V-B-III', '794': 'SB-22-V-B-IV', '795': 'SB-22-V-B-V', '796': 'SB-22-V-B-VI', '864': 'SB-22-V-C-I', '865': 'SB-22-V-C-II', '866': 'SB-22-V-C-III', '941': 'SB-22-V-C-IV', '942': 'SB-22-V-C-V', '943': 'SB-22-V-C-VI', '867': 'SB-22-V-D-I', '868': 'SB-22-V-D-II', '869': 'SB-22-V-D-III', '944': 'SB-22-V-D-IV', '945': 'SB-22-V-D-V', '946': 'SB-22-V-D-VI', '727': 'SB-22-X-A-I', '728': 'SB-22-X-A-II', '729': 'SB-22-X-A-III', '797': 'SB-22-X-A-IV', '798': 'SB-22-X-A-V', '799': 'SB-22-X-A-VI', '730': 'SB-22-X-B-I', '731': 'SB-22-X-B-II', '732': 'SB-22-X-B-III', '800': 'SB-22-X-B-IV', '801': 'SB-22-X-B-V', '802': 'SB-22-X-B-VI', '870': 'SB-22-X-C-I', '871': 'SB-22-X-C-II', '872': 'SB-22-X-C-III', '947': 'SB-22-X-C-IV', '948': 'SB-22-X-C-V', '949': 'SB-22-X-C-VI', '873': 'SB-22-X-D-I', '874': 'SB-22-X-D-II', '875': 'SB-22-X-D-III', '950': 'SB-22-X-D-IV', '951': 'SB-22-X-D-V', '952': 'SB-22-X-D-VI', '1018': 'SB-22-Y-A-I', '1019': 'SB-22-Y-A-II', '1020': 'SB-22-Y-A-III', '1097': 'SB-22-Y-A-IV', '1098': 'SB-22-Y-A-V', '1099': 'SB-22-Y-A-VI', '1021': 'SB-22-Y-B-I', '1022': 'SB-22-Y-B-II', '1023': 'SB-22-Y-B-III', '1100': 'SB-22-Y-B-IV', '1101': 'SB-22-Y-B-V', '1102': 'SB-22-Y-B-VI', '1176': 'SB-22-Y-C-I', '1177': 'SB-22-Y-C-II', '1178': 'SB-22-Y-C-III', '1255': 'SB-22-Y-C-IV', '1256': 'SB-22-Y-C-V', '1257': 'SB-22-Y-C-VI', '1179': 'SB-22-Y-D-I', '1180': 'SB-22-Y-D-II', '1181': 'SB-22-Y-D-III', '1258': 'SB-22-Y-D-IV', '1259': 'SB-22-Y-D-V', '1260': 'SB-22-Y-D-VI', '1024': 'SB-22-Z-A-I', '1025': 'SB-22-Z-A-II', '1026': 'SB-22-Z-A-III', '1103': 'SB-22-Z-A-IV', '1104': 'SB-22-Z-A-V', '1105': 'SB-22-Z-A-VI', '1027': 'SB-22-Z-B-I', '1028': 'SB-22-Z-B-II', '1029': 'SB-22-Z-B-III', '1106': 'SB-22-Z-B-IV', '1107': 'SB-22-Z-B-V', '1108': 'SB-22-Z-B-VI', '1182': 'SB-22-Z-C-I', '1183': 'SB-22-Z-C-II', '1184': 'SB-22-Z-C-III', '1261': 'SB-22-Z-C-IV', '1262': 'SB-22-Z-C-V', '1263': 'SB-22-Z-C-VI', '1185': 'SB-22-Z-D-I', '1186': 'SB-22-Z-D-II', '1187': 'SB-22-Z-D-III', '1264': 'SB-22-Z-D-IV', '1265': 'SB-22-Z-D-V', '1266': 'SB-22-Z-D-VI', '257': 'SA-20-V-A-I', '258': 'SA-20-V-A-II', '259': 'SA-20-V-A-III', '301': 'SA-20-V-A-IV', '302': 'SA-20-V-A-V', '303': 'SA-20-V-A-VI', '260': 'SA-20-V-B-I', '261': 'SA-20-V-B-II', '262': 'SA-20-V-B-III', '304': 'SA-20-V-B-IV', '305': 'SA-20-V-B-V', '306': 'SA-20-V-B-VI', '349': 'SA-20-V-C-I', '350': 'SA-20-V-C-II', '351': 'SA-20-V-C-III', '400': 'SA-20-V-C-IV', '401': 'SA-20-V-C-V', '402': 'SA-20-V-C-VI', '352': 'SA-20-V-D-I', '353': 'SA-20-V-D-II', '354': 'SA-20-V-D-III', '403': 'SA-20-V-D-IV', '404': 'SA-20-V-D-V', '405': 'SA-20-V-D-VI', '263': 'SA-20-X-A-I', '264': 'SA-20-X-A-II', '265': 'SA-20-X-A-III', '307': 'SA-20-X-A-IV', '308': 'SA-20-X-A-V', '309': 'SA-20-X-A-VI', '266': 'SA-20-X-B-I', '267': 'SA-20-X-B-II', '268': 'SA-20-X-B-III', '310': 'SA-20-X-B-IV', '311': 'SA-20-X-B-V', '312': 'SA-20-X-B-VI', '355': 'SA-20-X-C-I', '356': 'SA-20-X-C-II', '357': 'SA-20-X-C-III', '406': 'SA-20-X-C-IV', '407': 'SA-20-X-C-V', '408': 'SA-20-X-C-VI', '358': 'SA-20-X-D-I', '359': 'SA-20-X-D-II', '360': 'SA-20-X-D-III', '409': 'SA-20-X-D-IV', '410': 'SA-20-X-D-V', '411': 'SA-20-X-D-VI', '452': 'SA-20-Y-A-I', '453': 'SA-20-Y-A-II', '454': 'SA-20-Y-A-III', '506': 'SA-20-Y-A-IV', '507': 'SA-20-Y-A-V', '508': 'SA-20-Y-A-VI', '455': 'SA-20-Y-B-I', '456': 'SA-20-Y-B-II', '457': 'SA-20-Y-B-III', '509': 'SA-20-Y-B-IV', '510': 'SA-20-Y-B-V', '511': 'SA-20-Y-B-VI', '567': 'SA-20-Y-C-I', '568': 'SA-20-Y-C-II', '569': 'SA-20-Y-C-III', '630': 'SA-20-Y-C-IV', '631': 'SA-20-Y-C-V', '632': 'SA-20-Y-C-VI', '570': 'SA-20-Y-D-I', '571': 'SA-20-Y-D-II', '572': 'SA-20-Y-D-III', '633': 'SA-20-Y-D-IV', '634': 'SA-20-Y-D-V', '635': 'SA-20-Y-D-VI', '458': 'SA-20-Z-A-I', '459': 'SA-20-Z-A-II', '460': 'SA-20-Z-A-III', '512': 'SA-20-Z-A-IV', '513': 'SA-20-Z-A-V', '514': 'SA-20-Z-A-VI', '461': 'SA-20-Z-B-I', '462': 'SA-20-Z-B-II', '463': 'SA-20-Z-B-III', '515': 'SA-20-Z-B-IV', '516': 'SA-20-Z-B-V', '517': 'SA-20-Z-B-VI', '573': 'SA-20-Z-C-I', '574': 'SA-20-Z-C-II', '575': 'SA-20-Z-C-III', '636': 'SA-20-Z-C-IV', '637': 'SA-20-Z-C-V', '638': 'SA-20-Z-C-VI', '576': 'SA-20-Z-D-I', '577': 'SA-20-Z-D-II', '578': 'SA-20-Z-D-III', '639': 'SA-20-Z-D-IV', '640': 'SA-20-Z-D-V', '641': 'SA-20-Z-D-VI', '281': 'SA-22-V-A-I', '282': 'SA-22-V-A-II', '283': 'SA-22-V-A-III', '325': 'SA-22-V-A-IV', '326': 'SA-22-V-A-V', '327': 'SA-22-V-A-VI', '284': 'SA-22-V-B-I', '285': 'SA-22-V-B-II', '286': 'SA-22-V-B-III', '328': 'SA-22-V-B-IV', '329': 'SA-22-V-B-V', '330': 'SA-22-V-B-VI', '373': 'SA-22-V-C-I', '374': 'SA-22-V-C-II', '375': 'SA-22-V-C-III', '424': 'SA-22-V-C-IV', '425': 'SA-22-V-C-V', '426': 'SA-22-V-C-VI', '376': 'SA-22-V-D-I', '377': 'SA-22-V-D-II', '378': 'SA-22-V-D-III', '427': 'SA-22-V-D-IV', '428': 'SA-22-V-D-V', '429': 'SA-22-V-D-VI', '287': 'SA-22-X-A-I', '288': 'SA-22-X-A-II', '289': 'SA-22-X-A-III', '331': 'SA-22-X-A-IV', '332': 'SA-22-X-A-V', '333': 'SA-22-X-A-VI', '290': 'SA-22-X-B-I', '291': 'SA-22-X-B-II', '292': 'SA-22-X-B-III', '334': 'SA-22-X-B-IV', '335': 'SA-22-X-B-V', '336': 'SA-22-X-B-VI', '379': 'SA-22-X-C-I', '380': 'SA-22-X-C-II', '381': 'SA-22-X-C-III', '430': 'SA-22-X-C-IV', '431': 'SA-22-X-C-V', '432': 'SA-22-X-C-VI', '382': 'SA-22-X-D-I', '383': 'SA-22-X-D-II', '384': 'SA-22-X-D-III', '433': 'SA-22-X-D-IV', '434': 'SA-22-X-D-V', '435': 'SA-22-X-D-VI', '476': 'SA-22-Y-A-I', '477': 'SA-22-Y-A-II', '478': 'SA-22-Y-A-III', '530': 'SA-22-Y-A-IV', '531': 'SA-22-Y-A-V', '532': 'SA-22-Y-A-VI', '479': 'SA-22-Y-B-I', '480': 'SA-22-Y-B-II', '481': 'SA-22-Y-B-III', '533': 'SA-22-Y-B-IV', '534': 'SA-22-Y-B-V', '535': 'SA-22-Y-B-VI', '591': 'SA-22-Y-C-I', '592': 'SA-22-Y-C-II', '593': 'SA-22-Y-C-III', '654': 'SA-22-Y-C-IV', '655': 'SA-22-Y-C-V', '656': 'SA-22-Y-C-VI', '594': 'SA-22-Y-D-I', '595': 'SA-22-Y-D-II', '596': 'SA-22-Y-D-III', '657': 'SA-22-Y-D-IV', '658': 'SA-22-Y-D-V', '659': 'SA-22-Y-D-VI', '482': 'SA-22-Z-A-I', '483': 'SA-22-Z-A-II', '484': 'SA-22-Z-A-III', '536': 'SA-22-Z-A-IV', '537': 'SA-22-Z-A-V', '538': 'SA-22-Z-A-VI', '485': 'SA-22-Z-B-I', '486': 'SA-22-Z-B-II', '487': 'SA-22-Z-B-III', '539': 'SA-22-Z-B-IV', '540': 'SA-22-Z-B-V', '541': 'SA-22-Z-B-VI', '597': 'SA-22-Z-C-I', '598': 'SA-22-Z-C-II', '599': 'SA-22-Z-C-III', '660': 'SA-22-Z-C-IV', '661': 'SA-22-Z-C-V', '662': 'SA-22-Z-C-VI', '600': 'SA-22-Z-D-I', '601': 'SA-22-Z-D-II', '602': 'SA-22-Z-D-III', '663': 'SA-22-Z-D-IV', '664': 'SA-22-Z-D-V', '665': 'SA-22-Z-D-VI', '745': 'SB-24-V-A-I', '746': 'SB-24-V-A-II', '747': 'SB-24-V-A-III', '815': 'SB-24-V-A-IV', '816': 'SB-24-V-A-V', '817': 'SB-24-V-A-VI', '748': 'SB-24-V-B-I', '749': 'SB-24-V-B-II', '750': 'SB-24-V-B-III', '818': 'SB-24-V-B-IV', '819': 'SB-24-V-B-V', '820': 'SB-24-V-B-VI', '888': 'SB-24-V-C-I', '889': 'SB-24-V-C-II', '890': 'SB-24-V-C-III', '965': 'SB-24-V-C-IV', '966': 'SB-24-V-C-V', '967': 'SB-24-V-C-VI', '891': 'SB-24-V-D-I', '892': 'SB-24-V-D-II', '893': 'SB-24-V-D-III', '968': 'SB-24-V-D-IV', '969': 'SB-24-V-D-V', '970': 'SB-24-V-D-VI', '751': 'SB-24-X-A-I', '752': 'SB-24-X-A-II', '752-A': 'SB-24-X-A-III', '821': 'SB-24-X-A-IV', '822': 'SB-24-X-A-V', '823': 'SB-24-X-A-VI', '824': 'SB-24-X-B-IV', '825': 'SB-24-X-B-V', '894': 'SB-24-X-C-I', '895': 'SB-24-X-C-II', '896': 'SB-24-X-C-III', '971': 'SB-24-X-C-IV', '972': 'SB-24-X-C-V', '973': 'SB-24-X-C-VI', '897': 'SB-24-X-D-I', '898': 'SB-24-X-D-II', '899': 'SB-24-X-D-III', '974': 'SB-24-X-D-IV', '975': 'SB-24-X-D-V', '976': 'SB-24-X-D-VI', '1042': 'SB-24-Y-A-I', '1043': 'SB-24-Y-A-II', '1044': 'SB-24-Y-A-III', '1121': 'SB-24-Y-A-IV', '1122': 'SB-24-Y-A-V', '1123': 'SB-24-Y-A-VI', '1045': 'SB-24-Y-B-I', '1046': 'SB-24-Y-B-II', '1047': 'SB-24-Y-B-III', '1124': 'SB-24-Y-B-IV', '1125': 'SB-24-Y-B-V', '1126': 'SB-24-Y-B-VI', '1200': 'SB-24-Y-C-I', '1201': 'SB-24-Y-C-II', '1202': 'SB-24-Y-C-III', '1279': 'SB-24-Y-C-IV', '1280': 'SB-24-Y-C-V', '1281': 'SB-24-Y-C-VI', '1203': 'SB-24-Y-D-I', '1204': 'SB-24-Y-D-II', '1205': 'SB-24-Y-D-III', '1282': 'SB-24-Y-D-IV', '1283': 'SB-24-Y-D-V', '1284': 'SB-24-Y-D-VI', '1048': 'SB-24-Z-A-I', '1049': 'SB-24-Z-A-II', '1050': 'SB-24-Z-A-III', '1127': 'SB-24-Z-A-IV', '1128': 'SB-24-Z-A-V', '1129': 'SB-24-Z-A-VI', '1051': 'SB-24-Z-B-I', '1052': 'SB-24-Z-B-II', '1053': 'SB-24-Z-B-III', '1130': 'SB-24-Z-B-IV', '1131': 'SB-24-Z-B-V', '1132': 'SB-24-Z-B-VI', '1206': 'SB-24-Z-C-I', '1207': 'SB-24-Z-C-II', '1208': 'SB-24-Z-C-III', '1285': 'SB-24-Z-C-IV', '1286': 'SB-24-Z-C-V', '1287': 'SB-24-Z-C-VI', '1209': 'SB-24-Z-D-I', '1210': 'SB-24-Z-D-II', '1211': 'SB-24-Z-D-III', '1288': 'SB-24-Z-D-IV', '1289': 'SB-24-Z-D-V', '1290': 'SB-24-Z-D-VI', '2553': 'SF-22-V-A-I', '2554': 'SF-22-V-A-II', '2555': 'SF-22-V-A-III', '2589': 'SF-22-V-A-IV', '2590': 'SF-22-V-A-V', '2591': 'SF-22-V-A-VI', '2556': 'SF-22-V-B-I', '2557': 'SF-22-V-B-II', '2558': 'SF-22-V-B-III', '2592': 'SF-22-V-B-IV', '2593': 'SF-22-V-B-V', '2594': 'SF-22-V-B-VI', '2625': 'SF-22-V-C-I', '2626': 'SF-22-V-C-II', '2627': 'SF-22-V-C-III', '2660': 'SF-22-V-C-IV', '2661': 'SF-22-V-C-V', '2662': 'SF-22-V-C-VI', '2628': 'SF-22-V-D-I', '2629': 'SF-22-V-D-II', '2630': 'SF-22-V-D-III', '2663': 'SF-22-V-D-IV', '2664': 'SF-22-V-D-V', '2665': 'SF-22-V-D-VI', '2559': 'SF-22-X-A-I', '2560': 'SF-22-X-A-II', '2561': 'SF-22-X-A-III', '2595': 'SF-22-X-A-IV', '2596': 'SF-22-X-A-V', '2597': 'SF-22-X-A-VI', '2562': 'SF-22-X-B-I', '2563': 'SF-22-X-B-II', '2564': 'SF-22-X-B-III', '2598': 'SF-22-X-B-IV', '2599': 'SF-22-X-B-V', '2600': 'SF-22-X-B-VI', '2631': 'SF-22-X-C-I', '2632': 'SF-22-X-C-II', '2633': 'SF-22-X-C-III', '2666': 'SF-22-X-C-IV', '2667': 'SF-22-X-C-V', '2668': 'SF-22-X-C-VI', '2634': 'SF-22-X-D-I', '2635': 'SF-22-X-D-II', '2636': 'SF-22-X-D-III', '2669': 'SF-22-X-D-IV', '2670': 'SF-22-X-D-V', '2671': 'SF-22-X-D-VI', '2694': 'SF-22-Y-A-I', '2695': 'SF-22-Y-A-II', '2696': 'SF-22-Y-A-III', '2724': 'SF-22-Y-A-IV', '2725': 'SF-22-Y-A-V', '2726': 'SF-22-Y-A-VI', '2697': 'SF-22-Y-B-I', '2698': 'SF-22-Y-B-II', '2699': 'SF-22-Y-B-III', '2727': 'SF-22-Y-B-IV', '2728': 'SF-22-Y-B-V', '2729': 'SF-22-Y-B-VI', '2753': 'SF-22-Y-C-I', '2754': 'SF-22-Y-C-II', '2755': 'SF-22-Y-C-III', '2779': 'SF-22-Y-C-IV', '2780': 'SF-22-Y-C-V', '2781': 'SF-22-Y-C-VI', '2756': 'SF-22-Y-D-I', '2757': 'SF-22-Y-D-II', '2758': 'SF-22-Y-D-III', '2782': 'SF-22-Y-D-IV', '2783': 'SF-22-Y-D-V', '2784': 'SF-22-Y-D-VI', '2700': 'SF-22-Z-A-I', '2701': 'SF-22-Z-A-II', '2702': 'SF-22-Z-A-III', '2730': 'SF-22-Z-A-IV', '2731': 'SF-22-Z-A-V', '2732': 'SF-22-Z-A-VI', '2703': 'SF-22-Z-B-I', '2704': 'SF-22-Z-B-II', '2705': 'SF-22-Z-B-III', '2733': 'SF-22-Z-B-IV', '2734': 'SF-22-Z-B-V', '2735': 'SF-22-Z-B-VI', '2759': 'SF-22-Z-C-I', '2760': 'SF-22-Z-C-II', '2761': 'SF-22-Z-C-III', '2785': 'SF-22-Z-C-IV', '2786': 'SF-22-Z-C-V', '2787': 'SF-22-Z-C-VI', '2762': 'SF-22-Z-D-I', '2763': 'SF-22-Z-D-II', '2764': 'SF-22-Z-D-III', '2788': 'SF-22-Z-D-IV', '2789': 'SF-22-Z-D-V', '2790': 'SF-22-Z-D-VI', '337': 'SA-23-V-A-IV', '338': 'SA-23-V-A-V', '339': 'SA-23-V-A-VI', '340': 'SA-23-V-B-IV', '385': 'SA-23-V-C-I', '386': 'SA-23-V-C-II', '387': 'SA-23-V-C-III', '436': 'SA-23-V-C-IV', '437': 'SA-23-V-C-V', '438': 'SA-23-V-C-VI', '388': 'SA-23-V-D-I', '389': 'SA-23-V-D-II', '390': 'SA-23-V-D-III', '439': 'SA-23-V-D-IV', '440': 'SA-23-V-D-V', '441': 'SA-23-V-D-VI', '391': 'SA-23-X-C-I', '442': 'SA-23-X-C-IV', '443': 'SA-23-X-C-V', '488': 'SA-23-Y-A-I', '489': 'SA-23-Y-A-II', '490': 'SA-23-Y-A-III', '542': 'SA-23-Y-A-IV', '543': 'SA-23-Y-A-V', '544': 'SA-23-Y-A-VI', '491': 'SA-23-Y-B-I', '492': 'SA-23-Y-B-II', '493': 'SA-23-Y-B-III', '545': 'SA-23-Y-B-IV', '546': 'SA-23-Y-B-V', '547': 'SA-23-Y-B-VI', '603': 'SA-23-Y-C-I', '604': 'SA-23-Y-C-II', '605': 'SA-23-Y-C-III', '666': 'SA-23-Y-C-IV', '667': 'SA-23-Y-C-V', '668': 'SA-23-Y-C-VI', '606': 'SA-23-Y-D-I', '607': 'SA-23-Y-D-II', '608': 'SA-23-Y-D-III', '669': 'SA-23-Y-D-IV', '670': 'SA-23-Y-D-V', '671': 'SA-23-Y-D-VI', '494': 'SA-23-Z-A-I', '495': 'SA-23-Z-A-II', '495-A': 'SA-23-Z-A-III', '548': 'SA-23-Z-A-IV', '549': 'SA-23-Z-A-V', '550': 'SA-23-Z-A-VI', '496': 'SA-23-Z-B-I', '497': 'SA-23-Z-B-II', '551': 'SA-23-Z-B-IV', '552': 'SA-23-Z-B-V', '553': 'SA-23-Z-B-VI', '609': 'SA-23-Z-C-I', '610': 'SA-23-Z-C-II', '611': 'SA-23-Z-C-III', '672': 'SA-23-Z-C-IV', '673': 'SA-23-Z-C-V', '674': 'SA-23-Z-C-VI', '612': 'SA-23-Z-D-I', '613': 'SA-23-Z-D-II', '614': 'SA-23-Z-D-III', '675': 'SA-23-Z-D-IV', '676': 'SA-23-Z-D-V', '677': 'SA-23-Z-D-VI', '2797': 'SG-21-X-B-I', '2798': 'SG-21-X-B-II', '2799': 'SG-21-X-B-III', '2816': 'SG-21-X-B-VI', '2831': 'SG-21-X-D-II', '2832': 'SG-21-X-D-III', '2846': 'SG-21-X-D-V', '2847': 'SG-21-X-D-VI', '2882-A': 'SG-21-Z-D-II', '2883': 'SG-21-Z-D-III', '2896': 'SG-21-Z-D-IV', '2897': 'SG-21-Z-D-V', '2898': 'SG-21-Z-D-VI', '1358': 'SC-24-V-A-I', '1359': 'SC-24-V-A-II', '1360': 'SC-24-V-A-III', '1436': 'SC-24-V-A-IV', '1437': 'SC-24-V-A-V', '1438': 'SC-24-V-A-VI', '1361': 'SC-24-V-B-I', '1362': 'SC-24-V-B-II', '1363': 'SC-24-V-B-III', '1439': 'SC-24-V-B-IV', '1440': 'SC-24-V-B-V', '1441': 'SC-24-V-B-VI', '1513': 'SC-24-V-C-I', '1514': 'SC-24-V-C-II', '1515': 'SC-24-V-C-III', '1588': 'SC-24-V-C-IV', '1589': 'SC-24-V-C-V', '1590': 'SC-24-V-C-VI', '1516': 'SC-24-V-D-I', '1517': 'SC-24-V-D-II', '1518': 'SC-24-V-D-III', '1591': 'SC-24-V-D-IV', '1592': 'SC-24-V-D-V', '1593': 'SC-24-V-D-VI', '1364': 'SC-24-X-A-I', '1365': 'SC-24-X-A-II', '1366': 'SC-24-X-A-III', '1442': 'SC-24-X-A-IV', '1443': 'SC-24-X-A-V', '1444': 'SC-24-X-A-VI', '1367': 'SC-24-X-B-I', '1368': 'SC-24-X-B-II', '1369': 'SC-24-X-B-III', '1445': 'SC-24-X-B-IV', '1446': 'SC-24-X-B-V', '1447': 'SC-24-X-B-VI', '1519': 'SC-24-X-C-I', '1520': 'SC-24-X-C-II', '1521': 'SC-24-X-C-III', '1594': 'SC-24-X-C-IV', '1595': 'SC-24-X-C-V', '1596': 'SC-24-X-C-VI', '1522': 'SC-24-X-D-I', '1523': 'SC-24-X-D-II', '1524': 'SC-24-X-D-III', '1597': 'SC-24-X-D-IV', '1598': 'SC-24-X-D-V', '1599': 'SC-24-X-D-VI', '1657': 'SC-24-Y-A-I', '1658': 'SC-24-Y-A-II', '1659': 'SC-24-Y-A-III', '1723': 'SC-24-Y-A-IV', '1724': 'SC-24-Y-A-V', '1725': 'SC-24-Y-A-VI', '1660': 'SC-24-Y-B-I', '1661': 'SC-24-Y-B-II', '1662': 'SC-24-Y-B-III', '1726': 'SC-24-Y-B-IV', '1727': 'SC-24-Y-B-V', '1728': 'SC-24-Y-B-VI', '1785': 'SC-24-Y-C-I', '1786': 'SC-24-Y-C-II', '1787': 'SC-24-Y-C-III', '1842': 'SC-24-Y-C-IV', '1843': 'SC-24-Y-C-V', '1844': 'SC-24-Y-C-VI', '1788': 'SC-24-Y-D-I', '1789': 'SC-24-Y-D-II', '1790': 'SC-24-Y-D-III', '1845': 'SC-24-Y-D-IV', '1846': 'SC-24-Y-D-V', '1847': 'SC-24-Y-D-VI', '1663': 'SC-24-Z-A-I', '1664': 'SC-24-Z-A-II', '1665': 'SC-24-Z-A-III', '1729': 'SC-24-Z-A-IV', '1730': 'SC-24-Z-A-V', '1731': 'SC-24-Z-A-VI', '1666': 'SC-24-Z-B-I', '1667': 'SC-24-Z-B-II', '1668': 'SC-24-Z-B-III', '1732': 'SC-24-Z-B-IV', '1733': 'SC-24-Z-B-V', '1734': 'SC-24-Z-B-VI', '1791': 'SC-24-Z-C-I', '1792': 'SC-24-Z-C-II', '1793': 'SC-24-Z-C-III', '1848': 'SC-24-Z-C-IV', '1849': 'SC-24-Z-C-V', '1850': 'SC-24-Z-C-VI', '1794': 'SC-24-Z-D-I', '1851': 'SC-24-Z-D-IV', '1346': 'SC-23-V-A-I', '1347': 'SC-23-V-A-II', '1348': 'SC-23-V-A-III', '1424': 'SC-23-V-A-IV', '1425': 'SC-23-V-A-V', '1426': 'SC-23-V-A-VI', '1349': 'SC-23-V-B-I', '1350': 'SC-23-V-B-II', '1351': 'SC-23-V-B-III', '1427': 'SC-23-V-B-IV', '1428': 'SC-23-V-B-V', '1429': 'SC-23-V-B-VI', '1501': 'SC-23-V-C-I', '1502': 'SC-23-V-C-II', '1503': 'SC-23-V-C-III', '1576': 'SC-23-V-C-IV', '1577': 'SC-23-V-C-V', '1578': 'SC-23-V-C-VI', '1504': 'SC-23-V-D-I', '1505': 'SC-23-V-D-II', '1506': 'SC-23-V-D-III', '1579': 'SC-23-V-D-IV', '1580': 'SC-23-V-D-V', '1581': 'SC-23-V-D-VI', '1352': 'SC-23-X-A-I', '1353': 'SC-23-X-A-II', '1354': 'SC-23-X-A-III', '1430': 'SC-23-X-A-IV', '1431': 'SC-23-X-A-V', '1432': 'SC-23-X-A-VI', '1355': 'SC-23-X-B-I', '1356': 'SC-23-X-B-II', '1357': 'SC-23-X-B-III', '1433': 'SC-23-X-B-IV', '1434': 'SC-23-X-B-V', '1435': 'SC-23-X-B-VI', '1507': 'SC-23-X-C-I', '1508': 'SC-23-X-C-II', '1509': 'SC-23-X-C-III', '1582': 'SC-23-X-C-IV', '1583': 'SC-23-X-C-V', '1584': 'SC-23-X-C-VI', '1510': 'SC-23-X-D-I', '1511': 'SC-23-X-D-II', '1512': 'SC-23-X-D-III', '1585': 'SC-23-X-D-IV', '1586': 'SC-23-X-D-V', '1587': 'SC-23-X-D-VI', '1645': 'SC-23-Y-A-I', '1646': 'SC-23-Y-A-II', '1647': 'SC-23-Y-A-III', '1711': 'SC-23-Y-A-IV', '1712': 'SC-23-Y-A-V', '1713': 'SC-23-Y-A-VI', '1648': 'SC-23-Y-B-I', '1649': 'SC-23-Y-B-II', '1650': 'SC-23-Y-B-III', '1714': 'SC-23-Y-B-IV', '1715': 'SC-23-Y-B-V', '1716': 'SC-23-Y-B-VI', '1773': 'SC-23-Y-C-I', '1774': 'SC-23-Y-C-II', '1775': 'SC-23-Y-C-III', '1830': 'SC-23-Y-C-IV', '1831': 'SC-23-Y-C-V', '1832': 'SC-23-Y-C-VI', '1776': 'SC-23-Y-D-I', '1777': 'SC-23-Y-D-II', '1778': 'SC-23-Y-D-III', '1833': 'SC-23-Y-D-IV', '1834': 'SC-23-Y-D-V', '1835': 'SC-23-Y-D-VI', '1651': 'SC-23-Z-A-I', '1652': 'SC-23-Z-A-II', '1653': 'SC-23-Z-A-III', '1717': 'SC-23-Z-A-IV', '1718': 'SC-23-Z-A-V', '1719': 'SC-23-Z-A-VI', '1654': 'SC-23-Z-B-I', '1655': 'SC-23-Z-B-II', '1656': 'SC-23-Z-B-III', '1720': 'SC-23-Z-B-IV', '1721': 'SC-23-Z-B-V', '1722': 'SC-23-Z-B-VI', '1779': 'SC-23-Z-C-I', '1780': 'SC-23-Z-C-II', '1781': 'SC-23-Z-C-III', '1836': 'SC-23-Z-C-IV', '1837': 'SC-23-Z-C-V', '1838': 'SC-23-Z-C-VI', '1782': 'SC-23-Z-D-I', '1783': 'SC-23-Z-D-II', '1784': 'SC-23-Z-D-III', '1839': 'SC-23-Z-D-IV', '1840': 'SC-23-Z-D-V', '1841': 'SC-23-Z-D-VI', '64': 'NA-19-X-C-VI', '65': 'NA-19-X-D-IV', '90': 'NA-19-Y-B-II', '91': 'NA-19-Y-B-III', '125': 'NA-19-Y-B-V', '126': 'NA-19-Y-B-VI', '163A': 'NA-19-Y-D-I', '164': 'NA-19-Y-D-II', '165': 'NA-19-Y-D-III', '205': 'NA-19-Y-D-IV', '206': 'NA-19-Y-D-V', '207': 'NA-19-Y-D-VI', '92': 'NA-19-Z-A-I', '93': 'NA-19-Z-A-II', '94': 'NA-19-Z-A-III', '127': 'NA-19-Z-A-IV', '128': 'NA-19-Z-A-V', '129': 'NA-19-Z-A-VI', '95': 'NA-19-Z-B-I', '130': 'NA-19-Z-B-IV', '131': 'NA-19-Z-B-V', '166': 'NA-19-Z-C-I', '167': 'NA-19-Z-C-II', '168': 'NA-19-Z-C-III', '208': 'NA-19-Z-C-IV', '209': 'NA-19-Z-C-V', '210': 'NA-19-Z-C-VI', '169': 'NA-19-Z-D-I', '170': 'NA-19-Z-D-II', '171': 'NA-19-Z-D-III', '211': 'NA-19-Z-D-IV', '212': 'NA-19-Z-D-V', '213': 'NA-19-Z-D-VI', '1310': 'SC-20-V-A-I', '1311': 'SC-20-V-A-II', '1312': 'SC-20-V-A-III', '1388': 'SC-20-V-A-IV', '1389': 'SC-20-V-A-V', '1390': 'SC-20-V-A-VI', '1313': 'SC-20-V-B-I', '1314': 'SC-20-V-B-II', '1315': 'SC-20-V-B-III', '1391': 'SC-20-V-B-IV', '1392': 'SC-20-V-B-V', '1393': 'SC-20-V-B-VI', '1465': 'SC-20-V-C-I', '1466': 'SC-20-V-C-II', '1467': 'SC-20-V-C-III', '1540': 'SC-20-V-C-IV', '1541': 'SC-20-V-C-V', '1542': 'SC-20-V-C-VI', '1468': 'SC-20-V-D-I', '1469': 'SC-20-V-D-II', '1470': 'SC-20-V-D-III', '1543': 'SC-20-V-D-IV', '1544': 'SC-20-V-D-V', '1545': 'SC-20-V-D-VI', '1316': 'SC-20-X-A-I', '1317': 'SC-20-X-A-II', '1318': 'SC-20-X-A-III', '1394': 'SC-20-X-A-IV', '1395': 'SC-20-X-A-V', '1396': 'SC-20-X-A-VI', '1319': 'SC-20-X-B-I', '1320': 'SC-20-X-B-II', '1321': 'SC-20-X-B-III', '1397': 'SC-20-X-B-IV', '1398': 'SC-20-X-B-V', '1399': 'SC-20-X-B-VI', '1471': 'SC-20-X-C-I', '1472': 'SC-20-X-C-II', '1473': 'SC-20-X-C-III', '1546': 'SC-20-X-C-IV', '1547': 'SC-20-X-C-V', '1548': 'SC-20-X-C-VI', '1474': 'SC-20-X-D-I', '1475': 'SC-20-X-D-II', '1476': 'SC-20-X-D-III', '1549': 'SC-20-X-D-IV', '1550': 'SC-20-X-D-V', '1551': 'SC-20-X-D-VI', '1610': 'SC-20-Y-A-II', '1611': 'SC-20-Y-A-III', '1676': 'SC-20-Y-A-V', '1677': 'SC-20-Y-A-VI', '1612': 'SC-20-Y-B-I', '1613': 'SC-20-Y-B-II', '1614': 'SC-20-Y-B-III', '1678': 'SC-20-Y-B-IV', '1679': 'SC-20-Y-B-V', '1680': 'SC-20-Y-B-VI', '1738': 'SC-20-Y-C-II', '1739': 'SC-20-Y-C-III', '1795': 'SC-20-Y-C-V', '1796': 'SC-20-Y-C-VI', '1740': 'SC-20-Y-D-I', '1741': 'SC-20-Y-D-II', '1742': 'SC-20-Y-D-III', '1797': 'SC-20-Y-D-IV', '1798': 'SC-20-Y-D-V', '1799': 'SC-20-Y-D-VI', '1615': 'SC-20-Z-A-I', '1616': 'SC-20-Z-A-II', '1617': 'SC-20-Z-A-III', '1681': 'SC-20-Z-A-IV', '1682': 'SC-20-Z-A-V', '1683': 'SC-20-Z-A-VI', '1618': 'SC-20-Z-B-I', '1619': 'SC-20-Z-B-II', '1620': 'SC-20-Z-B-III', '1684': 'SC-20-Z-B-IV', '1685': 'SC-20-Z-B-V', '1686': 'SC-20-Z-B-VI', '1743': 'SC-20-Z-C-I', '1744': 'SC-20-Z-C-II', '1745': 'SC-20-Z-C-III', '1800': 'SC-20-Z-C-IV', '1801': 'SC-20-Z-C-V', '1802': 'SC-20-Z-C-VI', '1746': 'SC-20-Z-D-I', '1747': 'SC-20-Z-D-II', '1748': 'SC-20-Z-D-III', '1803': 'SC-20-Z-D-IV', '1804': 'SC-20-Z-D-V', '1805': 'SC-20-Z-D-VI', '248': 'SA-19-V-B-I', '249': 'SA-19-V-B-II', '250': 'SA-19-V-B-III', '293': 'SA-19-V-B-V', '294': 'SA-19-V-B-VI', '341': 'SA-19-V-D-II', '342': 'SA-19-V-D-III', '392': 'SA-19-V-D-V', '393': 'SA-19-V-D-VI', '251': 'SA-19-X-A-I', '252': 'SA-19-X-A-II', '253': 'SA-19-X-A-III', '295': 'SA-19-X-A-IV', '296': 'SA-19-X-A-V', '297': 'SA-19-X-A-VI', '254': 'SA-19-X-B-I', '255': 'SA-19-X-B-II', '256': 'SA-19-X-B-III', '298': 'SA-19-X-B-IV', '299': 'SA-19-X-B-V', '300': 'SA-19-X-B-VI', '343': 'SA-19-X-C-I', '344': 'SA-19-X-C-II', '345': 'SA-19-X-C-III', '394': 'SA-19-X-C-IV', '395': 'SA-19-X-C-V', '396': 'SA-19-X-C-VI', '346': 'SA-19-X-D-I', '347': 'SA-19-X-D-II', '348': 'SA-19-X-D-III', '397': 'SA-19-X-D-IV', '398': 'SA-19-X-D-V', '399': 'SA-19-X-D-VI', '444': 'SA-19-Y-B-II', '445': 'SA-19-Y-B-III', '498': 'SA-19-Y-B-V', '499': 'SA-19-Y-B-VI', '559': 'SA-19-Y-D-II', '560': 'SA-19-Y-D-III', '622': 'SA-19-Y-D-V', '623': 'SA-19-Y-D-VI', '446': 'SA-19-Z-A-I', '447': 'SA-19-Z-A-II', '448': 'SA-19-Z-A-III', '500': 'SA-19-Z-A-IV', '501': 'SA-19-Z-A-V', '502': 'SA-19-Z-A-VI', '449': 'SA-19-Z-B-I', '450': 'SA-19-Z-B-II', '451': 'SA-19-Z-B-III', '503': 'SA-19-Z-B-IV', '504': 'SA-19-Z-B-V', '505': 'SA-19-Z-B-VI', '561': 'SA-19-Z-C-I', '562': 'SA-19-Z-C-II', '563': 'SA-19-Z-C-III', '624': 'SA-19-Z-C-IV', '625': 'SA-19-Z-C-V', '626': 'SA-19-Z-C-VI', '564': 'SA-19-Z-D-I', '565': 'SA-19-Z-D-II', '566': 'SA-19-Z-D-III', '627': 'SA-19-Z-D-IV', '628': 'SA-19-Z-D-V', '629': 'SA-19-Z-D-VI', '1852': 'SD-20-V-A-III', '1853': 'SD-20-V-B-I', '1854': 'SD-20-V-B-II', '1855': 'SD-20-V-B-III', '1907': 'SD-20-V-B-IV', '1908': 'SD-20-V-B-V', '1909': 'SD-20-V-B-VI', '1856': 'SD-20-X-A-I', '1857': 'SD-20-X-A-II', '1858': 'SD-20-X-A-III', '1910': 'SD-20-X-A-IV', '1911': 'SD-20-X-A-V', '1912': 'SD-20-X-A-VI', '1859': 'SD-20-X-B-I', '1860': 'SD-20-X-B-II', '1861': 'SD-20-X-B-III', '1913': 'SD-20-X-B-IV', '1914': 'SD-20-X-B-V', '1915': 'SD-20-X-B-VI', '1961': 'SD-20-X-C-I', '1962': 'SD-20-X-C-II', '1963': 'SD-20-X-C-III', '2010': 'SD-20-X-C-VI', '1964': 'SD-20-X-D-I', '1965': 'SD-20-X-D-II', '1966': 'SD-20-X-D-III', '2011': 'SD-20-X-D-IV', '2012': 'SD-20-X-D-V', '2013': 'SD-20-X-D-VI', '2057': 'SD-20-Z-B-III', '2101': 'SD-20-Z-B-VI', '2145': 'SD-20-Z-D-II', '2146': 'SD-20-Z-D-III', '2190': 'SD-20-Z-D-VI', '19': 'NA-20-V-A-III', '20': 'NA-20-V-B-I', '21': 'NA-20-V-B-II', '22': 'NA-20-V-B-III', '33': 'NA-20-V-B-IV', '34': 'NA-20-V-B-V', '35': 'NA-20-V-B-VI', '47': 'NA-20-V-D-I', '48': 'NA-20-V-D-II', '49': 'NA-20-V-D-III', '66': 'NA-20-V-D-IV', '67': 'NA-20-V-D-V', '68': 'NA-20-V-D-VI', '23': 'NA-20-X-A-I', '24': 'NA-20-X-A-II', '25': 'NA-20-X-A-III', '36': 'NA-20-X-A-IV', '37': 'NA-20-X-A-V', '38': 'NA-20-X-A-VI', '26': 'NA-20-X-B-I', '27': 'NA-20-X-B-II', '28': 'NA-20-X-B-III', '39': 'NA-20-X-B-IV', '40': 'NA-20-X-B-V', '41': 'NA-20-X-B-VI', '50': 'NA-20-X-C-I', '51': 'NA-20-X-C-II', '52': 'NA-20-X-C-III', '69': 'NA-20-X-C-IV', '70': 'NA-20-X-C-V', '71': 'NA-20-X-C-VI', '53': 'NA-20-X-D-I', '54': 'NA-20-X-D-II', '55': 'NA-20-X-D-III', '72': 'NA-20-X-D-IV', '73': 'NA-20-X-D-V', '74': 'NA-20-X-D-VI', '132': 'NA-20-Y-A-V', '133': 'NA-20-Y-A-VI', '96': 'NA-20-Y-B-I', '97': 'NA-20-Y-B-II', '98': 'NA-20-Y-B-III', '134': 'NA-20-Y-B-IV', '135': 'NA-20-Y-B-V', '136': 'NA-20-Y-B-VI', '172': 'NA-20-Y-C-I', '173': 'NA-20-Y-C-II', '174': 'NA-20-Y-C-III', '214': 'NA-20-Y-C-IV', '215': 'NA-20-Y-C-V', '216': 'NA-20-Y-C-VI', '175': 'NA-20-Y-D-I', '176': 'NA-20-Y-D-II', '177': 'NA-20-Y-D-III', '217': 'NA-20-Y-D-IV', '218': 'NA-20-Y-D-V', '219': 'NA-20-Y-D-VI', '99': 'NA-20-Z-A-I', '100': 'NA-20-Z-A-II', '101': 'NA-20-Z-A-III', '137': 'NA-20-Z-A-IV', '138': 'NA-20-Z-A-V', '139': 'NA-20-Z-A-VI', '102': 'NA-20-Z-B-I', '103': 'NA-20-Z-B-II', '104': 'NA-20-Z-B-III', '140': 'NA-20-Z-B-IV', '141': 'NA-20-Z-B-V', '142': 'NA-20-Z-B-VI', '178': 'NA-20-Z-C-I', '179': 'NA-20-Z-C-II', '180': 'NA-20-Z-C-III', '220': 'NA-20-Z-C-IV', '221': 'NA-20-Z-C-V', '222': 'NA-20-Z-C-VI', '181': 'NA-20-Z-D-I', '182': 'NA-20-Z-D-II', '183': 'NA-20-Z-D-III', '223': 'NA-20-Z-D-IV', '224': 'NA-20-Z-D-V', '225': 'NA-20-Z-D-VI'}
