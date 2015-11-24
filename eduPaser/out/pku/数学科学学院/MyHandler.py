# coding=utf-8

from models import Employee
from bs4 import BeautifulSoup
from config import Config

# driver
import urllib2
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
import selenium.webdriver.support.ui as ui

# @brief: 函数将过滤结果转化为Employee数据
# @tag: 输入为待处理的BeautifulSoup的tag对象
# @output:输出employee
def handler(tag):
    employee = Employee(url=tag['href'], name=tag.string)
    #print(tag)
    return employee

#<a onclick="$(&quot;#more&quot;).show();resizePage();">显示更多</a>

# @doc: 输入为个人详情页的整个网页源码
# @output:输出employee，如果没有检测到内容返回None
# employee可用属性(url, name, email, tel, title, profile, research, departments,fax,addr):
def profile_handler(doc,name,url,path):
    symbols = {
        0:None,
        1:"title",
        2:"departments",
        3:None,
        4:"research",
        5:"profile",
        6:None,
        7:"tel",
        8:"email",
        9:None
    }
    employee = Employee(name=name,url=url)
    div = None
    # 太乱了，只保存名称和个人主页，个人简历文件另存当前目录
    soup = BeautifulSoup(doc, Config.SOUP_PARSER)
    divs = soup.find_all(id="main",limit=2)
    if not divs or len(divs) == 0:
        print("id main not found:  %s"%url)
        return employee
    if len(divs) >= 2:
        div = divs[1]
    else:
        div = divs[0]
    filename = path+name+".html"
    with open(filename,'wb') as fp:
        content = div.prettify()
        fp.write(content)
        fp.close()
    
    # 解析详细内容
    
    #print("\n\n\n\n\n\div1\n\n\n\n\n\n")
    #print doc
    
    td_c2s = div.find_all(name="td",attrs={"class":"c2"},limit=11)
    
    idx = 0
    for td in td_c2s:
        name = symbols.get(idx)
        idx += 1
        
        if not name:
            continue
        value = td.string
        if not value:
            continue
        
        if idx != 9:
            value = ''.join(value.split())
        else:
            value = value.strip() 
            
        #print (name + ":" + value)
        if hasattr(employee, name):
            setattr(employee, name, value)
        else:
            print ("no attr %s in employee" % name)
    return employee


def engine_handler(driver):
    doc = None
    try:
        wait = ui.WebDriverWait(driver,10)
        wait.until(lambda driver: driver.find_element_by_id('photo_ext'))
        
        more_link = driver.find_element_by_link_text(u'显示更多')
        more_link.click()
        wait.until(lambda driver: driver.find_element_by_id('more'))
        doc = driver.page_source
    except Exception as e:
        return doc
    return doc