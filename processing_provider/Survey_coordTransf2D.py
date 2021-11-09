# -*- coding: utf-8 -*-

"""
Survey_coordTransf2D.py
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
__date__ = '2019-11-08'
__copyright__ = '(C) 2019, Leandro França'

from PyQt5.QtCore import QCoreApplication, QVariant
from qgis.core import *
import numpy as np
from numpy.linalg import norm, inv, pinv, det, solve
from lftools.geocapt.imgs import Imgs
from lftools.geocapt.topogeo import str2HTML, dd2dms
from lftools.geocapt.adjust import Ajust2D, ValidacaoVetores, transformGeom2D
import os
from qgis.PyQt.QtGui import QIcon


class CoordTransf2D(QgsProcessingAlgorithm):

    INPUT = 'INPUT'
    VECTOR = 'VECTOR'
    METHOD = 'METHOD'
    OUTPUT = 'OUTPUT'
    HTML = 'HTML'

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
        return CoordTransf2D()

    def name(self):
        return 'coordtransf2D'

    def displayName(self):
        return self.tr('Coordinate transformation 2D', 'Transformação de coordenadas 2D')

    def group(self):
        return self.tr('Survey', 'Agrimensura')

    def groupId(self):
        return 'survey'

    def tags(self):
        return self.tr('survey,agrimensura,helmert,2D,georreferencing,tranformation,conformal,register,adjustment,least squares,spatial').split(',')

    def icon(self):
        return QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images/total_station.png'))

    txt_en = """This tool performs the following types of coordinate transformation:
◼️ <b>Translation Transformation</b>: 1 vector without adjustment / 2 or + vectors with adjustment.
◼️ <b>Conformal Transformation (2D Helmert)</b>: 2 vectors without adjustment / 3 or + vectors with adjustment.
◼️ <b>Affine Transformation</b>: 3 vectors without adjustment / 4 or + vectors with adjustment.
With this tool it is possible to perform correctly the georeferencing of vector files in QGIS.
"""
    txt_pt = """Esta ferramenta realiza os seguintes tipos de transformação de coordenadas:
◼️	<b>Transformação de Translação</b>: 1 vetor sem ajustamento / 2 ou + vetores com ajustamento.
◼️	<b>Transformação Conforme (Helmert 2D)</b>: 2 vetores sem ajustamento / 3 ou + vetores com ajustamento.
◼️	<b>Transformação Afim</b>: 3 vetores sem ajustamento / 4 ou + vetores com ajustamento.
Com esta ferramenta é possível realizar o correto georreferenciamento de arquivos vetoriais no QGIS.
"""
    figure = 'images/tutorial/survey_helmert2D.jpg'

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
        # INPUT
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT,
                self.tr('Input Vector Layer', 'Camada vetorial de entrada'),
                [QgsProcessing.TypeVectorAnyGeometry]
            )
        )

        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.VECTOR,
                self.tr('Vectors Lines (two points)', 'Linhas de vetores (dois pontos)'),
                [QgsProcessing.TypeVectorLine]
            )
        )

        tipos = [self.tr('Translation','Translação'),
                  self.tr('Helmert 2D (Conformal)','Helmert 2D (Conforme)'),
                  self.tr('Afinne','Afim (Polinomial grau 1)')
               ]

        self.addParameter(
            QgsProcessingParameterEnum(
                self.METHOD,
                self.tr('Method', 'Método'),
				options = tipos,
                defaultValue= 2
            )
        )

        # OUTPUT
        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT,
                self.tr('Transformed Layer', 'Camada transformada')
            )
        )

        self.addParameter(
            QgsProcessingParameterFileDestination(
                self.HTML,
                self.tr('Adjustment Report', 'Relatório de Ajustamento'),
                self.tr('HTML files (*.html)')
            )
        )

    def processAlgorithm(self, parameters, context, feedback):

        entrada = self.parameterAsSource(
            parameters,
            self.INPUT,
            context
        )
        if entrada is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.INPUT))

        deslc = self.parameterAsSource(
            parameters,
            self.VECTOR,
            context
        )
        if deslc is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.VECTOR))

        # Validação dos vetores de georreferenciamento

        # OUTPUT
        (sink, dest_id) = self.parameterAsSink(
            parameters,
            self.OUTPUT,
            context,
            entrada.fields(),
            entrada.wkbType(),
            entrada.sourceCrs()
        )
        if sink is None:
            raise QgsProcessingException(self.invalidSinkError(parameters, self.OUTPUT))

        html_output = self.parameterAsFileOutput(
            parameters,
            self.HTML,
            context
        )

        metodo = self.parameterAsEnum(
            parameters,
            self.METHOD,
            context
        )

        validacao = ValidacaoVetores(deslc, metodo)

        COORD, PREC, CoordTransf, texto, CoordInvTransf = Ajust2D(deslc, metodo)

        feature = QgsFeature()
        total = 100.0 / entrada.featureCount() if entrada.featureCount() else 0
        for current, feat in enumerate(entrada.getFeatures()):
            geom = feat.geometry()
            newgeom = transformGeom2D(geom, CoordTransf)
            feature.setGeometry(newgeom)
            feature.setAttributes(feat.attributes())
            sink.addFeature(feature, QgsFeatureSink.FastInsert)
            if feedback.isCanceled():
                break
            feedback.setProgress(int(current * total))

        # Exportar HTML
        arq = open(html_output, 'w')
        arq.write(texto)
        arq.close()

        feedback.pushInfo(self.tr('Operation completed successfully!', 'Operação finalizada com sucesso!'))
        feedback.pushInfo(self.tr('Leandro Franca - Cartographic Engineer', 'Leandro França - Eng Cart'))
        return {self.OUTPUT: dest_id,
                self.HTML: html_output}
