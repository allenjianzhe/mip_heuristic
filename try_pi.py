# -*- coding: utf-8 -*-
import sys
sys.path.append('C:/gurobi604/win32/python27/lib/gurobipy')
#sys.path.append('F:/gurobi651/win32/python27/lib/gurobipy')

from gurobipy import *
from Update_UpperBound import *
from new110315_20160522down import *

# import importlib
# m=importlib.import_module("110315")
print sigma
print "#################################################################算出zlb之后############################"
print 'Zlb', Zlb
print 'Zub', Zub
print 'obj_total', obj_total
kkk = {}
pi = {}
for i in nodes:
    if i == 4:
        continue
    else:
        for k in modes:
            for s in departure:
                pi[i, k, s] = 0
for row in customer:
    for kkk in row:
        # m = Model('MIP_OneCustomer%s')
        # obj=MIP_OneCustomer(m,arc_C,kkk,pi,nodes)
        threePLCost = 0;
        TransCost = 0;
        TotalTransCost = 0;
        TotalTardinessCost = 0;
        TotalCost = 0;
    if this_run_m.status == GRB.status.OPTIMAL:  # get rid of for row in customer and problem solved.
        # print 'row',row
        for i in nodes[:-1]:
            # print 'i',i
            if y[int(kkk[0]), i].x == 1:
                # print y[int(kkk[0]),i].x,'int(kkk[0])',int(kkk[0]),'i',i
                ##                if y[int(kkk[0]),i] not in y_list:
                y_list.append(y[int(kkk[0]), i])
                # print y_list,'#####################################'
            for k in modes:
                for s in departure:
                    if X[int(kkk[0]), i, k, s].x > 0:  # print 'Customer',int(kkk[0]),'link',i,'arc_mode_num',k,'departureTimeIndex',s,'arc_cost',arc_trans_cost[int(kkk[0]),i,k]*int(kkk[2]),'start_Time',dT[i,k,s],'Trans_time',trans_time[i,k],'t',t[int(kkk[0]),i].x,'real_arrive_time',dT[i,k,s]+trans_time[i,k]
                        a = []
                        TransCost += arc_trans_cost[int(kkk[0]), i, k] * int(kkk[2])
                        a.append(X[int(kkk[0]), i, k, s].VarName.split('_')[1:])  # print a,'############################test'
                        arc_C[i, k, s] = arc_C[i, k, s] - int(kkk[2])
                        X_list.append(a)  # print X_list,'################################################################'

    obj_total += obj  ##    print 'obj',obj_total
    obj_list.append(obj)
    print 'obj_total', obj_total
    print X_list
    GG = {}
    for i in nodes:
        if i == 4:
            continue
        else:
            for k in modes:
                for s in departure:
                    GG[i, k, s] = 0

    for k in modes:

        for i in nodes:
            # a=LinExpr()
            if i == 4:
                continue
            else:
                for row in customer:
                    for s in departure:
                        if X[ int(kkk[0]), i, k, s].x > 0:  # print 'i,k,s',i,k,s
                                # print 'GG[i,k,s]',GG[i,k,s]
                            GG[i, k, s] = GG[i, k, s] + int(kkk[2])  # print 'GG[i,k,s]',GG[i,k,s]
                            GG[i, k, s] = GG[i, k, s] - arc_C[i, k, s]  # where is the problem?
    print GG

# 首先,obj_total没有pi cost ,所以要计算出pi cost 利用GG更新pi
# G size is nmt, similar to pi. but G is a number
# Update_UpperBound.py里面的X-list需要调用
'''
if this_run_m.status == GRB.status.OPTIMAL:
    G = 0
    for k in modes:  # 这里面的x需要和子程序的对应，而不是主程序
        for s in departure:
            for i in nodes:
                if i == 4:
                    continue
                else:
                    for row in customer:
                        for kkk in row:
                            if X[int(kkk[0]), i, k, s].x > 0:
                                # print 'test',X[int(row[0]),i,k,s].x # why X=0 will also be shown?
                                # if you print X[int(row[0]),i,k,s], then all the X will be shown
                                G = G + int(kkk[2]) * X[int(kkk[0]), i, k, s].x
                                # print 'middle G',G, 'i,k,s',i,k,s
                                G = G - arc_C[i, k, s]  # right?????????
print '\n'
print 'G', G'''

pi_cost = 0
for row in customer:
    for kkk in row:
        for k in modes:  # 这里面的x需要和子程序的对应，而不是主程序
            for s in departure:
                for i in nodes:
                    if i == 4:
                        continue
                    else:
                        pi_cost += pi[i, k, s] * GG[i, k, s]
print 'pi_cost', pi_cost

z_h = pi_cost + obj_total
print 'z_h', z_h
