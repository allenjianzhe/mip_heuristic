# file name read72916
import csv
import sys
import math
import numpy
import random
import pandas as pd
# from createdata73116 import *


# def generate_cutomer_data(size_of_customer):
#     from random import randint as uniform_dist
#     data = pd.DataFrame(
#         columns=['Customer_Id', 'Final_Destination', 'Demand', 'Due_Date', 'Penalty'])
#     for i in range(size_of_customer):
#         data.loc[i] = [i, 'SS', uniform_dist(50, 250), uniform_dist(6, 35), 50]
#     return data
# size_of_customer = 10
# d = generate_cutomer_data(size_of_customer)
# d.to_csv('C:\Users\MacBook Air\Desktop\my research\cus_10_7.csv',
# index=False)
#d = pd.read_csv('C:\Users\MacBook Air\Desktop\my research\cus_5_13.csv')
# customer=[]
# for i,row in d.iterrows():
#    customer.append(row.tolist())
#customer = d.values.tolist()
#customer = sorted(customer, key=lambda x: x[2], reverse=True) #big to small
#customer = sorted(customer, key=lambda x: x[2]) # small to big
#random.shuffle(customer) # make customer random order sequance
#print customer,'test'
M = 1000000000
F = 1250
# set of routes
nodes = [1, 2, 3, 4]
# each plan has two departure time
departure = [1, 2]
# modes = ['T','R','H','A']
modes = [1, 2, 3, 4]

def customers_shuffle(seed):
    random.seed(seed)
    d = pd.read_csv('C:\Users\MacBook Air\Desktop\my research\cus_5_13.csv')
    # customer=[]
    # for i,row in d.iterrows():
    #    customer.append(row.tolist())
    customer = d.values.tolist()
    customer = sorted(customer, key=lambda x: x[2], reverse=True) #big to small
    # customer = sorted(customer, key=lambda x: x[2]) # small to big
    #start weighted sampling
    weight = numpy.array([c[2] for c in customer])
    weight = 1.*weight/weight.sum()
    samples = numpy.random.choice(len(customer),size=len(customer),replace=False,p=weight)
    customer = [customer[i] for i in samples]
    # numpy.random.choice(customer,size=None,replace=True,p=None)
    # customer = random.shuffle(customer) # make customer random order sequance
    return customer
def customer_bigtosmall():
    d = pd.read_csv('C:\Users\MacBook Air\Desktop\my research\cus_5_13.csv')
    customer = d.values.tolist()
    customer = sorted(customer, key=lambda x: x[2], reverse=True) #big to small
    return customer
def customer_smalltobig():
    d = pd.read_csv('C:\Users\MacBook Air\Desktop\my research\cus_5_13.csv')
    customer = d.values.tolist()
    customer = sorted(customer, key=lambda x: x[2]) #small to big
    return customer
def customer_order():
    d = pd.read_csv('C:\Users\MacBook Air\Desktop\my research\cus_30_8.csv')
    customer = d.values.tolist()
    customer = sorted(customer, key=lambda x: float(x[2]*x[4]/x[3]),reverse = True)# big to small
    return customer

def getC(nodes, modes, departure):
    C = {}
    fix_C = 1000
    for n in nodes:
        if n != 4:
            for k in modes:
                for s in departure:
                    C[n, k, s] = fix_C
    return C, fix_C




def getDistance():#edge parameter
    Distance = {}
    Distance[1] = 400
    Distance[2] = 500
    Distance[3] = 700
    Distance[4] = 800
    return Distance


def getTau(nodes, modes, Distance):#once we know distance, then we know tau
    tau = {}
    for n in nodes:
        if n == 4:
            continue
        else:
            for k in modes:
                tau[n, 1] = round(Distance[n] / 60.0)
                tau[n, 2] = round(Distance[n] / 100.0)
                tau[n, 3] = round(Distance[n] / 250.0)
                tau[n, 4] = round(Distance[n] / 500.0)
    return tau


def getf(nodes, modes, Distance):  # once we know distance, then we know f
    f = {}
    unit = 1000.0
    for n in nodes:
        if n == 4:
            continue
        else:
            for k in modes:
                f[n, 1] = int(300 * Distance[n] / unit)
                f[n, 2] = int(500 * Distance[n] / unit)
                f[n, 3] = int(1500 * Distance[n] / unit)
                f[n, 4] = int(2000 * Distance[n] / unit)
    return f


def getST(nodes):
    ST = {}  # shipping time of route n if 3PL is used, here all make ==1
    for n in nodes:
        if n == 4:
            continue
        else:
            ST[n] = 1
    return ST
# first dT, using distance 1=400


def getdT():# edge parameter
    dT = {}
    dT[1, 1, 1] = 1
    dT[1, 1, 2] = 2

    dT[1, 2, 1] = 1
    dT[1, 2, 2] = 2

    dT[1, 3, 1] = 1
    dT[1, 3, 2] = 3

    dT[1, 4, 1] = 1
    dT[1, 4, 2] = 3

    dT[2, 1, 1] = 9
    dT[2, 1, 2] = 10

    dT[2, 2, 1] = 9
    dT[2, 2, 2] = 10

    dT[2, 3, 1] = 5
    dT[2, 3, 2] = 7

    dT[2, 4, 1] = 4
    dT[2, 4, 2] = 6

    dT[3, 1, 1] = 18
    dT[3, 1, 2] = 20

    dT[3, 2, 1] = 15
    dT[3, 2, 2] = 20

    dT[3, 3, 1] = 9
    dT[3, 3, 2] = 11

    dT[3, 4, 1] = 8
    dT[3, 4, 2] = 10
    return dT
