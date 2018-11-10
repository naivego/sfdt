# -*- coding: cp936 -*-
__author__ = 'naivego'

'''
  2017.1.17 gengx
'''

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import csv
import datetime
#---------------------------------------------
gpath=r'D:\py\futs\csvf'
wpath=r'D:\pythonfs\profut\csvf'
symbol="000001.SH"    #  "IFC1.ZJ"   # "CU01.SQ"  #    "RB.SQ"  #
outto_zbcsvfile=gpath+r'\zbabs_'+symbol+'.csv'
datas_csvfile=gpath+r'\dat_'+symbol+'.csv'
qspoutto_zbcsvfile=gpath+r'\zbqspabs_'+symbol+'.csv'

bgni=3000
endi=3990
dtmbgn="2016/04/15 09:45:00"
dtmend="2017/01/17 15:00:00"
avgski=1
avgsk_cn=30
maxbarback=20

#rsts
decsn=2  #小数位数
syb_open=symbol+'.open'
syb_high=symbol+'.high'
syb_low=symbol+'.low'
syb_close=symbol+'.close'
syb_volume=symbol+'.volume'
syb_oi=symbol+'.oi'
syb_factor=symbol+'.factor'

#----------------------------------------------
datas=pd.read_csv(datas_csvfile,index_col='datetime', parse_dates=True)  #
dask=datas.loc[dtmbgn:dtmend, [syb_open, syb_high, syb_low, syb_close,syb_volume, syb_oi,syb_factor]]
sk_factor=dask[syb_factor]
sk_open=(dask[syb_open]/sk_factor).apply(lambda x: round(x,decsn))
sk_high=(dask[syb_high]/sk_factor).apply(lambda x: round(x,decsn))
sk_low=(dask[syb_low]/sk_factor).apply(lambda x: round(x,decsn))
sk_close=(dask[syb_close]/sk_factor).apply(lambda x: round(x,decsn))
sk_volume=dask[syb_volume]
sk_oi=dask[syb_oi]


#----------------------------------------------
sk_ckl=[]  # 与ck同步，由元组（ckli,cksdh,cksdl）构成的队列，记录当前的sk链所包括的sk数目和实体部分的区间
sk_ckdtpst=0.2  #0.2倍平均涨幅作为涨跌柱子的公差
ckls=[]   # 与ckl线段列表，由列表[cklbi,cklei,cklbp,cklep,cklsd]构成,记录线段的起点位置、终点位置、起点价格、终点价格、长度
detsuc=5  #strong上升链构成上涨反转的链长 =detsuc*avgski
detsdc=-5 #strong下降链构成下降反转的链长 =detsdc*avgski
sk_cklsm=[] #在sk序列框架下对ckls结构进行描述，指示当前的sk处于ckls结构中的水平 (ckltp, ickls)
'''
   ckltp                             ickls
   1---处于wuckl weak up ckl         (ickls0,)
   2---处于suckl strong up ckl       (ickls0,)
   3---处于nuckl N-S up ckl          (ickls1,ickls2,ickls0)
   -1--处于wdckl weak down ckl       (ickls0,)
   -2--处于sdckl strong down ckl     (ickls0,)
   -3--处于ndckl N-S down ckl        (ickls1,ickls2,ickls0)

'''
nsckls=[]  #在ckls基础上，将相邻的可以聚合的n元聚合起来构成，由列表由[nsckltp，insckls]组成 insckls=[ickls0,ickls1,ickls2...]构成，当形成新的局部n元时更新
nscklsedi=0 #最新段的nsckls处于ckls的第几号链上
#-----------------------------------------------
qspds=[] #趋势前沿列表 每段由[qsprti,nscklidx,nscklitp,qspbi,qspei,qspbsdp,qspesdp,qspbp,qspep]组成，来自于nsckls的波段
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
sk_qspds=[]

def ftpvalue(syb):
    if syb[:2].upper()=="IF": return 300
    elif syb[:2].upper()=="CU": return 5
    elif syb[:2].upper() == "RB": return 10
    else: return 1

class ftorder:  #期货订单
    # 定义基本属性
    symbol=""
    openi = 0 #开仓位置
    openp=0   #开仓价格
    slot=1    #开仓手数  正数-多头， 负数-空头
    closei= -1 #平仓位置 -1 未平仓
    closep=0  #平仓价格
    stplp=0   # 止损价位  0--未设止损
    tpftp=0   #目标价位   0--未设止盈
    ordtype=0  #订单类型： 0-市价单， 1-限价单， 2-stop单
    ordstate=0  #订单状态  -1：失效 0： 未成交  1： 已成交
    ordid = 0
    # 定义私有属性,私有属性在类外部无法直接进行访问
    # __weight = 0

    # 定义构造方法

    '''
    def __init__(self, syb="", opi=0, opp=0, slot=0, cdi=0, cdp=0, state=0,id=""):
        self.symbol= syb
        self.openi=opi
        self.openp=opp
        self.slot=slot
        self.closei=cdi
        self.closep=cdp
        self.ordstate=state
        self.ordid=id
    '''

    def __init__(self):
        self.ordstate=0

    def ordopen(self, syb, opi, opp, slot, ordtyp, stplp, tpftp, sgnid):   #开仓
        self.symbol= syb
        self.openi=opi
        self.openp=opp
        self.slot=slot
        self.ordtype=ordtyp
        self.stplp=stplp
        self.tpftp=tpftp
        self.ordid=sgnid

    def ordclose(self, cdi, cdp):    #平仓
        self.closei=cdi
        self.closep=cdp

    def setstpl(self, newstplp):
        self.stplp=newstplp
    def settpft(self, newtpftp):
        self.tpftp=newtpftp

    def getopl(self, isk): #计算在sk_i上的浮动盈亏
        if isk>=self.openi and isk<=self.closei :
            return ftpvalue(symbol)*(sk_close[isk]-self.openp)*self.slot
        else: return 0
    def getcpl(self, isk): #计算在sk_i上的平仓盈亏
        if self.closei>=0 :
            return ftpvalue(symbol) * (self.closep - self.openp) * self.slot
        else: return 0

    def chkordexit(self, ski, sk_op, sk_hp, sk_lp, sk_cp):  #检查止损止盈出场
        if self.closei>0: return 0 #已经出场
        if self.stplp>0 :
            if self.slot>0 : # 买单
                if sk_lp<=self.stplp: #止损
                    self.closei = ski
                    self.closep = self.stplp
                    return 1
            elif self.slot<0 : # 卖单
                if sk_hp>=self.stplp: #止损
                    self.closei = ski
                    self.closep = self.stplp
                    return 1

        if self.tpftp>0:
            if self.slot<0 : # 卖单
                if sk_lp<=self.tpftp: #止盈
                    self.closei = ski
                    self.closep = self.tpftp
                    return 1
            elif self.slot>0 : # 买单
                if sk_hp>=self.tpftp: #止盈
                    self.closei = ski
                    self.closep = self.tpftp
                    return 1
        return 0

    def chkordtrd(self, ski, sk_op, sk_hp, sk_lp, sk_cp):  #检查订单在当前 ski成交情况
        if self.openi>0 : return 0
        if self.ordtype==0 : #市价单
           self.openi=ski
           self.openp=sk_op
           return 1
        elif self.ordtype == 1 and self.openp>0  :  # 限价单
            if self.slot > 0:  # 买单
                if sk_lp <= self.openp:  #
                    self.openi = ski
                    return 1
            elif self.slot < 0:  # 卖单
                if sk_hp >= self.openp:  #
                    self.openi = ski
                    return 1

        elif self.ordtype == 2 and self.openp>0  :  # 止损单
            if self.slot > 0:  # 买单
                if sk_hp >= self.openp:  #
                    self.openi = ski
                    return 1
            elif self.slot < 0:  # 卖单
                if sk_lp <= self.openp:  #
                    self.openi = ski
                    return 1

        return 0

#---------------------------------------------信号部分全局变量
'''
   处理逻辑流程如下：
   1、在sk收盘时计算信号
   2、核算持仓在本sk的出场情况，包括止损和止盈
   3、核查是否撤销或修改未成交订单
   4、核算之前发出的未成交订单在本sk的成交情况，更新3大列表
   5、发送本sk产生的信号订单, 实际在下一个sk发送，包括 mktord, lmtord, stpord 三种类型

   订单信号的命名： ski+sgnname
'''
qsrstp=[]  #多空转换点 收盘突破前沿，趋势方向转化 (sgn_rsti, sgn_rstp, sgn_rstdir) 突破位置，突破价格，突破方向：1-向上， -1 向下
sgn_qspcl=[0.75,0.5]  #当趋势反转后，原趋势方向的单子在当前趋势前沿回撤一定幅度分别平仓
sgn_qspcv=[0.5,0]     # 降仓到相对于原趋势反转点处总持仓水平的比例

sgn_qskcl=[0.5,0.3,0] #当趋势反转后，当前趋势前沿回撤档位上分别开仓
sgn_qskcv=[0.5,0.8,1.0] #当趋势反转后，当前趋势前沿回撤档位上分别开仓量，累计加仓到标准持仓的水平
#-------------------------------------------------------------

#---------------------------------------------资金和仓位部分全局变量
bdcap=1000000   # 初始资金
sk_rtcap=[]     # 实时资产 在每根K按收盘价核算
sendords=[]     # 发出去的未成交的订单列表
posiords=[]     # 持仓， 已成交但未平仓订单列表
cldords=[]      # 已平仓订单列表
stdcv=1         # 标准持仓水平，根据实时资产计算
uselever=3      # 使用杠杆倍数

def sendmktord(syb, slot, sgnid):
    mktord=ftorder()
    mktord.symbol=syb
    mktord.slot=slot
    mktord.ordid=sgnid
    sendords.append(mktord)
    return mktord


def sendlmtord(syb, slot, lmtp, sgnid):
    lmtord=ftorder()
    lmtord.symbol=syb
    lmtord.slot=slot
    lmtord.openp=lmtp
    lmtord.ordid=sgnid
    sendords.append(lmtord)
    return lmtord

def sendstpord(syb, slot, stpp, sgnid):
    stpord=ftorder()
    stpord.symbol=syb
    stpord.slot=slot
    stpord.openp=stpp
    stpord.ordid=sgnid
    sendords.append(stpord)
    return stpord



#=========================================================================

def avgsk(i):  #注意：本函数是计算第i根sK之前的cn根柱子的平均柱子涨幅，要求i>0
    if i<=0 :return abs(sk_close[0]-sk_open[0])
    sumsk=abs(sk_close[0]-sk_open[0])
    bi=max(0,i-avgsk_cn)
    if bi==0: sumsk=abs(sk_close[0]-sk_open[0])
    else:sumsk=abs(sk_close[bi]-sk_close[bi-1])
    for idx in range(bi+1, i):  # bi+1--i
        sumsk+=abs(sk_close[idx]-sk_close[idx-1])
    return sumsk/(i-bi)
#print( avgsk(60))

def cklinit():
    if sk_close[0]>=sk_open[0] :
        ckli=1
        cksdh=sk_close[0]
        cksdl=sk_open[0]
    else:
        ckli=-1
        cksdl=sk_close[0]
        cksdh=sk_open[0]
    sk_ckl.append((ckli, cksdh, cksdl))

    #ckls=[]   # 与ckl线段列表，由列表[cklbi,cklei,cklbp,cklep,cklsd]构成,记录线段的起点、终点、长度
    cklbi=0
    cklei=0
    cklbp=sk_open[0]
    cklep=sk_close[0]
    cklsd=ckli*(cksdh-cksdl)
    ckls.append([cklbi, cklei,cklbp,cklep,cklsd])

    #sk_cklsm=[] #在sk序列框架下对ckls结构进行描述，指示当前的sk处于ckls结构中的水平 (ckltp, ickls)
    ckltp=ckli
    ickls0=tuple(ckls[-1])
    ickls=(ickls0,)
    sk_cklsm.append((ckltp, ickls))
    #print(0,sk_close.index[0],(ckli, round(cksdh,decsn), round(cksdl,decsn)))
    sk_qspds.append([0, 0, 0, 0, 0, sk_open[0], sk_close[0], sk_open[0], sk_close[0]])

    #---------------------初始资金
    sk_rtcap.append(bdcap)

    for i in range(1,sk_close.size):
        avgski=avgsk(i)
        if sk_ckl[i-1][0]>0 :
            if sk_close[i]>=sk_close[i-1]-sk_ckdtpst*avgski:
               ckli=sk_ckl[i-1][0]+1
               cksdh=max(sk_ckl[i-1][1],sk_close[i])
               cksdl=sk_ckl[i-1][2]
               sk_ckl.append((ckli, cksdh, cksdl))

               #更新 ckls
               ckls[-1][1]+=1
               ckls[-1][3]=cksdh
               ckls[-1][4]=cksdh-cksdl
            else:
               ckli=-1
               cksdh=sk_ckl[i-1][1]
               cksdl=sk_close[i]
               sk_ckl.append((ckli, cksdh, cksdl))

               #更新 ckls
               cklbi=i
               cklei=i
               cklbp=cksdh
               cklep=cksdl
               cklsd=cklep-cklbp
               ckls.append([cklbi, cklei, cklbp, cklep,cklsd])

        else:
            if sk_close[i]<=sk_close[i-1]+sk_ckdtpst*avgski:
               ckli=sk_ckl[i-1][0]-1
               cksdl=min(sk_ckl[i-1][2],sk_close[i])
               cksdh=sk_ckl[i-1][1]
               sk_ckl.append((ckli, cksdh, cksdl))
               #更新 ckls
               ckls[-1][1]+=1
               ckls[-1][3]=cksdl
               ckls[-1][4]=cksdl-cksdh

            else:
               ckli=1
               cksdl=sk_ckl[i-1][2]
               cksdh=sk_close[i]
               sk_ckl.append((ckli, cksdh, cksdl))

               #更新 ckls
               cklbi=i
               cklei=i
               cklbp=cksdl
               cklep=cksdh
               cklsd=cklep-cklbp
               ckls.append([cklbi, cklei, cklbp, cklep,cklsd])

        #print(i,sk_close.index[i],(ckli, round(cksdh,decsn), round(cksdl,decsn)))
        #sk_cklsm=[] #在sk序列框架下对ckls结构进行描述，指示当前的sk处于ckls结构中的水平 (ckltp, ickls)
        if len(ckls)>=3:
            ickls0=tuple(ckls[-1])
            ickls1=tuple(ckls[-2])
            ickls2=tuple(ckls[-3])
            if (ickls0[4]>0 and sk_cklsm[-1][0]>=3 ) or (ickls0[4]>0 and ickls0[3]>ickls1[2] and ickls1[3]>=ickls2[2]):
                # 3---处于nuckl N-S up ckl            (ickls0,ickls1,ickls2)
                ckltp=3
                ickls=(ickls0,ickls1,ickls2)
                sk_cklsm.append((ckltp, ickls))

                #更新nsckls=[]  由[nsckltp，insckls]组成 insckls=[insckls0,insckls1,insckls2...]
                if len(nsckls)<1 :
                    nsckltp=3
                    insckls0=ickls0
                    insckls1=ickls1
                    insckls2=ickls2
                    insckls=[insckls2,insckls1,insckls0]

                    for icklsx in ckls[0:-3]:
                        if icklsx[4]>=0:
                            nsckls.append([1, [tuple(icklsx)]])
                        else:
                            nsckls.append([-1, [tuple(icklsx)]])
                    nsckls.append([nsckltp, insckls])
                    nscklsedi=len(ckls)-1
                else: #if len[nsckls]>=1 :
                    insckls=nsckls[-1][1]
                    if ickls1[0]>= insckls[-2][0] and ickls1[1]<= insckls[-2][1] and ickls2[0]>= insckls[-3][0] and ickls2[1]<= insckls[-3][1] \
                        and ickls0[0]<= insckls[-1][1] :
                        nsckls[-1][1][-1] = ickls0
                    elif ickls2[0]== insckls[-1][0] and  ickls2[1]== insckls[-1][1] and ickls1[1]> insckls[-1][1]:
                        nsckls[-1][0]+=2
                        nsckls[-1][1].append(ickls1)
                        nsckls[-1][1].append(ickls0)
                        nscklsedi=len(ckls)-1
                    elif ickls2[0]>insckls[-1][1]:
                        nsckltp=3
                        insckls0=ickls0
                        insckls1=ickls1
                        insckls2=ickls2
                        insckls=[insckls2,insckls1,insckls0]
                        for icklsx in ckls[nscklsedi+1:-3]:
                            if icklsx[4]>=0:
                                nsckls.append([1, [tuple(icklsx)]])
                            else:
                                nsckls.append([-1, [tuple(icklsx)]])
                        nsckls.append([nsckltp, insckls])
                        nscklsedi=len(ckls)-1


            elif (ickls0[4]<0 and sk_cklsm[-1][0]<=-3) or  (ickls0[4]<0 and ickls0[3]<ickls1[2] and ickls1[3]<=ickls2[2]):
                # -3---处于ndckl N-S dowm ckl          (ickls0,ickls1,ickls2)
                ckltp=-3
                ickls=(ickls0,ickls1,ickls2)
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
                    if ickls1[0] >= insckls[-2][0] and ickls1[1] <= insckls[-2][1] and ickls2[0] >= insckls[-3][0] and \
                                    ickls2[1] <= insckls[-3][1] \
                            and ickls0[0] <= insckls[-1][1]:
                        nsckls[-1][1][-1] = ickls0
                    elif ickls2[0] == insckls[-1][0] and ickls2[1] == insckls[-1][1] and ickls1[1] > insckls[-1][1]:
                        nsckls[-1][0] += -2
                        nsckls[-1][1].append(ickls1)
                        nsckls[-1][1].append(ickls0)
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

            elif (ickls0[4]>0 and sk_cklsm[-1][0]>=2) or  ickls0[4]>=detsuc*avgski:
                # 2---处于suckl strong up ckl       (ickls0,)
                ckltp=2
                ickls=(ickls0,)
                sk_cklsm.append((ckltp, ickls))
            elif (ickls0[4]<0 and sk_cklsm[-1][0]<=-2) or ickls0[4]<=detsdc*avgski:
                # -2--处于sdckl strong down ckl     (ickls0,)
                ckltp=-2
                ickls=(ickls0,)
                sk_cklsm.append((ckltp, ickls))
            elif ickls0[4]>0 and ickls0[4]<detsuc*avgski:
                # 1---处于wuckl weak up ckl         (ickls0,)
                ckltp=1
                ickls=(ickls0,)
                sk_cklsm.append((ckltp, ickls))
            elif ickls0[4]<0 and ickls0[4]>detsdc*avgski:
                # -1--处于wdckl weak down ckl       (ickls0,)
                ckltp=-1
                ickls=(ickls0,)
                sk_cklsm.append((ckltp, ickls))
            else:
                ckltp=0
                ickls=(ickls0,)
                sk_cklsm.append((ckltp, ickls))
        else: #if len(ckls)<3:
            ickls0=tuple(ckls[-1])
            if (ickls0[4]>0 and sk_cklsm[-1][0]>=2) or  ickls0[4]>=detsuc*avgski:
                # 2---处于suckl strong up ckl       (ickls0,)
                ckltp=2
                ickls=(ickls0,)
                sk_cklsm.append((ckltp, ickls))
            elif (ickls0[4]<0 and sk_cklsm[-1][0]<=-2) or ickls0[4]<=detsdc*avgski:
                # -2--处于sdckl strong down ckl     (ickls0,)
                ckltp=-2
                ickls=(ickls0,)
                sk_cklsm.append((ckltp, ickls))
            if ickls0[4]>0 and ickls0[4]<detsuc*avgski:
                # 1---处于wuckl weak up ckl         (ickls0,)
                ckltp=1
                ickls=(ickls0,)
                sk_cklsm.append((ckltp, ickls))
            elif ickls0[4]<0 and ickls0[4]>detsdc*avgski:
                # -1--处于wdckl weak down ckl       (ickls0,)
                ckltp=-1
                ickls=(ickls0,)
                sk_cklsm.append((ckltp, ickls))
            else:
                ckltp=0
                ickls=(ickls0,)
                sk_cklsm.append((ckltp, ickls))

        #更新  qspds=[] #趋势前沿列表 每段由[qsprti,nscklidx,nscklitp,qspbi,qspei,qspbsdp,qspesdp,qspbp,qspep]组成，来自于nsckls的波段
        if len(qspds)<=0 and len(nsckls)>0:  #当首次形成确定性的聚合链（数量可能大于1）的时候逐链划分趋势前沿
            nscklidx = 0
            qsprti=nsckls[0][1][-1][1]
            nscklitp=nsckls[0][0]
            qspbi=nsckls[0][1][0][0]
            qspei = nsckls[0][1][-1][1]
            qspbsdp=nsckls[0][1][0][2]
            qspesdp=nsckls[0][1][-1][3]
            if nscklitp>0 :
                if qspbi>0: qspbp=min(sk_low[qspbi],sk_low[qspbi-1])
                else: qspbp=sk_low[qspbi]

                if qspei <= i-1: qspep = max(sk_high[qspei], sk_high[qspei + 1])
                else: qspep = sk_high[qspei]

            else:
                if qspbi>0: qspbp=max(sk_high[qspbi],sk_high[qspbi-1])
                else: qspbp=sk_high[qspbi]

                if qspei <= i-1: qspep = min(sk_low[qspei], sk_low[qspei + 1])
                else: qspep = sk_low[qspei]

            qspds.append([qsprti,nscklidx,nscklitp,qspbi,qspei,qspbsdp,qspesdp,qspbp,qspep])
            if i>qspei:
                for idx in range(qspei+1,i+1):
                    iqspds0=qspds[-1]
                    if iqspds0[2]>0 : # 当前的趋势是向上前沿
                       if sk_close[idx]>iqspds0[8] : #向上步进
                           #检查此时的idx 处于第几个nsckls
                           nscklidx = idxof_nsckls(idx)
                           if nscklidx>0 and nscklidx>iqspds0[1]:
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
                       elif sk_close[idx]<iqspds0[7] : #向下反转
                           # 检查此时的idx 处于第几个nsckls
                           nscklidx = idxof_nsckls(idx)
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

                    elif iqspds0[2]<0 : # 当前的趋势是向下前沿
                       if sk_close[idx]<iqspds0[8] : #向下步进
                           #检查此时的idx 处于第几个nsckls
                           nscklidx = idxof_nsckls(idx)
                           if nscklidx>0 and nscklidx>iqspds0[1]:
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
                       elif sk_close[idx]>iqspds0[7] : #向上反转
                           # 检查此时的idx 处于第几个nsckls
                           nscklidx = idxof_nsckls(idx)
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

        #对于当前的isk, 更新qspds
        elif len(qspds)>=1 :
            iqspds0 = qspds[-1]
            if iqspds0[2] > 0:  # 之前的趋势是向上前沿
                #最新的isk与之前的趋势前沿同处于一个聚合链或单链上--延伸
                if i == nsckls[-1][1][-1][1] and nsckls[-1][1][0][0]<=iqspds0[3]: #最新的isk与之前的趋势前沿同处于一个聚合链
                    nscklidx = len(nsckls) - 1
                    qsprti = iqspds0[0]
                    nscklitp = nsckls[-1][0]
                    qspbi = nsckls[-1][1][0][0]
                    qspei = nsckls[-1][1][-1][1]
                    qspbsdp = nsckls[-1][1][0][2]
                    qspesdp = nsckls[-1][1][-1][3]
                    if qspbi > 0:
                        qspbp = min(sk_low[qspbi], sk_low[qspbi - 1])
                    else:
                        qspbp = sk_low[qspbi]
                    if qspei <= i - 1:
                        qspep = max(sk_high[qspei], sk_high[qspei + 1])
                    else:
                        qspep = sk_high[qspei]
                    qspds[-1] = [qsprti, nscklidx, nscklitp, qspbi, qspei, qspbsdp, qspesdp, qspbp, qspep]

                elif iqspds0[4]>=ckls[-1][0] and iqspds0[4]<=ckls[-1][1] : #最新的isk与之前的趋势前沿同处于一个单链
                    nscklidx = 0
                    qsprti = iqspds0[0]
                    nscklitp = 1
                    qspbi = ckls[-1][0]
                    qspei = ckls[-1][1]
                    qspbsdp = ckls[-1][2]
                    qspesdp = ckls[-1][3]
                    if qspbi > 0:
                        qspbp = min(sk_low[qspbi], sk_low[qspbi - 1])
                    else:
                        qspbp = sk_low[qspbi]
                    if qspei <= i - 1:
                        qspep = max(sk_high[qspei], sk_high[qspei + 1])
                    else:
                        qspep = sk_high[qspei]
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
                        if qspbi > 0:
                            qspbp = min(sk_low[qspbi], sk_low[qspbi - 1])
                        else:
                            qspbp = sk_low[qspbi]
                        if qspei <= i - 1:
                            qspep = max(sk_high[qspei], sk_high[qspei + 1])
                        else:
                            qspep = sk_high[qspei]
                        qspds.append([qsprti, nscklidx, nscklitp, qspbi, qspei, qspbsdp, qspesdp, qspbp, qspep])

                    else: # 该isk还还不在一个聚合链上，但一定在最新的单链上，将此单链作为趋势前沿
                        nscklidx = 0
                        qsprti = i
                        nscklitp = 1
                        qspbi = ckls[-1][0]
                        qspei = ckls[-1][1]
                        qspbsdp = ckls[-1][2]
                        qspesdp = ckls[-1][3]
                        if qspbi > 0:
                            qspbp = min(sk_low[qspbi], sk_low[qspbi - 1])
                        else:
                            qspbp = sk_low[qspbi]
                        if qspei <= i - 1:
                            qspep = max(sk_high[qspei], sk_high[qspei + 1])
                        else:
                            qspep = sk_high[qspei]
                        qspds.append( [qsprti, nscklidx, nscklitp, qspbi, qspei, qspbsdp, qspesdp, qspbp, qspep])

                elif sk_close[i] < iqspds0[7]:  # 趋势前沿向下逆转
                    # 检查此时的isk 是否处于最新的nsckls上
                    if i == nsckls[-1][1][-1][1]:  # 该聚合链是新前沿
                        nscklidx = len(nsckls) - 1
                        qsprti = i
                        nscklitp = nsckls[-1][0]
                        qspbi = nsckls[-1][1][0][0]
                        qspei = nsckls[-1][1][-1][1]
                        qspbsdp = nsckls[-1][1][0][2]
                        qspesdp = nsckls[-1][1][-1][3]
                        if qspbi > 0:
                            qspbp = max(sk_high[qspbi], sk_high[qspbi - 1])
                        else:
                            qspbp = sk_high[qspbi]
                        if qspei <= i - 1:
                            qspep = min(sk_low[qspei], sk_low[qspei + 1])
                        else:
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
                        if qspbi > 0:
                            qspbp = max(sk_high[qspbi], sk_high[qspbi - 1])
                        else:
                            qspbp = sk_high[qspbi]
                        if qspei <= i - 1:
                            qspep = min(sk_low[qspei], sk_low[qspei + 1])
                        else:
                            qspep = sk_low[qspei]
                        qspds.append([qsprti, nscklidx, nscklitp, qspbi, qspei, qspbsdp, qspesdp, qspbp, qspep])

                if i==qspds[-1][4]+1:  #更新右端极值点
                    if qspds[-1][2] >0 :
                        qspep=max(sk_high[i], qspds[-1][8])
                        qspds[-1][8]=qspep
                    elif qspds[-1][2] <0 :
                        qspep = min(sk_low[i], qspds[-1][8])
                        qspds[-1][8] = qspep

            elif iqspds0[2] < 0:  # 之前的趋势是向下前沿
                #最新的isk与之前的趋势前沿同处于一个聚合链或单链上--延伸
                if i == nsckls[-1][1][-1][1] and nsckls[-1][1][0][0]<=iqspds0[3]: #最新的isk与之前的趋势前沿同处于一个聚合链
                    nscklidx = len(nsckls) - 1
                    qsprti = iqspds0[0]
                    nscklitp = nsckls[-1][0]
                    qspbi = nsckls[-1][1][0][0]
                    qspei = nsckls[-1][1][-1][1]
                    qspbsdp = nsckls[-1][1][0][2]
                    qspesdp = nsckls[-1][1][-1][3]
                    if qspbi > 0:
                        qspbp = max(sk_high[qspbi], sk_high[qspbi - 1])
                    else:
                        qspbp = sk_high[qspbi]
                    if qspei <= i - 1:
                        qspep = min(sk_low[qspei], sk_low[qspei + 1])
                    else:
                        qspep = sk_low[qspei]

                    qspds[-1] = [qsprti, nscklidx, nscklitp, qspbi, qspei, qspbsdp, qspesdp, qspbp, qspep]

                elif iqspds0[4]>=ckls[-1][0] and iqspds0[4]<=ckls[-1][1] : #最新的isk与之前的趋势前沿同处于一个单链
                    nscklidx = 0
                    qsprti = iqspds0[0]
                    nscklitp = -1
                    qspbi = ckls[-1][0]
                    qspei = ckls[-1][1]
                    qspbsdp = ckls[-1][2]
                    qspesdp = ckls[-1][3]
                    if qspbi > 0:
                        qspbp = max(sk_high[qspbi], sk_high[qspbi - 1])
                    else:
                        qspbp = sk_high[qspbi]
                    if qspei <= i - 1:
                        qspep = min(sk_low[qspei], sk_low[qspei + 1])
                    else:
                        qspep = sk_low[qspei]

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
                        if qspbi > 0:
                            qspbp = max(sk_high[qspbi], sk_high[qspbi - 1])
                        else:
                            qspbp = sk_high[qspbi]
                        if qspei <= i - 1:
                            qspep = min(sk_low[qspei], sk_low[qspei + 1])
                        else:
                            qspep = sk_low[qspei]
                        qspds.append([qsprti, nscklidx, nscklitp, qspbi, qspei, qspbsdp, qspesdp, qspbp, qspep])

                    else: # 该isk还还不在一个聚合链上，但一定在最新的单链上，将此单链作为趋势前沿
                        nscklidx = 0
                        qsprti = i
                        nscklitp = -1
                        qspbi = ckls[-1][0]
                        qspei = ckls[-1][1]
                        qspbsdp = ckls[-1][2]
                        qspesdp = ckls[-1][3]
                        if qspbi > 0:
                            qspbp = max(sk_high[qspbi], sk_high[qspbi - 1])
                        else:
                            qspbp = sk_high[qspbi]
                        if qspei <= i - 1:
                            qspep = min(sk_low[qspei], sk_low[qspei + 1])
                        else:
                            qspep = sk_low[qspei]
                        qspds.append( [qsprti, nscklidx, nscklitp, qspbi, qspei, qspbsdp, qspesdp, qspbp, qspep])

                elif sk_close[i] > iqspds0[7]:  # 趋势前沿向上逆转
                    # 检查此时的isk 是否处于最新的nsckls上
                    if i == nsckls[-1][1][-1][1]:  # 该聚合链是新前沿，向上逆转
                        nscklidx = len(nsckls) - 1
                        qsprti = i
                        nscklitp = nsckls[-1][0]
                        qspbi = nsckls[-1][1][0][0]
                        qspei = nsckls[-1][1][-1][1]
                        qspbsdp = nsckls[-1][1][0][2]
                        qspesdp = nsckls[-1][1][-1][3]
                        if qspbi > 0:
                            qspbp = min(sk_low[qspbi], sk_low[qspbi - 1])
                        else:
                            qspbp = sk_low[qspbi]
                        if qspei <= i - 1:
                            qspep = max(sk_high[qspei], sk_high[qspei + 1])
                        else:
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
                        if qspbi > 0:
                            qspbp = min(sk_low[qspbi], sk_low[qspbi - 1])
                        else:
                            qspbp = sk_low[qspbi]
                        if qspei <= i - 1:
                            qspep = max(sk_high[qspei], sk_high[qspei + 1])
                        else:
                            qspep = sk_high[qspei]
                        qspds.append([qsprti, nscklidx, nscklitp, qspbi, qspei, qspbsdp, qspesdp, qspbp, qspep])

                if i==qspds[-1][4]+1:  #更新右端极值点
                    if qspds[-1][2] >0 :
                        qspep=max(sk_high[i], qspds[-1][8])
                        qspds[-1][8]=qspep
                    elif qspds[-1][2] <0 :
                        qspep = min(sk_low[i], qspds[-1][8])
                        qspds[-1][8] = qspep

        if len(qspds)<=0:
            qsprti=i
            nscklidx=0
            nscklitp=0
            qspbi=0
            qspei=i
            qspbsdp=sk_open[0]
            qspesdp=sk_close[i]
            qspbp=sk_open[0]
            qspep=sk_close[i]
        else:
            qsprti=qspds[-1][0]
            nscklidx=qspds[-1][1]
            nscklitp=qspds[-1][2]
            qspbi=qspds[-1][3]
            qspei=qspds[-1][4]
            qspbsdp=qspds[-1][5]
            qspesdp=qspds[-1][6]
            qspbp=qspds[-1][7]
            qspep=qspds[-1][8]
        sk_qspds.append([qsprti,nscklidx,nscklitp,qspbi,qspei,qspbsdp,qspesdp,qspbp,qspep])
        '''
          ==============以下是信号部分==============
        '''
        if len(sk_qspds)>=1 and sk_qspds[-1][2]>0 and sk_qspds[-2][2]<0 : #向上转换
            sgn_rsti=i
            sgn_rstp=sk_qspds[-2][7]
            sgn_rstdir=1
            qsrstp.append((sgn_rsti, sgn_rstp, sgn_rstdir))

        if len(sk_qspds)>=1 and sk_qspds[-1][2]<0 and sk_qspds[-2][2]>0 : #向上转换
            sgn_rsti=i
            sgn_rstp=sk_qspds[-2][7]
            sgn_rstdir=-1
            qsrstp.append((sgn_rsti, sgn_rstp, sgn_rstdir))

        if len(qsrstp)>=1  :  #转多头，寻找做多时机
            # 计算做多的估计价位：


            pass


        if len(qsrstp) >= 1   :  # 转空头，寻找做空时机
            # 计算做多的估计价位：
            pass















def idxof_nsckls(ski):
    if len(nsckls)<=0: return -1
    for idx in range(0,len(nsckls)):
        if ski>=nsckls[idx][1][0][0] and ski<=nsckls[idx][1][-1][1] :
            return idx
    return -1



def sk_isnuc(i): # 根据sk_ckl判断当前是否是上升N元
    pass


def outtozbcsv( csvfpth):  #趋势前沿相关信息输出
    zbnsckls=[]
    csvfobw=open(csvfpth,'wb')
    csv_writer = csv.writer(csvfobw)
    for idx in range(0, len(nsckls)):
        bi=nsckls[idx][1][0][0]
        bp=nsckls[idx][1][0][2]
        ei=nsckls[idx][1][-1][1]
        ep=nsckls[idx][1][-1][3]
        bt=strtoeldatime(str(sk_close.index[bi]))
        et=strtoeldatime(str(sk_close.index[ei]))
        zbnsckls.append((bt[0],bt[1], et[0],et[1], bp, ep))
        csv_writer.writerow(zbnsckls[-1])
    csvfobw.close()

def qspouttozbcsv( csvfpth):
    csvfobw=open(csvfpth,'wb')
    csv_writer = csv.writer(csvfobw)
    for idx in range(0, len(sk_qspds)):
        qsprti = sk_qspds[idx][0]
        nscklidx = sk_qspds[idx][1]
        nscklitp = sk_qspds[idx][2]
        qspbi = sk_qspds[idx][3]
        qspei = sk_qspds[idx][4]
        qspbsdp = sk_qspds[idx][5]
        qspesdp = sk_qspds[idx][6]
        qspbp = sk_qspds[idx][7]
        qspep = sk_qspds[idx][8]
        idxt=strtoeldatime(str(sk_close.index[idx]))
        csv_writer.writerow((idxt[0],idxt[1], qsprti,nscklidx,nscklitp,qspbi,qspei,qspbsdp,qspesdp,qspbp,qspep))
    csvfobw.close()


def strtoeldatime(strdatetime):
    dtm = datetime.datetime.strptime(strdatetime, '%Y-%m-%d %H:%M:%S')
    eldate= (dtm.year-1900)*10000+dtm.month*100+dtm.day
    eltime= dtm.hour*100+dtm.minute
    return (eldate, eltime)




#'''
cklinit()

for i in range(0, len(ckls)):
    print sk_close.index[ckls[i][0]], ckls[i]
#'''
'''
for i in range(0,sk_close.size):
    #print i
    print i,sk_close.index[i],sk_cklsm[i]

'''
#'''
for idx in range(0, len(nsckls)):
    print nsckls[idx]
#'''
outtozbcsv( outto_zbcsvfile)

#'''
for idx in range(0, len(qspds)):
    print qspds[idx]
#'''
qspouttozbcsv( qspoutto_zbcsvfile )




