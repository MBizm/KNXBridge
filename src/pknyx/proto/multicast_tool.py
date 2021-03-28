class MulticastValueError(PKNyXValueError):
    """
    """


class Multicast(object):
    """ Multicast class

    @ivar _xxx:
    @type _xxx:
    """
    def __init__(self, src="0.0.0", mcastAddr="224.0.23.12", mcastPort=3671):
        """

        @param xxx:
        @type xxx:

        raise MulticastValueError:
        """
        super(Multicast, self).__init__()

        if not isinstance(src, IndividualAddress):
            src = IndividualAddress(src)
        self._src = src
        self._mcastAddr = mcastAddr
        self._mcastPort = mcastPort

        self._receiverSock = MulticastSocket(mcastPort)
        self._receiverSock.joinGroup(mcastAddr)

    def write(self, gad, value, dptId="1.xxx", priority=Priority("low"), hopCount=6):
        """ Send a write request
        """
        if not isinstance(gad, GroupAddress):
            gad = GroupAddress(gad)

        sock = MulticastSocket(self._mcastPort, self._mcastAddr)

        dptXlator = DPTXlatorFactory().create(dptId)
        type_ = type(dptXlator.dpt.limits[0])  # @todo: implement this in dptXlators
        value = type_(value)
        frame = dptXlator.dataToFrame(dptXlator.valueToData(value))

        # Application layer (layer 7)
        aPDU = APDU.makeGroupValue(APCI.GROUPVALUE_WRITE, frame, dptXlator.typeSize)

        # Transport layer (layer 4)
        tPDU = aPDU
        tPDU[0] |= TPCI.UNNUMBERED_DATA

        # Network layer (layer 3)
        nPDU = bytearray(len(tPDU) + 1)
        nPDU[0] = len(tPDU) - 1
        nPDU[1:] = tPDU

        # Link layer (layer 2)
        cEMI = CEMILData()
        cEMI.messageCode = CEMILData.MC_LDATA_IND
        cEMI.sourceAddress = self._src
        cEMI.destinationAddress = gad
        cEMI.priority = priority
        cEMI.hopCount = hopCount
        cEMI.npdu = nPDU

        cEMIFrame = cEMI.frame
        cEMIRawFrame = cEMIFrame.raw
        header = KNXnetIPHeader(service=KNXnetIPHeader.ROUTING_IND, serviceLength=len(cEMIRawFrame))
        frame = header.frame + cEMIRawFrame

        sock.transmit(frame)

    def read(self, gad, dptId="1.xxx", timeout=3, priority=Priority("low"), hopCount=6):
        """ Send a read request and wait for answer
        """
        if not isinstance(gad, GroupAddress):
            gad = GroupAddress(gad)

        self._receiverSock.timeout = timeout

        sock = MulticastSocket(self._mcastPort, self._mcastAddr)

        # Application layer (layer 7)
        aPDU = APDU.makeGroupValue(APCI.GROUPVALUE_READ)

        # Transport layer (layer 4)
        tPDU = aPDU
        tPDU[0] |= TPCI.UNNUMBERED_DATA

        # Network layer (layer 3)
        nPDU = bytearray(len(tPDU) + 1)
        nPDU[0] = len(tPDU) - 1
        nPDU[1:] = tPDU

        # Link layer (layer2)
        cEMI = CEMILData()
        cEMI.messageCode = CEMILData.MC_LDATA_IND
        cEMI.sourceAddress = self._src
        cEMI.destinationAddress = gad
        cEMI.priority = priority
        cEMI.hopCount = hopCount
        cEMI.npdu = nPDU

        cEMIFrame = cEMI.frame
        cEMIRawFrame = cEMIFrame.raw
        header = KNXnetIPHeader(service=KNXnetIPHeader.ROUTING_IND, serviceLength=len(cEMIRawFrame))
        frame = header.frame + cEMIRawFrame

        sock.transmit(frame)

        # Link layer (layer2)
        receivedData = None
        receivedStatus = None
        while True:
            try:
                inFrame, (fromAddr, fromPort) = self._receiverSock.receive()
                Logger().debug("Multicast.read(): inFrame=%s (%s, %d)" % (repr(inFrame), fromAddr, fromPort))
                inFrame = bytearray(inFrame)

                header = KNXnetIPHeader(inFrame)
                Logger().debug("Multicast.read(): KNXnetIP header=%s" % repr(header))

                frame = inFrame[KNXnetIPHeader.HEADER_SIZE:]
                Logger().debug("Multicast.read(): frame=%s" % repr(frame))
                cEMI = CEMILData(frame)
                Logger().debug("Multicast.read(): cEMI=%s" % cEMI)

                destAddr = cEMI.destinationAddress
                if isinstance(cEMI.destinationAddress, GroupAddress):
                    receivedData = cEMI
                    receivedStatus = 0
                elif isinstance(destAddr, IndividualAddress):
                    Logger().warning("Multicast.read(): unsupported destination address type (%s)" % repr(destAddr))
                else:
                    Logger().warning("Multicast.read(): unknown destination address type (%s)" % repr(destAddr))

            except:
                Logger().exception("Multicast.read()")
                raise

            # Network layer (layer 3)
            if cEMI is not None:
                if cEMI.messageCode == CEMILData.MC_LDATA_IND:
                    hopCount = cEMI.hopCount
                    mc = cEMI.messageCode
                    src = cEMI.sourceAddress
                    dest = cEMI.destinationAddress
                    priority = cEMI.priority
                    hopCount = cEMI.hopCount

                    if dest == gad and src != self._src:  # Avoid loop

                        # Transport layer (layer 4)
                        tPDU = cEMI.npdu[1:]
                        if isinstance(dest, GroupAddress) and not dest.isNull:
                            tPCI = tPDU[0] & 0xc0
                            if tPCI == TPCI.UNNUMBERED_DATA:

                                # Application layer (layer 7)
                                aPDU = tPDU
                                aPDU[0] &= 0x3f
                                length = len(aPDU) - 2
                                if length >= 0:
                                    aPCI = aPDU[0] << 8 | aPDU[1]
                                    if (aPCI & APCI._4) == APCI.GROUPVALUE_WRITE:
                                        Logger().debug("Multicast.read(): GROUPVALUE_WRITE ignored")
                                        continue

                                    elif (aPCI & APCI._4) == APCI.GROUPVALUE_READ:
                                        Logger().debug("Multicast.read(): GROUPVALUE_READ ignored")
                                        continue

                                    elif (aPCI & APCI._4) == APCI.GROUPVALUE_RES:
                                        data = APDU.getGroupValue(aPDU)

                                        dptXlator = DPTXlatorFactory().create(dptId)
                                        value = dptXlator.dataToValue(dptXlator.frameToData(data))
                                        return value
