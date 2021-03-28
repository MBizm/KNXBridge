import re
from datetime import datetime, timedelta

import dateparser as dateparser

from core.util.BasicUtil import log


def executeFunction(dpt, function, val):
    """
    performs the selected functions val and returns the outcome. functions can be chained by givign a comma
    or semicolon separated list being processed from left to right
    """
    if not function:
        return val

    # remove all spaces
    function = function.replace(" ", "")

    # check for appearance of a function list (function separated by comma or semicolon)
    tok = re.split("[,;]", function)
    for i in range(0, len(tok)):
        if len(tok[i]) > 0:
            val = __executeFunctionImpl(dpt, tok[i], val)

    return val


def __executeFunctionImpl(dpt, function, val):
    errDetail = None
    if function[:3] == 'val':
        try:
            val = float(function[4:-1])
        except ValueError:
            val = function[4:-1]
    elif function[:3] == 'inv':
        if isinstance(val, bool):
            # generic 0/1 representation required for dpxlator DPT conversion
            val = not val
        else:
            errDetail = 'wrong value type'
    elif function[:3] == 'div':
        if isinstance(val, (int, float)):
            try:
                div = float(function[4:-1])
                if div is not 0:
                    val = val / div
                else:
                    errDetail = 'divider is zero'
            except ValueError:
                errDetail = 'wrong function definition'
        else:
            errDetail = 'wrong value type'
    elif function[:3] == 'mul':
        if isinstance(val, (int, float)):
            try:
                div = float(function[4:-1])
                val = val * div
            except ValueError:
                errDetail = 'wrong function definition'
        else:
            errDetail = 'wrong value type'
    elif function[:2] == 'lt':
        if isinstance(val, (int, float)):
            try:
                val = float(val) < float(function[3:-1])
            except ValueError:
                errDetail = 'wrong function definition'
        else:
            errDetail = 'wrong value type'
    elif function[:2] == 'gt':
        if isinstance(val, (int, float)):
            try:
                val = float(val) > float(function[3:-1])
            except ValueError:
                errDetail = 'wrong function definition'
        else:
            errDetail = 'wrong value type'
    elif function[:9] == 'timedelta':
        """ 
        checks delta in seconds between now and given date
        :returns:   true if delta is outside defined delta in seconds
        """
        try:
            errDetail = 'wrong function definition'
            delta = abs(int(function[10:-1]))
            errDetail = 'wrong value type (date cannot be parsed)'
            val = timedelta(seconds=delta) < abs(datetime.now() - dateparser.parse(val))
            errDetail = None
        except ValueError:
            pass
    elif function[:7] == 'timechg':
        """ 
        adds/deducts the defined delta in seconds to given date
        :returns:   the new time with the time in seconds added/deducted
        """
        try:
            errDetail = 'wrong function definition'
            delta = int(function[8:-1])
            errDetail = 'wrong value type (no date)'
            # calculate time with delta and convert it to original value type
            val = type(val)(dateparser.parse(val) + timedelta(seconds=delta))
            errDetail = None
        except ValueError:
            pass
    if errDetail:
        log('error',
            'Could not apply function "{0}" to value {1} - {2}'.format(function,
                                                                       val,
                                                                       errDetail))
    return val
