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

 - B{DPTIDValueError}
 - B{DPTID}

Usage
=====

>> from dptId import DPTID
>> dptId = DPTID("1")
ValueError: invalid Datapoint Type ID ('1')
>> dptId = DPTID("1.001")
>> dptId
<DPTID("1.001")>
>> dptId.id
'1.001'
>> dptId.main
'1'
>> dptId.sub
'001'
>> dptId.generic
<DPTID("1.xxx")>
>> dptId.generic.main
'1'
>> dptId.generic.sub
'xxx'
>> dptId.generic.generic
<DPTID("1.xxx")>

@author: Frédéric Mantegazza
@copyright: (C) 2013 Frédéric Mantegazza
@license: GPL
"""

__revision__ = "$Id$"

import re

from pknyx.common.exception import PKNyXValueError
from pknyx.services.logger import Logger


class DPTIDValueError(PKNyXValueError):
    """
    """


class DPTID(object):
    """ Datapoint Type ID class

    @ivar _id: Datapoint Type ID
    @type _id: str
    """
    def __init__(self, dptId="1.xxx"):
        """ Create a new Datapoint Type ID from the given id

        @param dptId: Datapoint Type ID to create
        @type dptId: str

        raise DPTIDValueError: invalid id
        """
        super(DPTID, self).__init__()

        try:
            if not re.match("^\d{1,3}\.\d{3}$", dptId) and not re.match("^\d{1,3}\.xxx$", dptId):
                raise DPTIDValueError("invalid Datapoint Type ID (%r)" % repr(dptId))
        except:
            Logger().exception("Flags.__init__()", debug=True)
            raise DPTIDValueError("invalid Datapoint Type ID (%r)" % repr(dptId))

        self._id = dptId

    def __repr__(self):
        return "<DPTID('%s')>" % self._id

    def __str__(self):
        return self._id

    def __lt__(self, other):
        return self._cmp(other) == -1

    def __le__(self, other):
        return self._cmp(other) in (-1, 0)

    def __eq__(self, other):
        return self._cmp(other) == 0

    def __ne__(self, other):
        return self._cmp(other) != 0

    def __gt__(self, other):
        return self._cmp(other) == 1

    def __ge__(self, other):
        return self._cmp(other) in (0, 1)

    def __hash__(self):
        return hash(self._id)

    def _cmp(self, other):
        """ Make comp on id

        @return: -1 if self < other, zero if self == other, +1 if self > other
        @rtype: int
        """
        if self.main != other.main:
            return DPTID.cmp(int(self.main), int(other.main))
        elif self.sub == other.sub:
            return 0
        elif self.sub == "xxx":
            return -1
        elif other.sub == "xxx":
            return 1
        else:
            return DPTID.cmp(self.sub, other.sub)

    # https://portingguide.readthedocs.io/en/latest/comparisons.html
    @staticmethod
    def cmp(x, y):
        return (x > y) - (x < y)

    @property
    def id(self):
        """ Return the Datapoint Type ID
        """
        return self._id

    @property
    def main(self):
        """ Return the main part of the Datapoint Type ID
        """
        return self._id.split('.')[0]

    @property
    def sub(self):
        """ Return the sub part of the Datapoint Type ID
        """
        return self._id.split('.')[1]

    @property
    def generic(self):
        """ Return the generic Datapoint Type ID
        """
        genericId = re.sub(r"^(.*)\..*$", r"\1.xxx",  self._id)
        return DPTID(genericId)

    def isGeneric(self):
        """ Test if generic ID

        @return: True if Datapoint Type ID is a generic Datapoint Type ID
        @rtype: bool
        """
        return self == self.generic


if __name__ == '__main__':
    import unittest

    # Mute logger
    Logger().setLevel('error')


    class DPTIDTestCase(unittest.TestCase):

        def setUp(self):
            self.dptId = DPTID("9.003")
            self.dptId1 = DPTID("1.xxx")
            self.dptId2 = DPTID("1.001")
            self.dptId3 = DPTID("3.xxx")
            self.dptId4 = DPTID("3.001")
            self.dptId5 = DPTID("9.xxx")
            self.dptId6 = DPTID("9.001")
            self.dptId7 = DPTID("9.001")

        def tearDown(self):
            pass

        def test_display(self):
            print(repr(self.dptId))
            print(self.dptId1)

        def test_constructor(self):
            with self.assertRaises(DPTIDValueError):
                DPTID("1.00")
            with self.assertRaises(DPTIDValueError):
                DPTID(".001")
            with self.assertRaises(DPTIDValueError):
                DPTID("001.0010")
            with self.assertRaises(DPTIDValueError):
                DPTID("0001.001")

        def test_cmp(self):
            dptIds = [self.dptId3, self.dptId6, self.dptId1, self.dptId2, self.dptId5, self.dptId4, self.dptId7]
            dptIds.sort()
            sortedDptIds = [self.dptId1, self.dptId2, self.dptId3, self.dptId4, self.dptId5, self.dptId6, self.dptId7]
            self.assertEqual(dptIds, sortedDptIds)

        def test_main(self):
            self.assertEqual(self.dptId.main, "9")

        def test_sub(self):
            self.assertEqual(self.dptId.sub, "003")

        def test_generic(self):
            self.assertEqual(self.dptId.generic, DPTID("9.xxx"))

        def test_isGeneric(self):
            self.assertEqual(self.dptId.isGeneric(), False)
            self.assertEqual(self.dptId1.isGeneric(), True)


    unittest.main()
