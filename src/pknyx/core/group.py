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

 - B{GroupValueError}
 - B{Group}

Documentation
=============

A B{Group} is identified by its L{GroupAddress}. It contains all listeners bound to this GAD.
Whenever group data events occur, they are sent to Group, which then dispatch them to all listeners (Group Object).

Note that group data events may come from a real KNX bus or not.

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
from pknyx.stack.groupAddress import GroupAddress


class GroupValueError(PKNyXValueError):
    """
    """


class Group(A_GroupDataListener):
    """ Group class

    @ivar _gad: Group address (GAD) identifying this group
    @type _gad: L{GroupAddress}

    @ivar _agds: Application Group Data Service object
    @type _agds: L{A_GroupDataService}

    @ivar _listeners: Listeners bound to the group handled GAD
    @type _listeners: set of L{GroupObject<pknyx.core.groupObject>}
    """
    def __init__(self, gad, agds):
        """ Init the Group object

        @param gad: Group address identifying this group
        @type gad: L{GroupAddress}

        @param agds: Application Group Data Service object
        @type agds: L{GroupDataService}

        raise GroupValueError:
        """
        super(Group, self).__init__()

        if not isinstance(gad, GroupAddress):
            gad = GroupAddress(gad)
        self._gad = gad

        self._agds = agds

        self._listeners = set()

    def __repr__(self):
        return "<Group(gad='%s')>" % self._gad

    def __str__(self):
        return "<Group('%s')>" % self._gad

    def groupValueWriteInd(self, src, priority, data):
        Logger().debug("Group.groupValueWriteInd(): src=%s, priority=%s, data=%s" % (src, priority, repr(data)))
        for listener in self._listeners:
            try:
                listener.onWrite(src, data)
            except PKNyXValueError:
                Logger().exception("Group.groupValueWriteInd()")

    def groupValueReadInd(self, src, priority):
        Logger().debug("Group.groupValueReadInd(): src=%s, priority=%s" % (src, priority))
        for listener in self._listeners:
            try:
                listener.onRead(src)
            except PKNyXValueError:
                Logger().exception("Group.groupValueReadInd()")

    def groupValueReadCon(self, src, priority, data):
        Logger().debug("Group.groupValueReadCon(): src=%s, priority=%s, data=%s" % (src, priority, repr(data)))
        for listener in self._listeners:
            try:
                listener.onResponse(src, data)
            except PKNyXValueError:
                Logger().exception("Group.groupValueReadCon()")

    @property
    def gad(self):
        return self._gad

    @property
    def listeners(self):
        return self._listeners

    def addListener(self, listener):
        """ Add a listener to this group

        The given listener is added to the listeners bound with the GAD handled by this group.

        @param listener: Listener
        @type listener: L{GroupListener<pknyx.core.groupListener>}

        @todo: check listener type
        """
        self._listeners.add(listener)

    def write(self, priority, data, size):
        """ Write data request on the GAD associated with this group
        """
        self._agds.groupValueWriteReq(self._gad, priority, data, size)

    def read(self, priority):
        """ Read data request on the GAD associated with this group
        """
        self._agds.groupValueReadReq(self._gad, priority)

    def response(self, priority, data, size):
        """ Response data request on the GAD associated with this group
        """
        self._agds.groupValueReadRes(self._gad, priority, data, size)


if __name__ == '__main__':
    import unittest

    # Mute logger
    Logger().setLevel('error')


    class GroupTestCase(unittest.TestCase):

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
