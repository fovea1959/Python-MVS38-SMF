from .bareader import BAReader
from .smf import SMF
from .smf_errors import SMFParseError

class SMF70(SMF):
    smf_description = "CPU Activity"

    def __init__(self):
        super().__init__()
        self.smf70ist = None
        self.smf70dat = None
        self.smf70int = None
        self.smf70mfv = None
        self.smf70rls = None
        self.smf70cpu = None

    def fill(self, reader: BAReader):
        smf70siz = reader.get_halfword()
        s_reader = reader.subreader(smf70siz - 2)

        self.smf70ist = s_reader.read(4)
        self.smf70dat = s_reader.get_yydddf()
        self.logger.info("reading smf70int @ %d bytes", s_reader.tell())
        self.smf70int = s_reader.get_packed_decimal(4)
        s_reader.read(2 + 6)    # smf70cyc, sub
        self.logger.info("reading smf70mfv @ %d bytes", s_reader.tell())
        self.smf70mfv = s_reader.get_string(2)
        s_reader.read(2)        # smf70rv1
        self.logger.info("reading smf70rls @ %d bytes", s_reader.tell())
        self.smf70rls = s_reader.get_string(4)
        # there are two bytes at the end of the common control section that are not documented in gc28-0754-0
        #if s_reader.bytes_remaining() > 0:
        #    self.logger.info("end of smf70_common @ %d bytes, %d bytes left over", smf70_common_start + s_reader.tell(), s_reader.bytes_remaining())

        smf70scc = reader.get_halfword()
        s_reader = reader.subreader(smf70scc - 2)

        self.logger.info("reading smf70cpu @ %d bytes", s_reader.tell())
        smf70cpu = s_reader.get_halfword()
        self.logger.info("reading smf70scd @ %d bytes", s_reader.tell())
        smf70scd = s_reader.get_halfword()
        self.logger.info("smf70scd = %d", smf70scd)
        s_reader.read(2)    # smf70rv1

        self.smf70cpu = {}
        for _ in range(smf70cpu):
            s_reader = reader.subreader(smf70scd)
            smf70wat = s_reader.get_doubleword()
            smf70cid = s_reader.get_halfword()
            s_reader.read(1 + 1 + 1)     # smf70rv3, smf70cnf, smf70rv4        TODO: process smf70cnf
            smf70ser = s_reader.read(3).hex()
            self.logger.info("smf70ser = %s", smf70ser)
            self.smf70cpu[smf70cid] = { "smf70wat": smf70wat, "smf70wat_s": smf70wat / 4096000, "smf70ser": smf70ser }



class SMF71(SMF):
    smf_description = "Paging Activity"

class SMF72(SMF):
    smf_description = "Workload Activity"

class SMF73(SMF):
    smf_description = "Channel Activity"

class SMF74(SMF):
    smf_description = "Device Activity"

