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
from lftools.geocapt.imgs import Imgs
from lftools.translations.translate import translate
import os
from qgis.PyQt.QtGui import QIcon


class Accuracy_Horizontal(QgsProcessingAlgorithm):

    INPUT = 'INPUT'
    OUTPUT = 'OUTPUT'
    HTML = 'HTML'

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

    def shortHelpString(self):
        return self.tr('''Esta ferramenta pode ser utilizada para a avaliação da acurácia posicional planimétrica de produtos cartográficos digitais.
Obtem-se como saída:
1 - Cálculo das discrepâncias em X e Y, bem como a resultande planimétrica XY.
2 - Relatório do Padrão de Exatidão Cartográfica com resultado da REMQ e classificação do PEC-PCD.

Obs: As feições de entrada devem ser linhas de exatamente dois vértices. O primeiro vértice corresponde ao ponto teste e o segundo ao ponto de checagem.
Autor: Leandro França - Eng. Cartógrafo''')

    def initAlgorithm(self, config=None):
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT,
                self.tr('Linhas de vetores'),
                [QgsProcessing.TypeVectorLine]
            )
        )
        
        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT,
                self.tr('Discrepâncias planimétricas')
            )
        )
        
        self.addParameter(
            QgsProcessingParameterFileDestination(
                'HTML',
                'Relatório do PEC-PCD planimétrico',
                self.tr('arquivo HTML (*.html)')
            )
        )
        
    def str2HTML(self, texto):
        if texto:
            dicHTML = {'Á': '&Aacute;',	'á': '&aacute;',	'Â': '&Acirc;',	'â': '&acirc;',	'À': '&Agrave;',	'à': '&agrave;',	'Å': '&Aring;',	'å': '&aring;',	'Ã': '&Atilde;',	'ã': '&atilde;',	'Ä': '&Auml;',	'ä': '&auml;',	'Æ': '&AElig;',	'æ': '&aelig;',	'É': '&Eacute;',	'é': '&eacute;',	'Ê': '&Ecirc;',	'ê': '&ecirc;',	'È': '&Egrave;',	'è': '&egrave;',	'Ë': '&Euml;',	'ë': '&Euml;',	'Ð': '&ETH;',	'ð': '&eth;',	'Í': '&Iacute;',	'í': '&iacute;',	'Î': '&Icirc;',	'î': '&icirc;',	'Ì': '&Igrave;',	'ì': '&igrave;',	'Ï': '&Iuml;',	'ï': '&iuml;',	'Ó': '&Oacute;',	'ó': '&oacute;',	'Ô': '&Ocirc;',	'ô': '&ocirc;',	'Ò': '&Ograve;',	'ò': '&ograve;',	'Ø': '&Oslash;',	'ø': '&oslash;',	'Ù': '&Ugrave;',	'ù': '&ugrave;',	'Ü': '&Uuml;',	'ü': '&uuml;',	'Ç': '&Ccedil;',	'ç': '&ccedil;',	'Ñ': '&Ntilde;',	'ñ': '&ntilde;',	'Ý': '&Yacute;',	'ý': '&yacute;',	'"': '&quot;', '”': '&quot;',	'<': '&lt;',	'>': '&gt;',	'®': '&reg;',	'©': '&copy;',	'\'': '&apos;', 'ª': '&ordf;', 'º': '&ordm', '°':'&deg;'}
            for item in dicHTML:
                if item in texto:
                    texto = texto.replace(item, dicHTML[item])
            return texto
        else:
            return ''

    def processAlgorithm(self, parameters, context, feedback):
        
        source = self.parameterAsSource(
            parameters,
            self.INPUT,
            context
        )

        if source is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.INPUT))
        
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

        
        PEC = { '0.5k': {'planim': {'A': {'EM': 0.14, 'EP': 0.085},'B': {'EM': 0.25, 'EP': 0.15},'C': {'EM': 0.4, 'EP': 0.25},'D': {'EM': 0.5, 'EP': 0.3}}, 'altim': {'A': {'EM': 0.135, 'EP': 0.085},'B': {'EM': 0.25, 'EP': 0.165},'C': {'EM': 0.3, 'EP': 0.2},'D': {'EM': 0.375, 'EP': 0.25}}},
        '1k': {'planim': {'A': {'EM': 0.28, 'EP': 0.17},'B': {'EM': 0.5, 'EP': 0.3},'C': {'EM': 0.8, 'EP': 0.5},'D': {'EM': 1, 'EP': 0.6}}, 'altim': {'A': {'EM': 0.27, 'EP': 0.17},'B': {'EM': 0.5, 'EP': 0.33},'C': {'EM': 0.6, 'EP': 0.4},'D': {'EM': 0.75, 'EP': 0.5}}},
        '2k': {'planim': {'A': {'EM': 0.56, 'EP': 0.34},'B': {'EM': 1, 'EP': 0.6},'C': {'EM': 1.6, 'EP': 1},'D': {'EM': 2, 'EP': 1.2}}, 'altim': {'A': {'EM': 0.27, 'EP': 0.17},'B': {'EM': 0.5, 'EP': 0.33},'C': {'EM': 0.6, 'EP': 0.4},'D': {'EM': 0.75, 'EP': 0.5}}},
        '5k': {'planim': {'A': {'EM': 1.4, 'EP': 0.85},'B': {'EM': 2.5, 'EP': 1.5},'C': {'EM': 4, 'EP': 2.5},'D': {'EM': 5, 'EP': 3}}, 'altim': {'A': {'EM': 0.54, 'EP': 0.34},'B': {'EM': 1, 'EP': 0.67},'C': {'EM': 1.2, 'EP': 0.8},'D': {'EM': 1.5, 'EP': 1}}},
        '10k': {'planim': {'A': {'EM': 2.8, 'EP': 1.7},'B': {'EM': 5, 'EP': 3},'C': {'EM': 8, 'EP': 5},'D': {'EM': 10, 'EP': 6}}, 'altim': {'A': {'EM': 1.35, 'EP': 0.84},'B': {'EM': 2.5, 'EP': 1.67},'C': {'EM': 3, 'EP': 2},'D': {'EM': 3.75, 'EP': 2.5}}},
        '25k': {'planim': {'A': {'EM': 7, 'EP': 4.25},'B': {'EM': 12.5, 'EP': 7.5},'C': {'EM': 20, 'EP': 12.5},'D': {'EM': 25, 'EP': 15}}, 'altim': {'A': {'EM': 2.7, 'EP': 1.67},'B': {'EM': 5, 'EP': 3.33},'C': {'EM': 6, 'EP': 4},'D': {'EM': 7.5, 'EP': 5}}},
        '50k': {'planim': {'A': {'EM': 14, 'EP': 8.5},'B': {'EM': 25, 'EP': 15},'C': {'EM': 40, 'EP': 25},'D': {'EM': 50, 'EP': 30}}, 'altim': {'A': {'EM': 5.5, 'EP': 3.33},'B': {'EM': 10, 'EP': 6.67},'C': {'EM': 12, 'EP': 8},'D': {'EM': 15, 'EP': 10}}},
        '100k': {'planim': {'A': {'EM': 28, 'EP': 17},'B': {'EM': 50, 'EP': 30},'C': {'EM': 80, 'EP': 50},'D': {'EM': 100, 'EP': 60}}, 'altim': {'A': {'EM': 13.7, 'EP': 8.33},'B': {'EM': 25, 'EP': 16.67},'C': {'EM': 30, 'EP': 20},'D': {'EM': 37.5, 'EP': 25}}},
        '250k': {'planim': {'A': {'EM': 70, 'EP': 42.5},'B': {'EM': 125, 'EP': 75},'C': {'EM': 200, 'EP': 125},'D': {'EM': 250, 'EP': 150}}, 'altim': {'A': {'EM': 27, 'EP': 16.67},'B': {'EM': 50, 'EP': 33.33},'C': {'EM': 60, 'EP': 40},'D': {'EM': 75, 'EP': 50}}}}
        
        dicionario = {'0.5k': '1:500', '1k': '1:1.000', '2k': '1:2.000', '5k': '1:5.000', '10k': '1:10.000', '25k': '1:25.000', '50k': '1:50.000', '100k': '1:100.000', '250k': '1:250.000'}
        
        valores = ['A', 'B', 'C', 'D']
        
        Escalas = [ esc for esc in dicionario]
        
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
        
        feedback.pushInfo(self.tr('Operação finalizada com sucesso!'))
        feedback.pushInfo('Leandro França - Eng Cart')
        return {self.OUTPUT: dest_id,
                self.HTML: html_output}
