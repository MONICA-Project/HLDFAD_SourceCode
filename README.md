# High Level Data Fusion and Anomaly Detection Module (HLDFAD) Quick Start Guide
<!-- Short description of the project. -->


## HLDFAD Overview

HLDFAD is a back end deputed to provide high level outputs based on acquisition and elaboration of selected on field observables received from MQTT Platform Broker. MQTT input topics are filtered
according to contents reported in Platform GOST Observation Catalog. Output Messages can be provided in MQTT format through internal MQTT Output Broker and\or OGC Service Catalog Output.

The complete bottom-up data chain is the following: 
- On Field Data Sensors (wristband and cameras)
- On Field Gateway
- SCRAL
- LinkSmart
- HLDFAD
- OGC and DSS

Figure below provides a quick overview to give a general understanding about HLDFAD position module.![General MONICA Architecture](https://github.com/MONICA-Project/HLDFAD_SourceCode/blob/master/WP6BreakdownDiagram.png "General Monica Architecture") 

HLDFAD Module actually interacts directly with exchange end point, that are middleware between different MONICA modules. Such elements are reported in the following:
- *WP6 Service Catalog*: Beginning End Point that communicates IOT ID and MQTT output broker for MQTT output messages;
- *OGC Service Catalog*: Beginning End Point that reports all Things and Datastreams available. HLDFAD extracts MQTT Observations topics from there
- *MQTT Broker Observations and Output*: Runtime MQTT endpoint for input observations acquisition and output provisioning

## Definition and Terms
<table>
    <tr>
        <td> Observation </td>
        <td> OGC Paradigm element: Raw timestamped data provided by the field </td>
    </tr>
    <tr>
        <td> Thing </td>
        <td> OGC Paradigm element: Element that can handle multiple datastreams-features (e.g. Security Fusion Node for cameras, Wristband Gateway) </td>
    </tr>
    <tr>
        <td> Datastream </td>
        <td> OGC Paradigm element that refers to a a specific feature of Thing that provides specific observation type (e.g. local density map, wristband location) </td>
    </tr>
    <tr>
        <td> MQTT Platform Broker </td>
        <td> Solution component that provides real time observation from the monitored field [e.g. camera observation, localizations' observations) </td>
    </tr>
    <tr>
        <td> MQTT Output Broker </td>
        <td> HLDFAD Component that can be activated to provide HLDFAD output messages </td>
    </tr>    
    <tr>
        <td> OGC Service Catalog Output </td>
        <td> Solution Component exploited to provide HLDFAD output messages </td>
    </tr>    
    <tr>
        <td> MQTT Datastream Broker </td>
        <td> Solution component that provides real time new datastream for dynamic real time registration </td>
    </tr>
    <tr>
        <td> Platform GOST Observation Catalog </td>
        <td> Solution component (compliant with OGC paradigm) that gives list of datastreams and associated topics for MQTT Platform Broker Subscription </td>
    </tr>
    <tr>
        <td> Security Fusion Node </td>
        <td> On field gateway that perform pre-processing of video cameras images and extracts numerical features provided to MONICA cloud modules </td>
    </tr>
</table>

## Docker Hub

It is available a Docker Hub image monicaproject/hldfad_worker at [DockerHub](https://hub.docker.com/repository/docker/monicaproject/hldfad_worker) web site. Latest tag is 02.06.01.05.

## Main functionalities

Tag 02.06.01.05 of HLFDAD Docker hub images offers the following functionalities:

- Crowd Heatmap, based on Wristbands Localization input
- Queue detection Alert, based on Security Fusion Node density maps.

### Crowd Heatmap

Based on localization received by Wristbands Gateway, HLDFAD calculates people density map, i.e. the occurrency of the positions within a geographic monitored area expressed in terms of geo spatial rectangular matrix.

### Queue Detection Alert

Based on people geospatial density maps received by Security Fusion Nodes, HLDFAD generates geographic polygons with adjacent cells with specific mean of people.

## Detailed Information

### Docker Composition

HLDFAD is a Docker-composed solution relying on Django Python framework. Docker containers that compose the HLDFAD solution are the following: 

- *worker*: Django-Celery main docker, that includes task generation and management (High Level Data Fusion core)
- *rabbit*: Exchange and Queue for Django task system management
- *redis*: Cache for temporarily storage of incoming observation input before elaboration (second most important container after celery)
- *posgresql*: Used only in Development for creating PosgreSQL server and database (in production, it is used an external PosgreSQL Database)

### Core Application

Service worker is the core application. After waiting for startup PosgreSQL database, rabbit and redis, the container starts running, as reported in the following phases:
- **Startup**: it perform migrations of local models to databases if required and then launch celery exchanges for task management.
- **Topic Acquisition**: it connects to OGC Service Catalog in order to retrieve topics for accessing to required observations (based on configuration explained in Section [configuration](#custom-types-and-additional-definition) and queries WP6 Service Catalog to retrieve ID for creating output topics.
- **Topic Subscription**: it connects and requires subscription to MQTT broker in order to start receiving observations filtered.
- **Observation Acquisition**: it receives and parse observations (that are temporarily stored on redis cache)
- **Elaboration**: Processing of received observation retrieved from redis cache. The result is stored in PosgreSQL database.
- **Provisioning**: When processing is completed, it is activated async provisioning that exctracts output messages from database and sends to MQTT Broker using specific topic associated
	
## Repository Contents

In the following it is reported a quick overview of the current repository in terms of folder presentation.

|Folder|Content|Link|
| ---- | -------------------------------- | ---- |
|.| Docker Composes and environment files. Note: docker-compose_os is the file to build up only the base OS for HLDFAD worker|[${REPO_ROOT}](.)|
|environment| It contains files supporting tools for beginning setup project| [${REPO_ROOT}/environment](environment)|
|images| Volumes, Dockerfile, entrypoints and configuration for containers| [${REPO_ROOT}/images](images)| 
|monica| Python Source Code for HLDFAD Worker Docker application (Django-Celery based)| [${REPO_ROOT}/monica](monica)|
|tools| Bash script to startup environment for first usage| [${REPO_ROOT}/tools](tools)|

## HLDFAD Component Configuration

File ${REPO_ROOT}/.env (symbolic link generated after startup setup) reports the environment variables that area mapped on docker-compose file. In the following, the environment variable are categorized in different sub lists. For each variable, it is indicated the name, the matching with default .env value (based on .env reported in Git Hub repository), the type (intended in terms of internal parsing) , an explaination and default value (if available).
See [Getting Started](#getting-started).

### Environment Variables: External Interfaces

Such variables allows to set up this module towards external end point: GOST, MQTT Broker and Service Catalog (Things, Datastreams and topics providers).

| Environment Docker | .env Variable | Type | Meaning | Default Value |
| ---------- | ---------- | ---- | --------------- | ------- |
|**WP6_CATALOG_CONNECTIONURL**| ${V_WP6CATALOG_URL} | *str* | WP6 Service Catalog Connection Hostname||
|**WP6_CATALOG_CONNECTIONPORT**| ${V_WP6CATALOG_PORT} | *int* | WP6 Service Catalog Connection Port||
|**ENV_MQTT_OBSERVATION_URL**| ${V_MQTTOBSERV_URL} | *str* | MQTT Broker Observations and output IP Address||
|**ENV_MQTT_OBSERVATION_PORT**| ${V_MQTTOBSERV_PORT} | *int* | MQTT Broker Observations and output Port||
|**OUTPUT_MQTTBROKER_USERNAME**| ${V_MQTTOUTPUT_USER} | *str* | MQTT Broker Observations and output Username||
|**OUTPUT_MQTTBROKER_PASSWORD**| ${V_MQTTOUTPUT_PWD} | *str* | MQTT Broker Observations and output Password||
|**ENV_CATALOG_PORT**| ${V_CATALOG_PORT} | *int* | OGC Catalog Port||
|**ENV_WEB_BASE_URL**| ${V_BASE_URL} | *str* | OGC IP Address-Domain||
|**ENV_CATALOG_USERNAME**| ${V_CATALOG_USER} | *str* | OGC Catalog Username||
|**ENV_CATALOG_PASSWORD**| ${V_CATALOG_PWD} | *str* | OGC Catalog Password||
|**DB_PORT_5432_TCP_ADDR**| ${PGSQL_WORKER_HOST} | *str* | PosgreSQL Connection Database IP Address ||
|**DB_PORT_5432_TCP_PORT**| ${PGSQL_WORKER_PORT} | *int* | PosgreSQL Connection Database TCP Port)|5432|
|**DB_USER**| ${PGSQL_WORKER_USER} | *str* | PosgreSQL Connection Username||
|**DB_PASSWORD**| ${PGSQL_WORKER_PWD} | *str* | PosgreSQL Connection Password||
|**DB_NAME**| ${PGSQL_WORKER_DB} | *str* | PosgreSQL Connection Database Name||

### Environment Variables: Internal Subnetwork interfaces

Such variables allows to set up this module towards internal sub net docker components interfaces (inside docker-compose file).
| Environment Docker | .env Variable | Type | Meaning | Default Value |
| ---------- | ---------- | ---- | --------------- | ------- |
|**RABBITMQ_DEFAULT_USER**| ${RABBITMQ_USER}|*str* | RabbitMQ Username||
|**RABBITMQ_DEFAULT_PASS**| ${RABBITMQ_PASS}|*str* |RabbitMQ Password||
|**RABBITMQ_HOSTNAME**| rabbit|*str* | RabbitMQ Hostname||
|**RABBITMQ_PORT**| |*str* | RabbitMQ Port|5672|
|**CACHEREDIS_DEFAULT_HOSTNAME**||*str* | Cache Redis Hostname|redis|
|**CACHEREDIS_DEFAULT_PORT**| |*int* | Cache Redis Port|6379|

### Environment Variables: Main Application Configurations

Such variables allows to set up main internal configuration data, in particular the geographic monitored area (useful for Crowd Heatmap computation based on Wristband Localization).

| Environment Docker | .env Variable | Type | Meaning | Default Value |
| ---------- | ---------- | ---- | --------------- | ------- |
|**APPSETTING_MONITORINGAREA_LATITUDE**| ${V_APPSETTING_MONAREA_LAT}|*float*| Crowd Heatmap Output Ground Plane Position Latitude||
|**APPSETTING_MONITORINGAREA_LONGITUDE**| ${V_APPSETTING_MONAREA_LONG}|*float*| Crowd Heatmap Output Ground Plane Position Longitude|| 
|**APPSETTING_MONITORINGAREA_HORIZONTALSIZE_M**| ${V_APPSETTING_MONAREA_HORIZSIZE_M}| *int*| Crowd Heatmap Output Ground Plane Position Horizontal Size, in meters|| 
|**APPSETTING_MONITORINGAREA_VERTICALSIZE_M**| ${V_APPSETTING_MONAREA_VERTSIZE_M}|*int*| Crowd Heatmap Output Ground Plane Position Vertical Size, in meters||
|**APPSETTING_MONITORINGAREA_CELLSIZE_M**| ${V_APPSETTING_MONAREA_CELLSIZE_M}|*int*| Crowd Heatmap Output Ground Plane Position Cell Size, in meter (The single size of square cell)||

### Environment Variables: Additional Application Configurations

Such variables allows to set up main additional configuration data to regulate internal software behaviour.

| Environment Docker | .env Variable | Type | Meaning | Default Value |
| -------- | -------- | ---- | ------------------ | ------- |
|**APPSETTING_ENABLE_EMPTY_CROWD_HEATMAP**| ${V_APPSETTING_ENABLE_EMPTYCROWDHEATMAP}|*bool*| Enable Creation of empty Crowd Heatmap when no observation are received | False|
|**APPSETTING_ENABLE_RANDOM_OUTPUT**| ${V_APPSETTING_ENABLE_RANDOM_OUTPUT}|*bool*| Enable Creation of random Crowd Heatmap when no observation are received| False|
|**APPSETTING_ENABLE_RANDOM_QUEUEDETECTIONALERT**| ${V_APPSETTING_ENABLE_RANDOM_QUEUEDETECTIONALERT}|*bool*| Enable Creation of random Queue Detection Alert when no observation are received||
|**APPSETTING_TASK_ELABORATION_FREQ_SECS**| ${V_APPSETTING_TASK_ELABORATION_FREQ_SECS}|*int*| Interval of forcing elaboration expressed in seconds (independently from observations received)||
|**APPSETTING_TASK_ALIVEAPP_FREQ_SECS**| ${V_APPSETTING_TASK_ALIVEAPP_FREQ_SECS}|*int*| Interval of Task Alive in seconds (it just provides evidence via log that HLDFAD is up and running and the thread are up))|False|
|**APPSETTING_ENABLE_OBS_IOTIDRETRIEVE**| ${V_APPSETTING_ENABLE_OBS_IOTIDRETRIEVE}|*bool*| Enable Retrieving of observation IoT Identifier from OGC Catalog| True |
|**APPSETTING_GOST_NAME**| ${V_APPSETTING_GOST_NAME}|*str*| Beginning Label in composition of observation topics |GOST|
|**APPSETTINGS_ENABLE_IMMELAB**  | ${V_APPSETTINGS_ENABLE_IMMELAB}|*bool*| Enable immediate trigger elaboration of Crowd Heatmap (and-or Queue Detection) when the number of observations unprocessed reaches up the number of associated datastreams |True|
|**CONFENVIRONMENT_GLOBALINFO**| ${V_CONFENVIRONMENT_GLOBALINFO}|*str*| Label To Identify Environment||

**NOTE**:  APPSETTINGS_ENABLE_IMMELAB real name is APPSETTINGS_ENABLE_IMMEDIATEELABORATION_FEEDBYNUMBEROBS, whereas V_APPSETTINGS_ENABLE_IMMELAB real value is V_APPSETTINGS_ENABLE_IMMEDIATEELABORATION_FEEDBYNUMBEROBS. They was changed just for formatting issues

### Custom Types and additional definition

HLDFAD Worker Docker has its own json external configuration file under path [${REPO_ROOT}/images/monica_celery/appconfig/appconfig.json](images/monica_celery/appconfig/appconfig.json).

It allows to enable one or both the output by field **LIST_OUTPUT_MESSAGES**. It is an array of labels that is parsed from application that can includes one or both:

- **OUTPUT_MESSAGE_TYPE_CROWDHEATMAPOUTPUT**: It enables Crowd Heatmap computation based on Wristband Localization. NOTES: it enables also Wristband localization input acquisition (otherwise exluded); 
- **OUTPUT_MESSAGE_TYPE_QUEUEDETECTIONALERT**: It enables Queue Detection Alert based on Security Fusion Node Crowd Density Local Maps messages. NOTES: it enables also Crowd Density Local messages acquisition (otherwise excluded).

## Getting Started
<!-- Instruction to make the project up and running. -->
Ensuring that Docker Engine is correctly installed. Then, after clone current git, from bash shell go to ${REPO_ROOT}/tools folder and launch command:
```bash
${REPO_ROOT}/tools:$ sh configure_docker_environment.sh ${ENV_TYPE}
```

where ${ENV_TYPE} sets the .env environment variables and docker-compose.override file. It can be set to:
- local
- dev
- prod

For local configuration, type:

```bash
${REPO_ROOT}/tools:$ sh configure_docker_environment.sh local
```

### Simulators

Complete execution of such application mainly depends on presence of input messsages. Therefore, it is required to activate input messages from the field (real data) 
or through simulators. There are two simulator already available to test solution:  

- **Wristband Generator**: Java gradle application that emulates Wristband Gateway (it requires SCRAL and LinkSmart)
- **Wristband Complete Generator**: Docker-compose emulator that replace Wristbands, Wristband Gateway, SCRAL and LinkSmart (HLDFAD can connect to it directly)

## Deployment
<!-- Deployment/Installation instructions. If this is software library, change this section to "Usage" and give usage examples -->

### Build

It is possible to create docker container launching command:

```bash
${REPO_ROOT}:$ docker-compose build
```

### Docker
To run the latest version of HLDFAD Module:
```bash
${REPO_ROOT}:$ docker-compose up -d
```

## Development
<!-- Developer instructions. -->

### Prerequisite
This project depends just on Docker Engine. For Linux, instruction installation are available [here](https://runnable.com/docker/install-docker-on-linux).

### Test

The repository itself contains the source code and docker environment up and running, but without specific input and output elements (OGC Catalog and MQTT Broker), it stops immediately 
for lack of information (it is self consistent, but it is part of more complex architecture and needs observations to elaborate and middleware to provide output).

For this reason, it has been created a dedicated repository that allows to easily performs complete MONICA test, including HLDFAD module on [GitHub](https://github.com/MONICA-Project/DockerGlobalWristbandSimulation). Follows the instructions reported in README.

## Simulators

Complete execution of such application mainly depends on presence of input messsages. Therefore, it is required to activate input messages from the field (real data) 
or through simulators. There are two simulator already available to test solution:
- **Wristband Generator**: Java gradle application that emulates Wristband Gateway (it requires SCRAL and LinkSmart), see  [Wristband Localization Simulator](https://github.com/MONICA-Project/WristbandLocationSimulators/blob/master/README.md)
- **Wristband Complete Generator**: Docker-compose emulator that replace Wristbands, Wristband Gateway, SCRAL and LinkSmart (HLDFAD can connect to it directly) [Wristband Complete Docker Repo](https://github.com/MONICA-Project/WristbandGwMqttEmulator)

## Contributing
Contributions are welcome. 

Please fork, make your changes, and submit a pull request. For major changes, please open an issue first and discuss it with the other authors.

## Affiliation
![MONICA](https://github.com/MONICA-Project/template/raw/master/monica.png)  
This work is supported by the European Commission through the [MONICA H2020 PROJECT](https://www.monica-project.eu) under grant agreement No 732350.
