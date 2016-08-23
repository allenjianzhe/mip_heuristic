#redefine MIP model, useing setObjective
import sys

sys.path.append('C:/gurobi604/win32/python27/lib/gurobipy')
from gurobipy import *
import time
from read102715 import *

print 'Basic info'
for row in customer:
    print 'Customer',int(row[0])+1,'Destination ',row[1], 'quantity ',int(row[2]),'DD',int(row[3])
print "\n"
start_time=time.clock()
m = Model('MIP')
M=1000000000
#fix cost of 3pl
F=600000
# set of routes
nodes=[1,2,3,4]
#departure time
departure=[1,2] 
#modes = ['T','R','H','A']
modes=[1,2,3,4]

arc_C={}
arc_C=getArcC(nodes,modes,departure)
##print 'len',len(arc_C)
##print arc_C
Distance={}
Distance=getDistance()
trans_time={}
trans_time=getTransTime(nodes,modes,getDistance())
arc_trans_cost={}
arc_trans_cost=getArcTransCost(customer,nodes,modes,getDistance())
dT={}
dT=getdT()

pi={}#i=0,1,2,3; k=1,2,3,4; s=1,2,3,4,5,6
#pi=[ [[[0] for row1 in range(6)] for row2 in range(4)] for row3 in range(4)]
for i in nodes:
    if i==4:
        continue
    else:
        for k in modes:
            for s in departure:
                pi[i,k,s]=0
                
GG={}#{} means dictionary, [] means list
#GG=[ [[0 for row1 in range(6)] for row2 in range(4)] for row3 in range(4)]
##print 'len(GG)',len(GG)
##print 'len(arc_C)',len(arc_C)


for i in nodes:
    if i==4:
        continue
    else:
        for k in modes:
            for s in departure:
                GG[i,k,s]=0
def MIP(m,customer,arc_C,nodes,modes,departure,pi):
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
    
    expr1=LinExpr()
    for row in customer:
        for i in nodes:
            if i==4:
                continue
            else:
                for k in modes:
                    for s in departure:
                        expr1=expr1+X[int(row[0]),i,k,s]*int(row[2])*arc_trans_cost[int(row[0]),i,k]
    #obj add pi, i cannot use LinExpr() formula, how to dicribe the relathion by other way?
    expr2 = LinExpr()
    for k in modes:
        for s in departure:
            for i in nodes:
                a=LinExpr()
                if i==4:
                    continue
                else:
                    for row in customer:
                            a.addTerms(int(row[2]),X[int(row[0]),i,k,s])
                    a.add(-1,arc_C[i,k,s])
                expr2=expr2+pi[i,k,s]*a
         
    m.update()
    #decision variable y: binary variable of 3PL
    y={}
    for row in customer:
        for i in nodes:
            if i==4:
                continue
            else:
                y[int(row[0]),i]=m.addVar(vtype=GRB.BINARY,name='y_%s_%s'%(int(row[0]),i))     
    m.update()

    expr3=LinExpr()
    for row in customer:
        for i in nodes:
            if i==4:
                continue
            else:
                expr3=expr3+y[int(row[0]),i]*int(row[2])*F
                
    #decision variable: arrive time at each node
    t={}
    for row in customer:
        for i in nodes:
            if i==4:
                continue
            else:
                t[int(row[0]),i]=m.addVar(vtype='C',name='nodeTime_%s_%s'%(int(row[0]),i))  
    #decision variable:Time tardiness of customer
    T={}
    for row in customer:
            T[int(row[0])]=m.addVar(vtype='C',name='Tardiness_%s'%(int(row[0])))
    m.update()

    expr4=LinExpr()
    for row in customer:
        expr4=expr4+T[int(row[0])]*int(row[2])*int(row[4])

    m.setObjective(expr1+expr2+expr3+expr4)
    #Constraint 3.2 for each customer, each link, only one plan can be selected
    for row in customer:
        for i in nodes:
            if i==4:
                continue
            else:
                expr5 = LinExpr()       
                for k in modes:
                        for s in departure:
                                expr5.addTerms(1.0,X[int(row[0]),i,k,s])
                expr5.add(y[int(row[0]),i])
                m.addConstr(expr5, GRB.EQUAL, 1,name='One_%s_%s_%s_%s'%(int(row[0]),i,k,s))
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
                    expr6 = LinExpr()
                    for row in customer:
                            expr6.addTerms(int(row[2]),X[int(row[0]),i,k,s])
                    expr6.addConstant(-1*arc_C[i,k,s])
                    m.addConstr(expr6,GRB.LESS_EQUAL, 0,'arcCapacity_%s_%s_%s_%s'%(int(row[0]),i,k,s))      
    m.update()                                          
    #constraint 3.5 time constraint One
    for row in customer:        
            for i in nodes:
                if i==4:
                    continue
                else: 
                    expr7 = LinExpr()                
                    for k in modes:
                            for s in departure:                                            
                                    expr7.addTerms(dT[i,k,s]+trans_time[i,k],X[int(row[0]),i,k,s])
                    expr7.add(-1*y[int(row[0]),i]*M)
                    m.addConstr(expr7,GRB.LESS_EQUAL,t[int(row[0]),i],name='timeConstr1_%s_%s'%(int(row[0]),i))                        
    m.update()                    
    for row in customer:        
            for i in nodes:                    
                    expr8 = LinExpr()
                    if i==1 or i==4:
                            continue
                    else:
                            for k in modes:
                                    for s in departure:                                            
                                            expr8.addTerms(dT[i,k,s],X[int(row[0]),i,k,s])
                            expr8.add(y[int(row[0]),i])
                            m.addConstr(expr8,GRB.GREATER_EQUAL,t[int(row[0]),i-1],name='timeConstr2_%s_%s'%(int(row[0]),i))
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
    m.optimize()
    return X,y,t,T,m.objVal
