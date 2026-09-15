from .bareader import BAReader
from .model_lookup import lookup_model, lookup_device_class
from .smf import SMF
from .smf_errors import SMFParseError

class SMF70(SMF):
    smf_description = "CPU Activity"

    # noinspection PyAttributeOutsideInit
    def fill(self, reader: BAReader):
        smf7xsiz = reader.get_halfword()

        # process common section
        s_reader = reader.subreader(smf7xsiz - 2)
        smf7xist = s_reader.get_0hhmmssf()
        smf7xdat = s_reader.get_0yyydddf()
        self.smf7xist_datetime = reader.make_datetime(smf7xdat, smf7xist)
        self.smf7xint = s_reader.get_mmsstttf()
        self.smf7xien_datetime = self.smf7xist_datetime + self.smf7xint
        s_reader.read(2)        # smf70cyc
        s_reader.read(6)        # smf70sub
        self.smf7xmfv = s_reader.get_string(2)
        s_reader.read(2)        # smf7xrv1
        self.smf7xrls = s_reader.get_string(4)
        # there are two bytes at the end of the common control section that are not documented in gc28-0754-0
        #if s_reader.bytes_remaining() > 0:
        #    self.logger.info("end of smf70_common @ %d bytes, %d bytes left over", smf70_common_start + s_reader.tell(), s_reader.bytes_remaining())

        assert s_reader.tell() == 44, f"smf70scc in wrong place, @ {reader.tell()}"
        smf70scc = reader.get_halfword()

        # process CPU control section
        s_reader = reader.subreader(smf70scc - 2)
        smf70cpu = s_reader.get_halfword()
        smf70scd = s_reader.get_halfword()
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

    def fill(self, reader: BAReader):
        smf7xsiz = reader.get_halfword()

        # process common control section
        s_reader = reader.subreader(smf7xsiz - 2)
        smf7xist = s_reader.get_0hhmmssf()
        smf7xdat = s_reader.get_0yyydddf()
        self.smf7xist_datetime = reader.make_datetime(smf7xdat, smf7xist)
        self.smf7xint = s_reader.get_mmsstttf()
        self.smf7xien_datetime = self.smf7xist_datetime + self.smf7xint
        s_reader.get_packed_decimal(2) / 1000.0 # smf7xcyc
        s_reader.read(2)  # smf7Xsub
        s_reader.get_fullword() # SMF7XSAM
        self.smf7xmfv = s_reader.get_string(2)
        s_reader.read(2)  # smf7xrv1
        assert s_reader.tell() == 40, f"smf7xrls in wrong place, @ {reader.tell()}"
        self.smf7xrls = s_reader.get_string(4)

        smf71spc = reader.get_halfword()
        smf71spd = reader.get_halfword()

class SMF72(SMF):
    # not sure if this is useful to me right now
    smf_description = "Workload Activity"


class SMF73(SMF):
    smf_description = "Channel Activity"

    # noinspection PyAttributeOutsideInit
    def fill(self, reader: BAReader):
        smf7xsiz = reader.get_halfword()
        s_reader = reader.subreader(smf7xsiz - 2)

        smf7xist = s_reader.get_0hhmmssf()
        smf7xdat = s_reader.get_0yyydddf()
        self.smf7xist_datetime = reader.make_datetime(smf7xdat, smf7xist)
        self.logger.info("reading smf7xint @ %d bytes", s_reader.tell())
        self.smf7xint = s_reader.get_mmsstttf()
        self.smf7xien_datetime = self.smf7xist_datetime + self.smf7xint
        self.smf7xcyc = s_reader.get_packed_decimal(2) / 1000.0
        s_reader.read(2)        # smf73sub
        self.smf7xsam = s_reader.get_fullword()
        self.logger.info("reading smf7xmfv @ %d bytes", s_reader.tell())
        self.smf7xmfv = s_reader.get_string(2)
        s_reader.read(2)        # smf7xrv1
        self.logger.info("reading smf7xrls @ %d bytes", s_reader.tell())
        self.smf7xrls = s_reader.get_string(4)



class SMF74(SMF):
    smf_description = "Device Activity"

    # noinspection PyAttributeOutsideInit
    def fill(self, reader: BAReader):
        smf7xsiz = reader.get_halfword()
        s_reader = reader.subreader(smf7xsiz - 2)

        smf7xist = s_reader.get_0hhmmssf()
        smf7xdat = s_reader.get_0yyydddf()
        self.smf7xist_datetime = reader.make_datetime(smf7xdat, smf7xist)
        self.logger.info("reading smf7xint @ %d bytes", s_reader.tell())
        self.smf7xint = s_reader.get_mmsstttf()
        self.smf7xien_datetime = self.smf7xist_datetime + self.smf7xint
        self.smf74cyc = s_reader.get_packed_decimal(2) / 1000.0
        self.smf74sub = s_reader.read(2)[-1]
        self.smf74sub_s = lookup_device_class(self.smf74sub)
        self.smf74sam = s_reader.get_fullword()
        self.smf7xmfv = s_reader.get_string(2)
        s_reader.read(2)  # smf7xrv1
        self.logger.info("reading smf7xrls @ %d bytes", s_reader.tell())
        self.smf7xrls = s_reader.get_string(4)
        # there are two bytes at the end of the common control section that are not documented in gc28-0754-0
        # if s_reader.bytes_remaining() > 0:
        #    self.logger.info("end of smf70_common @ %d bytes, %d bytes left over", smf70_common_start + s_reader.tell(), s_reader.bytes_remaining())

        smf74sdc = reader.get_halfword()
        s_reader = reader.subreader(smf74sdc - 2)

        # self.logger.info("reading smf70cpu @ %d bytes", s_reader.tell())
        smf74dev = s_reader.get_halfword()
        smf74sdd = s_reader.get_halfword()
        s_reader.read(2)  # smf74rv2

        self.smf74dev = {}
        for _ in range(smf74dev):
            s_reader = reader.subreader(smf74sdd)
            smf74add = s_reader.read(2).hex()[:3].upper()
            s_reader.read(1 + 1)  # smf74rv3, smf74cnf      TODO: process smf74cnf
            smf74typ = s_reader.get_fullword()
            smf74model = lookup_model(smf74typ)
            smf74ser = s_reader.get_string(6).rstrip()
            # self.logger.info("smf70ser = %s", smf70ser)
            s_reader.get_halfword()     # smf74rv4
            smf74cnt = s_reader.get_fullword()
            smf74act = s_reader.get_fullword()
            smf74que = s_reader.get_fullword()
            dev_dict = {
                # "smf74typ": hex(smf74typ),
                "smf74model": smf74model,
                "smf74cnt": smf74cnt,
                "smf74act": smf74act,
                "smf74que": smf74que,
            }
            if len(smf74ser) > 0:
                dev_dict["smf74ser"] = smf74ser
            self.smf74dev[smf74add] = dev_dict


