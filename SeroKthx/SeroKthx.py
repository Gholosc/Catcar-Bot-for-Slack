import os
import time
import json
import requests
from slackclient import SlackClient
from xml.etree import ElementTree 

import openweathermap as Weather
import dictapi as Dictionary

TOKEN = open("token.txt", "r").readline().strip()

DEFN_RSP = \
"{}\n\n" +\
"_Definitions were fetched using the API for the Merriam-Webster\'s Collegiate Dictionary_ " +\
"http://goo.gl/J9BwCd"
def defineWord(message, channel, prefixLength, isAll=False):
    try: 
        word = str(message)[prefixLength:].strip()
        defn = DEFN_RSP.format(Dictionary.GetDictionaryDefnResponse(word, isAll))
        if not defn:
            raise Exception
        sc.rtm_send_message(channel, defn)
    except: 
        sc.rtm_send_message(channel, "Problem finding definition. \n")

WTHR_RSP = \
"*Weather for {}, {}:*\n" + \
"\n*Description*\n{}\n " + \
"\n*Temperature* \nCurrent: {}            Low: {}            High: {}"
def getWeather(channel, location):
    weather = Weather.GetWeather(location)
    resp = ''
    if weather:
        resp = WTHR_RSP.format(weather['city'], weather['country'],
                               weather['desc_second'], weather['temp_curr'], 
                               weather['temp_low'], weather['temp_high'])
    else:
        resp = 'Error finding weather for {0}'.format(location)
    sc.rtm_send_message(channel, resp)

sc = SlackClient(TOKEN)
if sc.rtm_connect():
    hi_count = 0
    while True:
        feed = sc.rtm_read()
       
        if feed != []:
            print "ALL: " + str(feed)

            newMsgs = [new for new in feed if u'text' in new]
            if newMsgs != []:
                for msg in newMsgs:
                        if msg['text'].lower().startswith('catcar, '):
                            message = msg['text'].lower()[len('catcar, '):]

                            # Long definition
                            if "definefull:" in message:
                                defineWord(message, str(msg[u'channel']), len('definefull:'), isAll=True)
                            if "definefull" in msg['text'].lower():
                                defineWord(message, str(msg[u'channel']), len('definefull'), isAll=True)

                            # Short definition
                            elif "define:" in message:
                                defineWord(message, str(msg[u'channel']), len('define:'))
                            elif "define" in msg['text'].lower():
                                defineWord(message, str(msg[u'channel']), len('define'))

                            # Weather
                            elif "weather in " in message:
                                weatherLoc = message[len('weather in '):]
                                getWeather(msg[u'channel'], weatherLoc)

                            # Other
                            elif "make me a sandwich" in msg['text'].lower():
                                sc.rtm_send_message(str(msg[u'channel']), "how about you go fuck off")

                            elif "sero" in message:
                                sc.rtm_send_message(str(msg[u'channel']), "IS AWESOME")

                        else:
                            message = msg['text'].lower()
                            if "define:" in message:
                                defineWord(message, str(msg[u'channel']), len('define:'))

                print "TEXT:" + str(newMsgs)
            
        time.sleep(1) # Bot API has a limit of 1 message per second.