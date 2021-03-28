# -*- coding: utf-8 -*-

from pknyx.api import Device

from actuatorFB import ActuatorFB


class Actuator(Device):
    FB_01 = dict(cls=ActuatorFB, name="actuator_fb", desc="actuator fb")

    LNK_01 = dict(fb="actuator_fb", dp="cmd", gad="6/0/1")
    LNK_01 = dict(fb="actuator_fb", dp="state", gad="6/1/1")

    DESC = "Actuator"


DEVICE = Actuator
