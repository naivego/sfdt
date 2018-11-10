# encoding: UTF-8
from __future__ import division
import os
import re
import time
import pandas as pd
import numpy as np
import datetime
from copy import deepcopy
from datetime import datetime, timedelta






 #***********************************************************************
    #****************以下为CS 策略计算因子所需要的函数************************

def var_select(data1, selectlength, threshold):
         data    = deepcopy(data1)
         value   = data.rolling(window = selectlength).mean()
         value1  = data.rolling(window = selectlength).min()
         data[data != np.nan] = np.nan
         data[(value >= threshold) & (value1 >= ((threshold*2)/3.0))] = 1
         return data

#-----------------------------------------------------------------------
def mom_factor(data1,length):
          data    = deepcopy(data1)
          value   = data/data.shift(length)-1
          return value

#-----------------------------------------------------------------------
def stock1_factor(data, period, dir1 = None):
         factor      = pd.DataFrame(index = data.index, columns = data.columns)
         value       = deepcopy(data)
         pastvalue   = value.shift(period)
         pastvalue[pastvalue[pastvalue.columns]== 0] = np.nan
         factor      = (value - pastvalue)/pastvalue
         if dir1:
             factor.to_csv(dir1)
         else:
             return factor

#---------------------------------------------------------------------
def stock3_factor(data, period, dir1 = None):
         factor      = pd.DataFrame(index = data.index, columns = data.columns)
         value       = deepcopy(data)
         pastvalue   = value.shift(period)
         pastvalue[pastvalue[pastvalue.columns]== 0] = np.nan
         value[value[value.columns]==0] = np.nan
         factor      = (value - pastvalue)/pastvalue
         if dir1:
             factor.to_csv(dir1)
         else:
             return factor

#--------------------------------------------------------------------
def roll_factor(DomDf, MongDB):
        factor  = pd.DataFrame(index = DomDf.index,columns =['SL','SM'])
        day     = DomDf.index[-1]
        var     = DomDf.ix[day,'var']
        pv      = MongDB.find({'date':day,'var':var})
        if pv.count()==0:
            print 'cs_factor: roll', var ,' data not find in db!'
        pv      = list(pv)
        pv      = pd.DataFrame(pv)
        pv.ix[:,'_id'] = pv.ix[0,'_id']
        pv_dup  = pv.duplicated()
        if pv_dup.sum()!= 0:
            print 'cs_factor: roll ',var,' repeated data!'
            pv      = pv.drop_duplicates()
        pv      = pv.sort_values(by = ['lastTradeDate'])  # lastdelivery_date
        try:
           s1p   = pv.ix[0,'close']
           s1d   = pv.ix[0,'lastTradeDate']
           s2p   = pv.ix[pv.index[-1],'close']
           s2d   = pv.ix[pv.index[-1],'lastTradeDate']
           rsl   = 365*(np.log(s1p)-np.log(s2p))/((s2d-s1d).days)
        except:
            rsl  = np.nan
        try:
           s1p   = pv.ix[0,'close']
           s1d   = pv.ix[0,'lastTradeDate']
           domp  = DomDf.ix[day,'close']
           domd  = DomDf.ix[day,'lastTradeDate']
           rsm   = 365*(np.log(s1p)-np.log(domp))/((domd-s1d).days)
        except:
            rsm  = np.nan
        factor.ix[day,'SL'] = rsl
        factor.ix[day,'SM'] = rsm
        return factor

        # 计算多日因子
        '''
        factor  = pd.DataFrame(index = DomDf.index,columns =['2S','SM'])
        for day in DomDf.index:
            var   = DomDf.ix[day,'var']
            pv    = MongDB.find({'date':day,'var':var})
            pv    = list(pv)
            pv    = pd.DataFrame(pv)
            pv    = pv.sort_values(by = ['lastTradeDate'])  # lastdelivery_date
            try:
               s1p   = pv.ix[0,'close'] 
               s1d   = pv.ix[0,'lastTradeDate']
               s2p   = pv.ix[1,'close']
               s2d   = pv.ix[1,'lastTradeDate']
               r2s   = 365*(np.log(s1p)-np.log(s2p))/((s2d-s1d).days)
            except:
                r2s  = np.nan
            try:
               s1p   = pv.ix[0,'close'] 
               s1d   = pv.ix[0,'lastTradeDate']
               domp  = DomDf.ix[day,'close']
               domd  = DomDf.ix[day,'lastTradeDate']
               rsm   = 365*(np.log(s1p)-np.log(domp))/((domd-s1d).days)
            except:
                rsm  = np.nan 
            factor.ix[day,'2S'] = r2s
            factor.ix[day,'SM'] = rsm
        return factor
        '''

#----------------------------------------------------------------------
def basis_factor(DomDf, MongDB, SLDay, SMDay):
        factor = pd.DataFrame(index = DomDf.index, columns = ['SL','SM'])
        index1 = DomDf.shape[0]-1
        var  = DomDf.ix[DomDf.index[index1],'var']
        try:
           SLTday = DomDf.index[index1-SLDay+1]
           hpv    = MongDB.find({'date':SLTday,'var':var})
           if hpv.count() == 0:
               print 'cs_factor: basis', var, ' data not find in db!'
           hpv    = list(hpv)
           hpv    = pd.DataFrame(hpv)
           hpv.ix[:, '_id'] = hpv.ix[0, '_id']
           hpv_dup = hpv.duplicated()
           if hpv_dup.sum() != 0:
               print 'cs_factor: basis ', var, ' repeated data!'
               hpv = hpv.drop_duplicates()
           hpv    = hpv.sort_values(by = ['lastTradeDate'])
           hsp    = hpv.ix[0,'close']
           hss    = hpv.ix[0,'symbol']
           hlp    = hpv.ix[hpv.index[-1],'close']
           hls    = hpv.ix[hpv.index[-1],'symbol']
           day    = DomDf.index[index1]
           dpv    = MongDB.find({'date':day,'var':var})
           if dpv.count() == 0:
               print 'cs_factor: basis', var, ' data not find in db!'
           dpv    = list(dpv)
           dpv    = pd.DataFrame(dpv)
           dpv.ix[:, '_id'] = dpv.ix[0, '_id']
           dpv_dup = dpv.duplicated()
           if dpv_dup.sum() != 0:
               print 'cs_factor: basis ', var, ' repeated data!'
               dpv = dpv.drop_duplicates()
           dpv    = dpv.sort_values(by = ['lastTradeDate'])
           dsp    = dpv.ix[0,'close']
           dss    = dpv.ix[0,'symbol']
           dlp    = dpv.ix[dpv.index[-1],'close']
           dls    = dpv.ix[dpv.index[-1],'symbol']
           if (hss == dss) and (hls == dls):
               SL = (dsp/hsp) - (dlp/hlp)
           else:
               SL = np.nan
        except:
            SL  = np.nan
        try:
           SMTday = DomDf.index[index1-SMDay+1]
           hpv    = MongDB.find({'date':SMTday,'var':var})
           if hpv.count() == 0:
               print 'cs_factor: basis', var, ' data not find in db!'
           hpv    = list(hpv)
           hpv    = pd.DataFrame(hpv)
           hpv.ix[:, '_id'] = hpv.ix[0, '_id']
           hpv_dup = hpv.duplicated()
           if hpv_dup.sum() != 0:
               print 'cs_factor: basis ', var, ' repeated data!'
               hpv = hpv.drop_duplicates()
           hpv    = hpv.sort_values(by = ['lastTradeDate'])
           hsp    = hpv.ix[0,'close']
           hss    = hpv.ix[0,'symbol']
           hmp    = DomDf.ix[SMTday, 'close']
           hms    = DomDf.ix[SMTday, 'symbol']
           day    = DomDf.index[index1]
           dpv    = MongDB.find({'date':day,'var':var})
           if dpv.count() == 0:
               print 'cs_factor: basis', var, ' data not find in db!'
           dpv    = list(dpv)
           dpv    = pd.DataFrame(dpv)
           dpv.ix[:, '_id'] = dpv.ix[0, '_id']
           dpv_dup = dpv.duplicated()
           if dpv_dup.sum() != 0:
               print 'cs_factor: basis ', var, ' repeated data!'
               dpv = dpv.drop_duplicates()
           dpv    = dpv.sort_values(by = ['lastTradeDate'])
           dsp    = dpv.ix[0,'close']
           dss    = dpv.ix[0,'symbol']
           dmp    = DomDf.ix[day,'close']
           dms    = DomDf.ix[day,'symbol']
           if (hss == dss) and (hms == dms):
               SM  = (dsp/hsp) - (dmp/hmp)
           else:
               SM  = np.nan
        except:
            SM = np.nan
        factor.ix[DomDf.index[index1],'SL'] = SL
        factor.ix[DomDf.index[index1],'SM'] = SM
        return factor
        # 计算多日因子
        '''
        factor = pd.DataFrame(index = DomDf.index, columns = ['SL','SM'])
        for index1 in range(DomDf.shape[0]):
            var  = DomDf.ix[DomDf.index[index1],'var']
            if index1 < SLDay-1:
                SL  = np.nan
            else:
                try:
                   SLTday = DomDf.index[index1-SLDay+1]
                   hpv    = MongDB.find({'date':SLTday,'var':var})
                   hpv    = list(hpv)
                   hpv    = pd.DataFrame(hpv)
                   hpv    = hpv.sort_values(by = ['lastTradeDate'])
                   hsp    = hpv.ix[0,'close']
                   hss    = hpv.ix[0,'symbol']
                   hlp    = hpv.ix[hpv.index[-1],'close']
                   hls    = hpv.ix[hpv.index[-1],'symbol']
                   day    = DomDf.index[index1]
                   dpv    = MongDB.find({'date':day,'var':var})
                   dpv    = list(dpv)
                   dpv    = pd.DataFrame(dpv)
                   dpv    = dpv.sort_values(by = ['lastTradeDate'])
                   dsp    = dpv.ix[0,'close']
                   dss    = dpv.ix[0,'symbol']
                   dlp    = dpv.ix[dpv.index[-1],'close']
                   dls    = dpv.ix[dpv.index[-1],'symbol']
                   if (hss == dss) and (hls == dls):
                       SL = (dsp/hsp) - (dlp/hlp)
                   else:
                       SL = np.nan
                except:
                    SL  = np.nan
            if index1 < SMDay-1:
                SM  = np.nan
            else:
                try:
                   SMTday = DomDf.index[index1-SMDay+1]
                   hpv    = MongDB.find({'date':SMTday,'var':var})
                   hpv    = list(hpv)
                   hpv    = pd.DataFrame(hpv)
                   hpv    = hpv.sort_values(by = ['lastTradeDate'])
                   hsp    = hpv.ix[0,'close']
                   hss    = hpv.ix[0,'symbol']
                   hmp    = DomDf.ix[SMTday, 'close']
                   hms    = DomDf.ix[SMTday, 'symbol']
                   day    = DomDf.index[index1]
                   dpv    = MongDB.find({'date':day,'var':var})
                   dpv    = list(dpv)
                   dpv    = pd.DataFrame(dpv)
                   dpv    = dpv.sort_values(by = ['lastTradeDate'])
                   dsp    = dpv.ix[0,'close']
                   dss    = dpv.ix[0,'symbol']
                   dmp    = DomDf.ix[day,'close']
                   dms    = DomDf.ix[day,'symbol']
                   if (hss == dss) and (hms == dms):
                       SM  = (dsp/hsp) - (dmp/hmp)
                   else:
                       SM  = np.nan
                except:
                    SM = np.nan
            factor.ix[DomDf.index[index1],'SL'] = SL
            factor.ix[DomDf.index[index1],'SM'] = SM
        return factor
        '''

#----------------------------------------------------------------------
def basa_factor(DomDf, MongDB, SLDay):
       factor = pd.DataFrame(index = DomDf.index, columns = ['SL'])
       index1 = DomDf.shape[0]-1
       var  = DomDf.ix[DomDf.index[index1],'var']
       try:
           SLTdays = DomDf.index[index1-SLDay+1:index1+1]
           SRe = 1
           LRe = 1
           for day in SLTdays:
               pv = MongDB.find({'date':day,'var':var})
               if pv.count() == 0:
                   print 'cs_factor: basa', var, ' data not find in db!'
               pv = list(pv)
               pv = pd.DataFrame(pv)
               pv.ix[:, '_id'] = pv.ix[0, '_id']
               pv_dup = pv.duplicated()
               if pv_dup.sum() != 0:
                   print 'cs_factor: basa ', var, ' repeated data!'
                   pv = pv.drop_duplicates()
               pv = pv.sort_values(by = ['lastTradeDate'])
               S  = 0
               while (S< (pv.shape[0])) and ((pv.ix[pv.index[S],'close'] != pv.ix[pv.index[S],'close']) or (pv.ix[pv.index[S],'preClosePrice'] != pv.ix[pv.index[S],'preClosePrice'])):
                    S = S+1
               if S < pv.shape[0]:
                   dSRe = pv.ix[S,'close']/pv.ix[S,'preClosePrice']
               else:
                   dSRe = np.nan
               L  = pv.shape[0]-1
               while L>=0 and ((pv.ix[pv.index[L],'close'] != pv.ix[pv.index[L],'close']) or (pv.ix[pv.index[L],'preClosePrice'] != pv.ix[pv.index[L],'preClosePrice'])):
                   L = L-1
               if L < 0:
                   dLRe = np.nan
               else:
                   dLRe = pv.ix[pv.index[L],'close']/pv.ix[pv.index[L],'preClosePrice']
               SRe  = SRe*dSRe
               LRe  = LRe*dLRe
           SL = SRe-LRe
                   #print SL
       except:
                    SL = np.nan
       factor.ix[DomDf.index[index1],'SL'] = SL
       return factor
       # 计算多日因子
       '''
       factor = pd.DataFrame(index = DomDf.index, columns = ['SL'])
       for index1 in range(DomDf.shape[0]):
            var  = DomDf.ix[DomDf.index[index1],'var']
            if index1 < SLDay-1:
                SL  = np.nan
            else:
                try:
                   SLTdays = DomDf.index[index1-SLDay+1:index1+1]
                   SRe = 1
                   LRe = 1
                   for day in SLTdays:
                       pv = MongDB.find({'date':day,'var':var})
                       pv = list(pv)
                       pv = pd.DataFrame(pv)
                       pv = pv.sort_values(by = ['lastTradeDate'])
                       S  = 0
                       while (S< (pv.shape[0])) and ((pv.ix[pv.index[S],'close'] != pv.ix[pv.index[S],'close']) or (pv.ix[pv.index[S],'preClosePrice'] != pv.ix[pv.index[S],'preClosePrice'])):
                            S = S+1
                       if S < pv.shape[0]:
                           dSRe = pv.ix[S,'close']/pv.ix[S,'preClosePrice']
                       else:
                           dSRe = np.nan
                       L  = pv.shape[0]-1
                       while L>=0 and ((pv.ix[pv.index[L],'close'] != pv.ix[pv.index[L],'close']) or (pv.ix[pv.index[L],'preClosePrice'] != pv.ix[pv.index[L],'preClosePrice'])):
                           L = L-1
                       if L < 0:
                           dLRe = np.nan
                       else:
                           dLRe = pv.ix[pv.index[L],'close']/pv.ix[pv.index[L],'preClosePrice']
                       SRe  = SRe*dSRe
                       LRe  = LRe*dLRe
                   SL = SRe-LRe
                   #print SL
                except:
                    SL = np.nan
            factor.ix[DomDf.index[index1],'SL'] = SL
       return factor
       '''

#----------------------------------------------------------------------
def calc_ewmvar(Input_Df, Span = 30, Dropna = False):
        if type(Input_Df) == pd.Panel:
            Input_Df = Input_Df.iloc[:,:,0]
        Input_Df_Index = Input_Df.index
        if Dropna:
            Input_Df.dropna(inplace = True)
        #Output_Df = np.sqrt(pd.ewmvar(Input_Df, span=Span) * 261)
        Output_Df = np.sqrt(Input_Df.ewm(span=Span).var(bias=False) * 261)
        Output_Df = Output_Df.reindex(Input_Df_Index)
        Output_Df.fillna(method = 'ffill', inplace = True)
        return Output_Df

    #**************CS 策略因子计算函数结束******************************
    #********************************************************************