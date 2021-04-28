import re
from datetime import datetime, timedelta, timezone

import dateparser as dateparser
import pytz

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
        # None values might be set by functions, no further processing in these cases
        if len(tok[i]) > 0 and val is not None:
            val = __executeFunctionImpl(dpt, tok[i], val)

    return val


def __executeFunctionImpl(dpt, function, val):
    errDetail = None
    if function[:3] == 'val':
        # replace current value by static value
        try:
            val = float(function[4:-1])
        except ValueError:
            val = function[4:-1]
    elif function[:3] == 'inv':
        # invert current value - restricted to boolean currently
        if isinstance(val, bool):
            # generic 0/1 representation required for dpxlator DPT conversion
            val = not val
        else:
            errDetail = 'wrong value type'
    elif function[:3] == 'div':
        # divide current value by given value
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
        # multiply current value with given value
        if isinstance(val, (int, float)):
            try:
                div = float(function[4:-1])
                val = val * div
            except ValueError:
                errDetail = 'wrong function definition'
        else:
            errDetail = 'wrong value type'
    elif function[:2] == 'lt':
        # checks if current value is less then given value
        if isinstance(val, (int, float)):
            try:
                val = float(val) < float(function[3:-1])
            except ValueError:
                errDetail = 'wrong function definition'
        else:
            errDetail = 'wrong value type'
    elif function[:2] == 'gt':
        # checks if current value is greater then given value
        if isinstance(val, (int, float)):
            try:
                val = float(val) > float(function[3:-1])
            except ValueError:
                errDetail = 'wrong function definition'
        else:
            errDetail = 'wrong value type'
    elif function[:6] == 'eqExcl':
        # checks if current value matches given value
        # return only True if matching, otherwise None for no further processing
        if isinstance(val, (int, float)):
            try:
                if float(val) == float(function[7:-1]):
                    val = True
                else:
                    val = None
            except ValueError:
                errDetail = 'wrong function definition'
        elif isinstance(val, bool):
            try:
                if bool(val) == bool(function[7:-1]):
                    val = True
                else:
                    val = None
            except ValueError:
                errDetail = 'wrong function definition'
        elif isinstance(val, str):
            try:
                if str(val) == str(function[7:-1]):
                    val = True
                else:
                    val = None
            except ValueError:
                errDetail = 'wrong function definition'
        else:
            errDetail = 'wrong value type'
    elif function[:2] == 'eq':
        # checks if current value matches given value, return either true or false
        if isinstance(val, (int, float)):
            try:
                val = (float(val) == float(function[3:-1]))
            except ValueError:
                errDetail = 'wrong function definition'
        elif isinstance(val, bool):
            try:
                val = (bool(val) == bool(function[3:-1]))
            except ValueError:
                errDetail = 'wrong function definition'
        elif isinstance(val, str):
            try:
                val = (str(val) == str(function[3:-1]))
            except ValueError:
                errDetail = 'wrong function definition'
        else:
            errDetail = 'wrong value type'
    elif function[:9] == 'timedelta':
        # checks delta in seconds between now and given date
        # :returns:   true if delta is outside defined delta in seconds
        try:
            errDetail = 'wrong function definition'
            delta = abs(int(function[12:-1]))
            errDetail = 'wrong value type (date cannot be parsed)'
            # retrieve both date value and set them to UTC for comparison
            timenow = datetime.now(timezone.utc)
            clienttime = dateparser.parse(val)
            if function[9:11] == 'LT':
                val = timedelta(seconds=delta) > abs(timenow - clienttime)
            elif function[9:11] == 'GT':
                val = timedelta(seconds=delta) < abs(timenow - clienttime)
            errDetail = None
        except ValueError as ex:
            errDetail += str(ex)
    elif function[:7] == 'timechg':
        # adds/deducts the defined delta in seconds to given date
        # :returns:   the new time with the time in seconds added/deducted
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
