#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: leon

import os
import time
import threading
import queue  
import re
from bs4 import BeautifulSoup
from console import uConsole

import unittest

class uParser(threading.Thread):
    def __init__(self,name, console):
        threading.Thread.__init__(self)
        self.name = name
        self.console = console
        # ["']http://yixiaoyang.github.io/([^'"]+)["']{1}
        self.partternStr="[\"\']%s/([^\'\"]+)[\"\']{1}"%(self.console.rootUrl)
    def run(self):
        filename = ""
        while True:
            filename = self.console.getDoc(self)
            if filename == None:
                self.console.postMsg(self,"thread exit")
                break
            try:
                fp = open(filename, 'r')
                self.parse(fp.read())
                fp.close()    
            except IOError as errStr:
                self.console.postMsg(self,errStr,True)
            finally:
                self.console.docWorkerCnt -= 1  
    def parse(self,content):
        result = re.findall(self.partternStr,content)
        #result = re.search( self.partternStr, content)
        if result != None:
            # 结果去重
            result = list(set(result))
            for url in result:
                if url[-1] == '/':
                    url = url + self.console.index
                if os.path.isfile(url):
                    continue 
                self.console.postMsg(self,"putUrl:%s"%url)
                self.console.putUrl(url)