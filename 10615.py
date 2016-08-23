

#121615.py based on 041515. try to test time like capacity,read041415
import sys
import math
sys.path.append('C:/gurobi604/win32/python27/lib/gurobipy')  # for apple
#sys.path.append('C:/gurobi562/win64/python27/lib/gurobipy')   # for windows
from gurobipy import *
from read041415 import *
import time   
start_time=time.clock()
m = Model('MIP')
M=1000000000
F=1250
#test
example_x2_1=[] #create a set of x2_1
example_x2_0=[]
example_x1_0=[]
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
                X1[int(row[0]),k,s]=m.addVar(obj=int(row[2])*arc_trans_cost[int(row[0]),0,1,k],vtype=GRB.BINARY,name='X1_%s_%s_%s'%(int(row[0]),k,s))# they are binary,no change
    m.update()
    #decision variable X for arc 1-2: binary variable. X[customer,i,i+1,m,k]
    X2 = {}
    for row in customer: 
        for k in modes:
            for s in range(len(departure)):
                X2[int(row[0]),k,s]=m.addVar(obj=int(row[2])*arc_trans_cost[int(row[0]),1,2,k],vtype='C',name='X2_%s_%s_%s'%(int(row[0]),k,s))#here is continous, main job 
    m.update()
##    print 'example_y',example_y
##    print 'example_x1',example_x1
##    print 'example_x1_0',example_x1_0
##    print 'example_x2_1',example_x2_1
##    print 'example_x2_0',example_x2_0
    #example constraint for all X1=1
    for (row,k,s) in example_x1:
        m.addConstr(X1[int(row),k,s],GRB.EQUAL,1,name='OneX1_%s'%(int(row)))# fix them to be constant
    #example constraint for all X1=0
    for (row,k,s) in example_x1_0:
        m.addConstr(X1[int(row),k,s], GRB.EQUAL, 0,name='OneX10_%s3'%(int(row)))# fix them to be constant
    #example constraint for all X2=1
    for (row,k,s) in example_x2_1:
        m.addConstr(X2[int(row),k,s], GRB.EQUAL, 1,name='Onex2_%s3'%(int(row)))# fix them to be constant
    #example constraint for all X2=0
    for (row,k,s) in example_x2_0:
        m.addConstr(X2[int(row),k,s], GRB.EQUAL, 0,name='One_%s3'%(int(row)))# fix them to be constant
    
    #decision variable y: binary variable of 3PL
    y={}
    for row in customer:
        y[int(row[0])]=m.addVar(obj=int(row[2])*F,vtype=GRB.BINARY,name='y_%s'%(int(row[0])))     
    m.update()
    #example_y constraint
    for r in example_y:
        m.addConstr(y[r],GRB.EQUAL,1,name='one_y%s'%(r))# fix them to be constant
    #decision variable: arrive time at each node
    t={}
    for row in customer:
        for i in node:
                if i==0:        
                        continue
                else:
                        t[int(row[0]),i]=m.addVar(obj=0,vtype=GRB.INTEGER,name='nodeTime_%s_%s'%(int(row[0]),i))  # t is integer, not continous, 
    #decision variable:Time tardiness of customer
    T={}
    for row in customer:
            T[int(row[0])]=m.addVar(obj=int(row[2])*int(row[4]),vtype=GRB.INTEGER,name='Tardiness_%s'%(int(row[0])))
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
            m.addConstr(expr,GRB.LESS_EQUAL, 0,'arcCapacity2_%s_%s_%s'%(int(row[0]),k,s))    # we will relax this one    
    m.update()
    #constraint 3.5 time constraint One
    for row in customer:
        for i in node:
                expr = LinExpr()                
                if i==0 or i==2:  # here i=1
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
                if i==0 or i==1:# i=2
                        continue
                else:
                        for k in modes:
                                for s in range(len(departure)):                                            
                                        expr.addTerms(dT[i-1,i,k,s]+trans_time[i-1,i,k],X2[int(row[0]),k,s])
                        #expr.add(-1*y[int(row[0])]*M)
                        m.addConstr(expr,GRB.LESS_EQUAL,t[int(row[0]),i],name='timeConstr_%s_%s'%(int(row[0]),i))
    m.update()
    #constraint 3.6 time constraint Two
    for row in customer:
        for i in node:                    
                expr1 = LinExpr()
                if i==0 or i==2:#i=1
                        continue
                else:
                        for k in modes:
                                for s in range(len(departure)):                                            
                                        expr1.addTerms(dT[i,i+1,k,s],X2[int(row[0]),k,s])                          
                        m.addConstr(expr1,GRB.GREATER_EQUAL,t[int(row[0]),i],name='timeConstr_%s_%s'%(int(row[0]),i))
    m.update()
    nothing=0
    ###constraint 3.7 time constraint Three, tardiness time , t[n,2]
##    for row in customer:
##        for k in modes:
##                for s in range(len(departure)):
##                        if X2[int(row[0]),k,s]>0 and (dT[i-1,i,k,s]+trans_time[i-1,i,k])*X2[int(row[0]),k,s]>=int(row[3]):
##                            m.addConstr(T[int(row[0])],GRB.EQUAL,(dT[i-1,i,k,s]+trans_time[i-1,i,k])*X2[int(row[0]),k,s]-int(row[3]),name='Tardiness_%s'%(int(row[0])) )
##    m.update()
    for row in customer:
        for k in modes:
                for s in range(len(departure)):
                        if X2[int(row[0]),k,s]>0 and t[int(row[0]),2]>=int(row[3]):
                            m.addConstr(T[int(row[0])],GRB.EQUAL,t[int(row[0]),2]-int(row[3]),name='Tardiness_%s'%(int(row[0])) )
    m.update()
    m.__data=X1,X2,y,t,T
    return m
for l in range(0,5):
    print 'round',l
#while len(example_x2_1)+len(example_y) !=len(customer):
    m=Model('MIP')
    (r_bi,k_bi,s_bi)=(100,100,100)
    MIP(m,customer,arc_C,r_bi,k_bi,s_bi)
    m.optimize()
    X1,X2,y,t,T=m.__data
    #print '\n'
    if m.status == GRB.status.INFEASIBLE:
        m.computeIIS()
        m.write('mipmodelconstraintError.ilp')
    if m.status == GRB.status.OPTIMAL:
        for row in customer:
            if y[int(row[0])].x>0:
                #print 'Customer',int(row[0]),' using 3PL','Trans_cost',F*int(row[2])
                if y[int(row[0])].x==1 and int(row[0]) not in example_y:
                    example_y.append(int(row[0]))# first put y into example                     
        for row in customer:
            for k in modes:
                for s in range(len(departure)):
##                    if X1[int(row[0]),k,s].x > 0: 
##                        print 'Customer',int(row[0]),'arc',0,1,'arc_mode_num',k,'departureNum',s+1,'X1',X1[int(row[0]),k,s].x
                    if X2[int(row[0]),k,s].x > 0:
                        #print 'Customer',int(row[0]),'arc',1,2,'arc_mode_num',k,'departureNum',s+1,'X2',X2[int(row[0]),k,s].x
                        if X2[int(row[0]),k,s].x==1 and [int(row[0]),k,s] not in example_x2_1:
                            a=[]
                            a.append(int(row[0]))
                            a.append(k)
                            a.append(s)
                            example_x2_1.append(a)
                            a=[]
                            #print test_capacity[k,s],'$$$$$$$$$$$$$'
                            test_capacity[k,s]=test_capacity[k,s]-int(row[2])
                            #print test_capacity[k,s],'$$$$$$$$$$$$$$$$$$$','k',k,'s',s
                            for k in modes:
                                for s in range(len(departure)):
                                    if X1[int(row[0]),k,s].x > 0:
                                        a=[]
                                        a.append(int(row[0]))
                                        a.append(k)
                                        a.append(s)
                                        example_x1.append(a)
                                        a=[]
        #print '\n'
    #until here, first round is end, check y, X1, X2 whether into the example set. 
    node_arc=[] # create the arc set to check ? shall be here? Yes, it is here, because each time once we fix a X2, we need to run the MIP again to get new X2
    for k in modes:
        for s in range(len(departure)):                
            for row in customer:
                if X2[int(row[0]),k,s].x>0 and X2[int(row[0]),k,s].x !=1:
                    arr=str([int(row[0]),k,s])
                    arrr=[]
                    arrr.append(arr)
                    arrr.append(X2[int(row[0]),k,s].x) # put index and X2 value together! in the node_arc
                    node_arc.append(arrr)#create arc set so that in the future can be checked, put the index into it.
    #print 'len node_arc', node_arc
    if len(node_arc)>0:
      node_arcs=sorted(node_arc, key=lambda x: x[1],reverse=True)
      #print 'X2 order start',node_arcs
      #print len(example_y),'111111111111111111111111111'
      #start to choose X2###############################################in other word, test capacity in the example
      for iks in range(len(node_arcs)):
          max_value=node_arcs[iks]# order all the continous X2, choose the max one
          a=[]
          rows=max_value[0][1:-1].split(',')
          (r_try,k_try,s_try)=map(int,rows)#don't put three index into the example_x2_1, wait until the test has been done.
          p=int(customer[r_try][2])
          if p<=test_capacity[k_try,s_try]:#means capacity is satisfied!!!
              #print 'capacity is satisfied'
              #print 'r_try',r_try,'k_try',k_try,'s_try',s_try
              k_try_x1=0
              s_try_x1=0
              for k in modes:
                  for s in range(len(departure)):
                      if X1[r_try,k,s].x>0:
                          k_try_x1=k
                          s_try_x1=s
              #print 'dT[1,2,k_try,s_try]',dT[1,2,k_try,s_try]
              #print 'dT[0,1,k_try_x1,s_try_x1]',dT[0,1,k_try_x1,s_try_x1]
              #print 'trans_time[0,1,k_try_x1])',trans_time[0,1,k_try_x1]
              if dT[1,2,k_try,s_try]>=(dT[0,1,k_try_x1,s_try_x1]+trans_time[0,1,k_try_x1]):
                  #print 'time capcaity is satisfied and X2 will be fixed'
                  test_capacity[k_try,s_try]=test_capacity[k_try,s_try]-int(customer[r_try][2])
                  a=[]
                  a.append(r_try)
                  a.append(k_try)
                  a.append(s_try)#r_try,k_try,s_try are the most important index that i need to remember!!!
                  example_x2_1.append(a)# put the max index into example first, then we need to test capacity
                  a_x1=[]
                  a_x1.append(r_try)
                  a_x1.append(k_try_x1)
                  a_x1.append(s_try_x1)
                  example_x1.append(a_x1)
                  #print 'k_try_x1',k_try_x1
                  break
              else:#meas time costraint is not satisfied!!!
                  #print 'time capcaity is not satisfied'
                  a=[]
                  a.append(r_try)
                  a.append(k_try)
                  a.append(s_try)
                  example_x2_0.append(a)
                  continue
          else:#means if p>test_capacity[k_try,s_try]:#means capacity is not satisfied!!!!
              #print 'capacity is not satisfied'
              p=0
              a.append(r_try)
              a.append(k_try)
              a.append(s_try)#r_try,k_try,s_try are the most important index that i need to remember!!!
              example_x2_0.append(a)

##      if max_value==[]:
##          print len(example_y),'222222222222222222'
##          example_y.append(r_try)#not finish yeah, we need to change the X1 to 0 too.
##          print len(example_y),'3333333333333333'
##          #example_x1_0.append(a)
##          a=[]
##      else:
##          node_arc=[]
##          #until now, we need to change max_value
##          max_value=[]
print '\n'
print 'Summary','$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$'
threePLCost=0
TransCost=0
TotalTransCost=0
TotalTardinessCost=0
TotalCost=0
for row in customer:
    print 'customer',int(row[0]),'Tardiness',T[int(row[0])].x
    TotalTardinessCost+=T[int(row[0])].x*int(row[4])*int(row[2])
    if y[int(row[0])].x>0:
        print 'Customer',int(row[0]),' using 3PL','Trans_cost',F*int(row[2])
        threePLCost+=F*int(row[2])
for row in customer:
            for k in modes:
                for s in range(len(departure)):
                    if X1[int(row[0]),k,s].x > 0: 
                        print 'Customer',int(row[0]),'arc',0,1,'arc_mode_num',k,'departureNum',s+1,'X1',X1[int(row[0]),k,s].x,'arc_cost',arc_trans_cost[int(row[0]),0,1,k]*int(row[2]),'start_Time',dT[0,1,k,s],'Trans_time',trans_time[0,1,k],'t',t[int(row[0]),1].x,'real_arrive_time',dT[0,1,k,s]+trans_time[0,1,k]
                        TransCost+=arc_trans_cost[int(row[0]),0,1,k]*int(row[2])
                    if X2[int(row[0]),k,s].x > 0: 
                        print 'Customer',int(row[0]),'arc',1,2,'arc_mode_num',k,'departureNum',s+1,'X2',X2[int(row[0]),k,s].x,'arc_cost',arc_trans_cost[int(row[0]),1,2,k]*int(row[2]),'start_Time',dT[1,2,k,s],'Trans_time',trans_time[1,2,k],'t',t[int(row[0]),2].x,'real_arrive_time',dT[1,2,k,s]+trans_time[1,2,k]
                        TransCost+=arc_trans_cost[int(row[0]),1,2,k]*int(row[2])

TotalTransCost=TransCost+threePLCost
TotalCost=  TotalTardinessCost+   TotalTransCost
print '\n'
print 'MIP SOLUTION 3 ARCS'
print 'customer size',len(customer)
print 'Trans_Cost',TransCost
print '3PL_Cost',threePLCost
print 'Total_Trans_Cost',TotalTransCost
print 'Total_Penalty_Cost',TotalTardinessCost
print 'Total_Cost',TotalCost
print 'computer time (seconds): ',time.clock() - float(start_time)
print '\n'
