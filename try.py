example=[]

a=[]
r1=1
r2=2

c1=3
c2=4

a.append(r1)
a.append(r2)

example.append(a)


a=[]
a.append(c1)
a.append(c2)
example.append(a)


print example

for (c,d) in example:
    print c,d
