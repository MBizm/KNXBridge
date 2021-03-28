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

Application layer group data management

Implements
==========

 - B{A_GroupDataService}

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
from pknyx.core.group import Group
from pknyx.core.groupMonitor import GroupMonitor
from pknyx.stack.groupAddress import GroupAddress
from pknyx.stack.layer7.apci import APCI
from pknyx.stack.layer7.apdu import APDU
from pknyx.stack.layer4.t_groupDataListener import T_GroupDataListener


class A_GDSValueError(PKNyXValueError):
    """
    """


class A_GroupDataService(T_GroupDataListener):
    """ A_GroupDataService class

    @ivar _tgds: transport group data service object
    @type _tgds: L{T_GroupDataService<pknyx.core.layer4.t_groupDataService>}

    @ivar _groups: Groups managed
    @type _groups: set of L{Group}
    """
    def __init__(self, tgds):
        """

        @param tgds: Transport group data service object
        @type tgds: L{T_GroupDataService<pknyx.core.layer4.t_groupDataService>}

        raise A_GDSValueError:
        """
        super(A_GroupDataService, self).__init__()

        self._tgds = tgds

        self._groups = {}

        tgds.setListener(self)

    def groupDataInd(self, src, gad, priority, aPDU):  # aPDU -> tSDU
        Logger().debug("A_GroupDataService.groupDataInd(): src=%s, gad=%s, priority=%s, aPDU=%s" % \
                       (src, gad, priority, repr(aPDU)))

        length = len(aPDU) - 2
        if length >= 0:
            apci = aPDU[0] << 8 | aPDU[1]

            group = self._groups.get(gad.address,None)
            if group is None:
                Logger().debug("A_GroupDataService.groupDataInd(): no registered group for that GAD (%s)" % repr(gad))

            groupMonitor = self._groups.get("0/0/0",None)

            if (apci & APCI._4) == APCI.GROUPVALUE_WRITE:
                data = APDU.getGroupValue(aPDU)
                if group is not None:
                    group.groupValueWriteInd(src, priority, data)
                if groupMonitor is not None:
                    groupMonitor.groupValueWriteInd(src, gad, priority, data)

            elif (apci & APCI._4) == APCI.GROUPVALUE_READ:
                if length == 0:
                    if group is not None:
                        group.groupValueReadInd(src, priority)
                    if groupMonitor is not None:
                        groupMonitor.groupValueReadInd(src, gad, priority)
                else:
                    Logger().warning("A_GroupDataService.groupDataInd(): invalid aPDU length")

            elif (apci & APCI._4) == APCI.GROUPVALUE_RES:
                data = APDU.getGroupValue(aPDU)
                if group is not None:
                    group.groupValueReadCon(src, priority, data)
                if groupMonitor is not None:
                    groupMonitor.groupValueReadCon(src, gad, priority, data)

        else:
            Logger().warning("A_GroupDataService.groupDataInd(): invalid aPDU length")

    @property
    def groups(self):
        return self._groups

    def subscribe(self, gad, listener):
        """ Subscribe listener to specified group address

        If a Group handling this group address already exists, it is used. If not, it is created.
        The listener is added as a listener to this group.

        If gad is null ("0/0/0"), a special group will be created, and the listener will receive all group telegrams.

        @param gad: Group address the listener wants to subscribe to
        @type gad : L{GroupAddress}

        @param listener: object to link to the GAD
        @type listener: L{GroupListener<pknyx.core.groupListener>} or L{GroupMonitorListener<pknyx.core.groupMonitorListener>}

        @return: group handling the group address
        @rtype: L{Group}
        """
        Logger().debug("A_GroupDataService.subscribe(): gad=%s, listener=%s" % (gad, repr(listener)))
        if not isinstance(gad, GroupAddress):
            gad = GroupAddress(gad)

        try:
            group = self._groups[gad.address]
        except KeyError:
            if gad.isNull:
                group = self._groups[gad.address] = GroupMonitor(self)
            else:
                group = self._groups[gad.address] = Group(gad, self)

        group.addListener(listener)

        return group

    def groupValueWriteReq(self, gad, priority, data, size):
        """
        """
        Logger().debug("A_GroupDataService.groupValueWriteReq(): gad=%s, priority=%s, data=%s, size=%d" % \
                       (gad, priority, repr(data), size))

        aPDU = APDU.makeGroupValue(APCI.GROUPVALUE_WRITE, data, size)
        return self._tgds.groupDataReq(gad, priority, aPDU)

    def groupValueReadReq(self, gad, priority):
        """
        """
        Logger().debug("A_GroupDataService.groupValueReadReq(): gad=%s, priority=%s" % \
                       (gad, priority))

        aPDU = APDU.makeGroupValue(APCI.GROUPVALUE_READ)
        return self._tgds.groupDataReq(gad, priority, aPDU)

    def groupValueReadRes(self, gad, priority, data, size):
        """
        """
        Logger().debug("A_GroupDataService.groupValueReadRes(): gad=%s, priority=%s, data=%s, size=%d" % \
                       (gad, priority, repr(data), size))

        aPDU = APDU.makeGroupValue(APCI.GROUPVALUE_RES, data, size)
        return self._tgds.groupDataReq(gad, priority, aPDU)


if __name__ == '__main__':
    import unittest

    # Mute logger
    Logger().setLevel('error')


    class A_GDSTestCase(unittest.TestCase):

        def setUp(self):
            pass

        def tearDown(self):
            pass

        def test_constructor(self):
            pass


    unittest.main()
