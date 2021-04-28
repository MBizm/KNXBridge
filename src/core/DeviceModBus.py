from datetime import datetime

from pymodbus.client.sync import ModbusTcpClient

from core.DeviceBase import KNXDDevice
from core.util.BasicUtil import log
from core.util.ModBusUtil import modbus_utils


class ModBusClient(KNXDDevice):
    def __init__(self, host, port):
        super(ModBusClient, self).__init__()

        self.__mbcImpl = ModbusTcpClient(host, port)

    # specific attribute requests based on configuration
    def getAttribute(self, attrName, mbFormat, mbAddr):
        val = None

        if self.__mbcImpl.connect():
            try:
                # check modbus data type
                # TODO implement more ModBus datatypes
                if mbFormat == 'float':
                    # configuration supports summing up multiple values automatically
                    # single value from corresponding modbus client
                    if isinstance(mbAddr, int):
                        val = modbus_utils.ReadFloat(self.__mbcImpl,
                                                     mbAddr)
                    # sum of multiple values from corresponding modbus client
                    elif isinstance(mbAddr, list):
                        val = 0
                        # TODO implement functions
                        for ids in mbAddr:
                            val = val + modbus_utils.ReadFloat(self.__mbcImpl,
                                                               ids)
            except Exception as ex:
                log('error',
                    'Error reading ModBus value - {0}: {1}'.format(attrName,
                                                                   ex))

            self.__mbcImpl.close()
        else:
            # log connection error
            log('error',
                'Could not connect to ModBus server {0}:{1}'.format(self.__mbcImpl.host,
                                                                    self.__mbcImpl.port))

        return val

    def setAttribute(self, attr, val):
        """
        sends request to update client status, currently not implemented
        :exception will throw error in all cases
        """
        raise NotImplementedError
