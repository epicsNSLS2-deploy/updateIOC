#!/usr/bin/python3

import os
import read_configure

version = "v0.0.1"

unique_file_elems = ["SUPPORT_DIR", "LOCATION", "PORT", "IOC", 
                        "EPICS_CA_AUTO_ADDR_LIST", "EPICS_CA_ADDR_LIST", 
                        "EIPCS_CA_MAX_ARRAY_BYTES", "CAM-ID", "CAM-IP", 
                        "CONFIGURATION_PATH", "UID-NUM", "PREFIX", "CTPREFIX", 
                        "HOSTNAME", "IOCNAME", "QSIZE", "NCHANS", "HIST_SIZE",
                        "XSIZE", "YSIZE", "NELMT", "NDTYPE", "NDFTVL", "CBUFFS", "FRAMERATE"]

def identify_target_iocs(ioc_location, ioc_prefix):
    target_iocs = []
    for elem in os.listdir(ioc_location):
        if os.path.isdir(ioc_location + elem) and elem.startswith(ioc_prefix):
            target_iocs.append(ioc_location + elem)
    return target_iocs


def add_support_env_var(unique_fp, bin_location, bin_flat):
    if bin_flat:
        unique_fp.write('epicEnvSet("SUPPORT_DIR", "{}"\n'.format(bin_location))
    else:
        unique_fp.write('epicEnvSet("SUPPORT_DIR", "{}"\n'.format(bin_location + "/support"))


def create_unique_from_st(ioc_path, bin_location, bin_flat):
    if os.path.exists(ioc_path + "/st.cmd")
        st_file = open(ioc_path+"/st.cmd", "r+")
        unique_file = open(ioc_path + "/unique.cmd", "w+")

        line = st_file.readline()
        while line:
            if line.startswith("epicsEnvSet"):
                for elem in unique_file_elems:
                    if elem in line and "$({})".format(elem) not in line:
                        unique_file.write(line)

            line = st_file.readline()

        add_support_env_var(unique_file, bin_location, bin_flat)
        unique_file.close()
        st_file.close()
        return 0
    else:
        print("Error processing {}, no st.cmd file identified".format(ioc_path.split('/')[-1]))
        return -1


def update_unique(ioc_path, bin_location, bin_flat):
    if os.path.exists(ioc_path + "/unique.cmd"):
        found_support_set = False
        os.rename(ioc_path +"/unique.cmd", ioc_path + "/unique_OLD.cmd")
        old_unique_file = open(ioc_path + "/unique_OLD.cmd", "r+")
        new_unique_file = open(ioc_path + "/unique.cmd", "w+")
        line = unique_file.readline()
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
        result = create_unique_from_st(ioc_path, bin_location, bin_flat)
        return result


def update_st(ioc_path, bin_loction, bin_flat):
    if os.path.exists(ioc_path + "/st.cmd"):
        os.rename(ioc_path + "/st.cmd", ioc_path + "/st_OLD.cmd")
        old_st = open(ioc_path + "/st_OLD.cmd", "r+")
        new_st = open(ioc_path + "/st.cmd", "w+")

        line = old_st.readline()
        line_counter = 0

        while line:
            if line_counter == 0:
                if bin_flat:
                    new_st.write("#!{} st.cmd\n".format(bin_loction + "/areaDetector/" + line.strip()[line.index("AD") + len(line.strip()):]))
                else:
                    new_st.write("#!{} st.cmd\n".format(bin_loction + "/support/areaDetector/" + line.strip()[line.index("AD") + len(line.strip()):]))


def process_ioc_update(ioc_path, bin_location, bin_flat_str):
    print("---------------------")
    print("Updating IOC {}\n".format(ioc_path.split('/')[-1]))
    bin_flat = True
    if bin_flat_str == "NO":
        bin_flat = False

    print("Updating unique file")
    update_unique(ioc_path, bin_location, bin_flat)
    print("Updating st.cmd")
    update_st(ioc_path, bin_location, bin_flat)
    print("Updating envPaths")
    update_envPaths(bin_flat)
    



def update_iocs():
    print("Welcome to updateIOCs version {}\n".format(version))
    configuration = read_configure.read_config()
    target_iocs = identify_target_iocs(configuration["IOC_LOCATION"], configuration["CAMERA_IOC_PREFIX"])
    if len(target_iocs) == 0:
        print("There were no IOCs that fit the specified configuration settings.\n")

    for ioc in target_iocs:
        process_ioc_update(ioc, configuration["BINARY_LOCATION"], configuration["BINARIES_FLAT"])
    
    print("Done\n")


update_iocs()