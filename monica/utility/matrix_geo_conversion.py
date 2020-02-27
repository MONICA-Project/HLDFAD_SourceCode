from entities.densitymap_types import MatrixCell
from utility.geodesy import GeoPosition, SurfaceVector
from numpy import nan

from math import (radians, sqrt, atan2, cos, sin)


class MatrixGeoConversion:
    @staticmethod
    def get_polar_coordinates_surface(surface_x: float, surface_y: float) -> PolarCoordinates:
        return PolarCoordinates().set_surface_coordinates(surface_x=surface_x,
                                                          surface_y=surface_y)

    @staticmethod
    def convert_matrixcell_to_enudistance_from_origin(cell: MatrixCell,
                                                      bearing_matrix: float,
                                                      row_number: int,
                                                      col_number: int,
                                                      cell_size_row: int = 1,
                                                      cell_size_col: int = 1) -> (float, float, float):
        if not cell:
            return nan

        distance_east_m_0 = cell.index_col * cell_size_col
        distance_north_m_0 = -1*cell.brow_idx * cell_size_row
        up_m = 0

        polar_coordinates = PolarCoordinates()
        polar_coordinates.set_surface_coordinates(surface_vector=SurfaceVector(x=distance_east_m_0,
                                                                               y=distance_north_m_0))

        polar_coordinates.add_rotation_angle(rotation=bearing_matrix)
        surface_vector = polar_coordinates.convert_surface_coordinate()

        return surface_vector.x, \
               surface_vector.y, \
               up_m

    @staticmethod
    def convert_matrixcell_to_position(ground_plane_position: GeoPosition,
                                       cell: MatrixCell,
                                       bearing_matrix: float,
                                       row_number: int,
                                       col_number: int,
                                       cell_size_row: int = 1,
                                       cell_size_col: int = 1) -> GeoPosition:
        try:
            distance_east_m, distance_north_m, up_m = MatrixGeoConversion.\
                convert_matrixcell_to_enudistance_from_origin(cell=cell,
                                                              bearing_matrix=bearing_matrix,
                                                              row_number=row_number,
                                                              col_number=col_number,
                                                              cell_size_row=cell_size_row,
                                                              cell_size_col=cell_size_col)

            point = ground_plane_position.add_enu_distance(enu_distance=[distance_east_m, distance_north_m, up_m])
            return point
        except Exception as ex:
            return None
