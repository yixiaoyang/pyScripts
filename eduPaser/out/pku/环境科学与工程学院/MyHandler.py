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
    tables = soup.find_all(name="table",limit=4)
    if len(tables)  < 2:
        return employee

    tabel_content = tables[3]
    with open(filename, 'wb') as fp:
        content = tabel_content.prettify()
        fp.write(content)
        fp.close()

    td = tabel_content.find_all("td",attrs={"valign":"top","width":"577"})
    if not td or len(td) == 0:
        return employee

    # 提取各人信息
    lines = td[0].stripped_strings
    parser = ProfileParser(lines=lines,employee=employee)
    return parser.parse()
