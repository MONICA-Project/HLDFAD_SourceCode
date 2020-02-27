from jobs.models import MonitoringArea
from shared.settings.appglobalconf import LOCAL_CONFIG
from shared.settings.appstableconf import MONITORING_AREA
from general_types.labelsdictionaries import LocConfLbls
from jobs.processing.processing import Processing
import logging

logger = logging.getLogger('textlogger')


class ProcessingFake:
    @staticmethod
    def creation_empty_processed_info() -> bool:
        try:
            monitoring_area = MonitoringArea(pilot_name=LOCAL_CONFIG[LocConfLbls.LABEL_PILOT_NAME])
            monitoring_area.from_dictionary(dictionary=MONITORING_AREA)

            return Processing.calculate_empty_crowd_heatmap(monitoring_area=monitoring_area)
        except Exception as ex:
            logger.error('ProcessingFake creation_empty_processed_info Exception: {}'.format(ex))
            return False

    @staticmethod
    def creation_random_processed_info() -> bool:
        try:
            monitoring_area = MonitoringArea(pilot_name=LOCAL_CONFIG[LocConfLbls.LABEL_PILOT_NAME])
            monitoring_area.from_dictionary(dictionary=MONITORING_AREA)

            return Processing.calculate_random_crowd_heatmap(monitoring_area=monitoring_area)
        except Exception as ex:
            logger.error('ProcessingFake creation_empty_processed_info Exception: {}'.format(ex))
            return False
