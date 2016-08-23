#----------------------------------------------------------------------------
#        HYDRO ENERGY SUPPLY CHAIN
#----------------------------------------------------------------------------
#   Objective: MAXimizing GDP from Power/Water supplies and prevention from flood for 20 PERIODS in Pakistan.
#   Last updated: March 29, 2015
#----------------------------------------------------------------------------
#    UNITS:
#    money: $ mil
#    water: bil. cubic meter
#    time: half year
#    power: MWh
#    distance: 100 miles
#----------------------------------------------------------------------------

# Call Library
import sys
import xlrd

sys.path.append('C:/gurobi604/win32/python27/lib/gurobipy')

from gurobipy import *

#   Modeling start
#   Create a model
try:
    model = Model("Hydro_Based Energy Supply Chain")

######################################
#   open InputData
######################################
    from xlrd import open_workbook,cellname

    inputdata = open_workbook('InputData_current.xls')
    player = inputdata.sheet_by_name("Index")
    rainfall = inputdata.sheet_by_name("Dam_external_jt")
    variable_cost = inputdata.sheet_by_name("Op_cost_j")
    p_capacity = inputdata.sheet_by_name("Dam_Power_Capacity_j")
    convert = inputdata.sheet_by_name("Dam_Conversion_Ratio_j")
    w_capacity = inputdata.sheet_by_name("Dam_Storage_Capacity_j")
    p_yield = inputdata.sheet_by_name("Trans_yield_jk")
    w_yield = inputdata.sheet_by_name("water_dist_yield_jn")
    outlimit = inputdata.sheet_by_name("water_limit_jn")
    p_shortage = inputdata.sheet_by_name("Electricity_Demand_kt")
    w_shortage = inputdata.sheet_by_name("Farm_Demand_nt")
    f_tolerance = inputdata.sheet_by_name("Tolerance_j")
    impact = inputdata.sheet_by_name("Beta_t")
    RATION = inputdata.sheet_by_name("RA_t")

#######################################
#   Definition of Index
#######################################
    SOURCE = int(player.cell_value(rowx=1, colx=1))
    DEMANDZONE = int(player.cell_value(rowx=1, colx=2))
    FARM = int(player.cell_value(rowx=1, colx=3))
    PERIODS = int(player.cell_value(rowx=1, colx=4))
    percentage = int(player.cell_value(rowx=1, colx=5))

#    print SOURCE
#    print DEMANDZONE
#    print PERIODS
#######################################
#   Definition of Variables
#######################################
#type of variables: GRB.CONTINUOUS, GRB.BINARY, GRB.INTEGER
#addVar ( lb=0.0, ub=GRB.INFINITY, obj=0.0, vtype=GRB.CONTINUOUS, name='''', column=None ) 
################ Decision Variables ######################
      
#o[j][t]: How much water to release from j In period t.
#A Decision Variable 
#A Continuous Variable
    o = []
    for j in range(SOURCE):
        o.append([])
        for t in range(PERIODS):
            o[j].append(model.addVar(vtype=GRB.CONTINUOUS, name="o_%s,%s" % (j,t)))

#u[j][k][t]: The Quantity Of water supplied From A Source j To A FARM Location k In period t.
#A Decision Variable
#A Continuous Variable.
    u = []
    for j in range(SOURCE):
        u.append([])
        for n in range(FARM):
            u[j].append([])
            for t in range(PERIODS):
                u[j][n].append(model.addVar(vtype=GRB.CONTINUOUS, name="u_%s,%s,%s" % (j,n,t)))

#s[j][t]: How much water to be store at j In period t.
#A Decision Variable
#A Continuous Variable
    s = []
    for j in range(SOURCE):
        s.append([])
        for t in range(PERIODS):
            s[j].append(model.addVar(vtype=GRB.CONTINUOUS, name="s_%s,%s" % (j,t)))

#e[j][t]: The Total Amount Of Electricity Generated At j In period t.
#A Continuous Variable
#A Decision Variable
    e = []
    for j in range(SOURCE):
        e.append([])
        for t in range(PERIODS):
            e[j].append(model.addVar(vtype=GRB.CONTINUOUS, name="e_%s%s" % (j,t)))

#p[j][k][t]: The Total Amount Of Electricity Supplied From j to k in period t
#To A Demand Zone k In Year t.
#A Continuous Variable.
#A Decision Variable
    p = []
    for j in range(SOURCE):
        p.append([])
        for k in range(DEMANDZONE):
            p[k].append([])
            for t in range(PERIODS):
                p[j][k].append(model.addVar(vtype=GRB.CONTINUOUS, name="p_%s,%s,%s" % (j,k,t)))

#f[j][t]: The Total Amount Of water flooded above MT At j In period t.
#A Continuous Variable
#A Decision Variable
    f = []
    for j in range(SOURCE):
        f.append([])
        for t in range(PERIODS):
            f[j].append(model.addVar(vtype=GRB.CONTINUOUS, name="f_%s%s" % (j,t)))


################ Other Variables #####################
#q[j][t]: flow Of water into j In period t.
#A Continuous Variable
    q = []
    for j in range(SOURCE):
        q.append([])
        for t in range(PERIODS):
            q[j].append(model.addVar(vtype=GRB.CONTINUOUS, name="q_%s%s" % (j,t)))
#b_HPP2[t]: The Budget For OPERATION In period t.
#A Continuous Variable
    b_HPP2 = {}
    for t in range(PERIODS):
        b_HPP2[t] = model.addVar(vtype=GRB.CONTINUOUS, name='b_HPP2_%s' % (t))
#g[t]: GDP In Year t
    g = {}
    for t in range(PERIODS):
        g[t] = model.addVar(vtype=GRB.CONTINUOUS, name='g_%s' % (t))
###############FOR TEST: START ######################
##total_cost[t]: Yearly investment
#    total_cost = {}
#    for t in range(PERIODS):
#        total_cost[t] = model.addVar(vtype=GRB.CONTINUOUS, name='total_cost_%s' % (t))
##periodical_power_gap[t]
#    periodical_power_gap = {}
#    for t in range(PERIODS):
#        periodical_power_gap[t] = model.addVar(vtype=GRB.CONTINUOUS, name='periodical_power_gap_%s' % (t)) 
##periodical_water_gap[t]
#    periodical_water_gap = {}
#    for t in range(PERIODS):
#        periodical_water_gap[t] = model.addVar(vtype=GRB.CONTINUOUS, name='periodical_water_gap_%s' % (t)) 
###############FOR TEST: END ######################

#######################################
#   Parameter Setting
#######################################
#A[J][t]: RAINFALL at 'J' IN PERIOD T
    RAIN = []
    for j in range(SOURCE):
        RAIN.append([])
        for t in range(PERIODS):
            RAIN[j].append(rainfall.cell_value(rowx=j+1,colx=t+1))

#OC[j]: operations cost of 'j'
    OC = variable_cost.row_values(1)

#PC[j]: installed capacity of 'j'
    PC = p_capacity.row_values(1)

#CR[j]: conversion ratio of 'j'
    CR = convert.row_values(1)

#STORAGE[j]: water storage capacity of 'j'
    STORAGE = w_capacity.row_values(1)
#PY[j][k]: power yield between 'j' and 'k'
    PY = []
    for j in range(SOURCE):
        PY.append([])
        for k in range(DEMANDZONE):
            PY[j].append(p_yield.cell_value(rowx=j+1,colx=k+1))
#WY[j][n]: water yield between 'j' and 'n'
    WY = []
    for j in range(SOURCE):
        WY.append([])
        for n in range(FARM):
            WY[j].append(w_yield.cell_value(rowx=j+1,colx=n+1))
#WL[j][n]: LIMIT OF WATER USAGE between 'j' and 'n'
    WL = []
    for j in range(SOURCE):
        WL.append([])
        for n in range(DEMANDZONE):
            WL[j].append(p_yield.cell_value(rowx=j+1,colx=n+1))
    
#GAP1[k][t]: The Energy Gap AT 'K'
    GAP1 = []
    for k in range(DEMANDZONE):
        GAP1.append([])
        for t in range(PERIODS):
            GAP1[k].append(p_shortage.cell_value(rowx=k+1,colx=t+1))

#GAP2[n][t]: The Water Gap AT 'n'
    GAP2 = []
    for n in range(FARM):
        GAP2.append([])
        for t in range(PERIODS):
            GAP2[n].append(w_shortage.cell_value(rowx=n+1,colx=t+1))


#MT[j]: water storage capacity of 'j'
    MT = f_tolerance.row_values(1)

#RA[t]: Ration in period t
    RA = RATION.row_values(1)

#BETA[t]: Beta_t
    BETA = impact.row_values(1)
#    for t in range(PERIODS):
#        print "BETA[",t,"]=", BETA[t]

#DISTANCE1[j][k]: Distance between 'j' and 'k'
#    DISTANCE1 = []
#    for j in range(SOURCE):
#        DISTANCE1.append([])
#        for k in range(DEMANDZONE):
#            DISTANCE1[j].append(DIST1.cell_value(rowx=j+1,colx=k+1))

#DISTANCE1[j][k]: Distance between 'j' and 'k'
#    DISTANCE2 = []
#    for j in range(SOURCE):
#        DISTANCE2.append([])
#        for n in range(FARM):
#            DISTANCE2[j].append(DIST2.cell_value(rowx=j+1,colx=n+1))

#Other Parameters: a bigM
    bigM = 20000000000000.0
    
############################################################################
#### Constraints
############################################################################

#Scascading model constraints
# QUANTITY BALANCE (x_jj' NOT USED) Constraint #1   ##############################################
    for j in range(0,1):
        for t in range(0,PERIODS):
            model.addConstr(q[j][t] == (RAIN[j][t] + o[j+15][t]))

    for j in range(1,2):
        for t in range(0,PERIODS):
            model.addConstr(q[j][t] == RAIN[j][t])

    for j in range(2,3):
        for t in range(0,PERIODS):
            model.addConstr(q[j][t] == (RAIN[j][t] + o[j+1][t]))

    for j in range(3,4):
        for t in range(0,PERIODS):
            model.addConstr(q[j][t] == (RAIN[j][t] + o[j+7][t]))

    for j in range(4,5):
        for t in range(0,PERIODS):
            model.addConstr(q[j][t] == (RAIN[j][t] + o[j+5][t]))

    for j in range(5,6):
        for t in range(0,PERIODS):
            model.addConstr(q[j][t] == (RAIN[j][t] + o[j-5][t] + o[j-4][t] + o[j+6][t]))

    for j in range(6,7):
        for t in range(0,PERIODS):
            model.addConstr(q[j][t] == (RAIN[j][t] + o[j-1][t]))

    for j in range(7,8):
        for t in range(0,PERIODS):
            model.addConstr(q[j][t] == (RAIN[j][t] + o[j-4][t]))

    for j in range(8,9):
        for t in range(0,PERIODS):
            model.addConstr(q[j][t] == (RAIN[j][t] + o[j-1][t]))

    for j in range(9,10):
        for t in range(0,PERIODS):
            model.addConstr(q[j][t] == RAIN[j][t])

    for j in range(10,11):
        for t in range(0,PERIODS):
            model.addConstr(q[j][t] == RAIN[j][t])

    for j in range(11,12):
        for t in range(0,PERIODS):
            model.addConstr(q[j][t] == (RAIN[j][t] + o[j-9][t]))

    for j in range(12,13):
        for t in range(0,PERIODS):
            model.addConstr(q[j][t] == (RAIN[j][t] + o[j+4][t]))

    for j in range(13,14):
        for t in range(0,PERIODS):
            model.addConstr(q[j][t] == (RAIN[j][t] + o[j-1][t]))

    for j in range(14,15):
        for t in range(0,PERIODS):
            model.addConstr(q[j][t] == RAIN[j][t])

    for j in range(15,16):
        for t in range(0,PERIODS):
            model.addConstr(q[j][t] == (RAIN[j][t] + o[j-2][t] + o[j-1][t]))

    for j in range(16,SOURCE):
        for t in range(0,PERIODS):
            model.addConstr(q[j][t] == RAIN[j][t])

###################### Constraint #1 ###########################################
########################cONSTRAINT 2###################################
    for j in range(0,SOURCE):
        for t in range(0,1):
            model.addConstr(s[j][t] == 0.80*(q[j][t] - o[j][t] - quicksum(u[j][n][t] for n in range(0,FARM))))

    for j in range(0,SOURCE):
        for t in range(1,PERIODS):
            model.addConstr(s[j][t] == 0.80*(s[j][t-1] + q[j][t] - o[j][t] - quicksum(u[j][n][t] for n in range(0,FARM))))
########################cONSTRAINT 2###################################
    for j in range(0,SOURCE):
        for t in range(0,PERIODS):
            model.addConstr(s[j][t] + quicksum(u[j][n][t] for n in range(0,FARM)) <= bigM)

    for j in range(0,SOURCE):
        for t in range(0,PERIODS):
            model.addConstr(s[j][t] <= STORAGE[j])

#Hydropower plant constraints
    for t in range(0,PERIODS):
        model.addConstr(b_HPP2[t] == quicksum(OC[j] for j in range(0,SOURCE)))

#Water supply constraint
    for n in range(0,FARM):
        for t in range(0,PERIODS):
            model.addConstr(quicksum(WY[j][n]*u[j][n][t] for j in range(0,SOURCE)) <= GAP2[n][t])

    for j in range(SOURCE):
        for n in range(FARM):
            for t in range(PERIODS):
                model.addConstr(u[j][n][t] <= bigM*(1-WL[j][n]))

    for j in range(0,SOURCE):
        for t in range(0,PERIODS):
            model.addConstr(quicksum(u[j][n][t] for n in range(0,FARM)) <= 0.45*q[j][t])


#Electricity supply constraints
    for j in range(0,SOURCE):
        for t in range(0,PERIODS):
            model.addConstr(e[j][t] <= PC[j])

    for j in range(0,SOURCE):
        for t in range(0,PERIODS):
            model.addConstr(e[j][t] <= CR[j]*o[j][t])

    for j in range(0,SOURCE):
        for t in range(0,PERIODS):
            model.addConstr(quicksum(p[j][k][t] for k in range(0,DEMANDZONE)) <= e[j][t])

    for k in range(0,DEMANDZONE):
        for t in range(0,PERIODS):
            model.addConstr(quicksum(PY[j][k]*p[j][k][t] for j in range(0,SOURCE)) <= GAP1[k][t])

#Flood constraints
    for j in range(0,SOURCE):
        for t in range(0,PERIODS):
            model.addConstr(f[j][t] <= q[j][t] - MT[j])

#   Budget Constraint
#g[t-1]*RA[t] >=  b_HPP1[2*t] + b_HPP2[2*t] + b_HPP1[2*t-1] + b_HPP2[2*t-1]   for t = 1...T/2
    for t in range(1,2):
        model.addConstr(133000000.0*RA[t] >= b_HPP2[t]+b_HPP2[t-1])
    for t in xrange(3,PERIODS,2):
        model.addConstr((g[t]*RA[t]) >= b_HPP2[t-1] + b_HPP2[t])   


#GDP
    for t in range(1,2):
        model.addConstr((g[t]) == 133000000.0 + (135.439*quicksum(quicksum((PY[j][k]*(p[j][k][t] + p[j][k][t-1])) for j in range(0,SOURCE)) for k in range(0,DEMANDZONE))) + (12.224*quicksum(quicksum(WY[j][n]*(u[j][n][t] + u[j][n][t-1]) for j in range(0,SOURCE)) for n in range(0,FARM))) - (71.196*quicksum(f[j][t] + f[j][t-1]) for j in range(0,SOURCE)))
    for t in xrange(3,PERIODS,2):
        model.addConstr((g[t]) == (g[t-2]) + (135.439*quicksum(quicksum((PY[j][k]*(p[j][k][t] + p[j][k][t-1] - p[j][k][t-2] - p[j][k][t-3])) for j in range(0,SOURCE)) for k in range(0,DEMANDZONE))) + (12.224*quicksum(quicksum(WY[j][n]*(u[j][n][t] + u[j][n][t-1] - u[j][n][t-2] - u[j][n][t-3]) for j in range(0,SOURCE)) for n in range(0,FARM))) - (71.196*quicksum(f[j][t] + f[j][t-1] - f[j][t-2] - f[j][t-3]) for j in range(0,SOURCE))) 
    for t in xrange(0,PERIODS,2):
        model.addConstr((g[t]) == 0.0)
#####################################
#   Setting Objective Function
######################################
    model.setObjective(quicksum(BETA[t]*(g[t]) for t in range(0,PERIODS)))
#    model.params.MIPGap = 0.01
    model.optimize()






#   print "Model Constraints:"
#   for gCon in model.getConstrs():
#       print gCon
        
#   print "Done Pinting constraints"
#    print "Size of constraint list is %s" % (len(model.getConstrs()))


    #    Solve MILP for Coal-Based Energy Supply Chain Problem
#    model.optimize()

    
#     for v in model.getVars():
#        print v.varName, v.x  
#     print 'Obj:', model.objVal
# v.varName
################### PRINTING OUTPUT onto a Text file START ################################
#    Python_Output = open("python_output.txt", "w")
#   numPP = model.getVarByName('y_%s_%s'
#  Python_Output.write(str(numPP))
# Python_Output.close()
 
    outputfile_name = "python_current_J%dK%dT%dP%d.txt" % (SOURCE,DEMANDZONE,PERIODS,percentage)      
    Python_Output = open(outputfile_name, "w")
    for v in model.getVars():
        Python_Output.write("%.8f\t" % (v.x))
    Python_Output.close()
################### PRINTING OUTPUT onto a Text file END   ################################    
except Exception as e:
    print e




