#!/bin/bash

source /root/rpi/smart_gas/openrc
/root/rpi/env_ws2812/bin/python /root/rpi/smart_gas/home_temp.py >> /var/log/temp.log
