import requests
from slackclient import SlackClient
from xml.etree import ElementTree 

DictApiKey = open("dictapikey.txt", "r").readline().strip()
EnglishDictURL = 'http://www.dictionaryapi.com/api/v1/references/collegiate/xml/{0}?key={1}'
XmlTagsRmv = ['<aq>', '</aq>', '<ca>', '</ca>', '<cat>', '</cat>', '<dx>', '</dx>', '<dxn>', '</dxn>',
              '<dxt>', '</dxt>', '<g>', '</g>', '<it>', '</it>', '<sx>', '</sx>', '<sxn>', '</sxn>', 
              '<un>', '</un>', '<ri>', '</ri>', '<va>', '</va>', '<vi>', '</vi>', '<vr>', '</vr>', 
              '<vl>', '</vl>', '<fw>', '</fw>', '<d_link>', '</d_link>']


def _terribleXMLParsing(xmlDef):
    ''' Stop using XML if JSON is better suited to the purpose PLEASE.
        Hardcoded for use with dictionaryapi '''
    xml = xmlDef
    defns = []
    while xml.find('<dt>') != -1:
       indivDefn = xml[xml.find('<dt>')+4 : xml.find('</dt>')].strip(' :')
       defns.append(indivDefn)
       xml = xml[xml.find('</dt>')+5:]
    return defns

def _isolateSingleEntry(xml):
    ''' Meriam-Webster API provides several suggests within seperate <entry id="foo"> tags.
    Just get the first one. '''
    isolated =  xml[xml.find('<entry') : xml.find('</entry>')]
    print "ISOLATED: " + isolated
    return isolated

def _format(defnList, isAll=False):
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

def _getDictDefnResponse(word, isAll=False):
    title = '*Dictionary definition(s) for \'' + word[0].upper() + word[1:].lower() + '\':*' 

    rsp = requests.get(EnglishDictURL.format(word, DictApiKey)).content
    rsp = _isolateSingleEntry(rsp)
    
    hasMultipleEntries = rsp.find('<sn>') != -1
    if hasMultipleEntries: 
        definition = rsp[rsp.find('<sn>') : rsp.rfind('</dt>') + 5]
    else:
        definition = rsp[rsp.find('<dt>') : rsp.rfind('</dt>') + 5]

    for tag in XmlTagsRmv: definition = definition.replace(tag, '')
    definition = definition.replace(' :', ' -- ')

    defnList = _terribleXMLParsing(definition)
    formatted = _format(defnList, isAll)
    if formatted.strip() == '':
        formatted = "\nCould not find definition :tumbleweed:" 
    return title + formatted

def GetDictionaryDefnResponse(word, isAll=False):
    try:
        return _getDictDefnResponse(word, isAll=False)
    except:
        pass

