#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
从扇贝口语网站下载练习材料并制作成anki卡片
'''

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

logger = None
 # webdriver.Firefox()
l_driver = None
l_tab_opened = False

def _init():
    global  logger

    reload(sys)
    sys.setdefaultencoding('utf-8')

    mlog = setup_custom_logger("root")
    mlog.debug("setup logger")

    logger = logging.getLogger('root')


def path_of_img(file_or_dir):
    return os.path.join(os.getcwd(), Config.IMG_DIR, file_or_dir)

def path_of_sound(file_or_dir):
    return os.path.join(os.getcwd(), Config.SOUND_DIR, file_or_dir)

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

class Card:
    def __init__(self,pTopic="",cTopic="",sound="",eSentense=""):
        self.pTopic = pTopic
        self.cTopic = cTopic
        self.sound = sound
        self.eSentense = eSentense

class Topic:
    def __init__(self,name):
        self.name = name
        self.children = []

def mkcard_loop(words,filename):
    cards = {}
    total = len(words)
    with open(filename,'wb') as fp:
        for cnt, word in enumerate(words):
            card = parse(word)
            cards[word] = card
            #logStr = "%d %s %s %s %s %d"%(cnt,card.word,card.rate,card.phonetic,card.cdef,len(card.edef))
            logStr = "%d/%d %s %s"%(cnt+1,total,card.word,card.cdef)
            logger.debug(logStr)

            outStr = "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n"%(card.word,card.rate,
                card.phonetic,card.cdef,card.img,card.sound, 
                card.eSentense,card.cSentense,card.collins)
            fp.write(outStr)
        fp.close()

def get_list_from_url(url):
    result = []
    doc = get_doc_byUrllib2(url)
    if not doc:
        logger.error("get url failed")
        return None

    soup = BeautifulSoup(doc, Config.SOUP_PARSER,from_encoding="utf-8")
    div_classes = soup.find_all("li",class_="unit-item clearfix")
    if div_classes:
        for div in div_classes:
            topic = None
            topic_name = None
            
            div_topic = div.find("div",class_="unit-title clearfix")
            if div_topic:
                topic_name = "".join(div_topic.stripped_strings)
            else:
                continue

            topic = Topic(topic_name)

            div_links = div.find_all("a")
            if div_links:
                for link in div_links:
                    name = "".join(link.stripped_strings)
                    url = "".join(Config.SHANBAY_ROOT+link["href"])
                    topic.children.append({name:url})

            if topic:
                logger.debug("topic:%s, %s"%(topic.name,topic.children))
                result.append(topic)
    else:
        logger.error("get div_classes failed")
    return result

def parse(topic):
    for cTopic,url in topic.children.items():
        card = Card(pTopic=topic.name, cTopic=cTopic)
        doc = get_doc_byUrllib2(url)
        soup = BeautifulSoup(doc, Config.SOUP_PARSER,from_encoding="utf-8")
        div_items = soup.find("div",class_="dialog-items")


if __name__ == "__main__":
    global l_driver

    _init()

    topic_urls = {
        "生存口语：背包游记":"https://www.shanbay.com/speak/courses/xbxai"
    }

    for key,url in topic_urls.items():
        topList = get_list_from_url(url)
        if topList:
            for topic in topList:
                card = parse(topic)

    logger.debug("Goodbye")

    if l_driver:
        l_driver.close()
    pass
