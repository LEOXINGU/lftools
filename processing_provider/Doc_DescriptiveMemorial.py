# -*- coding: utf-8 -*-

"""
***************************************************************************
    Doc_DescriptiveMemorial.py
    ---------------------
    Date                 : Sept 22
    Copyright            : (C) 2019 by Leandro França
    Email                : geoleandro.franca@gmail.com
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
__date__ = 'Sept 22'
__copyright__ = '(C) 2019, Leandro França'

from PyQt5.QtCore import QCoreApplication
from qgis.core import (QgsProcessing,
                       QgsProject,
                       QgsCoordinateReferenceSystem,
                       QgsCoordinateTransform,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterEnum,
                       QgsProcessingParameterFile,
                       QgsProcessingParameterString,
                       QgsProcessingParameterNumber,
                       QgsProcessingParameterBoolean,
                       QgsProcessingException,
                       QgsProcessingParameterFileDestination,
                       QgsApplication)
from processing.algs.qgis.QgisAlgorithm import QgisAlgorithm
from math import atan, pi, sqrt, floor
import math
from lftools.geocapt.imgs import *
from lftools.geocapt.cartography import FusoHemisf, geom2PointList
from lftools.geocapt.topogeo import str2HTML, dd2dms, azimute
import os
from qgis.PyQt.QtGui import QIcon

class DescriptiveMemorial(QgisAlgorithm):
    """
    This algorithm takes three vector layers (point, line, and polygon)
    that define a specific ownership and creates an HTML file with the
    descriptive characteristics of the area.
    """
    HTML = 'HTML'
    INPUT1 = 'INPUT1'
    INPUT2 = 'INPUT2'
    INPUT3 = 'INPUT3'
    COORD = 'COORD'
    LOGO = 'LOGO'
    SLOGAN = 'SLOGAN'
    DECIMAL = 'DECIMAL'
    PROJECTION = 'PROJECTION'
    TOPOLOGY = 'TOPOLOGY'
    ATTRIBUTES = 'ATTRIBUTES'
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
        return DescriptiveMemorial()

    def name(self):
        return 'descriptivememorial'

    def displayName(self):
        return self.tr('Deed description', 'Memorial descritivo')

    def group(self):
        return self.tr('Documents', 'Documentos')

    def groupId(self):
        return 'documents'

    def tags(self):
        return self.tr('area,perimeter,deed,description,descriptive,memorial,property,topography,survey,real,estate,georreferencing,plan,cadastral,cadastre,documnt').split(',')

    def icon(self):
        return QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images/document.png'))

    figure = 'images/tutorial/doc_descriptive_memorial.jpg'
    txt_en = 'Elaboration of Deed Description based on vector layers that define a property.'
    txt_pt = 'Elaboração de Memorial Descritivo a partir de camadas vetorias que definem uma propriedade.'

    def shortHelpString(self):
        social_BW = Imgs().social_BW
        footer = '''<div align="center">
                      <img src="'''+ os.path.join(os.path.dirname(os.path.dirname(__file__)), self.figure) +'''">
                      </div>
                      <div align="right">
                      <div>''' + self.tr('This tool works properly only with data in "topogeo" modeling.',
                                         'Esta ferramenta funciona adequadamente com os dados na modelagem "topogeo".') + '''
                      </div>
                      <p align="right">
                      <b><a href="'''+ self.tr('https://www.researchgate.net/publication/356911797_TopoGeo_a_data_model_for_elaboration_of_cadastral_survey_plans_and_land_register_documents',
                      'https://geoone.com.br/ebook_gratis/') + '''" target="_blank">'''+ self.tr('Click here for understanding this data model.',
                                    'Clique aqui para entender esse modelo de dados') +'</a><br><br>'+ self.tr('Author: Leandro Franca', 'Autor: Leandro França')+'''</b>
                      </p>'''+ social_BW + '''</div>
                    </div>'''
        return self.tr(self.txt_en, self.txt_pt) + footer

    def initAlgorithm(self, config=None):
        # 'INPUTS'
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                'INPUT1',
                self.tr('Boundary Survey Points', 'Pontos de Limite'),
                types=[QgsProcessing.TypeVectorPoint]
            )
        )
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                'INPUT2',
                self.tr('Neighborhood Dividing Lines', 'Elementos Confrontantes'),
                types=[QgsProcessing.TypeVectorLine]
            )
        )
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                'INPUT3',
                self.tr('Property Polygon', 'Área do Imóvel'),
                types=[QgsProcessing.TypeVectorPolygon]
            )
        )

        opcoes = [self.tr('(N,E)'),
                  self.tr('(E,N)'),
                  self.tr('(N,E,h)'),
                  self.tr('(E,N,h)'),
                  self.tr('(lat,lon)'),
                  self.tr('(lon,lat)'),
                  self.tr('(lat,lon,h)'),
                  self.tr('(lon,lat,h)'),
               ]

        self.addParameter(
            QgsProcessingParameterEnum(
                self.COORD,
                self.tr('Coordinates', 'Coordenadas'),
				options = opcoes,
                defaultValue= 2
            )
        )

        self.addParameter(
            QgsProcessingParameterFile(
                self.LOGO,
                self.tr('Logo (JPEG)', 'Logomarca (JPEG)'),
                behavior=QgsProcessingParameterFile.File,
                defaultValue=None,
                fileFilter = 'Image (*.jpeg *.jpg *.JPG)',
                optional = True
            )
        )

        self.addParameter(
            QgsProcessingParameterString(
                self.SLOGAN,
                self.tr('Slogan'),
                defaultValue = self.tr(str2HTML('CARTOGRAPHY & SURVEYING'), str2HTML('CARTOGRAFIA & AGRIMENSURA')),
                optional = True,
                multiLine = True
            )
        )

        self.addParameter(
            QgsProcessingParameterNumber(
                self.DECIMAL,
                self.tr('Decimal places', 'Casas decimais'),
                type =0,
                defaultValue = 2
                )
            )

        self.addParameter(
            QgsProcessingParameterBoolean(
                self.PROJECTION,
                self.tr('Verify map projection', 'Verificar projeção do mapa'),
                defaultValue = True
            )
        )

        self.addParameter(
            QgsProcessingParameterBoolean(
                self.ATTRIBUTES,
                self.tr('Verify attributes', 'Verificar atributos'),
                defaultValue = True
            )
        )

        self.addParameter(
            QgsProcessingParameterBoolean(
                self.TOPOLOGY,
                self.tr('Verify topology', 'Verificar topologia'),
                defaultValue = True
            )
        )

        # 'OUTPUTS'
        self.addParameter(
            QgsProcessingParameterFileDestination(
                'HTML',
                self.tr('Deed description', 'Memorial Descritivo'),
                self.tr('HTML files (*.html)')
            )
        )


    def processAlgorithm(self, parameters, context, feedback):

        vertices = self.parameterAsSource(parameters,
                                                     'INPUT1',
                                                     context)
        limites = self.parameterAsSource(parameters,
                                                     'INPUT2',
                                                     context)
        area = self.parameterAsSource(parameters,
                                                     'INPUT3',
                                                     context)
        coordenadas = self.parameterAsEnum(
            parameters,
            self.COORD,
            context
        )

        logo = self.parameterAsFile(
            parameters,
            self.LOGO,
            context
        )
        if logo:
            LOGO = 'jpg;base64,'+img2html_resized(logo, lado=380)
        else:
            LOGO = 'png;base64,'+lftools_logo

        SLOGAN = self.parameterAsString(
            parameters,
            self.SLOGAN,
            context
        )
        if not SLOGAN:
            SLOGAN = ''
        else:
            SLOGAN = SLOGAN.replace('\n', '<br>')

        decimal = self.parameterAsInt(
            parameters,
            self.DECIMAL,
            context
        )
        if decimal is None or decimal<1:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.DECIMAL))

        format_num = '{:,.Xf}'.replace('X', str(decimal))

        projecao = self.parameterAsBool(
            parameters,
            self.PROJECTION,
            context
        )

        topologia = self.parameterAsBool(
            parameters,
            self.TOPOLOGY,
            context
        )

        atributos = self.parameterAsBool(
            parameters,
            self.ATTRIBUTES,
            context
        )

        meses = {1: 'janeiro', 2:'fevereiro', 3: 'março', 4:'abril', 5:'maio', 6:'junho', 7:'julho', 8:'agosto', 9:'setembro', 10:'outubro', 11:'novembro', 12:'dezembro'}

        # Validando atributos dos dados de entrada
        if atributos:
            feedback.pushInfo(self.tr('Validating layer attributes...', 'Validando atributos das camadas...' ))
            # ponto_limite
            ordem_list = list(range(1,vertices.featureCount()+1))
            ordem_comp = []
            for feat in vertices.getFeatures():
                try:
                    ordem_comp += [feat['sequence']]
                    codigo_item = feat['code']
                except:
                    raise QgsProcessingException(self.tr('Check that your layer "limit_point_p" has the correct field names for the TopoGeo model! More information: https://bit.ly/3FDNQGC', 'Verifique se sua camada "Ponto Limite" está com os nomes dos campos corretos para o modelo TopoGeo! Mais informações: https://geoone.com.br/ebook_gratis/'))
                if not codigo_item or codigo_item in ['', ' ']:
                    raise QgsProcessingException(self.tr('The code attribute must be filled in for all features!', 'O atributo código deve ser preenchido para todas as feições!'))
            ordem_comp.sort()
            if ordem_list != ordem_comp:
                raise QgsProcessingException(self.tr('The point sequence field must be filled in correctly!', 'O campo de sequência dos pontos deve preenchido corretamente!'))

            # elemento_confrontante
            for feat in limites.getFeatures():
                try:
                    att1 = feat['start_pnt_descr']
                    att2 = feat['borderer']
                except:
                    raise QgsProcessingException(self.tr('Check that your layer "boundary_element_l" has the correct field names for the TopoGeo model! More information: https://bit.ly/3FDNQGC', 'Verifique se sua camada "Elemento confrontante" está com os nomes dos campos corretos para o modelo TopoGeo! Mais informações: https://geoone.com.br/ebook_gratis/'))
                if not att1 or att1 in ['', ' ']:
                    raise QgsProcessingException(self.tr('The attribute of the starting point description must be filled in for all features!', 'O atributo de descrição do ponto inicial deve ser preenchido para todas as feições!'))
                if not att2 or att2 in ['', ' ']:
                    raise QgsProcessingException(self.tr("The confrontant's name must be filled in for all features!", 'O nome do confrontante deve ser preenchido para todas as feições!'))

        # Validando a Topologia dos dados de entrada
        if topologia:
            feedback.pushInfo(self.tr('Validating topology of geometries...', 'Validando topologia das geometrias...' ))
            # Verificar se cada vértice da camada limite (linha) tem o correspondente da camada vétice (ponto)
            for feat1 in limites.getFeatures():
                geom1 = feat1.geometry()
                if geom1.isMultipart():
                    linha = feat1.geometry().asMultiPolyline()[0]
                else:
                    linha = feat1.geometry().asPolyline()
                for pnt in linha:
                    corresp = False
                    for feat2 in vertices.getFeatures():
                        vert = feat2.geometry().asPoint()
                        if vert == pnt:
                            corresp = True
                            continue
                    if not corresp:
                        raise QgsProcessingException(self.tr('Coordinate point ({}, {}) of the "boundary_element_l" layer has no correspondent in the "limit_point_p" layer!',
                                                             'Ponto de coordenadas ({}, {}) da camada "Elemento Confrontante" não possui correspondente na camada "Ponto Limite"!').format(pnt.x(), pnt.y()))

    		# Verificar se cada vértice da camada parcela (polígono) tem o correspondente da camada vétice (ponto)
            for feat1 in area.getFeatures():
                geom1 = feat1.geometry()
                if geom1.isMultipart():
                    pols = geom1.asMultiPolygon()
                else:
                    pols = [geom1.asPolygon()]
                for pol in pols:
                    for pnt in pol[0]:
                        corresp = False
                        for feat2 in vertices.getFeatures():
                            vert = feat2.geometry().asPoint()
                            if vert == pnt:
                                corresp = True
                                continue
                        if not corresp:
                            raise QgsProcessingException(self.tr('Coordinate point ({}, {}) of the "property_area_a" layer has no correspondent in the "limit_point_p" layer!',
                                                                 'Ponto de coordenadas ({}, {}) da camada "Área do imóvel" não possui correspondente na camada "Ponto Limite"!').format(pnt.x(), pnt.y()))

            # Verificar se cada vértice da camada Ponto Limite tem o correspondente da camada Elemento confrontante
            for feat1 in vertices.getFeatures():
                geom1 = feat1.geometry()
                vert = geom1.asPoint()
                geom1 = geom1.buffer(0.001/110000,5)
                corresp = False
                for feat2 in limites.getFeatures():
                    geom2 = feat2.geometry()
                    if geom2.intersects(geom1):
                        corresp = True
                        break
                if not corresp:
                    raise QgsProcessingException(self.tr('Coordinate point ({}, {}) of the "limit_point_p" layer has no correspondent in the "boundary_element_l" layer!',
                                                         'Ponto de coordenadas ({}, {}) da camada "Ponto Limite" não possui correspondente na camada "Elemento confrontante"!').format(vert.x(), vert.y()))

            # Geometrias duplicadas na camada limit_point_p
            pontos = []
            for feat1 in vertices.getFeatures():
                vert = feat1.geometry().asPoint()
                if vert not in pontos:
                    pontos += [vert]
                else:
                    raise QgsProcessingException(self.tr('Coordinate point ({}, {}) of the "limit_point_p" layer is duplicated!',
                                                         'Ponto de coordenadas ({}, {}) da camada "Ponto Limite" está duplicado!').format(vert.x(), vert.y()))
            # Nós duplicados dentro da camada boundary_element_l
            for feat1 in limites.getFeatures():
                geom1 = feat1.geometry()
                if geom1.isMultipart():
                    linha = feat1.geometry().asMultiPolyline()[0]
                else:
                    linha = feat1.geometry().asPolyline()
                pontos = []
                for pnt in linha:
                    if pnt not in pontos:
                        pontos += [pnt]
                    else:
                        raise QgsProcessingException(self.tr('Coordinate point ({}, {}) of the "boundary_element_l" layer is duplicated!',
                                                             'Ponto de coordenadas ({}, {}) da camada "Elemento confrontante" está duplicado!').format(pnt.x(), pnt.y()))
            # Nós duplicados dentro da camada property_area_a
            for feat1 in area.getFeatures():
                geom1 = feat1.geometry()
                if geom1.isMultipart():
                    pol = feat1.geometry().asMultiPolygon()[0][0]
                else:
                    pol = feat1.geometry().asPolygon()[0]
                pontos = []
                for pnt in pol[:-1]:
                    if pnt not in pontos:
                        pontos += [pnt]
                    else:
                        raise QgsProcessingException(self.tr('Coordinate point ({}, {}) of the "property_area_a" layer is duplicated!',
                                                             'Ponto de coordenadas ({}, {}) da camada "Área do imóvel" está duplicado!').format(pnt.x(), pnt.y()))

        feedback.pushInfo(self.tr('Sequencing "boundary_element_l" features...', 'Ordenando a sequência dos confrontantes...' ))
        # Pegando ponto inicial
        for feat1 in vertices.getFeatures():
            ordem_pnt = feat1['sequence']
            if ordem_pnt == 1:
                ponto_ini = feat1.geometry().asPoint()
        # listando confrontantes
        dic_linhas = {}
        for linha in limites.getFeatures():
            dic_linhas[linha.id()] = linha
        # idenficando primeiro confrontante
        first_lin = -1
        lista_ordem = []
        last_coord = []
        for item in dic_linhas:
            geom = dic_linhas[item].geometry()
            if geom.isMultipart():
                coord = geom.asMultiPolyline()[0]
            else:
                coord = geom.asPolyline()
            if coord[0] == ponto_ini:
                lista_ordem += [item]
                last_coord += [coord[-1]]
                break
        # Verificar sequência dos confrontantes
        cont = 0
        while cont < len(dic_linhas)-1:
            encontrou = False
            ponto_fim = last_coord[-1]
            for item in dic_linhas:
                if item not in lista_ordem:
                    geom = dic_linhas[item].geometry()
                    if geom.isMultipart():
                        coord = geom.asMultiPolyline()[0]
                    else:
                        coord = geom.asPolyline()
                    ponto_ini = coord[0]
                    if ponto_fim == ponto_ini:
                        lista_ordem += [item]
                        last_coord += [coord[-1]]
                        encontrou = True
                        cont += 1
                        break
            if not encontrou:
                raise QgsProcessingException(self.tr('Coordinate point ({}, {}) of the "boundary_element_l" layer is not connected!',
                                                     'Ponto de coordenadas ({}, {}) da camada "Elemento confrontante" não está conectado!').format(ponto_fim.x(), ponto_fim.y()))

        # Pegando informações dos confrontantes (limites)
        ListaDescr = []
        ListaCont = []
        soma = 0
        for item in lista_ordem:
            linha = dic_linhas[item]
            geom = linha.geometry()
            if geom.isMultipart():
                Lin_coord = geom.asMultiPolyline()[0]
            else:
                Lin_coord = geom.asPolyline()
            ListaDescr += [[str2HTML(linha['start_pnt_descr']), str2HTML(linha['borderer'])]]
            cont = len(Lin_coord)
            ListaCont += [(soma, cont-1)]
            soma += cont-1

        # Pegando o SRC do Projeto
        SRC = QgsProject.instance().crs().description()

        # Verificando o SRC
        if QgsProject.instance().crs().isGeographic():
            raise QgsProcessingException(self.tr('The Project CRS must be projected!', 'O SRC do Projeto deve ser Projetado!'))
        feedback.pushInfo(self.tr('Project CRS is {}.', 'SRC do Projeto é {}.').format(SRC))

        # Número de Pontos
        if vertices.featureCount() < 3:
            raise QgsProcessingException(self.tr('The number of points must be greater than 2!', 'O número de pontos deve ser maior que 2!'))

        # Verificar se possui coordenada Z
        for feat in vertices.getFeatures():
                geom = feat.geometry()
                break

        if str(geom2PointList(geom).z()) == 'nan': #PointZ
            raise QgsProcessingException(self.tr('Limit Point layer must be "PointZ" type!', 'Camada pontos limites deve ser do tipo "PointZ"!'))

        # Dados do levantamento
        for feat in area.getFeatures():
                feat1 = feat
                break

        geom = feat1.geometry()
        centroideG = geom.centroid().asPoint()

        # Verificar se a projeção UTM do Projeto está correta
        if projecao:
            fuso, hemisf = FusoHemisf(centroideG)
            if SRC.split(' ')[-1] != str(fuso)+hemisf :
                raise QgsProcessingException(self.tr('Warning: Make sure your projection is correct!'.upper(), 'Aviso: Verifique se sua projeção está correta!'.upper()))

        # Área do imóvel
        Fields = area.fields()
        fieldnames = [field.name() for field in Fields]
        for fieldname in fieldnames:
            att = feat1[fieldname]
            if not att or att in ['', ' ']:
                raise QgsProcessingException(self.tr('All attributes of the class "area_imovel" must be filled!', 'Todos os atributos da classe "area_imovel" devem ser preenchido!'))

        # Transformar Coordenadas de Geográficas para o sistema UTM
        coordinateTransformer = QgsCoordinateTransform()
        coordinateTransformer.setDestinationCrs(QgsProject.instance().crs())
        coordinateTransformer.setSourceCrs(vertices.sourceCrs())

        pnts = {}

        for feat in vertices.getFeatures():
            geom = feat.geometry()
            if geom.isMultipart():
                pnts[feat['sequence']] = [coordinateTransformer.transform(geom.asMultiPoint()[0]), feat['type'], feat['code'], (geom.constGet()[0].x(), geom.constGet()[0].y(), geom.constGet()[0].z())]
            else:
                pnts[feat['sequence']] = [coordinateTransformer.transform(geom.asPoint()), feat['type'], feat['code'], (geom.constGet().x(), geom.constGet().y(), geom.constGet().z())]

        # Cálculo dos Azimutes e Distâncias
        tam = len(pnts)
        Az_lista, Dist = [], []
        for k in range(tam):
            pntA = pnts[k+1][0]
            pntB = pnts[max((k+2)%(tam+1),1)][0]
            Az_lista += [(180/pi)*azimute(pntA, pntB)[0]]
            Dist += [sqrt((pntA.x() - pntB.x())**2 + (pntA.y() - pntB.y())**2)]


        def CoordN (x, y, z):
            if coordenadas in (0,1,2,3):
                Xn = self.tr(format_num.format(x), format_num.format(x).replace(',', 'X').replace('.', ',').replace('X', '.'))
                Yn = self.tr(format_num.format(y), format_num.format(y).replace(',', 'X').replace('.', ',').replace('X', '.'))
            if coordenadas in (4,5,6,7):
                Xn = str2HTML(self.tr(dd2dms(x,4), dd2dms(x,4).replace('.', ','))).replace('-','') + 'W' if x < 0 else 'E'
                Yn = str2HTML(self.tr(dd2dms(y,4), dd2dms(y,4).replace('.', ','))).replace('-','') + 'S' if y < 0 else 'N'
            Zn = self.tr(format_num.format(z), format_num.format(z).replace(',', 'X').replace('.', ',').replace('X', '.'))

            if coordenadas == 0:
                txt = '''<b>N [Yn]m </b>''' + self.tr('and','e') +''' <b>E [Xn]m</b>'''
                return txt.replace('[Yn]', Yn).replace('[Xn]', Xn)
            elif coordenadas == 1:
                txt = '''<b>E [Xn]m </b>''' + self.tr('and','e') +''' <b>N [Yn]m</b>'''
                return txt.replace('[Yn]', Yn).replace('[Xn]', Xn)
            elif coordenadas == 2:
                txt = '''<b>N [Yn]m</b>, <b>E [Xn]m</b> ''' + self.tr('and','e') +''' <b>h [Zn]m</b>'''
                return txt.replace('[Yn]', Yn).replace('[Xn]', Xn).replace('[Zn]', Zn)
            elif coordenadas == 3:
                txt = '''<b>E [Xn]m</b>, <b>N [Yn]m</b> ''' + self.tr('and','e') +''' <b>h [Zn]m</b>'''
                return txt.replace('[Yn]', Yn).replace('[Xn]', Xn).replace('[Zn]', Zn)
            elif coordenadas == 4:
                txt = '''<b> [Yn] </b>''' + self.tr('and','e') +''' <b> [Xn]</b>'''
                return txt.replace('[Yn]', Yn).replace('[Xn]', Xn)
            elif coordenadas == 5:
                txt = '''<b> [Xn] </b>''' + self.tr('and','e') +''' <b> [Yn]</b>'''
                return txt.replace('[Yn]', Yn).replace('[Xn]', Xn)
            elif coordenadas == 6:
                txt = '''<b> [Yn]</b>, <b> [Xn]</b> ''' + self.tr('and','e') +''' <b>h [Zn]m</b>'''
                return txt.replace('[Yn]', Yn).replace('[Xn]', Xn).replace('[Zn]', Zn)
            elif coordenadas == 7:
                txt = '''<b> [Xn]</b>, <b> [Yn]</b> ''' + self.tr('and','e') +''' <b>h [Zn]m</b>'''
                return txt.replace('[Yn]', Yn).replace('[Xn]', Xn).replace('[Zn]', Zn)


        texto_inicial = '''
    <!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
    <html>
    <head>
      <meta content="text/html; charset=ISO-8859-1"
     http-equiv="content-type">
      <title>'''+ self.tr('Descriptive memorial', 'Memorial descritivo') + '''</title>
      <link rel = "icon" href = "https://github.com/LEOXINGU/lftools/blob/main/images/lftools.png?raw=true" type = "image/x-icon">
    </head>
    <body>
    <div style="text-align: center;"><span style="font-weight: bold;"><br>
    <img height="80" src="data:image/'''+ LOGO + '''">
    <br>'''+ str2HTML(SLOGAN) + '''</span><br style="font-weight: bold;">
    <br></div>
    <p class="western"
     style="margin-bottom: 0.0001pt; text-align: center;"
     align="center"><b><u><span style="font-size: 12pt;">'''+ self.tr('DESCRIPTIVE MEMORIAL','MEMORIAL DESCRITIVO') + '''</span></u></b><o:p></o:p></p>
    <p class="western" style="margin-bottom: 0.0001pt;"><o:p>&nbsp;</o:p></p>
    <table class="MsoTableGrid"
     style="border: medium none ; border-collapse: collapse;"
     border="0" cellpadding="0" cellspacing="0">
      <tbody>
        <tr style="">
          <td style="padding: 0cm 5.4pt; width: 247.85pt;"
     valign="top" width="330">
          <p class="western" style="margin-bottom: 0.0001pt;"><b>'''+ self.tr('Property',str2HTML('Imóvel')) + ''': </b>[IMOVEL]<o:p></o:p></p>
          </td>
          <td style="padding: 0cm 5.4pt; width: 176.85pt;"
     valign="top" width="236">
          <p class="western" style="margin-bottom: 0.0001pt;"><b>''' + self.tr('Real estate registry', 'Registro') + ''':</b>
    [REGISTRO]<o:p></o:p></p>
          </td>
        </tr>
        <tr style="">
          <td colspan="2"
     style="padding: 0cm 5.4pt; width: 424.7pt;" valign="top"
     width="566">
          <p class="western" style="margin-bottom: 0.0001pt;"><b>''' + self.tr('Owner', str2HTML('Proprietário')) + ''':</b>
    [PROPRIETARIO]<o:p></o:p></p>
          </td>
        </tr>
        <tr style="">
          <td style="padding: 0cm 5.4pt; width: 247.85pt;"
     valign="top" width="330">
          <p class="western" style="margin-bottom: 0.0001pt;"><b>''' + self.tr('County', str2HTML('Município')) + ''':</b>
    [MUNICIPIO]<b><o:p></o:p></b></p>
          </td>
          <td style="padding: 0cm 5.4pt; width: 176.85pt;"
     valign="top" width="236">
          <p class="western" style="margin-bottom: 0.0001pt;"><b>''' + self.tr('State', str2HTML('Estado')) + ''':
          </b>[UF]<o:p></o:p></p>
          </td>
        </tr>
        <tr style="">
          <td colspan="2"
     style="padding: 0cm 5.4pt; width: 424.7pt;" valign="top"
     width="566">
          <p class="western" style="margin-bottom: 0.0001pt;"><b>''' + self.tr('Registration(s)', str2HTML('Matrícula(s)')) + ''':</b>
    [MATRICULAS]<o:p></o:p></p>
          </td>
        </tr>
        <tr style="">
          <td style="padding: 0cm 5.4pt; width: 247.85pt;"
     valign="top" width="330">
          <p class="western" style="margin-bottom: 0.0001pt;"><b>''' + self.tr('Area', str2HTML('Área')) + ''' (m<sup>2</sup>): </b>[AREA]<o:p></o:p></p>
          </td>
          <td style="padding: 0cm 5.4pt; width: 176.85pt;"
     valign="top" width="236">
          <p class="western" style="margin-bottom: 0.0001pt;"><b>''' + self.tr('Perimeter', str2HTML('Perímetro')) + ''' (m):</b> [PERIMETRO]<o:p></o:p></p>
          </td>
        </tr>
        <tr style="">
          <td colspan="2"
     style="padding: 0cm 5.4pt; width: 424.7pt;" valign="top"
     width="566">
          <p class="western" style="margin-bottom: 0.0001pt;"><b>''' + self.tr('Coordinate Reference System', str2HTML('Sistema de Referência de Coordenadas')) + ''':</b> [SRC]<b><o:p></o:p></b></p>
          </td>
        </tr>
      </tbody>
    </table>
    <p class="western" style="margin-bottom: 0.0001pt;"><o:p>&nbsp;</o:p></p>
    <p class="western"
     style="margin-bottom: 0.0001pt; text-align: justify;">'''+ self.tr('The description of this perimeter begins ', str2HTML('Inicia-se a descrição deste perímetro n'))

        texto_var1 = self.tr('at the vertex ', str2HTML('o vértice ')) + '''<b>[Vn]</b>, '''+ self.tr('with coordinates ', 'de coordenadas ') + '''[Coordn],
    [Descr_k], '''+ self.tr('from this, it continues to confront [Confront_k], with the following flat azimuths and distances: [Az_n] and [Dist_n]m up to ',
                   str2HTML('deste, segue confrontando com [Confront_k], com os seguintes azimutes planos e distâncias: [Az_n] e [Dist_n]m até '))

        texto_var2 = self.tr('the vertex ', str2HTML('o vértice ')) + '''<span> </span><b>[Vn]</b>, '''+ self.tr('with coordinates ', 'de coordenadas ') + '''[Coordn]; '''+ self.tr('[Az_n] and [Dist_n]m up to ', str2HTML('[Az_n] e [Dist_n]m até '))

        texto_final = self.tr('the vertex ', str2HTML('o vértice ')) + '''<b>[P-01]</b>, '''+ self.tr('with coordinates', 'de coordenadas') + ''' [Coord1],
    ''' + self.tr('the starting point for the description of this perimeter. All coordinates described here are georeferenced to the Geodetic Reference System (GRS)',
         str2HTML('ponto inicial da descrição deste perímetro. Todas as coordenadas aqui descritas estão georreferenciadas ao Sistema Geodésico de Referência (SGR)')) + ''' <b>[GRS]</b>,
    ''' + self.tr('and are projected in the UTM system, zone [FUSO] and hemisphere [HEMISFERIO], from which all azimuths and distances, area and perimeter were calculated.',
         str2HTML('sendo projetadas no Sistema UTM, fuso [FUSO] e hemisfério [HEMISFERIO], a partir das quais todos os azimutes e distâncias, área e perímetro foram calculados.')) + '''
     <o:p></o:p></p>
    <p class="western"
     style="margin-bottom: 0.0001pt; text-align: right;"
     align="right">[LOCAL], [DATA].<o:p></o:p></p>
    <p class="western" style="margin-bottom: 0.0001pt;"><o:p>&nbsp;</o:p></p>
    <p class="western"
     style="margin: 0cm 0cm 0.0001pt; text-align: center;"
     align="center">___________________________________________<o:p></o:p></p>
    <p class="western"
     style="margin: 0cm 0cm 0.0001pt; text-align: center;"
     align="center">[RESP_TEC]<o:p></o:p></p>
    <p class="western"
     style="margin: 0cm 0cm 0.0001pt; text-align: center;"
     align="center">[CREA]<o:p></o:p></p>
    <p class="western"
     style="margin: 0cm 0cm 0.0001pt; text-align: center;"
     align="center">''' + self.tr('TECHNICAL MANAGER', str2HTML('RESPONSÁVEL TÉCNICO')) + '''<o:p></o:p></p>
    <p class="MsoNormal"><o:p>&nbsp;</o:p></p>
    </body>
    </html>
    '''
        # Inserindo dados iniciais do levantamento
        try:
            itens = {'[IMOVEL]': str2HTML(feat1['property']),
                    '[PROPRIETARIO]': str2HTML(feat1['owner']),
                    '[UF]': feat1['state'],
                    '[MATRICULAS]': str2HTML(feat1['transcript']),
                    '[AREA]': self.tr(format_num.format(feat1['area']), format_num.format(feat1['area']).replace(',', 'X').replace('.', ',').replace('X', '.')),
                    '[SRC]': self.tr(SRC, SRC.replace('zone', 'fuso')),
                    '[REGISTRO]': str2HTML(feat1['registry']),
                    '[MUNICIPIO]': str2HTML(feat1['county']),
                    '[PERIMETRO]': self.tr(format_num.format(feat1['perimeter']), format_num.format(feat1['perimeter']).replace(',', 'X').replace('.', ',').replace('X', '.')),
                        }
        except:
            raise QgsProcessingException(self.tr('Check that your layer "property_area_a" has the correct field names for the TopoGeo model! More information: https://bit.ly/3FDNQGC', 'Verifique se sua camada "Área do imóvel" está com os nomes dos campos corretos para o modelo TopoGeo! Mais informações: https://geoone.com.br/ebook_gratis/'))
        for item in itens:
                texto_inicial = texto_inicial.replace(item, itens[item])

        LINHAS = texto_inicial
        for w,t in enumerate(ListaCont):
            linha0 = texto_var1
            itens =    {'[Vn]': pnts[t[0]+1][2],
                        '[Coordn]': CoordN(pnts[t[0]+1][0].x(), pnts[t[0]+1][0].y(), pnts[t[0]+1][3][2]) if coordenadas in (0,1,2,3) else CoordN(pnts[t[0]+1][3][0], pnts[t[0]+1][3][1], pnts[t[0]+1][3][2]),
                        '[Az_n]': str2HTML(self.tr(dd2dms(Az_lista[t[0]],1), dd2dms(Az_lista[t[0]],1).replace('.', ','))),
                        '[Dist_n]': self.tr(format_num.format(Dist[t[0]]), format_num.format(Dist[t[0]]).replace(',', 'X').replace('.', ',').replace('X', '.')),
                        '[Descr_k]': ListaDescr[w][0],
                        '[Confront_k]': ListaDescr[w][1]
                        }
            for item in itens:
                linha0 = linha0.replace(item, itens[item])
            LINHAS += linha0
            LIN0 = ''
            for k in range(t[0]+1, t[0]+t[1]):
                linha1 = texto_var2
                itens = {'[Vn]': pnts[k+1][2],
                        '[Coordn]': CoordN(pnts[k+1][0].x(), pnts[k+1][0].y(), pnts[k+1][3][2]) if coordenadas in (0,1,2,3) else CoordN(pnts[k+1][3][0], pnts[k+1][3][1], pnts[k+1][3][2]),
                        '[Az_n]': str2HTML(self.tr(dd2dms(Az_lista[k],1), dd2dms(Az_lista[k],1).replace('.', ','))),
                        '[Dist_n]': self.tr(format_num.format(Dist[k]), format_num.format(Dist[k]).replace(',', 'X').replace('.', ',').replace('X', '.'))
                        }
                for item in itens:
                    linha1 = linha1.replace(item, itens[item])
                LIN0 += linha1
            LINHAS += LIN0

        # Inserindo dados finais
        itens = {   '[P-01]': pnts[1][2],
                    '[Coord1]': CoordN(pnts[1][0].x(), pnts[1][0].y(), pnts[1][3][2])  if coordenadas in (0,1,2,3) else CoordN(pnts[1][3][0], pnts[1][3][1], pnts[1][3][2]),
                    '[GRS]': SRC.split(' /')[0],
                    '[FUSO]': str(FusoHemisf(centroideG)[0]),
                    '[HEMISFERIO]': FusoHemisf(centroideG)[1],
                    '[RESP_TEC]': str2HTML(feat1['tech_manager'].upper()),
                    '[CREA]': str2HTML(feat1['prof_id']),
                    '[LOCAL]': str2HTML((feat1['county']) +' - ' + (feat1['state']).upper()),
                    '[DATA]': self.tr((feat1['survey_date'].toPyDate()).strftime("%b %d, %Y"),
                                       (feat1['survey_date'].toPyDate()).strftime("%d de {} de %Y").format(meses[feat1['survey_date'].month()]))
                    }

        for item in itens:
                texto_final = texto_final.replace(item, itens[item])

        LINHAS += texto_final

        output = self.parameterAsFileOutput(parameters, self.HTML, context)
        arq = open(output, 'w')
        arq.write(LINHAS)
        arq.close()

        # Check for cancelation
        if feedback.isCanceled():
            return {}

        feedback.pushInfo(self.tr('Operation completed successfully!', 'Operação finalizada com sucesso!'))
        feedback.pushInfo(self.tr('Leandro França - Cartographic Engineer', 'Leandro França - Eng Cart'))

        return {self.HTML: output}
