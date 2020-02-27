from typing import Dict, Any, List
import logging

logger = logging.getLogger('textlogger')


class UtilityDictionaries:
    @staticmethod
    def get_dict_field_if(dictionary: Dict[str, Any],
                          label: str,
                          none_value: Any = None) -> Any:
        try:
            if not dictionary:
                return None

            if label not in dictionary.keys():
                return none_value

            return dictionary[label]
        except Exception as ex:
            logger.error('UtilityDictionaries get_dict_field_if Exception: {}'.format(ex))
            return None


class UtilityList:
    @staticmethod
    def get_list_noduplicates(list_to_clean: List[Any]) -> List[Any]:
        if not list_to_clean:
            return None

        return list(dict.fromkeys(list_to_clean))