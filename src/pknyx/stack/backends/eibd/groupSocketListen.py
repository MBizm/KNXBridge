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

KNX Bus access

Implements
==========

 - B{GroupSocketListen}

@author: Frédéric Mantegazza
@copyright: (C) 2013 Frédéric Mantegazza
@license: GPL
"""
__revision__ = "$Id$"

import os
import sys

from pknyx.services.logger import Logger
from pknyx.stack.backends.eibd.eibConnection import EIBConnection, EIBBuffer, EIBAddr


class EIBAddress(EIBAddr):
    def toGroup(self):
        return "%d/%d/%d" % ((self.data >> 11) & 0x1f, (self.data >> 8) & 0x07, (self.data) & 0xff)

    def toIndividual(self):
        return "%d.%d.%d" % ((self.data >> 12) & 0x0f, (self.data >> 8) & 0x0f, (self.data) & 0xff)


class GroupSocketListen(object):
    """
    """
    def __init__(self, url, callback):
        """
        """
        super(GroupSocketListen, self).__init__()

        self._connection = EIBConnection()
        err = self._connection.EIBSocketURL(url)
        if err:
            Logger().critical("GroupsSocketListen.__init__(): %s" % os.strerror(self._connection.errno))
            Logger().critical("GroupsSocketListen.__init__(): call to EIBConnection.EIBSocketURL() failed (err=%d)" % err)
            sys.exit(-1)
        Logger().info("EIB socket successufully opened")
        self._url = url
        self._callback = callback

        self._src = EIBAddress()
        self._dest = EIBAddress()
        self._buffer = EIBBuffer()

    def run(self):
        """
        """
        err = self._connection.EIBOpen_GroupSocket(write_only=0)
        Logger().info("EIB group socket successfully opened")
        if err:
            Logger().critical("GroupsSocketListen.run(): %s" % os.strerror(self._connection.errno))
            Logger().critical("GroupsSocketListen.run(): call to EIBConnection.EIBOpen_GroupSocket() failed (err=%d)" % err)
            sys.exit(-1)
        while True:
            length = self._connection.EIBGetGroup_Src(self._buffer, self._src, self._dest)
            if length == -1:
                Logger().critical("GroupsSocketListen.run(): %s" % os.strerror(self._connection.errno))
                Logger().critical("GroupsSocketListen.run(): call to EIBConnection.EIBGetGroup_Src() failed")
                sys.exit(-1)
            if length < 2:
                Logger().error("GroupsSocketListen.run(): EIBConnection.EIBGetGroup_Src() returned invalid length (%d)" % length)
            #Logger().debug("GroupsSocketListen.run(): src=%s, dest=%s, buf=%r" % (hex(self._src.data), hex(self._dest.data), self._buffer.buffer))

            if self._buffer.buffer[0] & 0x03 or self._buffer.buffer[1] & 0xc0 == 0xc0:
                Logger().error("GroupsSocketListen.run(): unknown ADPU from %s to %s (%s)" % (self._src.toIndividual(), self._dest.toGroup(), self._buffer.buffer))
            else:
                if self._buffer.buffer[1] & 0xc0 == 0x00:
                    s = "Read"
                elif self._buffer.buffer[1] & 0xc0 == 0x40:
                    s = "Response"
                elif self._buffer.buffer[1] & 0xc0 == 0x80:
                    s = "Write"
                s += " from %s to %s" % (self._src.toIndividual(), self._dest.toGroup())
                if self._buffer.buffer[1] & 0xc0:
                    s += ": "
                    if length == 2:
                        s += "%02x" % (self._buffer.buffer[1] & 0x3f)
                    else:
                        s +="%s" % " ".join([hex(val) for val in self._buffer.buffer[2:]])
                Logger().debug("GroupsSocketListen.run(): %s" % s)
                self._callback(s)


def dummy(s):
    pass


if __name__ == "__main__":
    groupSocketListen = GroupSocketListen("ip:linknxwebbox", dummy)
    groupSocketListen.run()
