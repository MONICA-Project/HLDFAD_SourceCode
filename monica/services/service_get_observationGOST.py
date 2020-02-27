from datetime import datetime
import requests
import logging
from typing import List, Dict, Any
from dateutil.parser import isoparse
from general_types.virtual_classes import ObservableGeneric
from jobs.cache_redis import CachedComponents

logger = logging.getLogger('textlogger')


class ServiceGetObservationGOST:
    LABEL_CONTAINER = "value"
    LABEL_IOTID = "@iot.id"
    LABEL_RESULT = "result"
    LABEL_TIMESTAMP = "timestamp_2"

    @staticmethod
    def get_complete_url(gost_main_url: str,
                         datastream_id: int) -> str:
        return "{0}/Datastreams({1})/Observations".format(gost_main_url,
                                                          datastream_id)

    @staticmethod
    def set_correct_obs_iotid(catalog_observations: Dict[str, List[ObservableGeneric]],
                              gost_url: str) -> Dict[str, List[ObservableGeneric]]:
        if not catalog_observations:
            return None

        for type_obs in catalog_observations.keys():
            observables = catalog_observations[type_obs]
            if not observables:
                continue

            for observable in observables:
                iot_id = ServiceGetObservationGOST.get_obs_id_observable(gost_main_url=gost_url,
                                                                         observable=observable)

                if iot_id == 0:
                    continue

                CachedComponents.set_last_observation_id(obs_id=iot_id)

                observable.obs_iot_id = ServiceGetObservationGOST.get_obs_id_observable(gost_main_url=gost_url,
                                                                                        observable=observable)
        return catalog_observations

    @staticmethod
    def get_obs_id_observable(gost_main_url: str,
                              observable: ObservableGeneric) -> int:
        if not observable:
            return 0

        datastream_id = observable.get_datastream_id()
        timestamp = observable.get_timestamp()

        return ServiceGetObservationGOST.get_obs_id(gost_main_url=gost_main_url,
                                                    datastream_id=datastream_id,
                                                    timestamp=timestamp)

    @staticmethod
    def get_obs_id(gost_main_url: str,
                   datastream_id: int,
                   timestamp: datetime) -> int:
        try:
            url_complete = ServiceGetObservationGOST.get_complete_url(gost_main_url=gost_main_url,
                                                                      datastream_id=datastream_id)
            params = {"$top": 5}
            resp = requests.get(url_complete, params=params)

            if not resp:
                return 0

            observations = resp.json()

            if not observations or ServiceGetObservationGOST.LABEL_CONTAINER not in observations.keys():
                return 0

            observations = observations[ServiceGetObservationGOST.LABEL_CONTAINER]

            for observation in observations:
                iot_id = observation[ServiceGetObservationGOST.LABEL_IOTID]
                obs_result = observation[ServiceGetObservationGOST.LABEL_RESULT]

                obs_timestamp = isoparse(obs_result[ServiceGetObservationGOST.LABEL_TIMESTAMP])

                logger.info("ServiceGetObservationGOST iot_id={0}, Timestamp: {1} Found: {2}".format(iot_id,
                                                                                                     obs_timestamp,
                                                                                                     timestamp))  # .strftime("%m/%d/%Y, %H:%M:%S")

                if timestamp != obs_timestamp:
                    continue

                logger.info("ServiceGetObservationGOST Datastream: {0} get obs_iot_id: {1}".format(datastream_id,
                                                                                                   iot_id))

                return iot_id

            logger.info("ServiceGetObservationGOST Datastream: {0} NOT Found Obs IOT ID".format(datastream_id))

            return 0
        except Exception as ex:
            logger.error('ServiceGetObservationGOST Exception: {}'.format(ex))
            return 0

