# -*- coding: utf-8 -*-

""" Python KNX framework

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

Configuration management.

Implements
==========

- ConfigManager

@author: Frédéric Mantegazza
@copyright: (C) 2013 Frédéric Mantegazza
@license: GPL
"""

__revision__ = "$Id$"

import sys
import os.path
import shutil
import sets

from pknyx.common import config
from pknyx.common.utils import isOdd
from pknyx.services.logger import Logger

if hasattr(sys, "frozen"):
    path = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), config.APP_NAME.lower(), "common")
else:
    path = os.path.dirname(__file__)
configManager = None


class ConfigManagerObject(object):
    """ Configuration manager.
    """
    def __init__(self):
        """ Init the object.
        """
        super(ConfigManagerObject, self).__init__()

        self.__config = None
        self.__install = False
        self.__saved = False

    def load(self):
        """ Load configuration.
        """

        #Load dist config.
        distConfigFile = os.path.join(path, config.CONFIG_FILE)
        distConfig = QtCore.QSettings(distConfigFile, QtCore.QSettings.IniFormat)
        if not distConfig.contains('CONFIG_VERSION'):
            raise IOError("Can't read configuration file (%s)" % distConfigFile)

        # Check if user config. exists, or need to be updated/overwritten
        distConfigVersion = config.VERSION.split('.')
        userConfig = QtCore.QSettings(config.USER_CONFIG_FILE, QtCore.QSettings.IniFormat)
        if not userConfig.contains('CONFIG_VERSION'):
            self.__install = True
        else:
            userConfigVersion = unicode(userConfig.value('CONFIG_VERSION').toString()).split('.')
            Logger().debug("ConfigManager.__init__(): versions: dist=%s, user=%s" % (distConfigVersion, userConfigVersion))

            # Old versioning system
            if len(userConfigVersion) < 2:
                self.__install = True

            # Versions differ
            elif distConfigVersion != userConfigVersion:
                self.__install = True

        if self.__install:
            Logger().debug("ConfigManager.__init__(): install user config.")
            shutil.copy(distConfigFile, config.USER_CONFIG_FILE)

            # Set config. version
            userConfig.setValue('CONFIG_VERSION', QtCore.QVariant("%s" % '.'.join(distConfigVersion)))

            # Write user config.
            userConfig.sync()

        else:
            Logger().debug("ConfigManager.__init__(): user config. is up-to-date")

        self.__config = userConfig

    def save(self):
        """ Save config.

        Config is saved in user directory. Preferences are first
        set back to config.
        """
        self.__config.sync()
        self.__saved = True
        Logger().debug("Configuration saved")

    def isConfigured(self):
        """ Check if configuration has been set by user.
        """
        if self.__install and not self.__saved:
            return False
        else:
            return True

    def contains(self, key):
        """ Check if the config contains the given section/option.

        @param key: config key
        @type key: str
        """
        return self.__config.contains(key)

    def _check(self, key):
        """ Check if the config contains the given section/option.

        @param key: config key
        @type key: str
        """
        if not self.contains(key):
            raise KeyError("ConfigManager does not contain key '%s'" % key)

    def get(self, key):
        """ Get a str value.

        @param key: config key
        @type key: str
        """
        self._check(key)
        return unicode(self.__config.value(key).toString())

    def getInt(self, key):
        """ Get an int value.

        @param key: config key
        @type key: str
        """
        self._check(key)
        value, flag = self.__config.value(key).toInt()
        if flag:
            return value
        else:
            raise ValueError("ConfigManager can't get key '%s' as int" % key)

    def getFloat(self, key):
        """ Get a float value.

        @param key: config key
        @type key: str
        """
        self._check(key)
        value, flag = self.__config.value(key).toDouble()
        if flag:
            return value
        else:
            raise ValueError("ConfigManager can't get key '%s' as float" % key)

    def getBoolean(self, key):
        """ Get a boolean value.

        @param key: config key
        @type key: str
        """
        self._check(key)
        return self.__config.value(key).toBool()

    def set(self, key, value):
        """ Set a value as str.

        @param key: config key
        @type key: str

        @param value: value to set
        @type value: str
        """
        self.__config.setValue(key, QtCore.QVariant(value))
        self.__saved = False

    def setInt(self, key, value):
        """ Set a value as int.

        @param key: config key
        @type key: str

        @param value: value to set
        @type value: int
        """
        self.__config.setValue(key, QtCore.QVariant(value))
        self.__saved = False

    def setFloat(self, key, value, prec):
        """ Set a value as float.

        @param key: config key
        @type key: str

        @param value: value to set
        @type value: float

        @param prec: precision
        @type prec: int
        """
        #value = ("%(format)s" % {'format': "%%.%df" % prec}) % value
        self.__config.setValue(key, QtCore.QVariant(value))
        self.__saved = False

    def setBoolean(self, key, value):
        """ Set a value as boolean.

        @param key: config key
        @type key: str

        @param value: value to set
        @type value: str
        """
        self.__config.setValue(key, QtCore.QVariant(value))
        self.__saved = False


# ConfigManager factory
def ConfigManager():
    global configManager
    if configManager is None:
        configManager = ConfigManagerObject()

    return configManager
