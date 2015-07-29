#!/usr/bin/env python
#-*- coding: UTF-8 -*-  

'''
parser：解析document，生成url
downloader：请求url，下载document
console：监控url，document及其他进程资源情况
'''

import os
import time
import threading
import queue  
from downloader import uDwonloader
from console import uConsole
from parser import uParser

import unittest

if __name__ == '__main__':
    baseUrl=r"yinwang.org"
    partterns=set()
    cnt = 0
    p = []
    
    baseUrl.lstrip()
    
    baseUrls=["http://www.%s"%(baseUrl), "www.%s"%(baseUrl), "http://%s"%(baseUrl)]
    for url in baseUrls:
        partterns.add("[\"\']%s/([^\'\"]+)[\"\']{1}"%(url))

    console = uConsole("Monitor",baseUrl)
    parser = uParser("Parser[%d][1]"%(cnt), console)
    parser.addPartterns(partterns)
    dl1 = uDwonloader("dl[%d][1]"%(cnt), console)
    dl2 = uDwonloader("dl[%d][2]"%(cnt), console)
    p.append(parser)
    p.append(dl1)
    p.append(dl2)

    for process in p:
        process.start()
    cnt += 1


