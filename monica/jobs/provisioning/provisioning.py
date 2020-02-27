from general_types.virtual_classes import OutputMessage
from general_types.modelsenums import OutputMessageType
from general_types.general_enums import MQTTPayloadConversion
from general_types.labelsdictionaries import MQTTLabelsConfigurations
from shared.settings.appglobalconf import MQTT_BROKERPROVISIONING

import logging

from jobs.cache_redis import CachedComponents
from entities.mqtt_connection_info import MQTTConnectionParams
from utility.utility_database import UtilityDatabase
import paho.mqtt.publish as publish
from typing import Dict, Any, List
import datetime
import json

logger = logging.getLogger('textlogger')


class DateTimeEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime.datetime):
            return o.isoformat()

        return json.JSONEncoder.default(self, o)


class Provisioning:
    @staticmethod
    def get_topic_simplemqtt(message_output_type: OutputMessageType) -> str:
        if MQTTLabelsConfigurations.LABEL_DICTIONARY_TOPICS not in MQTT_BROKERPROVISIONING:
            return str('')

        dictionary_topics = MQTT_BROKERPROVISIONING[MQTTLabelsConfigurations.LABEL_DICTIONARY_TOPICS]

        if message_output_type == OutputMessageType.OUTPUT_MESSAGE_TYPE_QUEUEDETECTIONALERT \
                and MQTTLabelsConfigurations.LABEL_TOPICS_QUEUEDETECTIONALERT in dictionary_topics:
            return dictionary_topics[MQTTLabelsConfigurations.LABEL_TOPICS_QUEUEDETECTIONALERT]
        elif message_output_type == OutputMessageType.OUTPUT_MESSAGE_TYPE_CROWDHEATMAPOUTPUT \
                and MQTTLabelsConfigurations.LABEL_TOPICS_CROWDHEATMAPOUTPUT in dictionary_topics:
            return dictionary_topics[MQTTLabelsConfigurations.LABEL_TOPICS_CROWDHEATMAPOUTPUT]

        return str('')

    @staticmethod
    def get_simplemqtt_connectioninfo(message_output_type: OutputMessageType) -> MQTTConnectionParams:
        try:
            mqtt_message_info = MQTTConnectionParams(topic=Provisioning.get_topic_simplemqtt(message_output_type=message_output_type),
                                                     type_conversion=MQTTPayloadConversion.TYPE_CONVERSION_STANDARDDICTIONARY)

            mqtt_message_info.from_dictionary(dictionary=MQTT_BROKERPROVISIONING)

            return mqtt_message_info
        except Exception as ex:
            logger.error('Provisioning get_simplemqtt_connectioninfo Exception: {}'.format(ex))
            return None

    @staticmethod
    def get_servicecatalog_connection_info(message_output_type: OutputMessageType,
                                           username: str = str(),
                                           password: str = str()) -> MQTTConnectionParams:
        try:
            broker_connection_info = CachedComponents.get_brokeroutput_servicecatalog(output_message_type=message_output_type)

            if not broker_connection_info:
                return None

            return broker_connection_info.to_mqtt_connection_params(username=username,
                                                                    password=password)
        except Exception as ex:
            logger.error('get_servicecatalog_connection_info Exception: {}'.format(ex))
            return None

    @staticmethod
    def get_mqtt_connection_info(message_output_type: OutputMessageType,
                                 mqtt_dictionary_conversion_type: MQTTPayloadConversion,
                                 username: str = str(),
                                 password: str = str()) -> MQTTConnectionParams:
        try:
            if mqtt_dictionary_conversion_type == MQTTPayloadConversion.TYPE_CONVERSION_OGCDICTIONARY:
                return Provisioning.get_servicecatalog_connection_info(message_output_type=message_output_type,
                                                                       username=username,
                                                                       password=password)

            elif mqtt_dictionary_conversion_type == MQTTPayloadConversion.TYPE_CONVERSION_STANDARDDICTIONARY:
                return Provisioning.get_simplemqtt_connectioninfo(message_output_type=message_output_type)

            return None
        except Exception as ex:
            logger.error('get_mqtt_connection_info Exception: {}'.format(ex))
            return None

    @staticmethod
    def push_message_mqtt_queue(output_message: OutputMessage,
                                outputtype: MQTTPayloadConversion,
                                mqtt_connection_params: MQTTConnectionParams) -> bool:
        try:
            if not output_message or not mqtt_connection_params:
                return False

            logger.info('Pushing MQTT Message to URL: {0}:{1}, username: {2}, password: {3}'.format(mqtt_connection_params.m_url,
                                                                                                    mqtt_connection_params.m_tcpport,
                                                                                                    mqtt_connection_params.m_username,
                                                                                                    mqtt_connection_params.m_password))

            if not mqtt_connection_params.m_topic:
                logger.error('push_message_mqtt_queue Cannot Find Topic')
                return False

            dictionary = output_message.to_specific_dictionary(mqtt_payloadtype=outputtype)

            if not dictionary:
                return None

            string_json = json.dumps(obj=dictionary,
                                     cls=DateTimeEncoder)

            dict_auth = mqtt_connection_params.get_authentication_info()

            publish.single(topic=mqtt_connection_params.m_topic,
                           payload=string_json,
                           hostname=mqtt_connection_params.m_url,
                           port=mqtt_connection_params.m_tcpport,
                           client_id=mqtt_connection_params.m_client_id,
                           retain=False,
                           auth=dict_auth
                           )

            logger.info('Push MQTT Message to URL: {0}:{1}, topic: {2}, messageJson: {3}'.
                        format(str(mqtt_connection_params.m_url),
                               mqtt_connection_params.m_tcpport,
                               mqtt_connection_params.m_topic,
                               string_json))

            return True

        except Exception as ex:
            logger.error('Exception push_serializer_mqtt_queue: {}'.format(ex))
            return False

    # FIXME: Defines correcly MQTT_BROKERPROVISIONING['URL'] (it could be BROKER_URL?)
    # FIXME: Defines inheritance for output classes CrowdHeatmapOutput and QueueDetectionAlert

    @staticmethod
    def deliver_output_messages(list_output_messages: List[OutputMessage],
                                output_type: MQTTPayloadConversion,
                                mqtt_connection_info: MQTTConnectionParams) -> bool:
        try:
            if not list_output_messages or not mqtt_connection_info:
                return False

            for output_message in list_output_messages:
                if not output_message:
                    continue

                Provisioning.push_message_mqtt_queue(output_message=output_message,
                                                     outputtype=output_type,
                                                     mqtt_connection_params=mqtt_connection_info)

            return True
        except Exception as ex:
            logger.error('Provisioning deliver_output_messages Exception: {}'.format(ex))
            return False

    @staticmethod
    def get_list_messages(outmessagetype: OutputMessageType) -> List[OutputMessage]:
        try:
            list_outputs_id = CachedComponents.get_list_outputmessage_ids(outmessagetype=outmessagetype)

            if not list_outputs_id:
                return None

            list_output_messages = UtilityDatabase.get_list_messageoutput_byids(list_ids=list_outputs_id,
                                                                                outputmessagetype=outmessagetype)

            return list_output_messages
        except Exception as ex:
            logger.error('get_list_messages Exception: {}'.format(ex))
            return None

    # FIXME: Create Dict[OutputType{Enum}, List[int]] output return to retrieve all identifier of output sent
    @staticmethod
    def real_provisioning_task(list_output_type: List[OutputMessageType],
                               list_message_conversions: List[MQTTPayloadConversion],
                               username: str = str(),
                               password: str = str()) -> bool:
        try:
            if not list_output_type or not list_message_conversions:
                return False

            for output_message_type in list_output_type:
                list_output_messages = Provisioning.get_list_messages(outmessagetype=output_message_type)

                if not list_output_messages:
                    logger.warning('Provisioning real_provisioning_task Did not find Message To Forward')
                    return False

                for message_conversion in list_message_conversions:
                    mqtt_connection_info = Provisioning.\
                        get_mqtt_connection_info(message_output_type=output_message_type,
                                                 mqtt_dictionary_conversion_type=message_conversion,
                                                 username=username,
                                                 password=password)

                    if not mqtt_connection_info:
                        continue

                    Provisioning.deliver_output_messages(list_output_messages=list_output_messages,
                                                         output_type=message_conversion,
                                                         mqtt_connection_info=mqtt_connection_info)

            return True
        except Exception as ex:
            logger.error("real_provisioning_task [Exception] {}".format(ex))
            return None
