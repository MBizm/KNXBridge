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

Sun position management

Implements
==========

 - B{Sun}

Documentation
=============

Usage
=====

@author: Frédéric Mantegazza
@copyright: (C) 2013 Frédéric Mantegazza
@license: GPL
"""

__revision__ = "$Id$"

import sys
import math
import time

from pknyx.common.utils import dd2dms, dms2dd


class Sun(object):
    """ Sun behaviour class.
    """
    def __init__(self, latitude, longitude, timeZone, savingTime):
        """ Init the Sun object.
        """
        super(Sun, self).__init__()

        self._latitude = latitude
        self._longitude = longitude
        self._timeZone = timeZone
        self._savingTime = savingTime

    @property
    def latitude(self):
        self._latitude

    @latitude.setter
    def latitude(self, latitude):
        self._latitude = latitude

    @property
    def longitude(self):
        self._longitude

    @longitude.setter
    def longitude(self, longitude):
        self._longitude = longitude

    @property
    def timeZone(self):
        self._timeZone

    @latitude.setter
    def timeZone(self, timeZone):
        self._timeZone = timeZone

    @property
    def savingTime(self):
        self._savingTime

    @savingTime.setter
    def savingTime(self, savingTime):
        self._savingTime = savingTime

    def computeJulianDay(self, year, month, day, hour, minute, second):
        """ Compute the julian day.
        """
        day += hour / 24. + minute / 1440. + second / 86400.

        if month in (1, 2):
            year -= 1
            month += 12

        a = int(year / 100.)
        b = 2 - a + int(a / 4.)

        julianDay = int(365.25 * (year + 4716.)) + int(30.6001 * (month + 1)) + day + b - 1524.5
        julianDay -= (self._timeZone + self._savingTime) / 24.
        julianDay -= 2451545.  # ???!!!???

        return julianDay

    def siderealTime(self, julianDay):
        """ Compute the sidereal time.
        """
        centuries = julianDay / 36525.
        siderealTime = (24110.54841 + (8640184.812866 * centuries) + (0.093104 * (centuries ** 2)) - (0.0000062 * (centuries ** 3))) / 3600.
        siderealTime = ((siderealTime / 24.) - int(siderealTime / 24.)) * 24.

        return siderealTime

    def equatorialCoordinates(self, year, month, day, hour, minute, second):
        """ Compute rightAscension and declination.
        """
        julianDay =  self.computeJulianDay(year, month, day, hour, minute, second)

        g = 357.529 + 0.98560028 * julianDay
        q = 280.459 + 0.98564736 * julianDay
        l = q + 1.915 * math.sin(math.radians(g)) + 0.020 * math.sin(math.radians(2 * g))
        e = 23.439 - 0.00000036 * julianDay
        rightAscension = math.degrees(math.atan(math.cos(math.radians(e)) * math.sin(math.radians(l)) / math.cos(math.radians(l)))) / 15.
        if math.cos(math.radians(l)) < 0.:
            rightAscension += 12.
        if math.cos(math.radians(l)) > 0. and math.sin(math.radians(l)) < 0.:
            rightAscension += 24.

        declination = math.degrees(math.asin(math.sin(math.radians(e)) * math.sin(math.radians(l))))

        return rightAscension, declination

    def azimuthalCoordinates(self, year, month, day, hour, minute, second):
        """ Compute elevation and azimuth.
        """
        julianDay =  self.computeJulianDay(year, month, day, hour, minute, second)
        siderealTime = self.siderealTime(julianDay)
        angleH = 360. * siderealTime / 23.9344
        angleT = (hour - (self._timeZone + self._savingTime) - 12. + minute / 60. + second / 3600.) * 360. / 23.9344
        angle = angleH + angleT
        rightAscension, declination = self.equatorialCoordinates(year, month, day, hour, minute, second)
        angle_horaire = angle - rightAscension * 15. + self._longitude

        elevation = math.degrees(math.asin(math.sin(math.radians(declination)) * math.sin(math.radians(self._latitude)) - math.cos(math.radians(declination)) * math.cos(math.radians(self._latitude)) * math.cos(math.radians(angle_horaire))))

        azimuth = math.degrees(math.acos((math.sin(math.radians(declination)) - math.sin(math.radians(self._latitude)) * math.sin(math.radians(elevation))) / (math.cos(math.radians(self._latitude)) * math.cos(math.radians(elevation)))))
        sinazimuth = (math.cos(math.radians(declination)) * math.sin(math.radians(angle_horaire))) / math.cos(math.radians(elevation))
        if (sinazimuth < 0.):
            azimuth = 360. - azimuth

        return elevation, azimuth

    def generateAzimuthal(self, year, month, day, step=3600):
        """ Generate azimuthl coordinates for all day.

        @param step: step generation (s)
        @type step: int

        @return: azimuthl coordinates for all day
        @rtype: list of (elevation, azimuth) tuples
        """
        coords = []
        for second in xrange(0, 3600 * 24, step):
            h = int(second / 3600.)
            m = int((second - h * 3600.) / 60.)
            s = int(second - h * 3600. - m * 60.)
            elevation, azimuth = self.azimuthalCoordinates(year, month, day, h, m, s)
            coords.append((elevation, azimuth))

        return coords


def main():
    sun = Sun(latitude=45., longitude=5., timeZone=1, savingTime=1)

    # Get curent date/time
    if len(sys.argv) == 5:
        tm_year = int(sys.argv[1])
        tm_mon = int(sys.argv[2])
        tm_day = int(sys.argv[3])
        tm_hour = int(sys.argv[4])
        tm_min, tm_sec = 0, 0
    else:
        tm_year, tm_mon, tm_day, tm_hour, tm_min, tm_sec, tm_wday, tm_yday, tm_isdst = time.localtime()
        print u"Date/hour        : %s" % time.ctime()

    # Compute julian day
    julianDay =  sun.computeJulianDay(tm_year, tm_mon, tm_day, tm_hour, tm_min, tm_sec)
    print u"Julian day       : %14.6f" % julianDay

    # Compute Sidereal time
    siderealTime = sun.siderealTime(julianDay)
    print u"Sidereal time    : %.6f" % siderealTime
    print

    # Compute equatorial coordinates
    rightAscension, declination = sun.equatorialCoordinates(tm_year, tm_mon, tm_day, tm_hour, tm_min, tm_sec)
    d, m, s = dd2dms(rightAscension)
    print u"Right ascension  : %10.6f° (%3d°%02d'%06.3f\")" % (rightAscension, d, m, s)
    d, m, s = dd2dms(declination)
    print u"Declination      : %10.6f° (%3d°%02d'%06.3f\")" % (declination, d, m, s)
    print

    # Compute azimuthal coordinates
    elevation, azimuth = sun.azimuthalCoordinates(tm_year, tm_mon, tm_day, tm_hour, tm_min, tm_sec)
    d, m, s = dd2dms(elevation)
    print u"Elevation        : %10.6f° (%3d°%02d'%06.3f\")" % (elevation, d, m, s)
    d, m, s = dd2dms(azimuth)
    print u"Azimuth          : %10.6f° (%3d°%02d'%06.3f\")" % (azimuth, d, m, s)

    from math import cos, sin, radians
    print
    print cos(radians(azimuth - 90)) * cos(radians(elevation));
    print sin(radians(azimuth - 90)) * cos(radians(elevation));
    print sin(radians(elevation));
    print


if __name__ == "__main__":
    main()
