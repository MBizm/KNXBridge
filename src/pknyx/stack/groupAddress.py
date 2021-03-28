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

Group data service management

Implements
==========

 - B{GroupAddressValueError}
 - B{GroupAddress}

Documentation
=============


Usage
=====

>>> from groupAddress import GroupAddress
>>> groupAddr = GroupAddress(1)
GroupAddressValueError: invalid group address
>>> groupAddr = GroupAddress("32/8/256")
GroupAddressValueError: group address out of range
>>> groupAddr = GroupAddress("1/2/3")
>>> groupAddr
<GroupAddress("1/2/3")>
>>> groupAddr.raw
2563
>>> groupAddr.outFormatLevel
3
>>> groupAddr.address
'1/2/3'
>>> groupAddr.main
1
>>> groupAddr.middle
2
>>> groupAddr.sub
3
>>> groupAddr.outFormatLevel = 2
>>> groupAddr.address
'1/515'
>>> groupAddr.main
1
>>> groupAddr.middle
0
>>> groupAddr.sub
515
>>> groupAddr.outFormatLevel = 4
GroupAddressValueError: outFormatLevel 4 must be 2 or 3
>>> groupAddr.frame
'\n\x03'

@author: Frédéric Mantegazza
@copyright: (C) 2013 Frédéric Mantegazza
@license: GPL
"""

__revision__ = "$Id$"

from pknyx.common.exception import PKNyXValueError
from pknyx.services.logger import Logger
from pknyx.stack.knxAddress import KnxAddress, KnxAddressValueError


class GroupAddressValueError(KnxAddressValueError):
    """
    """


class GroupAddress(KnxAddress):
    """ Group address hanlding class

    @ivar _outFormatLevel: output format level representation, in (2, 3).
    @type _outFormatLevel: int
    """
    def __init__(self, address="0/0/0", outFormatLevel=3):
        """ Create a group address

        @param address: group address
        @type address: str or tuple of int

        @param outFormatLevel: output format level representation, in (2, 3)
                               Note that the format is only used for output; the address can always be entered as
                               level 2 or level 3, whatever the value of outFormatLevel is.
        @type outFormatLevel: int

        @raise GroupAddressValueError:

        @todo: add constructor with simple int
        """
        #Logger().debug("GroupAddress.__init__(): address=%s" % repr(address))

        if isinstance(address, str):
            address = address.strip().split('/')
            try:
                address = [int(val) for val in address]
            except ValueError:
                Logger().exception("GroupAddress.__init__()", debug=True)
                raise GroupAddressValueError("invalid group address")
        try:
            if len(address) == 2:
                if not 0 <= address[0] <= 0x1f or not 0 <= address[1] <= 0x7ff:
                    raise GroupAddressValueError("group address out of range")
                address = address[0] << 11 | address[1]
            elif len(address) == 3:
                if not 0 <= address[0] <= 0x1f or not 0 <= address[1] <= 0x7 or not 0 <= address[2] <= 0xff:
                    raise GroupAddressValueError("group address out of range")
                address = address[0] << 11 | address[1] << 8 | address[2]
            else:
                raise GroupAddressValueError("invalid group address")
        except TypeError:
            if not isinstance(address, int):
                Logger().exception("GroupAddress.__init__()", debug=True)
                raise GroupAddressValueError("invalid group address")

        if outFormatLevel not in (2, 3):
            raise GroupAddressValueError("outFormatLevel %d must be 2 or 3" % outFormatLevel)
        self._outFormatLevel = outFormatLevel

        super(GroupAddress, self).__init__(address)

    def __repr__(self):
        return "<GroupAddress('%s')>" % self.address

    def __str__(self):
        return self.address

    @property
    def address(self):
        address = []
        address.append("%d" % self.main)
        if self._outFormatLevel == 3:
            address.append("%d" % self.middle)
        address.append("%d" % self.sub)

        return '/'.join(address)

    @property
    def main(self):
        return self._raw >> 11 & 0x1f

    @property
    def middle(self):
        if self._outFormatLevel == 2:
            return 0
        elif self._outFormatLevel == 3:
            return self._raw >> 8 & 0x07

    @property
    def sub(self):
        if self._outFormatLevel == 2:
            return self._raw & 0x07ff
        elif self._outFormatLevel == 3:
            return self._raw & 0x0ff

    @property
    def outFormatLevel(self):
        return self._outFormatLevel

    @outFormatLevel.setter
    def outFormatLevel(self, level):
        if level not in (2, 3):
            raise GroupAddressValueError("outFormatLevel %d must be 2 or 3" % level)
        self._outFormatLevel = level


if __name__ == '__main__':
    import unittest

    # Mute logger
    Logger().setLevel('error')


    class GroupAddressTestCase(unittest.TestCase):

        def setUp(self):
            self.ad1 = GroupAddress("1/2/3")
            #print self.ad1
            self.ad2 = GroupAddress("1/2")
            self.ad3 = GroupAddress((1, 2, 3))
            self.ad4 = GroupAddress((1, 2))
            self.ad5 = GroupAddress(4321)

        def tearDown(self):
            pass

        def test_display(self):
            print repr(self.ad1)
            print self.ad3

        def test_constructor(self):
            #with self.assertRaises(GroupAddressValueError):
                #GroupAddress(0)
            with self.assertRaises(GroupAddressValueError):
                GroupAddress("0")
            with self.assertRaises(GroupAddressValueError):
                GroupAddress((0, 0, 0, 0))
            with self.assertRaises(GroupAddressValueError):
                GroupAddress("0/0/0/0")

            with self.assertRaises(GroupAddressValueError):
                GroupAddress((-1, 0, 0))
            with self.assertRaises(GroupAddressValueError):
                GroupAddress("-1/0/0")
            with self.assertRaises(GroupAddressValueError):
                GroupAddress((0, -1, 0))
            with self.assertRaises(GroupAddressValueError):
                GroupAddress("0/-1/0")
            with self.assertRaises(GroupAddressValueError):
                GroupAddress((0, 0, -1))
            with self.assertRaises(GroupAddressValueError):
                GroupAddress("0/0/-1")
            with self.assertRaises(GroupAddressValueError):
                GroupAddress((32, 0, 0))
            with self.assertRaises(GroupAddressValueError):
                GroupAddress("32/0/0")
            with self.assertRaises(GroupAddressValueError):
                GroupAddress((0, 8, 0))
            with self.assertRaises(GroupAddressValueError):
                GroupAddress("0/8/0")
            with self.assertRaises(GroupAddressValueError):
                GroupAddress((0, 0, 256))
            with self.assertRaises(GroupAddressValueError):
                GroupAddress("0/0/256")

            with self.assertRaises(GroupAddressValueError):
                GroupAddress((-1, 0))
            with self.assertRaises(GroupAddressValueError):
                GroupAddress("-1/0")
            with self.assertRaises(GroupAddressValueError):
                GroupAddress((0, -1))
            with self.assertRaises(GroupAddressValueError):
                GroupAddress("0/-1")
            with self.assertRaises(GroupAddressValueError):
                GroupAddress((32, 0))
            with self.assertRaises(GroupAddressValueError):
                GroupAddress("32/0")
            with self.assertRaises(GroupAddressValueError):
                GroupAddress((0, 2048))
            with self.assertRaises(GroupAddressValueError):
                GroupAddress("0/2048")

        def test_cmp(self):
            self.assertNotEqual(self.ad1, self.ad2)
            self.assertEqual(self.ad1, self.ad3)

        def test_address3(self):
            self.assertEqual(self.ad1.address, "1/2/3")
            self.assertEqual(self.ad2.address, "1/0/2")
            self.assertEqual(self.ad3.address, "1/2/3")
            self.assertEqual(self.ad4.address, "1/0/2")

        def test_address2(self):
            self.ad1.outFormatLevel = 2
            self.ad2.outFormatLevel = 2
            self.ad3.outFormatLevel = 2
            self.ad4.outFormatLevel = 2
            self.assertEqual(self.ad1.address, "1/515")
            self.assertEqual(self.ad2.address, "1/2")
            self.assertEqual(self.ad3.address, "1/515")
            self.assertEqual(self.ad4.address, "1/2")

        def test_main(self):
            self.assertEqual(self.ad1.main, 1)
            self.assertEqual(self.ad2.main, 1)
            self.assertEqual(self.ad3.main, 1)
            self.assertEqual(self.ad4.main, 1)

        def test_middle3(self):
            self.assertEqual(self.ad1.middle, 2)
            self.assertEqual(self.ad2.middle, 0)
            self.assertEqual(self.ad3.middle, 2)
            self.assertEqual(self.ad4.middle, 0)

        def test_middle2(self):
            self.ad1.outFormatLevel = 2
            self.ad2.outFormatLevel = 2
            self.ad3.outFormatLevel = 2
            self.ad4.outFormatLevel = 2
            self.assertEqual(self.ad1.middle, 0)
            self.assertEqual(self.ad2.middle, 0)
            self.assertEqual(self.ad3.middle, 0)
            self.assertEqual(self.ad4.middle, 0)

        def test_sub3(self):
            self.assertEqual(self.ad1.sub, 3)
            self.assertEqual(self.ad2.sub, 2)
            self.assertEqual(self.ad3.sub, 3)
            self.assertEqual(self.ad4.sub, 2)

        def test_sub2(self):
            self.ad1.outFormatLevel = 2
            self.ad2.outFormatLevel = 2
            self.ad3.outFormatLevel = 2
            self.ad4.outFormatLevel = 2
            self.assertEqual(self.ad1.sub, 515)
            self.assertEqual(self.ad2.sub, 2)
            self.assertEqual(self.ad3.sub, 515)
            self.assertEqual(self.ad4.sub, 2)

        def test_outFormatLevel(self):
            self.assertEqual(self.ad1.outFormatLevel, 3)
            with self.assertRaises(GroupAddressValueError):
                self.ad1.outFormatLevel = 1
            with self.assertRaises(GroupAddressValueError):
                self.ad1.outFormatLevel = 4


    unittest.main()
