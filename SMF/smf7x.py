from .bareader import BAReader
from .smf import SMF
from .smf_errors import SMFParseError

class SMF7X(SMF):
    """
    all the SMF 7X records have a common control data section with the same layout...
    """
    def __init__(self):
        super().__init__()
        self.smf7xist_datetime = None
        self.smf7xint = None
        self.smf7xien_datetime = None
        self.smf7xmfv = None
        self.smf7xrls = None

    def fill7x(self, reader: BAReader):
        smf7xsiz = reader.get_halfword()
        s_reader = reader.subreader(smf7xsiz - 2)

        smf7xist = s_reader.get_0hhmmssf()
        smf7xdat = s_reader.get_0yyydddf()
        self.smf7xist_datetime = reader.make_datetime(smf7xdat, smf7xist)
        self.logger.info("reading smf7xint @ %d bytes", s_reader.tell())
        self.smf7xint = s_reader.get_mmsstttf()
        self.smf7xien_datetime = self.smf7xist_datetime + self.smf7xint
        s_reader.read(2 + 6)    # smf7xcyc, sub
        self.logger.info("reading smf7xmfv @ %d bytes", s_reader.tell())
        self.smf7xmfv = s_reader.get_string(2)
        s_reader.read(2)        # smf7xrv1
        self.logger.info("reading smf7xrls @ %d bytes", s_reader.tell())
        self.smf7xrls = s_reader.get_string(4)
        # there are two bytes at the end of the common control section that are not documented in gc28-0754-0
        #if s_reader.bytes_remaining() > 0:
        #    self.logger.info("end of smf70_common @ %d bytes, %d bytes left over", smf70_common_start + s_reader.tell(), s_reader.bytes_remaining())


class SMF70(SMF7X):
    smf_description = "CPU Activity"

    def __init__(self):
        super().__init__()
        self.smf70cpu = None

    def fill(self, reader: BAReader):
        self.fill7x(reader)    # get common control data section

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

