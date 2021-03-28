# -*- coding: utf-8 -*-

""" Python KNX framework.

License
=======

 - B{pKNyX} (U{http://www.pknyx.org}) is Copyright:
  - (C) 2013 Frédéric Mantegazza

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
or see:

 - U{http://www.gnu.org/licenses/gpl.html}

Module purpose
==============

Logging service

Implements
==========

- B{DefaultFormatter}
- B{ColorFormatter}
- B{SpaceFormatter}
- B{SpaceColorFormatter}

@author: Frédéric Mantegazza
@copyright: (C) 2013 Frédéric Mantegazza
@license: GPL
"""

__revision__ = "$Id$"

import logging
import time
import sys
if sys.platform == 'win32':
    from ctypes import windll
    STD_INPUT_HANDLE = -10
    STD_OUTPUT_HANDLE = -11
    STD_ERROR_HANDLE = -12
    stderrHandle = windll.kernel32.GetStdHandle(STD_ERROR_HANDLE)
    stdoutHandle = windll.kernel32.GetStdHandle(STD_OUTPUT_HANDLE)
    setConsoleTextAttribute = windll.kernel32.SetConsoleTextAttribute


class DefaultFormatter(logging.Formatter):
    """ Default formatter
    """


class LinuxColorFormatter(DefaultFormatter):
    """ Colors for linux console.
    """
    colors = {'trace': "\033[0;36;40;22m",     # cyan/noir, normal
              'debug': "\033[0;36;40;1m",      # cyan/noir, gras
              'info': "\033[0;37;40;1m",       # blanc/noir, gras
              'warning': "\033[0;33;40;1m",    # jaune/noir, gras
              'error': "\033[0;31;40;1m",      # rouge/noir, gras
              'exception': "\033[0;35;40;1m",  # magenta/noir, gras
              'critical': "\033[0;37;41;1m",   # blanc/rouge, gras
              'default': "\033[0m",            # defaut
              }

    def _toColor(self, msg, levelname):
        """ Colorize.
        """
        if levelname == 'TRACE':
            color = LinuxColorFormatter.colors['trace']
        elif levelname == 'DEBUG':
            color = LinuxColorFormatter.colors['debug']
        elif  levelname in 'INFO':
            color = LinuxColorFormatter.colors['info']
        elif levelname == 'COMMENT':
            color = LinuxColorFormatter.colors['comment']
        elif levelname == 'PROMPT':
            color = LinuxColorFormatter.colors['prompt']
        elif levelname == 'WARNING':
            color = LinuxColorFormatter.colors['warning']
        elif levelname == 'ERROR':
            color = LinuxColorFormatter.colors['error']
        elif levelname == 'EXCEPTION':
            color = LinuxColorFormatter.colors['exception']
        elif levelname == 'CRITICAL':
            color = LinuxColorFormatter.colors['critical']
        else:
            color = LinuxColorFormatter.colors['default']

        return color + msg + LinuxColorFormatter.colors['default']

    def format(self, record):
        msg = DefaultFormatter.format(self, record)
        return self._toColor(msg, record.levelname)


class WindowsColorFormatter(DefaultFormatter):
    """ Colors for Windows console.
    """
    FOREGROUND_BLACK     = 0x0000
    FOREGROUND_BLUE      = 0x0001
    FOREGROUND_GREEN     = 0x0002
    FOREGROUND_CYAN      = 0x0003
    FOREGROUND_RED       = 0x0004
    FOREGROUND_MAGENTA   = 0x0005
    FOREGROUND_YELLOW    = 0x0006
    FOREGROUND_GREY      = 0x0007
    FOREGROUND_INTENSITY = 0x0008 # foreground color is intensified.

    BACKGROUND_BLACK     = 0x0000
    BACKGROUND_BLUE      = 0x0010
    BACKGROUND_GREEN     = 0x0020
    BACKGROUND_CYAN      = 0x0030
    BACKGROUND_RED       = 0x0040
    BACKGROUND_MAGENTA   = 0x0050
    BACKGROUND_YELLOW    = 0x0060
    BACKGROUND_GREY      = 0x0070
    BACKGROUND_INTENSITY = 0x0080 # background color is intensified.

    colors = {'trace': FOREGROUND_CYAN | BACKGROUND_BLACK,                                # cyan/noir, normal
              'debug': FOREGROUND_CYAN | BACKGROUND_BLACK | FOREGROUND_INTENSITY,         # cyan/noir, gras
              'info': FOREGROUND_GREY | BACKGROUND_BLACK | FOREGROUND_INTENSITY,          # blanc/noir, gras
              'warning': FOREGROUND_YELLOW | BACKGROUND_BLACK | FOREGROUND_INTENSITY,     # jaune/noir, gras
              'error': FOREGROUND_RED | BACKGROUND_BLACK | FOREGROUND_INTENSITY,          # rouge/noir, gras
              'exception': FOREGROUND_MAGENTA | BACKGROUND_BLACK | FOREGROUND_INTENSITY,  # magenta/noir, gras
              'critical': FOREGROUND_GREY | BACKGROUND_RED | FOREGROUND_INTENSITY,        # blanc/rouge, gras
              'default': FOREGROUND_GREY | BACKGROUND_BLACK,                              # defaut
              }

    def _setTextAttribute(self, color):
        """ Sets the character attributes (colors).

        Color is a combination of foreground and background color, foreground and background intensity.
        """
        setConsoleTextAttribute(stderrHandle, color)

    def _toColor(self, msg, levelname):
        """ Colorize.
        """
        if levelname == 'TRACE':
            self._setTextAttribute(WindowsColorFormatter.colors['trace'])
        elif levelname == 'DEBUG':
            self._setTextAttribute(WindowsColorFormatter.colors['debug'])
        elif  levelname == 'INFO':
            self._setTextAttribute(WindowsColorFormatter.colors['info'])
        elif levelname == 'WARNING':
            self._setTextAttribute(WindowsColorFormatter.colors['warning'])
        elif levelname == 'ERROR':
            self._setTextAttribute(WindowsColorFormatter.colors['error'])
        elif levelname == 'EXCEPTION':
            self._setTextAttribute(WindowsColorFormatter.colors['exception'])
        elif levelname == 'CRITICAL':
            self._setTextAttribute(WindowsColorFormatter.colors['critical'])
        else:
            self._setTextAttribute(WindowsColorFormatter.colors['default'])

        return msg

    def format(self, record):
        msg = DefaultFormatter.format(self, record)
        return self._toColor(msg, record.levelname)


class SpaceFormatter(DefaultFormatter):
    """ Format with newlines
    """
    def __init__(self, *args, **kwargs):
        super(SpaceFormatter, self).__init__(*args, **kwargs)

        self._lastLogTime = time.time()

    def _addSpace(self, msg):
        """ Add newlines

        Compute number of newlines according to delay from last log.

        @todo: does not work if multiple handlers use this formatter
        """
        if time.time() - self._lastLogTime > 3600:
            space = "\n\n\n"
        elif time.time() - self._lastLogTime > 60:
            space = "\n\n"
        elif time.time() - self._lastLogTime > 3:
            space = "\n"
        else:
            space = ""
        self._lastLogTime = time.time()

        return space + msg

    def format(self, record):
        msg = DefaultFormatter.format(self, record)
        return self._addSpace(msg)


class LinuxSpaceColorFormatter(SpaceFormatter, LinuxColorFormatter):
    """ Linux formatter with colors and newlines
    """
    def format(self, record):
        msg = SpaceFormatter.format(self, record)
        return self._toColor(msg, record.levelname)


class WindowsSpaceColorFormatter(SpaceFormatter, WindowsColorFormatter):
    """ Windows formatter with colors and newlines
    """
    def format(self, record):
        msg = SpaceFormatter.format(self, record)
        return self._toColor(msg, record.levelname)


if sys.platform in ('linux2', 'darwin'):
    ColorFormatter = LinuxColorFormatter
    SpaceColorFormatter = LinuxSpaceColorFormatter
elif sys.platform == 'win32':
    ColorFormatter = WindowsColorFormatter
    SpaceColorFormatter = WindowsSpaceColorFormatter
else:
    # raise ValueError("Unsupported platform '%s'" % sys.platform)
    ColorFormatter = LinuxColorFormatter
    SpaceColorFormatter = LinuxSpaceColorFormatter
