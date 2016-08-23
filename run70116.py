#name Run70116 try to test if  Model('MIP_OneCustomer%s') only run once.
import sys
sys.path.append('C:/gurobi604/win32/python27/lib/gurobipy')
from gurobipy import *
import time
import matplotlib.pyplot as plt
from func62016 import *
Z_list=[]
sigma=2
#set initial upper bound Zub
Zub=float("inf")
#Zub=763500
Zlb=-float("inf")
o=0
alpha=1
Zlb_list=[]
Zub_list=[]
pi_trace = {}
for i,k,s in pi:
    pi_trace[i,k,s] = [pi[i,k,s]]
#update the upper bound, get feasible solution
#while sigma>=0.005 and alpha!=0:
while o!=5:
    arc_C=getArcC(nodes,modes,departure)
    (m,X,y,t,T,Z,e1,e2,e3,e4)=MIP(customer,nodes,modes,departure,pi)
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
    GG={}
    GG_square = 0
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
                        GG[i,k,s]=GG[i,k,s]+int(row[2])*X[int(row[0]),i,k,s].x
                    GG[i,k,s]=GG[i,k,s]-arc_C[i,k,s]
                    GG_square += GG[i,k,s]**2
##    print '\n'
##    print 'GG',GG
    #print GG_square,'GG_square'
    obj_total=0
    obj_list=[]
    X_list=[]
    y_list=[]
    transCost_list=[]
    piCost_list=[]
    yCost_list=[]
    TimeCost_list=[]
##    print '\n'
##    print 'before AL2 arc_C',arc_C
##    print '\n'
    if o==0:
        for kkk in customer:
            this_run_m = Model('MIP_OneCustomer%s')
            this_run_m,X,y,t,T,obj,e21,e22,e23,e24=MIP_OneCustomer(arc_C,kkk,pi)        
            transCost_list.append(e21.getValue())
            piCost_list.append(e22.getValue())
            yCost_list.append(e23.getValue())
            TimeCost_list.append(e24.getValue())
            nopicost=e21.getValue()+e23.getValue()+e24.getValue()
    ##        print '********************************************'
    ##        print e21.getValue(),'transporation cost'
    ##        print e22.getValue(),'pi  cost'
    ##        print e23.getValue(),'y cost'
    ##        print e24.getValue(),'Time tardiness cost'
    ##        print 'cost not include pi cost',nopicost
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
                        y_list.append([int(e) for e in raw_yidxes])
                        TransCost+=F*int(kkk[2])
                    for k in modes:
                        for s in departure:
                            if X[int(kkk[0]),i,k,s].x > 0:
                                #print 'X[int(kkk[0]),i,k,s].x',int(kkk[0]),i,k,s,'arc_trans_cost[int(kkk[0]),i,k]',arc_trans_cost[int(kkk[0]),i,k],'Q*arc',arc_trans_cost[int(kkk[0]),i,k]*int(kkk[2])
                                TransCost+=arc_trans_cost[int(kkk[0]),i,k]*int(kkk[2])
                                arc_C[i,k,s]=arc_C[i,k,s]-int(kkk[2])
                                raw_idxes = X[int(kkk[0]),i,k,s].VarName.split('_')[1:]
                                X_list.append([int(e) for e in raw_idxes])
            obj_total+=obj # obj includes the pi cost, but what i want is cost exclude pi cost
            obj_list.append(obj)
##    print '\n'
##    print 'after Al2 arc_C',arc_C
##    print '\n'
##    print 'X_list',X_list
##    print 'y_list',y_list
##    print 'transCost_list',transCost_list
##    print 'piCost_list',piCost_list
##    print sum(piCost_list),'sum of pi cost'
##    print 'yCost_list',yCost_list
##    print 'TimeCost_list',TimeCost_list
##    print 'obj_total',obj_total    
        Zub_temple=sum(transCost_list)+sum(yCost_list)+sum(TimeCost_list)
        Zub=min(Zub,Zub_temple)
        Zub=int(Zub)
        Zub_list.append(Zub)
    Zlb=max(Z,Zlb)
    Zlb=int(Zlb)
    Zlb_list.append(Zlb)        
    alpha_temple=sigma*(Zub-Zlb)/(GG_square)
    alpha=max(0,alpha_temple)
    if Zlb>Zub:
        Zlb=Zlb_list[-2]
    for k in modes:
        for s in departure:
            for i in nodes:
                if i==4:
                    continue
                else:
                    pi[i,k,s]=max(0,pi[i,k,s]+GG[i,k,s]*alpha)
                    pi_trace[i,k,s].append(pi[i,k,s])
##                    print 'pi[',i,k,s,']=',pi[i,k,s]
##                    pi_list.append(pi[i,k,s])
##                    print 'pi_list',i,k,s,pi_list
##    print '\n'
##    print '#########################################'
##    print 'pi'
##    print pi
##    print '\n'
##    print 'o',o,'alpha',alpha,'Zlb',Zlb,'Zub',Zub,'sigma',sigma,'GG_square',GG_square  
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
print 'o',o,'alpha',alpha,'sigma',sigma,'GG_square',GG_square  
print '\n'
print Zlb_list,'Zlb_list'
print '\n'
print Zub_list,'Zub_list'
print '\n'
##for i,k,s in pi_trace:
##    print 'i,k,s',i,k,s,pi_trace[i,k,s],'\n'
#print plot_Zub(pi_trace)
##print plot_Zlb(Zlb_list)
##plt.ylabel('pi value')
##plt.plot(pi_trace[3,1,1])
##plt.show()
