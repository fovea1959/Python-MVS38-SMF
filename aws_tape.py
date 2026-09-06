import logging
import struct

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class TapeMark:
    def __repr__(self):
        return "TapeMark"


class TapeBlock:
    def __init__(self, data: bytes):
        self.data = data

    def __repr__(self):
        return f"TapeBlock: {len(self.data)} byte(s)"

    @property
    def len(self):
        return len(self.data)


# Official AWSTAPE Specification Flags:
_TMK = 0x40 # TMK (Tape Mark / EOF)
_NEWREC = 0x80 # NEWREC (Start of new record chunk)
_ENDREC = 0x20 # ENDREC (End of record chunk)

def read_aws_tape(file_path):
    with open(file_path, 'rb') as f:
        block_count = 0

        while True:
            header = f.read(6)
            if not header or len(header) < 6:
                break  # End of file

            # Unpack fields:
            # <H (2B) Current Length, <H (2B) Previous Length
            # B (1B) Flags1, B (1B) Flags2
            curr_len, prev_len, flags1, flags2 = struct.unpack('<HHBB', header)

            # Official AWSTAPE Specification Flags:
            # 0x40 = TMK (Tape Mark / EOF)
            # 0x80 = NEWREC (Start of new record chunk)
            # 0x20 = ENDREC (End of record chunk)
            is_tapemark = bool(flags1 & 0x40) or (curr_len == 0 and flags1 == _TMK)

            logger.debug(
                f"Block {block_count:04d} | Length: {curr_len} | Prev: {prev_len} | Flags1: 0x{flags1:02X} | Flags2: 0x{flags2:02X}")

            if is_tapemark:
                logger.debug("   --> [Tape Mark / EOF] <--")
                yield TapeMark()
                continue  # Tape marks have 0 blocks payload length

            if flags1 != _NEWREC + _ENDREC:
                logger.warning("chunk is spanning blocks")
            if curr_len > 0:
                payload = f.read(curr_len)
                if logger.isEnabledFor(logging.DEBUG):
                    try:
                        text_preview = payload[:40].decode('cp500', errors='replace')
                        logger.debug(f"  Data Preview ({len(payload)} bytes: {text_preview}")
                    except Exception:
                        logger.debug(f"  Data Preview( {len(payload)} bytes: [Binary]")
                yield TapeBlock(payload)

            block_count += 1


def main():
    for content in read_aws_tape('20260905-1046.aws'):
        print(content)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()