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

Template management.

Implements
==========

 - B{TemplateGenerator}
 - B{TemplateGeneratorValueError}

Documentation
=============

Usage
=====

@author: Frédéric Mantegazza
@copyright: (C) 2013 Frédéric Mantegazza
@license: GPL
"""

__revision__ = "$Id$"

import string
import shutil
import stat
import os

from pknyx.common import config
from pknyx.common.exception import PKNyXValueError

MODE_EXEC = stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH
MODE_0664 = stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IWGRP | stat.S_IROTH
MODE_0775 = MODE_0664 | MODE_EXEC


class TemplateGeneratorValueError(PKNyXValueError):
    """
    """


class TemplateGenerator(object):
    """ TemplateGenerator class definition
    """
    def __init__(self, template):
        """ TemplateGenerator object init
        """
        super(TemplateGenerator, self).__init__()

        self._template = string.Template(template)

    @classmethod
    def createDir(cls, dirName):
        """ Create a fresh directory

        The directory is created at the current path.

        @param dirName: dirName of the directory to create
        @type dirName: str
        """
        os.mkdir(dirName)

    def _createFile(self, fileName, script=False):
        """ Create a new file

        Create a new file in write mode and return the open descriptor.

        @param fileName: name of the file to create (can be a complete path)
        @type fileName: str

        @param script: if True, the file will be set to exec mode
        @type script: bool

        @return: file descriptor
        """
        f = open(fileName, 'w')
        if script:
            mode = os.stat(fileName).st_mode
            os.chmod(fileName, mode | MODE_EXEC)

        return f

    def generateToFile(self, fileName, replaceDict, script=False):
        """ Generate template to file

        @param fileName: name of the file to create (can be a complete path)
        @type fileName: str
        """
        f = self._createFile(fileName, script)
        output = self.generate(replaceDict)
        f.write(output)
        f.close()

    def generate(self, replaceDict):
        """
        """
        return self._template.safe_substitute(replaceDict)


if __name__ == '__main__':
    import unittest

    # Mute logger
    Logger().setLevel('error')


    class TemplateGeneratorTestCase(unittest.TestCase):

        def setUp(self):
            pass

        def tearDown(self):
            pass

        def test_constructor(self):
            pass


    unittest.main()
