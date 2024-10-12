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


# save point to file, point is in project's crs
def save_point(self, point, address):
    self.logMessage('Saving point ' + str(point[0])  + ' ' + str(point[1]))
    # create and add the point layer if not exists or not set
    if not self._get_registry().mapLayer(self.layerid) :
        # create layer with same CRS as map canvas
        crs = self._get_canvas_crs()
        self.layer = QgsVectorLayer("Point?crs=" + crs.authid(), "GeoCoding Plugin Results", "memory")
        self.provider = self.layer.dataProvider()

        # add fields
        self.provider.addAttributes([QgsField("address", QVariant.String)])

        # BUG: need to explicitly call it, should be automatic!
        self.layer.updateFields()

        # Labels on
        try:
            label_settings = QgsPalLayerSettings()
            label_settings.fieldName = "address"
            self.layer.setLabeling(QgsVectorLayerSimpleLabeling(label_settings))
            self.layer.setLabelsEnabled(True)
        except:
            self.layer.setCustomProperty("labeling", "pal")
            self.layer.setCustomProperty("labeling/enabled", "true")
            #self.layer.setCustomProperty("labeling/fontFamily", "Arial")
            #self.layer.setCustomProperty("labeling/fontSize", "10")
            self.layer.setCustomProperty("labeling/fieldName", "address")
            self.layer.setCustomProperty("labeling/placement", "2")

        # add layer if not already
        self._get_registry().addMapLayer(self.layer)

        # store layer id
        self.layerid = self.layer.id()


    # add a feature
    try:
        fields=self.layer.pendingFields()
    except:
        fields=self.layer.fields()

    fet = QgsFeature(fields)
    try:
        fet.setGeometry(QgsGeometry.fromPoint(point))
    except:
        fet.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(point)))

    try: # QGIS < 1.9
        fet.setAttributeMap({0 : address})
    except: # QGIS >= 1.9
        fet['address'] = address

    self.layer.startEditing()
    self.layer.addFeatures([ fet ])
    self.layer.commitChanges()


# check config and project settings before geocoding,
# return an error string
def check_settings (self):
    p = QgsProject.instance()
    error = ''
    if QT_VERSION==4:
        if not self.iface.mapCanvas().hasCrsTransformEnabled() and self.iface.mapCanvas().mapRenderer().destinationCrs().authid() != 'EPSG:4326':
            error = QCoreApplication.translate('GeoCoding', "On-the-fly reprojection must be enabled if the destination CRS is not EPSG:4326. Please enable on-the-fly reprojection.")

    return error
