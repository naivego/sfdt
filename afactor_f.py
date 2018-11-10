# -*- coding: cp936 -*-
__author__ = 'naivego'

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import csv
# from datetime import datetime
from datetime import datetime, timedelta
import copy


# ---------------------------------------------------------------------------
# sk 与 rsline 的触及关系
def sklreach(sk_open, sk_high, sk_low, sk_close, rsp, dir='dw', atr=0.016):
    det = 0.05 * atr * sk_close
    atl = 0
    if dir == 'dw':
        if sk_low > rsp + det * 2:
            atl = 3
        elif rsp + det * 2 >= sk_low > rsp + det * 0.5:
            atl = 2
        elif rsp - det * 1 > sk_close >= rsp - det * 2 and sk_high > rsp:
            atl = -4
        elif rsp - det * 2 > sk_close and sk_high > rsp:
            atl = -5
        elif sk_high <= rsp:
            atl = -6
        else:  # rsp + det * 0.5  >=  sk_low >= rsp - det * 0.5:
            atl = 1

        if sk_close >= sk_open:
            dwrp = (sk_close - sk_low) / (sk_close * atr)
        else:
            dwrp = (2 * sk_close - sk_low - sk_open) / (sk_close * atr)
        return (atl, dwrp)
    else:
        if sk_high < rsp - det * 2:
            atl = -3
        elif rsp - det * 2 <= sk_high < rsp - det * 0.5:
            atl = -2
        elif rsp + det * 1 < sk_close <= rsp + det * 2 and sk_low < rsp:
            atl = 4
        elif rsp + det * 2 < sk_close and sk_low < rsp:
            atl = 5
        elif sk_low >= rsp:
            atl = 6
        else:  # rsp - det * 0.5  <=  sk_high <= rsp + det * 0.5:
            atl = -1

        if sk_close <= sk_open:
            uprp = (sk_close - sk_high) / (sk_close * atr)
        else:
            uprp = (2 * sk_close - sk_high - sk_open) / (sk_close * atr)
        return (atl, uprp)


# ---------------------------------------------------------------------------
# 极值点: 位置、价格、高低点类型，-1：低点， 1：高点， 0：一般点
class Extrp(object):
    def __init__(self, ski, skp, tob):
        self.ski = ski
        self.skp = skp
        self.tob = tob


# ---------------------------------------------------------------------------
class Trpline(object):
    def __init__(self, trpb, trpd):
        self.trpb = trpb
        self.trpd = trpd
        self.ak = (trpd.skp - trpb.skp) / (trpd.ski - trpb.ski)
        self.rk = (trpd.skp - trpb.skp) * 100 / trpd.skp / (trpd.ski - trpb.ski)

    def extendp(self, exti):
        return self.trpb.skp + self.ak * (exti - self.trpb.ski)


# ---------------------------------------------------------------------------

class Rsband(object):
    def __init__(self, dtbi, dtei, bandhp, bandlp):
        self.dtbi = dtbi
        self.dtei = dtei
        self.bandhp = bandhp
        self.bandlp = bandlp


# ---------------------------------------------------------------------------
class Rsbandvec(object):
    def __init__(self, rsdir=1, maxbds=10):
        self.rsdir = rsdir  # 趋势方向 ，1：上升（按低点从大到小排序）  -1：下降（按高点从小到大排序）
        self.rsdtvec = []  # 按时间从大到小排序的队列
        self.rspvec = []  # 按价格大小排序
        self.maxbds = maxbds
        self.mindti = 0
        self.count = 0

    def cmpbydt(self, bd1, bd2):
        return 1 if bd2.dtei - bd1.dtei > 0 else -1

    def cmpbyrsp(self, bd1, bd2):
        if self.rsdir < 0:
            return 1 if bd1.bandhp - bd2.bandhp > 0 else -1
        else:
            return 1 if bd2.bandlp - bd1.bandlp > 0 else -1

    def sortby_dt(self):
        self.rsdtvec.sort(self.cmpbydt)

    def sortby_rsp(self):
        self.rspvec.sort(self.cmpbyrsp)

    def addband(self, newband):
        if len(self.rsdtvec) >= self.maxbds:
            delband = self.rsdtvec.pop()
            self.rspvec.remove(delband)
            self.count -= 1
        self.rsdtvec.append(newband)
        self.rspvec.append(newband)
        self.count += 1
        self.sortby_dt()
        self.sortby_rsp()

    def updateband(self, newband):
        if self.count > 0:
            delband = self.rsdtvec.pop(0)
            self.rspvec.remove(delband)
            self.rsdtvec.append(newband)
            self.rspvec.append(newband)
            self.sortby_dt()
            self.sortby_rsp()

    def updateformdti(self, mindti, mbp):
        self.mindti = mindti
        tempvec = self.rsdtvec[:]
        for band in tempvec:
            if band.dtbi < self.mindti:
                self.rsdtvec.remove(band)
                self.count -= 1
            elif (self.rsdir > 0 and band.bandhp >= mbp) or (self.rsdir < 0 and band.bandlp <= mbp):
                self.rsdtvec.remove(band)
                self.count -= 1

        tempvec = self.rspvec[:]
        for band in tempvec:
            if band.dtbi < self.mindti:
                self.rspvec.remove(band)
            elif (self.rsdir > 0 and band.bandhp >= mbp) or (self.rsdir < 0 and band.bandlp <= mbp):
                self.rspvec.remove(band)

    def getbandby_dt(self, index):
        if -self.count <= index <= self.count - 1 and self.count > 0:
            return self.rsdtvec[index]
        else:
            return None

    def getbandby_rsp(self, index):
        if -self.count <= index <= self.count - 1 and self.count > 0:
            return self.rspvec[index]
        else:
            return None

    def getbandby_bmp(self, mx='min'):
        if self.count == 1:
            return self.rsdtvec[0]
        elif self.count > 1:
            mband = self.rsdtvec[0]
            if mx == 'min':
                for band in self.rsdtvec[1:]:
                    if band.bandlp <= mband.bandlp:
                        mband = band
            else:
                for band in self.rsdtvec[1:]:
                    if band.bandhp >= mband.bandhp:
                        mband = band
            return mband
        else:
            return None


# ---------------------------------------------------------------------------
class Sgn_Rst(object):
    def __init__(self, rstdir, rsti, rstp):
        self.rstdir = rstdir
        self.rsti = rsti  # 转折确认点
        self.rstp = rstp
        self.rstbi = rsti  # 转折起点

        self.rsp_zs1a = None
        self.rsp_zs1c = None
        self.rsp_zs2a = None
        self.rsp_zs2c = None
        self.rsp_qs1a = None
        self.rsp_qs1c = None
        self.rsp_qs2a = None
        self.rsp_qs2c = None

        self.sgn_zs1a = None
        self.sgn_zs1c = None
        self.sgn_zs2a = None
        self.sgn_zs2c = None
        self.sgn_qs1a = None
        self.sgn_qs1c = None
        self.sgn_qs2a = None
        self.sgn_qs2c = None

    def setqsrsp(self, bandvec):
        if self.rstdir > 0 and bandvec.rsdir > 0:
            if bandvec.count > 0:
                tepband = bandvec.getbandby_rsp(0)
                self.rsp_qs1c = tepband.bandlp
                self.rsp_qs1a = tepband.bandhp
            if bandvec.count > 1:
                tepband = bandvec.getbandby_rsp(1)
                self.rsp_qs2c = tepband.bandlp
                self.rsp_qs2a = tepband.bandhp
        elif self.rstdir < 0 and bandvec.rsdir < 0:
            if bandvec.count > 0:
                tepband = bandvec.getbandby_rsp(0)
                self.rsp_qs1c = tepband.bandhp
                self.rsp_qs1a = tepband.bandlp
            if bandvec.count > 1:
                tepband = bandvec.getbandby_rsp(1)
                self.rsp_qs2c = tepband.bandhp
                self.rsp_qs2a = tepband.bandlp

    def setzsrsp(self, bandvec):
        if self.rstdir > 0 and bandvec.rsdir > 0:
            if bandvec.count > 0:
                tepband = bandvec.getbandby_rsp(0)
                self.rsp_zs1c = tepband.bandlp
                self.rsp_zs1a = tepband.bandhp
            if bandvec.count > 1:
                tepband = bandvec.getbandby_rsp(1)
                self.rsp_zs2c = tepband.bandlp
                self.rsp_zs2a = tepband.bandhp
            elif bandvec.count == 1:
                self.rsp_zs2c = self.rsp_zs1c
                self.rsp_zs2a = self.rsp_zs1a
        elif self.rstdir < 0 and bandvec.rsdir < 0:
            if bandvec.count > 0:
                tepband = bandvec.getbandby_rsp(0)
                self.rsp_zs1c = tepband.bandhp
                self.rsp_zs1a = tepband.bandlp
            if bandvec.count > 1:
                tepband = bandvec.getbandby_rsp(1)
                self.rsp_zs2c = tepband.bandhp
                self.rsp_zs2a = tepband.bandlp
            elif bandvec.count == 1:
                self.rsp_zs2c = self.rsp_zs1c
                self.rsp_zs2a = self.rsp_zs1a

    def set_sgn(self, sk_open, sk_high, sk_low, sk_close, sk_atr):
        rsdir = 'dw' if self.rstdir > 0 else 'up'
        if self.rsp_zs1a:
            self.sgn_zs1a = sklreach(sk_open, sk_high, sk_low, sk_close, self.rsp_zs1a, dir=rsdir, atr=sk_atr)
        if self.rsp_zs1c:
            self.sgn_zs1c = sklreach(sk_open, sk_high, sk_low, sk_close, self.rsp_zs1c, dir=rsdir, atr=sk_atr)
        if self.rsp_zs2a:
            self.sgn_zs2a = sklreach(sk_open, sk_high, sk_low, sk_close, self.rsp_zs2a, dir=rsdir, atr=sk_atr)
        if self.rsp_zs2c:
            self.sgn_zs2c = sklreach(sk_open, sk_high, sk_low, sk_close, self.rsp_zs2c, dir=rsdir, atr=sk_atr)

        if self.rsp_qs1a:
            self.sgn_qs1a = sklreach(sk_open, sk_high, sk_low, sk_close, self.rsp_qs1a, dir=rsdir, atr=sk_atr)
        if self.rsp_qs1c:
            self.sgn_qs1c = sklreach(sk_open, sk_high, sk_low, sk_close, self.rsp_qs1c, dir=rsdir, atr=sk_atr)
        if self.rsp_qs2a:
            self.sgn_qs2a = sklreach(sk_open, sk_high, sk_low, sk_close, self.rsp_qs2a, dir=rsdir, atr=sk_atr)
        if self.rsp_qs2c:
            self.sgn_qs2c = sklreach(sk_open, sk_high, sk_low, sk_close, self.rsp_qs2c, dir=rsdir, atr=sk_atr)


class Sgn_Ans(object):
    def __init__(self, sgnlist, sk_open, sk_high, sk_low, sk_close, sk_atr):
        self.sgnlist = sgnlist
        self.sk_open = sk_open
        self.sk_high = sk_high
        self.sk_low = sk_low
        self.sk_close = sk_close
        self.sk_atr = sk_atr
        self.rptlist = []
        self.skatzs2 = []
        self.skatqs2 = []
        self.bslist = []
        self.rsllist = []

    def updaterpt(self, i):
        if len(self.sgnlist) < 1:
            return
        rpt = (0, 0, None)
        # -----------------------记录当前sk相对当日rsl的情况，
        lstsgn = self.sgnlist[-1]
        if not lstsgn:
            self.skatzs2.append(None)
            self.skatqs2.append(None)
            self.bslist.append(None)
            self.rsllist.append(None)
            self.rptlist.append(rpt)
            return

        if lstsgn.sgn_zs2c and abs(lstsgn.sgn_zs2c[0]) != 3:
            zsrpt = lstsgn.sgn_zs2c[0] / abs(lstsgn.sgn_zs2c[0]) * 20 + lstsgn.sgn_zs2c[0]
        elif lstsgn.sgn_zs1c and abs(lstsgn.sgn_zs1c[0]) != 3:
            zsrpt = lstsgn.sgn_zs1c[0] / abs(lstsgn.sgn_zs1c[0]) * 10 + lstsgn.sgn_zs1c[0]
        else:
            zsrpt = 0

        if lstsgn.sgn_qs2c and abs(lstsgn.sgn_qs2c[0]) != 3:
            qsrpt = lstsgn.sgn_qs2c[0] / abs(lstsgn.sgn_qs2c[0]) * 20 + lstsgn.sgn_qs2c[0]
        elif lstsgn.sgn_qs1c and abs(lstsgn.sgn_qs1c[0]) != 3:
            qsrpt = lstsgn.sgn_qs1c[0] / abs(lstsgn.sgn_qs1c[0]) * 10 + lstsgn.sgn_qs1c[0]
        else:
            qsrpt = 0

        # ------------------------------------
        if not lstsgn.rsp_zs2c:
            rsl = None
            atl = self.skatzs2[-1]
        else:
            bdh = max(lstsgn.rsp_zs2c, lstsgn.rsp_zs2a)
            bdl = min(lstsgn.rsp_zs2c, lstsgn.rsp_zs2a)
            if len(self.skatzs2) > 0:
                lst_atzs2 = self.skatzs2[-1]
                if not lst_atzs2 or lst_atzs2[0] > 0:
                    rsdir = 'dw'
                    rsl = bdl
                    atl = sklreach(self.sk_open[i], self.sk_high[i], self.sk_low[i], self.sk_close[i], bdl, dir=rsdir, atr=self.sk_atr[i])
                else:
                    rsdir = 'up'
                    rsl = bdh
                    atl = sklreach(self.sk_open[i], self.sk_high[i], self.sk_low[i], self.sk_close[i], bdh, dir=rsdir, atr=self.sk_atr[i])
        self.skatzs2.append(atl)
        # self.rsllist.append(rsl)
        # bsfact = self.sgn_bs(i)
        # -----------------------------------
        if not lstsgn.rsp_qs2c:
            rsl = None
            atl = self.skatqs2[-1]
        else:
            bdh = max(lstsgn.rsp_qs2c, lstsgn.rsp_qs2a)
            bdl = min(lstsgn.rsp_qs2c, lstsgn.rsp_qs2a)
            if len(self.skatqs2) > 0:
                lst_atqs2 = self.skatqs2[-1]
                if not lst_atqs2 or lst_atqs2[0] > 0:
                    rsdir = 'dw'
                    rsl = bdl
                    atl = sklreach(self.sk_open[i], self.sk_high[i], self.sk_low[i], self.sk_close[i], bdl, dir=rsdir, atr=self.sk_atr[i])
                else:
                    rsdir = 'up'
                    rsl = bdh
                    atl = sklreach(self.sk_open[i], self.sk_high[i], self.sk_low[i], self.sk_close[i], bdh, dir=rsdir, atr=self.sk_atr[i])
        self.skatqs2.append(atl)
        self.rsllist.append(rsl)
        bsfact = self.sgn_bs(i)

        self.bslist.append(bsfact)
        rpt = (zsrpt, qsrpt, bsfact)
        self.rptlist.append(rpt)
        return

    # ----------------------生成买卖决策信号,向交易模块提供交易要素：多空方向、委托价格-------------
    def sgn_bs(self, i):
        '''
        基于rsband的交易逻辑：
        1、若当日sk处于rsband上方（skath = 3,2,1,4,5），次日执行如下2个任务：
            st. det = 0.1 * atr * sk_close（即单日平均波动的1/20）
            A：尽快以合适的价格限价平空单（橄榄形减仓）
                设定:橄榄中线区间： mop = bandh + det * mo  pmo=[8,16]  --不动作
                    内侧清仓线 piop = bandl + det * io     pio=[8, 6, 4]  ---主动减仓
                    止损清仓线 peop = bandl + det * eo    peo=[16,20,24]    --被动减仓
            B：分批以较优的成本开多单
                开仓线 kop=bandl + det * ko   ko=[4,2,0]

        2、若当日sk处于rsband下方（skatl = -3,-2,-1,-4,-5），次日执行如上2个相应反向任务，但实际中由于下跌比较迅猛，参数设置偏保守些
        上方参数设置在字典bsolive_dic中
        :return:
        '''
        # print 'sgn_bs'
        rsl = self.rsllist[-1]
        atl = self.skatqs2[-1]
        det = self.sk_atr[i] * self.sk_close[i] * 0.05
        if rsl:
            return (rsl, atl[0], det)
        else:
            return None


# ---------------------------------------------------------------------------
class Grst_Factor(object):
    def __init__(self, skdata):
        self.quotes = skdata.loc[:]
        Column0 = self.quotes.columns[0]
        if '_' not in Column0:
            Period = 'd'
        else:
            Period = Column0.split('_')[1]

        self.quotes = self.quotes.rename(
            columns={'Open_' + Period: 'open', 'High_' + Period: 'high', 'Low_' + Period: 'low', 'Close_' + Period: 'close',
                     'Volume_' + Period: 'volume'})
        if Period == 'd':
            # self.quotes = self.quotes.rename(columns={'Open': 'open', 'High': 'high', 'Low': 'low', 'Close': 'close','Volume':'volume'})
            self.quotes['time'] = skdata.index
            xdate = [datetime.strptime(i, '%Y_%m_%d') for i in self.quotes['time']]
            self.quotes['time'] = xdate
        else:
            self.quotes['time'] = skdata.index
            xdate = [datetime.strptime(i, '%Y-%m-%d %H:%M:%S') for i in self.quotes['time']]
            self.quotes['time'] = xdate

        Dat_bar = self.quotes.loc[:]
        '''
        Dat_open = self.quotes.loc[:,'open']
        Dat_high = self.quotes.loc[:, 'high']
        Dat_low = self.quotes.loc[:, 'low']
        Dat_close = self.quotes.loc[:, 'close']

        '''

        Dat_bar['TR1'] = Dat_bar['high'] - Dat_bar['low']
        Dat_bar['TR2'] = abs(Dat_bar['high'] - Dat_bar['close'].shift(1))
        Dat_bar['TR3'] = abs(Dat_bar['low'] - Dat_bar['close'].shift(1))
        TR = Dat_bar.loc[:, ['TR1', 'TR2', 'TR3']].max(axis=1)
        ATR = TR.rolling(14).mean() / Dat_bar['close'].shift(1)
        self.quotes['ATR'] = ATR

        self.tops = []
        self.botms = []
        self.reslines = []
        self.suplines = []
        self.crtbbl = None
        self.crtttl = None

    def update_supline(self, sk_open, sk_high, sk_low, sk_close, sk_volume, sk_time, sk_atr, i):
        # --calc new update_supline
        if len(self.botms) >= 2:
            newbbl = Trpline(self.botms[-2], self.botms[-1])
            if 0 <= newbbl.ak < sk_close[i] * sk_atr[i] * 0.3:
                for ski in range(self.botms[-2].ski, self.botms[-1].ski):
                    if sk_open[ski] < newbbl.extendp(ski) and sk_close[ski] < newbbl.extendp(ski):
                        return
                self.suplines.append(newbbl)
                self.crtbbl = newbbl

    def update_resline(self, sk_open, sk_high, sk_low, sk_close, sk_volume, sk_time, sk_atr, i):
        # --calc new update_resline
        if len(self.tops) >= 2:
            newttl = Trpline(self.tops[-2], self.tops[-1])
            if -sk_close[i] * sk_atr[i] * 0.3 < newttl.ak <= 0:
                for ski in range(self.tops[-2].ski, self.tops[-1].ski):
                    if sk_open[ski] > newttl.extendp(ski) and sk_close[ski] > newttl.extendp(ski):
                        return
                self.suplines.append(newttl)
                self.crtttl = newttl

    def idxof_nsckls(self, nsckls, ski):
        if len(nsckls) <= 0: return -1
        for idx in range(0, len(nsckls)):
            if ski >= nsckls[idx][1][0][0] and ski <= nsckls[idx][1][-1][1]:
                return idx
        return -1

    def cal_Grst(self):
        skbgi = 20  # 起始点
        sk_open = self.quotes['open'].values
        sk_high = self.quotes['high'].values
        sk_low = self.quotes['low'].values
        sk_close = self.quotes['close'].values
        sk_volume = self.quotes['volume'].values
        sk_time = self.quotes['time'].values
        sk_atr = self.quotes['ATR'].values
        # ----------------------------------------------
        sk_ckl = []  # 与ck同步，由元组（ckli,cksdh,cksdl）构成的队列，记录当前的sk链所包括的sk数目和实体部分的区间
        sk_ckdtpst = 0.05  # 0.05倍平均涨幅作为涨跌柱子的公差
        ckls = []  # 与ckl线段列表，由列表[cklbi,cklei,cklbp,cklep,cklsd]构成,记录线段的起点位置、终点位置、起点价格、终点价格、长度
        detsuc = 5  # strong上升链构成上涨反转的链长 =detsuc*avgski
        detsdc = -5  # strong下降链构成下降反转的链长 =detsdc*avgski
        sk_cklsm = []  # 在sk序列框架下对ckls结构进行描述，指示当前的sk处于ckls结构中的水平 (ckltp, ickls)
        '''
           ckltp                             ickls
           1---处于wuckl weak up ckl         (ickls0,)
           2---处于suckl strong up ckl       (ickls0,)
           3---处于nuckl N-S up ckl          (ickls1,ickls2,ickls0)
           -1--处于wdckl weak down ckl       (ickls0,)
           -2--处于sdckl strong down ckl     (ickls0,)
           -3--处于ndckl N-S down ckl        (ickls1,ickls2,ickls0)

        '''
        nsckls = []  # 在ckls基础上，将相邻的可以聚合的n元聚合起来构成，由列表由[nsckltp，insckls]组成 insckls=[ickls0,ickls1,ickls2...]构成，当形成新的局部n元时更新
        nscklsedi = 0  # 最新段的nsckls处于ckls的第几号链上
        # -----------------------------------------------
        qspds = []  # 趋势前沿列表 每段由[qsprti,nscklidx,nscklitp,qspbi,qspei,qspbsdp,qspesdp,qspbp,qspep]组成，来自于nsckls的波段
        '''
           qsprti--形成新的qsdps时（步进或逆转）的sk索引
           nscklidx--该qspds所在的聚合链的索引
           nscklitp--该qspds所在的聚合链的ckltp
           qspbi--该qspds的起点索引
           qspei--该qspds的终点索引
           qspbsdp--该qspds的起点实柱价格
           qspesdp--该qspds的终点实柱价格
           qspbp--该qspds的起点远端价格，逆向突破该价格确定新的反转的趋势前沿
           qspep--该qspds的终点远端价格，正向突破该价格确定新步进趋势前沿

        '''
        qsrstp = []  # 多空转换点 收盘突破前沿，趋势方向转化 (sgn_rsti, sgn_rstp, sgn_rstdir) 突破位置，突破价格，突破方向：1-向上， -1 向下
        sk_qspds = []
        sk_qsrstp = []
        sk_rstspl = []
        sk_rstsph = []

        ctp = None
        cbp = None
        zsdir = None
        zsckl = None
        zsski = None
        zslp = None
        zshp = None
        bslp = None  # 回看低点
        bshp = None  # 回看高点
        bscp = None  # 回看远端
        bsbj = 0  # 步进标记

        # ********************************************************显示信号线
        sk_qsh = []
        sk_qsl = []
        sk_qswr = []  # 指示当前价格在趋势前沿中枢相对ATR得到宽度
        sk_rsl = []  # 指示当前价格在趋势前沿中枢中的价格水平
        sk_itp = []
        sk_disrst = []
        sk_bbl = []
        sk_ttl = []
        sk_zsh = []  # 转换中枢高点
        sk_zsl = []  # 转换中枢低点
        sk_bsh = []  # 转换回看高点
        sk_bsl = []  # 转换回看低点

        dwqsbands = Rsbandvec(rsdir=-1)
        upqsbands = Rsbandvec(rsdir=1)
        dwzsbands = Rsbandvec(rsdir=-1)
        upzsbands = Rsbandvec(rsdir=1)
        lstdwqsbd = None
        lstupqsbd = None
        lstdwzsbd = None
        lstupzsbd = None
        crtrsdwqsbd = None
        crtrsupqsbd = None
        crtrsdwzsbd = None
        crtrsupzsbd = None
        sk_sgn = []
        sgnans = Sgn_Ans(sk_sgn, sk_open, sk_high, sk_low, sk_close, sk_atr)
        sk_zs1c = []
        sk_zs1a = []
        sk_zs2c = []
        sk_zs2a = []
        sk_qs1c = []
        sk_qs1a = []
        sk_qs2c = []
        sk_qs2a = []
        sk_zsrpt = []
        sk_qsrpt = []
        sk_bsfact = []
        # *******************************************************************
        # ----------------------------------------------------------------------

        if sk_close.size <= skbgi:
            return

        for i in range(0, skbgi):
            sk_ckl.append(None)
            sk_cklsm.append(None)
            sk_qspds.append(None)
            sk_qsrstp.append(0)
            sk_rstspl.append(sk_low[i])
            sk_rstsph.append(sk_high[i])

            sk_qsh.append(sk_high[i])
            sk_qsl.append(sk_low[i])
            sk_zsh.append(sk_high[i])
            sk_zsl.append(sk_low[i])
            sk_bsh.append(sk_high[i])
            sk_bsl.append(sk_low[i])

            sk_qswr.append(0)
            sk_rsl.append(0)
            sk_itp.append(0)

            sk_disrst.append(sk_low[i])
            sk_ttl.append(sk_disrst[-1])
            sk_bbl.append(sk_disrst[-1])
            # -----------------
            sk_sgn.append(None)
            sgnans.updaterpt(i)
            sk_zs1c.append(sk_close[i])
            sk_zs1a.append(sk_close[i])
            sk_zs2c.append(sk_close[i])
            sk_zs2a.append(sk_close[i])
            sk_qs1c.append(sk_close[i])
            sk_qs1a.append(sk_close[i])
            sk_qs2c.append(sk_close[i])
            sk_qs2a.append(sk_close[i])
            sk_zsrpt.append(0)
            sk_qsrpt.append(0)
            sk_bsfact.append(np.nan)
            # -----------------

        sk_qsrstp[0] = 2
        sk_qsrstp[1] = -2

        sk_qsh.append(sk_high[skbgi])
        sk_qsl.append(sk_low[skbgi])
        sk_zsh.append(sk_high[skbgi])
        sk_zsl.append(sk_low[skbgi])
        sk_bsh.append(sk_high[skbgi])
        sk_bsl.append(sk_low[skbgi])

        sk_qswr.append(0)
        sk_rsl.append(0)
        sk_itp.append(0)

        sk_disrst.append(sk_low[skbgi])
        sk_ttl.append(sk_disrst[-1])
        sk_bbl.append(sk_disrst[-1])

        sk_sgn.append(None)
        sgnans.updaterpt(skbgi)
        sk_zs1c.append(sk_close[skbgi])
        sk_zs1a.append(sk_close[skbgi])
        sk_zs2c.append(sk_close[skbgi])
        sk_zs2a.append(sk_close[skbgi])
        sk_qs1c.append(sk_close[skbgi])
        sk_qs1a.append(sk_close[skbgi])
        sk_qs2c.append(sk_close[skbgi])
        sk_qs2a.append(sk_close[skbgi])
        sk_zsrpt.append(0)
        sk_qsrpt.append(0)
        sk_bsfact.append(np.nan)

        if sk_close[skbgi] >= sk_open[skbgi]:
            ckli = 1
            cksdh = sk_close[skbgi]
            cksdl = sk_open[skbgi]
        else:
            ckli = -1
            cksdl = sk_close[skbgi]
            cksdh = sk_open[skbgi]
        sk_ckl.append((ckli, cksdh, cksdl))

        # ckls=[]   # 单纯K链列表，ckl线段列表，由列表[cklbi,cklei,cklbp,cklep,cklsd]构成,记录线段的起点、终点、长度
        cklbi = skbgi
        cklei = skbgi
        cklbp = sk_open[skbgi]
        cklep = sk_close[skbgi]
        cklsd = ckli * (cksdh - cksdl)
        ckls.append([cklbi, cklei, cklbp, cklep, cklsd])

        # sk_cklsm=[] #在sk序列框架下对ckls结构进行描述，指示当前的sk处于ckls结构中的水平 (ckltp, ickls),最近的3段ckls
        ckltp = ckli
        ickls0 = tuple(ckls[-1])
        ickls = (ickls0,)
        sk_cklsm.append((ckltp, ickls))
        # print(0,sk_close.index[0],(ckli, round(cksdh,decsn), round(cksdl,decsn)))
        sk_qspds.append([0, 0, 0, 0, 0, sk_open[skbgi], sk_close[skbgi], sk_open[skbgi], sk_close[skbgi]])
        sk_qsrstp.append(0)
        sk_rstspl.append(sk_low[skbgi])
        sk_rstsph.append(sk_high[skbgi])

        for i in range(skbgi + 1, sk_close.size):
            avgski = sk_atr[i - 1] * sk_close[i - 1]
            if sk_ckl[i - 1][0] > 0:
                if sk_close[i] >= sk_close[i - 1] - sk_ckdtpst * sk_atr[i - 1] * sk_close[i - 1]:  # sk_open[i] - sk_ckdtpst * sk_atr[i]:  #
                    ckli = sk_ckl[i - 1][0] + 1
                    cksdh = max(sk_ckl[i - 1][1], sk_close[i])
                    cksdl = sk_ckl[i - 1][2]
                    sk_ckl.append((ckli, cksdh, cksdl))

                    # 更新 ckls
                    ckls[-1][1] += 1
                    ckls[-1][3] = cksdh
                    ckls[-1][4] = cksdh - cksdl
                else:
                    ckli = -1
                    cksdh = sk_ckl[i - 1][1]
                    cksdl = sk_close[i]
                    sk_ckl.append((ckli, cksdh, cksdl))

                    # 更新 ckls
                    cklbi = i
                    cklei = i
                    cklbp = cksdh
                    cklep = cksdl
                    cklsd = cklep - cklbp
                    ckls.append([cklbi, cklei, cklbp, cklep, cklsd])

            else:
                if sk_close[i] <= sk_close[i - 1] + sk_ckdtpst * sk_atr[i - 1] * sk_close[i - 1]:  # sk_open[i] + sk_ckdtpst * sk_atr[i]:  #
                    ckli = sk_ckl[i - 1][0] - 1
                    cksdl = min(sk_ckl[i - 1][2], sk_close[i])
                    cksdh = sk_ckl[i - 1][1]
                    sk_ckl.append((ckli, cksdh, cksdl))
                    # 更新 ckls
                    ckls[-1][1] += 1
                    ckls[-1][3] = cksdl
                    ckls[-1][4] = cksdl - cksdh

                else:
                    ckli = 1
                    cksdl = sk_ckl[i - 1][2]
                    cksdh = sk_close[i]
                    sk_ckl.append((ckli, cksdh, cksdl))

                    # 更新 ckls
                    cklbi = i
                    cklei = i
                    cklbp = cksdl
                    cklep = cksdh
                    cklsd = cklep - cklbp
                    ckls.append([cklbi, cklei, cklbp, cklep, cklsd])

            # print(i,sk_close.index[i],(ckli, round(cksdh,decsn), round(cksdl,decsn)))
            # sk_cklsm=[] #在sk序列框架下对ckls结构进行描述，指示当前的sk处于ckls结构中的水平 (ckltp, ickls)
            if len(ckls) >= 3:
                ickls0 = tuple(ckls[-1])
                ickls1 = tuple(ckls[-2])
                ickls2 = tuple(ckls[-3])
                if (ickls0[4] > 0 and sk_cklsm[-1][0] >= 3) or (
                                    ickls0[4] > 0 and ickls0[3] > ickls1[2] and ickls1[3] >= ickls2[2]):
                    # 3---处于nuckl N-S up ckl            (ickls0,ickls1,ickls2)
                    ckltp = 3
                    ickls = (ickls0, ickls1, ickls2)
                    sk_cklsm.append((ckltp, ickls))

                    # 更新nsckls=[]  由[nsckltp，insckls]组成 insckls=[insckls0,insckls1,insckls2...]
                    if len(nsckls) < 1:
                        nsckltp = 3
                        insckls0 = ickls0
                        insckls1 = ickls1
                        insckls2 = ickls2
                        insckls = [insckls2, insckls1, insckls0]

                        for icklsx in ckls[0:-3]:
                            if icklsx[4] >= 0:
                                nsckls.append([1, [tuple(icklsx)]])
                            else:
                                nsckls.append([-1, [tuple(icklsx)]])
                        nsckls.append([nsckltp, insckls])
                        nscklsedi = len(ckls) - 1
                    else:  # if len[nsckls]>=1 :
                        insckls = nsckls[-1][1]
                        if nsckls[-1][0] > 0 and ickls1[0] >= insckls[-2][0] and ickls1[1] <= insckls[-2][1] and ickls2[0] >= insckls[-3][0] and \
                                        ickls2[1] <= insckls[-3][1] \
                                and ickls0[0] <= insckls[-1][1]:
                            nsckls[-1][1][-1] = ickls0
                        elif nsckls[-1][0] > 0 and ickls2[0] == insckls[-1][0] and ickls2[1] == insckls[-1][1] and ickls1[1] > insckls[-1][1]:
                            nsckls[-1][0] += 2
                            nsckls[-1][1].append(ickls1)
                            nsckls[-1][1].append(ickls0)
                            nscklsedi = len(ckls) - 1

                        elif ickls2[0] == insckls[-1][1]:
                            nsckltp = 3
                            insckls0 = ickls0
                            insckls1 = ickls1
                            insckls2 = ickls2
                            insckls = [insckls2, insckls1, insckls0]
                            nsckls.append([nsckltp, insckls])
                            nscklsedi = len(ckls) - 1

                        elif ickls2[0] > insckls[-1][1]:
                            nsckltp = 3
                            insckls0 = ickls0
                            insckls1 = ickls1
                            insckls2 = ickls2
                            insckls = [insckls2, insckls1, insckls0]
                            for icklsx in ckls[nscklsedi + 1:-3]:
                                if icklsx[4] >= 0:
                                    nsckls.append([1, [tuple(icklsx)]])
                                else:
                                    nsckls.append([-1, [tuple(icklsx)]])
                            nsckls.append([nsckltp, insckls])
                            nscklsedi = len(ckls) - 1


                elif (ickls0[4] < 0 and sk_cklsm[-1][0] <= -3) or (
                                    ickls0[4] < 0 and ickls0[3] < ickls1[2] and ickls1[3] <= ickls2[2]):
                    # -3---处于ndckl N-S dowm ckl          (ickls0,ickls1,ickls2)
                    ckltp = -3
                    ickls = (ickls0, ickls1, ickls2)
                    sk_cklsm.append((ckltp, ickls))

                    # 更新nsckls=[]  由[nsckltp，insckls]组成 insckls=[insckls0,insckls1,insckls2...]
                    if len(nsckls) < 1:
                        nsckltp = -3
                        insckls0 = ickls0
                        insckls1 = ickls1
                        insckls2 = ickls2
                        insckls = [insckls2, insckls1, insckls0]

                        for icklsx in ckls[0:-3]:
                            if icklsx[4] >= 0:
                                nsckls.append([1, [tuple(icklsx)]])
                            else:
                                nsckls.append([-1, [tuple(icklsx)]])
                        nsckls.append([nsckltp, insckls])
                        nscklsedi = len(ckls) - 1
                    else:  # if len[nsckls]>=1 :
                        insckls = nsckls[-1][1]
                        if nsckls[-1][0] < 0 and ickls1[0] >= insckls[-2][0] and ickls1[1] <= insckls[-2][1] and ickls2[0] >= insckls[-3][0] and \
                                        ickls2[1] <= insckls[-3][1] \
                                and ickls0[0] <= insckls[-1][1]:
                            nsckls[-1][1][-1] = ickls0
                        elif nsckls[-1][0] < 0 and ickls2[0] == insckls[-1][0] and ickls2[1] == insckls[-1][1] and ickls1[1] > insckls[-1][1]:
                            nsckls[-1][0] += -2
                            nsckls[-1][1].append(ickls1)
                            nsckls[-1][1].append(ickls0)
                            nscklsedi = len(ckls) - 1
                        elif ickls2[0] == insckls[-1][1]:
                            nsckltp = -3
                            insckls0 = ickls0
                            insckls1 = ickls1
                            insckls2 = ickls2
                            insckls = [insckls2, insckls1, insckls0]
                            nsckls.append([nsckltp, insckls])
                            nscklsedi = len(ckls) - 1

                        elif ickls2[0] > insckls[-1][1]:
                            nsckltp = -3
                            insckls0 = ickls0
                            insckls1 = ickls1
                            insckls2 = ickls2
                            insckls = [insckls2, insckls1, insckls0]
                            for icklsx in ckls[nscklsedi + 1:-3]:
                                if icklsx[4] >= 0:
                                    nsckls.append([1, [tuple(icklsx)]])
                                else:
                                    nsckls.append([-1, [tuple(icklsx)]])
                            nsckls.append([nsckltp, insckls])
                            nscklsedi = len(ckls) - 1

                elif (ickls0[4] > 0 and sk_cklsm[-1][0] >= 2) or ickls0[4] >= detsuc * avgski:
                    # 2---处于suckl strong up ckl       (ickls0,)
                    ckltp = 2
                    ickls = (ickls0,)
                    sk_cklsm.append((ckltp, ickls))
                elif (ickls0[4] < 0 and sk_cklsm[-1][0] <= -2) or ickls0[4] <= detsdc * avgski:
                    # -2--处于sdckl strong down ckl     (ickls0,)
                    ckltp = -2
                    ickls = (ickls0, ickls1, ickls2)
                    sk_cklsm.append((ckltp, ickls))
                elif ickls0[4] > 0 and ickls0[4] < detsuc * avgski:
                    # 1---处于wuckl weak up ckl         (ickls0,)
                    ckltp = 1
                    ickls = (ickls0, ickls1, ickls2)
                    sk_cklsm.append((ckltp, ickls))
                elif ickls0[4] < 0 and ickls0[4] > detsdc * avgski:
                    # -1--处于wdckl weak down ckl       (ickls0,)
                    ckltp = -1
                    ickls = (ickls0, ickls1, ickls2)
                    sk_cklsm.append((ckltp, ickls))
                else:
                    ckltp = 0
                    ickls = (ickls0, ickls1, ickls2)
                    sk_cklsm.append((ckltp, ickls))
            else:  # if len(ckls)<3:
                ickls0 = tuple(ckls[-1])
                if (ickls0[4] > 0 and sk_cklsm[-1][0] >= 2) or ickls0[4] >= detsuc * avgski:
                    # 2---处于suckl strong up ckl       (ickls0,)
                    ckltp = 2
                    ickls = (ickls0,)
                    sk_cklsm.append((ckltp, ickls))
                elif (ickls0[4] < 0 and sk_cklsm[-1][0] <= -2) or ickls0[4] <= detsdc * avgski:
                    # -2--处于sdckl strong down ckl     (ickls0,)
                    ckltp = -2
                    ickls = (ickls0,)
                    sk_cklsm.append((ckltp, ickls))
                if ickls0[4] > 0 and ickls0[4] < detsuc * avgski:
                    # 1---处于wuckl weak up ckl         (ickls0,)
                    ckltp = 1
                    ickls = (ickls0,)
                    sk_cklsm.append((ckltp, ickls))
                elif ickls0[4] < 0 and ickls0[4] > detsdc * avgski:
                    # -1--处于wdckl weak down ckl       (ickls0,)
                    ckltp = -1
                    ickls = (ickls0,)
                    sk_cklsm.append((ckltp, ickls))
                else:
                    ckltp = 0
                    ickls = (ickls0,)
                    sk_cklsm.append((ckltp, ickls))

            # 更新  qspds=[] #趋势前沿列表 每段由[qsprti,nscklidx,nscklitp,qspbi,qspei,qspbsdp,qspesdp,qspbp,qspep]组成，来自于nsckls的波段
            bsbj = 0
            if len(qspds) <= 0 and len(nsckls) > 0:  # 当首次形成确定性的聚合链（数量可能大于1）的时候逐链划分趋势前沿
                nscklidx = 0
                qsprti = nsckls[-1][1][-1][1]
                nscklitp = nsckls[-1][0]
                qspbi = nsckls[-1][1][0][0]
                qspei = nsckls[-1][1][-1][1]
                qspbsdp = nsckls[-1][1][0][2]
                qspesdp = nsckls[-1][1][-1][3]
                if nscklitp > 0:
                    qspbp = min(sk_low[qspbi], sk_low[qspbi - 1])
                    qspep = sk_high[qspei]
                else:
                    qspbp = max(sk_high[qspbi], sk_high[qspbi - 1])
                    qspep = sk_low[qspei]

                qspds.append([qsprti, nscklidx, nscklitp, qspbi, qspei, qspbsdp, qspesdp, qspbp, qspep])
                # --------------------------------------------------------------------------------------------
                if False:  # i > qspei:
                    for idx in range(qspei + 1, i + 1):
                        iqspds0 = qspds[-1]
                        if iqspds0[2] > 0:  # 当前的趋势是向上前沿
                            if sk_close[idx] > iqspds0[6]:  # 向上步进
                                # 检查此时的idx 处于第几个nsckls
                                nscklidx = self.idxof_nsckls(nsckls, idx)
                                if nscklidx > 0 and nscklidx > iqspds0[1]:
                                    qsprti = idx
                                    nscklitp = nsckls[nscklidx][0]
                                    qspbi = nsckls[nscklidx][1][0][0]
                                    qspei = nsckls[nscklidx][1][-1][1]
                                    qspbsdp = nsckls[nscklidx][1][0][2]
                                    qspesdp = nsckls[nscklidx][1][-1][3]
                                    if qspbi > 0:
                                        qspbp = min(sk_low[qspbi], sk_low[qspbi - 1])
                                    else:
                                        qspbp = sk_low[qspbi]
                                    if qspei <= i - 1:
                                        qspep = max(sk_high[qspei], sk_high[qspei + 1])
                                    else:
                                        qspep = sk_high[qspei]
                                    qspds.append([qsprti, nscklidx, nscklitp, qspbi, qspei, qspbsdp, qspesdp, qspbp, qspep])
                            elif sk_close[idx] < iqspds0[7]:  # 向下反转
                                # 检查此时的idx 处于第几个nsckls
                                nscklidx = self.idxof_nsckls(nsckls, idx)
                                if nscklidx > 0 and nscklidx > iqspds0[1]:
                                    qsprti = idx
                                    nscklitp = nsckls[nscklidx][0]
                                    qspbi = nsckls[nscklidx][1][0][0]
                                    qspei = nsckls[nscklidx][1][-1][1]
                                    qspbsdp = nsckls[nscklidx][1][0][2]
                                    qspesdp = nsckls[nscklidx][1][-1][3]
                                    if qspbi > 0:
                                        qspbp = max(sk_high[qspbi], sk_high[qspbi - 1])
                                    else:
                                        qspbp = sk_high[qspbi]
                                    if qspei <= i - 1:
                                        qspep = min(sk_low[qspei], sk_low[qspei + 1])
                                    else:
                                        qspep = sk_low[qspei]
                                    qspds.append([qsprti, nscklidx, nscklitp, qspbi, qspei, qspbsdp, qspesdp, qspbp, qspep])

                        elif iqspds0[2] < 0:  # 当前的趋势是向下前沿
                            if sk_close[idx] < iqspds0[6]:  # 向下步进
                                # 检查此时的idx 处于第几个nsckls
                                nscklidx = self.idxof_nsckls(nsckls, idx)
                                if nscklidx > 0 and nscklidx > iqspds0[1]:
                                    qsprti = idx
                                    nscklitp = nsckls[nscklidx][0]
                                    qspbi = nsckls[nscklidx][1][0][0]
                                    qspei = nsckls[nscklidx][1][-1][1]
                                    qspbsdp = nsckls[nscklidx][1][0][2]
                                    qspesdp = nsckls[nscklidx][1][-1][3]
                                    if qspbi > 0:
                                        qspbp = max(sk_high[qspbi], sk_high[qspbi - 1])
                                    else:
                                        qspbp = sk_high[qspbi]
                                    if qspei <= i - 1:
                                        qspep = min(sk_low[qspei], sk_low[qspei + 1])
                                    else:
                                        qspep = sk_low[qspei]
                                    qspds.append([qsprti, nscklidx, nscklitp, qspbi, qspei, qspbsdp, qspesdp, qspbp, qspep])
                            elif sk_close[idx] > iqspds0[7]:  # 向上反转
                                # 检查此时的idx 处于第几个nsckls
                                nscklidx = self.idxof_nsckls(nsckls, idx)
                                if nscklidx > 0 and nscklidx > iqspds0[1]:
                                    qsprti = idx
                                    nscklitp = nsckls[nscklidx][0]
                                    qspbi = nsckls[nscklidx][1][0][0]
                                    qspei = nsckls[nscklidx][1][-1][1]
                                    qspbsdp = nsckls[nscklidx][1][0][2]
                                    qspesdp = nsckls[nscklidx][1][-1][3]
                                    if qspbi > 0:
                                        qspbp = min(sk_low[qspbi], sk_low[qspbi - 1])
                                    else:
                                        qspbp = sk_low[qspbi]
                                    if qspei <= i - 1:
                                        qspep = max(sk_high[qspei], sk_high[qspei + 1])
                                    else:
                                        qspep = sk_high[qspei]
                                    qspds.append([qsprti, nscklidx, nscklitp, qspbi, qspei, qspbsdp, qspesdp, qspbp, qspep])

            # 对于当前的isk, 更新qspds
            elif len(qspds) >= 1:
                if iqspds0[2] > 0:  # 之前的趋势是向上前沿
                    if sk_ckl[i][0] < 0:
                        if not bscp:
                            bscp = sk_high[i]
                        else:
                            bscp = max(bscp, sk_high[i])
                    if bscp and sk_close[i] > bscp:
                        bsbj = 1
                    # 最新的isk与之前的趋势前沿同处于一个聚合链或单链上--延伸
                    if i == nsckls[-1][1][-1][1] and nsckls[-1][1][0][0] <= iqspds0[3]:  # 最新的isk与之前的趋势前沿同处于一个聚合链
                        nscklidx = len(nsckls) - 1
                        qsprti = iqspds0[0]
                        nscklitp = nsckls[-1][0]
                        qspbi = nsckls[-1][1][0][0]
                        qspei = nsckls[-1][1][-1][1]
                        qspbsdp = nsckls[-1][1][0][2]
                        qspesdp = nsckls[-1][1][-1][3]
                        qspbp = min(sk_low[qspbi], sk_low[qspbi - 1])
                        qspep = max(iqspds0[8], sk_high[qspei])
                        qspds[-1] = [qsprti, nscklidx, nscklitp, qspbi, qspei, qspbsdp, qspesdp, qspbp, qspep]

                    elif iqspds0[4] >= ckls[-1][0] and iqspds0[4] <= ckls[-1][1]:  # 最新的isk与之前的趋势前沿同处于一个单链
                        nscklidx = 0
                        qsprti = iqspds0[0]
                        nscklitp = 1
                        qspbi = ckls[-1][0]
                        qspei = ckls[-1][1]
                        qspbsdp = ckls[-1][2]
                        qspesdp = ckls[-1][3]
                        qspbp = min(sk_low[qspbi], sk_low[qspbi - 1])
                        qspep = max(iqspds0[8], sk_high[qspei])
                        qspds[-1] = [qsprti, nscklidx, nscklitp, qspbi, qspei, qspbsdp, qspesdp, qspbp, qspep]

                    elif sk_close[i] > iqspds0[8]:  # 向上步进
                        # 检查此时的isk 是否处于最新的nsckls上
                        if i == nsckls[-1][1][-1][1]:  # 该聚合链是新前沿，向上步进
                            nscklidx = len(nsckls) - 1
                            qsprti = i
                            nscklitp = nsckls[-1][0]
                            qspbi = nsckls[-1][1][0][0]
                            qspei = nsckls[-1][1][-1][1]
                            qspbsdp = nsckls[-1][1][0][2]
                            qspesdp = nsckls[-1][1][-1][3]
                            qspbp = min(sk_low[qspbi], sk_low[qspbi - 1])
                            qspep = sk_high[qspei]
                            qspds.append([qsprti, nscklidx, nscklitp, qspbi, qspei, qspbsdp, qspesdp, qspbp, qspep])

                        else:  # 该isk还还不在一个聚合链上，但一定在最新的单链上，将此单链作为趋势前沿
                            nscklidx = 0
                            qsprti = i
                            nscklitp = 1
                            qspbi = ckls[-1][0]
                            qspei = ckls[-1][1]
                            qspbsdp = ckls[-1][2]
                            qspesdp = ckls[-1][3]
                            qspbp = min(sk_low[qspbi], sk_low[qspbi - 1])
                            qspep = sk_high[qspei]
                            qspds.append([qsprti, nscklidx, nscklitp, qspbi, qspei, qspbsdp, qspesdp, qspbp, qspep])

                    elif sk_close[i] < zslp:  # iqspds0[7]:  # 趋势前沿向下逆转
                        # 检查此时的isk 是否处于最新的nsckls上
                        if i == nsckls[-1][1][-1][1]:  # 该聚合链是新前沿
                            nscklidx = len(nsckls) - 1
                            qsprti = i
                            nscklitp = nsckls[-1][0]
                            qspbi = nsckls[-1][1][0][0]
                            qspei = nsckls[-1][1][-1][1]
                            qspbsdp = nsckls[-1][1][0][2]
                            qspesdp = nsckls[-1][1][-1][3]
                            qspbp = max(sk_high[qspbi], sk_high[qspbi - 1])
                            qspep = sk_low[qspei]
                            qspds.append([qsprti, nscklidx, nscklitp, qspbi, qspei, qspbsdp, qspesdp, qspbp, qspep])

                        else:  # 该isk还还不在一个聚合链上，但一定在最新的单链上，将此单链作为趋势前沿
                            nscklidx = 0
                            qsprti = i
                            nscklitp = -1
                            qspbi = ckls[-1][0]
                            qspei = ckls[-1][1]
                            qspbsdp = ckls[-1][2]
                            qspesdp = ckls[-1][3]
                            qspbp = max(sk_high[qspbi], sk_high[qspbi - 1])
                            qspep = sk_low[qspei]
                            qspds.append([qsprti, nscklidx, nscklitp, qspbi, qspei, qspbsdp, qspesdp, qspbp, qspep])

                    if i == qspds[-1][4] + 1:  # 更新右端极值点
                        if qspds[-1][2] > 0:
                            qspep = max(sk_high[i], qspds[-1][8])
                            qspds[-1][8] = qspep
                        elif qspds[-1][2] < 0:
                            qspep = min(sk_low[i], qspds[-1][8])
                            qspds[-1][8] = qspep

                elif iqspds0[2] < 0:  # 之前的趋势是向下前沿
                    if sk_ckl[i][0] > 0:
                        if not bscp:
                            bscp = sk_low[i]
                        else:
                            bscp = min(bscp, sk_low[i])
                    if bscp and sk_close[i] < bscp:
                        bsbj = -1
                    # 最新的isk与之前的趋势前沿同处于一个聚合链或单链上--延伸
                    if i == nsckls[-1][1][-1][1] and nsckls[-1][1][0][0] <= iqspds0[3]:  # 最新的isk与之前的趋势前沿同处于一个聚合链
                        nscklidx = len(nsckls) - 1
                        qsprti = iqspds0[0]
                        nscklitp = nsckls[-1][0]
                        qspbi = nsckls[-1][1][0][0]
                        qspei = nsckls[-1][1][-1][1]
                        qspbsdp = nsckls[-1][1][0][2]
                        qspesdp = nsckls[-1][1][-1][3]
                        qspbp = max(sk_high[qspbi], sk_high[qspbi - 1])
                        qspep = min(qspds[-1][8], sk_low[qspei])
                        qspds[-1] = [qsprti, nscklidx, nscklitp, qspbi, qspei, qspbsdp, qspesdp, qspbp, qspep]

                    elif iqspds0[4] >= ckls[-1][0] and iqspds0[4] <= ckls[-1][1]:  # 最新的isk与之前的趋势前沿同处于一个单链
                        nscklidx = 0
                        qsprti = iqspds0[0]
                        nscklitp = -1
                        qspbi = ckls[-1][0]
                        qspei = ckls[-1][1]
                        qspbsdp = ckls[-1][2]
                        qspesdp = ckls[-1][3]
                        qspbp = max(sk_high[qspbi], sk_high[qspbi - 1])
                        qspep = min(qspds[-1][8], sk_low[qspei])
                        qspds[-1] = [qsprti, nscklidx, nscklitp, qspbi, qspei, qspbsdp, qspesdp, qspbp, qspep]

                    elif sk_close[i] < iqspds0[8]:  # 向下步进
                        # 检查此时的isk 是否处于最新的nsckls上
                        if i == nsckls[-1][1][-1][1]:  # 该聚合链是新前沿，向下步进
                            nscklidx = len(nsckls) - 1
                            qsprti = i
                            nscklitp = nsckls[-1][0]
                            qspbi = nsckls[-1][1][0][0]
                            qspei = nsckls[-1][1][-1][1]
                            qspbsdp = nsckls[-1][1][0][2]
                            qspesdp = nsckls[-1][1][-1][3]
                            qspbp = max(sk_high[qspbi], sk_high[qspbi - 1])
                            qspep = sk_low[qspei]
                            qspds.append([qsprti, nscklidx, nscklitp, qspbi, qspei, qspbsdp, qspesdp, qspbp, qspep])

                        else:  # 该isk还还不在一个聚合链上，但一定在最新的单链上，将此单链作为趋势前沿
                            nscklidx = 0
                            qsprti = i
                            nscklitp = -1
                            qspbi = ckls[-1][0]
                            qspei = ckls[-1][1]
                            qspbsdp = ckls[-1][2]
                            qspesdp = ckls[-1][3]
                            qspbp = max(sk_high[qspbi], sk_high[qspbi - 1])
                            qspep = sk_low[qspei]
                            qspds.append([qsprti, nscklidx, nscklitp, qspbi, qspei, qspbsdp, qspesdp, qspbp, qspep])

                    elif sk_close[i] > zshp:  # iqspds0[7]:  # 趋势前沿向上逆转
                        # 检查此时的isk 是否处于最新的nsckls上
                        if i == nsckls[-1][1][-1][1]:  # 该聚合链是新前沿，向上逆转
                            nscklidx = len(nsckls) - 1
                            qsprti = i
                            nscklitp = nsckls[-1][0]
                            qspbi = nsckls[-1][1][0][0]
                            qspei = nsckls[-1][1][-1][1]
                            qspbsdp = nsckls[-1][1][0][2]
                            qspesdp = nsckls[-1][1][-1][3]
                            qspbp = min(sk_low[qspbi], sk_low[qspbi - 1])
                            qspep = sk_high[qspei]
                            qspds.append([qsprti, nscklidx, nscklitp, qspbi, qspei, qspbsdp, qspesdp, qspbp, qspep])

                        else:  # 该isk还还不在一个聚合链上，但一定在最新的单链上，将此单链作为趋势前沿
                            nscklidx = 0
                            qsprti = i
                            nscklitp = 1
                            qspbi = ckls[-1][0]
                            qspei = ckls[-1][1]
                            qspbsdp = ckls[-1][2]
                            qspesdp = ckls[-1][3]
                            qspbp = min(sk_low[qspbi], sk_low[qspbi - 1])
                            qspep = sk_high[qspei]
                            qspds.append([qsprti, nscklidx, nscklitp, qspbi, qspei, qspbsdp, qspesdp, qspbp, qspep])

                    if i == qspds[-1][4] + 1:  # 更新右端极值点
                        if qspds[-1][2] > 0:
                            qspep = max(sk_high[i], qspds[-1][8])
                            qspds[-1][8] = qspep
                        elif qspds[-1][2] < 0:
                            qspep = min(sk_low[i], qspds[-1][8])
                            qspds[-1][8] = qspep
            newsgn = None
            if len(qspds) <= 0:
                qsprti = i
                nscklidx = 0
                nscklitp = 0
                qspbi = 0
                qspei = i
                qspbsdp = sk_open[0]
                qspesdp = sk_close[i]
                qspbp = sk_open[0]
                qspep = sk_close[i]
                zslp = cksdl
                zshp = cksdh
                bslp = cksdl
                bshp = cksdh
                sk_sgn.append(None)
                sgnans.updaterpt(i)
            else:
                qsprti = qspds[-1][0]
                nscklidx = qspds[-1][1]
                nscklitp = qspds[-1][2]
                qspbi = qspds[-1][3]
                qspei = qspds[-1][4]
                qspbsdp = qspds[-1][5]
                qspesdp = qspds[-1][6]
                qspbp = qspds[-1][7]
                qspep = qspds[-1][8]
                # 对于当前的isk, 更新zs
                iqspds0 = qspds[-1]
                headqsp = sk_cklsm[qspds[-1][4]]  # 趋势前沿头部 triple ckls
                zsdir = iqspds0[2]
                # dtmi= pd.to_datetime(sk_time[i])
                # if '2010-11-17' in str(dtmi):
                #     print 'none'
                if len(headqsp[1]) > 1:
                    zsckl = headqsp[1][1]
                    zsski = zsckl[1]
                    bsski = zsckl[0]
                    if nscklitp > 0:
                        zslp = min(sk_low[zsski], sk_low[zsski + 1])  # sk_low[zsski]
                        zshp = max(min(sk_open[zsski], sk_close[zsski]), min(sk_open[zsski + 1], sk_close[
                            zsski + 1]))  # min(sk_open[zsski],sk_close[zsski])   max(sk_low[zsski], sk_low[zsski+1])
                        zshp = zslp
                        bslp = sorted([max(sk_open[bsski], sk_close[bsski]), max(sk_open[bsski - 1], sk_close[bsski - 1]),
                                       max(sk_open[bsski - 2], sk_close[bsski - 2])])[1]  # min(sk_high[bsski], sk_high[bsski - 1]) #
                        bshp = sorted([sk_high[bsski], sk_high[bsski - 1], sk_high[bsski - 2]])[
                            1]  # max(max(sk_open[bsski], sk_close[bsski]), max(sk_open[bsski-1], sk_close[bsski-1])) #min(sk_high[bsski], sk_high[bsski - 1]) #max(sk_high[bsski], sk_high[bsski - 1])
                    else:
                        zshp = max(sk_high[zsski], sk_high[zsski + 1])  # sk_high[zsski]
                        zslp = min(max(sk_open[zsski], sk_close[zsski]),
                                   max(sk_open[zsski + 1], sk_close[zsski + 1]))  # max(sk_open[zsski], sk_close[zsski])
                        zslp = zshp
                        bslp = sorted([sk_low[bsski], sk_low[bsski - 1], sk_low[bsski - 2]])[
                            1]  # min(min(sk_open[bsski], sk_close[bsski]), min(sk_open[bsski-1], sk_close[bsski-1])) # max(sk_low[bsski], sk_low[bsski - 1])   # min(sk_low[bsski], sk_low[bsski - 1])
                        bshp = sorted([min(sk_open[bsski], sk_close[bsski]), min(sk_open[bsski - 1], sk_close[bsski - 1]),
                                       min(sk_open[bsski - 2], sk_close[bsski - 2])])[1]  # max(sk_low[bsski], sk_low[bsski - 1]) #

                        # zslp = sk_low[zsckl[1]]
                        # zshp = sk_high[zsckl[1]]
                else:
                    zsckl = headqsp[1][0]
                    zsski = zsckl[0]
                    bsski = zsski - abs(sk_ckl[zsski - 1][0])
                    if nscklitp > 0:
                        zslp = min(sk_low[zsski], sk_low[zsski - 1])  # sk_low[zsski]
                        zshp = max(min(sk_open[zsski], sk_close[zsski]),
                                   min(sk_open[zsski - 1], sk_close[zsski - 1]))  # min(sk_open[zsski],sk_close[zsski])
                        zshp = zslp
                        bslp = sorted([max(sk_open[bsski], sk_close[bsski]), max(sk_open[bsski - 1], sk_close[bsski - 1]),
                                       max(sk_open[bsski - 2], sk_close[bsski - 2])])[1]  # min(sk_high[bsski], sk_high[bsski - 1])
                        bshp = sorted([sk_high[bsski], sk_high[bsski - 1], sk_high[bsski - 2]])[
                            1]  # max(max(sk_open[bsski], sk_close[bsski]), max(sk_open[bsski-1], sk_close[bsski-1])) # max(sk_high[bsski], sk_high[bsski - 1])
                    else:
                        zshp = max(sk_high[zsski], sk_high[zsski - 1])  # sk_high[zsski]
                        zslp = min(max(sk_open[zsski], sk_close[zsski]),
                                   max(sk_open[zsski - 1], sk_close[zsski - 1]))  # min(sk_open[zsski], sk_close[zsski])
                        zslp = zshp
                        bslp = sorted([sk_low[bsski], sk_low[bsski - 1], sk_low[bsski - 2]])[
                            1]  # min(min(sk_open[bsski], sk_close[bsski]), min(sk_open[bsski-1], sk_close[bsski-1]))  #  min(sk_low[bsski], sk_low[bsski - 1])
                        bshp = sorted([min(sk_open[bsski], sk_close[bsski]), min(sk_open[bsski - 1], sk_close[bsski - 1]),
                                       min(sk_open[bsski - 2], sk_close[bsski - 2])])[1]  # max(sk_low[bsski], sk_low[bsski - 1])
                        # zslp = sk_low[zsckl[0]]
                        # zshp = sk_high[zsckl[0]]
                # ------------------------------更新 qsbands, zsbands
                if nscklitp > 0:
                    bandlp = qspbp
                    bandhp = min(min(sk_open[qspbi], sk_close[qspbi]), min(sk_open[qspbi - 1], sk_close[qspbi - 1]))
                    newband = Rsband(qspbi, qspei, bandhp, bandlp)
                    if not lstupqsbd or lstupqsbd.dtbi != newband.dtbi:
                        upqsbands.addband(newband)
                        lstupqsbd = newband
                    elif lstupqsbd.dtei != newband.dtei:
                        upqsbands.updateband(newband)
                        lstupqsbd = newband
                # --------------------------------------------------
                elif nscklitp < 0:
                    bandhp = qspbp
                    bandlp = max(max(sk_open[qspbi], sk_close[qspbi]), max(sk_open[qspbi - 1], sk_close[qspbi - 1]))
                    newband = Rsband(qspbi, qspei, bandhp, bandlp)
                    if not lstdwqsbd or lstdwqsbd.dtbi != newband.dtbi:
                        dwqsbands.addband(newband)
                        lstdwqsbd = newband
                    elif lstdwqsbd.dtei != newband.dtei:
                        dwqsbands.updateband(newband)
                        lstdwqsbd = newband
                # --------------------------------------------------

                if sk_qspds[-1][2] > 0 and nscklitp < 0:
                    newband = copy.copy(lstupzsbd)
                    newband.dtbi = i
                    newband.dtei = i
                    dwzsbands.addband(newband)
                if sk_qspds[-1][2] < 0 and nscklitp > 0:
                    newband = copy.copy(lstdwzsbd)
                    newband.dtbi = i
                    newband.dtei = i
                    upzsbands.addband(newband)

                newband = Rsband(zsski, zsski, zshp, zslp)
                if zsdir > 0:
                    if not lstupzsbd or lstupzsbd.dtbi != newband.dtbi:
                        upzsbands.addband(newband)
                        lstupzsbd = newband
                elif zsdir < 0:
                    if not lstdwzsbd or lstdwzsbd.dtbi != newband.dtbi:
                        dwzsbands.addband(newband)
                        lstdwzsbd = newband

                # --------------------------------------------------
                # 更新 ----------------------------------------------sk_sgn
                lstsgn = sk_sgn[-1]
                sgndir = 0
                newsgn = Sgn_Rst(0, i, sk_close[i])
                if not lstsgn:
                    newsgn.rsti = i
                    newsgn.rstp = sk_close[i]
                    newsgn.rstbi = qspbi
                    if nscklitp > 0:
                        sgndir = 1
                        upqsbands.updateformdti(newsgn.rstbi, newsgn.rstp)
                        upzsbands.updateformdti(newsgn.rstbi, newsgn.rstp)
                    if nscklitp < 0:
                        sgndir = -1
                        dwqsbands.updateformdti(newsgn.rstbi, newsgn.rstp)
                        dwzsbands.updateformdti(newsgn.rstbi, newsgn.rstp)
                else:
                    lstsgn.set_sgn(sk_open[i], sk_high[i], sk_low[i], sk_close[i], sk_atr[i])
                    # dtmi= pd.to_datetime(sk_time[i])
                    # if '2011-10-28' in str(dtmi):
                    #     print lstsgn.sgn_qs2c
                    #     print 'chk'

                    newsgn.rsti = lstsgn.rsti
                    newsgn.rstp = lstsgn.rstp
                    newsgn.rstbi = lstsgn.rstbi
                    if lstsgn.rstdir > 0:
                        sgndir = 1

                        if lstsgn.sgn_qs1c and lstsgn.sgn_qs1c[0] <= -5:

                            if dwqsbands.count > 0:
                                sgndir = -1
                                newsgn.rsti = i

                                newsgn.rstp = lstsgn.rsp_qs1c
                                dwrsband = dwqsbands.getbandby_bmp('max')
                                newsgn.rstbi = dwrsband.dtbi
                                dwqsbands.updateformdti(newsgn.rstbi, newsgn.rstp)
                                dwzsbands.updateformdti(newsgn.rstbi, newsgn.rstp)
                                # elif not lstsgn.sgn_qs2c and lstsgn.sgn_qs1c and lstsgn.sgn_qs1c[0] <= -5:
                                #
                                #     if dwqsbands.count>0:
                                #         sgndir = -1
                                #         newsgn.rsti = i
                                #
                                #         newsgn.rstp = lstsgn.rsp_qs1c
                                #         dwrsband = dwqsbands.getbandby_bmp('max')
                                #         newsgn.rstbi = dwrsband.dtbi
                                #         dwqsbands.updateformdti(newsgn.rstbi, newsgn.rstp)
                                #         dwzsbands.updateformdti(newsgn.rstbi, newsgn.rstp)

                    else:
                        sgndir = -1

                        if lstsgn.sgn_qs1c and lstsgn.sgn_qs1c[0] >= 5:

                            if upqsbands.count > 0:
                                sgndir = 1
                                newsgn.rsti = i

                                newsgn.rstp = lstsgn.rsp_qs1c
                                uprsband = upqsbands.getbandby_bmp('min')
                                newsgn.rstbi = uprsband.dtbi
                                upqsbands.updateformdti(newsgn.rstbi, newsgn.rstp)
                                upzsbands.updateformdti(newsgn.rstbi, newsgn.rstp)
                                # elif not lstsgn.sgn_qs2c and lstsgn.sgn_qs1c and lstsgn.sgn_qs1c[0] >= 5:
                                #
                                #     if upqsbands.count>0:
                                #         sgndir = 1
                                #         newsgn.rsti = i
                                #
                                #         newsgn.rstp = lstsgn.rsp_qs1c
                                #         uprsband = upqsbands.getbandby_bmp('min')
                                #         newsgn.rstbi = uprsband.dtbi
                                #         upqsbands.updateformdti(newsgn.rstbi, newsgn.rstp)
                                #         upzsbands.updateformdti(newsgn.rstbi, newsgn.rstp)
                if sgndir > 0:
                    newsgn.rstdir = 1
                    newsgn.setqsrsp(upqsbands)
                    newsgn.setzsrsp(upzsbands)

                elif sgndir < 0:
                    newsgn.rstdir = -1
                    newsgn.setqsrsp(dwqsbands)
                    newsgn.setzsrsp(dwzsbands)

                else:
                    newsgn = None

                sk_sgn.append(newsgn)
                # dtmi= pd.to_datetime(sk_time[i])
                # if '2010-07-28' in str(dtmi):
                #     print 'chk'

                sgnans.updaterpt(i)
                # 更新 ----------------------------------------------sk_sgn

            if newsgn:
                sk_zs1c.append(newsgn.rsp_zs1c if newsgn.rsp_zs1c else np.nan)
                sk_zs1a.append(newsgn.rsp_zs1a if newsgn.rsp_zs1a else np.nan)
                sk_zs2c.append(newsgn.rsp_zs2c if newsgn.rsp_zs2c else np.nan)
                sk_zs2a.append(newsgn.rsp_zs2a if newsgn.rsp_zs2a else np.nan)
                sk_qs1c.append(newsgn.rsp_qs1c if newsgn.rsp_qs1c else np.nan)
                sk_qs1a.append(newsgn.rsp_qs1a if newsgn.rsp_qs1a else np.nan)
                sk_qs2c.append(newsgn.rsp_qs2c if newsgn.rsp_qs2c else np.nan)
                sk_qs2a.append(newsgn.rsp_qs2a if newsgn.rsp_qs2a else np.nan)
                sk_zsrpt.append(sgnans.rptlist[-1][0])
                sk_qsrpt.append(sgnans.rptlist[-1][1])
                sk_bsfact.append(sgnans.bslist[-1] if sgnans.bslist[-1] else np.nan)
            else:
                sk_zs1c.append(np.nan)
                sk_zs1a.append(np.nan)
                sk_zs2c.append(np.nan)
                sk_zs2a.append(np.nan)
                sk_qs1c.append(np.nan)
                sk_qs1a.append(np.nan)
                sk_qs2c.append(np.nan)
                sk_qs2a.append(np.nan)
                sk_zsrpt.append(0)
                sk_qsrpt.append(0)
                sk_bsfact.append(np.nan)
            sk_qspds.append([qsprti, nscklidx, nscklitp, qspbi, qspei, qspbsdp, qspesdp, qspbp, qspep])
            '''
              ==============以下是信号部分==============
            '''
            sk_zsl.append(zslp)
            sk_zsh.append(zshp)
            sk_bsl.append(bslp)
            sk_bsh.append(bshp)

            sk_itp.append(sk_qspds[-1][2])
            if sk_qspds[-1][2] > 0:
                sk_qsh.append(sk_qspds[-1][8])
                sk_qsl.append(sk_qspds[-1][7])
                sk_qswr.append((sk_qsh[-1] - sk_qsl[-1]) / sk_atr[i])
                sk_rsl.append(0.2 + (sk_qsh[-1] - sk_close[i]) / (sk_qsh[-1] - sk_qsl[-1]))
                sk_disrst.append(sk_qsh[-1])

                # ---------------------------------------------------------------------------------------------------trdline
                if ctp:
                    if ctp.skp < sk_high[i]:
                        ctp = Extrp(i, sk_high[i], 1)

                        # ----------------------------------------------------------------------------------------------------
            elif sk_qspds[-1][2] < 0:
                sk_qsh.append(sk_qspds[-1][7])
                sk_qsl.append(sk_qspds[-1][8])
                sk_qswr.append(-(sk_qsh[-1] - sk_qsl[-1]) / sk_atr[i])
                sk_rsl.append(-0.2 + (sk_qsl[-1] - sk_close[i]) / (sk_qsh[-1] - sk_qsl[-1]))
                sk_disrst.append(sk_qsl[-1])

                # ---------------------------------------------------------------------------------------------------trdline
                if cbp:
                    if cbp.skp > sk_low[i]:
                        cbp = Extrp(i, sk_low[i], -1)

                        # ----------------------------------------------------------------------------------------------------

            else:
                sk_qsh.append(sk_qspds[-1][7])
                sk_qsl.append(sk_qspds[-1][8])
                sk_qswr.append(0)
                sk_rsl.append(0)
                sk_disrst.append(sk_qsl[-1])

            if len(sk_qspds) > 1 and sk_qspds[-1][2] > 0 and sk_qspds[-2][2] < 0:  # 向上转换
                sgn_rsti = i
                sgn_rstp = sk_qspds[-2][7]
                sgn_rstdir = 1
                qsrstp.append((sgn_rsti, sgn_rstp, sgn_rstdir))
                sk_qsrstp.append(sgn_rstdir)
                sk_rstspl.append(sk_bsl[-2])
                sk_rstsph.append(sk_bsh[-2])
                bscp = None
                # ---------------------------------------------------------------------------------------------------trdline
                ctp = Extrp(i, sk_high[i], 1)
                if cbp:
                    self.botms.append(cbp)
                self.update_supline(sk_open, sk_high, sk_low, sk_close, sk_volume, sk_time, sk_atr, i)

            elif len(sk_qspds) > 1 and sk_qspds[-1][2] < 0 and sk_qspds[-2][2] > 0:  # 向下转换
                sgn_rsti = i
                sgn_rstp = sk_qspds[-2][7]
                sgn_rstdir = -1
                qsrstp.append((sgn_rsti, sgn_rstp, sgn_rstdir))
                sk_qsrstp.append(sgn_rstdir)
                sk_rstspl.append(sk_bsl[-2])
                sk_rstsph.append(sk_bsh[-2])
                bscp = None
                # ---------------------------------------------------------------------------------------------------trdline
                cbp = Extrp(i, sk_low[i], -1)
                if ctp:
                    self.tops.append(ctp)
                self.update_resline(sk_open, sk_high, sk_low, sk_close, sk_volume, sk_time, sk_atr, i)
            else:
                sk_qsrstp.append(0)
                if bsbj != 0:
                    sk_rstspl.append(sk_close[i])
                    sk_rstsph.append(sk_close[i])
                    bscp = None
                else:
                    sk_rstspl.append(sk_rstspl[-1])
                    sk_rstsph.append(sk_rstsph[-1])

            if self.crtbbl:
                sk_bbl.append(self.crtbbl.extendp(i))
            else:
                sk_bbl.append(sk_disrst[-1])

            if self.crtttl:
                sk_ttl.append(self.crtttl.extendp(i))
            else:
                sk_ttl.append(sk_disrst[-1])

        self.quotes['qrst'] = sk_qsrstp
        self.quotes['qsh'] = sk_qsh
        self.quotes['qsl'] = sk_qsl
        self.quotes['zsh'] = sk_zsh
        self.quotes['zsl'] = sk_zsl
        self.quotes['qswr'] = sk_qswr
        self.quotes['rsl'] = sk_rsl
        self.quotes['itp'] = sk_itp
        self.quotes['disrst'] = sk_disrst
        self.quotes['bbl'] = sk_bbl
        self.quotes['ttl'] = sk_ttl
        self.quotes['rstspl'] = sk_rstspl
        self.quotes['rstsph'] = sk_rstsph

        self.quotes['bsl'] = sk_bsl
        self.quotes['bsh'] = sk_bsh

        self.quotes['sk_zs1c'] = sk_zs1c
        self.quotes['sk_zs1a'] = sk_zs1a
        self.quotes['sk_zs2c'] = sk_zs2c
        self.quotes['sk_zs2a'] = sk_zs2a
        self.quotes['sk_qs1c'] = sk_qs1c
        self.quotes['sk_qs1a'] = sk_qs1a
        self.quotes['sk_qs2c'] = sk_qs2c
        self.quotes['sk_qs2a'] = sk_qs2a
        self.quotes['sk_zsrpt'] = sk_zsrpt
        self.quotes['sk_qsrpt'] = sk_qsrpt
        self.quotes['sk_bsfact'] = sk_bsfact
        return self.quotes