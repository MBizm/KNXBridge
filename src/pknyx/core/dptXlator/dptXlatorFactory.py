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

Datapoint Types management

Implements
==========

 - B{DPTMainTypeMapper}
 - B{DPTXlatorFactoryObject}
 - B{DPTXlatorFactory}

Usage
=====

@author: Frédéric Mantegazza
@author: B. Malinowsky
@copyright: (C) 2013 Frédéric Mantegazza
@copyright: (C) 2006, 2011 B. Malinowsky
@license: GPL
"""

__revision__ = "$Id$"

import re

from pknyx.services.logger import Logger
from pknyx.core.dptXlator.dptId import DPTID
#from pknyx.core.dptXlator.dpt import DPT
from pknyx.core.dptXlator.dptXlatorBase import DPTXlatorBase, DPTXlatorValueError
from pknyx.core.dptXlator.dptXlatorBoolean import DPTXlatorBoolean                  #  1.xxx
from pknyx.core.dptXlator.dptXlator3BitControl import DPTXlator3BitControl          #  3.xxx
#from pknyx.core.dptXlator.dptXlatorCharacter import DPTXlatorCharacter              #  4.xxx
from pknyx.core.dptXlator.dptXlator8BitUnsigned import DPTXlator8BitUnsigned        #  5.xxx
from pknyx.core.dptXlator.dptXlator8BitSigned import DPTXlator8BitSigned            #  6.xxx
from pknyx.core.dptXlator.dptXlator2ByteUnsigned import DPTXlator2ByteUnsigned      #  7.xxx
from pknyx.core.dptXlator.dptXlator2ByteSigned import DPTXlator2ByteSigned          #  8.xxx
from pknyx.core.dptXlator.dptXlator2ByteFloat import DPTXlator2ByteFloat            #  9.xxx
from pknyx.core.dptXlator.dptXlatorTime import DPTXlatorTime                        # 10.xxx
from pknyx.core.dptXlator.dptXlatorDate import DPTXlatorDate                        # 11.xxx
from pknyx.core.dptXlator.dptXlator4ByteUnsigned import DPTXlator4ByteUnsigned      # 12.xxx
from pknyx.core.dptXlator.dptXlator4ByteSigned import DPTXlator4ByteSigned          # 13.xxx
from pknyx.core.dptXlator.dptXlator4ByteFloat import DPTXlator4ByteFloat            # 14.xxx
from pknyx.core.dptXlator.dptXlatorString import DPTXlatorString                    # 16.xxx
from pknyx.core.dptXlator.dptXlatorScene import DPTXlatorScene                      # 17.xxx
#from pknyx.core.dptXlator.dptXlatorDateTime import DPTXlatorDateTime                # 19.xxx
from pknyx.core.dptXlator.dptXlator8BitEncAbsValue import DPTXlator8BitEncAbsValue  # 20.xxx

dptFactory = None


class DPTMainTypeMapper(object):
    """ Datapoint Type main type mapper class

    Maps a Datapoint Type main part to a corresponding DPTXlator class doing the DPT conversion.

    @ivar _dptId: Datapoint Type ID
    @type _dptId: DPTID

    @ivar _dptXlatorClass: Datapoint Type class
    @type _dptXlatorClass: class

    @ivar _desc: description of the DPT
    @type _desc: str
    """
    def __init__(self, dptId, dptXlatorClass, desc=""):
        """ Creates a new Datapoint Type main type to DPT mapper

        @param dptId: Datapoint Type ID
                      This id must be the generic form ("1.xxx")
        @type dptId: str or L{DPTID}

        @param dptXlatorClass: Datapoint Type class
        @type dptXlatorClass: class

        @param desc: description of the Datapoint Type main type mapper
        @type desc: str

        @raise DPTXlatorValueError:
        """
        super(DPTMainTypeMapper, self).__init__()

        if not issubclass(dptXlatorClass, DPTXlatorBase):
            raise DPTXlatorValueError("dptXlatorClass %s not a sub-class of DPT" % repr(dptXlatorClass))
        if not isinstance(dptId, DPTID):
            dptId = DPTID(dptId)
        self._dptId = dptId
        self._dptXlatorClass = dptXlatorClass
        self._desc = desc

    @property
    def id(self):
        """ return the DPT ID
        """
        return self._dptId

    @property
    def desc(self):
        """ return the mapper description
        """
        return self._desc

    @property
    def dptXlatorClass(self):
        """ return the Datapoint Type class
        """
        return self._dptXlatorClass

    def createXlator(self, dptId):
        """ Create the Datapoint Type for the given dptId

        This method instanciates the DPT using the stored DPTXlator class.

        @param dptId: Datapoint Type ID (full)
        @type dptId: str or L{DPTID}
        """
        return self._dptXlatorClass(dptId)


class DPTXlatorFactoryObject(object):
    """Datapoint Type factory class

    Maintains available KNX Datapoint Type main numbers and creates associated DPTs.

    It stores all available, registered DPT main numbers with the corresponding DPT and an optional description of
    the type.
    For more common used data types, the main types are declared as constants, although this doesn't necessarily indicate a
    translator is actually available.
    All DPT implementations in this package are registered here and available by default. Converters might be
    added or removed by the user.

    A Datapoint Type consists of a data type and a dimension. The data type is referred to through a main number, the
    existing dimensions of a data type are listed through sub numbers. The data type specifies format and encoding, while
    dimension specifies the range and unit.
    A datapoint type identifier (dptID for short), stands for one particular Datapoint Type. The preferred - but not
    enforced - way of naming a dptID is using the expression I{main number}.I{sub number}.
    In short, a datapoint type has a dptID and standardizes one combination of format, encoding, range and unit.

    @ivar _handledMainDPTMappers: table containing all main Datapoint Type mappers
    @type _handledMainDPTMappers: dict
    """
    TYPE_Boolean = DPTMainTypeMapper("1.xxx", DPTXlatorBoolean, "Boolean (main type 1)")
    TYPE_3BitControlled = DPTMainTypeMapper("3.xxx", DPTXlator3BitControl, "3-Bit-Control (main type 3)")
    #TYPE_Character= DPTMainTypeMapper("4.xxx", DPTCharacter, "Character (main type 4)")
    TYPE_8BitUnsigned = DPTMainTypeMapper("5.xxx", DPTXlator8BitUnsigned, "8-Bit-Unsigned (main type 5)")
    TYPE_8BitSigned = DPTMainTypeMapper("6.xxx", DPTXlator8BitSigned, "8-Bit-Signed (main type 6)")
    TYPE_2ByteUnsigned = DPTMainTypeMapper("7.xxx", DPTXlator2ByteUnsigned, "2 Byte-Unsigned (main type 7)")
    TYPE_2ByteSigned = DPTMainTypeMapper("8.xxx", DPTXlator2ByteSigned, "2 Byte-Signed (main type 8)")
    TYPE_2ByteFloat = DPTMainTypeMapper("9.xxx", DPTXlator2ByteFloat, "2 Byte-Float (main type 9)")
    TYPE_Time = DPTMainTypeMapper("10.xxx", DPTXlatorTime, "Time (main type 10)")
    TYPE_Date = DPTMainTypeMapper("11.xxx", DPTXlatorDate, "Date (main type 11)")
    TYPE_4ByteUnsigned = DPTMainTypeMapper("12.xxx", DPTXlator4ByteUnsigned, "4-Byte-Unsigned (main type 12)")
    TYPE_4ByteSigned = DPTMainTypeMapper("13.xxx", DPTXlator4ByteSigned, "4-Byte-Signed (main type 13)")
    TYPE_4ByteFloat = DPTMainTypeMapper("14.xxx", DPTXlator4ByteFloat, "4-Byte-Float (main type 14)")
    TYPE_String = DPTMainTypeMapper("16.xxx", DPTXlatorString, "String (main type 16)")
    TYPE_Scene = DPTMainTypeMapper("17.xxx", DPTXlatorScene, "Scene (main type 17)")
    #TYPE_DateTime = DPTMainTypeMapper("19.xxx", DPTXlatorDateTime, "DateTime (main type 19)")
    TYPE_8BitEncAbsValue = DPTMainTypeMapper("20.xxx", DPTXlator8BitEncAbsValue, "Encoding absolute value (main type 20)")
    #TYPE_HeatingMode = DPTMainTypeMapper("20.xxx", DPTXlatorHeatingMode, "Heating mode (main type 20)")

    def __new__(cls, *args, **kwargs):
        """ Init the class with all available main Types

        All class objects name B{TYPE_xxx}, will be treated as MainTypeMapper objects and added to the
        B{_handledDPT} dict.
        """
        self = super(DPTXlatorFactoryObject, cls).__new__(cls)
        cls._handledMainDPTMappers = {}
        for key, value in cls.__dict__.items():
            if key.startswith("TYPE_"):
                cls._handledMainDPTMappers[vars(self.__class__)[key].id] = vars(self.__class__)[key]

        return self

    def __init__(self):
        """ Init the Datapoint Type convertor factory
        """
        super(DPTXlatorFactoryObject, self).__init__()

    @property
    def handledMainDPTIDs(self):
        """ Return all handled main Datapoint Type IDs the factory can create
        """
        handleMainDPTIDs = self._handledMainDPTMappers.keys()
        handleMainDPTIDs.sort()
        return handleMainDPTIDs

    def create(self, dptId):
        """ Create the Datapoint Type for the given dptId

        The creation is delegated to the main type mapper.

        @param dptId: Datapoint Type ID
        @type dptId: str
        """
        if not isinstance(dptId, DPTID):
            dptId = DPTID(dptId)
        return self._handledMainDPTMappers[dptId.generic].createXlator(dptId)


def DPTXlatorFactory():
    """ Create or return the global dptFactory object

    Sort of Singleton/Borg pattern.
    """
    global dptFactory
    if dptFactory is None:
        dptFactory = DPTXlatorFactoryObject()

    return dptFactory


if __name__ == '__main__':
    import unittest

    # Mute logger
    Logger().setLevel('error')

    class DPTMainTypeMapperTestCase(unittest.TestCase):

        def setUp(self):
            pass

        def tearDown(self):
            pass

        def test_constructor(self):
            class DummyClass:
                pass

            with self.assertRaises(DPTXlatorValueError):
                DPTMainTypeMapper("1.xxx", DummyClass, "Dummy")
            DPTMainTypeMapper("1.xxx", DPTXlatorBoolean, "Dummy")

    class DPTXlatorFactoryObjectTestCase(unittest.TestCase):

        def setUp(self):
            pass

        def tearDown(self):
            pass

        #def test_constructor(self):
            #print DPTXlatorFactory().handledMainDPTIDs

    unittest.main()
