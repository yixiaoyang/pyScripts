# coding=utf-8

from os import listdir
from os.path import isfile, join, splitext

from ImageMagic_sh import image_quality


srcPath = '/run/media/yixiaoyang/3733-6430/DCIM/100D5200/'
dstath = '/home/yixiaoyang/images/Yunnan-SD2/'
extSet = set(['.jpg'])
files = []

for f in listdir(srcPath):
    absFilename = srcPath + f
    # Warning: use absolute path or it return False
    if isfile(absFilename):
        name,ext = splitext(f)
        if ext.lower() in extSet:
            files.append(f)

for count,f in enumerate(files):
    ifile = srcPath + f
    ofile = dstath + f
    image_quality(ifile, ofile)
    print("[%04d] %s => %s"%(count, ifile, ofile))

print("Done!")