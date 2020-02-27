from typing import List, Dict, Any, Union
from general_types.label_ogc import LabelThings, LabelObservationType, LabelOGCDatastreams

PILOT_SELECTED = 'TIVOLI'
DEBUG_DEFAULT_SELECTED_GOST = 'GOST_' + PILOT_SELECTED
# DEBUG_DEFAULT_SELECTED_GOST = 'GOST_'+DEBUG_DEFAULT_SELECTED_PILOT


class GOSTProvider:
    @staticmethod
    def get_datastream(gost: str, id: int) -> str:
        return '{0}/Datastreams({1})/Observations'.format(gost, id)

    @staticmethod
    def get_device_id(pilot_name: str,
                      id: int) -> str:
        return 'SFN/Camera/CDL-Estimation/{0}'.format(GOSTProvider.get_device_name(pilot_name=pilot_name,
                                                                                   id=id)
                                                      )

    @staticmethod
    def get_device_name(pilot_name: str,
                        id: int):
        return '{0}_CAM_{1}'.format(pilot_name,
                                    id)


class LabelLocalDicts:
    LABEL_GPP = "ground_plane_position"
    LABEL_GPROT = "ground_plane_orientation"
    LABEL_IOTID = "@iot.id"
    LABEL_NAME = "name"
    LABEL_DESCR = "description"
    LABEL_DEVICENAME = "camera_id"
    LABEL_REGDEVICE = "unitOfMeasurement"
    LABEL_CAMERAID = 'camera_id'
    LABEL_GPSIZE = 'ground_plane_size'

    @staticmethod
    def get_list_labels_registrationdict() -> List[str]:
        return [
            LabelLocalDicts.LABEL_DEVICENAME,
            LabelLocalDicts.LABEL_GPP,
            LabelLocalDicts.LABEL_GPROT,
            LabelLocalDicts.LABEL_GPSIZE
        ]

    @staticmethod
    def get_list_labels_headerregistration() -> List[str]:
        return [
            LabelLocalDicts.LABEL_IOTID,
            LabelLocalDicts.LABEL_DESCR,
            LabelLocalDicts.LABEL_NAME,
            LabelLocalDicts.LABEL_REGDEVICE
        ]


DICTIONARY_LOCATIONS = {
    4156:
        {
            LabelLocalDicts.LABEL_DEVICENAME: 25,
            LabelLocalDicts.LABEL_GPP: [55.67474, 12.56539],
            LabelLocalDicts.LABEL_GPROT: 250,
            LabelLocalDicts.LABEL_GPSIZE: [10, 18]
        },
    4157:
        {
            LabelLocalDicts.LABEL_DEVICENAME: 26,
            LabelLocalDicts.LABEL_GPP: [55.6648, 12.56573],
            LabelLocalDicts.LABEL_GPROT: 90,
            LabelLocalDicts.LABEL_GPSIZE: [10, 18]
        }
}

DICTIONARY_OBSERVABLE_TOPICS = {
    4156: [GOSTProvider.get_datastream(gost=DEBUG_DEFAULT_SELECTED_GOST, id=4156),
           GOSTProvider.get_device_id(pilot_name=PILOT_SELECTED, id=25)],
    4157: [GOSTProvider.get_datastream(gost=DEBUG_DEFAULT_SELECTED_GOST, id=4157),
           GOSTProvider.get_device_id(pilot_name=PILOT_SELECTED, id=26)],
}


class RegistrationJSONMaker:

    @staticmethod
    def get_complete_regdevicedict(iot_id: int,
                                   list_single_topic: List[str],
                                   dict_descr_single_dev: Dict[str, Any]) -> Dict[str, Any]:
        try:
            if not list_single_topic or not dict_descr_single_dev:
                return None

            headers = LabelLocalDicts.get_list_labels_headerregistration()

            dict_return = dict()

            for header in headers:
                if not header:
                    continue
                value = None
                if header == LabelLocalDicts.LABEL_IOTID:
                    value = iot_id
                elif header == LabelLocalDicts.LABEL_NAME:
                    value = list_single_topic[1]
                elif header == LabelLocalDicts.LABEL_DESCR:
                    value = "Datastream for Estimation of Crowd Density Local"
                elif header == LabelLocalDicts.LABEL_REGDEVICE:
                    value = \
                        RegistrationJSONMaker.get_registration_dict(dict_input=dict_descr_single_dev)

                if value is None:
                    continue

                dict_return[header] = value

            return dict_return
        except:
            return None

    @staticmethod
    def get_registration_dict(
            dict_input: Dict[str, Any]) \
            -> Dict[str, Any]:
        labels = LabelLocalDicts.get_list_labels_registrationdict()

        if not labels:
            return None

        dict_ret: Dict[str, Union[str, Any]] = dict()

        for label in labels:
            if not label:
                continue

            value = dict_input[label]

            if label == LabelLocalDicts.LABEL_DEVICENAME:
                value = GOSTProvider.get_device_name(pilot_name=PILOT_SELECTED,
                                                     id=value)
            if not value:
                continue

            dict_ret[label] = value

        return dict_ret

    @staticmethod
    def get_dictionary_thing_cdl():
        return {LabelObservationType.LABEL_OBSTYPE_CROWDDENSITY: LabelOGCDatastreams.LABEL_DATASTREAM_CROWDDENSITYLOCAL}

    @staticmethod
    def get_prefix_topic():
        return DEBUG_DEFAULT_SELECTED_GOST

    @staticmethod
    def get_thing_name():
        return LabelThings.LABEL_THING_SFN

    @staticmethod
    def get_complete_registrationdevices_dicts() -> Dict[str, List[Any]]:
        if not DICTIONARY_OBSERVABLE_TOPICS or not DICTIONARY_LOCATIONS:
            return None

        dict_return = dict()
        list_devices = list()

        for iot_id in DICTIONARY_OBSERVABLE_TOPICS.keys():
            if iot_id not in DICTIONARY_LOCATIONS.keys():
                continue

            list_single_topic = DICTIONARY_OBSERVABLE_TOPICS[iot_id]
            dict_descr_single_dev = DICTIONARY_LOCATIONS[iot_id]

            if not list_single_topic:
                continue

            if not dict_descr_single_dev:
                continue

            single_device_reg = RegistrationJSONMaker.get_complete_regdevicedict(iot_id=iot_id,
                                                                                 list_single_topic=list_single_topic,
                                                                                 dict_descr_single_dev=dict_descr_single_dev)

            if not single_device_reg:
                continue

            list_devices.append(single_device_reg)

        if not list_devices:
            return None

        return {
            'value':
                list_devices
        }

DEBUG_PREFIX_CAMERA = str('SFN/Camera/')
DEBUG_PREFIX_CAMERA_CDL = DEBUG_PREFIX_CAMERA+'CDL-Estimation/'
DEBUG_PREFIX_CAMERASIMPLENAME=PILOT_SELECTED+'_CAM_'

DICTIONARY_OBSERVABLE_TOPICS_CAMERAS = {
    56: [DEBUG_DEFAULT_SELECTED_GOST+'/Datastreams(56)/Observations', DEBUG_PREFIX_CAMERA_CDL+DEBUG_PREFIX_CAMERASIMPLENAME+'4']
}
