import re
from collections import deque
from datetime import datetime, timedelta, timezone

import dateparser as dateparser

from threading import Timer
from core.util.BasicUtil import log, is_number, convert_number, is_bool, convert_bool, convert_val2xy, convert_oct2int, NoneValueClass

queueList = {}

def executeFunction(deviceInstance, dpt, function, val,
                    attrName, knxDest, knxFormat):
    """
    performs the selected functions val and returns the outcome. functions can be chained by givign a comma
    or semicolon separated list being processed from left to right
    :param deviceInstance:      KNXDDevice instance for knx value callbacks, type hint not specified due to import loop
    :param dpt:                 data point type of value
    :param function:            function to be applied on value
    :param val:                 val from external source
    :param attrName:            textual description of val context
    :param knxDest:             destination for value
    :param knxFormat:           string representation of target format
    :returns val of corresponding type after function execution
    """
    if not function:
        return val

    # check for appearance of a function list (function separated by comma or semicolon)
    # sample used for evaluation 'max(10),av(1,5),min(),hu('abc';56),oh([34/54/67]),(),async(59,val(false)),())'
    regex = r"([a-zA-Z0-9_-]+\(.*?\)+)[,;]?"
    functionStatements = re.findall(regex, function)
    for f in functionStatements:
        if type(val) != NoneValueClass:
            val = __executeFunctionImpl(deviceInstance, dpt, f, val,
                                        attrName, knxDest, knxFormat)

    return val


def _asynchWrite(deviceInstance, attrName, knxDest, knxFormat, val):
    # called by asynchronous thread by function definition
    deviceInstance.writeKNXAttribute(attrName, knxDest, knxFormat, val)


def __executeFunctionImpl(deviceInstance, dpt, function, val,
                          attrName, knxDest, knxFormat):
    global queueList
    errDetail = None

    if function[:3] == 'val':
        # replace current value by static value
        try:
            val = function[4:-1]
            if is_number(val):
                val = float(val)
            elif is_bool(val):
                val = convert_bool(val)
        except ValueError:
            val = function[4:-1]
    elif function[:3] == 'inv':
        # invert current value - restricted to boolean currently
        if is_bool(val):
            # generic 0/1 representation required for dpxlator DPT conversion
            val = not val
        # check for legitim None value
        elif type(val) is NoneValueClass:
            pass # do nothing
        else:
            errDetail = 'wrong value type'
    elif function[:3] == 'max':
        # returns the greater value, useful for greater 0 assurancce
        if is_number(val):
            try:
                val = convert_number(val)
                val = max(val, float(function[4:-1]))
            except ValueError:
                errDetail = 'wrong function definition'
        else:
            errDetail = 'wrong value type'
    elif function[:3] == 'min':
        # returns the lower value
        if is_number(val):
            try:
                val = convert_number(val)
                val = min(val, float(function[4:-1]))
            except ValueError:
                errDetail = 'wrong function definition'
        else:
            errDetail = 'wrong value type'
    elif function[:3] == 'rnd':
        # rounds the current value to the given precision
        if is_number(val):
            try:
                val = convert_number(val)
                val = round(val, float(function[4:-1]))
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
            if '/' in gv:
                gv = deviceInstance.readKNXAttribute("functions live value",
                                                gv, knxFormat)
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
    elif function[:5] == 'avMax':
        # returns the max value for a queue of values
        # queue values are dropped sequentially when capacity is hit
        par = re.split("[,;]", function[3:-1])
        # split function parameter - av(<queueID>,<FIFOsize>)
        queueID = str(par[0])
        # check existing of queueID and save current value
        if not queueID in queueList:
            # optional definition of queue size, e.g. multiple references to the same queue
            if (len(par) > 1):
                queueSize = int(par[1])
            else:
                # arbitrary value
                queueSize = 10
            queueList[queueID] = deque(maxlen=queueSize)
        queue = queueList[queueID]

        if is_number(val):
            queue.append(float(val))
            # identify max value
            for i in queue:
                val = max(val, i)
        elif is_bool(val):
            queue.append(bool(val))
            # identify false/true maximum
            val = False
            for i in queue:
                if i:
                    val = True
                    break
        elif type(val) == str and \
            (val == 'Off' or val == 'On'):
            # perform avMax execution by recursive call
            if val == 'Off':
                val = __executeFunctionImpl(deviceInstance, dpt, function, False,
                                            attrName, knxDest, knxFormat)
            else:
                val = __executeFunctionImpl(deviceInstance, dpt, function, True,
                                            attrName, knxDest, knxFormat)
            # perform backward mapping to On/Off value
            if val:
                val = 'On'
            else:
                val = 'Off'
        else:
            errDetail = 'wrong value type'
    elif function[:5] == 'avMin':
        # returns the min value for a queue of values
        # queue values are dropped sequentially when capacity is hit
        par = re.split("[,;]", function[3:-1])
        # split function parameter - av(<queueID>,<FIFOsize>)
        queueID = str(par[0])
        # check existing of queueID and save current value
        if not queueID in queueList:
            # optional definition of queue size, e.g. multiple references to the same queue
            if (len(par) > 1):
                queueSize = int(par[1])
            else:
                # arbitrary value
                queueSize = 10
            queueList[queueID] = deque(maxlen=queueSize)
        queue = queueList[queueID]

        if is_number(val):
            queue.append(float(val))
            # identify min value
            for i in queue:
                val = min(val, i)
        elif is_bool(val):
            queue.append(bool(val))
            # identify false/true minimum
            val = True
            for i in queue:
                if not i:
                    val = False
                    break
        elif type(val) == str and \
                (val == 'Off' or val == 'On'):
            # perform avMin execution by recursive call
            if val == 'Off':
                val = __executeFunctionImpl(deviceInstance, dpt, function, False,
                                            attrName, knxDest, knxFormat)
            else:
                val = __executeFunctionImpl(deviceInstance, dpt, function, True,
                                            attrName, knxDest, knxFormat)
            # perform backward mapping to On/Off value
            if val:
                val = 'On'
            else:
                val = 'Off'
        else:
            errDetail = 'wrong value type'
    elif function[:2] == 'av':
        # returns the average value for a queue of values
        # queue values are dropped sequentially when capacity is hit
        par = re.split("[,;]", function[3:-1])
        # split function parameter - av(<queueID>,<FIFOsize>)
        queueID = str(par[0])
        # check existing of queueID and save current value
        if not queueID in queueList:
            # optional definition of queue size, e.g. multiple references to the same queue
            if (len(par) > 1):
                queueSize = int(par[1])
            else:
                # arbitrary value
                queueSize = 10
            queueList[queueID] = deque(maxlen=queueSize)
        queue = queueList[queueID]

        if is_number(val):
            queue.append(float(val))
            # calculate average
            sum = 0
            for i in queue:
                sum = sum + i
            val = sum / len(queue)
        else:
            errDetail = 'wrong value type'
    elif function[:6] == 'eqExcl':
        # checks if current value matches given value
        # in case of string values simply put the pattern into brackets without further escaping
        # example: eqExcl("Check against this string")
        # return only True if matching, otherwise None for no further processing
        # check for live KNX value
        gv = function[7:-1]
        if '/' in gv:
            gv = deviceInstance.readKNXAttribute("functions live value",
                                                 gv, knxFormat)
        # start comparison
        if is_number(val):
            try:
                if float(val) == convert_number(float(gv)):
                    val = True
                else:
                    # indicate legitim None value
                    val = NoneValueClass()
            except ValueError:
                errDetail = 'wrong function definition'
        elif is_bool(val):
            try:
                if convert_bool(val) == convert_bool(gv):
                    val = True
                else:
                    # indicate legitim None value
                    val = NoneValueClass()
            except ValueError:
                errDetail = 'wrong function definition'
        elif type(val) == str:
            try:
                if str(val) == str(gv):
                    val = True
                else:
                    # indicate legitim None value
                    val = NoneValueClass()
            except ValueError:
                errDetail = 'wrong function definition'
        else:
            errDetail = 'wrong value type'
    elif function[:2] == 'eq':
        # checks if current value matches given value, return either true or false
        # check for live KNX value
        gv = function[3:-1]
        if '/' in gv:
            gv = deviceInstance.readKNXAttribute("functions live value",
                                                 gv, knxFormat)
        # start comparison
        if is_number(val):
            try:
                val = (float(val) == convert_number(float(gv)))
            except ValueError:
                errDetail = 'wrong function definition'
        elif is_bool(val):
            try:
                val = (convert_bool(val) == convert_bool(gv))
            except ValueError:
                errDetail = 'wrong function definition'
        elif type(val) == str:
            try:
                val = (str(val) == str(gv))
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
    elif function[:6] == 'asynch':
        # asynchronous method call with not interfere with current execution
        # but it will start another thread after defined duration with defined value as function
        # syntax: asynch(<duration in sec> <function call>)
        # important: use blank as separator not comma or semicolon!
        # examples: asynch(60 val(true))
        try:
            tok = re.split("[,;]", function[7:-1])
            duration = tok[0]
            func = tok[1]
            asynchVal = executeFunction(deviceInstance,
                                      dpt, func, val,
                                      attrName, knxDest, knxFormat)
            Timer(int(duration), _asynchWrite, kwargs={"deviceInstance": deviceInstance,
                                                       "attrName": attrName,
                                                       "knxDest": knxDest,
                                                       "knxFormat": knxFormat,
                                                       "val": asynchVal
                                                       }).start()
        except Exception as e:
            errDetail = 'Could not start asynchronous function - ' + str(e)
    elif function[:8] == 'rgb_2_xy':
        # converts an rgb list into a xy coordinate list
        try:
            val = convert_val2xy(val)
        except TypeError as e:
            errDetail = 'Wrong value for color transformation'
    elif function[:9] == 'oct_2_int':
        oldVal = val
        val = convert_oct2int(val)
    if errDetail:
        log('error',
            'Could not apply function "{0}" to value {1} - {2}'.format(function,
                                                                       val,
                                                                       errDetail))
    return val
