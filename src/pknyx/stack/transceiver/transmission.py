# -*- coding: utf-8 -*-

""" Python KNX payloadwork

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

Transceiver management

Implements
==========

 - B{Transmission}
 - B{TransmissionValueError}

Documentation
=============

Usage
=====

@author: Frédéric Mantegazza
@copyright: (C) 2013 Frédéric Mantegazza
@license: GPL
"""

__revision__ = "$Id$"

import threading

from pknyx.common.exception import PKNyXValueError
from pknyx.services.logger import Logger
from pknyx.stack.result import Result


class TransmissionValueError(PKNyXValueError):
    """
    """


class Transmission(object):
    """ Transmission class

    @ivar _payload:
    @type _payload: bytearray

    @ivar _waitConfirm:
    @type _waitConfirm: bool

    @ivar _result:
    @type _result: int
    """
    def __init__(self, payload, waitConfirm=True):
        """

        @param payload:
        @type payload: bytearray

        @param waitConfirm:
        @type waitConfirm: bool

        raise TransmissionValueError:
        """
        super(Transmission, self).__init__()

        self._payload = payload
        self._waitConfirm = waitConfirm
        self._result = Result.OK

        self._condition = threading.Condition()

    def __repr__(self):
        return "<Transmission(payload=%s, waitConfirm=%s, result=%d)>" % (repr(self._payload), self._waitConfirm, self._result)

    @property
    def payload(self):
        return self._payload

    @property
    def waitConfirm(self):
        return self._waitConfirm

    @waitConfirm.setter
    def waitConfirm(self, flag):
        self._waitConfirm = flag

    @property
    def result(self):
        return self._result

    @result.setter
    def result(self, code):
        if code not in Result.AVAILABLE_CODES:
            raise TransmissionValueError("invalid result code (%s)" % repr(code))

        self._result = code

    def acquire(self):
        self._condition.acquire()

    def release(self):
        self._condition.release()

    def wait(self):
        self._condition.wait()

    def notify(self):
        self._condition.notify()

    def notifyAll(self):
        self._condition.notifyAll()


if __name__ == '__main__':
    import unittest

    # Mute logger
    Logger().setLevel('error')


    class TransmissionTestCase(unittest.TestCase):

        def setUp(self):
            pass

        def tearDown(self):
            pass

        def test_constructor(self):
            pass


    unittest.main()
