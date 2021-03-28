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

 - B{GroupListener}

Documentation
=============

This is the base class for L{Group<pknyx.core.group>} listeners.

Usage
=====

@author: Frédéric Mantegazza
@copyright: (C) 2013 Frédéric Mantegazza
@license: GPL
"""

__revision__ = "$Id$"

from pknyx.services.logger import Logger


class GroupListener(object):
    """ GroupListener class
    """
    def __init__(self):
        """ Init the GroupListener object
        """
        super(GroupListener, self).__init__()

    def onWrite(self, src, data):
        """
        """
        raise NotImplementedError

    def onRead(self, src):
        """
        """
        raise NotImplementedError

    def onResponse(self, src, data):
        """
        """
        raise NotImplementedError


if __name__ == '__main__':
    import unittest

    # Mute logger
    Logger().setLevel('error')


    class GroupListenerTestCase(unittest.TestCase):

        def setUp(self):
            pass

        def tearDown(self):
            pass

        def test_constructor(self):
            pass


    unittest.main()
