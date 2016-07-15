#!/usr/bin/env python

""" Ref manual:
https://www.fullstackpython.com/blog/build-first-slack-bot-python.html
"""
import os
import time
from slackclient import SlackClient
from lib_sensors import HTU21D,mhz19

import pytz, datetime, time
import struct
import array
import threading

slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))
BOT_ID = os.environ.get("SLACK_BOT_ID")
post_channel = os.environ.get("SLACK_POST_IN")

# constants
AT_BOT = "<@" + BOT_ID + ">:"
HELP_COMMAND = "help"
warn_list = "@alexz @abubyr @max_borodavka @okosse @amatveev"
graph_link = "https://thingspeak.com/channels/127030"
HELP_MESSAGE = """Hi!For now i can understant commands:\n
status: fetch current sensors status \n\n
Current list of warned peoples:\n
{}
Btw, you can check weather history here {}""".format(warn_list,graph_link)

def get_sensors():
    sensor_ht = HTU21D()
    sensor_co2 = mhz19()
    return {'Co2 in ppm:' : sensor_co2.read_co2() , 'Temp in C:' : round(sensor_ht.read_temperature(),1),
            'Humidity in %' : round(sensor_ht.read_humidity()) }

def get_status():
    status = get_sensors()
    tz = pytz.timezone('Europe/Kiev')
    c_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    return "For time:{}\n state was:{}\nHistory is here:{}".format(c_time,status,graph_link)

def handle_command(command, channel):
    """
        Receives commands directed at the bot and determines if they
        are valid commands. If so, then acts on the commands. If not,
        returns back what it needs for clarification.
    """
    response = "Not sure what you mean. Use the *" + HELP_COMMAND + \
               "* for help."
    if command.startswith(HELP_COMMAND):
        response = HELP_MESSAGE
    elif command.startswith('status'):
        response = get_status()

    slack_client.api_call("chat.postMessage", channel=channel,
                          text=response, as_user=True)


def parse_slack_output(slack_rtm_output):
    """
        The Slack Real Time Messaging API is an events firehose.
        this parsing function returns None unless a message is
        directed at the Bot, based on its ID.
    """
    output_list = slack_rtm_output
    if output_list and len(output_list) > 0:
        for output in output_list:
            if output and 'text' in output and AT_BOT in output['text']:
                # return text after the @ mention, whitespace removed
                return output['text'].split(AT_BOT)[1].strip().lower(), \
                       output['channel']
    return None, None

def check_status(timertime=60*5):
    # it's not good time to notify someone in non-working time...
    if int(datetime.datetime.now().strftime("%H")) not in range(10,20):
        return
    # post it only in one channel
    channel = post_channel
    threading.Timer(timertime, check_status).start()
    status = get_sensors()['Co2 in ppm:']
    if status < 1400:
        return
    elif status >= 1400:
        response = "Co2 now is:{}\n I would like to propose open windows for a while...".format(status)
    elif status > 1500:
        response = "Co2 now is:{}\n Hey folks: {} time to open windows...".format(status,warn_list)
    elif status > 1800:
        response = """Co2 now is:{}!!!\n Folks: {} @here ! :nothingtodohere:\n
                      You will die in a while! OPEN WINDOWS!""".format(status,warn_list)
    slack_client.api_call("chat.postMessage", channel=channel,
                          text=response, as_user=True)

if __name__ == "__main__":
    READ_WEBSOCKET_DELAY = 1 # 1 second delay between reading from firehose
    if slack_client.rtm_connect():
        print("StarterBot connected and running!")
        check_status()
        while True:
            command, channel = parse_slack_output(slack_client.rtm_read())
            if command and channel:
                handle_command(command, channel)
            time.sleep(READ_WEBSOCKET_DELAY)
    else:
        print("Connection failed. Invalid Slack token or bot ID?")


