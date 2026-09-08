from .bareader import BAReader
from .smf import SMF
from .smf_errors import SMFParseError

class SMF0(SMF):
    smf_description = "IPL Header"

    def __init__(self):
        super().__init__()
        self.smf0vst = None
        self.smf0rst = None
        self.smf0osl = None
        self.smf0syn = None

    def fill(self, reader: BAReader):
        reader.get_fullword()  # smf0jwt
        reader.get_fullword()  # smf0buf
        self.smf0vst = reader.get_fullword()
        reader.get_byte()      # smf0opt
        self.smf0rst = reader.get_fullword()
        if reader.bytes_remaining() > 0:
            reader.get_byte()      # smf0rsv
        if reader.bytes_remaining() > 0:
            self.smf0osl = reader.get_string(8)
        if reader.bytes_remaining() > 0:
            self.smf0syn = reader.get_string(8)

    def __repr__(self) -> str:
        return self._repr(
            virtual=self.smf0vst,
            real=self.smf0rst,
            product=self.smf0osl,
            sysname=self.smf0syn,
        )


class SMF2(SMF):
    smf_description = "Dump header"


class SMF3(SMF):
    smf_description = "Dump trailer"


class SMF4(SMF):
    smf_description = "Step Termination"

    def __init__(self):
        super().__init__()
        self.smf4jbn = None
        self.smf4rs_datetime = None
        self.smf4stn = None
        self.smf4si_datetime = None

    def fill(self, reader: BAReader):
        self.smf4jbn = reader.get_string(8).rstrip()
        self.smf4rs_datetime = reader.get_tme_dte()
        reader.get_string(8)    # smf4uif
        self.smf4stn = reader.get_byte()
        self.smf4si_datetime = reader.get_tme_dte()
        self.smf4nci = reader.get_fullword()
        smf4jcc = reader.get_halfword()
        reader.get_byte()       # smf4jpty
        self.smf4prgn = reader.get_string(8).rstrip()
        self.smf4stmn = reader.get_string(8).rstrip()
        assert reader.tell() == 70, f"smf4rsh0 in wrong place, @ {reader.tell()}"
        self.smf4rsh0 = reader.get_halfword()       #### TODO spelling ####
        self.smf4syst = reader.get_halfword()
        self.smf4h0st = reader.get_halfword()       # check spelling ################ TODO ####################
        reader.read(6 + 1)          # smf4rv1, smf4spk
        assert reader.tell() == 83, f"smf4sti in wrong place, @ {reader.tell()}"
        smf4sti = reader.get_byte()
        reader.read(2 + 4 + 4 + 1)          # smf4rv2, ast, ppst, rv3
        assert reader.tell() == 95, f"smf4srbt in wrong place, @ {reader.tell()}"
        self.smf4srbt = reader.read(3)              ################## TODO ########################
        reader.get_halfword()                 # smf4rin

        smf4rlct = reader.get_halfword()
        assert reader.tell() == 102, f"smf4llen in wrong place, @ {reader.tell()}"
        smf4llen = reader.get_halfword()
        self.smf5jicl = reader.get_string(1)

        '''
        assert reader.tell() == 72, 
        reader.get_byte()       # smf5spk
        reader.read(3)          # smf5srbt  ########################### TODO ##############################
        self.smf5tjs = reader.get_fullword()
        self.smf5ttat = reader.get_fullword()
        reader.get_fullword()   # smf5rv2
        reader.read(2 + 2)      # smf5pgno, smf5rv3
        # offset s/b 92
        assert reader.tell() == 92, "smf5tlen in wrong place, @ {reader.tell()}"
        smf5tlen = reader.get_byte()

        s_reader = reader.subreader(smf5tlen)
        self.smf5prgn = s_reader.get_string(20).rstrip()
        smf5jcpu = s_reader.read(3)             ################## TODO ##################
        smf5actf = s_reader.get_byte()
        self.smf5act = []

        for _ in range(smf5actf):
            l = s_reader.get_byte()
            af = s_reader.get_string(l)
            self.smf5act.append(af)
        '''

    def __repr__(self) -> str:
        return self._repr(
            job=self.smf4jbn,
            step=self.smf4stn,
            reader=str(self.smf4rs_datetime)[:-4],
            initiated=str(self.smf4si_datetime)[:-4],
        )

class SMF5(SMF):
    smf_description = "Job Termination"

    def __init__(self):
        super().__init__()
        self.smf5jbn = None
        self.smf5rs_datetime = None
        self.smf5nst = None
        self.smf5ji_datetime = None
        self.smf5nci = None
        self.smf5jicl = None
        self.smf5tjs = None
        self.smf5ttat = None
        self.smf5prgn = None
        self.smf5jcpu = None
        self.smf5act = None

    def fill(self, reader: BAReader):
        self.smf5jbn = reader.get_string(8).rstrip()
        self.smf5rs_datetime = reader.get_tme_dte()
        reader.get_string(8)    # smf5uif
        self.smf5nst = reader.get_byte()
        self.smf5ji_datetime = reader.get_tme_dte()
        self.smf5nci = reader.get_fullword()
        smf5jcc = reader.get_halfword()
        reader.get_byte()       # smf5jpty
        reader.get_tme_dte()    # smf5rstt smf5rstd
        smf5jbti = reader.get_byte()
        reader.read(1 + 4 + 1 + 1 + 1)  #smf5smci, tran, ckre, rdcl, ruty
        self.smf5jicl = reader.get_string(1)
        assert reader.tell() == 72, f"smf5spk in wrong place, @ {reader.tell()}"
        reader.get_byte()       # smf5spk
        reader.read(3)          # smf5srbt  ########################### TODO ##############################
        self.smf5tjs = reader.get_fullword()
        self.smf5ttat = reader.get_fullword()
        reader.get_fullword()   # smf5rv2
        reader.read(2 + 2)      # smf5pgno, smf5rv3
        # offset s/b 92
        assert reader.tell() == 92, "smf5tlen in wrong place, @ {reader.tell()}"
        smf5tlen = reader.get_byte()

        s_reader = reader.subreader(smf5tlen)
        self.smf5prgn = s_reader.get_string(20).rstrip()
        smf5jcpu = s_reader.read(3)             ################## TODO ##################
        smf5actf = s_reader.get_byte()
        self.smf5act = []

        for _ in range(smf5actf):
            l = s_reader.get_byte()
            af = s_reader.get_string(l)
            self.smf5act.append(af)



    def __repr__(self) -> str:
        return self._repr(
            job=self.smf5jbn,
            steps=self.smf5nst,
            reader=str(self.smf5rs_datetime)[:-4],
            initiated=str(self.smf5ji_datetime)[:-4],
        )


class SMF6(SMF):
    smf_description = "JES Output Writer"

    def __init__(self):
        super().__init__()
        self.smf6jbn = None
        self.smf6rs_datetime = None
        self.smf6owc = None
        self.smf6ws_datetime = None
        self.smf6nlr = None
        self.smf6nds = None
        self.smf6fmn = None
        self.smf6out = None
        self.smf6jnm = None
        self.smf6pge = None

    def fill(self, reader: BAReader):
        self.smf6jbn = reader.get_string(8).rstrip()
        self.smf6rs_datetime = reader.get_tme_dte()
        reader.get_string(8)    # smf6uif
        self.smf6owc = reader.get_string(1)
        self.smf6ws_datetime = reader.get_tme_dte()
        self.smf6nlr = reader.get_fullword()
        reader.get_byte()       # smf6ioe
        self.smf6nds = reader.get_byte()
        self.smf6fmn = reader.get_string(4)
        reader.get_byte()       # smf6pad1
        reader.get_halfword()   # smf6sbs

        reader.get_halfword()  # smf6ln1
        reader.read(1)  # smf6dci
        smf6indc = reader.get_byte()
        if smf6indc == 0:
            self.smf6jnm = reader.get_string(4)
        else:
            reader.read(4)
        self.smf6out = reader.get_string(8).rstrip()
        reader.get_string(4)    # smf6fcb
        reader.get_string(4)    # smf6ucs
        self.smf6pge = reader.get_fullword()
        reader.get_halfword()   # smf6rte

    def __repr__(self) -> str:
        return self._repr(job=self.smf6jbn, reader=str(self.smf6rs_datetime)[:-4])
