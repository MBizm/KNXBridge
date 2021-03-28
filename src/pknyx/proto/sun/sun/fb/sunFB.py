# -*- coding: utf-8 -*-

import time

from pknyx.api import FunctionalBlock
from pknyx.api import logger, schedule, notify

import sun


class SunFB(FunctionalBlock):

    # Datapoints definition
    DP_01 = dict(name="right_ascension", access="output", dptId="14.007", default=0.)
    DP_02 = dict(name="declination", access="output", dptId="14.007", default=0.)
    DP_03 = dict(name="elevation", access="output", dptId="14.007", default=0.)
    DP_04 = dict(name="azimuth", access="output", dptId="14.007", default=0.)
    DP_05 = dict(name="latitude", access="param", dptId="14.007", default=0.)
    DP_06 = dict(name="longitude", access="param", dptId="14.007", default=0.)
    DP_07 = dict(name="time_zone", access="param", dptId="8.007", default=1)
    DP_08 = dict(name="saving_time", access="param", dptId="1.xxx", default=1)

    GO_01 = dict(dp="right_ascension", flags="CRT", priority="low")
    GO_02 = dict(dp="declination", flags="CRT", priority="low")
    GO_03 = dict(dp="elevation", flags="CRT", priority="low")
    GO_04 = dict(dp="azimuth", flags="CRT", priority="low")
    GO_05 = dict(dp="latitude", flags="CWU", priority="low")
    GO_06 = dict(dp="longitude", flags="CWU", priority="low")
    GO_07 = dict(dp="time_zone", flags="CWU", priority="low")
    GO_08 = dict(dp="saving_time", flags="CWU", priority="low")

    DESC = "Sun position management FB"

    def _init(self):
        """ Additionnal init of our functional block
        """
        self._sun = sun.Sun(latitude=self.dp["latitude"].value,
                            longitude = self.dp["longitude"].value,
                            timeZone = self.dp["time_zone"].value,
                            savingTime = self.dp["saving_time"].value)

    def _update(self, event=None):
        """ Update sun position
        """

        # Read inputs/params
        self._sun.latitude = self.dp["latitude"].value
        self._sun.longitude = self.dp["longitude"].value
        self._sun.timeZone = self.dp["time_zone"].value
        self._sun.savingTime = self.dp["saving_time"].value

        # Computations
        tm_year, tm_mon, tm_day, tm_hour, tm_min, tm_sec, tm_wday, tm_yday, tm_isdst = time.localtime()

        rightAscension, declination = self._sun.equatorialCoordinates(tm_year, tm_mon, tm_day, tm_hour, tm_min, tm_sec)
        elevation, azimuth = self._sun.azimuthalCoordinates(tm_year, tm_mon, tm_day, tm_hour, tm_min, tm_sec)

        #logger.info("right_ascension=%f, declination=%f, elevation=%f, azimuth=%f" % \
                      #(rightAscension, declination, elevation, azimuth))

        # Write outputs
        self.dp["right_ascension"].value = rightAscension
        self.dp["declination"].value = declination
        self.dp["elevation"].value = elevation
        self.dp["azimuth"].value = azimuth

    @schedule.every(minutes=5)
    def updatePosition(self):
        """ This method will be triggered every 5 minutes
        """
        self._update()

    @notify.datapoint(dp="latitude", condition="change")
    @notify.datapoint(dp="longitude", condition="change")
    @notify.datapoint(dp="time_zone", condition="change")
    @notify.datapoint(dp="saving_time", condition="change")
    def updateConditions(self, event):
        """ This method will be trigger when some datapoints change.
        """
        self._update()