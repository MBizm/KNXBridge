# KNXBridge
Declarative EIB/KNX client for ease of bridging between KNX and other home automation specifications. Declaration is done via simple YAML file. The KNX Bridge client running as a daemon, assuring data transfer (r/w) and data transformation without the need for one line of code.

## Prerequisites:
 - Running [KNXD daemon](https://github.com/smurfix/knxd) for communication with the KNX bus
 - The [EIB/KNX Client](https://github.com/MBizm/KNXPClient) as the Python-interface with KNXD
 - The [Python3-ified version of pKNyX](https://github.com/MBizm/KNXPDPT) for transformation of KNX Datapoint Types (DPT) 

## Installation

    git clone https://github.com/MBizm/KNXBridge
    cd src
    ./register_daemon.sh

KNX Bridge will be executed as a daemon service. Configuration will be taken from *~/.knx/bridge/CONFIG.yaml*.
The daemon needs to be restarted everytime the configuration changes via *sudo systemctl restart KNXBridgeDaemon*.

# Configuration
The configuration file declaring the client and their respective attributes to be exchanged is located in *~/.knx/bridge/CONFIG.yaml*. Folder and initial configuration template will be created by installation script.

## Structure

 1. **Section - general configuration for KNXBridge service:**
		 General KNXBridge service related configuration like logging level. all configuration values start with *config**.
 2. **Section - appliances/gateway definitions:**
		 List of defined appliance/gateways. Multiple instances of the same appliance/gateway type can be defined and are identified by their unique ID. An appliance is a physical device in the real world either being directly available via a TCP-based network(e.g. ModBus via TCP) or a gateway acting an intermediate translator for the actual devices (e.g. ZigBee gateway).
 3. **Section - physical device and attributes definition:**
		 List of physical devices and attributes which are supposed to be monitored or updated based on either changes in the physical device or the KNX bus.

For reference of all attributes and template of the whole configuration file refer to [template configuration file](https://github.com/MBizm/KNXBridge/blob/main/src/CONFIG.yaml).

## KNXBridge configuration

    configSet:  Optional Title for your configuration file
    configNote: >
      Optional detailed description and remarks for your configuration file
    configVersion:  0.3 		# format version of config file
    configVerbose:  "info"	# log level - "off", "error", "warning", "change", "info" 

## Supported appliances/gateways
| Specification | Querying procedure |  Remark |
|--|--|--|
| ModBus | Polling with frequency defined via *updFreq* attribute | -- |
|ZigBee|Polling via the [deConz ZigBee Gateway Rest API](https://www.dresden-elektronik.de/funk/software/deconz.html) with frequency defined via *updFreq* attribute | -- |
| MQTT | Listening to defined MQTT broker instance with immediate update to the KNX bus. | **Watch out: high frequency update of MQTT clients might flood your KNX bus!!**|
|KNX | KNXDaemon can register as a listener for a KNX address and route the value to another target address. | -- |

### KNXD appliance definition (obligatory):

    knxdAppliance:
    knxdIP:     <ENTER YOUR IP HERE>
  
### ModBus appliance definition (optional):

    modbusAppliance:
      - modbusApplID: 0
        modbusName:   "Solar Inverter"
        modbusIP:     <ENTER YOUR IP HERE>
        modbusPort:   "1502"

### ZigBee gateway definition (optional):

The ZigBee gateway acts as a multiplexer for multiple physical devices. Configuration is therefore two-folded by configuration of gateway and the actual physical zigbee device.

**deConz Gateway configuration:**

    deconzAppliance:
        deConzIP:     <ENTER YOUR IP HERE>
        deConzPort:   <ENTER YOUR PORT HERE>
        deConzToken:  <ENTER YOUR AUTH TOKEN HERE>

**ZigBee appliance configuration:**

    zigbeeAppliance:
      - zigbeeApplID: 	1001a
        zigbeeName:   	"Smart Things Garage Gate - Closing State"
        deConzID:     	2
        deConzType:   	"sensors"

### MQTT broker definition (optional):

    mqttAppliance:
      - mqttApplID:   100
        mqttName:     "MQTT Broker Instance"
        mqttIP:       <ENTER YOUR IP HERE>
    	mqttPort:     "1883"
    	mqttUser:     "myUser"
    	mqttPasswd:   "myPasswd"

## Physical device and attribute configurations

The definition of all physical devices and attributes independent of their appliance type is listed under the *attributes* section, each physical device or attribute representing one YAML block item. The corresponding appliance ID (e.g. modbusApplID, zigbeeApplID) links the physical device or attribute to the corresponding appliance.

### General configuration components
Some components (can be also called YAML block items) are shared across appliance types: 
| Component | Purpose | Reference |
|--|--|--|
| *name* (obligatory) | String explanation of attribute, mainly for YAML readability as well as logging purpose |--|
| *knxAddr* (obligatory) | KNX address in *XXX/YYY/ZZZ* representation; for all KNX write actions (e.g. *modbus2knx*) this defines the target the value shall be written to, for all KNX read actions (e.g. *knx2knx*) this defines the source the value shall be retrieved from |--|
| *knxFormat* (obligatory) | DPT representation which defines how the KNX bus expects the value to be represented / value from the KNX bus shall be interpreted. The DPT is supposed to defined in the full DPT value definition, e.g. "*14.077"*, *"1.002"*. Carefully check the DPT type expected for the specific scenarios, e.g. some vendor write *"1.001"* Switch Value with corresponding values *"On"*/*"Off"* while actually expecting *"1.002"* Boolean Value with corresponding values *"True"*/*"False"*.| [KNX DPT Definition](https://web.archive.org/web/20140809211802/http:/www.knx.org/fileadmin/template/documents/downloads_support_menu/KNX_tutor_seminar_page/Advanced_documentation/05_Interworking_E1209.pdf) |
| *updFreq* (obligatory for some appliance types) | Defines the time interval the value shall be checked for changes; this applies to appliances which are polled only (e.g. ZigBee, ModBus) |--|
| *function* (optional) | Set of transformations that can be performed before the value is written to its destination. | [Functions implementation docu](https://github.com/MBizm/KNXBridge/blob/main/src/core/Functions.py) |


## Examples

### ModBus

      - name:           "Current AC Power"
        type:           "modbus2knx"
        modbusApplID:   0
        modbusAddrDec:  100
        modbusFormat:   "float"
        knxAddr:        <ENTER YOUR KNX ADDRESS HERE>
        knxFormat:      "14.056"
        updFreq:        "very high"
      - name:           "Current Power Consumption"
        type:           "modbus2knx"
        modbusApplID:   0
        modbusAddrDec:  [106, 108, 116] #aggregation of ModBus attributes
        modbusFormat:   "float"
        knxAddr:        <ENTER YOUR KNX ADDRESS HERE>
        knxFormat:      "14.056"
        updFreq:        "very high"
    

### ZigBee physical device and attributes
Given example is from a Samsung SmartThings gate control and a Devolo smoke alarm device

      - name:           "Garage Gate Closing State"
        type:           "zigbee2knx"
        zigbeeApplID:   1a
        zigbeeAttr:     "open"
        zigbeeFormat:   "boolean"
        function:       "inv"
        knxAddr:        <ENTER YOUR KNX ADDRESS HERE>
        knxFormat:      "1.002"
        updFreq:        "very high"
      - name:           "Garage Gate LowBattery"
        type:           "zigbee2knx"
        zigbeeApplID:   1b
        zigbeeAttr:     "battery"
        zigbeeFormat:   "int"
        zigbeeSection:  "config"
        function:       "lt(10)"
        knxAddr:        <ENTER YOUR KNX ADDRESS HERE>
        knxFormat:      "1.002"
        updFreq:        "low"
      - name:           "Living Room Fire"
        type:           "zigbee2knx"
        zigbeeApplID:   2a
        zigbeeAttr:     "fire"
        zigbeeFormat:   "boolean"
        knxAddr:        <ENTER YOUR KNX ADDRESS HERE>
        knxFormat:      "1.002"
        updFreq:        "very high"
      - name:           "TER NoConnection"
        type:           "zigbee2knx"
        zigbeeApplID:   2a
        zigbeeAttr:     "lastupdated"
        zigbeeFormat:   "date"
        function:       "timedeltaGT(900)"
        knxAddr:        <ENTER YOUR KNX ADDRESS HERE>
        knxFormat:      "1.002"
        updFreq:        "medium"

### MQTT attribute
  
    - name:           " Waterflow sensor"
        type:           "mqtt2knx"
        mqttApplID:     100
        mqttTopic:      "/waterflow"
        knxAddr:        <ENTER YOUR KNX ADDRESS HERE>
        knxFormat:      "14.077"   # liter/sec

### KNX physical device and attributes (knx2knx)

      - name:           "Solar Extra Production" # PV Mehrerlös
        type:           "knx2knx"
        knxAddr:        <ENTER YOUR KNX ADDRESS HERE>
        knxFormat:      "14.056"
        knxDest:        <ENTER YOUR KNX ADDRESS HERE>
        function:       "sub(<ENTER YOUR KNX ADDRESS HERE>), max(0)"
      - name:           "AZ Paneel on/off status"
        type:           "knx2knx"
        knxAddr:        <ENTER YOUR KNX ADDRESS HERE>
        knxFormat:      "1.002"
        knxDest:        <ENTER YOUR KNX ADDRESS HERE>

