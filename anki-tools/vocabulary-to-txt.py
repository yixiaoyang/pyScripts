#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import csv
import os
from time import sleep
import chardet
import re
import logging
import logging.handlers
import chardet

import urllib2
from urllib import urlretrieve
from urlparse import urljoin

from bs4 import BeautifulSoup
from bs4.element import Tag as Bs4Tag
from urlparse import urlparse, urljoin

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
import selenium.webdriver.support.ui as ui
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from log import setup_custom_logger
from config import Config

 # webdriver.Firefox()
l_driver = None
l_tab_opened = False

def get_doc_byUrllib2(url):
    charset = None
    headers = {
        'User-Agent':'Mozilla/5.0 (X11; Linux i686; rv:41.0) Gecko/20100101 Firefox/41.0',
        'Accept':'"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"'
    }
    req = urllib2.Request(url=url,headers=headers)
    try:
        request = urllib2.urlopen(req, timeout=Config.URL_TIMEOUT)
    except urllib2.URLError:
        return None
    except urllib2.HTTPError:
        return None
    except Exception,e:
        return None
    doc = request.read()

    # detect charset
    charset = request.headers.getparam('charset')
    if not charset:
        re_result = re.compile('charset=(.*)"').findall(doc)
        if re_result and len(re_result) > 0:
            charset = re_result[0]

    if not charset:
        result = chardet.detect(doc)
        if result:
            charset = result['encoding']

    if charset and (not charset in set(['utf-8','UTF-8'])):
        if charset in set(['gb2312','GB2312','GBK','gbk']):
            doc = unicode(doc,'gb18030')

    request.close()
    return doc


def get_doc_bySelenium(url):
    global l_tab_opened
    global l_driver
    charset = None

    if not l_driver:
        l_driver = webdriver.Chrome()
    driver = l_driver
    driver.get(url)
    try:
        element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "dg_u")))
    finally:
        pass

    print(url)

    doc = driver.page_source
    if l_tab_opened:
        driver.find_element_by_tag_name('body').send_keys(Keys.COMMAND + 'w')
    driver.find_element_by_tag_name('body').send_keys(Keys.COMMAND + 't')
    l_tab_opened = True

    return doc

def dl_byUrllib2(url, filename):
    urlretrieve(url, filename)


def get_wordlist(url,filename):
    with open(filename,'wb') as fp:
        doc = get_doc_byUrllib2(url)
        soup = BeautifulSoup(doc, Config.SOUP_PARSER,from_encoding="utf-8")
        div_words = soup.find_all("a",class_="word dynamictext")
        if div_words:
            for div_word in div_words:
                fp.write(div_word.string+"\n")
        fp.close()
        print("%s: %d words parsed"%(filename,len(div_words)))

if __name__ == "__main__":
    global l_driver

    get_wordlist("https://www.vocabulary.com/lists/52473","vocab-top-1000.txt")
    get_wordlist("https://www.vocabulary.com/lists/194479","gre-high-frequency.txt")
    get_wordlist("https://www.vocabulary.com/lists/1088364","word-power-mde-easy-500.txt")
    get_wordlist("https://www.vocabulary.com/lists/620191","400-Must-have-words-for-TOEFL.txt")

    if l_driver:
        l_driver.close()
    pass
 
