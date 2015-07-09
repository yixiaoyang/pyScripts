#! /usr/bin/env python                                                                                                                # -*- coding: utf-8 -*-  

#
# pms module detect
# by leon@2015-07-09
# 
# curl -d "{\"value\":50}" -H "U-ApiKey: b06b39d890b39332127b90637f728e64" 'http://api.yeelink.net/v1.1/device/115167/sensor/144483/datapoints'
#

# -*- coding: utf-8 -*-  

import serial
from yeelink import YeelinkHelper

# global enum
DATALEN     = 10
SBYTE       = 0xaa
EBYTE       = 0xab
HDR_IDX     = 0     #0xaa
CMD_IDX     = 1
PM25L_IDX   = 2
PM25H_IDX   = 3
PM10L_IDX   = 4
PM10H_IDX   = 5
R1_IDX      = 6
R2_IDX      = 7
CHK_IDX     = 8
END_IDX     = 9     #0xab

# yeelink 
YEELINK_API_KAY = 'b06b39d890b39332127b90637f728e64'
YEELINK_DEV = '115167'
# pm2.5, pm10, cpu_temp
YEELINK_SENSORS = ['144020','144022','144483']

class RPiDev:
    @staticmethod
    def get_cpu_temp():
        cpu_temp_file = open( "/sys/class/thermal/thermal_zone0/temp" )
        cpu_temp = cpu_temp_file.read()
        cpu_temp_file.close()
        return float(cpu_temp)/1000
    
class PmsMod:
    def __init__(self,p,ydev):
        self.port = p
        self.idx = 0
        self.maxLen = DATALEN*2
        self.datas = [0]*self.maxLen
        self.ydev = ydev
    
    def getPm25(self,pos):
        offset = pos*DATALEN + PM25L_IDX
        return float(self.datas[offset]+256*self.datas[offset+1])/10;
    
    def getPm10(self,pos):
        offset = pos*DATALEN + PM10L_IDX
        return float(self.datas[offset]+256*self.datas[offset+1])/10;        
    
    def collect(self):
        # read firs start byte
        byte=ord(self.port.read())
        while byte != EBYTE:
            byte=ord(self.port.read())
            print(byte)
        self.idx = 0
        
        count = 0 
        while True:
            byte = self.port.read()
            self.datas[self.idx] = ord(byte)
            self.idx += 1
            
            if self.idx == self.maxLen:
                count+=1
                # every 5*2=10s
                if count >= 5:
                    pos = self.idx/DATALEN-1
                    pm25 = self.getPm25(pos)
                    pm10 = self.getPm10(pos)
                    cpu_temp = RPiDev.get_cpu_temp()
                    vals = [int(pm25),int(pm10),int(cpu_temp)]
                    self.ydev.up(vals)
                    print("pm25=%.1fug/m3, pm10=%.1fug/m3 tmp=%.1f'C" %(pm25,pm10,cpu_temp))
                    count = 0
                self.idx = 0
    
if __name__ == "__main__":
    ydev1 = YeelinkHelper(YEELINK_API_KAY,YEELINK_DEV,YEELINK_SENSORS)
    port = serial.Serial("/dev/ttyAMA0",baudrate=9600,bytesize=8,parity='N',stopbits=1,xonxoff=0,timeout=3.0)
    mod = PmsMod(port,ydev1)
    mod.collect()
    port.close()