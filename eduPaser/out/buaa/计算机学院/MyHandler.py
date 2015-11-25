# coding=utf-8
import os
from models import Employee
from bs4 import BeautifulSoup
from config import Config
from mparser import ProfileParser
from mparser import get_doc_bySelenium

# @brief: 函数将过滤结果转化为Employee数据
# @tag: 输入为待处理的BeautifulSoup的tag对象
# @output:输出employee
def handler(tag):
    
    name_spans = tag.find_all(class_="handle")
    if not name_spans or len(name_spans) == 0:
        return None
    
    # js <span class="handle" onclick="toCardDetailAction('10c07e70-3fb6-42af-aa26-bfab26b6ce0406');" style="color:#2084D2;font-size: 16px;">艾明晶</span>
    
    employee = Employee()
    employee.name = name_spans[0].get_text()
    employee.name = ''.join(employee.name.split())
    
    card_id = name_spans[0]['onclick'][len('toCardDetailAction(\''):-3]
    employee.url = 'http://scse.buaa.edu.cn/buaa-css-web/toCardDetailAction.action?firstSelId=CARD_TMPL_OF_FIRST_NAVI_CN%20&%20secondSelId=CARD_TMPL_OF_ALL_TEACHER_CN%20&cardId='+card_id
    print ("card_id=[%s]"%card_id)

    
    lines = tag.stripped_strings
    parser = ProfileParser(lines=lines,employee=employee)
    return parser.parse()

def set_attr_hook(name,value):
    if name == "profile":
        print value
        if u'www' in value:
            return value
    return ''


def profile_handler(doc,name,url,path):
    employee = Employee(name=name,url=url)
    filename = os.path.join(path, name + ".html")
    div = None
    
    # 保存名称和个人主页，个人简历文件另存当前目录
    soup = BeautifulSoup(doc, Config.SOUP_PARSER)
    divs = soup.find_all(name="div",class_="right_content",limit=1)
    if not divs or len(divs) == 0:
        print("id main not found:  %s"%url)
        return employee
    
    div = divs[0]
    with open(filename,'wb') as fp:
        content = div.prettify()
        fp.write(content)
        fp.close()
    
    
    return employee