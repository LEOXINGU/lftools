# -*- coding: utf-8 -*-

"""
***************************************************************************
    Doc_PointsFromText.py
    ---------------------
    Date                 : Jun 12
    Copyright            : (C) 2022 by Leandro França
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
__date__ = 'Jun 12'
__copyright__ = '(C) 2022, Leandro França'

from qgis.PyQt.QtCore import QCoreApplication, QVariant
from qgis.core import (QgsProcessing,
                       QgsApplication,
                       QgsProcessingParameterString,
                       QgsProcessingParameterCrs,
                       QgsProcessingParameterBoolean,
                       QgsFields,
                       QgsWkbTypes,
                       QgsField,
                       QgsFeature,
                       QgsGeometry,
                       QgsPointXY,
                       QgsFeatureSink,
                       QgsProcessingException,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterFeatureSink)

import re, os
from lftools.geocapt.imgs import *
from lftools.geocapt.topogeo import dd2dms, dd2dms
from qgis.PyQt.QtGui import QIcon

class PointsFromText(QgsProcessingAlgorithm):

    RE_NAME = 'RE_NAME'
    RE_X = 'RE_X'
    RE_Y = 'RE_Y'
    TEXT = 'TEXT'
    CRS = 'CRS'
    OUTPUT ='OUTPUT'
    DEC_SEPARATOR = 'DEC_SEPARATOR'

    LOC = QgsApplication.locale()[:2]

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
        return PointsFromText()

    def name(self):
        return 'pointsfromtext'

    def displayName(self):
        return self.tr('Points from Deed Description', 'Reconstituição de Memorial')

    def group(self):
        return self.tr('Documents', 'Documentos')

    def groupId(self):
        return 'documents'

    def tags(self):
        return self.tr('deed,regex,regular,expression,expressão,description,descriptive,memorial,property,topography,surveying,real,estate,georreferencing,plan,cadastral,cadastre,document').split(',')

    def icon(self):
        return QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images/document.png'))

    txt_en = 'Performs the reconstitution of a Deed Description using Regular Expressions (RegEx).'
    txt_pt = 'Realiza a reconstituição de Memorial descritivo utilizando Expressões Regulares (RegEx).'
    figure = 'images/tutorial/doc_pointsFromText.jpg'

    def shortHelpString(self):
        social_BW = Imgs().social_BW
        footer = '''<div align="center">
                      <img src="'''+ os.path.join(os.path.dirname(os.path.dirname(__file__)), self.figure) +'''">
                      </div>
                      <div align="right">
                      <p align="right">
                      <b><a href="https://regex101.com/" target="_blank">'''+ self.tr('Click here for testing your regular expression (RegEx).',
                                    'Clique aqui para testar sua expressão regular (RegEx).') +'</a><br><br>'+ self.tr('Author: Leandro Franca', 'Autor: Leandro França')+'''</b>
                      </p>'''+ social_BW + '''</div>
                    </div>'''
        return self.tr(self.txt_en, self.txt_pt) + footer

    def initAlgorithm(self, config=None):

        self.addParameter(
            QgsProcessingParameterString(
                self.RE_NAME,
                self.tr('RegEx for Vertex Code','RegEx do Código do vértice'),
                defaultValue = r'\w+[\s-]+\d{2,3}'
            )
        )

        self.addParameter(
            QgsProcessingParameterString(
                self.RE_X,
                self.tr('X coordinate RegEx', 'RegEx da coordenada X'),
                defaultValue = self.tr(r'E[\s-]+[\d\,-]+[\d\.-]+[\d]', r'E[\s-]+[\d\.-]+[\d\,-]+[\d]')
            )
        )

        self.addParameter(
            QgsProcessingParameterString(
                self.RE_Y,
                self.tr('X coordinate RegEx', 'RegEx da coordenada Y'),
                defaultValue = self.tr(r'N[\s-]+[\d\,-]+[\d\,-]+[\d\.-]+[\d]', r'N[\s-]+[\d\.-]+[\d\.-]+[\d\,-]+[\d]')
            )
        )

        self.addParameter(
            QgsProcessingParameterCrs(
                self.CRS,
                self.tr('CRS','SRC'),
                'ProjectCrs'))

        self.addParameter(
            QgsProcessingParameterString(
                self.TEXT,
                self.tr('Text','Texto do Memorial Descritivo'),
                multiLine = True
            )
        )

        self.addParameter(
            QgsProcessingParameterBoolean(
            self.DEC_SEPARATOR,
            self.tr('Decimal separator is dot', 'Separador decimal é ponto'),
            defaultValue = False if self.LOC == 'pt' else True
            )
        )

        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT,
                self.tr('Point layer','Vértices do Memorial')
            )
        )


    def processAlgorithm(self, parameters, context, feedback):

        regex_nome = self.parameterAsString(
            parameters,
            self.RE_NAME,
            context
        )

        regex_x = self.parameterAsString(
            parameters,
            self.RE_X,
            context
        )

        regex_y = self.parameterAsString(
            parameters,
            self.RE_Y,
            context
        )

        crs = self.parameterAsCrs(
            parameters,
            self.CRS,
            context
        )

        texto = self.parameterAsString(
            parameters,
            self.TEXT,
            context
        )

        sep_decimal = self.parameterAsBool(
            parameters,
            self.DEC_SEPARATOR,
            context
        )

        Fields = QgsFields()
        itens  = {
                     'ord' : QVariant.Int,
                     self.tr('code') : QVariant.String,
                     self.tr('x') : QVariant.Double,
                     self.tr('y') : QVariant.Double
                     }
        for item in itens:
            Fields.append(QgsField(item, itens[item]))

        (sink, dest_id) = self.parameterAsSink(
            parameters,
            self.OUTPUT,
            context,
            Fields,
            QgsWkbTypes.Point,
            crs
        )
        if sink is None:
            raise QgsProcessingException(self.invalidSinkError(parameters, self.OUTPUT))

        # Eliminando espaços duplos e nova linha no texto
        texto = texto.replace('\n',' ').replace('\t',' ').replace('  ',' ')

        # Extraindo dados
        nm_list = re.findall(regex_nome, texto)
        x_list = re.findall(regex_x, texto)
        y_list = re.findall(regex_y, texto)

        tam_nome = len(nm_list)
        tam_x = len(x_list)
        tam_y = len(y_list)

        # Eliminando \n (nova linha)
        for k in range(tam_nome):
            nm_list[k] = nm_list[k].replace('\n',' ')
        for k in range(tam_x):
            x_list[k] = x_list[k].replace('\n',' ')
        for k in range(tam_y):
            y_list[k] = y_list[k].replace('\n',' ')

        # Validando dados
        if tam_x != tam_nome or tam_y!= tam_nome:
            feedback.pushInfo(self.tr('Códigos:'))
            feedback.pushInfo(self.tr(str(nm_list)))
            feedback.pushInfo(self.tr('Coordenadas X:'))
            feedback.pushInfo(self.tr(str(x_list)))
            feedback.pushInfo(self.tr('Coordenadas Y:'))
            feedback.pushInfo(self.tr(str(y_list)))
            raise QgsProcessingException(self.tr('Error: The number of input values does not match.', 'Erro na quantidade de coordenadas'))

        tam = tam_nome
        feedback.pushInfo(self.tr('Codes and coordinates', 'Código e coordenadas:'))
        for k, nome in enumerate(nm_list):
            feedback.pushInfo(self.tr('{}   {}  {}'.format(nome ,x_list[k], y_list[k])))

        # Removendo caracteres não digito
        lista_X, lista_Y = [],[]
        if sep_decimal:
            for k in range(tam):
                txt = ''
                for s in x_list[k]:
                    if s.isdigit() or s == '.':
                        txt += s
                lista_X += [float(txt)]

                txt = ''
                for s in y_list[k]:
                    if s.isdigit() or s == '.':
                        txt += s
                lista_Y += [float(txt)]
        else:
            for k in range(tam):
                txt = ''
                for s in x_list[k]:
                    if s.isdigit() or s == ',':
                        txt += s
                txt = txt.replace(',','.')
                lista_X += [float(txt)]

                txt = ''
                for s in y_list[k]:
                    if s.isdigit() or s == ',':
                        txt += s
                txt = txt.replace(',','.')
                lista_Y += [float(txt)]

        # Varrer pontos
        feat = QgsFeature()
        total = 100.0 / tam if tam else 0

        for k in range(tam):
            NOME = nm_list[k]
            X = lista_X[k]
            Y = lista_Y[k]
            feat.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(X,Y)))
            feat.setAttributes([k+1, NOME, X, Y])
            sink.addFeature(feat, QgsFeatureSink.FastInsert)
            if feedback.isCanceled():
                break
            feedback.setProgress(int((k+1) * total))

        feedback.pushInfo(self.tr('Operation completed successfully!', 'Operação finalizada com sucesso!'))
        feedback.pushInfo('Leandro França - Eng Cart')

        return {self.OUTPUT: dest_id}
