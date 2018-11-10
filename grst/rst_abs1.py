# -*- coding: cp936 -*-
__author__ = 'naivego'
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

#---------------------------------------------
datas_csvfile=r'D:\py\futs\csvf\ifc1.zj.csv'
bgni=3000
endi=3990
dtmbgn="2016/10/14 09:30:00"
dtmend="2017/01/06 15:00:00"
avgski=1
avgsk_cn=30
maxbarback=20

#rsts
symbol="IFC1.ZJ"
decsn=2  #小数位数
syb_open=symbol+'.aopen'
syb_high=symbol+'.high'
syb_low=symbol+'.low'
syb_close=symbol+'.close'
syb_volume=symbol+'.volume'
syb_oi=symbol+'.oi'
syb_factor=symbol+'.factor'

#----------------------------------------------
datas=pd.read_csv(datas_csvfile,index_col='datetime', parse_dates=True)  #
dask=datas.ix[dtmbgn:dtmend, [syb_open, syb_high, syb_low, syb_close,syb_volume, syb_oi,syb_factor]]
sk_factor=dask[syb_factor]
#sk_open=dask[syb_open]
sk_close=(dask[syb_close]/sk_factor).apply(lambda x: round(x,decsn))
sk_open=(dask[syb_open]/sk_factor).apply(lambda x: round(x,decsn))
sk_high=(dask[syb_high]/sk_factor).apply(lambda x: round(x,decsn))
sk_low=(dask[syb_low]/sk_factor).apply(lambda x: round(x,decsn))

sk_volume=dask[syb_volume]
sk_oi=dask[syb_oi]

print sk_open