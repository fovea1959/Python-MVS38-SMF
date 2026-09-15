from .bareader import BAReader
from .smf import SMF
from .model_lookup import lookup_model_by_class_and_type

class SMF10(SMF):
    smf_description = "Allocation Recovery"

    # noinspection PyAttributeOutsideInit
    def fill(self, reader: BAReader):
        # picking up from after smfxsid
        self.smfxjbn = reader.get_string(8).rstrip()
        self.smfxrst = reader.get_tme_dte()
        reader.get_string(8)    # smf10uif
        smf10ln = reader.get_halfword()
        s_reader = reader.subreader(smf10ln - 2)
        device_entries = []
        while s_reader.bytes_remaining() >= 4:
            devc = s_reader.get_byte()
            utyp = s_reader.get_byte()
            dt = lookup_model_by_class_and_type(devc, utyp)
            smf4cuad = s_reader.get_halfword()
            dd = {
                'smf10model': dt,
                'smf10cuad': f'{smf4cuad:03x}',
            }
            device_entries.append(dd)
        self.smf10devices = device_entries
        if s_reader.bytes_remaining() > 0:
            self.logger.warn("extra bytes at end of device entries")

    def __repr__(self) -> str:
        return self._repr(
            jobname=self.smfxjbn,
        )
