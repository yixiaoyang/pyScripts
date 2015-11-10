#import glob
#print glob.glob("/devel/git/github/pyScripts/*")

import os
for root, dirs, files in os.walk("/devel/git/github/pyScripts"):
    print dirs
    print files
