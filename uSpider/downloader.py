#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: leon

import os
import time
import threading
import queue

from urllib.parse import urlparse
import urllib.request
import urllib.error
import mimetypes
from console import uConsole
import logging
import socket

class uDwonloader(threading.Thread):
    def __init__(self,name,console):
        threading.Thread.__init__(self)
        self.console = console
        self.name = name
        self.count = 0
        self.allowMimes=set(['text/html'])
        socket.setdefaulttimeout(5.0)

    def tryDownload(self,url,filepath):
        try:
            if os.path.isfile(filepath):
                self.console.postMsg(self,"skip:%s"%url)
                return True
            self.console.postMsg(self, "request "+url)
            urlfp =  urllib.request.urlopen(url)
            self.handleUrlContent(urlfp,filepath)
            urlfp.close()
            self.console.postMsg(self, "done "+url)
        except urllib.error.HTTPError as e:
            self.console.postMsg(self, "%d %s => url:%s"%(e.code,e.reason,url),True)
            return True
        except urllib.error.URLError as e:
            if hasattr(e, 'reason'):
                errStr = str(e.reason)
                self.console.postMsg(self, "%s => url:%s"%(errStr,url),True)
                # if timeout, retry download it
                if errStr.find('timed out') >= 0:
                    return False
            else:
                self.console.postMsg(self, "%s => url:%s"%("URLError",url),True)
            return True
        else:
            pass
        return True
    
    def run(self):
        while True:
            url = self.console.getUrl(self)
            if url == None:
                self.console.postMsg(self,"thread exit")
                break
            
            parser = urlparse(urllib.parse.unquote(url))
            filepath = self.console.rootPath+parser.path
            
            retry = 3
            while retry > 0:
                if self.tryDownload(url,filepath):
                    break;
                else:
                    retry-=1
                    self.console.postMsg(self, "retryDownload => url:%s"%(url),True)
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
            