#!/usr/bin/python
# -*- coding: utf-8 -*- 

import urllib2
from urlparse import urlparse
import logging
import logging.handlers
# import requests
from bs4 import BeautifulSoup
from bs4.element import Tag as Bs4Tag
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
                if value in tag[attr]:
                    return True
        elif value.__class__.__name__ == 'bool':
            #logger.debug("tag has attr %s ?= %s"%( attr,value))
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
            res = self.soup.find_all(name=self.rule.tag_name)
            logger.debug("find_(\'%s\') in %s count %d" % (self.rule.tag_name, self.url, len(res)))
            for idx, tag in enumerate(res):
                valid = True if (len(self.rule.select) == 0) else False
                # 查看目标是否在规定范围
                for rg in self.rule.select:
                    if rg.contains(idx):
                        valid = True
                        break
                if not valid:
                    continue

                # 验证目标属性
                for attr, value in self.rule.attrs.items():
                    if not self.check(tag, attr, value):
                        valid = False
                        break
                if not valid:
                    continue

                #logger.debug(tag)

                # 验证父亲节点
                for i, t in enumerate(tag.parents):
                    if i >= len(self.rule.parents):
                        break
                    logger.debug("<%s>"%self.rule.parents[i])

                    if t.name != self.rule.parents[i]:
                        valid = False
                        logger.debug("parents not incorrect")
                        break
                if not valid:
                    continue

                # 提取带href属性的子节点
                if valid:
                    if tag.has_attr('href'):
                        self.rlist.append(tag)
                    else:
                        for child in tag.descendants:
                            if isinstance(child, Bs4Tag):
                                if child.has_attr('href'):
                                    self.rlist.append(child)
                                    logger.debug(child)
                    continue
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
    try:
        request = urllib2.urlopen(url, timeout=Config.URL_TIMEOUT)
        doc = request.read()
        request.close()
        soup = BeautifulSoup(doc, Config.SOUP_PARSER)
        if soup.title:
            print soup.title.string
            return soup.title.string
        return ''
    except Exception as e:
        logger.error("guess name of url %s failed"%url)
        return ''

def aca_filter(col_name, col_url, url, name):
    # 检查col_url
    if col_url is None or url is None:
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
    if name:
        # 对于链接名==链接地址的重新识别
        if name == url:
            name = None
    name = name or aca_guess_name(url)
    logger.debug(name)
    if len(name) != 0:
        name = name.strip(' \t\n\r')
        idx = name.find(col_name)
        if idx != -1:
            # "XX大学数学系首页XXXX" => "数学系"
            name = name[idx + len(col_name):]
        for key in Config.ACA_NAME_FILTER:
            if key in name:
                return url, name
    return None, None


def is_sublist(parents, sublist):
    if len(sublist) >= len(parents):
        return False
    for i, s in enumerate(sublist):
        if s != parents[i]:
            return False
    return True


l_parsers = {
    "Parser": Parser,
    "Hao123_211_Parser": Hao123_211_Parser,
    "SimpleAParser": SimpleAParser,
    "AutoAcademyParser": AutoAcademyParser,
    "TsinghuaAcademyParser": TsinghuaAcademyParser
}
