from typing import Dict

import requests
import yaml

### ZigBee constants
# ZigBee client type
from EIBClient import EIBClientListener, EIBClientFactory
from common import printGroup, printValue
from core.DeviceBase import KNXDDevice
from core.util.BasicUtil import log
from core.util.ZigBeeUtil import zigbee_utils

ZIGBEETYPEDEF: Dict[int, str] = {
    0: "lights",
    1: "switches",
    2: "sensors",
    3: "groups"
}


class ZigBeeGateway:
    """ central singleton gateway handling all ZigBee client requests (r/w) """
    __instance = None
    __deconzIP = None
    __deconzPort = 0
    __deconzToken = None
    __state = None

    def __new__(cls, *args, **kwargs):
        if ZigBeeGateway.__instance is None:
            ZigBeeGateway.__instance = object.__new__(cls)
        return ZigBeeGateway.__instance

    @staticmethod
    def initialize(deconzIP, deconzPort, deconzToken):
        ZigBeeGateway.__deconzIP = deconzIP
        ZigBeeGateway.__deconzPort = deconzPort
        ZigBeeGateway.__deconzToken = deconzToken
        ZigBeeGateway.__state = None

    def isActive(self):
        # check whether ZigBeeGateway is initialized
        if ZigBeeGateway.__deconzIP is None or ZigBeeGateway.__deconzPort is None or ZigBeeGateway.__deconzToken is None:
            return False
        return True

    def getState(self):
        """ performs get request to load latest status of all clients """

        try:
            response = requests.get("http://{0}:{1}/api/{2}/".format(ZigBeeGateway.__deconzIP,
                                                                     ZigBeeGateway.__deconzPort,
                                                                     ZigBeeGateway.__deconzToken))
            ZigBeeGateway.__state = yaml.safe_load(response.text)
        except requests.exceptions.RequestException as e:
            print("ZigBeeGateway - could not load client information: {0}".format(e))

    def getClientState(self, id, type, attr, section=None):
        """ get attribute for a defined client """
        ret = None

        # default is state sectionwith only a few exceptions
        if section is None:
            section = 'state'

        if not ZigBeeGateway.__state:
            # check if state information was requested at least once
            self.getState()

        try:
            # section can be omitted by specifying >>zigbeeSection: ''<< in configuration
            if len(section) > 0:
                ret = ZigBeeGateway.__state[type][str(id)][section][attr]
            else:
                ret = ZigBeeGateway.__state[type][str(id)][attr]
        except KeyError as ex:
            log('error',
                'Configuration error - attribute "{0}" in section "{1}" for deConzID "{2}" type "{3}" not defined: {4}'.format(
                    attr, section, id, type, ex))
        except TypeError as ex :
            log('error',
                'Configuration error (2) - attribute "{0}" in section "{1}" for deConzID "{2}" type "{3}" not defined: {4}'.format(
                    attr, section, id, type, ex))

        return ret

    def putClientState(self, id, type, attr, val):
        """ send attribute update and returns true if successful """

        response = requests.put("http://{0}:{1}/api/{2}/{3}/{4}/{5}".format(ZigBeeGateway.__deconzIP,
                                                                            ZigBeeGateway.__deconzPort,
                                                                            ZigBeeGateway.__deconzToken,
                                                                            type,
                                                                            id,
                                                                            'state'),
                                json={attr: val})

        if response.status_code != 200:
            return False
        return True


class ZigBeeClient(KNXDDevice):
    """ client stub addressing one section in ZigBee Gateway response via the gateway

        Basic client representation according to Dresden Elektroniks documentation:
        http://dresden-elektronik.github.io/deconz-rest-doc/
    """

    # reference to ZigBee Gateway singleton

    def __init__(self, name, deconzID, deconzType):
        super(ZigBeeClient, self).__init__()
        self.name = name
        self.deconzID = deconzID
        self.deconzType = deconzType

    # generic attributes
    @property
    def reachable(self) -> bool:
        """True if light is reachable and accepts commands."""

        section = None
        # reachable flag is listed in config section for sensores, while in state section for lights
        if self.deconzType == ZIGBEETYPEDEF[2]:  # sensors
            section = 'config'

        return ZigBeeGateway().getClientState(self.deconzID,
                                              self.deconzType,
                                              "reachable",
                                              section)

    @property
    def uniqueID(self) -> str:
        """Client MAC address."""
        return ZigBeeGateway().getClientState(self.deconzID,
                                              self.deconzType,
                                              "uniqueid",
                                              section='')

    #########################################
    #   ZigBee specific read/write methods  #
    #########################################

    # specific attribute requests based on configuration
    def getAttribute(self, name, zbFormat, zbAttr, zbSection=None):
        """ returns defined attribute for client """
        return ZigBeeGateway().getClientState(self.deconzID,
                                              self.deconzType,
                                              zbAttr,
                                              zbSection)

    def setAttribute(self, attr, val):
        """ sends request to update client status, will return true in case of success """
        return ZigBeeGateway().putClientState(self.deconzID,
                                              self.deconzType,
                                              attr,
                                              val)

    def installListener(self, attrName: str,
                        knxSrc: str, knxFormat: str,
                        zbAttr: str, zbFormat: str, zbSection: str):
        # create new listener that will route incoming knx events and zigbee update requests
        listener = ZigBeeClientListener(self, attrName,
                                        knxSrc, knxFormat,
                                        zbAttr, zbFormat, zbSection)
        # register listener on central EIB/KNX bus monitor
        EIBClientFactory().registerListener(listener)

    #########################################
    #           overridden KNX methods      #
    #########################################
    def writeKNXAttribute(self, attrName, knxDest, knxFormat, val, function=None, flags=None) -> bool:
        """ adds additional reachable check for client """
        ret = None
        if self.reachable:
            ret = super().writeKNXAttribute(attrName,
                                            knxDest,
                                            knxFormat,
                                            val,
                                            function,
                                            flags)
        else:
            log('error',
                'Could not connect to ZigBee client {0}[{1}]'.format(attrName,
                                                                     self.uniqueID))

        return ret


class ZigBeeClientListener(EIBClientListener):
    """
    will route knx event trigger received from EIB/KNX client to zigbee device
    """

    def __init__(self, zbClient: ZigBeeClient, attrName: str,
                 knxSrc: str, knxFormat: str,
                 zbAttr: str, zbFormat: str, zbSection: str):
        # call super class
        super().__init__(knxSrc)
        # store instance attributes
        self.zbClient = zbClient
        self.attrName = attrName
        self.knxFormat = knxFormat
        self.zbSection = zbSection
        self.zbAttr = zbAttr
        self.zbFormat = zbFormat
        # self.knxAggr = knxAggr
        # self.zigTrans = zigTrans

    def updateOccurred(self, srcAddr, val):
        """
        takes value from KNX and sends it to ZigBee device
        """
        knxSrc = printGroup(self.gaddrInt)

        val = printValue(val, len(val))

        # avoid error state in case KNX device is reset via the KNX app
        if not val:
            return

        val = int(val, 16)

        # transform data from python to zigbee protocol adequate form
        zbValue = zigbee_utils.getZigBeeValue(self.zbFormat, val)

        # sends update to zigbee device
        if self.zbClient.setAttribute(attr=self.zbAttr, val=zbValue):
            log('change',
                'Value updated based on KNX value change {0}({1}): {2}(KNX value: {3}) for ZigBee client {4}'.format(
                    self.attrName, knxSrc,
                    zbValue, val,
                    self.zbClient.uniqueID))
        else:
            log('error',
                'Value could not be updated based on KNX value change {0}({1}): {2}(KNX value: {3}) for ZigBee client {4}'.format(
                    self.attrName, knxSrc,
                    zbValue, val,
                    self.zbClient.uniqueID))
