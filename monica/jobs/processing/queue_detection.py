from numpy import ndarray
from entities.densitymap_types import MatrixCell, RegionAdiacentCells, \
    SingleRowAdiacentCells, GroupRegionsAdiacentCells, GroupMatrixCoords, MatrixCoords, DensityMapConfiguration
from typing import List, Dict
from django.contrib.gis.geos import Polygon, MultiPolygon
# from shapely.ops import cascaded_union  # FIXME: Removed (check if polygon.union works at the same way)
import logging

logger = logging.getLogger('textLogger')


class QueueDetectionAlgorithm:
    @staticmethod
    def get_adiacentregion(list_regions: List[RegionAdiacentCells], matrix_cell: MatrixCell) \
            -> RegionAdiacentCells:
        try:
            if not list_regions or not matrix_cell:
                return None

            for region in list_regions:
                if not region or not region.check_matrixcell_adiacent(matrix_cell=matrix_cell):
                    continue

                return region

            return None
        except Exception as ex:
            print('Exception get_adiacentregion: {}'.format(ex))
            return None

    @staticmethod
    def consolidate_region_list(list_regions: List[RegionAdiacentCells], min_cell_count: int) \
            -> List[RegionAdiacentCells]:
        try:
            if not list_regions:
                return None

            for region in list_regions:
                if not region:
                    list_regions.remove(region)
                    continue

                if region.get_matrixcell_count() < min_cell_count:
                    list_regions.remove(region)

            return list_regions
        except Exception as ex:
            logger.error('Exception consolidate_region_list: {}'.format(ex))
            return None

    @staticmethod
    def get_list_adiacentcells_singlerow(single_row: ndarray,
                                         brow_idx: int,
                                         min_mean: float,
                                         list_region_to_exclude: GroupRegionsAdiacentCells = None) -> List[SingleRowAdiacentCells]:
        try:
            if not single_row.shape or single_row.shape[0] == 0:
                return None

            singlerow_conseq = None
            list_return = list()
            current_sum = 0
            counter_elem = 0

            if single_row.max() < min_mean:
                return None

            for index_cell in range(0, single_row.shape[0]):
                cell_value = single_row[index_cell]

                current_sum += cell_value
                counter_elem += 1

                if cell_value == 0 or (float(current_sum*1.0/counter_elem*1.0) < min_mean):
                    current_sum = 0
                    counter_elem = 0

                    if not singlerow_conseq:
                        continue

                    list_return.append(singlerow_conseq)
                    singlerow_conseq = None
                    continue

                curr_cell = MatrixCell(brow_idx=brow_idx,
                                       index_col=index_cell,
                                       count=cell_value)

                if list_region_to_exclude and list_region_to_exclude.check_cell_inside_list_region(cell=curr_cell):
                    current_sum = 0
                    counter_elem = 0

                    if not singlerow_conseq:
                        continue

                    list_return.append(singlerow_conseq)
                    singlerow_conseq = None

                    del curr_cell
                    continue

                if not singlerow_conseq:
                    singlerow_conseq = SingleRowAdiacentCells()

                if singlerow_conseq.empty() or singlerow_conseq.check_cell_adiacent(cell=curr_cell):
                    singlerow_conseq.add_cell(cell=curr_cell)

            if not singlerow_conseq:
                return list_return

            list_return.append(singlerow_conseq)

            return list_return
        except Exception as ex:
            print('get_list_adiacentcells_singlerow Exception: {}'.format(ex))
            return None

    @staticmethod
    def create_listregion_adjacents(list_singlerow_adiacent: List[SingleRowAdiacentCells]) -> GroupRegionsAdiacentCells:
        try:
            if not list_singlerow_adiacent:
                return None

            list_adjacent_regions = GroupRegionsAdiacentCells()
            list_elem_to_exclude = list()

            for index_curr_row in range(0, len(list_singlerow_adiacent)-1):

                is_row_inglobed_previous_regions = False

                if index_curr_row in list_elem_to_exclude:
                    continue

                curr_row = list_singlerow_adiacent[index_curr_row]

                if not curr_row:
                    continue

                for previous_region in list_adjacent_regions.get_listregions():
                    if not previous_region:
                        continue

                    if previous_region.check_is_rowadiacent(row_to_check=curr_row):
                        previous_region.add_singlerow_adiacent(single_row=curr_row)
                        is_row_inglobed_previous_regions = True

                if is_row_inglobed_previous_regions:
                    continue

                specific_region = RegionAdiacentCells()
                specific_region.add_singlerow_adiacent(single_row=curr_row)

                for index_next_region in range(index_curr_row+1, len(list_singlerow_adiacent)):
                    if index_next_region in list_elem_to_exclude:
                        continue

                    next_row = list_singlerow_adiacent[index_next_region]

                    if not specific_region.check_is_rowadiacent(row_to_check=next_row):
                        continue

                    specific_region.add_singlerow_adiacent(single_row=next_row)
                    list_elem_to_exclude.append(index_next_region)

                list_adjacent_regions.append(specific_region)

            return list_adjacent_regions
        except Exception as ex:
            print('create_listregion_adjacents Exception: {}'.format(ex))
            return None

    @staticmethod
    def remove_regions_toosmall(list_region_input: GroupRegionsAdiacentCells, min_cell_count: int) \
            -> GroupRegionsAdiacentCells:
        try:
            if not list_region_input:
                return None

            list_output = GroupRegionsAdiacentCells()

            for region in list_region_input.get_listregions():
                if not region:
                    continue

                if region.get_count_cells() < min_cell_count:
                    continue

                list_output.append(region)
            return list_output
        except Exception as ex:
            print('{}'.format(ex))
            return None

    @staticmethod
    def create_dictionary_from_globallistregions(global_list_regions: GroupRegionsAdiacentCells) \
            -> Dict[int, GroupRegionsAdiacentCells]:
        if not global_list_regions:
            return None

        try:
            dictionary_output = dict()

            for region in global_list_regions.get_listregions():
                if not region:
                    continue

                mean_people = region.get_mean()

                if mean_people not in dictionary_output.keys():
                    group_regions = GroupRegionsAdiacentCells()
                else:
                    group_regions = dictionary_output[mean_people]

                group_regions.append(region=region)
                dictionary_output[mean_people] = group_regions

            return dictionary_output
        except Exception as ex:
            return None

    @staticmethod
    def find_queueshape_areas(density_map: ndarray,
                              min_cell_count: int) \
            -> Dict[int, GroupRegionsAdiacentCells]:
        try:
            if density_map.shape[0] == 0:
                print('No Queue Found, Empty Density Map')
                return None

            max_people_count = int(density_map.max())
            min_people_count = int(density_map.min())

            if max_people_count == 0:
                logger.info('No Queue Found, Zeros Density Map')
                return None

            if min_people_count > 0:
                min_people_count -= 1

            global_list_regions = GroupRegionsAdiacentCells()

            for mean_people in range(max_people_count, min_people_count, -1):
                list_regions = QueueDetectionAlgorithm.find_regions_densitymap(density_map=density_map,
                                                                               min_mean=mean_people,
                                                                               min_cell_count=min_cell_count,
                                                                               list_region_to_exclude=global_list_regions)
                if not list_regions:
                    logger.debug('No Region Available, minimum mean queue people: {0}, min cells: {1}'.format(mean_people, min_cell_count))
                    continue

                logger.info('Region Counter: {0}, minimum queue people: {1}, min cells: {2}'.format(len(list_regions),
                                                                                                     mean_people,
                                                                                                     min_cell_count))

                global_list_regions.extend(list_regions.get_listregions())

            global_list_regions.consolidate_regions()

            return QueueDetectionAlgorithm.create_dictionary_from_globallistregions(global_list_regions=global_list_regions)
        except Exception as ex:
            logger.error('find_queueshape_areas Exception: {}'.format(ex))
            return None

    @staticmethod
    def convert_matrixpolygon_to_geo_area(
                            polygon_matrix_coords: GroupMatrixCoords,
                            densitymap_conf: DensityMapConfiguration
                            ) -> Polygon:
        try:
            if not polygon_matrix_coords:
                logger.info('convert_matrixpolygon_to_geo_area polygon_matrix_coords None. Exit')
                return None

            list_coordinates = list()

            logger.info('convert_matrixpolygon_to_geo_area Started Procedure')
            polygon_matrix_coords.consolidate_polygon()

            for matrix_coords in polygon_matrix_coords.get_listvertex():
                if not matrix_coords:
                    continue
                geo_point = matrix_coords.to_geoposition_coordinates(density_map_conf=densitymap_conf)

                if not geo_point:
                    continue

                logger.info('convert_matrixpolygon_to_geo_area GeoPoint: {}'.format(geo_point.to_string()))

                list_coordinates.append((geo_point.longitude, geo_point.latitude))

            logger.info('convert_matrixpolygon_to_geo_area Creating')
            polygon = Polygon(list_coordinates)
            logger.info('convert_matrixpolygon_to_geo_area Created')
            return polygon
        except Exception as ex:
            logger.error('convert_matrixpolygon_to_geo_area Exception: {}'.format(ex))
            return None

    @staticmethod
    def convert_polygon_to_matrix_coords(polygon: Polygon) -> GroupMatrixCoords:
        try:
            if not polygon:
                return None

            group_matrix_coords = GroupMatrixCoords()

            logger.debug('convert_polygon_to_matrix_coords len polygon: {}'.format(len(polygon[0])))

            for external_ring in polygon:
                if not external_ring:
                    continue

                for index_element in range(0, len(external_ring)):
                    single_tuple = [
                        external_ring[index_element][0],
                        external_ring[index_element][1],
                    ]

                    logger.debug('convert_polygon_to_matrix_coords IndexElement: {0}, '
                                 'brow_idx: {1}, index_col: {2}'.format(
                        index_element,
                        single_tuple[1],
                        single_tuple[0]
                        )
                    )

                    matrix_coords = MatrixCoords(
                        brow_idx=single_tuple[1],
                        index_col=single_tuple[0]
                    )
                    group_matrix_coords.append(matrix_coords)
            return group_matrix_coords
        except Exception as ex:
            logger.error('convert_polygon_to_matrix_coords2 Exception: {}'.format(ex))
            return None

    @staticmethod
    def convert_region_to_polygon(region_queue_shape: RegionAdiacentCells) -> Polygon:
        try:
            if not region_queue_shape:
                logger.info('convert_region_to_polygon region_queue_shape None. Exit')
                return None

            list_shapesrow_region = region_queue_shape.get_rowshapesvertex()

            if not list_shapesrow_region:
                return None

            list_rectangles = list()

            for single_shape in list_shapesrow_region.get_listgroupvertex():
                if not single_shape:
                    continue

                list_points = list()
                for vertex in single_shape.get_listvertex():
                    if not vertex:
                        continue

                    tuple_point = vertex.to_tuple()

                    if not tuple_point:
                        continue

                    list_points.append(tuple_point)
                sub_rectangle = Polygon(list_points)
                list_rectangles.append(sub_rectangle)

            multi_polygon = MultiPolygon()
            multi_polygon.extend(list_rectangles)
            merged_polygon = multi_polygon.unary_union

            del multi_polygon

            logger.debug('convert_shapes_to_list_rectangles Created, typeof: {}'.format(type(merged_polygon).__name__))

            # merged_polygon = cascaded_union(list_rectangles)
            # FIXME: Check if the operations above gives the same results

            return merged_polygon
        except Exception as ex:
            logger.error('convert_shapes_to_list_rectangles Exception {}'.format(ex))
            return None

    @staticmethod
    def find_regions_densitymap(density_map: ndarray,
                                min_cell_count: int,
                                min_mean: float,
                                list_region_to_exclude: GroupRegionsAdiacentCells = None) \
            -> GroupRegionsAdiacentCells:
        try:
            if not density_map.shape or density_map.shape[0] == 0:
                return None

            list_rowadiacent_cells = list()

            for brow_idx in range(0, density_map.shape[0]):
                current_row = density_map[brow_idx, :]

                list_cells_row = QueueDetectionAlgorithm.get_list_adiacentcells_singlerow(single_row=current_row,
                                                                                          brow_idx=brow_idx,
                                                                                          min_mean=min_mean,
                                                                                          list_region_to_exclude=list_region_to_exclude)

                if not list_cells_row:
                    continue

                list_rowadiacent_cells.extend(list_cells_row)

            list_return = QueueDetectionAlgorithm.create_listregion_adjacents(list_singlerow_adiacent=list_rowadiacent_cells)
            list_return = QueueDetectionAlgorithm.remove_regions_toosmall(list_region_input=list_return, min_cell_count=min_cell_count)
            return list_return
        except Exception as ex:
            print('Exception in find_regions_densitymap: {}'.format(ex))
            return None