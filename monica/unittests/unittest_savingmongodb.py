# from utility.utilitymongodb import UtilityMongoDB
from unittests.unittests_utilities_observables import UnitTestsUtilityObservables
from jobs.models import Localization, ObservableGeneric, DictionaryHelper
from typing import List
import datetime
import pytz
from django.contrib.gis.geos import Point
import logging

logger = logging.getLogger('textlogger')


class UnitTestMongoDB:
    COUNTER_OBSERVABLE_SAVING=500
    @staticmethod
    def initialize_environment() -> bool:
        return True

    @staticmethod
    def create_emulated_observables(counter_observables: int = 500) -> List[dict]:
        try:
            timestamp = datetime.datetime.now(tz=pytz.utc)
            list_localization = list()
            for index_element in range(0, counter_observables):
                localization = UnitTestsUtilityObservables.test_method_create_observable(label_gost='TEST_GOST',
                                                                                         index_element=index_element,
                                                                                         device_index=1,
                                                                                         timestamp=timestamp)
                list_localization.append(localization)

            list_dictionaries = DictionaryHelper.list_to_documents(list_localization)

            return list_dictionaries
        except Exception as ex:
            logger.error('{}'.format(ex))

    @staticmethod
    def test_method_save() -> bool:
        try:
            logger.info('UnitTestMongoDB test_method_save launched')

            list_dictionaries = UnitTestMongoDB.create_emulated_observables(counter_observables=UnitTestMongoDB.COUNTER_OBSERVABLE_SAVING)

            # UtilityMongoDB.initialize()

            # counter_obs_before = UtilityMongoDB.get_collections_global_count()

            # UtilityMongoDB.save_many_observable(collection_json_messages=list_dictionaries)
            # counter_obs_after = UtilityMongoDB.get_collections_global_count()
            # UtilityMongoDB.close()

            result = False

            # if counter_obs_after == (counter_obs_before + UnitTestMongoDB.COUNTER_OBSERVABLE_SAVING):
            #     result = True
            #
            # logger.info('UnitTestMongoDB test_method_save result, '
            #             'before_saving: {0}, counter_saved: {1}, after_saved: {2}. Result Operation: {3}'.format(counter_obs_before,
            #                                                                                                       str(UnitTestMongoDB.COUNTER_OBSERVABLE_SAVING),
            #                                                                                                       str(counter_obs_after),
            #                                                                                                       str(result)))
            return result
        except Exception as ex:
            logger.error('UnitTestMongoDB test_method_save Exception: {}'.format(ex))
            return False
