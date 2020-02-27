from general_types.modelsenums import OutputMessageType
from general_types.general_enums import MQTTPayloadConversion
from typing import Dict, Any, List, Tuple
import datetime
from django.contrib.gis.geos import Point, MultiPoint, Polygon
import json
import logging

logger = logging.getLogger('textlogger')


class Dictionarizable(object):
    @staticmethod
    def convert_geojsonpoint_todictionary(position: Point) -> Dict[str, Any]:
        if not position:
            return None

        return {"coordinates": [position.x,
                                position.y],
                "type": "Point"}

    @staticmethod
    def convert_polygon_to_listpoints(polygon: Polygon) -> List[List[float]]:
        try:
            if not polygon:
                return None

            list_points = list()

            for index_ring in range(0, len(polygon)):
                external_ring = polygon[index_ring]
                for index_point in range(0, len(external_ring)):
                    x = external_ring[index_point][0]
                    y = external_ring[index_point][1]
                    list_points.append([x, y])

            return list_points
        except Exception as ex:
            logger.error('convert_polygon_to_listpoints Exception: {}'.format(ex))
            return None

    @staticmethod
    def convert_polygon_todictionary(polygon: Polygon) -> Dict[str, Any]:
        try:
            if not polygon:
                return None

            list_points = Dictionarizable.convert_polygon_to_listpoints(polygon=polygon)

            if not list_points:
                return None

            return {
                "type": "Feature",
                "properties": {},
                "geometry": {
                    "coordinates":
                        [list_points],
                    "type": "Polygon"
                }
            }

        except Exception as ex:
            logger.error('convert_polygon_to_listpoints Exception: {}'.format(ex))
            return None

    @staticmethod
    def convert_multipoint_todictionary(multipoint: MultiPoint) -> Dict[str, Any]:
        if not multipoint:
            return None

        list_dict_points = list()

        for point in multipoint:
            if not point:
                continue

            list_dict_points.append((point.x, point.y))

        return {
            "coordinates": [
                json.dumps(list_dict_points)],
            "type": "MultiPoint"
        }

    def get_list_keys(self) -> List[str]:
        raise NotImplemented

    def get_specific_value(self, key: str) -> Any:
        raise NotImplemented

    @staticmethod
    def dictionarize_element(elem_to_dict: Any) -> Any:
        try:
            if isinstance(elem_to_dict, datetime.datetime):
                return elem_to_dict.isoformat()

            elif isinstance(elem_to_dict, Point):
                return Dictionarizable.convert_geojsonpoint_todictionary(position=elem_to_dict)

            elif isinstance(elem_to_dict, MultiPoint):
                return Dictionarizable.convert_multipoint_todictionary(multipoint=elem_to_dict)

            elif isinstance(elem_to_dict, Polygon):
                return Dictionarizable.convert_polygon_todictionary(polygon=elem_to_dict)

            elif isinstance(elem_to_dict, list):
                list_return = list()

                for elem in elem_to_dict:
                    dict_elem = Dictionarizable.dictionarize_element(elem_to_dict=elem)

                    list_return.append(dict_elem)

                return list_return
            return elem_to_dict
        except Exception as ex:
            logger.error('dictionarize_element Exception: {}'.format(ex))
            return None

    def to_dictionary(self) -> Dict[str, Any]:
        try:
            list_labels = self.get_list_keys()

            if not list_labels:
                return None

            dictionary = dict()

            for key in list_labels:
                value = self.get_specific_value(key)

                if value is None:
                    continue

                value = Dictionarizable.dictionarize_element(elem_to_dict=value)

                dictionary[key] = value

            return dictionary
        except Exception as ex:
            logger.error('to_dictionary Exception: {}'.format(ex))
            return None

    def to_string(self) -> str:
        try:
            dictionary = self.to_dictionary()

            if not dictionary:
                return str()

            return json.dumps(dictionary)
        except Exception as ex:
            logger.error('Dictionarizable to_string Exception: {}'.format(ex))
            return str()

    def set_single_property(self, key: str, value: Any) -> bool:
        raise NotImplemented

    def from_dictionary(self, dictionary: Dict[str, Any]) -> bool:
        if not dictionary:
            return False
        try:
            counter_elem_set = 0
            for key in dictionary:
                value = dictionary[key]
                if self.set_single_property(key=key,
                                            value=value):
                    counter_elem_set += 1
            if counter_elem_set == 0:
                return False

            return True
        except Exception as ex:
            logger.error('Dictionarizable from_dictionary Exception: {}'.format(ex))
            return False


class OutputMessage(Dictionarizable):
    def set_timestamp(self, timestamp: datetime.datetime):
        raise NotImplemented

    def get_outputmessagetype(self) -> OutputMessageType:
        raise NotImplemented

    def get_timestamp(self) -> datetime.datetime:
        raise NotImplemented

    def to_specific_dictionary(self, mqtt_payloadtype: MQTTPayloadConversion) -> Dict[str, Any]:
        if mqtt_payloadtype == MQTTPayloadConversion.TYPE_CONVERSION_STANDARDDICTIONARY:
            return self.to_dictionary()
        elif mqtt_payloadtype == MQTTPayloadConversion.TYPE_CONVERSION_OGCDICTIONARY:
            return self.to_ogc_dictionary()

        return None

    def to_ogc_dictionary(self) -> Dict[str, Any]:
        return_dictionary = {"phenomenonTime": self.get_timestamp().isoformat(),
                             "result": self.to_dictionary()
                             }
        return return_dictionary


# FIXME: Add Dependency Dictionarizable
class ObservableGeneric(object):
    def __init__(self):
        self.observation_id = 0
        self.run_id = 0
        self.datastream_id = 0
        self.device_id = str()
        self.timestamp: datetime.datetime = datetime.datetime.now()
        self.label_cache_group = str()
        self.is_exploited = False
        self.pilot_name = str()
        self.obs_iot_id = str()

    @classmethod
    def from_json(cls, json_data):
        return cls(json_data)

    def __eq__(self, other) -> bool:
        if not isinstance(other, self.__class__):
            return False

        return self.observation_id == other.observation_id and self.datastream_id == other.datastream_id

    def __ne__(self, other) -> bool:
        if not isinstance(other, self.__class__):
            return True

        return self.observation_id != other.observation_id or self.datastream_id != other.datastream_id

    def __hash__(self, *args, **kwargs):
        return self.observation_id

    def set_obs_iot_id(self, iot_id: str):
        self.obs_iot_id = iot_id

    def get_obs_iot_id(self):
        return self.obs_iot_id

    def set_datastream_id(self, datastream_id: int):
        self.datastream_id = datastream_id

    def get_datastream_id(self) -> int:
        return self.datastream_id

    def from_dictionary(self, dictionary: Dict[str, Any]):
        raise NotImplemented

    def to_dictionary(self) -> Dict[str, Any]:
        return dict()

    def to_trace_string(self):
        return self.to_string()

    def to_string(self) -> str:
        return str(self.to_dictionary())

    def set_pilot_name(self, pilot_name: str):
        self.pilot_name = pilot_name

    def get_pilot_name(self) -> str:
        return self.pilot_name

    def get_timestamp(self) -> datetime.datetime:
        return self.timestamp

    def set_observable_id(self, observable_id: int):
        self.observation_id = observable_id

    def get_observable_id(self) -> int:
        return self.observation_id

    def set_label_cache(self, label_cache: str):
        self.label_cache_group = label_cache

    def get_label_cache(self) -> str:
        return self.label_cache_group

    def set_output_id(self, output_id: int):
        raise NotImplementedError

    def get_output_id(self) -> int:
        return 0

    def get_run_id(self) -> int:
        return self.run_id

    def set_run_id(self, run_id: int):
        self.run_id = run_id

    def ckeck_observable_complete(self) -> bool:
        return False

    def get_type_observable(self) -> str:
        raise NotImplementedError()

    def set_device_id(self, device_id):
        self.device_id = device_id

    def get_device_id(self) -> str:
        return self.device_id

    def check_is_observation(self, observation_id: int) -> bool:
        return observation_id == self.observation_id

    def check_equals(self, observation):
        if not observation:
            return False

        return self.check_is_observation(observation_id=observation.get_observable_id())
