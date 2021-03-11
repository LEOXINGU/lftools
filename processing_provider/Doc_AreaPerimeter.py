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
                       QgsProcessingParameterFeatureSink,
                       QgsProcessingParameterFileDestination,
                       QgsApplication,
                       QgsProject,
                       QgsCoordinateTransform,
                       QgsCoordinateReferenceSystem)
from math import atan, pi, sqrt, floor
import math
from lftools.geocapt.imgs import Imgs, lftools_logo
from lftools.geocapt.topogeo import str2HTML, dd2dms, azimute
import os
from qgis.PyQt.QtGui import QIcon

class AreaPerimterReport(QgsProcessingAlgorithm):

    PONTOLIMITE = 'PONTOLIMITE'
    AREAIMOVEL = 'AREAIMOVEL'
    HTML = 'HTML'

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
        return AreaPerimterReport()

    def name(self):
        return 'areaperimeter'

    def displayName(self):
        return self.tr('Area and Perimeter Report', 'Planilha de Área e Perímetro')

    def group(self):
        return self.tr('Documents', 'Documentos')

    def groupId(self):
        return 'documents'

    def tags(self):
        return self.tr('area,perimeter,descriptive,memorial,property,topography,survey,real,estate,georreferencing,plan,cadastral,cadastre,documnt').split(',')

    def icon(self):
        return QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images/document.png'))

    def shortHelpString(self):
        txt_en = 'This tool generate the Report for the Analytical Calculation of Area, Azimuths, Sides, UTM Projected and Geodetic Coordinates of a Property.'
        txt_pt = 'Esta gera o Relatório de Cálculo Analítico de Área, Azimutes, Lados, Coordenadas Planas e Geodésicas de um Imóvel.'
        social_BW = Imgs().social_BW
        footer = '''<div align="center">
                      <img src="'''+ os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images/tutorial/doc_analytical_results.jpg') +'''">
                      </div>
                      <div align="right">
                      <div>''' + self.tr('This tool works properly only with data in "topogeo" modeling.',
                                         'Esta ferramenta funciona adequadamente com os dados na modelagem "topogeo".') + '''
                      </div>
                      <p align="right">
                      <b><a href="https://www.researchgate.net/publication/346925730_PROPOSICAO_METODOLOGICA_COM_EMPREGO_DE_SOFTWARE_LIVRE_PARA_A_ELABORACAO_DE_DOCUMENTOS_DE_LEVANTAMENTO_TOPOGRAFICO_DE_IMOVEIS_DA_UNIAO_Methodological_proposition_with_the_use_of_free_software_for_the_p" target="_blank">'''+self.tr('Click here for more informations!',
                                    'Clique aqui para saber mais sobre essa modelagem!') +'</a><br><br>'+ self.tr('Author: Leandro Franca', 'Autor: Leandro França')+'''</b>
                      </p>'''+ social_BW + '''</div>
                    </div>'''
        return self.tr(txt_en, txt_pt) + footer

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

        # Validando dados de entrada
        # ponto_limite
        ordem_list = list(range(1,vertices.featureCount()+1))
        ordem_comp = []
        for feat in vertices.getFeatures():
            ordem_comp += [feat['ordem']]
            codigo_item = feat['codigo']
            if not codigo_item or codigo_item in ['', ' ']:
                raise QgsProcessingException(self.tr('The code attribute must be filled in for all features!', 'O atributo código deve ser preenchido para todas as feições!'))
        ordem_comp.sort()
        if ordem_list != ordem_comp:
            raise QgsProcessingException(self.tr('The point sequence field must be filled in correctly!', 'O campo de sequência dos pontos deve preenchido corretamente!'))
        # area_imovel
        Fields = area.fields()
        fieldnames = [field.name() for field in Fields]
        for fieldname in fieldnames:
            att = feat1[fieldname]
            if not att or att in ['', ' ']:
                raise QgsProcessingException(self.tr('All attributes of the class "property_polygon" must be filled!', 'Todos os atributos da classe "area_imovel" devem ser preenchidos!'))


        INICIO = '''<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
<html>
<head>
  <meta content="text/html; charset=ISO-8859-1"
 http-equiv="content-type">
  <title>'''+ self.tr('Area and Perimeter Calculation', str2HTML('Cálculo de Área e Perímetro')) + '''</title>
</head>
<body>
<div style="text-align: center;"><span style="font-weight: bold;"><br>
<img src="data:image/png;base64,'''+ lftools_logo + '''">
<br>'''+ self.tr(str2HTML('CARTOGRAPHY & SURVEYING'), str2HTML('CARTOGRAFIA & AGRIMENSURA')) + '''</span><br style="font-weight: bold;">
<br></div>
<div style="text-align: center;"><big><big><span
 style="font-weight: bold;">'''+ self.tr('Analytical Calculation of Area, Azimuths, Sides, Flat and Geodetic Coordinates',
                                         str2HTML('Cálculo Analítico de Área, Azimutes, Lados, Coordenadas Planas e Geodésicas')) + '''</span><br
 style="font-weight: bold;">
</big></big>
<div style="text-align: left;"><br>
<span style="font-weight: bold;">'''+ self.tr('Property',str2HTML('Imóvel')) + ''':</span>
[IMOVEL]<br>
<span style="font-weight: bold;">'''+ self.tr('County-State',str2HTML('Município-UF')) + ''':</span>
[MUNICIPIO] - [UF]<br style="font-weight: bold;">
<span style="font-weight: bold;">''' + self.tr('GRS','SGR') + ''':</span>
SIRGAS2000<br>
<span style="font-weight: bold;">''' + self.tr('Projection', str2HTML('Projeção')) + ''':</span>
[UTM] <br>
</div>
</div>
<table style="text-align: center; width: 100%;" border="1"
 cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td style="text-align: center; font-weight: bold;">''' + self.tr('Station', str2HTML('Estação') ) + '''</td>
      <td style="text-align: center; font-weight: bold;">''' + self.tr('Forward', str2HTML('Vante') ) + '''</td>
      <td style="text-align: center; font-weight: bold;">''' + self.tr('East (m)', str2HTML('Leste (m)') ) + '''</td>
      <td style="text-align: center; font-weight: bold;">''' + self.tr('North (m)', str2HTML('Norte (m)') ) + '''</td>
      <td style="text-align: center; font-weight: bold;">''' + self.tr('Azimuth', str2HTML('Azimute') ) + '''</td>
      <td style="text-align: center; font-weight: bold;">''' + self.tr('Distance (m)', str2HTML('Distância (m)') ) + '''</td>
      <td style="text-align: center; font-weight: bold;">''' + self.tr('Longitude', str2HTML('Longitude') ) + '''</td>
      <td style="text-align: center; font-weight: bold;">''' + self.tr('Latitude', str2HTML('Latitude') ) + '''</td>
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
<span style="font-weight: bold;">'''+ self.tr('Perimeter',str2HTML('Perímetro')) + ''':</span>
&nbsp;[PERIMETRO] m<br>
<span style="font-weight: bold;">''' + self.tr('Total Area', str2HTML('Área Total')) + ''':</span>
[AREA] m&sup2; / [AREA_HA] ha
</body>
</html>
'''

        # Inserindo dados iniciais do levantamento
        itens = {'[IMOVEL]': str2HTML(feat1['imóvel']),
                    '[UF]': feat1['UF'],
                    '[UTM]': (SRC.split('/')[-1]).replace('zone', 'fuso'),
                    '[MUNICIPIO]': str2HTML(feat1['município']),
                    }
        for item in itens:
                INICIO = INICIO.replace(item, itens[item])

        # Inserindo dados finais do levantamento
        itens = {   '[AREA]': self.tr('{:,.2f}'.format(feat1['area']), '{:,.2f}'.format(feat1['area']).replace(',', 'X').replace('.', ',').replace('X', '.')),
                    '[AREA_HA]': self.tr('{:,.2f}'.format(feat1['area']/1e4), '{:,.2f}'.format(feat1['area']/1e4).replace(',', 'X').replace('.', ',').replace('X', '.')),
                    '[PERIMETRO]': self.tr('{:,.2f}'.format(feat1['perimetro']), '{:,.2f}'.format(feat1['perimetro']).replace(',', 'X').replace('.', ',').replace('X', '.'))
                    }
        for item in itens:
                FIM = FIM.replace(item, itens[item])

        LINHAS = INICIO

        pnts_UTM = {}
        for feat in vertices.getFeatures():
            pnt = feat.geometry().asMultiPoint()[0]
            pnts_UTM[feat['ordem']] = [coordinateTransformer.transform(pnt), feat['codigo'], pnt]

        # Cálculo dos Azimutes e Distâncias
        tam = len(pnts_UTM)
        Az_lista, Dist = [], []
        for k in range(tam):
            pntA = pnts_UTM[k+1][0]
            pntB = pnts_UTM[1 if k+2 > tam else k+2][0]
            Az_lista += [(180/pi)*azimute(pntA, pntB)[0]]
            Dist += [sqrt((pntA.x() - pntB.x())**2 + (pntA.y() - pntB.y())**2)]

        for k in range(tam):
            linha0 = linha
            itens = {
                  '[EST1]': pnts_UTM[k+1][1],
                  '[EST2]': pnts_UTM[1 if k+2 > tam else k+2][1],
                  '[E]': self.tr('{:,.2f}'.format(pnts_UTM[k+1][0].x()), '{:,.2f}'.format(pnts_UTM[k+1][0].x()).replace(',', 'X').replace('.', ',').replace('X', '.')),
                  '[N]': self.tr('{:,.2f}'.format(pnts_UTM[k+1][0].y()), '{:,.2f}'.format(pnts_UTM[k+1][0].y()).replace(',', 'X').replace('.', ',').replace('X', '.')),
                  '[AZ]': str2HTML(self.tr(dd2dms(Az_lista[k],1), dd2dms(Az_lista[k],1).replace('.', ','))),
                  '[D]': '{:,.2f}'.format(Dist[k]).replace(',', 'X').replace('.', ',').replace('X', '.'),
                  '[LON]': str2HTML(self.tr(dd2dms(pnts_UTM[k+1][2].x(),4), dd2dms(pnts_UTM[k+1][2].x(),4).replace('.', ','))),
                  '[LAT]': str2HTML(self.tr(dd2dms(pnts_UTM[k+1][2].y(),4), dd2dms(pnts_UTM[k+1][2].y(),4).replace('.', ','))),
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
