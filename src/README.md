# ModBus Gateway
ModBus-KNX Gateway script - sending data via simple configuration

The ModBus-KNX Gatway sends data from a ModBus appliance to KNX. It is based on the IP/KNX Gateway device with an installed KNXD library.
All configuration can be done via the CONFIG.yaml file.

## Prerequisites:
- A Python runtime version >= 3.5
- Ensure that you have a IP/KNX gateway installed and KNXD library set up
- Find the instructions here: https://www.meintechblog.de/2018/07/tul-stick-als-knx-ip-gateway-auf-dem-raspberry-pi-einrichten-mit-knxd/

## Configuration instructions:
The configuration file contains the following sections:

- **config section**:
  - general configurations for executing the script
  - define your intended logging level here (*"off"*, *"error"*, *"info"*) with *"info"* providing information about each sent attribute
- **modbusAppliance**:
  - defines all physical appliances that shall be linked. The script supports multiple ModBus devices as source for data sent to the KNX bus.
  - Attributes are linked via the *modbusApplID* attribute id that every attribute needs to define
  - *knxdIP* represents the IP/KNX bus devices IP
- **attributes**:
  - list of attributes transferred between the ModBus appliance and the KNX bus
  - script currently only supports ModBus-READ and KNX-WRITE instructions, defined by *type* value *"modbus2knx"* (TODO)
  - *modbusAddrDec* defines the ModBus address in decimal representation, *modbusFormat* the ModBus attribute data type - currently only "float" is supported (TODO)
  - *modbusAddrDec* allows the automatic calculation of the sum of several ModBus addresses by *"addr1, addr2"* representation
  - *knxAddr* defines the KNX address in *"x/y/z"* notation, *knxFormat* the KNX DPT data type - currently only *"DPT14"* is supported (TODO)
  - *updFreq* defines the frequency the attribute is updated:
    - *"very high"*   - updates once every 10sec, be careful not to flood the bus with too many requests
    - *"high"*        - updates once every minute
    - *"medium"*      - updates once every hour
    - *"low"*         - updates once every 24hours
  
## Daemon setup
The ModBus 2 KNX Gateway can be executed as a daemon service at system startup. To do so, execute the *register_daemon.sh* script file. 
The script file needs to be executed everytime the configuration changes or you update to the latest version.
