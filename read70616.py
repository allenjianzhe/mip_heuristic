#file name read70616, based on read051315 CHANGE DT to 2 departure time for each mode
import csv 
import sys
import math


#plan=list(range(1,17))
##arcs={
##    1:('CS', 'WH'),
##    2:('WH', 'ZZ'),
##    3:('ZZ', 'BJ')
##    }
nodes=[1,2,3,4] # set of routes
departure=[1,2] #each plan has two departure time
#modes = ['T','R','H','A']
modes=[1,2,3,4]
#arc capacity
def getC(nodes, modes, departure):
    C={}
    for i in nodes:
        if i != 4:
            for k in modes:
                for s in departure:
                    C[i,1,s]=400
                    C[i,2,s]=400
                    C[i,3,s]=400
                    C[i,4,s]=400
    return C

##C={}
###max_arc_C=0
##for i in nodes:
##    for k in modes:
##        for s in departure:
##            if k==1:#truck
##                C[i,k,s]=400
##            if k==2:#rail
##                C[i,k,s]=400
##            if k==3:#high speed
##                C[i,k,s]=400
##            if k==4:#air
##                C[i,k,s]=400
##            if max_arc_C<arc_C[i,k,s]:
##                max_arc_C=arc_C[i,k,s]
#print 'arc_C',arc_C

o=open(r'C:\Users\MacBook Air\Desktop\my research\cus_500.csv','r')#apple
#o=open(r'C:\Users\zjian\Desktop\my research\cus_3.csv','r')
reader= csv.reader(o)
#header = reader.next()
o.seek(0)
customer=[]
##quantity=[]
DD={}
penalty=[]
Destination=[]
for row in reader:
    customer.append(row)
o.close()
#print 'customer',customer

for row in customer:
    DD[int(row[0])]=int(row[3])
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
##Distance  ={}
####Distance[1]=413
####Distance[2]=485
####Distance[3]=695
####Distance[4]=741
##Distance[1]=400
##Distance[2]=500
##Distance[3]=700
##Distance[4]=800
#print Distance[3,4]
#trans time of mode trans_time[i-1,i,mode]
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
##tau={}
##for i in nodes:
##    if i ==4:
##        continue
##    else:
##        for k in modes:
##            if k==1:
##                tau[i,k]=round(Distance[i]/60.0)
##            if k==2:
##                tau[i,k]=round(Distance[i]/100.0)
##            if k==3:
##                tau[i,k]=round(Distance[i]/250.0)
##            if k==4:
##                tau[i,k]=round(Distance[i]/500.0)
# TRANS time of y (3PL)
##trans_time_y={}
##for i in node:
##    if i==1:
##        trans_time_y[i]=round(Distance[i]/500.0)
##    elif i==2:
##        trans_time_y[i]=round(Distance[i]/500.0)
##    elif i==3:
##        trans_time_y[i]=round(Distance[i]/500.0)
##    elif i==4:
##        trans_time_y[i]=round(Distance[i]/500.0)
#print trans_time_y

#print 'trans_time',trans_time


#arc trans cost
def getf(nodes,modes,Distance):#similar to above but delete the customer
    f={}
    for i in nodes:
        if i==4:
            continue
        else:
            for k in modes:
                f[i,1]=0.3*3000*Distance[i]/1000.0
                f[i,2]=0.5*3000*Distance[i]/1000.0
                f[i,3]=1.5*3000*Distance[i]/1000.0
                f[i,4]=2.0*3000*Distance[i]/1000.0
    return f
##f={}
##
##for i in nodes:
##    if i==4:
##        continue
##    else:
##        for k in modes:
##            if k==1:
##                f[i,k]=0.3*3000*Distance[i]/1000.0
##            elif k==2:
##                f[i,k]=0.5*3000*Distance[i]/1000.0
##            elif k==3:
##                f[i,k]=1.5*3000*Distance[i]/1000.0
##            elif k==4:
##                f[i,k]=2.0*3000*Distance[i]/1000.0
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
##dT={}
##                
##dT[1,1,1]=1
##dT[1,1,2]=2
##
##
##
##dT[1,2,1]=1
##dT[1,2,2]=2
##
##
##dT[1,3,1]=1
##dT[1,3,2]=3
##
##
##dT[1,4,1]=1
##dT[1,4,2]=3
##
##
##dT[2,1,1]=9
##dT[2,1,2]=10
##
##
##dT[2,2,1]=9
##dT[2,2,2]=10
##
##
##dT[2,3,1]=5
##dT[2,3,2]=7
##
##
##dT[2,4,1]=4
##dT[2,4,2]=6
##
##
##dT[3,1,1]=18
##dT[3,1,2]=20
##
##
##dT[3,2,1]=15
##dT[3,2,2]=20
##
##
##dT[3,3,1]=9
##dT[3,3,2]=11
##
##
##dT[3,4,1]=8
##dT[3,4,2]=10

ST={}#shipping time of route n if 3PL is used, here all make ==1

for i in nodes:
    if i==4:
        continue
    else:
        ST[i]=1
customer = sorted(customer,key=lambda x:x[2],reverse=True)

