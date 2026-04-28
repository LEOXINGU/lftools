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
__date__ = '2021-03-01'
__copyright__ = '(C) 2021, Leandro França'

import os
import base64
from lftools.dependencies import ensure_pillow

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
ICONS_DIR = os.path.join(BASE_DIR, 'images', 'icons')


# Imagem para HTML
def img2html(path_file):
    arq = open(path_file, 'rb')
    leitura = arq.read()
    arq.close()
    encoded = base64.b64encode(leitura)
    texto = str(encoded)[2:-1]
    return texto

# Redimensionar Imagem
def ImgResize(path_file, lado, resized):
    Image = ensure_pillow()
    if Image is None:
        raise ImportError(
            "Pillow (PIL) is required but could not be loaded. Try to install it using pip: pip install Pillow"
        )
    caminho, arquivo = os.path.split(path_file)
    img = Image.open(path_file)
    altura = img.size[1]
    largura = img.size[0]
    if largura < altura:
        new_height = lado
        new_width =int(lado/float(altura)*largura)
    else:
        new_width = lado
        new_height =int(lado/float(largura)*altura)

    img = img.resize((new_width, new_height))
    path_file_reduced = os.path.join(caminho, resized)
    img.save(path_file_reduced)
    del img
    return path_file_reduced

# Imagem para HTML redimensionada
def img2html_resized(path_file, lado=500, resized = 'reduzido.jpg'):
    if os.path.isfile(path_file):
        caminho, arquivo = os.path.split(path_file)
        path_file_reduced = ImgResize(path_file, lado, resized)
        texto = img2html(path_file_reduced)
        os.remove(path_file_reduced)
        return texto
    else:
        return ''

def img_file_to_base64(filename):
    path = os.path.join(ICONS_DIR, filename)

    if not os.path.isfile(path):
        raise FileNotFoundError(f'Image file not found: {path}')

    with open(path, 'rb') as f:
        return base64.b64encode(f.read()).decode('ascii')
    

# icons and logos
dic_color = {
    'face': img_file_to_base64('face.png'),
    'g1': img_file_to_base64('g1.png'),
    'github': img_file_to_base64('github.png'),
    'instagram': img_file_to_base64('instagram.png'),
    'lattes': img_file_to_base64('lattes.png'),
    'linkedin': img_file_to_base64('linkedin.png'),
    'RG': img_file_to_base64('RG.png'),
    'twitter': img_file_to_base64('twitter.png'),
    'udemy': img_file_to_base64('udemy.png'),
    'youtube': img_file_to_base64('youtube.png'),
}

lftools_logo = img_file_to_base64('lftools.png')

geom_icons = {
    'ponto': img_file_to_base64('ponto.png'),
    'linha': img_file_to_base64('linha.png'),
    'area': img_file_to_base64('area.png'),
    'nogeom': img_file_to_base64('nogeom.png'),
}

class Imgs:
    social_BW = '''<a target="_blank" rel="noopener noreferrer" href="https://www.geoone.com.br"><img title="GeoOne" src="data:image/png;base64,'''+dic_color['g1']+'''"></a> <a target="_blank" rel="noopener noreferrer" href="https://www.youtube.com/leandrofranca"><img title="Youtube" src="data:image/png;base64,'''+dic_color['youtube']+'''"></a> <a target="_blank" rel="noopener noreferrer" href="https://www.facebook.com/geoleandrofranca/"><img title="Facebook" src="data:image/png;base64,'''+dic_color['face']+'''"></a> <a target="_blank" rel="noopener noreferrer" href="https://www.linkedin.com/in/leandro-fran%C3%A7a-93093714b/"><img title="Linkedin" src="data:image/png;base64,'''+dic_color['linkedin']+'''"></a> <a target="_blank" rel="noopener noreferrer" href="https://www.researchgate.net/profile/Leandro_Franca2"><img title="ResearchGate" src="data:image/png;base64,'''+dic_color['RG']+'''"></a> <a target="_blank" rel="noopener noreferrer" href="https://www.instagram.com/geoleandrofranca/"><img title="Instagram" src="data:image/png;base64,''' + dic_color['instagram'] + '''"></a> <a target="_blank" rel="noopener noreferrer" href="http://lattes.cnpq.br/8559852745183879"><img title="Lattes" src="data:image/png;base64,''' + dic_color['lattes'] + '''"></a>'''

    social_table_color = '''<table style="text-align: right;" border="0"
     cellpadding="2" cellspacing="2">
      <tbody>
        <tr>
          <td><a target="_blank" rel="noopener noreferrer" href="https://www.geoone.com.br">
          <img title="GeOne" style="border: 0px solid ; width: 28px; height: 28px;" alt="udemy"
           src="data:image/png;base64,'''+dic_color['g1']+'''">
           </a>
          </td>
          <td><a target="_blank" rel="noopener noreferrer" href="https://www.youtube.com/leandrofranca">
          <img title="Youtube" style="border: 0px solid ; width: 28px; height: 28px;" alt="youtube"
           src="data:image/png;base64,'''+dic_color['youtube']+'''">
           </a>
          </td>
          <td><a target="_blank" rel="noopener noreferrer" href="https://www.facebook.com/geoleandrofranca/">
          <img title="Facebook" style="border: 0px solid ; width: 28px; height: 28px;" alt="facebook"
           src="data:image/png;base64,'''+dic_color['face']+'''">
           </a>
          </td>
          <td><a target="_blank" rel="noopener noreferrer" href="https://www.linkedin.com/in/leandro-fran%C3%A7a-93093714b/">
          <img title="Linkedin" style="border: 0px solid ; width: 28px; height: 28px;" alt="linkedin"
           src="data:image/png;base64,'''+dic_color['linkedin']+'''">
           </a>
          </td>
          <td><a target="_blank" rel="noopener noreferrer" href="https://www.researchgate.net/profile/Leandro_Franca2">
          <img title="ResearchGate" style="border: 0px solid ; width: 28px; height: 28px;" alt="RG"
           src="data:image/png;base64,'''+dic_color['RG']+'''">
           </a>
          </td>
          <td><a target="_blank" rel="noopener noreferrer" href="https://www.instagram.com/geoleandrofranca/">
          <img title="Linkedin" style="border: 0px solid ; width: 28px; height: 28px;" alt="linkedin"
           src="data:image/png;base64,'''+dic_color['instagram']+'''">
           </a>
          </td>
          <td><a target="_blank" rel="noopener noreferrer" href="http://lattes.cnpq.br/8559852745183879">
          <img title="Lattes" style="border: 0px solid ; width: 28px; height: 28px;" alt="lattes"
           src="data:image/png;base64,'''+dic_color['lattes']+'''">
           </a>
          </td>
        </tr>
      </tbody>
    </table>'''
