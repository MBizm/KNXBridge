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
#           -- script currently only supports ModBus-READ and KNX-WRITE instructions, defined by [type] value "modbus2knx" (TODO)
#           -- [modbusAddrDec] defines the ModBus address in decimal representation, [modbusFormat] the ModBus attribute data type - currently only "float" is supported (TODO)
#           -- [modbusAddrDec] allows the automatic calculation of the sum of several ModBus addresses by "[addr1, addr2]" representation
#           -- [knxAddr] defines the KNX address in "x/y/z" notation, [knxFormat] the KNX DPT data type - currently only "DPT14" is supported (TODO)
#           -- [updFreq] defines the frequency the attribute is updated:
#               --- "very high"   - updates once every 10sec, be careful not to flood the bus with too many requests
#               --- "high"        - updates once every minute
#               --- "medium"      - updates once every hour
#               --- "low"         - updates once every 24hours
#
#####################################################################################################################
import os
import yaml
from datetime import datetime
from typing import Dict
from threading import Timer
from pymodbus.client.sync import ModbusTcpClient
from pymodbus.constants import Endian
from pymodbus.payload import BinaryPayloadDecoder


# -------------- Utility number conversion from registers -------------
# https://forum.fhem.de/index.php/topic,75638.msg987876.html?PHPSESSID=b17q82mhkt6bjj8s550cmgrdjr#msg987876
class modbus_utils:
    def __init__(self):
        pass

    # -----------------------------------------
    # Routine to read a string from one address with 8 registers 
    @staticmethod
    def ReadStr8(client, myadr_dec):
        r1 = client.read_holding_registers(myadr_dec, 8, unit=71)
        STRG8Register = BinaryPayloadDecoder.fromRegisters(r1.registers, byteorder=Endian.Big)
        result_STRG8Register = STRG8Register.decode_string(8)
        return result_STRG8Register
        # -----------------------------------------

    # Routine to read a Float from one address with 2 registers
    @staticmethod
    def ReadFloat(client, myadr_dec):
        r1 = client.read_holding_registers(myadr_dec, 2, unit=71)
        FloatRegister = BinaryPayloadDecoder.fromRegisters(r1.registers, byteorder=Endian.Big, wordorder=Endian.Little)
        result_FloatRegister = round(FloatRegister.decode_32bit_float(), 2)
        return result_FloatRegister
        # -----------------------------------------

    # Routine to read a U16 from one address with 1 register
    @staticmethod
    def ReadU16_1(client, myadr_dec):
        r1 = client.read_holding_registers(myadr_dec, 1, unit=71)
        U16register = BinaryPayloadDecoder.fromRegisters(r1.registers, byteorder=Endian.Big, wordorder=Endian.Little)
        result_U16register = U16register.decode_16bit_uint()
        return result_U16register

    # -----------------------------------------
    # Routine to read a U16 from one address with 2 registers 
    @staticmethod
    def ReadU16_2(client, myadr_dec):
        r1 = client.read_holding_registers(myadr_dec, 2, unit=71)
        U16register = BinaryPayloadDecoder.fromRegisters(r1.registers, byteorder=Endian.Big, wordorder=Endian.Little)
        result_U16register = U16register.decode_16bit_uint()
        return result_U16register

    # -----------------------------------------
    # Routine to read a U32 from one address with 2 registers 
    @staticmethod
    def ReadU32(client, myadr_dec):
        r1 = client.read_holding_registers(myadr_dec, 2, unit=71)
        U32register = BinaryPayloadDecoder.fromRegisters(r1.registers, byteorder=Endian.Big, wordorder=Endian.Little)
        result_U32register = U32register.decode_32bit_uint()
        return result_U32register

    # -----------------------------------------
    # Routine to read a U32 from one address with 2 registers 
    @staticmethod
    def ReadS16(client, myadr_dec):
        r1 = client.read_holding_registers(myadr_dec, 1, unit=71)
        S16register = BinaryPayloadDecoder.fromRegisters(r1.registers, byteorder=Endian.Big, wordorder=Endian.Little)
        result_S16register = S16register.decode_16bit_uint()
        return result_S16register


# -------------- Utility number conversion for KNX DPT -------------

# https://www.geeksforgeeks.org/python-program-to-represent-floating-number-as-hexadecimal-by-ieee-754-standard/
class knxd_util:
    def __init__(self):
        pass

    # Function for converting decimal to binary 
    @staticmethod
    def float_bin(my_number, places=3):
        my_whole, my_dec = str(my_number).split(".")
        my_whole = int(my_whole)
        res = (str(bin(my_whole)) + ".").replace('0b', '')

        for x in range(places):
            my_dec = str('0.') + str(my_dec)
            temp = '%1.20f' % (float(my_dec) * 2)
            my_whole, my_dec = temp.split(".")
            res += my_whole
        return res

        # conversion to IEEE-754 / DPT 14

    # https://www.geeksforgeeks.org/python-program-to-represent-floating-number-as-hexadecimal-by-ieee-754-standard/
    @staticmethod
    def IEEE754(n):
        # identifying whether the number 
        # is positive or negative 
        sign = 0
        if n < 0:
            sign = 1
            n = n * (-1)
        p = 30
        # convert float to binary 
        dec = knxd_util.float_bin(n, places=p)

        dotPlace = dec.find('.')
        onePlace = dec.find('1')
        # finding the mantissa 
        if onePlace > dotPlace:
            dec = dec.replace(".", "")
            onePlace -= 1
            dotPlace -= 1
        elif onePlace < dotPlace:
            dec = dec.replace(".", "")
            dotPlace -= 1
        mantissa = dec[onePlace + 1:]

        # calculating the exponent(E) 
        exponent = dotPlace - onePlace
        exponent_bits = exponent + 127

        # converting the exponent from 
        # decimal to binary 
        exponent_bits = bin(exponent_bits).replace("0b", '')

        mantissa = mantissa[0:23]

        # the IEEE754 notation in binary
        final = str(sign) + exponent_bits.zfill(8) + mantissa

        # convert the binary to hexadecimal 
        hstr = '0x%0*X' % ((len(final) + 3) // 4, int(final, 2))

        # convert hex to knxd format
        kstr = hstr[2:4] + ' ' + hstr[4:6] + ' ' + hstr[6:8] + ' ' + hstr[8:10]

        return (hstr, final, kstr)


class modbus2knxd:
    # dictionary for update frequency mask
    UPD_FREQ: Dict[str, int] = {
        "very high": 0x01,
        "high": 0x02,
        "medium": 0x04,
        "low": 0x08,
        "initial": 0x0F
    }
    # verbosity mask
    VERBOSITY: Dict[str, int] = {
        "off": 0x00,
        "error": 0x01,
        "info": 0x07
    }

    def __init__(self):
        configuration = None

        try:
            with open("CONFIG.yaml", 'r') as stream:
                configuration = yaml.safe_load(stream)
        except OSError as ex:
            print("ERROR: {0} Could not load configuration file".format(datetime.now().strftime("%d.%b. %I:%M:%S")))
            exit(1)

        # build up list of defined modbus clients
        self.modbusClients = []
        for cc in configuration['modbusAppliance']:
            mbc = ModbusTcpClient(host=cc['modbusIP'], port=cc['modbusPort'])
            if cc['modbusApplID'] > len(self.modbusClients):
                self.modbusClients.insert(len(self.modbusClients) - 1, mbc)
            else:
                self.modbusClients.insert(cc['modbusApplID'], mbc)

        # get KNXD TCP/Bus configuration
        self.knxdIP = configuration['knxdAppliance']['knxdIP']

        # get update attribute list
        self.attrs = configuration['attributes']

        # verbosity level
        self.verbosity = type(self).VERBOSITY[configuration['configVerbose']]

    def update(self, freq):
        # initialize connection with modbus clients
        for mbc in self.modbusClients:
            # do not check for success, error will be given by requesting values
            success = mbc.connect()
            if not success and self.verbosity & type(self).VERBOSITY["error"] == self.verbosity & type(self).VERBOSITY["error"]:
                # log connection error
                print('ERROR: {0} Could not connect to ModBus client {1}:{2}'.format(datetime.now().strftime("%d.%b. %I:%M:%S"),
                                                                                     mbc.host,
                                                                                     mbc.port))

        # iterate list of attributes to be updated
        for attr in self.attrs:

            # check attribute update frequency matches current thread definition
            if type(self).UPD_FREQ[attr['updFreq']] & freq == freq:

                # check update type - currently only modbus read, knx write is supported
                if attr['type'] == 'modbus2knx':
                    val = None

                    # retrieve value from modBus
                    try:
                        # check modbus data type - TODO currently only float is implemented
                        if attr['modbusFormat'] == 'float':
                            # configuration supports summing up multiple values automatically
                            # single value from corresponding modbus client
                            if isinstance(attr['modbusAddrDec'], int):
                                val = modbus_utils.ReadFloat(self.modbusClients[attr['modbusApplID']],
                                                             attr['modbusAddrDec'])
                            # sum of multiple values from corresponding modbus client
                            elif isinstance(attr['modbusAddrDec'], list):
                                val = 0
                                for ids in attr['modbusAddrDec']:
                                    val = val + modbus_utils.ReadFloat(self.modbusClients[attr['modbusApplID']],
                                                                       ids)
                    except Exception as ex:
                        print("ERROR: {0} Error reading ModBus value - {1}: {2}".format(datetime.now().strftime("%d.%b. %I:%M:%S"),
                                                                                        attr['name'],
                                                                                        ex))
                        val = None

                    if not (val is None):
                        dpt = 0
                        # convert to defined KNX data type - TODO implement different DPT target data types
                        if attr['knxFormat'] == 'DPT14':
                            dpt = knxd_util.IEEE754(val)[2]

                        # send value to the knx bus - TODO implement proper error handling
                        os.popen('knxtool groupwrite ip:{0} {1} {2}'.format(self.knxdIP,
                                                                            attr['knxAddr'],
                                                                            dpt))
                        if self.verbosity & type(self).VERBOSITY["info"] == type(self).VERBOSITY["info"]:
                            # log success
                            print('INFO: {0} Send to KNXD "{1}"[{2}](modbus={3}, knx={4})'.format(datetime.now().strftime("%d.%b. %I:%M:%S"),
                                                                                                  attr['name'],
                                                                                                  attr['knxAddr'],
                                                                                                  val,
                                                                                                  dpt))

        # initialize connection with modbus clients
        for mbc in self.modbusClients:
            # do not check for success, error will be given by requesting values
            mbc.close()

        # run periodically update of values - each update frequency initiating its own thread
        # initial run by main will initiate all threads at once
        ut = None
        if freq & type(self).UPD_FREQ['very high'] > 0:
            # VERY HIGH - runs every 10 seconds
            ut = Timer(10, gateway.update, (type(self).UPD_FREQ['very high'],))
            ut.start()
        if freq & type(self).UPD_FREQ['high'] > 0:
            # HIGH - runs every 60 seconds
            Timer(60, gateway.update, (type(self).UPD_FREQ['high'],)).start()
        if freq & type(self).UPD_FREQ['medium'] > 0:
            # MEDIUM - runs every 60 minutes
            Timer(3600, gateway.update, (type(self).UPD_FREQ['medium'],)).start()
        if freq & type(self).UPD_FREQ['low'] > 0:
            # LOW - runs every 24 hours
            Timer(86400, gateway.update, (type(self).UPD_FREQ['low'],)).start()

        # return reference to very high thread for synchronization
        return ut


if __name__ == '__main__':
    # initialize modbus2knxd gateway
    gateway = modbus2knxd()
    # initiate update process - update is self-iterating by starting various timer threads
    thread = gateway.update(type(gateway).UPD_FREQ['initial'])

    # keep on running... the update thread will run forever
    # https://blog.miguelgrinberg.com/post/how-to-make-python-wait
    thread.join()
