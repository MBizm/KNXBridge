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

Application layer group data management

Implements
==========

 - B{APCI}

Documentation
=============

This class defines constants used for the APCI (Application Protocol Control Interface).

Usage
=====

@author: Frédéric Mantegazza
@copyright: (C) 2013 Frédéric Mantegazza
@license: GPL
"""

__revision__ = "$Id$"


class APCI(object):

    _4  = 0x03c0

    GROUPVALUE_READ      = 0x0000  # 4 bit
    GROUPVALUE_RES       = 0x0040  # 4 bit
    GROUPVALUE_WRITE     = 0x0080  # 4 bit

    #_4  = 0x03c00000
    #_10 = 0x03ff0000
    #_18 = 0x03ffff00

    #GROUPVALUE_WRITE     = 0x00800000  # 4 bit
    #GROUPVALUE_READ      = 0x00000000  # 4 bit
    #GROUPVALUE_RES       = 0x00400000  # 4 bit

    #PHYSADDR_WRITE       = 0x00C00000  # 4 bit
    #PHYSADDR_READ        = 0x01000000  # 4 bit
    #PHYSADDR_RES         = 0x01400000  # 4 bit

    #ADC_READ             = 0x01800000  # 4 bit
    #ADC_RES              = 0x01c00000  # 4 bit
    #MEMORY_READ          = 0x02000000  # 4 bit
    #MEMORY_RES           = 0x02400000  # 4 bit
    #MEMORY_WRITE         = 0x02800000  # 4 bit

    #USERMEMORY_READ      = 0x02c00000  # 10 bit
    #USERMEMORY_RES       = 0x02c10000  # 10 bit
    #USERMEMORY_WRITE     = 0x02c20000  # 10 bit
    #USERMEMORYBIT_WRITE  = 0x02c40000  # 10 bit
    #USERMFACTINFO_READ   = 0x02c50000  # 10 bit
    #USERMFACTINFO_RES    = 0x02c60000  # 10 bit

    #DEVICEDESCR_READ     = 0x03000000  # 4 bit
    #DEVICEDESCR_RES      = 0x03400000  # 4 bit
    #RESTART              = 0x03800000  # 4 bit

    #ENABLEEXTERNMEMORY   = 0x03c00000  # 10 bit
    #EXTERNMEMORY_READ    = 0x03c10000  # 10 bit
    #EXTERNMEMORY_RES     = 0x03c20000  # 10 bit
    #EXTERNMEMORY_WRITE   = 0x03c30000  # 10 bit
    #SLAVEMEMORY_READ     = 0x03c80000  # 10 bit
    #SLAVEMEMORY_RES      = 0x03c90000  # 10 bit
    #SLAVEMEMORY_WRITE    = 0x03ca0000  # 10 bit
    #GRPROUTECONFIG_READ  = 0x03cd0000  # 10 bit
    #GRPROUTECONFIG_RES   = 0x03ce0000  # 10 bit
    #GRPROUTECONFIG_WRITE = 0x03cf0000  # 10 bit

    #MEMORYBIT_WRITE      = 0x03d00000  # 10 bit
    #AUTHORIZE_REQ        = 0x03d10000  # 10 bit
    #AUTHORIZE_RES        = 0x03d20000  # 10 bit
    #KEY_WRITE            = 0x03d30000  # 10 bit
    #KEY_RES              = 0x03d40000  # 10 bit

    #PROPERTYVALUE_READ   = 0x03d50000  # 10 bit
    #PROPERTYVALUE_RES    = 0x03d60000  # 10 bit
    #PROPERTYVALUE_WRITE  = 0x03d70000  # 10 bit
    #PROPERTYDESCR_READ   = 0x03d80000  # 10 bit
    #PROPERTYDESCR_RES    = 0x03d90000  # 10 bit

    #PHYSADDRSERNO_READ   = 0x03dc0000  # 10 bit
    #PHYSADDRSERNO_RES    = 0x03dd0000  # 10 bit
    #PHYSADDRSERNO_WRITE  = 0x03de0000  # 10 bit
    #SERVICEINFO_WRITE    = 0x03df0000  # 10 bit

    #DOMAINADDR_WRITE     = 0x03e00000  # 10 bit
    #DOMAINADDR_READ      = 0x03e10000  # 10 bit
    #DOMAINADDR_RES       = 0x03e20000  # 10 bit
    #DOMAINADDRSEL_READ   = 0x03e30000  # 10 bit

    #FREAD_PROPERTY_REQ   = 0x03ff0100  # 18 bit
    #FREAD_PROPERTY_RES   = 0x03ff0200  # 18 bit
    #FWRITE_PROPERTY_REQ  = 0x03ff0300  # 18 bit
    #FWRITE_PROPERTY_RES  = 0x03ff0400  # 18 bit
