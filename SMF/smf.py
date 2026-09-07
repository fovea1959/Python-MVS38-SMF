import datetime
import logging
import typing

from typing import TYPE_CHECKING

from .bareader import BAReader

if TYPE_CHECKING:
    from .smf_parser import SMFParser

class SMF:
    smf_description = None
    def __init__(self):
        self.logger = logging.getLogger(f"SMF.{self.__class__.__name__}")
        self.smf_datetime = None
        self.smf_type = None
        # the SMF documents describe these, but they are actually the RDW
        # self.smf_len: int | None = None
        # self.smf_seg: int | None = None
        self.smf_flag: int | None = None
        self.smf_type: int | None = None
        self.smf_datetime: datetime.datetime | None = None
        self.smf_sid: str | None = None
        # self.smf_description: str | None = None

    def fill(self, reader: BAReader):
        gobble = reader.read()
        self.logger.debug("ate %d bytes at end of type %d record", self.smf_type, len(gobble))

    def _repr(self, **fields: typing.Dict[str, typing.Any]) -> str:
        my_fields: typing.Dict[str, typing.Any] = {
            '-timestamp': str(self.smf_datetime)[:-4],      # remove extra decimal places
        }
        my_fields.update(fields)
        return self._repr_no_common(**my_fields)

    def _repr_no_common(self, **fields: typing.Dict[str, typing.Any]) -> str:
        # Helper for __repr__
        cn = self.__class__.__name__

        dd = ''
        if self.smf_description is not None:
            dd = f'[{self.smf_description}]'
        elif cn == "SMF":
            dd = f'[{self.smf_type}]'

        field_strings = []
        for key, field in fields.items():
            if key.startswith('-'):
                field_strings.append(f'{field}')
            else:
                field_strings.append(f'{key}={field!r}')

        return f"<{cn}{dd}({','.join(field_strings)})>"

    def __repr__(self) -> str:
        return self._repr()
