# Python file that contians functions for fixing ownership and permissions for updated IOCs
#
# Author: Jakub Wlodek

import os
import pwd
import grp

def change_ownership(ioc_location, ioc_owner):
    uid = pwd.getpwnam(ioc_owner).pw_uid
    gid = grp.getgrpnam(ioc_owner).gr_gid
    if os.path.exists(ioc_location + "/st.cmd"):
        os.chown(ioc_location + "/st.cmd", uid, gid)
    if os.path.exists(ioc_location + "/unique.cmd"):
        os.chown(ioc_location + "/unique.cmd", uid, gid)
    if os.path.exists(ioc_location + "/envPaths"):
        os.chown(ioc_location + "/envPaths", uid, gid)

def change_permissions(ioc_location):
    if os.path.exists(ioc_location + "/st.cmd"):
        os.chmod(ioc_location + "/st.cmd", 755)