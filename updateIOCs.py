#!/usr/bin/python3

# Script used for automatically updating AreaDetector IOCs to the new format
# 
# Author: Jakub Wlodek
# Created: 15-May-2019


import os
import read_configure
import fix_ownership


# Version Number
version = "v0.0.2"


# EPICS environment variables that are defined in the unique.cmd file rather than in st.cmd or envPaths
unique_file_elems = ["SUPPORT_DIR", "LOCATION", "PORT", "IOC", 
                        "EPICS_CA_AUTO_ADDR_LIST", "EPICS_CA_ADDR_LIST", 
                        "EPICS_CA_MAX_ARRAY_BYTES", "CAM-ID", "CAM-IP", 
                        "CONFIGURATION_PATH", "UID-NUM", "PREFIX", "CTPREFIX", 
                        "HOSTNAME", "IOCNAME", "QSIZE", "NCHANS", "HIST_SIZE",
                        "XSIZE", "YSIZE", "NELMT", "NDTYPE", "NDFTVL", "CBUFFS", "FRAMERATE"]



# Function that searches provided IOC location for ioc dirs that start with the given prefix
def identify_target_iocs(ioc_location, ioc_prefix, single_ioc):
    target_iocs = []
    for elem in os.listdir(ioc_location):
        if single_ioc == "YES" and os.path.isdir(ioc_location + "/" + elem) and elem == ioc_prefix:
            target_iocs.append(ioc_location + "/" + elem)
        elif os.path.isdir(ioc_location + "/" + elem) and elem.startswith(ioc_prefix):
            target_iocs.append(ioc_location + "/" + elem)
    return target_iocs



# Function that adds SUPPORT_DIR environment variable to unique.cmd
def add_support_env_var(unique_fp, bin_location, bin_flat):
    if bin_flat:
        unique_fp.write('epicsEnvSet("SUPPORT_DIR", "{}")\n'.format(bin_location))
    else:
        unique_fp.write('epicsEnvSet("SUPPORT_DIR", "{}")\n'.format(bin_location + "/support"))



# Function that creates unique.cmd file from existing st.cmd file
def create_unique_from_st(ioc_path, bin_location, bin_flat):
    # Check if st.cmd exists
    if os.path.exists(ioc_path + "/st.cmd"):
        st_file = open(ioc_path+"/st.cmd", "r+")
        unique_file = open(ioc_path + "/unique.cmd", "w+")
        unique_file.write("# This file was autogenerated by reading from existing st.cmd by the updateIOCs.py script\n\n")
        line = st_file.readline()
        while line:
            # if it is an epicsEnvSet call (unique.cmd is all envSet calls)
            if line.startswith("epicsEnvSet"):
                # Check if it is in the list of env vars that should be in unique and make sure it isn't used as a macro
                for elem in unique_file_elems:
                    if elem in line and "$({})".format(elem) not in line:
                        unique_file.write(line)

            line = st_file.readline()

        # add support dir to bottom of unique.cmd
        add_support_env_var(unique_file, bin_location, bin_flat)
        unique_file.close()
        st_file.close()
        return 0
    else:
        print("Error processing {}, no st.cmd file identified".format(ioc_path.split('/')[-1]))
        return -1


# Function that updates the unique file given an old unique file
def update_unique(ioc_path, bin_location, bin_flat):
    if os.path.exists(ioc_path + "/unique.cmd"):
        print("unique.cmd exits, using it as template.")
        found_support_set = False
        os.rename(ioc_path +"/unique.cmd", ioc_path + "/unique_OLD.cmd")
        old_unique_file = open(ioc_path + "/unique_OLD.cmd", "r+")
        new_unique_file = open(ioc_path + "/unique.cmd", "w+")
        line = old_unique_file.readline()
        # Copy exisiting unique.cmd, except SUPPORT_DIR
        while line:
            if "SUPPORT_DIR" in line:
                found_support_set = True
                add_support_env_var(new_unique_file, bin_location, bin_flat)
            else:
                new_unique_file.write(line)
            line = old_unique_file.readline()
        if not found_support_set:
            add_support_env_var(new_unique_file, bin_location, bin_flat)
        old_unique_file.close()
        new_unique_file.close()
        return 0
    else:
        print("unique.cmd does not exist, attempting to build it from st.cmd")
        result = create_unique_from_st(ioc_path, bin_location, bin_flat)
        return result



# Function that updates st.cmd into the new format
def update_st(ioc_path, bin_loction, bin_flat):
    if os.path.exists(ioc_path + "/st.cmd"):
        os.rename(ioc_path + "/st.cmd", ioc_path + "/st_OLD.cmd")
        old_st = open(ioc_path + "/st_OLD.cmd", "r+")
        new_st = open(ioc_path + "/st.cmd", "w+")

        line = old_st.readline()
        line_counter = 0

        while line:
            # At the start of the script
            if line_counter == 0:
                # executable
                if line.startswith("#!"):
                    if bin_flat:
                        new_st.write("#!{}\n".format(bin_loction + "/areaDetector/AD" + line.strip().split("AD")[-1]))
                    else:
                        new_st.write("#!{}\n".format(bin_loction + "/support/areaDetector/AD" + line.strip().split("AD")[-1]))
                else:
                    print("Error: st.cmd file for {} does not have executable line at the top.".format(ioc_path.split('/')[-1]))
                    return -1
                # unique and envPaths loaded next
                new_st.write("< unique.cmd\n")
                new_st.write("< envPaths\n")
                line_counter += 1
            else:
                # For all other lines, check if they are already in the unique file, if not write them in
                in_unique = False
                for elem in unique_file_elems:
                    if elem in line and "$({})".format(elem) not in line and line.startswith('epicsEnvSet'):
                        in_unique = True
                if (not in_unique or line.startswith('#')) and "envPaths" not in line and "unique" not in line:
                    new_st.write(line)
            line = old_st.readline()
        
        new_st.close()
        old_st.close()
        return 0
    else:
        print("Error processing {}, no st.cmd file identified".format(ioc_path.split('/')[-1]))
        return -1



# Function that copies envPaths, checking if the env var for base is correct (Flat or not flat support dir)
def update_envPaths(ioc_path, bin_flat):
    if os.path.exists(ioc_path + "/envPaths"):
        os.rename(ioc_path + "/envPaths", ioc_path + "/envPaths_OLD")
    new_env = open(ioc_path + "/envPaths", "w+")
    old_env = open("Examples/envPaths", "r+")

    line = old_env.readline()
    while line:
        if "EPICS_BASE" in line:
            if bin_flat:
                new_env.write(line)
            else:
                new_env.write('epicsEnvSet("EPICS_BASE", "$(SUPPORT_DIR)/../base")\n')
        else:
            new_env.write(line)
        line = old_env.readline()
        
    old_env.close()
    new_env.close()



# Function called for each IOC to update it to the new format
def process_ioc_update(ioc_path, bin_location, bin_flat_str, ioc_owner):
    print("---------------------")
    print("Updating IOC {}".format(ioc_path.split('/')[-1]))
    bin_flat = True
    if bin_flat_str == "NO":
        bin_flat = False

    print("Updating unique file")
    result = update_unique(ioc_path, bin_location, bin_flat)
    if result != 0:
        return
    print("Updating st.cmd")
    result = update_st(ioc_path, bin_location, bin_flat)
    if result != 0:
        return
    print("Updating envPaths")
    result = update_envPaths(ioc_path, bin_flat)

    print("Fixing IOC ownership and permissions...")
    fix_ownership.change_ownership(ioc_path, ioc_owner)
    fix_ownership.change_permissions(ioc_path)



# Top level function that calls read_configure and then sends the target IOCs
def update_iocs():
    print("-----------------------")
    print("Welcome to updateIOCs version {}".format(version))
    configuration = read_configure.read_config()
    target_iocs = identify_target_iocs(configuration["IOC_LOCATION"], configuration["CAMERA_IOC_PREFIX"], configuration["SINGLE_IOC"])
    if len(target_iocs) == 0:
        print("There were no IOCs that fit the specified configuration settings.")

    for ioc in target_iocs:
        process_ioc_update(ioc, configuration["BINARY_LOCATION"], configuration["BINARIES_FLAT"], configuration["IOC_OWNER"])
    
    print("Done")


update_iocs()
