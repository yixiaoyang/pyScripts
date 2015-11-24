# coding=utf-8
import os
from models import Employee
from bs4 import BeautifulSoup
from config import Config
from mparser import ProfileParser


# @brief: 函数将过滤结果转化为Employee数据
# @tag: 输入为待处理的BeautifulSoup的tag对象
# @output:输出employee
def handler(tag):
    tds = tag.find_all(name='td')
    if not tds or len(tds) != 3:
        return None
    employee = Employee()

    employee.name = tds[0].get_text() or ''
    employee.name = ''.join(employee.name.split()) 
    
    # 过滤表头
    if employee.name == u'姓名':
        return None
    
    employee.title = tds[1].get_text()
    employee.title = ''.join(employee.title.split()) 
    
    employee.email = tds[2].get_text()
    employee.email = ''.join(employee.email.split()) 
    employee.email = email_value_strip(employee.email)
    # print(tag)
    return employee

def email_value_strip(value):
    new_value = value.replace('(at)','@')
    new_value = new_value.replace('（at）','@')
    new_value = new_value.replace('@.','@')
    return new_value
    return value

