import collections
#import datetime
import inspect
#import io
#import json
import logging
#import struct
import re

from collections.abc import Collection
from typing import TYPE_CHECKING

from .smf0x import *
from .smf2x import *
from .smf3x import *
from .smf4x import *
from .smf7x import *

if TYPE_CHECKING:
    from .smf import SMF


logger = logging.getLogger(__name__)


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
        self.reader = None
        self.all_counter = collections.Counter()
        self.all_count = 0
        self.filtered_counter = collections.Counter()
        self.filtered_count = 0

    def make_smf_from_bytes(self, b: bytes | bytearray, type_filter: Collection[int] | None = None) -> SMF | None:
        self.reader = BAReader(b)

        # these are the SDW
        # smf_len = self.get_halfword()
        # smf_seg = self.get_halfword()
        smf_flag = self.reader.get_byte()
        smf_type = self.reader.get_byte()
        smf_tme_dte = self.reader.get_tme_dte()
        smf_sid = self.reader.get_string(4).rstrip()

        self.all_counter[smf_type] += 1
        self.all_count += 1

        if type_filter is not None:
            if smf_type not in type_filter:
                return None

        self.filtered_counter[smf_type] += 1
        self.filtered_count += 1

        class_name = f'SMF{smf_type}'

        if has_class_in_smfnx_module(class_name):
            logger.debug(f"Found {class_name}")
            class_object = globals()[class_name]
            rv = class_object()
        else:
            logger.debug(f"No {class_name}")
            from .smf import SMF
            rv = SMF()

        rv.smf_flag = smf_flag
        rv.smf_type = smf_type
        rv.smf_sid = smf_sid

        rv.smf_datetime = smf_tme_dte

        rv.fill(self.reader)

        bc = self.reader.bytes_remaining()
        if bc != 0:
            logger.info("Had %d unprocessed bytes at end of SMF %d record", bc, rv.smf_type)

        self.reader = None
        return rv
