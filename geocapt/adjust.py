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
__date__ = '2021-11-04'
__copyright__ = '(C) 2021, Leandro França'

from qgis.core import *
from qgis.gui import *
from lftools.geocapt.topogeo import str2HTML
from lftools.geocapt.imgs import Imgs
from lftools.translations.translate import translate
from qgis.core import *
from qgis.gui import *
import numpy as np
from numpy.linalg import norm, det, inv, solve

# Tradução
LOC = QgsApplication.locale()[:2]
def tr(*string):
    return translate(string, LOC)

# Validação dos Pontos Homólogos
def ValidacaoVetores(vetores, metodo):
    # número de feições por modelo matemático
    cont = vetores.featureCount()
    sinal = True
    if metodo == 0:
        if cont < 1:
            raise QgsProcessingException(tr('It takes 1 or more vectors to perform this transformation!', 'É necessario 1 ou mais vetores para realizar essa transformação!'))
    elif metodo == 1:
        if cont < 2:
            raise QgsProcessingException(tr('It takes 2 or more vectors to perform this transformation!', 'É necessario 2 ou mais vetores para realizar essa transformação!'))

    elif metodo == 2:
        if cont < 3:
            raise QgsProcessingException(tr('It takes 3 or more vectors to perform this transformation!', 'É necessario 3 ou mais vetores para realizar essa transformação!'))

    # cada feição (vetor) deve ter 2 dois vértices distintos
    for feat in vetores.getFeatures():
        geom = feat.geometry()
        coord = geom.asPolyline()
        if len(coord) != 2:
            raise QgsProcessingException(tr('The vector lines must be created with exactly two points!', 'As linhas de vetores devem ter exatamente 2 vértices!'))
    return sinal

# Transformação de Coordenadas de Geometrias a partir de uma função de transformação
def transformGeom2D(geom, CoordTransf):
    if geom.type() == 0: #Point
        if geom.isMultipart():
            pnts = geom.asMultiPoint()
            newPnts = []
            for pnt in pnts:
                x, y = CoordTransf(pnt)
                newPnts += [QgsPointXY(x,y)]
            newGeom = QgsGeometry.fromMultiPointXY(newPnts)
            return newGeom
        else:
            pnt = geom.asPoint()
            x, y = CoordTransf(pnt)
            newPnt = QgsPointXY(x,y)
            newGeom = QgsGeometry.fromPointXY(newPnt)
            return newGeom
    elif geom.type() == 1: #Line
        if geom.isMultipart():
            linhas = geom.asMultiPolyline()
            newLines = []
            for linha in linhas:
                newLine =[]
                for pnt in linha:
                    x, y = CoordTransf(pnt)
                    newLine += [QgsPointXY(x,y)]
                newLines += [newLine]
            newGeom = QgsGeometry.fromMultiPolylineXY(newLines)
            return newGeom
        else:
            linha = geom.asPolyline()
            newLine =[]
            for pnt in linha:
                x, y = CoordTransf(pnt)
                newLine += [QgsPointXY(x,y)]
            newGeom = QgsGeometry.fromPolylineXY(newLine)
            return newGeom
    elif geom.type() == 2: #Polygon
        if geom.isMultipart():
            poligonos = geom.asMultiPolygon()
            newPolygons = []
            for pol in poligonos:
                newPol = []
                for anel in pol:
                    newAnel = []
                    for pnt in anel:
                        x, y = CoordTransf(pnt)
                        newAnel += [QgsPointXY(x,y)]
                    newPol += [newAnel]
                newPolygons += [newPol]
            newGeom = QgsGeometry.fromMultiPolygonXY(newPolygons)
            return newGeom
        else:
            pol = geom.asPolygon()
            newPol = []
            for anel in pol:
                newAnel = []
                for pnt in anel:
                    x, y = CoordTransf(pnt)
                    newAnel += [QgsPointXY(x,y)]
                newPol += [newAnel]
            newGeom = QgsGeometry.fromPolygonXY(newPol)
            return newGeom
    else:
        return None

# Ajustamento 2D
def Ajust2D(vetores, metodo):
    # Métodos:
    # 0 - translação, 1 - Helmert 2D, 2 - Afim

    # numero de pontos homologos
    n_pnts_homo = vetores.featureCount()

    # numero minimo de pontos homologos por metodo
    if metodo == 0: # 0 - translação
        min_pnts_homo = n_pnts_homo == 1
    elif metodo == 1: # 1 - Helmert 2D
        min_pnts_homo = n_pnts_homo == 2
    elif metodo == 2: # 2 - Afim
        min_pnts_homo = n_pnts_homo == 3

    A = [] # Matriz Design
    L = [] # Coordenadas Finais
    Lo = [] # Coordenadas Iniciais
    for feat in vetores.getFeatures():
        geom = feat.geometry()
        coord = geom.asPolyline()
        xa = coord[0].x()
        ya = coord[0].y()
        xb = coord[1].x()
        yb = coord[1].y()
        if metodo == 0:
            A += [[1, 0], [0, 1]]
        elif metodo == 1:
            A += [[xa, -ya, 1, 0], [ya, xa, 0, 1]]
        elif metodo == 2:
            A += [[xa, ya, 1, 0, 0, 0], [0, 0, 0, xa, ya, 1]]
        L +=[[xb], [yb]]
        Lo +=[[xa], [ya]]

    A = np.matrix(A)
    L = np.matrix(L)
    Lo = np.matrix(Lo)

    msg_erro = tr('Georeferencing vectors should not be aligned!', 'Os vetores de georreferenciamento não podem ter a mesma direção (alinhados)!')
    if metodo == 0:
        if min_pnts_homo:
            X = L - Lo
        else:
            M = A.T*A
            if det(M):
                X = solve(M, A.T*(L - Lo))
            else:
                raise QgsProcessingException(msg_erro)
    else:
        if min_pnts_homo:
            if det(A):
                X = solve(A, L)
            else:
                raise QgsProcessingException(msg_erro)
        else: # asjustamento
            M = A.T*A
            if det(M):
                X = solve(M, A.T*L)
            else:
                raise QgsProcessingException(msg_erro)

    # Parametros e Função da Transformação
    if metodo == 0:
        a = X[0,0]
        b = X[1,0]
        def CoordTransf(pnt, a = a, b = b): # Translacao
            X, Y = pnt.x(), pnt.y()
            Xt = X + a
            Yt = Y + b
            return (Xt, Yt)
        def CoordInvTransf(pnt, a = a, b = b): # Translacao (Inversa)
            X, Y = pnt.x(), pnt.y()
            Xit = X - a
            Yit = Y - b
            return (Xit, Yit)

    elif metodo == 1:
        a = X[0,0]
        b = X[1,0]
        c = X[2,0]
        d = X[3,0]
        def CoordTransf(pnt, a = a, b = b, c = c, d = d): # Transformação Conforme - Helmert 2D
            '''
            Xt = X*a - Y*b + c
            Yt = X*b + Y*a + d
            a = S*cos(alfa)
            b = S*sin(alfa)
            '''
            X, Y = pnt.x(), pnt.y()
            Xt = X*a - Y*b + c
            Yt = X*b + Y*a + d
            return (Xt, Yt)
        def CoordInvTransf(pnt, a = a, b = b, c = c, d = d): # Transformação de Helmert 2D (Inversa)
            X, Y = pnt.x(), pnt.y()
            A = np.matrix([[a,-b],[b,a]])
            B = np.matrix([[X-c],[Y-d]])
            sol = solve(A,B)
            Xit = sol[0,0]
            Yit = sol[1,0]
            return (Xit, Yit)

    elif metodo == 2:
        a = X[0,0]
        b = X[1,0]
        c = X[2,0]
        d = X[3,0]
        e = X[4,0]
        f = X[5,0]
        def CoordTransf(pnt, a = a, b = b, c = c, d = d, e = e, f = f): # Transformação Afim
            X, Y = pnt.x(), pnt.y()
            Xt = X*a + Y*b + c
            Yt = X*d + Y*e + f
            return (Xt, Yt)
        def CoordInvTransf(pnt, a = a, b = b, c = c, d = d, e = e, f = f): # Transformação Afim (Inversa)
            X, Y = pnt.x(), pnt.y()
            A = np.matrix([[a,b],[d,e]])
            B = np.matrix([[X-c],[Y-f]])
            sol = solve(A,B)
            Xit = sol[0,0]
            Yit = sol[1,0]
            return (Xit, Yit)

    # Cálculo do Resíduos
    transf = []
    for feat in vetores.getFeatures():
        geom = feat.geometry()
        coord = geom.asPolyline()
        Xt, Yt = CoordTransf(coord[0])
        transf += [[Xt],[Yt]]
        X, Y = coord[-1].x(), coord[-1].y()
        Vx = X - Xt
        Vy = Y - Yt

    # MVC dos Parametros e das coordenadas Ajustadas
    n = np.shape(A)[0] # número de observações
    u = np.shape(A)[1] # número de parâmetros
    if not min_pnts_homo:
        # Residuos
        V = L - np.matrix(transf)
        # Sigma posteriori
        sigma2 = V.T*V/(n-u)
        # Precisão dos Pontos Ajustados
        # MVC de Xa
        SigmaXa = sigma2[0,0]*inv(A.T*A)
        SigmaXa  = np.matrix(SigmaXa).astype(float)
        # MVC de La
        SigmaLa = A*SigmaXa*A.T
        SigmaLa  = np.matrix(SigmaLa).astype(float)
        # RMSE
        RMSE = np.sqrt((V.T*V)[0,0]/n_pnts_homo)
    else:
        sigma2 = 0
        RMSE = 0

    # Lista de Coordenadas Ajustadas, Precisões e Resíduos
    COORD = []
    PREC = []
    DELTA = []
    for index, feat in enumerate(vetores.getFeatures()):
        X = transf[2*index][0]
        Y = transf[2*index+1][0]
        COORD += [QgsPointXY(X, Y)]
        if not min_pnts_homo:
            s_X = float(np.sqrt(SigmaLa[2*index,2*index]))
            s_Y = float(np.sqrt(SigmaLa[2*index+1,2*index+1]))
            PREC += [(s_X, s_Y)]
            d_X = float(V[2*index][0])
            d_Y = float(V[2*index+1][0])
            DELTA += [(d_X, d_Y)]
        else:
            PREC += [(0, 0)]
            DELTA += [(0, 0)]


    if metodo == 0:
        formula = '''<p class="MsoNormal" style="text-align: center;"
 align="center"><i><span style="">'''+ str2HTML(tr('Translation','Translação')) + '''</span></i></p>
<p class="MsoNormal" style="text-align: center;"
 align="center"><i><span style=""></span></i></p>
<p class="MsoNormal" style="text-align: center;"
 align="center"><i><span style="">X
=&nbsp;</span></i><i><span style="">x
</span></i><i><span style="">+</span></i><i><span
 style=""> a</span></i><i><span style="">
+</span></i><i><span style=""> Vx<o:p></o:p></span></i></p>
<div style="text-align: center;"><i><span style="">Y&nbsp;=
</span></i><i><span style="">y
</span></i><i><span style="">+</span></i><i><span
 style=""> b</span></i><i><span style="">
+</span></i><i><span style=""> </span></i><i><span
 style=""></span></i><i><span style="">Vy</span></i></div>
'''
    elif metodo == 1:
        formula = '''<p class="MsoNormal" style="text-align: center;"
 align="center"><i><span style="">'''+ str2HTML(tr('Helmert 2D (Conformal)','Helmert 2D (Conforme)')) + '''</span></i></p>
<p class="MsoNormal" style="text-align: center;"
 align="center"><i><span style="">X = </span></i><i><span
 style="">ax
</span></i><i><span style="">-</span></i><i><span
 style=""> by </span></i><i><span
 style=""></span></i><i><span style="">+
c +</span></i><i><span style=""> Vx<o:p></o:p></span></i></p>
<div style="text-align: center;"><i><span style="">Y&nbsp;=
</span></i><i><span style="">bx
</span></i><i><span style="">+</span></i><i><span
 style=""> ay </span></i><i><span
 style="">+ d +</span></i><i><span
 style=""> </span></i><i><span style=""></span></i><i><span
 style="">Vy</span></i></div>
'''
    elif metodo == 2:
        formula = '''<p class="MsoNormal" style="text-align: center;"
 align="center"><i><span style="">'''+ str2HTML(tr('Affine Transform','Transformação Afim')) + '''</span></i></p>
<p class="MsoNormal" style="text-align: center;"
 align="center"><i><span style="">X = </span></i><i><span
 style="">ax </span></i><i><span
 style="">+</span></i><i><span style="">
by </span></i><i><span style=""></span></i><i><span
 style="">+ c +</span></i><i><span
 style=""> Vx<o:p></o:p></span></i></p>
<div style="text-align: center;"><i><span style="">Y&nbsp;=
</span></i><i><span style="">dx
</span></i><i><span style="">+</span></i><i><span
 style=""> ey </span></i><i><span
 style="">+ f +</span></i><i><span
 style=""> </span></i><i><span style=""></span></i><i><span
 style="">Vy</span></i></div>
'''

    parametros = ''
    for k in range(u): # para cada parâmetro
        letra = chr(k+97)
        parametros += '''<p class="MsoNormal" style="text-align: center;"
align="center"><span style="">letrax
</span><span style="">=</span><span
style=""> [x]<o:p></o:p></span></p>
'''.replace('letrax', letra).replace('[x]', str(eval(letra)))


    texto = '''<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
<html>
<head>
<meta content="text/html; charset=ISO-8859-1"
http-equiv="content-type">
<title>'''+ str2HTML(tr('Coordinate Transformation','Transformação de Coordenadas')) + '''</title>
<link rel = "icon" href = "https://github.com/LEOXINGU/lftools/blob/main/images/lftools.png?raw=true" type = "image/x-icon">
</head>
<body
style="color: rgb(0, 0, 0); background-color: rgb(255, 255, 204);"
alink="#000099" link="#000099" vlink="#990099">
<p class="MsoNormal" style="text-align: center;"
align="center"><b><span
style="font-size: 12pt; line-height: 107%;"><o:p></o:p></span></b><span
style="font-weight: bold; text-decoration: underline;">'''+ str2HTML(tr('COORDINATE TRANSFORMATION','TRANSFORMAÇÃO DE COORDENDAS')) + ''' (2D)</span></p>
<p class="MsoNormal" style="text-align: center;"
align="center"><span style="font-style: italic;">''' + str2HTML(tr('Mathematical Formulation','Formulação Matemática')) + '''
</span></p>''' + formula + '''<p style="text-align: center;" class="MsoNormal"><b><span
style="">''' + str2HTML(tr('Residual Errors of Control Points','Erro residual dos Pontos de Controle')) + '''<o:p></o:p></span></b></p>
<table
style="border: medium none ; border-collapse: collapse; text-align: left; margin-left: auto; margin-right: auto;"
class="MsoTableGrid" border="0" cellpadding="0"
cellspacing="0">
<tbody>
<tr style="">
  <td style="padding: 0cm 5.4pt; width: 84.9pt;"
valign="top" width="113">
  <p class="MsoNormal"
style="margin-bottom: 0.0001pt; text-align: center; line-height: normal;"
align="center"><i><span style="">''' + str2HTML(tr('Point','Ponto')) + '''<o:p></o:p></span></i></p>
  </td>
  <td style="padding: 0cm 5.4pt; width: 84.95pt;"
valign="top" width="113">
  <p class="MsoNormal"
style="margin-bottom: 0.0001pt; text-align: center; line-height: normal;"
align="center"><i><span style="">Vx<o:p></o:p></span></i></p>
  </td>
  <td style="padding: 0cm 5.4pt; width: 84.95pt;"
valign="top" width="113">
  <p class="MsoNormal"
style="margin-bottom: 0.0001pt; text-align: center; line-height: normal;"
align="center"><i><span style="">Vy<o:p></o:p></span></i></p>
  </td>
</tr>
[TABLE]
</tbody>
</table>
<br>
<div>
<p class="MsoNormal" style="text-align: center;"
align="center"><b><span style="">''' + str2HTML(tr('Transformation Parameters:','Parâmetros de Transformação:')) + '''<o:p></o:p></span></b></p>
''' + parametros + '''
<div style="text-align: center;"><b><span style=""
>''' + str2HTML(tr('Adjustment&rsquo;s Reference Variance','Variância a posteriori')) + '''</span></b><span style=""
> <span style="">&nbsp;</span>=
</span><span style="">''' + str(round(sigma2[0,0] if not min_pnts_homo else 0, 4)) + '''</span></div>
<br>
<div style="text-align: center;"><b><span style=""
>''' + str2HTML(tr('Root Mean Square Error (RMSE)','Raiz do Erro Médio Quadrático (REMQ)')) + '''</span></b><span style=""
> <span style="">&nbsp;</span>=
</span><span style="">''' + str(round(RMSE,4)) + '''</span></div>

</div>
<footer">
<p class="MsoNormal" style="margin-bottom: 0.0001pt; text-align: right;" align="right"><b>''' + str2HTML(tr('Leandro Franca', 'Leandro França')) + '''
</br>''' + tr('Cartographic Engineer', 'Eng. Cart&oacute;grafo') + '''<o:p></o:p></b></p>
</br>
<div align="right">'''+ Imgs().social_table_color + '''
</div>
<o:p></o:p></b></p>
</footer>
</body>
</html>
'''

    table_row = '''<tr style="">
      <td style="padding: 0cm 5.4pt; width: 84.9pt;"
 valign="top" width="113">
      <p class="MsoNormal"
 style="margin-bottom: 0.0001pt; text-align: center; line-height: normal;"
 align="center"><span style="">[ID]<o:p></o:p></span></p>
      </td>
      <td style="padding: 0cm 5.4pt; width: 84.95pt;"
 valign="top" width="113">
      <p class="MsoNormal"
 style="margin-bottom: 0.0001pt; text-align: center; line-height: normal;"
 align="center"><span style="">[Vx]<o:p></o:p></span></p>
      </td>
      <td style="padding: 0cm 5.4pt; width: 84.95pt;"
 valign="top" width="113">
      <p class="MsoNormal"
 style="margin-bottom: 0.0001pt; text-align: center; line-height: normal;"
 align="center"><span style="">[Vy]</span></p>
      </td>
    </tr>'''

    tabela = ''

    # Tabela de Residuos
    for ind, delta in enumerate(DELTA):
        tableRowN = table_row
        itens  = {'[ID]' : str(ind+1),
                     '[Vx]' : '{:.4f}'.format(float(delta[0])),
                     '[Vy]' : '{:.4f}'.format(float(delta[1])),
                     }
        for item in itens:
            tableRowN = tableRowN.replace(item, itens[item])
        tabela += tableRowN

    texto = texto.replace('[TABLE]', tabela)

    return COORD, PREC, CoordTransf, texto, CoordInvTransf



# Validação dos Pontos de Controle (GCP)
def ValidacaoGCP(lista, metodo):
    # número de feições por modelo matemático
    cont = len(lista)
    if metodo == 0:
        if cont < 1:
            raise QgsProcessingException(tr('It takes 1 or more GPC to perform this adjustment!', 'É necessario 1 ou mais GCP para realizar esse ajustamento!'))
    elif metodo == 1:
        if cont < 3:
            raise QgsProcessingException(tr('It takes 3 or more GPC to perform this adjustment!', 'É necessario 3 ou mais GCP para realizar esse ajustamento!'))


# Ajustamento Vertical
def AjustVertical(lista, metodo):
    # lista: [(Xa, Ya, Za), Zb] - ponto A - GCP, Zb - cota do MDE
    # Métodos:
    # 0 - constante, 1 - plano

    # numero de pontos homologos
    n_pnts_ctrl = len(lista)

    # numero minimo de pontos de controle por metodo
    if metodo == 0: # 0 - constante
        min_pnts_ctrl = n_pnts_ctrl == 1
    elif metodo == 1: # 1 - plano
        min_pnts_ctrl = n_pnts_ctrl == 3

    A = [] # Matriz Design
    L = [] # Coordenadas Finais
    Lo = [] # Coordenadas Iniciais
    for item in lista:
        xa = item[0][0]
        ya = item[0][1]
        za = item[1]
        zb = item[0][2]

        if metodo == 0:
            A += [[1]]
        elif metodo == 1:
            A += [[xa, ya, 1]]
        L +=[[zb]]
        Lo +=[[za]]

    A = np.matrix(A)
    L = np.matrix(L)
    Lo = np.matrix(Lo)

    msg_erro = tr('Inconsistent values, check your control points!', 'Valores inconsistentes, verifique seus pontos de controle!')
    if metodo == 0:
        X = (L - Lo).mean()
    elif metodo == 1:
        if min_pnts_ctrl:
            if det(A):
                X = solve(A, L - Lo)
            else:
                raise QgsProcessingException(msg_erro)
        else: # asjustamento
            M = A.T*A
            if det(M):
                X = solve(M, A.T*(L-Lo))
            else:
                raise QgsProcessingException(msg_erro)

    # Parametros e Função da Transformação
    if metodo == 0:
        a = X
        def CoordTransf(X, Y, a = a): # Transformação dz Plano
            '''
            dz = a
            '''
            dz = a
            return dz

    elif metodo == 1:
        a = X[0,0]
        b = X[1,0]
        c = X[2,0]
        def CoordTransf(X, Y, a = a, b = b, c = c): # Transformação dz Plano
            '''
            dz = X*a + Y*b + c
            '''
            dz = X*a + Y*b + c
            return dz

    # Cálculo do Resíduos
    V = []
    COTAS = []
    DELTA = []
    for item in lista:
        X = item[0][0]
        Y = item[0][1]
        Z = item[1]
        dz = CoordTransf(X, Y)
        Zaj = Z + dz
        COTAS += [Zaj]
        difer = Zaj - item[0][2]
        DELTA += [difer]
        V += [[difer]]

    # MVC dos Parametros e das coordenadas Ajustadas
    n = np.shape(A)[0] # número de observações
    u = np.shape(A)[1] # número de parâmetros
    V = np.matrix(V)
    if not min_pnts_ctrl:
        # Sigma posteriori
        sigma2 = V.T*V/(n-u)
        # Precisão dos Pontos Ajustados
        # MVC de Xa
        SigmaXa = sigma2[0,0]*inv(A.T*A)
        SigmaXa  = np.matrix(SigmaXa).astype(float)
        # MVC de La
        SigmaLa = A*SigmaXa*A.T
        SigmaLa  = np.matrix(SigmaLa).astype(float)
        # RMSE
        RMSE = np.sqrt((V.T*V)[0,0]/n_pnts_ctrl)
    else:
        sigma2 = 0
        RMSE = 0

    # Lista Precisões das Cotas Ajustadas
    PREC = (np.array(SigmaLa.diagonal())).tolist()

    if metodo == 0:
        formula = '''<p class="MsoNormal" style="text-align: center;"
 align="center"><i><span style="">''' + tr('Constant (XY Parallel Plane)','Constante (Plano Paralelo ao XY)') + '''</span></i></p>
<p class="MsoNormal" style="text-align: center;"
 align="center"><i><span style=""></span></i></p>
<p class="MsoNormal" style="text-align: center;"
 align="center"><i><span style="">Z = Zo</span></i><i><span
 style=""></span></i><i><span style="">
+ a +</span></i><i><span style=""> Vz<o:p></o:p></span></i></p>
'''
    elif metodo == 1:
        formula = '''<p class="MsoNormal" style="text-align: center;"
 align="center"><i><span style="">''' + str2HTML(tr('Plan as a function of X and Y','Plano em função de X e Y')) + '''</span></i></p>
<p class="MsoNormal" style="text-align: center;"
 align="center"><i><span style=""></span></i></p>
<p class="MsoNormal" style="text-align: center;"
 align="center"><i><span style="">Z = Zo</span></i><i><span
 style=""></span></i><i><span style="">
+aX + bY
+ c +</span></i><i><span style=""> Vz<o:p></o:p></span></i></p>
'''

    parametros = ''
    for k in range(u): # para cada parâmetro
        letra = chr(k+97)
        parametros += '''<p class="MsoNormal" style="text-align: center;"
align="center"><span style="">letrax
</span><span style="">=</span><span
style=""> [x]<o:p></o:p></span></p>
'''.replace('letrax', letra).replace('[x]', str(eval(letra)))


    texto = '''<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
<html>
<head>
<meta content="text/html; charset=ISO-8859-1"
http-equiv="content-type">
<title>'''+ str2HTML(tr('Vertical Adjustment','Ajuste Vertical')) + '''</title>
<link rel = "icon" href = "https://github.com/LEOXINGU/lftools/blob/main/images/lftools.png?raw=true" type = "image/x-icon">
</head>
<body
style="color: rgb(0, 0, 0); background-color: rgb(255, 255, 204);"
alink="#000099" link="#000099" vlink="#990099">
<p class="MsoNormal" style="text-align: center;"
align="center"><b><span
style="font-size: 12pt; line-height: 107%;"><o:p></o:p></span></b><span
style="font-weight: bold; text-decoration: underline;">'''+ str2HTML(tr('VERTICAL ADJUSTMENT','AJUSTE VERTICAL')) + ''' </span></p>
<p class="MsoNormal" style="text-align: center;"
align="center"><span style="font-style: italic;">''' + str2HTML(tr('Mathematical Formulation','Formulação Matemática')) + '''
</span></p>''' + formula + '''<p style="text-align: center;" class="MsoNormal"><b><span
style="">''' + str2HTML(tr('Residual Errors of Control Points','Erro residual dos Pontos de Controle')) + '''<o:p></o:p></span></b></p>
<table
style="border: medium none ; border-collapse: collapse; text-align: left; margin-left: auto; margin-right: auto;"
class="MsoTableGrid" border="0" cellpadding="0"
cellspacing="0">
<tbody>
<tr style="">
  <td style="padding: 0cm 5.4pt; width: 84.9pt;"
valign="top" width="113">
  <p class="MsoNormal"
style="margin-bottom: 0.0001pt; text-align: center; line-height: normal;"
align="center"><i><span style="">''' + str2HTML(tr('Point','Ponto')) + '''<o:p></o:p></span></i></p>
  </td>
  <td style="padding: 0cm 5.4pt; width: 84.95pt;"
valign="top" width="113">
  <p class="MsoNormal"
style="margin-bottom: 0.0001pt; text-align: center; line-height: normal;"
align="center"><i><span style="">Vz<o:p></o:p></span></i></p>
  </td>
</tr>
[TABLE]
</tbody>
</table>
<br>
<div>
<p class="MsoNormal" style="text-align: center;"
align="center"><b><span style="">''' + str2HTML(tr('Transformation Parameters:','Parâmetros de Transformação:')) + '''<o:p></o:p></span></b></p>
''' + parametros + '''
<div style="text-align: center;"><b><span style=""
>''' + str2HTML(tr('Adjustment Reference Variance','Variância a posteriori')) + '''</span></b><span style=""
> <span style="">&nbsp;</span>=
</span><span style="">''' + str(round(sigma2[0,0],4)) + '''</span></div>
<br>
<div style="text-align: center;"><b><span style=""
>''' + str2HTML(tr('Root Mean Square Error (RMSE)','Raiz do Erro Médio Quadrático (REMQ)')) + '''</span></b><span style=""
> <span style="">&nbsp;</span>=
</span><span style="">''' + str(round(RMSE,4)) + '''</span></div>

</div>
<footer">
<p class="MsoNormal" style="margin-bottom: 0.0001pt; text-align: right;" align="right"><b>''' + str2HTML(tr('Leandro Franca', 'Leandro França')) + '''
</br>''' + tr('Cartographic Engineer', 'Eng. Cart&oacute;grafo') + '''<o:p></o:p></b></p>
</br>
<div align="right">'''+ Imgs().social_table_color + '''
</div>
<o:p></o:p></b></p>
</footer>
</body>
</html>
'''

    table_row = '''<tr style="">
      <td style="padding: 0cm 5.4pt; width: 84.9pt;"
 valign="top" width="113">
      <p class="MsoNormal"
 style="margin-bottom: 0.0001pt; text-align: center; line-height: normal;"
 align="center"><span style="">[ID]<o:p></o:p></span></p>
      </td>
      <td style="padding: 0cm 5.4pt; width: 84.95pt;"
 valign="top" width="113">
      <p class="MsoNormal"
 style="margin-bottom: 0.0001pt; text-align: center; line-height: normal;"
 align="center"><span style="">[Vz]<o:p></o:p></span></p>
      </td>
    </tr>'''

    tabela = ''

    # Tabela de Residuos
    for ind, delta in enumerate(DELTA):
        tableRowN = table_row
        itens  = {'[ID]' : str(ind+1),
                     '[Vz]' : '{:.4f}'.format(float(delta)),
                     }
        for item in itens:
            tableRowN = tableRowN.replace(item, itens[item])
        tabela += tableRowN

    texto = texto.replace('[TABLE]', tabela)

    return COTAS, PREC[0], DELTA, CoordTransf, texto
