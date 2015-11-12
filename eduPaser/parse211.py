#!/usr/bin/python
# -*- coding: utf-8 -*- 

import os
import time
import urllib2
import mimetypes

from bs4 import BeautifulSoup

def dl_211():
	url = "http://www.hao123.com/eduhtm/211.htm"
	doc =  urllib2.urlopen(url).read()
	soup = BeautifulSoup(doc)
	#for content in soup.find_all(name='tr',attrs={'bgcolor':'#EFF7F0'}):
	for td in soup.find_all(name='td'):
            if td.has_attr('class'):
                continue
            elif td.has_attr('height'):
                continue
            elif td.has_attr('width'):
                if td['width'] != '21%':
                    continue
            elif len(td.contents) == 0:
                continue
           
            if td.contents[0].name != 'a':
                continue
            print (td.contents[0])

if __name__ == '__main__':
	dl_211()
