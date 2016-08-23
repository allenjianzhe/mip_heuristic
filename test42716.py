##from myfile import title
##print title,'ty'

##
##import random
##print random.random()
##print random.choice([1,2,3,4])
##

##S='spam'
##
##print S[1:3]

##print '{:,.3f}'.format(296999.2567) #3f means leave 3 digit after '.'
##print '{:,.1f}'.format(296999.2567)

##L=[123,'spam',1.23]
##print L
##L.append('NI')
##print L
##L.pop(2)
##print L

M=[[1,2,3],[4,5,6],[7,8,9]]
##print M
##print M[1]
##print M[1][2]

##col2=[row[1] for row in M]
##print col2
##k=[row[1]for row in M if row[1]%2==0]
##print k

diag=[M[i][i]for i in [0,1,2]]
print diag
