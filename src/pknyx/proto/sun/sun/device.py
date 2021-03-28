# -*- coding: utf-8 -*-

from pknyx.api import Device

from fb.sunFB import SunFB


class Sun(Device):
    FB_01 = dict(cls=SunFB, name="sun_fb", desc="sun fb")

    LNK_01 = dict(fb="sun_fb", dp="right_ascension", gad="1/1/1")
    LNK_02 = dict(fb="sun_fb", dp="declination", gad="1/1/2")
    LNK_03 = dict(fb="sun_fb", dp="elevation", gad="1/1/3")
    LNK_04 = dict(fb="sun_fb", dp="azimuth", gad="1/1/4")
    LNK_05 = dict(fb="sun_fb", dp="latitude", gad="1/1/5")
    LNK_06 = dict(fb="sun_fb", dp="longitude", gad="1/1/6")
    LNK_07 = dict(fb="sun_fb", dp="time_zone", gad="1/1/7")
    LNK_08 = dict(fb="sun_fb", dp="saving_time", gad="1/1/8")

    DESC = "Sun"

DEVICE = Sun
