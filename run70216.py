#name Run70216
import sys
sys.path.append('C:/gurobi563/win32/python27/lib/gurobipy')
from gurobipy import *
import time
import matplotlib.pyplot as plt
from func70216 import *
Z_list=[]

#set initial upper bound Zub
Zub=float("inf")
#Zub=763500
Zlb=-float("inf")
o=0
delta=1
delta_list=[]
delta_list.append(delta)
lamda=2
lamda_list=[]
lamda_list.append(lamda)
Zlb_list=[]
Zub_list=[]
pi_trace = {}
for n,k,s in pi:
    pi_trace[n,k,s] = [pi[n,k,s]]
#update the upper bound, get feasible solution
    
#while lamda>=0.005 and delta!=0:
while o!=2:
    C=getC(nodes,modes,departure)
    (m,X,y,t,TD,Z,e1,e2,e3,e4)=MIP(customer,nodes,modes,departure,pi)
    threePLCost=0
    TransCost=0
    TotalTransCost=0
    TotalTardinessCost=0
    TotalCost=0
    #print 'main round solution of subgradient method'
    if m.status == GRB.status.OPTIMAL:
            for row in customer:
                TotalTardinessCost+=TD[int(row[0])].x*int(row[4])*int(row[2])
                for n in nodes:
                    if n==4:
                        continue
                    else:
                        if y[int(row[0]),n].x>0:
                                #print 'Customer',int(row[0])+1,'arc',n,' using 3PL','Trans_cost',F*int(row[2])
                                threePLCost+=F*int(row[2])        
    for row in customer:
            for n in nodes:
                if n==4:
                    continue
                else:
                    for k in modes:
                        for s in departure:
                                if X[int(row[0]),n,k,s].x > 0:
                                        #print 'Customer',int(row[0])+1,'link',n,'arc_mode_num',k,'departureTimeIndex',s,'f',f[n,k]*int(row[2]),'start_Time',dT[n,k,s],'tau',tau[n,k],'t',t[int(row[0]),n].x,'real_arrive_time',dT[n,k,s]+tau[n,k]
                                        TransCost+=f[n,k]*int(row[2])
    TotalTransCost=TransCost+threePLCost
    TotalCost=  TotalTardinessCost+   TotalTransCost
    GG={}
    GG_square = 0
    for n in nodes:
        if n==4:
            continue
        else:
            for k in modes:
                for s in departure:
                    GG[n,k,s]=0
    for k in modes:
        for s in departure:
            for n in nodes:
                if n==4:
                    continue
                else:
                    for row in customer:
                        GG[n,k,s]=GG[n,k,s]+int(row[2])*X[int(row[0]),n,k,s].x
                    GG[n,k,s]=GG[n,k,s]-C[n,k,s]
                    GG_square += GG[n,k,s]**2
##    print '\n'
##    print 'GG'
##    print GG
##    print '\n'
##    for k in modes:
##        for s in departure:
##            for n in nodes:
##                if n==4:
##                    continue
##                #if GG[n,k,s]!=-400:
##                if -400<GG[n,k,s]<=0:
##                    print GG[n,k,s],'GG[n,k,s]'
##                    for row in customer:
##                        if X[int(row[0]),n,k,s].x>0:
##                            print X[int(row[0]),n,k,s].x,'X[int(row[0]),n,k,s].x','int(row[0]),n,k,s',int(row[0]),n,k,s
                
                    

    obj_total=0
    obj_list=[]
    X_list=[]
    y_list=[]
    transCost_list=[]
    piCost_list=[]
    yCost_list=[]
    TimeCost_list=[]
##    print '\n'
##    print 'before AL2 C',C
##    print '\n'
    for kkk in customer:
        this_run_m = Model('MIP_OneCustomer%s')
        this_run_m,X,y,t,TD,obj,e21,e22,e23,e24=MIP_OneCustomer(C,kkk,pi)        
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
            for n in nodes[:-1]:
                if y[int(kkk[0]),n].x==1:
                    raw_yidxes=y[int(kkk[0]),n].VarName.split('_')[1:]
                    y_list.append([int(e) for e in raw_yidxes])
                    TransCost+=F*int(kkk[2])
                for k in modes:
                    for s in departure:
                        if X[int(kkk[0]),n,k,s].x > 0:
                            #print 'X[int(kkk[0]),i,k,s].x',int(kkk[0]),i,k,s,'f[i,k]',f[i,k],'Q*arc',f[i,k]*int(kkk[2])
                            TransCost+=f[n,k]*int(kkk[2])
                            C[n,k,s]=C[n,k,s]-int(kkk[2])
                            raw_idxes = X[int(kkk[0]),n,k,s].VarName.split('_')[1:]
                            X_list.append([int(e) for e in raw_idxes])
        obj_total+=obj # obj includes the pi cost, but what i want is cost exclude pi cost
        obj_list.append(obj)
##    print '\n'
##    print 'after Al2 C',C
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
    Zub_list.append(Zub)
    Zlb=max(Z,Zlb)
    Zlb=int(Zlb)
    Zlb_list.append(Zlb)        
    delta_temple=lamda*(Zub-Zlb)/(GG_square)
    delta=max(0,delta_temple)
    #delta='{:,.4f}'.format(delta)
    delta_list.append(delta)
    if Zlb>Zub:
        Zlb=Zlb_list[-2]
    for k in modes:
        for s in departure:
            for n in nodes:
                if n==4:
                    continue
                else:
                    pi[n,k,s]=max(0,pi[n,k,s]+GG[n,k,s]*delta)
                    pi_trace[n,k,s].append(pi[n,k,s])
##                    print 'pi[',i,k,s,']=',pi[i,k,s]
##                    pi_list.append(pi[i,k,s])
##                    print 'pi_list',i,k,s,pi_list
##    print '\n'
##    print '#########################################'
##    print 'pi'
##    print pi
##    print '\n'
##    print 'o',o,'delta',delta,'Zlb',Zlb,'Zub',Zub,'lamda',lamda,'GG_square',GG_square  
    #print '\n'
    if len(Z_list)==3:
        if Z<min(Z_list):
            Z_list=[]
            Z_list.append(Z)
        else:
            lamda=0.5*lamda
            Z_list=[]
            Z_list.append(Z)
    else:
        Z_list.append(Z)
        lamda_list.append(lamda)
        o+=1
print '\n'
print 'size of customer',len(customer)
print '\n'
print 'computer time (seconds): ',time.clock() - float(start_time)
print '\n'
print 'o',o,'delta',delta,'lambda',lamda,'GG_square',GG_square  
print '\n'
print Zlb_list,'Zlb_list'
print '\n'
print Zub_list,'Zub_list'
print '\n'
print delta_list,'delta_list'
print '\n'
print lamda_list,'lamda_list'
print '\n'
Gap_Zlb=0
Gap_Zub=0
##if len(customer)==5:
##    opt=2088000.0
##if len(customer)==10:
##    opt=4427000.0
##if len(customer)==50:
##    opt=4530900.0
##if len(customer)==100:
##    opt=14619000.0
##if len(customer)==200:
##    opt=15845400.0
##Gap_Zlb=(opt-Zlb_list[-1])/opt
##Gap_Zub=(Zub_list[-1]-opt)/opt

print 'Gap_Zlb',(format(Gap_Zlb,'.2%'))
print 'Gap_Zub',(format(Gap_Zub,'.2%'))
##plt.ylabel('pi value')
##plt.plot(pi_trace[3,1,1])
##plt.show()
