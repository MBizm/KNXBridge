# -*- coding: utf-8 -*-

""" Python KNX framework

License
=======

 - B{pKNyX} (U{http://www.pknyx.org}) is Copyright:
  - (C) 2013 Frédéric Mantegazza

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
or see:

 - U{http://www.gnu.org/licenses/gpl.html}

Module purpose
==============

Datapoint Types management.

Implements
==========

 - B{DPTXlator8BitSigned}

Usage
=====

see L{DPTXlatorBoolean}

@author: Frédéric Mantegazza
@author: B. Malinowsky
@copyright: (C) 2013 Frédéric Mantegazza
@copyright: (C) 2006, 2012 B. Malinowsky
@license: GPL
"""

__revision__ = "$Id$"

import struct

from pknyx.services.logger import Logger
from pknyx.core.dptXlator.dptId import DPTID
from pknyx.core.dptXlator.dpt import DPT
from pknyx.core.dptXlator.dptXlatorBase import DPTXlatorBase, DPTXlatorValueError


def twos_comp(val, bits):
    """compute the 2's compliment of int value val"""
    if (val & (1 << (bits - 1))) != 0:
        val = val - (1 << bits)
    return val


class DPTXlator8BitSigned(DPTXlatorBase):
    """ DPTXlator class for 8-Bit-Signed (V8) KNX Datapoint Type

     - 1 Byte: VVVVVVVV
     - V: Byte [-128:127]

    .
    """
    DPT_Generic = DPT("6.xxx", "Generic", (-128, 127))

    DPT_Percent_V8 = DPT("6.001", "Percent (8 bit)", (-128, 127), "%")
    DPT_Value_1_Count = DPT("6.010", "Signed count", (-128, 127), "pulses")
    #DPT_Status_Mode3 = DPT("6.020", "Status mode 3", (, ))

    def __init__(self, dptId):
        super(DPTXlator8BitSigned, self).__init__(dptId, 1)

    def checkData(self, data):
        if not 0x00 <= data <= 0xff:
            raise DPTXlatorValueError("data %s not in (0x00, 0xff)" % hex(data))

    def checkValue(self, value):
        if not self._dpt.limits[0] <= value <= self._dpt.limits[1]:
            raise DPTXlatorValueError("value not in range %r" % repr(self._dpt.limits))

    def dataToValue(self, data):
        if data >= 0x80:
            value = -((data - 1) ^ 0xff)  # invert twos complement
        else:
            value = data
        #Logger().debug("DPTXlator8BitSigned._toValue(): value=%d" % value)
        return value

    def valueToData(self, value):
        if value < 0:
            value = (abs(value) ^ 0xff) + 1  # twos complement
        data = value
        #Logger().debug("DPTXlator8BitSigned.valueToData(): data=%s" % hex(data))
        return data

    def dataToFrame(self, data):
        return bytearray(struct.pack(">B", data))

    def frameToData(self, frame):
        data = struct.unpack(">B", str(frame))[0]
        return data


if __name__ == '__main__':
    import unittest

    # Mute logger
    Logger().setLevel('error')

    class DPT8BitSignedTestCase(unittest.TestCase):

        def setUp(self):
            self.testTable = (
                (-128, 0x80, "\x80"),
                (  -4, 0xfc, "\xfc"),
                (  -1, 0xff, "\xff"),
                (   0, 0x00, "\x00"),
                (   1, 0x01, "\x01"),
                ( 127, 0x7f, "\x7f"),
            )
            self.dptXlator = DPTXlator8BitSigned("6.xxx")

        def tearDown(self):
            pass

        #def test_constructor(self):
            #print self.dptXlator.handledDPT

        def test_typeSize(self):
            self.assertEqual(self.dptXlator.typeSize, 1)

        def testcheckValue(self):
            with self.assertRaises(DPTXlatorValueError):
                self.dptXlator.checkValue(self.dptXlator._dpt.limits[1] + 1)

        def test_dataToValue(self):
            for value, data, frame in self.testTable:
                value_ = self.dptXlator.dataToValue(data)
                self.assertEqual(value_, value, "Conversion failed (converted value for %s is %d, should be %d)" %
                                 (hex(data), value_, value))

        def test_valueToData(self):
            for value, data, frame in self.testTable:
                data_ = self.dptXlator.valueToData(value)
                self.assertEqual(data_, data, "Conversion failed (converted data for %d is %s, should be %s)" %
                                 (value, hex(data_), hex(data)))

        def test_dataToFrame(self):
            for value, data, frame in self.testTable:
                frame_ = self.dptXlator.dataToFrame(data)
                self.assertEqual(frame_, frame, "Conversion failed (converted frame for %s is %r, should be %r)" %
                                 (hex(data), frame_, frame))

        def test_frameToData(self):
            for value, data, frame in self.testTable:
                data_ = self.dptXlator.frameToData(frame)
                self.assertEqual(data_, data, "Conversion failed (converted data for %r is %s, should be %s)" %
                                 (frame, hex(data_), hex(data)))

    unittest.main()
