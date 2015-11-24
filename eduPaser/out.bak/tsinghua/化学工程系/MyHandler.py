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
蒋国强
副教授
研究方向：药物传输工程和控释技术、化学与生物反应工程
    办公电话： (O)86-10-62782824 (L)86-10-62773845
    办公地址：北京清华大学英士楼4层 化学工程系 生物化工研究所
    电子邮件： jianggq@tsinghua.edu.cn

<td valign="top">
<h3>蒋国强 </h3>
<dl>
<dt>副教授</dt>
<dt>研究方向：药物传输工程和控释技术、化学与生物反应工程</dt>
<dd>办公电话： (O)86-10-62782824  (L)86-10-62773845</dd>
<dd>办公地址：北京清华大学英士楼4层 化学工程系 生物化工研究所</dd>
<dd>电子邮件： jianggq@tsinghua.edu.cn</dd>
</dl>
</td>

<div class="teachcontent"><p><a href="http://www.chemeng.tsinghua.edu.cn/scholars/jianggq/indexsc.html"><span style="color: rgb(0, 0, 255);"><u><strong>个人主页地址</strong></u></span></a></p>
</div>
'''


def profile_handler(doc,name,url,path):
    # employee可用属性(url, name, email, tel, title, profile, research, departments,fax,addr):
    symbols = {
        'email': u'电子邮件：',
        'tel': u'办公电话：',
        'addr': u'办公地址：',
        'research':u'研究方向：'
    }
    employee = None

    soup = BeautifulSoup(doc, Config.SOUP_PARSER)
    divs = soup.find_all("td",attrs={"valign":"top"},limit=1)
    if not divs or len(divs) == 0:
        return employee

    div = divs[0]
    employee = Employee()
    
    # save file
    filename = path+name+".html"
    with open(filename,'wb') as fp:
        content = div.prettify()
        fp.write(content)
        fp.close()
        
    # parse name
    name_h3 = div.h3
    if name_h3:
        employee.name = name_h3.string.strip(' \t\n\r')
    else:
        print name_h3
    # parse title
    dls = soup.dl
    if dls and len(dls) >= 1:
        print dls
        if dls.dt:
            employee.title = dls.dt.string
        # parse everything
        for tag in dls.children:
            if not tag.string:
                continue
            text = tag.string.strip(' \t\n\r')
            if len(text) == 0:
                continue
            for name, symbol in symbols.items():
                idx = text.find(symbol)
                if idx != -1:
                    idx += len(symbol)
                    value = text[idx:]
                    if hasattr(employee, name):
                        setattr(employee, name, value)
                        # print (name + ":" + value)
                    else:
                        print ("no attr %s in employee" % name)
                    break
    # parse profile
    teachcontent = soup.find_all("div",class_="teachcontent",limit=1)
    if len(teachcontent) != 0:
        content = teachcontent[0]
        link= content.a
        if link:
            employee.url = link['href']

    return employee
