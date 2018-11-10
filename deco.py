class Trpline(object):
    def __init__(self, trpb, trpd, atr, tbl):
        self.trpb = trpb  # ���
        self.trpd = trpd  # �˵�
        self.tbl= tbl     # ���������� 'ttl' or 'bbl'
        self.dir = 1 if tbl == 'bbl' else -1
        self.tdlna = tbl+'_' + str(trpb.ski) + '_' + str(trpd.ski)
        self.socna = None
        self.fsocna = None
        self.ak = (trpd.skp - trpb.skp)/(trpd.ski- trpb.ski)
        self.rk = (trpd.skp - trpb.skp)/(trpd.ski- trpb.ski)/trpd.skp/atr  # ƽ��ÿ���Ƿ����atr�ı���
        self.fbi = None
        self.mxi = None
        self.btm = None #  tdl�����ʱ��
        self.dtm = None  # tdl���Ҷ˵�ʱ��
        self.frtm = None # ����tdl��ʱ��
        self.srk  = None  # б�ʱ�׼�÷�
        self.srsk = None  # ��sk�赲��׼�÷�
        self.sfs  = 0     # �ϼƱ�׼�÷�
        self.ocover = 0
        self.hlover = 0
        self.pdreach = 0

        self.initi = None
        self.exti = self.trpd.ski
        self.extp = self.trpd.skp

        self.bki = None   # ��skͻ�Ƶ�λ�� None�� δ��ͻ��
        self.bkp = None   # ��skͻ�Ƶļ۸�
        self.eop = None   # ͻ��SK�⼫��
        self.eip = None   # �ٽ�sk�ڼ���

        self.bkcn= 0   # ͻ�ƴ���
        self.rsta = 0     # sk ��������ߵĹ�ϵ״̬ 0��δ��ͻ�ƣ�  >0:��ͻ�� -1��ʧЧ
        self.crsp = None  # Ԥ�Ƶ�ǰ��sk�赲�ļ۸���� ʧЧ��ΪNone ��
        self.rspdet = None  # sk���̼��������赲�۲������atr�ı���
        self.mpti = None  # sk���ƫ��tdl��Զ��λ��
        self.mptv = None  # sk���ƫ��tdl��Զ�ļ۸�
        self.bkmpti = None  # ͻ��tdl���sk���ƫ��tdl��Զ��λ��
        self.bkmptv = None  # ͻ��tdl���sk���ƫ��tdl��Զ�ļ۸�
        # ----------------- fibo �ź����
        self.sfib = None # ����fibo�÷�
        self.fib0 = None
        self.fib1 = None
        self.fibr = None
        self.fib16 = None
        self.fib2 = None
        self.fib26 = None
        self.fib3 = None
        self.fib42 = None
        self.catfb = None # ��ǰ���̼۴���fibon����е�λ��
        self.fbrh0 = None

        #-----------------�����׽�������ص��ź�ͳ��
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
        # ------------------------------sadl���
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

        # ----------------------tdl����ڱ�����sk��λ��״̬

        self.se_ini = None  # ����tdlʱ���ⲿsk������
        self.se_upti = None  # �������ʱ������i
        self.se_sta = None  # sk ���tdl��״̬��ż��--��tdl�ڲ࣬����--��� ÿ������Խ��ֵ����1
        self.se_beks = []   # sk����ഩԽtdl��ski�б�
        self.se_reks = []   # sk���ڲഩԽtdl��ski�б�
        self.se_berhs = []  # sk����ഥ��tdl��ski�б�
        self.se_rerhs = []  # sk���ڲഥ��tdl��ski�б�


        self.se_bkl_sta = None  # sk ���bkl��״̬��ż��--��bkl�ڲ࣬����--��� ÿ������Խ��ֵ����1
        self.se_bkl_beks = []  # sk����ഩԽtdl��ski�б�
        self.se_bkl_reks = []  # sk���ڲഩԽtdl��ski�б�
        self.se_bkl_berhs = []  # sk����ഥ��bkl��ski�б�
        self.se_bkl_rerhs = []  # sk���ڲഥ��bkl��ski�б�


        self.se_bki = None  # ��ʽͻ��i
        self.se_bekp = None  # ��ʽ���ּ�
        self.se_besp = None  # ��ʽֹ���

        self.se_bek1i = None   #
        self.se_bek2i = None   #
        self.se_bek3i = None  #

        self.se_bek0sta = None
        self.se_bek1sta = None
        self.se_bek2sta = None
        self.se_bek3sta = None

        self.se_rti = None  # �ع�ͻ��i
        self.se_rekp = None  # �ع鿪�ּ�
        self.se_resp = None  # �ع�ֹ���

        self.se_rek1i = None  #
        self.se_rek2i = None  #
        self.se_rek3i = None  #

        self.se_rek0sta = None
        self.se_rek1sta = None
        self.se_rek2sta = None
        self.se_rek3sta = None

        #----------------------tdl������ⲿ����sk��λ��״̬
        self.et_ini  = None  # ����tdlʱ���ⲿsk������
        self.et_sta = None  # sk ���tdl��״̬��ż��--��tdl�ڲ࣬����--��� ÿ������Խ��ֵ����1
        self.et_beks = []  # sk����ഩԽtdl��ski�б�
        self.et_reks = []  # sk���ڲഩԽtdl��ski�б�
        self.et_berhs = []  # sk����ഥ��tdl��ski�б�
        self.et_rerhs = []  # sk���ڲഥ��tdl��ski�б�

        self.et_bkl_sta = None  # sk ���bkl��״̬��ż��--��bkl�ڲ࣬����--��� ÿ������Խ��ֵ����1
        self.et_bkl_beks = []  # sk����ഩԽtdl��ski�б�
        self.et_bkl_reks = []  # sk���ڲഩԽtdl��ski�б�
        self.et_bkl_berhs = []  # sk����ഥ��bkl��ski�б�
        self.et_bkl_rerhs = []  # sk���ڲഥ��bkl��ski�б�


        self.et_bki  = None  # ��ʽͻ��i
        self.et_bekp = None  # ��ʽ���ּ�
        self.et_besp = None  # ��ʽֹ���

        self.et_bek1i = None  #
        self.et_bek2i = None  #
        self.et_bek3i = None  #
        self.et_bek0sta = None
        self.et_bek1sta = None
        self.et_bek2sta = None
        self.et_bek3sta = None

        self.et_rti = None  # �ع�ͻ��i
        self.et_rekp = None  # �ع鿪�ּ�
        self.et_resp = None  # �ع�ֹ���
        self.et_rek1i = None  #
        self.et_rek2i = None  #
        self.et_rek3i = None  #
        self.et_rek0sta = None
        self.et_rek1sta = None
        self.et_rek2sta = None
        # ------------------------------�����ź�
        self.trpkops = {}
        self.trpcsts = {}
        self.trpctps = {}

        #-----------------��Ч״̬
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