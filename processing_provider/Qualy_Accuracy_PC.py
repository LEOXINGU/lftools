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
from lftools.geocapt.imgs import *
from lftools.translations.translate import translate
from lftools.geocapt.topogeo import str2HTML
from lftools.geocapt.cartography import PEC
import os
from qgis.PyQt.QtGui import QIcon


class Accuracy_PC(QgsProcessingAlgorithm):

    CHECKPOINTS = 'CHECKPOINTS'
    FIELD = 'FIELD'
    CLOUD = 'CLOUD'
    DISTFILTER = 'DISTFILTER'
    CRS = 'CRS'
    DECIMAL = 'DECIMAL'
    OUTPUT = 'OUTPUT'
    HTML = 'HTML'

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

    LOC = QgsApplication.locale()[:2]

    def tr(self, *string):
        return translate(string, self.LOC)

    def tags(self):
        return 'GeoOne,PEC,qualidade,padrão,rmse,remq,exactness,point cloud,PC,nuvem de pontos,precision,precisão,tendência,tendency,correctness,accuracy,acurácia,discrepância,discrepancy,vector,deltas,3d,vertical,altimétrico,altimetric,cqdg,asprs'.split(',')

    def icon(self):
        return QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images/quality.png'))

    txt_en = '''This tool can be used to evaluate the <b>altimetric (Z) positional accuracy</b> of point clouds.

<b>Outputs</b>
1. <b>Discrepancy calculations</b> in Z for the point in the cloud closest to the reference point.
2. <b>Accuracy report</b>: Cartographic Accuracy Standard report containing RMSE results and classification according to the PEC-PCD.

<b>Input Requirements:</b>
 - Point cloud in <b>.txt</b> format
 - Point layer with an altitude (Z) field'''
    
    txt_pt = '''Esta ferramenta pode ser utilizada para avaliar a acurácia posicional altimétrica (Z) de nuvem de pontos.

<b>Saídas:</b>
1. Cálculo das discrepâncias em Z para o ponto da nuvem mais próximo do ponto de referência.
2. Relatório do Padrão de Exatidão Cartográfica com resultado da REMQ e classificação do PEC-PCD.

<b>Requisitos de Entrada:</b>
- Nuvem de pontos no formato .txt
- Camada de pontos com campo de altitude (Z)'''
    
    figure = 'images/tutorial/qualy_pc.jpg'

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
            QgsProcessingParameterFile(
                self.CLOUD,
                self.tr('Point Cloud', 'Nuvem de pontos') + ' .TXT',
                behavior = QgsProcessingParameterFile.File,
                fileFilter = 'Texto (*.txt)'
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
                parentLayerParameterName=self.CHECKPOINTS,
                type=QgsProcessingParameterField.Numeric
            )
        )
        
        self.addParameter(
            QgsProcessingParameterNumber(
                self.DISTFILTER,
                self.tr('Distance to filter nearest points (m)', 'Distância para filtrar pontos mais próximos (m)'),
                QgsProcessingParameterNumber.Type.Double,
                defaultValue = 1.2,
                minValue = 0
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
                self.tr('Point Cloud Discrepancies', 'Discrepâncias da Nuvem de Pontos')
            )
        )

        self.addParameter(
            QgsProcessingParameterFileDestination(
                self.HTML,
                self.tr('Accuracy Report of the Point Cloud', 'Relatório de Acurácia da nuvem de pontos'),
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
                     'np_distância' : QVariant.Double,
                     'np_h' : QVariant.Double,
                     'np_discrep_z' : QVariant.Double
                     }
        for item in itens:
            Fields.append(QgsField(item, itens[item]))

        
        html_output = self.parameterAsFileOutput(
            parameters, 
            self.HTML, 
            context
        )


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

        dicionario = {'0.5k': '1:500', '1k': '1:1.000', '2k': '1:2.000', '5k': '1:5.000', '10k': '1:10.000', '25k': '1:25.000', '50k': '1:50.000', '100k': '1:100.000', '250k': '1:250.000'}
        
        valores = ['A', 'B', 'C', 'D']
        
        Escalas = [ esc for esc in dicionario]
        
        # função cálculo das distâncias
        def QuadDist3D (pnt1, pnt2):
            return (pnt1.x() - pnt2.x())**2 + (pnt1.y() - pnt2.y())**2 + (pnt1.z() - pnt2.z())**2
        
        
        # Número de pontos
        with open(caminho) as myfile:
            total_pnts = sum(1 for line in myfile)
        feedback.pushInfo(self.tr('Total number of points: ', 'Número total de pontos: ') + '{}'.format(total_pnts))
    
        
        # Filtrando os pontos mais próximos
        feedback.pushInfo(self.tr('Filtering nearest points...', 'Filtrando os pontos mais próximos...'))
        pontos_ref = []
        for feat in source.getFeatures():
            geom = feat.geometry()
            if coordTransf and crs != SRC:
                geom.transform(coordinateTransf)
            pnt = geom.asPoint()
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
        feedback.pushInfo(self.tr('Altimetric calculation...', 'Cálculo das discrepâncias altimétricas...'))
        DISCREP = []
        total = 100.0 / source.featureCount() if source.featureCount() else 0
        for w, feat in enumerate(source.getFeatures()):
            geom = feat.geometry()
            if coordTransf and crs != SRC:
                geom.transform(coordinateTransf)
            pnt = geom.asPoint()
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
            
        
        # Gerar relatorio
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
        arq = open(html_output, 'w')

        texto = '''<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
<html>
<head>
  <meta content="text/html; charset=ISO-8859-1" http-equiv="content-type">
  <title>''' + str2HTML(self.tr('POINT CLOUD POSITIONAL ACCURACY', 'ACURÁCIA POSICIONAL DE NUVEM DE PONTOS')) + '''</title>
  <link rel = "icon" href = "https://github.com/LEOXINGU/lftools/blob/main/images/lftools.png?raw=true" type = "image/x-icon">
  <meta name="qrichtext" content="1">
  <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
</head>
<body style="background-color: rgb(229, 233, 166);">
<div style="text-align: center;"><span style="font-weight: bold;"><br>
    <img height="80" src="data:image/'''+ 'png;base64,' + lftools_logo + '''">
</div>
<div style="text-align: center;"><span style="font-weight: bold; text-decoration: underline;">''' + str2HTML(self.tr('POINT CLOUD POSITIONAL ACCURACY', 'ACURÁCIA POSICIONAL DE NUVEM DE PONTOS')) + '''</span><br>
</div>
<br>
<span style="font-weight: bold;"><br>''' + str2HTML(self.tr('EVALUATED DATA', 'DADOS AVALIADOS')) + '''</span><br>
&nbsp;&nbsp;&nbsp; a. ''' + str2HTML(self.tr('Point Cloud', 'Nuvem de pontos')) + ''': [cloud]<br>
&nbsp;&nbsp;&nbsp; b. ''' + str2HTML(self.tr('Reference Points', 'Pontos de referência')) + ''': [layer_name]<br>
&nbsp;&nbsp;&nbsp; c. ''' + str2HTML(self.tr('Total Number of Homologous Point Pairs', 'Total de pares de pontos homólogos')) + ''': [layer_count]<br>
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
                   '[cloud]': str2HTML(os.path.basename(caminho)),
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
