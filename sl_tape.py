import logging

from nl_tape import *
from dataset import *
from utils import *


class SLTapeException(Exception):
    pass


class SLTape:
    def __init__(self, filename):
        self.logger = logging.getLogger("SLTape")
        self.logger.setLevel(logging.INFO)

        self.nl_tape = NLTape(filename)

        self.volume_name = None

        self.datasets_by_name = {}
        self.datasets_by_index = []

        tape_files = self.nl_tape.tape_files.copy()

        if len(tape_files) < 5:
            raise SLTapeException("Not enough tape files")

        if tape_files[-1].len() != 0 or tape_files[-2].len() != 0:
            raise SLTapeException("Don't have 2 trailing tape marks")

        tape_files = tape_files[0:-2]   # get rid of trailing tape marks

        if len(tape_files) % 3 != 0:
            raise SLTapeException("Don't have sets of (labels, blocks, labels)")

        while len(tape_files) > 0:
            hdr_labels = tape_files.pop(0)
            data_blocks = tape_files.pop(0)
            end_labels = tape_files.pop(0)

            dataset = Dataset()
            labels = Only1Dict()

            dataset.blocks = data_blocks.blocks

            for label in hdr_labels.blocks:
                if len(label.data) != 80:
                    raise Exception("Header label is wrong length")
                ascii = label.data.decode('cp500')
                self.logger.debug("header label: %s", ascii)

                id = ascii[:4]
                if id == 'VOL1':
                    if self.volume_name is not None:
                        raise SLTapeException("multiple VOL1 labels")
                    self.volume_name = ascii[4:10].rstrip()
                elif id in ('HDR1', 'HDR2'):
                    try:
                        labels[id] = ascii
                    except Only1Error:
                        raise SLTapeException(f"Multiple {id} labels")
                else:
                    raise SLTapeException(f"Unknown header label {id}")

            for label in end_labels.blocks:
                if len(label.data) != 80:
                    raise Exception("End label is wrong length")
                ascii = label.data.decode('cp500')
                self.logger.debug("end label: %s", ascii)

                id = ascii[:4]
                if id in ('EOF1', 'EOF2'):
                    try:
                        labels[id] = ascii
                    except Only1Error:
                        raise SLTapeException(f"Multiple {id} labels")
                else:
                    raise SLTapeException(f"Unknown ending label {id}")

            logger.debug("labels: %s", labels)

            hdr1 = labels.get('HDR1')
            if hdr1 is None:
                raise SLTapeException("no HDR1 label")
            dataset.dsn = hdr1[4:4+17].rstrip()
            dataset.sequence_number = int(hdr1[31:31+4])

            hdr2 = labels.get('HDR2')
            if hdr2 is None:
                raise SLTapeException("no HDR2 label")
            dataset.dcb.record_format = hdr2[4:4+1]
            dataset.dcb.block_length = int(hdr2[5:5+5])
            dataset.dcb.record_length = int(hdr2[10:10+5])
            dataset.dcb.block_attribute = hdr2[38:38+1]

            eof1 = labels.get('EOF1')
            if eof1 is None:
                raise SLTapeException("no EOF1 label")
            block_count = int(eof1[54:54+6])
            if block_count != data_blocks.len():
                raise SLTapeException(f"wrong number of blocks, label says {block_count}, actual is {data_blocks.len()}")

            eof2 = labels.get('EOF2')
            if eof2 is None:
                raise SLTapeException("no EOF2 label")

            self.logger.info("dataset: %s", dataset)

            self.datasets_by_index.append(dataset)
            self.datasets_by_name[dataset.dsn] = dataset


def main():
    import json
    sl_tape = SLTape("20260905-1722.aws")


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    main()

