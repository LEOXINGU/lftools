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
__date__ = '2025-12-25'
__copyright__ = '(C) 2025 Leandro França'

import math
import numpy as np
import os
from PIL import Image
from qgis.core import QgsProcessingException


# Nome das faces
FACE_NAMES = {
    ('x',  1): '+X',
    ('x', -1): '-X',
    ('y',  1): '+Y',
    ('y', -1): '-Y',
    ('z',  1): '+Z',
    ('z', -1): '-Z',
}

# Tabela que define como calcular (u, v)
# Para a projeção: qual componente vai em u e qual em v
# u = a / dominant
# v = b / dominant
UV_TABLE = {
    'x': ('y', 'z'),
    'y': ('x', 'z'),
    'z': ('x', 'y')
}


# Tabela para reconstrução: eixo dominante e ordem dos eixos
# Para o inverso: eixo dominante, sinal e ordem de u/v
RECON_TABLE = {
    '+X': ('x',  1, ('y', 'z')),
    '-X': ('x', -1, ('y', 'z')),
    '+Y': ('y',  1, ('x', 'z')),
    '-Y': ('y', -1, ('x', 'z')),
    '+Z': ('z',  1, ('x', 'y')),
    '-Z': ('z', -1, ('x', 'y'))
}


def latlon_to_cube(lat, lon):
    """
    Converte latitude e longitude (graus) para:
      - face do cubo: '+X', '-X', '+Y', '-Y', '+Z', '-Z'
      - coordenadas planas u, v em [-1, 1]
    """

    # 1) Graus -> radianos
    phi = math.radians(lat)
    lam = math.radians(lon)

    # 2) Esfera unidade
    x = math.cos(phi) * math.cos(lam)
    y = math.cos(phi) * math.sin(lam)
    z = math.sin(phi)

    vec = [x, y, z]
    axes = ['x', 'y', 'z']

    # 3) Eixo dominante: empates quebrados na ordem X > Y > Z
    idx = max(range(3), key=lambda i: abs(vec[i]))
    axis = axes[idx]
    compA = vec[idx]

    # 4) Sinal da componente dominante
    sign = 1 if compA >= 0 else -1

    # 5) Nome da face
    face = FACE_NAMES[(axis, sign)]

    # 6) Cálculo de u e v (fórmula genérica)
    comps = {'x': x, 'y': y, 'z': z}
    u_axis, v_axis = UV_TABLE[axis]

    denom = compA  # componente dominante original

    u = (comps[u_axis] / denom) * sign
    v = (comps[v_axis] / denom) * sign

    return face, u, v



def cube_to_latlon(face, u, v):
    """
    Converte:
      - face: '+X', '-X', '+Y', '-Y', '+Z', '-Z'
      - u, v em [-1, 1]
    para:
      - latitude (graus)
      - longitude (graus)
    """

    # 1) Clamping para limites numéricos
    u = max(-1.0, min(1.0, u))
    v = max(-1.0, min(1.0, v))

    dominant_axis, sign, (u_axis, v_axis) = RECON_TABLE[face]

    # 2) Reconstrói vetor não normalizado
    comps = {'x': 0.0, 'y': 0.0, 'z': 0.0}

    # eixo dominante leva o sinal da face
    comps[dominant_axis] = float(sign)

    # u e v entram direto nos eixos secundários (sem sign!)
    comps[u_axis] = float(u)
    comps[v_axis] = float(v)

    x, y, z = comps['x'], comps['y'], comps['z']

    # 3) Normaliza
    r = math.sqrt(x*x + y*y + z*z)
    x /= r
    y /= r
    z /= r

    # 4) Vetor -> lat/lon
    lat = math.degrees(math.asin(z))
    lon = math.degrees(math.atan2(y, x))

    return lat, lon



def latlon_to_cube_np(lat, lon, feedback=None):
    """
    Recebe lat e lon como matrizes 2D (H x W).
    Retorna:
        face_map: matriz de strings (H x W)
        u, v: matrizes numéricas (H x W)
    """

    # 1) Graus → radianos
    lat_rad = np.radians(lat)
    lon_rad = np.radians(lon)
    
    feedback.setProgress(10)


    # 2) Coordenadas cartesianas da esfera unidade
    x = np.cos(lat_rad) * np.cos(lon_rad)
    y = np.cos(lat_rad) * np.sin(lon_rad)
    z = np.sin(lat_rad)
    
    feedback.setProgress(20)

    # 3) empilha como (3, H, W)
    xyz = np.stack([x, y, z], axis=0)
    abs_xyz = np.abs(xyz)
    
    feedback.setProgress(30)

    # 4) eixo dominante: idx ∈ {0,1,2} com shape (H,W)
    idx = np.argmax(abs_xyz, axis=0)

    axes = np.array(["x", "y", "z"])
    face_axis = axes[idx]   # matriz H×W com 'x','y','z'
    
    feedback.setProgress(40)

    # 5) componente dominante: extraída por máscara
    dominant_vals = np.take_along_axis(xyz, idx[None, :, :], axis=0)[0]
    
    feedback.setProgress(50)

    # 6) sinal da face
    sign = np.where(dominant_vals >= 0, 1, -1)

    signs_char = np.where(sign > 0, "+", "-")
    face_map = np.char.add(signs_char, np.char.upper(face_axis))
    
    feedback.setProgress(60)

    # 7) lookup dos eixos que formam u e v
    uv_tbl = {"x": ("y", "z"), "y": ("x", "z"), "z": ("x", "y")}
    axis_idx = {"x": 0, "y": 1, "z": 2}

    # converte face_axis em arrays de índices
    u_axis = np.vectorize(lambda a: uv_tbl[a][0])(face_axis)
    v_axis = np.vectorize(lambda a: uv_tbl[a][1])(face_axis)

    u_idx = np.vectorize(axis_idx.get)(u_axis)
    v_idx = np.vectorize(axis_idx.get)(v_axis)
    
    feedback.setProgress(70)

    # 8) extrair componentes u e v
    u_vals = np.take_along_axis(xyz, u_idx[None, :, :], axis=0)[0]
    v_vals = np.take_along_axis(xyz, v_idx[None, :, :], axis=0)[0]
    
    feedback.setProgress(80)

    # 9) calcular u e v finais
    u = (u_vals / dominant_vals) * sign
    v = (v_vals / dominant_vals) * sign
    
    feedback.setProgress(90)

    return face_map, u, v


# # Exemplo de teste
# lat, lon = -8, -49

# face, u, v = latlon_to_cube(lat, lon)
# print("Forward:", face, u, v)

# lat2, lon2 = cube_to_latlon(face, u, v)
# print("Back:", lat2, lon2)


def cube_to_latlon_np_single_face(face, u, v):
    """
    Aceita u e v como matrizes N×N e retorna lat/lon também N×N.
    """

    # guarda formato original
    shape = u.shape      # ex.: (1024,1024)
    N_total = u.size     # ex.: 1048576

    # achatar arrays para 1D
    u = u.reshape(-1)
    v = v.reshape(-1)

    # clipping
    u = np.clip(u, -1.0, 1.0)
    v = np.clip(v, -1.0, 1.0)

    # sinal da face
    sign = 1 if face[0] == "+" else -1

    # eixo dominante
    axis = face[1].lower()

    axis_to_idx = {"x": 0, "y": 1, "z": 2}
    uv_tbl = {
        "x": ("y", "z"),
        "y": ("x", "z"),
        "z": ("x", "y"),
    }

    u_axis, v_axis = uv_tbl[axis]
    dom_idx = axis_to_idx[axis]
    u_idx  = axis_to_idx[u_axis]
    v_idx  = axis_to_idx[v_axis]

    # constrói matriz xyz (3 × N)
    xyz = np.zeros((3, N_total))
    xyz[dom_idx] = sign
    xyz[u_idx]   = u
    xyz[v_idx]   = v

    # normalização
    norm = np.linalg.norm(xyz, axis=0)
    xyz /= norm

    x, y, z = xyz

    # conversão final
    lat = np.degrees(np.arcsin(z))
    lon = np.degrees(np.arctan2(y, x))

    # remodela para o formato original N×N
    lat = lat.reshape(shape)
    lon = lon.reshape(shape)

    return lat, lon



def uv_grid(N):
    """
    Gera grade (u, v) para uma face do cubo, com u,v em [-1, 1],
    correspondendo aos CENTROS dos pixels de uma imagem N x N.

    u: -1 -> esquerda, +1 -> direita
    v: -1 -> baixo,    +1 -> cima
    """
    # índices de colunas e linhas (0..N-1)
    j = np.arange(N) + 0.5  # colunas (x)
    i = np.arange(N) + 0.5  # linhas (y)

    # mapeia para [-1, 1]
    u_1d = 2.0 * (j / N) - 1.0            # esquerda (-1) -> direita (+1)
    v_1d = 1.0 - 2.0 * (i / N)            # topo (+1) -> baixo (-1)

    # cria grade 2D
    u, v = np.meshgrid(u_1d, v_1d)

    return u, v



def generate_cube_face_from_image(img_np, face, N=2048):

    H, W, _ = img_np.shape

    # 1) grade u,v
    u, v = uv_grid(N)

    # 2) u,v -> lat,lon
    lat, lon = cube_to_latlon_np_single_face(face, u, v)

    # 3) lat/lon -> coordenadas reais x,y no espaço da imagem
    x = (lon + 180.0) / 360.0 * W
    y = (90.0 - lat) / 180.0 * H

    # 4) nearest neighbor baseado no centro do pixel
    xi = np.round(x - 0.5).astype(np.int32)
    yi = np.round(y - 0.5).astype(np.int32)

    # impedir extrapolação
    xi = np.clip(xi, 0, W - 1)
    yi = np.clip(yi, 0, H - 1)

    # 5) amostragem
    face_img = img_np[yi, xi]

    return face_img




def load_cube_faces(folder, feedback=None):
    """
    Carrega os 6 arquivos PNG das faces de um cubemap no formato:
        <basename>_+X.png, <basename>_-X.png, ...
    onde <basename> é o nome do arquivo original (ex.: foto360).
    A pasta normalmente se chama <basename>_faces.
    """

    required = ["+X", "-X", "+Y", "-Y", "+Z", "-Z"]
    faces = {}

    # Ex.: folder = ".../foto360_faces" -> basename = "foto360"
    folder_name = os.path.basename(folder)
    if folder_name.lower().endswith("_faces"):
        basename = folder_name[:-6]  # remove "_faces"
    else:
        # fallback: usa o nome da pasta como basename
        basename = folder_name

    for f in required:
        filename = os.path.join(folder, f"{basename}_{f}.png")
        if not os.path.exists(filename):
            raise QgsProcessingException( FileNotFoundError(f"File not found: {filename}. Verify if the files have the same name of the folder!") )
        img = Image.open(filename).convert("RGB")
        faces[f] = np.array(img)

    return faces



def rebuild_equirectangular(faces, H, feedback=None):
    """
    faces: dicionário com np.array das faces editadas
    H: altura da imagem equiretangular final (W = 2H)

    Retorna: imagem equiretangular reconstruída (np.array HxWx3)
    """

    W = 2 * H
    out = np.zeros((H, W, 3), dtype=np.uint8)

    # 1) grade da imagem equiretangular
    j = np.arange(W) + 0.5
    i = np.arange(H) + 0.5

    lon = (j / W) * 360.0 - 180.0         # graus
    lat = 90.0 - (i / H) * 180.0          # graus

    lon, lat = np.meshgrid(lon, lat)

    # 2) converter lat/lon → face + u,v
    face_map, u, v = latlon_to_cube_np(lat, lon, feedback=feedback)

    # 3) preencher a imagem final
    for f in ["+X", "-X", "+Y", "-Y", "+Z", "-Z"]:
        feedback.pushInfo(f'Filling face {f}...')
        mask = (face_map == f)
        if not np.any(mask):
            continue

        img_face = faces[f]
        N = img_face.shape[0]   # face NxN

        # converter u,v para coordenadas da face
        x = (u[mask] + 1) * 0.5 * (N - 1)
        y = (1 - v[mask]) * 0.5 * (N - 1)

        xi = np.round(x).astype(int)
        yi = np.round(y).astype(int)

        xi = np.clip(xi, 0, N - 1)
        yi = np.clip(yi, 0, N - 1)

        out[mask] = img_face[yi, xi]

    return out



def cube_faces_to_equirect(folder, output_path, H, exif_data=None, feedback=None):
    """
    Carrega as faces de uma pasta, reconstrói a equiretangular e salva no disco.
    H: altura da imagem equiretangular final.
    exif_data: bytes do EXIF original (opcional).
    """

    feedback.pushInfo('Loading faces...')
    faces = load_cube_faces(folder, feedback=feedback)

    feedback.pushInfo('Rebuilding equirectangular image...')
    eq = rebuild_equirectangular(faces, H, feedback=feedback)

    img_eq = Image.fromarray(eq)

    if exif_data is not None:
        img_eq.save(output_path, exif=exif_data)
    else:
        img_eq.save(output_path)

    feedback.setProgress(100)


