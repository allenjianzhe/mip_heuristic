import csv 
import sys
import math
o=open(r'C:\Users\MacBook Air\Desktop\my research\cus_3.csv','r')#apple
#o=open(r'C:\Users\zjian\Desktop\my research\cus_3.csv','r')
reader=csv.reader(o)
o.seek(0)
customer=[]
for row in reader:
    customer.append(row)
o.close()
DD={}
for row in customer:
    DD[int(row[0])]=int(row[3])
    
nodes=[1,2,3,4]
modes=[1,2,3,4]
departure=[1,2,3,4,5,6]
