# updateIOC

This module is a collection of scripts designed to update exsisting IOCs to use the new binary distribution format.

### Installation

`updateIOC` requires python3, install it with
```
sudo apt install python3
```
You may clone this repository with:
```
git clone https://github.com/epicsNSLS2-deploy/updateIOC
```

### Usage

To use updateIOC, there are several configuration options, which are edited in the `CONFIGURATION` file:

Option  |   Description
-------|----------------
IOC_LOCATION | Dir containting all iocs (usually `/epics/iocs`)
CAMERA_IOC_PREFIX | Prefix for directories contiaining AreaDetector IOCs (`cam` or `det`)
BINARY_LOCATION | Path to precompiled binaries
BINARIES_FLAT | `YES` or `NO`, if base is in same dir as synApps modules set to `YES` otherwise `NO`
IOC_OWNER | Set this to the desired owner of all IOC files (ex. `softioc`)
SINGLE_IOC | If set to yes, the script will attempt to match an IOC directly with prefix, and only convert that IOC

In order to use the module, set up the `CONFIGURATION` file with the correct parameters. In order to target an individual IOC rather than the entire directory, set the `SINGLE_IOC` option to `YES`.

To run the script, navigate to the `updateIOC` directory that contains it, and type either
```
./updateIOCs.py
```
or
```
python3 updateIOCs.py
```
Note that sudo may be required in order to run the script if the `IOC_LOCATION` is set to a dir that is not owned by the user running the script.

You should now have reorganized IOCs!

### Usage notes

When using the script with iocs created with areaDetector 1-9-1, there is an issue with identifying the correct binary location in st.cmd. The reason for this is that the script identifies the camera type by reading the existing st.cmd file and finding the name of the driver, ex: `ADProsilica`. In areaDetector 1-9-1, all drivers were built into one `bin/` directory, and thus the driver cannot be identified. 
