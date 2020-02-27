from utility.utility_url_conversion import UtilityURLConversion
from typing import List
import logging

logger = logging.getLogger('textlogger')


class ThingAdapter(object):
    LABEL_IOT_ID = '@iot.id'
    LABEL_NAME = 'name'
    LABEL_DESCRIPTION = 'description'
    LABEL_NAVIGATIONLINK = 'Datastreams@iot.navigationLink'

    @staticmethod
    def get_list_keysjson() -> List[str]:
        list_return = list()
        list_return.append(ThingAdapter.LABEL_IOT_ID)
        list_return.append(ThingAdapter.LABEL_NAME)
        list_return.append(ThingAdapter.LABEL_DESCRIPTION)
        # list_return.append(ThingAdapter.LABEL_NAVIGATIONLINK)
        return list_return

    def __init__(self, json_message, pilot_name=str('')):
        self.iot_device_id = ''
        self.name_thing = ''
        self.description = ''
        self.datastream_link = ''
        self.pilot_name = pilot_name

        self.extract_info_json(json_message)

    # FIXME: Complete missing check
    @staticmethod
    def check_info_json_available(json_message):

        if not json_message:
            return False

        list_return = ThingAdapter.get_list_keysjson()

        if not list_return:
            return False

        for label in list_return:
            if label not in json_message.keys():
                return False

        return True

    def set_base_url(self, base_url: str) -> bool:
        if self.datastream_link:
            return True

        if not base_url:
            return False

        self.datastream_link = '{0}({1})/Datastreams'.format(base_url,
                                                             self.iot_device_id)
        return True

    def extract_info_json(self,
                          json_message: dict) -> bool:
        try:
            if not ThingAdapter.check_info_json_available(json_message):
                return False

            for key in json_message.keys():
                value = json_message[key]
                if key == ThingAdapter.LABEL_IOT_ID:
                    self.iot_device_id = value
                elif key == ThingAdapter.LABEL_NAME:
                    self.name_thing = value
                elif key == ThingAdapter.LABEL_DESCRIPTION:
                    self.description = value
                elif key == ThingAdapter.LABEL_NAVIGATIONLINK:
                    self.datastream_link = UtilityURLConversion. \
                        convert_bgwurl_to_vpnurl(value)
            return True
        except Exception as ex:
            logger.error('ThingAdapter extract_info_json Exception: {}'.format(ex))
            return False



