# coding=utf-8
import os
from models import Employee
from bs4 import BeautifulSoup
from config import Config
from mparser import ProfileParser

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
import selenium.webdriver.support.ui as ui
from selenium.webdriver.support import expected_conditions as EC
import time

# @brief: 函数将过滤结果转化为Employee数据
# @tag: 输入为待处理的BeautifulSoup的tag对象
# @output:输出employee
def handler(tag):
    employee = Employee()
    name_divs = tag.find_all("div",class_="teacher-title")
    if name_divs and len(name_divs) != 0:
        employee.name = name_divs[0].get_text()
        employee.name = ''.join(employee.name.split())
    
    # 使用纯文本方式处理
    lines = tag.stripped_strings
    # text=div.get_text(strip=True)
    parser = ProfileParser(lines=lines,employee=employee)
    return parser.parse()


# 对于需要预处理的站点进行处理将网站保存到文件以后期处理
def pre_handler(url,filename):
    driver = webdriver.Firefox()
    doc = None    

    driver.get(url)
    doc = driver.page_source
    
    # 点击页面上所有的展开，等待若干秒，保存文件，退出 .pic-techshow > li:nth-child(2) > div:nth-child(1) > span:nth-child(4) > a:nth-child(1)
    list_links = driver.find_elements_by_partial_link_text(u'[展开]')
    for link in list_links:
        link.click()
        time.sleep(0.3)     
    
    with open(filename, 'wb') as fp:
        fp.write(doc)
        fp.close()
    driver.close()


# @doc: 输入为个人详情页的整个网页源码
# @output:输出employee，如果没有检测到内容返回None          
# employee可用属性(url, name, email, tel, title, profile, research, departments,fax,addr):
def profile_handler(doc, name, url, path):
    filename = os.path.join(path, name + ".html")
    employee = Employee(name=name, url=url)

    # 只保存名称和个人主页，个人简历文件另存当前目录
    soup = BeautifulSoup(doc, Config.SOUP_PARSER)
    div = soup
    with open(filename, 'wb') as fp:
        content = div.prettify()
        fp.write(content)
        fp.close()

    # 使用纯文本方式处理
    lines = div.stripped_strings
    # text=div.get_text(strip=True)
    parser = ProfileParser(lines=lines,employee=employee)
    return parser.parse()
