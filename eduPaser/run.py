#!/usr/bin/python
# -*- coding: utf-8 *-*

import sys
import csv
import os
import imp
from log import *
from config import Config
from config import path_of
from mparser import Hao123_211_Parser
from mparser import get_doc_bySelenium, selenium_close
from models import College, China211
from models import obj_to_file, obj_from_file
import html2text

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
    logger.info("All %d colleges save to %s done" % (len(colleges), path_of(Config.COL_CSV_FILE)))


def csv_to_colleges():
    with open(path_of(Config.COL_CSV_FILE), 'rb') as csvfp:
        fieldnames = ['name', 'eng_name', 'url']
        reader = csv.DictReader(csvfp, fieldnames=fieldnames, delimiter=',',
                                quotechar='|', quoting=csv.QUOTE_MINIMAL)
        for row in reader:
            colleges.append(College(row['url'], row['name'], row['eng_name']))
        csvfp.close()
    logger.info("All %d colleges laod from to %s done" % (len(colleges), path_of(Config.COL_CSV_FILE)))


def _init():
    global  logger

    # set encoding
    reload(sys)
    sys.setdefaultencoding('utf-8')

    mlog = setup_custom_logger("root")
    mlog.debug("setup logger")

    mpath = path_of('')
    if not os.path.isdir(mpath):
        os.mkdir(mpath)
        mlog.debug("mkdir %s" % mpath)

    logger = logging.getLogger('root')

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
s.Save to china211
1.Fetch colleges save to json
2.Make output dirs
3.Test Academies parser
4.Auto Fetch all academiesUrl
5.Auto Fetch Academy
6.Auto Fetch Employees
7.MyParser Test
-------------------------------------------------
"""
def menu_save_china985_json():
    china211.to_json_file()


def menu_mkdirs():
    for c in colleges:
        path = path_of(c.sname)
        logger.debug(path)
        if not os.path.isdir(path):
            os.mkdir(path)
            c.to_json_file()
        print("%s,%s,%s" % (c.name, c.eng_name, c.url))


def menu_parse211():
    global china211
    parse_colleges()

    logger.debug("This operation is danger, china985.json will be overwrite with data from %s" % Config.C211_URL)
    ans = raw_input("press 'yes' to continue or ignore it: ")
    if ans != "yes":
        return

    if not china211:
        colleges_to_csv()
        china211 = China211(Config.C211_URL, colleges)
        china211.to_json_file()
    else:
        logger.warnning("parsing colleges ignored")


def menu_load211_from_json():
    global colleges
    global china211
    if len(colleges) == 0:
        if not china211:
            china211 = obj_from_file(path_of(Config.C211_FILE))
            colleges = china211.colleges


def menu_parse_academy():
    print_colleges()
    ans = raw_input("Which college would you like to parse? ")
    college = colleges[int(ans)]
    logger.debug("start parsing %s" % college.name)
    if college:
        if not college.academiesUrl:
            college.parse_aurl_auto()
        obj_to_file(college, college.json_filename())


def menu_parse_academy_url_auto():
    logger.debug("auto parsing academy link...")
    for i, college in enumerate(colleges):
        college.parse_aurl_auto()
        obj_to_file(college, college.json_filename())
    china211.colleges = colleges
    china211.to_json_file()
    print_colleges()


def menu_parse_academies():
    print_colleges()
    c_ans = raw_input("Which college would you like to parse? ")
    c = colleges[int(c_ans)]

    college = c
    if os.path.exists(c.json_filename()):
        obj = obj_from_file(c.json_filename())
        if 0 != len(obj.academies):
            college = obj

    if 0 == len(college.academies):
        college.parse_academies()
        if len(college.academies) != 0:
            obj_to_file(college, college.json_filename())
            college.mkdirs()


def menu_parse_employees():
    print_colleges()
    c_ans = raw_input("Which college would you like to parse? ")
    c = colleges[int(c_ans)]

    college = c
    if os.path.exists(c.json_filename()):
        obj = obj_from_file(c.json_filename())
        if 0 != len(obj.academies):
            college = obj

    if 0 != len(college.academies):
        college.print_academies()
        a_ans = raw_input("Academy to parse? ")
        academy = college.academies[int(a_ans)]
        academy.parse_employees(college)
        logger.debug("parsed employees count %d"%len(academy.employees))

        if academy.employees_existed(college):
            academy.employees_to_csv(college)
            academy.to_json_file(college)
        academy.print_employees()


def menu_test_imp():
    foo = imp.load_source('MyParser', '/devel/git/github/pyScripts/eduPaser/out/pku/MyParser.py')
    foo.handler()


# menus
menus = {
    "p":print_colleges,
    "s":menu_save_china985_json,
    "1":menu_parse211,
    "2":menu_mkdirs,
    "3":menu_parse_academy,
    "4":menu_parse_academy_url_auto,
    "5":menu_parse_academies,
    "6":menu_parse_employees,
    "7":menu_test_imp,
}


if __name__ == "__main__":
    _init()

    ans = True

    while ans:
        print (menu1)
        ans = raw_input("What would you like to do? ")
        if ans == "q":
            logger.debug("\n Goodbye")
            break
        else:
            if ans != "1":
                menu_load211_from_json()

            foo = menus.get(ans)
            if foo:
                foo()
            elif ans == "s":
                china211.to_json_file()
                continue

    # do something clean
    selenium_close()
    # end of file
