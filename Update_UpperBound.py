#file name 32516H.py  based on netflow051215MIP, delete Tardiness, change 3PL to arc. 
import sys
sys.path.append('C:/gurobi604/win32/python27/lib/gurobipy')
#sys.path.append('C:/gurobi604/win32/python27/lib/gurobipy')  # for apple
from gurobipy import *
from read111115 import *
import time   
start_time=time.clock()
#F=1250
F=3000
P=1000000000
start_time=time.clock()
pi={}
for i in nodes:
    if i==4:
        continue
    else:
        for k in modes:
            for s in departure:
                pi[i,k,s]=5
def MIP_OneCustomer(arc_C,kkk,pi):
    m=Model('MIP_OneCustomer')
    ending_time={}
    ####################################################################################################
    #decision variable X: binary variable. X[customer,i,i+1,m,k]
    row = kkk
    X = {}        
    for i in nodes:
        if i==4:
            continue
        else:
            for k in modes:
                for s in departure:
                    #print row[0]
                    X[int(row[0]),i,k,s]=m.addVar(vtype=GRB.BINARY,name='X_%s_%s_%s_%s'%(int(row[0]),i,k,s))
    m.update()
    #expr1:the transportation cost related with X    
    expr1=LinExpr()
    
    for i in nodes:
        if i==4:
            continue
        else:
            for k in modes:
                for s in departure:
                    expr1=expr1+X[int(row[0]),i,k,s]*int(row[2])*arc_trans_cost[int(row[0]),i,k]
    y={}        
    for i in nodes:
        if i==4:
            continue
        else:
            y[int(row[0]),i]=m.addVar(vtype=GRB.BINARY,name='y_%s_%s'%(int(row[0]),i))     
    m.update()
    #expr2:cost with pi
    expr2 = LinExpr()
    for k in modes:
        for s in departure:
            for i in nodes:
                a=LinExpr()
                if i==4:
                    continue
                else:
                    a.addTerms(int(row[2]),X[int(row[0]),i,k,s])
                    a.add(-1,arc_C[i,k,s]/int(len(customer)))
                    expr2=expr2+pi[i,k,s]*a  
    m.update()
    #expr3:cost related with y, 3PL
    expr3=LinExpr()        
    for i in nodes:
        if i==4:
            continue
        else:
            expr3=expr3+y[int(row[0]),i]*int(row[2])*F                    
    #decision variable: arrive time at each node.
    #t[int(row[0]),i] is arrive time of customer int(row[0]) at arc i.
    t={}
    
    for i in nodes:
        if i==4:
            continue
        else:
            t[int(row[0]),i]=m.addVar(vtype='C',name='nodeTime_%s_%s'%(int(row[0]),i))  
    #decision variable:Time tardiness of customer
    #T[int(row[0])] is tardiness of customer int(row[0])
    T={}        
    T[int(row[0])]=m.addVar(vtype='C',name='Tardiness_%s'%(int(row[0])))
    m.update()
    #expr4:cost of time tardiness penalty 
    expr4=LinExpr()       
    expr4=expr4+T[int(row[0])]*int(row[2])*int(row[4])

    #######################################
    #m.setObjective(expr1+expr2+expr3+expr4)
    m.setObjective(expr1+expr2+expr3+expr4)
    ####################################################################################################
    #Constraint 3.2 for each customer, each link, only one plan can be selected        
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
                    expr.addTerms(int(row[2]),X[int(row[0]),i,k,s])
                    expr.addConstant(-1*arc_C[i,k,s])
                    m.addConstr(expr,GRB.LESS_EQUAL, 0,'arcCapacity_%s_%s_%s_%s'%(int(row[0]),i,k,s))      
    m.update()                                          
    #constraint 3.5 time constraint One
    for i in nodes:
        if i==4:
            continue
        else: 
            expr = LinExpr()                
            for k in modes:
                    for s in departure:                                            
                            expr.addTerms(dT[i,k,s]+trans_time[i,k],X[int(row[0]),i,k,s])
            expr.add(-1*y[int(row[0]),i]*P)
            m.addConstr(expr,GRB.LESS_EQUAL,t[int(row[0]),i],name='timeConstr1_%s_%s'%(int(row[0]),i))                        
    m.update()                    
    #constraint 3.6 time constraint Two
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
    for k in modes:
        for s in departure:
            if X[int(row[0]),3,k,s]>0:
                ending_time[int(row[0])]=(dT[3,k,s]+trans_time[3,k])*X[int(row[0]),3,k,s]
                if t[int(row[0]),3]>DD[int(row[0])]:
                    m.addConstr(T[int(row[0])],GRB.EQUAL,t[int(row[0]),3]-DD[int(row[0])],name='Tardiness_%s'%(int(row[0])) )
    m.update()
    m.optimize()
    return m,X,y,t,T,m.objVal
def expr1_v(X,kkk):
    expr1=0
    for i in nodes:
        if i==4:
            continue
        else:
            for k in modes:
                for s in departure:
                    expr1=expr1+X[int(kkk[0]),i,k,s].x*int(row[2])*arc_trans_cost[int(kkk[0]),i,k]
    return expr1
    
def expr2_v(X,pi,kkk):
    k2=0
    for k in modes:
        for s in departure:
            for i in nodes:
                a=0
                if i==4:
                    continue
                else:
                    if X[int(kkk[0]),i,k,s].x >0:
                        a=a+int(kkk[2])*X[int(kkk[0]),i,k,s].x
                    if a==0:#make sure whether X==1, so that we wont add the 0 in the following and make sure a is bigger than 0.
                        a=0
                    else:
                        a=a-arc_C[i,k,s]
                    k2=k2+pi[i,k,s]*a
    return k2

##def expr2_v(X_list,pi,kkk):
##    iks_idx_list = []
##    for x in X_list:
##        if x[1:] not in iks_idx_list:
##            iks_idx_list.append(x[1:])    
##    k2 = 0
##    for iks in iks_idx_list:
##        i = iks[0]
##        k = iks[1]
##        s = iks[2]
##        a=0
##        for row in customer:     
##            if [int(kkk[0]), i, k, s] in X_list:
##                a=a+int(kkk[2])
##        if a==0:
##            a=a
##        else:
##            a=a-arc_C[i,k,s]
##        k2=k2+pi[i,k,s]*a
##    return k2    
def expr3_v(y,kkk):
    expr3=0
    for i in nodes:
        if i==4:
            continue
        else:
            expr3=expr3+y[int(kkk[0]),i].x*int(kkk[2])*F
    return expr3
def expr4_v(T,kkk):
    expr4=0
    expr4=expr4+T[int(kkk[0])].x*int(kkk[2])*int(kkk[4])
    return expr4
#def Excutive(MIP_OneCustomer(m,arc_C,kkk,pi),expr2_value(X,pi)):
def execute():
    X_list=[]
    y_list=[]
    transCost_list=[]
    piCost_list=[]
    yCost_list=[]
    TimeCost_list=[]

    obj_total=0
    obj_list=[]
    TransCost=0
    for kkk in customer:
        this_run_m = Model('MIP_OneCustomer%s')
        this_run_m,X,y,t,T,obj=MIP_OneCustomer(arc_C,kkk,pi)
        transCost_list.append(expr1_v(X,kkk))
        piCost_list.append(expr2_v(X,pi,kkk))
        yCost_list.append(expr3_v(y,kkk))
        TimeCost_list.append(expr4_v(T,kkk))
    ##    print '********************************************'
    ##    print expr1_value(X,kkk),'transporation cost'
    ##    print expr2_value(X,pi,kkk),'pi  cost'
    ##    print expr3_value(y,kkk),'y cost'
    ##    print expr4_value(T,kkk),'Time tardiness cost'
    ##    print '********************************************'
        threePLCost=0
        TransCost=0
        TotalTransCost=0
        TotalTardinessCost=0
        TotalCost=0
        if this_run_m.status == GRB.status.OPTIMAL:    
            for i in nodes[:-1]:
                if y[int(kkk[0]),i].x==1:
                    y_list.append(y[int(kkk[0]),i])
                    TransCost+=F*int(kkk[2])
                for k in modes:
                    for s in departure:
                        if X[int(kkk[0]),i,k,s].x > 0:
                            print X[int(kkk[0]),i,k,s].x,int(kkk[0]),i,k,s
                            TransCost+=arc_trans_cost[int(kkk[0]),i,k]*int(kkk[2])
                            arc_C[i,k,s]=arc_C[i,k,s]-int(kkk[2])
                            raw_idxes = X[int(kkk[0]),i,k,s].VarName.split('_')[1:]
                            X_list.append([int(e) for e in raw_idxes])
        obj_total+=obj
        obj_list.append(obj)
    print 'len(y_list)',len(y_list)
    print 'len(X_list)',len(X_list)
    #print 'X_list',X_list
    print 'transCost_list',transCost_list
    print 'piCost_list',piCost_list
    print 'yCost_list',yCost_list
    print 'TimeCost_list',TimeCost_list

    print 'obj_list',obj_list
    print 'obj_total',obj_total
    print 'computer time (seconds): ',time.clock() - float(start_time)



#print Excutive(MIP_OneCustomer(m,arc_C,kkk,pi),expr2_value(X,pi))
