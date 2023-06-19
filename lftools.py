# -*- coding: utf-8 -*-

"""
/***************************************************************************
 LFTools
                                 A QGIS plugin
 Tools for cartographic production and spatial analysis.
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2021-03-01
        copyright            : (C) 2021 by Leandro Franca
        email                : geoleandro.franca@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

__author__ = 'Leandro Franca'
__date__ = '2021-03-01'
__copyright__ = '(C) 2021 by Leandro Franca'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

import os
import sys
import inspect

from qgis.core import (QgsProcessingAlgorithm,
                       QgsApplication,
                       QgsExpression)
from PyQt5.QtCore import QCoreApplication
from .lftools_provider import LFToolsProvider
from .expressions import *

exprs = (coord2inom, fieldstat, dd2dms, projectCRS, layerCRS, magneticdec, mainAzimuth,
         dms2dd, scalefactor, zonehemisf, deedtable, inom2mi, meridianconv, cusum, inter_area,
         removespetialchar, deedtable2, deedtable3, areaLTP, deedtext, geoneighbors, gpsdate,
         str2html, img2html)

cmd_folder = os.path.split(inspect.getfile(inspect.currentframe()))[0]

if cmd_folder not in sys.path:
    sys.path.insert(0, cmd_folder)


class LFToolsPlugin(object):

    def __init__(self):
        self.provider = None
        self.plugin_dir = os.path.dirname(__file__)

    def initProcessing(self):
        """Init Processing provider for QGIS >= 3.8."""
        self.provider = LFToolsProvider()
        QgsApplication.processingRegistry().addProvider(self.provider)


    def initGui(self):
        self.initProcessing()
        for expr in exprs:
            if not QgsExpression.isFunctionName(expr.name()):
                QgsExpression.registerFunction(expr)

    def unload(self):
        QgsApplication.processingRegistry().removeProvider(self.provider)
        for expr in exprs:
            if QgsExpression.isFunctionName(expr.name()):
                QgsExpression.unregisterFunction(expr.name())
