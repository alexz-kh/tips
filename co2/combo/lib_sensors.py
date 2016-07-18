#!/usr/bin/env python

import struct
import array
import time
import i2c_base
import serial
import datetime

class mhz19(object):
    def __init__(self):
        self.SERIAL_DEVICE = '/dev/ttyAMA0'
        self.warmup_time = 60*5

    def _get_uptime(self, return_type):
        with open('/proc/uptime', 'r') as f:
            uptime_seconds = float(f.readline().split()[0])
            uptime_string = str(datetime.timedelta(seconds = uptime_seconds))
        _is_safe = True
        # CO2 meter need few min to start
        if uptime_seconds < self.warmup_time:
            _is_safe = False
        if return_type == 'seconds':
            return uptime_seconds
        elif return_type == 'string':
            return uptime_string
        elif return_type == 'safe':
            return _is_safe

    def read_co2(self):
      """
      Can return int or None
      """
      with serial.Serial(self.SERIAL_DEVICE, baudrate=9600, timeout=1.0) as ser:
          result=ser.write("\xff\x01\x86\x00\x00\x00\x00\x00\x79")
          s=ser.read(9)
          co_result=ord(s[2])*256 + ord(s[3])
      # return None value,if sensor not warmed yet
      if not self._get_uptime('safe'):
          return None
      return co_result

class HTU21D(object):
    def __init__(self):
        self.HTU21D_ADDR = 0x40
        self.CMD_READ_TEMP_HOLD = b"\xE3"
        self.CMD_READ_HUM_HOLD = b"\xE5"
        self.CMD_READ_TEMP_NOHOLD = b"\xF3"
        self.CMD_READ_HUM_NOHOLD = b"\xF5"
        self.CMD_WRITE_USER_REG = b"\xE6"
        self.CMD_READ_USER_REG = b"\xE7"
        self.CMD_SOFT_RESET = b"\xFE"
        self.dev = i2c_base.i2c(self.HTU21D_ADDR, 1)  # HTU21D 0x40, bus 1
        self.dev.write(self.CMD_SOFT_RESET)  # Soft reset
        time.sleep(.1)

    def ctemp(self, sensor_temp):
        t_sensor_temp = sensor_temp / 65536.0
        return -46.85 + (175.72 * t_sensor_temp)

    def chumid(self, sensor_humid):
        t_sensor_humid = sensor_humid / 65536.0
        return -6.0 + (125.0 * t_sensor_humid)

    def temp_coefficient(self, rh_actual, temp_actual, coefficient=-0.15):
        return rh_actual + (25 - temp_actual) * coefficient

    def crc8check(self, value):
        # Ported from Sparkfun Arduino HTU21D Library:
        # https://github.com/sparkfun/HTU21D_Breakout
        remainder = ((value[0] << 8) + value[1]) << 8
        remainder |= value[2]

        # POLYNOMIAL = 0x0131 = x^8 + x^5 + x^4 + 1 divisor =
        # 0x988000 is the 0x0131 polynomial shifted to farthest
        # left of three bytes
        divisor = 0x988000

        for i in range(0, 16):
            if(remainder & 1 << (23 - i)):
                remainder ^= divisor
            divisor = divisor >> 1

        if remainder == 0:
            return True
        else:
            return False

    def read_temperature(self):
        self.dev.write(self.CMD_READ_TEMP_NOHOLD)  # Measure temp
        time.sleep(.1)
        data = self.dev.read(3)
        buf = array.array('B', data)
        if self.crc8check(buf):
            temp = (buf[0] << 8 | buf[1]) & 0xFFFC
            return self.ctemp(temp)
        else:
            return -255

    def read_humidity(self):
        temp_actual = self.read_temperature()  # For temperature coefficient compensation
        self.dev.write(self.CMD_READ_HUM_NOHOLD)  # Measure humidity
        time.sleep(.1)
        data = self.dev.read(3)
        buf = array.array('B', data)

        if self.crc8check(buf):
            humid = (buf[0] << 8 | buf[1]) & 0xFFFC
            rh_actual = self.chumid(humid)

            rh_final = self.temp_coefficient(rh_actual, temp_actual)

            rh_final = 100.0 if rh_final > 100 else rh_final  # Clamp > 100
            rh_final = 0.0 if rh_final < 0 else rh_final  # Clamp < 0

            return rh_final
        else:
            return -255

if __name__ == "__main__":
    sensor_ht = HTU21D()
    sensor_mhz = mhz19()
    print("Co2: %s ppm" % sensor_mhz.read_co2())
    print("Temp: %s C" % sensor_ht.read_temperature())
    print("Humid: %s %% rH" % sensor_ht.read_humidity())
