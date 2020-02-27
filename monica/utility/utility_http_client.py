import urllib.request
import urllib.response
from typing import Any, Dict
import json
import socket

import logging

logger = logging.getLogger('textlogger')


class UtilityHTTPClient:
    @staticmethod
    def check_server_active(ip: str, port: int) -> bool:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.connect((ip, int(port)))
            s.shutdown(2)
            return True
        except Exception as ex:
            logger.error('check_server_active Exception: {}'.format(ex))
            return False

    @staticmethod
    def get_authentication_opener(requesturl, username, password):
        try:
            password_mngr = urllib.request.HTTPPasswordMgrWithDefaultRealm()
            password_mngr.add_password(None, requesturl, username, password)
            handlerAuth = urllib.request.HTTPBasicAuthHandler(password_mngr)
            # create opener (OpenerDirector instance)
            opener = urllib.request.build_opener(handlerAuth)
            return opener
        except Exception as ex:
            logger.error('UtilityHTTPClient::get_authentication_opener Exception: {}'.format(ex))
            return None

    @staticmethod
    def http_post_request(requesturl: str,
                          json_message_tosend: Dict[str, Any],
                          username: str = str(),
                          password: str = str()) -> str:
        try:
            if username and password:
                http_opener = UtilityHTTPClient.get_authentication_opener(requesturl, username, password)

                if http_opener is None:
                    return str()

                urllib.request.install_opener(http_opener)

            message_to_send = bytearray(json.dumps(obj=json_message_tosend).encode(encoding='ascii'))

            headers = {"Content-type": "application/json"}

            catalog_request = urllib.request.Request(url=requesturl, data=message_to_send, headers=headers)
            catalog_response = urllib.request.urlopen(catalog_request)
            catalog_response_str = catalog_response.read().decode('utf8')

            return catalog_response_str
        except Exception as ex:
            logger.error('UtilityHTTPClient::http_post_request Exception: {}'.format(ex))
            return str()

    @staticmethod
    def http_get_request(requesturl: str,
                         username: str,
                         password: str):
        try:
            # requesturl = "http://130.192.85.204:8001/v1.0/Things(5)/Datastreams"
            if username and password:
                http_opener = UtilityHTTPClient.get_authentication_opener(requesturl,
                                                                          username,
                                                                          password)

                if http_opener is None:
                    return ''

                urllib.request.install_opener(http_opener)
            catalog_request = urllib.request.Request(requesturl)
            catalog_response = urllib.request.urlopen(catalog_request)
            catalog_response_str = catalog_response.read().decode('utf8')

            return catalog_response_str
        except Exception as ex:
            logger.error('UtilityHTTPClient::http_get_request Exception: {}'.format(ex))
