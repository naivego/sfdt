# -*- coding: cp936 -*-
__author__ = 'naivego'

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import csv
import datetime
#---------------------------------------------
gdpath=r'D:\py\futs\csvf'
datas_csvfile=gdpath+r'\future_lastday.csv'
syb_code='code'
syb_date='date'
datas=pd.read_csv(datas_csvfile)  #

setdats=datas.loc[:, [syb_code, syb_date]]
codes=setdats[syb_code]
dates=setdats[syb_date]

syb_if_code=[]
syb_if_date=[]
for i in  range(len(codes)):
   if codes[i][0:2]=="IF":
       print codes[i], dates[i]

'''
print setdats[syb_code]
print setdats[syb_date]
'''

