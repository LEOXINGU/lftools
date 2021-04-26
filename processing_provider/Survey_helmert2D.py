# -*- coding: utf-8 -*-

"""
Survey_helmert2D.py
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
__date__ = '2019-11-08'
__copyright__ = '(C) 2019, Leandro França'

from PyQt5.QtCore import QCoreApplication, QVariant
from qgis.core import *
import numpy as np
from numpy.linalg import norm, inv, pinv, det
from lftools.geocapt.imgs import Imgs
from lftools.geocapt.topogeo import str2HTML, dd2dms
import os
from qgis.PyQt.QtGui import QIcon


class Helmert2D(QgsProcessingAlgorithm):

    INPUT = 'INPUT'
    VECTOR = 'VECTOR'
    OUTPUT = 'OUTPUT'
    HTML = 'HTML'

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
        return Helmert2D()

    def name(self):
        return 'helmert2D'

    def displayName(self):
        return self.tr('2D conformal transformation', 'Transformação conforme 2D')

    def group(self):
        return self.tr('Survey', 'Agrimensura')

    def groupId(self):
        return 'survey'

    def tags(self):
        return self.tr('survey,agrimensura,helmert,2D,georreferencing,tranformation,conformal,register,adjustment,least squares').split(',')

    def icon(self):
        return QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images/total_station.png'))

    txt_en = """Two-dimensional conformal coordinate transformation, also known as the four-parameter similarity transformation or Helmert 2D, has the characteristic that true shape is retained after transformation.
It is typically used in surveying when converting separate surveys into a common reference coordinate system.
This transformation involves: Scaling, Rotation and Translations.
"""
    txt_pt = """A transformação Conforme, também conhecida como transformação de similaridade de quatro parâmetros ou Helmert 2D, tem a característica de manter a forma (configuração) verdadeira da feição após a transformação.
É normalmente utilizada para o correto georreferenciamento de levantamentos topográficos com coordenadas arbitrárias.
Esta transformação envolve: Escala, Rotação e Translação.
"""
    figure = 'images/tutorial/survey_helmert2D.jpg'

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

    def transformPoint(self, pnt, a, b, c, d):
        X, Y = pnt.x(), pnt.y()
        Xt = X*a - Y*b + c
        Yt = X*b + Y*a + d
        return QgsPointXY(Xt, Yt)

    def transformGeom(self, geom, a, b, c, d):
        if geom.type() == 0: #Point
            if geom.isMultipart():
                pnts = geom.asMultiPoint()
                newPnts = []
                for pnt in pnts:
                    newPnts += [self.transformPoint(pnt, a, b, c, d)]
                newGeom = QgsGeometry.fromMultiPointXY(newPnts)
                return newGeom
            else:
                pnt = geom.asPoint()
                newPnt = self.transformPoint(pnt, a, b, c, d)
                newGeom = QgsGeometry.fromPointXY(newPnt)
                return newGeom
        elif geom.type() == 1: #Line
            if geom.isMultipart():
                linhas = geom.asMultiPolyline()
                newLines = []
                for linha in linhas:
                    newLine =[]
                    for pnt in linha:
                        newLine += [self.transformPoint(pnt, a, b, c, d)]
                    newLines += [newLine]
                newGeom = QgsGeometry.fromMultiPolylineXY(newLines)
                return newGeom
            else:
                linha = geom.asPolyline()
                newLine =[]
                for pnt in linha:
                    newLine += [self.transformPoint(pnt, a, b, c, d)]
                newGeom = QgsGeometry.fromPolylineXY(newLine)
                return newGeom
        elif geom.type() == 2: #Polygon
            if geom.isMultipart():
                poligonos = geom.asMultiPolygon()
                newPolygons = []
                for pol in poligonos:
                    newPol = []
                    for anel in pol:
                        newAnel = []
                        for pnt in anel:
                            newAnel += [self.transformPoint(pnt, a, b, c, d)]
                        newPol += [newAnel]
                    newPolygons += [newPol]
                newGeom = QgsGeometry.fromMultiPolygonXY(newPolygons)
                return newGeom
            else:
                pol = geom.asPolygon()
                newPol = []
                for anel in pol:
                    newAnel = []
                    for pnt in anel:
                        newAnel += [self.transformPoint(pnt, a, b, c, d)]
                    newPol += [newAnel]
                newGeom = QgsGeometry.fromPolygonXY(newPol)
                return newGeom
        else:
            return None

    def initAlgorithm(self, config=None):
        # INPUT
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT,
                self.tr('Input Vector Layer', 'Camada vetorial de entrada'),
                [QgsProcessing.TypeVectorAnyGeometry]
            )
        )

        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.VECTOR,
                self.tr('Vectors Lines (two points)', 'Linhas de vetores (dois pontos)'),
                [QgsProcessing.TypeVectorLine]
            )
        )

        # OUTPUT
        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT,
                self.tr('Transformed Layer', 'Camada transformada')
            )
        )

        self.addParameter(
            QgsProcessingParameterFileDestination(
                self.HTML,
                self.tr('Adjustment Report', 'Relatório de Ajustamento'),
                self.tr('HTML files (*.html)')
            )
        )

    def processAlgorithm(self, parameters, context, feedback):

        entrada = self.parameterAsSource(
            parameters,
            self.INPUT,
            context
        )
        if entrada is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.INPUT))

        deslc = self.parameterAsSource(
            parameters,
            self.VECTOR,
            context
        )
        if deslc is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.VECTOR))
        # Validação dos vetores de georreferenciamento
        if deslc.featureCount()<3:
            raise QgsProcessingException(self.tr('Number of vectors must be greater than two!', 'O número de vetores deve ser maior que 2!'))
        for feat in deslc.getFeatures():
            geom = feat.geometry()
            coord = geom.asPolyline()
            if len(coord) != 2:
                raise QgsProcessingException(self.tr('The vector lines must be created with exactly two points!', 'As linhas de vetores devem ter exatamente 2 vértices!'))

        # OUTPUT
        (sink, dest_id) = self.parameterAsSink(
            parameters,
            self.OUTPUT,
            context,
            entrada.fields(),
            entrada.wkbType(),
            entrada.sourceCrs()
        )
        if sink is None:
            raise QgsProcessingException(self.invalidSinkError(parameters, self.OUTPUT))

        html_output = self.parameterAsFileOutput(
            parameters,
            self.HTML,
            context
        )

        # Transformação Conforme
        '''
        Xt = X*a - Y*b + c
        Yt = X*b + Y*a + d
        a = S*cos(alfa)
        b = S*sin(alfa)
        '''
        # Lista de Pontos
        A = [] # Matriz Design
        L = [] # Transformed Coordinate A to B
        for feat in deslc.getFeatures():
            geom = feat.geometry()
            coord = geom.asPolyline()
            xa = coord[0].x()
            ya = coord[0].y()
            xb = coord[1].x()
            yb = coord[1].y()
            A += [[xa, -ya, 1, 0], [ya, xa, 0, 1]]
            L +=[[xb], [yb]]

        A = np.matrix(A)
        L = np.matrix(L)

        M = A.T*A
        if det(M):
            X = inv(M)*A.T*L

            a = X[0,0]
            b = X[1,0]
            c = X[2,0]
            d = X[3,0]

            theta = np.degrees(np.arctan2(b, a))
            if theta < 0:
                theta = 360 + theta

            S = a/abs(np.cos(np.radians(theta)))
        else:
            raise QgsProcessingException(self.tr('Georeferencing vectors should not be aligned!', 'Os vetores de georreferenciamento não podem ter a mesma direção (alinhados)!'))

        feature = QgsFeature()
        total = 100.0 / entrada.featureCount() if entrada.featureCount() else 0
        for current, feat in enumerate(entrada.getFeatures()):
            geom = feat.geometry()
            newgeom = self.transformGeom(geom, a, b, c, d)
            feature.setGeometry(newgeom)
            feature.setAttributes(feat.attributes())
            sink.addFeature(feature, QgsFeatureSink.FastInsert)
            if feedback.isCanceled():
                break
            feedback.setProgress(int(current * total))

        texto = '''<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
<html>
<head>
  <meta content="text/html; charset=ISO-8859-1"
 http-equiv="content-type">
  <title>Helmert 2D</title>
</head>
<body
 style="color: rgb(0, 0, 0); background-color: rgb(255, 255, 204);"
 alink="#000099" link="#000099" vlink="#990099">
<p class="MsoNormal" style="text-align: center;"
 align="center"><b><span
 style="font-size: 12pt; line-height: 107%;"><o:p></o:p></span></b><span
 style="font-weight: bold; text-decoration: underline;">'''+ self.tr('CONFORMAL TRANSFORMATION',str2HTML('TRANSFORMAÇÃO CONFORME')) + '''(HELMERT 2D)</span></p>
<p class="MsoNormal" style="text-align: center;"
 align="center"><span style="font-style: italic;">''' + self.tr('Mathematical Formulation',str2HTML('Formulação Matemática')) + '''</span></p>
<p class="MsoNormal" style="text-align: center;"
 align="center"><i><span style="">ax
</span></i><i><span style="">-</span></i><i><span
 style=""> by </span></i><i><span
 style="">+</span></i><i><span
 style=""> Tx <span style="">&nbsp;</span>=
X </span></i><i><span style="">+</span></i><i><span
 style=""> Vx<o:p></o:p></span></i></p>
<div style="text-align: center;"><i><span style=""
>bx
</span></i><i><span style="">+</span></i><i><span
 style=""> ay </span></i><i><span
 style="">+</span></i><i><span style=""
> Ty = Y </span></i><i><span
 style="">+</span></i><i><span style=""
> Vy</span></i></div>
<p style="text-align: center;" class="MsoNormal"><b><span
 style="">''' + self.tr('Residual Errors of Control Points',str2HTML('Erro residual dos Pontos de Controle')) + '''<o:p></o:p></span></b></p>
<table
 style="border: medium none ; border-collapse: collapse; text-align: left; margin-left: auto; margin-right: auto;"
 class="MsoTableGrid" border="0" cellpadding="0"
 cellspacing="0">
  <tbody>
    <tr style="">
      <td style="padding: 0cm 5.4pt; width: 84.9pt;"
 valign="top" width="113">
      <p class="MsoNormal"
 style="margin-bottom: 0.0001pt; text-align: center; line-height: normal;"
 align="center"><i><span style="">''' + self.tr('Point',str2HTML('Ponto')) + '''<o:p></o:p></span></i></p>
      </td>
      <td style="padding: 0cm 5.4pt; width: 84.95pt;"
 valign="top" width="113">
      <p class="MsoNormal"
 style="margin-bottom: 0.0001pt; text-align: center; line-height: normal;"
 align="center"><i><span style="">Vx<o:p></o:p></span></i></p>
      </td>
      <td style="padding: 0cm 5.4pt; width: 84.95pt;"
 valign="top" width="113">
      <p class="MsoNormal"
 style="margin-bottom: 0.0001pt; text-align: center; line-height: normal;"
 align="center"><i><span style="">Vy<o:p></o:p></span></i></p>
      </td>
    </tr>
    [TABLE]
  </tbody>
</table>
<br>
<div>
<p class="MsoNormal" style="text-align: center;"
 align="center"><b><span style="">''' + self.tr('Transformation Parameters:',str2HTML('Parâmetros de Transformação:')) + '''<o:p></o:p></span></b></p>
<p class="MsoNormal" style="text-align: center;"
 align="center"><span style="">a
</span><span style="">=</span><span
 style=""> [a]<o:p></o:p></span></p>
<p class="MsoNormal" style="text-align: center;"
 align="center"><span style="">b
</span><span style="">= [b]</span><span
 style=""><o:p></o:p></span></p>
<p class="MsoNormal" style="text-align: center;"
 align="center"><span style="">Tx
</span><span style="">= [c]</span><span
 style=""><o:p></o:p></span></p>
<p class="MsoNormal" style="text-align: center;"
 align="center"><span style="">Ty
</span><span style="">= [d]</span><span
 style=""><o:p></o:p></span></p>
<p class="MsoNormal" style="text-align: center;"
 align="center"><b><span style="">''' + self.tr('Rotation',str2HTML('Rotação')) + '''</span></b><span
 style=""> =</span><span style=""
> [theta]</span><span style=""
><o:p></o:p></span></p>
<p class="MsoNormal" style="text-align: center;"
 align="center"><b><span style="">''' + self.tr('Scale',str2HTML('Escala')) + '''</span></b><span
 style=""> </span><span style=""
>= [S]</span><span style=""
><o:p></o:p></span></p>
<div style="text-align: center;"><b><span style=""
>''' + self.tr('Adjustment&rsquo;s Reference Variance',str2HTML('Variância a posteriori')) + '''</span></b><span style=""
> <span style="">&nbsp;</span>=
</span><span style="">0.02962389940671276</span></div>
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

        table_row = '''<tr style="">
          <td style="padding: 0cm 5.4pt; width: 84.9pt;"
     valign="top" width="113">
          <p class="MsoNormal"
     style="margin-bottom: 0.0001pt; text-align: center; line-height: normal;"
     align="center"><span style="">[ID]<o:p></o:p></span></p>
          </td>
          <td style="padding: 0cm 5.4pt; width: 84.95pt;"
     valign="top" width="113">
          <p class="MsoNormal"
     style="margin-bottom: 0.0001pt; text-align: center; line-height: normal;"
     align="center"><span style="">[Vx]<o:p></o:p></span></p>
          </td>
          <td style="padding: 0cm 5.4pt; width: 84.95pt;"
     valign="top" width="113">
          <p class="MsoNormal"
     style="margin-bottom: 0.0001pt; text-align: center; line-height: normal;"
     align="center"><span style="">[Vy]</span></p>
          </td>
        </tr>'''

        tabela = ''

        # Calculo de Residuos
        transf = []
        for feat in deslc.getFeatures():
            geom = feat.geometry()
            coord = geom.asPolyline()
            Xt, Yt = self.transformPoint(coord[0], a, b, c, d)
            transf += [[Xt],[Yt]]
            X, Y = coord[-1].x(), coord[-1].y()
            Vx = X - Xt
            Vy = Y - Yt
            tableRowN = table_row
            itens  = {'[ID]' : str(feat.id()),
                         '[Vx]' : '{:.4f}'.format(float(Vx)),
                         '[Vy]' : '{:.4f}'.format(float(Vy)),
                         }
            for item in itens:
                tableRowN = tableRowN.replace(item, itens[item])
            tabela += tableRowN

        # Residuos
        V = L - np.matrix(transf)
        # Sigma posteriori
        n = np.shape(A)[0] # número de observações
        u = np.shape(A)[1] # número de parâmetros
        sigma2 = V.T*V/(n-u)

        # Dados finais
        itens  = {
                     '[a]' : str(a),
                     '[b]': str(b),
                     '[c]': str(c),
                     '[d]': str(d),
                     '[theta]': str2HTML(dd2dms(theta,2)),
                     '[S]': str(S),
                     '[sigma]': str(round(sigma2[0,0],4))
                     }
        for item in itens:
                texto = texto.replace(item, itens[item])

        texto = texto.replace('[TABLE]', tabela)

        # Exportar HTML
        arq = open(html_output, 'w')
        arq.write(texto)
        arq.close()

        feedback.pushInfo(self.tr('Operation completed successfully!', 'Operação finalizada com sucesso!'))
        feedback.pushInfo(self.tr('Leandro Franca - Cartographic Engineer', 'Leandro França - Eng Cart'))
        return {self.OUTPUT: dest_id,
                    self.HTML: html_output}
