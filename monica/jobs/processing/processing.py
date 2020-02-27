import datetime
import logging
import random
from datetime import datetime
from typing import List, Dict

import numpy as np
import pytz
from django.contrib.gis.geos import Point

from jobs.processing.queue_detection import QueueDetectionAlgorithm

from general_types.general_enums import TypeQueueDetection
# from jobs.provisioning.provisioning import Provisioning
from jobs.cache_redis import CachedComponents
from jobs.models import *
from jobs.processing.calculate_crowdheatmap_from_positions import CrowdHeatmapCalculation
from general_types.label_ogc import LabelObservationType
from utility.geodesy import GeoPosition
from utility.utility_geographic_conversion import GeographicRectangleArea
from utility.utility_matrix_calculation import UtilityMatrixCalculation

# import math

logger = logging.getLogger('textlogger')


class Processing:
    max_number_element_to_process = 10
    flag_get_single_execution=False

    def __init__(self):
        self.max_number_element_to_process = 10

    @staticmethod
    def test_method():
        try:
            geo_ref_area = GeographicRectangleArea(ground_plane_position=GeoPosition(longitude=10.198338,
                                                                               latitude=56.152402),
                                                   size_x_m=120,
                                                   size_y_m=110,
                                                   cell_size_m=10)

            point_to_translate = Point(x=10.199919954191003,
                                       y=56.15339087936523,
                                       srid=4326)

            pos_index = CrowdHeatmapCalculation.calculate_matrixindex_position(postoidentify=point_to_translate,
                                                                               geographic_area=geo_ref_area)

            if not pos_index:
                logger.error('Test Failed')
                return

            if not pos_index.check_inside_limit():
                logger.error('Outside Limit (test failed)')

            # matrix_density = CrowdHeatmapCalculation.create_startup_densitymatrix(geographic_area=geo_ref_area)

            # matrix_density[pos_index.index_matrix_y, pos_index.index_matrix_x] = 1

            matrix_density, list_enu, list_positions_outside = CrowdHeatmapCalculation.calculate_densitymatrix_from_positions(list_position=[point_to_translate], geographic_area=geo_ref_area)

            logger.info('Position Index: {}'.format(pos_index.to_string()))

        except Exception as ex:
            logger.error(ex)

    @staticmethod
    def calculate_numberpeople_shapearea(queue_shape_area, crowd_density_local_event):
        try:
            geographic_area = Processing.convert_queuestape_to_geographicarea(queue_shape_area)

            if not geographic_area.check_position_inside_area(queue_shape_area.ground_plane_position):
                return False

            surface_vector = geographic_area.get_vector_distance(crowd_density_local_event.ground_plane_position)
            density_matrix_queue_shape_subarea = UtilityMatrixCalculation.calculate_matrix_queueshape_subarea(surface_vector,geographic_area)

            return UtilityMatrixCalculation.calculate_numberpeople_queueshapearea(crowd_density_local_event.density_map,
                                                                                  density_matrix_queue_shape_subarea,
                                                                                  queue_shape_area.threshold_alert)

        except Exception as ex:
            logger.error('check_queueevent_crowd_density_local Exception: {}'.format(ex))
            return False

    @staticmethod
    def convert_queuestape_to_geographicarea(queue_shape_single_element):
        try:
            position_ref_queue = queue_shape_single_element.ground_plane_position
            geographic_area = GeographicRectangleArea()
            geographic_area.set_properties(ground_plane_position=position_ref_queue,
                                           size_x_m=queue_shape_single_element.horizontal_size_m,
                                           size_y_m=queue_shape_single_element.vertical_size_m)
            return geographic_area
        except Exception as ex:
            logger.error('convert_queuestape_to_geographicarea Exception: {}'.format(ex))
            return None

    @staticmethod
    def get_timestamp(list_localization: List[Localization]) -> datetime:
        if not list_localization:
            return None

        try:
            list_datetime = list()

            for localization in list_localization:
                list_datetime.append(localization.timestamp)

            return max(list_datetime)
        except Exception as ex:
            return None

    @staticmethod
    def check_locationdevice_mostrecent(local_origin: Localization, local_new: Localization) -> bool:
        try:
            if not local_new:
                return False

            if not local_origin:
                return True

            if local_origin.timestamp < local_new.timestamp:
                return True

            return False
        except Exception:
            return False

    @staticmethod
    def get_list_position(localization_list: List[Localization]) -> List[GeoPosition]:
        try:
            if not localization_list:
                return None

            list_position = list()

            for localization in localization_list:
                list_position.append(GeoPosition.point_to_geoposition(point=localization.position))

            return list_position

        except Exception as ex:
            logger.error(ex)
            return None

    @staticmethod
    def extract_field_observations_id_crowdheatmap(list_observations: List[Localization]) -> np.ndarray:
        try:
            if not list_observations:
                return None

            list_observation_ids = np.zeros(shape=len(list_observations), dtype=int)

            for index in range(0, len(list_observations), 1):
                single_observation = list_observations[index]
                list_observation_ids[index] = single_observation.observation_id

            return list_observation_ids.tolist()
        except Exception as ex:
            logger.error(ex)
            return None

    @staticmethod
    def create_crowdheatmap_record(pilot_name: str,
                                 timestamp: datetime,
                                 geographic_area: GeographicRectangleArea,
                                 density_matrix: np.matrix,
                                 list_observations: List[Localization] = list(), total_number_people: int = 0) -> CrowdHeatmapOutput:
        try:
            crowd_heatmap_output = CrowdHeatmapOutput()

            crowd_heatmap_output.pilot_name = pilot_name
            crowd_heatmap_output.timestamp = timestamp
            # FIXME: RESTORE
            crowd_heatmap_output.density_map = density_matrix.tolist()
            crowd_heatmap_output.ground_plane_position = geographic_area.get_groundplaneposition().to_point()
            crowd_heatmap_output.cell_size_m = geographic_area.cell_size_m
            crowd_heatmap_output.num_cols = density_matrix.shape[1]
            crowd_heatmap_output.num_rows = density_matrix.shape[0]
            crowd_heatmap_output.global_people_counting = total_number_people
            crowd_heatmap_output.is_transferred = False
            crowd_heatmap_output.confidence_level = 0.7
            crowd_heatmap_output.ground_plane_orientation = 0
            crowd_heatmap_output.localization_counter_active = 0
            crowd_heatmap_output.computation_strategy = CrowdHeatmapOutput.LABEL_WRISTBAND

            # FIXME: RESTORE
            crowd_heatmap_output.observation_list = \
                Processing.extract_field_observations_id_crowdheatmap(list_observations=list_observations)

            # FIXME: RESTORE
            if crowd_heatmap_output.observation_list:
                crowd_heatmap_output.localization_counter_active = len(crowd_heatmap_output.observation_list)

            crowd_heatmap_output.sw_run_id = CachedComponents.get_sw_running_current_id()

            crowd_heatmap_output.localization_counter_registered = \
                CachedComponents.get_counter_datastreams_registered(datastream_feature=LabelObservationType.LABEL_OBSTYPE_LOCALIZATION)

            logger.info('Processing crowd_heatmap_output generated (TO BE SAVED), time: {0}, global_counting: {1}'
                        .format(timestamp.isoformat(),
                                crowd_heatmap_output.global_people_counting))

            return crowd_heatmap_output

        except Exception as ex:
            logger.error('Exception create_crowdheatmap_record: {}'.format(ex))
            return None

    @staticmethod
    def associated_localization_crowdheatmapoutput_post(list_localization: List[Localization],
                                                        crowd_heatmap_output: CrowdHeatmapOutput) -> List[Localization]:
        try:
            if not list_localization:
                return False

            if not crowd_heatmap_output:
                return False

            for localization in list_localization:
                localization.crowd_heatmap_associated = crowd_heatmap_output.id
                localization.is_processed = True
                localization.save()

            return list_localization

        except Exception as ex:
            logger.error('associated_localization_crowdheatmapoutput_post Exception; {}'.format(ex))
            return None

    @staticmethod
    def create_random_matrix(zero_matrix: np.matrix) -> np.matrix:
        try:
            return_matrix = zero_matrix

            size = return_matrix.shape

            max_elem_notzero = random.randint(a=1, b=(size[0]*size[1]))
            count_elem_notzero = 0

            for index_row in range(0, size[0]):
                for index_col in range(0, size[0]):
                    return_matrix[index_row, index_col] = random.randint(a=1, b=20)
                    count_elem_notzero += 1
                    if count_elem_notzero == max_elem_notzero:
                        return return_matrix
            return return_matrix
        except Exception as ex:
            logger.error('create_random_matrix Exception: {}'.format(ex))
            return zero_matrix

    @staticmethod
    def calculate_random_crowd_heatmap(monitoring_area: MonitoringArea) -> bool:
        try:
            if not monitoring_area:
                return False

            timestamp = datetime.now(tz=pytz.utc)
            timestampStr = timestamp.strftime("%d-%b-%Y (%H:%M:%S.%f)")

            logger.info('Processing Localization without Localization timestamp: {0}'.format(timestampStr))

            ground_plane_pos_geo = GeoPosition.point_to_geoposition(point=monitoring_area.ground_plane_position,
                                                                    request_ecef_conv=True)
            ground_plane_pos_geo.consolidate_calculation()

            geographic_area = GeographicRectangleArea(ground_plane_position=ground_plane_pos_geo,
                                                      size_x_m=monitoring_area.horizontal_size_m,
                                                      size_y_m=monitoring_area.vertical_size_m,
                                                      cell_size_m=monitoring_area.cell_size_m
                                                      )

            density_matrix = CrowdHeatmapCalculation.create_startup_densitymatrix(geographic_area=geographic_area)

            if density_matrix.size == 0:
                logger.error('processing_localization Unable to Create DensityMatrix. Exit')
                return False

            density_matrix = Processing.create_random_matrix(zero_matrix=density_matrix)

            crowd_heatmap_output = Processing.create_crowdheatmap_record(pilot_name=monitoring_area.pilot_name,
                                                                         timestamp=timestamp,
                                                                         geographic_area=geographic_area,
                                                                         density_matrix=density_matrix,
                                                                         list_observations=list(),
                                                                         total_number_people=density_matrix.sum())

            if not crowd_heatmap_output:
                logger.error('processing_localization Unable to Perform Computation')
                return False

            crowd_heatmap_output.save()

            CachedComponents.notify_new_crowdheatmapoutput(id=crowd_heatmap_output.id)

            logger.info('Processing_localization New CrowdHeatmapOutput, ID: {0}'.format(crowd_heatmap_output.id))

            return True
        except Exception as ex:
            logger.error('calculate_random_crowd_heatmap Exception:{0}'.format(ex))
            return False

    @staticmethod
    def calculate_empty_crowd_heatmap(monitoring_area: MonitoringArea) -> bool:
        try:
            if not monitoring_area:
                return False

            timestamp = datetime.now(tz=pytz.utc)
            timestampStr = timestamp.strftime("%d-%b-%Y (%H:%M:%S.%f)")

            logger.info('Processing Localization without Localization timestamp: {0}'.format(timestampStr))

            ground_plane_pos_geo = GeoPosition.point_to_geoposition(point=monitoring_area.ground_plane_position,
                                                                    request_ecef_conv=True)
            ground_plane_pos_geo.consolidate_calculation()

            geographic_area = GeographicRectangleArea(ground_plane_position=ground_plane_pos_geo,
                                                      size_x_m=monitoring_area.horizontal_size_m,
                                                      size_y_m=monitoring_area.vertical_size_m,
                                                      cell_size_m=monitoring_area.cell_size_m
                                                      )

            density_matrix = CrowdHeatmapCalculation.create_startup_densitymatrix(geographic_area=geographic_area)

            if density_matrix.size == 0:
                logger.error('processing_localization Unable to Create DensityMatrix. Exit')
                return False

            crowd_heatmap_output = Processing.create_crowdheatmap_record(pilot_name=monitoring_area.pilot_name,
                                                                       timestamp=timestamp,
                                                                       geographic_area=geographic_area,
                                                                       density_matrix=density_matrix,
                                                                       list_observations=list(),
                                                                       total_number_people=density_matrix.sum())

            if not crowd_heatmap_output:
                logger.error('processing_localization Unable to Perform Computation')
                return False

            crowd_heatmap_output.save()

            CachedComponents.notify_new_crowdheatmapoutput(id=crowd_heatmap_output.id)

            logger.info('Processing_localization New CrowdHeatmapOutput, ID: {0}'.format(crowd_heatmap_output.id))

            return True
        except Exception as ex:
            logger.error('calculate_empty_crowd_heatmap Exception:{0}'.format(ex))
            return False

    @staticmethod
    def processing_localization(list_observations: List[Localization], monitoring_area: MonitoringArea) -> bool:
        try:
            if not monitoring_area:
                return False

            if not list_observations:
                logger.info('ProcessingLocalization No Unprocessed Localization Found')
                return False

            timestamp = Processing.get_timestamp(list_localization=list_observations)
            timestampStr = timestamp.strftime("%d-%b-%Y (%H:%M:%S.%f)")
            ground_plane_pos_geo = GeoPosition.point_to_geoposition(point=monitoring_area.ground_plane_position,
                                                                    request_ecef_conv=True)
            ground_plane_pos_geo.consolidate_calculation()

            logger.info('Processing Localization with {0} Localization timestamp: {1}'.format(str(len(list_observations)),
                                                                                              timestampStr))

            geographic_area = GeographicRectangleArea(ground_plane_position=ground_plane_pos_geo,
                                                      size_x_m=monitoring_area.horizontal_size_m,
                                                      size_y_m=monitoring_area.vertical_size_m,
                                                      cell_size_m=monitoring_area.cell_size_m
                                                      )

            list_positions = Processing.get_list_position(localization_list=list_observations)

            logger.info('PROCESSING_LOCALIZATION Start effective processing, Counter Position: {}'.format(len(list_positions)))
            (density_matrix, list_enu_distance, list_positions_outsidearea) = \
                CrowdHeatmapCalculation.calculate_densitymatrix_from_positions(list_position=list_positions,
                                                                               geographic_area=geographic_area)
            if density_matrix.size == 0:
                logger.error('processing_localization Unable to Create DensityMatrix. Exit')
                return False
            logger.info('PROCESSING_LOCALIZATION End Effective Processing')

            global_people_counting = density_matrix.sum()

            crowd_heatmap_output = Processing.create_crowdheatmap_record(pilot_name=monitoring_area.pilot_name,
                                                                       timestamp=timestamp,
                                                                       geographic_area=geographic_area,
                                                                       density_matrix=density_matrix,
                                                                       list_observations=list_observations,
                                                                       total_number_people=global_people_counting)

            if not crowd_heatmap_output:
                logger.error('processing_localization Unable to Perform Computation')
                return False

            crowd_heatmap_output.save()
            Processing.associated_localization_crowdheatmapoutput_post(list_localization=list_observations,
                                                                       crowd_heatmap_output=crowd_heatmap_output)
            CachedComponents.notify_new_crowdheatmapoutput(id=crowd_heatmap_output.id)

            logger.info('Processing_localization New CrowdHeatmapOutput, ID: {0}'.format(crowd_heatmap_output.id))

            return True
        except Exception as ex:
            logger.error('processing_localization Exception:{0}'.format(ex))
            return False

    @staticmethod
    def arrange_densitymatrix_correctformat(crowd_density_element: CrowdDensityLocalObservation) -> np.matrix:
        try:
            return crowd_density_element.density_map
        except Exception as ex:
            return np.matrix(data=[])

    @staticmethod
    def createfake_queuedetectionalert() -> List[QueueDetectionAlert]:
        try:
            # TODO: To be implemented
            return None
        except Exception as ex:
            logger.error('createfake_queuedetectionalert Exception:{0}'.format(ex))
            return False

    @staticmethod
    def convert_catalogregions_to_list_queuedetection(catalog_regions: Dict[int, GroupRegionsAdiacentCells],
                                                      camera_registration: CameraRegistration,
                                                      device_id: str = str(),
                                                      obs_iot_id: str = str(),
                                                      mean_value_filter: int = 0,
                                                      start_id_number: int = 0) \
            -> List[QueueDetectionAlert]:
        try:
            if not catalog_regions:
                return None

            list_queuedetectionalert = list()

            list_mean = list(catalog_regions.keys())
            list_mean.sort()

            for mean_people in list_mean:
                if mean_people < mean_value_filter:
                    logger.info('convert_catalogregions_to_list_queuedetection Filter QueueDetectionAlert with mean: {}'.format(mean_people))
                    continue

                logger.info('convert_catalogregions_to_list_queuedetection mean count queue: {}'.format(mean_people))

                group_region = catalog_regions[mean_people]

                if not group_region or group_region.empty():
                    logger.info('convert_catalogregions_to_list_queuedetection group_region empty')
                    continue

                logger.info('convert_catalogregions_to_list_queuedetection group_region count: {}'.format(len(group_region)))

                for region in group_region.get_listregions():
                    if not region:
                        continue

                    logger.debug('convert_catalogregions_to_list_queuedetection single queue detection creation...')
                    single_queue_detection = QueueDetectionAlert()
                    single_queue_detection.obs_iot_id = obs_iot_id
                    single_queue_detection.qsma_id = "{0}/QSA_ID{1}".format(device_id,
                                                                            start_id_number)
                    single_queue_detection.device_id = device_id
                    single_queue_detection.initialize_status()

                    single_queue_detection.set_region_queue(region_queue=region,
                                                            camera_registration=camera_registration)

                    single_queue_detection.mean_people = mean_people
                    single_queue_detection.set_timestamp(timestamp=datetime.datetime.now(tz=pytz.utc))
                    single_queue_detection.save()

                    CachedComponents.save_queuedetectionalert_id(queue_detection_alert_id=single_queue_detection.qda_id)

                    list_queuedetectionalert.append(single_queue_detection)

                    logger.info('convert_catalogregions_to_list_queuedetection crowd_density_event,'
                                'New Queue Event, QDA_ID: {}'.format(single_queue_detection.qda_id))

                    start_id_number += 1

            return list_queuedetectionalert
        except Exception as ex:
            print('convert_catalogregions_to_list_queuedetection Exception: {}'.format(ex))
            return None

    @staticmethod
    def processing_crowd_density_finding_queuedetection(crowd_density_list: List[CrowdDensityLocalObservation]) \
            -> List[QueueDetectionAlert]:
        try:
            logger.info('processing_crowd_density_finding_queuedetection called')

            list_return = list()

            start_id_number = 0

            for crowd_density_event in crowd_density_list:
                if not crowd_density_event or not crowd_density_event.get_cameraregistration():
                    continue

                catalog_region_meanpeople = QueueDetectionAlgorithm.find_queueshape_areas(density_map=crowd_density_event.density_map,
                                                                                          min_cell_count=3)

                if not catalog_region_meanpeople:
                    continue

                list_queuedetectionalert = Processing.convert_catalogregions_to_list_queuedetection(
                    catalog_regions=catalog_region_meanpeople,
                    device_id=crowd_density_event.device_id,
                    obs_iot_id=crowd_density_event.get_obs_iot_id(),
                    camera_registration=crowd_density_event.get_cameraregistration(),
                    start_id_number=start_id_number)

                if not list_queuedetectionalert:
                    continue

                list_return.extend(list_queuedetectionalert)
                start_id_number += len(list_queuedetectionalert)

            return list_return
        except Exception as ex:
            logger.error('processing_crowd_density_finding_queuedetection Exception: {}'.format(ex))
            return None

    # FIXME: Revision of this method is suggested
    @staticmethod
    def real_processing_task(last_catalog_observation: Dict[str, List[ObservableGeneric]],
                             monitoring_area: MonitoringArea,
                             list_output_requested: List[OutputMessageType]) -> bool:
        try:
            if not last_catalog_observation:
                return False

            counter_processing_success = 0

            for type_observable_label in last_catalog_observation.keys():
                catalog_observation = last_catalog_observation[type_observable_label]

                if not catalog_observation:
                    continue

                if type_observable_label == LabelObservationType.LABEL_OBSTYPE_CROWDDENSITY:

                    if OutputMessageType.OUTPUT_MESSAGE_TYPE_QUEUEDETECTIONALERT not in list_output_requested:
                        continue

                    crowd_density_list = CrowdDensityLocalObservation.cast_listobservables_to_list_crowddensitylocal(
                        list_observables=catalog_observation
                    )
                    logger.info('real_processing_task CrowdDensityLocal Global QueueDetection Algorithm')
                    list_queue_detection_alert = \
                        Processing.processing_crowd_density_finding_queuedetection(
                            crowd_density_list=crowd_density_list
                        )
                    if list_queue_detection_alert:
                        logger.info('real_processing_task CrowdDensityLocal Found Queue Alert to send')
                        CachedComponents.increase_counter_output(output_type=OutputMessageType.OUTPUT_MESSAGE_TYPE_QUEUEDETECTIONALERT,
                                                                 increase=len(list_queue_detection_alert))
                        counter_processing_success += 1

                elif LabelObservationType.LABEL_OBSTYPE_LOCALIZATION in last_catalog_observation:
                    if OutputMessageType.OUTPUT_MESSAGE_TYPE_CROWDHEATMAPOUTPUT not in list_output_requested:
                        continue

                    if not monitoring_area:
                        return False

                    test_processing = \
                        Processing.processing_localization(list_observations=catalog_observation,
                                                           monitoring_area=monitoring_area)

                    if test_processing:
                        counter_processing_success += 1
                        CachedComponents.increase_counter_output(
                            output_type=OutputMessageType.OUTPUT_MESSAGE_TYPE_CROWDHEATMAPOUTPUT,
                            increase=1)

            return_processing = False
            if counter_processing_success > 0:
                return_processing = True

            logger.info('real_processing_task Elaboration CounterSuccess: {}'.format(counter_processing_success))

            return return_processing
        except Exception as ex:
            logger.error('Processing real_processing_task Exception:{0}'.format(ex))
            Processing.flag_get_single_execution = False
            return False
