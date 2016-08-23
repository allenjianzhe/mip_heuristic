#name 100915_3  try t=formula
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
    model.setObjective((16-8*u)*x1+(10-2*u)*x2+(-1)*u*x3+(4-4*u)*x4+10*u,GRB.MAXIMIZE)
    model.update()
    #add constaint
    model.addConstr(x1+x2<=1,'c0')
    model.addConstr(x3+x4<=1,'c1')
    #model.addConstr(8*x1+2*x2+x3+4*x4<=10,'c2')
    model.update()
    model.optimize()
    return x1,x2,x3,x4,model.objVal


##(x1,x2,x3,x4,ZZ)=MIP(model, u=0)
##print 'u0',u
##print 'ZZ',ZZ
##print 'x1',x1.x
##print 'x2',x2.x
##print 'x3',x3.x
##print 'x4',x4.x

u=0
k=0
sigma=2
Z_fea=0 
t=1
#(x1,x2,x3,x4,Z)=MIP(model,u)
Zub=20
Z_fea_temple=0
print 'k',k,'t',t,'u',u,'sigma',sigma
#for i in range(0,5):
while sigma>0.005:
        (x1,x2,x3,x4,Z)=MIP(model,u)
        u=max(0,u-t*(10-8*x1.x-2*x2.x-x3.x-4*x4.x))
        t=sigma*(Zub-Z_fea)/((10-8*x1.x-2*x2.x-x3.x-4*x4.x)**2)
        print '\n'
        print 'x1',x1.x,'x2',x2.x,'x3',x3.x,'x4',x4.x
        print 'k',k,'t',t,'u',u
        print 'sigma',sigma,'Z',Z,'Z_fea',Z_fea,'Zub',Zub
        print '\n'
        #sigma=sigma*0.5
        if Z<Zub:
            Zub=Z
            sigma=sigma
        else:
            sigma=0.9*sigma
        Zub=min(Zub,Z)
        if 8*x1.x+2*x2.x+x3.x+4*x4.x<=10 and Z>0:
            Z_fea_temple=16*x1.x+10*x2.x+4*x4.x
            Z_fea=max(Z_fea_temple,Z_fea)
        k+=1
##for i in range(0,10):
##    if i==0:
##        (x1,x2,x3,x4,ZZ)=MIP(model,u)
##        t=sigma*(ZZ-Z_fea)/((10-8*x1.x-2*x2.x-x3.x-4*x4.x)**2)
##        u=max(0,u-t*(10-8*x1.x-2*x2.x-x3.x-4*x4.x))
##        print 'k',k,'t',t,'u',u,'sigma',sigma
##        k+=1
##    else:
##        (x1,x2,x3,x4,Z)=MIP(model,u)
##        if ZZ==Z:# means no change, then we need to change sigma and go on
##            sigma=sigma*0.5
##            t=sigma*(Z-Z_fea)/((10-8*x1.x-2*x2.x-x3.x-4*x4.x)**2)
##            u=max(0,u-t*(10-8*x1.x-2*x2.x-x3.x-4*x4.x))
##            print 'k',k,'t',t,'u',u
##            k+=1
##        else: # means u is getting small, keep going, no change.
##            ZZ=Z
##            print 'k',k,'t',t,'u',u
##            k+=1
