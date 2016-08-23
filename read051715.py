#file name read051715, based on read1028
import csv 
import sys
import math


#plan=list(range(1,17))
##arcs={
##    1:('CS', 'WH'),
##    2:('WH', 'ZZ')
##
##    }
node=[2,3]

departure=[1,2,3,4,5,6] #each plan has two departure time
#modes = ['T','R','H','A']; T:1 R:2  H:3  A:4
modes=[1,2,3,4]

#arc capacity
arc_C={}
capacity_left={}
max_arc_C=0
for i in node:
    if i==2:
        continue
    else:
        for k in modes:
            for s in range(len(departure)):
                if k==1:#truck
                    arc_C[i-1,i,k,s]=300
                if k==2:#rail
                    arc_C[i-1,i,k,s]=500
                if k==3:#high speed
                    arc_C[i-1,i,k,s]=400
                if k==4:#air
                    arc_C[i-1,i,k,s]=100
                if max_arc_C<arc_C[i-1,i,k,s]:
                    max_arc_C=arc_C[i-1,i,k,s]
capacity_left=arc_C
#print 'arc_C',arc_C
#print 'capacity_left beginning',capacity_left
#print arc_C
#o=open(r'C:\Users\zjian\Desktop\my research\cus_300.csv','r')#windows
o=open(r'C:\Users\MacBook Air\Desktop\my research\cus_300.csv','r')#apple
reader= csv.reader(o)
#header = reader.next()
o.seek(0)
customer=[]
quantity=[]
DD=[]
penalty=[]
##Destination=[]
for row in reader:
    customer.append(row)
    #print customer
o.close()

Distance  ={}
#Distance[0,1]=413
##Distance[1,2]=485
Distance[2,3]=695
##Distance[3,4]=741
#print Distance[3,4]
#trans time of mode trans_time[i-1,i,mode]
trans_time={}
for i in node:
    if i==2:
        continue
    else:
        for k in modes:
            if k==1:
                trans_time[i-1,i,k]=math.ceil(Distance[i-1,i]/60.0)
            if k==2:
                trans_time[i-1,i,k]=math.ceil(Distance[i-1,i]/100.0)
            if k==3:
                trans_time[i-1,i,k]=math.ceil(Distance[i-1,i]/250.0)
            if k==4:
                trans_time[i-1,i,k]=math.ceil(Distance[i-1,i]/500.0)
# TRANS time of y (3PL)
#print 'trans_time',trans_time
##trans_time_y={}
##for i in node:
##    if i==2:
##        continue
##    else:
##        if i==1:
##            trans_time_y[i-1,i]=math.ceil(Distance[i-1,i]/500.0)
##        elif i==2:
##            trans_time_y[i-1,i]=math.ceil(Distance[i-1,i]/500.0)
##        elif i==3:
##            trans_time_y[i-1,i]=math.ceil(Distance[i-1,i]/500.0)
##        elif i==4:
##            trans_time_y[i-1,i]=math.ceil(Distance[i-1,i]/500.0)
            
#print 'trans_time_y',trans_time_y
#print trans_time
#arc trans cost
arc_trans_cost={}
for row in customer:
    for i in node:
        if i==2:
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
##dT={}
##for i in node:
##    if i==0:
##        continue
##    else:
##        for k in modes:
##            for s in range(len(departure)):
##                if i==1:
##                    if s==0:
##                        dT[i-1,i,k,s]=1
##                    elif s==1:
##                        dT[i-1,i,k,s]=10
##                elif i==2:
##                    dT[i-1,i,k,s]=dT[i-2,i-1,k,s]+trans_time[i-2,i-1,k]+1
##                elif i==3:
##                    dT[i-1,i,k,s]=dT[i-2,i-1,k,s]+trans_time[i-2,i-1,k]+1
##                elif i==4:
##                    dT[i-1,i,k,s]=dT[i-2,i-1,k,s]+trans_time[i-2,i-1,k]+1
##print 'dT',dT
##arc_id={}
##for row in customer:
##    for i in node:
##        if i==2:
##            continue
##        else:
##            arc_id[int(row[0]),i]=0
#print arc_id
##customer_id={}
##for row in customer:
##    customer_id[int(row[0])]=0
#print customer
#print customer_id
##arrive_time={}
##for row in customer:
##    arrive_time[int(row[0])]=0
new_Total_Trans_Cost=0
new_Total_Penalty_Cost=0
new_Total_Cost=0
dT={}
            
##dT[0,1,1,0]=1
##dT[0,1,1,1]=3
##dT[0,1,1,2]=5
##dT[0,1,1,3]=7
##dT[0,1,1,4]=9
##dT[0,1,1,5]=11
##
##dT[0,1,2,0]=1
##dT[0,1,2,1]=4
##dT[0,1,2,2]=7
##dT[0,1,2,3]=10
##dT[0,1,2,4]=13
##dT[0,1,2,5]=16
##
##dT[0,1,3,0]=1
##dT[0,1,3,1]=5
##dT[0,1,3,2]=9
##dT[0,1,3,3]=13
##dT[0,1,3,4]=17
##dT[0,1,3,5]=21
##
##dT[0,1,4,0]=1
##dT[0,1,4,1]=6
##dT[0,1,4,2]=11
##dT[0,1,4,3]=16
##dT[0,1,4,4]=21
##dT[0,1,4,5]=26
##
##dT[1,2,1,0]=9
##dT[1,2,1,1]=11
##dT[1,2,1,2]=13
##dT[1,2,1,3]=15
##dT[1,2,1,4]=17
##dT[1,2,1,5]=19
##
##dT[1,2,2,0]=7
##dT[1,2,2,1]=10
##dT[1,2,2,2]=13
##dT[1,2,2,3]=16
##dT[1,2,2,4]=19
##dT[1,2,2,5]=22
##
##dT[1,2,3,0]=5
##dT[1,2,3,1]=9
##dT[1,2,3,2]=13
##dT[1,2,3,3]=17
##dT[1,2,3,4]=21
##dT[1,2,3,5]=25
##
##dT[1,2,4,0]=4
##dT[1,2,4,1]=9
##dT[1,2,4,2]=14
##dT[1,2,4,3]=19
##dT[1,2,4,4]=24
##dT[1,2,4,5]=29

dT[2,3,1,0]=18
dT[2,3,1,1]=20
dT[2,3,1,2]=22
dT[2,3,1,3]=24
dT[2,3,1,4]=26
dT[2,3,1,5]=28

dT[2,3,2,0]=14
dT[2,3,2,1]=17
dT[2,3,2,2]=20
dT[2,3,2,3]=23
dT[2,3,2,4]=26
dT[2,3,2,5]=29

dT[2,3,3,0]=9
dT[2,3,3,1]=13
dT[2,3,3,2]=17
dT[2,3,3,3]=21
dT[2,3,3,4]=25
dT[2,3,3,5]=29

dT[2,3,4,0]=7
dT[2,3,4,1]=11
dT[2,3,4,2]=15
dT[2,3,4,3]=19
dT[2,3,4,4]=23
dT[2,3,4,5]=27

##arrive_time={}
##arrive_time[0]=5
##arrive_time[1]=7
##arrive_time[2]=11




##for row in customer:
##    print arrive_time[int(row[0])]


#print 'arrive_time',arrive_time
##for row in customer:
##    for i in node:
##        if i==2:
##            continue
##        else:
##            for k in modes:
##                for s in range(len(departure)):
##                    print 'k',k,'s',s,'dT',dT[i-1,i,k,s]
