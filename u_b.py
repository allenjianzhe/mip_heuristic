




    for row in customer:
        for k in modes:
            for s in departure:
    customer = sorted(row[0] ,key=row[2])

arc_C={}#arc_C: each arc capacity
arc_C=getArcC(nodes,modes,departure)


    G = 0
    for k in modes:
        for s in departure:
            for i in nodes:
                if i==4:
                    continue
                else:
                    for row in customer:
                        if X[int(row[0]),i,k,s].x>0:
                            #print 'test',X[int(row[0]),i,k,s].x # why X=0 will also be shown?
                            #if you print X[int(row[0]),i,k,s], then all the X will be shown
                            G=G+int(row[2])*X[int(row[0]),i,k,s].x
                    #print 'middle G',G, 'i,k,s',i,k,s
                    G=G-arc_C[i,k,s] # right?????????
                    m.addConstr(0,GRB.LESS_EQUAL,G[int(row[0]),i,k,s],name='HeurisConstr1_%s_%s_%s_%s'%(int(row[0]),i,k,s))   #公式37的约束条件

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
            #a=LinExpr()
            if i==4:
                continue
            else:
                for row in customer:
                    if X[int(row[0]),i,k,s].x>0:
                        #print 'i,k,s',i,k,s
                        #print 'GG[i,k,s]',GG[i,k,s]
                        GG[i,k,s]=GG[i,k,s]+int(row[2])*X[int(row[0]),i,k,s].x  #公式38的表达
                        #print 'GG[i,k,s]',GG[i,k,s]
                GG[i,k,s]=GG[i,k,s]-arc_C[i,k,s]# where is the problem?
                
print 'GG','\n',GG