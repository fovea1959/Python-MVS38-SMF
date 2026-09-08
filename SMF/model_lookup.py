import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# GC28-6628-9_OS_System_Ctl_Blks_R21.7_Apr73.pdf


dasd_table = {
    0x08: "2314",
    0x09: "3330",
    0x0a: "3340",
    0x0b: "3350",
    0x0c: "3375",
    0x0d: "3330-1",
    0x0e: "3380",
    0x0f: "3390",
}

tape_table = {
    0x01: "2400",
    0x03: "3420",   # 12804003 is model 8 (6250 bpi), 10804003 is model 4/6 or 8)
    0x07: "3410",
}

unit_record_table = {
    # need double checking against the reference
    0x01: "2540",
    0x02: "2501",
    0x05: "3215",
    0x06: "3505",
    0x08: "1403",
    0x09: "3211",
    0x0b: "3203",
    0x0c: "3525",
    0x0e: "3800",
    0x23: "3215-C",         # empirical guesswork
}

terminal_table = {
    0x01: "2250-1",
    0x02: "2250-3",
    0x03: "2260",
    0x04: "2260",
    0x05: "2260-1",
    0x09: "3277-1",
    0x0a: "3277-2",
    0x0b: "3284/3286",
}


def lookup_model(unit_type: int) -> str:
    device_class = (unit_type & 0xff00) >> 8
    b4 = unit_type & 0xff
    logger.debug(f"unit_type {unit_type:x} -> device class=0x{device_class:02x}, b4=0x{b4:02x}")

    device_class_string, model_lookup_table = {
        0x04: ("Character Reader", None),
        0x08: ("Unit Record", unit_record_table),
        0x10: ("Terminal", terminal_table),
        0x20: ("DASD", dasd_table),
        0x40: ("Communications", None),
        0x80: ("Magnetic Tape", tape_table),
    }.get(device_class, (f"Unknown device class string {device_class:x}", None))

    if model_lookup_table is not None:
        rv = model_lookup_table.get(b4)
        if rv is None:
            rv = f"Unknown {device_class_string}: 0x{b4:02x}"
    else:
        rv = device_class_string

    return rv
