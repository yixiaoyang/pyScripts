#!/usr/bin/python
# -*- coding: utf-8 *-*

import os

basedir = os.path.abspath(os.path.dirname(__file__))


# gloabel vars
class Config:
    SOUP_PARSER = "html.parser"
    OUT_DIR = 'out'

    C211_URL = 'http://www.hao123.com/eduhtm/211.htm'
    C211_FILE = 'china985.json'
    COL_CSV_FILE = 'colleges.csv'

    ACA_STRINGS = [u'院系设置', u'学院设置', u'院系总揽', u'学院部门', u'院部设置', u'教学单位', u'机构设置', u'院所设置', u'院系部门', u'二级学院',
                   u'院系', u'学院（系）', u'院系总览', u'专业学院', u'院系导航', u'院系介绍', u'教学院部', u'学部院系', u'学院系所', u'学院总览']
    ACA_TAGS = ['a', 'span', 'area']

    # Computer Science
    # EE
    # Math
    # Physics
    # Chemistry
    # Chemical Engineering
    # Environmental Engineering
    # Materials Engineering
    ACA_NAME_FILTER = set([u'数学', u'计算机', u'物理', u'化学', u'化工', u'环境', u'材料', u'机电'])
    ACA_MODFILE = 'MyParser.py'

    URL_TIMEOUT = 5


class DevConfig(Config):
    DEBUG = True
    pass


class TestConfig(Config):
    TEST = True
    pass


class ProConfig(Config):
    pass


def path_of(file_or_dir):
    return os.path.join(os.getcwd(), Config.OUT_DIR, file_or_dir)


config = {
    'development': DevConfig,
    'test': TestConfig,
    'production': ProConfig,
    'default': DevConfig
}
