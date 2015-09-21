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

def read_excel_file():
    wb = open_workbook('AnwaltZH_raw.xlsx')
    first_column = wb.sheet_by_index(0).col_values(0, start_rowx=0, end_rowx=5946);
    cleaned_list = []
    filename = "AnwaltZH.csv"
    target = open(filename, 'w')
    target.truncate()
    for entry in first_column[::2]:
        #print entry
        target.write(entry)
        target.write("\n")
    target.close()

if __name__=='__main__':
    read_excel_file()