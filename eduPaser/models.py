#!/usr/bin/python
# -*- coding: utf-8 -*-

import json
import logging
import csv
import imp
import os
from urlparse import urlparse
from urlparse import urljoin
from config import Config
from config import path_of, relative_path_of
from mparser import SimpleAParser, AutoAcademyParser, Hao123_211_Parser
from mparser import aca_filter, employee_filter, get_parser

logger = logging.getLogger('root')


def get_sname(eng_name):
    if eng_name:
        name_list= eng_name.split('.')
        if name_list[0] == 'www':
            if len(name_list) >= 2:
                return name_list[1]
            return ''
        else:
            return name_list[0]
    return ''


class Range:
    def __init__(self):
        self.min = 0
        self.max = 0

    def contains(self, idx):
        return (idx >= self.min) and (self.idx < max)


class ParseRule:
    def __init__(self, tag_name=None):
        # 目标所在的区域
        self.zone_tag = ''
        self.zone_attr = {}

        # 要抓取的目标标签
        self.tag_name = tag_name or ''
        # 要抓取的目标标签的附表前
        self.parents = []
        # 1. 目标节点属性
        # {
        #   'class':True, true或者false表示是否含有此标签
        #   'width':'21%'，标签为具体值则表示仅当标签=值时抓取
        #   'class':['class1','class2'], 标签为列表时表示仅当标签值为列表中的值才成立
        # }
        self.attrs = {}

        # 2. 结果筛选
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
        self.parser = parser

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


class Employee:
    def __init__(self, url='', name='', email='', tel='', title='', profile='', research='', departments='', fax='',
                 addr=''):
        self.name = name
        self.tel = tel
        self.email = email
        self.title = title
        self.profile = profile
        self.research = research
        self.departments = departments
        self.url = url
        self.fax = fax
        self.addr = addr

    def try_set_attr(self, name, value):
        if hasattr(self, name):
            setattr(self, name, value)
            logger.debug(name + ":" + value)
        else:
            logger.debug("no attr %s in employee" % name)


class Academy(ItemBase):
    def __init__(self, url=None, name=None, eng=None):
        ItemBase.__init__(self, url, name, eng)
        self.sname = get_sname(self.eng_name)

        # self.hasDepartments = False
        # self.departmentsUrl = ''
        # self.departmentsRule = ParseRule()
        self.departments = {}

        self.web_engine = Config.DEFAULT_WEB_ENGINE
        self.employees = []

    def json_dirname(self, col):
        return os.path.join(path_of(col.sname), self.name)

    def json_filename(self, col):
        return os.path.join(self.json_dirname(col), (self.eng_name + ".json"))

    def csv_filename(self, col):
        return os.path.join(self.json_dirname(col), (self.eng_name + ".csv"))

    def mypaser_filename(self, col):
        return os.path.join(self.json_dirname(col), Config.ACA_MY_MODFILE)

    def index_filename(self, col, name):
        path = os.path.join(self.json_dirname(col), name+".html")
        return path

    def to_json_file(self, col):
        path = self.json_filename(col)
        # if not os.path.exists(path):
        obj_to_file(self, path)

    # TODO: test me
    def parse_departments(self):
        pass
        # if len(self.departmentsUrl) == 0:
        #     return
        # parser = SimpleAParser(self.departmentsUrl, self.rule)
        # if parser.run():
        #     for tag in parser.rlist:
        #         if tag.has_attr('href'):
        #             self.departments[tag.string] = tag['href']

    def load_user_handler(self, name, col):
        handler = None
        mod_path = self.mypaser_filename(col)
        mod_path = mod_path.decode('utf-8')
        if os.path.exists(mod_path):
            # logger.debug("load MyHandler.py mode %s from: " % name + mod_path)
            mod = imp.load_source(Config.ACA_MY_MODNAME, mod_path)
            # 检查函数handler有没有实现
            handler = getattr(mod, name, None)
            if not callable(handler):
                logger.warning("%s in %s not found" % (name, mod_path))
        # logger.warning(mod_path)
        # logger.debug(col.sname)
        return handler

    def parse_employees(self, col):
        if len(self.departments) == 0:
            self.parse_departments()
            logger.debug("departments none")
            return
        if self.employees_existed(col):
            logger.warning(self.csv_filename(col) + " existed")
            return

        # get custom parser class
        my_parser = None
        if self.parser:
            my_parser = get_parser(self.parser)
            if my_parser:
                logger.debug('get parser %s'%my_parser)
        my_parser = my_parser or SimpleAParser

        # load user's custom handler
        handler = self.load_user_handler(Config.ACA_MY_HANDLER, col)
        phandler = self.load_user_handler(Config.ACA_MY_PHANDLER, col)
        engine_handler = self.load_user_handler(Config.ACA_MY_EHANDLER, col)

        for name, url in self.departments.items():
            parser = my_parser(file=self.index_filename(col,name), url=url, rule=self.rule, web_engine=self.web_engine)
            if parser.run():
                if len(parser.rlist) != 0:
                    if handler:
                        for count, tag in enumerate(parser.rlist):
                            try:
                                employ1 = handler(tag)
                                if not employ1 or not employ1.name:
                                    logger.warning("parse failed employee none")
                                    continue
                                employ1.url, employ1.name = employee_filter(self.sname, url, employ1.url, employ1.name)
                                if employ1.name:
                                    # 学院+部门名称
                                    employ1.departments = (self.name+'-'+name)
                                    logger.debug("try parsing " + employ1.name + ", url=%s"%(employ1.url if employ1.url else 'None'))
                                    if employ1.url:
                                        if phandler:
                                            logger.debug("try get profile of " + employ1.name)
                                            engine = parser.engine()
                                            # logger.debug(parser.web_engine)
                                            doc = engine(employ1.url, handler=engine_handler)
                                            employ2 = phandler(doc=doc, name=employ1.name, url=employ1.url,
                                                               path=self.json_dirname(col))
                                            if not employ2:
                                                logger.warning("profile handler failed")
                                                continue
                                            employ2.name = employ2.name or employ1.name
                                            employ2.url = employ2.url or employ1.url
                                            if employ2:
                                                logger.debug("parsed: " + employ2.name + " done")
                                                self.employees.append(employ2)
                                            else:
                                                logger.warning("profile handler failed")
                                    else:
                                        logger.debug("parsed: " + employ1.name + " done")
                                        self.employees.append(employ1)
                                    # if employ1.url
                                # if employ1.name
                            except Exception as e:
                                logger.error("Exception %s" % e)
                                continue
                            # if count >= 1:
                            #    break
                    else:
                        logger.error("handler not found")

    def print_employees(self):
        for i, e in enumerate(self.employees):
            print(('[%3d]:' % i) + e.name + ":, " + e.email)

    def employees_to_csv(self, col):
        filename = self.csv_filename(col)
        fieldnames = ['name', 'title', 'email', 'tel', 'fax', 'research', 'departments', 'url', 'profile']
        with open(path_of(filename), 'wb') as csvfp:
            writer = csv.DictWriter(csvfp, fieldnames=fieldnames, delimiter=',',
                                    quotechar='|', quoting=csv.QUOTE_MINIMAL)
            writer.writeheader()
            for e in self.employees:
                writer.writerow({'name': e.name,
                                 'title': e.title,
                                 'email': e.email,
                                 'tel': e.tel,
                                 'fax': e.fax,
                                 'research': e.research,
                                 'departments': e.departments or self.name,
                                 'url': e.url,
                                 'profile': e.profile})
            csvfp.close()
        pass

    def employees_existed(self, col):
        filename = self.csv_filename(col)
        return os.path.exists(filename) or len(self.employees) != 0


class College(ItemBase):
    def __init__(self, url=None, name=None, eng=None):
        ItemBase.__init__(self, url, name, eng)
        self.academies = []
        self.academiesUrl = ''
        self.sname = get_sname(self.eng_name)

    def print_academies(self):
        for i, c in enumerate(self.academies):
            # tag = ' ' if (len(c.employees) == 0) else '#'
            tag = '#' if (os.path.exists(c.csv_filename(self))) else ' '
            print("[%2s][%3d] %s,%s,%s" % (tag, i, c.name, c.eng_name, c.url))

    def parse_academies(self):
        logger.debug("start parsing academies..")
        if len(self.academiesUrl) == 0:
            return
        parser = SimpleAParser(file=self.index_filename(), url=self.academiesUrl, rule=self.rule)
        if parser.run():
            for tag in parser.rlist:
                if tag.has_attr('href'):
                    url, name = aca_filter(self.name, self.url, tag['href'], tag.string)
                    if url and name:
                        aca = Academy(url=url, name=name)
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
                    self.academiesUrl = urljoin(self.url, self.academiesUrl)
                logger.debug("parsed %d academies links for " % len(aca_parser.rlist) + self.name)
            else:
                logger.error("parsed %d academies links for " % len(aca_parser.rlist) + self.name + " failed")

    def to_json_file(self):
        path = self.json_filename()
        # if not os.path.exists(path):
        obj_to_file(self, path)

    def json_filename(self):
        return os.path.join(path_of(self.sname), (self.eng_name + ".json"))

    def index_filename(self):
        return os.path.join(path_of(self.sname), "index.html")

    def mkdirs(self):
        if len(self.academies):
            for a in self.academies:
                path = a.json_dirname(self)
                print (path)
                if not os.path.isdir(path):
                    os.mkdir(path)
                obj_to_file(a, a.json_filename(self))


class China211:
    def __init__(self, url=None, cols=None):
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
    "Employee": Employee,
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
    d = {'__classname__': obj.__class__.__name__, '__module__': obj.__module__}
    d.update(vars(obj))
    return d


def obj_to_json(obj):
    return json.dumps(obj, indent=4, sort_keys=True, default=serialize_instance, ensure_ascii=False)


def obj_from_file(filename):
    logger.debug("obj from :%s" % filename)
    with open(filename, 'rb') as fp:
        return json.loads(fp.read(), object_hook=unserialize_object)
    return None


def obj_to_file(obj, filepath):
    with open(filepath, 'wb') as fp:
        fp.write(obj_to_json(obj))
        fp.close()
        # logger.debug('obj %s to json %s' % (obj.__class__.__name__, filepath))
