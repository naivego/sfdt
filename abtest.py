# -*- coding: utf-8 -*-

# 2018-05-18 单品种TS测试模块
# ------------------------------------------------------------------------------
from __future__ import division
import pandas as pd
import numpy as np
from copy import deepcopy
import os
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from datetime import datetime, timedelta
from time import localtime, strftime
import csv
import json
import collections
import shutil
from scipy.interpolate import griddata
from matplotlib import cm
from matplotlib.ticker import LinearLocator, FormatStrFormatter
from matplotlib.pylab import date2num
from factosdp import *



class Order(object):
    # ----------------------------------------------------------------------
    def __init__(self, Symbol, OrdSize, OrdAmount, OrdPrice, OrdTyp, OrdTime, Offset, OrdSki=None, OrdSp = None, OrdTp = None, Psn=None, Msn = None, Ordid=None, OrdFlg='NB'):
        """Constructor"""
        self.Symbol = Symbol
        self.OrdSize = OrdSize
        self.OrdAmount = OrdAmount
        self.OrdPrice = OrdPrice
        self.OrdTyp = OrdTyp
        self.OrdTime = OrdTime
        self.Offset = Offset
        self.OrdSki = OrdSki
        self.OrdSp = OrdSp
        self.OrdTp = OrdTp
        self.Psn = Psn
        self.Msn = Msn
        self.Ordid = Ordid
        self.OrdFlg = OrdFlg


class Trdord(object):
    # ----------------------------------------------------------------------
    def __init__(self, Symbol, TrdSize, TrdPrice, TrdTime, Offset, Trdski=None, TrdSp = None, TrdTp = None, Psn=None, Msn = None, Trdid=None, TrdFlg='NB'):
        """Constructor"""
        self.Symbol = Symbol
        self.TrdSize = TrdSize
        self.TrdPrice = TrdPrice
        self.TrdTime = TrdTime
        self.Offset = Offset
        self.Trdski = Trdski
        self.TrdSp = TrdSp
        self.TrdTp = TrdTp
        self.Psn = Psn
        self.Msn = Msn
        self.Trdid = Trdid
        self.TrdFlg = TrdFlg

class Position(object):
    # ----------------------------------------------------------------------
    def __init__(self, OpenTrd):
        """Constructor"""
        self.Symbol = OpenTrd.Symbol
        self.EntSize = OpenTrd.TrdSize
        self.EntPrice = OpenTrd.TrdPrice
        self.EntTime = OpenTrd.TrdTime
        self.EntSki = OpenTrd.Trdski
        self.EntSp = OpenTrd.TrdSp
        self.EntTp = OpenTrd.TrdTp
        self.Psn = OpenTrd.Psn
        self.Msn = OpenTrd.Msn
        self.MktValue = 0
        self.Margin = 0
        self.PAL = 0
        self.CldPrice = 0
        self.CldTime = 0
        self.CldFlg = None
        self.EntFlg = OpenTrd.TrdFlg
        self.Posid = OpenTrd.Trdid
        self.SpFlg = None
        self.TpFlg = None

class Sgnposinf(object):
    # ----------------------------------------------------------------------
    def __init__(self, SgnFlg, Symbol):
        self.SgnFlg = SgnFlg
        self.Symbol = Symbol
        self.EntNum = 0

        self.Lg_Vol = 0
        self.Lg_EntNum = 0
        self.Lg_Avg = 0
        self.Lg_MinEntp = None
        self.Lg_MaxEntp = None
        self.Lg_Sum = 0.0


        self.St_Vol = 0
        self.St_EntNum = 0
        self.St_Avg = 0
        self.St_MinEntp = None
        self.St_MaxEntp = None
        self.St_Sum = 0.0

    def addpos(self, pos):
        if pos.Symbol != self.Symbol or pos.EntFlg.split('_')[0] != self.SgnFlg:
            return
        self.EntNum += 1
        if pos.EntSize > 0:
            self.Lg_Sum += pos.EntSize * pos.EntPrice
            self.Lg_Vol += pos.EntSize
            self.Lg_Avg = self.Lg_Sum/self.Lg_Vol
            self.Lg_EntNum += 1
            self.Lg_MinEntp = min(self.Lg_MinEntp, pos.EntPrice) if self.Lg_MinEntp else pos.EntPrice
            self.Lg_MaxEntp = max(self.Lg_MaxEntp, pos.EntPrice) if self.Lg_MaxEntp else pos.EntPrice
        elif pos.EntSize < 0:
            self.St_Sum += pos.EntSize * pos.EntPrice
            self.St_Vol += pos.EntSize
            self.St_Avg = self.St_Sum / self.St_Vol
            self.St_EntNum += 1
            self.St_MinEntp = min(self.St_MinEntp, pos.EntPrice) if self.St_MinEntp else pos.EntPrice
            self.St_MaxEntp = max(self.St_MaxEntp, pos.EntPrice) if self.St_MaxEntp else pos.EntPrice




class Lspsd(object):
    # ----------------------------------------------------------------------
    def __init__(self, Lgvar, Lgsize, Lgid, Stvar, Stsize, Stid, Lscorr, Lsflg, Sddtm, Offset='close'):
        """Constructor"""
        self.Lgvar = Lgvar
        self.Lgsize = Lgsize
        self.Lgid = Lgid
        self.Stvar = Stvar
        self.Stsize = Stsize
        self.Stid = Stid
        self.Lscorr = Lscorr
        self.Lsflg = Lsflg
        self.Sddtm = Sddtm
        self.Offset = Offset


class Sglsd(object):
    # ----------------------------------------------------------------------
    def __init__(self, Sdvar, Sdsize, Sdid, Sdflg, Sddtm, Offset='close'):
        """Constructor"""
        self.Sdvar = Sdvar
        self.Sdsize = Sdsize
        self.Sdid = Sdid
        self.Sdflg = Sdflg
        self.Sddtm = Sddtm
        self.Offset = Offset


# ----------------------------------------------------------------------
def max_drawdown(Networth_Series):
    Series = Networth_Series[:-1]
    Size = Series.size
    Max = np.zeros(Size)
    Drawdown = np.zeros(Size)
    Drawdown_Duration = np.zeros(Size)
    Recovery_Duration = None
    Max_Drawdown = 0
    Ind = 0

    for t in range(Size):
        Max[t] = max(Max[t - 1], Series[t])
        Drawdown[t] = float(Series[t] - Max[t]) / Max[t]
        if Drawdown[t] < Max_Drawdown:
            Max_Drawdown = Drawdown[t]
            Ind = t
        Drawdown_Duration[t] = (0 if Drawdown[t] >= 0 else Drawdown_Duration[t - 1] + 1)

    if Ind is not 0:
        Temp_Max = map(lambda x: x - Max[Ind], Max[Ind:])
        for i in range(len(Max[Ind:])):
            if Temp_Max[i] > 0:
                Recovery_Duration = i
                break

    return {'Max': Max, 'Max_Drawdown': Drawdown[Ind], 'Drawdown_Duration': Drawdown_Duration[Ind],
            'Recovery_Duration': Recovery_Duration}


# ----------------------------------------------------------------------
def return_metrics(Networth_Series, Trading_Days_Per_Year=242):
    Num_Days = Networth_Series.size
    Daily_Return = (Networth_Series / Networth_Series.shift() - 1)[1:]
    Winning_Rate = Daily_Return[Daily_Return > 0].size / Daily_Return.dropna().size

    Mean_Daily_Return = Daily_Return.mean()
    Annualized_Return = np.power((Mean_Daily_Return + 1), Trading_Days_Per_Year) - 1
    Annualized_Std = Daily_Return.std() * np.sqrt(Trading_Days_Per_Year)
    Sharpe_Ratio = Annualized_Return / Annualized_Std
    Sortino_Ratio = Annualized_Return / (Daily_Return[Daily_Return < 0].std() * np.sqrt(Trading_Days_Per_Year))

    return {'Daily_Return': Daily_Return, 'Annualized_Return': Annualized_Return, 'Annualized_Std': Annualized_Std,
            'Sharpe_Ratio': Sharpe_Ratio, 'Sortino_Ratio': Sortino_Ratio, 'Winning_Rate': Winning_Rate,
            'Num_Days': Num_Days}


# ----------------------------------------------------------------------
def calc_metrics(Networth_Series, Trading_Days_Per_Year=242):
    Drawdown_Metrics_Dict = max_drawdown(Networth_Series)
    Return_Metrics_Dict = return_metrics(Networth_Series, Trading_Days_Per_Year=Trading_Days_Per_Year)
    Drawdown_Metrics_Dict.update(Return_Metrics_Dict)
    Drawdown_Metrics_Dict['Calmar_Ratio'] = Drawdown_Metrics_Dict['Annualized_Return'] / abs(
        Drawdown_Metrics_Dict['Max_Drawdown'])
    return Drawdown_Metrics_Dict


class TSBacktest(object):
    # ----------------------------------------------------------------------
    # def __init__(self, Var, sk_open, sk_high, sk_low, sk_close, sk_volume, sk_time, sk_atr, sk_ckl, TS_Config):
    def __init__(self, Var, quotes, sk_ckl, TS_Config):
        self.Rt_Dir = TS_Config['Rt_Dir']
        self.Result_Dir = self.Rt_Dir + '/TSBT_results/'
        self.Var = Var
        self.Variety_List = [Var]

        # self.sk_open = sk_open
        # self.sk_high = sk_high
        # self.sk_low = sk_low
        # self.sk_close = sk_close
        # self.sk_volume = sk_volume
        # self.sk_time = sk_time
        # self.sk_atr = sk_atr
        # self.sk_ckl = sk_ckl
        self.quotes = quotes
        self.sk_open = quotes['open'].values
        self.sk_high = quotes['high'].values
        self.sk_low = quotes['low'].values
        self.sk_close = quotes['close'].values
        self.sk_volume = quotes['volume'].values
        self.sk_time = quotes['time'].values
        self.sk_atr = quotes['ATR'].values
        self.sk_ckl = sk_ckl

        self.Time_Param = TS_Config['Time_Param']
        self.Start_Date = self.Time_Param[0]
        self.End_Date = self.Time_Param[1]

        self.Return_Panel = None
        self.Return_Metric = {}

        self.OrdMkt_Df = None
        self.OrdLmt_Df = None
        self.OrdStp_Df = None


        self.SdOpen_dic = {}
        self.SdCld_dic = {}

        self.Remids = []  # 已经记录入备用队列的订单号


        # 回测相关
        self.Trade_Date_DT = None
        self.Meta_Csv_Dir = self.Rt_Dir + '/CommodityMetaData.csv'
        Init_Capital = TS_Config['Init_Capital']
        self.Init_Capital = TS_Config['Init_Capital']
        self.SlipT = TS_Config['SlipT']
        self.Free_Money = self.Init_Capital
        self.Networth = 1
        self.Record_Frame = pd.DataFrame([[Init_Capital, 0, Init_Capital, 0, 0]], index=['Init'],
                                         columns=['Free', 'Margin', 'Networth', 'Max_Holding_Ratio','Net_Holding_Ratio'])
        self.Transaction_Rate = pd.Series([0.0] * len(self.Variety_List), index=self.Variety_List)
        self.Transaction_Rate_Same_Day = pd.Series([0.0] * len(self.Variety_List), index=self.Variety_List)
        self.Transaction_Fee = pd.Series([0.0] * len(self.Variety_List), index=self.Variety_List)
        self.Multiplier = pd.Series([1] * len(self.Variety_List), index=self.Variety_List)
        self.Margin_Rate = pd.Series([0.1] * len(self.Variety_List), index=self.Variety_List)
        self.Tick_Size = pd.Series([0.0] * len(self.Variety_List), index=self.Variety_List)
        self.Transaction_Cost = 0
        self.Slippage_Cost = 0
        self.OrdTypSet = TS_Config['OrdTyp']
        self.set_param(self.Meta_Csv_Dir)

        self.LogOrds = pd.DataFrame(
            columns=['OrdID', 'Symbol', 'Size', 'OrdAmount', 'EntPrice', 'Ordtyp', 'EntTime', 'Offset', 'OrdSp', 'OrdTp', 'OrdFlg'])
        self.LogOrdsnum = 0
        self.LogTrds = pd.DataFrame(
            columns=['TrdID', 'Symbol', 'Size', 'TrdAmount', 'TrdPrice', 'TrdTime', 'Offset', 'TrdSp', 'TrdTp', 'TrdFlg'])
        self.LogTrdsnum = 0
        self.LogCldPos = pd.DataFrame(
            columns=['PosID', 'Symbol', 'Size', 'EntAmount', 'EntPrice', 'EntTime', 'EntSp', 'EntTp', 'CldPrice', 'CldTime', 'PAL', 'EntFlg', 'CldFlg'])

        self.Position_List = []
        self.SgnVarPos_Dic = {}  # 仓位更新时统计各个策略的各个品种的持仓
        self.SgnVarLstSdop_Dic = {}  # 各个策略的各个品种最近的开仓信号
        self.SocPos_Dic = {} # 各信号源持仓汇总

        self.Ostpn_Dic = TS_Config['Ostpn_Dic']
        self.Sgnwt_Dic = TS_Config['Sgnwt_Dic']

        self.Opid = 0
        self.MktValue = 0
        self.Long_MktValue = 0
        self.Short_MktValue = 0
        self.Margin = 0
        self.PAL = 0
        self.CldPosition_List = []
        self.CldPAL = 0
        self.LongEnt_Df = None
        self.ShortEnt_Df = None
        self.testname = ''
        self.Ordslogfile = ''
        self.Trdslogfile = ''
        self.CldPoslogfile = ''
        self.NetValuefile = ''
        self.Remark = TS_Config['Remark']

    # ----------------------------------------------------------------------
    def write_to_csv_file(self, csvdir, Item_List):
        with open(csvdir, 'ab+') as Csvfile:
            Csv_Writer = csv.writer(Csvfile, delimiter=',')
            Csv_Writer.writerow(Item_List)
# ----------------------------------------------------------------------
    def set_param(self, Csv_Dir=None):
        self.set_transaction_rate(Csv_Dir)
        self.set_transaction_rate_same_day(Csv_Dir)
        self.set_transaction_fee(Csv_Dir)
        self.set_multiplier(Csv_Dir)
        self.set_margin_rate(Csv_Dir)
        self.set_tick_size(Csv_Dir)

    def set_transaction_rate(self, Csv_Dir, Col_Num=11, Index_Col=0):
        Transaction_Rate = pd.read_csv(Csv_Dir, index_col=Index_Col).iloc[:, Col_Num]
        for x in self.Variety_List:
            self.Transaction_Rate[x] = Transaction_Rate[x.lower()]

    def set_transaction_rate_same_day(self, Csv_Dir, Col_Num=12, Index_Col=0):
        Transaction_Rate_Same_Day = pd.read_csv(Csv_Dir, index_col=Index_Col).iloc[:, Col_Num]
        for x in self.Variety_List:
            self.Transaction_Rate_Same_Day[x] = Transaction_Rate_Same_Day[x.lower()]

    def set_transaction_fee(self, Csv_Dir, Col_Num=10, Index_Col=0):
        Transaction_Fee = pd.read_csv(Csv_Dir, index_col=Index_Col).iloc[:, Col_Num]
        for x in self.Variety_List:
            self.Transaction_Fee[x] = Transaction_Fee[x.lower()]

    def set_multiplier(self, Csv_Dir, Col_Num=4, Index_Col=0):
        Multiplier = pd.read_csv(Csv_Dir, index_col=Index_Col).iloc[:, Col_Num]
        for x in self.Variety_List:
            self.Multiplier[x] = Multiplier[x.lower()]

    def set_margin_rate(self, Csv_Dir, Col_Num=7, Index_Col=0):
        Margin_Rate = pd.read_csv(Csv_Dir, index_col=Index_Col).iloc[:, Col_Num]
        for x in self.Variety_List:
            self.Margin_Rate[x] = Margin_Rate[x.lower()]

    def set_tick_size(self, Csv_Dir, Col_Num=3, Index_Col=0):
        Tick_Size = pd.read_csv(Csv_Dir, index_col=Index_Col).iloc[:, Col_Num]
        for x in self.Variety_List:
            self.Tick_Size[x] = Tick_Size[x.lower()]

    def sendord(self, Symbol, Size, Amount, Price, OrdTyp='Mkt', EntTime=None, Offset='open', EntSki=None, OrdSp = None, OrdTp = None, Psn=None, Msn = None, Ordid=None, OrdFlg='NB'):
        # print 'sendord:', Symbol, Size, Amount, Price, OrdTyp, EntTime, Offset, OrdSp, OrdTp, OrdFlg
        self.LogOrdsnum += 1
        # self.LogOrds.loc[self.LogOrdsnum, :] = [self.LogOrdsnum, Symbol, Size, Amount, Price, OrdTyp, EntTime, Offset, OrdSp, OrdTp, OrdFlg]
        self.write_to_csv_file(self.Ordslogfile, [self.LogOrdsnum, Symbol, Size, Amount, Price, OrdTyp, EntTime, Offset, OrdSp, OrdTp, OrdFlg])
        if OrdTyp == 'Mkt':
            ords = self.OrdMkt_Df.loc[Symbol, 'ords']
            neword = Order(Symbol, Size, Amount, Price, OrdTyp, EntTime, Offset, OrdSki=EntSki, OrdSp = OrdSp, OrdTp = OrdTp, Psn=Psn, Msn = Msn, Ordid=Ordid, OrdFlg=OrdFlg)
            if ords == ords:
                self.OrdMkt_Df.loc[Symbol, 'ords'].append(neword)
            else:
                self.OrdMkt_Df.loc[Symbol, 'ords'] = [neword]
        elif OrdTyp == 'Lmt':
            ords = self.OrdLmt_Df.loc[Symbol, 'ords']
            neword = Order(Symbol, Size, Amount, Price, OrdTyp, EntTime, Offset, OrdSki=EntSki, OrdSp = OrdSp, OrdTp = OrdTp, Psn=Psn, Msn = Msn, Ordid=Ordid, OrdFlg=OrdFlg)
            if ords == ords:
                self.OrdLmt_Df.loc[Symbol, 'ords'].append(neword)
            else:
                self.OrdLmt_Df.loc[Symbol, 'ords'] = [neword]
        elif OrdTyp == 'Stp':
            ords = self.OrdStp_Df.loc[Symbol, 'ords']
            neword = Order(Symbol, Size, Amount, Price, OrdTyp, EntTime, Offset, OrdSki=EntSki, OrdSp = OrdSp, OrdTp = OrdTp, Psn=Psn, Msn = Msn, Ordid=Ordid, OrdFlg=OrdFlg)
            if ords == ords:
                self.OrdStp_Df.loc[Symbol, 'ords'].append(neword)
            else:
                self.OrdStp_Df.loc[Symbol, 'ords'] = [neword]

    def newposition(self, OpenTrd):
        newpos = Position(OpenTrd)
        newpos.MktValue = OpenTrd.TrdSize * OpenTrd.TrdPrice * self.Multiplier[OpenTrd.Symbol]

        # newpos.Margin = abs(newpos.MktValue) * self.Margin_Rate[OpenTrd.Symbol]
        # self.MktValue += newpos.MktValue
        # self.Long_MktValue += max(0, newpos.MktValue)
        # self.Short_MktValue += min(0, newpos.MktValue)
        # self.Margin += newpos.Margin
        # self.PAL += newpos.PAL

        self.Position_List.append(newpos)
        newfee_cost = abs(OpenTrd.TrdSize) * self.Transaction_Fee[OpenTrd.Symbol] + abs(newpos.MktValue) * self.Transaction_Rate[OpenTrd.Symbol]
        # newfee_cost = 0
        self.Transaction_Cost += newfee_cost
        self.CldPAL -= newfee_cost

        if newpos.MktValue > 0:
            self.LongEnt_Df.at[OpenTrd.Symbol, 'entnum'] += 1
            self.LongEnt_Df.at[OpenTrd.Symbol, 'size'] += OpenTrd.TrdSize
            self.LongEnt_Df.at[OpenTrd.Symbol, 'mktvalue'] += newpos.MktValue
        elif newpos.MktValue < 0:
            self.ShortEnt_Df.at[OpenTrd.Symbol, 'entnum'] += 1
            self.ShortEnt_Df.at[OpenTrd.Symbol, 'size'] += OpenTrd.TrdSize
            self.ShortEnt_Df.at[OpenTrd.Symbol, 'mktvalue'] += newpos.MktValue

        pass

    def closeposition(self, CldTrd):  # 根据开仓单号来平仓持仓
        Tocldposlist = []
        for pos in self.Position_List:
            if pos.Posid == CldTrd.Trdid:
                if CldTrd.TrdSize == 0:
                    break
                if pos.EntSize * CldTrd.TrdSize < 0:
                    if abs(pos.EntSize) <= abs(CldTrd.TrdSize):
                        pos.CldPrice = CldTrd.TrdPrice
                        pos.CldTime = CldTrd.TrdTime
                        pos.PAL = pos.EntSize * (pos.CldPrice - pos.EntPrice) * self.Multiplier[pos.Symbol]
                        pos.CldFlg = CldTrd.TrdFlg
                        Tocldposlist.append(pos)
                        CldTrd.TrdSize += pos.EntSize
                        newfee_cost = abs(pos.EntSize) * self.Transaction_Fee[pos.Symbol] + abs(
                            pos.EntSize * pos.CldPrice * self.Multiplier[pos.Symbol]) * self.Transaction_Rate[pos.Symbol]
                        # newfee_cost = 0
                        self.Transaction_Cost += newfee_cost
                        self.CldPAL -= newfee_cost

                    elif abs(pos.EntSize) > abs(CldTrd.TrdSize):
                        pos.EntSize += CldTrd.TrdSize
                        newcldtrd = Trdord(pos.Symbol, - CldTrd.TrdSize, pos.EntPrice, pos.EntTime, Offset='open', Trdski=pos.EntSki,
                                           TrdSp=pos.EntSp, TrdTp=pos.EntTp, Psn=pos.Psn, Msn=pos.Msn, Trdid=pos.Posid, TrdFlg=pos.EntFlg)
                        newcldpos = Position(newcldtrd)
                        newcldpos.CldPrice = CldTrd.TrdPrice
                        newcldpos.CldTime = CldTrd.TrdTime
                        newcldpos.PAL = newcldpos.EntSize * (newcldpos.CldPrice - pos.EntPrice) * self.Multiplier[newcldpos.Symbol]
                        newcldpos.CldFlg = CldTrd.TrdFlg
                        self.CldPosition_List.append(newcldpos)
                        self.CldPAL += newcldpos.PAL
                        newfee_cost = abs(newcldtrd.TrdSize) * self.Transaction_Fee[newcldtrd.Symbol] + abs(
                            newcldtrd.TrdSize * newcldpos.CldPrice * self.Multiplier[newcldtrd.Symbol]) * self.Transaction_Rate[newcldtrd.Symbol]
                        # newfee_cost = 0
                        self.Transaction_Cost += newfee_cost
                        self.CldPAL -= newfee_cost
                break
        for pos in Tocldposlist:
            self.CldPosition_List.append(pos)
            self.CldPAL += pos.PAL
            self.Position_List.remove(pos)

            if pos.EntSize > 0:
                self.LongEnt_Df.at[pos.Symbol, 'entnum'] -= 1
                self.LongEnt_Df.at[pos.Symbol, 'size'] -= pos.EntSize
                self.LongEnt_Df.at[pos.Symbol, 'mktvalue'] -= pos.MktValue
            if pos.EntSize < 0:
                self.ShortEnt_Df.at[pos.Symbol, 'entnum'] -= 1
                self.ShortEnt_Df.at[pos.Symbol, 'size'] -= pos.EntSize
                self.ShortEnt_Df.at[pos.Symbol, 'mktvalue'] -= pos.MktValue

    def update_posinfo(self, ski):  # 更新统计持仓、盈亏、资产、保证金、杠杆水平
        sk_close = self.sk_close
        sk_time  = self.sk_time
        idtime = str(sk_time[ski])[:10]
        iski = ski

        self.MktValue = 0
        self.Long_MktValue = 0
        self.Short_MktValue = 0
        self.Margin = 0
        self.PAL = 0
        self.LongEnt_Df['mktvalue'] = 0
        self.ShortEnt_Df['mktvalue'] = 0
        self.SgnVarPos_Dic = {}
        self.SocPos_Dic = {}
        nullpvarlist = []  # 记录空值合约
        for pos in self.Position_List:
            Symbol = pos.Symbol
            Flag = pos.EntFlg
            Lastprice = sk_close[ski]
            pos.MktValue = pos.EntSize * Lastprice * self.Multiplier[Symbol]
            pos.Margin = abs(pos.MktValue) * self.Margin_Rate[Symbol]
            pos.PAL = pos.EntSize * (Lastprice - pos.EntPrice) * self.Multiplier[Symbol]
            if pos.PAL != pos.PAL:
                nullpvarlist.append(Symbol)
            self.MktValue += pos.MktValue
            self.Long_MktValue += max(0, pos.MktValue)
            self.Short_MktValue += min(0, pos.MktValue)
            self.Margin += pos.Margin
            self.PAL += pos.PAL
            if pos.MktValue > 0:
                self.LongEnt_Df['mktvalue'] += pos.MktValue
                self.ShortEnt_Df['mktvalue'] += pos.MktValue

            #------------------------------------------------------------统计各子策略中各品种持仓信息
            sgnid = Flag.split('_')[0]
            if sgnid in self.SgnVarPos_Dic:
                self.SgnVarPos_Dic[sgnid].addpos(pos)
            else:
                self.SgnVarPos_Dic[sgnid] = Sgnposinf(sgnid, Symbol)
                self.SgnVarPos_Dic[sgnid].addpos(pos)

            socna = Flag.split('-')[1]
            if socna in self.SocPos_Dic:
                if sgnid in self.SocPos_Dic[socna]:
                    self.SocPos_Dic[socna][sgnid].append(pos)
                else:
                    self.SocPos_Dic[socna][sgnid]=[pos]
            else:
                self.SocPos_Dic[socna]= {sgnid: [pos]}
            #------------------------------------------------------------------------------
        self.Free_Money = self.Init_Capital + self.PAL + self.CldPAL - self.Margin
        if self.CldPAL !=self.CldPAL:
            print 'mkv nan'
        self.Networth = self.Init_Capital + self.PAL + self.CldPAL
        maxRatio = (self.Long_MktValue - self.Short_MktValue) / self.Networth
        netRatio = (self.MktValue) / self.Networth
        self.Record_Frame.loc[idtime, :] = [self.Free_Money, self.Margin, self.Networth, maxRatio, netRatio]

        if len(nullpvarlist)>0:
            nullpvarlist.insert(0, idtime)
            self.write_to_csv_file(r'D:\temp\nullvar.csv', nullpvarlist)
        # print Date, 'Networth: ', self.Networth, 'maxRatio: ',maxRatio

    def newtrd(self, Ord, trdsize, trdp, trdtime, trdski=None):
        if Ord.Offset == 'open':
            self.Opid += 1
            Trd = Trdord(Ord.Symbol, trdsize, trdp, trdtime, Ord.Offset, trdski, Ord.OrdSp, Ord.OrdTp, Ord.Psn, Ord.Msn, self.Opid, Ord.OrdFlg)
            self.LogTrdsnum += 1
            # self.LogTrds.loc[self.LogTrdsnum, :] = [self.LogTrdsnum, Ord.Symbol, trdsize, Ord.OrdAmount, trdp, trdtime, Ord.Offset, Ord.OrdSp, Ord.OrdTp, Ord.OrdFlg]
            self.write_to_csv_file(self.Trdslogfile, [self.LogTrdsnum, Ord.Symbol, trdsize, Ord.OrdAmount, trdp, trdtime, Ord.Offset, Ord.OrdSp, Ord.OrdTp, Ord.OrdFlg])
            self.newposition(Trd)
        elif Ord.Offset == 'close':
            Trd = Trdord(Ord.Symbol, trdsize, trdp, trdtime, Ord.Offset, trdski, TrdSp = None, TrdTp = None, Psn = None, Msn = None, Trdid = Ord.Ordid, TrdFlg = Ord.OrdFlg)
            self.LogTrdsnum += 1
            # self.LogTrds.loc[self.LogTrdsnum, :] = [self.LogTrdsnum, Ord.Symbol, trdsize, Ord.OrdAmount, trdp, trdtime, Ord.Offset, None, None, Ord.OrdFlg]
            self.write_to_csv_file(self.Trdslogfile, [self.LogTrdsnum, Ord.Symbol, trdsize, Ord.OrdAmount, trdp, trdtime, Ord.Offset, None, None, Ord.OrdFlg])
            self.closeposition(Trd)

    # -------------------------------------------------------------------------------------------------------
    def save_result(self, Result_Dir=None):
        if not Result_Dir:
            Result_Dir = self.Result_Dir
        self.Return_Panel.Return.plot()
        plt.savefig(Result_Dir + '/Return.png')
        plt.close('all')
        #self.to_h5(Result=True)

        with open(Result_Dir + '/Return_Metric.csv', 'wb') as Csvfile:
            Row_Writer = csv.writer(Csvfile, delimiter=',')
            Header_Row = ['Num_Days', 'Annualized_Return', 'Annualized_Std', 'Max_Drawdown', 'Sharpe_Ratio']
            Row_Writer.writerow(Header_Row)
            Row_Writer.writerow([self.Return_Metric[x] for x in Header_Row])

    def Show_SaveResult(self):
        self.Record_Frame.to_csv(self.NetValuefile)
        PosID = 0
        with open(self.CldPoslogfile, 'ab+') as Csvfile:
            Csv_Writer = csv.writer(Csvfile, delimiter=',')
            # Csv_Writer.writerow(['PosID','Symbol','Size','EntAmount','EntPrice','EntTime','EntSp','EntTp','CldPrice','CldTime','PAL','EntFlg'])
            for pos in self.CldPosition_List:
                PosID += 1
                Csv_Writer.writerow(
                    [PosID, pos.Symbol, pos.EntSize, pos.EntSize * pos.EntPrice, pos.EntPrice, pos.EntTime, pos.EntSp, pos.EntTp, pos.CldPrice, pos.CldTime, pos.PAL, pos.EntFlg, pos.CldFlg])

        Networth_Series = self.Record_Frame['Networth']
        Asmreport = calc_metrics(Networth_Series)

        Fact_cfg_str = 'grst'
        Rep_Dic = collections.OrderedDict()

        Rep_Dic['Time_Param'] = self.Time_Param
        Rep_Dic['SlipT'] = self.SlipT
        Rep_Dic['OrdTypSet'] = self.OrdTypSet

        Rep_Dic['Init_Capital'] = self.Init_Capital,
        Rep_Dic['Final_Networth'] = self.Networth
        Rep_Dic['Final_PAL'] = self.Networth - self.Init_Capital
        Rep_Dic['Final_PAL%'] = self.Networth / self.Init_Capital
        Rep_Dic['Trdsnum'] = self.LogTrdsnum
        Rep_Dic['Fee_Cost'] = self.Transaction_Cost

        Rep_Dic['Annualized_Return'] = Asmreport['Annualized_Return']
        Rep_Dic['Annualized_Std'] = Asmreport['Annualized_Std']
        Rep_Dic['Max_Drawdown'] = Asmreport['Max_Drawdown']
        Rep_Dic['Num_Days'] = Asmreport['Num_Days']
        Rep_Dic['Drawdown_Duration'] = Asmreport['Drawdown_Duration']
        Rep_Dic['Recovery_Duration'] = Asmreport['Recovery_Duration']
        Rep_Dic['Winning_Rate'] = Asmreport['Winning_Rate']
        Rep_Dic['Sharpe_Ratio'] = Asmreport['Sharpe_Ratio']
        Rep_Dic['Sortino_Ratio'] = Asmreport['Sortino_Ratio']
        Rep_Dic['Calmar_Ratio'] = Asmreport['Calmar_Ratio']
        Rep_Dic['Remark'] = self.Remark

        with open(self.Result_Dir + '/' + self.testname + '_Report' + '.json', 'a') as Reportfile:
            json.dump(Rep_Dic, Reportfile, ensure_ascii=False, indent=4)

        matplotlib.style.use('ggplot')
        fig, (ax1, ax2) = plt.subplots(2, sharex=True)
        Res_Networth = self.Record_Frame.loc[:, ['Networth']]
        Res_MkvRatio = self.Record_Frame.loc[:, ['Max_Holding_Ratio', 'Net_Holding_Ratio']]

        Res_Networth.plot(ax=ax1, title='Total Networth')
        Res_MkvRatio.plot(ax=ax2, title='MkvRatio')
        xdate = [itime for itime in Res_Networth.index]
        def mydate(x, pos):
            try:
                return xdate[int(x)]
            except IndexError:
                return ''
        ax1.xaxis.set_major_formatter( ticker.FuncFormatter(mydate))
        plt.grid()
        plt.savefig(self.Result_Dir + '/' + self.testname + '_' + Fact_cfg_str + '.png')
        # plt.show()

    def initbacktest(self, ):
        if not (os.path.exists(self.Result_Dir)):
            os.makedirs(self.Result_Dir)

        self.testname = 'TS_' + strftime("%Y-%m-%d_%H_%M_%S", localtime())
        self.Ordslogfile = self.Result_Dir + '/' + self.testname + '_Ords' + '.csv'
        self.Trdslogfile = self.Result_Dir + '/' + self.testname + '_Trds' + '.csv'
        self.CldPoslogfile = self.Result_Dir + '/' + self.testname + '_CldPos' + '.csv'
        self.NetValuefile = self.Result_Dir + '/' + self.testname + '_NetValue' + '.csv'
        self.write_to_csv_file(self.Ordslogfile, self.LogOrds.columns)
        self.write_to_csv_file(self.Trdslogfile, self.LogTrds.columns)
        self.write_to_csv_file(self.CldPoslogfile, self.LogCldPos.columns)

        self.OrdMkt_Df = pd.DataFrame(index=self.Variety_List, columns=['ords'])
        self.OrdLmt_Df = pd.DataFrame(index=self.Variety_List, columns=['ords'])
        self.OrdStp_Df = pd.DataFrame(index=self.Variety_List, columns=['ords'])

        self.LongEnt_Df = pd.DataFrame([[0, 0, 0]], index=self.Variety_List, columns=['entnum', 'size', 'mktvalue'])
        self.ShortEnt_Df = pd.DataFrame([[0, 0, 0]], index=self.Variety_List, columns=['entnum', 'size', 'mktvalue'])

    def sgntotrd(self, ski, intedsgn):
        # --撮合市价单
        # --撮合限价单
        # --撮合止损单
        # --统计持仓、盈亏、资产、保证金、杠杆水平
        # --根据因子信号设置委托单
        sk_open = self.sk_open
        sk_high = self.sk_high
        sk_low = self.sk_low
        sk_close = self.sk_close
        sk_volume = self.sk_volume
        sk_time = self.sk_time
        sk_atr = self.sk_atr
        atr = sk_atr[ski] * sk_close[ski]
        sk_ckl = self.sk_ckl
        #-----------------------------------其他因子，包括外部周期添加的因子---------------
        if 'disrst' in self.quotes.columns:
            sk_disrst = self.quotes['disrst'].values
        if 'disrst_d' in self.quotes.columns:
            sk_disrst_d = self.quotes['disrst_d'].values

        #-----------------------------------------------------------------
        stridtm = pd.Timestamp((sk_time[ski])).strftime('%Y-%m-%d %H:%M:%S')
        print 'backtest: trade on ', stridtm
        # print stridtm
        idtime = stridtm[:]
        iski  = ski # str(sk_time[ski])[:10]
        ihigh = sk_high[ski]
        if '2014-11-17' in stridtm:
            print ' iski:', iski, 'crtdate:', idtime[:10], 'crttime:', stridtm



        '''
        rstdir = intedsgn.rstdir
        crtbbl = None
        prebbl = None
        crtttl = None
        prettl = None
        crtsal = None
        presal = None
        if len(intedsgn.sals_dic)>0:
            crtsal = intedsgn.sals_dic.values()[-1]
        if len(intedsgn.sals_dic)>1:
            presal = intedsgn.sals_dic.values()[-2]

        if len(intedsgn.bbls_dic)>0:
            crtbbl = intedsgn.bbls_dic.values()[-1]['rdl']
        if len(intedsgn.bbls_dic)>1:
            prebbl = intedsgn.bbls_dic.values()[-2]['rdl']

        if len(intedsgn.ttls_dic)>0:
            crtttl = intedsgn.ttls_dic.values()[-1]['rdl']
        if len(intedsgn.ttls_dic)>1:
            prettl = intedsgn.ttls_dic.values()[-2]['rdl']

        if crtsal:
            crtsal.trgsgn(sk_open, sk_high, sk_low, sk_close, sk_atr, sk_ckl, ski)
            intedsgn.addsgn(crtsal.socna, crtsal.trpkops, crtsal.trpcsts, crtsal.trpctps, 0)
        if presal:
            presal.trgsgn(sk_open, sk_high, sk_low, sk_close, sk_atr, sk_ckl, ski)
            intedsgn.addsgn(presal.socna, presal.trpkops, presal.trpcsts, presal.trpctps, 1)
        if crtbbl:
            crtbbl.trgsgn(sk_open, sk_high, sk_low, sk_close, sk_atr, sk_ckl, ski)
            intedsgn.addsgn(crtbbl.socna, crtbbl.trpkops, crtbbl.trpcsts, crtbbl.trpctps, 0)
        if crtttl:
            crtttl.trgsgn(sk_open, sk_high, sk_low, sk_close, sk_atr, sk_ckl, ski)
            intedsgn.addsgn(crtttl.socna, crtttl.trpkops, crtttl.trpcsts, crtttl.trpctps, 0)        
        
        if prebbl:
            prebbl.trgsgn(sk_open, sk_high, sk_low, sk_close, sk_atr, sk_ckl, ski)
            intedsgn.addsgn(prebbl.socna, prebbl.trpkops, prebbl.trpcsts, prebbl.trpctps, 1)
        if prettl:
            prettl.trgsgn(sk_open, sk_high, sk_low, sk_close, sk_atr, sk_ckl, ski)
            intedsgn.addsgn(prettl.socna, prettl.trpkops, prettl.trpcsts, prettl.trpctps, 1)

        if len(intedsgn.uprstsas)>0:
            crtupr = intedsgn.uprstsas.values()[-1]
        else:
            crtupr = None
        if len(intedsgn.dwrstsas)>0:
            crtdwr = intedsgn.dwrstsas.values()[-1]
        else:
            crtdwr = None


        subrst = intedsgn.subrst
        intedsgn.intsgn()
        sgnkops= intedsgn.isgnkop
        '''




        # ----------------------------------------------------------------------------------------------------撮合订单
        if True:
            CurOrdMkt = self.OrdMkt_Df.dropna(how='any')
            if not CurOrdMkt.empty:
                for Var, Ords in CurOrdMkt.iterrows():
                    # 过滤行情缺失
                    if sk_open[ski] > 0 and sk_close[ski] > 0 and sk_low[ski] > 0 and sk_high[ski] > 0:
                        pass
                    else:
                        print 'cross CurOrdMkt error: ', Var, sk_time[ski]
                        continue
                    for Ord in Ords['ords']:
                        try:
                            if Ord.OrdSize != 0:
                                trdsize = Ord.OrdSize
                            else:
                                trdsize = int(Ord.OrdAmount / (sk_open[ski] * self.Multiplier[Var]))
                            if trdsize > 0:
                                trdp = sk_open[ski] + self.SlipT * self.Tick_Size[Var]
                            elif trdsize < 0:
                                trdp = sk_open[ski] - self.SlipT * self.Tick_Size[Var]
                            else:
                                print 'cross CurOrdMkt error: ', Var, idtime, ' trdp =', trdp
                                continue
                            self.newtrd(Ord, trdsize, trdp, idtime, iski)
                        except Exception, e:
                            print 'cross CurOrdMkt', e.message
                            pass
            # ------------------------------------------------------------
            CurOrdStp = self.OrdStp_Df.dropna(how='any')
            if not CurOrdStp.empty:
                for Var, Ords in CurOrdStp.iterrows():
                    # 过滤行情缺失
                    if sk_open[ski] > 0 and sk_close[ski] > 0 and sk_low[ski] > 0 and sk_high[ski] > 0:
                        pass
                    else:
                        print 'cross CurOrdStp error: ', Var, idtime
                        continue
                    for Ord in Ords['ords']:
                        try:
                            if Ord.OrdSize != 0:
                                trdsize = Ord.OrdSize
                            else:
                                trdsize = Ord.OrdAmount / (Ord.OrdPrice * self.Multiplier[Var])

                            if trdsize > 0 and sk_high[ski] >= Ord.OrdPrice:
                                trdp = max(Ord.OrdPrice, sk_open[ski])
                            elif trdsize < 0 and sk_low[ski] <= Ord.OrdPrice:
                                trdp = min(Ord.OrdPrice, sk_open[ski])
                            else:
                                continue
                            self.newtrd(Ord, trdsize, trdp, idtime, iski)
                        except Exception, e:
                            print 'cross CurOrdStp', e.message
                            pass

            # ------------------------------------------------------------
            CurOrdLmt = self.OrdLmt_Df.dropna(how='any')
            if not CurOrdLmt.empty:
                for Var, Ords in CurOrdLmt.iterrows():
                    # 过滤行情缺失
                    if sk_open[ski] > 0 and sk_close[ski] > 0 and sk_low[ski] > 0 and sk_high[ski] > 0:
                        pass
                    else:
                        print 'cross CurOrdLmt error: ', Var, idtime
                        continue
                    for Ord in Ords['ords']:
                        try:
                            if Ord.OrdSize != 0:
                                trdsize = Ord.OrdSize
                            else:
                                trdsize = Ord.OrdAmount / (Ord.OrdPrice * self.Multiplier[Var])

                            if trdsize > 0 and Ord.OrdPrice >= sk_low[ski]:
                                trdp = min(Ord.OrdPrice, sk_open[ski])
                            elif trdsize < 0 and Ord.OrdPrice <= sk_high[ski]:
                                trdp = max(Ord.OrdPrice, sk_open[ski])
                            else:
                                continue
                            self.newtrd(Ord, trdsize, trdp, idtime, iski)
                        except Exception, e:
                            print 'cross CurOrdLmt', e.message
                            pass


        self.update_posinfo(ski)
        # ------------------------------------------------------------
        self.OrdMkt_Df[:] = np.nan
        self.OrdLmt_Df[:] = np.nan
        self.OrdStp_Df[:] = np.nan
        self.SdCld_dic = {}
        self.SdOpen_dic = {}

        sekops = intedsgn.skatsel.trpkops
        etkops = intedsgn.skatetl.trpkops
        rstdir = intedsgn.mafs['rstdir']
        if len(intedsgn.mafs['upsas']) > 0:
            crtupr = intedsgn.mafs['upsas'].values()[-1]
        else:
            crtupr = None
        if len(intedsgn.mafs['dwsas']) > 0:
            crtdwr = intedsgn.mafs['dwsas'].values()[-1]
        else:
            crtdwr = None

        intedsgn.cmbsgn(self.SocPos_Dic)

        # --------------------------------------------------------平仓逻辑 止损 止盈
        for socna, sgnpos in self.SocPos_Dic.iteritems():
            for sgnid, poslist in sgnpos.iteritems():
                for pos in poslist:
                    entski = pos.EntSki
                    entsize = pos.EntSize
                    entprice = pos.EntPrice
                    entflg = pos.EntFlg
                    var = pos.Symbol
                    psn = pos.Psn
                    msn = pos.Msn
                    sgnna = entflg
                    # -------------------止损单
                    sdsp = pos.EntSp
                    sdflg = pos.SpFlg
                    # --------------------------平保止损
                    pbsp = None
                    if psn:
                        if entsize > 0 and sk_close[ski] >= entprice + psn * atr:
                            pbsp = entprice + 0.5 * atr
                        elif entsize < 0 and sk_close[ski] <= entprice - psn * atr:
                            pbsp = entprice - 0.5 * atr

                    # --------------------------移动止损
                    msp = None
                    if msn:
                        if msn>1:
                            # --------------------------简单移动止损
                            if entsize > 0 and sdsp and sdsp < sk_close[ski] - msn * atr and entprice < sk_close[ski] - msn * atr:
                                msp = sk_close[ski] - msn * atr
                            elif entsize < 0 and sdsp and sdsp > sk_close[ski] + msn * atr and entprice > sk_close[ski] + msn * atr:
                                msp = sk_close[ski] + msn * atr
                        else:
                            # --------------------------基于sads的移动止损
                            if entsize > 0 and rstdir > 0 and crtupr:
                                rsti = crtupr.values()[-1].rsti
                                if rsti:
                                    msp = sk_open[rsti] - 0.4 * atr
                            elif entsize < 0 and rstdir < 0 and crtdwr:
                                rsti = crtdwr.values()[-1].rsti
                                if rsti:
                                    msp = sk_open[rsti] + 0.4 * atr

                    # --------------------------信号止损
                    sgnbs = None
                    #---------------------------------
                    sgnsp = None
                    spflg = ''
                    if sgnbs:
                        if sgnbs.mark and entski > sgnbs.mark:
                            sgnsp = sgnbs.sdsp
                            spflg = sgnbs.sgnna

                    # --------------------------------------
                    if entsize > 0:
                        if not sdsp or (pbsp and sdsp < pbsp):
                            sdsp = pbsp
                            sdflg = 'pbsp'
                        if not sdsp or (msp and sdsp < msp):
                            sdsp = msp
                            sdflg = 'msp'
                        if not sdsp or (sgnsp and sdsp < sgnsp):
                            sdsp = sgnsp
                            sdflg = spflg

                    elif entsize < 0:
                        if not sdsp or (pbsp and sdsp > pbsp):
                            sdsp = pbsp
                            sdflg = 'pbsp'
                        if not sdsp or (msp and sdsp > msp):
                            sdsp = msp
                            sdflg = 'msp'
                        if not sdsp or (sgnsp and sdsp > sgnsp):
                            sdsp = sgnsp
                            sdflg = spflg

                    if sdsp and abs(sdsp - sk_close[ski]) < sk_atr[ski] * sk_close[ski] * 6:
                        self.sendord(var, -entsize, 0, sdsp, 'Stp', idtime, Offset='close', EntSki=iski, Ordid=pos.Posid, OrdFlg=sdflg)
                        pos.EntSp = sdsp
                        pos.SpFlg = sdflg
                    # --------------------限价平仓止盈单
                    sdtp = None

                    if True or not sdtp:
                        sdtp = pos.EntTp
                        sdflg = 'tp0'
                    if sdtp and abs(sdtp - sk_close[ski]) < sk_atr[ski] * sk_close[ski] * 6:
                        self.sendord(var, -entsize, 0, sdtp, 'Lmt', idtime, Offset='close', EntSki=iski, Ordid=pos.Posid, OrdFlg=sdflg)

        # --------------------------------------------------------开仓逻辑
        for socna, sgnkops in intedsgn.cmbkops.iteritems():
            for sgnid, koplist in sgnkops.iteritems():
                for kop in koplist:
                    var = self.Var
                    sgnna= kop.sgnna
                    sdop = kop.sdop
                    sdsp = kop.sdsp
                    sdtp = kop.sdtp
                    psn = kop.psn
                    msn = kop.msn
                    if kop.bsdir > 0:
                        stp = sdop - sdsp if sdsp else None
                        tpl = sdtp - sdop if sdtp else None
                    else:
                        stp = -sdop + sdsp if sdsp else None
                        tpl = -sdtp + sdop if sdtp else None

                    if abs(sdop - sk_close[ski]) > sk_atr[ski] * sk_close[ski] * 6:
                        continue

                    etcn = 1
                    iMsp = self.Networth * 0.1 / etcn
                    if iMsp != iMsp:
                        continue
                    imsize = round(iMsp * 1.0 / sdop / self.Multiplier[var])  # 单次开仓最大用1倍杠杆
                    # 通过风险比例分配策略下单量
                    iRsp = iMsp * 0.01   # 单次风险最大 1%
                    perstp = stp * self.Multiplier[var] if stp else None
                    ifsize = round(iRsp / perstp) if perstp else None

                    entsize = min(ifsize, imsize) if ifsize else imsize

                    # entsize = imsize
                    entsize = entsize * kop.bsdir
                    ordtyp = kop.ordtyp

                    self.sendord(var, entsize, 0, sdop, ordtyp, idtime, Offset='open', EntSki=iski, OrdSp=sdsp, OrdTp=sdtp, Psn=psn, Msn=msn,
                                 OrdFlg=sgnna)

        '''        
        # --------------------------------------------------------平仓逻辑 止损 止盈
        for pos in self.Position_List:
            entski = pos.EntSki
            entsize = pos.EntSize
            entprice = pos.EntPrice
            entflg  = pos.EntFlg
            var     = pos.Symbol
            psn = pos.Psn
            msn = pos.Msn

            sgnna =  entflg
            sgntyp = sgnna.split('-')[0]
            socna  = sgnna.split('-')[1]
            soctyp = socna.split('_')[0]
            sgnid  = sgntyp + '-' + soctyp
            # -------------------止损单
            sdsp = pos.EntSp
            sdflg = pos.SpFlg
            # --------------------------平保止损
            pbsp = None
            if psn:
                if entsize>0 and sk_close[ski] >= entprice + psn * atr:
                    pbsp = entprice + 0.5 * atr
                elif entsize<0 and sk_close[ski] <= entprice - psn * atr:
                    pbsp = entprice - 0.5 * atr

            # --------------------------基于sads的移动止损
            msp = None
            if msn:
                if entsize > 0 and rstdir>0 and crtupr:
                    rsti = crtupr.values()[-1].rsti
                    if rsti:
                        msp = sk_open[rsti] - 0.4* atr
                elif entsize < 0 and rstdir<0 and crtdwr:
                    rsti = crtdwr.values()[-1].rsti
                    if rsti:
                        msp = sk_open[rsti] + 0.4* atr
            # --------------------------信号止损
            sgnbs = None
            if 'tdk' in sgnna:
                fsgnna = sgnna.replace('tdk', 'cst')
                soctdl = None
                if socna in intedsgn.bbls_dic:
                    soctdl = intedsgn.bbls_dic[socna]['mdl']
                elif socna in intedsgn.ttls_dic:
                    soctdl = intedsgn.ttls_dic[socna]['mdl']
                elif socna in intedsgn.sals_dic:
                    soctdl = intedsgn.sals_dic[socna]

                if soctdl:
                    soctdl.trgsgn(sk_open, sk_high, sk_low, sk_close, sk_atr, sk_ckl, ski)
                    if fsgnna in soctdl.trpcsts:
                        sgnbs = soctdl.trpcsts[fsgnna]
            else:
                # sgnbs = intedsgn.samsocsgn(self, sgnna, sgnost='cst', frech=0)
                sgnbs = None #intedsgn.simsocsgn(sgnna, sgnost='cst', frech=0)

            sgnsp = None
            spflg = ''
            if  sgnbs:
                if sgnbs.mark and entski > sgnbs.mark:
                    sgnsp = sgnbs.sdsp
                    spflg = sgnbs.sgnna

            #--------------------------------------
            if entsize>0:
                if not sdsp or ( pbsp and sdsp < pbsp ):
                    sdsp = pbsp
                    sdflg = 'pbsp'
                if not sdsp or ( msp and sdsp < msp ):
                    sdsp = msp
                    sdflg = 'msp'
                if not sdsp or ( sgnsp and sdsp < sgnsp ):
                    sdsp = sgnsp
                    sdflg = spflg

            elif entsize<0:
                if not sdsp or ( pbsp and sdsp > pbsp ):
                    sdsp = pbsp
                    sdflg = 'pbsp'
                if not sdsp or ( msp and sdsp > msp ):
                    sdsp = msp
                    sdflg = 'msp'
                if not sdsp or ( sgnsp and sdsp > sgnsp ):
                    sdsp = sgnsp
                    sdflg = spflg

            if sdsp and abs(sdsp - sk_close[ski]) < sk_atr[ski] * sk_close[ski] * 6:
                self.sendord(var, -entsize, 0, sdsp, 'Stp', idtime, Offset='close', EntSki=iski, Ordid=pos.Posid, OrdFlg=sdflg)
                pos.EntSp = sdsp
                pos.SpFlg = sdflg
            # --------------------限价平仓止盈单
            sdtp = None

            # sgnbs = intedsgn.simsocsgn(sgnna, sgnost='ctp', frech=0)
            # if sgnbs:
            #     sdtp = sgnbs.sdtp
            #     sdflg = sgnbs.sgnna
            # else:
            #     sgnbs = intedsgn.difsocsgn(sgnna, sgnost='kop', frech=0)
            #     if sgnbs:
            #         sdtp = sgnbs.sdop
            #         sdflg = sgnbs.sgnna

            if True or not sdtp:
                sdtp = pos.EntTp
                sdflg = 'tp0'
            if sdtp and abs(sdtp - sk_close[ski]) < sk_atr[ski] * sk_close[ski] * 6:
                self.sendord(var, -entsize, 0, sdtp, 'Lmt', idtime, Offset='close', EntSki=iski, Ordid=pos.Posid, OrdFlg=sdflg)

        # --------------------------------------------------------开仓逻辑
        # if idtime == '2017-06-15':
        #     print 'crttime:', idtime, ' crthigh:', ihigh
        var = self.Var
        for sgnna, sgnbs in sgnkops.iteritems():
            sgnid = sgnna.split('_')[0]
            if sgnid in self.SgnVarPos_Dic:
                svpinf = self.SgnVarPos_Dic[sgnid]  # 策略持仓信息
            else:
                svpinf = None

            sdop = sgnbs.sdop
            sdsp = sgnbs.sdsp
            sdtp = sgnbs.sdtp
            psn = sgnbs.psn
            msn = sgnbs.msn
            if sgnbs.bsdir>0:
                stp = sdop - sdsp if sdsp else None
                tpl = sdtp - sdop if sdtp else None
            else:
                stp = -sdop + sdsp if sdsp else None
                tpl = -sdtp + sdop if sdtp else None

            if abs(sdop - sk_close[ski]) >  sk_atr[ski] * sk_close[ski] * 6:
                continue

            #--同类信号开仓次数不能超限
            if svpinf and  svpinf.EntNum >= 1:
                continue
            # 已经开了tdk2/6则不再开tdk4
            if sgnid == 'tdk4-bbl' and ('tdk2-bbl' in self.SgnVarPos_Dic or 'tdk6-bbl' in self.SgnVarPos_Dic):
                continue
            if sgnid == 'tdk4-ttl' and ('tdk2-ttl' in self.SgnVarPos_Dic or 'tdk6-ttl' in self.SgnVarPos_Dic):
                continue
            if sgnid == 'tdk4-sa' and ('tdk2-sa' in self.SgnVarPos_Dic or 'tdk6-sa' in self.SgnVarPos_Dic):
                continue
            if sgnid == 'tdk4-sd' and ('tdk2-sd' in self.SgnVarPos_Dic or 'tdk6-sd' in self.SgnVarPos_Dic):
                continue
            # 已经开了tdk1则不再开tdk3
            if sgnid == 'tdk3-bbl' and 'tdk1-bbl' in self.SgnVarPos_Dic :
                continue
            if sgnid == 'tdk3-ttl' and 'tdk1-ttl' in self.SgnVarPos_Dic :
                continue
            if sgnid == 'tdk3-sa' and 'tdk1-sa' in self.SgnVarPos_Dic :
                continue
            if sgnid == 'tdk3-sd' and 'tdk1-sd' in self.SgnVarPos_Dic :
                continue
            etcn = 1
            iMsp = self.Networth * 0.1 / etcn
            if iMsp != iMsp:
                continue
            imsize = round(iMsp * 1.0 / sdop / self.Multiplier[var])  # 单次开仓最大用1倍杠杆
            # 通过风险比例分配策略下单量
            # iRsp = iMsp * 0.01   # 单次风险最大 1%
            # perstp = stp * self.Multiplier[var] if stp else None
            # ifsize = round(iRsp / perstp) if perstp else None

            # entsize = min(ifsize, imsize) if ifsize else imsize

            entsize = imsize
            entsize = entsize * sgnbs.bsdir
            ordtyp = sgnbs.ordtyp

            self.sendord(var, entsize, 0, sdop, ordtyp, idtime, Offset='open', EntSki=iski, OrdSp=sdsp, OrdTp=sdtp, Psn= psn, Msn = msn, OrdFlg=sgnna)

            # if isgn not in self.SgnVarLstSdop_Dic:
            #     self.SgnVarLstSdop_Dic[isgn] = {}
            # self.SgnVarLstSdop_Dic[isgn][var] = {'sdsize': entsize, 'sdop': sdop}
            
            '''









