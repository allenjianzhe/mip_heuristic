#file name 022415.py  ��021115 we need to test before X2 fixed 1 , ����һ��capacityʣ����������X2=1�����������capacityʣ������
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
def MIP(m,customer,arc_C,r_bi,k_bi,s_bi):
    r_try=0
    j_try=0
    
    k_try=0
    s_try=0
    ####################################################################################################
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
    ####################################################################################################    
  
    for (row,k,s) in example:
        m.addConstr(X2[int(row),k,s], GRB.EQUAL, 1,name='One_%s3'%(int(row)))
                                            
                                        
    #decision variable y: binary variable of 3PL
    y={}
    for row in customer:
        y[int(row[0])]=m.addVar(obj=F*int(row[2]),vtype=GRB.BINARY,name='y_%s'%(int(row[0])))     
    m.update()
    #one more constraint for y

        
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
                if i==0 or i==2:  #������ʵi=1
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
                if i==0 or i==1:#������ʵi=2
                        continue
                else:
                        for k in modes:
                                for s in range(len(departure)):                                            
                                        expr.addTerms(dT[i-1,i,k,s]+trans_time[i-1,i,k],X2[int(row[0]),k,s])
                        expr.add(-1*y[int(row[0])]*M)
                        m.addConstr(expr,GRB.LESS_EQUAL,t[int(row[0]),i],name='timeConstr_%s_%s'%(int(row[0]),i))
    m.update()
    #constraint 3.6 time constraint Two, ��һ�ڵĳ���ʱ�������һ�ڵĵ���ʱ��
    for row in customer:
        for i in node:                    
                expr1 = LinExpr()
                if i==0 or i==2:#������ʵi=1
                        continue
                else:
                        for k in modes:
                                for s in range(len(departure)):                                            
                                        expr1.addTerms(dT[i,i+1,k,s],X2[int(row[0]),k,s])                          
                        m.addConstr(expr1,GRB.GREATER_EQUAL,t[int(row[0]),i],name='timeConstr_%s_%s'%(int(row[0]),i))

    m.update()
    nothing=0
    ###constraint 3.7 time constraint Three, tardiness time ֻ�����һ��t[n,2]�й�
    for row in customer:
        for k in modes:
                for s in range(len(departure)):
                        if X2[int(row[0]),k,s]>0:
                                if t[int(row[0]),2]>int(row[3]):                                        
                                        m.addConstr(T[int(row[0])],GRB.EQUAL,t[int(row[0]),2]-int(row[3]),name='Tardiness_%s'%(int(row[0])) )
                                else:
                                        nothing=nothing+1#������ʵʲôҲ����Ҫ��

    m.update()
    m.__data=X1,X2,y,t,T
    return m


####################################################################################################
##y_move=[]
##cus_move=[]
##def update_cus(cus_arr,arc_arr,r_try,i_try,k_try,s_try):#move_index ����ʱ�������������ô֪��ָ���ĸ���()������Ǳ���
##    #print i,k,s
##    index_g=r # index_g �ʼ�����︳ֵ��������������������������������
##    print index_g,'move'
##    if arc_arr[i-1,i,k,s]>=int(cus_arr[r][2]):
##        del customer_id[index_g]   #??????????????????
##        arc_arr[i-1,i,k,s]=arc_arr[i-1,i,k,s]-int(cus_arr[r][2])
##        #global_index.index([r,i])
##        #print index_g,'index...........'
##    else:# ˵�����е�capacity ������
##        del customer_id[index_g]
##        y_move.append(index_g)   #����ֱ�Ӹ�y[index_g]��ֵ1����Ϊy��MIP������variables. ������ֱ�Ӹģ� ������customer_id һ��������һ���ռ��� ��mip����Ķ�         
##    return (cus_arr,arc_arr)
##mmm=0
################################################################################
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
###print 'arc 0-1:','SC-WH ','arc 1-2:','WH-ZZ'
##for row in customer:
##    print 'Customer',int(row[0]),'Destination ',row[1], 'quantity ',int(row[2]),'DD',int(row[3])
##print "\n"

##global_index=[]
##for row in customer:
##    global_index.append([int(row[0]),1])#?????????����Բ��ԣ�
move_set=[]
move_index_set=[]
new_transport_cost=0
for l in range(len(customer)):#������ô�ģ� 3��customer�� ��3��X2Ҫ�ң� ��������3�Σ�������ã� ��һ���˵��Ѿ���1�ˣ� �Ͳ�������.�и��õķ���???????????????
    #print len(global_index),'global length...........................................'
    (r_bi,k_bi,s_bi)=(100,100,100)
    #mmm+=1 
    MIP(m,customer,arc_C,r_bi,k_bi,s_bi)
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
                if y[int(row[0])].x>0:
                        print 'Customer',int(row[0]),' using 3PL','Trans_cost',F
                        #threePLCost+=F
                        
                for k in modes:
                        for s in range(len(departure)):
                                if X1[int(row[0]),k,s].x > 0:
                                  
                                    print 'Customer',int(row[0]),'arc',0,1,'arc_mode_num',k,'departureNum',s+1,'X1',X1[int(row[0]),k,s].x#'Tardiness',T[int(row[0])].x,'start_Time',dT[0,1,k,s],'Ending_time',t[int(row[0]),2].x,
                              
                                if X2[int(row[0]),k,s].x > 0:
                                    print 'Customer',int(row[0]),'arc',1,2,'arc_mode_num',k,'departureNum',s+1,'X2',X2[int(row[0]),k,s].x
                                if X2[int(row[0]),k,s].x==1 and [int(row[0]),k,s] not in example:
                                    a=[]
                                    a.append(int(row[0]))
                                    a.append(k)
                                    a.append(s)#,i_try,k_try,s_try)
                                    example.append(a)
                                    a=[]
                                    #print 'X2[int(row[0]),k,s].x################################',X2[int(row[0]),k,s].x
                                    capacity_left[1,2,k,s]=capacity_left[1,2,k,s]-X2[int(row[0]),k,s].x*int(row[2])
                                    #print 'capacity_left[1,2,k,s]',capacity_left[1,2,k,s]
                                           
    print '\n'
    #print 'capacity_left',capacity_left

# third step, pick biggest X2
#֮ǰ�Ѿ�fixedΪ1�Ĳ��òμ����������
    node_arc=[]
    indexes=[]
    for k in modes:
        for s in range(len(departure)):                
            for row in customer:
                #print i,k,s,X[int(row[0]),i-1,i,k,s].x
                if [int(row[0]),k,s] not in example and X2[int(row[0]),k,s]>0:
                    #print row,k,s
                    # and (row[0],2,k,s) not in example
                    #print 'arc',i-1,i,'k',k,'s',s,'customer',row[0],X[int(row[0]),i-1,i,k,s].x
                    #print i-1,i,k,s,X[int(row[0]),i-1,i,k,s].x
                    arr=str([int(row[0]),k,s])  #�����ǿ���һ��str
                    arrr=[]
                    arrr.append(arr)
                    #print 'X2[int(row[0]),k,s].x###########',X2[int(row[0]),k,s].x
                    arrr.append(X2[int(row[0]),k,s].x)
                    node_arc.append(arrr)
                    indexes.append([int(row[0]),k,s])
                            #print sorted(node_arc)[0:5]                                
                            #print node_arc
                            #print 'test',indexes[0]
                    #sort(node_arc[i-1,i,k,s])
    #print node_arc,'node_arc'
                    
def test(test_r,test_k,test_s):
    if capacity_left[1,2,int(test_k),int(test_s)]>=int(customer[int(test_r)][2]):# �ĵã�����ֱ����MIP�����row��2������Ϊ����ȫ�ֱ�����
        print 'capacity_left[1,2,int(test_k),int(test_s)]',capacity_left[1,2,int(test_k),int(test_s)],'int(customer[int(test_r)][2])',int(customer[int(test_r)][2])
        return 1
    else:
        return 0
    
    if len(node_arc)>0:
      node_arcs=sorted(node_arc, key=lambda x: x[1],reverse=True)
      #print 'node_arcs',node_arcs
      forindex=0
      max_value = []
      for idx in range(len(node_arcs)):
          forindex+=1
          new_node=node_arcs[idx]
          #new_node[-1]=1
          #print 'new_node[0][1]',new_node[0][1],'new_node[0][4]',new_node[0][4],'new_node[0][7]',new_node[0][7]
          if test(new_node[0][1],new_node[0][4],new_node[0][7])==1:
              max_value = new_node
              #print '#######################################################'
              new_node=[]
              break
      print 'forindex*************************************************************',forindex
      

      node_arc=[] #�ҵ��ˣ��͹�0���´��ҾͲ������
      indexes=[]
      print 'max_value',max_value
    ####################################################################################################
      (r_try,k_try,s_try)=(int(max_value[0][1]),int(max_value[0][4]),int(max_value[0][7]))
      print '(r_try,k_try,s_try)',(r_try,k_try,s_try)
      #print '(r_try,k_try,s_try)',(r_try,k_try,s_try)
      a=[]
      a.append(r_try)
      a.append(k_try)
      a.append(s_try)#,i_try,k_try,s_try)
      example.append(a)
      a=[]
      
          #print (r,j,i,k,s)

##      if check_capacity(r_try1,try1,try1,try1)>0:
##      else:
##         check_capacity(r_try2,try2
      MIP(m,customer,arc_C,r_try,k_try,s_try)
      #print 'X2[2,1,0]',X2[2,1,0]
      #print 'X2[0,1,0]******************',X2[0,1,0]
      m.optimize()
      X1,X2,y,t,T=m.__data
      move_set.append(max_value)
##      (customer,arc_C)=update_cus(customer,arc_C,r_try,j_try,i_try,k_try,s_try)
##                      print len(global_index)
##                      print arc_C
                      #X,y,t,T=m.__data
                      #print 'try',r,i,k,s,X[r,i-1,i,k,s]
    #print arc_C
##print '\n'
print 'move set',move_set


