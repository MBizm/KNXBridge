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

 - B{CEMILData}

Documentation
=============

Usage
=====

>>> from cemiLData import CEMILData
>>> f = CEMILData(")\x00\xbc\xd0\x11\x0e\x19\x02\x01\x00\x80")

@author: Frédéric Mantegazza
@author: B. Malinowsky
@copyright: (C) 2013 Frédéric Mantegazza
@copyright: (C) 2006, 2011 B. Malinowsky
@license: GPL
"""

__revision__ = "$Id$"

from pknyx.common.exception import PKNyXValueError
from pknyx.services.logger import Logger
from pknyx.stack.cemi.cemi import CEMI, CEMIValueError
from pknyx.stack.cemi.cemiLDataFrame import CEMILDataFrame
from pknyx.stack.individualAddress import IndividualAddress, IndividualAddressValueError
from pknyx.stack.groupAddress import GroupAddress, GroupAddressValueError
from pknyx.stack.priority import Priority


class CEMILData(CEMI):
    """ cEMI L_Data message

    @ivar _frame: cEMI L_Data raw frame
    @type _frame: L{CEMILDataFrame}
    """
    MC_LDATA_REQ = 0x11  # message code for L-Data request
    MC_LDATA_CON = 0x2E  # message code for L-Data confirmation
    MC_LDATA_IND = 0x29  # message code for L-Data indication

    MESSAGE_CODES = (MC_LDATA_REQ,
                     MC_LDATA_CON,
                     MC_LDATA_IND
                    )

    FT_EXT_FRAME = 0
    FT_STD_FRAME = 1

    R_REPEAT = 0
    R_NO_REPEAT = 1

    SB_SYSTEM_BROADCAST = 0
    SB_BROADCAST = 1

    ACQ_DONT_CARE = 0
    ACK_REQUESTED = 1

    C_NO_ERROR = 0
    C_ERROR = 1

    AT_INDIVIDUAL_ADDRESS = 0
    AT_GROUP_ADDRESS = 1

    EFF_STD_FRAME = 0
    EFF_LTE_FRAME_MASK = 0x08

    def __init__(self, frame=None):
        """ Create a new cEMI L-Data message

        @param frame: raw frame
        @type frame: str or bytearray
        """
        super(CEMILData, self).__init__()

        self._frame = CEMILDataFrame(frame)

        if frame is not None:
            if self.messageCode not in CEMILData.MESSAGE_CODES:
                raise CEMIValueError("invalid Message Code (%d)" % mc)
            elif self._frame.addIL:
                raise CEMIValueError("Additional Informations not supported")
            elif self.frameType == CEMILData.FT_EXT_FRAME:
                raise CEMIValueError("only standard frame supported")
        else:
            self.frameType = CEMILData.FT_STD_FRAME

    def __repr__(self):
        s= "<CEMILData(mc=%s, priority=%s, src=%s, dest=%s, npdu=%s)>" % \
            (hex(self.messageCode), repr(self.priority), repr(self.sourceAddress), repr(self.destinationAddress), repr(self.npdu))
        return s

    def __str__(self):
        s= "<CEMILData(mc=%s, priority=%s, src=%s, dest=%s, npdu=%s)>" % \
            (hex(self.messageCode), self.priority, self.sourceAddress, self.destinationAddress, repr(self.npdu))
        return s

    @property
    def frame(self):
        return self._frame

    @property
    def messageCode(self):
        return self._frame.mc

    @messageCode.setter
    def messageCode(self, mc):
        if mc not in CEMILData.MESSAGE_CODES:
            raise("invalid Message Code (%d)" % mc)
        if mc == CEMILData.MC_LDATA_REQ:
            self.systemBroadcast = CEMILData.SB_BROADCAST
            self.confirm = CEMILData.C_NO_ERROR
            self.repeat = CEMILData.R_NO_REPEAT
        elif mc == CEMILData.MC_LDATA_CON:
            self.systemBroadcast = CEMILData.SB_BROADCAST
        elif mc == CEMILData.MC_LDATA_IND:
            self.systemBroadcast = CEMILData.SB_BROADCAST
            self.confirm = CEMILData.C_NO_ERROR
            self.repeat = CEMILData.R_NO_REPEAT
        self._frame.mc = mc

    @property
    def frameType(self):
        return (self._frame.ctrl1 >> 7) & 0x01

    @frameType.setter
    def frameType(self, ft):
        ctrl1 = self._frame.ctrl1 & 0x7f
        ctrl1 |= (ft & 0x01) << 7
        self._frame.ctrl1 = ctrl1

    @property
    def repeat(self):
        """ According to calimero:
        // ind: flag 0 = repeated frame, 1 = not repeated
        if (mc == MC_LDATA_IND)
            return (ctrl1 & 0x20) == 0;
        // req, (con): flag 0 = do not repeat, 1 = default behavior
        return (ctrl1 & 0x20) == 0x20;
        """
        return (self._frame.ctrl1 >> 5) & 0x01

    @repeat.setter
    def repeat(self, r):
        """ According to calimero:
        final boolean flag = mc == MC_LDATA_IND ? !repeat : repeat;
        """
        ctrl1 = self._frame.ctrl1 & 0xdf
        ctrl1 |= (r & 0x01) << 5
        self._frame.ctrl1 = ctrl1

    @property
    def systemBroadcast(self):
        return (self._frame.ctrl1 >> 4) & 0x01

    @systemBroadcast.setter
    def systemBroadcast(self, sb):
        #if sb != SB_SYSTEM_BROADCAST:
            #raise CEMIValueError("only System Broadcast supported")
        ctrl1 = self._frame.ctrl1 & 0xef
        ctrl1 |= (sb & 0x01) << 4
        self._frame.ctrl1 = ctrl1

    @property
    def priority(self):
        pr = (self._frame.ctrl1 >> 2) & 0x03
        return Priority(pr)

    @priority.setter
    def priority(self, pr):
        if isinstance(pr, Priority):
            pr = pr.level
        ctrl1 = self._frame.ctrl1 & 0xf3
        ctrl1 |= (pr & 0x03) << 2
        self._frame.ctrl1 = ctrl1

    @property
    def ack(self):
        return (self._frame.ctrl1 >> 1) & 0x01

    @ack.setter
    def ack(self, ack):
        ctrl1 = self._frame.ctrl1 & 0xfd
        ctrl1 |= (ack & 0x01) << 1
        self._frame.ctrl1 = ctrl1

    @property
    def confirm(self):
        return self._frame.ctrl1 & 0x01

    @confirm.setter
    def confirm(self, c):
        if c and self.mc == CEMILData.MC_LDATA_REQ:
            raise CEMIValueError("Confirm flag must be 0 for L_Data.req")
        ctrl1 = self._frame.ctrl1 & 0xfe
        ctrl1 |= c & 0x01
        self._frame.ctrl1 = ctrl1

    @property
    def addressType(self):
        return (self._frame.ctrl2 >> 7) & 0x01

    @addressType.setter
    def addressType(self, at):
        ctrl2 = self._frame.ctrl2 & 0x7f
        ctrl2 |= (at & 0x01) << 7
        self._frame.ctrl2 = ctrl2

    @property
    def hopCount(self):
        return (self._frame.ctrl2 >> 4) & 0x07

    @hopCount.setter
    def hopCount(self, hop):
        ctrl2 = self._frame.ctrl2 & 0x8f
        ctrl2 |= (hop & 0x07) << 4
        self._frame.ctrl2 = ctrl2

    @property
    def extFrameFormat(self):
        return self._frame.ctrl2 & 0x0f

    @extFrameFormat.setter
    def extFrameFormat(self, eff):
        ctrl2 = self._frame.ctrl2 & 0xf0
        ctrl2 |= eff & 0x0f
        self._frame.ctrl2 = ctrl2

    @property
    def sourceAddress(self):
        return IndividualAddress(self._frame.sa)

    @sourceAddress.setter
    def sourceAddress(self, sa):
        if not isinstance(sa, IndividualAddress):
            sa = IndividualAddress(sa)
        self._frame.sa = sa.raw

    @property
    def destinationAddress(self):
        if self.addressType == 0:
            da = IndividualAddress(self._frame.da)
        else:
            da = GroupAddress(self._frame.da)
        return da

    @destinationAddress.setter
    def destinationAddress(self, da):
        if isinstance(da, str):
            try:
                da = GroupAddress(da)
            except GroupAddressValueError:
                try:
                    da = IndividualAddress(da)
                except IndividualAddressValueError:
                    raise CEMIValueError("invalid address (%s)" % da)
        elif isinstance(da, int):
            da = IndividualAddress(da)

        if isinstance(da, IndividualAddress):
            self.addressType = CEMILData.AT_INDIVIDUAL_ADDRESS
        elif isinstance(da, GroupAddress):
            self.addressType = CEMILData.AT_GROUP_ADDRESS
        else:
            raise CEMIValueError("invalid address (%s)" % da)
        self._frame.da = da.raw

    @property
    def npdu(self):
        return self._frame.npdu

    @npdu.setter
    def npdu(self, npdu):
        self._frame.npdu = npdu

    @property
    def l(self):
        #return self._frame.l
        return self.npdu[0]

    #@l.setter
    #def l(self, l):
        #self._frame.l = l


if __name__ == '__main__':
    import unittest

    # Mute logger
    Logger().setLevel('error')


    class CEMILDataTestCase(unittest.TestCase):

        def setUp(self):
            self.frame1 = CEMILData()
            self.frame2 = CEMILData(")\x00\xbc\xd0\x11\x0e\x19\x02\x01\x00\x80")
            self.frame3 = CEMILData(")\x00\xbc\xd0\x11\x04\x10\x04\x03\x00\x80\x19,")

        def tearDown(self):
            pass

        def test_display(self):
            print repr(self.frame2)
            print self.frame3

        def test_constructor(self):
            with self.assertRaises(CEMIValueError):
                CEMILData(")\x03\xff\xff\xff\xbc\xd0\x11\x04\x10\x04\x03\x00\x80\x19,")  # ext frame


    unittest.main()
