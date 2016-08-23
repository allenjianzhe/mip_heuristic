#file name netflow0829LP.py
#similar to netflow0818LP.py, but try to create the def only for the X which will change into binary
import sys
sys.path.append('C:/gurobi600/win32/python27/lib/gurobipy')  # for apple
#sys.path.append('C:/gurobi562/win64/python27/lib/gurobipy')

from gurobipy import *
from read0804 import *
import time


    
start_time=time.clock()
m = Model('MIP')
M=10000000000
F=10000000

##def MIP_change_bi(m,r,i,k,s):
##    X[r,i-1,i,k,s]=m.addVar(obj=arc_trans_cost[r,i-1,i,k],vtype=GRB.BINARY,name='X_%s_%s_%s_%s'%(r,i,k,s))
##    m.update()
##    #Constraint 3.2 for each customer, only one plan can be selected
    
    
    
    

def MIP(m,customer,arc_C,r_bi,i_bi,k_bi,s_bi):
    ####################################################################################################
    #decision variable X: binary variable. X[customer,i,i+1,m,k]
    X = {}
    for row in customer:
            for i in node:
                    if i==0:
                            continue
                    else:
                        for k in modes:
                            for s in range(len(departure)):
                                if (int(row[0]),i,k,s)==(r_bi,i_bi,k_bi,s_bi):
                                   X[int(row[0]),i-1,i,k,s]=m.addVar(obj=arc_trans_cost[int(row[0]),i-1,i,k],vtype=GRB.BINARY,name='X_%s_%s_%s_%s'%(int(row[0]),i,k,s))
                                else:
                                   X[int(row[0]),i-1,i,k,s]=m.addVar(obj=arc_trans_cost[int(row[0]),i-1,i,k],vtype='C',name='X_%s_%s_%s_%s'%(int(row[0]),i,k,s)) 
    m.update()                  
                        
    #decision variable y: binary variable of 3PL
    y={}
    for row in customer:
            for i in node:
                    if i==0:
                            continue
                    else:
                        y[int(row[0]),i-1,i]=m.addVar(obj=F,vtype=GRB.BINARY,name='y_%s'%(int(row[0])))         
    m.update()
    #decision variable: arrive time at each node
    t={}
    for row in customer:
        for i in node:
                if i==0:        
                        continue
                else:
                        t[int(row[0]),i]=m.addVar(obj=0,vtype="C",name='nodeTime_%s_%s'%(int(row[0]),i))  
    #decision variable:Time tardiness of customer
    T={}
    for row in customer:
            T[int(row[0])]=m.addVar(obj=int(row[4]),vtype="C",name='Tardiness_%s'%(int(row[0])))
    m.update()
    ####################################################################################################
    #Constraint 3.2 for each customer, only one plan can be selected
    for row in customer:
        for i in node:
            if i==0:
                continue
            else:
                expr = LinExpr()       
                for k in modes:
                        for s in range(len(departure)):
                                expr.addTerms(1.0,X[int(row[0]),i-1,i,k,s])
                expr.add(y[int(row[0]),i-1,i])
                m.addConstr(expr, GRB.EQUAL, 1,name='One_%s'%(int(row[0])))
    m.update()
    ####################################################################################################
    #Constraint 3.3, in the middlepoint, In = Out
    for row in customer:
        for i in node:
                if i==0 or i==4:
                        continue
                else:
                        expr = LinExpr()
                        expr1 = LinExpr()
                        for k in modes:
                                for s in range(len(departure)):
                                        expr.addTerms(1.0,X[int(row[0]),i-1,i,k,s])
                                        expr.addTerms(1.0,y[int(row[0]),i-1,i])
                                        expr1.addTerms(1.0,X[int(row[0]),i,i+1,k,s])
                                        expr1.addTerms(1.0,y[int(row[0]),i,i+1])
                        m.addConstr(expr, GRB.EQUAL, expr1,name='middlePointOne_%s'%(int(row[0])))                                                              
    #constraint 3.4 arc capacity
    for k in modes:
        for s in range(len(departure)):
            for i in node:
                    if i==4:
                            continue
                    else:
                            expr = LinExpr()
                            for row in customer:
                                    expr.addTerms(int(row[2]),X[int(row[0]),i,i+1,k,s])
                            expr.addConstant(-1*arc_C[i,i+1,k,s])
                            m.addConstr(expr,GRB.LESS_EQUAL, 0,'arcCapacity_%s_%s_%s_%s'%(int(row[0]),i,k,s))      
    m.update()                                          
    #constraint 3.5 time constraint One
    for row in customer:        
            for i in node:
                    expr = LinExpr()                
                    if i==0:
                            continue
                    else:
                            for k in modes:
                                    for s in range(len(departure)):                                            
                                            expr.addTerms(dT[i-1,i,k,s]+trans_time[i-1,i,k],X[int(row[0]),i-1,i,k,s])
                            expr.add(y[int(row[0]),i-1,i]*trans_time_y[i-1,i])
                            m.addConstr(expr,GRB.LESS_EQUAL,t[int(row[0]),i],name='timeConstrOne_%s_%s'%(int(row[0]),i))                        
    m.update()                    
    #constraint 3.8 time constraint Two, 新一期的出发时间大于上一期的到达时间
    for row in customer:        
        for i in node:
                expr = LinExpr()                
                if i==0 or i==4:
                        continue
                else:
                        for k in modes:
                                for s in range(len(departure)):                                            
                                        expr.addTerms(dT[i,i+1,k,s]+trans_time[i,i+1,k],X[int(row[0]),i,i+1,k,s])
                        expr.add(y[int(row[0]),i,i+1]*trans_time_y[i,i+1])
                        m.addConstr(expr,GRB.GREATER_EQUAL,t[int(row[0]),i],name='timeConstrTwo_%s_%s'%(int(row[0]),i))

    m.update()
##    #constraint 3.7 time constraint Three,two arrive time relationship by using y
##    for row in customer:        
##            for i in node:
##                    expr = LinExpr()                
##                    if i==0 or i==1:
##                            continue
##                    else:
##                        expr.addTerms(1.0,t[int(row[0]),i-1])
##                        expr.addTerms(y[int(row[0]),i-1,i]*trans_time_y[i-1,i])
##                        m.addConstr(t[int(row[0]),i],GRB.GREATER_EQUAL,expr,name='timeConstrThree_%s_%s'%(int(row[0]),i))
##    m.update()
    
    ###constraint 3.9 time constraint five, tardiness time 只跟最后一个t[n,4]有关， 不用联系
    nothing=0
    for row in customer:      
            for k in modes:
                    for s in range(len(departure)):
                            if X[int(row[0]),3,4,k,s]>0:
                                    if t[int(row[0]),4]>int(row[3]):                                        
                                            m.addConstr(T[int(row[0])],GRB.EQUAL,t[int(row[0]),4]-int(row[3]),name='Tardiness_%s'%(int(row[0])) )
                                    else:
                                            nothing=nothing+1#这里其实什么也不需要做

    m.update()
    m.__data=X,y,t,T
    return m


####################################################################################################
(a_bi,b_bi,c_bi,d_bi)=(100,100,100,100)

MIP(m,customer,arc_C,a_bi,b_bi,c_bi,d_bi)
m.optimize()
X,y,t,T=m.__data

print "\n"
print 'Basic info'
for row in customer:
    print 'Customer',int(row[0]),'Destination ',row[1], 'quantity ',int(row[2]),'DD',int(row[3])
print "\n"
print 'Summary solution'
TotalTardinessCost=0
TotalTransCost=0
if m.status == GRB.status.OPTIMAL:
        for row in customer:
            print 'Customer',int(row[0]),'Tardiness',T[int(row[0])].x
            TotalTardinessCost+=T[int(row[0])].x*int(row[4])
            for i in node:                
                if i==0:
                    continue
                else:
                    if y[int(row[0]),i-1,i].x>0:
                            print 'node',i-1,i,' using 3PL','Trans_cost',F
                            TotalTransCost+=F
                    for k in modes:
                            for s in range(len(departure)):
                                    if X[int(row[0]),i-1,i,k,s].x > 0:
                                        print 'arc',i-1,i,'m',k,'s',s,'X',X[int(row[0]),i-1,i,k,s].x,'arc_cost',arc_trans_cost[int(row[0]),i-1,i,k],'Depart_time',dT[i-1,i,k,s],'Trans_time',trans_time[i-1,i,k],'Arrived_time',t[int(row[0]),i].x
                                        TotalTransCost+=arc_trans_cost[int(row[0]),i-1,i,k]
            print '\n'
print 'Total_Trans_Cost',TotalTransCost
print 'Total_Penalty_Cost',TotalTardinessCost                    
print 'computer time (seconds): ',time.clock() - float(start_time)
#在0804LP的基础上改，应该是先run把最大的X变为0,1变量，完了run一遍，完了如果为1，fix，kick them out, 再开始第二遍，直到X的数量小于2为止。
#给X排序
X_move={}
node_arc=[]
indexes=[]
for i in node:
    if i==0:
        continue
    else:
        for k in modes:
            for s in range(len(departure)):                
                for row in customer:
                    print i,k,s,X[int(row[0]),i-1,i,k,s].x
                    if X[int(row[0]),i-1,i,k,s].x > 0:
                        #print 'arc',i-1,i,'k',k,'s',s,'customer',row[0],X[int(row[0]),i-1,i,k,s].x
                        #print i-1,i,k,s,X[int(row[0]),i-1,i,k,s].x
                        arr=str([i-1,i,k,s])
                        node_arc.append(X[int(row[0]),i-1,i,k,s].x)
                        indexes.append([int(row[0]),i,k,s])
                #sort(node_arc[i-1,i,k,s])
                if len(node_arc)>0:
                  max_value = max(node_arc)
                  max_index = node_arc.index(max_value)
                  print 'max',indexes[max_index],max_value,max_index
                  (r,i,k,s)=indexes[max_index]
                  print 'change' ,r,i,k,s
                  node_arc=[]
                  indexes=[]
                  
                  MIP(m,customer,arc_C,r,i,k,s)
                  m.optimize()
                  X,y,t,T=m.__data

                  #X,y,t,T=m.__data
                  print 'try',r,i,k,s,X[r,i-1,i,k,s]


#让每组里面最大的X变为【0,1】变量

                     

