#!/bin/sh

filename=$(date "+%Y-%m-%d").html

cd /devel/git/github/pyScripts/spider/spider58/respider/
scrapy crawl rent_spider &> $filename.log
scp $filename root@45.32.58.58:/var/www/html/
#echo -e $passwd | sudo -S poweroff
