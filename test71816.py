#file name netflow71816.py  based on netflow051215MIP, delete Tardiness, change 3PL to arc. 
import sys
#sys.path.append('C:/gurobi563/win32/python27/lib/gurobipy')
sys.path.append('C:/gurobi605/win32/python27/lib/gurobipy')
#sys.path.append('C:/gurobi604/win32/python27/lib/gurobipy')  # for apple
from gurobipy import *
from read70816 import *
import time   

from netflow71816 import MIP2
def MIP3(m,customer,C,all_fixed_x_idxes):
    ####################################################################################################
    #decision variable X: binary variable. X[customer,i,i+1,m,k]
    X = {}
    for row in customer:
        for n in nodes:
            if n==4:
                continue
            else:
                for k in modes:
                    for s in departure:
                        X[int(row[0]),n,k,s]=m.addVar(obj=int(row[2])*f[n,k],vtype=GRB.BINARY,name='X_%s_%s_%s_%s'%(int(row[0]),n,k,s))
    m.update()
    for (row,n,k,s)in all_fixed_x_idxes:
        print (row,n,k,s),'$$$$$$$$$$$$$$$$$'
        m.addConstr(X[row,n,k,s],GRB.EQUAL,1)
    #decision variable y: binary variable of 3PL
    y={}
    for row in customer:
        for n in nodes:
            if n==4:
                continue
            else:
                y[int(row[0]),n]=m.addVar(obj=int(row[2])*F,vtype=GRB.BINARY,name='y_%s_%s'%(int(row[0]),n))     
    m.update()
    #decision variable: arrive time at each node
    t={}
    for row in customer:
        for n in nodes:
            if n==4:
                continue
            else:
                t[int(row[0]),n]=m.addVar(obj=0,vtype='C',name='nodeTime_%s_%s'%(int(row[0]),n))  
    #decision variable:Time tardiness of customer
    TD={}
    for row in customer:
            TD[int(row[0])]=m.addVar(obj=int(row[2])*int(row[4]),vtype='C',name='Tardiness_%s'%(int(row[0])))
    m.update()
    ####################################################################################################
    #Constraint 3.2 for each customer, each link, only one plan can be selected
    for row in customer:
        for n in nodes:
            if n==4:
                continue
            else:
                expr = LinExpr()       
                for k in modes:
                        for s in departure:
                                expr.addTerms(1.0,X[int(row[0]),n,k,s])
                expr.add(y[int(row[0]),n])
                m.addConstr(expr, GRB.EQUAL, 1,name='One_%s_%s_%s_%s'%(int(row[0]),n,k,s))
    m.update()
    ####################################################################################################
    #Constraint binarty of 3PL
    for row in customer:
        for n in nodes:
            if n==1 or n==4:
                continue
            else:
                m.addConstr(y[int(row[0]),n-1],GRB.LESS_EQUAL,y[int(row[0]),n],name='one3pl_%s_%s'%(int(row[0]),n))
    #constraint 3.4 arc capacity
    for k in modes:
        for s in departure:
            for n in nodes:
                if n==4:
                    continue
                else:
                    expr = LinExpr()
                    for row in customer:
                            expr.addTerms(int(row[2]),X[int(row[0]),n,k,s])
                    expr.addConstant(-1*C[n,k,s])
                    m.addConstr(expr,GRB.LESS_EQUAL, 0,'arcCapacity_%s_%s_%s_%s'%(int(row[0]),n,k,s))      
    m.update()                                          
    #constraint 3.5 time constraint One
    for row in customer:        
            for n in nodes:
                if n==4:
                    continue
                else: 
                    expr = LinExpr()                
                    for k in modes:
                            for s in departure:                                            
                                    expr.addTerms(dT[n,k,s]+tau[n,k],X[int(row[0]),n,k,s])
                    expr.add(-1*y[int(row[0]),n]*M)
                    m.addConstr(expr,GRB.LESS_EQUAL,t[int(row[0]),n],name='timeConstr1_%s_%s'%(int(row[0]),n))                        
    m.update()                    
    #constraint 3.6 time constraint Two
    for row in customer:        
            for n in nodes:                    
                    expr1 = LinExpr()
                    if n==1 or n==4:
                            continue
                    else:
                            for k in modes:
                                    for s in departure:                                            
                                            expr1.addTerms(dT[n,k,s],X[int(row[0]),n,k,s])
                            expr1.add(y[int(row[0]),n])
                            m.addConstr(expr1,GRB.GREATER_EQUAL,t[int(row[0]),n-1],name='timeConstr2_%s_%s'%(int(row[0]),n))
    m.update()
    #definition of T
    for row in customer:
        for k in modes:
            for s in departure:
                if X[int(row[0]),3,k,s]>0:
                    ending_time[int(row[0])]=(dT[3,k,s]+tau[3,k])*X[int(row[0]),3,k,s]
                    if t[int(row[0]),3]>DD[int(row[0])]:
                        m.addConstr(TD[int(row[0])],GRB.EQUAL,t[int(row[0]),3]-DD[int(row[0])],name='Tardiness_%s'%(int(row[0])) )
    m.update()    
    m.__data=X,y,t,TD,ending_time
    return m
####################################################################################################

if __name__ == '__main__':
    start_time=time.clock()
    


    ending_time={}
    C={}
    C=getC(nodes,modes,departure)
    #Distance: each arc distance
    Distance={}
    Distance=getDistance()
    #tau: each mode at each arc transporatation time
    tau={}
    tau=getTau(nodes,modes,getDistance())
    #f: unit cost of mode at each arc
    f={}
    f=getf(nodes,modes,getDistance())
    #dT: departure time at each arc
    dT={}
    dT=getdT()
    all_fixed_x_idxes=[]
    all_fixed_x_idxes.append((0,1,2,1))
    all_fixed_x_idxes.append((0,2,3,1))
    all_fixed_x_idxes.append((0,3,4,1))
    print '-'*50
    print customer
    print C
    print all_fixed_x_idxes
    m = Model('MIP')
    MIP2(m,customer,C,all_fixed_x_idxes)
    m.optimize()
    X,y,t,TD,ending_time=m.__data
##    q=m.objVal
##    print q,'$$$$$$$$$$$'
    ##print "\n"
    print 'Basic info'
    print 'customer size',len(customer)
    print '\n'
    for row in customer:
        print 'Customer',int(row[0])+1,'Destination ',row[1], 'quantity ',int(row[2]),'DD',int(row[3]),'penalty',int(row[4]),'Tardiness',TD[int(row[0])].x
    print "\n"
    ####print 'Summary solution'                    
    threePLCost=0
    TransCost=0
    TotalTransCost=0
    TotalTardinessCost=0
    TotalCost=0
    if m.status == GRB.status.OPTIMAL:
            for row in customer:
                #print 'Customer',int(row[0]),'Tardiness',T[int(row[0])].x
                TotalTardinessCost+=TD[int(row[0])].x*int(row[4])*int(row[2])
                for n in nodes:
                    if n==4:
                        continue
                    else:
                        if y[int(row[0]),n].x>0:
                                print 'Customer',int(row[0])+1,'arc',n,' using 3PL','Trans_cost',F*int(row[2])
                                threePLCost+=F*int(row[2])        
    TotalTransCost=0
    for row in customer:
            for n in nodes:
                if n==4:
                    continue
                else:
                    for k in modes:
                        for s in departure:
                                if X[int(row[0]),n,k,s].x > 0:
                                        print 'Customer',int(row[0])+1,'link',n,'arc_mode_num',k,'departureTimeIndex',s,'arc_cost',f[n,k]*int(row[2]),'start_Time',dT[n,k,s],'Trans_time',tau[n,k],'t',t[int(row[0]),n].x,'real_arrive_time',dT[n,k,s]+tau[n,k]
                                        TransCost+=f[n,k]*int(row[2])
    TotalTransCost=TransCost+threePLCost
    TotalCost=  TotalTardinessCost+   TotalTransCost
    print '\n'
    print 'MIP SOLUTION 3 ARCS'

    print 'Trans_Cost',TransCost
    print '3PL_Cost',threePLCost
    print 'Total_Trans_Cost',TotalTransCost
    print 'Total_Penalty_Cost',TotalTardinessCost
    print 'Total_Cost',TotalCost
    print 'computer time (seconds): ',time.clock() - float(start_time)
    print '\n' 
