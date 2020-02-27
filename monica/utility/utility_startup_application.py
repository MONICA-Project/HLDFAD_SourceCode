import logging
from jobs.cache_redis import CachedComponents, CacheRedisAdapter
from utility.utility_database import UtilityDatabase
from utility.utility_catalog_cached import UtilityCatalogCached
from shared.settings.appglobalconf import LOCAL_CONFIG, LocConfLbls
from services.service_observation_client import ServiceObservationClient
from shared.settings.dockersconf import DATABASES
from shared.settings.appglobalconf import MONITORING_AREA

logger = logging.getLogger('textlogger')


class UtilityStartupApplication:
    @staticmethod
    def startup():
        CachedComponents.startup()
        UtilityCatalogCached.initialize_catalog()

    @staticmethod
    def trace_startup_info():
        try:
            logger.info("HLDFAD MODULE STARTED, VERSION: {0}".format(LOCAL_CONFIG[LocConfLbls.LABEL_SW_RELEASE_VERSION]))

            for key in LOCAL_CONFIG:
                if "SW_RELEASE_VERSION" == key:
                    continue

                logger.info(" - {0}: {1}"
                            .format(key, LOCAL_CONFIG[key]))

            logger.info('HLDFAD DATABASES STRUCTURE: {}'.format(DATABASES))
            logger.info('HLDFAD MONITORING_AREA: {}'.format(MONITORING_AREA))

        except Exception as ex:
            logger.error('UtilityStartupApplication trace_startup_info Exception: {}'.format(ex))

    @staticmethod
    def adjust_startup_data():
        try:

            UtilityDatabase.purge_db_connections()
            UtilityDatabase.update_database_startup()

            running_id = UtilityDatabase.update_get_sw_running_info(LOCAL_CONFIG[LocConfLbls.LABEL_SW_RELEASE_VERSION])

            logger.info('UtilityStartupApplication Running ID: {0} SW_VERSION: {1}'
                        .format(str(running_id),
                                LOCAL_CONFIG[LocConfLbls.LABEL_SW_RELEASE_VERSION]))

            CachedComponents.initialize_components(running_id=running_id)

            ServiceObservationClient.set_running_id(running_id=running_id)
        except Exception as ex:
            logger.error('UtilityStartupApplication adjust_startup_data Exception: {}'.format(ex))