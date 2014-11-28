#!/usr/bin/env python
# -*- coding:utf-8 -*-

import urllib.request

debug=True
#debug=False

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

    def ParseResultStr(resultstr):
        if(debug): print(resultstr)
        slist=resultstr[14:-3]
        if(debug): print(slist)
        slist=slist.split('~')

        if(debug) : print(slist)

        #print('*******************************')
        print('  股票名称:', slist[1])
        print('  股票代码:', slist[2])

        print('  当前价格:', slist[3])
        print('  涨    跌:', slist[4])
        print('  涨   跌%:', slist[5],'%')
        print('成交量(手):', slist[6])
        print('成交额(万):', slist[7])
        #print('date and time is :', dateandtime)
        print('*******************************')

    def GetStockInfo(num):
        str=StockInfo.GetStockStrByNum(num)
        strGB=Utility.ToGB(str)
        StockInfo.ParseResultStr(strGB)


if __name__ == '__main__':
    stocks = ['sz002065']
    for stock in stocks:
        StockInfo.GetStockInfo(stock)
