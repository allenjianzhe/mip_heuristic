#test all
import sys
a=[-1,-2,-3,-5,6]
if  all(k<0 for k in a)==True:
    print 'that is right'
else:
    print 'no '
##    print 'true'
##else:
##    print 'false'
