import re
from datetime import datetime, timedelta, timezone

import dateparser as dateparser

from core.util.BasicUtil import log, is_number, convert_number, is_bool


def executeFunction(deviceInstance, dpt, function, val):
    """
    performs the selected functions val and returns the outcome. functions can be chained by givign a comma
    or semicolon separated list being processed from left to right
    :param deviceInstance:      KNXDDevice instance for knx value callbacks, type hint not specified due to import loop
    :returns val of corresponding type after function execution
    """
    if not function:
        return val

    # check for appearance of a function list (function separated by comma or semicolon)
    tok = re.split("[,;]", function)
    for i in range(0, len(tok)):
        # None values might be set by functions, no further processing in these cases
        if len(tok[i]) > 0 and val is not None:
            val = __executeFunctionImpl(deviceInstance, dpt, tok[i].strip(), val)

    return val


def __executeFunctionImpl(deviceInstance, dpt, function, val):
    errDetail = None
    if function[:3] == 'val':
        # replace current value by static value
        try:
            val = float(function[4:-1])
        except ValueError:
            val = function[4:-1]
    elif function[:3] == 'inv':
        # invert current value - restricted to boolean currently
        if is_bool(val):
            # generic 0/1 representation required for dpxlator DPT conversion
            val = not val
        else:
            errDetail = 'wrong value type'
    elif function[:3] == 'max':
        # returns the greater value, useful for greater 0 assurancce
        if is_number(val):
            try:
                val = convert_number(val)
                val = max(val, function[4:-1])
            except ValueError:
                errDetail = 'wrong function definition'
        else:
            errDetail = 'wrong value type'
    elif function[:3] == 'min':
        # returns the lower value
        if is_number(val):
            try:
                val = convert_number(val)
                val = min(val, function[4:-1])
            except ValueError:
                errDetail = 'wrong function definition'
        else:
            errDetail = 'wrong value type'
    elif function[:3] == 'rnd':
        # rounds the current value to the given precision
        if is_number(val):
            try:
                val = convert_number(val)
                val = round(val, function[4:-1])
            except ValueError:
                errDetail = 'wrong function definition'
        else:
            errDetail = 'wrong value type'
    elif function[:3] == 'div':
        # divide current value by given value
        if is_number(val):
            try:
                val = convert_number(val)
                div = float(function[4:-1])
                if div is not 0:
                    val = val / div
                else:
                    if float(function[4:-1]) == 0:
                        errDetail = 'divider is zero'
                    else:
                        errDetail = 'wrong function definition'
            except ValueError:
                errDetail = 'wrong function definition'
        else:
            errDetail = 'wrong value type'
    elif function[:3] == 'mul':
        # multiply current value with given value
        if is_number(val):
            try:
                val = convert_number(val)
                div = float(function[4:-1])
                val = val * div
            except ValueError:
                errDetail = 'wrong function definition'
        else:
            errDetail = 'wrong value type'
    elif function[:3] == 'add':
        # adds given value to current value
        if is_number(val):
            try:
                val = convert_number(val)
                div = float(function[4:-1])
                val = val + div
            except ValueError:
                errDetail = 'wrong function definition'
        else:
            errDetail = 'wrong value type'
    elif function[:3] == 'sub':
        # substracts given value from current value
        if is_number(val):
            gv = function[4:-1]
            # check for live KNX value
            if gv[:1] == '/':
                deviceInstance.readKNXAttribute("functions live value",
                                                gv, dpt)
            try:
                val = convert_number(val)
                val = val - float(gv)
            except ValueError:
                errDetail = 'wrong function definition'
        else:
            errDetail = 'wrong value type'
    elif function[:2] == 'lt':
        # checks if current value is less then given value
        if is_number(val):
            try:
                val = float(val) < float(function[3:-1])
            except ValueError:
                errDetail = 'wrong function definition'
        else:
            errDetail = 'wrong value type'
    elif function[:2] == 'gt':
        # checks if current value is greater then given value
        if is_number(val):
            try:
                val = float(val) > float(function[3:-1])
            except ValueError:
                errDetail = 'wrong function definition'
        else:
            errDetail = 'wrong value type'
    elif function[:6] == 'eqExcl':
        # checks if current value matches given value
        # in case of string values simply put the pattern into brackets without further escaping
        # example: eqExcl("Check against this string")
        # return only True if matching, otherwise None for no further processing
        if is_number(val):
            try:
                if float(val) == float(function[7:-1]):
                    val = True
                else:
                    val = None
            except ValueError:
                errDetail = 'wrong function definition'
        elif is_bool(val):
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
        if is_number(val):
            try:
                val = (float(val) == float(function[3:-1]))
            except ValueError:
                errDetail = 'wrong function definition'
        elif is_bool(val):
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
