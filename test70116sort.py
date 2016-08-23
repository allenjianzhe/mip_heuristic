#test sort
import sys

D={'d':1,'c':2,'b':3,'a':4}
print D
K=list(D.keys())
print K
K.sort()
print K

for key in K:
    print (key,'=>',D[key])

L=list(D.values())
print L
