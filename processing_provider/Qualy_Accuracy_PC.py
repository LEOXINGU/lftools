# -*- coding: utf-8 -*-

"""
Qualy_Accuracy_PC.py
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
__date__ = '2021-12-26'
__copyright__ = '(C) 2021, Leandro França'

from PyQt5.QtCore import *
from qgis.core import *
from numpy import sqrt, array, mean, std, pi, sin
import numpy as np
from lftools.geocapt.imgs import Imgs
from lftools.translations.translate import translate
import os
from qgis.PyQt.QtGui import QIcon


class Accuracy_PC(QgsProcessingAlgorithm):

    CHECKPOINTS = 'CHECKPOINTS'
    FIELD = 'FIELD'
    CLOUD = 'CLOUD'
    DISTFILTER = 'DISTFILTER'
    OUTPUT = 'OUTPUT'
    HTML = 'HTML'

    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return Accuracy_PC()

    def name(self):
        return 'Accuracy_PC'.lower()

    def displayName(self):
        return self.tr('Point Cloud positional accuracy', 'Acurácia posicional de Nuvem de Pontos')

    def group(self):
        return self.tr('Qualidade')

    def groupId(self):
        return 'quality'

    def shortHelpString(self):
        return self.tr('''Esta ferramenta pode ser utilizada para a avaliação da acurácia posicional altimétrica de Nuvem de Pontos.
Obtem-se como saída:
1 - Cálculo das discrepâncias em Z para o ponto da nuvem mais próximo do ponto de checagem.
2 - Relatório do Padrão de Exatidão Cartográfica com resultado da REMQ e classificação do PEC-PCD.

Autor: Leandro França - Eng. Cartógrafo''')

    def initAlgorithm(self, config=None):
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.CHECKPOINTS,
                self.tr('Pontos de checagem'),
                [QgsProcessing.TypeVectorPoint]
            )
        )
        
        self.addParameter(
            QgsProcessingParameterField(
                self.FIELD,
                self.tr('Altitude de referência'),
                parentLayerParameterName=self.CHECKPOINTS,
                type=QgsProcessingParameterField.Numeric
            )
        )
        
        self.addParameter(
            QgsProcessingParameterFile(
                self.CLOUD,
                self.tr('Nuvem de pontos como arquivo .txt'),
                behavior = QgsProcessingParameterFile.File,
                fileFilter = 'Texto (*.txt)'
            )
        )
        
        self.addParameter(
            QgsProcessingParameterNumber(
                self.DISTFILTER,
                self.tr('Filtrar pontos mais próximos (metros)'),
                QgsProcessingParameterNumber.Type.Double,
                defaultValue = 1.2,
                minValue = 0
                )
            )
                
        
        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT,
                self.tr('Discrepâncias da Nuvem de Pontos')
            )
        )
        
        self.addParameter(
            QgsProcessingParameterFileDestination(
                'HTML',
                'Relatório do PEC-PCD da nuvem de pontos',
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
            self.CHECKPOINTS,
            context
        )
        if source is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.CHECKPOINTS))
            
        campo = self.parameterAsFields(
            parameters,
            self.FIELD,
            context
        )
        if campo is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.FIELD))
        
        columnIndex = source.fields().indexFromName(campo[0])
        
        caminho = self.parameterAsFile(
            parameters,
            self.CLOUD,
            context
        )
        if not caminho:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.CLOUD))
        
        distProx = self.parameterAsDouble(
            parameters,
            self.DISTFILTER,
            context
        )
        if distProx is None or distProx<=0:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.DISTFILTER))
        
        Fields = source.fields()
        
        itens  = {
                     'np_distância' : QVariant.Double,
                     'np_h' : QVariant.Double,
                     'np_discrep_z' : QVariant.Double
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
        
        # função cálculo das distãncias
        def QuadDist3D (pnt1, pnt2):
            return (pnt1.x() - pnt2.x())**2 + (pnt1.y() - pnt2.y())**2 + (pnt1.z() - pnt2.z())**2
        
        
        # Número de pontos
        with open(caminho) as myfile:
            total_pnts = sum(1 for line in myfile)
        feedback.pushInfo('Número total de pontos: {}'.format('{:,.0f}'.format(total_pnts).replace('.','x').replace(',','.').replace('x',',')))
    
        
        # Filtrando os pontos mais próximos
        feedback.pushInfo('Filtrando os pontos mais próximos...')
        pontos_ref = []
        for feat in source.getFeatures():
            pnt = feat.geometry().asPoint()
            x_ref, y_ref = pnt.x(), pnt.y()
            pontos_ref += [[x_ref, y_ref]]
        
        arquivo = open(caminho, 'r')
        pontos_teste = []
        total = 100.0/total_pnts if total_pnts else 0
        cont = 0
        for linha in arquivo:
            lista = linha.replace('\n', '').split(' ')
            x = float(lista[0])
            y = float(lista[1])
            z = float(lista[2])
            for pnt in pontos_ref:
                x_ref, y_ref = pnt
                if abs(x - x_ref) < distProx and abs(y - y_ref) < distProx:
                    pontos_teste += [[x,y,z]]
                    break
            if feedback.isCanceled():
                break
            cont += 1
            feedback.setProgress(int(cont * total))
        
        # Cálculo das discrepâncias
        feedback.pushInfo('Cálculo das discrepâncias...')
        DISCREP = []
        total = 100.0 / source.featureCount() if source.featureCount() else 0
        for w, feat in enumerate(source.getFeatures()):
            pnt = feat.geometry().asPoint()
            z_ref = float(feat[columnIndex])
            att = feat.attributes()
            nearestPoint = (0,0,0)
            distMin = 1e12
            arquivo = open(caminho, 'r')
            for teste in pontos_teste:
                x = teste[0]
                y = teste[1]
                z = teste[2]
                dist2 = QuadDist3D(QgsPoint(x, y, z), QgsPoint(pnt.x(), pnt.y(), z_ref))
                if dist2 < distMin:
                    distMin = dist2
                    nearestPoint = (x,y,z)
            arquivo.close()
            discrep = nearestPoint[2] - float(z_ref)
            DISCREP += [discrep]
            fet = QgsFeature(Fields)
            fet.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(float(nearestPoint[0]),float(nearestPoint[1]))))
            fet.setAttributes(att + [float(np.sqrt(distMin)), float(nearestPoint[2]), float(discrep)])
            sink.addFeature(fet, QgsFeatureSink.FastInsert)
            if feedback.isCanceled():
                break
            feedback.setProgress(int((w+1) * total))
            
        
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
        arq = open(html_output, 'w')
        texto = '''<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
<html>
<head>
  <meta content="text/html; charset=ISO-8859-1"
 http-equiv="content-type">
  <title>ACUR&Aacute;CIA POSICIONAL ALTIM&Eacute;TRICA</title>
  <meta name="qrichtext" content="1">
  <meta http-equiv="Content-Type"
 content="text/html; charset=utf-8">
</head>
<body style="background-color: rgb(229, 233, 166);">
<div style="text-align: center;"><span
 style="font-weight: bold; text-decoration: underline;">RELAT&Oacute;RIO DE ACUR&Aacute;CIA POSICIONAL ALTIM&Eacute;TRICA</span><br>
</div>
<br>
<span style="font-weight: bold;">1. Dados de entrada </span><br>
&nbsp;&nbsp;&nbsp; a. Pontos de Checagem: {}<br>
&nbsp;&nbsp;&nbsp; b. Nuvem de pontos: {}<br>
&nbsp;&nbsp;&nbsp; c. total de pontos de checagem: {}<br>
<br>
<span style="font-weight: bold;">2. Relat&oacute;rio</span><br>
&nbsp;&nbsp;&nbsp; a. Discrep&acirc;ncias em Z:<br>
&nbsp;&nbsp;&nbsp; &nbsp;&nbsp;&nbsp; a.1. 
m&eacute;dia das discrep&acirc;ncias (tend&ecirc;ncia): {:.3f} m<br>
&nbsp;&nbsp;&nbsp; &nbsp;&nbsp;&nbsp; a.2. 
desvio-padr&atilde;o (precis&atilde;o):&nbsp;{:.3f} m<br>
&nbsp;&nbsp;&nbsp; &nbsp;&nbsp;&nbsp; a.3. 
discrep&acirc;ncia m&aacute;xima:&nbsp;{:.3f} m<br>
&nbsp;&nbsp;&nbsp; &nbsp;&nbsp;&nbsp; a.4. 
discrep&acirc;ncia m&iacute;nima:&nbsp;{:.3f} m<br>
&nbsp;&nbsp;&nbsp; &nbsp;&nbsp;&nbsp; a.5. 
REMQ: {:.3f} m<br>
<br>
<span style="font-weight: bold;">3. Padr&atilde;o de Exatid&atilde;o Cartogr&aacute;fica (</span><span style="font-weight: bold;">PEC-PCD)<br>
<br>
</span>'''.format(self.str2HTML(source.sourceName()), str(os.path.basename(caminho)), source.featureCount(), float(DISCREP.mean()), float(DISCREP.std()), float(DISCREP.max()), float(DISCREP.min()), float(RMSE))
        
        texto += '''<table style="margin: 0px;" border="1" cellpadding="2"
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
