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
__date__ = '2024-10-07'
__copyright__ = '(C) 2024, Leandro França'

import pyproj
from qgis.core import *
from qgis.gui import *
from lftools.translations.translate import translate

LOC = QgsApplication.locale()[:2]
def tr(*string):
    return translate(string, LOC)

def DefinirUTM(iface):
    # Obter a extensão atual da tela do mapa
    canvas = iface.mapCanvas()
    extent = canvas.extent()

    # Acessar o projeto atual
    project = QgsProject.instance()

    # Extrair os limites da extensão
    xmin = extent.xMinimum()
    xmax = extent.xMaximum()
    ymin = extent.yMinimum()
    ymax = extent.yMaximum()

    # Centro da tela
    x_medio = (xmin + xmax)/2
    y_medio = (ymin + ymax)/2
    geom = QgsGeometry.fromPointXY(QgsPointXY(x_medio, y_medio))

    # SRC e datum
    SRC = project.crs()

    # Reprojetar coordenada do ponto central para Geográfico, se projetado
    if not SRC.isGeographic():
        GeoSRC = SRC.toGeographicCrs()
        crsSrc = QgsCoordinateReferenceSystem(SRC)
        crsDest = QgsCoordinateReferenceSystem(GeoSRC)
        proj2geo = QgsCoordinateTransform(crsSrc, crsDest, project)
        geom.transform(proj2geo)

    lon = geom.asPoint().x()
    lat = geom.asPoint().y()

    # Fuso e hemisfério
    fuso = int(round((183+lon)/6.0))
    # Hemisferio
    hemisf = 'N' if lat>= 0 else 'S'

    # Nome do datum
    datum = SRC.description().split(' / ')[0]

    # Nome da projeção UTM
    UTM = datum + ' / UTM zone ' + str(fuso) + hemisf

    # crs_info_list = pyproj.database.query_crs_info(auth_name="EPSG", pj_types="PROJECTED_CRS")
    crs_info_list = pyproj.database.query_utm_crs_info(datum_name= datum)

    for crs_info in crs_info_list:
        nome = crs_info.name
        if UTM == nome:
            epsg_code = crs_info.code
            break

    # Criar o objeto SRC usando o código EPSG
    EPSG = "EPSG:{}".format(epsg_code)
    crs = QgsCoordinateReferenceSystem(EPSG)

    # Definir o SRC do projeto
    project.setCrs(crs)

    # Verificar se o SRC foi alterado corretamente
    mensagem = tr('New CRS defined to zone {} and hemisphere {}.', 'Novo SRC definido para o Fuso {} e Hemisfério {}').format(fuso, hemisf)
    iface.messageBar().pushMessage("Projeção", mensagem, level=Qgis.Info)
    # print(f"O novo SRC do projeto é: {project.crs().authid()}")


def copiar_estilo_camada_ativa(iface):
    # Obter a camada ativa
    camada_ativa = iface.activeLayer()

    # Verificar se há uma camada ativa
    if camada_ativa is not None:
        # Copiar o estilo da camada ativa
        iface.actionCopyLayerStyle().trigger()
        iface.messageBar().pushMessage("LFTools", tr('Active layer style successfully copied.', 'Estilo da camada ativa copiado com sucesso.'), level=Qgis.Info)
        return camada_ativa
    else:
        iface.messageBar().pushMessage("LFTools", tr("No active layer found!", "Nenhuma camada ativa encontrada!"), level=Qgis.Warning)
        return


def colar_estilo_em_camada_destino(iface, camada_origem):
    # Obter a camada ativa
    camada_destino = iface.activeLayer()

    if camada_origem is None:
        iface.messageBar().pushMessage("LFTools", tr("No style copied!", "Nenhum estilo copiado!"), level=Qgis.Warning)
        return

    if camada_destino is None:
        iface.messageBar().pushMessage("LFTools", tr("No active layer found!", "Nenhuma camada ativa encontrada!"), level=Qgis.Warning)
        return

    # Verificar se ambas as camadas são do mesmo tipo
    if camada_origem.type() != camada_destino.type():
        iface.messageBar().pushMessage("LFTools", tr("The layers are of different types (raster and vector)!", "As camadas são de tipos diferentes (raster e vetor)!"), level=Qgis.Warning)
        return

    # Verificar se ambas as camadas são vetores e se possuem a mesma geometria
    if camada_destino.type() == QgsMapLayer.VectorLayer:
        if camada_origem.geometryType() != camada_destino.geometryType():
            iface.messageBar().pushMessage("LFTools", tr("The vector layers have different geometry types!", "As camadas vetoriais têm tipos de geometria diferentes!"), level=Qgis.Warning)
            return

    # Colar o estilo se as camadas forem compatíveis
    iface.actionPasteLayerStyle().trigger()
    camada_destino.triggerRepaint()
    camada_destino.emitStyleChanged()
    iface.messageBar().pushMessage("LFTools", tr('Style successfully pasted to the destination layer.', 'Estilo colado com sucesso na camada de destino.'), level=Qgis.Info)
