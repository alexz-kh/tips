#!/bin/bash

source /root/rpi/openrc
/root/rpi/env_ws2812/bin/python /root/rpi/smart_gas/smart_gas.py >> /var/log/gas.log
