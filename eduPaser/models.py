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
        name_list = eng_name.split('.')
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
        self.zone_index = 0

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

class Paginator:
    def __init__(self, page_min=0, page_max=1, param_name='page'):
        self.page_min = page_min
        self.page_max = page_max
        self.param_name = param_name


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

    def set_value(self, employ):
        if employ:
            self.name = self.name if len(self.name) != 0 else employ.name
            self.tel = self.tel if len(self.tel) != 0 else employ.tel
            self.email = self.email if len(self.email) != 0 else employ.email
            self.title = self.title if len(self.title) != 0 else employ.title
            self.profile = self.profile if len(self.profile) != 0 else employ.profile
            self.research = self.research if len(self.research) != 0 else employ.research
            self.url = self.url if len(self.url) != 0 else employ.url
            self.fax = self.fax if len(self.fax) != 0 else employ.fax
            self.addr = self.addr if len(self.addr) != 0 else employ.addr

    def try_set_attr(self, name, value):
        if hasattr(self, name):
            old_value = getattr(self,name)
            # 如果存在值，不覆盖，忽略
            if old_value and len(old_value) != 0:
                return
            else:
                setattr(self, name, value)
                logger.debug(name + ":[" + value + "], len=%d"%len(value))
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

        # ‘全体教师’导航页面是否分页，默认为1整页，若分页需要在配置文件写上具体的页数。
        # 另外需要在departments字段填写基本的字段“page1”：“url”
        # self.pages = 1

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
        path = os.path.join(self.json_dirname(col), name + ".html")
        return path

    def to_json_file(self, col):
        path = self.json_filename(col)
        # if not os.path.exists(path):
        obj_to_file(self, path)

    # TODO: 如果存在用户定义的分析器则使用用户定义的DEPARTMENTS_HANDLER
    def parse_departments(self,col):
        handler = self.load_user_handler(Config.ACA_MY_DEPARTMENTS_HANDLER, col)
        if handler:
            self.departments = handler()

    def load_user_handler(self, name, col):
        handler = None
        mod_path = self.mypaser_filename(col)
        mod_path = mod_path.decode('utf-8')

        # in windows 
        # mod_path = "./out/MyHandler.py"
        if os.path.exists(mod_path):
            logger.debug("load MyHandler.py mode %s from: " % name + mod_path)
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
            self.parse_departments(col)
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
                logger.debug('get parser %s' % my_parser)
        my_parser = my_parser or SimpleAParser

        # load user's custom handler
        handler = self.load_user_handler(Config.ACA_MY_HANDLER, col)
        phandler = self.load_user_handler(Config.ACA_MY_PHANDLER, col)
        engine_handler = self.load_user_handler(Config.ACA_MY_EHANDLER, col)
        pre_handler = self.load_user_handler(Config.ACA_MY_PREHANDLER, col)

        name_set = set()
        for name, url in self.departments.items():
            index_filename = self.index_filename(col, name)
            if pre_handler and not os.path.exists(index_filename):
                pre_handler(url=url,filename=index_filename)
            parser = my_parser(file=index_filename, url=url, rule=self.rule, web_engine=self.web_engine)
            if parser.run():
                #logger.debug("parser.rlist=%d"%len(parser.rlist))
                if len(parser.rlist) != 0:
                    if handler:
                        for count, tag in enumerate(parser.rlist):
                            # if count >= 4:
                            #     break
                            try:
                            #if True:
                                #print(tag), "\n"
                                employ1 = handler(tag)
                                if not employ1 or not employ1.name:
                                    logger.warning("parse failed employee none")
                                    continue
                                employ1.url, employ1.name = employee_filter(self.sname, url, employ1.url, employ1.name)
                                if employ1.name:
                                    if employ1.name in name_set:
                                        logger.warning("name: " + employ1.name + " already pasred")
                                        continue
                                    else:
                                        name_set.add(employ1.name)

                                    # 学院+部门名称
                                    employ1.departments = (self.name + '-' + name)
                                    logger.debug("try parsing " + employ1.name + ", url=%s" % (
                                        employ1.url if employ1.url else 'None'))
                                    if employ1.url:
                                        if phandler:
                                            #logger.debug("try get profile of " + employ1.name)
                                            profile_file = os.path.join(self.json_dirname(col), (employ1.name + ".html"))
                                            doc = None

                                            if os.path.exists(profile_file):
                                                doc = open(profile_file,'rb').read()
                                            else:
                                                engine = parser.engine()
                                                # logger.debug(parser.web_engine)
                                                doc = engine(employ1.url, handler=engine_handler)
                                            employ2 = phandler(doc=doc, name=employ1.name, url=employ1.url,
                                                               path=self.json_dirname(col))
                                            if not employ2:
                                                logger.warning("profile handler failed")
                                                continue
                                            else:
                                                employ2.set_value(employ1)
                                                logger.debug("parsed: " + employ2.name + ":" + employ2.email + " done")
                                                self.employees.append(employ2)
                                    else:
                                        #logger.debug("parsed: " + employ1.name + " done")
                                        self.employees.append(employ1)
                                        # if employ1.url
                                        # if employ1.name
                            except Exception as e:
                            #else:
                                logger.error("Exception %s" % e)
                                continue
                    else:
                        logger.error("handler not found")
            else: # if parser.run()
                logger.error("parser run failed")

    def print_employees(self):
        for i, e in enumerate(self.employees):
            print(('[%3d]:' % i) + e.name + ":, " + e.email)

    def employees_to_csv(self, col):
        filename = self.csv_filename(col)
        fieldnames = ['name', 'title', 'email', 'tel', 'fax', 'research', 'departments', 'url', 'profile']
        with open(path_of(filename), 'wb') as csvfp:
            writer = csv.DictWriter(csvfp, fieldnames=fieldnames, delimiter=',',
                                    quotechar=' ', quoting=csv.QUOTE_MINIMAL)
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
                    url, name = aca_filter(self.name, parser.url, tag['href'], tag.string)
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
