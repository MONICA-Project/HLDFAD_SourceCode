from general_types.modelsenums import OutputMessageType
from general_types.label_ogc import LabelThings, LabelOGCDatastreams, LabelObservationType
from general_types.labelsdictionaries import LabelDictionaryMonitoringArea
from shared.settings.settingscustompilot import SELECTED_PILOT
from utility.utility_environment_variables import UtilityEnvironment
import os

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '*v$ykys&=(aag!7f%b$rtss$*al4-%!d6@y_qh0zd+yq@#56&l'

CATALOG_VERSION = "v1.0"
BGW_PORT = "5050"
SUBSTRING_URL_GETDEVICECOUNT = "datastreams?$count=true"
CATALOG_THINGS = "Things"
LABEL_TCP_PORT = "PORT"
LABEL_TCP_URL = "URL"
WP6_SERVICECATAOLG_WEBSERVICENAME = "SearchOrCreateOGCDataStreamId"

OGC_SCRAL_DICTIONARY_BASEURL = {
    "DOM": "monappdwp3.monica-cloud.eu",
    "TIVOLI": "monappdwp3.monica-cloud.eu",
    "RiF": "monappdwp3.monica-cloud.eu",
    "LARGE_SCALE_TEST": "monapp-lst.monica-cloud.eu",
    "IOTWEEK": "monappdwp3.monica-cloud.eu",
    "WOODSTOWER": "monappdwp3.monica-cloud.eu",
    "LEEDS": "monappdwp3.monica-cloud.eu",
    "LUMIERE_2019": "monappdwp3.monica-cloud.eu"
}

OBSERVABLE_MQTTBROKER_DICTIONARY_CONNINFO = {
    "DOM": {LABEL_TCP_PORT: 1883, LABEL_TCP_URL: "monappdwp3.monica-cloud.eu"},
    "TIVOLI": {LABEL_TCP_PORT: 1883, LABEL_TCP_URL: "monappdwp3.monica-cloud.eu"},
    "RiF": {LABEL_TCP_PORT: 1883, LABEL_TCP_URL: "monappdwp3.monica-cloud.eu"},
    "LARGE_SCALE_TEST": {LABEL_TCP_PORT: 1883, LABEL_TCP_URL: "mpclsifrmq01.monica-cloud.eu"},
    "IOTWEEK": {LABEL_TCP_PORT: 1883, LABEL_TCP_URL: "monappdwp3.monica-cloud.eu"},
    "WOODSTOWER": {LABEL_TCP_PORT: 1883, LABEL_TCP_URL: "monappdwp3.monica-cloud.eu"},
    "LEEDS": {LABEL_TCP_PORT: 1883, LABEL_TCP_URL: "monappdwp3.monica-cloud.eu"},
    "LUMIERE_2019": {LABEL_TCP_PORT: 1883, LABEL_TCP_URL: "monappdwp3.monica-cloud.eu"}
}

LIST_SCRAL_VPN_PORTS = {
    "DOM": 8095,
    "TIVOLI": 8099,
    "RiF": 8100,
    "PORT": 8102,
    "LARGE_SCALE_TEST": 8090,
    "IOTWEEK": 8103,
    "WOODSTOWER": 8105,
    "LEEDS": 8098,
    "LUMIERE_2019": 8109
}

LIST_WP6_SERVICECATALOG_CONNPARAMS = {
    "DOM": {LABEL_TCP_PORT: 8911, LABEL_TCP_URL: "monappdwp6.monica-cloud.eu"},
    "TIVOLI": {LABEL_TCP_PORT: 8911, LABEL_TCP_URL: "monappdwp6.monica-cloud.eu"},
    "RiF": {LABEL_TCP_PORT: 8911, LABEL_TCP_URL: "monappdwp6.monica-cloud.eu"},
    "LARGE_SCALE_TEST": {LABEL_TCP_PORT: 8911, LABEL_TCP_URL: "monappdwp6.monica-cloud.eu"},
    "IOTWEEK": {LABEL_TCP_PORT: 8911, LABEL_TCP_URL: "monappdwp6.monica-cloud.eu"},
    "WOODSTOWER": {LABEL_TCP_PORT: 8916, LABEL_TCP_URL: "monappdwp6.monica-cloud.eu"},
    "LEEDS": {LABEL_TCP_PORT: 8917, LABEL_TCP_URL: "monappdwp6.monica-cloud.eu"},
    "LUMIERE_2019": {LABEL_TCP_PORT: 8920, LABEL_TCP_URL: "monappdwp6.monica-cloud.eu"},
}


LIST_DEVICE_TO_EXCLUDE = [
    'LEEDS_CAM_0',
    'LEEDS_CAM_1',
    'LEEDS_CAM_2',
    'LEEDS_CAM_3',
    'LEEDS_CAM_5',
    'LEEDS_CAM_6',
    'LEEDS_CAM_7',
    'LEEDS_CAM_9',
    'LEEDS_CAM_10',
    'test-mannella-2',
    'test-mannella'
]

WP6_DICTIONARY_CATALOGOUTPUTINFO_CROWDHEATMAP = {"externalId": "HLDFAD:PeopleHetmap",
                                                 "metadata": "PeopleHeatMap datastream",
                                                 "sensorType": "PeopleHeatmap:1",
                                                 "unitOfMeasurement": "ppl/sqm",
                                                 "fixedLatitude": 0,
                                                 "fixedLongitude": 0
                                                 }

WP6_DICTIONARY_CATALOGOUTPUTINFO_QUEUEDETECTIONALERT = {"externalId": "HLDFAD:QueueDetectionAlert",
                                                        "metadata": "Queue Detection Alert Notification",
                                                        "sensorType": "HLDFAD:QueueDetectionModule",
                                                        "unitOfMeasurement": "ppl",
                                                        "fixedLatitude": 0,
                                                        "fixedLongitude": 0
                                                        }
WP6_CATALOG_LABEL_CROWDHEATMAP = "CrowdHeatmap"
WP6_CATALOG_LABEL_QUEUEDETECTIONALERT = "QueueDetectionAlert"

WP6_DICTIONARY_CATALOGOUTPUTINFO = \
    {
        OutputMessageType.OUTPUT_MESSAGE_TYPE_CROWDHEATMAPOUTPUT: WP6_DICTIONARY_CATALOGOUTPUTINFO_CROWDHEATMAP,
        OutputMessageType.OUTPUT_MESSAGE_TYPE_QUEUEDETECTIONALERT: WP6_DICTIONARY_CATALOGOUTPUTINFO_QUEUEDETECTIONALERT
    }

LIST_UNITTESTS_ENABLED = {
    "CacheRedis",
    "Processing"
    "MongoDB"
    "QueueDetection"
}

THINGS_TO_ANALYSE = {
    LabelThings.LABEL_THING_WRISTBANDGW: {
        LabelObservationType.LABEL_OBSTYPE_LOCALIZATION: LabelOGCDatastreams.LABEL_DATASTREAM_LOCALIZATION
    },
    LabelThings.LABEL_THING_SFN: {
        LabelObservationType.LABEL_OBSTYPE_CROWDDENSITY: LabelOGCDatastreams.LABEL_DATASTREAM_CROWDDENSITYLOCAL
    }
}

MAPPING_OUTPUT_DATASTREAMS = {
    OutputMessageType.OUTPUT_MESSAGE_TYPE_CROWDHEATMAPOUTPUT: [LabelObservationType.LABEL_OBSTYPE_LOCALIZATION],
    OutputMessageType.OUTPUT_MESSAGE_TYPE_QUEUEDETECTIONALERT: [LabelObservationType.LABEL_OBSTYPE_CROWDDENSITY]
}


class LABELS_CACHE_REDIS:
    LABEL_CACHE_LOCALIZATIONOBS = "LOCALIZATIONOBS"
    LABEL_CACHE_CROWDHEATMAPOUTPUT = "CROWDHEATMAPIDS"
    LABEL_CACHE_CROWDHEATMAPCOUNTER = "CROWDHEATMAPCOUNTVALUE"
    LABEL_CACHE_OBSERVATION_ID = "OBS_COUNTER_IDENTIFIER"
    LABEL_CACHE_QUEUEDETECTIONALERT = "QUEUEDETECTIONALERTID"


CACHE_REDIS_LABELS = {
    "LOCALIZATIONOBS": "LOCALIZATIONOBSIDS",
    "CROWDHEATMAPOUTPUT": "CROWDHEATMAPIDS",
    "CROWDHEATMAPCOUNTER": "CROWDHEATMAPCOUNTVALUE",
    "OBSERVATION_ID":   "OBS_COUNTER_IDENTIFIER",
    "QUEUEDETECTIONALERTID": "QUEUEDETECTIONALERTID"
}

# NOTE: CAM8 GroundPlanePosition: 53.817211, -1.579963, ground_plane_size: 15x18 m| CameraBearing: 180 degree
# NOTE: CAM4 GroundPlanePosition: 53.81761, -1.58331, ground_plane_size: 30x10 m
# | 30 number_rows x 10 Number_columns| CameraBearing: 90 degree

MONITORING_AREAS = {
    "IoTWeek": {
        LabelDictionaryMonitoringArea.LABEL_DICTIONARY_LATITUDE: 56.152402,
        LabelDictionaryMonitoringArea.LABEL_DICTIONARY_LONGITUDE: 10.198338,
        LabelDictionaryMonitoringArea.LABEL_DICTIONARY_HORIZONTALSIZE_M: 120,            # Set as Max East Coords from Point(Latitude, Longitude)
        LabelDictionaryMonitoringArea.LABEL_DICTIONARY_VERTICALSIZE_M: 110,              # Set as Max North Coords from Point(Latitude, Longitude)
        LabelDictionaryMonitoringArea.LABEL_DICTIONARY_CELLSIZE_M: 10
    },

    "LARGE_SCALE_TEST": {
        LabelDictionaryMonitoringArea.LABEL_DICTIONARY_LATITUDE: 55.672792,
        LabelDictionaryMonitoringArea.LABEL_DICTIONARY_LONGITUDE: 12.566985,
        LabelDictionaryMonitoringArea.LABEL_DICTIONARY_HORIZONTALSIZE_M: 120,
        LabelDictionaryMonitoringArea.LABEL_DICTIONARY_VERTICALSIZE_M: 140,
        LabelDictionaryMonitoringArea.LABEL_DICTIONARY_CELLSIZE_M: 10},

    "TIVOLI": {
        LabelDictionaryMonitoringArea.LABEL_DICTIONARY_LATITUDE: 55.672792,
        LabelDictionaryMonitoringArea.LABEL_DICTIONARY_LONGITUDE: 12.566985,
        LabelDictionaryMonitoringArea.LABEL_DICTIONARY_HORIZONTALSIZE_M: 120,
        LabelDictionaryMonitoringArea.LABEL_DICTIONARY_VERTICALSIZE_M: 140,
        LabelDictionaryMonitoringArea.LABEL_DICTIONARY_CELLSIZE_M: 10
    },

    # 45.7968451744, 4.95029322898 Origin (Bottom-Left) --> High Corner: 45.7984878319, 4.95404401336
    "WOODSTOWER": {
        LabelDictionaryMonitoringArea.LABEL_DICTIONARY_LATITUDE: 45.7968451744,
        LabelDictionaryMonitoringArea.LABEL_DICTIONARY_LONGITUDE: 4.95029322898,
        LabelDictionaryMonitoringArea.LABEL_DICTIONARY_HORIZONTALSIZE_M: 300,
        LabelDictionaryMonitoringArea.LABEL_DICTIONARY_VERTICALSIZE_M: 200,
        LabelDictionaryMonitoringArea.LABEL_DICTIONARY_CELLSIZE_M: 10
    },

    "LEEDS": {
        LabelDictionaryMonitoringArea.LABEL_DICTIONARY_LATITUDE: 53.81761,
        LabelDictionaryMonitoringArea.LABEL_DICTIONARY_LONGITUDE: -1.58331,
        LabelDictionaryMonitoringArea.LABEL_DICTIONARY_HORIZONTALSIZE_M: 300,
        LabelDictionaryMonitoringArea.LABEL_DICTIONARY_VERTICALSIZE_M: 200,
        LabelDictionaryMonitoringArea.LABEL_DICTIONARY_CELLSIZE_M: 10
    },
}

DEF_MON_AREA = MONITORING_AREAS[SELECTED_PILOT]

MONITORING_AREA = {
    LabelDictionaryMonitoringArea.LABEL_DICTIONARY_LATITUDE: UtilityEnvironment.get_envvar_type(env_name='APPSETTING_MONITORINGAREA_LATITUDE', type_var=float, value_if_no=DEF_MON_AREA[LabelDictionaryMonitoringArea.LABEL_DICTIONARY_LATITUDE]),
    LabelDictionaryMonitoringArea.LABEL_DICTIONARY_LONGITUDE: UtilityEnvironment.get_envvar_type(env_name='APPSETTING_MONITORINGAREA_LONGITUDE', type_var=float, value_if_no=DEF_MON_AREA[LabelDictionaryMonitoringArea.LABEL_DICTIONARY_LONGITUDE]),
    LabelDictionaryMonitoringArea.LABEL_DICTIONARY_HORIZONTALSIZE_M: UtilityEnvironment.get_envvar_type(env_name='APPSETTING_MONITORINGAREA_HORIZONTALSIZE_M', type_var=int, value_if_no=DEF_MON_AREA[LabelDictionaryMonitoringArea.LABEL_DICTIONARY_HORIZONTALSIZE_M]),
    LabelDictionaryMonitoringArea.LABEL_DICTIONARY_CELLSIZE_M: UtilityEnvironment.get_envvar_type(env_name='APPSETTING_MONITORINGAREA_CELLSIZE_M', type_var=int, value_if_no=DEF_MON_AREA[LabelDictionaryMonitoringArea.LABEL_DICTIONARY_CELLSIZE_M]),
    LabelDictionaryMonitoringArea.LABEL_DICTIONARY_VERTICALSIZE_M: UtilityEnvironment.get_envvar_type(env_name='APPSETTING_MONITORINGAREA_VERTICALSIZE_M', type_var=int, value_if_no=DEF_MON_AREA[LabelDictionaryMonitoringArea.LABEL_DICTIONARY_VERTICALSIZE_M]),
}
