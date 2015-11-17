from bs4 import BeautifulSoup
from urlparse import urlparse
from urlparse import urljoin
import urllib2
import sys

#url = "http://www.pku.edu.cn/academics/index.htm"
#request = urllib2.urlopen(url, timeout=10)
#doc = request.read()
#request.close()
#with open('index.html','wb') as fp:
#    fp.write(doc)
#    fp.close()

doc = None
with open('index.html','rb') as fp:
    doc = fp.read()
    fp.close()

soup = BeautifulSoup(doc,"html.parser")
#soup = BeautifulSoup(doc,"lxml")
res = soup.find_all("a",attrs={"target":"_blank"})
print (len(res))
for i, r in enumerate(res):
    print r
