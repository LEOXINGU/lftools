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
                       QgsProcessingParameterVectorLayer,
                       QgsGeometry,
                       QgsPointXY,
                       QgsWkbTypes,
                       QgsFeature,
                       QgsField,
                       QgsFields,
                       QgsAction,
                       QgsCoordinateReferenceSystem,
                       QgsProcessing,
                       QgsProcessingParameterFile,
                       QgsProcessingParameterField,
                       QgsProcessingParameterBoolean,
                       QgsProcessingParameterEnum,
                       QgsProcessingParameterNumber,
                       QgsFeatureSink,
                       QgsProcessingUtils,
                       QgsProcessingException,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterFeatureSink)

import datetime
import shutil
from lftools.geocapt.imgs import Imgs
import os
from qgis.PyQt.QtGui import QIcon
from PIL import Image, TiffTags, ExifTags
from PIL.TiffImagePlugin import ImageFileDirectory_v2
from PIL.TiffTags import TAGS
ImageFileDirectory_v2._load_dispatch[13] = ImageFileDirectory_v2._load_dispatch[TiffTags.LONG]

class ImportPhotos(QgsProcessingAlgorithm):

    LOC = QgsApplication.locale()[:2]

    def translate(self, string):
        return QCoreApplication.translate('Processing', string)

    def tr(self, *string):
        # Traduzir para o portugês: arg[0] - english (translate), arg[1] - português
        if self.LOC == 'pt':
            if len(string) == 2:
                return string[1]
            else:
                return self.translate(string[0])
        else:
            return self.translate(string[0])

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
        return self.tr('import','photo','reambulation','geotag','geophoto','reambulação','fotografia','photography').split(',')

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
            data_hora = texto.replace(' ',':')
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
        crs = QgsCoordinateReferenceSystem()
        crs.createFromSrid(4326)
        fields = QgsFields()
        fields.append(QgsField(self.tr('name','nome'), QVariant.String))
        fields.append(QgsField(self.tr('longitude'), QVariant.Double))
        fields.append(QgsField(self.tr('latitude'), QVariant.Double))
        fields.append(QgsField(self.tr('altitude'), QVariant.Double))
        fields.append(QgsField(self.tr('azimuth','azimute'), QVariant.Int))
        fields.append(QgsField(self.tr('date_time','data_hora'), QVariant.String))
        fields.append(QgsField(self.tr('path','caminho'), QVariant.String))

        (sink, dest_id) = self.parameterAsSink(
            parameters,
            self.OUTPUT,
            context,
            fields,
            QgsWkbTypes.Point,
            crs
        )
        if sink is None:
            raise QgsProcessingException(self.invalidSinkError(parameters, self.OUTPUT))

        Percent = 100.0/tam if tam!=0 else 0
        for index, filepath in enumerate(lista):
            if (filepath).lower().endswith(('.jpg', '.jpeg')):
                caminho, arquivo = os.path.split(filepath)
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
                if 'GPSInfo' in exif:
                    lat, lon = coordenadas(exif)
                    if lat != 0:
                        if 17 in exif['GPSInfo']:
                            Az = azimute(exif)
                        if 6 in exif['GPSInfo']:
                            try:
                                altitude = float(exif['GPSInfo'][6][0])/exif['GPSInfo'][6][1]
                            except:
                                altitude = float(exif['GPSInfo'][6])
                if 'DateTimeOriginal' in exif:
                    date_time = data_hora(exif['DateTimeOriginal'])
                elif 'DateTime' in exif:
                    date_time = data_hora(exif['DateTime'])
                if lon != 0:
                    feature = QgsFeature(fields)
                    feature.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(lon, lat)))
                    feature.setAttributes([arquivo, lon, lat, altitude, Az, date_time, os.path.join(caminho, arquivo)])
                    sink.addFeature(feature, QgsFeatureSink.FastInsert)
                else:
                    feedback.pushInfo(self.tr('The file "{}" has no geotag!'.format(arquivo), 'A imagem "{}" não possui geotag!'.format(arquivo)))
                    if copy_ngeo:
                        shutil.copy2(os.path.join(pasta, arquivo), os.path.join(fotos_nao_geo, arquivo))

            elif (filepath).lower().endswith(('.tif', '.tiff')):
                caminho, arquivo = os.path.split(filepath)
                img = Image.open(os.path.join(caminho,arquivo))
                meta_dict = {TAGS[key] : img.tag[key] for key in img.tag_v2}
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
                    date_time = data_hora(meta_dict['DateTime'][0])

                    if lon != 0:
                        feature = QgsFeature(fields)
                        feature.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(lon, lat)))
                        feature.setAttributes([arquivo, lon, lat, altitude, Az, date_time, os.path.join(caminho, arquivo)])
                        sink.addFeature(feature, QgsFeatureSink.FastInsert)
                else:
                    feedback.pushInfo(self.tr('The file "{}" has no geotag!'.format(arquivo), 'A imagem "{}" não possui geotag!'.format(arquivo)))
                    if copy_ngeo:
                        shutil.copy2(os.path.join(pasta, arquivo), os.path.join(fotos_nao_geo, arquivo))
            if feedback.isCanceled():
                break
            feedback.setProgress(int((index+1) * Percent))

        feedback.pushInfo(self.tr('Operation completed successfully!', 'Operação finalizada com sucesso!'))
        feedback.pushInfo(self.tr('Leandro Franca - Cartographic Engineer', 'Leandro França - Eng Cart'))
        self.SAIDA = dest_id
        self.pasta = pasta
        return {self.OUTPUT: dest_id}

    def postProcessAlgorithm(self, context, feedback):
        layer = QgsProcessingUtils.mapLayerFromString(self.SAIDA, context)
        if self.pasta[0:2] in (r'\\', r'//'):
            layer.setMapTipTemplate(r'''<img src="file://[%''' + self.tr('path','caminho') + '''%]" width="450">''')
        else:
            layer.setMapTipTemplate(r'''<img src="file:///[%''' + self.tr('path','caminho') + '''%]" width="450">''')

        acManager = layer.actions()
        acActor = QgsAction(1 , 'Abrir foto',"""
import os
os.popen(r'[%"caminho"%]')
""", False)
        acActor.setActionScopes({'Field', 'Layer', 'Canvas', 'Feature'})
        acManager.addAction(acActor)

        return {self.OUTPUT: self.SAIDA}
