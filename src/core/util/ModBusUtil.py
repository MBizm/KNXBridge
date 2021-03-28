
# https://forum.fhem.de/index.php/topic,75638.msg987876.html?PHPSESSID=b17q82mhkt6bjj8s550cmgrdjr#msg987876
from pymodbus.constants import Endian
from pymodbus.payload import BinaryPayloadDecoder


class modbus_utils:
    """ Utility for number conversion from ModBus registers """

    def __init__(self):
        pass

    @staticmethod
    def ReadStr8(client, myadr_dec):
        """ Routine to read a string from one address with 8 registers  """
        r1 = client.read_holding_registers(myadr_dec, 8, unit=71)
        STRG8Register = BinaryPayloadDecoder.fromRegisters(r1.registers, byteorder=Endian.Big)
        result_STRG8Register = STRG8Register.decode_string(8)
        return result_STRG8Register

    @staticmethod
    def ReadFloat(client, myadr_dec):
        """ Routine to read a Float from one address with 2 registers """
        r1 = client.read_holding_registers(myadr_dec, 2, unit=71)
        FloatRegister = BinaryPayloadDecoder.fromRegisters(r1.registers, byteorder=Endian.Big, wordorder=Endian.Little)
        result_FloatRegister = round(FloatRegister.decode_32bit_float(), 2)
        return result_FloatRegister

    @staticmethod
    def ReadU16_1(client, myadr_dec):
        """ Routine to read a U16 from one address with 1 register """
        r1 = client.read_holding_registers(myadr_dec, 1, unit=71)
        U16register = BinaryPayloadDecoder.fromRegisters(r1.registers, byteorder=Endian.Big, wordorder=Endian.Little)
        result_U16register = U16register.decode_16bit_uint()
        return result_U16register

    @staticmethod
    def ReadU16_2(client, myadr_dec):
        """ Routine to read a U16 from one address with 2 registers  """
        r1 = client.read_holding_registers(myadr_dec, 2, unit=71)
        U16register = BinaryPayloadDecoder.fromRegisters(r1.registers, byteorder=Endian.Big, wordorder=Endian.Little)
        result_U16register = U16register.decode_16bit_uint()
        return result_U16register

    @staticmethod
    def ReadU32(client, myadr_dec):
        """ Routine to read a U32 from one address with 2 registers  """
        r1 = client.read_holding_registers(myadr_dec, 2, unit=71)
        U32register = BinaryPayloadDecoder.fromRegisters(r1.registers, byteorder=Endian.Big, wordorder=Endian.Little)
        result_U32register = U32register.decode_32bit_uint()
        return result_U32register

    @staticmethod
    def ReadS16(client, myadr_dec):
        """ Routine to read a U32 from one address with 2 registers  """
        r1 = client.read_holding_registers(myadr_dec, 1, unit=71)
        S16register = BinaryPayloadDecoder.fromRegisters(r1.registers, byteorder=Endian.Big, wordorder=Endian.Little)
        result_S16register = S16register.decode_16bit_uint()
        return result_S16register
