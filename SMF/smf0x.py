from .bareader import BAReader
from .smf import SMF
from .smf_errors import SMFParseError

class SMF0(SMF):
    smf_description = "IPL Header"

    def __init__(self):
        super().__init__()
        self.smf0vst = None
        self.smf0rst = None
        self.smf0osl = None
        self.smf0syn = None

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

