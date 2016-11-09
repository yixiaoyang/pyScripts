#!/usr/bin/python
# -*- coding: utf-8 -*- 

import os
import urllib2
import chardet
import re
from pattern.web import URL

import logging
import logging.handlers

from bs4 import BeautifulSoup
from bs4.element import Tag as Bs4Tag
from config import Config
import chardet

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
import selenium.webdriver.support.ui as ui

logger = logging.getLogger('root')
l_driver = None # webdriver.Firefox()
l_tab_opened = False


def dl_byUrllib2(url, filename):
    myurl = URL(url)
    if os.path.exists(filename):
        return
    with open(filename,'wb') as fp:
        fp.write(myurl.download(cached=False))
        fp.close()

def get_doc_byUrllib2(url,path=None,name=None,handler=None):
    charset = None
    headers = {
        'User-Agent':'Mozilla/5.0 (X11; Linux i686; rv:41.0) Gecko/20100101 Firefox/41.0',
        'Accept':'"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"'
    }

    if '.pdf' in url:
        pdfFilepath = os.path.join(path, name+'.pdf')
        htmlFilepath = os.path.join(path, name+'.html')
        dl_byUrllib2(url,pdfFilepath)
        print pdfFilepath
        call(["pdf2txt.py", "-o", htmlFilepath, pdfFilepath])
        with open(htmlFilepath,'rb') as fp:
            logger.debug("Detect pdf => html content")
            return fp.read()

    req = urllib2.Request(url=url,headers=headers)
    request = urllib2.urlopen(req, timeout=Config.URL_TIMEOUT)
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


def get_doc_bySelenium(url,path=None,name=None,handler=None):
    global l_tab_opened
    global l_driver

    charset = None

    if not l_driver:
        l_driver = webdriver.Firefox()
    driver = l_driver

    doc = None
    if handler:
        driver.get(url)
        doc = handler(driver)
    else:
        driver.get(url)

    doc = doc or driver.page_source
    if l_tab_opened:
        driver.find_element_by_tag_name('body').send_keys(Keys.COMMAND + 'w')
    driver.find_element_by_tag_name('body').send_keys(Keys.COMMAND + 't')
    l_tab_opened = True

    return doc

def selenium_close():
    if l_driver:
        l_driver.close()

l_web_engines = {
    "urllib2": get_doc_byUrllib2,
    "selenium": get_doc_bySelenium
}

class Parser:
    def __init__(self, file=None, url=None, rlist=None, encoding='utf-8', web_engine=Config.DEFAULT_WEB_ENGINE):
        self.url = url or ''
        self.rlist = rlist or list()
        self.soup = None
        self.encoding = encoding
        self.web_engine = web_engine
        self.file = file

    def parse(self):
        logger.debug("parsing...")
        pass

    def run(self):
        try:
            # get document from file or url
            doc = None
            if self.file:
                if os.path.exists(self.file):
                    logger.debug("parsing from file %s"%self.file)
                    doc = open(self.file).read()
            if not doc:
                web_engine = self.engine()
                if web_engine:
                    logger.debug("parsing from url %s"%self.url)
                    doc = web_engine(self.url)
                else:
                    logger.error("web engine %s not found" % self.web_engine)
            # parse document
            if doc:
                if self.file:
                    with open(self.file,'wb') as fp:
                        fp.write(doc)
                        fp.close()
                self.soup = BeautifulSoup(doc, Config.SOUP_PARSER,from_encoding=self.encoding)
                self.parse()
                return True
            else:
                logger.error("no document in %s" % self.url)
            return False
        except Exception as e:
            logger.error("exception '%s' captured when parsing %s" % (e, self.url))
            return False

    def engine(self):
        return l_web_engines.get(self.web_engine)
