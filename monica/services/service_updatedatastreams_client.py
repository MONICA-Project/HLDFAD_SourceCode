from paho.mqtt import client as mqtt
import json
from general_types.label_ogc import LabelObservationType
from entities.datastream_topic_adapter import DatastreamTopicAdapter
from services.service_observation_client import ServiceObservationClient
from shared.settings.appglobalconf import LOCAL_CONFIG, LIST_DEVICE_TO_EXCLUDE, LocConfLbls
from jobs.cache_redis import CacheRedisAdapter, CachedComponents
import logging

logger = logging.getLogger('textlogger')


class ServiceUpdateDatastreamsClient:
    list_topics = list()
    dictionary_datastreams = dict()
    client = None
    LABEL_FLAG_SUBSCRIBED = 'SERVICEUPDATEDATASTREAM_FLAGSUBSCRIBED'
    LABEL_FLAG_CONNECTED = 'SERVICEUPDATEDATASTREAM_FLAGCONNECTED'

    @staticmethod
    def initialize(client_id: str):
        ServiceUpdateDatastreamsClient.client = mqtt.Client(client_id=client_id,
                                                            clean_session=True)
        ServiceUpdateDatastreamsClient.client.on_connect = ServiceUpdateDatastreamsClient.on_connect
        ServiceUpdateDatastreamsClient.client.on_message = ServiceUpdateDatastreamsClient.on_message
        ServiceUpdateDatastreamsClient.client.on_subscribe = ServiceUpdateDatastreamsClient.on_subscribe
        ServiceUpdateDatastreamsClient.client.on_unsubscribe = ServiceUpdateDatastreamsClient.on_unsubscribe
        ServiceUpdateDatastreamsClient.client.on_log = ServiceUpdateDatastreamsClient.on_log
        ServiceUpdateDatastreamsClient.client.on_disconnect = ServiceUpdateDatastreamsClient.on_disconnect

        ServiceUpdateDatastreamsClient.set_flag_subscribed(0)
        ServiceUpdateDatastreamsClient.set_flag_connected(0)

        logger.info('ServiceUpdateDatastreamsClient Setup with ClientID: {}'.format(client_id))

    @staticmethod
    def get_flag_subscribed() -> int:
        value_return = CacheRedisAdapter.get_cached_info(label_info=ServiceUpdateDatastreamsClient.LABEL_FLAG_SUBSCRIBED,
                                                         type_data=int)
        return value_return

    @staticmethod
    def get_flag_connected() -> int:
        value_return = CacheRedisAdapter.get_cached_info(label_info=ServiceUpdateDatastreamsClient.LABEL_FLAG_CONNECTED,
                                                         type_data=int)
        return value_return

    @staticmethod
    def set_flag_subscribed(new_value: int):
        CacheRedisAdapter.set_cache_info(label_info=ServiceUpdateDatastreamsClient.LABEL_FLAG_SUBSCRIBED,
                                         data=new_value)

    @staticmethod
    def set_flag_connected(new_value: int):
        CacheRedisAdapter.set_cache_info(label_info=ServiceUpdateDatastreamsClient.LABEL_FLAG_CONNECTED,
                                         data=new_value)

    @staticmethod
    def check_subscribed() -> bool:
        flag_subscribed = ServiceUpdateDatastreamsClient.get_flag_subscribed()
        logger.info("ServiceUpdateDatastreamsClient Value flag_subscribed={0}"
                    .format(str(flag_subscribed)))

        if flag_subscribed == 0:
            return False

        return True

    @staticmethod
    def check_status_connection() -> bool:
        debug_print_flag_connected = ServiceUpdateDatastreamsClient.get_flag_connected()
        debug_print_flag_subscribed = ServiceUpdateDatastreamsClient.get_flag_subscribed()

        logger.info("ServiceUpdateDatastreamsClient check_status_connection flag_connected={0} flag_subscribed={1}"
                    .format(str(debug_print_flag_connected),
                            str(debug_print_flag_subscribed)))

        if debug_print_flag_connected == 1:
            if debug_print_flag_subscribed == 1:
                return True

        return False

    @staticmethod
    def start(mqtt_broker_url: str,
              mqtt_broker_port: int):
        try:
            ServiceUpdateDatastreamsClient.client.connect(host=mqtt_broker_url,
                                                          port=mqtt_broker_port)

            ServiceUpdateDatastreamsClient.client.loop_start()
            logger.info('ServiceUpdateDatastreamsClient start event. Connect To Broker: {0}:{1}'.format(mqtt_broker_url, mqtt_broker_port))
        except Exception as ex:
            logger.error('ServiceUpdateDatastreamsClient start Exception: {}'.format(ex))

    @staticmethod
    def on_unsubscribe(client, userdata, mid):
        try:
            logger.debug('ServiceUpdateDatastreamsClient on_unsubscribe event')
        except Exception as ex:
            logger.error('ServiceUpdateDatastreamsClient on_unsubscribe Exception: {}'.format(ex))

    @staticmethod
    def on_subscribe(client: mqtt.Client, userdata, mid, granted_qos):
        try:
            ServiceUpdateDatastreamsClient.set_flag_subscribed(1)

            if not granted_qos:
                return

            logger.info(
                'ServiceUpdateDatastreamsClient on_subscribe event raised, '
                'flag_subscribed={0}, TopicSubscribedNumber: {1}'
                    .format(str(ServiceUpdateDatastreamsClient.get_flag_subscribed()),
                            str(len(granted_qos)))
            )

        except Exception as ex:
            logger.error('ServiceUpdateDatastreamsClient onSubscribe Exception: {}'.format(ex))

    @staticmethod
    def on_disconnect(client: mqtt.Client, userdata, rc):
        try:
            logger.debug('ServiceUpdateDatastreamsClient MQTT Client Disconnected, retry connection (update)')
            # ServiceUpdateDatastreamsClient.start()
        except Exception as ex:
            logger.error('ServiceUpdateDatastreamsClient MQTT Client Disconnected Exception: {}'.format(ex))

    @staticmethod
    def on_log(client: mqtt.Client, userdata, level, buf):
        logger.debug('ServiceUpdateDatastreamsClient MQTT Log raised: {}'.format(buf))

    @staticmethod
    def on_connect(client: mqtt.Client, userdata, flags, rc):
        try:
            ServiceUpdateDatastreamsClient.set_flag_connected(1)
            ServiceUpdateDatastreamsClient.subscribe_topics()
            # self.client.subscribe('#')
            logger.info('ServiceUpdateDatastreamsClient on_connect, flag_connected={0}'
                        .format(str(ServiceUpdateDatastreamsClient.get_flag_connected())))
        except Exception as ex:
            logger.error('ServiceUpdateDatastreamsClient on_connect Exception: {}'.format(ex))

    @staticmethod
    def subscribe_topics():
        ServiceUpdateDatastreamsClient.client.subscribe(LOCAL_CONFIG[LocConfLbls.LABEL_UPDATE_DATASTREAM_LIST], qos=2)
        logger.info('ServiceUpdateDatastreamsClient Subscribed to Topic: {}'
                    .format(LOCAL_CONFIG[LocConfLbls.LABEL_UPDATE_DATASTREAM_LIST]))
        return True

    @staticmethod
    def convert_payload_to_json(message):
        try:
            content = message.decode('utf8')

            json_message = json.loads(content)

            return json_message
        except Exception as ex:
            logger.error('convert_payload_to_json Exception: {}'.format(ex))

    @staticmethod
    def create_datastream(json_message: dict) -> DatastreamTopicAdapter:
        try:
            if "observed_property" not in json_message:
                return None

            if "datastream_id" not in json_message:
                return None

            if json_message["observed_property"] != "Localization-Wristband":
                logger.info('ServiceUpdateDatastreamsClient Datastream Not Required, obs_prop: {0}, datastream_id: {1}'
                            .format(json_message["observed_property"], str(json_message["datastream_id"])))
                return None

            if "wristband_id" not in json_message:
                return None

            new_datastream = DatastreamTopicAdapter(json_message['wristband_id'], prefix_topic=LOCAL_CONFIG[LocConfLbls.LABEL_PREFIX_TOPIC])
            new_datastream.set_properties_from_text(name_complete=json_message['wristband_id'],
                                                    datastream_id=json_message['datastream_id'],
                                                    prefix_topic=LOCAL_CONFIG[LocConfLbls.LABEL_PREFIX_TOPIC],
                                                    description=json_message['observed_property'])

            new_datastream.label_matching = LabelObservationType.LABEL_OBSTYPE_LOCALIZATION

            if new_datastream.tagId in LIST_DEVICE_TO_EXCLUDE:
                logger.info('ServiceUpdateDatastreamsClient Datastrem excluded because it is in Black List: {}'
                            .format(new_datastream.tagId))
                return None

            return new_datastream

        except Exception as ex:
            logger.error('ServiceUpdateDatastreamsClient create_datastream Exception: {}'.format(ex))
            return None

    @staticmethod
    def on_message(client: mqtt.Client, userdata, message: mqtt.MQTTMessage):
        try:
            logger.debug('ServiceUpdateDatastreamsClient on_message arised, topic: {}'.format(message.topic))

            # {"wristband_id": "GeoTag12", "observed_property": "Localization-Wristband", "datastream_id": 4182}

            json_message = ServiceUpdateDatastreamsClient.convert_payload_to_json(message.payload)

            new_datastream = ServiceUpdateDatastreamsClient.create_datastream(json_message=json_message)

            if not new_datastream:
                logger.debug('ServiceUpdateDatastreamsClient Excluded Datastream')
                return

            logger.info('ServiceUpdateDatastreamsClient Request Subscribe new Topic')

            ServiceObservationClient.append_datastreamadapter(datastream_adapter=new_datastream,
                                                              flag_immediate_subscription=True)
        except Exception as ex:
            logger.error('ServiceUpdateDatastreamsClient on_message Exception: {}'.format(ex))
