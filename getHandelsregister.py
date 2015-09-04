#-*- coding: UTF-8 -*-

import sys
import time
import urllib
import urllib2
import requests
import re
from bs4 import BeautifulSoup
from openpyxl import Workbook

reload(sys)
sys.setdefaultencoding('utf8')

#Some User Agents    
headers=[{'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6'},\
         {'User-Agent':'Mozilla/5.0 (Windows NT 6.2) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.12 Safari/535.11'},\
         {'User-Agent': 'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; Trident/6.0)'}];

def handelsregister_spider():
    register_list = [];

    firma = "stiftung"
    #url="http://zefix.admin.ch/WebServices/Zefix/Zefix.asmx/SearchFirm?name=" + firma + "&suche_nach=aktuell";
    url="http://zh.powernet.ch/webservices/inet/HRG/HRG.asmx/getHRGHTML?chnr=0207901300&amt=020&toBeModified=0&validOnly=1&lang=1&sort=0"
    print "Pulling information from [%s]" % url;

    #Last Version
    try:
        req = urllib2.Request(url, headers=headers[1]);
        source_code = urllib2.urlopen(req).read();
        plain_text=str(source_code);
    except (urllib2.HTTPError, urllib2.URLError), e:
        print e
    #plain_text = '<p><b>"Gottlieb Fischer-Stiftung" im Bergli Stans</b><i> in <a target="_top" href="https://nw.chregister.ch">Stans</a></i>, Stiftung, <a target="result" href="/WebServices/Zefix/Zefix.asmx/ShowFirm?parId=272375&amp;parChnr=CH-150.7.000.034-0&amp;language=1">+</a>, <a target="_blank" href="https://nw.chregister.ch/cr-portal/auszug/zefix.xhtml?uid=CHE-114.513.996&amp;lang=de">CHE-114.513.996</a>, <a target="_blank" href="https://nw.chregister.ch/cr-portal/auszug/zefix?uid=CHE-114.513.996&amp;lang=de">PDF</a></p>'
    soup = BeautifulSoup(plain_text);
    #all_registers_link = soup.findAll('font')[0].findAll('a')
    all_registers_link = soup.findAll(lambda tag: (tag.name == 'a' and tag.text == '<Excerpt>'), href=True)
    if all_registers_link == None:
        print "There is handelsregister yet.";
        return;
    for register_link in all_registers_link:
        print register_link['href']
    
    return register_list



if __name__=='__main__':
    register_list = handelsregister_spider();
