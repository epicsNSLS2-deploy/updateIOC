#
# Function that reads the configure file for updating IOCs
#
# Author: Jakub Wlodek
#

import os

def read_config():
    result = {}
    config_file = open("CONFIGURE", "r+")

    line = config_file.readline()
    while line:
        line = line.strip()
        if not line.startswith("#") and len(line) > 0:
            pair = line.split('=')
            result[pair[0]] = pair[1]
        
        line = config_file.readline()
    
    config_file.close()
    print("CONFIGURE file read with the following values:")
    print(result)
    return result