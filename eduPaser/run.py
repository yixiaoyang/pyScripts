#!/usr/bin/python
# -*- coding: utf-8 *-*

import sys
import csv
import os
import imp

from log import *
from config import Config
from config import path_of
from parser import SimpleAParser
from parser import AutoAcademyParser
from parser import Parser
from parser import Hao123_211_Parser
from models import College, China211
from models import unserialize_object,serialize_instance,obj_to_json,obj_to_file,obj_from_file

logger = None
china211 = None
colleges = list()


def parse_colleges():
    if len(colleges) != 0:
        logger.error("colleges list existed, ignore parsing")
        return
    hao123_parser = Hao123_211_Parser(Config.C211_URL)
    if hao123_parser.run():
        for item in hao123_parser.rlist:
            college = College(item['href'], item.string)
            colleges.append(college)
            print("href:%s" % item['href'])


def print_colleges():
    for i, c in enumerate(colleges):
        symbol = ' '
        if len(c.academiesUrl) != 0:
            symbol = '#'
        print("[%2s][%3d] %s , %s , %s " % (symbol, i, c.name, c.eng_name, c.url))


def colleges_to_csv():
    fieldnames = ['name', 'eng_name', 'url']
    with open(path_of(Config.COL_CSV_FILE), 'wb') as csvfp:
        writer = csv.DictWriter(csvfp, fieldnames=fieldnames, delimiter=',',
                                quotechar='|', quoting=csv.QUOTE_MINIMAL)
        # writer.writeheader()
        for c in colleges:
            writer.writerow({'name': c.name, 'eng_name': c.eng_name, 'url': c.url})
        csvfp.close()
    logger.info("All %d colleges save to %s done" % (len(colleges), path_of(Config.COL_CSV_FILE)));


def csv_to_colleges():
    with open(path_of(Config.COL_CSV_FILE), 'rb') as csvfp:
        fieldnames = ['name', 'eng_name', 'url']
        reader = csv.DictReader(csvfp, fieldnames=fieldnames, delimiter=',',
                                quotechar='|', quoting=csv.QUOTE_MINIMAL)
        for row in reader:
            colleges.append(College(row['url'], row['name'], row['eng_name']))
        csvfp.close()
    logger.info("All %d colleges laod from to %s done" % (len(colleges), path_of(Config.COL_CSV_FILE)));


def mkdirs():
    for c in colleges:
        path = path_of(c.sname)
        logger.debug(path)
        if not os.path.isdir(path):
            os.mkdir(path)
            c.to_json_file()
        print("%s,%s,%s" % (c.name, c.eng_name, c.url))


def _init():
    # set encoding
    reload(sys)
    sys.setdefaultencoding('utf-8')

    mlog = setup_custom_logger("root")
    mlog.debug("setup logger")

    mpath = path_of('')
    if not os.path.isdir(mpath):
        os.mkdir(mpath)
        mlog.debug("mkdir %s" % mpath)

menu0 = '''
q. 退出
p. 打印所有大学名单
1. 抓取211名单到json文件
2. 从json文件导入211名单
3. 构建输出目录
4. 测试抓取院系导航目录
5. 自动猜测并分析出学校的院系导航链接
6. 抓取院系的名称和主页
'''

menu1 = """
-------------------------------------------------
q.Exit
p.Print colleges
1.Fetch colleges save to json
2.Fetch colleges from json
3.Make output dirs
4.Test Academies parser
5.Auto Fetch all academiesUrl
6.Auto Fetch Academy
7.Academy test
8.MyParser Test
-------------------------------------------------
"""

if __name__ == "__main__":
    _init()
    logger = logging.getLogger('root')

    ans = True
    while ans:
        print (menu1)
        ans = raw_input("What would you like to do? ")
        if ans == "q":
            logger.debug("\n Goodbye")
            break

        elif ans == "1":
            logger.debug("load from %s" % Config.C211_URL)
            parse_colleges()
            if not china211:
                colleges_to_csv()
                china211 = China211(Config.C211_URL, colleges)
                china211.to_json_file()
            else:
                logger.error("parsing colleges failed")
            continue
        else:
            if len(colleges) == 0:
                if not china211:
                    china211 = obj_from_file(path_of(Config.C211_FILE))
                    colleges = china211.colleges

            if ans == "2" or ans == "p":
                print_colleges()
                continue

            elif ans == "3":
                mkdirs()
                continue

            elif ans == "4":
                print_colleges()
                ans = raw_input("Which college would you like to parse? ")
                college = colleges[int(ans)]
                logger.debug("start parsing %s" % college.name)
                if college:
                    if not college.academiesUrl:
                        college.parse_aurl_auto()
                    obj_to_file(college,college.json_filename())
                continue

            elif ans == "5":
                logger.debug("auto parsing academy link...")
                for i, college in enumerate(colleges):
                    college.parse_aurl_auto()
                    obj_to_file(college,college.json_filename())
                china211.colleges = colleges
                china211.to_json_file()
                print_colleges()
                continue

            elif ans == "6" or ans == "7":
                print_colleges()
                c_ans = raw_input("Which college would you like to parse? ")
                c = colleges[int(c_ans)]
                obj = obj_from_file(c.json_filename())
                college = obj or c

                if len(college.academies) == 0:
                    if ans == "6":
                        college.parse_academies()
                        if len(college.academies) != 0:
                            obj_to_file(college,college.json_filename())
                            college.mkdirs()
                elif ans == "7":
                    a_ans = raw_input("Academy to parse? ")
                    academy = college.academies[int(a_ans)]
                    #logger.debug("start parsing %s" % academy.name)
                continue
            elif ans == "8":
                foo = imp.load_source('MyParser', '/devel/git/github/pyScripts/eduPaser/out/pku/MyParser.py')
                parser = foo.MyParser()
                parser.test()
            else:
                ans = True
                continue
# end of file