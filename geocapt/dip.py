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
__date__ = '2021-11-05'
__copyright__ = '(C) 2021, Leandro França'

# Digital Image Processing (DIP)

import numpy as np
from math import floor, ceil

# Função de Interpolação
def Interpolar(X, Y, BAND, origem, resol_X, resol_Y, metodo, nulo):
    if metodo == 'nearest':
        I = int(round((origem[1]-Y)/resol_Y - 0.5))
        J = int(round((X - origem[0])/resol_X - 0.5))
        try:
            return float(BAND[I][J])
        except:
            return nulo
    elif metodo == 'bilinear':
        I = (origem[1]-Y)/resol_Y - 0.5
        J = (X - origem[0])/resol_X - 0.5
        di = I - floor(I)
        dj = J - floor(J)
        try:
            if (BAND[int(floor(I)):int(ceil(I))+1, int(floor(J)):int(ceil(J))+1] == nulo).sum() == 0:
                Z = (1-di)*(1-dj)*BAND[int(floor(I))][int(floor(J))] + (1-dj)*di*BAND[int(ceil(I))][int(floor(J))] + (1-di)*dj*BAND[int(floor(I))][int(ceil(J))] + di*dj*BAND[int(ceil(I))][int(ceil(J))]
                return float(Z)
            else:
                return nulo
        except:
            return nulo
    elif metodo == 'bicubic':
        I = (origem[1]-Y)/resol_Y - 0.5
        J = (X - origem[0])/resol_X - 0.5
        di = I - floor(I)
        dj = J - floor(J)
        I=int(floor(I))
        J=int(floor(J))
        try:
            if (BAND[I-1:I+3, J-1:J+3] == nulo).sum() == 0:
                MatrInv = np.mat([[-1/6, 0.5, -0.5, 1/6], [ 0.5, -1., 0.5, 0.], [-1/3, -0.5,  1., -1/6], [ 0., 1., 0., 0.]]) # resultado da inversa: (np.mat([[-1, 1, -1, 1], [0, 0, 0, 1], [1, 1, 1, 1], [8, 4, 2, 1]])).I #
                MAT  = np.mat([ [BAND[I-1, J-1],  BAND[I-1, J], BAND[I-1, J+1], BAND[I-2, J+2]],
                                [BAND[I, J-1],    BAND[I, J],   BAND[I, J+1],   BAND[I, J+2]],
                                [BAND[I+1, J-1],  BAND[I+1, J], BAND[I+1, J+1], BAND[I+1, J+2]],
                                [BAND[I+2, J-1],  BAND[I+2, J], BAND[I+2, J+1], BAND[I+2, J+2]]])
                coef = MatrInv*MAT.transpose()
                # Horizontal
                pi = coef[0,:]*pow(dj,3)+coef[1,:]*pow(dj,2)+coef[2,:]*dj+coef[3,:]
                # Vertical
                coef2 = MatrInv*pi.transpose()
                pj = coef2[0]*pow(di,3)+coef2[1]*pow(di,2)+coef2[2]*di+coef2[3]
                return float(pj)
            else:
                return nulo
        except:
            return nulo
