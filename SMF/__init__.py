from typing import TYPE_CHECKING

from .smf_parser import SMFParser

if TYPE_CHECKING:
    from .smf0x import *
    from .smf1x import *
    from .smf2x import *
    from .smf3x import *
    from .smf4x import *
    from .smf7x import *
    from .smf24x import *