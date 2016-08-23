#name 100915_3  try t=formula
import sys
sys.path.append('C:/gurobi604/win32/python27/lib/gurobipy')
from gurobipy import *
import time
from start_file import *
u=0
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
Z_list=[]
sigma=2
Z_fea=0
i=0
Z=1
t=1
while  i!=50:
    (x1,x2,x3,x4,Z)=MIP(model, u)
    u=max(0,u-t*(10-8*x1.x-2*x2.x-x3.x-4*x4.x))
    print 'k',i,'t',t,'u',u,'x1',x1.x,'x2',x2.x,'x3',x3.x,'x4',x4.x
    print 'Z_fea',Z_fea, 'sigma',sigma
    #t=sigma*(Z-Z_fea)/((10-8*x1.x-2*x2.x-x3.x-4*x4.x)**2)
    t=t/3.0
    if 8*x1.x+2*x2.x+x3.x+4*x4.x<=10 and Z>=Z_fea:
        Z_fea=Z
    else:
        Z_fea=Z_fea
    if len(Z_list)==5:
        if Z<min(Z_list):
            Z_list=[]
            Z_list.append(Z)
        else:
            sigma=sigma/2.0
            Z_list=[]
            Z_list.append(Z)
    else:
        Z_list.append(Z)
        i+=1
# how to test the result? why x4 is not 0 but 1. why Z_fea is 16. 
        
