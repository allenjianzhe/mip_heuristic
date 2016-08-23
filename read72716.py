
# coding: utf-8

# In[5]:

#name run72616.py
import pandas as pd
def generate_cutomer_data(size_of_customer):
    from random import randint as uniform_dist
    data = pd.DataFrame(columns=['Customer_Id', 'Final_Destination', 'Demand','Due_Date','Penalty'])
    for i in range(size_of_customer):
        data.loc[i] = [i, 'SS', uniform_dist(50,250), uniform_dist(6,35), 50]
    return data
size_of_customer = 5
d = generate_cutomer_data(size_of_customer)
d.to_csv('c:/Users/MacBook Air/Desktop/cus_5_8.csv', index=False)
d = pd.read_csv('c:/Users/MacBook Air/Desktop/customer.csv')
#customer=[]
#for i,row in d.iterrows():
#    customer.append(row.tolist())
customer=d.values.tolist()


# In[12]:

# %load read72516
#file name read70816, based on read051315 CHANGE DT to 2 departure time for each mode
import csv 
import sys
import math
M=1000000000
F=1250

nodes=[1,2,3,4] # set of routes
departure=[1,2] #each plan has two departure time
#modes = ['T','R','H','A']
modes=[1,2,3,4]
def getC(nodes, modes, departure):
    C={}
    fix_C=200
    for n in nodes:
        if n != 4:
            for k in modes:
                for s in departure:
                    C[n,k,s]=fix_C
    return C,fix_C

customer = sorted(customer,key=lambda x:x[2],reverse=True)

def getDistance():
    Distance={}
    Distance[1]=400
    Distance[2]=500
    Distance[3]=700
    Distance[4]=800
    return Distance
def getTau(nodes,modes,Distance):
    tau={}
    for n in nodes:
            if n==4:
                continue
            else:
                for k in modes:
                    tau[n,1]=round(Distance[n]/60.0)
                    tau[n,2]=round(Distance[n]/100.0)
                    tau[n,3]=round(Distance[n]/250.0)
                    tau[n,4]=round(Distance[n]/500.0)
    return tau
def getf(nodes,modes,Distance):#similar to above but delete the customer
    f={}
    unit=1000.0
    for n in nodes:
        if n==4:
            continue
        else:
            for k in modes:
                f[n,1]=int(300*Distance[n]/unit)
                f[n,2]=int(500*Distance[n]/unit)
                f[n,3]=int(1500*Distance[n]/unit)
                f[n,4]=int(2000*Distance[n]/unit)    
    return f
def getST(nodes):
    ST={}#shipping time of route n if 3PL is used, here all make ==1
    for n in nodes:
        if n==4:
            continue
        else:
            ST[n]=1
    return ST
# first dT, using distance 1=400
def getdT():
    dT={}         
    dT[1,1,1]=1
    dT[1,1,2]=2

    dT[1,2,1]=1
    dT[1,2,2]=2

    dT[1,3,1]=1
    dT[1,3,2]=3

    dT[1,4,1]=1
    dT[1,4,2]=3

    dT[2,1,1]=9
    dT[2,1,2]=10

    dT[2,2,1]=9
    dT[2,2,2]=10

    dT[2,3,1]=5
    dT[2,3,2]=7

    dT[2,4,1]=4
    dT[2,4,2]=6

    dT[3,1,1]=18
    dT[3,1,2]=20

    dT[3,2,1]=15
    dT[3,2,2]=20

    dT[3,3,1]=9
    dT[3,3,2]=11

    dT[3,4,1]=8
    dT[3,4,2]=10
    return dT




# In[15]:

# %load func72216

#----------------------------------------------------------------------------
#name func72216.py 
#----------------------------------------------------------------------------
#           Multimodal transportation problem
#----------------------------------------------------------------------------
# Objective: Minimize total cost including transport mode cost, delay penalty cost and 3PL cost
# Last updated: 
#----------------------------------------------------------------------------

import sys
#sys.path.append('C:/gurobi563/win32/python27/lib/gurobipy')
#from gurobipy import *
import time
import copy
import matplotlib.pyplot as plt
import numpy as np

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



# In[17]:

# %load run72216.py
#name run72216  based on run71916
import sys
sys.path.append('C:/gurobi563/win32/python27/lib/gurobipy')
from gurobipy import *
import time
import pdb
import matplotlib.pyplot as plt

Z_list=[]
#set initial upper bound Zub
Zub=float("inf")
#Zub=763500
Zlb=-float("inf")
o=0
delta=1
delta_list=[]
delta_list.append(delta)
lamda=2
lamda_list=[]
lamda_list.append(lamda)
Zlb_list=[]
Zub_list=[]
pi_trace = {}
for n,k,s in pi:
    pi_trace[n,k,s] = [pi[n,k,s]]
#update the upper bound, get feasible solution

#loop_condition_validate = lambda lamda,delta: lamda>=0.05 and delta!=0
#while(loop_condition_validate(lamda, delta)):
    
#while lamda>=0.005 and delta!=0:
while o!=2:
    (C,fix_C)=getC(nodes,modes,departure)
    (m,X,y,t,TD,Z,e1,e2,e3,e4)=MIP(customer,nodes,modes,departure,pi)
    threePLCost=0
    TransCost=0
    TotalTransCost=0
    TotalTardinessCost=0
    TotalCost=0
    #print 'main solution'
    with open('c:/Users/MacBook Air/Desktop/output_infeasible.txt', 'w') as f_out:
        if m.status == GRB.status.OPTIMAL:
                for row in customer:
                    TotalTardinessCost+=TD[int(row[0])].x*int(row[4])*int(row[2])
                    for n in nodes:
                        if n==4:
                            continue
                        else:
                            if y[int(row[0]),n].x>0:
                                    #print 'Customer',int(row[0]),'arc',n,' using 3PL','Trans_cost',F*int(row[2])
                                    f_out.write('Customer %d arc %d using 3PL Trans_cost %d\n'%(int(row[0]),n,F*int(row[2])))
                                    threePLCost+=F*int(row[2])        
        for row in customer:
                for n in nodes:
                    if n==4:
                        continue
                    else:
                        for k in modes:
                            for s in departure:
                                if X[int(row[0]),n,k,s].x > 0:
                                    f_out.write('Customer %d link %d arc_mode_num %d departureTimeIndex %d f %d start_Time %d tau %d t %f real_arrive_time %f\n'%(int(row[0]),n,k,s,f[n,k]*int(row[2]),dT[n,k,s],tau[n,k],t[int(row[0]),n].x,dT[n,k,s]+tau[n,k]))
                                            #print 'Customer',int(row[0]),'link',n,'arc_mode_num',k,'departureTimeIndex',s,'f',f[n,k]*int(row[2]),'start_Time',dT[n,k,s],'tau',tau[n,k],'t',t[int(row[0]),n].x,'real_arrive_time',dT[n,k,s]+tau[n,k]
                                    TransCost+=f[n,k]*int(row[2])
    TotalTransCost=TransCost+threePLCost
    TotalCost=  TotalTardinessCost+   TotalTransCost
    GG={}
    GG_square = 0
    for n in nodes:
        if n==4:
            continue
        else:
            for k in modes:
                for s in departure:
                    GG[n,k,s]=0
    for k in modes:
        for s in departure:
            for n in nodes:
                if n==4:
                    continue
                else:
                    for row in customer:
                        GG[n,k,s]=GG[n,k,s]+int(row[2])*X[int(row[0]),n,k,s].x
                    GG[n,k,s]=GG[n,k,s]-C[n,k,s]
                    GG_square += GG[n,k,s]**2
##    print '\n'
##    print 'GG'
##    print GG
##    print '\n'
    all_fixed_x_idxes = []
    for k in modes:
        for s in departure:
            for n in nodes:
                if n==4:
                    continue
                if -fix_C<GG[n,k,s]<=0:
                    print GG[n,k,s],'GG[n,k,s]',n,k,s
                    for row in customer:
                        if X[int(row[0]),n,k,s].x>0:
                            a=[]
                            a.append(int(row[0]))
                            a.append(n)
                            a.append(k)
                            a.append(s)
                            #here is the first to fix x to 1. 
                            all_fixed_x_idxes.append(a)
                    #print all_fixed_x_idxes,'first time fix x to 1'
                            #print X[int(row[0]),n,k,s].x,'X[int(row[0]),n,k,s].x','int(row[0]),n,k,s',int(row[0]),n,k,s
                if GG[n,k,s]>0:
                    print GG[n,k,s],'GG[n,k,s]',n,k,s
##                    for row in customer:
##                        if X[int(row[0]),n,k,s].x>0:
##                            print X[int(row[0]),n,k,s].x,'X[int(row[0]),n,k,s].x','int(row[0]),n,k,s',int(row[0]),n,k,s
                    customers_for_current_capacity = [(int(row[0]), int(row[2])) for row in customer if X[int(row[0]),n,k,s].x and int(row[2])<=C[n,k,s]]
                    customers_for_current_capacity.sort(key = lambda r: r[1],reverse = True)
                    #print('*'*50,'\n',customers_for_current_capacity)
                    current_sum = 0
                    for i,c in enumerate(customers_for_current_capacity):
                        current_sum += c[1]
                        if current_sum > C[n,k,s]:
                            #C[n,k,s] = C[n,k,s] - (current_sum - c[1])#here upadate C will get bug when you run the MIP because X has fixed to 1 after C being updated
                            break
                    else:
                        i += 1
                    x_to_fix = [[c[0], n, k, s] for c in customers_for_current_capacity[:i]]
                    #print x_to_fix,'x_to_fix'
                    #here is second time, also here is remove the overuse capacity
                    all_fixed_x_idxes.extend(x_to_fix)
                                        #all_fixed_x_idxes.append(x_to_fix)
                    #x_var = [c[0] for c in customers_for_current_capacity[i:]]
    
    #print x_var,'x_var'
    #print 'after for loop' 
    print all_fixed_x_idxes,'all fix x to 1'
    #break

    #from netflow71816 import MIP2
    #mm = Model("MM")
##    print customer
##    print C
##    print all_fixed_x_idxes
    
##    MIP2(mm,customer,C,all_fixed_x_idxes)
##    mm.optimize()
##    X,y,t,TD,ending_time=mm.__data
##    if mm.status == GRB.status.OPTIMAL:
##            for row in customer:
##                #print 'Customer',int(row[0]),'Tardiness',T[int(row[0])].x
##                #TotalTardinessCost+=TD[int(row[0])].x*int(row[4])*int(row[2])
##                for n in nodes:
##                    if n==4:
##                        continue
##                    else:
##                        if y[int(row[0]),n].x>0:
                                #print 'Customer',int(row[0])+1,'arc',n,' using 3PL','Trans_cost',F*int(row[2])
                               # threePLCost+=F*int(row[2])        
    #TotalTransCost=0
##    for row in customer:
##            for n in nodes:
##                if n==4:
##                    continue
##                else:
##                    for k in modes:
##                        for s in departure:
##                                if X[int(row[0]),n,k,s].x > 0:
##                                        print 'Customer',int(row[0])+1,'link',n,'arc_mode_num',k,'departureTimeIndex',s,'arc_cost',f[n,k]*int(row[2]),'start_Time',dT[n,k,s],'Trans_time',tau[n,k],'t',t[int(row[0]),n].x,'real_arrive_time',dT[n,k,s]+tau[n,k]
##                                        TransCost+=f[n,k]*int(row[2])
    #Zub_temple=mm.objVal
    #print 'Zub_temple',Zub_temple
    obj_total=0
    obj_list=[]
    X_list=[]
    y_list=[]
    transCost_list=[]
    piCost_list=[]
    yCost_list=[]
    TimeCost_list=[]
    for kkk in customer:
        this_run_m = Model('MIP_OneCustomer%s')
        this_run_m,X,y,t,TD,obj,e21,e22,e23,e24=MIP_OneCustomer(C,kkk,pi,all_fixed_x_idxes)        
        transCost_list.append(e21.getValue())
        piCost_list.append(e22.getValue())
        yCost_list.append(e23.getValue())
        TimeCost_list.append(e24.getValue())
        nopicost=e21.getValue()+e23.getValue()+e24.getValue()
##        print '********************************************'
##        print e21.getValue(),'transporation cost'
##        print e22.getValue(),'pi  cost'
##        print e23.getValue(),'y cost'
##        print e24.getValue(),'Time tardiness cost'
##        print 'cost not include pi cost',nopicost
##        print '********************************************'
        #threePLCost=0
        #TransCost=0
        #TotalTransCost=0
        #TotalTardinessCost=0
        #TotalCost=0
        #print 'solution of update upperbound \n'
        if this_run_m.status == GRB.status.OPTIMAL:    
            for n in nodes[:-1]:
                if y[int(kkk[0]),n].x==1:
                    #f2_out.write('Customer %d arc %d using 3PL Trans_cost %d\n'%(int(row[0]),n,F*int(row[2])))
                    #print 'Customer',int(kkk[0]),'arc',n,' using 3PL','Trans_cost',F*int(kkk[2])
                    #print '/n'
                    raw_yidxes=y[int(kkk[0]),n].VarName.split('_')[1:]
                    y_list.append([int(e) for e in raw_yidxes])
                    #TransCost+=F*int(kkk[2])
                for k in modes:
                    for s in departure:
                        if X[int(kkk[0]),n,k,s].x > 0:
                            #f2_out.write('Customer %d link %d arc_mode_num %d departureTimeIndex %d f %d start_Time %d tau %d t %f real_arrive_time %f\n'%(int(kkk[0]),n,k,s,f[n,k]*int(kkk[2]),dT[n,k,s],tau[n,k],t[int(kkk[0]),n].x,dT[n,k,s]+tau[n,k]))
                            #print 'X[int(kkk[0]),i,k,s].x',int(kkk[0]),n,k,s,'f[i,k]',f[n,k],'Q*arc',f[n,k]*int(kkk[2])
                            #TransCost+=f[n,k]*int(kkk[2])
                            C[n,k,s]=C[n,k,s]-int(kkk[2])
                            raw_idxes = X[int(kkk[0]),n,k,s].VarName.split('_')[1:]
                            X_list.append([int(e) for e in raw_idxes])
        obj_total+=obj # obj includes the pi cost, but what i want is cost exclude pi cost
        obj_list.append(obj)
##    print '\n'
##    print 'after Al2 C',C
    #print '\n'
    with open('c:/Users/MacBook Air/Desktop/output_upperbound_%d.txt'%i, 'w') as f2_out:
        #f2_out.write(y_list)
        for item in X_list:
            f2_out.write('%s\n'% item)
        for item in y_list:
            f2_out.write('%s\n'% item)
    
    #print 'y_list',y_list
    #print 'X_list',X_list
##    print 'transCost_list',transCost_list
##    print 'piCost_list',piCost_list
##    print sum(piCost_list),'sum of pi cost'
##    print 'yCost_list',yCost_list
##    print 'TimeCost_list',TimeCost_list
##    print 'obj_total',obj_total    
    Zub_temple=sum(transCost_list)+sum(yCost_list)+sum(TimeCost_list)
    #print Zub_temple,'Zub_temple'
    Zub=min(Zub,Zub_temple)
    #print 'Zub updated',Zub
    Zub_list.append(Zub)


    
    Zlb=max(Z,Zlb)
    Zlb=int(Zlb)
    #print 'Zlb updated',Zlb
    Zlb_list.append(Zlb)        
    delta_temple=lamda*(Zub-Zlb)/(GG_square)
    delta=max(0,delta_temple)
    #delta='{:,.4f}'.format(delta)
    delta_list.append(delta)
    if Zlb>Zub:
        Zlb=Zlb_list[-2]
    for k in modes:
        for s in departure:
            for n in nodes:
                if n==4:
                    continue
                else:
                    pi[n,k,s]=max(0,pi[n,k,s]+GG[n,k,s]*delta)
                    pi_trace[n,k,s].append(pi[n,k,s])
    if len(Z_list)==3:
        if Z<min(Z_list):
            Z_list=[]
            Z_list.append(Z)
        else:
            lamda=0.5*lamda
            Z_list=[]
            Z_list.append(Z)
    else:
        Z_list.append(Z)
        lamda_list.append(lamda)
        o+=1
print '\n'
print 'size of customer',len(customer)
print '\n'
print 'computer time (seconds): ',time.clock() - float(start_time)
print '\n'
print 'o',o,'delta',delta,'lambda',lamda,'GG_square',GG_square  
print '\n'
print Zlb_list,'Zlb_list'
print '\n'
print Zub_list,'Zub_list'
print '\n'
print delta_list,'delta_list'
print '\n'
print lamda_list,'lamda_list'
print '\n'
Gap_Zlb=0
Gap_Zub=0
opt=0
##if len(customer)==5:
##    opt=2088000.0
##if len(customer)==10:
##    opt=6378000.0
##if len(customer)==20:
##    opt=3320030.0
    
##if len(customer)==50:
##    opt=4530900.0
##if len(customer)==100:
##    opt=14619000.0
##if len(customer)==200:
##    opt=15845400.0
##Gap_Zlb=(opt-Zlb_list[-1])/opt
##Gap_Zub=(Zub_list[-1]-opt)/opt

print 'Gap_Zlb',(format(Gap_Zlb,'.2%'))
print 'Gap_Zub',(format(Gap_Zub,'.2%'))
##plt.ylabel('pi value')
##plt.plot(pi_trace[3,1,1])
##plt.show()


# In[2]:

'c:/Users/MacBook Air/Desktop/output_upperbound_%r.txt'%5


# In[ ]:



