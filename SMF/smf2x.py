from .bareader import BAReader
from .smf import SMF
from .smf_errors import SMFParseError

class SMF20(SMF):
    smf_description = "Job initiation"

    # noinspection PyAttributeOutsideInit
    def fill(self, reader: BAReader):
        self.smf20jbn = reader.get_string(8).rstrip()
        self.smf20rs_datetime = reader.get_tme_dte()
        self.smf20uid = reader.get_string(8).rstrip()
        reader.read(2)      # smf20rin
        self.smf20pgm = reader.get_string(20)
        smf20naf = reader.get_byte()
        self.smf20act = []
        for _ in range(smf20naf):
            l = reader.get_byte()
            af = reader.get_string(l)
            self.smf20act.append(af)

    def __repr__(self) -> str:
        return self._repr(
            job=self.smf20jbn,
            reader=str(self.smf20rs_datetime)[:-4],
        )

class SMF26(SMF):
    smf_description = "JES Job Purge"

    # noinspection PyAttributeOutsideInit
    def fill(self, reader: BAReader):
        self.smf26jbn = reader.get_string(8).rstrip()
        self.smf26rs_datetime = reader.get_tme_dte()
        reader.read(8 + 4)      # uif, rsv
        smf26sbs = reader.get_halfword()
        if smf26sbs != 2:
            raise SMFParseError("Got a Type 26 record from other than JES2")
        reader.read(2)    # smf26ind

        smf26ln1 = reader.get_halfword()   # smf26ln1
        s_reader = reader.subreader(smf26ln1 - 2)

        s_reader.read(2 + 1 + 1)     # smf26rv1, smf26in2, smf26inf
        self.smf26jnm = s_reader.get_string(4)
        self.smf26jid = s_reader.get_string(8)
        self.smf26nam = s_reader.get_string(20).rstrip()
        self.smf26msg = s_reader.get_string(1)
        self.smf26cls = s_reader.get_string(1)
        s_reader.read(1 + 1 + 1 + 1 + 2)        # xpi, xps, opi, ops, loc
        self.smf26dev = s_reader.get_string(8).rstrip()
        self.smf26act = s_reader.get_string(4).rstrip().replace("\x00", "")
        self.smf26rom = s_reader.get_string(4).rstrip().replace("\x00", "")
        assert s_reader.tell() == 108, f"smf26xtm in wrong place, @ {s_reader.tell()}"
        s_reader.read(4 + 4 + 4 + 4 + 2 + 2 + 2 + 2) # xtm, eln, epu, frm, cyp, lin, prr, pur
        s_reader.get_string(8).rstrip() # pdd
        if s_reader.bytes_remaining() > 0:
            self.logger.info("descriptor section @ %d bytes, %d bytes left over", s_reader.tell(), s_reader.bytes_remaining())

        smf26ln2 = reader.get_halfword()
        reader.read(smf26ln2 - 2)

        smf26ln3 = reader.get_halfword()
        reader.read(smf26ln3 - 2)

        if reader.bytes_remaining() > 0:
            smf26ln4 = reader.get_halfword()
            reader.read(smf26ln4 - 2)

    def __repr__(self) -> str:
        return self._repr(
            job=self.smf26jbn,
            reader=str(self.smf26rs_datetime)[:-4],
        )

