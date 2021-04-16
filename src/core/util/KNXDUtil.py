from core.util.BasicUtil import log
from pknyx.core.dptXlator.dptXlatorBase import DPTXlatorBase
from pknyx.core.dptXlator.dptXlatorBoolean import DPTXlatorBoolean
from pknyx.core.dptXlator.dptXlatorFactory import DPTXlatorFactory

dptFactory = None


class DPTXlatorFactoryObjectFacade:
    """ mimics the original implementation of the factory for customizing the DPT implementation it delivers"""

    def __init__(self, dptfImpl):
        self.__dptfImpl = dptfImpl

    def create(self, dptId):
        """ wrap DPT object for customization """
        dptHandler = self.__dptfImpl.create(dptId)
        return DPTXlatorBaseFacade(dptHandler)


def DPTXlatorFactoryFacade():
    """ wraps the original implementation to customize resulting DPT implementation objects """

    global dptFactory
    if dptFactory is None:
        dptFactory = DPTXlatorFactoryObjectFacade(DPTXlatorFactory())

    return dptFactory


class DPTXlatorBaseFacade(DPTXlatorBase):
    """ facade that introduces additional method to the DPT types """

    def __init__(self, dptimpl):
        """ store implementing class for facade """
        # no need to call super-class constructor due to facade character
        self.__dptimpl = dptimpl

    #############################
    #       custom methos       #
    #############################

    def valueToData(self, value):
        """
        customize original implementation by returning hex-ified and chunked value representation for direct usage in cmd
        :returns:   4 typles á 00-FF hex representation separated by spaces
        :raises:    NotImplementedError in case value is not of type int or float
        """
        ret = self.__dptimpl.valueToData(value)
        if not isinstance(ret, (int, float)):
            log('error',
                "KNXUtil.valueToData() - Data type {0} not yet implemented".format(type(value)))
            raise NotImplementedError

        ret = hex(int(ret))

        # fill up with leading 0's if hex not filling corresponding byte representation
        if len(ret[2:]) < (2 * self.typeSize):
            for i in range(0, (2 * self.typeSize) - len(ret[2:])):
                ret = ret[:2] + '0' + ret[2:]

        # print byte-wise representation separated by blanks
        return ' '.join(ret[i:i + 2] for i in range(2, len(ret), 2))

    def checkValue(self, value):
        # original implementation returns None in case of success, throws exception in case of error
        # change to return success state as boolean
        return self.__dptimpl.checkValue(value) is None

    def checkData(self, data):
        # original implementation returns None in case of success, throws exception in case of error
        # change to return success state as boolean
        return self.__dptimpl.checkData(data) is None

    #############################
    #       facade methos       #
    #############################

    @property
    def handledDPT(self):
        return self.__dptimpl.handledDPT

    @property
    def dpt(self):
        return self.__dptimpl.dpt

    @dpt.setter
    def dpt(self, dptId):
        return self.__dptimpl.dpt(self, dptId)

    @property
    def typeSize(self):
        return self.__dptimpl.typeSize

    @property
    def unit(self):
        return self.__dptimpl.unit

    def checkFrame(self, frame):
        return self.__dptimpl.checkFrame(frame)

    def dataToValue(self, data):
        return self.__dptimpl.dataToValue(data)

    def dataToFrame(self, data):
        return self.__dptimpl.dataToFrame(data)

    def frameToData(self, frame):
        return self.__dptimpl.frameToData(frame)
