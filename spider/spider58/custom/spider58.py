#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import csv
import os
import imp
from time import sleep
from urlparse import urljoin

import urllib2
import chardet
import re
import logging
import logging.handlers
import chardet
from bs4 import BeautifulSoup
from bs4.element import Tag as Bs4Tag
from urlparse import urlparse, urljoin

"""
获取url内容
"""
def get_doc_byUrllib2(url):
    charset = None
    headers = {
        'User-Agent':'Mozilla/5.0 (X11; Linux i686; rv:41.0) Gecko/20100101 Firefox/41.0',
        'Accept':'"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"'
    }
    req = urllib2.Request(url=url,headers=headers)
    request = urllib2.urlopen(req, timeout=10)
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

class Info:
    url = None
    title = None

class Parser58:
    def __init__(self,url):
        self.url = url
        self.soup = None
        self.doc = None
        self.infos = {}

    def parse(self):
        have_news = False
        fp = open('infos.data', 'a+')

        self.doc = get_doc_byUrllib2(self.url)
        self.soup = BeautifulSoup(self.doc, "html.parser", from_encoding="utf-8")
        trs = self.soup.select('a.t')

        if trs == None or len(trs) == 0:
            return
        for a in trs:
            info = Info()
            info.url = a['href']
            info.title = a.string
            if not self.infos.has_key(info.title):
                self.infos[info.title] = info
                fp.write("<a href=\"%s\">%s</a><br>\n" % (info.url, info.title))
                have_news = True
                print("%s" % (info.title))
        if have_news:
            # 2500Hz, 200ms
            os.system("beep -f 1000 -l 200")
        fp.close()
    def parse2(self):
        have_news = False
        fp = open('infos.data', 'a+')

        print("--------------------------------------------")
        self.doc = get_doc_byUrllib2(self.url)
        self.soup = BeautifulSoup(self.doc, "html.parser", from_encoding="utf-8")
        trs = self.soup.find('tr')

        if trs == None or len(trs) == 0:
            return
        for tr in trs:
            print(tr)
            ass = tr.find("a")
            for a in tr:
                print(a)
        fp.close()

"""
主函数
1. 下载主页面
2. 分析主页面中的感兴趣的元素
3. 提取信息，存入哈系表
"""
if __name__ == "__main__":
    # set encoding
    reload(sys)
    sys.setdefaultencoding('utf-8')

    fp = open('infos.data', 'w')
    fp.write("<head><meta charset=UTF-8> <meta name=renderer content=webkit></head>")
    fp.close()

    parser = Parser58("http://sz.58.com/nanshan/zufang/0/j1/?minprice=0_2500&PGTID=0d300008-0071-3f5c-78fc-4306be39860a&ClickID=6")

    while True:
        parser.parse()
        sleep(10)
    pass
