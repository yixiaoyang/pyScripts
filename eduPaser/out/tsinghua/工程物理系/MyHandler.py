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
    # employee可用属性(url, name, email, tel, title, profile, research, departments,fax,addr):
    symbols = {
        u'Email：'    :'email',
        u'email：'   :'email',
        u'邮箱：'      :'email',
        u'邮件：':     "email",
        u'电子邮件：'   :'email',
        u'电子邮箱：'   :'email',
        u'电子邮件地址：':'email',
        u'电子邮件地址' :'email',
        u'E-MAIL:'      :'email',
        u'电话：'      :'tel',  
        u'联系电话：'   :'tel',
        u'Tel：'       :'tel',
        u'办公电话：'   :'tel',
        u'传真：'      :'fax',  
        u'Fax：'      :'fax',  
        u'URL：'      :'url',
        u'职称：'      :'title'
    }
    employee = None
    
    # 太乱了，只保存名称和个人主页，个人简历文件另存当前目录
    soup = BeautifulSoup(doc, Config.SOUP_PARSER)
    divs = soup.find_all(id="s2_right_con",limit=1)
    filename = path+name+".html"
    if not divs or len(divs) == 0:
        return Employee(name=name,url=url)
    div =divs[0]
    with open(filename,'wb') as fp:
        content = div.prettify()
        fp.write(content)
        fp.close()
     
    
    employee = Employee()
    for tag in div.children:
        if not tag.string:
            continue
        text = tag.string
        text = ''.join(text.split())
        if len(text) == 0:
            continue
        for symbol,name in symbols.items():
            idx = text.find(symbol)
            if idx != -1:
                idx += len(symbol)
                value = text[idx:]
                if hasattr(employee, name):
                    setattr(employee, name, value)
                    symbols
                    # print (name + ":" + value)
                else:
                    print ("no attr %s in employee" % name)
                break
    return  employee
