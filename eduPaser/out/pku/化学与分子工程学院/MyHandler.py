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
    employee = Employee(url=tag['href'], name=tag.string)
    # print(tag)
    return employee


# @doc: 输入为个人详情页的整个网页源码
# @output:输出employee，如果没有检测到内容返回None          
# employee可用属性(url, name, email, tel, title, profile, research, departments,fax,addr):
def profile_handler(doc, name, url, path):
    filename = os.path.join(path, name + ".html")
    employee = Employee(name=name, url=url)

    # 太乱了，只保存名称和个人主页，个人简历文件另存当前目录
    soup = BeautifulSoup(doc, Config.SOUP_PARSER)
    divs = soup.find_all(name="td", class_="bd-content", limit=1)
    if not divs or len(divs) == 0:
        divs = soup.find_all(name="td", attrs={"width": "79%"}, limit=1)
        if not divs or len(divs) == 0:
            with open(filename, 'wb') as fp:
                content = doc
                fp.write(content)
                fp.close()
            return employee

    div = divs[0]
    with open(filename, 'wb') as fp:
        content = div.prettify()
        fp.write(content)
        fp.close()

    # 使用纯文本方式处理
    lines = div.stripped_strings
    # text=div.get_text(strip=True)
    parser = ProfileParser(lines=lines,employee=employee)
    return parser.parse()
