from django import db
from general_types.virtual_classes import OutputMessage
from general_types.modelsenums import OutputMessageType
from jobs.models import MonitoringArea, CrowdHeatmapOutput, SWRunningInfo, QueueDetectionAlert
from django.contrib.gis.geos import MultiPoint
from shared.settings.settingscustompilot import SELECTED_PILOT
from shared.settings.appglobalconf import MONITORING_AREA
from django.contrib.gis.geos import GEOSGeometry
import logging
import datetime
import pytz
from typing import List

logger = logging.getLogger('textlogger')


class UtilityDatabase:
    @staticmethod
    def purge_db_connections():
        db.connections.close_all()

    @staticmethod
    def connection_db_close():
        db.connection.close()

    @staticmethod
    def create_sw_running_info(sw_version: str):
        try:
            sw_running_info = SWRunningInfo(software_version=sw_version)
            sw_running_info.run_id = 1
            sw_running_info.timestamp_start = datetime.datetime.now(tz=pytz.utc)
            sw_running_info.save()

            return 1
        except Exception as ex:
            logger.error('UtilityDatabase create_sw_running Exception: {}'.format(ex))
            return 0

    @staticmethod
    def update_sw_running_timestop(sw_version: str,
                                   timestamp_stop: datetime,
                                   counter_message_output: int,
                                   counter_observables: int,
                                   counter_device_registered: int):
        try:
            sw_running_info = SWRunningInfo.objects.get(software_version=sw_version)

            if not sw_running_info:
                return False

            sw_running_info.timestamp_stop = timestamp_stop   # datetime.datetime.now(tz=pytz.utc)
            sw_running_info.counter_observables = counter_observables
            sw_running_info.counter_message_output = counter_message_output
            sw_running_info.counter_device_registered = counter_device_registered
            sw_running_info.save()

            logger.info('UtilityDatabase update_sw_running_timestop now')

            return True
        except Exception as ex:
            logger.error('UtilityDatabase update_sw_running_timestop exception; {}'.format(ex))
            return False

    @staticmethod
    def get_specific_sw_running_info(sw_version: str) -> SWRunningInfo:
        try:
            return SWRunningInfo.objects.get(software_version=sw_version)
        except Exception as ex:
            logger.info('UtilityDatabase get_specific_sw_running_info: {}'.format(ex))
            return None

    @staticmethod
    def update_get_sw_running_info(sw_version: str) -> int:
        try:
            sw_running_info = UtilityDatabase.get_specific_sw_running_info(sw_version=sw_version)

            if not sw_running_info:
                return UtilityDatabase.create_sw_running_info(sw_version=sw_version)

            sw_running_info.run_id = sw_running_info.run_id + 1
            sw_running_info.timestamp_start = datetime.datetime.now(tz=pytz.utc)
            sw_running_info.save()

            running_id = sw_running_info.run_id

            return running_id
        except Exception as ex:
            logger.error('UtilityDatabase update_sw_running_info exception; {}'.format(ex))
            return UtilityDatabase.create_sw_running_info(sw_version=sw_version)

    @staticmethod
    def extract_localization_ids(localization_list: list):
        try:
            if not localization_list:
                return list()

            list_ids = list()

            for localization in localization_list:
                list_ids.append(localization.key)

            return list_ids
        except Exception as ex:
            return None

    @staticmethod
    def confirm_crowdheatmapoutput_sending(crowd_heatmap_output: CrowdHeatmapOutput) -> bool:
        try:
            if not crowd_heatmap_output:
                return False

            crowd_heatmap_output.is_transferred = True
            crowd_heatmap_output.save()

            logger.info('Provisioning: CrowdHeatmapOutput Sending Confirmation ID: {0}'.format(str(crowd_heatmap_output.id)))

            return True

        except Exception as ex:
            logger.error('Provisioning confirm_crowdheatmapoutput_sending Error: {}'.format(ex))
            return False

    @staticmethod
    def convert_string_to_list_multipoint(string_list_multipoint: str) -> List[MultiPoint]:
        try:
            if not string_list_multipoint:
                return None

            string_list_multipoint = string_list_multipoint.replace('{', '')
            string_list_multipoint = string_list_multipoint.replace('}', '')

            list_string = string_list_multipoint.split(':')

            list_multipoints = list()

            if not list_string:
                return None

            for string_multipoint in list_string:
                if not string_multipoint:
                    continue

                multipoint = GEOSGeometry(geo_input=string_multipoint)

                if not multipoint:
                    continue

                list_multipoints.append(multipoint)

            return list_multipoints
        except Exception as ex:
            logger.error('UtilityDatabase convert_string_to_list_multipoint Exception: {}'.format(ex))
            return None

    @staticmethod
    def get_outputmessage_byid(id: int,
                               outputmessagetype: OutputMessageType) -> OutputMessage:
        try:
            if outputmessagetype == OutputMessageType.OUTPUT_MESSAGE_TYPE_CROWDHEATMAPOUTPUT:
                return CrowdHeatmapOutput.objects.get(id=id)
            elif outputmessagetype == OutputMessageType.OUTPUT_MESSAGE_TYPE_QUEUEDETECTIONALERT:
                queue_detectionalert = QueueDetectionAlert.objects.get(qda_id=id)

                return queue_detectionalert

            return None
        except Exception as ex:
            logger.error('get_outputmessage Exception: {}'.format(ex))
            return None

    @staticmethod
    def get_list_messageoutput_byids(list_ids: List[int], outputmessagetype: OutputMessageType) -> List[OutputMessage]:
        try:
            if not list_ids:
                return None

            list_output_messages = list()

            for id in list_ids:
                output_message = UtilityDatabase.get_outputmessage_byid(id=id,
                                                                        outputmessagetype=outputmessagetype)

                if not output_message:
                    continue

                list_output_messages.append(output_message)

            return list_output_messages
        except Exception as ex:
            logger.error('UtilityDatabase get_list_messageoutput_byids Exception: {}'.format(ex))
            return None

    @staticmethod
    def update_database_startup():
        try:
            if not MONITORING_AREA:
                logger.warning('UpdateDBStartup No MonitoringArea ADDED')
                return

            monitoring_area = MonitoringArea(pilot_name=SELECTED_PILOT)
            monitoring_area.from_dictionary(dictionary=MONITORING_AREA)
            logger.info('UpdateDBStartup Added MonitoringArea Pilot: {}'.format(monitoring_area.to_string()))
        except Exception as ex:
            logger.error('UtilityDatabase update_database_startup Exception; {}'.format(ex))

