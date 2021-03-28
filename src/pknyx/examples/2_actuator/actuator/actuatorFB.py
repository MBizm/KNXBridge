# -*- coding: utf-8 -*-

from pknyx.api import FunctionalBlock
from pknyx.api import logger, schedule, notify


class ActuatorFB(FunctionalBlock):
    """ Actuator functional block
    """

    # Datapoints definition
    DP_01 = dict(name="cmd", access="input", dptId="1.001", default="Off")
    DP_02 = dict(name="state", access="output", dptId="1.001", default="Off")

    GO_01 = dict(dp="cmd", flags="CWU", priority="low")
    GO_02 = dict(dp="state", flags="CRT", priority="low")

    DESC = "Actuator"

    @notify.datapoint(dp="cmd", condition="change")
    def cmdChanged(self, event):
        """ Method called when the 'cmd' datapoint changes

        We just copy the 'cmd' datapoint value to the 'state' datapoint.
        """
        logger.debug("ActuatorFB.cmdChanged(): event=%s" % repr(event))

        value = event['newValue']
        logger.info("%s: switch output %s" % (self.name, value))
        self.dp["state"].value = value

