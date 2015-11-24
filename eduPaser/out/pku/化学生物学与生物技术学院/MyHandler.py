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
    lis = tag.find_all('li')
    if len(lis) < 4:
        return None
    employee = Employee()
    
    pre_len = len(u'职务：')
    
    employee.name = lis[0].get_text()
    employee.profile = lis[0].a['href']
    employee.url = employee.url or employee.profile
    if not employee.name:
        employee.name = employee.name[pre_len:]
        employee.name = ''.join(employee.name.split()) 
  
    employee.title = lis[1].get_text()
    if employee.title:
        employee.title =  employee.title[pre_len:]
        employee.title = ''.join(employee.title.split()) 
        
    employee.tel = lis[2].get_text()
    if employee.tel:
        employee.tel =  employee.tel[pre_len:]
        employee.tel = ''.join(employee.tel.split()) 
    
    employee.email = lis[3].get_text()
    if employee.email:
        employee.email =  employee.email[pre_len:]
        employee.email = ''.join(employee.email.split()) 

    print("name:"+employee.name+",email:"+employee.email)
    return employee


# @doc: 输入为个人详情页的整个网页源码
# @output:输出employee，如果没有检测到内容返回None          
# employee可用属性(url, name, email, tel, title, profile, research, departments,fax,addr):
def profile_handler(doc, name, url, path):
    filename = os.path.join(path, name + ".html")
    employee = Employee(name=name, url=url)

    # 只保存名称和个人主页，个人简历文件另存当前目录
    soup = BeautifulSoup(doc, Config.SOUP_PARSER)
    divs = soup.find_all(name="div", class_="teacher-content", limit=1)
    if not divs or len(divs) == 0:
        return employee
    div = divs[0]
    with open(filename, 'wb') as fp:
        content = div.prettify()
        fp.write(content)
        fp.close()
    
    return employee