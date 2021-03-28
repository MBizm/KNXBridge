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

Datapoint Types translation management

Implements
==========

 - B{DPTXlatorValueError}
 - B{DPTXlatorBase}

Documentation
=============

Usage
=====

@author: Frédéric Mantegazza
@author: B. Malinowsky
@copyright: (C) 2013 Frédéric Mantegazza
@copyright: (C) 2006, 2011 B. Malinowsky
@license: GPL
"""

__revision__ = "$Id$"

from pknyx.common.exception import PKNyXValueError
from pknyx.common.utils import reprStr
from pknyx.services.logger import Logger
from pknyx.core.dptXlator.dptId import DPTID


class DPTXlatorValueError(PKNyXValueError):
    """
    """


class DPTXlatorBase(object):
    """ Base DPT translator class

    Manage conversion between KNX encoded data and python types.

    Each DPTXlator class can handles all DPTs of a same main type.

    The handled DPTs must be defined in sub-classes, as class objects, and named B{DPT_xxx}.

    @ivar _handledDPT: table containing all DPT the DPTXlator can handle (defined in sub-classes)
    @type _handledDPT: dict

    @ivar _dpt: current DPT object of the DPTXlator
    @type _dpt: L{DPT}

    @ivar _typeSize: size of the data type. 0 for data size <= 6bits
    @type _typeSize: int

    @ivar _data: KNX encoded data
    @type _data: depends on sub-class

    @todo: remove the strValue stuff
    """
    def __new__(cls, *args, **kwargs):
        """ Init the class with all available types for this DPT

        All class objects defined in sub-classes name B{DPT_xxx}, will be treated as DPT objects and added to the
        B{_handledDPT} dict.
        """
        self = super(DPTXlatorBase, cls).__new__(cls)
        cls._handledDPT = {}
        for key, value in cls.__dict__.items():
            if key.startswith("DPT_"):
                self._handledDPT[value.id] = value

        return self

    def __init__(self, dptId, typeSize):
        """ Creates a DPT for the given Datapoint Type ID

        @param dptId: available implemented Datapoint Type ID
        @type dptId: str or L{DPTID}

        @param typeSize: size of the data type. Use 0 for data size <= 6bits
        @type typeSize: int

        @raise DPTXlatorValueError:
        """
        super(DPTXlatorBase, self).__init__()

        if not isinstance(dptId, DPTID):
            dptId = DPTID(dptId)
        try:
            self._dpt = self._handledDPT[dptId]
        except KeyError:
            Logger().exception("DPTXlatorBase.__init__()", debug=True)
            raise DPTXlatorValueError("unhandled DPT ID (%s)" % dptId)
        self._typeSize = typeSize

        self._data = None

    def __repr__(self):
        try:
            data_ = hex(self._data)
        except TypeError:
            data_ = None
        return "<%s(dpt='%s')>" % (reprStr(self.__class__), repr(self._dpt.id))

    def __str__(self):
        return "<%s('%s')>" % (reprStr(self.__class__), self._dpt.id)

    @property
    def handledDPT(self):
        handledDPT = sorted(self._handledDPT.keys())
        return handledDPT

    @property
    def dpt(self):
        return self._dpt

    @dpt.setter
    def dpt(self, dptId):
        if not isinstance(dptId, DPTID):
            dptId = DPTID(dptId)
        try:
            self._dpt = self._handledDPT[dptId]
        except KeyError:
            Logger().exception("DPTXlatorBase.dpt", debug=True)
            raise DPTXlatorValueError("unhandled DPT ID (%s)" % dptId)

    @property
    def typeSize(self):
        return self._typeSize

    @property
    def unit(self):
        return self._dpt.unit

    def checkData(self, data):
        """ Check if the data can be handled by the Datapoint Type

        @param data: KNX Datapoint Type to check
        @type data: int

        @raise DPTXlatorValueError: data can't be handled
        """
        Logger().warning("DPTXlatorBase.checkData() not implemented is sub-class")

    def checkValue(self, value):
        """ Check if the value can be handled by the Datapoint Type

        @param value: value to check
        @type value: depends on the DPT

        @raise DPTXlatorValueError: value can't be handled
        """
        Logger().warning("DPTXlatorBase.checkValue() not implemented is sub-class")

    def checkFrame(self, frame):
        """ Check if KNX frame can be handled by the Datapoint Type

        @param frame: KNX Datapoint Type to check
        @type frame: str

        @raise DPTXlatorValueError: frame can't be handled
        """
        Logger().warning("DPTXlatorBase._checkFrame() not implemented is sub-class")

    def dataToValue(self, data):
        """ Conversion from KNX encoded data to python value

        @param data: KNX encoded data
        @type data: int

        @return: python value
        @rtype: depends on the DPT
        """
        raise NotImplementedError

    def valueToData(self, value):
        """ Conversion from python value to KNX encoded data

        @param value: python value
        @type value: depends on the DPT
        """
        raise NotImplementedError

    def dataToFrame(self, data):
        """ Conversion from KNX encoded data to bus frame

        @param data: KNX encoded data
        @type data: int

        @return: KNX encoded data as bus frame
        @rtype: bytearray
        """
        raise NotImplementedError

    def frameToData(self, frame):
        """ Conversion from bus frame to KNX encoded data

        @param frame: KNX encoded data as bus frame
        @type frame: bytearray

        @return: KNX encoded data
        @rtype: depends on the DPT
        """
        raise NotImplementedError


if __name__ == '__main__':
    import unittest

    # Mute logger
    Logger().setLevel('error')


    class DPTXlatorBaseTestCase(unittest.TestCase):

        def setUp(self):
            pass

        def tearDown(self):
            pass

        def test_display(self):
            pass

        def test_constructor(self):
            with self.assertRaises(DPTXlatorValueError):
                DPTXlatorBase("1.001", 0)

    unittest.main()
