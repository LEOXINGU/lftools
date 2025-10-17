# -*- coding: utf-8 -*-

"""
Reamb_KmlPhotos.py
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
__date__ = '2023-06-18'
__copyright__ = '(C) 2023, Leandro França'

from qgis.PyQt.QtCore import QVariant
from qgis.core import (QgsApplication,
                       QgsProcessing,
                       QgsProcessingParameterFile,
                       QgsProcessingParameterBoolean,
                       QgsProcessingParameterNumber,
                       QgsProcessingParameterField,
                       QgsCoordinateReferenceSystem,
                       QgsProcessingParameterFileDestination,
                       QgsProcessingUtils,
                       QgsCoordinateTransform,
                       QgsProject,
                       QgsProcessingException,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterFeatureSink)

from lftools.geocapt.imgs import Imgs
from lftools.translations.translate import translate
import os
from qgis.PyQt.QtGui import QIcon
from lftools.geocapt.imgs import img2html_resized


class KmlPhotos(QgsProcessingAlgorithm):

    LOC = QgsApplication.locale()[:2]

    def tr(self, *string):
        return translate(string, self.LOC)

    def createInstance(self):
        return KmlPhotos()

    def name(self):
        return 'kmlphotos'

    def displayName(self):
        return self.tr('KML with photos', 'KML com fotos')

    def group(self):
        return self.tr('Reambulation', 'Reambulação')

    def groupId(self):
        return 'reambulation'

    def tags(self):
        return 'GeoOne,resized,photo,kmz,reambulation,redimensionar,geophoto,reambulação,fotografia,photography,diminuir,reduzir,compactar,foto,kml,google,earth'.split(',')

    def icon(self):
        return QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images/reamb_camera.png'))

    txt_en = '''Creates a KML file embedding in that single file all photographs in base64 textual format to be viewed in Google Earth.
    Images are resized to a new size corresponding to the image's largest side.'''
    txt_pt = '''Cria um arquivo KML incorporando nesse único arquivo todas as fotografias em formato textual base64 para ser visualizado no Google Earth.
    As imagens são redimensionadas para um novo tamanho correspondente ao maior lado da imagem.'''
    figure = 'images/tutorial/reamb_kml_photos.jpg'

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

    LAYER = 'LAYER'
    SIZE = 'SIZE'
    KML = 'KML'
    FILEPATH = 'FILEPATH'
    TITLE = 'TITLE'
    DESCRIPTION = 'DESCRIPTION' #optional
    ALTITUDE = 'ALTITUDE' #optional

    def initAlgorithm(self, config=None):

        # INPUT
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.LAYER,
                self.tr('Input photo layer', 'Camada de fotos'),
                [QgsProcessing.TypeVectorPoint]
            )
        )

        self.addParameter(
            QgsProcessingParameterField(
                self.FILEPATH,
                self.tr('Filepath to image', 'Caminho para imagem'),
                parentLayerParameterName = self.LAYER,
                type = QgsProcessingParameterField.String,
            )
        )

        self.addParameter(
            QgsProcessingParameterNumber(
                self.SIZE,
                self.tr("Size for the image's largest side", 'Tamanho para o lado maior da imagem'),
                type = QgsProcessingParameterNumber.Type.Integer,
                minValue = 50,
                defaultValue = 400
                )
            )

        self.addParameter(
            QgsProcessingParameterField(
                self.TITLE,
                self.tr('Title', 'Título'),
                parentLayerParameterName = self.LAYER
            )
        )

        self.addParameter(
            QgsProcessingParameterField(
                self.DESCRIPTION,
                self.tr('Description', 'Descrição'),
                parentLayerParameterName = self.LAYER,
                type = QgsProcessingParameterField.String,
                optional = True
            )
        )

        self.addParameter(
            QgsProcessingParameterField(
                self.ALTITUDE,
                self.tr('Altitude'),
                parentLayerParameterName = self.LAYER,
                type = QgsProcessingParameterField.Numeric,
                optional = True
            )
        )

        # OUTPUT
        self.addParameter(
            QgsProcessingParameterFileDestination(
                self.KML,
                self.tr('KML file with photos', 'KML com fotos'),
                fileFilter = 'KML (*.kml)'
            )
        )

    def processAlgorithm(self, parameters, context, feedback):

        layer = self.parameterAsSource(
            parameters,
            self.LAYER,
            context
        )
        if layer is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.LAYER))

        tamanho = self.parameterAsInt(
            parameters,
            self.SIZE,
            context
        )

        caminho_foto = self.parameterAsFields(
            parameters,
            self.FILEPATH,
            context
        )
        caminho_foto = layer.fields().indexFromName(caminho_foto[0])

        campo_titulo = self.parameterAsFields(
            parameters,
            self.TITLE,
            context
        )
        campo_titulo = layer.fields().indexFromName(campo_titulo[0])

        campo_descr = self.parameterAsFields(
            parameters,
            self.DESCRIPTION,
            context
        )
        if campo_descr:
            campo_descr = layer.fields().indexFromName(campo_descr[0])

        campo_h = self.parameterAsFields(
            parameters,
            self.ALTITUDE,
            context
        )
        if campo_h:
            campo_h = layer.fields().indexFromName(campo_h[0])

        filename = self.parameterAsFileOutput(
            parameters,
            self.KML,
            context
        )
        Tail, File = os.path.split(filename)

        texto = '''<?xml version="1.0" encoding="UTF-8"?>
        <kml xmlns="http://www.opengis.net/kml/2.2" xmlns:gx="http://www.google.com/kml/ext/2.2" xmlns:kml="http://www.opengis.net/kml/2.2" xmlns:atom="http://www.w3.org/2005/Atom">
        <Document>
        	<name>[FILENAME]</name>
        	<StyleMap id="msn_camera">
        		<Pair>
        			<key>normal</key>
        			<styleUrl>#sn_camera</styleUrl>
        		</Pair>
        		<Pair>
        			<key>highlight</key>
        			<styleUrl>#sh_camera</styleUrl>
        		</Pair>
        	</StyleMap>
        	<Style id="sh_camera">
        		<IconStyle>
        			<scale>1.4</scale>
        			<Icon>
        				<href>http://maps.google.com/mapfiles/kml/shapes/camera.png</href>
        			</Icon>
        			<hotSpot x="0.5" y="0" xunits="fraction" yunits="fraction"/>
        		</IconStyle>
        		<BalloonStyle>
        		</BalloonStyle>
        		<ListStyle>
        		</ListStyle>
        	</Style>
        	<Style id="sn_camera">
        		<IconStyle>
        			<scale>1.2</scale>
        			<Icon>
        				<href>http://maps.google.com/mapfiles/kml/shapes/camera.png</href>
        			</Icon>
        			<hotSpot x="0.5" y="0" xunits="fraction" yunits="fraction"/>
        		</IconStyle>
        		<BalloonStyle>
        		</BalloonStyle>
        		<ListStyle>
        		</ListStyle>
        	</Style>
        	[LUGARES]
        </Document>
        </kml>
        '''

        ponto_txt  = '''<Placemark>
        		<name>[TITULO]</name>
        		<description>[DESCR]<![CDATA[<img src="data:image/jpg;base64,[FOTO]">]]></description>
        		<LookAt>
        			<longitude>[LON]</longitude>
        			<latitude>[LAT]</latitude>
        			<altitude>[ALTITUDE]</altitude>
        			<heading>-2.595305769485352</heading>
        			<tilt>0</tilt>
        			<range>1383584.739067059</range>
        			<gx:altitudeMode>relativeToSeaFloor</gx:altitudeMode>
        		</LookAt>
        		<styleUrl>#msn_camera</styleUrl>
        		<Point>
        			<gx:drawOrder>1</gx:drawOrder>
        			<coordinates>[LON],[LAT],[ALTITUDE]</coordinates>
        		</Point>
        	</Placemark>
        	'''

        campos = [field.name() for field in layer.fields()]

        # Transformação de coordenadas para WGS84
        crsSrc = layer.sourceCrs()
        crsDest = QgsCoordinateReferenceSystem('EPSG:4326')
        if crsSrc != crsDest:
            transf_SRC = True
            coordTransf = QgsCoordinateTransform(crsSrc, crsDest, QgsProject.instance())
        else:
            transf_SRC = False

        lugares = ''
        for feat in layer.getFeatures():
            if transf_SRC:
                geom = feat.geometry()
                geom.transform(coordTransf)
                pnt = geom.asPoint()
            else:
                pnt = feat.geometry().asPoint()
            lon = pnt.x()
            lat = pnt.y()

            titulo = feat[campo_titulo]
            altitude = feat[campo_h] if campo_h in campos else 0
            descricao = feat[campo_descr] if campo_descr in campos else ''
            arquivo = feat[caminho_foto]

            # Verificar se o arquivo existe
            if os.path.exists(arquivo):
                foto = img2html_resized(arquivo, tamanho)
            else:
                foto = ''

            texto0 = ponto_txt
            dic_lugares = {'[TITULO]': str(titulo),
                           '[DESCR]': str(descricao),
                           '[LON]': str(lon),
                           '[LAT]': str(lat),
                           '[ALTITUDE]': str(altitude),
                           '[FOTO]': foto
                           }
            for item in dic_lugares:
                texto0 = texto0.replace(item, dic_lugares[item])
            lugares += texto0

        # Substituir valores
        texto = texto.replace('[FILENAME]', File).replace('[LUGARES]', lugares)

        arq = open(filename, 'w')
        arq.write(texto)
        arq.close()

        feedback.pushInfo(self.tr('Operation completed successfully!', 'Operação finalizada com sucesso!'))
        feedback.pushInfo(self.tr('Leandro Franca - Cartographic Engineer', 'Leandro França - Eng Cart'))

        return {}
