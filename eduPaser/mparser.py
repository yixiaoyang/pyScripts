#!/usr/bin/python
# -*- coding: utf-8 -*- 

import os
import urllib2
import chardet
import re
from urlparse import urlparse, urljoin
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

def get_doc_byUrllib2(url,handler=None):
    charset = None
    headers = {
        'User-Agent':'Mozilla/5.0 (X11; Linux i686; rv:41.0) Gecko/20100101 Firefox/41.0',
        'Accept':'"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"'
    }
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
        if not result:
            charset = result['encoding']

    if charset and charset != 'utf-8':
        if charset == 'gb2312':
            doc = unicode(doc,'gb18030')

    request.close()
    return doc


def get_doc_bySelenium(url,handler=None):
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
#def get_doc_byGhost(url):
#    headers = {
#        'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
#        'Accept-Language':'en-US,en;q=0.8',
#        'Connection':'keep-alive',
#        'Host':'soundcloud.com',
#        'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.107 Safari/537.36'
#    }
#    ghost = Ghost()
#    with ghost.start() as session:
#        page, extra_resources = session.open(url,headers=headers)
#        if page:
#            if page.http_status == 200:
#                return page.content
#    return None

l_web_engines = {
    "urllib2": get_doc_byUrllib2,
#    "ghost.py": get_doc_byGhost,
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

# url = "http://www.hao123.com/eduhtm/211.htm"
class Hao123_211_Parser(Parser):
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
    def __init__(self, rule, file=None,url=None, rlist=None, web_engine=Config.DEFAULT_WEB_ENGINE, force_href=False):
        Parser.__init__(self, file=file, url=url,rlist=rlist,web_engine=web_engine)
        self.rule = rule
        self.force_href = force_href

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
            # 查看zone
            zone = self.soup
            if len(self.rule.zone_tag) != 0:
                zones = self.soup.find_all(name=self.rule.zone_tag, attrs=self.rule.zone_attr,limit=1)
                if len(zones) > self.rule.zone_index:
                    zone = zones[self.rule.zone_index]
                    #print zone
                else:
                    logger.debug("can not parse zone")
            
            res = zone.find_all(name=self.rule.tag_name)
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

                # logger.debug(tag)

                # 验证父亲节点
                for i, t in enumerate(tag.parents):
                    if i >= len(self.rule.parents):
                        break
                    # logger.debug("<%s>"%self.rule.parents[i])

                    if t.name != self.rule.parents[i]:
                        valid = False
                        # logger.debug("parents not incorrect")
                        break
                if not valid:
                    continue

                # 提取带href属性的子节点
                if valid:
                    if tag.has_attr('href'):
                        self.rlist.append(tag)
                    else:
                        if(self.force_href):
                            for child in tag.descendants:
                                if isinstance(child, Bs4Tag):
                                    if child.has_attr('href'):
                                        self.rlist.append(child)
                                        # logger.debug(child)
                        else:
                            self.rlist.append(tag)
                    continue
            return True


class SimpleTableParser(SimpleAParser):
    def __init__(self, rule, file=None,url=None, rlist=None, web_engine=Config.DEFAULT_WEB_ENGINE):
        SimpleAParser.__init__(self, rule=rule, file=file, url=url,rlist=rlist,web_engine=web_engine, force_href=False)

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


class ProfileParser():
    def __init__(self,employee,text=None,max_line=32,min_char=2,lines=None, set_attr_hook=None,force_inline=False):
        self.text = text
        self.max_line = max_line
        self.employee = employee
        self.min_char = min_char
        self.lines = lines
        self.symbols = Config.PROFILE_SYMBOLS
        self.split_str = [':', '：']

        # 在设置真正的数据前再次调用用户过滤函数，如在解析email时将'（at）'更改为'@'
        self.set_attr_hook = set_attr_hook


    def line_pipe(self, line):
        # new_line = line.replace('：',':')

        # TODO:清除文本中的多余空格，注意此处如果为英文，所有空格都会被清除
        new_line = ''.join(line.split())
        return new_line

    def check_symbols(self,line):
        for symbol, name in self.symbols.items():
            if symbol in line:
                return True
        return False

    # 返回1：是否需要在下行进行解析，如果时返回值为需要解析的key
    # 返回2：不需要在下行解析，正常返回键值对
    def parse_inline(self, line):
        name_values = {}
        names, symbols, indexes = [], [], []
        indexes_set = set()

        # 使用这个管道过滤是为了消除处理上的不便
        line = self.line_pipe(line)

        # 根据预定的symbol推测字段和值
        for symbol, name in self.symbols.items():
            idx = line.find(symbol)
            if idx != -1:
                pos = idx + len(symbol)
                # 对于‘电子邮箱’，‘邮箱’两个关键串都可以匹配，为了避免可能的冗余需要进行去重
                if not (pos in indexes_set):
                    symbols.append(symbol)
                    names.append(name)
                    name_values[name] = None
                    indexes.append(pos)
                    indexes_set.add(pos)

        indexes_len = len(indexes)
        for pos, index in enumerate(indexes):
            name = names[pos]
            value = None
            if pos < (indexes_len-1):
                end_idx = indexes[pos+1]-len(symbols[pos+1])
                if end_idx >= index:
                    value = line[index:end_idx]
                else:
                    logger.error("parse failed, end_idx %d >= index %d" % (end_idx,index))
            else:
                value = line[index:]

            if not value:
                return name, name_values

            value = value.strip()
            if len(value) == 0:
                return name, name_values

            # remove split chars
            for str in self.split_str:
                splits = value.split(str)
                if len(splits) >= 2:
                    value = splits[1]
                    break
                #split_idx = value.find(str)
                #if split_idx != -1:
                    #value = value[split_idx+len(str):]
                    # value = value[split_idx+len(str):]
                    # print("handle split:"+name+","+value+",len=%d,str=%s"%(len(str),str))
                    #break

            if len(value) == 0:
                print(name+":"+value+" =>next line2=>%d"%index)
                return name, name_values

            name_values[name] = value

        # 根据预定的关键词推测身分
        if len(name_values) == 0 and len(self.employee.title) == 0:
            for keywords in Config.PROFILE_TITLES:
                if keywords in line:
                    self.employee.title = keywords
                    break

        return None, name_values

    def parse(self):
        if not self.lines:
            for line in self.text.splitlines():
                line = line.strip()
                # line = ''.join(line.split())
                if len(line) >= self.min_char:
                    print "origin:"+line
                    self.lines.append(line)

        # parse each line
        to_parse_value = None
        for count,line in enumerate(self.lines):
            # 下行解析
            if to_parse_value:
                # 只有当下行不包含关键字才认为是合法值
                if self.check_symbols(line):
                    to_parse_value = None
                    pass
                else:
                    if self.set_attr_hook:
                        line = ''.join(line.split())
                        line = self.set_attr_hook(to_parse_value,line)
                    self.employee.try_set_attr(to_parse_value,line)
                    to_parse_value = None
                    continue
            if count >= self.max_line:
                break

            to_parse_value,name_values = self.parse_inline(line)
            # 正常解析
            if not to_parse_value:
                for name, value in name_values.items():
                    if self.set_attr_hook:
                        value = ''.join(value.split())
                        value = self.set_attr_hook(name,value)
                    self.employee.try_set_attr(name,value)
        return self.employee


def check_url(base,url):
    # 检查base_url
    if base is None or url is None:
        logger.erorr("base or url None")
        return None
    if len(url) == 0:
        return None
     # 检查url
    parser = urlparse(url)
    # base_parser = urlparse(base)

    if len(parser.netloc) == 0:
        newUrl = urljoin(base,url)
        parser = urlparse(newUrl)
        # parser = parser._replace(netloc = base_parser.netloc)
    if len(parser.scheme) == 0:
        parser = parser._replace(scheme = "http")
    return parser.geturl()

def aca_guess_name(url):
    try:
        request = urllib2.urlopen(url, timeout=Config.URL_TIMEOUT)
        doc = request.read()
        request.close()
        soup = BeautifulSoup(doc, Config.SOUP_PARSER)
        if soup.title:
            return soup.title.string
        return ''
    except Exception as e:
        logger.error("guess name of url %s failed"%url)
        return ''

def aca_filter(col_name, col_url, url, name):
    logger.debug(url)
    url = check_url(col_url,url)
    logger.debug(url)
    if not url:
        return None,None

    # 检查name. 如果没有找到了url但是没有找到院系名称，则打开院系url，根据title猜测院系名称
    if name:
        # 对于链接名==链接地址的重新识别
        if name == url:
            name = None
        name = ''.join(name.split())
    name = name or aca_guess_name(url)
    logger.debug(name)
    if len(name) != 0:
        name = ''.join(name.split())
        idx = name.find(col_name)
        if idx != -1:
            # "XX大学数学系首页XXXX" => "数学系"
            name = name[idx + len(col_name):]
        for key in Config.ACA_NAME_FILTER:
            if key in name:
                return url, name
    return None, None

def employee_filter(aca_name, aca_url, url, name):
    url = check_url(aca_url,url)
    if not url:
        logger.warning("url null in employee_filter, name = "+name)
        # return None,None
    if len(name) != 0:
        name = ''.join(name.split())
    # 太长的不识别为名称
    if len(name) >= 32:
        logger.warning("name is too long, ignore it")
        return url,name
    # logger.debug(url)
    return url,name


def is_sublist(parents, sublist):
    if len(sublist) >= len(parents):
        return False
    for i, s in enumerate(sublist):
        if s != parents[i]:
            return False
    return True


def get_parser(name):
    return l_parsers.get(name)

l_parsers = {
    "Parser": Parser,
    "Hao123_211_Parser": Hao123_211_Parser,
    "SimpleAParser": SimpleAParser,
    "AutoAcademyParser": AutoAcademyParser,
    "SimpleTableParser":SimpleTableParser
}

