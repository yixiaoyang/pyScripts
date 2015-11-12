#!/usr/bin/python
# -*- utf-8 *-*

import json
import sqlite3
import csv

from models import *
from parser import *

import sys
reload(sys)
sys.setdefaultencoding('utf-8')


# gloabel vars
colleges = list()
c211_url = 'http://www.hao123.com/eduhtm/211.htm'
china211jfile = 'china211.json'

def getCollege():
   hao123Parser = Hao123_211_Parser(c211_url)
   hao123Parser.run()
   for item in hao123Parser.rlist:
	   college = College(item['href'],item.string)
	   colleges.append(college)

def colleges2csv():
	fieldnames = ['name', 'eng_name','url']
	with open('colleges.csv','wb') as csvfp:
		writer = csv.DictWriter(csvfp, fieldnames=fieldnames, delimiter=',', 
						  quotechar='|', quoting=csv.QUOTE_MINIMAL)
		writer.writeheader()
		for c in colleges:
			writer.writerow({'name':c.name,'eng_name':c.eng_name,'url':c.url})

def csv2colleges():
	with open('colleges.csv','rb') as csvfp:
		fieldnames = ['name', 'eng_name','url']
		reader = csv.DictReader(csvfp, fieldnames=fieldnames, delimiter=',', 
						  quotechar='|', quoting=csv.QUOTE_MINIMAL)
		for row in reader:
			colleges.append(College(row['url'],row['name'],row['eng_name']))

def printColleges():
	for c in colleges:
		print("%s,%s,%s" % (c.name, c.eng_name, c.url))

if __name__ == "__main__":
	#getCollege()
	csv2colleges()
	
	#printColleges();
	#print colleges[0].to_json()
	
	# output to json
	#china211 = China211(c211_url,colleges);
	#print(china211_to_json(china211))
	
	# import from json
	china211 = china211_from_file(china211jfile)
	print(china211_to_json(china211))
	#print(china211.__class__.__name__)
