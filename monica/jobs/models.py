# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.contrib.gis.db import models
from django.contrib.postgres.fields import ArrayField
# from django.db.models import signals
from pygments.lexers import get_all_lexers
from pygments.styles import get_all_styles
from django.contrib.gis.geos import Point, MultiPoint, Polygon

from general_types.modelsenums import OutputMessageType
from general_types.labelsdictionaries import LabelDictionaryQueueShapeArea
from general_types.label_ogc import LabelObservationType

from general_types.virtual_classes import OutputMessage
from general_types.virtual_classes import Dictionarizable
from general_types.virtual_classes import ObservableGeneric
from general_types.labelsdictionaries import LabelDictionaryMonitoringArea
from entities.densitymap_types import RegionAdiacentCells, DensityMapConfiguration, GroupRegionsAdiacentCells
from jobs.processing.queue_detection import QueueDetectionAlgorithm
from utility.geodesy import GeoPosition

import json
import logging
import datetime
from dateutil.parser import isoparse
from typing import List, Dict, Any
from enum import Enum

logger = logging.getLogger('textlogger')


LEXERS = [item for item in get_all_lexers() if item[1]]
LANGUAGE_CHOICES = sorted([(item[1][0], item[0]) for item in LEXERS])
STYLE_CHOICES = sorted((item, item) for item in get_all_styles())


class FakeModel(models.Model):
    software_version = models.TextField(primary_key=True, blank=True)
    field_integer = models.IntegerField(blank=True, default=0, null=True)
    field_array = ArrayField(
            ArrayField(
                models.IntegerField(default=0)
            ), null=True, blank=True
    )
    # field_point = models.PointField(geography=True, blank=True, null=True, dim=2)

    class Meta:
        db_table = 'fake_model'


class SWRunningInfo(models.Model):
    software_version = models.TextField(primary_key=True, blank=True)
    timestamp_start = models.DateTimeField(null=True, auto_created=False, auto_now=False, blank=True)
    timestamp_stop = models.DateTimeField(null=True, auto_created=False, auto_now=False, blank=True)
    run_id = models.IntegerField(blank=True, null=True)
    counter_observables = models.IntegerField(blank=True, default=0, null=True)
    counter_device_registered = models.IntegerField(blank=True, default=0, null=True)
    counter_message_output = models.IntegerField(blank=True, default=0, null=True)

    class Meta:
        db_table = 'sw_running_info'


class CrowdHeatmapOutput(models.Model, OutputMessage):
    LABEL_WRISTBAND = "WristbandOnly"
    LABEL_CAMERA = "CameraOnly"
    LABEL_WRISTBAND_CAMERA = "WristbandCamera"

    LABEL_DICTIONARY_ID = "id"
    LABEL_DICTIONARY_DENSITY_MAP = "density_map"
    LABEL_DICTIONARY_TIMESTAMP = "timestamp"
    LABEL_DICTIONARY_GROUND_PLANE_POSITION = "ground_plane_position"
    LABEL_DICTIONARY_GROUND_PLANE_ORIENTATION = "ground_plane_orientation"
    LABEL_DICTIONARY_CELL_SIZE_M = "cell_size_m"
    LABEL_DICTIONARY_NUM_COLS = "num_cols"
    LABEL_DICTIONARY_NUM_ROWS = "num_rows"
    LABEL_DICTIONARY_GLOBAL_PEOPLE_COUNTING = "global_people_counting"
    LABEL_DICTIONARY_CONFIDENCE_LEVEL = "confidence_level"
    LABEL_DICTIONARY_LOCALIZATION_COUNTER_REGISTERED = "localization_counter_registered"
    LABEL_DICTIONARY_LOCALIZATION_COUNTER_ACTIVE = "localization_counter_active"
    LABEL_DICTIONARY_COMPUTATION_STRATEGY = "computation_strategy"

    list_choices = [(LABEL_WRISTBAND, "Wristband Only"), (LABEL_CAMERA, "Camera Only"), (LABEL_WRISTBAND_CAMERA, "Wristband Camera")]

    id = models.AutoField(primary_key=True)
    pilot_name = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now=False, auto_now_add=False, null=True, blank=True)
    density_map = ArrayField(
            ArrayField(
                models.IntegerField(default=0)
            ), null=True, blank=True
    )
    ground_plane_position = models.PointField(geography=True, blank=True, null=True, dim=2)
    cell_size_m = models.IntegerField(blank=True, null=True, default=1)
    num_cols = models.IntegerField(default=0)
    num_rows = models.IntegerField(default=0)
    global_people_counting = models.IntegerField(default=0)
    is_transferred = models.BooleanField(default=False)
    confidence_level = models.FloatField(blank=True, null=True,default=0.7)
    ground_plane_orientation = models.FloatField(blank=True, null=True, default=0)
    observation_list = ArrayField(
                models.IntegerField(default=0), null=True, blank=True
            )
    localization_counter_registered = models.IntegerField(default=0, blank=True)
    localization_counter_active = models.IntegerField(default=0, blank=True)
    sw_run_id = models.IntegerField(default=0, blank=True, null=True)
    computation_strategy = models.TextField(blank=True, null=True, default=LABEL_WRISTBAND, choices=list_choices)

    def set_timestamp(self, timestamp: datetime.datetime):
        self.timestamp = timestamp

    def get_timestamp(self) -> datetime.datetime:
        return self.timestamp

    def get_outputmessagetype(self) -> OutputMessageType:
        return OutputMessageType.OUTPUT_MESSAGE_TYPE_CROWDHEATMAPOUTPUT

    def get_list_keys(self) -> List[str]:
        return [CrowdHeatmapOutput.LABEL_DICTIONARY_ID,
                CrowdHeatmapOutput.LABEL_DICTIONARY_DENSITY_MAP,
                CrowdHeatmapOutput.LABEL_DICTIONARY_TIMESTAMP,
                CrowdHeatmapOutput.LABEL_DICTIONARY_GROUND_PLANE_POSITION,
                CrowdHeatmapOutput.LABEL_DICTIONARY_GROUND_PLANE_ORIENTATION,
                CrowdHeatmapOutput.LABEL_DICTIONARY_CELL_SIZE_M,
                CrowdHeatmapOutput.LABEL_DICTIONARY_NUM_COLS,
                CrowdHeatmapOutput.LABEL_DICTIONARY_NUM_ROWS,
                CrowdHeatmapOutput.LABEL_DICTIONARY_GLOBAL_PEOPLE_COUNTING,
                CrowdHeatmapOutput.LABEL_DICTIONARY_CONFIDENCE_LEVEL,
                CrowdHeatmapOutput.LABEL_DICTIONARY_LOCALIZATION_COUNTER_REGISTERED,
                CrowdHeatmapOutput.LABEL_DICTIONARY_LOCALIZATION_COUNTER_ACTIVE,
                CrowdHeatmapOutput.LABEL_DICTIONARY_COMPUTATION_STRATEGY]

    def get_specific_value(self, key: str) -> Any:
        try:
            if not key:
                return None

            if key == CrowdHeatmapOutput.LABEL_DICTIONARY_ID:
                return self.id
            elif key == CrowdHeatmapOutput.LABEL_DICTIONARY_DENSITY_MAP:
                return self.density_map
            elif key == CrowdHeatmapOutput.LABEL_DICTIONARY_TIMESTAMP:
                return self.get_timestamp()
            elif key == CrowdHeatmapOutput.LABEL_DICTIONARY_GROUND_PLANE_POSITION:
                return self.ground_plane_position
            elif key == CrowdHeatmapOutput.LABEL_DICTIONARY_GROUND_PLANE_ORIENTATION:
                return self.ground_plane_orientation
            elif key == CrowdHeatmapOutput.LABEL_DICTIONARY_CELL_SIZE_M:
                return self.cell_size_m
            elif key == CrowdHeatmapOutput.LABEL_DICTIONARY_NUM_COLS:
                return self.num_cols
            elif key == CrowdHeatmapOutput.LABEL_DICTIONARY_NUM_ROWS:
                return self.num_rows
            elif key == CrowdHeatmapOutput.LABEL_DICTIONARY_GLOBAL_PEOPLE_COUNTING:
                return self.global_people_counting
            elif key == CrowdHeatmapOutput.LABEL_DICTIONARY_CONFIDENCE_LEVEL:
                return self.confidence_level
            elif key == CrowdHeatmapOutput.LABEL_DICTIONARY_LOCALIZATION_COUNTER_REGISTERED:
                return self.localization_counter_registered
            elif key == CrowdHeatmapOutput.LABEL_DICTIONARY_LOCALIZATION_COUNTER_ACTIVE:
                return self.localization_counter_active
            elif key == CrowdHeatmapOutput.LABEL_DICTIONARY_COMPUTATION_STRATEGY:
                return self.computation_strategy

            return None
        except Exception as ex:
            logger.error('CrowdHeatmapOutput get_specific_value Exception: {}'.format(ex))
            return None

    class Meta:
        db_table = 'crowd_heatmap_output'


class QueueDetectionAlertLabels:
    LABEL_DICTIONARY_SPECIFIC_ID = "specific_id"
    LABEL_DICTIONARY_SHAPEID = "shape_id"
    LABEL_DICTIONARY_TIMESTAMP = "timestamp"
    LABEL_DICTIONARY_QUEUECOUNT = "queuecount"
    LABEL_DICTIONARY_QUEUESIZEAREA = "queuesizearea"
    LABEL_DICTIONARY_THRESHOLD_ALERT = "threshold_alert"
    LABEL_DICTIONARY_DESCRIPTION = "description"
    LABEL_DICTIONARY_GEOGRAPHIC_REGION = "georegion"
    LABEL_DICTIONARY_MEANPEOPLE = "meanpeople"
    LABEL_DICTIONARY_OBSIOTID = "obs_iotid"
    LABEL_DICTIONARY_DEVICEINPUTID = "device_id"


class QueueDetectionAlert(models.Model, OutputMessage):

    qda_id = models.AutoField(primary_key=True)
    qsma_id = models.TextField(default="", null=True, blank=True)
    timestamp = models.DateTimeField(auto_now=False, auto_now_add=False, null=True, blank=True)
    number_people = models.IntegerField(blank=True, null=True, default=0)
    extensionregion_squaremeters = models.IntegerField(blank=True, null=True, default=0)
    threshold_alert = models.IntegerField(blank=True, null=True, default=0)
    mean_people = models.IntegerField(blank=True, null=True, default=0)
    device_id = models.CharField(max_length=128, verbose_name='device identifier', blank=True, null=True, default='')
    is_notified = models.BooleanField(default=False, null=True)
    obs_iot_id = models.IntegerField(default=0, null=True, blank=True)
    # FIXME: FIELDS UNUSED (JUST FOR RETROFIT)
    horizontal_size_m = models.IntegerField(blank=True, null=True, default=0)
    vertical_size_m = models.IntegerField(blank=True, null=True, default=0)
    timestamp = models.DateTimeField(auto_now=True, auto_now_add=False, null=True, blank=True)
    # FIXME: FIELDS UNUSED (JUST FOR RETROFIT)

    geographyc_area = models.PolygonField(blank=True, null=True)

    class QueueDetectionAlert:
        db_table = 'queue_detection_alert_calculated'

    def initialize_status(self):
        pass

    def set_device_id(self, device_id: str()):
        self.device_id = device_id

    def get_device_id(self) -> str:
        return self.device_id

    def set_timestamp(self, timestamp: datetime.datetime):
        self.timestamp = timestamp

    def get_timestamp(self) -> datetime.datetime:
        return self.timestamp

    def get_outputmessagetype(self) -> OutputMessageType:
        return OutputMessageType.OUTPUT_MESSAGE_TYPE_QUEUEDETECTIONALERT

    def set_region_queue(self,
                         region_queue: RegionAdiacentCells,
                         camera_registration: "CameraRegistration") \
            -> bool:
        if not region_queue or region_queue.empty() or not camera_registration:
            return False

        try:
            gpp = GeoPosition.point_to_geoposition(point=camera_registration.ground_plane_position)
            densitymap_conf = DensityMapConfiguration(ground_plane_position=gpp,
                                                      bearing_map=camera_registration.ground_plane_orientation,
                                                      )

            self.number_people = region_queue.get_count_element()
            self.extensionregion_squaremeters = region_queue.get_matrixcell_count()

            list_row_shapes = region_queue.get_rowshapesvertex()

            if not list_row_shapes:
                return False

            polygon_region_matrix = QueueDetectionAlgorithm.convert_region_to_polygon(region_queue_shape=region_queue)
            logger.debug('QueueDetetectionAlert set_region_queue 2, type_polygon: {}'
                        .format(type(polygon_region_matrix).__name__))
            polygon_matrix_coords = \
                QueueDetectionAlgorithm.convert_polygon_to_matrix_coords(
                    polygon=polygon_region_matrix
                )

            self.geographyc_area = QueueDetectionAlgorithm.convert_matrixpolygon_to_geo_area(polygon_matrix_coords=polygon_matrix_coords,
                                                                                             densitymap_conf=densitymap_conf)

            return True
        except Exception as ex:
            logger.error('QueueDetetectionAlert set_region_queue Exception: {}'.format(ex))
            return False

    def get_list_keys(self) -> List[str]:
        return [QueueDetectionAlertLabels.LABEL_DICTIONARY_SPECIFIC_ID,
                QueueDetectionAlertLabels.LABEL_DICTIONARY_SHAPEID,
                QueueDetectionAlertLabels.LABEL_DICTIONARY_TIMESTAMP,
                QueueDetectionAlertLabels.LABEL_DICTIONARY_QUEUECOUNT,
                QueueDetectionAlertLabels.LABEL_DICTIONARY_QUEUESIZEAREA,
                QueueDetectionAlertLabels.LABEL_DICTIONARY_THRESHOLD_ALERT,
                QueueDetectionAlertLabels.LABEL_DICTIONARY_DESCRIPTION,
                QueueDetectionAlertLabels.LABEL_DICTIONARY_GEOGRAPHIC_REGION,
                QueueDetectionAlertLabels.LABEL_DICTIONARY_MEANPEOPLE,
                QueueDetectionAlertLabels.LABEL_DICTIONARY_OBSIOTID,
                QueueDetectionAlertLabels.LABEL_DICTIONARY_DEVICEINPUTID
                ]

    def get_specific_value(self, key: str) -> Any:
        if not key:
            return None
        if key == QueueDetectionAlertLabels.LABEL_DICTIONARY_SPECIFIC_ID:
            return self.qda_id
        elif key == QueueDetectionAlertLabels.LABEL_DICTIONARY_SHAPEID:
            return self.qsma_id
        elif key == QueueDetectionAlertLabels.LABEL_DICTIONARY_TIMESTAMP:
            return self.timestamp
        elif key == QueueDetectionAlertLabels.LABEL_DICTIONARY_QUEUECOUNT:
            return self.number_people
        elif key == QueueDetectionAlertLabels.LABEL_DICTIONARY_THRESHOLD_ALERT:
            return self.threshold_alert
        elif key == QueueDetectionAlertLabels.LABEL_DICTIONARY_DESCRIPTION:
            return "HLDFAD Queue Detection Alert"
        elif key == QueueDetectionAlertLabels.LABEL_DICTIONARY_QUEUESIZEAREA:
            return self.extensionregion_squaremeters
        elif key == QueueDetectionAlertLabels.LABEL_DICTIONARY_MEANPEOPLE:
            return self.mean_people
        elif key == QueueDetectionAlertLabels.LABEL_DICTIONARY_GEOGRAPHIC_REGION:
            return self.geographyc_area
        elif key == QueueDetectionAlertLabels.LABEL_DICTIONARY_OBSIOTID:
            return self.obs_iot_id
        elif key == QueueDetectionAlertLabels.LABEL_DICTIONARY_DEVICEINPUTID:
            return self.device_id
        return None


class DictionaryHelper:
    @staticmethod
    def list_to_documents(list_observables: List[ObservableGeneric]) -> List[dict]:
        if not list_observables:
            return None

        list_dictionaries = list()
        for observable in list_observables:
            list_dictionaries.append(observable.to_dictionary())

        return list_dictionaries


class Localization(ObservableGeneric):
    def __init__(self, device=None):
        super().__init__()
        self.key = 0
        self.device = device
        self.position = Point(x=0, y=0, srid=4326)
        self.pilot_name = ''
        self.type = ''
        self.area_id = ''
        self.crowd_heatmap_associated = 0

    def save(self):
        self.key = self.observation_id
        return True

    def set_position(self, latitude, longitude):
        self.position = Point(x=longitude, y=latitude, srid=4326)

    def set_output_id(self, output_id: int):
        self.crowd_heatmap_associated = output_id

    def get_output_id(self) -> int:
        return self.crowd_heatmap_associated

    @classmethod
    def from_json(cls, json_data):
        return cls(json_data)
        # or something like:
        # instance = cls()
        # instance.attr1 = json_data['attr1']
        # ...

    def to_json(self) -> str:
        return json.dumps({
            'device': self.device,
            'position': self.position,
            'timestamp': self.timestamp,
            'pilot_name': self.pilot_name,
            'crowd_heatmap_associated': self.crowd_heatmap_associated,
            'observation_id': self.observation_id,
            'type': self.type,
            'areaId': self.area_id,
            'tagId': self.get_device_id()
        })

    def get_type_observable(self):
        return LabelObservationType.LABEL_OBSTYPE_LOCALIZATION

    def from_dictionary(self, dictionary: Dict[str, Any]) -> bool:
        try:
            if not dictionary:
                return False

            for key in dictionary:
                value = dictionary[key]

                if not value:
                    continue

                if key == 'lat':
                    self.position.y = value
                elif key == 'lon':
                    self.position.x = value
                elif key == 'device':
                    self.device_id = value
                elif key == 'pilot_name':
                    self.pilot_name = value
                elif key == 'crowd_heatmap_associated':
                    self.crowd_heatmap_associated = value
                elif key == 'timestamp':
                    self.timestamp = isoparse(value)
                elif key == 'obs_id':
                    self.observation_id = value
                elif key == 'type':
                    self.type = value
                elif key == 'areaId':
                    self.area_id = value
                elif key == 'tagId':
                    self.set_device_id(device_id=value)

        except Exception as ex:
            logger.error('Localization FromDictionary Exception: {}'.format(ex))

    def to_dictionary(self) -> Dict[str, Any]:
        try:
            dictionary_ret = {
                'device': self.get_device_id(),
                'lat': self.position.y,
                'lon': self.position.x,
                'obs_id': self.get_observable_id(),
                'pilot_name': self.pilot_name,
                'crowd_heatmap_associated': self.crowd_heatmap_associated,
                # 'run_id': str(self.get_run_id()),
                'timestamp': self.get_timestamp().isoformat()
            }

            return dictionary_ret
        except Exception as ex:
            logger.error('convert_observation_to_dictionary Exception: {}'.format(ex))


class MonitoringArea(Dictionarizable):
    def __init__(self, pilot_name: str):
        self.pilot_name = pilot_name
        self.ground_plane_position = None
        self.horizontal_size_m = 0
        self.vertical_size_m = 0
        self.cell_size_m = 0
        self.latitude = 0
        self.longitude = 0
        self.ground_plane_position = Point(x=0, y=0, srid=4326)

    def set_single_property(self, key: str, value: Any) -> bool:
        if not key:
            return False

        if key == LabelDictionaryMonitoringArea.LABEL_DICTIONARY_LATITUDE:
            self.ground_plane_position.y = value
            return True

        elif key == LabelDictionaryMonitoringArea.LABEL_DICTIONARY_LONGITUDE:
            self.ground_plane_position.x = value
            return True

        elif key == LabelDictionaryMonitoringArea.LABEL_DICTIONARY_HORIZONTALSIZE_M:
            self.horizontal_size_m = value
            return True

        elif key == LabelDictionaryMonitoringArea.LABEL_DICTIONARY_CELLSIZE_M:
            self.cell_size_m = value
            return True

        elif key == LabelDictionaryMonitoringArea.LABEL_DICTIONARY_VERTICALSIZE_M:
            self.vertical_size_m = value
            return True

        return False

    def to_string(self) -> str:
        try:
            return json.dumps({"Latitude": self.latitude,
                               "Longitude:": self.longitude,
                               "PilotName": self.pilot_name,
                               "HorizontalSize_m": self.horizontal_size_m,
                               "VerticalSize_m": self.vertical_size_m,
                               "CellSize_m": self.cell_size_m})
        except:
            return str("")


# {
#     LabelDictionaryQueueShapeArea.LABEL_FORCESTATICAPPR_INDEXROW: 6,
#     LabelDictionaryQueueShapeArea.LABEL_FORCESTATICAPPR_RANGECOLUMNS: [range(0, 9)]
# },

class ForceStaticResearchIndexes(Dictionarizable):
    def __init__(self):
        self.index_row = 0
        self.list_index_columns = list()

    def get_list_index_columns(self) -> List[int]:
        return self.list_index_columns

    def set_single_property(self, key: str, value: Any) -> bool:
        try:
            if not key or not value:
                return False

            if key == LabelDictionaryQueueShapeArea.LABEL_FORCESTATICAPPR_INDEXROW:
                self.index_row = value
                return True
            elif key == LabelDictionaryQueueShapeArea.LABEL_FORCESTATICAPPR_RANGECOLUMNS:
                self.list_index_columns = value
                return True

            return False
        except Exception as ex:
            logger.error('ForceStaticResearchIndexes set_single_property Exception: {}'.format(ex))
            return False


class ForceStaticResearch(Dictionarizable):
    def __init__(self):
        self.listelement_indexes = list()
        self.camera_id = str('')

    def get_listelement_indexes(self) -> List[ForceStaticResearchIndexes]:
        return self.listelement_indexes

    @staticmethod
    def get_list_forcestaticresearchindexes(list_dictionaries: List[Dict[str, Any]]) -> List[ForceStaticResearchIndexes]:
        try:
            if not list_dictionaries:
                return None

            list_return = list()

            for dictionary in list_dictionaries:
                forceindex = ForceStaticResearchIndexes()

                if not forceindex.from_dictionary(dictionary=dictionary):
                    del forceindex
                    continue
                list_return.append(forceindex)

            return list_return
        except Exception as ex:
            logger.error('{}'.format(ex))
            return None

    def set_single_property(self, key: str, value: Any) -> bool:
        try:
            if not key or not value:
                return False

            if key == LabelDictionaryQueueShapeArea.LABEL_FORCESTATICAPPR_ARRAYELEMENT_QUEUESHAPE:
                self.listelement_indexes = ForceStaticResearch.get_list_forcestaticresearchindexes(list_dictionaries=value)
                return True

            elif key == LabelDictionaryQueueShapeArea.LABEL_FORCESTATICAPPR_CAMERA_ID:
                self.camera_id = value
                return True
        except Exception as ex:
            logger.error('ForceStaticResearch set_single_property Exception: {}'.format(ex))
            return False


class DeviceType(Enum):
    NOT_DEFINED = 0,
    CAMERA = 1,
    WRISTBAND = 2


class DeviceRegistration(Dictionarizable):
    def __init__(self):
        self.datastream_id: int = 0
        self.pilot_name: str = str()
        self.device_id: str = str()
        self.obs_type : str = str()
        self.device_type: DeviceType = DeviceType.NOT_DEFINED

    def set_associated_obs_type(self, obs_type: str):
        self.obs_type = obs_type

    def get_obs_type(self):
        return self.obs_type

    def get_device_id(self) -> str:
        return self.device_id

    def set_device_id(self, device_id: str):
        self.device_id = device_id

    def get_device_type(self) -> DeviceType:
        return self.device_type

    def set_device_type(self, device_type: DeviceType):
        self.device_type = device_type

    def set_datastream_id(self, datastream_id: str):
        self.datastream_id = datastream_id

    def set_pilot_name(self, pilot_name: str):
        self.pilot_name = pilot_name

    def get_pilot_name(self) -> str:
        return self.pilot_name

    def get_datastream_id(self) -> str:
        return self.datastream_id

    def to_dictionary(self) -> Dict[str, Any]:
        raise NotImplementedError

    def set_single_property_father(self, key: str, value: Any) -> bool:
        try:
            if not key or not value:
                return False

            if key == "deviceid":
                self.set_device_ic(device_id=value)
                return True

            if key == 'datastreamid':
                self.datastream_id = value
                return True

            if key == 'pilot_name':
                self.pilot_name = value
                return True

            if key == 'device_type':
                self.device_type = value
                return True

            return False
        except Exception as ex:
            return False

    def set_single_property_child(self, key: str, value: Any) -> bool:
        raise NotImplementedError

    def set_single_property(self, key: str, value: Any) -> bool:
        if self.set_single_property_father(key=key,
                                               value=value):
            return True
        return self.set_single_property_child(key=key,
                                              value=value)

    def add_list_child(self) -> List[str]:
        raise NotImplementedError

    def get_specific_value_child(self, key: str):
        raise NotImplementedError

    def get_list_keys(self) -> List[str]:
        list_return = list()
        list_return.append("deviceid")
        list_return.append("datastreamid")
        list_return.append("device_type")
        list_return.append("pilot_name")

        list_child = self.add_list_child()
        if list_child:
            list_return.extend(list_child)
        return list_return

    def get_specific_value(self, key: str) -> Any:
        if key == "datastreamid":
            return self.datastream_id

        if key == "deviceid":
            return self.device_id

        if key == "device_type":
            return self.device_type

        if key == "pilot_name":
            return self.pilot_name

        return self.get_specific_value_child(key)


class WristbandRegistration(DeviceRegistration):
    LABEL_WRISTBANDREGISTRATION_PHYSICALID = "buttonId"
    LABEL_WRISTBANDREGISTRATION_TAGID = "tagId"
    LABEL_WRISTBANDREGISTRATION_TYPE = "type"

    def __init__(self,
                 phy_id: int = 0,
                 pilot_name: str = str(),
                 tag_id: str = str(),
                 wristband_type: str = "868",
                 device_type: DeviceType = DeviceType.WRISTBAND):
        super().__init__()
        self.phy_id = phy_id
        self.tag_id = tag_id
        self.wristband_type = wristband_type
        self.pilot_name = pilot_name
        self.set_device_type(device_type=device_type)

    @classmethod
    def from_json(cls, json_data):
        return cls(json_data)

    def to_json(self) -> str:
        return json.dumps(self.to_dictionary())

    def add_list_child(self) -> List[str]:
        list_return = list()
        list_return.append(WristbandRegistration.LABEL_WRISTBANDREGISTRATION_PHYSICALID)
        list_return.append(WristbandRegistration.LABEL_WRISTBANDREGISTRATION_TAGID)
        list_return.append(WristbandRegistration.LABEL_WRISTBANDREGISTRATION_TYPE)

        return list_return

    def get_specific_value_child(self, key: str) -> Any:
        if key == WristbandRegistration.LABEL_WRISTBANDREGISTRATION_PHYSICALID:
            return self.phy_id

        elif key == WristbandRegistration.LABEL_WRISTBANDREGISTRATION_TAGID:
            return self.tag_id

        elif key == WristbandRegistration.LABEL_WRISTBANDREGISTRATION_TYPE:
            return self.wristband_type

        return None

    def set_single_property_child(self, key: str,
                                  value: Any) -> bool:
        try:
            if key == WristbandRegistration.LABEL_WRISTBANDREGISTRATION_PHYSICALID:
                self.phy_id = value
                return True

            elif key == WristbandRegistration.LABEL_WRISTBANDREGISTRATION_TAGID:
                self.tag_id = value
                return True

            elif key == WristbandRegistration.LABEL_WRISTBANDREGISTRATION_TYPE:
                self.wristband_type = value
                return True

        except Exception as ex:
            logger.error('CameraRegistration FromDictionary Exception: {}'.format(ex))
            return False


class CameraRegistration(DeviceRegistration):
    LABEL_CAMERAREGISTRATION_GROUNDPLANEPOSITION = "ground_plane_position"
    LABEL_CAMERAREGISTRATION_GROUNDPLANEORIENTATION = "ground_plane_orientation"
    LABEL_CAMERAREGISTRATION_CAMERAID = "camera_id"
    LABEL_CAMERAREGISTRATION_GROUNDPLANESIZE = "ground_plane_size"

    def __init__(self,
                 ground_plane_position: Point = None,
                 ground_plane_orientation: int = 0,
                 pilot_name: str = str(),
                 device_type: DeviceType = DeviceType.CAMERA):
        super().__init__()
        self.ground_plane_position = ground_plane_position
        self.ground_plane_orientation = ground_plane_orientation
        self.size_area_x = 0
        self.size_area_y = 0
        self.pilot_name = pilot_name
        self.set_device_type(device_type=device_type)

    def set_position(self, position_vect: List[float]):
        if not position_vect or position_vect.count() < 2:
            return
        self.ground_plane_position = Point(x=position_vect[1], y=position_vect[0], srid=4326)

    @classmethod
    def from_json(cls, json_data):
        return cls(json_data)
        # or something like:
        # instance = cls()
        # instance.attr1 = json_data['attr1']
        # ...

    def to_json(self) -> str:
        return json.dumps(self.to_dictionary())

    def add_list_child(self) -> List[str]:
        list_return = list()
        list_return.append(CameraRegistration.LABEL_CAMERAREGISTRATION_GROUNDPLANEPOSITION)
        list_return.append(CameraRegistration.LABEL_CAMERAREGISTRATION_CAMERAID)
        list_return.append(CameraRegistration.LABEL_CAMERAREGISTRATION_GROUNDPLANEORIENTATION)
        list_return.append(CameraRegistration.LABEL_CAMERAREGISTRATION_GROUNDPLANESIZE)

        return list_return

    def get_specific_value_child(self, key: str) -> Any:
        if key == CameraRegistration.LABEL_CAMERAREGISTRATION_GROUNDPLANEPOSITION and self.ground_plane_position:
            return [self.ground_plane_position.y, self.ground_plane_position.x]

        elif key == CameraRegistration.LABEL_CAMERAREGISTRATION_CAMERAID:
            return self.get_device_id()

        elif key == CameraRegistration.LABEL_CAMERAREGISTRATION_GROUNDPLANEORIENTATION:
            return self.ground_plane_orientation

        elif key == CameraRegistration.LABEL_CAMERAREGISTRATION_GROUNDPLANESIZE:
            return [self.size_area_x, self.size_area_y]

        return None

    def set_single_property_child(self, key: str, value: Any) -> bool:
        try:
            if key == CameraRegistration.LABEL_CAMERAREGISTRATION_GROUNDPLANEPOSITION:
                if len(value) < 2:
                    return False

                # FIXME: TO BE SOLVED SCRAL SIDE

                latitude = max(value)
                longitude = min(value)

                self.ground_plane_position = Point(x=longitude,
                                                   y=latitude,
                                                   srid=4326)
                return True

            elif key == CameraRegistration.LABEL_CAMERAREGISTRATION_GROUNDPLANEORIENTATION:
                self.ground_plane_orientation = value
                return True

            elif key == CameraRegistration.LABEL_CAMERAREGISTRATION_CAMERAID:
                self.set_device_id(device_id=value)
                return True

            elif key == CameraRegistration.LABEL_CAMERAREGISTRATION_GROUNDPLANESIZE:
                if len(value) < 2:
                    return False

                self.size_area_x = value[0]
                self.size_area_y = value[1]
                return True

        except Exception as ex:
            logger.error('CameraRegistration FromDictionary Exception: {}'.format(ex))
            return False


class DeviceRegistrationAdapter:
    @staticmethod
    def convert_from_dictionary_static(dictionary: Dict[str, Any]) -> DeviceRegistration:
        try:
            if not dictionary:
                return None

            if "device_type" not in dictionary or type(dictionary["device_type"] is not DeviceType):
                return None

            if dictionary["device_type"] == DeviceType.CAMERA:
                return CameraRegistration().from_dictionary(dictionary=dictionary)

            return None
        except Exception as ex:
            return None

    @staticmethod
    def dynamic_cast_camera_registration(device_registration: DeviceRegistration) -> CameraRegistration:
        return device_registration


import numpy as np


class CrowdDensityLocalObservation(ObservableGeneric):
    def __init__(self):
        super().__init__()
        self.module_id = str('')
        self.camera_registration = None
        self.timestamp = None
        self.density_map = np.ndarray(shape=[0])
        self.ground_plane_position = Point(x=0,
                                           y=0,
                                           srid=4326)
        self.density_count = 0
        self.size_area_x = 0
        self.size_area_y = 0
        self.is_element_adjusted = False

    @staticmethod
    def cast_listobservables_to_list_crowddensitylocal(list_observables: List[ObservableGeneric]) -> List["CrowdDensityLocalObservation"]:
        return list_observables

    def get_cameraregistration(self) -> CameraRegistration:
        return self.camera_registration

    def to_trace_string(self):
        return str({
            "camera_id": self.get_device_id(),
            "timestamp": self.get_timestamp().isoformat(),
            "density_count": self.density_count,
            "obs_id": self.get_observable_id()
        })

    @staticmethod
    def acquire_matrix(original_matrix: List[List[float]]) -> np.matrix:
        if not original_matrix:
            return None

        try:
            number_rows = len(original_matrix)
            number_column = len(original_matrix[0])

            matrix_out = np.zeros(shape=[number_rows, number_column], dtype=int)

            for index_row in range(0, number_rows):
                for index_col in range(0, number_column):

                    if np.isnan(original_matrix[index_row][index_col]):
                        logger.error('CrowdDensityLocalObservation Found NAN Value: ')
                        return matrix_out

                    matrix_out[index_row, index_col] = int(original_matrix[index_row][index_col])

            return matrix_out
        except Exception as ex:
            logger.error('CrowdDensityLocalObservation acquire_matrix Exception: {}'.format(ex))
            return np.matrix(data=[])

    def ckeck_observable_complete(self) -> bool:
        if not self.get_device_id() or self.density_map.size == 0 or not self.timestamp:
            return False

        return True

    def from_dictionary(self, dictionary: Dict[str, Any]) -> bool:
        try:
            if not dictionary:
                return False

            for key in dictionary.keys():
                value = dictionary[key]

                if value is None:
                    continue

                if key == 'density_map':
                    self.density_map = CrowdDensityLocalObservation.acquire_matrix(original_matrix=value)
                elif key == 'timestamp_2':
                    self.timestamp = isoparse(value)
                elif key == 'density_count':
                    self.density_count = value
                elif key == 'camera_ids':
                    self.set_device_id(value[0])
                elif key == 'module_id':
                    self.module_id = value
            return self.ckeck_observable_complete()
        except Exception as ex:
            logger.error('CrowdDensityLocalObservation from_dictionary Exception: {}'.format(ex))
            return False

    def set_info_registration(self, device_registration: DeviceRegistration) -> bool:
        try:
            if not device_registration:
                return False

            if device_registration.get_datastream_id() != self.get_datastream_id():
                return False

            camera_registration = DeviceRegistrationAdapter.dynamic_cast_camera_registration(device_registration=device_registration)

            if not camera_registration:
                return False

            self.ground_plane_position = camera_registration.ground_plane_position
            self.camera_registration = camera_registration
            self.size_area_x = camera_registration.size_area_x
            self.size_area_y = camera_registration.size_area_y

            return True

        except Exception as ex:
            logger.error('CrowdDensityLocalObservation set_info_registration Exception: {}'.format(ex))
            return False

    def get_type_observable(self) -> str:
        return LabelObservationType.LABEL_OBSTYPE_CROWDDENSITY

    def to_dictionary(self) -> Dict[str, Any]:
        try:
            return {
                "camera_id": self.get_device_id(),
                "timestamp": self.timestamp,
                "density_map": self.density_map,
                "Lat": self.ground_plane_position.y,
                "Long": self.ground_plane_position.x,
                "SizeAreaX": self.size_area_x,
                "SizeAreaY": self.size_area_y,
                "densityCount": self.density_count
            }

        except Exception as ex:
            return None

    def save(self) -> bool:
        return True