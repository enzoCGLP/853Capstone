###################################################################################################################################################
# CLIENT: Connects to MQTT broker, calls and CSMIM functions, and disconnects client from MQTT broker.
# Automatic and Manual testing are available (See README and client_config.py)
# Version: 1.5
# Author(s): Gunnar Snyder
# Editor(s): Enzo Gonzalez, Parker Labine, and Trevor French
# !!!! WARNING: Do NOT alter any variables in this file, doing so could break the program. Please see client_config.py for altering variables.
##################################################################################################################################################
import client_config
import csmim_functions
import client_execute
import topic_functions
import paho.mqtt.client as paho
from paho.mqtt.properties import Properties
from paho.mqtt.packettypes import PacketTypes
import schedule
import time

#################### Initialize and connect to client ####################
cur_client = paho.Client(paho.CallbackAPIVersion.VERSION2, client_config.client_name, protocol=5)
cur_client.username_pw_set(username=client_config.user_name, password=client_config.password)
    ###### Set custom user properties for CONNECT ######
properties = Properties(PacketTypes.CONNECT)
###### Uncomment for Debug ######  
#cur_client.on_connect = on_connect
    ###### For TLS ######
cur_client.tls_set(ca_certs = client_config.ca_certs_file)
cur_client.tls_insecure_set(True) # !!!! Setting false will break TLS !!!!
    ###### Connect and loop ######
cur_client.connect(client_config.broker_name, client_config.broker_port, client_config.keep_alive, clean_start=False, properties=properties)
cur_client.loop_start()

###### Check if client is executable and subscribes to its executable topic ######
if client_config.is_executable.lower() == "yes":
    print("WAITING FOR SAVED EXECUTE COMMAND...")
    csmim_functions.csmim_exec_subscribe(cur_client, client_config.topic_1)
    
###### Catch and decode received messages ######
cur_client.on_message = topic_functions.decode_cbor_message
#################### AUTOMATIC TRAFFIC ####################
if client_config.auto_testing == 'yes':

    ###### SET READ SCHEDULE ######
    if client_config.can_read == "yes":
        schedule.every(client_config.read_time).seconds.do(csmim_functions.csmim_read_single, cur_client, client_config.topic_0)

    ###### SET SEND SCHEDULE ######
    if client_config.can_send_single == "yes":
        send_data = client_execute.light_value
        encode_send = topic_functions.encode_cbor_data(send_data)
        schedule.every(client_config.send_single_time).seconds.do(csmim_functions.csmim_send, cur_client, client_config.topic_0, encode_send)
        
    ###### SET EXECUTE SCHEDULE ######
    if client_config.can_execute == "yes": 
        topic = topic_functions.process_execute_topic(client_config.executable_users, client_config.exe_user_1, client_config.topic_1)
        exe_data_1 = topic_functions.encode_cbor_data(client_config.exec_message_0)
        exe_data_2 = topic_functions.encode_cbor_data(client_config.exec_message_1)
        schedule.every(client_config.execute_time_1).seconds.do(csmim_functions.csmim_execute, cur_client, topic, exe_data_1, client_config.user_property_response_1)
        schedule.every(client_config.execute_time_2).seconds.do(csmim_functions.csmim_execute, cur_client, topic, exe_data_2, client_config.user_property_response_1)

    ###### Loop scheduled processes ######
    while True:
        schedule.run_pending()
        time.sleep(1)

#################### MANUAL TRAFFIC ####################  
else:
    function_option = input("Would you like to READ 'r', SEND 's', EXECUTE 'e' or QUIT 'q': ")
    function_option = function_option.lower()

    while function_option != "q":
        if function_option == "r":
            csmim_functions.csmim_read_single(cur_client, client_config.topic_0)
        elif function_option == "s":
            send_data = input("Enter status of light 1: ")
            encoded_data = topic_functions.encode_cbor_data(send_data)
            csmim_functions.csmim_send(cur_client, client_config.topic_0, encoded_data)
        elif function_option == 'e':
            count = 0
            for x in client_config.executable_users:
                print(f"{count}: {x} \n")
                count = (count+1)
            selected_user = input("Select number of executable user: ")
            selected_user = int(selected_user)
            topic = topic_functions.edit_topic_value(client_config.topic_1, 2, client_config.executable_users[selected_user])
            print(topic)
            action = input("Enter action for light, 'on' or 'off': ")
            encoded_action = topic_functions.encode_cbor_data(action)
            csmim_functions.csmim_execute(cur_client, topic, encoded_action)

        else:
            print("Wrong entry, try again! \n")
        function_option = input("Would you like to READ 'r', SEND 's', EXECUTE 'e' or QUIT 'q': ")
    
cur_client.disconnect()
