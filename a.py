

#python a.py --file=abc --drift=3
#python a.py -f abc -d 3
from optparse import OptionParser
#定义一个OptionParser对象
parser = OptionParser()
#添加参数选项
#-f是命令行选项的简写，可以在命令行使用-f abc传递参数
#--file是命令行选项的全称，可以在命令行使用--file=abc传递参数
#help是现实帮助信息，执行python a.py --help的时候会显示
#type是指定传递变量的类型
parser.add_option("-f", "--file", dest="filename",
                  help="the file to read", type="string")
parser.add_option("-d", "--drift", dest="verbose", default=0,
                  help="drift", type='int')

(options, args) = parser.parse_args()
print options
print args
#我只写了一个再read052815_2中的函数函数
#原则上只能在主程序中可以定义变量，运行代码
#其它文件只能定义函数
#这个函数应该import到主文件中
#nodes, modes, departure也在主文件中定义
#然后通过调用getArcC获取arc_C的值
def getArcC(nodes, modes, departure):
    arc_C={}
    for i in nodes:
        if i != 3:
            for k in modes:
                for s in departure:
                    arc_C[i,1,s]=300
                    arc_C[i,2,s]=500
                    arc_C[i,3,s]=400
                    arc_C[i,4,s]=100
    return arc_C