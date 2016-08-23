#file name 1122.py  在1121的基础上试着改，把改最大的X2 变为改最大的前5个。 目的是为了加快运行速度。

import sys
sys.path.append('C:/gurobi600/win32/python27/lib/gurobipy')

from gurobipy import *
from read1028 import *
import time


    
start_time=time.clock()
m = Model('MIP')
M=1000000000
F=10000000
del_list=[[100,100,100,100,100]]
def MIP(m,customer,arc_C,del_list):
    
    ####################################################################################################
    #decision variable X for arc 0-1: binary variable. X[customer,i,i+1,m,k]
    X1 = {}
    for row in customer:
        if int(row[0]) in customer_id:
            for i in node:
                    if i==0 or i==2:
                            continue
                    else:
                        for k in modes:
                            for s in range(len(departure)):
                                X1[int(row[0]),i-1,i,k,s]=m.addVar(obj=arc_trans_cost[int(row[0]),i-1,i,k],vtype=GRB.BINARY,name='X1_%s_%s_%s_%s'%(int(row[0]),i,k,s))
    m.update()
    #decision variable X for arc 1-2: binary variable. X[customer,i,i+1,m,k]
    X2 = {}
    for row in customer:
        if int(row[0]) in customer_id:
            for i in node:
                    if i==0 or i==1:
                            continue
                    else:
                        for k in modes:
                            for s in range(len(departure)):
                                X2[int(row[0]),i-1,i,k,s]=m.addVar(obj=arc_trans_cost[int(row[0]),i-1,i,k],vtype='C',name='X2_%s_%s_%s_%s'%(int(row[0]),i,k,s))
    m.update()
                        
    #decision variable y: binary variable of 3PL
    y={}
    for row in customer:
        if int(row[0]) in customer_id:
        #print row
            y[int(row[0])]=m.addVar(obj=F*int(row[2]),vtype=GRB.BINARY,name='y_%s'%(int(row[0])))     
    m.update()
    #decision variable: arrive time at each node
    t={}
    for row in customer:
        if int(row[0]) in customer_id:
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
        if int(row[0]) in customer_id:
            expr = LinExpr()       
            for k in modes:
                    for s in range(len(departure)):
                            expr.addTerms(1.0,X1[int(row[0]),0,1,k,s])
            expr.add(y[int(row[0])])
            m.addConstr(expr, GRB.EQUAL, 1,name='One_%s'%(int(row[0])))
    m.update()
    ####################################################################################################
    #Constraint 3.3, in the middlepoint, In = Out
    for row in customer:
        if int(row[0]) in customer_id:
            expr = LinExpr()
            expr1 = LinExpr()
            for k in modes:
                for s in range(len(departure)):
                    expr.addTerms(1.0,X1[int(row[0]),0,1,k,s])
                    expr1.addTerms(1.0,X2[int(row[0]),1,2,k,s])
            m.addConstr(expr, GRB.EQUAL, expr1,name='middlePointOne_%s'%(int(row[0])))                                                              
    #constraint 3.4 arc capacity
    for k in modes:
        for s in range(len(departure)):
            for i in node:
                    if i==0 or i==2:
                            continue
                    else:
                            expr = LinExpr()
                            for row in customer:
                                if int(row[0]) in customer_id:
                                    expr.addTerms(int(row[2]),X1[int(row[0]),i-1,i,k,s])
                            expr.addConstant(-1*arc_C[i-1,i,k,s])
                            m.addConstr(expr,GRB.LESS_EQUAL, 0,'arcCapacity_%s_%s_%s_%s'%(int(row[0]),i,k,s))      
    m.update()
    for k in modes:
        for s in range(len(departure)):
            for i in node:
                    if i==0 or i==1:
                            continue
                    else:
                            expr = LinExpr()
                            for row in customer:
                                if int(row[0]) in customer_id:
                                    expr.addTerms(int(row[2]),X2[int(row[0]),i-1,i,k,s])
                            expr.addConstant(-1*arc_C[i-1,i,k,s])
                            m.addConstr(expr,GRB.LESS_EQUAL, 0,'arcCapacity_%s_%s_%s_%s'%(int(row[0]),i,k,s))      
    m.update()
    #constraint 3.5 time constraint One
    for row in customer:
        if int(row[0]) in customer_id:
            for i in node:
                    expr = LinExpr()                
                    if i==0 or i==2:
                            continue
                    else:
                            for k in modes:
                                    for s in range(len(departure)):                                            
                                            expr.addTerms(dT[i-1,i,k,s]+trans_time[i-1,i,k],X1[int(row[0]),i-1,i,k,s])
                            expr.add(-1*y[int(row[0])]*M)
                            m.addConstr(expr,GRB.LESS_EQUAL,t[int(row[0]),i],name='timeConstr_%s_%s'%(int(row[0]),i))                            
    m.update()
    for row in customer:
        if int(row[0]) in customer_id:
            for i in node:
                    expr = LinExpr()                
                    if i==0 or i==1:
                            continue
                    else:
                            for k in modes:
                                    for s in range(len(departure)):                                            
                                            expr.addTerms(dT[i-1,i,k,s]+trans_time[i-1,i,k],X2[int(row[0]),i-1,i,k,s])
                            expr.add(-1*y[int(row[0])]*M)
                            m.addConstr(expr,GRB.LESS_EQUAL,t[int(row[0]),i],name='timeConstr_%s_%s'%(int(row[0]),i))
    m.update()
    #constraint 3.6 time constraint Two, 新一期的出发时间大于上一期的到达时间
    for row in customer:
        if int(row[0]) in customer_id:
            for i in node:                    
                    expr1 = LinExpr()
                    if i==0 or i==2:
                            continue
                    else:
                            for k in modes:
                                    for s in range(len(departure)):                                            
                                            expr1.addTerms(dT[i,i+1,k,s],X2[int(row[0]),i,i+1,k,s])                          
                            m.addConstr(expr1,GRB.GREATER_EQUAL,t[int(row[0]),i],name='timeConstr_%s_%s'%(int(row[0]),i))

    m.update()
    nothing=0
    ###constraint 3.7 time constraint Three, tardiness time 只跟最后一个t[n,2]有关
    for row in customer:
        if int(row[0]) in customer_id:
            for k in modes:
                    for s in range(len(departure)):
                            if X2[int(row[0]),1,2,k,s]>0:
                                    if t[int(row[0]),2]>int(row[3]):                                        
                                            m.addConstr(T[int(row[0])],GRB.EQUAL,t[int(row[0]),2]-int(row[3]),name='Tardiness_%s'%(int(row[0])) )
                                    else:
                                            nothing=nothing+1#这里其实什么也不需要做
    m.update()
    m.__data=X1,X2,y,t,T
    return m
####################################################################################################
cus_move=[]
def update_cus(cus_arr,arc_arr,del_list):#move_index 是临时变量，计算机怎么知道指代哪个？()里面的是变量
    #print i,k,s       
    for row in del_list:
        (r,j,i,k,s)=row
        index_g=r        
        arc_arr[i-1,i,k,s]=arc_arr[i-1,i,k,s]-int(cus_arr[r][2])
        del customer_id[index_g]
    #global_index.index([r,i])
        print index_g,'index...........'
    return (cus_arr,arc_arr)
mmm=0
################################################################################
##global_index=[]
##for row in customer:
##    global_index.append([int(row[0]),1])#?????????这里对不对？
# first step, print basic info 
print "\n"
print 'Basic info'
print 'total number of customer', len(customer)
print "\n"
##    #print 'arc 0-1:','SC-WH ','arc 1-2:','WH-ZZ'
##    for row in customer:
##        print 'Customer',int(row[0]),'Destination ',row[1], 'quantity ',int(row[2]),'DD',int(row[3])
##    print "\n"
move_set=[]
move_index_set=[]
new_transport_cost=0
while len(customer_id)>1:
    #print len(global_index),'global length...........................................'
    (r_bi,i_bi,k_bi,s_bi)=(100,100,100,100) #??????????这里是什么意思， 原来
    mmm+=1
    MIP(m,customer,arc_C,del_list)
    m.optimize()
    X1,X2,y,t,T=m.__data

    print "\n"
    #print t[n,4].x
    threePLCost=0
    TransCost=0
    TotalTransCost=0
    TotalTardinessCost=0
    TotalCost=0
    highest_X={}
    new_X={}            
    new_y={}


# second step, print X1 and X2  
    print 'Summary solution'
    
    if m.status == GRB.status.OPTIMAL:
            for row in customer:
                if int(row[0]) in customer_id:
                    if y[int(row[0])].x>0:
                            print 'Customer',int(row[0]),' using 3PL','Trans_cost',F
                            threePLCost+=F
                            
                    for k in modes:
                            for s in range(len(departure)):
                                    if X1[int(row[0]),0,1,k,s].x > 0:
                                        #print 'X1',X1[int(row[0]),0,1,k,s].x
                                        print 'Customer',int(row[0]),'arc',0,1,'arc_mode_num',k,'departureNum',s+1,'X1',X1[int(row[0]),0,1,k,s].x#'Tardiness',T[int(row[0])].x,'start_Time',dT[0,1,k,s],'Ending_time',t[int(row[0]),2].x,
                                        TotalTardinessCost+=T[int(row[0])].x*int(row[4])
                                    if X2[int(row[0]),1,2,k,s].x > 0:
                                        print 'Customer',int(row[0]),'arc',1,2,'arc_mode_num',k,'departureNum',s+1,'X2',X2[int(row[0]),1,2,k,s].x
                                           
    print '\n'
    print 'Solution detail'        
    
    for row in customer:
        if int(row[0]) in customer_id:
            for k in modes:
                for s in range(len(departure)):
                    if X1[int(row[0]),0,1,k,s].x > 0:
                        print 'Customer',int(row[0]),'arc',0,1,'arc_mode_num',k,'departureNum',s+1,'arc_cost',arc_trans_cost[int(row[0]),0,1,k],'start_Time',dT[0,1,k,s],'Trans_time',trans_time[0,1,k],'Ending_Time',t[int(row[0]),1].x
                        TransCost+=arc_trans_cost[int(row[0]),0,1,k]
                    if X2[int(row[0]),1,2,k,s].x > 0:
                        print 'Customer',int(row[0]),'arc',1,2,'arc_mode_num',k,'departureNum',s+1,'arc_cost',arc_trans_cost[int(row[0]),1,2,k],'start_Time',dT[1,2,k,s],'Trans_time',trans_time[1,2,k],'Ending_Time',t[int(row[0]),2].x
                        TransCost+=arc_trans_cost[int(row[0]),1,2,k]
                #print '\n'
    TotalTransCost=TransCost+threePLCost
    TotalCost=  TotalTardinessCost+   TotalTransCost 
    print '\n'
    print 'Trans_Cost',TransCost
    print '3PL_Cost',threePLCost
    print 'Total_Trans_Cost',TotalTransCost
    print 'Total_Penalty_Cost',TotalTardinessCost
    print 'Total_Cost',TotalCost
    print '\n'
# third step, pick biggest X2

    node_arc=[]
    indexes=[]
    LPlist=[]
    for i in node:
        if i==0: #?？？？？？？？？？这里是不是可以不要？
            continue
        else:
            for k in modes:
                for s in range(len(departure)):                
                    for row in customer:
                        if int(row[0]) in customer_id:
                        #print i,k,s,X[int(row[0]),i-1,i,k,s].x
                            if X2[int(row[0]),1,2,k,s].x > 0:  # 从这里开始重点改， 改为前五个值。
                                #LPlist.append(X2[int(row[0]),1,2,k,s].x)
                                #A=sorted（LPlist,reverse=True）
                                
                                #print 'arc',i-1,i,'k',k,'s',s,'customer',row[0],X[int(row[0]),i-1,i,k,s].x
                                #print i-1,i,k,s,X[int(row[0]),i-1,i,k,s].x
                                arr=str([int(row[0]),i-1,i,k,s])  #? 这部有什么用
                                arrr=[]
                                arrr.append(arr)
                                #print arr
                                arrr.append(X2[int(row[0]),1,2,k,s].x)
                                node_arc.append(arrr)
                                indexes.append([int(row[0]),i,k,s])
                                #print sorted(node_arc)[0:5]
                                
                            #print node_arc
                            #print 'test',indexes[0]
                    #sort(node_arc[i-1,i,k,s])
    #print node_arc,'node_arc'
    if len(node_arc)>0:
      #print node_arc,'before'
      node_arcs=sorted(node_arc, key=lambda x: x[1],reverse=True)
      #print node_arcs,'end'                
      max_value = node_arcs[0:2]      
      print 'max value',max_value      
      node_arc=[]
      indexes=[]
      del_list=[]
      for row in max_value:
          rows=row[0][1:-1].split(',')
          del_row=map(int,rows)
          del_list.append(del_row)
          #print 'del_list',del_list         
      MIP(m,customer,arc_C,del_list)
      m.optimize()
      X1,X2,y,t,T=m.__data
      move_set.append(max_value)
      (customer,arc_C)=update_cus(customer,arc_C,del_list)
##                      print len(global_index)
##                      print arc_C

                      #X,y,t,T=m.__data
                      #print 'try',r,i,k,s,X[r,i-1,i,k,s]
    #print arc_C
 

print 'move_set',move_set

