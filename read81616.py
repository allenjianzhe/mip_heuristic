import networkx as nx 
import csv
import sys
import math
import numpy
import random
import pandas as pd
G = nx.DiGraph()
M = 1000000000
F = 1250
modes = [1, 2, 3, 4]
departure = [1,2]
G.add_nodes_from([1,2,3,4])
G.add_edges_from([(1,2),(2,3),(3,4)])
#define edge attributes
def getGdistance(G):	
	G[1][2]['distance'] = 400
	G[2][3]['distance'] = 500
	G[3][4]['distance'] = 700
def customer_shuffle(seed,customer):
    random.seed(seed)
    # d = pd.read_csv('C:\Users\MacBook Air\Desktop\my research\cus_5_13.csv')
    # customer = d.values.tolist()
    # print([c[2] for c in customer])
    weight = numpy.array([c[2] for c in customer])
    weight = 1.*weight/weight.sum()
    samples = numpy.random.choice(len(customer),size=len(customer),replace=False,p=weight)
    customer = [customer[i] for i in samples]
    return customer
def customer_bigtosmall(customer):
    # d = pd.read_csv('C:\Users\MacBook Air\Desktop\my research\cus_5_13.csv')
    # customer = d.values.tolist()
    customer = sorted(customer, key=lambda x: x[2], reverse=True) #big to small
    return customer
def customer_smalltobig(customer):
    # d = pd.read_csv('C:\Users\MacBook Air\Desktop\my research\cus_5_13.csv')
    # customer = d.values.tolist()
    customer = sorted(customer, key=lambda x: x[2]) #small to big
    return customer
def customer_DpDD(customer):
    # d = pd.read_csv('C:\Users\MacBook Air\Desktop\my research\cus_30_8.csv')
    # customer = d.values.tolist()
    customer = sorted(customer, key=lambda x: float(x[2]*x[4]/x[3]),reverse = True)# big to small
    return customer
def customer_DpDDshuffle(seed,customer):
    random.seed(seed)
    weight = numpy.array([c[2]*c[4]/c[3] for c in customer])
    weight = 1.*weight/weight.sum()
    samples = numpy.random.choice(len(customer),size=len(customer),replace=False,p=weight)
    customer = [customer[i] for i in samples]
    return customer
fix_C = 1000
def getGC(G,fix_C):
	for (u,v) in G.edges():
		for k in modes:
			for s in departure:
				G[u][v]['C',k,s] = fix_C
def getGtau(G):
	for (u,v) in G.edges():
		for k in modes:
			if k == 1:
				G[u][v]['tau',k] = round (G[u][v]['distance']/60.0)
			if k == 2:
				G[u][v]['tau',k] = round (G[u][v]['distance']/100.0)
			if k == 3:
				G[u][v]['tau',k] = round (G[u][v]['distance']/250.0)
			if k == 4:
				G[u][v]['tau',k] = round (G[u][v]['distance']/500.0)
def getGf(G):
	unit = 1000.0
	for (u,v) in G.edges():
		for k in modes:
			if k == 1:
				G[u][v]['f',k] = int(300 * G[u][v]['distance']/ unit)
			if k == 2:
				G[u][v]['f',k] = int(500 * G[u][v]['distance']/ unit)
			if k == 3:
				G[u][v]['f',k] = int(1500 * G[u][v]['distance']/ unit)
			if k == 4:
				G[u][v]['f',k] = int(2000 * G[u][v]['distance']/ unit)
def getGST(G):
	for (u,v) in G.edges():
		G[u][v]['ST'] = 1
def getGdT(G):
	G[1][2]['dT',1,1] = 1
	G[1][2]['dT',1,2] = 2
	G[1][2]['dT',2,1] = 1
	G[1][2]['dT',2,2] = 2
	G[1][2]['dT',3,1] = 1
	G[1][2]['dT',3,2] = 3
	G[1][2]['dT',4,1] = 1
	G[1][2]['dT',4,2] = 3

	G[2][3]['dT',1,1] = 9
	G[2][3]['dT',1,2] = 10
	G[2][3]['dT',2,1] = 9
	G[2][3]['dT',2,2] = 10
	G[2][3]['dT',3,1] = 5
	G[2][3]['dT',3,2] = 7
	G[2][3]['dT',4,1] = 4
	G[2][3]['dT',4,2] = 6

	G[3][4]['dT',1,1] = 18
	G[3][4]['dT',1,2] = 20
	G[3][4]['dT',2,1] = 15
	G[3][4]['dT',2,2] = 20
	G[3][4]['dT',3,1] = 9
	G[3][4]['dT',3,2] = 11
	G[3][4]['dT',4,1] = 8
	G[3][4]['dT',4,2] = 10
ending_time = {}
customer = []
d = pd.read_csv('C:\Users\MacBook Air\Desktop\my research\cus_5_13.csv')
# d = pd.read_csv('C:\Users\MacBook Air\Desktop\my research\cus_50_21.csv',header=None)
customer = d.values.tolist()
# customer = customer_shuffle(5,customer)
customer = customer_bigtosmall(customer)
# customer = customer_smalltobig(customer)
# customer = customer_DpDD(customer)
# customer = customer_DpDDshuffle(6,customer)
#Distance: each arc distance
# G[u][v]['distance'] = {}
getGdistance(G)
#CAPACITY
getGC(G,fix_C)
#tau: each mode at each arc transportation time
getGtau(G)
#f: unit cost of mode at each arc
getGf(G)
# time of 3PL
getGST(G)
#dT: departure time at each arc
getGdT(G)