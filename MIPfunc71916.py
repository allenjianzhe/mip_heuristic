#file name netflow71816.py  based on netflow051215MIP, delete Tardiness, change 3PL to arc. 
import sys
#sys.path.append('C:/gurobi563/win32/python27/lib/gurobipy')
sys.path.append('C:/gurobi605/win32/python27/lib/gurobipy')
#sys.path.append('C:/gurobi604/win32/python27/lib/gurobipy')  # for apple
from gurobipy import *
from read70816 import *

def MIP(m,customer,C):
    m = Model('MIP')
    ####################################################################################################
    #decision variable X: binary variable. X[customer,i,i+1,m,k]
    X = {}
    for row in customer:
        for n in nodes:
            if n==4:
                continue
            else:
                for k in modes:
                    for s in departure:
                        X[int(row[0]),n,k,s]=m.addVar(obj=int(row[2])*f[n,k],vtype=GRB.BINARY,name='X_%s_%s_%s_%s'%(int(row[0]),n,k,s))
    m.update()                                
    #decision variable y: binary variable of 3PL
    y={}
    for row in customer:
        for n in nodes:
            if n==4:
                continue
            else:
                y[int(row[0]),n]=m.addVar(obj=int(row[2])*F,vtype=GRB.BINARY,name='y_%s_%s'%(int(row[0]),n))     
    m.update()
    #decision variable: arrive time at each node
    t={}
    for row in customer:
        for n in nodes:
            if n==4:
                continue
            else:
                t[int(row[0]),n]=m.addVar(obj=0,vtype='C',name='nodeTime_%s_%s'%(int(row[0]),n))  
    #decision variable:Time tardiness of customer
    TD={}
    for row in customer:
            TD[int(row[0])]=m.addVar(obj=int(row[2])*int(row[4]),vtype='C',name='Tardiness_%s'%(int(row[0])))
    m.update()
    ####################################################################################################
    #Constraint 3.2 for each customer, each link, only one plan can be selected
    for row in customer:
        for n in nodes:
            if n==4:
                continue
            else:
                expr = LinExpr()       
                for k in modes:
                        for s in departure:
                                expr.addTerms(1.0,X[int(row[0]),n,k,s])
                expr.add(y[int(row[0]),n])
                m.addConstr(expr, GRB.EQUAL, 1,name='One_%s_%s_%s_%s'%(int(row[0]),n,k,s))
    m.update()
    ####################################################################################################
    #Constraint binarty of 3PL
    for row in customer:
        for n in nodes:
            if n==1 or n==4:
                continue
            else:
                m.addConstr(y[int(row[0]),n-1],GRB.LESS_EQUAL,y[int(row[0]),n],name='one3pl_%s_%s'%(int(row[0]),n))
    #constraint 3.4 arc capacity
    for k in modes:
        for s in departure:
            for n in nodes:
                if n==4:
                    continue
                else:
                    expr = LinExpr()
                    for row in customer:
                            expr.addTerms(int(row[2]),X[int(row[0]),n,k,s])
                    expr.addConstant(-1*C[n,k,s])
                    m.addConstr(expr,GRB.LESS_EQUAL, 0,'arcCapacity_%s_%s_%s_%s'%(int(row[0]),n,k,s))      
    m.update()                                          
    #constraint 3.5 time constraint One
    for row in customer:        
            for n in nodes:
                if n==4:
                    continue
                else: 
                    expr = LinExpr()                
                    for k in modes:
                            for s in departure:                                            
                                    expr.addTerms(dT[n,k,s]+tau[n,k],X[int(row[0]),n,k,s])
                    expr.add(-1*y[int(row[0]),n]*M)
                    m.addConstr(expr,GRB.LESS_EQUAL,t[int(row[0]),n],name='timeConstr1_%s_%s'%(int(row[0]),n))                        
    m.update()                    
    #constraint 3.6 time constraint Two
    for row in customer:        
            for n in nodes:                    
                    expr1 = LinExpr()
                    if n==1 or n==4:
                            continue
                    else:
                            for k in modes:
                                    for s in departure:                                            
                                            expr1.addTerms(dT[n,k,s],X[int(row[0]),n,k,s])
                            expr1.add(y[int(row[0]),n])
                            m.addConstr(expr1,GRB.GREATER_EQUAL,t[int(row[0]),n-1],name='timeConstr2_%s_%s'%(int(row[0]),n))
    m.update()
    #definition of T
    for row in customer:
        for k in modes:
            for s in departure:
                if X[int(row[0]),3,k,s]>0:
                    ending_time[int(row[0])]=(dT[3,k,s]+tau[3,k])*X[int(row[0]),3,k,s]
                    if t[int(row[0]),3]>DD[int(row[0])]:
                        m.addConstr(TD[int(row[0])],GRB.EQUAL,t[int(row[0]),3]-DD[int(row[0])],name='Tardiness_%s'%(int(row[0])) )
    m.update()    
    m.__data=X,y,t,TD,ending_time
    return m
####################################################################################################

