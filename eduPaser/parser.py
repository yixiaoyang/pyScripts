#!/usr/bin/python
# -*- coding: utf-8 -*- 

import os
import time
import urllib2
import mimetypes
import logging  
import logging.handlers  

from bs4 import BeautifulSoup

from models import *

logger = logging.getLogger('root')

class Parser():
	def __init__(self,url,rlist=None):
		self.url = url
		self.rlist = rlist or list()
		self.soup = None
	def parse(self):
		logger.debug("parsing...");
		pass
	def run(self):
		try:
			logger.debug("running...");
			request =  urllib2.urlopen(self.url, timeout=30)
			doc =  request.read()
			request.close()
			self.soup = BeautifulSoup(doc)
			self.parse()
		# ValueError
		except Exception  as e:
			logger.error("%s:%s"%(e,self.url))
		finally:
			pass

# url = "http://www.hao123.com/eduhtm/211.htm"
class Hao123_211_Parser(Parser):
	logger.debug("parsing...");
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
				item = td.contents[0]
				college = College(item['href'],item.string)
				self.rlist.append(college)

class SimpleAParser(Parser):
	def __init__(self,url,rule,rlist=None):
		Parser.__init__(self,url,rlist)
		self.rule = rule
	def check(self,tag,attr,value):
		if len(value) == 0 or len(attr) == 0:
			return False
		if value.__class__.__name__ == 'unicode':
			if tag.has_attr(attr):
				if tag[attr] == value:
					return True
		elif value.__class__.__name__ == 'bool':
			if tag.has_attr(attr) == value:
				return True
		elif value.__class__.__name__ == 'dict':
			pass 
		return False
	def parse(self):
		logger.debug("parsing...");
		if not self.rule:
			logger.error("Rule should has a tag")
			return
		if self.soup:
			logger.debug("url:%s",(self.url))
			for tag in self.soup.find_all(name=self.rule.tag):
				for attr,value in self.rule.attrDict.items():
					if not self.check(tag,attr,value):
						continue
				self.rlist.append(tag)




l_parsers = {
	"Parser":Parser,
	"SimpleAParser":SimpleAParser,
}
