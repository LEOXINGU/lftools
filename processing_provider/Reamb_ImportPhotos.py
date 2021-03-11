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
                       QgsCoordinateReferenceSystem,
                       QgsProcessing,
                       QgsProcessingParameterFile,
                       QgsProcessingParameterField,
                       QgsProcessingParameterBoolean,
                       QgsProcessingParameterEnum,
                       QgsProcessingParameterNumber,
                       QgsFeatureSink,
                       QgsProcessingException,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterFeatureSink)
import PIL.Image, PIL.ExifTags
import datetime
import shutil
from lftools.geocapt.imgs import Imgs
import os
from qgis.PyQt.QtGui import QIcon

class ImportPhotos(QgsProcessingAlgorithm):

    LOC = QgsApplication.locale()

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
        return self.tr('Photos with Geotag', 'Fotos com Geotag')

    def group(self):
        return self.tr('Reambulation', 'Reambulação')

    def groupId(self):
        return 'reambulation'

    def tags(self):
        return self.tr('import','photo','reambulation','geotag','geophoto','reambulação','fotografia','photography').split(',')

    def icon(self):
        return QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images/reamb_camera.png'))

    def shortHelpString(self):
        txt_en = 'Imports photos with geotag to a Point Layer.'
        txt_pt = 'Importa fotos com geotag para uma camada de pontos.'
        social_BW = Imgs().social_BW
        footer = '''<div align="center">
                      <img src="'''+ os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images/tutorial/reamb_geotag.jpg') +'''">
                      </div>
                      <div align="right">
                      <p align="right">
                      <b>'''+self.tr('Author: Leandro Franca', 'Autor: Leandro França')+'''</b>
                      </p>'''+ social_BW + '''</div>
                    </div>'''
        return self.tr(txt_en, txt_pt) + footer

    FOLDER = 'FOLDER'
    NONGEO = 'NONGEO'
    OUTPUT = 'OUTPUT'

    def initAlgorithm(self, config=None):

        self.addParameter(
            QgsProcessingParameterFile(
                self.FOLDER,
                self.tr('Folder with JPEG photos', 'Pasta com fotos JPEG'),
                behavior=QgsProcessingParameterFile.Folder,
                defaultValue=None
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

        fotos_nao_geo = self.parameterAsFile(
            parameters,
            self.NONGEO,
            context
        )

        lista = os.listdir(pasta)
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
                grausLat,grausLon = exif['GPSInfo'][2][0][0], exif['GPSInfo'][4][0][0]
                minLat, minLon = exif['GPSInfo'][2][1][0], exif['GPSInfo'][4][1][0]
                segLat = exif['GPSInfo'][2][2][0]/float(exif['GPSInfo'][2][2][1])
                segLon = exif['GPSInfo'][4][2][0]/float(exif['GPSInfo'][4][2][1])
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
        for index, arquivo in enumerate(lista):
            if (arquivo).lower().endswith(('.jpg', '.jpeg')):
                img = PIL.Image.open(os.path.join(pasta,arquivo))
                if img._getexif():
                    exif = {
                        PIL.ExifTags.TAGS[k]: v
                        for k, v in img._getexif().items()
                        if k in PIL.ExifTags.TAGS
                    }
                else:
                    exif = {}
                lon, lat = 0, 0
                Az = None
                date_time = None
                if 'GPSInfo' in exif:
                    lat, lon = coordenadas(exif)
                    if 17 in exif['GPSInfo']:
                        Az = azimute(exif)
                if 'DateTimeOriginal' in exif:
                    date_time = data_hora(exif['DateTimeOriginal'])
                elif 'DateTime' in exif:
                    date_time = data_hora(exif['DateTime'])
                if lon != 0:
                    feature = QgsFeature(fields)
                    feature.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(lon, lat)))
                    feature.setAttributes([arquivo, Az, date_time, os.path.join(pasta, arquivo)])
                    sink.addFeature(feature, QgsFeatureSink.FastInsert)
                else:
                    print()
                    feedback.pushInfo(self.tr('The file "{}" has no geotag!'.format(arquivo), 'A imagem "{}" não possui geotag!'.format(arquivo)))
                    if copy_ngeo:
                        shutil.copy2(os.path.join(pasta, arquivo), os.path.join(fotos_nao_geo, arquivo))
            if feedback.isCanceled():
                break
            feedback.setProgress(int((index+1) * Percent))

        feedback.pushInfo(self.tr('Operation completed successfully!', 'Operação finalizada com sucesso!'))
        feedback.pushInfo(self.tr('Leandro Franca - Cartographic Engineer', 'Leandro França - Eng Cart'))

        return {self.OUTPUT: dest_id}
