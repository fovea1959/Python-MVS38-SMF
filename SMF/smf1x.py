from .bareader import BAReader
from .smf import SMF
from .model_lookup import lookup_model_by_class_and_type, lookup_model


class SMF10(SMF):
    smf_description = "Allocation Recovery"

    # noinspection PyAttributeOutsideInit
    def fill(self, reader: BAReader):
        # picking up from after smfxsid
        self.smfxjbn = reader.get_string(8).rstrip()
        self.smfxrst = reader.get_tme_dte()
        reader.get_string(8)    # smf10uif
        smf10ln = reader.get_halfword()
        s_reader = reader.subreader(smf10ln - 2)
        device_entries = []
        while s_reader.bytes_remaining() >= 4:
            devc = s_reader.get_byte()
            utyp = s_reader.get_byte()
            dt = lookup_model_by_class_and_type(devc, utyp)
            smf4cuad = s_reader.get_halfword()
            dd = {
                'smf10model': dt,
                'smf10cuad': f'{smf4cuad:03x}',
            }
            device_entries.append(dd)
        self.smf10devices = device_entries
        if s_reader.bytes_remaining() > 0:
            self.logger.warn("extra bytes at end of device entries")

    def __repr__(self) -> str:
        return self._repr(
            jobname=self.smfxjbn,
        )


class SMF1415(SMF):
    # noinspection PyAttributeOutsideInit
    def fill(self, reader: BAReader):
        # picking up from after smfxsid
        self.smfxjbn = reader.get_string(8).rstrip()
        self.smfxrst = reader.get_tme_dte()
        reader.get_string(8)    # smf14uid
        smf14rin = reader.get_halfword()
        smf14sdc = reader.get_byte()
        assert smf14sdc == 24
        smf14nuc = reader.get_byte()
        smf14suc = reader.get_byte()
        assert smf14suc == 24
        smf14set = reader.get_byte()
        smf14rv1 = reader.get_fullword()
        reader.read(16)     # TIOT section
        assert reader.tell() == 64, "SMFJFCB1 in wrong places"
        reader.read(176)    # JFCB1

        dcbdeb = reader.subreader(smf14sdc)
        while dcbdeb.bytes_remaining() > 0:
            dcbdeb.read(2 + 1 + 2 + 1 + 1 + 1 + 1 + 1 + 2)  # smfdcbor .. smfdebvl
            dcbdeb.read(12)     # either a tape or dasd extension

        ucb = reader.subreader(smf14nuc*smf14suc)
        for _ in range(smf14nuc):
            ucb.read(1 + 1 + 6 + 4 + 1 + 1 + 2 + 4 + 4)     # read a section
        if ucb.bytes_remaining() > 0:
            self.logger.warn("extra bytes at end of UCB section")

        ### TODO: pick up ISAM extension section


    def __repr__(self) -> str:
        return self._repr(
            jobname=self.smfxjbn,
        )


class SMF14(SMF1415):
    smf_description = "Input or RDBACK Device Activity"


class SMF15(SMF1415):
    smf_description = "OUTPUT, UPDAT, INOUT, or OUTIN Data Set Activity"


class SMF19(SMF):
    smf_description = "Direct Access Volume"

    # noinspection PyAttributeOutsideInit
    def fill(self, reader: BAReader):
        # picking up from after smfxsid
        smf19rv1 = reader.get_halfword()
        self.smf19vol = reader.get_string(6).rstrip()
        reader.get_string(10)   # smf19oid
        smf19dev = reader.get_fullword()
        self.smf19dev = lookup_model(smf19dev)
        reader.read(5 + 1)  # vtc, vti
        self.smf19nds = reader.get_halfword()
        self.smf19dsr = reader.get_halfword()
        reader.get_halfword()   # smf19nat
        self.smf19spc_cyl = reader.get_halfword()
        self.smf19spc_trk = reader.get_halfword()
        self.smf19lex_cyl = reader.get_halfword()
        self.smf19lex_trk = reader.get_halfword()
        self.smf19nue = reader.get_halfword()
        reader.get_halfword()   # smf19rv2
        smf19cuu = reader.get_halfword()
        self.smf19cuad = f'{smf19cuu:03x}'
        reader.get_halfword()   # smf19ind


    def __repr__(self) -> str:
        return self._repr(
            jobname=self.smf19vol,
        )
