# -*- coding: utf-8 -*-

"""
Reamb_ImportPhotos.py
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
__date__ = '2021-02-16'
__copyright__ = '(C) 2021, Leandro França'

from qgis.PyQt.QtCore import QCoreApplication
from PyQt5.QtCore import QVariant
from qgis.core import (QgsApplication,
                       QgsGeometry,
                       QgsPoint,
                       QgsWkbTypes,
                       QgsFeature,
                       QgsField,
                       QgsFields,
                       QgsAction,
                       QgsCoordinateReferenceSystem,
                       QgsProcessingParameterFile,
                       QgsProcessingParameterBoolean,
                       QgsFeatureSink,
                       QgsProcessingUtils,
                       QgsProcessingException,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterFeatureSink)

import datetime
import shutil
from lftools.geocapt.imgs import Imgs
from lftools.geocapt.topogeo import azimute as CalAZ
from lftools.translations.translate import translate
import os
from math import pi
from qgis.PyQt.QtGui import QIcon
from PIL import Image, TiffTags, ExifTags
from PIL.TiffImagePlugin import ImageFileDirectory_v2
from PIL.TiffTags import TAGS
ImageFileDirectory_v2._load_dispatch[13] = ImageFileDirectory_v2._load_dispatch[TiffTags.LONG]

class ImportPhotos(QgsProcessingAlgorithm):

    LOC = QgsApplication.locale()[:2]

    def tr(self, *string):
        return translate(string, self.LOC)

    def createInstance(self):
        return ImportPhotos()

    def name(self):
        return 'importphotos'

    def displayName(self):
        return self.tr('Photos with geotag', 'Fotos com geotag')

    def group(self):
        return self.tr('Reambulation', 'Reambulação')

    def groupId(self):
        return 'reambulation'

    def tags(self):
        return 'GeoOne,import,photo,reambulation,geotag,geophoto,reambulação,fotografia,photography'.split(',')

    def icon(self):
        return QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images/reamb_camera.png'))

    txt_en = 'Imports photos with geotag to a Point Layer.'
    txt_pt = 'Importa fotos com geotag para uma camada de pontos.'
    figure = 'images/tutorial/reamb_geotag.jpg'

    def shortHelpString(self):
        social_BW = Imgs().social_BW
        footer = '''<div align="center">
                      <img src="'''+ os.path.join(os.path.dirname(os.path.dirname(__file__)), self.figure) +'''">
                      </div>
                      <div align="right">
                      <p align="right">
                      <b>'''+self.tr('Author: Leandro Franca', 'Autor: Leandro França')+'''</b>
                      </p>'''+ social_BW + '''</div>
                    </div>'''
        return self.tr(self.txt_en, self.txt_pt) + footer

    FOLDER = 'FOLDER'
    NONGEO = 'NONGEO'
    OUTPUT = 'OUTPUT'
    SUBFOLDER = 'SUBFOLDER'
    AZIMUTH = 'AZIMUTH'

    def initAlgorithm(self, config=None):

        self.addParameter(
            QgsProcessingParameterFile(
                self.FOLDER,
                self.tr('Folder with geotagged photos', 'Pasta de fotos com Geotag'),
                behavior=QgsProcessingParameterFile.Folder,
                defaultValue=None
            )
        )

        self.addParameter(
            QgsProcessingParameterBoolean(
                self.SUBFOLDER,
                self.tr('Check subfolders', 'Verificar sub-pastas'),
                defaultValue = False
            )
        )

        self.addParameter(
            QgsProcessingParameterBoolean(
                self.AZIMUTH,
                self.tr('Estimate azimuth', 'Estimar azimute'),
                defaultValue = False
            )
        )

        self.addParameter(
            QgsProcessingParameterFile(
                self.NONGEO,
                self.tr('Folder to copy the photos without geotag', 'Pasta para copiar as fotos sem geotag'),
                behavior=QgsProcessingParameterFile.Folder,
                defaultValue=None,
                optional = True
            )
        )

        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT,
                self.tr('Geolocated photos', 'Fotos Geolocalizadas')
            )
        )


    def processAlgorithm(self, parameters, context, feedback):

        pasta = self.parameterAsFile(
            parameters,
            self.FOLDER,
            context
        )
        if not pasta:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.FOLDER))

        subpasta = self.parameterAsBool(
            parameters,
            self.SUBFOLDER,
            context
        )

        CalcAz = self.parameterAsBool(
            parameters,
            self.AZIMUTH,
            context
        )
        if CalcAz:
            Atributos = []

        fotos_nao_geo = self.parameterAsFile(
            parameters,
            self.NONGEO,
            context
        )

        feedback.pushInfo(self.tr('Checking files in the folder...', 'Checando arquivos na pasta...'))
        lista = []
        if subpasta:
            for root, dirs, files in os.walk(pasta, topdown=True):
                for name in files:
                    if (name).lower().endswith(('.jpg', '.jpeg', '.tif', '.tiff')):
                        lista += [os.path.join(root, name)]
        else:
            for item in os.listdir(pasta):
                if (item).lower().endswith(('.jpg', '.jpeg', '.tif', '.tiff')):
                    lista += [os.path.join(pasta, item)]

        tam = len(lista)
        copy_ngeo = False
        if os.path.isdir(fotos_nao_geo):
            copy_ngeo = True

        # Funcao para transformar os dados do EXIF em coordenadas em graus decimais
        def coordenadas(exif):
            try:
                ref_lat = exif['GPSInfo'][1][0]
                ref_lon = exif['GPSInfo'][3][0]
                sinal_lat, sinal_lon = 0, 0
                if ref_lat == 'S':
                    sinal_lat = -1
                elif ref_lat == 'N':
                    sinal_lat = 1
                if ref_lon == 'W':
                    sinal_lon = -1
                elif ref_lon == 'E':
                    sinal_lon = 1

                try:
                    grausLat,grausLon = exif['GPSInfo'][2][0][0], exif['GPSInfo'][4][0][0]
                    minLat, minLon = exif['GPSInfo'][2][1][0], exif['GPSInfo'][4][1][0]
                    segLat = exif['GPSInfo'][2][2][0]/float(exif['GPSInfo'][2][2][1])
                    segLon = exif['GPSInfo'][4][2][0]/float(exif['GPSInfo'][4][2][1])
                except:
                    grausLat,grausLon = exif['GPSInfo'][2][0], exif['GPSInfo'][4][0]
                    minLat, minLon = exif['GPSInfo'][2][1], exif['GPSInfo'][4][1]
                    segLat = exif['GPSInfo'][2][2]
                    segLon = exif['GPSInfo'][4][2]
                if sinal_lat!=0 and sinal_lon!=0:
                    lat = sinal_lat*(float(grausLat)+minLat/60.0+segLat/3600.0)
                    lon = sinal_lon*(float(grausLon)+minLon/60.0+segLon/3600.0)
                return lat, lon
            except:
                return 0,0

        # Funcao para pegar Azimute
        def azimute(exif):
            Az = exif['GPSInfo'][17]
            if isinstance(Az, tuple):
                Az = Az[0]/float(Az[1])
                return Az
            else:
                return Az

        # Funcao para gerar o padrao data-hora
        def data_hora(texto):
            data_hora = texto.replace(' ',':').replace('-',':')
            data_hora = data_hora.split(':')
            ano = int(data_hora[0])
            mes = int(data_hora[1])
            dia = int(data_hora[2])
            hora = int(data_hora[3])
            minuto = int(data_hora[4])
            segundo = int(data_hora[5])
            data_hora = unicode(datetime.datetime(ano, mes, dia, hora, minuto, segundo))
            return data_hora

        # Criando Output
        crs = QgsCoordinateReferenceSystem('EPSG:4326')
        fields = QgsFields()
        fields.append(QgsField(self.tr('name','nome'), QVariant.String))
        fields.append(QgsField(self.tr('longitude'), QVariant.Double))
        fields.append(QgsField(self.tr('latitude'), QVariant.Double))
        fields.append(QgsField(self.tr('altitude'), QVariant.Double))
        fields.append(QgsField(self.tr('azimuth','azimute'), QVariant.Int))
        fields.append(QgsField(self.tr('date_time','data_hora'), QVariant.String))
        fields.append(QgsField(self.tr('path','caminho'), QVariant.String))
        fields.append(QgsField(self.tr('make','fabricante'), QVariant.String))
        fields.append(QgsField(self.tr('model','modelo'), QVariant.String))

        (sink, dest_id) = self.parameterAsSink(
            parameters,
            self.OUTPUT,
            context,
            fields,
            QgsWkbTypes.PointZ,
            crs
        )
        if sink is None:
            raise QgsProcessingException(self.invalidSinkError(parameters, self.OUTPUT))

        Percent = 100.0/tam if tam!=0 else 0
        for index, filepath in enumerate(lista):
            if (filepath).lower().endswith(('.jpg', '.jpeg')):
                caminho, arquivo = os.path.split(filepath)
                try:
                    img = Image.open(os.path.join(caminho,arquivo))
                    if img._getexif():
                        exif = {
                            ExifTags.TAGS[k]: v
                            for k, v in img._getexif().items()
                            if k in ExifTags.TAGS
                        }
                    else:
                        exif = {}
                    lon, lat = 0, 0
                    Az = None
                    date_time = None
                    altitude = None
                    img.close()
                except:
                    lon = 0
                    exif = {}
                if 'GPSInfo' in exif:
                    lat, lon = coordenadas(exif)
                    if lat != 0:
                        if 17 in exif['GPSInfo']:
                            Az = float(azimute(exif))
                        if 6 in exif['GPSInfo']:
                            try:
                                altitude = float(exif['GPSInfo'][6][0])/exif['GPSInfo'][6][1]
                            except:
                                altitude = float(exif['GPSInfo'][6])
                if 'DateTimeOriginal' in exif:
                    date_time = data_hora(exif['DateTimeOriginal'])
                elif 'DateTime' in exif:
                    date_time = data_hora(exif['DateTime'])

                if 'Make' in exif:
                    fabricante = str(exif['Make'].replace('\x00', ''))
                else:
                    fabricante = ''

                if 'Model' in exif:
                    modelo = str(exif['Model'].replace('\x00', ''))
                else:
                    modelo = ''

                if lon != 0:
                    if not CalcAz:
                        feature = QgsFeature(fields)
                        feature.setGeometry(QgsGeometry(QgsPoint(lon, lat, altitude if altitude != None else 0)))
                        feature.setAttributes([arquivo, lon, lat, altitude, Az, date_time, os.path.join(caminho, arquivo), fabricante, modelo])
                        sink.addFeature(feature, QgsFeatureSink.FastInsert)
                    else:
                        Atributos += [[arquivo, lon, lat, altitude, Az, date_time, os.path.join(caminho, arquivo), fabricante, modelo]]
                else:
                    feedback.pushInfo(self.tr('The file "{}" has no geotag!'.format(arquivo), 'A imagem "{}" não possui geotag!'.format(arquivo)))
                    if copy_ngeo:
                        shutil.copy2(os.path.join(pasta, arquivo), os.path.join(fotos_nao_geo, arquivo))

            elif (filepath).lower().endswith(('.tif', '.tiff')):
                caminho, arquivo = os.path.split(filepath)
                img = Image.open(os.path.join(caminho,arquivo))
                try:
                    meta_dict = {TAGS[key] : img.tag[key] for key in img.tag_v2}
                except:
                    exif = img.getexif()
                    meta_dict = {}
                    for tag_id, value in exif.items():
                        tag_name = TAGS.get(tag_id)
                        meta_dict[tag_name] = value

                gps_offset = img.tag_v2.get(0x8825)
                tags = {}
                if gps_offset:
                	ifh = b"II\x2A\x00\x08\x00\x00\x00" if img.tag_v2._endian == "<" else "MM\x00\x2A\x00\x00\x00\x08"
                	info = ImageFileDirectory_v2(ifh)
                	img.fp.seek(gps_offset)
                	info.load(img.fp)
                	gps_keys = ['GPSVersionID','GPSLatitudeRef','GPSLatitude','GPSLongitudeRef','GPSLongitude','GPSAltitudeRef','GPSAltitude','GPSTimeStamp','GPSSatellites','GPSStatus','GPSMeasureMode','GPSDOP','GPSSpeedRef','GPSSpeed','GPSTrackRef','GPSTrack','GPSImgDirectionRef','GPSImgDirection','GPSMapDatum','GPSDestLatitudeRef','GPSDestLatitude','GPSDestLongitudeRef','GPSDestLongitude','GPSDestBearingRef','GPSDestBearing','GPSDestDistanceRef','GPSDestDistance','GPSProcessingMethod','GPSAreaInformation','GPSDateStamp','GPSDifferential']
                	for k, v in info.items():
                		tags[gps_keys[k]] = str(v)

                lon, lat = 0, 0
                Az = None
                date_time = None
                altitude = None

                if 'GPSLatitudeRef' in tags:
                    lat_ref = str(tags['GPSLatitudeRef'])
                    lat = eval(str(tags['GPSLatitude']))
                    lat = (-1 if lat_ref.upper() == 'S' else 1)*(lat[0] + lat[1]/60 + lat[2]/3600)
                    lon_ref = str(tags['GPSLongitudeRef'])
                    lon = eval(str(tags['GPSLongitude']))
                    lon = (-1 if lon_ref.upper() == 'W' else 1)*(lon[0] + lon[1]/60 + lon[2]/3600)
                    alt_ref = str(tags['GPSAltitudeRef'])
                    altitude = eval(str(tags['GPSAltitude']))
                    try:
                        date_time = data_hora(meta_dict['DateTime'][0])
                    except:
                        date_time = data_hora(meta_dict['DateTime'])
                    if 'Make' in meta_dict:
                        fabricante = str(meta_dict['Make'][0])
                    else:
                        fabricante = ''

                    if 'Model' in meta_dict:
                        modelo = str(meta_dict['Model'][0])
                    else:
                        modelo = ''

                    if lon != 0:
                        if not CalcAz:
                            feature = QgsFeature(fields)
                            feature.setGeometry(QgsGeometry(QgsPoint(lon, lat, altitude if altitude != None else 0)))
                            feature.setAttributes([arquivo, lon, lat, altitude, Az, date_time, os.path.join(caminho, arquivo), fabricante, modelo])
                            sink.addFeature(feature, QgsFeatureSink.FastInsert)
                        else:
                            Atributos += [[arquivo, lon, lat, altitude, Az, date_time, os.path.join(caminho, arquivo), fabricante, modelo]]
                else:
                    feedback.pushInfo(self.tr('The file "{}" has no geotag!'.format(arquivo), 'A imagem "{}" não possui geotag!'.format(arquivo)))
                    if copy_ngeo:
                        shutil.copy2(os.path.join(pasta, arquivo), os.path.join(fotos_nao_geo, arquivo))
                img.close()
            if feedback.isCanceled():
                break
            feedback.setProgress(int((index+1) * Percent))

        if CalcAz and len(Atributos) > 0:
            # Calcular azimutes
            for k in range(len(Atributos)-1):
                pntA = QgsPoint( float(Atributos[k][1]),  float(Atributos[k][2]))
                pntB = QgsPoint( float(Atributos[k+1][1]),float(Atributos[k+1][2]))
                Az = int(180*CalAZ(pntA, pntB)[0]/pi)
                Atributos[k][4] = Az
            Atributos[-1][4] = Az

            # Criar feições
            for att in Atributos:
                feature = QgsFeature(fields)
                lon, lat = att[1], att[2]
                h = att[3] if att[3] != None else 0
                feature.setGeometry(QgsGeometry(QgsPoint(float(lon), float(lat), float(h))))
                feature.setAttributes(att)
                sink.addFeature(feature, QgsFeatureSink.FastInsert)

        feedback.pushInfo(self.tr('Operation completed successfully!', 'Operação finalizada com sucesso!'))
        feedback.pushInfo(self.tr('Leandro Franca - Cartographic Engineer', 'Leandro França - Eng Cart'))
        self.SAIDA = dest_id
        self.pasta = pasta
        return {self.OUTPUT: dest_id}

    def postProcessAlgorithm(self, context, feedback):
        layer = QgsProcessingUtils.mapLayerFromString(self.SAIDA, context)
        if self.pasta[0:2] in (r'\\', r'//'):
            layer.setMapTipTemplate(r'''[%''' + self.tr("name","nome") + '''%]<br><img src="file://[%''' + self.tr('path','caminho') + '''%]" width="450">''')
        else:
            layer.setMapTipTemplate(r'''[%''' + self.tr("name","nome") + '''%]<br><img src="file:///[%''' + self.tr('path','caminho') + '''%]" width="450">''')

        acManager = layer.actions()
        acActor = QgsAction(QgsAction.ActionType.GenericPython , self.tr('Open photo', 'Abrir foto'),"""
import os
os.popen(r'[%"{}"%]')
""".format(self.tr("path","caminho")), False)
        acActor.setActionScopes({'Field', 'Layer', 'Canvas', 'Feature'})
        acManager.addAction(acActor)

        return {self.OUTPUT: self.SAIDA}
