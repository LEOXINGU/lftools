# -*- coding: utf-8 -*-

"""
Easy_exportASCII.py
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
__date__ = '2023-08-22'
__copyright__ = '(C) 2023, Leandro França'

from PyQt5.QtCore import QCoreApplication, QVariant
from qgis.core import *
import qgis.utils
from numpy import radians, array, sin, cos, sqrt, matrix, zeros, floor, identity, diag
from numpy.linalg import pinv, norm
from lftools.geocapt.imgs import Imgs
from lftools.geocapt.topogeo import str2HTML, String2CoordList, String2StringList, dms2dd
import os, subprocess
from qgis.PyQt.QtGui import QIcon

class ExportASCII(QgsProcessingAlgorithm):

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
        return ExportASCII()

    def name(self):
        return 'ExportASCII'.lower()

    def displayName(self):
        return self.tr('Export expression as ASCII', 'Exportar expressão como ASCII')

    def group(self):
        return self.tr('Easy', 'Mão na roda')

    def groupId(self):
        return 'easy'

    def tags(self):
        return self.tr('mão na roda,easy,fácil,ASCII,atributos,attributes,expressions,expressão,concatenar,concatenate,functions,funções').split(',')

    def icon(self):
        return QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images/easy.png'))

    txt_en = 'This tool exports one or several files in standard text file (ASCII) based on an expression considering the attributes of a layer.'
    txt_pt = 'Esta ferramenta exporta um ou vários arquivos no padrão de arquivo texto (ASCII) baseada em uma expressão considerando os atributos de uma camada.'
    figure = 'images/tutorial/easy_expr_ascii.jpg'

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

    LAYER = 'LAYER'
    ATT = 'ATT' # nome para o arquivo
    EXPR = 'EXPR' # expressão para ser salva
    UNIQUE = 'UNIQUE' # arquivo único
    ORDER = 'ORDER' # campo de ordenação
    FORMAT = 'FORMAT' # formato de saída
    FOLDER = 'FOLDER' # pasta de saída

    def initAlgorithm(self, config=None):

        # INPUTS
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.LAYER,
                self.tr('Input layer', 'Camada de entrada'),
                [QgsProcessing.TypeVector]
            )
        )

        self.addParameter(
            QgsProcessingParameterField(
                self.ATT,
                self.tr('Output file name', 'Nome do arquivo de saída'),
                parentLayerParameterName = self.LAYER
            )
        )

        self.addParameter(
            QgsProcessingParameterExpression(
                self.EXPR,
                self.tr('Expression to be written', 'Expressão a ser escrita'),
                parentLayerParameterName = self.LAYER
            )
        )

        self.addParameter(
            QgsProcessingParameterBoolean(
                self.UNIQUE,
                self.tr('Write to single file', 'Escrever em arquivo único'),
                defaultValue = False
            )
        )

        self.addParameter(
            QgsProcessingParameterField(
                self.ORDER,
                self.tr('Sort field', 'Campo de ordenação'),
                parentLayerParameterName = self.LAYER
            )
        )

        self.addParameter(
            QgsProcessingParameterString(
                self.FORMAT,
                self.tr('Output file format', 'Formato do arquivo de saída'),
                defaultValue = '.html'
            )
        )

        # OUTPUT
        self.addParameter(
            QgsProcessingParameterFile(
                self.FOLDER,
                self.tr('Destination folder', 'Pasta de destino'),
                behavior = QgsProcessingParameterFile.Folder
            )
        )

    def processAlgorithm(self, parameters, context, feedback):

        layer = self.parameterAsSource(
            parameters,
            self.LAYER,
            context
        )
        if layer is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.LAYER))

        campo = self.parameterAsFields(
            parameters,
            self.ATT,
            context
        )
        if campo:
            campo = campo[0]
            campo_idx = layer.fields().indexFromName(campo)
        else:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.ATT))

        expr = self.parameterAsString(
            parameters,
            self.EXPR,
            context
        )
        if expr is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.EXPR))
        expr = QgsExpression(expr)

        formato = self.parameterAsString(
            parameters,
            self.FORMAT,
            context
        )
        if formato is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.FORMAT))
        if formato[0] != '.':
            formato = '.' + str(formato)
        nova_linha = '<br>' if formato == '.html' else '\n'

        unico = self.parameterAsBool(
            parameters,
            self.UNIQUE,
            context
        )

        pasta = self.parameterAsFile(
            parameters,
            self.FOLDER,
            context
        )

        ordem = self.parameterAsFields(
            parameters,
            self.ORDER,
            context
        )

        if ordem:
            ordem = ordem[0]
            ordem_idx = layer.fields().indexFromName(ordem)
        else:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.ORDER))

        if unico:
            output = os.path.join(pasta, str(campo) + formato)
            arq = open(output, 'w')
            dic = {}

        Percent = 100.0/layer.featureCount() if layer.featureCount()>0 else 0
        for current, feat in enumerate(layer.getFeatures()):
            nome = str(feat[campo]) + formato
            att = feat.attributes()
            contexto = QgsExpressionContext()
            contexto.setFeature(feat)

            if not unico:
                output = os.path.join(pasta, nome)
                arq = open(output, 'w')
                arq.write(str(expr.evaluate(contexto)))
                arq.close()
            else:
                nome_seq = feat[ordem]
                if nome_seq not in dic:
                    dic[nome_seq] = [str(expr.evaluate(contexto)) + nova_linha]
                else:
                    dic[nome_seq] = dic[nome_seq] + [str(expr.evaluate(contexto)) + nova_linha]

            if feedback.isCanceled():
                break
            feedback.setProgress(int((current+1) * Percent))

        # Fechar arquivo
        if unico:
            # Preencher a partir do dicionário
            # ordenar a partir do atributo
            itens = list(dic.keys())
            itens.sort()
            for item in itens:
                lista_txt = dic[item]
                for texto in lista_txt:
                    arq.write(texto)
            arq.close()

        feedback.pushInfo(self.tr('Operation completed successfully!', 'Operação finalizada com sucesso!'))
        feedback.pushInfo(self.tr('Leandro França - Eng Cart', 'Leandro Franca - Cartographic Engineer'))
        try:
            subprocess.Popen(r'explorer /select,"{}"'.format(output))
        except:
            pass
        return {self.FOLDER: pasta}
