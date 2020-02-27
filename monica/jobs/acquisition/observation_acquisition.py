from utility.utility_http_client import UtilityHTTPClient
import logging
from entities.datastream_topic_adapter import DatastreamTopicAdapter
from services.service_observation_acquisition import ServiceObservationAcquisition # FIXME: To be fused with this Unit
import json

logger = logging.getLogger('textlogger')


class ObservationAcquisition:
    @staticmethod
    def get_complete_url(gost_url: str, specific_datastream):
        complete_url_return = gost_url+'/'+specific_datastream.get_datastreams_suburl() + '?$expand=Observations($top=1)'
        return complete_url_return

    @staticmethod
    def get_lastobservation_specificdatastream(gost_url: str,
                                               specific_datastream: DatastreamTopicAdapter,
                                               username: str,
                                               password: str):
        try:
            httpget_response = UtilityHTTPClient.http_get_request(requesturl=ObservationAcquisition.get_complete_url(gost_url, specific_datastream),
                                                                  username=username,
                                                                  password=password
                                               )
            if not httpget_response:
                return None

            dictionary_json = json.loads(httpget_response)

            if 'Observations' not in dictionary_json:
                return None

            observation_list = dictionary_json['Observations']

            if not observation_list:
                return None

            return observation_list[0]

        except Exception as ex:
            return None

    @staticmethod
    def acquire_lasts_observations(gost_url: str,
                                   catalog_datastreams: dict,
                                   username: str,
                                   password: str,
                                   pilot_name: str):
        dictionary_observation = dict()
        try:

            for single_topic in catalog_datastreams:
                dictionary_observation[single_topic] = dict()
                list_datastreams_topic = catalog_datastreams[single_topic]

                for single_datastream in list_datastreams_topic:
                    if not single_datastream:
                        continue

                    single_observation_dict = ObservationAcquisition.get_lastobservation_specificdatastream(gost_url=gost_url,
                                                                                                            specific_datastream=single_datastream,
                                                                                                            username=username,
                                                                                                            password=password)

                    if not single_observation_dict:
                        continue

                    single_observation_object = ServiceObservationAcquisition.acquire_single_observation(json_observation=single_observation_dict,
                                                                                                         associated_topic=single_topic,
                                                                                                         pilot_name=pilot_name)

                    if not single_observation_object:
                        continue

                    dictionary_observation[single_topic][single_datastream.datastreamid] = single_observation_object

            return dictionary_observation

        except Exception as ex:
            logger.error('Exception: {}'.format(ex))
            return None
