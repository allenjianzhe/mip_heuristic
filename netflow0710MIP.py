#file name netflow0710MIP.py
#totaly new modal, 1ROUTE WITH 4 ARCS.
#写成函数形式，为了以后方便时间的控制，当size变大的时候，控制computer时间为1hour。同netflow0709MIP.py 一样
import sys
sys.path.append('C:/gurobi562/win64/python27/lib/gurobipy')
from gurobipy import *
from read0713 import *
import time
start_time=time.clock()
m = Model('netflow14')
M=1000000000
F=100000000
def mip(m):
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
        #decision variable y: binary variable of 3PL
        y = {}
        for n in range(len(customer)):
                y[n]=m.addVar(obj=F,vtype=GRB.BINARY,name='y_%s'%(n))     
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

        ###constraint 3.5 time constraint Three, tardiness time 只跟最后一个t[n,4]有关， 不用联系
        for n in range(len(customer)):      
                for k in modes:
                        for s in range(len(departure)):
                                if X[n,3,4,k,s]>0:
                                        if t[n,4]>DD[n]:                                        
                                                m.addConstr(T[n],GRB.EQUAL,t[n,4]-DD[n],name='Tardiness_%s'%(n) )
        m.update()
        m.__data=X,y,T,t
        return m
####################################################################################################
mip(m)
m.optimize()
X,y,T,t=m.__data

print "\n"
TotalTardinessCost=0
if m.status == GRB.status.OPTIMAL:
        for n in range(len(customer)):
                if y[n].x>0:
                        print 'Customer',n+1,'Destination ',Destination[n], 'quantity ',quantity[n],'DD',DD[n],' using 3PL','Trans_cost',F
                        print '\n'
                for k in modes:
                        for s in range(len(departure)):
                                if X[n,0,1,k,s].x > 0:
                                        print 'Customer',n+1,'Destination ',Destination[n],'quantity ',quantity[n],'DD',DD[n],'Ending_time',t[n,4].x,'Tardiness',T[n].x
                                        TotalTardinessCost+=int(T[n].x*penalty[n])
        print '\n'
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
        #print '\n'
print 'Total_Trans_Cost',TotalTransCost
print 'Total_Penalty_Cost',TotalTardinessCost                    
print 'computer time (seconds): ',time.clock() - float(start_time)
print '\n'
##def mycallback(model,where):
##	if where == GRB.Callback.MIP:
##		time = model.cbGet(GRB.Callback.RUNTIME)
##		best = model.cbGet(GRB.Callback.MIP_OBJBST)
##		if (time >50) & (best < GRB.INFINITY):
##			model.terminate()
##
##model = mip(m)
##model.optimize(mycallback)
