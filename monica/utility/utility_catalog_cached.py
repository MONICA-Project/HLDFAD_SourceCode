from jobs.cache_redis import CachedComponents, CacheRedisAdapter
from general_types.virtual_classes import ObservableGeneric
from general_types.label_ogc import LabelObservationType
from jobs.models import DeviceRegistration, DeviceRegistrationAdapter
# FIXME: Localization to be reviewed
from typing import List, Dict
import logging
from entities.datastream_topic_adapter import DatastreamTopicAdapter
import datetime

logger = logging.getLogger('textlogger')


class UtilityCatalogCached:
    LABEL_DICTIONARY_OBS_ALREADYUSED = 'LABEL_DICTIONARY_OBS_BLACKLIST_MAIN'
    LABEL_DICTIONARY_OBSERVABLE_TO_BACKUP = 'DICTIONARY_OBS_TO_BACKUP'
    LABEL_DICTIONARY_OBSERVABLE_NEW = 'DICTIONARY_OBSERVABLE_NEW'
    LABEL_DICTIONARY_TOPICS = 'SERVICEOBSERVATION_DICTIONARY_TOPICS'
    LABEL_DICTIONARY_DEVICE_REGISTRATION = 'DICTIONARY_DEVICEREGISTRATION'

    @staticmethod
    def initialize_catalog() -> bool:
        try:
            CacheRedisAdapter.initialize()

            CacheRedisAdapter.dictionary_create(label_info=UtilityCatalogCached.LABEL_DICTIONARY_TOPICS)
            CacheRedisAdapter.dictionary_create(label_info=UtilityCatalogCached.LABEL_DICTIONARY_DEVICE_REGISTRATION)

            UtilityCatalogCached.configure_catalog_observable_backup([LabelObservationType.LABEL_OBSTYPE_LOCALIZATION])

            return True

        except Exception as ex:
            logger.error('initialize_catalog Exception: {}'.format(ex))
            return False

    @staticmethod
    def add_device_registration(device_registration: DeviceRegistration) -> bool:
        try:
            if not device_registration:
                return False

            CachedComponents.checkandset_maxiotid(observable_type=device_registration.get_obs_type(),
                                                  iot_id=device_registration.get_datastream_id())

            return CacheRedisAdapter.dictionary_update_value(label_info=UtilityCatalogCached.LABEL_DICTIONARY_DEVICE_REGISTRATION,
                                                             key=device_registration.get_datastream_id(),
                                                             value=device_registration)
        except Exception as ex:
            logger.error('UtilityCatalogCached add_device_registration Exception: {}'.format(ex))
            return False

    @staticmethod
    def get_device_registration(datastream_id: str) -> DeviceRegistration:
        try:
            if not datastream_id:
                return None

            elem_read = CacheRedisAdapter.dictionary_get_value(label_info=UtilityCatalogCached.LABEL_DICTIONARY_DEVICE_REGISTRATION,
                                                               key=datastream_id,
                                                               type_value=DeviceRegistration)

            return elem_read
        except Exception as ex:
            logger.error('UtilityCatalogCached add_device_registration Exception: {}'.format(ex))
            return False

    @staticmethod
    def configure_catalog_observable_backup(label_list_types: List[str]):
        try:
            CacheRedisAdapter.dictionary_create(label_info=UtilityCatalogCached.LABEL_DICTIONARY_OBSERVABLE_TO_BACKUP)

            for type_observable in label_list_types:
                label_store = UtilityCatalogCached.LABEL_DICTIONARY_OBSERVABLE_TO_BACKUP+type_observable
                CacheRedisAdapter.dictionary_update_value(label_info=UtilityCatalogCached.LABEL_DICTIONARY_OBSERVABLE_TO_BACKUP,
                                                          key=type_observable,
                                                          value=label_store)

        except Exception as ex:
            logger.error('configure_catalog_observable_backup Exception: {}'.format(ex))

    @staticmethod
    def set_catalog_observable_backup(catalog_observable: Dict[str, List[ObservableGeneric]]) -> bool:
        try:
            if not catalog_observable:
                return False

            for type_observable in catalog_observable:
                UtilityCatalogCached.set_list_obstobackup(type_observable=type_observable,
                                                          list_obs_to_backup=catalog_observable[type_observable])

            return True
        except Exception as ex:
            logger.error('set_catalog_observable_backup Exception: {}'.format(ex))
            return False

    @staticmethod
    def set_list_obstobackup(type_observable: str, list_obs_to_backup: List[ObservableGeneric]) -> bool:
        try:
            label_list = UtilityCatalogCached.LABEL_DICTIONARY_OBSERVABLE_TO_BACKUP + type_observable

            return CacheRedisAdapter.set_cache_info(label_info=label_list,
                                                    data=list_obs_to_backup)
        except Exception as ex:
            logger.error('set_list_obstobackup Exception: {}'.format(ex))
            return False

    @staticmethod
    def get_list_obstobackup() -> List[ObservableGeneric]:
        try:
            dictionary_type_observable = \
                CacheRedisAdapter.dictionary_get_all(label_info=UtilityCatalogCached.LABEL_DICTIONARY_OBSERVABLE_TO_BACKUP,
                                                     type_value=str)

            if not dictionary_type_observable:
                return None

            list_return = list()

            for type_observable in dictionary_type_observable:

                if dictionary_type_observable[type_observable] is None:
                    continue

                list_partial = CacheRedisAdapter.get_cached_info(label_info=dictionary_type_observable[type_observable],
                                                                 type_data=list)

                if not list_partial:
                    continue

                list_return.extend(list_partial)
            return list_return

        except Exception as ex:
            logger.error('get_dictionary_specific_observable Exception: {}'.format(ex))
            return None

    @staticmethod
    def confirm_obs_backup() -> bool:
        try:
            dictionary_type_observable = CacheRedisAdapter.\
                dictionary_get_all(label_info=UtilityCatalogCached.LABEL_DICTIONARY_OBSERVABLE_TO_BACKUP,
                                   type_value=str)

            if not dictionary_type_observable:
                return None

            for type_observable in dictionary_type_observable:

                if dictionary_type_observable[type_observable] is None:
                    continue

                CacheRedisAdapter.remove_cache_info(label_info=dictionary_type_observable[type_observable])

            return True
        except Exception as ex:
            logger.error('get_dictionary_specific_observable Exception: {}'.format(ex))
            return False

    @staticmethod
    def get_dictionary_name(label_type_observable: str):
        return '{0}_{1}'.format(UtilityCatalogCached.LABEL_DICTIONARY_OBSERVABLE_NEW,
                                label_type_observable)

    @staticmethod
    def append_new_observable(label_type_observable: str, observable: ObservableGeneric) -> bool:
        try:
            if not observable:
                return False

            return CacheRedisAdapter.dictionary_update_value(label_info=UtilityCatalogCached.get_dictionary_name(label_type_observable),
                                                             key=observable.get_label_cache(),
                                                             value=observable)
        except Exception as ex:
            logger.error('UtilityCatalogCache append_new_observable Exception: {}'.format(ex))
            return False

    @staticmethod
    def get_complete_dictionary_observables(list_type_observables: List[str]) -> Dict[str, ObservableGeneric]:
        try:
            if not list_type_observables:
                logger.warning('UtilityCatalogCache get_complete_dictionary_observables list_type_observable is None')
                return None

            dict_return = dict()

            for type_observable in list_type_observables:
                dict_observable_type = \
                    CacheRedisAdapter.dictionary_get_all(label_info=UtilityCatalogCached.get_dictionary_name(type_observable),
                                                         type_value=ObservableGeneric)
                if not dict_observable_type:
                    logger.info('UtilityCatalogCache get_complete_dictionary_observables not available for type_obs: {}'.format(type_observable))
                    continue

                logger.info('UtilityCatalogCache get_complete_dictionary_observables available for type_obs: {0}, '
                            'counter_elements: {1}'.format(type_observable,
                                                           len(dict_observable_type)))

                dict_return[type_observable] = dict_observable_type

            return dict_return
        except Exception as ex:
            logger.error('UtilityCatalogCache: get_complete_dictionary_observables Exception: {}'.format(ex))
            return None

    @staticmethod
    def get_last_observable(label_observable: str) -> ObservableGeneric:
        try:
            return CacheRedisAdapter.get_cached_info(label_info=label_observable,
                                                     type_data=ObservableGeneric)
        except Exception as ex:
            logger.error('get_mostrecent_observable Exception: {}'.format(ex))
            return None

    # @staticmethod
    # def get_observation_catalog(catalog_datastreams: Dict[str, List[DatastreamTopicAdapter]]) \
    #         -> Dict[str, List[ObservableGeneric]]:
    #     try:
    #         catalog_observation = dict()
    #         for subject in catalog_datastreams:
    #             list_observation_subject = \
    #                 UtilityCatalogCached.get_observations_catalog(list_datastreams_subject=catalog_datastreams[subject])
    #
    #             if not list_observation_subject:
    #                 continue
    #
    #             catalog_observation[subject] = list_observation_subject
    #
    #             UtilityCatalogCached.set_list_obstobackup(type_observable=subject,
    #                                                       list_obs_to_backup=list_observation_subject)
    #
    #         return catalog_observation
    #     except Exception as ex:
    #         logger.error('get_observation_catalog Exception: {}'.format(ex))
    #         return None

    @staticmethod
    def check_observable_new(dictionary_obs_time: Dict[str, datetime.datetime], observable: ObservableGeneric) -> bool:
        try:
            if not observable:
                return False

            if not dictionary_obs_time:
                return True

            if observable.get_label_cache() not in dictionary_obs_time \
                    or not dictionary_obs_time[observable.get_label_cache()]:
                return True

            timestamp_prev_obs = dictionary_obs_time[observable.get_label_cache()]
            timestamp_curr_obs = observable.get_timestamp()

            if (timestamp_curr_obs - timestamp_prev_obs).total_seconds() <= 0:
                return False

            return True
        except Exception as ex:
            logger.error('check_observable_new {}'.format(ex))
            return True

    @staticmethod
    def get_complete_list_mqtttopics(list_datastreams_subject: List[DatastreamTopicAdapter]) -> List[str]:
        try:
            if not list_datastreams_subject:
                return None
            list_topics = list()

            for datastream in list_datastreams_subject:
                list_topics.append(datastream.topic_associated)

            return list_topics
        except Exception as ex:
            logger.error('check_observable_new {}'.format(ex))
            return None

    @staticmethod
    def get_observationlist_specifictype(type_observable: str,
                                         list_mqtttopics_admitted: List[str],
                                         dictionary_singletype_observables: Dict[str, ObservableGeneric],
                                         dictionary_obs_time: Dict[str, datetime.datetime]) -> List[ObservableGeneric]:

        list_observable_singletype = list()

        for mqtt_topic in dictionary_singletype_observables:
            single_observation = dictionary_singletype_observables[mqtt_topic]

            if not single_observation:
                logger.info('UtilityCatalogCache get_observationlist_specifictype not observable')
                continue

            # if not UtilityCatalogCached.check_observable_new(dictionary_obs_time=dictionary_obs_time,
            #                                                  observable=single_observation):
            #     continue

            list_observable_singletype.append(single_observation)

        return list_observable_singletype

    @staticmethod
    def update_observables_timestamp(catalog_observable: Dict[str, List[ObservableGeneric]],
                                     dictionary_obs_time: Dict[str, datetime.datetime]) -> bool:
        try:
            if not catalog_observable:
                return False

            counter_changes = 0

            for type_observable in catalog_observable:
                list_observable = catalog_observable[type_observable]

                if not list_observable:
                    continue

                for observable in list_observable:
                    if not observable:
                        continue

                    dictionary_obs_time[observable.get_label_cache()] = observable.get_timestamp()
                    counter_changes += 1

            if counter_changes == 0:
                return False

            logger.info('UtilityCatalogCached Updated Dictionary ObsTimestamps {} Elements Changed'
                        .format(counter_changes))
            return CachedComponents.update_dictionary_observable_timestamps(dictionary_obs_timestamp=dictionary_obs_time)
        except Exception as ex:
            logger.error('UtilityCatalogCached Updated Dictionary ObsTimestamp Exception: {}'.format(ex))
            return False

    @staticmethod
    def get_observations_catalog(catalog_datastreams: Dict[str, List[DatastreamTopicAdapter]]) \
            -> Dict[str, List[ObservableGeneric]]:
        try:
            if not catalog_datastreams:
                logger.warning('UtilityCatalogCached CatalogDatastream is Empty')
                return None

            catalog_observables = dict()

            dictionary_obs_time = CachedComponents.get_dictionary_observable_timestamps()

            if not dictionary_obs_time:
                dictionary_obs_time = dict()

            catalog_all_observables = \
                UtilityCatalogCached.get_complete_dictionary_observables(list_type_observables=catalog_datastreams.keys())

            if not catalog_all_observables:
                logger.info('UtilityCatalogCached No CATALOG OBSERVABLE FOUND')
                return None

            for type_observable in catalog_all_observables:
                if type_observable not in catalog_datastreams:
                    logger.info('UtilityCatalogCached type_observable: {} not in catalog_datastream'.format(type_observable))
                    continue

                list_datastreams = catalog_datastreams[type_observable]

                if not list_datastreams:
                    logger.info('UtilityCatalogCached NOT list_datastreams')
                    continue

                list_mqtttopics = UtilityCatalogCached.\
                    get_complete_list_mqtttopics(list_datastreams_subject=list_datastreams)

                if not list_mqtttopics:
                    logger.info('UtilityCatalogCached NO list_mqtt_topic associated to list_datastreams type_obs: {}'.format(type_observable))
                    continue

                list_observable_singletype = UtilityCatalogCached.\
                    get_observationlist_specifictype(type_observable=type_observable,
                                                     list_mqtttopics_admitted=list_mqtttopics,
                                                     dictionary_singletype_observables=catalog_all_observables[type_observable],
                                                     dictionary_obs_time=dictionary_obs_time)

                if not list_observable_singletype:
                    logger.info('UtilityCatalogCached NOT list_observable_singletype type_observable: {}'.format(type_observable))
                    continue

                catalog_observables[type_observable] = list_observable_singletype

            UtilityCatalogCached.update_observables_timestamp(catalog_observable=catalog_observables,
                                                              dictionary_obs_time=dictionary_obs_time)

            return catalog_observables
        except Exception as ex:
            logger.info('UtilityCatalogCached get_observations_catalog Exception: {}'.format(ex))
            return None

    @staticmethod
    def store_catalog_datastreams(catalog_datastreams: Dict[str, List[DatastreamTopicAdapter]]):
        try:
            if not catalog_datastreams:
                return False

            for subject in catalog_datastreams:
                list_datastreams_adapter = catalog_datastreams[subject]
                CacheRedisAdapter.dictionary_create(label_info=subject)

                if not list_datastreams_adapter:
                    continue

                CacheRedisAdapter.set_cache_info(label_info=subject,
                                                 data=list_datastreams_adapter)

                logger.info('UtilityCatalogCache Store Datastreams Subject: {0} number: {1}'.format(subject,
                                                                                                    len(list_datastreams_adapter)))
        except Exception as ex:
            logger.info('UtilityCatalogCached store_catalog_datastreams Exception: {}'.format(ex))
            return False

    @staticmethod
    def append_topic(single_topic: str) -> bool:
        try:
            CacheRedisAdapter.dictionary_update_value(label_info=UtilityCatalogCached.LABEL_DICTIONARY_TOPICS,
                                                      key=single_topic,
                                                      value=1)
        except Exception as ex:
            logger.info('UtilityCatalogCached append_topic Exception: {}'.format(ex))
            return False

    @staticmethod
    def get_list_topics() -> List[str]:
        try:
            dictionary_topics = CacheRedisAdapter.\
                dictionary_get_all(label_info=UtilityCatalogCached.LABEL_DICTIONARY_TOPICS,
                                   type_value=str)

            list_topics = list()
            for key in dictionary_topics:
                if not key:
                    continue
                list_topics.append(key)

            return list_topics
        except Exception as ex:
            logger.info('UtilityCatalogCached get_list_topics Exception: {}'.format(ex))
            return False

