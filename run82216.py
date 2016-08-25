#name run82216  based on run71916
import sys
#sys.path.append('C:/gurobi563/win32/python27/lib/gurobipy')
sys.path.append('C:/gurobi605/win32/python27/lib/gurobipy')
from gurobipy import *
import time
import pdb
import matplotlib.pyplot as plt
from func82216 import *
Z_list = [ ]
#set initial upper bound Zub
Zub = float("inf")
#Zub=763500
Zlb = -float("inf")
o=0
delta = 1
delta_list = []
delta_list.append(delta)
lamda = 2
lamda_list = []
lamda_list.append(lamda)
Zub_temple_list = []
Zlb_list = []
Zub_list = []
pi_trace = {}
for u,v,k,s in pi:
    pi_trace[u,v,k,s] = [pi[u,v,k,s]]
while lamda >= 0.005 and delta!=0:
# while o!=3:
    getGC(G,fix_C)
    (m,X,y,t,TD,Z,e1,e2,e3,e4) = MIP(customer,G,modes,pi)
    m.write('./run82216.lp')
    # threePLCost = 0
    # TransCost = 0
    # TotalTransCost = 0
    # TotalTardinessCost = 0
    # TotalCost = 0
    #print 'main solution'
    with open('c:/Users/MacBook Air/Desktop/output_infeasible2.txt', 'w') as f_out:
        if m.status == GRB.status.OPTIMAL:
                for row in customer:
                    # TotalTardinessCost+=TD[int(row[0])].x*int(row[4])*int(row[2])
                    for (u,v) in G.edges():
                        if y[int(row[0]),u,v].x>0:
                            f_out.write('Customer %d arc %s using 3PL Trans_cost %d\n'%(int(row[0]),(u,v),F*int(row[2])))
                            # threePLCost+=F*int(row[2])        
        for row in customer:
            for (u,v) in G.edges():
                for k in modes:
                    for s in departure:
                        if X[int(row[0]),u,v,k,s].x > 0:
                            f_out.write('Customer %d link %s arc_mode_num %d departureTimeIndex %d f %d start_Time %d tau %d t %f real_arrive_time %f\n'%(int(row[0]),(u,v),k,s,G[u][v]['f',k]*int(row[2]),G[u][v]['dT',k,s],G[u][v]['tau',k],t[int(row[0]),v].x,G[u][v]['dT',k,s]+ G[u][v]['tau',k]))
                            #print 'Customer',int(row[0]),'link',n,'arc_mode_num',k,'departureTimeIndex',s,'f',f[n,k]*int(row[2]),'start_Time',dT[n,k,s],'tau',tau[n,k],'t',t[int(row[0]),n].x,'real_arrive_time',dT[n,k,s]+tau[n,k]
    #                         TransCost+=G[u][v]['f',k]*int(row[2])
    # TotalTransCost=TransCost+threePLCost
    # TotalCost=  TotalTardinessCost + TotalTransCost
    GG={}
    GG_square = 0
    for (u,v) in G.edges():
        for k in modes:
            for s in departure:
                GG[u,v,k,s]=0
    for k in modes:
        for s in departure:
            for (u,v) in G.edges():
                for row in customer:
                    GG[u,v,k,s]=GG[u,v,k,s]+int(row[2])*X[int(row[0]),u,v,k,s].x
                GG[u,v,k,s]=GG[u,v,k,s]-G[u][v]['C',k,s]
                GG_square += GG[u,v,k,s]**2
    all_fixed_x_idxes = []
    for k in modes:
        for s in departure:
            for (u,v) in G.edges():
                if -fix_C<GG[u,v,k,s]<=0:
                    for row in customer:
                        if X[int(row[0]),u,v,k,s].x>0:
                            all_fixed_x_idxes.append([int(row[0]),u,v,k,s])
                if GG[u,v,k,s]>0:
                    customers_for_current_capacity = [(int(row[0]), int(row[2])) for row in customer if X[int(row[0]),u,v,k,s].x and int(row[2])<=G[u][v]['C',k,s]]
                    customers_for_current_capacity.sort(key = lambda r: r[1],reverse = True)
                    current_sum = 0
                    for i,c in enumerate(customers_for_current_capacity):
                        current_sum += c[1]
                        if current_sum > G[u][v]['C',k,s]:
                            break
                    else:
                        i += 1
                    x_to_fix = [[c[0], u,v, k, s] for c in customers_for_current_capacity[:i]]
                    all_fixed_x_idxes.extend(x_to_fix)
    # print all_fixed_x_idxes,'all fix x to 1'
    # print '\n'
    #after all_fixed_x_idxed, we need to update capacity_for_nonfixed.
    customer_demands = dict()
    for row in customer:
        customer_demands[int(row[0])]= int(row[2]) 
    for k in modes:
        for s in departure:
            for (u,v) in G.edges():
                customer_for_fixed_nks = [idx[0] for idx in all_fixed_x_idxes if idx[1:] == [u,v,k,s]]
                if customer_for_fixed_nks:
                    customer_deamand_for_fixed_nks = sum([customer_demands[d] for d in customer_for_fixed_nks])
                    G[u][v]['C',k,s] -= customer_deamand_for_fixed_nks
    X_list=[]
    y_list=[]
    transCost_list=[]
    piCost_list=[]
    yCost_list=[]
    TimeCost_list=[]
    for kkk in customer:
        print kkk,'kkk'
        this_run_m = Model('MIP_OneCustomer%s')
        #print C,'try C each time'
        this_run_m,X,y,t,TD,obj,e21,e22,e23,e24=MIP_OneCustomer(G,kkk,pi,all_fixed_x_idxes)
        # print TD,'6'*100
        transCost_list.append(e21.getValue())
        piCost_list.append(e22.getValue())
        yCost_list.append(e23.getValue())
        TimeCost_list.append(e24.getValue())
        nopicost = e21.getValue()+e23.getValue()+e24.getValue()
        # print '********************************************'
        # print e21.getValue(),'transporation cost'
        # print e22.getValue(),'pi  cost'
        # print e23.getValue(),'y cost'
        # print e24.getValue(),'Time tardiness cost'
        # print 'cost not include pi cost',nopicost
        # print '********************************************'   
        if this_run_m.status == GRB.status.OPTIMAL:    
            for (u,v) in G.edges():
                if y[int(kkk[0]),u,v].x==1:
                    raw_yidxes=y[int(kkk[0]),u,v].VarName.split('_')[1:]
                    # print raw_yidxes, 'try'*100
                    y_list.append([int(float(e)) for e in raw_yidxes])
                for k in modes:
                    for s in departure:
                        if X[int(kkk[0]),u,v,k,s].x > 0:
                            G[u][v]['C',k,s]-=int(kkk[2])
                            raw_idxes = X[int(kkk[0]),u,v,k,s].VarName.split('_')[1:]
                            # print raw_idxes,'&'*100
                            X_list.append([int(float(e)) for e in raw_idxes])
    Zub_temple=sum(transCost_list)+sum(yCost_list)+sum(TimeCost_list)
    # print Zub_temple,'Zub_temple'*10
    if not Zub_list or Zub_temple <= min(Zub_list):
        with open('c:/Users/MacBook Air/Desktop/output_upperbound2.txt', 'w') as f2_out:
            for item in X_list:
                f2_out.write('%s\n'% item)
            for item in y_list:
                f2_out.write('%s\n'% item)
            f2_out.write('TransCost_list_%s\n'% sum(transCost_list))
            f2_out.write('TimeCost_list_%s\n'% sum(TimeCost_list))
    Zub_temple_list.append(Zub_temple)
    Zub=min(Zub,Zub_temple)
    Zub_list.append(round(Zub,0))
    Zlb=max(Z,Zlb)
    Zlb_list.append(round(Zlb,0))        
    delta_temple=lamda*(Zub-Zlb)/(GG_square)
    delta=max(0,delta_temple)
    delta_list.append(round(delta,5))
    for k in modes:
        for s in departure:
            for (u,v) in G.edges():
                pi[u,v,k,s]=max(0,pi[u,v,k,s]+GG[u,v,k,s]*delta)
                pi_trace[u,v,k,s].append(pi[u,v,k,s])
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
        lamda_list.append(round(lamda,4))
        o+=1
print '\n'
print 'size of customer',len(customer)
print '\n'
print 'computer time (seconds): ',time.clock() - float(start_time)
print '\n'
print 'o',o,'delta',delta,'lambda',lamda,'GG_square',GG_square  
print '\n'
print 'size of Zlb_list,size of Zub_list',len(Zlb_list),len(Zub_list),'\n'
print Zlb_list,'Zlb_list'
print '\n'
print Zub_list,'Zub_list'
print '\n'
print delta_list,'delta_list'
print '\n'
print lamda_list,'lamda_list'
print '\n'
# Gap_Zlb=0
# Gap_Zub=0
# opt=0
##if len(customer)==5:
##    opt=2088000.0
##if len(customer)==10:
##    opt=6378000.0
##if len(customer)==20:
##    opt=3320030.0
    
##if len(customer)==50:
##    opt=4530900.0
##if len(customer)==100:
##    opt=14619000.0
##if len(customer)==200:
##    opt=15845400.0
##Gap_Zlb=(opt-Zlb_list[-1])/opt
##Gap_Zub=(Zub_list[-1]-opt)/opt

# print 'Gap_Zlb',(format(Gap_Zlb,'.2%'))
# print 'Gap_Zub',(format(Gap_Zub,'.2%'))
# plt.ylabel('pi value')
# plt.plot(Zlb_list)
# plt.show()
