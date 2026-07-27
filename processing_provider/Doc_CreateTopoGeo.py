# -*- coding: utf-8 -*-

"""
Doc_CreateTopoGeo.py
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
__date__ = '2026-07-26'
__copyright__ = '(C) 2026, Leandro França'

import os
import processing

from qgis.PyQt.QtGui import QIcon
from qgis.core import (
    QgsApplication,
    QgsCoordinateReferenceSystem,
    QgsProcessingAlgorithm,
    QgsProcessingException,
    QgsProcessingParameterBoolean,
    QgsProcessingParameterCrs,
    QgsProcessingParameterFileDestination,
    QgsProject,
    QgsVectorLayer,
)

from lftools.geocapt.imgs import Imgs
from lftools.translations.translate import translate


class CreateTopoGeo(QgsProcessingAlgorithm):

    LOC = QgsApplication.locale()[:2]

    def tr(self, *string):
        return translate(string, self.LOC)

    def createInstance(self):
        return CreateTopoGeo()

    def name(self):
        return 'createtopogeo'

    def displayName(self):
        return self.tr('TopoGeo - Create Demo', 'TopoGeo - Criar Demo')

    def group(self):
        return self.tr('Documents', 'Documentos')

    def groupId(self):
        return 'documents'

    def tags(self):
        return 'GeoOne,TopoGeo,demo,template,GeoPackage,GPKG,database,copy,reproject,CRS,GeoOne,TopoGeo,demonstração,modelo,GeoPackage,GPKG,banco de dados,copiar,reprojetar,SRC'.split(',')

    def icon(self):
        return QIcon(
            os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                'images',
                'document.png'
            )
        )

    def flags(self):
        # The layers are inserted directly into the current QGIS project after
        # the child algorithm finishes. Therefore, this algorithm must run in
        # the main thread.
        return super().flags() | QgsProcessingAlgorithm.FlagNoThreading

    txt_en = '''This tool creates a new GeoPackage file based on the simplified <b>TopoGeo Demo</b> template.

<p>
The generated database contains the minimum set of layers required to use the automated documentation tools available in the <b>LFTools</b> plugin, such as the generation of Survey Descriptions and other technical documents.
</p>

<h3>Generated layers</h3>

<ul>
  <li><code>limit_point_p</code></li>
  <li><code>boundary_element_l</code></li>
  <li><code>property_area_a</code></li>
  <li><code>reference_point_p</code> — optional</li>
</ul>

<h3>Important notes</h3>

<p>
<b>1.</b> The <code>reference_point_p</code> layer is used exclusively to generate the <b>Geodetic mark report</b>.
</p>

<p>
<b>2.</b> For the LFTools documentation tools to work correctly, the Coordinate Reference System (CRS) of the database must be <b>Geographic</b>.
</p>
'''


    txt_pt = '''Esta ferramenta cria um novo arquivo GeoPackage a partir do modelo simplificado <b>TopoGeo Demo</b>.

<p>
O banco de dados gerado contém o conjunto mínimo de camadas necessário para utilizar as ferramentas de documentação automatizada disponíveis no plugin <b>LFTools</b>, como a geração do Memorial Descritivo e de outras peças técnicas.
</p>

<h3>Camadas geradas</h3>

<ul>
  <li><code>limit_point_p</code></li>
  <li><code>boundary_element_l</code></li>
  <li><code>property_area_a</code></li>
  <li><code>reference_point_p</code> — opcional</li>
</ul>

<h3>Observações importantes</h3>

<p>
<b>1.</b> A camada <code>reference_point_p</code> é utilizada exclusivamente para a geração da <b>Monografia do Marco Geodésico</b>.
</p>

<p>
<b>2.</b> Para que as ferramentas de documentação do LFTools funcionem corretamente, o Sistema de Referência de Coordenadas (<b>SRC</b>) do banco de dados deve ser geográfico.
</p>
'''

    figure = 'images/tutorial/vect_createTopoGeo.jpg'

    def shortHelpString(self):
        social_BW = Imgs().social_BW
        footer = '''<div align="center">
                      <img src="'''+ os.path.join(os.path.dirname(os.path.dirname(__file__)), self.figure) +'''">
                      </div>
                      <div align="right">
                      <p align="right">
                      <b>'''+self.tr('Author: Leandro Franca', 'Autor: Leandro França')+'''</b>
                      </p>'''+ social_BW + '''</div>
                      '''
        return self.tr(self.txt_en, self.txt_pt) + footer

    OUTPUT = 'OUTPUT'
    CRS = 'CRS'
    PROJECTED = 'PROJECTED'
    LOAD_REFERENCE = 'LOAD_REFERENCE'

    def initAlgorithm(self, config=None):

        self.addParameter(
            QgsProcessingParameterCrs(
                self.CRS,
                self.tr('Output CRS', 'SRC de saída'),
                defaultValue=QgsCoordinateReferenceSystem('EPSG:4674')
            )
        )
        
        self.addParameter(
            QgsProcessingParameterBoolean(
                self.PROJECTED,
                self.tr('Allow projected CRS', 'Permitir SRC projetado'),
                defaultValue = False
            )
        )

        self.addParameter(
            QgsProcessingParameterBoolean(
                self.LOAD_REFERENCE,
                self.tr(
                    'Load GNSS reference point layer',
                    'Carregar camada de pontos de referência GNSS'
                ),
                defaultValue=False,
                optional=True
            )
        )

        self.addParameter(
            QgsProcessingParameterFileDestination(
                self.OUTPUT,
                self.tr('Output TopoGeo GeoPackage', 'GeoPackage TopoGeo de saída'),
                fileFilter='GeoPackage (*.gpkg)'
            )
        )

    def processAlgorithm(self, parameters, context, feedback):

        output_gpkg = self.parameterAsFileOutput(
            parameters,
            self.OUTPUT,
            context
        )
        if not output_gpkg:
            raise QgsProcessingException(
                self.invalidSinkError(parameters, self.OUTPUT)
            )

        if os.path.exists(output_gpkg):
            raise QgsProcessingException(
                self.tr(
                    'The output file already exists! Choose another file name or remove the existing GeoPackage.',
                    'O arquivo de saída já existe! Escolha outro nome ou remova o GeoPackage existente.'
                )
            )

        output_directory = os.path.dirname(output_gpkg)
        if not os.path.isdir(output_directory):
            raise QgsProcessingException(
                self.tr(
                    'The selected output directory does not exist!',
                    'A pasta de saída selecionada não existe!'
                )
            )
        
        print(output_gpkg )
        print( output_directory)

        output_crs = self.parameterAsCrs(
            parameters,
            self.CRS,
            context
        )
        if not output_crs.isValid():
            raise QgsProcessingException(
                self.tr('Invalid output CRS.', 'SRC de saída inválido.')
            )

        load_reference = self.parameterAsBool(
            parameters,
            self.LOAD_REFERENCE,
            context
        )

        plugin_root = os.path.dirname(os.path.dirname(__file__))
        template_gpkg = os.path.join(
            plugin_root,
            'templates',
            'TopoGeo_Demo.gpkg'
        )
        
        Projetado = self.parameterAsBool(
            parameters,
            self.PROJECTED,
            context
        )

        if not os.path.isfile(template_gpkg):
            raise QgsProcessingException(
                self.tr(
                    'The TopoGeo Demo template was not found at: {}',
                    'O modelo TopoGeo Demo não foi encontrado em: {}'
                ).format(template_gpkg)
            )
        
        if not Projetado:
            if not output_crs.isGeographic():
                raise QgsProcessingException(self.tr('Choose a geographic CRS!', 'Escolha um SRC geográfico!'))

        if not output_crs.isGeographic():
            feedback.reportError(
                self.tr(
                    'Warning: a projected CRS was selected. The LFTools tools for generating survey documents only work with geographic CRSs.',
                    'Aviso: foi selecionado um SRC projetado. As ferramentas do LFTools para geração de documentação funcionam apenas com SRCs geográficos.'
                ),
                fatalError=False
            )

        feedback.pushInfo(
            self.tr(
                'Creating TopoGeo Demo in {}...',
                'Criando o TopoGeo Demo em {}...'
            ).format(output_gpkg)
        )

        # Reuse the existing LFTools algorithm so all layers from the template
        # are copied and reprojected consistently.
        reproject_params = {
            'INPUT': template_gpkg,
            'CRS': output_crs,
            'PROJECTED': Projetado,
            'INSTANTIATED': False,
            'OUTPUT': output_gpkg,
        }

        result = processing.run(
            'lftools:reprojectgpkg',
            reproject_params,
            context=context,
            feedback=feedback,
            is_child_algorithm=True
        )

        created_gpkg = result.get('OUTPUT', output_gpkg)
        if not created_gpkg or not os.path.isfile(created_gpkg):
            raise QgsProcessingException(
                self.tr(
                    'The TopoGeo GeoPackage could not be created.',
                    'Não foi possível criar o GeoPackage TopoGeo.'
                )
            )

        main_layers = [
            'limit_point_p',
            'boundary_element_l',
            'property_area_a',
        ]

        project = QgsProject.instance()
        root = project.layerTreeRoot()

        # Pasta de estilos do LFTools.
        styles_directory = os.path.join(
            plugin_root,
            'styles'
        )

        # Associação entre cada camada e seu respectivo arquivo QML.
        layer_styles = {
            'limit_point_p': 'TopoGeo_limit_point_p.qml',
            'boundary_element_l': 'TopoGeo_boundary_element_l.qml',
            'property_area_a': 'TopoGeo_property_area_a.qml',
            'reference_point_p': 'TopoGeo_reference_point_p.qml',
        }

        # Posição onde o grupo será inserido na árvore de camadas.
        insert_index = 0

        # Cria o grupo principal.
        group = root.insertGroup(
            insert_index,
            'TopoGeo Demo'
        )
        group.setExpanded(True)


        def load_gpkg_layer(layer_name):
            """
            Loads a GeoPackage layer and applies its corresponding QML style.
            """

            layer_uri = '{}|layername={}'.format(
                created_gpkg,
                layer_name
            )

            layer = QgsVectorLayer(
                layer_uri,
                layer_name,
                'ogr'
            )

            if not layer.isValid():
                feedback.reportError(
                    self.tr(
                        'The layer "{}" could not be loaded.',
                        'A camada "{}" não pôde ser carregada.'
                    ).format(layer_name),
                    fatalError=False
                )
                return None

            # Identifica o arquivo de estilo correspondente à camada.
            style_filename = layer_styles.get(layer_name)

            if style_filename:
                style_path = os.path.join(
                    styles_directory,
                    style_filename
                )

                if os.path.isfile(style_path):

                    message, style_loaded = layer.loadNamedStyle(
                        style_path
                    )

                    if style_loaded:
                        feedback.pushInfo(
                            self.tr(
                                'Style applied to layer "{}".',
                                'Estilo aplicado à camada "{}".'
                            ).format(layer_name)
                        )
                    else:
                        feedback.reportError(
                            self.tr(
                                'The style could not be applied to layer "{}": {}',
                                'Não foi possível aplicar o estilo à camada "{}": {}'
                            ).format(layer_name, message),
                            fatalError=False
                        )

                else:
                    feedback.reportError(
                        self.tr(
                            'Style file not found: {}',
                            'Arquivo de estilo não encontrado: {}'
                        ).format(style_path),
                        fatalError=False
                    )

            # Atualiza a representação da camada após carregar o estilo.
            layer.triggerRepaint()

            # Registra a camada no projeto sem inseri-la automaticamente
            # na árvore de camadas.
            project.addMapLayer(
                layer,
                False
            )

            return layer


        # Carrega as três camadas principais dentro do grupo TopoGeo Demo.
        for group_index, layer_name in enumerate(main_layers):

            layer = load_gpkg_layer(layer_name)

            if layer is not None:
                group.insertLayer(
                    group_index,
                    layer
                )

                feedback.pushInfo(
                    self.tr(
                        'Layer "{}" loaded.',
                        'Camada "{}" carregada.'
                    ).format(layer_name)
                )


        # Carrega a camada opcional fora do grupo e imediatamente abaixo dele.
        if load_reference:

            reference_layer = load_gpkg_layer(
                'reference_point_p'
            )

            if reference_layer is not None:
                root.insertLayer(
                    insert_index + 1,
                    reference_layer
                )

                feedback.pushInfo(
                    self.tr(
                        'Layer "{}" loaded.',
                        'Camada "{}" carregada.'
                    ).format('reference_point_p')
                )

        feedback.pushInfo(
            self.tr(
                'TopoGeo Demo created successfully!',
                'TopoGeo Demo criado com sucesso!'
            )
        )
        feedback.pushInfo(
            self.tr(
                'Leandro Franca - Cartographic Engineer',
                'Leandro França - Eng. Cartógrafo'
            )
        )

        return {self.OUTPUT: created_gpkg}
