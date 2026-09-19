# -*- coding: utf-8 -*-

"""Shared hydrological routines used by the LFTools Hydrology algorithms."""

from collections import deque
from math import ceil

import numpy as np
from osgeo import gdal, osr

from qgis.PyQt.QtCore import QMetaType, QTimer
from qgis.PyQt.QtGui import QColor
from qgis.core import (
    Qgis,
    QgsApplication,
    QgsCategorizedSymbolRenderer,
    QgsDistanceArea,
    QgsFeature,
    QgsFeatureSink,
    QgsField,
    QgsFields,
    QgsFillSymbol,
    QgsGeometry,
    QgsLineSymbol,
    QgsMarkerSymbol,
    QgsPointXY,
    QgsProcessing,
    QgsProcessingException,
    QgsProcessingLayerPostProcessorInterface,
    QgsProject,
    QgsRendererCategory,
    QgsSingleSymbolRenderer,
    QgsUnitTypes,
)

import processing

from lftools.translations.translate import translate


# QGIS requires post-processors to remain alive until output layers are loaded.
_POST_PROCESSORS = []


def locale_translate(*strings):
    return translate(strings, QgsApplication.locale()[:2])


def grass_algorithm(module_name, tr):
    registry = QgsApplication.processingRegistry()
    for provider_id in ('grass', 'grass7'):
        algorithm_id = '{}:{}'.format(provider_id, module_name)
        if registry.algorithmById(algorithm_id) is not None:
            return algorithm_id
    raise QgsProcessingException(
        tr(
            'The GRASS Processing provider or the {} module is not available. Install/enable GRASS in QGIS and try again.',
            'O provedor GRASS do Processamento ou o módulo {} não está disponível. Instale/ative o GRASS no QGIS e tente novamente.',
        ).format(module_name)
    )


def supported_parameters(algorithm_id, parameters):
    algorithm = QgsApplication.processingRegistry().algorithmById(algorithm_id)
    if algorithm is None:
        return parameters
    supported = {
        definition.name() for definition in algorithm.parameterDefinitions()
    }
    return {
        name: value
        for name, value in parameters.items()
        if name in supported
    }


def validate_input_raster(path, tr):
    dataset = gdal.Open(path, gdal.GA_ReadOnly)
    if dataset is None:
        raise QgsProcessingException(
            tr(
                'The input DEM could not be opened.',
                'Não foi possível abrir o MDE de entrada.',
            )
        )
    if dataset.RasterCount != 1:
        dataset = None
        raise QgsProcessingException(
            tr(
                'The input DEM must have exactly one band.',
                'O MDE de entrada deve possuir exatamente uma banda.',
            )
        )
    geotransform = dataset.GetGeoTransform()
    if not geotransform or geotransform[1] == 0 or geotransform[5] == 0:
        dataset = None
        raise QgsProcessingException(
            tr(
                'The input DEM has an invalid geotransform.',
                'O MDE de entrada possui geotransformação inválida.',
            )
        )
    dataset = None


def linear_unit_to_metre(crs):
    try:
        factor = QgsUnitTypes.fromUnitToUnitFactor(
            crs.mapUnits(), Qgis.DistanceUnit.Meters
        )
        if not np.isfinite(factor) or factor <= 0:
            return None
        return factor
    except Exception:
        return None


def distance_area(crs, context):
    calculator = QgsDistanceArea()
    calculator.setSourceCrs(crs, context.transformContext())
    ellipsoid = QgsProject.instance().ellipsoid()
    if not ellipsoid or str(ellipsoid).upper() in ('NONE', 'NOT_SET'):
        ellipsoid = crs.ellipsoidAcronym()
    if not ellipsoid and crs.isGeographic():
        ellipsoid = 'WGS84'
    if ellipsoid:
        calculator.setEllipsoid(ellipsoid)
    return calculator


def representative_pixel_area_m2(
    geotransform,
    rows,
    cols,
    is_geographic,
    metre_factor,
    distance_calculator,
):
    pixel_area_map_units = abs(
        geotransform[1] * geotransform[5]
        - geotransform[2] * geotransform[4]
    )
    if not is_geographic:
        return pixel_area_map_units * metre_factor * metre_factor

    row = rows // 2
    col = cols // 2

    def corner(column, line):
        return QgsPointXY(
            geotransform[0]
            + column * geotransform[1]
            + line * geotransform[2],
            geotransform[3]
            + column * geotransform[4]
            + line * geotransform[5],
        )

    ring = [
        corner(col, row),
        corner(col + 1, row),
        corner(col + 1, row + 1),
        corner(col, row + 1),
        corner(col, row),
    ]
    geometry = QgsGeometry.fromPolygonXY([ring])
    return abs(float(distance_calculator.measureArea(geometry)))


def threshold_in_cells(value, unit, pixel_area_m2):
    if unit == 0:
        return float(max(1, ceil(value)))
    if unit == 1:
        return value * 1_000_000.0 / pixel_area_m2
    return value * 10_000.0 / pixel_area_m2


def valid_mask(array, nodata):
    valid = np.isfinite(array)
    if nodata is not None:
        if np.isnan(nodata):
            valid &= ~np.isnan(array)
        else:
            valid &= array != nodata
    return valid


def validate_matching_grids(datasets, tr):
    reference = datasets[0]
    reference_size = (reference.RasterXSize, reference.RasterYSize)
    reference_transform = reference.GetGeoTransform()
    reference_projection = reference.GetProjection()
    for dataset in datasets[1:]:
        if (dataset.RasterXSize, dataset.RasterYSize) != reference_size:
            raise QgsProcessingException(
                tr(
                    'The hydrological rasters have different dimensions.',
                    'Os rasters hidrológicos possuem dimensões diferentes.',
                )
            )
        if not np.allclose(
            dataset.GetGeoTransform(), reference_transform, rtol=0, atol=1e-9
        ):
            raise QgsProcessingException(
                tr(
                    'The hydrological rasters are not aligned.',
                    'Os rasters hidrológicos não estão alinhados.',
                )
            )
        reference_srs = osr.SpatialReference()
        dataset_srs = osr.SpatialReference()
        reference_srs.ImportFromWkt(reference_projection)
        dataset_srs.ImportFromWkt(dataset.GetProjection())
        if not bool(reference_srs.IsSame(dataset_srs)):
            raise QgsProcessingException(
                tr(
                    'The hydrological rasters have different coordinate reference systems.',
                    'Os rasters hidrológicos possuem sistemas de referência diferentes.',
                )
            )


def write_raster(path, array, reference, data_type, nodata):
    driver = gdal.GetDriverByName('GTiff')
    dataset = driver.Create(
        path,
        reference.RasterXSize,
        reference.RasterYSize,
        1,
        data_type,
        options=['COMPRESS=LZW', 'TILED=YES', 'BIGTIFF=IF_SAFER'],
    )
    if dataset is None:
        raise QgsProcessingException(
            'Could not create output raster: {}'.format(path)
        )
    dataset.SetGeoTransform(reference.GetGeoTransform())
    dataset.SetProjection(reference.GetProjection())
    band = dataset.GetRasterBand(1)
    band.SetNoDataValue(nodata)
    band.WriteArray(array)
    band.FlushCache()
    dataset.FlushCache()
    dataset = None


def condition_dem(
    source_path,
    conditioned_path,
    condition,
    context,
    feedback,
    tr,
):
    if condition:
        algorithm = grass_algorithm('r.fill.dir', tr)
        parameters = supported_parameters(
            algorithm,
            {
                'input': source_path,
                'format': 0,
                '-f': False,
                'output': conditioned_path,
                'direction': QgsProcessing.TEMPORARY_OUTPUT,
                'areas': QgsProcessing.TEMPORARY_OUTPUT,
            },
        )
        processing.run(
            algorithm,
            parameters,
            context=context,
            feedback=feedback,
            is_child_algorithm=True,
        )
    else:
        processing.run(
            'gdal:translate',
            {
                'INPUT': source_path,
                'TARGET_CRS': None,
                'NODATA': None,
                'COPY_SUBDATASETS': False,
                'OPTIONS': 'COMPRESS=LZW|TILED=YES|BIGTIFF=IF_SAFER',
                'EXTRA': '',
                'DATA_TYPE': 0,
                'OUTPUT': conditioned_path,
            },
            context=context,
            feedback=feedback,
            is_child_algorithm=True,
        )


def calculate_d8(
    conditioned_path,
    direction_path,
    accumulation_path,
    memory,
    context,
    feedback,
    tr,
):
    algorithm = grass_algorithm('r.watershed', tr)
    parameters = supported_parameters(
        algorithm,
        {
            'elevation': conditioned_path,
            'convergence': 5,
            'memory': memory,
            '-s': True,
            '-m': False,
            '-4': False,
            '-a': False,
            '-b': False,
            'accumulation': accumulation_path,
            'drainage': direction_path,
        },
    )
    processing.run(
        algorithm,
        parameters,
        context=context,
        feedback=feedback,
        is_child_algorithm=True,
    )


def open_hydrology_rasters(
    conditioned_path, direction_path, accumulation_path, tr
):
    dem_dataset = gdal.Open(conditioned_path, gdal.GA_ReadOnly)
    direction_dataset = gdal.Open(direction_path, gdal.GA_ReadOnly)
    accumulation_dataset = gdal.Open(accumulation_path, gdal.GA_ReadOnly)
    if not dem_dataset or not direction_dataset or not accumulation_dataset:
        raise QgsProcessingException(
            tr(
                'One or more hydrological rasters could not be opened.',
                'Não foi possível abrir um ou mais rasters hidrológicos.',
            )
        )
    validate_matching_grids(
        (dem_dataset, direction_dataset, accumulation_dataset), tr
    )
    return dem_dataset, direction_dataset, accumulation_dataset


def read_hydrology_arrays(
    dem_dataset, direction_dataset, accumulation_dataset
):
    dem_band = dem_dataset.GetRasterBand(1)
    direction_band = direction_dataset.GetRasterBand(1)
    accumulation_band = accumulation_dataset.GetRasterBand(1)
    dem = dem_band.ReadAsArray().astype(np.float32, copy=False)
    direction = direction_band.ReadAsArray().astype(np.int16, copy=False)
    accumulation = accumulation_band.ReadAsArray().astype(np.float64, copy=False)
    valid = valid_mask(dem, dem_band.GetNoDataValue())
    valid &= valid_mask(direction, direction_band.GetNoDataValue())
    accumulation_valid = valid_mask(
        accumulation, accumulation_band.GetNoDataValue()
    )
    return dem, direction, accumulation, valid, accumulation_valid


def guard_raster_size(cell_count, feedback, tr, hand=False):
    if cell_count > 100_000_000:
        raise QgsProcessingException(
            tr(
                'The raster has more than 100 million cells. Clip the DEM to the study area or use a coarser resolution.',
                'O raster possui mais de 100 milhões de células. Recorte o MDE para a área de estudo ou utilize uma resolução mais grosseira.',
            )
        )
    if hand and cell_count > 25_000_000:
        feedback.pushWarning(
            tr(
                'This raster has more than 25 million cells. The HAND calculation may require substantial RAM.',
                'Este raster possui mais de 25 milhões de células. O cálculo do HAND pode exigir muita memória RAM.',
            )
        )


def build_downstream(direction, valid):
    rows, cols = direction.shape
    size = rows * cols
    direction_flat = np.abs(direction).ravel()
    valid_flat = valid.ravel()
    downstream = np.full(size, -1, dtype=np.int64)
    offsets = {
        1: (-1, 1),
        2: (-1, 0),
        3: (-1, -1),
        4: (0, -1),
        5: (1, -1),
        6: (1, 0),
        7: (1, 1),
        8: (0, 1),
    }
    for code, (delta_row, delta_col) in offsets.items():
        source = np.flatnonzero(valid_flat & (direction_flat == code))
        if source.size == 0:
            continue
        source_row = source // cols
        source_col = source - source_row * cols
        target_row = source_row + delta_row
        target_col = source_col + delta_col
        inside = (
            (target_row >= 0)
            & (target_row < rows)
            & (target_col >= 0)
            & (target_col < cols)
        )
        if not np.any(inside):
            continue
        source = source[inside]
        target = target_row[inside] * cols + target_col[inside]
        target_valid = valid_flat[target]
        downstream[source[target_valid]] = target[target_valid]
    downstream[valid_flat & (direction.ravel() < 0)] = -1
    return downstream


def build_external_outlets(direction, valid, downstream):
    direction_flat = np.asarray(direction).ravel()
    valid_flat = np.asarray(valid).ravel()
    has_direction = (np.abs(direction_flat) >= 1) & (
        np.abs(direction_flat) <= 8
    )
    return valid_flat & has_direction & (
        (downstream < 0) | (direction_flat < 0)
    )


def calculate_hand_targets(downstream, stream_flat, outlet_flat=None):
    size = downstream.size
    target = downstream.copy()
    stream_index = np.flatnonzero(stream_flat)
    target[stream_index] = stream_index
    if outlet_flat is not None:
        outlet_index = np.flatnonzero(outlet_flat)
        target[outlet_index] = outlet_index
    max_iterations = max(2, int(ceil(np.log2(max(size, 2)))) + 2)
    for _ in range(max_iterations):
        active = target >= 0
        if not np.any(active):
            break
        current = target[active]
        jumped = target[current]
        changed = np.any(jumped != current)
        target[active] = jumped
        if not changed:
            break
    resolved_index = np.flatnonzero(target >= 0)
    if resolved_index.size:
        reaches_reference = stream_flat[target[resolved_index]]
        if outlet_flat is not None:
            reaches_reference |= outlet_flat[target[resolved_index]]
        target[resolved_index[~reaches_reference]] = -1
    return target


def calculate_stream_orders(stream_flat, downstream):
    size = downstream.size
    stream_index = np.flatnonzero(stream_flat)
    indegree = np.zeros(size, dtype=np.uint16)
    target = downstream[stream_index]
    linked = target >= 0
    if np.any(linked):
        linked_position = np.flatnonzero(linked)
        linked[linked_position] = stream_flat[target[linked_position]]
        np.add.at(indegree, target[linked], 1)

    remaining = indegree.copy()
    strahler = np.zeros(size, dtype=np.uint16)
    shreve = np.zeros(size, dtype=np.uint64)
    maximum_upstream_order = np.zeros(size, dtype=np.uint16)
    maximum_order_count = np.zeros(size, dtype=np.uint16)
    shreve_sum = np.zeros(size, dtype=np.uint64)
    sources = stream_index[indegree[stream_index] == 0]
    strahler[sources] = 1
    shreve[sources] = 1
    queue = deque(int(index) for index in sources)
    processed = 0
    while queue:
        cell = queue.popleft()
        processed += 1
        next_cell = int(downstream[cell])
        if next_cell < 0 or not stream_flat[next_cell]:
            continue
        upstream_order = strahler[cell]
        if upstream_order > maximum_upstream_order[next_cell]:
            maximum_upstream_order[next_cell] = upstream_order
            maximum_order_count[next_cell] = 1
        elif upstream_order == maximum_upstream_order[next_cell]:
            maximum_order_count[next_cell] += 1
        shreve_sum[next_cell] += shreve[cell]
        remaining[next_cell] -= 1
        if remaining[next_cell] == 0:
            order = maximum_upstream_order[next_cell]
            if maximum_order_count[next_cell] >= 2:
                order += 1
            strahler[next_cell] = max(1, order)
            shreve[next_cell] = max(1, shreve_sum[next_cell])
            queue.append(next_cell)
    return indegree, strahler, shreve, processed


def drainage_fields():
    fields = QgsFields()
    fields.append(QgsField('stream_id', QMetaType.Type.Int))
    fields.append(QgsField('from_node', QMetaType.Type.Int))
    fields.append(QgsField('to_node', QMetaType.Type.Int))
    fields.append(QgsField('strahler', QMetaType.Type.Int))
    fields.append(QgsField('shreve', QMetaType.Type.LongLong))
    fields.append(QgsField('length_m', QMetaType.Type.Double, len=20, prec=3))
    fields.append(QgsField('up_area_km2', QMetaType.Type.Double, len=20, prec=6))
    fields.append(QgsField('z_start', QMetaType.Type.Double, len=20, prec=3))
    fields.append(QgsField('z_end', QMetaType.Type.Double, len=20, prec=3))
    fields.append(QgsField('slope_pct', QMetaType.Type.Double, len=20, prec=6))
    return fields


def cell_centre(cell, cols, geotransform):
    row = cell // cols
    col = cell - row * cols
    return QgsPointXY(
        geotransform[0]
        + (col + 0.5) * geotransform[1]
        + (row + 0.5) * geotransform[2],
        geotransform[3]
        + (col + 0.5) * geotransform[4]
        + (row + 0.5) * geotransform[5],
    )


def map_to_cell(point, rows, cols, geotransform):
    delta_x = point.x() - geotransform[0]
    delta_y = point.y() - geotransform[3]
    determinant = (
        geotransform[1] * geotransform[5]
        - geotransform[2] * geotransform[4]
    )
    if abs(determinant) < 1e-18:
        return None
    column = int(np.floor(
        (delta_x * geotransform[5] - delta_y * geotransform[2])
        / determinant
    ))
    row = int(np.floor(
        (delta_y * geotransform[1] - delta_x * geotransform[4])
        / determinant
    ))
    if row < 0 or row >= rows or column < 0 or column >= cols:
        return None
    return row * cols + column


def create_vector_network(
    sink,
    fields,
    stream_flat,
    downstream,
    accumulation,
    dem,
    cols,
    geotransform,
    pixel_area_m2,
    metre_factor,
    distance_calculator,
    feedback,
    tr,
    progress_start=70,
):
    indegree, strahler, shreve, processed = calculate_stream_orders(
        stream_flat, downstream
    )
    stream_index = np.flatnonzero(stream_flat)
    if processed != stream_index.size:
        feedback.pushWarning(
            tr(
                '{} drainage cells could not be topologically ordered. Check the D8 raster for cycles.',
                '{} células de drenagem não puderam ser ordenadas topologicamente. Verifique se existem ciclos no raster D8.',
            ).format(stream_index.size - processed)
        )

    downstream_is_stream = np.zeros(downstream.size, dtype=bool)
    linked_index = np.flatnonzero(downstream >= 0)
    downstream_is_stream[linked_index] = stream_flat[downstream[linked_index]]
    node_mask = stream_flat & ((indegree != 1) | ~downstream_is_stream)
    node_cells = np.flatnonzero(node_mask)
    node_ids = np.full(downstream.size, -1, dtype=np.int32)
    node_ids[node_cells] = np.arange(1, node_cells.size + 1, dtype=np.int32)
    start_cells = np.flatnonzero(
        stream_flat & (indegree != 1) & downstream_is_stream
    )

    reach_count = 0
    maximum_strahler = 0
    total_starts = max(1, start_cells.size)
    for position, start in enumerate(start_cells):
        if feedback.isCanceled():
            break
        cells = [int(start)]
        visited = {int(start)}
        current = int(start)
        while True:
            next_cell = int(downstream[current])
            if next_cell < 0 or not stream_flat[next_cell]:
                break
            if next_cell in visited:
                feedback.pushWarning(
                    tr(
                        'A cycle was found in the D8 drainage raster; the affected reach was truncated.',
                        'Foi encontrado um ciclo no raster de drenagem D8; o trecho afetado foi interrompido.',
                    )
                )
                break
            cells.append(next_cell)
            visited.add(next_cell)
            current = next_cell
            if indegree[current] != 1 or not downstream_is_stream[current]:
                break
        if len(cells) < 2:
            continue

        points = [cell_centre(cell, cols, geotransform) for cell in cells]
        geometry = QgsGeometry.fromPolylineXY(points)
        length_m = (
            float(distance_calculator.measureLength(geometry))
            if metre_factor is None
            else geometry.length() * metre_factor
        )
        z_start = float(dem[start])
        z_end = float(dem[current])
        attribute_end = (
            cells[-2] if indegree[current] > 1 and len(cells) > 1 else current
        )
        slope_pct = (
            100.0 * (z_start - z_end) / length_m if length_m > 0 else 0.0
        )
        reach_count += 1
        reach_order = int(strahler[start])
        maximum_strahler = max(maximum_strahler, reach_order)
        feature = QgsFeature(fields)
        feature.setGeometry(geometry)
        feature.setAttributes(
            [
                reach_count,
                int(node_ids[start]),
                int(node_ids[current]),
                reach_order,
                int(shreve[start]),
                float(length_m),
                float(accumulation[attribute_end] * pixel_area_m2 / 1_000_000.0),
                z_start,
                z_end,
                float(slope_pct),
            ]
        )
        sink.addFeature(feature, QgsFeatureSink.FastInsert)
        feedback.setProgress(
            progress_start
            + int((100 - progress_start) * (position + 1) / total_starts)
        )
    return {'reach_count': reach_count, 'max_strahler': maximum_strahler}


def create_drainage_raster(stream, valid):
    drainage = np.full(stream.shape, 255, dtype=np.uint8)
    drainage[valid] = 0
    drainage[stream] = 1
    return drainage


class _OutputState:

    def __init__(self, group_name, order, visible):
        self.group_name = group_name
        self.order = tuple(order)
        self.visible = set(visible)
        self.layer_ids = {}
        self.expected = set()
        self.group = None


def configure_output_postprocessors(
    context,
    results,
    names,
    order,
    visible,
    group_name,
    styles=None,
):
    state = _OutputState(group_name, order, visible)
    styles = styles or {}
    for output_name, destination in results.items():
        if not destination or not context.willLoadLayerOnCompletion(destination):
            continue
        state.expected.add(output_name)
        processor = HydroOutputPostProcessor(
            state,
            output_name,
            names.get(output_name, output_name),
            styles.get(output_name),
        )
        _POST_PROCESSORS.append(processor)
        context.layerToLoadOnCompletionDetails(destination).setPostProcessor(
            processor
        )
    # Avoid unbounded growth while keeping recent processors alive.
    if len(_POST_PROCESSORS) > 200:
        del _POST_PROCESSORS[:-100]


class HydroOutputPostProcessor(QgsProcessingLayerPostProcessorInterface):

    def __init__(self, state, output_name, layer_name, style):
        super().__init__()
        self.state = state
        self.output_name = output_name
        self.name = layer_name
        self.style = style

    def postProcessLayer(self, layer, context, feedback):
        del context
        layer.setName(self.name)
        self.state.layer_ids[self.output_name] = layer.id()
        if self.style == 'drainage':
            self._apply_drainage_style(layer, feedback)
        elif self.style == 'basin':
            self._apply_basin_style(layer)
        elif self.style == 'outlets':
            self._apply_outlet_style(layer, feedback)
        self._organize_output_layers()
        QTimer.singleShot(0, self._organize_output_layers)
        if self.state.expected.issubset(self.state.layer_ids):
            feedback.pushInfo(
                locale_translate(
                    'Post-processing completed: output group, layer order and visibility configured.',
                    'Pós-processamento concluído: grupo de saída, ordem e visibilidade das camadas configurados.',
                )
            )

    @staticmethod
    def _apply_drainage_style(layer, feedback):
        field_index = layer.fields().indexFromName('strahler')
        if field_index < 0:
            feedback.pushWarning(
                locale_translate(
                    'The strahler field was not found; the drainage style was not applied.',
                    'O campo strahler não foi encontrado; a simbologia da drenagem não foi aplicada.',
                )
            )
            return
        widths = {1: 0.25, 2: 0.40, 3: 0.60, 4: 0.85}
        values = sorted(
            int(value)
            for value in layer.uniqueValues(field_index)
            if value is not None
        )
        categories = []
        for order in values:
            symbol = QgsLineSymbol.createSimple(
                {
                    'color': QColor('#1565c0').name(),
                    'width': str(widths.get(order, 1.10)),
                    'line_style': 'solid',
                    'capstyle': 'round',
                    'joinstyle': 'round',
                }
            )
            categories.append(
                QgsRendererCategory(order, symbol, 'Strahler {}'.format(order))
            )
        if categories:
            layer.setRenderer(
                QgsCategorizedSymbolRenderer('strahler', categories)
            )
            layer.triggerRepaint()

    @staticmethod
    def _apply_basin_style(layer):
        symbol = QgsFillSymbol.createSimple(
            {
                'color': '100,181,246,75',
                'outline_color': '13,71,161,255',
                'outline_width': '0.8',
                'outline_style': 'solid',
            }
        )
        layer.setRenderer(QgsSingleSymbolRenderer(symbol))
        layer.triggerRepaint()

    @staticmethod
    def _apply_outlet_style(layer, feedback):
        field_index = layer.fields().indexFromName('point_type')
        if field_index < 0:
            feedback.pushWarning(
                locale_translate(
                    'The point_type field was not found; the outlet style was not applied.',
                    'O campo point_type não foi encontrado; a simbologia dos exutórios não foi aplicada.',
                )
            )
            return
        original = QgsMarkerSymbol.createSimple(
            {
                'name': 'circle',
                'color': '255,255,255,0',
                'outline_color': '251,140,0,255',
                'outline_width': '0.8',
                'size': '3.2',
            }
        )
        adjusted = QgsMarkerSymbol.createSimple(
            {
                'name': 'circle',
                'color': '229,57,53,255',
                'outline_color': '255,255,255,255',
                'outline_width': '0.5',
                'size': '3.2',
            }
        )
        categories = [
            QgsRendererCategory(
                'original',
                original,
                locale_translate('Original point', 'Ponto original'),
            ),
            QgsRendererCategory(
                'adjusted',
                adjusted,
                locale_translate('Adjusted outlet', 'Exutório ajustado'),
            ),
        ]
        layer.setRenderer(
            QgsCategorizedSymbolRenderer('point_type', categories)
        )
        layer.triggerRepaint()

    def _organize_output_layers(self):
        root = QgsProject.instance().layerTreeRoot()
        group = self._output_group(root)
        ordered_nodes = []
        for output_name in self.state.order:
            layer_id = self.state.layer_ids.get(output_name)
            node = root.findLayer(layer_id) if layer_id else None
            if node is not None:
                ordered_nodes.append((output_name, node))
        if not ordered_nodes:
            return
        clones = [(name, node.clone()) for name, node in ordered_nodes]
        for index, (output_name, clone) in enumerate(clones):
            group.insertChildNode(index, clone)
            clone.setItemVisibilityChecked(output_name in self.state.visible)
        for output_name, node in ordered_nodes:
            parent = node.parent()
            if parent is not None:
                parent.removeChildNode(node)

    def _output_group(self, root):
        if self.state.group is not None and self.state.group.parent() is not None:
            return self.state.group
        base_name = self.state.group_name
        group_name = base_name
        suffix = 2
        while root.findGroup(group_name) is not None:
            group_name = '{} ({})'.format(base_name, suffix)
            suffix += 1
        self.state.group = root.insertGroup(0, group_name)
        self.state.group.setExpanded(True)
        return self.state.group
