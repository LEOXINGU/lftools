# -*- coding: utf-8 -*-

"""
Qualy_Accuracy_Vertical.py
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
from numpy import sqrt, array, mean, std, pi, sin, floor, ceil
from osgeo import osr, gdal
from lftools.geocapt.imgs import Imgs
from lftools.translations.translate import translate
import os
from qgis.PyQt.QtGui import QIcon


class Accuracy_Vertical(QgsProcessingAlgorithm):

    CHECKPOINTS = 'CHECKPOINTS'
    FIELD = 'FIELD'
    DEM = 'DEM'
    RESAMPLING = 'RESAMPLING'
    OUTPUT = 'OUTPUT'
    HTML = 'HTML'

    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return Accuracy_Vertical()

    def name(self):
        return 'Accuracy_Vertical'.lower()

    def displayName(self):
        return self.tr('Vertical positional accuracy', 'Acurácia posicional altimétrica')

    def group(self):
        return self.tr('Qualidade')

    def groupId(self):
        return 'quality'

    def shortHelpString(self):
        return self.tr('''Esta ferramenta pode ser utilizada para a avaliação da acurácia posicional altimétrica de produtos cartográficos digitais.
Obtem-se como saída:
1 - Cálculo das discrepâncias em Z (altimétricas).
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
                parentLayerParameterName=self.CHECKPOINTS
            )
        )
        
        self.addParameter(
            QgsProcessingParameterRasterLayer(
                self.DEM,
                self.tr('MDE'),
                [QgsProcessing.TypeRaster]
            )
        )
        
        opcoes = [self.tr('Vizinho mais próximo'),
          self.tr('Bilinear'),
          self.tr('Bicúbica')
          ]

        self.addParameter(
            QgsProcessingParameterEnum(
                self.RESAMPLING,
                self.tr('Método de Interpolação'),
                options = opcoes,
                defaultValue= 1
            )
        )
        
        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT,
                self.tr('Discrepâncias altimétricas')
            )
        )
        
        self.addParameter(
            QgsProcessingParameterFileDestination(
                'HTML',
                'Relatório do PEC-PCD altimétrico',
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
        
        MDE = self.parameterAsRasterLayer(
            parameters,
            self.DEM,
            context
        )
        if MDE is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.DEM))
        
        reamostragem = self.parameterAsEnum(
            parameters,
            self.RESAMPLING,
            context
        )
        if reamostragem is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.RESAMPLING))
        metodo = ['nearest','bilinear','bicubic'][reamostragem]
        
        Fields = source.fields()
        CRS = source.sourceCrs()
        itens  = {
                     'discrep_Z' : QVariant.Double
                     }
        for item in itens:
            Fields.append(QgsField(item, itens[item]))
            
        (sink, dest_id) = self.parameterAsSink(
            parameters,
            self.OUTPUT,
            context,
            Fields,
            source.wkbType(),
            CRS
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
        
        # Funcao de Interpolacao
        def Interpolar(X, Y, BAND, origem, resol_X, resol_Y, metodo, nulo):
            if metodo == 'nearest':
                I = int(round((origem[1]-Y)/resol_Y - 0.5))
                J = int(round((X - origem[0])/resol_X - 0.5))
                try:
                    return float(BAND[I][J])
                except:
                    return nulo
            elif metodo == 'bilinear':
                I = (origem[1]-Y)/resol_Y - 0.5
                J = (X - origem[0])/resol_X - 0.5
                di = I - floor(I)
                dj = J - floor(J)
                try:
                    if (BAND[int(floor(I)):int(ceil(I))+1, int(floor(J)):int(ceil(J))+1] == nulo).sum() == 0:
                        Z = (1-di)*(1-dj)*BAND[int(floor(I))][int(floor(J))] + (1-dj)*di*BAND[int(ceil(I))][int(floor(J))] + (1-di)*dj*BAND[int(floor(I))][int(ceil(J))] + di*dj*BAND[int(ceil(I))][int(ceil(J))]
                        return float(Z)
                    else:
                        return nulo
                except:
                    return nulo
            elif metodo == 'bicubic':
                I = (origem[1]-Y)/resol_Y - 0.5
                J = (X - origem[0])/resol_X - 0.5
                di = I - floor(I)
                dj = J - floor(J)
                I=int(floor(I))
                J=int(floor(J))
                try:
                    if (BAND[I-1:I+3, J-1:J+3] == nulo).sum() == 0:
                        MatrInv = np.mat([[-1/6, 0.5, -0.5, 1/6], [ 0.5, -1., 0.5, 0.], [-1/3, -0.5,  1., -1/6], [ 0., 1., 0., 0.]]) # resultado da inversa: (np.mat([[-1, 1, -1, 1], [0, 0, 0, 1], [1, 1, 1, 1], [8, 4, 2, 1]])).I #
                        MAT  = np.mat([ [BAND[I-1, J-1],  BAND[I-1, J], BAND[I-1, J+1], BAND[I-2, J+2]],
                                        [BAND[I, J-1],    BAND[I, J],   BAND[I, J+1],   BAND[I, J+2]],
                                        [BAND[I+1, J-1],  BAND[I+1, J], BAND[I+1, J+1], BAND[I+1, J+2]],
                                        [BAND[I+2, J-1],  BAND[I+2, J], BAND[I+2, J+1], BAND[I+2, J+2]]])
                        coef = MatrInv*MAT.transpose()
                        # Horizontal
                        pi = coef[0,:]*pow(dj,3)+coef[1,:]*pow(dj,2)+coef[2,:]*dj+coef[3,:]
                        # Vertical
                        coef2 = MatrInv*pi.transpose()
                        pj = coef2[0]*pow(di,3)+coef2[1]*pow(di,2)+coef2[2]*di+coef2[3]
                        return float(pj)
                    else:
                        return nulo
                except:
                    return nulo
        
        # Abrir camada raster de teste
        feedback.pushInfo('Abrindo o MDE...')
        image = gdal.Open(MDE.dataProvider().dataSourceUri())
        band = image.GetRasterBand(1).ReadAsArray()
        NULO = image.GetRasterBand(1).GetNoDataValue()
        if NULO == None:
            NULO =-9999
        prj=image.GetProjection()
        SRC = QgsCoordinateReferenceSystem()
        SRC.createFromWkt(prj)
        # Number of rows and columns
        cols = image.RasterXSize # Number of columns
        rows = image.RasterYSize # Number of rows
        # Origem e resolucao da imagem
        ulx, xres, xskew, uly, yskew, yres  = image.GetGeoTransform()
        origem = (ulx, uly)
        resol_X = abs(xres)
        resol_Y = abs(yres)
        lrx = ulx + (cols * xres)
        lry = uly + (rows * yres)
        bbox = [ulx, lrx, lry, uly]
        image=None # Fechar imagem
        
        # Verificar SRC
        if not SRC.description() == CRS.description():
            raise QgsProcessingException('As camadas raster e vetorial de entrada devem ter o mesmo SRC!')
        
        ## Criar camada de discrepancias
        DISCREP = []
        total_nulos = 0
        # Para cada ponto
            # calcular a discrepancia em relacao ao MDE, caso nao haja pixel nulo
            # armazenar nas somas para gerar (media, desvPad, EMQ, max, min,). quantidade de pontos avaliados, qnt de pontos em pixel nulo
        total = 100.0 / source.featureCount() if source.featureCount() else 0
        for current, feat in enumerate(source.getFeatures()):
            geom = feat.geometry()
            att = feat.attributes()
            pnt = geom.asPoint()
            X = pnt.x()
            Y = pnt.y()
            if bbox[0]<X and bbox[1]>X and bbox[2]<Y and bbox[3]>Y:
                cotaRef = float(feat[columnIndex])
                cotaTest = Interpolar(X, Y, band, origem, resol_X, resol_Y, metodo, NULO)
                if cotaTest != NULO:
                    discrep = cotaTest - cotaRef
                    DISCREP += [discrep]
                    feature = QgsFeature(Fields)
                    feature.setGeometry(geom)
                    feature.setAttributes(att + [float(discrep)])
                    sink.addFeature(feature, QgsFeatureSink.FastInsert)
                else:
                    total_nulos +=1
            else:
               total_nulos +=1
            if feedback.isCanceled():
                break
            feedback.setProgress(int((current+1) * total))

            
        # Gerar relatorio do metodo
        feedback.pushInfo('Gerando relatório do PEC-PCD...')
        DISCREP = array(DISCREP)
        RMSE = sqrt((DISCREP*DISCREP).sum()/len(DISCREP))
        cont = 0
        RESULTADOS = {}
        for escala in Escalas:
            mudou = False
            for valor in valores[::-1]:
                EM = PEC[escala]['altim'][valor]['EM']
                EP = PEC[escala]['altim'][valor]['EP']
                if ((DISCREP<EM).sum()/float(len(DISCREP)))>0.9 and (RMSE < EP):
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
<span style="font-weight: bold;">1. Camadas de Entrada</span><br>
&nbsp;&nbsp;&nbsp; a. Pontos de Checagem: {}<br>
&nbsp;&nbsp;&nbsp; b. MDE: {}<br>
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
</span>'''.format(self.str2HTML(source.sourceName()), MDE.name() , source.featureCount(), float(DISCREP.mean()), float(DISCREP.std()), float(DISCREP.max()), float(DISCREP.min()), float(RMSE)) 
        
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
