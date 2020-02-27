from shared.settings.appstableconf import THINGS_TO_ANALYSE, MAPPING_OUTPUT_DATASTREAMS
from shared.settings.appglobalconf import LIST_OUTPUT_MESSAGES
from typing import List, Dict, Any
from general_types.modelsenums import OutputMessageType
import logging

logger = logging.getLogger('textlogger')


class UtilitySettings:
    @staticmethod
    def find_key_thing(things_dictionary: Dict[str, Dict[str, str]],
                       datastream_name: str) -> str:
        if not things_dictionary:
            return str()

        for thing_name in things_dictionary.keys():
            datastreams = things_dictionary[thing_name]

            if not datastreams:
                continue

            if datastream_name not in datastreams.keys():
                continue

            return thing_name

        return str()

    @staticmethod
    def create_dictionary_things_datastream(dict_global: Dict[str, Dict[str, str]],
                                            list_output_types: List[OutputMessageType],
                                            mapping_output_datastreams: Dict[OutputMessageType, List[str]]) -> Dict[str, Dict[str, str]]:
        if not dict_global or not list_output_types or not mapping_output_datastreams:
            return None

        dict_return = dict()

        try:
            for output_type in list_output_types:
                if output_type not in mapping_output_datastreams.keys():
                    continue

                list_datastrams_useful = mapping_output_datastreams[output_type]

                if not list_datastrams_useful:
                    continue

                for datastream in list_datastrams_useful:
                    name_thing = UtilitySettings.find_key_thing(things_dictionary=dict_global,
                                                                datastream_name=datastream)
                    if not name_thing or name_thing not in dict_global.keys():
                        continue

                    thing_dict = dict_global[name_thing]

                    dict_return[name_thing] = {datastream: thing_dict[datastream]}
            return dict_return
        except Exception as ex:
            logger.error('UtilitySettings Exception: {}'.format(ex))
            return None

    @staticmethod
    def get_global_dict_thing_datastream():
        return UtilitySettings.create_dictionary_things_datastream(dict_global=THINGS_TO_ANALYSE,
                                                                   list_output_types=LIST_OUTPUT_MESSAGES,
                                                                   mapping_output_datastreams=MAPPING_OUTPUT_DATASTREAMS)