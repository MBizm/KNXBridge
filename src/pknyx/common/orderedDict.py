# -*- coding: utf-8 -*-

""" Panohead remote control.

License
=======

 - This file is Copyright:
  - (C) 2006-2010 Igor Ghisi

B{Python Software Foundation License Version 2}

 1. This LICENSE AGREEMENT is between the Python Software Foundation
 ("PSF"), and the Individual or Organization ("Licensee") accessing and
 otherwise using this software ("Python") in source or binary form and
 its associated documentation.

 2. Subject to the terms and conditions of this License Agreement, PSF
 hereby grants Licensee a nonexclusive, royalty-free, world-wide
 license to reproduce, analyze, test, perform and/or display publicly,
 prepare derivative works, distribute, and otherwise use Python
 alone or in any derivative version, provided, however, that PSF's
 License Agreement and PSF's notice of copyright, i.e., "Copyright (c)
 2001, 2002, 2003, 2004, 2005, 2006 Python Software Foundation; All Rights
 Reserved" are retained in Python alone or in any derivative version
 prepared by Licensee.

 3. In the event Licensee prepares a derivative work that is based on
 or incorporates Python or any part thereof, and wants to make
 the derivative work available to others as provided herein, then
 Licensee hereby agrees to include in any such work a brief summary of
 the changes made to Python.

 4. PSF is making Python available to Licensee on an "AS IS"
 basis. PSF MAKES NO REPRESENTATIONS OR WARRANTIES, EXPRESS OR
 IMPLIED. BY WAY OF EXAMPLE, BUT NOT LIMITATION, PSF MAKES NO AND
 DISCLAIMS ANY REPRESENTATION OR WARRANTY OF MERCHANTABILITY OR FITNESS
 FOR ANY PARTICULAR PURPOSE OR THAT THE USE OF PYTHON WILL NOT
 INFRINGE ANY THIRD PARTY RIGHTS.

 5. PSF SHALL NOT BE LIABLE TO LICENSEE OR ANY OTHER USERS OF PYTHON
 FOR ANY INCIDENTAL, SPECIAL, OR CONSEQUENTIAL DAMAGES OR LOSS AS
 A RESULT OF MODIFYING, DISTRIBUTING, OR OTHERWISE USING PYTHON,
 OR ANY DERIVATIVE THEREOF, EVEN IF ADVISED OF THE POSSIBILITY THEREOF.

 6. This License Agreement will automatically terminate upon a material
 breach of its terms and conditions.

 7. Nothing in this License Agreement shall be deemed to create any
 relationship of agency, partnership, or joint venture between PSF and
 Licensee.  This License Agreement does not grant permission to use PSF
 trademarks or trade name in a trademark sense to endorse or promote
 products or services of Licensee, or any third party.

 8. By copying, installing or otherwise using Python, Licensee
 agrees to be bound by the terms and conditions of this License
 Agreement.

Module purpose
==============

Custom type

Implements
==========

- OrderedDict

From recipe ASPN N°496761

@author: Igor Ghisi
@author: Brodie Rao
@author: Frédéric Mantegazza
@copyright: (C) 2006-2010 Igor Ghisi
@license: PSF license v2
"""

__revision__ = "$Id$"

from UserDict import DictMixin


class OrderedDict(DictMixin):
    """ Ordered dict.
    """
    def __init__(self, data=None, **kwdata):
        self._keys = []
        self._data = {}
        if data is not None:
            if hasattr(data, 'items'):
                items = data.items()
            else:
                items = list(data)
            for i in xrange(len(items)):
                length = len(items[i])
                if length != 2:
                    raise ValueError('dictionary update sequence element '
                        '#%d has length %d; 2 is required' % (i, length))
                self._keys.append(items[i][0])
                self._data[items[i][0]] = items[i][1]
        if kwdata:
            self._merge_keys(kwdata.iterkeys())
            self.update(kwdata)

    def __setitem__(self, key, value):
        if key not in self._data:
            self._keys.append(key)
        self._data[key] = value

    def __getitem__(self, key):
        if isinstance(key, slice):
            result = [(k, self._data[k]) for k in self._keys[key]]
            return OrderedDict(result)
        return self._data[key]

    def __delitem__(self, key):
        del self._data[key]
        self._keys.remove(key)

    def __repr__(self):
        result = []
        for key in self._keys:
            result.append('(%s, %s)' % (repr(key), repr(self._data[key])))
        return ''.join(['OrderedDict', '([', ', '.join(result), '])'])

    def _merge_keys(self, keys):
        self._keys.extend(keys)
        newkeys = {}
        self._keys = [newkeys.setdefault(x, x) for x in self._keys
            if x not in newkeys]

    def update(self, data):
        if data is not None:
            if hasattr(data, 'iterkeys'):
                self._merge_keys(data.iterkeys())
            else:
                self._merge_keys(data.keys())
            self._data.update(data)

    def keys(self):
        return list(self._keys)

    def copy(self):
        copyDict = OrderedDict()
        copyDict._data = self._data.copy()
        copyDict._keys = self._keys[:]
        return copyDict
