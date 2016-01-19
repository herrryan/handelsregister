#-*- coding: UTF-8 -*-
import sys
import urllib
import urllib2
import requests
import re
import time
import json
from bs4 import BeautifulSoup
from openpyxl import Workbook

reload(sys)
sys.setdefaultencoding('utf8')

#Some User Agents    
headers=[{'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6'},\
         {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.71 Safari/537.36'},\
         {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36'}];
#lawyer_ids = ["hbeed13602b9b0e6ecb5b568ff5058f07", "h4b2944dfea61be814911110c21ddd974"];
lawyer_ids = [];
info_list = [];

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

def persist_to_excel():
    wb = Workbook(optimized_write=True);
    ws = wb.create_sheet(title="anwalt")
    for info in info_list:
        ws.append(info);
    save_path='fullinfo.xlsx';
    wb.save(save_path)

def save_json():
    with open('data.txt', 'w') as outfile:
        json.dump(info_list, outfile)

def getDetailInfo():
    true_tag = ["Jahrgang", "Patentjahr", "Arbeitsgebiete", "Sprachen", "Kanzleiprofil", "Adresse", "Telefon", "Fax", "E-Mail", "Homepage"]
    for lawyer_id in lawyer_ids:
        time.sleep(1)
        print "waiting 1s to get information of", lawyer_id
        url = "http://www.zav.ch/modules/Mitglieder/templates/suche_detail_ajax.php?senderid=" + lawyer_id;
        #url = "http://www.zav.ch/modules/Mitglieder/templates/suche_detail_ajax.php?senderid=hbeed13602b9b0e6ecb5b568ff5058f07";
      #  url = "http://www.zav.ch/modules/Mitglieder/templates/suche_detail_ajax.php?senderid=h5982e32d2cd58d7f3e71f90600b59267";
        true_tags = ["Jahrgang", "Patentjahr", "Bevorzugte Arbeitsgebiete" , "Sprachen", "Fachanwältin SAV", "Kanzleiprofil", "Adresse", "Telefon", "Fax", "E-Mail", "Homepage"]
        soup = BeautifulSoup(read_withcookie(url), "html.parser");
        
        tags = soup.findAll("p", {'class': 'columns alpha three'});
        contents = soup.findAll("p", {'class' : 'columns omega five'});
        name = soup.find("h2")
        if (name == None):
            continue;
        print name.text.split(".")
        info = [];
        info.append(name.text);
        idx = 0;
        for i in range(0, len(true_tags)):
            if (idx > len(tags)-1):
                break;
            if (tags[idx].text.rstrip(":") == true_tags[i]):
                if (true_tags[i] == "Adresse"):
                    address = contents[idx].text.split("#");
                    info.append(address[0]);
                    if ("Postfach" in address[1]) :
                        info.append(address[1]);
                        info.append(address[2]);
                    else:
                        info.append("unknown");
                        info.append(address[1]);
                else:
                    info.append(contents[idx].text);
                idx += 1;
            else:
                if (true_tags[i] == "Adresse"):
                    info.append("unknown");
                    info.append("unknown");
                    info.append("unknown");
                else:
                    info.append("unknown");
        print str(info)
        info_list.append(info)

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

def read_withcookie(url):
    print "Pulling information from [%s]" % url;
    try:
        req = urllib2.Request(url, headers=headers[1]);
        req.add_header("cookie", "PHPSESSID=rgm7r2rck17riptq88iftkkvm3");
        source_code = urllib2.urlopen(req).read();
        plain_text=str(re.sub('<br/>','#', source_code));
        return plain_text;
    except (urllib2.HTTPError, urllib2.URLError), e:
        req = urllib2.Request(url, headers=headers[1]);
        req.add_header("cookie", "PHPSESSID=rgm7r2rck17riptq88iftkkvm3");
        source_code = urllib2.urlopen(req).read();
        plain_text=str(re.sub('<br/>','#', source_code));
        return plain_text;

def load_file():
    for info in info_list:
        data = json.loads(info);
        if (data['name']):
            print data['name']
        

if __name__=='__main__':
    getLawyerIds();
    getDetailInfo();
    #persist_to_file();
    #load_file();
    persist_to_excel();
    #save_json();
    #load_json();