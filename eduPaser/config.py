#!/usr/bin/python
# -*- coding: utf-8 *-*

import os

basedir = os.path.abspath(os.path.dirname(__file__))


# gloabel vars
class Config:
    c211_url = 'http://www.hao123.com/eduhtm/211.htm'
    # out
    out_dir = 'out'
    col_csv_file = 'colleges.csv'
    c211_file = 'china211.json'

    aca_strings = [u'院系设置',u'学院设置',u'院系总揽',u'学院部门',u'院部设置',u'教学单位',u'机构设置', u'院所设置']
    aca_tags = ['a','span']

    url_timeout = 10

class DevConfig(Config):
    DEBUG = True
    pass


class TestConfig(Config):
    TEST = True
    pass


class ProConfig(Config):
    pass


def path_of(file_or_dir):
    return os.path.join(os.getcwd(), Config.out_dir, file_or_dir)


config = {
    'development': DevConfig,
    'test': TestConfig,
    'production': ProConfig,
    'default': DevConfig
}
