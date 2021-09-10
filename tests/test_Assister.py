import os,sys,inspect
#sys.path.insert(0, os.path.realpath(os.path.pardir))
print((os.path.pardir))


currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir) 

print(currentdir)
import re
#from Assister import MainProgram
#
#
#help(MainProgram)
#

X = 'Grand total: $10.68'
y = float(re.findall("\d+\.\d+", X)[0])
print(y)