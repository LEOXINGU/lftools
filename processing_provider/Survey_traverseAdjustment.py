# -*- coding: utf-8 -*-

"""
Survey_traverseAdjustment.py
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
__date__ = '2019-11-17'
__copyright__ = '(C) 2019, Leandro França'

from PyQt5.QtCore import QCoreApplication, QVariant
from qgis.core import (QgsProcessing,
                       QgsFeatureSink,
                       QgsProcessingException,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterFeatureSink,
                       QgsProcessingParameterString,
                       QgsProcessingParameterPoint,
                       QgsProcessingParameterNumber,
                       QgsProcessingParameterCrs,
                       QgsProcessingParameterFileDestination,
                       QgsFields,
                       QgsField,
                       QgsWkbTypes,
                       QgsFeature,
                       QgsGeometry,
                       QgsPointXY,
                       QgsPoint,
                       QgsApplication
                       )
from numpy import radians, arctan, pi, sin, cos, matrix, sqrt, degrees, array, diag, ones, zeros, floor
from numpy.linalg import norm, pinv, inv
from lftools.geocapt.imgs import Imgs
from lftools.geocapt.topogeo import *
import os
from qgis.PyQt.QtGui import QIcon


class TraverseAdjustment(QgsProcessingAlgorithm):
    A = 'A'
    B = 'B'
    Y = 'Y'
    Z = 'Z'
    DIST = 'DIST'
    ANGS = 'ANGS'
    DIST_PREC = 'DIST_PREC'
    PPM = 'PPM'
    ANGS_PREC = 'ANGS_PREC'
    CRS = 'CRS'
    OUTPUT = 'OUTPUT'
    HTML = 'HTML'
    rho = 180*3600/pi

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
        return TraverseAdjustment()

    def name(self):
        return 'traverseadjustment'

    def displayName(self):
        return self.tr('Traverse adjustment', 'Poligonal enquadrada')

    def group(self):
        return self.tr('Survey', 'Agrimensura')

    def groupId(self):
        return 'survey'

    def tags(self):
        return self.tr('survey,agrimensura,polygonal,adjustment,total,station,angle,least square').split(',')

    def icon(self):
        return QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images/total_station.png'))

    txt_en = 'This algorithm performs the traverse adjustments of a framed polygonal by least squares method, where  the distances, angles, and directions observations are adjusted simultaneously, providing the most probable values for the given data set.  Futhermore, the observations can be rigorously weighted based on their estimated errors and adjusted accordingly.'
    txt_pt = 'Este algoritmo realiza o ajustamento de poligonal enquadrada pelo método dos mínimos quadrados, onde as observações de distâncias, ângulos e direções são ajustadas simultaneamente, fornecendo os valores mais prováveis para o conjunto de dados. Além disso, as observações podem ser rigorosamente ponderadas considerando os erros estimados e ajustados.'
    figure = 'images/tutorial/survey_traverse.jpg'

    def shortHelpString(self):
        social_BW = Imgs().social_BW
        nota_en = '''Note: Sample data obtained from class notes of the Geodetic Survey discipline at UFPE.
'''
        nota_pt = '''Nota: Dados de exemplo obtidos das notas de aula da disciplina de Levantamento Geodésicos na UFPE.
'''
        footer = '''<div align="center">
                      <img src="'''+ os.path.join(os.path.dirname(os.path.dirname(__file__)), self.figure) +'''">
                      </div>
                      <div align="right">
                      <div>''' + self.tr(nota_en, nota_pt) + '''
                      ''' +'</a><br><b>'+ self.tr('Author: Leandro Franca', 'Autor: Leandro França')+'''</b>
                      </p>'''+ social_BW + '''</div>
                    </div>'''
        return self.tr(self.txt_en, self.txt_pt) + footer

    def initAlgorithm(self, config=None):
        # INPUT
        self.addParameter(
            QgsProcessingParameterPoint(
                self.A,
                self.tr('A: first (E,N) coordinates','A: 1º ponto (E,N)'),
                defaultValue = QgsPointXY(150000, 250000)
            )
        )

        self.addParameter(
            QgsProcessingParameterPoint(
                self.B,
                self.tr('B: second (E,N) coordinates','B: 2º ponto (E,N)'),
                defaultValue = QgsPointXY(149922.119, 249875.269)
            )
        )

        self.addParameter(
            QgsProcessingParameterPoint(
                self.Y,
                self.tr('Y: penultimate (E,N) coordinates', 'Y: penúltimo ponto (E,N)'),
                defaultValue = QgsPointXY(150347.054, 249727.281)
            )
        )

        self.addParameter(
            QgsProcessingParameterPoint(
                self.Z,
                self.tr('Z: final (E,N) coordinates', 'Z: último ponto (E,N)'),
                defaultValue = QgsPointXY(150350.201, 249622.000)
            )
        )

        self.addParameter(
            QgsProcessingParameterString(
                self.DIST,
                self.tr('List of Horizontal Distances (m)', 'Lista de Distâncias Horizontais (m)'),
                defaultValue = '110.426, 72.375, 186.615, 125.153, 78.235, 130.679, 110.854',
                multiLine = True
            )
        )

        self.addParameter(
            QgsProcessingParameterString(
                self.ANGS,
                self.tr('List of Angles', 'Lista de Ângulos'),
                defaultValue = '''75°23'34", 202°4'36", 56°51'15", 283°31'32", 242°57'31", 185°5'12", 94°11'35", 266°13'20" ''',
                multiLine = True
            )
        )

        self.addParameter(
            QgsProcessingParameterNumber(
                self.DIST_PREC,
                self.tr('Initial distance precision (mm)', 'Precisão linear inicial (mm)'),
                type = QgsProcessingParameterNumber.Type.Double,
                defaultValue = 3
            )
        )

        self.addParameter(
            QgsProcessingParameterNumber(
                self.PPM,
                self.tr('PPM distance precision', 'Precisão linear em PPM'),
                type = QgsProcessingParameterNumber.Type.Double,
                defaultValue = 3
            )
        )

        self.addParameter(
            QgsProcessingParameterNumber(
                self.ANGS_PREC,
                self.tr('Angular precision (seconds)', 'Precisão angular (em segundos)'),
                type = QgsProcessingParameterNumber.Type.Double,
                defaultValue = 10
            )
        )

        self.addParameter(
            QgsProcessingParameterCrs(
                self.CRS,
                self.tr('CRS','SRC'),
                'ProjectCrs'))

        # OUTPUT
        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT,
                self.tr('Adjusted Points', 'Pontos da Poligonal')
            )
        )

        self.addParameter(
            QgsProcessingParameterFileDestination(
                'HTML',
                self.tr('Report of the closed traverse', 'Relatório de ajuste da Poligonal'),
                self.tr('HTML files (*.html)')
            )
        )

    # F(Xo) para distâncias:
    def F_X_d(self, pnts, B, Y):
        F_X = [[sqrt((B[0]-pnts[0][0])**2 + (B[1]-pnts[0][1])**2)]]
        for k in range(len(pnts)-1):
            x1 = pnts[k][0]
            y1 = pnts[k][1]
            x2 = pnts[k+1][0]
            y2 = pnts[k+1][1]
            F_X += [[sqrt((x1-x2)**2 + (y1-y2)**2)]]
        F_X += [[sqrt((Y[0]-pnts[-1][0])**2 + (Y[1]-pnts[-1][1])**2)]]
        return F_X

    # F(Xo) para ângulos:
    def F_X_a(self, pnts, A, B, Y, Z):
        pnts2 = [B] + pnts + [Y]
        # leitura do ângulo no sentido horário
        F_X = [[3600*degrees(DifAz(azimute(QgsPointXY(B[0], B[1]), QgsPointXY(A[0], A[1]))[0], azimute(QgsPointXY(B[0], B[1]),QgsPointXY(pnts[0][0], pnts[0][1]))[0]))]]
        for k in range(len(pnts2)-2):
            pnt0 = QgsPointXY(pnts2[k][0], pnts2[k][1])
            pnt1 = QgsPointXY(pnts2[k+1][0], pnts2[k+1][1])
            pnt2 = QgsPointXY(pnts2[k+2][0], pnts2[k+2][1])
            F_X += [[3600*degrees(DifAz(azimute(pnt1,pnt0)[0], azimute(pnt1, pnt2)[0]))]]
        F_X += [[3600*degrees(DifAz(azimute(QgsPointXY(Y[0], Y[1]), QgsPointXY(pnts2[-2][0], pnts2[-2][1]))[0], azimute(QgsPointXY(Y[0], Y[1]), QgsPointXY(Z[0], Z[1]))[0]))]]
        return F_X

    def Jacobiana_d(self, pnts, B, Y, n_d, n_par):
        Jac = zeros([n_d, n_par])
        pnts2 = [B] + pnts + [Y]
        for k in range(n_d):
            I = pnts2[k]
            J = pnts2[k+1]
            IJ = norm(array(J) - array(I))
            linha = [(I[0]-J[0])/IJ, (I[1]-J[1])/IJ, (J[0]-I[0])/IJ, (J[1]-I[1])/IJ]
            if k == 0:
                Jac[k, 0:2] = linha[2:]
            elif k < (n_d-1):
                Jac[k, (2*k-2):(2*k-2 + 4)] = linha
            else:
                Jac[k, (2*k-2):(2*k-2 + 2)] = linha[:2]
        return list(Jac)

    def Jacobiana_a(self, pnts, A, B, Y, Z, n_angs, n_par):
        Jac = zeros([n_angs, n_par])
        pnts2 = [A, B] + pnts + [Y, Z]
        for k in range(n_angs):
            B = pnts2[k]
            I = pnts2[k+1]
            F = pnts2[k+2]
            IB = norm(array(B) - array(I))
            IF = norm(array(F) - array(I))
            linha = [(I[1]-B[1])/IB**2, (B[0]-I[0])/IB**2, (B[1]-I[1])/IB**2 - (F[1]-I[1])/IF**2,
                     (I[0]-B[0])/IB**2 - (I[0]-F[0])/IF**2, (F[1]-I[1])/IF**2, (I[0]-F[0])/IF**2]
            linha = list(self.rho*array(linha))
            if n_par > 2:
                if k == 0:
                    Jac[k, 0:2] = linha[4:]
                elif k==1:
                    Jac[k, 0:4] = linha[2:]
                elif k < (n_angs-2):
                    Jac[k, (2*k-4):(2*k-4 + 6)] = linha
                elif k == n_angs-2:
                    Jac[k, (2*k-4):(2*k-4 + 4)] = linha[:4]
                else:
                    Jac[k, (2*k-4):(2*k-4 + 2)] = linha[:2]
            else:
                if k == 0:
                    Jac[0, 0:2] = linha[4:]
                elif k == 1:
                    Jac[1, 0:2] = linha[2:4]
                elif k == 2:
                    Jac[2, 0:2] = linha[:2]
        return list(Jac)

    def processAlgorithm(self, parameters, context, feedback):

        A = self.parameterAsPoint(
            parameters,
            self.A,
            context
        )
        A = [A.x(), A.y()]

        B = self.parameterAsPoint(
            parameters,
            self.B,
            context
        )
        B = [B.x(), B.y()]

        Y = self.parameterAsPoint(
            parameters,
            self.Y,
            context
        )
        Y = [Y.x(), Y.y()]

        Z = self.parameterAsPoint(
            parameters,
            self.Z,
            context
        )
        Z = [Z.x(), Z.y()]

        d = self.parameterAsString(
            parameters,
            self.DIST,
            context
        )
        d = String2NumberList(d)
        #feedback.pushInfo('Distances list: ' + str(d))

        angs = self.parameterAsString(
            parameters,
            self.ANGS,
            context
        )
        angs = String2StringList(angs)
        #feedback.pushInfo('Angles list: ' + str(angs))

        lista = []
        for ang in angs:
            lista += [3600*float(dms2dd(ang))]
        angs = lista


        dist_precision = self.parameterAsDouble(
            parameters,
            self.DIST_PREC,
            context
        )
        dist_precision *= 1e-3 # milimeter to meters

        ppm = self.parameterAsDouble(
            parameters,
            self.PPM,
            context
        )
        ppm *= 1e-6 # ppm

        ang_precision = self.parameterAsDouble(
            parameters,
            self.ANGS_PREC,
            context
        )

        CRS = self.parameterAsCrs(
            parameters,
            self.CRS,
            context
        )
        if CRS.isGeographic():
            raise QgsProcessingException(self.tr('The output CRS must be Projected!', 'O SRC da camada de saída deve ser Projetado!'))

        # OUTPUT
        Fields = QgsFields()
        Fields.append(QgsField('id', QVariant.Int))
        GeomType = QgsWkbTypes.Point
        (sink, dest_id) = self.parameterAsSink(
            parameters,
            self.OUTPUT,
            context,
            Fields,
            GeomType,
            CRS
        )
        if sink is None:
            raise QgsProcessingException(self.invalidSinkError(parameters, self.OUTPUT))

        html_output = self.parameterAsFileOutput(
            parameters,
            self.HTML,
            context
        )

        # Precisões
        sd_d = list(dist_precision + array(d)*ppm)
        sd_a = list(ang_precision*ones(len(angs)))

        # Observações
        Lb = matrix(d + angs).reshape([len(d)+len(angs),1])

        # Cálculo de aproximações inicias
        Xo = []
        pnts = []
        Az0 = azimute(QgsPointXY(B[0], B[1]), QgsPointXY(A[0], A[1]))[0]
        p0 = B
        for k in range(len(d)-1):
            ang = pi/2 - Az0 - radians(angs[k]/3600) # leitura do ângulo no sentido horário
            x = p0[0] + d[k]*cos(ang)
            y = p0[1] + d[k]*sin(ang)
            Xo += [[x], [y]]
            pnts += [(x, y)]
            Az0 = -pi/2 - ang
            p0 = (x, y)
        pnts_ini = pnts

        # Cálculo do Erro de Fechamento Linear
        ang = pi/2 - Az0 - radians(angs[-2]/3600)
        x = p0[0] + d[-1]*cos(ang)
        y = p0[1] + d[-1]*sin(ang)
        Y_ = (x, y)
        Erro = array(Y_)-array(Y)
        feedback.pushInfo('Linear closure error: ' + str(round(norm(array(Y_)-array(Y)),4)) + ' m')
        feedback.pushInfo('E and N errors: ' + str((round(Erro[0],4),round(Erro[1],4))) + ' m')

        # Cálculo do Erro de Azimute
        Az0 = azimute(QgsPointXY(B[0], B[1]), QgsPointXY(A[0], A[1]))[0]
        for k in range(len(angs)):
            ang = pi/2 - Az0 - radians(angs[k]/3600) # leitura do ângulo no sentido horário
            Az = pi/2 - ang
            Az0 = Az -pi
        if Az<0 or Az>2*pi:
            if (Az<0):
               Az=Az+2*pi
            else:
               Az=Az-2*pi
        feedback.pushInfo('Angular closure error: ' + str(round(3600*(degrees(Az - azimute(QgsPointXY(Y[0], Y[1]), QgsPointXY(Z[0], Z[1]))[0])),2)) + ' sec')

        # Dados para matrix jacobiana
        n_par = len(pnts)*2
        n_d = len(d)
        n_angs = len(angs)
        n_obs = n_d + n_angs

        # Matriz Peso
        P = matrix(diag(array(sd_d + sd_a)**(-2)))

        # Cálculo iterativo das Coordenadas (Parâmetros)
        cont = 0
        cont_max = 10
        tol = 1e-4

        while cont < cont_max:
            F_Xo = self.F_X_d(pnts, B, Y) + self.F_X_a(pnts, A, B, Y, Z)
            J = matrix(list(self.Jacobiana_d(pnts, B, Y, n_d, n_par)) + list(self.Jacobiana_a(pnts, A, B, Y, Z, n_angs, n_par)))
            L = matrix(Lb - F_Xo)
            delta = pinv(J.T*P*J)*J.T*P*L
            Xa = array(Xo) + array(delta)
            cont += 1
            #print('Iteração:', cont, '\ncoord:', Xa.T, '\ndelta:', delta.T)
            feedback.pushInfo('Iteração: ' + str( cont) + '\nCoord: ' + str(Xa.T) + '\nDelta:' + str(delta.T))
            if max(abs(delta))[0,0] > tol:
                Xo = Xa
                pnts = []
                for k in range(int(len(Xo)/2)):
                    pnts += [(float(Xo[2*k][0]), float(Xo[2*k+1][0]))]
            else:
                break

        # Resíduos
        V = Lb - F_Xo

        # Sigma posteriori
        n = len(Lb) # número de observações
        u = len(Xa) # número de parâmetros
        sigma2 = V.T*P*V/(n-u)

        # Observações Ajustadas (La)
        La = Lb + V

        # MVC de Xa
        SigmaXa = sigma2[0,0]*pinv(J.T*P*J)

        # MVC de La
        SigmaLa = J*SigmaXa*J.T

        # MVC de Lb
        var_priori = 1.0
        SigmaLb = var_priori*inv(P)

        # MVC dos resíduos
        SigmaV = SigmaLa + SigmaLb


        feature = QgsFeature()
        total = 100.0 /len(pnts)  if len(pnts) else 0
        for current, pnt in enumerate(pnts):
            geom = QgsGeometry(QgsPoint(float(pnt[0]), float(pnt[1])))
            feature.setGeometry(geom)
            feature.setAttributes([current+1])
            sink.addFeature(feature, QgsFeatureSink.FastInsert)
            if feedback.isCanceled():
                break
            feedback.setProgress(int(current * total))

       # Relatório
        tabela1 = '''<tr style="">
          <td
style="border: 1pt solid windowtext; padding: 0cm 5.4pt; width: 39.3pt;"
valign="top" width="52">
          <p class="MsoNormal"
style="margin-bottom: 0.0001pt; text-align: center; line-height: normal;"
align="center"><i>[EST]</i><o:p></o:p></p>
          </td>
          <td
style="border-style: solid solid solid none; border-color: windowtext windowtext windowtext -moz-use-text-color; border-width: 1pt 1pt 1pt medium; padding: 0cm 5.4pt; width: 46.05pt;"
valign="top" width="61">
          <p class="MsoNormal"
style="margin-bottom: 0.0001pt; text-align: center; line-height: normal;"
align="center"><i>[E]</i><o:p></o:p></p>
          </td>
          <td
style="border-style: solid solid solid none; border-color: windowtext windowtext windowtext -moz-use-text-color; border-width: 1pt 1pt 1pt medium; padding: 0cm 5.4pt; width: 46.05pt;"
valign="top" width="61">
          <p class="MsoNormal"
style="margin-bottom: 0.0001pt; text-align: center; line-height: normal;"
align="center"><span style="font-style: italic;">[N]</span><o:p></o:p></p>
          </td>
        </tr>
'''
        tabela2 = '''<tr style="">
          <td
style="border: 1pt solid windowtext; padding: 0cm 5.4pt; width: 39.3pt;"
valign="top" width="52">
          <p class="MsoNormal"
style="margin-bottom: 0.0001pt; text-align: center; line-height: normal;"
align="center"><i>[EST]</i><o:p></o:p></p>
          </td>
          <td
style="border-style: solid solid solid none; border-color: windowtext windowtext windowtext -moz-use-text-color; border-width: 1pt 1pt 1pt medium; padding: 0cm 5.4pt; width: 46.05pt;"
valign="top" width="61">
          <p class="MsoNormal"
style="margin-bottom: 0.0001pt; text-align: center; line-height: normal;"
align="center"><i>[E]</i><o:p></o:p></p>
          </td>
          <td
style="border-style: solid solid solid none; border-color: windowtext windowtext windowtext -moz-use-text-color; border-width: 1pt 1pt 1pt medium; padding: 0cm 5.4pt; width: 46.05pt;"
valign="top" width="61">
          <p class="MsoNormal"
style="margin-bottom: 0.0001pt; text-align: center; line-height: normal;"
align="center"><span style="font-style: italic;">[N]</span><o:p></o:p></p>
          </td>
          <td style="text-align: center;"><i>&nbsp;[S_E]&nbsp;</i></td>
          <td style="text-align: center;"><i>&nbsp;[S_N]&nbsp;</i></td>
        </tr>
'''
        tabela3 = '''<tr style="">
          <td
style="border-style: none solid solid; border-color: -moz-use-text-color windowtext windowtext; border-width: medium 1pt 1pt; padding: 0cm 5.4pt; width: 84.9pt;"
valign="top" width="113">
          <p class="MsoNormal"
style="margin-bottom: 0.0001pt; text-align: center; line-height: normal;"
align="center"><span style="" >[obs]<o:p></o:p></span></p>
          </td>
          <td
style="border-style: none solid solid none; border-color: -moz-use-text-color windowtext windowtext -moz-use-text-color; border-width: medium 1pt 1pt medium; padding: 0cm 5.4pt; width: 84.95pt;"
valign="top" width="113">
          <p class="MsoNormal"
style="margin-bottom: 0.0001pt; text-align: center; line-height: normal;"
align="center"><span style="" >[r]<o:p></o:p></span></p>
          </td>
          <td
style="border-style: none solid solid none; border-color: -moz-use-text-color windowtext windowtext -moz-use-text-color; border-width: medium 1pt 1pt medium; padding: 0cm 5.4pt; width: 117.6pt;"
valign="top" width="157">
          <p class="MsoNormal"
style="margin-bottom: 0.0001pt; text-align: center; line-height: normal;"
align="center"><span style="" >[adj_obs]<o:p></o:p></span></p>
          </td>
          <td
style="border-style: none solid solid none; border-color: -moz-use-text-color windowtext windowtext -moz-use-text-color; border-width: medium 1pt 1pt medium; padding: 0cm 5.4pt; width: 102.05pt;"
valign="top" width="136">
          <p class="MsoNormal"
style="margin-bottom: 0.0001pt; text-align: center; line-height: normal;"
align="center"><span style="" >[sd]<o:p></o:p></span></p>
          </td>
        </tr>
'''

        texto = '''<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
<html>
<head>
  <meta content="text/html; charset=ISO-8859-1"
 http-equiv="content-type">
  <title>'''+ self.tr('Traverse Adjustment Report', 'Relatório de Ajuste de Poligonal') + '''</title>
  <link rel = "icon" href = "https://github.com/LEOXINGU/lftools/blob/main/images/lftools.png?raw=true" type = "image/x-icon">
</head>
<body
 style="color: rgb(0, 0, 0); background-color: rgb(255, 255, 204);"
 alink="#000099" link="#000099" vlink="#990099">
<p class="MsoNormal" style="text-align: center;"
 align="center"><b><span
 style="font-size: 12pt; line-height: 107%;">''' + self.tr('TRAVERSE ADJUSTMENT', 'POLIGONAL ENQUADRADA') + '''<o:p></o:p></span></b></p>
<p class="MsoNormal" style="text-align: center;"
 align="center"><span style="font-style: italic;">''' + self.tr('Method of Least Squares', str2HTML('Método dos Mínimos Quadrados')) + '''</span></p>
<p class="MsoNormal" style="text-align: center;"
 align="center"><b><u>''' + self.tr('REPORT', str2HTML('RELATÓRIO')) + '''<o:p></o:p></u></b></p>
<div align="center">
<table style="text-align: center; width: 100%;" border="1"
 cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td width="50%"><b><span style=""
 >'''+ self.tr('Initial approximation', str2HTML('Aproximação Incial')) + '''</span></b></td>
      <td width="50%"><b><span style=""
 >'''+ self.tr('Adjusted Coordinates', 'Coordenadas Ajustadas') + '''<o:p></o:p></span></b></td>
    </tr>
    <tr>
      <td style="text-align: center;">
      <div align="center">
      <table class="MsoTableGrid"
 style="border: medium none ; border-collapse: collapse;"
 border="1" cellpadding="0" cellspacing="0">
        <tbody>
          <tr style="">
            <td
 style="border: 1pt solid windowtext; padding: 0cm 5.4pt; width: 39.3pt;"
 valign="top" width="52">
            <p class="MsoNormal"
 style="margin-bottom: 0.0001pt; text-align: center; line-height: normal;"
 align="center"><i>'''+self.tr('Station',
str2HTML('Estação')) + '''</i><o:p></o:p></p>
            </td>
            <td
 style="border-style: solid solid solid none; border-color: windowtext windowtext windowtext -moz-use-text-color; border-width: 1pt 1pt 1pt medium; padding: 0cm 5.4pt; width: 46.05pt;"
 valign="top" width="61">
            <p class="MsoNormal"
 style="margin-bottom: 0.0001pt; text-align: center; line-height: normal;"
 align="center"><span style="font-style: italic;">E</span><o:p></o:p></p>
            </td>
            <td
 style="border-style: solid solid solid none; border-color: windowtext windowtext windowtext -moz-use-text-color; border-width: 1pt 1pt 1pt medium; padding: 0cm 5.4pt; width: 46.05pt;"
 valign="top" width="61">
            <p class="MsoNormal"
 style="margin-bottom: 0.0001pt; text-align: center; line-height: normal;"
 align="center"><span style="font-style: italic;">N</span><o:p></o:p></p>
            </td>
          </tr>
          [TABLE 1]
        </tbody>
      </table>
      </div>
      </td>
      <td style="text-align: center;">
      <div align="center"></br>
      <table class="MsoTableGrid"
 style="border: medium none ; border-collapse: collapse;"
 border="1" cellpadding="0" cellspacing="0">
        <tbody>
          <tr style="">
            <td
 style="border: 1pt solid windowtext; padding: 0cm 5.4pt; width: 39.3pt;"
 valign="top" width="52">
            <p class="MsoNormal"
 style="margin-bottom: 0.0001pt; text-align: center; line-height: normal;"
 align="center"><i>'''+self.tr('Station',
str2HTML('Estação')) + '''</i><o:p></o:p></p>
            </td>
            <td
 style="border-style: solid solid solid none; border-color: windowtext windowtext windowtext -moz-use-text-color; border-width: 1pt 1pt 1pt medium; padding: 0cm 5.4pt; width: 46.05pt;"
 valign="top" width="61">
            <p class="MsoNormal"
 style="margin-bottom: 0.0001pt; text-align: center; line-height: normal;"
 align="center"><span style="font-style: italic;">E</span><o:p></o:p></p>
            </td>
            <td
 style="border-style: solid solid solid none; border-color: windowtext windowtext windowtext -moz-use-text-color; border-width: 1pt 1pt 1pt medium; padding: 0cm 5.4pt; width: 46.05pt;"
 valign="top" width="61">
            <p class="MsoNormal"
 style="margin-bottom: 0.0001pt; text-align: center; line-height: normal;"
 align="center"><span style="font-style: italic;">N</span><o:p></o:p></p>
            </td>
            <td style="text-align: center;">&nbsp;
&sigma;<span style="font-style: italic;">E &nbsp;</span></td>
            <td style="text-align: center;">&nbsp;
&sigma;<span style="font-style: italic;">N &nbsp;</span></td>
          </tr>
          [TABLE 2]
        </tbody>
      </table>
      <i><span style="" >''' + self.tr('Posteriori variance', str2HTML('Variância a posteriori')) + '''</span></i><span style="" >:&nbsp;</span><span
 style="" >&nbsp;<span
 style="color: red;">[sigma2]</span></span>
      </div>
      </td>
    </tr>
    <tr>
      <td colspan="2" rowspan="1"><b><span
 style="" >''' + self.tr('Observations', str2HTML('Observações')) + '''<o:p></o:p></span></b></td>
    </tr>
    <tr>
      <td colspan="2" rowspan="1"
 style="text-align: center;"> &nbsp;
      <div align="center">
      <table class="MsoTableGrid"
 style="border: medium none ; width: 389.5pt; border-collapse: collapse;"
 border="1" cellpadding="0" cellspacing="0"
 width="519">
        <tbody>
          <tr style="">
            <td
 style="border: 1pt solid windowtext; padding: 0cm 5.4pt; width: 84.9pt;"
 valign="top" width="113">
            <p class="MsoNormal"
 style="margin-bottom: 0.0001pt; text-align: center; line-height: normal;"
 align="center"><span style="" >''' + self.tr('Observation', str2HTML('Observação')) + '''<o:p></o:p></span></p>
            </td>
            <td
 style="border-style: solid solid solid none; border-color: windowtext windowtext windowtext -moz-use-text-color; border-width: 1pt 1pt 1pt medium; padding: 0cm 5.4pt; width: 84.95pt;"
 valign="top" width="113">
            <p class="MsoNormal"
 style="margin-bottom: 0.0001pt; text-align: center; line-height: normal;"
 align="center"><span style="" >''' + self.tr('Residual', str2HTML('Resíduo')) + '''<o:p></o:p></span></p>
            </td>
            <td
 style="border-style: solid solid solid none; border-color: windowtext windowtext windowtext -moz-use-text-color; border-width: 1pt 1pt 1pt medium; padding: 0cm 5.4pt; width: 117.6pt;"
 valign="top" width="157">
            <p class="MsoNormal"
 style="margin-bottom: 0.0001pt; text-align: center; line-height: normal;"
 align="center"><span style="" >''' + self.tr('Adjusted Observation', str2HTML('Observação Ajustada')) + '''<o:p></o:p></span></p>
            </td>
            <td
 style="border-style: solid solid solid none; border-color: windowtext windowtext windowtext -moz-use-text-color; border-width: 1pt 1pt 1pt medium; padding: 0cm 5.4pt; width: 102.05pt;"
 valign="top" width="136">
            <p class="MsoNormal"
 style="margin-bottom: 0.0001pt; text-align: center; line-height: normal;"
 align="center"><span style="" >''' + self.tr('Standard Deviation', str2HTML('Desvio Padrão')) + '''<o:p></o:p></span></p>
            </td>
          </tr>
          [TABLE 3]
        </tbody>
      </table></br>
      </div>
      </td>
    </tr>
  </tbody>
</table>
<p class="MsoNormal" style="text-align: left;"
 align="left"><i><span
 style="font-size: 10pt; line-height: 100%; color: rgb(127, 127, 127);">''' + self.tr(str2HTML('*The unit of measurement of the adjusted coordinates is the same as the input coordinates.'), str2HTML('*A unidade de medida das coordenadas ajustadas é a mesma da coordenadas de entrada.')) + '''<o:p></o:p></span></i></p>
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

        # Aproximação inicial
        cont = 0
        table1 = ''
        for k, pnt in enumerate(pnts_ini):
            X = pnt[0]
            Y = pnt[1]
            cont += 1
            tableRowN = tabela1
            itens  = {
                         '[EST]' : str(k+1),
                         '[E]': self.tr('{:,.3f}'.format(X), '{:,.3f}'.format(X).replace(',', 'X').replace('.', ',').replace('X', '.')),
                         '[N]': self.tr('{:,.3f}'.format(Y), '{:,.3f}'.format(Y).replace(',', 'X').replace('.', ',').replace('X', '.')),
                         }
            for item in itens:
                tableRowN = tableRowN.replace(item, itens[item])
            table1 += tableRowN

        # Ajustamento
        cont = 0
        table2 = ''
        SD = SigmaXa.diagonal()
        for k in range(len(pnts_ini)):
            X = Xa[2*k, 0]
            Y = Xa[2*k+1, 0]
            sdx = sqrt(SD[0, 2*k])
            sdy = sqrt(SD[0, 2*k+1])
            cont += 1
            tableRowN = tabela2
            itens  = {
                         '[EST]' : str(k+1),
                         '[E]': self.tr('{:,.3f}'.format(X), '{:,.3f}'.format(X).replace(',', 'X').replace('.', ',').replace('X', '.')),
                         '[N]': self.tr('{:,.3f}'.format(Y), '{:,.3f}'.format(Y).replace(',', 'X').replace('.', ',').replace('X', '.')),
                         '[S_E]': self.tr('{:,.3f}'.format(sdx), '{:,.3f}'.format(sdx).replace(',', 'X').replace('.', ',').replace('X', '.')),
                         '[S_N]': self.tr('{:,.3f}'.format(sdy), '{:,.3f}'.format(sdy).replace(',', 'X').replace('.', ',').replace('X', '.')),
                         }
            for item in itens:
                tableRowN = tableRowN.replace(item, itens[item])
            table2 += tableRowN

        # Observações
        table3 = ''
        SD = SigmaLa.diagonal()
        for k in range(n_d): # Distâncias
            obs = Lb[k, 0]
            adj_obs = La[k, 0]
            sd = sqrt(SD[0, k])
            r = V[k, 0]
            cont += 1
            tableRowN = tabela3
            itens  = {
                         '[obs]' : str(round(obs,3)),
                         '[r]': str(round(r,4)),
                         '[adj_obs]': str(round(adj_obs,3)),
                         '[sd]': str(round(sd,3))
                         }
            for item in itens:
                tableRowN = tableRowN.replace(item, itens[item])
            table3 += tableRowN
        for t in range(k+1, k+1+ n_angs): # Ângulos
            obs = Lb[t, 0]
            adj_obs = La[t, 0]
            sd = sqrt(SD[0, t])
            r = V[t, 0]
            cont += 1
            tableRowN = tabela3
            itens  = {
                         '[obs]' : str2HTML(dd2dms(obs/3600,3)),
                         '[r]': str(round(r,4)) + '"',
                         '[adj_obs]': str2HTML(dd2dms(adj_obs/3600,3)),
                         '[sd]': str(round(sd,3)) + '"'
                         }
            for item in itens:
                tableRowN = tableRowN.replace(item, itens[item])
            table3 += tableRowN

        # Documento prinicipal
        itens  = {
                         '[TABLE 1]': table1,
                         '[TABLE 2]': table2,
                         '[TABLE 3]': table3,
                         '[sigma2]': str(round(sigma2[0,0],3))
                         }
        for item in itens:
            texto = texto.replace(item, itens[item])

        # Exportar HTML
        arq = open(html_output, 'w')
        arq.write(texto)
        arq.close()

        feedback.pushInfo(self.tr('Operation completed successfully!', 'Operação finalizada com sucesso!'))
        feedback.pushInfo(self.tr('Leandro Franca - Cartographic Engineer', 'Leandro França - Eng Cart'))
        return {self.OUTPUT: dest_id,
                    self.HTML: html_output}
