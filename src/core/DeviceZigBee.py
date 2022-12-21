from typing import Dict

import requests
import yaml
import json

### ZigBee constants
# ZigBee client type
from EIBClient import EIBClientListener, EIBClientFactory
from common import printGroup, printValue
from core import Functions
from core.DeviceBase import KNXDDevice
from core.util.BasicUtil import log
from core.util.ZigBeeUtil import zigbee_utils
from json.decoder import JSONDecodeError

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
        if not(self.isActive()):
            return

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

        if not(self.isActive()):
            return ret

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

    def putClientState(self, id, type, attr, val, function):
        """ send attribute update and returns true if successful """
        if not(self.isActive()):
            return False

        # perform transformations if defined before sending
        if function:
            val = Functions.executeFunction(None, None, function, val,
                                            attr, None, None)

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

    def setAttribute(self, attr, val, function):
        """ sends request to update client status, will return true in case of success """
        return ZigBeeGateway().putClientState(self.deconzID,
                                              self.deconzType,
                                              attr,
                                              val,
                                              function)

    def installListener(self, attrName: str,
                        knxSrc: str, knxFormat: str,
                        zbAttr: str, zbFormat: str, zbSection: str, function: str):
        # create new listener that will route incoming knx events and zigbee update requests
        if knxSrc.find("[") == -1:
            listener = ZigBeeClientListener(self, attrName,
                                            knxSrc, knxFormat,
                                            zbAttr, zbFormat, zbSection, function)
            # register listener on central EIB/KNX bus monitor
            EIBClientFactory().registerListener(listener)
        # create new group listener that will route multiple incoming knx events and zigbee update requests
        else:
            # parse group definition
            try:
                knxSrc = json.loads(knxSrc)
                if not type(knxSrc) == list:
                    raise ValueError()
            except JSONDecodeError as e:
                log('error',
                    'Could not interpret value attribute: {0} knxSrc: {1}'.format(attrName,
                                                                                    knxSrc))
            except ValueError as e:
                log('error',
                    'Wrong group definition, group must be of type list - attribute: {0} knxSrc: {1}'.format(attrName,
                                                                                                                knxSrc))
            # create group listener
            glistener = ZigBeeGroupInstance(self, attrName,
                                            knxSrc, knxFormat,
                                            zbAttr, zbFormat, zbSection, function)
            # register listener on central EIB/KNX bus monitor
            for listener in glistener.getListenerList():
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
                 zbAttr: str, zbFormat: str, zbSection: str, function: str):
        # call super class
        super().__init__(knxSrc)
        # store instance attributes
        self.zbClient = zbClient
        self.attrName = attrName
        self.knxFormat = knxFormat
        self.zbSection = zbSection
        self.zbAttr = zbAttr
        self.zbFormat = zbFormat
        self.function = function
        # self.knxAggr = knxAggr
        # self.zigTrans = zigTrans

    def updateOccurred(self, srcAddr, val):
        """
        takes value from KNX and sends it to ZigBee device
        """
        self.fireUpdate(val)

    def fireUpdate(self, val):
        """
        actual implementation to send update to ZigBee device
        """
        knxSrc = printGroup(self.gaddrInt)

        if self.zbFormat != zigbee_utils.ZBFORMAT_LIST and \
                self.zbFormat != zigbee_utils.ZBFORMAT_MIREDCOL:
            # convert buffer to hex string representation
            val = printValue(val, len(val))

            # avoid error state in case KNX device is reset via the KNX app
            if not val:
                return

            val = int(val, 16)

        # transform data from python to zigbee protocol adequate form
        zbValue = zigbee_utils.getZigBeeValue(self.zbFormat, val)

        # sends update to zigbee device
        if self.zbClient.setAttribute(attr=self.zbAttr, val=zbValue, function=self.function):
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

class ZigBeeGroupInstance():
    """
    will route multiple knx event trigger received from EIB/KNX client to zigbee device
    """

    def __init__(self, zbClient: ZigBeeClient, attrName: str,
                 knxSrcs: str, knxFormat: str,
                 zbAttr: str, zbFormat: str, zbSection: str, function: str):
        super().__init__()
        self.__listenerList = []
        # event list to track all events before sending zigbee command
        self.__events = None

        srcs = []
        for src in knxSrcs:
            # convert keys to EIB representation if required
            srcs.append(src.replace("/", "."))
            listener = ZigBeeGroupClientListener(self, zbClient, attrName,
                                                    src, knxFormat,
                                                    zbAttr, zbFormat, zbSection, function)
            # store listener reference
            self.__listenerList.append(listener)

        self.__events = dict.fromkeys(srcs, None)

    def getListenerList(self):
        return self.__listenerList

    def updateOccurred(self, listener: ZigBeeClientListener, knxSrc: str, val):
        # store value in event list
        self.__events[knxSrc] = val

        is_ready = True

        for src in self.__events.keys():
            if self.__events[src] is None:
                is_ready = False
                break

        if is_ready:
            # send update
            listener.fireUpdate(list(self.__events.values()))

             # reset event values
            for src in self.__events.keys():
                self.__events[src] = None


class ZigBeeGroupClientListener(ZigBeeClientListener):
    """
    overrides base class to accumulate events of the group before sending zigbee update
    """

    def __init__(self, zbGroup: ZigBeeGroupInstance, zbClient: ZigBeeClient, attrName: str,
                 knxSrc: str, knxFormat: str,
                 zbAttr: str, zbFormat: str, zbSection: str, function: str):
        super().__init__(zbClient, attrName,
                            knxSrc, knxFormat,
                            zbAttr, zbFormat, zbSection, function)
        self.__zbGroup = zbGroup

    def updateOccurred(self, srcAddr, val):
        knxSrc = printGroup(self.gaddrInt)

        # convert buffer to hex string representation
        val = printValue(val, len(val))

        # avoid error state in case KNX device is reset via the KNX app
        if not val:
            return

        val = int(val, 16)

        # delegate decision to send event to group instance
        self.__zbGroup.updateOccurred(self, knxSrc, val)