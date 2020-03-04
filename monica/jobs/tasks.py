#!/usr/bin/env python

from shared.celery_settings import app
from celery.signals import celeryd_after_setup

from shared.settings.appstableconf import WP6_DICTIONARY_CATALOGOUTPUTINFO
from general_types.virtual_classes import ObservableGeneric
from general_types.label_ogc import LabelObservationType
from jobs.processing.processing import Processing
from jobs.processing.processing_fake import ProcessingFake
from jobs.cache_redis import CachedComponents
from services.service_catalog_client import ServiceCatalogClient
from services.service_observation_client import ServiceObservationClient
from utility.utility_database import UtilityDatabase
from utility.utility_startup_application import UtilityStartupApplication
from jobs.provisioning.provisioning import Provisioning
from utility.utility_catalog_cached import UtilityCatalogCached
from services.service_updatedatastreams_client import ServiceUpdateDatastreamsClient
from services.service_get_observationGOST import ServiceGetObservationGOST
from utility.utility_settings import UtilitySettings
from utility.utility_sw_update_info import UtilitySWUpdateInfo
from shared.settings.appglobalconf import LOCAL_CONFIG, LIST_UNITTESTS_ENABLED, MONITORING_AREA
from jobs.models import DictionaryHelper, MonitoringArea
from general_types.modelsenums import OutputMessageType
from general_types.labelsdictionaries import LocConfLbls
from shared.settings.default_datastreams import DICTIONARY_OBSERVABLE_TOPICS, RegistrationJSONMaker
from entities.datastream_topic_adapter import HelperDatastreamGenerator
from unittests.unittests_main import UnitTestMain
from typing import List
from sys import exit

import celery

import logging

logger = logging.getLogger('textlogger')


class WorkerTasks(celery.Task):
    """ Implements after return hook to close the invalid connection.
    This way, django is forced to serve a new connection for the next
    task.
    """
    abstract = True

    catalog_datastreams = dict()
    list_datastreams = list()
    flag_debug_launch_singletask = False
    debug_remove_value_increase = 1
    mutex_protectprocessingtask = 0
    alive_counter = 0

    def run(self, *args, **kwargs):
        logging.info('WorkerTasks RUNNING METHOD CALLED')

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        logging.info('{0!r} failed: {1!r}'.format(task_id, exc))

    def after_return(self, *args, **kwargs):
        UtilityDatabase.connection_db_close()

    def on_retry(self, exc, task_id, args, kwargs, einfo):
        logging.info('WorkerTasks ON RETRY METHOD')

    # @classmethod
    # def on_bound(cls, app):
    #     logging.info('RAISED ON BOUND')

    def on_success(self, retval, task_id, args, kwargs):
        logging.info('WorkerTasks SUCCESS ACTIVATION WORKERTASK')

    def shadow_name(self, args, kwargs, options):
        logging.info('WorkerTasks SHADOW NAME')

    @staticmethod
    def backup_observables_remaining(list_output_ids: List[int]):
        try:
            list_observable_to_backup = UtilityCatalogCached.get_list_obstobackup()

            if not list_observable_to_backup:
                return

            for observable in list_observable_to_backup:
                observable.set_output_id(output_id=list_output_ids[0])

            # for observable in list_observable_to_backup:
            #     logger.info('Observable Print: {0}'.format(observable.to_string()))

            list_dictionary = DictionaryHelper.list_to_documents(list_observable_to_backup)

            if not list_dictionary:
                return

            counter_elem_to_backup = len(list_dictionary)

            logger.info('WorkerTask Backup {0} Observable to MongoDB'.format(counter_elem_to_backup))
            # FIXME: DISABLED FOR PILOT EMERGENCY (ENABLE AGAIN!)
            # UtilityMongoDB.initialize()
            # UtilityMongoDB.save_many_observable(collection_json_messages=list_dictionary)
            # UtilityMongoDB.close()

            UtilityCatalogCached.confirm_obs_backup()

        except Exception as ex:
            logger.error('backup_observables_remaining Exception: {}'.format(ex))

    @staticmethod
    def handle_fakeprocessing_queuedetection() -> bool:
        try:
            if LocConfLbls.LABEL_ENABLE_RANDOM_QUEUEDETECTIONALERT not in LOCAL_CONFIG or \
                    not LOCAL_CONFIG[LocConfLbls.LABEL_ENABLE_RANDOM_QUEUEDETECTIONALERT]:
                return False

            if not Processing.createfake_queuedetectionalert():
                return False

            logger.info('WorkingTask generated fake QueueDetectionAlert')

            return True
        except Exception as ex:
            logger.error('WorkingTask handle_fakeprocessing_queuedetection Exception: {}'.format(ex))
            return False

    @staticmethod
    def handle_fakeprocessing_crowdheatmap() -> bool:
        try:
            if LOCAL_CONFIG[LocConfLbls.LABEL_ENABLE_RANDOM_DENSITYMATRIX]:
                if ProcessingFake.creation_random_processed_info():
                    logger.info('TASK ELABORATION REQUEST CALCULATION RANDOM CROWD HEATMAP')
                    return True

            if not LOCAL_CONFIG[LocConfLbls.LABEL_ENABLE_EMPTY_CROWD_HEATMAP]:
                WorkerTasks.request_launch_task_sw_update()
                return True

            if ProcessingFake.creation_empty_processed_info():
                return True

            return False
        except Exception as ex:
            logger.error('WorkingTask handle_fakeprocessing_crowdheatmap Exception: {}'.format(ex))
            return False

    @staticmethod
    def appconf_get_list_expectedoutmessages() -> List[OutputMessageType]:
        if LocConfLbls.LABEL_OUTPUT_MESSAGELIST_SELECTED not in LOCAL_CONFIG or not LOCAL_CONFIG[LocConfLbls.LABEL_OUTPUT_MESSAGELIST_SELECTED]:
            return list()

        return LOCAL_CONFIG[LocConfLbls.LABEL_OUTPUT_MESSAGELIST_SELECTED]

    @staticmethod
    def appconf_checkoutputmessage_required(output_message_type: OutputMessageType) -> bool:
        if LocConfLbls.LABEL_OUTPUT_MESSAGELIST_SELECTED not in LOCAL_CONFIG or not LOCAL_CONFIG[LocConfLbls.LABEL_OUTPUT_MESSAGELIST_SELECTED]:
            return False

        if output_message_type not in LOCAL_CONFIG[LocConfLbls.LABEL_OUTPUT_MESSAGELIST_SELECTED]:
            return False

        return True

    @staticmethod
    def received_notification_new_observation(observable: ObservableGeneric) -> bool:
        try:
            CachedComponents.increase_counter_observable(increase=1)
            if not LOCAL_CONFIG[LocConfLbls.LABEL_ENABLE_IMMEDIATEELABORATION_FEEDBYNUMBEROBS]:
                return False

            if OutputMessageType.OUTPUT_MESSAGE_TYPE_QUEUEDETECTIONALERT in \
                    LOCAL_CONFIG[LocConfLbls.LABEL_OUTPUT_MESSAGELIST_SELECTED] and \
                    observable.get_type_observable() == LabelObservationType.LABEL_OBSTYPE_CROWDDENSITY:

                logger.info('WorkerTask Called request_launch_task_elaboration')
                WorkerTasks.request_launch_task_elaboration()
                return True
            # FIXME: Missing check for request launch task elaboration
            elif OutputMessageType.OUTPUT_MESSAGE_TYPE_CROWDHEATMAPOUTPUT in \
                    LOCAL_CONFIG[LocConfLbls.LABEL_OUTPUT_MESSAGELIST_SELECTED] and \
                    observable.get_type_observable() == LabelObservationType.LABEL_OBSTYPE_LOCALIZATION:

                CachedComponents.increase_counter_observable_localization_unprocessed(increase=1)
                counter_wb_registered = CachedComponents.get_counter_datastreams_registered(datastream_feature=LabelObservationType.LABEL_OBSTYPE_LOCALIZATION)
                counter_unprocessed = CachedComponents.get_counter_observable_localization_unprocessed()

                if counter_unprocessed < counter_wb_registered:
                    return False

                CachedComponents.set_counter_observable_localization_unprocessed(value=0)

                # max_iot_id = CachedComponents.get_maxiotid(observable_type=observable.get_type_observable())
                #
                # if max_iot_id is None:
                #     return False
                #
                # if max_iot_id > observable.get_datastream_id():
                #     return False

                logger.info('WorkerTask Called request_launch_task_elaboration, counter_wb_registered: {0}, counterobsunproc: {1}'.format(counter_wb_registered,
                                                                                                                                          counter_unprocessed))
                WorkerTasks.request_launch_task_elaboration()
                return True

            return False
        except Exception as ex:
            logger.error('WorkerTask received_notification_new_observation Exception: {}'.format(ex))
            return False

    @staticmethod
    def request_launch_task_elaboration():
        try:
            logger.info('WorkerTask request_launch_task_elaboration')
            task_elaboration.apply_async(args=None,
                                         queue='crowd_queue_elaboration',
                                         serializer='json'
                                         )
        except Exception as ex:
            logger.error('WorkerTask request_launch_task_elaboration Exception: {}'.format(ex))

    @staticmethod
    def request_launch_task_provisioning():
        try:
            logger.info('WorkerTask request_launch_task_provisioning')
            task_provisioning.apply_async(args=["{'Prova':1}"],
                                          queue='crowd_queue_provisioning',
                                          serializer='json'
                                          )
        except Exception as ex:
            logger.error('request_launch_task_provisioning Exception: {}'.format(ex))

    @staticmethod
    def request_launch_task_sw_update():
        try:
            logger.info('WorkerTask request_launch_task_sw_update')
            task_sw_update_info.apply_async(args=["{'Prova':1}"],
                                            queue='queue_sw_update_info',
                                            serializer='json')
        except Exception as ex:
            logger.error('request_launch_task_sw_update Exception: {}'.format(ex))

    @staticmethod
    def update_global_servicecatalog() -> bool:
        try:
            if not LOCAL_CONFIG[LocConfLbls.LABEL_BYPASS_BEGINNING_CATALOG_ACQUISITION] or \
                    (not DICTIONARY_OBSERVABLE_TOPICS):
                logger.info('WorkerTask Request Launch Get_Service_Catalog')

                temp_catalog_datastream, \
                temp_list_datastream, \
                flag_update_catalog \
                    = ServiceCatalogClient.get_service_catalog(dict_thing_datastreams=UtilitySettings.get_global_dict_thing_datastream())

                if not flag_update_catalog or not temp_catalog_datastream or not temp_list_datastream:
                    logger.info('WorkerTask Required Exit (NO CATALOG EXTRACTED)')
                    exit()
                    return False

                WorkerTasks. \
                    catalog_datastreams = temp_catalog_datastream

                WorkerTasks. \
                    list_datastreams = temp_list_datastream
            else:
                if DICTIONARY_OBSERVABLE_TOPICS:
                    logger.info('WorkerTasks update_global_servicecatalog VOLUNTARY BYPASS CATALOG ACQUISITION. '
                                'EMULATION DATA HARDCODED')

                    WorkerTasks.catalog_datastreams, \
                    WorkerTasks.list_datastreams = \
                        HelperDatastreamGenerator.\
                            debug_create_datastreams_from_dictionary(specific_argument=LabelObservationType.LABEL_OBSTYPE_LOCALIZATION,
                                                                     dictionary_topics=DICTIONARY_OBSERVABLE_TOPICS)

                    dict_reg_test = RegistrationJSONMaker.get_complete_registrationdevices_dicts()
                    dict_thing = RegistrationJSONMaker.get_dictionary_thing_cdl()
                    prefix_topic = RegistrationJSONMaker.get_prefix_topic()
                    thing_name = RegistrationJSONMaker.get_thing_name()
                    WorkerTasks.list_datastreams = ServiceCatalogClient.get_datastreams_catalog_thing(thing_name=thing_name,
                                                                                                      list_datastreams_json=dict_reg_test,
                                                                                                      list_datastreams_thing=dict_thing,
                                                                                                      prefix_topic=prefix_topic
                                                                                                      )
                    WorkerTasks.catalog_datastreams[LabelObservationType.LABEL_OBSTYPE_CROWDDENSITY] = WorkerTasks.list_datastreams

            logger.info('WorkerTasks update_global_servicecatalog Done')

            if not WorkerTasks.catalog_datastreams:
                logger.info('WorkerTask Required Exit (NO CATALOG EXTRACTED)')
                exit()
                return False

            UtilityCatalogCached.store_catalog_datastreams(WorkerTasks.catalog_datastreams)

            ServiceObservationClient.create_list_mqtt_client(WorkerTasks.list_datastreams)

            logger.info('WorkerTasks Saved Info To Cache. Request Launch Start MQTT Clients')

            ServiceObservationClient.start(mqtt_broker_url=LOCAL_CONFIG[LocConfLbls.LABEL_MQTT_OBSERVATION_URL],
                                           mqtt_broker_port=LOCAL_CONFIG[LocConfLbls.LABEL_MQTT_OBSERVATION_PORT])
            logger.info('WorkerTasks Saved Info To Cache. Launched MQTT Observable')
            ServiceUpdateDatastreamsClient.start(mqtt_broker_url=LOCAL_CONFIG[LocConfLbls.LABEL_MQTT_OBSERVATION_URL],
                                                 mqtt_broker_port=LOCAL_CONFIG[LocConfLbls.LABEL_MQTT_OBSERVATION_PORT])
            logger.info('WorkerTasks Saved Info To Cache. Launched MQTT Datastreams')

            return True
        except Exception as ex:
            logger.error('update_global_servicecatalog Exception: {}'.format(ex))
            return False

    @staticmethod
    def create_fake_output() -> bool:
        try:
            if LocConfLbls.LABEL_ENABLE_RANDOM_OUTPUT not in DICTIONARY_OBSERVABLE_TOPICS:
                return False

            if not DICTIONARY_OBSERVABLE_TOPICS[LocConfLbls.LABEL_ENABLE_RANDOM_OUTPUT]:
                return False

            if WorkerTasks.appconf_checkoutputmessage_required(
                    OutputMessageType.OUTPUT_MESSAGE_TYPE_CROWDHEATMAPOUTPUT):
                if WorkerTasks.handle_fakeprocessing_crowdheatmap():
                    WorkerTasks.request_launch_task_provisioning()
                    return True

            if WorkerTasks.appconf_checkoutputmessage_required(
                    OutputMessageType.OUTPUT_MESSAGE_TYPE_QUEUEDETECTIONALERT):
                if WorkerTasks.handle_fakeprocessing_queuedetection():
                    WorkerTasks.request_launch_task_provisioning()
                    return True

            return False
        except Exception as ex:
            logger.error('WorkerTask create_fake_output {}'.format(ex))
            return False

    @staticmethod
    def handle_task_elaboration() -> bool:
        try:
            if not CachedComponents.check_startupapplication_completed():
                logger.info('TASK ELABORATION BLOCKED (Registration Phase Not Completed)')
                return False

            pilot_name = LOCAL_CONFIG[LocConfLbls.LABEL_PILOT_NAME]

            monitoring_area = MonitoringArea(pilot_name=pilot_name)
            if WorkerTasks.appconf_checkoutputmessage_required(OutputMessageType.OUTPUT_MESSAGE_TYPE_CROWDHEATMAPOUTPUT):
                if not MONITORING_AREA:
                    logger.critical("TASK ELABORATION NOT POSSIBLE MONITORED AREA NOT SPECIFIED")
                    return False

                monitoring_area_dictionary = MONITORING_AREA
                monitoring_area.from_dictionary(dictionary=monitoring_area_dictionary)

            # TODO: Gestire il caso di crowd_density_global multipli
            UtilityDatabase.purge_db_connections()

            logger.info('TASK ELABORATION REQUEST ACTIVATION')

            last_catalog_observation = \
                UtilityCatalogCached.get_observations_catalog(catalog_datastreams=WorkerTasks.catalog_datastreams)

            if not last_catalog_observation:
                logger.info('TaskElaboration Did Not find Any measures')

                return WorkerTasks.create_fake_output()

            logger.info('TASK ELABORATION CALLED')

            if LocConfLbls.LABEL_ENABLE_OBS_IOTIDRETRIEVE in LOCAL_CONFIG and \
                LOCAL_CONFIG[LocConfLbls.LABEL_ENABLE_OBS_IOTIDRETRIEVE]:
                logger.info('WorkerTask Elaboration Asking OBS_IOT_ID retrieve before computation')
                last_catalog_observation = ServiceGetObservationGOST.set_correct_obs_iotid(catalog_observations=last_catalog_observation,
                                                                                           gost_url=LOCAL_CONFIG[LocConfLbls.LABEL_GOST_URL]
                                                                                           )

            if not Processing.real_processing_task(last_catalog_observation=last_catalog_observation,
                                                   monitoring_area=monitoring_area,
                                                   list_output_requested=LOCAL_CONFIG[LocConfLbls.LABEL_OUTPUT_MESSAGELIST_SELECTED]):
                logger.info('TASK real_processing_task FAILED')
                return False

            UtilityCatalogCached.set_catalog_observable_backup(catalog_observable=last_catalog_observation)

            logger.info('TASK ELABORATION SUCCESS')

            return True
        except Exception as ex:
            logger.error('handle_task_elaboration Exception: {}'.format(ex))
            return False


@app.task(bind=True, typing=False, serializer='json', base=WorkerTasks)
def first(self, data):
    try:
        return {"status": True}
    except Exception as ex:
        logger.error('First Task Exception: {}'.format(ex))


@app.task(bind=True, typing=False, serializer='json', base=WorkerTasks)
def check_db(self):
    # TODO
    return {"status": True}


@app.task(bind=True, typing=False, serializer='json', base=WorkerTasks)
def task_sw_update_info(self, data):
    try:
        UtilitySWUpdateInfo.update_sw_info_realtime()
        return {"status": True}
    except Exception as ex:
        logger.error('Task Discover Devices Exception: {}'.format(ex))
        return {"status": False}


@app.task(bind=True, typing=False, serializer='json', base=WorkerTasks)
def task_alive(self):
    try:
        logger.info('TASK ALIVE CALLED Counter: {}'.format(WorkerTasks.alive_counter))

        WorkerTasks.alive_counter += 1

        return {"status": True}
    except Exception as ex:
        logger.error('TASK ALIVE EXCEPTION: {}'.format(ex))
        return {"status": False}


@app.task(bind=True, typing=False, serializer='json', base=WorkerTasks)
def task_elaboration(self):
    try:
        if WorkerTasks.mutex_protectprocessingtask >= 1:
            logger.info('TASK ELABORATION BLOCKED (Another Is Running)')
            return {"status": False}

        WorkerTasks.mutex_protectprocessingtask = 1

        if WorkerTasks.handle_task_elaboration():
            logger.info('TASK ELABORATION SUCCESS. ASKED PROVISIONING')
            WorkerTasks.request_launch_task_provisioning()

        WorkerTasks.mutex_protectprocessingtask = 0

        return {"status": True}
    except Exception as ex:
        WorkerTasks.mutex_protectprocessingtask = 0
        logger.error('task_elaboration Exception: {}'.format(ex))
        return {"status": False}


@app.task(bind=True,
          typing=False,
          serializer='json',
          base=WorkerTasks)
def task_provisioning(self, data):
    try:
        logger.info('TASK PROVISIONING STARTED')
        UtilityDatabase.purge_db_connections()
        Provisioning.real_provisioning_task(list_message_conversions=LOCAL_CONFIG[LocConfLbls.LABEL_OUTPUT_MQTT_LISTTYPES],
                                            list_output_type=LOCAL_CONFIG[LocConfLbls.LABEL_OUTPUT_MESSAGELIST_SELECTED],
                                            username=LOCAL_CONFIG[LocConfLbls.LABEL_OUTPUT_MQTT_BROKER_USERNAME],
                                            password=LOCAL_CONFIG[LocConfLbls.LABEL_MQTT_CLIENT_PASSWORD])

        WorkerTasks.request_launch_task_sw_update()
        # WorkerTasks.backup_observables_remaining(list_output_ids=list_output_ids)

        logger.info('TASK PROVISIONING ENDED')

        return {"status": True}
    except Exception as ex:
        logger.error('Task Provisioning Exception: {}'.format(ex))
        return {"status": False}


@celeryd_after_setup.connect()
def broker_connection(sender, instance, **kwargs):
    try:
        UtilityDatabase.purge_db_connections()

        ServiceObservationClient.on_event_notify_obs = WorkerTasks.received_notification_new_observation

        dictionary_result = UnitTestMain.launch_all_tests(enable_tests=LOCAL_CONFIG[LocConfLbls.LABEL_ENABLE_UNIT_TESTS],
                                                          list_enabled_tests=LIST_UNITTESTS_ENABLED)
        UnitTestMain.print_report(dictionary_test_results=dictionary_result)

        if LOCAL_CONFIG[LocConfLbls.LABEL_ABORT_EXECUTION_AFTERUNITTESTS]:
            logger.info('EXECUTION VOLUNTARY ABORTED AFTER UNIT TESTS EXECUTION')
            return {"status", False}

        UtilityStartupApplication.trace_startup_info()
        UtilityStartupApplication.startup()
        UtilityStartupApplication.adjust_startup_data()

        ServiceCatalogClient.initialize()
        ServiceUpdateDatastreamsClient.initialize(client_id=LOCAL_CONFIG[LocConfLbls.LABEL_MQTT_CLIENT_PAHO_NAME_DATASTREAMUPDATE])
        ServiceObservationClient.initialize(client_id=LOCAL_CONFIG[LocConfLbls.LABEL_MQTT_CLIENT_PAHO_NAME_OBSERVABLES],
                                            username=LOCAL_CONFIG[LocConfLbls.LABEL_MQTT_CLIENT_USERNAME],
                                            password=LOCAL_CONFIG[LocConfLbls.LABEL_MQTT_CLIENT_PASSWORD])

        list_output_messages = LOCAL_CONFIG[LocConfLbls.LABEL_OUTPUT_MESSAGELIST_SELECTED]

        if list_output_messages:
            for output_message in list_output_messages:

                if output_message not in WP6_DICTIONARY_CATALOGOUTPUTINFO.keys():
                    continue

                dictionary_sending = WP6_DICTIONARY_CATALOGOUTPUTINFO[output_message]

                broker_output_info = ServiceCatalogClient.acquire_output_broker_info(request_catalog_url=LOCAL_CONFIG[LocConfLbls.LABEL_WP6_CATALOG_CONNECTIONURL],
                                                                                     service_to_call=LOCAL_CONFIG[LocConfLbls.LABEL_WP6_CATALOG_POSTSERVICERETRIEVEOUTPUTINFO],
                                                                                     request_catalog_port=LOCAL_CONFIG[LocConfLbls.LABEL_WP6_CATALOG_CONNECTIONPORT],
                                                                                     dictionary_message_sent=dictionary_sending)
                if not broker_output_info:
                    logger.warning('UNABLE TO LOAD BROKER INFO. REQUEST EXIT APPLICATION')
                    exit()

                CachedComponents.save_brokeroutput_servicecatalog(broker_output=broker_output_info,
                                                                  output_message_type=output_message)

        if LocConfLbls.LABEL_BYPASS_MQTTINPUTMESSAGEACQUISITION not in LOCAL_CONFIG or \
                not LOCAL_CONFIG[LocConfLbls.LABEL_BYPASS_MQTTINPUTMESSAGEACQUISITION]:
            WorkerTasks.update_global_servicecatalog()
        else:
            logger.info("VOLUNTARY BYPASS MANAGEMENT MQTT INPUT DATA")
            CachedComponents.set_startupapplication_completed()

        if LOCAL_CONFIG[LocConfLbls.LABEL_MINIMUM_ACCEPTED_WRISTBAND_TO_START] > 0 and \
                OutputMessageType.OUTPUT_MESSAGE_TYPE_CROWDHEATMAPOUTPUT in \
                LOCAL_CONFIG[LocConfLbls.LABEL_OUTPUT_MESSAGELIST_SELECTED]:
                    counter_wb_registered = CachedComponents.get_counter_datastreams_registered(
                    datastream_feature=LabelObservationType.LABEL_OBSTYPE_LOCALIZATION)

                    if counter_wb_registered < LOCAL_CONFIG[LocConfLbls.LABEL_MINIMUM_ACCEPTED_WRISTBAND_TO_START]:
                        logger.info('HLDFAD MODULE STOPPED AFTER ACQUISITION FOR INSUFFICIENT NUMBER OF WRISTBAND, '
                                    '{0} against {1} minimum configured'.format(counter_wb_registered,
                                                                                LOCAL_CONFIG[LocConfLbls.LABEL_MINIMUM_ACCEPTED_WRISTBAND_TO_START]))
                        exit()

        logger.info('HLDFAD STARTUP PHASE DONE WITH SUCCESS')

        return {"status", True}
    except Exception as ex:
        logger.error(ex)
        return {"status", False}
