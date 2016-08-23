#name 11416.py,based on 110315
import sys

sys.path.append('C:/gurobi604/win32/python27/lib/gurobipy')
from gurobipy import *
import time
from read111215 import *

print 'Basic info'
for row in customer:
    print 'Customer',int(row[0])+1,'Destination ',row[1], 'quantity ',int(row[2]),'DD',int(row[3])
print "\n"
start_time=time.clock()
m = Model('MIP')
M=1000000000
#fix cost of 3pl
F=1250
# set of routes
nodes=[1,2,3]
#departure time
departure=[1,2] 
#modes = ['T','R','H','A']
modes=[1,2,3,4]

arc_C={}
arc_C=getArcC(nodes,modes,departure)
##print 'len',len(arc_C)
##print arc_C
Distance={}
Distance=getDistance()
trans_time={}
trans_time=getTransTime(nodes,modes,getDistance())
arc_trans_cost={}
arc_trans_cost=getArcTransCost(customer,nodes,modes,getDistance())
dT={}
dT=getdT()


                
#{} means dictionary, [] means list
#GG=[ [[0 for row1 in range(6)] for row2 in range(4)] for row3 in range(4)]
##print 'len(GG)',len(GG)
##print 'len(arc_C)',len(arc_C)


##pi2={}
##for i in nodes:
##    if i==4:
##        continue
##    else:
##        for k in modes:
##            for s in departure:
##                pi2[i,k,s]=0
def MIP(m,customer,arc_C,nodes,modes,departure,pi):
    #decision variable X: binary variable. X[customer,i,i+1,m,k]
    X = {}
    for row in customer:
        for i in nodes:
            if i==3:
                continue
            else:
                for k in modes:
                    for s in departure:
                        #print row[0]
                        X[int(row[0]),i,k,s]=m.addVar(vtype=GRB.BINARY,name='X_%s_%s_%s_%s'%(int(row[0]),i,k,s))
    m.update()
    
    expr1=LinExpr()
    for row in customer:
        for i in nodes:
            if i==3:
                continue
            else:
                for k in modes:
                    for s in departure:
                        expr1=expr1+X[int(row[0]),i,k,s]*int(row[2])*arc_trans_cost[int(row[0]),i,k]
    #pi, i cannot use LinExpr() formula, how to dicribe the relathion by other way?
    expr2 = LinExpr()
    for k in modes:
        for s in departure:
            for i in nodes:
                a=LinExpr()
                if i==3:
                    continue
                else:
                    for row in customer:
                            a.addTerms(int(row[2]),X[int(row[0]),i,k,s])
                    a.add(-1,arc_C[i,k,s])
                expr2=expr2+pi[i,k,s]*a
    #print 'test expr2',expr2
         
    m.update()
    #decision variable y: binary variable of 3PL
    y={}
    for row in customer:
        for i in nodes:
            if i==3:
                continue
            else:
                y[int(row[0]),i]=m.addVar(vtype=GRB.BINARY,name='y_%s_%s'%(int(row[0]),i))     
    m.update()

    expr3=LinExpr()
    for row in customer:
        for i in nodes:
            if i==3:
                continue
            else:
                expr3=expr3+y[int(row[0]),i]*int(row[2])*F
                
    #decision variable: arrive time at each node
    t={}
    for row in customer:
        for i in nodes:
            if i==3:
                continue
            else:
                t[int(row[0]),i]=m.addVar(vtype='C',name='nodeTime_%s_%s'%(int(row[0]),i))  
    #decision variable:Time tardiness of customer
    T={}
    for row in customer:
            T[int(row[0])]=m.addVar(vtype='C',name='Tardiness_%s'%(int(row[0])))
    m.update()

    expr4=LinExpr()
    for row in customer:
        expr4=expr4+T[int(row[0])]*int(row[2])*int(row[4])
    

    
    #######################################
    m.setObjective(expr1+expr2+expr3+expr4)
    #######################################
    
    #Constraint 3.2 for each customer, each link, only one plan can be selected
    for row in customer:
        for i in nodes:
            if i==3:
                continue
            else:
                expr5 = LinExpr()       
                for k in modes:
                        for s in departure:
                                expr5.addTerms(1.0,X[int(row[0]),i,k,s])
                expr5.add(y[int(row[0]),i])
                m.addConstr(expr5, GRB.EQUAL, 1,name='One_%s_%s_%s_%s'%(int(row[0]),i,k,s))
    m.update()
    #Constraint binarty of 3PL
    for row in customer:
        for i in nodes:
            if i==1 or i==3:
                continue
            else:
                m.addConstr(y[int(row[0]),i-1],GRB.LESS_EQUAL,y[int(row[0]),i],name='one3pl_%s_%s'%(int(row[0]),i))
    #constraint 3.4 arc capacity
    for k in modes:
        for s in departure:
            for i in nodes:
                if  i==3:
                    continue
                else:
                    expr6 = LinExpr()
                    for row in customer:
                            expr6.addTerms(int(row[2]),X[int(row[0]),i,k,s])
                    expr6.addConstant(-1*arc_C[i,k,s])
                    m.addConstr(expr6,GRB.LESS_EQUAL, 0,'arcCapacity_%s_%s_%s_%s'%(int(row[0]),i,k,s))      
    m.update()                                          
    #constraint 3.5 time constraint One
    for row in customer:        
            for i in nodes:
                if i==3:
                    continue
                else: 
                    expr7 = LinExpr()                
                    for k in modes:
                            for s in departure:                                            
                                    expr7.addTerms(dT[i,k,s]+trans_time[i,k],X[int(row[0]),i,k,s])
                    expr7.add(-1*y[int(row[0]),i]*M)
                    m.addConstr(expr7,GRB.LESS_EQUAL,t[int(row[0]),i],name='timeConstr1_%s_%s'%(int(row[0]),i))                        
    m.update()                    
    for row in customer:        
            for i in nodes:                    
                    expr8 = LinExpr()
                    if i==1 or i==3:
                            continue
                    else:
                            for k in modes:
                                    for s in departure:                                            
                                            expr8.addTerms(dT[i,k,s],X[int(row[0]),i,k,s])
                            expr8.add(y[int(row[0]),i])
                            m.addConstr(expr8,GRB.GREATER_EQUAL,t[int(row[0]),i-1],name='timeConstr2_%s_%s'%(int(row[0]),i))
    m.update()
    #definition of T
    for row in customer:
        for k in modes:
            for s in departure:
                if X[int(row[0]),2,k,s]>0:
                    #ending_time[int(row[0])]=(dT[3,k,s]+trans_time[3,k])*X[int(row[0]),3,k,s]
                    if t[int(row[0]),2]>DD[int(row[0])]:
                        m.addConstr(T[int(row[0])],GRB.EQUAL,t[int(row[0]),2]-DD[int(row[0])],name='Tardiness_%s'%(int(row[0])) )
    m.update()
    m.optimize()
    return X,y,t,T,m.objVal


#while sigma>=0.005: # means when sigma<0.005, stop
def expr1_value(X):
    expr1=0
    for row in customer:
        for i in nodes:
            if i==3:
                continue
            else:
                for k in modes:
                    for s in departure:
                        expr1=expr1+X[int(row[0]),i,k,s].x*int(row[2])*arc_trans_cost[int(row[0]),i,k]
    return expr1
    
def expr2_value(X,pi):
    k2=0
    for k in modes:
        for s in departure:
            for i in nodes:
                a=0
                if i==3:
                    continue
                else:
                    for row in customer:
                            a=a+int(row[2])*X[int(row[0]),i,k,s].x
                    a=a-arc_C[i,k,s]
                k2=k2+pi[i,k,s]*a
    return k2
    
def expr3_value(y):
    expr3=0
    for row in customer:
        for i in nodes:
            if i==3:
                continue
            else:
                expr3=expr3+y[int(row[0]),i].x*int(row[2])*F
    return expr3
def expr4_value(T):
    expr4=0
    for row in customer:
        expr4=expr4+T[int(row[0])].x*int(row[2])*int(row[4])
    return expr4

pi={}#i=0,1,2,3; k=1,2,3,4; s=1,2,3,4,5,6
#pi=[ [[[0] for row1 in range(6)] for row2 in range(4)] for row3 in range(4)]
for i in nodes:
    if i==3:
        continue
    else:
        for k in modes:
            for s in departure:
                pi[i,k,s]=0
Z_list=[]
sigma=2
Zub=15171100
o=0
alpha=1
#Z=1
#G=0 # G is a single value, means sum of QX-C


m=Model('MIP')
(X,y,t,T,Z)=MIP(m,customer,arc_C,nodes,modes,departure,pi)#the first round is only to get the Zlb, 
Zlb=Z # to get the initial Zlb

for i in nodes:
    if i==3:
        continue
    else:
        for k in modes:
            for s in departure:
                pi[i,k,s]=1#first round pi should be 1
p=0
#while sigma>=0.005:
while o!=1:# means when o=3, stop
    m = Model('MIP')
    (X,y,t,T,Z)=MIP(m,customer,arc_C,nodes,modes,departure,pi) #Z is the lower bound, set pi=0 get the Zlb
    print '********************************************'
    print expr1_value(X),'transporation cost'
    print expr2_value(X,pi),'pi  cost'
    print expr3_value(y),'y cost'
    print expr4_value(T),'Time tardiness cost'
    print '********************************************'

    for row in customer:
        print 'Customer',int(row[0])+1,'Tardiness',T[int(row[0])].x
    print '\n'
    threePLCost=0
    TransCost=0
    TotalTransCost=0
    TotalTardinessCost=0
    TotalCost=0
    if m.status == GRB.status.OPTIMAL:
            for row in customer:
                #print 'Customer',int(row[0]),'Tardiness',T[int(row[0])].x
                TotalTardinessCost+=T[int(row[0])].x*int(row[4])*int(row[2])
                for i in nodes:
                    if i==3:
                        continue
                    else:
                        if y[int(row[0]),i].x>0:
                                print 'Customer',int(row[0])+1,'arc',i,' using 3PL','Trans_cost',F*int(row[2])
                                threePLCost+=F*int(row[2])        
    for row in customer:
            for i in nodes:
                if i==3:
                    continue
                else:
                    for k in modes:
                        for s in departure:
                                if X[int(row[0]),i,k,s].x > 0:
                                        print 'Customer',int(row[0])+1,'link',i,'arc_mode_num',k,'departureTimeIndex',s,'arc_cost',arc_trans_cost[int(row[0]),i,k]*int(row[2]),'start_Time',dT[i,k,s],'Trans_time',trans_time[i,k],'t',t[int(row[0]),i].x,'real_arrive_time',dT[i,k,s]+trans_time[i,k]
                                        TransCost+=arc_trans_cost[int(row[0]),i,k]*int(row[2])
    TotalTransCost=TransCost+threePLCost
    TotalCost=  TotalTardinessCost+   TotalTransCost
    print '\n'
    #print 'check'
    #print 'expr1',expr1
##    print 'expr3',expr3
##    print 'expr4',expr4
##    print 'expr2',expr2
    print '\n'
    print 'MIP SOLUTION 3 ARCS'
    print 'customer size',len(customer)
    print 'Trans_Cost',TransCost
    print '3PL_Cost',threePLCost
    print 'Total_Trans_Cost',TotalTransCost
    print 'Total_Penalty_Cost',TotalTardinessCost
    print 'Total_Cost',TotalCost
    
    #G size is nmt, similar to pi. 
    G = 0
    for k in modes:
        for s in departure:
            for i in nodes:
                if i==3:
                    continue
                else:
                    for row in customer:
                        if X[int(row[0]),i,k,s].x>0:
                            #print 'test',X[int(row[0]),i,k,s].x # why X=0 will also be shown?
                            #if you print X[int(row[0]),i,k,s], then all the X will be shown
                            G=G+int(row[2])*X[int(row[0]),i,k,s].x
                    #print 'middle G',G, 'i,k,s',i,k,s
                    G=G-arc_C[i,k,s] # right?????????
    print '\n'
    print 'G',G
    GG={}
    for i in nodes:
        if i==3:
            continue
        else:
            for k in modes:
                for s in departure:
                    GG[i,k,s]=0
    for k in modes:
        for s in departure:
            for i in nodes:
                #a=LinExpr()
                if i==3:
                    continue
                else:
                    for row in customer:
                        if X[int(row[0]),i,k,s].x>0:
                            #print 'i,k,s',i,k,s
                            #print 'GG[i,k,s]',GG[i,k,s]
                            GG[i,k,s]=GG[i,k,s]+int(row[2])*X[int(row[0]),i,k,s].x
                            #print 'GG[i,k,s]',GG[i,k,s]
                    GG[i,k,s]=GG[i,k,s]-arc_C[i,k,s]# where is the problem?
    print 'GG','\n',GG
    #print 'size of GG',len(GG)
    #print 'size of pi',len(pi)
    #K=alpha*GG
    #print 'K',K
                    
    #define alpha, intial alpha=1, then become smaller. 
    #alpha=sigma*(Z_fea-Z)/(G*G)
    #update pi,pi is three degree of n, m ,t. also GG, same degree
    
    print 'pi','\n',pi
    for k in modes:
        for s in departure:
            for i in nodes:
                if i==3:
                    continue
                else:
                    pi[i,k,s]=max(0,pi[i,k,s]+GG[i,k,s]*alpha)
    print 'pi','\n',pi
    #alpha=alpha/5.0
    print '\n'
    print 'o',o,'alpha',alpha,'Zlb',Zlb,'Zub',Zub,'sigma',sigma
    print '\n'
    #t=t/3.0
    #if we want to confirm that solutionis optimal, then no value in GG is bigger than 0
    #here it is nothing about G, because G is summary,
    if all(l <0 for l in GG)==True: #this means the solution is feasible, it means we found the opt
        break
        #Zlb=max(Z,Zlb)
    else:#means infeasible which it make sense, it is not easy to find the opt
        if Z>Zlb:
            Zlb=Z#here only update Zlb, the key thing is to update Zub
            sigma=2
        else:
            p=p+1
    alpha=sigma*(Zub-Zlb)/(G*G)                     
##    if G<=0 and Z>=Z_fea:
##        Z_fea=max(Z,Z_fea)# here has problem?
##    else:
##        Z_fea=Z_fea# update Z_fea if possible
    if len(Z_list)==3:# run 5 round to make sure Z is not decrease anymore
        if Z<min(Z_list):
            Z_list=[]
            Z_list.append(Z)
        else:
            sigma=sigma/2.0
            Z_list=[]
            Z_list.append(Z)
    else:
        Z_list.append(Z)
        o+=1
    
                
    

##x=MIP(nodes,modes,departure),nodes,modes,departure, pi1)
#pi2 is after MIP pi, pi2 is f(x), every round, initial pi will be set to 0.
##def getpi2(nodes,modes,departure,X):
##    for k in modes:
##        for s in departure:
##            for i in nodes:
##                if i==4:
##                    continue
##                else:
##                    a = 0
##                    for row in customer:
##                            a=a+int(row[2])*X[int(row[0]),i,k,s].x
##                    pi2[i,k,s]=a-1*arc_C[i,k,s]
##    return pi2

#while loop start!!!
##my_turn=0
##while my_turn<3:
##    print my_turn
##    print "pi1",pi1
##    pi1=pi2
##    MIP(m,customer,arc_C,nodes,modes,departure,pi1)
##    #print 'mid done'
##    m.optimize()
##    X,y,t,T=m.__data
##    pi2=getpi2(nodes,modes,departure,X)
##    print 'after MIP, pi2',pi2
##    
##    threePLCost=0
##    TransCost=0
##    TotalTransCost=0
##    TotalTardinessCost=0
##    TotalCost=0
##    if m.status == GRB.status.OPTIMAL:
##        for row in customer:
##            print 'Customer',int(row[0]),'Tardiness',T[int(row[0])].x
##            TotalTardinessCost+=T[int(row[0])].x*int(row[4])*int(row[2])
##            for i in nodes:
##                if i==4:
##                    continue
##                else:
##                    if y[int(row[0]),i].x>0:
##                            print 'Customer',int(row[0])+1,'arc',i,' using 3PL','Trans_cost',F*int(row[2])
##                            threePLCost+=F*int(row[2])        
##    for row in customer:
##            for i in nodes:
##                if i==4:
##                    continue
##                else:
##                    for k in modes:
##                        for s in departure:
##                                if X[int(row[0]),i,k,s].x > 0:
##                                        print 'Customer',int(row[0])+1,'link',i,'arc_mode_num',k,'departureTimeIndex',s,'arc_cost',arc_trans_cost[int(row[0]),i,k]*int(row[2]),'start_Time',dT[i,k,s],'Trans_time',trans_time[i,k],'t',t[int(row[0]),i].x,'real_arrive_time',dT[i,k,s]+trans_time[i,k]
##                                        TransCost+=arc_trans_cost[int(row[0]),i,k]*int(row[2])
##    TotalTransCost=TransCost+threePLCost
##    TotalCost=  TotalTardinessCost+   TotalTransCost
##    print '\n'
##    print 'MIP SOLUTION 3 ARCS'
##    print 'customer size',len(customer)
##    print 'Trans_Cost',TransCost
##    print '3PL_Cost',threePLCost
##    print 'Total_Trans_Cost',TotalTransCost
##    print 'Total_Penalty_Cost',TotalTardinessCost
##    print 'Total_Cost',TotalCost
##    my_turn+=1
    
##MIP(nodes,modes,departure),nodes,modes,departure, pi1)
##m.optimize()
##X,y,t,T=m.__data
