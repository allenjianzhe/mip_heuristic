#-*- coding: utf-8 -*-
#file name 32516H.pyh  based on netflow051215MIP, delete Tardiness, change 3PL to arc. 
#guolei:这个函数实现的功能可以是得到优化后的x，然后带入算法二，更新容量
import sys
sys.path.append('F:/gurobi651/win32/python27/lib/gurobipy') #lenovo
from gurobipy import *
from read111115 import *
import time   
start_time=time.clock()
F=1250
M=1000000000
start_time=time.clock()
pi={}
for i in nodes:
    if i==4:
        continue
    else:
        for k in modes:
            for s in departure:
                pi[i,k,s]=0
                
def MIP_OneCustomer(m,customer,arc_C,kkk,pi):#XH
        ending_time={}
        ####################################################################################################
        #decision variable XH: binaryh variable. XH[customer,i,i+1,m,k]
        XH = {}
        for row in customer:
            for i in nodes:
                if i==4:
                    continue
                else:
                    for k in modes:
                        for s in departure:
                            #print row[0]
                            XH[int(row[0]),i,k,s]=m.addVar(vtype=GRB.BINARY,name='XH_%s_%s_%s_%s'%(int(row[0]),i,k,s))
        m.update()

        expr1=LinExpr()#expr1:the transportation cost related with XH
        for row in customer:
            for i in nodes:
                if i==4:
                    continue
                else:
                    for k in modes:
                        for s in departure:
                            expr1=expr1+XH[int(row[0]),i,k,s]*int(row[2])*arc_trans_cost[int(row[0]),i,k]
        #expr2:cost with pi
##        expr2 = LinExpr()
##        for k in modes:
##            for s in departure:
##                for i in nodes:
##                    a=LinExpr()
##                    if i==4:
##                        continue
##                    else:
##                        for row in customer:
##                                a.addTerms(int(row[2]),XH[int(row[0]),i,k,s])
##                        a.add(-1,arc_C[i,k,s])
##                    expr2=expr2+pi[i,k,s]*a  
##        m.update()

        yh={}#主要针对的是自身的运输能力，设置第三方的变量#decision variable yh: binaryh variable of 3PL
        for row in customer:
            for i in nodes:
                if i==4:
                    continue
                else:
                    yh[int(row[0]),i]=m.addVar(vtype=GRB.BINARY,name='yh_%s_%s'%(int(row[0]),i))     
        m.update()

        expr3=LinExpr()        #expr3:cost related with yh, 3PL
        for row in customer:
            for i in nodes:
                if i==4:
                    continue
                else:
                    expr3=expr3+yh[int(row[0]),i]*int(row[2])*F
                    

        t={} #decision variable: arrive time at each node.,t[int(row[0]),i] is arrive time of customer int(row[0]) at arc i.
        for row in customer:
            for i in nodes:
                if i==4:
                    continue
                else:
                    t[int(row[0]),i]=m.addVar(vtype='C',name='nodeTime_%s_%s'%(int(row[0]),i))  
        #decision variable:Time tardiness of customer
        #T[int(row[0])] is tardiness of customer int(row[0])
        T={}
        for row in customer:
                T[int(row[0])]=m.addVar(vtype='C',name='Tardiness_%s'%(int(row[0])))
        m.update()
        #expr4:cost of time tardiness penaltyh 
        expr4=LinExpr()
        for row in customer:
            expr4 += T[int(row[0])] * int(row[2]) * int(row[4])

        #######################################
        #m.setObjective(expr1+expr2+expr3+expr4)
        m.setObjective(expr1+expr3+expr4)#为什么还需要优化第三方的
        ####################################################################################################
        #Constraint 3.2 for each customer, each link, onlyh one plan can be selected
        for row in customer:#约束为一个客户
            if row==kkk:
                for i in nodes:
                    if i==4:
                        continue
                    else:
                        expr = LinExpr()       
                        for k in modes:
                                for s in departure:
                                        expr.addTerms(1.0,XH[int(row[0]),i,k,s])#1.0*XH
                        expr.add(yh[int(row[0]),i])#1.0*XH + yh
                        m.addConstr(expr, GRB.EQUAL, 1,name='One_%s_%s_%s_%s'%(int(row[0]),i,k,s))#1.0*XH + yh = 1，这个只是说明不选择第三方的啊
        m.update()
        ####################################################################################################
        #Constraint binartyh of 3PL
        for row in customer:
            if row==kkk:
                for i in nodes:
                    if i==1 or i==4:
                        continue
                    else:
                        m.addConstr(yh[int(row[0]),i-1],GRB.LESS_EQUAL,yh[int(row[0]),i],name='one3pl_%s_%s'%(int(row[0]),i))
        #constraint 3.4 arc capacityh
        for k in modes:
            for s in departure:
                for i in nodes:
                    if i==4:
                        continue
                    else:
                        expr = LinExpr()
                        for row in customer:
                            if row ==kkk:
                                expr.addTerms(int(row[2]),XH[int(row[0]),i,k,s])#Q*XH
                        expr.addConstant(-1*arc_C[i,k,s])#
                        m.addConstr(expr,GRB.LESS_EQUAL, 0,'arcCapacityh_%s_%s_%s_%s'%(int(row[0]),i,k,s))      
        m.update()                                          
        #constraint 3.5 time constraint One
        for row in customer:
            if row==kkk:
                for i in nodes:
                    if i==4:
                        continue
                    else: 
                        expr = LinExpr()                
                        for k in modes:
                                for s in departure:                                            
                                        expr.addTerms(dT[i,k,s]+trans_time[i,k],XH[int(row[0]),i,k,s])
                        expr.add(-1*yh[int(row[0]),i]*M)
                        m.addConstr(expr,GRB.LESS_EQUAL,t[int(row[0]),i],name='timeConstr1_%s_%s'%(int(row[0]),i))                        
        m.update()                    

        for row in customer:#constraint 3.6 time constraint Two
            if row==kkk:
                for i in nodes:                    
                        expr1 = LinExpr()
                        if i==1 or i==4:
                                continue
                        else:
                                for k in modes:
                                        for s in departure:                                            
                                                expr1.addTerms(dT[i,k,s],XH[int(row[0]),i,k,s])
                                expr1.add(yh[int(row[0]),i])
                                m.addConstr(expr1,GRB.GREATER_EQUAL,t[int(row[0]),i-1],name='timeConstr2_%s_%s'%(int(row[0]),i))
        m.update()

        for row in customer:#definition of T
            if row==kkk:
                for k in modes:
                    for s in departure:
                        if XH[int(row[0]),3,k,s]>0:
                            ending_time[int(row[0])]=(dT[3,k,s]+trans_time[3,k])*XH[int(row[0]),3,k,s]
                            if t[int(row[0]),3]>DD[int(row[0])]:
                                m.addConstr(T[int(row[0])],GRB.EQUAL,t[int(row[0]),3]-DD[int(row[0])],name='Tardiness_%s'%(int(row[0])) )
        m.update()
        m.optimize()
        m.__data=XH,yh,t,T,ending_time
        return m,XH,yh,t,T,m.objVal
def expr1_value(XH):
    expr1=0
    for row in customer:
        for i in nodes:
            if i==4:
                continue
            else:
                for k in modes:
                    for s in departure:
                        expr1=expr1+XH[int(row[0]),i,k,s].x*int(row[2])*arc_trans_cost[int(row[0]),i,k]
    return expr1
    
def expr2_value(XH,pi):
    k2=0
    for k in modes:
        for s in departure:
            for i in nodes:
                a=0
                if i==4:
                    continue
                else:
                    for row in customer:
                        if XH[int(row[0]),i,k,s].x >0:
                            a=a+int(row[2])*XH[int(row[0]),i,k,s].x
                    if a==0:#make sure whether XH==1, so that we wont add the 0 in the following and make sure a is bigger than 0.
                        a=a
                    else:
                        a=a-arc_C[i,k,s]  #print a,'a', 'after all the customer sum'
                k2=k2+pi[i,k,s]*a
    return k2
    
def expr3_value(yh):
    expr3=0
    for row in customer:
        for i in nodes:
            if i==4:
                continue
            else:
                expr3=expr3+yh[int(row[0]),i].x*int(row[2])*F
    return expr3
def expr4_value(T):
    expr4=0
    for row in customer:
        expr4=expr4+T[int(row[0])].x*int(row[2])*int(row[4])
    return expr4


aaa=[]
XH_list=[]
yh_list=[]
obj_total=0
obj_list=[]
TransCost=0

for kkk in customer:
    m = Model('MIP_OneCustomer')
    this_run_m,XH,yh,t,T,obj=MIP_OneCustomer(m,customer,arc_C,kkk,pi)

    threePLCost=0
    TransCost=0
    TotalTransCost=0
    TotalTardinessCost=0
    TotalCost=0
    if this_run_m.status == GRB.status.OPTIMAL:   # get rid of for row in customer and problem solved.
        for i in nodes[:-1]:
            if yh[int(kkk[0]),i].x==1:
                yh_list.append(yh[int(kkk[0]),i])
            for k in modes:
                for s in departure:
                    if XH[int(kkk[0]),i,k,s].x > 0:
                        a=[]
                        TransCost+=arc_trans_cost[int(kkk[0]),i,k]*int(kkk[2])
                        a.append(XH[int(kkk[0]),i,k,s])
                        arc_C[i,k,s]=arc_C[i,k,s]-int(kkk[2])
                        XH_list.append(a)

    obj_total+=obj
    obj_list.append(obj)
print 'len(yh_list)',len(yh_list)
print yh_list
print 'len(XH_list)',len(XH_list)
print XH_list
print 'computer time (seconds): ',time.clock() - float(start_time)
print 'obj_total', obj_total
print 'obj', obj