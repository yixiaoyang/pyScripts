#!/usr/bin/python
# -*- coding: utf-8 -*- 

import urllib2
from urlparse import urlparse
import logging
import logging.handlers
# import requests
from bs4 import BeautifulSoup
from config import Config

logger = logging.getLogger('root')


class Parser:
    def __init__(self, url, rlist=None, encoding=None):
        self.url = url
        self.rlist = rlist or list()
        self.soup = None
        self.encoding = encoding or "utf-8"

    def parse(self):
        logger.debug("parsing...")
        pass

    def run(self):
        stat = False
        try:
            # logger.debug("running...")

            request = urllib2.urlopen(self.url, timeout=Config.URL_TIMEOUT)
            doc = request.read()
            request.close()
            # print(request.getcode())

            # r = requests.get(self.url,timeout=30)
            # doc = r.text
            # print r.status_code

            # self.soup = BeautifulSoup(doc,"lxml")
            self.soup = BeautifulSoup(doc, Config.SOUP_PARSER)
            self.parse()
            stat = True
        # ValueError
        except Exception as e:
            logger.error("%s:%s" % (e, self.url))
        finally:
            return stat


# url = "http://www.hao123.com/eduhtm/211.htm"
class Hao123_211_Parser(Parser):
    logger.debug("parsing...")

    def parse(self):
        if self.soup:
            for td in self.soup.find_all(name='td'):
                if td.has_attr('class'):
                    continue

                if td.has_attr('height'):
                    continue

                if td.has_attr('width'):
                    if td['width'] != '21%':
                        continue

                if len(td.contents) == 0:
                    continue

                if td.contents[0].name != 'a':
                    continue

                # print td.contents[0]
                self.rlist.append(td.contents[0])


class SimpleAParser(Parser):
    def __init__(self, url, rule, rlist=None):
        Parser.__init__(self, url, rlist)
        self.rule = rule

    def check(self, tag, attr, value):
        if len(attr) == 0:
            return False
        if value.__class__.__name__ == 'unicode':
            if len(value) == 0:
                return False
            if tag.has_attr(attr):
                if tag[attr] == value:
                    return True
        elif value.__class__.__name__ == 'bool':
            if tag.has_attr(attr) == value:
                return True
        elif value.__class__.__name__ == 'dict':
            if len(value) == 0:
                return False
        return False

    def parse(self):
        # logger.debug("parsing...")
        if not self.rule:
            logger.error("Rule should has a tag")
            return False
        if self.soup:
            logger.debug("url: %s", self.url)
            res = self.soup.find_all(name=self.rule.tag_name)
            logger.debug("find_all(\'%s\') count %d" % (self.rule.tag_name, len(res)))
            for tag in res:
                valid = True
                # 验证目标属性
                for attr, value in self.rule.attrs.items():
                    if not self.check(tag, attr, value):
                        valid = False
                        continue
                if valid:
                    self.rlist.append(tag)
            return True


class AutoAcademyParser(Parser):
    def __init__(self, url, rlist=None):
        Parser.__init__(self, url=url, rlist=rlist, encoding="gb18030")

    def parse(self):
        # logger.debug("auto parsing academy link...")
        if self.soup:
            rlist = self.soup.find_all(Config.ACA_TAGS, string=Config.ACA_STRINGS)
            if len(rlist) != 0:
                for item in rlist:
                    if item.has_attr('href'):
                        self.rlist.append(item)
                        break


class TsinghuaAcademyParser(Parser):
    def parse(self):
        pass


def aca_guess_name(url):
    request = urllib2.urlopen(url, timeout=Config.URL_TIMEOUT)
    doc = request.read()
    request.close()
    soup = BeautifulSoup(doc, Config.SOUP_PARSER)
    if soup.title:
        return soup.title.string
    return ''


def aca_filter(col_name, col_url, url, name):
    # 检查col_url
    if col_url == None:
        logger.erorr("col_url None")
        return None, None

    # 检查url
    parser = urlparse(url)
    if len(parser.netloc) == 0:
        if col_url[-1] != '/':
            url = col_url + '/' + url
        else:
            url = col_url + url

    # 检查name. 如果没有找到了url但是没有找到院系名称，则打开院系url，根据title猜测院系名称
    name = name or aca_guess_name(url)
    logger.debug(name)
    if len(name) != 0:
        idx = name.find(col_name)
        if idx != -1:
            # "XX大学数学系首页XXXX" => "数学系"
            name = name[idx + len(col_name):]
        for key in Config.ACA_NAME_FILTER:
            if key in name:
                return url, name
    return None, None


l_parsers = {
    "Parser": Parser,
    "Hao123_211_Parser": Hao123_211_Parser,
    "SimpleAParser": SimpleAParser,
    "AutoAcademyParser": AutoAcademyParser,
    "TsinghuaAcademyParser": TsinghuaAcademyParser
}
