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

 - B{DPTXlator3BitControl}

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
from pknyx.core.dptXlator.dpt import DPT
from pknyx.core.dptXlator.dptXlatorBoolean import DPTXlatorBoolean
from pknyx.core.dptXlator.dptXlatorBase import DPTXlatorBase, DPTXlatorValueError


class DPTXlator3BitControl(DPTXlatorBase):
    """ DPTXlator class for 3-Bit-Control (B1U3) KNX Datapoint Type

    This is a composite DPT.

     - 1 Byte: 0000CSSSS
     - C: Control bit [0, 1]
     - S: StepCode [0:7]

    The _data param of this DPT only handles the stepCode; the control bit is handled by the sub-DPT.

    @todo: create and use a DPTCompositeConverterBase?

    @ivar _dpt: sub-DPT
    @type _dpt: L{DPT}
    """
    DPT_Generic = DPT("3.xxx", "Generic", (-7, 7))

    DPT_Control_Dimming = DPT("3.007", "Dimming", (-7, 7))
    DPT_Control_Blinds = DPT("3.008", "Blinds", (-7, 7))

    def __init__(self, dptId):
        super(DPTXlator3BitControl, self).__init__(dptId, 0)

        mainId, subId = dptId.split('.')
        dptId_ = "1.%s" % subId
        self._dpt2 = DPTXlatorBoolean(dptId_)

    def checkData(self, data):
        if not 0x00 <= data <= 0x0f:
            raise DPTXlatorValueError("data %s not in (0x00, 0x0f)" % hex(data))

    def checkValue(self, value):
        if not self._dpt.limits[0] <= value <= self._dpt.limits[1]:
            raise DPTXlatorValueError("value %d not in range %r" % (value, repr(self._dpt.limits)))

    def dataToValue(self, data):
        ctrl = (data & 0x08) >> 3
        stepCode = data & 0x07
        value = stepCode if ctrl else -stepCode
        return value

    def valueToData(self, value):
        ctrl = 1 if value > 0 else 0
        stepCode = abs(value) & 0x07
        data = ctrl << 3 | stepCode
        return data

    # Add properties control and stepCode + helper methods (+ intervals?)

    def dataToFrame(self, data):
        return bytearray(struct.pack(">B", data))

    def frameToData(self, frame):

        # Note the usage of self.data, and not data!
        data = struct.unpack(">B", str(frame))[0]
        return data

    #def nbIntervalsToStepCode(self, nbIntervals):
        #""" Compute the stepCode for a given number of intervals

        #The number of intervals is rounded to the nearest intervals representable with a stepcode
        #(e.g 48 rounded of to 32, 3 rounded of to 2).

        #@todo: use property, and work on _data

        #@param nbIntervals: number of intervals to devide the 0-100% range
        #@type nbIntervals: int

        #@return: stepCode
        #@rtype: int
        #"""
        #if nbIntervals - 1 not in range(64):
            #raise ValueError("nbIntervals not in range (1, 64)");
        #stepCode = 7
        #thres = 0x30
        #while thres >= nbIntervals:
            #stepCode -= 1
            #thres >>= 1
        #return stepCode

    #def stepCodeToNbIntervals(self, stepCode):
        #""" Compute the number of intervals for a given stepCode

        #@todo: use property, and work on _data

        #@param stepCode: stepCode to use
        #@type stepCode: int

        #@return: number of intervals
        #@rtype: int
        #"""
        #return 1 << stepCode - 1


if __name__ == '__main__':
    import unittest

    # Mute logger
    Logger().setLevel('error')

    class DPT3BitControlTestCase(unittest.TestCase):

        def setUp(self):
            self.testTable = (
                ( 0, 0x00, '\x00'),
                ( 1, 0x09, '\x09'),
                (-1, 0x01, '\x01'),
                ( 7, 0x0f, '\x0f'),
                (-7, 0x07, '\x07'),
            )
            self.stepCodeIntervalTable = (
                (1,  1),
                (2,  2),
                (3,  4),
                (4,  8),
                (5, 16),
                (6, 32),
                (7, 64),
            )
            self.dptXlator = DPTXlator3BitControl("3.xxx")

        def tearDown(self):
            pass

        #def test_constructor(self):
            #print self.dptXlator.handledDPT

        def test_typeSize(self):
            self.assertEqual(self.dptXlator.typeSize, 0)

        def testcheckValue(self):
            with self.assertRaises(DPTXlatorValueError):
                self.dptXlator.checkValue(self.dptXlator.dpt.limits[1] + 1)

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

        #def test_nbIntervalsToStepCode(self):
            #for stepCode, nbIntervals in self.stepCodeIntervalTable:
                #nbIntervals_ = self.dptXlator.stepCodeToNbIntervals(stepCode)
                #self.assertEqual(nbIntervals_, nbIntervals, "Conversion failed (computed nbIntervals for stepCode %d is %d, should be %d)" %
                                 #(stepCode, nbIntervals_, nbIntervals))

        #def test_stepCodeToNbIntervals(self):
            #for stepCode, nbIntervals in self.stepCodeIntervalTable:
                #stepCode_ = self.dptXlator.nbIntervalsToStepCode(nbIntervals)
                #self.assertEqual(stepCode_, stepCode, "Conversion failed (computed stepCode for %d intervals is %d, should be %d)" %
                                 #(nbIntervals, stepCode_, stepCode))


    unittest.main()
