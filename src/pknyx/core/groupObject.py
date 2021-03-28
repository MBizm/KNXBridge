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

 - B{GroupObject}

Documentation
=============

B{GroupObject} are used by L{Datapoint<pknyx.core.datapoint>} to communicate over the bus using group data service.

Usage
=====

@author: Frédéric Mantegazza
@copyright: (C) 2013 Frédéric Mantegazza
@license: GPL
"""

__revision__ = "$Id$"

from pknyx.common.exception import PKNyXValueError
from pknyx.services.logger import Logger
from pknyx.core.groupListener import GroupListener
from pknyx.stack.flags import Flags
from pknyx.stack.priority import Priority


class GroupObjectValueError(PKNyXValueError):
    """
    """


class GroupObject(GroupListener):
    """ GroupObject class

    @ivar _datapoint: associated datapoint
    @type _datapoint: L{Datapoint<pknyx.core.datapoint>}

    @ivar _flags: bus message flags
    @type _flags: str or L{Flags}

    @ivar _priority: bus message priority
    @type _priority: str or L{Priority}

    @ivar _group: group to use to communicate on the bus
    @type _group: L{Group<pknyx.core.group>}

    @todo: take 'access' into account when managing flags
    @todo: add lock for user
    """
    def __init__(self, datapoint, flags=Flags(), priority=Priority()):
        """

        @param datapoint: associated datapoint
        @type datapoint: L{Datapoint<pknyx.core.datapoint>}

        @param flags: bus message flags
        @type flags: str or L{Flags}

        @param priority: bus message priority
        @type priority: str or L{Priority}

        raise GroupObjectValueError:
        """
        super(GroupObject, self).__init__()

        self._datapoint = datapoint
        if not isinstance(flags, Flags):
            flags = Flags(flags)
        self._flags = flags
        if not isinstance(priority, Priority):
            priority = Priority(priority)
        self._priority = priority

        self._group = None

        # Connect signals
        datapoint.signalChanged.connect(self._slotChanged)

    def __repr__(self):
        return "<GroupObject(dp='%s', flags='%s', priority='%s')>" % (self.name, self._flags, self._priority)

    def __str__(self):
        return "<GroupObject('%s')>" % self.name

    def _slotChanged(self, oldValue, newValue):
        """ Slot handling a changing value of the associated datapoint.

        @param oldValue: old value of the datapoint
        @type oldValue: depends on the datapoint DPT

        @param newValue: new value of the datapoint
        @type newValue: depends on the datapoint DPT

        @todo: transmit a more generic object, like SignalEvent?
        """
        Logger().debug("GroupObject._slotChanged(): dp=%s, oldValue=%s, newValue=%s" % (self._datapoint.name, repr(oldValue), repr(newValue)))

        if self._flags.communicate:
            if (oldValue != newValue and self._flags.transmit) or self._flags.stateless:
                frame, size = self._datapoint.frame
                self._group.write(self._priority, frame, size)
        # @todo: add a param to set refresh max delay

    @property
    def datapoint(self):
        return self._datapoint

    @property
    def flags(self):
        return self._flags

    @flags.setter
    def flags(self, flags):
        if not isinstance(flags, Flags):
            flags = Flags(flags)
        self._flags = flags

    @property
    def priority(self):
        return self._priority

    @priority.setter
    def priority(str, level):
        if not isinstance(priority, Priority):
            priority = Priority(priority)
        self._priority = priority

    @property
    def group(self):
        return self._group

    @group.setter
    def group(self, group):
        self._group = group

        # If the flag init is set, send a read request on that accesspoint, which is bound to the default GAD
        # Does not work, as stck is not yet running!!!!!!
        # Must be done *after* starting it...
        #if self._flags.communicate:
            #if self._flags.init:
                #self._group.read(self._priority)

    @property
    def name(self):
        return self._datapoint.name

    def onWrite(self, src, data):
        Logger().debug("GroupObject.onWrite(): src=%s, data=%s" % (src, repr(data)))

        # Check if datapoint should be updated
        if self._flags.write:  # and data != self.datapoint.data:
            self.datapoint.frame = data

    def onRead(self, src):
        Logger().debug("GroupObject.onRead(): src=%s" % src)

        # Check if data should be send over the bus
        if self._flags.communicate:
            if self._flags.read:
                frame, size = self._datapoint.frame
                self._group.response(self._priority, frame, size)

    def onResponse(self, src, data):
        Logger().debug("GroupObject.onResponse(): src=%s, data=%s" % (src, repr(data)))

        # Check if datapoint should be updated
        if self._flags.update:  # and data != self.datapoint.data:
            self.datapoint.frame = data


if __name__ == '__main__':
    import unittest

    # Mute logger
    Logger().setLevel('error')


    class GroupObjectTestCase(unittest.TestCase):

        def setUp(self):
            pass

        def tearDown(self):
            pass

        def test_constructor(self):
            pass


    unittest.main()


