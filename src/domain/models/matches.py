from typing import TypedDict, Optional

from src.domain.models.scanner import ScannerFinds

class Matches(TypedDict):
    matches: list[ScannerFinds]
    severity: list[float]

class FormatScan(TypedDict):
    words_found: int
    matches: list[ScannerFinds]
    severity: float

class SeverityResult(TypedDict):
    percentage: float
    analysis: str

class ScanMatches(TypedDict):
    unprotected: bool
    severity: SeverityResult
    finds: Optional[list[FormatScan]]
