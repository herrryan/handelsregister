#-*- coding: UTF-8 -*-
import sys
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
register_list = [];

def handelsregister_spider():
    for pageNum in range(0, 10500, 1500):
        getRegisterHtml(pageNum)

def getRegisterHtml(pageNum):
    register_list = [];

    firma = "stiftung"
    url="http://zefix.admin.ch/WebServices/Zefix/Zefix.asmx/SearchFirm?name=" + firma + "&suche_nach=aktuell&posMin=" + str(pageNum);
    soup = BeautifulSoup(read(url));
    all_registers_link = soup.findAll('font')[0].findAll('a', href=True)
    if all_registers_link == None:
        print "There is handelsregister yet.";
        return;
    count = 0;
    for register_link in all_registers_link:
        if "HTML" in register_link['href']:
            count += 1
            getXmlLink(register_link['href'])
    print count
    return register_list

def getXmlLink(url):
    soup = BeautifulSoup(read(url));
    excerpt = soup.findAll(lambda tag: (tag.name == 'a' and tag.text == '<Excerpt>'), href=True)
    if (excerpt):
        xml_link = excerpt[0]['href']
        parseXml(xml_link);
    else:
        print "empty found"
        return;
    print xml_link

def parseXml(url):
    #url = "http://be.powernet.ch/webservices/inet/hrg/hrg.asmx/getExcerpt?Chnr=CH-092.7.002.980-9&Amt=36&Lang=1&Code=5cd792dec3687030282338e41528575d";
    xmlsoup = BeautifulSoup(read(url));
    if (xmlsoup.find("native", {'status': '1'})):
        stiftungName = xmlsoup.find("native", {'status': '1'}).text.replace("\"","").strip()
        if ("Personalfürsorgestiftung" not in stiftungName or 
            "Wohlfahrtsstiftung" not in stiftungName or 
            "Fürsorgestiftung" not in stiftungName or 
            "BVG-Personalfürsorgestiftung" not in stiftungName):

            stiftungSitzKanton = xmlsoup.find("canton").text;
            stiftungSitzStadt = xmlsoup.findAll("seat", {'status': '1'})[0].find('seattext').text;
            persons = xmlsoup.findAll("person", {'status': '1'})
            for person in persons:
                if (person.find('firstname') and person.find('name')):
                    print [stiftungName, person.find('firstname').text, remove_title(person.find('firstname').text), person.find('name').text, stiftungSitzKanton, stiftungSitzStadt]
                    register_list.append([stiftungName, person.find('firstname').text, remove_title(person.find('firstname').text), person.find('name').text, stiftungSitzKanton, stiftungSitzStadt])

def remove_title(name):
    if ("." in name.rstrip(".")):
        last_dot_pos = name.rstrip(".").rfind(".")
        return name[last_dot_pos+2:]
    else:
        return name

def persist_to_excel(register_list):
    wb = Workbook(optimized_write=True);
    ws = wb.create_sheet(title="Handelsregister")
    ws.append(['Stiftung Name', 'Vorname', 'Cleaned Vorname', 'Nachname', 'Kanton', 'Stadt']);
    for register in register_list:
        ws.append([register[0],register[1], register[2], register[3], register[4], register[5]]);
    save_path='Handelsregister.xlsx';
    wb.save(save_path)

def read(url):
    print "Pulling information from [%s]" % url;
    try:
        req = urllib2.Request(url, headers=headers[0]);
        source_code = urllib2.urlopen(req).read();
        plain_text=str(source_code);
        return plain_text;
    except (urllib2.HTTPError, urllib2.URLError), e:
        print e


if __name__=='__main__':
    handelsregister_spider();
    #parseXml("")
    persist_to_excel(register_list)
