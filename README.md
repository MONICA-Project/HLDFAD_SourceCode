# High Level Data Fusion and Anomaly Detection Module (HLDFAD) Quick Start Guide
<!-- Short description of the project. -->

HLDFAD is a back end deputed to provide high level outputs based on acquisition and elaboration of selected on field observables received from MQTT Platform Broker. MQTT input topics are filtered
according to contents reported in Platform GOST Observation Catalog. Output Messages can be provided in MQTT format through internal MQTT Output Broker and\or OGC Service Catalog Output.

The complete bottom-up data chain is the following: 

    - On Field Data Sensors (wristband and cameras)
    - On Field Gateway
    - SCRAL
    - LinkSmart
    - HLDFAD
    - OGC and DSS
Figure below provides a quick overview to give a general understanding about HLDFAD position module.
![General MONICA Architecture](https://github.com/MONICA-Project/HLDFAD_SourceCode/blob/master/WP6BreakdownDiagram.png) 

It is a Docker-composed solution relying on Django Python framework. Docker containers that compose the solution are the following: 

    - mosquitto: Used for MQTT Output Broker (Not necessary if not used such output datastream); 
    - posgresql: Store output messages generated and some trace information;
    - rabbit: Exchange and Queue for Django task system management
    - celery: Task generation and management (application source code run in this container)
    - redis: Cache for temporarily storage of incoming observation input before elaboration (second most important container after celery) 

<!-- A teaser figure may be added here. It is best to keep the figure small (<500KB) and in the same repo -->
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
        <td> Solution component that provides real time observation from the monitored field [e.g. camera observation, localizations' observations)</td>
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
</table>

## HLDFAD Component Configuration

Python dictionary LOCAL_CONFIG reported in file ${REPO_ROOT}/monica/shared/settings/appglobalconf.py (generated after startup configuration) allows to configure behaviour of application. In the following the list of element reported in 
such configuration dictionary: 


    - **LocConfLbls.LABEL_MQTT_OBSERVATION_URL**: [str] MQTT Platform Broker URL; 
    - **LocConfLbls.LABEL_MQTT_OBSERVATION_PORT**: [int] MQTT Platform Broker Port; 
    - **LocConfLbls.LABEL_CATALOG_URL**: [str] Platform GOST Observation Catalog web URL Things list (GOST_URL/v.10/Things)
    - **LocConfLbls.LABEL_CATALOG_USERNAME**: [str] Platform GOST Observation Catalog Username
    - **LocConfLbls.LABEL_CATALOG_PASSWORD**: [str] Platform GOST Observation Catalog Password
    - **LocConfLbls.LABEL_PILOT_NAME**: [str] Selected Pilot (Useful for multi pilot instance)
    - **LocConfLbls.LABEL_SW_RELEASE_VERSION**: SW_VERSION,
    - **LocConfLbls.LABEL_UPDATE_DATASTREAM_LIST**: [str] MQTT URL to retrieve real time new registered datastreams 
    - **LocConfLbls.LABEL_PREFIX_TOPIC**: [str] Set Topic Prefix (GOST Name) useful to complete MQTT Platform Broker URL
    - **LocConfLbls.LABEL_INTERVAL_OBS_VALIDITY_SECS**: [int] Timeout (seconds) to consider single observation "old" and reject it from computation
    - **LocConfLbls.LABEL_ENABLE_EMPTY_CROWD_HEATMAP**: [bool] Flag to enable generation of empty (zeros matrix) crowd heatmap generated in case of no input received (for wristband input only) 
    - **LocConfLbls.LABEL_BYPASS_BEGINNING_CATALOG_ACQUISITION**: [bool] Flag to bypass Platform GOST Observation Catalog (it can be used in simulated mode, see below)
    - **LocConfLbls.LABEL_BYPASS_MQTTINPUTMESSAGEACQUISITION**: [bool] Flag to bypass MQTT Platform Broker (for debugging only)
    - **LocConfLbls.LABEL_ENABLE_UNIT_TESTS**: [bool] Flag request unit tests (for debugging only)
    - **LocConfLbls.LABEL_ENABLE_RANDOM_QUEUEDETECTIONALERT**: [bool] Flag to enable random queue detection alert (for debugging only)
    - **LocConfLbls.LABEL_ABORT_EXECUTION_AFTERUNITTESTS**: [bool] Flag to abort application execution after unit tests (for debugging only)
    - **LocConfLbls.LABEL_ENABLE_RANDOM_DENSITYMATRIX**: [bool] Flag to generate random density matrix (for simulation only)
    - **LocConfLbls.LABEL_MQTT_CLIENT_PAHO_NAME_OBSERVABLES**: [str] MQTT Presentation client ID for MQTT Platform Broker
    - **LocConfLbls.LABEL_MQTT_CLIENT_PAHO_NAME_DATASTREAMUPDATE**: [str] MQTT Presentation client ID for MQTT Datastream Broker
    - **LocConfLbls.LABEL_WP6_CATALOG_CONNECTIONURL**: [str] OGC Service Catalog Output URL Connection
    - **LocConfLbls.LABEL_WP6_CATALOG_CONNECTIONPORT**: [int] OGC Service Catalog Output Port Connection
    - **LocConfLbls.LABEL_WP6_CATALOG_POSTSERVICERETRIEVEOUTPUTINFO**: [str] OGC Service Catalog Output Service Name to recall to retrieve message output information
    - **LocConfLbls.LABEL_OBSERVATION_DEBUG_INTERVALNUMBERNOTIFICATION**: [int] Debug Setting (for tracing only) interval seconds of notification in trace of received observation
    - **LocConfLbls.LABEL_WP6_SERVICECATALOG_DICTIONARYSELECTED**: [Dict[OutputMessageType, Dict[str, Any]] Dictionary to be configured for OGC Service Catalog Output to associate output type and JSON to send as input for request OGC Output format 
    - **LocConfLbls.LABEL_OUTPUT_MESSAGELIST_SELECTED**: [List[OutputMessageType]] List of selected output messages
    - **LocConfLbls.LABEL_OUTPUT_MQTT_LISTTYPES**: [List[MQTTPayloadConversion]] List of output type: Simple MQTT Output Broker and\or OGC Service Catalog Output
    
Furthermore, there is additional configuration elements. For instance Python dictionary SCHEDULER_SETTINGS (reported also in ${REPO_ROOT}/monica/shared/settings/appglobalconf.py) that allows to 
set timing tasks with:  

    -   "TASK_ELABORATION": [int] Period (seconds) to activate elaboration
    -   "TASK_ALIVEAPP": [int] Period (seconds) for alive tasks to communicate that application is up and running
    
As aforementioned, it is possible to bypass Platform GOST Observation Catalog with auxiliary simulator that provides input data with well-known associated topics (see LocConfLbls.LABEL_BYPASS_BEGINNING_CATALOG_ACQUISITION).
In order to obtain such result, it is necessary to set LocConfLbls.LABEL_BYPASS_BEGINNING_CATALOG_ACQUISITION to True, fills out DICTIONARY_OBSERVABLE_TOPICS reported in ${REPO_ROOT}/monica/shared/settings/default_datastreams.py 
and activate simulator (explained in the following). 

DICTIONARY_OBSERVABLE_TOPICS is Python dictionary [Dict[int, List[str]]] that specifies for each datastream ID:
    - MQTT Broker Topic [str]
    - Datastream ID [str]
    
Such configuration can be exploited also when the datastreams and MQTT topics are well known from official Platform GOST Observation Catalog. It has to be remarked that, in case of simulation, 
topics must match with reported ones. 

## Dockers Environment Variables

File ${REPO_ROOT}/.env (symbolic link generated after startup setup) includes very specific Docker container configurations that shall not be changed if not necessary.


### Custom Types and additional definition

LOCAL_CONFIG dictionary includes custom types that are documented in the following list:  

    - **OutputMessageType**: HLDFAD Output Message Type, defined in ${REPO_ROOT}/monica/general_types/modelsenums.py. Original version includes the following values:
        - *OutputMessageType.OUTPUT_MESSAGE_TYPE_CROWDHEATMAPOUTPUT*: Calculation of Crowd Heatmap based on Wristband Locations; 
        - *OutputMessageType.OUTPUT_MESSAGE_TYPE_QUEUEDETECTIONALERT*: Estimation of Queue Detection Alert based on Density Local Map Security Fusion Node messages
    - **MQTTPayloadConversion**: HLDFAD Selected Output Stream, defined in  ${REPO_ROOT}/monica/general_types/general_enums.py. Original version includes the following values:
        - *MQTTPayloadConversion.TYPE_CONVERSION_STANDARDDICTIONARY*:  MQTT Output Broker
        - *MQTTPayloadConversion.TYPE_CONVERSION_OGCDICTIONARY*: OGC Service Catalog Output
    - **Dictionary Configuration OGC Service Catalog Output (see LocConfLbls.LABEL_WP6_SERVICECATALOG_DICTIONARYSELECTED)**:  Dictionary to present specific output to OGC Service Catalog Output 
    with the following fields:
        - "externalId": [str] Name for presentation of output;  
        - "metadata": [str] Name for Datastream;  
        - "sensorType": [str] Sensor Type;  
        - "unitOfMeasurement": [str] Unit of measurement;  
        - "fixedLatitude": [float] Fixed Latitude <Optional, default=0>; 
        - "fixedLongitude": [float] Fixed Longitude <Optional, default=0>

## Getting Started
<!-- Instruction to make the project up and running. -->
Ensuring that Docker Engine is correctly installed. Then, after clone current git, from bash shell go to ${REPO_ROOT}/tools folder and launch command:
```bash
${REPO_ROOT}/tools:$ sh startup_configure_elements_prod.sh
```
Such command initializes machine folders for docker containers with correct permissions in order to allow effective lauch of the application and create file ${REPO_ROOT}/monica/shared/settings/appglobalconf.py. 

**NOTE**: It is possible to copy contents of file  ${REPO_ROOT}/monica/shared/settings/dev.py in ${REPO_ROOT}/monica/shared/settings/appglobalconf.py for debugging purposes.

### Simulators

Complete execution of such application mainly depends on presence of input messsages. Therefore, it is required to activate input messages from the field (real data) 
or through simulators. There are two simulator already available to test solution:  

    - **Wristband Generator**: Java gradle application that emulates Wristband Gateway (it requires SCRAL and LinkSmart)
    - **Wristband Complete Generator**: Docker-compose emulator that replace Wristbands, Wristband Gateway, SCRAL and LinkSmart (HLDFAD can connect to it directly)

## Deployment
<!-- Deployment/Installation instructions. If this is software library, change this section to "Usage" and give usage examples -->

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
Work in progress.

### Build

It is possible to create docker container launching command:

```bash
${REPO_ROOT}:$ docker-compose build
```

## Simulators

Complete execution of such application mainly depends on presence of input messsages. Therefore, it is required to activate input messages from the field (real data) 
or through simulators. There are two simulator already available to test solution:  

    - **Wristband Generator**: Java gradle application that emulates Wristband Gateway (it requires SCRAL and LinkSmart), see  [Wristband Localization Simulator](https://github.com/MONICA-Project/WristbandLocationSimulators/blob/master/README.md)
    - **Wristband Complete Generator**: Docker-compose emulator that replace Wristbands, Wristband Gateway, SCRAL and LinkSmart (HLDFAD can connect to it directly)

## Contributing
Contributions are welcome. 

Please fork, make your changes, and submit a pull request. For major changes, please open an issue first and discuss it with the other authors.

## Affiliation
![MONICA](https://github.com/MONICA-Project/template/raw/master/monica.png)  
This work is supported by the European Commission through the [MONICA H2020 PROJECT](https://www.monica-project.eu) under grant agreement No 732350.

> # Notes
>
> * The above templace is adapted from [[1](https://github.com/cpswarm/template), [2](https://www.makeareadme.com), [3](https://gist.github.com/PurpleBooth/109311bb0361f32d87a2), [4](https://github.com/dbader/readme-template)].
> * Versioning: Use [SemVer](http://semver.org/) and tag the repository with full version string. E.g. `v1.0.0`
> * License: Provide a LICENSE file at the top level of the source tree. You can use Github to [add a license](https://help.github.com/en/articles/adding-a-license-to-a-repository). This template repository has an [Apache 2.0](LICENSE) file.
>
> *Remove this section from the actual readme.*
