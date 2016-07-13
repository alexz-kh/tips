#!/usr/bin/env python

import serial
import requests
import time


def mh_z19():
  with serial.Serial('/dev/ttyUSB0', baudrate=9600, timeout=1.0) as ser:
      result=ser.write("\xff\x01\x86\x00\x00\x00\x00\x00\x79") ; s=ser.read(9); 
      co_result=ord(s[2])*256 + ord(s[3])
  return co_result


value = mh_z19()
print "Co2: %s" % value
requests.get('https://api.thingspeak.com/update?api_key=X3FRUHF0JRLA0ODF&field1={}'.format(value))
#time.sleep(60)
