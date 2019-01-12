import os
import sys
import re as r
import Function_OMPi as Function

try:
    data_path=sys.argv[1]
    if os.path.isfile(data_path) and (data_path.endswith('.c') or data_path.endswith('.C')):
        Function.Trim(data_path)
    else :
        #传入的不是文件就终止程序
        print('It\'s not a file')
except:
    print('Please Import .c Code u\'d like to analyaze.\nAborted.')
