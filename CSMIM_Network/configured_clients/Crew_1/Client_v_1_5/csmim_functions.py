##################################################################################################################################################
# CSMIM FUNCTIONS: READ, SEND, EXECUTE, RESPOND*, and Execute subscribe
# Version: 1.5
# Author(s): Gunnar Snyder
# Editor(s): Enzo Gonzalez, Parker Labine, and Trevor French
# To be used by the client to execute CSMIM functions.
# * RESPOND is not currently, fully, implemented.
# !!!! WARNING: Do NOT alter any variables in this file, doing so could break the program.
##################################################################################################################################################

import paho.mqtt.client as paho
import paho.mqtt.subscribe as subscribe
from paho.mqtt.properties import Properties
from paho.mqtt.packettypes import PacketTypes
import cbor2

#################### For Debugging ####################
def on_connect(client, obj, flags, reason_code, properties):
    print(f"Flag: {flags} reason_code: {reason_code}")

def decode_cbor_message(client, obj, msg):
    msg.payload = cbor2.loads(msg.payload)
    print(f"Message Recieved: {msg.payload}")

def on_message(client, obj, msg):
    print(f"{msg.topic}: {msg.payload.decode()}")
    ##### Uncomment below to see message properties ######
    #print(f"mqttv5 properties: {msg.properties}")
    
def on_subscribe(client, obj, mid, reason_code_list, properties):
    print(f"Subscribed: {mid} {reason_code_list}")

def on_publish(client, obj, mid, reason_code, properties):
    print(f"on_publish, mid {mid}")
    print(f"on_publish: {reason_code}")

def on_log(client, obj, level, string):
    print(string)

#################### CSMIM FUNCTIONS ####################

###### CSMIM READ function ######
# Retrieve a single resource current value from CSMIM server
# read a resource can be achieved by using SUBSCRIBE and then UNSUBSCRIBE
# if value is only desired once
# encoded CBOR
# see pg. 39 ARINC-853

def csmim_read_single(client, topic): 
    ###### Uncomment for debug ######
    #client.on_message = decode_cbor_message
    #client.on_subscribe = on_subscribe
    #client.on_log = on_log
    ###### Set custom user properties for SUBSCRIBE ######
    properties = Properties(PacketTypes.SUBSCRIBE)
    client.subscribe(topic, qos=0, options=None, properties=properties)
    client.unsubscribe(topic)

###### CSMIM EXECUTE ######
# Triggers action on a single resource's origin server for exec. resources
# includes parameters for the action
# response sent by CSMIM server indicates success or failure of action and may have return value
# send pub message to broker, param must be sent as a dict. in the payload
# encoded CBOR except if it is raw (then payload is a raw sequence of bytes w/out encode should be defined by obj type)
# See pg. 44-46 of ARINC 853

def csmim_execute(client, topic, action, response):
    ###### Uncomment for Debug ######
    #client.on_publish = on_publish
    ###### Set custom user properties for PUBLISH ######
    properties = Properties(PacketTypes.PUBLISH)
    if response == "no":
        properties.UserProperty=("respond","0")
    
    client.publish(topic, action, qos=0, retain=True, properties=properties)

###### CSMIM SEND ######
# Used to update the value of a readable resource
# This is an MQTT PUBLISH method
# must be a representation of the resources value encoded in CBOR
# More on pg 42 of ARINC 853

def csmim_send(client, topic, message):
    ###### Uncomment for Debug ######
    #client.on_publish = on_publish
    ###### Set custom user properties for PUBLISH ######
    properties = Properties(PacketTypes.PUBLISH)

    client.publish(topic, message, qos=0, retain=True, properties=properties)

###### CSMIM SUBSCRIBE TO EXECUTE TOPIC ######
# To SUBSCRIBE to client's executable 

def csmim_exec_subscribe(client, topic):
    ###### Uncomment for Debug ######
    #client.on_subscribe = on_subscribe
    #client.on_message = decode_cbor_message
    ###### Set custom user properties for SUBSCRIBE ######   
    properties = Properties(PacketTypes.SUBSCRIBE)

    client.subscribe(topic, qos=0, options=None, properties=properties)

###### CSMIM PUBLISH RESPONSE TO EXECUTE TOPIC ######
# For future respond topics (Current messages will not require a response!)

def csmim_exec_respond(client, topic, message):
    resp_message = f"Command {message.payload} received" 
    ###### Uncomment for Debug ######
    #client.on_publish = on_publish
    ###### Set custom user properties for PUBLISH ######
    properties = Properties(PacketTypes.PUBLISH)

    client.publish(topic, resp_message, qos=0, retain=True, properties=properties)
