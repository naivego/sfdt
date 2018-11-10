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
decsn=2  #С��λ��
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
sk_ckl=[]  # ��ckͬ������Ԫ�飨ckli,cksdh,cksdl�����ɵĶ��У���¼��ǰ��sk����������sk��Ŀ��ʵ�岿�ֵ�����
sk_ckdtpst=0.2  #0.2��ƽ���Ƿ���Ϊ�ǵ����ӵĹ���
ckls=[]   # ��ckl�߶��б����б�[cklbi,cklei,cklbp,cklep,cklsd]����,��¼�߶ε����λ�á��յ�λ�á����۸��յ�۸񡢳���
detsuc=5  #strong�������������Ƿ�ת������ =detsuc*avgski
detsdc=-5 #strong�½��������½���ת������ =detsdc*avgski
sk_cklsm=[] #��sk���п���¶�ckls�ṹ����������ָʾ��ǰ��sk����ckls�ṹ�е�ˮƽ (ckltp, ickls)
'''
   ckltp                             ickls
   1---����wuckl weak up ckl         (ickls0,)
   2---����suckl strong up ckl       (ickls0,)
   3---����nuckl N-S up ckl          (ickls1,ickls2,ickls0)
   -1--����wdckl weak down ckl       (ickls0,)
   -2--����sdckl strong down ckl     (ickls0,)
   -3--����ndckl N-S down ckl        (ickls1,ickls2,ickls0)

'''
nsckls=[]  #��ckls�����ϣ������ڵĿ��Ծۺϵ�nԪ�ۺ��������ɣ����б���[nsckltp��insckls]��� insckls=[ickls0,ickls1,ickls2...]���ɣ����γ��µľֲ�nԪʱ����
nscklsedi=0 #���¶ε�nsckls����ckls�ĵڼ�������
#-----------------------------------------------
qspds=[] #����ǰ���б� ÿ����[qsprti,nscklidx,nscklitp,qspbi,qspei,qspbsdp,qspesdp,qspbp,qspep]��ɣ�������nsckls�Ĳ���
'''
   qsprti--�γ��µ�qsdpsʱ����������ת����sk����
   nscklidx--��qspds���ڵľۺ���������
   nscklitp--��qspds���ڵľۺ�����ckltp
   qspbi--��qspds���������
   qspei--��qspds���յ�����
   qspbsdp--��qspds�����ʵ���۸�
   qspesdp--��qspds���յ�ʵ���۸�
   qspbp--��qspds�����Զ�˼۸�����ͻ�Ƹü۸�ȷ���µķ�ת������ǰ��
   qspep--��qspds���յ�Զ�˼۸�����ͻ�Ƹü۸�ȷ���²�������ǰ��

'''
sk_qspds=[]

def ftpvalue(syb):
    if syb[:2].upper()=="IF": return 300
    elif syb[:2].upper()=="CU": return 5
    elif syb[:2].upper() == "RB": return 10
    else: return 1

class ftorder:  #�ڻ�����
    # �����������
    symbol=""
    openi = 0 #����λ��
    openp=0   #���ּ۸�
    slot=1    #��������  ����-��ͷ�� ����-��ͷ
    closei= -1 #ƽ��λ�� -1 δƽ��
    closep=0  #ƽ�ּ۸�
    stplp=0   # ֹ���λ  0--δ��ֹ��
    tpftp=0   #Ŀ���λ   0--δ��ֹӯ
    ordtype=0  #�������ͣ� 0-�м۵��� 1-�޼۵��� 2-stop��
    ordstate=0  #����״̬  -1��ʧЧ 0�� δ�ɽ�  1�� �ѳɽ�
    ordid = 0
    # ����˽������,˽�����������ⲿ�޷�ֱ�ӽ��з���
    # __weight = 0

    # ���幹�췽��

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

    def ordopen(self, syb, opi, opp, slot, ordtyp, stplp, tpftp, sgnid):   #����
        self.symbol= syb
        self.openi=opi
        self.openp=opp
        self.slot=slot
        self.ordtype=ordtyp
        self.stplp=stplp
        self.tpftp=tpftp
        self.ordid=sgnid

    def ordclose(self, cdi, cdp):    #ƽ��
        self.closei=cdi
        self.closep=cdp

    def setstpl(self, newstplp):
        self.stplp=newstplp
    def settpft(self, newtpftp):
        self.tpftp=newtpftp

    def getopl(self, isk): #������sk_i�ϵĸ���ӯ��
        if isk>=self.openi and isk<=self.closei :
            return ftpvalue(symbol)*(sk_close[isk]-self.openp)*self.slot
        else: return 0
    def getcpl(self, isk): #������sk_i�ϵ�ƽ��ӯ��
        if self.closei>=0 :
            return ftpvalue(symbol) * (self.closep - self.openp) * self.slot
        else: return 0

    def chkordexit(self, ski, sk_op, sk_hp, sk_lp, sk_cp):  #���ֹ��ֹӯ����
        if self.closei>0: return 0 #�Ѿ�����
        if self.stplp>0 :
            if self.slot>0 : # ��
                if sk_lp<=self.stplp: #ֹ��
                    self.closei = ski
                    self.closep = self.stplp
                    return 1
            elif self.slot<0 : # ����
                if sk_hp>=self.stplp: #ֹ��
                    self.closei = ski
                    self.closep = self.stplp
                    return 1

        if self.tpftp>0:
            if self.slot<0 : # ����
                if sk_lp<=self.tpftp: #ֹӯ
                    self.closei = ski
                    self.closep = self.tpftp
                    return 1
            elif self.slot>0 : # ��
                if sk_hp>=self.tpftp: #ֹӯ
                    self.closei = ski
                    self.closep = self.tpftp
                    return 1
        return 0

    def chkordtrd(self, ski, sk_op, sk_hp, sk_lp, sk_cp):  #��鶩���ڵ�ǰ ski�ɽ����
        if self.openi>0 : return 0
        if self.ordtype==0 : #�м۵�
           self.openi=ski
           self.openp=sk_op
           return 1
        elif self.ordtype == 1 and self.openp>0  :  # �޼۵�
            if self.slot > 0:  # ��
                if sk_lp <= self.openp:  #
                    self.openi = ski
                    return 1
            elif self.slot < 0:  # ����
                if sk_hp >= self.openp:  #
                    self.openi = ski
                    return 1

        elif self.ordtype == 2 and self.openp>0  :  # ֹ��
            if self.slot > 0:  # ��
                if sk_hp >= self.openp:  #
                    self.openi = ski
                    return 1
            elif self.slot < 0:  # ����
                if sk_lp <= self.openp:  #
                    self.openi = ski
                    return 1

        return 0

#---------------------------------------------�źŲ���ȫ�ֱ���
'''
   �����߼��������£�
   1����sk����ʱ�����ź�
   2������ֲ��ڱ�sk�ĳ������������ֹ���ֹӯ
   3���˲��Ƿ������޸�δ�ɽ�����
   4������֮ǰ������δ�ɽ������ڱ�sk�ĳɽ����������3���б�
   5�����ͱ�sk�������źŶ���, ʵ������һ��sk���ͣ����� mktord, lmtord, stpord ��������

   �����źŵ������� ski+sgnname
'''
qsrstp=[]  #���ת���� ����ͻ��ǰ�أ����Ʒ���ת�� (sgn_rsti, sgn_rstp, sgn_rstdir) ͻ��λ�ã�ͻ�Ƽ۸�ͻ�Ʒ���1-���ϣ� -1 ����
sgn_qspcl=[0.75,0.5]  #�����Ʒ�ת��ԭ���Ʒ���ĵ����ڵ�ǰ����ǰ�ػس�һ�����ȷֱ�ƽ��
sgn_qspcv=[0.5,0]     # ���ֵ������ԭ���Ʒ�ת�㴦�ֲܳ�ˮƽ�ı���

sgn_qskcl=[0.5,0.3,0] #�����Ʒ�ת�󣬵�ǰ����ǰ�ػس���λ�Ϸֱ𿪲�
sgn_qskcv=[0.5,0.8,1.0] #�����Ʒ�ת�󣬵�ǰ����ǰ�ػس���λ�Ϸֱ𿪲������ۼƼӲֵ���׼�ֲֵ�ˮƽ
#-------------------------------------------------------------

#---------------------------------------------�ʽ�Ͳ�λ����ȫ�ֱ���
bdcap=1000000   # ��ʼ�ʽ�
sk_rtcap=[]     # ʵʱ�ʲ� ��ÿ��K�����̼ۺ���
sendords=[]     # ����ȥ��δ�ɽ��Ķ����б�
posiords=[]     # �ֲ֣� �ѳɽ���δƽ�ֶ����б�
cldords=[]      # ��ƽ�ֶ����б�
stdcv=1         # ��׼�ֲ�ˮƽ������ʵʱ�ʲ�����
uselever=3      # ʹ�øܸ˱���

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

def avgsk(i):  #ע�⣺�������Ǽ����i��sK֮ǰ��cn�����ӵ�ƽ�������Ƿ���Ҫ��i>0
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

    #ckls=[]   # ��ckl�߶��б����б�[cklbi,cklei,cklbp,cklep,cklsd]����,��¼�߶ε���㡢�յ㡢����
    cklbi=0
    cklei=0
    cklbp=sk_open[0]
    cklep=sk_close[0]
    cklsd=ckli*(cksdh-cksdl)
    ckls.append([cklbi, cklei,cklbp,cklep,cklsd])

    #sk_cklsm=[] #��sk���п���¶�ckls�ṹ����������ָʾ��ǰ��sk����ckls�ṹ�е�ˮƽ (ckltp, ickls)
    ckltp=ckli
    ickls0=tuple(ckls[-1])
    ickls=(ickls0,)
    sk_cklsm.append((ckltp, ickls))
    #print(0,sk_close.index[0],(ckli, round(cksdh,decsn), round(cksdl,decsn)))
    sk_qspds.append([0, 0, 0, 0, 0, sk_open[0], sk_close[0], sk_open[0], sk_close[0]])

    #---------------------��ʼ�ʽ�
    sk_rtcap.append(bdcap)

    for i in range(1,sk_close.size):
        avgski=avgsk(i)
        if sk_ckl[i-1][0]>0 :
            if sk_close[i]>=sk_close[i-1]-sk_ckdtpst*avgski:
               ckli=sk_ckl[i-1][0]+1
               cksdh=max(sk_ckl[i-1][1],sk_close[i])
               cksdl=sk_ckl[i-1][2]
               sk_ckl.append((ckli, cksdh, cksdl))

               #���� ckls
               ckls[-1][1]+=1
               ckls[-1][3]=cksdh
               ckls[-1][4]=cksdh-cksdl
            else:
               ckli=-1
               cksdh=sk_ckl[i-1][1]
               cksdl=sk_close[i]
               sk_ckl.append((ckli, cksdh, cksdl))

               #���� ckls
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
               #���� ckls
               ckls[-1][1]+=1
               ckls[-1][3]=cksdl
               ckls[-1][4]=cksdl-cksdh

            else:
               ckli=1
               cksdl=sk_ckl[i-1][2]
               cksdh=sk_close[i]
               sk_ckl.append((ckli, cksdh, cksdl))

               #���� ckls
               cklbi=i
               cklei=i
               cklbp=cksdl
               cklep=cksdh
               cklsd=cklep-cklbp
               ckls.append([cklbi, cklei, cklbp, cklep,cklsd])

        #print(i,sk_close.index[i],(ckli, round(cksdh,decsn), round(cksdl,decsn)))
        #sk_cklsm=[] #��sk���п���¶�ckls�ṹ����������ָʾ��ǰ��sk����ckls�ṹ�е�ˮƽ (ckltp, ickls)
        if len(ckls)>=3:
            ickls0=tuple(ckls[-1])
            ickls1=tuple(ckls[-2])
            ickls2=tuple(ckls[-3])
            if (ickls0[4]>0 and sk_cklsm[-1][0]>=3 ) or (ickls0[4]>0 and ickls0[3]>ickls1[2] and ickls1[3]>=ickls2[2]):
                # 3---����nuckl N-S up ckl            (ickls0,ickls1,ickls2)
                ckltp=3
                ickls=(ickls0,ickls1,ickls2)
                sk_cklsm.append((ckltp, ickls))

                #����nsckls=[]  ��[nsckltp��insckls]��� insckls=[insckls0,insckls1,insckls2...]
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
                # -3---����ndckl N-S dowm ckl          (ickls0,ickls1,ickls2)
                ckltp=-3
                ickls=(ickls0,ickls1,ickls2)
                sk_cklsm.append((ckltp, ickls))

                # ����nsckls=[]  ��[nsckltp��insckls]��� insckls=[insckls0,insckls1,insckls2...]
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
                # 2---����suckl strong up ckl       (ickls0,)
                ckltp=2
                ickls=(ickls0,)
                sk_cklsm.append((ckltp, ickls))
            elif (ickls0[4]<0 and sk_cklsm[-1][0]<=-2) or ickls0[4]<=detsdc*avgski:
                # -2--����sdckl strong down ckl     (ickls0,)
                ckltp=-2
                ickls=(ickls0,)
                sk_cklsm.append((ckltp, ickls))
            elif ickls0[4]>0 and ickls0[4]<detsuc*avgski:
                # 1---����wuckl weak up ckl         (ickls0,)
                ckltp=1
                ickls=(ickls0,)
                sk_cklsm.append((ckltp, ickls))
            elif ickls0[4]<0 and ickls0[4]>detsdc*avgski:
                # -1--����wdckl weak down ckl       (ickls0,)
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
                # 2---����suckl strong up ckl       (ickls0,)
                ckltp=2
                ickls=(ickls0,)
                sk_cklsm.append((ckltp, ickls))
            elif (ickls0[4]<0 and sk_cklsm[-1][0]<=-2) or ickls0[4]<=detsdc*avgski:
                # -2--����sdckl strong down ckl     (ickls0,)
                ckltp=-2
                ickls=(ickls0,)
                sk_cklsm.append((ckltp, ickls))
            if ickls0[4]>0 and ickls0[4]<detsuc*avgski:
                # 1---����wuckl weak up ckl         (ickls0,)
                ckltp=1
                ickls=(ickls0,)
                sk_cklsm.append((ckltp, ickls))
            elif ickls0[4]<0 and ickls0[4]>detsdc*avgski:
                # -1--����wdckl weak down ckl       (ickls0,)
                ckltp=-1
                ickls=(ickls0,)
                sk_cklsm.append((ckltp, ickls))
            else:
                ckltp=0
                ickls=(ickls0,)
                sk_cklsm.append((ckltp, ickls))

        #����  qspds=[] #����ǰ���б� ÿ����[qsprti,nscklidx,nscklitp,qspbi,qspei,qspbsdp,qspesdp,qspbp,qspep]��ɣ�������nsckls�Ĳ���
        if len(qspds)<=0 and len(nsckls)>0:  #���״��γ�ȷ���Եľۺ������������ܴ���1����ʱ��������������ǰ��
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
                    if iqspds0[2]>0 : # ��ǰ������������ǰ��
                       if sk_close[idx]>iqspds0[8] : #���ϲ���
                           #����ʱ��idx ���ڵڼ���nsckls
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
                       elif sk_close[idx]<iqspds0[7] : #���·�ת
                           # ����ʱ��idx ���ڵڼ���nsckls
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

                    elif iqspds0[2]<0 : # ��ǰ������������ǰ��
                       if sk_close[idx]<iqspds0[8] : #���²���
                           #����ʱ��idx ���ڵڼ���nsckls
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
                       elif sk_close[idx]>iqspds0[7] : #���Ϸ�ת
                           # ����ʱ��idx ���ڵڼ���nsckls
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

        #���ڵ�ǰ��isk, ����qspds
        elif len(qspds)>=1 :
            iqspds0 = qspds[-1]
            if iqspds0[2] > 0:  # ֮ǰ������������ǰ��
                #���µ�isk��֮ǰ������ǰ��ͬ����һ���ۺ���������--����
                if i == nsckls[-1][1][-1][1] and nsckls[-1][1][0][0]<=iqspds0[3]: #���µ�isk��֮ǰ������ǰ��ͬ����һ���ۺ���
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

                elif iqspds0[4]>=ckls[-1][0] and iqspds0[4]<=ckls[-1][1] : #���µ�isk��֮ǰ������ǰ��ͬ����һ������
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


                elif sk_close[i] > iqspds0[8]:  # ���ϲ���
                    # ����ʱ��isk �Ƿ������µ�nsckls��
                    if i == nsckls[-1][1][-1][1]:  # �þۺ�������ǰ�أ����ϲ���
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

                    else: # ��isk��������һ���ۺ����ϣ���һ�������µĵ����ϣ����˵�����Ϊ����ǰ��
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

                elif sk_close[i] < iqspds0[7]:  # ����ǰ��������ת
                    # ����ʱ��isk �Ƿ������µ�nsckls��
                    if i == nsckls[-1][1][-1][1]:  # �þۺ�������ǰ��
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

                    else:  # ��isk��������һ���ۺ����ϣ���һ�������µĵ����ϣ����˵�����Ϊ����ǰ��
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

                if i==qspds[-1][4]+1:  #�����Ҷ˼�ֵ��
                    if qspds[-1][2] >0 :
                        qspep=max(sk_high[i], qspds[-1][8])
                        qspds[-1][8]=qspep
                    elif qspds[-1][2] <0 :
                        qspep = min(sk_low[i], qspds[-1][8])
                        qspds[-1][8] = qspep

            elif iqspds0[2] < 0:  # ֮ǰ������������ǰ��
                #���µ�isk��֮ǰ������ǰ��ͬ����һ���ۺ���������--����
                if i == nsckls[-1][1][-1][1] and nsckls[-1][1][0][0]<=iqspds0[3]: #���µ�isk��֮ǰ������ǰ��ͬ����һ���ۺ���
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

                elif iqspds0[4]>=ckls[-1][0] and iqspds0[4]<=ckls[-1][1] : #���µ�isk��֮ǰ������ǰ��ͬ����һ������
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


                elif sk_close[i] < iqspds0[8]:  # ���²���
                    # ����ʱ��isk �Ƿ������µ�nsckls��
                    if i == nsckls[-1][1][-1][1]:  # �þۺ�������ǰ�أ����²���
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

                    else: # ��isk��������һ���ۺ����ϣ���һ�������µĵ����ϣ����˵�����Ϊ����ǰ��
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

                elif sk_close[i] > iqspds0[7]:  # ����ǰ��������ת
                    # ����ʱ��isk �Ƿ������µ�nsckls��
                    if i == nsckls[-1][1][-1][1]:  # �þۺ�������ǰ�أ�������ת
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

                    else:  # ��isk��������һ���ۺ����ϣ���һ�������µĵ����ϣ����˵�����Ϊ����ǰ��
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

                if i==qspds[-1][4]+1:  #�����Ҷ˼�ֵ��
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
          ==============�������źŲ���==============
        '''
        if len(sk_qspds)>=1 and sk_qspds[-1][2]>0 and sk_qspds[-2][2]<0 : #����ת��
            sgn_rsti=i
            sgn_rstp=sk_qspds[-2][7]
            sgn_rstdir=1
            qsrstp.append((sgn_rsti, sgn_rstp, sgn_rstdir))

        if len(sk_qspds)>=1 and sk_qspds[-1][2]<0 and sk_qspds[-2][2]>0 : #����ת��
            sgn_rsti=i
            sgn_rstp=sk_qspds[-2][7]
            sgn_rstdir=-1
            qsrstp.append((sgn_rsti, sgn_rstp, sgn_rstdir))

        if len(qsrstp)>=1  :  #ת��ͷ��Ѱ������ʱ��
            # ��������Ĺ��Ƽ�λ��


            pass


        if len(qsrstp) >= 1   :  # ת��ͷ��Ѱ������ʱ��
            # ��������Ĺ��Ƽ�λ��
            pass















def idxof_nsckls(ski):
    if len(nsckls)<=0: return -1
    for idx in range(0,len(nsckls)):
        if ski>=nsckls[idx][1][0][0] and ski<=nsckls[idx][1][-1][1] :
            return idx
    return -1



def sk_isnuc(i): # ����sk_ckl�жϵ�ǰ�Ƿ�������NԪ
    pass


def outtozbcsv( csvfpth):  #����ǰ�������Ϣ���
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




