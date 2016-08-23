
#----------------------------------------------------------------------------
#name 51716.py 
#----------------------------------------------------------------------------
#           Multimodal transportation problem
#----------------------------------------------------------------------------
# Objective: Minimize total cost including transport mode cost, delay penalty cost and 3PL cost
# Last updated: 
#----------------------------------------------------------------------------

import sys
sys.path.append('C:/gurobi604/win32/python27/lib/gurobipy')
from gurobipy import *
import time
from read111215 import *

#######################################
#   Definition of Perameter
#######################################

print 'Basic info'
for row in customer:
    print 'Customer',int(row[0])+1,'Destination ',row[1], 'quantity ',int(row[2]),'DD',int(row[3])
print "\n"
start_time=time.clock()

P=1000000000
#fix cost of 3pl
F=1250
# set of routes
nodes=[1,2,3,4]
#departure time
departure=[1,2] 
#modes = ['T','R','H','A'], truck, rail, high speed, air
modes=[1,2,3,4]
#arc_C: each arc capacity
arc_C={}
arc_C=getArcC(nodes,modes,departure)
#Distance: each arc distance
Distance={}
Distance=getDistance()
#trans_time: each mode at each arc transporatation time
trans_time={}
trans_time=getTransTime(nodes,modes,getDistance())
#arc_trans_cost: unit cost of mode at each arc
arc_trans_cost={}
arc_trans_cost=getArcTransCost(customer,nodes,modes,getDistance())
#dT: departure time at each arc
dT={}
dT=getdT()
#sub method key variable pi, change every round,related with i,k,s
pi={}#i=0,1,2,3; k=1,2,3,4; s=1,2,3,4,5,6
#initial pi has been set to 0 
for i in nodes:
    if i==4:
        continue
    else:
        for k in modes:
            for s in departure:
                pi[i,k,s]=0                
#{} means dictionary, [] means list
#type of variables: GRB.CONTINUOUS, GRB.BINARY, GRB.INTEGER
def MIP(customer,arc_C,nodes,modes,departure,pi):
    m=Model('MIP')
    X = {}
    for row in customer:
        for i in nodes:
            if i==4:
                continue
            else:
                for k in modes:
                    for s in departure:
                        X[int(row[0]),i,k,s]=m.addVar(vtype=GRB.BINARY,name='X_%s_%s_%s_%s'%(int(row[0]),i,k,s))
    m.update()
    #expr1:the transportation cost related with X    
    expr1=LinExpr()
    for row in customer:
        for i in nodes:
            if i==4:
                continue
            else:
                for k in modes:
                    for s in departure:
                        expr1=expr1+X[int(row[0]),i,k,s]*int(row[2])*arc_trans_cost[int(row[0]),i,k]
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
    #expr3:cost related with y, 3PL
    expr3=LinExpr()
    for row in customer:
        for i in nodes:
            if i==4:
                continue
            else:
                expr3=expr3+y[int(row[0]),i]*int(row[2])*F  
    #decision variable: arrive time at each node.
    #t[int(row[0]),i] is arrive time of customer int(row[0]) at arc i.
    t={}
    for row in customer:
        for i in nodes:
            if i==4:
                continue
            else:
                t[int(row[0]),i]=m.addVar(vtype='C',name='nodeTime_%s_%s'%(int(row[0]),i))
    m.update()
    #decision variable:Time tardiness of customer
    #T[int(row[0])] is tardiness of customer int(row[0])
    T={}
    for row in customer:
            T[int(row[0])]=m.addVar(vtype='C',name='Tardiness_%s'%(int(row[0])))
    m.update()
    #expr4:cost of time tardiness penalty 
    expr4=LinExpr()
    for row in customer:
        expr4=expr4+T[int(row[0])]*int(row[2])*int(row[4])
    #######################################
    m.setObjective(expr1+expr2+expr3+expr4)
    #######################################    
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
                    expr7.add(-P*y[int(row[0]),i])
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
                    if t[int(row[0]),3]>DD[int(row[0])]:
                        m.addConstr(T[int(row[0])],GRB.EQUAL,t[int(row[0]),3]-DD[int(row[0])],name='Tardiness_%s'%(int(row[0])) )
    m.update()
    m.optimize()
    return m,X,y,t,T,m.objVal
def MIP_OneCustomer(arc_C,kkk,pi):
    m=Model('MIP_OneCustomer')
    ending_time={}
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
    #pi, i cannot use LinExpr() formula, how to dicribe the relathion by other way?
    #decision variable y: binary variable of 3PL
    y={}    
    for i in nodes:
        if i==4:
            continue
        else:
            y[int(row[0]),i]=m.addVar(vtype=GRB.BINARY,name='y_%s_%s'%(int(row[0]),i))     
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
    m.update()
    #decision variable:Time tardiness of customer
    #T[int(row[0])] is tardiness of customer int(row[0])
    T={}
    T[int(row[0])]=m.addVar(vtype='C',name='Tardiness_%s'%(int(row[0])))
    m.update()
    #expr4:cost of time tardiness penalty 
    expr4=LinExpr()
    expr4=expr4+T[int(row[0])]*int(row[2])*int(row[4])
    #######################################
    m.setObjective(expr1+expr3+expr4)
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
    m.update()
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
    return X,y,t,T,m.objVal
def expr1_value(X):
    expr1=0
    for row in customer:
        for i in nodes:
            if i==4:
                continue
            else:
                for k in modes:
                    for s in departure:
                        expr1=expr1+X[int(row[0]),i,k,s].x*int(row[2])*arc_trans_cost[int(row[0]),i,k]
    return expr1
def expr2_value(X,pi):
    k2=0
    for k in modes:
        for s in departure:
            for i in nodes:
                a=0
                if i==4:
                    continue
                else:
                    for row in customer:
                        if X[int(row[0]),i,k,s].x >0:
                            a=a+int(row[2])*X[int(row[0]),i,k,s].x
                    if a==0:#make sure whether X==1, so that we wont add the 0 in the following and make sure a is bigger than 0.
                        a=a
                    else:
                        a=a-arc_C[i,k,s]
                        #print a,'a', 'after all the customer sum'
                k2=k2+pi[i,k,s]*a
    return k2
def expr2_v(X_list,pi):
    iks_idx_list = []
    for x in X_list:
        if x[1:] not in iks_idx_list:
            iks_idx_list.append(x[1:])
    k2 = 0
    for iks in iks_idx_list:
        i = iks[0]
        k = iks[1]
        s = iks[2]
        a=0
        for row in customer:     
            if [int(row[0]), i, k, s] in X_list:
                a=a+int(row[2])
        if a==0:#make sure whether X==1, so that we wont add the 0 in the following and make sure a is bigger than 0.
            a=a
        else:
            a=a-arc_C[i,k,s]
        k2=k2+pi[i,k,s]*a
    return k2    
def expr3_value(y):
    expr3=0
    for row in customer:
        for i in nodes:
            if i==4:
                continue
            else:
                expr3=expr3+y[int(row[0]),i].x*int(row[2])*F
    return expr3
def expr4_value(T):
    expr4=0
    for row in customer:
        expr4=expr4+T[int(row[0])].x*int(row[2])*int(row[4])
    return expr4
Z_list=[]
sigma=2
#set initial upper bound Zub
#Zub=15171100
Zub=763500
o=0
alpha=1
#here def Transfer help me to get the X1, X2, X3 and y from the MIP so that i can consider them as input to the H. 
def Transfer(X,y):
    for row in customer:
        for i in nodes:
            if i==4:
                continue
            else:
                if y[int(row[0]),i].x==1:
                    a=[]
                    a.append(int(row[0]))
                    a.append(i)
                    yy.append(a)
    for i in nodes:
        if i==4:
            continue
        else:
            if i==1:
                for row in customer:
                    for k in modes:
                        for s in departure:
                            if X[int(row[0]),i,k,s].x==1:
                                a=[]
                                a.append(int(row[0]))
                                a.append(k)
                                a.append(s)
                                XX1.append(a)
            if i==2:
                for row in customer:
                    for k in modes:
                        for s in departure:
                            if X[int(row[0]),i,k,s].x==1:
                                a=[]
                                a.append(int(row[0]))
                                a.append(k)
                                a.append(s)
                                XX2.append(a)
            if i==3:
                for row in customer:
                    for k in modes:
                        for s in departure:
                            if X[int(row[0]),i,k,s].x==1:
                                a=[]
                                a.append(int(row[0]))
                                a.append(k)
                                a.append(s)
                                XX3.append(a) 
    return yy, XX1, XX2, XX3
#in ordor to get the lower bound, we set pi=0 and run MIP to get it. 
#M=Model('MIP')
(O,X,y,t,T,Z)=MIP(customer,arc_C,nodes,modes,departure,pi)
threePLCost=0
TransCost=0
TotalTransCost=0
TotalTardinessCost=0
TotalCost=0
if O.status == GRB.status.OPTIMAL:
        for row in customer:
            TotalTardinessCost+=T[int(row[0])].x*int(row[4])*int(row[2])
            for i in nodes:
                if i==4:
                    continue
                else:
                    if y[int(row[0]),i].x>0:
                            #print 'Customer',int(row[0])+1,'arc',i,' using 3PL','Trans_cost',F*int(row[2])
                            threePLCost+=F*int(row[2])        
for row in customer:
        for i in nodes:
            if i==4:
                continue
            else:
                for k in modes:
                    for s in departure:
                            if X[int(row[0]),i,k,s].x > 0:
                                    #print 'Customer',int(row[0])+1,'link',i,'arc_mode_num',k,'departureTimeIndex',s,'arc_cost',arc_trans_cost[int(row[0]),i,k]*int(row[2]),'start_Time',dT[i,k,s],'Trans_time',trans_time[i,k],'t',t[int(row[0]),i].x,'real_arrive_time',dT[i,k,s]+trans_time[i,k]
                                    TransCost+=arc_trans_cost[int(row[0]),i,k]*int(row[2])
TotalTransCost=TransCost+threePLCost
TotalCost=  TotalTardinessCost+   TotalTransCost
##print '\n'
##print 'MIP SOLUTION 3 ARCS','first time to get the lower bound'
##print 'customer size',len(customer)
##print 'Trans_Cost',TransCost
##print '3PL_Cost',threePLCost
##print 'Total_Trans_Cost',TotalTransCost
##print 'Total_Penalty_Cost',TotalTardinessCost
##print 'Total_Cost',TotalCost
Zlb=Z
print '\n'
print 'initial Zlb',Zlb,'$$$$$$$$$$$$$$$$$'
Z_list=[]
o=0
print 'o',o,'alpha',alpha,'Zlb',Zlb,'Zub',Zub,'sigma',sigma
GG={}
for i in nodes:
    if i==4:
        continue
    else:
        for k in modes:
            for s in departure:
                GG[i,k,s]=0
for k in modes:
    for s in departure:
        for i in nodes:
            #a=LinExpr()
            if i==4:
                continue
            else:
                for row in customer:
                    if X[int(row[0]),i,k,s].x>0:
                        #print 'i,k,s',i,k,s
                        #print 'GG[i,k,s]',GG[i,k,s]
                        GG[i,k,s]=GG[i,k,s]+int(row[2])*X[int(row[0]),i,k,s].x
                        #print 'GG[i,k,s]',GG[i,k,s]
                GG[i,k,s]=GG[i,k,s]-arc_C[i,k,s]              
#print 'GG','\n',GG
#here we first time to update pi
for k in modes:
    for s in departure:
        for i in nodes:
            if i==4:
                continue
            else:
                pi[i,k,s]=max(0,pi[i,k,s]+GG[i,k,s]*alpha)
print 'pi','updated','\n',pi
#update the upper bound, get feasible solution
#while sigma>=0.05: # means when sigma<0.005, stop
#start our first time run, each run will include the AL2(for kkk in customer), this takes a lot of time
while o!=3:
##    yy=[]
##    XX1=[]
##    XX2=[]
##    XX3=[]
    print 'main round',o
    (m,X,y,t,T,Z)=MIP(customer,arc_C,nodes,modes,departure,pi)
##    Transfer(X,y)
##    print '#####################################$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$'
##    print 'XX1',XX1
##    print 'XX2',XX2
##    print 'XX3',XX3
##    print 'YY',yy
##    print '********************************************'
    print expr1_value(X),'transporation cost'
    print expr2_value(X,pi),'pi  cost'
    print expr3_value(y),'y cost'
    print expr4_value(T),'Time tardiness cost'
    print '********************************************'
    for row in customer:
        print 'Customer',int(row[0])+1,'Tardiness',T[int(row[0])].x
    print '\n'
    threePLCost=0
    TransCost=0
    TotalTransCost=0
    TotalTardinessCost=0
    TotalCost=0
    if m.status == GRB.status.OPTIMAL:
            for row in customer:
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
    print 'MIP SOLUTION 3 ARCS','o',o
    print 'customer size',len(customer)
    print 'Trans_Cost',TransCost
    print '3PL_Cost',threePLCost
    print 'Total_Trans_Cost',TotalTransCost
    print 'Total_Penalty_Cost',TotalTardinessCost
    print 'Total_Cost',TotalCost
    #G size is nmt, similar to pi. but G is a number
    G = 0
    for k in modes:
        for s in departure:
            for i in nodes:
                if i==4:
                    continue
                else:
                    for row in customer:
                        if X[int(row[0]),i,k,s].x>0:
                            G=G+int(row[2])*X[int(row[0]),i,k,s].x
                    G=G-arc_C[i,k,s]
    print '\n'
    print 'G',G
    GG={}
    for i in nodes:
        if i==4:
            continue
        else:
            for k in modes:
                for s in departure:
                    GG[i,k,s]=0
    for k in modes:
        for s in departure:
            for i in nodes:
                #a=LinExpr()
                if i==4:
                    continue
                else:
                    for row in customer:
                        if X[int(row[0]),i,k,s].x>0:
                            GG[i,k,s]=GG[i,k,s]+int(row[2])*X[int(row[0]),i,k,s].x
                    GG[i,k,s]=GG[i,k,s]-arc_C[i,k,s]
    print 'GG','\n',GG
    #update pi,pi is three degree of n, m ,t. also GG, same degree
    print 'pi','\n',pi
    for k in modes:
        for s in departure:
            for i in nodes:
                if i==4:
                    continue
                else:
                    pi[i,k,s]=max(0,pi[i,k,s]+GG[i,k,s]*alpha)
    print 'pi','updated','\n',pi
    import copy
    obj_total=0
    obj_list=[]
    X_list=[]
    y_list=[]
    for kkk in customer:
        print 'round',int(kkk[0])
        this_run_m = Model('MIP_OneCustomer%s')
        (X,y,t,T,obj)=MIP_OneCustomer(arc_C,kkk,pi)
        threePLCost=0
        TransCost=0
        TotalTransCost=0
        TotalTardinessCost=0
        TotalCost=0
        if this_run_m.status == GRB.status.OPTIMAL:   # get rid of for row in customer and problem solved.     
            for i in nodes[:-1]:
                if y[int(kkk[0]),i].x==1:
                    y_list.append(y[int(kkk[0]),i])
                for k in modes:
                    for s in departure:
                        if X[int(kkk[0]),i,k,s].x > 0:
                            TransCost+=arc_trans_cost[int(kkk[0]),i,k]*int(kkk[2])
                            arc_C[i,k,s]=arc_C[i,k,s]-int(kkk[2])
                            raw_idxes = X[int(kkk[0]),i,k,s].VarName.split('_')[1:]
                            X_list.append([int(e) for e in raw_idxes])
        obj_total+=obj
        obj_list.append(obj)
    #for now , only get the solution of feasible, but we need to add pi cost, and get the total cost. 
    print 'obj_total',obj_total
    print X_list
    pi_cost=expr2_v(X_list,pi)
    print 'pi_cost',pi_cost
    Zub_temple=pi_cost+obj_total
    print 'Zub_temple',Zub_temple,'Zub',Zub
    Zub=min(Zub,Zub_temple)
    print 'updated Zub',Zub
    Zlb=max(Z,Zlb)
    print 'Z',Z,'Zlb',Zlb
    print 'updated Zlb',Zlb
    print 'sigma',sigma,'G',G
    alpha=sigma*(Zub-Zlb)/(G*G)
    print 'o',o,'alpha',alpha,'Zlb',Zlb,'Zub',Zub,'sigma',sigma    
    print '\n'
    if len(Z_list)==3:
        if Z<min(Z_list):
            Z_list=[]
            Z_list.append(Z)
        else:
            sigma=0.9*sigma
            Z_list=[]
            Z_list.append(Z)
    else:
        Z_list.append(Z)
        o+=1
print 'computer time (seconds): ',time.clock() - float(start_time)
