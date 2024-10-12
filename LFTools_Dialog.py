# -*- coding: utf-8 -*-

"""
/***************************************************************************
 LFTools
                                 A QGIS plugin
 Tools for cartographic production and spatial analysis.
                              -------------------
        begin                : 2024-10-09
        copyright            : (C) 2024 by Leandro Franca
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
from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import QDialog
import os

class ImportXYZ_Dialog(QDialog):
    def __init__(self):
        super(ImportXYZ_Dialog, self).__init__()
        uic.loadUi(os.path.join(os.path.dirname(__file__), 'Ui_ImportXYZ.ui'), self)
