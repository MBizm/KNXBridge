# -*- coding: utf-8 -*-

from pknyx.api import FunctionalBlock
from pknyx.api import logger, schedule, notify


class WeatherTempFB(FunctionalBlock):
    """ Temperature/humidity handling
    """

    # Datapoints definition
    DP_01 = dict(name="temperature", access="output", dptId="9.001", default=19.)
    DP_02 = dict(name="humidity", access="output", dptId="9.007", default=50.)

    GO_01 = dict(dp="temperature", flags="CRT", priority="low")
    GO_02 = dict(dp="humidity", flags="CRT", priority="low")

    DESC = "Weather temp/humidity FB"

    @schedule.every(minutes=1)
    def updateTempHumidity(self):
        """ This method is called every minute to refresh the temperature/himidity
        """

        # A real implementation should read a real weather station, or get data from a web station
        temperature = 20.
        humidity = 55.

        self.dp["temperature"].value = temperature
        self.dp["humidity"].value = humidity
