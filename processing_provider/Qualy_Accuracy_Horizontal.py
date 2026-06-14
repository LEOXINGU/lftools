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
__date__ = '2026-06-12'
__copyright__ = '(C) 2026, Leandro França'

from qgis.PyQt.QtCore import QMetaType
from qgis.PyQt.QtGui import QIcon, QColor, QFont
from qgis.core import *
from numpy import sqrt, array
import numpy as np
from datetime import datetime
import base64
from io import BytesIO
from lftools.geocapt.imgs import *
from lftools.translations.translate import translate
from lftools.geocapt.topogeo import str2HTML
from lftools.geocapt.cartography import PEC
from lftools.dependencies import (
                                    ensure_scipy,
                                    ensure_pyplot
                                )
import os


class Accuracy_Horizontal(QgsProcessingAlgorithm):

    INPUT = 'INPUT'
    OUTPUT = 'OUTPUT'
    HTML = 'HTML'
    DECIMAL = 'DECIMAL'
    CRS = 'CRS'

    def createInstance(self):
        return Accuracy_Horizontal()

    def name(self):
        return 'Accuracy_Horizontal'.lower()

    def displayName(self):
        return self.tr('Horizontal positional accuracy', 'Acurácia posicional planimétrica')

    def group(self):
        return self.tr('Quality','Qualidade')

    def groupId(self):
        return 'quality'
    
    LOC = QgsApplication.locale()[:2]

    def tr(self, *string):
        return translate(string, self.LOC)

    def tags(self):
        return 'GeoOne,PEC,PEC-PCD,qualidade,padrão,rmse,remq,checkpoints,gcps,exactness,precision,precisão,tendência,tendency,correctness,accuracy,acurácia,discrepância,discrepancy,vector,deltas,2d,planimetrico,horizontal,cqdg,asprs,confidence ellipse,elipse de confiança'.split(',')

    def icon(self):
        return QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images/quality.png'))
       
    txt_en = '''This tool evaluates the <b>horizontal (2D) positional accuracy</b> of cartographic and geospatial products from discrepancy vectors.

<b>Outputs</b>
1. Discrepancies in X and Y coordinates, including the horizontal resultant (XY).
2. ASPRS-oriented horizontal accuracy report with RMSE components, RMSEXY, percentile-based indicators, robust statistics, normality tests, confidence ellipses, graphical analyses and PEC-PCD classification.

<b>Input Requirements</b>
- The input layer must consist of lines with two vertices.
- The first vertex corresponds to the test point and the second vertex corresponds to the reference point.'''
    
    txt_pt = '''Esta ferramenta avalia a <b>acurácia posicional horizontal (2D)</b> de produtos cartográficos e geoespaciais a partir de vetores de discrepância.

<b>Saídas</b>
1. Discrepâncias em X e Y, incluindo a resultante horizontal (XY).
2. Relatório de acurácia horizontal orientado à ASPRS com componentes de REMQ, REMQXY, indicadores percentílicos, estatísticas robustas, testes de normalidade, elipses de confiança, análises gráficas e classificação PEC-PCD.

<b>Requisitos de Entrada</b>
- A camada de entrada deve consistir em linhas com dois vértices.
- O primeiro vértice corresponde ao ponto de teste e o segundo vértice corresponde ao ponto de referência.'''
    
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
                self.tr('Discrepancy vectors', 'Vetores de discrepância'),
                [QgsProcessing.TypeVectorLine]
            )
        )

        self.addParameter(
            QgsProcessingParameterCrs(
                self.CRS,
                self.tr('CRS', 'SRC'),
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
                self.HTML,
                self.tr('2D Horizontal Accuracy Report', 'Relatório de Acurácia Horizontal 2D'),
                self.tr('HTML files (*.html)')
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        
        scipy_stats = ensure_scipy(feedback)
        plt = ensure_pyplot(feedback)

        source = self.parameterAsSource(parameters, self.INPUT, context)
        if source is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.INPUT))
        
        decimal = self.parameterAsInt(parameters, self.DECIMAL, context)
        out_CRS = self.parameterAsCrs(parameters, self.CRS, context)
        
        format_num = '{:,.Xf}'.replace('X', str(decimal))
        def fnum(value):
            try:
                return format_num.format(float(value))
            except Exception:
                return str(value)

        Fields = source.fields()
        itens  = {
                     'discrep_x' : QMetaType.Type.Double,
                     'discrep_y' : QMetaType.Type.Double,
                     'discrep_xy' : QMetaType.Type.Double
                     }
        for item in itens:
            Fields.append(QgsField(item, itens[item]))
        
        html_output = self.parameterAsFileOutput(parameters, self.HTML, context)
        
        dicionario = {'0.5k': '1:500', '1k': '1:1.000', '2k': '1:2.000', '5k': '1:5.000', '10k': '1:10.000', '25k': '1:25.000', '50k': '1:50.000', '100k': '1:100.000', '250k': '1:250.000'}
        valores = ['A', 'B', 'C', 'D']
        Escalas = [esc for esc in dicionario]

        num_teste = source.featureCount()
        if num_teste < 4:
            raise QgsProcessingException(self.tr('Insufficient number of features for quality evaluation!', 'Número de feições insuficiente para avaliação de qualidade!'))
          
        msg = self.tr('Define a projected CRS for the calculations!', 'Defina um SRC projetado para os cálculos!')
        coordTransf = False
        crs = source.sourceCrs()
        if out_CRS.isValid():
            if out_CRS.isGeographic():
                raise QgsProcessingException(msg)
            coordinateTransf = QgsCoordinateTransform(crs, out_CRS, QgsProject.instance())
            coordTransf = True
            SRC = out_CRS
        elif crs.isGeographic():
            raise QgsProcessingException(msg)
        else:
            SRC = crs
        
        (sink, dest_id) = self.parameterAsSink(parameters, self.OUTPUT, context, Fields, source.wkbType(), SRC)
        if sink is None:
            raise QgsProcessingException(self.invalidSinkError(parameters, self.OUTPUT))
        
        DISCREP_X = []
        DISCREP_Y = []
        DISCREP_XY = []
        total = 100.0 / source.featureCount() if source.featureCount() else 0
        feedback.pushInfo(self.tr('Horizontal calculation...', 'Cálculo horizontal...'))
        for current, feat in enumerate(source.getFeatures()):
            geom = feat.geometry()
            if coordTransf and crs != SRC:
                geom.transform(coordinateTransf)
            att = feat.attributes()

            if geom.isMultipart():
                lines = geom.asMultiPolyline()
                if not lines or len(lines[0]) < 2:
                    continue
                p_test = lines[0][0]
                p_ref = lines[0][1]
            else:
                line = geom.asPolyline()
                if len(line) < 2:
                    continue
                p_test = line[0]
                p_ref = line[1]

            deltax = p_test.x() - p_ref.x()
            deltay = p_test.y() - p_ref.y()
            discrep_xy = sqrt(deltax**2 + deltay**2)

            DISCREP_X.append(deltax)
            DISCREP_Y.append(deltay)
            DISCREP_XY.append(discrep_xy)

            feature = QgsFeature(Fields)
            feature.setGeometry(geom)
            feature.setAttributes(att + [float(deltax), float(deltay), float(discrep_xy)])
            sink.addFeature(feature, QgsFeatureSink.FastInsert)
            if feedback.isCanceled():
                break
            feedback.setProgress(int((current+1) * total))

        if len(DISCREP_XY) < 4:
            raise QgsProcessingException(self.tr('Insufficient number of valid vectors for quality evaluation!', 'Número insuficiente de vetores válidos para avaliação de qualidade!'))

        DISCREP_X = array(DISCREP_X, dtype=float)
        DISCREP_Y = array(DISCREP_Y, dtype=float)
        DISCREP_XY = array(DISCREP_XY, dtype=float)
        n = len(DISCREP_XY)

        RMSE_X = sqrt(np.mean(DISCREP_X**2))
        RMSE_Y = sqrt(np.mean(DISCREP_Y**2))
        RMSE_XY = sqrt(np.mean(DISCREP_XY**2))

        feedback.pushInfo(self.tr('Planimetric classification...', 'Classificação planimétrica...'))
        RESULTADOS_XY = {}
        for escala in Escalas:
            mudou = False
            for valor in valores[::-1]:
                EM = PEC[escala]['planim'][valor]['EM']
                EP = PEC[escala]['planim'][valor]['EP']
                if (np.sum(DISCREP_XY < EM) / float(n)) > 0.9 and (RMSE_XY < EP):
                    RESULTADOS_XY[escala] = valor
                    mudou = True
            if not mudou:
                RESULTADOS_XY[escala] = 'R'
        feedback.pushInfo('RMSE_XY: {}'.format(fnum(RMSE_XY)))
        for result in RESULTADOS_XY:
            feedback.pushInfo('{} ➜ {}'.format(dicionario[result], RESULTADOS_XY[result]))

        def signed_stats(data):
            data = np.asarray(data, dtype=float)
            med = np.median(data)
            mad = np.median(np.abs(data - med))
            nmad = 1.4826 * mad
            q1 = np.percentile(data, 25)
            q3 = np.percentile(data, 75)
            iqr = q3 - q1
            low = q1 - 1.5 * iqr
            high = q3 + 1.5 * iqr
            out = int(((data < low) | (data > high)).sum())
            out_perc = 100.0 * out / len(data) if len(data) else 0
            return {
                'mean': float(np.mean(data)), 'median': float(med), 'std': float(np.std(data)),
                'min': float(np.min(data)), 'max': float(np.max(data)), 'mad': float(mad),
                'nmad': float(nmad), 'q1': float(q1), 'q3': float(q3), 'iqr': float(iqr),
                'low': float(low), 'high': float(high), 'out': out, 'out_perc': float(out_perc)
            }

        def abs_percentiles(data):
            adata = np.abs(np.asarray(data, dtype=float))
            return {
                'P68': float(np.percentile(adata, 68)),
                'P90': float(np.percentile(adata, 90)),
                'P95': float(np.percentile(adata, 95)),
                'P99': float(np.percentile(adata, 99))
            }

        S_X = signed_stats(DISCREP_X)
        S_Y = signed_stats(DISCREP_Y)
        S_XY = signed_stats(DISCREP_XY)
        P_X = abs_percentiles(DISCREP_X)
        P_Y = abs_percentiles(DISCREP_Y)
        P_XY = abs_percentiles(DISCREP_XY)

        self.P68_XY = P_XY['P68']
        self.P90_XY = P_XY['P90']
        self.P95_XY = P_XY['P95']
        self.P99_XY = P_XY['P99']

        def normality_text(data):
            if scipy_stats is None or len(data) < 3:
                return (self.tr('SciPy unavailable', 'SciPy indisponível'), self.tr('SciPy unavailable', 'SciPy indisponível'), self.tr('Not assessed', 'Não avaliada'))
            try:
                shapiro = scipy_stats.shapiro(data)
                shapiro_class = self.tr('Normality not rejected', 'Normalidade não rejeitada') if shapiro.pvalue > 0.05 else self.tr('Normality rejected', 'Normalidade rejeitada')
                shapiro_txt = 'W = {}, p-value = {} ({})'.format(fnum(shapiro.statistic), fnum(shapiro.pvalue), shapiro_class)
            except Exception as e:
                shapiro_txt = str(e)
                shapiro_class = self.tr('Not assessed', 'Não avaliada')
            try:
                anderson = scipy_stats.anderson(data, dist='norm')
                critical_5 = anderson.critical_values[2]
                ad_class = self.tr('Normality not rejected at 5%', 'Normalidade não rejeitada a 5%') if anderson.statistic < critical_5 else self.tr('Normality rejected at 5%', 'Normalidade rejeitada a 5%')
                anderson_txt = 'A² = {}, critical 5% = {} ({})'.format(fnum(anderson.statistic), fnum(critical_5), ad_class)
            except Exception as e:
                anderson_txt = str(e)
            return (shapiro_txt, anderson_txt, shapiro_class)

        SH_X, AD_X, CLASS_X = normality_text(DISCREP_X)
        SH_Y, AD_Y, CLASS_Y = normality_text(DISCREP_Y)

        def confidence_ellipse_points(dx, dy, level=95, npts=360):
            chi2_values = {68: 2.27887, 90: 4.60517, 95: 5.99146, 99: 9.21034}
            s = chi2_values[level]
            x = np.asarray(dx, dtype=float)
            y = np.asarray(dy, dtype=float)
            center = np.array([np.mean(x), np.mean(y)])
            cov = np.cov(x, y)
            eigvals, eigvecs = np.linalg.eigh(cov)
            order = eigvals.argsort()[::-1]
            eigvals = eigvals[order]
            eigvecs = eigvecs[:, order]
            eigvals = np.maximum(eigvals, 0)
            a, b = np.sqrt(eigvals * s)
            angle = np.arctan2(eigvecs[1, 0], eigvecs[0, 0])
            t = np.linspace(0, 2*np.pi, npts)
            ellipse = np.vstack((a*np.cos(t), b*np.sin(t)))
            R = np.array([[np.cos(angle), -np.sin(angle)], [np.sin(angle), np.cos(angle)]])
            pts = R @ ellipse
            pts[0, :] += center[0]
            pts[1, :] += center[1]
            return pts[0, :], pts[1, :], center, a, b, np.degrees(angle)

        _, _, ellipse_center, ell_a_95, ell_b_95, ell_angle_95 = confidence_ellipse_points(DISCREP_X, DISCREP_Y, 95)
        ell_anisotropy = ell_a_95 / ell_b_95 if ell_b_95 > 0 else np.inf

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

        def GeneratePlanimetricScatterBase64():
            if plt is None:
                return None
            try:
                fig, ax = plt.subplots(figsize=(7.2, 7.2))
                ax.scatter(DISCREP_X, DISCREP_Y, s=28, alpha=0.75, edgecolors='black', linewidths=0.4, label=self.tr('Checkpoints', 'Checkpoints'))
                ax.axhline(0, linewidth=1, linestyle=':', color='black')
                ax.axvline(0, linewidth=1, linestyle=':', color='black')
                ax.scatter([DISCREP_X.mean()], [DISCREP_Y.mean()], marker='x', s=90, linewidths=2.0, label=self.tr('Mean center', 'Centro médio'))
                for level in [68, 90, 95, 99]:
                    ex, ey, _, _, _, _ = confidence_ellipse_points(DISCREP_X, DISCREP_Y, level)
                    ax.plot(ex, ey, linewidth=1.8, label='{}%'.format(level))
                ax.set_aspect('equal', adjustable='datalim')
                ax.set_title(self.tr('Horizontal Error Pattern (ΔX × ΔY)', 'Padrão do Erro Horizontal (ΔX × ΔY)'))
                ax.set_xlabel('ΔX (m)')
                ax.set_ylabel('ΔY (m)')
                ax.grid(True, alpha=0.25)
                ax.legend(loc='best')
                fig.tight_layout()
                return FigToBase64(fig)
            except Exception as e:
                feedback.reportError(self.tr('Could not generate horizontal scatterplot: {}', 'Não foi possível gerar o scatterplot horizontal: {}').format(str(e)))
                return None

        def GenerateComponentBoxplotBase64():
            if plt is None:
                return None
            try:
                fig, ax = plt.subplots(figsize=(7.6, 5.2))
                bp = ax.boxplot([DISCREP_X, DISCREP_Y], labels=['ΔX', 'ΔY'], showmeans=True)
                ax.axhline(0, linewidth=1, linestyle=':', color='black')
                ax.set_title(self.tr('Horizontal Component Residual Distributions', 'Distribuições dos Resíduos por Componente Horizontal'))
                ax.set_ylabel(self.tr('Residual (m)', 'Resíduo (m)'))
                ax.grid(True, axis='y', alpha=0.25)
                ax.legend([bp['medians'][0], bp['means'][0]], ['Median Residual', 'Mean Residual'], loc='upper right', fontsize=9, frameon=True)
                fig.tight_layout()
                return FigToBase64(fig)
            except Exception as e:
                feedback.reportError(self.tr('Could not generate component boxplot: {}', 'Não foi possível gerar o boxplot das componentes: {}').format(str(e)))
                return None

        def GenerateCDFBase64():
            if plt is None:
                return None
            try:
                fig, ax = plt.subplots(figsize=(8.8, 5.2))
                series = [
                    (np.abs(DISCREP_X), '|ΔX|', RMSE_X, P_X['P95']),
                    (np.abs(DISCREP_Y), '|ΔY|', RMSE_Y, P_Y['P95']),
                    (DISCREP_XY, 'DXY', RMSE_XY, P_XY['P95'])
                ]
                for data, label, rmse, p95 in series:
                    abs_errors = np.sort(np.abs(data))
                    cdf = np.arange(1, len(abs_errors) + 1) / len(abs_errors) * 100.0
                    ax.plot(abs_errors, cdf, linewidth=2, label='{} (RMSE = {} m | P95 = {} m)'.format(label, fnum(rmse), fnum(p95)))
                for level in [68, 90, 95, 99]:
                    ax.axhline(level, linestyle=':', linewidth=1.0, color='gray')
                    ax.text(ax.get_xlim()[1], level, 'P{}'.format(level), fontsize=8, va='center')
                ax.set_title(self.tr('CDF of Absolute Horizontal Errors', 'FDA dos Erros Horizontais Absolutos'))
                ax.set_xlabel(self.tr('Absolute error / horizontal resultant (m)', 'Erro absoluto / resultante horizontal (m)'))
                ax.set_ylabel(self.tr('Cumulative percentage (%)', 'Porcentagem acumulada (%)'))
                ax.set_xlim(left=0)
                ax.set_ylim(0, 100)
                ax.grid(True, alpha=0.30)
                ax.legend(loc='best', fontsize=8)
                fig.tight_layout()
                return FigToBase64(fig)
            except Exception as e:
                feedback.reportError(self.tr('Could not generate CDF: {}', 'Não foi possível gerar a FDA: {}').format(str(e)))
                return None

        scatter_b64 = GeneratePlanimetricScatterBase64()
        boxplot_b64 = GenerateComponentBoxplotBase64()
        cdf_b64 = GenerateCDFBase64()
        scatter_chart = '<img class="chart-img" src="data:image/png;base64,{}">'.format(scatter_b64) if scatter_b64 else ChartUnavailableBlock()
        boxplot_chart = '<img class="chart-img" src="data:image/png;base64,{}">'.format(boxplot_b64) if boxplot_b64 else ChartUnavailableBlock()
        cdf_chart = '<img class="chart-img" src="data:image/png;base64,{}">'.format(cdf_b64) if cdf_b64 else ChartUnavailableBlock()

        def TabelaPEC(RESULTADOS):
            tabela = '''<table><tr>'''
            for escala in Escalas:
                tabela += '<th style="text-align:center;">{}</th>'.format(dicionario[escala])
            tabela += '</tr><tr>'
            for escala in Escalas:
                tabela += '<td style="text-align:center;">{}</td>'.format(RESULTADOS[escala])
            tabela += '</tr></table>'
            return tabela

        def component_rows():
            rows = ''
            for metric, key in [
                ('Mean Error (m)', 'mean'), ('Median Error (m)', 'median'), ('Standard Deviation (m)', 'std'),
                ('RMSE (m)', 'rmse'), ('Minimum Error (m)', 'min'), ('Maximum Error (m)', 'max'),
                ('MAD (m)', 'mad'), ('NMAD (m)', 'nmad'), ('P68 |error| (m)', 'P68'), ('P90 |error| (m)', 'P90'),
                ('P95 |error| (m)', 'P95'), ('P99 |error| (m)', 'P99'), ('Outliers (IQR)', 'out')
            ]:
                if key == 'rmse':
                    vals = [fnum(RMSE_X), fnum(RMSE_Y)]
                elif key in ['P68', 'P90', 'P95', 'P99']:
                    vals = [fnum(P_X[key]), fnum(P_Y[key])]
                elif key == 'out':
                    vals = ['{} ({}%)'.format(S_X['out'], fnum(S_X['out_perc'])), '{} ({}%)'.format(S_Y['out'], fnum(S_Y['out_perc']))]
                else:
                    vals = [fnum(S_X[key]), fnum(S_Y[key])]
                rows += '<tr><td>{}</td><td>{}</td><td>{}</td></tr>'.format(metric, vals[0], vals[1])
            return rows

        def resultant_rows():
            rows = ''
            for metric, value in [
                ('RMSEXY (m)', RMSE_XY), ('Mean DXY (m)', S_XY['mean']), ('Median DXY (m)', S_XY['median']),
                ('Minimum DXY (m)', S_XY['min']), ('Maximum DXY (m)', S_XY['max']), ('P68 DXY (m)', P_XY['P68']),
                ('P90 DXY (m)', P_XY['P90']), ('P95 DXY (m)', P_XY['P95']), ('P99 DXY (m)', P_XY['P99'])
            ]:
                rows += '<tr><td>{}</td><td>{}</td></tr>'.format(metric, fnum(value))
            return rows

        normality_table = '''<table>
<tr><th>Component</th><th>Shapiro-Wilk</th><th>Anderson-Darling</th><th>Main classification</th></tr>
<tr><td>ΔX</td><td>{}</td><td>{}</td><td>{}</td></tr>
<tr><td>ΔY</td><td>{}</td><td>{}</td><td>{}</td></tr>
</table>'''.format(str2HTML(SH_X), str2HTML(AD_X), str2HTML(CLASS_X), str2HTML(SH_Y), str2HTML(AD_Y), str2HTML(CLASS_Y))

        check30 = '<span class="ok">OK</span>' if n >= 30 else '<span class="warn">' + str2HTML(self.tr('Below ASPRS recommendation', 'Abaixo da recomendação ASPRS')) + '</span>'
        check_norm = '<span class="ok">OK</span>' if scipy_stats is not None else '<span class="warn">SciPy unavailable</span>'

        bias_xy = sqrt(S_X['mean']**2 + S_Y['mean']**2)
        normal_summary = self.tr('normality was not rejected for ΔX and ΔY', 'a normalidade não foi rejeitada para ΔX e ΔY') if ('not rejected' in CLASS_X and 'not rejected' in CLASS_Y) or ('não rejeitada' in CLASS_X and 'não rejeitada' in CLASS_Y) else self.tr('normality was rejected for at least one horizontal component', 'a normalidade foi rejeitada para pelo menos uma componente horizontal')
        interpretation = self.tr(
            ('The evaluated dataset contains {} horizontal discrepancy vectors. RMSEXY = {} m, with RMSEX = {} m and RMSEY = {} m. The horizontal mean bias is {} m, with mean components ΔX = {} m and ΔY = {} m. The 95% confidence ellipse of horizontal discrepancies has semi-major axis = {} m, semi-minor axis = {} m, rotation angle = {}°, and anisotropy ratio = {}. The P95 horizontal resultant discrepancy was {} m. According to the Shapiro-Wilk criterion, {}. Outliers were identified by the IQR criterion and were not automatically removed from the analysis.').format(n, fnum(RMSE_XY), fnum(RMSE_X), fnum(RMSE_Y), fnum(bias_xy), fnum(S_X['mean']), fnum(S_Y['mean']), fnum(ell_a_95), fnum(ell_b_95), fnum(ell_angle_95), fnum(ell_anisotropy), fnum(P_XY['P95']), normal_summary),
            ('O conjunto avaliado contém {} vetores de discrepância horizontal. REMQXY = {} m, com REMQX = {} m e REMQY = {} m. A tendência média horizontal é {} m, com componentes médias ΔX = {} m e ΔY = {} m. A elipse de confiança de 95% das discrepâncias horizontais possui semieixo maior = {} m, semieixo menor = {} m, ângulo de rotação = {}° e razão de anisotropia = {}. O percentil P95 da resultante horizontal foi {} m. Pelo critério de Shapiro-Wilk, {}. Os outliers foram identificados pelo critério IQR e não foram removidos automaticamente da análise.').format(n, fnum(RMSE_XY), fnum(RMSE_X), fnum(RMSE_Y), fnum(bias_xy), fnum(S_X['mean']), fnum(S_Y['mean']), fnum(ell_a_95), fnum(ell_b_95), fnum(ell_angle_95), fnum(ell_anisotropy), fnum(P_XY['P95']), normal_summary)
        )

        arq = open(html_output, 'w', encoding='utf-8')
        texto = '''<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>''' + str2HTML(self.tr('2D HORIZONTAL POSITIONAL ACCURACY REPORT', 'RELATÓRIO DE ACURÁCIA POSICIONAL HORIZONTAL 2D')) + '''</title>
  <link rel="icon" href="https://github.com/LEOXINGU/lftools/blob/main/images/lftools.png?raw=true" type="image/x-icon">
  <script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
  <style>
    body { font-family: Arial, sans-serif; background:#f4f6f0; color:#222; margin:0; padding:0; }
    .page { max-width:1120px; margin:24px auto; background:white; padding:32px; border-radius:12px; box-shadow:0 2px 12px rgba(0,0,0,.12); }
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
    .chart-img { width:100%; max-width:900px; display:block; margin:16px auto 8px auto; border:1px solid #ddd; border-radius:8px; }
    .footer { margin-top:30px; border-top:1px solid #ccc; padding-top:12px; color:#555; font-size:12px; }
  </style>
</head>
<body>
<div class="page">
<div class="header">
  <img src="data:image/png;base64,'''+ lftools_logo + '''">
  <h1>''' + str2HTML(self.tr('2D HORIZONTAL POSITIONAL ACCURACY REPORT', 'RELATÓRIO DE ACURÁCIA POSICIONAL HORIZONTAL 2D')) + '''</h1>
  <div class="subtitle">LFTools | ASPRS-oriented horizontal accuracy assessment | ''' + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + '''</div>
</div>
<div class="cards">
  <div class="card"><div class="label">''' + str2HTML(self.tr('Vectors', 'Vetores')) + '''</div><div class="big">[N]</div></div>
  <div class="card"><div class="label">RMSE<sub>X</sub></div><div class="big">[RMSE_X] m</div></div>
  <div class="card"><div class="label">RMSE<sub>Y</sub></div><div class="big">[RMSE_Y] m</div></div>
  <div class="card"><div class="label">RMSE<sub>XY</sub></div><div class="big">[RMSE_XY] m</div></div>
</div>
<h2>''' + str2HTML(self.tr('1. Evaluated Data', '1. Dados Avaliados')) + '''</h2>
<table><tr><th>''' + str2HTML(self.tr('Item', 'Item')) + '''</th><th>''' + str2HTML(self.tr('Value', 'Valor')) + '''</th></tr>
<tr><td>''' + str2HTML(self.tr('Discrepancy vectors', 'Vetores de discrepância')) + '''</td><td>[layer_name]</td></tr>
<tr><td>''' + str2HTML(self.tr('Valid horizontal vectors', 'Vetores horizontais válidos')) + '''</td><td>[N]</td></tr>
<tr><td>''' + str2HTML(self.tr('Coordinate reference system', 'Sistema de referência')) + '''</td><td>[crs]</td></tr></table>
<h2>''' + str2HTML(self.tr('2. Methodology', '2. Metodologia')) + '''</h2>
<p>''' + str2HTML(self.tr('For each discrepancy vector, the first vertex is interpreted as the test point and the second vertex as the reference point. Horizontal discrepancies were computed as the test coordinates minus the corresponding reference coordinates.', 'Para cada vetor de discrepância, o primeiro vértice é interpretado como ponto de teste e o segundo vértice como ponto de referência. As discrepâncias horizontais foram calculadas como as coordenadas do ponto de teste menos as coordenadas correspondentes do ponto de referência.')) + '''</p>

<div class="note">
$$\\Delta X_i = X_{test,i} - X_{ref,i}$$
$$\\Delta Y_i = Y_{test,i} - Y_{ref,i}$$
$$D_{XY,i}=\\sqrt{(\\Delta X_i)^2+(\\Delta Y_i)^2}$$
$$RMSE_X = \\sqrt{\\frac{\\sum_{i=1}^{n}(\\Delta X_i)^2}{n}}$$
$$RMSE_Y = \\sqrt{\\frac{\\sum_{i=1}^{n}(\\Delta Y_i)^2}{n}}$$
$$RMSE_{XY}=\\sqrt{RMSE_X^2+RMSE_Y^2}$$
$$MAD = median(|\\Delta_i - median(\\Delta)|)$$
$$NMAD = 1.4826 \\times MAD$$
$$IQR=Q_3-Q_1$$
$$Lower\\ Limit=Q_1-1.5 \\times IQR$$
$$Upper\\ Limit=Q_3+1.5 \\times IQR$$
</div>

<p>''' + str2HTML(self.tr('Confidence ellipses were computed from the variance-covariance matrix of ΔX and ΔY. The ellipse axes are obtained from eigenvalues and eigenvectors, and their size is scaled by Chi-square values with two degrees of freedom for 68%, 90%, 95%, and 99% confidence levels.', 'As elipses de confiança foram calculadas a partir da matriz de variância-covariância de ΔX e ΔY. Os eixos da elipse são obtidos por autovalores e autovetores, e seu tamanho é escalonado por valores da distribuição Qui-quadrado com dois graus de liberdade para os níveis de confiança de 68%, 90%, 95% e 99%.')) + '''</p>
<h2>''' + str2HTML(self.tr('3. Component Accuracy Statistics', '3. Estatísticas de Acurácia por Componente')) + '''</h2><table><tr><th>Statistic</th><th>ΔX</th><th>ΔY</th></tr>[COMPONENT_ROWS]</table>
<h2>''' + str2HTML(self.tr('4. Horizontal Resultant Accuracy Statistics', '4. Estatísticas da Resultante Horizontal')) + '''</h2><table><tr><th>Statistic</th><th>DXY</th></tr>[RESULTANT_ROWS]</table>
<h2>''' + str2HTML(self.tr('5. Residual Normality Assessment', '5. Avaliação da Normalidade dos Resíduos')) + '''</h2>
<p>''' + str2HTML(self.tr('Normality classification is based on the Shapiro-Wilk test at the 5% significance level. Anderson-Darling statistics are reported as complementary indicators, especially for tail-related deviations.', 'A classificação da normalidade é baseada no teste de Shapiro-Wilk ao nível de significância de 5%. As estatísticas de Anderson-Darling são apresentadas como indicadores complementares, especialmente para desvios associados às caudas da distribuição.')) + '''</p>[NORMALITY_TABLE]
<h2>''' + str2HTML(self.tr('6. Horizontal Error Pattern and Confidence Ellipses', '6. Padrão do Erro Horizontal e Elipses de Confiança')) + '''</h2>
<p>''' + str2HTML(self.tr('The scatterplot of ΔX and ΔY shows the directional structure of horizontal discrepancies. Confidence ellipses summarize dispersion, anisotropy and preferential orientation of the horizontal errors.', 'O scatterplot de ΔX e ΔY mostra a estrutura direcional das discrepâncias horizontais. As elipses de confiança resumem a dispersão, anisotropia e orientação preferencial dos erros horizontais.')) + '''</p>
[SCATTER_CHART]<table><tr><th>Ellipse parameter</th><th>Value</th></tr><tr><td>95% semi-major axis</td><td>[ELL_A95] m</td></tr><tr><td>95% semi-minor axis</td><td>[ELL_B95] m</td></tr><tr><td>95% rotation angle</td><td>[ELL_ANGLE95]°</td></tr><tr><td>Anisotropy ratio</td><td>[ELL_ANISO]</td></tr></table>
<h2>''' + str2HTML(self.tr('7. Graphical Distribution Analysis', '7. Análise Gráfica das Distribuições')) + '''</h2>[BOXPLOT_CHART][CDF_CHART]
<h2>''' + str2HTML(self.tr('8. ASPRS-Oriented Checklist', '8. Checklist Orientado à ASPRS')) + '''</h2><table><tr><th>Requirement</th><th>Status</th></tr><tr><td>Independent checkpoints / discrepancy vectors</td><td class="ok">''' + str2HTML(self.tr('User-defined', 'Definido pelo usuário')) + '''</td></tr><tr><td>Minimum 30 checkpoints for horizontal assessment</td><td>[CHECK_30]</td></tr><tr><td>RMSE<sub>X</sub>, RMSE<sub>Y</sub> and RMSE<sub>XY</sub> reported</td><td class="ok">OK</td></tr><tr><td>Residual normality assessed</td><td>[CHECK_NORMALITY]</td></tr><tr><td>Outliers reported without automatic removal</td><td class="ok">OK</td></tr></table>
<h2>''' + str2HTML(self.tr('9. PEC-PCD Classification', '9. Classificação PEC-PCD')) + '''</h2>[PEC_XY]
<h2>''' + str2HTML(self.tr('10. Automatic Interpretation', '10. Interpretação Automática')) + '''</h2><div class="note">[INTERPRETATION]</div>
<div class="footer">Leandro França 2026<br>Cartographic Engineer<br>email: contato@geoone.com.br</div>
</div></body></html>
'''

        valores_replace = {
            '[layer_name]': str2HTML(source.sourceName()), '[N]': str(n), '[crs]': str2HTML(SRC.authid() + ' - ' + SRC.description() if SRC.isValid() else ''),
            '[RMSE_X]': fnum(RMSE_X), '[RMSE_Y]': fnum(RMSE_Y), '[RMSE_XY]': fnum(RMSE_XY),
            '[COMPONENT_ROWS]': component_rows(), '[RESULTANT_ROWS]': resultant_rows(), '[NORMALITY_TABLE]': normality_table,
            '[SCATTER_CHART]': scatter_chart, '[BOXPLOT_CHART]': boxplot_chart, '[CDF_CHART]': cdf_chart,
            '[ELL_A95]': fnum(ell_a_95), '[ELL_B95]': fnum(ell_b_95), '[ELL_ANGLE95]': fnum(ell_angle_95), '[ELL_ANISO]': fnum(ell_anisotropy),
            '[CHECK_30]': check30, '[CHECK_NORMALITY]': check_norm, '[PEC_XY]': TabelaPEC(RESULTADOS_XY), '[INTERPRETATION]': str2HTML(interpretation),
        }
        for key, value in valores_replace.items():
            texto = texto.replace(key, value)

        arq.write(texto)
        arq.close()
        
        feedback.pushInfo(self.tr('Operation completed successfully!', 'Operação finalizada com sucesso!'))
        feedback.pushInfo(self.tr('Leandro Franca - Cartographic Engineer', 'Leandro França - Eng Cart'))
        
        self.SAIDA = dest_id
        return {self.OUTPUT: dest_id, self.HTML: html_output}


    def postProcessAlgorithm(self, context, feedback):
        layer = QgsProcessingUtils.mapLayerFromString(self.SAIDA, context)
        if layer is None or layer.featureCount() == 0:
            return {}

        field = 'discrep_xy'
        if layer.fields().indexFromName(field) == -1:
            return {}

        root_rule = QgsRuleBasedRenderer.Rule(None)
        classes = [
            (self.tr('DXY ≤ P68', 'DXY ≤ P68'), '"{}" <= {}'.format(field, self.P68_XY), '#1a9850'),
            (self.tr('P68 < DXY ≤ P90', 'P68 < DXY ≤ P90'), '"{}" > {} AND "{}" <= {}'.format(field, self.P68_XY, field, self.P90_XY), '#91cf60'),
            (self.tr('P90 < DXY ≤ P95', 'P90 < DXY ≤ P95'), '"{}" > {} AND "{}" <= {}'.format(field, self.P90_XY, field, self.P95_XY), '#fee08b'),
            (self.tr('P95 < DXY ≤ P99', 'P95 < DXY ≤ P99'), '"{}" > {} AND "{}" <= {}'.format(field, self.P95_XY, field, self.P99_XY), '#fc8d59'),
            (self.tr('DXY > P99', 'DXY > P99'), '"{}" > {}'.format(field, self.P99_XY), '#d73027'),
        ]

        for label, expression, color in classes:
            arrow = QgsArrowSymbolLayer()
            arrow.setArrowWidth(4.0)
            arrow.setArrowStartWidth(0.6)
            arrow.setHeadLength(5.9)
            arrow.setHeadThickness(4.5)
            arrow.setColor(QColor(color))
            symbol = QgsLineSymbol()
            symbol.changeSymbolLayer(0, arrow)
            rule = QgsRuleBasedRenderer.Rule(symbol)
            rule.setFilterExpression(expression)
            rule.setLabel(label)
            root_rule.appendChild(rule)

        renderer = QgsRuleBasedRenderer(root_rule)
        layer.setRenderer(renderer)

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
