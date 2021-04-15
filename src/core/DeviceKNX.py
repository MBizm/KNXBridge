from EIBClient import EIBClientFactory, EIBClientListener
from common import printGroup, printValue
from core.DeviceBase import KNXDDevice
from core.util.BasicUtil import log


class KNX2KNXClient(KNXDDevice):
    """
    a knx2knx client will router values from a knxSrc address to a knxDest address on the same bus.
    scenarios might be any state changing device that is reflected in the ETS/KNX-system by:
        - a KNX address under which state might be changed (e.g. lamp on/off)
        - a KNX address which represents the status
    without sync, events might be triggered but current status may not be reflected
    """
    def __init__(self):
        """
        empty constructor sufficient
        KNX gateway information by base class singleton instance being initialized centrally
        """
        super()

    def getAttribute(self, name, format, attr):
        # the knx2knx implementation shall get value of src via readKNXAttribute()
        raise NotImplementedError

    def setAttribute(self, attrName: str, val,
                     dest: str, format: str,
                     function: str):
        # reuse base implementation to write value to bus with destination target
        self.writeKNXAttribute(attrName, dest, format,
                               val, function)

    def installListener(self, attrName: str,
                        knxSrc: str, knxFormat: str,
                        knxDest: str, function=None):
        # create new listener that will route incoming knx events and to another knx target
        listener = KNX2KNXClientListener(self, attrName,
                                         knxSrc, knxFormat,
                                         knxDest, function)
        # register listener on central EIB/KNX bus monitor
        EIBClientFactory().registerListener(listener)


class KNX2KNXClientListener(EIBClientListener):
    """
    will route knx event trigger received from EIB/KNX client to another knx device
    """

    def __init__(self, knxClient: KNX2KNXClient, attrName: str,
                 knxSrc: str, knxFormat: str,
                 knxDest: str, function=None):
        # call super class
        super().__init__(knxSrc)
        # store instance attributes
        self.knxClient = knxClient
        self.attrName = attrName
        self.knxFormat = knxFormat
        self.knxDest = knxDest
        self.function = function
        # self.knxAggr = knxAggr
        # self.zigTrans = zigTrans

    def updateOccurred(self, srcAddr, val):
        """
        takes value from KNX and sends it to another knx device
        """
        knxSrc = printGroup(self.gaddrInt)

        val = int(printValue(val, len(val)), 16)

        # currently no conversion from one DPT type to another is foreseen

        # sends update to the other knx device
        if self.knxClient.setAttribute(attrName=self.attrName, val=val,
                                       dest=self.knxDest, format=self.knxFormat,
                                       function=self.function):
            log('info',
                'Value updated based on KNX value change {0}({1}): {2} for KNX client {3}'.format(self.attrName, knxSrc,
                                                                                                  val, self.knxDest))
        else:
            log('error',
                'Value could not be updated based on KNX value change {0}({1}): {2} for KNX client {3}'.format(
                    self.attrName, knxSrc,
                    val, self.knxDest))
