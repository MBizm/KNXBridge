
class zigbee_utils:
    """ Utility for value conversion for ZigBee protocol """

    def __init__(self):
        pass

    @staticmethod
    def getZigBeeValue(zigFormat, val):
        ret = None
        if zigFormat == "boolean":
            ret = bool(val)
        if zigFormat == "int":
            ret = int(val, 16)
        return ret