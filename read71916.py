#file name read70816, based on read051315 CHANGE DT to 2 departure time for each mode
import csv 
import sys
import math

M=1000000000
#fix cost of 3pl
#F=15480
F=1250
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
##def getC(nodes, modes, departure):
##    C={}
##    for i in nodes:
##        if i != 4:
##            for k in modes:
##                for s in departure:
##                    C[i,1,s]=400
##                    C[i,2,s]=400
##                    C[i,3,s]=400
##                    C[i,4,s]=400
##    return C
def getC(nodes, modes, departure):
    C={}
    for n in nodes:
        if n != 4:
            for k in modes:
                for s in departure:
                    C[n,k,s]=6000
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

o=open(r'C:\Users\MacBook Air\Desktop\my research\cus_5.csv','r')#apple
#o=open(r'C:\Users\zjian\Desktop\my research\cus_3.csv','r')
reader= csv.reader(o)
#header = reader.next()
o.seek(0)
customer=[]
##quantity=[]
DD={}
#penalty=[]
#Destination=[]
for row in reader:
    customer.append(row)
o.close()

#print 'customer',customer

for row in customer:
    DD[int(row[0])]=int(row[3])
def getDistance():
    Distance={}
    Distance[1]=400
    Distance[2]=500
    Distance[3]=700
    Distance[4]=800
    return Distance
    
##def getDistance():
##    Distance  ={}
####    Distance[1]=413
####    Distance[2]=485
####    Distance[3]=695
####    Distance[4]=741
##    Distance[1]=500
##    Distance[2]=750
##    Distance[3]=1000
##    Distance[4]=2000
##    return Distance
##Distance  ={}
##Distance=getDistance()
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
    for n in nodes:
            if n==4:
                continue
            else:
                for k in modes:
                    tau[n,1]=round(Distance[n]/60.0)
                    tau[n,2]=round(Distance[n]/100.0)
                    tau[n,3]=round(Distance[n]/250.0)
                    tau[n,4]=round(Distance[n]/500.0)
    return tau
##tau={}
##tau=getTau(nodes,modes,Distance)
#print tau
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
#def getf(nodes,modes,Distance):#similar to above but delete the customer
 #   f={}
  #  unit=500.0
   # for n in nodes:
    #    if n==4:
     #       continue
      #  else:
       #     for k in modes:
        #        f[n,1]=int(300*Distance[n]/unit)
         #       f[n,2]=int(500*Distance[n]/unit)
          #      f[n,3]=int(1500*Distance[n]/unit)
           #     f[n,4]=int(2000*Distance[n]/unit)    
    #return f
#arc trans cost
##def getf(nodes,modes,Distance):#similar to above but delete the customer
##    f={}
##    unit=1000.0
##    for n in nodes:
##        if n==4:
##            continue
##        else:
##            for k in modes:
##                f[n,1]=int(0.3*int(row[2])*Distance[n]/unit)
##                f[n,2]=int(0.5*int(row[2])*Distance[n]/unit)
##                f[n,3]=int(1.5*int(row[2])*Distance[n]/unit)
##                f[n,4]=int(2*int(row[2])*Distance[n]/unit)    
##    return f
def getf(nodes,modes,Distance):#similar to above but delete the customer
    f={}
    unit=1000.0
    for n in nodes:
        if n==4:
            continue
        else:
            for k in modes:
                f[n,1]=int(300*Distance[n]/unit)
                f[n,2]=int(500*Distance[n]/unit)
                f[n,3]=int(1500*Distance[n]/unit)
                f[n,4]=int(2000*Distance[n]/unit)    
    return f
def getST(nodes):
    ST={}#shipping time of route n if 3PL is used, here all make ==1
    for n in nodes:
        if n==4:
            continue
        else:
            ST[n]=1
    return ST
# first dT, using distance 1=400
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

#change dT, first distance is 500
##def getdT():
##    dT={}         
##    dT[1,1,1]=1
##    dT[1,1,2]=2
##
##    dT[1,2,1]=1
##    dT[1,2,2]=2
##
##    dT[1,3,1]=1
##    dT[1,3,2]=3
##
##    dT[1,4,1]=1
##    dT[1,4,2]=3
##
##    dT[2,1,1]=9
##    dT[2,1,2]=10
##
##    dT[2,2,1]=6
##    dT[2,2,2]=7
##
##    dT[2,3,1]=3
##    dT[2,3,2]=5
##
##    dT[2,4,1]=2
##    dT[2,4,2]=4
##
##    dT[3,1,1]=22
##    dT[3,1,2]=24
##
##    dT[3,2,1]=15
##    dT[3,2,2]=17
##
##    dT[3,3,1]=7
##    dT[3,3,2]=9
##
##    dT[3,4,1]=5
##    dT[3,4,2]=7
##    return dT
customer = sorted(customer,key=lambda x:x[2],reverse=True)
#ending_time={}
C={}
C=getC(nodes,modes,departure)
#Distance: each arc distance
Distance={}
Distance=getDistance()
#tau: each mode at each arc transporatation time
tau={}
tau=getTau(nodes,modes,getDistance())
#f: unit cost of mode at each arc
f={}
f=getf(nodes,modes,getDistance())
#dT: departure time at each arc
dT={}
dT=getdT()
