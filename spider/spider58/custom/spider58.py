#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
用于监控58租房信息列表
"""

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
    try:
        request = urllib2.urlopen(req, timeout=10)
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

class Info:
    url = None
    title = None
    price = ""
    showroom = ""
    place1 = ""
    place2 = ""
    post_time = ""


class Parser58:
    def __init__(self,urls):
        self.urls = urls
        self.soup = None
        self.doc = None
        self.infos = {}
        self.query_count = 0

    def parse(self):
        have_news = False
        fp = open('infos.data', 'a+')

        for url in self.urls:
            self.doc = get_doc_byUrllib2(url)
            if not self.doc:
                continue ;
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

        self.query_count += 1
        for url in self.urls:
            self.doc = get_doc_byUrllib2(url)
            self.soup = BeautifulSoup(self.doc, "html.parser", from_encoding="utf-8")
            trs = self.soup.find_all('tr')
            if not trs or len(trs) == 0:
                return
            for tr in trs:
                if tr.has_attr("logr"):
                    alinks = tr.find_all('a',class_='t')
                    if alinks == None or len(alinks) == 0:
                        continue
                    a = alinks[0]

                    info = Info()

                    # 提取标题，链接
                    info.url = a['href']
                    info.title = a.string

                    if not self.infos.has_key(info.title):
                        price_isLow = False
                        delicate = info.title.find('精')!=-1
                        excepted_rome = False
                        # 忽略置顶条目
                        ding = tr.find("span",class_="ico ding")
                        if ding:
                            continue

                        # 提取价格，厅室，位置
                        showroom = tr.find("span",class_='showroom')
                        if showroom:
                            info.showroom = showroom.string
                            if len(info.showroom) < 6:
                                info.showroom = info.showroom + "0卫"

                        excepted_rome = info.showroom.find("1室1厅") != -1
                        price = tr.find("b", class_='pri')
                        if price:
                            info.price = price.string
                            price_isLow = (int(info.price) <= 2000)

                        place1 = tr.find("a", class_='a_xq1')
                        place2 = tr.find("span", class_='f12')
                        if place1:
                            info.place1 = place1.string or ""
                        if place2:
                            info.place2 = place2.string or ""
                        info.place1.strip()
                        info.place2.strip()

                        post_time = tr.find("p",class_="qj-renaddr")
                        if post_time:
                            post_time = post_time.get_text()
                            if post_time:
                                post_time = post_time.strip()
                                post_time = post_time.replace(' ', '')
                                post_time = post_time.replace('\r', '')
                                post_time = post_time.replace('\n', '')

                                post_times = post_time.split('/')
                                if len(post_times) >= 2:
                                    info.post_time = post_times[1]

                        self.infos[info.title] = info
                        if self.query_count > 0:
                            style = ""
                            if excepted_rome:
                                style = "recommend-normal"
                                if price_isLow:
                                    style = "recommend-better"
                                    if delicate:
                                        style = "recommend-best"
                                else:
                                    if delicate:
                                        style = "recommend-better"
                            fp.write("<p class=\"pitem %s\">"
                                     "<span class=\"room %s %s\">%s</span>/"
                                     "<span class=\"item price %s\">%s</span>/"
                                     "<span class=\"item post_time\">%s</span>/"
                                     "<span class=\"item place\">%s-%s</span>/"
                                     "<a target=\"_blank\"href=\"%s\">%s</a></p>\n"
                                     % (style ,
                                        "excepted_rome" if (excepted_rome) else "unexcepted_rome",
                                        "delicate" if (delicate) else "",
                                        info.showroom,
                                        "low_price" if price_isLow else "",
                                        info.price, info.post_time, info.place1,info.place2,info.url, info.title))
                        have_news = True
                        print("%-8s %-8s %-8s %-s\t %s" % (info.price, info.showroom, info.post_time, info.place1+"/"+info.place2, info.title))
        if have_news:
            # 2500Hz, 200ms
            os.system("beep -f 1000 -l 200")
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
    fp.write("<head><meta charset=UTF-8> <meta name=renderer content=webkit><link rel=\"stylesheet\" type=\"text/css\" href=\"./style.css\"/></head>")
    fp.close()

    #parser = Parser58(["http://sz.58.com/nanshan/zufang/0/j1/?minprice=0_2500&PGTID=0d300008-0071-3f5c-78fc-4306be39860a&ClickID=6",
    #"http://sz.58.com/baoanzhongxinquba/zufang/0/j1/?minprice=0_2500&PGTID=0d300008-0180-96ef-9d87-e8e13a507831&ClickID=3"
    #])

    parser = Parser58(
            ["http://sz.58.com/nanshan/zufang/0/j1/?minprice=0_2500&PGTID=0d300008-0071-313e-79b2-411e3ccffeb5&ClickID=8"])

    while True:
        parser.parse2()
        sleep(30)
    pass
