#-*- coding: UTF-8 -*-
import sys 
import urllib 
import urllib2 
import re
import time
import random
from bs4 import BeautifulSoup
from openpyxl import Workbook

reload(sys) 
sys.setdefaultencoding('utf8') 
info = [];
#Some User Agents 
headers=[{'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6'},\
		 {'User-Agent':'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36'},\
		 {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36'}];

proxies = [None];

def initiate():
	print "Initiate Search on SAV website..."
	data=urllib.urlencode({'ort' : '',
							'plz': '',
							'umkreis': '200',
							'kanton_id[]': '',
							'sprache_id[]': '',
							'geschlecht':'',
							'sav_code[]': '',
							'sav_fachanwalt_id': '',
							'sav_fachanwalt_id_mediation': '',
							'name': '',
							'vorname': '',
							'suche': 'suchen'})
	#url="http://www.sav-fsa.ch/de/anwaltssuche.html?"; 
	url = "http://suche.sav-fsa.ch/de/anwaltssuche.iframe.html?"
	soup = BeautifulSoup(post(url, data), 'html.parser');
	ids = retrieveUserId(soup);
	for aid in ids:
		time.sleep(1)
		getDetailInfo(aid);
	spider()
def spider():
	for pageNum in range(0, 10, 10):
		print "Getting Anwalt Id Number {} - {}" .format(pageNum + 1 , pageNum + 10)
		anwalt_ids = getSavHtmlAtPage(pageNum);
		print "The SVA ids of current page is ";
		print map("{}".format, anwalt_ids);
		for anwalt in anwalt_ids:
			time.sleep(1)
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
	#detail_url = "https://www.sav-fsa.ch/modules/Anwaltssuche/templates/detail.ajax.php";
	detail_url = "http://suche.sav-fsa.ch/modules/Anwaltssuche/templates/detail.ajax.php";
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
	url = "http://suche.sav-fsa.ch/de/anwaltssuche.iframe.html?"
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
		header = random.choice(headers);
		proxy = random.choice(proxies);
		if proxy == None:
			print "No proxy used"
			proxy_support = urllib2.ProxyHandler({})
		else:
			print "Switched to proxy %s" % proxy
			proxy_support = urllib2.ProxyHandler({'http':proxy})
		opener = urllib2.build_opener(proxy_support);
		urllib2.install_opener(opener);
		req = urllib2.Request(url, data=data, headers=header);
		req.add_header('cookie', 'visit=a9pbgokhlfrqavge2fmtpmat55; PHPSESSID=a9pbgokhlfrqavge2fmtpmat55'); 
		response = urllib2.urlopen(req).read();
		return response; 
	except (urllib2.HTTPError, urllib2.URLError), e: 
		print e;

def get_proxy():
	# 使用全局变量,修改之
	global proxies
	try:
		# 试图获取西刺代理的 IP 列表
		req = urllib2.Request('http://www.xicidaili.com/',None,headers)
	except:
		print('无法获取代理信息!')
		return
	response = urllib.request.urlopen(req)
	html = response.read().decode('utf-8')
	p = re.compile(r'''<tr\sclass[^>]*>\s+
									<td>.+</td>\s+
									<td>(.*)?</td>\s+
									<td>(.*)?</td>\s+
									<td>(.*)?</td>\s+
									<td>(.*)?</td>\s+
									<td>(.*)?</td>\s+
									<td>(.*)?</td>\s+
								</tr>''',re.VERBOSE)
	proxy_list = p.findall(html)
	for each_proxy in proxy_list[1:]:
		if each_proxy[4] == 'HTTP':
			proxies.append(each_proxy[0]+':'+each_proxy[1])

if __name__=='__main__': 
	initiate();
	#spider();
	#persist_to_excel(info);
	#get_proxy()
	#print proxies
