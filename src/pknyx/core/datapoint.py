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

Datapoint management

Implements
==========

 - B{Datapoint}
 - B{DatapointValueError}

Documentation
=============

Usage
=====

>>> from datapoint import Datapoint
>>> dp = Datapoint(None, id="test", name="PID_TEST", access='output')
>>> dp
<Datapoint(id='test', name='PID_TEST', access='output', dptId='1.xxx')>
>>> dp.id
'test'
>>> dp.name
'PID_TEST"
>>> dp.access
'output'
>>> dp.dptId
<DPTID("1.xxx")>

@author: Frédéric Mantegazza
@copyright: (C) 2013 Frédéric Mantegazza
@license: GPL
"""

__revision__ = "$Id$"

from pknyx.common.exception import PKNyXValueError
from pknyx.services.logger import Logger
from pknyx.common.signal import Signal
from pknyx.core.dptXlator.dptXlatorFactory import DPTXlatorFactory
from pknyx.core.dptXlator.dpt import DPTID
from pknyx.stack.flags import Flags
from pknyx.stack.priority import Priority


class DatapointValueError(PKNyXValueError):
    """
    """


class Datapoint(object):
    """ Datapoint handling class

    The term B{data} refers to the KNX representation of the python type B{value}. It is stored in this object.
    The B{frame} is the 'data' as bytearray, which can be sent/received over the bus.

    @ivar _owner: owner of the Datapoint
    @type _owner: L{FunctionalBlock<pknyx.core.functionalBlock>}

    @ivar _name: name of the Datapoint
    @type _name: str

    @ivar _access: access to Datapoint, in ('input', 'output', 'param') -> set possible GroupObject flags
                   - input:
                   - output:
                   - param:
    @type _access: str

    @ivar _dptId: Datapoint Type ID
    @type _dptId: str or L{DPTID}

    @ivar _default: value to use as default
    @type _default: depend on the DPT

    @ivar _data: KNX encoded data
    @type _data: depends on sub-class

    @ivar _dptXlator: DPT translator associated with this Datapoint
    @type _dptXlator: L{DPTXlator<pknyx.core.dptXlator>}

    @ivar _dptXlatorGeneric: generic DPT translator associated with this Datapoint
    @type _dptXlatorGeneric: L{DPTXlator<pknyx.core.dptXlator>}

    @ivar _signalChanged: emitted when the datapoint value has been updated by the owner
                          Used to notify associated GroupObject (and other proxies), if any
                          Params sent are datapoint name, old and new values.
    @type _signalChanged: L{Signal}

    @todo: add desc. param
    @todo: take 'access' into account when transmit/receive
    """
    def __init__(self, owner, name, access, dptId=DPTID(), default=None):
        """

        @param owner: owner of the datapoint
        @type owner: L{FunctionalBlock<pknyx.core.functionalBloc>}

        @param name: name of the Datapoint
        @type name: str

        @param access: access to Datapoint, in ('input', 'output', 'param')
        @type access: str

        @param dptId: Datapoint Type ID
        @type dptId: str or L{DPTID}

        @param default: value to use as default
        @type default: depend on the DPT
        """
        super(Datapoint, self).__init__()

        #Logger().debug("Datapoint.__init__(): name=%s, access=%s, dptId=%s, default=%s" % \
                       #repr(name), repr(access), repr(dptId), repr(default)))

        # Check input
        if access not in ('input', 'output', 'param'):
            raise DatapointValueError("invalid access (%s)" % repr(access))

        self._owner = owner
        self._name = name
        if not isinstance(dptId, DPTID):
            dptId = DPTID(dptId)
        self._dptId = dptId
        self._access = access
        self._default = default
        self._data = None

        self._dptXlator = DPTXlatorFactory().create(dptId)
        if dptId != dptId.generic:
            self._dptXlatorGeneric = DPTXlatorFactory().create(dptId.generic)
        else:
            self._dptXlatorGeneric = self._dptXlator

        # Signals definition
        self._signalChanged = Signal()

        # Set default value
        if default is not None:
            self._setValue(default)

    def __repr__(self):
        return "<Datapoint(name='%s', access='%s', dptId='%s')>" % \
               (self._name, self._access, self._dptId)

    def __str__(self):
        return "<Datapoint('%s')>" % self._name

    @property
    def owner(self):
        return self._owner

    @property
    def name(self):
        return self._name

    @property
    def dptId(self):
        return self._dptId

    @property
    def access(self):
        return self._access

    @property
    def default(self):
        return self._default

    @property
    def data(self):
        return self._data

    def _setData(self, data):
        self._dptXlator.checkData(data)
        self._data = data

    @property
    def dptXlator(self):
        return self._dptXlator

    @property
    def dptXlatorGeneric(self):
        return self._dptXlatorGeneric

    @property
    def signalChanged(self):
        return self._signalChanged

    @property
    def value(self):
        if self._data is None:
            return None
        return self._dptXlator.dataToValue(self._data)

    def _setValue(self, value):
        self._dptXlator.checkValue(value)
        data = self._dptXlator.valueToData(value)
        self._setData(data)

    @value.setter
    def value(self, value):
        oldValue = self.value
        self._dptXlator.checkValue(value)
        data = self._dptXlator.valueToData(value)
        self._setData(data)

        # Notify associated GroupObject (if any)
        self._signalChanged.emit(oldValue, self.value)

        # Notify owner (FunctionalBlock)
        self._owner.notify(self.name, oldValue, self.value)  # TBD

    @property
    def unit(self):
        return self._dptXlator.unit

    @property
    def frame(self):
        return (self._dptXlator.dataToFrame(self._data), self._dptXlator.typeSize)

    @frame.setter
    def frame(self, frame):
        oldValue = self.value
        data = self._dptXlator.frameToData(frame)  # @todo: check frame size with _dptXlator.typeSize...
        self._setData(data)

        # Notify owner (FunctionalBlock)
        self._owner.notify(self.name, oldValue, self.value)


if __name__ == '__main__':
    import unittest

    # Mute logger
    Logger().setLevel('error')


    class DPTestCase(unittest.TestCase):

        def setUp(self):
            self.dp = Datapoint(self, name="dp", access="output", dptId="1.xxx", default=0.)

        def tearDown(self):
            pass

        def test_display(self):
            print repr(self.dp)
            print self.dp

        def test_constructor(self):
            with self.assertRaises(DatapointValueError):
                DP = dict(name="dp", access="outpu", dptId="1.xxx", default=0.)
                Datapoint(self, **DP)


    unittest.main()
