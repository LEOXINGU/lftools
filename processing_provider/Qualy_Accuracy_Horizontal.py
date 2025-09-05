# -*- coding: utf-8 -*-

"""
Qualy_Accuracy_Horizontal.py
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
__date__ = '2021-12-24'
__copyright__ = '(C) 2021, Leandro França'

from PyQt5.QtCore import *
from qgis.core import *
from numpy import sqrt, array, mean, std, pi, sin
from lftools.geocapt.imgs import *
from lftools.translations.translate import translate
from lftools.geocapt.topogeo import str2HTML
from lftools.geocapt.cartography import PEC
import os
from qgis.PyQt.QtGui import QIcon


class Accuracy_Horizontal(QgsProcessingAlgorithm):

    INPUT = 'INPUT'
    OUTPUT = 'OUTPUT'
    HTML = 'HTML'
    DECIMAL = 'DECIMAL'
    HTML = 'HTML'
    CRS = 'CRS'
    FIELD = 'FIELD'

    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return Accuracy_Horizontal()

    def name(self):
        return 'Accuracy_Horizontal'.lower()

    def displayName(self):
        return self.tr('Horizontal positional accuracy', 'Acurácia posicional planimétrica')

    def group(self):
        return self.tr('Qualidade')

    def groupId(self):
        return 'quality'
    
    LOC = QgsApplication.locale()[:2]

    def tr(self, *string):
        return translate(string, self.LOC)

    def tags(self):
        return 'GeoOne,PEC,qualidade,padrão,rmse,remq,exactness,precision,precisão,tendência,tendency,correctness,accuracy,acurácia,discrepância,discrepancy,vector,deltas,3d,planimetrico,cqdg,asprs'.split(',')

    def icon(self):
        return QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images/quality.png'))
       
    txt_en = '''This tool can be used to evaluate the <b>planimetric (2D) positional accuracy</b> of digital cartographic products.

<b>Outputs</b>
1. <b>Discrepancy calculations</b>: differences in X and Y coordinates, including the planimetric (XY) resultants.
2. <b>Accuracy report</b>: Cartographic Accuracy Standard report containing RMSE values and classification according to the <b>Planimetric PEC-PCD</b>.

<b>Input Requirements</b>
- The input layer must consist of lines with two vertices.
- The vertices must correspond to homologous points, such that the <b>first vertex</b> corresponds to the test point and the <b>second vertex</b> corresponds to the check point.'''
    
    txt_pt = '''Esta ferramenta pode ser utilizada para avaliar a acurácia posicional planimétrica (2D) de produtos cartográficos digitais.

<b>Saídas</b>
1. <b>Cálculo das discrepâncias</b>: diferenças nas coordenadas X e Y, incluindo as resultantes planimétrica (XY).
2. <b>Relatório de acurácia</b>: relatório do Padrão de Exatidão Cartográfica contendo valores de REMQ e classificação conforme o PEC-PCD Planimétrico.

<b>Requisitos de Entrada</b>
- A camada de entrada deve consistir em linhas com dois vértices.
- Os vértices devem corresponder aos pontos homólogos, de tal forma que o primeiro vértice corresponde ao ponto de teste e o segundo vértice corresponde ao ponto de checagem.'''
    
    figure = 'images/tutorial/raster_rgb.jpg'

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
            QgsProcessingParameterFeatureSource(
                self.INPUT,
                self.tr('Vector lines', 'Linhas de vetores'),
                [QgsProcessing.TypeVectorLine]
            )
        )

        self.addParameter(
            QgsProcessingParameterCrs(
                self.CRS,
                self.tr('CRS', 'SRC'),
                # QgsProject.instance().crs(),
                optional = True
                )
            )

        self.addParameter(
            QgsProcessingParameterNumber(
                self.DECIMAL,
                self.tr('Decimal places', 'Casas decimais'),
                QgsProcessingParameterNumber.Type.Integer,
                defaultValue = 3,
                minValue = 0
                )
            )
        
        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT,
                self.tr('2D Planimetric Discrepancies', 'Discrepâncias planimétricas 2D')
            )
        )
        
        self.addParameter(
            QgsProcessingParameterFileDestination(
                'HTML',
                self.tr('2D Planimetric PEC-PCD Report', 'Relatório do PEC-PCD planimétrico 2D'),
                self.tr('HTML files (*.html)')
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        
        source = self.parameterAsSource(
            parameters,
            self.INPUT,
            context
        )

        if source is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.INPUT))
        
        
        decimal = self.parameterAsInt(
            parameters,
            self.DECIMAL,
            context
        )
        
        out_CRS = self.parameterAsCrs(
            parameters,
            self.CRS,
            context
        )
        
        format_num = '{:,.Xf}'.replace('X', str(decimal))

        Fields = source.fields()
        itens  = {
                     'discrep_x' : QVariant.Double,
                     'discrep_y' : QVariant.Double,
                     'discrep_xy' : QVariant.Double
                     }
        for item in itens:
            Fields.append(QgsField(item, itens[item]))
            
        (sink, dest_id) = self.parameterAsSink(
            parameters,
            self.OUTPUT,
            context,
            Fields,
            source.wkbType(),
            source.sourceCrs()
        )
        if sink is None:
            raise QgsProcessingException(self.invalidSinkError(parameters, self.OUTPUT))
        
        html_output = self.parameterAsFileOutput(
            parameters, 
            self.HTML, 
            context
        )
        
        dicionario = {'0.5k': '1:500', '1k': '1:1.000', '2k': '1:2.000', '5k': '1:5.000', '10k': '1:10.000', '25k': '1:25.000', '50k': '1:50.000', '100k': '1:100.000', '250k': '1:250.000'}
        
        valores = ['A', 'B', 'C', 'D']
        
        Escalas = [ esc for esc in dicionario]

        # VALIDAÇÕES
        
        
        # Cálculo das discrepâncias
        DISCREP = []
        DISCREP_X = []
        DISCREP_Y = []
        total = 100.0 / source.featureCount() if source.featureCount() else 0
        for current, feat in enumerate(source.getFeatures()):
            geom = feat.geometry()
            att = feat.attributes()
            x1 = geom.asPolyline()[0].x()
            x2 = geom.asPolyline()[1].x()
            y1 = geom.asPolyline()[0].y()
            y2 = geom.asPolyline()[1].y()
            deltax = x1 - x2
            deltay = y1 - y2
            DISCREP_X += [deltax]
            DISCREP_Y += [deltay]
            discrep = sqrt( (x2 - x1)**2 + (y2 - y1)**2)
            DISCREP += [discrep]
            feature = QgsFeature(Fields)
            feature.setGeometry(geom)
            feature.setAttributes(att + [float(deltax), float(deltay), float(discrep)])
            sink.addFeature(feature, QgsFeatureSink.FastInsert)
            if feedback.isCanceled():
                break
            feedback.setProgress(int((current+1) * total))

        # Gerar relatorio do metodo
        feedback.pushInfo('Gerando relatório do PEC-PCD...')
        DISCREP = array(DISCREP)
        RMSE = sqrt((DISCREP*DISCREP).sum()/len(DISCREP))
        RESULTADOS = {}
        for escala in Escalas:
            mudou = False
            for valor in valores[::-1]:
                EM = PEC[escala]['planim'][valor]['EM']
                EP = PEC[escala]['planim'][valor]['EP']
                if (sum(DISCREP<EM)/len(DISCREP))>0.9 and (RMSE < EP):
                    RESULTADOS[escala] = valor
                    mudou = True
            if not mudou:
                RESULTADOS[escala] = 'R'
        
        feedback.pushInfo('RMSE: {}'.format(round(RMSE,3)))
        for result in RESULTADOS:
            feedback.pushInfo('{} ➜ {}'.format(dicionario[result],RESULTADOS[result]))
        
        # Criacao do arquivo html com os resultados
        DISCREP_X = array(DISCREP_X)
        DISCREP_Y = array(DISCREP_Y)
        
        arq = open(html_output, 'w')
        texto = '''<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
<html>
<head>
  <meta content="text/html; charset=ISO-8859-1"
 http-equiv="content-type">
  <title>ACUR&Aacute;CIA POSICIONAL PLANIM&Eacute;TRICA</title>
  <meta name="qrichtext" content="1">
  <meta http-equiv="Content-Type"
 content="text/html; charset=utf-8">
</head>
<body style="background-color: rgb(229, 233, 166);">
<div style="text-align: center;"><span
 style="font-weight: bold; text-decoration: underline;">RELAT&Oacute;RIO DE ACUR&Aacute;CIA POSICIONAL PLANIM&Eacute;TRICA</span><br>
</div>
<br>
<span style="font-weight: bold;">1. Camada de Entrada</span><br>
&nbsp;&nbsp;&nbsp; a. Vetores de discrep&acirc;ncias: {}<br>
&nbsp;&nbsp;&nbsp; b. Total de pares de pontos hom&oacute;logos: {}<br>
<br>
<span style="font-weight: bold;">2. Relat&oacute;rio</span><br>
&nbsp;&nbsp;&nbsp; a. Discrep&acirc;ncias em X:<br>
&nbsp;&nbsp;&nbsp; &nbsp;&nbsp;&nbsp; a.1. 
m&eacute;dia das discrep&acirc;ncias (tend&ecirc;ncia): {:.3f} m<br>
&nbsp;&nbsp;&nbsp; &nbsp;&nbsp;&nbsp; a.2. 
desvio-padr&atilde;o (precis&atilde;o):&nbsp;{:.3f} m<br>
&nbsp;&nbsp;&nbsp; &nbsp;&nbsp;&nbsp; a.3. 
discrep&acirc;ncia m&aacute;xima:&nbsp;{:.3f} m<br>
&nbsp;&nbsp;&nbsp; &nbsp;&nbsp;&nbsp; a.4. 
discrep&acirc;ncia m&iacute;nima:&nbsp;{:.3f} m<br>
&nbsp;&nbsp;&nbsp; b. Discrep&acirc;ncias em Y:<br>
&nbsp;&nbsp;&nbsp; &nbsp;&nbsp;&nbsp; b.1. 
m&eacute;dia das discrep&acirc;ncias
(tend&ecirc;ncia):&nbsp;{:.3f} m<br>
&nbsp;&nbsp;&nbsp; &nbsp;&nbsp;&nbsp; b.2. 
desvio-padr&atilde;o (precis&atilde;o):&nbsp;{:.3f} m<br>
&nbsp;&nbsp;&nbsp; &nbsp;&nbsp;&nbsp; b.3. 
discrep&acirc;ncia m&aacute;xima:&nbsp;{:.3f} m<br>
&nbsp;&nbsp;&nbsp; &nbsp;&nbsp;&nbsp; b.4. 
discrep&acirc;ncia m&iacute;nima:&nbsp;{:.3f} m<br>
&nbsp;&nbsp;&nbsp; c. REMQ:&nbsp;{:.3f} m<br>
&nbsp;&nbsp;&nbsp; d. discrep&acirc;ncia m&aacute;xima (XY):&nbsp;{:.3f} m<br>
&nbsp;&nbsp;&nbsp; e. discrep&acirc;ncia m&iacute;nima(XY):&nbsp;{:.3f} m<br>
<br>
<span style="font-weight: bold;">3. Padr&atilde;o de Exatid&atilde;o Cartogr&aacute;fica (</span><span style="font-weight: bold;">PEC-PCD)<br>
<br>
</span>'''.format(self.str2HTML(source.sourceName()), source.featureCount(), float(DISCREP_X.mean()), float(DISCREP_X.std()), float(DISCREP_X.max()), float(DISCREP_X.min()), float(DISCREP_Y.mean()), float(DISCREP_Y.std()), float(DISCREP_Y.max()), float(DISCREP_Y.min()), float(RMSE), float(DISCREP.max()), float(DISCREP.min()))
        
        texto += '''<table style="margin: 0px;" border="1" cellpadding="4"
 cellspacing="0">
  <tbody>
    <tr>'''
        for escala in Escalas:
            texto += '    <td style="text-align: center; font-weight: bold;">{}</td>'.format(dicionario[escala])
        
        texto +='''
        </tr>
        <tr>'''
        for escala in Escalas:
            texto += '    <td style="text-align: center;">{}</td>'.format(RESULTADOS[escala])
        
        texto +='''
    </tr>
  </tbody>
</table>
<br>
<hr>
<address><font size="+l">Leandro Fran&ccedil;a
2023<br>
Eng. Cart&oacute;grafo<br>
email: contato@geoone.com.br<br>
</font>
</address>
</body>
</html>
    '''
        arq.write(texto)
        arq.close()
        
        feedback.pushInfo(self.tr('Operation completed successfully!', 'Operação finalizada com sucesso!'))
        feedback.pushInfo(self.tr('Leandro Franca - Cartographic Engineer', 'Leandro França - Eng Cart'))
        return {self.OUTPUT: dest_id,
                self.HTML: html_output}
