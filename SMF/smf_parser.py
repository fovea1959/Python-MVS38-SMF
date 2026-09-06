import datetime
import inspect
import io
import json
import logging
import struct
import re

from collections.abc import Collection
from typing import TYPE_CHECKING

from .smf0x import *
from .smf7x import *

if TYPE_CHECKING:
    from .smf import SMF


class SMFParseError(Exception):
    pass


def has_class_in_smfnx_module(class_name: str) -> bool:
    obj = globals().get(class_name)
    if obj is None:
        return False
    if not inspect.isclass(obj):
        return False

    reg = re.compile(r"^SMF.smf\dx$")
    m = reg.match(obj.__module__)
    return True if m else False


class SMFParser:
    def __init__(self):
        self.logger = logging.getLogger(__class__.__name__)
        self.logger.setLevel(logging.DEBUG)
        self.reader = None
        pass

    def make_smf_from_bytes(self, b: bytes | bytearray, type_filter: Collection[int] | None = None) -> SMF | None:
        self.reader = io.BytesIO(b)

        # these are the SDW
        # smf_len = self.get_halfword()
        # smf_seg = self.get_halfword()
        smf_flag = self.get_byte()
        smf_type = self.get_byte()
        smf_tme = self.get_tod()
        smf_dte = self.get_yydddf()
        smf_sid = self.get_string(4).rstrip()

        if type_filter is not None:
            if smf_type not in type_filter:
                return None

        class_name = f'SMF{smf_type}'

        if has_class_in_smfnx_module(class_name):
            logging.debug(f"Found {class_name}")
            class_object = globals()[class_name]
            rv = class_object()
        else:
            logging.debug(f"No {class_name}")
            from .smf import SMF
            rv = SMF()

        rv.smf_flag = smf_flag
        rv.smf_type = smf_type
        rv.smf_sid = smf_sid

        rv.smf_datetime = self.make_datetime(smf_dte, smf_tme)

        rv.fill(self)

        b = self.reader.read()
        if len(b) != 0:
            logging.info("Had %d unprocessed bytes at end of SMF %d record", len(b), rv.smf_type)

        self.reader = None
        return rv

    def read(self, l):
        assert self.bytes_remaining() >= l
        return self.reader.read(l)

    def bytes_remaining(self):
        # Calculate remaining bytes
        total_size = self.reader.getbuffer().nbytes
        current_pos = self.reader.tell()
        return total_size - current_pos

    @staticmethod
    def make_datetime(dte: datetime.date, tme: datetime.timedelta):
        midnight = datetime.datetime.combine(dte, datetime.time.min)
        rv = midnight + tme
        return rv

    def get_string(self, l):
        b = self.read(l)
        rv = b.decode('cp500')
        return rv

    def get_fullword(self):
        b = self.read(4)
        rv, = struct.unpack(">I", b)
        return rv

    def get_halfword(self):
        b = self.read(2)
        rv, = struct.unpack(">H", b)
        return rv

    def get_byte(self):
        b = self.read(1)
        return int.from_bytes(b, signed=False)

    def get_tme_dte(self) -> datetime.datetime:
        tme = self.get_tod()
        dte = self.get_yydddf()
        return self.make_datetime(dte, tme)

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
        packed_bytes = self.read(l)
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

