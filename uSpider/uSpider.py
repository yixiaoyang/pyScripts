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
    p = []
    baseUrl=r"http://yixiaoyang.github.io"
    
    console = uConsole("Monitor",baseUrl)
    parser = uParser("Parser1", console)
    dl1 = uDwonloader("dl1", console)
    dl2 = uDwonloader("dl2", console)
    p.append(parser)
    p.append(dl1)
    p.append(dl2)

    for process in p:
        process.start()


    