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

Documentation
=============

This module contains templates for device generation.

Usage
=====

@author: Frédéric Mantegazza
@copyright: (C) 2013 Frédéric Mantegazza
@license: GPL
"""

__revision__ = "$Id$"


INIT = \
""""""


ADMIN = \
"""#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import os.path
import sys


def main():
    os.environ.setdefault("PKNYX_DEVICE_PATH", os.path.join(os.path.dirname(__file__), "${deviceName}"))

    from pknyx.tools.adminUtility import AdminUtility

    AdminUtility().execute()


if __name__ == "__main__":
    main()
"""


DEVICE = \
"""# -*- coding: utf-8 -*-

from pknyx.api import Device

from ${deviceName}FB import ${deviceClass}FB


class ${deviceClass}(Device):
    FB_01 = dict(cls=${deviceClass}FB, name="${deviceName}_fb", desc="${deviceName} fb")

    LNK_01 = dict(fb="${deviceName}_fb", dp="dp_01", gad="1/1/1")

    DESC = "${deviceClass}"


DEVICE = ${deviceClass}
"""


SETTINGS = \
"""# -*- coding: utf-8 -*-

from pknyx.common import config

DEVICE_NAME = "${deviceName}"
DEVICE_IND_ADDR = "1.1.1"
DEVICE_VERSION = "0.1"

# Override default logger level
config.LOGGER_LEVEL = "info"
"""


FB = \
"""# -*- coding: utf-8 -*-

from pknyx.api import FunctionalBlock
from pknyx.api import logger, schedule, notify


class ${deviceClass}FB(FunctionalBlock):
    DP_01 = dict(name="dp_01", access="output", dptId="1.001", default="Off")

    GO_01 = dict(dp="dp_01", flags="CRWTU", priority="low")

    DESC = "${deviceClass} FB"
"""
