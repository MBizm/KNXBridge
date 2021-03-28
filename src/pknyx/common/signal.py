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

Signal/slot pattern

Implements
==========

 - B{Signal}
 - B{_WeakMethod_FuncHost}
 - B{_WeakMethod}

Documentation
=============

To use, simply create a B{Signal} instance. The instance may be a member of a class, a global, or a local; it makes no
difference what scope it resides within. Connect slots to the signal using the B{connect()} method.

The slot may be a member of a class or a simple function. If the slot is a member of a class, Signal will automatically
detect when the method's class instance has been deleted and remove it from its list of connected slots.

This class was generously donated by a poster on ASPN see U{http://aspn.activestate.com}

Usage
=====

>>> sig = Signal()
>>> def test(value): print "test(): %s" % repr(value)
>>> sig.connect(test)
>>> sig.emit("Hello World!")
test(): 'Hello World!'
>>> sig.disconnect(test)
>>> sig.emit("Hello World!")

@author: Frédéric Mantegazza
@copyright: (C) 2013 Frédéric Mantegazza
@license: GPL
"""

__revision__ = "$Id$"

import os
import os.path
import weakref
import inspect

#from pknyx.services.logger import Logger


class Signal(object):
    """ class Signal.
    """
    def __init__(self):
        """ Init the Signal object.
        """
        self.__slots = []

        # Keeping references to _WeakMethod_FuncHost objects.
        # If we didn't, then the weak references would die for
        # non-method slots that we've created.
        self.__funchost = []

    def __call__(self, *args, **kwargs):
        self.emit(*args, **kwargs)

    def emit(self, *args, **kwargs):
        """ Emit the signal.

        @todo: add try/except?
        """
        for i in xrange(len(self.__slots)):
            slot = self.__slots[i]
            if slot != None:
                #try:
                slot(*args, **kwargs)
                #except:
                #    Logger().exception("Signal.emit()", debug=True)
                #    raise
            else:
                del self.__slots[i]

    def connect(self, slot): # , keepRef=False):
        """ Connect slot to the signal

        @param slot: method or function
        @type slot: callable
        """
        self.disconnect(slot)
        if inspect.ismethod(slot):
            #if keepRef:
                #self.__slots.append(slot)
            #else:
            self.__slots.append(_WeakMethod(slot))
        else:
            o = _WeakMethod_FuncHost(slot)
            self.__slots.append(_WeakMethod(o.func))

            # we stick a copy in here just to keep the instance alive
            self.__funchost.append(o)

    def disconnect(self, slot):
        """ Disconnect slot from the signal

        @param slot: method or function
        @type slot: callable
        """
        try:
            for i in xrange(len(self.__slots)):
                wm = self.__slots[i]
                if inspect.ismethod(slot):
                    if wm.f == slot.im_func and wm.c() == slot.im_self:
                        del self.__slots[i]
                        return
                else:
                    if wm.c().hostedFunction == slot:
                        del self.__slots[i]
                        return
        except:
            pass

    def disconnectAll(self):
        """ Disconnect all slots from the signal
        """
        del self.__slots
        del self.__funchost
        del self.__methodhost
        self.__slots = []
        self.__funchost = []
        self.__methodhost = []


class _WeakMethod_FuncHost:
    """
    """
    def __init__(self, func):
        self.hostedFunction = func

    def func(self, *args, **kwargs):
        self.hostedFunction(*args, **kwargs)


class _WeakMethod:
    """
    """
    def __init__(self, f):
        self.f = f.im_func
        self.c = weakref.ref(f.im_self)

    def __call__(self, *args, **kwargs):
        if self.c() == None:
            return
        self.f(self.c(), *args, **kwargs)
