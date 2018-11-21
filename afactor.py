# -*- coding: cp936 -*-
__author__ = 'naivego'

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import csv
#from datetime import datetime
from datetime import datetime, timedelta
import  copy
from itertools import combinations, permutations
from abtest import *
from  collections import OrderedDict

#---------------------------------------------------------------------------
# sk 与 rsline 的触及关系
def sklreach(sk_open, sk_high, sk_low, sk_close, rsp, dir = 'dw', atr = 0.016 ):
    det = 0.05 * atr * sk_close
    atl = 0
    if dir == 'dw':
        if sk_low > rsp + det * 2:
            atl = 3
        elif  rsp + det * 2  >=  sk_low > rsp + det * 0.5:
            atl = 2
        elif  rsp -det * 1 >  sk_close >= rsp - det * 2  and  sk_high > rsp:
            atl = -4
        elif  rsp - det * 2 >  sk_close and  sk_high > rsp:
            atl = -5
        elif sk_high <= rsp:
            atl = -6
        else: #  rsp + det * 0.5  >=  sk_low >= rsp - det * 0.5:
            atl = 1

        if sk_close >= sk_open:
            dwrp = (sk_close - sk_low) / (sk_close * atr)
        else:
            dwrp = (2*sk_close - sk_low - sk_open) / (sk_close * atr)
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



#---------------------------------------------------------------------------
# 极值点: 位置、价格、高低点类型，-1：低点， 1：高点， 0：一般点
class Extrp(object):
    def __init__(self, ski, skp, tob):
        self.ski = ski
        self.skp = skp
        self.tob = tob

# 被tdl分割的sk集合区域
class Sadl(object):
    def __init__(self, dwup=1, bi=None, ei=None, bap=None):
        self.dwup = dwup
        self.bap = bap
        self.bi = bi
        self.ei = ei
        self.upti = 0
        self.cn = 0
        self.mdp = None
        self.mdi = None
        self.mp = None
        self.mi = None
        self.sdp = 0
        self.mret = 1 # sk 偏离tdl最远距离后回归tdl的百分比
        self.chg = 0
        self.rsti=None
        self.rstp=None

    def uptsta(self, sk_open, sk_high, sk_low, sk_close, sk_atr, ski):
        print 'uptsta'

# ---------------------------------------------------------------------------
class Rsline(object):
    def __init__(self, linesk, trpb, trpd, atr, tbl):
        pass


#---------------------------------------------------------------------------
class Trpline(object):
    def __init__(self, trpb, trpd, atr, tbl):
        self.trpb = trpb  # 起点
        self.trpd = trpd  # 端点
        self.tbl= tbl     # 趋势线类型 'ttl' or 'bbl'
        self.dir = 1 if tbl == 'bbl' else -1
        self.tdlna = tbl+'_' + str(trpb.ski) + '_' + str(trpd.ski)
        self.socna = None
        self.fsocna = None
        self.ak = (trpd.skp - trpb.skp)/(trpd.ski- trpb.ski)
        self.rk = (trpd.skp - trpb.skp)/(trpd.ski- trpb.ski)/trpd.skp/atr  # 平均每日涨幅相对atr的倍数
        self.fbi = None
        self.mxi = None
        self.btm = None #  tdl的起点时间
        self.dtm = None  # tdl的右端点时间
        self.frtm = None # 生成tdl的时间
        self.srk  = None  # 斜率标准得分
        self.srsk = None  # 对sk阻挡标准得分
        self.sfs  = 0     # 合计标准得分
        self.ocover = 0
        self.hlover = 0
        self.pdreach = 0

        self.initi = None
        self.exti = self.trpd.ski
        self.extp = self.trpd.skp

        self.bki = None   # 被sk突破的位置 None： 未被突破
        self.bkp = None   # 被sk突破的价格
        self.eop = None   # 突破SK外极点
        self.eip = None   # 临界sk内极点

        self.bkcn= 0   # 突破次数
        self.rsta = 0     # sk 与该趋势线的关系状态 0：未被突破，  >0:被突破 -1：失效
        self.crsp = None  # 预计当前对sk阻挡的价格（如果 失效则为None ）
        self.rspdet = None  # sk收盘价与趋势阻挡价差相对于atr的倍数
        self.mpti = None  # sk尖端偏离tdl最远的位置
        self.mptv = None  # sk尖端偏离tdl最远的价格
        self.bkmpti = None  # 突破tdl后的sk尖端偏离tdl最远的位置
        self.bkmptv = None  # 突破tdl后的sk尖端偏离tdl最远的价格
        # ----------------- fibo 信号相关
        self.sfib = None # 构造fibo得分
        self.fib0 = None
        self.fib1 = None
        self.fibr = None
        self.fib16 = None
        self.fib2 = None
        self.fib26 = None
        self.fib3 = None
        self.fib42 = None
        self.catfb = None # 当前收盘价处于fibon标尺中的位置
        self.fbrh0 = None

        #-----------------跟交易进出场相关的信号统计
        self.bkp_rhcn = 0
        self.bkp_ovcn = 0
        self.bkp_rhi  = None
        self.bkp_ovi = None
        self.bkp_ovsti = None
        self.bkp_ovstp = None

        self.extp_rhi = None
        self.extp_rhcn = 0
        self.extp_rhsti = None
        self.extp_rhstp = None
        self.extp_ovi = None
        self.extp_ovcn = 0

        self.reb_enstp = None
        self.reb_ensti = None

        self.bk_ensti = None
        self.bk_enstp = None
        self.skat_bkp = 0
        self.skat_extp = 0
        self.skov_bkp = 0
        self.skov_extp = 0
        self.mirp = None
        self.bkmirp = None
        # ------------------------------sadl相关
        self.sadls =[]
        self.tepups =None
        self.tepdws =None
        self.crtups =None
        self.crtdws = None
        self.mdwsadl =None
        self.mupsadl =None
        self.dwmdis = []
        self.dwmdps = []
        self.upmdis = []
        self.upmdps = []
        self.dwsmdp = None
        self.dwsmdi = None
        self.upsmdp = None
        self.upsmdi = None
        self.dwsmp = None
        self.dwsmi = None
        self.upsmp = None
        self.upsmi = None

        # ----------------------tdl相对于本周期sk的位置状态

        self.se_ini = None  # 生成tdl时在外部sk的索引
        self.se_upti = None  # 最近更新时的索引i
        self.se_sta = None  # sk 相对tdl的状态，偶数--在tdl内侧，奇数--外侧 每发生穿越，值增加1
        self.se_beks = []   # sk向外侧穿越tdl的ski列表
        self.se_reks = []   # sk向内侧穿越tdl的ski列表
        self.se_berhs = []  # sk从外侧触及tdl的ski列表
        self.se_rerhs = []  # sk从内侧触及tdl的ski列表

        self.se_bklp = None
        self.se_bkl_sta = None  # sk 相对bkl的状态，偶数--在bkl内侧，奇数--外侧 每发生穿越，值增加1
        self.se_bkl_beks = []  # sk向外侧穿越tdl的ski列表
        self.se_bkl_reks = []  # sk向内侧穿越tdl的ski列表
        self.se_bkl_berhs = []  # sk从外侧触及bkl的ski列表
        self.se_bkl_rerhs = []  # sk从内侧触及bkl的ski列表

        self.se_bki = None  # 反式突破i
        self.se_bekp = None  # 反式开仓价
        self.se_besp = None  # 反式止损价

        self.se_bek1i = None   #
        self.se_bek2i = None   #
        self.se_bek3i = None  #
        self.se_bek4i = None  #
        self.se_bek0sta = None
        self.se_bek1sta = None
        self.se_bek2sta = None
        self.se_bek3sta = None
        self.se_bek4sta = None

        self.se_rti = None  # 回归突破i
        self.se_rekp = None  # 回归开仓价
        self.se_resp = None  # 回归止损价

        self.se_rek1i = None  #
        self.se_rek2i = None  #
        self.se_rek3i = None  #

        self.se_rek0sta = None
        self.se_rek1sta = None
        self.se_rek2sta = None
        self.se_rek3sta = None

        #----------------------tdl相对于外部周期sk的位置状态
        self.et_ini  = None  # 生成tdl时在外部sk的索引
        self.et_upti = None  # 最近更新时的索引i
        self.et_sta = None  # sk 相对tdl的状态，偶数--在tdl内侧，奇数--外侧 每发生穿越，值增加1
        self.et_beks = []  # sk向外侧穿越tdl的ski列表
        self.et_reks = []  # sk向内侧穿越tdl的ski列表
        self.et_berhs = []  # sk从外侧触及tdl的ski列表
        self.et_rerhs = []  # sk从内侧触及tdl的ski列表

        self.et_bklp = None
        self.et_bkl_sta = None  # sk 相对bkl的状态，偶数--在bkl内侧，奇数--外侧 每发生穿越，值增加1
        self.et_bkl_beks = []  # sk向外侧穿越tdl的ski列表
        self.et_bkl_reks = []  # sk向内侧穿越tdl的ski列表
        self.et_bkl_berhs = []  # sk从外侧触及bkl的ski列表
        self.et_bkl_rerhs = []  # sk从内侧触及bkl的ski列表


        self.et_bki  = None  # 反式突破i
        self.et_bekp = None  # 反式开仓价
        self.et_besp = None  # 反式止损价

        self.et_bek1i = None  #
        self.et_bek2i = None  #
        self.et_bek3i = None  #
        self.et_bek4i = None  #
        self.et_bek0sta = None
        self.et_bek1sta = None
        self.et_bek2sta = None
        self.et_bek3sta = None
        self.et_bek4sta = None

        self.et_rti = None  # 回归突破i
        self.et_rekp = None  # 回归开仓价
        self.et_resp = None  # 回归止损价
        self.et_rek1i = None  #
        self.et_rek2i = None  #
        self.et_rek3i = None  #
        self.et_rek0sta = None
        self.et_rek1sta = None
        self.et_rek2sta = None
        # ------------------------------交易信号
        self.trpkops = {}
        self.trpcsts = {}
        self.trpctps = {}

        #-----------------有效状态
        self.trgi = 0
        self.vak0 = 0
        self.vak1 = 0
        self.vak3 = 0
        self.vak5 = 0
        self.vak7 = 0
        self.vak2 = 0
        self.vak4 = 0
        self.vak6 = 0
        self.vak8 = 0


        self.tdk0 = None
        self.tdk1 = None
        self.tdk3 = None
        self.tdk5 = None
        self.tdk7 = None
        self.tdk2 = None
        self.tdk4 = None
        self.tdk6 = None
        self.tdk8 = None
        # ---------------
        self.cst1 = None
        self.cst3 = None
        self.cst5 = None
        self.cst7 = None
        self.cst2 = None
        self.cst4 = None
        self.cst6 = None
        self.cst8 = None
        # --------------
        self.csi1 = None
        self.csi3 = None
        self.csi5 = None
        self.csi7 = None
        self.csi2 = None
        self.csi4 = None
        self.csi6 = None
        self.csi8 = None
        # --------------
        self.ctp1 = None
        self.ctp3 = None
        self.ctp5 = None
        self.ctp7 = None
        self.ctp2 = None
        self.ctp4 = None
        self.ctp6 = None
        self.ctp8 = None
        #---------------

    # -------------------------------------
    def extendp(self, exti):
        return self.trpb.skp + self.ak * (exti - self.trpb.ski)

    # -------------------------------------
    def uptsklsta(self, sk_open, sk_high, sk_low, sk_close, sk_atr, sk_ckl, cri):  # 更新趋势线与当前sk的位置状态
        if self.exti>= cri:
            return
        sbi = self.exti + 1
        for ski in range(sbi, cri+1):
            self.uptskista(sk_open, sk_high, sk_low, sk_close, sk_atr, sk_ckl, ski)

    def uptskista(self, sk_open, sk_high, sk_low, sk_close, sk_atr, sk_ckl, ski): # 更新趋势线与当前sk的位置状态
        self.exti = ski
        self.extp = self.extendp(ski)
        atr = sk_atr[ski]
        if self.rsta % 3 == 0:
            if self.tbl == 'bbl':
                if sk_close[ski] < self.extp - atr * sk_close[ski] * 0.2:
                    self.bki = ski
                    self.bkp = self.extp - self.ak
                    self.eop = min(sk_low[ski],sk_low[ski-1])
                    self.eip = max(sk_high[ski],sk_high[ski-1])
                    self.bkcn +=1
                    self.rsta += 1
                    self.bkp_rhcn = 0
                    self.bkp_ovcn = 0
                    self.bk_ensti = None
                    self.reb_ensti = None
                    # self.extp_rhi = None

            elif self.tbl == 'ttl':
                if sk_close[ski] > self.extp + atr * sk_close[ski] * 0.2:
                    self.bki = ski
                    self.bkp = self.extp - self.ak
                    self.eop = max(sk_high[ski], sk_high[ski - 1])
                    self.eip = min(sk_low[ski], sk_low[ski - 1])
                    self.bkcn +=1
                    self.rsta += 1
                    self.bkp_rhcn = 0
                    self.bkp_ovcn = 0
                    self.bk_ensti = None
                    self.reb_ensti = None
                    # self.extp_rhi = None
        elif self.rsta % 3 == 1:
            if self.tbl == 'bbl':
                if sk_close[ski] >= self.extp + atr * sk_close[ski] * 0.05:
                    self.rsta += 1
            elif self.tbl == 'ttl':
                if sk_close[ski] <= self.extp - atr * sk_close[ski] * 0.05:
                    self.rsta += 1
        elif self.rsta  % 3 == 2:  # 回归趋势线临界点 2根sk收到趋势线内部才算回归（虚假突破）
            if self.tbl == 'bbl':
                if sk_close[ski] >= self.extp + atr * sk_close[ski] * 0.2:
                    self.rsta += 1
                elif sk_close[ski] < self.extp - atr * sk_close[ski] * 0.2:
                    self.rsta += -1
            elif self.tbl == 'ttl':
                if sk_close[ski] <= self.extp - atr * sk_close[ski] * 0.2:
                    self.rsta += 1
                elif sk_close[ski] > self.extp + atr * sk_close[ski] * 0.2:
                    self.rsta += -1

        #----------------------------------update
        if self.dir>0:
            diskl = sk_high[ski] - self.extp
            if not self.mptv or diskl >=  self.mptv:
                self.mpti = ski
                self.mptv = diskl
        else:
            diskl = sk_low[ski] - self.extp
            if not self.mptv or diskl <= self.mptv:
                self.mpti = ski
                self.mptv = diskl
        #----------------------------------
        if self.dir>0:
            diskl = sk_low[ski] - self.extp
            if not self.bkmptv or diskl <=  self.bkmptv:
                self.bkmpti = ski
                self.bkmptv = diskl
        else:
            diskl = sk_high[ski] - self.extp
            if not self.bkmptv or diskl >= self.bkmptv:
                self.bkmpti = ski
                self.bkmptv = diskl

        if ski - self.mpti >1:
            self.mirp = self.extp + self.mptv - self.dir * atr * sk_close[ski] * 0.1
        else:
            self.mirp = None

        if ski - self.bkmpti >1:
            self.bkmirp = self.extp + self.bkmptv + self.dir * atr * sk_close[ski] * 0.1
            if self.bkmptv * self.dir >= 0:
                self.bkmirp = None
        else:
            self.bkmirp = None
        #-------------------------------
        bkprh = 0
        bkpderh = 0
        bkpov = 0
        bkpdeov = 0
        extprh = 0
        extpderh = 0
        extpov = 0
        extpdeov = 0
        if self.bkp and ski > self.bki and self.tbl == 'bbl' :  #self.bkp and ski > self.bki
            if sk_high[ski] >= self.bkp + atr * sk_close[ski] * 0.0:
                bkprh = 1
            if sk_high[ski] < self.bkp - atr * sk_close[ski] * 0.1:
                bkpderh = 1
            if bkprh > 0:
                if self.skat_bkp == 0:
                    self.bkp_rhcn += 1
                    self.bkp_rhi = ski
                self.skat_bkp += 1
            if  bkpderh > 0:
                self.skat_bkp = 0
            #----------------------------
            if sk_close[ski] > self.bkp + atr * sk_close[ski] * 0.2:
                bkpov = 1
            if sk_close[ski] < self.bkp - atr * sk_close[ski] * 0.1:
                bkpdeov = 1
            if bkpov > 0:
                if self.skov_bkp == 0:
                    self.bkp_ovcn += 1
                    self.bkp_ovi = ski
                self.skov_bkp += 1

            if bkpdeov > 0:
                self.skov_bkp = 0
            # -------------------------------------
            if not self.bk_ensti:
                if sk_ckl[ski][0] > 0:
                    self.bk_enstp = min(sk_low[ski-1], sk_low[ski]) - atr * sk_close[ski] *0.05
                    self.bk_ensti = ski
            #--------------------------------------
            if ski >= self.bki + 5 and sk_high[ski] >= self.extp + atr * sk_close[ski]* 0.0:
                extprh = 1
            if sk_high[ski] < self.extp - atr * sk_close[ski] * 0.3:
                extpderh = 1
            if extprh > 0:
                if self.skat_extp == 0:
                    self.extp_rhcn += 1
                    self.extp_rhi = ski
                self.skat_extp += 1
            if extpderh > 0:
                self.skat_extp = 0
            # ----------------------------
            if sk_close[ski] > self.extp + atr * sk_close[ski] * 0.2:
                extpov = 1
            if sk_close[ski] < self.extp - atr * sk_close[ski] * 0.1:
                extpdeov = 1
            if extpov > 0:
                if self.skov_extp == 0:
                    self.extp_ovcn += 1
                    self.extp_ovi = ski
                self.skov_extp += 1
            if extpdeov > 0:
                self.skov_extp = 0
        # -----------------------------------------------------------
        elif self.bkp and ski > self.bki and self.tbl == 'ttl':
            if sk_low[ski] <= self.bkp + atr * sk_close[ski] * 0.0:
                bkprh = 1
            if sk_low[ski] > self.bkp + atr * sk_close[ski] * 0.1:
                bkpderh = 1
            if bkprh > 0:
                if self.skat_bkp == 0:
                    self.bkp_rhcn += 1
                    self.bkp_rhi = ski
                self.skat_bkp += 1
            if bkpderh > 0:
                self.skat_bkp = 0
            # ----------------------------
            if sk_close[ski] < self.bkp - atr * sk_close[ski] * 0.2:
                bkpov = 1
            if sk_close[ski] > self.bkp + atr * sk_close[ski] * 0.1:
                bkpdeov = 1
            if bkpov > 0:
                if self.skov_bkp == 0:
                    self.bkp_ovcn += 1
                    self.bkp_ovi = ski
                self.skov_bkp += 1
            if bkpdeov > 0:
                self.skov_bkp = 0
            # -------------------------------------
            if not self.bk_ensti:
                if sk_ckl[ski][0] < 0:
                    self.bk_enstp = max(sk_high[ski - 1], sk_high[ski]) + atr * sk_close[ski] * 0.05
                    self.bk_ensti = ski
            # --------------------------------------
            if ski >= self.bki + 5 and  sk_low[ski] <= self.extp + atr * sk_close[ski] * 0.0:
                extprh = 1
            if sk_low[ski] > self.extp + atr * sk_close[ski] * 0.3:
                extpderh = 1
            if extprh > 0:
                if self.skat_extp == 0:
                    self.extp_rhcn += 1
                    self.extp_rhi = ski
                self.skat_extp += 1
            if extpderh > 0:
                self.skat_extp = 0
            # ----------------------------
            if sk_close[ski] < self.extp - atr * sk_close[ski] * 0.2:
                extpov = 1
            if sk_close[ski] > self.extp + atr * sk_close[ski] * 0.1:
                extpdeov = 1
            if extpov > 0:
                if self.skov_extp == 0:
                    self.extp_ovcn += 1
                    self.extp_ovi = ski
                self.skov_extp += 1
            if extpdeov > 0:
                self.skov_extp = 0

        # -------------------------------------
        if self.bkp_ovi:
            if self.tbl == 'bbl' and sk_ckl[ski][0] < 0:
                self.bkp_ovstp = max(sk_high[ski - 1], sk_high[ski]) + atr * sk_close[ski] * 0.05
                self.bkp_ovsti = ski
                self.bkp_ovi = None
            elif self.tbl == 'ttl' and sk_ckl[ski][0] > 0:
                self.bkp_ovstp = min(sk_low[ski - 1], sk_low[ski]) - atr * sk_close[ski] * 0.05
                self.bkp_ovsti = ski
                self.bkp_ovi = None

        if self.extp_ovi:
            if self.tbl == 'bbl'  and sk_ckl[ski][0] < 0:
                self.reb_enstp = max(sk_high[ski-1], sk_high[ski]) + atr * sk_close[ski] *0.05
                self.reb_ensti = ski
                self.extp_ovi = None
            elif self.tbl == 'ttl'  and sk_ckl[ski][0] > 0:
                self.reb_enstp = min(sk_low[ski-1], sk_low[ski]) - atr * sk_close[ski] *0.05
                self.reb_ensti = ski
                self.extp_ovi = None

        if self.extp_rhi:
            if self.tbl == 'bbl' and sk_ckl[ski][0] < 0:
                self.extp_rhstp = max(sk_high[ski - 1], sk_high[ski]) + atr * sk_close[ski] * 0.05
                self.extp_rhsti = ski
                self.extp_rhi = None

            elif self.tbl == 'ttl' and sk_ckl[ski][0] > 0:
                self.extp_rhstp = min(sk_low[ski - 1], sk_low[ski]) - atr * sk_close[ski] * 0.05
                self.extp_rhsti = ski
                self.extp_rhi = None

        if self.rsta % 3 == 0:
            self.crsp = self.extp          # 未突破 or 突破后回归到趋势线内的， 阻力线为趋势线
        elif self.rsta % 3 == 1 or self.rsta % 3 == 2:
            if ski - self.bki <= 0:        # 突破后短期内阻力线为趋势线
                self.crsp = self.extp
            elif 0 < ski - self.bki <= 300: # 突破后中期内阻力线为突破线
                self.crsp = self.bkp
            else:                          # 突破很久后阻力线失效
                self.crsp = None

        if self.crsp:
            if self.tbl == 'bbl':
                self.rspdet = ( self.crsp - sk_close[ski] ) / atr /sk_close[ski]
            elif self.tbl == 'ttl':
                self.rspdet = -( self.crsp - sk_close[ski] ) / atr /sk_close[ski]
            else:
                self.rspdet = None
        else:
            self.rspdet = None

        self.uptsadls(sk_open, sk_high, sk_low, sk_close, sk_atr, sk_ckl, ski)
        #----------------------更新fibo
        if not self.fib0 and self.bk_enstp and self.bk_ensti and self.initi< self.bk_ensti:
            if self.tbl == 'bbl' and self.upsmp and sk_low[ski] < self.bk_enstp and (ski - self.bk_ensti) % 10 >= 2:
                self.getfib(sk_open, sk_high, sk_low, sk_close, atr, ski)
            elif self.tbl == 'ttl' and self.dwsmp and sk_high[ski] > self.bk_enstp and (ski - self.bk_ensti) % 10 >= 2:
                self.getfib(sk_open, sk_high, sk_low, sk_close, atr, ski)

        elif self.fib0:
            if (self.tbl == 'bbl' and sk_high[ski]>= self.fib0) or (self.tbl == 'ttl' and sk_low[ski] <= self.fib0):
                self.fib0 = None

        #-------------------------------------------
    # 计算斜率标准得分
    def fak(self):
        fs = 10
        dx = [0.08, 0.04, 0.01]
        ux = [0.12, 0.2, 0.3]
        dy = [1, 0.3, 0]
        if self.tbl == 'bbl':
            xrk = self.rk
        elif self.tbl == 'ttl':
            xrk = -self.rk
        else:
            xrk = -1
        if xrk < 0:
            self.srk = - fs
            return

        if dx[0] <= xrk <= ux[0]:
            self.srk = fs * dy[0]

        elif dx[1] <= xrk < dx[0]:
            self.srk = fs * dy[1] + (xrk - dx[1]) * (dy[1] - dy[0]) / (dx[1] - dx[0])
        elif dx[2] <= xrk < dx[1]:
            self.srk = fs * dy[2] + (xrk - dx[2]) * (dy[2] - dy[1]) / (dx[2] - dx[1])
        elif dx[2] > xrk:
            self.srk = fs * dy[2]

        elif ux[1] >= xrk > ux[0]:
            self.srk = fs * dy[1] + (xrk - ux[1]) * (dy[1] - dy[0]) / (ux[1] - ux[0])
        elif ux[2] >= xrk > ux[1]:
            self.srk = fs * dy[2] + (xrk - ux[2]) * (dy[2] - dy[1]) / (ux[2] - ux[1])
        elif ux[2] < xrk:
            self.srk = fs * dy[2]

    # -------------------------------------
    # 计算齐K标准得分
    def frsk(self, sk_open, sk_high, sk_low, sk_close, atr, bi, ei):
        psis = [] #被惩罚sk列表
        fs = 0
        sdps = -2  # sk实体越线惩罚因子
        tpps = -1.5  # sk尖端越线惩罚因子
        tpwd = 1   # sk尖端触线奖励因子
        # self.ocover = 0        self.hlover = 0    self.pdreach = 0
        if self.tbl == 'bbl':
            for ski in range(bi, ei):
                lip = self.extendp(ski)
                if min(sk_open[ski], sk_close[ski]) < lip:
                    fs += sdps
                    self.ocover += 1
                    psis.append(ski)
                elif sk_low[ski] < lip - sk_close[ski]*atr*0.062:
                    fs += tpps
                    self.hlover += 1
                    psis.append(ski)
                elif lip - sk_close[ski]*atr*0.03 <= sk_low[ski] <= lip + sk_close[ski]*atr*0.062:
                    self.pdreach += 1
                    fs += tpwd

            self.srsk = fs
            return psis
        elif self.tbl == 'ttl':
            for ski in range(bi, ei):
                lip = self.extendp(ski)
                if max(sk_open[ski], sk_close[ski]) > lip:
                    self.ocover += 1
                    fs += sdps
                    psis.append(ski)
                elif sk_high[ski] > lip + sk_close[ski]*atr*0.062:
                    self.hlover += 1
                    fs += tpps
                    psis.append(ski)
                elif lip - sk_close[ski]*atr*0.062 <= sk_high[ski] <= lip + sk_close[ski]*atr*0.03:
                    self.pdreach += 1
                    fs += tpwd

            self.srsk = fs
            return psis
        else:
            self.srsk = fs
            return psis

    # -----------------------------fibo
    def getfib(self, sk_open, sk_high, sk_low, sk_close, atr, i):
        fs = 0
        sdps = -1  # sk实体越线惩罚因子
        tpps = -1  # sk尖端越线惩罚因子
        supwd = 1   # sk尖端触线奖励因子
        reswd = 1
        minfib = 2.5 # fibo最小头肩距
        maxfib = 5
        scr = 0.1
        sbr = 0.1
        ssr = 0.05
        rhbi = None
        hsifs = {}
        #------------------------
        if self.tbl == 'bbl':
            fibmp = None
            fibmi = None
            for ski in range(self.fbi, i+1, 1):
                if sk_low[ski] <= self.extendp(ski) + atr * sk_close[ski] * 0.3:
                    rhbi = ski
                    fibmi = ski
                    fibmp = sk_high[ski]
                    break
            if not rhbi:
                return
            for ski in range(rhbi, i+1, 1):
                if sk_high[ski] > fibmp:
                    fibmi = ski
                    fibmp = sk_high[ski]
            for ski in range(fibmi, i+1, 1):  # rhbi
                fibp = sk_low[ski]
                hs = fibmp - fibp
                if fibp > self.bkp or hs < atr * sk_close[ski] * minfib or hs > atr * sk_close[ski] * maxfib:
                    hsifs[ski] = -100
                    continue
                fsup = 0
                fres = 0
                for sfi in range(rhbi, i+1, 1):
                    det = atr * sk_close[sfi]
                    sup = 0
                    if sk_low[sfi] <= fibp and min(sk_open[sfi], sk_close[sfi])>= fibp - ssr  * det:
                        for si in range(sfi, sfi-10, -1):
                            if sk_low[si] > fibp:
                                sup = 1
                                break
                            if min(sk_open[si], sk_close[si])< fibp - ssr * det or sk_low[si] < sk_low[sfi]- sbr * det:
                                sup = 0
                                break
                        if sup > 0:
                            for si in range(sfi+1, i+1, 1):
                                if sk_low[si] > fibp:
                                    sup += 1
                                    break
                                if min(sk_open[si], sk_close[si]) < fibp  - ssr * det or sk_low[si] < sk_low[sfi] - sbr * det:
                                    sup = 0
                                    break
                        fsup += sup * supwd
                    #-------------------
                    res = 0
                    if sk_high[sfi] >= fibp and max(sk_open[sfi], sk_close[sfi])<= fibp + ssr * det :
                        for si in range(sfi, sfi-10, -1):
                            if sk_high[si] < fibp:
                                res = 1
                                break
                            if max(sk_open[si], sk_close[si]) > fibp + ssr * det or sk_high[si] > sk_high[sfi] + sbr * det:
                                res = 0
                                break
                        if res >0 :
                            for si in range(sfi+1, i+1, 1):
                                if sk_high[si] < fibp:
                                    res += 1
                                    break
                                if max(sk_open[si], sk_close[si]) > fibp + ssr * det or sk_high[si] > sk_high[sfi] + sbr * det:
                                    res = 0
                                    break
                        fres += res * reswd

                hsifs[ski] = fsup * 2 + fres * 0.1

            if hsifs:
                maxfi = max(hsifs, key=hsifs.get)
                fibp = sk_low[maxfi]
                if hsifs[maxfi] >1:
                    self.sfib = hsifs[maxfi]
                    self.fib0 = fibmp
                    self.fib1 = fibp
                    self.fibr = fibmp + 0.618 * (fibp - fibmp)
                    self.fib16 = fibmp + 1.618 * (fibp - fibmp)
                    self.fib2 = fibmp + 2 * (fibp - fibmp)
                    self.fib26 = fibmp + 2.618 * (fibp - fibmp)
                    self.fib3 = fibmp + 3 * (fibp - fibmp)
                    self.fib42 = fibmp + 4.236 * (fibp - fibmp)

        # ------------------------
        if self.tbl == 'ttl':
            fibmp = None
            fibmi = None
            for ski in range(self.fbi, i + 1, 1):
                if sk_high[ski] >= self.extendp(ski) - atr * sk_close[ski] * 0.3:
                    rhbi = ski
                    fibmi = ski
                    fibmp = sk_low[ski]
                    break
            if not rhbi:
                return
            for ski in range(rhbi, i + 1, 1):
                if sk_low[ski] < fibmp:
                    fibmi = ski
                    fibmp = sk_low[ski]
            for ski in range(fibmi, i + 1, 1):
                fibp = sk_high[ski]
                hs = fibmp - fibp
                if fibp < self.bkp or -hs < atr * sk_close[ski] * minfib or -hs > atr * sk_close[ski] * maxfib:
                    hsifs[ski] = -100
                    continue
                fsup = 0
                fres = 0
                for sfi in range(rhbi, i+1, 1):
                    det = atr * sk_close[sfi]
                    sup = 0
                    if sk_low[sfi] <= fibp and min(sk_open[sfi], sk_close[sfi])>= fibp - ssr  * det:
                        for si in range(sfi, sfi-10, -1):
                            if sk_low[si] > fibp:
                                sup = 1
                                break
                            if min(sk_open[si], sk_close[si])< fibp - ssr * det or sk_low[si] < sk_low[sfi]- sbr * det:
                                sup = 0
                                break
                        if sup > 0:
                            for si in range(sfi+1, i+1, 1):
                                if sk_low[si] > fibp:
                                    sup += 1
                                    break
                                if min(sk_open[si], sk_close[si]) < fibp  - ssr * det or sk_low[si] < sk_low[sfi] - sbr * det:
                                    sup = 0
                                    break
                        fsup += sup * supwd
                    #-------------------
                    res = 0
                    if sk_high[sfi] >= fibp and max(sk_open[sfi], sk_close[sfi])<= fibp + ssr * det :
                        for si in range(sfi, sfi-10, -1):
                            if sk_high[si] < fibp:
                                res = 1
                                break
                            if max(sk_open[si], sk_close[si]) > fibp + ssr * det or sk_high[si] > sk_high[sfi] + sbr * det:
                                res = 0
                                break
                        if res >0 :
                            for si in range(sfi+1, i+1, 1):
                                if sk_high[si] < fibp:
                                    res += 1
                                    break
                                if max(sk_open[si], sk_close[si]) > fibp + ssr * det or sk_high[si] > sk_high[sfi] + sbr * det:
                                    res = 0
                                    break
                        fres += res * reswd

                hsifs[ski] = fsup * 0.1 + fres * 2

            if hsifs:
                maxfi = max(hsifs, key=hsifs.get)
                fibp = sk_high[maxfi]
                if hsifs[maxfi] > 1:
                    sortfs = sorted(hsifs.items(), key=lambda hsifs: hsifs[1], reverse=True)
                    # print sortfs

                    self.sfib = hsifs[maxfi]
                    # print 'ski:', ski, 'maxfi:', maxfi, hsifs[maxfi]
                    self.fib0 = fibmp
                    self.fib1 = fibp
                    self.fibr = fibmp + 0.618 * (fibp - fibmp)
                    self.fib16 = fibmp + 1.618 * (fibp - fibmp)
                    self.fib2 = fibmp + 2 * (fibp - fibmp)
                    self.fib26 = fibmp + 2.618 * (fibp - fibmp)
                    self.fib3 = fibmp + 3 * (fibp - fibmp)
                    self.fib42 = fibmp + 4.236 * (fibp - fibmp)


    # -----------------------------获取fibov
    def fibp(self, k):
        if self.fib0:
            return self.fib0 + k * (self.fib1 - self.fib0)
        else:
            return None

    # -----------------------------rhcn
    def calrhcn(self, updw, bi, ei, trp, sk_open, sk_high, sk_low, sk_close, atr):
        #--sk整体上穿trp上方det一段时间（holdn）才表示 处于trp 上方
        holdn = 2
        det = 0.5
        rhcn = 0
        if updw == 'dw':
            rhcn = 0
            hdn = holdn
            for ski in range(bi, ei+1, 1):
                if sk_low[ski] <= trp - atr * sk_close[ski]*0:
                    if hdn >= holdn:
                        rhcn += 1
                    hdn = 0
                if sk_low[ski] >= trp + atr * sk_close[ski] * det:
                    hdn += 1

        elif updw == 'up':
            rhcn = 0
            hdn = holdn
            for ski in range(bi, ei + 1, 1):
                if sk_high[ski] >= trp + atr * sk_close[ski] * 0:
                    if hdn >= holdn:
                        rhcn += 1
                    hdn = 0
                if sk_high[ski] <= trp - atr * sk_close[ski] * det:
                    hdn += 1
        return rhcn

    # -----------------------------获取最近的未突破的ski
    def lstubkski(self, sk_open, sk_high, sk_low, sk_close, atr, i):
        for ski in range(i, self.trpd.ski, -1):
            if self.tbl == 'bbl':
                if sk_close[ski] >= self.extendp(ski) + atr * sk_close[ski] * 0.05:
                    return ski
            if self.tbl == 'ttl':
                if sk_close[ski] <= self.extendp(ski) - atr * sk_close[ski] * 0.05:
                    return ski
        return None

    # -----------------------------初始化偏离tdl最远的ski
    def initmaxpt(self, sk_open, sk_high, sk_low, sk_close, atr, i):
        mpti = i
        mptv = 0
        for ski in range(self.fbi, i, 1):
            if self.tbl == 'bbl':
                diskl = sk_high[ski] - self.extendp(ski)
                if diskl >= mptv :
                    mpti = ski
                    mptv = diskl
            elif self.tbl == 'ttl':
                diskl = sk_low[ski] - self.extendp(ski)
                if diskl <= mptv:
                    mpti = ski
                    mptv = diskl
        self.mpti = mpti
        self.mptv = mptv
        #---------------------反向偏离
        bkmpti = i
        bkmptv = 0
        for ski in range(self.fbi, i, 1):
            if self.tbl == 'bbl':
                diskl = sk_low[ski] - self.extendp(ski)
                if diskl <= mptv:
                    bkmpti = ski
                    bkmptv = diskl
            elif self.tbl == 'ttl':
                diskl = sk_high[ski] - self.extendp(ski)
                if diskl >= mptv:
                    bkmpti = ski
                    bkmptv = diskl
        self.bkmpti = bkmpti
        self.bkmptv = bkmptv

    # -------------------------------------
    def uptsadls(self, sk_open, sk_high, sk_low, sk_close, sk_atr, sk_ckl, ski):
        # if 'bbl_592_up' in self.socna:
        #     print self.socna, 'uptsadls'
        atr = sk_close[ski] * sk_atr[ski]
        det = atr * 0.05
        mdet = 5 * atr
        ldet = 0.2 * atr
        mcn = 5
        ldp = 2
        rtp = 0.4
        #-------------------------------
        if not self.tepups:
            if sk_low[ski - 1] -det <= self.extendp(ski) <= sk_high[ski]:
                self.tepups = Sadl(1, bi=ski)
                if sk_low[ski] >= self.extendp(ski) + ldet:
                    self.tepups.cn += 1
                self.tepups.mdi = ski
                self.tepups.mdp = sk_high[ski] - self.extendp(ski)
                self.tepups.sdp = sk_high[ski] - self.extendp(ski)
                self.tepups.mp = sk_high[ski]
                self.tepups.mi = ski
                self.tepups.upti = ski
        else:
            if sk_low[ski] >= self.extendp(ski) + ldet:
                self.tepups.cn += 1
            if not self.tepups.mp or self.tepups.mp <= sk_high[ski]:
                self.tepups.mp = sk_high[ski]
                self.tepups.mi = ski
            dep = max(sk_high[ski] - self.extendp(ski), 0.0)
            rep = max(sk_low[ski] - self.extendp(ski), 0.0)
            if dep >= self.tepups.mdp:
                self.tepups.mdi = ski
                self.tepups.mdp = dep
            self.tepups.sdp += dep
            self.tepups.upti = ski
            if self.crtups and self.crtups.ei :
                if rep < self.crtups.mdp * self.crtups.mret:
                    if self.crtups.mdp < self.tepups.mdp:
                        self.crtups.mdp = self.tepups.mdp
                        self.crtups.mdi = self.tepups.mdi
                    self.crtups.ei = ski
                    self.crtups.sdp += self.tepups.sdp
                    self.crtups.mret = rep / self.crtups.mdp
                    self.crtups.cn += self.tepups.cn
                    self.crtups.upti = ski
                    if not self.crtups.mp or self.crtups.mp <= self.tepups.mp:
                        self.crtups.mp = self.tepups.mp
                        self.crtups.mi = self.tepups.mi
                    self.upmdps[-1]= self.crtups.mdp
                    self.upmdis[-1] = self.crtups.mdi
                    if not self.mupsadl or self.mupsadl.mdp <= self.crtups.mdp:
                        self.mupsadl = self.crtups
                    if not self.upsmdp or self.upsmdp < self.crtups.mdp and abs(self.crtups.mdp) <= mdet:
                        self.upsmdp = self.crtups.mdp
                        self.upsmdi = self.crtups.mdi
                    if self.extendp(ski) < sk_high[ski]:
                        self.tepups = Sadl(1, bi=ski)
                        self.tepups.mdp = max(sk_high[ski] - self.extendp(ski), 0.0)
                        self.tepups.mdi = ski
                    else:
                        self.tepups = None
                if not self.upsmp or self.upsmp <= self.crtups.mp:
                    self.upsmp = self.crtups.mp
                    self.upsmi = self.crtups.mi
            if self.tepups and self.tepups.cn >= mcn and self.tepups.mdp >= atr * ldp :
                self.crtups = self.tepups
                self.sadls.append(self.crtups)
                self.tepups = None
            if self.tepups and sk_low[ski] <= self.extendp(ski):
                if self.tepups.cn < mcn:
                    self.tepups = None
        if self.crtups and self.crtups.upti < ski:
            if not self.crtups.ei:
                if not self.crtups.mp or self.crtups.mp <= sk_high[ski]:
                    self.crtups.mp = sk_high[ski]
                    self.crtups.mi = ski
                if sk_low[ski] >= self.extendp(ski) + ldet :
                    self.crtups.cn += 1
                dep = max(sk_high[ski] - self.extendp(ski), 0.0)
                rep = max(sk_low[ski] - self.extendp(ski), 0.0)
                if dep >= self.crtups.mdp:
                    self.crtups.mdi = ski
                    self.crtups.mdp = dep
                    self.crtups.mret = 1
                self.crtups.sdp += dep
                mret = rep / self.crtups.mdp
                if self.crtups.mret > mret:
                    self.crtups.mret = mret
                if self.crtups.mret<= rtp :
                    self.crtups.ei = ski
                    self.upmdps.append(self.crtups.mdp)
                    self.upmdis.append(self.crtups.mdi)
                    if not self.mupsadl or self.mupsadl.mdp <= self.crtups.mdp:
                        self.mupsadl = self.crtups
                    if not self.upsmp or self.upsmp <= self.crtups.mp:
                        self.upsmp = self.crtups.mp
                        self.upsmi = self.crtups.mi
                    if not self.upsmdp or self.upsmdp < self.crtups.mdp and abs(self.crtups.mdp) <= mdet:
                        self.upsmdp = self.crtups.mdp
                        self.upsmdi = self.crtups.mdi
                    if self.extendp(ski) < sk_high[ski]:
                        self.tepups = Sadl(1, bi=ski)
                        self.tepups.mdp = max(sk_high[ski] - self.extendp(ski), 0.0)
                        self.tepups.mdi = ski
                    else:
                        self.tepups = None
                self.crtups.upti = ski

        # -------------------------------
        if not self.tepdws:
            if sk_high[ski - 1] + det >= self.extendp(ski) >= sk_low[ski]:
                self.tepdws = Sadl(-1, bi=ski)
                if sk_high[ski] <= self.extendp(ski) - ldet:
                    self.tepdws.cn += 1
                self.tepdws.mdi = ski
                self.tepdws.mdp = sk_low[ski] - self.extendp(ski)
                self.tepdws.sdp = sk_low[ski] - self.extendp(ski)
                self.tepdws.mp = sk_low[ski]
                self.tepdws.mi = ski
                self.tepdws.upti = ski
        else:
            if sk_high[ski] <= self.extendp(ski) - ldet:
                self.tepdws.cn += 1
            if not self.tepdws.mp or self.tepdws.mp >=sk_low[ski]:
                self.tepdws.mp = sk_low[ski]
                self.tepdws.mi = ski
            dep = min(sk_low[ski] - self.extendp(ski), 0.0)
            rep = min(sk_high[ski] - self.extendp(ski), 0.0)
            if dep <= self.tepdws.mdp:
                self.tepdws.mdi = ski
                self.tepdws.mdp = dep
            self.tepdws.sdp += dep
            self.tepdws.upti = ski
            if self.crtdws and self.crtdws.ei:
                if rep > self.crtdws.mdp * self.crtdws.mret:
                    if self.crtdws.mdp > self.tepdws.mdp:
                        self.crtdws.mdp = self.tepdws.mdp
                        self.crtdws.mdi = self.tepdws.mdi
                    self.crtdws.ei = ski
                    self.crtdws.sdp += self.tepdws.sdp
                    self.crtdws.mret = rep / self.crtdws.mdp
                    self.crtdws.cn += self.tepdws.cn
                    self.crtdws.upti = ski
                    if not self.crtdws.mp or self.crtdws.mp >= self.tepdws.mp:
                        self.crtdws.mp = self.tepdws.mp
                        self.crtdws.mi = self.tepdws.mi
                    self.dwmdps[-1] = self.crtdws.mdp
                    self.dwmdis[-1] = self.crtdws.mdi
                    if not self.mdwsadl or self.mdwsadl.mdp >= self.crtdws.mdp:
                        self.mdwsadl = self.crtdws
                    if not self.dwsmdp or self.dwsmdp > self.crtdws.mdp and abs(self.crtdws.mdp) <= mdet:
                        self.dwsmdp = self.crtdws.mdp
                        self.dwsmdi = self.crtdws.mdi
                    if self.extendp(ski) > sk_low[ski]:
                        self.tepdws = Sadl(-1, bi=ski)
                        self.tepdws.mdp = min(sk_low[ski] - self.extendp(ski), 0.0)
                        self.tepdws.mdi = ski
                    else:
                        self.tepdws = None
                if not self.dwsmp or self.dwsmp >= self.crtdws.mp:
                    self.dwsmp = self.crtdws.mp
                    self.dwsmi = self.crtdws.mi
            if self.tepdws and self.tepdws.cn >= mcn and self.tepdws.mdp <= -atr * ldp:
                self.crtdws = self.tepdws

                self.sadls.append(self.crtdws)
                self.tepdws = None
            if self.tepdws and sk_high[ski] >= self.extendp(ski):
                if self.tepdws.cn < mcn:
                    self.tepdws = None
        if self.crtdws and self.crtdws.upti < ski:
            if not self.crtdws.ei:
                if not self.crtdws.mp or self.crtdws.mp >= sk_low[ski]:
                    self.crtdws.mp = sk_low[ski]
                    self.crtdws.mi = ski
                if sk_high[ski] <= self.extendp(ski) - ldet:
                    self.crtdws.cn += 1
                dep = min(sk_low[ski] - self.extendp(ski), 0.0)
                rep = min(sk_high[ski] - self.extendp(ski), 0.0)
                if dep <= self.crtdws.mdp:
                    self.crtdws.mdi = ski
                    self.crtdws.mdp = dep
                    self.crtdws.mret = 1
                self.crtdws.sdp += dep
                mret = rep / self.crtdws.mdp
                if self.crtdws.mret > mret:
                    self.crtdws.mret = mret
                if self.crtdws.mret <= rtp:
                    self.crtdws.ei = ski
                    self.dwmdps.append(self.crtdws.mdp)
                    self.dwmdis.append(self.crtdws.mdi)
                    if not self.mdwsadl or self.mdwsadl.mdp >= self.crtdws.mdp:
                        self.mdwsadl = self.crtdws
                    if not self.dwsmp or self.dwsmp >= self.crtdws.mp:
                        self.dwsmp = self.crtdws.mp
                        self.dwsmi = self.crtdws.mi
                    if not self.dwsmdp or self.dwsmdp > self.crtdws.mdp and abs(self.crtdws.mdp) <= mdet:
                        self.dwsmdp = self.crtdws.mdp
                        self.dwsmdi = self.crtdws.mdi
                    if self.extendp(ski) > sk_low[ski]:
                        self.tepdws = Sadl(-1, bi=ski)
                        self.tepdws.mdp = min(sk_low[ski] - self.extendp(ski), 0.0)
                        self.tepdws.mdi = ski
                    else:
                        self.tepdws = None
                self.crtdws.upti = ski


    def initsklsta(self, sk_open, sk_high, sk_low, sk_close, sk_atr, sk_ckl, i): # 初始化趋势线与当前sk的位置状态
        atr = sk_atr[i]
        self.initmaxpt(sk_open, sk_high, sk_low, sk_close, atr, i)
        self.initi = i
        ubki = self.lstubkski(sk_open, sk_high, sk_low, sk_close, atr, i)
        if  True or ubki and ubki < i:  #True or
            for ski in range(self.trpb.ski, i, 1):  #fbi
                self.uptsadls(sk_open, sk_high, sk_low, sk_close, sk_atr, sk_ckl, ski)
        if ubki and ubki < i:
            for ski in range(ubki, i):
                self.uptskista(sk_open, sk_high, sk_low, sk_close, sk_atr, sk_ckl, ski)

    # -------------------------------------
    def trgsgn(self, sk_open, sk_high, sk_low, sk_close, sk_atr, sk_ckl, ski):
        if self.trgi >= ski:
            return
        self.trgi = ski
        self.tdk0 = None
        self.tdk1 = None
        self.tdk3 = None
        self.tdk5 = None
        self.tdk7 = None
        self.tdk2 = None
        self.tdk4 = None
        self.tdk6 = None
        self.tdk8 = None
        # ---------------
        self.cst0 = None
        self.cst1 = None
        self.cst3 = None
        self.cst5 = None
        self.cst7 = None
        self.cst2 = None
        self.cst4 = None
        self.cst6 = None
        self.cst8 = None
        # --------------
        self.csi0 = None
        self.csi1 = None
        self.csi3 = None
        self.csi5 = None
        self.csi7 = None
        self.csi2 = None
        self.csi4 = None
        self.csi6 = None
        self.csi8 = None
        # --------------
        self.ctp0 = None
        self.ctp1 = None
        self.ctp3 = None
        self.ctp5 = None
        self.ctp7 = None
        self.ctp2 = None
        self.ctp4 = None
        self.ctp6 = None
        self.ctp8 = None

        atr = sk_atr[ski]
        det = sk_close[ski] * atr
        # -------------------------------------开仓
        if self.rsta % 3 == 0:
            self.vak0 = 0
            self.vak2 = 0
            self.vak4 = 0

            self.tdk1 = self.extp + self.ak + self.dir * det * 0.2

            if self.reb_ensti:
                self.tdk3 = self.reb_enstp
                if self.vak3 == 0:
                    self.vak3 = ski

            # self.tdk5 = self.bkmirp + self.ak if self.bkmirp else None

        elif self.rsta % 3 == 1:
            self.vak3 = 0

            if ski == self.bki and  abs( sk_close[ski] - self.bkp) <  det * 3:
                self.tdk0 = self.eop - self.dir * det * 0.2
                if self.vak0==0:
                    self.vak0 = ski

            self.tdk2 = self.bkp - self.dir * det * 0.2
            if self.vak2 == 0:
                self.vak2 = ski

            if self.bk_ensti:
                self.tdk4 = self.bk_enstp
                if self.vak4 ==0:
                    self.vak4 = ski

            if ski - self.bki>= 5:
                self.tdk6 = self.extp + self.ak - self.dir * det * 0.15
            # self.tdk8 = self.mirp + self.ak if self.mirp else None

        if 0< self.vak0 < ski :
            self.vak0 = -1

        if 0< self.vak2 < ski and ( (self.dir>0 and sk_high[ski]>= self.bkp) or (self.dir<0 and sk_low[ski]<= self.bkp) ) :
            self.vak2 = -1

        if 0< self.vak4 < ski and ( (self.dir>0 and sk_low[ski]<= self.bk_enstp) or (self.dir<0 and sk_high[ski]>= self.bk_enstp) ) :
            self.vak4 = -1

        if 0< self.vak3 < ski and ( (self.dir>0 and sk_high[ski]>= self.reb_enstp) or (self.dir<0 and sk_low[ski]<= self.reb_enstp) ) :
            self.vak3 = -1


        # -------------------------------------止损  为None则在回测端使用固定比例止损 k3/k5/k8 采用atr倍数止损
        self.cst1 = self.eop - self.dir * det * 0.2 if self.eop else None
        self.csi1 = self.bki

        self.cst0 = self.eip + self.dir * det * 0.2 if self.eip else None
        self.csi0 = self.bki

        self.cst2 = self.bkp_ovstp
        self.csi2 = self.bkp_ovsti

        self.cst4 = self.bkp_ovstp
        self.csi4 = self.bkp_ovsti

        self.cst6 = self.extp_rhstp
        self.csi6 = self.extp_rhsti
        # -------------------------------------平仓目标  为None则在回测端使用固定比例atr倍数出场
        if self.rsta % 3 == 0:
            self.ctp0 = self.extp + self.ak + self.dir * det * 0.15
            self.ctp2 = self.extp + self.ak + self.dir * det * 0.15
            self.ctp4 = self.extp + self.ak + self.dir * det * 0.15
            self.ctp6 = self.extp + self.ak + self.dir * det * 0.15

        if self.rsta % 3 != 0:
            # self.ctp1 = self.mirp + self.ak if self.mirp else None
            self.ctp1 = self.bkp - self.dir * det * 0.15
            if self.bkp_ovsti and self.bkp_ovsti > self.bki:
                self.ctp2 = self.bkp
                self.ctp4 = self.bkp

        #-------------------------------------------------------------------------------------------------
        self.trpkops = {}
        self.trpcsts = {}
        self.trpctps = {}
        #-------------------------------------------------------------------------------------------开仓信号

        if 0< self.vak0 and self.tdk0:
            sgnna = 'tdk0' + '-' + self.socna
            sgntyp = 'tdk0'
            bsdir = -self.dir
            sdop = self.tdk0
            ordtyp = 'Stp'
            sdsp = self.cst0
            sdtp = None
            psn = 3
            msn = 0
            mark = self.initi
            prio = 0
            self.trpkops[sgnna] = Sgnkop(sgnna, sgntyp, bsdir, sdop, ordtyp, sdsp, sdtp, psn, msn, mark, prio)
        #------------------
        if False and 0< self.vak2 and self.tdk2:
            sgnna = 'tdk2' + '-' + self.socna
            sgntyp = 'tdk2'
            bsdir = -self.dir
            sdop = self.tdk2
            ordtyp = 'Lmt'
            sdsp = None
            sdtp = None
            psn = 2
            msn = 1
            mark = self.initi
            prio = 0
            self.trpkops[sgnna] = Sgnkop(sgnna, sgntyp, bsdir, sdop, ordtyp, sdsp, sdtp, psn, msn, mark, prio)
        # ------------------
        if False and 0< self.vak4 and self.tdk4:
            sgnna = 'tdk4' + '-' + self.socna
            sgntyp = 'tdk4'
            bsdir = -self.dir
            sdop = self.tdk4
            ordtyp = 'Stp'
            sdsp = None
            sdtp = None
            psn = 2
            msn = 1
            mark = self.initi
            prio = 0
            self.trpkops[sgnna] = Sgnkop(sgnna, sgntyp, bsdir, sdop, ordtyp, sdsp, sdtp, psn, msn, mark, prio)
        # ------------------
        if False and self.tdk6:
            sgnna = 'tdk6' + '-' + self.socna
            sgntyp = 'tdk6'
            bsdir = -self.dir
            sdop = self.tdk6
            ordtyp = 'Lmt'
            sdsp = None
            sdtp = None
            psn = 2
            msn = 1
            mark = None
            prio = 0
            self.trpkops[sgnna] = Sgnkop(sgnna, sgntyp, bsdir, sdop, ordtyp, sdsp, sdtp, psn, msn, mark, prio)
        # ------------------
        if self.tdk1:
            sgnna = 'tdk1' + '-' + self.socna
            sgntyp = 'tdk1'
            bsdir = self.dir
            sdop = self.tdk1
            ordtyp = 'Lmt'
            sdsp = None
            sdtp = None
            psn = 2
            msn = 1
            mark = self.initi
            prio = 0
            self.trpkops[sgnna] = Sgnkop(sgnna, sgntyp, bsdir, sdop, ordtyp, sdsp, sdtp, psn, msn, mark, prio)
        #------------------
        if False and 0< self.vak3 and self.tdk3:
            sgnna = 'tdk3' + '-' + self.socna
            sgntyp = 'tdk3'
            bsdir = self.dir
            sdop = self.tdk3
            ordtyp = 'Stp'
            sdsp = None
            sdtp = None
            psn = 2
            msn = 1
            mark = self.initi
            prio = 0
            self.trpkops[sgnna] = Sgnkop(sgnna, sgntyp, bsdir, sdop, ordtyp, sdsp, sdtp, psn, msn, mark, prio)
        # ------------------
        if False and self.tdk5:
            sgnna = 'tdk5' + '-' + self.socna
            sgntyp = 'tdk5'
            bsdir = self.dir
            sdop = self.tdk5
            ordtyp = 'Lmt'
            sdsp = None
            sdtp = None
            psn = 2
            msn = 1
            mark = self.initi
            prio = 0
            self.trpkops[sgnna] = Sgnkop(sgnna, sgntyp, bsdir, sdop, ordtyp, sdsp, sdtp, psn, msn, mark, prio)
        # -------------------------------------------------------------------------------------------止损平仓信号
        # ------------------
        if self.cst1:
            sgnna = 'cst1' + '-' + self.socna
            sgntyp = 'cst1'
            bsdir = -self.dir
            sdop = self.cst1
            mark = self.csi1
            prio = 0
            self.trpcsts[sgnna] = Sgncst(sgnna, sgntyp, bsdir, sdop, mark, prio)

        # ------------------
        if self.cst0:
            sgnna = 'cst0' + '-' + self.socna
            sgntyp = 'cst0'
            bsdir = self.dir
            sdop = self.cst0
            mark = self.csi0
            prio = 0
            self.trpcsts[sgnna] = Sgncst(sgnna, sgntyp, bsdir, sdop, mark, prio)

        # ------------------
        if self.cst2:
            sgnna = 'cst2' + '-' + self.socna
            sgntyp = 'cst2'
            bsdir = self.dir
            sdop = self.cst2
            mark = self.csi2
            prio = 0
            self.trpcsts[sgnna] = Sgncst(sgnna, sgntyp, bsdir, sdop, mark, prio)

        # ------------------
        if self.cst4:
            sgnna = 'cst4' + '-' + self.socna
            sgntyp = 'cst4'
            bsdir = self.dir
            sdop = self.cst4
            mark = self.csi4
            prio = 0
            self.trpcsts[sgnna] = Sgncst(sgnna, sgntyp, bsdir, sdop, mark, prio)

        # ------------------
        if self.cst6:
            sgnna = 'cst6' + '-' + self.socna
            sgntyp = 'cst6'
            bsdir = self.dir
            sdop = self.cst6
            mark = self.csi6
            prio = 0
            self.trpcsts[sgnna] = Sgncst(sgnna, sgntyp, bsdir, sdop, mark, prio)

        # -------------------------------------------------------------------------------------------止赢平仓信号
        # ------------------
        if self.ctp1:
            sgnna = 'ctp1' + '-' + self.socna
            sgntyp = 'ctp1'
            bsdir = -self.dir
            sdop = self.ctp1
            mark = ski
            prio = 0
            self.trpctps[sgnna] = Sgnctp(sgnna, sgntyp, bsdir, sdop, mark, prio)

        # ------------------
        if self.ctp0:
            sgnna = 'ctp0' + '-' + self.socna
            sgntyp = 'ctp0'
            bsdir = self.dir
            sdop = self.ctp0
            mark = ski
            prio = 0
            self.trpctps[sgnna] = Sgnctp(sgnna, sgntyp, bsdir, sdop, mark, prio)

        # ------------------
        if self.ctp2:
            sgnna = 'ctp2' + '-' + self.socna
            sgntyp = 'ctp2'
            bsdir = self.dir
            sdop = self.ctp2
            mark = ski
            prio = 0
            self.trpctps[sgnna] = Sgnctp(sgnna, sgntyp, bsdir, sdop, mark, prio)

        # ------------------
        if self.ctp4:
            sgnna = 'ctp4' + '-' + self.socna
            sgntyp = 'ctp4'
            bsdir = self.dir
            sdop = self.ctp4
            mark = ski
            prio = 0
            self.trpctps[sgnna] = Sgnctp(sgnna, sgntyp, bsdir, sdop, mark, prio)

        # ------------------
        if self.ctp6:
            sgnna = 'ctp6' + '-' + self.socna
            sgntyp = 'ctp6'
            bsdir = self.dir
            sdop = self.ctp6
            mark = ski
            prio = 0
            self.trpctps[sgnna] = Sgnctp(sgnna, sgntyp, bsdir, sdop, mark, prio)

# --------------------------------------------------------------------------------------------
def gettrpline(fidna, trp1, trp2, tbl, sk_open, sk_high, sk_low, sk_close, sk_atr, sk_time, sk_ckl, i, upski = None):
    mbdi = 5
    wrsk = 1.5
    trpis =[trp1.ski, trp2.ski]
    tdls = {}
    tdlfs= {}
    trpb = trp1
    trpd = trp2
    atr  = sk_atr[i]
    newtbl = Trpline(trpb, trpd, atr, tbl)
    newtbl.fak()
    fbi = trp1.ski
    fei = i
    tdlna= tbl + '_'+ str(trp1.ski)+'_'+str(trp2.ski)
    newtbl.fbi = fbi
    psis = newtbl.frsk(sk_open, sk_high, sk_low, sk_close, atr, fbi, fei)
    newtbl.sfs = newtbl.srk + wrsk * newtbl.srsk
    tdls[tdlna]  = newtbl
    tdlfs[tdlna] = newtbl.sfs

    if psis:
        trpis = sorted(list(set(trpis) | set(psis)))
        trpbdis = list(combinations(trpis, 2))
        for trp in trpbdis:
            bi = trp[0]
            ei = trp[1]
            if ei - bi < mbdi:
                continue
            if tbl=='bbl':
                trpb = Extrp(bi, sk_low[bi], -1)
                trpd = Extrp(ei, sk_low[ei], -1)
            elif tbl=='ttl':
                trpb = Extrp(bi, sk_high[bi], 1)
                trpd = Extrp(ei, sk_high[ei], 1)
            else:
                continue

            tdlna =  tbl + '_'+ str(bi) + '_' + str(ei)
            if tdlna in tdls:
                continue
            newtbl = Trpline(trpb, trpd, atr, tbl)
            newtbl.fbi = fbi
            newtbl.et_ini = upski if upski else i
            newtbl.fak()
            newtbl.frsk(sk_open, sk_high, sk_low, sk_close, atr, fbi, fei)  #   fbi, fei
            newtbl.sfs = newtbl.srk + wrsk * newtbl.srsk
            tdls[tdlna] = newtbl
            tdlfs[tdlna] = newtbl.sfs
    if tdlfs:
        sortfs = sorted(tdlfs.items(), key=lambda tdlfs: tdlfs[1], reverse=True)
        # print sortfs[:5]
        maxna  = max(tdlfs, key=tdlfs.get)
        newtbl = tdls[maxna]
        if newtbl.sfs> 5:
            newtbl.socna = tbl + '_' + str(i)
            newtbl.fsocna = fidna + '_' + newtbl.socna
            newtbl.btm = sk_time[newtbl.trpb.ski]
            newtbl.dtm = sk_time[newtbl.trpd.ski]
            newtbl.frtm = sk_time[i]
            #self.ocover = 0        self.hlover = 0    self.pdreach = 0
            print str(sk_time[i])[:10], newtbl.socna, ' rk:', '%.2f' % newtbl.rk, 'srk:', '%.2f' % newtbl.srk, 'srsk:', '%.2f' % newtbl.srsk, 'sfs:', '%.2f' % newtbl.sfs, \
                'ocovr:', newtbl.ocover, 'hlovr:', newtbl.hlover, 'pdrch:', newtbl.pdreach    #'newtbl:' , maxna,
            return newtbl
    return None

# --------------------------------------------------------------------------------------------
def getasline(socna, mdi, mp, mdp, ak, sk_time, atr, i, upski = None):
    if not mdi:
        return None
    tbl = socna.split('_')[0]
    bi = mdi
    bp = mp + mdp * 0.9
    ei = bi + 1
    ep = bp + ak
    trpb = Extrp(bi, bp, 0)
    trpd = Extrp(ei, ep, 0)
    asline = Trpline(trpb, trpd, atr, tbl)
    asline.socna = socna
    asline.fsocna = socna
    asline.btm = sk_time[bi]
    asline.dtm = sk_time[ei]
    asline.frtm = sk_time[i]
    asline.fbi = bi
    asline.exti = bi
    asline.extp = bp
    asline.initi = i
    asline.et_ini = upski if upski else i
    asline.bki = bi
    asline.bkp = bp
    asline.bkcn = 0
    asline.rsta = 1
    return asline

# --------------------------------------------------------------------------------------------
def getmrline1(socna, mri, mrp, ak, sk_time, atr, i, upski = None):
    if not mri:
        return None
    tbl = socna.split('_')[0]
    bi = mri
    bp = mrp
    ei = bi + 1
    ep = bp + ak
    trpb = Extrp(bi, bp, 0)
    trpd = Extrp(ei, ep, 0)
    mrline = Trpline(trpb, trpd, atr, tbl)
    mrline.socna = socna
    mrline.fsocna = socna
    mrline.btm = sk_time[bi]
    mrline.dtm = sk_time[ei]
    mrline.frtm = sk_time[i]
    mrline.fbi = bi
    mrline.exti = bi
    mrline.extp = bp
    mrline.initi = i
    mrline.et_ini = upski if upski else i
    mrline.bkcn = 0
    mrline.rsta = 0
    return mrline
# --------------------------------------------------------------------------------------------
def getsdi(bi, bp, ski, skp, lkp, rkp, dir = 1):
    ei = ski+1
    ep = rkp
    ak = (ep - bp) / (ei - bi)
    esp = ep - ak
    if (dir > 0 and skp <= esp) or (dir < 0 and skp >= esp):
        return (ei, ep)
    else:
        return (ski, skp)

def getsdi3(bi, bp, ski, skp, lkp, rkp):
    ei = ski
    ep = skp
    ak = (ep - bp) / (ei - bi)
    elp = ep - ak
    erp = ep + ak
    if (lkp > elp and rkp <= erp) or (lkp < elp and rkp >= erp) or lkp == elp:
        return (ei, ep)
    #-----------------------------
    ei = ski+1
    ep = rkp
    ak = (ep - bp) / (ei - bi)
    elp = ep - ak - ak
    esp = ep - ak
    if (lkp > elp and skp <= esp) or (lkp < elp and skp >= esp) or lkp == elp:
        return (ei, ep)
    #------------------------------
    ei = ski-1
    ep = lkp
    ak =  (ep - bp)/(ei-bi)
    esp = ep + ak
    erp = ep + ak + ak
    if (skp > esp and rkp <= erp) or (skp < esp and rkp >= erp) or skp == esp:
        return (ei, ep)

    return None


def getmrline2(socna, bi, bp, mri, mrp, fbi, sk_time, atr, i, upski = None):
    tbl = socna.split('_')[0]
    bi = bi
    bp = bp
    ei = mri
    ep = mrp
    trpb = Extrp(bi, bp, 0)
    trpd = Extrp(ei, ep, 0)
    mrline = Trpline(trpb, trpd, atr, tbl)
    if not (0.02 <= mrline.rk * mrline.dir <= 0.4):
        return None
    mrline.socna = socna
    mrline.fsocna = socna
    mrline.btm = sk_time[bi]
    mrline.dtm = sk_time[ei]
    mrline.frtm = sk_time[i]
    mrline.fbi = fbi
    mrline.exti = ei
    mrline.extp = ep
    mrline.initi = i
    mrline.et_ini = upski if upski else i
    mrline.bkcn = 0
    mrline.rsta = 0
    return mrline

def getsaline2(socna, bi, bp, sad2, rkp, fbi, sk_time, atr, i, upski = None):
    tbl = socna.split('_')[0]
    tbl = 'bbl' if tbl=='sa' else 'ttl'
    bi = bi
    bp = bp
    ei = sad2.mi
    ep = sad2.mp
    trpb = Extrp(bi, bp, 0)
    trpd = Extrp(ei, ep, 0)
    saline = Trpline(trpb, trpd, atr, tbl)
    if saline.rk * saline.dir <= 0.02:
        ei = sad2.mi+1
        ep = rkp
        trpd = Extrp(ei, ep, 0)
        saline = Trpline(trpb, trpd, atr, tbl)
        if saline.rk * saline.dir <= 0.02:
            return None
    elif saline.rk * saline.dir > 0.9:
        return None

    saline.socna = socna
    saline.fsocna = socna
    saline.btm = sk_time[bi]
    saline.dtm = sk_time[ei]
    saline.frtm = sk_time[i]
    saline.fbi = fbi
    saline.exti = ei
    saline.extp = ep
    saline.initi = i
    saline.et_ini = upski if upski else i
    saline.bkcn = 0
    saline.rsta = 0
    return saline

class Skatline(object):
    def __init__(self,sk_open, sk_high, sk_low, sk_close, sk_atr, sk_ckl, sk_dkcn, setting =None):
        if setting is None:
            self.det = 0.2
            self.rdet = 0.05
            self.mdet = 0.1
        else:
            self.det = setting['det']
            self.rdet = setting['rdet']
            self.mdet = setting['mdet']

        self.sk_open = sk_open
        self.sk_high = sk_high
        self.sk_low = sk_low
        self.sk_close = sk_close
        self.sk_atr = sk_atr
        self.sk_ckl = sk_ckl
        self.sk_dkcn = sk_dkcn
        self.sgni = None  # 最新产生信号的ski
        self.trpkops = {}

    def uptsta(self, tdl, i, upix = None, mosi = 0):
        det = self.det
        rdet = self.rdet
        mdet = self.mdet
        if not upix:
            if not tdl.se_upti:
                tdl.se_ini = tdl.initi
                ubi = tdl.se_ini
                tdl.se_sta = 0
            else:
                ubi = tdl.se_upti + 1
            for idx in range(ubi, i + 1):
                si = idx
                atr = self.sk_atr[idx-1] * self.sk_close[idx-1]
                extp= tdl.extendp(si)
                if tdl.dir > 0:
                    # 更新对tdl和bkl的触及状态
                    if tdl.se_sta % 2 == 1:
                        if not tdl.se_bek2i and self.sk_low[idx] <= tdl.se_bekp:
                            tdl.se_bek2i = idx
                    if tdl.se_sta % 2 == 0 and tdl.se_sta>0:
                        if not tdl.se_rek2i and self.sk_high[idx] >= tdl.se_rekp:
                            tdl.se_rek2i = idx

                    if tdl.se_sta % 2 == 1 and self.sk_high[idx] >= extp - rdet * atr:
                        tdl.se_berhs.append(idx)
                        tdl.se_bek3i = idx
                    if tdl.se_sta % 2 == 0 and self.sk_low[idx] <= extp + rdet * atr:
                        tdl.se_rerhs.append(idx)
                        tdl.se_rek3i = idx

                    if tdl.se_bklp:
                        if tdl.se_bkl_sta % 2 == 1 :
                            if self.sk_high[idx] >= tdl.se_bklp - rdet * atr:      #sk从下方向上触及bklp作为bek1信号
                                tdl.se_bkl_berhs.append(idx)
                                tdl.se_bek1i = idx
                            if not tdl.se_bek4i and 3<=tdl.se_bkl_sta<=5 and self.sk_low[idx] <= self.sk_ckl[tdl.se_bkl_beks[-1]][4] - mdet * atr:  #第一次sk从bklp上方突破作为bek4信号
                                tdl.se_bek4i = idx

                        if tdl.se_bkl_sta % 2 == 0 and self.sk_low[idx] <= tdl.se_bklp + rdet * atr:
                            tdl.se_bkl_rerhs.append(idx)

                        if tdl.se_bkl_sta % 2 != 1 and self.sk_close[idx] <= tdl.se_bklp - det * atr and self.sk_ckl[idx][0] < 0:
                            tdl.se_bkl_sta +=1
                            tdl.se_bkl_beks.append(idx)
                        elif tdl.se_bkl_sta % 2 != 0 and self.sk_close[idx] >= tdl.se_bklp + det * atr and self.sk_ckl[idx][0] > 0:
                            tdl.se_bkl_sta += 1
                            tdl.se_bkl_reks.append(idx)

                    # 更新对tdl和bkl的突破状态
                    if tdl.se_sta % 2 != 1 and self.sk_close[idx] <= extp - det * atr and self.sk_ckl[idx][0] < 0:
                        if 1:
                            tdl.se_bki = idx
                            tdl.se_besp = max(self.sk_ckl[idx][3], self.sk_high[self.sk_ckl[idx][5] - 1]) + det * atr
                            tdl.se_bekp = self.sk_ckl[idx][4]  - mdet * atr
                            tdl.se_sta += 1
                            tdl.se_beks.append(idx)
                            tdl.se_bek1i = None
                            tdl.se_bek2i = None
                            tdl.se_bek3i = None
                            tdl.se_bek4i = None
                            tdl.se_bklp = extp
                            tdl.se_bkl_sta = 1
                            tdl.se_bkl_beks=[idx]
                            tdl.se_bkl_reks = []
                            tdl.se_bkl_berhs = []
                            tdl.se_bkl_rerhs = []

                    elif tdl.se_sta % 2 != 0 and self.sk_close[idx] >= extp + det * atr and self.sk_ckl[idx][0] > 0:
                        if 1:
                            tdl.se_rti = idx
                            tdl.se_resp = min(self.sk_ckl[idx][4], self.sk_low[self.sk_ckl[idx][5] - 1]) - det * atr
                            tdl.se_rekp = self.sk_ckl[idx][3] + mdet * atr
                            tdl.se_sta += 1
                            tdl.se_reks.append(idx)

                            tdl.se_rek1i = None
                            tdl.se_rek2i = None
                            tdl.se_rek3i = None


                elif tdl.dir < 0:
                    if tdl.se_sta % 2 == 1:
                        if not tdl.se_bek2i and self.sk_high[idx] >= tdl.se_bekp + mdet * atr:
                            tdl.se_bek2i = idx
                    if tdl.se_sta % 2 == 0 and tdl.se_sta > 0:
                        if not tdl.se_rek2i and self.sk_low[idx] <= tdl.se_rekp - mdet * atr:
                            tdl.se_rek2i = idx

                    if tdl.se_sta % 2 == 1 and self.sk_low[idx] <= extp + rdet * atr:
                        tdl.se_berhs.append(idx)
                        tdl.se_bek3i = idx
                    if tdl.se_sta % 2 == 0 and self.sk_high[idx] >= extp - rdet * atr:
                        tdl.se_rerhs.append(idx)
                        tdl.se_rek3i = idx

                    if tdl.se_bklp:
                        if tdl.se_bkl_sta % 2 == 1:
                            if self.sk_low[idx] <= tdl.se_bklp + rdet * atr:  # sk从上方向上触及bklp作为bek1信号
                                tdl.se_bkl_berhs.append(idx)
                                tdl.se_bek1i = idx
                            if not tdl.se_bek4i and 3<=tdl.se_bkl_sta<=5 and self.sk_high[idx] >= self.sk_ckl[tdl.se_bkl_beks[-1]][3] + mdet * atr:  # 第一次sk从bklp下方突破作为bek4信号
                                tdl.se_bek4i = idx

                        if tdl.se_bkl_sta % 2 == 0 and self.sk_high[idx] >= tdl.se_bklp - rdet * atr:
                            tdl.se_bkl_rerhs.append(idx)

                        if tdl.se_bkl_sta % 2 != 1 and self.sk_close[idx] >= tdl.se_bklp + det * atr and self.sk_ckl[idx][0] > 0:
                            tdl.se_bkl_sta += 1
                            tdl.se_bkl_beks.append(idx)
                        elif tdl.se_bkl_sta % 2 != 0 and self.sk_close[idx] <= tdl.se_bklp - det * atr and self.sk_ckl[idx][0] < 0:
                            tdl.se_bkl_sta += 1
                            tdl.se_bkl_reks.append(idx)

                    # 更新对tdl和bkl的突破状态
                    if tdl.se_sta % 2 != 1 and self.sk_close[idx] >= extp + det * atr and self.sk_ckl[idx][0] > 0:
                        if 1:
                            tdl.se_bki = idx
                            tdl.se_besp = min(self.sk_ckl[idx][4], self.sk_low[self.sk_ckl[idx][5] - 1]) - det * atr
                            tdl.se_bekp = self.sk_ckl[idx][3] + mdet * atr
                            tdl.se_sta += 1
                            tdl.se_beks.append(idx)
                            tdl.se_bek1i = None
                            tdl.se_bek2i = None
                            tdl.se_bek3i = None
                            tdl.se_bek4i = None
                            tdl.se_bklp = extp
                            tdl.se_bkl_sta = 1
                            tdl.se_bkl_beks = [idx]
                            tdl.se_bkl_reks = []
                            tdl.se_bkl_berhs = []
                            tdl.se_bkl_rerhs = []

                    elif tdl.se_sta % 2 != 0 and self.sk_close[idx] <= extp - det * atr and self.sk_ckl[idx][0] < 0:
                        if 1:
                            tdl.se_rti = idx
                            tdl.se_resp = max(self.sk_ckl[idx][3], self.sk_high[self.sk_ckl[idx][5] - 1]) + det * atr
                            tdl.se_rekp = self.sk_ckl[idx][4]  - mdet * atr
                            tdl.se_sta += 1
                            tdl.se_reks.append(idx)

                            tdl.se_rek1i = None
                            tdl.se_rek2i = None
                            tdl.se_rek3i = None

                tdl.se_upti = idx
        else:
            if not tdl.et_upti:
                ubi = tdl.et_ini
                tdl.et_sta = 0
            else:
                ubi = tdl.et_upti + 1
            for idx in range(ubi, i+1):
                atr = self.sk_atr[idx-1] * self.sk_close[idx-1]
                si = upix[idx]
                if self.sk_dkcn.size>idx:
                    dkcn = self.sk_dkcn[idx]
                    extp = tdl.extendp(si) + mosi * tdl.ak/dkcn
                else:
                    extp = tdl.extendp(si)
                if tdl.dir > 0:
                    # 更新对tdl和bkl的触及状态
                    if tdl.et_sta % 2 == 1:
                        if not tdl.et_bek2i and self.sk_low[idx] <= tdl.et_bekp:
                            tdl.et_bek2i = idx
                    if tdl.et_sta % 2 == 0 and tdl.et_sta > 0:
                        if not tdl.et_rek2i and self.sk_high[idx] >= tdl.et_rekp:
                            tdl.et_rek2i = idx

                    if tdl.et_sta % 2 == 1 and self.sk_high[idx] >= extp - rdet * atr:
                        tdl.et_berhs.append(idx)
                        tdl.et_bek3i = idx
                    if tdl.et_sta % 2 == 0 and self.sk_low[idx] <= extp + rdet * atr:
                        tdl.et_rerhs.append(idx)
                        tdl.et_rek3i = idx

                    if tdl.et_bklp:
                        if tdl.et_bkl_sta % 2 == 1:
                            if self.sk_high[idx] >= tdl.et_bklp - rdet * atr:  # sk从下方向上触及bklp作为bek1信号
                                tdl.et_bkl_berhs.append(idx)
                                tdl.et_bek1i = idx
                            if not tdl.et_bek4i and 3<=tdl.et_bkl_sta<=5 and self.sk_low[idx] <= self.sk_ckl[tdl.et_bkl_beks[-1]][4] - mdet * atr:  # 第一次sk从bklp上方突破作为bek4信号
                                tdl.et_bek4i = idx

                        if tdl.et_bkl_sta % 2 == 0 and self.sk_low[idx] <= tdl.et_bklp + rdet * atr:
                            tdl.et_bkl_rerhs.append(idx)

                        if tdl.et_bkl_sta % 2 != 1 and self.sk_close[idx] <= tdl.et_bklp - det * atr and self.sk_ckl[idx][0] < 0:
                            tdl.et_bkl_sta += 1
                            tdl.et_bkl_beks.append(idx)
                        elif tdl.et_bkl_sta % 2 != 0 and self.sk_close[idx] >= tdl.et_bklp + det * atr and self.sk_ckl[idx][0] > 0:
                            tdl.et_bkl_sta += 1
                            tdl.et_bkl_reks.append(idx)

                    # 更新对tdl和bkl的突破状态
                    if tdl.et_sta % 2 != 1 and self.sk_close[idx] <= extp - det * atr and self.sk_ckl[idx][0] < 0:
                        if 1:
                            tdl.et_bki = idx
                            tdl.et_besp = max(self.sk_ckl[idx][3], self.sk_high[self.sk_ckl[idx][5] - 1]) + det * atr
                            tdl.et_bekp = self.sk_ckl[idx][4] - mdet * atr
                            tdl.et_sta += 1
                            tdl.et_beks.append(idx)
                            tdl.et_bek1i = None
                            tdl.et_bek2i = None
                            tdl.et_bek3i = None
                            tdl.et_bek4i = None
                            tdl.et_bklp = extp
                            tdl.et_bkl_sta = 1
                            tdl.et_bkl_beks = [idx]
                            tdl.et_bkl_reks = []
                            tdl.et_bkl_berhs = []
                            tdl.et_bkl_rerhs = []

                    elif tdl.et_sta % 2 != 0 and self.sk_close[idx] >= extp + det * atr and self.sk_ckl[idx][0] > 0:
                        if 1:
                            tdl.et_rti = idx
                            tdl.et_resp = min(self.sk_ckl[idx][4], self.sk_low[self.sk_ckl[idx][5] - 1]) - det * atr
                            tdl.et_rekp = self.sk_ckl[idx][3] + mdet * atr
                            tdl.et_sta += 1
                            tdl.et_reks.append(idx)

                            tdl.et_rek1i = None
                            tdl.et_rek2i = None
                            tdl.et_rek3i = None

                elif tdl.dir < 0:
                    if tdl.et_sta % 2 == 1:
                        if not tdl.et_bek2i and self.sk_high[idx] >= tdl.et_bekp + mdet * atr:
                            tdl.et_bek2i = idx
                    if tdl.et_sta % 2 == 0 and tdl.et_sta > 0:
                        if not tdl.et_rek2i and self.sk_low[idx] <= tdl.et_rekp - mdet * atr:
                            tdl.et_rek2i = idx

                    if tdl.et_sta % 2 == 1 and self.sk_low[idx] <= extp + rdet * atr:
                        tdl.et_berhs.append(idx)
                        tdl.et_bek3i = idx
                    if tdl.et_sta % 2 == 0 and self.sk_high[idx] >= extp - rdet * atr:
                        tdl.et_rerhs.append(idx)
                        tdl.et_rek3i = idx

                    if tdl.et_bklp:
                        if tdl.et_bkl_sta % 2 == 1:
                            if self.sk_low[idx] <= tdl.et_bklp + rdet * atr:  # sk从上方向上触及bklp作为bek1信号
                                tdl.et_bkl_berhs.append(idx)
                                tdl.et_bek1i = idx
                            if not tdl.et_bek4i and 3<=tdl.et_bkl_sta<=5 and self.sk_high[idx] >= self.sk_ckl[tdl.et_bkl_beks[-1]][3] + mdet * atr:  # 第一次sk从bklp下方突破作为bek4信号
                                tdl.et_bek4i = idx

                        if tdl.et_bkl_sta % 2 == 0 and self.sk_high[idx] >= tdl.et_bklp - rdet * atr:
                            tdl.et_bkl_rerhs.append(idx)

                        if tdl.et_bkl_sta % 2 != 1 and self.sk_close[idx] >= tdl.et_bklp + det * atr and self.sk_ckl[idx][0] > 0:
                            tdl.et_bkl_sta += 1
                            tdl.et_bkl_beks.append(idx)
                        elif tdl.et_bkl_sta % 2 != 0 and self.sk_close[idx] <= tdl.et_bklp - det * atr and self.sk_ckl[idx][0] < 0:
                            tdl.et_bkl_sta += 1
                            tdl.et_bkl_reks.append(idx)

                    # 更新对tdl和bkl的突破状态
                    if tdl.et_sta % 2 != 1 and self.sk_close[idx] >= extp + det * atr and self.sk_ckl[idx][0] > 0:
                        if 1:
                            tdl.et_bki = idx
                            tdl.et_besp = min(self.sk_ckl[idx][4], self.sk_low[self.sk_ckl[idx][5] - 1]) - det * atr
                            tdl.et_bekp = self.sk_ckl[idx][3] + mdet * atr
                            tdl.et_sta += 1
                            tdl.et_beks.append(idx)
                            tdl.et_bek1i = None
                            tdl.et_bek2i = None
                            tdl.et_bek3i = None
                            tdl.et_bek4i = None
                            tdl.et_bklp = extp
                            tdl.et_bkl_sta = 1
                            tdl.et_bkl_beks = [idx]
                            tdl.et_bkl_reks = []
                            tdl.et_bkl_berhs = []
                            tdl.et_bkl_rerhs = []

                    elif tdl.et_sta % 2 != 0 and self.sk_close[idx] <= extp - det * atr and self.sk_ckl[idx][0] < 0:
                        if 1:
                            tdl.et_rti = idx
                            tdl.et_resp = max(self.sk_ckl[idx][3], self.sk_high[self.sk_ckl[idx][5] - 1]) + det * atr
                            tdl.et_rekp = self.sk_ckl[idx][4] - mdet * atr
                            tdl.et_sta += 1
                            tdl.et_reks.append(idx)

                            tdl.et_rek1i = None
                            tdl.et_rek2i = None
                            tdl.et_rek3i = None

                tdl.et_upti = idx
                

    def sgnskatl(self, tdl, i, upix = None, mosi = 0):
        # 反向交易信号 bek0(信号确认后按收盘价进场 -市价单), bek1（信号确认后待回踩突破线进场 -限价单）, bek2（信号确认后待突破进场 -突破单），bek3（信号确认后待回踩tdl进场 -限价单）
        # 顺向交易信号 rek0(信号确认后按收盘价进场 -市价单), rek1（信号确认后待回踩突破线进场 -限价单）, rek2（信号确认后待突破进场 -突破单），rek3（信号确认后待回踩tdl进场 -限价单）
        # 信号命名格式： 信号类_信号点-tdl名称    eg: bek2_65-ma_rdl_bbl_60, bek1_65-ma_sa_45_2
        atr = self.sk_atr[i] * self.sk_close[i]
        det = self.det
        rdet = self.rdet
        mdet = self.mdet
        usrpsn = 4
        usrmsn = 1

        self.rek0 = None
        self.rek1 = None
        self.rek2 = None
        self.rek3 = None
        self.bek0 = None
        self.bek1 = None
        self.bek2 = None
        self.bek3 = None
        self.bek4 = None
        if not upix:
            si = i
            nextp = tdl.extendp(si+1)
            if tdl.se_sta % 2 == 0:
                if tdl.se_rti:
                    if not tdl.se_rek2i and tdl.se_sta<=5:
                        self.rek2 = tdl.se_rekp + mdet * atr * tdl.dir
                if tdl.se_sta <= 5:
                    self.rek3 = nextp + rdet * atr * tdl.dir

                #---------------------------------------------
                if self.rek0:
                    sgnna = 'rek0' + '_' +str(i) + '-' + tdl.fsocna
                    sgntyp = 'rek0'
                    bsdir = tdl.dir
                    sdop =  self.rek0
                    ordtyp = 'Mkt'
                    sdsp =  tdl.se_resp
                    sdtp = None
                    psn = usrpsn
                    msn = usrmsn
                    mark = i
                    prio = 0
                    self.trpkops[sgnna] = Sgnkop(sgnna, sgntyp, bsdir, sdop, ordtyp, sdsp, sdtp, psn, msn, mark, prio)
                # ---------------------------------------------
                if self.rek1:
                    sgnna = 'rek1' + '_' + str(i) + '-' + tdl.fsocna
                    sgntyp = 'rek0'
                    bsdir = tdl.dir
                    sdop = self.rek1
                    ordtyp = 'Lmt'
                    sdsp = tdl.se_resp
                    sdtp = None
                    psn = usrpsn
                    msn = usrmsn
                    mark = i
                    prio = 0
                    self.trpkops[sgnna] = Sgnkop(sgnna, sgntyp, bsdir, sdop, ordtyp, sdsp, sdtp, psn, msn, mark, prio)
                # ---------------------------------------------
                if self.rek2:
                    sgnna = 'rek2' + '_' + str(i) + '-' + tdl.fsocna
                    sgntyp = 'rek2'
                    bsdir = tdl.dir
                    sdop = self.rek2
                    ordtyp = 'Stp'
                    sdsp = tdl.se_resp
                    sdtp = None
                    psn = usrpsn
                    msn = usrmsn
                    mark = i
                    prio = 0
                    self.trpkops[sgnna] = Sgnkop(sgnna, sgntyp, bsdir, sdop, ordtyp, sdsp, sdtp, psn, msn, mark, prio)
                # ---------------------------------------------
                if self.rek3:
                    sgnna = 'rek3' + '_' + str(i) + '-' + tdl.fsocna
                    sgntyp = 'rek3'
                    bsdir = tdl.dir
                    sdop = self.rek3
                    ordtyp = 'Lmt'
                    sdsp = tdl.se_resp
                    sdtp = None
                    psn = usrpsn
                    msn = usrmsn
                    mark = i
                    prio = 0
                    self.trpkops[sgnna] = Sgnkop(sgnna, sgntyp, bsdir, sdop, ordtyp, sdsp, sdtp, psn, msn, mark, prio)
            if tdl.se_sta % 2 == 1:
                if not tdl.se_bek1i and tdl.se_sta <= 5:
                    self.bek1 = tdl.se_bklp - rdet * atr * tdl.dir

                if not tdl.se_bek2i and tdl.se_sta <= 5:
                    self.bek2 = tdl.se_bekp
                if tdl.se_sta <= 5:
                    self.bek3 = nextp - rdet * atr * tdl.dir

                if not tdl.se_bek4i and (tdl.se_bkl_sta == 3 or tdl.se_bkl_sta == 5) :  # 第一次sk从bklp上方突破作为bek4信号
                    self.bek4 = self.sk_ckl[tdl.se_bkl_beks[-1]][4] - mdet * atr * tdl.dir
                # ---------------------------------------------
                if self.bek0:
                    sgnna = 'bek0' + '_' + str(i) + '-' + tdl.fsocna
                    sgntyp = 'bek0'
                    bsdir = -tdl.dir
                    sdop = self.bek0
                    ordtyp = 'Mkt'
                    sdsp = tdl.se_besp
                    sdtp = None
                    psn = usrpsn
                    msn = usrmsn
                    mark = i
                    prio = 0
                    self.trpkops[sgnna] = Sgnkop(sgnna, sgntyp, bsdir, sdop, ordtyp, sdsp, sdtp, psn, msn, mark, prio)
                # ---------------------------------------------
                if self.bek1:
                    sgnna = 'bek1' + '_' + str(i) + '-' + tdl.fsocna
                    sgntyp = 'bek0'
                    bsdir = -tdl.dir
                    sdop = self.bek1
                    ordtyp = 'Lmt'
                    sdsp = tdl.se_besp
                    sdtp = None
                    psn = usrpsn
                    msn = usrmsn
                    mark = i
                    prio = 0
                    self.trpkops[sgnna] = Sgnkop(sgnna, sgntyp, bsdir, sdop, ordtyp, sdsp, sdtp, psn, msn, mark, prio)
                # ---------------------------------------------
                if self.bek2:
                    sgnna = 'bek2' + '_' + str(i) + '-' + tdl.fsocna
                    sgntyp = 'bek2'
                    bsdir = -tdl.dir
                    sdop = self.bek2
                    ordtyp = 'Stp'
                    sdsp = tdl.se_besp
                    sdtp = None
                    psn = usrpsn
                    msn = usrmsn
                    mark = i
                    prio = 0
                    self.trpkops[sgnna] = Sgnkop(sgnna, sgntyp, bsdir, sdop, ordtyp, sdsp, sdtp, psn, msn, mark, prio)
                # ---------------------------------------------
                if self.bek3:
                    sgnna = 'bek3' + '_' + str(i) + '-' + tdl.fsocna
                    sgntyp = 'bek3'
                    bsdir = -tdl.dir
                    sdop = self.bek3
                    ordtyp = 'Lmt'
                    sdsp = tdl.se_besp
                    sdtp = None
                    psn = usrpsn
                    msn = usrmsn
                    mark = i
                    prio = 0
                    self.trpkops[sgnna] = Sgnkop(sgnna, sgntyp, bsdir, sdop, ordtyp, sdsp, sdtp, psn, msn, mark, prio)
                # ---------------------------------------------
                if self.bek4:
                    sgnna = 'bek4' + '_' + str(i) + '-' + tdl.fsocna
                    sgntyp = 'bek4'
                    bsdir = -tdl.dir
                    sdop = self.bek4
                    ordtyp = 'Lmt'
                    sdsp = tdl.se_besp
                    sdtp = None
                    psn = usrpsn
                    msn = 1
                    mark = i
                    prio = 0
                    self.trpkops[sgnna] = Sgnkop(sgnna, sgntyp, bsdir, sdop, ordtyp, sdsp, sdtp, psn, msn, mark, prio)

        else:
            si = upix[i]
            if self.sk_dkcn.size > i:
                dkcn = self.sk_dkcn[i]
                nextp = tdl.extendp(si) + (mosi+1) * tdl.ak / dkcn
            else:
                nextp = tdl.extendp(si)
            if tdl.et_sta % 2 == 0:
                if tdl.et_rti:
                    if not tdl.et_rek2i and tdl.et_sta<=5 :
                        self.rek2 = tdl.et_rekp + mdet * atr * tdl.dir
                if tdl.et_sta <= 5:
                    self.rek3 = nextp + rdet * atr * tdl.dir

                # ---------------------------------------------
                if self.rek0:
                    sgnna = 'rek0' + '_' + str(i) + '-' + tdl.fsocna
                    sgntyp = 'rek0'
                    bsdir = tdl.dir
                    sdop = self.rek0
                    ordtyp = 'Mkt'
                    sdsp = tdl.et_resp
                    sdtp = None
                    psn = usrpsn
                    msn = usrmsn
                    mark = i
                    prio = 0
                    self.trpkops[sgnna] = Sgnkop(sgnna, sgntyp, bsdir, sdop, ordtyp, sdsp, sdtp, psn, msn, mark, prio)
                # ---------------------------------------------
                if self.rek1:
                    sgnna = 'rek1' + '_' + str(i) + '-' + tdl.fsocna
                    sgntyp = 'rek0'
                    bsdir = tdl.dir
                    sdop = self.rek1
                    ordtyp = 'Lmt'
                    sdsp = tdl.et_resp
                    sdtp = None
                    psn = usrpsn
                    msn = usrmsn
                    mark = i
                    prio = 0
                    self.trpkops[sgnna] = Sgnkop(sgnna, sgntyp, bsdir, sdop, ordtyp, sdsp, sdtp, psn, msn, mark, prio)
                # ---------------------------------------------
                if self.rek2:
                    sgnna = 'rek2' + '_' + str(i) + '-' + tdl.fsocna
                    sgntyp = 'rek2'
                    bsdir = tdl.dir
                    sdop = self.rek2
                    ordtyp = 'Stp'
                    sdsp = tdl.et_resp
                    sdtp = None
                    psn = usrpsn
                    msn = usrmsn
                    mark = i
                    prio = 0
                    self.trpkops[sgnna] = Sgnkop(sgnna, sgntyp, bsdir, sdop, ordtyp, sdsp, sdtp, psn, msn, mark, prio)
                # ---------------------------------------------
                if self.rek3:
                    try:
                        sgnna = 'rek3' + '_' + str(i) + '-' + tdl.fsocna
                    except:
                        pass
                    sgntyp = 'rek3'
                    bsdir = tdl.dir
                    sdop = self.rek3
                    ordtyp = 'Lmt'
                    sdsp = tdl.et_resp
                    sdtp = None
                    psn = usrpsn
                    msn = usrmsn
                    mark = i
                    prio = 0
                    self.trpkops[sgnna] = Sgnkop(sgnna, sgntyp, bsdir, sdop, ordtyp, sdsp, sdtp, psn, msn, mark, prio)
            if tdl.et_sta % 2 == 1:
                if not tdl.et_bek1i and tdl.et_sta <= 5:
                    self.bek1 = tdl.et_bklp - rdet * atr * tdl.dir

                if not tdl.et_bek2i and tdl.et_sta <= 5:
                    self.bek2 = tdl.et_bekp
                if tdl.et_sta <= 5:
                    self.bek3 = nextp - rdet * atr * tdl.dir

                if not tdl.et_bek4i and (tdl.et_bkl_sta == 3 or tdl.et_bkl_sta == 5):  # 第一次sk从bklp上方突破作为bek4信号
                    self.bek4 = self.sk_ckl[tdl.et_bkl_beks[-1]][4] - mdet * atr * tdl.dir
                # ---------------------------------------------
                if self.bek0:
                    sgnna = 'bek0' + '_' + str(i) + '-' + tdl.fsocna
                    sgntyp = 'bek0'
                    bsdir = -tdl.dir
                    sdop = self.bek0
                    ordtyp = 'Mkt'
                    sdsp = tdl.et_besp
                    sdtp = None
                    psn = usrpsn
                    msn = usrmsn
                    mark = i
                    prio = 0
                    self.trpkops[sgnna] = Sgnkop(sgnna, sgntyp, bsdir, sdop, ordtyp, sdsp, sdtp, psn, msn, mark, prio)
                # ---------------------------------------------
                if self.bek1:
                    sgnna = 'bek1' + '_' + str(i) + '-' + tdl.fsocna
                    sgntyp = 'bek0'
                    bsdir = -tdl.dir
                    sdop = self.bek1
                    ordtyp = 'Lmt'
                    sdsp = tdl.et_besp
                    sdtp = None
                    psn = usrpsn
                    msn = usrmsn
                    mark = i
                    prio = 0
                    self.trpkops[sgnna] = Sgnkop(sgnna, sgntyp, bsdir, sdop, ordtyp, sdsp, sdtp, psn, msn, mark, prio)
                # ---------------------------------------------
                if self.bek2:
                    sgnna = 'bek2' + '_' + str(i) + '-' + tdl.fsocna
                    sgntyp = 'bek2'
                    bsdir = -tdl.dir
                    sdop = self.bek2
                    ordtyp = 'Stp'
                    sdsp = tdl.et_besp
                    sdtp = None
                    psn = usrpsn
                    msn = usrmsn
                    mark = i
                    prio = 0
                    self.trpkops[sgnna] = Sgnkop(sgnna, sgntyp, bsdir, sdop, ordtyp, sdsp, sdtp, psn, msn, mark, prio)
                # ---------------------------------------------
                if self.bek3:
                    sgnna = 'bek3' + '_' + str(i) + '-' + tdl.fsocna
                    sgntyp = 'bek3'
                    bsdir = -tdl.dir
                    sdop = self.bek3
                    ordtyp = 'Lmt'
                    sdsp = tdl.et_besp
                    sdtp = None
                    psn = usrpsn
                    msn = usrmsn
                    mark = i
                    prio = 0
                    self.trpkops[sgnna] = Sgnkop(sgnna, sgntyp, bsdir, sdop, ordtyp, sdsp, sdtp, psn, msn, mark, prio)
                # ---------------------------------------------
                if self.bek4:
                    sgnna = 'bek4' + '_' + str(i) + '-' + tdl.fsocna
                    sgntyp = 'bek4'
                    bsdir = -tdl.dir
                    sdop = self.bek4
                    ordtyp = 'Lmt'
                    sdsp = tdl.et_besp
                    sdtp = None
                    psn = usrpsn
                    msn = usrmsn
                    mark = i
                    prio = 0
                    self.trpkops[sgnna] = Sgnkop(sgnna, sgntyp, bsdir, sdop, ordtyp, sdsp, sdtp, psn, msn, mark, prio)

#---------------------------------------------------------------------------


#------------------------开仓信号------
class Sgnkop(object):
    def __init__(self, sgnna=None, sgntyp=None, bsdir=None, sdop=None, ordtyp='Lmt', sdsp=None, sdtp=None, psn=None, msn = None, mark=None, prio=0):
        self.sgnna = sgnna   # 拟开仓仓的信号名称
        self.sgntyp = sgntyp
        self.bsdir = bsdir
        self.sdop = sdop
        self.ordtyp = ordtyp
        self.sdsp = sdsp
        self.sdtp = sdtp
        self.psn = psn
        self.msn = msn
        self.mark = mark
        self.prio = prio
#------------------------止损平仓信号-----
class Sgncst(object):
    def __init__(self, sgnna=None, sgntyp=None, bsdir=None, sdsp=None, mark=None, prio=0):
        self.sgnna = sgnna    # 拟平持仓的信号名称，为xx-all 则平此类信号的所有持仓
        self.sgntyp = sgntyp
        self.bsdir = bsdir
        self.sdsp = sdsp
        self.mark = mark
        self.prio = prio

#------------------------获利平仓信号-----
class Sgnctp(object):
    def __init__(self, sgnna=None, sgntyp=None, bsdir=None, sdtp=None, mark=None, prio=0):
        self.sgnna = sgnna   # 拟平持仓的信号名称 xx-all 则平此类信号的所有持仓
        self.sgntyp = sgntyp
        self.bsdir = bsdir
        self.sdtp = sdtp
        self.mark = mark
        self.prio = prio


class Sgnsource(object):  # 同源信号
    def __init__(self, socna =None, kop_dic=None, cst_dic=None, ctp_dic=None, fresh= 0):
        self.socna = socna
        self.sockop = deepcopy(kop_dic)
        self.soccst = deepcopy(cst_dic)
        self.socctp = deepcopy(ctp_dic)
        self.fresh  = fresh

class Sgnman(object):  # 信号强度管理
    def __init__(self, ):
        self.lgsgn = {
            'tdk1-bbl' : {'prio':5, 'cmat': []},
            'tdk3-bbl' : {'prio':5, 'cmat': ['tdk2-bbl', 'tdk4-bbl']},
            'tdk5-bbl' : {'prio':5, 'cmat': ['tdk2-bbl', 'tdk4-bbl']},
            'tdk0-ttl' : {'prio':5, 'cmat': ['tdk2-bbl', 'tdk4-bbl']},
            'tdk2-ttl' : {'prio':6, 'cmat': ['tdk2-bbl', 'tdk4-bbl']},
            'tdk4-ttl' : {'prio':5, 'cmat': ['tdk2-bbl', 'tdk4-bbl']},
            'tdk6-ttl' : {'prio':7, 'cmat': ['tdk2-bbl', 'tdk4-bbl']},
            'tdk1-sa': {'prio': 5, 'cmat': []},
            'tdk3-sa': {'prio': 5, 'cmat': ['tdk2-sa', 'tdk4-sa']},
            'tdk5-sa': {'prio': 5, 'cmat': ['tdk2-sa', 'tdk4-sa']},
            'tdk0-sd': {'prio': 5, 'cmat': ['tdk2-sa', 'tdk4-sa']},
            'tdk2-sd': {'prio': 6, 'cmat': ['tdk2-sa', 'tdk4-sa']},
            'tdk4-sd': {'prio': 5, 'cmat': ['tdk2-sa', 'tdk4-sa']},
            'tdk6-sd': {'prio': 7, 'cmat': ['tdk2-sa', 'tdk4-sa']},
        }

        self.stsgn = {
            'tdk1-ttl': {'prio':5, 'cmat': []},
            'tdk3-ttl': {'prio':5, 'cmat': ['tdk2-ttl', 'tdk4-ttl']},
            'tdk5-ttl': {'prio':5, 'cmat': ['tdk2-ttl', 'tdk4-ttl']},
            'tdk0-bbl': {'prio':5, 'cmat': ['tdk2-ttl', 'tdk4-ttl']},
            'tdk2-bbl': {'prio':5, 'cmat': ['tdk2-ttl', 'tdk4-ttl']},
            'tdk4-bbl': {'prio':5, 'cmat': ['tdk2-ttl', 'tdk4-ttl']},
            'tdk6-bbl': {'prio':5, 'cmat': ['tdk2-ttl', 'tdk4-ttl']},
            'tdk1-sd': {'prio': 5, 'cmat': []},
            'tdk3-sd': {'prio': 5, 'cmat': ['tdk2-sd', 'tdk4-sd']},
            'tdk5-sd': {'prio': 5, 'cmat': ['tdk2-sd', 'tdk4-sd']},
            'tdk0-sa': {'prio': 5, 'cmat': ['tdk2-sd', 'tdk4-sd']},
            'tdk2-sa': {'prio': 5, 'cmat': ['tdk2-sd', 'tdk4-sd']},
            'tdk4-sa': {'prio': 5, 'cmat': ['tdk2-sd', 'tdk4-sd']},
            'tdk6-sa': {'prio': 5, 'cmat': ['tdk2-sd', 'tdk4-sd']},
        }


class Intsgnbs(object):
    def __init__(self, tdkopset, skatsel, skatetl, mafs, sufs = None, upix = None, mosi = 0):
        self.tdkopset = tdkopset
        self.skatsel = skatsel
        self.skatetl = skatetl
        self.mafs = mafs
        self.sufs = sufs
        self.upix = upix
        self.mosi = mosi

        self.cmbkops = {}
        self.sgnsocs = {}  # 源信号字典
        self.sgnman = Sgnman()
        self.isgnkop = {}
        self.isgncst = {}
        self.isgnctp = {}

    # ------------------------------------------
    def sesgnbs(self, i):
        kopset = self.tdkopset['sekop']
        rstdir = self.mafs['rstdir']
        bbls_dic = self.mafs['bbls']
        ttls_dic = self.mafs['ttls']
        sals_dic = self.mafs['sals']
        upsas = self.mafs['upsas']
        dwsas = self.mafs['dwsas']

        if self.skatsel.sgni != i:
            self.skatsel.trpkops = {}
            self.skatsel.sgni = i
        crtsal = None
        presal = None

        crtb_rdl = None
        preb_rdl = None
        crtt_rdl = None
        pret_rdl = None

        crtb_mdl = None
        preb_mdl = None
        crtt_mdl = None
        pret_mdl = None

        if len(sals_dic) > 0:
            crtsal = sals_dic.values()[-1]
        if len(sals_dic) > 1:
            presal = sals_dic.values()[-2]

        if len(bbls_dic) > 0:
            crtb_rdl = bbls_dic.values()[-1]['rdl']
            crtb_mdl = bbls_dic.values()[-1]['mdl']
        if len(bbls_dic) > 1:
            preb_rdl = bbls_dic.values()[-2]['rdl']
            preb_mdl = bbls_dic.values()[-2]['mdl']
        if len(ttls_dic) > 0:
            crtt_rdl = ttls_dic.values()[-1]['rdl']
            crtt_mdl = ttls_dic.values()[-1]['mdl']
        if len(ttls_dic) > 1:
            pret_rdl = ttls_dic.values()[-2]['rdl']
            pret_mdl = ttls_dic.values()[-2]['mdl']

        if 'sal' in kopset and  kopset['sal'] >=1 and crtsal:
            self.skatsel.sgnskatl(crtsal, i)
        if 'sal' in kopset and  kopset['sal'] >=2 and presal:
            self.skatsel.sgnskatl(presal, i)
        # ----------------------------------
        if 'rdl' in kopset and  kopset['rdl'] >=1 and crtb_rdl:
            self.skatsel.sgnskatl(crtb_rdl, i)
        if 'rdl' in kopset and  kopset['rdl'] >=1 and crtt_rdl:
            self.skatsel.sgnskatl(crtt_rdl, i)
        #----------------------------------
        if 'rdl' in kopset and  kopset['rdl'] >=2 and preb_rdl:
            self.skatsel.sgnskatl(preb_rdl, i)
        if 'rdl' in kopset and  kopset['rdl'] >=2 and pret_rdl:
            self.skatsel.sgnskatl(pret_rdl, i)

        # ----------------------------------
        if 'mdl' in kopset and  kopset['mdl'] >=1 and crtb_mdl:
            self.skatsel.sgnskatl(crtb_mdl, i)
        if 'mdl' in kopset and  kopset['mdl'] >=1 and crtt_mdl:
            self.skatsel.sgnskatl(crtt_mdl, i)
        # ----------------------------------
        if 'mdl' in kopset and  kopset['mdl'] >=2 and preb_mdl:
            self.skatsel.sgnskatl(preb_mdl, i)
        if 'mdl' in kopset and  kopset['mdl'] >=2 and pret_mdl:
            self.skatsel.sgnskatl(pret_mdl, i)

        if len(upsas) > 0:
            crtupr = upsas.values()[-1]
        else:
            crtupr = None
        if len(dwsas) > 0:
            crtdwr = dwsas.values()[-1]
        else:
            crtdwr = None

    # ------------------------------------------
    def etsgnbs(self, i):
        if self.sufs is None:
            return
        kopset = self.tdkopset['etkop']
        rstdir = self.sufs['rstdir']
        bbls_dic = self.sufs['bbls']
        ttls_dic = self.sufs['ttls']
        sals_dic = self.sufs['sals']
        upsas = self.sufs['upsas']
        dwsas = self.sufs['dwsas']

        if self.skatetl.sgni != i:
            self.skatetl.trpkops = {}
            self.skatetl.sgni = i
        crtsal = None
        presal = None

        crtb_rdl = None
        preb_rdl = None
        crtt_rdl = None
        pret_rdl = None

        crtb_mdl = None
        preb_mdl = None
        crtt_mdl = None
        pret_mdl = None

        if len(sals_dic) > 0:
            crtsal = sals_dic.values()[-1]
        if len(sals_dic) > 1:
            presal = sals_dic.values()[-2]

        if len(bbls_dic) > 0:
            crtb_rdl = bbls_dic.values()[-1]['rdl']
            crtb_mdl = bbls_dic.values()[-1]['mdl']
        if len(bbls_dic) > 1:
            preb_rdl = bbls_dic.values()[-2]['rdl']
            preb_mdl = bbls_dic.values()[-2]['mdl']
        if len(ttls_dic) > 0:
            crtt_rdl = ttls_dic.values()[-1]['rdl']
            crtt_mdl = ttls_dic.values()[-1]['mdl']
        if len(ttls_dic) > 1:
            pret_rdl = ttls_dic.values()[-2]['rdl']
            pret_mdl = ttls_dic.values()[-2]['mdl']

        if 'sal' in kopset and  kopset['sal'] >=1 and crtsal:
            self.skatetl.sgnskatl(crtsal, i, self.upix, self.mosi)
        if 'sal' in kopset and  kopset['sal'] >=2 and presal:
            self.skatetl.sgnskatl(presal, i, self.upix, self.mosi)
        # ----------------------------------
        if 'rdl' in kopset and  kopset['rdl'] >=1 and crtb_rdl:
            self.skatetl.sgnskatl(crtb_rdl, i, self.upix, self.mosi)
        if 'rdl' in kopset and  kopset['rdl'] >=1 and crtt_rdl:
            self.skatetl.sgnskatl(crtt_rdl, i, self.upix, self.mosi)
        # ----------------------------------
        if 'rdl' in kopset and  kopset['rdl'] >=2 and preb_rdl:
            self.skatetl.sgnskatl(preb_rdl, i, self.upix, self.mosi)
        if 'rdl' in kopset and  kopset['rdl'] >=2 and pret_rdl:
            self.skatetl.sgnskatl(pret_rdl, i, self.upix, self.mosi)
        # ----------------------------------
        if 'mdl' in kopset and  kopset['mdl'] >=1 and crtb_mdl:
            self.skatetl.sgnskatl(crtb_mdl, i, self.upix, self.mosi)
        if 'mdl' in kopset and  kopset['mdl'] >=1 and crtt_mdl:
            self.skatetl.sgnskatl(crtt_mdl, i, self.upix, self.mosi)
        # ----------------------------------
        if 'mdl' in kopset and  kopset['mdl'] >=2 and preb_mdl:
            self.skatetl.sgnskatl(preb_mdl, i, self.upix, self.mosi)
        if 'mdl' in kopset and  kopset['mdl'] >=2 and pret_mdl:
            self.skatetl.sgnskatl(pret_mdl, i, self.upix, self.mosi)

        if len(upsas) > 0:
            crtupr = upsas.values()[-1]
        else:
            crtupr = None
        if len(dwsas) > 0:
            crtdwr = dwsas.values()[-1]
        else:
            crtdwr = None


    # ------------------------------------------根据新开仓信号和持仓整合新进场和出场信号
    def cmbsgn(self, socpos_dic):
        # 1、根据新开仓信号和信号持仓字典决定新开仓是否生效
        # 2、调整同源持仓的止损和目标
        # 3、根据信号源之间的优先关系调整异源信号开仓和持仓
        self.cmbkops = {}

        kopsdic = self.skatsel.trpkops
        sgni = self.skatsel.sgni
        for sgn, kop in kopsdic.iteritems():
            ckpos = None
            sgnid = sgn.split('_')[0]
            socna = sgn.split('-')[1]
            if kop.sdsp:
                if (kop.bsdir > 0 and kop.sdsp > kop.sdop) or (kop.bsdir < 0 and kop.sdsp < kop.sdop):
                    continue

            if sgnid in ['bek1', 'bek2']:
                if socna not in socpos_dic:
                    ckpos = kop
                elif 'bek1' in socpos_dic[socna] or 'bek2' in socpos_dic[socna]:
                    continue
                else:
                    ckpos = kop
            else:
                try:
                    pos = socpos_dic[socna][sgnid][-1]
                    if abs(kop.sdop - pos.EntPrice) >= self.skatsel.sk_atr[sgni] * self.skatsel.sk_close[sgni] * 2:
                        ckpos = kop
                except:
                    ckpos = kop
            if ckpos:
                if socna in self.cmbkops:
                    if sgnid in self.cmbkops[socna]:
                        self.cmbkops[socna][sgnid].append(kop)
                    else:
                        self.cmbkops[socna][sgnid] = [kop]
                else:
                    self.cmbkops[socna] = {sgnid: [kop]}

        #---------------
        kopsdic = self.skatetl.trpkops
        sgni = self.skatetl.sgni
        for sgn, kop in kopsdic.iteritems():
            ckpos = None
            sgnid = sgn.split('_')[0]
            socna = sgn.split('-')[1]
            if kop.sdsp:
                if (kop.bsdir > 0 and kop.sdsp > kop.sdop) or (kop.bsdir < 0 and kop.sdsp < kop.sdop):
                    continue

            if sgnid in ['bek1', 'bek2']:
                if socna not in socpos_dic:
                    ckpos = kop
                elif 'bek1' in socpos_dic[socna] or 'bek2' in socpos_dic[socna]:
                    continue
                else:
                    ckpos = kop
            else:
                try:
                    pos = socpos_dic[socna][sgnid][-1]
                    if abs(kop.sdop - pos.EntPrice) >= self.skatetl.sk_atr[sgni] * self.skatetl.sk_close[sgni] * 2:
                        ckpos = kop
                except:
                    ckpos = kop
            if ckpos:
                if socna in self.cmbkops:
                    if sgnid in self.cmbkops[socna]:
                        self.cmbkops[socna][sgnid].append(kop)
                    else:
                        self.cmbkops[socna][sgnid] = [kop]
                else:
                    self.cmbkops[socna] = {sgnid: [kop]}

        #-----------------
        for socna, sgnpos in socpos_dic.iteritems():
            rek1op = None
            rek2op = None
            rek3op = None

            bek1op = None
            bek2op = None
            bek3op = None
            bek4op = None
            try:
                bek1op = self.cmbkops[socna]['bek1'][-1].sdop
            except:
                pass
            try:
                bek2op = self.cmbkops[socna]['bek2'][-1].sdop
            except:
                pass

            try:
                rek3s= sgnpos['rek3']
                for pos in rek3s:
                    if not pos.EntSp or (bek2op and ( pos.EntSp - bek2op ) * pos.EntSize < 0 ):
                        pos.EntSp = bek2op

                    if not pos.EntTp or (bek1op and ( pos.EntTp - bek1op ) * pos.EntSize > 0 ):
                        pos.EntTp = bek1op
            except:
                pass


    # ------------------------------------------
    def addsgn(self, socna =None, kop_dic=None, cst_dic=None, ctp_dic=None, fresh=0):
        newsgnsoc = Sgnsource(socna, kop_dic, cst_dic, ctp_dic, fresh)
        self.sgnsocs[socna] = newsgnsoc


    # ------------------------------------------
    def intsgn(self):
        self.isgnkop.clear()
        self.isgncst.clear()
        self.isgnctp.clear()
        # -----同源信号的决策整合
        # -----同类源信号的决策整合
        # -----异源信号的决策整合

        for socna, sgnsoc in self.sgnsocs.iteritems():
            if sgnsoc.sockop:
                self.isgnkop = dict(self.isgnkop, **sgnsoc.sockop)
            if sgnsoc.soccst:
                self.isgncst = dict(self.isgncst, **sgnsoc.soccst)
            if sgnsoc.socctp:
                self.isgnctp = dict(self.isgnctp, **sgnsoc.socctp)


        #-----交叉信号的决策整合，生成一些通用信号的平仓指令，生成一些综合开仓信号，处理可能的过时信号的仓位
    #--------------------------------------------------------------------------------------------
    def samsocsgn(self, sgnna, sgnost='cst'):  # 根据开仓信号 从整合的字典中查找【同源信号】
        if sgnost == 'kop':
            sgn_dic = self.isgnkop
        elif sgnost == 'cst':
            sgn_dic = self.isgncst
        elif sgnost == 'ctp':
            sgn_dic = self.isgnctp
        else:
            sgn_dic = None

        if not sgn_dic:
            return None

        if 'tdk' in sgnna:
            if sgnost == 'kop':
                fsgnna = sgnna
            elif sgnost == 'cst':
                fsgnna = sgnna.replace('tdk', 'cst')
            elif sgnost == 'ctp':
                fsgnna = sgnna.replace('tdk', 'ctp')
            else:
                fsgnna = None
        else:
            return None
        if fsgnna in sgn_dic:
            return sgn_dic[fsgnna]
        else:
            return None

    def simsocsgn(self, sgnna, sgnost='cst', frech = 0 ):  # 根据开仓信号 从整合的字典中查找【同类源信号】 格式形如：sgnna = 'tdk0-bbl_87' , sgnost='kop'/'cst'/'ctp'
        # sgntyp = sgnna.split('-')[0]
        # socna = sgnna.split('-')[1]
        # soctyp = socna.split('_')[0]
        # sgnid = sgnna.split('_')[0]
        if sgnost == 'kop':
            sgn_dic = self.isgnkop
        elif sgnost == 'cst':
            sgn_dic = self.isgncst
        elif sgnost == 'ctp':
            sgn_dic = self.isgnctp
        else:
            sgn_dic = None

        if not sgn_dic:
            return None
        if 'tdk' in sgnna:
            if sgnost == 'kop':
                fsgnna = sgnna
            elif sgnost == 'cst':
                fsgnna = sgnna.replace('tdk', 'cst')
            elif sgnost == 'ctp':
                fsgnna = sgnna.replace('tdk', 'ctp')
            else:
                fsgnna = None
        else:
            return None

        if not fsgnna:
            return None

        if fsgnna in sgn_dic:
            return sgn_dic[fsgnna]
        #----------------------------查找同类源相似的信号
        fsgnid = fsgnna.split('_')[0]
        for isgnna, sgnbs in  sgn_dic.iteritems():
            isgnid = isgnna.split('_')[0]
            isocna = isgnna.split('-')[1]
            if fsgnid != isgnid:
                continue
            if self.sgnsocs[isocna].fresh == frech:
                return sgnbs
        return None

    def difsocsgn(self, sgnna, sgnost='kop', frech =0 ):  # 根据开仓信号 从整合的字典中查找【异源信号】
        # sgntyp = sgnna.split('-')[0]
        # socna = sgnna.split('-')[1]
        # soctyp = socna.split('_')[0]
        sgnid = sgnna.split('_')[0]
        if sgnid in self.sgnman.lgsgn:
            matsgns = self.sgnman.lgsgn[sgnid]['cmat']
        elif sgnid in self.sgnman.stsgn:
            matsgns = self.sgnman.stsgn[sgnid]['cmat']
        if not matsgns:
            return None
        for msgnid in matsgns:
            msgnna = msgnid+'_x'
            msgnbs = self.simsocsgn( msgnna, sgnost=sgnost, frech = frech )
            if msgnbs:
                return msgnbs
        return None


#---------------------------------------------------------------------------
class Rsband(object):
    def __init__(self, dtbi, dtei, bandhp, bandlp):
        self.dtbi = dtbi
        self.dtei = dtei
        self.bandhp = bandhp
        self.bandlp = bandlp
#---------------------------------------------------------------------------
class Rsbandvec(object):
    def __init__(self, rsdir = 1, maxbds = 10):
        self.rsdir = rsdir  # 趋势方向 ，1：上升（按低点从大到小排序）  -1：下降（按高点从小到大排序）
        self.rsdtvec = []   # 按时间从大到小排序的队列
        self.rspvec  = []   # 按价格大小排序
        self.maxbds  = maxbds
        self.mindti  = 0
        self.count   = 0

    def cmpbydt(self, bd1, bd2):
        return  1 if  bd2.dtei - bd1.dtei > 0 else -1

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
        if self.count > 0 :
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
        if -self.count <= index <= self.count-1 and self.count > 0 :
            return self.rsdtvec[index]
        else:
            return None
    def getbandby_rsp(self, index):
        if -self.count <= index <= self.count-1 and self.count > 0 :
            return self.rspvec[index]
        else:
            return None

    def getbandby_bmp(self, mx= 'min'):
        if self.count ==1 :
            return self.rsdtvec[0]
        elif self.count >1 :
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
        self.rsti   = rsti  # 转折确认点
        self.rstp   = rstp
        self.rstbi  = rsti  # 转折起点

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
        if self.rstdir > 0 and bandvec.rsdir > 0 :
            if bandvec.count > 0:
                tepband = bandvec.getbandby_rsp(0)
                self.rsp_qs1c = tepband.bandlp
                self.rsp_qs1a = tepband.bandhp
            if bandvec.count > 1:
                tepband = bandvec.getbandby_rsp(1)
                self.rsp_qs2c = tepband.bandlp
                self.rsp_qs2a = tepband.bandhp
        elif self.rstdir < 0 and bandvec.rsdir < 0 :
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
        rsdir = 'dw' if self.rstdir >0 else 'up'
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
    def __init__(self, sk_open, sk_high, sk_low, sk_close, sk_atr, sk_itp, sk_disrst, sk_zsh, sk_zsl, sk_bsh, sk_bsl, sk_rstn, sk_rstspl, sk_rstsph, sk_sgn):
        self.sk_open = sk_open
        self.sk_high = sk_high
        self.sk_low  = sk_low
        self.sk_close= sk_close
        self.sk_atr  = sk_atr

        self.sk_disrst = sk_disrst
        self.sk_itp    = sk_itp
        self.sk_zsh    = sk_zsh
        self.sk_zsl    = sk_zsl
        self.sk_bsh    = sk_bsh
        self.sk_bsl    = sk_bsl
        self.sk_rstn   = sk_rstn
        self.sk_rstspl = sk_rstspl
        self.sk_rstsph = sk_rstsph
        self.sk_sgn    = sk_sgn

        self.rptlist = []
        self.skatzs2 = []
        self.skatqs2 = []

        self.itp = 0
        self.qsp = 0
        self.rstn = 0
        self.b_rstp = 0
        self.b_zsp  = 0
        self.b_bsp  = 0
        self.b_det  = 0
        self.s_rstp = 0
        self.s_zsp = 0
        self.s_bsp = 0
        self.s_det = 0

        self.bslist  = []
        self.rsllist = []

    def updaterpt(self, i):
        if len(self.sk_sgn)<1:
            return
        rpt = (0,0, None)
        #-----------------------记录当前sk相对当日rsl的情况，
        lstsgn = self.sk_sgn[-1]
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

        #------------------------------------
        if not lstsgn.rsp_zs2c:
            rsl = None
            atl = self.skatzs2[-1]
        else:
            bdh = max(lstsgn.rsp_zs2c, lstsgn.rsp_zs2a)
            bdl = min(lstsgn.rsp_zs2c, lstsgn.rsp_zs2a)
            if len(self.skatzs2)>0:
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
        #-----------------------------------
        if not lstsgn.rsp_qs2c:
            rsl = None
            atl = self.skatqs2[-1]
        else:
            bdh = max(lstsgn.rsp_qs2c, lstsgn.rsp_qs2a)
            bdl = min(lstsgn.rsp_qs2c, lstsgn.rsp_qs2a)
            if len(self.skatqs2)>0:
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
        # self.rsllist.append(rsl)

        self.itp = self.sk_itp[-1]
        if self.itp == 0:
            self.qsp = self.sk_close[i]
        elif self.sk_itp[-1] * self.sk_itp[-2] <=0:
            self.qsp = self.sk_close[i]

        self.disrst = self.sk_disrst[-1]
        self.rstn = self.sk_rstn[-1]
        if self.itp >0:
            self.b_rstp = max(self.sk_rstsph[-1], self.sk_rstspl[-1])
            self.b_zsp =  min(self.sk_zsh[-1], self.sk_zsl[-1])
            self.b_bsp = max(self.sk_bsh[-1], self.sk_bsl[-1])
            self.b_det = self.sk_atr[i] * self.sk_close[i] * 0.05
        elif self.itp <0:
            self.s_rstp = min(self.sk_rstsph[-1], self.sk_rstspl[-1])
            self.s_zsp = max(self.sk_zsh[-1], self.sk_zsl[-1])
            self.s_bsp = min(self.sk_bsh[-1], self.sk_bsl[-1])
            self.s_det = self.sk_atr[i] * self.sk_close[i] * 0.05

        bsfact = self.sgn_bs(i)

        self.bslist.append(bsfact)
        rpt = (zsrpt, qsrpt, bsfact)
        self.rptlist.append(rpt)
        return
    # ----------------------生成买卖决策信号,向交易模块提供交易要素：多空方向、委托价格-------------
    def sgn_bs(self, i):
        # print 'sgn_bs'
        fact = (self.itp, self.qsp, self.disrst, self.rstn, self.b_rstp, self.b_zsp, self.b_bsp, self.b_det, self.s_rstp, self.s_zsp, self.s_bsp, self.s_det)
        return fact

# ---------------------------------------------------------------------------
class Stepchain(object):
    def __init__(self, stpdir, stpi, piockl, revls):   # piockl 和 revls 都是skcl单链 来自 sk_ckl[i] = (ckli, cksdh, cksdl, cklhp, ckllp, cklbi)
        self.stpdir = stpdir
        self.stpis    = [stpi]  #步进起始点
        self.revckls  = [revls]  #逆势链
        self.piockl   = piockl
        self.farrevl = None      # 逆势链实体的最远段
    def updatestep(self, i, crtckl):
        if not crtckl:
            return
        if self.stpdir * crtckl[0] < 0:  #逆势链
            if self.stpdir>0:
                if not self.farrevl:
                    self.farrevl = crtckl
                elif self.farrevl[2] >=  crtckl[2]:
                    self.farrevl = crtckl
            else:
                if not self.farrevl:
                    self.farrevl = crtckl
                elif self.farrevl[1] <=  crtckl[1]:
                    self.farrevl = crtckl
        else:
            if self.stpdir>0:
                if crtckl[1] >= self.piockl[1]:  # 更新前沿
                    self.piockl = crtckl
                if not self.farrevl:
                    return
                if crtckl[1] > self.farrevl[3]: # 新上升sk链实体突破最远逆势链高点，产生新的上升步进点
                    self.stpis.append(i)
                    self.revckls.append(self.farrevl)
                    self.farrevl = None
            elif self.stpdir < 0:
                if crtckl[2] <= self.piockl[2]: # 更新前沿
                    self.piockl = crtckl
                if not self.farrevl:
                    return
                if crtckl[2] < self.farrevl[4]:  # 新下降sk链实体突破最远逆势链低点，产生新的下跌步进点
                    self.stpis.append(i)
                    self.revckls.append(self.farrevl)
                    self.farrevl = None

#---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
class Rstsa(object):
    def __init__(self, sk_open, sk_high, sk_low, sk_close, sk_atr, rstdir, trpi, rstbi):
        self.sk_open = sk_open
        self.sk_high = sk_high
        self.sk_low = sk_low
        self.sk_close = sk_close
        self.sk_atr = sk_atr

        self.rstdir = rstdir
        self.trpi = trpi    # 转折起点 极值点
        self.rstbi = rstbi  # 转折确认点
        self.rsti = None  # 回阻ski
        self.rstp = None  # 回阻skp
        self.mexi = None
        self.mexp = None

    def getrst(self):
        msdki = self.trpi
        msdk = self.rstdir * (self.sk_close[msdki] - self.sk_open[msdki])
        for ski in range(self.trpi+1, self.rstbi+1):
            sdk = self.rstdir * (self.sk_close[ski] - self.sk_open[ski])
            if msdk < sdk:
                msdki = ski
                msdk = sdk
        self.rsti = msdki
        self.rstp = self.sk_open[self.rsti]

    def uptmex(self, ski):
        sdk = self.rstdir * (self.sk_close[ski] - self.sk_open[ski])
        if not self.mexi:
            msdk = self.rstdir * (self.sk_close[self.rsti] - self.sk_open[self.rsti])
        else:
            msdk = self.rstdir * (self.sk_close[self.mexi] - self.sk_open[self.mexi])
        if msdk < sdk:
            self.mexi = ski
            self.mexp = self.sk_open[ski]
        else:
            if not self.mexi:
                self.mexi = self.rsti
                self.mexp = self.rstp



class Grst_Factor(object):
    def __init__(self, var, period, skdata, sdt=True, fid= 'ma'):
        self.quotes = skdata.loc[:]
        if not sdt:
            Column0 = self.quotes.columns[0]
            if '_' not in Column0:
                Period = 'd'
            else:
                Period = Column0.split('_')[1]

            self.quotes = self.quotes.rename( columns={'Open_' + Period: 'open', 'High_' + Period: 'high', 'Low_' + Period: 'low','Close_' + Period: 'close', 'Volume_' + Period: 'volume'})
            if Period=='d':
                #self.quotes = self.quotes.rename(columns={'Open': 'open', 'High': 'high', 'Low': 'low', 'Close': 'close','Volume':'volume'})
                self.quotes['time'] = skdata.index
                # for dtm in skdata.index:
                #     print type(dtm)
                xdate = [datetime.strptime(i, '%Y_%m_%d') for i in self.quotes['time']]
                self.quotes['time'] = xdate
            else:
                self.quotes['time'] = skdata.index
                xdate = [datetime.strptime(i, '%Y-%m-%d %H:%M:%S') for i in self.quotes['time']]
                self.quotes['time'] = xdate
        else:
            # if period=='d':
            #     xdate = [datetime.strptime(dtm, "%Y-%m-%d") for dtm in self.quotes.index]
            # else:
            #     xdate = [datetime.strptime(dtm, '%Y-%m-%d %H:%M:%S') for dtm in self.quotes.index]
            # self.quotes['time'] = xdate
            self.quotes['time'] = self.quotes.index
        Dat_bar  =self.quotes.loc[:]
        '''
        Dat_open = self.quotes.loc[:,'open']
        Dat_high = self.quotes.loc[:, 'high']
        Dat_low = self.quotes.loc[:, 'low']
        Dat_close = self.quotes.loc[:, 'close']
        
        '''

        Dat_bar['TR1'] = Dat_bar['high']-Dat_bar['low']
        Dat_bar['TR2'] = abs(Dat_bar['high'] - Dat_bar['close'].shift(1))
        Dat_bar['TR3'] = abs(Dat_bar['low'] - Dat_bar['close'].shift(1))
        TR = Dat_bar.loc[:,['TR1', 'TR2','TR3']].max(axis=1)
        ATR= TR.rolling(14).mean()/Dat_bar['close'].shift(1)
        self.quotes['ATR']=ATR
        Ma = Dat_bar['close'].rolling(10).mean()
        Boll_mid = Dat_bar['close'].rolling(20).mean()
        Std = Dat_bar['close'].rolling(20).std()
        Boll_upl = Boll_mid + 2 * Std
        Boll_dwl = Boll_mid - 2 * Std
        self.quotes['ma'] = Ma
        self.quotes['mid'] = Boll_mid
        self.quotes['upl'] = Boll_upl
        self.quotes['dwl'] = Boll_dwl

        self.extqts = []

        self.sads = OrderedDict()
        self.rstdir = 0
        self.crtsad = None
        self.tepsad = None
        self.sadlines = OrderedDict()
        self.dwrstsas = OrderedDict()
        self.uprstsas = OrderedDict()

        self.tops = []
        self.botms = []
        self.boti = 0
        self.topi = 0
        self.reslines = OrderedDict()
        self.suplines = OrderedDict()
        self.crtbbl = None
        self.crtttl = None
        self.prebbl = None
        self.prettl = None


        self.Var = var
        self.TS_Config = None
        self.TSBT = None
        self.fid = fid
    # ----------------------
    def addsgn(self, sgndat, sgnids, Tn='d', fillna = True):
        for isgn in  sgnids:
            if isgn in sgndat.columns:
                self.extqts.append(isgn)
                if 'ak_'+ isgn in sgndat.columns:
                    self.extqts.append('ak_'+ isgn)

        if len(self.extqts)==0:
            return
        toaddf = sgndat.loc[:,self.extqts]
        newindex = []
        for dtm in toaddf.index:
            if ' ' not in dtm:
                newindex.append(dtm.replace('_','-') + ' 16:00:00')
            else:
                newindex.append(''.join([dtm.split(' ')[0],'16:00:00']))

        sindex = self.quotes.index
        reindex = []
        for dtm in newindex:
            redtm = sindex[sindex <= dtm][-1]
            reindex.append(redtm)
        toaddf.index = reindex
        coldic = {isgn: isgn + '_' + Tn for isgn in self.extqts }
        toaddf.rename(columns=coldic, inplace = True)
        self.extqts= toaddf.columns.tolist()
        self.quotes = pd.concat([self.quotes, toaddf], axis=1, join_axes=[self.quotes.index])
        if fillna:
            self.quotes.fillna(method='pad', inplace = True)

    def renamequote(self, oldna, newna):
        if oldna in self.quotes.columns:
            self.quotes.rename(columns={oldna: newna}, inplace=True)

    def setmacn(self, swt='15:00:00'):
        self.quotes['dkcn'] = np.nan
        kcn = 1
        for idtm in self.quotes.index[::-1]:
            # print idtm
            # if idtm.split(' ')[1] ==swt:
            if not np.isnan(self.quotes.loc[idtm, 'sudc']):
                self.quotes.loc[idtm,'dkcn'] = kcn
                kcn = 1
            else:
                kcn += 1
        self.quotes.loc[:, 'dkcn'].fillna(method='pad', inplace=True)
        # print 'ok'





    # ----------------------
    def new_supline(self, fidna, bdpt, edpt, sk_open, sk_high, sk_low, sk_close, sk_volume, sk_time, sk_atr, sk_ckl, i, upski = None):
        # --calc new new_supline
        if bdpt.skp > edpt.skp:
            return
        newbbl = gettrpline(fidna, bdpt, edpt, 'bbl', sk_open, sk_high, sk_low, sk_close, sk_atr, sk_time, sk_ckl, i, upski)
        if newbbl:
            newbbl.initsklsta(sk_open, sk_high, sk_low, sk_close, sk_atr, sk_ckl, i)
            return newbbl
            # self.suplines[newbbl.socna]=newbbl
            # self.prebbl = self.crtbbl
            # self.crtbbl = newbbl
        return None

    def new_resline(self, fidna, bdpt, edpt, sk_open, sk_high, sk_low, sk_close, sk_volume, sk_time, sk_atr, sk_ckl, i, upski = None):
        # --calc new new_resline
        if bdpt.skp < edpt.skp:
            return
        newttl = gettrpline(fidna, bdpt, edpt, 'ttl', sk_open, sk_high, sk_low, sk_close, sk_atr, sk_time, sk_ckl, i, upski)
        if newttl:
            newttl.initsklsta(sk_open, sk_high, sk_low, sk_close, sk_atr, sk_ckl, i)
            return newttl
            # self.reslines[newttl.socna]=newttl
            # self.prettl = self.crtttl
            # self.crtttl = newttl
        return None

    def new_supline2(self, fidna, sk_open, sk_high, sk_low, sk_close, sk_volume, sk_time, sk_atr, sk_ckl, i, upski = None):
        # --calc new new_supline2
        mbdi = 5
        wrsk = 1.5
        tdls = {}
        tdlfs = {}
        atr = sk_atr[i]
        trpbdis = []
        fei = i
        botms = self.botms
        boti = self.boti
        botn= len(botms)
        if boti>= botn-1:
            return
        mxi = boti
        mxp = botms[mxi].skp
        for ix in range(boti + 1, botn - 1):
            if botms[ix].skp <= mxp:
                mxi = ix
                mxp = botms[ix].skp
        for ix in range(mxi, botn-1):
            for kx in range(ix+1, botn):
                if botms[ix].skp < botms[kx].skp:
                    trpbdis.append((botms[ix].ski , botms[kx].ski))

        for trp in trpbdis:
            bi = trp[0]
            ei = trp[1]
            if ei - bi < mbdi:
                continue
            tdlna =  'bbl' + '_'+ str(bi) + '_' + str(ei)
            if tdlna in tdls:
                continue
            #----------------------------------
            # trpb = Extrp(bi, sk_low[bi], -1)
            # trpd = Extrp(ei, sk_low[ei], -1)
            # newtbl = Trpline(trpb, trpd, atr, 'bbl')
            # newtbl.fbi = bi
            #---------------------------------
            fbi = ei
            skp = min(sk_open[ei], sk_close[ei])
            lkp = min(sk_open[ei - 1], sk_close[ei - 1])
            rkp = min(sk_open[ei + 1], sk_close[ei + 1])
            sdpt = getsdi(bi, sk_low[bi], ei, skp, lkp, rkp, 1)
            if not sdpt:
                continue
            mri = sdpt[0]
            mrp = sdpt[1]
            newtbl = getmrline2(tdlna, bi, sk_low[bi], mri, mrp, fbi, sk_time, atr, i, upski)
            if not newtbl:
                continue
            # -----------------------------------
            newtbl.fak()
            newtbl.frsk(sk_open, sk_high, sk_low, sk_close, atr, bi, fei)  #   fbi, fei
            newtbl.sfs = newtbl.srk + wrsk * newtbl.srsk
            tdls[tdlna] = newtbl
            tdlfs[tdlna] = newtbl.sfs
        if tdlfs:
            # sortfs = sorted(tdlfs.items(), key=lambda tdlfs: tdlfs[1], reverse=True)
            # print sortfs[:5]
            maxna = max(tdlfs, key=tdlfs.get)
            newtbl = tdls[maxna]
            if newtbl.sfs > -50:
                newtbl.socna = 'bbl' + '_' + str(i)
                newtbl.fsocna = fidna + '_' + newtbl.socna
                # self.boti = mxi + 1
                newtbl.mxi = mxi
                #--------------------------------------------------------------
                # self.ocover = 0        self.hlover = 0    self.pdreach = 0
                print str(sk_time[i])[
                      :10], newtbl.socna, ' rk:', '%.2f' % newtbl.rk, 'srk:', '%.2f' % newtbl.srk, 'srsk:', '%.2f' % newtbl.srsk, 'sfs:', '%.2f' % newtbl.sfs, \
                    'ocovr:', newtbl.ocover, 'hlovr:', newtbl.hlover, 'pdrch:', newtbl.pdreach  # 'newtbl:' , maxna,
                newtbl.initsklsta(sk_open, sk_high, sk_low, sk_close, sk_atr, sk_ckl, i)
                return newtbl
                # self.suplines[newtbl.socna] = {'mdl': newtbl, 'mir': OrderedDict(), 'upl': OrderedDict(), 'dwl': OrderedDict()}
                # self.prebbl = self.crtbbl
                # self.crtbbl = newtbl
        return None

    def new_resline2(self, fidna, sk_open, sk_high, sk_low, sk_close, sk_volume, sk_time, sk_atr, sk_ckl, i, upski = None):
        # --calc new new_supline2
        mbdi = 5
        wrsk = 1.5
        tdls = {}
        tdlfs = {}
        atr = sk_atr[i]
        trpbdis = []
        fei = i
        tops = self.tops
        topi = self.topi
        topn= len(tops)
        if topi>= topn-1:
            return
        mxi = topi
        mxp = tops[mxi].skp
        for ix in range(topi+1, topn - 1):
            if tops[ix].skp>= mxp:
                mxi = ix
                mxp = tops[ix].skp

        for ix in range(mxi, topn-1):
            for kx in range(ix+1, topn):
                if tops[ix].skp > tops[kx].skp:
                    trpbdis.append((tops[ix].ski , tops[kx].ski))

        for trp in trpbdis:
            bi = trp[0]
            ei = trp[1]
            if ei - bi < mbdi:
                continue
            tdlna = 'ttl' + '_' + str(bi) + '_' + str(ei)
            if tdlna in tdls:
                continue
            # -----------------------------------------
            # trpb = Extrp(bi, sk_high[bi], 1)
            # trpd = Extrp(ei, sk_high[ei], 1)
            # newtbl = Trpline(trpb, trpd, atr, 'ttl')
            # newtbl.fbi = bi
            # -----------------------------------------
            fbi = ei
            skp = max(sk_open[ei], sk_close[ei])
            lkp = max(sk_open[ei - 1], sk_close[ei - 1])
            rkp = max(sk_open[ei + 1], sk_close[ei + 1])
            sdpt = getsdi(bi, sk_high[bi], ei, skp, lkp, rkp, -1)
            if not sdpt:
                continue
            mri = sdpt[0]
            mrp = sdpt[1]
            newtbl = getmrline2(tdlna, bi, sk_high[bi], mri, mrp, fbi, sk_time, atr, i, upski)
            if not newtbl:
                continue
            # -----------------------------------
            newtbl.fak()
            newtbl.frsk(sk_open, sk_high, sk_low, sk_close, atr, bi, fei)  #   fbi, fei
            newtbl.sfs = newtbl.srk + wrsk * newtbl.srsk
            tdls[tdlna] = newtbl
            tdlfs[tdlna] = newtbl.sfs
        if tdlfs:
            # sortfs = sorted(tdlfs.items(), key=lambda tdlfs: tdlfs[1], reverse=True)
            # print sortfs[:5]
            maxna = max(tdlfs, key=tdlfs.get)
            newtbl = tdls[maxna]
            if newtbl.sfs > -50:
                newtbl.socna = 'ttl' + '_' + str(i)
                newtbl.fsocna = fidna + '_' + newtbl.socna
                # self.topi = mxi + 1
                newtbl.mxi = mxi
                #--------------------------------------------------------------
                # self.ocover = 0        self.hlover = 0    self.pdreach = 0
                print str(sk_time[i])[
                      :10], newtbl.socna, ' rk:', '%.2f' % newtbl.rk, 'srk:', '%.2f' % newtbl.srk, 'srsk:', '%.2f' % newtbl.srsk, 'sfs:', '%.2f' % newtbl.sfs, \
                    'ocovr:', newtbl.ocover, 'hlovr:', newtbl.hlover, 'pdrch:', newtbl.pdreach  # 'newtbl:' , maxna,
                newtbl.initsklsta(sk_open, sk_high, sk_low, sk_close, sk_atr, sk_ckl, i)
                return newtbl
                # self.reslines[newtbl.socna] = {'mdl': newtbl, 'mir': OrderedDict(), 'upl': OrderedDict(), 'dwl': OrderedDict()}
                # self.prettl = self.crtttl
                # self.crtttl = newtbl
        return None

    def new_supline3(self, fidna, sk_open, sk_high, sk_low, sk_close, sk_volume, sk_time, sk_atr, sk_ckl, i, upski = None):
        # --calc new new_supline3
        mbdi = 5
        wrsk = 1.5
        tdls = {}
        tdlfs = {}
        atr = sk_atr[i]
        fei = i
        botms = self.botms
        boti = self.boti
        botn= len(botms)
        if boti>= botn-1:
            return
        mxi = boti
        mxp = botms[mxi].skp
        for ix in range(boti + 1, botn):
            if botms[ix].skp <= mxp:
                mxi = ix
                mxp = botms[ix].skp
        if mxi>= botn-1:
            return

        bi = botms[mxi].ski
        ei = fei
        peaks = []
        for ix in range(bi, ei):
            if sk_low[ix]< sk_low[ix+1] and sk_low[ix]<= sk_low[ix-1]:
                peaks.append(ix)

        trpbdis = list(combinations(peaks, 2))

        for trp in trpbdis:
            bi = trp[0]
            ei = trp[1]
            if ei - bi < mbdi or sk_low[bi] >= sk_low[ei]:
                continue
            trpb = Extrp(bi, sk_low[bi], -1)
            trpd = Extrp(ei, sk_low[ei], -1)
            tdlna =  'bbl' + '_'+ str(bi) + '_' + str(ei)

            if tdlna in tdls:
                continue
            newtbl = Trpline(trpb, trpd, atr, 'bbl')
            newtbl.fbi = botms[mxi].ski
            newtbl.et_ini = upski if upski else i
            newtbl.fak()
            newtbl.frsk(sk_open, sk_high, sk_low, sk_close, atr, bi, fei)  #   fbi, fei
            newtbl.sfs = newtbl.srk + wrsk * newtbl.srsk
            tdls[tdlna] = newtbl
            tdlfs[tdlna] = newtbl.sfs
        if tdlfs:
            # sortfs = sorted(tdlfs.items(), key=lambda tdlfs: tdlfs[1], reverse=True)
            # print sortfs[:5]
            maxna = max(tdlfs, key=tdlfs.get)
            newtbl = tdls[maxna]
            if newtbl.sfs > 0:
                newtbl.socna = 'bbl' + '_' + str(i)
                newtbl.fsocna = fidna + '_' + newtbl.socna
                # self.boti = mxi + 1
                newtbl.mxi = mxi
                #--------------------------------------------------------------
                # self.ocover = 0        self.hlover = 0    self.pdreach = 0
                print str(sk_time[i])[
                      :10], newtbl.socna, ' rk:', '%.2f' % newtbl.rk, 'srk:', '%.2f' % newtbl.srk, 'srsk:', '%.2f' % newtbl.srsk, 'sfs:', '%.2f' % newtbl.sfs, \
                    'ocovr:', newtbl.ocover, 'hlovr:', newtbl.hlover, 'pdrch:', newtbl.pdreach  # 'newtbl:' , maxna,
                newtbl.initsklsta(sk_open, sk_high, sk_low, sk_close, sk_atr, sk_ckl, i)
                return newtbl
                # self.suplines[newtbl.socna] = {'mdl': newtbl, 'mir': OrderedDict(), 'upl': OrderedDict(), 'dwl': OrderedDict()}
                # self.prebbl = self.crtbbl
                # self.crtbbl = newtbl
        return None

    def new_resline3(self,  fidna, sk_open, sk_high, sk_low, sk_close, sk_volume, sk_time, sk_atr, sk_ckl, i, upski = None):
        # --calc new new_supline3
        mbdi = 5
        wrsk = 1.5
        tdls = {}
        tdlfs = {}
        atr = sk_atr[i]
        fei = i
        tops = self.tops
        topi = self.topi
        topn= len(tops)
        if topi>= topn-1:
            return

        mxi = topi
        mxp = tops[mxi].skp
        for ix in range(topi+1, topn):
            if tops[ix].skp>= mxp:
                mxi = ix
                mxp = tops[ix].skp
        if mxi>= topn-1:
            return
        bi = tops[mxi].ski
        ei = fei
        peaks = []
        for ix in range(bi, ei):
            if sk_high[ix] > sk_high[ix + 1] and sk_high[ix] >= sk_high[ix - 1]:
                peaks.append(ix)

        trpbdis = list(combinations(peaks, 2))

        for trp in trpbdis:
            bi = trp[0]
            ei = trp[1]
            if ei - bi < mbdi or sk_high[bi] <= sk_high[ei]:
                continue
            trpb = Extrp(bi, sk_high[bi], 1)
            trpd = Extrp(ei, sk_high[ei], 1)
            tdlna =  'ttl' + '_'+ str(bi) + '_' + str(ei)
            if tdlna in tdls:
                continue
            newtbl = Trpline(trpb, trpd, atr, 'ttl')
            newtbl.fbi = tops[mxi].ski
            newtbl.et_ini = upski if upski else i
            newtbl.fak()
            newtbl.frsk(sk_open, sk_high, sk_low, sk_close, atr, bi, fei)  #   fbi, fei
            newtbl.sfs = newtbl.srk + wrsk * newtbl.srsk
            tdls[tdlna] = newtbl
            tdlfs[tdlna] = newtbl.sfs
        if tdlfs:
            # sortfs = sorted(tdlfs.items(), key=lambda tdlfs: tdlfs[1], reverse=True)
            # print sortfs[:5]
            maxna = max(tdlfs, key=tdlfs.get)
            newtbl = tdls[maxna]
            if newtbl.sfs > 0:
                newtbl.socna = 'ttl' + '_' + str(i)
                newtbl.fsocna = fidna + '_' + newtbl.socna
                # self.topi = mxi + 1
                newtbl.mxi = mxi
                #--------------------------------------------------------------
                # self.ocover = 0        self.hlover = 0    self.pdreach = 0
                print str(sk_time[i])[
                      :10], newtbl.socna, ' rk:', '%.2f' % newtbl.rk, 'srk:', '%.2f' % newtbl.srk, 'srsk:', '%.2f' % newtbl.srsk, 'sfs:', '%.2f' % newtbl.sfs, \
                    'ocovr:', newtbl.ocover, 'hlovr:', newtbl.hlover, 'pdrch:', newtbl.pdreach  # 'newtbl:' , maxna,
                newtbl.initsklsta(sk_open, sk_high, sk_low, sk_close, sk_atr, sk_ckl, i)
                return newtbl
                # self.reslines[newtbl.socna] = {'mdl': newtbl, 'mir': OrderedDict(), 'upl': OrderedDict(), 'dwl': OrderedDict()}
                # self.prettl = self.crtttl
                # self.crtttl = newtbl
        return None

    def idxof_nsckls(self, nsckls, ski):
        if len(nsckls) <= 0: return -1
        for idx in range(0, len(nsckls)):
            if ski >= nsckls[idx][1][0][0] and ski <= nsckls[idx][1][-1][1]:
                return idx
        return -1

    # -------------------------------------
    def uptsads(self, sk_open, sk_high, sk_low, sk_close, sk_atr, sk_ckl, sk_disrst, ski):
        atr = sk_close[ski] * sk_atr[ski]
        det = atr * 0.05
        mdet = 5 * atr
        ldet = 0.1 * atr
        mcn = 4
        ldp = 1.5
        rtp = 0.3

        if self.rstdir<0:
            if not self.tepsad:
                if sk_low[ski - 1] -det <= sk_disrst[ski] <= sk_high[ski]:
                    self.tepsad = Sadl(1, bi=ski, bap= sk_disrst[ski])
                    self.tepsad.sdp += max(sk_close[ski] - self.tepsad.bap, 0.0)
                    if sk_low[ski] >= self.tepsad.bap + ldet:
                        self.tepsad.cn += 1
                    self.tepsad.upti = ski
            else:
                if self.tepsad.dwup > 0:
                    if sk_low[ski] >= self.tepsad.bap + ldet:
                        self.tepsad.cn += 1
                    if not self.tepsad.mp or self.tepsad.mp <= sk_high[ski]:
                        self.tepsad.mp = sk_high[ski]
                        self.tepsad.mi = ski
                    dep = max(sk_high[ski] - self.tepsad.bap, 0.0)
                    rep = max(sk_low[ski] - self.tepsad.bap, 0.0)
                    if not self.tepsad.mdp or dep >= self.tepsad.mdp:
                        self.tepsad.mdi = ski
                        self.tepsad.mdp = dep
                        self.tepsad.mret=1
                    self.tepsad.sdp += max(sk_close[ski] - self.tepsad.bap, 0.0)

                    if self.crtsad and self.crtsad.ei:
                        if rep < self.crtsad.mdp * self.crtsad.mret:
                            if self.crtsad.mdp < self.tepsad.mdp:
                                self.crtsad.mdp = self.tepsad.mdp
                                self.crtsad.mdi = self.tepsad.mdi
                            self.crtsad.ei = ski
                            self.crtsad.sdp += self.tepsad.sdp
                            self.crtsad.mret = rep / self.crtsad.mdp
                            self.crtsad.cn += self.tepsad.cn
                            self.crtsad.upti = ski
                            if not self.crtsad.mp or self.crtsad.mp <= self.tepsad.mp:
                                self.crtsad.mp = self.tepsad.mp
                                self.crtsad.mi = self.tepsad.mi
                                self.crtsad.chg = 1

                            if self.tepsad.bap < sk_high[ski]:
                                self.tepsad = Sadl(1, bi=ski, bap=sk_disrst[ski])
                                self.tepsad.sdp += max(sk_close[ski] - self.tepsad.bap, 0.0)
                            else:
                                self.tepsad = None

                    if self.tepsad and ((self.tepsad.cn >= mcn and self.tepsad.sdp >= 3 * atr) or ( self.tepsad.cn>=3 and self.tepsad.sdp >= 3 * atr )) and self.tepsad.mdp >= atr * ldp:
                        self.crtsad = self.tepsad
                        self.sads.values()[-1].append(self.crtsad)
                        self.tepsad = None
                    if self.tepsad and sk_low[ski] <= self.tepsad.bap:
                        if self.tepsad.cn < mcn:
                            # self.tepsad = None
                            self.tepsad = Sadl(1, bi=ski, bap=sk_disrst[ski])
                            self.tepsad.sdp += max(sk_close[ski] - self.tepsad.bap, 0.0)
            if self.crtsad and self.crtsad.upti < ski:
                if not self.crtsad.ei:
                    if not self.crtsad.mp or self.crtsad.mp <= sk_high[ski]:
                        self.crtsad.mp = sk_high[ski]
                        self.crtsad.mi = ski
                    if sk_low[ski] >= self.crtsad.bap + ldet:
                        self.crtsad.cn += 1
                    dep = max(sk_high[ski] - self.crtsad.bap, 0.0)
                    rep = max(sk_low[ski] - self.crtsad.bap, 0.0)
                    if dep >= self.crtsad.mdp:
                        self.crtsad.mdi = ski
                        self.crtsad.mdp = dep
                        self.crtsad.mret = 1
                    self.crtsad.sdp += max(sk_close[ski] - self.crtsad.bap, 0.0)
                    if self.crtsad.mdi == ski:
                        mret = 1
                    else:
                        mret = rep / self.crtsad.mdp
                    if self.crtsad.mret > mret:
                        self.crtsad.mret = mret
                    if self.crtsad.mret <= rtp:
                        self.crtsad.ei = ski
                        if sk_disrst[ski] < sk_high[ski]:
                            self.tepsad = Sadl(1, bi=ski, bap= sk_disrst[ski])
                            self.tepsad.sdp += max(sk_close[ski] - self.tepsad.bap, 0.0)
                        else:
                            self.tepsad = None
                    self.crtsad.upti = ski
            if self.crtsad and self.crtsad.ei and (not self.crtsad.rsti or self.crtsad.chg > 0):
                if not self.crtsad.rsti:
                    self.crtsad.rsti = ski
                crtrstna = self.dwrstsas.keys()[-1]
                rstna = crtrstna + '_' + str(len(self.sads)-1)
                nrstsa = Rstsa(sk_open, sk_high, sk_low, sk_close, sk_atr, self.rstdir, self.crtsad.mi, self.crtsad.ei)
                nrstsa.getrst()
                self.dwrstsas[crtrstna][rstna] = nrstsa

        elif self.rstdir > 0:
            if not self.tepsad:
                if sk_high[ski - 1] + det >= sk_disrst[ski] >= sk_low[ski]:
                    self.tepsad = Sadl(-1, bi=ski, bap=sk_disrst[ski])
                    self.tepsad.sdp += min(sk_close[ski] - self.tepsad.bap, 0.0)
                    if sk_high[ski] <= self.tepsad.bap - ldet:
                        self.tepsad.cn += 1
                    self.tepsad.upti = ski
            else:
                if self.tepsad.dwup < 0:
                    if sk_high[ski] <= self.tepsad.bap - ldet:
                        self.tepsad.cn += 1
                    if not self.tepsad.mp or self.tepsad.mp >= sk_low[ski]:
                        self.tepsad.mp = sk_low[ski]
                        self.tepsad.mi = ski
                    dep = min(sk_low[ski] - self.tepsad.bap, 0.0)
                    rep = min(sk_high[ski] - self.tepsad.bap, 0.0)
                    if not self.tepsad.mdp or dep <= self.tepsad.mdp:
                        self.tepsad.mdi = ski
                        self.tepsad.mdp = dep
                        self.tepsad.mret= 1
                    self.tepsad.sdp += min(sk_close[ski] - self.tepsad.bap, 0.0)
                    if self.crtsad and self.crtsad.ei:
                        if rep > self.crtsad.mdp * self.crtsad.mret:
                            if self.crtsad.mdp > self.tepsad.mdp:
                                self.crtsad.mdp = self.tepsad.mdp
                                self.crtsad.mdi = self.tepsad.mdi
                            self.crtsad.ei = ski
                            self.crtsad.sdp += self.tepsad.sdp
                            self.crtsad.mret = rep / self.crtsad.mdp
                            self.crtsad.cn += self.tepsad.cn
                            self.crtsad.upti = ski
                            if not self.crtsad.mp or self.crtsad.mp >= self.tepsad.mp:
                                self.crtsad.mp = self.tepsad.mp
                                self.crtsad.mi = self.tepsad.mi
                                self.crtsad.chg = 1

                            if self.tepsad.bap > sk_low[ski]:
                                self.tepsad = Sadl(-1, bi=ski, bap=sk_disrst[ski])
                                self.tepsad.sdp += min(sk_close[ski] - self.tepsad.bap, 0.0)
                            else:
                                self.tepsad = None

                    if self.tepsad and ((self.tepsad.cn >= mcn and self.tepsad.sdp <= -3 * atr ) or ( self.tepsad.cn>=3 and self.tepsad.sdp <= -3 * atr )) and self.tepsad.mdp <= -atr * ldp:
                        self.crtsad = self.tepsad
                        self.sads.values()[-1].append(self.crtsad)
                        self.tepsad = None
                    if self.tepsad and sk_high[ski] >= self.tepsad.bap:
                        if self.tepsad.cn < mcn:
                            # self.tepsad = None
                            self.tepsad = Sadl(-1, bi=ski, bap=sk_disrst[ski])
                            self.tepsad.sdp += min(sk_close[ski] - self.tepsad.bap, 0.0)
            if self.crtsad and self.crtsad.upti < ski:
                if not self.crtsad.ei:
                    if not self.crtsad.mp or self.crtsad.mp >= sk_low[ski]:
                        self.crtsad.mp = sk_low[ski]
                        self.crtsad.mi = ski
                    if sk_high[ski] <= self.crtsad.bap - ldet:
                        self.crtsad.cn += 1
                    dep = min(sk_low[ski] - self.crtsad.bap, 0.0)
                    rep = min(sk_high[ski] - self.crtsad.bap, 0.0)
                    if dep <= self.crtsad.mdp:
                        self.crtsad.mdi = ski
                        self.crtsad.mdp = dep
                    self.crtsad.sdp += min(sk_close[ski] - self.crtsad.bap, 0.0)
                    if self.crtsad.mdi == ski:
                        mret = 1
                    else:
                        mret = rep / self.crtsad.mdp
                    if self.crtsad.mret > mret:
                        self.crtsad.mret = mret
                    if self.crtsad.mret <= rtp:
                        self.crtsad.ei = ski
                        if sk_disrst[ski] > sk_low[ski]:
                            self.tepsad = Sadl(-1, bi=ski, bap=sk_disrst[ski])
                            self.tepsad.sdp += min(sk_close[ski] - self.tepsad.bap, 0.0)
                        else:
                            self.tepsad = None
                    self.crtsad.upti = ski
            if self.crtsad and self.crtsad.ei and (not self.crtsad.rsti or self.crtsad.chg > 0):
                if not self.crtsad.rsti:
                    self.crtsad.rsti = ski
                crtrstna = self.uprstsas.keys()[-1]
                rstna = crtrstna + '_' + str(len(self.sads)-1)
                nrstsa = Rstsa(sk_open, sk_high, sk_low, sk_close, sk_atr, self.rstdir, self.crtsad.mi, self.crtsad.ei)
                nrstsa.getrst()
                self.uprstsas[crtrstna][rstna] = nrstsa

    def updt_newbar(self):
        pass
    def grst_init(self, faset = {}, btest = False, btconfig = None, subrst = None, tdkopset = None):
        self.crtski = 0
        self.mosi = 0 # 记录Mrst的当前sk相对subrst最新sk偏移的数目
        skbgi = 20  # 起始点
        self.upix= [0] * (skbgi+1)  # 用于存储不同周期sk对应的bar索引
        self.sk_open = self.quotes['open'].values
        self.sk_high = self.quotes['high'].values
        self.sk_low = self.quotes['low'].values
        self.sk_close = self.quotes['close'].values
        self.sk_volume = self.quotes['volume'].values
        self.sk_time = self.quotes['time'].values
        self.sk_atr = self.quotes['ATR'].values
        if 'dkcn' in self.quotes.columns:
            self.dkcn = self.quotes['dkcn'].values
        else:
            self.dkcn = np.array([])
        if 'sudc' in self.quotes.columns:
            self.sk_sudc = self.quotes['sudc'].values
        else:
            self.sk_sudc = np.array([])
            # ----------------------------------------------
        self.faset = faset
        self.subrst = subrst
        self.sk_ckl = []  # 与ck同步，由元组（ckli,cksdh,cksdl）构成的队列，记录当前的sk链所包括的sk数目和实体部分的区间
        self.ckls = []  # 与ckl线段列表，由列表[cklbi,cklei,cklbp,cklep,cklsd]构成,记录线段的起点位置、终点位置、起点价格、终点价格、长度
        self.sk_cklsm = []  # 在sk序列框架下对ckls结构进行描述，指示当前的sk处于ckls结构中的水平 (ckltp, ickls)
        '''
           ckltp                             ickls
           1---处于wuckl weak up ckl         (ickls0,)
           2---处于suckl strong up ckl       (ickls0,)
           3---处于nuckl N-S up ckl          (ickls1,ickls2,ickls0)
           -1--处于wdckl weak down ckl       (ickls0,)
           -2--处于sdckl strong down ckl     (ickls0,)
           -3--处于ndckl N-S down ckl        (ickls1,ickls2,ickls0)

        '''
        self.nsckls = []  # 在ckls基础上，将相邻的可以聚合的n元聚合起来构成，由列表由[nsckltp，insckls]组成 insckls=[ickls0,ickls1,ickls2...]构成，当形成新的局部n元时更新
        self.nscklsedi = 0  # 最新段的nsckls处于ckls的第几号链上
        # -----------------------------------------------
        self.qspds = []  # 趋势前沿列表 每段由[qsprti,nscklidx,nscklitp,qspbi,qspei,qspbsdp,qspesdp,qspbp,qspep]组成，来自于nsckls的波段
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
        self.qsstpchain = []  # 与 qspds 同步
        self.qsrstp = []  # 多空转换点 收盘突破前沿，趋势方向转化 (sgn_rsti, sgn_rstp, sgn_rstdir) 突破位置，突破价格，突破方向：1-向上， -1 向下
        self.sk_qspds = []
        self.sk_qsrstp = []
        self.sk_rstn = []
        self.sk_rstspl = []
        self.sk_rstsph = []

        self.ctp = None
        self.cbp = None
        self.zsdir = None
        self.zsckl = None
        self.zsski = None
        self.zslp = None
        self.zshp = None
        self.bslp = None  # 回看低点
        self.bshp = None  # 回看高点
        self.bscp = None  # 回看远端
        self.bsbj = 0  # 步进标记

        # ********************************************************显示信号线
        self.sk_qsh = []
        self.sk_qsl = []
        self.sk_qswr = []  # 指示当前价格在趋势前沿中枢相对ATR得到宽度
        self.sk_rsl = []  # 指示当前价格在趋势前沿中枢中的价格水平
        self.sk_itp = []
        self.sk_disrst = []

        self.sk_sal = []   # sal
        self.sk_bbl = []   # rdl
        self.sk_ttl = []   # rdl
        self.sk_obbl = []  # mdl
        self.sk_ottl = []  # mdl

        self.ak_sal = []  # sal
        self.ak_bbl = []  # rdl
        self.ak_ttl = []  # rdl
        self.ak_obbl = []  # mdl
        self.ak_ottl = []  # mdl

        self.sk_alp1 = []
        self.sk_alp2 = []
        self.sk_alp3 = []
        self.sk_alp4 = []
        self.sk_alp5 = []
        self.sk_alp6 = []
        self.sk_dlp1 = []
        self.sk_dlp2 = []
        self.sk_dlp3 = []
        self.sk_dlp4 = []
        self.sk_dlp5 = []
        self.sk_dlp6 = []

        self.sk_zsh = []  # 转换中枢高点
        self.sk_zsl = []  # 转换中枢低点
        self.sk_bsh = []  # 转换回看高点
        self.sk_bsl = []  # 转换回看低点

        self.dwqsbands = Rsbandvec(rsdir=-1)
        self.upqsbands = Rsbandvec(rsdir=1)
        self.dwzsbands = Rsbandvec(rsdir=-1)
        self.upzsbands = Rsbandvec(rsdir=1)
        self.lstdwqsbd = None
        self.lstupqsbd = None
        self.lstdwzsbd = None
        self.lstupzsbd = None

        self.sk_zs1c = []
        self.sk_zs1a = []
        self.sk_zs2c = []
        self.sk_zs2a = []
        self.sk_qs1c = []
        self.sk_qs1a = []
        self.sk_qs2c = []
        self.sk_qs2a = []
        self.sk_zsrpt = []
        self.sk_qsrpt = []
        self.sk_sgn = []

        self.skatsel = Skatline(self.sk_open, self.sk_high, self.sk_low, self.sk_close, self.sk_atr, self.sk_ckl, self.dkcn)
        if self.subrst:
            self.skatetl = Skatline(self.sk_open, self.sk_high, self.sk_low, self.sk_close, self.sk_atr, self.sk_ckl, self.dkcn)
        else:
            self.skatetl = None

            # *******************************************************************
        # ----------------回测相关模块----------------------------------------
        if btest:
            self.tdkopset = tdkopset
            self.TS_Config = btconfig
            self.TSBT = TSBacktest(self.Var, self.quotes, self.sk_ckl, btconfig)
            self.TSBT.initbacktest()
            # self.intedsgn = Intsgnbs(self.rstdir, self.skatsel, self.skatetl, self.suplines, self.reslines, self.sadlines, self.uprstsas, self.dwrstsas, subrst=self.subrst)

        # ----------------------------------------------------------------------
        if self.sk_close.size <= skbgi:
            self.crtski = 0
            return
        for i in range(0, skbgi):
            self.sk_ckl.append(None)
            self.sk_cklsm.append(None)
            self.sk_qspds.append(None)
            self.sk_qsrstp.append(0)
            self.sk_rstn.append(0)
            self.sk_rstspl.append(self.sk_low[i])
            self.sk_rstsph.append(self.sk_high[i])

            self.sk_qsh.append(self.sk_high[i])
            self.sk_qsl.append(self.sk_low[i])
            self.sk_zsh.append(self.sk_high[i])
            self.sk_zsl.append(self.sk_low[i])
            self.sk_bsh.append(self.sk_high[i])
            self.sk_bsl.append(self.sk_low[i])

            self.sk_qswr.append(0)
            self.sk_rsl.append(0)
            self.sk_itp.append(0)

            self.sk_disrst.append(self.sk_low[i])
            self.sk_sal.append(self.sk_disrst[-1])
            self.sk_ttl.append(self.sk_disrst[-1])
            self.sk_bbl.append(self.sk_disrst[-1])
            self.sk_obbl.append(self.sk_disrst[-1])
            self.sk_ottl.append(self.sk_disrst[-1])
            self.ak_sal.append(0)
            self.ak_ttl.append(0)
            self.ak_bbl.append(0)
            self.ak_obbl.append(0)
            self.ak_ottl.append(0)

            self.sk_alp1.append(self.sk_disrst[-1])
            self.sk_alp2.append(self.sk_disrst[-1])
            self.sk_alp3.append(self.sk_disrst[-1])
            self.sk_alp4.append(self.sk_disrst[-1])
            self.sk_alp5.append(self.sk_disrst[-1])
            self.sk_alp6.append(self.sk_disrst[-1])
            self.sk_dlp1.append(self.sk_disrst[-1])
            self.sk_dlp2.append(self.sk_disrst[-1])
            self.sk_dlp3.append(self.sk_disrst[-1])
            self.sk_dlp4.append(self.sk_disrst[-1])
            self.sk_dlp5.append(self.sk_disrst[-1])
            self.sk_dlp6.append(self.sk_disrst[-1])
            # -----------------
            self.sk_zs1c.append(self.sk_close[i])
            self.sk_zs1a.append(self.sk_close[i])
            self.sk_zs2c.append(self.sk_close[i])
            self.sk_zs2a.append(self.sk_close[i])
            self.sk_qs1c.append(self.sk_close[i])
            self.sk_qs1a.append(self.sk_close[i])
            self.sk_qs2c.append(self.sk_close[i])
            self.sk_qs2a.append(self.sk_close[i])
            self.sk_zsrpt.append(0)
            self.sk_qsrpt.append(0)
            self.sk_sgn.append(None)
            # -----------------

        self.sk_qsrstp[0] = 2
        self.sk_qsrstp[1] = -2

        self.sk_qsh.append(self.sk_high[skbgi])
        self.sk_qsl.append(self.sk_low[skbgi])
        self.sk_zsh.append(self.sk_high[skbgi])
        self.sk_zsl.append(self.sk_low[skbgi])
        self.sk_bsh.append(self.sk_high[skbgi])
        self.sk_bsl.append(self.sk_low[skbgi])

        self.sk_qswr.append(0)
        self.sk_rsl.append(0)
        self.sk_itp.append(0)

        self.sk_disrst.append(self.sk_low[skbgi])
        self.sk_sal.append(self.sk_disrst[-1])
        self.sk_ttl.append(self.sk_disrst[-1])
        self.sk_bbl.append(self.sk_disrst[-1])
        self.sk_ottl.append(self.sk_disrst[-1])
        self.sk_obbl.append(self.sk_disrst[-1])
        self.ak_sal.append(0)
        self.ak_ttl.append(0)
        self.ak_bbl.append(0)
        self.ak_obbl.append(0)
        self.ak_ottl.append(0)

        self.sk_alp1.append(self.sk_disrst[-1])
        self.sk_alp2.append(self.sk_disrst[-1])
        self.sk_alp3.append(self.sk_disrst[-1])
        self.sk_alp4.append(self.sk_disrst[-1])
        self.sk_alp5.append(self.sk_disrst[-1])
        self.sk_alp6.append(self.sk_disrst[-1])
        self.sk_dlp1.append(self.sk_disrst[-1])
        self.sk_dlp2.append(self.sk_disrst[-1])
        self.sk_dlp3.append(self.sk_disrst[-1])
        self.sk_dlp4.append(self.sk_disrst[-1])
        self.sk_dlp5.append(self.sk_disrst[-1])
        self.sk_dlp6.append(self.sk_disrst[-1])

        self.sk_zs1c.append(self.sk_close[skbgi])
        self.sk_zs1a.append(self.sk_close[skbgi])
        self.sk_zs2c.append(self.sk_close[skbgi])
        self.sk_zs2a.append(self.sk_close[skbgi])
        self.sk_qs1c.append(self.sk_close[skbgi])
        self.sk_qs1a.append(self.sk_close[skbgi])
        self.sk_qs2c.append(self.sk_close[skbgi])
        self.sk_qs2a.append(self.sk_close[skbgi])
        self.sk_zsrpt.append(0)
        self.sk_qsrpt.append(0)
        self.sk_sgn.append(None)

        if self.sk_close[skbgi] >= self.sk_open[skbgi]:
            ckli = 1
            cksdh = self.sk_close[skbgi]
            cksdl = self.sk_open[skbgi]
            cklhp = self.sk_high[skbgi]
            ckllp = self.sk_low[skbgi]
        else:
            ckli = -1
            cksdl = self.sk_close[skbgi]
            cksdh = self.sk_open[skbgi]
            cklhp = self.sk_high[skbgi]
            ckllp = self.sk_low[skbgi]
        self.sk_ckl.append((ckli, cksdh, cksdl, cklhp, ckllp, skbgi))

        # self.ckls=[]   # 单纯K链列表，ckl线段列表，由列表[cklbi,cklei,cklbp,cklep,cklsd]构成,记录线段的起点、终点、长度
        cklbi = skbgi
        cklei = skbgi
        cklbp = self.sk_open[skbgi]
        cklep = self.sk_close[skbgi]
        cklsd = ckli * (cksdh - cksdl)
        self.ckls.append([cklbi, cklei, cklbp, cklep, cklsd])

        # self.sk_cklsm=[] #在sk序列框架下对ckls结构进行描述，指示当前的sk处于ckls结构中的水平 (ckltp, ickls),最近的3段ckls
        ckltp = ckli
        ickls0 = tuple(self.ckls[-1])
        ickls = (ickls0,)
        self.sk_cklsm.append((ckltp, ickls))
        # print(0,self.sk_close.index[0],(ckli, round(cksdh,decsn), round(cksdl,decsn)))
        self.sk_qspds.append([0, 0, 0, 0, 0, self.sk_open[skbgi], self.sk_close[skbgi], self.sk_open[skbgi], self.sk_close[skbgi]])
        self.sk_qsrstp.append(0)
        self.sk_rstn.append(0)
        self.sk_rstspl.append(self.sk_low[skbgi])
        self.sk_rstsph.append(self.sk_high[skbgi])
        self.crtski = skbgi
        # self.crtidtm  = pd.Timestamp((self.sk_time[self.crtski])).strftime('%Y-%m-%d %H:%M:%S')
        self.crtidtm  = self.sk_time[self.crtski]
        self.crtidate = self.crtidtm[:10]

    def cal_next(self, upidtm = None, upski = None):
        sk_ckdtpst = 0.05  # 0.05倍平均涨幅作为涨跌柱子的公差
        detsdc = -5  # strong下降链构成下降反转的链长 =detsdc*avgski
        detsuc = 5  # strong上升链构成上涨反转的链长 =detsuc*avgski
        nxti = self.crtski + 1
        if nxti > self.sk_close.size -1:
            return self.crtski

        for i in range(nxti, self.sk_close.size):
            if i==1085:
                print i
            # idtm = pd.Timestamp((self.sk_time[i])).strftime('%Y-%m-%d %H:%M:%S')
            idtm = self.sk_time[i]
            if upidtm and upidtm < idtm:
                break
            self.crtski = i
            self.crtidtm = idtm
            self.crtidate = self.crtidtm[:10]

            avgski = self.sk_atr[i - 1] * self.sk_close[i - 1]
            if self.sk_ckl[i - 1][0] > 0:
                if self.sk_close[i] >= self.sk_close[i - 1] - sk_ckdtpst * self.sk_atr[i - 1] * self.sk_close[i - 1]:  # self.sk_open[i] - sk_ckdtpst * self.sk_atr[i]:  #
                    ckli = self.sk_ckl[i - 1][0] + 1
                    cksdh = max(self.sk_ckl[i - 1][1], self.sk_close[i])
                    cksdl = self.sk_ckl[i - 1][2]
                    cklhp = max(self.sk_ckl[i - 1][3], self.sk_high[i])
                    ckllp = min(self.sk_ckl[i - 1][4], self.sk_low[i])
                    cklbi = self.sk_ckl[i - 1][5]
                    self.sk_ckl.append((ckli, cksdh, cksdl, cklhp, ckllp, cklbi))

                    # 更新 self.ckls
                    self.ckls[-1][1] += 1
                    self.ckls[-1][3] = cksdh
                    self.ckls[-1][4] = cksdh - cksdl
                else:
                    ckli = -1
                    cksdh = self.sk_ckl[i - 1][1]
                    cksdl = self.sk_close[i]
                    cklhp = max(self.sk_high[i], cksdh)
                    ckllp = self.sk_low[i]
                    self.sk_ckl.append((ckli, cksdh, cksdl, cklhp, ckllp, i))

                    # 更新 self.ckls
                    cklbi = i
                    cklei = i
                    cklbp = cksdh
                    cklep = cksdl
                    cklsd = cklep - cklbp
                    self.ckls.append([cklbi, cklei, cklbp, cklep, cklsd])

            else:
                if self.sk_close[i] <= self.sk_close[i - 1] + sk_ckdtpst * self.sk_atr[i - 1] * self.sk_close[i - 1]:  # self.sk_open[i] + sk_ckdtpst * self.sk_atr[i]:  #
                    ckli = self.sk_ckl[i - 1][0] - 1
                    cksdl = min(self.sk_ckl[i - 1][2], self.sk_close[i])
                    cksdh = self.sk_ckl[i - 1][1]
                    cklhp = max(self.sk_ckl[i - 1][3], self.sk_high[i])
                    ckllp = min(self.sk_ckl[i - 1][4], self.sk_low[i])
                    cklbi = self.sk_ckl[i - 1][5]
                    self.sk_ckl.append((ckli, cksdh, cksdl, cklhp, ckllp, cklbi))

                    # 更新 self.ckls
                    self.ckls[-1][1] += 1
                    self.ckls[-1][3] = cksdl
                    self.ckls[-1][4] = cksdl - cksdh

                else:
                    ckli = 1
                    cksdl = self.sk_ckl[i - 1][2]
                    cksdh = self.sk_close[i]
                    cklhp = self.sk_high[i]
                    ckllp = min(self.sk_low[i], cksdl)
                    self.sk_ckl.append((ckli, cksdh, cksdl, cklhp, ckllp, i))

                    # 更新 self.ckls
                    cklbi = i
                    cklei = i
                    cklbp = cksdl
                    cklep = cksdh
                    cklsd = cklep - cklbp
                    self.ckls.append([cklbi, cklei, cklbp, cklep, cklsd])

            # print(i,self.sk_close.index[i],(ckli, round(cksdh,decsn), round(cksdl,decsn)))
            # self.sk_cklsm=[] #在sk序列框架下对ckls结构进行描述，指示当前的sk处于ckls结构中的水平 (ckltp, ickls)
            if len(self.ckls) >= 3:
                ickls0 = tuple(self.ckls[-1])
                ickls1 = tuple(self.ckls[-2])
                ickls2 = tuple(self.ckls[-3])
                if (ickls0[4] > 0 and self.sk_cklsm[-1][0] >= 3) or (
                                    ickls0[4] > 0 and ickls0[3] > ickls1[2] and ickls1[3] >= ickls2[2]):
                    # 3---处于nuckl N-S up ckl            (ickls0,ickls1,ickls2)
                    ckltp = 3
                    ickls = (ickls0, ickls1, ickls2)
                    self.sk_cklsm.append((ckltp, ickls))

                    # 更新self.nsckls=[]  由[nsckltp，insckls]组成 insckls=[insckls0,insckls1,insckls2...]
                    if len(self.nsckls) < 1:
                        nsckltp = 3
                        insckls0 = ickls0
                        insckls1 = ickls1
                        insckls2 = ickls2
                        insckls = [insckls2, insckls1, insckls0]

                        for icklsx in self.ckls[0:-3]:
                            if icklsx[4] >= 0:
                                self.nsckls.append([1, [tuple(icklsx)]])
                            else:
                                self.nsckls.append([-1, [tuple(icklsx)]])
                        self.nsckls.append([nsckltp, insckls])
                        self.nscklsedi = len(self.ckls) - 1
                    else:  # if len[self.nsckls]>=1 :
                        insckls = self.nsckls[-1][1]
                        if self.nsckls[-1][0] > 0 and ickls1[0] >= insckls[-2][0] and ickls1[1] <= insckls[-2][1] and ickls2[0] >= insckls[-3][0] and \
                                        ickls2[1] <= insckls[-3][1] \
                                and ickls0[0] <= insckls[-1][1]:
                            self.nsckls[-1][1][-1] = ickls0
                        elif self.nsckls[-1][0] > 0 and ickls2[0] == insckls[-1][0] and ickls2[1] == insckls[-1][1] and ickls1[1] > insckls[-1][1]:
                            self.nsckls[-1][0] += 2
                            self.nsckls[-1][1].append(ickls1)
                            self.nsckls[-1][1].append(ickls0)
                            self.nscklsedi = len(self.ckls) - 1

                        elif ickls2[0] == insckls[-1][1]:
                            nsckltp = 3
                            insckls0 = ickls0
                            insckls1 = ickls1
                            insckls2 = ickls2
                            insckls = [insckls2, insckls1, insckls0]
                            self.nsckls.append([nsckltp, insckls])
                            self.nscklsedi = len(self.ckls) - 1

                        elif ickls2[0] > insckls[-1][1]:
                            nsckltp = 3
                            insckls0 = ickls0
                            insckls1 = ickls1
                            insckls2 = ickls2
                            insckls = [insckls2, insckls1, insckls0]
                            for icklsx in self.ckls[self.nscklsedi + 1:-3]:
                                if icklsx[4] >= 0:
                                    self.nsckls.append([1, [tuple(icklsx)]])
                                else:
                                    self.nsckls.append([-1, [tuple(icklsx)]])
                            self.nsckls.append([nsckltp, insckls])
                            self.nscklsedi = len(self.ckls) - 1


                elif (ickls0[4] < 0 and self.sk_cklsm[-1][0] <= -3) or (
                                    ickls0[4] < 0 and ickls0[3] < ickls1[2] and ickls1[3] <= ickls2[2]):
                    # -3---处于ndckl N-S dowm ckl          (ickls0,ickls1,ickls2)
                    ckltp = -3
                    ickls = (ickls0, ickls1, ickls2)
                    self.sk_cklsm.append((ckltp, ickls))

                    # 更新self.nsckls=[]  由[nsckltp，insckls]组成 insckls=[insckls0,insckls1,insckls2...]
                    if len(self.nsckls) < 1:
                        nsckltp = -3
                        insckls0 = ickls0
                        insckls1 = ickls1
                        insckls2 = ickls2
                        insckls = [insckls2, insckls1, insckls0]

                        for icklsx in self.ckls[0:-3]:
                            if icklsx[4] >= 0:
                                self.nsckls.append([1, [tuple(icklsx)]])
                            else:
                                self.nsckls.append([-1, [tuple(icklsx)]])
                        self.nsckls.append([nsckltp, insckls])
                        self.nscklsedi = len(self.ckls) - 1
                    else:  # if len[self.nsckls]>=1 :
                        insckls = self.nsckls[-1][1]
                        if self.nsckls[-1][0] < 0 and ickls1[0] >= insckls[-2][0] and ickls1[1] <= insckls[-2][1] and ickls2[0] >= insckls[-3][0] and \
                                        ickls2[1] <= insckls[-3][1] \
                                and ickls0[0] <= insckls[-1][1]:
                            self.nsckls[-1][1][-1] = ickls0
                        elif self.nsckls[-1][0] < 0 and ickls2[0] == insckls[-1][0] and ickls2[1] == insckls[-1][1] and ickls1[1] > insckls[-1][1]:
                            self.nsckls[-1][0] += -2
                            self.nsckls[-1][1].append(ickls1)
                            self.nsckls[-1][1].append(ickls0)
                            self.nscklsedi = len(self.ckls) - 1
                        elif ickls2[0] == insckls[-1][1]:
                            nsckltp = -3
                            insckls0 = ickls0
                            insckls1 = ickls1
                            insckls2 = ickls2
                            insckls = [insckls2, insckls1, insckls0]
                            self.nsckls.append([nsckltp, insckls])
                            self.nscklsedi = len(self.ckls) - 1

                        elif ickls2[0] > insckls[-1][1]:
                            nsckltp = -3
                            insckls0 = ickls0
                            insckls1 = ickls1
                            insckls2 = ickls2
                            insckls = [insckls2, insckls1, insckls0]
                            for icklsx in self.ckls[self.nscklsedi + 1:-3]:
                                if icklsx[4] >= 0:
                                    self.nsckls.append([1, [tuple(icklsx)]])
                                else:
                                    self.nsckls.append([-1, [tuple(icklsx)]])
                            self.nsckls.append([nsckltp, insckls])
                            self.nscklsedi = len(self.ckls) - 1

                elif (ickls0[4] > 0 and self.sk_cklsm[-1][0] >= 2) or ickls0[4] >= detsuc * avgski:
                    # 2---处于suckl strong up ckl       (ickls0,)
                    ckltp = 2
                    ickls = (ickls0,)
                    self.sk_cklsm.append((ckltp, ickls))
                elif (ickls0[4] < 0 and self.sk_cklsm[-1][0] <= -2) or ickls0[4] <= detsdc * avgski:
                    # -2--处于sdckl strong down ckl     (ickls0,)
                    ckltp = -2
                    ickls = (ickls0, ickls1, ickls2)
                    self.sk_cklsm.append((ckltp, ickls))
                elif ickls0[4] > 0 and ickls0[4] < detsuc * avgski:
                    # 1---处于wuckl weak up ckl         (ickls0,)
                    ckltp = 1
                    ickls = (ickls0, ickls1, ickls2)
                    self.sk_cklsm.append((ckltp, ickls))
                elif ickls0[4] < 0 and ickls0[4] > detsdc * avgski:
                    # -1--处于wdckl weak down ckl       (ickls0,)
                    ckltp = -1
                    ickls = (ickls0, ickls1, ickls2)
                    self.sk_cklsm.append((ckltp, ickls))
                else:
                    ckltp = 0
                    ickls = (ickls0, ickls1, ickls2)
                    self.sk_cklsm.append((ckltp, ickls))
            else:  # if len(ckls)<3:
                ickls0 = tuple(self.ckls[-1])
                if (ickls0[4] > 0 and self.sk_cklsm[-1][0] >= 2) or ickls0[4] >= detsuc * avgski:
                    # 2---处于suckl strong up ckl       (ickls0,)
                    ckltp = 2
                    ickls = (ickls0,)
                    self.sk_cklsm.append((ckltp, ickls))
                elif (ickls0[4] < 0 and self.sk_cklsm[-1][0] <= -2) or ickls0[4] <= detsdc * avgski:
                    # -2--处于sdckl strong down ckl     (ickls0,)
                    ckltp = -2
                    ickls = (ickls0,)
                    self.sk_cklsm.append((ckltp, ickls))
                if ickls0[4] > 0 and ickls0[4] < detsuc * avgski:
                    # 1---处于wuckl weak up ckl         (ickls0,)
                    ckltp = 1
                    ickls = (ickls0,)
                    self.sk_cklsm.append((ckltp, ickls))
                elif ickls0[4] < 0 and ickls0[4] > detsdc * avgski:
                    # -1--处于wdckl weak down ckl       (ickls0,)
                    ckltp = -1
                    ickls = (ickls0,)
                    self.sk_cklsm.append((ckltp, ickls))
                else:
                    ckltp = 0
                    ickls = (ickls0,)
                    self.sk_cklsm.append((ckltp, ickls))

            # 更新  qspds=[] #趋势前沿列表 每段由[qsprti,nscklidx,nscklitp,qspbi,qspei,qspbsdp,qspesdp,qspbp,qspep]组成，来自于self.nsckls的波段
            self.bsbj = 0
            if len(self.qspds) <= 0 and len(self.nsckls) > 0:  # 当首次形成确定性的聚合链（数量可能大于1）的时候逐链划分趋势前沿
                nscklidx = 0
                qsprti = self.nsckls[-1][1][-1][1]
                nscklitp = self.nsckls[-1][0]
                qspbi = self.nsckls[-1][1][0][0]
                qspei = self.nsckls[-1][1][-1][1]
                qspbsdp = self.nsckls[-1][1][0][2]
                qspesdp = self.nsckls[-1][1][-1][3]
                if nscklitp > 0:
                    qspbp = min(self.sk_low[qspbi], self.sk_low[qspbi - 1])
                    qspep = self.sk_high[qspei]
                else:
                    qspbp = max(self.sk_high[qspbi], self.sk_high[qspbi - 1])
                    qspep = self.sk_low[qspei]

                self.qspds.append([qsprti, nscklidx, nscklitp, qspbi, qspei, qspbsdp, qspesdp, qspbp, qspep])

                revlsi = self.ckls[-1][0] - 1
                self.qsstpchain.append(Stepchain(nscklitp, i, self.sk_ckl[i], self.sk_ckl[revlsi]))
                # --------------------------------------------------------------------------------------------
                if False:  # i > qspei:
                    for idx in range(qspei + 1, i + 1):
                        iqspds0 = self.qspds[-1]
                        if iqspds0[2] > 0:  # 当前的趋势是向上前沿
                            if self.sk_close[idx] > iqspds0[6]:  # 向上步进
                                # 检查此时的idx 处于第几个nsckls
                                nscklidx = self.idxof_nsckls(self.nsckls, idx)
                                if nscklidx > 0 and nscklidx > iqspds0[1]:
                                    qsprti = idx
                                    nscklitp = self.nsckls[nscklidx][0]
                                    qspbi = self.nsckls[nscklidx][1][0][0]
                                    qspei = self.nsckls[nscklidx][1][-1][1]
                                    qspbsdp = self.nsckls[nscklidx][1][0][2]
                                    qspesdp = self.nsckls[nscklidx][1][-1][3]
                                    if qspbi > 0:
                                        qspbp = min(self.sk_low[qspbi], self.sk_low[qspbi - 1])
                                    else:
                                        qspbp = self.sk_low[qspbi]
                                    if qspei <= i - 1:
                                        qspep = max(self.sk_high[qspei], self.sk_high[qspei + 1])
                                    else:
                                        qspep = self.sk_high[qspei]
                                    self.qspds.append([qsprti, nscklidx, nscklitp, qspbi, qspei, qspbsdp, qspesdp, qspbp, qspep])
                            elif self.sk_close[idx] < iqspds0[7]:  # 向下反转
                                # 检查此时的idx 处于第几个nsckls
                                nscklidx = self.idxof_nsckls(self.nsckls, idx)
                                if nscklidx > 0 and nscklidx > iqspds0[1]:
                                    qsprti = idx
                                    nscklitp = self.nsckls[nscklidx][0]
                                    qspbi = self.nsckls[nscklidx][1][0][0]
                                    qspei = self.nsckls[nscklidx][1][-1][1]
                                    qspbsdp = self.nsckls[nscklidx][1][0][2]
                                    qspesdp = self.nsckls[nscklidx][1][-1][3]
                                    if qspbi > 0:
                                        qspbp = max(self.sk_high[qspbi], self.sk_high[qspbi - 1])
                                    else:
                                        qspbp = self.sk_high[qspbi]
                                    if qspei <= i - 1:
                                        qspep = min(self.sk_low[qspei], self.sk_low[qspei + 1])
                                    else:
                                        qspep = self.sk_low[qspei]
                                    self.qspds.append([qsprti, nscklidx, nscklitp, qspbi, qspei, qspbsdp, qspesdp, qspbp, qspep])

                        elif iqspds0[2] < 0:  # 当前的趋势是向下前沿
                            if self.sk_close[idx] < iqspds0[6]:  # 向下步进
                                # 检查此时的idx 处于第几个nsckls
                                nscklidx = self.idxof_nsckls(self.nsckls, idx)
                                if nscklidx > 0 and nscklidx > iqspds0[1]:
                                    qsprti = idx
                                    nscklitp = self.nsckls[nscklidx][0]
                                    qspbi = self.nsckls[nscklidx][1][0][0]
                                    qspei = self.nsckls[nscklidx][1][-1][1]
                                    qspbsdp = self.nsckls[nscklidx][1][0][2]
                                    qspesdp = self.nsckls[nscklidx][1][-1][3]
                                    if qspbi > 0:
                                        qspbp = max(self.sk_high[qspbi], self.sk_high[qspbi - 1])
                                    else:
                                        qspbp = self.sk_high[qspbi]
                                    if qspei <= i - 1:
                                        qspep = min(self.sk_low[qspei], self.sk_low[qspei + 1])
                                    else:
                                        qspep = self.sk_low[qspei]
                                    self.qspds.append([qsprti, nscklidx, nscklitp, qspbi, qspei, qspbsdp, qspesdp, qspbp, qspep])
                            elif self.sk_close[idx] > iqspds0[7]:  # 向上反转
                                # 检查此时的idx 处于第几个nsckls
                                nscklidx = self.idxof_nsckls(self.nsckls, idx)
                                if nscklidx > 0 and nscklidx > iqspds0[1]:
                                    qsprti = idx
                                    nscklitp = self.nsckls[nscklidx][0]
                                    qspbi = self.nsckls[nscklidx][1][0][0]
                                    qspei = self.nsckls[nscklidx][1][-1][1]
                                    qspbsdp = self.nsckls[nscklidx][1][0][2]
                                    qspesdp = self.nsckls[nscklidx][1][-1][3]
                                    if qspbi > 0:
                                        qspbp = min(self.sk_low[qspbi], self.sk_low[qspbi - 1])
                                    else:
                                        qspbp = self.sk_low[qspbi]
                                    if qspei <= i - 1:
                                        qspep = max(self.sk_high[qspei], self.sk_high[qspei + 1])
                                    else:
                                        qspep = self.sk_high[qspei]
                                    self.qspds.append([qsprti, nscklidx, nscklitp, qspbi, qspei, qspbsdp, qspesdp, qspbp, qspep])

            # 对于当前的isk, 更新qspds
            elif len(self.qspds) >= 1:
                iqspds0 = self.qspds[-1]
                if iqspds0[2] > 0:  # 之前的趋势是向上前沿
                    if self.sk_ckl[i][0] < 0:
                        if not self.bscp:
                            self.bscp = self.sk_high[i]
                        else:
                            self.bscp = max(self.bscp, self.sk_high[i])
                    if self.bscp and self.sk_close[i] > self.bscp:
                        self.bsbj = 1
                    # 最新的isk与之前的趋势前沿同处于一个聚合链或单链上--延伸
                    if i == self.nsckls[-1][1][-1][1] and self.nsckls[-1][1][0][0] <= iqspds0[3]:  # 最新的isk与之前的趋势前沿同处于一个聚合链
                        nscklidx = len(self.nsckls) - 1
                        qsprti = iqspds0[0]
                        nscklitp = self.nsckls[-1][0]
                        qspbi = self.nsckls[-1][1][0][0]
                        qspei = self.nsckls[-1][1][-1][1]
                        qspbsdp = self.nsckls[-1][1][0][2]
                        qspesdp = self.nsckls[-1][1][-1][3]
                        qspbp = min(self.sk_low[qspbi], self.sk_low[qspbi - 1])
                        qspep = max(iqspds0[8], self.sk_high[qspei])
                        self.qspds[-1] = [qsprti, nscklidx, nscklitp, qspbi, qspei, qspbsdp, qspesdp, qspbp, qspep]

                    elif iqspds0[4] >= self.ckls[-1][0] and iqspds0[4] <= self.ckls[-1][1]:  # 最新的isk与之前的趋势前沿同处于一个单链
                        nscklidx = 0
                        qsprti = iqspds0[0]
                        nscklitp = 1
                        qspbi = self.ckls[-1][0]
                        qspei = self.ckls[-1][1]
                        qspbsdp = self.ckls[-1][2]
                        qspesdp = self.ckls[-1][3]
                        qspbp = min(self.sk_low[qspbi], self.sk_low[qspbi - 1])
                        qspep = max(iqspds0[8], self.sk_high[qspei])
                        self.qspds[-1] = [qsprti, nscklidx, nscklitp, qspbi, qspei, qspbsdp, qspesdp, qspbp, qspep]

                    elif self.sk_close[i] > iqspds0[8]:  # 向上步进
                        # 检查此时的isk 是否处于最新的nsckls上
                        if i == self.nsckls[-1][1][-1][1]:  # 该聚合链是新前沿，向上步进
                            nscklidx = len(self.nsckls) - 1
                            qsprti = i
                            nscklitp = self.nsckls[-1][0]
                            qspbi = self.nsckls[-1][1][0][0]
                            qspei = self.nsckls[-1][1][-1][1]
                            qspbsdp = self.nsckls[-1][1][0][2]
                            qspesdp = self.nsckls[-1][1][-1][3]
                            qspbp = min(self.sk_low[qspbi], self.sk_low[qspbi - 1])
                            qspep = self.sk_high[qspei]
                            self.qspds.append([qsprti, nscklidx, nscklitp, qspbi, qspei, qspbsdp, qspesdp, qspbp, qspep])

                        else:  # 该isk还还不在一个聚合链上，但一定在最新的单链上，将此单链作为趋势前沿
                            nscklidx = 0
                            qsprti = i
                            nscklitp = 1
                            qspbi = self.ckls[-1][0]
                            qspei = self.ckls[-1][1]
                            qspbsdp = self.ckls[-1][2]
                            qspesdp = self.ckls[-1][3]
                            qspbp = min(self.sk_low[qspbi], self.sk_low[qspbi - 1])
                            qspep = self.sk_high[qspei]
                            self.qspds.append([qsprti, nscklidx, nscklitp, qspbi, qspei, qspbsdp, qspesdp, qspbp, qspep])

                    elif self.sk_close[i] < self.zslp:  # iqspds0[7]:  # 趋势前沿向下逆转
                        # 检查此时的isk 是否处于最新的nsckls上
                        if i == self.nsckls[-1][1][-1][1]:  # 该聚合链是新前沿
                            nscklidx = len(self.nsckls) - 1
                            qsprti = i
                            nscklitp = self.nsckls[-1][0]
                            qspbi = self.nsckls[-1][1][0][0]
                            qspei = self.nsckls[-1][1][-1][1]
                            qspbsdp = self.nsckls[-1][1][0][2]
                            qspesdp = self.nsckls[-1][1][-1][3]
                            qspbp = max(self.sk_high[qspbi], self.sk_high[qspbi - 1])
                            qspep = self.sk_low[qspei]
                            self.qspds.append([qsprti, nscklidx, nscklitp, qspbi, qspei, qspbsdp, qspesdp, qspbp, qspep])

                        else:  # 该isk还还不在一个聚合链上，但一定在最新的单链上，将此单链作为趋势前沿
                            nscklidx = 0
                            qsprti = i
                            nscklitp = -1
                            qspbi = self.ckls[-1][0]
                            qspei = self.ckls[-1][1]
                            qspbsdp = self.ckls[-1][2]
                            qspesdp = self.ckls[-1][3]
                            qspbp = max(self.sk_high[qspbi], self.sk_high[qspbi - 1])
                            qspep = self.sk_low[qspei]
                            self.qspds.append([qsprti, nscklidx, nscklitp, qspbi, qspei, qspbsdp, qspesdp, qspbp, qspep])

                    if i == self.qspds[-1][4] + 1:  # 更新右端极值点
                        if self.qspds[-1][2] > 0:
                            qspep = max(self.sk_high[i], self.qspds[-1][8])
                            self.qspds[-1][8] = qspep
                        elif self.qspds[-1][2] < 0:
                            qspep = min(self.sk_low[i], self.qspds[-1][8])
                            self.qspds[-1][8] = qspep

                elif iqspds0[2] < 0:  # 之前的趋势是向下前沿
                    if self.sk_ckl[i][0] > 0:
                        if not self.bscp:
                            self.bscp = self.sk_low[i]
                        else:
                            self.bscp = min(self.bscp, self.sk_low[i])
                    if self.bscp and self.sk_close[i] < self.bscp:
                        self.bsbj = -1
                    # 最新的isk与之前的趋势前沿同处于一个聚合链或单链上--延伸
                    if i == self.nsckls[-1][1][-1][1] and self.nsckls[-1][1][0][0] <= iqspds0[3]:  # 最新的isk与之前的趋势前沿同处于一个聚合链
                        nscklidx = len(self.nsckls) - 1
                        qsprti = iqspds0[0]
                        nscklitp = self.nsckls[-1][0]
                        qspbi = self.nsckls[-1][1][0][0]
                        qspei = self.nsckls[-1][1][-1][1]
                        qspbsdp = self.nsckls[-1][1][0][2]
                        qspesdp = self.nsckls[-1][1][-1][3]
                        qspbp = max(self.sk_high[qspbi], self.sk_high[qspbi - 1])
                        qspep = min(self.qspds[-1][8], self.sk_low[qspei])
                        self.qspds[-1] = [qsprti, nscklidx, nscklitp, qspbi, qspei, qspbsdp, qspesdp, qspbp, qspep]

                    elif iqspds0[4] >= self.ckls[-1][0] and iqspds0[4] <= self.ckls[-1][1]:  # 最新的isk与之前的趋势前沿同处于一个单链
                        nscklidx = 0
                        qsprti = iqspds0[0]
                        nscklitp = -1
                        qspbi = self.ckls[-1][0]
                        qspei = self.ckls[-1][1]
                        qspbsdp = self.ckls[-1][2]
                        qspesdp = self.ckls[-1][3]
                        qspbp = max(self.sk_high[qspbi], self.sk_high[qspbi - 1])
                        qspep = min(self.qspds[-1][8], self.sk_low[qspei])
                        self.qspds[-1] = [qsprti, nscklidx, nscklitp, qspbi, qspei, qspbsdp, qspesdp, qspbp, qspep]

                    elif self.sk_close[i] < iqspds0[8]:  # 向下步进
                        # 检查此时的isk 是否处于最新的nsckls上
                        if i == self.nsckls[-1][1][-1][1]:  # 该聚合链是新前沿，向下步进
                            nscklidx = len(self.nsckls) - 1
                            qsprti = i
                            nscklitp = self.nsckls[-1][0]
                            qspbi = self.nsckls[-1][1][0][0]
                            qspei = self.nsckls[-1][1][-1][1]
                            qspbsdp = self.nsckls[-1][1][0][2]
                            qspesdp = self.nsckls[-1][1][-1][3]
                            qspbp = max(self.sk_high[qspbi], self.sk_high[qspbi - 1])
                            qspep = self.sk_low[qspei]
                            self.qspds.append([qsprti, nscklidx, nscklitp, qspbi, qspei, qspbsdp, qspesdp, qspbp, qspep])

                        else:  # 该isk还还不在一个聚合链上，但一定在最新的单链上，将此单链作为趋势前沿
                            nscklidx = 0
                            qsprti = i
                            nscklitp = -1
                            qspbi = self.ckls[-1][0]
                            qspei = self.ckls[-1][1]
                            qspbsdp = self.ckls[-1][2]
                            qspesdp = self.ckls[-1][3]
                            qspbp = max(self.sk_high[qspbi], self.sk_high[qspbi - 1])
                            qspep = self.sk_low[qspei]
                            self.qspds.append([qsprti, nscklidx, nscklitp, qspbi, qspei, qspbsdp, qspesdp, qspbp, qspep])

                    elif self.sk_close[i] > self.zshp:  # iqspds0[7]:  # 趋势前沿向上逆转
                        # 检查此时的isk 是否处于最新的nsckls上
                        if i == self.nsckls[-1][1][-1][1]:  # 该聚合链是新前沿，向上逆转
                            nscklidx = len(self.nsckls) - 1
                            qsprti = i
                            nscklitp = self.nsckls[-1][0]
                            qspbi = self.nsckls[-1][1][0][0]
                            qspei = self.nsckls[-1][1][-1][1]
                            qspbsdp = self.nsckls[-1][1][0][2]
                            qspesdp = self.nsckls[-1][1][-1][3]
                            qspbp = min(self.sk_low[qspbi], self.sk_low[qspbi - 1])
                            qspep = self.sk_high[qspei]
                            self.qspds.append([qsprti, nscklidx, nscklitp, qspbi, qspei, qspbsdp, qspesdp, qspbp, qspep])

                        else:  # 该isk还还不在一个聚合链上，但一定在最新的单链上，将此单链作为趋势前沿
                            nscklidx = 0
                            qsprti = i
                            nscklitp = 1
                            qspbi = self.ckls[-1][0]
                            qspei = self.ckls[-1][1]
                            qspbsdp = self.ckls[-1][2]
                            qspesdp = self.ckls[-1][3]
                            qspbp = min(self.sk_low[qspbi], self.sk_low[qspbi - 1])
                            qspep = self.sk_high[qspei]
                            self.qspds.append([qsprti, nscklidx, nscklitp, qspbi, qspei, qspbsdp, qspesdp, qspbp, qspep])

                    if i == self.qspds[-1][4] + 1:  # 更新右端极值点
                        if self.qspds[-1][2] > 0:
                            qspep = max(self.sk_high[i], self.qspds[-1][8])
                            self.qspds[-1][8] = qspep
                        elif self.qspds[-1][2] < 0:
                            qspep = min(self.sk_low[i], self.qspds[-1][8])
                            self.qspds[-1][8] = qspep
            newsgn = None
            if len(self.qspds) <= 0:
                qsprti = i
                nscklidx = 0
                nscklitp = 0
                qspbi = 0
                qspei = i
                qspbsdp = self.sk_open[0]
                qspesdp = self.sk_close[i]
                qspbp = self.sk_open[0]
                qspep = self.sk_close[i]
                self.zslp = cksdl
                self.zshp = cksdh
                self.bslp = cksdl
                self.bshp = cksdh
                self.sk_sgn.append(None)

            else:
                qsprti = self.qspds[-1][0]
                nscklidx = self.qspds[-1][1]
                nscklitp = self.qspds[-1][2]
                qspbi = self.qspds[-1][3]
                qspei = self.qspds[-1][4]
                qspbsdp = self.qspds[-1][5]
                qspesdp = self.qspds[-1][6]
                qspbp = self.qspds[-1][7]
                qspep = self.qspds[-1][8]
                # 对于当前的isk, 更新zs
                iqspds0 = self.qspds[-1]
                headqsp = self.sk_cklsm[self.qspds[-1][4]]  # 趋势前沿头部 triple ckls
                self.zsdir = iqspds0[2]
                # dtmi= pd.to_datetime(self.sk_time[i])
                # if '2010-11-17' in str(dtmi):
                #     print 'none'
                if len(headqsp[1]) > 1:
                    self.zsckl = headqsp[1][1]
                    self.zsski = self.zsckl[1]
                    bsski = self.zsckl[0]
                    if nscklitp > 0:
                        self.zslp = min(self.sk_low[self.zsski], self.sk_low[self.zsski + 1])  # self.sk_low[self.zsski]
                        self.zshp = max(min(self.sk_open[self.zsski], self.sk_close[self.zsski]), min(self.sk_open[self.zsski + 1], self.sk_close[
                            self.zsski + 1]))  # min(self.sk_open[self.zsski],self.sk_close[self.zsski])   max(self.sk_low[self.zsski], self.sk_low[self.zsski+1])
                        self.zshp = self.zslp
                        self.bslp = sorted([max(self.sk_open[bsski], self.sk_close[bsski]), max(self.sk_open[bsski - 1], self.sk_close[bsski - 1]),
                                            max(self.sk_open[bsski - 2], self.sk_close[bsski - 2])])[
                            1]  # min(self.sk_high[bsski], self.sk_high[bsski - 1]) #
                        self.bshp = sorted([self.sk_high[bsski], self.sk_high[bsski - 1], self.sk_high[bsski - 2]])[
                            1]  # max(max(self.sk_open[bsski], self.sk_close[bsski]), max(self.sk_open[bsski-1], self.sk_close[bsski-1])) #min(self.sk_high[bsski], self.sk_high[bsski - 1]) #max(self.sk_high[bsski], self.sk_high[bsski - 1])
                    else:
                        self.zshp = max(self.sk_high[self.zsski], self.sk_high[self.zsski + 1])  # self.sk_high[self.zsski]
                        self.zslp = min(max(self.sk_open[self.zsski], self.sk_close[self.zsski]),
                                        max(self.sk_open[self.zsski + 1],
                                            self.sk_close[self.zsski + 1]))  # max(self.sk_open[self.zsski], self.sk_close[self.zsski])
                        self.zslp = self.zshp
                        self.bslp = sorted([self.sk_low[bsski], self.sk_low[bsski - 1], self.sk_low[bsski - 2]])[
                            1]  # min(min(self.sk_open[bsski], self.sk_close[bsski]), min(self.sk_open[bsski-1], self.sk_close[bsski-1])) # max(self.sk_low[bsski], self.sk_low[bsski - 1])   # min(self.sk_low[bsski], self.sk_low[bsski - 1])
                        self.bshp = sorted([min(self.sk_open[bsski], self.sk_close[bsski]), min(self.sk_open[bsski - 1], self.sk_close[bsski - 1]),
                                            min(self.sk_open[bsski - 2], self.sk_close[bsski - 2])])[
                            1]  # max(self.sk_low[bsski], self.sk_low[bsski - 1]) #

                        # self.zslp = self.sk_low[self.zsckl[1]]
                        # self.zshp = self.sk_high[self.zsckl[1]]
                else:
                    self.zsckl = headqsp[1][0]
                    self.zsski = self.zsckl[0]
                    bsski = self.zsski - abs(self.sk_ckl[self.zsski - 1][0])
                    if nscklitp > 0:
                        self.zslp = min(self.sk_low[self.zsski], self.sk_low[self.zsski - 1])  # self.sk_low[self.zsski]
                        self.zshp = max(min(self.sk_open[self.zsski], self.sk_close[self.zsski]),
                                        min(self.sk_open[self.zsski - 1],
                                            self.sk_close[self.zsski - 1]))  # min(self.sk_open[self.zsski],self.sk_close[self.zsski])
                        self.zshp = self.zslp
                        self.bslp = sorted([max(self.sk_open[bsski], self.sk_close[bsski]), max(self.sk_open[bsski - 1], self.sk_close[bsski - 1]),
                                            max(self.sk_open[bsski - 2], self.sk_close[bsski - 2])])[
                            1]  # min(self.sk_high[bsski], self.sk_high[bsski - 1])
                        self.bshp = sorted([self.sk_high[bsski], self.sk_high[bsski - 1], self.sk_high[bsski - 2]])[
                            1]  # max(max(self.sk_open[bsski], self.sk_close[bsski]), max(self.sk_open[bsski-1], self.sk_close[bsski-1])) # max(self.sk_high[bsski], self.sk_high[bsski - 1])
                    else:
                        self.zshp = max(self.sk_high[self.zsski], self.sk_high[self.zsski - 1])  # self.sk_high[self.zsski]
                        self.zslp = min(max(self.sk_open[self.zsski], self.sk_close[self.zsski]),
                                        max(self.sk_open[self.zsski - 1],
                                            self.sk_close[self.zsski - 1]))  # min(self.sk_open[self.zsski], self.sk_close[self.zsski])
                        self.zslp = self.zshp
                        self.bslp = sorted([self.sk_low[bsski], self.sk_low[bsski - 1], self.sk_low[bsski - 2]])[
                            1]  # min(min(self.sk_open[bsski], self.sk_close[bsski]), min(self.sk_open[bsski-1], self.sk_close[bsski-1]))  #  min(self.sk_low[bsski], self.sk_low[bsski - 1])
                        self.bshp = sorted([min(self.sk_open[bsski], self.sk_close[bsski]), min(self.sk_open[bsski - 1], self.sk_close[bsski - 1]),
                                            min(self.sk_open[bsski - 2], self.sk_close[bsski - 2])])[
                            1]  # max(self.sk_low[bsski], self.sk_low[bsski - 1])
                        # self.zslp = self.sk_low[self.zsckl[0]]
                        # self.zshp = self.sk_high[self.zsckl[0]]
                # ------------------------------更新 qsbands, zsbands
                if nscklitp > 0:
                    bandlp = qspbp
                    bandhp = min(min(self.sk_open[qspbi], self.sk_close[qspbi]), min(self.sk_open[qspbi - 1], self.sk_close[qspbi - 1]))
                    newband = Rsband(qspbi, qspei, bandhp, bandlp)
                    if not self.lstupqsbd or self.lstupqsbd.dtbi != newband.dtbi:
                        self.upqsbands.addband(newband)
                        self.lstupqsbd = newband
                    elif self.lstupqsbd.dtei != newband.dtei:
                        self.upqsbands.updateband(newband)
                        self.lstupqsbd = newband
                # --------------------------------------------------
                elif nscklitp < 0:
                    bandhp = qspbp
                    bandlp = max(max(self.sk_open[qspbi], self.sk_close[qspbi]), max(self.sk_open[qspbi - 1], self.sk_close[qspbi - 1]))
                    newband = Rsband(qspbi, qspei, bandhp, bandlp)
                    if not self.lstdwqsbd or self.lstdwqsbd.dtbi != newband.dtbi:
                        self.dwqsbands.addband(newband)
                        self.lstdwqsbd = newband
                    elif self.lstdwqsbd.dtei != newband.dtei:
                        self.dwqsbands.updateband(newband)
                        self.lstdwqsbd = newband
                # --------------------------------------------------

                if self.sk_qspds[-1][2] > 0 and nscklitp < 0:
                    newband = copy.copy(self.lstupzsbd)
                    newband.dtbi = i
                    newband.dtei = i
                    self.dwzsbands.addband(newband)
                if self.sk_qspds[-1][2] < 0 and nscklitp > 0:
                    newband = copy.copy(self.lstdwzsbd)
                    newband.dtbi = i
                    newband.dtei = i
                    self.upzsbands.addband(newband)

                newband = Rsband(self.zsski, self.zsski, self.zshp, self.zslp)
                if self.zsdir > 0:
                    if not self.lstupzsbd or self.lstupzsbd.dtbi != newband.dtbi:
                        self.upzsbands.addband(newband)
                        self.lstupzsbd = newband
                elif self.zsdir < 0:
                    if not self.lstdwzsbd or self.lstdwzsbd.dtbi != newband.dtbi:
                        self.dwzsbands.addband(newband)
                        self.lstdwzsbd = newband

                # --------------------------------------------------
                # 更新 ----------------------------------------------self.sk_sgn
                lstsgn = self.sk_sgn[-1]
                sgndir = 0
                newsgn = Sgn_Rst(0, i, self.sk_close[i])
                if not lstsgn:
                    newsgn.rsti = i
                    newsgn.rstp = self.sk_close[i]
                    newsgn.rstbi = qspbi
                    if nscklitp > 0:
                        sgndir = 1
                        self.upqsbands.updateformdti(newsgn.rstbi, newsgn.rstp)
                        self.upzsbands.updateformdti(newsgn.rstbi, newsgn.rstp)
                    if nscklitp < 0:
                        sgndir = -1
                        self.dwqsbands.updateformdti(newsgn.rstbi, newsgn.rstp)
                        self.dwzsbands.updateformdti(newsgn.rstbi, newsgn.rstp)
                else:
                    lstsgn.set_sgn(self.sk_open[i], self.sk_high[i], self.sk_low[i], self.sk_close[i], self.sk_atr[i])
                    # dtmi= pd.to_datetime(self.sk_time[i])
                    # if '2011-10-28' in str(dtmi):
                    #     print lstsgn.sgn_qs2c
                    #     print 'chk'

                    newsgn.rsti = lstsgn.rsti
                    newsgn.rstp = lstsgn.rstp
                    newsgn.rstbi = lstsgn.rstbi
                    if lstsgn.rstdir > 0:
                        sgndir = 1

                        if lstsgn.sgn_qs1c and lstsgn.sgn_qs1c[0] <= -5:

                            if self.dwqsbands.count > 0:
                                sgndir = -1
                                newsgn.rsti = i

                                newsgn.rstp = lstsgn.rsp_qs1c
                                dwrsband = self.dwqsbands.getbandby_bmp('max')
                                newsgn.rstbi = dwrsband.dtbi
                                self.dwqsbands.updateformdti(newsgn.rstbi, newsgn.rstp)
                                self.dwzsbands.updateformdti(newsgn.rstbi, newsgn.rstp)
                                # elif not lstsgn.sgn_qs2c and lstsgn.sgn_qs1c and lstsgn.sgn_qs1c[0] <= -5:
                                #
                                #     if self.dwqsbands.count>0:
                                #         sgndir = -1
                                #         newsgn.rsti = i
                                #
                                #         newsgn.rstp = lstsgn.rsp_qs1c
                                #         dwrsband = self.dwqsbands.getbandby_bmp('max')
                                #         newsgn.rstbi = dwrsband.dtbi
                                #         self.dwqsbands.updateformdti(newsgn.rstbi, newsgn.rstp)
                                #         self.dwzsbands.updateformdti(newsgn.rstbi, newsgn.rstp)

                    else:
                        sgndir = -1

                        if lstsgn.sgn_qs1c and lstsgn.sgn_qs1c[0] >= 5:

                            if self.upqsbands.count > 0:
                                sgndir = 1
                                newsgn.rsti = i

                                newsgn.rstp = lstsgn.rsp_qs1c
                                uprsband = self.upqsbands.getbandby_bmp('min')
                                newsgn.rstbi = uprsband.dtbi
                                self.upqsbands.updateformdti(newsgn.rstbi, newsgn.rstp)
                                self.upzsbands.updateformdti(newsgn.rstbi, newsgn.rstp)
                                # elif not lstsgn.sgn_qs2c and lstsgn.sgn_qs1c and lstsgn.sgn_qs1c[0] >= 5:
                                #
                                #     if self.upqsbands.count>0:
                                #         sgndir = 1
                                #         newsgn.rsti = i
                                #
                                #         newsgn.rstp = lstsgn.rsp_qs1c
                                #         uprsband = self.upqsbands.getbandby_bmp('min')
                                #         newsgn.rstbi = uprsband.dtbi
                                #         self.upqsbands.updateformdti(newsgn.rstbi, newsgn.rstp)
                                #         self.upzsbands.updateformdti(newsgn.rstbi, newsgn.rstp)
                if sgndir > 0:
                    newsgn.rstdir = 1
                    newsgn.setqsrsp(self.upqsbands)
                    newsgn.setzsrsp(self.upzsbands)

                elif sgndir < 0:
                    newsgn.rstdir = -1
                    newsgn.setqsrsp(self.dwqsbands)
                    newsgn.setzsrsp(self.dwzsbands)

                else:
                    newsgn = None

                self.sk_sgn.append(newsgn)
                # dtmi= pd.to_datetime(self.sk_time[i])
                # if '2010-07-28' in str(dtmi):
                #     print 'chk'

                # 更新 ----------------------------------------------self.sk_sgn

            if newsgn:
                self.sk_zs1c.append(newsgn.rsp_zs1c if newsgn.rsp_zs1c else np.nan)
                self.sk_zs1a.append(newsgn.rsp_zs1a if newsgn.rsp_zs1a else np.nan)
                self.sk_zs2c.append(newsgn.rsp_zs2c if newsgn.rsp_zs2c else np.nan)
                self.sk_zs2a.append(newsgn.rsp_zs2a if newsgn.rsp_zs2a else np.nan)
                self.sk_qs1c.append(newsgn.rsp_qs1c if newsgn.rsp_qs1c else np.nan)
                self.sk_qs1a.append(newsgn.rsp_qs1a if newsgn.rsp_qs1a else np.nan)
                self.sk_qs2c.append(newsgn.rsp_qs2c if newsgn.rsp_qs2c else np.nan)
                self.sk_qs2a.append(newsgn.rsp_qs2a if newsgn.rsp_qs2a else np.nan)
            else:
                self.sk_zs1c.append(np.nan)
                self.sk_zs1a.append(np.nan)
                self.sk_zs2c.append(np.nan)
                self.sk_zs2a.append(np.nan)
                self.sk_qs1c.append(np.nan)
                self.sk_qs1a.append(np.nan)
                self.sk_qs2c.append(np.nan)
                self.sk_qs2a.append(np.nan)

            self.sk_qspds.append([qsprti, nscklidx, nscklitp, qspbi, qspei, qspbsdp, qspesdp, qspbp, qspep])
            '''
              ==============以下是信号部分==============
            '''
            self.sk_zsl.append(self.zslp)
            self.sk_zsh.append(self.zshp)
            self.sk_bsl.append(self.bslp)
            self.sk_bsh.append(self.bshp)

            self.sk_itp.append(self.sk_qspds[-1][2])

            if self.sk_qspds[-1][2] > 0:
                self.sk_qsh.append(self.sk_qspds[-1][8])
                self.sk_qsl.append(self.sk_qspds[-1][7])
                self.sk_qswr.append((self.sk_high[i] - self.zslp) / self.zslp / self.sk_atr[i - 1])
                self.sk_rsl.append(0.2 + (self.sk_qsh[-1] - self.sk_close[i]) / (self.sk_qsh[-1] - self.sk_qsl[-1]))
                self.sk_disrst.append(self.sk_qsh[-1])

                # ---------------------------------------------------------------------------------------------------trdline
                if self.ctp:
                    if self.ctp.skp < self.sk_high[i]:
                        self.ctp = Extrp(i, self.sk_high[i], 1)

                        # ----------------------------------------------------------------------------------------------------
            elif self.sk_qspds[-1][2] < 0:
                self.sk_qsh.append(self.sk_qspds[-1][7])
                self.sk_qsl.append(self.sk_qspds[-1][8])
                self.sk_qswr.append((self.sk_low[i] - self.zshp) / self.zshp / self.sk_atr[i - 1])
                self.sk_rsl.append(-0.2 + (self.sk_qsl[-1] - self.sk_close[i]) / (self.sk_qsh[-1] - self.sk_qsl[-1]))
                self.sk_disrst.append(self.sk_qsl[-1])

                # ---------------------------------------------------------------------------------------------------trdline
                if self.cbp:
                    if self.cbp.skp > self.sk_low[i]:
                        self.cbp = Extrp(i, self.sk_low[i], -1)
                # ----------------------------------------------------------------------------------------------------
            else:
                self.sk_qsh.append(self.sk_qspds[-1][7])
                self.sk_qsl.append(self.sk_qspds[-1][8])
                self.sk_qswr.append(0)
                self.sk_rsl.append(0)
                self.sk_disrst.append(self.sk_qsl[-1])

            # ----------------------------------------------基于 self.sk_disrst 生成 sadl序列
            self.uptsads(self.sk_open, self.sk_high, self.sk_low, self.sk_close, self.sk_atr, self.sk_ckl, self.sk_disrst, i)
            if len(self.sk_qspds) > 1 and self.sk_qspds[-1][2] > 0 and self.sk_qspds[-2][2] < 0:  # 向上转换
                self.rstdir = 1
                self.sads['sa_' + str(i)] = []
                self.uprstsas['upr_' + str(i)] = OrderedDict()

                self.crtsad = None
                self.tepsad = Sadl(-1, bi=i, bap=self.sk_disrst[i])

                sgn_rsti = i
                sgn_rstp = self.sk_qspds[-2][7]
                sgn_rstdir = 1
                self.qsrstp.append((sgn_rsti, sgn_rstp, sgn_rstdir))
                self.sk_qsrstp.append(sgn_rstdir)
                self.sk_rstn.append(0)
                # self.sk_rstspl.append(self.sk_bsl[-2])
                # self.sk_rstsph.append(self.sk_bsh[-2])
                self.bscp = None
                newstpchain = Stepchain(1, i, self.sk_ckl[i], self.qsstpchain[-1].piockl)
                self.qsstpchain.append(newstpchain)
                self.sk_rstsph.append(self.qsstpchain[-1].revckls[-1][3])
                self.sk_rstspl.append(self.qsstpchain[-1].revckls[-1][4])
                # ---------------------------------------------------------------------------------------------------trdline
                self.ctp = Extrp(i, self.sk_high[i], 1)
                if self.cbp:
                    self.botms.append(self.cbp)
                    nrstsa = Rstsa(self.sk_open, self.sk_high, self.sk_low, self.sk_close, self.sk_atr, self.rstdir, self.cbp.ski, i)
                    rstna = self.uprstsas.keys()[-1]
                    self.uprstsas[rstna][rstna] = nrstsa
                    nrstsa.getrst()
                    nrstsa.uptmex(i)

                if len(self.botms) > 1:
                    pass
                    # self.new_supline(self.botms[-2], self.tops[-1], self.sk_open, self.sk_high, self.sk_low, self.sk_close, self.sk_volume, self.sk_time, self.sk_atr, self.sk_ckl, i)
                    if self.faset['rdl']:
                        newsupl = self.new_supline2(self.fid+'_rdl', self.sk_open, self.sk_high, self.sk_low, self.sk_close, self.sk_volume, self.sk_time, self.sk_atr,
                                                    self.sk_ckl, i, upski)
                        if newsupl:
                            self.suplines[newsupl.socna] = {'rdl': newsupl, 'mdl': None, 'mir': OrderedDict(), 'upl': OrderedDict(),
                                                            'dwl': OrderedDict()}
                            self.prebbl = self.crtbbl
                            self.crtbbl = newsupl
                            if self.faset['mdl']:
                                newtbl = self.new_supline3(self.fid+'_mdl', self.sk_open, self.sk_high, self.sk_low, self.sk_close, self.sk_volume, self.sk_time,
                                                           self.sk_atr, self.sk_ckl, i, upski)
                                if newtbl:
                                    self.suplines[newsupl.socna]['mdl'] = newtbl
                            self.boti = newsupl.mxi + 1
                if len(self.tops) > 1:
                    pass
                    if False and self.tops[-2].skp > self.tops[-2].skp:
                        self.new_resline(self.fid+'_mdl', self.tops[-2], self.botms[-1], self.sk_open, self.sk_high, self.sk_low, self.sk_close, self.sk_volume,
                                         self.sk_time, self.sk_atr, self.sk_ckl, i, upski)

            elif len(self.sk_qspds) > 1 and self.sk_qspds[-1][2] < 0 and self.sk_qspds[-2][2] > 0:  # 向下转换
                self.rstdir = -1
                self.sads['sd_' + str(i)] = []
                self.dwrstsas['dwr_' + str(i)] = OrderedDict()
                self.crtsad = None
                self.tepsad = Sadl(1, bi=i, bap=self.sk_disrst[i])

                sgn_rsti = i
                sgn_rstp = self.sk_qspds[-2][7]
                sgn_rstdir = -1
                self.qsrstp.append((sgn_rsti, sgn_rstp, sgn_rstdir))
                self.sk_qsrstp.append(sgn_rstdir)
                self.sk_rstn.append(0)
                # self.sk_rstspl.append(self.sk_bsl[-2])
                # self.sk_rstsph.append(self.sk_bsh[-2])
                self.bscp = None
                newstpchain = Stepchain(-1, i, self.sk_ckl[i], self.qsstpchain[-1].piockl)
                self.qsstpchain.append(newstpchain)
                self.sk_rstspl.append(self.qsstpchain[-1].revckls[-1][4])
                self.sk_rstsph.append(self.qsstpchain[-1].revckls[-1][3])
                # ---------------------------------------------------------------------------------------------------trdline
                self.cbp = Extrp(i, self.sk_low[i], -1)
                if self.ctp:
                    self.tops.append(self.ctp)
                    nrstsa = Rstsa(self.sk_open, self.sk_high, self.sk_low, self.sk_close, self.sk_atr, self.rstdir, self.ctp.ski, i)
                    rstna = self.dwrstsas.keys()[-1]
                    self.dwrstsas[rstna][rstna] = nrstsa
                    nrstsa.getrst()
                    nrstsa.uptmex(i)

                if len(self.tops) > 1:
                    pass
                    # self.new_resline(self.tops[-2], self.botms[-1], self.sk_open, self.sk_high, self.sk_low, self.sk_close, self.sk_volume, self.sk_time, self.sk_atr, self.sk_ckl, i)
                    if self.faset['rdl']:
                        newresl = self.new_resline2(self.fid+'_rdl', self.sk_open, self.sk_high, self.sk_low, self.sk_close, self.sk_volume, self.sk_time, self.sk_atr,
                                                    self.sk_ckl, i, upski)
                        if newresl:
                            self.reslines[newresl.socna] = {'rdl': newresl, 'mdl': None, 'mir': OrderedDict(), 'upl': OrderedDict(),
                                                            'dwl': OrderedDict()}
                            self.prettl = self.crtttl
                            self.crtttl = newresl
                            if self.faset['mdl']:
                                newtbl = self.new_resline3(self.fid+'_mdl', self.sk_open, self.sk_high, self.sk_low, self.sk_close, self.sk_volume, self.sk_time,
                                                           self.sk_atr, self.sk_ckl, i, upski)
                                if newtbl:
                                    self.reslines[newresl.socna]['mdl'] = newtbl
                            self.topi = newresl.mxi + 1

                if len(self.botms) > 1:
                    pass
                    if False and self.botms[-2].skp < self.botms[-2].skp:
                        self.new_supline(self.fid+'_mdl', self.botms[-2], self.tops[-1], self.sk_open, self.sk_high, self.sk_low, self.sk_close, self.sk_volume,
                                         self.sk_time, self.sk_atr, self.sk_ckl, i, upski, upski)
            else:
                self.sk_qsrstp.append(0)
                if len(self.qsstpchain) > 0:
                    self.qsstpchain[-1].updatestep(i, self.sk_ckl[i])
                    self.sk_rstn.append(len(self.qsstpchain[-1].revckls) - 1)

                    if self.sk_rstn[-1] > 0 and self.sk_rstn[-1] > self.sk_rstn[-2]:  # 发生步进
                        if len(self.botms) > 1 and self.qsstpchain[-1].stpdir > 0 and self.ctp:
                            pass
                            # self.new_supline(self.botms[-2], self.ctp , self.sk_open, self.sk_high, self.sk_low, self.sk_close, self.sk_volume, self.sk_time, self.sk_atr, i)
                        elif len(self.tops) > 1 and self.qsstpchain[-1].stpdir < 0 and self.cbp:
                            pass
                            # self.new_resline(self.tops[-2], self.cbp, self.sk_open, self.sk_high, self.sk_low, self.sk_close, self.sk_volume, self.sk_time, self.sk_atr, i)

                    if self.qsstpchain[-1].stpdir > 0:
                        self.sk_rstsph.append(self.qsstpchain[-1].revckls[-1][3])
                        self.sk_rstspl.append(self.qsstpchain[-1].revckls[-1][4])
                    else:
                        self.sk_rstsph.append(self.qsstpchain[-1].revckls[-1][3])
                        self.sk_rstspl.append(self.qsstpchain[-1].revckls[-1][4])
                else:
                    self.sk_rstn.append(0)
                    self.sk_rstsph.append(self.sk_close[i])
                    self.sk_rstspl.append(self.sk_close[i])

                if self.bsbj != 0:
                    # self.sk_rstspl.append(self.sk_close[i])
                    # self.sk_rstsph.append(self.sk_close[i])
                    # self.sk_rstn.append(self.sk_rstn[-1]+1)
                    self.bscp = None
                else:
                    pass
                    # self.sk_rstn.append(self.sk_rstn[-1])
                    # self.sk_rstspl.append(self.sk_rstspl[-1])
                    # self.sk_rstsph.append(self.sk_rstsph[-1])

                if self.rstdir > 0:
                    if len(self.uprstsas) > 0 and len(self.uprstsas.values()[-1].values()) > 0:
                        self.uprstsas.values()[-1].values()[-1].uptmex(i)
                elif self.rstdir < 0:
                    if len(self.dwrstsas) > 0 and len(self.dwrstsas.values()[-1].values()):
                        self.dwrstsas.values()[-1].values()[-1].uptmex(i)

            if self.faset['sal'] and self.sads:
                sadlist = self.sads.values()[-1]
                sad1 = None
                sad2 = None
                six = 0
                atr = self.sk_atr[i]
                if len(sadlist) > 0:
                    if sadlist[-1].ei:
                        sad2 = sadlist[-1]
                        six = len(sadlist) - 1
                        if len(sadlist) > 1:
                            sad1 = sadlist[-2]
                    elif len(sadlist) > 1:
                        sad2 = sadlist[-2]
                        six = len(sadlist) - 2
                        if len(sadlist) > 2:
                            sad1 = sadlist[-3]
                if sad2:
                    salna = self.fid + '_' + self.sads.keys()[-1] + '_' + str(six)
                    if salna not in self.sadlines or sad2.chg > 0:
                        sad2.chg = 0
                        if not sad1:
                            if sad2.dwup > 0 and len(self.tops) > 0:
                                sbi = self.tops[-1].ski
                                sbp = self.tops[-1].skp
                            elif sad2.dwup < 0 and len(self.botms) > 0:
                                sbi = self.botms[-1].ski
                                sbp = self.botms[-1].skp
                            else:
                                sbi = None
                                sbp = None
                        else:
                            sbi = sad1.mi
                            sbp = sad1.mp
                        if sbi:
                            rkp = max(self.sk_open[sad2.mi + 1], self.sk_close[sad2.mi + 1]) if sad2.dwup > 0 else min(self.sk_open[sad2.mi + 1],
                                                                                                                       self.sk_close[sad2.mi + 1])
                            newsal = getsaline2(salna, sbi, sbp, sad2, rkp, sbi, self.sk_time, atr, i, upski)
                            if newsal:
                                newsal.uptsklsta(self.sk_open, self.sk_high, self.sk_low, self.sk_close, self.sk_atr, self.sk_ckl, i)
                                self.sadlines[salna] = newsal
            if len(self.sadlines) > 0:
                crtsal = self.sadlines.values()[-1]
                crtsal.uptsklsta(self.sk_open, self.sk_high, self.sk_low, self.sk_close, self.sk_atr, self.sk_ckl, i)
                self.skatsel.uptsta(crtsal, i)
            else:
                crtsal = None
            if len(self.sadlines) > 1:
                presal = self.sadlines.values()[-2]
                presal.uptsklsta(self.sk_open, self.sk_high, self.sk_low, self.sk_close, self.sk_atr, self.sk_ckl, i)
                self.skatsel.uptsta(presal, i)
            else:
                presal = None

            # -------------集中更新tdls与sk的位置状态----------------------------------------------
            # 只更新最新的3组tdl
            supls = self.suplines.keys()
            for tdlna in supls[-3:]:
                bbls = self.suplines[tdlna]
                rdl = bbls['rdl']
                mdl = bbls['mdl']
                upls = bbls['upl']
                mirs = bbls['mir']

                rdl.uptsklsta(self.sk_open, self.sk_high, self.sk_low, self.sk_close, self.sk_atr, self.sk_ckl, i)
                self.skatsel.uptsta(rdl, i)
                if not mdl:
                    continue
                mdl.uptsklsta(self.sk_open, self.sk_high, self.sk_low, self.sk_close, self.sk_atr, self.sk_ckl, i)
                self.skatsel.uptsta(mdl, i)
                if not self.faset['upl']:
                    continue
                if mdl.upsmdi:
                    uplna = tdlna + '_up_' + str(mdl.upsmdi)
                    if uplna not in upls:
                        mdi = mdl.upsmdi
                        mp = mdl.extendp(mdi)
                        mdp = mdl.upsmdp
                        ak = mdl.ak
                        atr = self.sk_atr[i]
                        upl = getasline(uplna, mdi, mp, mdp, ak, self.sk_time, atr, i)
                        if upl:
                            upls[uplna] = upl
                            upl.uptsklsta(self.sk_open, self.sk_high, self.sk_low, self.sk_close, self.sk_atr, self.sk_ckl, i)
                toaddupl = {}
                for upl in upls.values():
                    upl.uptsklsta(self.sk_open, self.sk_high, self.sk_low, self.sk_close, self.sk_atr, self.sk_ckl, i)
                    if upl.upsmdi:
                        nuplna = tdlna + '_up_' + str(upl.upsmdi)
                        if nuplna in upls or nuplna in toaddupl:
                            continue
                        mdi = upl.upsmdi
                        mp = upl.extendp(mdi)
                        mdp = upl.upsmdp
                        ak = upl.ak
                        atr = self.sk_atr[i]
                        nupl = getasline(nuplna, mdi, mp, mdp, ak, self.sk_time, atr, i)
                        if nupl:
                            toaddupl[nuplna] = nupl
                            nupl.uptsklsta(self.sk_open, self.sk_high, self.sk_low, self.sk_close, self.sk_atr, self.sk_ckl, i)

                for nuplna, nupl in toaddupl.iteritems():
                    upls[nuplna] = nupl
                    nupl.uptsklsta(self.sk_open, self.sk_high, self.sk_low, self.sk_close, self.sk_atr, self.sk_ckl, i)
                # ---------------------------
                if not self.faset['mir']:
                    continue
                mirl = mirs.values()[-1] if mirs else None
                miri = None
                mirp = None
                for upl in upls.values():
                    if upl.dwmdis:
                        nmdi = upl.dwmdis[-1]
                        nmdp = self.sk_low[nmdi]
                        if not mirp or mirp < nmdp:
                            miri = nmdi
                            mirp = nmdp
                if miri:
                    if not mirl:
                        # nmrlna = tdlna + '_mr_' + str(miri)
                        # mri = miri
                        # mrp = mirp
                        # ak = mdl.ak
                        # atr = self.sk_atr[i]
                        # nmrl = getmrline1(nmrlna, mri, mrp, ak, self.sk_time, atr, i)
                        # if nmrl:
                        #     nmrl.uptsklsta(self.sk_open, self.sk_high, self.sk_low, self.sk_close, self.sk_atr, self.sk_ckl, i)
                        #     mirl = nmrl
                        #     mirs[nmrlna] = nmrl
                        nmrlna = tdlna + '_mr_' + str(miri)
                        if miri < i:
                            mbi = mdl.fbi
                            mbp = self.sk_low[mbi]
                            fbi = miri
                            ski = miri
                            skp = min(self.sk_open[ski], self.sk_close[ski])
                            lkp = min(self.sk_open[ski - 1], self.sk_close[ski - 1])
                            rkp = min(self.sk_open[ski + 1], self.sk_close[ski + 1])
                            sdpt = getsdi(mbi, mbp, fbi, skp, lkp, rkp, 1)
                            if sdpt:
                                mri = sdpt[0]
                                mrp = sdpt[1]
                                atr = self.sk_atr[i]
                                nmrl = getmrline2(nmrlna, mbi, mbp, mri, mrp, fbi, self.sk_time, atr, i)
                                if nmrl:
                                    nmrl.uptsklsta(self.sk_open, self.sk_high, self.sk_low, self.sk_close, self.sk_atr, self.sk_ckl, i)
                                    mirl = nmrl
                                    mirs[nmrlna] = nmrl
                    elif miri != mirl.fbi:
                        nmrlna = tdlna + '_mr_' + str(miri)
                        if miri < i:
                            mbi = mirl.fbi
                            mbp = self.sk_low[mbi]
                            fbi = miri
                            ski = miri
                            skp = min(self.sk_open[ski], self.sk_close[ski])
                            lkp = min(self.sk_open[ski - 1], self.sk_close[ski - 1])
                            rkp = min(self.sk_open[ski + 1], self.sk_close[ski + 1])
                            sdpt = getsdi(mbi, mbp, fbi, skp, lkp, rkp, 1)
                            if sdpt:
                                mri = sdpt[0]
                                mrp = sdpt[1]
                                atr = self.sk_atr[i]
                                nmrl = getmrline2(nmrlna, mbi, mbp, mri, mrp, fbi, self.sk_time, atr, i)
                                if nmrl:
                                    nmrl.uptsklsta(self.sk_open, self.sk_high, self.sk_low, self.sk_close, self.sk_atr, self.sk_ckl, i)
                                    mirl = nmrl
                                    mirs[nmrlna] = nmrl

                if mirl:
                    mirl.uptsklsta(self.sk_open, self.sk_high, self.sk_low, self.sk_close, self.sk_atr, self.sk_ckl, i)

            resls = self.reslines.keys()
            for tdlna in resls[-3:]:
                ttls = self.reslines[tdlna]
                rdl = ttls['rdl']
                mdl = ttls['mdl']
                dwls = ttls['dwl']
                mirs = ttls['mir']
                rdl.uptsklsta(self.sk_open, self.sk_high, self.sk_low, self.sk_close, self.sk_atr, self.sk_ckl, i)
                self.skatsel.uptsta(rdl, i)
                if not mdl:
                    continue
                mdl.uptsklsta(self.sk_open, self.sk_high, self.sk_low, self.sk_close, self.sk_atr, self.sk_ckl, i)
                self.skatsel.uptsta(mdl, i)
                if not self.faset['dwl']:
                    continue
                if mdl.dwsmdi:
                    dwlna = tdlna + '_dw_' + str(mdl.dwsmdi)
                    if dwlna not in dwls:
                        mdi = mdl.dwsmdi
                        mp = mdl.extendp(mdi)
                        mdp = mdl.dwsmdp
                        ak = mdl.ak
                        atr = self.sk_atr[i]
                        dwl = getasline(dwlna, mdi, mp, mdp, ak, self.sk_time, atr, i)
                        if dwl:
                            dwls[dwlna] = dwl
                            dwl.uptsklsta(self.sk_open, self.sk_high, self.sk_low, self.sk_close, self.sk_atr, self.sk_ckl, i)
                toadddwl = {}
                for dwl in dwls.values():
                    dwl.uptsklsta(self.sk_open, self.sk_high, self.sk_low, self.sk_close, self.sk_atr, self.sk_ckl, i)
                    if dwl.dwsmdi:
                        ndwlna = tdlna + '_dw_' + str(dwl.dwsmdi)
                        if ndwlna in dwls or ndwlna in toadddwl:
                            continue
                        mdi = dwl.dwsmdi
                        mp = dwl.extendp(mdi)
                        mdp = dwl.dwsmdp
                        ak = dwl.ak
                        atr = self.sk_atr[i]
                        ndwl = getasline(ndwlna, mdi, mp, mdp, ak, self.sk_time, atr, i)
                        if ndwl:
                            toadddwl[ndwlna] = ndwl
                            ndwl.uptsklsta(self.sk_open, self.sk_high, self.sk_low, self.sk_close, self.sk_atr, self.sk_ckl, i)

                for ndwlna, ndwl in toadddwl.iteritems():
                    dwls[ndwlna] = ndwl
                    ndwl.uptsklsta(self.sk_open, self.sk_high, self.sk_low, self.sk_close, self.sk_atr, self.sk_ckl, i)
                # ---------------------------
                if not self.faset['mir']:
                    continue
                miri = None
                mirp = None
                mirl = mirs.values()[-1] if mirs else None
                for dwl in dwls.values():
                    if dwl.upmdis:
                        nmdi = dwl.upmdis[-1]
                        nmdp = self.sk_high[nmdi]
                        if not mirp or mirp > nmdp:
                            miri = nmdi
                            mirp = nmdp
                if miri:
                    if not mirl:
                        # nmrlna = tdlna + '_mr_' + str(miri)
                        # mri = miri
                        # mrp = mirp
                        # ak = mdl.ak
                        # atr = self.sk_atr[i]
                        # nmrl = getmrline1(nmrlna, mri, mrp, ak, self.sk_time, atr, i)
                        # if nmrl:
                        #     nmrl.uptsklsta(self.sk_open, self.sk_high, self.sk_low, self.sk_close, self.sk_atr, self.sk_ckl, i)
                        #     mirl = nmrl
                        #     mirs[nmrlna] = nmrl
                        nmrlna = tdlna + '_mr_' + str(miri)
                        if miri < i:
                            mbi = mdl.fbi
                            mbp = self.sk_high[mbi]
                            fbi = miri
                            ski = miri
                            skp = max(self.sk_open[ski], self.sk_close[ski])
                            lkp = max(self.sk_open[ski - 1], self.sk_close[ski - 1])
                            rkp = max(self.sk_open[ski + 1], self.sk_close[ski + 1])
                            sdpt = getsdi(mbi, mbp, fbi, skp, lkp, rkp, -1)
                            if sdpt:
                                mri = sdpt[0]
                                mrp = sdpt[1]
                                atr = self.sk_atr[i]
                                nmrl = getmrline2(nmrlna, mbi, mbp, mri, mrp, fbi, self.sk_time, atr, i)
                                if nmrl:
                                    nmrl.uptsklsta(self.sk_open, self.sk_high, self.sk_low, self.sk_close, self.sk_atr, self.sk_ckl, i)
                                    mirl = nmrl
                                    mirs[nmrlna] = nmrl
                    elif miri != mirl.fbi:
                        nmrlna = tdlna + '_mr_' + str(miri)
                        if miri < i:
                            mbi = mirl.fbi
                            mbp = self.sk_high[mbi]
                            fbi = miri
                            ski = miri
                            skp = max(self.sk_open[ski], self.sk_close[ski])
                            lkp = max(self.sk_open[ski - 1], self.sk_close[ski - 1])
                            rkp = max(self.sk_open[ski + 1], self.sk_close[ski + 1])
                            sdpt = getsdi(mbi, mbp, fbi, skp, lkp, rkp, -1)
                            if sdpt:
                                mri = sdpt[0]
                                mrp = sdpt[1]
                                atr = self.sk_atr[i]
                                nmrl = getmrline2(nmrlna, mbi, mbp, mri, mrp, fbi, self.sk_time, atr, i)
                                if nmrl:
                                    nmrl.uptsklsta(self.sk_open, self.sk_high, self.sk_low, self.sk_close, self.sk_atr, self.sk_ckl, i)
                                    mirl = nmrl
                                    mirs[nmrlna] = nmrl
                if mirl:
                    mirl.uptsklsta(self.sk_open, self.sk_high, self.sk_low, self.sk_close, self.sk_atr, self.sk_ckl, i)
            # -----------------------------------------------------------------------------------------------------------------
            #-----------------------------------------------------------------------------------------------------------------因子输出

            if self.rstdir > 0 and len(self.uprstsas) > 0 and len(self.uprstsas.values()[-1].values()) > 0:
                self.sk_alp1.append(self.uprstsas.values()[-1].values()[-1].mexp)
            else:
                self.sk_alp1.append(self.sk_alp1[-1])
            if self.rstdir < 0 and len(self.dwrstsas) > 0 and len(self.dwrstsas.values()[-1].values()) > 0:
                self.sk_dlp1.append(self.dwrstsas.values()[-1].values()[-1].mexp)
            else:
                self.sk_dlp1.append(self.sk_dlp1[-1])

            if crtsal:
                self.sk_sal.append(crtsal.extp)
                self.ak_sal.append(crtsal.ak)
            else:
                self.sk_sal.append(np.nan)
                self.ak_sal.append(np.nan)

            if self.crtbbl:
                # if str(self.sk_time[i])[:10] == '2016-06-27':
                #     print 'sta:', self.crtbbl.rsta
                ydbblrsta = self.crtbbl.rsta
                tdbblrsta = self.crtbbl.rsta
                if None and ydbblrsta % 3 == 2 and tdbblrsta % 3 == 0 and tdbblrsta != ydbblrsta:  # None and
                    if len(self.botms) > 1 and self.ctp:
                        pass
                        self.new_supline(self.botms[-2], self.ctp, self.sk_open, self.sk_high, self.sk_low, self.sk_close, self.sk_volume,
                                         self.sk_time, self.sk_atr, self.sk_ckl, i, upski)
                        if self.crtbbl:
                            self.crtbbl.uptsklsta(self.sk_open, self.sk_high, self.sk_low, self.sk_close, self.sk_atr, self.sk_ckl, i)

                if self.crtbbl.crsp:
                    self.sk_bbl.append(self.crtbbl.extp)
                    self.ak_bbl.append(self.crtbbl.ak)
                    tdlna = self.crtbbl.socna
                    bbls = self.suplines[tdlna]
                    rdl = bbls['rdl']
                    mdl = bbls['mdl']
                    upls = bbls['upl'].values()

                    if mdl:
                        self.sk_obbl.append(mdl.extp)
                        self.ak_obbl.append(mdl.ak)
                    else:
                        self.sk_obbl.append(np.nan)
                        self.ak_obbl.append(np.nan)

                    mirs = self.suplines[tdlna]['mir']
                    mirl = mirs.values()[-1] if mirs else None
                    if mirl:
                        self.sk_alp2.append(mirl.extp)
                    else:
                        self.sk_alp2.append(np.nan)
                else:
                    self.sk_bbl.append(np.nan)
                    self.ak_bbl.append(np.nan)
                    self.sk_obbl.append(np.nan)
                    self.ak_obbl.append(np.nan)
                    self.sk_alp2.append(np.nan)
            else:
                self.sk_bbl.append(np.nan)
                self.ak_bbl.append(np.nan)
                self.sk_obbl.append(np.nan)
                self.ak_obbl.append(np.nan)
                self.sk_alp2.append(np.nan)

            if self.crtttl:
                ydttlrsta = self.crtttl.rsta
                tdttlrsta = self.crtttl.rsta
                if None and ydttlrsta % 3 == 2 and tdttlrsta % 3 == 0 and tdttlrsta != ydttlrsta:  # None and
                    if len(self.tops) > 1 and self.cbp:
                        pass
                        self.new_resline(self.tops[-2], self.cbp, self.sk_open, self.sk_high, self.sk_low, self.sk_close, self.sk_volume,
                                         self.sk_time, self.sk_atr, self.sk_ckl, i, upski)
                        if self.crtttl:
                            self.crtttl.uptsklsta(self.sk_open, self.sk_high, self.sk_low, self.sk_close, self.sk_atr, self.sk_ckl, i)

                if self.crtttl.crsp:
                    self.sk_ttl.append(self.crtttl.extp)
                    self.ak_ttl.append(self.crtttl.ak)
                    tdlna = self.crtttl.socna
                    ttls = self.reslines[tdlna]
                    rdl = ttls['rdl']
                    mdl = ttls['mdl']
                    dwls = ttls['dwl'].values()
                    # if len(dwls) > 0:
                    #     self.sk_dlp1.append(dwls[-1].extp)
                    # else:
                    #     self.sk_dlp1.append(np.nan)

                    if mdl:
                        self.sk_ottl.append(mdl.extp)
                        self.ak_ottl.append(mdl.ak)
                    else:
                        self.sk_ottl.append(np.nan)
                        self.ak_ottl.append(np.nan)

                    mirs = self.reslines[tdlna]['mir']
                    mirl = mirs.values()[-1] if mirs else None
                    if mirl:
                        self.sk_dlp2.append(mirl.extp)
                    else:
                        self.sk_dlp2.append(np.nan)

                else:
                    self.sk_ttl.append(np.nan)
                    self.ak_ttl.append(np.nan)
                    self.sk_ottl.append(np.nan)
                    self.ak_ottl.append(np.nan)
                    self.sk_dlp2.append(np.nan)

            else:
                self.sk_ttl.append(np.nan)
                self.ak_ttl.append(np.nan)
                self.sk_ottl.append(np.nan)
                self.ak_ottl.append(np.nan)
                self.sk_dlp2.append(np.nan)


            # ----------------------生成集成信号----
            # ------------------------------------------------------------------------
            # iski = i
            # ihigh = self.sk_high[i]
            # if '2014-11-18' in self.crtidtm:
            #     print 'iski:', i, 'idtm:', self.crtidtm, ' idate:', self.crtidate
            # chkvar = self.crtsad
            # chkobj = self.dwrstsas
            # -----------------------------------------------------------------------
            if self.subrst:
                if '2010-07-27' in self.crtidtm:
                    ihigh = self.sk_high[i]
                    print 'iski:', i, 'idtm:', self.crtidtm, ' idate:', self.crtidate, 'ihigh:', ihigh

                if np.isnan(self.sk_sudc[i]):
                    dix = self.upix[-1]
                    self.upix.append(dix)
                    self.mosi += 1
                else:
                    dix = self.subrst.cal_next(upidtm=self.crtidtm, upski=i)
                    self.upix.append(dix)
                    self.mosi = 0

                if len(self.subrst.sadlines) > 0:
                    subcrtsal = self.subrst.sadlines.values()[-1]
                    self.skatetl.uptsta(subcrtsal, i, self.upix, self.mosi)
                if len(self.subrst.sadlines) > 1:
                    subpresal = self.subrst.sadlines.values()[-2]
                    self.skatetl.uptsta(subpresal, i, self.upix, self.mosi)

                supls = self.subrst.suplines.keys()
                for tdlna in supls[-3:]:
                    bbls = self.subrst.suplines[tdlna]
                    rdl = bbls['rdl']
                    mdl = bbls['mdl']
                    upls = bbls['upl']
                    mirs = bbls['mir']
                    if rdl:
                        self.skatetl.uptsta(rdl, i, self.upix, self.mosi)
                    if mdl:
                        self.skatetl.uptsta(mdl, i, self.upix, self.mosi)

                resls = self.subrst.reslines.keys()
                for tdlna in resls[-3:]:
                    ttls = self.subrst.reslines[tdlna]
                    rdl = ttls['rdl']
                    mdl = ttls['mdl']
                    dwls = ttls['dwl']
                    mirs = ttls['mir']
                    if rdl:
                        self.skatetl.uptsta(rdl, i, self.upix, self.mosi)
                    if mdl:
                        self.skatetl.uptsta(mdl, i, self.upix, self.mosi)
                if '2010-08-12' in self.crtidtm or i == 1088:
                    print 'iski:', i, 'idtm:', self.crtidtm, ' idate:', self.crtidate
            # ------------------------------------------------------------------------
            iski = i
            ihigh = self.sk_high[i]
            if '2010-08-12' in self.crtidtm or i ==1088:
                print 'iski:', i, 'idtm:', self.crtidtm, ' idate:', self.crtidate
            chkvar = self.crtsad
            chkobj = self.dwrstsas
            # -----------------------------------------------------------------------

            if self.TSBT:
                mafs = {'rstdir': self.rstdir, 'sals': self.sadlines, 'bbls': self.suplines, 'ttls': self.reslines, 'upsas': self.uprstsas, 'dwsas': self.dwrstsas}
                if self.subrst is None:
                    sufs = None
                else:
                    sufs = {'rstdir': self.subrst.rstdir, 'sals': self.subrst.sadlines, 'bbls': self.subrst.suplines, 'ttls': self.subrst.reslines,
                            'upsas': self.subrst.uprstsas, 'dwsas': self.subrst.dwrstsas}
                self.intedsgn = Intsgnbs(self.tdkopset, self.skatsel, self.skatetl, mafs, sufs,  self.upix, self.mosi)
                self.intedsgn.sesgnbs(i)
                self.intedsgn.etsgnbs(i)
                self.TSBT.sgntotrd(i, self.intedsgn)



        return self.crtski
    # ------------------------------------------------------------------------
    def colfas(self):
        self.quotes['qrst'] = self.sk_qsrstp
        self.quotes['qsh'] = self.sk_qsh
        self.quotes['qsl'] = self.sk_qsl
        self.quotes['zsh'] = self.sk_zsh
        self.quotes['zsl'] = self.sk_zsl
        self.quotes['qswr'] = self.sk_qswr
        self.quotes['rsl'] = self.sk_rsl
        self.quotes['itp'] = self.sk_itp

        self.quotes['disrst'] = self.sk_disrst
        self.quotes['sal'] = self.sk_sal
        self.quotes['brdl'] = self.sk_bbl
        self.quotes['trdl'] = self.sk_ttl
        self.quotes['bmdl'] = self.sk_obbl
        self.quotes['tmdl'] = self.sk_ottl

        self.quotes['ak_sal'] = self.ak_sal
        self.quotes['ak_brdl'] = self.ak_bbl
        self.quotes['ak_trdl'] = self.ak_ttl
        self.quotes['ak_bmdl'] = self.ak_obbl
        self.quotes['ak_tmdl'] = self.ak_ottl

        self.quotes['alp1'] = self.sk_alp1
        self.quotes['alp2'] = self.sk_alp2
        # self.quotes['alp3'] = self.sk_alp3
        # self.quotes['alp4'] = self.sk_alp4
        # self.quotes['alp5'] = self.sk_alp5
        # self.quotes['alp6'] = self.sk_alp6
        self.quotes['dlp1'] = self.sk_dlp1
        self.quotes['dlp2'] = self.sk_dlp2
        # self.quotes['dlp3'] = self.sk_dlp3
        # self.quotes['dlp4'] = self.sk_dlp4
        # self.quotes['dlp5'] = self.sk_dlp5
        # self.quotes['dlp6'] = self.sk_dlp6

        self.quotes['rstn'] = self.sk_rstn
        self.quotes['rstspl'] = self.sk_rstspl
        self.quotes['rstsph'] = self.sk_rstsph

        self.quotes['bsl'] = self.sk_bsl
        self.quotes['bsh'] = self.sk_bsh

        self.quotes['sk_zs1c'] = self.sk_zs1c
        self.quotes['sk_zs1a'] = self.sk_zs1a
        self.quotes['sk_zs2c'] = self.sk_zs2c
        self.quotes['sk_zs2a'] = self.sk_zs2a
        self.quotes['sk_qs1c'] = self.sk_qs1c
        self.quotes['sk_qs1a'] = self.sk_qs1a
        self.quotes['sk_qs2c'] = self.sk_qs2c
        self.quotes['sk_qs2a'] = self.sk_qs2a
        # self.quotes['sk_zsrpt'] = self.sk_zsrpt
        # self.quotes['sk_qsrpt'] = self.sk_qsrpt

        afc = []
        for col in self.quotes.columns:
            if '_d' in col and 'ak_' + col in self.quotes.columns:
                afc.append(col)

        for col in afc:
            self.quotes.loc[:,'ak_'+col].fillna(method='pad', inplace=True)
        if len(afc)>0:
            fidtm = self.quotes.index[0]
            for idtm in self.quotes.index[1:]:
                for col in afc:
                    if np.isnan(self.quotes.loc[idtm, col]):
                        self.quotes.loc[idtm, col] = self.quotes.loc[fidtm, col] + self.quotes.loc[fidtm, 'ak_'+col]*1.0/self.quotes.loc[fidtm, 'dkcn']
                fidtm = idtm
        self.quotes.fillna(method='pad', inplace=True)