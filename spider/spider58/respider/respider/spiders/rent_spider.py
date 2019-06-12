#!/usr/bin/python
# -*- coding: utf-8 -*-

import scrapy
from respider.items import RespiderItem

import time
import datetime
import sqlite3
import sys

class RentSpider(scrapy.Spider):
    name = "rent_spider"
    start_urls = [
        # 南山，用前三页
        "http://sz.58.com/nanshan/zufang/0/j1/?minprice=1000_3000",
        "http://sz.58.com/nanshan/zufang/0/j1/pn2/?minprice=1000_3000",
        "http://sz.58.com/nanshan/zufang/0/j1/pn3/?minprice=1000_3000",
        # 宝安
        "http://sz.58.com/baoanlu/zufang/0/j1/?minprice=1000_3000",
        # 宝安中心区
        "http://sz.58.com/baoanzhongxinquba/zufang/0/j1/?minprice=1000_3000",
        # 翻身路
        "http://sz.58.com/fanshenlu/zufang/0/j1/?minprice=1000_3000",
        # 新安
        "http://sz.58.com/xinanlu/zufang/0/j1/?minprice=1000_3000",
        # 新中心区
        "http://sz.58.com/xinzhongxinqu/zufang/0/j1/?minprice=1000_3000",
        # 西乡
        #"http://sz.58.com/xixiangsz/zufang/0/j1/?minprice=1000_3000"
    ]
    # 获取所有的li下的链接
    start_xpath = "/html/body/div[3]/div[1]/div[5]/div[2]/ul/li[*]/div[2]/h2/a[1]/@href"
    detail_xpaths = {
        "title":"/html/body/div[4]/div[1]/h1/text()",
        "price":"/html/body/div[4]/div[2]/div[2]/div[1]/div[1]/div/span[1]/b/text()",
        "room":"/html/body/div[4]/div[2]/div[2]/div[1]/div[1]/ul/li[2]/span[2]/text()",
        "zone":"/html/body/div[4]/div[2]/div[2]/div[1]/div[1]/ul/li[5]/span[2]/a/text()",
        "last_post":"/html/body/div[4]/div[1]/p/text()",
        "location":"/html/body/div[4]/div[2]/div[2]/div[1]/div[1]/ul/li[4]/span[2]/a/text()",
        "detail":"/html/body/div[4]/div[3]/div[1]/div[1]/p/text()",
        "ptitle":"/html/head/title/text()"
    }
    headers = {
        'User-Agent':'Mozilla/5.0 (X11; Linux i686; rv:41.0) Gecko/20100101 Firefox/41.0',
        'Accept':'"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"'
    }
    yesterday = datetime.datetime.now() - datetime.timedelta(days = 1)

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            sql_uri = crawler.settings.get('SQLITE_FILE'),
            sql_table = crawler.settings.get('SQLITE_TABLE', 'items'))

    def __init__(self, sql_uri, sql_table):
        self.sql_uri = sql_uri
        self.sql_table = sql_table
        self.query_str = "select count(*) from %s where url=(?);"%(self.sql_table)
        self.sql_conn = sqlite3.connect(self.sql_uri)
        self.sql_cur = self.sql_conn.cursor()

        reload(sys)
        sys.setdefaultencoding('utf-8')

    def if_record_existed(self, url):
        self.sql_cur.execute(self.query_str, (url,))
        total = self.sql_cur.fetchone()
        return total[0] != 0

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url=url, headers=self.headers, callback=self.parse)

    def parse(self, response):
        sels = response.xpath(self.start_xpath).extract()
        for sel in sels:
            # TODO: 去重检测，如果当前url已经存在数据库中则不再抓取
            if (not self.if_record_existed(sel)):
                yield scrapy.Request(url=sel, headers=self.headers, callback=self.parse_detail)

    def parse_detail(self, response):
        value = lambda ilist: "-".join([v for v in ilist]) if len(ilist) else ''
        item = RespiderItem()
        item["url"] = response.url
        for key in ["title","price","room","zone","last_post","location","detail"]:
            xpath = self.detail_xpaths[key] or None
            if xpath:
                doc = value(response.xpath(xpath).extract()).strip().encode('utf-8')
                item[key] = doc

        xpath = self.detail_xpaths['ptitle']
        ptitle_doc = value(response.xpath(xpath).extract()).strip().encode('utf-8')
        idx1 = ptitle_doc.find("【")
        idx2 = ptitle_doc.find("图")
        if idx1 != -1 and idx2 != -1:
            item['img_cnt'] = int(ptitle_doc[idx1+3:idx2])
            print "LDEBUG" ,idx1, idx2, item['img_cnt'],  ptitle_doc

        self.strip_item(item)
        # 只解析今天，昨天的
        if item["last_post"].split(" ")[0] != time.strftime("%Y-%m-%d"):
            if item["last_post"].split(" ")[0] != self.yesterday.strftime("%Y-%m-%d"):
                return
        # 只看1室1厅
        if item["room"].find("1室1厅") == -1:
            return
        yield item

    def strip_item(self, item):
        item["last_post"] =item["last_post"][:19]
        if item["room"].find("精") != -1:
            item["fine"] = 1
        else:
            item["fine"] = 0
        if len(item["room"]) > 0:
            item["room"] = item["room"].split(' ')[0]
        for key in ["title","zone","location","detail"]:
            if len(item[key]) > 0:
                item[key] = "".join(item[key].split())
