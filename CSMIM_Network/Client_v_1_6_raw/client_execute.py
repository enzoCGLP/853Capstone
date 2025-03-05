##################################################################################################################################################
# EXECUTABLE CODE: All EXECUTE messages are directed to this file. Place your executable code here!
# Version: 1.6
# Author(s): Gunnar Snyder
# Editor(s): Enzo Gonzalez, Parker Labine, and Trevor French
# USED FOR EXECUTE COMMANDS ON THE CLIENT
##################################################################################################################################################
import client_config # testing changing variable

# To test light status changes from execute message. Currently prints the light status changes.
def light_one(command):
    client_config.light_status = command
    client_config.message_0 = client_config.light_status
    print(f"LIGHT_CHANGED: {client_config.light_status}")





