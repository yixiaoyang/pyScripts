# coding=utf-8

from models import Employee
from bs4 import BeautifulSoup
from config import Config


# @brief: 函数将过滤结果转化为Employee数据
# @tag: 输入为待处理的BeautifulSoup的tag对象
# @output:输出employee
def handler(tag):
    employee = Employee(url=tag['href'], name=tag.string)
    #print(tag)
    return employee


# @doc: 输入为个人详情页的整个网页源码
# @output:输出employee，如果没有检测到内容返回None

def profile_handler(doc,name,url,path):
    # 太乱了，只保存名称和个人主页，个人简历文件另存当前目录
    soup = BeautifulSoup(doc, Config.SOUP_PARSER)
    div = soup.find_all(id="s2_right_con",limit=1)
    filename = path+name+".html"
    if not div or len(div) == 0:
        return Employee(name=name,url=url)
    with open(filename,'wb') as fp:
        content = div[0].prettify()
        fp.write(content)
        fp.close()
    return Employee(name=name,url=url)
