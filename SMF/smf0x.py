from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .smf_parser import SMFParser

from .smf import SMF

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

