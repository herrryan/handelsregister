#-*- coding: UTF-8 -*-
import sys
import urllib
import urllib2
import requests
import re
import time
from bs4 import BeautifulSoup
from openpyxl import Workbook

reload(sys)
sys.setdefaultencoding('utf8')

#Some User Agents    
headers=[{'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6'},\
         {'User-Agent':'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36'},\
         {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36'}];
register_list = [];
lawyer_ids = [];

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
        time.sleep(1)
        print "waiting 1s until next request"
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
    #url = "http://bs.powernet.ch/webservices/inet/hrg/hrg.asmx/getExcerpt?Chnr=CH-270.7.001.449-6&Amt=270&Lang=1&Code=20eba7e350c066ed42e19c02466bb9fb";
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
                    if (person.find('residence')):
                        wohnsitz = person.find('residence').find('city').text;
                    else:
                        wohnsitz = u'Unknown'
                    print [stiftungName, person.find('firstname').text, remove_title(person.find('firstname').text), person.find('name').text, stiftungSitzKanton, stiftungSitzStadt, wohnsitz]
                    register_list.append([stiftungName, person.find('firstname').text, remove_title(person.find('firstname').text), person.find('name').text, stiftungSitzKanton, stiftungSitzStadt, wohnsitz])

def remove_title(name):
    if ("." in name.rstrip(".")):
        last_dot_pos = name.rstrip(".").rfind(".")
        return name[last_dot_pos+2:]
    else:
        return name

def persist_to_excel(register_list):
    wb = Workbook(optimized_write=True);
    ws = wb.create_sheet(title="Handelsregister")
    ws.append(['Stiftung Name', 'Vorname', 'Cleaned Vorname', 'Nachname', 'Kanton', 'Stadt', 'Wohnsitz']);
    for register in register_list:
        ws.append([register[0],register[1], register[2], register[3], register[4], register[5], register[6]]);
    save_path='Handelsregister.xlsx';
    wb.save(save_path)

def getDetailInfo():
    #for lawyer_id in lawyer_ids:
    #    time.sleep(1)
    #    print "waiting 1s to get information of", lawyer_id
    url = "http://www.zav.ch/modules/Mitglieder/templates/suche_detail_ajax.php?senderid=h4b2944dfea61be814911110c21ddd974"
    soup = BeautifulSoup(read(url));
    print soup.findAll("p")

def getLawyerIds():
    url = "http://localhost:8000/search.html";
    soup = BeautifulSoup(read(url));
    lawyers = soup.findAll("a", {'class':'asdv'});
    count = 0;
    for lawyer in lawyers:
        count += 1;
        lawyer_ids.append(lawyer['id']);
    print count
    return lawyer_ids;

def read(url):
    print "Pulling information from [%s]" % url;
    try:
        req = urllib2.Request(url, headers=headers[1]);
        source_code = urllib2.urlopen(req).read();
        plain_text=str(source_code);
        return plain_text;
    except (urllib2.HTTPError, urllib2.URLError), e:
        req = urllib2.Request(url, headers=headers[1]);
        source_code = urllib2.urlopen(req).read();
        plain_text=str(source_code);
        return plain_text;


if __name__=='__main__':
    #getLawyerIds();
    getDetailInfo();
