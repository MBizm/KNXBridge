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

Framework usage ideas

Documentation
=============

 - General configuration (GA mapping)
  - manual mapping of group addresses
  - ETS import
  - auto-detecting group addresses by listening to the bus

 -

@author: Frédéric Mantegazza
@copyright: (C) 2013 Frédéric Mantegazza
@license: GPL
"""

__revision__ = "$Id$"


################################################################################

from pknyx import GroupAddressManager, Rule, RuleManager, Scheduler

scheduler = Scheduler()


class SimpleRule(Rule):

    @scheduler.every(hours=2)
    def simpleEvent(self):
        ga = GroupAddressManager().find("1/1/1")
        ga.write(1)


myRule = SimpleRule()
RuleManager().register(myRule)

################################################################################

from pknyx.services import group, schedule, log, manager
from pknyx.elements import Rule


class HeatingRules(Rule):

    @schedule.every(hours=2)
    def bathroom(self):
        group.write("1/1/1", 0)


manager.registerRule(HeatingRules)  # Auto-instanciation

################################################################################

from pknyx.rule import Rule


class Heating(Rule):

    def bathroom(self, every="2h"):
        ga = self.get("1/1/1")
        ga.write(0)


Heating()  # Auto-registering

################################################################################

from pknyx.services import schedule, manager
from pknyx.elements import Rule


class HeatingRules(Rule):

    @schedule.every(hours=2)
    def bathroom(self):
        ga = self.groupAddressManager.find("1/1/1")
        ga.write(0)


heatRules = HeatingRules()
manager.registerRule(heatRules)

""" Notes

- Register some services in Rule class
- registerRule() can take a Rule instance, a Rule subclass, or a function. In this last case, the function
will be binded to a Rule instance, and registered.
- Instead of the decorator, the behavior of the rule can be given as parameter to registerRule() (simple string, or
object describing the behavior).

Or rules only as functions?
-> Use Participant for complete state-based stuff...
"""

################################################################################

from pknyx.services import Trigger, Logger  #, Scheduler
from pknyx.managers import RulesManager, GroupAddressManager

#schedule = Scheduler()
trigger = Trigger()
logger = Logger()
grp = GroupAddressManager()
rules = RulesManager()

#@schedule.every(minutes=1)
@trigger.schedule.every(hour=1)
#@trigger.group(id="1/1/1").changed()   <<<<<<<<< Does not work
@trigger.system.start
def heatingBathroomManagement(event):
    """ Simple heating management

    @param event: contain some informations about the triggering event
    @type event: dict or Event-type?
    """
    temp = grp.findById("bathroom_temp").read()
    #tempObj = grp.find("bathroom_temp")
    #tempObj = grp.find("1/1/1")
    #temp = tempObj.read()  # read from bus
    #temp = tempObj.value   # get last known value
    tempSetup = grp.findById("bathroom_temp_setup").read()
    heaterObj = grp.findById("bathroom_heater")

    if temp < tempSetup - 0.25:
        logger.info("bathroom heater on")
        heaterObj.write(1)
    elif temp > tempSetup + 0.25:
        logger.info("bathroom heater off")
        heaterObj.write(0)

rules.register(heatingBathroomManagement)

################################################################################

from pknyx.api import Device, \
                      ETS


class VMC(Device):
    """ VMC virtual device

    @todo: add parameters, for more generic devices (as real devices)
    @todo: make as thread
    @todo: should also react with time-based events, system events... -> decorator @trigger.xxx
    """

    # Datapoints are created as class entities and automatically instancianted as real DP in constructor
    # Their name must start with 'DP_' ; they will be stored in self.dp dict-like object.
    # Ex: DP_1 = ("truc", "1.001", "cwtu", "low", 0) ... > self.dp["truc"]  <<<< special dict, with additionnal features

    DP_01 = ("temp_entree", "9.001", "cwtu", "low", 0)
    DP_02 = {'name': "temp_sortie", dptId: "9.001", 'flags': "cwtu", 'priority': "low", 'initValue': 0}
    DP_03 = dict(name="temp_repris", dptId="9.001", flags="cwtu", priority="low", initValue=0)

    def _init(self):
        """
        """

    def _initDP(self):
        """
        """
        self.dp["temp_entree"].value = 0  # Add persistence feature!!!
        # self.dp.temp_entree.value = 0

    @Device.trigger.at("...")  # take a complete date and/or time
    @Device.trigger.cron("...")  # cron-like syntax
    @Device.trigger.after(minute=5)  # after the device is created (day/month/year/hour/minute/second)
    @Device.trigger.every(day=1, start="...", end="...")  # (day/month/year/hour/minute/second + start/end)
    def timeCallback(self, event):
        """
        """

    @Device.trigger.poll()
    def pollingCallback(self, event):
        """
        Fast polling.
        This method is called regularly by the thread. Do here whatever you need to do.
        Issue if freeze or take too much time?
        """

    @Device.trigger.dp("temp_sortie")  # dp value has changed (from the bus)
    def dpCallback(self, event):
        """
        """
        #print event.src
        #print event.dest
        #print event.value
        #print event.priority
        #print event.cEMI

    @Device.trigger.system("start")  # "start"/"stop"/"crash"
    def systemCallback(self, event):
        """
        """


vmc = VMC("1.2.3")
ETS.link(vmc, "temp_entree", "1/1/1")
ETS.link(vmc, "temp_entree", ("1/1/1", "1/1/2"))

################################################################################

from pknyx.api import Device, Stack, ETS

stack = Stack()
ets = ETS(stack)

# Weather station class definition
class WeatherStation(Device):

    # Datapoints (= Group Objects) definition
    DP_01 = dict(name="temperature", dptId="9.001", flags="CRT", priority="low", initValue=0.)
    DP_02 = dict(name="humidity", dptId="9.007", flags="CRT", priority="low", initValue=0.)
    DP_03 = dict(name="wind_speed", dptId="9.005", flags="CRT", priority="low", initValue=0.)
    DP_04 = dict(name="wind_alarm", dptId="1.005", flags="CRT", priority="normal", initValue="No alarm")
    DP_05 = dict(name="wind_speed_limit", dptId="9.005", flags="CWTU", priority="low", initValue=15.)
    DP_06 = dict(name="wind_alarm_enable", dptId="1.003", flags="CWTU", priority="low", initValue="Disable")

    @Device.schedule.every(minute=5)
    def checkWindSpeed(self):

        # How we retreive the speed is out of the scope of this proposal
        # speed = xxx

        # Now, write the new speed value to the Datapoint
        self.dp["wind_speed"].value = speed

        # Check alarm speed
        if self.dp["wind_alarm_enable"].value == "Enable":
            if speed >= self.dp["wind_speed_limit"].value:
                self.dp["wind_alarm"].value = "Alarm"
            elif speed < self.dp["wind_speed_limit"].value - 5.:
                self.dp["wind_alarm"].value = "No alarm"

# Instanciation of the weather station device object
station = WeatherStation(name="weather_station", desc="My simple weather station example", address="1.2.3")

# Linking weather station Datapoints to Group Address
ets.link(dev=station, dp="temperature", gad="1/1/1")
ets.link(dev=station, dp="humidity", gad="1/1/2")
ets.link(dev=station, dp="wind_speed", gad="1/1/3")
ets.link(dev=station, dp="wind_alarm", gad="1/1/4")
ets.link(dev=station, dp="wind_speed_limit", gad="1/1/5")
ets.link(dev=station, dp="wind_alarm_enable", gad="1/1/6")

################################################################################

from pknyx.api import Device, Stack, ETS

stack = Stack()
ets = ETS(stack)

class WeatherBlock(FuntionalBlock):

    # Datapoints definition
    DP_01 = dict(name="PID_TEMPERATURE", type="out", dptId="9.001", defaultValue=0.)
    DP_02 = dict(name="PID_HUMIDITY", type="out", dptId="9.007", defaultValue=0.)
    DP_03 = dict(name="PID_WIND_SPEED", type="out", dptId="9.005", defaultValue=0.)
    DP_04 = dict(name="PID_WIND_ALARM", type="out", dptId="1.005", defaultValue="No alarm")
    DP_05 = dict(name="PID_WIND_SPEED_LIMIT", type="in", dptId="9.005", defaultValue=15.)
    DP_06 = dict(name="PID_WIND_ALARM_ENABLE", type="in", dptId="1.003", defaultValue="Disable")
    DP_07 = dict(name="PID_LATTITUDE", type="param")
    DP_08 = dict(name="PID_LONGITUDE", type="param")
    DP_09 = dict(name="PID_ALTITUDE", type="param")

    # Group Objects datapoints definition
    GO_01 = dict(name="temperature", dp="PID_TEMPERATURE", flags="CRT", priority="low")
    GO_02 = dict(name="humidity", dp="PID_HUMIDITY", flags="CRT", priority="low")
    GO_03 = dict(name="wind_speed", dp="PID_WIND_SPEED", flags="CRT", priority="low")
    GO_04 = dict(name="wind_alarm", dp="PID_WIND_ALARM", flags="CRT", priority="normal")
    GO_05 = dict(name="wind_speed_limit", dp="PID_WIND_SPEED", flags="CWTU", priority="low")
    GO_06 = dict(name="wind_alarm_enable", dp="PID_WIND_SPEED", flags="CWTU", priority="low")

    # Interface Object Properties datapoints definition
    PR_01 = dict(dp="PID_LATTITUDE")
    PR_02 = dict(dp="PID_LONGITUDE")
    PR_03 = dict(dp="PID_ALTITUDE")

    # Polling Values datapoints definition
    #PV_01 = dict(dp="temperature")

    # Memory Mapped datapoints definition
    #MM_01 = dict(dp="temperature")

    @Device.schedule.every(minute=5)
    def checkWindSpeed(self):

        # How we retreive the speed is out of the scope of this proposal
        # speed = xxx

        # Now, write the new speed value to the Datapoint
        self.dp["PID_WIND_SPEED"].value = speed

        # Check alarm speed
        if self.dp["PID_WIND_ALARM_ENABLE"].value == "Enable":
            if speed >= self.dp["PID_WIND_SPEED_LIMIT"].value:
                self.dp["PID_WIND_ALARM"].value = "Alarm"
            elif speed < self.dp["PID_WIND_SPEED_LIMIT"].value - 5.:
                self.dp["PID_WIND_ALARM"].value = "No alarm"

    #@Device.notify


# Weather station class definition
class WeatherStation(Device):

    FB_01 = WeatherBlock(name="weather_block")

# Instanciation of the weather station device object
station = WeatherStation(name="weather_station", desc="My simple weather station example", address="1.2.3")

# Linking weather station Datapoints to Group Address
ets.link(dev=station, dp="temperature", gad="1/1/1")
ets.link(dev=station, dp="humidity", gad="1/1/2")
ets.link(dev=station, dp="wind_speed", gad="1/1/3")
ets.link(dev=station, dp="wind_alarm", gad="1/1/4")
ets.link(dev=station, dp="wind_speed_limit", gad="1/1/5")
ets.link(dev=station, dp="wind_alarm_enable", gad="1/1/6")
