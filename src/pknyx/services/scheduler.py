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

Scheduler management

Implements
==========

 - B{Scheduler}
 - B{SchedulerValueError}

Documentation
=============

One of the nice feature of B{pKNyX} is to be able to register some L{FunctionalBlock<pknyx.core.functionalBlock>}
sub-classes methods to have them executed at specific times. For that, B{pKNyX} uses the nice third-party module
U{APScheduler<http://pythonhosted.org/APScheduler>}.

The idea is to use the decorators syntax to register these methods

Unfortunally, a decorator can only wraps a function. But what we want is to register an instance method! How can it be
done, as we didn't instanciated the class yet?

Luckily, such classes are not directly instanciated by the user, but through the L{ETS<pknyx.core.ets>} register()
method. So, here is how this registration is done.

Instead of directly using the APScheduler, the Scheduler class below provides the decorators we need, and maintains a
list of names of the decorated functions, in _pendingFuncs.

Then, when a new instance of the FunctionalBlock sub-class is created, in ets.register(), we call the
Scheduler.doRegisterJobs() method which tried to retreive the bounded method matching one of the decorated functions.
If found, the method is registered in APScheduler.

Scheduler also adds a listener to be notified when a decorated method call fails to be run, so we can log it.

Usage
=====

@author: Frédéric Mantegazza
@copyright: (C) 2013 Frédéric Mantegazza
@license: GPL
"""

__revision__ = "$Id$"

import traceback

import apscheduler.scheduler

from pknyx.common.exception import PKNyXValueError
from pknyx.common.singleton import Singleton
from pknyx.services.logger import Logger, LEVELS

scheduler = None


class SchedulerValueError(PKNyXValueError):
    """
    """


class Scheduler(object):
    """ Scheduler class

    @ivar _pendingFuncs:
    @type _pendingFuncs: list

    @ivar _apscheduler: real scheduler
    @type _apscheduler: APScheduler
    """
    __metaclass__ = Singleton

    TYPE_EVERY = 1
    TYPE_AT = 2
    TYPE_CRON = 3

    def __init__(self, autoStart=False):
        """ Init the Scheduler object

        @param autoStart: if True, automatically starts the scheduler
        @type autoStart: bool

        raise SchedulerValueError:
        """
        super(Scheduler, self).__init__()

        self._pendingFuncs = []

        self._apscheduler = apscheduler.scheduler.Scheduler()
        self._apscheduler.add_listener(self._listener, mask=(apscheduler.scheduler.EVENT_JOB_ERROR|apscheduler.scheduler.EVENT_JOB_MISSED))

        if autoStart:
            scheduler.start()

    def _listener(self, event):
        """ APScheduler listener.

        This listener is called by APScheduler when executing jobs.

        It can be setup so only errors are triggered.
        """
        Logger().debug("Scheduler._listener(): event=%s" % repr(event))

        if event.exception:
            message = "Scheduler._listener()\n" + "".join(traceback.format_tb(event.traceback)) + str(event.exception)
            Logger().log(LEVELS['exception'], message)

    @property
    def apscheduler(self):
        return self._apscheduler

    def every(self, **kwargs):
        """ Decorator for addEveryJob()
        """
        Logger().debug("Scheduler.every(): kwargs=%s" % repr(kwargs))

        def decorated(func):
            """ We don't wrap the decorated function!
            """
            self._pendingFuncs.append((Scheduler.TYPE_EVERY, func, kwargs))

            return func

        return decorated

    def addEvery(self, func, **kwargs):
        """ Add a job which has to be called 'every xxx'

        @param func: job to register
        @type func: callable

        @param kwargs: additional arguments for APScheduler
        @type kwargs: dict
        """
        Logger().debug("Scheduler.addEveryJob(): func=%s" % repr(func))
        self._apscheduler.add_interval_job(func, **kwargs)

    def at(self, **kwargs):
        """ Decorator for addAtJob()
        """
        Logger().debug("Scheduler.at(): kwargs=%s" % repr(kwargs))

        def decorated(func):
            """ We don't wrap the decorated function!
            """
            self._pendingFuncs.append((Scheduler.TYPE_AT, func, kwargs))

            return func

        return decorated

    def addAt(self, func, **kwargs):
        """ Add a job which has to be called 'at xxx'

        @param func: job to register
        @type func: callable
        """
        Logger().debug("Scheduler.addAtJob(): func=%s" % repr(func))
        self._apscheduler.add_date_job(func, **kwargs)

    def cron(self, **kwargs):
        """ Decorator for addCronJob()
        """
        Logger().debug("Scheduler.cron(): kwargs=%s" % repr(kwargs))

        def decorated(func):
            """ We don't wrap the decorated function!
            """
            self._pendingFuncs.append((Scheduler.TYPE_CRON, func, kwargs))

            return func

        return decorated

    def addCron(self, func, **kwargs):
        """ Add a job which has to be called with cron

        @param func: job to register
        @type func: callable
        """
        Logger().debug("Scheduler.addCronJob(): func=%s" % repr(func))
        self._apscheduler.add_cron_job(func, **kwargs)

    def doRegisterJobs(self, obj):
        """ Really register jobs in APScheduler

        @param obj: instance for which a method may have been pre-registered
        @type obj: object
        """
        Logger().debug("Scheduler.doRegisterJobs(): obj=%s" % repr(obj))

        for type_, func, kwargs in self._pendingFuncs:
            Logger().debug("Scheduler.doRegisterJobs(): type_=\"%s\", func=%s, kwargs=%s" % (type_, func.func_name, repr(kwargs)))
            method = getattr(obj, func.func_name, None)
            if method is not None:
                Logger().debug("Scheduler.doRegisterJobs(): add method %s() of %s" % (method.im_func.func_name, method.im_self))
                if method.im_func is func:
                    if type_ == Scheduler.TYPE_EVERY:
                        self._apscheduler.add_interval_job(method, **kwargs)
                    elif type_ == Scheduler.TYPE_AT:
                        self._apscheduler.add_date_job(method, **kwargs)
                    elif type_ == Scheduler.TYPE_CRON:
                        self._apscheduler.add_cron_job(method, **kwargs)

    def printJobs(self):
        """ Print pending jobs

        Simple proxy to APScheduler.print_jobs() method.
        """
        self._apscheduler.print_jobs()

    def start(self):
        """ Start the scheduler

        Simple proxy to APScheduler.start() method.
        """
        Logger().trace("Scheduler.start()")

        if not self._apscheduler.running:
            self._apscheduler.start()

        Logger().debug("Scheduler.start(): running")

    def stop(self):
        """ Shutdown the scheduler

        Simple proxy to APScheduler.stop() method.
        """
        Logger().trace("Scheduler.stop()")

        if self._apscheduler.running:
            self._apscheduler.shutdown()

        Logger().debug("Scheduler.stop(): stopped")


if __name__ == '__main__':
    import unittest

    # Mute logger
    Logger().setLevel('error')


    class SchedulerTestCase(unittest.TestCase):

        def setUp(self):
            pass

        def tearDown(self):
            pass

        def test_constructor(self):
            pass


    unittest.main()
