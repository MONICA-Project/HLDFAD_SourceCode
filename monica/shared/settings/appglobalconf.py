from shared.settings.base import *
from shared.settings.dockersconf import *
from shared.settings.version import SW_VERSION
from general_types.modelsenums import OutputMessageType
from general_types.general_enums import MQTTPayloadConversion
from utility.utility_environment_variables import UtilityEnvironment
from shared.settings.appstableconf import *
from general_types.labelsdictionaries import LocConfLbls
from general_types.general_enums import TypeQueueDetection
from utility.utility_json import UtilityJSONConfig
import os

# Database Condocker-composeuration
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases

GLOBAL_INFO_ENVIRONMENT = os.environ.get('CONFENVIRONMENT_GLOBALINFO', 'PROD')
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = UtilityEnvironment.get_envvar_type(env_name='CONFENVIRONMENT_DEBUG', type_var=bool, value_if_no=False)
TEMPLATE_DEBUG = UtilityEnvironment.get_envvar_type(env_name='CONFENVIRONMENT_DEBUGTEMPLATE', type_var=bool, value_if_no=False)

WEB_BASE_URL = os.environ.get('ENV_WEB_BASE_URL', OGC_SCRAL_DICTIONARY_BASEURL[SELECTED_PILOT])
MQTT_OBSERVATION_URL = OBSERVABLE_MQTTBROKER_DICTIONARY_CONNINFO[SELECTED_PILOT][LABEL_TCP_URL]
MQTT_OBSERVATION_PORT = OBSERVABLE_MQTTBROKER_DICTIONARY_CONNINFO[SELECTED_PILOT][LABEL_TCP_PORT]
GOST_NAME_ORIGINAL = "GOST_" + SELECTED_PILOT
GOST_NAME = os.environ.get('APPSETTING_GOST_NAME', GOST_NAME_ORIGINAL)
BGW_GOST_SELECTED = GOST_NAME.lower()


CATALOG_BASE_URL = "http://"+WEB_BASE_URL
SUBSTRING_SCRAL_TOREPLACE = ":"+BGW_PORT+"/"+BGW_GOST_SELECTED
SELECTED_VPN_PORT = os.environ.get('ENV_CATALOG_PORT', LIST_SCRAL_VPN_PORTS[SELECTED_PILOT])
SCRAL_URL_BASE = CATALOG_BASE_URL+":"+str(SELECTED_VPN_PORT)+"/"
GOST_URL = SCRAL_URL_BASE+CATALOG_VERSION
SCRAL_URL_COMPLETE = SCRAL_URL_BASE+CATALOG_VERSION+"/"+CATALOG_THINGS

WP6_CATALOG_CONNECTIONURL = os.environ.get('WP6_CATALOG_CONNECTIONURL', LIST_WP6_SERVICECATALOG_CONNPARAMS[SELECTED_PILOT][LABEL_TCP_URL])
WP6_CATALOG_CONNECTIONPORT = UtilityEnvironment.get_envvar_type(env_name='WP6_CATALOG_CONNECTIONPORT', type_var=int, value_if_no=LIST_WP6_SERVICECATALOG_CONNPARAMS[SELECTED_PILOT][LABEL_TCP_PORT])

PATH_JSON_CONFIG = os.environ.get('JSON_CONFIGURATION_PATH', '/appconfig/appconfig.json')

LIST_OUTPUT_MESSAGES = UtilityJSONConfig.get_list_output(json_conf_path=PATH_JSON_CONFIG,
                                                         list_default=[OutputMessageType.OUTPUT_MESSAGE_TYPE_CROWDHEATMAPOUTPUT])
LIST_MQTT_OUTPUT_TYPE = UtilityJSONConfig.get_list_mqtttypes(json_conf_path=PATH_JSON_CONFIG,
                                                             list_default=[MQTTPayloadConversion.TYPE_CONVERSION_OGCDICTIONARY])

LOCAL_CONFIG = {
    LocConfLbls.LABEL_MQTT_OBSERVATION_URL: os.environ.get('ENV_MQTT_OBSERVATION_URL', MQTT_OBSERVATION_URL),
    LocConfLbls.LABEL_MQTT_OBSERVATION_PORT: int(os.environ.get('ENV_MQTT_OBSERVATION_PORT', str(MQTT_OBSERVATION_PORT))),
    LocConfLbls.LABEL_CATALOG_URL: os.environ.get('ENV_CATALOG_URL', SCRAL_URL_COMPLETE),
    LocConfLbls.LABEL_GOST_URL: GOST_URL,
    LocConfLbls.LABEL_CATALOG_USERNAME: os.environ.get('ENV_CATALOG_USERNAME', ''),
    LocConfLbls.LABEL_CATALOG_PASSWORD: os.environ.get('ENV_CATALOG_PASSWORD', ''),
    LocConfLbls.LABEL_PILOT_NAME: SELECTED_PILOT,
    LocConfLbls.LABEL_ENABLE_OBS_IOTIDRETRIEVE: UtilityEnvironment.get_envvar_type(env_name='APPSETTING_ENABLE_OBS_IOTIDRETRIEVE', type_var=bool, value_if_no=True),
    LocConfLbls.LABEL_URL_GET_DEVICECOUNT: GOST_URL + "/" + SUBSTRING_URL_GETDEVICECOUNT,
    LocConfLbls.LABEL_SW_RELEASE_VERSION: SW_VERSION,
    LocConfLbls.LABEL_UPDATE_DATASTREAM_LIST: GOST_NAME + "/Datastreams",
    LocConfLbls.LABEL_PREFIX_TOPIC: GOST_NAME,
    LocConfLbls.LABEL_INTERVAL_OBS_VALIDITY_SECS: UtilityEnvironment.get_envvar_type(env_name='APPSETTING_INTERVAL_OBS_VALIDITY_SECS', type_var=int, value_if_no=-1),
    LocConfLbls.LABEL_ENABLE_EMPTY_CROWD_HEATMAP: UtilityEnvironment.get_envvar_type(env_name='APPSETTING_ENABLE_EMPTY_CROWD_HEATMAP', type_var=bool, value_if_no=False),
    LocConfLbls.LABEL_ENABLE_RANDOM_OUTPUT: DEBUG & UtilityEnvironment.get_envvar_type(env_name='APPSETTING_ENABLE_RANDOM_OUTPUT', type_var=bool, value_if_no=False),
    LocConfLbls.LABEL_ENABLE_IMMEDIATEELABORATION_FEEDBYNUMBEROBS: UtilityEnvironment.get_envvar_type(
        env_name='APPSETTINGS_ENABLE_IMMEDIATEELABORATION_FEEDBYNUMBEROBS', type_var=bool, value_if_no=True),
    LocConfLbls.LABEL_BYPASS_BEGINNING_CATALOG_ACQUISITION: DEBUG & False,
    LocConfLbls.LABEL_BYPASS_MQTTINPUTMESSAGEACQUISITION: DEBUG & False,
    LocConfLbls.LABEL_ENABLE_UNIT_TESTS: DEBUG & False,
    LocConfLbls.LABEL_ENABLE_RANDOM_QUEUEDETECTIONALERT: DEBUG & UtilityEnvironment.get_envvar_type(env_name='APPSETTING_ENABLE_RANDOM_QUEUEDETECTIONALERT', type_var=bool, value_if_no=False),
    LocConfLbls.LABEL_ABORT_EXECUTION_AFTERUNITTESTS: DEBUG & False,
    LocConfLbls.LABEL_ENABLE_RANDOM_DENSITYMATRIX: DEBUG & UtilityEnvironment.get_envvar_type(env_name='APPSETTING_ENABLE_RANDOM_DENSITYMATRIX', type_var=bool, value_if_no=False),
    LocConfLbls.LABEL_ENABLE_RANDOM_FAKEQUEUEDETECTION: DEBUG & UtilityEnvironment.get_envvar_type(env_name='APPSETTING_ENABLE_RANDOM_FAKEQUEUEDETECTION', type_var=bool, value_if_no=False),
    LocConfLbls.LABEL_MQTT_CLIENT_PAHO_NAME_OBSERVABLES: "MONICA_HLDFAD_OBSERVABLE_" + GLOBAL_INFO_ENVIRONMENT,
    LocConfLbls.LABEL_MQTT_CLIENT_PAHO_NAME_DATASTREAMUPDATE: "MONICA_HLDFAD_DATASTREAMUPDATE_{}".format(GLOBAL_INFO_ENVIRONMENT),
    LocConfLbls.LABEL_WP6_CATALOG_CONNECTIONURL: "http://"+WP6_CATALOG_CONNECTIONURL,
    LocConfLbls.LABEL_WP6_CATALOG_CONNECTIONPORT: WP6_CATALOG_CONNECTIONPORT,
    LocConfLbls.LABEL_WP6_CATALOG_POSTSERVICERETRIEVEOUTPUTINFO: WP6_SERVICECATAOLG_WEBSERVICENAME,
    LocConfLbls.LABEL_OBSERVATION_DEBUG_INTERVALNUMBERNOTIFICATION: UtilityEnvironment.get_envvar_type(env_name='APPSETTING_OBSERVATION_DEBUG_INTERVALNUMBERNOTIFICATION', type_var=int, value_if_no=100),
    LocConfLbls.LABEL_OUTPUT_MESSAGELIST_SELECTED: LIST_OUTPUT_MESSAGES,
    LocConfLbls.LABEL_OUTPUT_MQTT_LISTTYPES: LIST_MQTT_OUTPUT_TYPE,
    LocConfLbls.LABEL_TYPEQUEUEDETECTIONCOMPUTATION: TypeQueueDetection.QUEUEDETECTION_ALLMONITOREDAREA,
    LocConfLbls.LABEL_MQTT_CLIENT_USERNAME: os.environ.get('MOSQUITTO_USERNAME', ''),
    LocConfLbls.LABEL_MQTT_CLIENT_PASSWORD: os.environ.get('MOSQUITTO_PASSWORD', ''),
    LocConfLbls.LABEL_OUTPUT_MQTT_BROKER_USERNAME: os.environ.get('OUTPUT_MQTTBROKER_USERNAME', ''),
    LocConfLbls.LABEL_OUTPUT_MQTT_BROKER_PASSWORD: os.environ.get('OUTPUT_MQTTBROKER_PASSWORD', '')
}

SCHEDULER_SETTINGS = {
    "TASK_ELABORATION": UtilityEnvironment.get_envvar_type(env_name='APPSETTING_TASK_ELABORATION_FREQ_SECS', type_var=int, value_if_no=100),
    "TASK_ALIVEAPP": UtilityEnvironment.get_envvar_type(env_name='APPSETTING_TASK_ALIVEAPP_FREQ_SECS', type_var=int, value_if_no=100)
}
