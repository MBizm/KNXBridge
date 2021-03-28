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

KNX Address management

Implements
==========

 - B{KnxAddressValueError}
 - B{KnxAddress}

Documentation
=============


Usage
=====

>>> from knxAddress import KnxAddress
>>> knxAddr = KnxAddress(-1)
KnxAddressValueError: address -0x1 not in range(0, 0xffff)
>>> knxAddr = KnxAddress(123)
>>> knxAddr
<KnxAddress(0x7b)>
>>> knxAddr.raw
123
>>> knxAddr.frame
'\x00{'


@author: Frédéric Mantegazza
@copyright: (C) 2013 Frédéric Mantegazza
@license: GPL
"""

__revision__ = "$Id$"

import struct

from pknyx.common.exception import PKNyXValueError
from pknyx.services.logger import Logger


class KnxAddressValueError(PKNyXValueError):
    """
    """


class KnxAddress(object):
    """ KNX address hanlding class

    @ivar _raw: knx raw address
    @type _raw: int
    @todo: use buffer protocole (bytearray)?
    """
    def __init__(self, raw=0x0000):
        """ Create a generic address

        @param raw: knx raw address
        @type raw: int or str (frame) -> switch to bytearray

        @raise KnxAddressValueError:
        """
        super(KnxAddress, self).__init__()

        #Logger().debug("KnxAddress.__init__(): raw=%r" % raw)

        if isinstance(raw, str) and len(raw) == 2:
            raw = struct.unpack(">H", raw)[0]
        if isinstance(raw, int):
            if not 0 <= raw <= 0xffff:
                raise KnxAddressValueError("address %s not in range(0, 0xffff)" % hex(raw))
        else:
            raise KnxAddressValueError("invalid address (%r)" % repr(raw))
        self._raw = raw

    def __repr__(self):
        return "<KnxAddress('%s')>" % hex(self._raw)

    def __cmp__(self, other):
        return cmp(self.raw, other.raw)

    @property
    def raw(self):
        return self._raw

    @property
    def low(self):
        return self._raw & 0xff

    @property
    def high(self):
        return (self._raw >> 8) & 0xff

    @property
    def address(self):
        raise NotImplementedError

    @property
    def frame(self):
        """ Return the address as frame
        """
        return struct.pack(">H", self._raw)

    @property
    def isNull(self):
        return self._raw == 0x0000


if __name__ == '__main__':
    import unittest

    # Mute logger
    Logger().setLevel('error')


    class KnxAddressTestCase(unittest.TestCase):

        def setUp(self):
            self.ad1 = KnxAddress(123)
            self.ad2 = KnxAddress("\x22\x31")
            self.ad3 = KnxAddress(123)

        def tearDown(self):
            pass

        def test_display(self):
            print repr(self.ad1)
            print self.ad2

        def test_constructor(self):
            with self.assertRaises(KnxAddressValueError):
                KnxAddress(-1)
            with self.assertRaises(KnxAddressValueError):
                KnxAddress(0x10000)
            with self.assertRaises(KnxAddressValueError):
                KnxAddress("\x00\x00\x00")

        def test_raw(self):
            self.assertEqual(self.ad2.raw, 8753)

        def test_lowhigh(self):
            self.assertEqual(self.ad2.low, 0x31)
            self.assertEqual(self.ad2.high, 0x22)

        def test_cmp(self):
            self.assertNotEqual(self.ad1, self.ad2)
            self.assertEqual(self.ad1, self.ad3)

        def test_frame(self):
            self.assertEqual(self.ad1.frame, "\x00\x7b")


    unittest.main()
