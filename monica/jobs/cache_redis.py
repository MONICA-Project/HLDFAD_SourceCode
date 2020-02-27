import redis
import pickle
import json
import logging
import redis_lock
import datetime
from jobs.models import Localization
from typing import Any, Dict, List
from utility.utility_collections import UtilityList
from entities.catalog_broker_info import CatalogBrokerOutput
from general_types.modelsenums import OutputMessageType
from general_types.label_ogc import LabelObservationType

from shared.settings.appglobalconf import CACHE_REDIS_CONFIGURATION, LABELS_CACHE_REDIS

logger = logging.getLogger('textlogger')


class MyClass(object):
    def __init__(self):
        self.attr1 = 1
        self.attr2 = "stringa di prova"

    @classmethod
    def from_json(cls, json_data):
        return cls(json_data)
        # or something like:
        # instance = cls()
        # instance.attr1 = json_data['attr1']
        # ...

    def to_json(self):
        return json.dumps({
            'attr1': self.attr1,
            'attr2': self.attr2
        })


class CacheRecord:
    @staticmethod
    def string_to_number(byte_array_counter: bytearray) -> int:
        try:
            if not byte_array_counter:
                return 0

            string_converted = str(byte_array_counter, 'utf-8')

            return int(string_converted)
        except Exception as ex:
            logger.error('CacheRecord string_to_number Exception: {}'.format(ex))
            return 0

    @staticmethod
    def dumps(record: Any) -> bytearray:
        try:
            if record is None:
                return None
            if type(record) is str:
                return str(record).encode(encoding='utf-8')
            if type(record) is int:
                return int(record).to_bytes(length=4,
                                            byteorder='little')
            return pickle.dumps(obj=record)
        except Exception as ex:
            logger.info('CacheRecord Dump Exception: {}'.format(ex))
            return None

    @staticmethod
    def loads(byte_array: bytearray, type_object: Any) -> Any:
        try:
            if not byte_array:
                return None
            if type_object is str:
                return byte_array.decode(encoding='utf-8')
            if type_object is int:
                return int.from_bytes(bytes=byte_array,
                                      byteorder='little')
            return pickle.loads(byte_array)
        except Exception as ex:
            logger.info('CacheRecord Dump Exception: {}'.format(ex))
            return None

    @staticmethod
    def dumps_list(list_elements: list) -> List[bytearray]:
        try:
            if not list_elements:
                return None

            list_return = list()

            for elem in list_elements:
                byte_array = CacheRecord.dumps(elem)

                if not byte_array:
                    continue
                list_return.append(object=byte_array)

            return list_return
        except Exception as ex:
            logger.info('CacheRecord DumpList Exception: {}'.format(ex))
            return None

    @staticmethod
    def load_list(list_bytesarray: List[bytearray], type_elems: Any = object) -> list:
        try:
            if not list_bytesarray:
                return None

            list_return = list()

            for byte_array in list_bytesarray:
                elem = CacheRecord.loads(byte_array=byte_array, type_object=type_elems)

                if not elem:
                    continue
                list_return.append(object=elem)

            return list_return
        except Exception as ex:
            logger.info('CacheRecord load_list Exception: {}'.format(ex))
            return None

    @staticmethod
    def load_dictionary(dict_bytesarray: Dict[bytearray, bytearray], type_key: Any, type_value: Any) -> Dict[Any, Any]:
        try:
            if not dict_bytesarray:
                return None

            dict_return = dict()

            for key_bytes in dict_bytesarray:
                key = CacheRecord.loads(byte_array=key_bytes,
                                        type_object=type_key)

                if not key:
                    continue

                value_bytes = dict_bytesarray[key_bytes]

                value = CacheRecord.loads(byte_array=value_bytes,
                                          type_object=type_value)

                if not value:
                    continue

                dict_return[key] = value

            return dict_return
        except Exception as ex:
            logger.info('CacheRecord load_dictionary Exception: {}'.format(ex))
            return None


class CacheRedisAdapter:
    is_initialized = False
    client_cache = redis.Redis
    dictionary_locker = dict()

    @staticmethod
    def initialize():
        try:
            if CacheRedisAdapter.is_initialized:
                return True

            if "HOST" not in CACHE_REDIS_CONFIGURATION or "PORT" not in CACHE_REDIS_CONFIGURATION:
                return False

            host = CACHE_REDIS_CONFIGURATION["HOST"]
            port = CACHE_REDIS_CONFIGURATION["PORT"]

            CacheRedisAdapter.client_cache = redis.Redis(host=host, port=port)

            redis_lock.reset_all(redis_client=CacheRedisAdapter.client_cache)

            if not CacheRedisAdapter.client_cache:
                logger.error('CacheRedisAdapter Initialization Failed')
                return False

            CacheRedisAdapter.client_cache.config_resetstat()
            CacheRedisAdapter.client_cache.flushall()

            CacheRedisAdapter.is_initialized = True

            logger.info('CacheRedisAdapter Initialization Success')
            return True
        except Exception as ex:
            logger.error('CacheRedisAdapter Initialization Exception: {}'.format(ex))
            return False

    @staticmethod
    def release_locker(label_info: str,
                       locker: redis_lock.Lock) -> bool:
        try:
            if not locker:
                return False

            if label_info in CacheRedisAdapter.dictionary_locker \
                    and CacheRedisAdapter.dictionary_locker[label_info]:
                locker.release()
                logger.warning('CacheRedisAdapter recycle_locker Already Available')
                return False

            CacheRedisAdapter.dictionary_locker[label_info] = locker
            locker.release()

            return True
        except Exception as ex:
            logger.error('CacheRedisAdapter recycle_locker Exception: {}'.format(ex))
            return None

    @staticmethod
    def acquire_locker(label_info: str) -> redis_lock.Lock:
        try:
            if label_info not in CacheRedisAdapter.dictionary_locker \
                    or not CacheRedisAdapter.dictionary_locker[label_info]:

                lock = redis_lock.Lock(redis_client=CacheRedisAdapter.client_cache, name=str(label_info))
                CacheRedisAdapter.dictionary_locker[label_info] = lock

            locker_return = CacheRedisAdapter.dictionary_locker.pop(label_info)

            if not locker_return:
                logger.error('CacheRedisAdapter acquire_locker gives None Locker! Exit')
                return None

            locker_return.acquire()
            return locker_return
        except Exception as ex:
            logger.error('CacheRedisAdapter GetLocker Exception: {}'.format(ex))
            return None

    @staticmethod
    def remove_cache_info(label_info: str):
        try:
            if not CacheRedisAdapter.is_initialized:
                return False

            CacheRedisAdapter.client_cache.delete(label_info)

            return True
        except Exception as ex:
            logger.error('CacheRedisAdapter RemoveCachedInfo Exception: {}'.format(ex))
            return False

    @staticmethod
    def set_cache_info(label_info: str, data: Any) -> bool:
        try:
            if not CacheRedisAdapter.is_initialized:
                return False

            value_to_set = CacheRecord.dumps(record=data)

            if value_to_set is None:
                logger.info('CacheRedisAdapter set_cache_info Failed (Wrong Dump Operation), label: {}'
                            .format(label_info))
                return False

            lock = CacheRedisAdapter.acquire_locker(label_info=label_info)
            return_flag = CacheRedisAdapter.client_cache.set(name=label_info,
                                                             value=value_to_set)
            CacheRedisAdapter.release_locker(label_info=label_info, locker=lock)

            return return_flag
        except Exception as ex:
            logger.error('CacheRedisAdapter set_cache_info Label={0}, Exception: {1}'.format(label_info, ex))
            return False

    @staticmethod
    def get_cached_info(label_info: str, type_data: Any) -> Any:
        if not CacheRedisAdapter.is_initialized:
            return None
        try:
            if not CacheRedisAdapter.client_cache.exists(label_info):
                return None

            lock = CacheRedisAdapter.acquire_locker(label_info=label_info)
            return_value = CacheRedisAdapter.client_cache.get(name=label_info)
            CacheRedisAdapter.release_locker(label_info=label_info, locker=lock)

            return CacheRecord.loads(byte_array=return_value, type_object=type_data)
        except Exception as ex:
            logger.error('CacheRedisAdapter get_cached_info Label={0}, Exception: {1}'.format(label_info, ex))
            return None

    @staticmethod
    def list_append_singleelement(label_info: str, elem_to_append: Any) -> bool:
        try:
            if not CacheRedisAdapter.is_initialized:
                return False

            if not elem_to_append:
                return False

            value_to_append = CacheRecord.dumps(record=elem_to_append)

            lock = CacheRedisAdapter.acquire_locker(label_info=label_info)

            if not CacheRedisAdapter.client_cache.exists(label_info):
                result = CacheRedisAdapter.client_cache.rpush(label_info,
                                                              value_to_append)
            else:
                result = CacheRedisAdapter.client_cache.rpushx(name=label_info,
                                                               value=value_to_append)

            CacheRedisAdapter.release_locker(label_info=label_info, locker=lock)

            if result <= 0:
                return False

            return True
        except Exception as ex:
            logger.error('CacheRedisAdapter list_append_singleelement Label={0}, Exception: {1}'.format(label_info, ex))
            return False

    @staticmethod
    def list_create(label_info: str, list_startup: list = None):
        try:
            if not CacheRedisAdapter.is_initialized:
                return False

            if not list_startup:
                return True

            list_to_set = CacheRecord.dumps_list(list_elements=list_startup)

            if not list_to_set:
                logger.error('CacheRedisAdapter list_append Label={0} Failed (Dump Error)'.format(label_info))
                return False

            lock = CacheRedisAdapter.acquire_locker(label_info=label_info)

            result = CacheRedisAdapter.client_cache.rpush(name=label_info,
                                                 *list_to_set)
            CacheRedisAdapter.release_locker(label_info=label_info, locker=lock)

            if result <=0 :
                return False

            return True
        except Exception as ex:
            logger.error('CacheRedisAdapter list_append Label={0}, Exception: {1}'.format(label_info, ex))
            return False

    @staticmethod
    def list_getcounterelements(label_info: str) -> int:
        try:
            if not CacheRedisAdapter.is_initialized:
                return -1

            if not CacheRedisAdapter.client_cache.exists(label_info):
                return 0

            lock = CacheRedisAdapter.acquire_locker(label_info=label_info)

            counter_elements = CacheRedisAdapter.client_cache.llen(name=label_info)

            CacheRedisAdapter.release_locker(label_info=label_info, locker=lock)

            if not counter_elements:
                return 0

            return counter_elements
        except Exception as ex:
            logger.error('CacheRedisAdapter list_getcounterelements Label={0}, Exception: {1}'.format(label_info, ex))
            return 0

    @staticmethod
    def list_extractlastelement(label_info: str, type_element: Any) -> Any:
        try:
            if not CacheRedisAdapter.is_initialized:
                return None

            if not CacheRedisAdapter.client_cache.exists(label_info):
                return None

            lock = CacheRedisAdapter.acquire_locker(label_info=label_info)

            elem_return = CacheRedisAdapter.client_cache.rpop(name=label_info)

            CacheRedisAdapter.release_locker(label_info=label_info, locker=lock)

            if not elem_return:
                return None

            return CacheRecord.loads(byte_array=elem_return,
                                     type_object=type_element)

        except Exception as ex:
            logger.error('CacheRedisAdapter list_extractlastelement Label={0}, Exception: {1}'.format(label_info, ex))
            return None

    @staticmethod
    def list_extractallelements(label_info: str, type_element: Any) -> List[Any]:
        try:
            if not CacheRedisAdapter.is_initialized:
                return None

            if not CacheRedisAdapter.client_cache.exists(label_info):
                return None

            list_elements_raw = list()

            while CacheRedisAdapter.list_getcounterelements(label_info=label_info) > 0:
                lock = CacheRedisAdapter.acquire_locker(label_info=label_info)

                elem_return = CacheRedisAdapter.client_cache.lpop(name=label_info)

                CacheRedisAdapter.release_locker(label_info=label_info, locker=lock)

                if not elem_return:
                    break

                list_elements_raw.append(elem_return)

            if not list_elements_raw:
                return None

            list_elems_return = list()

            for raw_elem in list_elements_raw:
                elem = CacheRecord.loads(byte_array=raw_elem,
                                         type_object=type_element)

                if not elem:
                    continue

                list_elems_return.append(elem)

            list_elements_raw.clear()

            return list_elems_return
        except Exception as ex:
            logger.error('CacheRedisAdapter list_extractlastelement Label={0}, Exception: {1}'.format(label_info, ex))
            return None

    @staticmethod
    def list_extractfirstelement(label_info: str, type_element: Any) -> Any:
        try:
            if not CacheRedisAdapter.is_initialized:
                return None

            if not CacheRedisAdapter.client_cache.exists(label_info):
                return None

            lock = CacheRedisAdapter.acquire_locker(label_info=label_info)

            elem_return = CacheRedisAdapter.client_cache.lpop(name=label_info)

            CacheRedisAdapter.release_locker(label_info=label_info, locker=lock)

            return CacheRecord.loads(byte_array=elem_return,
                                     type_object=type_element)

        except Exception as ex:
            logger.error('CacheRedisAdapter list_extractlastelement Label={0}, Exception: {1}'.format(label_info, ex))
            return None

    @staticmethod
    def counter_get(label_info: str) -> int:
        try:
            if not CacheRedisAdapter.is_initialized:
                return False

            lock = CacheRedisAdapter.acquire_locker(label_info=label_info)

            if not CacheRedisAdapter.client_cache.exists(label_info):
                CacheRedisAdapter.release_locker(label_info=label_info, locker=lock)
                return 0

            byte_array_counter = CacheRedisAdapter.client_cache.get(name=label_info)

            CacheRedisAdapter.release_locker(label_info=label_info, locker=lock)

            return CacheRecord.string_to_number(byte_array_counter=byte_array_counter)
        except Exception as ex:
            logger.error('CacheRedisAdapter counter_get Label={0}, Exception: {1}'.format(label_info, ex))
            return False

    @staticmethod
    def counter_create(label_info: str, start_value: int = 0) -> bool:
        try:
            if not CacheRedisAdapter.is_initialized:
                return False

            lock = CacheRedisAdapter.acquire_locker(label_info=label_info)

            if CacheRedisAdapter.client_cache.exists(label_info):
                CacheRedisAdapter.client_cache.delete(label_info)

            CacheRedisAdapter.client_cache.incr(name=label_info,
                                                amount=start_value)
            CacheRedisAdapter.release_locker(label_info=label_info, locker=lock)
            return True
        except Exception as ex:
            logger.error('CacheRedisAdapter counter_create Label={0}, Exception: {1}'.format(label_info, ex))
            return False

    @staticmethod
    def counter_increase(label_info: str, increase: int = 1) -> bool:
        try:
            if not CacheRedisAdapter.is_initialized:
                return False

            if not CacheRedisAdapter.client_cache.exists(label_info):
                return False

            lock = CacheRedisAdapter.acquire_locker(label_info=label_info)

            CacheRedisAdapter.client_cache.incr(name=label_info,
                                                amount=increase)

            CacheRedisAdapter.release_locker(label_info=label_info, locker=lock)
            return True
        except Exception as ex:
            logger.error('CacheRedisAdapter counter_increase Label={0}, Exception: {1}'.format(label_info, ex))
            return False

    @staticmethod
    def counter_decrease(label_info: str, decrease: int = 1) -> bool:
        try:
            if not CacheRedisAdapter.is_initialized:
                return False

            if not CacheRedisAdapter.client_cache.exists(label_info):
                return False

            lock = CacheRedisAdapter.acquire_locker(label_info=label_info)

            CacheRedisAdapter.client_cache.decr(name=label_info,
                                                amount=decrease)
            CacheRedisAdapter.release_locker(label_info=label_info, locker=lock)

            return True
        except Exception as ex:
            logger.error('CacheRedisAdapter counter_decrease Label={0}, Exception: {1}'.format(label_info, ex))
            return False

    @staticmethod
    def dictionary_create(label_info: str, dict_startup: dict = dict()) -> Any:
        try:
            if not CacheRedisAdapter.is_initialized:
                return False

            # if label_info not in CacheRedisAdapter.list_dictionaries:
            #     CacheRedisAdapter.list_dictionaries.append(label_info)

            return True
        except Exception as ex:
            logger.error('CacheRedisAdapter dictionary_get_value Label={0}, Exception: {1}'.format(label_info, ex))
            return None

    @staticmethod
    def dictionary_get_value(label_info: str, key: str, type_value: Any) -> Any:
        try:
            if not CacheRedisAdapter.is_initialized:
                return None

            if not CacheRedisAdapter.client_cache.exists(label_info):
                return None

            if not CacheRedisAdapter.client_cache.hexists(name=label_info,
                                                          key=key):
                return None

            lock = CacheRedisAdapter.acquire_locker(label_info=label_info)
            byte_array = CacheRedisAdapter.client_cache.hget(name=label_info,
                                                             key=key)
            CacheRedisAdapter.release_locker(label_info=label_info, locker=lock)

            if not byte_array:
                return None

            return CacheRecord.loads(byte_array=byte_array, type_object=type_value)
        except Exception as ex:
            logger.error('CacheRedisAdapter dictionary_get_value Label={0}, Exception: {1}'.format(label_info, ex))
            return None

    @staticmethod
    def dictionary_remove_value(label_info: str, key: str) -> bool:
        try:
            if not CacheRedisAdapter.is_initialized:
                return False

            if not CacheRedisAdapter.client_cache.exists(label_info):
                return False

            lock = CacheRedisAdapter.acquire_locker(label_info=label_info)
            CacheRedisAdapter.client_cache.hdel(label_info, key)
            CacheRedisAdapter.release_locker(label_info=label_info, locker=lock)
            return True
        except Exception as ex:
            logger.error('CacheRedisAdapter dictionary_remove_value Label={0}, Exception: {1}'.format(label_info, ex))
            return False

    @staticmethod
    def dictionary_get_all(label_info: str, type_value: Any) -> Dict[str, Any]:
        try:
            if not CacheRedisAdapter.is_initialized:
                return None

            if not CacheRedisAdapter.client_cache.exists(label_info):
                return None

            lock = CacheRedisAdapter.acquire_locker(label_info=label_info)
            return_value = CacheRedisAdapter.client_cache.hgetall(name=label_info)
            CacheRedisAdapter.release_locker(label_info=label_info, locker=lock)

            if not return_value:
                return None

            return CacheRecord.load_dictionary(dict_bytesarray=return_value,
                                               type_key=str,
                                               type_value=type_value)
        except Exception as ex:
            logger.error('CacheRedisAdapter dictionary_get_all Label={0}, Exception: {1}'.format(label_info, ex))
            return None

    @staticmethod
    def dictionary_update_value(label_info: str, key: str, value: Any) -> bool:
        try:
            if not CacheRedisAdapter.is_initialized:
                return False

            if value is None:
                return False

            lock = CacheRedisAdapter.acquire_locker(label_info=label_info)
            CacheRedisAdapter.client_cache.hset(name=label_info,
                                                key=key,
                                                value=CacheRecord.dumps(record=value))
            CacheRedisAdapter.release_locker(label_info=label_info, locker=lock)
            return True
        except Exception as ex:
            logger.error('CacheRedisAdapter dictionary_update_value Label={0}, Exception: {1}'.format(label_info, ex))
            return False


class CachedComponents:

    cache_redis_adapter = None
    LABEL_PREFIX_COUNTER = 'MONICAHASH_COUNTER_CACHED_'
    LABEL_PREFIX_TIMESTAMP_OBSERVABLE = 'MONICAHASH_TIMESTAMP_OBSERVABLE_DATASTREAM'
    LABEL_PREFIX_ID_OBSERVABLE='MONICAHASH_ID_OBSERVABLE_DATASTREAM'
    LABEL_SW_RUNNING = 'SW_RUNNING_IDENTIFIER'
    LABEL_DICTIONARY_TIMESTAMP_OBSERVABLE = 'DICTIONARY_TIMESTAMP_OBSERVABLES'
    LABEL_DICTIONARY_MAXIOTID_OBSTYPE = 'DICTIONARY_MAXIOTID_OBSTYPE'
    LABEL_STARTUP_COMPLETED = 'STARTUP_APPLICATION_COMPLETED'
    LABEL_BROKER_OUTPUT_CATALOG = 'WP6_BROKEROUTPUT_SERVICECATALOG'
    LABEL_QUEUEDETECTIONALERT_CATALOG = "QUEUEDETECTIONALERT_CATALOG"
    LABEL_COUNTER_OBSERVABLE_LOCALIZATION_UNPROCESSED = "COUNTER_OBSERVABLE_LOCALIZATION_UNPROCESSED"
    LABEL_COUNTER_OBSERVABLES_TOTAL = "COUNTER_OBSERVABLES_TOTAL"

    VALUE_STARTUP_NOTCOMPLETED = 1
    VALUE_STARTUP_COMPLETED = 2

    @staticmethod
    def get_label_observable_id(topic_id: str):
        return CachedComponents.LABEL_PREFIX_ID_OBSERVABLE + topic_id

    @staticmethod
    def get_dictionary_observable_timestamps() -> Dict[str, datetime.datetime]:
        try:
            dictionary_return = \
                CacheRedisAdapter.get_cached_info(label_info=CachedComponents.LABEL_DICTIONARY_TIMESTAMP_OBSERVABLE,
                                                  type_data=dict)

            if not dictionary_return:
                return dict()

            return dictionary_return

        except Exception as ex:
            logger.error('CachedComponent get_dictionary_observable_timestamp Exception: {}'.format(ex))
            return dict()

    @staticmethod
    def update_dictionary_observable_timestamps(dictionary_obs_timestamp: Dict[str, datetime.datetime]) -> bool:
        try:
            if not dictionary_obs_timestamp:
                return False

            return CacheRedisAdapter.set_cache_info(label_info=CachedComponents.LABEL_DICTIONARY_TIMESTAMP_OBSERVABLE,
                                                    data=dictionary_obs_timestamp)
        except Exception as ex:
            logger.error('CachedComponent get_dictionary_observable_timestamp Exception: {}'.format(ex))
            return False

    @staticmethod
    def get_lastid_observable(topic_id: str) -> int:
        try:
            label_obs_id = CachedComponents.get_label_observable_id(topic_id)

            return CacheRedisAdapter.get_cached_info(label_info=label_obs_id,
                                                     type_data=int)
        except Exception as ex:
            logger.error('get_lastid_observable Exception: {}'.format(ex))
            return None

    @staticmethod
    def set_lastid_observable(topic_id: str, obs_id: int) -> bool:
        try:
            label_obs_lastid = CachedComponents.get_label_observable_id(topic_id)

            return CacheRedisAdapter.set_cache_info(label_info=label_obs_lastid,
                                                    data=obs_id)

            return True
        except Exception as ex:
            logger.error('set_lastid_observable Exception: {}'.format(ex))
            return False

    @staticmethod
    def get_label_observable_timestamp(observable_id: str):
        return CachedComponents.LABEL_PREFIX_TIMESTAMP_OBSERVABLE + observable_id

    @staticmethod
    def set_sw_running_current_id(identifier: int) -> bool:
        return CacheRedisAdapter.set_cache_info(label_info=CachedComponents.LABEL_SW_RUNNING,
                                                data=identifier)

    @staticmethod
    def get_sw_running_current_id() -> int:
        return CacheRedisAdapter.get_cached_info(label_info=CachedComponents.LABEL_SW_RUNNING,
                                                 type_data=int)

    @staticmethod
    def save_brokeroutput_servicecatalog(broker_output: CatalogBrokerOutput,
                                         output_message_type: OutputMessageType):
        return CacheRedisAdapter.dictionary_update_value(label_info=CachedComponents.LABEL_BROKER_OUTPUT_CATALOG,
                                                         key=output_message_type.name,
                                                         value=broker_output)

    @staticmethod
    def get_brokeroutput_servicecatalog(output_message_type: OutputMessageType) -> CatalogBrokerOutput:
        try:
            return CacheRedisAdapter.dictionary_get_value(
                label_info=CachedComponents.LABEL_BROKER_OUTPUT_CATALOG,
                key=output_message_type.name,
                type_value=CatalogBrokerOutput
            )
        except Exception as ex:
            logger.error('get_brokeroutput_servicecatalog Exception: {}'.format(ex))
            return None

    @staticmethod
    def get_label_counter(main_label: str):
        return CachedComponents.LABEL_PREFIX_COUNTER + main_label

    @staticmethod
    def get_counter_datastreams_registered(datastream_feature: str) -> int:
        try:
            return_value = CacheRedisAdapter.counter_get(
                label_info=CachedComponents.get_label_counter(main_label=datastream_feature))

            if not return_value:
                return 0

            return return_value
        except Exception as ex:
            logger.error(ex)
            return 0

    @staticmethod
    def set_counter_observable(value: int = 0):
        try:
            CacheRedisAdapter.counter_create(
                                                label_info=CachedComponents.LABEL_COUNTER_OBSERVABLES_TOTAL,
                                                start_value=value)
            return True
        except Exception as ex:
            logger.error('set_counter_observable Exception: {}'.format(ex))
            return False

    @staticmethod
    def increase_counter_observable(increase: int = 1):
        try:
            CacheRedisAdapter.counter_increase(
                                                label_info=CachedComponents.LABEL_COUNTER_OBSERVABLES_TOTAL,
                                                increase=increase)
            return True
        except Exception as ex:
            logger.error('increase_counter_observable Exception: {}'.format(ex))
            return False

    @staticmethod
    def get_counter_observable():
        try:
            return CacheRedisAdapter.counter_get(label_info=CachedComponents.LABEL_COUNTER_OBSERVABLES_TOTAL)
        except Exception as ex:
            logger.error('get_counter_observable Exception: {}'.format(ex))
            return False

    @staticmethod
    def set_counter_observable_localization_unprocessed(value: int = 0):
        try:
            CacheRedisAdapter.counter_create(
                                                label_info=CachedComponents.LABEL_COUNTER_OBSERVABLE_LOCALIZATION_UNPROCESSED,
                                                start_value=value)
            return True
        except Exception as ex:
            logger.error('set_counter_observable_localization_unprocessed Exception: {}'.format(ex))
            return False

    @staticmethod
    def get_counter_observable_localization_unprocessed() -> int:
        try:
            return CacheRedisAdapter.counter_get(label_info=CachedComponents.LABEL_COUNTER_OBSERVABLE_LOCALIZATION_UNPROCESSED)
        except Exception as ex:
            logger.error('get_counter_observable_localization_unprocessed Exception: {}'.format(ex))
            return False

    @staticmethod
    def increase_counter_observable_localization_unprocessed(increase: int = 1):
        try:
            CacheRedisAdapter.counter_increase(label_info=CachedComponents.LABEL_COUNTER_OBSERVABLE_LOCALIZATION_UNPROCESSED,
                                               increase=increase)
            return True
        except Exception as ex:
            logger.error('increase_counter_observable_localization_unprocessed Exception: {}'.format(ex))
            return False

    @staticmethod
    def set_counter_datastreams_registered(datastream_feature: str, value: int) -> bool:
        try:
            CacheRedisAdapter.counter_create(
                                                label_info=CachedComponents.get_label_counter(main_label=datastream_feature),
                                                start_value=value)
            return True
        except Exception as ex:
            logger.error('set_counter_datastreams_registered Exception: {}'.format(ex))
            return False

    @staticmethod
    def increase_counter_datastreams_registered(datastream_feature: str, increase: int = 1) -> bool:
        try:
            return CacheRedisAdapter.counter_increase(
                label_info=CachedComponents.get_label_counter(main_label=datastream_feature),
                increase=increase)
        except Exception as ex:
            logger.error("CachedComponent increase_counter_datastreams_registered Exception: {}".format(ex))
            return False

    @staticmethod
    def get_maxiotid(observable_type: str) -> int:
        try:
            elem_read = CacheRedisAdapter.dictionary_get_value(
                label_info=CachedComponents.LABEL_DICTIONARY_MAXIOTID_OBSTYPE,
                key=observable_type,
                type_value=int)

            if elem_read is None:
                return 0

            return elem_read
        except Exception as ex:
            logger.error('CachedComponent checkandset_maxiotid Exception: {}'.format(ex))
            return False

    @staticmethod
    def checkandset_maxiotid(observable_type: str,
                             iot_id: int) -> bool:
        try:
            elem_read = CacheRedisAdapter.dictionary_get_value(
                label_info=CachedComponents.LABEL_DICTIONARY_MAXIOTID_OBSTYPE,
                key=observable_type,
                type_value=int)

            if elem_read is not None and elem_read >= iot_id:
                return False
            CacheRedisAdapter.dictionary_update_value(
                label_info=CachedComponents.LABEL_DICTIONARY_MAXIOTID_OBSTYPE,
                key=observable_type,
                value=iot_id)
            return True
        except Exception as ex:
            logger.error('CachedComponent checkandset_maxiotid Exception: {}'.format(ex))
            return False

    @staticmethod
    def startup():
        if CachedComponents.cache_redis_adapter:
            return True

        CachedComponents.cache_redis_adapter = CacheRedisAdapter()
        CacheRedisAdapter.initialize()

        CacheRedisAdapter.counter_create(LABELS_CACHE_REDIS.LABEL_CACHE_CROWDHEATMAPCOUNTER)
        CacheRedisAdapter.counter_create(LABELS_CACHE_REDIS.LABEL_CACHE_QUEUEDETECTIONALERT)
        CacheRedisAdapter.dictionary_create(label_info=CachedComponents.LABEL_DICTIONARY_MAXIOTID_OBSTYPE)
        CacheRedisAdapter.dictionary_create(label_info=CachedComponents.LABEL_BROKER_OUTPUT_CATALOG)

        CacheRedisAdapter.set_cache_info(label_info=CachedComponents.LABEL_STARTUP_COMPLETED,
                                         data=CachedComponents.VALUE_STARTUP_NOTCOMPLETED)

        CacheRedisAdapter.list_create(label_info=CachedComponents.LABEL_QUEUEDETECTIONALERT_CATALOG)

        CachedComponents.set_counter_datastreams_registered(datastream_feature=LabelObservationType.LABEL_OBSTYPE_LOCALIZATION,
                                                            value=0)
        CachedComponents.set_counter_datastreams_registered(datastream_feature=LabelObservationType.LABEL_OBSTYPE_CROWDDENSITY,
                                                            value=0)
        return True

    @staticmethod
    def set_startupapplication_completed() -> bool:
        try:
            logger.info('CACHEDComponent Receive Confirmation Startup Completed')
            return CacheRedisAdapter.set_cache_info(label_info=CachedComponents.LABEL_STARTUP_COMPLETED,
                                                    data=CachedComponents.VALUE_STARTUP_COMPLETED)
        except Exception as ex:
            logger.error('set_startupapplication_completed Exception: {}'.format(ex))
            return False

    @staticmethod
    def check_startupapplication_completed() -> bool:
        try:
            value_to_check = CacheRedisAdapter.get_cached_info(label_info=CachedComponents.LABEL_STARTUP_COMPLETED, type_data=int)

            if not value_to_check:
                return False

            if value_to_check != CachedComponents.VALUE_STARTUP_COMPLETED:
                return False

            return True
        except Exception as ex:
            logger.error('check_startupapplication_completed Exception: {}'.format(ex))
            return False

    @staticmethod
    def save_queuedetectionalert_id(queue_detection_alert_id: int) -> bool:
        try:
            return CacheRedisAdapter.list_append_singleelement(label_info=CachedComponents.LABEL_QUEUEDETECTIONALERT_CATALOG,
                                                               elem_to_append=queue_detection_alert_id)

        except Exception as ex:
            logger.error('save_queuedetectionalert_id Exception: {}'.format(ex))
            return False

    @staticmethod
    def get_queuedetectionalert_id() -> int:
        try:
            return CacheRedisAdapter.\
                list_extractfirstelement(label_info=CachedComponents.LABEL_QUEUEDETECTIONALERT_CATALOG,
                                         type_element=int)
        except Exception as ex:
            logger.error('get_queuedetectionalert_id Exception: {}'.format(ex))
            return 0

    @staticmethod
    def get_list_outputmessage_ids(outmessagetype: OutputMessageType) -> List[int]:
        try:
            list_ids = None
            if outmessagetype == OutputMessageType.OUTPUT_MESSAGE_TYPE_QUEUEDETECTIONALERT:
                list_ids = CachedComponents.getlist_queuedetectionalert_id()
            elif outmessagetype == OutputMessageType.OUTPUT_MESSAGE_TYPE_CROWDHEATMAPOUTPUT:
                list_ids = CachedComponents.getlist_crowdheatmapoutputids()

            return UtilityList.get_list_noduplicates(list_to_clean=list_ids)
        except Exception as ex:
            logger.error('get_list_outputmessage_ids Exception: {}'.format(ex))
            return None

    @staticmethod
    def getlist_queuedetectionalert_id() -> List[int]:
        try:
            return CacheRedisAdapter.list_extractallelements(label_info=CachedComponents.LABEL_QUEUEDETECTIONALERT_CATALOG, type_element=int)
        except Exception as ex:
            logger.error('getlist_queuedetectionalert_id Exception: {}'.format(ex))
            return None

    @staticmethod
    def getcounter_queuedetectionalert_id() -> int:
        try:
            return CacheRedisAdapter.list_getcounterelements(label_info=CachedComponents.LABEL_QUEUEDETECTIONALERT_CATALOG)
        except Exception as ex:
            logger.error('getcounter_queuedetectionalert_id Exception: {}'.format(ex))
            return 0

    @staticmethod
    def increase_counter_output(output_type: OutputMessageType, increase: int = 1) -> bool:
        if output_type == OutputMessageType.OUTPUT_MESSAGE_TYPE_CROWDHEATMAPOUTPUT:
            return CacheRedisAdapter.counter_increase(label_info=LABELS_CACHE_REDIS.LABEL_CACHE_CROWDHEATMAPCOUNTER,
                                                      increase=increase)
        elif output_type == OutputMessageType.OUTPUT_MESSAGE_TYPE_QUEUEDETECTIONALERT:
            return CacheRedisAdapter.counter_increase(label_info=LABELS_CACHE_REDIS.LABEL_CACHE_QUEUEDETECTIONALERT,
                                                      increase=increase)
        return False

    @staticmethod
    def get_counter_output(output_list: List[OutputMessageType]) -> int:
        if not output_list:
            return 0

        counter_total = 0

        for output_type in output_list:
            if output_type == OutputMessageType.OUTPUT_MESSAGE_TYPE_CROWDHEATMAPOUTPUT:
                counter_total += CacheRedisAdapter.counter_get(label_info=LABELS_CACHE_REDIS.LABEL_CACHE_CROWDHEATMAPCOUNTER)
            elif output_type == OutputMessageType.OUTPUT_MESSAGE_TYPE_QUEUEDETECTIONALERT:
                counter_total += CacheRedisAdapter.counter_get(label_info=LABELS_CACHE_REDIS.LABEL_CACHE_QUEUEDETECTIONALERT)

        return counter_total

    @staticmethod
    def increase_counter_crowd_heatmap_output():
        try:
            return CacheRedisAdapter.counter_increase(LABELS_CACHE_REDIS.LABEL_CACHE_CROWDHEATMAPCOUNTER)
        except Exception as ex:
            logger.error('CachedComponents increase_counter_crowd_heatmap_output Exception: {}'.format(ex))
            return 0

    @staticmethod
    def initialize_components(running_id: int):
        try:
            CachedComponents.initialize_counter_crowd_heatmap_output()
            CachedComponents.initialize_observable_id()
            CachedComponents.set_sw_running_current_id(identifier=running_id)
            CachedComponents.initialize_list_localization_id()
            CachedComponents.set_counter_observable_localization_unprocessed(value=0)
            CachedComponents.set_counter_observable(value=0)
        except Exception as ex:
            logger.error('CachedComponents initialize_components Exception: {}'.format(ex))
            return False

    @staticmethod
    def initialize_counter_crowd_heatmap_output() -> bool:
        try:
            return CacheRedisAdapter.counter_create(label_info=LABELS_CACHE_REDIS.LABEL_CACHE_CROWDHEATMAPCOUNTER)
        except Exception as ex:
            logger.error('CachedComponents get_counter_crowd_heatmap_output Exception: {}'.format(ex))
            return False

    @staticmethod
    def get_counter_crowd_heatmap_output():
        try:
            value_return = CacheRedisAdapter.counter_get(LABELS_CACHE_REDIS.LABEL_CACHE_CROWDHEATMAPCOUNTER)

            if not value_return:
                return 0

            return value_return
        except Exception as ex:
            logger.error('CachedComponents get_counter_crowd_heatmap_output Exception: {}'.format(ex))
            return 0

    @staticmethod
    def check_remaining_crowdheatmap_output() -> bool:
        try:
            if CacheRedisAdapter.list_getcounterelements(LABELS_CACHE_REDIS.LABEL_CACHE_CROWDHEATMAPOUTPUT) == 0:
                return False

            return True
        except Exception as ex:
            logger.error('CachedComponents check_remaining_crowdheatmap_output Exception: {}'.format(ex))
            return False

    @staticmethod
    def get_new_crowdheatmapoutput_id() -> int:
        try:
            return CacheRedisAdapter.list_extractlastelement(label_info=LABELS_CACHE_REDIS.LABEL_CACHE_CROWDHEATMAPOUTPUT,
                                                             type_element=int)
        except Exception as ex:
            logger.error('CachedComponents check_remaining_crowdheatmap_output Exception: {}'.format(ex))
            return -1

    @staticmethod
    def set_last_observation_id(obs_id: int) -> bool:
        try:
            if not CacheRedisAdapter.is_initialized:
                return False

            return CacheRedisAdapter.set_cache_info(label_info=LABELS_CACHE_REDIS.LABEL_CACHE_OBSERVATION_ID,
                                                    data=obs_id)
        except Exception as ex:
            logger.error('CachedComponents set_last_observation_id Exception: {}'.format(ex))
            return False

    @staticmethod
    def get_last_observable_id():
        try:
            if not CacheRedisAdapter.is_initialized:
                return 0

            current_counter = CacheRedisAdapter.get_cached_info(label_info=LABELS_CACHE_REDIS.LABEL_CACHE_OBSERVATION_ID,
                                                                type_data=int)

            if current_counter is None:
                return 0

            return current_counter
        except Exception as ex:
            logger.error('CachedComponents get_last_observable_id Exception: {}'.format(ex))
            return 0

    @staticmethod
    def initialize_observable_id():
        try:
            if not CacheRedisAdapter.is_initialized:
                return False

            return CacheRedisAdapter.set_cache_info(label_info=LABELS_CACHE_REDIS.LABEL_CACHE_OBSERVATION_ID,
                                                    data=0)

        except Exception as ex:
            logger.error('CachedComponents initialize_cached_counters Exception: {}'.format(ex))

    @staticmethod
    def notify_new_crowdheatmapoutput(id: int):
        try:
            return CacheRedisAdapter.list_append_singleelement(label_info=LABELS_CACHE_REDIS.LABEL_CACHE_CROWDHEATMAPOUTPUT,
                                                               elem_to_append=id)
        except Exception as ex:
            logger.error('CachedComponents get_list_observation_id Exception: {}'.format(ex))
            return None

    @staticmethod
    def getlist_crowdheatmapoutputids() -> List[int]:
        try:
            return CacheRedisAdapter.list_extractallelements(label_info=LABELS_CACHE_REDIS.LABEL_CACHE_CROWDHEATMAPOUTPUT,
                                                             type_element=int)
        except Exception as ex:
            logger.error('CachedComponents get_list_observation_id Exception: {}'.format(ex))
            return None

    @staticmethod
    def initialize_list_localization_id(list_obs_ids=list()) -> bool:
        try:
            return CacheRedisAdapter.list_create(label_info=LABELS_CACHE_REDIS.LABEL_CACHE_LOCALIZATIONOBS,
                                                 list_startup=list_obs_ids)
        except Exception as ex:
            logger.error('CachedComponents get_list_observation_id Exception: {}'.format(ex))
            return False

