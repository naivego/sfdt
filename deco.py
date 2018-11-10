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

        self.se_bek0sta = None
        self.se_bek1sta = None
        self.se_bek2sta = None
        self.se_bek3sta = None

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
        self.et_sta = None  # sk 相对tdl的状态，偶数--在tdl内侧，奇数--外侧 每发生穿越，值增加1
        self.et_beks = []  # sk向外侧穿越tdl的ski列表
        self.et_reks = []  # sk向内侧穿越tdl的ski列表
        self.et_berhs = []  # sk从外侧触及tdl的ski列表
        self.et_rerhs = []  # sk从内侧触及tdl的ski列表

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
        self.et_bek0sta = None
        self.et_bek1sta = None
        self.et_bek2sta = None
        self.et_bek3sta = None

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