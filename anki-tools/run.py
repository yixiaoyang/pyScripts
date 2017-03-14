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

def path_of_renrenSound(file_or_dir):
    return os.path.join(os.getcwd(), Config.SOUND_RENREN_DIR, file_or_dir)

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


def get_doc_bySelenium_waitFor(url,tagName):
    global l_tab_opened
    global l_driver
    charset = None

    if not l_driver:
        l_driver = webdriver.Chrome()
    driver = l_driver
    driver.get(url)
    try:
        element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, tagName)))
    except Exception,e:
        return None

    #print(url)

    doc = driver.page_source
    if l_tab_opened:
        driver.find_element_by_tag_name('body').send_keys(Keys.COMMAND + 'w')
    driver.find_element_by_tag_name('body').send_keys(Keys.COMMAND + 't')
    l_tab_opened = True

    return doc

def dl_byUrllib2(url, filename):
    try:
        urlretrieve(url, filename)
    except Exception,e:
        print(e)

def get_img_from_bing(word):
    imgUrl = None
    url = "https://cn.bing.com/images/search?q=%s"%(word)
    doc = get_doc_bySelenium_waitFor(url,"dg_u")
    if doc:
        soup = BeautifulSoup(doc, Config.SOUP_PARSER,from_encoding="utf-8")
        div_img = soup.find("div",class_="dg_u")
        if div_img:
            tag_img = div_img.find("img")
            if tag_img:
                imgUrl = tag_img["src"]
            else:
                print("tag_img not found")
        else:
            print ("div_img not found")
    else:
        print("doc none")
    return imgUrl

class Card:
    def __init__(self,word,rate="star0",edef="",cdef="",img="",sound="",
        phonetic="",collins="",cSentense="",eSentense="",sSentense=""):
        self.word = word
        self.rate = rate
        self.edef = edef
        # bs4.element.Tag
        self.cdef = cdef
        self.img = img
        self.sound = sound
        self.phonetic = phonetic
        self.collins = collins
        self.cSentense = cSentense
        self.eSentense = eSentense
        self.sSentense = sSentense

def get_def_from_youdao(word):
    base_def, collins = "",""
    url = "http://dict.youdao.com/w/eng/%s"%(word)
    doc = get_doc_byUrllib2(url)
    if not doc:
        logger.error("doc none")
        return base_def, collins
    soup = BeautifulSoup(doc, Config.SOUP_PARSER,from_encoding="utf-8")
    div_define = soup.find("div",id="collinsResult")
    if div_define:
        html = str(div_define)
        #html = html.replace(word, "<b class=\"keyword\">%s</b>"%(word))
        html = html.replace("\n","")
        html = html.replace("\t","")
        html = html.replace("  ","")
        collins = html
    div_base = soup.find("div",class_="trans-container")
    if div_base:
        lis = div_base.find_all("li")
        if lis:
            for li in lis:
                li_str = li.string
                if li_str:
                    base_def = base_def + li.string + "； "
    else:
        logger.error("div_base not found")
    return base_def, collins

def get_sentense_from_iciba(word):
    enStr, cnStr = "",""
    url = "http://dj.iciba.com/%s"%(word)
    doc = get_doc_bySelenium_waitFor(url,"stc_cn_txt")
    #doc = get_doc_byUrllib2(url)
    if not doc:
        logger.error("doc none")
        return enStr,cnStr
    soup = BeautifulSoup(doc, Config.SOUP_PARSER,from_encoding="utf-8")
    span_en = soup.find("span",class_="stc_en_txt")
    if span_en:
        enStr = " ".join(span_en.stripped_strings)
        if len(enStr) > 3:
            if enStr[0:3] == "1. ":
                enStr = enStr[3:]
    span_cn = soup.find("span",class_="stc_cn_txt")
    if span_cn:
        cnStr = "".join(span_cn.stripped_strings)
    enStr = enStr.replace(word, "<b class=\"keyword\">%s</b>"%(word))
    return enStr,cnStr

def get_sentense_from_renren(word):
    url = "http://www.91dict.com/seek.php?keyword=%s"%word
    mp3_file, enStr, cnStr = "","",""
    sound_url = ""
    doc = get_doc_byUrllib2(url)
    if not doc:
        logger.error("doc none from renren")
        return enStr,cnStr
    soup = BeautifulSoup(doc, Config.SOUP_PARSER,from_encoding="utf-8")
    div_rightBody = soup.find("div",id="rightBody")
    if div_rightBody:
        ps = div_rightBody.find_all("p")
        if ps:
            if len(ps) > 1:
                ps1 = ps[1]
                
                mp3_file = path_of_renrenSound("_%s.mp3"%(word))
                if True:
                #if not os.path.exists(mp3_file):
                    a_mp3 = ps1.find("a",class_="play")
                    if a_mp3:
                        if a_mp3.has_attr("onclick"):
                            sound_str = a_mp3["onclick"]
                            if len(sound_str) >= 10:
                                strings = sound_str.split("\"")
                                if len(strings) >= 2:
                                    sound_url = strings[1]
                                dl_byUrllib2(sound_url,mp3_file)
                span_sub = ps1.find("span",class_="sub-mask")
                if span_sub:
                    span_cn = ps1.find("span",class_="sub-black")
                    if span_cn:
                        cnStr = "".join(span_cn.stripped_strings)
                        span_cn.extract()

                    enStr = " ".join(span_sub.stripped_strings)

    #print(enStr)
    #print(cnStr)
    #print(sound_url)
    return enStr,cnStr
    
def parse(word):
    url = Config.BASE_URL + "/" + word
    doc = get_doc_byUrllib2(url)
    if not doc:
        logger.error("doc none")
        return None
    soup = BeautifulSoup(doc, Config.SOUP_PARSER,from_encoding="utf-8")

    if soup:
        # word rate
        card = Card(word)
        div_rate = soup.find("div",class_="word-rate")
        if div_rate:
            p_rate = div_rate.find("p")
            if p_rate:
                card.rate = p_rate["class"][0]

        # phonetic
        div_speak = soup.find("div",class_="base-speak")
        if div_speak:
            card.phonetic =  ",".join(div_speak.stripped_strings)

        # base defination
        div_base = soup.find_all("ul",class_="base-list switch_part")
        #if div_base:
        #    print(div_base.stripped_strings)
        #div_base = soup.find_all("li",class_="clearfix")
        #if div_base:
        #    card.cdef = ""
        #    for item in div_base:
        #        cdef = " ".join(item.stripped_strings)
        #        card.cdef = card.cdef+cdef+" "
        #    if len(card.cdef) > 4:
        #        card.cdef = card.cdef[:-4]
        #    card.cdef = card.cdef.replace("\t","")
        #    card.cdef = card.cdef.replace("\n"," ")
        #else:
        #    logger.debug("div_base not found")

        #card.eSentense,card.cSentense = get_sentense_from_iciba(word)
        #card.eSentense,card.cSentense = get_sentense_from_renren(word)
        #if len(card.eSentense) == 0:
        card.eSentense,card.cSentense = get_sentense_from_iciba(word)
        #else:
        #    card.sSentense = "./renren/_%s.mp3"%(word)
        #print(card.eSentense)
        #print(card.cSentense)
        
        # collins
        div_collins = soup.find("div",class_="collins-section")
        collins_def = ""
        if div_collins:
            html = str(div_collins)
            html = html.replace(word, "<b class=\"keyword\">%s</b>"%(word))
            html = html.replace("\n","")
            html = html.replace("\t","")
            html = html.replace("  ","")
            card.edef = html

        card.cdef ,card.collins = get_def_from_youdao(word)

        # 重命名文件使其以下划线开头，如“_logo.jpg”。 下划线提示Anki该文件被模板使用并在分享记忆库（牌组）时同时导出。
        # sound 
        filename = path_of_sound("_%s.mp3"%(word))
        if not os.path.exists(filename):
            tag_sound = soup.find("i",class_="new-speak-step")  
            if tag_sound:
                if tag_sound.has_attr("ms-on-mouseover"):
                    sound_str = tag_sound["ms-on-mouseover"]
                    if len(sound_str) >= 10:
                        sound_url = sound_str[7:-2]
                        #print(filename)
                        dl_byUrllib2(sound_url,filename)
                else:
                    logging.error("parse sound failed")
            else:
                logging.error("parse sound failed")
        card.sound = "./sounds/_%s.mp3"%(word)

        filename = path_of_img("_%s.jpg"%(word))
        if not os.path.exists(filename):
            imgUrl = get_img_from_bing(word)
            dl_byUrllib2(imgUrl,filename)
            #print(filename)
        card.img = "./images/_%s.jpg"%(word)
    return card

def mkcard_loop(words,filename):
    cards = {}
    total = len(words)

    num_lines = 0
    if os.path.exists(filename):
        with open(filename,'r') as fp:
            num_lines = sum(1 for line in fp)
            fp.close()
    print("file:%s, aready parsed:%d"%(filename,num_lines))

    with open(filename,'a') as fp:
        for cnt, word in enumerate(words):
            if cnt < num_lines:
                continue
            card = parse(word)
            if not card:
                continue
            cards[word] = card
            #logStr = "%d %s %s %s %s %d"%(cnt,card.word,card.rate,card.phonetic,card.cdef,len(card.edef))
            logStr = "%d/%d %s %s"%(cnt+1,total,card.word,card.cdef)
            logger.debug(logStr)

            outStr = "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n"%(card.word,card.rate,
                card.phonetic,card.cdef,card.img,card.sound, 
                card.eSentense,card.cSentense,card.collins)
            fp.write(outStr)
        fp.close()

def get_words_from_txt(fielname):
    result = []
    with open(fielname,'r') as fp:
        for line in fp.readlines():
            if len(line) > 1:
                line = line.strip()
                line = line.replace("\n","")
                result.append(line)
        fp.close()
    return result

if __name__ == "__main__":
    global l_driver

    _init()

    #get_sentense_from_renren("sustain")
    #exit(0)

    wordlist = {
        #"./wordlist/test.txt":"anki-test.txt",
        #"./wordlist/vocab-toefl-leon.txt":"anki-vocab-toefl-leon.txt",
        #"./wordlist/vocab-toefl-leon2.txt":"anki-vocab-toefl-leon2.txt",
        #"./wordlist/vocab-cet4-leon.txt":"anki-vocab-cet4-leon.txt",
        "./wordlist/word-power-mde-easy-500.txt":"anki-word-power-mde-easy-500.txt",
        #"./wordlist/vocab-top-1000.txt":"anki-vocab-top-1000.txt",   
        "./wordlist/gre-high-frequency.txt":"anki-gre-high-frequency.txt",
        "./wordlist/400-Must-have-words-for-TOEFL.txt":"anki-400-Must-have-words-for-TOEFL.txt",
    }

    for listFile,exportFile in wordlist.items():
        #if os.path.exists(exportFile):
        #   continue
        words = get_words_from_txt(listFile)
        mkcard_loop(words,exportFile)

    logger.debug("Goodbye")

    if l_driver:
        l_driver.close()
    pass
