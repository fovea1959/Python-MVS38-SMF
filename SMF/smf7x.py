from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .smf_parser import *

from .smf import SMF

class SMF70(SMF):
    def __init__(self):
        super().__init__()

    def __repr__(self) -> str:
        return self._repr(name='smf70')


class SMF71(SMF):
    def __init__(self):
        super().__init__()

    def __repr__(self) -> str:
        return self._repr_no_common(name='smf71')