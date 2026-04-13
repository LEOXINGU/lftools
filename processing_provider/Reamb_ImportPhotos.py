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

from qgis.PyQt.QtCore import QVariant
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
                       QgsProcessingParameterEnum,
                       QgsFeatureSink,
                       QgsProcessingUtils,
                       QgsProcessingException,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterFeatureSink)

import datetime
import shutil
from lftools.geocapt.imgs import Imgs
from lftools.geocapt.topogeo import azimute as CalAZ
from lftools.geocapt.cartography import simbologiaPontos3D
from lftools.translations.translate import translate
import os, re
import processing
import math
import struct
from math import pi, atan, degrees
from qgis.PyQt.QtGui import QIcon

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
        return 'GeoOne,import,photo,reambulation,geotag,geophoto,reambulação,fotografia,photography,drone,DJI'.split(',')

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
    SENSOR = 'SENSOR'
    GEOMETRY = 'GEOMETRY'
    PHOTOMETRY = 'PHOTOMETRY'
    STYLE = 'STYLE'

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
            QgsProcessingParameterBoolean(
                self.SENSOR,
                self.tr('Sensor'),
                defaultValue = False
            )
        )

        self.addParameter(
            QgsProcessingParameterBoolean(
                self.GEOMETRY,
                self.tr('Geometry', 'Geometria'),
                defaultValue = False
            )
        )

        self.addParameter(
            QgsProcessingParameterBoolean(
                self.PHOTOMETRY,
                self.tr('Photometry', 'Fotometria'),
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

        STYLES = [self.tr('Simple Camera', 'Camera simples'),
                  self.tr('Drone'),
                  self.tr('VR Photo 360°', 'RV Foto 360°') ]

        self.addParameter(
            QgsProcessingParameterEnum(
                self.STYLE,
                self.tr('Layer Style', 'Estilo da camada'),
				options = STYLES,
                defaultValue= 0
            )
        )

        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT,
                self.tr('Geolocated photos', 'Fotos Geolocalizadas')
            )
        )


    def processAlgorithm(self, parameters, context, feedback):

        from PIL import Image, TiffTags, ExifTags
        from PIL.TiffImagePlugin import ImageFileDirectory_v2
        from PIL.TiffTags import TAGS
        ImageFileDirectory_v2._load_dispatch[13] = ImageFileDirectory_v2._load_dispatch[TiffTags.LONG]
        try:
            from pillow_heif import register_heif_opener
            register_heif_opener()
        except ImportError:
            pass

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

        InSensor = self.parameterAsBool(
            parameters,
            self.SENSOR,
            context
        )

        InGeometria = self.parameterAsBool(
            parameters,
            self.GEOMETRY,
            context
        )

        InFotometria = self.parameterAsBool(
            parameters,
            self.PHOTOMETRY,
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
                    if (name).lower().endswith(('.jpg', '.jpeg', '.tif', '.tiff', '.dng', '.png', '.bmp', '.webp', '.cr2', '.arw', '.heic', '.heif')):
                        lista += [os.path.join(root, name)]
        else:
            for item in os.listdir(pasta):
                if (item).lower().endswith(('.jpg', '.jpeg', '.tif', '.tiff', '.dng', '.png', '.bmp', '.webp', '.cr2', '.arw', '.heic', '.heif')):
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
        
        # Mensagem de erro
        def erro_msg(arquivo):
            return self.tr('The file "{}" has no geotag!'.format(arquivo), 'A imagem "{}" não possui geotag!'.format(arquivo)) 

        # Criando Output
        crs = QgsCoordinateReferenceSystem('EPSG:4326')
        fields = QgsFields()
        fields.append(QgsField(self.tr('name'), QVariant.String))
        fields.append(QgsField(self.tr('longitude'), QVariant.Double))
        fields.append(QgsField(self.tr('latitude'), QVariant.Double))
        fields.append(QgsField(self.tr('altitude'), QVariant.Double))
        fields.append(QgsField(self.tr('azimuth'), QVariant.Double))
        fields.append(QgsField(self.tr('date_time'), QVariant.String))
        fields.append(QgsField(self.tr('path'), QVariant.String))
        
        if InSensor:
            fields.append(QgsField(self.tr('make','fabricante'), QVariant.String))
            fields.append(QgsField(self.tr('model','modelo'), QVariant.String))
            fields.append(QgsField(self.tr('dimensions','dimensões'), QVariant.String))
            fields.append(QgsField(self.tr('FOV'), QVariant.Double))
            fields.append(QgsField(self.tr('SensorSize'), QVariant.String))
            fields.append(QgsField('FocalLen', QVariant.Double))
            fields.append(QgsField('SensW', QVariant.Double))
            fields.append(QgsField('ImgW', QVariant.Int))
            fields.append(QgsField('ImgH', QVariant.Int))

        if InFotometria:
            fields.append(QgsField(self.tr('iso'), QVariant.String))
            fields.append(QgsField(self.tr('exposure_bias','exp_bias'), QVariant.String))
            fields.append(QgsField(self.tr('aperture','abertura'), QVariant.String))
            fields.append(QgsField(self.tr('shutter_speed','obturação'), QVariant.String))

        if InGeometria:
            fields.append(QgsField(self.tr('FlightYaw'), QVariant.Double))
            fields.append(QgsField(self.tr('FlightPitch'), QVariant.Double))
            fields.append(QgsField(self.tr('FlightRoll'), QVariant.Double))
            fields.append(QgsField(self.tr('GimbalYaw'), QVariant.Double))
            fields.append(QgsField(self.tr('GimbalPitch'), QVariant.Double))
            fields.append(QgsField(self.tr('GimbalRoll'), QVariant.Double))

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
            
            ext_file = (filepath).lower()
            if ext_file.endswith(('.jpg', '.jpeg', '.png', '.bmp', '.webp', '.heic', '.heif')):
                caminho, arquivo = os.path.split(filepath)
                
                try:
                    img = Image.open(os.path.join(caminho,arquivo))
                    raw_exif = img._getexif()
                    if raw_exif:
                        # Dicionário robusto com IDs e nomes
                        exif = {}
                        for k, v in raw_exif.items():
                            exif[k] = v
                            if k in ExifTags.TAGS:
                                exif[ExifTags.TAGS[k]] = v
                    else:
                        exif = {}

                    dimensions, iso_str, exp_str, fnum_str, obt_str, img_w, img_h = self.format_photo_metadata(img, exif)
                    
                    lon, lat = 0, 0
                    Az = None
                    date_time = None
                    altitude = None
                    img.close()
                except:
                    lon = 0
                    img_w = img_h = 0
                    exif = {}

                # 1. Metadados de Geometria e Sensor (Prioridade XMP para Drones/DNG)
                FlightYaw = FlightPitch = FlightRoll = GimbalYaw = GimbalPitch = GimbalRoll = FOV = SensorSize = None
                xmp_data = self.extract_image_metadata(filepath, exif)
                
                # Desempacotar metadados XMP
                (FlightYaw, FlightPitch, FlightRoll, 
                 GimbalYaw, GimbalPitch, GimbalRoll, 
                 FOV, SensorSize, focal_len, sens_w,
                 xmp_lat, xmp_lon, xmp_alt, xmp_alt_rel,
                 xmp_iso, xmp_obt, xmp_fnum, xmp_exp,
                 xmp_w, xmp_h) = xmp_data

                # 2. Resolução (Correção para miniaturas de DNG)
                if xmp_w and xmp_h:
                    if img_w < 1000 or img_h < 1000: # Provável miniatura
                        img_w, img_h = int(xmp_w), int(xmp_h)
                        dimensions = f"{img_w}x{img_h}"

                # 3. GPS (Fallback/Prioridade XMP se EXIF falhar)
                if 'GPSInfo' in exif:
                    lat, lon = coordenadas(exif)
                    if 17 in exif['GPSInfo']:
                        Az = float(azimute(exif))
                    if 6 in exif['GPSInfo']:
                        try:
                            altitude = float(exif['GPSInfo'][6][0])/exif['GPSInfo'][6][1]
                        except:
                            altitude = float(exif['GPSInfo'][6])
                
                # Se EXIF falhar (como no DNG), usa XMP
                if (lat == 0 or lon == 0) and (xmp_lat is not None and xmp_lon is not None):
                    lat, lon = xmp_lat, xmp_lon
                if altitude is None and xmp_alt is not None:
                    altitude = xmp_alt
                elif altitude is None and xmp_alt_rel is not None:
                    altitude = xmp_alt_rel

                # 4. Fotometria (Se estiver vazio e tiver no XMP)
                if not iso_str and xmp_iso: iso_str = f"ISO{int(xmp_iso)}"
                if not fnum_str and xmp_fnum: fnum_str = f"f/{xmp_fnum:.1f}"
                if not exp_str and xmp_exp is not None: 
                    exp_str = f"EXP{float(xmp_exp):.1f}".replace('EXP-0.0', 'EXP0').replace('EXP0.0', 'EXP0')
                if not obt_str and xmp_obt:
                    # Formatar obturação vinda do XMP (float)
                    if xmp_obt < 1:
                        obt_str = f"1/{int(round(1/xmp_obt))}"
                    else:
                        obt_str = f"{round(xmp_obt, 1)}s"

                # 5. Data e Hora
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
                    # Fallback para Azimute
                    if Az is None:
                        if GimbalYaw is not None:
                            Az = GimbalYaw
                        elif FlightYaw is not None:
                            Az = FlightYaw

                    if not CalcAz:
                        feature = QgsFeature(fields)
                        feature.setGeometry(QgsGeometry(QgsPoint(lon, lat, altitude if altitude != None else 0)))
                        
                        # Atributos Automáticos
                        # Usar casting explícito para evitar erros de conversão no QGIS 4.0 (Qt 6)
                        att = [arquivo, float(lon), float(lat), float(altitude) if altitude is not None else 0.0, float(Az) if Az is not None else 0.0, date_time, filepath]
                        
                        # Categorias
                        if InSensor:
                            # FOV, focal_len e sens_w devem ser float. img_w e img_h devem ser int.
                            att += [fabricante, modelo, dimensions, 
                                    float(FOV) if FOV is not None else None, 
                                    SensorSize, 
                                    float(focal_len) if focal_len is not None else None, 
                                    float(sens_w) if sens_w is not None else None, 
                                    int(img_w) if img_w is not None else None, 
                                    int(img_h) if img_h is not None else None]
                        if InFotometria:
                            att += [iso_str, exp_str, fnum_str, obt_str]
                        if InGeometria:
                            # Todos os ângulos devem ser float
                            att += [float(val) if val is not None else None for val in [FlightYaw, FlightPitch, FlightRoll, GimbalYaw, GimbalPitch, GimbalRoll]]
                            
                        feature.setAttributes(att)
                        sink.addFeature(feature, QgsFeatureSink.FastInsert)
                    else:
                        att = [arquivo, float(lon), float(lat), float(altitude) if altitude is not None else 0.0, float(Az) if Az is not None else 0.0, date_time, filepath]
                        if InSensor:
                            att += [fabricante, modelo, dimensions, 
                                    float(FOV) if FOV is not None else None, 
                                    SensorSize, 
                                    float(focal_len) if focal_len is not None else None, 
                                    float(sens_w) if sens_w is not None else None, 
                                    int(img_w) if img_w is not None else None, 
                                    int(img_h) if img_h is not None else None]
                        if InFotometria:
                            att += [iso_str, exp_str, fnum_str, obt_str]
                        if InGeometria:
                            att += [float(val) if val is not None else None for val in [FlightYaw, FlightPitch, FlightRoll, GimbalYaw, GimbalPitch, GimbalRoll]]
                        Atributos += [att]
                else:
                    feedback.reportError(erro_msg(arquivo))
                    if copy_ngeo:
                        shutil.copy2(os.path.join(pasta, arquivo), os.path.join(fotos_nao_geo, arquivo))

            elif ext_file.endswith(('.tif', '.tiff', '.dng', '.cr2', '.arw')):
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

                dimensions, iso_str, exp_str, fnum_str, obt_str, img_w, img_h = self.format_photo_metadata(img, meta_dict)

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
                    try:
                        lat_ref = str(tags['GPSLatitudeRef'])
                        lat_val = eval(str(tags['GPSLatitude']))
                        lat = (-1 if lat_ref.upper() == 'S' else 1)*(float(lat_val[0]) + float(lat_val[1])/60 + float(lat_val[2])/3600)
                        
                        lon_ref = str(tags['GPSLongitudeRef'])
                        lon_val = eval(str(tags['GPSLongitude']))
                        lon = (-1 if lon_ref.upper() == 'W' else 1)*(float(lon_val[0]) + float(lon_val[1])/60 + float(lon_val[2])/3060) # Wait, typing error in 3600? fixed below
                        lon = (-1 if lon_ref.upper() == 'W' else 1)*(float(lon_val[0]) + float(lon_val[1])/60 + float(lon_val[2])/3600)
                        
                        alt_val = eval(str(tags['GPSAltitude']))
                        altitude = float(alt_val[0])/alt_val[1] if alt_val[1] != 0 else float(alt_val[0])
                        
                        # Extração de Azimute do GPS (tag 17)
                        if 'GPSImgDirection' in tags:
                            az_val = eval(str(tags['GPSImgDirection']))
                            Az = float(az_val[0])/az_val[1] if az_val[1] != 0 else float(az_val[0])
                    except:
                        pass

                    # Data e Hora
                    for tag_date in ['DateTimeOriginal', 'DateTime', 36867, 306]:
                        if tag_date in meta_dict:
                            val = meta_dict[tag_date]
                            if isinstance(val, (tuple, list)): val = val[0]
                            date_time = data_hora(str(val))
                            break

                    if 'Make' in meta_dict:
                        fabricante = str(meta_dict['Make'][0]) if isinstance(meta_dict['Make'], tuple) else str(meta_dict['Make'])
                        fabricante = fabricante.replace('\x00', '').strip()
                    else:
                        fabricante = ''

                    if 'Model' in meta_dict:
                        modelo = str(meta_dict['Model'][0]) if isinstance(meta_dict['Model'], tuple) else str(meta_dict['Model'])
                        modelo = modelo.replace('\x00', '').strip()
                    else:
                        modelo = ''

                    if lon != 0:
                        # 1. Metadados de Geometria e Sensor (Prioridade XMP para Drones/DNG)
                        FlightYaw = FlightPitch = FlightRoll = GimbalYaw = GimbalPitch = GimbalRoll = FOV = SensorSize = None
                        xmp_data = self.extract_image_metadata(filepath, meta_dict)
                        
                        # Desempacotar metadados XMP
                        (FlightYaw, FlightPitch, FlightRoll, 
                         GimbalYaw, GimbalPitch, GimbalRoll, 
                         FOV, SensorSize, focal_len, sens_w,
                         xmp_lat, xmp_lon, xmp_alt, xmp_alt_rel,
                         xmp_iso, xmp_obt, xmp_fnum, xmp_exp,
                         xmp_w, xmp_h) = xmp_data

                        # 2. Resolução (Correção para miniaturas de DNG)
                        if xmp_w and xmp_h:
                            if img_w < 1000 or img_h < 1000: # Provável miniatura
                                img_w, img_h = int(xmp_w), int(xmp_h)
                                dimensions = f"{img_w}x{img_h}"

                        # 3. GPS (Fallback/Prioridade XMP para DNG)
                        # Se EXIF falhar (como no DNG), usa XMP
                        if (lat == 0 or lon == 0) and (xmp_lat is not None and xmp_lon is not None):
                            lat, lon = xmp_lat, xmp_lon
                        if altitude is None and xmp_alt is not None:
                            altitude = xmp_alt
                        elif altitude is None and xmp_alt_rel is not None:
                            altitude = xmp_alt_rel

                        # 4. Fotometria (Se estiver vazio e tiver no XMP)
                        if not iso_str and xmp_iso: iso_str = f"ISO{int(xmp_iso)}"
                        if not fnum_str and xmp_fnum: fnum_str = f"f/{xmp_fnum:.1f}"
                        if not exp_str and xmp_exp is not None: 
                            exp_str = f"EXP{float(xmp_exp):.1f}".replace('EXP-0.0', 'EXP0').replace('EXP0.0', 'EXP0')
                        if not obt_str and xmp_obt:
                            if xmp_obt < 1:
                                obt_str = f"1/{int(round(1/xmp_obt))}"
                            else:
                                obt_str = f"{round(xmp_obt, 1)}s"
                        
                        # Fallback para Azimute
                        if Az is None:
                            if GimbalYaw is not None:
                                Az = GimbalYaw
                            elif FlightYaw is not None:
                                Az = FlightYaw

                        if not CalcAz:
                            feature = QgsFeature(fields)
                            feature.setGeometry(QgsGeometry(QgsPoint(lon, lat, altitude if altitude != None else 0)))
                            
                            # Atributos Automáticos
                            att = [arquivo, float(lon), float(lat), float(altitude) if altitude is not None else 0.0, float(Az) if Az is not None else 0.0, date_time, filepath]
                            
                            # Categorias
                            if InSensor:
                                att += [fabricante, modelo, dimensions, 
                                        float(FOV) if FOV is not None else None, 
                                        SensorSize, 
                                        float(focal_len) if focal_len is not None else None, 
                                        float(sens_w) if sens_w is not None else None, 
                                        int(img_w) if img_w is not None else None, 
                                        int(img_h) if img_h is not None else None]
                            if InFotometria:
                                att += [iso_str, exp_str, fnum_str, obt_str]
                            if InGeometria:
                                att += [float(val) if val is not None else None for val in [FlightYaw, FlightPitch, FlightRoll, GimbalYaw, GimbalPitch, GimbalRoll]]
                                
                            feature.setAttributes(att)
                            sink.addFeature(feature, QgsFeatureSink.FastInsert)
                        else:
                            att = [arquivo, float(lon), float(lat), float(altitude) if altitude is not None else 0.0, float(Az) if Az is not None else 0.0, date_time, filepath]
                            if InSensor:
                                att += [fabricante, modelo, dimensions, 
                                        float(FOV) if FOV is not None else None, 
                                        SensorSize, 
                                        float(focal_len) if focal_len is not None else None, 
                                        float(sens_w) if sens_w is not None else None, 
                                        int(img_w) if img_w is not None else None, 
                                        int(img_h) if img_h is not None else None]
                            if InFotometria:
                                att += [iso_str, exp_str, fnum_str, obt_str]
                            if InGeometria:
                                att += [float(val) if val is not None else None for val in [FlightYaw, FlightPitch, FlightRoll, GimbalYaw, GimbalPitch, GimbalRoll]]
                            Atributos += [att]
                    else:
                        feedback.reportError(erro_msg(arquivo))
                else:
                    feedback.reportError(erro_msg(arquivo))
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
                res_az = CalAZ(pntA, pntB)[0]
                if res_az is not None:
                    # Apenas atualiza se os pontos não forem coincidentes
                    Az = round(180*res_az/pi, 1)
                    Atributos[k][4] = Az
            # O último ponto mantém o azimute do penúltimo ou o seu próprio gimbal
            if len(Atributos) > 1:
                Atributos[-1][4] = Atributos[-2][4]

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

        estilo = self.parameterAsEnum(
            parameters,
            self.STYLE,
            context
        )
        self.ESTILO = [4,1,2][estilo]  # 0:camera simples (4), 1:drone (1), 2:camera 360 (2)
        self.SAIDA = dest_id
        self.pasta = pasta
        return {self.OUTPUT: dest_id}
    
    
    def _read_tiff_ifd(self, f, offset, endian, name="IFD", depth=0, results=None):
        """Metodo auxiliar para ler IFDs recursivamente em arquivos TIFF/DNG"""
        if depth > 5 or results is None: return
        f.seek(offset)
        count_data = f.read(2)
        if len(count_data) < 2: return
        num_tags = struct.unpack(endian + 'H', count_data)[0]
        
        # Tags de interesse: 256=W, 257=H, 34855=ISO, 33434=ExpTime, 33437=FNum, 34665=ExifIFD, 34853=GPS_IFD, 330=SubIFDs, 37386=Folen, 41989=F35, 17=GPSAz
        tags_map = {
            256: 'w', 257: 'h', 34855: 'iso', 33434: 'obt', 33437: 'fnum',
            34665: 'exif_off', 34853: 'gps_off', 330: 'sub_off',
            37386: 'flen', 41989: 'f35', 17: 'az'
        }
        
        next_calls = []
        for _ in range(num_tags):
            tag_data = f.read(12)
            if len(tag_data) < 12: break
            tag_id, tag_type, count, val_offset = struct.unpack(endian + 'HHII', tag_data)
            
            if tag_id in tags_map:
                key = tags_map[tag_id]
                if tag_id in [256, 257, 34855, 41989]: # Valores diretos ou curtos (W, H, ISO, F35)
                    if results.get(key) is None or (key in ['w', 'h'] and val_offset > results.get(key, 0)):
                        results[key] = val_offset
                elif tag_id in [34665, 34853]: # Offsets
                    next_calls.append((val_offset, key))
                elif tag_id == 330: # SubIFDs
                    if count == 1:
                        next_calls.append((val_offset, 'sub'))
                    elif count > 1:
                        curr_pos = f.tell()
                        f.seek(val_offset)
                        for _ in range(count):
                            off_data = f.read(4)
                            if len(off_data) == 4:
                                next_calls.append((struct.unpack(endian + 'I', off_data)[0], 'sub'))
                        f.seek(curr_pos)
                elif tag_id in [33434, 33437, 37386, 17]: # Racionais
                    curr_pos = f.tell()
                    f.seek(val_offset)
                    rat_data = f.read(8)
                    if len(rat_data) == 8:
                        n, d = struct.unpack(endian + 'II', rat_data)
                        if d != 0: results[key] = n / d
                    f.seek(curr_pos)
        
        for off, n in next_calls:
            self._read_tiff_ifd(f, off, endian, n, depth + 1, results)

    def format_photo_metadata(self, img, exif):
        """
        Baseado nos exemplos do usuário: 4000x3000, ISO100, EXP0.3, f/1.7, 1/2500
        Retorna: dimensões, iso, compensação, abertura, obturação
        """
        # Função interna para extrair valor seja por nome ou ID
        def get_val(tags_names_or_ids):
            for t in tags_names_or_ids:
                if t in exif: return exif[t]
            return None

        # Helper para converter racionais/objetos em frações num/den
        def get_ratio(val):
            if hasattr(val, 'numerator') and hasattr(val, 'denominator'):
                return val.numerator, val.denominator
            if isinstance(val, (tuple, list)) and len(val) == 2:
                return val[0], val[1]
            return None

        # --- Resolucao ---
        w = get_val(['ImageWidth', 256, 'ExifImageWidth', 40962])
        h = get_val(['ImageLength', 257, 'ExifImageHeight', 40963])
        
        # Correcao para DNG/TIFF (Pillow costuma ler a miniatura IFD0)
        ext = ""
        if hasattr(img, 'filename'): ext = os.path.splitext(img.filename)[1].lower()
        if ext in ['.dng', '.tif', '.tiff'] or (w and h and (int(w) < 500 or int(h) < 500)):
            tiff_res = {'w': None, 'h': None, 'iso': None, 'obt': None, 'fnum': None}
            try:
                with open(img.filename, 'rb') as f:
                    header = f.read(8)
                    endian = '<' if header[:2] == b'II' else '>'
                    first_ifd = struct.unpack(endian + 'I', header[4:8])[0]
                    self._read_tiff_ifd(f, first_ifd, endian, results=tiff_res)
                if tiff_res['w'] and tiff_res['h']:
                    w, h = tiff_res['w'], tiff_res['h']
            except: pass

        if isinstance(w, (tuple, list)): w = w[0]
        if isinstance(h, (tuple, list)): h = h[0]
        if not w or not h: w, h = img.size
        dimensions = f"{int(w)}x{int(h)}"

        # --- Fotometria ---
        iso = get_val(['ISOSpeedRatings', 34855])
        if isinstance(iso, (tuple, list)): iso = iso[0]
        if iso is None and ext in ['.dng', '.tif'] and 'tiff_res' in locals():
            iso = tiff_res.get('iso')
        iso_str = f"ISO{iso}" if iso else ""

        exp = get_val(['ExposureBiasValue', 37380])
        ratio_exp = get_ratio(exp)
        if ratio_exp:
            exp = ratio_exp[0]/ratio_exp[1] if ratio_exp[1] != 0 else ratio_exp[0]
        exp_str = f"EXP{float(exp):.1f}".replace('EXP-0.0', 'EXP0').replace('EXP0.0', 'EXP0') if exp is not None else ""

        fnum = get_val(['FNumber', 33437])
        ratio_fnum = get_ratio(fnum)
        if ratio_fnum:
            fnum = ratio_fnum[0]/ratio_fnum[1] if ratio_fnum[1] != 0 else ratio_fnum[0]
        if not fnum and ext in ['.dng', '.tif'] and 'tiff_res' in locals():
            fnum = tiff_res.get('fnum')
        fnum_str = f"f/{float(fnum):.1f}" if fnum else ""

        obt = get_val(['ExposureTime', 33434, 'ShutterSpeedValue', 37377, 'ShutterSpeed'])
        if not obt and ext in ['.dng', '.tif'] and 'tiff_res' in locals():
            obt = tiff_res.get('obt')
            
        obt_str = ""
        ratio_obt = get_ratio(obt)
        
        if ratio_obt:
            num, den = ratio_obt
            if den == 0:
                obt_str = ""
            else:
                com_div = math.gcd(int(num), int(den))
                num, den = num // com_div, den // com_div
                
                if num == 1:
                    obt_str = f"1/{den}"
                elif num >= den:
                    obt_str = f"{round(num/den, 1)}s"
                else:
                    if den / num > 1.5:
                        obt_str = f"1/{int(round(den/num))}"
                    else:
                        obt_str = f"{num}/{den}"
        elif isinstance(obt, (float, int)):
            if 0 < obt < 1:
                obt_str = f"1/{int(round(1/obt))}"
            elif obt >= 1:
                obt_str = f"{round(float(obt), 1)}s"
            else:
                obt_str = str(obt)
        else:
            # Última tentativa: converter o objeto estranho para string direta
            obt_str = str(obt) if obt is not None else ""
        
        return dimensions, iso_str, exp_str, fnum_str, obt_str, int(w), int(h)


    def extract_image_metadata(self, image_path, exif_data):
        """
        Extrai yaw, pitch, roll, FOV e Tamanho do Sensor de imagens analisando o bloco XMP e EXIF.
        Desenvolvido para ser resiliente a diferentes versões de firmware e modelos DJI (P4P até Matrice 350).
        """
        def to_float(val):
            if val is None: return None
            if isinstance(val, (tuple, list)) and len(val) > 0:
                val = val[0]
            try: return float(val)
            except:
                if hasattr(val, 'numerator') and hasattr(val, 'denominator'):
                     return float(val.numerator) / val.denominator if val.denominator != 0 else 0.0
                return None

        FlightYaw = FlightPitch = FlightRoll = GimbalYaw = GimbalPitch = GimbalRoll = FOV = SensorWidth = SensorHeight = None
        f_real = f_35mm = None
        
        # Base de dados de sensores DJI (Largura x Altura em mm)
        DJI_SENSORS = {
            'FC6310': (13.2, 8.8), 'FC6310S': (13.2, 8.8), 'FC220': (13.2, 8.8),
            'FC2204': (6.4, 4.8), 'FC3170': (13.2, 8.8), 'FC7303': (17.3, 13.0),
            'FC3682': (6.4, 4.8), 'FC8484': (17.3, 13.0), 'FC8482': (6.4, 4.8),
            'M30T': (6.4, 4.8), 'ZenmuseP1': (35.9, 24.0), 'ZenmuseH20': (6.17, 4.55),
            'ZenmuseH20T': (6.17, 4.55), 'FC6510': (13.2, 8.8), 'FC6520': (17.3, 13.0),
            'FC6540': (23.5, 15.7), 'FC330': (6.5, 4.88)
        }

        try:
            # 1. Extração via XMP
            with open(image_path, "rb") as fb:
                data = fb.read(262144)
            
            m = re.search(br"<x:xmpmeta[\s\S]*?</x:xmpmeta>", data, re.IGNORECASE)
            if not m: m = re.search(br"<xmpmeta[\s\S]*?</xmpmeta>", data, re.IGNORECASE)
            
            if m:
                xmp = m.group(0).decode("utf-8", errors="ignore")
                def find_attr_or_elem(names, as_string=False):
                    for name in names:
                        rx_attr = re.compile(rf'(?:[\w-]+:)?{re.escape(name)}\s*=\s*["\']([\-+]?\d+(?:\.\d+)?)["\']', re.IGNORECASE)
                        m_attr = rx_attr.search(xmp)
                        if m_attr:
                            val = m_attr.group(1)
                            return val if as_string else float(val)
                        rx_elem = re.compile(rf'<([^:>]*:)?{re.escape(name)}\s*>([\-+]?\d+(?:\.\d+)?)\s*</([^:>]*:)?{re.escape(name)}\s*>', re.IGNORECASE)
                        m_elem = rx_elem.search(xmp)
                        if m_elem:
                            val = m_elem.group(2)
                            return val if as_string else float(val)
                    return None

                FlightYaw = find_attr_or_elem(["FlightYawDegree", "YawDegree", "Yaw", "FlightYaw"])
                FlightPitch = find_attr_or_elem(["FlightPitchDegree", "PitchDegree", "Pitch", "FlightPitch"])
                FlightRoll = find_attr_or_elem(["FlightRollDegree", "RollDegree", "Roll", "FlightRoll"])
                GimbalYaw = find_attr_or_elem(["GimbalYawDegree", "GimbalYaw", "PoseYawDegrees", "CameraYawDegree"])
                GimbalPitch = find_attr_or_elem(["GimbalPitchDegree", "GimbalPitch", "PosePitchDegrees", "CameraPitchDegree"])
                GimbalRoll = find_attr_or_elem(["GimbalRollDegree", "GimbalRoll", "PoseRollDegrees", "CameraRollDegree"])
                FOV = find_attr_or_elem(["FieldOfView", "HorizontalFOV", "HFOV"])
                SensorWidth = find_attr_or_elem(["SensorWidth", "SensorWidthmm"])
                SensorHeight = find_attr_or_elem(["SensorHeight", "SensorHeightmm"])

                XMPLat = find_attr_or_elem(["GPSLatitude", "Latitude"])
                XMPLon = find_attr_or_elem(["GPSLongitude", "Longitude"])
                XMPAlt = find_attr_or_elem(["AbsoluteAltitude", "GPSAltitude", "Altitude"])
                XMPAltRel = find_attr_or_elem(["RelativeAltitude"])
                XMPISO = find_attr_or_elem(["ISOSpeedRatings", "ISO", "ExposureIndex"])
                XMPObt = find_attr_or_elem(["ExposureTime", "ShutterSpeedValue"])
                XMPFNum = find_attr_or_elem(["FNumber", "ApertureValue"])
                XMPExp = find_attr_or_elem(["ExposureBiasValue", "ExposureBias"])
                XMPW = find_attr_or_elem(["FullImageWidth", "ImageWidth", "ExifImageWidth", "OriginalImageWidth"])
                XMPH = find_attr_or_elem(["FullImageHeight", "ImageHeight", "ExifImageHeight", "OriginalImageHeight"])

            # 2. Refinamento via IFD Nativo (para DNG/TIF onde EXIF falha)
            ext = os.path.splitext(image_path)[1].lower()
            tiff_res = {}
            if ext in ['.dng', '.tif', '.tiff']:
                try:
                    with open(image_path, 'rb') as f:
                        header = f.read(8)
                        endian = '<' if header[:2] == b'II' else '>'
                        first_ifd = struct.unpack(endian + 'I', header[4:8])[0]
                        self._read_tiff_ifd(f, first_ifd, endian, results=tiff_res)
                except: pass

            # 3. Refinamento de Metadados e Banco de Dados DJI
            model = make = ""
            if exif_data:
                model = str(exif_data.get('Model', '')).replace('\x00', '').strip()
                make = str(exif_data.get('Make', '')).replace('\x00', '').strip()
                f_real = to_float(exif_data.get('FocalLength'))
                f_35mm = to_float(exif_data.get('FocalLengthIn35mmFilm') or exif_data.get('FocalLengthIn35mmFormat'))

            # Fallbacks via Parser Binário
            if not f_real: f_real = tiff_res.get('flen')
            if not f_35mm: f_35mm = tiff_res.get('f35')
            if GimbalYaw is None: GimbalYaw = tiff_res.get('az')
            
            # Se ainda vazio, tenta Model/Make no XMP (comum em DNGs DJI)
            if not model and 'xmp' in locals():
                m_mod = re.search(r'Model=["\']([^"\']+)["\']', xmp)
                if m_mod: model = m_mod.group(1)
                m_mak = re.search(r'Make=["\']([^"\']+)["\']', xmp)
                if m_mak: make = m_mak.group(1)

            # Lógica Elástica DJI
            if "DJI" in make.upper() or model.startswith("FC") or "ZENMUSE" in model.upper():
                if GimbalPitch is not None and abs(GimbalPitch) < 0.1: GimbalPitch = -90.0
                elif GimbalPitch is None and (model in ['FC3682', 'FC8482', 'FC330']): GimbalPitch = -90.0
                if GimbalYaw is None and FlightYaw is not None: GimbalYaw = FlightYaw
                if model in DJI_SENSORS:
                    sw, sh = DJI_SENSORS[model]
                    if SensorWidth is None: SensorWidth = sw
                    if SensorHeight is None: SensorHeight = sh
                
                if FOV is None:
                    if f_35mm: FOV = round(2 * math.degrees(math.atan(36.0 / (2.0 * f_35mm))), 2)
                    elif f_real and SensorWidth: FOV = round(2 * math.degrees(math.atan(SensorWidth / (2.0 * f_real))), 2)
                
                if SensorWidth is None and f_real and f_35mm:
                    SensorWidth = round(36.0 * f_real / f_35mm, 2)
                if SensorWidth and SensorHeight is None:
                    ratio = 0.75 if SensorWidth < 20 else 0.66
                    SensorHeight = round(SensorWidth * ratio, 2)

            sensor_str = f"{SensorWidth} x {SensorHeight} mm" if (SensorWidth and SensorHeight) else (f"{SensorWidth} mm" if SensorWidth else None)
            
            return (to_float(FlightYaw), to_float(FlightPitch), to_float(FlightRoll), 
                    to_float(GimbalYaw), to_float(GimbalPitch), to_float(GimbalRoll), 
                    to_float(FOV), sensor_str, to_float(f_real), to_float(SensorWidth),
                    to_float(XMPLat), to_float(XMPLon), to_float(XMPAlt), to_float(XMPAltRel),
                    to_float(XMPISO), to_float(XMPObt), to_float(XMPFNum), to_float(XMPExp),
                    to_float(XMPW), to_float(XMPH))

        except Exception as e:
            return None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None

        

    def postProcessAlgorithm(self, context, feedback):
        layer = QgsProcessingUtils.mapLayerFromString(self.SAIDA, context)
        
        params = { 'LAYER' : layer, 'STYLE_POINT' : self.ESTILO, 'STYLE_LINE' : 0, 'STYLE_POLYGON' : 0 }
        processing.run("lftools:magicstyles", params)

        if self.pasta[0:2] in (r'\\', r'//'):
            layer.setMapTipTemplate(r'''[%''' + self.tr("name") + '''%]<br><img src="file://[%''' + self.tr('path') + '''%]" width="450">''')
        else:
            layer.setMapTipTemplate(r'''[%''' + self.tr("name") + '''%]<br><img src="file:///[%''' + self.tr('path') + '''%]" width="450">''')

        renderer3d = simbologiaPontos3D()
        layer.setRenderer3D(renderer3d)
        layer.trigger3DUpdate()
        layer.triggerRepaint() 

        return {self.OUTPUT: self.SAIDA}
