import logging
import struct

from sl_tape import *

def main():
    sl_tape = SLTape("20260905-1722.aws")
    print(sl_tape.datasets_by_name)


    if True:
        dataset: Dataset = sl_tape.datasets_by_name.get('ALL.SMFDATA.VBS')

        if False:
            sum_bdw = 0
            for block in dataset.blocks:
                bdw, = struct.unpack(">H", block.data[:2])
                sum_bdw += bdw
                print(bdw, block.len)

            print(sum_bdw)

        if True:
            for i, record in enumerate(dataset.records()):
                print('VBS record', i, len(record))

    dataset : Dataset = sl_tape.datasets_by_name.get('ALL.SMFDATA.VB')
    for i, record in enumerate(dataset.records()):
        print('VB  record', i, len(record))


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    main()
