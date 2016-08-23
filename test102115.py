#test matrix
import math
import numpy as np
#a=np.mat([[1,2,3],[4,5,6]])
#print a
#print a.shape
#c=5
##b=np.mat([[1,2,3],[4,5,6]])
##print c*a
##print b+c*a
##
##count = 1
##a = []
##for i in range(0, 3):
##    tmp = []
##    for j in range(0, 3):
##        tmp.append(count)
##        count += 1
##    a.append(tmp)
##print a

#a=[ [[[0] for row1 in range(6)] for row2 in range(4)] for row3 in range(4)]

##b=[1,2,3]
##bb=[row-2 for row in b]
##cc=[row*2 for row in b]
##print bb,cc

a=[ [[[0] for row1 in range(3)] for row2 in range(2)]]
b=[[1,2,3],[4,5,6]]
print a+b
