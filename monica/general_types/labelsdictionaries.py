class MQTTLabelsConfigurations:
    LABEL_DICTIONARY_USERNAME = 'USERNAME'
    LABEL_DICTIONARY_PASSWORD = 'PASSWORD'
    LABEL_DICTIONARY_URL = 'URL'
    LABEL_DICTIONARY_TOPICS = 'TOPICS'
    LABEL_TOPICS_CROWDHEATMAPOUTPUT = 'CROWDHEATMAPOUTPUT'
    LABEL_TOPICS_QUEUEDETECTIONALERT = 'QUEUEDETECTIONALERT'
    LABEL_DICTIONARY_CLIENT_ID = "CLIENT_ID"
    # MQTT Broker Provisioning


class LocConfLbls:
    LABEL_MQTT_OBSERVATION_URL = "MQTT_OBSERVATION_URL"
    LABEL_MQTT_OBSERVATION_PORT = "MQTT_OBSERVATION_PORT"
    LABEL_CATALOG_URL = "CATALOG_URL"
    LABEL_GOST_URL = 'GOST_URL'
    LABEL_CATALOG_USERNAME = "CATALOG_USERNAME"
    LABEL_CATALOG_PASSWORD = "CATALOG_PASSWORD"
    LABEL_TYPE_GLOBAL_CROWD_DENSITY_LABEL = "TYPE_GLOBAL_CROWD_DENSITY_LABEL"
    LABEL_TYPE_LOCAL_CROWD_DENSITY_LABEL = "TYPE_LOCAL_CROWD_DENSITY_LABEL"
    LABEL_TYPE_MIC_LABEL = "TYPE_MIC_LABEL"
    LABEL_TYPE_GATE_LABEL = "TYPE_GATE_LABEL"
    LABEL_TYPE_WEAREABLES = "TYPE_WEAREABLES"
    LABEL_TYPE_FLOW_ANALYSIS = "TYPE_FLOW_ANALYSIS"
    LABEL_PILOT_NAME = "PILOT_NAME"
    LABEL_ENABLE_OBS_IOTIDRETRIEVE = "OBS_IOTIDRETRIEVE"
    LABEL_URL_GET_DEVICECOUNT = "URL_GET_DEVICECOUNT"
    LABEL_SW_RELEASE_VERSION = "SW_RELEASE_VERSION"
    LABEL_UPDATE_DATASTREAM_LIST = "UPDATE_DATASTREAM_LIST"
    LABEL_PREFIX_TOPIC = "PREFIX_TOPIC"
    LABEL_INTERVAL_OBS_VALIDITY_SECS = "INTERVAL_OBS_VALIDITY_SECS"
    LABEL_ENABLE_EMPTY_CROWD_HEATMAP = "ENABLE_EMPTY_CROWD_HEATMAP"
    LABEL_BYPASS_BEGINNING_CATALOG_ACQUISITION = "BYPASS_BEGINNING_CATALOG_ACQUISITION"
    LABEL_MINIMUM_ACCEPTED_WRISTBAND_TO_START = "MINIMUM_ACCEPTED_WRISTBAND_START"
    LABEL_BYPASS_MQTTINPUTMESSAGEACQUISITION = "BYPASS_MQTTINPUTMESSAGEACQUISITION"
    LABEL_ENABLE_UNIT_TESTS = "ENABLE_UNIT_TESTS"
    LABEL_ABORT_EXECUTION_AFTERUNITTESTS = "ABORT_EXECUTION_AFTERUNITTESTS"
    LABEL_ENABLE_RANDOM_DENSITYMATRIX = "ENABLE_RANDOM_DENSITYMATRIX"
    LABEL_ENABLE_RANDOM_QUEUEDETECTIONALERT = "ENABLE_RANDOM_QUEUEDETECTIONALERT"
    LABEL_ENABLE_RANDOM_FAKEQUEUEDETECTION = "ENABLE_RANDOM_FAKEQUEUEDETECTION"
    LABEL_ENABLE_IMMEDIATEELABORATION_FEEDBYNUMBEROBS = "ENABLE_IMMEDIATEELABORATION_FEEDBYNUMBEROBS"
    LABEL_ENABLE_RANDOM_OUTPUT = "ENABLE_OUTPUT_RANDOMOUTPUT"
    LABEL_MQTT_CLIENT_PAHO_NAME_OBSERVABLES = "MQTT_CLIENT_PAHO_NAME_OBSERVABLES"
    LABEL_MQTT_CLIENT_USERNAME="MQTT_CLIENT_USERNAME"
    LABEL_MQTT_CLIENT_PASSWORD="MQTT_CLIENT_PASSWORD"
    LABEL_MQTT_CLIENT_PAHO_NAME_DATASTREAMUPDATE = "MQTT_CLIENT_PAHO_NAME_DATASTREAMUPDATE"
    LABEL_WP6_CATALOG_CONNECTIONURL = "WP6_CATALOG_CONNECTIONURL"
    LABEL_WP6_CATALOG_CONNECTIONPORT = "WP6_CATALOG_CONNECTIONPORT"
    LABEL_WP6_CATALOG_POSTSERVICERETRIEVEOUTPUTINFO = "WP6_CATALOG_POSTSERVICERETRIEVEOUTPUTINFO"
    LABEL_OBSERVATION_DEBUG_INTERVALNUMBERNOTIFICATION = "OBSERVATION_DEBUG_INTERVALNUMBERNOTIFICATION"
    LABEL_WP6_SERVICECATALOG_DICTIONARYSELECTED = "WP6_SERVICECATALOG_DICTIONARYSELECTED"
    LABEL_OUTPUT_MESSAGELIST_SELECTED = "OUTPUT_MESSAGELIST_SELECTED"
    LABEL_OUTPUT_MQTT_LISTTYPES = "OUTPUT_MQTT_LISTTYPES"
    LABEL_TYPEQUEUEDETECTIONCOMPUTATION = "TYPE_QUEUEDETECTION"
    LABEL_OUTPUT_MQTT_BROKER_USERNAME = "OUTPUT_MQTT_BROKER_USERNAME"
    LABEL_OUTPUT_MQTT_BROKER_PASSWORD = "OUTPUT_MQTT_BROKER_PASSWORD"


class LabelDictionaryQueueShapeArea:
    LABEL_DICT_QSMA_ID = "qsma_id"
    LABEL_DICT_LAT = "Lat"
    LABEL_DICT_LONG = "Long"
    LABEL_DICT_HORIZONTAL_SIZE_M = "Horizontal_Size_m"
    LABEL_DICT_VERTICAL_SIZE_M = "Vertical_Size_m"
    LABEL_DICT_THRESHOLD_ALERT = "Threshold_Alert"
    LABEL_DICT_FORCESTATICAPPROACH = "ForceStaticApproach"
    LABEL_FORCESTATICAPPR_CAMERA_ID = "CameraID"
    LABEL_FORCESTATICAPPR_ARRAYELEMENT_QUEUESHAPE = "QueueShapeInMatrix"
    LABEL_FORCESTATICAPPR_INDEXROW = "IndexRow"
    LABEL_FORCESTATICAPPR_RANGECOLUMNS = "RangeColumns"
    LABEL_DICT_DATASTREAMID="DatastreamID"
    LABEL_DICT_GROUNDPLANEORIENTATION="GPPOrient"


class LabelDictionaryMonitoringArea:
    LABEL_DICTIONARY_LATITUDE = "Latitude"
    LABEL_DICTIONARY_LONGITUDE = "Longitude"
    LABEL_DICTIONARY_HORIZONTALSIZE_M = "HorizontalSize_m"
    LABEL_DICTIONARY_CELLSIZE_M = "CellSize_m"
    LABEL_DICTIONARY_VERTICALSIZE_M = "VerticalSize_m"
