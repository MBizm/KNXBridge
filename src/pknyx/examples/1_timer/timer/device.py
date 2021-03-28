# -*- coding: utf-8 -*-

from pknyx.api import Device

from timerFB import TimerFB


class Timer(Device):
    FB_01 = dict(cls=TimerFB, name="timer_fb", desc="timer fb")

    LNK_01 = dict(fb="timer_fb", dp="cmd", gad="1/1/1")
    LNK_02 = dict(fb="timer_fb", dp="state", gad="1/2/1")
    LNK_03 = dict(fb="timer_fb", dp="delay", gad="1/3/1")

    DESC = "Timer"


DEVICE = Timer
