#!/usr/bin/env python

import os
import requests
import pytz, datetime, time
import struct
import array
from Adafruit_BME280 import *

# Main program logic follows:
if __name__ == '__main__':

    tz = pytz.timezone('Europe/Kiev')
    c_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    sensor = BME280(mode=BME280_OSAMPLE_8, address=0x76)

    degrees = sensor.read_temperature()
    pascals = sensor.read_pressure()
    hectopascals = pascals / 100
    humidity = sensor.read_humidity()

    print "{} \nPressure:{}. Temp:{}. Humidity:{}\n".format(c_time, hectopascals, degrees, humidity)

    thingspeak_key = os.environ.get("THINGSPEAK_KEY")
    requests.get('https://api.thingspeak.com/update?api_key={}&field1={}&field2={}&field3={}'.format(thingspeak_key,degrees,hectopascals,humidity))
