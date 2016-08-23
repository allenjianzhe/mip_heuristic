#file name 32516H.py  based on netflow051215MIP, delete Tardiness, change 3PL to arc. 
import sys
sys.path.append('C:/gurobi604/win32/python27/lib/gurobipy')
#sys.path.append('C:/gurobi604/win32/python27/lib/gurobipy')  # for apple
from gurobipy import *
from read111115 import *
import time   
start_time=time.clock()
m = Model('MIP')
M=1000000000
F=1250
ending_time={}
aaa=[]
def MIP(m,customer,arc_C,kkk):
    ####################################################################################################
    #decision variable X: binary variable. X[customer,i,i+1,m,k]
    X = {}
    for row in customer:
        if row==kkk:
            for i in nodes:
                if i==4:
                    continue
                else:
                    for k in modes:
                        for s in departure:
                            X[int(row[0]),i,k,s]=m.addVar(obj=int(row[2])*arc_trans_cost[int(row[0]),i,k],vtype=GRB.BINARY,name='X_%s_%s_%s_%s'%(int(row[0]),i,k,s))
    m.update()                                
    #decision variable y: binary variable of 3PL
    y={}
    for row in customer:
        if row==kkk:
            for i in nodes:
                if i==4:
                    continue
                else:
                    y[int(row[0]),i]=m.addVar(obj=int(row[2])*F,vtype=GRB.BINARY,name='y_%s_%s'%(int(row[0]),i))     
    m.update()
    #decision variable: arrive time at each node
    t={}
    for row in customer:
        if row ==kkk:
            for i in nodes:
                if i==4:
                    continue
                else:
                    t[int(row[0]),i]=m.addVar(obj=0,vtype='C',name='nodeTime_%s_%s'%(int(row[0]),i))  
    #decision variable:Time tardiness of customer
    T={}
    for row in customer:
        if row==kkk:
            T[int(row[0])]=m.addVar(obj=int(row[2])*int(row[4]),vtype='C',name='Tardiness_%s'%(int(row[0])))
    m.update()
    ####################################################################################################
    #Constraint 3.2 for each customer, each link, only one plan can be selected
    for row in customer:
        if row==kkk:
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
    ####################################################################################################
    #Constraint binarty of 3PL
    for row in customer:
        if row==kkk:
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
                        if row ==kkk:
                            expr.addTerms(int(row[2]),X[int(row[0]),i,k,s])
                    expr.addConstant(-1*arc_C[i,k,s])
                    m.addConstr(expr,GRB.LESS_EQUAL, 0,'arcCapacity_%s_%s_%s_%s'%(int(row[0]),i,k,s))      
    m.update()                                          
    #constraint 3.5 time constraint One
    for row in customer:
        if row==kkk:
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
    #constraint 3.6 time constraint Two
    for row in customer:
        if row==kkk:
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
        if row==kkk:
            for k in modes:
                for s in departure:
                    if X[int(row[0]),3,k,s]>0:
                        ending_time[int(row[0])]=(dT[3,k,s]+trans_time[3,k])*X[int(row[0]),3,k,s]
                        if t[int(row[0]),3]>DD[int(row[0])]:
                            m.addConstr(T[int(row[0])],GRB.EQUAL,t[int(row[0]),3]-DD[int(row[0])],name='Tardiness_%s'%(int(row[0])) )
    m.update()
    m.optimize()
    m.__data=X,y,t,T,ending_time
    return m,X,y,m.objVal

X_list=[]
y_list=[]
obj_total=0
obj_list=[]
TransCost=0
for kkk in customer:
    this_run_m,X,y,obj=MIP(m,customer,arc_C,kkk)
    obj_total+=obj
    obj_list.append(obj)
    #print obj
    #print 'kkk',kkk

    if this_run_m.status == GRB.status.OPTIMAL:
        #print X,y
        #second, update arc_C
        a=[]
        for i in nodes:
            if i==4:
                continue
                if y[int(kkk[0]),i]==1:
                    y_list.append(y[int(kkk[0]),i])
                else:
                    continue
            else:
                for k in modes:
                    for s in departure:
                        if X[int(kkk[0]),i,k,s].x==1:
                            TransCost+=arc_trans_cost[int(kkk[0]),i,k]*int(kkk[2])
                            print 'TransCost',TransCost,'arc_trans_cost[int(kkk[0]),i,k]',arc_trans_cost[int(kkk[0]),i,k],'int(kkk[2])',int(kkk[2]),arc_trans_cost[int(kkk[0]),i,k]*int(kkk[2])
                            print '(int(kkk[0]),i,k,s)',(int(kkk[0]),i,k,s)
                            #print 'X_list',X_list
                            
                            a.append(X[int(kkk[0]),i,k,s])
                            #print 'a',a
                            #print 'arc_C[i,k,s]',arc_C[i,k,s]
                            arc_C[i,k,s]=arc_C[i,k,s]-int(kkk[2])
                            #print 'arc_C[i,k,s]',arc_C[i,k,s]
        X_list.append(a)
for row in X_list:
    print row
for row in y_list:
    print row
print obj_total
print obj_list                        
    
