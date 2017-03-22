# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import time

class RespiderPipeline(object):
    keys =  ["room","price","fine","title","zone","location","last_post","url","detail"]
    def open_spider(self, spider):
        self.fp_html = open("%s.html"%(time.strftime("%Y-%m-%d")), 'w')
        self.fp_html.write("<head><meta charset=UTF-8> <meta name=renderer content=webkit><link rel=\"stylesheet\" type=\"text/css\" href=\"./style.css\"/></head><html><body>")

        self.fp = open("%s.csv"%(time.strftime("%Y-%m-%d")), "wb")
        self.fp.write("\t".join(self.keys))
        self.fp.write("\n")

    def if_item_excepted(self, item):
        if item["room"].find("1室1厅") == -1:
            return False
        if item["fine"] == 0:
            return False
        return True

    def if_item_delicate(self,item):
        if item["fine"] == 0:
            return False
        return True

    def process_item(self, item, spider):
        for key in self.keys:
            self.fp.write("%s\t"%(item[key]))
        self.fp.write("\n")

        self.fp_html.write("<p class=\"pitem %s\">"
            "<span class=\"room %s\">%s</span>"
            "<span class=\"item price\">%s</span>"
            "<span class=\"item post_time\">%s</span>"
            "<span class=\"item place\">%s</span>"
            "<a target=\"_blank\"href=\"%s\">%s</a></p>\n"%(
            "recommend-best" if self.if_item_excepted(item) else "recommend-normal",
            "delicate" if (self.if_item_delicate(item)) else "",
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
