from pknyx.api import FunctionalBlock
from pknyx.api import logger, schedule, notify


class TimerFB(FunctionalBlock):
    DP_01 = dict(name="cmd", access="output", dptId="1.001", default="Off")
    DP_02 = dict(name="state", access="input", dptId="1.001", default="Off")
    DP_03 = dict(name="delay", access="input", dptId="7.005", default=10)

    GO_01 = dict(dp="cmd", flags="CWT", priority="low")
    GO_02 = dict(dp="state", flags="CWUI", priority="low")
    GO_03 = dict(dp="delay", flags="CWU", priority="low")

    DESC = "Timer FB"

    def init(self):
        self._timer = 0

    @notify.datapoint(dp="state", condition="change")
    def stateChanged(self, event):
        if event['newValue'] == "On":
            delay = self.dp["delay"].value
            logger.info("%s: start timer for %ds" % (self._name, delay))
            self._timer = delay
        elif event['newValue'] == "Off":
            if self._timer:
                logger.info("%s: switched off detected; cancel timer" % self._name)
                self._timer = 0

    @schedule.every(seconds=1)
    def updateTimer(self):
        if self._timer:
            self._timer -= 1
            if not self._timer:
                logger.info("%s: timer expired; switch off" % self._name)
                self.dp["cmd"].value = "Off"

    @notify.datapoint(dp="delay", condition="change")
    def delayChanged(self, event):
        if self._timer:
            delay = self.dp["delay"].value
            logger.info("%s: delay changed; restart timer" % self._name)
            self._timer = delay
