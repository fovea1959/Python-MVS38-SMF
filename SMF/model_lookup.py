import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# GC28-6628-9_OS_System_Ctl_Blks_R21.7_Apr73.pdf
# GC28-0710-0_OS_VS2_Debugging_Handbook_Vol_3_Rel_3.7_Dec78.pdf
# LC28-1389-0_MVS_370_System_Programming_Library_Debugging_Handbook_Volume_5_Data_Areas_S-Z_Jul1985.pdf

dasd_table = {
    0x06: "2305-1",
    0x07: "2305-2",
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
    0x01: "2540-R",
    0x02: "2540-P",
    0x03: "1442",
    0x04: "2501",
    0x05: "2520",
    0x06: "3505",
    0x08: "1403",
    0x09: "3211",
    0x0a: "1403-N1",
    0x0b: "3203",   # double check this?
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

device_classes = {
    0x04: ("Character Reader", None),
    0x08: ("Unit Record", unit_record_table),
    0x10: ("Terminal", terminal_table),
    0x20: ("DASD", dasd_table),
    0x40: ("Communications", None),
    0x80: ("Magnetic Tape", tape_table),
}

def lookup_device_class(device_class: int) -> str:
    rv, _ = device_classes.get(device_class)
    if rv is None:
        rv = "Unknown device class 0x{device_class:x}"
    return rv

def lookup_model(unit_type: int) -> str:
    device_class = (unit_type & 0xff00) >> 8
    device_type = unit_type & 0xff
    logger.debug(f"unit_type {unit_type:08x} -> device class=0x{device_class:02x}, device_type {device_type:02x}")
    return lookup_model_by_class_and_type(device_class, device_type)

def lookup_model_by_class_and_type(device_class, device_type):
    device_class_string, model_lookup_table =(
        device_classes.get(device_class, (f"Unknown device class 0x{device_class:x}", None)))

    if model_lookup_table is not None:
        rv = model_lookup_table.get(device_type)
        if rv is None:
            rv = f"Unknown {device_class_string}: 0x{device_type:02x}"
    else:
        rv = device_class_string

    return rv
