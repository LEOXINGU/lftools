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
- The vertices must correspond to homologous points, such that the <b>first vertex</b> corresponds to the test point and the <b>second vertex</b> corresponds to the reference point.'''
    
    txt_pt = '''Esta ferramenta pode ser utilizada para avaliar a acurácia posicional planimétrica (2D) de produtos cartográficos digitais.

<b>Saídas</b>
1. <b>Cálculo das discrepâncias</b>: diferenças nas coordenadas X e Y, incluindo as resultantes planimétrica (XY).
2. <b>Relatório de acurácia</b>: relatório do Padrão de Exatidão Cartográfica contendo valores de REMQ e classificação conforme o PEC-PCD Planimétrico.

<b>Requisitos de Entrada</b>
- A camada de entrada deve consistir em linhas com dois vértices.
- Os vértices devem corresponder aos pontos homólogos, de tal forma que o primeiro vértice corresponde ao ponto de teste e o segundo vértice corresponde ao ponto de referência.'''
    
    figure = 'images/tutorial/qualy_horizontal.jpg'

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
        
        html_output = self.parameterAsFileOutput(
            parameters, 
            self.HTML, 
            context
        )
        
        dicionario = {'0.5k': '1:500', '1k': '1:1.000', '2k': '1:2.000', '5k': '1:5.000', '10k': '1:10.000', '25k': '1:25.000', '50k': '1:50.000', '100k': '1:100.000', '250k': '1:250.000'}
        
        valores = ['A', 'B', 'C', 'D']
        
        Escalas = [ esc for esc in dicionario]

        # VALIDAÇÕES
        num_teste = source.featureCount()
        if num_teste < 4:
            raise QgsProcessingException(self.tr('Insufficient number of features for quality evaluation!', 'Número de feições insuficiente para avaliação de qualidade!'))
          
        # SRC definido deve ser projetado
        msg = self.tr('Define a projected CRS for the calculations!', 'Defina um SRC projetado para os cálculos!')
        coordTransf = False
        crs = source.sourceCrs()
        if out_CRS.isValid():
            if out_CRS.isGeographic():
                raise QgsProcessingException(msg)
            else:
                # Transformação de coordenadas
                coordinateTransf = QgsCoordinateTransform(crs, out_CRS, QgsProject.instance())
                coordTransf = True
                SRC = out_CRS
        elif crs.isGeographic():
            raise QgsProcessingException(msg)
        else:
            SRC = crs
        

        (sink, dest_id) = self.parameterAsSink(
            parameters,
            self.OUTPUT,
            context,
            Fields,
            source.wkbType(),
            SRC
        )
        if sink is None:
            raise QgsProcessingException(self.invalidSinkError(parameters, self.OUTPUT))
        
        # Cálculo das discrepâncias
        DISCREP = []
        DISCREP_X = []
        DISCREP_Y = []
        total = 100.0 / source.featureCount() if source.featureCount() else 0
        feedback.pushInfo(self.tr('Planimetric calculation...', 'Cálculo planimétrico...'))
        for current, feat in enumerate(source.getFeatures()):
            geom = feat.geometry()
            if coordTransf and crs != SRC:
                geom.transform(coordinateTransf)
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
        feedback.pushInfo(self.tr('Generating accuracy report...', 'Gerando relatório do PEC-PCD...'))
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
  <meta content="text/html; charset=ISO-8859-1" http-equiv="content-type">
  <title>''' + str2HTML(self.tr('PLANIMETRIC POSITIONAL ACCURACY', 'ACURÁCIA POSICIONAL PLANIMÉTRICA')) + '''</title>
  <link rel = "icon" href = "https://github.com/LEOXINGU/lftools/blob/main/images/lftools.png?raw=true" type = "image/x-icon">
  <meta name="qrichtext" content="1">
  <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
</head>
<body style="background-color: rgb(229, 233, 166);">
<div style="text-align: center;"><span style="font-weight: bold;"><br>
    <img height="80" src="data:image/'''+ 'png;base64,' + lftools_logo + '''">
</div>
<div style="text-align: center;"><span style="font-weight: bold; text-decoration: underline;">''' + str2HTML(self.tr('PLANIMETRIC POSITIONAL ACCURACY REPORT (2D)', 'RELATÓRIO DE ACURÁCIA POSICIONAL PLANIMÉTRICA (2D)')) + '''</span><br>
</div>
<br>
<span style="font-weight: bold;"><br>''' + str2HTML(self.tr('EVALUATED DATA', 'DADOS AVALIADOS')) + '''</span><br>
&nbsp;&nbsp;&nbsp; a. ''' + str2HTML(self.tr('Discrepancy Vectors', 'Vetores de discrepâncias')) + ''': [layer_name]<br>
&nbsp;&nbsp;&nbsp; b. ''' + str2HTML(self.tr('Total Number of Homologous Point Pairs', 'Total de pares de pontos homólogos')) + ''': [layer_count]<br>
<span style="font-weight: bold;"><br>
</span>
<p class="MsoNormal"><b>''' + str2HTML(self.tr('PLANIMETRIC POSITIONAL ACCURACY', 'ACURÁCIA POSICIONAL PLANIMÉTRICA')) + ''' (XY)</b><o:p></o:p></p>
&nbsp;&nbsp;&nbsp; <span style="font-weight: bold;">
1. ''' + str2HTML(self.tr('X Discrepancies', 'Discrepâncias em X')) + ''':</span><br>
&nbsp;&nbsp;&nbsp; &nbsp;&nbsp;&nbsp; a. ''' + str2HTML(self.tr('average (tendency)', 'média (tendência)')) + ''': [discrepX_mean] m<br>
&nbsp;&nbsp;&nbsp; &nbsp;&nbsp;&nbsp; b. ''' + str2HTML(self.tr('standard deviation (precision)', 'desvio-padrão (precisão)')) + ''':&nbsp;[discrepX_std] m<br>
&nbsp;&nbsp;&nbsp; &nbsp;&nbsp;&nbsp; c. ''' + str2HTML(self.tr('maximum', 'máxima')) + ''':&nbsp;[discrepX_max] m<br>
&nbsp;&nbsp;&nbsp; &nbsp;&nbsp;&nbsp; d. ''' + str2HTML(self.tr('minimum', 'mínima')) + ''':&nbsp;[discrepX_min] m<br>
&nbsp;<span style="font-weight: bold;">&nbsp;&nbsp;
2. ''' + str2HTML(self.tr('Y Discrepancies', 'Discrepâncias em Y')) + ''':</span><br>
&nbsp;&nbsp;&nbsp; &nbsp;&nbsp;&nbsp; a. ''' + str2HTML(self.tr('average (tendency)', 'média (tendência)')) + ''': [discrepY_mean] m<br>
&nbsp;&nbsp;&nbsp; &nbsp;&nbsp;&nbsp; b. ''' + str2HTML(self.tr('standard deviation (precision)', 'desvio-padrão (precisão)')) + ''':&nbsp;[discrepY_std] m<br>
&nbsp;&nbsp;&nbsp; &nbsp;&nbsp;&nbsp; c. ''' + str2HTML(self.tr('maximum', 'máxima')) + ''':&nbsp;[discrepY_max] m<br>
&nbsp;&nbsp;&nbsp; &nbsp;&nbsp;&nbsp; d. ''' + str2HTML(self.tr('minimum', 'mínima')) + ''':&nbsp;[discrepY_min] m<br>
&nbsp;&nbsp;&nbsp; <span style="font-weight: bold;">
3. ''' + str2HTML(self.tr('RMSE', 'REMQ')) + ''': [RMSE_XY] m</span><br>
&nbsp;&nbsp;&nbsp; &nbsp;&nbsp;&nbsp; a. ''' + str2HTML(self.tr('maximum discrepancy', 'discrepância máxima')) + ''' (XY):&nbsp;[discrepXY_max] m<br>
&nbsp;&nbsp;&nbsp; &nbsp;&nbsp;&nbsp; b. ''' + str2HTML(self.tr('minimum discrepancy', 'discrepância mínima')) + ''' (XY):&nbsp;[discrepXY_min] m<br>
&nbsp;&nbsp;&nbsp; <span style="font-weight: bold;">
4. ''' + str2HTML(self.tr('Cartographic Accuracy Standard', 'Padrão de Exatidão Cartográfica')) + ''' (</span><span  style="font-weight: bold;">PEC-PCD)<br>
</span>&nbsp;&nbsp;&nbsp; <br> [PEC_YX]<br>
<br>
<hr>''' + str2HTML(self.tr('Leandro Franca', 'Leandro França')) + ''' 2025<br>
<address><font size="+l">''' + str2HTML(self.tr('Cartographic Engineer', 'Eng. Cartógrafo')) + '''<br>
email: contato@geoone.com.br<br>
</font>
</address>
</body>
</html>
        '''
        
        def TabelaPEC(RESULTADOS):
            tabela = '''<table style="margin: 0px;" border="1" cellpadding="4"
     cellspacing="0">
      <tbody>
        <tr>'''
            for escala in Escalas:
                tabela += '    <td style="text-align: center; font-weight: bold;">{}</td>'.format(dicionario[escala])
            
            tabela +='''
            </tr>
            <tr>'''
            for escala in Escalas:
                tabela += '    <td style="text-align: center;">{}</td>'.format(RESULTADOS[escala])
            
            tabela +='''
        </tr>
      </tbody>
    </table>'''
            return tabela
        
        valores = {'[layer_name]': str2HTML(source.sourceName()),
                   '[layer_count]': str(source.featureCount()),
                   '[discrepX_mean]': format_num.format(float(DISCREP_X.mean())),
                   '[discrepX_std]': format_num.format(DISCREP_X.std()),
                   '[discrepX_max]': format_num.format(DISCREP_X.max()),
                   '[discrepX_min]': format_num.format(DISCREP_X.min()),
                   
                   '[discrepY_mean]': format_num.format(DISCREP_Y.mean()),
                   '[discrepY_std]': format_num.format(DISCREP_Y.std()),
                   '[discrepY_max]': format_num.format(DISCREP_Y.max()),
                   '[discrepY_min]': format_num.format(DISCREP_Y.min()),
                   
                   '[RMSE_XY]': format_num.format(RMSE),
                   '[discrepXY_max]': format_num.format(DISCREP.max()),
                   '[discrepXY_min]': format_num.format(DISCREP.min()),
                                     
                   '[PEC_YX]': TabelaPEC(RESULTADOS),
                   }
        
        for valor in valores:
            texto = texto.replace(valor, valores[valor])

        arq.write(texto)
        arq.close()
        
        feedback.pushInfo(self.tr('Operation completed successfully!', 'Operação finalizada com sucesso!'))
        feedback.pushInfo(self.tr('Leandro Franca - Cartographic Engineer', 'Leandro França - Eng Cart'))
        return {self.OUTPUT: dest_id,
                self.HTML: html_output}
