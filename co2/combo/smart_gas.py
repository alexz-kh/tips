#!/usr/bin/env python

import time
from neopixel import *
import serial
import requests
import time
import pytz, datetime
import struct
import array
import i2c_base
from temp import HTU21D
tz = pytz.timezone('Europe/Kiev')
from ISStreamer.Streamer import Streamer

# LED strip configuration:
LED_COUNT      = 8      # Number of LED pixels.
LED_PIN        = 18      # GPIO pin connected to the pixels (must support PWM!).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 5       # DMA channel to use for generating signal (try 5)
LED_BRIGHTNESS = 255     # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
co2_value      = 400     # set default value, in case pri just started and co2 meter didn't finish calibrating
def mh_z19():
  with serial.Serial('/dev/ttyAMA0', baudrate=9600, timeout=1.0) as ser:
      result=ser.write("\xff\x01\x86\x00\x00\x00\x00\x00\x79") ; s=ser.read(9);
      co_result=ord(s[2])*256 + ord(s[3])
  return co_result

# Define functions which animate LEDs in various ways.
def colorWipe(strip, color, wait_ms=50):
	"""Wipe color across display a pixel at a time."""
	for i in range(strip.numPixels()):
		strip.setPixelColor(i, color)
		strip.show()
		time.sleep(wait_ms/1000.0)

def get_uptime(return_type):
    with open('/proc/uptime', 'r') as f:
        uptime_seconds = float(f.readline().split()[0])
        uptime_string = str(datetime.timedelta(seconds = uptime_seconds))
    _is_safe = True
    # CO2 meter need few min to start
    if uptime_seconds < 10 * 60:
        _is_safe = False
    if return_type == 'seconds':
        return uptime_seconds
    elif return_type == 'string':
        return uptime_string
    elif return_type == 'get_safe':
        return _is_safe


def to_level(ppm):
    intn = 10
    # gled=G,R,B
    gled=Color(intn, 0, 0)
    rled=Color(0, intn*9, 0)
    yled=Color(intn/2,intn/2,0)
    zled=Color(0,0,0)
    wled=Color(intn/3,intn/3,intn/3)

    def _leds(ledcolor, back, n, LED_COUNT):
       #back = back or zled
       # set backlight always white
       back = wled
       for i in range(0, LED_COUNT):
           if i < n:
               strip.setPixelColor(i, ledcolor)
           else:
               strip.setPixelColor(i, back)
    n=0
    if ppm<600:
        n=(ppm-400)/25+1
        _leds(gled, wled, n, LED_COUNT)
    elif ppm<1400:
        n=(ppm-600)/100+1
        _leds(yled, gled, n, LED_COUNT)
    else:
#        n=(ppm-1400)/100+1
        n=(ppm-1400)/200+1
        _leds(rled, yled, n, LED_COUNT)
    strip.show()

# Main program logic follows:
if __name__ == '__main__':
	# Create NeoPixel object with appropriate configuration.
	strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS)
        streamer = Streamer(bucket_name="OS WEST-B", bucket_key="TVK4BERXLDS8", access_key="7J5eFza7KJHeXb0WaVvwbFlwVhLKjPei")
	# Intialize the library (must be called once before other functions).
	strip.begin()
        sensor_ht = HTU21D()

        c_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        if get_uptime('get_safe'):
            co2_value = mh_z19()
        t_value = sensor_ht.read_temperature()
        humid_value = sensor_ht.read_humidity()
        #import ipdb;ipdb.set_trace()
#        range_color(strip,co2_value)
        time.sleep(3)
        to_level(co2_value)
        print "{} \nCo2:{}. Temp:{}. Humidity:{}\n".format(c_time, co2_value, t_value,humid_value)
        requests.get('https://api.thingspeak.com/update?api_key=X3FRUHF0JRLA0ODF&field1={}&field2={}&field3={}'.format(co2_value,t_value,humid_value))
        streamer.log("co2", co2_value)
        streamer.log("Temp", t_value)
        streamer.log("Humidity", humid_value)
