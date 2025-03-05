################################################################################
                        READ ME FOR CSMIM CLIENT
################################################################################
Version: 1.6
Author(s): Gunnar Snyder
Editor(s): Enzo Gonzalez, Parker Labine, and Trevor French

########################################
                GENERAL
########################################
DOCUMENTATION:
    * PAHO-MQTT Documentation: https://eclipse.dev/paho/files/paho.mqtt.python/html/client.html
    * Mosquitto Broker Documentation: https://mosquitto.org/man/mosquitto-conf-5.html
DEPENDENCIES:
    * Python Libraries:
        * paho-mqtt
        * cbor2
        * schedule
        * time
    * Broker's CA-root-certificate saved in "certs" file
    * Network connection to the Broker server
NOTE:
    * Ensure client_config settings are correct before running this script.
    * Current message encoding is CBOR.

TROUBLESHOOTING TIPS:
    * Check Mosquitto logs on the broker for any errors.
    * Ensure all dependencies are installed on the client.
    * Both client.py and csmim_functions.py contain DEBUG sections to uncomment for message call-backs.
    * If pip install will not install packages, the "--break_system_packages" tag may be needed.
        * Or client may need to be ran in Python virtual environment.
    * Ensure paho-mqtt is the most current version.
    * Check network connection between client and broker.

########################################
             CLIENT_CONFIG
########################################
Contains the configuration settings for client.py.
All client and topic variables should be changed here.

VARIABLE INFORMATION:
* client_name should be unique from other clients.
* The executable_users list should be updated to included all executable users the client can execute on.
    * Currently used in the MANUAL testing feature.
* user_name should be unique from other clients, the MQTT Broker can not differentiate between clients sharing
    the same username.
* "is_registered" is a global variable used by client.py to indicate if the client has successfully registered with
    the CDS.
        * Default "False", only change to "True" for testing script without a registration service.
* broker_name is the IP address of the server running Mosquitto.
* broker_port is the destination port on the broker. Use port 8883 for TLS. (Unsecure=1883 Secure=8883)
* ca_certs_file is the file location containing the CA root certificate of the Mosquitto broker. (Windows file
    paths must be raw strings, ex: r"file\path")
* The auto_testing variable can be set to 'yes' for AUTOMATIC testing or 'no' for MANUAL testing.
* Auto testing config settings are in seconds. You can decide the time interval for each function to be scheduled,
    if it is being used. Otherwise, the variable will have no effect.
* Allowed client functions are used to specify what CSMIM functions the client has access to.
    * "yes" if the client is ALLOWED to use the specific function.
    * "no" if the client is NOT ALLOWED to use the specific function.
    * "can_send_single" is used for sending a fixed messages.
* Execute/executable config settings are used executable client's status and for fixed execute messages.
* Topic config section allows you to specify specific topics for the client.
    * If using a fixed message, ensure that the correct message variable is used in the single_send and execute functions.

TOPIC FORMAT:
    * GENERAL TOPIC LAYOUT: v1/<CSMIM_action>/<object-path>/<resource-id>
        * <object-path> is the path of the object registered
            * EXAMPLE: crew/lights/units/<row#>/<seat#>
        * <resource-id> is the id of a resource registered to the object, that the object is interacting with
            * EXAMPLE: statusCmd (a resource that commands the light to do an action)
    * READ: "v1/data/<object-path>/<resource-id>" 
        * [SUBSCRIBE] (Using the "data" tag from SEND function ARINC 853 pg. 42, READ can read from any "readable" topic accessible to client)
    * SEND: "v1/data/<object-path>/<resource-id>" 
        * [PUBLISH] (ARINC 853 pg. 42, see TOPIC 0 for example.)
    * EXECUTE: "v1/command/<user-name>/<object-path>/<resource-id>" 
        * [PUBLISH] (ARINC 853 pg. 45, "user-name" is the client to execute command on. 
        * "user-name" should be SUBSCRIBED to that topic.
        * If response is not needed, set "user_property_response" = 0. See TOPIC 1 for example.)
    * RESPOND (to TO EXECUTE): "v1/response/<user-name>/<object-path>/<resource-id>" 
        * [PUBLISH] (ARINC 853 pg. 46, NOT REQUIRED if "user_property_response" = 0, otherwise, "user-name" must be copied from the "user" 
            sending the PUBLISH EXECUTE message and RESPOND must be sent. See TOPIC 2 for example.)
    * REGISTER: "v1/command/<user_name>/core/csmim/registration/claim"
        * reg_payload: edit this variable to reflect the required objects and their resources for this client
            * "path" should be unique to each client
!!WARNING!!:
    * Do not delete the REGISTER or RESPONSE to REGISTER topic! It is required for a client to register its objects with the CDS.
NOTE: 
    * RESPOND action is currently NOT implemented for EXECUTE! 
        * (ALL EXECUTE RESPOND VALUES SHOULD BE SET TO '0'). 
        * It will implement if required.
    * If more topics are needed copy and paste from "EXAMPLE TOPIC" and "EXAMPLE TOPIC FORMAT" below.
        * change "X" to the next number in the sequence
        * EXECUTE topic's user name is linked to a variable, the username is filled out with 'exe_user_x' variable.

########################################
  EXAMPLE TOPIC SECTION (COPY BELOW)
########################################

###### Topic Config Topic X (SEND/READ)######
    ###### Uncomment for EXECUTE Actions ######
#resp_topic_X = "" # For future RESPOND operation. 
#exe_user_X = "" # For EXECUTE. Enter user_name of executable client.
#user_property_response_X = "yes" # Set to "yes" if response is required to EXECUTE message. (!!!! PLEASE USE 'no' FOR NOW !!!!) 
    ###### General Topic Options ######
topic_X = ""
message_X = "" # For fixed messages
qos_X = 0

########################################
  EXAMPLE TOPIC FORMAT (COPY BELOW)
########################################
'''
READ: [ "v1/data/<object-path>/<resource-id>" ]
SEND: [ "v1/data/<object-path>/<resource-id>" ]
EXECUTE: [ f"v1/command/{exe_user_X}/<object-path>/<resource-id>" ]
'''

########################################
             CLIENT_EXECUTE
########################################
Used for executable script. This is for clients that have executable resources and is accessed by client.py and topic_functions.py.
Write script to execute on here.
EXAMPLE:
    * If your client was a light bulb, the script to receive an execute action to turn it on or off would be placed here.

########################################
                CLIENT
########################################
!!!! WARNING !!!!
    * Client variables are changed through client_config.py, altering variables here could break the program!
    * Setting tls_insecure_set() to False will break TLS when using self signed certificates. Please keep setting to True.
This is the main script for the client's operation and should be ran to enable the client.
It contains MQTT functions to connect and disconnect the client to the MQTT Broker.
Both Automatic and Manual testing are supported and can be configured in the client_config.py file.

CURRENT USAGE:
    * For automatic connections:
        * Execute will send an "on" or "off" signal to the light.
        * When the light receives the EXECUTE, it will SEND the status back to the status topic.
        * The crew will READ from the status topic at a specified interval.
    * For MANUAL connections:
        * Can be used to SEND, READ, or EXECUTE single messages on specified topics.

########################################
                CDS
########################################
!!!! WARNING !!!!
    * Cds variables are changed through client_config.py, altering variables here could break the program!
    * Setting tls_insecure_set() to False will break TLS when using self signed certificates. Please keep setting to True.
This is the main script for the cds's operation and should be ran to enable the cds client.
It contains MQTT functions to connect and disconnect the cds to the MQTT Broker.

CURRENT USAGE:
    * Registration Service:
        * Receives and processes registration requests from clients connecting to the broker.
        * Responds with status code of registration status. (See Registration Response Code section)
            * Currently implemented:
                * 200 Success
                * 409 Conflict
    * Resource Directory:
        * Adds registered client as a dictionary to retain registered clients.

########################################
             CSMIM_FUNCTIONS
########################################
This file contains the CSMIM functions:
    * READ: SUBSCRIBE to a readable topic and then unsubscribe.
    * SEND: PUBLISH message to update a value of a readable resource.
    * EXECUTE: PUBLISH an EXECUTE command to and executable client's topic.
    * RESPOND (Not currently used! Will be fully implemented in the future if needed!)
    * Execute SUBSCRIBE: Subscribe to an executable client's EXECUTE topic.

########################################
             TOPIC_FUNCTIONS
########################################
This file contains the functions to manipulate, encode, and decode information used by topics and messages.

################################################
#   Registration Response codes ARINC853 pg.50 
################################################
# 200:OK (Registration was successful)
# 400:Bad Request (The request header or payload contains an error. The server should not retry the same registration request.)
# 403:Forbidden (At least one of the objects could not be registered because the server does not possess “create” permission for its path. 
#   The response payload must contain one offending object path (see Table 6-8). The server should not retry the same registration request; 
#   it may send a request without the offending object.)
# 409:Conflict (At least one of the objects could not be registered because its path has already been registered by another server; 
#   or because its path equals or lies inside the path of a resource that was registered by another server; or
#   because the path of one of its resources equals or contains the path of an object registered by another server. The response payload must contain
#   one offending object path (see Table 6-8). The server may retry the same request after waiting for a certain time. 
#   Persistent 409 errors indicate a configuration problem.)
# 413:Payload Too Large (The number of objects or resources to be registered exceeded the limit defined by the system integrator. 
#   The server should not retry the same registration request.)
# 429:Too Many Requests (The server has sent too many registration requests in a given amount of time. Upon this error code, 
#   the server must reduce its request rate.)
# 503: Service Unavailable (Registration is currently not possible. This may mean that the CSMIM installation only allows registration in dedicated phases, 
#   for example on ground or during maintenance. The server should try registration renewal instead. If that is not possible, the server may retry the same request after
#   waiting for a certain time.)
##################################################################################################################################################
