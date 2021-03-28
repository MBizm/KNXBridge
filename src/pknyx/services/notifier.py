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

Notifier management

Implements
==========

 - B{Notifier}
 - B{NotifierValueError}

Documentation
=============

One of the nice feature of B{pKNyX} is to be able to register some L{FunctionalBlock<pknyx.core.functionalBlock>}
sub-classes methods to have them executed at specific times. For that, B{pKNyX} uses the nice third-party module
U{APScheduler<http://pythonhosted.org/APScheduler>}.

The idea is to use the decorators syntax to register these methods.

Unfortunally, a decorator can only wraps a function. But what we want is to register an instance method! How can it be
done, as we didn't instanciated the class yet?

Luckily, such classes are not directly instanciated by the user, but through the L{ETS<pknyx.core.ets>} register()
method. So, here is how this registration is done.

Instead of directly using the APScheduler, the Notifier class below provides the decorators we need, and maintains a
list of names of the decorated functions, in _pendingFuncs.

Then, when a new instance of the FunctionalBlock sub-class is created, in ETS.register(), we call the
Notifier.doRegisterJobs() method which tried to retreive the bounded method matching one of the decorated functions.
If found, the method is registered in APScheduler.

Notifier also adds a listener to be notified when a decorated method call fails to be run, so we can log it.

Usage
=====

@author: Frédéric Mantegazza
@copyright: (C) 2013 Frédéric Mantegazza
@license: GPL

@todo: solve name conflicts between blocks -> also store block name when registering?

@todo: use metaclass for FunctionalBlock to store funcs in the class itself. Is it usefull?
--------------------
Juste une idée comme ça: tu pourrais aussi utiliser une métaclasse. Cela permet de personnaliser la création d'une classe. La création de la classe a lieu après que son corps ait été interprété; cela veut dire que les décorateurs sont exécutés avant.

Donc pour les décorateurs, pas grand chose ne change: ils stockent les fonctions décorées dans une liste (funcs).
La métaclasse va récupérer les fonctions; comme la classe est maintenant connue (en cours de création, en fait), tu peux les associer à celle-ci (par exemple faire de funcs un attribut de la classe).

[edit]... ou bien avec un décorateur de classe (Python 2.6+), ça devrait fonctionner aussi
---------------------
See: http://www.developpez.net/forums/d1361199/autres-langages/python-zope/general-python/apschduler-methodes-classe/#post7387938

Idem for scheduler.
"""

__revision__ = "$Id$"

from pknyx.common.exception import PKNyXValueError
from pknyx.common.utils import reprStr
from pknyx.common.singleton import Singleton
from pknyx.services.logger import Logger

scheduler = None


class NotifierValueError(PKNyXValueError):
    """
    """


class Notifier(object):
    """ Notifier class

    @ivar _pendingFuncs:
    @type _pendingFuncs: list

    @ivar _datapointJobs:
    @type _registeredJobs: dict
    """
    __metaclass__ = Singleton

    def __init__(self):
        """ Init the Notifier object

        raise NotifierValueError:
        """
        super(Notifier, self).__init__()

        self._pendingFuncs = []
        self._datapointJobs = {}
        #self._groupJobs = {}

    def addDatapointJob(self, func, dp, condition="change"):
        """ Add a job for a datapoint change

        @param func: job to register
        @type func: callable

        @param dp: name of the datapoint
        @type dp: str

        @param condition: watching condition, in ("change", "always")
        @type condition: str
        """
        Logger().debug("Notifier.addDatapointJob(): func=%s, dp=%s" % (repr(func), repr(dp)))

        if condition not in ("change", "always"):
            raise NotifierValueError("invalid condition (%s)" % repr(condition))

        self._pendingFuncs.append(("datapoint", func, (dp, condition)))

    def datapoint(self, **kwargs):
        """ Decorator for addDatapointJob()
        """
        Logger().debug("Notifier.datapoint(): kwargs=%s" % repr(kwargs))

        def decorated(func):
            """ We don't wrap the decorated function!
            """
            self.addDatapointJob(func, **kwargs)

            return func

        return decorated

    #def addGroupJob(self, func, gad):
        #""" Add a job for a group adress activity

        #@param func: job to register
        #@type func: callable

        #@param gad: group address
        #@type gad: str or L{GroupAddress}
        #"""
        #Logger().debug("Notifier.addGroupJob(): func=%s" % repr(func))

        #self._pendingFuncs.append(("group", func, gad))

    #def group(self, **kwargs):
        #""" Decorator for addGroupJob()
        #"""
        #Logger().debug("Notifier.datapoint(): kwargs=%s" % repr(kwargs))

        #def decorated(func):
            #""" We don't wrap the decorated function!
            #"""
            #self.addGroupJob(func, **kwargs)

            #return func

        #return decorated

    def doRegisterJobs(self, obj):
        """ Really register jobs

        @param obj: instance for which a method may have been pre-registered
        @type obj: object
        """
        Logger().debug("Notifier.doRegisterJobs(): obj=%s" % repr(obj))

        for type_, func, args in self._pendingFuncs:
            Logger().debug("Notifier.doRegisterJobs(): type_=\"%s\", func=%s, args=%s" % (type_, func.func_name, repr(args)))
            method = getattr(obj, func.func_name, None)
            if method is not None:
                Logger().debug("Notifier.doRegisterJobs(): add method %s() of %s" % (method.im_func.func_name, method.im_self))
                if method.im_func is func:
                    if type_ == "datapoint":
                        dp, condition = args
                        try:
                            self._datapointJobs[dp].append((method, condition))
                        except KeyError:
                            self._datapointJobs[dp] = [(method, condition)]
                    #elif type_ == "group":
                        #gad = args
                        #try:
                            #self._groupJobs[gad].append(method)
                        #except KeyError:
                            #self._groupJobs[gad] = [method]

    def datapointNotify(self, dp, oldValue, newValue):
        """ Notification of a datapoint change

        This method is called when a datapoint value changes.

        @param dp: name of the datapoint
        @type dp: str

        @param oldValue: previous value of the datapoint
        @type oldValue: depends on datapoint type

        @param newValue: new value of the datapoint
        @type newValue: depends on datapoint type
        """
        Logger().debug("Notifier.datapointNotify(): dp=%s, oldValue=%s, newValue=%s" % (dp, repr(oldValue), repr(newValue)))

        if dp in self._datapointJobs:
            for method, condition in self._datapointJobs[dp]:
                if oldValue != newValue and condition == "change" or condition == "always":
                    try:
                        Logger().debug("Notifier.datapointNotify(): trigger method %s() of %s" % (method.im_func.func_name, method.im_self))
                        event = dict(name="datapoint", dp=dp, oldValue=oldValue, newValue=newValue, condition=condition)
                        method(event)
                    except:
                        Logger().exception("Notifier.datapointNotify()")

    def printJobs(self):
        """ Print registered jobs
        """


if __name__ == '__main__':
    import unittest

    # Mute logger
    Logger().setLevel('error')


    class NotifierTestCase(unittest.TestCase):

        def setUp(self):
            pass

        def tearDown(self):
            pass

        def test_constructor(self):
            pass


    unittest.main()
