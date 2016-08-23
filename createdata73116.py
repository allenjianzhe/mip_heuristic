# file name createdata73116
import csv
import sys
import math
import numpy
import pandas as pd


def generate_cutomer_data(size_of_customer):
    from random import randint as uniform_dist
    data = pd.DataFrame(
        columns=['Customer_Id', 'Final_Destination', 'Demand', 'Due_Date', 'Penalty'])
    for i in range(size_of_customer):
        data.loc[i] = [i, 'SS', uniform_dist(50, 250), uniform_dist(6, 35), 50]
    return data
size_of_customer = 50
d = generate_cutomer_data(size_of_customer)
d.to_csv('C:\Users\MacBook Air\Desktop\my research\cus_50_21.csv', index=False)
