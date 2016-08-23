#file name netflow052415MIP.py  based on netflow051315MIP
import sys
sys.path.append('C:/gurobi604/win32/python27/lib/gurobipy')  # for apple
#sys.path.append('C:/gurobi562/win64/python27/lib/gurobipy')
from gurobipy import *
##from read052415 import *
from read10616 import *
import time   
start_time=time.clock()
m = Model('MIP')
M=1000000000
F=600000
ending_time={}
def MIP(m,customer,arc_C):
    ####################################################################################################
    #decision variable X: binary variable. X[customer,i,i+1,m,k]
    X = {}
    for row in customer:
        for i in nodes:
            if i == 3:
                continue
            else:
                for k in modes:
                    for s in departure:
                        X[int(row[0]),i,k,s]=m.addVar(obj=int(row[2])*arc_trans_cost[int(row[0]),i,k],vtype=GRB.BINARY,name='X_%s_%s_%s_%s'%(int(row[0]),i,k,s))
    m.update()                                        
    #decision variable y: binary variable of 3PL
    y={}
    for row in customer:
        for i in nodes:
            y[int(row[0]),i]=m.addVar(obj=int(row[2])*F,vtype=GRB.BINARY,name='y_%s_%s'%(int(row[0]),i))     
    m.update()
    #decision variable: arrive time at each node
    t={}
    for row in customer:
        for i in nodes:
            t[int(row[0]),i]=m.addVar(obj=0,vtype='C',name='nodeTime_%s_%s'%(int(row[0]),i))  
    #decision variable:Time tardiness of customer
    T={}
    for row in customer:
            T[int(row[0])]=m.addVar(obj=int(row[2])*int(row[4]),vtype='C',name='Tardiness_%s'%(int(row[0])))
    m.update()
    ####################################################################################################
    #Constraint 3.2 for each customer, each link, only one plan can be selected
    for row in customer:
        for i in nodes:
            if i==3:
                continue
            else:
                expr = LinExpr()       
                for k in modes:
                        for s in departure:
                                expr.addTerms(1.0,X[int(row[0]),i,k,s])
                expr.add(y[int(row[0]),i])
                m.addConstr(expr, GRB.EQUAL, 1,name='One_%s_%s_%s_%s'%(int(row[0]),i,k,s))
    m.update()
    ####################################################################################################
    #Constraint binarty of 3PL
    for row in customer:
        for i in nodes:
            if i==3 or i==1:
                continue
            else:
                m.addConstr(y[int(row[0]),i-1],GRB.LESS_EQUAL,y[int(row[0]),i],name='one3pl_%s_%s'%(int(row[0]),i))
    
    #constraint 3.4 arc capacity
    for k in modes:
        for s in departure:
            for i in nodes:
                if i==3:
                    continue
                else:
                    expr = LinExpr()
                    for row in customer:
                            expr.addTerms(int(row[2]),X[int(row[0]),i,k,s])
                    expr.addConstant(-1*arc_C[i,k,s])
                    m.addConstr(expr,GRB.LESS_EQUAL, 0,'arcCapacity_%s_%s_%s_%s'%(int(row[0]),i,k,s))      
    m.update()                                          
    #constraint 3.5 time constraint One
    for row in customer:        
            for i in nodes:
                if i==3:
                    continue
                else:
                    expr = LinExpr()                
                    for k in modes:
                            for s in departure:                                            
                                    expr.addTerms(dT[i,k,s]+trans_time[i,k],X[int(row[0]),i,k,s])
                    expr.add(-1*y[int(row[0]),i]*M)
                    m.addConstr(expr,GRB.LESS_EQUAL,t[int(row[0]),i],name='timeConstr1_%s_%s'%(int(row[0]),i))                        
    m.update()                    
    #constraint 3.6 time constraint Two, 新一期的出发时间大于上一期的到达时间
    for row in customer:
        expr1 = LinExpr()
        for k in modes:
                for s in departure:                                            
                        expr1.addTerms(dT[2,k,s],X[int(row[0]),2,k,s])
        expr1.add(y[int(row[0]),i]*M) #???????????????????????
        m.addConstr(expr1,GRB.GREATER_EQUAL,t[int(row[0]),1],name='timeConstr2_%s_%s'%(int(row[0]),i))
    m.update()
    #definition of T
    global ending_time
    for row in customer:
        for k in modes:
            for s in departure:
                if X[int(row[0]),2,k,s]>0:
                    ending_time[int(row[0])]=(dT[1,k,s]+trans_time[2,k])*X[int(row[0]),1,k,s]
                    if t[int(row[0]),2]>DD[int(row[0])]:
                        m.addConstr(T[int(row[0])],GRB.EQUAL,t[int(row[0]),2]-DD[int(row[0])],name='Tardiness_%s'%(int(row[0])) )
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
    print 'Customer',int(row[0]), 'quantity ',int(row[2]),'DD',DD[int(row[0])]
print "\n"
print 'Summary solution'
threePLCost=0
TransCost=0
TotalTransCost=0
TotalTardinessCost=0
TotalCost=0
if m.status == GRB.status.OPTIMAL:
        for row in customer:
            print 'Customer',int(row[0]),'Tardiness',T[int(row[0])].x
            TotalTardinessCost+=T[int(row[0])].x*int(row[4])*int(row[2])
            for i in nodes:
                if y[int(row[0]),i].x>0:
                        print 'Customer',int(row[0]),'arc',i,' using 3PL','Trans_cost',F*int(row[2])
                        threePLCost+=F*int(row[2])        
TotalTransCost=0
for row in customer:
        for i in nodes:
            if i==3:
                continue
            else:
                for k in modes:
                    for s in departure:
                            if X[int(row[0]),i,k,s].x > 0:
                                    print 'Customer',int(row[0])+1,'link',i,'arc_mode_num',k,'departureTimeIndex',s,'arc_cost',arc_trans_cost[int(row[0]),i,k]*int(row[2]),'start_Time',dT[i,k,s],'Trans_time',trans_time[i,k],'t',t[int(row[0]),i].x,'real_arrive_time',dT[i,k,s]+trans_time[i,k]
                                    TransCost+=arc_trans_cost[int(row[0]),i,k]*int(row[2])
TotalTransCost=TransCost+threePLCost
TotalCost=  TotalTardinessCost+   TotalTransCost
print '\n'
print 'MIP SOLUTION 2 ARCS'
print 'customer size',len(customer)
print 'Trans_Cost',TransCost
print '3PL_Cost',threePLCost
print 'Total_Trans_Cost',TotalTransCost
print 'Total_Penalty_Cost',TotalTardinessCost
print 'Total_Cost',TotalCost
print 'computer time (seconds): ',time.clock() - float(start_time)
print '\n'                   
