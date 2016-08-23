#file name read70216.py
import csv 
import sys
import math

M=1000000000
#fix cost of 3pl
#F=15480
F=1250
# set of routes
nodes=[1,2,3,4]
#departure time
departure=[1,2] 
#modes = ['T','R','H','A'], truck, rail, high speed, air
modes=[1,2,3,4]

def getC(nodes, modes, departure):
    C={}
    for i in nodes:
        if i != 4:
            for k in modes:
                for s in departure:
                    C[i,k,s]=6000
##                    C[i,1,s]=500
##                    C[i,2,s]=500
##                    C[i,3,s]=500
##                    C[i,4,s]=500
    return C
    
def getDistance():
    Distance  ={}
##    Distance[1]=413
##    Distance[2]=485
##    Distance[3]=695
##    Distance[4]=741
    Distance[1]=400
    Distance[2]=500
    Distance[3]=700
    Distance[4]=800
    return Distance
#transportation time
def getTau(nodes,modes,Distance):
    tau={}
    for i in nodes:
            if i==4:
                continue
            else:
                for k in modes:
                    tau[i,1]=round(Distance[i]/60.0)
                    tau[i,2]=round(Distance[i]/100.0)
                    tau[i,3]=round(Distance[i]/250.0)
                    tau[i,4]=round(Distance[i]/500.0)
    return tau
##def getArcTransCost(customer,nodes,modes,Distance):
##    arc_trans_cost={}
##    for row in customer:
##        for i in nodes:
##            if i==4:
##                continue
##            else:
##                for k in modes:
##                    arc_trans_cost[int(row[0]),i,1]=0.3*3000*Distance[i]/1000.0
##                    arc_trans_cost[int(row[0]),i,2]=0.5*3000*Distance[i]/1000.0
##                    arc_trans_cost[int(row[0]),i,3]=1.5*3000*Distance[i]/1000.0
##                    arc_trans_cost[int(row[0]),i,4]=2.0*3000*Distance[i]/1000.0
##    return arc_trans_cost
##def getf(nodes,modes,Distance):#similar to above but delete the customer
##    f={}
##    for i in nodes:
##        if i==4:
##            continue
##        else:
##            for k in modes:
##                f[i,1]=0.3*3000*Distance[i]/1000.0
##                f[i,2]=0.5*3000*Distance[i]/1000.0
##                f[i,3]=1.5*3000*Distance[i]/1000.0
##                f[i,4]=2.0*3000*Distance[i]/1000.0
##    return f
def getf(nodes,modes,Distance):#similar to above but delete the customer
    f={}
    for i in nodes:
        if i==4:
            continue
        else:
            for k in modes:
                f[i,1]=300*Distance[i]/1000.0
                f[i,2]=500*Distance[i]/1000.0
                f[i,3]=1500*Distance[i]/1000.0
                f[i,4]=2000*Distance[i]/1000.0
    return f
def getdT():
    dT={}         
    dT[1,1,1]=1
    dT[1,1,2]=2

    dT[1,2,1]=1
    dT[1,2,2]=2


    dT[1,3,1]=1
    dT[1,3,2]=3


    dT[1,4,1]=1
    dT[1,4,2]=3


    dT[2,1,1]=9
    dT[2,1,2]=10


    dT[2,2,1]=9
    dT[2,2,2]=10


    dT[2,3,1]=5
    dT[2,3,2]=7


    dT[2,4,1]=4
    dT[2,4,2]=6


    dT[3,1,1]=18
    dT[3,1,2]=20


    dT[3,2,1]=15
    dT[3,2,2]=20


    dT[3,3,1]=9
    dT[3,3,2]=11


    dT[3,4,1]=8
    dT[3,4,2]=10
    return dT
o=open(r'C:\Users\MacBook Air\Desktop\my research\cus_5.csv','r')
reader= csv.reader(o)
o.seek(0)
customer=[]
DD={}
for row in reader:
    customer.append(row)
for row in customer:
    DD[int(row[0])]=int(row[3])
customer = sorted(customer,key=lambda x:x[2],reverse=True)
ending_time={}

customer = sorted(customer,key=lambda x:x[2],reverse=True)                
#print customer,'customer'
