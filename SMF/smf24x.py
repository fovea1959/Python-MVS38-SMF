from .bareader import BAReader
from .model_lookup import lookup_model, lookup_device_class
from .smf import SMF
from .smf_errors import SMFParseError

class SMF242(SMF):
    smf_description = "BREXX"

    # noinspection PyAttributeOutsideInit
    def fill(self, reader: BAReader):
        self.smf242ssi = reader.get_string(4).rstrip()
        smf242subrectype = reader.get_halfword()

        self.smf242user = reader.get_string(8).rstrip()
        self.smf242runid = reader.get_string(4).rstrip()
        if smf242subrectype == 1:
            self.smf242subrectype = "start"
            self.smf242dsname = reader.get_string(54).rstrip()
            self.smf242args = reader.get_string(82).rstrip()
        elif smf242subrectype == 2:
            self.smf242subrectype = "load"
            self.smf242dsname = reader.get_string(44).rstrip()
            self.smf242ddname = reader.get_string(8).rstrip()
            self.smf242member = reader.get_string(8).rstrip()
            self.smf242found = reader.get_string(12).rstrip()
        elif smf242subrectype == 10:
            self.smf242subrectype = "term"
            self.smf242retcode = reader.get_halfword()
            self.smf242abendcode = reader.get_string(6).rstrip()
        else:
            self.smf242subrectype = str(smf242subrectype)

    def __repr__(self) -> str:
        return self._repr(
            subsys=self.smf242ssi,
            subtype=self.smf242subrectype,
            user=self.smf242user,
            runid=self.smf242runid,
        )