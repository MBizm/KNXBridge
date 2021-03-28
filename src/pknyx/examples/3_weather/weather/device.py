# -*- coding: utf-8 -*-

from pknyx.api import Device

from fb.weatherTempFB import WeatherTempFB
from fb.weatherWindFB import WeatherWindFB
from fb.weatherSunFB import WeatherSunFB


class Weather(Device):
    FB_01 = dict(cls=WeatherTempFB, name="weather_temp_fb", desc="weather temp fb")
    FB_02 = dict(cls=WeatherWindFB, name="weather_wind_fb", desc="weather wind fb")
    FB_03 = dict(cls=WeatherSunFB, name="weather_sun_fb", desc="weather sun fb")

    LNK_01 = dict(fb="weather_temp_fb", dp="temperature", gad="1/1/1")
    LNK_02 = dict(fb="weather_temp_fb", dp="humidity", gad="1/1/2")

    LNK_03 = dict(fb="weather_wind_fb", dp="wind_speed", gad="1/2/1")
    LNK_04 = dict(fb="weather_wind_fb", dp="wind_alarm", gad="1/2/2")
    LNK_05 = dict(fb="weather_wind_fb", dp="wind_speed_limit", gad="1/2/3")
    LNK_06 = dict(fb="weather_wind_fb", dp="wind_alarm_enable", gad="1/2/4")

    LNK_07 = dict(fb="weather_sun_fb", dp="right_ascension", gad="1/3/1")
    LNK_08 = dict(fb="weather_sun_fb", dp="declination", gad="1/3/2")
    LNK_09 = dict(fb="weather_sun_fb", dp="elevation", gad="1/3/3")
    LNK_10 = dict(fb="weather_sun_fb", dp="azimuth", gad="1/3/4")
    LNK_11 = dict(fb="weather_sun_fb", dp="latitude", gad="1/3/5")
    LNK_12 = dict(fb="weather_sun_fb", dp="longitude", gad="1/3/6")
    LNK_13 = dict(fb="weather_sun_fb", dp="time_zone", gad="1/3/7")
    LNK_14 = dict(fb="weather_sun_fb", dp="saving_time", gad="1/3/8")

    DESC = "Weather"


DEVICE = Weather
