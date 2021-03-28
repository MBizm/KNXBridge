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

 - B{DPTXlatorScene}

Usage
=====

see L{DPTXlatorBoolean}

@author: Frédéric Mantegazza
@author: B. Malinowsky
@copyright: (C) 2013 Frédéric Mantegazza
@copyright: (C) 2013 B. Malinowsky
@license: GPL
"""

__revision__ = "$Id$"

import struct

from pknyx.services.logger import Logger
from pknyx.core.dptXlator.dptId import DPTID
from pknyx.core.dptXlator.dpt import DPT
from pknyx.core.dptXlator.dptXlatorBase import DPTXlatorBase, DPTXlatorValueError


class DPTXlatorScene(DPTXlatorBase):
    """ DPTXlator class for Scene (B1r1U6) KNX Datapoint Type

     - 1 Byte: CrUUUUUU
     - C: Control bit [0, 1]
     - U: Value [0:63]
     - r: reserved (0)

    .
    """
    DPT_Generic = DPT("17.xxx", "Generic", (0, 255))

    DPT_Date = DPT("17.001", "Scene", ((0, 0), (1, 63)))

    def __init__(self, dptId):
        super(DPTXlatorScene, self).__init__(dptId, 1)

    def checkData(self, data):
        if not 0x00 <= data <= 0xff:
            raise DPTXlatorValueError("data %s not in (0x00, 0xff)" % hex(data))

    def checkValue(self, value):
        for index in range(2):
            if not self._dpt.limits[0][index] <= value[index] <= self._dpt.limits[1][index]:
                raise DPTXlatorValueError("value not in range %r" % repr(self._dpt.limits))

    def dataToValue(self, data):
        ctrl = (data >> 7) & 0x01
        scene = data & 0x3f
        value = (ctrl, scene)
        #Logger().debug("DPTXlatorScene._toValue(): value=%d" % value)
        return value

    def valueToData(self, value):
        ctrl = value[0]
        scene = value[1]
        data = ctrl << 7 | scene
        #Logger().debug("DPTXlatorScene.valueToData(): data=%s" % hex(data))
        return data

    def dataToFrame(self, data):
        return bytearray(struct.pack(">B", data))

    def frameToData(self, frame):
        data = struct.unpack(">B", str(frame))[0]
        return data

    @property
    def ctrl(self):
        return self.value[0]

    @property
    def scene(self):
        return self.value[1]


if __name__ == '__main__':
    import unittest

    # Mute logger
    Logger().setLevel('error')

    class DPTSceneTestCase(unittest.TestCase):

        def setUp(self):
            self.testTable = (
                ((0,  0), 0x00, "\x00"),
                ((0,  1), 0x01, "\x01"),
                ((0, 63), 0x3f, "\x3f"),
                ((1,  0), 0x80, "\x80"),
                ((1,  1), 0x81, "\x81"),
                ((1, 63), 0xbf, "\xbf"),
            )
            self.dptXlator = DPTXlatorScene("17.001")

        def tearDown(self):
            pass

        #def test_constructor(self):
            #print self.dptXlator.handledDPT

        def test_typeSize(self):
            self.assertEqual(self.dptXlator.typeSize, 1)

        def testcheckValue(self):
            with self.assertRaises(DPTXlatorValueError):
                self.dptXlator.checkValue((-1, 0))
            with self.assertRaises(DPTXlatorValueError):
                self.dptXlator.checkValue((0, -1))

            with self.assertRaises(DPTXlatorValueError):
                self.dptXlator.checkValue((0, 64))
            with self.assertRaises(DPTXlatorValueError):
                self.dptXlator.checkValue((2, 0))

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
