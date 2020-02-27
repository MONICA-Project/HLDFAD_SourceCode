import json

from utility.utility_http_client import UtilityHTTPClient
from entities.things_adapter import ThingAdapter
from entities.datastream_topic_adapter import DatastreamTopicAdapter
from jobs.acquisition.observation_acquisition import ObservationAcquisition
from jobs.cache_redis import CacheRedisAdapter, CachedComponents
from utility.utility_catalog_cached import UtilityCatalogCached
from utility.utility_url_conversion import UtilityURLConversion

from shared.settings.appglobalconf import HEADER_JSON, LOCAL_CONFIG, SELECTED_PILOT, LocConfLbls, WEB_BASE_URL
from typing import Callable, Iterable, Union, Optional, List, Dict, Any
from entities.catalog_broker_info import CatalogBrokerOutput

import logging

logger = logging.getLogger('textlogger')


class ServiceCatalogClient:
    list_datastreams = list()
    global_catalog_dictionary = dict()
    list_datastreams_global = list()
    LABEL_COUNTER_TOTAL_DEVICE_REGISTERED = 'SERVICECATALOGCLIENT_COUNTERTOTALDEVICEREGISTERED'

    @staticmethod
    def initialize():
        CacheRedisAdapter.counter_create(label_info=ServiceCatalogClient.LABEL_COUNTER_TOTAL_DEVICE_REGISTERED,
                                         start_value=0)

    @staticmethod
    def increase_counter_totaldevices(incr_value: int):
        try:
            CacheRedisAdapter.counter_increase(label_info=ServiceCatalogClient.LABEL_COUNTER_TOTAL_DEVICE_REGISTERED,
                                               increase=incr_value)
        except Exception as ex:
            logger.error('ServiceCatalogClient increase_counter_totaldevices Exception: {}'.format(ex))

    @staticmethod
    def get_total_counterdevices() -> int:
        try:
            value_return = \
                CacheRedisAdapter.counter_get(label_info=ServiceCatalogClient.LABEL_COUNTER_TOTAL_DEVICE_REGISTERED)

            if not value_return:
                return 0

            return value_return

        except Exception as ex:
            logger.error('ServiceCatalogClient: Exception {}'.format(ex))
            return 0

    @staticmethod
    def set_datastream_list(list_datastreams: list):
        ServiceCatalogClient.list_datastreams = list_datastreams
    # @staticmethod
    # def extract_info_single_thing(single_thing):

    @staticmethod
    def check_device_inlist(sensor_adapter: DatastreamTopicAdapter,
                            list_datastreams_json: Dict[str, str]) -> DatastreamTopicAdapter:

        for key in list_datastreams_json.keys():
            device_label = list_datastreams_json[key]

            if not device_label:
                continue

            if sensor_adapter.is_sensor_matching(device_label):
                sensor_adapter.set_label(label=key)
                return sensor_adapter

        return sensor_adapter

    @staticmethod
    def get_datastreams_catalog_thing(thing_name: str,
                                      list_datastreams_json: dict,
                                      list_datastreams_thing,
                                      prefix_topic: str = '') -> List[DatastreamTopicAdapter]:
        list_devices_return = list()
        try:
            catalog_all_datastreams = list_datastreams_json['value']

            if not catalog_all_datastreams:
                return None

            for single_datastream in catalog_all_datastreams:
                datastream_adapter = DatastreamTopicAdapter(thing_name=thing_name,
                                                            prefix_topic=prefix_topic)

                if not datastream_adapter.set_properties_from_json(json_message=single_datastream):
                    del datastream_adapter
                    continue

                datastream_adapter = ServiceCatalogClient.check_device_inlist(sensor_adapter=datastream_adapter,
                                                                              list_datastreams_json=list_datastreams_thing)

                if datastream_adapter.get_matching():
                    list_devices_return.append(datastream_adapter)

                device_registration = datastream_adapter.get_device_registration()

                del datastream_adapter

                if not device_registration:
                    continue

                UtilityCatalogCached.add_device_registration(device_registration=device_registration)

            return list_devices_return

        except Exception as ex:
            logger.error('get_datastreams_catalog_thing Exception: {}'.format(ex))
            return list_devices_return

    @staticmethod
    def extract_nextpage(list_datastreams_json: dict):
        if '@iot.nextLink' not in list_datastreams_json:
            return None

        return list_datastreams_json['@iot.nextLink']

    @staticmethod
    def extract_list_datastreams_singlepage_thing(requesturl: str,
                                                  username: str,
                                                  password: str,
                                                  name_thing: str,
                                                  base_url: str,
                                                  list_datastreamsnames_thing: dict) \
            -> (List[DatastreamTopicAdapter], str):
        try:
            requesturl = UtilityURLConversion.replace_base_url(original_complete_url=requesturl,
                                                               base_url=base_url)

            logger.info('ServiceCatalogClient Connect to Catalog URL: {}'.format(str(requesturl)))

            list_datastreams_response = UtilityHTTPClient.http_get_request(
                                                                            requesturl=requesturl,
                                                                            username=username,
                                                                            password=password
                                                                          )

            if not list_datastreams_response:
                return None, None

            list_datastreams_json = json.loads(list_datastreams_response)

            prefix_topic = ""
            if LocConfLbls.LABEL_PREFIX_TOPIC in LOCAL_CONFIG:
                prefix_topic = LOCAL_CONFIG[LocConfLbls.LABEL_PREFIX_TOPIC]

            list_datastreams_associated = ServiceCatalogClient.get_datastreams_catalog_thing(thing_name=name_thing,
                                                                                             list_datastreams_json=list_datastreams_json,
                                                                                             list_datastreams_thing=list_datastreamsnames_thing,
                                                                                             prefix_topic=prefix_topic
                                                                                             )
            if not list_datastreams_associated:
                return None, None

            link_next_page = ServiceCatalogClient.extract_nextpage(list_datastreams_json)

            return list_datastreams_associated, link_next_page

        except Exception as ex:
            logger.error('ServiceCatalogClient extract_list_datastreams_singlepage_thing Exception: {}'.format(ex))
            return None, None

    @staticmethod
    def acquire_allupdatedobservations(catalog_datastream: dict):
        return ObservationAcquisition.acquire_lasts_observations(gost_url=LOCAL_CONFIG[LocConfLbls.LABEL_GOST_URL],
                                                                 catalog_datastreams=catalog_datastream,
                                                                 username=LOCAL_CONFIG[LocConfLbls.LABEL_CATALOG_USERNAME],
                                                                 password=LOCAL_CONFIG[LocConfLbls.LABEL_CATALOG_PASSWORD],
                                                                 pilot_name=SELECTED_PILOT)

    @staticmethod
    def check_totalcountdevice_changed() -> bool:
        try:
            logger.info('ServiceCatalogClient get_count_devices Total from URL: {}'
                        .format(LOCAL_CONFIG[LocConfLbls.LABEL_URL_GET_DEVICECOUNT]))

            catalog_response_globalstring = UtilityHTTPClient.http_get_request(requesturl=LOCAL_CONFIG[LocConfLbls.LABEL_URL_GET_DEVICECOUNT],
                                                                               username=LOCAL_CONFIG[LocConfLbls.LABEL_CATALOG_USERNAME],
                                                                               password=LOCAL_CONFIG[LocConfLbls.LABEL_CATALOG_PASSWORD]
                                                                               )
            if not catalog_response_globalstring:
                logger.info('ServiceCatalogClient get_count_devices Found Empty String')
                return False

            json_message_parsing = json.loads(catalog_response_globalstring)

            if '@iot.count' not in json_message_parsing:
                logger.error('ServiceCatalogClient unable to find @iot.count field!')
                return False

            total_counter_string = json_message_parsing['@iot.count']

            total_counter_value_temp = int(total_counter_string)

            previous_value_counter = ServiceCatalogClient.get_total_counterdevices()

            if previous_value_counter == total_counter_value_temp:
                logger.info('ServiceCatalogClient get_count_devices No update is present, total amount: {}'
                            .format(str(total_counter_value_temp)))
                return False

            logger.info('ServiceCatalogClient get_count_devices Update Value from {0} to {1}'
                        .format(str(previous_value_counter),
                                str(total_counter_value_temp)))

            ServiceCatalogClient.increase_counter_totaldevices(total_counter_value_temp-previous_value_counter)

            return True

        except Exception as ex:
            logger.error('ServiceCatalogClient get_count_device Exception: {}'.format(ex))
            return False

    # NOTE: Method to retrieve WP6 Catalog Info for output
    @staticmethod
    def acquire_output_broker_info(request_catalog_url: str,
                                   service_to_call: str,
                                   request_catalog_port: int,
                                   dictionary_message_sent: Dict[str, Any]) -> CatalogBrokerOutput:
        try:
            logger.info('ServiceCatalogClient Try Acquiring WP6 Catalog Info from url: {0}:{1}/{2}'.format(request_catalog_url,
                                                                                                           request_catalog_port,
                                                                                                           service_to_call))
            request_global_url = '{0}:{1}/{2}'.format(request_catalog_url,
                                                      request_catalog_port,
                                                      service_to_call)
            response_catalog_output = UtilityHTTPClient.http_post_request(requesturl=request_global_url,
                                                                          json_message_tosend=dictionary_message_sent)

            if not response_catalog_output:
                return None

            catalog_json = json.loads(response_catalog_output)

            if 'mqttServer' not in catalog_json or 'mqttTopic' not in catalog_json:
                return None

            catalog_broker_output = CatalogBrokerOutput(mqtt_completeurl=catalog_json['mqttServer'],
                                                        mqtt_topic=catalog_json['mqttTopic'])

            if not catalog_broker_output:
                return None

            logger.info('ServiceCatalogClient WP6 Catalog Output Info: {}'.format(catalog_broker_output.to_string()))

            return catalog_broker_output

        except Exception as ex:
            logger.error('acquire_output_broker_info Exception: {}'.format(ex))
            return None

    @staticmethod
    def get_service_catalog(dict_thing_datastreams: Dict[str, Dict[str, str]]) \
            -> (Dict[str, List[DatastreamTopicAdapter]], List[DatastreamTopicAdapter], bool):

        try:
            if not dict_thing_datastreams:
                logger.warning('ServiceCatalogClient get_service_catalog '
                               'Unable to proceed (MISSING dict_thing_datastreams)')
                return None, None, False

            logger.info('ServiceCatalogClient GET CATALOG EVENT RECEIVED')

            catalog_response_globalstring = UtilityHTTPClient.http_get_request(requesturl=LOCAL_CONFIG[LocConfLbls.LABEL_CATALOG_URL],
                                                                               username=LOCAL_CONFIG[LocConfLbls.LABEL_CATALOG_USERNAME],
                                                                               password=LOCAL_CONFIG[LocConfLbls.LABEL_CATALOG_PASSWORD]
                                                                               )

            if not catalog_response_globalstring:
                return ServiceCatalogClient.global_catalog_dictionary, \
                       ServiceCatalogClient.list_datastreams_global, \
                       False

            catalog_json = json.loads(catalog_response_globalstring)

            if not catalog_json:
                return ServiceCatalogClient.global_catalog_dictionary, \
                       ServiceCatalogClient.list_datastreams_global, \
                       False

            if 'value' not in catalog_json:
                return ServiceCatalogClient.global_catalog_dictionary, \
                       ServiceCatalogClient.list_datastreams_global, \
                       False

            catalog_all_things = catalog_json['value']
            counter_datastream = 0
            datastream_page_link = None

            for single_thing_json in catalog_all_things:
                thing_adapter = ThingAdapter(single_thing_json,
                                             pilot_name=SELECTED_PILOT)

                if thing_adapter.name_thing not in dict_thing_datastreams.keys():
                    del thing_adapter
                    continue

                complete_url = LOCAL_CONFIG[LocConfLbls.LABEL_CATALOG_URL]

                logger.info('ServiceCatalogClient Get Service URL: {}'.format(complete_url))

                thing_adapter.set_base_url(base_url=complete_url)

                list_datastreamsnames_thing = dict_thing_datastreams[thing_adapter.name_thing]

                if not list_datastreamsnames_thing:
                    return ServiceCatalogClient.global_catalog_dictionary, ServiceCatalogClient.list_datastreams_global

                for namedatastream in list_datastreamsnames_thing:
                    ServiceCatalogClient.global_catalog_dictionary[namedatastream] = list()

                flag_new_page_available = True
                datastream_page_link = thing_adapter.datastream_link
                datastream_page_link = UtilityURLConversion.replace_base_url(original_complete_url=datastream_page_link,
                                                                             base_url=WEB_BASE_URL)

                while flag_new_page_available:
                    list_datastreams, datastream_page_link = \
                        ServiceCatalogClient.extract_list_datastreams_singlepage_thing(
                            requesturl=datastream_page_link,
                            username=LOCAL_CONFIG[LocConfLbls.LABEL_CATALOG_USERNAME],
                            password=LOCAL_CONFIG[LocConfLbls.LABEL_CATALOG_PASSWORD],
                            name_thing=thing_adapter.name_thing,
                            list_datastreamsnames_thing=list_datastreamsnames_thing,
                            base_url=WEB_BASE_URL
                        )

                    if not list_datastreams:
                        flag_new_page_available = False
                        logger.info('ServiceCatalogClient Datastreams list_datastreams Empty')
                        continue

                    logger.info('ServiceCatalogClient Datastreams list_datastreams Get')
                    logger.info('ServiceCatalogClient DatastreamsXX list_datastreams Get, Lenght={}'
                                .format(len(list_datastreams)))

                    for datastream_adapter in list_datastreams:
                        if datastream_adapter.label_matching not in ServiceCatalogClient.global_catalog_dictionary:
                            continue

                        list_datastream_topic = \
                            ServiceCatalogClient.global_catalog_dictionary[datastream_adapter.label_matching]

                        list_datastream_topic.append(datastream_adapter)

                        logger.info('ServiceCatalogClient New DatastreamTopicAdapter: {0}'.format(datastream_adapter.topic_associated))

                        ServiceCatalogClient.list_datastreams_global.append(datastream_adapter)
                        ServiceCatalogClient.global_catalog_dictionary[datastream_adapter.label_matching] = \
                            list_datastream_topic

                    if not datastream_page_link:
                        flag_new_page_available = False
                        continue

                    logger.debug('ServiceCatalogClient New Page To Acquired: {}'.format(datastream_page_link))
            logger.info('ServiceCatalogClient Terminated Acquisition Phase'.format(datastream_page_link))

            if not ServiceCatalogClient.global_catalog_dictionary:
                logger.warning('ServiceCatalogClient global_catalog_dictionary is None!')
                return ServiceCatalogClient.global_catalog_dictionary, ServiceCatalogClient.list_datastreams_global, False

            for datastram_feature in ServiceCatalogClient.global_catalog_dictionary:
                list_datastream_local = ServiceCatalogClient.global_catalog_dictionary[datastram_feature]

                if list_datastream_local:
                    counter_datastream += len(list_datastream_local)

            logger.info("ServiceCatalogClient set_counter_datastreams_registered: {}".format(counter_datastream))
            return ServiceCatalogClient.global_catalog_dictionary, ServiceCatalogClient.list_datastreams_global, True
        except Exception as ex:
            logger.error('ServiceCatalogClient get_service_catalog Exception {}'.format(ex))
            return ServiceCatalogClient.global_catalog_dictionary, ServiceCatalogClient.list_datastreams_global, False
