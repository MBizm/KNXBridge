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

Implements
==========

 - B{FrozenDict}
 - B{FrozenDictAttributeError}

Documentation
=============

Usage
=====

@author: Oren Tirosh
@copyright: (C) 2005 Oren Tirosh
@license: PSF License
"""

__revision__ = "$Id$"

from pknyx.common.exception import PKNyXAttributeError


class FrozenDictAttributeError(PKNyXAttributeError):
    """
    """


class FrozenDict(dict):
    """ Read-only dict

    Created by U{Oren Tirosh<http://code.activestate.com/recipes/users/2033964>}
    See: U{http://code.activestate.com/recipes/414283}
    """

    @property
    def _blocked(obj):
        raise FrozenDictAttributeError("A FrozenDict cannot be modified")

    __delitem__ = __setitem__ = _blocked
    pop = popitem = setdefault = update = clear = _blocked

    def __new__(cls, *args, **kwargs):
        new = dict.__new__(cls)
        dict.__init__(new, *args, **kwargs)
        return new

    def __init__(self, *args, **kwargs):
        pass

    def __hash__(self):
        try:
            return self._cachedHash
        except AttributeError:
            h = self._cachedHash = hash(tuple(sorted(self.items())))
            return h

    def __repr__(self):
        return "FrozenDict(%s)" % dict.__repr__(self)
