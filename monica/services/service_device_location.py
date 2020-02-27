# import urllib.request
# import urllib.response
#
# from shared.settings.appglobalconf import HEADER_JSON, LOCAL_CONFIG


class ServiceDeviceLocation(object):
    def api_keys(self):
        pass
        # payload = { "email": LOCAL_CONFIG[LocConfLbls.LABEL_RUCKUS_EMAIL],
        # "password": LOCAL_CONFIG[LocConfLbls.LABEL_RUCKUS_PASSWORD] }
        # payload_encode = urllib.parse.urlencode(payload).encode('ascii')
        #
        # url_api_keys = "{0}/api_keys.json".format(LOCAL_CONFIG[LocConfLbls.LABEL_RUCKUS_URL])
        #
        # ruckus_request = urllib.request.Request(url=url_api_keys, data=payload_encode, headers=HEADER_JSON)
        # ruckus_response = urllib.request.urlopen(ruckus_request)
        # ruckus_response_str = ruckus_response.read().decode('utf8')

        #json.dumps(ruckus_response_str)

        #RESPONSE
        # {
        #     "api_key": "string",
        #     "role": "string"
        # }

        #return