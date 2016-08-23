#name Run60816

import sys
sys.path.append('C:/gurobi604/win32/python27/lib/gurobipy')
from gurobipy import *
import time
from func60716 import *

Z_list=[]
sigma=2
#set initial upper bound Zub
Zub=float("inf")
#Zub=763500
Zlb=-float("inf")
o=0
alpha=1
###in ordor to get the lower bound, we set pi=0 and run MIP to get it. 
###M=Model('MIP')
##print pi,'pi'
##(O,X,y,t,T,Z)=MIP(customer,arc_C,nodes,modes,departure,pi)
##threePLCost=0
##TransCost=0
##TotalTransCost=0
##TotalTardinessCost=0
##TotalCost=0
##if O.status == GRB.status.OPTIMAL:
##        for row in customer:
##            TotalTardinessCost+=T[int(row[0])].x*int(row[4])*int(row[2])
##            for i in nodes:
##                if i==4:
##                    continue
##                else:
##                    if y[int(row[0]),i].x>0:
##                            #print 'Customer',int(row[0])+1,'arc',i,' using 3PL','Trans_cost',F*int(row[2])
##                            threePLCost+=F*int(row[2])        
##for row in customer:
##        for i in nodes:
##            if i==4:
##                continue
##            else:
##                for k in modes:
##                    for s in departure:
##                            if X[int(row[0]),i,k,s].x > 0:
##                                    #print 'Customer',int(row[0])+1,'link',i,'arc_mode_num',k,'departureTimeIndex',s,'arc_cost',arc_trans_cost[int(row[0]),i,k]*int(row[2]),'start_Time',dT[i,k,s],'Trans_time',trans_time[i,k],'t',t[int(row[0]),i].x,'real_arrive_time',dT[i,k,s]+trans_time[i,k]
##                                    TransCost+=arc_trans_cost[int(row[0]),i,k]*int(row[2])
##TotalTransCost=TransCost+threePLCost
##TotalCost=  TotalTardinessCost+   TotalTransCost
##print '\n'
##print 'MIP SOLUTION 3 ARCS','first time to get the lower bound'
##print 'customer size',len(customer)
##print 'Trans_Cost',TransCost
##print '3PL_Cost',threePLCost
##print 'Total_Trans_Cost',TotalTransCost
##print 'Total_Penalty_Cost',TotalTardinessCost
##print 'Total_Cost',TotalCost
##Zlb=Z
##print '\n'
##print 'initial Zlb',Zlb,'$$$$$$$$$$$$$$$$$'
##Z_list=[]
##o=0
##print 'o',o,'alpha',alpha,'Zlb',Zlb,'Zub',Zub,'sigma',sigma
##GG={}
##for i in nodes:
##    if i==4:
##        continue
##    else:
##        for k in modes:
##            for s in departure:
##                GG[i,k,s]=0
##for k in modes:
##    for s in departure:
##        for i in nodes:
##            #a=LinExpr()
##            if i==4:
##                continue
##            else:
##                for row in customer:
##                    if X[int(row[0]),i,k,s].x>0:
##                        #print 'i,k,s',i,k,s
##                        #print 'GG[i,k,s]',GG[i,k,s]
##                        GG[i,k,s]=GG[i,k,s]+int(row[2])*X[int(row[0]),i,k,s].x
##                        #print 'GG[i,k,s]',GG[i,k,s]
##                GG[i,k,s]=GG[i,k,s]-arc_C[i,k,s]              
###print 'GG','\n',GG
###here we first time to update pi
##for k in modes:
##    for s in departure:
##        for i in nodes:
##            if i==4:
##                continue
##            else:
##                pi[i,k,s]=max(0,pi[i,k,s]+GG[i,k,s]*alpha)
##print 'pi','updated','\n',pi
Zlb_list=[]
Zub_list=[]

#update the upper bound, get feasible solution

while sigma>=0.05 and alpha!=0: 
#while o!=20:
##    yy=[]
##    XX1=[]
##    XX2=[]
##    XX3=[]
    #print 'main round',o
    #print 'o',o,'alpha',alpha,'Zlb',Zlb,'Zub',Zub,'sigma',sigma
    (m,X,y,t,T,Z,e1,e2,e3,e4)=MIP(customer,arc_C,nodes,modes,departure,pi)
##    print '*************main loop******************' 
##    print e1.getValue(),'X cost'
##    print e2.getValue(),'pi cost'
##    print e3.getValue(),'penalty'
##    print e4.getValue(),'T cost'
    
    #print X
##    Transfer(X,y)
##    print '#####################################$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$'
##    print 'XX1',XX1
##    print 'XX2',XX2
##    print 'XX3',XX3
##    print 'YY',yy
##    print '*************main loop******************'
##    print expr1_value(X),'transporation cost'
##    import sys
##    sys.exit()
##    print expr2_value(X,pi),'pi  cost'
##    print expr3_value(y),'y cost'
##    print expr4_value(T),'Time tardiness cost'
##    print '*************main loop*********************'
##    for row in customer:
##        print 'Customer',int(row[0])+1,'Demand Time',int(row[3]),'Tardiness',T[int(row[0])].x
##    print '\n'
    #print 'the ',o,' round'
    threePLCost=0
    TransCost=0
    TotalTransCost=0
    TotalTardinessCost=0
    TotalCost=0
    #print 'main round solution of subgradient method'
    if m.status == GRB.status.OPTIMAL:
            for row in customer:
                TotalTardinessCost+=T[int(row[0])].x*int(row[4])*int(row[2])
                for i in nodes:
                    if i==4:
                        continue
                    else:
                        if y[int(row[0]),i].x>0:
                                #print 'Customer',int(row[0])+1,'arc',i,' using 3PL','Trans_cost',F*int(row[2])
                                threePLCost+=F*int(row[2])        
    for row in customer:
            for i in nodes:
                if i==4:
                    continue
                else:
                    for k in modes:
                        for s in departure:
                                if X[int(row[0]),i,k,s].x > 0:
                                        #print 'Customer',int(row[0])+1,'link',i,'arc_mode_num',k,'departureTimeIndex',s,'arc_cost',arc_trans_cost[int(row[0]),i,k]*int(row[2]),'start_Time',dT[i,k,s],'Trans_time',trans_time[i,k],'t',t[int(row[0]),i].x,'real_arrive_time',dT[i,k,s]+trans_time[i,k]
                                        TransCost+=arc_trans_cost[int(row[0]),i,k]*int(row[2])
    TotalTransCost=TransCost+threePLCost
    TotalCost=  TotalTardinessCost+   TotalTransCost
##    print '\n'
    #print 'MIP SOLUTION 3 ARCS','o',o
    #print 'customer size',len(customer)
##    print 'Trans_Cost',TransCost
##    print '3PL_Cost',threePLCost
##    print 'Total_Trans_Cost',TotalTransCost
##    print 'Total_Penalty_Cost',TotalTardinessCost
##    print 'Total_Cost',TotalCost
    #G size is nmt, similar to pi. but G is a number
    G = 0
    for k in modes:
        for s in departure:
            for i in nodes:
                if i==4:
                    continue
                else:
                    for row in customer:
                        if X[int(row[0]),i,k,s].x>0:
                            G=G+int(row[2])*X[int(row[0]),i,k,s].x
                    G=G-arc_C[i,k,s]
##    print '\n'
    #print 'G',G
    GG={}
    for i in nodes:
        if i==4:
            continue
        else:
            for k in modes:
                for s in departure:
                    GG[i,k,s]=0
    for k in modes:
        for s in departure:
            for i in nodes:
                if i==4:
                    continue
                else:
                    for row in customer:
                        if X[int(row[0]),i,k,s].x>0:
                            GG[i,k,s]=GG[i,k,s]+int(row[2])*X[int(row[0]),i,k,s].x
                    GG[i,k,s]=GG[i,k,s]-arc_C[i,k,s]
    #print 'GG','\n',GG
    #update pi,pi is three degree of n, m ,t. also GG, same degree
##    print 'pi','\n',pi
##    for k in modes:
##        for s in departure:
##            for i in nodes:
##                if i==4:
##                    continue
##                else:
##                    pi[i,k,s]=max(0,pi[i,k,s]+GG[i,k,s]*alpha)
##    print 'pi','updated','\n',pi
    
    obj_total=0
    obj_list=[]
    X_list=[]
    y_list=[]
    transCost_list=[]
    piCost_list=[]
    yCost_list=[]
    TimeCost_list=[]
##    print '!!!!!!!!!!!!!!!!!!update upper bound start!!!!!!!!!!!!!!!!!!!!!'
##    print 'pi',pi
    for kkk in customer:
        this_run_m = Model('MIP_OneCustomer%s')
        this_run_m,X,y,t,T,obj,e21,e22,e23,e24=MIP_OneCustomer(arc_C,kkk,pi)
        
        transCost_list.append(e21.getValue())
        piCost_list.append(e22.getValue())
        yCost_list.append(e23.getValue())
        TimeCost_list.append(e24.getValue())
##        print '********************************************'
##        print e21.getValue(),'transporation cost'
##        print e22.getValue(),'pi  cost'
##        print e23.getValue(),'y cost'
##        print e24.getValue(),'Time tardiness cost'
##        print '********************************************'
        threePLCost=0
        TransCost=0
        TotalTransCost=0
        TotalTardinessCost=0
        TotalCost=0
        if this_run_m.status == GRB.status.OPTIMAL:    
            for i in nodes[:-1]:
                if y[int(kkk[0]),i].x==1:
                    raw_yidxes=y[int(kkk[0]),i].VarName.split('_')[1:]
                    #print raw_yidxes
                    #print raw_yidxes, 'test $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$'
                    y_list.append([int(e) for e in raw_yidxes])
                    #y_list.append(y[int(kkk[0]),i])
                    #print y_list,'test y_list'
                    TransCost+=F*int(kkk[2])
                for k in modes:
                    for s in departure:
                        if X[int(kkk[0]),i,k,s].x > 0:
                            TransCost+=arc_trans_cost[int(kkk[0]),i,k]*int(kkk[2])
                            arc_C[i,k,s]=arc_C[i,k,s]-int(kkk[2])
                            raw_idxes = X[int(kkk[0]),i,k,s].VarName.split('_')[1:]
                            X_list.append([int(e) for e in raw_idxes])
        obj_total+=obj
        obj_list.append(obj)
##    print 'Heuristic solution of fixing the customer one by one'
##    print 'len(y_list)',len(y_list)
##    print 'len(X_list)',len(X_list)
##    print 'X_list',X_list
##    print 'y_list',y_list

##    print 'transCost_list',transCost_list
##    print 'piCost_list',piCost_list
##    print sum(piCost_list),'sum of pi cost'
##    print 'yCost_list',yCost_list
##    print 'TimeCost_list',TimeCost_list
    
##    print 'obj_list',obj_list
    #print 'obj_total',obj_total
    
    Zub_temple=sum(transCost_list)+sum(yCost_list)+sum(TimeCost_list)
    #print 'Zub_temple',Zub_temple,'Zub',Zub
    Zub=min(Zub,Zub_temple)
    Zub_list.append(Zub)
    #print 'updated Zub',Zub
    #print 'Z',Z,'Zlb',Zlb
##    if Z>Zub:
##        Zlb=Zlb
##    else:
    Zlb=max(Z,Zlb)
    Zlb_list.append(Zlb)
    #print 'updated Zlb',Zlb
    alpha_temple=sigma*(Zub-Zlb)/(G*G)
    alpha=max(0,alpha_temple)
    #print 'o',o,'alpha',alpha,'Zlb',Zlb,'Zub',Zub,'sigma',sigma,'G',G,'after updated'
    for k in modes:
        for s in departure:
            for i in nodes:
                if i==4:
                    continue
                else:
                    pi[i,k,s]=max(0,pi[i,k,s]+GG[i,k,s]*alpha)
    #print pi,'#########################################'
    #print 'o',o,'alpha',alpha,'Zlb',Zlb,'Zub',Zub,'sigma',sigma    
    #print '\n'
    if len(Z_list)==3:
        if Z<min(Z_list):
            Z_list=[]
            Z_list.append(Z)
        else:
            sigma=0.5*sigma
            Z_list=[]
            Z_list.append(Z)
    else:
        Z_list.append(Z)
        o+=1
print '\n'
print 'size of customer',len(customer)
print '\n'
print 'computer time (seconds): ',time.clock() - float(start_time)
print '\n'
print 'o',o,'alpha',alpha,'sigma',sigma
print '\n'
print Zlb_list,'Zlb_list'
print '\n'
print Zub_list,'Zub_list'

##print plot_Zub(Zub_list)
##print plot_Zlb(Zlb_list)

