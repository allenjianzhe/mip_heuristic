#file name netflow0709MIP.py
#totaly new modal, 1ROUTE WITH 4 ARCS.
#2 MODES AND 2 DEPARTURE TIME.


import sys
sys.path.append('C:/gurobi562/win64/python27/lib/gurobipy')

from gurobipy import *
from read0713 import *
import time
start_time=time.clock()
m = Model('netflow14')
M=1000000000
F=100000

####################################################################################################
#decision variable X: binary variable. X[customer,i,i+1,m,k]
X = {}
for n in range(len(customer)):
        for i in node:
                if i==0:
                        continue
                else:
                    for k in modes:
                        for s in range(len(departure)):
                            X[n,i-1,i,k,s]=m.addVar(obj=arc_trans_cost[n,i-1,i,k],vtype=GRB.BINARY,name='X_%s_%s_%s_%s'%(n,i,k,s))
m.update()
#test
##for n in range(len(customer)):
##    for i in node:
##            if i==0:
##                    continue
##            else:
##                    print X[n,i-1,i,k,s]                 
                    
#decision variable y: binary variable of 3PL
y={}
for n in range(len(customer)):
        y[n]=m.addVar(obj=F*quantity[n],vtype=GRB.BINARY,name='y_%s'%(n))     
m.update()
#decision variable: arrive time at each node
t={}
for n in range(len(customer)):
    for i in node:
            if i==0:        
                    continue
            else:
                    t[n,i]=m.addVar(obj=0,vtype="C",name='nodeTime_%s_%s'%(n,i))
#decision variable:Time tardiness of customer
T={}
for n in range(len(customer)):
        T[n]=m.addVar(obj=penalty[n],vtype="C",name='Tardiness_%s'%(n))
m.update()
####################################################################################################

#Constraint 3.2 for each customer, only one plan can be selected
for n in range(len(customer)):
        expr = LinExpr()       
        for k in modes:
                for s in range(len(departure)):
                        expr.addTerms(1.0,X[n,0,1,k,s])
        expr.add(y[n])
        m.addConstr(expr, GRB.EQUAL, 1,name='One_%s'%(n))
m.update()
####################################################################################################
#Constraint 3.3, in the middlepoint, In = Out
#? 这种写法不对, i don't know how to improve it
##for n in range(len(customer)):
##    for i in node:
##            if i==0 or i==4:
##                    continue
##            else:
##                    m.addConstr(quicksum(X[n,i-1,i,k,s]for k in modes and s in departure)==quicksum(X[n,i,i+1,k,s]for k in modes and s in departure ),"node_%s_%s"%(k,s))
##m.update()
#换了一种笨点的写法
for n in range(len(customer)):
    for i in node:
            if i==0 or i==4:
                    continue
            else:
                    expr = LinExpr()
                    expr1 = LinExpr()
                    for k in modes:
                            for s in range(len(departure)):
                                    expr.addTerms(1.0,X[n,i-1,i,k,s])
                                    expr1.addTerms(1.0,X[n,i,i+1,k,s])
                    m.addConstr(expr, GRB.EQUAL, expr1,name='middlePointOne_%s'%(n))
                                  
                            
#constraint 3.4 arc capacity
for k in modes:
    for s in range(len(departure)):
        for i in node:
                if i==4:
                        continue
                else:
                        expr = LinExpr()
                        for n in range(len(customer)):
                                expr.addTerms(quantity[n],X[n,i,i+1,k,s])
                        expr.addConstant(-1*arc_C[i,i+1,k,s])
                        m.addConstr(expr,GRB.LESS_EQUAL, 0,'arcCapacity_%s_%s_%s_%s'%(n,i,k,s))      
m.update()

#constraint 3.5 time constraint One
for n in range(len(customer)):        
        for i in node:
                expr = LinExpr()
                
                if i==0:
                        continue
                else:
                        for k in modes:
                                for s in range(len(departure)):
                                        expr.addTerms(dT[i-1,i,k,s]+trans_time[i-1,i,k],X[n,i-1,i,k,s])
                                        
                        expr.add(-1*y[n]*M)
                        m.addConstr(expr,GRB.LESS_EQUAL,t[n,i],name='timeConstr_%s_%s'%(n,i))
                        
m.update()
###constraint 3.5 time constraint Two, make sure departure time should always bigger than arrive time
###这里有问题， 当X=0是， 任然有一个weak limitation，不对, 后面的写法不对， 两个decision 相乘， 过不去

##
###这个条件不多余，要有，上面3.5确保dT[i-1,i,k,s]一定小于t[n,i]，是同一个i的比较，现在是上下i的比较
##for n in range(len(customer)):
##    for i in node:
##            if i==0 or i==4:
##                    continue
##            else:                    
##                    for k in modes:
##                            for s in range(len(departure)):
##                                    if X[n,i,i+1,k,s]>0:
##                                            temple=(dT[i,i+1,k,s]-t[n,i])
##                                            m.addConstr(temple,GRB.GREATER_EQUAL,0,name='timeConstr2_%s_%s_%s_%s'%(n,i,k,s))
##m.update()                    

#constraint 3.6
for n in range(len(customer)):        
        for i in node:
                
                expr1 = LinExpr()
                if i==0 or i==4:
                        continue
                else:
                        for k in modes:
                                for s in range(len(departure)):
                                        
                                        expr1.addTerms(dT[i,i+1,k,s],X[n,i,i+1,k,s])
                        
                       
                        m.addConstr(expr1,GRB.GREATER_EQUAL,t[n,i],name='timeConstr_%s_%s'%(n,i))

m.update()
nothing=0
###constraint 3.7 time constraint Three, tardiness time 只跟最后一个t[n,4]有关， 不用联系
for n in range(len(customer)):      
        for k in modes:
                for s in range(len(departure)):
                        if X[n,3,4,k,s]>0:
                                if t[n,4]>DD[n]:                                        
                                        m.addConstr(T[n],GRB.EQUAL,t[n,4]-DD[n],name='Tardiness_%s'%(n) )
                                else:
                                        nothing=nothing+1#这里其实什么也不需要做

m.update()

####################################################################################################

m.optimize()
print "\n"
#print t[n,4].x
TotalTardinessCost=0
Total3PLcost=0
if m.status == GRB.status.OPTIMAL:
        for n in range(len(customer)):
                if y[n].x>0:
                        print 'Customer',n+1,'Destination ',Destination[n], 'quantity ',quantity[n],'DD',DD[n],' using 3PL','Trans_cost',F*quantity[n]
                        Total3PLcost=Total3PLcost+F*quantity[n]
                        print '\n'
                for k in modes:
                        for s in range(len(departure)):
                                if X[n,0,1,k,s].x > 0:
                                        print 'Customer',n+1,'Destination ',Destination[n],'quantity ',quantity[n],'DD',DD[n],'Ending_time',t[n,4].x,'Tardiness',T[n].x
                                        TotalTardinessCost+=int(T[n].x*penalty[n])
        print '\n'
#print dT[0,1,1,0]
#print dT[0,1,1,1]
TotalTransCost=0
for n in range(len(customer)):
        for i in node:
            if i==4:
                    continue
            else:
                 for k in modes:
                        for s in range(len(departure)):
                                if X[n,i,i+1,k,s].x > 0:
                                        print 'Customer',n+1,'arc',i,i+1,'arc_mode_num',k,'departureNum',s+1,'arc_cost',arc_trans_cost[n,i,i+1,k],'start_Time',dT[i,i+1,k,s],'Trans_time',trans_time[i,i+1,k],'Ending_Time',t[n,i+1].x
                                        TotalTransCost+=arc_trans_cost[n,i,i+1,k]
        print '\n'
    


            


print 'Total_Trans_Cost',TotalTransCost
print 'Total_Penalty_Cost',TotalTardinessCost
print 'Total_3PL_Cost',Total3PLcost
##for n in range(len(customer)):
##      for i in node:
##              if i==0:
##                    continue
##              else:
##                      print t[n,i].x
#print X                                                                               
                              
print 'computer time (seconds): ',time.clock() - float(start_time)
#print X[0,0,1,1,0].x
#print y[n].x
#print X[0,0,1].x
#print Sdp[0][0][1]
##def mycallback(m,where):
##	if where == GRB.Callback.MIP:
##		time = model.cbGet(GRB.Callback.RUNTIME)
##		best = model.cbGet(GRB.Callback.MIP_OBJBST)
##		if (time >5) & (best < GRB.INFINITY):
##			model.terminate()
##
##
##m.optimize(mycallback)
