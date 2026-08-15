from dataclasses import dataclass
from enum import Enum

class ScanType(Enum):
    COMPLETE = "complete"
    REGULAR  = "regular"
    SEQUENCE = "sequence"
    PATTERN  = "pattern"
    ALIKE    = "alike"

@dataclass
class Finds():
    sequence:  bool
    pattern:   bool
    blacklist: bool
    