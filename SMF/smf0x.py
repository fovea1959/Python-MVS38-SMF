from typing import cast

from .bareader import BAReader
from .smf import SMF
from .smf_errors import SMFParseError
from .model_lookup import lookup_model_by_class_and_type

class SMF0(SMF):
    smf_description = "IPL Header"

    # noinspection PyAttributeOutsideInit
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

    # noinspection PyAttributeOutsideInit
    def fill(self, reader: BAReader):
        self.smf4jbn = reader.get_string(8).rstrip()
        self.smf4rs_datetime = reader.get_tme_dte()
        reader.get_string(8)    # smf4uif
        self.smf4stn = reader.get_byte()
        self.smf4si_datetime = reader.get_tme_dte()
        self.smf4nci = reader.get_fullword()
        _smf4jcc = reader.get_halfword()
        reader.get_byte()       # smf4jpty
        self.smf4prgn = reader.get_string(8).rstrip()
        self.smf4stmn = reader.get_string(8).rstrip()
        assert reader.tell() == 70, f"smf4rsho in wrong place, @ {reader.tell()}"
        self.smf4rsho = reader.get_halfword()
        self.smf4syst = reader.get_halfword()
        self.smf4host = reader.get_halfword()
        reader.read(6 + 1)          # smf4rv1, smf4spk
        assert reader.tell() == 83, f"smf4sti in wrong place, @ {reader.tell()}"
        _smf4sti = reader.get_byte()
        reader.read(2 + 4 + 4 + 1)          # smf4rv2, ast, ppst, rv3
        assert reader.tell() == 95, f"smf4srbt in wrong place, @ {reader.tell()}"
        reader.get_3byteint()               # smf4srbt
        reader.get_halfword()               # smf4rin

        smf4rlct = reader.get_halfword()
        assert reader.tell() == 102, f"smf4llen in wrong place, @ {reader.tell()}"
        smf4llen = reader.get_halfword()

        s_reader = reader.subreader(smf4llen - 2)
        device_entries = []
        while s_reader.bytes_remaining() >= 8:
            smf4devc = s_reader.get_byte()
            smf4utyp = s_reader.get_byte()
            if smf4devc == 0 and smf4utyp == 0:
                continue
            dt = lookup_model_by_class_and_type(smf4devc, smf4utyp)
            smf4cuad = s_reader.get_halfword()
            smf4excp = s_reader.get_fullword()
            dd = {
                'smf4model': dt,
                'smf4cuad': f'{smf4cuad:03x}',
                'smf4excp': smf4excp,
            }
            device_entries.append(dd)
        self.smf4devices = device_entries
        if s_reader.bytes_remaining() > 0:
            ##### TODO this is happening, investigate
            self.logger.info(f"{s_reader.bytes_remaining()} extra bytes at end of device entries")

        smf4lnth = reader.get_byte()
        s_reader = reader.subreader(smf4lnth)
        self.smf4setm = s_reader.get_3byteint() / 100.0     # convert to seconds
        smf4naf = s_reader.get_byte()
        self.smf4account_fields = []

        for _ in range(smf4naf):
            l = s_reader.get_byte()
            af = s_reader.get_string(l)
            self.smf4account_fields.append(af)

        reader.r.seek(smf4rlct)
        s_reader = reader.subreader(70, offset=0) # s_reader.tell() is now relative to the start of the relocate section
        self.smf4pgin = s_reader.get_fullword()
        self.smf4pgot = s_reader.get_fullword()
        self.smf4nsw = s_reader.get_fullword()
        self.smf4psi = s_reader.get_fullword()
        self.smf4pso = s_reader.get_fullword()
        self.smf4vpi = s_reader.get_fullword()
        self.smf4vpo = s_reader.get_fullword()
        self.smf4sst = s_reader.get_fullword()
        self.smf4act = s_reader.get_seconds_from_1024microsecond_units()
        s_reader.read(2 + 4 + 4 + 4)        # smf4pgmo, tran, recl, rclm
        s_reader.read(4 + 4 + 4)            # smf4cpgm, crcl, pgst
        self.smf4psec = s_reader.get_doubleword()
        if s_reader.bytes_remaining() > 0:
            self.logger.info(f"{s_reader.bytes_remaining()} extra bytes at end of relocatable section")

    def __repr__(self) -> str:
        return self._repr(
            job=self.smf4jbn,
            step=self.smf4stn,
            reader=str(self.smf4rs_datetime)[:-4],
            initiated=str(self.smf4si_datetime)[:-4],
        )

class SMF5(SMF):
    smf_description = "Job Termination"

    # noinspection PyAttributeOutsideInit
    def fill(self, reader: BAReader):
        self.smf5jbn = reader.get_string(8).rstrip()
        self.smf5rs_datetime = reader.get_tme_dte()
        reader.get_string(8)    # smf5uif
        self.smf5nst = reader.get_byte()
        self.smf5ji_datetime = reader.get_tme_dte()
        self.smf5nci = reader.get_fullword()
        _smf5jcc = reader.get_halfword()
        reader.get_byte()       # smf5jpty
        reader.get_tme_dte()    # smf5rstt smf5rstd
        _smf5jbti = reader.get_byte()
        reader.read(1 + 4 + 1 + 1 + 1)  #smf5smci, tran, ckre, rdcl, ruty
        self.smf5jicl = reader.get_string(1)
        assert reader.tell() == 72, f"smf5spk in wrong place, @ {reader.tell()}"
        reader.get_byte()       # smf5spk
        self.smf5spk = reader.get_3byteint()
        self.smf5tjs = reader.get_fullword()
        self.smf5ttat = reader.get_fullword()
        reader.get_fullword()   # smf5rv2
        reader.read(2 + 2)      # smf5pgno, smf5rv3
        # offset s/b 92
        assert reader.tell() == 92, "smf5tlen in wrong place, @ {reader.tell()}"
        smf5tlen = reader.get_byte()

        s_reader = reader.subreader(smf5tlen)
        self.smf5prgn = s_reader.get_string(20).rstrip()
        self.smf5jcpu = s_reader.get_3byteint()
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

    # noinspection PyAttributeOutsideInit
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
