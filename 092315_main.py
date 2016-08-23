#name 092315_main
import sys
sys.path.append('C:/gurobi604/win32/python27/lib/gurobipy')
from gurobipy import *
import time
from start_file import *


start_time=time.clock()
m = Model('MIP')
M=1000000000
#fix cost of 3pl
F=600000
# set of routes
nodes=[1,2,3,4]
#departure time
departure=[1,2,3,4,5,6] 
#modes = ['T','R','H','A']
modes=[1,2,3,4]

arc_C={}
arc_C=getArcC(nodes,modes,departure)
Distance={}
Distance=getDistance()
trans_time={}
trans_time=getTransTime(nodes,modes,getDistance())
arc_trans_cost={}
arc_trans_cost=getArcTransCost(customer,nodes,modes,getDistance())
dT={}
dT=getdT()

##pi1={}
##for i in nodes:
##    if i==4:
##        continue
##    else:
##        for k in modes:
##            for s in departure:
##                pi1[i,k,s]=0
##pi2={}
##for i in nodes:
##    if i==4:
##        continue
##    else:
##        for k in modes:
##            for s in departure:
##                pi2[i,k,s]=0
def MIP(m,customer,arc_C,nodes,modes,departure):
    #decision variable X: binary variable. X[customer,i,i+1,m,k]
    X = {}
    for row in customer:
        for i in nodes:
            if i==4:
                continue
            else:
                for k in modes:
                    for s in departure:
                        #print row[0]
                        X[int(row[0]),i,k,s]=m.addVar(vtype=GRB.BINARY,name='X_%s_%s_%s_%s'%(int(row[0]),i,k,s))
    m.update()
    #decision variable pi,continue
    pi={}
    for k in modes:
        for s in departure:
            for i in nodes:
                if i==4:
                    continue
                else:
                    pi[i,k,s]=m.addVar(vtype='C',lb=0.5, ub=0.5,name='pi_%s_%s_%s'%(i,k,s))
    m.update()
##    for k in modes:
##        for s in departure:
##            for i in nodes:
##                a=LinExpr()
##                if i==4:
##                    continue
##                else:
##                    for row in customer:
##                            a.addTerms(int(row[2]),X[int(row[0]),i,k,s])
##                    a.addConstant(-arc_C[i,k,s])
##                pi[i,k,s]=m.addVar(obj=a,vtype='C',name='pi_%s_%s_%s'%(i,k,s))    
##    m.update()
    #decision variable y: binary variable of 3PL
    y={}
    for row in customer:
        for i in nodes:
            if i==4:
                continue
            else:
                y[int(row[0]),i]=m.addVar(vtype=GRB.BINARY,name='y_%s_%s'%(int(row[0]),i))     
    m.update()
##    y={}
##    for row in customer:
##        for i in nodes:
##            if i==4:
##                continue
##            else:
##                y[int(row[0]),i]=m.addVar(obj=int(row[2])*F,vtype=GRB.BINARY,name='y_%s_%s'%(int(row[0]),i))     
##    m.update()
    #decision variable: arrive time at each node
    t={}
    for row in customer:
        for i in nodes:
            if i==4:
                continue
            else:
                t[int(row[0]),i]=m.addVar(vtype='C',name='nodeTime_%s_%s'%(int(row[0]),i))
    #decision variable: T, continue
    T={}
    for row in customer:
            T[int(row[0])]=m.addVar(obj=int(row[2])*int(row[4]),vtype='C',name='Tardiness_%s'%(int(row[0])))
    m.update()
##    T={}
##    for row in customer:
##            T[int(row[0])]=m.addVar(obj=int(row[2])*int(row[4]),vtype='C',name='Tardiness_%s'%(int(row[0])))
##    m.update()
    ############################################### set Objective
    #set X
    expr1=QuadExpr()
    for row in customer:
        for i in nodes:
            if i==4:
                continue
            else:
                for k in modes:
                    for s in departure:
                        expr1=expr1+int(row[2])*arc_trans_cost[int(row[0]),i,k]*X[int(row[0]),i,k,s]
    m.update()
    m.setObjective(expr1)
    # set pi
    expr2=QuadExpr()
    for k in modes:
        for s in departure:
            for i in nodes:
                a=LinExpr()
                if i==4:
                    continue
                else:
                    for row in customer:
                            a.addTerms(int(row[2]),X[int(row[0]),i,k,s])
                    a.addConstant(-arc_C[i,k,s])
                    expr2=expr2-a*pi[i,k,s]# be careful, + or -, which one is correct?
    m.update()
    m.setObjective(expr2)
    # set y
    expr3=QuadExpr()
    for row in customer:
        for i in nodes:
            if i==4:
                continue
            else:
                expr3=expr3+y[int(row[0]),i]*int(row[2])*F   
    m.update()
    m.setObjective(expr3)
    #set T
    expr4=QuadExpr()
    for row in customer:
        expr4=expr4+int(row[2])*int(row[4])*T[int(row[0])]
    m.update()
    m.setObjective(expr4)

    #Constraint 3.2 for each customer, each link, only one plan can be selected
    for row in customer:
        for i in nodes:
            if i==4:
                continue
            else:
                expr = LinExpr()       
                for k in modes:
                        for s in departure:
                                expr.addTerms(1.0,X[int(row[0]),i,k,s])
                expr.add(y[int(row[0]),i])
                m.addConstr(expr, GRB.EQUAL, 1,name='One_%s_%s_%s_%s'%(int(row[0]),i,k,s))
    m.update()
    #Constraint binarty of 3PL
    for row in customer:
        for i in nodes:
            if i==1 or i==4:
                continue
            else:
                m.addConstr(y[int(row[0]),i-1],GRB.LESS_EQUAL,y[int(row[0]),i],name='one3pl_%s_%s'%(int(row[0]),i))
    #constraint 3.4 arc capacity
    for k in modes:
        for s in departure:
            for i in nodes:
                if i==4:
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
                if i==4:
                    continue
                else: 
                    expr = LinExpr()                
                    for k in modes:
                            for s in departure:                                            
                                    expr.addTerms(dT[i,k,s]+trans_time[i,k],X[int(row[0]),i,k,s])
                    expr.add(-1*y[int(row[0]),i]*M)
                    m.addConstr(expr,GRB.LESS_EQUAL,t[int(row[0]),i],name='timeConstr1_%s_%s'%(int(row[0]),i))                        
    m.update()                    

    for row in customer:        
            for i in nodes:                    
                    expr1 = LinExpr()
                    if i==1 or i==4:
                            continue
                    else:
                            for k in modes:
                                    for s in departure:                                            
                                            expr1.addTerms(dT[i,k,s],X[int(row[0]),i,k,s])
                            expr1.add(y[int(row[0]),i])
                            m.addConstr(expr1,GRB.GREATER_EQUAL,t[int(row[0]),i-1],name='timeConstr2_%s_%s'%(int(row[0]),i))
    m.update()
    #definition of T
    for row in customer:
        for k in modes:
            for s in departure:
                if X[int(row[0]),3,k,s]>0:
                    #ending_time[int(row[0])]=(dT[3,k,s]+trans_time[3,k])*X[int(row[0]),3,k,s]
                    if t[int(row[0]),3]>DD[int(row[0])]:
                        m.addConstr(T[int(row[0])],GRB.EQUAL,t[int(row[0]),3]-DD[int(row[0])],name='Tardiness_%s'%(int(row[0])) )
    m.update()    
    m.__data=X,pi,y,t,T
    
##x={}
##x=MIP(nodes,modes,departure),nodes,modes,departure, pi1)
#pi2 is after MIP pi, pi2 is f(x), every round, pi2 will be set to 0. ??????????????????????????
##def getpi2(nodes,modes,departure,X):
##    for k in modes:
##        for s in departure:
##            for i in nodes:
##                if i==4:
##                    continue
##                else:
##                    a = 0
##                    for row in customer:
##                            a=a+int(row[2])*X[int(row[0]),i,k,s].x
##                    pi2[i,k,s]=a-1*arc_C[i,k,s]
##    return pi2

#while loop start!!!

MIP(m,customer,arc_C,nodes,modes,departure)
#print 'mid done'
m.optimize()
X,pi,y,t,T=m.__data
##pi2=getpi2(nodes,modes,departure,X)
##print 'after MIP, pi2',pi2

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
            if i==4:
                continue
            else:
                if y[int(row[0]),i].x>0:
                        print 'Customer',int(row[0])+1,'arc',i,' using 3PL','Trans_cost',F*int(row[2])
                        threePLCost+=F*int(row[2])        
for row in customer:
        for i in nodes:
            if i==4:
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
print 'MIP SOLUTION 3 ARCS'
print 'customer size',len(customer)
print 'Trans_Cost',TransCost
print '3PL_Cost',threePLCost
print 'Total_Trans_Cost',TotalTransCost
print 'Total_Penalty_Cost',TotalTardinessCost
print 'Total_Cost',TotalCost

    
##MIP(nodes,modes,departure),nodes,modes,departure, pi1)
##m.optimize()
##X,y,t,T=m.__data
