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
    for row in customer:
            for i in node:
                    if i==0:
                            continue
                    else:
                        for k in modes:
                            for s in range(len(departure)):
                                X[int(row[0]),i-1,i,k,s]=m.addVar(obj=arc_trans_cost[int(row[0]),i-1,i,k],vtype='C',name='X_%s_%s_%s_%s'%(int(row[0]),i,k,s))
    m.update()                
                        
    #decision variable y: binary variable of 3PL
    y={}
    for row in customer:
        #print row
        y[int(row[0])]=m.addVar(obj=F*int(row[2]),vtype='C',name='y_%s'%(int(row[0])))     
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
            expr = LinExpr()       
            for k in modes:
                    for s in range(len(departure)):
                            expr.addTerms(1.0,X[int(row[0]),0,1,k,s])
            expr.add(y[int(row[0])])
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
                                        expr1.addTerms(1.0,X[int(row[0]),i,i+1,k,s])
                        m.addConstr(expr, GRB.EQUAL, expr1,name='middlePointOne_%s'%(int(row[0])))
                                      
                                
    #constraint 3.4 arc capacity,这个条件没有什么用了，X可以为小数。
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
    ###constraint 3.4 arc capacity Two,这个是新加的条件，为了让LP出来的解feasible,这个条件很重要！！！
    for row in customer:
            for i in node:
                    if i==4:
                            continue
                    else:
                        for k in modes:
                            for s in range(len(departure)):
                                    if int(row[2])>max_arc_C:
                                             m.addConstr(X[int(row[0]),i,i+1,1,s],GRB.EQUAL,0,'ARCCAPACITY1_%s'%(int(row[0])))
                                             m.addConstr(X[int(row[0]),i,i+1,2,s],GRB.EQUAL,0,'ARCCAPACITY2_%s'%(int(row[0])))
                                             m.addConstr(X[int(row[0]),i,i+1,3,s],GRB.EQUAL,0,'ARCCAPACITY3_%s'%(int(row[0])))
                                             m.addConstr(X[int(row[0]),i,i+1,4,s],GRB.EQUAL,0,'ARCCAPACITY4_%s'%(int(row[0])))

                                    if int(row[2])>400:
                                            m.addConstr(X[int(row[0]),i,i+1,1,s],GRB.EQUAL,0,'ARCCAPACITY5_%s'%(int(row[0])))
                                            m.addConstr(X[int(row[0]),i,i+1,3,s],GRB.EQUAL,0,'ARCCAPACITY6_%s'%(int(row[0])))
                                            m.addConstr(X[int(row[0]),i,i+1,4,s],GRB.EQUAL,0,'ARCCAPACITY7_%s'%(int(row[0])))

                                    if int(row[2])>300:
                                            m.addConstr(X[int(row[0]),i,i+1,1,s],GRB.EQUAL,0,'ARCCAPACITY8_%s'%(int(row[0])))
                                            m.addConstr(X[int(row[0]),i,i+1,4,s],GRB.EQUAL,0,'ARCCAPACITY9_%s'%(int(row[0])))

                                    if int(row[2])>100:
                                            m.addConstr(X[int(row[0]),i,i+1,4,s],GRB.EQUAL,0,'ARCCAPACITY10_%s'%(int(row[0])))                                                
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
                            expr.add(-1*y[int(row[0])]*M)
                            m.addConstr(expr,GRB.LESS_EQUAL,t[int(row[0]),i],name='timeConstr_%s_%s'%(int(row[0]),i))                        
    m.update()                    

    #constraint 3.6
    for row in customer:        
            for i in node:
                    
                    expr1 = LinExpr()
                    if i==0 or i==4:
                            continue
                    else:
                            for k in modes:
                                    for s in range(len(departure)):
                                            
                                            expr1.addTerms(dT[i,i+1,k,s],X[int(row[0]),i,i+1,k,s])
                            
                           
                            m.addConstr(expr1,GRB.GREATER_EQUAL,t[int(row[0]),i],name='timeConstr_%s_%s'%(int(row[0]),i))

    m.update()
    nothing=0
    ###constraint 3.7 time constraint Three, tardiness time 只跟最后一个t[n,4]有关， 不用联系
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
cus_move=[]
def update_cus(cus_arr,arc_arr,move_index):#move_index 是临时变量，计算机怎么知道指代哪个？
    for i in node:
        if i==4:
            continue
        else:
            for k in modes:
                for s in range(len(departure)):                
                    if X_move[move_index,i,i+1,k,s]==1:                    
                        arc_arr[i,i+1,k,s]=arc_arr[i,i+1,k,s]-int(cus_arr[move_index][2])
                    
    del cus_arr[move_index]
    return (cus_arr,arc_arr)
mmm=0
#print mmm, len(customer)

####################################################################################################
#while 语句开始，循环开始
while len(customer)>1:
    #print mmm
    mmm+=1
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
    for row in customer:
            print 'Customer',int(row[0]),'Destination ',row[1], 'quantity ',int(row[2]),'DD',int(row[3])
    print '\n'
    #print '\n'
    #第一步，print出来所有大于0的X
    print 'LP relaxation X'                                                
    for row in customer:
                    for i in node:
                        if i==4:
                                continue
                        else:
                             for k in modes:
                                    for s in range(len(departure)):
                                            if X[int(row[0]),i,i+1,k,s].x > 0:
                                                    print 'n',int(row[0]),'node',i,i+1,'k',k,'s',s,X[int(row[0]),i,i+1,k,s].x
    print '\n'
    #第二步，找出4个X都大于0.9的customer
    X_move={}#把X赋值给新的X_move，以后只要看X_move
    X_move_cus_temple={}
    move_index=0
    for row in customer:
        for k in modes:
            for s in range(len(departure)):
                if X[int(row[0]),0,1,k,s].x>=0.6 and X[int(row[0]),1,2,k,s].x>=0.6 and X[int(row[0]),2,3,k,s].x>=0.6 and X[int(row[0]),3,4,k,s].x>=0.6:
                    X_move[int(row[0]),0,1,k,s]=X_move[int(row[0]),1,2,k,s]=X_move[int(row[0]),2,3,k,s]=X_move[int(row[0]),3,4,k,s]=1
                    #cus_move_cost=
                    X_move_cus_temple=move_index
                    print 'index',move_index
                    cus_move.append(row[0])
                    #print 'move customer',X_move_cus_temple
                else:
                    X_move[int(row[0]),0,1,k,s]=X_move[int(row[0]),1,2,k,s]=X_move[int(row[0]),2,3,k,s]=X_move[int(row[0]),3,4,k,s]=0
        move_index+=1
    #print X_move            
    #第三步，update customer，kick it out
    #print customer[X_move_cus_temple][2]
    #print X_move_cus_temple
    (customer,arc_C)=update_cus(customer,arc_C,X_move_cus_temple)

#while 语句结束，customer里面只剩一个customer
####################################################################################################
#手工给最后一个customer赋值
##LP(m,customer,arc_C)
##m.optimize()
##X,y,t,T=m.__data
##print '\n'
##print 'customer basic infomation'
##for row in customer:
##        print 'Customer',int(row[0]),'Destination ',row[1], 'quantity ',int(row[2]),'DD',int(row[3])
##print '\n'
##print 'LP relaxation X'                                                
##for row in customer:
##                for i in node:
##                    if i==4:
##                            continue
##                    else:
##                         for k in modes:
##                                for s in range(len(departure)):
##                                        if X[int(row[0]),i,i+1,k,s].x > 0:
##                                                print 'n',int(row[0]),'node',i,i+1,'k',k,'s',s,X[int(row[0]),i,i+1,k,s].x
####X_temple={}
##for i in node:
##    if i==4:
##        continue
##    else:
##        for k in modes:
##            for s in range(len(departure)):
##                if X[int(row[0]),i,i+1,k,s].x > 0:
##                    if X[int(row[0]),i,i+1,k,s].x>X_temple[int(row(0)),i,i+1]:
##                        X_temple=X[int(row[0]),i,i+1,k,s].x
                    
