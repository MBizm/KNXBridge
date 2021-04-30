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

