from utility.utility_catalog_cached import UtilityCatalogCached
from jobs.cache_redis import CacheRedisAdapter, CacheRecord
from jobs.models import Localization, ObservableGeneric
from general_types.label_ogc import LabelObservationType
from unittests.unittests_utilities_observables import UnitTestsUtilityObservables
import datetime
import logging
import pytz
from typing import List, Dict

logger = logging.getLogger('textlogger')


class UnitTestCacheRedis:
    @staticmethod
    def test_method():
        try:
            LABEL_DICTIONARY_OBSERVABLE = 'OBSERVABLE'
            LABEL_COUNTER = 'TEST_COUNTER'
            LABEL_TEST_LIST = 'TEST_LIST'
            LABEL_TEST_LISTSTRING = 'TEST_LIST_STRING'
            STRING_TRY = 'PROVA'
            LABEL_LIST_OBSERVABLE = 'TEST_LIST_OBSERVABLE'
            LABEL_DICT_OBSERVABLE = 'TEST_DICT_OBSERVABLES'
            LABEL_GOST_FILTER = 'GOST_LARGE_SCALE_TEST'

            max_counter = 3
            timestamp = datetime.datetime.now(tz=pytz.utc)

            logger.info('STARTED TEST DEMO {} Observable CatalogCache Write Simulated'.format(max_counter))

            start_value = 4
            increase_time = 10

            CacheRedisAdapter.set_cache_info(label_info='NEW', data=0)

            byte_array = CacheRecord.dumps(STRING_TRY)
            string_return = CacheRecord.loads(byte_array=byte_array,
                                              type_object=str)

            byte_array = CacheRecord.dumps(start_value)
            compare_value = CacheRecord.loads(byte_array=byte_array, type_object=int)

            logger.info('String pass: {0}, string get: {1}'.format(STRING_TRY,
                                                                   string_return))

            observable = UnitTestsUtilityObservables.test_method_create_observable(label_gost=LABEL_GOST_FILTER,
                                                                                   index_element=1,
                                                                                   device_index=1,
                                                                                   timestamp=timestamp)

            byte_array = CacheRecord.dumps(record=observable)
            observable_test = CacheRecord.loads(byte_array=byte_array, type_object=Localization)

            CacheRedisAdapter.counter_create(label_info=LABEL_COUNTER,
                                             start_value=start_value)

            for counter in range(0, increase_time):
                CacheRedisAdapter.counter_increase(label_info=LABEL_COUNTER)

            value = CacheRedisAdapter.counter_get(label_info=LABEL_COUNTER)

            if value != start_value + increase_time:
                logger.error('Unexpected counter value: {0} rather than {1}'.format(value, counter + increase_time))

            list_elements = list()
            dictionary_test = dict()

            for index_element in range(0, max_counter):
                observable = UnitTestsUtilityObservables.test_method_create_observable(label_gost=LABEL_GOST_FILTER,
                                                                                       index_element=index_element,
                                                                                       device_index=index_element,
                                                                                       timestamp=timestamp)
                list_elements.append(observable)
                dictionary_test[observable.get_label_cache()] = observable

            CacheRedisAdapter.set_cache_info(label_info=LABEL_LIST_OBSERVABLE,
                                             data=list_elements)

            CacheRedisAdapter.set_cache_info(label_info=LABEL_DICT_OBSERVABLE,
                                             data=dictionary_test)

            list_return = CacheRedisAdapter.get_cached_info(label_info=LABEL_LIST_OBSERVABLE,
                                                            type_data=list)

            dict_return = CacheRedisAdapter.get_cached_info(label_info=LABEL_DICT_OBSERVABLE,
                                                            type_data=dict)

            CacheRedisAdapter.dictionary_create(label_info=LABEL_DICTIONARY_OBSERVABLE)

            CacheRedisAdapter.list_create(label_info=LABEL_TEST_LISTSTRING)
            CacheRedisAdapter.list_append_singleelement(label_info=LABEL_TEST_LISTSTRING,
                                                        elem_to_append=STRING_TRY)
            string_get = CacheRedisAdapter.list_extractfirstelement(label_info=LABEL_TEST_LISTSTRING, type_element=str)

            logger.info('Test Set String: {0}, Extracted: {1}'
                        .format(STRING_TRY,
                                string_get))

            for index_element in range(0, max_counter):

                if (index_element % 500) == 0:
                    logger.info('TEST EXAMPLE COUNTER: {}'.format(index_element))

                localization_test = UnitTestsUtilityObservables.test_method_create_observable(label_gost=LABEL_GOST_FILTER,
                                                                                              index_element=index_element,
                                                                                              device_index=index_element,
                                                                                              timestamp=timestamp)

                CacheRedisAdapter.dictionary_update_value(label_info=LABEL_DICTIONARY_OBSERVABLE,
                                                          key=localization_test.get_label_cache(),
                                                          value=localization_test)

            logger.info('STARTED TEST DEMO {} Observable CatalogCache Read Simulated'.format(max_counter))

            dictionary_imported = CacheRedisAdapter.dictionary_get_all(label_info=LABEL_DICTIONARY_OBSERVABLE,
                                                                       type_value=ObservableGeneric)

            for index_element in range(0, max_counter):
                label_cache = UnitTestsUtilityObservables.\
                    test_method_get_label_cache(label_gostfilter=LABEL_GOST_FILTER,
                                                index_element=index_element)

                if label_cache not in dictionary_imported or not dictionary_imported[label_cache]:
                    return False

                localization_read = dictionary_imported[label_cache]

                if not UnitTestsUtilityObservables.test_method_check_obs_validity(observable=localization_read,
                                                                                  index_element=index_element,
                                                                                  timestamp=timestamp):
                    return False

                if (index_element % 500) == 0:
                    logger.info('TEST EXAMPLE COUNTER READ: {}'.format(index_element))

            logger.info('END TEST DEMO {} Observable CatalogCache Read Simulated'.format(max_counter))

            CacheRedisAdapter.list_create(label_info=LABEL_TEST_LIST)

            for index_element in range(0, max_counter):
                localiz_to_append = UnitTestsUtilityObservables.test_method_create_observable(label_gost=LABEL_GOST_FILTER,
                                                                                              index_element=index_element,
                                                                                              device_index=index_element,
                                                                                              timestamp=timestamp)
                CacheRedisAdapter.list_append_singleelement(label_info=LABEL_TEST_LIST,
                                                            elem_to_append=localiz_to_append)

            index_element = 0
            while CacheRedisAdapter.list_getcounterelements(label_info=LABEL_TEST_LIST) > 0:
                localiz_extracted = CacheRedisAdapter.list_extractfirstelement(label_info=LABEL_TEST_LIST,
                                                                               type_element=Localization)

                if not UnitTestsUtilityObservables.test_method_check_obs_validity(observable=localiz_extracted,
                                                                                  index_element=index_element,
                                                                                  timestamp=timestamp):
                    return False

                index_element += 1

            logger.info('END TEST DEMO {} Observable CatalogCache List Extract'.format(max_counter))

            return True
        except Exception as ex:
            logger.error('UnitTestCacheRedis test_method Exception: {}'.format(ex))
            return False

    @staticmethod
    def initialize_environment() -> bool:
        try:
            return CacheRedisAdapter.initialize()
        except Exception as ex:
            logger.error('initialize_environment test_method Exception: {}'.format(ex))
            return False

    @staticmethod
    def test_method_obs_management() -> bool:
        try:
            max_counter = 10000
            LABEL_GOST_FILTER = 'GOST_LARGE_SCALE_TEST'
            timestamp = datetime.datetime.now(tz=pytz.utc)

            logger.info('STARTED TEST DEMO {} Observable CatalogCache Write Simulated'.format(max_counter))

            for counter in range(0, max_counter):
                observable = UnitTestsUtilityObservables.test_method_create_observable(label_gost=LABEL_GOST_FILTER,
                                                                                       index_element=counter,
                                                                                       device_index=counter,
                                                                                       timestamp=timestamp)
                UtilityCatalogCached.append_new_observable(label_type_observable=observable.get_label_cache(),
                                                           observable=observable)

            logger.info('END WRITE-START READING Counter: {}'.format(max_counter))
            dictionary_observable = UtilityCatalogCached.get_complete_dictionary_observables(list_type_observables=LabelObservationType.LABEL_OBSTYPE_LOCALIZATION)

            for counter in range(0, max_counter):
                label_cache = UnitTestsUtilityObservables.\
                    test_method_get_label_cache(label_gostfilter=LABEL_GOST_FILTER,
                                                index_element=counter)

                if label_cache not in dictionary_observable\
                        or not dictionary_observable[label_cache]:
                    logger.error('Test Failed (cannot find observable in Dictionary)')
                    return False

                if not UnitTestCacheRedis.test_method_check_obs_validity(observable=dictionary_observable[label_cache],
                                                                         index_element=counter,
                                                                         timestamp=timestamp):
                    logger.error('Test Failed (Wrong Observable Extracted)')
                    return False
            logger.info('Test Read-Write Success')

        except Exception as ex:
            logger.error('UnitTestCacheRedis test_method_obs_management Exception: {}'.format(ex))
            return False
