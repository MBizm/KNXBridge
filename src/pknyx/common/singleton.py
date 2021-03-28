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

Singleton pattern.

Implements
==========

 - B{Singleton}

Documentation
=============

Juste set this class as __metaclass__ attribute value of your class which need to be a Singleton.

Usage
=====

@author: Frédéric Mantegazza
@copyright: (C) 2013 Frédéric Mantegazza
@license: GPL
"""

__revision__ = "$Id$"



class Singleton(type):
    """ Singleton metaclass
    """
    def __init__(self, *args, **kwargs):
        """ Init the metaclass

        @ivar __instances: instance of the class
        @type __instance: object
        """
        super(Singleton, self).__init__(*args, **kwargs)

        self.__instance = None

    def __call__(self, *args, **kwargs):
        if self.__instance is None:
            self.__instance = super(Singleton, self).__call__(*args, **kwargs)

        return self.__instance


if __name__ == '__main__':
    import unittest

    # Mute logger
    from pknyx.services.logger import Logger
    Logger().setLevel('error')


    class SingletonTest(object):

        __metaclass__ = Singleton


    class SingletonTestCase(unittest.TestCase):

        def setUp(self):
            pass

        def tearDown(self):
            pass

        def test_constructor(self):
            s1 = SingletonTest()
            s2 = SingletonTest()
            self.assertIs(s1, s2)


    unittest.main()
