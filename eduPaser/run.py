#!/usr/bin/python
# -*- utf-8 *-*

import json
import sqlite3
import csv
import sys

import logging  
import logging.handlers  

from models import *
from parser import *
from log import *

# gloabel vars
l_dump = False
l_colleges = list()
l_c211_url = 'http://www.hao123.com/eduhtm/211.htm'
# out
l_out_dir = 'out'
l_csv_file = 'colleges.csv'
l_china211jfile = 'china211.json'
logger = None
china211 = None

def path_of(file_or_dir):
	return  os.path.join(os.getcwd(), l_out_dir,file_or_dir)

def colleges_to_csv():
	fieldnames = ['name', 'eng_name','url']
	with open(path_of(l_csv_file),'wb') as csvfp:
		writer = csv.DictWriter(csvfp, fieldnames=fieldnames, delimiter=',', 
						  quotechar='|', quoting=csv.QUOTE_MINIMAL)
		#writer.writeheader()
		for c in l_colleges:
			writer.writerow({'name':c.name,'eng_name':c.eng_name,'url':c.url})
		csvfp.close()
	logger.info("All %d colleges save to %s done" % (len(l_colleges),path_of(l_csv_file)));

def csv_to_colleges():
	with open(path_of(l_csv_file),'rb') as csvfp:
		fieldnames = ['name', 'eng_name','url']
		reader = csv.DictReader(csvfp, fieldnames=fieldnames, delimiter=',', 
						  quotechar='|', quoting=csv.QUOTE_MINIMAL)
		for row in reader:
			l_colleges.append(College(row['url'],row['name'],row['eng_name']))
		csvfp.close()
	logger.info("All %d colleges laod from to %s done" % (len(l_colleges),path_of(l_csv_file)));

def printColleges():
	for c in l_colleges:
		print("%s,%s,%s" % (c.name, c.eng_name, c.url))

def make_output_dirs():
	for c in l_colleges:
		path = path_of(c.name)
		logger.debug(path)
		if not os.path.isdir(path):
			os.mkdir(path)
		print("%s,%s,%s" % (c.name, c.eng_name, c.url))


def _init():
	#l_dump = True
	l_dump = False
		
	# set encoding
	reload(sys)
	sys.setdefaultencoding('utf-8')

	logger = setup_custom_logger("root")
	logger.debug("setup logger")

	path = path_of('')
	if not os.path.isdir(path):
		os.mkdir(path)
		logger.debug("mkdir %s"%path)

if __name__ == "__main__":
	_init()
	logger = logging.getLogger('root')

	ans=True
	while ans:
		print ("""
-------------------------------------------------
			0.Exit
			1.Fetch colleges save to csv
			2.Fetch colleges from csv
			3.Make output dirs
			4.Test Academies parser
-------------------------------------------------
		""")
		ans=raw_input("\t\t\tWhat would you like to do? ") 
		if ans=="0": 
			logger.debug("\n Goodbye")
			break 
		elif ans=="1":
			logger.debug ("load from %s" % l_c211_url)
			hao123Parser = Hao123_211_Parser(l_c211_url)
			hao123Parser.run()
			l_colleges = hao123Parser.rlist
			china211 = China211(l_c211_url,l_colleges);
			colleges_to_csv()
			obj_to_file(china211,path_of(l_china211jfile))
		elif ans=="2":
			csv_to_colleges()
			printColleges()
			china211 = China211(l_c211_url,l_colleges);
		elif ans=="3":
			make_output_dirs()	
		elif ans=="4":	
			china211 = obj_from_file(path_of(l_china211jfile))
			logger.debug("china211(%d colleges) load from json done"%(len(china211.colleges)))
			for college in china211.colleges:				
				# do something
				logger.debug('parsing [%s], url:[%s]'%(college.name,college.academiesUrl))
				aparser = SimpleAParser(college.academiesUrl,college.rule)
				aparser.run()
				#if len(aparser.rlist) != 0:
				#	print(aparser.rlist)
				
				for tag in aparser.rlist:
					college.academies.append(Academy(tag['href']))
				obj_to_file(college,path_of("%s/%s.json"%(college.name,college.eng_name)))
				#FIXME
				break;
		elif ans=="4":
			print("\n Goodbye") 
		else:
			ans = True
