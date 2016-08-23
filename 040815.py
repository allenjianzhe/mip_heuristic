#040815.py based on 031015. try to fix X1 too. 
import sys
import math
sys.path.append('C:/gurobi600/win32/python27/lib/gurobipy')  # for apple
#sys.path.append('C:/gurobi562/win64/python27/lib/gurobipy')   # for windows
from gurobipy import *
from read041415 import *
import time   
start_time=time.clock()
m = Model('MIP')
M=1000000000
F=3000000
example_x2_1=[]
example_x2_0=[]
example_x1=[]
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
    #example constraint for all X1=1
    for (row,k,s) in example_x1:
        m.addConstr(X1[int(row),k,s],GRB.EQUAL,1,name='OneX1_%s'%(int(row)))
    #example constraint for all X2=1
    for (row,k,s) in example_x2_1:
        m.addConstr(X2[int(row),k,s], GRB.EQUAL, 1,name='Onex2_%s3'%(int(row)))
    #example constraint for all X2=0
    for (row,k,s) in example_x2_0:
        m.addConstr(X2[int(row),k,s], GRB.EQUAL, 0,name='One_%s3'%(int(row)))
    
    #decision variable y: binary variable of 3PL
    y={}
    for row in customer:
        y[int(row[0])]=m.addVar(obj=F,vtype=GRB.BINARY,name='y_%s'%(int(row[0])))     
    m.update()
    #example_y constraint
    for r in example_y:
        m.addConstr(y[r],GRB.EQUAL,1,name='one_y%s'%(r))
    #decision variable: arrive time at each node
    t={}
    for row in customer:
        for i in node:
                if i==0:        
                        continue
                else:
                        t[int(row[0]),i]=m.addVar(obj=0,vtype=GRB.INTEGER,name='nodeTime_%s_%s'%(int(row[0]),i))  
    #decision variable:Time tardiness of customer
    T={}
    for row in customer:
            T[int(row[0])]=m.addVar(obj=int(row[4]),vtype=GRB.INTEGER,name='Tardiness_%s'%(int(row[0])))
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
                        #expr.add(-1*y[int(row[0])]*M)
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
                        #expr.add(-1*y[int(row[0])]*M)
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
                        if X2[int(row[0]),k,s]>0 and t[int(row[0]),2]>=int(row[3]):
                            m.addConstr(T[int(row[0])],GRB.EQUAL,t[int(row[0]),2]-int(row[3]),name='Tardiness_%s'%(int(row[0])) )
    m.update()
    m.__data=X1,X2,y,t,T
    return m




while len(example_x2_1)+len(example_y) !=len(customer):
    (r_bi,k_bi,s_bi)=(100,100,100)
    MIP(m,customer,arc_C,r_bi,k_bi,s_bi)
    m.optimize()
    #m.computerIIS()
    #m.write('model.ilp')
    X1,X2,y,t,T=m.__data
    #print "\n"
    #print 'Summary solution'
    print '\n'
    if m.status == GRB.status.INFEASIBLE:
        m.computeIIS()
        m.write('mipmodelconstraintError.ilp')
    if m.status == GRB.status.OPTIMAL:
        for row in customer:
            if y[int(row[0])].x>0 and int(row[0]) not in example_y:
                print 'Customer',int(row[0]),' using 3PL','Trans_cost',F
                example_y.append(int(row[0]))
                #print 'example_y',example_y,'###'
                
        #print '\n'
        for row in customer:
            for k in modes:
                for s in range(len(departure)):
                    if X1[int(row[0]),k,s].x > 0: 
                        #print '\n'
                        print 'Customer',int(row[0]),'arc',0,1,'arc_mode_num',k,'departureNum',s+1,'X1',X1[int(row[0]),k,s].x
        #print '\n'
        nothing=0
                        
        for row in customer:
            for k in modes:
                for s in range(len(departure)):
                    if X2[int(row[0]),k,s].x > 0:
                        #print '\n'
                        print 'Customer',int(row[0]),'arc',1,2,'arc_mode_num',k,'departureNum',s+1,'X2',X2[int(row[0]),k,s].x
                    if X2[int(row[0]),k,s].x==1 and [int(row[0]),k,s] not in example_x2_1:
                        a=[]
                        a.append(int(row[0]))
                        a.append(k)
                        a.append(s)
                        example_x2_1.append(a)
                        a=[]
                        print 'example_x2_1',example_x2_1
                        for k in modes:
                            for s in range(len(departure)):
                                if X1[int(row[0]),k,s].x>0:
                                    a=[]
                                    a.append(int(row[0]))
                                    a.append(k)
                                    a.append(s)
                                    example_x1.append(a)
                                    a=[]
                    else:
                        nothing+=1
                    
        print 'example_x1',example_x1
            
                                    
        #print 'example',example, '这是第一次查看example，可能已经有X2=1'    
        #print '\n'

    node_arc=[]
    for k in modes:
        for s in range(len(departure)):                
            for row in customer:
                if X2[int(row[0]),k,s].x>0 and X2[int(row[0]),k,s].x !=1:
                    arr=str([int(row[0]),k,s])
                    arrr=[]
                    arrr.append(arr)
                    arrr.append(X2[int(row[0]),k,s].x)
                    node_arc.append(arrr)
    #print 'node_arc',node_arc 
    if len(node_arc)>0:
      node_arcs=sorted(node_arc, key=lambda x: x[1],reverse=True)
      print '\n'
      print 'node_arcs',node_arcs
      #start to choose X2###############################################in other word, test capacity in the example

      for iks in range(len(node_arcs)):
          max_value=node_arcs[iks]
          #print 'max_value',max_value
          #print '\n'
          a=[]
          rows=max_value[0][1:-1].split(',')
          (r_try,k_try,s_try)=map(int,rows)
          a.append(r_try)
          a.append(k_try)
          a.append(s_try)
          #print 'a',a
          example_x2_1.append(a)
          #print 'example',example, new X2 is in the example now
          p=int(customer[r_try][2])
          #print 'DDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDD'
          #print 'r_try',r_try,'customer[t_try][2]',customer[r_try][2]
          #print 'p','customer[int(max_value[0][1])][2]',customer[r_try][2]
          # we only need to test the capacity for k=k_try and s=s_try
          for (r1,k1,s1) in example_x2_1:
              if k1==k_try and s1==s_try and r1 != r_try:
                  p=p+int(customer[int(r1)][2])
                  #print 'customer[int(r1)][2]',customer[int(r1)][2]
          #print 'p',p,'####'
          if p<=arc_C[0,1,k_try,s_try]:
              p=0 # back to 0 is necessiry
              a=[]
              print 'example_x2_1',example_x2_1,'this time should add one more X2 in the list'
              print 'r_try',r_try
              # here find X2,X1 are not enough, we need to test time constraint
              
              for k in modes:
                  for s in range(len(departure)):
                      if X1[r_try,k,s].x>0:
                          a=[]
                          a.append(r_try)
                          a.append(k)
                          a.append(s)
                          example_x1.append(a)
                          a=[]
                
              print 'example_x1',example_x1,'this time should one more X1 too'  
              #print 'p',p,'arc_C[0,1,k,s]',arc_C[0,1,k_try,s_try]
              break
          else:
              #print 'p',p,'arc_C[0,1,int(max_value[0][4]),int(max_value[0][7])]',arc_C[0,1,k_try,s_try]
              #else means capacity is full
              #back to original, meanwhile we should let this new varilable back to 0 so that next time we would not test again.
              example_x2_0.append(a)
              a=[]
              rr=r_try
              max_value=[]
              del example_x2_1[-1]
              p=0
              continue
      if max_value==[]:
          example_y.append(rr)
          print 'example_y',example_y
          a=[]
      else:
          node_arc=[]
          #到这里，已经选完，要改max_value#############################################
          max_value=[]
      
##    else:
##        print 'all variables are 1'
    
    
#MIP(m,customer,arc_C,r_try,k_try,s_try)
#m.optimize()
#X1,X2,y,t,T=m.__data      
      

        
  
#全部结束以后，再打印一遍
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

ThirdPartyTransCost=0
X1TransCost=0
X2TransCost=0
TardinessCost=0
if m.status == GRB.status.OPTIMAL:
        for row in customer:
            if y[int(row[0])].x==1:
                print 'Customer',int(row[0]),' using 3PL','Trans_cost',F
                ThirdPartyTransCost+=F
        #print '\n'
        for row in customer:
            for k in modes:
                for s in range(len(departure)):
                    if X1[int(row[0]),k,s].x ==1:
                        print 'Customer',int(row[0]),'arc',0,1,'arc_mode_num',k,'departureNum',s+1,'X1',X1[int(row[0]),k,s].x,'StartTime',dT[0,1,k,s],'TransTime',trans_time[0,1,k],'endingTime',t[int(row[0]),1].x,'TransCost',arc_trans_cost[int(row[0]),0,1,k]
                        X1TransCost+=arc_trans_cost[int(row[0]),0,1,k]
        #print '\n'
        for row in customer:
            for k in modes:
                for s in range(len(departure)):
                    if X2[int(row[0]),k,s].x ==1:
                        print 'Customer',int(row[0]),'arc',1,2,'arc_mode_num',k,'departureNum',s+1,'X2',X2[int(row[0]),k,s].x,'StartTime',dT[1,2,k,s],'TransTime',trans_time[0,1,k],'endingTime',t[int(row[0]),2].x,'TransCost',arc_trans_cost[int(row[0]),1,2,k],'   Tardiness',T[int(row[0])].x
                        X2TransCost+=arc_trans_cost[int(row[0]),1,2,k]
                        TardinessCost+=T[int(row[0])].x*int(row[4])
print '\n'
print '3LTransCost',ThirdPartyTransCost
print 'X1TransCost',X1TransCost
print 'X2TransCost',X2TransCost
print 'Penalty_Cost',TardinessCost
print 'Total',X1TransCost+X2TransCost+TardinessCost+ThirdPartyTransCost
print 'computer time (seconds): ',time.clock() - float(start_time)
print '\n'
