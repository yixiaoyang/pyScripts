#!/usr/bin/python
# -*- coding: utf-8 *-*

from bs4 import BeautifulSoup
from urlparse import urlparse
from urlparse import urljoin
import urllib2
import sys


aca_strings = [u'院系设置', u'学院设置', u'院系总揽', u'学院部门', u'院部设置', u'教学单位', u'机构设置', u'院所设置', u'院系部门', u'二级学院',
			u'院系', u'学院（系）', u'院系总览', u'<span>专业学院</span>',u'院系导航', u'院系介绍',u'教学院部']

doc = None
with open('tj.html','rb') as fp:
	doc = fp.read()
	fp.close()

soup = BeautifulSoup(doc,"html.parser")
#soup = BeautifulSoup(doc,"lxml")
res = soup.find_all("a",string=aca_strings)
print (len(res))
for i, r in enumerate(res):
    print r
