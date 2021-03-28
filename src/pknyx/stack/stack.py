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

KNX Stack management

Implements
==========

 - B{Stack}
 - B{StackValueError}

Documentation
=============

Usage
=====

@author: Frédéric Mantegazza
@copyright: (C) 2013 Frédéric Mantegazza
@license: GPL
"""

__revision__ = "$Id$"

import time

from pknyx.common.exception import PKNyXValueError
from pknyx.services.logger import Logger
from pknyx.stack.individualAddress import IndividualAddress
from pknyx.stack.layer7.a_groupDataService import A_GroupDataService
from pknyx.stack.layer4.t_groupDataService import T_GroupDataService
from pknyx.stack.layer3.n_groupDataService import N_GroupDataService
from pknyx.stack.layer2.l_dataService import L_DataService
from pknyx.stack.transceiver.udpTransceiver import UDPTransceiver


class StackValueError(PKNyXValueError):
    """
    """


class Stack(object):
    """ Stack class

    @ivar _agds: Application layer Group Data Service object
    @type _agds: L{A_GroupDataService}

    @ivar _tgds: Transport layer Group Data Service object
    @type _tgds: L{T_GroupDataService}

    @ivar _ngds: Network layer Group Data Service object
    @type _ngds: L{N_GroupDataService}

    @ivar _lds: Transport layer Data Service object
    @type _lds: L{L_DataService}

    @ivar _tc: transciever
    @type _tc: L{Transceiver<pknyx.stack.transceiver.transceiver>}
    """
    PRIORITY_DISTRIBUTION = (-1, 3, 2)

    def __init__(self, individualAddress=IndividualAddress("0.0.0"),
                 transCls=UDPTransceiver, transParams=dict(mcastAddr="224.0.23.12", mcastPort=3671)):
        """

        raise StackValueError:
        """
        super(Stack, self).__init__()
        if not isinstance(individualAddress, IndividualAddress):
            individualAddress = IndividualAddress(individualAddress)

        self._lds = L_DataService(Stack.PRIORITY_DISTRIBUTION, individualAddress)
        self._tc = transCls(self._lds, **transParams)
        self._ngds = N_GroupDataService(self._lds)
        self._tgds = T_GroupDataService(self._ngds)
        self._agds = A_GroupDataService(self._tgds)

    @property
    def agds(self):
        return self._agds

    @property
    def individualAddress(self):
        return self._lds.individualAddress

    def start(self):
        """ Start the stack threads
        """
        Logger().trace("Stack.start()")

        self._lds.start()
        self._tc.start()

        time.sleep(0.25)
        Logger().debug("Stack.start(): running")

    def stop(self):
        """ Stop the stack threads
        """
        Logger().trace("Stack.stop()")

        self._tc.stop()
        self._lds.stop()
        self._tc.join()
        self._lds.join()

        Logger().debug("Stack.stop(): stopped")

    def mainLoop(self):
        """ Start the main loop

        Blocking.
        """
        self.start()
        try:
            while True:
                time.sleep(0.1)
        except KeyboardInterrupt:
            self.stop()


if __name__ == '__main__':
    import unittest

    # Mute logger
    Logger().setLevel('error')


    class StackTestCase(unittest.TestCase):

        def setUp(self):
            pass

        def tearDown(self):
            pass

        def test_constructor(self):
            pass


    unittest.main()
