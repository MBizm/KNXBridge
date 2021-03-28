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

 - B{DPTXlatorBoolean}

Usage
=====

>> from dptBoolean import DPTXlatorBoolean
>> dpt = DPTXlatorBoolean("1.001")
>> dpt.value
ValueError: data not initialized
>> dpt.data = 0x01
>> dpt.data
1
>> dpt.value
'On'
>> dpt.value = 'Off'
>> dpt.data
0
>> dpt.frame
'\x00'
>> dpt.data = 2
ValueError: data 0x2 not in (0x00, 0x01)
>> dpt.value = 3
ValueError: value 3 not in ("Off", "On")
>> dpt.handledDPT
[<DPTID("1.xxx")>, <DPTID("1.001")>, <DPTID("1.002")>, <DPTID("1.003")>, <DPTID("1.004")>, <DPTID("1.005")>,
<DPTID("1.006")>, <DPTID("1.007")>, <DPTID("1.008")>, <DPTID("1.009")>, <DPTID("1.010")>, <DPTID("1.011")>,
<DPTID("1.012")>, <DPTID("1.013")>, <DPTID("1.014")>, <DPTID("1.015")>, <DPTID("1.016")>, <DPTID("1.017")>,
<DPTID("1.018")>, <DPTID("1.019")>, <DPTID("1.021")>, <DPTID("1.022")>, <DPTID("1.023")>]

@author: Frédéric Mantegazza
@author: B. Malinowsky
@copyright: (C) 2013 Frédéric Mantegazza
@copyright: (C) 2006, 2011 B. Malinowsky
@license: GPL
"""

__revision__ = "$Id$"

import struct

from pknyx.services.logger import Logger
from pknyx.core.dptXlator.dpt import DPT
from pknyx.core.dptXlator.dptXlatorBase import DPTXlatorBase, DPTXlatorValueError


class DPTXlatorBoolean(DPTXlatorBase):
    """ DPTXlator class for 1-Bit (B1) KNX Datapoint Type

     - 1 Byte: 00000000B
     - B: Binary [0, 1]

    .
    """
    DPT_Generic = DPT("1.xxx", "Generic", (0, 1))

    DPT_Switch = DPT("1.001", "Switch", ("Off", "On"))
    DPT_Bool = DPT("1.002", "Boolean", (False, True))
    DPT_Enable = DPT("1.003", "Enable", ("Disable", "Enable"))
    DPT_Ramp = DPT("1.004", "Ramp", ("No ramp", "Ramp"))
    DPT_Alarm = DPT("1.005", "Alarm", ("No alarm", "Alarm"))
    DPT_BinaryValue = DPT("1.006", "Binary value", ("Low", "High"))
    DPT_Step = DPT("1.007", "Step", ("Decrease", "Increase"))
    DPT_UpDown = DPT("1.008", "Up/Down", ("Up", "Down"))
    DPT_OpenClose = DPT("1.009", "Open/Close", ("Open", "Close"))
    DPT_Start = DPT("1.010", "Start", ("Stop", "Start"))
    DPT_State = DPT("1.011", "State", ("Inactive", "Active"))
    DPT_Invert = DPT("1.012", "Invert", ("Not inverted", "Inverted"))
    DPT_DimSendStyle = DPT("1.013", "Dimmer send-style", ("Start/stop", "Cyclically"))
    DPT_InputSource = DPT("1.014", "Input source", ("Fixed", "Calculated"))
    DPT_Reset = DPT("1.015", "Reset", ("No action", "Reset"))
    DPT_Ack = DPT("1.016", "Acknowledge", ("No action", "Acknowledge"))
    DPT_Trigger = DPT("1.017", "Trigger", ("Trigger", "Trigger"))
    DPT_Occupancy = DPT("1.018", "Occupancy", ("Not occupied", "Occupied"))
    DPT_Window_Door = DPT("1.019", "Window/Door", ("Closed", "Open"))
    DPT_LogicalFunction = DPT("1.021", "Logical function", ("OR", "AND"))
    DPT_Scene_AB = DPT("1.022", "Scene A/B", ("Scene A", "Scene B"))
    DPT_ShutterBlinds_Mode = DPT("1.023", "Shutter/Blinds mode", ("Only move Up/Down", "Move Up/Down + StepStop"))

    def __init__(self, dptId):
        super(DPTXlatorBoolean, self).__init__(dptId, 0)

    def checkData(self, data):
        if data not in (0x00, 0x01):
            try:
                raise DPTXlatorValueError("data %s not in (0x00, 0x01)" % hex(data))
            except TypeError:
                raise DPTXlatorValueError("data not in (0x00, 0x01)")

    def checkValue(self, value):
        if value not in self._dpt.limits and value not in self.DPT_Generic.limits:
            raise DPTXlatorValueError("value %d not in %s" % (value, str(self._dpt.limits)))

    def dataToValue(self, data):
        value = self._dpt.limits[data]
        #Logger().debug("DPTXlatorBoolean.dataToValue(): value=%d" % value)
        return value

    def valueToData(self, value):
        #Logger().debug("DPTXlatorBoolean.valueToData(): value=%d" % value)
        self.checkValue(value)
        data = self._dpt.limits.index(value)
        #Logger().debug("DPTXlatorBoolean.valueToData(): data=%s" % hex(data))
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

    class DPTBooleanTestCase(unittest.TestCase):

        def setUp(self):
            self.testTable = (
                (0, 0x00, "\x00"),
                (1, 0x01, "\x01")
            )
            self.dptXlator = DPTXlatorBoolean("1.xxx")

        def tearDown(self):
            pass

        #def test_constructor(self):
            #print self.dptXlator.handledDPT

        def test_typeSize(self):
            self.assertEqual(self.dptXlator.typeSize, 0)

        def test_dpt(self):
            self.assertEqual(self.dptXlator.dpt, DPTXlatorBoolean.DPT_Generic)
            self.dptXlator.dpt = "1.001"
            self.assertEqual(self.dptXlator.dpt, DPTXlatorBoolean.DPT_Switch)

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
