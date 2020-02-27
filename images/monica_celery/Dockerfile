FROM monicaproject/hldfad_worker_os:02.06.01.00

RUN mkdir /code

# FIXME: ENABLE the following line in order to create Dockerhub image
COPY ./monica /code/

COPY ./images/monica_celery/entrypoint/celery_entrypoint.sh /

# Update C env vars so compiler can find gdal
ENV CPLUS_INCLUDE_PATH=/usr/include/gdal
ENV C_INCLUDE_PATH=/usr/include/gdal

WORKDIR /code

RUN apt-get install -y dos2unix
RUN apt-get install -y netcat

RUN dos2unix /celery_entrypoint.sh && apt-get --purge remove -y dos2unix && rm -rf /var/lib/apt/lists/*

RUN chmod 777 /celery_entrypoint.sh
RUN chmod 777 /code/shared/settings/appglobalconf.py

ENTRYPOINT ["/celery_entrypoint.sh"]