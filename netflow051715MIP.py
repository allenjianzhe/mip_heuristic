#file name 1028.py
import sys
#sys.path.append('C:/gurobi562/win64/python27/lib/gurobipy')
sys.path.append('C:/gurobi600/win32/python27/lib/gurobipy')  # for apple
from gurobipy import *
from read051715 import *
import time    
start_time=time.clock()
m = Model('MIP')
M=1000000000
F=600000
def MIP(m,customer,arc_C):
    ####################################################################################################
    #decision variable X for arc 0-1: binary variable. X[customer,i,i+1,m,k]
    X1 = {}
    for row in customer:
            for i in node:
                    if i==2:
                            continue
                    else:
                        for k in modes:
                            for s in range(len(departure)):
                                X1[int(row[0]),i-1,i,k,s]=m.addVar(obj=int(row[2])*arc_trans_cost[int(row[0]),i-1,i,k],vtype=GRB.BINARY,name='X1_%s_%s_%s_%s'%(int(row[0]),i,k,s))
    m.update()
    #decision variable X for arc 1-2: binary variable. X[customer,i,i+1,m,k]
##    X2 = {}
##    for row in customer:
##            for i in node:
##                    if i==0 or i==1:
##                            continue
##                    else:
##                        for k in modes:
##                            for s in range(len(departure)):
##                                X2[int(row[0]),i-1,i,k,s]=m.addVar(obj=arc_trans_cost[int(row[0]),i-1,i,k],vtype=GRB.BINARY,name='X2_%s_%s_%s_%s'%(int(row[0]),i,k,s))
##    m.update()
##                        
    #decision variable y: binary variable of 3PL
    y={}
    for row in customer:
        #print row
        y[int(row[0])]=m.addVar(obj=F*int(row[2]),vtype=GRB.BINARY,name='y_%s'%(int(row[0])))     
    m.update()
    #decision variable: arrive time at each node
    t={}
    for row in customer:
        for i in node:
                if i==2:        
                        continue
                else:
                        t[int(row[0]),i]=m.addVar(obj=0,vtype="C",name='nodeTime_%s_%s'%(int(row[0]),i))  
    #decision variable:Time tardiness of customer
    T={}
    for row in customer:
            T[int(row[0])]=m.addVar(obj=int(row[2])*int(row[4]),vtype="C",name='Tardiness_%s'%(int(row[0])))
    m.update()
    ####################################################################################################
    #Constraint 3.2 for each customer, only one plan can be selected
    for row in customer:
            expr = LinExpr()       
            for k in modes:
                    for s in range(len(departure)):
                            expr.addTerms(1.0,X1[int(row[0]),2,3,k,s])
            expr.add(y[int(row[0])])
            m.addConstr(expr, GRB.EQUAL, 1,name='One_%s'%(int(row[0])))
    m.update()
    ####################################################################################################
    #Constraint 3.3, in the middlepoint, In = Out
##    for row in customer:
##        expr = LinExpr()
##        expr1 = LinExpr()
##        for k in modes:
##            for s in range(len(departure)):
##                expr.addTerms(1.0,X1[int(row[0]),0,1,k,s])
##                expr1.addTerms(1.0,X2[int(row[0]),1,2,k,s])
##        m.addConstr(expr, GRB.EQUAL, expr1,name='middlePointOne_%s'%(int(row[0])))                                                              
    #constraint 3.4 arc capacity
    for k in modes:
        for s in range(len(departure)):
            for i in node:
                    if i==2:
                            continue
                    else:
                            expr = LinExpr()
                            for row in customer:
                                    expr.addTerms(int(row[2]),X1[int(row[0]),i-1,i,k,s])
                            expr.addConstant(-1*arc_C[i-1,i,k,s])
                            m.addConstr(expr,GRB.LESS_EQUAL, 0,'arcCapacity_%s_%s_%s_%s'%(int(row[0]),i,k,s))      
    m.update()
    #constraint 3.5 time constraint One
    for row in customer:        
            for i in node:
                    expr = LinExpr()                
                    if i==2:
                            continue
                    else:
                            for k in modes:
                                    for s in range(len(departure)):                                            
                                            expr.addTerms(dT[i-1,i,k,s]+trans_time[i-1,i,k],X1[int(row[0]),i-1,i,k,s])
                            expr.add(-1*y[int(row[0])]*M)
                            m.addConstr(expr,GRB.LESS_EQUAL,t[int(row[0]),i],name='timeConstr_%s_%s'%(int(row[0]),i))                            
    m.update()
    # constraint 3.6 NEW time constraint
##    for row in customer:
##        expr = LinExpr()
##        for i in node:
##            if i==2:
##                continue
##            else:
##                for k in modes:
##                    for s in range(len(departure)):
##                        if X1[int(row[0]),i-1,i,k,s]>0:
##                            expr.addTerms(dT[i-1,i,k,s],X1[int(row[0]),i-1,i,k,s])
##                            global arrive_time
##        m.addConstr(expr,GRB.GREATER_EQUAL, arrive_time[int(row[0])],name='timeConstr2_%s'%(int(row[0])))
    ###constraint 3.7 time constraint Three, tardiness time 只跟最后一个t[n,4]有关， 不用联系
    for row in customer:      
            for k in modes:
                    for s in range(len(departure)):
                            if X1[int(row[0]),2,3,k,s]>0:
                                    if t[int(row[0]),3]>int(row[3]):                                        
                                            m.addConstr(T[int(row[0])],GRB.EQUAL,t[int(row[0]),3]-int(row[3]),name='Tardiness_%s'%(int(row[0])) )
                                    else:
                                            nothing=nothing+1#这里其实什么也不需要做

    m.update()
    m.__data=X1,y,t,T
    return m
####################################################################################################
MIP(m,customer,arc_C)
m.optimize()
X1,y,t,T=m.__data
print '\n'
print "MIP model"
print "\n"
print 'Basic info'
print 'arc, 2-3'
print 'mode_1, Truck; mode_2,Rail;mode_3,HighSpeed Rail; mode_4, Air'
#print 'arc 0-1:','SC-WH ','arc 1-2:','WH-ZZ'
for row in customer:
    print 'Customer',int(row[0]),'Destination ',"SH", 'quantity ',int(row[2]),'DD',int(row[3])
print "\n"
print 'Summary solution'
threePLCost=0
TransCost=0
TotalTransCost=0
TotalTardinessCost=0
TotalCost=0
if m.status == GRB.status.OPTIMAL:
        for row in customer:
                if y[int(row[0])].x>0:
                        print 'Customer',int(row[0]),' using 3PL','Trans_cost',F*int(row[2])
                        #TotalTransCost+=F
                        threePLCost+=F*int(row[2])                                       
print '\n'
print 'Solution detail'       
for row in customer:
    for k in modes:
        for s in range(len(departure)):
            if X1[int(row[0]),2,3,k,s].x > 0:
                print 'Customer',int(row[0]),'arc',0,1,'arc_mode_num',k,'departureNum',s+1,'arc_cost',arc_trans_cost[int(row[0]),2,3,k]*int(row[2]),'start_Time',dT[2,3,k,s],'Trans_time',trans_time[2,3,k],'Ending_Time',t[int(row[0]),3].x,'Tardiness',T[int(row[0])].x
                TransCost+=arc_trans_cost[int(row[0]),2,3,k]*int(row[2])
                TotalTardinessCost+=T[int(row[0])].x*int(row[4])*int(row[2])
TotalTransCost=TransCost+threePLCost
TotalCost=  TotalTardinessCost+   TotalTransCost   
print '\n'
print 'Trans_Cost',TransCost
print '3PL_Cost',threePLCost
print 'Total_Trans_Cost',TotalTransCost
print 'Total_Penalty_Cost',TotalTardinessCost
print 'Total_Cost',TotalCost
print 'computer time (seconds): ',time.clock() - float(start_time)
print '\n'
                    
