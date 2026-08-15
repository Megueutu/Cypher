from typing import TypedDict

class ScannerFinds(TypedDict):
    word:      str
    attempts:  int
    dataset:   str
    scan_type: str

class ScannerResult(TypedDict):
    matches:  list[ScannerFinds]
    score:    float
    attempts: int
