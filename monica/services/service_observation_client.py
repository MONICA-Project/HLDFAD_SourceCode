from paho.mqtt import client as mqtt
import json
from general_types.virtual_classes import ObservableGeneric
from entities.datastream_topic_adapter import DatastreamTopicAdapter
from services.service_observation_acquisition import ServiceObservationAcquisition
from shared.settings.appglobalconf import LOCAL_CONFIG, LocConfLbls
from jobs.cache_redis import CacheRedisAdapter, CachedComponents
from shared.settings.appglobalconf import LIST_DEVICE_TO_EXCLUDE
from utility.utility_catalog_cached import UtilityCatalogCached

from typing import List  # , Any, Callable, Iterable, Union, Optional, List, Dict

import logging

logger = logging.getLogger('textlogger')


class ServiceObservationClient:
    """
    Static class that connect to MQTT Broker for retrieving Observables to be parsed and stored.
    It contains a Paho MQTT client that connect to MQTT Broker and perform subscription to list of topics
    """

    list_topics = list()
    dictionary_datastreams = dict()
    general_topic_filter = str()
    flag_set_generic_filter = False
    counter_msg_received = 0
    counter_number_topics = 0
    observable_id = 1
    running_id = 0
    client = None
    CONSTANT_DEBUG_NUMBER_MODNOTIFICATION = LOCAL_CONFIG[LocConfLbls.LABEL_OBSERVATION_DEBUG_INTERVALNUMBERNOTIFICATION]
    LABEL_FLAG_SUBSCRIBED = 'SERVICEOBSERVATION_FLAGSUBSCRIBED'
    LABEL_FLAG_CONNECTED = 'SERVICEOBSERVATION_FLAGCONNECTED'
    on_event_notify_obs = None

    @staticmethod
    def notify_new_observable(observable: ObservableGeneric):
        try:
            if not ServiceObservationClient.on_event_notify_obs:
                return

            logger.debug('ServiceObservationClient Notify Observation')

            ServiceObservationClient.on_event_notify_obs(observable)
        except Exception as ex:
            logger.error('ServiceObservationClient notify_new_observable{}'.format(ex))

    @staticmethod
    def initialize(client_id: str,
                   username: str = str(),
                   password: str = str()):
        try:
            ServiceObservationClient.client = \
                mqtt.Client(client_id=client_id,
                            clean_session=True)
            ServiceObservationClient.client.on_connect = ServiceObservationClient.on_connect
            ServiceObservationClient.client.on_message = ServiceObservationClient.on_message
            ServiceObservationClient.client.on_subscribe = ServiceObservationClient.on_subscribe
            ServiceObservationClient.client.on_unsubscribe = ServiceObservationClient.on_unsubscribe
            ServiceObservationClient.client.on_log = ServiceObservationClient.on_log
            ServiceObservationClient.client.on_disconnect = ServiceObservationClient.on_disconnect

            ServiceObservationClient.set_flag_subscribed(0)
            ServiceObservationClient.set_flag_connected(0)

            if username and password:
                logger.info('ServiceObservationClient initialize Set MQTT Username: {0}, Password: {1}'.format(username,
                                                                                                               password))
                ServiceObservationClient.client.username_pw_set(username=username,
                                                                password=password)

            logger.info('ServiceObservationClient Setup with ClientID: {}'.format(client_id))
        except Exception as ex:
            logger.error('ServiceObservationClient Setup Exception: {}'.format(ex))

    @staticmethod
    def set_running_id(running_id: int):
        ServiceObservationClient.running_id = running_id

    @staticmethod
    def convert_payload_to_json(message):
        try:
            content = message.decode('utf8')

            json_message = json.loads(content)

            return json_message
        except Exception as ex:
            logger.error('convert_payload_to_json Exception: {}'.format(ex))

    @staticmethod
    def get_mqtt_client() -> mqtt.Client:
        if not ServiceObservationClient.client:
            raise Exception('MQTT Client Not Instanced')
        return ServiceObservationClient.client

    @staticmethod
    def get_flag_subscribed() -> int:
        value_return = CacheRedisAdapter.get_cached_info(ServiceObservationClient.LABEL_FLAG_SUBSCRIBED,
                                                         type_data=int)
        return value_return

    @staticmethod
    def get_flag_connected() -> int:
        value_return = CacheRedisAdapter.get_cached_info(ServiceObservationClient.LABEL_FLAG_CONNECTED,
                                                         type_data=int)
        return value_return

    @staticmethod
    def set_flag_subscribed(new_value: int):
        CacheRedisAdapter.set_cache_info(label_info=ServiceObservationClient.LABEL_FLAG_SUBSCRIBED,
                                         data=new_value)

    @staticmethod
    def set_generic_topic_filter(general_topic_filter: str):
        ServiceObservationClient.general_topic_filter = general_topic_filter

    @staticmethod
    def set_flag_connected(new_value: int):
        CacheRedisAdapter.set_cache_info(label_info=ServiceObservationClient.LABEL_FLAG_CONNECTED,
                                         data=new_value)

    @staticmethod
    def check_subscribed() -> bool:
        flag_subscribed = ServiceObservationClient.get_flag_subscribed()
        logger.info("ServiceObservationClient Value flag_subscribed={0}"
                    .format(str(flag_subscribed)))

        if flag_subscribed == 0:
            return False

        return True

    @staticmethod
    def check_status_connection() -> bool:
        debug_print_flag_connected = ServiceObservationClient.get_flag_connected()
        debug_print_flag_subscribed = ServiceObservationClient.get_flag_subscribed()

        logger.info("ServiceObservationClient check_status_connection flag_connected={0} flag_subscribed={1}"
                    .format(str(debug_print_flag_connected),
                            str(debug_print_flag_subscribed)))

        if debug_print_flag_connected == 1:
            if debug_print_flag_subscribed == 1:
                return True

        return False

    @staticmethod
    def update_subscription():
        try:
            if ServiceObservationClient.get_flag_connected() == 0:
                logger.warning('ServiceObservationClient Unable to update Subscription (Client Not Connected)')
                return False

            return ServiceObservationClient.subscribe_topics()
        except Exception as ex:
            logger.error('ServiceObservationClient reset_subscription Exception: {}'.format(ex))
            return False

    @staticmethod
    def append_topic_list(topic: str, qos=0) -> bool:
        try:
            single_tuple = (topic, qos)

            ServiceObservationClient.list_topics.append(single_tuple)

            UtilityCatalogCached.append_topic(single_topic=topic)

            return True
        except Exception as ex:
            logger.error(ex)
            return False

    @staticmethod
    def get_topic_list() -> List[str]:
        try:
            """
            Retrieve list of Topics for subscription
            """

            list_return = list()

            list_topics = UtilityCatalogCached.get_list_topics()

            if not list_topics:
                return list_return

            for single_topic in list_topics:
                single_tuple = (single_topic, 0)
                list_return.append(single_tuple)

            return list_return
        except Exception as ex:
            logger.error('get_topic_list Exception: {}'.format(ex))
            return None

    @staticmethod
    def append_datastreamadapter(datastream_adapter: DatastreamTopicAdapter,
                                 flag_immediate_subscription: bool = False) -> bool:
        try:
            """Request Append datastream information append for topic translation subscription
            
            Method called to append information of datastream useful for following MQTT topics subscription
            
            Args:
                datastream_adapter (DatastreamTopicAdapter): it includes associated topic and relative metadata to specific datastream
                flag_immediate_subscription (bool): Flag if an immediate subscription is required (used for asynchronous dynamic topic subscription
                
            Returns:
                bool: Result of operation           
            
            """
            if not datastream_adapter:
                return False

            if datastream_adapter.topic_associated in ServiceObservationClient.dictionary_datastreams:
                return True

            if LIST_DEVICE_TO_EXCLUDE and (datastream_adapter.tagId in LIST_DEVICE_TO_EXCLUDE):
                logger.info('ServiceObservationClient Exclude Device From Topic List: {0}'.format(datastream_adapter.name_complete))
                return False

            single_tuple = (datastream_adapter.topic_associated, 0)

            if single_tuple in ServiceObservationClient.list_topics:
                return True

            ServiceObservationClient.append_topic_list(topic=datastream_adapter.topic_associated)

            ServiceObservationClient.dictionary_datastreams[datastream_adapter.topic_associated] = datastream_adapter

            CachedComponents.increase_counter_datastreams_registered(datastream_feature=datastream_adapter.label_matching,
                                                                     increase=1)

            if not flag_immediate_subscription:
                return True

            logger.info('ServiceObservationClient Immediate Topic Registration: {}'
                        .format(datastream_adapter.topic_associated))

            ServiceObservationClient.get_mqtt_client().subscribe((datastream_adapter.topic_associated, 0))

            return True
        except Exception as ex:
            logger.error('ServiceObservationClient append_datastreamadapter Exception: {}'.format(ex))
            return False

    @staticmethod
    def launch_observation_acquisition():
        try:
            logger.info('ServiceObservationClient Request Reapply MQTT Subscription')
            ServiceObservationClient.update_subscription()
        except Exception as ex:
            logger.error('ServiceCatalogClient launch_observation_acquisition Exception: {}'.format(ex))

    @staticmethod
    def create_list_mqtt_client(list_datastreams: List[DatastreamTopicAdapter]):
        try:
            for single_datastreams in list_datastreams:
                ServiceObservationClient.append_datastreamadapter(single_datastreams)

        except Exception as ex:
            logger.error('ServiceObservationClient launch_list_mqtt_client Exception: {}'.format(ex))

    @staticmethod
    def suspend():
        try:
            ServiceObservationClient.get_mqtt_client().disconnect()
            logger.info('ServiceObservationClient suspend request')
        except Exception as ex:
            logger.error('ServiceObservationClient suspend Exception: {}'.format(ex))

    @staticmethod
    def start(mqtt_broker_url: str, mqtt_broker_port: int):
        try:
            ServiceObservationClient.get_mqtt_client().connect(host=mqtt_broker_url,
                                                               port=mqtt_broker_port)

            ServiceObservationClient.get_mqtt_client().loop_start()
            logger.info('ServiceObservationClient start event. Connect to Broker: {0}:{1}'
                        .format(mqtt_broker_url, mqtt_broker_port))
        except Exception as ex:
            logger.error('ServiceObservationClient start Exception: {}'.format(ex))

    @staticmethod
    def on_unsubscribe(client, userdata, mid):
        try:
            logger.info('ServiceObservationClient on_unsubscribe event')
        except Exception as ex:
            logger.error('ServiceObservationClient on_unsubscribe Exception: {}'.format(ex))

    @staticmethod
    def on_subscribe(client: mqtt.Client, userdata, mid, granted_qos):
        try:
            ServiceObservationClient.set_flag_subscribed(1)
            CachedComponents.set_startupapplication_completed()

            if not granted_qos:
                logger.error('ServiceObservationClient on_subscribe event raised No Topics')
                return

            ServiceObservationClient.counter_number_topics = len(granted_qos)

            logger.info(
                'ServiceObservationClient on_subscribe event raised, flag_subscribed={0}, TopicSubscribedNumber: {1}'
                    .format(str(ServiceObservationClient.get_flag_subscribed()),
                            str(len(granted_qos)))
            )

        except Exception as ex:
            logger.error('ServiceObservationClient onSubscribe Exception: {}'.format(ex))

    @staticmethod
    def on_disconnect(client: mqtt.Client, userdata, rc):
        try:
            logger.debug('ServiceObservationClient MQTT Client Disconnected')
            # ServiceObservationClient.get_mqtt_client().reconnect()
            # ServiceObservationClient.start()
        except Exception as ex:
            logger.error('ServiceObservationClient MQTT Client Disconnected Exception: {}'.format(ex))

    @staticmethod
    def on_log(client: mqtt.Client, userdata, level, buf):
        logger.debug('ServiceObservationClient MQTT Log raised: {}'.format(buf))

    @staticmethod
    def on_connect(client: mqtt.Client, userdata, flags, rc):
        try:
            if ServiceObservationClient.get_flag_connected() == 1:
                return

            ServiceObservationClient.set_flag_connected(1)
            ServiceObservationClient.subscribe_topics()
            # self.client.subscribe('#')
            logger.info('ServiceObservationClient on_connect, flag_connected={0}'
                        .format(str(ServiceObservationClient.get_flag_connected())))
        except Exception as ex:
            logger.error('ServiceObservationClient on_connect Exception: {}'.format(ex))

    @staticmethod
    def on_message(client: mqtt.Client, userdata, message: mqtt.MQTTMessage):
        try:
            """
            This is the event that communicates presence of new incoming MQTT message. 
            
            Event Connected to Paho MQTT Client on_connect
            """

            if message.topic not in ServiceObservationClient.dictionary_datastreams:
                logger.info('ServiceObsClient on_message exclude message from topic: '
                            .format(message.topic))
                return

            json_message = ServiceObservationClient.convert_payload_to_json(message.payload)

            if not json_message:
                logger.error('ServiceObsClient No JSON Created, topic: {}'.format(message.topic))
                return

            datastream = ServiceObservationClient.dictionary_datastreams[message.topic]

            observable = \
                ServiceObservationAcquisition.acquire_single_observation(json_observation=json_message,
                                                                         associated_topic=datastream.label_matching,
                                                                         pilot_name=LOCAL_CONFIG[LocConfLbls.LABEL_PILOT_NAME],
                                                                         observable_id=ServiceObservationClient.observable_id,
                                                                         running_id=ServiceObservationClient.running_id
                                                                         )
            if not observable:
                logger.warning('ServiceObservationClient SKYPPED ELEMENT TOPIC DecodeError: {}'.format(message.topic))
                return

            observable.set_label_cache(label_cache=message.topic)

            if (ServiceObservationClient.counter_msg_received %
                ServiceObservationClient.CONSTANT_DEBUG_NUMBER_MODNOTIFICATION) == 0:

                logger.info('ServiceObsClient CountMsg[{0}]: {1}, currentTopic: {2}'
                            .format(str(ServiceObservationClient.CONSTANT_DEBUG_NUMBER_MODNOTIFICATION),
                                    str(ServiceObservationClient.counter_msg_received),
                                    message.topic))

            ServiceObservationClient.counter_msg_received += 1
            ServiceObservationClient.observable_id = ServiceObservationClient.observable_id + 1

            ServiceObservationAcquisition.validate_and_save_observation_cache(observable=observable,
                                                                              associated_topic=datastream.label_matching,
                                                                              interval_validity_secs=LOCAL_CONFIG[LocConfLbls.LABEL_INTERVAL_OBS_VALIDITY_SECS]
                                                                              )
            ServiceObservationClient.notify_new_observable(observable=observable)
        except Exception as ex:
            logger.error('ServiceObservationClient on_message Exception: {}'.format(ex))

    @staticmethod
    def subscribe_topics() -> bool:
        try:
            list_topics = ServiceObservationClient.get_topic_list()

            if not list_topics:

                if not ServiceObservationClient.general_topic_filter:
                    logger.error('ServiceObservationClient subscribe_topics called'
                                 'listTopics empty! (No General Filter Set)')
                    return False

                logger.warning('ServiceObservationClient subscribed topic called, '
                               'GeneralTopic Subsciption: {}'.format(ServiceObservationClient.general_topic_filter))

                ServiceObservationClient.get_mqtt_client().subscribe(topic=ServiceObservationClient.general_topic_filter,
                                                                     qos=0)
                ServiceObservationClient.flag_set_generic_filter = True

                return True

            ServiceObservationClient.client.subscribe(list_topics)

            logger.info('ServiceObservationClient subscribe_topics called, Topic Subscription Number: {}'
                        .format(str(len(list_topics))))
            return True
        except Exception as ex:
            logger.error('ServiceObservationClient subscribe_topics Exception: {}'.format(ex))
            return False
