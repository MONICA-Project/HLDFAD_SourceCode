import logging
import json
from general_types.virtual_classes import ObservableGeneric
from general_types.label_ogc import LabelThings, LabelObservationType
from jobs.models import CameraRegistration, WristbandRegistration, DeviceType, DeviceRegistration
# from utility.utility_catalog_cached import UtilityCatalogCached
from typing import List, Dict

logger = logging.getLogger('textlogger')


class DatastreamTopicAdapter(object):
    def __init__(self,
                 thing_name: str,
                 prefix_topic: str):
        self.datastreamid = 0
        self.name_complete = ''
        self.registration_json = ''
        self.thing_name = thing_name
        self.matching = False
        self.label_matching = ''
        self.topic_associated = ''
        self.description = ''
        self.prefix_topic = prefix_topic
        self.datastream_db = None
        self.device_registration = None
        self.device_type: DeviceType = DeviceType.NOT_DEFINED
        self.tagId = str()

        if thing_name == LabelThings.LABEL_THING_WRISTBANDGW:
            self.device_type = DeviceType.WRISTBAND
        elif thing_name == LabelThings.LABEL_THING_SFN:
            self.device_type = DeviceType.CAMERA
        # self.set_properties_from_json(json_message=json_message,
        #                               prefix_topic=prefix_topic,
        #                               device_type=device_type)

    def get_device_registration(self) -> DeviceRegistration:
        return self.device_registration

    def get_deriving_thing_name(self):
        return self.thing_name

    def get_registration_json(self):
        return self.registration_json

    def get_datastream_object_db(self):
        return self.datastream_db

    @classmethod
    def from_json(cls, json_data):
        return cls(json_data)

    def to_json(self):
         return json.dumps(
             {
                 '@iot.id':             self.datastreamid,
                 'name':                self.name_complete,
                 'description':         self.description,
                 'topic_associated':    self.topic_associated,
                 'tagId':               self.tagId
             }
         )

    @staticmethod
    def convert_observable_to_topic(gost_label: str, observable: ObservableGeneric) -> str:
        if not observable:
            return ''

        datastream_id = observable.get_datastream_id()
        return DatastreamTopicAdapter.get_mqtt_topic(gost_label=gost_label,
                                                     datastream_id=datastream_id)

    @staticmethod
    def get_mqtt_topic(gost_label: str, datastream_id: int) -> str:
        return '{0}/Datastreams({1})/Observations' \
            .format(gost_label,
                    str(datastream_id))

    def get_datastreams_suburl(self):
        return 'Datastreams({0})'.format(str(self.datastreamid))

    def get_device_registration(self) -> DeviceRegistration:
        return self.device_registration

    def set_properties_from_text(self, name_complete, datastream_id, prefix_topic: str = '', description=""):
        try:
            self.datastreamid = datastream_id
            self.name_complete = name_complete
            # self.topic_associated = '{0}/Datastreams({1})/Observations' \
            #     .format(prefix_topic, self.datastreamid)
            self.description = description
            self.tagId = name_complete
            self.topic_associated = DatastreamTopicAdapter.get_mqtt_topic(gost_label=prefix_topic,
                                                                          datastream_id=datastream_id)
        except Exception as ex:
            logger.error('DataStreamTopicAdapter set_properties_from_text Exception: {}'.format(ex))

    def set_properties_from_json(self, json_message: dict) -> bool:
        try:
            if not json_message:
                return False

            self.datastreamid = json_message['@iot.id']
            self.name_complete = json_message['name']
            self.description = json_message['description']
            self.topic_associated ='Datastreams({0})/Observations'\
                .format(self.datastreamid)

            if self.prefix_topic:
                self.topic_associated = '{0}/Datastreams({1})/Observations'\
                .format(self.prefix_topic, self.datastreamid)

            if 'unitOfMeasurement' not in json_message:
                return False

            if self.device_type == DeviceType.WRISTBAND:
                if 'metadata' not in json_message['unitOfMeasurement']:
                    return False

                self.registration_json = json_message['unitOfMeasurement']['metadata']
                self.device_registration = WristbandRegistration()
                self.device_registration.set_associated_obs_type(obs_type=LabelObservationType.LABEL_OBSTYPE_LOCALIZATION)

                if 'tagId' not in self.registration_json:
                    return False

                self.tagId = self.registration_json['tagId']
            elif self.device_type == DeviceType.CAMERA:
                self.registration_json = json_message['unitOfMeasurement']
                self.device_registration = CameraRegistration()
                self.device_registration.set_associated_obs_type(obs_type=LabelObservationType.LABEL_OBSTYPE_CROWDDENSITY)

                self.tagId = self.device_registration.get_device_id()

            if self.device_registration:
                self.device_registration.set_datastream_id(datastream_id=self.datastreamid)
                self.device_registration.set_device_id(device_id=self.name_complete)

                if not self.device_registration.from_dictionary(dictionary=self.registration_json):
                    return False

            return True
        except Exception as ex:
            logger.error('DatastreamTopicAdapter::set_properties_from_json Exception: {}'.format(ex))
            return False

    def get_matching(self):
        return self.matching

    def get_associated_topic(self):
        return self.topic_associated

    def is_sensor_matching(self, device_id):
        string_check = self.name_complete
        string_check = string_check.replace(self.thing_name, '')

        if device_id not in string_check:
            return False

        return True

    def set_label(self, label):
        self.label_matching = label
        self.matching = True


class HelperDatastreamGenerator:
    @staticmethod
    def debug_create_datastreams_from_dictionary(specific_argument: str, dictionary_topics: Dict[int, List[str]]) -> \
            (Dict[str, List[DatastreamTopicAdapter]], List[DatastreamTopicAdapter]):

        try:
            if not dictionary_topics:
                return None, None

            return_dictionary = dict()
            return_list = list()

            for datastream_id in dictionary_topics:
                list_string = dictionary_topics[datastream_id]

                if len(list_string) < 2:
                    continue

                datastream_topic_adapter = DatastreamTopicAdapter(thing_name=list_string[1],
                                                                  prefix_topic='GOST_LARGE_SCALE_TEST')
                datastream_topic_adapter.datastreamid = datastream_id
                datastream_topic_adapter.topic_associated = list_string[0]
                datastream_topic_adapter.name_complete = list_string[1]
                datastream_topic_adapter.matching = True
                datastream_topic_adapter.thing_name = list_string[1]
                datastream_topic_adapter.tagId = datastream_topic_adapter.thing_name.replace('{0}/868/Localization-Wristband/'.format(LabelThings.LABEL_THING_WRISTBANDGW), '')
                datastream_topic_adapter.label_matching = specific_argument
                return_list.append(datastream_topic_adapter)

            return_dictionary[specific_argument] = return_list

            return return_dictionary, return_list
        except Exception as ex:
            logger.error('debug_create_datastreams_from_dictionary Exception: {}'.format(ex))
            return None, None

