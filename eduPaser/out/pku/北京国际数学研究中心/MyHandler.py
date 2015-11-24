# coding=utf-8
import os
from models import Employee
from bs4 import BeautifulSoup
from config import Config
from mparser import ProfileParser


# @brief: 函数将过滤结果转化为Employee数据
# @tag: 输入为待处理的BeautifulSoup的tag对象
# @output:输出employee
# employee可用属性(url, name, email, tel, title, profile, research, departments,fax,addr):
def handler(tag):
    dd_tables = {
        "Email":"email",
        "Phone":"tel",
        "Homepage":"profile",
        'Math Fields':'research'
    }
    
    h3 = tag.find_all(name='h3')
    if not h3:
        return None
    employee = Employee()
    employee.name = h3[0].get_text() or ''
    employee.name = ''.join(employee.name.split()) 
    
    title_spans = tag.find_all(name="span",class_="faculty-title")
    employee.title = title_spans[0].get_text()
    #employee.title = ''.join(employee.title.split()) 

    tds = tag.find_all(name='dt',class_="faculty-info")
    if not tds or len(tds) < 5:
        return None
    
    employee.email = tds[0].get_text()
    employee.email = ''.join(employee.email.split()) 
    
    employee.tel = tds[1].get_text()
    employee.tel = ''.join(employee.tel.split()) 
        
    employee.profile = tds[3].get_text()
    employee.profile = ''.join(employee.profile.split()) 
    
    employee.research = tds[4].get_text()
    #employee.research = ''.join(employee.research.split()) 

    return employee
