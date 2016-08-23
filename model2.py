#file name 060915_2.py model MIP2
import sys
#sys.path.append('C:/gurobi562/win64/python27/lib/gurobipy')
sys.path.append('C:/gurobi604/win32/python27/lib/gurobipy')  # for apple
from gurobipy import *
from read052815_2_apple import *
m2 = Model('MIP')
M=1000000000
F=600000
y2={}
for row in customer: 
    for i in nodes:
        y2[int(row[0]),i]=0
def MIP2(m2,customer,arc_C):
    #decision variable X: binary variable. X[customer,i,i+1,m,k]
    X2 = {}
    for row in customer:
        for i in nodes:
            if i==3:
                continue
            else:
                for k in modes:
                    for s in departure:
                        X2[int(row[0]),i,k,s]=m2.addVar(obj=int(row[2])*arc_trans_cost[int(row[0]),i,k],vtype=GRB.BINARY,name='X_%s_%s_%s_%s'%(int(row[0]),i,k,s))
    m2.update()                          
    #decision variable y: binary variable of 3PL
    global y2
    for row in customer:
        for i in nodes:
            if i==3:
                continue
            else:
                global F
                y2[int(row[0]),i]=m2.addVar(obj=int(row[2])*F,vtype=GRB.BINARY,name='y_%s_%s'%(int(row[0]),i))     
    m2.update()
    #decision variable: arrive time at each node
    t={}
    for row in customer:
        for i in nodes:
            if i==3:
                continue
            else:
                t[int(row[0]),i]=m2.addVar(obj=0,vtype='C',name='nodeTime_%s_%s'%(int(row[0]),i))  
    #decision variable:Time tardiness of customer
    T={}
    for row in customer:
            T[int(row[0])]=m2.addVar(obj=int(row[2])*int(row[4]),vtype='C',name='Tardiness_%s'%(int(row[0])))
    m2.update()
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
                                expr.addTerms(1.0,X2[int(row[0]),i,k,s])
                expr.add(y2[int(row[0]),i])
                m2.addConstr(expr, GRB.EQUAL, 1,name='One_%s_%s_%s_%s'%(int(row[0]),i,k,s))
    m2.update()
    #############################################################################
    #New constraint between y and y2
    for row in customer:
        global y
        if y[int(row[0]),1].x>0:
            m2.addConstr(y2[int(row[0]),2],GRB.EQUAL,1,name='yConstre_%s'%(int(row[0])))
    #constraint 3.4 arc capacity
    for k in modes:
        for s in departure:
            for i in nodes:
                if i==3:
                    continue
                else:
                    expr = LinExpr()
                    for row in customer:
                            expr.addTerms(int(row[2]),X2[int(row[0]),i,k,s])
                    expr.addConstant(-1*arc_C[i,k,s])
                    m2.addConstr(expr,GRB.LESS_EQUAL, 0,'arcCapacity_%s_%s_%s_%s'%(int(row[0]),i,k,s))      
    m2.update()                                          
    #constraint 3.5 time constraint One
    for row in customer:        
            for i in nodes:
                if i==3:
                    continue
                else:
                    expr = LinExpr()                
                    for k in modes:
                        for s in departure:
                            expr.addTerms(dT[i,k,s]+trans_time[i,k],X2[int(row[0]),i,k,s])
                    expr.add(-1*y2[int(row[0]),i]*M)
                    m2.addConstr(expr,GRB.LESS_EQUAL,t[int(row[0]),i],name='timeConstr1_%s_%s'%(int(row[0]),i))                        
    m2.update()                    
    # constraint 3.6 NEW time constraint
    for row in customer:
        expr = LinExpr()
        for i in nodes:
            if i==3:
                continue
            else:
                for k in modes:
                    for s in departure:
                        if X2[int(row[0]),i,k,s]>0:
                            global arrive_time
                            expr.addTerms(dT[i,k,s],X2[int(row[0]),i,k,s])
        m2.addConstr(expr,GRB.GREATER_EQUAL, arrive_time[int(row[0])],name='timeConstr2_%s'%(int(row[0])))
    m2.update()
    #global ending_time
    for row in customer:
        for k in modes:
            for s in departure:
                if X2[int(row[0]),2,k,s]>0:
                    if t[int(row[0]),2]>DD[int(row[0])]:
                        m2.addConstr(T[int(row[0])],GRB.EQUAL,t[int(row[0]),2]-DD[int(row[0])],name='Tardiness_%s'%(int(row[0])) )
    m2.update()
    m2.__data=X2,y2,t,T
    return m2
