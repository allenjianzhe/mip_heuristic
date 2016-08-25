
#----------------------------------------------------------------------------
#name func82216.py 
#----------------------------------------------------------------------------
#           Multimodal transportation problem
#----------------------------------------------------------------------------
# Objective: Minimize total cost including transport mode cost, delay penalty cost and 3PL cost
#----------------------------------------------------------------------------

import sys
sys.path.append('C:/gurobi563/win32/python27/lib/gurobipy')
from gurobipy import *
import time
start_time=time.clock()
import copy
import matplotlib.pyplot as plt
import numpy as np
from read81616 import *
# from read82316 import *
#sub method key variable pi, change every round,related with i,k,s
pi={}#i=0,1,2,3; k=1,2,3,4; s=1,2,3,4,5,6
#initial pi has been set to 0 
for (u,v) in G.edges():
    for k in modes:
        for s in departure:
            pi[u,v,k,s]=0
#type of variables: GRB.CONTINUOUS, GRB.BINARY, GRB.INTEGER
def MIP(customer,G,modes,pi):
    m=Model('MIP')
    X = {}
    for row in customer:
        for (u,v) in G.edges():
            for k in modes:
                for s in departure:
                    X[int(row[0]),u,v,k,s]=m.addVar(vtype=GRB.BINARY,name="X_%d_%d_%d_%d"%(row[0],u,k,s))
    m.update()
    #expr1:the transportation cost related with X    
    expr1=LinExpr()
    for row in customer:
        for (u,v) in G.edges():
            for k in modes:
                for s in departure:
                    expr1=expr1+X[int(row[0]),u,v,k,s]*int(row[2])*G[u][v]['f',k]
    m.update()
    #expr2:cost with pi
    expr2 = LinExpr()
    for k in modes:
        for s in departure:
            for (u,v) in G.edges():
                a=LinExpr()
                for row in customer:
                        a.addTerms(int(row[2]),X[int(row[0]),u,v,k,s])
                a.add(-1,G[u][v]['C',k,s])
                expr2=expr2+pi[u,v,k,s]*a  
    m.update()
    #decision variable y: binary variable of 3PL
    y={}
    for row in customer:
        for (u,v) in G.edges():
            y[int(row[0]),u,v]=m.addVar(vtype=GRB.BINARY,name="y_%d_%d"%(row[0],u))     
    m.update()
    #expr3:cost related with y, 3PL
    expr3=LinExpr()
    for row in customer:
        for (u,v) in G.edges():
            expr3=expr3+y[int(row[0]),u,v]*int(row[2])*F  
    #decision variable z: binary variable of route chosen
    z={}
    for row in customer:
        for (u,v) in G.edges():
            z[int(row[0]),u,v] = m.addVar(obj = 0 , vtype=GRB.BINARY, name="z_%d_%d"%(row[0],u))
    m.update()        
    #decision variable: arrive time at each node.
    #t[int(row[0]),i] is arrive time of customer int(row[0]) at arc i.
    t={}
    for row in customer:
        for u in G.nodes():
            if u!=1:
                t[int(row[0]),u]=m.addVar(obj=0,vtype='C', name="t_%d_%d"%(row[0],u))
    m.update()
    #decision variable:Time tardiness of customer
    #T[int(row[0])] is tardiness of customer int(row[0])
    TD={}
    for row in customer:
            TD[int(row[0])]=m.addVar(vtype='C',name='Tardiness_%d'%int(row[0]))
    m.update()
    #expr4:cost of time tardiness penalty 
    expr4=LinExpr()
    for row in customer:
        expr4=expr4+TD[int(row[0])]*int(row[2])*int(row[4])
    #######################################
    m.setObjective(expr1+expr2+expr3+expr4)
    #######################################    
    #constraint 2, definition of TD
    for row in customer:
        m.addConstr(TD[int(row[0])],GRB.EQUAL,t[int(row[0]),len(G.nodes())]-int(row[3]),name="TD_%s"%row[0])
    m.update()
    #Constraint 3,  for each customer, each link, only one mode can be selected
    for row in customer:
        for (u,v) in G.edges():
            expr = LinExpr()       
            for k in modes:
                    for s in departure:
                            expr.addTerms(1.0,X[int(row[0]),u,v,k,s])
            expr.add(y[int(row[0]),u,v])
            m.addConstr(expr, GRB.EQUAL, z[int(row[0]),u,v],name="OnlyOneMode_%s_%d"%(row[0],u))
    m.update()
    # #constraint 4,  arc capacity
    # for k in modes:
    #     for s in departure:
    #         for (u,v) in G.edges():
    #             expr = LinExpr()
    #             for row in customer:
    #                     expr.addTerms(int(row[2]),X[int(row[0]),u,v,k,s])
    #             expr.addConstant(-1*G[u][v]['C',k,s])
    #             m.addConstr(expr,GRB.LESS_EQUAL, 0,'arcCapacity_%r_%r_%r_%r_%r'%(int(row[0]),u,v,k,s))      
    # m.update() 
    #constraint 5, flow balance, all to start
    for row in customer:
        expr = LinExpr()
        for v in G.neighbors(1):
            expr.addTerms(1,z[int(row[0]),1,v])
        m.addConstr(expr,GRB.EQUAL,1,name="StarToAll_%s"%row[0])
    m.update()
    #constraint 6, flow balance
    for row in customer:        
        for u in G.nodes():
            expr5 = LinExpr()
            if u!=1 and u!=len(G.nodes()):
                all_node_to_u = [u1 for (u1,v1) in G.edges() if v1 == u]
                for to_u in all_node_to_u:
                    # print 'z_%s_%s'%(to_u,u)
                    expr5.addTerms(1, z[int(row[0]), to_u, u])
                all_node_from_u = [v1 for (u1,v1) in G.edges() if u1 == u]
                for from_u in all_node_from_u:
                    # print '-z_%s_%s'%(u,from_u)
                    expr5.addTerms(-1, z[int(row[0]), u, from_u])
            m.addConstr(expr5,GRB.EQUAL,0, name="in_out_rule_%d_%d"%(row[0],u))
    m.update()
    #constraint, flow balance, all to the end
    for row in customer:
        expr = LinExpr()
        #nodes_to_end = G.neighbors(len(G.nodes()))
        nodes_to_end = [u1 for (u1,v1) in G.edges() if v1 == len(G.nodes())]
        for u in nodes_to_end:
            if u!=len(G.nodes()):
                expr.addTerms(1,z[int(row[0]),u,len(G.nodes())])
        m.addConstr(expr,GRB.EQUAL,1,name="AlltoEnd_%s"%row[0])
    m.update()
    #constraint 7, time constraint 
    for row in customer:        
            for (u,v) in G.edges():
                expr = LinExpr()                
                for k in modes:
                        for s in departure:                                            
                                expr.addTerms(G[u][v]['dT',k,s]+G[u][v]['tau',k],X[int(row[0]),u,v,k,s])
                # expr.add(-1*y[int(row[0]),u,v]*M)
                m.addConstr(expr,GRB.LESS_EQUAL,t[int(row[0]),v],name="Time7_%s_%d"%(row[0],u))                        
    m.update()                    
    #constraint 8, time constraint 
    for row in customer:        
        for (u,v) in G.edges(): 
            if u != 1:                   
                expr = LinExpr()
                for k in modes:
                    for s in departure:                                            
                        expr.addTerms(G[u][v]['dT',k,s],X[int(row[0]),u,v,k,s])
                expr1.add((1+y[int(row[0]),u,v]-z[int(row[0]),u,v])*M)
                m.addConstr(expr,GRB.GREATER_EQUAL,t[int(row[0]),u],name="Time8_%s_%d"%(row[0],u))
    m.update()
    #constraint 9, time constraint 
    for row in customer:
        for (u,v) in G.edges():
            if u != 1:
                expr = LinExpr()
                expr.addTerms(1, t[int(row[0]), u])
                expr.add(G[u][v]['ST'] - M*(1 - y[int(row[0]), u, v]))
                m.addConstr(expr, GRB.LESS_EQUAL, t[int(row[0]), v],name="Time9_%s_%d"%(row[0],u))
    m.update()
    m.optimize()
    return m,X,y,t,TD,m.objVal,expr1,expr2,expr3,expr4
def MIP_OneCustomer(G,kkk,pi,all_fixed_x_idxes):
    m=Model('MIP_OneCustomer')
    ending_time={}
    ####################################################################################################
    #decision variable X: binary variable. X[customer,i,i+1,m,k]
    row = kkk
    X = {}
    for (u,v) in G.edges():
        for k in modes:
            for s in departure:
                X[int(row[0]),u,v,k,s]=m.addVar(vtype=GRB.BINARY,name="XH_%d_%d_%d_%d"%(row[0],u,k,s))
    m.update()
    #set all_fixed_x to be 1
    for (u,v) in G.edges():
        for k in modes:
            for s in departure:
                if [int(row[0]),u,v,k,s] in all_fixed_x_idxes:
                    X[int(row[0]),u,v,k,s].LB=1
                    G[u][v]['C',k,s]+=int(row[2])
    m.update()
    #expr1:the transportation cost related with X    
    expr1=LinExpr()
    for (u,v) in G.edges():
        for k in modes:
            for s in departure:
                expr1=expr1+X[int(row[0]),u,v,k,s]*int(row[2])*G[u][v]['f',k]
                # print expr1,'test'*10
    m.update()
    y={}       
    for (u,v) in G.edges():
        y[int(row[0]),u,v]=m.addVar(vtype=GRB.BINARY,name="yH_%d_%d"%(row[0],u))     
    m.update()
    #expr2:cost with pi
    expr2 = LinExpr()
    for k in modes:
        for s in departure:
            for (u,v) in G.edges():
                a=LinExpr()
                a.addTerms(int(row[2]),X[int(row[0]),u,v,k,s])
                a.add(-1,G[u][v]['C',k,s]/int(len(customer)))
                expr2=expr2+pi[u,v,k,s]*a  
    m.update()
    #decision variable z: binary variable of route chosen
    z={}
    for (u,v) in G.edges():
        z[int(row[0]),u,v] = m.addVar(obj = 0 , vtype=GRB.BINARY, name="zH_%s_%d"%(row[0],u))
    m.update()
    #expr3:cost related with y, 3PL
    expr3=LinExpr()        
    for (u,v) in G.edges():
        expr3=expr3+y[int(row[0]),u,v]*int(row[2])*F 
    m.update()                   
    #decision variable: arrive time at each node.
    #t[int(row[0]),i] is arrive time of customer int(row[0]) at arc i.
    t={}
    for u in G.nodes():
        if u!=1:
            t[int(row[0]),u]=m.addVar(obj=0,vtype='C', name="tH_%s_%d"%(row[0],u))  
    m.update()
    #decision variable:Time tardiness of customer
    #T[int(row[0])] is tardiness of customer int(row[0])
    TD={}        
    TD[int(row[0])]=m.addVar(vtype='C',name='TardinessH_%d'%int(row[0]))
    m.update()
    #expr4:cost of time tardiness penalty 
    expr4=LinExpr()       
    expr4=expr4+TD[int(row[0])]*int(row[2])*int(row[4])
    m.update()
    #######################################
    #m.setObjective(expr1+expr2+expr3+expr4)
    m.setObjective(expr1+expr2+expr3+expr4)
    #######################################
    #constraint 2, definition of TD
    m.addConstr(TD[int(row[0])],GRB.EQUAL,t[int(row[0]),len(G.nodes())]-int(row[3]),name="TDH_%s"%row[0])
    m.update()
    #Constraint 3.2 for each customer, each link, only one plan can be selected        
    for (u,v) in G.edges():
        expr = LinExpr()       
        for k in modes:
                for s in departure:
                        expr.addTerms(1.0,X[int(row[0]),u,v,k,s])
        expr.add(y[int(row[0]),u,v])
        m.addConstr(expr, GRB.EQUAL, z[int(row[0]),u,v],name="OnlyOneH_%d"%u)
    m.update()
    #constraint 3.4 arc capacity
    for k in modes:
        for s in departure:
            for (u,v) in G.edges():
                expr = LinExpr()
                expr.addTerms(int(row[2]),X[int(row[0]),u,v,k,s])
                expr.addConstant(-1*G[u][v]['C',k,s])
                m.addConstr(expr,GRB.LESS_EQUAL, 0,'arcCapacityH_%r_%d_%d_%d'%(int(row[0]),u,k,s))      
    m.update()                                         
    #constraint 5, flow balance, all to start
    expr = LinExpr()
    for v in G.neighbors(1):
        expr.addTerms(1,z[int(row[0]),1,v])
    m.addConstr(expr,GRB.EQUAL,1)
    m.update()
    #constraint 6, flow balance
    
    for u in G.nodes():
        expr5 = LinExpr()
        expr6 = LinExpr()
        if u!=1 and u!=len(G.nodes()):
            all_node_to_u = [u1 for (u1,v1) in G.edges() if v1 == u]
            for to_u in all_node_to_u:
                expr5.addTerms(1, z[int(row[0]), to_u, u])
            all_node_from_u = [v1 for (u1,v1) in G.edges() if u1 == u]
            for from_u in all_node_from_u:
                expr6.addTerms(1, z[int(row[0]), u, from_u])
        m.addConstr(expr5,GRB.EQUAL,expr6, name="in_out_H_%d"%u)
    m.update()
    #constraint, flow balance, all to the end
    expr = LinExpr()
    #nodes_to_end = G.neighbors(len(G.nodes()))
    nodes_to_end = [u1 for (u1,v1) in G.edges() if v1 == len(G.nodes())]
    for u in nodes_to_end:
        if u!=len(G.nodes()):
            expr.addTerms(1,z[int(row[0]),u,len(G.nodes())])
    m.addConstr(expr,GRB.EQUAL,1,name="AlltoEndH_%d"%u)
    m.update()
    #constraint 7, time constraint       
    for (u,v) in G.edges():
        expr = LinExpr()                
        for k in modes:
            for s in departure:                                            
                expr.addTerms(G[u][v]['dT',k,s]+G[u][v]['tau',k],X[int(row[0]),u,v,k,s])
        # expr.add(-1*y[int(row[0]),u,v]*M)
        m.addConstr(expr,GRB.LESS_EQUAL,t[int(row[0]),v],name="Time7H_%d"%u)                        
    m.update()                    
    #constraint 8, time constraint        
    for (u,v) in G.edges(): 
        if u != 1:                   
            expr7 = LinExpr()
            for k in modes:
                for s in departure:                                            
                    expr7.addTerms(G[u][v]['dT',k,s],X[int(row[0]),u,v,k,s])
            expr7.add((1+y[int(row[0]),u,v]-z[int(row[0]),u,v])*M)
            m.addConstr(expr7,GRB.GREATER_EQUAL,t[int(row[0]),u],name="Time8H_%d"%u)
    m.update()
    #constraint 9, time constraint 
    for (u,v) in G.edges():
        if u != 1:
            expr8 = LinExpr()
            expr8.addTerms(1, t[int(row[0]), u])
            expr8.add(G[u][v]['ST'] - M*(1 - y[int(row[0]), u, v]))
            m.addConstr(expr8, GRB.LESS_EQUAL, t[int(row[0]), v],name="Time9H_%d"%u)
    m.update()
    m.optimize()
    if m.status == GRB.status.INFEASIBLE:
        print 'Heuristic is infeasible'
        m.computeIIS()
        m.write('c:/HeuristicModelError72716.ilp')
    m.write('./customer_%s.lp'%row[0])
    m.write('./customer_%s.sol'%row[0])
    return m,X,y,t,TD,m.objVal,expr1,expr2,expr3,expr4
# def expr1_value(X):
#     expr1=0
#     for row in customer:
#         for (u,v) in G.edges():
#             for k in modes:
#                 for s in departure:
#                     expr1=expr1+X[int(row[0]),u,v,k,s].x*int(row[2])*G[u][v]['f',k]
#     return expr1
# def expr1_v(X,kkk):
#     expr1=0
#     row=kkk
#     #print kkk,'kkk'
#     #print X
#     for (u,v) in G.edges():
#         for k in modes:
#             for s in departure:
#                 if X[int(row[0]),u,v,k,s].x>0:
#                     expr1=expr1+X[int(row[0]),u,v,k,s].x*int(row[2])*G[u][v]['f',k]
#     return expr1
# def expr2_value(X,pi):
#     k2=0
#     for k in modes:
#         for s in departure:
#             for (u,v) in G.edges():
#                 a=0
#                 for row in customer:
#                     if X[int(row[0]),u,v,k,s].x >0:
#                         a=a+int(row[2])*X[int(row[0]),u,v,k,s].x
#                 if a==0:#make sure whether X==1, so that we wont add the 0 in the following and make sure a is bigger than 0.
#                     a=a
#                 else:
#                     a=a-G[u][v]['C',k,s]
#                 k2=k2+pi[u,v,k,s]*a
#     return k2
# def expr2_v(X,pi,kkk):
#     row=kkk
#     k2=0
#     for k in modes:
#         for s in departure:
#             for (u,v) in G.edges():
#                 if X[int(row[0]),u,v,k,s].x >0:
#                     a=a+int(row[2])*X[int(row[0]),u,v,k,s].x
#                 if a==0:#make sure whether X==1, so that we wont add the 0 in the following and make sure a is bigger than 0.
#                     a=a
#                 else:
#                     a=a-G[u][v]['C',k,s]
#                     #print a,'a', 'after all the customer sum'
#             k2=k2+pi[u,v,k,s]*a
#     return k2
##def expr2_v(X_list,pi):
##    iks_idx_list = []
##    for x in X_list:
##        if x[1:] not in iks_idx_list:
##            iks_idx_list.append(x[1:])
##    k2 = 0
##    for iks in iks_idx_list:
##        i = iks[0]
##        k = iks[1]
##        s = iks[2]
##        a=0
##        for row in customer:     
##            if [int(row[0]), i, k, s] in X_list:
##                a=a+int(row[2])
##        if a==0:#make sure whether X==1, so that we wont add the 0 in the following and make sure a is bigger than 0.
##            a=a
##        else:
##            a=a-C[i,k,s]
##        k2=k2+pi[i,k,s]*a
##    return k2    
# def expr3_value(y):
#     expr3=0
#     for row in customer:
#         for (u,v) in G.edges():
#             expr3=expr3+y[int(row[0]),u,v].x*int(row[2])*F
#     return expr3
# def expr3_v(y,kkk):
#     row=kkk
#     expr3=0
#     for (u,v) in G.edges():
#         expr3=expr3+y[int(row[0]),u,v].x*int(row[2])*M
#     return expr3
# def expr4_value(T):
#     expr4=0
#     for row in customer:
#         expr4=expr4+TD[int(row[0])].x*int(row[2])*int(row[4])
#     return expr4
# def expr4_v(T,kkk):
#     row=kkk
#     expr4=0
#     expr4=expr4+TD[int(row[0])].x*int(row[2])*int(row[4])
#     return expr4
#here def Transfer help me to get the X1, X2, X3 and y from the MIP so that i can consider them as input to the H. 
# def Transfer(X,y):
#     for row in customer:
#         for (u,v) in G.edges():
#             if y[int(row[0]),u,v].x==1:
#                 a=[]
#                 a.append(int(row[0]))
#                 a.append((u,v))
#                 yy.append(a)
#     for (u,v) in G.edges():
#         if (u,v)==(1,2):
#             for row in customer:
#                 for k in modes:
#                     for s in departure:
#                         if X[int(row[0]),u,v,k,s].x==1:
#                             a=[]
#                             a.append(int(row[0]))
#                             a.append(k)
#                             a.append(s)
#                             XX1.append(a)
#         if (u,v)==(2,3):
#             for row in customer:
#                 for k in modes:
#                     for s in departure:
#                         if X[int(row[0]),u,v,k,s].x==1:
#                             a=[]
#                             a.append(int(row[0]))
#                             a.append(k)
#                             a.append(s)
#                             XX2.append(a)
#         if (u,v)==(3,4):
#             for row in customer:
#                 for k in modes:
#                     for s in departure:
#                         if X[int(row[0]),u,v,k,s].x==1:
#                             a=[]
#                             a.append(int(row[0]))
#                             a.append(k)
#                             a.append(s)
#                             XX3.append(a) 
#     return yy, XX1, XX2, XX3
def plot_Zub(Zub_list):
    y1=Zub_list
    plt.ylabel('Zub')

    plt.plot(y1)
    plt.show()
def plot_Zlb(Zlb_list):    
    y2=Zlb_list
    plt.ylabel('Zlb')
    plt.plot(y2)
    plt.show()

