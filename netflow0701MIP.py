#file name netflow0701MIP.py
#totaly new modal, each plan has two departure time
#totally new, only 4 customers, only 'BJ', and 'CQ', only two arc in each route

import sys
sys.path.append('C:/gurobi562/win64/python27/lib/gurobipy')

from gurobipy import *
from read0703 import *
import time
start_time=time.clock()
m = Model('netflow14')
M=1000000000
####################################################################################################
#decision variable X: binary variable of plan and customer, Constraint One
X = {}
for n in range(len(customer)):
        for p in range(len(plan)):
                for s in range(len(departure)):
                        X[n,p,s]=m.addVar(obj=plan_cost[p],vtype=GRB.BINARY,name='X_%s_%s_%s'%(n,p,s))
m.update()

#decision variable y: binary variable of 3PL
#decision variable dTime: actually departure time of each customer
y={}
dTime={} 
for n in range(len(customer)):
        y[n]=m.addVar(obj=quantity[n]*F,vtype=GRB.BINARY,name='y_%s'%(n))
        dTime[n]=m.addVar(obj=0,vtype="C",name='dTime_%s'%(n))
m.update()
#decision variable:Time tardiness of customer
T={}
for n in range(len(customer)):
        T[n]=m.addVar(obj=penalty[n]/24,vtype="C",name='Tardiness_%s'%(n))
m.update()
####################################################################################################

#Constraint 3.1 for each customer, each plan, at most one subplan can be selected
##for n in range(len(customer)):
##        expr1 = LinExpr()
##        for p in range(len(plan)):
##                expr = LinExpr()
##                for s in range(len(departure)):
##                        expr.addTerms(1.0,X[n,p,s])
##                        expr1.addTerms(1.0,X[n,p,s])
##                m.addConstr(expr, GRB.LESS_EQUAL, 1,name='subplan_%s_%s_%s'%(n,p,s))
##        m.addConstr(expr1, GRB.LESS_EQUAL, 1,name='plan_%s_%s_%s'%(n,p,s))
##m.update()
#Constraint 3.2 for each customer, only one plan can be selected
for n in range(len(customer)):
        expr = LinExpr()       
        for p in range(len(plan)):
                for s in range(len(departure)):
                        expr.addTerms(1.0,X[n,p,s])
        expr.add(y[n])
        m.addConstr(expr, GRB.EQUAL, 1,name='One_%s'%(n))
m.update()
####################################################################################################
#constraint 3.3-1 departure time bigger than release time. 有了后2个，这个是废条件
##for n in range(len(customer)):
##        m.addConstr(r[n], GRB.LESS_EQUAL, dTime[n], name="dTime1_%s"%(n) )        
m.update()
#departure time definition
for n in range(len(customer)):
        expr = LinExpr()       
        for p in range(len(plan)):
                for s in range(len(departure)):
                        expr.addTerms(Sdp[n][p][s],X[n,p,s])
        expr.addTerms(r[n],y[n])
        m.addConstr(expr, GRB.EQUAL, dTime[n],name='dTime2_%s'%(n))
m.update()
#Constraint 3.3-2 departure time should bigger than subplan time
##for n in range(len(customer)):
##        for p in range(len(plan)):
##                for s in range(len(departure)):
##                        expr = LinExpr()
##                        expr.add(Sdp[n][p][s])
##                        expr.add((X[n,p,s]-1)*M)                        
##                        m.addConstr(expr, GRB.LESS_EQUAL, dTime[n], name="departureTime_%s"%(n) )
##m.update()

###Constraint 3.4 for each customer, subplan time should bigger than release time.这个恒成立
for n in range(len(customer)):
        for p in range(len(plan)):
                for s in range(len(departure)):
                                expr=LinExpr(Sdp[n][p][s],X[n,p,s])
                                expr.add((1-X[n,p,s])*M)
                                expr.addConstant(-1*r[n])
                                m.addConstr(expr,GRB.GREATER_EQUAL,0,name="departureTime_%s"%(n))
                    
                                
m.update()
###Constraint 3.6 time tardiness
### yTime[n] is the transportation time of y,is a constant
for n in range(len(customer)):        
        expr = LinExpr()
        for p in range(len(plan)):
                for s in range(len(departure)):
                        expr.addTerms(1,X[n,p,s])
                if X[n,p,s]==1:
                        p=k
        if expr==0:
                expr.addTerms(1,dTime[n])
                expr.add(3*y[n])
                expr.addConstant(-1*DD[n])
                m.addConstr(expr, GRB.LESS_EQUAL, T[n], name="time_%s_%s"%(p,n) )
        else:
                expr.addTerms(1,dTime[n])
                expr.addTerms(trans_time[k])
                expr.addConstant(-1*DD[n])
                m.addConstr(expr, GRB.LESS_EQUAL, T[n], name="time_%s_%s"%(p,n) )
m.update()
####################################################################################################
###constraint 3.7 plan capacity
for n in range(len(customer)):
        expr = LinExpr()
        for p in range(len(plan)):
                for s in range(len(departure)):
                        expr.addTerms(plan_capacity[p],X[n,p,s])
                        expr.add((1-X[n,p,s])*M)
                        expr.add(-1*quantity[n])
                        m.addConstr(expr,GRB.GREATER_EQUAL,0,name="plan_capacity_%s"%(n))
m.update()
###constraint 3.8 arc capacity
for j in range(len(modes)):
        for k in range(len(arcs)):
                expr = LinExpr()
                for n in range(len(customer)):
                        for p in range(len(plan)):
                                for s in range(len(departure)):
                                        expr.addTerms(a[p][j][k][n]*quantity[n], X[n,p,s])                               
                m.addConstr(expr,GRB.LESS_EQUAL,arc_C[j,k],name="arc_capacity_%s_%s"%(j,k))
m.update()



m.optimize()
print "\n"
if m.status == GRB.status.OPTIMAL:
        for n in range(len(customer)):
                if y[n].x>0:
                        print 'Customer',n+1,' using 3PL', 'quantity ',quantity[n],'cost',F,'departure_time',dTime[n].x,'Trans_time',yTime
                        print 'Ending_time',dTime[n].x+yTime,'DD',DD[n],'Tardiness',max(0,dTime[n].x+yTime-DD[n])
                        print '\n'
                for p in range(len(plan)):
                        for s in range(len(departure)):                
                                if X[n,p,s].x > 0:
                                        
                                        print 'Customer',n+1,'plan',p+1,'departureNum',s+1,'plan_mode',plan_mode[p],'Destination ',Destination[p],'quantity ',quantity[n]
                                        print 'cost', plan_cost[p],'departure_time',dTime[n].x,'Ending_time',plan_time[p],'DD',DD[n],'Tardiness',T[n].x
                                        print '\n'

                             
                              
#print 'computer time (seconds): ',time.clock() - float(start_time)
#print X[0,0,0].x
#print X[0,0,1].x
#print Sdp[0][0][1]
