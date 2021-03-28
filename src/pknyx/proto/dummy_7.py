# -*- coding: utf-8 -*-

import math
import time

from pknyx.common.utils import dd2dms, dms2dd

from pknyx.api import Logger
from pknyx.api import FunctionalBlock, Stack, ETS
from pknyx.api import Scheduler  #, Notifier

# ETS maps -> Group Object Association Table (GrOAT)
# @todo: make a tool to import from ETS
GAD_MAP = {"1": dict(name="heat", desc="Chauffage"),
           "1/1": dict(name="heat_setpoint", desc="Consigne"),
           "1/1/1": dict(name="heat_setpoint_living", desc="Salle à Manger"),
           "1/1/2": dict(name="heat_setpoint_bedroom_1", desc="Chambre 1"),
           "1/1/3": dict(name="heat_setpoint_bedroom_2", desc="Chambre 2"),
           "1/1/4": dict(name="heat_setpoint_bedroom_3", desc="Chambre 3"),
           "1/2": dict(name="heat_temperature", desc="Température"),
           "1/2/1": dict(name="heat_temperature_living", desc="Salle à Manger"),
           "1/2/2": dict(name="heat_temperature_bedroom_1", desc="Chambre 1"),
           "1/2/3": dict(name="heat_temperature_bedroom_2", desc="Chambre 2"),
           "1/2/4": dict(name="heat_temperature_bedroom_3", desc="Chambre 3"),
           "2": dict(name="light", desc="Lumière"),
           "2/1": dict(name="light_command", desc="Commande"),
           "2/2": dict(name="light_state", desc="État"),
           "2/2/1": dict(name="light_state_living", desc="Salle à Manger"),
           "2/2/2": dict(name="light_state_bedroom_1", desc="Chambre 1"),
          }

#BUILDING_MAP = {
               #}

stack = Stack(individualAddress="1.2.3")
ets = ETS(stack, gadMap=GAD_MAP)  # , buildingMap=BUILDING_MAP

schedule = Scheduler()
#notify = Notifier()


class DummyBlock(FunctionalBlock):

    @schedule.every(minutes=2)
    def generateException(self):
        raise Exception("Error test")


class WeatherTemperatureBlock(FunctionalBlock):

    # Datapoints definition
    DP_01 = dict(name="temperature", access="output", dptId="9.001", default=19.)
    DP_02 = dict(name="humidity", access="output", dptId="9.007", default=50.)

    GO_01 = dict(dp="temperature", flags="CRT", priority="low")
    GO_02 = dict(dp="humidity", flags="CRT", priority="low")

    DESC = "Temperature management block"

    @schedule.every(minutes=1)
    def updateTemperatureHumidity(self):  #, event):
        Logger().trace("WeatherTemperatureBlock.updateTemperatureHumidity()")

        # How we retreive the temperature/humidity is out of the scope of this proposal
        temperature = 20.
        humidity = 55.
        self.dp["temperature"].value = temperature
        self.dp["humidity"].value = humidity


class WeatherWindBlock(FunctionalBlock):

    # Datapoints definition
    DP_01 = dict(name="wind_speed", access="output", dptId="9.005", default=0.)
    DP_02 = dict(name="wind_alarm", access="output", dptId="1.005", default="No alarm")
    DP_03 = dict(name="wind_speed_limit", access="input", dptId="9.005", default=15.)
    DP_04 = dict(name="wind_alarm_enable", access="input", dptId="1.003", default="Disable")

    GO_01 = dict(dp="wind_speed", flags="CRT", priority="low")
    GO_02 = dict(dp="wind_alarm", flags="CRTS", priority="normal")
    GO_03 = dict(dp="wind_speed_limit", flags="CW", priority="low")
    GO_04 = dict(dp="wind_alarm_enable", flags="CW", priority="low")

    DESC = "Wind management block"

    @schedule.every(seconds=30)
    def updateWindSpeed(self):  #, event):
        Logger().trace("WeatherWindBlock.updateWindSpeed()")

        # How we retreive the speed is out of the scope of this proposal
        speed = 12.

        # Now, write the new speed value to the Datapoint
        # This will trigger the bus notification, if a group object is associated
        self.dp["wind_speed"].value = speed

    #notify.datapoint(name="wind_speed_limit")  # Single DP
    #notify.datapoint()  # All DP
    #notify.group(gad="1/1/1")  # Single group address
    def checkWindSpeed(self, event):
        Logger().trace("WeatherWindBlock.checkWindSpeed()")

        # Read inputs/params
        wind_speed = self.dp["wind_speed"]
        wind_alarm_enable = self.dp["wind_alarm_enable"].value
        wind_speed_limit = self.dp["wind_speed_limit"].value

        # Check if alarm
        if wind_speed > wind_speed_limit:
            wind_alarm = "Alarm"
        elif wind_speed < wind_speed_limit - 5.:  # Little histeresis
            wind_alarm = "No alarm"

        # Write outputs
        if wind_alarm_enable:
            self.dp["wind_alarm"].value = wind_alarm


class WeatherSunPositionBlock(FunctionalBlock):

    # Datapoints definition
    DP_01 = dict(name="right_ascension", access="output", dptId="14.007", default=0.)
    DP_02 = dict(name="declination", access="output", dptId="14.007", default=0.)
    DP_03 = dict(name="elevation", access="output", dptId="14.007", default=0.)
    DP_04 = dict(name="azimuth", access="output", dptId="14.007", default=0.)
    DP_05 = dict(name="latitude", access="param", dptId="14.007", default=0.)
    DP_06 = dict(name="longitude", access="param", dptId="14.007", default=0.)
    DP_07 = dict(name="timezone", access="param", dptId="1.xxx", default=1)
    DP_08 = dict(name="saving_time", access="param", dptId="1.xxx", default=1)

    GO_01 = dict(dp="right_ascension", flags="CRT", priority="low")
    GO_02 = dict(dp="declination", flags="CRT", priority="low")
    GO_03 = dict(dp="elevation", flags="CRT", priority="low")
    GO_04 = dict(dp="azimuth", flags="CRT", priority="low")
    GO_05 = dict(dp="latitude", flags="CRWT", priority="low")
    GO_06 = dict(dp="longitude", flags="CRWT", priority="low")
    GO_07 = dict(dp="timezone", flags="CRWT", priority="low")
    GO_08 = dict(dp="saving_time", flags="CRWT", priority="low")

    DESC = "Sun position management block"

    def _computeJulianDay(self, year, month, day, hour, minute, second):
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

    def _siderealTime(self, julianDay):
        """ Compute the sidereal time.
        """
        centuries = julianDay / 36525.
        siderealTime = (24110.54841 + (8640184.812866 * centuries) + (0.093104 * (centuries ** 2)) - (0.0000062 * (centuries ** 3))) / 3600.
        siderealTime = ((siderealTime / 24.) - int(siderealTime / 24.)) * 24.

        return siderealTime

    def _equatorialCoordinates(self, year, month, day, hour, minute, second):
        """ Compute rightAscension and declination.
        """
        julianDay =  self._computeJulianDay(year, month, day, hour, minute, second)

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

    def _azimuthalCoordinates(self, year, month, day, hour, minute, second):
        """ Compute elevation and azimuth.
        """
        julianDay =  self._computeJulianDay(year, month, day, hour, minute, second)
        siderealTime = self._siderealTime(julianDay)
        angleH = 360. * siderealTime / 23.9344
        angleT = (hour - (self._timeZone + self._savingTime) - 12. + minute / 60. + second / 3600.) * 360. / 23.9344
        angle = angleH + angleT
        rightAscension, declination = self._equatorialCoordinates(year, month, day, hour, minute, second)
        angle_horaire = angle - rightAscension * 15. + self._longitude

        elevation = math.degrees(math.asin(math.sin(math.radians(declination)) * math.sin(math.radians(self._latitude)) - math.cos(math.radians(declination)) * math.cos(math.radians(self._latitude)) * math.cos(math.radians(angle_horaire))))

        azimuth = math.degrees(math.acos((math.sin(math.radians(declination)) - math.sin(math.radians(self._latitude)) * math.sin(math.radians(elevation))) / (math.cos(math.radians(self._latitude)) * math.cos(math.radians(elevation)))))
        sinazimuth = (math.cos(math.radians(declination)) * math.sin(math.radians(angle_horaire))) / math.cos(math.radians(elevation))
        if (sinazimuth < 0.):
            azimuth = 360. - azimuth

        return elevation, azimuth

    @schedule.every(minutes=1)
    def updatePosition(self):  #, event):
        Logger().trace("WeatherSunPositionBlock.updatePosition()")

        # Read inputs/params
        self._latitude = self.dp["latitude"].value
        self._longitude = self.dp["longitude"].value
        self._timeZone = self.dp["timezone"].value
        self._savingTime = self.dp["saving_time"].value

        # Computations
        tm_year, tm_mon, tm_day, tm_hour, tm_min, tm_sec, tm_wday, tm_yday, tm_isdst = time.localtime()
        julianDay =  self._computeJulianDay(tm_year, tm_mon, tm_day, tm_hour, tm_min, tm_sec)
        siderealTime = self._siderealTime(julianDay)

        rightAscension, declination = self._equatorialCoordinates(tm_year, tm_mon, tm_day, tm_hour, tm_min, tm_sec)
        elevation, azimuth = self._azimuthalCoordinates(tm_year, tm_mon, tm_day, tm_hour, tm_min, tm_sec)

        # Write outputs
        self.dp["right_ascension"].value = rightAscension
        self.dp["declination"].value = declination
        self.dp["elevation"].value = elevation
        self.dp["azimuth"].value = azimuth


def main():

    # Register FunctionalBlocks
    ets.register(DummyBlock, name="dummy", desc="dummy")  # , building="mob/GTL")
    ets.register(WeatherTemperatureBlock, name="weather_temperature", desc="temp 1")  # , building="mob/GTL")
    ets.register(WeatherWindBlock, name="weather_wind", desc="wind 1")
    ets.register(WeatherSunPositionBlock, name="weather_sun_position", desc="sun 1")

    # Weave weather station Datapoints to GroupAddresses
    # @todo: allow use of gad name, from GrOAT
    ets.weave(fb="weather_temperature", dp="temperature", gad="1/1/1")
    ets.weave(fb="weather_temperature", dp="humidity", gad="1/1/2")

    ets.weave(fb="weather_wind", dp="wind_speed", gad="1/1/3")
    ets.weave(fb="weather_wind", dp="wind_alarm", gad="1/1/4")
    ets.weave(fb="weather_wind", dp="wind_speed_limit", gad="1/1/5")
    ets.weave(fb="weather_wind", dp="wind_alarm_enable", gad="1/1/6")

    ets.weave(fb="weather_sun_position", dp="right_ascension", gad="1/1/3")
    ets.weave(fb="weather_sun_position", dp="declination", gad="1/1/4")
    ets.weave(fb="weather_sun_position", dp="elevation", gad="1/1/5")
    ets.weave(fb="weather_sun_position", dp="azimuth", gad="1/1/6")
    ets.weave(fb="weather_sun_position", dp="latitude", gad="1/1/7")
    ets.weave(fb="weather_sun_position", dp="longitude", gad="1/1/8")
    ets.weave(fb="weather_sun_position", dp="timezone", gad="1/1/9")
    ets.weave(fb="weather_sun_position", dp="saving_time", gad="1/1/10")
    ets.weave(fb="weather_sun_position", dp="saving_time", gad="1/1/11")

    #print
    #print
    #ets.printMapTable("gad")
    #print
    #print
    #ets.printMapTable("go")

    # Start the scheduler
    # @todo: move to a better place
    print
    schedule.start()
    schedule.printJobs()
    print

    # Run the stack main loop (blocking call)
    stack.mainLoop()

    schedule.stop()


if __name__ == "__main__":
    main()
