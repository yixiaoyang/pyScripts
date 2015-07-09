#!/bin/sh
# File path: ~/sh/laptop_sensors.sh
# author: Weihong Guan (@aGuegu) 2013-01-16
# replace  with your application

apikey=b06b39d890b39332127b90637f728e64
url_core0=http://api.yeelink.net/v1.1/device/115167/sensor/144483/datapoints
curl -d "{\"value\":50}" -H "U-ApiKey: b06b39d890b39332127b90637f728e64" 'http://api.yeelink.net/v1.1/device/115167/sensor/144483/datapoints'