# -*- coding: utf-8 -*-

"""
Vect_LineSequence.py
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
__date__ = '2023-01-06'
__copyright__ = '(C) 2023, Leandro França'

from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (QgsApplication,
                       QgsProcessingParameterVectorLayer,
                       QgsGeometry,
                       QgsProcessing,
                       QgsProject,
                       QgsProcessingParameterField,
                       QgsProcessingParameterEnum,
                       QgsProcessingParameterBoolean,
                       QgsProcessingParameterNumber,
                       QgsFeatureSink,
                       QgsProcessingException,
                       QgsProcessingAlgorithm,
                       QgsCoordinateTransform,
                       QgsProcessingParameterFeatureSink)
from lftools.geocapt.imgs import Imgs
from lftools.translations.translate import translate
import os
from qgis.PyQt.QtGui import QIcon

class LineSequence(QgsProcessingAlgorithm):

    LOC = QgsApplication.locale()[:2]

    def tr(self, *string):
        return translate(string, self.LOC)

    def createInstance(self):
        return LineSequence()

    def name(self):
        return 'linesequence'

    def displayName(self):
        return self.tr('Line sequence', 'Sequenciar linhas')

    def group(self):
        return self.tr('Vector', 'Vetor')

    def groupId(self):
        return 'vector'

    def tags(self):
        return self.tr('sequence,lines,order,ordenar,orientar').split(',')

    def icon(self):
        return QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images/vetor.png'))

    txt_en = 'This script fills in a certain attribute of the features of a layer of lines according to their connectivity sequence between them.'
    txt_pt = 'Este script preenche um determinado atributo das feições de uma camada do tipo linha de acordo com sua sequência de conectividade entre as linhas.'
    figure = 'images/tutorial/vect_line_sequence.jpg'

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

    LINHAS = 'LINHAS'
    SELECTEDLINES = 'SELECTEDLINES'
    FIELD = 'FIELD'
    TOLERANCE = 'TOLERANCE'
    SAVE = 'SAVE'

    def initAlgorithm(self, config=None):
        self.addParameter(
            QgsProcessingParameterVectorLayer(
                self.LINHAS,
                self.tr('Line layer', 'Camada de linhas'),
                [QgsProcessing.TypeVectorLine]
            )
        )

        self.addParameter(
            QgsProcessingParameterBoolean(
                self.SELECTEDLINES,
                self.tr('Only selected line', 'Apenas linhas selecionadas'),
                defaultValue = False
            )
        )

        self.addParameter(
            QgsProcessingParameterField(
                self.FIELD,
                self.tr('Sequence Field', 'Campo de ordenação'),
                parentLayerParameterName=self.LINHAS,
                type = QgsProcessingParameterField.Numeric
            )
        )

        self.addParameter(
            QgsProcessingParameterNumber(
                self.TOLERANCE,
                self.tr('Tolerance (m)', 'Tolerância (m)'),
                type = QgsProcessingParameterNumber.Type.Double,
                defaultValue = 0.25,
                minValue = 0.001
                )
            )

        self.addParameter(
            QgsProcessingParameterBoolean(
                self.SAVE,
                self.tr('Save Editions', 'Salvar Edições'),
                defaultValue = False
            )
        )

    def processAlgorithm(self, parameters, context, feedback):

        layer = self.parameterAsVectorLayer(
            parameters,
            self.LINHAS,
            context
        )
        if layer is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.LINHAS))


        campo = self.parameterAsFields(
            parameters,
            self.FIELD,
            context
        )
        if campo is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.FIELD))

        columnIndex = layer.fields().indexFromName(campo[0])

        lin_selecionadas = self.parameterAsBool(
            parameters,
            self.SELECTEDLINES,
            context
        )

        tol = self.parameterAsDouble(
            parameters,
            self.TOLERANCE,
            context
        )

        if layer.crs().isGeographic():
            tol /= 111000

        linhas = {}

        for featA in layer.getSelectedFeatures() if lin_selecionadas else layer.getFeatures():
            mont = None
            jus = None
            geomA = featA.geometry()
            if geomA.isMultipart():
                coordsA = geomA.asMultiPolyline()[0]
            else:
                coordsA = geomA.asPolyline()
            pnt_iniA = QgsGeometry().fromPointXY(coordsA[0])
            pnt_fimA = QgsGeometry().fromPointXY(coordsA[-1])

            for featB in layer.getSelectedFeatures() if lin_selecionadas else layer.getFeatures():
                geomB = featB.geometry()
                if geomB.isMultipart():
                    coordsB = geomB.asMultiPolyline()[0]
                else:
                    coordsB = geomB.asPolyline()
                pnt_iniB = QgsGeometry().fromPointXY(coordsB[0])
                pnt_fimB = QgsGeometry().fromPointXY(coordsB[-1])

                if pnt_iniA.intersects(pnt_fimB.buffer(tol,5)):
                    mont = featB.id()
                elif pnt_fimA.intersects(pnt_iniB.buffer(tol,5)):
                    jus = featB.id()

                if mont != None and jus != None:
                    break

            linhas[featA.id()] = {'mont': mont, 'jus': jus}

        # Primeira feição
        for linha in linhas:
            if linhas[linha]['mont'] == None:
                seq = [linha]
                proximo = linhas[linha]['jus']
                break

        for k in range(len(linhas)-1):
            try:
                seq += [proximo]
                proximo = linhas[proximo]['jus']
            except:
                raise QgsProcessingException(self.tr('Check the connectivity between the lines or increase the tolerance value!', 'Verifique a conectividade entre as linhas ou aumente o valor da tolerância!'))

        layer.startEditing()
        total = 100.0 / (len(seq))
        for k, id in enumerate(seq):
            layer.changeAttributeValue(id, columnIndex, k+1)
            feedback.setProgress(int((k+1) * total))

        salvar = self.parameterAsBool(
            parameters,
            self.SAVE,
            context
        )
        if salvar is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.SAVE))

        if salvar:
            layer.commitChanges() # salva as edições

        feedback.pushInfo(self.tr('Operation completed successfully!', 'Operação finalizada com sucesso!'))
        feedback.pushInfo(self.tr('Leandro Franca - Cartographic Engineer', 'Leandro França - Eng Cart'))

        return {}
