#file name netflow0904MIP.py 
#把arc 拆开看成独立的cus, 4 arcs. 
import sys
sys.path.append('C:/gurobi600/win32/python27/lib/gurobipy')  # for apple
#sys.path.append('C:/gurobi562/win64/python27/lib/gurobipy')

from gurobipy import *
from read0804 import *
import time
    
start_time=time.clock()
m = Model('MIP')
M=10000000000
F=10000000
def MIP(m,customer,arc_C):
    ####################################################################################################
    #decision variable X: binary variable. X[customer,i,i+1,m,k]
    X = {}
    for row in customer:
            for i in node:
                    if i==0:
                            continue
                    else:
                        for k in modes:
                            for s in range(len(departure)):
                                X[int(row[0]),i-1,i,k,s]=m.addVar(obj=arc_trans_cost[int(row[0]),i-1,i,k],vtype=GRB.BINARY,name='X_%s_%s_%s_%s'%(int(row[0]),i,k,s))
    m.update()                
                        
    #decision variable y: binary variable of 3PL
    y={}
    for row in customer:
            for i in node:
                    if i==0:
                            continue
                    else:
                        y[int(row[0]),i-1,i]=m.addVar(obj=F,vtype=GRB.BINARY,name='y_%s'%(int(row[0])))         
    m.update()
    #decision variable: arrive time at each node
    t={}
    for row in customer:
        for i in node:
                if i==0:        
                        continue
                else:
                        t[int(row[0]),i]=m.addVar(obj=0,vtype="C",name='nodeTime_%s_%s'%(int(row[0]),i))  
    #decision variable:Time tardiness of customer
    T={}
    for row in customer:
            T[int(row[0])]=m.addVar(obj=int(row[4]),vtype="C",name='Tardiness_%s'%(int(row[0])))
    m.update()
    ####################################################################################################
    #Constraint 3.2 for each arc, only one mode can be selected
    for row in customer:
        for i in node:
            if i==0:
                continue
            else:
                expr = LinExpr()       
                for k in modes:
                        for s in range(len(departure)):
                                expr.addTerms(1.0,X[int(row[0]),i-1,i,k,s])
                expr.add(y[int(row[0]),i-1,i])
                m.addConstr(expr, GRB.EQUAL, 1,name='One_%s'%(int(row[0])))
    m.update()
    ####################################################################################################
    #Constraint 3.3, in the middlepoint, In = Out
    for row in customer:
        for i in node:
                if i==0 or i==4:
                        continue
                else:
                        expr = LinExpr()
                        expr1 = LinExpr()
                        for k in modes:
                                for s in range(len(departure)):
                                        expr.addTerms(1.0,X[int(row[0]),i-1,i,k,s])
                                        expr.addTerms(1.0,y[int(row[0]),i-1,i])
                                        expr1.addTerms(1.0,X[int(row[0]),i,i+1,k,s])
                                        expr1.addTerms(1.0,y[int(row[0]),i,i+1])
                        m.addConstr(expr, GRB.EQUAL, expr1,name='middlePointOne_%s'%(int(row[0])))                                                              
    #constraint 3.4 arc capacity
    for k in modes:
        for s in range(len(departure)):
            for i in node:
                    if i==4:
                            continue
                    else:
                            expr = LinExpr()
                            for row in customer:
                                    expr.addTerms(int(row[2]),X[int(row[0]),i,i+1,k,s])
                            expr.addConstant(-1*arc_C[i,i+1,k,s])
                            m.addConstr(expr,GRB.LESS_EQUAL, 0,'arcCapacity_%s_%s_%s_%s'%(int(row[0]),i,k,s))      
    m.update()                                          
    #constraint 3.5 time constraint One,出发+运输时间<=到达时间
    for row in customer:        
            for i in node:
                    expr = LinExpr()                
                    if i==0:
                            continue
                    else:
                            for k in modes:
                                    for s in range(len(departure)):                                            
                                            expr.addTerms(dT[i-1,i,k,s]+trans_time[i-1,i,k],X[int(row[0]),i-1,i,k,s])
                            expr.add(y[int(row[0]),i-1,i]*trans_time_y[i-1,i])
                            m.addConstr(expr,GRB.LESS_EQUAL,t[int(row[0]),i],name='timeConstrOne_%s_%s'%(int(row[0]),i))                        
    m.update()                    
    #constraint 3.8 time constraint Two, 新一期的出发时间大于上一期的到达时间
    for row in customer:        
        for i in node:
                expr = LinExpr()                
                if i==0 or i==4:
                        continue
                else:
                        for k in modes:
                                for s in range(len(departure)):                                            
                                        expr.addTerms(dT[i,i+1,k,s]+trans_time[i,i+1,k],X[int(row[0]),i,i+1,k,s])
                        expr.add(y[int(row[0]),i,i+1]*trans_time_y[i,i+1])
                        m.addConstr(expr,GRB.GREATER_EQUAL,t[int(row[0]),i],name='timeConstrTwo_%s_%s'%(int(row[0]),i))
    m.update()  
    ###constraint 3.9 time constraint five, tardiness time 只跟最后一个t[n,4]有关， 不用联系
    nothing=0
    for row in customer:      
            for k in modes:
                    for s in range(len(departure)):
                            if X[int(row[0]),3,4,k,s]>0:
                                    if t[int(row[0]),4]>int(row[3]):                                        
                                            m.addConstr(T[int(row[0])],GRB.EQUAL,t[int(row[0]),4]-int(row[3]),name='Tardiness_%s'%(int(row[0])) )
                                    else:
                                            nothing=nothing+1#这里其实什么也不需要做
    m.update()
    m.__data=X,y,t,T
    return m


####################################################################################################


MIP(m,customer,arc_C)
m.optimize()
X,y,t,T=m.__data



print "\n"
print 'Basic info'
for row in customer:
    print 'Customer',int(row[0]),'Destination ',row[1], 'quantity ',int(row[2]),'DD',int(row[3])
print "\n"
##for row in customer:
##        for i in node:
##                if i==0:        
##                        continue
##                else:
##                    print t[int(row[0]),i]

#print 'Summary solution'
TotalTardinessCost=0
TotalTransCost=0
if m.status == GRB.status.OPTIMAL:
        for row in customer:
            print 'Customer',int(row[0]),'Tardiness',T[int(row[0])].x
            TotalTardinessCost+=T[int(row[0])].x*int(row[4])
            for i in node:                
                if i==0:
                    continue
                else:
                    if y[int(row[0]),i-1,i].x>0:
                            print 'node',i-1,i,' using 3PL','Trans_cost',F
                            TotalTransCost+=F
                    for k in modes:
                            for s in range(len(departure)):
                                    if X[int(row[0]),i-1,i,k,s].x > 0:
                                            print 'arc',i-1,i,'m',k,'s',s+1,'arc_cost',arc_trans_cost[int(row[0]),i-1,i,k],'Depart_time',dT[i-1,i,k,s],'Trans_time',trans_time[i-1,i,k],'Arrived_time',t[int(row[0]),i].x
                                            TotalTransCost+=arc_trans_cost[int(row[0]),i-1,i,k]
print '\n'
print 'Total_Trans_Cost',TotalTransCost
print 'Total_Penalty_Cost',TotalTardinessCost                    
print 'computer time (seconds): ',time.clock() - float(start_time)

                    
