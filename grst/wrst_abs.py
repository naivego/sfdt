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
sk_open=dask[syb_open]
#sk_open=(dask[syb_open]/sk_factor).apply(lambda x: round(x,decsn))
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
   3---����nuckl N-S up ckl          (ickls0,ickls1,ickls2)
   -1--����wdckl weak down ckl       (ickls0,)
   -2--����sdckl strong down ckl     (ickls0,)
   -3--����ndckl N-S down ckl        (ickls0,ickls1,ickls2)

'''
nsckls=[]  #��ckls�����ϣ������ڵĿ��Ծۺϵ�nԪ�ۺ��������ɣ����б���[nsckltp��insckls]��� insckls=[ickls0,ickls1,ickls2...]���ɣ����γ��µľֲ�nԪʱ����
nscklsedi=0 #���¶ε�nsckls����ckls�ĵڼ�������
#-----------------------------------------------

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

def is_rising(i):  # // 3����
    #avgski=avgsk(i)
    if sk_close[i]>sk_open[i] and sk_close[i-1]>sk_open[i-1] and sk_close[i-2]>sk_open[i-2] and sk_close[i]-sk_open[i-2]>=3*avgski: return True
    if sk_close[i]>sk_open[i] and sk_close[i-1]>=sk_open[i-1] and sk_close[i-2]>sk_open[i-2] and sk_close[i]-sk_open[i-2]>=3*avgski: return True
    if sk_close[i]>sk_open[i] and sk_close[i-1]>sk_open[i-1] and sk_close[i-2]>=sk_open[i-2] and sk_close[i]-sk_open[i-2]>=3*avgski: return True
    else:return False

def is_falling(i):  # // 3����
    #avgski=avgsk(i)
    if sk_close[i]<sk_open[i] and sk_close[i-1]<sk_open[i-1] and sk_close[i-2]<sk_open[i-2] and sk_close[i]-sk_open[i-2]<=3*avgski: return True
    if sk_close[i]<sk_open[i] and sk_close[i-1]<=sk_open[i-1] and sk_close[i-2]<sk_open[i-2] and sk_close[i]-sk_open[i-2]<=3*avgski: return True
    if sk_close[i]<sk_open[i] and sk_close[i-1]<sk_open[i-1] and sk_close[i-2]<=sk_open[i-2] and sk_close[i]-sk_open[i-2]<=3*avgski: return True
    else:return False

def is_up_reversing(i):  #//��ת����
    #avgski=avgsk(i)
    if sk_close[i]>sk_open[i] and sk_close[i-1]>=sk_open[i-1] and sk_close[i-2]<sk_open[i-2] and sk_close[i]-sk_open[i-2]>=1.5*avgski:return True
    else: return False

def is_down_reversing(i):  #//��ת�µ�
    #avgski=avgsk(i)
    if sk_close[i]<sk_open[i] and sk_close[i-1]<=sk_open[i-1] and sk_close[i-2]>sk_open[i-2] and sk_close[i]-sk_open[i-2]<=-1.5*avgski:return True
    else: return False

def is_halfrest_rising(i):   #//��������  ����������
    #avgski=avgsk(i)
    if sk_close[i]>sk_open[i] and sk_close[i-1]>sk_open[i-1] and sk_close[i-2]<=sk_open[i-2] and sk_close[i-3]>sk_open[i-3] and sk_close[i-4]>sk_open[i-4] and sk_close[i]-sk_open[i-2]>=1*avgski: return True
    if sk_close[i]>sk_open[i] and sk_close[i-1]<=sk_open[i-1] and sk_close[i-2]>sk_open[i-2] and sk_close[i]>sk_open[i-1] and (sk_close[i-2]-sk_open[i-2] +sk_close[i]-sk_open[i])>4*(sk_open[i-1]-sk_close[i-1]) and\
       (sk_close[i]-sk_open[i]>1.5*avgski or sk_close[i-2]-sk_open[i-2]>1.5*avgski) :return True
    else:return False

def is_halfrest_falling(i):   #//��������  ����������
    #avgski=avgsk(i)
    if sk_close[i]<sk_open[i] and sk_close[i-1]<sk_open[i-1] and sk_close[i-2]>=sk_open[i-2] and sk_close[i-3]<sk_open[i-3] and sk_close[i-4]<sk_open[i-4] and sk_close[i]-sk_open[i-2]<=-1*avgski: return True
    if sk_close[i]<sk_open[i] and sk_close[i-1]>=sk_open[i-1] and sk_close[i-2]<sk_open[i-2] and sk_close[i]<sk_open[i-1] and (sk_close[i-2]-sk_open[i-2] +sk_close[i]-sk_open[i])<4*(sk_open[i-1]-sk_close[i-1]) and\
       (sk_close[i]-sk_open[i]<-1.5*avgski or sk_close[i-2]-sk_open[i-2]<-1.5*avgski) :return True
    else:return False

def is_uping(i):   # on rising
    avgski = avgsk(i)
    if is_rising(i) or is_up_reversing(i) or  is_halfrest_rising(i) : return True
    else: return False

def is_downing(i):       #// on falling
    avgski = avgsk(i)
    if is_falling(i) or is_down_reversing(i) or is_halfrest_falling(i): return True
    else: return False

def is_on_rising(i):   #// on rising leg
    if i<5 : return False
    if is_uping(i): return True
    elif is_downing(i): return False
    else: return is_on_rising(i-1)


def is_on_falling(i):  #// on falling leg
    if i < 5: return False
    if is_uping(i): return False
    elif is_downing(i): return True
    else: return is_on_falling(i-1)

def is_botmRT(i):
    if is_on_rising(i) and is_on_falling(i-1): return True
    else: return False

def is_topRT(i):
    if is_on_falling(i) and is_on_rising(i-1) : return True
    else: return False


def topbari(bi, ei ): #������sk������ʵ�岿�ֵ���ߵ�λ�úͼ۸�
    if bi<0 or bi>ei :return -1,0
    mi=bi
    mp=max(sk_close[mi], sk_open[mi])
    if ei==bi: return mi,mp
    for i in range(bi+1, ei+1):
        mip=max(sk_close[i], sk_open[i])
        if mip>mp :
            mi=i
            mp=mip

    return mi,mp


def botmbari(bi, ei):  # ������sk������ʵ�岿�ֵ���ߵ�λ�úͼ۸�
    if bi < 0 or bi > ei: return -1, 0
    mi = bi
    mp = min(sk_close[mi], sk_open[mi])
    if ei == bi: return mi, mp
    for i in range(bi + 1, ei + 1):
        mip = min(sk_close[i], sk_open[i])
        if mip < mp:
            mi = i
            mp = mip

    return mi, mp

#-------------------------------------------------------------------

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

def sk_isnuc(i): # ����sk_ckl�жϵ�ǰ�Ƿ�������NԪ
    pass




'''
for i in range(maxbarback,sk_close.size):
    #print i
    #print sk_close[i]
    print avgsk(i)
    if is_botmRT(i):
        print  sk_close.index[i] ,'is_botmRT'
    if is_topRT(i):
        print  sk_close.index[i], 'is_topRT'
'''
#print sk_close
'''
cklinit()

for i in range(0, len(ckls)):
    print sk_close.index[ckls[i][0]], ckls[i]
'''
'''
for i in range(0,sk_close.size):
    #print i
    print i,sk_close.index[i],sk_cklsm[i]

'''
'''
for idx in range(0, len(ckls)):
    print ckls[idx]
'''
print  syb_open
print  sk_open