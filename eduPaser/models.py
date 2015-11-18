#!/usr/bin/python
# -*- coding: utf-8 -*-

import json
import logging
import csv
import os
from urlparse import urlparse
from urlparse import urljoin
from config import Config
from config import path_of
from parser import SimpleAParser, AutoAcademyParser, Hao123_211_Parser
from parser import aca_filter

logger = logging.getLogger('root')


def get_sname(eng_name):
        if eng_name:
            nameList = eng_name.split('.')
            if nameList[0] == 'www':
                if len(nameList) >= 2:
                    return nameList[1]
                return ''
            else:
                return nameList[0]
        return ''

class Range:
    def __init__(self):
        self.min = 0
        self.max = 0

    def contains(self, idx):
        return (idx >= self.min) and (self.idx < max)

class ParseRule:
    def __init__(self, tag_name=None,parents=None):
        # 要抓取的目标标签
        self.tag_name = tag_name or ''
        # 要抓取的目标标签的父标签列表
        self.parents = parents or []
        # 目标节点属性
        # {
        #   'class':True, true或者false表示是否含有此标签
        #   'width':'21%'，标签为具体值则表示仅当标签=值时抓取
        #   'class':['class1','class2'], 标签为列表时表示仅当标签值为列表中的值才成立
        # }
        self.attrs = {}
        # 结果筛选
        self.select = []


class ItemBase:
    def __init__(self, url=None, name=None, eng=None, parser=None):
        self.url = url or ''

        if name:
            self.name = name.replace('/', '-')
        else:
            self.name = ''

        # [www.xxx.edu.cn]
        self.eng_name = urlparse(self.url).netloc or eng
        self.done = False
        self.rule = ParseRule()
        self.parser = None or parser

    def to_json(self):
        return json.dumps(self.__dict__, indent=4, sort_keys=True)

    def mkdirs(self):
        pass


class VisitingCard:
    def __init__(self, name=None, email=None, tel=None, title=None, profile=None, research=None, departments=None):
        self.name = name or ''
        self.tel = tel or ''
        self.email = email or ''
        self.title = title or ''
        self.profile = profile or ''
        self.research = research or ''
        self.departments = departments or ''

class Employee(ItemBase):
    pass

class Academy(ItemBase):
    def __init__(self, url=None, name=None, eng=None):
        ItemBase.__init__(self, url, name, eng)
        self.sname = get_sname(self.eng_name)

        self.hasDepartments = False
        self.departmentsUrl = ''
        self.departmentsRule = ParseRule()
        self.departments = {}

    def json_dirname(self,prefix):
        return path_of(prefix) +"/" + self.name + "/"

    def json_filename(self,prefix):
        return self.json_dirname(prefix) + self.eng_name + ".json"

    def mypaser_filename(self,prefix):
        return self.json_dirname(prefix) + Config.ACA_MODFILE;

    def to_json_file(self,prefix):
        path = self.json_filename(prefix)
        # if not os.path.exists(path):
        obj_to_file(self,path)

    def parse_departments(self):
        if len(self.departmentsUrl) == 0:
            return
        parser = SimpleAParser(self.departmentsUrl, self.rule)
        if parser.run():
            for tag in parser.rlist:
                if tag.has_attr('href'):
                    self.departments[tag.string] = tag['href']

    def parse_employees(self):
        if len(self.departments) == 0:
            self.parse_departments()
        for name,url in self.departments:
            parser = SimpleAParser(url=url, rule=self.rule)
            if parser.run():
                for tag in parser.rlist:
                    pass

    def mkdirs(self,prefix):
        pass

class College(ItemBase):
    def __init__(self, url=None, name=None, eng=None):
        ItemBase.__init__(self, url, name, eng)
        self.academies = []
        self.academiesUrl = ''
        self.sname = get_sname(self.eng_name)

    def print_academies(self):
        for i, c in enumerate(self.academies):
            print("[%3d] %s,%s,%s" % (i,c.name, c.eng_name, c.url))

    def parse_academies(self):
        logger.debug("start parsing academies..")
        if not self.academiesUrl:
            return
        parser = SimpleAParser(self.academiesUrl, self.rule)
        if parser.run():
            for tag in parser.rlist:
                if tag.has_attr('href'):
                    url,name = aca_filter(self.name,self.url,tag['href'],tag.string)
                    if url and name:
                        aca = Academy(url=url,name=name)
                        self.academies.append(aca)

    # auto guess the academy link
    def parse_aurl_auto(self):
        if len(self.academiesUrl) != 0:
            logger.info("academies links %s existed, ignore auto link parsing" % self.academiesUrl)
            return
        aca_parser = AutoAcademyParser(self.url)
        if aca_parser.run():
            if len(aca_parser.rlist) >= 1:
                # logger.warning("parsed [%d] academies links, auto choose link[0]"% len(aca_parser.rlist))
                self.academiesUrl = aca_parser.rlist[0]['href']

                uparse = urlparse(self.academiesUrl)
                if len(uparse.netloc) == 0:
                    self.academiesUrl = urljoin(self.url,self.academiesUrl) 
                logger.debug("parsed %d academies links for " % len(aca_parser.rlist) + self.name)
            else:
                logger.error("parsed %d academies links for " % len(aca_parser.rlist) + self.name + " failed")

    def to_json_file(self):
        path = self.json_filename()
        # if not os.path.exists(path):
        obj_to_file(self,path)

    def json_filename(self):
        return path_of("%s/%s.json")%(self.sname,self.eng_name)

    def mkdirs(self):
        if len(self.academies):
            for a in self.academies:
                path = a.json_dirname(self.sname)
                print (path)
                if not os.path.isdir(path):
                    os.mkdir(path)
                obj_to_file(a,a.json_filename(self.sname))


class China211:
    def __init__(self, url=None,cols=None):
        self.url = url or ''
        self.colleges = cols or list()

    def to_json_file(self):
        path = path_of(Config.C211_FILE)
        # if not os.path.exists(path):
        obj_to_file(self, path)

_l_classes = {
    "China211": China211,
    "ItemBase": ItemBase,
    "College": College,
    "Academy": Academy,
    "ParseRule": ParseRule,
    "Employee":Employee,
    "Range": Range
}


### Serialize
def unserialize_object(d):
    clsname = d.pop('__classname__', None)
    if clsname:
        cls = _l_classes[clsname]
        # Make instance without calling __init__
        obj = cls()
        obj.__init__()
        for key, value in d.items():
            setattr(obj, key, value)
        return obj
    else:
        return d


def serialize_instance(obj):
    d = {'__classname__': obj.__class__.__name__,'__module__':obj.__module__}
    d.update(vars(obj))
    return d


def obj_to_json(obj):
    return json.dumps(obj, indent=4, sort_keys=True, default=serialize_instance, ensure_ascii=False)


def obj_from_file(filename):
    logger.debug("obj from :%s"%filename)
    with open(filename, 'rb') as fp:
        return json.loads(fp.read(), object_hook=unserialize_object)
    return None


def obj_to_file(obj, filepath):
    with open(filepath, 'wb') as fp:
        fp.write(obj_to_json(obj))
        fp.close()
    #logger.debug('obj %s to json %s' % (obj.__class__.__name__, filepath))
