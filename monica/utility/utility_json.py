import json
from general_types.general_enums import MQTTPayloadConversion
from general_types.modelsenums import OutputMessageType
from typing import List
import logging
import os

logger = logging.getLogger('textlogger')


class LabelJSONConf:
    LABEL_LIST_OUTPUT_MESSAGE = "LIST_OUTPUT_MESSAGES"
    LABEL_LIST_MQTTMESSAGES = "LIST_MQTT_OUTPUT_TYPE"
    LABEL_OUTPUTMESSAGE_QUEUEDETECTION = "OUTPUT_MESSAGE_TYPE_QUEUEDETECTIONALERT"
    LABEL_OUTPUTMESSAGE_CROWDHEATMAPOUTPUT = "OUTPUT_MESSAGE_TYPE_CROWDHEATMAPOUTPUT"
    LABEL_MQTT_OUTPUT_TYPE_STANDARDDICT="TYPE_CONVERSION_STANDARDDICTIONARY"
    LABEL_MQTT_OUTPUT_TYPE_OGCDICTIONARY="TYPE_CONVERSION_OGCDICTIONARY"


class UtilityJSONConfig:
    @staticmethod
    def convert_liststring_to_mqttoutputtype(list_strings: List[str]) -> List[MQTTPayloadConversion]:
        if not list_strings:
            return None

        list_output = list()

        for string in list_strings:
            if string == LabelJSONConf.LABEL_MQTT_OUTPUT_TYPE_STANDARDDICT:
                list_output.append(MQTTPayloadConversion.TYPE_CONVERSION_STANDARDDICTIONARY)
            elif string == LabelJSONConf.LABEL_MQTT_OUTPUT_TYPE_OGCDICTIONARY:
                list_output.append(MQTTPayloadConversion.TYPE_CONVERSION_OGCDICTIONARY)

        return list_output

    @staticmethod
    def convert_liststring_to_outputmessages(list_strings: List[str]) -> List[OutputMessageType]:
        if not list_strings:
            return None

        list_output = list()

        for string in list_strings:
            if string == LabelJSONConf.LABEL_OUTPUTMESSAGE_CROWDHEATMAPOUTPUT:
                list_output.append(OutputMessageType.OUTPUT_MESSAGE_TYPE_CROWDHEATMAPOUTPUT)
            elif string == LabelJSONConf.LABEL_OUTPUTMESSAGE_QUEUEDETECTION:
                list_output.append(OutputMessageType.OUTPUT_MESSAGE_TYPE_QUEUEDETECTIONALERT)

        return list_output

    @staticmethod
    def convert_file_dictionary(json_conf_path: str):
        try:
            if not os.path.exists(json_conf_path):
                logger.error('UtilityJSONConfig Path NOT Found: {}'.format(json_conf_path))
                return None

            dictionary_complete = None
            with open(json_conf_path, 'r') as file_read:
                dictionary_complete = json.load(file_read)

            return dictionary_complete
        except Exception as ex:
            logger.error('UtilityJSON convert_file_dictionary Exception: {}'.format(ex))
            return None

    @staticmethod
    def get_list_output(json_conf_path: str) -> List[OutputMessageType]:
        try:
            dictionary_complete = UtilityJSONConfig.convert_file_dictionary(json_conf_path=json_conf_path)

            if not dictionary_complete:
                return None

            if LabelJSONConf.LABEL_LIST_OUTPUT_MESSAGE not in dictionary_complete:
                return None

            list_output_strings = dictionary_complete[LabelJSONConf.LABEL_LIST_OUTPUT_MESSAGE]

            if not list_output_strings:
                return None

            return UtilityJSONConfig.convert_liststring_to_outputmessages(list_strings=list_output_strings)
        except Exception as ex:
            logger.error('UtilityJSON get_list_output Exception: {}'.format(ex))
            return None

    @staticmethod
    def get_list_mqtttypes(json_conf_path: str) -> List[MQTTPayloadConversion]:
        try:
            dictionary_complete = UtilityJSONConfig.convert_file_dictionary(json_conf_path=json_conf_path)

            if not dictionary_complete:
                return None

            if LabelJSONConf.LABEL_LIST_MQTTMESSAGES not in dictionary_complete:
                return None

            list_mqtt_strings = dictionary_complete[LabelJSONConf.LABEL_LIST_MQTTMESSAGES]

            if not list_mqtt_strings:
                return None

            return UtilityJSONConfig.convert_liststring_to_mqttoutputtype(list_strings=list_mqtt_strings)
        except Exception as ex:
            logger.error('UtilityJSON get_list_output Exception: {}'.format(ex))
            return None
