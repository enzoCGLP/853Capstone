###################################################################################################################################################
# Central Data Service (CDS): Connects to MQTT Broker and acts as a registration service as well as provides a resource directory for the CSMIM network
#    All Clients must register with the CDS inorder to gain access to the CSMIM network.
#    All Successful registrations are immutable and stored as a dictionary in the resource directory.
#    Object paths cannot be duplicated.
#    Response codes in use: "200" and "409" all other codes are for future implementation
# Version: 1.6
# Author(s): Gunnar Snyder
# Editor(s): Enzo Gonzalez, Parker Labine, and Trevor French
# !!!! WARNING: Do NOT alter any variables in this file, doing so could break the program. Please see client_config.py for altering variables.
##################################################################################################################################################

######################################
#   Response codes ARINC853 pg.50 
######################################
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

import paho.mqtt.client as paho
import paho.mqtt.subscribe as subscribe
from paho.mqtt.properties import Properties
from paho.mqtt.packettypes import PacketTypes
import cbor2
import client_config
import topic_functions
import csmim_functions

###### GLOBAL: RESOURCE DIRECTORY ######
resource_directory = {} # FORMAT: {<registered_path>: <registration_payload>}
#######################################

###### Decodes received CBOR messages ######
def decode_reg_message(client, obj, msg):
    msg.payload = cbor2.loads(msg.payload)
    proc_reg_topic(client, obj, msg) # !!!! Integrate to: topic_functions
    print(f"Message Received: {msg.payload}")

###### Processes registration message and crafts response topic ######  
def proc_reg_topic(client, obj, msg):
    user_name = topic_functions.get_topic_value(msg.topic, 2)
    response_topic = f"v1/response/{user_name}/core/csmim/registration/claim"
    register_client(client, msg.payload, response_topic)

###### Registers client and adds payload to Resource Directory ######    
def register_client(client, msg, topic):
    objects = msg["objects"]
    first_obj = objects[0]
    path = first_obj["path"]
    # Error 409: Conflict    
    if path in resource_directory:
        error_code = "409"
        get_resp_payload(client, error_code, path, topic)
    # Error 200: Success
    else:
        error_code = "200"
        resource_directory[path] = msg
        get_resp_payload(client, error_code, path, topic)

###### Crafts response payload ######
def get_resp_payload(client, code, path, topic):
    resp_payload = {
    "error": "0", # Human readable error message
    "path": "" # One object path which produced the error code returned by the registration service
    }
    resp_payload["error"] = code
    resp_payload["path"] = path
    encoded_payload = topic_functions.encode_cbor_data(resp_payload)
    csmim_functions.csmim_response(client, topic, encoded_payload)

###### CDS CONNECT TO BROKER ######
cur_client = paho.Client(paho.CallbackAPIVersion.VERSION2, "cds", protocol=5)
cur_client.username_pw_set(username=client_config.user_name, password=client_config.password)
    ###### Set custom user properties for CONNECT ######
properties = Properties(PacketTypes.CONNECT)
    ###### Uncomment for Debug ######  
#cur_client.on_connect = csmim_functions.on_connect
    ###### For TLS ######
cur_client.tls_set(ca_certs = client_config.ca_certs_file)
cur_client.tls_insecure_set(True) # !!!! Setting false will break TLS !!!!
    ###### Connect ######
cur_client.connect(client_config.broker_name, client_config.broker_port, client_config.keep_alive, clean_start=False, properties=properties)

###### SUBSCRIBE TO REGISTRATION TOPIC(S) ######
    ###### Uncomment for Debug ###### 
#cur_client.on_subscribe = csmim_functions.on_subscribe
sub_topic = "v1/command/+/core/csmim/registration/claim" # wildcard "+" is any value at that level. This topic: (any "<user_name>")
csmim_functions.csmim_subscribe(cur_client, sub_topic)

###### REGISTRATION MESSAGE RECEIVED ######
cur_client.on_message = decode_reg_message

###### ENDLESS CONNECTION LOOP ######
cur_client.loop_forever() # Will loop until CDS power is terminated or (CTRL+C)
