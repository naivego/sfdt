# -*- coding: utf-8 -*-

class Ostpn(object):  #策略订单的开仓、止损、止盈位设置
    # ----------------------------------------------------------------------
    def __init__(self, LgOpn, LgSpn, LgTpn, StOpn, StSpn, StTpn):
        self.LgOpn = LgOpn
        self.LgSpn = LgSpn
        self.LgTpn = LgTpn
        self.StOpn = StOpn
        self.StSpn = StSpn
        self.StTpn = StTpn

class Sdostp(object):  #策略订单的开仓、止损、止盈价位
    # ----------------------------------------------------------------------
    def __init__(self, Opbl, Spbl, Tpbl, det, ostpn):
        self.LgOp = Opbl + ostpn.LgOpn * det
        self.LgSp = Spbl + ostpn.LgSpn * det
        self.LgTp = Tpbl + ostpn.LgTpn * det
        self.StOp = Opbl + ostpn.StOpn * det
        self.StSp = Spbl + ostpn.StSpn * det
        self.StTp = Tpbl + ostpn.StTpn * det

#---------------------------------------------------------------
def grst_qsp(fact,  ostpn, sgnx='2'):
    '''
    :param fact:
    :param ostpn:
    :return: lgsdsp, lgsdtp, lgsdop, stsdsp, stsdtp, stsdop,
    '''
    itp, qsp, prep, rstn, b_rstp, b_zsp, b_bsp, b_det, s_rstp, s_zsp, s_bsp, s_det = fact
    sgnx = sgnx[-1]
    if itp == 0:
        return (None, None, None, None, None, None)
    if itp > 0:
        lgsdop = qsp + ostpn.LgOpn * b_det
        lgsdsp = b_zsp + ostpn.LgSpn * b_det
        lgsdtp = b_zsp + ostpn.LgTpn * b_det

        stsdop = None
        stsdsp = None     #原来止损的位置
        stsdtp = lgsdop   #移动到多头开仓的位置
    else:
        stsdop = qsp + ostpn.StOpn * s_det
        stsdsp = s_zsp + ostpn.StSpn * s_det
        stsdtp = b_zsp + ostpn.StTpn * s_det

        lgsdop = None
        lgsdsp = None    #原来止损的位置
        lgsdtp = stsdop  #移动到空头开仓的位置
    return (lgsdop, lgsdsp, lgsdtp, stsdop, stsdsp, stsdtp)
#---------------------------------------------------------------
def grst_rsp(fact,  ostpn, sgnx='2'):
    '''
    :param fact:
    :param ostpn:
    :return: lgsdsp, lgsdtp, lgsdop, stsdsp, stsdtp, stsdop,
    '''
    itp, qsp, prep, rstn, b_rstp, b_zsp, b_bsp, b_det, s_rstp, s_zsp, s_bsp, s_det = fact
    sgnx = sgnx[-1]
    if itp == 0:
        return (None, None, None, None, None, None)
    if itp > 0:
        if rstn > 6:
            lgsdop = None
        else:
            lgsdop = b_rstp + ostpn.LgOpn * b_det

        if lgsdop:
            lgsdsp = b_zsp + ostpn.LgSpn * b_det
        else:
            lgsdsp = b_zsp + ostpn.LgSpn * b_det

        if sgnx == '1' and lgsdop:
            lgsdtp = lgsdop + ostpn.LgTpn * b_det
        else:
            lgsdtp = b_zsp + ostpn.LgTpn * b_det

        stsdop = None
        stsdsp = None        # 原来止损的位置
        if lgsdop:
            stsdtp = lgsdop  # 移动到多头开仓的位置
        else:
            stsdtp = None    # 原来止盈的位置
    else:
        if rstn > 6:
            stsdop = None
        else:
            stsdop = s_rstp + ostpn.StOpn * s_det

        if stsdop:
            stsdsp = s_zsp + ostpn.StSpn * s_det
        else:
            stsdsp = s_zsp + ostpn.StSpn * s_det

        if sgnx == '1' and stsdop:
            stsdtp = stsdop + ostpn.StTpn * s_det
        else:
            stsdtp = s_zsp + ostpn.StTpn * s_det

        lgsdop = None
        lgsdsp = None         # 原来止损的位置
        if stsdop:
            lgsdtp = stsdop   # 移动到空头开仓的位置
        else:
            lgsdtp = None     # 原来止盈的位置
    return (lgsdop, lgsdsp, lgsdtp, stsdop, stsdsp, stsdtp)


def grst_bsp(fact,  ostpn, sgnx='2'):
    '''
    :param fact:
    :param ostpn:
    :return: lgsdsp, lgsdtp, lgsdop, stsdsp, stsdtp, stsdop,
    '''
    itp, qsp, prep, rstn, b_rstp, b_zsp, b_bsp, b_det, s_rstp, s_zsp, s_bsp, s_det = fact
    sgnx = sgnx[-1]
    if itp == 0:
        return (None, None, None, None, None, None)
    if itp > 0:
        lgsdop = b_bsp + ostpn.LgOpn * b_det
        lgsdsp = b_zsp + ostpn.LgSpn * b_det
        lgsdtp = b_zsp + ostpn.LgTpn * b_det

        stsdop = None
        stsdsp = None     #原来止损的位置
        stsdtp = lgsdop   #移动到多头开仓的位置
    else:
        stsdop = s_bsp + ostpn.StOpn * s_det
        stsdsp = s_zsp + ostpn.StSpn * s_det
        stsdtp = s_zsp + ostpn.StTpn * s_det

        lgsdop = None
        lgsdsp = None    #原来止损的位置
        lgsdtp = stsdop  #移动到空头开仓的位置
    return (lgsdop, lgsdsp, lgsdtp, stsdop, stsdsp, stsdtp)
#---------------------------------------------------------------

def grst_zsp(fact,  ostpn, sgnx='2'):
    '''
    :param fact:
    :param ostpn:
    :return: lgsdsp, lgsdtp, lgsdop, stsdsp, stsdtp, stsdop,
    '''
    itp, qsp, prep, rstn, b_rstp, b_zsp, b_bsp, b_det, s_rstp, s_zsp, s_bsp, s_det = fact
    sgnx = sgnx[-1]
    if itp == 0:
        return (None, None, None, None, None, None)
    if itp > 0:
        lgsdop = b_zsp + ostpn.LgOpn * b_det
        lgsdsp = b_zsp + ostpn.LgSpn * b_det
        lgsdtp = b_zsp + ostpn.LgTpn * b_det

        stsdop = None
        stsdsp = None     #原来止损的位置
        stsdtp = lgsdop   #移动到多头开仓的位置
    else:
        stsdop = s_zsp + ostpn.StOpn * s_det
        stsdsp = s_zsp + ostpn.StSpn * s_det
        stsdtp = s_zsp + ostpn.StTpn * s_det

        lgsdop = None
        lgsdsp = None    #原来止损的位置
        lgsdtp = stsdop  #移动到空头开仓的位置
    return (lgsdop, lgsdsp, lgsdtp, stsdop, stsdsp, stsdtp)
#---------------------------------------------------------------


#---------------------------------------------------------------
def grst_ovr(fact,  ostpn, sgnx='2'):  #----------代表一类超卖超买的反转交易
    '''
    :param fact:
    :param ostpn:
    :return: lgsdsp, lgsdtp, lgsdop, stsdsp, stsdtp, stsdop,
    '''
    itp, qsp, prep, rstn, b_rstp, b_zsp, b_bsp, b_det, s_rstp, s_zsp, s_bsp, s_det = fact
    sgnx = sgnx[-1]
    if itp == 0:
        return (None, None, None, None, None, None)
    if itp < 0:
        lgsdop = s_zsp + ostpn.LgOpn * s_det
        lgsdsp = s_zsp + ostpn.LgSpn * s_det
        lgsdtp = s_zsp + ostpn.LgTpn * s_det
        stsdop = None  # 不开空头
        stsdsp = None  # 依据原来止损
        stsdtp = None  # 依据原来止盈
    else:
        stsdop = b_zsp + ostpn.StOpn * b_det
        stsdsp = b_zsp + ostpn.StSpn * b_det
        stsdtp = b_zsp + ostpn.StTpn * b_det
        lgsdop = None  # 不开空头
        lgsdsp = None  # 依据原来止损
        lgsdtp = None  # 依据原来止盈
    return (lgsdop, lgsdsp, lgsdtp, stsdop, stsdsp, stsdtp)