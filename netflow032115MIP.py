#file name netflow032115MIP.py based on netflow0814MIP
# change two kind of X, X2='C', X1=binary
import sys
sys.path.append('C:/gurobi600/win32/python27/lib/gurobipy')  # for apple
#sys.path.append('C:/gurobi562/win64/python27/lib/gurobipy')

from gurobipy import *
from read0916 import *
import time


    
start_time=time.clock()
m = Model('MIP')
M=1000000000
F=10000000
def MIP(m,customer,arc_C):
    ####################################################################################################
    #decision variable X: binary variable. X[customer,i,i+1,m,k]
    X1 = {}
    for row in customer:
            for i in node:
                    if i==0 or i==1:
                            continue
                    else:
                        for k in modes:
                            for s in range(len(departure)):
                                X1[int(row[0]),i-1,i,k,s]=m.addVar(obj=arc_trans_cost[int(row[0]),i-1,i,k],vtype=GRB.BINARY,name='X_%s_%s_%s_%s'%(int(row[0]),i,k,s))
    m.update()
    X2 = {}
    for row in customer: 
            for k in modes:
                for s in range(len(departure)):
                    X2[int(row[0]),0,1,k,s]=m.addVar(obj=arc_trans_cost[int(row[0]),0,1,k],vtype='C',name='X_%s_%s_%s'%(int(row[0]),k,s))
    m.update()
                        
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
    #Constraint 3.2 for each customer, only one plan can be selected
    for row in customer:
            expr = LinExpr()       
            for k in modes:
                    for s in range(len(departure)):
                            expr.addTerms(1.0,X2[int(row[0]),0,1,k,s])
            expr.add(y[int(row[0])])
            m.addConstr(expr, GRB.EQUAL, 1,name='One_%s'%(int(row[0])))
    m.update()
    ####################################################################################################
    #Constraint 3.3, in the middlepoint, In = Out
    for row in customer:
        for i in node:
                if i==0 or i==4 or i==1:
                        continue
                else:
                        expr = LinExpr()
                        expr1 = LinExpr()
                        for k in modes:
                                for s in range(len(departure)):
                                        expr.addTerms(1.0,X1[int(row[0]),i-1,i,k,s])
                                        expr1.addTerms(1.0,X1[int(row[0]),i,i+1,k,s])
                        m.addConstr(expr, GRB.EQUAL, expr1,name='middlePointOne_%s'%(int(row[0])))
    for row in customer:
        expr = LinExpr()
        expr1 = LinExpr()
        for k in modes:
                for s in range(len(departure)):
                        expr.addTerms(1.0,X2[int(row[0]),0,1,k,s])
                        expr1.addTerms(1.0,X1[int(row[0]),1,2,k,s])
        m.addConstr(expr, GRB.EQUAL, expr1,name='middlePointOne_%s'%(int(row[0])))
    #constraint 3.4 arc capacity
    for k in modes:
        for s in range(len(departure)):
            for i in node:
                    if i==4 or i==0:
                            continue
                    else:
                            expr = LinExpr()
                            for row in customer:
                                    expr.addTerms(int(row[2]),X1[int(row[0]),i,i+1,k,s])
                            expr.addConstant(-1*arc_C[i,i+1,k,s])
                            m.addConstr(expr,GRB.LESS_EQUAL, 0,'arcCapacity_%s_%s_%s_%s'%(int(row[0]),i,k,s))      
    m.update()
    for k in modes:
        for s in range(len(departure)):
            expr = LinExpr()
            for row in customer:
                    expr.addTerms(int(row[2]),X2[int(row[0]),0,1,k,s])
            expr.addConstant(-1*arc_C[0,1,k,s])
            m.addConstr(expr,GRB.LESS_EQUAL, 0,'arcCapacity_%s_%s_%s'%(int(row[0]),k,s))      
    m.update()
    #constraint 3.5 time constraint One
    for row in customer:        
            for i in node:
                    expr = LinExpr()                
                    if i==0 or i==1:
                            continue
                    else:
                            for k in modes:
                                    for s in range(len(departure)):                                            
                                            expr.addTerms(dT[i-1,i,k,s]+trans_time[i-1,i,k],X1[int(row[0]),i-1,i,k,s])
                            expr.add(-1*y[int(row[0])]*M)
                            m.addConstr(expr,GRB.LESS_EQUAL,t[int(row[0]),i],name='timeConstr_%s_%s'%(int(row[0]),i))                        
    m.update()
    for row in customer:
        expr = LinExpr()                
        for k in modes:
                for s in range(len(departure)):                                            
                        expr.addTerms(dT[0,1,k,s]+trans_time[0,1,k],X2[int(row[0]),0,1,k,s])
        expr.add(-1*y[int(row[0])]*M)
        m.addConstr(expr,GRB.LESS_EQUAL,t[int(row[0]),1],name='timeConstr_%s'%(int(row[0])))
    m.update()
    #constraint 3.6 time constraint Two, 新一期的出发时间大于上一期的到达时间
    for row in customer:        
            for i in node:                    
                    expr1 = LinExpr()
                    if i==0 or i==4:
                            continue
                    else:
                            for k in modes:
                                    for s in range(len(departure)):                                            
                                            expr1.addTerms(dT[i,i+1,k,s],X1[int(row[0]),i,i+1,k,s])                          
                            m.addConstr(expr1,GRB.GREATER_EQUAL,t[int(row[0]),i],name='timeConstr_%s_%s'%(int(row[0]),i))

    m.update()
    nothing=0
    ###constraint 3.7 time constraint Three, tardiness time 只跟最后一个t[n,4]有关， 不用联系
    for row in customer:      
            for k in modes:
                    for s in range(len(departure)):
                            if X1[int(row[0]),3,4,k,s]>0 and t[int(row[0]),4]>int(row[3]):                              
                                m.addConstr(T[int(row[0])],GRB.EQUAL,t[int(row[0]),4]-int(row[3]),name='Tardiness_%s'%(int(row[0])) )


    m.update()
    m.__data=X1,X2,y,t,T
    return m


####################################################################################################


MIP(m,customer,arc_C)
m.optimize()
X1,X2,y,t,T=m.__data



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
##                    print t[int(row[0]),i].x

#print t[0,4]
TotalTransCost=0
print 'Summary solution'
TotalTardinessCost=0
if m.status == GRB.status.OPTIMAL:
        for row in customer:
                if y[int(row[0])].x>0:
                        print 'Customer',int(row[0]),' using 3PL','Trans_cost',F
                        #print '\n'
                for k in modes:
                        for s in range(len(departure)):
                                if X2[int(row[0]),0,1,k,s].x > 0:
                                    print 'Customer',int(row[0]),'start_Time',dT[0,1,k,s],'Ending_time',t[int(row[0]),4].x,'Tardiness',T[int(row[0])].x
                                    TotalTardinessCost+=T[int(row[0])].x*int(row[4])
                                    TotalTransCost+=arc_trans_cost[int(row[0]),0,1,k]
                                       
print '\n'
print 'Solution detail'        

for row in customer:
    for k in modes:
        for s in range(len(departure)):
                if X2[int(row[0]),0,1,k,s].x > 0:
                    print 'Customer',int(row[0]),'arc 0-1','arc_mode_num',k,'departureNum',s+1,'X2',X2[int(row[0]),0,1,k,s].x
print '\n'
for row in customer:
    for i in node:
        if i==4 or i==0:
                continue
        else:
             for k in modes:
                    for s in range(len(departure)):
                            if X1[int(row[0]),i,i+1,k,s].x > 0:
                                print 'Customer',int(row[0]),'arc',i,i+1,'arc_mode_num',k,'departureNum',s+1,'arc_cost',arc_trans_cost[int(row[0]),i,i+1,k],'start_Time',dT[i,i+1,k,s],'Trans_time',trans_time[i,i+1,k],'Ending_Time',t[int(row[0]),i+1].x
                                TotalTransCost+=arc_trans_cost[int(row[0]),i,i+1,k]
                                
                                    
print '\n'
print 'Total_Trans_Cost',TotalTransCost
print 'Total_Penalty_Cost',TotalTardinessCost                    
print 'computer time (seconds): ',time.clock() - float(start_time)
print '\n'
                    
