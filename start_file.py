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
                    arc_C[i,2,s]=500
                    arc_C[i,3,s]=400
                    arc_C[i,4,s]=100
    return arc_C
def getDistance():
    Distance  ={}
    Distance[1]=413
    Distance[2]=485
    Distance[3]=695
    Distance[4]=741
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
                    arc_trans_cost[int(row[0]),i,1]=300*int(row[2])*Distance[i]/1000.0
                    arc_trans_cost[int(row[0]),i,2]=500*int(row[2])*Distance[i]/1000.0
                    arc_trans_cost[int(row[0]),i,3]=1500*int(row[2])*Distance[i]/1000.0
                    arc_trans_cost[int(row[0]),i,4]=2000*int(row[2])*Distance[i]/1000.0
    return arc_trans_cost
def getdT():
    dT={}         
    dT[1,1,1]=1
    dT[1,1,2]=3
    dT[1,1,3]=5
    dT[1,1,4]=7
    dT[1,1,5]=9
    dT[1,1,6]=11

    dT[1,2,1]=1
    dT[1,2,2]=4
    dT[1,2,3]=7
    dT[1,2,4]=10
    dT[1,2,5]=13
    dT[1,2,6]=16

    dT[1,3,1]=1
    dT[1,3,2]=5
    dT[1,3,3]=9
    dT[1,3,4]=13
    dT[1,3,5]=17
    dT[1,3,6]=21

    dT[1,4,1]=1
    dT[1,4,2]=6
    dT[1,4,3]=11
    dT[1,4,4]=16
    dT[1,4,5]=21
    dT[1,4,6]=26

    dT[2,1,1]=9
    dT[2,1,2]=11
    dT[2,1,3]=13
    dT[2,1,4]=15
    dT[2,1,5]=17
    dT[2,1,6]=19

    dT[2,2,1]=7
    dT[2,2,2]=10
    dT[2,2,3]=13
    dT[2,2,4]=16
    dT[2,2,5]=19
    dT[2,2,6]=22

    dT[2,3,1]=5
    dT[2,3,2]=9
    dT[2,3,3]=13
    dT[2,3,4]=17
    dT[2,3,5]=21
    dT[2,3,6]=25

    dT[2,4,1]=4
    dT[2,4,2]=9
    dT[2,4,3]=14
    dT[2,4,4]=19
    dT[2,4,5]=24
    dT[2,4,6]=29

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
    return dT
o=open(r'C:\Users\MacBook Air\Desktop\my research\cus_3.csv','r')
reader= csv.reader(o)
o.seek(0)
customer=[]
DD={}
for row in reader:
    customer.append(row)
for row in customer:
    DD[int(row[0])]=int(row[3])

