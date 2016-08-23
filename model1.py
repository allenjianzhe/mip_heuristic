#file name 060915.py for MIP1
import sys
#sys.path.append('C:/gurobi562/win64/python27/lib/gurobipy')
sys.path.append('C:/gurobi604/win32/python27/lib/gurobipy')  # for apple
from gurobipy import *
from read052815_apple import *
import time   
start_time=time.clock()
m = Model('MIP')
M=1000000000
F=600000

def MIP1(m,customer,arc_C):
    ####################################################################################################
    #decision variable X: binary variable. X[customer,i,i+1,m,k]
    X = {}
    for row in customer:
        for i in nodes:
            if i == 2:
                continue
            else:
                for k in modes:
                    for s in departure:
                        X[int(row[0]),i,k,s]=m.addVar(obj=int(row[2])*arc_trans_cost[int(row[0]),i,k],vtype=GRB.BINARY,name='X_%s_%s_%s_%s'%(int(row[0]),i,k,s))
    m.update()                
                        
    #decision variable y: binary variable of 3PL
    global y
    global F
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
            if i==2:
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
    #constraint 3.4 arc capacity
    for k in modes:
        for s in departure:
            for i in nodes:
                if i==2:
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
                if i==2:
                    continue
                else:
                    expr = LinExpr()                
                    for k in modes:
                            for s in departure:                                            
                                    expr.addTerms(dT[i,k,s]+trans_time[i,k],X[int(row[0]),i,k,s])
                    expr.add(-1*y[int(row[0]),i]*M)
                    m.addConstr(expr,GRB.LESS_EQUAL,t[int(row[0]),i],name='timeConstr1_%s_%s'%(int(row[0]),i))                        
    m.update()
    #definition of T
    for row in customer:
        for k in modes:
            for s in departure:
                if X[int(row[0]),1,k,s]>0:
                    if t[int(row[0]),1]>DD[int(row[0])]:
                        m.addConstr(T[int(row[0])],GRB.EQUAL,t[int(row[0]),1]-DD[int(row[0])],name='Tardiness_%s'%(int(row[0])) )
    m.update()
    
    m.__data=X,y,t,T
    return m

                  
