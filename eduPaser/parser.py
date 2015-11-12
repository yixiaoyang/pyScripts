#!/usr/bin/python
# -*- coding: utf-8 -*- 

import os
import time
import urllib2
import mimetypes
from bs4 import BeautifulSoup

from models import *

class Parser():
	def __init__(self,url,rlist=None):
		self.url = url
		self.rlist = rlist or list()
		self.soup = None
	def parse(self):
		pass
	def run(self):
		request =  urllib2.urlopen(self.url, timeout=30)
		doc =  request.read()
		request.close()
		self.soup = BeautifulSoup(doc)
		self.parse()
		pass

# url = "http://www.hao123.com/eduhtm/211.htm"
class Hao123_211_Parser(Parser):
	def parse(self):
		if self.soup:
			for td in self.soup.find_all(name='td'):
				if td.has_attr('class'):
					continue
				
				if td.has_attr('height'):
					continue
				
				if td.has_attr('width'):
					if td['width'] != '21%':
						continue
				
				if len(td.contents) == 0:
					continue
				
				if td.contents[0].name != 'a':
					continue
				
				#print td.contents[0]
				self.rlist.append(td.contents[0])


