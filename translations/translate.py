# -*- coding: utf-8 -*-

"""
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
__date__ = '2024-06-23'

from lftools.translations.spanish import dic_ES

def translate(string, loc):
    # Português
    if loc == 'pt':
        if len(string) == 2:
            return string[1]
        else:
            return string[0]
    # Espanhol
    elif loc == 'es':
        if string[0] in dic_ES:
            return dic_ES[string[0]]
        elif len(string) == 2:
            return string[1]
        else:
            return string[0]
    # Inglês
    else:
        return string[0]
