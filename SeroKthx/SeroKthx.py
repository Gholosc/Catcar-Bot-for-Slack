import os
import time
import json
import requests
from slackclient import SlackClient
from xml.etree import ElementTree 

TOKEN = open("token.txt", "r").readline().strip()
DictApiKey = open("dictapikey.txt", "r").readline().strip()
EnglishDictURL = 'http://www.dictionaryapi.com/api/v1/references/collegiate/xml/{0}?key={1}'
XmlTagsRmv = ['<aq>', '</aq>', '<ca>', '</ca>', '<cat>', '</cat>', '<dx>', '</dx>', '<dxn>', '</dxn>',
              '<dxt>', '</dxt>', '<g>', '</g>', '<it>', '</it>', '<sx>', '</sx>', '<sxn>', '</sxn>', 
              '<un>', '</un>', '<ri>', '</ri>', '<va>', '</va>', '<vi>', '</vi>', '<vr>', '</vr>', 
              '<vl>', '</vl>', '<fw>', '</fw>', '<d_link>', '</d_link>']

def terribleXMLParsing(xmlDef):
    ''' Stop using XML if JSON is better suited to the purpose PLEASE.
        Hardcoded for use with dictionaryapi '''
    xml = xmlDef
    defns = []
    while xml.find('<dt>') != -1:
       indivDefn = xml[xml.find('<dt>')+4 : xml.find('</dt>')].strip(' :')
       defns.append(indivDefn)
       xml = xml[xml.find('</dt>')+5:]
    return defns

def isolateSingleEntry(xml):
    ''' Meriam-Webster API provides several suggests within seperate <entry id="foo"> tags.
    Just get the first one. '''
    isolated =  xml[xml.find('<entry') : xml.find('</entry>')]
    print "ISOLATED: " + isolated
    return isolated

def format(defnList, isAll=False):
    lis = defnList
    finalStr = ''
    if isAll:
        count = 0
        for defn in lis:
            count += 1 
            defn = defn.strip()
            defn = defn[0].upper() + defn[1:]
            finalStr += '\n{0}) {1}'.format(count, defn)
    else:
        lis = lis[:4]
        count = 0
        for defn in lis:
            count += 1
            defn = defn.strip()
            defn = defn[0].upper() + defn[1:]
            finalStr += '\n{0}) {1}'.format(count, defn)
    return finalStr

def getDictDefnResponse(word, isAll=False):
    title = '*Dictionary definition(s) for \'' + word[0].upper() + word[1:].lower() + '\':*' 

    rsp = requests.get(EnglishDictURL.format(word, DictApiKey)).content
    rsp = isolateSingleEntry(rsp)
    
    hasMultipleEntries = rsp.find('<sn>') != -1
    if hasMultipleEntries: 
        definition = rsp[rsp.find('<sn>') : rsp.rfind('</dt>') + 5]
    else:
        definition = rsp[rsp.find('<dt>') : rsp.rfind('</dt>') + 5]

    for tag in XmlTagsRmv: definition = definition.replace(tag, '')
    definition = definition.replace(' :', ' -- ')

    defnList = terribleXMLParsing(definition)
    formatted = format(defnList, isAll)
    if formatted.strip() == '':
        formatted = "\nCould not find definition :tumbleweed:" 
    return title + formatted

def defineWord(message, channel, prefixLength, isAll=False):
    try: 
        word = str(message)[prefixLength:].strip()
        defn = getDictDefnResponse(word, isAll)

        defn += '\n\n_Definitions were fetched using the API for the Merriam-Webster\'s Collegiate Dictionary_ '
        defn += 'http://goo.gl/J9BwCd'
        sc.rtm_send_message(channel, defn)
    except: 
        sc.rtm_send_message(channel, "Problem finding definition. \n")

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

                            if "definefull:" in message:
                                defineWord(message, str(msg[u'channel']), len('definefull:'), isAll=True)
                            if "definefull" in msg['text'].lower():
                                defineWord(message, str(msg[u'channel']), len('definefull'), isAll=True)

                            elif "define:" in message:
                                defineWord(message, str(msg[u'channel']), len('define:'))
                            elif "define" in msg['text'].lower():
                                defineWord(message, str(msg[u'channel']), len('define'))

                            elif "sero" in msg['text'].lower():
                                sc.rtm_send_message(str(msg[u'channel']), "IS AWESOME")

                            elif "make me a sandwich" in msg['text'].lower():
                                sc.rtm_send_message(str(msg[u'channel']), "how about you go fuck off")
                        else:
                            message = msg['text'].lower()
                            if "define:" in message:
                                defineWord(msg['text'].lower(), str(msg[u'channel']), len('define:'))

                            #if "hello" in msg['text'].lower() or "hey" in msg['text'].lower() or "hi there!" in msg['text'].lower():
                            #    hi_count += 1
                            #    if hi_count < 30: 
                            #        sc.rtm_send_message(str(msg[u'channel']), "hi")
                            #    else: 
                            #        sc.rtm_send_message(str(msg[u'channel']), "go fuck yourself")
                            #        hi_count = 0

                            if "Ok." in message:
                                sc.rtm_send_message(str(msg[u'channel']), "kthx, sero is cool")

                print "TEXT:" + str(newMsgs)
            
        time.sleep(1) # Bot API has a limit of 1 message per second.