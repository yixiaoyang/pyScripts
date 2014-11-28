#!/usr/bin/env python
# -*- coding:utf-8 -*-

import urllib.request

#debug=True
debug=False
headerFormat="%-12s %-8s %-8s %-8s %-8s %-8s %-8s"

class Utility:
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

    def GetStockStrByNum(num):
        f= urllib.request.urlopen('http://qt.gtimg.cn/q=s_'+ str(num))
        if(debug): print(f.geturl())
        if(debug): print(f.info())
        #return like: v_s_sz000858="51~五 粮 液~000858~18.10~0.01~0.06~94583~17065~~687.07";
        return f.readline()
        f.close()
    def ParseResultStr(num,resultstr):
        if(debug): print(resultstr)
        slist=resultstr[14:-3]
        if(debug): print(slist)
        slist=slist.split('~')

        if(debug) : print(slist)        
        lineStr=headerFormat % (num,slist[3],slist[4],slist[5],slist[6],slist[7],slist[1])
        print(lineStr)

    def GetStockInfo(num):
        str=StockInfo.GetStockStrByNum(num)
        strGB=Utility.ToGB(str)
        StockInfo.ParseResultStr(num,strGB)
if __name__ == '__main__':
    stocks = ['sz002065','sz002439','sz002294','sz300378','sz002577']
    headerStr=headerFormat % ('Code','Last','Chg','Chg%','Hand','Volume','Name')
    print(headerStr)
    for stock in stocks:
        StockInfo.GetStockInfo(stock)
