# -*- coding: utf-8 -*-

"""
***************************************************************************
    Doc_AreaPerimeter.py
    ---------------------
    Date                 : Jul 09
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
__date__ = 'Jul 09'
__copyright__ = '(C) 2020, Leandro França'

from PyQt5.QtCore import QCoreApplication
from qgis.core import (QgsProcessing,
                       QgsFeatureSink,
                       QgsProcessingException,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterFile,
                       QgsProcessingParameterString,
                       QgsProcessingParameterEnum,
                       QgsProcessingParameterNumber,
                       QgsProcessingParameterBoolean,
                       QgsProcessingParameterFeatureSink,
                       QgsProcessingParameterFileDestination,
                       QgsApplication,
                       QgsProject,
                       QgsPoint,
                       QgsCoordinateTransform,
                       QgsCoordinateReferenceSystem)
from math import atan, pi, sqrt, floor
import math
from lftools.geocapt.imgs import *
from lftools.translations.translate import translate
from lftools.geocapt.cartography import FusoHemisf, AzimuteDistanciaSGL, areaSGL, perimetroSGL
from lftools.geocapt.topogeo import str2HTML, dd2dms, azimute, validar_precisoes
import os
from qgis.PyQt.QtGui import QIcon

class AreaPerimterReport(QgsProcessingAlgorithm):

    PONTOLIMITE = 'PONTOLIMITE'
    AREAIMOVEL = 'AREAIMOVEL'
    HTML = 'HTML'
    LOGO = 'LOGO'
    SLOGAN = 'SLOGAN'
    DECIMAL = 'DECIMAL'
    PROJECTION = 'PROJECTION'
    CALC = 'CALC'

    LOC = QgsApplication.locale()[:2]

    def tr(self, *string):
        return translate(string, self.LOC)

    def createInstance(self):
        return AreaPerimterReport()

    def name(self):
        return 'areaperimeter'

    def displayName(self):
        return self.tr('Area and perimeter report', 'Planilha de área e perímetro')

    def group(self):
        return self.tr('Documents', 'Documentos')

    def groupId(self):
        return 'documents'

    def tags(self):
        return 'GeoOne,area,perimeter,descriptive,memorial,property,topography,survey,real,estate,georreferencing,plan,cadastral,cadastre,document'.split(',')

    def icon(self):
        return QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images/document.png'))

    figure = 'images/tutorial/doc_analytical_results.jpg'
    txt_en = 'This tool generates a Report for the Analytical Calculation of Area, Azimuths, Polygon Sides, UTM Projection and Geodetic Coordinates of a Property.'
    txt_pt = 'Esta gera o Relatório de Cálculo Analítico de Área, Azimutes, Lados, Coordenadas Planas e Geodésicas de um Imóvel.'

    def shortHelpString(self):
        social_BW = Imgs().social_BW
        footer = '''<div align="center">
                      <img src="'''+ os.path.join(os.path.dirname(os.path.dirname(__file__)), self.figure) +'''">
                      </div>
                      <div align="right">
                      <div>''' + self.tr('This tool works properly only with data in "TopoGeo" modeling.',
                                         'Esta ferramenta funciona adequadamente com os dados na modelagem "TopoGeo" ou "GeoRural".') + '''
                      </div>
                      <p align="right">
                      <b><a href="'''+ self.tr('https://www.researchgate.net/publication/356911797_TopoGeo_a_data_model_for_elaboration_of_cadastral_survey_plans_and_land_register_documents',
                      'https://geoone.com.br/ebooks/livro2/') + '''" target="_blank">'''+ self.tr('Click here for understanding this data model.',
                                    'Clique aqui para entender esse modelo de dados') +'</a><br><br>'+ self.tr('Author: Leandro Franca', 'Autor: Leandro França')+'''</b>
                      </p>'''+ social_BW + '''</div>
                    </div>'''
        return self.tr(self.txt_en, self.txt_pt) + footer

    def initAlgorithm(self, config=None):

        # 'INPUTS'
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.PONTOLIMITE,
                self.tr('Boundary Survey Points', 'Pontos de Limite'),
                types=[QgsProcessing.TypeVectorPoint]
            )
        )

        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.AREAIMOVEL,
                self.tr('Property Polygon', 'Área do Imóvel'),
                types=[QgsProcessing.TypeVectorPolygon]
            )
        )

        tipos = [self.tr('Project CRS', 'SRC do projeto'),
                 self.tr('Local Tangent Plane (LTP)', 'Sistema Geodésico Local (SGL)'),
                 self.tr('LTP, Puissant azimuth', 'SGL, azimute de Puissant'),
               ]

        self.addParameter(
            QgsProcessingParameterEnum(
                self.CALC,
                self.tr('Calculation of azimuths, distances and area',
                        'Cálculo de azimutes, distâncias e área'),
				options = tipos,
                defaultValue = 0
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
                defaultValue = self.tr('CARTOGRAPHY & SURVEYING', 'CARTOGRAFIA & AGRIMENSURA'),
                optional = True,
                multiLine = True
            )
        )

        self.addParameter(
            QgsProcessingParameterString(
                self.DECIMAL,
                self.tr('Decimal places', 'Casas decimais'),
                defaultValue = '2' # 2,1,2,2,2 - Precisões das coordenadas, azimutes, distâncias, área, perímetro
                )
            )

        self.addParameter(
            QgsProcessingParameterBoolean(
                self.PROJECTION,
                self.tr('Verify map projection', 'Verificar projeção do mapa'),
                defaultValue=True
            )
        )

        # 'OUTPUTS'
        self.addParameter(
            QgsProcessingParameterFileDestination(
                self.HTML,
                self.tr('Analytical Calculation Results', 'Resultados do Cálculo Analítico'),
                self.tr('HTML files (*.html)')
            )
        )


    def processAlgorithm(self, parameters, context, feedback):

        vertices = self.parameterAsSource(parameters,
                                                     self.PONTOLIMITE,
                                                     context)
        area = self.parameterAsSource(parameters,
                                                     self.AREAIMOVEL,
                                                     context)

        if vertices is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.PONTOLIMITE))
        if area is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.AREAIMOVEL))

        for feat in area.getFeatures():
            feat1 = feat
            geomGeo = feat1.geometry()
            break
        crsGeo = area.sourceCrs()

        calculo = self.parameterAsEnum(
            parameters,
            self.CALC,
            context
        )

        if calculo == 0:
            calculo_texto = self.tr('Calculation of azimuths, distances and area considering the Project CRS.',
                                     str2HTML('Cálculo de azimutes, distâncias e área no SRC do projeto.'))
        elif calculo == 1:
            calculo_texto = self.tr('Calculation azimuths, distances and area considering the Local Tangent Plane (LTP).',
                                     str2HTML('Cálculo de azimutes, distâncias e área no Sistema Geodésico Local (SGL).'))
        elif calculo == 2:
            calculo_texto = self.tr('Calculation of distances and area considering the Local Tangent Plane (LTP). Calculation of azimuths carried out according to the Inverse Geodetic Problem formulae according to Puissant.',
                                     str2HTML('Cálculo de distâncias e área no Sistema Geodésico Local (SGL). Cálculo dos azimutes realizado conforme formulário do Problema Geodésico Inverso segundo Puissant.'))


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


        decimal = self.parameterAsString(
            parameters,
            self.DECIMAL,
            context
        )
        # Validar dado de entrada
        # Precisões das coordenadas, azimutes, distâncias, área, perímetro
        decimal = decimal.replace(' ','').split(',')
        if not validar_precisoes(decimal,[1,5]):
            raise QgsProcessingException(self.invalidSourceError(parameters, self.DECIMAL))

        # Precisão da altitude
        try:
        	prec_h = int(decimal[0]) # teste se precisão das coordenadas é número inteiro
        except:
        	prec_h = round(10*(float(decimal[0]) - math.floor(float(decimal[0]))))
        	decimal[0] = str(int(float(decimal[0])))

        format_utm = '{:,.Xf}'.replace('X', decimal[0])
        format_h = '{:,.Xf}'.replace('X', str(prec_h))

        if len(decimal) == 1:
        	decimal_geo = int(decimal[0]) + 2
        	format_dist = '{:,.Xf}'.replace('X', decimal[0])
        	decimal_area = int(decimal[0])
        	format_perim =  '{:,.Xf}'.replace('X', decimal[0])
        	decimal_azim = 1
        elif len(decimal) == 5:
        	decimal_geo = int(decimal[0])
        	decimal_azim = int(decimal[1])
        	format_dist = '{:,.Xf}'.replace('X', decimal[2])
        	decimal_area = int(decimal[3])
        	format_perim =  '{:,.Xf}'.replace('X', decimal[4])

        format_area_ha = '{:,.Xf}'.replace('X', str(decimal_area+2))
        format_area = '{:,.Xf}'.replace('X', str(decimal_area))


        projecao = self.parameterAsBool(
            parameters,
            self.PROJECTION,
            context
        )

        # Pegando o SRC do Projeto
        SRC = QgsProject.instance().crs().description()

        # Verificando o SRC do Projeto
        if QgsProject.instance().crs().isGeographic():
            raise QgsProcessingException(self.tr('The Project CRS must be projected!', 'O SRC do Projeto deve ser Projetado!'))
        feedback.pushInfo(self.tr('Project CRS is {}.', 'SRC do Projeto é {}.').format(SRC))

        # Transformar Coordenadas de Geográficas para o sistema UTM
        coordinateTransformer = QgsCoordinateTransform()
        coordinateTransformer.setDestinationCrs(QgsProject.instance().crs())
        coordinateTransformer.setSourceCrs(area.sourceCrs())

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

        # Validando dados de entrada
        modeloBD = None
        def TestModelo(campos_vertices, campos_area):
            sentinela = True
            for campo in campos_vertices:
                if campo not in [field.name() for field in vertices.fields()]:
                    sentinela = False
                    break
            for campo in campos_area:
                if campo not in [field.name() for field in area.fields()]:
                    sentinela = False
                    break
            return sentinela

        # Teste para o modelo de BD
        campos_vertices = ['type', 'code', 'sequence']
        campos_area = ['property', 'registry', 'transcript', 'owner', 'county', 'state', 'survey_date']
        if TestModelo(campos_vertices, campos_area):
            modeloBD = 'TG' # TopoGeo
            codigo, sequencia, tipo = ('code', 'sequence', 'type')
            feedback.pushInfo(self.tr('Database in the TopoGeo model...', 'Banco de dados no modelo TopoGeo...' ))

        campos_vertices = ['tipo_verti', 'vertice', 'indice']
        campos_area = ['denominacao', 'sncr', 'matricula', 'nome', 'municipio', 'uf', 'data', 'resp_tec', 'reg_prof']
        if TestModelo(campos_vertices, campos_area):
            modeloBD = 'GR' # GeoRural
            codigo, sequencia, tipo = ('vertice', 'indice', 'tipo_verti')
            feedback.pushInfo('Banco de dados no modelo GeoRural...' )

        if not modeloBD:
            raise QgsProcessingException(self.tr('Check that your layers have the correct field names for the TopoGeo model! More information: https://bit.ly/3FDNQGC', 'Verifique se suas camadas estão com os nomes dos campos corretos para o modelo de banco de dados (TopoGeo ou GeoRural)! Mais informações: https://geoone.com.br/ebooks/livro2/'))

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
                raise QgsProcessingException(self.tr('Check that your layer "limit_point_p" has the correct field names for the TopoGeo model! More information: https://bit.ly/3FDNQGC', 'Verifique se sua camada "Ponto Limite" está com os nomes dos campos corretos para o modelo TopoGeo! Mais informações: https://geoone.com.br/ebooks/livro2/'))
            if not codigo_item or codigo_item in ['', ' ']:
                raise QgsProcessingException(self.tr('The code attribute must be filled in for all features!', 'O atributo código deve ser preenchido para todas as feições!'))
        ordem_comp.sort()
        if ordem_list != ordem_comp:
            raise QgsProcessingException(self.tr('The point sequence field must be filled in correctly!', 'O campo de sequência dos pontos deve preenchido corretamente!'))

        # area_imovel
        Fields = area.fields()
        fieldnames = ['property', 'county', 'state'] if modeloBD == 'TG' else ['denominacao', 'municipio', 'uf']
        for fieldname in fieldnames:
            att = feat1[fieldname]
            if not att or att in ['', ' ']:
                raise QgsProcessingException(self.tr('All attributes of the class "property_polygon" must be filled!', 'Todos os atributos da classe "area_imovel" devem ser preenchidos!'))


        INICIO = '''<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
<html>
<head>
  <meta content="text/html; charset=ISO-8859-1"
 http-equiv="content-type">
  <title>'''+ str2HTML(self.tr('Area and Perimeter Calculation', 'Cálculo de Área e Perímetro')) + '''</title>
  <link rel = "icon" href = "https://github.com/LEOXINGU/lftools/blob/main/images/lftools.png?raw=true" type = "image/x-icon">
</head>
<body>
<div style="text-align: center;"><span style="font-weight: bold;"><br>
<img height="80" src="data:image/'''+ LOGO + '''">
<br>'''+ str2HTML(SLOGAN) + '''</span><br style="font-weight: bold;">
<br></div>
<div style="text-align: center;"><big><big><span
 style="font-weight: bold;">'''+ self.tr('Analytical Calculation of Area, Azimuths, Sides, Flat and Geodetic Coordinates',
                                         str2HTML('Cálculo Analítico de Área, Azimutes, Lados, Coordenadas Planas e Geodésicas')) + '''</span><br
 style="font-weight: bold;">
</big></big>
<div style="text-align: left;"><br>
<span style="font-weight: bold;">'''+ str2HTML(self.tr('Property','Imóvel')) + ''':</span>
[IMOVEL]<br>
<span style="font-weight: bold;">'''+ str2HTML(self.tr('County-State','Município-UF')) + ''':</span>
[MUNICIPIO] - [UF]<br style="font-weight: bold;">
<span style="font-weight: bold;">''' + self.tr('GRS','SGR') + ''':</span>
SIRGAS2000<br>
<span style="font-weight: bold;">''' + str2HTML(self.tr('Projection', 'Projeção')) + ''':</span>
[UTM] <br><br>
</div>
</div>
<table style="text-align: center; width: 100%;" border="1"
 cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td style="text-align: center; font-weight: bold;">''' + str2HTML(self.tr('Station', 'Estação') ) + '''</td>
      <td style="text-align: center; font-weight: bold;">''' + str2HTML(self.tr('Forward', 'Vante') ) + '''</td>
      <td style="text-align: center; font-weight: bold;">''' + str2HTML(self.tr('East (m)', 'Leste (m)') ) + '''</td>
      <td style="text-align: center; font-weight: bold;">''' + str2HTML(self.tr('North (m)', 'Norte (m)') ) + '''</td>
      <td style="text-align: center; font-weight: bold;">''' + str2HTML(self.tr('Azimuth', 'Azimute') ) + '''</td>
      <td style="text-align: center; font-weight: bold;">''' + str2HTML(self.tr('Distance (m)', 'Distância (m)') ) + '''</td>
      <td style="text-align: center; font-weight: bold;">''' + str2HTML(self.tr('Longitude', 'Longitude') ) + '''</td>
      <td style="text-align: center; font-weight: bold;">''' + str2HTML(self.tr('Latitude', 'Latitude') ) + '''</td>
    </tr>
    '''

        linha = '''<tr>
      <td>[EST1]</td>
      <td>[EST2]</td>
      <td>[E]</td>
      <td>[N]</td>
      <td>[AZ]</td>
      <td>[D]</td>
      <td>[LON]</td>
      <td>[LAT]</td>
    </tr>
  '''

        FIM = '''</tbody>
</table>
<br>
<span style="font-weight: bold;">'''+ str2HTML(self.tr('Perimeter', 'Perímetro')) + ''':</span>
&nbsp;[PERIMETRO] m<br>
<span style="font-weight: bold;">''' + str2HTML(self.tr('Total Area', 'Área Total')) + ''':</span>
[AREA] m&sup2; / [AREA_HA] ha
<br>
<span style="font-weight: bold;">''' + str2HTML(self.tr('Observation', 'Observação')) + ''':</span>
[CALCULO]
</body>
</html>
'''

        # Inserindo dados iniciais do levantamento
        property = 'property' if modeloBD == 'TG' else 'denominacao'
        state = 'state' if modeloBD == 'TG' else 'uf'
        county = 'county' if modeloBD == 'TG' else 'municipio'
        try:
            itens = {'[IMOVEL]': str2HTML(feat1[property]),
                        '[UF]': feat1[state],
                        '[UTM]': (SRC.split('/')[-1]).replace('zone', 'fuso'),
                        '[MUNICIPIO]': str2HTML(feat1[county]),
                        }
            for item in itens:
                    INICIO = INICIO.replace(item, itens[item])

            # Inserindo dados finais do levantamento
            geom1 = feat1.geometry()
            if calculo == 0: # Projetadas (Ex: UTM)
                geom1.transform(coordinateTransformer)
                area1 = geom1.area()
                perimeter1 = geom1.length()
            else: # SGL
                area1 = areaSGL(geom1, crsGeo)
                perimeter1 = perimetroSGL(geom1, crsGeo)

            itens = {   '[AREA]': self.tr(format_area.format(area1), format_area.format(area1).replace(',', 'X').replace('.', ',').replace('X', '.')),
                        '[AREA_HA]': self.tr(format_area_ha.format(area1/1e4), format_area_ha.format(area1/1e4).replace(',', 'X').replace('.', ',').replace('X', '.')),
                        '[PERIMETRO]': self.tr(format_perim.format(perimeter1), format_perim.format(perimeter1).replace(',', 'X').replace('.', ',').replace('X', '.')),
                        '[CALCULO]': calculo_texto
                        }
            for item in itens:
                    FIM = FIM.replace(item, itens[item])
        except:
            raise QgsProcessingException(self.tr('Check that your layer "property_area_a" has the correct field names for the TopoGeo model! More information: https://bit.ly/3FDNQGC', 'Verifique se sua camada "Área do imóvel" está com os nomes dos campos corretos para o modelo TopoGeo! Mais informações: https://geoone.com.br/ebooks/livro2/'))

        LINHAS = INICIO

        # Pegar pontos
        pnts = {}
        for feat in vertices.getFeatures():
            geom = feat.geometry()
            if modeloBD == 'GR':
                sequence = feat['indice']
                type = feat['tipo_verti']
                code = feat['vertice']
            else:
                sequence = feat['sequence']
                type = feat['type']
                code = feat['code']
            if geom.isMultipart():
                pnts[sequence] = [coordinateTransformer.transform(geom.asMultiPoint()[0]), type, code, (geom.constGet()[0].x(), geom.constGet()[0].y(), geom.constGet()[0].z())]
            else:
                pnts[sequence] = [coordinateTransformer.transform(geom.asPoint()), type, code, (geom.constGet().x(), geom.constGet().y(), geom.constGet().z())]

        # Cálculo dos Azimutes e Distâncias
        tam = len(pnts)
        Az_lista, Dist = [], []
        if calculo == 0: # Projetadas (Ex: UTM)
            for k in range(tam):
                pntA = pnts[k+1][0]
                pntB = pnts[max((k+2)%(tam+1),1)][0]
                Az_lista += [(180/pi)*azimute(pntA, pntB)[0]]
                Dist += [sqrt((pntA.x() - pntB.x())**2 + (pntA.y() - pntB.y())**2)]
        elif calculo == 1: # SGL
            for k in range(tam):
                pntA = QgsPoint(pnts[k+1][3][0], pnts[k+1][3][1], pnts[k+1][3][2])
                ind =  max((k+2)%(tam+1),1)
                pntB = QgsPoint(pnts[ind][3][0], pnts[ind][3][1], pnts[ind][3][2])
                Az, dist = AzimuteDistanciaSGL(pntA, pntB, geomGeo, crsGeo, 'SGL')
                Az_lista += [Az]
                Dist += [dist]
        elif calculo == 2: # SGL e Puissant
            for k in range(tam):
                pntA = QgsPoint(pnts[k+1][3][0], pnts[k+1][3][1], pnts[k+1][3][2])
                ind =  max((k+2)%(tam+1),1)
                pntB = QgsPoint(pnts[ind][3][0], pnts[ind][3][1], pnts[ind][3][2])
                Az, dist = AzimuteDistanciaSGL(pntA, pntB, geomGeo, crsGeo, 'puissant')
                Az_lista += [Az]
                Dist += [dist]

        for k in range(tam):
            linha0 = linha
            itens = {
                  '[EST1]': pnts[k+1][2],
                  '[EST2]': pnts[1 if k+2 > tam else k+2][2],
                  '[E]': self.tr(format_utm.format(pnts[k+1][0].x()), format_utm.format(pnts[k+1][0].x()).replace(',', 'X').replace('.', ',').replace('X', '.')),
                  '[N]': self.tr(format_utm.format(pnts[k+1][0].y()), format_utm.format(pnts[k+1][0].y()).replace(',', 'X').replace('.', ',').replace('X', '.')),
                  '[AZ]': str2HTML(self.tr(dd2dms(Az_lista[k],decimal_azim), dd2dms(Az_lista[k],decimal_azim).replace('.', ','))),
                  '[D]': format_dist.format(Dist[k]).replace(',', 'X').replace('.', ',').replace('X', '.'),
                  '[LON]': str2HTML(self.tr(dd2dms(pnts[k+1][3][0],decimal_geo), dd2dms(pnts[k+1][3][0],decimal_geo).replace('.', ','))),
                  '[LAT]': str2HTML(self.tr(dd2dms(pnts[k+1][3][1],decimal_geo), dd2dms(pnts[k+1][3][1],decimal_geo).replace('.', ','))),
                        }
            for item in itens:
                linha0 = linha0.replace(item, itens[item])

            LINHAS += linha0

        LINHAS += FIM

        # Check for cancelation
        if feedback.isCanceled():
            return {}

        output = self.parameterAsFileOutput(parameters, self.HTML, context)
        arq = open(output, 'w')
        arq.write(LINHAS)
        arq.close()

        feedback.pushInfo(self.tr('Operation completed successfully!', 'Operação finalizada com sucesso!'))
        feedback.pushInfo(self.tr('Leandro França - Cartographic Engineer', 'Leandro França - Eng Cart'))

        return {self.HTML: output}
