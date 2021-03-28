# -*- coding: utf-8 -*-

"""

License
=======

Module purpose
==============

Custom exceptions

Implements
==========

 - PKNyXError
 - HardwareError
 - KNXFormatError
 - OutOfLimitsError

@author: Frédéric Mantegazza
@copyright: (C) 2013 Frédéric Mantegazza
@license: GPL
"""

__revision__ = "$Id$"


class PKNyXError(Exception):
    """ Base class for pKNyX errors
    """


class PKNyXValueError(PKNyXError):
    """ Base class for pKNyX value errors
    """

class PKNyXAttributeError(PKNyXError):
    """ Base class for pKNyX attribute errors
    """