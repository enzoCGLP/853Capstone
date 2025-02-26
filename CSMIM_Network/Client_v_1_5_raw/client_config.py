##################################################################################################################################################
# CLIENT CONFIGURATION FILE: Contains variables used by client.py and topic_functions.py.
# !!!! WARNING: Please alter variables in this file only!
# Version: 1.5
# Author(s): Gunnar Snyder
# Editor(s): Enzo Gonzalez, Parker Labine, and Trevor French
##################################################################################################################################################

#################### Client Info ####################
client_name = "client_sub"
executable_users = ["user", "light_1"]
    ###### User/Pass ######
user_name = "user"
password = "password"
    ###### Broker Config ######
broker_name = "broker" # IP or host name of broker server
broker_port = 1883 # Destination port (Unsecure=1883 Secure=8883)
keep_alive = 60 # Connection keep alive value

#################### CA Cert Info ####################
ca_certs_file = r"C:\Users\snyde\OneDrive\Desktop\SP25\Capstone\MQTT\v5\certs\ca-root-cert.crt"  # File location of CA cert

#################### AUTO or MANUAL TESTING CONFIG ####################
auto_testing = "yes" # Set: 'yes' for AUTOMATIC or 'no' for MANUAL testing

#################### AUTO TESTING CONFIG ####################
read_time = 5
send_single_time = 5 
execute_time_1 = 5
execute_time_2 = 11
#################### ALLOWED CLIENT FUNCTIONS ####################
is_executable = "yes" # "no" if client is not executable
can_execute = "no" # "no" if client can not execute on another client
can_read = "no" # "no" if client can not read from a topic
can_send = "yes" # "no" if client can not send to a topic
can_send_single = "no" # "no" if client can not send a fixed message to to topic
#################### EXECUTE/EXECUTABLE CONFIG SECTION ####################
light_status = "off"
exec_message_0 = "off"
exec_message_1 = "on"
#################### TOPIC CONFIG SECTION ####################
# If more topics are needed copy and paste from "EXAMPLE TOPIC" below and change number to next number in sequence
# Copy needed topic from topic format examples and fill in the required sections.
# Note: EXECUTE topic's user name is linked to a variable, the username is filled out with 'exe_user_x' variable.
# Topic format is as follows:
# READ: ["v1/data/<object-path>/<resource-id>"] [SUBSCRIBE] (Using the "data" tag from SEND function ARINC 853 pg. 42, READ can read from any "readable" topic accessible to client)
# SEND: ["v1/data/<object-path>/<resource-id>"] [PUBLISH] (ARINC 853 pg. 42, see TOPIC 0 for example.)
# EXECUTE: [f"v1/command/{exe_user_X}/<object-path>/<resource-id>"] [PUBLISH] (ARINC 853 pg. 45, "user-name" is the client to execute command on. "user-name" should be SUBSCRIBED to that topic.
#       If response is not needed, set "user_property_response" = 0. See TOPIC 1 for example.)
# RESPOND (to TO EXECUTE): ["v1/response/<user-name>/<object-path>/<resource-id>"] (ARINC 853 pg. 46, NOT REQUIRED if "user_property_response" = 0, 
#       otherwise, "user-name" must be copied from the "user" sending the PUBLISH EXECUTE message and RESPOND must be sent. See TOPIC 2 for example.)
#       !!!! RESPOND action is currently disabled (ALL EXECUTE RESPOND VALUES SHOULD BE SET TO '0'). I will implement if we need it in the future.
#
###### EXAMPLE TOPIC SECTION (COPY BELOW) ######
'''
###### Topic Config Topic X (SEND/READ)######
    ###### Uncomment for EXECUTE Actions ######
#resp_topic_X = "" # For future RESPOND operation. 
#exe_user_X = "" # For EXECUTE. Enter user_name of executable client.
#user_property_response_X = "no" # Set to "yes" if response is required to EXECUTE message. (!!!! PLEASE USE 'no' FOR NOW !!!!) 
    ###### General Topic Options ######
topic_X = ""
message_X = "" # For fixed messages
qos_X = 0
'''
###### EXAMPLE TOPIC FORMAT (COPY BELOW) ######
'''
READ: [ "v1/data/<object-path>/<resource-id>" ]
SEND: [ "v1/data/<object-path>/<resource-id>" ]
EXECUTE: [ f"v1/command/{exe_user_X}/<object-path>/<resource-id>" ]
'''

####################################################
# TOPIC CONFIG BELOW:
####################################################

###### Topic Config Topic 0 (SEND/READ)######
    ###### Uncomment for EXECUTE Actions ######
#resp_topic_0 = "" # For future RESPOND operation.
#exe_user_0 = "" # For EXECUTE. Enter user_name of executable client.
#user_property_response_0 = "no" # Set to "yes" if response is required to EXECUTE message. (!!!! PLEASE USE 'no' FOR NOW !!!!) 
    ###### General Topic Options ######

topic_0 = "v1/data/crew/lights/unit/1/status"
message_0 = "" # For fixed messages
qos_0 = 0

###### Topic Config Topic 1 (EXECUTE)######
    ###### Uncomment for EXECUTE Actions ######
#resp_topic_1 = "" # For future RESPOND operation.
exe_user_1 = "user" # For EXECUTE. Enter user_name of executable client.
user_property_response_1 = "no" # Set to "yes" if response is required to EXECUTE message. (!!!! PLEASE USE 'no' FOR NOW !!!!)    
    ###### General Topic Options ######
topic_1 = f"v1/command/{exe_user_1}/crew/lights/unit/1"
message_1 = "" # For fixed messages
qos_1 = 0

###### Topic Config Topic 2 (RESPONSE Example FOR FUTURE USE)######
    ###### Uncomment for EXECUTE/RECEIVE Actions. ######
#resp_topic_2 = "" # # For future RESPOND operation.
#exe_user_2 = "" # For EXECUTE. Enter user_name of executable client.
#user_property_response_2 = "no" # Set to "yes" if response is required to EXECUTE message. (!!!! PLEASE USE 'no' FOR NOW !!!!)  
    ###### General Topic Options ######
topic_2 = f"v1/response/user_name/crew/lights/unit/1"
message_2="" # For fixed messages
qos_2 = 0

###### Topic Config Topic 3 (FUNCTION) ######
    ###### Uncomment for EXECUTE Actions. ######
#resp_topic_3 = "" # # For future RESPOND operation.
#exe_user_3 = "" #  For EXECUTE. Enter user_name of executable client.
#user_property_response_3 = "no" # Set to "yes" if response is required to EXECUTE message. (!!!! PLEASE USE 'no' FOR NOW !!!!)     
    ###### General Topic Options ######
topic_3 = ""
message_3 = "" # For fixed messages
qos_3 = 0
