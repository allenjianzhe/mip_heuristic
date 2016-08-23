import time #µº»Î time¿‡
start=time.clock()
def func(a,b):
    while True:
        end=time.clock ()
        if  int(end-start)==10:
            print('Warning: Timeout!!'*5)
            break
        a=a+b

    print a
func(1,2)
