from .bareader import BAReader
from .smf import SMF
from .smf_errors import SMFParseError


class SMF40(SMF):
    smf_description = "Dynamic DD"


class SMF43(SMF):
    smf_description = "JES start"

    # noinspection PyAttributeOutsideInit
    def fill(self, reader: BAReader):
        smf43sbs = reader.get_halfword()
        if smf43sbs != 2:
            raise SMFParseError("Got a Type 43 record from other than JES2")
        reader.read(2)    # smf43rsv

        smf43lrr = reader.get_halfword()
        s_reader = reader.subreader(smf43lrr)
        s_reader.get_halfword() # smf43rv1
        s_reader.get_byte()     # smf43rst
        self.smf43opt = s_reader.get_byte()
        if self.smf43opt & 0x80 != 0:
            self.smf43opt_format = 1
        if self.smf43opt & 0x40 != 0:
            self.smf43opt_cold = 1
        if self.smf43opt & 0x20 != 0:
            self.smf43opt_req = 1
        if self.smf43opt & 0x10 != 0:
            self.smf43opt_list = 1
        self.logger.info("smf43opt = 0x%x %d", self.smf43opt, self.smf43opt)
        s_reader.get_string(4)  # smf43eid
        if s_reader.bytes_remaining() > 0:
            self.logger.info("SMF43LRR area had %d extra bytes remaining", s_reader.bytes_remaining())


class SMF45(SMF):
    smf_description = "JES withdrawal"