#FROM monicaproject/hldfad_worker_os:02.06.01.00
FROM antoniodefina1980/django-celery-unofficial:alpine-00.00.02.00

RUN mkdir /code

# FIXME: ENABLE the following line in order to create Dockerhub image
COPY ./monica /code/

COPY ./volumes/monica_celery/entrypoint/celery_entrypoint.sh /

# Update C env vars so compiler can find gdal
ENV CPLUS_INCLUDE_PATH=/usr/include/gdal
ENV C_INCLUDE_PATH=/usr/include/gdal

WORKDIR /code

RUN apk add dos2unix
RUN dos2unix /celery_entrypoint.sh && apk del dos2unix

RUN chmod 777 /celery_entrypoint.sh
RUN chmod 777 /code/shared/settings/appglobalconf.py

ENTRYPOINT ["/celery_entrypoint.sh"]
# CMD tail -f /dev/null ## NOTE: To access with docker exec -it <docker_compose_name> /bin/ash, enable this row and disable previous one