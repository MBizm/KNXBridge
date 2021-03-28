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

 - B{GroupMonitorValueError}
 - B{GroupMonitor}

Documentation
=============

A B{GroupMonitor} is a special L{Group<pknyx.core.group>} which handles all group addresses. Unlink normal
L{Group<pknyx.core.group>}, it can't send anything on the bus.

Usage
=====

@author: Frédéric Mantegazza
@copyright: (C) 2013 Frédéric Mantegazza
@license: GPL
"""

__revision__ = "$Id$"

from pknyx.common.exception import PKNyXValueError
from pknyx.services.logger import Logger
from pknyx.stack.layer7.a_groupDataListener import A_GroupDataListener


class GroupMonitorValueError(PKNyXValueError):
    """
    """


class GroupMonitor(A_GroupDataListener):
    """ GroupMonitor class

    This special group monitors all group adress. It can't send anything on the bus, only receive.

    @ivar _agds: Application Group Data Service object
    @type _agds: L{A_GroupDataService}

    @ivar _listeners: Listeners bound to the group handled GAD
    @type _listeners: set of L{GroupObject<pknyx.core.groupObject>}
    """
    def __init__(self, agds):
        """ Init the GroupMonitor object

        @param agds: Application Group Data Service object
        @type agds: L{GroupDataService}

        raise GroupValueError:
        """
        super(GroupMonitor, self).__init__()

        self._agds = agds

        self._listeners = set()

    def __repr__(self):
        return "<GroupMonitor()>" % self._gad

    def __str__(self):
        return "<GroupMonitor()>" % self._gad

    def groupValueWriteInd(self, src, gad, priority, data):
        Logger().debug("GroupMonitor.groupValueWriteInd(): src=%s, gad=%s, priority=%s, data=%s" % \
                       (src, gad, priority, repr(data)))
        for listener in self._listeners:
            try:
                listener.onWrite(src, gad, priority, data)
            except PKNyXValueError:
                Logger().exception("GroupMonitor.groupValueWriteInd()")

    def groupValueReadInd(self, src, gad, priority):
        Logger().debug("GroupMonitor.groupValueReadInd(): src=%s, gad=%s, priority=%s" % (src, gad, priority))
        for listener in self._listeners:
            try:
                listener.onRead(src, gad, priority)
            except PKNyXValueError:
                Logger().exception("GroupMonitor.groupValueReadInd()")

    def groupValueReadCon(self, src, gad, priority, data):
        Logger().debug("GroupMonitor.groupValueReadCon(): src=%s, gad=%s, priority=%s, data=%s" % \
                       (src, gad, priority, repr(data)))
        for listener in self._listeners:
            try:
                listener.onResponse(src, gad, priority, data)
            except PKNyXValueError:
                Logger().exception("GroupMonitor.groupValueReadCon()")

    @property
    def listeners(self):
        return self._listeners

    def addListener(self, listener):
        """ Add a listener to this group

        The given listener is added to the listeners bound with the GAD handled by this group.

        @param listener: Listener
        @type listener: L{GroupMonitorListener<pknyx.core.groupMonitorListener>}

        @todo: check listener type
        """
        self._listeners.add(listener)


if __name__ == '__main__':
    import unittest

    # Mute logger
    Logger().setLevel('error')


    class GroupMonitorTestCase(unittest.TestCase):

        def setUp(self):
            self.group = Group("1/1/1", None)

        def tearDown(self):
            pass

        def test_display(self):
            print repr(self.group)
            print self.group

        def test_constructor(self):
            pass


    unittest.main()
