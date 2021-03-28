# -*- coding: utf-8 -*-

from pknyx.api import Device, Stack, ETS, FunctionalBlock

GAD_MAP = {1: {'root': "heating",
               1: {'root': "setpoint",
                   1: "living",
                   2: "bedroom 1",
                   3: "bedroom 2",
                   4: "bedroom 3"
                  },
               2: {'root': "temperature",
                   1: "living",
                   2: "bedroom 1",
                   3: "bedroom 2",
                   4: "bedroom 3"
                  }
              },
           2: {'root': "lights",
               1: {'root': None,
                   1: 'living',
                 },
               2: {'root': "etage",
                   1: None,
                   2: "bedroom 1"
                 }
              }
          }

stack = Stack()
ets = ETS(stack)
ets.gadMap = GAD_MAP


class WeatherBlock(FunctionalBlock):

    # Datapoints definition
    DP_01 = dict(name="temperature", access="output", dptId="9.007", default=19.)
    DP_02 = dict(name="humidity", access="output", dptId="9.007", default=50.)
    DP_03 = dict(name="wind_speed", access="output", dptId="9.005", default=0.)
    DP_04 = dict(name="wind_alarm", access="output", dptId="1.005", default="No alarm")
    DP_05 = dict(name="wind_speed_limit", access="input", dptId="9.005", default=15.)
    DP_06 = dict(name="wind_alarm_enable", access="input", dptId="1.003", default="Disable")
    DP_07 = dict(name="lattitude", access="param", dptId="9.xxx", default=0.)
    DP_08 = dict(name="longitude", access="param", dptId="9.xxx", default=0.)
    DP_09 = dict(name="altitude", access="param", dptId="9.xxx", default=0.)

    # Group Objects datapoints definition (can (should?) be defined in subclass)
    GO_01 = dict(dp="temperature", flags="CRT", priority="low")
    GO_02 = dict(dp="humidity", flags="CRT", priority="low")
    GO_03 = dict(dp="wind_speed", flags="CRT", priority="low")
    GO_04 = dict(dp="wind_alarm", flags="CRT", priority="normal")
    GO_05 = dict(dp="wind_speed_limit", flags="CWTU", priority="low")
    GO_06 = dict(dp="wind_alarm_enable", flags="CWTU", priority="low")

    # Interface Object Properties datapoints definition (name will be "PID_<upper(dp.name)>")
    #PR_01 = dict(dp="lattitude")
    #PR_02 = dict(dp="longitude")
    #PR_03 = dict(dp="altitude")

    # Polling Values datapoints definition
    #PV_01 = dict(dp="temperature")

    # Memory Mapped datapoints definition
    #MM_01 = dict(dp="temperature")

    DESC = "Class-level description"

    #@Device.schedule.every(minute=5)
    def checkWindSpeed(self, event):

        # How we retreive the speed is out of the scope of this proposal
        # speed = xxx

        # Now, write the new speed value to the Datapoint
        # This will trigger the bus notification, if a group object is associated
        self.dp["wind_speed"].value = speed

        # Check alarm speed
        if self.dp["wind_alarm_enable"].value == "Enable":
            if speed >= self.dp["wind_speed_limit"].value:
                self.dp["wind_alarm"].value = "Alarm"
            elif speed < self.dp["wind_speed_limit"].value - 5.:
                self.dp["wind_alarm"].value = "No alarm"

    #@Device.notify.datapoint(name="wind_speed")  # Single DP
    #@Device.notify.datapoint(name="temperature")  # Single DP
    #@Device.notify.datapoint(name=("wind_speed", "temperature"))  # Multiple DP
    #@Device.notify.datapoint()  # All DP
    #@Device.notify.datapoint(name="wind_speed", change=True)  # Only if value changed
    #@Device.notify.datapoint(name="wind_speed", condition="change")  # Only if value changed (could be "always")
    #@Device.notify.group(gad="1/1/1")  # Single group address
    #@Device.notify.groupObject(name="temperature")  # Single group object
    def doSomething(self, event):
        """
        event.type
        event.dp
        event.old
        event.new
        """
        pass


# Weather station class definition
class WeatherStation(Device):

    FB_01 = WeatherBlock(name="weather_block", desc="Instance-level description")

# Instanciation of the weather station device object
station = WeatherStation(name="weather_station", desc="Instance-level description", address="1.2.3")

ets.register(station)

# Linking weather station Datapoints to Group Address
ets.link(dev=station, dp="temperature", gad="1/1/1")
ets.link(dev=station, dp="humidity", gad="1/1/2")
ets.link(dev=station, dp="wind_speed", gad="1/1/3")
ets.link(dev=station, dp="wind_alarm", gad="1/1/4")
ets.link(dev=station, dp="wind_speed_limit", gad="1/1/5")
ets.link(dev=station, dp="wind_alarm_enable", gad="1/1/6")

print
print
ets.printMapTable("gad")
print
print
ets.printMapTable("go")
