from general_types.virtual_classes import ObservableGeneric
from jobs.models import Localization, CrowdDensityLocalObservation, CameraRegistration
import datetime
import logging
from numpy import matrix
from typing import Dict, Any

logger = logging.getLogger('textlogger')


class UnitTestsUtilityObservables:
    @staticmethod
    def test_method_get_label_cache(label_gostfilter: str, index_element: int) -> str:
        return '{0}/Datastreams({1})/Observations'.format(label_gostfilter, str(index_element))

    @staticmethod
    def test_method_get_device_name(device_index: int):
        return 'WRISTBAND-GW/868/Localization-Wristband/GeoTag{:02d}'.format(device_index)

    @staticmethod
    def test_method_get_latitude(index_element: int) -> float:
        return 55.67298336627162 + (index_element * 0.000000235)

    @staticmethod
    def test_method_get_longitude(index_element: int) -> float:
        return 12.56703788516 + (index_element * 0.0000000222)

    @staticmethod
    def test_method_create_obs_crowddensitylocal(labe_gost: str,
                                                 index_element: int,
                                                 device_id: str,
                                                 timestamp: datetime.datetime,
                                                 density_matrix: matrix) -> CrowdDensityLocalObservation:
        try:
            crowd_density_local = CrowdDensityLocalObservation()
            crowd_density_local.set_label_cache(
                label_cache=UnitTestsUtilityObservables.test_method_get_label_cache(label_gostfilter=labe_gost,
                                                                                    index_element=index_element)
            )
            crowd_density_local.timestamp = timestamp
            crowd_density_local.set_device_id(device_id=device_id)
            crowd_density_local.density_map = density_matrix
            crowd_density_local.density_count = density_matrix.sum()

            return crowd_density_local
        except Exception as ex:
            return None

    @staticmethod
    def test_method_create_observable(label_gost: str,
                                      index_element: int,
                                      device_index: int,
                                      timestamp: datetime.datetime) -> ObservableGeneric:
        localization_test = Localization()
        localization_test.set_label_cache(
            label_cache=UnitTestsUtilityObservables.test_method_get_label_cache(label_gostfilter=label_gost,
                                                                                index_element=index_element)
        )
        localization_test.set_observable_id(index_element)
        localization_test.device_id = UnitTestsUtilityObservables.test_method_get_device_name(device_index=device_index)
        localization_test.position.x = UnitTestsUtilityObservables.test_method_get_longitude(index_element=index_element)
        localization_test.position.y = UnitTestsUtilityObservables.test_method_get_latitude(index_element=index_element)
        localization_test.position.srid = 4326
        localization_test.timestamp = timestamp
        localization_test.set_datastream_id(index_element)

        return localization_test

    @staticmethod
    def test_method_check_obs_validity(observable: ObservableGeneric,
                                       index_element: int,
                                       timestamp: datetime.datetime) -> bool:
        if not observable:
            return False

        if observable.get_observable_id() != index_element:
            logger.error('TEST READING FAILED READ obsID Wrong')
            return False

        if observable.position.x - \
                UnitTestsUtilityObservables.test_method_get_longitude(index_element=index_element) > 1e-5:
            logger.error('TEST READING FAILED (Lat Wrong)')
            return False

        if (observable.get_timestamp() - timestamp).total_seconds() != 0:
            logger.error('TEST READING FAILED (timestamp Wrong)')
            return False

        return True
