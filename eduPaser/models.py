#!/usr/bin/python
# -*- coding: utf-8 -*-

import json
import logging
import csv
from urlparse import urlparse
from urlparse import urljoin
from config import *
from parser import *

logger = logging.getLogger('root')

# Classes
# @note:设置抓取规则
class ParseRule:
    def __init__(self,tag=None):
        # @param tag:要抓取的目标标签
        self.tag = tag or ''
        # {
        #   'class':True, true或者false表示是否含有此标签
        #   'width':'21%'，标签为具体值则表示仅当标签=值时抓取
        #   'class':['class1','class2'], 标签为列表时表示仅当标签值为列表中的值才成立
        # }
        self.attrDict = {}


class ItemBase:
    def __init__(self, url=None, name=None, eng=None, parser=None):
        self.url = url or ''
        self.name = name or ''
        # www.[xxx.edu.cn]
        self.eng_name = urlparse(self.url).netloc[4:] or eng
        self.done = False
        self.rule = ParseRule()
        self.parser = None or parser

    def to_json(self):
        return json.dumps(self.__dict__, indent=4, sort_keys=True)

    def mkdirs(self):
        pass


class VisitingCard:
    def __init__(self, name, email, role=None):
        self.name = name
        self.email = email


class Employee(ItemBase):
    def __init__(self, url=None, name=None, eng=None):
        ItemBase.__init__(self, url, name, eng)


class Academy(ItemBase):
    def __init__(self, url=None, name=None, eng=None):
        ItemBase.__init__(self, url, name, eng)
        # may have multi urls
        self.employeesUrl = {}


class College(ItemBase):
    def __init__(self, url=None, name=None, eng=None):
        ItemBase.__init__(self, url, name, eng)
        self.academies = list()
        self.academiesUrl = ''

    def print_academies(self):
        for i, c in enumerate(self.academies):
            print("[%3d] %s,%s,%s" % (i,c.name, c.eng_name, c.url))

    def parse_academies(self):
        self.parser = self.parser or SimpleAParser(self.academiesUrl, self.rule)
        if self.parser.run():
            for tag in self.parser.rlist:
                self.academies.append(Academy(url=tag['href'],name=tag.string))

    # auto guess the academy link
    def parse_aurl_auto(self):
        if len(self.academiesUrl) != 0:
            logger.info("academies links %s existed, ignore auto link parsing" % self.academiesUrl)
            return
        acaParser = AutoAcademyParser(self.url)
        if acaParser.run():
            if len(acaParser.rlist) >= 1:
                #logger.warning("parsed [%d] academies links, auto choose link[0]"% len(acaParser.rlist))
                self.academiesUrl = acaParser.rlist[0]['href']

                uparse = urlparse(self.academiesUrl)
                if len(uparse.netloc) == 0:
                    self.academiesUrl = urljoin(self.url,self.academiesUrl) 
                logger.debug("parsed %d academies links for " % len(acaParser.rlist) + self.name)
            else:
                logger.error("parsed %d academies links for " % len(acaParser.rlist) + self.name + " failed")


class China211:
    def __init__(self, url=None, cols=None):
        self.url = url or ''
        self.colleges = cols or list()

    def parse_colleges(self):
        if len(self.colleges) != 0:
            logger.error("colleges list existed, ignore parsing")
            return 
        hao123Parser = Hao123_211_Parser(Config.c211_url)
        if hao123Parser.run():
            for item in hao123Parser.rlist:
                college = College(item['href'], item.string)
                self.colleges.append(college)
                print("href:%s"%item['href'])
    def printColleges(self):
        for i,c in enumerate(self.colleges):
            symbol = ' '
            if len(c.academiesUrl) != 0:
                symbol = '#'
            print("[%2s][%3d] %s , %s , %s " % (symbol,i,c.name, c.eng_name, c.url))

    def colleges_to_csv(self):
        fieldnames = ['name', 'eng_name', 'url']
        with open(path_of(Config.col_csv_file), 'wb') as csvfp:
            writer = csv.DictWriter(csvfp, fieldnames=fieldnames, delimiter=',',
                                    quotechar='|', quoting=csv.QUOTE_MINIMAL)
            # writer.writeheader()
            for c in self.colleges:
                writer.writerow({'name': c.name, 'eng_name': c.eng_name, 'url': c.url})
            csvfp.close()
        logger.info("All %d colleges save to %s done" % (len(self.colleges), path_of(Config.col_csv_file)));

    def csv_to_colleges(self):
        with open(path_of(Config.col_csv_file), 'rb') as csvfp:
            fieldnames = ['name', 'eng_name', 'url']
            reader = csv.DictReader(csvfp, fieldnames=fieldnames, delimiter=',',
                                    quotechar='|', quoting=csv.QUOTE_MINIMAL)
            for row in reader:
                self.colleges.append(College(row['url'], row['name'], row['eng_name']))
            csvfp.close()
        logger.info("All %d colleges laod from to %s done" % (len(self.colleges), path_of(Config.col_csv_file)));

    def mkdirs(self):
        for c in self.colleges:
            path = path_of(c.name)
            logger.debug(path)
            if not os.path.isdir(path):
                os.mkdir(path)
            print("%s,%s,%s" % (c.name, c.eng_name, c.url))


_l_classes = {
    "China211": China211,
    "College": College,
    "Academy": Academy,
    "ParseRule": ParseRule
}


### Serialize
def unserialize_object(d):
    clsname = d.pop('__classname__', None)
    if clsname:
        cls = _l_classes[clsname]
        # Make instance without calling __init__
        obj = cls()
        for key, value in d.items():
            setattr(obj, key, value)
        return obj
    else:
        return d


def serialize_instance(obj):
    d = {'__classname__': obj.__class__.__name__}
    d.update(vars(obj))
    return d


def obj_to_json(obj):
    return json.dumps(obj, indent=4, sort_keys=True, default=serialize_instance, ensure_ascii=False)


def obj_from_file(filename):
    with open(filename, 'rb') as fp:
        return json.loads(fp.read(), object_hook=unserialize_object)


def obj_to_file(obj, filepath):
    with open(filepath, 'wb') as fp:
        fp.write(obj_to_json(obj))
        fp.close()
    #logger.debug('obj %s to json %s' % (obj.__class__.__name__, filepath))
