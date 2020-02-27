import os
from typing import Any
import logging

logger = logging.getLogger('textlogger')


class UtilityEnvironment:
    @staticmethod
    def get_envvar_type(env_name: str,
                        type_var: type,
                        value_if_no: Any):
        try:
            value_string = os.environ.get(env_name, '')

            if not value_string:
                logger.info('UtilityEnvironment Unable To Read Env Value {0}. Set Default {1}'.format(env_name,
                                                                                                      value_if_no))
                return value_if_no

            if type_var == str:
                return value_string
            elif type_var == bool:
                if value_string.upper() == "TRUE":
                    return True
                return False
            elif type_var == int:
                return int(value_string)
            elif type_var == float:
                return float(value_string)
            return value_string
        except Exception as ex:
            logger.error('UtilityEnvironment Exception {0}: {1}'.format(env_name, ex))
            return value_if_no