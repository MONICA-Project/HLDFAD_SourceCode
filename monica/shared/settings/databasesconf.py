import os
import logging

logger = logging.getLogger('textlogger')

DATABASES = {
    'default':
        {
            'ENGINE': 'django.contrib.gis.db.backends.postgis',
            'NAME': os.environ.get('DB_NAME', ''),
            'USER':  os.environ.get('DB_USER', ''),
            'PASSWORD': os.environ.get('DB_PASSWORD', ''),
            'HOST': os.environ.get('DB_PORT_5432_TCP_ADDR', os.environ.get('PGSQL_HOST', '')),
            'PORT': os.environ.get('DB_PORT_5432_TCP_PORT', '5432'),
        }
}

try:
    engine_db = os.environ.get('ENV_SELECT_DB_TYPE', 'posgresql')

    if engine_db == 'spatialite':
        DATABASES['default']['ENGINE'] = 'django.contrib.gis.db.backends.spatialite'
    elif engine_db == 'sqlite':
        DATABASES['default']['ENGINE'] = 'django.db.backends.sqlite3'

    logger.info('DOCKER DATABASES DICTIONARY Done')

except Exception as ex:
    logger.error('DOCKER DATABASES DICTIONARY Exception: {}'.format(ex))


# logger.info('DOCKER DATABASES DICTIONARY: {}'.format(DATABASES))
