#name 100915_2  try t=1/3 remember, u is not variables, is constent. 
import sys
sys.path.append('C:/gurobi604/win32/python27/lib/gurobipy')
from gurobipy import *
import time
from start_file import *

model=Model('MIP')
def MIP(model,u):
    #add variables to model
    x1=model.addVar(lb=0,ub=1,vtype=GRB.BINARY,name='x1')
    x2=model.addVar(lb=0,ub=1,vtype=GRB.BINARY,name='x2')
    x3=model.addVar(lb=0,ub=1,vtype=GRB.BINARY,name='x3')
    x4=model.addVar(lb=0,ub=1,vtype=GRB.BINARY,name='x4')
    #u=model.addVar(lb=0,vtype='C',name='u')
    model.update()
    #set Obj
    obj=QuadExpr()
    model.setObjective((16-8*u)*x1+(10-2*u)*x2+(-1)*u*x3+(4-4*u)*x4,GRB.MAXIMIZE)
    model.update()
    #add constaint
    model.addConstr(x1+x2<=1,'c0')
    model.addConstr(x3+x4<=1,'c1')
    #model.addConstr(8*x1+2*x2+x3+4*x4<=10,'c2')
    model.update()
    model.optimize()
    
    return x1,x2,x3,x4,model.objVal

#t=0
k=0
t=1
sigma=2
u=0
print 'initial data','u=0','t0=1',
for i in range(0,10):
    Z_fea=0
    (x1,x2,x3,x4,Z)=MIP(model,u)
    #t=sigma*Z/((10-8*x1.x-2*x2.x-x3.x-4*x4.x)**2)
    u=max(0,u-t*(10-8*x1.x-2*x2.x-x3.x-4*x4.x))
    if u*(10-8*x1.x-2*x2.x-x3.x-4*x4.x)>=0:
        print '##############################',u*(10-8*x1.x-2*x2.x-x3.x-4*x4.x)
        Z_fea=16*x1.x+2*x2.x+4*x4.x
    else:
        print 'not feasible',u*(10-8*x1.x-2*x2.x-x3.x-4*x4.x)
    print 'k',k,'t',t,'u',u
    print 'x1',x1.x,'x2',x2.x,'x3',x3.x,'x4',x4.x
    print 'feasible solution',Z_fea
    t=t*(0.333)
    k+=1
