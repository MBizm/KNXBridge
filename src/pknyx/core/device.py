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

Device (process) management.

Implements
==========

 - B{Device}

Documentation
=============

The Device is the top-level object. It runs as a process. It mainly encapsulates some initialisations.

Usage
=====

@author: Frédéric Mantegazza
@copyright: (C) 2013 Frédéric Mantegazza
@license: GPL
"""

__revision__ = "$Id$"

from pknyx.common import config
from pknyx.common.exception import PKNyXValueError
from pknyx.services.logger import Logger


class DeviceValueError(PKNyXValueError):
    """
    """


class Device(object):
    """ Device class definition.
    """
    def __init__(self):
        """ Init Device object.
        """
        super(Device, self).__init__()

    def init(self):
        """ Additionnal user init
        """
        pass

    def shutdown(self):
        """ Additionnal user shutdown
        """
        pass

    def register(self, ets):
        """
        """
        Logger().trace("Device._register()")

        for key, value in self.__class__.__dict__.iteritems():
            if key.startswith("FB_"):
                Logger().debug("Device._register(): %s=(%s)" % (key, repr(value)))
                cls = value["cls"]

                # Remove 'cls' key from FB_xxx dict
                # Use a copy to let original untouched
                value_ = dict(value)
                value_.pop('cls')
                ets.register(cls, **value_)

    def weave(self, ets):
        """
        """
        Logger().trace("Device._weave()")

        for key, value in self.__class__.__dict__.iteritems():
            if key.startswith("LNK_"):
                Logger().debug("Device._weave(): %s=(%s)" % (key, repr(value)))
                ets.weave(**value)


if __name__ == '__main__':
    import unittest

    # Mute logger
    Logger().setLevel('error')


    class DeviceTestCase(unittest.TestCase):

        def setUp(self):
            pass

        def tearDown(self):
            pass

        def test_constructor(self):
            pass


    unittest.main()
