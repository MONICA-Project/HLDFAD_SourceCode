from typing import Dict, Any
from general_types.general_enums import MQTTPayloadConversion
from general_types.labelsdictionaries import MQTTLabelsConfigurations
import logging

logger = logging.getLogger('textlogger')


class MQTTConnectionParams(object):
    def __init__(self,
                 topic: str = str(),
                 url: str = str(),
                 port: int = 1883,
                 client_id: str = str(),
                 type_conversion: MQTTPayloadConversion = MQTTPayloadConversion.TYPE_CONVERSION_STANDARDDICTIONARY,
                 username: str = str(),
                 password: str = str()):
        self.m_url = url
        self.m_topic = topic
        self.m_username = username
        self.m_password = password
        self.m_client_id = client_id
        self.m_tcpport = port
        self.m_type_dictionary_conversion = type_conversion

    def from_dictionary(self, dictionary: Dict[str, Any]) -> bool:
        if not dictionary:
            return False

        for key in dictionary.keys():
            value = dictionary[key]

            if not value:
                continue

            if key == MQTTLabelsConfigurations.LABEL_DICTIONARY_URL:
                self.m_url = value
            elif key == MQTTLabelsConfigurations.LABEL_DICTIONARY_USERNAME:
                self.m_username = value
            elif key == MQTTLabelsConfigurations.LABEL_DICTIONARY_PASSWORD:
                self.m_password = value
            elif key == MQTTLabelsConfigurations.LABEL_DICTIONARY_CLIENT_ID:
                self.m_client_id = value

        return True

    def get_authentication_info(self) -> Dict[str, str]:
        if not self.m_username and not self.m_password:
            return None

        try:
            dictionary_auth = dict()

            if self.m_username:
                dictionary_auth['username'] = self.m_username

            if self.m_password:
                dictionary_auth['password'] = self.m_password

            return dictionary_auth
        except Exception as ex:
            logger.error('MQTTConnectionInfo get_authentication_info Exception: {}'.format(ex))
            return None

