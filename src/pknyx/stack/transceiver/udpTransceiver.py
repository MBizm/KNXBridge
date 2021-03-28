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

Transceiver management

Implements
==========

 - B{UDPTransceiver}
 - B{UDPTransceiverValueError}

Documentation
=============

Usage
=====

@author: Frédéric Mantegazza
@copyright: (C) 2013 Frédéric Mantegazza
@license: GPL

@todo: run transmitter and receiver in a simple threaded method, instead of a complete class thread.
"""

__revision__ = "$Id$"

import threading
import socket

from pknyx.common.exception import PKNyXValueError
from pknyx.services.logger import Logger
from pknyx.stack.result import Result
from pknyx.stack.knxAddress import KnxAddress
from pknyx.stack.groupAddress import GroupAddress
from pknyx.stack.individualAddress import IndividualAddress
from pknyx.stack.multicastSocket import MulticastSocketReceive, MulticastSocketTransmit
from pknyx.stack.transceiver.transceiver import Transceiver
from pknyx.stack.knxnetip.knxNetIPHeader import KNXnetIPHeader, KNXnetIPHeaderValueError
from pknyx.stack.cemi.cemiLData import CEMILData, CEMIValueError


class UDPTransceiverValueError(PKNyXValueError):
    """
    """


class UDPTransceiver(Transceiver):
    """ UDPTransceiver class

    @ivar _mcastAddr:
    @type _mcastAddr:

    @ivar _mcastPort:
    @type _mcastPort:

    @ivar _receiver: multicast receiver loop
    @type _receiver: L{Thread<threading>}

    @ivar _transmitter: multicast transmitter loop
    @type _transmitter: L{Thread<threading>}
    """
    def __init__(self, tLSAP, mcastAddr="224.0.23.12", mcastPort=3671):
        """

        @param tLSAP:
        @type tLSAP: L{TransceiverLSAP}

        @param mcastAddr: multicast address to bind to
        @type mcastAddr: str

        @param mcastPort: multicast port to bind to
        @type mcastPort: str

        raise UDPTransceiverValueError:
        """
        super(UDPTransceiver, self).__init__(tLSAP)

        self._mcastAddr = mcastAddr
        self._mcastPort = mcastPort

        localAddr = socket.gethostbyname(socket.gethostname())
        self._receiverSock = MulticastSocketReceive(localAddr, mcastAddr, mcastPort)
        self._transmitterSock = MulticastSocketTransmit(localAddr, mcastPort, mcastAddr, mcastPort)

        # Create transmitter and receiver threads
        self._receiver = threading.Thread(target=self._receiverLoop, name="UDP receiver")
        #self._receiver.setDaemon(True)
        self._transmitter = threading.Thread(target=self._transmitterLoop, name="UDP transmitter")
        #self._transmitter.setDaemon(True)

    @property
    def tLSAP(self):
        return self._tLSAP

    @property
    def mcastAddr(self):
        return self._mcastAddr

    @property
    def mcastPort(self):
        return self._mcastPort

    @property
    def localAddr(self):
        return self._receiverSock.localAddr

    @property
    def localPort(self):
        return self._receiverSock.localPort

    def _receiverLoop(self):
        """
        """
        Logger().trace("UDPTransceiver._receiverLoop()")

        while self._running:
            try:
                inFrame, (fromAddr, fromPort) = self._receiverSock.receive()
                Logger().debug("UDPTransceiver._receiverLoop(): inFrame=%s (%s, %d)" % (repr(inFrame), fromAddr, fromPort))
                inFrame = bytearray(inFrame)
                try:
                    header = KNXnetIPHeader(inFrame)
                except KNXnetIPHeaderValueError:
                    Logger().exception("UDPTransceiver._receiverLoop()", debug=True)
                    continue
                Logger().debug("UDPTransceiver._receiverLoop(): KNXnetIP header=%s" % repr(header))

                frame = inFrame[KNXnetIPHeader.HEADER_SIZE:]
                Logger().debug("UDPTransceiver._receiverLoop(): frame=%s" % repr(frame))
                try:
                    cEMI = CEMILData(frame)
                except CEMIValueError:
                    Logger().exception("UDPTransceiver._receiverLoop()")  #, debug=True)
                    continue
                Logger().debug("UDPTransceiver._receiverLoop(): cEMI=%s" % cEMI)

                destAddr = cEMI.destinationAddress
                if isinstance(cEMI.destinationAddress, GroupAddress):
                    self._tLSAP.putInFrame(cEMI)

                elif isinstance(destAddr, IndividualAddress):
                    Logger().warning("UDPTransceiver._receiverLoop(): unsupported destination address type (%s)" % repr(destAddr))
                else:
                    Logger().warning("UDPTransceiver._receiverLoop(): unknown destination address type (%s)" % repr(destAddr))

            except socket.timeout:
                pass
                #Logger().exception("UDPTransceiver._receiverLoop()", debug=True)

            except:
                Logger().exception("UDPTransceiver._receiverLoop()")  #, debug=True)

        self._receiverSock.close()

        Logger().trace("UDPTransceiver._receiverLoop(): ended")

    def _transmitterLoop(self):
        """
        """
        Logger().trace("UDPTransceiver._transmitterLoop()")

        while self._running:
            try:
                transmission = self._tLSAP.getOutFrame()
                Logger().debug("UDPTransceiver._transmitterLoop(): transmission=%s" % repr(transmission))

                if transmission is not None:

                    cEMIFrame = transmission.payload
                    cEMIRawFrame = cEMIFrame.raw
                    header = KNXnetIPHeader(service=KNXnetIPHeader.ROUTING_IND, serviceLength=len(cEMIRawFrame))
                    frame = header.frame + cEMIRawFrame
                    Logger().debug("UDPTransceiver._transmitterLoop(): frame= %s" % repr(frame))

                    try:
                        self._transmitterSock.transmit(frame)
                        transmission.result = Result.OK
                    except:
                        Logger().exception("UDPTransceiver._transmitterLoop()")
                        transmission.result = Result.ERROR

                    if transmission.waitConfirm:
                        transmission.acquire()
                        try:
                            transmission.waitConfirm = False
                            transmission.notify()
                        finally:
                            transmission.release()
                        Logger().debug("UDPTransceiver._transmitterLoop(): transmission=%s" % repr(transmission))

            except:
                Logger().exception("UDPTransceiver._transmitterLoop()")  #, debug=True)

        self._transmitterSock.close()

        Logger().trace("UDPTransceiver._transmitterLoop(): ended")

    def start(self):
        """
        """
        Logger().trace("UDPTransceiver.start()")

        self._running = True
        self._receiver.start()
        self._transmitter.start()

    def stop(self):
        """
        """
        Logger().trace("UDPTransceiver.stop()")

        self._running = False

    def join(self):
        """
        """
        Logger().trace("UDPTransceiver.join()")

        self._transmitter.join()
        self._receiver.join()


if __name__ == '__main__':
    import unittest

    # Mute logger
    Logger().setLevel('error')


    class UDPTransceiverTestCase(unittest.TestCase):

        def setUp(self):
            pass

        def tearDown(self):
            pass

        def test_constructor(self):
            pass


    unittest.main()
