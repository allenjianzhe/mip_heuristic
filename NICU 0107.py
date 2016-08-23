# 0107 NICU problem
import random

import math
pre_roundTime_list=[]
def Prerounding(N):
    A=random.randint(60*N-120,60*N+120)# Assume average time for one baby is 120
    B=random.randint(30,90)
    C0=random.randint(10,60)

##    N=10 # number of patient 这个是核心的variable

##    preround_decision=1 # preround decision, yes or no

##    delete_order_probablity=0.7#random.random() # need to delete old orders 这个其实意义不大，？ 需要吗

    C1_list=[]
    C2_list=[]
    D_list=[]
    F_list=[]
    H_list=[]
    I_list=[]
    J_list=[]
    G_list=[]
    Neo_preroundTime_temple=0
    Neo_preroundTime=0
    Neo_preroundTime_temple_list=[]

    RA1_preroundTime_temple=0
    RA1_preroundTime=0
    RA1_preroundTime_temple_list=[]

    RA2_preroundTime_temple=0
    RA2_preroundTime=0
    RA2_preroundTime_temple_list=[]

    

    Total_TeamTime_pre=0
    # 2 RA 的结构 #BIGGEST difference 是preround可以给2个RA节省检查的时间
    #assume rounding的时候，他们总是一起的，所以应该是他们三人最大的时间为他们每个人的时间！
    #Assume 只有Neo做prerounding.
    #prerounding, 对Neo来说time 分为第一部分是A+B+C0， 第二部分是prerounding, C1+C1+D(for), 第三部分是rounding, H,实际时间是pre_roundTime=max(F+H+I,G+H)
    #this for prerounding, Neo the sequence is A,B,C0,C1,C2,D,H
    #prerounding, 对RA1来说time 分为第一部分是rounding, F+H+G+I
    #this for prerounding, RA1 the sequence is F,H,G,I(for)
    #prerounding, 对RA2来说time分为第一部分是rounding, G+H,实际时间是pre_roundTime
    #this for prerounding, RA2 the sequence is H+J(for)
    #所以，rounding部分的时间是max(F+H+G+I,H+J),为他们三人的pre_roundTime

    #rounding, 对Neo来说time分为第一部分是A+B+C0,第二部分是rounding,E1+E2+E3+H(for)
    #for rounding without prerounding,  Neo is A,B,C0,E1,E2,E3,H
    #rounding, 对RA1来说time分为第一部分是rounding,E1+E2+E3+F+H+I+J
    #for rounding without prerounding,  RA1 is E1,E2,E3,F,H,G,I(for)
    #rounding, 对RA2来说time分为第一部分是rounding,E1+E2+E3+H+J
    #for rounding without prerounding,  RA2 is E1,E2,E3,H,J（for）

    for n in range(0,N):    
        C1=random.randint(30,90)
        C1_list.append(C1)
        C2=random.randint(180,420)
        C2_list.append(C2)
        D=random.randint(90,150)
        D_list.append(D)
        
        F=random.randint(90,120)
        F_list.append(F)
        H=random.randint(90,150)
        H_list.append(H)
        I=random.randint(120,360)
        I_list.append(I)
        
        G=random.randint(150,210)
        G_list.append(G)

        J=random.randint(60,720)

        pre_roundTime=max(F+H+I+G,H+J) #三人里面最长的时间为准
        
        Neo_preroundTime_temple=C1+C2+D+pre_roundTime
        Neo_preroundTime_temple_list.append(Neo_preroundTime_temple)
        Neo_preroundTime+=Neo_preroundTime_temple
        
        RA1_preroundTime_temple=pre_roundTime
        RA1_preroundTime_temple_list.append(RA1_preroundTime_temple)
        RA1_preroundTime+=RA1_preroundTime_temple
        
        RA2_preroundTime_temple=pre_roundTime
        RA2_preroundTime_temple_list.append(RA2_preroundTime_temple)
        RA2_preroundTime+=RA2_preroundTime_temple

        pre_roundTime_list.append(pre_roundTime)
        
    

       
    Neo_preroundTime=Neo_preroundTime+A+B+C0 #Renew Neo, add A,B,C0 to Neo time
    Total_TeamTime_pre=Neo_preroundTime+RA1_preroundTime+RA2_preroundTime
    return (Neo_preroundTime,RA1_preroundTime,RA2_preroundTime,Total_TeamTime_pre)

##    print "######################################################"
##    print 'preround time schedule'
##    print 'Neo_preroundTime',Neo_preroundTime
##    print "RA1_preroundTime",RA1_preroundTime
##    print 'RA2_preroundTime',RA2_preroundTime
##    print 'Total_TeamTime',Total_TeamTime
##    print 'C1_list',C1_list
##    print 'C2_list',C2_list
##    print 'D_list',D_list
##    print 'F_list',F_list
##    print 'H_list',H_list
##    print 'I_list',I_list
##    print 'J_list',J_list
##    print 'G_list',G_list
##    print 'Neo_preroundTime_list',Neo_preroundTime_list
##    print 'RA1_preroundTime_list',RA1_preroundTime_list
##    print 'RA2_preroundTime_list',RA2_preroundTime_list
##    print "######################################################"

Prerounding(N=10)
print 'pre_roundTime_list',pre_roundTime_list
repeat=2
Final_Neo_pre_list=[]
Final_RA1_pre_list=[]
Final_RA2_pre_list=[]
Final_Time_pre_list=[]
for i in range(0,repeat):
    x,y,z,t=Prerounding(N=10)
    Final_Neo_pre_list.append(x)
    Final_RA1_pre_list.append(y)
    Final_RA2_pre_list.append(z)
    Final_Time_pre_list.append(t)
    
print 'Monte carlo simulation','repeat times: ',repeat
print 'Total_Neo with prerounding',(sum(Final_Neo_pre_list)/len(Final_Neo_pre_list))
print 'Total_RA1 with prerounding',(sum(Final_RA1_pre_list)/len(Final_RA1_pre_list))
print 'Total_RA2 with prerounding',(sum(Final_RA2_pre_list)/len(Final_RA2_pre_list))
print 'Total_TeamTime with prerounding',(sum(Final_Time_pre_list)/len(Final_Time_pre_list))
##print 'Total_TeamTime_list',Total_TeamTime_list

#Preround(10)

########################################################################################################################
##def Rounding(N):
##    A=random.randint(350,450)
##    B=random.randint(5,15)
##    C0=random.randint(10,30)
##    E1_list=[]
##    E2_list=[]
##    E3_list=[]
##    F_list=[]
##    H_list=[]
##    I_list=[]
##    G_list=[]
##    Neo_roundTime_temple=0
##    Neo_roundTime=0
##    Neo_roundTime_temple_list=[]
##
##    RA1_roundTime_temple=0
##    RA1_roundTime=0
##    RA1_roundTime_temple_list=[]
##
##    RA2_roundTime_temple=0
##    RA2_roundTime=0
##    RA2_roundTime_temple_list=[]
##
##    Total_TeamTime_round=0
##    for n in range(0,N):        
##        E1=random.randint(20,40)
##        E1_list.append(E1)
##        E2=random.randint(100,200)
##        E2_list.append(E2)
##        E3=random.randint(10,30)
##        E3_list.append(E3)
##        F=random.randint(30,90)
##        F_list.append(F)
##        H=random.randint(60,180)
##        H_list.append(H)
##        I=random.randint(100,300)
##        I_list.append(I)
##        
##        G=random.randint(60,120)
##        G_list.append(G)
##        
##        Neo_roundTime_temple=E1+E2+E3+H
##        Neo_roundTime_temple_list.append(Neo_roundTime_temple)
##        Neo_roundTime+=Neo_roundTime_temple
##        
##        RA1_roundTime_temple=E1+E2+E3+F+H+I
##        RA1_roundTime_temple_list.append(RA1_roundTime_temple)
##        RA1_roundTime+=RA1_roundTime_temple
##        
##        RA2_roundTime_temple=E1+E2+E3+G+H
##        RA2_roundTime_temple_list.append(RA2_roundTime_temple)
##        RA2_roundTime+=RA2_roundTime_temple
##        
##    J=random.randint(250,550)
##
##    RA1_roundTime=RA1_roundTime+J # Renew RA1, add J to RA1    
##    Neo_roundTime=Neo_roundTime+A+B+C0 #Renew Neo, add A,B,C0 to Neo time
##    Total_TeamTime_round=Neo_roundTime+RA1_roundTime+RA2_roundTime
##    
####    print "######################################################"
####    print 'Round time schedule'
####    print 'Neo_preroundTime',Neo_preroundTime
####    print "RA1_preroundTime",RA1_preroundTime
####    print 'RA2_preroundTime',RA2_preroundTime
####    print 'Total_TeamTime',Total_TeamTime
##    
##    return Total_TeamTime_round
####    print 'C1_list',E1_list
####    print 'C2_list',E2_list
####    print 'D_list',E3_list
####    print 'F_list',F_list
####    print 'H_list',H_list
####    print 'I_list',I_list
####    print 'G_list',G_list
####    print 'Neo_preroundTime_list',Neo_preroundTime_list
####    print 'RA1_preroundTime_list',RA1_preroundTime_list
####    print 'RA2_preroundTime_list',RA2_preroundTime_list
####    print "######################################################"
##
##
##Rounding(N=10)
##repeat=100
##Total_TeamTime_round_list=[]
##for i in range(0,repeat):    
##    Total_TeamTime_round_list.append(Rounding(N=10))
##print 'Monte carlo simulation','Total_TeamTime without prerounding',(sum(Total_TeamTime_round_list)/len(Total_TeamTime_round_list))
####print 'Total_TeamTime_list',Total_TeamTime_list

