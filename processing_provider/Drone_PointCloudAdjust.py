# -*- coding: utf-8 -*-

"""
Drone_PointCloudAdjust.py
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
__date__ = '2023-01-22'
__copyright__ = '(C) 2023, Leandro França'

from PyQt5.QtCore import QCoreApplication, QVariant
from qgis.core import (QgsProcessing,
                       QgsFeatureSink,
                       QgsWkbTypes,
                       QgsFields,
                       QgsField,
                       QgsFeature,
                       QgsPointXY,
                       QgsGeometry,
                       QgsProcessingException,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterString,
                       QgsProcessingParameterNumber,
                       QgsProcessingParameterField,
                       QgsProcessingParameterBoolean,
                       QgsProcessingParameterFile,
                       QgsProcessingParameterEnum,
                       QgsFeatureRequest,
                       QgsExpression,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterFeatureSink,
                       QgsProcessingParameterFileDestination,
                       QgsProcessingParameterMultipleLayers,
                       QgsProcessingParameterVectorLayer,
                       QgsProcessingParameterRasterLayer,
                       QgsProcessingParameterRasterDestination,
                       QgsApplication,
                       QgsProject,
                       QgsRasterLayer,
                       QgsCoordinateTransform,
                       QgsCoordinateReferenceSystem)

from osgeo import osr, gdal_array, gdal #https://gdal.org/python/
import numpy as np
from pyproj.crs import CRS
from math import floor, ceil
from lftools.geocapt.imgs import Imgs
from lftools.geocapt.dip import Interpolar
from lftools.geocapt.adjust import AjustVertical, ValidacaoGCP, Ajust2D, ValidacaoVetores
from lftools.geocapt.cartography import geom2PointList
import os
import codecs
from qgis.PyQt.QtGui import QIcon

class PointCloudAdjust(QgsProcessingAlgorithm):

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
        return PointCloudAdjust()

    def name(self):
        return 'pointcloudadjust'

    def displayName(self):
        return self.tr('Point cloud adjustment', 'Ajuste de Nuvem de Pontos')

    def group(self):
        return self.tr('Drones')

    def groupId(self):
        return 'drones'

    def tags(self):
        return self.tr('drone,model,modelo,mosaic,adjustment,point,cloud,vertical,dem,dsm,mdt,georreferenciamento,ajuste,mds,dtm,GCP,ground control points,pontos de controle,elevation,terrain,surface').split(',')

    def icon(self):
        return QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images/drone.png'))

    txt_en = '''This tool performs the horizontal and vertical adjustment of Cloud of Points in (TXT) format using LineStringZ vectors.'''
    txt_pt = '''Esta ferramenta realiza o ajuste horizontal e vertical de Nuvem de Pontos no formato (TXT) utilizando vetores do tipo LineStringZ.'''
    figure = 'images/tutorial/drone_point_cloud_adjust.jpg'

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

    VECTORS = 'VECTORS'
    PC = 'PC'
    HORIZONTAL = 'HORIZONTAL'
    VERTICAL = 'VERTICAL'
    ADJUSTED = 'ADJUSTED'
    DECIMAL = 'DECIMAL'

    def initAlgorithm(self, config=None):
        # INPUT
        self.addParameter(
            QgsProcessingParameterFile(
                self.PC,
                self.tr('Point Cloud', 'Nuvem de Pontos'),
                behavior = QgsProcessingParameterFile.File,
                fileFilter = 'Text (*.txt)'
            )
        )

        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.VECTORS,
                self.tr('Vectors Lines (two 3D vertices)', 'Linhas de vetores (dois vértices 3D)'),
                [QgsProcessing.TypeVectorLine]
            )
        )

        horiz_ajust = [self.tr('Translation','Translação'),
                       self.tr('Helmert 2D (Conformal)','Helmert 2D (Conforme)'),
                       self.tr('Afinne','Afim (Polinomial grau 1)')]

        self.addParameter(
            QgsProcessingParameterEnum(
                self.HORIZONTAL,
                self.tr('Method of horizontal adjustment', 'Método de ajuste horizontal'),
				options = horiz_ajust,
                defaultValue= 2
            )
        )

        vert_ajust = [self.tr('Constant','Constante'),
                      self.tr('Plane','Plano')]

        self.addParameter(
            QgsProcessingParameterEnum(
                self.VERTICAL,
                self.tr('Method of vertical adjustment', 'Método de ajuste vertical'),
				options = vert_ajust,
                defaultValue = 1
            )
        )

        self.addParameter(
            QgsProcessingParameterNumber(
                self.DECIMAL,
                self.tr('Decimal places', 'Casas decimais'),
                type =0,
                defaultValue = 2,
                minValue = 0
                )
            )

        # OUTPUT
        self.addParameter(
            QgsProcessingParameterFileDestination(
                self.ADJUSTED,
                self.tr('Adjusted Point Cloud', 'Nuvem de pontos ajustada'),
                fileFilter = 'Text (*.txt)'
            )
        )

    def processAlgorithm(self, parameters, context, feedback):


        nuvem = self.parameterAsFile(
            parameters,
            self.PC,
            context
        )
        if not nuvem:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.PC))

        deslc = self.parameterAsSource(
            parameters,
            self.VECTORS,
            context
        )
        if deslc is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.VECTORS))

        # Verificar se é 3D
        if deslc.wkbType() != QgsWkbTypes.LineStringZ:
            raise QgsProcessingException(self.tr('Input layer must be of type LineStringZ!',
                                                 'Camada de entrada deve ser do tipo LineStringZ!'))

        metodo_Hz = self.parameterAsEnum(
            parameters,
            self.HORIZONTAL,
            context
        )

        metodo_Vert = self.parameterAsEnum(
            parameters,
            self.VERTICAL,
            context
        )

        decimal = self.parameterAsInt(
            parameters,
            self.DECIMAL,
            context
        )
        if decimal is None or decimal<1:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.DECIMAL))

        format_num = '{:,.Xf}'.replace('X', str(decimal))

        arquivo_saida = self.parameterAsFile(
            parameters,
            self.ADJUSTED,
            context
        )

        if 'ADJUSTED.txt' in arquivo_saida: # não permitir arquivo temporário
            raise QgsProcessingException(self.tr('Output file path must be filled!', 'Caminho do arquivo de saída deve ser preenchido!'))

        # Contagem de pontos
        feedback.pushInfo(self.tr('Opening point cloud file...', 'Abrindo arquivo de nuvem de pontos...'))
        with codecs.open(nuvem, 'r', encoding='utf-8', errors='ignore') as arq_in:
            total_lines = sum(1 for line in arq_in)

        feedback.pushInfo(self.tr('Total number of points: ', 'Número total de pontos: ') + self.tr('{:,d}'.format(total_lines), '{:,d}'.format(total_lines).replace(',','.')) )

        # Ajustamento Horizontal
        feedback.pushInfo(self.tr('Calculating horizontal adjustment parameters...', 'Calculando parâmetros de ajustamento horizontal...'))
        validacao = ValidacaoVetores(deslc, metodo_Hz)
        COORD, PREC, CoordTransf_Hz, texto, CoordInvTransf = Ajust2D(deslc, metodo_Hz)

        # Ajustamento Vertical
        feedback.pushInfo(self.tr('Calculating vertical adjustment parameters...', 'Calculando parâmetros de ajustamento vertical...'))
        lista = []
        for feat in deslc.getFeatures():
            geom = feat.geometry()
            coords = geom2PointList(geom)
            X = coords[-1].x()
            Y = coords[-1].y()
            Z_ini = coords[0].z()
            Z_fim = coords[-1].z()
            lista += [[(X,Y,Z_ini),Z_fim]]
        COTAS, PREC, DELTA, CoordTransf_V, texto = AjustVertical(lista, metodo_Vert)

        # Realizando as correções horizontais e verticais
        feedback.pushInfo(self.tr("Performing horizontal and vertical adjustment...", 'Realizando ajuste horizontal e vertical...'))

        # Abrir arquivo TXT de nuvem de pontos
        arq_in = codecs.open(nuvem, 'r', encoding='utf-8', errors='ignore')
        arq_out = open(arquivo_saida, 'w')

        Percent = 100.0/total_lines if total_lines else 0

        for current, line in enumerate(arq_in.readlines()):
            print(line)
            print(line.split(' '))
            try:
                lista = line.split(' ')
                if len(lista) == 3:
                    X, Y, Z = lista
                elif len(lista) == 6:
                    X, Y, Z, R, G, B = lista
                else:
                    X, Y, Z = lista[0], lista[1], lista[2]
                # Correção HORIZONTAL
                X_novo, Y_novo = CoordTransf_Hz(QgsPointXY(float(X),float(Y)))
                dz = CoordTransf_V(X_novo, Y_novo)
                Z_novo = float(Z) - dz
                if len(lista) == 3:
                    arq_out.write('{:.2f} {:.2f} {:.2f}\n'.format(X_novo, Y_novo, Z_novo))
                elif len(lista) == 6:
                    arq_out.write('{:.2f} {:.2f} {:.2f} {} {} {}\n'.format(X_novo, Y_novo, Z_novo, int(R), int(G), int(B)))
                else:
                    linha = '{:.2f} {:.2f} {:.2f}' + (len(lista)-3)*' {}' + '\n'
                    arq_out.write(linha.format(X_novo, Y_novo, Z_novo, *lista[3:]))
            except:
                pass
            if feedback.isCanceled():
                break
            feedback.setProgress(int((current + 1) * Percent))

        arq_in.close()
        arq_out.close()

        feedback.pushInfo(self.tr('Operation completed successfully!', 'Operação finalizada com sucesso!'))
        feedback.pushInfo(self.tr('Leandro Franca - Cartographic Engineer', 'Leandro França - Eng Cart'))

        return {self.ADJUSTED: arquivo_saida}
