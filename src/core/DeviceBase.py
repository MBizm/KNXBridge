import os
import re

from EIBClient import EIBClientFactory
from common import printValue
from core import Functions, Flags
from core.ApplianceBase import ApplianceBase
from core.util.BasicUtil import log, is_number, convert_number, is_bool, NoneValueClass
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

    def writeAttribute(self, type: str, attrName: str,
                          knxDest: str, knxFormat: str,
                          val, function=None, flags=None, appliance: ApplianceBase = None) -> bool:
        """
        segregator function to allow derived classes to have their own KNX independent implementation
        """
        ret = False

        if type == 'modbus2knx' or type == 'zigbee2knx' or type == 'knx2knx':
            ret = self.writeKNXAttribute(attrName, knxDest, knxFormat, val, function, flags)
        else:
            raise NotImplementedError

        return ret

    #########################################
    #   KNX specific methods, read/write    #
    #########################################
    @staticmethod
    def __readKNXAttributeRaw(knxSrc):
        """
        reads values via EIB/KNX client
        :returns    KNX raw value from bus
        """

        # EIBCache gets stuck in the processing when explicitly calling readKNXAttribute +
        # EIBCache throws errors for existing exceptions for addresses not within the major address space
        # e.g. Client source address "1/1/1", works for "1/1/2" or "1/2/1" but not for "24/1/1"
        #
        # retrieve values via cmd tool as alternative
        #try:
        #    raw = EIBClientFactory().getClient().GroupCache_Read(knxSrc)
        #except ValueError:
        raw = os.popen('knxtool groupcacheread ip:{0} {1}'.format(KNXGateway().hostIP,
                                                                  knxSrc)).readline().strip()
        # extract result from stdout output
        regex = r": (.*?)$"
        rf = re.findall(regex, raw)
        if len(rf) > 0:
            raw = rf[0].strip()

        return raw

    def readKNXAttribute(self, attrName, knxSrc, knxFormat, function=None):
        """
        reads values via EIB/KNX client
        :returns    pythonic value from bus
        """
        val = None

        raw = KNXDDevice.__readKNXAttributeRaw(knxSrc)

#        # convert value from string representation into hex
#        dpt = int(dpt, 16)

        # get DPT implementation for python type conversion
        dc = DPTXlatorFactoryFacade().create(knxFormat)

        try:
            # transform to hex representation
            raw = "0x" + raw.replace(" ", "")
            # convert by respective Xlator
            val = dc.dataToValue(int(raw, 16))

            log('info', f'Value retrieved (group cache) "{attrName}"[{knxSrc}] value={val}({raw})')
        except DPTXlatorValueError as ex:
            # log failure
            log('error',
                f'Value could not be read "{attrName}"[{knxSrc}] value={raw} - Check type definition for DPT type "{knxFormat}" and value "{raw}" - {ex}')
        except (TypeError, ValueError) as ex:
            # log failure
            log('error',
                f'Value could not be read "{attrName}"[{knxSrc}] value={raw} - {ex}')

        return val

    def writeKNXAttribute(self, attrName:str,
                          knxDest:str, knxFormat:str,
                          val, function=None, flags=None) -> bool:
        """
        writes values via the KNXD command line tool
        :returns true if successful
        """
        dpt = None

        # get DPT implementation
        dc = DPTXlatorFactoryFacade().create(knxFormat)

        if dc is None:
            return False

        # perform transformations if defined before sending to bus
        if function:
            val = self.performFunction(dc.dpt, function, val,
                                       attrName, knxDest, knxFormat)

        # check value, some functions like an exclusive equal comparison may return None
        # for valid reason with no further write action to be performed
        if val is None:
            return False
        # indicate legitim None value
        if type(val) is NoneValueClass:
            return True

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
                f'Value could not be updated "{attrName}"[{knxDest}] value={val} - Check type definition for DPT type "{knxFormat}" and value "{val}", Details: {ex}')

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

    def performFunction(self, dpt, function, val,
                        attrName, knxDest, knxFormat):
        """ calls Functions library, overwrite in case of client specific behavior required """
        return Functions.executeFunction(self, dpt, function, val,
                                         attrName, knxDest, knxFormat)

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
            curKNXVal = KNXDDevice.__readKNXAttributeRaw(knxDest)

            if len(newVal) == 1 and len(curKNXVal) == 2:
                curKNXVal = curKNXVal[1:]

            curKNXVal = curKNXVal.upper().strip()
            newVal = newVal.upper().strip()

            # normalize numeric and boolean values
            if is_number(curKNXVal):
                curKNXVal = convert_number(curKNXVal)
            elif is_bool(curKNXVal):
                curKNXVal = bool(curKNXVal)
            if is_number(newVal):
                newVal = convert_number(newVal)
            elif is_bool(newVal):
                newVal = bool(newVal)

            # compare normalized values
            ret = curKNXVal == newVal
        except ValueError as ex:
            log('warning',
                'Value comparison failed - {0}'.format(ex))
        except BrokenPipeError as ex:
            log('warning',
                'Value comparison failed (broken pipe) - {0}'.format(ex))
        return ret

    #################################################
    #   target client methods, read/write           #
    #   target client may be modbus, zigbee, ...    #
    #################################################
    def getAttribute(self, name, format, attr):
        """ retrieves the value from specific client and converts it into python datatype"""
        raise NotImplementedError

    def setAttribute(self, attr, val, function):
        raise NotImplementedError
