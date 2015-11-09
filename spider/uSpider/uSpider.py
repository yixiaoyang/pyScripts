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
import logging

import unittest

if __name__ == '__main__':
    hostnames = [r'yinwang.org',r'yixiaoyang.github.io']
    cnt = 0
    for host in hostnames:
        # 只接受hostname的url
        partterns=set()
        p = []
        
        host.lstrip()
        
        hosts=["http://www.%s"%(host), "www.%s"%(host), "http://%s"%(host)]
        for url in hosts:
            partterns.add("[\"\']%s/([^\'\"]+)[\"\']{1}"%(url))

        console = uConsole("Console[%d]"%(cnt),host)
        parser = uParser("Parser[%d][1]"%(cnt), console)
        parser.addPartterns(partterns)
        dl1 = uDwonloader("dl[%d][1]"%(cnt), console)
        dl2 = uDwonloader("dl[%d][2]"%(cnt), console)
        p.append(parser)
        p.append(dl1)
        p.append(dl2)

        for process in p:
            process.start()
            
        # 等待所有进程结束
        for process in p:
            process.join()
        cnt += 1


