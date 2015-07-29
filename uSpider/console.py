#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: leon 

import os
import time
import threading
import queue
import logging
import unittest

class uConsole():
    def __init__(self, name, rootUrl, index="index.html", rootPath="./dl", urlQsize=1024, docQsize=1024):
        self.name = name
        
        ###self.urls = queue.Queue(urlQsize)
        ###self.docs = queue.Queue(docQsize)
        self.urls = set()
        self.docs = set()
        
        rootUrl.strip(' \t')
        rootUrl.rstrip('/')
        
        self.rootPath = rootPath + '/' + rootUrl

        if rootUrl.find('http://') != 0:
            rootUrl = 'http://'+rootUrl
        self.rootUrl = rootUrl
        
        index.lstrip('./')
        self.index = index
        
        self.putUrl(self.index)
        self.urlLock = threading.Lock()
        self.docLock = threading.Lock()
        self.urlWorkerCnt = 0
        self.docWorkerCnt = 0
        
        logging.basicConfig(level=logging.DEBUG,
                            datefmt='%a, %d %b %Y %H:%M:%S',
                            filename=rootPath+'/err.log',
                            filemode='w')
    def register(self,child):
        self.children[child.name] = child
        print ("[MSG:%-12s] child %s registerd" %(self.name, child.name))
    
    def postMsg(self, child, msg, err=False):
        if err:
            errStr = "[ERR:%-10s] %s" %(child.name,msg)
            print (errStr)
            logging.error(errStr)
        else:
            print ("[MSG:%-10s][%d/%d] %s" %(child.name,len(self.urls),len(self.docs),msg))
            
    def urlsEmpty(self):
        return len(self.urls)==0
    
    def docsEmpty(self):
        return len(self.docs)==0
    
    def done(self):
        #print ("[MSG:%-10s] urls %d docs %d %d %d" %(self.name,len(self.urls),len(self.docs),self.urlWorkerCnt,self.docWorkerCnt))
        return self.urlsEmpty() and self.docsEmpty() and (self.urlWorkerCnt == 0) and (self.docWorkerCnt == 0)
    
    #
    # 格式： "a.html"，加上self.rootUrl+'/'才形成完整url
    #
    def putUrl(self,url):
        self.urls.add(url)
        
    def putDoc(self,doc):      
        self.docs.add(doc)
        
    #
    # @brief 非阻塞获取url资源
    # @return 若没有done则一直尝试获取直到获取到一条url，否则返回None
    #
    def getUrl(self,child):
        self.urlLock.acquire()
        
        while True:
            if self.done():
                self.urlLock.release()
                return None
            try:
                if not self.urlsEmpty():
                    url = self.urls.pop()
                    self.urlWorkerCnt += 1
                    break;
            except KeyError:
                # empty URLs, sleep 50ms
                time.sleep(0.05)    
                continue;
        
        #self.postMsg(child,"getUrl %s"%(url))
        self.urlLock.release()
        
        return self.rootUrl+'/'+url 
    #
    # @brief 非阻塞获取doc资源
    # @return 若没有done则一直尝试获取直到获取到一条doc，否则返回None
    #
    def getDoc(self,child):
        self.docLock.acquire()
        
        while True:
            if self.done():
                self.docLock.release()
                return None
            try:
                doc = self.docs.pop()
                self.docWorkerCnt += 1
                break;
            except KeyError:
                # empty Docs, sleep 50ms
                time.sleep(0.05) 
                continue;
        #self.postMsg(child,"getDoc %s"%(doc))
        self.docLock.release()
        return doc
    
    