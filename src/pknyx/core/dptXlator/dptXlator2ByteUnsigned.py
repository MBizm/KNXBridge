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

Datapoint Types management

Implements
==========

 - B{DPTXlator2ByteUnsigned}

Usage
=====

see L{DPTXlatorBoolean}

@author: Frédéric Mantegazza
@author: B. Malinowsky
@copyright: (C) 2013 Frédéric Mantegazza
@copyright: (C) 2006, 2011 B. Malinowsky
@license: GPL
"""

__revision__ = "$Id$"

import struct

from pknyx.services.logger import Logger
from pknyx.core.dptXlator.dptId import DPTID
from pknyx.core.dptXlator.dpt import DPT
from pknyx.core.dptXlator.dptXlatorBase import DPTXlatorBase, DPTXlatorValueError


class DPTXlator2ByteUnsigned(DPTXlatorBase):
    """ DPTXlator class for 2-Byte-Unsigned (U16) KNX Datapoint Type

      - 2 Byte Unsigned: UUUUUUUU UUUUUUUU
      - U: Bytes [0:65535]

    .
    """
    DPT_Generic = DPT("7.xxx", "Generic", (0, 65535))

    DPT_Value_2_Ucount = DPT("7.001", "Unsigned count", (0, 65535), "pulses")
    DPT_TimePeriodMsec = DPT("7.002", "Time period (resol. 1ms)", (0, 65535), "ms")
    DPT_TimePeriod10Msec = DPT("7.003", "Time period (resol. 10ms)", (0, 655350), "ms")
    DPT_TimePeriod100Msec = DPT("7.004", "Time period (resol. 100ms)", (0, 6553500), "ms")
    DPT_TimePeriodSec = DPT("7.005", "Time period (resol. 1s)", (0, 65535), "s")
    DPT_TimePeriodMin = DPT("7.006", "Time period (resol. 1min)", (0, 65535), "min")
    DPT_TimePeriodHrs = DPT("7.007", "Time period (resol. 1h)", (0, 65535), "h")
    DPT_PropDataType = DPT("7.010", "Interface object property ID", (0, 65535))
    DPT_Length_mm = DPT("7.011", "Length", (0, 65535), "mm")
    #DPT_UEICurrentmA = DPT("7.012", "Electrical current", (0, 65535), "mA")  # Add special meaning for 0 (create Limit object)
    DPT_Brightness = DPT("7.013", "Brightness", (0, 65535), "lx")

    def __init__(self, dptId):
        super(DPTXlator2ByteUnsigned, self).__init__(dptId, 2)

    def checkData(self, data):
        if not 0x0000 <= data <= 0xffff:
            raise DPTXlatorValueError("data %s not in (0x0000, 0xffff)" % hex(data))

    def checkValue(self, value):
        if not self._dpt.limits[0] <= value <= self._dpt.limits[1]:
            raise DPTXlatorValueError("Value not in range %r" % repr(self._dpt.limits))

    def dataToValue(self, data):
        if self._dpt is self.DPT_TimePeriod10Msec:
            value = data * 10.
        elif self._dpt is self.DPT_TimePeriod100Msec:
            value = data * 100.
        else:
            value = data
        #Logger().debug("DPTXlator2ByteUnsigned._toValue(): value=%d" % value)
        return value

    def valueToData(self, value):
        if self._dpt is self.DPT_TimePeriod10Msec:
            data = int(round(value / 10.))
        elif self._dpt is self.DPT_TimePeriod100Msec:
            data = int(round(value / 100.))
        else:
            data = value
        #Logger().debug("DPTXlator2ByteUnsigned.valueToData(): data=%s" % hex(data))
        return data

    def dataToFrame(self, data):
        return bytearray(struct.pack(">H", data))

    def frameToData(self, frame):
        data = struct.unpack(">H", str(frame))[0]
        return data


if __name__ == '__main__':
    import unittest

    # Mute logger
    Logger().setLevel('error')

    class DPT2ByteUnsignedTestCase(unittest.TestCase):

        def setUp(self):
            self.testTable = (
                (    0, 0x0000, "\x00\x00"),
                (    1, 0x0001, "\x00\x01"),
                (65535, 0xffff, "\xff\xff"),
            )
            self.dptXlator = DPTXlator2ByteUnsigned("7.xxx")

        def tearDown(self):
            pass

        #def test_constructor(self):
            #print self.dptXlator.handledDPT

        def test_typeSize(self):
            self.assertEqual(self.dptXlator.typeSize, 2)

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
