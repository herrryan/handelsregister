#-*- coding: UTF-8 -*-
import sys
import urllib
import urllib2
import requests
import re
from bs4 import BeautifulSoup
from xlrd import open_workbook

reload(sys)
sys.setdefaultencoding('utf8')

def remove_title(name):
    #name = "Prof. Dr. Dr. hc. mult. Hermann Felix H."
    if ("." in name.rstrip(".")):
        last_dot_pos = name.rstrip(".").rfind(".")
        print name[last_dot_pos+2:]
    else:
        print name

def read_excel_file():
    wb = open_workbook('Handelsregister_mit_filter_00.xlsx')
    firstname_list = wb.sheet_by_index(0).col_values(1, start_rowx=1);
    cleaned_list = []
    for firstname in firstname_list:
        remove_title(firstname)
        #cleaned_list.append(remove_title(firstname))
    #print cleaned_list

if __name__=='__main__':
    read_excel_file()