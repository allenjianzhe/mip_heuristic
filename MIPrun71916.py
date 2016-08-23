#file name netflow71816.py  based on netflow051215MIP, delete Tardiness, change 3PL to arc. 
import sys
#sys.path.append('C:/gurobi563/win32/python27/lib/gurobipy')
sys.path.append('C:/gurobi605/win32/python27/lib/gurobipy')
#sys.path.append('C:/gurobi604/win32/python27/lib/gurobipy')  # for apple
from gurobipy import *
from read71916 import *
import time   
start_time=time.clock()

from MIPfunc71916 import *
m = Model('MIP')
MIP(m,customer,C)
m.optimize()
X,y,t,TD,ending_time=m.__data
##print "\n"
print 'Basic info'
print 'customer size',len(customer)
print '\n'
for row in customer:
    print 'Customer',int(row[0])+1,'Destination ',row[1], 'quantity ',int(row[2]),'DD',int(row[3]),'penalty',int(row[4]),'Tardiness',TD[int(row[0])].x
print "\n"
####print 'Summary solution'                    
threePLCost=0
TransCost=0
TotalTransCost=0
TotalTardinessCost=0
TotalCost=0
if m.status == GRB.status.OPTIMAL:
        for row in customer:
            #print 'Customer',int(row[0]),'Tardiness',T[int(row[0])].x
            TotalTardinessCost+=TD[int(row[0])].x*int(row[4])*int(row[2])
            for n in nodes:
                if n==4:
                    continue
                else:
                    if y[int(row[0]),n].x>0:
                            print 'Customer',int(row[0])+1,'arc',n,' using 3PL','Trans_cost',F*int(row[2])
                            threePLCost+=F*int(row[2])        
TotalTransCost=0
for row in customer:
        for n in nodes:
            if n==4:
                continue
            else:
                for k in modes:
                    for s in departure:
                            if X[int(row[0]),n,k,s].x > 0:
                                    print 'Customer',int(row[0])+1,'link',n,'arc_mode_num',k,'departureTimeIndex',s,'arc_cost',f[n,k]*int(row[2]),'start_Time',dT[n,k,s],'Trans_time',tau[n,k],'t',t[int(row[0]),n].x,'real_arrive_time',dT[n,k,s]+tau[n,k]
                                    TransCost+=f[n,k]*int(row[2])
TotalTransCost=TransCost+threePLCost
TotalCost=  TotalTardinessCost+   TotalTransCost
print '\n'
print 'MIP SOLUTION 3 ARCS'

print 'Trans_Cost',TransCost
print '3PL_Cost',threePLCost
print 'Total_Trans_Cost',TotalTransCost
print 'Total_Penalty_Cost',TotalTardinessCost
print 'Total_Cost',TotalCost
print 'computer time (seconds): ',time.clock() - float(start_time)
print '\n' 
