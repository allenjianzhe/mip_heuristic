# -*- coding: utf-8 -*-
"""
Created on Fri Jul 15 13:54:36 2016

@author: MacBook Air
"""

import os

def read_input(f):
    pass
def compute(data):
    pass

csv_files = os.listdir('.')
datas = []
results = []

for f in csv_files:
    data = read_input(f)
    result = compute(data)
    datas.append(data)
    results.append(result)
#----------------------------------
