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

cEMI message management

Implements
==========

 - B{CEMILDataFrame}
 - B{CEMILDataFrameValueError}

Documentation
=============

Structure of a cEMI L_Data raw frame:

 - Message code (MC): 1 byte
 - Additional Info Length (AddIL): 1 byte
 - Additional Information: 0 to n bytes (depending of AddIL)
 - Control field 1 (Ctrl1): 1 byte
 - Control field 2 (Ctrl2): 1 byte
 - Source address high/low (SAH/SAL): 2 bytes
 - Destination address high/low (DAH, DAL): 2 bytes
 - NPDU: 1 to n bytes. First byte is NPDU length

Usage
=====

>>> from cemiLDataFrame import CEMILDataFrame
>>> f = CEMILDataFrame(")\x00\xbc\xd0\x11\x0e\x19\x02\x01\x00\x80")
>>> f.raw
bytearray(b')\x00\xbc\xd0\x11\x0e\x19\x02\x01\x00\x80')
>>> f.mc
41
>>> f.addIL
0
>>> f.addInfo
>>> f.ctrl1
188
>>> f.ctrl2
208
>>> f.sa
4366
>>> f.da
6402

@author: Frédéric Mantegazza
@copyright: (C) 2013 Frédéric Mantegazza
@license: GPL
"""

__revision__ = "$Id$"

import struct

from pknyx.services.logger import Logger
from pknyx.stack.cemi.cemi import CEMIValueError


class CEMILDataFrame(object):
    """ cEMI L_Data Raw Frame container

    @ivar _raw: raw frame
    @type _raw: bytearray
    """
    BASIC_LENGTH = 9

    def __init__(self, frame=None, addIL=0):
        """ Init frame

        @param frame: raw frame
        @type frame: str or bytearray

        @param addIL: additional info length
        @type addIL: int
        """
        super(CEMILDataFrame, self).__init__()

        if frame is not None:
            if addIL:
                raise CEMIValueError("can't give both frame and addIL args")
            elif len(frame) < CEMILDataFrame.BASIC_LENGTH:
                raise CEMIValueError("data too short (%d)" % len(frame))
            self._raw = bytearray(frame)
        else:
            self._raw = bytearray(CEMILDataFrame.BASIC_LENGTH+addIL)
            self._raw[1] = addIL

    def __repr__(self):
        return "<CEMILDataFrame(mc=%s, addIL=%d, ctrl1=%s, ctrl2=%s, src=%s, dest=%s)>" % (hex(self.mc), self.addIL, hex(self.ctrl1), hex(self.ctrl2), hex(self.sa), hex(self.da))

    def __str__(self):
        return repr(str(self._raw))

    @property
    def raw(self):
        return self._raw

    @property
    def mc(self):
        return self._raw[0]

    @mc.setter
    def mc(self, mc):
        self._raw[0] = mc & 0xff

    @property
    def addIL(self):
        return self._raw[1]

    # Must be set at frame creation
    #@addIL.setter
    #def addIL(self, addIL):
        #self._raw[1] = addIL & 0xff

    @property
    def addInfo(self):
        if self.addIL:
            return self._raw[2:2+self.addIL]
        else:
            return None

    @addInfo.setter
    def addInfo(self, addInfo):
        if not self.addIL or self.addIL != len(addInfo):
            raise CEMIValueError("incompatible addIL value (%d)" % self.addIL)
        self._raw[2:2+self.addIL] = addInfo

    @property
    def ctrl1(self):
        return self._raw[2+self.addIL]

    @ctrl1.setter
    def ctrl1(self, ctrl1):
        self._raw[2+self.addIL] = ctrl1

    @property
    def ctrl2(self):
        return self._raw[3+self.addIL]

    @ctrl2.setter
    def ctrl2(self, ctrl2):
        self._raw[3+self.addIL] = ctrl2

    @property
    def sah(self):
        return self._raw[4+self.addIL]

    @sah.setter
    def sah(self, sah):
        self._raw[4+self.addIL] = sah

    @property
    def sal(self):
        return self._raw[5+self.addIL]

    @sal.setter
    def sal(self, sal):
        self._raw[5+self.addIL] = sal

    @property
    def sa(self):
        b = self._raw[4+self.addIL:6+self.addIL]
        return struct.unpack(">H", str(b))[0]

    @sa.setter
    def sa(self, sa):
        if isinstance(sa, int):
            self.sah = (sa >> 8) & 0xff  # use struct.pack!!!
            self.sal = sa & 0xff
        else:
            self._raw[4+self.addIL:6+self.addIL] = sa

    @property
    def dah(self):
        return self._raw[6+self.addIL]

    @dah.setter
    def dah(self, dah):
        self._raw[6+self.addIL] = dah

    @property
    def dal(self):
        return self._raw[7+self.addIL]

    @dal.setter
    def dal(self, dal):
        self._raw[7+self.addIL] = dal

    @property
    def da(self):
        b = self._raw[6+self.addIL:8+self.addIL]
        return struct.unpack(">H", str(b))[0]

    @da.setter
    def da(self, da):
        if isinstance(da, int):
            self.dah = (da >> 8) & 0xff  # use struct.pack!!!
            self.dal = da & 0xff
        else:
            self._raw[6+self.addIL:8+self.addIL] = da

    @property
    def npdu(self):
        return self._raw[8+self.addIL:]

    @npdu.setter
    def npdu(self, npdu):
        self._raw[8+self.addIL:] = npdu

    #@property
    #def l(self):
        #return self._raw[8]

    ##@l.setter
    ##def l(self, l):
        ##self._raw[8] = l


if __name__ == '__main__':
    import unittest

    # Mute logger
    Logger().setLevel('error')


    class CEMILDataFrameTestCase(unittest.TestCase):

        def setUp(self):
            self.frame1 = CEMILDataFrame()
            self.frame2 = CEMILDataFrame(")\x00\xbc\xd0\x11\x0e\x19\x02\x01\x00\x80")
            self.frame3 = CEMILDataFrame(")\x00\xbc\xd0\x11\x04\x10\x04\x03\x00\x80\x19,")
            self.frame4 = CEMILDataFrame(addIL=2)
            self.frame5 = CEMILDataFrame(")\x03\xff\xff\xff\xbc\xd0\x11\x04\x10\x04\x03\x00\x80\x19,")  # ext frame

        def tearDown(self):
            pass

        def test_display(self):
            print repr(self.frame2)
            print self.frame3

        def test_constructor(self):
            with self.assertRaises(CEMIValueError):
                CEMILDataFrame(frame=bytearray(10), addIL=1)  # too much args
            with self.assertRaises(CEMIValueError):
                CEMILDataFrame(frame=bytearray(5))  # frame too short

        def test_raw(self):
            self.assertEqual(self.frame1.raw, bytearray(9))
            self.assertEqual(self.frame2.raw, ")\x00\xbc\xd0\x11\x0e\x19\x02\x01\x00\x80")

        def test_mc(self):
            self.assertEqual(self.frame1.mc, 0)
            self.frame1.mc = 1
            self.assertEqual(self.frame1.mc, 1)
            self.assertEqual(self.frame2.mc, 0x29)

        def test_addIL(self):
            self.assertEqual(self.frame1.addIL, 0)
            with self.assertRaises(AttributeError):
                self.frame1.addIL = 1
            self.assertEqual(self.frame2.addIL, 0)
            self.assertEqual(self.frame4.addIL, 2)
            self.assertEqual(self.frame5.addIL, 3)

        def test_addInfo(self):
            self.assertEqual(self.frame1.addInfo, None)
            with self.assertRaises(CEMIValueError):
                self.frame2.addInfo = '\x00'
            self.assertEqual(self.frame2.addInfo, None)
            self.assertEqual(self.frame4.addInfo, '\x00\x00')
            with self.assertRaises(CEMIValueError):
                self.frame4.addInfo = '\x00'  # not enough values
            self.frame4.addInfo = '\xff\xff'
            self.assertEqual(self.frame4.addInfo, '\xff\xff')
            self.assertEqual(self.frame5.addInfo, '\xff\xff\xff')
            self.frame5.addInfo = '\x00\x00\x00'
            self.assertEqual(self.frame5.addInfo, '\x00\x00\x00')

        def test_ctrl1(self):
            self.assertEqual(self.frame1.ctrl1, 0)
            self.frame1.ctrl1 = 0xff
            self.assertEqual(self.frame1.ctrl1, 0xff)
            self.assertEqual(self.frame2.ctrl1, 0xbc)

        def test_ctrl2(self):
            self.assertEqual(self.frame1.ctrl2, 0)
            self.frame1.ctrl2 = 0xff
            self.assertEqual(self.frame1.ctrl2, 0xff)
            self.assertEqual(self.frame2.ctrl2, 0xd0)

        def test_sah(self):
            self.assertEqual(self.frame1.sah, 0)
            self.frame1.sah = 1
            self.assertEqual(self.frame1.sah, 1)
            self.assertEqual(self.frame2.sah, 17)

        def test_sal(self):
            self.assertEqual(self.frame1.sal, 0)
            self.frame1.sal = 1
            self.assertEqual(self.frame1.sal, 1)
            self.assertEqual(self.frame2.sal, 14)

        def test_sa(self):
            self.assertEqual(self.frame1.sa, 0)
            self.frame1.sa = 1000
            self.assertEqual(self.frame1.sa, 1000)
            self.assertEqual(self.frame2.sa, 4366)

        def test_dah(self):
            self.assertEqual(self.frame1.dah, 0)
            self.frame1.dah = 1
            self.assertEqual(self.frame1.dah, 1)
            self.assertEqual(self.frame2.dah, 25)

        def test_dal(self):
            self.assertEqual(self.frame1.dal, 0)
            self.frame1.dal = 1
            self.assertEqual(self.frame1.dal, 1)
            self.assertEqual(self.frame2.dal, 2)

        def test_da(self):
            self.assertEqual(self.frame1.da, 0)
            self.frame1.sa = 2000
            self.assertEqual(self.frame1.sa, 2000)
            self.assertEqual(self.frame2.da, 6402)

        def test_npdu(self):
            self.assertEqual(self.frame1.npdu, '\x00')
            self.frame1.npdu = '\xff\xff'
            self.assertEqual(self.frame1.npdu, '\xff\xff')
            self.assertEqual(self.frame2.npdu, '\x01\x00\x80')
            self.assertEqual(self.frame3.npdu, '\x03\x00\x80\x19,')

    unittest.main()
