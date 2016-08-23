﻿#file name 1028.py
import sys
#sys.path.append('C:/gurobi562/win64/python27/lib/gurobipy')
sys.path.append('C:/gurobi600/win32/python27/lib/gurobipy')  # for apple
from gurobipy import *
from read1028 import *
import time


    
start_time=time.clock()
m1 = Model('MIP')
M=1000000000
F=600000
y={}
for row in customer:
    y[int(row[0])]=0
def MIP1(m1,customer,arc_C):
    ####################################################################################################
    #decision variable X for arc 0-1: binary variable. X[customer,i,i+1,m,k]
    X1 = {}
    for row in customer:
            for i in node:
                    if i==0 or i==2:
                            continue
                    else:
                        for k in modes:
                            for s in range(len(departure)):
                                X1[int(row[0]),i-1,i,k,s]=m1.addVar(obj=int(row[2])*arc_trans_cost[int(row[0]),i-1,i,k],vtype=GRB.BINARY,name='X1_%s_%s_%s_%s'%(int(row[0]),i,k,s))
    m1.update()
    #decision variable X for arc 1-2: binary variable. X[customer,i,i+1,m,k]
    X2 = {}
    for row in customer:
            for i in node:
                    if i==0 or i==1:
                            continue
                    else:
                        for k in modes:
                            for s in range(len(departure)):
                                X2[int(row[0]),i-1,i,k,s]=m1.addVar(obj=int(row[2])*arc_trans_cost[int(row[0]),i-1,i,k],vtype=GRB.BINARY,name='X2_%s_%s_%s_%s'%(int(row[0]),i,k,s))
    m1.update()
                        
    #decision variable y: binary variable of 3PL
    global y
    for row in customer:
        #print row
        y[int(row[0])]=m1.addVar(obj=F*int(row[2]),vtype=GRB.BINARY,name='y_%s'%(int(row[0])))     
    m1.update()
    #decision variable: arrive time at each node
    t={}
    for row in customer:
        for i in node:
                if i==0:        
                        continue
                else:
                        t[int(row[0]),i]=m1.addVar(obj=0,vtype="C",name='nodeTime_%s_%s'%(int(row[0]),i))  
    #decision variable:Time tardiness of customer
    T={}
    for row in customer:
            T[int(row[0])]=m1.addVar(obj=int(row[2])*int(row[4]),vtype="C",name='Tardiness_%s'%(int(row[0])))
    m1.update()
    ####################################################################################################
    #Constraint 3.2 for each customer, only one plan can be selected
    for row in customer:
            expr = LinExpr()       
            for k in modes:
                    for s in range(len(departure)):
                            expr.addTerms(1.0,X1[int(row[0]),0,1,k,s])
            expr.add(y[int(row[0])])
            m1.addConstr(expr, GRB.EQUAL, 1,name='One_%s'%(int(row[0])))
    m1.update()
    ####################################################################################################
    #Constraint 3.3, in the middlepoint, In = Out
    for row in customer:
        expr = LinExpr()
        expr1 = LinExpr()
        for k in modes:
            for s in range(len(departure)):
                expr.addTerms(1.0,X1[int(row[0]),0,1,k,s])
                expr1.addTerms(1.0,X2[int(row[0]),1,2,k,s])
        m1.addConstr(expr, GRB.EQUAL, expr1,name='middlePointOne_%s'%(int(row[0])))                                                              
    #constraint 3.4 arc capacity
    for k in modes:
        for s in range(len(departure)):
            for i in node:
                    if i==0 or i==2:
                            continue
                    else:
                            expr = LinExpr()
                            for row in customer:
                                    expr.addTerms(int(row[2]),X1[int(row[0]),i-1,i,k,s])
                            expr.addConstant(-1*arc_C[i-1,i,k,s])
                            m1.addConstr(expr,GRB.LESS_EQUAL, 0,'arcCapacity_%s_%s_%s_%s'%(int(row[0]),i,k,s))      
    m1.update()
    for k in modes:
        for s in range(len(departure)):
            for i in node:
                    if i==0 or i==1:
                            continue
                    else:
                            expr = LinExpr()
                            for row in customer:
                                    expr.addTerms(int(row[2]),X2[int(row[0]),i-1,i,k,s])
                            expr.addConstant(-1*arc_C[i-1,i,k,s])
                            m1.addConstr(expr,GRB.LESS_EQUAL, 0,'arcCapacity_%s_%s_%s_%s'%(int(row[0]),i,k,s))      
    m1.update()
    #constraint 3.5 time constraint One
    for row in customer:        
            for i in node:
                    expr = LinExpr()                
                    if i==0 or i==2:
                            continue
                    else:
                            for k in modes:
                                    for s in range(len(departure)):                                            
                                            expr.addTerms(dT[i-1,i,k,s]+trans_time[i-1,i,k],X1[int(row[0]),i-1,i,k,s])
                            expr.add(-1*y[int(row[0])]*M)
                            m1.addConstr(expr,GRB.LESS_EQUAL,t[int(row[0]),i],name='timeConstr_%s_%s'%(int(row[0]),i))                            
    m1.update()
    for row in customer:        
            for i in node:
                    expr = LinExpr()                
                    if i==0 or i==1:
                            continue
                    else:
                            for k in modes:
                                    for s in range(len(departure)):                                            
                                            expr.addTerms(dT[i-1,i,k,s]+trans_time[i-1,i,k],X2[int(row[0]),i-1,i,k,s])
                            expr.add(-1*y[int(row[0])]*M)
                            m1.addConstr(expr,GRB.LESS_EQUAL,t[int(row[0]),i],name='timeConstr_%s_%s'%(int(row[0]),i))
    m1.update()
    #constraint 3.6 time constraint Two, 新一期的出发时间大于上一期的到达时间
    for row in customer:        
            for i in node:                    
                    expr1 = LinExpr()
                    if i==0 or i==2:
                            continue
                    else:
                            for k in modes:
                                    for s in range(len(departure)):                                            
                                            expr1.addTerms(dT[i,i+1,k,s],X2[int(row[0]),i,i+1,k,s])                          
                            m1.addConstr(expr1,GRB.GREATER_EQUAL,t[int(row[0]),i],name='timeConstr_%s_%s'%(int(row[0]),i))

    m1.update()
    nothing=0
    ###constraint 3.7 time constraint Three, tardiness time 只跟最后一个t[n,4]有关， 不用联系
    for row in customer:      
            for k in modes:
                    for s in range(len(departure)):
                            if X2[int(row[0]),1,2,k,s]>0:
                                    if t[int(row[0]),2]>int(row[3]):                                        
                                            m1.addConstr(T[int(row[0])],GRB.EQUAL,t[int(row[0]),2]-DD[int(row[0])],name='Tardiness_%s'%(int(row[0])) )
                                    else:
                                            nothing=nothing+1#这里其实什么也不需要做

    m1.update()
    m1.__data=X1,X2,y,t,T
    return m1


####################################################################################################


MIP1(m1,customer,arc_C)
m1.optimize()
X1,X2,y,t,T=m1.__data


print '\n'
print "MIP model"
print "\n"
print 'Basic info'
print 'arc, 0-1,1-2'
print 'mode_1, Truck; mode_2,Rail;mode_3,HighSpeed Rail; mode_4, Air'
#print 'arc 0-1:','SC-WH ','arc 1-2:','WH-ZZ'
for row in customer:
    print 'Customer',int(row[0]),'Destination ','ZZ', 'quantity ',int(row[2]),'DD',DD[int(row[0])]
print "\n"

#print t[0,4]
print 'Summary solution'
threePLCost1=0
TransCost1=0
TotalTransCost1=0
TotalTardinessCost1=0
TotalCost1=0
if m1.status == GRB.status.OPTIMAL:
        for row in customer:
                if y[int(row[0])].x>0:
                        print 'Customer',int(row[0]),' using 3PL','Trans_cost',F*int(row[2])
                        #TotalTransCost+=F
                        threePLCost1+=F*int(row[2])
                                       
print '\n'
print 'Solution detail'       
for row in customer:
    for k in modes:
        for s in range(len(departure)):
            if X1[int(row[0]),0,1,k,s].x > 0:
                print 'Customer',int(row[0]),'arc',0,1,'arc_mode_num',k,'departureNum',s+1,'arc_cost',arc_trans_cost[int(row[0]),0,1,k]*int(row[2]),'start_Time',dT[0,1,k,s],'Trans_time',trans_time[0,1,k],'Ending_Time',t[int(row[0]),1].x
                TransCost1+=arc_trans_cost[int(row[0]),0,1,k]*int(row[2])
            if X2[int(row[0]),1,2,k,s].x > 0:
                arrive_time[int(row[0])]=dT[1,2,k,s]+trans_time[1,2,k]
                print 'Customer',int(row[0]),'arc',1,2,'arc_mode_num',k,'departureNum',s+1,'arc_cost',arc_trans_cost[int(row[0]),1,2,k]*int(row[2]),'start_Time',dT[1,2,k,s],'Trans_time',trans_time[1,2,k],'Ending_Time',t[int(row[0]),2].x,'Tardiness',T[int(row[0])].x,'arrive_time',dT[1,2,k,s]+trans_time[1,2,k]
                TransCost1+=arc_trans_cost[int(row[0]),1,2,k]*int(row[2])
                
TotalTransCost1=TransCost1+threePLCost1
TotalCost1=  TotalTardinessCost1+   TotalTransCost1 
print '\n'
print 'Trans_Cost1',TransCost1
print '3PL_Cost1',threePLCost1
print 'Total_Trans_Cost1',TotalTransCost1
print 'Total_Penalty_Cost1',TotalTardinessCost1
print 'Total_Cost1',TotalCost1
print 'computer time (seconds): ',time.clock() - float(start_time)
print '\n'


###########################################################################################################################################################
###########################################################################################################################################################
###########################################################################################################################################################
from read051715 import *
m = Model('MIP')
def MIP(m,customer,arc_C):
    ####################################################################################################
    #decision variable X for arc 0-1: binary variable. X[customer,i,i+1,m,k]
    X3 = {}
    for row in customer:
            for i in node:
                    if i==2:
                            continue
                    else:
                        for k in modes:
                            for s in range(len(departure)):
                                X3[int(row[0]),i-1,i,k,s]=m.addVar(obj=int(row[2])*arc_trans_cost[int(row[0]),i-1,i,k],vtype=GRB.BINARY,name='X1_%s_%s_%s_%s'%(int(row[0]),i,k,s))
    m.update()
                      
    #decision variable y: binary variable of 3PL
    y2={}
    for row in customer:
        #print row
        y2[int(row[0])]=m.addVar(obj=F*int(row[2]),vtype=GRB.BINARY,name='y2_%s'%(int(row[0])))     
    m.update()
    #decision variable: arrive time at each node
    t={}
    for row in customer:
        for i in node:
                if i==2:        
                        continue
                else:
                        t[int(row[0]),i]=m.addVar(obj=0,vtype="C",name='nodeTime_%s_%s'%(int(row[0]),i))  
    #decision variable:Time tardiness of customer
    T={}
    for row in customer:
            T[int(row[0])]=m.addVar(obj=int(row[2])*int(row[4]),vtype="C",name='Tardiness_%s'%(int(row[0])))
    m.update()
    ####################################################################################################
    #Constraint 3.2 for each customer, only one plan can be selected
    for row in customer:
            expr = LinExpr()       
            for k in modes:
                    for s in range(len(departure)):
                            expr.addTerms(1.0,X3[int(row[0]),2,3,k,s])
            expr.add(y2[int(row[0])])
            m.addConstr(expr, GRB.EQUAL, 1,name='One_%s'%(int(row[0])))
    m.update()
    ####################################################################################################
    #new constraint between y and y2
    for row in customer:
        global y
        if y[int(row[0])].x==1:
            #print 'test','y[int(row[0])]',y[int(row[0])]
            m.addConstr(y2[int(row[0])],GRB.EQUAL,1,name='yConstre_%s'%(int(row[0])))                                                                
    #constraint 3.4 arc capacity
    for k in modes:
        for s in range(len(departure)):
            for i in node:
                    if i==2:
                            continue
                    else:
                            expr = LinExpr()
                            for row in customer:
                                    expr.addTerms(int(row[2]),X3[int(row[0]),i-1,i,k,s])
                            expr.addConstant(-1*arc_C[i-1,i,k,s])
                            m.addConstr(expr,GRB.LESS_EQUAL, 0,'arcCapacity_%s_%s_%s_%s'%(int(row[0]),i,k,s))      
    m.update()
    #constraint 3.5 time constraint One
    for row in customer:        
            for i in node:
                    expr = LinExpr()                
                    if i==2:
                            continue
                    else:
                            for k in modes:
                                    for s in range(len(departure)):                                            
                                            expr.addTerms(dT[i-1,i,k,s]+trans_time[i-1,i,k],X3[int(row[0]),i-1,i,k,s])
                            expr.add(-1*y2[int(row[0])]*M)
                            m.addConstr(expr,GRB.LESS_EQUAL,t[int(row[0]),i],name='timeConstr_%s_%s'%(int(row[0]),i))                            
    m.update()
    # constraint 3.6 NEW time constraint
    for row in customer:
        expr = LinExpr()
        for i in node:
            if i==2:
                continue
            else:
                for k in modes:
                    for s in range(len(departure)):
                        if X3[int(row[0]),i-1,i,k,s]>0:
                            global arrive_time
                            expr.addTerms(dT[i-1,i,k,s],X3[int(row[0]),i-1,i,k,s])
        m.addConstr(expr,GRB.GREATER_EQUAL, arrive_time[int(row[0])],name='timeConstr2_%s'%(int(row[0])))

    ###constraint 3.7 time constraint Three, tardiness time 只跟最后一个t[n,4]有关， 不用联系
    for row in customer:      
            for k in modes:
                    for s in range(len(departure)):
                            if X3[int(row[0]),2,3,k,s]>0 and t[int(row[0]),3]>int(row[3]) :                                           
                                m.addConstr(T[int(row[0])],GRB.EQUAL,t[int(row[0]),3]-int(row[3]),name='Tardiness_%s'%(int(row[0])) )
                            else:
                                nothing=nothing+1#这里其实什么也不需要做

    m.update()
    m.__data=X3,y2,t,T
    
    return m


####################################################################################################


MIP(m,customer,arc_C)
m.optimize()
X3,y2,t,T=m.__data


##m.computerIIS()
##m.write('model.ilp')


print '\n'
print "MIP model"
print "\n"
print 'Basic info'
print 'arc, 2-3'
print 'mode_1, Truck; mode_2,Rail;mode_3,HighSpeed Rail; mode_4, Air'

for row in customer:
    print 'Customer',int(row[0]),'Destination ',"SH", 'quantity ',int(row[2]),'DD',int(row[3]),'required start time',arrive_time[int(row[0])]
print "\n"

print 'Summary solution'
threePLCost2=0
TransCost2=0
TotalTransCost2=0
TotalTardinessCost2=0
TotalCost2=0
if m.status == GRB.status.OPTIMAL:
        for row in customer:
                if y2[int(row[0])].x>0:
                        print 'Customer',int(row[0]),' using 3PL','Trans_cost',F*int(row[2])
                        #TotalTransCost+=F
                        threePLCost2+=F*int(row[2])                                       
print '\n'
print 'Solution detail'       
for row in customer:
    for k in modes:
        for s in range(len(departure)):
            if X3[int(row[0]),2,3,k,s].x > 0:
                print 'Customer',int(row[0]),'arc',2,3,'arc_mode_num',k,'departureNum',s+1,'arc_cost',arc_trans_cost[int(row[0]),2,3,k]*int(row[2]),'start_Time',dT[2,3,k,s],'Trans_time',trans_time[2,3,k],'Ending_Time',t[int(row[0]),3].x,'Tardiness',T[int(row[0])].x
                TransCost2+=arc_trans_cost[int(row[0]),2,3,k]*int(row[2])
                TotalTardinessCost2+=T[int(row[0])].x*int(row[4])*int(row[2])

TotalTransCost2=TransCost2
TotalCost2=  TotalTardinessCost2+   TotalTransCost2   
##print '\n'
##print '3PL_Cost',threePLCost2
##print 'Trans_Cost',TransCost2
##print 'Total_Trans_Cost',TotalTransCost2
##print 'Total_Penalty_Cost',TotalTardinessCost2
##print 'Total_Cost',TotalCost2
print 'computer time (seconds): ',time.clock() - float(start_time)
print '\n'
print '3PL_Cost',threePLCost2
print 'Trans_Cost',TransCost2+TransCost1
print 'Total_Trans_Cost',TotalTransCost2+TotalTransCost1
print 'Total_Penalty_Cost',TotalTardinessCost2
print 'Total',TotalCost1+TotalCost2
