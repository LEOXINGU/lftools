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
                       QgsProcessingParameterFile,
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
from lftools.translations.translate import translate
from lftools.geocapt.cartography import CentralMeridian, FusoHemisf
from lftools.geocapt.topogeo import dd2dms, str2HTML
from qgis.PyQt.QtGui import QIcon

class SurveyMarkDoc(QgsProcessingAlgorithm):

    PONTOREF = 'PONTOREF'
    CODIGO = 'CODIGO'
    HTML = 'HTML'
    LOGO = 'LOGO'
    SLOGAN = 'SLOGAN'

    LOC = QgsApplication.locale()[:2]

    def tr(self, *string):
        return translate(string, self.LOC)

    def createInstance(self):
        return SurveyMarkDoc()

    def name(self):
        return 'surveymarkdoc'

    def displayName(self):
        return self.tr('Geodetic mark report', 'Monografia de marco geodésico')

    def group(self):
        return self.tr('Documents', 'Documentos')

    def groupId(self):
        return 'documents'

    def tags(self):
        return self.tr('monograph,mark,report,geodetic,descriptive,memorial,property,topography,survey,real,estate,georreferencing,plan,cadastral,cadastre,document').split(',')

    def icon(self):
        return QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images/document.png'))

    txt_en = 'This tool generates report(s) with the informations about a geodetic landmarks automatically from the "reference_point_p" layer.'
    txt_pt = 'Esta ferramenta gera monografia(s) de marcos geodésicos de forma automática a partir da camada "reference_point_p".'
    figure = 'images/tutorial/doc_mark.jpg'

    def shortHelpString(self):
        social_BW = Imgs().social_BW
        footer = '''<div align="center">
                      <img src="'''+ os.path.join(os.path.dirname(os.path.dirname(__file__)), self.figure) +'''">
                      </div>
                      <div align="right">
                      <div>''' + self.tr('This tool works properly only with data in "TopoGeo" modeling.',
                                         'Esta ferramenta funciona adequadamente com os dados na modelagem "TopoGeo".') + '''
                      </div>
                      <p align="right">
                      <b><a href="'''+ self.tr('https://www.researchgate.net/publication/356911797_TopoGeo_a_data_model_for_elaboration_of_cadastral_survey_plans_and_land_register_documents',
                      'https://geoone.com.br/ebook_gratis/') + '''" target="_blank">'''+ self.tr('Click here for understanding this data model.',
                                    'Clique aqui para entender esse modelo de dados') +'</a><br><br>'+ self.tr('Author: Leandro Franca', 'Autor: Leandro França')+'''</b>
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

        self.addParameter(
            QgsProcessingParameterFile(
                self.LOGO,
                self.tr('Logo (JPEG)', 'Logomarca (JPEG)'),
                behavior=QgsProcessingParameterFile.File,
                defaultValue=None,
                fileFilter = 'Image (*.jpeg *.jpg *.JPG)',
                optional = True
            )
        )

        self.addParameter(
            QgsProcessingParameterString(
                self.SLOGAN,
                self.tr('Slogan'),
                defaultValue = self.tr('CARTOGRAPHY & SURVEYING', 'CARTOGRAFIA & AGRIMENSURA'),
                optional = True,
                multiLine = True
            )
        )

        # 'OUTPUTS'
        self.addParameter(
            QgsProcessingParameterFileDestination(
                self.HTML,
                self.tr('Geodetic Landmark Report', 'Monografia de Marco Geodésico'),
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

        logo = self.parameterAsFile(
            parameters,
            self.LOGO,
            context
        )
        if logo:
            LOGO = 'jpg;base64,'+img2html_resized(logo, lado=380)
        else:
            LOGO = 'png;base64,'+lftools_logo

        SLOGAN = self.parameterAsString(
            parameters,
            self.SLOGAN,
            context
        )
        if not SLOGAN:
            SLOGAN = ''
        else:
            SLOGAN = SLOGAN.replace('\n', '<br>')

        # Pegando o SRC do Projeto
        SRC = QgsProject.instance().crs().description()

        # Verificando o SRC do Projeto
        if QgsProject.instance().crs().isGeographic():
            raise QgsProcessingException(self.tr('The Project CRS must be projected!', 'O SRC do Projeto deve ser Projetado!'))

        feedback.pushInfo(self.tr('Project CRS is {}.', 'SRC do Projeto é {}.').format(SRC))

        # Verificar se a projeção UTM do Projeto está correta
        for feat in vertice.getFeatures():
                geom = feat.geometry()
                break
        fuso, hemisf = FusoHemisf(geom.asMultiPoint()[0] if geom.isMultipart() else geom.asPoint())
        if SRC.split(' ')[-1] != str(fuso)+hemisf :
            raise QgsProcessingException(self.tr('Warning: Make sure your projection is correct!'.upper(), 'Aviso: Verifique se sua projeção está correta!'.upper()))

        # Transformar Coordenadas de Geográficas para o sistema UTM
        coordinateTransformer = QgsCoordinateTransform()
        coordinateTransformer.setDestinationCrs(QgsProject.instance().crs())
        coordinateTransformer.setSourceCrs(vertice.sourceCrs())

        expr = QgsExpression( "\"code\"='{}'".format( codigo ) )
        pnt = False
        for feat in vertice.getFeatures(QgsFeatureRequest( expr )):
            pnt = feat.geometry().asMultiPoint()[0]
            ponto = feat
            break

        # Verificando se o código do marco é válido
        if not pnt:
            erro_txt = self.tr('The survey mark code {} is not valid!', 'O código do marco {} não é válido!').format(codigo)
            raise QgsProcessingException(erro_txt)

        # Validando coordenadas geodésicas da camada de entrada
        if pnt.x() < -180 or pnt.x() > 180 or pnt.y() < -90 or pnt.y() > 90:
            raise QgsProcessingException(self.tr('Input coordinates must be geodetic (longitude and latitude)!', 'As coordenadas de entrada devem ser geodésicas (longitude e latitude)!'))

        # Validando dados de entrada
        Fields = vertice.fields()
        fieldnames = [field.name() for field in Fields]
        for fieldname in fieldnames:
            att = ponto[fieldname]
            if fieldname not in ['survey_ref_base']:
                if not att or att in ['', ' ']:
                    raise QgsProcessingException(self.tr('The attributes of the class "reference_point_p" must be filled!', 'Os atributos da classe "Ponto de Referência Geodésica" devem ser preenchidos!'))

        # Coordenada em UTM
        pnt_UTM = coordinateTransformer.transform(pnt)

        TEXTO = '''<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
<html>
<head>
  <meta content="text/html; charset=ISO-8859-1" http-equiv="content-type">
  <title>'''+ str2HTML(self.tr('Monograph of Geodetic Landmark','Monografia de Marco Geodésico')) + '''</title>
  <link rel = "icon" href = "https://github.com/LEOXINGU/lftools/blob/main/images/lftools.png?raw=true" type = "image/x-icon">
</head>
<body>
<div style="text-align: center;"><span style="font-weight: bold;">
<img height="80" src="data:image/'''+ LOGO + '''">
<br>'''+ str2HTML(SLOGAN) + '''</span><br style="font-weight: bold;">
<br></div>
<div style="text-align: center;">
<table style="text-align: left; width: 100%;" border="1" cellpadding="1" cellspacing="0">
  <tbody>
    <tr style="font-weight: bold;" align="center">
      <td colspan="5" rowspan="1">'''+ str2HTML(self.tr('MONOGRAPH OF GEODETIC LANDMARK','MONOGRAFIA DE MARCO GEODÉSICO')) + '''</td>
    </tr>
    <tr>
      <td style="text-align: center; font-weight: bold;">'''+ str2HTML(self.tr('CODE','CÓDIGO')) + '''</td>
      <td style="text-align: center; font-weight: bold;">'''+ str2HTML(self.tr('TYPE','TIPO')) + '''</td>
      <td style="text-align: center; font-weight: bold;">'''+ str2HTML(self.tr('PROPERTY','IMÓVEL')) + '''</td>
      <td style="text-align: center; font-weight: bold;">'''+ str2HTML(self.tr('COUNTY','MUNICÍPIO')) + '''</td>
      <td style="text-align: center; font-weight: bold;">'''+ str2HTML(self.tr('STATE','UF')) + '''</td>
    </tr>
    <tr>
      <td style="text-align: center;">[CD]</td>
      <td style="text-align: center;">[TP]</td>
      <td style="text-align: center;">[NI]</td>
      <td style="text-align: center;">[MUN]</td>
      <td style="text-align: center;">[UF]</td>
    </tr>
    <tr>
      <td colspan="5" rowspan="1">'''+ str2HTML(self.tr('Description/Location:','Descrição/Localização:')) + ''': [DESCR]</td>
    </tr>
    <tr>
      <td colspan="5" rowspan="1"></td>
    </tr>
    <tr>
      <td style="text-align: center; font-weight: bold;" colspan="2" rowspan="1">'''+ str2HTML(self.tr('GEODESIC COORDINATES','COORDENADAS GEODÉSICAS')) + '''</td>
      <td style="text-align: center; font-weight: bold;" colspan="2" rowspan="1">'''+ str2HTML(self.tr('FLAT COORDINATES (UTM)','COORDENADAS PLANAS (UTM)')) + '''</td>
      <td style="text-align: center; font-weight: bold;">'''+ str2HTML(self.tr('PRECISIONS (m)','PRECISÕES (m)')) + '''</td>
    </tr>
    <tr>
      <td>'''+ self.tr('Longitude') + ''' <span style="font-family: &quot;Times New Roman&quot;,serif;">(</span><big><big><span style="font-size: 9pt; font-family: &quot;Times New Roman&quot;,serif;">&lambda;</span></big></big><span style="font-family: &quot;Times New Roman&quot;,serif;">)</span></td>
      <td>[LON]</td>
      <td>'''+ str2HTML(self.tr('East','Este')) + '''</td>
      <td>[E] m</td>
      <td><span style="font-size: 9pt; font-family: &quot;Times New Roman&quot;,serif;"></span><big><big><span style="font-size: 9pt; font-family: &quot;Times New Roman&quot;,serif;"></span></big></big><span style="font-family: &quot;Times New Roman&quot;,serif;">&sigma;(</span><big><big><span style="font-size: 9pt; font-family: &quot;Times New Roman&quot;,serif;">&lambda;</span></big></big><span style="font-family: &quot;Times New Roman&quot;,serif;">) &nbsp;= &nbsp;[sigma_x]</span><b><span style="font-size: 9pt; font-family: &quot;Times New Roman&quot;,serif;"></span></b><b><span style="font-size: 9pt; font-family: &quot;Times New Roman&quot;,serif;"></span></b></td>
    </tr>
    <tr>
      <td>'''+ self.tr('Latitude') + ''' <span style="font-family: &quot;Times New Roman&quot;,serif;">(&phi;)</span></td>
      <td>[LAT]</td>
      <td>'''+ str2HTML(self.tr('North','Norte')) + '''</td>
      <td>[N] m</td>
      <td><b><span style="font-size: 9pt; font-family: &quot;Times New Roman&quot;,serif;"></span></b><b><span style="font-size: 9pt; font-family: &quot;Times New Roman&quot;,serif;"></span></b><b><span style="font-size: 9pt; font-family: &quot;Times New Roman&quot;,serif;"></span></b><span style="font-family: &quot;Times New Roman&quot;,serif;">&sigma;(&phi;) = </span><span style="font-family: &quot;Times New Roman&quot;,serif;">[sigma_y]</span></td>
    </tr>
    <tr>
      <td>'''+ str2HTML(self.tr('Elipsoidal Altitude','Altitude Elipsoidal')) + ''' (h)</td>
      <td>[h] m</td>
      <td>'''+ str2HTML(self.tr('CM','MC')) + '''</td>
      <td>[MC]</td>
      <td><b><span style="font-size: 9pt; font-family: &quot;Times New Roman&quot;,serif;"></span></b><b><span style="font-size: 9pt; font-family: &quot;Times New Roman&quot;,serif;"></span></b>&sigma;(h) = <span style="font-family: &quot;Times New Roman&quot;,serif;">[sigma_h]</span></td>
    </tr>
    <tr>
      <td>'''+ str2HTML(self.tr('Orthometric Altitude','Altitude Ortométrica')) + ''' (H)</td>
      <td>[H] m</td>
      <td style="text-align: center;" colspan="3" rowspan="1"><span style="font-weight: bold;">[SRC]</td>
    </tr>
    <tr>
      <td colspan="5" rowspan="1"></td>
    </tr>
    <tr>
      <td style="font-weight: bold;">'''+ str2HTML(self.tr('EQUIPMENT','EQUIPAMENTO')) + ''':</td>
      <td>[EQP]</td>
      <td style="font-weight: bold; text-align: center;">'''+ str2HTML(self.tr('STEP','ETAPA')) + '''</td>
      <td style="font-weight: bold; text-align: center;">'''+ str2HTML(self.tr('DATE','DATA')) + '''</td>
      <td style="font-weight: bold; text-align: center;">'''+ str2HTML(self.tr('RESPONSIBLE','RESPONSÁVEL')) + '''</td>
    </tr>
    <tr>
      <td style="font-weight: bold;">'''+ str2HTML(self.tr('METHOD','MÉTODO')) + ''':</td>
      <td>[MET]</td>
      <td>'''+ str2HTML(self.tr('Surveying','Levantamento')) + '''</td>
      <td>[LEV_DT]</td>
      <td>[LEV_RESP]</td>
    </tr>
    <tr>
      <td style="font-weight: bold;">'''+ str2HTML(self.tr('REF. BASE(S)','BASE(S) DE REF.')) + ''':</td>
      <td>[BASE]</td>
      <td>'''+ str2HTML(self.tr('Processing','Processamento')) + '''</td>
      <td>[PROC_DT]</td>
      <td>[PROC_RESP]</td>
    </tr>
    <tr>
      <td><span style="font-weight: bold;">SOFTWARE:</span></td>
      <td>[SOFT]</td>
      <td>'''+ str2HTML(self.tr('Monograph','Monografia')) + '''</td>
      <td>[MON_DT]</td>
      <td>[MON_RESP]</td>
    </tr>
    <tr>
      <td colspan="5" rowspan="1"></td>
    </tr>
    <tr>
      <td style="text-align: center;" colspan="2" rowspan="1"><span style="font-weight: bold;">'''+ str2HTML(self.tr('LANDMARK PHOTO','FOTO DO MARCO')) + '''</span></td>
      <td style="text-align: center;" colspan="3" rowspan="1"><span style="font-weight: bold;">'''+ str2HTML(self.tr('AERIAL IMAGE','IMAGEM AÉREA')) + '''</span></td>
    </tr>
    <tr>
      <td style="text-align: center;" colspan="2" rowspan="1"><img style="width: 200px; height: 150px;" alt="marco" src="data:image/jpg;base64,[FOTO_MARCO]"></td>
      <td style="text-align: center;" colspan="3" rowspan="3"><img style="width: 400px;" alt="imagem" src="data:image/jpg;base64,[IMAGEM_AER]"></td>
    </tr>
    <tr style="font-weight: bold;">
      <td style="text-align: center;" colspan="2" rowspan="1">'''+ str2HTML(self.tr('PANORAMIC PHOTO','FOTO PANORÂMICA')) + '''</td>
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
      <td style="text-align: center; font-weight: bold;" colspan="3" rowspan="1">'''+ str2HTML(self.tr('TECHNICAL MANAGER','RESPONSÁVEL TÉCNICO')) + '''</td>
      <td style="text-align: center; font-weight: bold;">'''+ str2HTML(self.tr('PROFESSION/SPECIALIZATION','CONFEA/CREA')) + '''</td>
      <td style="text-align: center; font-weight: bold;">'''+ str2HTML(self.tr('PROFESSIONAL REGISTRATION','CÓD. CRED. INCRA')) + '''</td>
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
        try:
            itens = {'[CD]': str2HTML(ponto['code']),
                    '[TP]':  str2HTML(tipos[ponto['type']]) ,
                    '[NI]':  str2HTML(ponto['property']),
                    '[MUN]': str2HTML(ponto['county']),
                    '[UF]':  str2HTML(ponto['state']),
                    '[LON]': str2HTML(self.tr(dd2dms(pnt.x(),5), dd2dms(pnt.x(),5).replace('.',','))),
                    '[LAT]': str2HTML(self.tr(dd2dms(pnt.y(),5), dd2dms(pnt.y(),5).replace('.',','))),
                    '[h]': self.tr('{:,.3f}'.format(ponto['ellip_height']), '{:,.3f}'.format(ponto['ellip_height']).replace(',', 'X').replace('.', ',').replace('X', '.')),
                    '[H]': self.tr('{:,.3f}'.format(ponto['ortho_height']), '{:,.3f}'.format(ponto['ortho_height']).replace(',', 'X').replace('.', ',').replace('X', '.')),
                    '[E]': self.tr('{:,.3f}'.format(pnt_UTM.x()), '{:,.3f}'.format(pnt_UTM.x()).replace(',', 'X').replace('.', ',').replace('X', '.')),
                    '[N]': self.tr('{:,.3f}'.format(pnt_UTM.y()), '{:,.3f}'.format(pnt_UTM.y()).replace(',', 'X').replace('.', ',').replace('X', '.')),
                    '[MC]':  str2HTML(str(CentralMeridian(pnt))),
                    '[sigma_x]': self.tr('{:,.3f}'.format(ponto['sigma_x']), '{:,.3f}'.format(ponto['sigma_x']).replace(',', 'X').replace('.', ',').replace('X', '.')),
                    '[sigma_y]': self.tr('{:,.3f}'.format(ponto['sigma_y']), '{:,.3f}'.format(ponto['sigma_y']).replace(',', 'X').replace('.', ',').replace('X', '.')),
                    '[sigma_h]': self.tr('{:,.3f}'.format(ponto['sigma_h']), '{:,.3f}'.format(ponto['sigma_h']).replace(',', 'X').replace('.', ',').replace('X', '.')),
                    '[EQP]':  str2HTML(ponto['equipment']),
                    '[MET]':  str2HTML(metodo[ponto['survey_method']]),
                    '[BASE]':  str2HTML(ponto['survey_ref_base']),
                    '[SOFT]':  str2HTML(ponto['software']),
                    '[LEV_DT]': str2HTML(self.tr((ponto['survey_date']).toPyDate().isoformat(), (ponto['survey_date']).toPyDate().strftime("%d/%m/%Y"))),
                    '[LEV_RESP]': str2HTML(ponto['survey_resp']),
                    '[PROC_DT]': str2HTML(self.tr((ponto['processing_date']).toPyDate().isoformat(), (ponto['processing_date']).toPyDate().strftime("%d/%m/%Y"))),
                    '[PROC_RESP]': str2HTML(ponto['processing_resp']),
                    '[MON_DT]': str2HTML(self.tr((ponto['report_date']).toPyDate().isoformat(), (ponto['report_date']).toPyDate().strftime("%d/%m/%Y"))),
                    '[MON_RESP]': str2HTML(ponto['report_resp']),
                    '[REP_TEC]':  str2HTML(ponto['tech_manager']),
                    '[CREA]': str2HTML(ponto['profession']),
                    '[COD_INCRA]': str2HTML(ponto['profession_id']),
                    '[DESCR]': str2HTML(ponto['description']),
                    '[OBS]': str2HTML(ponto['observation']),
                    '[SRC]': self.tr(SRC, SRC.replace('zone', 'fuso'))
                        }
        except:
            raise QgsProcessingException(self.tr('Check that your layer "reference_point_p" has the correct field names for the TopoGeo model! More information: https://bit.ly/3FDNQGC', 'Verifique se sua camada "Ponto de Referência Geodésica" está com os nomes dos campos corretos para o modelo TopoGeo! Mais informações: https://geoone.com.br/ebook_gratis/'))

        try:
            itens['[FOTO_MARCO]'] = img2html_resized(ponto['mark_photo']) if ponto['mark_photo'] else ''
        except:
            raise QgsProcessingException(self.tr('Make sure the landmark photo is in JPEG format!', 'Verifique se a foto do marco está no formato JPEG!'))

        try:
            itens['[FOTO_PAN]'] = img2html_resized(ponto['pan_photo']) if ponto['pan_photo'] else ''
        except:
            raise QgsProcessingException(self.tr('Make sure the panoramic photo is in JPEG format!', 'Verifique se a foto panorâmica está no formato JPEG!'))

        try:
            itens['[IMAGEM_AER]'] = img2html_resized(ponto['aerial_image']) if ponto['aerial_image'] else ''
        except:
            raise QgsProcessingException(self.tr('Make sure your aerial sketch is in JPEG format!', 'Verifique se o seu croqui aéreo está no formato JPEG!'))


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
