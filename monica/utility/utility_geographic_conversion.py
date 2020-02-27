from django.contrib.gis.gdal import SpatialReference, CoordTransform
# from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.geos import Point
from utility.geodesy import GeoPosition, SurfaceVector
# from django.contrib.gis.geos import LineString
# from geopy.distance import distance
# from shapely.geometry import Polygon
import math
import logging

logger = logging.getLogger('textlogger')


class ECEFPosition:
    def __init__(self, x=0, y=0, z=0):
        self.x = x
        self.y = y
        self.z = z

    def set_pos_diff(self, pos_a, pos_b):
        self.x = pos_a.x-pos_b.x
        self.y = pos_a.y-pos_b.y
        self.z = pos_a.z-pos_b.z

    def get_point_ecef_conversion(self):
        return Point(x=self.x,y=self.y,z=self.z,srid=4978)


class GeographicRectangleArea:
    def __init__(self, ground_plane_position: GeoPosition, size_x_m, size_y_m, cell_size_m=1):
        self.ground_plane_position = None
        self.size_x_m = 0
        self.size_y_m = 0
        self.cell_size_m = 1
        self.set_properties(ground_plane_position, size_x_m, size_y_m, cell_size_m)

    def set_properties(self, ground_plane_position: GeoPosition, size_x_m, size_y_m, cell_size_m):
        self.ground_plane_position = ground_plane_position
        self.size_x_m = size_x_m
        self.size_y_m = size_y_m
        self.cell_size_m = cell_size_m

    def get_groundplaneposition(self) -> GeoPosition:
        if not self.ground_plane_position:
            raise Exception("GeographicRectangleArea ground_plane_position not set")

        return self.ground_plane_position

    def check_surfacevector_inside_area(self, surface_vector: SurfaceVector) -> bool:
        if not surface_vector:
            return False

        if surface_vector.x < 0 or surface_vector.x >= self.size_x_m:
            return False

        if surface_vector.y < 0 or surface_vector.y >= self.size_y_m:
            return False

        return True

    def check_position_inside_area(self, position):
        return True

    def get_vector_distance(self, position) -> SurfaceVector:
        try:
            referencepos_ecef = GeopgraphicConversion.convert_llhtoecef(self.ground_plane_position)
            position_ecef = GeopgraphicConversion.convert_llhtoecef(position)

            return GeopgraphicConversion.convert_eceftoenu(pos1=position_ecef,
                                                           ref_position_ecef=referencepos_ecef,
                                                           ref_position_llh=self.ground_plane_position)
        except Exception as ex:
            return None
        # gcoord = SpatialReference(4326)
        # mycoord = SpatialReference(4978)
        # trans = CoordTransform(gcoord, mycoord)
        #
        # pos1 = self.ground_plane_position
        # pos2 = position
        #
        # pos1.transform(trans)
        # pos2.transform(trans)
        #
        # delta_x = pos1.x-pos2.x
        # delta_y = pos1.y-pos2.y
        #
        # return SurfaceVector(delta_y,delta_y)


class GeopgraphicConversion:

    @staticmethod
    def create_copy_point(start_point):
        try:
            if not start_point.z:
                return Point(x=start_point.x,y=start_point.y,z=0,srid=start_point.srid)

            return Point(x=start_point.x,y=start_point.y,z=start_point.z,srid=start_point.srid)
        except Exception as ex:
            return None

    @staticmethod
    def test_method():
        posA = Point(x=45.062222, y=7.654426, z=0, srid=4326)
        posB = Point(x=45.062432, y=7.654415, z=0, srid=4326)

        posA_ecef = GeopgraphicConversion.convert_llhtoecef(posA)
        posB_ecef = GeopgraphicConversion.convert_llhtoecef(posB)

        enu_result =GeopgraphicConversion.convert_eceftoenu(posA_ecef, posB_ecef)

        distance_m = posA.distance(posB)

        print('ENU Conversion: East={0}, North={1}, Distance_m: {2}'.format(str(enu_result.x), str(enu_result.y), str(distance_m)))

    @staticmethod
    def check_point_inside_geographic_area(point,geographic_area):
        return True

    @staticmethod
    def convert_eceftollh(position):
        try:
            gcoord = SpatialReference(4978)
            mycoord = SpatialReference(4326)
            trans = CoordTransform(gcoord, mycoord)

            postoconv=GeopgraphicConversion.create_copy_point(position)
            postoconv.transform(trans)

            return postoconv
        except Exception as ex:
            return None

    @staticmethod
    def calculate_enu_distance(position: Point, ref_position: Point) -> SurfaceVector:
        try:
            position_ecef = GeopgraphicConversion.convert_llhtoecef(position)
            ref_position_ecef = GeopgraphicConversion.convert_llhtoecef(ref_position)

            enu_result = GeopgraphicConversion.convert_eceftoenu(position_ecef, ref_position_ecef, ref_position)

            return enu_result
            
        except Exception as ex:
            return None

    @staticmethod
    def convert_eceftoenu(pos1: Point, ref_position_ecef: Point, ref_position_llh: Point) -> SurfaceVector:
        try:
            diff_pos = ECEFPosition()
            diff_pos.set_pos_diff(pos1, ref_position_ecef)
            # ref_position_llh = GeopgraphicConversion.convert_eceftollh(ref_position)

            latitude_rads = math.radians(ref_position_llh.y)
            longitude_rads = math.radians(ref_position_llh.x)

            sin_phi = math.sin(latitude_rads)
            cos_phi = math.cos(latitude_rads)
            sin_lam = math.sin(longitude_rads)
            cos_lam = math.cos(longitude_rads)

            x = ((-1*sin_lam)*diff_pos.x)+(cos_lam*diff_pos.y)
            y = ((-1*sin_phi*cos_lam)*diff_pos.x) - (sin_phi*sin_lam*diff_pos.y)+(cos_phi*diff_pos.z)

            return SurfaceVector(x=x,
                                 y=y)

        except Exception as ex:
            logger.error('convert_eceftoenu Exception: {}'.format(ex))
            return None


    @staticmethod
    def convert_llhtoecef(position:Point):
        try:
            gcoord = SpatialReference(4326)
            mycoord = SpatialReference(4978)
            trans = CoordTransform(gcoord, mycoord)

            postoconv=GeopgraphicConversion.create_copy_point(position)
            postoconv.transform(trans)

            return postoconv
        except Exception as ex:
            logger.error('convert_llhtoecef exception: {}'.format(ex))
            return None
