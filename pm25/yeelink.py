#! /usr/bin/env python                                                                                                                
# -*- coding: utf-8 -*-  

#
# email sent app
# by leon@2015-07-09
#
# curl -d "{\"value\":50}" -H "U-ApiKey: b06b39d890b39332127b90637f728e64" 'http://api.yeelink.net/v1.1/device/115167/sensor/144483/datapoints'
#
import time
import json
import requests

# example: http://api.yeelink.net/v1.1/device/115167/sensor/144020/datapoints
class YeelinkHelper:
    url = 'http://api.yeelink.net/v1.1'
    key = ''
    hdr = ''
    dev = ''
    sensors = []

    def __init__(self,key,dev,sensors):
        self.key = key
        self.dev = dev
        self.sensors = sensors
        self.hdr = {'U-ApiKey':key,'content-type': 'application/json'}
    def up(self,vals):
        idx = 0
        utime=time.strftime("%Y-%m-%dT%H:%M:%S")
        for sen in self.sensors:
            if idx < len(vals):
                post_url=r'%s/device/%s/sensor/%s/datapoints' % (self.url, self.dev, sen)
                data={"timestamp":utime , "value": vals[idx]}
                res=requests.post(post_url,headers=self.hdr,data=json.dumps(data))
                idx += 1
                print("utime:%s, url:%s, status_code:%d" %(utime,post_url,res.status_code))
                print(self.hdr)
                print(json.dumps(data))
