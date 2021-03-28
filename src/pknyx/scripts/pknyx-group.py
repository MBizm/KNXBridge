#!/usr/bin/python
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

Multicast tool to send requests on group address. Can also act as a bus monitor.

Implements
==========

 - B{GroupUtility} (todo)
 - B{SimpleQueue}
 - B{SimpleGroupObject}
 - B{SimpleGroupMonitorObject}

Documentation
=============

This script is used to send/receive multicast requests. It mimics what the stack does.

Usage
=====

pknyx-group.py --help

@author: Frédéric Mantegazza
@copyright: (C) 2013 Frédéric Mantegazza
@license: GPL
"""

__revision__ = "$Id$"

import sys
import time
import argparse
import threading

from pknyx.common.exception import PKNyXValueError
from pknyx.services.logger import Logger
from pknyx.core.dptXlator.dptXlatorFactory import DPTXlatorFactory
from pknyx.core.groupListener import GroupListener
from pknyx.core.groupMonitorListener import GroupMonitorListener
from pknyx.stack.stack import Stack
from pknyx.stack.priority import Priority


class SimpleQueue(list):
    """ Simple condition locked queue

    This queue is a list with additionnal condition locking features.

    @ivar _condition: condition for locking feature
    @type _condition: L{Condition<threading>}
    """
    def __init__(self):
        """ Init the queue
        """
        super(SimpleQueue, self).__init__()

        self._condition = threading.Condition()

    def acquire(self, *args):
        """ Acquire the condition
        """
        self._condition.acquire(*args)

    def release(self):
        """ Release the condition
        """
        self._condition.release()

    def wait(self, timeout=None):
        """ Wait far a condition notification
        """
        self._condition.wait(timeout)

    def notify(self, n=1):
        """ Notify thread waiting for the condition
        """
        self._condition.notify(n)

    def notifyAll(self):
        """ Notify all threads waiting for the condition
        """
        self._condition.notifyAll()


class SimpleGroupObject(GroupListener):
    """
    """
    def __init__(self):
        """ Init the group listener
        """
        super(SimpleGroupObject, self).__init__()

        self._queue = SimpleQueue()

    def onWrite(self, src, data):
        Logger().debug("SimpleGroupObject.onWrite(): src=%s, data=%s" % (src, repr(data)))

    def onRead(self, src):
        Logger().debug("SimpleGroupObject.onRead(): src=%s" % src)

    def onResponse(self, src, data):
        Logger().debug("SimpleGroupObject.onResponse(): src=%s, data=%s" % (src, repr(data)))

        self._queue.acquire()
        try:
            self._queue.insert(0, data)
            self._queue.notify()
        finally:
            self._queue.release()

    @property
    def queue(self):
        return self._queue


class SimpleGroupMonitorObject(GroupMonitorListener):
    """
    """
    def __init__(self):
        """ Init the group listener
        """
        super(SimpleGroupMonitorObject, self).__init__()

        self._queue = SimpleQueue()

    def _enqueue(self, type_, src, gad, priority, data):
        """
        """
        self._queue.acquire()
        try:
            self._queue.insert(0, (type_, src, gad, priority, data))
            self._queue.notify()
        finally:
            self._queue.release()

    def onWrite(self, src, gad, priority, data):
        Logger().debug("SimpleGroupMonitorObject.onWrite(): src=%s, gad=%s, priority=%s, data=%s" % \
                       (src, gad, priority, repr(data)))

        self._enqueue("GROUPVALUE_WRITE", src, gad, priority, data)

    def onRead(self, src, gad, priority):
        Logger().debug("SimpleGroupMonitorObject.onRead(): src=%s, gad=%s, priority=%s" % (src, gad, priority))

        self._enqueue("GROUPVALUE_READ", src, gad, priority, None)

    def onResponse(self, src, gad, priority, data):
        Logger().debug("SimpleGroupMonitorObject.onResponse(): src=%s, gad=%s, priority=%s, data=%s" % \
                       (src, gad, priority, repr(data)))

        self._enqueue("GROUPVALUE_RESP", src, gad, priority, data)

    @property
    def queue(self):
        return self._queue


def write(gad, value, dptId="1.xxx", src="0.0.0",  priority="low", hopCount=6):
    """
    """
    if not isinstance(priority, Priority):
        priority = Priority(priority)

    stack = Stack(individualAddress=src)

    groupObject = SimpleGroupObject()
    group = stack.agds.subscribe(gad, groupObject)

    dptXlator = DPTXlatorFactory().create(dptId)
    type_ = type(dptXlator.dpt.limits[0])  # @todo: implement this in dptXlators
    value = type_(value)
    data = dptXlator.dataToFrame(dptXlator.valueToData(value))

    stack.start()
    try:
        group.write(priority, data, dptXlator.typeSize)
        time.sleep(1)  # Find a way to wait until the stack sending queue is empty (stack.waitEmpty()?)

    finally:
        stack.stop()


def read(gad, timeout=1, wait=True, dptId="1.xxx", src="0.0.0", priority="low", hopCount=6):
    """
    """
    if not isinstance(priority, Priority):
        priority = Priority(priority)

    stack = Stack(individualAddress=src)

    groupObject = SimpleGroupObject()
    group = stack.agds.subscribe(gad, groupObject)

    stack.start()
    try:
        group.read(priority)

        if wait:
            groupObject.queue.acquire()
            try:
                groupObject.queue.wait(timeout)  # Find a wait to know if timeout expired
                try:
                    data = groupObject.queue.pop()
                except IndexError:
                    Logger().warning("No answer from %s" % gad)
                    sys.exit(1)
            finally:
                groupObject.queue.release()

            dptXlator = DPTXlatorFactory().create(dptId)
            value = dptXlator.dataToValue(dptXlator.frameToData(data))
            Logger().info(repr(value))

    finally:
        stack.stop()


def response(gad, value, dptId="1.xxx", src="0.0.0",  priority="low", hopCount=6):
    """
    """
    if not isinstance(priority, Priority):
        priority = Priority(priority)

    stack = Stack(individualAddress=src)

    groupObject = SimpleGroupObject()
    group = stack.agds.subscribe(gad, groupObject)

    dptXlator = DPTXlatorFactory().create(dptId)
    type_ = type(dptXlator.dpt.limits[0])  # @todo: implement this in dptXlators
    value = type_(value)
    data = dptXlator.dataToFrame(dptXlator.valueToData(value))

    stack.start()
    try:
        group.response(priority, data, dptXlator.typeSize)
        time.sleep(1)  # Find a way to wait until the stack sending queue is empty (stack.waitEmpty()?)

    finally:
        stack.stop()


def monitor(src="0.0.1"):
    """
    """
    Logger().debug("monitor(): src=%s" % src)

    stack = Stack(individualAddress=src)

    groupMonitorObject = SimpleGroupMonitorObject()
    group = stack.agds.subscribe("0/0/0", groupMonitorObject)

    stack.start()
    try:
        while True:
            try:
                groupMonitorObject.queue.acquire()
                try:
                    groupMonitorObject.queue.wait(0.1)
                    try:
                        type_, src, gad, priority, data = groupMonitorObject.queue.pop()
                        Logger().info("Got %-16s from %-8s to %-8s with priority %-6s data=%s" % (type_, src, gad, priority, repr(data)))
                    except IndexError:
                        pass
                finally:
                    groupMonitorObject.queue.release()

            except KeyboardInterrupt:
                break

    finally:
        stack.stop()


def main():

    # Common options
    parser = argparse.ArgumentParser(prog="multicast.py",
                                     description="This tool is used to send multicast requests on KNX bus.",
                                     epilog="Under developement...")
    parser.add_argument("-l", "--logger",
                        choices=["trace", "debug", "info", "warning", "error", "exception", "critical"],
                        action="store", dest="loggerLevel", default="info", metavar="LEVEL",
                        help="logger level")
    parser.add_argument("-s", "--srcAddr", action="store", type=str, dest="src",
                        help="source address to use")

    readWriteRespParser = argparse.ArgumentParser(add_help=False)
    readWriteRespParser.add_argument("-d", "--dptId", action="store", type=str, dest="dptId", default="1.xxx",
                                     help="DPTID to use to encode/decode data")
    readWriteRespParser.add_argument("--priority", choices=["system", "normal", "urgent", "low"],
                                     type=str, dest="priority", default="low",
                                     help="bus priority")
    readWriteRespParser.add_argument("--hopCount", type=int, dest="hopCount", default=6, metavar="HOPCOUNT",
                                     help="hopcount")

    # Create sub-parsers
    subparsers = parser.add_subparsers(title="subcommands", description="valid subcommands",
                                       help="sub-command help")

    # Write parser
    parserWrite = subparsers.add_parser("write",
                                        parents=[readWriteRespParser],
                                        help="send a write request")
    parserWrite.set_defaults(func=write)
    parserWrite.add_argument("gad", type=str,
                             help="group address")
    parserWrite.add_argument("value", type=str,
                             help="value to send")

    # Read parser
    parserRead = subparsers.add_parser("read",
                                       parents=[readWriteRespParser],
                                       help="send a read request")
    parserRead.set_defaults(func=read)
    parserRead.add_argument("-t", "--timeout", type=int, default=1, metavar="TIMEOUT",
                            help="read timeout")
    parserRead.add_argument("-n", "--no-wait", action="store_false", dest="wait", default=True,
                            help="wait for response")
    parserRead.add_argument("gad", type=str,
                            help="group address")

    # Response parser
    parserResponse = subparsers.add_parser("response",
                                           parents=[readWriteRespParser],
                                           help="send a response")
    parserResponse.set_defaults(func=response)
    parserResponse.add_argument("gad", type=str,
                                help="group address")
    parserResponse.add_argument("value", type=str,
                                help="value to send")

    # Monitor parser
    parserMonitor = subparsers.add_parser("monitor",
                                          help="monitor bus")
    parserMonitor.set_defaults(func=monitor)

    # Parse
    args = parser.parse_args()

    Logger(level=args.loggerLevel)

    options = dict(vars(args))
    options.pop("func")
    options.pop("loggerLevel")
    if args.src is None:
        options.pop("src")
    args.func(**options)


if __name__ == '__main__':
    main()
