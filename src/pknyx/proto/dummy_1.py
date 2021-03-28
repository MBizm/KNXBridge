from pprint import pprint

from pknyx.api import Device, Stack, ETS

stack = Stack()
ets = ETS(stack)

# Weather station class definition
class WeatherStation(Device):

    # Datapoints (= Group Objects) definition
    DP_01 = dict(name="temperature", dptId="9.001", flags="CRT", priority="low", defaultValue=0.)
    DP_02 = dict(name="humidity", dptId="9.007", flags="CRT", priority="low", defaultValue=0.)
    DP_03 = dict(name="wind_speed", dptId="9.005", flags="CRT", priority="low", defaultValue=0.)
    DP_04 = dict(name="wind_alarm", dptId="1.005", flags="CRT", priority="urgent", defaultValue="No alarm")
    DP_05 = dict(name="wind_speed_limit", dptId="9.005", flags="CWTU", priority="low", defaultValue=15.)
    DP_06 = dict(name="wind_alarm_enable", dptId="1.003", flags="CWTU", priority="low", defaultValue="Disable")

# Instanciation of the weather station device object
station = WeatherStation(name="station", desc="My simple weather station example", address="1.2.3")

# Linking weather station Datapoints to Group Addresses
ets.link(dev=station, dp="temperature", gad="1/1/1")
ets.link(dev=station, dp="temperature", gad="1/2/1")
ets.link(dev=station, dp="humidity", gad="1/1/2")
ets.link(dev=station, dp="wind_speed", gad="1/1/3")
ets.link(dev=station, dp="wind_alarm", gad="1/1/4")
ets.link(dev=station, dp="wind_speed_limit", gad="1/1/5")
ets.link(dev=station, dp="wind_alarm_enable", gad="1/1/6")

pprint(ets.computeMapTable())