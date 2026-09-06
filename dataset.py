import io
import logging

from aws_tape import *

class DCB:
    def __init__(self):
        self.block_length = None
        self.record_length = None
        self.record_format = None
        self.block_attribute = None

    def __repr__(self):
        return f"DCB: record_length={self.record_length}/{self.block_length} record_format={self.record_format} block_attribute={self.block_attribute}"


class Dataset:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)

        self.dsn = None
        self.dcb = DCB()
        self.blocks: list[TapeBlock] = list()
        self.sequence_number = None

    def block_rdr(self):
        all_bytes = bytearray()
        for block in self.blocks:
            all_bytes.extend(block.data)
        self.logger.debug("Length of all bytes = %d", len(all_bytes))
        return io.BytesIO(all_bytes)

    def records(self):
        self.logger.debug("Dataset RECFM: %s, BLOCK_ATTRIBUTE: %s", self.dcb.record_format, self.dcb.block_attribute)
        if self.dcb.record_format == 'V':
            if self.dcb.block_attribute == 'R':
                return self.vbs_records()
            else:
                return self.vb_records()

    def vb_records(self):
        self.logger.info("Using VB reader")
        f = self.block_rdr()

        while True:
            # 1. Read the 4-byte BDW (Block Descriptor Word)
            bdw = f.read(4)
            if not bdw or len(bdw) < 4:
                break  # End of file reached

            # First 2 bytes = Block Length (Big-Endian unsigned short)
            # Next 2 bytes = Reserved / Flags
            block_len, _ = struct.unpack(">HH", bdw)

            # The length in the BDW includes the 4 bytes of the BDW itself
            bytes_left_in_block = block_len - 4

            # 2. Process all records inside this physical block
            while bytes_left_in_block > 0:
                # Read the 4-byte RDW (Record Descriptor Word)
                rdw = f.read(4)
                if not rdw or len(rdw) < 4:
                    break

                # First 2 bytes = Record Length (Big-Endian unsigned short)
                # Next 2 bytes = Reserved / Flags
                rec_len, _ = struct.unpack(">HH", rdw)

                # The length in the RDW includes the 4 bytes of the RDW itself
                data_len = rec_len - 4

                # Read the actual variable-length data record
                record_data = f.read(data_len)

                # Yield the raw record bytes (decode from EBCDIC later if needed)
                yield record_data

                # Track how many bytes we've consumed from this block
                bytes_left_in_block -= (4 + data_len)

    def vbs_records(self):
        self.logger.info("Using VBS reader")
        f = self.block_rdr()

        current_record = bytearray()

        while True:
            # 1. Read the 4-byte Block Descriptor Word (BDW)
            bdw_bytes = f.read(4)
            if not bdw_bytes or len(bdw_bytes) < 4:
                break  # End of file

            # Big-endian: 2 bytes length, 2 bytes reserved
            block_length, _ = struct.unpack('>HH', bdw_bytes)
            bytes_remaining_in_block = block_length - 4

            # 2. Process all segments within the current block
            while bytes_remaining_in_block > 4:
                sdw_bytes = f.read(4)
                if not sdw_bytes or len(sdw_bytes) < 4:
                    break

                # Big-endian: 2 bytes length, 2 bytes flags
                seg_length, flags_raw = struct.unpack('>HH', sdw_bytes)
                segment_control = flags_raw >> 8  # Use the first byte of the flags field

                # Calculate actual data payload length
                data_length = seg_length - 4
                if data_length < 0:
                    break

                segment_data = f.read(data_length)
                bytes_remaining_in_block -= seg_length

                # 3. Reassemble records using Segment Control Flags
                if segment_control == 0x00:
                    # Complete logical record (unspanned)
                    yield bytes(segment_data)
                    current_record.clear()

                elif segment_control == 0x01:
                    # First segment of a spanned record
                    current_record = bytearray(segment_data)

                elif segment_control == 0x03:
                    # Middle segment of a spanned record
                    current_record.extend(segment_data)

                elif segment_control == 0x02:
                    # Last segment of a spanned record
                    current_record.extend(segment_data)
                    yield bytes(current_record)
                    current_record.clear()

    def __repr__(self):
        return f"Dataset: DSN='{self.dsn}' DCB={self.dcb} #blocks={len(self.blocks)}"