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

 - B{DPTXlator2ByteFloat}

Usage
=====

see L{DPTXlatorBoolean}

@todo: handle NaN

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


class DPTXlator2ByteFloat(DPTXlatorBase):
    """ DPTXlator class for 2-Byte-Float (F16) KNX Datapoint Type

     - 2 Byte Float: SEEEEMMM MMMMMMMM
     - S: Sign [0, 1]
     - E: Exponent [0:15]
     - M: Significand (Mantissa) [-2048:2047]

    For all Datapoint Types 9.xxx, the encoded value 7FFFh shall always be used to denote invalid data.
    """
    DPT_Generic = DPT("9.xxx", "Generic", (-671088.64, +670760.96))

    DPT_Value_Temp = DPT("9.001", "Temperature", (-273., +670760.), "°C")
    DPT_Value_Tempd = DPT("9.002", "Temperature difference", (-670760., +670760.), "K")
    DPT_Value_Tempa = DPT("9.003", "Temperature gradient", (-670760., +670760.), "K/h")
    DPT_Value_Lux = DPT("9.004", "Luminous emittance", (0., +670760.), "lx")
    DPT_Value_Wsp = DPT("9.005", "Wind speed", (0., +670760.), "m/s")
    DPT_Value_Pres = DPT("9.006", "Air pressure", (0., +670760.), "Pa")
    DPT_Value_Humidity = DPT("9.007", "Humidity", (0., +670760.), "%")
    DPT_Value_AirQuality = DPT("9.008", "Air quality", (0., +670760.), "ppm")
    DPT_Value_Time1 = DPT("9.010", "Time difference 1", (-670760., +670760.), "s")
    DPT_Value_Time2 = DPT("9.011", "Time difference 2", (-670760., +670760.), "ms")
    DPT_Value_Volt = DPT("9.020", "Electrical voltage", (-670760., +670760.), "mV")
    DPT_Value_Current = DPT("9.021", "Electric current", (-670760., +670760.), "mA")
    DPT_PowerDensity = DPT("9.022", "Power density", (-670760., +670760.), "W/m²")
    DPT_KelvinPerPercent = DPT("9.023", "Kelvin/percent", (-670760., +670760.), "K/%")
    DPT_Power = DPT("9.024", "Power", (-670760., +670760.), "kW")
    DPT_Value_Volume_Flow = DPT("9.025", "Volume flow", (-670760., 670760.), "l/h")
    DPT_Rain_Amount = DPT("9.026", "Rain amount", (-670760., 670760.), "l/m²")
    DPT_Value_Temp_F = DPT("9.027", "Temperature (°F)", (-459.6, 670760.), "°F")
    DPT_Value_Wsp_kmh = DPT("9.028", "Wind speed (km/h)", (0., 670760.), "km/h")

    def __init__(self, dptId):
        super(DPTXlator2ByteFloat, self).__init__(dptId, 2)

    def checkData(self, data):
        if not 0x0000 <= data <= 0xffff:
            raise DPTXlatorValueError("data %s not in (0x0000, 0xffff)" % hex(data))

    def checkValue(self, value):
        if not self._dpt.limits[0] <= value <= self._dpt.limits[1]:
            raise DPTXlatorValueError("Value not in range %r" % repr(self._dpt.limits))

    def dataToValue(self, data):
        sign = (data & 0x8000) >> 15
        exp = (data & 0x7800) >> 11
        mant = data & 0x07ff
        if sign != 0:
            mant = -(~(mant - 1) & 0x07ff)
        value = (1 << exp) * 0.01 * mant
        #Logger().debug("DPT2ByteFloat.dataToValue(): sign=%d, exp=%d, mant=%r" % (sign, exp, mant))
        #Logger().debug("DPT2ByteFloat.dataToValue(): value=%.2f" % value)
        return value

    def valueToData(self, value):
        sign = 0
        exp = 0
        if value < 0:
            sign = 1
        mant = int(value * 100)
        while not -2048 <= mant <= 2047:
            mant = mant >> 1
            exp += 1
        #Logger().debug("DPT2ByteFloat.valueToData(): sign=%d, exp=%d, mant=%r" % (sign, exp, mant))
        data = (sign << 15) | (exp << 11) | (int(mant) & 0x07ff)
        #Logger().debug("DPT2ByteFloat.valueToData(): data=%s" % hex(data))
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

    class DPTXlator2ByteFloatTestCase(unittest.TestCase):

        def setUp(self):
            self.testTable = (
                (     0.,   0x0000, "\x00\x00"),
                (     0.01, 0x0001, "\x00\x01"),
                (    -0.01, 0x87ff, "\x87\xff"),
                (    -1.,   0x879c, "\x87\x9c"),
                (     1.,   0x0064, "\x00\x64"),
                (  -272.96, 0xa156, "\xa1\x56"),
                (670760.96, 0x7fff, "\x7f\xff"),
            )
            self.dptXlator = DPTXlator2ByteFloat("9.xxx")

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
                self.assertEqual(value_, value, "Conversion failed (converted value for %s is %.2f, should be %.2f)" %
                                 (hex(data), value_, value))

        def test_valueToData(self):
            for value, data, frame in self.testTable:
                data_ = self.dptXlator.valueToData(value)
                self.assertEqual(data_, data, "Conversion failed (converted data for %.2f is %s, should be %s)" %
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
