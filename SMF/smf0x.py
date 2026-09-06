from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .smf_parser import SMFParser

from .smf import SMF

class SMF0(SMF):
    smf_description = "IPL Header"

    def __init__(self):
        super().__init__()
        self.smf0vst = None
        self.smf0rst = None
        self.smf0osl = None
        self.smf0syn = None

    def fill(self, smf_parser: SMFParser):
        self.logger.info("getting ready to fill: have %d bytes", smf_parser.bytes_remaining())
        smf_parser.get_fullword()  # smf0jwt
        smf_parser.get_fullword()  # smf0buf
        self.smf0vst = smf_parser.get_fullword()
        smf_parser.get_byte()      # smf0opt
        self.smf0rst = smf_parser.get_fullword()
        if smf_parser.bytes_remaining() > 0:
            smf_parser.get_byte()      # smf0rsv
        if smf_parser.bytes_remaining() > 0:
            self.smf0osl = smf_parser.get_string(8)
        if smf_parser.bytes_remaining() > 0:
            self.smf0syn = smf_parser.get_string(8)

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

    def fill(self, smf_parser: SMFParser):
        self.smf6jbn = smf_parser.get_string(8).rstrip()
        self.smf6rs_datetime = smf_parser.get_tme_dte()
        smf_parser.get_string(8)    # smf6uif
        self.smf6owc = smf_parser.get_string(1)
        self.smf6ws_datetime = smf_parser.get_tme_dte()
        self.smf6nlr = smf_parser.get_fullword()
        smf_parser.get_byte()       # smf6ioe
        self.smf6nds = smf_parser.get_byte()
        self.smf6fmn = smf_parser.get_string(4)
        smf_parser.get_byte()       # smf6pad1
        smf_parser.get_halfword()   # smf6sbs

        smf_parser.get_halfword()  # smf6ln1
        smf_parser.read(1)  # smf6dci
        smf6indc = smf_parser.get_byte()
        if smf6indc == 0:
            self.smf6jnm = smf_parser.get_string(4)
        else:
            smf_parser.read(4)
        self.smf6out = smf_parser.get_string(8).rstrip()
        smf_parser.get_string(4)    # smf6fcb
        smf_parser.get_string(4)    # smf6ucs
        self.smf6pge = smf_parser.get_fullword()
        smf_parser.get_halfword()   # smf6rte

    def __repr__(self) -> str:
        return self._repr(job=self.smf6jbn, reader=str(self.smf6rs_datetime)[:-4])

