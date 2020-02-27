import logging
import json
from entities.mqtt_connection_info import MQTTConnectionParams
from general_types.general_enums import MQTTPayloadConversion

logger = logging.getLogger('textlogger')


class CatalogBrokerOutput:
    def __init__(self, mqtt_completeurl: str, mqtt_topic: str):
        try:
            self.mqtt_hostname = mqtt_completeurl.split(sep=':')[0]
            self.mqtt_port = int(mqtt_completeurl.split(sep=':')[1])
            self.mqtt_topic = mqtt_topic
        except Exception as ex:
            logger.error('CatalogBrokerOutput Exception: {}'.format(ex))

    def to_json(self):
        return {'mqtt_hostname': self.mqtt_hostname,
                'mqtt_port': self.mqtt_port,
                'mqtt_topic': self.mqtt_topic}

    def to_string(self):
        return json.dumps(obj=self.to_json())

    def to_mqtt_connection_params(self,
                                  username: str = str(),
                                  password: str = str()) -> MQTTConnectionParams:
        mqtt_connection_params = MQTTConnectionParams(topic=self.mqtt_topic,
                                                      type_conversion=MQTTPayloadConversion.TYPE_CONVERSION_OGCDICTIONARY,
                                                      username=username,
                                                      password=password)
        mqtt_connection_params.m_url = self.mqtt_hostname
        mqtt_connection_params.m_tcpport = self.mqtt_port
        mqtt_connection_params.m_client_id = 'MONICA_HLDFAD'

        return mqtt_connection_params
