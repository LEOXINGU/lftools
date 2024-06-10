# -*- coding: utf-8 -*-

"""
***************************************************************************
    Doc_DescriptiveTable.py
    ---------------------
    Date                 : Jul 10
    Copyright            : (C) 2020 by Leandro França
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
__date__ = 'Jul 10'
__copyright__ = '(C) 2020, Leandro França'

from PyQt5.QtCore import QCoreApplication
from qgis.core import (QgsProcessing,
                       QgsFeatureSink,
                       QgsProcessingException,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterNumber,
                       QgsProcessingParameterString,
                       QgsProcessingParameterNumber,
                       QgsProcessingParameterEnum,
                       QgsFeatureRequest,
                       QgsPoint, QgsLineString, QgsPolygon,
                       QgsGeometry,
                       QgsExpression,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterFeatureSink,
                       QgsProcessingParameterFileDestination,
                       QgsApplication,
                       QgsProject,
                       QgsCoordinateTransform,
                       QgsCoordinateReferenceSystem)

import os
from math import pi, sqrt
from lftools.geocapt.imgs import Imgs
from lftools.geocapt.cartography import MeridianConvergence, SRC_Projeto, geom2PointList, AzimuteDistanciaSGL
from lftools.geocapt.topogeo import azimute, dd2dms, str2HTML, validar_precisoes
from qgis.PyQt.QtGui import QIcon

class DescriptiveTable(QgsProcessingAlgorithm):

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
        return DescriptiveTable()

    def name(self):
        return 'descriptivetable'

    def displayName(self):
        return self.tr('Synthetic deed description', 'Memorial sintético')

    def group(self):
        return self.tr('Documents', 'Documentos')

    def groupId(self):
        return 'documents'

    def tags(self):
        return self.tr('monograph,table,deed,description,geodetic,descriptive,syntetic,memorial,property,topography,survey,real,estate,georreferencing,plan,cadastral,cadastre,documnt').split(',')

    def icon(self):
        return QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images/document.png'))

    figure = 'images/tutorial/doc_descriptive_table.jpg'
    txt_en = '''This tool generates the Vertices and Sides Descriptive Table, also known as Synthetic Deed Description, based on the attributes, sequence and code, in the point layer's attribute table.'''
    txt_pt = 'Esta ferramenta gera a Tabela Descriva de Vértices e Lados, também conhecida como Memorial Descritivo Sintético, a partir de uma camada de pontos com os atributos de código e ordem (sequência) dos pontos.'

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

    PONTOS = 'PONTOS'
    HTML = 'HTML'
    INICIO = 'INICIO'
    FIM = 'FIM'
    TITULO = 'TITULO'
    FONTSIZE = 'FONTSIZE'
    DECIMAL = 'DECIMAL'
    MODEL = 'MODEL'
    CALC = 'CALC'

    def initAlgorithm(self, config=None):

        # 'INPUTS'
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.PONTOS,
                self.tr('Boundary Survey Points', 'Pontos de Limite'),
                types=[QgsProcessing.TypeVectorPoint]
            )
        )

        self.addParameter(
            QgsProcessingParameterNumber(
                self.INICIO,
                self.tr('First vertex', 'Primeiro vértice'),
                type = QgsProcessingParameterNumber.Type.Integer,
                defaultValue = 1
                )
            )

        self.addParameter(
            QgsProcessingParameterNumber(
                self.FIM,
                self.tr('Last vertex', 'Último vértice'),
                type = QgsProcessingParameterNumber.Type.Integer,
                defaultValue = -1
                )
            )

        self.addParameter(
            QgsProcessingParameterString(
                self.TITULO,
                self.tr('Title', 'Título'),
                defaultValue = self.tr("SOMEONE'S PROPERTY", 'IMÓVEL DE ALGUÉM')
            )
        )

        self.addParameter(
            QgsProcessingParameterNumber(
                self.FONTSIZE,
                self.tr('Font size', 'Tamanho da fonte'),
                type = QgsProcessingParameterNumber.Type.Integer,
                defaultValue = 12
                )
            )

        self.addParameter(
            QgsProcessingParameterString(
                self.DECIMAL,
                self.tr('Decimal places', 'Casas decimais'),
                defaultValue = '2' # 2,1,2 - Precisões das coordenadas, azimutes, distâncias
                )
            )

        tipos = [self.tr('Planimetric (E,N)','Planimétrico (E,N)'),
                  self.tr('Planimetric (N,E)','Planimétrico (N,E)'),
				  self.tr('E, N, h, azimuth, distance', 'E, N, h, azimute, distância'),
                  self.tr('E, N, h'),
                  self.tr('Lon, Lat, h, azimuth, distance', 'Lon, Lat, h, azimute, distância'),
                  self.tr('Lon, Lat, h'),
                  self.tr('Lon, Lat, E, N, h, azimuth, distance', 'Lon, Lat, h, azimute, distância'),
                  self.tr('Lon, Lat, E, N, h'),
                  self.tr('Lon and Lat (without suffix), h, azimuth, distance', 'Lon e Lat (sem sufixo), h, azimute, distância'),
                  self.tr('Lon and Lat (without suffix), h', 'Lon e Lat (sem sufixo), h'),
                  self.tr('Lon and Lat (without suffix), E, N, h, azimuth, distance', 'Lon e Lat (sem sufixo), h, azimute, distância'),
                  self.tr('Lon and Lat (without suffix), E, N, h', 'Lon e Lat (sem sufixo), E, N, h')
               ]

        self.addParameter(
            QgsProcessingParameterEnum(
                self.MODEL,
                self.tr('Model', 'Modelo'),
				options = tipos,
                defaultValue= 0
            )
        )

        calc = [self.tr('Project CRS', 'SRC do projeto'),
                 self.tr('Local Tangent Plane (LTP)', 'Sistema Geodésico Local (SGL)'),
                 self.tr('LTP, Puissant azimuth', 'SGL, azimute de Puissant'),
               ]

        self.addParameter(
            QgsProcessingParameterEnum(
                self.CALC,
                self.tr('Calculation of azimuths, distances and area',
                        'Cálculo de azimutes, distâncias e área'),
				options = calc,
                defaultValue = 0
            )
        )

        # 'OUTPUTS'
        self.addParameter(
            QgsProcessingParameterFileDestination(
                self.HTML,
                self.tr('Synthetic deed description', 'Memorial Sintético'),
                self.tr('HTML files (*.html)')
            )
        )


    def processAlgorithm(self, parameters, context, feedback):

        vertices = self.parameterAsSource(parameters,
                                                     self.PONTOS,
                                                     context)

        if vertices is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.PONTOS))

        ini = self.parameterAsInt(
            parameters,
            self.INICIO,
            context
        )
        if ini is None or ini<1:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.INICIO))

        fim = self.parameterAsInt(
            parameters,
            self.FIM,
            context
        )
        if fim is None or fim==0 or fim<-1:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.FIM))
        if fim !=-1:
            if fim < ini:
                raise QgsProcessingException(self.invalidSourceError(parameters, self.FIM))

        titulo = self.parameterAsString(parameters,
                                         self.TITULO,
                                         context)
        if titulo is None:
            titulo = ''
        if not titulo in ['',' ']:
            titulo = ' - ' + titulo

        fontsize = self.parameterAsInt(
            parameters,
            self.FONTSIZE,
            context
        )
        if fontsize is None or ini<1:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.FONTSIZE))

        decimal = self.parameterAsString(
            parameters,
            self.DECIMAL,
            context
        )
        # Validar dado de entrada
        # Precisões das coordenadas, azimutes, distâncias, área, perímetro
        decimal = decimal.replace(' ','').split(',')
        if not validar_precisoes(decimal,[1,3]):
            raise QgsProcessingException(self.invalidSourceError(parameters, self.DECIMAL))
        format_utm = '{:,.Xf}'.replace('X', decimal[0])
        decimal_geo = int(decimal[0])+3
        if len(decimal) == 1:
            decimal_azim = 1
            format_dist = '{:,.Xf}'.replace('X', decimal[0])
        elif len(decimal) == 5:
            decimal_azim = int(decimal[1])
            format_dist = '{:,.Xf}'.replace('X', decimal[2])


        modelo = self.parameterAsEnum(
            parameters,
            self.MODEL,
            context
        )

        calculo = self.parameterAsEnum(
            parameters,
            self.CALC,
            context
        )

        # Pegando o SRC do Projeto
        SRC = QgsProject.instance().crs().description()
        # Verificando o SRC
        if QgsProject.instance().crs().isGeographic():
            raise QgsProcessingException(self.tr('The Project CRS must be projected!', 'O SRC do Projeto deve ser Projetado!'))
        feedback.pushInfo(self.tr('Project CRS is {}.', 'SRC do Projeto é {}.').format(SRC))

        # Validando dados de entrada

        # Teste para o modelo de BD
        modeloBD = None
        def TestModelo(campos_vertices):
            sentinela = True
            for campo in campos_vertices:
                if campo not in [field.name() for field in vertices.fields()]:
                    sentinela = False
                    break
            return sentinela

        if TestModelo(['code', 'sequence', 'type']):
            modeloBD = 'TG' # TopoGeo
            codigo, sequencia, tipo = ('code', 'sequence', 'type')
            feedback.pushInfo(self.tr('Layer in the TopoGeo model...', 'Camada no modelo TopoGeo...' ))

        if TestModelo(['vertice', 'indice', 'tipo_verti']):
            modeloBD = 'GR' # GeoRural
            codigo, sequencia, tipo = ('vertice', 'indice', 'tipo_verti')
            feedback.pushInfo('Camada no modelo GeoRural...' )

        if not modeloBD:
            raise QgsProcessingException(self.tr('Check that your layers have the correct field names for the TopoGeo model! More information: https://bit.ly/3FDNQGC', 'Verifique se suas camadas estão com os nomes dos campos corretos para o modelo de banco de dados (TopoGeo ou GeoRural)! Mais informações: https://geoone.com.br/ebook_gratis/'))

        # ponto_limite
        ordem_list = list(range(1,vertices.featureCount()+1))
        ordem_comp = []
        for feat in vertices.getFeatures():
            pnt = feat.geometry().asPoint()
            if pnt.x() < -180 or pnt.x() > 180 or pnt.y() < -90 or pnt.y() > 90:
                raise QgsProcessingException(self.tr('Input coordinates must be geodetic (longitude and latitude)!', 'As coordenadas de entrada devem ser geodésicas (longitude e latitude)!'))
            try:
                ordem_comp += [feat[sequencia]]
                codigo_item = feat[codigo]
            except:
                raise QgsProcessingException(self.tr('Check that your layer "limit_point_p" has the correct field names for the TopoGeo model! More information: https://bit.ly/3FDNQGC', 'Verifique se sua camada "Ponto Limite" está com os nomes dos campos corretos para o modelo TopoGeo! Mais informações: https://geoone.com.br/ebook_gratis/'))
            if not codigo_item or codigo_item in ['', ' ']:
                raise QgsProcessingException(self.tr('The code attribute must be filled in for all features!', 'O atributo código deve ser preenchido para todas as feições!'))
        ordem_comp.sort()
        if ordem_list != ordem_comp:
            raise QgsProcessingException(self.tr('The point sequence field must be filled in correctly!', 'O campo de sequência dos pontos deve preenchido corretamente!'))


        # Transformacao de Coordenadas Geograficas para Projetadas no sistema UTM
        crsDest = QgsCoordinateReferenceSystem(SRC_Projeto('EPSG'))
        coordinateTransformer = QgsCoordinateTransform()
        coordinateTransformer.setDestinationCrs(crsDest)
        coordinateTransformer.setSourceCrs(vertices.sourceCrs())

        pnts_UTM = {}
        pnts_GEO = {}
        for feat in vertices.getFeatures():
            pnt = feat.geometry().asPoint()
            coord = geom2PointList(feat.geometry())
            pnts_UTM[feat[sequencia]] = [coordinateTransformer.transform(pnt), feat[tipo], feat[codigo], MeridianConvergence(pnt.x(), pnt.y(), crsDest) ]
            pnts_GEO[feat[sequencia]] = [QgsPoint(pnt.x(),pnt.y(),coord.z()), feat[tipo], feat[codigo] ]

        # Calculo dos Azimutes e Distancias
        tam = len(pnts_UTM)
        Az_lista, Az_Geo_lista, Dist = [], [], []
        for k in range(tam):
            pntA = pnts_UTM[k+1][0]
            pntB = pnts_UTM[1 if k+2 > tam else k+2][0]
            Az_lista += [(180/pi)*azimute(pntA, pntB)[0]]
            ConvMerediana = pnts_UTM[k+1][3]
            Az_Geo_lista += [(180/pi)*azimute(pntA, pntB)[0]+ConvMerediana]
            Dist += [sqrt((pntA.x() - pntB.x())**2 + (pntA.y() - pntB.y())**2)]

        if calculo in (1,2):
            crsGeo = vertices.sourceCrs()
            # Criar polígono a partir dos pontos
            COORDS = []
            for k in range(tam):
                COORDS += [pnts_GEO[k+1][0]]
            anel = QgsLineString(COORDS + [COORDS[0]])
            pol = QgsPolygon(anel)
            geomGeo = QgsGeometry(pol)
            Az_lista, Dist = [], []
            rotulo_SGL = self.tr('LTP ','SLG ')
            if calculo == 1: # SGL
                rotulo_azimute = self.tr('LTP','SLG')
                sufixo_azimute = '<br>' + rotulo_azimute
                for k in range(tam):
                    pntA = pnts_GEO[k+1][0]
                    ind =  max((k+2)%(tam+1),1)
                    pntB = pnts_GEO[ind][0]
                    Az, dist = AzimuteDistanciaSGL(pntA, pntB, geomGeo, crsGeo, 'SGL')
                    Az_lista += [Az]
                    Dist += [dist]
            elif calculo == 2: # SGL e Puissant
                rotulo_azimute = self.tr('Puissant'.upper())
                sufixo_azimute = '<br>' + rotulo_azimute
                for k in range(tam):
                    pntA = pnts_GEO[k+1][0]
                    ind =  max((k+2)%(tam+1),1)
                    pntB = pnts_GEO[ind][0]
                    Az, dist = AzimuteDistanciaSGL(pntA, pntB, geomGeo, crsGeo, 'puissant')
                    Az_lista += [Az]
                    Dist += [dist]
        else:
            rotulo_azimute = self.tr('FLAT','PLANO')
            rotulo_SGL = ''
            sufixo_azimute = ''

        # Templates HTML
        if modelo in (0,1):
            coords = '<td>En</td> <td>Nn</td>' if modelo == 0 else '<td>Nn</td> <td>En</td>'
            linha = '''<tr>
              <td>Vn</td>
              [COORDS]
              <td>Ln</td>
              <td>Az_n</td>
              <td>AzG_n</td>
              <td>Dn</td>
            </tr>
            '''
            linha = linha.replace('[COORDS]', coords)

            texto = '''<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
            <html>
            <head>
              <title>''' + self.tr('Synthetic deed description', str2HTML('Memorial Sintético')) + '''</title>
              <link rel = "icon" href = "https://github.com/LEOXINGU/lftools/blob/main/images/lftools.png?raw=true" type = "image/x-icon">
            </head>
            <body>
            <table
            style="text-align: center; width: 100%; font-size: [FONTSIZE]px; font-family: Arial; border: medium none; border-collapse: collapse;"
            border="1" cellpadding="0" cellspacing="0">
            <tbody>
            <tr>
              <td colspan="7" rowspan="1">''' + self.tr('Synthetic deed description'.upper(), str2HTML('Memorial Sintético'.upper())) + '''[TITULO]</td>
            </tr>
            <tr>
              <td colspan="1" rowspan="2">''' + self.tr('VERTEX', str2HTML('VÉRTICE')) + '''</td>
              <td colspan="2" rowspan="1">''' + self.tr('COORDINATE', str2HTML('COORDENADA')) + '''</td>
              <td colspan="1" rowspan="2">''' + self.tr('SIDE', str2HTML('LADO')) + '''</td>
              <td colspan="2" rowspan="1">''' + self.tr('AZIMUTH', str2HTML('AZIMUTE')) + '''</td>
              <td colspan="1" rowspan="2">''' + self.tr('DISTANCE', str2HTML('DISTÂNCIA')) + '''<br>
              ''' + rotulo_SGL + '(m)</td>' + '''
            </tr>
            <tr>
            [COORDS]
              <td>''' + rotulo_azimute + '''</td>
              <td>''' + self.tr('TRUE', str2HTML('VERDADEIRO')) + '''</td>
            </tr>
            [LINHAS]
            </tbody>
            </table>
            <br>
            </body>
            </html>
            '''
            coords = '<td>E</td> <td>N</td>' if modelo == 0 else '<td>N</td> <td>E</td>'
            texto = texto.replace('[COORDS]', coords)

            LINHAS = ''
            if fim == -1 or fim > tam:
                fim = tam
            for k in range(ini-1,fim):
                linha0 = linha
                itens = {'Vn': pnts_UTM[k+1][2],
                            'En': self.tr(format_utm.format(pnts_UTM[k+1][0].x()), format_utm.format(pnts_UTM[k+1][0].x()).replace(',', 'X').replace('.', ',').replace('X', '.')),
                            'Nn': self.tr(format_utm.format(pnts_UTM[k+1][0].y()), format_utm.format(pnts_UTM[k+1][0].y()).replace(',', 'X').replace('.', ',').replace('X', '.')),
                            'Ln': pnts_UTM[k+1][2] + '/' + pnts_UTM[1 if k+2 > tam else k+2][2],
                            'Az_n': self.tr(dd2dms(Az_lista[k],decimal_azim), dd2dms(Az_lista[k],decimal_azim).replace('.', ',')),
                            'AzG_n':  self.tr(dd2dms(Az_Geo_lista[k],decimal_azim), dd2dms(Az_Geo_lista[k],decimal_azim).replace('.', ',')),
                            'Dn': self.tr(format_dist.format(Dist[k]), format_dist.format(Dist[k]).replace(',', 'X').replace('.', ',').replace('X', '.'))
                            }
                for item in itens:
                    linha0 = linha0.replace(item, itens[item])
                LINHAS += linha0
            resultado = texto.replace('[LINHAS]', LINHAS).replace('[TITULO]', str2HTML(titulo.upper())).replace('[FONTSIZE]', str(fontsize))

        else:
            texto = '''<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
            <html>
            <head>
              <title>''' + self.tr('Synthetic deed description', str2HTML('Memorial Sintético')) + '''</title>    </head>
            <body>
            <table
            style="text-align: center; width: 100%; font-size: [FONTSIZE]px; font-family: Arial; border: medium none; border-collapse: collapse;"
            border="1" cellpadding="0" cellspacing="0">
            <tbody>
            [CABECALHO]
            [LINHAS]
            </tbody>
            </table>
            <br>
            </body>
            </html>
            '''

            #Tipos de cabeçalhos

            # UTM
            if modelo == 2:
                linha = '''<tr>
              <td>Vn</td>
              <td>En</td>
              <td>Nn</td>
              <td>hn</td>
              <td>Ln</td>
              <td>Az_n</td>
              <td>Dn</td>
            </tr>
            '''
                cabec = '''<tr>
                  <td colspan="7" rowspan="1">''' + self.tr('Synthetic deed description'.upper(), str2HTML('Memorial Sintético'.upper())) + '''[TITULO]</td>
                </tr>
                <tr>
                  <td colspan="1" rowspan="2">''' + self.tr('VERTEX', str2HTML('VÉRTICE')) + '''</td>
                  <td colspan="3" rowspan="1">''' + self.tr('COORDINATE', str2HTML('COORDENADA')) + '''</td>
                  <td colspan="1" rowspan="2">''' + self.tr('SIDE', str2HTML('LADO')) + '''</td>
                  <td colspan="1" rowspan="2">''' + self.tr('AZIMUTH', str2HTML('AZIMUTE')) + sufixo_azimute + '''</td>
                  <td colspan="1" rowspan="2">''' + self.tr('DISTANCE', str2HTML('DISTÂNCIA')) + '''<br>
                  ''' + rotulo_SGL + '(m)</td>' + '''
                </tr>
                <tr>
                  <td>E</td>
                  <td>N</td>
                  <td>h</td>
                </tr>'''

            # UTM sem Az e d
            if modelo == 3:
                linha = '''<tr>
              <td>Vn</td>
              <td>En</td>
              <td>Nn</td>
              <td>hn</td>
            </tr>
            '''

                cabec = '''<tr>
                  <td colspan="4" rowspan="1">''' + self.tr('Synthetic deed description'.upper(), str2HTML('Memorial Sintético'.upper())) + '''[TITULO]</td>
                </tr>
                <tr>
                  <td colspan="1" rowspan="2">''' + self.tr('VERTEX', str2HTML('VÉRTICE')) + '''</td>
                  <td colspan="3" rowspan="1">''' + self.tr('COORDINATE', str2HTML('COORDENADA')) + '''</td>
                </tr>
                <tr>
                  <td>E</td>
                  <td>N</td>
                  <td>h</td>
                </tr>'''

            # GEO
            if modelo in (4,8):
                linha = '''<tr>
                  <td>Vn</td>
                  <td>lonn</td>
                  <td>latn</td>
                  <td>hn</td>
                  <td>Ln</td>
                  <td>Az_n</td>
                  <td>Dn</td>
                </tr>
                '''
                cabec = '''<tr>
                  <td colspan="7" rowspan="1">''' + self.tr('Synthetic deed description'.upper(), str2HTML('Memorial Sintético'.upper())) + '''[TITULO]</td>
                </tr>
                <tr>
                  <td colspan="1" rowspan="2">''' + self.tr('VERTEX', str2HTML('VÉRTICE')) + '''</td>
                  <td colspan="3" rowspan="1">''' + self.tr('COORDINATE', str2HTML('COORDENADA')) + '''</td>
                  <td colspan="1" rowspan="2">''' + self.tr('SIDE', str2HTML('LADO')) + '''</td>
                  <td colspan="1" rowspan="2">''' + self.tr('AZIMUTH', str2HTML('AZIMUTE')) + sufixo_azimute + '''</td>
                  <td colspan="1" rowspan="2">''' + self.tr('DISTANCE', str2HTML('DISTÂNCIA')) + '''<br>
                  ''' + rotulo_SGL + '(m)</td>' + '''
                </tr>
                <tr>
                  <td>longitude</td>
                  <td>latitude</td>
                  <td>h</td>
                </tr>'''

            # GEO sem Az e d
            if modelo in (5,9):
                linha = '''<tr>
                  <td>Vn</td>
                  <td>lonn</td>
                  <td>latn</td>
                  <td>hn</td>
                </tr>
                '''

                cabec = '''<tr>
                  <td colspan="4" rowspan="1">''' + self.tr('Synthetic deed description'.upper(), str2HTML('Memorial Sintético'.upper())) + '''[TITULO]</td>
                </tr>
                <tr>
                  <td colspan="1" rowspan="2">''' + self.tr('VERTEX', str2HTML('VÉRTICE')) + '''</td>
                  <td colspan="3" rowspan="1">''' + self.tr('COORDINATE', str2HTML('COORDENADA')) + '''</td>
                (m)</td>
                </tr>
                <tr>
                  <td>longitude</td>
                  <td>latitude</td>
                  <td>h</td>
                </tr>'''

            # UTM e GEO
            if modelo in (6,10):
                linha = '''<tr>
                  <td>Vn</td>
                  <td>lonn</td>
                  <td>latn</td>
                  <td>En</td>
                  <td>Nn</td>
                  <td>hn</td>
                  <td>Ln</td>
                  <td>Az_n</td>
                  <td>Dn</td>
                </tr>
                '''

                cabec = '''<tr>
                  <td colspan="9" rowspan="1">''' + self.tr('Synthetic deed description'.upper(), str2HTML('Memorial Sintético'.upper())) + '''[TITULO]</td>
                </tr>
                <tr>
                  <td colspan="1" rowspan="2">''' + self.tr('VERTEX', str2HTML('VÉRTICE')) + '''</td>
                  <td colspan="5" rowspan="1">''' + self.tr('COORDINATE', str2HTML('COORDENADA')) + '''</td>
                  <td colspan="1" rowspan="2">''' + self.tr('SIDE', str2HTML('LADO')) + '''</td>
                  <td colspan="1" rowspan="2">''' + self.tr('AZIMUTH', str2HTML('AZIMUTE')) + sufixo_azimute + '''</td>
                  <td colspan="1" rowspan="2">''' + self.tr('DISTANCE', str2HTML('DISTÂNCIA')) + '''<br>
                  ''' + rotulo_SGL + '(m)</td>' + '''
                </tr>
                <tr>
                  <td>longitude</td>
                  <td>latitude</td>
                  <td>E</td>
                  <td>N</td>
                  <td>h</td>
                </tr>'''

            # UTM e GEO sem Az e d
            if modelo in (7, 11):
                linha = '''<tr>
                  <td>Vn</td>
                  <td>lonn</td>
                  <td>latn</td>
                  <td>En</td>
                  <td>Nn</td>
                  <td>hn</td>
                </tr>
                '''

                cabec = '''<tr>
                  <td colspan="6" rowspan="1">''' + self.tr('Synthetic deed description'.upper(), str2HTML('Memorial Sintético'.upper())) + '''[TITULO]</td>
                </tr>
                <tr>
                  <td colspan="1" rowspan="2">''' + self.tr('VERTEX', str2HTML('VÉRTICE')) + '''</td>
                  <td colspan="5" rowspan="1">''' + self.tr('COORDINATE', str2HTML('COORDENADA')) + '''</td>
                </tr>
                <tr>
                  <td>longitude</td>
                  <td>latitude</td>
                  <td>E</td>
                  <td>N</td>
                  <td>h</td>
                </tr>'''

            LINHAS = ''
            if fim == -1 or fim > tam:
                fim = tam
            for k in range(ini-1,fim):
                linha0 = linha
                longitude = pnts_GEO[k+1][0].x()
                latitude = pnts_GEO[k+1][0].y()
                if modelo not in (8,9,10,11): # sem sufixo
                    longitude = self.tr(dd2dms(longitude,decimal_geo), dd2dms(longitude,decimal_geo).replace('.', ',')).replace('-','') + 'W' if longitude < 0 else 'E'
                    latitude = self.tr(dd2dms(latitude,decimal_geo), dd2dms(latitude,decimal_geo).replace('.', ',')).replace('-','') + 'S' if latitude < 0 else 'N'
                else:
                    longitude = self.tr(dd2dms(longitude,decimal_geo), dd2dms(longitude,decimal_geo).replace('.', ','))
                    latitude = self.tr(dd2dms(latitude,decimal_geo), dd2dms(latitude,decimal_geo).replace('.', ','))

                itens = {'Vn': pnts_UTM[k+1][2],
                            'En': self.tr(format_utm.format(pnts_UTM[k+1][0].x()), format_utm.format(pnts_UTM[k+1][0].x()).replace(',', 'X').replace('.', ',').replace('X', '.')),
                            'Nn': self.tr(format_utm.format(pnts_UTM[k+1][0].y()), format_utm.format(pnts_UTM[k+1][0].y()).replace(',', 'X').replace('.', ',').replace('X', '.')),
                            'hn': self.tr(format_utm.format(pnts_GEO[k+1][0].z()), format_utm.format(pnts_GEO[k+1][0].z()).replace(',', 'X').replace('.', ',').replace('X', '.')),
                            'lonn': longitude,
                            'latn': latitude,
                            'Ln': pnts_UTM[k+1][2] + '/' + pnts_UTM[1 if k+2 > tam else k+2][2],
                            'Az_n': self.tr(dd2dms(Az_lista[k],decimal_azim), dd2dms(Az_lista[k],decimal_azim).replace('.', ',')),
                            'Dn': self.tr(format_dist.format(Dist[k]), format_dist.format(Dist[k]).replace(',', 'X').replace('.', ',').replace('X', '.'))
                            }
                for item in itens:
                    linha0 = linha0.replace(item, itens[item])
                LINHAS += linha0
            resultado = texto.replace('[CABECALHO]', cabec).replace('[LINHAS]', LINHAS).replace('[TITULO]', str2HTML(titulo.upper())).replace('[FONTSIZE]', str(fontsize))


        output = self.parameterAsFileOutput(parameters, self.HTML, context)
        arq = open(output, 'w')
        arq.write(resultado)
        arq.close()

        feedback.pushInfo(self.tr('Operation completed successfully!', 'Operação finalizada com sucesso!'))
        feedback.pushInfo(self.tr('Leandro Franca - Cartographic Engineer', 'Leandro França - Eng Cart'))

        return {self.HTML: output}
