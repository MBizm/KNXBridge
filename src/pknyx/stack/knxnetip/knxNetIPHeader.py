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

Implements
==========

 - B{}

Documentation
=============

KNXnet/IP header is used to encapsulate cEMI frames.

It contains:

 - header length (8bits) - 0x06
 - protocol version (8 bits) - 0x10
 - service type identifier (16 bits)
 - total frame length (16 bits)

Usage
=====

>>> header = KNXnetIPHeader(frame="\x06\x10\x05\x30\x00\x11\x29\x00\xbc\xd0\x11\x0e\x19\x02\x01\x00\x80")
>>> header.serviceType
1328
>>> header.serviceName
'routing.ind'
>>> header.totalSize
17
>> header.byteArray
bytearray(b'\x06\x10\x05\x30\x00\x11')

>>> data = "\x29\x00\xbc\xd0\x11\x0e\x19\x02\x01\x00\x80\x00"
>>> header = KNXnetIPHeader(serviceType=KNXnetIPHeader.ROUTING_IND, totalSize=KNXnetIPHeader.HEADER_SIZE+len(data))
>>> header.totalSize
18
>> header.byteArray
bytearray(b'\x06\x10\x05\x30\x00\x12')

@author: Frédéric Mantegazza
@author: B. Malinowsky
@copyright: (C) 2013 Frédéric Mantegazza
@copyright: (C) 2006, 2011 B. Malinowsky
@license: GPL
"""

__revision__ = "$Id$"

import struct

from pknyx.common.exception import PKNyXValueError
from pknyx.services.logger import Logger


class KNXnetIPHeaderValueError(PKNyXValueError):
    """
    """


class KNXnetIPHeader(object):
    """ KNXNet/IP head object

    @ivar _serviceType: Service type identifier
    @type _serviceType: int

    @ivar _totalSize: total size of the KNXNet/IP telegram
    @type _totalSize: int

    raise KNXnetIPHeaderValueError:
    """

    # Services identifier values
    CONNECT_REQ = 0x0205
    CONNECT_RES = 0x0206
    CONNECTIONSTATE_REQ = 0x0207
    CONNECTIONSTATE_RES = 0x0208
    DISCONNECT_REQ = 0x0209
    DISCONNECT_RES = 0x020A
    DESCRIPTION_REQ = 0x0203
    DESCRIPTION_RES = 0x204
    SEARCH_REQ = 0x201
    SEARCH_RES = 0x202
    DEVICE_CONFIGURATION_REQ = 0x0310
    DEVICE_CONFIGURATION_ACK = 0x0311
    TUNNELING_REQ = 0x0420
    TUNNELING_ACK = 0x0421
    ROUTING_IND = 0x0530
    ROUTING_LOST_MSG = 0x0531

    SERVICE = (CONNECT_REQ, CONNECT_RES,
               CONNECTIONSTATE_REQ, CONNECTIONSTATE_RES,
               DISCONNECT_REQ, DISCONNECT_RES,
               DESCRIPTION_REQ, DESCRIPTION_RES,
               SEARCH_REQ, SEARCH_RES,
               DEVICE_CONFIGURATION_REQ, DEVICE_CONFIGURATION_ACK,
               TUNNELING_REQ, TUNNELING_ACK,
               ROUTING_IND, ROUTING_LOST_MSG
              )

    HEADER_SIZE = 0x06
    KNXNETIP_VERSION = 0x10

    def __init__(self, frame=None, service=None, serviceLength=0):
        """ Creates a new KNXnet/IP header

        Header can be loaded either from frame or from sratch

        @param frame: byte array with contained KNXnet/IP frame
        @type frame: sequence

        @param service: service identifier
        @type service: int

        @param serviceLength: length of the service structure
        @type serviceLength: int

        @raise KnxNetIPHeaderValueError:
        """

        # Check params
        if frame is not None and service is not None:
            raise KNXnetIPHeaderValueError("can't give both frame and service type")

        if frame is not None:
            frame = bytearray(frame)
            if len(frame) < KNXnetIPHeader.HEADER_SIZE:
                    raise KNXnetIPHeaderValueError("frame too short for KNXnet/IP header (%d)" % len(frame))

            headersize = frame[0] & 0xff
            if headersize != KNXnetIPHeader.HEADER_SIZE:
                raise KNXnetIPHeaderValueError("wrong header size (%d)" % headersize)

            protocolVersion = frame[1] & 0xff
            if protocolVersion != KNXnetIPHeader.KNXNETIP_VERSION:
                raise KNXnetIPHeaderValueError("unsupported KNXnet/IP protocol (%d)" % protocolVersion)

            self._service = (frame[2] & 0xff) << 8 | (frame[3] & 0xff)
            if self._service not in KNXnetIPHeader.SERVICE:
                raise KNXnetIPHeaderValueError("unsupported service (%d)" % self._service)

            self._totalSize = (frame[4] & 0xff) << 8 | (frame[5] & 0xff)
            if len(frame) != self._totalSize:
                raise KNXnetIPHeaderValueError("wrong frame length (%d; should be %d)" % (len(frame), self._totalSize))

        elif service is not None:
            if service not in KNXnetIPHeader.SERVICE:
                raise KNXnetIPHeaderValueError("unsupported service (%d)" % self._service)
            if not serviceLength:
                raise KNXnetIPHeaderValueError("service length missing")
            self._service = service
            self._totalSize = KNXnetIPHeader.HEADER_SIZE + serviceLength

        else:
            raise KNXnetIPHeaderValueError("must give either frame or service type")

    def __repr__(self):
        s = "<KNXnetIPHeader(service='%s', totalSize=%d)>" % (self.serviceName, self._totalSize)
        return s

    def __str__(self):
        s = "<KNXnetIPHeader('%s')>" % self.serviceName
        return s

    @property
    def service(self):
        return self._service

    @property
    def totalSize(self):
        return self._totalSize

    @property
    def frame(self):
        s = struct.pack(">2B2H", KNXnetIPHeader.HEADER_SIZE, KNXnetIPHeader.KNXNETIP_VERSION, self._service, self._totalSize)
        return bytearray(s)

    @property
    def serviceName(self):
        if self._service == KNXnetIPHeader.CONNECT_REQ:
            return "connect.req"
        elif self._service == KNXnetIPHeader.CONNECT_RES:
            return "connect.res"
        elif self._service == KNXnetIPHeader.CONNECTIONSTATE_REQ:
            return "connectionstate.req"
        elif self._service == KNXnetIPHeader.CONNECTIONSTATE_RES:
            return "connectionstate.res"
        elif self._service == KNXnetIPHeader.DISCONNECT_REQ:
            return "disconnect.req"
        elif self._service == KNXnetIPHeader.DISCONNECT_RES:
            return "disconnect.res"
        elif self._service == KNXnetIPHeader.DESCRIPTION_REQ:
            return "description.req"
        elif self._service == KNXnetIPHeader.DESCRIPTION_RES:
            return "description.res"
        elif self._service == KNXnetIPHeader.SEARCH_REQ:
            return "search.req"
        elif self._service == KNXnetIPHeader.SEARCH_RES:
            return "search.res"
        elif self._service == KNXnetIPHeader.DEVICE_CONFIGURATION_REQ:
            return "device-configuration.req"
        elif self._service == KNXnetIPHeader.DEVICE_CONFIGURATION_ACK:
            return "device-configuration.ack"
        elif self._service == KNXnetIPHeader.TUNNELING_REQ:
            return "tunneling.req"
        elif self._service == KNXnetIPHeader.TUNNELING_ACK:
            return "tunneling.ack"
        elif self._service == KNXnetIPHeader.ROUTING_IND:
            return "routing.ind"
        elif self._service == KNXnetIPHeader.ROUTING_LOST_MSG:
            return "routing-lost.msg"
        else:
            return "unknown/unsupported service"


if __name__ == '__main__':
    import unittest

    # Mute logger
    Logger().setLevel('error')


    class KNXnetIPHeaderTestCase(unittest.TestCase):

        def setUp(self):
            self._header1 = KNXnetIPHeader(frame="\x06\x10\x05\x30\x00\x11\x29\x00\xbc\xd0\x11\x0e\x19\x02\x01\x00\x80")
            data = "\x29\x00\xbc\xd0\x11\x0e\x19\x02\x01\x00\x80\x00"
            self._header2 = KNXnetIPHeader(service=KNXnetIPHeader.ROUTING_IND, serviceLength=len(data))

        def tearDown(self):
            pass

        def test_constructor(self):
            with self.assertRaises(KNXnetIPHeaderValueError):
                KNXnetIPHeader(frame="\x06\x10\x05\x30\x00")  # frame length
            with self.assertRaises(KNXnetIPHeaderValueError):
                KNXnetIPHeader(frame="\x05\x10\x05\x30\x00\x11\x29\x00\xbc\xd0\x11\x0e\x19\x02\x01\x00\x80")  # header size
            with self.assertRaises(KNXnetIPHeaderValueError):
                KNXnetIPHeader(frame="\x06\x11\x05\x30\x00\x11\x29\x00\xbc\xd0\x11\x0e\x19\x02\x01\x00\x80")  # protocol version
            with self.assertRaises(KNXnetIPHeaderValueError):
                KNXnetIPHeader(frame="\x06\x10\xff\xff\x00\x11\x29\x00\xbc\xd0\x11\x0e\x19\x02\x01\x00\x80")  # service
            with self.assertRaises(KNXnetIPHeaderValueError):
                KNXnetIPHeader(frame="\x06\x10\x05\x30\x00\x10\x29\x00\xbc\xd0\x11\x0e\x19\x02\x01\x00\x80")  # total length

        def test_service(self):
            self.assertEqual(self._header1.service, KNXnetIPHeader.ROUTING_IND)
            self.assertEqual(self._header2.service, KNXnetIPHeader.ROUTING_IND)

        def test_totalSize(self):
            self.assertEqual(self._header1.totalSize, 17)
            self.assertEqual(self._header2.totalSize, 18)

        def test_byteArray(self):
            self.assertEqual(self._header1.frame, "\x06\x10\x05\x30\x00\x11")
            self.assertEqual(self._header2.frame, "\x06\x10\x05\x30\x00\x12")

        def test_serviceName(self):
            self.assertEqual(self._header1.serviceName, "routing.ind")
            self.assertEqual(self._header2.serviceName, "routing.ind")

    unittest.main()
