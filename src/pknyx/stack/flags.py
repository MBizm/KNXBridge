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

Flags management

Implements
==========

 - B{FlagsValueError}
 - B{Flags}

Documentation
=============

L{Flags} class handles L{GroupObject<pknyx.core.groupObject>} bus behaviour.

Meaning of each flag, when set:
 - C - comm.:     the GroupObject interacts with the real KNX bus (even if not set, pKNyX communication remains)
 - R - read:      the GroupObject sends its associated Datapoint value on the bus when he receives a Read request on one of its bound GAD
 - W - write:     the GroupObject updates its associated Datapoint value if he receives a Write request on one of its bound GAD
 - T - tansmit:   the GroupObject sends its associated Datapoint value on the first bounded GAD when this value changes
 - U - update:    the GroupObject updates its associated Datapoint value if he receives a Response request on one of its bound GAD
 - I - init:      the GroupObject sends a Read request at startup
 - S - stateless: like T, but transmits its associated Datapoint value even if the value didn't changed (usefull for scenes)

Note: only one Datapoint per GAD should have its R flag set.

Flags in ETS:
 - en: S   C   R   W   T   U
 - fr: S   K   L   E   T   Act

Usage
=====

@author: Frédéric Mantegazza
@copyright: (C) 2013 Frédéric Mantegazza
@license: GPL
"""

__revision__ = "$Id$"

import re

from pknyx.common.exception import PKNyXValueError
from pknyx.services.logger import Logger


class FlagsValueError(PKNyXValueError):
    """
    """


class Flags(object):
    """ Flag class

    @ivar _raw: raw set of flags
    @type _raw: str
    """
    def __init__(self, raw="CRT"):
        """ Create a new set of flags

        @param raw: raw set of flags
        @type raw: str

        raise FlagsValueError: invalid flags

        @todo: allow +xx and -xx usage
        """
        super(Flags, self).__init__()

        try:
            if not re.match("^C?R?W?T?U?I?S?$", raw):
                raise FlagsValueError("invalid flags set (%r)" % repr(raw))
        except:
            Logger().exception("Flags.__init__()", debug=True)
            raise FlagsValueError("invalid flags set (%r)" % repr(raw))
        self._raw = raw

    def __repr__(self):
        return "<Flags('%s')>" % self._raw

    def __str__(self):
        return self._raw

    def __call__(self, value):
        return self.test(value)

    def test(self, value):
        """ Test if value matching flag is set

        @param value: flag(s) to test
        @type value: str

        @return: True if all value macthing flags are set
        @rtype: bool
        """
        for flag in value:
            if flag not in self._raw:
                return False

        return True

    @property
    def raw(self):
        return self._raw

    @property
    def communicate(self):
        return 'C' in self._raw

    @property
    def read(self):
        return 'R' in self._raw

    @property
    def write(self):
        return 'W' in self._raw

    @property
    def transmit(self):
        return 'T' in self._raw

    @property
    def update(self):
        return 'U' in self._raw

    @property
    def init(self):
        return 'I' in self._raw

    @property
    def stateless(self):
        return 'S' in self._raw


if __name__ == '__main__':
    import unittest

    # Mute logger
    Logger().setLevel('error')


    class DFlagsTestCase(unittest.TestCase):

        def setUp(self):
            self.flags = Flags("CRWTUIS")

        def tearDown(self):
            pass

        def test_display(self):
            print repr(self.flags)
            print self.flags

        def test_constructor(self):
            with self.assertRaises(FlagsValueError):
                Flags("A")
            with self.assertRaises(FlagsValueError):
                Flags("CWUT")
            with self.assertRaises(FlagsValueError):
                Flags("CCWUT")
            with self.assertRaises(FlagsValueError):
                Flags("CRWTUISA")

        def test_properties(self):
            self.assertEqual(self.flags.raw, "CRWTUIS")
            self.assertEqual(self.flags.communicate, True)
            self.assertEqual(self.flags.read, True)
            self.assertEqual(self.flags.write, True)
            self.assertEqual(self.flags.transmit, True)
            self.assertEqual(self.flags.update, True)
            self.assertEqual(self.flags.init, True)
            self.assertEqual(self.flags.stateless, True)

        def test_callable(self):
            self.assertFalse(self.flags("A"))
            self.assertFalse(self.flags("ABD"))
            self.assertTrue(self.flags("C"))
            self.assertTrue(self.flags("W"))
            self.assertTrue(self.flags("CRT"))
            self.assertTrue(self.flags("CRTWIUS"))

    unittest.main()
