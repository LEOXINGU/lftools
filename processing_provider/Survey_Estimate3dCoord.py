# -*- coding: utf-8 -*-

"""
Survey_Estimate3dCoord.py
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
__date__ = '2020-02-07'
__copyright__ = '(C) 2020, Leandro França'

from PyQt5.QtCore import QCoreApplication, QVariant
from qgis.core import *
import qgis.utils
from numpy import radians, array, sin, cos, sqrt, matrix, zeros, floor, identity, diag
from numpy.linalg import pinv, norm
from lftools.geocapt.imgs import Imgs
from lftools.geocapt.topogeo import str2HTML, String2CoordList, String2StringList, dms2dd
import os
from qgis.PyQt.QtGui import QIcon

class Estimate3dCoord(QgsProcessingAlgorithm):

    COC = 'COC'
    AZIMUTH = 'AZIMUTH'
    ZENITH = 'ZENITH'
    OUTPUT = 'OUTPUT'
    WEIGHT = 'WEIGHT'
    OPENOUTPUT = 'OPENOUTPUT'
    HTML = 'HTML'
    OPEN = 'OPEN'

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
        return Estimate3dCoord()

    def name(self):
        return 'estimate3dcoord'

    def displayName(self):
        return self.tr('Estimate 3D coordinates', 'Estimar coordenadas 3D')

    def group(self):
        return self.tr('Survey', 'Agrimensura')

    def groupId(self):
        return 'survey'

    def tags(self):
        return self.tr('survey,agrimensura,3D,coordinate,azimuth,zenith,angle,least square,minimum distantce,adjustment,slant').split(',')

    def icon(self):
        return QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images/total_station.png'))

    txt_en = 'This tool calculates the coordinates (X, Y, Z) of a point from azimuth and zenith angle measurements observed from two or more stations with known coordinates using the Foward Intersection Method adjusted by the Minimum Distances.'
    txt_pt = 'Esta ferramenta calcula as coordenadas (X,Y,Z) de um ponto a partir de medições de azimute e ângulo zenital observados de duas ou mais estações de coordenadas conhecidas utilizando o Método de Interseção à Vante ajustado pelas Distâncias Mínimas.'
    figure = 'images/tutorial/survey_3D_coord.jpg'

    def shortHelpString(self):
        social_BW = Imgs().social_BW
        nota_en = '''Notes: Data collected in the discipline of <i>Geodetic Surveys</i> in the Graduate Program at UFPE, in field work coordinated by <b>Prof. Dr. Andrea de Seixas</b>.
For more information on the methodology used, please read the article at the link below:'''
        nota_pt = '''Notas: Dados coletados na disciplina de <i>Levantamentos Geodésicos</i> no programa de Pós-Graduação da UFPE, em trabalho de campo coordenado pela <b>Profa. Dra. Andrea de Seixas</b>.
Para mais informações sobre a metodologia utilizada, por favor leia o artigo no link abaixo:'''
        footer = '''<div align="center">
                      <img src="'''+ os.path.join(os.path.dirname(os.path.dirname(__file__)), self.figure) +'''">
                      </div>
                      <div align="right">
                      <div>''' + self.tr(nota_en, nota_pt) + '''
                      </div>
                      <p align="right">
                      <b><a href="https://www.researchgate.net/publication/352817150_OPTIMIZED_DETERMINATION_OF_3D_COORDINATES_IN_THE_SURVEY_OF_INACCESSIBLE_POINTS_OF_BUILDINGS_-_EXAMPLE_OF_APPLICATION_IMPLEMENTED_IN_FREE_SOFTWARE_Determinacao_otimizada_de_coordenadas_3D_no_levantamen" target="_blank">'''+self.tr('FRANCA, L.; DE SEIXAS, A.; GAMA, L.; MORAES, J. Optimized determination of 3D coordinates in the survey of  inaccessible  points  of  buildings - example  of  application implemented  in  free  software.  Bulletin  of Geodetic  Sciences.  27(2): e2021017, 2021. ') + '''</b>
                                    ''' +'</a><br><b>'+ self.tr('Author: Leandro Franca', 'Autor: Leandro França')+'''</b>
                      </p>'''+ social_BW + '''</div>
                    </div>'''
        return self.tr(self.txt_en, self.txt_pt) + footer

    def initAlgorithm(self, config=None):

        # 'INPUTS'
        self.addParameter(
            QgsProcessingParameterString(
                self.COC,
                self.tr('Coordinates of Optical Centers', 'Coordenadas dos Centros Ópticos'),
                defaultValue = '149867.058, 249817.768, 1.825; 149988.309, 249782.867, 1.962; 150055.018, 249757.128, 1.346; 150085.600, 249877.691, 1.559',
                multiLine = True
            )
        )

        self.addParameter(
            QgsProcessingParameterString(
                self.AZIMUTH,
                self.tr('Azimuths', 'Azimutes'),
                defaultValue = '''46°10'06.37”, 359°12'12.21”, 338°32'59.40”, 298°46'22.93”''',
                multiLine = True
            )
        )

        self.addParameter(
            QgsProcessingParameterString(
                self.ZENITH,
                self.tr('Zenith Angles', 'Ângulos Zenitais'),
                defaultValue = '''72°24'22.25”, 70°43'01.75", 74°17'54.17", 65°04'27.25"''',
                multiLine = True
            )
        )

        self.addParameter(
            QgsProcessingParameterBoolean(
                self.WEIGHT,
                self.tr('Use Weight Matrix (W)', 'Usar Matrix Peso (P)'),
                defaultValue = False
            )
        )

        # 'OUTPUT'
        self.addParameter(
            QgsProcessingParameterFileDestination(
                self.OUTPUT,
                self.tr('Adjusted 3D Coordinates', 'Coordenadas 3D Ajustadas'),
                fileFilter = '.csv'
            )
        )

        self.addParameter(
            QgsProcessingParameterFileDestination(
                'HTML',
                self.tr('Adjustment Report', 'Relatório de Ajustamento'),
                self.tr('HTML files (*.html)')
            )
        )

        self.addParameter(
            QgsProcessingParameterBoolean(
                self.OPEN,
                self.tr('Open output file after executing the algorithm', 'Abrir arquivo de saída com coordenadas 3D'),
                defaultValue= True
            )
        )

    def CosDir(self, Az, Z):
        k = sin(Z)*sin(Az)
        m = sin(Z)*cos(Az)
        n = cos(Z)
        return array([[k],[m],[n]])

    def processAlgorithm(self, parameters, context, feedback):

        COs = self.parameterAsString(
            parameters,
            self.COC,
            context
        )

        Azimutes = self.parameterAsString(
            parameters,
            self.AZIMUTH,
            context
        )

        ÂngulosZenitais = self.parameterAsString(
            parameters,
            self.ZENITH,
            context
        )

        usar_peso = self.parameterAsBool(
            parameters,
            self.WEIGHT,
            context
        )

        abrir_arquivo = self.parameterAsBool(
            parameters,
            self.OPENOUTPUT,
            context
        )

        output = self.parameterAsFileOutput(
            parameters,
            self.OUTPUT,
            context
        )
        if output[-3:] != 'csv':
            output += '.csv'

        html_output = self.parameterAsFileOutput(
            parameters,
            self.HTML,
            context
        )

        # Pontos
        Coords = String2CoordList(COs)

        # Azimutes (radianos)
        Az = []
        for item in String2StringList(Azimutes):
            Az += [dms2dd(item)]
        Az = radians(array(Az))

        # Ângulos Zenitais (radianos)
        Z = []
        for item in String2StringList(ÂngulosZenitais):
            Z += [dms2dd(item)]
        Z = radians(array(Z))

        # Validação dos dados de entrada
        if not (len(Coords) == len(Az) and len(Az) == len(Z)):
            raise QgsProcessingException(self.tr('Wrong number of parameters!', 'Número de parâmetros errado!'))
        else:
            n = len(Coords)
        # não deve haver valores nulos
        # ângulos entre 0 e 360 graus

        # Montagem do Vetor L
        L = []
        for k in range(len(Coords)):
            L+= [[Coords[k][0]], [Coords[k][1]], [Coords[k][2]]]
        L = array(L)

        # Montagem da Matriz A
        e = 3*n
        p = 3 + n
        A = matrix(zeros([e, p]))
        for k in range(n):
            A[3*k:3*k+3, 0:3] = identity(3)
            A[3*k:3*k+3, 3+k] = -1*self.CosDir(Az[k], Z[k])

        # Ajustamento MMQ
        X = pinv(A.T*A)*A.T*L
        V = A*X - L
        sigma2 = (V.T*V)/(e-p)
        SigmaX = sigma2[0,0]*pinv(A.T*A)

        if usar_peso:
            Ponto = array(X[0:3, :].T)[0]
            d = []
            for coord in Coords:
                dist = norm(array(coord)-Ponto)
                d += [1/dist, 1/dist, 1/dist]
            P = diag(d)
            X = pinv(A.T*P*A)*A.T*P*L
            V = A*X - L
            sigma2 = (V.T*P*V)/(e-p)
            SigmaX = sigma2[0,0]*pinv(A.T*P*A)

        VAR = str(round(sigma2[0,0],5))
        x = round(float(X[0, 0]),3)
        y = round(float(X[1, 0]),3)
        z = round(float(X[2, 0]),3)
        s_x = round(float(sqrt(SigmaX[0, 0])),3)
        s_y = round(float(sqrt(SigmaX[1, 1])),3)
        s_z = round(float(sqrt(SigmaX[2, 2])),3)

        # Slant Range
        slant_range = []
        s_t = []
        for k in range(len(Coords)):
            slant_range += [round(float(X[k+3, 0]),3)]
            s_t += [round(float(sqrt(SigmaX[k+3, k+3])),3)]

        # Resultados
        arq = open(output, 'w')
        arq.write('X,Y,Z,'+ self.tr('type', 'tipo') + '\n')
        arq.write('{},{},{},'.format(x,y,z) + self.tr('Adjusted 3D Coordinates', 'Coordenadas 3D Ajustadas') + '\n')
        for k in range(len(Coords)):
            arq.write('{},{},{},{}'.format(Coords[k][0],Coords[k][1],Coords[k][2], self.tr('Station', 'Estacao') + ' ' + str(k+1) ) + '\n')
        arq.close()

        texto = '''<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
<html>
<head>

  <meta content="text/html; charset=ISO-8859-1" http-equiv="content-type">
  <title>''' + self.tr('Estimate 3D Coordinates', str2HTML('Estimação de Coordenadas 3D')) + '''</title>
</head>
<body style="color: rgb(0, 0, 0); background-color: rgb(255, 255, 204);" alink="#000099" link="#000099" vlink="#990099">
<p class="MsoNormal" style="text-align: center;" align="center"><b><span style="font-size: 12pt; line-height: 107%;">''' + self.tr('ESTIMATE 3D COORDINATES', 'ESTIMA&Ccedil;&Atilde;O DE COORDENADAS 3D') + '''<o:p></o:p></span></b></p>
<p class="MsoNormal" style="text-align: center;" align="center"><i>''' + self.tr('Minimum Distance Method', 'M&eacute;todo das Dist&acirc;ncias M&iacute;nimas') + '''</i></p>
<p class="MsoNormal" style="text-align: center;" align="center"><b><u>''' + self.tr('REPORT','RELAT&Oacute;RIO') + '''<o:p></o:p></u></b></p>
<div>
<table style="text-align: center; width: 100%;" border="1" cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td width="50%"><b>''' + self.tr('Inputs', 'Dados de Entrada') + '''</b></td>
      <td width="50%"><b>'''+ self.tr('Adjustment','Ajustamento') + '''</b></td>
    </tr>
    <tr>
      <td style="text-align:  center;">
      <p class="MsoNormal" style="text-align: center;" align="center"><span style="font-style: italic;">''' + self.tr('Coordinates of the Optical Centers','Coordenadas dos Centros &Oacute;pticos')+ '''</span><o:p></o:p></p>
      <div align="center">
      <table class="MsoTableGrid" style="border: medium none ; border-collapse: collapse;" border="1" cellpadding="0" cellspacing="0">
        <tbody>
        <tr style="">
            <td
 style="border: 1pt solid windowtext; padding: 0cm 5.4pt; width: 39.3pt;"
 valign="top" width="52">
            <p class="MsoNormal"
 style="margin-bottom: 0.0001pt; text-align: center; line-height: normal;"
 align="center"><i>'''+self.tr('Station', str2HTML('Estação')) + '''</i><o:p></o:p></p>
            </td>
            <td
 style="border-style: solid solid solid none; border-color: windowtext windowtext windowtext -moz-use-text-color; border-width: 1pt 1pt 1pt medium; padding: 0cm 5.4pt; width: 46.05pt;"
 valign="top" width="61">
            <p class="MsoNormal"
 style="margin-bottom: 0.0001pt; text-align: center; line-height: normal;"
 align="center"><i>X</i><o:p></o:p></p>
            </td>
            <td
 style="border-style: solid solid solid none; border-color: windowtext windowtext windowtext -moz-use-text-color; border-width: 1pt 1pt 1pt medium; padding: 0cm 5.4pt; width: 46.05pt;"
 valign="top" width="61">
            <p class="MsoNormal"
 style="margin-bottom: 0.0001pt; text-align: center; line-height: normal;"
 align="center"><i>Y</i><o:p></o:p></p>
            </td>
            <td
 style="border-style: solid solid solid none; border-color: windowtext windowtext windowtext -moz-use-text-color; border-width: 1pt 1pt 1pt medium; padding: 0cm 5.4pt; width: 46.05pt;"
 valign="top" width="61">
            <p class="MsoNormal"
 style="margin-bottom: 0.0001pt; text-align: center; line-height: normal;"
 align="center"><i>Z</i><o:p></o:p></p>
            </td>
          </tr>
          [tabela 1]
        </tbody>
      </table>
      </div>
      <p class="MsoNormal" style="text-align: center;" align="center"><span style="font-style: italic;"></span></p>
      <p class="MsoNormal" style="text-align: center;" align="center"><span style="font-style: italic;">''' + self.tr('Azimuths','Azimutes') + '''</span><o:p></o:p></p>
      <div align="center">
      <table class="MsoTableGrid" style="border: medium none ; border-collapse: collapse;" border="0" cellpadding="0" cellspacing="0">
        <tbody>
          [tabela 2]
        </tbody>
      </table>
      </div>
      <p class="MsoNormal" style="text-align: center;" align="center"><span style="font-style: italic;"></span></p>
      <p class="MsoNormal" style="text-align: center;" align="center"><span style="font-style: italic;">''' + self.tr('Zenith Angles', '&Acirc;ngulos Zenitais') + '''</span><o:p></o:p></p>
      <div align="center">
      <table class="MsoTableGrid" style="border: medium none ; border-collapse: collapse;" border="0" cellpadding="0" cellspacing="0">
        <tbody>
          [tabela 3]
        </tbody>
      </table>
        <p class="MsoNormal" style="text-align: center;" align="center"><span style="font-style: italic;">''' + self.tr('Weight Matrix'+str2HTML('*'),'Matriz Peso'+str2HTML('*')) + ''': [PESO]</span><o:p></o:p></p>
      </div>
      </td>
      <td>
      <p class="MsoNormal" style="text-align: center;" align="center"><o:p>&nbsp;</o:p><span style="font-style: italic;">'''+ self.tr('Residuals (V)', 'Res&iacute;duos (V)') + '''</span><o:p></o:p></p>
      <div align="center">
      <table class="MsoTableGrid" style="border: medium none ; border-collapse: collapse;" border="1" cellpadding="0" cellspacing="0">
        <tbody>
        <tr style="">
            <td
 style="border: 1pt solid windowtext; padding: 0cm 5.4pt; width: 39.3pt;"
 valign="top" width="52">
            <p class="MsoNormal"
 style="margin-bottom: 0.0001pt; text-align: center; line-height: normal;"
 align="center"><i>'''+self.tr('Station', str2HTML('Estação')) + '''</i><o:p></o:p></p>
            </td>
            <td
 style="border-style: solid solid solid none; border-color: windowtext windowtext windowtext -moz-use-text-color; border-width: 1pt 1pt 1pt medium; padding: 0cm 5.4pt; width: 46.05pt;"
 valign="top" width="61">
            <p class="MsoNormal"
 style="margin-bottom: 0.0001pt; text-align: center; line-height: normal;"
 align="center"><i>V_X</i><o:p></o:p></p>
            </td>
            <td
 style="border-style: solid solid solid none; border-color: windowtext windowtext windowtext -moz-use-text-color; border-width: 1pt 1pt 1pt medium; padding: 0cm 5.4pt; width: 46.05pt;"
 valign="top" width="61">
            <p class="MsoNormal"
 style="margin-bottom: 0.0001pt; text-align: center; line-height: normal;"
 align="center"><i>V_Y</i><o:p></o:p></p>
            </td>
            <td
 style="border-style: solid solid solid none; border-color: windowtext windowtext windowtext -moz-use-text-color; border-width: 1pt 1pt 1pt medium; padding: 0cm 5.4pt; width: 46.05pt;"
 valign="top" width="61">
            <p class="MsoNormal"
 style="margin-bottom: 0.0001pt; text-align: center; line-height: normal;"
 align="center"><i>V_Z</i><o:p></o:p></p>
            </td>
          </tr>
          [tabela 4]
        </tbody>
      </table>
      </div>
      <p class="MsoNormal" style="text-align: center;" align="center"><span style="font-style: italic;">''' + self.tr('Posteriori Variance', 'Vari&acirc;ncia a posteriori') + ''' &nbsp;</span>[VAR]<o:p></o:p></p>
      <p class="MsoNormal" style="text-align: center;" align="center"><span style="font-style: italic;">''' + self.tr(str2HTML('Adjusted Coordinates, Slant Ranges and Precisions**'), str2HTML('Coordenas Ajustados, Distâncias e Precis&otilde;es**')) + '''</span><o:p></o:p></p>
      <div align="center">
      <table class="MsoTableGrid" style="border: medium none ; width: 100.7pt; border-collapse: collapse;" border="1" cellpadding="0" cellspacing="0" width="134">
        <tbody>
          <tr style="">
            <td style="border: 1pt solid windowtext; padding: 0cm 5.4pt; width: 38.9pt;" valign="top" width="52">
            <p class="MsoNormal" style="margin-bottom: 0.0001pt; text-align: center; line-height: normal;" align="center">X<o:p></o:p></p>
            </td>
            <td style="border-style: solid solid solid none; border-color: windowtext windowtext windowtext -moz-use-text-color; border-width: 1pt 1pt 1pt medium; padding: 0cm 5.4pt; width: 28.75pt;" valign="top" width="38">
            <p class="MsoNormal" style="margin-bottom: 0.0001pt; text-align: center; line-height: normal;" align="center">[X]<o:p></o:p></p>
            </td>
            <td style="border-style: solid solid solid none; border-color: windowtext windowtext windowtext -moz-use-text-color; border-width: 1pt 1pt 1pt medium; padding: 0cm 5.4pt; width: 33.05pt;" valign="top" width="44">
            <p class="MsoNormal" style="margin-bottom: 0.0001pt; text-align: center; line-height: normal;" align="center">[sX]<o:p></o:p></p>
            </td>
          </tr>
          <tr style="">
            <td style="border-style: none solid solid; border-color: -moz-use-text-color windowtext windowtext; border-width: medium 1pt 1pt; padding: 0cm 5.4pt; width: 38.9pt;" valign="top" width="52">
            <p class="MsoNormal" style="margin-bottom: 0.0001pt; text-align: center; line-height: normal;" align="center">Y<o:p></o:p></p>
            </td>
            <td style="border-style: none solid solid none; border-color: -moz-use-text-color windowtext windowtext -moz-use-text-color; border-width: medium 1pt 1pt medium; padding: 0cm 5.4pt; width: 28.75pt;" valign="top" width="38">
            <p class="MsoNormal" style="margin-bottom: 0.0001pt; text-align: center; line-height: normal;" align="center">[Y]<o:p></o:p></p>
            </td>
            <td style="border-style: none solid solid none; border-color: -moz-use-text-color windowtext windowtext -moz-use-text-color; border-width: medium 1pt 1pt medium; padding: 0cm 5.4pt; width: 33.05pt;" valign="top" width="44">
            <p class="MsoNormal" style="margin-bottom: 0.0001pt; text-align: center; line-height: normal;" align="center">[sY]<o:p></o:p></p>
            </td>
          </tr>
          <tr style="">
            <td style="border-style: none solid solid; border-color: -moz-use-text-color windowtext windowtext; border-width: medium 1pt 1pt; padding: 0cm 5.4pt; width: 38.9pt;" valign="top" width="52">
            <p class="MsoNormal" style="margin-bottom: 0.0001pt; text-align: center; line-height: normal;" align="center">Z<o:p></o:p></p>
            </td>
            <td style="border-style: none solid solid none; border-color: -moz-use-text-color windowtext windowtext -moz-use-text-color; border-width: medium 1pt 1pt medium; padding: 0cm 5.4pt; width: 28.75pt;" valign="top" width="38">
            <p class="MsoNormal" style="margin-bottom: 0.0001pt; text-align: center; line-height: normal;" align="center">[Z]<o:p></o:p></p>
            </td>
            <td style="border-style: none solid solid none; border-color: -moz-use-text-color windowtext windowtext -moz-use-text-color; border-width: medium 1pt 1pt medium; padding: 0cm 5.4pt; width: 33.05pt;" valign="top" width="44">
            <p class="MsoNormal" style="margin-bottom: 0.0001pt; text-align: center; line-height: normal;" align="center">[sZ]<o:p></o:p></p>
            </td>
          </tr>
        [SLANT_RANGE]
        </tbody>
      </table>
      </br>
      </div>
      </td>
    </tr>
  </tbody>
</table>
<p class="MsoNormal" style="text-align: left;" align="left"><i><span style="font-size: 10pt; line-height: 100%; color: rgb(127, 127, 127);">''' + self.tr(str2HTML('*')+'The inverse of the distances to the diagonal of the Weight Matrix is considered.', str2HTML('*')+'&Eacute; considerado o inverso das dist&acirc;ncias para a diagonal da Matriz Peso.') + '''
</br>''' + self.tr(str2HTML('**The unit of measurement of the adjusted coordinates is the same as the input coordinates.'), str2HTML('**A unidade de medida das coordenadas ajustadas é a mesma da coordenadas de entrada.')) + '''<o:p></o:p></span></i></p>
</div>
<footer">
<p class="MsoNormal" style="margin-bottom: 0.0001pt; text-align: right;" align="right"><b>''' + self.tr('Leandro Franca', str2HTML('Leandro França')) + '''
</br>''' + self.tr('Cartographic Engineer', 'Eng. Cart&oacute;grafo') + '''<o:p></o:p></b></p>
</br>
<div align="right">'''+ Imgs().social_table_color + '''
</div>
<o:p></o:p></b></p>
</footer>
</body>
</html>
        '''
        template0 = '''<tr style="">
            <td style="border-style: none solid solid; border-color: -moz-use-text-color windowtext windowtext; border-width: medium 1pt 1pt; padding: 0cm 5.4pt; width: 39.3pt;"
 valign="top" width="52">
            <p class="MsoNormal"
 style="margin-bottom: 0.0001pt; text-align: center; line-height: normal;"
 align="center">[STATION]<o:p></o:p></p>
            </td>
            <td style="border-style: none solid solid none; border-color: -moz-use-text-color windowtext windowtext -moz-use-text-color; border-width: medium 1pt 1pt medium; padding: 0cm 5.4pt; width: 46.05pt;"
 valign="top" width="61">
            <p class="MsoNormal"
 style="margin-bottom: 0.0001pt; text-align: center; line-height: normal;"
 align="center">[X]<o:p></o:p></p>
            </td>
            <td
 style="border-style: none solid solid none; border-color: -moz-use-text-color windowtext windowtext -moz-use-text-color; border-width: medium 1pt 1pt medium; padding: 0cm 5.4pt; width: 46.05pt;"
 valign="top" width="61">
            <p class="MsoNormal"
 style="margin-bottom: 0.0001pt; text-align: center; line-height: normal;"
 align="center">[Y]<o:p></o:p></p>
            </td>
            <td
 style="border-style: none solid solid none; border-color: -moz-use-text-color windowtext windowtext -moz-use-text-color; border-width: medium 1pt 1pt medium; padding: 0cm 5.4pt; width: 46.05pt;"
 valign="top" width="61">
            <p class="MsoNormal"
 style="margin-bottom: 0.0001pt; text-align: center; line-height: normal;"
 align="center">[Z]<o:p></o:p></p>
            </td>
          </tr>
        '''

        template1 = '''<tr style="">
      <td style="padding: 0cm 5.4pt; width: 460.2pt;"
 valign="top" width="614">
      <p class="MsoNormal"
 style="margin-bottom: 0.0001pt; text-align: center; line-height: normal;"
 align="center">[SUBS]<o:p></o:p></p>
      </td>
    </tr>
        '''

        template2 = '''<tr style="">
            <td style="border-style: none solid solid; border-color: -moz-use-text-color windowtext windowtext; border-width: medium 1pt 1pt; padding: 0cm 5.4pt; width: 39.3pt;"
 valign="top" width="52">
            <p class="MsoNormal"
 style="margin-bottom: 0.0001pt; text-align: center; line-height: normal;"
 align="center">[STATION]<o:p></o:p></p>
            </td>
            <td style="border-style: none solid solid none; border-color: -moz-use-text-color windowtext windowtext -moz-use-text-color; border-width: medium 1pt 1pt medium; padding: 0cm 5.4pt; width: 46.05pt;"
 valign="top" width="61">
            <p class="MsoNormal"
 style="margin-bottom: 0.0001pt; text-align: center; line-height: normal;"
 align="center">[V_x]<o:p></o:p></p>
            </td>
            <td
 style="border-style: none solid solid none; border-color: -moz-use-text-color windowtext windowtext -moz-use-text-color; border-width: medium 1pt 1pt medium; padding: 0cm 5.4pt; width: 46.05pt;"
 valign="top" width="61">
            <p class="MsoNormal"
 style="margin-bottom: 0.0001pt; text-align: center; line-height: normal;"
 align="center">[V_y]<o:p></o:p></p>
            </td>
            <td
 style="border-style: none solid solid none; border-color: -moz-use-text-color windowtext windowtext -moz-use-text-color; border-width: medium 1pt 1pt medium; padding: 0cm 5.4pt; width: 46.05pt;"
 valign="top" width="61">
            <p class="MsoNormal"
 style="margin-bottom: 0.0001pt; text-align: center; line-height: normal;"
 align="center">[V_z]<o:p></o:p></p>
            </td>
          </tr>
        '''

        linha_slant_range = '''<tr style="">

            <td style="border-style: none solid solid; border-color: -moz-use-text-color windowtext windowtext; border-width: medium 1pt 1pt; padding: 0cm 5.4pt; width: 38.9pt;" valign="top" width="52">
            <p class="MsoNormal" style="margin-bottom: 0.0001pt; text-align: center; line-height: normal;" align="center">t[VISADA]<o:p></o:p></p>

            </td>

            <td style="border-style: none solid solid none; border-color: -moz-use-text-color windowtext windowtext -moz-use-text-color; border-width: medium 1pt 1pt medium; padding: 0cm 5.4pt; width: 28.75pt;" valign="top" width="38">
            <p class="MsoNormal" style="margin-bottom: 0.0001pt; text-align: center; line-height: normal;" align="center">[tn]<o:p></o:p></p>

            </td>

            <td style="border-style: none solid solid none; border-color: -moz-use-text-color windowtext windowtext -moz-use-text-color; border-width: medium 1pt 1pt medium; padding: 0cm 5.4pt; width: 33.05pt;" valign="top" width="44">
            <p class="MsoNormal" style="margin-bottom: 0.0001pt; text-align: center; line-height: normal;" align="center">[s_tn]<o:p></o:p></p>

            </td>
          </tr>'''

        linhas_s_r = ''
        for k, t in enumerate(slant_range):
            tableRowN = linha_slant_range
            str_t = self.tr('{:,.3f}'.format(t), '{:,.3f}'.format(t).replace(',', 'X').replace('.', ',').replace('X', '.'))
            str_s_t = self.tr('{:,.3f}'.format(s_t[k]), '{:,.3f}'.format(s_t[k]).replace(',', 'X').replace('.', ',').replace('X', '.'))
            linhas_s_r += tableRowN.replace('[VISADA]', str(k+1)).replace('[tn]', str_t).replace('[s_tn]', str_s_t)

        # Preenchimento das tabelas
        table1 = ''
        for k, coord in enumerate(Coords):
            vx = coord[0]
            vy = coord[1]
            vz = coord[2]
            tableRowN = template0
            itens  = {
                         '[X]' : self.tr('{:,.3f}'.format(vx), '{:,.3f}'.format(vx).replace(',', 'X').replace('.', ',').replace('X', '.')),
                         '[Y]' : self.tr('{:,.3f}'.format(vy), '{:,.3f}'.format(vy).replace(',', 'X').replace('.', ',').replace('X', '.')),
                         '[Z]' : self.tr('{:,.3f}'.format(vz), '{:,.3f}'.format(vz).replace(',', 'X').replace('.', ',').replace('X', '.')),
                         '[STATION]' : str(k+1),
                         }
            for item in itens:
                tableRowN = tableRowN.replace(item, itens[item])
            table1 += tableRowN

        table2 = ''
        for azimute in String2StringList(Azimutes):
            tableRowN = template1
            itens  = {
                         '[SUBS]' : self.tr(str2HTML(azimute), str2HTML(azimute).replace('.', ',')),
                         }
            for item in itens:
                tableRowN = tableRowN.replace(item, itens[item])
            table2 += tableRowN

        table3 = ''
        for zenite_ang in String2StringList(ÂngulosZenitais):
            tableRowN = template1
            itens  = {
                         '[SUBS]' : self.tr(str2HTML(zenite_ang), str2HTML(zenite_ang).replace('.', ',')),
                         }
            for item in itens:
                tableRowN = tableRowN.replace(item, itens[item])
            table3 += tableRowN

        table4 = ''
        for k in range(len(Coords)):
            vx = V[3*k,0]
            vy = V[3*k+1,0]
            vz = V[3*k+2,0]
            tableRowN = template2
            itens  = {
                         '[V_x]' : self.tr('{:,.3f}'.format(vx), '{:,.3f}'.format(vx).replace(',', 'X').replace('.', ',').replace('X', '.')),
                         '[V_y]' : self.tr('{:,.3f}'.format(vy), '{:,.3f}'.format(vy).replace(',', 'X').replace('.', ',').replace('X', '.')),
                         '[V_z]' : self.tr('{:,.3f}'.format(vz), '{:,.3f}'.format(vz).replace(',', 'X').replace('.', ',').replace('X', '.')),
                         '[STATION]' : str(k+1),
                         }
            for item in itens:
                tableRowN = tableRowN.replace(item, itens[item])
            table4 += tableRowN

        texto = texto.replace('[tabela 1]', table1).replace('[tabela 2]', table2).replace('[tabela 3]', table3).replace('[tabela 4]', table4)
        texto = texto.replace('[PESO]', self.tr('Yes', 'Sim') if usar_peso else self.tr('No', str2HTML('Não')))
        texto = texto.replace('[VAR]', VAR)
        strX = self.tr('{:,.3f}'.format(x), '{:,.3f}'.format(x).replace(',', 'X').replace('.', ',').replace('X', '.'))
        strY = self.tr('{:,.3f}'.format(y), '{:,.3f}'.format(y).replace(',', 'X').replace('.', ',').replace('X', '.'))
        strZ = self.tr('{:,.3f}'.format(z), '{:,.3f}'.format(z).replace(',', 'X').replace('.', ',').replace('X', '.'))
        str_S_X = self.tr('{:,.3f}'.format(s_x), '{:,.3f}'.format(s_x).replace(',', 'X').replace('.', ',').replace('X', '.'))
        str_S_Y = self.tr('{:,.3f}'.format(s_y), '{:,.3f}'.format(s_y).replace(',', 'X').replace('.', ',').replace('X', '.'))
        str_S_Z = self.tr('{:,.3f}'.format(s_z), '{:,.3f}'.format(s_z).replace(',', 'X').replace('.', ',').replace('X', '.'))
        texto = texto.replace('[X]', strX).replace('[Y]', strY).replace('[Z]', strZ).replace('[sX]', str_S_X).replace('[sY]', str_S_Y).replace('[sZ]', str_S_Z)
        texto = texto.replace('[SLANT_RANGE]', linhas_s_r)
        # Exportar HTML
        arq = open(html_output, 'w')
        arq.write(texto)
        arq.close()

        feedback.pushInfo(self.tr('Operation completed successfully!', 'Operação finalizada com sucesso!'))
        feedback.pushInfo(self.tr('Leandro França - Eng Cart', 'Leandro Franca - Cartographic Engineer'))

        Carregar = self.parameterAsBool(
            parameters,
            self.OPEN,
            context
        )

        self.CAMINHO = output
        self.CARREGAR = Carregar

        return {self.OUTPUT: output,
                self.HTML: html_output}


    # Carregamento de arquivo de saída
    CAMINHO = ''
    CARREGAR = True
    def postProcessAlgorithm(self, context, feedback):
        if self.CARREGAR:
            vlayer = QgsVectorLayer(self.CAMINHO, self.tr('Adjusted 3D Coordinates', 'Coordenadas 3D Ajustadas'), "ogr")
            QgsProject.instance().addMapLayer(vlayer)
        return {}
