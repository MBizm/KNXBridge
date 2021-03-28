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

 - B{DPTXlatorString}

Usage
=====

see L{DPTXlatorBoolean}

Note
====

KNX century encoding is as following:

 - if byte year >= 90, then real year is 20th century year
 - if byte year is < 90, then real year is 21th century year

Python time module does not encode century the same way:

 - if byte year >= 69, then real year is 20th century year
 - if byte year is < 69, then real year is 21th century year

The DPTXlatorString class follows the python encoding.

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


class DPTXlatorString(DPTXlatorBase):
    """ DPTXlator class for String (A112) KNX Datapoint Type

     - 14 Byte: AAAAAAAA ... AAAAAAAA
     - A: Char [0:255]

    .
    """
    DPT_Generic = DPT("16.xxx", "Generic", (0, 5192296858534827628530496329220095))

    DPT_String_ASCII = DPT("16.000", "String", (14 * (0,), 14 * (127,)))
    DPT_String_8859_1 = DPT("16.001", "String", (14 * (0,), 14 * (255,)))

    def __init__(self, dptId):
        super(DPTXlatorString, self).__init__(dptId, 14)

    def checkData(self, data):
        if not 0x0000000000000000000000000000 <= data <= 0xffffffffffffffffffffffffffff:
            raise DPTXlatorValueError("data %s not in (0x0000000000000000000000000000, 0xffffffffffffffffffffffffffff)" % hex(data))

    def checkValue(self, value):
        for index in range(14):
            if not self._dpt.limits[0][index] <= value[index] <= self._dpt.limits[1][index]:
                raise DPTXlatorValueError("value not in range %r" % repr(self._dpt.limits))

    def dataToValue(self, data):
        value = tuple([int((data >> shift) & 0xff) for shift in range(104, -1, -8)])
        #Logger().debug("DPTXlatorString._toValue(): value=%d" % value)
        return value

    def valueToData(self, value):
        data = 0x00
        for shift in range(104, -1, -8):
            data |= value[13 - shift / 8] << shift
        #Logger().debug("DPTXlatorString.valueToData(): data=%s" % hex(data))
        return data

    def dataToFrame(self, data):
        return bytearray(struct.pack(">14B", *self.dataToValue(data)))

    def frameToData(self, frame):
        value = struct.unpack(">14B", str(frame))
        data = self.valueToData(value)
        return data

    @property
    def day(self):
        return self.value[0]

    @property
    def month(self):
        return self.value[1]

    @property
    def year(self):
        return self.value[2]


if __name__ == '__main__':
    import unittest

    # Mute logger
    Logger().setLevel('error')

    class DPTStringTestCase(unittest.TestCase):

        def setUp(self):
            self.testTable = (
                (14 * (0,),                                            0x0000000000000000000000000000, 14 * "\x00"),
                ((48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 0, 0, 0, 0), 0x3031323334353637383900000000, "0123456789\x00\x00\x00\x00"),
                (14 * (255,),                                          0xffffffffffffffffffffffffffff, 14 * "\xff"),
            )
            self.dptXlator = DPTXlatorString("16.001")

        def tearDown(self):
            pass

        #def test_constructor(self):
            #print self.dptXlator.handledDPT

        def test_typeSize(self):
            self.assertEqual(self.dptXlator.typeSize, 14)

        #def testcheckValue(self):
            #with self.assertRaises(DPTXlatorValueError):
                #self.dptXlator.checkValue((0, 1, 1969))

        def test_dataToValue(self):
            for value, data, frame in self.testTable:
                value_ = self.dptXlator.dataToValue(data)
                self.assertEqual(value_, value, "Conversion failed (converted value for %s is %s, should be %s)" %
                                 (hex(data), value_, value))

        def test_valueToData(self):
            for value, data, frame in self.testTable:
                data_ = self.dptXlator.valueToData(value)
                self.assertEqual(data_, data, "Conversion failed (converted data for %s is %s, should be %s)" %
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
