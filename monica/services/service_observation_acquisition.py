from jobs.acquisition.messageacquisition import MessageAcquisition
from general_types.virtual_classes import ObservableGeneric
from general_types.label_ogc import LabelObservationType
from utility.utility_catalog_cached import UtilityCatalogCached
from jobs.cache_redis import CachedComponents
import logging
import datetime
import pytz

logger = logging.getLogger('textlogger')


class ServiceObservationAcquisition:
    global_counter_observation = 0

    @staticmethod
    def check_time_validity(observable: ObservableGeneric,
                            timestamp_now: datetime,
                            interval_secs: int) -> bool:
        try:
            if not observable:
                return False

            if interval_secs == -1:
                return True

            timestamp_obs = observable.get_timestamp()

            time_diff_secs = (timestamp_now-timestamp_obs).total_seconds()

            if time_diff_secs > interval_secs:
                logger.info("ServiceObsAcqu Obs Too Old: {0} {1} {2}"
                            .format(str(time_diff_secs),
                                    str(observable.get_observable_id()),
                                    str(observable.get_device_id()),
                                    observable.get_timestamp()))
                return False

            return True
        except Exception as ex:
            logger.error("ServiceObsAcqu check_time_validity Exception: {}".format(ex))
            return True

    @staticmethod
    def check_observable_type_admitted(observable: ObservableGeneric) -> bool:
        try:
            if not observable:
                return False

            if observable.get_type_observable() == LabelObservationType.LABEL_OBSTYPE_LOCALIZATION:
                return True

            elif observable.get_type_observable() == LabelObservationType.LABEL_OBSTYPE_CROWDDENSITY:
                return True

            return False
        except NotImplementedError:
            return False

    @staticmethod
    def validate_and_save_observation_cache(observable: ObservableGeneric,
                                            associated_topic: str,
                                            interval_validity_secs: int) -> bool:
        try:
            if not observable:
                logger.info('ServiceObsAqu Failed (observable is None)')
                return False

            if not ServiceObservationAcquisition.check_observable_type_admitted(observable=observable):
                logger.info("ServiceObsAcqu Type Observable Not Admitted: {}"
                            .format(observable.get_type_observable()))
                return False

            if not ServiceObservationAcquisition.check_if_observable_updated(observable=observable,
                                                                             associated_topic=associated_topic,
                                                                             interval_validity_secs=interval_validity_secs):
                logger.info('ServiceObsAcqu Observable {} NOT Updated. Discarded'.format(observable.get_device_id()))
                return False

            if not ServiceObservationAcquisition.update_cache_element_topic(observable=observable,
                                                                            associated_topic=associated_topic):
                logger.info('ServiceObsAcqu Observable {} update_cache_element_topic Failed. Discarded'.format(observable.get_device_id()))
                return False

            logger.debug('ServiceObsAcqu validate_and_save_observation_cache associated topic: {0}, datastream_id: {1}'
                        .format(associated_topic,
                                observable.get_datastream_id()))

            return True
        except Exception as ex:
            logger.error("ServiceObsAcqu validate_and_save_observation_cache Exception: {}".format(ex))
            return False

    @staticmethod
    def check_if_observable_updated(observable: ObservableGeneric,
                                    associated_topic: str,
                                    interval_validity_secs: int):
        try:
            if not observable:
                return False

            if not ServiceObservationAcquisition.check_time_validity(observable=observable,
                                                                     timestamp_now=datetime.datetime.now(tz=pytz.utc),
                                                                     interval_secs=interval_validity_secs):
                return False

            return True
        except Exception as ex:
            logger.error("ServiceObsAcqu check_if_observable_updated Exception: {}".format(ex))
            return False

    @staticmethod
    def update_cache_element_topic(observable: ObservableGeneric,
                                   associated_topic: str) -> bool:
        try:
            if not observable:
                return False

            return UtilityCatalogCached.append_new_observable(label_type_observable=associated_topic,
                                                              observable=observable)
        except Exception as ex:
            logger.error('ServiceObsAcqu update_cache_element_topic Exception: {}'.format(ex))
            return False

    @staticmethod
    def acquire_single_observation(json_observation: dict,
                                   associated_topic: str,
                                   pilot_name: str = '',
                                   observable_id: int = 0,
                                   running_id: int = 0) -> ObservableGeneric:

        if associated_topic == LabelObservationType.LABEL_OBSTYPE_CROWDDENSITY:
            return MessageAcquisition.crowd_density_local_observation(mqtt_dictionary=json_observation,
                                                                      pilot_name=pilot_name,
                                                                      observable_id=observable_id)
        elif associated_topic == 'GateCountingEstimation':
            return MessageAcquisition.gate_counting_observation(json_observation, pilot_name)
        elif associated_topic == LabelObservationType.LABEL_OBSTYPE_LOCALIZATION:
            return MessageAcquisition.localization_observation(mqtt_dictionary=json_observation,
                                                               pilot_name=pilot_name,
                                                               observable_id=observable_id,
                                                               running_id=running_id)

        return None
