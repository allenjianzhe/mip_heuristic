#file name netflow81716.py  based on netflow051215MIP, delete Tardiness, change 3PL to arc. 
import sys
#sys.path.append('C:/gurobi563/win32/python27/lib/gurobipy')
sys.path.append('C:/gurobi605/win32/python27/lib/gurobipy')
#sys.path.append('C:/gurobi604/win32/python27/lib/gurobipy')  # for apple
from gurobipy import *
from read81616 import *
# import time   
# start_time = time.clock()
# m = Model('MIP')

# def my_model_callback(model, where):
#     # if where == GRB.Callback.MESSAGE and time.clock() - start > 60:
#     #     model.terminate()
    
#     if where == GRB.Callback.MIP:
#         objbst = model.cbGet(GRB.Callback.MIP_OBJBST)
#         objbnd = model.cbGet(GRB.Callback.MIP_OBJBND)
#         if abs(objbst - objbnd) < 0.02 * (1.0 + abs(objbst)):
#             print ('stop ealier, 2% Gap achieved')
#             model.terminate()
def MIP2(m,customer):
    ####################################################################################################
    #decision variable X: binary variable. X[customer,i,i+1,m,k]
    X = {}
    for row in customer:
        for (u,v) in G.edges():
            for k in modes:
                for s in departure:
                    X[int(row[0]),u,v,k,s]=m.addVar(obj=int(row[2])*G[u][v]['f',k],vtype=GRB.BINARY, name="X_%s_%s_%s_%s_%s"%(row[0], u, v, k,s))
    m.update()
    # print(id(m),'*'*100)
    # for (row,u,v,k,s)in all_fixed_x_idxes:
    #     #print (row,u.v,k,s),'$$$$$$$$$$$$$$$$$'
    #     #m.addConstr(X[row,u.v,k,s],GRB.EQUAL,1)
    #     X[row,u.v,k,s].LB=1
        
    #decision variable y: binary variable of 3PL
    y={}
    for row in customer:
        for (u,v) in G.edges():
            y[int(row[0]),u,v] = m.addVar(obj=int(row[2])*F,vtype=GRB.BINARY)     
    m.update()
    #decision variable z: binary variable of route chosen
    z={}
    for row in customer:
        for (u,v) in G.edges():
            z[int(row[0]),u,v] = m.addVar(obj = 0 , vtype=GRB.BINARY, name="z_%s_%s_%s"%(row[0],u,v))
    m.update()
    #decision variable: arrive time at each node
    t={}
    for row in customer:
        for u in G.nodes():
            if u!=1:
                t[int(row[0]),u]=m.addVar(obj=0,vtype='C')  
    m.update()
    #decision variable:Time tardiness of customer
    TD={}
    for row in customer:
            TD[int(row[0])]=m.addVar(obj=int(row[2])*int(row[4]),vtype='C',name='Tardiness_%s'%(int(row[0])))
    m.update()
    ####################################################################################################
    #constraint 2, definition of T
    for row in customer:
        for k in modes:
            for s in departure:
                m.addConstr(TD[int(row[0])],GRB.EQUAL,t[int(row[0]),len(G.nodes())]-int(row[3]))
    m.update()
    #Constraint 3,  for each customer, each link, only one mode can be selected
    for row in customer:
        for (u,v) in G.edges():
            expr = LinExpr()       
            for k in modes:
                    for s in departure:
                            expr.addTerms(1.0,X[int(row[0]),u,v,k,s])
            expr.add(y[int(row[0]),u,v])
            m.addConstr(expr, GRB.EQUAL, z[int(row[0]),u,v])
    m.update()
    #constraint 4,  arc capacity
    for k in modes:
        for s in departure:
            for (u,v) in G.edges():
                expr = LinExpr()
                for row in customer:
                        expr.addTerms(int(row[2]),X[int(row[0]),u,v,k,s])
                expr.addConstant(-1*G[u][v]['C',k,s])
                m.addConstr(expr,GRB.LESS_EQUAL, 0,'arcCapacity_%r_%r_%r_%r_%r'%(int(row[0]),u,v,k,s))      
    m.update() 
    #constraint 5, flow balance, all to start
    for row in customer:
        expr = LinExpr()
        for v in G.neighbors(1):
            expr.addTerms(1,z[int(row[0]),1,v])
        m.addConstr(expr,GRB.EQUAL,1)
    m.update()
    #constraint 6, flow balance
    # print(id(G),'='*50)
    for row in customer:        
        for u in G.nodes():
            expr1 = LinExpr()
            if u!=1 and u!=len(G.nodes()):
                all_node_to_u = [u1 for (u1,v1) in G.edges() if v1 == u]
                for to_u in all_node_to_u:
                    # print 'z_%s_%s'%(to_u,u)
                    expr1.addTerms(1, z[int(row[0]), to_u, u])
                all_node_from_u = [v1 for (u1,v1) in G.edges() if u1 == u]
                for from_u in all_node_from_u:
                    # print '-z_%s_%s'%(u,from_u)
                    expr1.addTerms(-1, z[int(row[0]), u, from_u])
            m.addConstr(expr1,GRB.EQUAL,0, name="in_out_rule_at_%s"%u)
    m.update()
    #constraint, flow balance, all to the end
    for row in customer:
        expr = LinExpr()
        #nodes_to_end = G.neighbors(len(G.nodes()))
        nodes_to_end = [u1 for (u1,v1) in G.edges() if v1 == len(G.nodes())]
        for u in nodes_to_end:
            if u!=len(G.nodes()):
                expr.addTerms(1,z[int(row[0]),u,len(G.nodes())])
        m.addConstr(expr,GRB.EQUAL,1)
    m.update()
    #constraint 7, time constraint 
    for row in customer:        
            for (u,v) in G.edges():
                expr = LinExpr()                
                for k in modes:
                        for s in departure:                                            
                                expr.addTerms(G[u][v]['dT',k,s]+G[u][v]['tau',k],X[int(row[0]),u,v,k,s])
                # expr.add(-1*y[int(row[0]),u,v]*M)
                m.addConstr(expr,GRB.LESS_EQUAL,t[int(row[0]),v])                        
    m.update()                    
    #constraint 8, time constraint 
    for row in customer:        
        for (u,v) in G.edges(): 
            if u != 1:                   
                expr1 = LinExpr()
                for k in modes:
                        for s in departure:                                            
                                expr1.addTerms(G[u][v]['dT',k,s],X[int(row[0]),u,v,k,s])
                expr1.add((1+y[int(row[0]),u,v]-z[int(row[0]),u,v])*M)
                m.addConstr(expr1,GRB.GREATER_EQUAL,t[int(row[0]),u])
    m.update()
    #constraint 9, time constraint 
    for row in customer:
        for (u,v) in G.edges():
            if u != 1:
                expr1 = LinExpr()
                expr1.addTerms(1, t[int(row[0]), u])
                expr1.add(G[u][v]['ST'] - M*(1 - y[int(row[0]), u, v]))
                m.addConstr(expr1, GRB.LESS_EQUAL, t[int(row[0]), v])
    m.update()    
    m.__data = X, y, t, TD, ending_time
    return m
####################################################################################################
if __name__ == '__main__':
    m = Model("MIP2")
    MIP2(m,customer)
    m.setParam('MIPGap',.02)
    # m.setParam('TimeLimit', 60)
    m.optimize()
    # print(id(m))
    m.write('./my_model.lp')
    m.write('./my_model_sol.sol')
    # print(id(G),'-'*50)
    # m.optimize(my_model_callback)
    # if m.MIPGAP<=0.02:
    #     exit()
    X,y,t,TD,ending_time=m.__data
##    q=m.objVal
##    print q,'$$$$$$$$$$$'
    ##print "\n"
  
    for row in customer:
        print 'Customer',int(row[0]),'Destination ',row[1], 'quantity ',int(row[2]),'DD',int(row[3]),'penalty',int(row[4]),'Tardiness',TD[int(row[0])].x
    print "\n"
    ####print 'Summary solution'                    
    threePLCost=0
    TransCost=0
    TotalTransCost=0
    TotalTardinessCost=0
    TotalCost=0
    with open('c:/Users/MacBook Air/Desktop/output_mip.txt', 'w') as mip_out:
        if m.status == GRB.status.OPTIMAL:
            for row in customer:
                #print 'Customer',int(row[0]),'Tardiness',T[int(row[0])].x
                TotalTardinessCost+=TD[int(row[0])].x*int(row[4])*int(row[2])
                for (u,v) in G.edges():
                    if y[int(row[0]),u,v].x>0:
                        print 'Customer',int(row[0]),'arc',(u,v),' using 3PL','Trans_cost',F*int(row[2])
                        mip_out.write('Customer %d arc %r using 3PL Trans_cost %d\n'%(int(row[0]),(u,v),F*int(row[2])))
                        threePLCost+=F*int(row[2])        
        TotalTransCost=0
        for row in customer:
            for (u,v) in G.edges():
                # print (u,v)
                for k in modes:
                    for s in departure:
                        if X[int(row[0]),u,v,k,s].x > 0:
                            print 'Customer',int(row[0]),'link',(u,v),'arc_mode_num',k,'departureTimeIndex',s,'arc_cost',G[u][v]['f',k]*int(row[2]),'start_Time',G[u][v]['dT',k,s],'Trans_time',G[u][v]['tau',k],'t',t[int(row[0]),v].x,'real_arrive_time',G[u][v]['dT',k,s]+G[u][v]['tau',k]
                            mip_out.write('Customer %d link %r arc_mode_num %d departureTimeIndex %d f %d start_Time %d tau %d t %f real_arrive_time %f\n'%(int(row[0]),(u,v),k,s,G[u][v]['f',k]*int(row[2]),G[u][v]['dT',k,s],G[u][v]['tau',k],t[int(row[0]),v].x,G[u][v]['dT',k,s]+G[u][v]['tau',k]))
                            TransCost+=G[u][v]['f',k]*int(row[2])
    TotalTransCost=TransCost+threePLCost
    TotalCost=  TotalTardinessCost+   TotalTransCost
    print '\n'
    print 'Basic info'
    print 'customer size',len(customer)
    print 'MIP SOLUTION 3 ARCS'
    print 'Trans_Cost',TransCost
    print '3PL_Cost',threePLCost
    print 'Total_Trans_Cost',TotalTransCost
    print 'Total_Penalty_Cost',TotalTardinessCost
    print 'Total_Cost',TotalCost
    # print 'computer time (seconds): ',time.clock() - float(start_time)
    # print '\n' 
    # for u in G.nodes():
    #     if u!=1 and u!=len(G.nodes()):
    #         all_node_to_u = [u1 for (u1,v1) in G.edges() if v1 == u]
    #         print "all_node_to_%s"%u,all_node_to_u
    #         all_node_from_u = [v1 for (u1,v1) in G.edges() if u1 == u]
    #         print "all_node_from_%s"%u,all_node_from_u
