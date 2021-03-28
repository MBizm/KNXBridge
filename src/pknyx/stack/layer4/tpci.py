# -*- coding: utf-8 -*-

""" Python KNX framework

License
=======

 - B{pKNyX} (U{http://www.pknyx.org}) is Copyright:
  - (C) 2013 Frédéric Mantegazza

This program is free software you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program if not, write to the Free Software
Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
or see:

 - U{http://www.gnu.org/licenses/gpl.html}

Module purpose
==============

Transport layer group data management

Implements
==========

 - B{TPCI}

Documentation
=============

This class defines constants used for the TPCI (Transport Protocol Control Interface).

Usage
=====

@author: Frédéric Mantegazza
@copyright: (C) 2013 Frédéric Mantegazza
@license: GPL
"""

__revision__ = "$Id$"


class TPCI(object):

    UNNUMBERED_DATA = 0x00
    NUMBERED_DATA   = 0x40

    #CONNECT_REQ     = 0x80
    #CONNECT_CON     = 0x82
    #DISCONNECT_REQ  = 0x81

    #DATA_ACK        = 0xc2
    #DATA_NACK       = 0xc3
