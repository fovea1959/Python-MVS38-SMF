from .bareader import BAReader

from .smf import SMF
from .smf_errors import SMFParseError


class SMF26(SMF):
    smf_description = "JES Job Purge"

    # offsets are from GC28-0764.
    # the pacsys docsuments offsets are off by 4 because they include the RDW

    def __init__(self):
        super().__init__()
        self.smf26jbn = None
        self.smf26rs_datetime = None
        self.smf26jnm = None
        self.smf26jid = None
        self.smf26nam = None
        self.smf26msg = None
        self.smf26cls = None
        self.smf26dev = None
        self.smf26act = None
        self.smf26rom = None

    def fill(self, reader: BAReader):
        self.smf26jbn = reader.get_string(8).rstrip()
        self.smf26rs_datetime = reader.get_tme_dte()
        reader.read(8 + 4)      # uif, rsv
        smf26sbs = reader.get_halfword()
        if smf26sbs != 2:
            raise SMFParseError("Got a Type 26 record from other than JES2")
        reader.read(2)    # smf26ind

        smf26ln1_start = reader.tell() + 2      # 2 = length of smfln1
        smf26ln1 = reader.get_halfword()   # smf26ln1

        smf26ln1_buffer = reader.read(smf26ln1 - 2)

        if True:
            s_reader = BAReader(smf26ln1_buffer)
            # self.logger.info("reading smf26rv1 @ %d bytes", smf26ln1_start + s_reader.tell())
            s_reader.read(2 + 1 + 1)     # smf26rv1, smf26in2, smf26inf
            self.smf26jnm = s_reader.get_string(4)
            self.smf26jid = s_reader.get_string(8)
            self.smf26nam = s_reader.get_string(20).rstrip()
            self.smf26msg = s_reader.get_string(1)
            # self.logger.info("reading smf26cls @ %d bytes", smf26ln1_start + s_reader.tell())
            self.smf26cls = s_reader.get_string(1)
            s_reader.read(1 + 1 + 1 + 1 + 2)        # xpi, xps, opi, ops, loc
            self.smf26dev = s_reader.get_string(8).rstrip()
            self.smf26act = s_reader.get_string(4).rstrip()
            self.smf26rom = s_reader.get_string(4).rstrip()
            # self.logger.info("reading smf26xtm @ %d bytes", smf26ln1_start + s_reader.tell())
            s_reader.read(4 + 4 + 4 + 4 + 2 + 2 + 2 + 2) # xtm, eln, epu, frm, cyp, lin, prr, pur
            # self.logger.info("reading smf26pdd @ %d bytes", smf26ln1_start + s_reader.tell())
            s_reader.get_string(8).rstrip() # pdd
            x = s_reader.bytes_remaining()
            if x > 0:
                self.logger.info("smf26ln1_buffer @ %d bytes, %d bytes left over", smf26ln1_start + s_reader.tell(), x)

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

