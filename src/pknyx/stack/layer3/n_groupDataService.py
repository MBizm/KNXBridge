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

Network layer group data management

Implements
==========

 - B{N_GroupDataService}

Documentation
=============

Usage
=====

@author: Frédéric Mantegazza
@copyright: (C) 2013 Frédéric Mantegazza
@license: GPL
"""

__revision__ = "$Id$"

from pknyx.common.exception import PKNyXValueError
from pknyx.services.logger import Logger
from pknyx.stack.groupAddress import GroupAddress
from pknyx.stack.individualAddress import IndividualAddress
from pknyx.stack.layer2.l_dataListener import L_DataListener
from pknyx.stack.cemi.cemiLData import CEMILData, CEMIValueError


class N_GDSValueError(PKNyXValueError):
    """
    """


class N_GroupDataService(L_DataListener):
    """ N_GroupDataService class

    @ivar _lds: link data service object
    @type _lds: L{L_DataService<pknyx.core.layer2.l_dataService>}

    @ivar _ngdl: network group data listener
    @type _ngdl: L{N_GroupDataListener<pknyx.core.layer3.n_groupDataListener>}
    """
    def __init__(self, lds, hopCount=6):
        """

        @param lds: Link data service object
        @type lds: L{L_DataService<pknyx.core.layer2.l_dataService>}

        raise N_GDSValueError:
        """
        super(N_GroupDataService, self).__init__()

        self._lds = lds

        self._ngdl = None
        if not 0 < hopCount < 7:
            raise N_GDSValueError("invalid hopCount (%d)" % hopCount)
        self._hopCount = hopCount

        lds.setListener(self)

    def dataInd(self, cEMI):
        Logger().debug("N_GroupDataService.dataInd(): cEMI=%s" % repr(cEMI))

        if self._ngdl is None:
            Logger().warning("N_GroupDataService.dataInd(): not listener defined")
            return

        hopCount = cEMI.hopCount
        mc = cEMI.messageCode
        src = cEMI.sourceAddress
        dest = cEMI.destinationAddress
        priority = cEMI.priority
        hopCount = cEMI.hopCount
        nSDU = cEMI.npdu[1:]

        if isinstance(dest, GroupAddress):
            if not dest.isNull:
                self._ngdl.groupDataInd(src, dest, priority, nSDU)
            #else:
                #self._ngdl.broadcastInd(src, priority, hopCount, nSDU)
        #elif isinstance(dest, IndividualAddress):
            #self._ngdl.dataInd(src, priority, hopCount, nSDU)
        #else:
            #Logger().warning("N_GroupDataService.dataInd(): unknown destination address type (%s)" % repr(dest))
        else:
            Logger().warning("N_GroupDataService.dataInd(): unsupported destination address type (%s)" % repr(dest))

    def setListener(self, ngdl):
        """

        @param ngdl: listener to use to transmit data
        @type ngdl: L{N_GroupDataListener<pknyx.core.layer3.n_groupDataListener>}
        """
        self._ngdl = ngdl

    def groupDataReq(self, gad, priority, nSDU):
        """
        """
        Logger().debug("N_GroupDataService.groupDataReq(): gad=%s, priority=%s, nSDU=%s" % \
                       (gad, priority, repr(nSDU)))

        if gad.isNull:
            raise N_GDSValueError("invalid Group Address")

        cEMI = CEMILData()
        cEMI.messageCode = CEMILData.MC_LDATA_IND  # ???!!!??? Does not work with MC_LDATA_REQ!!!
        #cEMI.sourceAddress = src  # Added by Link Data Layer
        cEMI.destinationAddress = gad
        cEMI.priority = priority
        cEMI.hopCount = self._hopCount
        nPDU = bytearray(len(nSDU) + 1)
        nPDU[0] = len(nSDU) - 1
        nPDU[1:] = nSDU
        cEMI.npdu = nPDU

        return self._lds.dataReq(cEMI)


if __name__ == '__main__':
    import unittest

    # Mute logger
    Logger().setLevel('error')


    class N_GDSTestCase(unittest.TestCase):

        def setUp(self):
            pass

        def tearDown(self):
            pass

        def test_constructor(self):
            pass


    unittest.main()
