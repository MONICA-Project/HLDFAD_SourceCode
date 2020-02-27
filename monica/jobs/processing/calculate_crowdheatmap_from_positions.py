from utility.utility_geographic_conversion import *
from utility.geodesy import GeoTranslations, GeoPosition, TypePosition, SurfaceVector
from django.contrib.gis.geos import Point
import math
import numpy as np
import logging
from typing import List
import random

logger = logging.getLogger('textlogger')


class PositionIndexes:
    def __init__(self):
        self.index_matrix_x = 0
        self.index_matrix_y = 0
        self.max_x = 0
        self.max_y = 0
        self.cell_size = 0
        self.enu_x = 0
        self.enu_y = 0

    def __init__(self, enu_position: SurfaceVector,
                 geographic_area: GeographicRectangleArea):
        self.index_matrix_x = 0
        self.index_matrix_y = 0
        self.max_x = 0
        self.max_y = 0
        self.cell_size = 0

        if not enu_position:
            return

        if not geographic_area:
            return

        self.max_x      = math.floor(geographic_area.size_x_m / geographic_area.cell_size_m)
        self.max_y      = math.floor(geographic_area.size_y_m / geographic_area.cell_size_m)
        self.cell_size  = geographic_area.cell_size_m
        self.enu_x      = enu_position.y
        self.enu_y      = enu_position.y

        if self.max_x == 0 or self.max_y == 0 or self.cell_size == 0:
            return

        self.index_matrix_x = int(math.floor(enu_position.x/self.cell_size))
        self.index_matrix_y = int(math.floor(enu_position.y/self.cell_size))

    def reset(self):
        self.index_matrix_x = 0
        self.index_matrix_y = 0
        self.max_x          = 0
        self.max_y          = 0
        self.cell_size      = 0

    def to_string(self):
        return 'index_x: {0}, index_y: {1}, max_x: {2}, max_y: {3}'.format(str(self.index_matrix_x),
                                                                           str(self.index_matrix_y),
                                                                           str(self.max_x),
                                                                           str(self.max_y))

    def check_inside_limit(self) -> bool:
        if self.max_x <= 0 or self.max_y <= 0:
            return False
        if self.index_matrix_x < 0 or self.index_matrix_y < 0:
            return False
        if self.index_matrix_x >= self.max_x or self.index_matrix_y >= self.max_y:
            return False

        return True


class CrowdHeatmapCalculation:
    @staticmethod
    def create_startup_densitymatrix(geographic_area: GeographicRectangleArea, enable_fake_generation: bool = False) \
            -> np.matrix:
        try:
            if not geographic_area:
                logger.warning('CrowdHeatmapCalculation create_startup_densitymatrix NO Geographic Area')
                return np.array([])

            if geographic_area.cell_size_m == 0:
                logger.warning('CrowdHeatmapCalculation create_startup_densitymatrix Geographic Area cell_size_m = 0')
                return np.array([])

            if geographic_area.size_x_m == 0:
                logger.warning('CrowdHeatmapCalculation create_startup_densitymatrix Geographic Area size_x_m = 0')
                return np.array([])

            if geographic_area.size_y_m == 0:
                logger.warning('CrowdHeatmapCalculation create_startup_densitymatrix Geographic Area size_y_m = 0')
                return np.array([])

            size_x = math.floor(geographic_area.size_x_m/geographic_area.cell_size_m)
            size_y = math.floor(geographic_area.size_y_m/geographic_area.cell_size_m)

            density_matrix = np.zeros(shape=(size_y, size_x), dtype=int)

            if not enable_fake_generation:
                return density_matrix

            for counter_fake_cells in range(1, random.randint(1, 5)):
                index_change_x = random.randint(0, size_x-1)
                index_change_y = random.randint(0, size_y-1)
                density_matrix[index_change_y, index_change_x] = random.randint(10, 50)

            return density_matrix
        except Exception as ex:
            logger.error('CrowdHeatmapCalculation create_startup_densitymatrix Exception: {}'.format(ex))
            return np.array([])

    @staticmethod
    def debug_create_string_listpos(list_position: List[Point]) -> str:
        try:
            if not list_position:
                return ""

            list_string_pos = list()

            for single_position_out in list_position:
                single_string_pos = "{0}, {1}".format(str(single_position_out.y), str(single_position_out.x))
                list_string_pos.append(single_string_pos)

            return ",".join(list_string_pos)
        except Exception as ex:
            logger.error(ex)
            return ""

    @staticmethod
    def calculate_densitymatrix_from_positions(list_position: List[GeoPosition],
                                               geographic_area: GeographicRectangleArea) -> (np.matrix, list, list):
        try:
            if not list_position or not geographic_area:
                return np.array([]), None, None

            logger.info('calculate_densitymatrix_from_positions Start Allocate Density Matrix')
            density_matrix = CrowdHeatmapCalculation.create_startup_densitymatrix(geographic_area=geographic_area)

            if density_matrix.size == 0:
                return np.array([]), None, None

            logger.info('calculate_densitymatrix_from_positions End Allocate Density Matrix')

            list_enu_distance = list()
            list_position_outside_area = list()

            for single_position in list_position:

                if not single_position:
                    logger.warning('calculate_densitymatrix_from_positions null position in list!')
                    continue

                # position_indexes = PositionIndexes(enu_position=Point(x=2, y=4, srid=4326),
                #                                    geographic_area=geographic_area)
                # FIXME: ENABLE IT
                position_indexes = CrowdHeatmapCalculation.calculate_matrixindex_position(postoidentify=single_position,
                                                                                           geographic_area=geographic_area)
                if not position_indexes:
                    list_position_outside_area.append(single_position)
                    continue

                if not position_indexes.check_inside_limit():
                    list_position_outside_area.append(single_position)
                    continue

                density_matrix[position_indexes.index_matrix_y, position_indexes.index_matrix_x] = \
                    density_matrix[position_indexes.index_matrix_y, position_indexes.index_matrix_x]+1

                list_enu_distance.append([position_indexes.enu_x, position_indexes.enu_y])

            counter_position_outside = 0

            if list_position_outside_area:
                counter_position_outside = len(list_position_outside_area)

            counter_position_inside = len(list_position) - counter_position_outside

            logger.info('calculate_densitymatrix_from_positions found {0} positions outside area and {1} inside'
                        .format(str(counter_position_outside),
                                str(counter_position_inside)))

            return density_matrix, list_enu_distance, list_position_outside_area
        except Exception as ex:
            logger.error('calculate_densitymatrix_from_positions Exception: {}'.format(ex))
            return np.array([]), None, None

    @staticmethod
    def calculate_matrixindex_position(postoidentify: GeoPosition,
                                       geographic_area: GeographicRectangleArea) -> PositionIndexes:  # NOTE: set Point
        try:
            postoidentify.consolidate_calculation()
            geographic_area.get_groundplaneposition().consolidate_calculation()

            enu_position = postoidentify.calculate_vector_distance(ref_pos=geographic_area.get_groundplaneposition())

            if not enu_position:
                return None
            
            enu_position.x = math.floor(enu_position.x)
            enu_position.y = math.floor(enu_position.y)

            return PositionIndexes(enu_position=enu_position,
                                   geographic_area=geographic_area)
        except Exception as ex:
            logger.error('calculate_matrixindex_position Exception: {}'.format(ex))
            return None

