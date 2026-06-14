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
__date__ = '2026-06-09'
__copyright__ = '(C) 2026, Leandro França'

from qgis.PyQt.QtCore import QMetaType
from qgis.core import *
from numpy import sqrt, array, mean, std, pi, sin
import numpy as np
from datetime import datetime
import base64
from io import BytesIO
from lftools.geocapt.imgs import *
from lftools.translations.translate import translate
from lftools.geocapt.topogeo import str2HTML
from lftools.geocapt.cartography import PEC
import os
from qgis.PyQt.QtGui import QIcon, QColor, QFont
from lftools.dependencies import (
                                    ensure_scipy,
                                    ensure_pyplot
                                )


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
        return self.tr('Quality','Qualidade')

    def groupId(self):
        return 'quality'

    LOC = QgsApplication.locale()[:2]

    def tr(self, *string):
        return translate(string, self.LOC)

    def tags(self):
        return 'GeoOne,PEC,PEC-PCD,qualidade,padrão,rmse,remq,checkpoints,gcps,exactness,point cloud,PC,nuvem de pontos,precision,precisão,tendência,tendency,correctness,accuracy,acurácia,discrepância,discrepancy,vector,deltas,3d,vertical,altimétrico,altimetric,cqdg,asprs'.split(',')

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

        scipy_stats = ensure_scipy(feedback)
        plt = ensure_pyplot(feedback)
        
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
        def fnum(value):
            try:
                return format_num.format(float(value))
            except Exception:
                return str(value)

        
        Fields = source.fields()
        
        itens  = {
                     'pc_distance' : QMetaType.Type.Double,
                     'pc_h' : QMetaType.Type.Double,
                     'pc_discrep_z' : QMetaType.Type.Double
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
        DISTANCES = []
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
            DISTANCES += [float(np.sqrt(distMin))]
            fet = QgsFeature(Fields)
            fet.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(float(nearestPoint[0]),float(nearestPoint[1]))))
            fet.setAttributes(att + [float(np.sqrt(distMin)), float(nearestPoint[2]), float(discrep)])
            sink.addFeature(fet, QgsFeatureSink.FastInsert)
            if feedback.isCanceled():
                break
            feedback.setProgress(int((w+1) * total))
            
        
        # Gerar relatorio
        feedback.pushInfo(self.tr('Generating accuracy report...', 'Gerando relatório de acurácia...'))

        DISCREP = array(DISCREP, dtype=float)
        DISTANCES = array(DISTANCES, dtype=float)

        # Estatísticas de Acurácia
        RMSE = sqrt((DISCREP*DISCREP).sum()/len(DISCREP))
        P68 = np.percentile(np.abs(DISCREP), 68)
        P90 = np.percentile(np.abs(DISCREP), 90)
        P95 = np.percentile(np.abs(DISCREP), 95)
        P99 = np.percentile(np.abs(DISCREP), 99)

        MEDIAN = np.median(DISCREP)
        MAD = np.median(np.abs(DISCREP - MEDIAN))
        NMAD = 1.4826 * MAD

        Q1 = np.percentile(DISCREP, 25)
        Q3 = np.percentile(DISCREP, 75)
        IQR = Q3 - Q1
        OUT_LOW = Q1 - 1.5 * IQR
        OUT_HIGH = Q3 + 1.5 * IQR
        OUTLIERS = ((DISCREP < OUT_LOW) | (DISCREP > OUT_HIGH)).sum()
        OUTLIERS_PERC = 100.0 * OUTLIERS / len(DISCREP)

        # Cálculo do PEC-PCD
        RESULTADOS = {}
        for escala in Escalas:
            mudou = False
            for valor in valores[::-1]:
                EM = PEC[escala]['altim'][valor]['EM']
                EP = PEC[escala]['altim'][valor]['EP']
                if (sum(DISCREP<EM)/len(DISCREP))>0.9 and (RMSE < EP):
                    RESULTADOS[escala] = valor
                    mudou = True
            if not mudou:
                RESULTADOS[escala] = 'R'
        
        feedback.pushInfo('RMSE: {}'.format(round(RMSE,3)))
        for result in RESULTADOS:
            feedback.pushInfo('{} ➜ {}'.format(dicionario[result],RESULTADOS[result]))

        # Testes de Normalidade
        shapiro_text = self.tr('SciPy unavailable', 'SciPy indisponível')
        anderson_text = self.tr('SciPy unavailable', 'SciPy indisponível')
        normality_class = self.tr('Not assessed', 'Não avaliada')
        normality_explanation = self.tr(
            'Normality was not assessed because SciPy is unavailable or the sample size is insufficient.',
            'A normalidade não foi avaliada porque o SciPy está indisponível ou o tamanho da amostra é insuficiente.'
        )

        if scipy_stats is not None and len(DISCREP) >= 3:
            try:
                shapiro = scipy_stats.shapiro(DISCREP)
                if shapiro.pvalue > 0.05:
                    shapiro_result = self.tr('Normality not rejected', 'Normalidade não rejeitada')
                    normality_class = self.tr('Compatible with normality', 'Compatível com normalidade')
                    normality_explanation = self.tr(
                        'The Shapiro-Wilk test did not reject the null hypothesis of normality at the 5% significance level (p > 0.05).',
                        'O teste de Shapiro-Wilk não rejeitou a hipótese nula de normalidade ao nível de significância de 5% (p > 0,05).'
                    )
                else:
                    shapiro_result = self.tr('Normality rejected', 'Normalidade rejeitada')
                    normality_class = self.tr('Non-normal', 'Não normal')
                    normality_explanation = self.tr(
                        'The Shapiro-Wilk test rejected the null hypothesis of normality at the 5% significance level (p ≤ 0.05).',
                        'O teste de Shapiro-Wilk rejeitou a hipótese nula de normalidade ao nível de significância de 5% (p ≤ 0,05).'
                    )
                shapiro_text = 'W = {}, p-value = {} ({})'.format(
                    fnum(shapiro.statistic),
                    fnum(shapiro.pvalue),
                    shapiro_result
                )
            except Exception as e:
                shapiro_text = str(e)

            try:
                anderson = scipy_stats.anderson(DISCREP, dist='norm')
                critical_5 = anderson.critical_values[2]
                ad_result = self.tr('below 5% critical value', 'abaixo do valor crítico de 5%') if anderson.statistic < critical_5 else self.tr('above 5% critical value', 'acima do valor crítico de 5%')
                anderson_text = 'A² = {}, critical 5% = {} ({})'.format(
                    fnum(anderson.statistic),
                    fnum(critical_5),
                    ad_result
                )
            except Exception as e:
                anderson_text = str(e)

        # Gráficos do relatório (Histograma e CDF)
        def FigToBase64(fig):
            buffer = BytesIO()
            fig.savefig(buffer, format='png', dpi=200, bbox_inches='tight')
            buffer.seek(0)
            encoded = base64.b64encode(buffer.read()).decode('utf-8')
            try:
                plt.close(fig)
            except Exception:
                pass
            return encoded

        def ChartUnavailableBlock():
            return '<div class="note">' + str2HTML(self.tr(
                'Charts were not generated because Matplotlib is unavailable in the QGIS Python environment.',
                'Os gráficos não foram gerados porque o Matplotlib não está disponível no ambiente Python do QGIS.'
            )) + '</div>'

        def GenerateHistogramBase64():
            if plt is None:
                return None
            try:
                fig, ax = plt.subplots(figsize=(9, 5.2))

                ax.hist(DISCREP, bins='fd', edgecolor='black', alpha=0.75)

                ax.axvline(DISCREP.mean(), linewidth=2,
                           label='Mean = {} m'.format(fnum(DISCREP.mean())))
                ax.axvline(np.median(DISCREP), linewidth=2, linestyle='--',
                           label='Median = {} m'.format(fnum(np.median(DISCREP))))

                ax.axvline(-RMSE, linewidth=1.5, linestyle=':',
                           label='±RMSEz = {} m'.format(fnum(RMSE)))
                ax.axvline(RMSE, linewidth=1.5, linestyle=':')


                ax.axvline(-P95, linewidth=1.5, linestyle=(0, (5, 5)),
                           label='±P95 = {} m'.format(fnum(P95)))
                ax.axvline(P95, linewidth=1.5, linestyle=(0, (5, 5)))

                ax.set_title(self.tr('Histogram of Vertical Residuals (ΔZ)',
                                     'Histograma dos Resíduos Verticais (ΔZ)'))
                ax.set_xlabel(self.tr('Vertical discrepancy ΔZ (m)',
                                      'Discrepância vertical ΔZ (m)'))
                ax.set_ylabel(self.tr('Frequency', 'Frequência'))
                ax.grid(True, alpha=0.25)
                ax.legend(loc='best')
                fig.tight_layout()
                return FigToBase64(fig)
            except Exception as e:
                if feedback:
                    feedback.reportError(self.tr(
                        'Could not generate histogram: {}',
                        'Não foi possível gerar o histograma: {}'
                    ).format(str(e)))
                return None

        def GenerateCDFBase64():
            if plt is None:
                return None
            try:
                abs_errors = np.sort(np.abs(DISCREP))
                cdf = np.arange(1, len(abs_errors) + 1) / len(abs_errors) * 100.0

                fig, ax = plt.subplots(figsize=(9, 5.2))
                ax.plot(abs_errors, cdf, linewidth=2, label='CDF')

                for p_value, label, level in [
                    (P68, 'P68', 68),
                    (P90, 'P90', 90),
                    (P95, 'P95', 95),
                    (P99, 'P99', 99)
                ]:
                    ax.axvline(p_value, linestyle='--', linewidth=1.4)
                    ax.axhline(level, linestyle=':', linewidth=1.0)
                    ax.annotate('{} = {} m'.format(label, fnum(p_value)),
                                xy=(p_value, level),
                                xytext=(5, 5),
                                textcoords='offset points')


                ax.set_title(self.tr('CDF of Absolute Vertical Errors |ΔZ|',
                                     'CDF dos Erros Verticais Absolutos |ΔZ|'))
                ax.set_xlabel(self.tr('Absolute vertical error |ΔZ| (m)',
                                      'Erro vertical absoluto |ΔZ| (m)'))
                ax.set_ylabel(self.tr('Cumulative percentage (%)',
                                      'Percentual acumulado (%)'))
                ax.set_xlim(left=0)
                ax.set_ylim(0, 100)
                ax.grid(True, alpha=0.25)
                ax.legend(loc='best')
                fig.tight_layout()
                return FigToBase64(fig)
            except Exception as e:
                if feedback:
                    feedback.reportError(self.tr(
                        'Could not generate CDF chart: {}',
                        'Não foi possível gerar o gráfico CDF: {}'
                    ).format(str(e)))
                return None

        histogram_b64 = GenerateHistogramBase64()
        cdf_b64 = GenerateCDFBase64()

        histogram_chart = '<img class="chart-img" src="data:image/png;base64,{}">'.format(histogram_b64) if histogram_b64 else ChartUnavailableBlock()
        cdf_chart = '<img class="chart-img" src="data:image/png;base64,{}">'.format(cdf_b64) if cdf_b64 else ChartUnavailableBlock()
        
        # Criacao do arquivo html com os resultados
        arq = open(html_output, 'w', encoding='utf-8')

        texto = '''<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>''' + str2HTML(self.tr('POINT CLOUD POSITIONAL ACCURACY', 'ACURÁCIA POSICIONAL DE NUVEM DE PONTOS')) + '''</title>
  <link rel = "icon" href = "https://github.com/LEOXINGU/lftools/blob/main/images/lftools.png?raw=true" type = "image/x-icon">
  <script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
  <style>
    body { font-family: Arial, sans-serif; background:#f4f6f0; color:#222; margin:0; padding:0; }
    .page { max-width:1100px; margin:24px auto; background:white; padding:32px; border-radius:12px; box-shadow:0 2px 12px rgba(0,0,0,.12); }
    .header { text-align:center; border-bottom:3px solid #365f2c; padding-bottom:16px; margin-bottom:24px; }
    .header img { height:72px; }
    h1 { color:#274e22; font-size:24px; margin:12px 0 4px 0; }
    h2 { color:#365f2c; font-size:18px; border-bottom:1px solid #ddd; padding-bottom:6px; margin-top:28px; }
    .subtitle { color:#666; font-size:13px; }
    .cards { display:grid; grid-template-columns:repeat(4,1fr); gap:12px; margin:20px 0; }
    .card { background:#eef5ea; border-left:5px solid #365f2c; padding:14px; border-radius:8px; }
    .label { color:#666; font-size:12px; text-transform:uppercase; }
    .big { font-size:22px; font-weight:bold; color:#1f3f1b; margin-top:6px; }
    table { width:100%; border-collapse:collapse; margin:12px 0; font-size:13px; }
    th { background:#365f2c; color:white; padding:8px; text-align:left; }
    td { border:1px solid #ddd; padding:8px; }
    tr:nth-child(even) { background:#f8f8f8; }
    .note { background:#fff8dc; border-left:5px solid #c9a227; padding:12px; margin:12px 0; border-radius:6px; }
    .ok { color:#1f7a1f; font-weight:bold; }
    .warn { color:#b36b00; font-weight:bold; }
    .footer { margin-top:30px; border-top:1px solid #ccc; padding-top:12px; color:#555; font-size:12px; }
    .chart-img { width:100%; max-width:900px; display:block; margin:16px auto 8px auto; border:1px solid #ddd; border-radius:8px; }
  </style>
</head>
<body>
<div class="page">

<div class="header">
  <img src="data:image/''' + 'png;base64,' + lftools_logo + '''">
  <h1>''' + str2HTML(self.tr('POINT CLOUD POSITIONAL ACCURACY REPORT', 'RELATÓRIO DE ACURÁCIA POSICIONAL DE NUVEM DE PONTOS')) + '''</h1>
  <div class="subtitle">LFTools | ASPRS-oriented vertical accuracy assessment | ''' + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + '''</div>
</div>

<div class="cards">
  <div class="card"><div class="label">''' + str2HTML(self.tr('Checkpoints', 'Checkpoints')) + '''</div><div class="big">[layer_count]</div></div>
  <div class="card"><div class="label">RMSE<sub>Z</sub></div><div class="big">[RMSE_Z] m</div></div>
  <div class="card"><div class="label">''' + str2HTML(self.tr('Mean Error', 'Erro médio')) + '''</div><div class="big">[discrepZ_mean] m</div></div>
  <div class="card"><div class="label">P95 |ΔZ|</div><div class="big">[P95] m</div></div>
</div>

<h2>''' + str2HTML(self.tr('1. Evaluated Data', '1. Dados Avaliados')) + '''</h2>
<table>
<tr><th>''' + str2HTML(self.tr('Item', 'Item')) + '''</th><th>''' + str2HTML(self.tr('Value', 'Valor')) + '''</th></tr>
<tr><td>''' + str2HTML(self.tr('Point cloud', 'Nuvem de pontos')) + '''</td><td>[cloud]</td></tr>
<tr><td>''' + str2HTML(self.tr('Reference points', 'Pontos de referência')) + '''</td><td>[layer_name]</td></tr>
<tr><td>''' + str2HTML(self.tr('Number of checkpoints', 'Número de checkpoints')) + '''</td><td>[layer_count]</td></tr>
<tr><td>''' + str2HTML(self.tr('Search radius', 'Raio de busca')) + '''</td><td>[dist_filter] m</td></tr>
<tr><td>''' + str2HTML(self.tr('Coordinate reference system', 'Sistema de referência')) + '''</td><td>[crs]</td></tr>
</table>

<h2>''' + str2HTML(self.tr('2. Methodology', '2. Metodologia')) + '''</h2>
<p>''' + str2HTML(self.tr(
'For each independent checkpoint, the algorithm searches for the nearest point in the point cloud within the defined search radius. The vertical discrepancy is computed as the elevation of the nearest point minus the reference elevation. No interpolation or averaging is applied to the point cloud.',
'Para cada checkpoint independente, o algoritmo procura o ponto mais próximo na nuvem de pontos dentro do raio de busca definido. A discrepância vertical é calculada como a altitude do ponto mais próximo menos a altitude de referência. Nenhuma interpolação ou média é aplicada à nuvem de pontos.'
)) + '''</p>

<div class="note">
$$\Delta Z_i = Z_{test,i} - Z_{reference,i}$$
$$RMSE_z = \\sqrt{\\frac{\\sum_{i=1}^{n}(\\Delta Z_i)^2}{n}}$$
$$MAD = median(|\Delta Z_i - median(\Delta Z)|)$$
$$NMAD = 1.4826 \times MAD$$
$$IQR = Q_3 - Q_1$$
$$Lower\ Limit = Q_1 - 1.5 \times IQR$$
$$Upper\ Limit = Q_3 + 1.5 \times IQR$$
</div>

<h2>''' + str2HTML(self.tr('3. ASPRS-Oriented Vertical Accuracy Summary', '3. Resumo da Acurácia Vertical orientado pela ASPRS')) + '''</h2>
<table>
<tr><th>Metric</th><th>Value</th><th>Description</th></tr>
<tr><td>Mean Error</td><td>[discrepZ_mean] m</td><td>Vertical bias</td></tr>
<tr><td>Standard Deviation</td><td>[discrepZ_std] m</td><td>Residual dispersion</td></tr>
<tr><td>Minimum ΔZ</td><td>[discrepZ_min] m</td><td>Minimum vertical discrepancy</td></tr>
<tr><td>Maximum ΔZ</td><td>[discrepZ_max] m</td><td>Maximum vertical discrepancy</td></tr>
<tr><td>RMSE<sub>Z</sub></td><td>[RMSE_Z] m</td><td>ASPRS primary vertical accuracy metric</td></tr>
</table>

<h2>''' + str2HTML(self.tr('4. Histogram of Residuals', '4. Histograma dos Resíduos')) + '''</h2>
<p>''' + str2HTML(self.tr(
'The histogram presents the distribution of vertical residuals (ΔZ), including the mean, median, RMSEz and P95 indicators.',
'O histograma apresenta a distribuição dos resíduos verticais (ΔZ), incluindo os indicadores de média, mediana, RMSEz e P95.'
)) + '''</p>
[HISTOGRAM_CHART]

<h2>''' + str2HTML(self.tr('5. CDF of Absolute Errors', '5. CDF dos Erros Absolutos')) + '''</h2>
<p>''' + str2HTML(self.tr(
'The cumulative distribution function (CDF) summarizes the percentage of checkpoints whose absolute vertical error is smaller than a given threshold. Percentiles P68, P90, P95 and P99 are highlighted as empirical indicators of the absolute error distribution.',
'A função de distribuição acumulada (CDF) resume o percentual de checkpoints cujo erro vertical absoluto é menor que um determinado limiar. Os percentis P68, P90, P95 e P99 são destacados como indicadores empíricos da distribuição dos erros absolutos.'
)) + '''</p>
[CDF_CHART]
<h2>''' + str2HTML(self.tr('6. Percentile-based Accuracy', '6. Acurácia baseada em Percentis')) + '''</h2>
<table>
<tr><th>Percentile</th><th>|ΔZ|</th></tr>
<tr><td>P68</td><td>[P68] m</td></tr>
<tr><td>P90</td><td>[P90] m</td></tr>
<tr><td>P95</td><td>[P95] m</td></tr>
<tr><td>P99</td><td>[P99] m</td></tr>
</table>

<h2>''' + str2HTML(self.tr('7. Robust Statistics and Outliers', '7. Estatísticas Robustas e Outliers')) + '''</h2>
<table>
<tr><th>Metric</th><th>Value</th></tr>
<tr><td>Median Error</td><td>[median] m</td></tr>
<tr><td>MAD</td><td>[MAD] m</td></tr>
<tr><td>NMAD</td><td>[NMAD] m</td></tr>
<tr><td>IQR Lower Limit</td><td>[OUT_LOW] m</td></tr>
<tr><td>IQR Upper Limit</td><td>[OUT_HIGH] m</td></tr>
<tr><td>Outliers</td><td>[OUTLIERS] ([OUTLIERS_PERC]%)</td></tr>
</table>

<h2>''' + str2HTML(self.tr('8. Residual Normality Assessment', '8. Avaliação da Normalidade dos Resíduos')) + '''</h2>
<table>
<tr><th>Test</th><th>Result</th></tr>
<tr><td>Shapiro-Wilk</td><td>[SHAPIRO]</td></tr>
<tr><td>Anderson-Darling</td><td>[ANDERSON]</td></tr>
<tr><td>''' + str2HTML(self.tr('Classification', 'Classificação')) + '''</td><td>[NORMALITY_CLASS]</td></tr>
</table>
<div class="note">[NORMALITY_EXPLANATION]</div>

<h2>''' + str2HTML(self.tr('9. Point Cloud Sampling Statistics', '9. Estatísticas de Amostragem da Nuvem')) + '''</h2>
<table>
<tr><th>Metric</th><th>Distance</th></tr>
<tr><td>Mean nearest-point distance</td><td>[dist_mean] m</td></tr>
<tr><td>Median nearest-point distance</td><td>[dist_median] m</td></tr>
<tr><td>Minimum nearest-point distance</td><td>[dist_min] m</td></tr>
<tr><td>Maximum nearest-point distance</td><td>[dist_max] m</td></tr>
</table>

<h2>''' + str2HTML(self.tr('10. ASPRS-Oriented Checklist', '10. Checklist orientado pela ASPRS')) + '''</h2>
<table>
<tr><th>Requirement</th><th>Status</th></tr>
<tr><td>Independent checkpoints</td><td class="ok">''' + str2HTML(self.tr('User-defined', 'Definido pelo usuário')) + '''</td></tr>
<tr><td>Minimum 30 checkpoints</td><td>[CHECK_30]</td></tr>
<tr><td>RMSE<sub>Z</sub> reported</td><td class="ok">OK</td></tr>
<tr><td>Residual normality assessed</td><td>[CHECK_NORMALITY]</td></tr>
<tr><td>Outliers reported without automatic removal</td><td class="ok">OK</td></tr>
</table>

<h2>''' + str2HTML(self.tr('11. PEC-PCD Classification', '11. Classificação PEC-PCD')) + '''</h2>
[PEC_Z]

<h2>''' + str2HTML(self.tr('12. Automatic Interpretation', '12. Interpretação Automática')) + '''</h2>
<div class="note">
[INTERPRETATION]
</div>

<div class="footer">
Leandro França 2026<br>
Cartographic Engineer<br>
email: contato@geoone.com.br
</div>

</div>
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
        
        check30 = '<span class="ok">OK</span>' if len(DISCREP) >= 30 else '<span class="warn">Below ASPRS recommendation</span>'
        check_norm = '<span class="ok">OK</span>' if scipy_stats is not None else '<span class="warn">SciPy unavailable</span>'

        # Interpretação automática
        if OUTLIERS == 0:
            outlier_comment_en = 'No IQR-based outliers were detected.'
            outlier_comment_pt = 'Nenhum outlier pelo critério IQR foi detectado.'
        elif OUTLIERS == 1:
            outlier_comment_en = 'One IQR-based outlier was detected and kept in the analysis.'
            outlier_comment_pt = 'Um outlier pelo critério IQR foi detectado e mantido na análise.'
        else:
            outlier_comment_en = '{} IQR-based outliers were detected and kept in the analysis.'.format(int(OUTLIERS))
            outlier_comment_pt = '{} outliers pelo critério IQR foram detectados e mantidos na análise.'.format(int(OUTLIERS))

        interpretation = self.tr(
            (
                'The evaluated point cloud achieved RMSEz = {} m based on {} independent checkpoints. '
                'The mean vertical error was {} m, indicating the vertical bias of the dataset. '
                'The P95 absolute vertical discrepancy was {} m, meaning that 95% of the checkpoints presented |ΔZ| below this value. '
                'Residual normality classification: {}. {} {} '
                'No outliers were automatically removed from the analysis.'
            ).format(
                fnum(RMSE),
                len(DISCREP),
                fnum(DISCREP.mean()),
                fnum(P95),
                normality_class,
                normality_explanation,
                outlier_comment_en
            ),
            (
                'A nuvem de pontos avaliada obteve RMSEz = {} m com base em {} checkpoints independentes. '
                'A média das discrepâncias verticais foi {} m, indicando a tendência vertical do conjunto de dados. '
                'O percentil P95 das discrepâncias verticais absolutas foi {} m, ou seja, 95% dos checkpoints apresentaram |ΔZ| abaixo desse valor. '
                'Classificação da normalidade dos resíduos: {}. {} {} '
                'Nenhum outlier foi removido automaticamente da análise.'
            ).format(
                fnum(RMSE),
                len(DISCREP),
                fnum(DISCREP.mean()),
                fnum(P95),
                normality_class,
                normality_explanation,
                outlier_comment_pt
            )
        )


        valores = {
            '[layer_name]': str2HTML(source.sourceName()),
            '[cloud]': str2HTML(os.path.basename(caminho)),
            '[layer_count]': str(len(DISCREP)),
            '[dist_filter]': fnum(distProx),
            '[crs]': str2HTML(SRC.authid() + ' - ' + SRC.description() if SRC.isValid() else ''),
            '[HISTOGRAM_CHART]': histogram_chart,
            '[CDF_CHART]': cdf_chart,

            '[discrepZ_mean]': fnum(DISCREP.mean()),
            '[discrepZ_std]': fnum(DISCREP.std()),
            '[discrepZ_max]': fnum(DISCREP.max()),
            '[discrepZ_min]': fnum(DISCREP.min()),

            '[RMSE_Z]': fnum(RMSE),
            '[P68]': fnum(P68),
            '[P90]': fnum(P90),
            '[P95]': fnum(P95),
            '[P99]': fnum(P99),

            '[median]': fnum(MEDIAN),
            '[MAD]': fnum(MAD),
            '[NMAD]': fnum(NMAD),
            '[OUT_LOW]': fnum(OUT_LOW),
            '[OUT_HIGH]': fnum(OUT_HIGH),
            '[OUTLIERS]': str(int(OUTLIERS)),
            '[OUTLIERS_PERC]': fnum(OUTLIERS_PERC),

            '[SHAPIRO]': str2HTML(shapiro_text),
            '[ANDERSON]': str2HTML(anderson_text),
            '[NORMALITY_CLASS]': str2HTML(normality_class),
            '[NORMALITY_EXPLANATION]': str2HTML(normality_explanation),

            '[dist_mean]': fnum(DISTANCES.mean()),
            '[dist_median]': fnum(np.median(DISTANCES)),
            '[dist_min]': fnum(DISTANCES.min()),
            '[dist_max]': fnum(DISTANCES.max()),

            '[CHECK_30]': check30,
            '[CHECK_NORMALITY]': check_norm,

            '[PEC_Z]': TabelaPEC(RESULTADOS),
            '[INTERPRETATION]': str2HTML(interpretation),
        }
        
        for valor in valores:
            texto = texto.replace(valor, valores[valor])

        arq.write(texto)
        arq.close()
        
        feedback.pushInfo(self.tr('Operation completed successfully!', 'Operação finalizada com sucesso!'))
        feedback.pushInfo(self.tr('Leandro Franca - Cartographic Engineer', 'Leandro França - Eng Cart'))

        self.SAIDA = dest_id
        self.P68 = P68
        self.P90 = P90
        self.P95 = P95
        self.P99 = P99

        return {self.OUTPUT: dest_id,
                self.HTML: html_output}

    def postProcessAlgorithm(self, context, feedback):

        layer = QgsProcessingUtils.mapLayerFromString(self.SAIDA, context)

        if layer is None or layer.featureCount() == 0:
            return {}

        field = 'pc_discrep_z'

        # Verifica se o campo existe
        if layer.fields().indexFromName(field) == -1:
            return {}

        # Criar simbologia baseada em regras por |ΔZ|
        root_rule = QgsRuleBasedRenderer.Rule(None)

        classes = [
            (
                self.tr('|ΔZ| ≤ P68', '|ΔZ| ≤ P68'),
                'abs("{}") <= {}'.format(field, self.P68),
                '#1a9850',
                2.4
            ),
            (
                self.tr('P68 < |ΔZ| ≤ P90', 'P68 < |ΔZ| ≤ P90'),
                'abs("{}") > {} AND abs("{}") <= {}'.format(field, self.P68, field, self.P90),
                '#91cf60',
                2.6
            ),
            (
                self.tr('P90 < |ΔZ| ≤ P95', 'P90 < |ΔZ| ≤ P95'),
                'abs("{}") > {} AND abs("{}") <= {}'.format(field, self.P90, field, self.P95),
                '#fee08b',
                2.8
            ),
            (
                self.tr('P95 < |ΔZ| ≤ P99', 'P95 < |ΔZ| ≤ P99'),
                'abs("{}") > {} AND abs("{}") <= {}'.format(field, self.P95, field, self.P99),
                '#fc8d59',
                3.0
            ),
            (
                self.tr('|ΔZ| > P99', '|ΔZ| > P99'),
                'abs("{}") > {}'.format(field, self.P99),
                '#d73027',
                3.4
            ),
        ]

        for label, expression, color, size in classes:
            symbol = QgsMarkerSymbol.createSimple({
                'name': 'circle',
                'color': color,
                'outline_color': '0,0,0',
                'outline_style': 'solid',
                'size': str(size),
                'size_unit': 'MM'
            })

            rule = QgsRuleBasedRenderer.Rule(symbol)
            rule.setFilterExpression(expression)
            rule.setLabel(label)
            root_rule.appendChild(rule)

        renderer = QgsRuleBasedRenderer(root_rule)
        layer.setRenderer(renderer)

        # Rotular com discrepância Z
        label_settings = QgsPalLayerSettings()
        label_settings.fieldName = 'round("{}", 3)'.format(field)
        label_settings.isExpression = True
        label_settings.enabled = True

        text_format = QgsTextFormat()
        font = QFont("Arial", 8)
        font.setBold(True)
        text_format.setFont(font)
        text_format.setSize(8)
        text_format.setColor(QColor("white"))

        buffer_settings = QgsTextBufferSettings()
        buffer_settings.setEnabled(True)
        buffer_settings.setSize(0.6)
        buffer_settings.setColor(QColor("black"))
        text_format.setBuffer(buffer_settings)

        label_settings.setFormat(text_format)

        labeling = QgsVectorLayerSimpleLabeling(label_settings)
        layer.setLabeling(labeling)
        layer.setLabelsEnabled(True)

        layer.triggerRepaint()

        return {}