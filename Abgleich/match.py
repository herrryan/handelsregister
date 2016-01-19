#-*- coding: UTF-8 -*-
import sys
import urllib
import urllib2
import requests
import re
from bs4 import BeautifulSoup
from xlrd import open_workbook


def compare():
	register = "register_key.csv"
	anwalt = "anwalt_key.csv"
	#register_file = open(register, 'r')
	#anwalt_file = open(anwalt, 'r')
	result = "result.csv"
	result_file = open(result, 'w')
	register_list = [line.strip() for line in open(register, 'r')]
	anwalt_list = [line.strip() for line in open(anwalt, 'r')]
	for r in register_list:
		match = 0;
		for a in anwalt_list:
			if (r == a):
				match = 1
				print "match!"
				break
		result_file.write(str(match))
		result_file.write("\n")
	result_file.close()

def generate_register_key():
	#wb = open_workbook('Handelsregister.xlsx')
	#key_list_register = wb.sheet_by_index(0).col_values(7, start_rowx=1, end_rowx=None);
	input_filename = "Handelregister.csv"
	input_file = open(input_filename, 'r')

	filename = "register_key.csv";
	output_file = open(filename, 'w')
	output_file.truncate()
	for register in input_file:
		print register
		output_file.write("".join(register.split(" ")))
	output_file.close()

def generate_anwalt_key():
	filename = "AnwaltZH.csv"
	anwalt_list = open(filename, 'r')
	output = "anwalt_key.csv"
	output_file = open(output, 'w')
	output_file.truncate()
	for anwalt in anwalt_list:
		anwalt_key = remove_title(anwalt.split(",")[1]) + anwalt.split(",")[0]
		output_file.write(("").join(anwalt_key.split(" ")))
		output_file.write("\n")
	output_file.close()

def remove_title(name):
	#name = "Prof. Dr. Dr. hc. mult. Hermann Felix H."
	#name = "Saurer Peter M.\n"
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

if __name__=='__main__':
	compare();
	#print remove_title("")