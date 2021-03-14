# -*- coding: utf-8 -*-

"""
***************************************************************************
    Doc_MarkInformation.py
    ---------------------
    Date                 : Jul 10
    Copyright            : (C) 2020 by Leandro França
    Email                : geoleandro.franca@gmail.com
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
__date__ = 'Jul 10'
__copyright__ = '(C) 2020, Leandro França'

from PyQt5.QtCore import QCoreApplication
from qgis.core import (QgsProcessing,
                       QgsFeatureSink,
                       QgsProcessingException,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterString,
                       QgsFeatureRequest,
                       QgsExpression,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterFeatureSink,
                       QgsProcessingParameterFileDestination,
                       QgsApplication,
                       QgsProject,
                       QgsCoordinateTransform,
                       QgsCoordinateReferenceSystem)

import os
from lftools.geocapt.imgs import *
from lftools.geocapt.cartography import CentralMeridian
from lftools.geocapt.topogeo import dd2dms, str2HTML
from qgis.PyQt.QtGui import QIcon

class SurveyMarkDoc(QgsProcessingAlgorithm):

    PONTOREF = 'PONTOREF'
    CODIGO = 'CODIGO'
    HTML = 'HTML'

    LOC = QgsApplication.locale()

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
        return SurveyMarkDoc()

    def name(self):
        return 'surveymarkdoc'

    def displayName(self):
        return self.tr('Geodetic landmark informations', 'Monografia de marco geodésico')

    def group(self):
        return self.tr('Documents', 'Documentos')

    def groupId(self):
        return 'documents'

    def tags(self):
        return self.tr('monograph,mark,geodetic,descriptive,memorial,property,topography,survey,real,estate,georreferencing,plan,cadastral,cadastre,documnt').split(',')

    def icon(self):
        return QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images/document.png'))

    txt_en = 'This tool generates monograph(s) of geodetic landmarks automatically from the "pto_ref_geod_topo_p" layer.'
    txt_pt = 'Esta ferramenta gera monografia(s) de marcos geodésicos de forma automática a partir da camada "pto_ref_geod_topo_p".'
    figure = 'images/tutorial/doc_mark.jpg'

    def shortHelpString(self):
        social_BW = Imgs().social_BW
        footer = '''<div align="center">
                      <img src="'''+ os.path.join(os.path.dirname(os.path.dirname(__file__)), self.figure) +'''">
                      </div>
                      <div align="right">
                      <div>''' + self.tr('This tool works properly only with data in "topogeo" modeling.',
                                         'Esta ferramenta funciona adequadamente com os dados na modelagem "topogeo".') + '''
                      </div>
                      <p align="right">
                      <b><a href="https://www.researchgate.net/publication/346925730_PROPOSICAO_METODOLOGICA_COM_EMPREGO_DE_SOFTWARE_LIVRE_PARA_A_ELABORACAO_DE_DOCUMENTOS_DE_LEVANTAMENTO_TOPOGRAFICO_DE_IMOVEIS_DA_UNIAO_Methodological_proposition_with_the_use_of_free_software_for_the_p" target="_blank">'''+self.tr('Click here for more informations!',
                                    'Clique aqui para saber mais sobre essa modelagem!') +'</a><br><br>'+ self.tr('Author: Leandro Franca', 'Autor: Leandro França')+'''</b>
                      </p>'''+ social_BW + '''</div>
                    </div>'''
        return self.tr(self.txt_en, self.txt_pt) + footer

    def initAlgorithm(self, config=None):

        # 'INPUTS'
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.PONTOREF,
                self.tr('Survey Landmark', 'Marco Geodésico'),
                types=[QgsProcessing.TypeVectorPoint]
            )
        )

        self.addParameter(
            QgsProcessingParameterString(
                self.CODIGO,
                self.tr('Code', 'Código')
            )
        )

        # 'OUTPUTS'
        self.addParameter(
            QgsProcessingParameterFileDestination(
                self.HTML,
                self.tr('Monograph of Geodetic Landmark', 'Monografia de Marco Geodésico'),
                self.tr('HTML files (*.html)')
            )
        )


    def processAlgorithm(self, parameters, context, feedback):

        vertice = self.parameterAsSource(parameters,
                                                     self.PONTOREF,
                                                     context)

        codigo = self.parameterAsString(parameters,
                                                     self.CODIGO,
                                                     context)

        if vertice is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.PONTOREF))
        if codigo is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.CODIGO))


        # Pegando o SRC do Projeto
        SRC = QgsProject.instance().crs().description()

        # Verificando o SRC do Projeto
        if QgsProject.instance().crs().isGeographic():
            raise QgsProcessingException(self.tr('The Project CRS must be projected!', 'O SRC do Projeto deve ser Projetado!'))

        feedback.pushInfo(self.tr('Project CRS is {}.', 'SRC do Projeto é {}.').format(SRC))

        # Transformar Coordenadas de Geográficas para o sistema UTM
        coordinateTransformer = QgsCoordinateTransform()
        coordinateTransformer.setDestinationCrs(QgsProject.instance().crs())
        coordinateTransformer.setSourceCrs(vertice.sourceCrs())

        expr = QgsExpression( "\"codigo\"='{}'".format( codigo ) )
        pnt = False
        for feat in vertice.getFeatures(QgsFeatureRequest( expr )):
            pnt = feat.geometry().asMultiPoint()[0]
            ponto = feat
            break

        # Verificando se o código do marco é válido
        if not pnt:
            erro_txt = self.tr('The survey mark code {} is not valid!'.format(codigo), 'O código do marco {} não é válido!'.format(codigo))
            raise QgsProcessingException(erro_txt)

        # Validando dados de entrada
        Fields = vertice.fields()
        fieldnames = [field.name() for field in Fields]
        for fieldname in fieldnames:
            att = ponto[fieldname]
            if not att or att in ['', ' ']:
                raise QgsProcessingException(self.tr('All attributes of the class "survey_landmark" must be filled!', 'Todos os atributos da classe "pnt_ref_geod_topo" devem ser preenchidos!'))

        # Coordenada em UTM
        pnt_UTM = coordinateTransformer.transform(pnt)

        TEXTO = '''<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
<html>
<head>
  <meta content="text/html; charset=ISO-8859-1" http-equiv="content-type">
  <title>'''+ self.tr('Monograph of Geodetic Landmark',str2HTML('Monografia de Marco Geodésico')) + '''</title>
</head>
<body>
<div style="text-align: center;"><span style="font-weight: bold;">
<img src="data:image/png;base64,'''+ lftools_logo + '''">
<br>'''+ self.tr(str2HTML('CARTOGRAPHY & SURVEYING'), str2HTML('CARTOGRAFIA & AGRIMENSURA')) + '''</span><br style="font-weight: bold;">
<br></div>
<div style="text-align: center;">
<table style="text-align: left; width: 100%;" border="1" cellpadding="1" cellspacing="0">
  <tbody>
    <tr style="font-weight: bold;" align="center">
      <td colspan="5" rowspan="1">'''+ self.tr('MONOGRAPH OF GEODETIC LANDMARK',str2HTML('MONOGRAFIA DE MARCO GEODÉSICO')) + '''</td>
    </tr>
    <tr>
      <td style="text-align: center; font-weight: bold;">'''+ self.tr('CODE',str2HTML('CÓDIGO')) + '''</td>
      <td style="text-align: center; font-weight: bold;">'''+ self.tr('TYPE',str2HTML('TIPO')) + '''</td>
      <td style="text-align: center; font-weight: bold;">'''+ self.tr('PROPERTY',str2HTML('IMÓVEL')) + '''</td>
      <td style="text-align: center; font-weight: bold;">'''+ self.tr('COUNTY',str2HTML('MUNICÍPIO')) + '''</td>
      <td style="text-align: center; font-weight: bold;">'''+ self.tr('STATE',str2HTML('UF')) + '''</td>
    </tr>
    <tr>
      <td style="text-align: center;">[CD]</td>
      <td style="text-align: center;">[TP]</td>
      <td style="text-align: center;">[NI]</td>
      <td style="text-align: center;">[MUN]</td>
      <td style="text-align: center;">[UF]</td>
    </tr>
    <tr>
      <td colspan="5" rowspan="1">'''+ self.tr('Description/Location:',str2HTML('Descrição/Localização:')) + ''': [DESCR]</td>
    </tr>
    <tr>
      <td colspan="5" rowspan="1"></td>
    </tr>
    <tr>
      <td style="text-align: center; font-weight: bold;" colspan="2" rowspan="1">'''+ self.tr('GEODESIC COORDINATES',str2HTML('COORDENADAS GEODÉSICAS')) + '''</td>
      <td style="text-align: center; font-weight: bold;" colspan="2" rowspan="1">'''+ self.tr('FLAT COORDINATES (UTM)',str2HTML('COORDENADAS PLANAS (UTM)')) + '''</td>
      <td style="text-align: center; font-weight: bold;">'''+ self.tr('PRECISIONS (m)',str2HTML('PRECISÕES (m)')) + '''</td>
    </tr>
    <tr>
      <td>'''+ self.tr('Longitude') + ''' <span style="font-family: &quot;Times New Roman&quot;,serif;">(</span><big><big><span style="font-size: 9pt; font-family: &quot;Times New Roman&quot;,serif;">&lambda;</span></big></big><span style="font-family: &quot;Times New Roman&quot;,serif;">)</span></td>
      <td>[LON]</td>
      <td>'''+ self.tr('East',str2HTML('Este')) + '''</td>
      <td>[E] m</td>
      <td><span style="font-size: 9pt; font-family: &quot;Times New Roman&quot;,serif;"></span><big><big><span style="font-size: 9pt; font-family: &quot;Times New Roman&quot;,serif;"></span></big></big><span style="font-family: &quot;Times New Roman&quot;,serif;">&sigma;(</span><big><big><span style="font-size: 9pt; font-family: &quot;Times New Roman&quot;,serif;">&lambda;</span></big></big><span style="font-family: &quot;Times New Roman&quot;,serif;">) &nbsp;= &nbsp;[sigma_x]</span><b><span style="font-size: 9pt; font-family: &quot;Times New Roman&quot;,serif;"></span></b><b><span style="font-size: 9pt; font-family: &quot;Times New Roman&quot;,serif;"></span></b></td>
    </tr>
    <tr>
      <td>'''+ self.tr('Latitude') + ''' <span style="font-family: &quot;Times New Roman&quot;,serif;">(&phi;)</span></td>
      <td>[LAT]</td>
      <td>'''+ self.tr('North',str2HTML('Norte')) + '''</td>
      <td>[N] m</td>
      <td><b><span style="font-size: 9pt; font-family: &quot;Times New Roman&quot;,serif;"></span></b><b><span style="font-size: 9pt; font-family: &quot;Times New Roman&quot;,serif;"></span></b><b><span style="font-size: 9pt; font-family: &quot;Times New Roman&quot;,serif;"></span></b><span style="font-family: &quot;Times New Roman&quot;,serif;">&sigma;(&phi;) = </span><span style="font-family: &quot;Times New Roman&quot;,serif;">[sigma_y]</span></td>
    </tr>
    <tr>
      <td>'''+ self.tr('Elipsoidal Altitude',str2HTML('Altitude Elipsoidal')) + ''' (h)</td>
      <td>[h] m</td>
      <td>'''+ self.tr('CM',str2HTML('MC')) + '''</td>
      <td>[MC]</td>
      <td><b><span style="font-size: 9pt; font-family: &quot;Times New Roman&quot;,serif;"></span></b><b><span style="font-size: 9pt; font-family: &quot;Times New Roman&quot;,serif;"></span></b>&sigma;(h) = <span style="font-family: &quot;Times New Roman&quot;,serif;">[sigma_h]</span></td>
    </tr>
    <tr>
      <td>'''+ self.tr('Orthometric Altitude',str2HTML('Altitude Ortométrica')) + ''' (H)</td>
      <td>[H] m</td>
      <td></td>
      <td></td>
      <td></td>
    </tr>
    <tr>
      <td colspan="5" rowspan="1"></td>
    </tr>
    <tr>
      <td style="font-weight: bold;">'''+ self.tr('EQUIPMENT',str2HTML('EQUIPAMENTO')) + ''':</td>
      <td>[EQP]</td>
      <td style="font-weight: bold; text-align: center;">'''+ self.tr('STEP',str2HTML('ETAPA')) + '''</td>
      <td style="font-weight: bold; text-align: center;">'''+ self.tr('DATE',str2HTML('DATA')) + '''</td>
      <td style="font-weight: bold; text-align: center;">'''+ self.tr('RESPONSIBLE',str2HTML('RESPONSÁVEL')) + '''</td>
    </tr>
    <tr>
      <td style="font-weight: bold;">'''+ self.tr('METHOD',str2HTML('MÉTODO')) + ''':</td>
      <td>[MET]</td>
      <td>'''+ self.tr('Surveying',str2HTML('Levantamento')) + '''</td>
      <td>[LEV_DT]</td>
      <td>[LEV_RESP]</td>
    </tr>
    <tr>
      <td style="font-weight: bold;">'''+ self.tr('REF. BASE(S)',str2HTML('BASE(S) DE REF.')) + ''':</td>
      <td>[BASE]</td>
      <td>'''+ self.tr('Processing',str2HTML('Processamento')) + '''</td>
      <td>[PROC_DT]</td>
      <td>[PROC_RESP]</td>
    </tr>
    <tr>
      <td><span style="font-weight: bold;">SOFTWARE:</span></td>
      <td>[SOFT]</td>
      <td>'''+ self.tr('Monograph',str2HTML('Monografia')) + '''</td>
      <td>[MON_DT]</td>
      <td>[MON_RESP]</td>
    </tr>
    <tr>
      <td colspan="5" rowspan="1"></td>
    </tr>
    <tr>
      <td style="text-align: center;" colspan="2" rowspan="1"><span style="font-weight: bold;">'''+ self.tr('LANDMARK PHOTO',str2HTML('FOTO DO MARCO')) + '''</span></td>
      <td style="text-align: center;" colspan="3" rowspan="1"><span style="font-weight: bold;">'''+ self.tr('AERIAL IMAGE',str2HTML('IMAGEM AÉREA')) + '''</span></td>
    </tr>
    <tr>
      <td style="text-align: center;" colspan="2" rowspan="1"><img style="width: 200px; height: 150px;" alt="marco" src="data:image/jpg;base64,[FOTO_MARCO]"></td>
      <td style="text-align: center;" colspan="3" rowspan="3"><img style="width: 400px; height: 300px;" alt="imagem" src="data:image/jpg;base64,[IMAGEM_AER]"></td>
    </tr>
    <tr style="font-weight: bold;">
      <td style="text-align: center;" colspan="2" rowspan="1">'''+ self.tr('PANORAMIC PHOTO',str2HTML('FOTO PANORÂMICA')) + '''</td>
    </tr>
    <tr align="center">
      <td colspan="2" rowspan="1"><img style="width: 200px; height: 150px;" alt="panoramica" src="data:image/jpg;base64,[FOTO_PAN]"></td>
    </tr>
    <tr>
      <td colspan="5" rowspan="1">Obs.: [OBS]</td>
    </tr>
    <tr>
      <td colspan="5" rowspan="1"></td>
    </tr>
    <tr>
      <td style="text-align: center; font-weight: bold;" colspan="3" rowspan="1">'''+ self.tr('TECHNICAL MANAGER',str2HTML('RESPONSÁVEL TÉCNICO')) + '''</td>
      <td style="text-align: center; font-weight: bold;">'''+ self.tr('PROFESSION/SPECIALIZATION',str2HTML('CONFEA/CREA')) + '''</td>
      <td style="text-align: center; font-weight: bold;">'''+ self.tr('PROFESSIONAL REGISTRATION',str2HTML('CÓD. CRED. INCRA')) + '''</td>
    </tr>
    <tr>
      <td style="text-align: center;" colspan="3" rowspan="1">[REP_TEC]</td>
      <td style="text-align: center;">[CREA]</td>
      <td style="text-align: center;">[COD_INCRA]</td>
    </tr>
  </tbody>
</table>
</div>
</body>
</html>'''

        tipos = {1: 'Atimétrico',
                 2: 'Planimétrico',
                 3: 'Planialtimétrico',
                 4: 'Gravimétrico'}
        metodo = {1: 'PPP', 2: 'Relativo Estático'}


        # Inserindo dados iniciais do levantamento
        itens = {'[CD]': str2HTML(ponto['codigo']),
                '[TP]':  str2HTML(tipos[ponto['tipoptorefgeodtopo']]) ,
                '[NI]':  str2HTML(ponto['imóvel']),
                '[MUN]': str2HTML(ponto['município']),
                '[UF]':  str2HTML(ponto['UF']),
                '[LON]': str2HTML(dd2dms(pnt.x(),4)),
                '[LAT]': str2HTML(dd2dms(pnt.y(),4)),
                '[h]': '{:,.3f}'.format(ponto['altitude']).replace(',', 'X').replace('.', ',').replace('X', '.'),
                '[H]': '{:,.3f}'.format(ponto['altitudeortometrica']).replace(',', 'X').replace('.', ',').replace('X', '.'),
                '[E]': '{:,.3f}'.format(pnt_UTM.x()).replace(',', 'X').replace('.', ',').replace('X', '.'),
                '[N]': '{:,.3f}'.format(pnt_UTM.y()).replace(',', 'X').replace('.', ',').replace('X', '.'),
                '[MC]':  str(CentralMeridian(pnt)),
                '[sigma_x]': '{:,.3f}'.format(ponto['sigma_x']).replace(',', 'X').replace('.', ',').replace('X', '.'),
                '[sigma_y]': '{:,.3f}'.format(ponto['sigma_y']).replace(',', 'X').replace('.', ',').replace('X', '.'),
                '[sigma_h]': '{:,.3f}'.format(ponto['sigma_h']).replace(',', 'X').replace('.', ',').replace('X', '.'),
                '[EQP]':  str2HTML(ponto['equipamento']),
                '[MET]':  str2HTML(metodo[ponto['lev_metodo']]),
                '[BASE]':  str2HTML(ponto['lev_base_ref']),
                '[SOFT]':  str2HTML(ponto['software']),
                '[LEV_DT]': str2HTML(((ponto['lev_data']).toPyDate()).strftime("%d/%m/%Y")),
                '[LEV_RESP]': str2HTML(ponto['lev_resp']),
                '[PROC_DT]': str2HTML(((ponto['proc_data']).toPyDate()).strftime("%d/%m/%Y")),
                '[PROC_RESP]': str2HTML(ponto['proc_resp']),
                '[MON_DT]': str2HTML(((ponto['monografia_data']).toPyDate()).strftime("%d/%m/%Y")),
                '[MON_RESP]': str2HTML(ponto['monografia_resp']),
                '[REP_TEC]':  str2HTML(ponto['Resp_Tecnico']),
                '[CREA]': str2HTML(ponto['CREA']),
                '[COD_INCRA]': str2HTML(ponto['codigo_credenciado']),
                '[DESCR]': str2HTML(ponto['descricao']),
                '[FOTO_MARCO]': img2html_resized(ponto['foto_marco']) if ponto['foto_marco'] else '',
                '[FOTO_PAN]': img2html_resized(ponto['foto_panoramica']) if ponto['foto_panoramica'] else '',
                '[IMAGEM_AER]': img2html_resized(ponto['imagem_aerea']) if ponto['imagem_aerea'] else '',
                '[OBS]': str2HTML(ponto['obs'])
                    }
        for item in itens:
                TEXTO = TEXTO.replace(item, itens[item])


        # Check for cancelation
        if feedback.isCanceled():
            return {}

        output = self.parameterAsFileOutput(parameters, self.HTML, context)
        arq = open(output, 'w')
        arq.write(TEXTO)
        arq.close()

        feedback.pushInfo(self.tr('Operation completed successfully!', 'Operação finalizada com sucesso!'))
        feedback.pushInfo('Leandro França - Eng Cart')

        return {self.HTML: output}
