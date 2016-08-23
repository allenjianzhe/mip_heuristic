#file name 052715.py  based on 052615
import sys
#sys.path.append('C:/gurobi604/win64/python27/lib/gurobipy')
sys.path.append('C:/gurobi604/win32/python27/lib/gurobipy')  # for apple
from gurobipy import *
import time   
start_time=time.clock()
from read052715 import *
m = Model('MIP')
M=1000000000
F=600000
y={}
for row in customer:
    for i in nodes:
        y[int(row[0]),i]=0
def MIP1(m,customer,arc_C):
    ####################################################################################################
    #decision variable X: binary variable. X[customer,i,i+1,m,k]
    X = {}
    for row in customer:
        for i in nodes:
            if i == 2:
                continue
            else:
                for k in modes:
                    for s in departure:
                        X[int(row[0]),i,k,s]=m.addVar(obj=int(row[2])*arc_trans_cost[int(row[0]),i,k],vtype=GRB.BINARY,name='X_%s_%s_%s_%s'%(int(row[0]),i,k,s))
    m.update()                                  
    #decision variable y: binary variable of 3PL
    global y
    for row in customer:
        for i in nodes:
            y[int(row[0]),i]=m.addVar(obj=int(row[2])*F,vtype=GRB.BINARY,name='y_%s_%s'%(int(row[0]),i))     
    m.update()
    #decision variable: arrive time at each node
    t={}
    for row in customer:
        for i in nodes:
            t[int(row[0]),i]=m.addVar(obj=0,vtype='C',name='nodeTime_%s_%s'%(int(row[0]),i))  
    #decision variable:Time tardiness of customer
    T={}
    for row in customer:
            T[int(row[0])]=m.addVar(obj=int(row[2])*int(row[4]),vtype='C',name='Tardiness_%s'%(int(row[0])))
    m.update()
    ####################################################################################################
    #Constraint 3.2 for each customer, each link, only one plan can be selected
    for row in customer:
        for i in nodes:
            if i==2:
                continue
            else:
                expr = LinExpr()       
                for k in modes:
                        for s in departure:
                                expr.addTerms(1.0,X[int(row[0]),i,k,s])
                expr.add(y[int(row[0]),i])
                m.addConstr(expr, GRB.EQUAL, 1,name='One_%s_%s_%s_%s'%(int(row[0]),i,k,s))
    m.update()
    ####################################################################################################
    #constraint 3.4 arc capacity
    for k in modes:
        for s in departure:
            for i in nodes:
                if i==2:
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
                if i==2:
                    continue
                else:
                    expr = LinExpr()                
                    for k in modes:
                            for s in departure:                                            
                                    expr.addTerms(dT[i,k,s]+trans_time[i,k],X[int(row[0]),i,k,s])
                    expr.add(-1*y[int(row[0]),i]*M)
                    m.addConstr(expr,GRB.LESS_EQUAL,t[int(row[0]),i],name='timeConstr1_%s_%s'%(int(row[0]),i))                        
    m.update()                    
    #constraint 3.6 time constraint Two, 新一期的出发时间大于上一期的到达时间
    for row in customer:
        for k in modes:
            for s in departure:
                if X[int(row[0]),1,k,s]>0:
                    #ending_time[int(row[0])]=(dT[1,k,s]+trans_time[2,k])*X[int(row[0]),1,k,s]
                    if t[int(row[0]),1]>DD[int(row[0])]:
                        m.addConstr(T[int(row[0])],GRB.EQUAL,t[int(row[0]),1]-DD[int(row[0])],name='Tardiness_%s'%(int(row[0])) )
    m.update()
    m.__data=X,y,t,T
    return m
####################################################################################################
MIP1(m,customer,arc_C)
m.optimize()
X,y,t,T=m.__data
##    print "\n"
##    print 'Basic info'
##    for row in customer:
##        print 'Customer',int(row[0])+1, 'quantity ',int(row[2]),'DD',DD[int(row[0])]+drift,'Tardiness',T[int(row[0])].x
##    print "\n"
threePLCost1=0
TransCost1=0
TotalTransCost1=0
TotalTardinessCost1=0
TotalCost1=0
arrive_time={}
if m.status == GRB.status.OPTIMAL:
        for row in customer:
            for i in nodes:
                if i==2:
                    continue
                else:
                    if y[int(row[0]),i].x>0:
                            #print 'Customer',int(row[0])+1,'arc',i,' using 3PL','Trans_cost',F*int(row[2])
                            threePLCost1+=F*int(row[2])
                            global arrive_time
                            arrive_time[int(row[0])]=0       
TotalTransCost1=0
for row in customer:
        for i in nodes:
            if i==2:
                continue
            else:
                for k in modes:
                    for s in departure:
                            if X[int(row[0]),i,k,s].x > 0:
                                    #print 'Customer',int(row[0])+1,'link',i,'arc_mode_num',k,'departureTimeIndex',s,'arc_cost',arc_trans_cost[int(row[0]),i,k]*int(row[2]),'start_Time',dT[i,k,s],'Trans_time',trans_time[i,k],'t',t[int(row[0]),i].x,'real_arrive_time',dT[i,k,s]+trans_time[i,k]
                                    TransCost1+=arc_trans_cost[int(row[0]),i,k]*int(row[2])
                                    global arrive_time
                                    arrive_time[int(row[0])]=dT[1,k,s]+trans_time[1,k]
TotalTransCost1=TransCost1+threePLCost1
TotalCost1=  TotalTardinessCost1+   TotalTransCost1                   
####################################################################################################
from read052715_2 import *
m2 = Model('MIP')
y2={}
for row in customer:
    for i in nodes:
        y2[int(row[0]),i]=0
def MIP2(m2,customer,arc_C):    
    #decision variable X: binary variable. X[customer,i,i+1,m,k]
    X2 = {}
    for row in customer:
        for i in nodes:
            if i==3:
                continue
            else:
                for k in modes:
                    for s in departure:
                        X2[int(row[0]),i,k,s]=m2.addVar(obj=int(row[2])*arc_trans_cost[int(row[0]),i,k],vtype=GRB.BINARY,name='X_%s_%s_%s_%s'%(int(row[0]),i,k,s))
    m2.update()                                     
    #decision variable y: binary variable of 3PL
    global y2
    for row in customer:
        for i in nodes:
            if i==3:
                continue
            else:
                y2[int(row[0]),i]=m2.addVar(obj=int(row[2])*F,vtype=GRB.BINARY,name='y_%s_%s'%(int(row[0]),i))     
    m2.update()
    #decision variable: arrive time at each node
    t={}
    for row in customer:
        for i in nodes:
            if i==3:
                continue
            else:
                t[int(row[0]),i]=m2.addVar(obj=0,vtype='C',name='nodeTime_%s_%s'%(int(row[0]),i))  
    #decision variable:Time tardiness of customer
    T={}
    for row in customer:
            T[int(row[0])]=m2.addVar(obj=int(row[2])*int(row[4]),vtype='C',name='Tardiness_%s'%(int(row[0])))
    m2.update()
    ####################################################################################################
    #Constraint 3.2 for each customer, each link, only one plan can be selected
    for row in customer:
        for i in nodes:
            if i==3:
                continue
            else:
                expr = LinExpr()       
                for k in modes:
                        for s in departure:
                                expr.addTerms(1.0,X2[int(row[0]),i,k,s])
                expr.add(y2[int(row[0]),i])
                m2.addConstr(expr, GRB.EQUAL, 1,name='One_%s_%s_%s_%s'%(int(row[0]),i,k,s))
    m2.update()
    #############################################################################
    #New constraint between y and y2
    for row in customer:
        global y
        if y[int(row[0]),1].x>0:
            m2.addConstr(y2[int(row[0]),2],GRB.EQUAL,1,name='yConstre_%s'%(int(row[0])))
    #constraint 3.4 arc capacity
    for k in modes:
        for s in departure:
            for i in nodes:
                if i==3:
                    continue
                else:
                    expr = LinExpr()
                    for row in customer:
                            expr.addTerms(int(row[2]),X2[int(row[0]),i,k,s])
                    expr.addConstant(-1*arc_C[i,k,s])
                    m2.addConstr(expr,GRB.LESS_EQUAL, 0,'arcCapacity_%s_%s_%s_%s'%(int(row[0]),i,k,s))      
    m2.update()                                          
    #constraint 3.5 time constraint One
    for row in customer:        
            for i in nodes:
                if i==3:
                    continue
                else:
                    expr = LinExpr()                
                    for k in modes:
                        for s in departure:
                            expr.addTerms(dT[i,k,s]+trans_time[i,k],X2[int(row[0]),i,k,s])
                    expr.add(-1*y2[int(row[0]),i]*M)
                    m2.addConstr(expr,GRB.LESS_EQUAL,t[int(row[0]),i],name='timeConstr1_%s_%s'%(int(row[0]),i))                        
    m2.update()                    
    # constraint 3.6 NEW time constraint
    for row in customer:
        expr = LinExpr()
        for i in nodes:
            if i==3:
                continue
            else:
                for k in modes:
                    for s in departure:
                        if X2[int(row[0]),i,k,s]>0:
                            global arrive_time
                            expr.addTerms(dT[i,k,s],X2[int(row[0]),i,k,s])
        m2.addConstr(expr,GRB.GREATER_EQUAL, arrive_time[int(row[0])],name='timeConstr2_%s'%(int(row[0])))
    m2.update()
    for row in customer:
        for k in modes:
            for s in departure:
                if X2[int(row[0]),2,k,s]>0:
                    if t[int(row[0]),2]>DD[int(row[0])]:
                        m2.addConstr(T[int(row[0])],GRB.EQUAL,t[int(row[0]),2]-DD[int(row[0])],name='Tardiness_%s'%(int(row[0])) )
    m2.update()
    m2.__data=X2,y2,t,T
    return m2
####################################################################################################
MIP2(m2,customer,arc_C)
m2.optimize()
X2,y2,t,T=m2.__data
##    print "\n"
##    print 'Basic info'
##    for row in customer:
##        print 'Customer',int(row[0])+1, 'quantity ',int(row[2]),'DD',DD[int(row[0])],'Tardiness',T[int(row[0])].x
##    print "\n"
##    print 'Summary solution'
threePLCost2=0
TransCost2=0
TotalTransCost2=0
TotalTardinessCost2=0
TotalCost2=0

if m2.status == GRB.status.OPTIMAL:
        for row in customer:
            for i in nodes:
                if i==3:
                    continue
                else:
                    if y2[int(row[0]),i].x>0:
                            #print 'Customer',int(row[0])+1,' using 3PL','Trans_cost',F*int(row[2])
                            threePLCost2+=F*int(row[2])
for row in customer:
        for i in nodes:
            if i==3:
                continue
            else:
                for k in modes:
                    for s in departure:
                            if X2[int(row[0]),i,k,s].x > 0:
                                    #print 'Customer',int(row[0])+1,'link',i,'arc_mode_num',k,'departureTimeIndex',s,'arc_cost',arc_trans_cost[int(row[0]),i,k]*int(row[2]),'start_Time',dT[i,k,s],'Trans_time',trans_time[i,k],'t',t[int(row[0]),i].x,'real arrive_time',dT[i,k,s]+trans_time[i,k]
                                    TransCost2+=arc_trans_cost[int(row[0]),i,k]*int(row[2])
    ##        print '\n'
TotalTransCost2=TransCost2+threePLCost2
TotalCost2=  TotalTardinessCost2+   TotalTransCost2
####################################################################################################
####################################################################################################
####################################################################################################
m3 = Model('MIP3')
from read052715_3 import *
def MIP3(m3,customer,arc_C):    
    #decision variable X: binary variable. X[customer,i,i+1,m,k]
    X3 = {}
    for row in customer:
        for i in nodes:
            if i == 4:
                continue
            else:
                for k in modes:
                    for s in departure:
                        X3[int(row[0]),i,k,s]=m3.addVar(obj=int(row[2])*arc_trans_cost[int(row[0]),i,k],vtype=GRB.BINARY,name='X_%s_%s_%s_%s'%(int(row[0]),i,k,s))
    m3.update()                                        
    #decision variable y: binary variable of 3PL
    y3={}
    for row in customer:
        for i in nodes:
            y3[int(row[0]),i]=m3.addVar(obj=int(row[2])*F,vtype=GRB.BINARY,name='y_%s_%s'%(int(row[0]),i))     
    m3.update()
    #decision variable: arrive time at each node
    t={}
    for row in customer:
        for i in nodes:
            t[int(row[0]),i]=m3.addVar(obj=0,vtype='C',name='nodeTime_%s_%s'%(int(row[0]),i))  
    #decision variable:Time tardiness of customer
    T={}
    for row in customer:
            T[int(row[0])]=m3.addVar(obj=int(row[2])*int(row[4]),vtype='C',name='Tardiness_%s'%(int(row[0])))
    m3.update()
    ####################################################################################################
    #Constraint 3.2 for each customer, each link, only one plan can be selected
    for row in customer:
        for i in nodes:
            if i==4:
                continue
            else:
                expr = LinExpr()       
                for k in modes:
                        for s in departure:
                                expr.addTerms(1.0,X3[int(row[0]),i,k,s])
                expr.add(y3[int(row[0]),i])
                m3.addConstr(expr, GRB.EQUAL, 1,name='One_%s_%s_%s_%s'%(int(row[0]),i,k,s))
    m3.update()
    ####################################################################################################
    #constraint 3.4 arc capacity
    for k in modes:
        for s in departure:
            for i in nodes:
                if i==4:
                    continue
                else:
                    expr = LinExpr()
                    for row in customer:
                            expr.addTerms(int(row[2]),X3[int(row[0]),i,k,s])
                    expr.addConstant(-1*arc_C[i,k,s])
                    m3.addConstr(expr,GRB.LESS_EQUAL, 0,'arcCapacity_%s_%s_%s_%s'%(int(row[0]),i,k,s))      
    m3.update()                                          
    #constraint 3.5 time constraint One
    for row in customer:        
            for i in nodes:
                if i==4:
                    continue
                else:
                    expr = LinExpr()                
                    for k in modes:
                            for s in departure:                                            
                                    expr.addTerms(dT[i,k,s]+trans_time[i,k],X3[int(row[0]),i,k,s])
                    expr.add(-1*y3[int(row[0]),i]*M)
                    m3.addConstr(expr,GRB.LESS_EQUAL,t[int(row[0]),i],name='timeConstr1_%s_%s'%(int(row[0]),i))                        
    m3.update()                    
    #constraint 3.6 time constraint Two
    for row in customer:
        expr = LinExpr()
        for i in nodes:
            if i==4:
                continue
            else:
                for k in modes:
                    for s in departure:
                        if X3[int(row[0]),i,k,s]>0:
                            global arrive_time
                            expr.addTerms(dT[i,k,s],X3[int(row[0]),i,k,s])
        m3.addConstr(expr,GRB.GREATER_EQUAL, arrive_time[int(row[0])],name='timeConstr2_%s'%(int(row[0])))
    m3.update()

    global ending_time
    for row in customer:
        for k in modes:
            for s in departure:
                if X3[int(row[0]),3,k,s]>0:
                    #ending_time[int(row[0])]=(dT[3,k,s]+trans_time[3,k])*X[int(row[0]),3,k,s]
                    if t[int(row[0]),3]>DD[int(row[0])]:
                        m3.addConstr(T[int(row[0])],GRB.EQUAL,t[int(row[0]),3]-DD[int(row[0])],name='Tardiness_%s'%(int(row[0])) )
    m3.update()    
    m3.__data=X3,y3,t,T
    return m3
####################################################################################################
MIP3(m3,customer,arc_C)
m3.optimize()
X3,y3,t,T=m3.__data
##    print "\n"
##    print 'Basic info'
##    for row in customer:
##        print 'Customer',int(row[0])+1, 'quantity ',int(row[2]),'DD',DD[int(row[0])],'Tardiness',T[int(row[0])].x
##    print "\n"
##    print 'Summary solution'
threePLCost3=0
TransCost3=0
TotalTransCost3=0
TotalTardinessCost3=0
TotalCost3=0
if m3.status == GRB.status.OPTIMAL:
        for row in customer:
            TotalTardinessCost3+=T[int(row[0])].x*int(row[4])*int(row[2])
            for i in nodes:
                if y3[int(row[0]),i].x>0:
                        #print 'Customer',int(row[0])+1,'arc',i,' using 3PL','Trans_cost',F*int(row[2])
                        threePLCost3+=F*int(row[2])
arrive_time={}
for row in customer:
        for i in nodes:
            if i==4:
                continue
            else:
                for k in modes:
                    for s in departure:
                            if X3[int(row[0]),i,k,s].x > 0:
                                    #print 'Customer',int(row[0])+1,'link',i,'arc_mode_num',k,'departureTimeIndex',s,'arc_cost',arc_trans_cost[int(row[0]),i,k]*int(row[2]),'start_Time',dT[i,k,s],'Trans_time',trans_time[i,k],'t',t[int(row[0]),i].x,'real_arrive_time',dT[i,k,s]+trans_time[i,k]
                                    TransCost3+=arc_trans_cost[int(row[0]),i,k]*int(row[2])
                                    global arrive_time
                                    arrive_time[int(row[0])]=dT[3,k,s]+trans_time[3,k]
TotalTransCost3=TransCost3+threePLCost3
TotalCost3=  TotalTardinessCost3+   TotalTransCost3
TotalCost=TotalCost1+TotalCost2+TotalCost3


##    
##    print '\n'
##    print '3PL_Cost1',threePLCost1
##    print 'Trans_Cost1',TransCost1
##    print 'Total_Trans_Cost1',TotalTransCost1
##    print 'Total_Penalty_Cost1',TotalTardinessCost1
##    print 'Total_Cost1',TotalCost1
##
##    print '\n'
##    print '3PL_Cost2',threePLCost2
##    print 'Trans_Cost2',TransCost2
##    print 'Total_Trans_Cost2',TotalTransCost2
##    print 'Total_Penalty_Cost2',TotalTardinessCost2
##    print 'Total_Cost2',TotalCost2
##
##    print '\n'
##    print '3PL_Cost3',threePLCost3
##    print 'Trans_Cost3',TransCost3
##    print 'Total_Trans_Cost3',TotalTransCost3
##    print 'Total_Penalty_Cost3',TotalTardinessCost3
##    print 'Total_Cost3',TotalCost3
##
print '\n'
print 'H SOLUTION 3 ARCS'
print '3PL',threePLCost3+threePLCost2+threePLCost1
print 'Trans',TransCost1+TransCost2+TransCost3
print 'Total_Trans',TotalTransCost1+TotalTransCost2+TotalTransCost3
print 'Penalty',TotalTardinessCost3
print 'Total',TotalCost  
print '\n'                   


print 'computer time (seconds): ',time.clock() - float(start_time)
