#name 101515_main.py, based on 090715_main follow fisher's paper
import sys

sys.path.append('C:/gurobi604/win32/python27/lib/gurobipy')
from gurobipy import *
import time
from read102715 import *

print 'Basic info'
for row in customer:
    print 'Customer',int(row[0])+1,'Destination ',row[1], 'quantity ',int(row[2]),'DD',int(row[3])
print "\n"
start_time=time.clock()
m = Model('MIP')
M=1000000000
#fix cost of 3pl
F=600000
# set of routes
nodes=[1,2,3,4]
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

pi={}#i=0,1,2,3; k=1,2,3,4; s=1,2,3,4,5,6
#pi=[ [[[0] for row1 in range(6)] for row2 in range(4)] for row3 in range(4)]
for i in nodes:
    if i==4:
        continue
    else:
        for k in modes:
            for s in departure:
                pi[i,k,s]=0
                
GG={}#{} means dictionary, [] means list
#GG=[ [[0 for row1 in range(6)] for row2 in range(4)] for row3 in range(4)]
##print 'len(GG)',len(GG)
##print 'len(arc_C)',len(arc_C)


for i in nodes:
    if i==4:
        continue
    else:
        for k in modes:
            for s in departure:
                GG[i,k,s]=0
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
            if i==4:
                continue
            else:
                for k in modes:
                    for s in departure:
                        #print row[0]
                        X[int(row[0]),i,k,s]=m.addVar(obj=int(row[2])*arc_trans_cost[int(row[0]),i,k],vtype=GRB.BINARY,name='X_%s_%s_%s_%s'%(int(row[0]),i,k,s))
    m.update()
    #obj add pi, i cannot use LinExpr() formula, how to dicribe the relathion by other way?
    expr = LinExpr()
    for k in modes:
        for s in departure:
            for i in nodes:
                a=LinExpr()
                if i==4:
                    continue
                else:
                    for row in customer:
                            a.addTerms(int(row[2]),X[int(row[0]),i,k,s])
                    a.add(-1,arc_C[i,k,s])
##                print pi[i,k,s],pi,a
                expr=expr+pi[i,k,s]*a
    m.setObjective(expr)     
    m.update()
    #decision variable y: binary variable of 3PL
    y={}
    for row in customer:
        for i in nodes:
            if i==4:
                continue
            else:
                y[int(row[0]),i]=m.addVar(obj=int(row[2])*F,vtype=GRB.BINARY,name='y_%s_%s'%(int(row[0]),i))     
    m.update()
    #decision variable: arrive time at each node
    t={}
    for row in customer:
        for i in nodes:
            if i==4:
                continue
            else:
                t[int(row[0]),i]=m.addVar(obj=0,vtype='C',name='nodeTime_%s_%s'%(int(row[0]),i))  
    #decision variable:Time tardiness of customer
    T={}
    for row in customer:
            T[int(row[0])]=m.addVar(obj=int(row[2])*int(row[4]),vtype='C',name='Tardiness_%s'%(int(row[0])))
    m.update()
    #Constraint 3.2 for each customer, each link, only one plan can be selected
    for row in customer:
        for i in nodes:
            if i==4:
                continue
            else:
                expr = LinExpr()       
                for k in modes:
                        for s in departure:
                                expr.addTerms(1.0,X[int(row[0]),i,k,s])
                expr.add(y[int(row[0]),i])
                m.addConstr(expr, GRB.EQUAL, 1,name='One_%s_%s_%s_%s'%(int(row[0]),i,k,s))
    m.update()
    #Constraint binarty of 3PL
    for row in customer:
        for i in nodes:
            if i==1 or i==4:
                continue
            else:
                m.addConstr(y[int(row[0]),i-1],GRB.LESS_EQUAL,y[int(row[0]),i],name='one3pl_%s_%s'%(int(row[0]),i))
    #constraint 3.4 arc capacity
    for k in modes:
        for s in departure:
            for i in nodes:
                if i==4:
                    continue
                else:
                    expr = LinExpr()
                    for row in customer:
                            expr.addTerms(int(row[2]),X[int(row[0]),i,k,s])
                    expr.addConstant(-1*arc_C[i,k,s])
                    m.addConstr(expr,GRB.LESS_EQUAL, 0,'arcCapacity_%s_%s_%s_%s'%(int(row[0]),i,k,s))      
    m.update()                                          
    #constraint 3.5 time constraint One
    for row in customer:        
            for i in nodes:
                if i==4:
                    continue
                else: 
                    expr = LinExpr()                
                    for k in modes:
                            for s in departure:                                            
                                    expr.addTerms(dT[i,k,s]+trans_time[i,k],X[int(row[0]),i,k,s])
                    expr.add(-1*y[int(row[0]),i]*M)
                    m.addConstr(expr,GRB.LESS_EQUAL,t[int(row[0]),i],name='timeConstr1_%s_%s'%(int(row[0]),i))                        
    m.update()                    
    for row in customer:        
            for i in nodes:                    
                    expr1 = LinExpr()
                    if i==1 or i==4:
                            continue
                    else:
                            for k in modes:
                                    for s in departure:                                            
                                            expr1.addTerms(dT[i,k,s],X[int(row[0]),i,k,s])
                            expr1.add(y[int(row[0]),i])
                            m.addConstr(expr1,GRB.GREATER_EQUAL,t[int(row[0]),i-1],name='timeConstr2_%s_%s'%(int(row[0]),i))
    m.update()
    #definition of T
    for row in customer:
        for k in modes:
            for s in departure:
                if X[int(row[0]),3,k,s]>0:
                    #ending_time[int(row[0])]=(dT[3,k,s]+trans_time[3,k])*X[int(row[0]),3,k,s]
                    if t[int(row[0]),3]>DD[int(row[0])]:
                        m.addConstr(T[int(row[0])],GRB.EQUAL,t[int(row[0]),3]-DD[int(row[0])],name='Tardiness_%s'%(int(row[0])) )
    m.update()
    m.optimize()
    return X,y,t,T,m.objVal

Z_list=[]
sigma=2
Z_fea=0
o=0
Z=1
alpha=1
G=0 # G is a single value, means sum of QX-C
#pi=0
while o!=10:
    (X,y,t,T,Z)=MIP(m,customer,arc_C,nodes,modes,departure,pi)
    for row in customer:
        print 'Customer',int(row[0])+1,'Tardiness',T[int(row[0])].x

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
                    if i==4:
                        continue
                    else:
                        if y[int(row[0]),i].x>0:
                                print 'Customer',int(row[0])+1,'arc',i,' using 3PL','Trans_cost',F*int(row[2])
                                threePLCost+=F*int(row[2])        
    for row in customer:
            for i in nodes:
                if i==4:
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
    print 'MIP SOLUTION 3 ARCS'
    print 'customer size',len(customer)
    print 'Trans_Cost',TransCost
    print '3PL_Cost',threePLCost
    print 'Total_Trans_Cost',TotalTransCost
    print 'Total_Penalty_Cost',TotalTardinessCost
    print 'Total_Cost',TotalCost
    
    #G size is nmt, similar to pi. 
    #G = LinExpr()
    for k in modes:
        for s in departure:
            for i in nodes:
                if i==4:
                    continue
                else:
                    for row in customer:
                        if X[int(row[0]),i,k,s].x>0:
                            #print 'test',X[int(row[0]),i,k,s].x # why X=0 will also be shown?
                            #if you print X[int(row[0]),i,k,s], then all the X will be shown
                            G=G+int(row[2])*X[int(row[0]),i,k,s].x
                    #print 'middle G',G, 'i,k,s',i,k,s
                    G=G-arc_C[i,k,s]
    #print 'G',G
    for k in modes:
        for s in departure:
            for i in nodes:
                #a=LinExpr()
                if i==4:
                    continue
                else:
                    for row in customer:
                        if X[int(row[0]),i,k,s].x>0:
                            GG[i,k,s]=GG[i,k,s]+int(row[2])*X[int(row[0]),i,k,s].x
                    GG[i,k,s]=(GG[i,k,s]-arc_C[i,k,s])*alpha# where is the problem?
    #print 'size of GG',len(GG)
    #print 'size of pi',len(pi)
    #K=alpha*GG
    #print 'K',K
                    
    #define alpha, intial alpha=1, then become smaller. 
    #alpha=sigma*(Z_fea-Z)/(G*G)
    #update pi,pi is three degree of n, m ,t. also GG, same degree
    for k in modes:
        for s in departure:
            for i in nodes:
                if i==4:
                    continue
                else:
                    pi[i,k,s]=max(0,pi[i,k,s]+GG[i,k,s])
    alpha=alpha/3.0 
    print 'o',o,'alpha',alpha,'Z',Z,'Z_fea',Z_fea
    #t=t/3.0
    if G<=0 and Z>=Z_fea:
        Z_fea=Z
    else:
        Z_fea=Z_fea# update Z_fea if possible
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
