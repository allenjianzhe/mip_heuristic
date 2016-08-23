#file name 32516H.py  based on netflow051215MIP, delete Tardiness, change 3PL to arc. 
import sys
sys.path.append('C:/gurobi604/win32/python27/lib/gurobipy')
#sys.path.append('C:/gurobi604/win32/python27/lib/gurobipy')  # for apple
from gurobipy import *
from read111115 import *

import time   
start_time=time.clock()


from Update_UpperBound import execute

print 
