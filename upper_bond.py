#-*- coding: utf-8 -*-
#file name netflow051315MIP.py  based on netflow051215MIP, delete Tardiness, change 3PL to arc. 
import sys
#sys.path.append('F:/gurobi651/win32/python27/lib/gurobipy') #lenovo
sys.path.append('C:/gurobi604/win32/python27/lib/gurobipy')
from gurobipy import *
from read111115 import *
import time


#   Definition of Variables


print 'Basic info'
for row in customer:
    print 'Customer',int(row[0])+1,'Destination ',row[1], 'quantity ',int(row[2]),'DD',int(row[3])
print "\n"
#'Customer',int(row[0])+1,'link',i,'arc_mode_num',k,'departureTimeIndex',s
#'arc_cost',arc_trans_cost[int(row[0]),i,k]*int(row[2]),'start_Time',dT[i,k,s]
#'Trans_time',trans_time[i,k],'t',t[int(row[0]),i].x,'real_arrive_time',dT[i,k,s]+trans_time[i,k]
start_time=time.clock()
m = Model('MIP')
P=1000000000 

F=1250 #fix cost of 3pl
nodes=[1,2,3,4]# set of routes
departure=[1,2] #departure time
modes=[1,2,3,4]#modes = ['T','R','H','A'], truck, rail, high speed, air
arc_C={}#arc_C: each arc capacity
arc_C=getArcC(nodes,modes,departure)
Distance={}#Distance: each arc distance
Distance=getDistance()
trans_time={}#trans_time: each mode at each arc transporatation time
trans_time=getTransTime(nodes,modes,getDistance())#arc_trans_cost: unit cost of mode at each arc
arc_trans_cost={}
arc_trans_cost=getArcTransCost(customer,nodes,modes,getDistance())
dT={}#dT: departure time at each arc
dT=getdT()#sub method key variable pi, change every round,related with i,k,s
pi={} #i=0,1,2,3; k=1,2,3,4; s=1,2,3,4,5,6
#pi=[ [[[0] for row1 in range(6)] for row2 in range(4)] for row3 in range(4)]

for i in nodes:
    if i==4:
        continue
    else:
        for k in modes:
            for s in departure:
                pi[i,k,s]=0  #initial pi has been set to 0 
def MIP(m,customer,arc_C,nodes,modes,departure,pi):
    X = {}#decision variable X: binary variable. X[customer,i,i+1,m,k]
    for row in customer:
        for i in nodes:
            if i==4:
                continue
            else:
                for k in modes:
                    for s in departure:
                        X[int(row[0]),i,k,s]=m.addVar(vtype=GRB.BINARY,name='X_%s_%s_%s_%s'%(int(row[0]),i,k,s))
    m.update()

    expr1 = LinExpr()#expr1:the transportation cost related with X    #X相关的运输成本
    for row in customer:
        for i in nodes:
            if i==4:
                continue
            else:
                for k in modes:
                    for s in departure:
                        expr1=expr1+X[int(row[0]),i,k,s]*int(row[2])*arc_trans_cost[int(row[0]),i,k]
    expr2 = LinExpr()#expr2:cost with pi
    for k in modes:
        for s in departure:
            for i in nodes:
                a=LinExpr()  # a的表达的含义模糊 ，LinExpr()是Gurobi linear expression object. 
                if i==4:
                    continue
                else:
                    for row in customer:
                            a.addTerms(int(row[2]),X[int(row[0]),i,k,s])
                    a.add(-1,arc_C[i,k,s])
                expr2=expr2+pi[i,k,s]*a  
    m.update()
    
    y={}#decision variable y: binary variable of 3PL
    for row in customer:
        for i in nodes:
            if i==4:
                continue
            else:
                y[int(row[0]),i]=m.addVar(vtype=GRB.BINARY,name='y_%s_%s'%(int(row[0]),i))     
    m.update()
    
    expr3=LinExpr()#expr3:cost related with y, 3PL #模型公式1中的采用第三方物流的所有客户的F*y
    for row in customer:
        for i in nodes:
            if i==4:
                continue
            else:
                expr3=expr3+y[int(row[0]),i]*int(row[2])*F
    #decision variable: arrive time at each node.
    t={}    #t[int(row[0]),i] is arrive time of customer int(row[0]) at arc i.
    for row in customer:
        for i in nodes:
            if i==4:
                continue
            else:
                t[int(row[0]),i]=m.addVar(vtype='C',name='nodeTime_%s_%s'%(int(row[0]),i))  
    #decision variable:Time tardiness of customer客户的迟到时间
    T={}   #T[int(row[0])] is tardiness of customer int(row[0])
    for row in customer:
            T[int(row[0])]=m.addVar(vtype='C',name='Tardiness_%s'%(int(row[0])))
    m.update()

    expr4=LinExpr()  #expr4:cost of time tardiness penalty #公式1中的对于每个客户的p*TD
    for row in customer:
        expr4=expr4+T[int(row[0])]*int(row[2])*int(row[4])                       
##expr1:the transportation cost related with X    #X相关的运输成本
#expr2:cost with pi 
#expr3:cost related with y, 3PL #模型公式1中的采用第三方物流的所有客户的F*y
#expr4:cost of time tardiness penalty #公式1中的对于每个客户的p*TD
    m.setObjective(expr1+expr2+expr3+expr4)


####################################################################################################
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
                m.addConstr(expr5, GRB.EQUAL, 1,name='One_%s_%s_%s_%s'%(int(row[0]),i,k,s))  #模型中公式3，For each route, a customer can only choose one transportation mode or 3PL.
    m.update() 
    #Constraint binarty of 3PL
    for row in customer:
        for i in nodes:
            if i==1 or i==4:
                continue
            else:
                m.addConstr(y[int(row[0]),i-1],GRB.LESS_EQUAL,y[int(row[0]),i],name='one3pl_%s_%s'%(int(row[0]),i))
#sub method will relax capacity constraint, so we don't need that. 
    #constraint 3.4 arc capacity
##    for k in modes:
##        for s in departure:
##            for i in nodes:
##                if i==4:
##                    continue
##                else:
##                    expr6 = LinExpr()
##                    for row in customer:
##                            expr6.addTerms(int(row[2]),X[int(row[0]),i,k,s])
##                    expr6.addConstant(-1*arc_C[i,k,s])
##                    m.addConstr(expr6,GRB.LESS_EQUAL, 0,'arcCapacity_%s_%s_%s_%s'%(int(row[0]),i,k,s))      
##    m.update()  
    #constraint 3.5 time constraint One 时间约束条件一
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

    
    #constraint 3.6 time constraint Two, 新一期的出发时间大于上一期的到达时间
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
                            a=a+int(row[2])*X[int(row[0]),i,k,s].x
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


def Transfer(X,y):#here def Transfer help me to get the X1, X2, X3 and y from the MIP so that i can consider them as input to the H. 
    
    for row in customer:
        for i in nodes:
            if i==4:
                continue
            else:
                if y[int(row[0]),i].x==1:
                    a=[]   #
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
                                XX1.append(a) #XX1[int(row[0]),k,s]=1
                                
            if i==2:
                
                for row in customer:
                    for k in modes:
                        for s in departure:
                            if X[int(row[0]),i,k,s].x==1:
                                a=[]
                                a.append(int(row[0]))
                                a.append(k)
                                a.append(s)
                                XX2.append(a)#XX2[int(row[0]),k,s]=1
                                
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


Z_list=[]
sigma=2
Zub=763500#set initial upper bound Z to 763500
o=0
alpha=1

#G=0 # G is a single value, means sum of QX-C 所有路线的期望的运输量减去承载量的和

M=Model('MIP')
(X,y,t,T,Z)=MIP(m,customer,arc_C,nodes,modes,departure,pi)#here pi=0

threePLCost=0
TransCost=0
TotalTransCost=0
TotalTardinessCost=0
TotalCost=0
if m.status == GRB.status.OPTIMAL:
        for row in customer:
            #print 'Customer',int(row[0]),'Tardiness',T[int(row[0])].x
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
Zlb=Z
print 'initial Zlb',Zlb,'$$$$$$$$$$$$$$$$$'
Z_list=[]
sigma=2

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
                GG[i,k,s]=GG[i,k,s]-arc_C[i,k,s]# where is the problem?
                
print 'GG','\n',GG

print 'pi','\n',pi
for k in modes:
    for s in departure:
        for i in nodes:
            if i==4:
                continue
            else:
                pi[i,k,s]=max(0,pi[i,k,s]+GG[i,k,s]*alpha)


#here i need to try how to use input(infeasible solution) to get the feasible solution
#?????????????????? how to change MIP so that i can get the input and put them in the X1_list, yy_list and so on.

#while sigma>=0.005: # means when sigma<0.005, stop

while o!=5:# means when o=3, stop
    yy=[]
    XX1=[]
    XX2=[]
    XX3=[]
    m = Model('MIP')
    (X,y,t,T,Z)=MIP(m,customer,arc_C,nodes,modes,departure,pi) #Z is the lower bound, set pi=0 get the Zlb
    Transfer(X,y)

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
                #print 'Customer',int(row[0]),'Tardiness',T[int(row[0])].x
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
                    GG[i,k,s]=GG[i,k,s]-arc_C[i,k,s]# where is the problem?

    
    print 'pi','\n',pi
    for k in modes:
        for s in departure:
            for i in nodes:
                if i==4:
                    continue
                else:
                    pi[i,k,s]=max(0,pi[i,k,s]+GG[i,k,s]*alpha)
    print 'pi','\n',pi
##    if Zlb!=TotalTransCost:
##        Zub=min(TotalTransCost,Zub)
    #Zlb=max(TotalTransCost,Zlb)
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
                            #print 'test',X[int(row[0]),i,k,s].x # why X=0 will also be shown?
                            #if you print X[int(row[0]),i,k,s], then all the X will be shown
                            G=G+int(row[2])*X[int(row[0]),i,k,s].x
                    #print 'middle G',G, 'i,k,s',i,k,s
                    G=G-arc_C[i,k,s] # right?????????
    print '\n'
    print 'G',G  
    alpha=sigma*(Zub-Zlb)/(G*G)
    #alpha=alpha/5.0
    if all(l <0 for l in GG)==True: #this means the solution is feasible, but never happen! because GG always has negative number, how to fix that?
        Zlb=max(Z,Zlb)
    else:
        Zlb=Zlb
    print '\n'
    print 'o',o,'alpha',alpha,'Zlb',Zlb,'Zub',Zub,'sigma',sigma



    print '\n'
    if len(Z_list)==3:# run 5 round to make sure Z is not decrease anymore
        if Z<min(Z_list):
            Z_list=[]
            Z_list.append(Z)
        else:
            sigma=0.5*sigma
            Z_list=[]
            Z_list.append(Z)
    else:
        Z_list.append(Z)
        o+=1


    m.__data=X,y,t,T,ending_time
    return m

####################################################################################################


MIP(m,customer,arc_C)

m.optimize()
for row in customer:
    print 'Customer',int(row[0])+1,'Destination ',row[1], 'quantity ',int(row[2]),'DD',int(row[3]),'Tardiness',T[int(row[0])].x
print "\n"



for r in range(iter_max):
