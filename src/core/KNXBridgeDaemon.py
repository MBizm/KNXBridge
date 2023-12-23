#####################################################################################################################
#
#   ModBus-KNX Gateway script - sending data via simple configuration
#   The script and the configuration file are provided under Apache 2.0 license.
#   Author: MBizm [https://github.com/MBizm]
#
#   The ModBus-KNX Gatway sends data from a ModBus appliance to KNX. It is based on the IP/KNX Gateway device with an installed KNXD library.
#   All configuration can be done via the CONFIG.yaml file. Follow the below instruction. The configuration file contains the following sections:
#     -config section:
#           -- general configurations for executing the script
#           -- define your intended logging level here ("off", "error", "info") with "info" providing information about each sent attribute
#     - modbusAppliance:
#           -- defines all physical appliances that shall be linked. The script supports multiple ModBus devices as source for data sent to the KNX bus.
#           -- Attributes are linked via the [modbusApplID] attribute id that every attribute needs to define
#           -- knxdIP represents the IP/KNX bus devices IP
#     - attributes:
#           -- list of attributes transferred between the ModBus appliance and the KNX bus
#           -- script currently only supports ModBus-READ and KNX-WRITE instructions, defined by [type] value "modbus2knx"
#           -- [modbusAddrDec] defines the ModBus address in decimal representation, [modbusFormat] the ModBus attribute data type - currently only "float" is supported
#           -- [modbusAddrDec] allows the automatic calculation of the sum of several ModBus addresses by "[addr1, addr2]" representation
#           -- [knxAddr] defines the KNX address in "x/y/z" notation, [knxFormat] the KNX DPT data type
#           -- [updFreq] defines the frequency the attribute is updated:
#               --- "very high"   - updates once every 10sec, be careful not to flood the bus with too many requests
#               --- "high"        - updates once every minute
#               --- "medium"      - updates once every hour
#               --- "low"         - updates once every 24hours
#
#####################################################################################################################
from threading import Timer
from typing import Dict

from core.DeviceBase import KNXGateway
from core.DeviceKNX import KNX2KNXClient, KNX2KNXFactory
from core.DeviceMQTT import MQTTAppliance
from core.DeviceModBus import ModBusClient
from core.DeviceZigBee import ZigBeeClient, ZigBeeGateway
from core.util.BasicUtil import readConfig, setLogLevel, getAttrSafe, log

# dictionary for update frequency mask
UPDATEFREQ: Dict[str, int] = {
    "critical": 0x01,
    "very high": 0x02,
    "high": 0x04,
    "medium": 0x08,
    "low": 0x10,
    "very low": 0x20,
    "initial": 0xFF
}


class KNXWriter:

    def __init__(self):
        configuration = readConfig()

        # check if configuration can be loaded
        if not configuration:
            exit(1)

        #####   Get Gateway information #####
        # get KNXD TCP/Bus configuration
        KNXGateway().setHostIP(configuration['knxdAppliance']['knxdIP'])

        # get ZigBee Gateway configuration
        if 'deconzAppliance' in configuration.keys():
            ZigBeeGateway().initialize(configuration['deconzAppliance']['deConzIP'],
                                       configuration['deconzAppliance']['deConzPort'],
                                       configuration['deconzAppliance']['deConzToken'])

        #####   Get external client information #####
        # build up list of defined modbus clients
        self.modbusClients = {}
        for cc in configuration['modbusAppliance']:
            self.modbusClients[cc['modbusApplID']] = ModBusClient(cc['modbusIP'],
                                                                  cc['modbusPort'])

        # build up list of defined MQTT appliance
        # due to the self-contained (threaded) architecture of MQTT client, MQTT clients
        # will be set up in initialization as part of update method
        self.mqttAppliances = {}
        for cc in configuration['mqttAppliance']:
            self.mqttAppliances[cc['mqttApplID']] = MQTTAppliance(cc['mqttIP'],
                                                                  getAttrSafe(cc, 'mqttPort'),
                                                                  getAttrSafe(cc, 'mqttUser'),
                                                                  getAttrSafe(cc, 'mqttPasswd'))

        # build up list of defined zigbee devices
        self.zigbeeClients = {}
        for cc in configuration['zigbeeAppliance']:
            self.zigbeeClients[cc['zigbeeApplID']] = ZigBeeClient(cc['zigbeeName'],
                                                                  cc['deConzID'],
                                                                  cc['deConzType'])

        #####   Store list of client attributes #####
        # get update attribute list
        self.attrs = configuration['attributes']

        # verbosity level
        setLogLevel(configuration['configVerbose'])

    def update(self, freq):
        global UPDATEFREQ

        #####   initialization of clients #####
        # ModBus clients will be implicitely update as part of the getAttribute call

        # initialize ZigBee Gateway with latest client state
        if ZigBeeGateway().isActive():
            ZigBeeGateway().getState()

        # iterate list of attributes to be updated
        for attr in self.attrs:

            # first time initialization steps
            if UPDATEFREQ['initial'] & freq == UPDATEFREQ['initial']:
                # setup knx-based event trigger based on EIB/KNX client listener
                # ModBus - currently not implemented
                if attr['type'] == 'knx2modbus':
                    raise NotImplementedError
                # set up ZigBee listener
                elif attr['type'] == 'knx2zigbee':
                    # find corresponding ZigBee device
                    if attr['zigbeeApplID'] in self.zigbeeClients:
                        client = self.zigbeeClients[attr['zigbeeApplID']]
                        client.installListener(attr['name'],
                                               attr['knxAddr'], attr['knxFormat'],
                                               attr['zigbeeAttr'], attr['zigbeeFormat'],
                                               getAttrSafe(attr, 'zigbeeSection'), getAttrSafe(attr, 'function'))
                elif attr['type'] == 'knx2knx':
                    # initialize new client, implicitely setting up the listener during construction
                    # usually KNX clients react to changes to the KNX source ('knxAddr') but can also define an update frequency explicitely
                    client = KNX2KNXFactory.initializeClient(attr['name'],
                                                               attr['knxAddr'], attr['knxFormat'],
                                                               attr['knxDest'], getAttrSafe(attr, 'function'),
                                                               getAttrSafe(attr, 'flags'))
                elif attr['type'] == 'mqtt2knx':
                    # mqtt client defines its own thread which permanently listens to update events
                    # avoid registering to targets which flood your KNX bus due to high frequency of update
                    if attr['mqttApplID'] in self.mqttAppliances:
                        appliance = self.mqttAppliances[attr['mqttApplID']]
                        appliance.setupClient(attr['name'], attr['mqttTopic'],
                                              attr['knxAddr'], attr['knxFormat'],
                                              getAttrSafe(attr, 'mqttFormat'),
                                              getAttrSafe(attr, 'function'),
                                              getAttrSafe(attr, 'flags'))

            # check attribute update frequency matches current thread definition
            if 'updFreq' in attr and UPDATEFREQ[attr['updFreq']] & freq > 0:

                client = None
                newVal = None
                appliance = None

                destAddr = getAttrSafe(attr, 'knxAddr')
                destFormat = getAttrSafe(attr, 'knxFormat')

                # check update type - currently only modbus read, knx write is supported
                if attr['type'] == 'modbus2knx' or attr['type'] == 'modbus2mqtt':
                    # find corresponding ModBus device
                    if attr['modbusApplID'] in self.modbusClients:
                        client = self.modbusClients[attr['modbusApplID']]

                        # get latest ModBus value for attribute
                        newVal = client.getAttribute(attr['name'],
                                                     attr['modbusFormat'],
                                                     attr['modbusAddrDec'])

                        # define appliance and destination for sending MQTT updates
                        if attr['type'] == 'modbus2mqtt':
                            appliance = self.mqttAppliances[attr['mqttApplID']]
                            destAddr = attr['mqttTopic']
                            destFormat = None
                    else:
                        log('error',
                            'Configuration error - modbusApplID({0}) not defined'.format(attr['zigbeeApplID']))
                # handle ZigBee attributes
                elif attr['type'] == 'zigbee2knx' and ZigBeeGateway().isActive():
                    # find corresponding ZigBee device
                    if attr['zigbeeApplID'] in self.zigbeeClients:
                        client = self.zigbeeClients[attr['zigbeeApplID']]

                        # get latest ZigBee value for attribute
                        newVal = client.getAttribute(attr['name'],
                                                     attr['zigbeeFormat'],
                                                     attr['zigbeeAttr'],
                                                     getAttrSafe(attr, 'zigbeeSection'))
                    else:
                        log('error',
                            'Configuration error - zigbeeApplID({0}) not defined'.format(attr['zigbeeApplID']))
                # handle knx attributes that explicitly define an update frequency
                # normal knx client reacts to changes to the knx source address
                elif attr['type'] == 'knx2knx':
                    # get defined knx client
                    client = KNX2KNXFactory.getClient(attr['name'])
                    # knx2knx protocal foresees 'knxAddr' as the source and 'knxDest' as the destination
                    destAddr = getAttrSafe(attr, 'knxDest')
                    # get current value of source address
                    newVal = client.getSrcValue()

                # write value to bus
                if client is not None and newVal is not None:
                    client.writeAttribute(attr['type'],
                                             attr['name'],
                                             destAddr,
                                             destFormat,
                                             newVal,
                                             getAttrSafe(attr, 'function'),
                                             getAttrSafe(attr, 'flags'),
                                             appliance)

        # run periodically update of values - each update frequency initiating its own thread
        # initial run by main will initiate all threads at once
        ut = None
        if freq & UPDATEFREQ['critical'] > 0:
            # CRITICAL - runs every 3 seconds - ONLY USE IN EXCEPTIONABLE CASES!!
            ut = Timer(3, gateway.update, (UPDATEFREQ['critical'],))
            ut.start()
        if freq & UPDATEFREQ['very high'] > 0:
            # VERY HIGH - runs every 10 seconds
            ut = Timer(10, gateway.update, (UPDATEFREQ['very high'],))
            ut.start()
        if freq & UPDATEFREQ['high'] > 0:
            # HIGH - runs every 60 seconds
            Timer(60, gateway.update, (UPDATEFREQ['high'],)).start()
        if freq & UPDATEFREQ['medium'] > 0:
            # MEDIUM - runs every 10 minutes
            Timer(600, gateway.update, (UPDATEFREQ['medium'],)).start()
        if freq & UPDATEFREQ['very low'] > 0:
            # LOW - runs every 60 minutes
            Timer(3600, gateway.update, (UPDATEFREQ['very low'],)).start()
        if freq & UPDATEFREQ['low'] > 0:
            # LOW - runs every 24 hours
            Timer(86400, gateway.update, (UPDATEFREQ['low'],)).start()

        # return reference to very high thread for synchronization
        return ut


if __name__ == '__main__':
    # initialize modbus2knxd gateway
    gateway = KNXWriter()
    # initiate update process - update is self-iterating by starting various timer threads
    thread = gateway.update(UPDATEFREQ['initial'])

    # keep on running... the update thread will run forever
    # https://blog.miguelgrinberg.com/post/how-to-make-python-wait
    thread.join()
