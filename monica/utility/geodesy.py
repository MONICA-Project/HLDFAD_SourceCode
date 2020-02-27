#!/usr/bin/env python3

"""
Geoscience Australia - Python Geodesy Package
Geodesy Module
"""

from math import (pi, degrees, radians, sqrt, sin,
                  cos, tan, asin, acos, atan, atan2, fabs)
import numpy as np
# from geodepy.constants import grs80
from enum import Enum
from django.contrib.gis.geos import Point
from typing import List


# Ellipsoid Constants
class Ellipsoid(object):
    def __init__(self, semimaj, inversef):
        self.semimaj = semimaj
        self.inversef = inversef
        self.f = 1 / self.inversef
        self.semimin = float(self.semimaj * (1 - self.f))
        self.ecc1sq = float(self.f * (2 - self.f))
        self.ecc2sq = float(self.ecc1sq / (1 - self.ecc1sq))
        self.ecc1 = sqrt(self.ecc1sq)
        self.n = float(self.f / (2 - self.f))
        self.n2 = self.n ** 2


# Geodetic Reference System 1980 (http://www.epsg-registry.org/export.htm?gml=urn:ogc:def:ellipsoid:EPSG::7019)
grs80 = Ellipsoid(6378137, 298.257222101)


class SurfaceVector:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def set_properties(self, x, y):
        self.x = x
        self.y = y


class PolarCoordinates(object):
    def __init__(self, magnitude: float=0, angle: float=0):
        self.magnitude = magnitude
        self.angle = angle

    def set_surface_coordinates(self, surface_vector: SurfaceVector) -> "PolarCoordinates":
        self.magnitude = sqrt((surface_vector.x**2)+(surface_vector.y**2))
        self.angle = atan2(surface_vector.y, surface_vector.x)
        return self

    def add_rotation_angle(self, rotation: float):
        self.angle += radians(rotation)

    def convert_surface_coordinate(self) -> SurfaceVector:
        surface_x = self.magnitude * cos(self.angle)
        surface_y = self.magnitude * sin(self.angle)
        return SurfaceVector(x=surface_x, y=surface_y)


class TypePosition(Enum):
    ONLY_ECEF = 1,
    ONLY_LLH = 2,
    ECEF_LLH = 3


class ENUCoordinates(object):
    def __init__(self, east: float = 0,
                 north: float = 0,
                 up: float = 0):
        self.east = east
        self.north = north
        self.up = up


class GeoLocalConstants:
    eps_difference_coords = 1e-10


class GeoPosition(object):
    @staticmethod
    def point_to_geoposition(point: Point,
                             request_ecef_conv: bool = False) -> "GeoPosition":
        if not point:
            return None
        try:
            return GeoPosition(latitude=point.y,
                               longitude=point.x,
                               altitude=0,
                               request_ecef_conv=request_ecef_conv)
        except Exception:
            return None

    def __init__(self,
                 latitude: float,
                 longitude: float,
                 altitude: float,
                 request_ecef_conv: bool = False):
        self.latitude = latitude
        self.longitude = longitude
        self.altitude = altitude
        self.ecef_x = 0
        self.ecef_y = 0
        self.ecef_z = 0
        self.type_position = TypePosition.ONLY_LLH

        if request_ecef_conv:
            self.ecef_x, self.ecef_y, self.ecef_z = GeoTranslations.llh2xyz(lat=self.latitude,
                                                                            long=self.longitude,
                                                                            ellht=0)
            self.type_position = TypePosition.ECEF_LLH

    def to_string(self) -> str:
        return "Lat: {}, Long: {}".format(self.latitude,
                                          self.longitude)

    @staticmethod
    def remove_duplicates(list_points: List["GeoPosition"]) -> List["GeoPosition"]:
        if not GeoPosition.check_if_duplicates(list_points=list_points):
            return list_points

        list_new = list()

        for geo_point in list_points:
            if not geo_point:
                continue

            if not list_new or geo_point not in list_new:
                list_new.append(geo_point)
            else:
                del geo_point

        del list_points

        return list_new

    @staticmethod
    def check_if_duplicates(list_points: List["GeoPosition"]) -> bool:
        if not list_points:
            return False

        if len(list_points) == 1:
            return False

        for index_point_start in range(0, len(list_points)-1):
            point_master = list_points[index_point_start]
            for index_point_end in range(index_point_start+1, len(list_points)):
                point_check = list_points[index_point_end]

                if point_master == point_check:
                    return True

        return False

    def __eq__(self, other: "GeoPosition"):
        if not other:
            return False
        if fabs(self.latitude-other.latitude) > GeoLocalConstants.eps_difference_coords:
            return False
        if fabs(self.longitude-other.longitude) > GeoLocalConstants.eps_difference_coords:
            return False
        if fabs(self.altitude-other.altitude) > GeoLocalConstants.eps_difference_coords:
            return False

        return True

    def consolidate_calculation(self) -> bool:
        if self.type_position == TypePosition.ECEF_LLH:
            return True

        if self.type_position == TypePosition.ONLY_ECEF:
            self.latitude, self.longitude, self.altitude = GeoTranslations.xyz2llh(x=self.ecef_x,
                                                                                   y=self.ecef_y,
                                                                                   z=self.ecef_z)
        elif self.type_position == TypePosition.ONLY_LLH:
            self.ecef_x, self.ecef_y, self.ecef_z = GeoTranslations.llh2xyz(lat=self.latitude,
                                                                            long=self.longitude,
                                                                            ellht=0)
        self.type_position = TypePosition.ECEF_LLH

    def to_point(self) -> Point:

        if self.type_position == TypePosition.ONLY_ECEF:
            self.latitude, self.longitude, self.altitude = GeoTranslations.xyz2llh(x=self.ecef_x,
                                                                                   y=self.ecef_y,
                                                                                   z=self.ecef_z)
            self.type_position = TypePosition.ECEF_LLH

        return Point(x=self.longitude,
                     y=self.latitude,
                     srid=4326)

    def add_enu_distance(self, enu_distance: List[float]) -> "GeoPosition":
        try:
            if not enu_distance or len(enu_distance) < 2:
                return self.to_point()

            self.ecef_x, self.ecef_y, self.ecef_z = \
                GeoTranslations.enu2xyz(lat=self.latitude,
                                        long=self.longitude,
                                        east=enu_distance[0],
                                        north=enu_distance[1],
                                        up=0)

            self.latitude, self.longitude, self.altitude = GeoTranslations.xyz2llh(x=self.ecef_x,
                                                                                   y=self.ecef_y,
                                                                                   z=self.ecef_z)
            return self
        except Exception as ex:
            return self

    def calculate_vector_distance(self, ref_pos: "GeoPosition") -> SurfaceVector:
        self.consolidate_calculation()
        ref_pos.consolidate_calculation()

        (east, north, up) = GeoTranslations.xyz2enu_bis(pos_to_translate=self,
                                                        ref_pos=ref_pos)

        return SurfaceVector(x=east,
                             y=north)


class RotationMatrixType(Enum):
    TYPE_ECEF_LLH = 1,
    TYPE_LLH_ECEF = 2


class GeoTranslations:
    @staticmethod
    def calculate_rotation_matrix(latitude: float,
                                  longitude: float,
                                  type_matrix: RotationMatrixType) -> np.array:
        """
        function to calculate rotation matrix from position latitude and longitude
        :param latitude: latitude in decimal degrees
        :param longitude: longitude in decimal degrees
        :param type_matrix: RotationMatrixType.TYPE_ECEF_LLH or RotationMatrixType.TYPE_LLH_ECEF
        :return: rotation_matrix np.array
        """

        lat_rad = radians(latitude)
        long_rad = radians(longitude)
        sin_lat = sin(lat_rad)
        cos_lat = cos(lat_rad)
        sin_long = sin(long_rad)
        cos_long = cos(long_rad)

        if type_matrix == RotationMatrixType.TYPE_LLH_ECEF:
            rotate = np.array([[-sin_long, -sin_lat * cos_long, cos_lat * cos_long],
                               [cos_long, -sin_lat * sin_long, cos_lat * sin_long],
                               [0, cos_lat, sin_lat]])

        elif type_matrix == RotationMatrixType.TYPE_ECEF_LLH:
            rotate = np.array([[-sin_long, cos_long, 0],
                               [-sin_lat * cos_long, -sin_lat * sin_long, cos_lat],
                               [cos_lat * cos_long, cos_lat * sin_long, sin_lat]])

        return rotate

    @staticmethod
    def enu2xyz(lat, long, east, north, up) -> (float, float, float):
        """
        function to convert a vector in a local east, north, up reference frame to
        a vector in a cartesian x, y, z reference frame
        :param lat: latitude in decimal degrees
        :param long: longitude in decimal degrees
        :param east: in metres
        :param north: in metres
        :param up: in metres
        :return: x, y, z in metres
        """
        # Create ENU Vector
        enu = np.array([[east],
                        [north],
                        [up]])
        # Create Rotation Matrix

        rotate = GeoTranslations.calculate_rotation_matrix(latitude=lat,
                                                           longitude=long,
                                                           type_matrix=RotationMatrixType.TYPE_LLH_ECEF)

        inv_rotate = np.linalg.inv(rotate)

        delta_xyz = np.dot(inv_rotate, enu)
        # Assign to separate variables

        org_x, org_y, org_z = GeoTranslations.llh2xyz(lat=lat,
                                                      long=long,
                                                      ellht=0)

        x = org_x + float(delta_xyz[0])
        y = org_y + float(delta_xyz[1])
        z = org_z + float(delta_xyz[2])

        return x, y, z

    @staticmethod
    def xyz2llh(x, y, z, ellipsoid=grs80) -> (float, float, float):
        # Add input for ellipsoid (default: grs80)
        """
        Input: Cartesian XYZ coordinate in metres
        Output: Latitude and Longitude in Decimal
        Degrees and Ellipsoidal Height in Metres
        """
        # Calculate Longitude
        long = atan2(y, x)
        # Calculate Latitude
        p = sqrt(x ** 2 + y ** 2)
        latinit = atan((z * (1 + ellipsoid.ecc2sq)) / p)
        lat = latinit
        itercheck = 1
        while abs(itercheck) > 1e-10:
            nu = ellipsoid.semimaj / (sqrt(1 - ellipsoid.ecc1sq * (sin(lat)) ** 2))
            itercheck = lat - atan((z + nu * ellipsoid.ecc1sq * sin(lat)) / p)
            lat = atan((z + nu * ellipsoid.ecc1sq * sin(lat)) / p)
        nu = ellipsoid.semimaj / (sqrt(1 - ellipsoid.ecc1sq * (sin(lat)) ** 2))
        ellht = p / (cos(lat)) - nu
        # Convert Latitude and Longitude to Degrees
        lat = degrees(lat)
        long = degrees(long)
        return lat, long, ellht

    @staticmethod
    def xyz2enu(lat, long, x, y, z):
        """
         function to convert a vector in a cartesian x, y, z reference frame to a
         vector in a local east, north, up reference frame
         :param lat: latitude in decimal degrees
         :param long: longitude in decimal degrees
         :param x: in metres
         :param y: in metres
         :param z: in metres
         :return: east, north, up in metres
         """
        # Create XYZ Vector

        (xref, yref, zref) = GeoTranslations.llh2xyz(lat=lat,
                                                     long=long,
                                                     ellht=0)

        xyz = np.array([[x - xref],
                        [y - yref],
                        [z - zref]])
        # Create Rotation Matrix
        rotate = GeoTranslations.calculate_rotation_matrix(latitude=lat,
                                                           longitude=long,
                                                           type_matrix=RotationMatrixType.TYPE_ECEF_LLH)
        enu = np.dot(rotate, xyz)
        # Assign to separate variables
        east = float(enu[0])
        north = float(enu[1])
        up = float(enu[2])
        return east, north, up

    @staticmethod
    def xyz2enu_bis(pos_to_translate: GeoPosition,
                    ref_pos: GeoPosition) -> (float, float, float):
        """
        function to convert a vector in a cartesian x, y, z reference frame to a
        vector in a local east, north, up reference frame
        :param pos_to_translate GeoPosition to be converted in ENU Coordinates
        :param ref_pos: GeoPosition reference position
        :return: east, north, up in meters
        """
        # Create Delta XYZ Vector
        difxyz = np.array([[pos_to_translate.ecef_x-ref_pos.ecef_x],
                        [pos_to_translate.ecef_y-ref_pos.ecef_y],
                        [pos_to_translate.ecef_z-ref_pos.ecef_z]])
        # Create Rotation Matrix
        rotate = GeoTranslations.calculate_rotation_matrix(latitude=ref_pos.latitude,
                                                           longitude=ref_pos.longitude,
                                                           type_matrix=RotationMatrixType.TYPE_ECEF_LLH)
        enu = np.dot(rotate, difxyz)
        # Assign to separate variables
        east = float(enu[0])
        north = float(enu[1])
        up = float(enu[2])
        return east, north, up

    @staticmethod
    def surfacedistanceheading2llh(surface_distance_m: float,
                                   surface_heading_deg: float,
                                   org_latitude: float,
                                   org_longitude: float) -> (float, float, float):
        """
        function to convert a distance, heading in surface from origin to latitude, longitude position
        :param surface_distance_m: in metres
        :param surface_heading_deg: in degree
        :param org_latitude: latitude origin in degree
        :param org_longitude: longitude origin in degree
        :return: lat_deg, long_deg, altitude in metres
        """

        east = surface_distance_m * cos(radians(surface_heading_deg))
        north = surface_distance_m * cos(radians(surface_heading_deg))
        up = 0

        out_lat, out_long, out_altit = GeoTranslations.enu2llh(east=east,
                                                               north=north,
                                                               up=up,
                                                               org_lat=org_latitude,
                                                               org_long=org_longitude)

        return out_lat, out_long, out_altit

    @staticmethod
    def enu2llh(east: float,
                north: float,
                up: float,
                org_lat: float,
                org_long: float) -> (float, float, float):
        """
        function to convert a vector in a llh position reference frame to a
        vector in a local east, north, up reference frame
        :param east: in metres
        :param north: in metres
        :param up: in metres
        :param org_lat: latitude in decimal degrees
        :param org_long: longitude in decimal degrees
        :return: lat_deg, long_deg, altitude in metres
        """
        try:
            enu = np.array([[east],
                            [north],
                            [up]])

            rotate = GeoTranslations.calculate_rotation_matrix(latitude=org_lat,
                                                               longitude=org_long,
                                                               type_matrix=RotationMatrixType.TYPE_ECEF_LLH)

            inv_rotate = np.linalg.inv(rotate)
            diff_xyz = np.dot(inv_rotate, enu)
            (tmp_x, tmp_y, tmp_z) = GeoTranslations.llh2xyz(lat=org_lat,
                                                            long=org_long,
                                                            ellht=0)
            x = tmp_x + float(diff_xyz[0])
            y = tmp_y + float(diff_xyz[1])
            z = tmp_z + float(diff_xyz[2])

            (out_lat, out_long, out_alt) = GeoTranslations.xyz2llh(x=x,
                                                                   y=y,
                                                                   z=z)

            return out_lat, out_long, out_alt
        except Exception as ex:
            return 0, 0, 0

    @staticmethod
    def llh2xyz(lat, long, ellht, ellipsoid=grs80):
        # Add input for ellipsoid (default: grs80)
        """
        Input: Latitude and Longitude in Decimal Degrees, Ellipsoidal Height in metres
        Output: Cartesian X, Y, Z Coordinates in metres
        """
        # Convert lat & long to radians
        lat = radians(lat)
        long = radians(long)
        # Calculate Ellipsoid Radius of Curvature in the Prime Vertical - nu
        if lat == 0:
            nu = grs80.semimaj
        else:
            nu = ellipsoid.semimaj / (sqrt(1 - ellipsoid.ecc1sq * (sin(lat) ** 2)))
        # Calculate x, y, z
        x = (nu + ellht) * cos(lat) * cos(long)
        y = (nu + ellht) * cos(lat) * sin(long)
        z = ((ellipsoid.semimin ** 2 / ellipsoid.semimaj ** 2) * nu + ellht) * sin(lat)
        return x, y, z

    @staticmethod
    def vincdir(lat1, lon1, azimuth1to2, ell_dist, ellipsoid=grs80):
        """
        Vincenty's Direct Formula
        :param lat1: Latitude of Point 1 (Decimal Degrees)
        :param lon1: Longitude of Point 1 (Decimal Degrees)
        :param azimuth1to2: Azimuth from Point 1 to 2 (Decimal Degrees)
        :param ell_dist: Ellipsoidal Distance between Points 1 and 2 (m)
        :param ellipsoid: Ellipsoid Object
        :return: lat2: Latitude of Point 2 (Decimal Degrees),
                 lon2: Longitude of Point 2 (Decimal Degrees),
                 azimuth2to1: Azimuth from Point 2 to 1 (Decimal Degrees)

        Code review: 14-08-2018 Craig Harrison
        """

        azimuth1to2 = radians(azimuth1to2)

        # Equation numbering is from the GDA2020 Tech Manual v1.0

        # Eq. 88
        u1 = atan((1 - ellipsoid.f) * tan(radians(lat1)))

        # Eq. 89
        sigma1 = atan2(tan(u1), cos(azimuth1to2))

        # Eq. 90
        alpha = asin(cos(u1) * sin(azimuth1to2))

        # Eq. 91
        u_squared = cos(alpha)**2 \
            * (ellipsoid.semimaj**2 - ellipsoid.semimin**2) \
            / ellipsoid.semimin**2

        # Eq. 92
        a = 1 + (u_squared / 16384) \
            * (4096 + u_squared * (-768 + u_squared * (320 - 175 * u_squared)))

        # Eq. 93
        b = (u_squared / 1024) \
            * (256 + u_squared * (-128 + u_squared * (74 - 47 * u_squared)))

        # Eq. 94
        sigma = ell_dist / (ellipsoid.semimin * a)

        # Iterate until the change in sigma, delta_sigma, is insignificant (< 1e-9)
        # or after 1000 iterations have been completed
        two_sigma_m = 0
        for i in range(1000):

            # Eq. 95
            two_sigma_m = 2*sigma1 + sigma

            # Eq. 96
            delta_sigma = b * sin(sigma) * (cos(two_sigma_m) + (b/4)
                                            * (cos(sigma)
                                               * (-1 + 2 * cos(two_sigma_m)**2)
                                               - (b/6) * cos(two_sigma_m)
                                               * (-3 + 4 * sin(sigma)**2)
                                               * (-3 + 4 * cos(two_sigma_m)**2)))
            new_sigma = (ell_dist / (ellipsoid.semimin * a)) + delta_sigma
            sigma_change = new_sigma - sigma
            sigma = new_sigma

            if abs(sigma_change) < 1e-12:
                break

        # Calculate the Latitude of Point 2
        # Eq. 98
        lat2 = atan2(sin(u1)*cos(sigma) + cos(u1)*sin(sigma)*cos(azimuth1to2),
                     (1 - ellipsoid.f)
                     * sqrt(sin(alpha)**2 + (sin(u1)*sin(sigma)
                            - cos(u1)*cos(sigma)*cos(azimuth1to2))**2))
        lat2 = degrees(lat2)

        # Calculate the Longitude of Point 2
        # Eq. 99
        lon = atan2(sin(sigma)*sin(azimuth1to2),
                    cos(u1)*cos(sigma) - sin(u1)*sin(sigma)*cos(azimuth1to2))

        # Eq. 100
        c = (ellipsoid.f/16)*cos(alpha)**2 \
            * (4 + ellipsoid.f*(4 - 3*cos(alpha)**2))

        # Eq. 101
        omega = lon - (1-c)*ellipsoid.f*sin(alpha) \
            * (sigma + c*sin(sigma)*(cos(two_sigma_m) + c*cos(sigma)
                                     * (-1 + 2*cos(two_sigma_m)**2)))

        # Eq. 102
        lon2 = float(lon1) + degrees(omega)

        # Calculate the Reverse Azimuth
        azimuth2to1 = degrees(atan2(sin(alpha), -sin(u1)*sin(sigma)
                              + cos(u1)*cos(sigma)*cos(azimuth1to2))) + 180

        return round(lat2, 11), round(lon2, 11), round(azimuth2to1, 9)



