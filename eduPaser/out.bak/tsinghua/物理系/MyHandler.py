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
    symbols = {
        u'电话：'      :'tel',  
        u'联系电话：'   :'tel',
        u'传真：'      :'fax',
    }
        
    employee = Employee(name=name,url=url)
    # 太乱了，只保存名称和个人主页，个人简历文件另存当前目录
    soup = BeautifulSoup(doc, Config.SOUP_PARSER)
    divs = soup.find_all(name="div",class_="box_detail",limit=1)
    if not divs or len(divs) == 0:
        return employee
    div = divs[0]
    
    filename = path+name+".html"
    with open(filename,'wb') as fp:
        content = div.prettify()
        fp.write(content)
        fp.close()
    
    td_left = div.find_all("td",attrs={ "style":"line-height: 16px","align":"left"})
    if not td_left or len(td_left) == 0:
        return employee
    
    # 解析详细内容
    links = div.find_all("a",limit=2)
    for link in links:
        if link.string:
            if '@' in link.string:
                employee.email = link.string
    for count,tag in  enumerate(td_left[0].children):
        if not tag.string:
            continue
        if count > 15:
            break
        
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
    return employee
