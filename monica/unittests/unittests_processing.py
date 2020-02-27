from utility.utility_catalog_cached import UtilityCatalogCached
from general_types.label_ogc import LabelObservationType
from jobs.cache_redis import CachedComponents, CacheRedisAdapter
from jobs.processing.processing import Processing
from shared.settings.default_datastreams import DICTIONARY_OBSERVABLE_TOPICS, \
    DICTIONARY_OBSERVABLE_TOPICS_CAMERAS, \
    DEBUG_DEFAULT_SELECTED_GOST
from shared.settings.appglobalconf import LOCAL_CONFIG, LocConfLbls, MONITORING_AREA
from entities.datastream_topic_adapter import HelperDatastreamGenerator
from jobs.models import MonitoringArea, QueueDetectionAlert, CameraRegistration
from unittests.unittests_utilities_observables import UnitTestsUtilityObservables

import datetime
import logging
import pytz
import numpy as np

logger = logging.getLogger('textlogger')


class UnitTestProcessing:

    @staticmethod
    def initialize_environment() -> bool:
        try:
            return UtilityCatalogCached.initialize_catalog()
        except Exception as ex:
            logger.error('initialize_environment test_method Exception: {}'.format(ex))
            return False

    @staticmethod
    def test_method_cachelist() -> bool:
        try:
            name_list = 'LISTTESTS'
            counter_test = 20

            CacheRedisAdapter.list_create(label_info=name_list)

            for index in range(0, counter_test):
                CacheRedisAdapter.list_append_singleelement(label_info=name_list, elem_to_append=index*2)

            list_extracted = CacheRedisAdapter.list_extractallelements(label_info=name_list, type_element=int)

            if not list_extracted:
                return False

            return True
        except Exception as ex:
            logger.error('Exception test_method_todelete: {}'.format(ex))

    @staticmethod
    def test_method() -> bool:
        UnitTestProcessing.test_method_cachelist()
        return UnitTestProcessing.test_method_queueshapearea()

    @staticmethod
    def test_method_queueshapearea() -> bool:
        try:
            camera_id = 'LEEDS_CAM_4'
            timestamp = datetime.datetime.now(tz=pytz.utc)
            density_map = np.matrix(
                [
                    [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                    [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                    [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                    [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0],
                    [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0],
                    [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                    [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0],
                    [2.0, 5.0, 7.0, 9.0, 11.0, 1.0, 17.0, 18.0, 19.0, 20.0],
                    [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                    [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                    [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                    [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                    [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                    [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                    [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                    [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                    [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                    [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                    [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                    [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                    [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                    [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                    [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                    [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                    [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                    [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                    [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                    [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                    [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                    [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
                ])

            dictionary_camera_registration = {
                'camera_id': camera_id,
                'camera_type': 'rgb',
                'camera_position': [53.81761, -1.58331],
                'ground_plane_position': [53.81761, -1.58331],
                'ground_plane_size': [10, 30],
                'image_2_ground_plane_matrix': [53.81761, -1.58331],
                'zone_id': 'Main Entrance',
                'state': 1
                }

            camera_registration = CameraRegistration()
            camera_registration.from_dictionary(dictionary=dictionary_camera_registration)

            UtilityCatalogCached.add_device_registration(device_registration=camera_registration)

            crowd_density_local = UnitTestsUtilityObservables.test_method_create_obs_crowddensitylocal(labe_gost=DEBUG_DEFAULT_SELECTED_GOST,
                                                                                                       device_id=camera_id,
                                                                                                       index_element=56,
                                                                                                       density_matrix=density_map,
                                                                                                       timestamp=timestamp)

            if not crowd_density_local:
                return False

            device_registration = UtilityCatalogCached.get_device_registration(datastream_id=camera_id)

            if not device_registration:
                return False

            if not crowd_density_local.set_info_registration(device_registration=device_registration):
                return False

            catalog_datastreams, list_datastreams = \
                HelperDatastreamGenerator.debug_create_datastreams_from_dictionary(specific_argument=LabelObservationType.LABEL_OBSTYPE_CROWDDENSITY,
                                                                                   dictionary_topics=DICTIONARY_OBSERVABLE_TOPICS_CAMERAS)

            UtilityCatalogCached.append_new_observable(label_type_observable=crowd_density_local.get_type_observable(),
                                                       observable=crowd_density_local)

            catalog_observables = UtilityCatalogCached.get_complete_dictionary_observables(list_type_observables=catalog_datastreams)

            Processing.real_processing_task(last_catalog_observation=catalog_observables,
                                            monitoring_area=None)

            total_element = CachedComponents.getcounter_queuedetectionalert_id()
            counter_element = 0

            while CachedComponents.getcounter_queuedetectionalert_id() > 0:

                if counter_element >= total_element:
                    logger.error('Unexpected Behaviour From CachedList QueueDetection Alert. Exit')
                    return False

                qdaid = CachedComponents.get_queuedetectionalert_id()

                if qdaid == 0:
                    return False

                queue_detection_alert = QueueDetectionAlert.objects.get(qda_id=qdaid)

                if not queue_detection_alert:
                    continue

                dictionary_to_transfer = queue_detection_alert.to_dictionary()

                if not dictionary_to_transfer:
                    continue

                logger.info('Dictionary QueueShapeArea: {0}'.format(dictionary_to_transfer))

                counter_element += 1

            logger.info('Test Processing QueueDetectionAlert Ended With Success')

            return True
        except Exception as ex:
            logger.error('test_method_queueshapearea Exception: {}'.format(ex))
            return False

    @staticmethod
    def test_method_localization() -> bool:
        try:
            # checkpos_llh = [45.223333, 7.6555333, 0]
            # refpos_llh = [45.223133, 7.6555033, 0]

            LABEL_GOST_FILTER = 'GOST_LARGE_SCALE_TEST'
            max_counter = 10

            pilot_name = LOCAL_CONFIG[LocConfLbls.LABEL_PILOT_NAME]
            monitoring_area_dictionary = MONITORING_AREA

            timestamp = datetime.datetime.now(tz=pytz.utc)

            logger.info('UNIT TEST PROCESSING STARTED. Launched Procedure Create-Store {} Observables'.format(max_counter))

            catalog_datastreams, list_datastreams = \
                HelperDatastreamGenerator.debug_create_datastreams_from_dictionary(specific_argument=LabelObservationType.LABEL_OBSTYPE_LOCALIZATION,
                                                                                   dictionary_topics=DICTIONARY_OBSERVABLE_TOPICS)
            for counter in range(0, max_counter):
                index_new_obs = (2*counter)+4157
                observable = UnitTestsUtilityObservables.test_method_create_observable(label_gost=LABEL_GOST_FILTER,
                                                                                       index_element=index_new_obs,
                                                                                       device_index=counter,
                                                                                       timestamp=timestamp)
                UtilityCatalogCached.append_new_observable(label_type_observable=observable.get_type_observable(),
                                                           observable=observable)

            logger.info('UNIT TEST PROCESSING END STORE PROCEDURE. LAUNCH DATA EXTRACTION')

            last_catalog_observation = UtilityCatalogCached.get_observations_catalog(catalog_datastreams)

            if not last_catalog_observation:
                return False

            logger.info('UNIT TEST PROCESSING END DATA EXTRACTION PROCEDURE. LAUNCH BACKUP')

            UtilityCatalogCached.set_catalog_observable_backup(catalog_observable=last_catalog_observation)

            logger.info('UNIT TEST PROCESSING END BACKUP. LAUNCH PROCESSING')

            if not Processing.real_processing_task(last_catalog_observation=last_catalog_observation,
                                                   monitoring_area=MonitoringArea(pilot_name=pilot_name,
                                                                                  dictionary=monitoring_area_dictionary)):
                logger.info('TASK real_processing_task FAILED')
                return False

            logger.info('UNIT TEST PROCESSING DONE WITH SUCCESS')

            list_observable_to_backup = UtilityCatalogCached.get_list_obstobackup()

            if not list_observable_to_backup:
                return False

            UtilityCatalogCached.confirm_obs_backup()

            list_observable_to_backup = UtilityCatalogCached.get_list_obstobackup()

            if list_observable_to_backup:
                return False

            return True
        except Exception as ex:
            logger.info('UnitTestProcessing Exception: {}'.format(ex))
            return False

