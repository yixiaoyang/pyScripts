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
    employee = Employee()
    ass = tag.find_all('a',class_="orangea")
    if ass and len(ass) != 0:
        employee.name = ass[0].get_text()
        employee.name = ''.join(employee.name.split())
        employee.profile = ass[0]['href']
    
    ass = tag.find_all('a',class_="black01")
    if ass and len(ass) != 0:
        lines = ass[0].stripped_strings
        parser = ProfileParser(lines=lines,employee=employee)
        employee = parser.parse()
    return employee