
class zigbee_utils:
    """ Utility for value conversion for ZigBee protocol """

    ZBFORMAT_BOOL   = "boolean"
    ZBFORMAT_INT    = "int"
    ZBFORMAT_LIST   = "list"
    ZBFORMAT_MIREDCOL = "miredCol" # https://en.m.wikipedia.org/wiki/Mired

    def __init__(self):
        pass

    @staticmethod
    def getZigBeeValue(zigFormat, val):
        ret = None
        if zigFormat == zigbee_utils.ZBFORMAT_BOOL:
            ret = bool(val)
        if zigFormat == zigbee_utils.ZBFORMAT_INT or \
                zigFormat == zigbee_utils.ZBFORMAT_LIST or \
                zigFormat == zigbee_utils.ZBFORMAT_MIREDCOL:
            # nothing to do here
            ret = val
        return ret