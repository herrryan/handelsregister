#-*- coding: UTF-8 -*-
import sys 
import urllib 
import urllib2 
import re 
import time
from bs4 import BeautifulSoup
from openpyxl import Workbook

reload(sys) 
sys.setdefaultencoding('utf8') 
info = [];
#Some User Agents 
headers=[{'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6'},\
         {'User-Agent':'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36'},\
         {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36'}];
def spider():
	for pageNum in range(0, 10, 10):
		print "Getting Anwalt Id Number {} - {}" .format(pageNum + 1 , pageNum + 10)
		anwalt_ids = getSavHtmlAtPage(pageNum);
		print "The SVA ids of current page is ";
		print map("{}".format, anwalt_ids);
		for anwalt in anwalt_ids:
			print "Retrieving information from anwalt {}".format(anwalt);
			getDetailInfo(anwalt);

def persist_to_excel(info):
    wb = Workbook(optimized_write=True);
    ws = wb.create_sheet(title="Anwalt_Info")
    ws.append(['Name', 'Email', 'Kanton']);
    for i in info:
        ws.append([i[0],i[1], i[2]]);
    save_path='SVA.xlsx';
    wb.save(save_path)

def getDetailInfo(id):
	data=urllib.urlencode({'sav_person_id' : id})
	detail_url = "https://www.sav-fsa.ch/modules/Anwaltssuche/templates/detail.ajax.php";
	soup = BeautifulSoup(post(detail_url, data), 'html.parser');
	email = retrieveEmailAddress(soup);
	kanton = retrieveKanton(soup);
	name = retrieveName(soup);
	print [name, email, kanton]
	info.append([name, email, kanton]);

def retrieveName(soup):
	name = soup.find('h2');
	return name.text;
	
def retrieveKanton(soup):
	candidates = soup.findAll('label', {'class', 'left'});
	for c in candidates:
		if (c.text == 'Registerkanton:'):
			return c.next_sibling.text;
			
def retrieveEmailAddress(soup):
	candidates = soup.findAll('a', href=True);
	for c in candidates:
		if ('mailto' in c['href']):
			return c['href'].split(':')[1];
	
def getSavHtmlAtPage(pageNum): 
	data=urllib.urlencode({'naechste' : pageNum}); 
	url="http://www.sav-fsa.ch/de/anwaltssuche.html?"; 
	soup = BeautifulSoup(post(url, data), 'html.parser');
	return retrieveUserId(soup);


def retrieveUserId(soup):
	ids = [];
	result_table = soup.find('table', {'class': 'suchresultat'});
	table_rows = result_table.findAll('tr');
	for tr in table_rows:
		if (tr.has_attr('id')):
			ids.append(tr['id']);
	return ids;
	
	
def post(url, data): 
	#print "Pulling information from [%s]" % url; 
	try: 
		req = urllib2.Request(url, data=data, headers=headers[1]); 
		req.add_header('cookie', 'visit=a9pbgokhlfrqavge2fmtpmat55; PHPSESSID=a9pbgokhlfrqavge2fmtpmat55'); 
		response = urllib2.urlopen(req).read(); 
		return response; 
	except (urllib2.HTTPError, urllib2.URLError), e: 
		print e; 

if __name__=='__main__': 
	spider();
	persist_to_excel(info);
