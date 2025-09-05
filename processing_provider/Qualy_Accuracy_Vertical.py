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
from lftools.geocapt.imgs import *
from lftools.translations.translate import translate
from lftools.geocapt.topogeo import str2HTML
from lftools.geocapt.cartography import PEC
from lftools.geocapt.dip import Interpolar
import os
from qgis.PyQt.QtGui import QIcon


class Accuracy_Vertical(QgsProcessingAlgorithm):

    CHECKPOINTS = 'CHECKPOINTS'
    FIELD = 'FIELD'
    DEM = 'DEM'
    RESAMPLING = 'RESAMPLING'
    CRS = 'CRS'
    DECIMAL = 'DECIMAL'
    OUTPUT = 'OUTPUT'
    HTML = 'HTML'

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
    
    LOC = QgsApplication.locale()[:2]

    def tr(self, *string):
        return translate(string, self.LOC)

    def tags(self):
        return 'GeoOne,PEC,qualidade,padrão,rmse,remq,exactness,point cloud,PC,nuvem de pontos,precision,precisão,tendência,tendency,correctness,accuracy,acurácia,discrepância,discrepancy,vector,deltas,3d,vertical,altimétrico,altimetric,cqdg,asprs'.split(',')

    def icon(self):
        return QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images/quality.png'))

    txt_en = '''This tool can be used to evaluate the <b>altimetric (Z) positional accuracy</b> of a Digital Elevation Model (DEM).

<b>Outputs</b>
1. <b>Discrepancy calculations</b> in Z for the reference point.
2. <b>Accuracy report</b>: Cartographic Accuracy Standard report containing RMSE results and classification according to the PEC-PCD.

<b>Input Requirements:</b>
 - DEM as raster layer
 - Point layer with an altitude (Z) field'''
    
    txt_pt = '''Esta ferramenta pode ser utilizada para avaliar a acurácia posicional altimétrica (Z) de Modelos Digitais de Elevação (MDE).

<b>Saídas:</b>
1. Cálculo das discrepâncias em Z para o ponto de referência.
2. Relatório do Padrão de Exatidão Cartográfica com resultado da REMQ e classificação do PEC-PCD.

<b>Requisitos de Entrada:</b>
- Raster do MDE
- Camada de pontos com campo de altitude (Z)'''
    
    figure = 'images/tutorial/qualy_vertical.jpg'

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
            QgsProcessingParameterRasterLayer(
                self.DEM,
                self.tr('DEM', 'MDE'),
                [QgsProcessing.TypeRaster]
            )
        )

        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.CHECKPOINTS,
                self.tr('Reference points', 'Pontos de referência'),
                [QgsProcessing.TypeVectorPoint]
            )
        )
        
        self.addParameter(
            QgsProcessingParameterField(
                self.FIELD,
                self.tr('Reference altitude', 'Altitude de referência'),
                parentLayerParameterName=self.CHECKPOINTS
            )
        )    

        interp = [self.tr('Nearest neighbor', 'Vizinho mais próximo'),
                 self.tr('Bilinear'),
                 self.tr('Bicubic', 'Bicúbica')]

        self.addParameter(
            QgsProcessingParameterEnum(
                self.RESAMPLING,
                self.tr('Interpolation', 'Interpolação'),
				options = interp,
                defaultValue= 1
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
                self.tr('DEM Discrepancies', 'Discrepâncias do MDE')
            )
        )

        self.addParameter(
            QgsProcessingParameterFileDestination(
                self.HTML,
                self.tr('Accuracy Report of the DEM', 'Relatório de Acurácia do MDE'),
                self.tr('HTML files (*.html)')
            )
        )
        

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
                     'discrep_Z' : QVariant.Double
                     }
        for item in itens:
            Fields.append(QgsField(item, itens[item]))


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
        
        html_output = self.parameterAsFileOutput(
            parameters, 
            self.HTML, 
            context
        )

        dicionario = {'0.5k': '1:500', '1k': '1:1.000', '2k': '1:2.000', '5k': '1:5.000', '10k': '1:10.000', '25k': '1:25.000', '50k': '1:50.000', '100k': '1:100.000', '250k': '1:250.000'}
        
        valores = ['A', 'B', 'C', 'D']
        
        Escalas = [ esc for esc in dicionario]
        
        # Abrir camada raster de teste
        feedback.pushInfo(self.tr('Opening DEM raster file...', 'Abrindo arquivo Raster do MDE...'))
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
        image = None # Fechar imagem
        
        # Verificar SRC
        msg = self.tr('The raster layer and the homologous point vector layer must have the same CRS!', 'As camadas raster e vetorial de entrada devem ter o mesmo SRC!')
        if out_CRS.isValid():
            if not out_CRS.description() == SRC.description():
                raise QgsProcessingException(msg)
        else:
            if not crs.description() == SRC.description():
                raise QgsProcessingException(msg)
        
        ## Criar camada de discrepancias altimétricas
        feedback.pushInfo(self.tr('Altimetric calculation...', 'Cálculo das discrepâncias altimétricas...'))
        DISCREP = []
        total_nulos = 0
        # Para cada ponto
            # calcular a discrepancia em relacao ao MDE, caso nao haja pixel nulo
            # armazenar nas somas para gerar (media, desvPad, EMQ, max, min,). quantidade de pontos avaliados, qnt de pontos em pixel nulo
        total = 100.0 / source.featureCount() if source.featureCount() else 0
        for current, feat in enumerate(source.getFeatures()):
            geom = feat.geometry()
            if coordTransf and crs != out_CRS:
                geom.transform(coordinateTransf)
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
  <meta content="text/html; charset=ISO-8859-1" http-equiv="content-type">
  <title>''' + str2HTML(self.tr('DEM POSITIONAL ACCURACY', 'ACURÁCIA POSICIONAL DE MDE')) + '''</title>
  <link rel = "icon" href = "https://github.com/LEOXINGU/lftools/blob/main/images/lftools.png?raw=true" type = "image/x-icon">
  <meta name="qrichtext" content="1">
  <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
</head>
<body style="background-color: rgb(229, 233, 166);">
<div style="text-align: center;"><span style="font-weight: bold;"><br>
    <img height="80" src="data:image/'''+ 'png;base64,' + lftools_logo + '''">
</div>
<div style="text-align: center;"><span style="font-weight: bold; text-decoration: underline;">''' + str2HTML(self.tr('DEM POSITIONAL ACCURACY', 'ACURÁCIA POSICIONAL DE MDE')) + '''</span><br>
</div>
<br>
<span style="font-weight: bold;"><br>''' + str2HTML(self.tr('EVALUATED DATA', 'DADOS AVALIADOS')) + '''</span><br>
&nbsp;&nbsp;&nbsp; a. ''' + str2HTML(self.tr('Digital Elevation Model (DEM)', 'Modelo Digital de Elevação (MDE)')) + ''': [MDE]<br>
&nbsp;&nbsp;&nbsp; b. ''' + str2HTML(self.tr('Reference Points', 'Pontos de referência')) + ''': [layer_name]<br>
&nbsp;&nbsp;&nbsp; c. ''' + str2HTML(self.tr('Number of Points', 'Número de pontos')) + ''': [layer_count]<br>
<span style="font-weight: bold;"><br>
</span>
<br>
<p class="MsoNormal"><b>''' + str2HTML(self.tr('VERTICAL POSITIONAL ACCURACY', 'ACURÁCIA POSICIONAL ALTIMÉTRICA')) + ''' (Z)</b><o:p></o:p></p>
&nbsp;&nbsp;&nbsp; <span style="font-weight: bold;">
1. ''' + str2HTML(self.tr('Z Discrepancies', 'Discrepâncias em Z')) + ''':</span><br>
&nbsp;&nbsp;&nbsp; &nbsp;&nbsp;&nbsp; a. ''' + str2HTML(self.tr('average (tendency)', 'média (tendência)')) + ''': [discrepZ_mean] m<br>
&nbsp;&nbsp;&nbsp; &nbsp;&nbsp;&nbsp; b. ''' + str2HTML(self.tr('standard deviation (precision)', 'desvio-padrão (precisão)')) + ''':&nbsp;[discrepZ_std] m<br>
&nbsp;&nbsp;&nbsp; &nbsp;&nbsp;&nbsp; c. ''' + str2HTML(self.tr('maximum', 'máxima')) + ''':&nbsp;[discrepZ_max] m<br>
&nbsp;&nbsp;&nbsp; &nbsp;&nbsp;&nbsp; d. ''' + str2HTML(self.tr('minimum', 'mínima')) + ''':&nbsp;[discrepZ_min] m<br>
&nbsp;<span style="font-weight: bold;"></span>&nbsp;&nbsp;&nbsp; <span style="font-weight: bold;">
2. ''' + str2HTML(self.tr('RMSE', 'REMQ')) + ''':&nbsp;</span><span  style="font-weight: bold;">[RMSE_Z]</span><span  style="font-weight: bold;"> m</span><br>
&nbsp;&nbsp;&nbsp; &nbsp;&nbsp;&nbsp;<br>
&nbsp;&nbsp;&nbsp; <span style="font-weight: bold;">
3. ''' + str2HTML(self.tr('Cartographic Accuracy Standard', 'Padrão de Exatidão Cartográfica')) + ''' (</span><span  style="font-weight: bold;">PEC-PCD)<br>
</span><br>
[PEC_Z]<br>
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
                   '[MDE]': str2HTML(MDE.name()),
                   '[layer_count]': str(source.featureCount()),
                   
                   '[discrepZ_mean]': format_num.format(DISCREP.mean()),
                   '[discrepZ_std]': format_num.format(DISCREP.std()),
                   '[discrepZ_max]': format_num.format(DISCREP.max()),
                   '[discrepZ_min]': format_num.format(DISCREP.min()),
                                      
                   '[RMSE_Z]': format_num.format(RMSE),
                   '[discrepZ_max]': format_num.format(DISCREP.max()),
                   '[discrepZ_min]': format_num.format(DISCREP.min()),
                   
                   '[PEC_Z]': TabelaPEC(RESULTADOS),
                   }
        
        for valor in valores:
            texto = texto.replace(valor, valores[valor])
        
        arq.write(texto)
        arq.close()
        
        feedback.pushInfo(self.tr('Operation completed successfully!', 'Operação finalizada com sucesso!'))
        feedback.pushInfo(self.tr('Leandro Franca - Cartographic Engineer', 'Leandro França - Eng Cart'))
        return {self.OUTPUT: dest_id,
                self.HTML: html_output}
