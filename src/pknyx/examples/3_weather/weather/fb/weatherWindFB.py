# -*- coding: utf-8 -*-

from pknyx.api import FunctionalBlock
from pknyx.api import logger, schedule, notify


class WeatherWindFB(FunctionalBlock):
    """ Wind handling
    """

    # Datapoints definition
    DP_01 = dict(name="wind_speed", access="output", dptId="9.005", default=0.)
    DP_02 = dict(name="wind_alarm", access="output", dptId="1.005", default="No alarm")
    DP_03 = dict(name="wind_speed_limit", access="input", dptId="9.005", default=15.)
    DP_04 = dict(name="wind_alarm_enable", access="input", dptId="1.003", default="Disable")

    GO_01 = dict(dp="wind_speed", flags="CRT", priority="low")
    GO_02 = dict(dp="wind_alarm", flags="CRTS", priority="normal")
    GO_03 = dict(dp="wind_speed_limit", flags="CWU", priority="low")
    GO_04 = dict(dp="wind_alarm_enable", flags="CWU", priority="low")

    DESC = "Wind management block"

    @schedule.every(seconds=10)
    def updateWindSpeed(self):
        """This method is called every 10 seconds to refresh the wind speed
        """

        # A real implementation should read a real weather station, or get data from a web station
        speed = 20.

        # Write the new speed value to matching Datapoint
        # This will trigger the bus notification (if a group object is associated)
        self.dp["wind_speed"].value = speed

    @notify.datapoint(dp="wind_speed", condition="always")
    @notify.datapoint(dp="wind_alarm_enable", condition="change")
    @notify.datapoint(dp="wind_speed_limit", condition="change")
    def checkWindSpeed(self, event):
        """ This method is called when some datapoints value are set

        Depending on the 'condition' value, the method is triggerd only when the corresponding datapoint value changes,
        or in any case.

        Here, we set the wind_alarm datapoint value accordingly to other datapoints values.
        """

        # Read inputs/params
        windSpeed = self.dp["wind_speed"].value
        windAlarm = self.dp["wind_alarm"].value
        windAlarmEnable = self.dp["wind_alarm_enable"].value
        windSpeedLimit = self.dp["wind_speed_limit"].value

        # Check if alarm
        if windSpeed > windSpeedLimit:
            windAlarm = "Alarm"
        elif windSpeed < windSpeedLimit - 5.:
            windAlarm = "No alarm"

        # Write outputs
        if windAlarmEnable == "Enable":
            self.dp["wind_alarm"].value = windAlarm

    DESC = "Weather wind FB"
