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
    #name = "Andreas B."
    if ("." in name.rstrip(".")):
        last_dot_pos = name.rstrip(".").rfind(".")
        inter_result = name[last_dot_pos+2:]
        if ("." in inter_result):
            name_array = inter_result.split(" ")
            return (" ").join(name_array[:-1])
        else:
            return inter_result
    else:
        if ("." in name):
            name_array = name.split(" ")
            return (" ").join(name_array[:-1])
        else:
            return name

def read_excel_file():
    wb = open_workbook('Handelsregister.xlsx')
    firstname_list = wb.sheet_by_index(0).col_values(1, start_rowx=1, end_rowx=None);
    cleaned_list = []
    filename = "cleaned.csv"
    target = open(filename, 'w')
    target.truncate()
    for firstname in firstname_list:
        #print firstname
        target.write(remove_title(firstname))
        target.write("\n")
    target.close()
        #cleaned_list.append(remove_title(firstname))
    #print cleaned_list

if __name__=='__main__':
    read_excel_file()
    #print remove_title("Marcel André")