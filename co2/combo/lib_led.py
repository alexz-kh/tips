#!/usr/bin/env python

from neopixel import *
import time
import pytz, datetime
import struct
import array


class my_ws_2812(object):
    def __init__(self,BRIGHTNESS=100,LED_COUNT=8):
        self.SERIAL_DEVICE = '/dev/ttyAMA0'
        # LED strip configuration:
        self.LED_COUNT      = LED_COUNT  # Number of LED pixels.
        self.LED_PIN        = 18         # GPIO pin connected to the pixels (must support PWM!).
        self.LED_FREQ_HZ    = 800000     # LED signal frequency in hertz (usually 800khz)
        self.LED_DMA        = 5          # DMA channel to use for generating signal (try 5)
        self.LED_BRIGHTNESS = BRIGHTNESS # Set to 0 for darkest and 255 for brightest
        self.LED_INVERT     = False      # True to invert the signal (when using NPN transistor level shift)
	self.strip = Adafruit_NeoPixel(self.LED_COUNT, self.LED_PIN,
            self.LED_FREQ_HZ, self.LED_DMA, self.LED_INVERT,
            self.LED_BRIGHTNESS)
        self.strip.begin()

    # Define functions which animate LEDs in various ways.
    # Animations was copyed from:
    # https://github.com/jgarff/rpi_ws281x/blob/master/python/examples/strandtest.py
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

    def theaterChase(self, color, wait_ms=50, iterations=10):
    	"""Movie theater light style chaser animation."""
    	for j in range(iterations):
    		for q in range(3):
    			for i in range(0, selg.strip.numPixels(), 3):
    				self.strip.setPixelColor(i+q, color)
    			self.strip.show()
    			time.sleep(wait_ms/1000.0)
    			for i in range(0, self.strip.numPixels(), 3):
    				self.strip.setPixelColor(i+q, 0)

    def wheel(self, pos):
    	"""Generate rainbow colors across 0-255 positions."""
    	if pos < 85:
    		return Color(pos * 3, 255 - pos * 3, 0)
    	elif pos < 170:
    		pos -= 85
    		return Color(255 - pos * 3, 0, pos * 3)
    	else:
    		pos -= 170
    		return Color(0, pos * 3, 255 - pos * 3)

    def rainbow(self, wait_ms=20, iterations=1):
    	"""Draw rainbow that fades across all pixels at once."""
    	for j in range(256*iterations):
    		for i in range(self.strip.numPixels()):
    			self.strip.setPixelColor(i, self.wheel((i+j) & 255))
    		self.strip.show()
    		time.sleep(wait_ms/1000.0)

    def rainbowCycle(self, wait_ms=20, iterations=5):
    	"""Draw rainbow that uniformly distributes itself across all pixels."""
    	for j in range(256*iterations):
    		for i in range(self.strip.numPixels()):
    			self.strip.setPixelColor(i, self.wheel(((i * 256 / self.strip.numPixels()) + j) & 255))
    		self.strip.show()
    		time.sleep(wait_ms/1000.0)

    def theaterChaseRainbow(self, wait_ms=50):
    	"""Rainbow movie theater light style chaser animation."""
    	for j in range(256):
    		for q in range(3):
    			for i in range(0, self.strip.numPixels(), 3):
    				self.strip.setPixelColor(i+q, self.wheel((i+j) % 255))
    			self.strip.show()
    			time.sleep(wait_ms/1000.0)
    			for i in range(0, self.strip.numPixels(), 3):
                            self.strip.setPixelColor(i+q, 0)

    def to_level(self, ppm):
        if ppm is None:
            self.rainbowCycle(wait_ms=1,iterations=5)
            self.colorWipe(Color(0, 0, 255), wait_ms=50)
            self.colorWipe(Color(10, 10, 10), wait_ms=100)
            return
        gled=Color(255, 0, 0)
        rled=Color(0, 255, 0)
        yled=Color(255,255,0)
        zled=Color(0,0,0)
        wled=Color(255,255,255)

        def _leds(self, ledcolor, n, blight=wled):
           # blight set backlight to color
           for i in range(0, self.LED_COUNT):
               if i < n:
                   self.strip.setPixelColor(i, ledcolor)
               else:
                   self.strip.setPixelColor(i, blight)
        n=0
        if ppm<600:
            n=(ppm-400)/25+1
            _leds(self,gled, n)
        elif ppm<1100:
            n=(ppm-600)/50+1
            _leds(self,yled, n)
        else:
            n=(ppm-1100)/100+1
            _leds(self,rled, n)
        self.strip.show()

# Main program logic follows:
if __name__ == '__main__':
	# Create NeoPixel object with appropriate configuration.
        lstrip = my_ws_2812()
        # import ipdb;ipdb.set_trace()
        lstrip.to_level(None)
        time.sleep(3)
        lstrip.colorWipe(Color(20, 10, 20), wait_ms=50)
