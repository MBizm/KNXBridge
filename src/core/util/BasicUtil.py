import os
from datetime import datetime
from pathlib import Path
from typing import Dict

import yaml

### verbosity mask
VERBOSITYDEF: Dict[str, int] = {
    "off": 0x00,
    "error": 0x01,
    "warning": 0x03,
    "change": 0x07,
    "info": 0xFF
}

__verbosity = VERBOSITYDEF['error']

HOMEDIR = "{0}/.knx/bridge/".format(Path.home())


def setLogLevel(level):
    global __verbosity
    __verbosity = VERBOSITYDEF[level]


def log(level, msg):
    """ logging functionality for KNX Bridge """
    global __verbosity
    logPath = HOMEDIR + ".log"

    # create central directory for Daemon script
    if not os.path.isdir(HOMEDIR):
        Path(HOMEDIR).mkdir(parents=True, exist_ok=True)
    # check activated log level
    # TODO switch to logging.handlers.RotatingFileHandler for size restriction
    if __verbosity & VERBOSITYDEF[level] == VERBOSITYDEF[level]:
        with open(logPath, 'a+') as stream:
            stream.write("{0} ###\t{1}\t###: {2}\n".format(datetime.now().strftime("%d.%b. %I:%M:%S"),
                                                           level.upper(),
                                                           msg))


def readConfig():
    """
    reads configuration for KNX Bridge.
    First attempt will be from home directory, otherwise local config as part of src repo will be taken

    :return: configuration in yaml representation or None if not found
    """
    configuration = None
    configPath = HOMEDIR + "CONFIG.yaml"

    try:
        if os.path.isfile(configPath):
            with open(configPath, 'r') as stream:
                log('info', 'Configuration file loaded: {0}'.format(configPath))
                configuration = yaml.safe_load(stream)
        else:
            with open("../CONFIG.yaml", 'r') as stream:
                log('info', 'Configuration file loaded: ../CONFIG.yaml')
                configuration = yaml.safe_load(stream)
    except OSError as ex:
        log('error',
            'Could not load configuration file [{0}]'.format(ex))

    return configuration


def getAttrSafe(attr, key):
    """
    fails safely for accessing optional parameters
    :returns    value defined for key or None if undefined
    """
    ret = None

    if key in attr:
        ret = attr[key]

    return ret

#################################
#   Numeric helper methods      #
#################################
def is_number(val):
    if isinstance(val, (int, float)):
        return True
    elif isinstance(val, list):
        return False
    else:
        try:
            float(val)
            return True
        except ValueError or TypeError:
            return False
    return False


def is_bool(val):
    if isinstance(val, bool):
        return True
    elif isinstance(val, str) and (
            val.lower() == "true" or val.lower() == "false"):
        return True
    return False

def convert_number(val):
    if isinstance(val, str):
        if val.isdigit():
            val = int(val)
        else:
            val = float(val)
    return val

def convert_bool(val):
    if val.lower() == "true":
        return True
    elif val.lower() == "false":
        return False
    else:
        return bool(val)
    
def convert_val2xy(val):
    # covnerts rgb color representation to xy coordinates
    # https://stackoverflow.com/questions/22564187/val-to-philips-hue-hsb
    X = float(val[0] * 0.649926 + val[1] * 0.103455 + val[2] * 0.197109)
    Y = float(val[0] * 0.234327 + val[1] * 0.743075 + val[2] * 0.022598)
    Z = float(val[0] * 0.0000000 + val[1] * 0.053077 + val[2] * 1.035763)

    if (X + Y + Z) == 0:
        return [float(0), float(0)]

    return [float(X / (X + Y + Z)),
            float(Y / (X + Y + Z))]

def convert_oct2int(val):
    # catch erroneous state - to be investigated
    if len(val) < 4:
        log("error",
            "Wrong value for oct2int conversion (must be 4 tuples): " + str(val))
        return int(str(0), 16)

    # converts a tuplet of 4 values (where last 2 represent the octet decimal and base into into
    # https://stackoverflow.com/questions/35450560/how-to-use-python-to-convert-an-octal-to-a-decimal
    a = int(val[3]) # decimal
    d = int(val[2]) # base
    b = ""
    while a != 0:
        x = '0123456789ABCDEF'
        c = a % d
        if c > 15:
            c = c % 15
        c1 = x[c]
        b = str(c1) + b
        a = int(a // d)
    return int(b, 16)