from typing import Dict

import requests
import yaml

### ZigBee constants
# ZigBee client type
from core.DeviceKNXDBase import KNXDDevice
from core.util.BasicUtil import log

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

    def getState(self):
        """ performs get request to load latest status of all clients """
        try:
            response = requests.get("http://{0}:{1}/api/{2}/".format(ZigBeeGateway.__deconzIP,
                                                                     ZigBeeGateway.__deconzPort,
                                                                     ZigBeeGateway.__deconzToken))
            ZigBeeGateway.__state = yaml.safe_load(response.text)
        except requests.exceptions.RequestException as e:
            print("ZigBeeGateway - could not load client information: {0}".format(e))

    def getClientState(self, id, type, attr, section='state'):
        """ get attribute for a defined client """
        ret = None

        if not ZigBeeGateway.__state:
            # check if state information was requested at least once
            self.getState()

        try:
            ret = ZigBeeGateway.__state[type][str(id)][section][attr]
        except KeyError as ex:
            log('error',
                'Configuration error - attribute "{0}" in section "{1}" for deConzID "{2}" type "{3}" not defined: {4}'.format(
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
    def getAttribute(self, name, zbFormat, zbAttr, section='state'):
        """ returns defined attribute for client """
        return ZigBeeGateway().getClientState(self.deconzID,
                                              self.deconzType,
                                              zbAttr,
                                              section)

    def setAttribute(self, attr, val):
        """ sends request to update client status, will return true in case of success """
        return ZigBeeGateway().putClientState(self.deconzID,
                                              self.deconzType,
                                              attr,
                                              val)

    #########################################
    #           overriden KNX methods       #
    #########################################
    def writeKNXAttribute(self, attrName, knxDest, knxFormat, val, function=None) -> bool:
        """ adds additional reachable check for client """
        ret = None
        if self.reachable:
            ret = super().writeKNXAttribute(attrName,
                                            knxDest,
                                            knxFormat,
                                            val,
                                            function)
        else:
            log('error',
                'Could not connect to ZigBee client {0}[{1}]'.format(attrName,
                                                                     self.uniqueID))

        return ret
