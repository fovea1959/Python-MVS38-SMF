import datetime
import io
import struct

class BAReader:
    def __init__(self, initial_bytes: bytes):
        self.r = io.BytesIO(initial_bytes)

    def tell(self) -> int:
        return self.r.tell()

    def bytes_remaining(self) -> int:
        # Calculate remaining bytes
        total_size = self.r.getbuffer().nbytes
        current_pos = self.r.tell()
        return total_size - current_pos

    def read(self, size: int = -1) -> bytes:
        br = self.bytes_remaining()
        assert br >= size, f"need at least {size} bytes, have only {br} bytes"
        return self.r.read(size)

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

