#file name 021115.py  在12.21 彻底不要i  
import sys
sys.path.append('C:/gurobi600/win32/python27/lib/gurobipy')  # for apple
#sys.path.append('C:/gurobi562/win64/python27/lib/gurobipy')   # for windows
from gurobipy import *
from read1028 import *
import time   
start_time=time.clock()
m = Model('MIP')
M=1000000000
F=10000000
example=[]
example_y=[]
def MIP(m,customer,arc_C,r_bi,k_bi,s_bi):
    r_try=0
    j_try=0
    k_try=0
    s_try=0
    #decision variable X for arc 0-1: binary variable. X[customer,i,i+1,m,k]
    X1 = {}
    for row in customer:
        for k in modes:
            for s in range(len(departure)):
                X1[int(row[0]),k,s]=m.addVar(obj=arc_trans_cost[int(row[0]),0,1,k],vtype=GRB.BINARY,name='X1_%s_%s_%s'%(int(row[0]),k,s))
    m.update()
    #decision variable X for arc 1-2: binary variable. X[customer,i,i+1,m,k]
    X2 = {}
    for row in customer: 
        for k in modes:
            for s in range(len(departure)):
                X2[int(row[0]),k,s]=m.addVar(obj=arc_trans_cost[int(row[0]),1,2,k],vtype='C',name='X2_%s_%s_%s'%(int(row[0]),k,s))
    m.update()
    #example constraint
    for (row,k,s) in example:
        m.addConstr(X2[int(row),k,s], GRB.EQUAL, 1,name='One_%s3'%(int(row)))
    
    #decision variable y: binary variable of 3PL
    y={}
    for row in customer:
        y[int(row[0])]=m.addVar(obj=F*int(row[2]),vtype=GRB.BINARY,name='y_%s'%(int(row[0])))     
    m.update()
    #example_y constraint
    for row in example_y:
        m.addConstr(y[int(row[0])],GRB.EQUAL,1,name='one_y%s'%(int(row[0])))
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

    #Constraint 3.2 for each customer, only one plan can be selected
    for row in customer:
        expr = LinExpr()       
        for k in modes:
                for s in range(len(departure)):
                        expr.addTerms(1.0,X1[int(row[0]),k,s])
        expr.add(y[int(row[0])])
        m.addConstr(expr, GRB.EQUAL, 1,name='One_%s'%(int(row[0])))
    m.update()
    #Constraint 3.3, in the middlepoint, In = Out
    for row in customer:
        expr = LinExpr()
        expr1 = LinExpr()
        for k in modes:
            for s in range(len(departure)):
                expr.addTerms(1.0,X1[int(row[0]),k,s])
                expr1.addTerms(1.0,X2[int(row[0]),k,s])
        m.addConstr(expr, GRB.EQUAL, expr1,name='middlePointOne_%s'%(int(row[0])))                                                              
    #constraint 3.4 arc capacity.
    for k in modes:
        for s in range(len(departure)):
            expr = LinExpr()
            for row in customer:
                expr.addTerms(int(row[2]),X1[int(row[0]),k,s])
            expr.addConstant(-1*arc_C[0,1,k,s])
            m.addConstr(expr,GRB.LESS_EQUAL, 0,'arcCapacity1_%s_%s_%s'%(int(row[0]),k,s))      
    m.update()
    for k in modes:
        for s in range(len(departure)):
            expr = LinExpr()
            for row in customer:
                expr.addTerms(int(row[2]),X2[int(row[0]),k,s])
            expr.addConstant(-1*arc_C[1,2,k,s])
            m.addConstr(expr,GRB.LESS_EQUAL, 0,'arcCapacity2_%s_%s_%s'%(int(row[0]),k,s))       
    m.update()
    #constraint 3.5 time constraint One
    for row in customer:
        for i in node:
                expr = LinExpr()                
                if i==0 or i==2:  #这里其实i=1
                        continue
                else:
                        for k in modes:
                                for s in range(len(departure)):                                            
                                        expr.addTerms(dT[i-1,i,k,s]+trans_time[i-1,i,k],X1[int(row[0]),k,s])
                        expr.add(-1*y[int(row[0])]*M)
                        m.addConstr(expr,GRB.LESS_EQUAL,t[int(row[0]),i],name='timeConstr_%s_%s'%(int(row[0]),i))                            
    m.update()
    for row in customer:
        for i in node:
                expr = LinExpr()                
                if i==0 or i==1:#这里其实i=2
                        continue
                else:
                        for k in modes:
                                for s in range(len(departure)):                                            
                                        expr.addTerms(dT[i-1,i,k,s]+trans_time[i-1,i,k],X2[int(row[0]),k,s])
                        expr.add(-1*y[int(row[0])]*M)
                        m.addConstr(expr,GRB.LESS_EQUAL,t[int(row[0]),i],name='timeConstr_%s_%s'%(int(row[0]),i))
    m.update()
    #constraint 3.6 time constraint Two, 新一期的出发时间大于上一期的到达时间
    for row in customer:
        for i in node:                    
                expr1 = LinExpr()
                if i==0 or i==2:#这里其实i=1
                        continue
                else:
                        for k in modes:
                                for s in range(len(departure)):                                            
                                        expr1.addTerms(dT[i,i+1,k,s],X2[int(row[0]),k,s])                          
                        m.addConstr(expr1,GRB.GREATER_EQUAL,t[int(row[0]),i],name='timeConstr_%s_%s'%(int(row[0]),i))
    m.update()
    nothing=0
    ###constraint 3.7 time constraint Three, tardiness time 只跟最后一个t[n,2]有关
    for row in customer:
        for k in modes:
                for s in range(len(departure)):
                        if X2[int(row[0]),k,s]>0:
                                if t[int(row[0]),2]>int(row[3]):                                        
                                        m.addConstr(T[int(row[0])],GRB.EQUAL,t[int(row[0]),2]-int(row[3]),name='Tardiness_%s'%(int(row[0])) )
                                else:
                                        nothing=nothing+1#这里其实什么也不需要做
    m.update()
    m.__data=X1,X2,y,t,T
    return m
# first step, print basic info 
print "\n"
print 'Basic info'
print 'total number of customer', len(customer)
print 'mode_1, Truck' 
print 'mode_2, Rail'
print 'mode_3, HighSpeed Rail' 
print 'mode_4, Air'
for row in customer:
    print 'Customer',int(row[0]),'Destination ',row[1], 'quantity ',int(row[2]),'DD',int(row[3])
print '\n'
##move_set=[]
##move_index_set=[]
##new_transport_cost=0
index1=0
index2=0
while index1 != len(customer)-index2:
    (r_bi,k_bi,s_bi)=(100,100,100)
    #mmm+=1 
    MIP(m,customer,arc_C,r_bi,k_bi,s_bi)
    m.optimize()
    X1,X2,y,t,T=m.__data
    print "\n"
    #print t[n,4].x
##    threePLCost=0
##    TransCost=0
##    TotalTransCost=0
##    TotalTardinessCost=0
##    TotalCost=0
##    highest_X={}
    new_X={}            
    new_y={}

# second step, print X1 and X2  
    print 'Summary solution'
    print '\n'
    if m.status == GRB.status.OPTIMAL:
            for row in customer:
                if y[int(row[0])].x>0 and int(row[0]) not in example_y:
                    index2+=1
                    b=[]
                    b.append(int(row[0]))
                    example_y.append(b)
                    b=[]
                    #print 'example###############################################','example_y',example_y
                    print 'Customer',int(row[0]),' using 3PL','Trans_cost',F
                for k in modes:
                        for s in range(len(departure)):
                                if X1[int(row[0]),k,s].x > 0:
                                    print 'Customer',int(row[0]),'arc',0,1,'arc_mode_num',k,'departureNum',s+1,'X1',X1[int(row[0]),k,s].x#'Tardiness',T[int(row[0])].x,'start_Time',dT[0,1,k,s],'Ending_time',t[int(row[0]),2].x,
                                    #print 'int(row[2])',int(row[2])
                                    #capacity_left[0,1,k,s]=capacity_left[0,1,k,s]-X1[int(row[0]),k,s].x*int(row[2])
                                if X2[int(row[0]),k,s].x > 0:
                                    print 'Customer',int(row[0]),'arc',1,2,'arc_mode_num',k,'departureNum',s+1,'X2',X2[int(row[0]),k,s].x
                                if X2[int(row[0]),k,s].x==1 and [int(row[0]),k,s] not in example:
                                    index1+=1
                                    #print '################################','index1',index1
                                    a=[]
                                    a.append(int(row[0]))
                                    a.append(k)
                                    a.append(s)#,i_try,k_try,s_try)
                                    example.append(a)
                                    a=[]                         
    
    print 'index1',index1
    print 'index2',index2
    print '\n'
    #print 'capacity_left', capacity_left
    node_arc=[]

    for k in modes:
        for s in range(len(departure)):                
            for row in customer:
                if [int(row[0]),k,s] not in example and X2[int(row[0]),k,s].x>0:
                    arr=str([int(row[0]),k,s])  #把他们看成一个str
                    arrr=[]
                    arrr.append(arr)

                    arrr.append(X2[int(row[0]),k,s].x)
                    node_arc.append(arrr)

    if len(node_arc)>0:
      node_arcs=sorted(node_arc, key=lambda x: x[1],reverse=True)
      #这里要先test capacity，不满足，继续下一个
      max_value = node_arcs[0:1]   #??????????????????  如果两个都是0.5
      print 'max_value',max_value
      node_arc=[] #找到了，就归0，下次找就不会出错。
      indexes=[]
      for row in max_value: 
          rows=row[0][1:-1].split(',')
          (r_try,k_try,s_try)=map(int,rows)
          a=[]
          a.append(r_try)
          a.append(k_try)
          a.append(s_try)#,i_try,k_try,s_try)
          example.append(a)
          a=[]
          print 'example###############################################',example
      MIP(m,customer,arc_C,r_try,k_try,s_try)
      m.optimize()
      X1,X2,y,t,T=m.__data
      #move_set.append(max_value)
#print 'move set',move_set



