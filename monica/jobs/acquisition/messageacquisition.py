from jobs.models import CrowdDensityLocalObservation, Localization
import logging
from dateutil.parser import isoparse
from utility.utility_catalog_cached import UtilityCatalogCached
from typing import Dict, Any
import json

logger = logging.getLogger('textlogger')


class MessageAcquisition:
    LABEL_DATASTREAM = "Datastream"
    LABEL_IOTID = "@iot.id"
    LABEL_RESULT = "result"
    LABEL_PHENOMENONTIME = "phenomenonTime"

    @staticmethod
    def mics_observation(j_data, pilot_name):
        return

    @staticmethod
    def crowd_density_local_observation(mqtt_dictionary: Dict[str, Any],
                                        pilot_name: str,
                                        observable_id: int) -> CrowdDensityLocalObservation:
        try:
            if MessageAcquisition.LABEL_DATASTREAM not in mqtt_dictionary.keys() \
                    or MessageAcquisition.LABEL_IOTID not in mqtt_dictionary[MessageAcquisition.LABEL_DATASTREAM]:
                return None

            if MessageAcquisition.LABEL_RESULT not in mqtt_dictionary or not mqtt_dictionary[MessageAcquisition.LABEL_RESULT]:
                return None

            # FIXME: The field extracted is the Observable identifier NOT the datastream id
            # (NOTE: it is not actually used)
            datastream_id = mqtt_dictionary[MessageAcquisition.LABEL_DATASTREAM][MessageAcquisition.LABEL_IOTID]
            iot_id = mqtt_dictionary[MessageAcquisition.LABEL_DATASTREAM][MessageAcquisition.LABEL_IOTID]

            json_result = mqtt_dictionary[MessageAcquisition.LABEL_RESULT]
            # Create Observation
            crowd_density_local = CrowdDensityLocalObservation()
            crowd_density_local.set_pilot_name(pilot_name=pilot_name)
            crowd_density_local.set_datastream_id(datastream_id=datastream_id)
            crowd_density_local.set_observable_id(observable_id=observable_id)
            crowd_density_local.set_obs_iot_id(iot_id=iot_id)

            if not crowd_density_local.from_dictionary(dictionary=json_result):
                del crowd_density_local
                return None

            device_registration = UtilityCatalogCached.\
                get_device_registration(datastream_id=crowd_density_local.get_datastream_id())

            if not device_registration:
                logger.warning('crowd_density_local_observation Unable To Find DeviceRegistration. Abort')
                del crowd_density_local
                return None

            if not crowd_density_local.set_info_registration(device_registration=device_registration):
                del crowd_density_local
                return None

            logger.info('CROWD DENSITY LOCAL OBSERVATION SAVED INFO: {}'.format(crowd_density_local.to_trace_string()))

            return crowd_density_local
        except Exception as ex:
            # logger.exception(ex)
            logger.error('CROWD DENSITY LOCAL REGISTRATION EXCEPTION: {0}'.format(ex))

    @staticmethod
    def localization_observation(mqtt_dictionary: Dict[str, Any],
                                 pilot_name: str,
                                 observable_id: int = 0,
                                 running_id: int = 0) -> Localization:
        try:
            if not mqtt_dictionary:
                return None

            if MessageAcquisition.LABEL_RESULT not in mqtt_dictionary:
                logger.error('localization observation Error. Probably received GOST Message, JSON: {}'
                             .format(json.dumps(mqtt_dictionary)))
                return None

            json_result = mqtt_dictionary[MessageAcquisition.LABEL_RESULT]

            timestamp = mqtt_dictionary[MessageAcquisition.LABEL_PHENOMENONTIME]

            datastream_id = 0

            json_datastream = mqtt_dictionary[MessageAcquisition.LABEL_DATASTREAM]

            if MessageAcquisition.LABEL_IOTID in json_datastream:
                datastream_id = json_datastream[MessageAcquisition.LABEL_IOTID]
                iot_id = json_datastream[MessageAcquisition.LABEL_IOTID]
            else:
                logger.warning("UNABLE TO FIND OBS_ID in Datastream")

            loc_observation = Localization()
            loc_observation.from_dictionary(dictionary=json_result)
            loc_observation.timestamp = isoparse(timestamp)
            loc_observation.set_pilot_name(pilot_name=pilot_name)
            loc_observation.set_datastream_id(datastream_id=datastream_id)
            loc_observation.set_observable_id(observable_id=observable_id)
            loc_observation.set_obs_iot_id(iot_id=iot_id)
            loc_observation.run_id = running_id
            loc_observation.save()

            return loc_observation

        except Exception as ex:
            logger.error('MessAcquisit localization_observation Exception: {0}'.format(ex))
            return None

    @staticmethod
    def flow_observation(j_data, pilot_name):
        logger.debug(j_data)

    @staticmethod
    def weareables_observation(j_data):
        logger.debug(j_data)
