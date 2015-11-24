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

'''
姓名：艾海舟
职称：教授
邮箱：ahz@tsinghua.edu.cn
URL：http://media.cs.tsinghua.edu.cn/cn/aihz
电话：010-62795495
传真：010-62795871
工学学士 (计算机应用), 清华大学, 中国, 1985;
工学硕士 (计算机应用), 清华大学, 中国, 1988;
工学博士 (计算机应用), 清华大学, 中国, 1991.
研究领域
计算机视觉与模式识别
讲授课程
'''


def profile_handler(doc,name,url,path):
    # employee可用属性(url, name, email, tel, title, profile, research, departments,fax,addr):
    symbols = {
        'name': u'姓名：',
        'email': u'邮箱：',
        'tel': u'电话：',
        'fax': u'传真：',
        'url': u'URL：',
        'title': u'职称：'
    }
    soup = BeautifulSoup(doc, Config.SOUP_PARSER)
    divs = soup.find_all(id="s2_right_con",limit=1)
    div = divs[0]
    
    filename = path+name+".html"
    with open(filename,'wb') as fp:
        content = div.prettify()
        fp.write(content)
        fp.close()

    # 提取前15个p标签就够了
    ps = div.find_all(name="p",limit=20)
    employee = None
    for count, p in enumerate(ps):
        text = p.text
        for name, symbol in symbols.items():
            idx = text.find(symbol)
            if idx != -1:
                idx += len(symbol)
                value = text[idx:]
                if not employee:
                    employee = Employee()
                if hasattr(employee, name):
                    setattr(employee, name, value)
                    # print (name + ":" + value)
                else:
                    print ("no attr %s in employee" % name)
                break
    return employee
