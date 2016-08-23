Z_list=[]

while:
    get Z
    if len(Z_list)==5:
        if Z<min(Z_list):
            Z_list=[]
            Z_list.append(Z)
        else:
            lamda=lamda/2
            Z_list=[]
            Z_list.append(Z)
    else:
        Z_list.append(Z)
