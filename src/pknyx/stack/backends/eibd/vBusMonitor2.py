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

KNX Bus management

Implements
==========

 - B{VBusMonitor2}

@author: Frédéric Mantegazza
@copyright: (C) 2013 Frédéric Mantegazza
@license: GPL
"""
__revision__ = "$Id$"

import os
import sys
import subprocess

from pknyx.services.logger import Logger
from pknyx.stack.backends.eibd.eibConnection import EIBConnection, EIBBuffer, EIBAddr


class EIBAddress(EIBAddr):
    def toGroup(self):
        return "%d/%d/%d" % ((self.data >> 11) & 0x1f, (self.data >> 8) & 0x07, (self.data) & 0xff)

    def toIndividual(self):
        return "%d.%d.%d" % ((self.data >> 12) & 0x0f, (self.data >> 8) & 0x0f, (self.data) & 0xff)


class VBusMonitor2(object):
    """
    """
    def __init__(self, url):
        """
        """
        super(VBusMonitor2, self).__init__()

        self._connection = EIBConnection()
        err = self._connection.EIBSocketURL(url)
        if err:
            Logger().critical("VBusMonitor2.__init__(): %s" % os.strerror(self._connection.errno))
            Logger().critical("VBusMonitor2.__init__(): call to EIBConnection.EIBSocketURL() failed (err=%d)" % err)
            sys.exit(-1)

    def run(self):
        """
        """
        err = self._connection.EIBOpenVBusmonitor()
        if err:
            Logger().critical("VBusMonitor2.run(): %s" % os.strerror(self._connection.errno))
            Logger().critical("VBusMonitor2.run(): call to EIBConnection.EIBOpenVBusmonitor() failed (err=%d)" % err)
            sys.exit(-1)
        while True:
            buffer_ = EIBBuffer()
            lenght = self._connection.EIBGetBusmonitorPacket(buffer_)
            if length == -1:
                Logger().critical("VBusMonitor2.run(): %s" % os.strerror(self._connection.errno))
                Logger().critical("VBusMonitor2.run(): call to EIBConnection.EIBGetBusmonitorPacket() failed")
                sys.exit(-1)
            print buffer_


class KNX(object):
    """ From Domogik project
    """
    def __init__(self):
        """
        """
        super(KNX, self).__init__()

    def listen(self):
        #command = "groupsocketlisten ip:linknxwebbox"
        command = "vbusmonitor2 ip:linknxwebbox"
        self.pipe = subprocess.Popen(command,
                     shell = True,
                     bufsize = 1024,
                     stdout = subprocess.PIPE
                     ).stdout
        self._read = True

        while self._read:
            data = self.pipe.readline()
            if not data:
                break
            print repr(data)

    def stop_listen(self):
        self._read = False


if __name__ == "__main__":
    vBusMonitor2 = VBusMonitor2("ip:linknxwebbox")
    vBusMonitor2.run()

    #device = "ipt:192.168.1.148"
    #obj = KNX()
    #obj.listen()
