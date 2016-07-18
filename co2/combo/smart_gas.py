#!/usr/bin/env python

import os
import requests
import pytz, datetime, time
import struct
import array
from neopixel import *
from lib_sensors import HTU21D,mhz19
from lib_led import my_ws_2812


# for https://app.initialstate.com/#/lines
#from ISStreamer.Streamer import Streamer
#        initialstate_bucket_key = os.environ.get("initialstate_bucket_key")
#        initialstate_access_key = os.environ.get("initialstate_access_key")
#        streamer = Streamer(bucket_name="OS WEST-B", bucket_key=initialstate_bucket_key, access_key=initialstate_access_key)
#        streamer.log("co2", co2_value)
#        streamer.log("Temp", t_value)
#        streamer.log("Humidity", humid_value)


# Main program logic follows:
if __name__ == '__main__':

        tz = pytz.timezone('Europe/Kiev')
        lstrip = my_ws_2812()
        sensor_ht = HTU21D()
        sensor_co2 = mhz19()
        c_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")


        co2_value = sensor_co2.read_co2()
        t_value = sensor_ht.read_temperature()
        humid_value = sensor_ht.read_humidity()
        lstrip.to_level(co2_value)

        print "{} \nCo2:{}. Temp:{}. Humidity:{}\n".format(c_time, co2_value, t_value,humid_value)

        # since co2_value could be None, we should skip whole string for thingspeak:
        co2_ts_string = "&field1={}".format(co2_value)
        if co2_value is None:
            co2_ts_string = None
        thingspeak_key = os.environ.get("thingspeak_key")
        requests.get('https://api.thingspeak.com/update?api_key={}&field1={}&field2={}&field3={}'.format(thingspeak_key,co2_ts_string,t_value,humid_value))
