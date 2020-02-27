from unittests.unittests_cache import UnitTestCacheRedis
from unittests.unittests_processing import UnitTestProcessing
from unittests.unittest_savingmongodb import UnitTestMongoDB
from unittests.unittest_queuedetection import UnitTestQueueDetection
import logging
from typing import List, Dict

logger = logging.getLogger('textlogger')


class UnitTestMain:
    @staticmethod
    def print_report(dictionary_test_results: Dict[str, bool] = dict()):
        if not dictionary_test_results:
            return

        for key in dictionary_test_results:
            logger.info('UnitTestName: {0}, Result: {1}'.format(key, dictionary_test_results[key]))

    @staticmethod
    def launch_all_tests(enable_tests: bool = False, list_enabled_tests: List[str] = list()) \
            -> Dict[str, bool]:
        try:
            if not enable_tests or not list_enabled_tests:
                return None

            dict_results = dict()

            for test_name in list_enabled_tests:
                if test_name == "QueueDetection":
                    if not UnitTestQueueDetection.initialize_environment():
                        dict_results[test_name] = False
                        continue
                    dict_results[test_name] = UnitTestQueueDetection.test_method_queue_detection()

                if test_name == 'CacheRedis':
                    if not UnitTestCacheRedis.initialize_environment():
                        dict_results[test_name] = False
                        continue
                    dict_results[test_name] = UnitTestCacheRedis.test_method()

                elif test_name == 'CacheRedisTestObservables':
                    if not UnitTestCacheRedis.initialize_environment():
                        dict_results[test_name] = False
                        continue
                    dict_results[test_name] = UnitTestCacheRedis.test_method_obs_management()

                elif test_name == 'Processing':
                    if not UnitTestProcessing.initialize_environment():
                        dict_results[test_name] = False
                        continue
                    dict_results[test_name] = UnitTestProcessing.test_method()

                elif test_name == 'MongoDB':
                    if not UnitTestMongoDB.initialize_environment():
                        dict_results[test_name] = False
                        continue
                    dict_results[test_name] = UnitTestMongoDB.test_method_save()

            return dict_results
        except Exception as ex:
            logger.error('UnitTestMain Execution Exception: {}'.format(ex))
            return None
