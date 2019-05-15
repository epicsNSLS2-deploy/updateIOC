#!/usr/bin/python3

import os
import read_configure


def identify_target_iocs(ioc_location, ioc_prefix):
    target_iocs = []
    for elem in os.listdir(ioc_location):
        if os.path.isdir(ioc_location + elem) and elem.startswith(ioc_prefix):
            target_iocs.append(ioc_location + elem)
    return target_iocs




read_configure.read_config()