#!/usr/bin/python
# -*- coding: utf-8 *-*

import os

basedir = os.path.abspath(os.path.dirname(__file__))


# globel vars
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
    ACA_NAME_FILTER = set([u'数学', u'计算机', u'物理', u'化学', u'化工', u'环境', u'材料', u'机电', u'信息科学'])

    ACA_MY_MODFILE = 'MyHandler.py'
    ACA_MY_MODNAME = 'MyHandler'
    ACA_MY_HANDLER = 'handler'
    ACA_MY_PHANDLER = 'profile_handler'
    ACA_MY_EHANDLER = 'engine_handler'

    URL_TIMEOUT = 8

    DEFAULT_WEB_ENGINE = "urllib2"

    PROFILE_SYMBOLS = {
        u'个人主页': 'profile',
        u'方向': 'research',
        u'邮箱': 'email',
        u'信箱': 'email',
        u'邮件': 'email',
        u'Email': 'email',
        u'E-mail': 'email',
        u'单位':  'departments',
        u'职称': 'title',
        u'电话': 'tel',
        u'传真': 'fax'
    }
    PROFILE_TITLES = [u'副教授', u'助理教授', u'教授', u'讲师', u'院长', u'副院长', u'工程师', u'院士', u'副研究员', u'研究员']


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


def relative_path_of(file_or_dir):
    return os.path.join(".", Config.OUT_DIR, file_or_dir)


config = {
    'development': DevConfig,
    'test': TestConfig,
    'production': ProConfig,
    'default': DevConfig
}
