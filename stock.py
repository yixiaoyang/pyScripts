#!/usr/bin/env python
# -*- coding:utf-8 -*-

#import urllib.request
import urllib2

#debug=True
debug=False
headerFormat="%-12s %-8s %-8s %-8s %-12s %-12s %-12s"

def ToGB(str):
   if(debug): print(str)
   return str.decode('gb2312')

class StockInfo:
    """
     0: 未知
     1: 名字
     2: 代码
     3: 当前价格
     4: 涨跌
     5: 涨跌%
     6: 成交量（手）
     7: 成交额（万）
     8:
     9: 总市值"""

    def ParseResultStr(self,num,resultstr):
        if(debug): print(resultstr)
        slist=resultstr[14:-3]
        if(debug): print(slist)
        slist=slist.split('~')
        if(debug) : print(slist)        
        lineStr=headerFormat % (num,slist[3],slist[4],slist[5],slist[6],slist[7],slist[1])
        print(lineStr)

    def GetStockInfo(self,num):
        request = urllib2.urlopen('http://qt.gtimg.cn/q=s_'+ str(num))
        mstr=request.read()
        strGB=ToGB(mstr)
        self.ParseResultStr(num,strGB)
    
if __name__ == '__main__':
    stocks = ['sz399001','sh000001','sz002415','sh600588','sz002439'] 
    headerStr=headerFormat % ('Code','Last','Chg','Chg%','Hand','Volume','Name')
    print(headerStr)
    
    stockinfo=StockInfo()
    for stock in stocks:
        stockinfo.GetStockInfo(stock)
