# -*- coding: utf-8 -*-

"""
Survey_closedPolygonal.py
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
__date__ = '2019-10-06'
__copyright__ = '(C) 2019, Leandro França'

from PyQt5.QtCore import QCoreApplication, QVariant
from qgis.core import *
import processing
from numpy import sin, cos, modf, radians, sqrt, floor
from lftools.geocapt.imgs import Imgs
from lftools.geocapt.topogeo import *
import os
from qgis.PyQt.QtGui import QIcon


class ClosedPolygonal(QgsProcessingAlgorithm):

    POINT = 'POINT'
    AZIMUTH_0 = 'AZIMUTH_0'
    ANGLES = 'ANGLES'
    DISTANCES = 'DISTANCES'
    CRS = 'CRS'
    POINTS = 'POINTS'
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
        return ClosedPolygonal()

    def name(self):
        return 'planimetry'

    def displayName(self):
        return self.tr('Closed polygonal', 'Poligonal fechada')

    def group(self):
        return self.tr('Survey', 'Agrimensura')

    def groupId(self):
        return 'survey'

    def tags(self):
        return self.tr('survey,agrimensura,closed,traverse,polygonal,adjustment,total,station,angle,least square').split(',')

    def icon(self):
        return QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images/total_station.png'))

    txt_en = 'Calculates the adjusted coordinates from angles and horizontal distances of a Closed Polygonal.'
    txt_pt = 'Cálculo das coordenadas ajustadas a partir de medições de ângulos e distâncias de uma poligonal fechada.'
    figure = 'images/tutorial/survey_closed_polygonal.jpg'

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

    def initAlgorithm(self, config=None):

        self.addParameter(
            QgsProcessingParameterPoint(
                self.POINT,
                self.tr('Origin Point Coordinates', 'Coordenadas do ponto inicial'),
                defaultValue = QgsPointXY(1000.0, 1000.0)
            )
        )

        self.addParameter(
            QgsProcessingParameterString(
                self.AZIMUTH_0,
                self.tr('Azimuth (origin)', 'Azimute inicial'),
                defaultValue = '''211°58'50.0"'''
            )
        )

        self.addParameter(
            QgsProcessingParameterString(
                self.DISTANCES,
                self.tr('List of Horizontal Distances', 'Lista de Distâncias Horizontais'),
                defaultValue = '147.058, 110.404, 72.372, 186.583, 105.451',
                multiLine = True
            )
        )

        self.addParameter(
            QgsProcessingParameterString(
                self.ANGLES,
                self.tr('List of Angles','Lista de Ângulos'),
                defaultValue = '''112°00'15.0", 75°24'35.0", 202°05'05.0", 56°50'10.0", 93°40'20.0" ''',
                multiLine = True
            )
        )

        self.addParameter(
            QgsProcessingParameterCrs(
                self.CRS,
                self.tr('CRS', 'SRC'),
                'ProjectCrs'
            )
        )

        # OUTPUT
        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.POINTS,
                self.tr('Adjusted Points', 'Pontos ajustados')
            )
        )

        self.addParameter(
            QgsProcessingParameterFileDestination(
                'HTML',
                self.tr('Adjustment Report', 'Relatório de Ajustamento'),
                self.tr('HTML files (*.html)')
            )
        )

    def processAlgorithm(self, parameters, context, feedback):

        ponto = self.parameterAsPoint(
            parameters,
            self.POINT,
            context
        )

        E_0 = ponto.x()
        N_0 = ponto.y()

        Az_0 = self.parameterAsString(
            parameters,
            self.AZIMUTH_0,
            context
        )

        distances = self.parameterAsString(
            parameters,
            self.DISTANCES,
            context
        )

        angles = self.parameterAsString(
            parameters,
            self.ANGLES,
            context
        )

        distances = String2NumberList(distances)
        angles = String2StringList(angles)
        if len(distances) !=  len(angles):
            raise QgsProcessingException(self.tr('The number of measured distances must be equal to the number of angles!', 'O número de distâncias medidas deve ser igual ao número de ângulos!'))
        tam = len(distances)

        html_output = self.parameterAsFileOutput(
            parameters,
            self.HTML,
            context
        )

        CRS = self.parameterAsCrs(
            parameters,
            self.CRS,
            context
        )

        if CRS.isGeographic():
            raise QgsProcessingException(self.tr('The output CRS must be Projected!', 'O SRC da camada de saída deve ser Projetado!'))

        readings = {}
        SomaAng = 0

        for k in range(tam):
            SomaAng += dms2dd(angles[k])
            estacao = k+1
            readings[estacao] = {'fwd': k+2 if k+1 <= tam else 1 ,
                                 'angle': dms2dd(angles[k]) ,
                                 'dist':distances[k]}

        # Erro de Fechamento Angular (ângulos internos)
        n = tam
        E_alfa = SomaAng - (n-2)*180

        # Compensação do Erro de Fechamento Angular
        C_alfa = - E_alfa/n
        SomaAng_Comp = 0
        for est in readings:
            readings[est]['angle_comp'] = readings[est]['angle'] + C_alfa
            SomaAng_Comp += readings[est]['angle'] + C_alfa

        # Cálculo dos Azimutes e Deltas
        Az_0 = dms2dd(Az_0)
        Az = Az_0
        soma_delta_x = 0
        soma_delta_y = 0
        perimetro = 0
        for est in readings:
            if est !=1:
                Az = readings[est]['angle_comp'] + Az + 180
            readings[est]['Az'] = Az%360
            delta_x = readings[est]['dist']*cos(radians(90-Az))
            delta_y = readings[est]['dist']*sin(radians(90-Az))
            readings[est]['delta_x'] = delta_x
            readings[est]['delta_y'] = delta_y
            soma_delta_x += delta_x
            soma_delta_y += delta_y
            perimetro += readings[est]['dist']

        E_linear = sqrt(soma_delta_x**2 + soma_delta_y**2)
        Precisao = '1/'+ str(round(perimetro/E_linear))

        # Compensação Linear
        for est in readings:
            readings[est]['delta_x_comp'] = readings[est]['delta_x'] - soma_delta_x*readings[est]['dist']/perimetro
            readings[est]['delta_y_comp'] = readings[est]['delta_y'] - soma_delta_y*readings[est]['dist']/perimetro

        # Coordenadas Finais
        E = E_0
        N = N_0
        for est in readings:
            if est ==1:
                readings[est]['E'] = E
                readings[est]['N'] = N
            else:
                readings[est]['E'] = readings[est-1]['E'] + readings[est-1]['delta_x_comp']
                readings[est]['N'] = readings[est-1]['N'] + readings[est-1]['delta_y_comp']

        # Relatório
        texto_inicial = '''<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
<html>
<head>
  <meta content="text/html; charset=ISO-8859-1"
 http-equiv="content-type">
  <title>'''+self.tr('Closed Traverse', 'Poligonal Fechada')+'''</title>
</head>
<body
 style="color: rgb(0, 0, 0); background-color: rgb(255, 255, 204);"
 alink="#000099" link="#000099" vlink="#990099">
<p class="MsoNormal" style="text-align: center;"
 align="center"><b><span
 style="font-size: 12pt; line-height: 107%;"><o:p></o:p></span></b><span
 style="font-weight: bold;">'''+self.tr('CLOSED TRAVERSE', 'POLIGONAL FECHADA')+'''</span></p>
<p class="MsoNormal" style="text-align: center;"
 align="center"><span style="font-style: italic;">'''+self.tr('Analytical Calculation', str2HTML('Cálculo Analítico'))+'''</span></p>
<p class="MsoNormal" style="text-align: center;"
 align="center"><b><u>'''+self.tr('REPORT', str2HTML('RELATÓRIO'))+'''<o:p></o:p></u></b></p>
<div>
<div align="center">
<table style="height: 210px; width: 1064.4px;" cellpadding="2"
 cellspacing="0">
  <tbody>
    <tr valign="top">
      <td
 style="border: 1pt solid rgb(0, 0, 0); padding: 0.05cm; width: 61px;">
      <p align="center">'''+self.tr('Station', str2HTML('Estação'))+'''</p>
      </td>
      <td
 style="border-style: solid solid solid none; border-color: rgb(0, 0, 0) rgb(0, 0, 0) rgb(0, 0, 0) -moz-use-text-color; border-width: 1pt 1pt 1pt medium; padding: 0.05cm 0.05cm 0.05cm 0cm; width: 58px;">
      <p align="center">'''+self.tr('Forward', str2HTML('Vante'))+'''</p>
      </td>
      <td
 style="border-style: solid solid solid none; border-color: rgb(0, 0, 0) rgb(0, 0, 0) rgb(0, 0, 0) -moz-use-text-color; border-width: 1pt 1pt 1pt medium; padding: 0.05cm 0.05cm 0.05cm 0cm; width: 108px;">
      <p align="center">'''+self.tr('Angle', str2HTML('Ângulo'))+'''</p>
      </td>
      <td
 style="border-style: solid solid solid none; border-color: rgb(0, 0, 0) rgb(0, 0, 0) rgb(0, 0, 0) -moz-use-text-color; border-width: 1pt 1pt 1pt medium; padding: 0.05cm 0.05cm 0.05cm 0cm; width: 80px;">
      <p align="center">'''+self.tr('Distance', str2HTML('Distância'))+'''</p>
      </td>
      <td
 style="border-style: solid solid solid none; border-color: rgb(0, 0, 0) rgb(0, 0, 0) rgb(0, 0, 0) -moz-use-text-color; border-width: 1pt 1pt 1pt medium; padding: 0.05cm 0.05cm 0.05cm 0cm; width: 108px;">
      <p align="center">'''+self.tr('Corrected Angle', str2HTML('Ângulo Corrigido'))+'''</p>
      </td>
      <td
 style="border-style: solid solid solid none; border-color: rgb(0, 0, 0) rgb(0, 0, 0) rgb(0, 0, 0) -moz-use-text-color; border-width: 1pt 1pt 1pt medium; padding: 0.05cm 0.05cm 0.05cm 0cm; width: 98px;">
      <p align="center">'''+self.tr('Azimuth', str2HTML('Azimute'))+'''</p>
      </td>
      <td
 style="border-style: solid solid solid none; border-color: rgb(0, 0, 0) rgb(0, 0, 0) rgb(0, 0, 0) -moz-use-text-color; border-width: 1pt 1pt 1pt medium; padding: 0.05cm 0.05cm 0.05cm 0cm; width: 78px;">
      <p align="center">dE</p>
      </td>
      <td
 style="border-style: solid solid solid none; border-color: rgb(0, 0, 0) rgb(0, 0, 0) rgb(0, 0, 0) -moz-use-text-color; border-width: 1pt 1pt 1pt medium; padding: 0.05cm 0.05cm 0.05cm 0cm; width: 79px;">
      <p align="center">dN</p>
      </td>
      <td
 style="border-style: solid solid solid none; border-color: rgb(0, 0, 0) rgb(0, 0, 0) rgb(0, 0, 0) -moz-use-text-color; border-width: 1pt 1pt 1pt medium; padding: 0.05cm 0.05cm 0.05cm 0cm; width: 91px;">
      <p align="center">Corrected&nbsp;<br>
dE</p>
      </td>
      <td
 style="border-style: solid solid solid none; border-color: rgb(0, 0, 0) rgb(0, 0, 0) rgb(0, 0, 0) -moz-use-text-color; border-width: 1pt 1pt 1pt medium; padding: 0.05cm 0.05cm 0.05cm 0cm; width: 89px;">
      <p align="center">Corrected&nbsp;<br>
dN</p>
      </td>
      <td
 style="border-style: solid solid solid none; border-color: rgb(0, 0, 0) rgb(0, 0, 0) rgb(0, 0, 0) -moz-use-text-color; border-width: 1pt 1pt 1pt medium; padding: 0.05cm 0.05cm 0.05cm 0cm; width: 97px;">
      <p align="center">'''+self.tr('Final E', str2HTML('E final'))+'''</p>
      </td>
      <td
 style="border-style: solid solid solid none; border-color: rgb(0, 0, 0) rgb(0, 0, 0) rgb(0, 0, 0) -moz-use-text-color; border-width: 1pt 1pt 1pt medium; padding: 0.05cm 0.05cm 0.05cm 0cm; width: 85px;">
      <p align="center">'''+self.tr('Final N', str2HTML('N final'))+'''</p>
      </td>
    </tr>
'''
        texto_tabela ='''<tr valign="top">
      <td
 style="border-style: none solid solid; border-color: -moz-use-text-color rgb(0, 0, 0) rgb(0, 0, 0); border-width: medium 1pt 1pt; padding: 0cm 0.05cm 0.05cm; width: 61px;">
      <p align="center">[Sn]</p>
      </td>
      <td
 style="border-style: none solid solid none; border-color: -moz-use-text-color rgb(0, 0, 0) rgb(0, 0, 0) -moz-use-text-color; border-width: medium 1pt 1pt medium; padding: 0cm 0.05cm 0.05cm 0cm; width: 58px;">
      <p align="center">[fSn]</p>
      </td>
      <td
 style="border-style: none solid solid none; border-color: -moz-use-text-color rgb(0, 0, 0) rgb(0, 0, 0) -moz-use-text-color; border-width: medium 1pt 1pt medium; padding: 0cm 0.05cm 0.05cm 0cm; width: 100px;">
      <p align="center">[An]</p>
      </td>
      <td
 style="border-style: none solid solid none; border-color: -moz-use-text-color rgb(0, 0, 0) rgb(0, 0, 0) -moz-use-text-color; border-width: medium 1pt 1pt medium; padding: 0cm 0.05cm 0.05cm 0cm; width: 80px;">
      <p align="center">[d]</p>
      </td>
      <td
 style="border-style: none solid solid none; border-color: -moz-use-text-color rgb(0, 0, 0) rgb(0, 0, 0) -moz-use-text-color; border-width: medium 1pt 1pt medium; padding: 0cm 0.05cm 0.05cm 0cm; width: 96px;">
      <p align="center">[cA]</p>
      </td>
      <td
 style="border-style: none solid solid none; border-color: -moz-use-text-color rgb(0, 0, 0) rgb(0, 0, 0) -moz-use-text-color; border-width: medium 1pt 1pt medium; padding: 0cm 0.05cm 0.05cm 0cm; width: 98px;">
      <p align="center">[Az]</p>
      </td>
      <td
 style="border-style: none solid solid none; border-color: -moz-use-text-color rgb(0, 0, 0) rgb(0, 0, 0) -moz-use-text-color; border-width: medium 1pt 1pt medium; padding: 0cm 0.05cm 0.05cm 0cm; width: 78px;">
      <p align="center">[dE]</p>
      </td>
      <td
 style="border-style: none solid solid none; border-color: -moz-use-text-color rgb(0, 0, 0) rgb(0, 0, 0) -moz-use-text-color; border-width: medium 1pt 1pt medium; padding: 0cm 0.05cm 0.05cm 0cm; width: 79px;">
      <p align="center">[dN]</p>
      </td>
      <td
 style="border-style: none solid solid none; border-color: -moz-use-text-color rgb(0, 0, 0) rgb(0, 0, 0) -moz-use-text-color; border-width: medium 1pt 1pt medium; padding: 0cm 0.05cm 0.05cm 0cm; width: 91px;">
      <p align="center">[cdE]</p>
      </td>
      <td
 style="border-style: none solid solid none; border-color: -moz-use-text-color rgb(0, 0, 0) rgb(0, 0, 0) -moz-use-text-color; border-width: medium 1pt 1pt medium; padding: 0cm 0.05cm 0.05cm 0cm; width: 89px;">
      <p align="center">[cdN]</p>
      </td>
      <td
 style="border-style: none solid solid none; border-color: -moz-use-text-color rgb(0, 0, 0) rgb(0, 0, 0) -moz-use-text-color; border-width: medium 1pt 1pt medium; padding: 0cm 0.05cm 0.05cm 0cm; width: 97px;">
      <p align="center">[fE]</p>
      </td>
      <td
 style="border-style: none solid solid none; border-color: -moz-use-text-color rgb(0, 0, 0) rgb(0, 0, 0) -moz-use-text-color; border-width: medium 1pt 1pt medium; padding: 0cm 0.05cm 0.05cm 0cm; width: 85px;">
      <p align="center">[fN]</p>
      </td>
    </tr>
'''
        texto_final ='''<tr valign="top">
      <td colspan="1"
 style="border: medium none ; padding: 0cm; width: 61px;">
      <p style="text-align: right;"></p>
      </td>
      <td style="text-align: right; width: 58px;">Sum:</td>
      <td style="padding: 0cm; width: 100px;">
      <p align="center">[SumAn]&nbsp;</p>
      </td>
      <td style="border: medium none ; padding: 0cm; width: 80px;">
      <p align="center">&nbsp;[SumD]</p>
      </td>
      <td style="border: medium none ; padding: 0cm; width: 96px;">
      <p align="center">[SumCAng]&nbsp;</p>
      </td>
      <td style="border: medium none ; padding: 0cm; width: 98px;">
      <p align="center">&nbsp;</p>
      </td>
      <td style="border: medium none ; padding: 0cm; width: 78px;">
      <p align="center">&nbsp;[SumdE]</p>
      </td>
      <td style="border: medium none ; padding: 0cm; width: 79px;">
      <p align="center">&nbsp;[SumdN]</p>
      </td>
      <td style="border: medium none ; padding: 0cm; width: 91px;">
      <p align="center">0&nbsp;</p>
      </td>
      <td style="border: medium none ; padding: 0cm; width: 89px;">
      <p align="center">&nbsp;0&nbsp;</p>
      </td>
      <td style="border: medium none ; padding: 0cm; width: 97px;">
      <p align="center">&nbsp;</p>
      </td>
      <td style="border: medium none ; padding: 0cm; width: 85px;">
      <p align="center">&nbsp;</p>
      </td>
    </tr>
  </tbody>
</table>
</div>
<p lang="en-US">'''+self.tr('Angular closure error', str2HTML('Erro de fechamento angular'))+''': [Ace]</p>
<p lang="en-US">'''+self.tr('Linear closure error', str2HTML('Erro de fechamento linear'))+''': [Lce]</p>
<p lang="en-US">'''+self.tr('Linear relative error', str2HTML('Erro linear relativo'))+''': [Lre]</p>
<p class="MsoNormal" style="text-align: left;"
 align="left"><br>
<i><span
 style="font-size: 10pt; line-height: 100%; color: rgb(127, 127, 127);">''' + self.tr(str2HTML('*The unit of measurement of the adjusted coordinates is the same as the input coordinates.'), str2HTML('*A unidade de medida das coordenadas ajustadas é a mesma da coordenadas de entrada.')) + '''<o:p></o:p></span></i></p>
</div>
<footer">
<p class="MsoNormal" style="margin-bottom: 0.0001pt; text-align: right;" align="right"><b>''' + self.tr('Leandro Franca', str2HTML('Leandro França')) + '''
</br>''' + self.tr('Cartographic Engineer', str2HTML('Eng. Cartógrafo')) + '''<o:p></o:p></b></p>
</br>
<div align="right">'''+ Imgs().social_table_color + '''
</div>
<o:p></o:p></b></p>
</footer>
</body>
</html>
'''

        texto = texto_inicial

        # Alimentando tabela
        for est in readings:
            tableRowN = texto_tabela
            itens  = {
                         '[Sn]' : str(est),
                         '[fSn]': str(readings[est]['fwd']),
                         '[An]': str2HTML(self.tr(dd2dms(readings[est]['angle'],1), dd2dms(readings[est]['angle'],1).replace('.', ','))),
                         '[d]': self.tr('{:,.3f}'.format(readings[est]['dist']), '{:,.3f}'.format(readings[est]['dist']).replace(',', 'X').replace('.', ',').replace('X', '.')),
                         '[cA]': str2HTML(self.tr(dd2dms(readings[est]['angle_comp'],1), dd2dms(readings[est]['angle_comp'],1).replace('.', ','))),
                         '[Az]': str2HTML(self.tr(dd2dms(readings[est]['Az'],1), dd2dms(readings[est]['Az'],1).replace('.', ','))),
                         '[dE]': self.tr('{:,.3f}'.format(readings[est]['delta_x']), '{:,.3f}'.format(readings[est]['delta_x']).replace(',', 'X').replace('.', ',').replace('X', '.')),
                         '[dN]': self.tr('{:,.3f}'.format(readings[est]['delta_y']), '{:,.3f}'.format(readings[est]['delta_y']).replace(',', 'X').replace('.', ',').replace('X', '.')),
                         '[cdE]': self.tr('{:,.3f}'.format(readings[est]['delta_x_comp']), '{:,.3f}'.format(readings[est]['delta_x_comp']).replace(',', 'X').replace('.', ',').replace('X', '.')),
                         '[cdN]': self.tr('{:,.3f}'.format(readings[est]['delta_y_comp']), '{:,.3f}'.format(readings[est]['delta_y_comp']).replace(',', 'X').replace('.', ',').replace('X', '.')),
                         '[fE]': self.tr('{:,.3f}'.format(readings[est]['E']), '{:,.3f}'.format(readings[est]['E']).replace(',', 'X').replace('.', ',').replace('X', '.')),
                         '[fN]': self.tr('{:,.3f}'.format(readings[est]['N']), '{:,.3f}'.format(readings[est]['N']).replace(',', 'X').replace('.', ',').replace('X', '.'))
                         }
            for item in itens:
                tableRowN = tableRowN.replace(item, itens[item])
            texto += tableRowN

        # Dados finais
        itens  = {
                     '[SumAn]' : str2HTML(self.tr(dd2dms(SomaAng,1), dd2dms(SomaAng,1).replace('.', ','))),
                     '[SumD]': self.tr('{:,.3f}'.format(perimetro), '{:,.3f}'.format(perimetro).replace(',', 'X').replace('.', ',').replace('X', '.')),
                     '[SumCAng]': str2HTML(self.tr(dd2dms(SomaAng_Comp,1), dd2dms(SomaAng_Comp,1).replace('.', ','))),
                     '[SumdE]': self.tr('{:,.3f}'.format(soma_delta_x), '{:,.3f}'.format(soma_delta_x).replace(',', 'X').replace('.', ',').replace('X', '.')),
                     '[SumdN]': self.tr('{:,.3f}'.format(soma_delta_y), '{:,.3f}'.format(soma_delta_y).replace(',', 'X').replace('.', ',').replace('X', '.')),
                     '[Ace]': str2HTML(self.tr(dd2dms(E_alfa,1), dd2dms(E_alfa,1).replace('.', ','))),
                     '[Lce]': self.tr('{:,.3f}'.format(E_linear), '{:,.3f}'.format(E_linear).replace(',', 'X').replace('.', ',').replace('X', '.')),
                     '[Lre]': Precisao
                     }
        for item in itens:
                texto_final = texto_final.replace(item, itens[item])

        texto += texto_final

        # Exportar HTML
        arq = open(html_output, 'w')
        arq.write(texto)
        arq.close()

        # Camada de Saída
        GeomType = QgsWkbTypes.Point
        Fields = QgsFields()
        itens  = {
                     'estation' : QVariant.Int,
                     'forward':  QVariant.Int,
                     'angle': QVariant.String,
                     'distance':  QVariant.Double,
                     'corrAng': QVariant.String,
                     'azimuth': QVariant.String,
                     'deltaE': QVariant.Double,
                     'deltaN': QVariant.Double,
                     'CdeltaE': QVariant.Double,
                     'CdeltaN': QVariant.Double,
                     'E': QVariant.Double,
                     'N': QVariant.Double,
                     }
        for item in itens:
            Fields.append(QgsField(item, itens[item]))

        (sink, dest_id) = self.parameterAsSink(
            parameters,
            self.POINTS,
            context,
            Fields,
            GeomType,
            CRS
        )

        if sink is None:
            raise QgsProcessingException(self.invalidSinkError(parameters, self.POINTS))

        # Criar pontos ajustados
        feat = QgsFeature(Fields)
        for est in readings:
            itens  = {
                         'estation' : str(est),
                         'forward': str(readings[est]['fwd']),
                         'angle': dd2dms(readings[est]['angle'],1),
                         'distance': str(round(readings[est]['dist'],4)),
                         'corrAng': dd2dms(readings[est]['angle_comp'],1),
                         'azimuth': dd2dms(readings[est]['Az'],1),
                         'deltaE': str(round(readings[est]['delta_x'],4)),
                         'deltaN': str(round(readings[est]['delta_y'],4)),
                         'CdeltaE': str(round(readings[est]['delta_x_comp'],4)),
                         'CdeltaN': str(round(readings[est]['delta_y_comp'],4)),
                         'E': str(round(readings[est]['E'],4)),
                         'N': str(round(readings[est]['N'],4))
                         }
            for item in itens:
                feat[item] = itens[item]
            geom = QgsGeometry.fromPointXY(QgsPointXY(readings[est]['E'], readings[est]['N']))
            feat.setGeometry(geom)
            sink.addFeature(feat, QgsFeatureSink.FastInsert)
            if feedback.isCanceled():
                break

        feedback.pushInfo(self.tr('Operation completed successfully!', 'Operação finalizada com sucesso!'))
        feedback.pushInfo(self.tr('Leandro Franca - Cartographic Engineer', 'Leandro França - Eng Cart'))

        return {self.POINTS: dest_id,
                    self.HTML: html_output}
