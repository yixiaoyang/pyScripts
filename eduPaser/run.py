#!/usr/bin/python
# -*- coding: utf-8 *-*

import sys
from log import *
from config import *
from models import *

logger = None
china211 = None

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


if __name__ == "__main__":
    _init()
    logger = logging.getLogger('root')

    ans = True
    while ans:
        print ("""
-------------------------------------------------
q.Exit
1.Fetch colleges save to csv
2.Fetch colleges from csv
3.Make output dirs
4.Test Academies parser
5.Auto Fetch all academiesUrl
6.Auto Fetch Academy
-------------------------------------------------
""")
        ans = raw_input("What would you like to do? ")
        if ans == "q":
            logger.debug("\n Goodbye")
            break
        elif ans == "1":
            logger.debug("load from %s" % Config.c211_url)
            if not china211:
                china211 = China211(Config.c211_url)
            china211.parse_colleges()
            if china211.colleges:
                china211.colleges_to_csv()
                obj_to_file(china211, path_of(Config.c211_file))
            else:
                logger.error("china211 parsing colleges failed")
        elif ans == "2":
            china211 = China211(Config.c211_url)
            china211.csv_to_colleges()
            china211.printColleges()
        elif ans == "3":
            if not china211:
                china211 = obj_from_file(path_of(Config.c211_file))
            china211.mkdirs()
        elif ans == "4":
            if not china211:
                china211 = obj_from_file(path_of(Config.c211_file))
                logger.debug("china211(%d colleges) load from json done" % (len(china211.colleges)))
            
            china211.printColleges()
            ans = raw_input("Which college would you like to parse? ")
            college = china211.colleges[int(ans)]
            logger.debug("start parsing %s"%college.name)
            
            if college:
                if not college.academiesUrl:
                    college.parse_aurl_auto()
                path = path_of("%s/%s.json" % (college.name, college.eng_name))
                obj_to_file(college, path)
                # break
        elif ans == "5":
            if not china211:
                china211 = obj_from_file(path_of(Config.c211_file))
                logger.debug("china211(%d colleges) load from json done" % (len(china211.colleges)))
            logger.debug("auto parsing academy link...")
            for i,college in enumerate(china211.colleges):
                college.parse_aurl_auto()
                path = path_of("%s/%s.json" % (college.name, college.eng_name))
                obj_to_file(college, path)
                #if i > 20:
                #    break;
            obj_to_file(china211, path_of(Config.c211_file))
            china211.printColleges()
            break;
        elif ans == "6":
            if not china211:
                china211 = obj_from_file(path_of(Config.c211_file))
                logger.debug("china211(%d colleges) load from json done" % (len(china211.colleges)))
            
            china211.printColleges()
            ans = raw_input("Which college would you like to parse? ")
            college = china211.colleges[int(ans)]

            if len(college.academiesUrl) != 0:
                if len(college.academies) != 0:
                    college.print_academies()
                    ans = raw_input("academy to parse? ")
                    academy = college.academies[int(ans)]
                    logger.debug("start parsing %s"%academy.name)
                else:
                    logger.debug("no academies parsed")
        else:
            ans = True
