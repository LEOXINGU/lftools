# -*- coding: utf-8 -*-

"""
Drone_exportToDJI_KML.py
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
__date__ = '2026-03-07'
__copyright__ = '(C) 2026, Leandro França'

from qgis.core import (
    QgsApplication,
    QgsProcessingParameterVectorLayer,
    QgsProcessing,
    QgsCoordinateReferenceSystem,
    QgsCoordinateTransform,
    QgsProject,
    QgsProcessingParameterFileDestination,
    QgsProcessingException,
    QgsProcessingAlgorithm,
    QgsGeometry
)
from lftools.geocapt.imgs import Imgs
from xml.sax.saxutils import escape
from lftools.translations.translate import translate
import os
from qgis.PyQt.QtGui import QIcon


class ExportToDJI_KML(QgsProcessingAlgorithm):

    LOC = QgsApplication.locale()[:2]

    POLYGON = 'POLYGON'
    FILE = 'FILE'    

    def tr(self, *string):
        return translate(string, self.LOC)

    def createInstance(self):
        return ExportToDJI_KML()

    def name(self):
        return 'ExportToDJI_KML'.lower()

    def displayName(self):
        return self.tr(
            'Export Flight Area to DJI KML',
            'Exportar área de voo para KML da DJI'
        )

    def group(self):
        return self.tr('Drones')

    def groupId(self):
        return 'drones'

    def tags(self):
        return 'drone,drones,flight,planner,flight area,dji,kml,kmz,google earth,polygon,export,voo,planejamento,área de voo,dji,kml,kmz,google earth,polígono,exportar'.split(',')

    def icon(self):
        return QIcon(
            os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                'images/drone.png'
            )
        )
    
    txt_en = '''Exports polygon features to a simplified KML compatible with DJI flight controllers.
            Multipart geometries are reduced to the first polygon part, interior rings are removed, and the output is automatically transformed to WGS84 (EPSG:4326).'''
    txt_pt = '''Exporta feições poligonais para um KML simplificado compatível com controles de voo da DJI.
            Geometrias multipartes são reduzidas à primeira parte do polígono, anéis internos são removidos e a saída é automaticamente transformada para WGS84 (EPSG:4326).'''
    figure = 'images/tutorial/drone_exportDJI_KML.jpg'

    def shortHelpString(self):
        social_BW = Imgs().social_BW
        footer = '''<div align="center">
                      <img src="'''+ os.path.join(os.path.dirname(os.path.dirname(__file__)), self.figure) +'''">
                      </div>
                      <div align="left">
                      <p>
                      <b><a href="'''+ self.tr('https://portal.geoone.com.br/m/lessons/drone-webodm?classId=2300') + '''" target="_blank">'''+ self.tr('Click here to watch a full class on this tool',
                                    'Clique aqui para assistir uma aula completa sobre esta ferramenta') +'''</a></b>
                      </p>
                      <p>
                      <b><a href="'''+ self.tr('https://geoone.com.br/pvdrone/') + '''" target="_blank">'''+ self.tr('Sign up for the WebODM and QGIS course',
                                    'Inscreva-se no curso de WebODM e QGIS') +'</a><br><br>'+ self.tr('Author: Leandro Franca', 'Autor: Leandro França')+'''</b>
                      </p>'''+ social_BW + '''
                    </div>'''
        return self.tr(self.txt_en, self.txt_pt) + footer

    def initAlgorithm(self, config=None):
        self.addParameter(
            QgsProcessingParameterVectorLayer(
                self.POLYGON,
                self.tr('Polygon Layer', 'Camada de Polígono'),
                [QgsProcessing.TypeVectorPolygon]
            )
        )

        self.addParameter(
            QgsProcessingParameterFileDestination(
                self.FILE,
                self.tr('DJI-Compatible KML', 'KML compatível com a DJI'),
                fileFilter='KML (*.kml)'
            )
        )

    def processAlgorithm(self, parameters, context, feedback):

        layer = self.parameterAsVectorLayer(
            parameters,
            self.POLYGON,
            context
        )
        if layer is None:
            raise QgsProcessingException(
                self.invalidSourceError(parameters, self.POLYGON)
            )

        filepath = self.parameterAsFile(
            parameters,
            self.FILE,
            context
        )
        if not filepath:
            raise QgsProcessingException(
                self.invalidSourceError(parameters, self.FILE)
            )

        TESSSELLATE = True
        CASAS_DECIMAIS = 15

        def fmt(v, ndigits=15):
            txt = f'{float(v):.{ndigits}f}'
            return txt.rstrip('0').rstrip('.')

        def ring_to_kml_coords(ring):
            if not ring:
                return ''

            coords = [
                f"{fmt(p.x(), CASAS_DECIMAIS)},{fmt(p.y(), CASAS_DECIMAIS)},0"
                for p in ring
            ]

            p0 = ring[0]
            pN = ring[-1]
            if p0.x() != pN.x() or p0.y() != pN.y():
                coords.append(
                    f"{fmt(p0.x(), CASAS_DECIMAIS)},{fmt(p0.y(), CASAS_DECIMAIS)},0"
                )

            return ' '.join(coords)

        def geometry_to_outer_ring(geom):
            if geom is None or geom.isEmpty():
                return None

            if geom.isMultipart():
                multi = geom.asMultiPolygon()
                if not multi or not multi[0] or not multi[0][0]:
                    return None
                return multi[0][0]

            poly = geom.asPolygon()
            if not poly or not poly[0]:
                return None
            return poly[0]

        def outer_ring_to_polygon_kml(outer_ring):
            if not outer_ring:
                return ''

            coords = ring_to_kml_coords(outer_ring)
            if not coords:
                return ''

            lines = []
            lines.append('    <Polygon>')
            if TESSSELLATE:
                lines.append('      <tessellate>1</tessellate>')
            lines.append('      <outerBoundaryIs>')
            lines.append('        <LinearRing>')
            lines.append(f'          <coordinates>{coords}</coordinates>')
            lines.append('        </LinearRing>')
            lines.append('      </outerBoundaryIs>')
            lines.append('    </Polygon>')
            return '\n'.join(lines)

        crs_dest = QgsCoordinateReferenceSystem('EPSG:4326')
        transform = None

        if layer.crs() != crs_dest:
            transform = QgsCoordinateTransform(
                layer.crs(),
                crs_dest,
                QgsProject.instance()
            )
            feedback.pushInfo(
                self.tr(
                    'Reprojecting geometries to EPSG:4326...',
                    'Reprojetando geometrias para EPSG:4326...'
                )
            )

        kml = []
        kml.append('<?xml version="1.0" encoding="UTF-8"?>')
        kml.append('<kml xmlns="http://www.opengis.net/kml/2.2">')
        kml.append('<Document>')
        kml.append(f'  <name>{escape(layer.name())}</name>')

        total = layer.featureCount()
        exported = 0
        skipped_empty = 0
        skipped_transform = 0

        for i, feat in enumerate(layer.getFeatures(), start=1):

            if feedback.isCanceled():
                break

            if total:
                feedback.setProgress(int(i * 100 / total))

            geom = feat.geometry()
            if geom is None or geom.isEmpty():
                skipped_empty += 1
                continue

            if transform is not None:
                ok = geom.transform(transform)
                if ok != 0:
                    skipped_transform += 1
                    continue

            outer_ring = geometry_to_outer_ring(geom)
            if not outer_ring:
                continue

            polygon_xml = outer_ring_to_polygon_kml(outer_ring)
            if not polygon_xml:
                continue

            name_value = f'Polygon_{i}'

            kml.append('  <Placemark>')
            kml.append(f'    <name>{escape(name_value)}</name>')
            kml.append(polygon_xml)
            kml.append('  </Placemark>')

            exported += 1

        kml.append('</Document>')
        kml.append('</kml>')

        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write('\n'.join(kml))
        except Exception as e:
            raise QgsProcessingException(
                self.tr(
                    f'Could not write output file: {str(e)}',
                    f'Não foi possível gravar o arquivo de saída: {str(e)}'
                )
            )

        feedback.pushInfo(
            self.tr(
                'Operation completed successfully!',
                'Operação finalizada com sucesso!'
            )
        )
        
        feedback.pushInfo(
            self.tr(
                'Leandro Franca - Cartographic Engineer',
                'Leandro França - Eng. Cartógrafo'
            )
        )

        return {self.FILE: filepath}