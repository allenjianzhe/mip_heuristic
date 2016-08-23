#file name netflow0715H.py
import sys
sys.path.append('C:/gurobi562/win64/python27/lib/gurobipy')

from gurobipy import *
from read0804 import *
import time


start_time=time.clock()
m = Model('LP_relaxation')
M=1000000000
F=10000000
def LP(m,customer,arc_C):
    ####################################################################################################
    #decision variable X: binary variable. X[customer,i,i+1,m,k]
    X = {}
    ##X_up={}
    ##X_down={}
    ##for n in range(len(customer)):
    ##        for i in node:
    ##                if i==0:
    ##                        continue
    ##                else:
    ##                    for k in modes:
    ##                        for s in range(len(departure)):
    ##                                X_down[n,i-1,i,k,s]=0
    ##                                X_up[n,i-1,i,k,s]=1
    for n in range(len(customer)):
            for i in node:
                    if i==0:
                            continue
                    else:
                        for k in modes:
                            for s in range(len(departure)):
                                X[n,i-1,i,k,s]=m.addVar(obj=arc_trans_cost[n,i-1,i,k],vtype='C',name='X_%s_%s_%s_%s'%(n,i,k,s))
    m.update()                
                        
    #decision variable y: binary variable of 3PL
    y={}
    for n in range(len(customer)):
            y[n]=m.addVar(obj=F*quantity[n],vtype='C',name='y_%s'%(n))     
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
                                      
                                
    #constraint 3.4 arc capacity,这个条件没有什么用了，X可以为小数。
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
    ###constraint 3.4 arc capacity Two,这个是新加的条件，为了让LP出来的解feasible,这个条件很重要！！！
    for n in range(len(customer)):
            for i in node:
                    if i==4:
                            continue
                    else:
                        for k in modes:
                            for s in range(len(departure)):
                                    if quantity[n]>max_arc_C:
                                             m.addConstr(X[n,i,i+1,1,s],GRB.EQUAL,0,'ARCCAPACITY1_%s'%(n))
                                             m.addConstr(X[n,i,i+1,2,s],GRB.EQUAL,0,'ARCCAPACITY2_%s'%(n))
                                             m.addConstr(X[n,i,i+1,3,s],GRB.EQUAL,0,'ARCCAPACITY3_%s'%(n))
                                             m.addConstr(X[n,i,i+1,4,s],GRB.EQUAL,0,'ARCCAPACITY4_%s'%(n))

                                    if quantity[n]>400:
                                            m.addConstr(X[n,i,i+1,1,s],GRB.EQUAL,0,'ARCCAPACITY5_%s'%(n))
                                            m.addConstr(X[n,i,i+1,3,s],GRB.EQUAL,0,'ARCCAPACITY6_%s'%(n))
                                            m.addConstr(X[n,i,i+1,4,s],GRB.EQUAL,0,'ARCCAPACITY7_%s'%(n))

                                    if quantity[n]>300:
                                            m.addConstr(X[n,i,i+1,1,s],GRB.EQUAL,0,'ARCCAPACITY8_%s'%(n))
                                            m.addConstr(X[n,i,i+1,4,s],GRB.EQUAL,0,'ARCCAPACITY9_%s'%(n))

                                    if quantity[n]>100:
                                            m.addConstr(X[n,i,i+1,4,s],GRB.EQUAL,0,'ARCCAPACITY10_%s'%(n))                                                
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
    m.__data=X,y,t,T
    return m


####################################################################################################
LP(m,customer,arc_C)
m.optimize()
X,y,t,T=m.__data

print "\n"
#print t[n,4].x
TotalTardinessCost=0
Total3PLcost=0
highest_X={}


new_X={}            
new_y={}
print 'customer basic infomation'
for n in range(len(customer)):
        print 'Customer',n+1,'Destination ',Destination[n], 'quantity ',quantity[n],'DD',DD[n]
print '\n'
#print 'new solution check y first'
#先把明显的y分离出来，若quantity[n]>max arc_capacity, 让new_y[n]=1. 这个不需要， 超出arc capacity没有意思， 所以肯定是要符合arc capacity的才行
##for n in range(len(customer)):
##        if quantity[n]>max_arc_C:
##                new_y[n]=1        
##                print 'no current mode is satisfy for customer',n+1,'3PL will be chosen'
##        else:
##                new_y[n]=0
##                #print 'no customer chose 3PL'
##                for i in node:
##                        if i==4:
##                                continue
##                        else:
##                                for k in modes:
##                                        for s in range(len(departure)):
##                                                new_X[n,i,i+1,k,s]=0
#以上的步骤肯定没有问题，接下的步骤要想清楚！
####################################################################################################
#print initial LP X
#要把每个n对应的X都存起来，X不为0肯定有它的道理，先根据arc capacity过滤一次。
#print '\n'                                                
print 'LP relaxation X'                                                
for n in range(len(customer)):
##        if new_y[n]==1:
##                continue
##        else:
                for i in node:
                    if i==4:
                            continue
                    else:
                         for k in modes:
                                for s in range(len(departure)):
                                        if X[n,i,i+1,k,s].x > 0:
                                                print 'n',n+1,'node',i,i+1,'k',k,'s',s,X[n,i,i+1,k,s].x
print '\n'

#第一步， 把X=1的先选出来
for n in range(len(customer)):
    for i in node:
        if i==4:
            continue
        else:
            for k in modes:
                for s in range(len(departure)):
                    if X[n,i,i+1,k,s].x==1:
                        print 'n',n+1,'node',i,i+1,'k',k,'s',s,X[n,i,i+1,k,s].x
print '\n'
#第二步，找出4个X都是1的customer
X_move={}
X_move_cus_temple={}
for n in range(len(customer)):
    for k in modes:
        for s in range(len(departure)):
            if X[n,0,1,k,s].x==X[n,1,2,k,s].x==X[n,2,3,k,s].x==X[n,3,4,k,s].x==1:
                X_move[n,0,1,k,s]=X_move[n,1,2,k,s]=X_move[n,2,3,k,s]=X_move[n,3,4,k,s]=1
                X_move_cus_temple=n
                print 'n',n+1
            else:
                X_move[n,0,1,k,s]=X_move[n,1,2,k,s]=X_move[n,2,3,k,s]=X_move[n,3,4,k,s]=0
#print X_move            
#第三步，update customer，kick it out
del customer[X_move_cus_temple]
print customer
for n in range(len(customer)):
        print 'Customer',n+1,'Destination ',Destination[n], 'quantity ',quantity[n],'DD',DD[n]
#第四步，update arc_capacity
##print 'arc_C[0,1,2,1]',arc_C[0,1,2,1]
##print 'quantity[0]',quantity[0]
##print 'X_move[0,0,1,2,1]',X_move[0,0,1,2,1]

for i in node:
    if i==4:
        continue
    else:
        for k in modes:
            for s in range(len(departure)):
                if X_move[X_move_cus_temple,i,i+1,k,s]==1:
                    #print 'X_move_cus_temple',X_move_cus_temple+1,'i,i+1',i,i+1,'k',k,'s',s,'X_move'
                    arc_C[i,i+1,k,s]=arc_C[i,i+1,k,s]-quantity[X_move_cus_temple]
                    #arc_C[i,i+1,k,s]=temple
##print 'arc_C[0,1,2,1]',arc_C[0,1,2,1]
##print 'arc_C[1,2,2,1]',arc_C[1,2,2,1]
##print 'arc_C[2,3,2,1]',arc_C[2,3,2,1]
##print 'arc_C[3,4,2,1]',arc_C[3,4,2,1]

#第五步，把updated后的数据再导入函数，再run一次.??????????
LP(m,customer,arc_C)                    
m.optimize()
X,y,t,T=m.__data
print 'customer basic infomation'
for n in range(len(customer)):
        print 'Customer',n+1,'Destination ',Destination[n], 'quantity ',quantity[n],'DD',DD[n]
print '\n'
print 'LP relaxation X'                                                
for n in range(len(customer)):
                for i in node:
                    if i==4:
                            continue
                    else:
                         for k in modes:
                                for s in range(len(departure)):
                                        if X[n,i,i+1,k,s].x > 0:
                                                print 'n',n+1,'node',i,i+1,'k',k,'s',s,X[n,i,i+1,k,s].x
