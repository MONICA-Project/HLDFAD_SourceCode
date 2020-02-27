

import logging

from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from rest_framework import serializers
import io
import json

from jobs.models import CrowdHeatmapOutput
from jobs.serializers import CrowdHeatmapOutputSerializer

logger = logging.getLogger('textlogger')


class JSONProxySerializer(object):
    def __init__(self,serializer):
        self.serializer = serializer

    @classmethod
    def from_json(cls, json_data):
        deserializer = CrowdHeatmapOutputSerializer(data=json_data)

        if not deserializer.is_valid():
            return False

        return cls(CrowdHeatmapOutput(**deserializer.validated_data))

    def to_json(self):
        return UtilitySerializer.convert_serializer_to_json(self.serializer)


class UtilitySerializer:
    @staticmethod
    def convert_serializer_to_json(serializer: serializers.ModelSerializer):
        try:
            if not serializer.is_valid():
                logger.error('UtilitySerializer convert_serializer_to_json Failed is_valid, error: {}'
                             .format(serializer.error_messages))
                return None

            return serializer.validated_data

            # json_serialized_output = JSONRenderer().render(data=serializer.data)
            #
            # return json_serialized_output
            # stream = io.BytesIO(json_serialized_output)
            # json_conversion = JSONParser().parse(stream)

            #return json_conversion
        except Exception as ex:
            return None