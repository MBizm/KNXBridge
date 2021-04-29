import os

from EIBClient import EIBClientFactory
from core import Functions, Flags
from core.util.BasicUtil import log
from core.util.KNXDUtil import DPTXlatorFactoryFacade
from pknyx.core.dptXlator.dptXlatorBase import DPTXlatorValueError


class KNXGateway:
    """ central singleton instance with KNX Gateway host information """
    __instance = None
    __hostIP = None

    def __new__(cls, *args, **kwargs):
        if KNXGateway.__instance is None:
            KNXGateway.__instance = object.__new__(cls)
        return KNXGateway.__instance

    def setHostIP(self, hostIP):
        KNXGateway.__hostIP = hostIP

    @property
    def hostIP(self):
        """ IP address of the machine where KNXD process is running """
        return KNXGateway.__hostIP


class KNXDDevice:
    """
    abstract device implementation allowing interaction with EIB/KNX client (https://github.com/MBizm/KNXPClient)
    derive all endpoint device class (zigbee, modbus, ...) from this class
    use KNX read/write methods for interaction with the KNX device
    """

    #########################################
    #   KNX specific methods, read/write    #
    #########################################
    def readKNXAttribute(self, attrName, knxSrc, knxFormat, function=None):
        """
        reads values via EIB/KNX client
        :returns    pythonic value from bus
        """
        val = None

        dpt = EIBClientFactory().getClient().GroupCache_Read(knxSrc)

        # convert value from string representation into hex
        dpt = int(dpt, 16)

        # get DPT implementation for python type conversion
        dc = DPTXlatorFactoryFacade().create(knxFormat)

        try:
            if dc.checkData(dpt):
                val = dc.dataToValue(dpt)

                log('info',
                    f'Value retrieved (group cache) "{attrName}"[{knxSrc}] value={val}({dpt})')
        except DPTXlatorValueError as ex:
            # log failure
            log('error',
                f'Value could not be read "{attrName}"[{knxSrc}] value={dpt} - Check type definition for DPT type "{knxFormat}" and value "{dpt}" - {ex}')
        except (TypeError, ValueError) as ex:
            # log failure
            log('error',
                f'Value could not be read "{attrName}"[{knxSrc}] value={dpt} - {ex}')

        return val

    def writeKNXAttribute(self, attrName, knxDest, knxFormat, val, function=None, flags=None) -> bool:
        """
        writes values via the KNXD command line tool
        :returns true if successful
        """
        dpt = None

        # get DPT implementation
        dc = DPTXlatorFactoryFacade().create(knxFormat)

        # perform transformations if defined before sending to bus
        if function:
            val = self.performFunction(dc.dpt, function, val)

        # check value, some functions like an exclusive equal comparison may return None
        # for valid reason with no further write action to be performed
        if val is None:
            return False

        # convert to DPT representation
        try:
            if dc.checkValue(val):
                dpt = dc.valueToData(val)
        except DPTXlatorValueError:
            # log failure
            log('error',
                f'Value could not be updated "{attrName}"[{knxDest}] value={val} - Check type definition for DPT type "{knxFormat}" and value "{val}"')
        except (TypeError, ValueError) as ex:
            # log failure
            log('error',
                f'Value could not be updated "{attrName}"[{knxDest}] value={val} - {ex}')

        if dpt is None:
            return False

        # do not load the bus with unnecessary request, check against cached value
        if (flags and Flags.FLAGS_FORCE in flags) or \
                not self.isCurrentKNXAttribute(knxDest, knxFormat, dpt):
            # send value to the knx bus
            os.popen('knxtool groupwrite ip:{0} {1} {2}'.format(KNXGateway().hostIP,
                                                                knxDest,
                                                                dpt))

            # log success
            if flags and Flags.FLAGS_FORCE in flags:
                log('change',
                    f'Updated value (enforced) on KNX bus "{attrName}"[{knxDest}] value={val}[DPT:{dpt}]')
            else:
                log('change',
                    f'Updated value on KNX bus "{attrName}"[{knxDest}] value={val}[DPT:{dpt}]')
        else:
            # log success
            log('info',
                f'Value is up to date "{attrName}"[{knxDest}] value={val}')

        return True

    def performFunction(self, dpt, function, val):
        """ calls Functions library, overwrite in case of client specific behavior required """
        return Functions.executeFunction(self, dpt, function, val)

    @staticmethod
    def isCurrentKNXAttribute(knxDest, knxFormat, newVal) -> bool:
        """
        checks whether new value matches to stored value last sent on the bus
        :param knxFormat:   DPT format that is expected for the given destination
        :param knxDest:     KNX destionation under which the value is stored
        :param newVal:      value in dpt representation
        :returns            true if new value matches cached value
        """
        ret = False
        try:
            curKNXVal = EIBClientFactory().getClient().GroupCache_Read(knxDest)

            if len(newVal) == 1 and len(curKNXVal) == 2:
                curKNXVal = curKNXVal[1:]

            ret = curKNXVal.upper() == newVal.upper()
        except ValueError as ex:
            log('warning',
                'Value comparison failed - {0}'.format(ex))
        return ret

    #################################################
    #   target client methods, read/write           #
    #   target client may be modbus, zigbee, ...    #
    #################################################
    def getAttribute(self, name, format, attr):
        """ retrieves the value from specific client and converts it into python datatype"""
        raise NotImplementedError

    # TODO define format for setAttribute abstract methods
