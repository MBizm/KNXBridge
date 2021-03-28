from pknyx.core.dptXlator.dptXlatorBase import DPTXlatorValueError
from pknyx.core.dptXlator.dptXlatorFactory import DPTXlatorFactory

if __name__ == '__main__':
    # instantiate factory
    df = DPTXlatorFactory()

    ##############################
    n = 1

    # create DPT converter for boolean
    print("##### Check " + str(n) + " - Boolean/DPT1 #####")
    # checkFrame for validating data type definition
    dc = df.create('1.002')
    print("Supported Types: " + str(dc.handledDPT))

    # KNX data check - KNX2XXX
    knxVal = 0x01
    try:
        if not dc.checkData(knxVal):
            print("Check " + str(n) + " - Python value("+str(knxVal)+"): " + str(dc.dataToValue(knxVal)))
            print("Check " + str(n) + " - Frame Python value("+str(knxVal)+"): " + str(dc.dataToFrame(knxVal)))
    except DPTXlatorValueError:
        print("Check " + str(n) + " - ERROR checkData: cannot be handled")
    except TypeError:
        print("Check " + str(n) + " - ERROR wrong type")

    # Python data check - XXX2KNX
    pyVal = True
    try:
        if not dc.checkValue(pyVal):
            print("Check " + str(n) + " - KNX value("+str(pyVal)+"): " + str(hex(dc.valueToData(pyVal))))
    except DPTXlatorValueError:
        print("Check " + str(n) + " - ERROR checkValue: cannot be handled")
    except TypeError:
        print("Check " + str(n) + " - ERROR wrong type")

    try:
        print("Check " + str(n) + " - Frame KNX value: " + str(dc.frameToData(dc.dataToFrame(knxVal))))
    except TypeError:
        print("Check " + str(n) + " - ERROR wrong type")

    ##############################
    n = 2
    # create DPT converter for float 4-oct
    print("##### Check " + str(n) + " - Float 4-oct/DPT14 #####")
    # checkFrame for validating data type definition
    dc = df.create('14.056')
    print("Supported Types: " + str(dc.handledDPT))

    # KNX data check - KNX2XXX
    knxVal = 0x43BC0000
    try:
        if not dc.checkData(knxVal):
            print("Check " + str(n) + " - Python value("+str(knxVal)+"): " + str(dc.dataToValue(knxVal)))
            print("Check " + str(n) + " - Frame Python value("+str(knxVal)+"): " + str(dc.dataToFrame(knxVal)))
    except DPTXlatorValueError:
        print("Check " + str(n) + " - ERROR checkData: cannot be handled")
    except TypeError:
        print("Check " + str(n) + " - ERROR wrong type")

    # Python data check - XXX2KNX
    pyVal = 1100.25
    try:
        if not dc.checkValue(pyVal):
            print("Check " + str(n) + " - KNX value("+str(pyVal)+"): " + str(hex(dc.valueToData(pyVal))))
    except DPTXlatorValueError:
        print("Check " + str(n) + " - ERROR checkValue: cannot be handled")
    except TypeError:
        print("Check " + str(n) + " - ERROR wrong type")

    cmdVal = '43 BC 00 00'
    try:
        print("Check " + str(n) + " - Frame KNX value("+str(cmdVal)+"): " + str(dc.frameToData(cmdVal)))
    except TypeError:
        print("Check " + str(n) + " - ERROR wrong type")

    ##############################
    n = 3
    # create DPT converter for float 2-oct
    print("##### Check " + str(n) + " - Float 2-oct/DPT9 #####")
    # checkFrame for validating data type definition
    dc = df.create('9.001')
    print("Supported Types: " + str(dc.handledDPT))

    # KNX data check - KNX2XXX
    knxVal = 625
    try:
        if not dc.checkData(knxVal):
            print("Check " + str(n) + " - Python value("+str(knxVal)+"): " + str(dc.dataToValue(knxVal)))
            print("Check " + str(n) + " - Frame Python value("+str(knxVal)+"): " + str(dc.dataToFrame(knxVal)))
    except DPTXlatorValueError:
        print("Check " + str(n) + " - ERROR checkData: cannot be handled")
    except TypeError:
        print("Check " + str(n) + " - ERROR wrong type")

    # Python data check - XXX2KNX
    pyVal = 6.25
    try:
        if not dc.checkValue(pyVal):
            print("Check " + str(n) + " - KNX value("+str(pyVal)+"): " + str(hex(dc.valueToData(pyVal))))
    except DPTXlatorValueError:
        print("Check " + str(n) + " - ERROR checkValue: cannot be handled")
    except TypeError:
        print("Check " + str(n) + " - ERROR wrong type")

    cmdVal = 625
    try:
        print("Check " + str(n) + " - Frame KNX value("+str(cmdVal)+"): " + str(dc.frameToData(cmdVal)))
    except TypeError:
        print("Check " + str(n) + " - ERROR wrong type")

    ##############################
    n = 4
    # create DPT converter for float 4-oct signed
    print("##### Check " + str(n) + " - Float 4-oct signed/DPT13 #####")
    # checkFrame for validating data type definition
    dc = df.create('13.010')
    print("Supported Types: " + str(dc.handledDPT))

    # KNX data check - KNX2XXX
    knxVal = 0x350000
    try:
        if not dc.checkData(knxVal):
            print("Check " + str(n) + " - Python value("+str(knxVal)+"): " + str(dc.dataToValue(knxVal)))
            print("Check " + str(n) + " - Frame Python value("+str(knxVal)+"): " + str(dc.dataToFrame(knxVal)))
    except DPTXlatorValueError:
        print("Check " + str(n) + " - ERROR checkData: cannot be handled")
    except TypeError:
        print("Check " + str(n) + " - ERROR wrong type")

    # Python data check - XXX2KNX
    pyVal = 35000.125
    try:
        if not dc.checkValue(pyVal):
            print("Check " + str(n) + " - KNX value("+str(pyVal)+"): " + str(hex(dc.valueToData(pyVal))))
    except DPTXlatorValueError:
        print("Check " + str(n) + " - ERROR checkValue: cannot be handled")
    except TypeError:
        print("Check " + str(n) + " - ERROR wrong type")

    cmdVal = 625
    try:
        print("Check " + str(n) + " - Frame KNX value("+str(cmdVal)+"): " + str(dc.frameToData(cmdVal)))
    except TypeError:
        print("Check " + str(n) + " - ERROR wrong type")
