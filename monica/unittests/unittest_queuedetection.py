from utility.utility_catalog_cached import UtilityCatalogCached
from jobs.cache_redis import CacheRedisAdapter, CacheRecord
from jobs.models import Localization, ObservableGeneric, QueueDetectionAlert, CrowdDensityLocalObservation, CameraRegistration
from unittests.unittests_utilities_observables import UnitTestsUtilityObservables
from jobs.processing.queue_detection import QueueDetectionAlgorithm
from entities.densitymap_types import DensityMapConfiguration, SingleRowAdiacentCells, MatrixCell, RegionAdiacentCells, GroupRegionsAdiacentCells
from utility.geodesy import GeoPosition
from django.contrib.gis.geos import Point, MultiPoint
from utility.utility_database import UtilityDatabase

import datetime
import logging
import pytz
import numpy as np
from typing import List, Dict, Any
from general_types.modelsenums import OutputMessageType

logger = logging.getLogger('textlogger')


class UnitTestQueueDetection:
    @staticmethod
    def initialize_environment() -> bool:
        try:
            return CacheRedisAdapter.initialize()
        except Exception as ex:
            logger.error('UnitTestQueueDetection initialize_environment test_method Exception: {}'.format(ex))
            return False

    @staticmethod
    def compare_list(list_a: List[Any], list_b: List[Any]) -> bool:
        try:
            if not list_a or not list_b:
                return False

            if len(list_a) != len(list_b):
                return False

            for item in list_a:
                if item not in list_b:
                    return False

            return True
        except Exception as ex:
            logger.error('UnitTestQueueDetection Exception compare_list: {}'.format(ex))
            return False

    @staticmethod
    def compare_dictionaries(dict_a: Dict[str, Any], dict_b: Dict[str, Any]) -> bool:
        try:
            if not dict_a or not dict_b:
                return False

            if len(list(dict_a.keys())) != len(list(dict_b.keys())):
                return False

            for key in dict_a.keys():
                if key not in dict_b.keys():
                    return False

                value_a = dict_a[key]
                value_b = dict_b[key]

                if value_a is None or value_b is None:
                    return False

                if type(value_a) != type(value_b):
                    return False

                if isinstance(value_a, dict):
                    if not UnitTestQueueDetection.compare_dictionaries(dict_a=value_a,
                                                                       dict_b=value_b):
                        return False
                    continue

                if isinstance(value_a, list):
                    if not UnitTestQueueDetection.compare_list(list_a=value_a,
                                                               list_b=value_b):
                        return False
                    continue

                if value_a != value_b:
                    return True

            return True
        except Exception as ex:
            logger.error('Exception: {}'.format(ex))
            return False

    @staticmethod
    def get_densitymap() -> np.ndarray:
        return np.array(
            [[0.0, 0.0, 1.0, 2.0, 1.0, 1.0, 1.0, 0.0, 0.0],
             [0.0, 0.0, 1.0, 2.0, 1.0, 0.0, 0.0, 0.0, 0.0],
             [1.0, 1.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0],
             [0.0, 2.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
             [0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 2.0, 2.0, 1.0],
             [0.0, 0.0, 1.0, 1.0, 1.0, 1.0, 2.0, 5.0, 4.0],
             [0.0, 0.0, 0.0, 0.0, 1.0, 2.0, 1.0, 3.0, 3.0],
             [0.0, 0.0, 0.0, 2.0, 3.0, 2.0, 1.0, 1.0, 1.0],
             [0.0, 0.0, 1.0, 4.0, 5.0, 2.0, 2.0, 2.0, 0.0],
             [0.0, 0.0, 1.0, 4.0, 3.0, 1.0, 5.0, 5.0, 1.0],
             [0.0, 2.0, 2.0, 3.0, 4.0, 3.0, 6.0, 11.0, 8.0],
             [0.0, 1.0, 2.0, 2.0, 3.0, 3.0, 3.0, 7.0, 7.0]])

    @staticmethod
    def convert_catalogregions_to_list_queuedetection(catalog_regions: Dict[int, GroupRegionsAdiacentCells],
                                                      camera_registration: CameraRegistration) -> List[QueueDetectionAlert]:
        list_queuedetectionalert = list()
        count_queueshapearea_saved = 0
        for mean_people in catalog_regions.keys():

            logger.info('test_method_queue_detection mean count queue: {}'.format(mean_people))

            group_region = catalog_regions[mean_people]

            if not group_region or group_region.empty():
                logger.info('test_method_queue_detection group_region empty')
                continue

            logger.info('test_method_queue_detection group_region count: {}'.format(len(group_region)))

            for region in group_region.get_listregions():
                if not region:
                    continue

                logger.info('test_method_queue_detection single queue detection creation...')
                single_queue_detection = QueueDetectionAlert()
                single_queue_detection.qsma_id = "QSA_ID{0:02d}_Mean{1:03d}".format(count_queueshapearea_saved,
                                                                                    mean_people)
                single_queue_detection.initialize_status()
                logger.info('test_method_queue_detection single queue detection created')

                single_queue_detection.set_region_queue(region_queue=region,
                                                        camera_registration=camera_registration)

                single_queue_detection.mean_people = mean_people
                single_queue_detection.set_timestamp(timestamp=datetime.datetime.now(tz=pytz.utc))
                list_queuedetectionalert.append(single_queue_detection)

            return list_queuedetectionalert

    @staticmethod
    def test_method_queue_detection() -> bool:
        try:
            CacheRedisAdapter.initialize()

            logger.info('test_method_queue_detection Started')
            crowd_density_local = CrowdDensityLocalObservation()
            crowd_density_local.density_map = UnitTestQueueDetection.get_densitymap()

            camera_registration = CameraRegistration(ground_plane_position=Point(x=12.56539,
                                                                                 y=55.67474,
                                                                                 srid=4326),
                                                     ground_plane_orientation=30)

            logger.info('test_method_queue_detection Third Step')
            dictionary_regions = QueueDetectionAlgorithm.find_queueshape_areas(density_map=crowd_density_local.density_map,
                                                                               min_cell_count=3)

            count_queueshapearea_saved = 0

            logger.info('test_method_queue_detection Fourth Step')
            for mean_people in dictionary_regions.keys():

                logger.info('test_method_queue_detection mean count queue: {}'.format(mean_people))

                group_region = dictionary_regions[mean_people]

                if not group_region or group_region.empty():
                    logger.info('test_method_queue_detection group_region empty')
                    continue

                logger.info('test_method_queue_detection group_region count: {}'.format(len(group_region)))

                for region in group_region.get_listregions():
                    if not region:
                        continue

                    logger.info('test_method_queue_detection single queue detection creation...')
                    single_queue_detection = QueueDetectionAlert()
                    single_queue_detection.qsma_id = "QSA_ID{0:02d}_Mean{1:03d}".format(count_queueshapearea_saved,
                                                                                        mean_people)
                    single_queue_detection.initialize_status()
                    logger.info('test_method_queue_detection single queue detection created')

                    single_queue_detection.set_region_queue(region_queue=region,
                                                            camera_registration=camera_registration)

                    single_queue_detection.mean_people = mean_people
                    single_queue_detection.set_timestamp(timestamp=datetime.datetime.now(tz=pytz.utc))

                    logger.info('test_method_queue_detection Try Saving SingleQueueDetection')
                    single_queue_detection.save()
                    logger.info('test_method_queue_detection saved single_queue_detection: {}'.format(single_queue_detection.qda_id))
                    count_queueshapearea_saved += 1

                    json_test = single_queue_detection.to_dictionary()
                    json_test1 = single_queue_detection.to_ogc_dictionary()
                    string_test = single_queue_detection.to_string()

                    CacheRedisAdapter.set_cache_info(label_info='DATATESTSAVED',
                                                     data=json_test1)

                    json_test_2 = CacheRedisAdapter.get_cached_info(label_info='DATATESTSAVED',
                                                                    type_data=dict)

                    logger.info('Cached JSON: {}'.format(json_test1))
                    logger.info('Read JSON From Cache: {}'.format(json_test_2))

                    queue_detection_db = UtilityDatabase.get_outputmessage_byid(id=single_queue_detection.qda_id,
                                                                                outputmessagetype=OutputMessageType.OUTPUT_MESSAGE_TYPE_QUEUEDETECTIONALERT)
                    json_test_db = queue_detection_db.to_dictionary()
                    string_test_db = queue_detection_db.to_string()

                    if UnitTestQueueDetection.compare_dictionaries(dict_a=json_test,
                                                                   dict_b=json_test_db):
                        logger.info('Comparison JSON From hardcoded to DB extracted QueueDetectionAlert info are equals')
                    else:
                        logger.info('Comparison JSON From hardcoded to DB extracted QueueDetectionAlert are not equals')

                    logger.info('String Hardcoded: {}'.format(string_test))
                    logger.info('String DB Extracted: {}'.format(string_test_db))

            logger.info('test_method_queue_detection saved correctly {} QueueDetectionAlert'.format(count_queueshapearea_saved))

            return True
        except Exception as ex:
            logger.error('UnitTestQueueDetection test_method_queue_detection test_method Exception: {}'.format(ex))
            return False
