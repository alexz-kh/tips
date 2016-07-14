#!/usr/bin/env python

from neopixel import *
import time
import pytz, datetime
import struct
import array



class my_ws_2812(object):
    def __init__(self):
        self.SERIAL_DEVICE = '/dev/ttyAMA0'
        # LED strip configuration:
        self.LED_COUNT      = 8      # Number of LED pixels.
        self.LED_PIN        = 18      # GPIO pin connected to the pixels (must support PWM!).
        self.LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
        self.LED_DMA        = 5       # DMA channel to use for generating signal (try 5)
        self.LED_BRIGHTNESS = 255     # Set to 0 for darkest and 255 for brightest
        self.LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
	self.strip = Adafruit_NeoPixel(self.LED_COUNT, self.LED_PIN,
            self.LED_FREQ_HZ, self.LED_DMA, self.LED_INVERT,
            self.LED_BRIGHTNESS)
        self.strip.begin()

    # Define functions which animate LEDs in various ways.
    def colorWipe(self, color, wait_ms=50):
    	"""Wipe color across display a pixel at a time."""
    	for i in range(self.strip.numPixels()):
    		self.strip.setPixelColor(i, color)
    		self.strip.show()
    		time.sleep(wait_ms/1000.0)

    def colorFill(self, color):
    	for i in range(self.strip.numPixels()):
    		self.strip.setPixelColor(i, color)
        self.strip.show()

    def to_level(self, ppm):
        intn = 10
        # gled=G,R,B
        gled=Color(intn, 0, 0)
        rled=Color(0, intn, 0)
        yled=Color(intn/2,intn/2,0)
        zled=Color(0,0,0)
        wled=Color(intn/3,intn/3,intn/3)

        def _leds(self, ledcolor, back, n):
           #back = back or zled
           # set backlight always white
           back = wled
           for i in range(0, self.LED_COUNT):
               if i < n:
                   self.strip.setPixelColor(i, ledcolor)
               else:
                   self.strip.setPixelColor(i, back)
        n=0
        if ppm<600:
            n=(ppm-400)/25+1
            _leds(self,gled, wled,n)
        elif ppm<1400:
            n=(ppm-600)/100+1
            _leds(self,yled, gled,n)
        else:
            n=(ppm-1400)/200+1
            _leds(self,rled, yled,n)
        self.strip.show()

# Main program logic follows:
if __name__ == '__main__':
	# Create NeoPixel object with appropriate configuration.
        lstrip = my_ws_2812()
        lstrip.to_level(500)
        time.sleep(3)
        lstrip.colorWipe(Color(20, 10, 20), wait_ms=50)
