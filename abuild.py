# -*- coding: utf-8 -*-
"""
Created on Thu Oct 26 14:42:03 2017

@author: naievgo
"""


from __future__ import division
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.pylab import date2num

import matplotlib.finance as mpf
from matplotlib.dates import DateFormatter, WeekdayLocator, DayLocator, MONDAY
from matplotlib.finance import candlestick2_ohlc
import matplotlib.ticker as ticker
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import re
import imp
import sys
import os
import pickle as pk
import traceback
import itertools
#from datetime import datetime
import urllib2, StringIO, docx, traceback
from copy import deepcopy
from afactor import *
from cs_factor import *
from datetime import datetime, timedelta

# 成交量或者持仓量进行品种帅选
def varselect(data1, selectlength, threshold):
    data = deepcopy(data1)
    value = data.rolling(window=selectlength).mean()
    data[data != np.nan] = np.nan
    data[value >= threshold] = 1
    return data

def plotsdk(stkdf, disfactors=[], Symbol='symbol', Period =''):
    quotes= stkdf.loc[:]
    # quotes['mid'] = 0
    xdate = [itime for itime in quotes['time']]

    # fig, (ax, ax1) = plt.subplots(2, sharex=True, figsize=(20, 10))
    fig, ax = plt.subplots(1, sharex=True, figsize=(20,8))
    #fig, ax = plt.subplots()
    fig.subplots_adjust(bottom=0.2, left=0.05)
    def mydate(x, pos):
        try:
            return xdate[int(x)]
        except IndexError:
            return ''
    candlestick2_ohlc(ax, quotes['open'], quotes['high'], quotes['low'], quotes['close'], width=0.5, colorup='r', colordown='green')
    ax.xaxis.set_major_locator(ticker.MaxNLocator(4))

    plt.title(Symbol + '_' + Period)
    plt.xlabel("time")
    plt.ylabel("price")

    ax.xaxis.set_major_formatter(ticker.FuncFormatter(mydate))
    # fig.autofmt_xdate()

    for disf in disfactors:
        if disf and disf in quotes.columns:
            if disf == 'ATR' or disf == 'sk_zsrpt' or disf == 'sk_qsrpt':
                # ax1 = ax.twinx()
                # quotes[disf].plot(ax=ax1)
                # ax1.xaxis.set_major_formatter(ticker.FuncFormatter(mydate))
                continue
            if disf == 'grst':
                pass
                # ax2 = ax.twinx()
                # quotes[disf].plot(ax=ax2)
                # ax2.xaxis.set_major_formatter(ticker.FuncFormatter(mydate))
            elif disf == 'qswr' or disf == 'rsl':
                pass
                # ax3 = ax1.twinx()
                # quotes[disf].plot(ax=ax1)
                # ax1.xaxis.set_major_formatter(ticker.FuncFormatter(mydate))
            #
            else:
                quotes[disf].plot(ax=ax)
                ax.xaxis.set_major_formatter(ticker.FuncFormatter(mydate))
    # quotes['mid'].plot(ax=ax1)

    fig.tight_layout()
    plt.grid()
    plt.legend(disfactors)
    plt.show()

    pass


class Load_BarData(object):
    # ----------------------------------------------------------------------
    def __init__(self, ABD_Config):
        self.DB_Rt_Dir = ABD_Config['DB_Rt_Dir']
        self.Time_Param = ABD_Config['Time_Param']
        self.Start_Date = self.Time_Param[0]
        self.End_Date = self.Time_Param[1]
        self.Period_List = ABD_Config['Period_List']
        self.First_Freq_Col_Param = ABD_Config['First_Freq_Col_Param']
        self.Other_Freq_Col_Param = ABD_Config['Other_Freq_Col_Param']
        sys.path.insert(0, self.DB_Rt_Dir + '/code/db_app.py')
        sys.path.insert(0, self.DB_Rt_Dir + '/code/')
        self.DB_App = getattr(imp.load_source('DB_App', self.DB_Rt_Dir + '/code/db_app.py'), 'DB_App')(self.DB_Rt_Dir)
        self.Panel_Data = None
        self.Variety_Index = None
        self.Date_Index = None
        self.Column_Index = None
        self.Sup_Signal_Col_List = None
        self.Filtered = False
        self.Filtered_Panel_Data = None
        self.Filtered_Dict_Data = {}
        self.Return_Dict = {}
        self.Data_Folder_List = []
        self.DF_Data = None

    def load_bar(self, Var_List=None):
        Start_Time = datetime.now()
        self.Panel_Data = self.DB_App.load_domContract_data_in_time(Var_List, self.Time_Param,
                                                                    self.First_Freq_Col_Param,
                                                                    self.Other_Freq_Col_Param, self.Period_List)
        print 'Loading panel data from database took:', (datetime.now() - Start_Time).total_seconds(), 's.'
        for x in self.Panel_Data.items:
            if self.Panel_Data[x].empty:
                self.Panel_Data.drop(x, inplace=True)
        self.Variety_Index = self.Panel_Data.items
        self.Date_Index = self.Panel_Data.major_axis
        self.Column_Index = self.Panel_Data.minor_axis
        # self.mark_date_on_panel()

    # ----------------------------------------------------------------------
    def clean_data(self, Col_List):
        for Col in Col_List:
            self.Panel_Data.loc[:, :, Col].replace(0, np.nan, inplace=True)

    # ----------------------------------------------------------------------
    def apply_adj_factor(self):
        Mult_List = [Minor for Minor in self.Column_Index if Minor.split('_')[0] in ['Open', 'High', 'Low', 'Close']]
        Join_List = list(set(self.Column_Index) - set(Mult_List))
        self.Panel_Data.update(self.Panel_Data.loc[:, :, Mult_List].mul(self.Panel_Data.loc[:, :, 'AdjFactor'], axis=2))

    # ----------------------------------------------------------------------
    def add_column(self, Column_Name, Func, Input_Col_List=[], **kwargs):
        self.Panel_Data.loc[:, :, Column_Name] = pd.DataFrame()
        for Variety in self.Variety_Index:
            Curr_Data = Func(self.Panel_Data.loc[Variety, :, Input_Col_List], **kwargs)
            if type(Curr_Data) == pd.DataFrame:
                self.Panel_Data.loc[Variety, :, Column_Name] = Curr_Data.iloc[:, 0]
            else:
                self.Panel_Data.loc[Variety, :, Column_Name] = Curr_Data

    # ----------------------------------------------------------------------
    def add_columns(self, Column_Name_List, Func, Input_Col_List=[], **kwargs):
        for Column_Name in Column_Name_List:
            self.Panel_Data.loc[:, :, Column_Name] = pd.DataFrame()
        for Variety in self.Variety_Index:
            Curr_Data = Func(self.Panel_Data.loc[Variety, :, Input_Col_List], Column_Name_List, **kwargs)
            for Column_Name in Column_Name_List:
                self.Panel_Data.loc[Variety, :, Column_Name] = Curr_Data[Column_Name]

    # ----------------------------------------------------------------------
    def add_df(self, Column_Name, Func, Input_Col_List=[], **kwargs):
        self.Panel_Data.loc[:, :, Column_Name] = pd.DataFrame()
        self.Panel_Data.loc[:, :, Column_Name] = Func(self.Panel_Data.loc[:, :, Input_Col_List], **kwargs)

    # ----------------------------------------------------------------------
    def set_sup_signal_col_list(self, Sup_Signal_Col_List):
        self.Sup_Signal_Col_List = Sup_Signal_Col_List
        for Variety in self.Variety_Index:
            self.Panel_Data[Variety].loc[:, self.Sup_Signal_Col_List] = self.Panel_Data[Variety].loc[:,
                                                                        self.Sup_Signal_Col_List].shift(1)

    # ----------------------------------------------------------------------
    def filter_by_column_value(self, Func, Separate=False, **kwargs):
        if not self.Filtered:
            if Separate:
                for Variety in self.Variety_Index:
                    self.Filtered_Dict_Data[Variety] = Func(self.Panel_Data[Variety], **kwargs)
            else:
                for Variety in self.Variety_Index:
                    self.Filtered_Panel_Data.loc[Variety, :, :] = Func(self.Panel_Data[Variety], **kwargs)
            self.Filtered = True
        else:
            pass

    # ----------------------------------------------------------------------



    # ----------------------------------------------------------------------
    def plot_k2(self, stkdf):
        Column0 = stkdf.columns[0]
        if '_' not in Column0:
            Period = 'd'
        else:
            Period = Column0.split('_')[1]

        data_list = []
        for dates, row in stkdf.iterrows():
            # 将时间转换为数字
            if Period == 'd':
                date_time = datetime.strptime(dates, '%Y_%m_%d')
            else:
                date_time = datetime.strptime(dates, '%Y-%m-%d %H:%M:%S')

            t = date2num(date_time)
            open, high, low, close = row[:4]
            datas = (t, open, high, low, close)
            data_list.append(datas)


        Dat_bar = stkdf.loc[:]
        if Period == 'd':
            Dat_bar= Dat_bar.rename(columns={'Open': 'open', 'High': 'high', 'Low': 'low', 'Close': 'close','Volume':'volume'})
        else:
            Dat_bar = Dat_bar.rename(columns={'Open_' + Period: 'open', 'High_' + Period: 'high', 'Low_' + Period: 'low', 'Close_' + Period: 'close', 'Volume_' + Period: 'volume'})

        Dat_bar['TR1'] = Dat_bar['high'] - Dat_bar['low']
        Dat_bar['TR2'] = abs(Dat_bar['high'] - Dat_bar['close'].shift(1))
        Dat_bar['TR3'] = abs(Dat_bar['low'] - Dat_bar['close'].shift(1))
        TR = Dat_bar.loc[:, ['TR1', 'TR2', 'TR3']].max(axis=1)
        ATR = TR.rolling(14).mean()
        stkdf['ATR'] = ATR
        stkdf['Ma'] = Dat_bar['close'].rolling(10).mean()

        # 创建子图
        fig, ax = plt.subplots()
        fig.subplots_adjust(bottom=0.2)
        # 设置X轴刻度为日期时间
        ax.xaxis_date()

        mpf.candlestick_ohlc(ax, data_list, width=0.1, colorup='r', colordown='green')
        plt.xticks(rotation=45)
        plt.yticks()
        plt.title('symbol')
        plt.xlabel("time")
        plt.ylabel("price")

        #plt.plot(stkdf['ATR'])
        plt.plot(stkdf['Ma'])


        fig.tight_layout()
        plt.grid()
        plt.show()


    def plotk( self, stkdf, disfactors=['ATR'], Symbol='symbol'):
        quotes= stkdf.loc[:]
        Column0= quotes.columns[0]
        if '_' not in Column0:
            Period = 'd'
        else:
            Period = Column0.split('_')[1]

        quotes = quotes.rename(columns={'Open_' + Period: 'open', 'High_' + Period: 'high', 'Low_' + Period: 'low',
                                        'Close_' + Period: 'close', 'Volume_' + Period: 'volume'})
        if Period=='d':
            #quotes = quotes.rename(columns={'Open': 'open', 'High': 'high', 'Low': 'low', 'Close': 'close','Volume':'volume'})
            quotes['time'] = stkdf.index
            xdate = [datetime.strptime(i, '%Y_%m_%d') for i in quotes['time']]
        else:
            #quotes = quotes.rename(columns={'Open_' + Period: 'open', 'High_' + Period: 'high', 'Low_' + Period: 'low','Close_' + Period: 'close', 'Volume_' + Period: 'volume'})
            quotes['time'] = stkdf.index
            xdate = [datetime.strptime(i, '%Y-%m-%d %H:%M:%S') for i in quotes['time']]

        Dat_bar = quotes.loc[:]
        Dat_bar['TR1'] = Dat_bar['high'] - Dat_bar['low']
        Dat_bar['TR2'] = abs(Dat_bar['high'] - Dat_bar['close'].shift(1))
        Dat_bar['TR3'] = abs(Dat_bar['low'] - Dat_bar['close'].shift(1))
        TR = Dat_bar.loc[:, ['TR1', 'TR2', 'TR3']].max(axis=1)
        MATR = TR.rolling(14).mean()
        quotes['ATR'] = MATR/Dat_bar['close'].shift(1)
        quotes['Ma'] = Dat_bar['close'].rolling(10).mean()
        quotes['Rp'] = (Dat_bar['close'] - Dat_bar['low'])/MATR

        fig, (ax, ax2) = plt.subplots(2, sharex=True)
        #fig, ax = plt.subplots()
        fig.subplots_adjust(bottom=0.2, left=0.05)
        candlestick2_ohlc(ax, quotes['open'], quotes['high'], quotes['low'], quotes['close'], width=0.5, colorup='r', colordown='green')
        ax.xaxis.set_major_locator(ticker.MaxNLocator(4))
        def mydate(x, pos):
            try:
                return xdate[int(x)]
            except IndexError:
                return ''
        plt.title(Symbol + '_' + Period)
        plt.xlabel("time")
        plt.ylabel("price")

        ax.xaxis.set_major_formatter(ticker.FuncFormatter(mydate))
        #fig.autofmt_xdate()
        #ax2 = ax.twinx()

        quotes['Ma'].plot(ax=ax)
        quotes['ATR'].plot(ax=ax2)
        for disf in disfactors:
            if disf and disf in quotes.columns:
                quotes[disf].plot(ax=ax2)
                ax2.xaxis.set_major_formatter(ticker.FuncFormatter(mydate))

        fig.tight_layout()
        plt.grid()
        plt.show()

    def plotsdk( self, stkdf, disfactors=[], Symbol='symbol', Period =''):
        quotes= stkdf.loc[:]
        # quotes['mid'] = 0
        xdate = [itime for itime in quotes['time']]

        # fig, (ax, ax1) = plt.subplots(2, sharex=True, figsize=(20, 10))
        fig, ax = plt.subplots(1, sharex=True, figsize=(20,10))
        #fig, ax = plt.subplots()
        fig.subplots_adjust(bottom=0.2, left=0.05)

        candlestick2_ohlc(ax, quotes['open'], quotes['high'], quotes['low'], quotes['close'], width=0.5, colorup='r', colordown='green')
        ax.xaxis.set_major_locator(ticker.MaxNLocator(4))
        def mydate(x, pos):
            try:
                return xdate[int(x)]
            except IndexError:
                return ''
        plt.title(Symbol + '_' + Period)
        plt.xlabel("time")
        plt.ylabel("price")

        ax.xaxis.set_major_formatter(ticker.FuncFormatter(mydate))
        # fig.autofmt_xdate()

        for disf in disfactors:
            if disf and disf in quotes.columns:
                if disf == 'ATR' or disf == 'sk_zsrpt' or disf == 'sk_qsrpt':
                    # ax1 = ax.twinx()
                    # quotes[disf].plot(ax=ax1)
                    # ax1.xaxis.set_major_formatter(ticker.FuncFormatter(mydate))
                    continue
                if disf == 'grst':
                    pass
                    # ax2 = ax.twinx()
                    # quotes[disf].plot(ax=ax2)
                    # ax2.xaxis.set_major_formatter(ticker.FuncFormatter(mydate))
                elif disf == 'qswr' or disf == 'rsl':
                    pass
                    # ax3 = ax1.twinx()
                    # quotes[disf].plot(ax=ax1)
                #
                else:
                    quotes[disf].plot(ax=ax)
                    ax.xaxis.set_major_formatter(ticker.FuncFormatter(mydate))
        # quotes['mid'].plot(ax=ax1)

        fig.tight_layout()
        plt.grid()
        plt.show()
        pass

def laod_DomDatas(  ):
    h5file = r'\data\db\CHN_F\II_O\VarietyFctr\\'.replace('\\',
                                                          '/') + 'CHN_F_II_O_VarietyFctr_DomContract_Original_Inter_DB.h5'
    ABD_Config = {}
    ABD_Config['Rt_Dir'] = os.getcwd()
    ABD_Config['DB_Rt_Dir'] = r'D:\ArcticFox\project\hdf5_database'.replace('\\', '/')
    ABD_Config['Time_Param'] = ['2016_01_01', '2017_06_30']
    ABD_Config['Group_Name'] = 'rst'
    ABD_Config['Period_List'] = ['H']
    ABD_Config['First_Freq_Col_Param'] = ['Open', 'High', 'Low', 'Close', 'Volume','Oi','AdjFactor']
    ABD_Config['Other_Freq_Col_Param'] = ['Close']

    dh5 = ABD_Config['DB_Rt_Dir'] + h5file
    h5stroe = pd.HDFStore(dh5)
    Var_List_all = h5stroe.root._v_children.keys()
    h5stroe.close()

    Var_List_all = ['Y', 'FU', 'BB', 'ZN', 'JR', 'WH', 'BU', 'FB', 'WR', 'FG', 'JD', 'HC', 'L', 'NI',
                    'PP', 'RS', 'PB', 'LR', 'TF', 'RM', 'RI', 'PM', 'A', 'C', 'B', 'AG', 'RU', 'I', 'J',
                    'M', 'AL', 'CF', 'IH', 'AU', 'T', 'V', 'CS', 'IC', 'CU', 'IF', 'MA', 'OI', 'JM', 'SR', 'SF',
                    'SN', 'SM', 'RB','TA', 'P', 'ZC']  # 'WT', 'WS', 'TC','ER',,'ME','RO',
    subvars = ['RB'] #Var_List_all

    for i in range(0,len(subvars),5):

        Var_List = subvars[i:i+5]    # Var_List_all  #  ['RB']  ['I', 'RB', 'AU', 'CU', 'IF']
        print Var_List
        # continue
        ABD = Load_BarData(ABD_Config)
        ABD.load_bar(Var_List)

        # ABD.clean_data(['Close_M'])
        if ABD_Config['Period_List'][0] != 'd':
            ABD.apply_adj_factor()

        # 因子存放目录
        dir1 = 'D:/lab/Dom/'
        period = ABD_Config['Period_List'][0] # 'Grst' # 'Qrst'  # 'Grst'
        # 创建目录
        factordir = dir1 + period + '/'
        if not (os.path.exists(factordir)):
            os.makedirs(factordir)

        for var in  Var_List:
            print 'buile factor ', period, 'for :', var
            skdata = ABD.Panel_Data[var]
            skdata = skdata.dropna(axis=0, how='any').copy()

            if 1:  # 标准化处理
                # 修改索引名称
                if period == 'd':
                    reindex = [date.replace('_', '-') for date in skdata.index]
                    skdata.index = reindex

                # 修改列名 去掉 '_d' or _M, bar数据列名与 catbardata保持一致
                recol = {}
                for col in skdata.columns:
                    ncol = col.replace('_' + period, '').lower()
                    if ncol == 'oi':
                        ncol = 'openInterest'
                    elif ncol == 'adjfactor':
                        ncol = 'adjFactor'
                    recol[col] = ncol
                skdata.rename(columns=recol, inplace=True)
                if 0:
                    skdata['time'] = skdata.index
                    plotsdk(skdata, Symbol=var, disfactors=[])
                print var, 'ok'
            # ----剔除集合竞价bar
            if 1 and period != 'd':
                skdata['hms'] = [x[11:] for x in skdata.index]
                skdata['crthh'] = [x[11:13] for x in skdata.index]
                skdata['prehh'] = skdata['crthh'].shift(1)
                skdata = skdata[~((skdata['prehh'] == u'15') & (skdata['high'] - skdata['low'] < 0.01) \
                                  & ((skdata['hms'] == u'21:00:00') | (skdata['hms'] == u'09:00:00') | (skdata['hms'] == u'09:30:00')))]

            skdata.to_csv(factordir + var + '_' + period + '.csv')


def laod_Dombar( Var, Period, Time_Param, DB_Rt_Dir):
    ABD_Config = {}
    ABD_Config['DB_Rt_Dir'] = DB_Rt_Dir
    ABD_Config['Time_Param'] = Time_Param
    ABD_Config['Period_List'] = [Period]
    ABD_Config['First_Freq_Col_Param'] = ['Open', 'High', 'Low', 'Close', 'Volume','Oi','AdjFactor']
    ABD_Config['Other_Freq_Col_Param'] = ['Close']

    ABD = Load_BarData(ABD_Config)
    ABD.load_bar([Var])
    period = Period
    # ABD.clean_data(['Close_M'])
    if period != 'd':
        ABD.apply_adj_factor()

    skdata = ABD.Panel_Data[Var]
    skdata = skdata.dropna(axis=0, how='any').copy()

    if 1:  # 标准化处理
        # 修改索引名称
        if period == 'd':
            reindex = [date.replace('_', '-') for date in skdata.index]
            skdata.index = reindex

        # 修改列名 去掉 '_d' or _M, bar数据列名与 catbardata保持一致
        recol = {}
        for col in skdata.columns:
            ncol = col.replace('_' + period, '').lower()
            if ncol == 'oi':
                ncol = 'openInterest'
            elif ncol == 'adjfactor':
                ncol = 'adjFactor'
            recol[col] = ncol
        skdata.rename(columns=recol, inplace=True)

    #----剔除集合竞价bar
    if 1 and period != 'd':
        skdata['hms'] = [x[11:] for x in skdata.index]
        skdata['crthh'] = [x[11:13] for x in skdata.index]
        skdata['prehh'] = skdata['crthh'].shift(1)
        skdata = skdata[~((skdata['prehh'] == u'15') & (skdata['high'] - skdata['low'] < 0.01) \
                         & ((skdata['hms'] == u'21:00:00') | (skdata['hms'] == u'09:00:00') | (skdata['hms'] == u'09:30:00')))]
        skdata.drop(['hms', 'crthh', 'prehh'], axis=1, inplace=True)
    return skdata


def pro_Grst_Factor(  ):
    h5file = r'\data\db\CHN_F\II_O\VarietyFctr\\'.replace('\\',
                                                          '/') + 'CHN_F_II_O_VarietyFctr_DomContract_Original_Inter_DB.h5'
    ABD_Config = {}
    ABD_Config['Rt_Dir'] = os.getcwd()
    ABD_Config['DB_Rt_Dir'] = r'D:\ArcticFox\project\hdf5_database'.replace('\\', '/')
    ABD_Config['Time_Param'] = ['2010_01_01', '2017_12_31']
    ABD_Config['Group_Name'] = 'rst'
    ABD_Config['Period_List'] = ['M15']
    ABD_Config['First_Freq_Col_Param'] = ['Open', 'High', 'Low', 'Close', 'Volume', 'AdjFactor']
    ABD_Config['Other_Freq_Col_Param'] = ['Close']

    dh5 = ABD_Config['DB_Rt_Dir'] + h5file
    h5stroe = pd.HDFStore(dh5)
    Var_List_all = h5stroe.root._v_children.keys()
    h5stroe.close()

    # Var_List_all = ['Y', 'FU', 'BB', 'ZN', 'JR', 'WH', 'BU', 'FB', 'WR', 'FG', 'JD', 'HC', 'L', 'NI',
    #                 'PP', 'RS', 'PB', 'LR', 'RB', 'TF', 'RM', 'RI', 'PM', 'A', 'C', 'B', 'AG', 'RU', 'I', 'J',
    #                 'M', 'AL', 'CF', 'IH', 'AU', 'T', 'V', 'CS', 'IC', 'CU', 'IF', 'MA', 'OI', 'JM', 'SR', 'SF',
    #                 'SN', 'SM', 'TA', 'P']  # 'WT', 'WS', 'TC','ER','ZC','ME','RO',

    Var_List = ['I', 'RB', 'CU', 'IF']  #  Var_List_all  #  ['RB']

    ABD = Load_BarData(ABD_Config)
    ABD.load_bar(Var_List)

    # ABD.clean_data(['Close_M'])
    if ABD_Config['Period_List'][0] != 'd':
        ABD.apply_adj_factor()

    # 因子存放目录
    dir1 = 'D:/Factor/'
    factorname = 'Grst' # 'Qrst'  # 'Grst'
    # 创建目录
    factordir = dir1 + factorname + '/'
    if not (os.path.exists(factordir)):
        os.makedirs(factordir)
        # 参数列表

    # 因子生成
    Period = 'd'
    factorvs = pd.DataFrame()

    for var in  Var_List:
        print 'buile factor ', factorname, 'for :', var
        skdata = ABD.Panel_Data[var]
        skdata = skdata.dropna(axis=0, how='any')
        Grst   = Grst_Factor(skdata)
        factor = Grst.cal_Grst()

        factor_var = factor['sk_bsfact']   #'sk_bsfact'
        factor_var = factor_var.rename(columns={'sk_bsfact': var})
        if not factor_var.empty:
            factorvs[var] = factor_var
    if not factorvs.empty:
        factorvs.to_csv(factordir + factorname  + '.csv')


def btest_Grst_Factor(  ):
    Var_List_all = ['Y', 'FU', 'BB', 'ZN', 'JR', 'BU', 'WR', 'FG', 'JD', 'HC', 'L', 'NI',
                    'PP', 'PB', 'RB', 'TF', 'RM', 'PM', 'A', 'C', 'B', 'AG', 'RU', 'I', 'J',
                    'M', 'AL', 'CF', 'V', 'CS', 'MA', 'OI', 'JM', 'SR', 'TA', 'P'] #

    Var_List_pat =['RB']# 'JD', 'CU', 'I',  'FG',  'IF'] #'CU', 'I',  'FG', 'RB', 'IF', ]

    Var_List =  Var_List_pat

    Msdpset = {'ma': 'M30', 'su': 'd'}
    #--------------------backtest------------------------
    TS_Config = {}
    TS_Config['Remark'] = ''
    TS_Config['DB_Rt_Dir'] = r'D:\ArcticFox\project\hdf5_database'.replace('\\', '/')
    TS_Config['Rt_Dir'] = os.getcwd()
    TS_Config['Init_Capital'] = 10000000
    TS_Config['Time_Param'] = ['2016-06-01', '2017-06-25']
    TS_Config['SlipT'] = 0
    TS_Config['OrdTyp'] = {'open': 'Lmt', 'close': 'Lmt'}  # ['Mkt', 'Lmt', 'Stp']

    # ---子策略ostp设置
    TS_Config['Ostpn_Dic'] = {
        'Grst':
            {
                'Grst-qsp1': Ostpn(0, -10, 200, 0, 10, -200),
                'Grst-bsp1': Ostpn(0, -10, -5, 0, 10, 5),
                'Grst-rsp1': Ostpn(0, -8, 50, 0, 8, -50),
                'Grst-zsp1': Ostpn(2, -20, 2, -2, 20, -2),
                'Grst-ovr1': Ostpn(-110, -150, -40, 110, 150, 40),

                'Grst-qsp2': Ostpn(0, -10, 800, 0, 10, -800),
                'Grst-bsp2': Ostpn(0, -10, 160, 0, 10, -160),
                'Grst-rsp2': Ostpn(0, -8, 160, 0, 8, -160),
                'Grst-zsp2': Ostpn(0, -20, 110, 0, 20, -120),
                'Grst-ovr2': Ostpn(-110, -150, -2, 110, 150, 2)
            }
    }
    # ---子策略开仓权重设置
    TS_Config['Sgnwt_Dic'] = {
        'Grst':
            {
                'Grst-qsp1': 0,
                'Grst-bsp1': 0,
                'Grst-rsp1': 1,
                'Grst-zsp1': 0,
                'Grst-ovr1': 0,
                'Grst-qsp2': 0,
                'Grst-bsp2': 0,
                'Grst-rsp2': 1,
                'Grst-zsp2': 0,
                'Grst-ovr2': 0
            }
    }

    # --------------------backtest------------------------
    # mfaset = {'sal': True, 'rdl': True, 'mdl': True, 'upl': True, 'dwl': True, 'mir': True}
    mfaset = {'sal': True, 'rdl': True, 'mdl': True, 'upl': False, 'dwl': False, 'mir': False}
    tdkopset = {
        'sekop' : {'sal': 0, 'rdl': 1, 'mdl': 0},
        'etkop' : {'sal': 0, 'rdl': 1, 'mdl': 0}
    }
    for var in Var_List:
        print 'Test Grst For ', var
        Time_Param = [TS_Config['Time_Param'][0].replace('-', '_'), TS_Config['Time_Param'][1].replace('-', '_')]
        DB_Rt_Dir = TS_Config['DB_Rt_Dir']
        skdata = laod_Dombar(var, Msdpset['ma'], Time_Param, DB_Rt_Dir)
        Mrst = Grst_Factor(var,  Msdpset['ma'], skdata,  fid= 'ma')
        btest = True
        if 'su' in Msdpset:
            sfaset = {'sal': True, 'rdl': True, 'mdl': True, 'upl': False, 'dwl': False, 'mir': False}
            stdsk = laod_Dombar(var, Msdpset['su'], Time_Param, DB_Rt_Dir)
            Arst = Grst_Factor(var, Msdpset['su'], stdsk, fid= 'su')
            Arst.grst_init(faset = sfaset, btest=False, btconfig=TS_Config, subrst= None)
            Mrst.addsgn(Arst.quotes, ['close'], Tn='d', fillna= False)
            Mrst.renamequote('close_d', 'sudc')
            Mrst.setmacn()
        else:
            Arst = None
        Mrst.grst_init(faset=mfaset, btest=btest, btconfig=TS_Config, subrst= Arst, tdkopset = tdkopset)
        Mrst.cal_next()

        if Mrst.TSBT:
            Mrst.TSBT.Show_SaveResult()

        disfas = ['disrst','sal', 'brdl', 'trdl', 'bmdl', 'tmdl'] #,'zsh', 'zsl', 'rstsph', 'rstspl','bsh', 'bsl' ,'bbl', 'ttl'  'bbl', 'ttl', 'obbl', 'ottl',
        # plotsdk(quotes, disfactors=['grst', 'qsh', 'qsl', 'zsh', 'zsl', 'rsl','disrst', 'bbl', 'ttl'])  # ,'ATR'  'qswr',
        # plotsdk(quotes, disfactors=['disrst','sk_qsrpt','sk_zs1c', 'sk_zs2c', 'sk_qs1c','sk_qs2c','sk_zs1a', 'sk_zs2a', 'sk_qs1a','sk_qs2a'])  #,'sk_zsrpt','sk_qsrpt'  'sk_zs1c','sk_zs2c', 'qsh', 'qsl',
        # plotsdk(quotes, Symbol=var, disfactors=['disrst', 'bbl', 'ttl', 'alp1', 'alp2', 'alp5', 'dlp1', 'dlp2', 'dlp5', ])
        # plotsdk(quotes, Symbol=var, disfactors=disfas)

        #---------------show sgns
        if 'su' in Msdpset:
            Arst.colfas()
            Tn = 'd'
            extfas= ['disrst', 'sal', 'brdl', 'trdl'] #['disrst', 'sal', 'brdl', 'trdl', 'bmdl', 'tmdl']
            Mrst.addsgn(Arst.quotes, extfas, Tn=Tn, fillna = False)
            disfas = [colna + '_'+ Tn for colna in extfas] + ['disrst','brdl', 'trdl', 'alp1', 'dlp1','sal' ] #'disrst','ma','mid', ['disrst','sal', 'brdl', 'trdl', 'alp1', 'dlp1' ]
        Mrst.colfas()
        quotesk = Mrst.quotes
        plotsdk(quotesk, Symbol=var, disfactors = disfas)

        print datetime.now(),  'ok'

class Realdata(object):
    # ----------------------------------------------------------------------
    def __init__(self):
        self.Mongo_Client = None
        self.db_login()
        self.Start_Date = "2017-01-05"
        self.Today_Date =  datetime.now().strftime('%Y-%m-%d')
        self.Data_List_Dict = {}
    # ----------------------------------------------------------------------
    def db_login(self):
        """连接MongoDB数据库"""
        if not self.Mongo_Client:
            # 读取MongoDB的设置
            Mongo_Host = "172.16.1.101"
            Mongo_Port = 27017
            try:
                # 设置MongoDB操作的超时时间为0.5秒
                self.Mongo_Client = MongoClient(Mongo_Host, Mongo_Port, connectTimeoutMS=500)
                # 调用server_info查询服务器状态，防止服务器异常并未连接成功
                self.Mongo_Client.server_info()
            except ConnectionFailure:
                print traceback.format_exc()

    #----------------------------------------------------------------------

    def get_variety_from_symbol(self, Symbol):
        if Symbol in {'Au(T+D)':0, 'Ag(T+D)':0, 'mAu(T+D)':0}:
            return Symbol
        else:
            return re.search('[A-Za-z]*', Symbol).group()

    # ----------------------------------------------------------------------
    def get_data(self):
        Database_Dom   = self.Mongo_Client['HisData']
        Collection_Dom = Database_Dom['Dom']
        Cursor         = Collection_Dom.find({"date":{"$gte":datetime.strptime(self.Start_Date, '%Y-%m-%d'),
                                                      "$lte":datetime.strptime(self.Today_Date, '%Y-%m-%d')}})
        for d in Cursor:
            Curr_Symbol  = d['symbol']
            Curr_Variety = self.get_variety_from_symbol(Curr_Symbol)
            if not (Curr_Variety in self.Data_List_Dict):
                self.Data_List_Dict[Curr_Variety] = [pd.Series(d)]
            else:
                self.Data_List_Dict[Curr_Variety].append(pd.Series(d))

    # ----------------------------------------------------------------------
    def getbar(self, var):
        print 'load his data: ',var
        Var_Data     = self.Data_List_Dict[var]
        Var_Data_Df  = pd.DataFrame(Var_Data)
        Var_Data_Df.index = Var_Data_Df['date']
        # 检查该品种的数据是否有重复
        if len(set(Var_Data_Df.index)) != Var_Data_Df.index.size:
            Var_Data_Df.ix[:,'_id'] = Var_Data_Df.ix[0,'_id']
            print '   ',var,':his data repeated!'
            Var_Data_Df  = Var_Data_Df.drop_duplicates()
            Var_Data_Df.sort_values(by = Var_Data_Df.index.name, inplace= True)
        # 计算品种筛选因子
        var1 = var_select(Var_Data_Df.ix[:,'volume'],20,10000)
        var1.replace(np.nan, 0, inplace = True)
        var2 = var_select(Var_Data_Df.ix[:,'amt'],20,500000000)
        var2.replace(np.nan, 0, inplace = True)
        var12  = var1 + var2
        var12.replace(1,0,inplace = True)
        var12.replace(2,1,inplace = True)
        var12.replace(0,np.nan,inplace = True)
        Var_Data_Df['VarTrade20'] = var12

        Close = Var_Data_Df.ix[:,'close']*(Var_Data_Df.ix[:,'adjF'].fillna('ffill'))
        Open  = Var_Data_Df.ix[:,'open']*(Var_Data_Df.ix[:,'adjF'].fillna('ffill'))
        High  = Var_Data_Df.ix[:, 'high'] * (Var_Data_Df.ix[:, 'adjF'].fillna('ffill'))
        Low   = Var_Data_Df.ix[:, 'low'] * (Var_Data_Df.ix[:, 'adjF'].fillna('ffill'))
        Volume = Var_Data_Df.ix[:, 'volume']
        skdata = pd.DataFrame(data= {'open':Open, 'high':High, 'low':Low, 'close':Close, 'volume': Volume}, index=Close.index)

        print var, ' ok'
        return skdata

def showrel_Grst_Factor(  ):
    relda = Realdata()
    relda.get_data()
    Var_List_all = ['Y', 'FU', 'BB', 'ZN', 'JR', 'BU', 'WR', 'FG', 'JD', 'HC', 'L', 'NI',
     'PP', 'PB', 'RB', 'TF', 'RM', 'PM', 'A', 'C', 'B', 'AG', 'RU', 'I', 'J',
     'M', 'AL', 'CF', 'V', 'CS', 'MA', 'OI', 'JM', 'SR', 'TA', 'P']
    Var_List = ['CF','CU', 'I', 'FG','JD', 'RB','IF'] # Var_List_all  #   ['CF','CU', 'I', 'FG','JD', 'RB','IF']

    for var in Var_List:
        skdata = relda.getbar(var)
        Grst = Grst_Factor(skdata, sdt=True)
        quotes = Grst.cal_Grst()

        # plotsdk(quotes, disfactors=['grst', 'qsh', 'qsl', 'zsh', 'zsl', 'rsl','disrst', 'bbl', 'ttl'])  # ,'ATR'  'qswr',
        # plotsdk(quotes, disfactors=['disrst','sk_qsrpt','sk_zs1c', 'sk_zs2c', 'sk_qs1c','sk_qs2c','sk_zs1a', 'sk_zs2a', 'sk_qs1a','sk_qs2a'])  #,'sk_zsrpt','sk_qsrpt'  'sk_zs1c','sk_zs2c', 'qsh', 'qsl',
        print 'plotsdk', var
        plotsdk(quotes, Symbol=var, disfactors=['disrst', 'bbl', 'ttl', 'alp1', 'alp2','alp3','alp4','alp5','alp6','dlp1', 'dlp2','dlp3','dlp4','dlp5','dlp6'])  #,'zsh', 'zsl', 'rstsph', 'rstspl','bsh', 'bsl'


if __name__ == '__main__':
    # laod_DomDatas()
    btest_Grst_Factor()
    # pro_Grst_Factor()
    # showrel_Grst_Factor()

    pass
























