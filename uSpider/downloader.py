#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: leon

import os
import time
import threading
import queue

from urllib.parse import urlparse
import urllib.request
import mimetypes
from console import uConsole

class uDwonloader(threading.Thread):
    def __init__(self,name,console):
        threading.Thread.__init__(self)
        self.console = console
        self.name = name
        self.count = 0
        self.allowMimes=set(['text/html'])
    def run(self):
        urlfp = None
        while True:
            url = self.console.getUrl(self)
            if url == None:
                self.console.postMsg(self,"thread exit")
                break
            parser = urlparse(url)
            try:
                urlfp =  urllib.request.urlopen(url)
            except urllib.error.HTTPError as e:
                self.console.postMsg(self, e.reason +" => url:"+url,True)
                self.console.urlWorkerCnt -= 1
                continue
            except ValueError:
                self.console.postMsg(self, "ValueError => url:"+url,True)
                self.console.urlWorkerCnt -= 1
                continue
            
            if urlfp != None:
                self.handleUrlContent(urlfp,self.console.rootPath+parser.path)
                urlfp.close()
            self.console.urlWorkerCnt -= 1
    def handleUrlContent(self,urlfp, filename, mode="wb"):
        if os.path.isdir(filename):
            os.path.join(filename,"./index.html")
        if not os.path.exists(os.path.dirname(filename)):
            os.makedirs(os.path.dirname(filename))
        if not os.path.isfile(filename):
            # 不存在重复文件 
            try:
                fp = open(filename, mode)
                fp.write(urlfp.read())
                fp.close()
                #self.console.postMsg(self,"putDoc: %s"%(filename))
                
                # 解析mime类型，仅将文本网页文件加入doc
                headers = urlfp.info()
                # Get the mimetype from the headerlines
                c_t = headers['Content-Type'].split(';')[0].strip()
                if c_t: 
                    mediatype = c_t.split(';')[0].strip()
                    if mediatype in self.allowMimes:
                        self.console.putDoc(filename)
                    else:
                        pass
                        #self.console.postMsg(self, "file %s mime %s mismatch"%(filename,mediatype))
            except IOError as errStr:
                self.console.postMsg(self,errStr,True)
        return True        
            