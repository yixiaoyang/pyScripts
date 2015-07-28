#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: leon

import os
import time
import threading
import queue

from urllib.parse import urlparse
import urllib.request

from console import uConsole

class uDwonloader(threading.Thread):
    def __init__(self,name,console):
        threading.Thread.__init__(self)
        self.console = console
        self.name = name
        self.count = 0
    def run(self):
        while True:
            url = self.console.getUrl(self)
            if url == None:
                self.console.postMsg(self,"thread exit")
                break
            parser = urlparse(url)
            try:
                content =  urllib.request.urlopen(url).read()
            except urllib.error.HTTPError as e:
                self.console.postMsg(self, e.reason +" => url:"+url,True)
                self.console.urlWorkerCnt -= 1
                continue
            self.save2file(content,self.console.rootPath+parser.path)
            self.console.urlWorkerCnt -= 1
    def save2file(self,doc, filename, mode="wb"):
        if os.path.isdir(filename):
            os.path.join(filename,"./index.html")
        if not os.path.exists(os.path.dirname(filename)):
            os.makedirs(os.path.dirname(filename))
        if not os.path.isfile(filename):
            # 不存在重复文件 
            try:
                fp = open(filename, mode)
                fp.write(doc)
                fp.close()
                self.console.postMsg(self,"putDoc: %s"%(filename))
                self.console.putDoc(filename)
            except IOError as errStr:
                self.console.postMsg(self,errStr,True)
        return True        
            