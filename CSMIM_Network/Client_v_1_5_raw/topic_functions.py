##################################################################################################################################################
# TOPIC FUNCTIONS: read, change, and craft MQTT/CSMIM topics and messages.
# Version: 1.5
# Author(s): Gunnar Snyder
# Editor(s): Enzo Gonzalez, Parker Labine, and Trevor French
# !!!! WARNING: Do NOT alter any variables in this file, doing so could break the program. Please see client_config.py for altering variables.
##################################################################################################################################################

import client_config
import client_execute
import csmim_functions
#import paho.mqtt.client as paho
#from paho.mqtt.properties import Properties
#from paho.mqtt.packettypes import PacketTypes
import time
import cbor2

###### Decodes received CBOR messages ######
def decode_cbor_message(client, obj, msg):
    print()
    msg.payload = cbor2.loads(msg.payload)
    #print(f"Message Received: {msg.payload}")
    process_topic(client, obj, msg)

###### Encodes outgoing CBOR messages ######
def encode_cbor_data(data):
    encoded_message = cbor2.dumps(data)
    return encoded_message

###### Sorts topics for received READ and EXECUTE messages ######
def process_topic(client, obj, msg):
    topic = get_topic_value(msg.topic, 1)
    if topic == "command":
        client_execute.light_one(msg.payload)
        if client_config.can_send == "yes":
            csmim_functions.csmim_send(client, client_config.topic_0, encode_cbor_data(msg.payload))
    elif topic == "data":
        print(f"STATUS RECEIVED: {msg.payload}")
        time.sleep(1)
    else:
        print("Incorrect function in topic!\n")

###### Build topic and select client to send executable ######
def process_execute_topic(user_list, user, topic): 
    if user in user_list:
         index = user_list.index(user)
         topic = edit_topic_value(topic, 2, client_config.executable_users[index])
         return topic
    else:
         return "Error User Not Found!"
    
def get_topic_value(topic, index):
    split_list =[]
    for x in topic.split('/'):
        split_list.append(x)
    return split_list[index]

def edit_topic_value(topic, index, new_value):
    split_list =[]
    for x in topic.split('/'):
        split_list.append(x)
    split_list.pop(2)
    split_list.insert(index, new_value)
    new_topic = "/".join(split_list)
    return new_topic
