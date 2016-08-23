#BASED on read102715, but change the cost unit. 
#-*- coding: utf-8 -*-
import csv 
import sys
import math


def getArcC(nodes, modes, departure):
    arc_C={}
    for i in nodes:
        if i != 4:
            for k in modes:
                for s in departure:
                    arc_C[i,1,s]=300
                    arc_C[i,2,s]=300
                    arc_C[i,3,s]=300
                    arc_C[i,4,s]=300
    return arc_C
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
def getTransTime(nodes,modes,Distance):
    trans_time={}
    for i in nodes:
            if i==4:
                continue
            else:
                for k in modes:
                    trans_time[i,1]=round(Distance[i]/60.0)
                    trans_time[i,2]=round(Distance[i]/100.0)
                    trans_time[i,3]=round(Distance[i]/250.0)
                    trans_time[i,4]=round(Distance[i]/500.0)
    return trans_time
def getArcTransCost(customer,nodes,modes,Distance):
    arc_trans_cost={}
    for row in customer:
        for i in nodes:
            if i==4:
                continue
            else:
                for k in modes:
                    arc_trans_cost[int(row[0]),i,1]=0.3*int(row[2])*Distance[i]/1000.0
                    arc_trans_cost[int(row[0]),i,2]=0.5*int(row[2])*Distance[i]/1000.0
                    arc_trans_cost[int(row[0]),i,3]=1.5*int(row[2])*Distance[i]/1000.0
                    arc_trans_cost[int(row[0]),i,4]=2.0*int(row[2])*Distance[i]/1000.0
    return arc_trans_cost
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
def getST(nodes):#update20160524
    ST={}#shipping time of route n if 3PL is used, here all make ==1  ,新加的20160521
    for i in nodes:
        if i==4:
            continue
        else:
            ST[i]=1
    return ST    		
o=open(r'C:\Users\MacBook Air\Desktop\my research\cus_5.csv','r')
reader= csv.reader(o)
o.seek(0)
customer=[]
DD={}
for row in reader:
    customer.append(row)
for row in customer:
    DD[int(row[0])]=int(row[3])

customer = sorted(customer,key=lambda x:x[2],reverse=True)#排序问题

                
