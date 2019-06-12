# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import time
import sqlite3
import sys
import datetime

class Items:
    keys =  ["room","price","fine","title","zone","location","last_post","url","detail", "img_cnt"]

def if_item_excepted(item):
    if item["room"].find("1室1厅") == -1:
        return False
    if str(item["fine"]) == "0":
        return False
    return True

def if_item_delicate(item):
    if item["fine"] == 0:
        return False
    return True

class RespiderPipeline(object):
    def open_spider(self, spider):
        self.fp_html = open("%s.html"%(time.strftime("%Y-%m-%d")), 'w')
        self.fp_html.write("<head><meta charset=UTF-8> <meta name=renderer content=webkit><link rel=\"stylesheet\" type=\"text/css\" href=\"./style.css\"/></head><html><body>")

        self.fp = open("%s.csv"%(time.strftime("%Y-%m-%d")), "wb")
        self.fp.write("\t".join(Items.keys))
        self.fp.write("\n")

    def process_item(self, item, spider):
        for key in Items.keys:
            self.fp.write("%s\t"%(item[key]))
        self.fp.write("\n")

        self.fp_html.write("<p class=\"pitem %s\">"
            "<span class=\"room %s\">%s</span>"
            "<span class=\"item price\">%s</span>"
            "<span class=\"item post_time\">%s</span>"
            "<span class=\"item place\">%s</span>"
            "<a target=\"_blank\"href=\"%s\">%s</a></p>\n"%(
            "recommend-best" if if_item_excepted(item) else "recommend-normal",
            "delicate" if (if_item_delicate(item)) else "",
            item["room"],
            item["price"],
            item["last_post"],
            item["zone"]+"/"+item["location"],
            item["url"],
            item["title"]))
        return item

    def close_spider(self, spider):
        self.fp_html.write("</body></html>")
        self.fp.close()

class RespiderSqlitePipeline(object):
    def __init__(self, sql_uri, sql_table):
        self.sql_uri = sql_uri
        self.sql_table = sql_table
        self.query_str = "select count(*) from %s where url=(?);"%(self.sql_table)

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            sql_uri = crawler.settings.get('SQLITE_FILE'),
            sql_table = crawler.settings.get('SQLITE_TABLE', 'items'))

    def open_spider(self, spider):
        self.sql_conn = sqlite3.connect(self.sql_uri)
        self.sql_cur = self.sql_conn.cursor()
        # create table  ["room","price","fine","title","zone","location","last_post","url","detail"]
        #sql =
        sql = '''CREATE TABLE IF NOT EXISTS %s (
            id INTEGER PRIMARY KEY NOT NULL,
            room TEXT,
            price REAL,
            fine BOOLEAN,
            title TEXT,
            zone CHAR(64),
            location CHAR(64),
            last_post DATETIME,
            url TEXT,
            detail TEXT,
            img_cnt INTEGER);'''%(self.sql_table)
        # 中文编码
        self.sql_conn.text_factory=lambda x: unicode(x, "utf-8")
        self.sql_cur.execute(sql)
        self.sql_conn.commit()

    def if_record_existed(self, url):
        self.sql_cur.execute(self.query_str, (url,))
        total = self.sql_cur.fetchone()
        return total[0] != 0

    def process_item(self, item, spider):
        update_str = "insert into %s(%s) values (%s)"%(
            self.sql_table,
            ",".join(Items.keys),
             ','.join(['?']*len(Items.keys))
        )
        if self.if_record_existed(item['url']):
            print("url %s existed in database"%(item['url']), )
            return item
        values = [item[k] for k in Items.keys]
        self.sql_cur.execute(update_str, values)
        self.sql_conn.commit()

        return item

    def close_spider(self, spider):
        # 导出记录到html文件
        yesterday = datetime.datetime.now() - datetime.timedelta(days = 2)
        date_str = time.strftime("%Y-%m-%d")
        yesterday_str = yesterday.strftime("%Y-%m-%d")
        sql_str = '''select * from data_58 where last_post between '%s 00:00:00' and '%s 23:59:59'
        '''%(yesterday_str, date_str)
        self.sql_cur.execute(sql_str)
        items = self.sql_cur.fetchall()
        if len(items) != 0:
            #               0    1      2       3       4       5       6           7       8       9
            header_str = ["id","room","price","fine","title","zone","location","last_post","url","detail", "img_cnt"]
            fp_html = open("%s.html"%(time.strftime("%Y-%m-%d")), 'w')
            fp_html.write("<head><meta charset=UTF-8> <meta name=renderer content=webkit><link rel=\"stylesheet\" type=\"text/css\" href=\"./style.css\"/></head><html><body>")

            for sql_item in items:
                item = {}
                #for i, name in enumerate(header_str):
                #    print sql_item[i]
                #    item[name] = str(sql_item[i]).encode("utf-8")
                item = dict( (name,str(value).encode("utf-8")) for name,value in zip(header_str,sql_item))
                fp_html.write("<p class=\"pitem %s\">"
                    "<span class=\"room %s %s\">%s</span>"
                    "<span class=\"item price\">%s</span>"
                    "<span class=\"item post_time\">%s</span>"
                    "<span class=\"item place\">%s</span>"
                    "<a target=\"_blank\"href=\"%s\">%s</a></p>\n"%(
                    "recommend-best" if if_item_excepted(item) else "recommend-normal",
                    "delicate" if (if_item_delicate(item)) else "",
                    "no_img" if item["img_cnt"]=="0" else "has_img",
                    item["room"],
                    item["price"],
                    item["last_post"],
                    item["zone"]+"/"+item["location"],
                    item["url"],
                    item["title"]))
            fp_html.write("</body></html>")
        self.sql_conn.close()
