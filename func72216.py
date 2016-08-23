
#----------------------------------------------------------------------------
#name func72216.py 
#----------------------------------------------------------------------------
#           Multimodal transportation problem
#----------------------------------------------------------------------------
# Objective: Minimize total cost including transport mode cost, delay penalty cost and 3PL cost
# Last updated: 
#----------------------------------------------------------------------------

import sys
sys.path.append('C:/gurobi563/win32/python27/lib/gurobipy')
from gurobipy import *
import time
import copy
import matplotlib.pyplot as plt
import numpy as np
from read72616 import *

#######################################
#   Definition of Perameter
#######################################

##print 'Basic info'
##for row in customer:
##    print 'Customer',int(row[0])+1,'Destination ',row[1], 'quantity ',int(row[2]),'DD',int(row[3])
##print "\n"
start_time=time.clock()
##M=1000000000
###fix cost of 3pl
##F=4000
### set of routes
##nodes=[1,2,3,4]
###departure time
##departure=[1,2] 
###modes = ['T','R','H','A'], truck, rail, high speed, air
##modes=[1,2,3,4]
#C: each arc capacity
C={}
(C,fix_C)=getC(nodes,modes,departure)
##print C
##print fix_C
##print -fix_C,'test $$$$$$$$$'
#Distance: each arc distance
Distance={}
Distance=getDistance()
#tau: each mode at each arc transporatation time
tau={}
tau=getTau(nodes,modes,getDistance())
#f: unit cost of mode at each arc
f={}
f=getf(nodes,modes,getDistance())
#dT: departure time at each arc
dT={}
dT=getdT()
#sub method key variable pi, change every round,related with i,k,s
pi={}#i=0,1,2,3; k=1,2,3,4; s=1,2,3,4,5,6
#initial pi has been set to 0 
for n in nodes:
    if n==4:
        continue
    else:
        for k in modes:
            for s in departure:
                pi[n,k,s]=0
example_x_1=[]
#{} means dictionary, [] means list
#type of variables: GRB.CONTINUOUS, GRB.BINARY, GRB.INTEGER
def MIP(customer,nodes,modes,departure,pi):
    m=Model('MIP')
    X = {}
    for row in customer:
        for n in nodes:
            if n==4:
                continue
            else:
                for k in modes:
                    for s in departure:
                        X[int(row[0]),n,k,s]=m.addVar(vtype=GRB.BINARY,name='X_%s_%s_%s_%s'%(int(row[0]),n,k,s))
    m.update()
    #try to fix X=1 in the next iteration.
    #print 'example_x_1\n',example_x_1
##    for (row,n,k,s)in example_x_1:
##        m.addConstr(X[int(row[0]),n,k,s],GRB.EQUAL,1)
        #print row, n, k, s
        #X[row,n,k,s].LB==1
    #expr1:the transportation cost related with X    
    expr1=LinExpr()
    for row in customer:
        for n in nodes:
            if n==4:
                continue
            else:
                for k in modes:
                    for s in departure:
                        expr1=expr1+X[int(row[0]),n,k,s]*int(row[2])*f[n,k]
    m.update()
    #expr2:cost with pi
    expr2 = LinExpr()
    for k in modes:
        for s in departure:
            for n in nodes:
                a=LinExpr()
                if n==4:
                    continue
                else:
                    for row in customer:
                            a.addTerms(int(row[2]),X[int(row[0]),n,k,s])
                    a.add(-1,C[n,k,s])
                expr2=expr2+pi[n,k,s]*a  
    m.update()
    #decision variable y: binary variable of 3PL
    y={}
    for row in customer:
        for n in nodes:
            if n==4:
                continue
            else:
                y[int(row[0]),n]=m.addVar(vtype=GRB.BINARY,name='y_%s_%s'%(int(row[0]),n))     
    m.update()
    #expr3:cost related with y, 3PL
    expr3=LinExpr()
    for row in customer:
        for n in nodes:
            if n==4:
                continue
            else:
                expr3=expr3+y[int(row[0]),n]*int(row[2])*F  
    #decision variable: arrive time at each node.
    #t[int(row[0]),i] is arrive time of customer int(row[0]) at arc i.
    t={}
    for row in customer:
        for n in nodes:
            if n==4:
                continue
            else:
                t[int(row[0]),n]=m.addVar(vtype='C',name='nodeTime_%s_%s'%(int(row[0]),n))
    m.update()
    #decision variable:Time tardiness of customer
    #T[int(row[0])] is tardiness of customer int(row[0])
    TD={}
    for row in customer:
            TD[int(row[0])]=m.addVar(vtype='C',name='Tardiness_%s'%(int(row[0])))
    m.update()
    #expr4:cost of time tardiness penalty 
    expr4=LinExpr()
    for row in customer:
        expr4=expr4+TD[int(row[0])]*int(row[2])*int(row[4])
    #######################################
    m.setObjective(expr1+expr2+expr3+expr4)
    #######################################    
    #Constraint 3.2 for each customer, each link, only one plan can be selected
    for row in customer:
        for n in nodes:
            if n==4:
                continue
            else:
                expr5 = LinExpr()       
                for k in modes:
                        for s in departure:
                                expr5.addTerms(1.0,X[int(row[0]),n,k,s])
                expr5.add(y[int(row[0]),n])
                m.addConstr(expr5, GRB.EQUAL, 1,name='One_%s_%s_%s_%s'%(int(row[0]),n,k,s))
    m.update()
    #Constraint binarty of 3PL
    for row in customer:
        for n in nodes:
            if n==1 or n==4:
                continue
            else:
                m.addConstr(y[int(row[0]),n-1],GRB.LESS_EQUAL,y[int(row[0]),n],name='one3pl_%s_%s'%(int(row[0]),n))
    m.update()
    #constraint 3.5 time constraint One
    for row in customer:        
            for n in nodes:
                if n==4:
                    continue
                else: 
                    expr7 = LinExpr()                
                    for k in modes:
                            for s in departure:                                            
                                    expr7.addTerms(dT[n,k,s]+tau[n,k],X[int(row[0]),n,k,s])
                    expr7.add(-M*y[int(row[0]),n])
                    m.addConstr(expr7,GRB.LESS_EQUAL,t[int(row[0]),n],name='timeConstr1_%s_%s'%(int(row[0]),n))                        
    m.update()                    
    for row in customer:        
            for n in nodes:                    
                    expr8 = LinExpr()
                    if n==1 or n==4:
                            continue
                    else:
                            for k in modes:
                                    for s in departure:                                            
                                            expr8.addTerms(dT[n,k,s],X[int(row[0]),n,k,s])
                            expr8.add(y[int(row[0]),n])
                            m.addConstr(expr8,GRB.GREATER_EQUAL,t[int(row[0]),n-1],name='timeConstr2_%s_%s'%(int(row[0]),n))
    m.update()
    #definition of T
    for row in customer:
        for k in modes:
            for s in departure:
                if X[int(row[0]),3,k,s]>0:
                    if t[int(row[0]),3]>int(row[3]):
                        m.addConstr(TD[int(row[0])],GRB.EQUAL,t[int(row[0]),3]-int(row[3]),name='Tardiness_%s'%(int(row[0])) )
    m.update()
    m.optimize()
    return m,X,y,t,TD,m.objVal,expr1,expr2,expr3,expr4
def MIP_OneCustomer(C,kkk,pi,all_fixed_x_idxes):
    #print pi,'SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS',''
    m=Model('MIP_OneCustomer')
    ending_time={}
    ####################################################################################################
    #decision variable X: binary variable. X[customer,i,i+1,m,k]
    row = kkk
    X = {}        
    for n in nodes:
        if n==4:
            continue
        else:
            for k in modes:
                for s in departure:
                    X[int(row[0]),n,k,s]=m.addVar(vtype=GRB.BINARY,name='X_%s_%s_%s_%s'%(int(row[0]),n,k,s))
                    if (int(row[0]),n,k,s) in all_fixed_x_idxes:
                        X[int(row[0]),n,k,s].LB==1
    m.update()
    #check all_fixed_x_idxes first
##    for (row,n,k,s)in all_fixed_x_idxes:
##        X[row,n,k,s].LB==1
    #expr1:the transportation cost related with X    
    expr1=LinExpr()
    for n in nodes:
        if n==4:
            continue
        else:
            for k in modes:
                for s in departure:
                    expr1=expr1+X[int(row[0]),n,k,s]*int(row[2])*f[n,k]
    m.update()
    y={}        
    for n in nodes:
        if n==4:
            continue
        else:
            y[int(row[0]),n]=m.addVar(vtype=GRB.BINARY,name='y_%s_%s'%(int(row[0]),n))     
    m.update()
    #expr2:cost with pi
    expr2 = LinExpr()
    for k in modes:
        for s in departure:
            for n in nodes:
                a=LinExpr()
                if n==4:
                    continue
                else:
                    a.addTerms(int(row[2]),X[int(row[0]),n,k,s])
                    a.add(-1,C[n,k,s]/int(len(customer)))
                    expr2=expr2+pi[n,k,s]*a  
    m.update()
    #expr3:cost related with y, 3PL
    expr3=LinExpr()        
    for n in nodes:
        if n==4:
            continue
        else:
            expr3=expr3+y[int(row[0]),n]*int(row[2])*F                    
    #decision variable: arrive time at each node.
    #t[int(row[0]),i] is arrive time of customer int(row[0]) at arc i.
    t={}
    
    for n in nodes:
        if n==4:
            continue
        else:
            t[int(row[0]),n]=m.addVar(vtype='C',name='nodeTime_%s_%s'%(int(row[0]),n))
    m.update()
    #decision variable:Time tardiness of customer
    #T[int(row[0])] is tardiness of customer int(row[0])
    TD={}        
    TD[int(row[0])]=m.addVar(vtype='C',name='Tardiness_%s'%(int(row[0])))
    m.update()
    #expr4:cost of time tardiness penalty 
    expr4=LinExpr()       
    expr4=expr4+TD[int(row[0])]*int(row[2])*int(row[4])
    m.update()
    #######################################
    #m.setObjective(expr1+expr2+expr3+expr4)
    m.setObjective(expr1+expr2+expr3+expr4)
    ####################################################################################################
    #Constraint 3.2 for each customer, each link, only one plan can be selected        
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
                    expr.addTerms(int(row[2]),X[int(row[0]),n,k,s])
                    expr.addConstant(-1*C[n,k,s])
                    m.addConstr(expr,GRB.LESS_EQUAL, 0,'arcCapacity_%s_%s_%s_%s'%(int(row[0]),n,k,s))      
    m.update()                                          
    #constraint 3.5 time constraint One
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
    for n in nodes:                    
            expr = LinExpr()
            if n==1 or n==4:
                    continue
            else:
                    for k in modes:
                            for s in departure:                                            
                                    expr.addTerms(dT[n,k,s],X[int(row[0]),n,k,s])
                    expr.add(y[int(row[0]),n])
                    m.addConstr(expr,GRB.GREATER_EQUAL,t[int(row[0]),n-1],name='timeConstr2_%s_%s'%(int(row[0]),n))
    m.update()
    #definition of T
    for k in modes:
        for s in departure:
            if X[int(row[0]),3,k,s]>0:
                ending_time[int(row[0])]=(dT[3,k,s]+tau[3,k])*X[int(row[0]),3,k,s]
                if t[int(row[0]),3]>int(row[3]):
                    m.addConstr(TD[int(row[0])],GRB.EQUAL,t[int(row[0]),3]-int(row[3]),name='Tardiness_%s'%(int(row[0])) )
    m.update()
    m.optimize()
    return m,X,y,t,TD,m.objVal,expr1,expr2,expr3,expr4
def expr1_value(X):
    expr1=0
    for row in customer:
        for n in nodes:
            if n==4:
                continue
            else:
                for k in modes:
                    for s in departure:
                        expr1=expr1+X[int(row[0]),n,k,s].x*int(row[2])*f[n,k]
    return expr1
def expr1_v(X,kkk):
    expr1=0
    row=kkk
    #print kkk,'kkk'
    #print X
    for n in nodes:
        if n==4:
            continue
        else:
            for k in modes:
                for s in departure:
                    if X[int(row[0]),n,k,s].x>0:
                        expr1=expr1+X[int(row[0]),n,k,s].x*int(row[2])*f[n,k]
    return expr1
def expr2_value(X,pi):
    k2=0
    for k in modes:
        for s in departure:
            for n in nodes:
                a=0
                if n==4:
                    continue
                else:
                    for row in customer:
                        if X[int(row[0]),n,k,s].x >0:
                            a=a+int(row[2])*X[int(row[0]),n,k,s].x
                    if a==0:#make sure whether X==1, so that we wont add the 0 in the following and make sure a is bigger than 0.
                        a=a
                    else:
                        a=a-C[n,k,s]
                        #print a,'a', 'after all the customer sum'
                k2=k2+pi[n,k,s]*a
    return k2
def expr2_v(X,pi,kkk):
    row=kkk
    k2=0
    for k in modes:
        for s in departure:
            for n in nodes:
                a=0
                if n==4:
                    continue
                else:

                    if X[int(row[0]),n,k,s].x >0:
                        a=a+int(row[2])*X[int(row[0]),n,k,s].x
                    if a==0:#make sure whether X==1, so that we wont add the 0 in the following and make sure a is bigger than 0.
                        a=a
                    else:
                        a=a-C[n,k,s]
                        #print a,'a', 'after all the customer sum'
                k2=k2+pi[n,k,s]*a
    return k2
##def expr2_v(X_list,pi):
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
##            if [int(row[0]), i, k, s] in X_list:
##                a=a+int(row[2])
##        if a==0:#make sure whether X==1, so that we wont add the 0 in the following and make sure a is bigger than 0.
##            a=a
##        else:
##            a=a-C[i,k,s]
##        k2=k2+pi[i,k,s]*a
##    return k2    
def expr3_value(y):
    expr3=0
    for row in customer:
        for n in nodes:
            if n==4:
                continue
            else:
                expr3=expr3+y[int(row[0]),n].x*int(row[2])*F
    return expr3
def expr3_v(y,kkk):
    row=kkk
    expr3=0

    for n in nodes:
        if i==n:
            continue
        else:
            expr3=expr3+y[int(row[0]),n].x*int(row[2])*M
    return expr3
def expr4_value(T):
    expr4=0
    for row in customer:
        expr4=expr4+TD[int(row[0])].x*int(row[2])*int(row[4])
    return expr4
def expr4_v(T,kkk):
    row=kkk
    expr4=0
    expr4=expr4+TD[int(row[0])].x*int(row[2])*int(row[4])
    return expr4
#here def Transfer help me to get the X1, X2, X3 and y from the MIP so that i can consider them as input to the H. 
def Transfer(X,y):
    for row in customer:
        for n in nodes:
            if n==4:
                continue
            else:
                if y[int(row[0]),n].x==1:
                    a=[]
                    a.append(int(row[0]))
                    a.append(n)
                    yy.append(a)
    for n in nodes:
        if n==4:
            continue
        else:
            if n==1:
                for row in customer:
                    for k in modes:
                        for s in departure:
                            if X[int(row[0]),n,k,s].x==1:
                                a=[]
                                a.append(int(row[0]))
                                a.append(k)
                                a.append(s)
                                XX1.append(a)
            if n==2:
                for row in customer:
                    for k in modes:
                        for s in departure:
                            if X[int(row[0]),n,k,s].x==1:
                                a=[]
                                a.append(int(row[0]))
                                a.append(k)
                                a.append(s)
                                XX2.append(a)
            if n==3:
                for row in customer:
                    for k in modes:
                        for s in departure:
                            if X[int(row[0]),nf,k,s].x==1:
                                a=[]
                                a.append(int(row[0]))
                                a.append(k)
                                a.append(s)
                                XX3.append(a) 
    return yy, XX1, XX2, XX3
def plot_Zub(Zub_list):
    y1=Zub_list
    plt.ylabel('Zub')

    plt.plot(y1)
    plt.show()
def plot_Zlb(Zlb_list):    
    y2=Zlb_list
    plt.ylabel('Zlb')
    plt.plot(y2)
    plt.show()

