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
# employee可用属性(url, name, email, tel, title, profile, research, departments,fax,addr):

'''
<Page index="/personnel/index.xml" folder="personnel">
        <Text>
                <Member>
                        <Name>曹庆宏 研究员</Name>
                        <FileName>CaoQH</FileName>
                        <Education>密歇根州立大学博士（2005年）</Education>
                        <Field>TeV物理与超出标准模型的新物理（理论物理研究所）</Field>
                        <Contact>电话 62762606</Contact>
                        <Homepage>http://www.phy.pku.edu.cn/~qhcao/index.html</Homepage>
                        <Office>South 432, Physics BLDG</Office>
                </Member>
        </Text>
</Page>
'''
    
def profile_handler(doc,name,url,path):
    symbols = {
        u'个人主页：'   :'profile',
        u'研究方向：'   :'research',
        u'电话:':'tel',
        u'电话':'tel'
    }
    filename = path+name+".html"
    
    employee = Employee(name=name,url=url)
    # 太乱了，只保存名称和个人主页，个人简历文件另存当前目录
    soup = BeautifulSoup(doc, Config.SOUP_PARSER)
    divs = soup.find_all(id="sub_main",limit=1)
    if not divs or len(divs) == 0:
        # xml
        members = soup.find_all(name="member",limit=1)
        if not members or len(members) == 0:
            print("id:main or sub_main not found")
            #print doc
            return employee
        member = members[0]
        # title
        names = member.find_all('name')
        if not names and len(names) != 0:
            name = name[0].string
            if name:
                idx = name.find(' ')
                if idx != -1:
                    employee.title = name[idx:]
        if member.field:
            employee.research = member.field.string or ''
        if member.homepage:
            employee.profile = member.homepage.string or ''
        if member.contact:
            if member.contact.string:
                for i,c in enumerate(member.contact.string):
                    if c.isdigit():
                        employee.tel += c
        
        with open(filename,'wb') as fp:
            content = member.prettify()
            fp.write(content)
            fp.close()
        return employee
    
    div = divs[0]
    with open(filename,'wb') as fp:
        content = div.prettify()
        fp.write(content)
        fp.close()
        
    h4s = div.find_all('h4')
    if not h4s and len(h4s) != 0:
        name = h4s[0].string
        idx = name.find(' ')
        if idx != -1:
            employee.tite = name[idx:]
            employee.tite = ''.join(employee.tite.split())
            
    lis = div.find_all("li",limit=8)
    if not lis or len(lis) == 0:
        return employee
    res = lis[0]
    # 解析详细内容
    for count,tag in  enumerate(lis[0].children):
        text = tag.string
        if not text:
            continue
        if len(text) == 0:
            continue
        text = ''.join(text.split())
        if '@' in text:
            employee.email = text
            continue
                
        for symbol,name in symbols.items():
            idx = text.find(symbol)
            if idx != -1:
                idx += len(symbol)
                value = text[idx:]
                if hasattr(employee, name):
                    setattr(employee, name, value)
                    print (name + ":" + value)
                else:
                    print ("no attr %s in employee" % name)
                break
    return employee
