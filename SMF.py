import datetime
import inspect
import io
import logging
import struct
import sys
import typing

from collections.abc import Collection
from decimal import Decimal

import utils


class SMF:
    def __init__(self):
        # the SMF documents describe these, but they are actually the RDW
        # self.smf_len: int | None = None
        # self.smf_seg: int | None = None
        self.smf_flag: int | None = None
        self.smf_type: int | None = None
        self.smf_datetime: datetime.datetime | None = None
        self.smf_sid: str | None = None

    def fill(self, smf_parser: SMFParser):
        pass

    def _repr(self, **fields: typing.Dict[str, typing.Any]) -> str:
        my_fields: typing.Dict[str, typing.Any] = { 'timestamp': f'{self.smf_datetime.isoformat()} {self.smf_datetime}' }
        my_fields.update(fields)
        return self._repr_no_common(**my_fields)

    def _repr_no_common(self, **fields: typing.Dict[str, typing.Any]) -> str:
        # Helper for __repr__
        field_strings = []
        cn = self.__class__.__name__
        if cn == "SMF":
            field_strings.append(f'type={self.smf_type}')
        for key, field in fields.items():
            field_strings.append(f'{key}={field!r}')
        return f"<{cn}({','.join(field_strings)})>"

    def __repr__(self) -> str:
        return self._repr()


class SMF70(SMF):
    def __init__(self):
        super().__init__()

    def __repr__(self) -> str:
        return self._repr(name='smf70')


class SMF71(SMF):
    def __init__(self):
        super().__init__()

    def __repr__(self) -> str:
        return self._repr_no_common(name='smf71')


class SMFParseError(Exception):
    pass


def has_class_in_current_module(class_name: str) -> bool:
    # 1. Fetch the object from the module's global scope
    obj = globals().get(class_name)

    # 2. Check if the object exists, is a class, and was defined in THIS module
    return (
            obj is not None
            and inspect.isclass(obj)
            and obj.__module__ == __name__
    )

class SMFParser:
    def __init__(self):
        self.logger = logging.getLogger("SMFParser")
        self.logger.setLevel(logging.DEBUG)
        self.reader = None
        pass

    def make_smf_from_bytes(self, b: bytes | bytearray, filter: Collection[int] | None = None) -> SMF | None:
        self.reader = io.BytesIO(b)

        # these are the SDW
        # smf_len = self.get_halfword()
        # smf_seg = self.get_halfword()
        smf_flag = self.get_byte()
        smf_type = self.get_byte()
        smf_tme = self.get_tod()
        smf_dte = self.get_yydddf()
        smf_sid = self.get_string(4).rstrip()

        class_name = f'SMF{smf_type}'

        if has_class_in_current_module(class_name):
            logging.debug(f"Found {class_name}")
            class_object = globals()[class_name]
            rv = class_object()
        else:
            logging.debug(f"No {class_name}")
            rv = SMF()

        rv.smf_flag = smf_flag
        rv.smf_type = smf_type
        rv.smf_sid = smf_sid

        midnight = datetime.datetime.combine(smf_dte, datetime.time.min)
        rv.smf_datetime = midnight + smf_tme

        self.reader = None
        return rv

    def get_string(self, l):
        b = self.reader.read(l)
        rv = b.decode('cp500')
        return rv

    def get_fullword(self):
        b = self.reader.read(4)
        rv, = struct.unpack(">I", b)
        return rv

    def get_halfword(self):
        b = self.reader.read(2)
        rv, = struct.unpack(">H", b)
        return rv

    def get_byte(self):
        b = self.reader.read(1)
        return int.from_bytes(b, signed=False)

    def get_tod(self) -> datetime.timedelta:
        time_in_hundredths = self.get_fullword()
        seconds_since_midnight = time_in_hundredths / 100
        rv = datetime.timedelta(seconds=seconds_since_midnight)
        return rv

    def get_yydddf(self) -> datetime.date:
        yyyddd = self.get_packed_decimal(4)
        julian_day = yyyddd % 1000
        year = 1900 + (yyyddd // 1000)
        s_yyyyddd = f'{year:04d}{julian_day:03d}'
        rv = datetime.date.strptime(s_yyyyddd, "%Y%j")
        return rv

    def get_packed_decimal(self, l: int) -> int:    # original had decimals: int = 0 argument
        packed_bytes = self.reader.read(l)
        digits = []

        # Iterate through all bytes except the last one
        for byte in packed_bytes[:-1]:
            digits.append(str(byte >> 4))  # High nibble
            digits.append(str(byte & 0x0F))  # Low nibble

        # Handle the very last byte (contains the last digit and the sign)
        last_byte = packed_bytes[-1]
        digits.append(str(last_byte >> 4))  # Final digit
        sign_nibble = last_byte & 0x0F  # Sign indicator

        # Combine digits into a string
        digit_str = "".join(digits)

        # Determine the sign (D or B indicate negative)
        # C, F, or A indicate positive
        sign = -1 if sign_nibble in (0x0D, 0x0B) else 1

        # Convert to integer first
        value = int(digit_str) * sign

        # Shift the decimal point programmatically if necessary
        #return Decimal(value) / (10 ** decimals)
        return value


def main(argv):
    records = utils.read_list_of_bytes("vb.json")
    smf_parser = SMFParser()
    for record in records:
        smf_record = smf_parser.make_smf_from_bytes(record)
        logging.info("Got %s", smf_record)

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    main(sys.argv[1:])

