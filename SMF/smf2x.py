from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .smf_parser import SMFParser

from .smf import SMF

class SMF26(SMF):
    smf_description = "JES Job Purge"

    def __init__(self):
        super().__init__()
        self.smf26jbn = None
        self.smf26rs_datetime = None

    def fill(self, smf_parser: SMFParser):
        self.smf26jbn = smf_parser.get_string(8).rstrip()
        self.smf26rs_datetime = smf_parser.get_tme_dte()
        smf_parser.read(8+4+2+2)    # smf26uif, rsc, sbs, ind

        smf26ln1 = smf_parser.get_halfword()
        smf_parser.read(smf26ln1-2)

        smf26ln2 = smf_parser.get_halfword()
        smf_parser.read(smf26ln2 - 2)

        smf26ln3 = smf_parser.get_halfword()
        smf_parser.read(smf26ln3 - 2)

        if smf_parser.bytes_remaining() > 0:
            smf26ln4 = smf_parser.get_halfword()
            smf_parser.read(smf26ln4 - 2)

    def __repr__(self) -> str:
        return self._repr(job=self.smf26jbn, reader=str(self.smf26rs_datetime)[:-4])

