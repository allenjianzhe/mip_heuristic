#main model
#file name main.py
import sys
#sys.path.append('C:/gurobi562/win64/python27/lib/gurobipy')
sys.path.append('C:/gurobi604/win32/python27/lib/gurobipy')  # for apple
from gurobipy import *
import time
from model1 import *
y={}
for row in customer:
    for i in nodes:
        if i==2:
            continue
        else:
            y[int(row[0]),i]=0
start_time=time.clock()
MIP1(m,customer,arc_C)
m.optimize()
X,y,t,T=m.__data
threePLCost1=0
TransCost1=0
TotalTransCost1=0
TotalTardinessCost1=0
TotalCost1=0
arrive_time={}
if m.status == GRB.status.OPTIMAL:
        for row in customer:
            for i in nodes:
                if i==2:
                    continue
                else:
                    if y[int(row[0]),i].x>0:
                            print 'Customer',int(row[0])+1,'arc',i,' using 3PL','Trans_cost',F*int(row[2])
                            threePLCost1+=F*int(row[2])
                            global arrive_time
                            arrive_time[int(row[0])]=0       
TotalTransCost1=0
for row in customer:
        for i in nodes:
            if i==2:
                continue
            else:
                for k in modes:
                    for s in departure:
                            if X[int(row[0]),i,k,s].x > 0:
                                    print 'Customer',int(row[0])+1,'link',i,'arc_mode_num',k,'departureTimeIndex',s,'arc_cost',arc_trans_cost[int(row[0]),i,k]*int(row[2]),'start_Time',dT[i,k,s],'Trans_time',trans_time[i,k],'t',t[int(row[0]),i].x,'real_arrive_time',dT[i,k,s]+trans_time[i,k]
                                    TransCost1+=arc_trans_cost[int(row[0]),i,k]*int(row[2])
                                    global arrive_time
                                    arrive_time[int(row[0])]=dT[1,k,s]+trans_time[1,k]
TotalTransCost1=TransCost1+threePLCost1
TotalCost1=  TotalTardinessCost1+   TotalTransCost1

from model2 import *
MIP2(m2,customer,arc_C)
m2.optimize()
X2,y2,t,T=m2.__data
threePLCost2=0
TransCost2=0
TotalTransCost2=0
TotalTardinessCost2=0
TotalCost2=0
if m2.status == GRB.status.OPTIMAL:
        for row in customer:
            TotalTardinessCost2+=T[int(row[0])].x*int(row[4])*int(row[2])
            for i in nodes:
                if i==3:
                    continue
                else:
                    if y2[int(row[0]),i].x>0:
                            print 'Customer',int(row[0])+1,' using 3PL','Trans_cost',F*int(row[2])
                            threePLCost2+=F*int(row[2])
for row in customer:
        for i in nodes:
            if i==3:
                continue
            else:
                for k in modes:
                    for s in departure:
                            if X2[int(row[0]),i,k,s].x > 0:
                                    print 'Customer',int(row[0])+1,'link',i,'arc_mode_num',k,'departureTimeIndex',s,'arc_cost',arc_trans_cost[int(row[0]),i,k]*int(row[2]),'start_Time',dT[i,k,s],'Trans_time',trans_time[i,k],'t',t[int(row[0]),i].x,'real arrive_time',dT[i,k,s]+trans_time[i,k]
                                    TransCost2+=arc_trans_cost[int(row[0]),i,k]*int(row[2])
    ##        print '\n'
TotalTransCost2=TransCost2+threePLCost2
TotalCost2=  TotalTardinessCost2+   TotalTransCost2
print '\n'
print 'Trans_Cost1',TransCost1
print '3PL_Cost1',threePLCost1
print 'Trans_Cost1',TransCost1
print 'Total_Trans_Cost1',TotalTransCost1
print 'Total_Penalty_Cost1',TotalTardinessCost1
print 'Total_Cost1',TotalCost1
print '\n'
print 'Trans_Cost2',TransCost2
print '3PL_Cost2',threePLCost2
print 'Trans_Cost',TransCost2
print 'Total_Trans_Cost2',TotalTransCost2
print 'Total_Penalty_Cost2',TotalTardinessCost2
print 'Total_Cost2',TotalCost2
print '\n'
print 'H SOLUTION 2 ARCS'
print 'customer size',len(customer)
print '3PL_Cost',threePLCost2+threePLCost1
print 'Trans_Cost',TransCost2+TransCost1
print 'Total_Trans_Cost',TotalTransCost1+TotalTransCost2
print 'Total_Penalty_Cost',TotalTardinessCost2
print 'Total_Cost',TotalCost1+TotalCost2
print 'computer time (seconds): ',time.clock() - float(start_time)
print '\n' 
