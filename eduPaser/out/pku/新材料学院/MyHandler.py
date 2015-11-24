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
    
    lines = tag.stripped_strings
    
    ass = tag.find_all(name="a",attrs={"class":"dt_text_tit"})
    if not ass or len(ass) == 0:
        # first line is the name
        for count,line in enumerate(lines):
            employee.name = line
            break
    else:
        employee.name = ass[0].string
        employee.profile = ass[0]['href']
        employee.url = employee.profile
    
    parser = ProfileParser(lines=lines,employee=employee)
    employee = parser.parse()
    return employee

# @doc: 输入为个人详情页的整个网页源码
# @output:输出employee，如果没有检测到内容返回None          
# employee可用属性(url, name, email, tel, title, profile, research, departments,fax,addr):
def profile_handler(doc, name, url, path):
    filename = os.path.join(path, name + ".html")
    employee = Employee(name=name, url=url)

    # 只保存名称和个人主页，个人简历文件另存当前目录
    soup = BeautifulSoup(doc, Config.SOUP_PARSER)
    
    divs = soup.find_all(name="div",attrs={"id":"dt_right","class":"staff"}, limit=1)
    if not divs or len(divs) == 0:
        return employee

    div = divs[0]
    with open(filename, 'wb') as fp:
        content = div.prettify()
        fp.write(content)
        fp.close()

    return employee
