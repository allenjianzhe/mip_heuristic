#file name read052515, based on read051315
import csv 
import sys
import math


#plan=list(range(1,17))
##arcs={
##    1:('CS', 'WH'),
##    2:('WH', 'ZZ'),
##    3:('ZZ', 'BJ')
##    }
nodes=[3,4] # set of routes

departure=[1,2,3,4,5,6] #each plan has two departure time
#modes = ['T','R','H','A']
modes=[1,2,3,4]

#arc capacity
arc_C={}
#max_arc_C=0
for i in nodes:
    if i==4:
        continue
    else:
        for k in modes:
            for s in departure:
                if k==1:#truck
                    arc_C[i,k,s]=300
                if k==2:#rail
                    arc_C[i,k,s]=500
                if k==3:#high speed
                    arc_C[i,k,s]=400
                if k==4:#air
                    arc_C[i,k,s]=100
##            if max_arc_C<arc_C[i,k,s]:
##                max_arc_C=arc_C[i,k,s]
#print 'arc_C',arc_C

#o=open(r'C:\Users\zjian\Desktop\my research\cus_200.csv','r')
o=open(r'C:\Users\MacBook Air\Desktop\my research\cus_7.csv','r')#apple
reader= csv.reader(o)
#header = reader.next()
o.seek(0)
customer=[]
quantity=[]
DD={}
penalty=[]
Destination=[]
for row in reader:
    customer.append(row)
    #print customer
o.close()
for row in customer:
    DD[int(row[0])]=int(row[3])
    #print DD[int(row[0])]

Distance  ={}
##Distance[1]=413
##Distance[2]=485
Distance[3]=695

#Distance[3,4]=741
#print Distance[3,4]
#trans time of mode trans_time[i-1,i,mode]
trans_time={}
for i in nodes:
    if i==4:
        continue
    else:
        for k in modes:
            if k==1:
                trans_time[i,k]=round(Distance[i]/60.0)
            if k==2:
                trans_time[i,k]=round(Distance[i]/100.0)
            if k==3:
                trans_time[i,k]=round(Distance[i]/250.0)
            if k==4:
                trans_time[i,k]=round(Distance[i]/500.0)
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
arc_trans_cost={}
for row in customer:
    for i in nodes:
        if i==4:
            continue
        else:
            for k in modes:
                if k==1:
                    arc_trans_cost[int(row[0]),i,k]=300*int(row[2])*Distance[i]/1000.0
                elif k==2:
                    arc_trans_cost[int(row[0]),i,k]=500*int(row[2])*Distance[i]/1000.0
                elif k==3:
                    arc_trans_cost[int(row[0]),i,k]=1500*int(row[2])*Distance[i]/1000.0
                elif k==4:
                    arc_trans_cost[int(row[0]),i,k]=2000*int(row[2])*Distance[i]/1000.0
#print 'arc_trans_cost',arc_trans_cost

#departure time [i,mode,departure]


##for i in node:
##    for k in modes:
##        for s in range(len(departure)):
##            if i==1:
##                if s==0:
##                    dT[i,k,s]=1
##                elif s==1:
##                    dT[i,k,s]=10
##            elif i==2:
##                dT[i,k,s]=dT[i-1,k,s]+trans_time[i-1,k]+1
##            elif i==3:
##                dT[i,k,s]=dT[i-2,i-1,k,s]+trans_time[i-2,i-1,k]+1
####                elif i==4:
####                    dT[i-1,i,k,s]=dT[i-2,i-1,k,s]+trans_time[i-2,i-1,k]+1
##arc_id={}
##for row in customer:
##    for i in node:
##        if i==0:
##            continue
##        else:
##            arc_id[int(row[0]),i]=0
#print arc_id
##customer_id={}
##for row in customer:
##    customer_id[int(row[0])]=0
###print customer
##
##new_Total_Trans_Cost=0
##new_Total_Penalty_Cost=0
##new_Total_Cost=0

#print 'dT',dT
dT={}
            
##dT[1,1,1]=1
##dT[1,1,2]=3
##dT[1,1,3]=5
##dT[1,1,4]=7
##dT[1,1,5]=9
##dT[1,1,6]=11
##
##dT[1,2,1]=1
##dT[1,2,2]=4
##dT[1,2,3]=7
##dT[1,2,4]=10
##dT[1,2,5]=13
##dT[1,2,6]=16
##
##dT[1,3,1]=1
##dT[1,3,2]=5
##dT[1,3,3]=9
##dT[1,3,4]=13
##dT[1,3,5]=17
##dT[1,3,6]=21
##
##dT[1,4,1]=1
##dT[1,4,2]=6
##dT[1,4,3]=11
##dT[1,4,4]=16
##dT[1,4,5]=21
##dT[1,4,6]=26
##
##dT[2,1,1]=9
##dT[2,1,2]=11
##dT[2,1,3]=13
##dT[2,1,4]=15
##dT[2,1,5]=17
##dT[2,1,6]=19
##
##dT[2,2,1]=7
##dT[2,2,2]=10
##dT[2,2,3]=13
##dT[2,2,4]=16
##dT[2,2,5]=19
##dT[2,2,6]=22
##
##dT[2,3,1]=5
##dT[2,3,2]=9
##dT[2,3,3]=13
##dT[2,3,4]=17
##dT[2,3,5]=21
##dT[2,3,6]=25
##
##dT[2,4,1]=4
##dT[2,4,2]=9
##dT[2,4,3]=14
##dT[2,4,4]=19
##dT[2,4,5]=24
##dT[2,4,6]=29

dT[3,1,1]=18
dT[3,1,2]=20
dT[3,1,3]=22
dT[3,1,4]=24
dT[3,1,5]=26
dT[3,1,6]=28

dT[3,2,1]=14
dT[3,2,2]=17
dT[3,2,3]=20
dT[3,2,4]=23
dT[3,2,5]=26
dT[3,2,6]=29

dT[3,3,1]=9
dT[3,3,2]=13
dT[3,3,3]=17
dT[3,3,4]=21
dT[3,3,5]=25
dT[3,3,6]=29

dT[3,4,1]=7
dT[3,4,2]=11
dT[3,4,3]=15
dT[3,4,4]=19
dT[3,4,5]=23
dT[3,4,6]=27
#print dT
