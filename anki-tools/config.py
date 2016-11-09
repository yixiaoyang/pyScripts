#!/usr/bin/python
# -*- coding: utf-8 *-*

import os

basedir = os.path.abspath(os.path.dirname(__file__))

# globel vars
class Config:
    SOUP_PARSER = "html.parser"
    OUT_DIR = 'out'
    IMG_DIR = 'images'
    SOUND_DIR = 'sounds'
    URL_TIMEOUT = 30
    DEFAULT_WEB_ENGINE = "urllib2"
    BASE_URL = 'http://www.iciba.com'

class DevConfig(Config):
    DEBUG = True
    pass


class TestConfig(Config):
    TEST = True
    pass


class ProConfig(Config):
    pass


config = {
    'development': DevConfig,
    'test': TestConfig,
    'production': ProConfig,
    'default': DevConfig
}
