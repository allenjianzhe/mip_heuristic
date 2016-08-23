#file name read0804
import csv 
import sys
import math


#plan=list(range(1,17))
arcs={
    1:('CS', 'WH'),
    2:('WH', 'ZZ'),
    3:('ZZ', 'BJ'),
    4:('BJ', 'SY')
    }
node=[0,1,2,3,4]

departure=[1,2] #each plan has two departure time
#modes = ['T','R','H','A']
modes=[1,2,3,4]

#arc capacity
arc_C={}
max_arc_C=0
for i in node:
    if i==4:
        continue
    else:
        for k in modes:
            for s in range(len(departure)):
                if k==1:#truck
                    arc_C[i,i+1,k,s]=300
                if k==2:#rail
                    arc_C[i,i+1,k,s]=500
                if k==3:#high speed
                    arc_C[i,i+1,k,s]=400
                if k==4:#air
                    arc_C[i,i+1,k,s]=100
                if max_arc_C<arc_C[i,i+1,k,s]:
                    max_arc_C=arc_C[i,i+1,k,s]

o=open(r'C:\Users\zjian\Desktop\my research\cus_300.csv','r')
reader= csv.reader(o)
#header = reader.next()
o.seek(0)
customer=[]
quantity=[]
DD=[]
penalty=[]
Destination=[]
for row in reader:
    customer.append(row)
    #print customer
o.close()

Distance  ={}
Distance[0,1]=413
Distance[1,2]=485
Distance[2,3]=695
Distance[3,4]=741
#print Distance[3,4]
#trans time of mode trans_time[i-1,i,mode]
trans_time={}
for i in node:
    if i==0:
        continue
    else:
        for k in modes:
            if k==1:
                trans_time[i-1,i,k]=round(Distance[i-1,i]/60)
            if k==2:
                trans_time[i-1,i,k]=round(Distance[i-1,i]/100)
            if k==3:
                trans_time[i-1,i,k]=round(Distance[i-1,i]/250)
            if k==4:
                trans_time[i-1,i,k]=round(Distance[i-1,i]/500)
# TRANS time of y (3PL)
trans_time_y={}
for i in node:
    if i==0:
        continue
    else:
        if i==1:
            trans_time_y[i-1,i]=round(Distance[i-1,i]/500)
        elif i==2:
            trans_time_y[i-1,i]=round(Distance[i-1,i]/500)
        elif i==3:
            trans_time_y[i-1,i]=round(Distance[i-1,i]/500)
        elif i==4:
            trans_time_y[i-1,i]=round(Distance[i-1,i]/500)
#print trans_time_y
#print trans_time
#arc trans cost
arc_trans_cost={}
for row in customer:
    for i in node:
        if i==0:
            continue
        else:
            for k in modes:
                if k==1:
                    arc_trans_cost[int(row[0]),i-1,i,k]=300*int(row[2])*Distance[i-1,i]/1000
                elif k==2:
                    arc_trans_cost[int(row[0]),i-1,i,k]=500*int(row[2])*Distance[i-1,i]/1000
                elif k==3:
                    arc_trans_cost[int(row[0]),i-1,i,k]=1500*int(row[2])*Distance[i-1,i]/1000
                elif k==4:
                    arc_trans_cost[int(row[0]),i-1,i,k]=2000*int(row[2])*Distance[i-1,i]/1000
#print arc_trans_cost

#departure time [i,i+1,mode,departure]
dT={}
for i in node:
    if i==0:
        continue
    else:
        for k in modes:
            for s in range(len(departure)):
                if i==1:
                    if s==0:
                        dT[i-1,i,k,s]=1
                    elif s==1:
                        dT[i-1,i,k,s]=10
                elif i==2:
                    dT[i-1,i,k,s]=dT[i-2,i-1,k,s]+trans_time[i-2,i-1,k]+1
                elif i==3:
                    dT[i-1,i,k,s]=dT[i-2,i-1,k,s]+trans_time[i-2,i-1,k]+1
                elif i==4:
                    dT[i-1,i,k,s]=dT[i-2,i-1,k,s]+trans_time[i-2,i-1,k]+1

